"use strict";
const $=id=>document.getElementById(id);
const labels={OPEN:"待处理",IN_PROGRESS:"处理中",RESOLVED:"已解决"};
const nextStates={OPEN:["OPEN","IN_PROGRESS"],IN_PROGRESS:["IN_PROGRESS","RESOLVED"],RESOLVED:["RESOLVED"]};
const types={DELAY:"运输延误",LATE_DELIVERY:"送达延误",MISSING_TIMESTAMP:"到达时间缺失",MISSING_ARRIVAL:"到达时间缺失",OVERDUE_IN_TRANSIT:"在途超时",DATA_QUALITY:"数据质量"};
const escapeHTML=s=>String(s??"—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const formatTime=value=>value?new Intl.DateTimeFormat("zh-CN",{timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).format(typeof value==="number"?new Date(value*1000):new Date(value)):"—";
let records=[],selected=null,page=1,busy=false,pendingConfirmation=null;
const pageSize=10;

async function api(url,options={}){
  const response=await fetch(url,{cache:"no-store",...options});
  const data=await response.json();
  if(!response.ok){const error=Error(data.error||`读取失败（${response.status}）`);error.status=response.status;throw error;}
  return data;
}

function renderList(){
  $("count-all").textContent=records.length;
  for(const [state,id]of[["OPEN","count-open"],["IN_PROGRESS","count-progress"],["RESOLVED","count-resolved"]])$(id).textContent=records.filter(r=>r.handling_status===state).length;
  const status=$("status-filter").value,query=$("search").value.trim().toLowerCase();
  const filtered=records.filter(r=>(!status||r.handling_status===status)&&(!query||[r.exception_id,r.shipment_id,r.carrier_name,r.origin_city,r.destination_city].join(" ").toLowerCase().includes(query)));
  const pages=Math.max(1,Math.ceil(filtered.length/pageSize));page=Math.min(page,pages);
  const rows=filtered.slice((page-1)*pageSize,page*pageSize);
  $("result-count").textContent=`当前范围 ${filtered.length} 条`;
  $("rows").innerHTML=rows.length?rows.map(r=>`<tr class="${selected?.exception_id===r.exception_id?"selected":""}"><td><button class="row-link" type="button" data-id="${escapeHTML(r.exception_id)}">${escapeHTML(r.exception_id)}</button><small>${escapeHTML(r.shipment_id)}</small></td><td>${escapeHTML(r.carrier_name)}<small>${escapeHTML(r.origin_city)} → ${escapeHTML(r.destination_city)}</small></td><td>${escapeHTML(types[r.exception_type]||r.exception_type)}</td><td><span class="badge ${r.handling_status}">${labels[r.handling_status]}</span><small>${r.saved_locally?"本地跟进记录":"源记录"}</small></td></tr>`).join(""):'<tr><td class="empty-row" colspan="4">没有符合条件的异常记录，试试其他筛选条件。</td></tr>';
  $("page-label").textContent=`第 ${page} / ${pages} 页`;
  $("previous").disabled=page<=1;$("next").disabled=page>=pages;
  $("rows").querySelectorAll("button[data-id]").forEach(button=>button.addEventListener("click",()=>{if(!busy)selectRecord(records.find(r=>r.exception_id===button.dataset.id));}));
}

function selectRecord(row){
  if(pendingConfirmation&&pendingConfirmation.id!==row?.exception_id)pendingConfirmation=null;
  selected=row;$("detail-empty").hidden=!!row;$("detail-body").hidden=!row;
  if(!row)return;
  $("exception-id").textContent=row.exception_id;
  $("record-status").textContent=labels[row.handling_status];$("record-status").className=`badge ${row.handling_status}`;
  $("record-origin").textContent=row.saved_locally?"本地跟进":"源记录";
  $("record-fields").innerHTML=[["运输单",row.shipment_id],["承运商",row.carrier_name],["线路",`${row.origin_city??"—"} → ${row.destination_city??"—"}`],["异常类型",types[row.exception_type]||row.exception_type],["跟进团队",row.assigned_team],["发现时间",formatTime(row.detected_epoch)]].map(([key,value])=>`<dt>${key}</dt><dd>${escapeHTML(value)}</dd>`).join("");
  $("source-state").textContent=`源记录状态：${labels[row.source_handling_status]}。源更新时间：${formatTime(row.source_updated_epoch)}。本机跟进不会修改源记录。`;
  $("next-status").replaceChildren(...nextStates[row.handling_status].map(state=>new Option(labels[state],state)));
  $("next-status").value=row.handling_status;$("note").value=row.follow_up_note||"";
  $("local-time").textContent=row.local_updated_at?`本机保存时间：${formatTime(row.local_updated_at)}`:"尚无本机保存记录";
  $("save-message").textContent="";renderList();
}

function setBusy(value){busy=value;$("save").disabled=value;$("read-record").disabled=value;$("reload").disabled=value;$("next-status").disabled=value;$("note").disabled=value;}
function replaceRecord(row){records=records.map(r=>r.exception_id===row.exception_id?row:r);selectRecord(row);}

async function load(){
  if(busy)return;
  $("workspace").hidden=true;$("error").hidden=true;$("loading").hidden=false;$("reload").disabled=true;
  try{
    const data=await api("/api/exceptions");records=data.rows;page=1;
    const chosen=selected&&records.find(r=>r.exception_id===selected.exception_id);
    selectRecord(chosen||null);renderList();$("workspace").hidden=false;
    $("source-info").textContent=`Databricks MCP · ${records.length} 条异常 · 读取于 ${formatTime(data.source.queried_at)} · ${(data.source.duration_ms/1000).toFixed(1)} 秒`;
  }catch(error){$("error-message").textContent=error.message;$("error").hidden=false;$("source-info").textContent="本次读取未完成";}
  finally{$("loading").hidden=true;$("reload").disabled=false;}
}

function saveMessage(text,success=false){$("save-message").className=success?"success":"failure";$("save-message").textContent=text;}
function confirmRecord(record,submission){
  if(!record||record.exception_id!==submission.id||record.handling_status!==submission.status||record.follow_up_note!==submission.note)return false;
  replaceRecord(record);pendingConfirmation=null;
  saveMessage("已保存到本机，并重新读取确认。",true);return true;
}
function unconfirmedMessage(submission,reason){
  saveMessage(`${submission.posted?"已提交但尚未确认":"提交结果未确认"}：${reason} 请重新读取本条记录核对。`);
}

$("followup-form").addEventListener("submit",async event=>{
  event.preventDefault();if(!selected||busy)return;
  const submission={id:selected.exception_id,status:$("next-status").value,note:$("note").value.trim(),expected_status:selected.handling_status,posted:false};
  pendingConfirmation=submission;setBusy(true);saveMessage("正在保存到本机…");
  try{
    await api(`/api/exceptions/${encodeURIComponent(submission.id)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:submission.status,note:submission.note,expected_status:submission.expected_status})});
    submission.posted=true;
    if(selected?.exception_id!==submission.id||pendingConfirmation!==submission)return;
    saveMessage("已提交，正在重新读取核对…");
    const data=await api(`/api/exceptions/${encodeURIComponent(submission.id)}`);
    if(selected?.exception_id!==submission.id||pendingConfirmation!==submission)return;
    if(!confirmRecord(data.record,submission))unconfirmedMessage(submission,"重读内容与本次提交不一致。");
  }catch(error){
    if(selected?.exception_id!==submission.id||pendingConfirmation!==submission)return;
    if(!submission.posted&&([400,404,409,501,502].includes(error.status))){
      pendingConfirmation=null;saveMessage(`保存失败：${error.message}`);
    }else unconfirmedMessage(submission,error.message);
  }finally{setBusy(false);}
});
$("read-record").addEventListener("click",async()=>{
  if(!selected||busy)return;
  const id=selected.exception_id,submission=pendingConfirmation;setBusy(true);
  try{
    const data=await api(`/api/exceptions/${encodeURIComponent(id)}`);
    if(selected?.exception_id!==id||pendingConfirmation!==submission)return;
    if(!data.record||data.record.exception_id!==id)throw Error("重读返回的异常编号不一致。");
    if(submission){
      if(!confirmRecord(data.record,submission)){
        replaceRecord(data.record);unconfirmedMessage(submission,"重读内容与本次提交不一致。");
      }
    }else{replaceRecord(data.record);saveMessage("已重新读取本条记录。",true);}
  }catch(error){
    if(selected?.exception_id!==id||pendingConfirmation!==submission)return;
    if(submission)unconfirmedMessage(submission,error.message);else saveMessage(error.message);
  }finally{setBusy(false);}
});
$("status-filter").addEventListener("change",()=>{page=1;renderList();});$("search").addEventListener("input",()=>{page=1;renderList();});
$("previous").addEventListener("click",()=>{page--;renderList();});$("next").addEventListener("click",()=>{page++;renderList();});
$("reload").addEventListener("click",load);$("retry").addEventListener("click",load);
load();
