from pathlib import Path
import json,hashlib,shutil
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/lamy-caster01';run.mkdir();(run/'before').mkdir()
changed=['Makefile.obj','spl-cast.cc','monster.cc','player.cc','status.cc','holo-batch.cc','holo-batch-resources.cc','holo-campaign.cc','holo-campaign-test.cc']
for n in changed:shutil.copy2(src/n,run/'before'/n)
shutil.copy2(r/'runtime/tiles01/HoloCrawl.exe',run/'before/HoloCrawl.exe')
preserved={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if p.name not in changed};(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
(run/'changed-files.json').write_text(json.dumps(changed+['holo-lamy.h','holo-lamy.cc']),encoding='utf-8')
print('Lamy caster baseline preserved.')
