(function(root){'use strict';
let atlas,rects,planes,texture,pending;const cache=new Map();
const dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function image(url){return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=url;});}
function load(){if(pending)return pending;return pending=Promise.all([image('../wall-height121/wall22.png'),fetch('../wall-height121/rects121.json').then(r=>r.json()),fetch('../wall-height121/planes121.json').then(r=>r.json()),image('../promise168/assets/wall-native.png')]).then(([a,r,p,t])=>{atlas=a;rects=r;planes=p;const c=document.createElement('canvas');c.width=t.width;c.height=t.height;c.getContext('2d').drawImage(t,0,0);texture={w:t.width,h:t.height,data:c.getContext('2d').getImageData(0,0,t.width,t.height).data};});}
function maskAt(cells,w,h,x,y){let mask=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<w&&yy<h&&cells[yy*w+xx]===0)mask|=1<<i;});return mask;}
function tile(mask,x,y){const pillar=(x+2*y)%4===0,key=mask+':'+(x%4)+':'+(y%2)+':'+pillar;if(cache.has(key))return cache.get(key);const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');q.drawImage(atlas,...rects[mask+':0'],0,0,32,32);const a=q.getImageData(0,0,32,32),face=planes[String(mask)];
for(let py=0;py<32;py++)for(let px=0;px<32;px++){const i=(py*32+px)*4;if(!a.data[i+3])continue;const l=(a.data[i]+a.data[i+1]+a.data[i+2])/3,ti=((((y*32+py)%texture.h)*texture.w)+(x*32+px)%texture.w)*4,t=Array.from(texture.data.slice(ti,ti+3)),tl=(t[0]+t[1]+t[2])/3,front=face[py*32+px]==='1';let color;
if(l<30)color=[27,33,43];
else if(l>110)color=l>136?[170,158,126]:[139,132,110];
else if(front){color=l<39?[73,76,75]:t;if(pillar&&px>=12&&px<=15&&py>=11&&py<=30)color=px===15?[151,132,87]:[43,53,73];}
else color=t.map((v,k)=>Math.round(v*.32+[17,22,32][k]));
for(let k=0;k<3;k++)a.data[i+k]=color[k];}
q.putImageData(a,0,0);cache.set(key,c);return c;}
function wall(q,cells,w,h,x,y,t=32){q.drawImage(tile(maskAt(cells,w,h,x,y),x,y),x*t,y*t,t,t);}
root.PromiseWall168={load,wall,tile,maskAt};
})(globalThis);
