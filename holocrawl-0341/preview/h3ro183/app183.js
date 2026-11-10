(async()=>{'use strict';const $=id=>document.getElementById(id),images={},maps={},canvases={},dirs=H3roLayout183.dirs;let opened=true;
const load=async(id,url)=>{const im=new Image();im.src=url;await im.decode();images[id]=im;};
await Promise.all([WallHeight121.load(),load('floor','../native-play107/assets/floor.png'),...['entrance','vehicle','zeta','kaela','kobo','maps'].map(k=>load(k,'assets/'+k+'-native.png'))]);
while(!window.material171Ready){if(window.material171Error)throw Error(window.material171Error);await new Promise(r=>setTimeout(r,30));}
const src=await fetch('../native-play107/maps/map-10786001-1.json').then(r=>r.json()),counts=new Map();for(const i of src.floors)counts.set(i,(counts.get(i)||0)+1);const ids=[...counts].sort((a,b)=>b[1]-a[1]).map(a=>a[0]).filter(i=>src.palette[i].atlas==='floor').slice(0,4),floors=[];
for(const id of ids)for(let r=0;r<4;r++){const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),f=src.palette[id];g.translate(16,16);g.rotate(r*Math.PI/2);g.drawImage(images.floor,f.sx,f.sy,32,32,-16,-16,32,32);floors.push(c);}
const theme={material:'metal',face:[79,92,97],top:[34,43,47],accent:[158,132,82]};
function mask(m,x,y){let n=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&!m.cells[yy*m.w+xx])n|=1<<i;});return n;}
const doorMask=(()=>{const c=document.createElement('canvas');c.width=128;c.height=64;const g=c.getContext('2d');g.drawImage(images.entrance,0,0);const d=g.getImageData(0,0,128,64).data,a=new Uint8Array(128*64),todo=[[64,61]];while(todo.length){const[x,y]=todo.pop();if(x<16||x>111||y<18||y>61)continue;const i=y*128+x;if(a[i]||d[i*4+3])continue;a[i]=1;for(const[dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]])todo.push([x+dx,y+dy]);}return a;})();
function entranceSprite(open){const c=document.createElement('canvas');c.width=128;c.height=64;const g=c.getContext('2d');for(let y=18;y<62;y++){const xs=[];for(let x=16;x<=111;x++)if(doorMask[y*128+x])xs.push(x);if(!xs.length)continue;const lo=xs[0],hi=xs.at(-1);for(const x of xs){const edge=Math.min(x-lo,hi-x);if(open&&edge>2)continue;g.fillStyle=edge<2?'#98afb0':y%6<2?'#829398':'#3e5660';g.fillRect(x,y,1,1);}}g.drawImage(images.entrance,0,0);return c;}
function fixtures(q,m){const o=m.origin,f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
for(const p of m.furniture){const x=p.x*32,y=p.y*32,w=p.w*32;
 if(p.id==='tires'){for(let k=0;k<2;k++){f('#20292c',x+4,y+8+k*9,24,12);f('#52606a',x+7,y+8+k*9,18,3);f('#101a20',x+10,y+11+k*9,12,4);f('#303e47',x+5,y+17+k*9,22,2);}continue;}
 f('#23313a',x+2,y+6,w-4,25);f('#577078',x+3,y+8,w-6,20);f('#a9b5b1',x+1,y+5,w-2,4);
 if(p.id==='tools'){for(let k=0;k<3;k++){f('#344752',x+7+k*18,y+12,13,12);f('#b69c65',x+10+k*18,y+12,6,2);f('#b4bcb6',x+10+k*18,y+17,7,2);}}
 else for(let k=0;k<3;k++){f(['#b9c5c4','#d0ad52','#639fca'][k],x+8+k*18,y+11,11,14);f('#d7d4b8',x+7+k*18,y+10,13,2);f('#334a59',x+11+k*18,y+18,5,3);}
}
// Four short, passable wheel-bay corner marks, not a road through the building.
for(const[x,y,sx,sy]of [[2,1,1,1],[7,1,-1,1],[2,6,1,-1],[7,6,-1,-1]]){const px=(o.x+x)*32,py=(o.y+y)*32;f('#9e956e',px+(sx<0?-12:0),py,12,2);f('#9e956e',px,py+(sy<0?-12:0),2,12);}
}
function draw(mode){const m=maps[mode],c=canvases[mode],q=c.getContext('2d');q.imageSmoothingEnabled=false;for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){const i=y*m.w+x;q.drawImage(floors[RandomFloor.index('H3RO183',0,x,y)%floors.length],x*32,y*32);if(m.inner[i]){q.fillStyle='rgba(72,98,107,.12)';q.fillRect(x*32,y*32,32,32);}if(!m.cells[i]){if(m.building[i])q.drawImage(FacilityMaterial171.tile(mask(m,x,y),x,y,theme),x*32,y*32);else WallHeight121.wall(q,m.cells,m.w,m.h,x,y,32);}}
fixtures(q,m);for(const p of [...m.props].sort((a,b)=>(a.y+a.h)-(b.y+b.h))){const im=images[p.id],w=p.drawW||im.width,h=p.drawH||im.height,x=p.x*32+(p.w*32-w)/2,y=p.fixture?p.y*32+p.anchorBottom-h:(p.y+p.h)*32-h;q.fillStyle='rgba(0,0,0,.23)';q.fillRect(x+3,y+h-3,w-6,3);q.drawImage(im,x,y,w,h);}

q.drawImage(entranceSprite(opened),m.entry.x*32+16-64,m.entry.y*32-30);
// Same thickness as the standard wall coping, joining both jambs.
q.fillStyle='#818e90';q.fillRect((m.entry.x-1)*32-1,m.entry.y*32+30,98,2);
if($('grid').checked){q.strokeStyle='rgba(196,211,205,.25)';for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)q.strokeRect(x*32+.5,y*32+.5,31,31);}
if($('labels').checked){q.font='11px system-ui';q.textAlign='center';for(const p of m.props){const cx=(p.x+p.w/2)*32;q.fillStyle='#182028';q.fillRect(cx-61,p.y*32-16,122,15);q.fillStyle='#e0e7e6';q.fillText(p.label,cx,p.y*32-5);}}
}
function drawAll(){for(const mode of ['attached','standalone'])draw(mode);$('status').textContent='입구 '+(opened?'열림':'닫힘')+' · 보급 차량과 세 멤버 작업 공간';}
for(const mode of ['attached','standalone']){const m=maps[mode]=H3roLayout183.generate(mode),c=canvases[mode]=$(mode);c.width=m.w*32;c.height=m.h*32;document.querySelector('[data-mode='+mode+']').onclick=()=>{const z=$('zoom');z.width=c.width*2;z.height=c.height*2;z.getContext('2d').imageSmoothingEnabled=false;z.getContext('2d').drawImage(c,0,0,z.width,z.height);$('title').textContent='h3ro 비클 · '+(mode==='attached'?'벽붙임':'독립 배치')+' · 2배 확대';$('detail').showModal();};}
$('door').onclick=()=>{opened=!opened;drawAll();};$('grid').onchange=$('labels').onchange=drawAll;$('close').onclick=()=>$('detail').close();drawAll();window.H3roArt183={maps,canvases,images,drawAll,doorMask,entranceSprite,getState:()=>({opened})};window.h3ro183Ready=true;
})().catch(e=>{console.error(e);document.getElementById('status').textContent='불러오기 실패: '+e.message;});
