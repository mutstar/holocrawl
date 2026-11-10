from pathlib import Path
P=Path(__file__).resolve().parents[1]/'preview'
s=(P/'facility-placement171/placements171.js').read_text(encoding='utf-8').replace('FacilityPlacement171','FacilityShapes172').replace('placement171Ready','shapes172Ready').replace('W=19,H=17','W=23,H=21')
s=s.replace("if(f.kind==='legacy'&&edge&&'.+'.includes(c))", "if(f.kind==='legacy'&&!f.shaped&&edge&&'.+'.includes(c))").replace("(edge||f.kind!=='legacy')", "(edge||f.kind!=='legacy'||f.shaped)").replace("fence=c==='G'&&edge", "fence=c==='G'&&(edge||f.fenceField)")
s=s.replace("if(f.kind!=='legacy')doors.push(f.entry);", "if(f.kind!=='legacy'||f.shaped)for(let i=0;i<(f.doorWidth||1);i++)doors.push({x:f.entry.x+i,y:f.entry.y});")
marker='function path(m,start,target)'
at=s.index(marker)
s=s[:at]+r'''
const grass=await load('assets/grass-native.png');
const grassColors=new Set(['74,87,63','75,88,63','71,84,60','73,86,61','83,90,66','85,91,66','81,88,64','83,89,64']);
for(const f of data.cards){if(!f.shaped)continue;const a=assets.get(f.id),[sx,sy]=f.sourceOffset;
 const sample=cv(32,32);sample.getContext('2d').drawImage(a.sourceClosed,sx+f.floorSample[0]*32,sy+f.floorSample[1]*32,32,32,0,0,32,32);a.floorTile=sample;
 for(const state of ['sourceClosed','sourceOpen']){const original=a[state],clean=cv(original.width,original.height),q=clean.getContext('2d');q.drawImage(original,0,0);
  if(f.fenceField){const d=q.getImageData(0,0,clean.width,clean.height);for(let y=0;y<f.oldH*32;y++)for(let x=0;x<f.oldW*32;x++){const i=((sy+y)*clean.width+sx+x)*4;if(grassColors.has(d.data[i]+','+d.data[i+1]+','+d.data[i+2]))d.data[i+3]=0;}q.putImageData(d,0,0);}
  else if(f.kind==='home')q.clearRect(sx+(f.oldEntry.x-1)*32,sy+f.oldEntry.y*32-16,96,16);
  else if(f.rows&&f.oldEntry&&f.id!=='fantasy'){const old=FacilityShapes172Dummy;}
  a[state+'Clean']=clean;
 }
 if(f.kind==='legacy'&&!f.fenceField){const original=a.sourceClosed,oldY=f.oldEntry.y*32,gateTop=f.sourceOpenMap[(f.oldEntry.y)*f.oldW+f.oldEntry.x]===1?14:0;
  // Transfer only the actual entrance span, leaving neighboring member props intact.
  a.gateTop=f.doorWidth===2||f.id==='holox'||f.id==='gamers'?14:0;
  for(const state of ['sourceClosed','sourceOpen']){const gate=cv((f.doorWidth||1)*32,32+a.gateTop);gate.getContext('2d').drawImage(a[state],sx+f.oldEntry.x*32,sy+oldY-a.gateTop,gate.width,gate.height,0,0,gate.width,gate.height);a[state+'Gate']=gate;if(a.gateTop)a[state+'Clean'].getContext('2d').clearRect(sx+f.oldEntry.x*32,sy+oldY-a.gateTop,gate.width,a.gateTop);}
 }
}
function terrain(q,f,o,a){for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(f.inside[y*f.w+x]){if(f.fenceField)q.drawImage(grass,((o.x+x)%2)*32,((o.y+y)%2)*32,32,32,(o.x+x)*32,(o.y+y)*32,32,32);else q.drawImage(a.floorTile,(o.x+x)*32,(o.y+y)*32);}}
function fence(q,f,o){const inside=(x,y)=>x>=0&&y>=0&&x<f.w&&y<f.h&&f.inside[y*f.w+x];q.lineWidth=1;for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(inside(x,y))for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]])if(!inside(x+dx,y+dy)){if(x+dx===f.entry.x&&y+dy===f.entry.y)continue;const px=(o.x+x)*32+(dx===1?32:0),py=(o.y+y)*32+(dy===1?32:0);q.fillStyle='#303d35';if(dy){q.fillRect(px,py-3,32,5);q.fillStyle='#7c8d77';q.fillRect(px,py-3,32,1);q.fillRect(px,py,32,1);for(const k of [0,16,30]){q.fillStyle='#445640';q.fillRect(px+k,py-8,2,9);q.fillStyle='#9aa38c';q.fillRect(px+k,py-8,2,1);}}else{q.fillRect(px-1,py,3,32);q.fillStyle='#7c8d77';q.fillRect(px-1,py,1,32);for(const k of [0,16,30]){q.fillStyle='#455740';q.fillRect(px-3,py+k,5,3);q.fillStyle='#96a38c';q.fillRect(px-3,py+k,1,2);}}}}
function decals(q,f,m,a){if(!a.decal)return;const raw=cv(a.decal.width,a.decal.height),g=raw.getContext('2d');g.drawImage(a.decal,0,0);const d=g.getImageData(0,0,raw.width,raw.height).data,[bx,by]=f.contentShift,candidates=[];for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(m.kind[(m.o.y+y)*W+m.o.x+x]===2)candidates.push({x,y});
 for(let y=0;y<f.oldH;y++)for(let x=0;x<f.oldW;x++){let opaque=false;for(let yy=0;yy<32&&!opaque;yy++)for(let xx=0;xx<32;xx++)if(d[((y*32+yy)*raw.width+x*32+xx)*4+3]){opaque=true;break;}if(!opaque)continue;let tx=x+bx,ty=y+by;if(y>=f.oldH-2){tx=f.entry.x+(x-f.oldEntry.x);ty=f.entry.y;}let c={x:tx,y:ty};if(!candidates.some(p=>p.x===tx&&p.y===ty))c=candidates.reduce((a,b)=>(a.x-tx)**2+(a.y-ty)**2<(b.x-tx)**2+(b.y-ty)**2?a:b);q.drawImage(a.decal,x*32,y*32,32,32,(m.o.x+c.x)*32,(m.o.y+c.y)*32,32,32);}}
''' +s[at:]
s=s.replace("  else if(f.rows&&f.oldEntry&&f.id!=='fantasy'){const old=FacilityShapes172Dummy;}\n",'')
a=s.index(" if(f.kind==='home')HomeMaterial159.paint" )
b=s.index(" if($('grid').checked)",a)
s=s[:a]+r'''
 if(f.shaped){terrain(q,f,o,a);if(f.kind==='home'){q.save();q.beginPath();for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(m.kind[y*W+x]===2)q.rect(x*32,y*32,32,32);q.clip();HomeMaterial159.paint(q,{home:o});q.restore();}
  const [sx,sy]=f.sourceOffset,[bx,by]=f.contentShift,clean=a[(open?'sourceOpen':'sourceClosed')+'Clean'];
  for(let y=0;y<f.oldH;y++)for(let x=0;x<f.oldW;x++)if(f.sourceInside[y*f.oldW+x])q.drawImage(clean,sx+x*32,sy+y*32,32,32,(o.x+x+bx)*32,(o.y+y+by)*32,32,32);
  if(f.fenceField){const py=(o.y+f.oldEntry.y+f.contentShift[1]-1)*32+16,end=m.entry.y*32+32;q.fillStyle='#7b806d';q.fillRect(m.entry.x*32,py,32,end-py);q.fillStyle='#646e5c';for(let yy=py;yy<end;yy+=16)q.fillRect(m.entry.x*32,yy,32,1);fence(q,f,o);}else if(f.kind==='home'){q.drawImage(HomeMaterial159.door(open),m.entry.x*32,m.entry.y*32);q.drawImage(homeGate,(m.entry.x-1)*32,m.entry.y*32-16);}else{decals(q,f,m,a);const gate=a[(open?'sourceOpen':'sourceClosed')+'Gate'];q.drawImage(gate,m.entry.x*32,m.entry.y*32-a.gateTop);}
 }else{
 const [sx,sy]=f.sourceOffset;for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(f.inside[y*f.w+x])q.drawImage(im,sx+x*32,sy+y*32,32,32,(o.x+x)*32,(o.y+y)*32,32,32);
 if(a.frieze)q.drawImage(a.frieze,(o.x+4)*32,o.y*32);q.drawImage(a[open?'gateOpen':'gateClosed'],(m.entry.x-1)*32,m.entry.y*32-14);
 }
''' +s[b:]
s=s.replace("kind[i]=fence?3:2;","kind[i]=fence?(mode==='attached'&&y===0?1:3):2;")
s=s.replace("f.w+'×'+f.h+'칸 · 같은 내부와 규모'", "f.w+'×'+f.h+'칸 · '+f.shapeName")
s=s.replace("'야외 운동장: 펜스와 내부 트랙 유지'", "'운동장: 잔디와 펜스를 같은 윤곽에 맞춤 · 트랙·4멤버 소품 유지'")
s=s.replace("assets,floors};", "assets,floors,grass};")
(P/'facility-shapes172/placements172.js').write_text(s,encoding='utf-8')
print('Patched172 rendering and turf clipping')
