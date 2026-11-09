from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];s=r/'engine/campaign-crawl/crawl-ref/source';b=r/'analysis/native/ayame-zanshin02';b.mkdir(exist_ok=False)
shutil.copytree(r/'analysis/native/ayame-zanshin01/before',b/'before')
p=s/'holo-batch-internal.h';t=p.read_text(encoding='utf-8');t=t.replace('int ayame_zanshin_end=0;','bool ayame_zanshin_unlocked=false;\n    int ayame_zanshin_end=0;');p.write_text(t,encoding='utf-8')
p=s/'holo-batch.cc';t=p.read_text(encoding='utf-8');t=t.replace('    ctx.eligible=eligible(target);','    ctx.eligible=eligible(target);\n    ctx.ayame_zanshin_unlocked=is(god_id::ayame) && you.piety>=50;')
t=t.replace('if(is(god_id::ayame) && you.piety>=50 && aut>0 && ctx.kind==attack_kind::melee','if(is(god_id::ayame) && ctx.ayame_zanshin_unlocked && you.piety>=50 && aut>0 && ctx.kind==attack_kind::melee');p.write_text(t,encoding='utf-8')
p=s/'holo-campaign-test.cc';t=p.read_text(encoding='utf-8');old='''void ayame_test_melee(monster *m,bool spend=true) {
    you.turn_is_over=false;you.time_taken=10;''';new='''void ayame_test_melee(monster *m,bool spend=true) {
    // Native outer command processing starts an ordinary action as turn-spending.
    you.turn_is_over=true;you.time_taken=10;''';assert old in t;t=t.replace(old,new);p.write_text(t,encoding='utf-8')
(r/'analysis/native/ayame-zanshin01/followup.txt').write_text('Native melee fixture initialized turn_is_over=false, so command_scope correctly cancelled post-attack mark handling.02 mirrors native outer command turn-spending initialization. Also snapshot tier2 eligibility before kill piety gain so a49-piety kill does not retroactively earn the passive.01 not deployed.',encoding='utf-8')
print('Native command fixture and pre-kill tier2 eligibility snapshot corrected.')
