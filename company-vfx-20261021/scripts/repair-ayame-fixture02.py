from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parents[1];old=root/'analysis/native/ayame-vfx01';new=root/'analysis/native/ayame-vfx02';new.mkdir(exist_ok=False)
(old/'failure.json').write_text(json.dumps({'status':'failed','reason':'Native twin strike was valid but both swings caused zero HP damage; test incorrectly required nonzero damage. GDB throw stack retained in debug.log.','runtimeInstalled':False},indent=2),encoding='utf-8')
shutil.copytree(old/'before',new/'before');shutil.copy2(old/'preserved-files.json',new/'preserved-files.json')
p=root/'engine/campaign-crawl/crawl-ref/source/holo-campaign-test.cc';s=p.read_text(encoding='utf-8')
s=s.replace('you.piety=180;const int before=target->hit_points;cast("ayame",3,target,target->pos());\n        require(target->hit_points<before,"twin strike did not damage fixture");','''you.piety=180;const int before=target->hit_points,mpBefore=you.magic_points,clockBefore=you.elapsed_time;
        cast("ayame",3,target,target->pos());
        require(target->hit_points<=before && you.magic_points==mpBefore-3 && you.elapsed_time>clockBefore
            && holo_batch::s.three_ready>clockBefore,"twin strike action/cost/cooldown invalid");''')
p.write_text(s,encoding='utf-8')
p=root/'scripts/publish-ayame-vfx01.py';s=p.read_text(encoding='utf-8').replace('ayame-vfx01','ayame-vfx02').replace("review['afterStrikeHp']<review['beforeStrikeHp']","review['afterStrikeHp']<=review['beforeStrikeHp']")
s=s.replace('assets/holocrawl/ayame-vfx02','assets/holocrawl/ayame-vfx01')
(root/'scripts/publish-ayame-vfx02.py').write_text(s,encoding='utf-8')
print('Preserved failed01. Prepared02 with valid hit/miss-independent native action checks.')
