from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parents[1];out=root/'analysis/native/wrath02';out.mkdir(parents=True,exist_ok=True)
src=root/'engine/campaign-crawl/crawl-ref/source';sdl=root/'engine/tiles-crawl/crawl-ref/source'
art=root/'assets/holocrawl/combat-art01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
manifest=json.loads((art/'manifest.json').read_text(encoding='utf-8'))
assert len(manifest['assets'])==74
for a in manifest['assets']:
    p=root/a['path'];im=Image.open(p)
    assert im.mode=='RGBA' and im.size==(32,32) and im.getchannel('A').getextrema()[0]==0 and sha(p)==a['sha256'],a['id']
    assert p.read_bytes()==(sdl/p.relative_to(src)).read_bytes(),a['id']
previous=json.loads((root/'analysis/native/altars05/checkpoint.json').read_text(encoding='utf-8'))
retained=[n for n in previous['sourceSha256'] if n.startswith(('rltiles/holo/altar_','rltiles/holo/god_'))]
assert len(retained)==44
for n in retained:assert sha(src/n)==previous['sourceSha256'][n],n
creatures='rose fox raven swordsman hound'.split()
for g in creatures:assert sha(src/'rltiles/holo'/(g+'.png'))!=sha(src/'rltiles/holo'/(g+'_1.png')),g
effects='warning urgent shrine garden water gravity orbit fire exhibit spotlight frost rhythm shield slime impact comet'.split()
different=[];coverage={}
for g in effects:
    if sha(src/'rltiles/holo'/('fx_'+g+'_0.png'))!=sha(src/'rltiles/holo'/('fx_'+g+'_1.png')):different.append(g)
    if g in ['impact','comet']:continue
    for frame in range(2):
        im=Image.open(src/'rltiles/holo'/('fx_'+g+'_'+str(frame)+'.png'))
        alpha=list(im.getchannel('A').crop((10,10,22,22)).getdata())
        coverage[g+'_'+str(frame)]=round(sum(v>=96 for v in alpha)/len(alpha),3)
        assert coverage[g+'_'+str(frame)]<0.2,(g,frame,coverage[g+'_'+str(frame)])
gui=root/'analysis/native/tiles01/wrath02-sdl01'
frames=sorted(gui.glob('*.png'));assert len(frames)==14
meta={}
for p in frames:
    im=Image.open(p);assert im.width>=1000 and im.height>=700
    m=json.loads(Path(str(p)+'.json').read_text(encoding='utf-8'));meta[p.stem]=m
    assert m['gearPreserved'] and m['styledHuman'],p.name
assert meta['garden-roses']['creatures'][0]==2
assert meta['fox-spirits']['creatures'][1]>=1
assert meta['ravens']['creatures'][2]==6
assert meta['wrath-swordsman']['creatures'][3]>=1
assert meta['wrath-hound']['creatures'][4]>=1
assert sha(gui/'ravens.png')!=sha(gui/'ravens-frame-alt.png')
assert 0 in meta['commander-badges']['badges'] and 1 in meta['commander-badges']['badges']
assert meta['water-field']['effectCells']>0 and meta['ghostfire']['effectCells']>0
assert 2 in meta['bombs-warning']['badges'] and 3 in meta['bombs-urgent']['badges']
proof=dict(status='passed',nativeTiles=74,retainedAltarsAndEmblems=44,creaturesWithDistinctFrames=5,distinctEffectFramePairs=len(different),transparentEffectCenterCoverage=coverage,nativeScreenshots=14,allNativeGearPreserved=True,allNativeHumanBasesApplied=True,nativeCreatureKinds=5,nativeBadgeWarningUrgency=True,metadata=meta)
(out/'render-validation.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items() if k not in ['metadata','transparentEffectCenterCoverage']}))
