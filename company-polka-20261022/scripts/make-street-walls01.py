from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1]; src=r/'analysis/previews/street-cement01'; dst=r/'analysis/previews/street-walls01'
dst.mkdir(exist_ok=True)
for n in ['index.html','style.css','app.js','generator.js','generator-validation.json']:shutil.copy2(src/n,dst/n)
shutil.copytree(src/'assets',dst/'assets',dirs_exist_ok=True)
p=dst/'app.js';s=p.read_text(encoding='utf-8')
s=s.replace("ctx.fillStyle='rgba(11,13,15,.72)'","ctx.fillStyle='rgba(11,13,15,.48)'")
s=s.replace('texture(facePatch,px,py+t*.28,t,t*.72);',"ctx.filter='brightness(1.35)';texture(facePatch,px,py+t*.08,t,t*.92);ctx.filter='none';")
decor='''
// Existing venue artwork supplies wall-mounted units; positions depend only on map seed.
if(stage>=3){for(let y=1;y<map.h-1;y++)for(let x=2;x<map.w-2;x++){
 if(cells[y*map.w+x]!==G.WALL||!open(x,y+1)||cells[y*map.w+x-1]!==G.WALL||cells[y*map.w+x+1]!==G.WALL)continue;
 const p=map.prefab;if(x>=p.x-1&&x<=p.x+p.w&&y>=p.y-1&&y<=p.y+p.h)continue;
 if(x%3!==1||hash(x,y)%100>=68)continue;
 const px=x*t,py=y*t,kind=hash(x+431,y)%4;
 ctx.filter='brightness(1.35)';
 if(kind===0)texture([289,34,37,19],px-t*.07,py+t*.13,t*1.15,t*.59);
 if(kind===1)texture([273,69,11,42],px+t*.31,py-t*.22,t*.31,t*1.18);
 if(kind===2)texture([294,86,22,16],px+t*.14,py+t*.27,t*.72,t*.52);
 if(kind===3)texture([183,31,32,12],px,py+t*.17,t,t*.38);
 ctx.filter='none';
}}
'''
s=s.replace('if(stage>=3){const p=map.prefab;',decor+'if(stage>=3){const p=map.prefab;')
p.write_text(s,encoding='utf-8')
p=dst/'index.html';s=p.read_text(encoding='utf-8').replace('잔향도시 · 시멘트 거리','잔향도시 · 골목의 벽장식').replace('승인한 80×70칸 구조 그대로 · 조금 밝아진 회색 시멘트 바닥 시안','80×70칸 구조와 시멘트 바닥 유지 · 조금 밝은 벽에 실외기·배관·환기구 추가')
p.write_text(s,encoding='utf-8')
test=(r/'scripts/check-street-cement01.cjs').read_text(encoding='utf-8-sig').replace('street-cement01','street-walls01').replace('8789/','8790/')
(r/'scripts/check-street-walls01.cjs').write_text(test,encoding='utf-8')
print('Created wall decoration preview.')
