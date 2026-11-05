(function(root){
'use strict';
const members=typeof module!=='undefined'&&module.exports?require('./members.js'):root.MarketMembers;
const catalog=typeof module!=='undefined'&&module.exports?require('./merch-catalog.js'):root.MerchCatalog;
const byId=Object.fromEntries(members.map(m=>[m.id,m])),fixtures=Object.fromEntries(catalog.map(p=>[p.id,p]));
let sprites={},shirts={};
function rng(seed){let h=2166136261;for(const c of seed)h=Math.imul(h^c.charCodeAt(0),16777619);return()=>{h+=0x6D2B79F5;let t=h;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
function select(seed,floor,fixture,mix=0){
 const random=rng(`${seed}:F${floor}:${fixture.type}:${fixture.x},${fixture.y}:stock${mix}`),pool=members.map(m=>m.id),result=[];
 for(let i=0;i<Math.min(3,pool.length);i++){const j=Math.floor(random()*pool.length);result.push(pool.splice(j,1)[0]);}
 return result;
}
function tint(hex,factor){const s=hex.slice(1);return '#'+[0,2,4].map(i=>Math.min(255,Math.round(parseInt(s.slice(i,i+2),16)*factor)).toString(16).padStart(2,'0')).join('');}
function makeSprites(images){
 for(const m of members){
   const canvas=document.createElement('canvas');canvas.width=16;canvas.height=24;const c=canvas.getContext('2d');c.imageSmoothingEnabled=false;
   const image=images['member-'+m.id];if(!image)throw Error('Missing member art: '+m.id);
   for(const[dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]])c.drawImage(image,2+dx,1+dy,12,20);
   c.globalCompositeOperation='source-in';c.fillStyle='#b9c6cb';c.fillRect(0,0,16,24);c.globalCompositeOperation='source-over';c.drawImage(image,2,1,12,20);
   c.fillStyle='#77888e';c.fillRect(2,21,12,2);c.fillStyle='#c1d2d5';c.fillRect(3,21,10,1);sprites[m.id]=canvas;
   const shirt=document.createElement('canvas');shirt.width=shirt.height=16;const s=shirt.getContext('2d');s.imageSmoothingEnabled=false;
   s.beginPath();s.moveTo(5,2);for(const[x,y]of [[2,3],[0,7],[3,9],[4,7],[4,14],[12,14],[12,7],[13,9],[16,7],[14,3],[11,2],[10,4],[6,4]])s.lineTo(x,y);s.closePath();s.fillStyle=tint(m.color,.85);s.fill();s.strokeStyle='#252b2e';s.lineWidth=1;s.stroke();
   s.fillStyle=tint(m.color,.58);s.fillRect(11,8,1,5);s.fillRect(4,13,8,1);s.fillStyle='#d3d5ce';s.fillRect(7,7,2,2);shirts[m.id]=shirt;
 }
}
function draw(ctx,fixture,map,images,t,mix=0){
 const meta=fixtures[fixture.type];if(!meta)throw Error('Unknown fixture: '+fixture.type);
 const w=meta.kind==='wall'?2*t:t,x=fixture.x*t,y=fixture.y*t,scale=t/32;
 ctx.drawImage(images[meta.id],x,y,w,t);
 if(!['acrylic','shirts'].includes(meta.content))return;
 const ids=select(map.seed,map.floorNumber,fixture,mix);
 ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);ctx.imageSmoothingEnabled=false;
 if(meta.content==='acrylic'){
   const points=meta.kind==='wall'?[[10,8,12,18],[26,8,12,18],[42,8,12,18]]:[[3,6,8,13],[12,6,8,13],[21,6,8,13]];
   ids.forEach((id,i)=>ctx.drawImage(sprites[id],...points[i]));
 }else if(meta.kind==='wall')ids.forEach((id,i)=>ctx.drawImage(shirts[id],9+i*16,11,13,13));
 else ids.forEach((id,i)=>{ctx.fillStyle=tint(byId[id].color,.48);ctx.fillRect(3+i*8,13+i*3,8,4);ctx.drawImage(shirts[id],3+i*8,8+i*3,10,10);});
 ctx.restore();
}
function describe(fixture,map,mix=0){
 const meta=fixtures[fixture.type];if(!meta)return '';
 return meta.name+(['acrylic','shirts'].includes(meta.content)?' · '+select(map.seed,map.floorNumber,fixture,mix).map(id=>byId[id].name).join(' / '):'');
}
function gallery(images){
 const grid=document.getElementById('propSwatches');if(!grid)return;
 grid.replaceChildren();for(const fixture of catalog){const f=document.createElement('figure'),c=document.createElement('canvas'),caption=document.createElement('figcaption');c.width=fixture.width;c.height=32;const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;draw(ctx,{type:fixture.id,x:0,y:0},{seed:'CATALOG',floorNumber:4},images,32,0);caption.textContent=fixture.name;f.append(c,caption);grid.append(f);}
 const count=document.getElementById('memberCount');if(count)count.textContent=members.length+'명';
}
const api={members,catalog,select,makeSprites,draw,describe,gallery,getSprite:id=>sprites[id],getShirt:id=>shirts[id]};root.MarketStock=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
