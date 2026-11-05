from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-complete04'
out.mkdir(exist_ok=True)
for name in ['index.html','app.js','boot.js','terrain.js','manifest.json','art-manifest.json']:
 shutil.copyfile(root/'preview/city-complete03'/name,out/name)
shutil.copytree(root/'preview/city-complete03/assets',out/'assets',dirs_exist_ok=True)
previous=(root/'preview/city-complete03/grounding.js').read_text(encoding='utf-8')
details=previous[previous.index('function drawDetails'):]
previous=previous[:previous.index('function drawDetails')].replace('function groundFixtures','function previousGroundFixtures').replace('function fixtureFeet','function previousFixtureFeet').replace('function groundStair','function previousGroundStair')
new='''
const footCache=new Map();
function propMask(p){const key=p.type+':'+mix;if(footCache.has(key))return footCache.get(key);const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;MarketStock.draw(cc,{type:p.type,x:0,y:0},m,images,32,mix);const data=cc.getImageData(0,0,32,32).data;let bottom=0;for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(data[(y*32+x)*4+3]>128)bottom=Math.max(bottom,y);let left=32,right=0;for(let y=Math.max(0,bottom-5);y<=bottom;y++)for(let x=0;x<32;x++)if(data[(y*32+x)*4+3]>128){left=Math.min(left,x);right=Math.max(right,x);}const mask=document.createElement('canvas');mask.width=mask.height=32;const mc=mask.getContext('2d');mc.drawImage(c,0,0);mc.globalCompositeOperation='source-in';mc.fillStyle='#090e0b';mc.fillRect(0,0,32,32);const result={c,mask,bottom,left,right};footCache.set(key,result);return result;}
function groundFixtures(){for(const p of fixtures){const meta=MerchCatalog.find(a=>a.id===p.type);if(meta.kind==='wall')continue;const{x,y}=p,px=x*32,py=y*32,b=propMask(p),rubbish=['paper-rubbish','trash-bags','poster-rolls'].includes(p.type),height=rubbish?3:7;
 // A short cast shadow meets the exact foot level; no detached ellipse or floor rectangle.
 ctx.save();ctx.globalAlpha=rubbish?.35:.58;ctx.drawImage(b.mask,px+3,py+b.bottom-height+3,32,height);ctx.restore();
 ctx.fillStyle='rgba(7,12,8,.76)';ctx.fillRect(px+b.left,py+b.bottom,Math.max(1,b.right-b.left+1),2);
 ctx.fillStyle='rgba(12,18,13,.38)';ctx.fillRect(px+b.left+2,py+b.bottom+2,Math.max(1,b.right-b.left),1);
}}
function fixtureFeet(p){const meta=MerchCatalog.find(a=>a.id===p.type);if(meta.kind==='wall')return;const b=propMask(p);ctx.fillStyle='rgba(9,13,10,.68)';ctx.fillRect(p.x*32+b.left,p.y*32+b.bottom+1,b.right-b.left+1,1);}
const stairMasks={};
function groundStair(c,up,px,py,t){const s=t/32,im=up?images.groundUp:images.groundDown;c.save();c.imageSmoothingEnabled=false;if(up){if(!stairMasks.up){const mask=document.createElement('canvas');mask.width=mask.height=32;const cc=mask.getContext('2d');cc.drawImage(im,0,0);cc.globalCompositeOperation='source-in';cc.fillStyle='#080e0a';cc.fillRect(0,0,32,32);stairMasks.up=mask;}c.globalAlpha=.63;c.drawImage(stairMasks.up,px+4*s,py+23*s,t,10*s);c.globalAlpha=1;c.globalAlpha=.8;c.drawImage(stairMasks.up,0,24,32,8,px,py+25*s,t,8*s);c.globalAlpha=1;}c.drawImage(im,px,py,t,t);if(!up){c.strokeStyle='rgba(5,9,7,.80)';c.lineWidth=2*s;c.beginPath();c.arc(px+16*s,py+16*s,12*s,Math.PI*1.03,Math.PI*1.88);c.stroke();c.fillStyle='rgba(126,124,110,.22)';c.fillRect(px+9*s,py+29*s,8*s,s);}c.restore();}
'''
details=details.replace("(j?'수정 후':'수정 전')","(j?'그림자 보강':'이전03')")
(out/'grounding.js').write_text(previous+new+details,encoding='utf-8')
p=out/'terrain.js';s=p.read_text(encoding='utf-8').replace('else c.drawImage(isUp(f)?images.up:images.down,px,py,t,t);','else previousGroundStair(c,isUp(f),px,py,t);');p.write_text(s,encoding='utf-8')
p=out/'app.js';s=p.read_text(encoding='utf-8').replace('if(grounded)groundFixtures();','if(grounded)groundFixtures();else previousGroundFixtures();').replace('if(grounded)fixtureFeet(p);','if(grounded)fixtureFeet(p);else previousFixtureFeet(p);');p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('바닥에 붙는 굿즈와 계단','굿즈·계단 접촉 그림자 보강').replace('같은 도트 배치에서 매대 받침의 접촉 그림자와 바닥 마모를 보강하고, 계단을 시멘트 바닥에 연결했습니다. 수정 전후 버튼으로 비교하세요.','받침 밑의 진한 접촉 그림자와 오른쪽 아래로 짧은 그림자를 넣었습니다. 네모 바닥 패치는 제거하고, 같은 맵에서 이전03과 비교합니다.').replace('왼쪽은 이전 모습, 오른쪽은 바닥 접점 수정입니다.','왼쪽은 이전03, 오른쪽은 그림자를 보강한 모습입니다.');p.write_text(s,encoding='utf-8')
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'));manifest.update({'previous':'city-complete03','stairAndPropPNGsUnchangedFrom03':True,'purpose':'stronger contact and directional cast shadows, remove rectangular floor aprons'});(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'scripts/check-city-complete03.cjs';s=p.read_text(encoding='utf-8').replace('city-complete03','city-complete04');(root/'scripts/check-city-complete04.cjs').write_text(s,encoding='utf-8')
print(out)
