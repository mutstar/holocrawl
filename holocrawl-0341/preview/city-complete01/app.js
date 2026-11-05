"use strict";
const $=id=>document.getElementById(id),canvas=$('field'),ctx=canvas.getContext('2d'),images={},tiles=[],wallRuns=new Map();
let selected=0,wallOld=false,opened=new Set(),mix=0;
const palette=['rock_wall','floor','closed_door','stone_stairs_up_i','stone_stairs_down_i','shallow_water','deep_water'];
const m={w:42,h:30,seed:'CITY-ALL-ART-01',floorNumber:4,palette,rows:Array.from({length:30},()=>Array(42).fill(0))},maps=[m];
const rect=(x,y,w,h,v=1)=>{for(let yy=y;yy<y+h;yy++)for(let xx=x;xx<x+w;xx++)m.rows[yy][xx]=v;};
// Deliberate review layout: connected irregular street spaces, not a native generator sample.
rect(2,3,15,11);rect(5,14,12,9);rect(3,22,20,5);rect(17,8,10,5);rect(17,17,9,6);rect(22,3,17,10);rect(25,13,14,14);rect(21,24,6,3);
rect(10,4,4,4,0);rect(10,8,1,4,0);rect(11,11,5,1,0);m.rows[10][10]=2;m.rows[11][13]=2;
rect(22,4,4,3,0);rect(29,14,5,3,0);rect(25,18,1,4,0);m.rows[20][25]=2;
rect(33,21,5,5,5);rect(34,22,3,3,6);m.rows[21][33]=1;m.rows[25][37]=1;
m.rows[6][5]=3;m.rows[24][20]=4;
const fixtures=[['acrylic-window',27,2],['closed-shutter',33,2],['half-shutter',36,2],['shirt-window',23,6],['poster-wall',10,7],['acrylic-rack',28,5],['shirt-stack',26,8],['hoodie-rack',36,7],['plush-basket',31,10],['poster-rolls',24,11],['keychain-hooks',37,10],['badge-trays',33,5],['shopping-bags',28,11],['delivery-boxes',27,17],['open-carton',29,19],['delivery-cart',37,17],['folding-crates',27,24],['trash-bags',6,20],['paper-rubbish',7,23],['recycling-bins',10,21]].map(([type,x,y])=>({type,x,y}));
const fences=[{x:5,y:12},{x:6,y:12},{x:7,y:12},{x:8,y:12},{x:16,y:18},{x:17,y:18},{x:18,y:18}];
const mounted=[{kind:0,x:5,y:2},{kind:1,x:8,y:2},{kind:2,x:13,y:2},{kind:3,x:30,y:16}];
function draw(){ctx.imageSmoothingEnabled=false;ctx.fillStyle='#080b0b';ctx.fillRect(0,0,canvas.width,canvas.height);for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)tile(ctx,m,x,y,x*32,y*32,32);
for(const p of mounted){const x=p.x*32,y=p.y*32;ctx.filter='brightness(1.35)';if(p.kind===0)texture(ctx,[289,34,37,19],x+2,y+9,27,14);if(p.kind===2)texture(ctx,[294,86,22,16],x+5,y+9,22,16);if(p.kind===3)texture(ctx,[183,31,32,12],x,y+7,32,12);if(p.kind===1){ctx.filter='none';ctx.strokeStyle='#292e2a';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(x+4,y+4);ctx.lineTo(x+19,y+4);ctx.lineTo(x+19,y+28);ctx.stroke();ctx.strokeStyle='#92938b';ctx.lineWidth=2;ctx.stroke();}ctx.filter='none';}
for(const p of fixtures)MarketStock.draw(ctx,p,m,images,32,mix);for(const p of fences)ctx.drawImage(images.fence,p.x*32,p.y*32+10,32,22);
}
function locate(e){const r=canvas.getBoundingClientRect();return{x:Math.floor((e.clientX-r.left)*canvas.width/r.width/32),y:Math.floor((e.clientY-r.top)*canvas.height/r.height/32)};}
canvas.onmousemove=e=>{const{x,y}=locate(e),p=fixtures.find(p=>p.y===y&&x>=p.x&&x<p.x+(MerchCatalog.find(a=>a.id===p.type).kind==='wall'?2:1));if(p)$('info').textContent=MarketStock.describe(p,m,mix);else $('info').textContent=isWater(feature(m,x,y))?(feature(m,x,y)==='deep_water'?'깊은 물':'얕은 물'):isDoor(feature(m,x,y))?'철제 문 · 클릭해서 열기/닫기':isUp(feature(m,x,y))?'올라가는 원형 계단':isDown(feature(m,x,y))?'내려가는 원형 계단':'잔향도시 · 전체 도트 검토용 배치';};
canvas.onclick=e=>{const{x,y}=locate(e);if(isDoor(feature(m,x,y))){const k=doorKey(x,y);opened.has(k)?opened.delete(k):opened.add(k);draw();}};
function fit(value){canvas.classList.toggle('fit',value);$('fit').textContent=value?'원래 크기 32×32로 보기':'전체 지도 맞춰 보기';}
$('fit').onclick=()=>fit(!canvas.classList.contains('fit'));
$('doors').onclick=()=>{const opening=!opened.size;opened.clear();if(opening)for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)if(isDoor(feature(m,x,y)))opened.add(doorKey(x,y));$('doors').textContent=opening?'문 모두 닫기':'문 모두 열기';draw();};
$('stock').onclick=()=>{mix++;draw();gallery();};
document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{fit(false);const[x,y]=b.dataset.go.split(',').map(Number),v=$('viewport');v.scrollTo({left:x*32-v.clientWidth/2,top:y*32-v.clientHeight/2,behavior:'smooth'});});
function gallery(){$('catalog').replaceChildren();for(const a of MerchCatalog){const f=document.createElement('figure'),c=document.createElement('canvas'),caption=document.createElement('figcaption');c.width=a.width;c.height=32;c.getContext('2d').imageSmoothingEnabled=false;MarketStock.draw(c.getContext('2d'),{type:a.id,x:0,y:0},m,images,32,mix);caption.textContent=a.name;f.append(c,caption);$('catalog').append(f);}}
