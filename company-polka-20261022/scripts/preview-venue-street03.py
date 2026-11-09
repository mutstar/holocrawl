from pathlib import Path
from PIL import Image
import json,sys,shutil
r=Path(__file__).resolve().parents[1];rev='venue-street03';a=r/'assets/holocrawl'/rev;out=r/'analysis/previews'/rev
assert not a.exists() and not out.exists()
a.mkdir(parents=True);out.mkdir(parents=True)
shutil.copy2(sys.argv[1],a/'scene-original.png')
im=Image.open(sys.argv[1]).convert('RGB').resize((512,384),Image.Resampling.NEAREST)
im.save(out/'scene-scale-reference.png')
im.resize((1024,768),Image.Resampling.NEAREST).save(out/'scene.png')
data=dict(status='whole-scene-art-direction-draft',date='2026-11-03',review=f'analysis/previews/{rev}/index.html',region='잔향도시1~3층 공연장 앞 거리',feedback=['01:flat modern tiles felt disconnected and unlike DCSS','02:literal original DCSS stone felt too much like DCSS'],direction='Modern urban venue materials with textured,muted low-resolution roguelike rendering. Cohesive full-scene draft before separate tile production.',newRasterTool='built-in image_gen',tileAssetsProduced=False,engineIntegrated=False,runtimeChanged=False)
for p in [a/'manifest.json',out/'manifest.json']:p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>잔향도시 · 현대 거리와 던전 도트의 중간 방향</title><style>body{background:#12151a;color:#edf1f5;font:17px "Malgun Gothic",sans-serif;max-width:1200px;margin:28px auto;padding:0 20px;line-height:1.8}h1,h2{color:#c6dce8}section{background:#20262d;padding:18px;margin:20px 0}img{max-width:100%;image-rendering:pixelated}a{color:#b9ddff}</style><h1>잔향도시 · 공연장 앞 거리 · 방향 시안03</h1><p>현대 공연장 거리의 소재와 돌죽 같은 도트 밀도·명도를 함께 맞추는 시안입니다. 타일을 따로 제작하기 전에 화면 전체의 질감과 색조부터 확인합니다.</p><section><h2>새 전체 화면 시안</h2><img src="scene.png"><p>이미지 생성 도구로 만든 장면 컨셉입니다. 실제32×32 타일 세트로 분리하거나 엔진에 적용한 결과가 아닙니다. 생성 이미지 속 배치·캐릭터는 분위기와 크기 참고용입니다.</p></section><section><h2>피드백 이력</h2><p>01: 매끈한 블록 벽·밝은 보도·별개 소품 때문에 짜깁기처럼 느껴짐.<br>02: 원본 돌죽 석조 배경을 너무 그대로 사용.<br>03: 현대 소재를 유지하고 거친 픽셀 질감·연결된 벽·절제된 명도로 통일.</p><a href="../venue-street01/index.html">01 확인</a> · <a href="../venue-street02/index.html">02 확인</a></section></html>'''
(out/'index.html').write_text(page,encoding='utf-8')
for name in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:(r/name).write_text('@echo off\r\nstart "" "%~dp0analysis\\previews\\venue-street03\\index.html"\r\n',encoding='ascii')
for name in ['VFX_DRAFT_STATUS.json','HOME_HANDOFF_STATE.json']:
    p=r/name;d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(activeWork='venue-street-cohesive-art-direction-review',currentMapArt=data,currentVisualReview=data['review'],lastArchiveIncludesLatest=False)
    if 'review' in d:d['review']=data['review']
    d['next']='Review whole-scene modern venue art direction03.01too flat/disconnected,02too literally DCSS.03is generated concept,not actual32px tile assets or native engine. Runtime remains ayame-zanshin02.'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='# 잔향도시 도트 방향03 / 2026-11-03\n\nanalysis/previews/venue-street03/index.html.01은매끈한블록/짜깁기,02는너무돌죽그대로라사용자거절.03은현대공연장거리소재+돌죽풍픽셀밀도/절제된명도의전체장면컨셉. 아직32px타일분리나실제엔진적용아님. runtime=ayame-zanshin02 유지.\n\n'
for name in ['CONTINUE_HERE.md','CURRENT_WORKSPACE.md','VFX_COMPANY_FEEDBACK.md','START_HERE_HOME.md']:
    p=r/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
print(json.dumps(data,ensure_ascii=False))
