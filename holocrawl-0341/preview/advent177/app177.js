(async()=>{'use strict';const $=id=>document.getElementById(id),images={},maps={},canvases={},dirs=AdventLayout177.dirs;let opened=true;
const load=async(id,url)=>{const im=new Image();im.src=url;await im.decode();images[id]=im;};
await Promise.all([WallHeight121.load(),load('floor','../native-play107/assets/floor.png'),...['entrance','shiori','bijou','nerissa','fuwawa','mococo','cot','locker'].map(k=>load(k,'../advent176/assets/'+k+'-native.png'))]);
while(!window.material171Ready){if(window.material171Error)throw Error(window.material171Error);await new Promise(r=>setTimeout(r,30));}
const src=await fetch('../native-play107/maps/map-10786001-1.json').then(r=>r.json()),counts=new Map();for(const i of src.floors)counts.set(i,(counts.get(i)||0)+1);const ids=[...counts].sort((a,b)=>b[1]-a[1]).map(a=>a[0]).filter(i=>src.palette[i].atlas==='floor').slice(0,4),floors=[];
for(const id of ids)for(let r=0;r<4;r++){const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),f=src.palette[id];g.translate(16,16);g.rotate(r*Math.PI/2);g.drawImage(images.floor,f.sx,f.sy,32,32,-16,-16,32,32);floors.push(c);}
const theme={material:'brick',face:[71,75,85],top:[32,40,46],accent:[98,78,85]};
function mask(m,x,y){let n=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&!m.cells[yy*m.w+xx])n|=1<<i;});return n;}
const doorMask=(()=>{const c=document.createElement('canvas');c.width=96;c.height=48;const g=c.getContext('2d');g.drawImage(images.entrance,0,0);const d=g.getImageData(0,0,96,48).data,a=new Uint8Array(96*48),todo=[[48,45]];while(todo.length){const[x,y]=todo.pop();if(x<24||x>72||y<14||y>45)continue;const i=y*96+x;if(a[i]||d[i*4+3])continue;a[i]=1;for(const[dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]])todo.push([x+dx,y+dy]);}return a;})();
function entranceSprite(open){const c=document.createElement('canvas');c.width=96;c.height=48;const g=c.getContext('2d');for(let y=14;y<46;y++){const xs=[];for(let x=24;x<=72;x++)if(doorMask[y*96+x])xs.push(x);if(!xs.length)continue;const lo=xs[0],hi=xs.at(-1);for(const x of xs){const edge=Math.min(x-lo,hi-x);if(open&&edge>2)continue;g.fillStyle=edge<2?'#9c9ca7':x===47||x===48?'#242b33':y===27||y===41?'#7c8190':'#454c5d';g.fillRect(x,y,1,1);if(!open&&y>25&&y<40&&x%8<2){g.fillStyle='#242b33';g.fillRect(x,y,1,1);}}}g.drawImage(images.entrance,0,0);return c;}
function bar(q,x,y,gate){x*=32;y*=32;const f=(c,a,b,w,h)=>{q.fillStyle=c;q.fillRect(x+a,y+b,w,h);};f('#171f29',0,7,32,3);f('#777f8c',0,7,32,2);f('#252e3b',0,29,32,3);if(gate){f('#7c8191',0,9,3,21);f('#7c8191',29,9,3,21);}else for(let a=3;a<32;a+=7){f('#121a23',a+2,9,2,20);f('#89909c',a,9,2,20);}}
function fixtures(q,m){const o=m.origin;const f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
// Short cable runs and room plates belong to the furniture, not loose floor icons.
for(const [x,y,color]of [[3,6,'#ab9ab7'],[7,6,'#b397d7'],[11,6,'#6386be'],[3,8,'#8ebada'],[11,8,'#d59aba']]){const px=(o.x+x)*32,py=(o.y+y)*32;f('#242c36',px+9,py+6,14,4);f(color,px+11,py+6,10,2);}
const x=m.counter.x*32,y=m.counter.y*32;f('#252d38',x+2,y+6,28,56);f('#777989',x+2,y+4,26,8);f('#484556',x+4,y+13,24,45);f('#bbb3c4',x+8,y+7,12,4);f('#834b58',x+10,y+28,8,5);f('#1b242e',x+3,y+60,26,3);
// Sparse floor grate in the lobby; passable and visually distinct from bars.
const gx=(o.x+8)*32,gy=(o.y+12)*32;f('#30363a',gx+8,gy+10,16,10);for(let i=0;i<4;i++)f('#717579',gx+9+i*4,gy+11,1,8);
// Mounted chains stay on the wall face, clear of the coping.
for(const [cx,cy]of [[3,2],[7,0],[11,2]]){const x=(o.x+cx)*32,y=(o.y+cy)*32;f('#272b34',11+x,12+y,12,4);f('#8c8d96',12+x,12+y,10,2);for(let i=0;i<3;i++){const dx=i%2?1:0;f('#252933',15+x+dx,15+y+i*4,5,6);f('#8d909a',15+x+dx,15+y+i*4,4,1);f('#676f7d',15+x+dx,16+y+i*4,1,3);}f('#a4a0a7',12+x,27+y,7,2);f('#626a79',12+x,29+y,2,2);f('#626a79',17+x,29+y,2,2);}
for(const [cx,cy,color]of [[1,2,'#aca0b3'],[13,2,'#6981a1']]){const x=(o.x+cx)*32,y=(o.y+cy)*32;f('#282c34',x+3,y+26,26,4);f('#7c8088',x+3,y+24,26,2);f(color,x+6,y+16,6,8);f('#8c7d79',x+14,y+18,4,6);f('#565f70',x+21,y+19,5,5);}
}
function draw(mode){const m=maps[mode],c=canvases[mode],q=c.getContext('2d');q.imageSmoothingEnabled=false;for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){const i=y*m.w+x;q.drawImage(floors[RandomFloor.index('ADVENT175',0,x,y)%floors.length],x*32,y*32);if(m.inner[i]){q.fillStyle='rgba(39,44,62,.18)';q.fillRect(x*32,y*32,32,32);}if(!m.cells[i]){if(m.building[i])q.drawImage(FacilityMaterial171.tile(mask(m,x,y),x,y,theme),x*32,y*32);else WallHeight121.wall(q,m.cells,m.w,m.h,x,y,32);}}
fixtures(q,m);for(const p of [...m.furniture,...m.props].sort((a,b)=>(a.y+a.h)-(b.y+b.h))){const im=images[p.id],w=p.drawW||im.width,h=p.drawH||im.height,x=p.x*32+(p.w*32-w)/2,y=(p.y+p.h)*32-h;q.fillStyle='rgba(0,0,0,.23)';q.fillRect(x+3,(p.y+p.h)*32-4,w-6,4);q.drawImage(im,x,y,w,h);}
for(const p of m.bars)bar(q,p.x,p.y,false);for(const p of m.gates)bar(q,p.x,p.y,true);
q.drawImage(entranceSprite(opened),(m.entry.x-1)*32,m.entry.y*32-14);
// Same thickness as the standard wall coping, joining both jambs.
q.fillStyle='#818e90';q.fillRect(m.entry.x*32-1,m.entry.y*32+30,34,2);
if($('grid').checked){q.strokeStyle='rgba(196,211,205,.25)';for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)q.strokeRect(x*32+.5,y*32+.5,31,31);}
if($('labels').checked){q.font='11px system-ui';q.textAlign='center';for(const p of m.props){const cx=(p.x+p.w/2)*32;q.fillStyle='#182028';q.fillRect(cx-61,p.y*32-16,122,15);q.fillStyle='#e0e7e6';q.fillText(p.label,cx,p.y*32-5);}}
}
function drawAll(){for(const mode of ['attached','standalone'])draw(mode);$('status').textContent='입구 '+(opened?'열림':'닫힘')+' · 5개 방 · 중앙 통로 연결';}
for(const mode of ['attached','standalone']){const m=maps[mode]=AdventLayout177.generate(mode),c=canvases[mode]=$(mode);c.width=m.w*32;c.height=m.h*32;document.querySelector('[data-mode='+mode+']').onclick=()=>{const z=$('zoom');z.width=c.width*2;z.height=c.height*2;z.getContext('2d').imageSmoothingEnabled=false;z.getContext('2d').drawImage(c,0,0,z.width,z.height);$('title').textContent='The Cell 리턴즈 · '+(mode==='attached'?'벽붙임':'독립 배치')+' · 2배 확대';$('detail').showModal();};}
$('door').onclick=()=>{opened=!opened;drawAll();};$('grid').onchange=$('labels').onchange=drawAll;$('close').onclick=()=>$('detail').close();drawAll();window.AdventArt177={maps,canvases,images,drawAll,doorMask,entranceSprite,getState:()=>({opened})};window.advent177Ready=true;
})().catch(e=>{console.error(e);document.getElementById('status').textContent='불러오기 실패: '+e.message;});
