"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"..","static","app.js"),"utf8");
const original={exception_id:"EXC1",shipment_id:"SHP1",handling_status:"OPEN",source_handling_status:"OPEN",follow_up_note:"源备注",source_updated_epoch:null,saved_locally:false,local_updated_at:null};
const saved={...original,handling_status:"IN_PROGRESS",follow_up_note:"跟进",saved_locally:true,local_updated_at:"2026-11-16T13:00:00+00:00"};
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const reply=(data,status=200)=>({ok:status>=200&&status<300,status,json:async()=>data});

async function harness(rows=[original,{...original,exception_id:"EXC2"}]){
  const elements=new Map(),calls=[],responses=[];
  const get=id=>{
    if(!elements.has(id))elements.set(id,{value:"",textContent:"",innerHTML:"",disabled:false,hidden:false,className:"",listeners:{},addEventListener(name,callback){this.listeners[name]=callback;},replaceChildren(...children){this.children=children;},querySelectorAll(){return [];}});
    return elements.get(id);
  };
  const context=vm.createContext({document:{getElementById:get},Option:function(text,value){this.text=text;this.value=value;},Intl,Date,console,
    fetch:async(url,options)=>{
      calls.push({url,options});
      if(calls.length===1)return reply({rows,source:{queried_at:"2026-11-16T13:00:00Z",duration_ms:10}});
      if(!responses.length)throw Error("Unexpected fetch");
      const next=responses.shift();
      if(next instanceof Error)throw next;
      return typeof next==="function"?next():next;
    }});
  vm.runInContext(source,context);
  await tick();
  vm.runInContext("selectRecord(records[0])",context);
  calls.length=0;
  // The initial list is already loaded; every subsequent request uses the queue.
  context.fetch=async(url,options)=>{
    calls.push({url,options});
    if(!responses.length)throw Error("Unexpected fetch");
    const next=responses.shift();
    if(next instanceof Error)throw next;
    return typeof next==="function"?next():next;
  };
  get("next-status").value="IN_PROGRESS";get("note").value="  跟进  ";
  return {get,calls,responses,context,submit:()=>get("followup-form").listeners.submit({preventDefault(){}}),read:()=>get("read-record").listeners.click(),run:code=>vm.runInContext(code,context)};
}

function enabled(h){for(const id of ["save","read-record","reload","next-status","note"])assert.equal(h.get(id).disabled,false,id);}

test("POST then independent GET confirms normalized content and recomputes counts",async()=>{
  const h=await harness();
  h.responses.push(reply({record:saved,saved_to:"local"}),reply({record:saved}));
  await h.submit();
  assert.deepEqual(h.calls.map(c=>c.url),["/api/exceptions/EXC1","/api/exceptions/EXC1"]);
  assert.equal(h.calls[0].options.method,"POST");
  assert.deepEqual(JSON.parse(h.calls[0].options.body),{status:"IN_PROGRESS",note:"跟进",expected_status:"OPEN"});
  assert.match(h.get("save-message").textContent,/已保存到本机，并重新读取确认/);
  assert.equal(h.run("records[0].handling_status"),"IN_PROGRESS");
  assert.equal(h.run("records[1].handling_status"),"OPEN");
  assert.equal(h.get("count-progress").textContent,1);
  assert.equal(h.get("count-open").textContent,1);
  enabled(h);
});

for(const [field,value]of [["exception_id","OTHER"],["handling_status","OPEN"],["follow_up_note","其他备注"]]){
  test(`GET mismatch in ${field} never confirms`,async()=>{
    const h=await harness();h.responses.push(reply({record:saved}),reply({record:{...saved,[field]:value}}));
    await h.submit();assert.match(h.get("save-message").textContent,/尚未确认/);assert.notEqual(h.get("save-message").className,"success");
    assert.equal(h.run("selected.exception_id"),"EXC1");enabled(h);
  });
}

test("POST success but GET failure can be confirmed by manual reread",async()=>{
  const h=await harness();h.responses.push(reply({record:saved}),new Error("读取断开"));
  await h.submit();assert.match(h.get("save-message").textContent,/已提交但尚未确认/);assert.equal(h.get("note").value,"  跟进  ");
  h.responses.push(reply({record:saved}));await h.read();
  assert.match(h.get("save-message").textContent,/重新读取确认/);assert.equal(h.calls.filter(c=>c.options.method==="POST").length,1);enabled(h);
});

for(const status of [400,404,409]){
  test(`explicit POST rejection ${status} preserves draft without GET`,async()=>{
    const h=await harness();h.responses.push(reply({error:status===409?"状态已变化，请重新读取。":"请求被拒绝"},status));
    await h.submit();assert.match(h.get("save-message").textContent,/保存失败/);assert.equal(h.calls.length,1);
    assert.equal(h.get("note").value,"  跟进  ");enabled(h);
    if(status===409){h.responses.push(reply({record:saved}));await h.read();assert.equal(h.run("selected.handling_status"),"IN_PROGRESS");assert.equal(h.get("save-message").textContent,"已重新读取本条记录。");}
  });
}

for(const [name,response]of [["network",new Error("连接中断")],["500",reply({error:"本机读写失败"},500)],["invalid JSON",{ok:true,status:200,json:async()=>{throw Error("invalid JSON");}}]]){
  test(`uncertain POST ${name} is not presented as definitely unwritten`,async()=>{
    const h=await harness();h.responses.push(response);await h.submit();
    assert.match(h.get("save-message").textContent,/提交结果未确认/);assert.equal(h.get("note").value,"  跟进  ");enabled(h);
    h.responses.push(reply({record:saved}));await h.read();assert.match(h.get("save-message").textContent,/重新读取确认/);
  });
}

test("busy prevents repeated submissions through POST and GET",async()=>{
  const h=await harness();let finishPost,finishGet;
  h.responses.push(()=>new Promise(resolve=>{finishPost=resolve;}),()=>new Promise(resolve=>{finishGet=resolve;}));
  const pending=h.submit();await h.submit();await h.submit();
  assert.equal(h.calls.length,1);assert.equal(h.get("save").disabled,true);
  finishPost(reply({record:saved}));await tick();await h.submit();
  assert.equal(h.calls.length,2);assert.equal(h.get("note").disabled,true);
  finishGet(reply({record:saved}));await pending;enabled(h);
});

test("switching record abandons old pending confirmation",async()=>{
  const h=await harness();h.responses.push(reply({record:saved}),new Error("read failed"));await h.submit();
  h.run("selectRecord(records[1])");h.responses.push(reply({record:{...original,exception_id:"EXC2"}}));await h.read();
  assert.equal(h.get("save-message").textContent,"已重新读取本条记录。");
});

test("late response cannot confirm a different selected record",async()=>{
  const h=await harness();let finishGet;h.responses.push(reply({record:saved}),()=>new Promise(resolve=>{finishGet=resolve;}));
  const pending=h.submit();await tick();h.run("selectRecord(records[1])");finishGet(reply({record:saved}));await pending;
  assert.equal(h.run("selected.exception_id"),"EXC2");assert.doesNotMatch(h.get("save-message").textContent,/已保存/);enabled(h);
});

test("manual reread retains unconfirmed mismatch and later confirms",async()=>{
  const h=await harness();h.responses.push(reply({record:saved}),reply({record:{...saved,follow_up_note:"其他"}}));await h.submit();
  h.responses.push(reply({record:{...saved,follow_up_note:"其他"}}));await h.read();assert.match(h.get("save-message").textContent,/尚未确认/);
  h.responses.push(reply({record:saved}));await h.read();assert.match(h.get("save-message").textContent,/重新读取确认/);
});

test("reload displays persisted overlay with source time, filters and pagination",async()=>{
  const h=await harness([saved,...Array.from({length:10},(_,i)=>({...original,exception_id:`OTHER${i}`}))]);
  assert.match(h.get("source-state").textContent,/源更新时间：—/);
  assert.match(h.get("local-time").textContent,/本机保存时间/);
  assert.match(h.get("page-label").textContent,/1 \/ 2/);
  h.get("status-filter").value="IN_PROGRESS";h.get("status-filter").listeners.change();assert.equal(h.get("result-count").textContent,"当前范围 1 条");
  h.responses.push(reply({rows:[{...saved,source_updated_epoch:1794834000}],source:{queried_at:"2026-11-16T13:00:00Z",duration_ms:10}}));
  await h.run("load()");assert.equal(h.get("note").value,"跟进");assert.match(h.get("source-state").textContent,/源更新时间：2026/);assert.equal(h.get("save-message").textContent,"");
});
