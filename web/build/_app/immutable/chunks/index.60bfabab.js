import{a as r}from"./index.7deef04d.js";const s=async()=>{let n=null;const o=await fetch(`${r}/api/config`,{method:"GET",headers:{"Content-Type":"application/json"}}).then(async t=>{if(!t.ok)throw await t.json();return t.json()}).catch(t=>(console.log(t),n=t,null));if(n)throw n;return o},l=async()=>{let n=null;const o=await fetch(`${r}/api/changelog`,{method:"GET",headers:{"Content-Type":"application/json"}}).then(async t=>{if(!t.ok)throw await t.json();return t.json()}).catch(t=>(console.log(t),n=t,null));if(n)throw n;return o},h=async()=>{let n=null;const o=await fetch(`${r}/api/version/updates`,{method:"GET",headers:{"Content-Type":"application/json"}}).then(async t=>{if(!t.ok)throw await t.json();return t.json()}).catch(t=>(console.log(t),n=t,null));if(n)throw n;return o},u=async n=>{let o=null;const t=await fetch(`${r}/api/config/model/filter`,{method:"GET",headers:{"Content-Type":"application/json",Authorization:`Bearer ${n}`}}).then(async e=>{if(!e.ok)throw await e.json();return e.json()}).catch(e=>(console.log(e),o=e,null));if(o)throw o;return t},f=async(n,o,t)=>{let e=null;const i=await fetch(`${r}/api/config/model/filter`,{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${n}`},body:JSON.stringify({enabled:o,models:t})}).then(async a=>{if(!a.ok)throw await a.json();return a.json()}).catch(a=>(console.log(a),e=a,null));if(e)throw e;return i};export{h as a,l as b,u as c,s as g,f as u};
