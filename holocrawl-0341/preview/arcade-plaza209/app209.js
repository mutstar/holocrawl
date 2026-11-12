(async()=>{'use strict';const $=id=>document.getElementById(id),images={},maps={},canvases={},dirs=ArcadeLayout209.dirs;
const load=async(id,url)=>{const im=new Image();im.src=url;await im.decode();images[id]=im;};
await Promise.all([WallHeight121.load(),load('floor','../native-play107/assets/floor.png'),load('planter','../holohome133/assets/planter-native.png'),...['kong','rack','crane','onigiri','phoenix','fighting'].map(k=>load(k,'../arcade-plaza191/assets/'+k+'-native.png'))]);
images.photo=ArcadeArtAdditions209.photoBooth();
while(!window.material171Ready){if(window.material171Error)throw Error(window.material171Error);await new Promise(r=>setTimeout(r,30));}
const src=await fetch('../native-play107/maps/map-10786001-1.json').then(r=>r.json()),counts=new Map();for(const i of src.floors)counts.set(i,(counts.get(i)||0)+1);const ids=[...counts].sort((a,b)=>b[1]-a[1]).map(a=>a[0]).filter(i=>src.palette[i].atlas==='floor').slice(0,4),floors=[];
for(const id of ids)for(let r=0;r<4;r++){const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),f=src.palette[id];g.translate(16,16);g.rotate(r*Math.PI/2);g.drawImage(images.floor,f.sx,f.sy,32,32,-16,-16,32,32);floors.push(c);}
const opened={main:false,left:false,right:false};
const theme={material:'metal',face:[90,88,88],top:[40,46,49],accent:[138,154,160]};
function mask(m,x,y){let n=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&!m.cells[yy*m.w+xx])n|=1<<i;});return n;}
function fixtures(q,m){const o=m.origin,f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
// Native editable benches and the shallow stock shelf are aligned to the yard edge.
for(const p of m.furniture){const x=p.x*32,y=p.y*32;if(p.id==='bench'){f('#282f31',x+3,y+25,58,5);f('#394c4b',x+5,y+15,4,12);f('#394c4b',x+55,y+15,4,12);f('#84785f',x+2,y+9,60,5);f('#b1a183',x+2,y+8,60,2);f('#7b6b54',x+2,y+17,60,5);f('#ab9573',x+2,y+17,60,2);}else if(p.id==='planter'){q.drawImage(images.planter,x,y);}else{f('#273333',x+2,y+8,60,22);f('#5a7167',x+3,y+8,58,19);f('#b1aa8a',x+2,y+6,60,4);for(let k=0;k<3;k++){f('#3b4b46',x+7+k*18,y+13,14,11);f(['#a49371','#9386ad','#a1b1a0'][k],x+9+k*18,y+15,10,5);}}}

}
function draw(mode){const m=maps[mode],c=canvases[mode],q=c.getContext('2d');q.imageSmoothingEnabled=false;for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){const i=y*m.w+x;q.drawImage(floors[RandomFloor.index('ARCADE-PLAZA191',0,x,y)%floors.length],x*32,y*32);if(ArcadeFloor209.contains(m,x,y))ArcadeFloor209.draw(q,m,x,y);if(!m.cells[i]){if(m.building[i]){q.drawImage(ArcadeWall192.tile(mask(m,x,y),x,y),x*32,y*32);}else WallHeight121.wall(q,m.cells,m.w,m.h,x,y,32);}}
ArcadeWall192.fascia(q,m);fixtures(q,m);for(const p of [...m.props].sort((a,b)=>(a.y+a.h)-(b.y+b.h))){const im=images[p.id],w=p.drawW||im.width,h=p.drawH||im.height,x=p.x*32+(p.w*32-w)/2,y=(p.y+p.h)*32-h;q.fillStyle='rgba(0,0,0,.23)';q.fillRect(x+3,(p.y+p.h)*32-4,w-6,4);q.drawImage(im,x,y,w,h);}

ArcadeDoor194.draw(q,m,opened);
ArcadeArtAdditions209.circuitDoor(q,m.circuit);
if($('grid').checked){q.strokeStyle='rgba(196,211,205,.25)';for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)q.strokeRect(x*32+.5,y*32+.5,31,31);}
if($('labels').checked){q.font='11px system-ui';q.textAlign='center';for(const p of [...m.props,m.circuit]){const cx=(p.x+p.w/2)*32;q.fillStyle='#182028';q.fillRect(cx-61,p.y*32-16,122,15);q.fillStyle='#e0e7e6';q.fillText(p.label,cx,p.y*32-5);}}
}
function drawAll(){for(const mode of ['attached','standalone'])draw(mode);const names={main:'정면',left:'왼쪽',right:'오른쪽'};for(const[id,label]of Object.entries(names))$('door-'+id).textContent=label+' 문 '+(opened[id]?'닫기':'열기');$('status').textContent='21×19칸 · 메가프리 · 메가서킷 전용 문';}
for (const mode of ['attached','standalone']) {
  const map = maps[mode] = ArcadeLayout209.generate(mode);
  const canvas = canvases[mode] = $(mode);
  canvas.width = map.w * 32;
  canvas.height = map.h * 32;

  const gate = document.querySelector('[data-gate=' + mode + ']');
  gate.style.left = map.circuit.x / map.w * 100 + '%';
  gate.style.top = map.circuit.y / map.h * 100 + '%';
  gate.style.width = map.circuit.w / map.w * 100 + '%';
  gate.style.height = map.circuit.h / map.h * 100 + '%';

  document.querySelector('[data-mode=' + mode + ']').onclick = () => {
    const zoom = $('zoom');
    zoom.width = canvas.width * 2;
    zoom.height = canvas.height * 2;
    const context = zoom.getContext('2d');
    context.imageSmoothingEnabled = false;
    context.drawImage(canvas,0,0,zoom.width,zoom.height);
    $('title').textContent = '게임센터 광장 · ' + (mode==='attached'?'벽붙임':'독립 배치');
    $('detail').showModal();
  };
}
$('grid').onchange=$('labels').onchange=drawAll;for(const id of ['main','left','right'])$('door-'+id).onclick=()=>{opened[id]=!opened[id];drawAll();};$('close').onclick=()=>$('detail').close();drawAll();window.ArcadeArt209={maps,canvases,images,drawAll,getState:()=>({opened:{...opened}}),setDoor:(value,id)=>{for(const k of id?[id]:['main','left','right'])opened[k]=!!value;drawAll();},collisionMap:mode=>ArcadeDoor194.collision(maps[mode],opened)};window.arcade209Ready=true;
})().catch(e=>{console.error(e);document.getElementById('status').textContent='불러오기 실패: '+e.message;});
