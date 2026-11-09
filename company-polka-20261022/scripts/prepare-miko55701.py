"""Apply approved Miko 5/5/7 footprint, preserving approved raster effects."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
src=root/'engine/campaign-crawl/crawl-ref/source'
checkpoint=root/'analysis/native/miko55701'
checkpoint.mkdir(exist_ok=False)
names=['holo-batch-martial.cc','holo-batch-space.cc','holo-batch.cc','holo-campaign.cc','holo-visual.cc','holo-campaign-test.cc']
for name in names:
    p=src/name
    original=p.read_text(encoding='utf-8')
    before=checkpoint/'before'/name
    before.parent.mkdir(exist_ok=True)
    before.write_text(original,encoding='utf-8')
    text=original
    if name=='holo-visual.cc':
        text=text.replace('holo_batch::five()?3:you.piety>=75?2:1','holo_batch::five()?3:2')
    elif name!='holo-campaign-test.cc':
        # These occurrences in these selected files belong to Miko only.
        text=text.replace('five()?3:you.piety>=75?2:1','five()?3:2')
    if name=='holo-campaign.cc':
        anchor='    if(g=="suisei")lines.push_back('
        at=text.index(anchor)
        text=text[:at]+'    if(g=="miko")lines.push_back("1* active: MP3/1turn, fixed5x5 sanctuary from unlock; duration20+0.5*Inv turns. Heal1+Inv/12 HP every2turns. 3* active: MP3/piety3/1turn, flames on5x5 boundary; passive: outside ranged damage reduced10+Inv/3 percent. 5* active: MP6/piety10/1turn, expands to7x7 for6+0.2*Inv turns, reduces damage15+Inv/3 percent and cleanses one condition.");\n'+text[at:]
    if name=='holo-campaign-test.cc':
        text=text.replace('require(has(you.pos()+coord_def(1,0),holo_visual::effect::shrine),"low faith shrine missing");','require(has(you.pos()+coord_def(2,2),holo_visual::effect::shrine),"low faith 5x5 corner missing");')
        text=text.replace('require(!has(you.pos()+coord_def(2,0),holo_visual::effect::shrine),"low faith shrine too wide");','require(!has(you.pos()+coord_def(3,0),holo_visual::effect::shrine),"low faith shrine exceeds5x5");\n        require(holo_batch::s.one_end-you.elapsed_time==200+5*holo_batch::s.inv,"shrine duration changed");')
        text=text.replace('\\"lowFaithWidth\\":3','\\"lowFaithWidth\\":5')
        assert 'lowFaithWidth\\":5' in text
    assert text!=original,name
    p.write_text(text,encoding='utf-8')
(checkpoint/'scope.json').write_text(json.dumps({'revision':'miko55701','widths':[5,5,7],'art':'Existing approved Miko raster effects reused on native terrain; no composited effects.','scope':'Footprint and effect coverage only. New tier2 healing/shield passive remains proposal.'},indent=2),encoding='utf-8')
print('Applied Miko5/5/7 to gameplay, faith bonus, status and native rendering.')
