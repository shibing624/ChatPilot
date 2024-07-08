import{s as I,E as G,f as v,a as w,g,N as C,c as T,j as f,i as x,F as K,G as J,H as Q,d as _,C as $,z as M,h as b,A as N,r as m,u as y,V as S,P as A,v as R,e as H,K as W,l as X,m as Y,n as ee}from"./scheduler.161605a7.js";import{S as D,i as E,a as V,t as L,b as U,d as z,m as F,e as O}from"./index.acd0f037.js";import{e as P}from"./each.65aa5674.js";function te(r){let e,a="Drop any files here to add to the conversation";return{c(){e=v("div"),e.textContent=a,this.h()},l(l){e=g(l,"DIV",{class:!0,"data-svelte-h":!0}),C(e)!=="svelte-1tl1xgp"&&(e.textContent=a),this.h()},h(){f(e,"class","mt-2 text-center text-sm dark:text-gray-200 w-full")},m(l,t){x(l,e,t)},p:$,d(l){l&&_(e)}}}function le(r){let e,a="📄",l,t,n="Add Files",s,c;const o=r[1].default,h=G(o,r,r[0],null),d=h||te();return{c(){e=v("div"),e.textContent=a,l=w(),t=v("div"),t.textContent=n,s=w(),d&&d.c(),this.h()},l(i){e=g(i,"DIV",{class:!0,"data-svelte-h":!0}),C(e)!=="svelte-g2aj7u"&&(e.textContent=a),l=T(i),t=g(i,"DIV",{class:!0,"data-svelte-h":!0}),C(t)!=="svelte-1szmb4c"&&(t.textContent=n),s=T(i),d&&d.l(i),this.h()},h(){f(e,"class","text-center text-6xl mb-3"),f(t,"class","text-center dark:text-white text-2xl font-semibold z-50")},m(i,u){x(i,e,u),x(i,l,u),x(i,t,u),x(i,s,u),d&&d.m(i,u),c=!0},p(i,[u]){h&&h.p&&(!c||u&1)&&K(h,o,i,i[0],c?Q(o,i[0],u,null):J(i[0]),null)},i(i){c||(V(d,i),c=!0)},o(i){L(d,i),c=!1},d(i){i&&(_(e),_(l),_(t),_(s)),d&&d.d(i)}}}function se(r,e,a){let{$$slots:l={},$$scope:t}=e;return r.$$set=n=>{"$$scope"in n&&a(0,t=n.$$scope)},[t,l]}class me extends D{constructor(e){super(),E(this,e,se,le,I,{})}}function Z(r){let e,a,l,t,n='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3"><path fill-rule="evenodd" d="M12.416 3.376a.75.75 0 0 1 .208 1.04l-5 7.5a.75.75 0 0 1-1.154.114l-3-3a.75.75 0 0 1 1.06-1.06l2.353 2.353 4.493-6.74a.75.75 0 0 1 1.04-.207Z" clip-rule="evenodd"></path></svg>',s,c;return{c(){e=v("div"),a=v("input"),l=w(),t=v("button"),t.innerHTML=n,this.h()},l(o){e=g(o,"DIV",{class:!0});var h=b(e);a=g(h,"INPUT",{class:!0,placeholder:!0}),l=T(h),t=g(h,"BUTTON",{type:!0,"data-svelte-h":!0}),C(t)!=="svelte-v680sa"&&(t.innerHTML=n),h.forEach(_),this.h()},h(){f(a,"class","cursor-pointer self-center text-xs h-fit bg-transparent outline-none line-clamp-1 w-[4rem]"),f(a,"placeholder","Add a tag"),f(t,"type","button"),f(e,"class","flex items-center")},m(o,h){x(o,e,h),m(e,a),A(a,r[1]),m(e,l),m(e,t),s||(c=[y(a,"input",r[3]),y(t,"click",r[4])],s=!0)},p(o,h){h&2&&a.value!==o[1]&&A(a,o[1])},d(o){o&&_(e),s=!1,R(c)}}}function ae(r){let e,a,l,t,n,s,c,o,h,d=r[0]&&Z(r);return{c(){e=v("div"),d&&d.c(),a=w(),l=v("button"),t=v("div"),n=M("svg"),s=M("path"),this.h()},l(i){e=g(i,"DIV",{class:!0});var u=b(e);d&&d.l(u),a=T(u),l=g(u,"BUTTON",{class:!0,type:!0});var p=b(l);t=g(p,"DIV",{class:!0});var k=b(t);n=N(k,"svg",{xmlns:!0,viewBox:!0,fill:!0,class:!0});var B=b(n);s=N(B,"path",{d:!0}),b(s).forEach(_),B.forEach(_),k.forEach(_),p.forEach(_),u.forEach(_),this.h()},h(){f(s,"d","M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"),f(n,"xmlns","http://www.w3.org/2000/svg"),f(n,"viewBox","0 0 16 16"),f(n,"fill","currentColor"),f(n,"class",c="w-3 h-3 "+(r[0]?"rotate-45":"")+" transition-all transform"),f(t,"class","m-auto self-center"),f(l,"class","cursor-pointer self-center p-0.5 space-x-1 flex h-fit items-center dark:hover:bg-gray-700 rounded-full transition border dark:border-gray-600 border-dashed"),f(l,"type","button"),f(e,"class","flex space-x-1 pl-1.5")},m(i,u){x(i,e,u),d&&d.m(e,null),m(e,a),m(e,l),m(l,t),m(t,n),m(n,s),o||(h=y(l,"click",r[5]),o=!0)},p(i,[u]){i[0]?d?d.p(i,u):(d=Z(i),d.c(),d.m(e,a)):d&&(d.d(1),d=null),u&1&&c!==(c="w-3 h-3 "+(i[0]?"rotate-45":"")+" transition-all transform")&&f(n,"class",c)},i:$,o:$,d(i){i&&_(e),d&&d.d(),o=!1,h()}}}function ne(r,e,a){const l=S();let t=!1,n="";function s(){n=this.value,a(1,n)}return[t,n,l,s,()=>{l("add",n),a(1,n=""),a(0,t=!1)},()=>{a(0,t=!t)}]}class re extends D{constructor(e){super(),E(this,e,ne,ae,I,{})}}function j(r,e,a){const l=r.slice();return l[3]=e[a],l}function q(r){let e,a,l=r[3].name+"",t,n,s,c='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3"><path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z"></path></svg>',o,h,d;function i(){return r[2](r[3])}return{c(){e=v("div"),a=v("div"),t=X(l),n=w(),s=v("button"),s.innerHTML=c,o=w(),this.h()},l(u){e=g(u,"DIV",{class:!0});var p=b(e);a=g(p,"DIV",{class:!0});var k=b(a);t=Y(k,l),k.forEach(_),n=T(p),s=g(p,"BUTTON",{class:!0,"data-svelte-h":!0}),C(s)!=="svelte-1uiqlcf"&&(s.innerHTML=c),o=T(p),p.forEach(_),this.h()},h(){f(a,"class","text-[0.7rem] font-medium self-center line-clamp-1"),f(s,"class","m-auto self-center cursor-pointer"),f(e,"class","px-2 py-0.5 space-x-1 flex h-fit items-center rounded-full transition border dark:border-gray-600 dark:text-white")},m(u,p){x(u,e,p),m(e,a),m(a,t),m(e,n),m(e,s),m(e,o),h||(d=y(s,"click",i),h=!0)},p(u,p){r=u,p&1&&l!==(l=r[3].name+"")&&ee(t,l)},d(u){u&&_(e),h=!1,d()}}}function ie(r){let e,a=P(r[0]),l=[];for(let t=0;t<a.length;t+=1)l[t]=q(j(r,a,t));return{c(){for(let t=0;t<l.length;t+=1)l[t].c();e=H()},l(t){for(let n=0;n<l.length;n+=1)l[n].l(t);e=H()},m(t,n){for(let s=0;s<l.length;s+=1)l[s]&&l[s].m(t,n);x(t,e,n)},p(t,[n]){if(n&3){a=P(t[0]);let s;for(s=0;s<a.length;s+=1){const c=j(t,a,s);l[s]?l[s].p(c,n):(l[s]=q(c),l[s].c(),l[s].m(e.parentNode,e))}for(;s<l.length;s+=1)l[s].d(1);l.length=a.length}},i:$,o:$,d(t){t&&_(e),W(l,t)}}}function oe(r,e,a){const l=S();let{tags:t=[]}=e;const n=s=>{l("delete",s.name)};return r.$$set=s=>{"tags"in s&&a(0,t=s.tags)},[t,l,n]}class ce extends D{constructor(e){super(),E(this,e,oe,ie,I,{tags:0})}}function de(r){let e,a,l,t,n;return a=new ce({props:{tags:r[0]}}),a.$on("delete",r[3]),t=new re({}),t.$on("add",r[4]),{c(){e=v("div"),U(a.$$.fragment),l=w(),U(t.$$.fragment),this.h()},l(s){e=g(s,"DIV",{class:!0});var c=b(e);z(a.$$.fragment,c),l=T(c),z(t.$$.fragment,c),c.forEach(_),this.h()},h(){f(e,"class","flex flex-row space-x-0.5 line-clamp-1")},m(s,c){x(s,e,c),F(a,e,null),m(e,l),F(t,e,null),n=!0},p(s,[c]){const o={};c&1&&(o.tags=s[0]),a.$set(o)},i(s){n||(V(a.$$.fragment,s),V(t.$$.fragment,s),n=!0)},o(s){L(a.$$.fragment,s),L(t.$$.fragment,s),n=!1},d(s){s&&_(e),O(a),O(t)}}}function ue(r,e,a){let{tags:l=[]}=e,{deleteTag:t}=e,{addTag:n}=e;const s=o=>{t(o.detail)},c=o=>{n(o.detail)};return r.$$set=o=>{"tags"in o&&a(0,l=o.tags),"deleteTag"in o&&a(1,t=o.deleteTag),"addTag"in o&&a(2,n=o.addTag)},[l,t,n,s,c]}class ve extends D{constructor(e){super(),E(this,e,ue,de,I,{tags:0,deleteTag:1,addTag:2})}}export{me as A,ve as T};