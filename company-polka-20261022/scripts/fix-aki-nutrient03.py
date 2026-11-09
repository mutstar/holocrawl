from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];b=r/'analysis/native/aki-nutrient03';b.mkdir(exist_ok=False)
shutil.copytree(r/'analysis/native/aki-nutrient01/before',b/'before')
p=r/'engine/campaign-crawl/crawl-ref/source/holo-campaign-test.cc';t=p.read_text(encoding='utf-8')
changes={
    'step(30);aki_test_hit(monster_by_mid(you.props["aki_second"].get_int()));require(you.magic_points==12,"restored cooldown expiry");':'step(30);const int prior=you.magic_points;aki_test_hit(monster_by_mid(you.props["aki_second"].get_int()));require(you.magic_points==prior+2,"restored cooldown expiry");',
    'step(30);aki_test_hit(second);require(you.magic_points==12,"cooldown failed to end");':'step(30);const int prior=you.magic_points;aki_test_hit(second);require(you.magic_points==prior+2,"cooldown failed to end");'
}
for old,new in changes.items():assert old in t;t=t.replace(old,new)
p.write_text(t,encoding='utf-8')
(r/'analysis/native/aki-nutrient01/followup.txt').write_text('Direct,DoT,rose,bloom source cases and5/5/7 passed. Cooldown test expected absoluteMP12 without native naturalMP regeneration during30aut.03 compares with MP immediately before kill.01 not deployed.',encoding='utf-8')
(r/'analysis/native/aki-nutrient02/followup.txt').write_text('Shell quoting prevented harness edit. Unchanged duplicate build from01; not tested or deployed. Correct guarded script fix-aki-nutrient03.py used for03.',encoding='utf-8')
print('Cooldown test now accounts for ordinary MP regeneration.')
