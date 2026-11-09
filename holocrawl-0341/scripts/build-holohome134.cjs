const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/holohome133'),D=path.join(R,'preview/holohome134');
fs.mkdirSync(D,{recursive:true});
fs.writeFileSync(path.join(D,'generator134.js'),`(function(root){'use strict';const native=typeof module!=='undefined'&&module.exports,Base=native?require('../holohome132/generator132.js'):root.HoloHomeGen132;
function cellsFor(m,p){const a=[];for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)a.push(y*m.w+x);return a;}
function generate(seed,floor=1){const m=Base.generate(seed,floor);m.generation='browser HoloHome134 restrained lounge; native integration pending';if(!m.home)return m;const old={...m.home};m.reservedHomeBounds=old;
for(let y=old.y;y<old.y+old.h;y++)for(let x=old.x;x<old.x+old.w;x++)m.cells[y*m.w+x]=1;
const h=m.home={...old,x:old.x+2,y:old.y+1,w:13,h:11};
for(let y=0;y<h.h;y++)for(let x=0;x<h.w;x++)m.cells[(h.y+y)*m.w+h.x+x]=x===0||y===0||x===h.w-1||y===h.h-1?0:1;
m.entrance={x:h.x+6,y:h.y+10};m.cells[m.entrance.y*m.w+m.entrance.x]=1;m.doors=m.doors.filter(d=>!d.home);m.doors.push({id:'home-6-10',...m.entrance,home:true,entrance:true});
const prop=(type,x,y,w,hh,extra={})=>({type,x:h.x+x,y:h.y+y,w,h:hh,...extra});
m.props=[prop('sofa',3,4,3,1),prop('coffee',4,6,2,1),prop('tv',9,3,2,2,{source:[0,0,60,96]}),prop('planter',1,8,2,1)];
m.homeStair.x=h.x+6;m.homeStair.y=h.y+2;m.homeFocus={x:h.x+7,y:h.y+7};
m.open=Uint8Array.from(m.cells,c=>c===1?1:0);const used=new Set();for(const p of m.props)for(const i of cellsFor(m,p)){if(used.has(i))throw Error('HoloHome furniture overlaps');used.add(i);m.open[i]=0;}
const d=Base.distances(m,m.start);m.walkable=m.open.reduce((a,b)=>a+b,0);if(d.filter(x=>x>=0).length!==m.walkable)throw Error('HoloHome disconnected');if(!m.open[m.homeStair.y*m.w+m.homeStair.x])throw Error('Stair blocked');m.homeDistance=d[m.homeStair.y*m.w+m.homeStair.x];m.validation={...m.validation,restrainedLounge:true,connected:true};return m;}
const api={generate,cellsFor,distances:Base.distances,isHome:Base.isHome};root.HoloHomeGen134=api;if(native)module.exports=api;
})(globalThis);`);
fs.writeFileSync(path.join(D,'materials134.js'),`(function(root){'use strict';let settings;const cache=new Map(),make=()=>{const c=document.createElement('canvas');c.width=c.height=32;return c;};
function configure(s){settings=s;cache.clear();}
function floors(){return settings.floorTiles.map(base=>{const c=make(),q=c.getContext('2d');q.drawImage(base,0,0);q.fillStyle='rgba(158,146,119,.25)';q.fillRect(0,0,32,32);return c;});}
function wall(mask){if(cache.has(mask))return cache.get(mask);const c=make(),q=c.getContext('2d'),{wall:atlas,rects}=settings;q.drawImage(atlas,...rects[mask+':0'],0,0,32,32);q.globalCompositeOperation='source-atop';q.fillStyle='rgba(188,176,145,.18)';q.fillRect(0,0,32,32);q.globalCompositeOperation='source-over';cache.set(mask,c);return c;}
function paint(q,m){if(!m.home)return;const h=m.home,x=h.x*32,y=h.y*32;
q.fillStyle='#536961';q.fillRect(x+2*32+6,y+4*32+3,5*32-12,4*32-6);q.strokeStyle='#8a846a';q.lineWidth=1;q.strokeRect(x+2*32+8.5,y+4*32+5.5,5*32-17,4*32-11);
// Just two small, worn mint windows; no full-height columns or ornate facade.
for(const wx of [3,9]){const xx=x+wx*32;q.fillStyle='#282f2d';q.fillRect(xx+5,y+12,22,17);q.fillStyle='#628a7f';q.fillRect(xx+7,y+13,18,14);q.fillStyle='#455e58';q.fillRect(xx+15,y+13,2,14);q.fillRect(xx+7,y+19,18,2);q.fillStyle='#938a72';q.fillRect(xx+4,y+28,24,2);}
}
function door(open){const key='door:'+open;if(cache.has(key))return cache.get(key);const c=make(),q=c.getContext('2d');q.fillStyle='#292b29';q.fillRect(3,2,26,30);q.fillStyle='#9b927b';q.fillRect(4,3,24,29);q.fillStyle='#45413a';q.fillRect(7,6,18,26);
if(open){q.clearRect(8,7,16,25);q.fillStyle='#74604a';q.fillRect(7,7,3,25);q.fillRect(23,7,2,25);}else{q.fillStyle='#77614b';q.fillRect(8,7,16,24);q.fillStyle='#39372f';q.fillRect(15,7,2,24);q.fillStyle='#bca77a';q.fillRect(13,20,1,3);q.fillRect(18,20,1,3);}q.fillStyle='#455b57';q.fillRect(7,2,18,4);q.fillStyle='#b2b6a0';q.fillRect(11,3,2,2);q.fillRect(15,3,2,2);q.fillRect(19,3,2,2);cache.set(key,c);return c;}
root.HomeMaterial134={configure,floors,wall,paint,door};})(globalThis);`);
let app=fs.readFileSync(path.join(S,'app133.js'),'utf8').replaceAll('133','134');
app=app.replace("['stairs','entrance','balcony','sofa','coffee','tv','bookcase','kotatsu','notice','planter']","['stairs','sofa','coffee','tv','planter']").replace("load('assets/'+k+'-native.png')","load('../holohome133/assets/'+k+'-native.png')");
app=app.replace('wall:im.wall,rects,planes','wall:im.wall,rects,planes,floorTiles');
app=app.replace('{x:m.home.x-1,y:m.home.y-1}','{x:m.home.x-3,y:m.home.y-2}');
app=app.replace("if(m.home)things.push({type:'entrance',x:m.home.x+7,y:m.home.y+11.5,bottom:(m.home.y+13)*32});",'');
app=app.replace('g.drawImage(im[p.type],p.x*32,p.bottom-im[p.type].height);',"if(p.source){const [sx,sy,w,h]=p.source;g.drawImage(im[p.type],sx,sy,w,h,p.x*32,p.bottom-h,w,h);}else g.drawImage(im[p.type],p.x*32,p.bottom-im[p.type].height);");
app=app.replaceAll('홀로홈17×13칸','홀로홈13×11칸');
fs.writeFileSync(path.join(D,'app134.js'),app);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('133','134').replace('홀로도리 참고 · 홀로홈 로비와 외벽 수정','홀로홈 · 기존 던전에 맞춘 소박한 라운지').replace('17×13칸','13×11칸').replace('사진의 대리석 로비·파란 소파·좌식 공간·TV 코너·뒤쪽 양갈래 계단을 도트로 옮겼습니다.','큰 계단·창·기둥은 덜어내고 파란 소파, 작은 테이블, TV와 화분만 남겼습니다.');
const c0=html.indexOf('<div class="cards">'),c1=html.indexOf('<footer>',c0);
html=html.slice(0,c0)+'<div class="cards"><section class="card"><h2>기존 맵과 같은 크기의 도트</h2><p>기존 콘크리트 벽·바닥 질감에 옅은 실내 색만 더했습니다. 소품은 원래 픽셀 크기로 표시하고, 입구도 한 칸짜리 문으로 정리했습니다.</p></section><section class="card"><h2>홀로홈 느낌만 남기기</h2><p>파란 소파 하나 · 작은 테이블 하나 · TV 하나 · 화분 하나. 로비는13×11칸, 계단은 뒤쪽 중앙에 있습니다.</p><p>1층 확정 출현과 전용 계단·2층 왕복은 유지합니다.</p></section></div><p><a href="../holohome133/">장식이 많았던 이전133 보기</a> · <a href="../holohome133/prompts.json">재사용한 도트 제작 기록</a></p>'+html.slice(c1);
html=html.replace('<a href="prompts.json">도트 제작 프롬프트·참고 출처</a>','<a href="../holohome133/prompts.json">도트 제작 프롬프트·참고 출처</a>');
fs.writeFileSync(path.join(D,'index.html'),html);
let check=fs.readFileSync(path.join(R,'scripts/check-holohome133.cjs'),'utf8').replaceAll('133','134');
check=check.replaceAll('[17,13]','[13,11]').replace("['stairs','entrance','balcony','sofa','coffee','tv','bookcase','kotatsu','notice','planter']","['stairs','sofa','coffee','tv','planter']").replace('assert.equal(assets.length,10)','assert.equal(assets.length,5)').replace('h=m.home;let changedOutside','h=m.reservedHomeBounds;let changedOutside').replace('referenceLobby:true','restrainedLounge:true');
fs.writeFileSync(path.join(R,'scripts/check-holohome134.cjs'),check);
console.log('Built restrained HoloHome134, preserving133.');
