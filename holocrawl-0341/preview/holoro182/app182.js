(async()=>{'use strict';const $=id=>document.getElementById(id),images={},maps={},canvases={},dirs=HoloroLayout182.dirs;let opened=true;
const load=async(id,url)=>{const im=new Image();im.src=url;await im.decode();images[id]=im;};
await Promise.all([WallHeight121.load(),load('floor','../native-play107/assets/floor.png'),...['entrance','penlights','ollie','anya','reine'].map(k=>load(k,'assets/'+k+'-native.png'))]);
while(!window.material171Ready){if(window.material171Error)throw Error(window.material171Error);await new Promise(r=>setTimeout(r,30));}
const src=await fetch('../native-play107/maps/map-10786001-1.json').then(r=>r.json()),counts=new Map();for(const i of src.floors)counts.set(i,(counts.get(i)||0)+1);const ids=[...counts].sort((a,b)=>b[1]-a[1]).map(a=>a[0]).filter(i=>src.palette[i].atlas==='floor').slice(0,4),floors=[];
for(const id of ids)for(let r=0;r<4;r++){const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),f=src.palette[id];g.translate(16,16);g.rotate(r*Math.PI/2);g.drawImage(images.floor,f.sx,f.sy,32,32,-16,-16,32,32);floors.push(c);}
const theme={material:'plaster',face:[96,83,105],top:[39,39,48],accent:[174,163,147],wood:true};
function mask(m,x,y){let n=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&!m.cells[yy*m.w+xx])n|=1<<i;});return n;}
const doorMask=(()=>{const c=document.createElement('canvas');c.width=96;c.height=48;const g=c.getContext('2d');g.drawImage(images.entrance,0,0);const d=g.getImageData(0,0,96,48).data,a=new Uint8Array(96*48),todo=[[48,45]];while(todo.length){const[x,y]=todo.pop();if(x<24||x>72||y<14||y>45)continue;const i=y*96+x;if(a[i]||d[i*4+3])continue;a[i]=1;for(const[dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]])todo.push([x+dx,y+dy]);}return a;})();
function entranceSprite(open){const c=document.createElement('canvas');c.width=96;c.height=48;const g=c.getContext('2d');for(let y=14;y<46;y++){const xs=[];for(let x=24;x<=72;x++)if(doorMask[y*96+x])xs.push(x);if(!xs.length)continue;const lo=xs[0],hi=xs.at(-1);for(const x of xs){const edge=Math.min(x-lo,hi-x);if(open&&edge>2)continue;g.fillStyle=edge<2?'#bab4b5':x===47||x===48?'#302e41':y===27||y===41?'#b0a3b0':'#595169';g.fillRect(x,y,1,1);if(!open&&y>25&&y<40&&x%8<2){g.fillStyle='#242b33';g.fillRect(x,y,1,1);}}}g.drawImage(images.entrance,0,0);return c;}
function fixtures(q,m){const o=m.origin,f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
for(const p of m.furniture){const x=p.x*32,y=p.y*32,w=p.w*32,h=p.h*32;
 if(p.id==='stock'){f('#37303d',x+2,y+6,w-4,24);f('#80735f',x+3,y+7,w-6,20);for(let k=0;k<3;k++){f('#4d4850',x+7+k*18,y+12,13,12);f(['#aa6877','#b3a37c','#7a9fb5'][k],x+9+k*18,y+13,9,5);}continue;}
 const accent=p.id==='ollie-counter'?'#a94b60':p.id==='anya-counter'?'#a89569':p.id==='reine-counter'?'#416e98':'#8d7b9e';
 const top=p.h===1?2:22;f('#282730',x+2,y+top+2,w-4,h-top-2);f('#62545f',x+3,y+top+3,w-6,h-top-6);f('#c2b49a',x+1,y+top,w-2,5);f('#eee0c4',x+2,y+top,w-4,2);f(accent,x+5,y+top+(p.h===1?10:9),w-10,p.h===1?5:h-top-14);f('#302c36',x+4,y+h-4,w-8,3);
 for(let k=1;k<p.w;k++)f('#453d48',x+k*32,y+top+16,2,Math.max(1,h-top-20));
 if(p.id==='ollie-counter'){
  const cx=x+w/2;f('#70313e',cx-11,y+35,22,20);for(let i=0;i<4;i++){f('#eee0c7',cx-8+i*4,y+37+i*4,4,3);f('#eee0c7',cx+4-i*4,y+37+i*4,4,3);}
 }else if(p.id==='anya-counter'){
  const cx=x+w/2;for(const[dy,dx]of [[0,-2],[4,1],[8,-2],[12,0]]){f('#3b3541',cx+dx-2,y+34+dy,8,5);f('#f0dfb3',cx+dx,y+34+dy,4,4);}f('#5b3e31',cx-8,y+51,16,3);f('#d1b464',cx-2,y+54,4,3);
 }else if(p.id==='reine-counter'){
  const cx=x+w/2;for(const[dx,dy]of [[-12,4],[0,0],[12,4]]){f('#84bdc5',cx+dx-4,y+35+dy,8,14);f('#84bdc5',cx+dx-2,y+33+dy,4,2);f('#d8c486',cx+dx-2,y+38+dy,4,6);f('#204e73',cx+dx-1,y+40+dy,2,3);}
 }
}

}
function draw(mode){const m=maps[mode],c=canvases[mode],q=c.getContext('2d');q.imageSmoothingEnabled=false;for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){const i=y*m.w+x;q.drawImage(floors[RandomFloor.index('HOLORO181',0,x,y)%floors.length],x*32,y*32);if(m.inner[i]){q.fillStyle='rgba(115,89,110,.13)';q.fillRect(x*32,y*32,32,32);}if(!m.cells[i]){if(m.building[i])q.drawImage(FacilityMaterial171.tile(mask(m,x,y),x,y,theme),x*32,y*32);else WallHeight121.wall(q,m.cells,m.w,m.h,x,y,32);}}
fixtures(q,m);for(const p of [...m.props].sort((a,b)=>(a.y+a.h)-(b.y+b.h))){const im=images[p.id],w=p.drawW||im.width,h=p.drawH||im.height,x=p.x*32+(p.w*32-w)/2,y=p.fixture?p.y*32+p.anchorBottom-h:(p.y+p.h)*32-h;q.fillStyle='rgba(0,0,0,.23)';q.fillRect(x+3,y+h-3,w-6,3);q.drawImage(im,x,y,w,h);}

q.drawImage(entranceSprite(opened),(m.entry.x-1)*32,m.entry.y*32-14);
// Same thickness as the standard wall coping, joining both jambs.
q.fillStyle='#818e90';q.fillRect(m.entry.x*32-1,m.entry.y*32+30,34,2);
if($('grid').checked){q.strokeStyle='rgba(196,211,205,.25)';for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)q.strokeRect(x*32+.5,y*32+.5,31,31);}
if($('labels').checked){q.font='11px system-ui';q.textAlign='center';for(const p of m.props){const cx=(p.x+p.w/2)*32;q.fillStyle='#182028';q.fillRect(cx-61,p.y*32-16,122,15);q.fillStyle='#e0e7e6';q.fillText(p.label,cx,p.y*32-5);}}
}
function drawAll(){for(const mode of ['attached','standalone'])draw(mode);$('status').textContent='입구 '+(opened?'열림':'닫힘')+' · 응원봉 진열대와 세 멤버 잡화 코너';}
for(const mode of ['attached','standalone']){const m=maps[mode]=HoloroLayout182.generate(mode),c=canvases[mode]=$(mode);c.width=m.w*32;c.height=m.h*32;document.querySelector('[data-mode='+mode+']').onclick=()=>{const z=$('zoom');z.width=c.width*2;z.height=c.height*2;z.getContext('2d').imageSmoothingEnabled=false;z.getContext('2d').drawImage(c,0,0,z.width,z.height);$('title').textContent='토코호로로 · '+(mode==='attached'?'벽붙임':'독립 배치')+' · 2배 확대';$('detail').showModal();};}
$('door').onclick=()=>{opened=!opened;drawAll();};$('grid').onchange=$('labels').onchange=drawAll;$('close').onclick=()=>$('detail').close();drawAll();window.HoloroArt182={maps,canvases,images,drawAll,doorMask,entranceSprite,getState:()=>({opened})};window.holoro182Ready=true;
})().catch(e=>{console.error(e);document.getElementById('status').textContent='불러오기 실패: '+e.message;});
