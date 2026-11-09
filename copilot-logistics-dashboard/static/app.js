"use strict";
const $ = (id) => document.getElementById(id);
const fmt = (n) => new Intl.NumberFormat("zh-CN").format(n);
const pct = (n) => n === null || n === undefined ? "N/A" : `${(Number(n)*100).toFixed(2)}%`;
const escapeHTML = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const time = (epoch) => epoch === null || epoch === undefined ? "—" : new Intl.DateTimeFormat("zh-CN", {timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).format(new Date(Number(epoch)*1000)).replaceAll("/","-");
const statuses = {ON_TIME:"准时送达",DELAYED:"延误送达",CANCELLED:"已取消",IN_TRANSIT:"运输中",MISSING_TIMESTAMP:"时间缺失"};
let current = null;
let pageNumber = 1;
let sequence = 0;

function bars(rows) {
  $("carrier-chart").innerHTML = rows.length ? rows.map((r) => `<div class="bar-row"><div class="bar-name">${escapeHTML(r.carrier_name)}<small>${escapeHTML(r.carrier_id)}</small></div><div class="track"><div class="bar" style="width:${r.on_time_rate === null ? 0 : Math.max(0,Math.min(100,r.on_time_rate*100))}%"></div></div><div class="bar-value">${pct(r.on_time_rate)}<small>${fmt(r.on_time_count)} / ${fmt(r.eligible_count)}</small></div></div>`).join("") : '<div class="empty">当前范围没有承运商数据</div>';
}

function trend(rows) {
  if (!rows.length) { $("trend-chart").innerHTML = '<div class="empty">当前范围暂无运输记录<span>清除筛选可查看整体结果</span></div>'; return; }
  const style = getComputedStyle($("trend-chart"));
  const w = Math.max(260,$("trend-chart").clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight)), h=210;
  const l=33, r=14, t=12, b=32;
  const max = Math.max(4,Math.ceil(Math.max(...rows.map((v)=>v.count))/4)*4);
  const x = (i) => l+(rows.length === 1 ? 0.5 : i/(rows.length-1))*(w-l-r);
  const y = (v) => h-b-(v/max)*(h-t-b);
  const coords = rows.map((v,i)=>`${x(i)},${y(v.count)}`);
  const grid = [0,.5,1].map((n)=>`<line x1="${l}" x2="${w-r}" y1="${y(n*max)}" y2="${y(n*max)}" stroke="#e1e9ef"/><text x="${l-8}" y="${y(n*max)+4}" text-anchor="end">${n*max}</text>`).join("");
  const ticks = [...new Set([0,Math.floor((rows.length-1)/2),rows.length-1])].map((i)=>`<text x="${x(i)}" y="${h-7}" text-anchor="middle">${escapeHTML(rows[i].date.slice(5))}</text>`).join("");
  const points = rows.map((v,i)=>`<circle cx="${x(i)}" cy="${y(v.count)}" r="2.2" fill="#087f86"><title>${escapeHTML(v.date)}：${v.count} 单</title></circle>`).join("");
  $("trend-chart").innerHTML = `<svg class="trend" viewBox="0 0 ${w} ${h}" role="img" aria-label="每日运输单量，${rows.length}个自然日">${grid}<polygon points="${x(0)},${y(0)} ${coords.join(" ")} ${x(rows.length-1)},${y(0)}" fill="#e9f4f4"/><polyline points="${coords.join(" ")}" fill="none" stroke="#087f86" stroke-width="2"/>${points}${ticks}</svg>`;
}

function render(data) {
  current = data;
  const m=data.summary;
  $("scope").textContent=data.scope;
  $("total").textContent=fmt(m.shipment_count);
  $("eligible").textContent=fmt(m.eligible_count);
  $("rate").textContent=pct(m.on_time_rate);
  $("delayed").textContent=fmt(m.delayed_count);
  $("on-time").textContent=fmt(m.on_time_count);
  $("denominator").textContent=fmt(m.eligible_count);
  $("excluded").textContent=fmt(m.excluded_count);
  $("rate-note").textContent=m.eligible_count ? `${fmt(m.on_time_count)} 单准时 / ${fmt(m.eligible_count)} 单有效` : "当前范围无有效分母";
  $("carrier").replaceChildren(new Option("全部承运商",""),...data.carriers.map((r)=>new Option(`${r.carrier_name} · ${r.carrier_id}`,r.carrier_id)));
  $("carrier").value=data.selected_carrier;
  bars(data.by_carrier);
  trend(data.daily);
  $("detail-total").textContent=`共 ${fmt(m.shipment_count)} 单`;
  $("detail-note").textContent=`${data.scope} · 业务日期倒序 · 每页 ${data.page_size} 条`;
  $("rows").innerHTML=data.shipments.length ? data.shipments.map((r)=>`<tr data-carrier="${escapeHTML(r.carrier_id)}"><td>${escapeHTML(r.shipment_id)}</td><td>${escapeHTML(r.carrier_name)}</td><td>${escapeHTML(r.shipment_date)}</td><td>${escapeHTML(r.origin_city)} → ${escapeHTML(r.destination_city)}</td><td>${escapeHTML(time(r.planned_epoch))}</td><td>${escapeHTML(time(r.actual_epoch))}</td><td><span class="result ${escapeHTML(r.result)}">${statuses[r.result]??escapeHTML(r.result)}</span></td></tr>`).join("") : '<tr><td colspan="7">当前范围暂无运输记录。</td></tr>';
  $("page-info").textContent=`第 ${data.page} / ${data.page_count} 页 · 本页 ${data.shipments.length} 条`;
  $("previous").disabled=data.page<=1;
  $("next").disabled=data.page>=data.page_count;
  $("snapshot").textContent=`数据快照：${time(data.snapshot_epoch)}（上海时间）`;
  $("updated").textContent=`查询完成于 ${time(Date.parse(data.source.queried_at)/1000)}`;
  $("query-note").textContent=`MCP 只读查询 · 耗时 ${(data.source.duration_ms/1000).toFixed(1)} 秒`;
}

async function load() {
  const id=++sequence;
  const params=new URLSearchParams({carrier:$("carrier").value,page:String(pageNumber)});
  $("results").hidden=true;
  $("error").hidden=true;
  $("loading").hidden=false;
  $("updated").textContent="正在查询 Databricks…";
  try {
    const response=await fetch(`/api/dashboard?${params}`,{cache:"no-store"});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||`查询失败（HTTP ${response.status}）`);
    if(id!==sequence)return;
    $("results").hidden=false;
    render(data);
  } catch(error) {
    if(id!==sequence)return;
    $("results").hidden=true;
    $("error-message").textContent=error.message;
    $("error").hidden=false;
    $("updated").textContent="查询未完成";
  } finally {
    if(id===sequence)$("loading").hidden=true;
  }
}

$("carrier").addEventListener("change",()=>{pageNumber=1;load();});
$("clear").addEventListener("click",()=>{$("carrier").value="";pageNumber=1;load();});
$("refresh").addEventListener("click",load);
$("retry").addEventListener("click",load);
$("previous").addEventListener("click",()=>{pageNumber=Math.max(1,pageNumber-1);load();});
$("next").addEventListener("click",()=>{if(current&&pageNumber<current.page_count){pageNumber++;load();}});
window.addEventListener("resize",()=>{if(current&&!$("results").hidden)trend(current.daily);});
load();
