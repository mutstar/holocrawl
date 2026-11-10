(async()=>{'use strict';const $=id=>document.getElementById(id),images={},maps={},canvases={},dirs=FountainLayout189.dirs;
const load=async(id,url)=>{const im=new Image();im.src=url;await im.decode();images[id]=im;};
await Promise.all([WallHeight121.load(),load('floor','../native-play107/assets/floor.png'),load('planter','../holohome133/assets/planter-native.png'),...['candy','penlights','balloon','fountain','zeta','kaela','kobo','ollie','anya','reine','risu','moona','iofi'].map(k=>load(k,'assets/'+k+'-native.png'))]);
while(!window.material171Ready){if(window.material171Error)throw Error(window.material171Error);await new Promise(r=>setTimeout(r,30));}
const src=await fetch('../native-play107/maps/map-10786001-1.json').then(r=>r.json()),counts=new Map();for(const i of src.floors)counts.set(i,(counts.get(i)||0)+1);const ids=[...counts].sort((a,b)=>b[1]-a[1]).map(a=>a[0]).filter(i=>src.palette[i].atlas==='floor').slice(0,4),floors=[];
for(const id of ids)for(let r=0;r<4;r++){const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),f=src.palette[id];g.translate(16,16);g.rotate(r*Math.PI/2);g.drawImage(images.floor,f.sx,f.sy,32,32,-16,-16,32,32);floors.push(c);}
const theme={material:'rock',face:[106,103,91],top:[53,58,53],accent:[156,151,128]};
function mask(m,x,y){let n=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&!m.cells[yy*m.w+xx])n|=1<<i;});return n;}
function fixtures(q,m){const o=m.origin,f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
// Native editable benches and the shallow stock shelf are aligned to the yard edge.
for(const p of m.furniture){const x=p.x*32,y=p.y*32;if(p.id==='bench'){f('#282f31',x+3,y+25,58,5);f('#394c4b',x+5,y+15,4,12);f('#394c4b',x+55,y+15,4,12);f('#84785f',x+2,y+9,60,5);f('#b1a183',x+2,y+8,60,2);f('#7b6b54',x+2,y+17,60,5);f('#ab9573',x+2,y+17,60,2);}else if(p.id==='planter'){q.drawImage(images.planter,x,y);}else{f('#273333',x+2,y+8,60,22);f('#5a7167',x+3,y+8,58,19);f('#b1aa8a',x+2,y+6,60,4);for(let k=0;k<3;k++){f('#3b4b46',x+7+k*18,y+13,14,11);f(['#a49371','#9386ad','#a1b1a0'][k],x+9+k*18,y+15,10,5);}}}

}
function draw(mode){const m=maps[mode],c=canvases[mode],q=c.getContext('2d');q.imageSmoothingEnabled=false;for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){const i=y*m.w+x;q.drawImage(floors[RandomFloor.index('FOUNTAIN-PLAZA185',0,x,y)%floors.length],x*32,y*32);if(m.inner[i]){q.fillStyle='rgba(137,124,102,.13)';q.fillRect(x*32,y*32,32,32);}if(!m.cells[i]){if(m.building[i]){q.drawImage(FacilityMaterial171.tile(mask(m,x,y),x,y,theme),x*32,y*32);}else WallHeight121.wall(q,m.cells,m.w,m.h,x,y,32);}}
fixtures(q,m);for(const p of [...m.props].sort((a,b)=>(a.y+a.h)-(b.y+b.h))){const im=images[p.id],w=p.drawW||im.width,h=p.drawH||im.height,x=p.x*32+(p.w*32-w)/2,y=(p.y+p.h)*32-h;q.fillStyle='rgba(0,0,0,.23)';q.fillRect(x+3,(p.y+p.h)*32-4,w-6,4);q.drawImage(im,x,y,w,h);}

if($('grid').checked){q.strokeStyle='rgba(196,211,205,.25)';for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)q.strokeRect(x*32+.5,y*32+.5,31,31);}
if($('labels').checked){q.font='11px system-ui';q.textAlign='center';for(const p of m.props){const cx=(p.x+p.w/2)*32;q.fillStyle='#182028';q.fillRect(cx-61,p.y*32-16,122,15);q.fillStyle='#e0e7e6';q.fillText(p.label,cx,p.y*32-5);}}
}
function drawAll(){for(const mode of ['attached','standalone'])draw(mode);$('status').textContent='15×15칸 광장 · 판매시설3개 · 기수별 소품9개';}
for(const mode of ['attached','standalone']){const m=maps[mode]=FountainLayout189.generate(mode),c=canvases[mode]=$(mode);c.width=m.w*32;c.height=m.h*32;document.querySelector('[data-mode='+mode+']').onclick=()=>{const z=$('zoom');z.width=c.width*2;z.height=c.height*2;z.getContext('2d').imageSmoothingEnabled=false;z.getContext('2d').drawImage(c,0,0,z.width,z.height);$('title').textContent='분수와 세 판매차 · '+(mode==='attached'?'벽붙임':'독립 배치')+' · 2배 확대';$('detail').showModal();};}
$('grid').onchange=$('labels').onchange=drawAll;$('close').onclick=()=>$('detail').close();drawAll();window.FountainArt189={maps,canvases,images,drawAll};window.fountain189Ready=true;
})().catch(e=>{console.error(e);document.getElementById('status').textContent='불러오기 실패: '+e.message;});
