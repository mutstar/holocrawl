"""Publish native framebuffer crops and raw screenshot links; never paint VFX."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, html, json, os, re

root=Path(__file__).resolve().parents[1]
run=root/'analysis/native/god-vfx-capture05'
shots=run/'native/shots'
proof=json.loads((run/'capture-validation.json').read_text())
assert proof['status']=='passed'
mapping=json.loads((root/'analysis/previews/current-god-art/mapping.json').read_text(encoding='utf-8'))
skills=json.loads((root/'scripts/god-art-skills.json').read_text(encoding='utf-8'))
assert set(skills)=={row['god'] for row in mapping['rows']}
source=(root/'engine/campaign-crawl/crawl-ref/source/holo-campaign.cc').read_text(encoding='utf-8')
choice_source=source[source.index('std::vector<choice> choices('):source.index('bool pick(')]
native_choices={g:{(int(t),int(o)):n for n,t,o in re.findall(r'\{"([^"\n]+)",(-?\d+),(-?\d+),',body)}
    for g,body in re.findall(r'if\(g=="(\w+)"\)return (.*?);',choice_source)}
# Name the actual captured branch rather than presenting a whole tier as one cast.
branches={
    ('suisei',1,0):('별자리 표식 · 표적 지정','별을 쌓을 적을 지정한다. 이후 공격으로 별을 축적하며, 지정 자체가 공격을 가하는 권능은 아니다.'),
    ('polka',1,1):('오늘의 공연 · 일점집중','강한 표적을 상대로 공연 과제를 시작한다. 과제 완수로 박수를 얻는다.'),
    ('polka',1,2):('오늘의 공연 · 외줄타기','외줄타기 공연 과제를 시작한다. 조건을 달성하면 박수를 얻는다.'),
    ('polka',1,3):('오늘의 공연 · 저글링','여러 적을 상대하는 저글링 공연 과제를 시작한다.'),
    ('polka',3,1):('공중곡예 · 박수 추가 소비','인접 적을 넘어 도약하고 다음 공격을 강화하며, 박수 1을 추가 소비해 주변 적을 약화한다.'),
    ('polka',5,0):('대단원 · 불꽃 피날레','박수를 소모해 지정 위치 주변에 화염 피해를 준다.'),
    ('polka',5,1):('대단원 · 커튼콜','박수를 소모해 HP를 회복하고 잠시 보호 효과를 얻는다.'),
    ('polka',5,2):('대단원 · 대혼란','박수를 소모해 주변 적을 밀치고 혼란 판정을 한다.'),
    ('koyori',1,1):('조수의 실험대 · 독성 시약 제조','MP를 사용해 독성 시약 재고를 준비한다. 제조 자체는 적을 공격하지 않는다.'),
    ('koyori',1,2):('조수의 실험대 · 발열 시약 제조','MP를 사용해 발열 시약 재고를 준비한다.'),
    ('koyori',1,3):('조수의 실험대 · 냉각 시약 제조','MP를 사용해 냉각 시약 재고를 준비한다.'),
    ('koyori',1,11):('조수의 실험대 · 독성 시약 투척','독성 시약 재고를 소비해 대상에게 독성 잔류물을 남긴다.'),
    ('koyori',1,12):('조수의 실험대 · 발열 시약 투척','발열 시약 재고를 소비해 대상을 공격하고 잔류 시약과 반응시킨다.'),
    ('koyori',1,13):('조수의 실험대 · 냉각 시약 투척','냉각 시약 재고를 소비해 대상을 공격하고 잔류 시약과 반응시킨다.'),
    ('koyori',5,3):('임계 실험 · 연소','다음 연소 반응을 강화하도록 준비한다. 이 사용 장면 자체가 연소 폭발은 아니다.'),
    ('koyori',5,4):('임계 실험 · 점액','다음 점액 반응을 강화하도록 준비한다.'),
    ('koyori',5,5):('임계 실험 · 열충격','다음 열충격 반응을 강화하도록 준비한다.'),
    ('raden',1,0):('전시 · 채색화','전시 작품을 채색화로 교체한다. 해당 작품의 가호와 사용 권능을 활성화한다.'),
    ('raden',1,1):('전시 · 조각','전시 작품을 조각으로 교체한다. 해당 작품의 가호와 사용 권능을 활성화한다.'),
    ('raden',1,2):('전시 · 공예품','전시 작품을 공예품으로 교체한다. 해당 작품의 가호와 사용 권능을 활성화한다.'),
    ('raden',3,0):('소장품 발동 · 채색 폭발','대상의 채색 중첩을 소모해 주변에 폭발 피해를 준다. 자신도 휘말릴 수 있다.'),
    ('raden',3,1):('소장품 발동 · 조각의 파동','지정 방향으로 파동을 보내 피해를 주고 적을 밀친다.'),
    ('raden',3,2):('소장품 발동 · 옻칠의 가호','보호막을 얻고 일부 해로운 상태를 완화한다.'),
    ('pekora',3,1):('당근 폭탄 · 지연 기폭','선택한 폭탄에 지연 신관을 설정한다. 폭발은 자신과 아군에게도 피해를 준다.'),
    ('sopia',6,0):('빅뱅 · 수동 기폭','준비된 빅뱅을 직접 기폭한다. 충전 및 실제 범위 조건에 따라 피해가 적용된다.'),
}

def describe(e):
    if e['tier'] in (1,3,5):
        name,kind,summary,visual=skills[e['god']][(1,3,5).index(e['tier'])]
    else:
        name,kind,summary,visual='빅뱅 수동 기폭','사용','준비된 빅뱅을 직접 기폭한다.','중력 효과'
    name,summary=branches.get((e['god'],e['tier'],e['option']),(name,summary))
    native=native_choices[e['god']].get((e['tier'],e['option']))
    assert native,(e['god'],e['tier'],e['option'])
    return dict(title=name,kind=kind,summary=summary,visual=visual,native=native)
out=root/'analysis/previews/god-vfx-ingame';out.mkdir(parents=True,exist_ok=True)
clips=out/'clips';clips.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
entries=[]
for file in sorted(shots.glob('*-frame0.png')):
    m=re.fullmatch(r'(\w+)-tier(-?\d+)-option(-?\d+)-(\d+)-frame0.png',file.name)
    assert m,file.name
    god,tier,option,seq=m.groups();stem=file.name[:-11]
    raw=[shots/(stem+'-'+s+'.png') for s in ['frame0','frame1','state']]
    assert all(p.is_file() for p in raw)
    frames=[Image.open(p).convert('RGB') for p in raw]
    assert all(im.size==(1152,800) for im in frames)
    meta=[json.loads(Path(str(p)+'.json').read_text()) for p in raw]
    assert meta[0]['effectCells']==meta[2]['effectCells']+1
    assert meta[1]['effectCells']==meta[2]['effectCells']+1
    assert frames[0].tobytes()!=frames[1].tobytes(),file.name
    assert frames[0].tobytes()!=frames[2].tobytes(),file.name
    crops=[]
    # Native 11x11-cell crop enlarged with nearest-neighbor; no overlay edits.
    for im,p in zip(frames,raw):
        crop=im.crop((195,164,547,516)).resize((480,480),Image.Resampling.NEAREST);crop.save(clips/p.name);crops.append(crop)
    crops[0].save(clips/(stem+'.gif'),save_all=True,append_images=[crops[1]],duration=550,loop=0)
    entries.append(dict(god=god,tier=int(tier),option=int(option),sequence=int(seq),stem=stem,
        gif='clips/'+stem+'.gif',frames=['clips/'+p.name for p in raw],
        originals=[os.path.relpath(p,out).replace('\\','/') for p in raw],
        hashes=[hashlib.sha256(p.read_bytes()).hexdigest().upper() for p in raw]))
assert {e['god'] for e in entries}=={r['god'] for r in mapping['rows']}
for e in entries:e.update(describe(e))
cards=[];selected=[]
for row in mapping['rows']:
    choices=sorted([e for e in entries if e['god']==row['god']],key=lambda e:e['sequence'])
    primary=next((e for e in choices if e['tier']==5),choices[0]);selected.append((row,primary))
    options=''.join('<option value="'+html.escape(e['stem'])+'"'+(' selected' if e==primary else '')+'>'+('추가 사용' if e['tier']==6 else str(e['tier'])+'성')+' · '+html.escape(e['title'])+' · #'+str(e['sequence'])+'</option>' for e in choices)
    powers=''.join('<div class="power'+(' selected-power' if tier==primary['tier'] else '')+'" data-tier="'+str(tier)+'"><h4>'+str(tier)+'성 · '+html.escape(name)+' <span>'+html.escape(kind)+'</span></h4><p><b>권능 효과:</b> '+html.escape(summary)+'</p><p class="visual"><b>화면 표시:</b> '+html.escape(visual)+'</p></div>' for tier,(name,kind,summary,visual) in zip((1,3,5),skills[row['god']]))
    cards.append('<article><h2>'+row['name']+'</h2><label>보고 있는 사용 장면<select onchange="choose(this)">'+options+'</select></label><section class="current"><h3 class="current-name">'+html.escape(primary['title'])+'</h3><p class="current-effect">'+html.escape(primary['summary'])+'</p><small class="current-native">실제 게임 메뉴: '+html.escape(primary['native'])+'</small></section><img class="scene" src="'+primary['gif']+'"><div class="buttons"><button onclick="mode(this,0)">1프레임</button><button onclick="mode(this,1)">2프레임</button><button onclick="mode(this,2)">효과 제거 후</button><button onclick="mode(this,3)">애니메이션</button></div><a class="raw" href="'+primary['originals'][0]+'" target="_blank">원본 전체 화면 보기</a><section class="power-list"><h3>권능 다시 보기</h3>'+powers+'</section></article>')
pages=[]
for part,start in enumerate(range(0,22,4),1):
    items=selected[start:start+4]
    sheet=Image.new('RGB',(1016,1160),'#111722');d=ImageDraw.Draw(sheet)
    d.text((18,12),f'실제 SDL 게임 화면 · 22신  {part}/6',font=font,fill='white')
    d.text((18,45),'테스트 전투장 · 고정 장비/높은 자원 · 성공한 권능의 2프레임째 · 원본은 갤러리에 포함',font=small,fill='#bdc9de')
    for i,(row,e) in enumerate(items):
        x=18+(i%2)*500;y=88+(i//2)*530
        d.text((x,y),row['name']+' · '+str(e['tier'])+'성 권능 사용 시',font=font,fill='#f9dda8')
        sheet.paste(Image.open(out/e['frames'][1]),(x,y+32))
    path=out/f'ingame-{part}.png';sheet.save(path);pages.append(path.name)
cards=[c.replace('<h2>스이세이</h2>','<h2>스이세이</h2><p><a href=\"../suisei-vfx04/index.html\"><b>새 1·3·5성 전용 효과 점검 보기</b></a><br>아래는 전용 효과를 나누기 전의 보존 캡처입니다.</p>',1) for c in cards]
data={e['stem']:e for e in entries}
doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>홀로죽 22신 실제 게임 화면</title><style>body{background:#101622;color:#edf2ff;font:16px "Malgun Gothic",sans-serif;margin:24px}p{line-height:1.7;color:#c1cde0}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:20px}article{background:#1c2636;border:1px solid #41516c;border-radius:10px;padding:16px}h2{margin-top:0}select,button{background:#283951;color:white;border:1px solid #607391;border-radius:5px;padding:7px;margin:3px}.scene{display:block;width:100%;max-width:480px;image-rendering:pixelated;margin:12px 0}a{color:#b8a2ff}.buttons{margin-bottom:10px}</style><h1>22신 · 실제 인게임 권능 사용 화면</h1><p>실제 SDL 게임 렌더러에서 성공한 권능 직후 저장한 화면입니다. 필드 11×11칸을 확대했으며 원본 전체 화면도 열 수 있습니다. 테스트 전투장·고정 장비·높은 HP/MP/신앙을 사용하며 일반 던전 플레이 영상은 아닙니다.<br>아래 움직임은 실제 두 프레임을 0.55초 간격으로 반복한 비교용입니다. 게임의 원래 효과 속도와 다릅니다. '효과 제거 후'는 같은 시점에서 순간 시전 알림만 지운 화면이며, 턴을 추가 진행한 장면이 아닙니다.<br>권능 선택 목록은 이번 실행에서 캡처한 호출만 포함합니다. 패시브·모든 선택 분기·명중 결과를 전부 보여주는 목록은 아닙니다.</p><main>'''+''.join(cards)+'''</main><script>const data='''+json.dumps(data,ensure_ascii=False)+''';function entry(a){return data[a.querySelector('select').value]}function choose(s){const a=s.closest('article'),e=entry(a);a.querySelector('.scene').src=e.gif;a.querySelector('.raw').href=e.originals[0]}function mode(b,m){const a=b.closest('article'),e=entry(a);a.querySelector('.scene').src=m===3?e.gif:e.frames[m];a.querySelector('.raw').href=e.originals[m===3?0:m]}</script></html>'''
doc=doc.replace('</style>','article{align-self:start}select{display:block;max-width:100%;width:100%;margin:8px 0}label{color:#b9cbe3;font-size:14px}.current{background:#26364b;border-left:3px solid #b4a0ff;padding:12px;margin-top:12px}.current h3{margin:0;color:#ffdf9a}.current p{margin:8px 0}.current small{color:#b5c5db;overflow-wrap:anywhere}.power-list{margin-top:22px}.power{border-top:1px solid #41516c;padding:12px 8px}.power h4{margin:0;color:#ffdda5}.power h4 span{display:inline-block;font-size:12px;color:#b6c8df;border:1px solid #607391;border-radius:4px;padding:2px 5px;margin-left:5px}.power p{margin:8px 0}.power .visual{font-size:14px;color:#aabed7}.selected-power{background:#26344a;border-left:3px solid #b4a0ff}</style>')
doc=doc.replace('<main>','<p><b>권능 해금: 1성 신앙 30 / 3성 75 / 5성 120.</b> 자동은 조건을 만족할 때 적용되는 가호, 사용은 직접 고르는 권능입니다. 각 카드 아래에 1·3·5성의 실제 효과와 화면 표시를 구분해 적었습니다. MP/신앙 비용은 선택 장면의 실제 영어 메뉴를 함께 확인하세요.<br>같은 신의 여러 권능이 같은 순간 효과를 공유할 수 있습니다. 순간 효과의 모양 자체가 피해 범위나 제어 성공을 뜻하지는 않습니다.</p><main>')
old="a.querySelector('.scene').src=e.gif;a.querySelector('.raw').href=e.originals[0]}"
new="a.querySelector('.scene').src=e.gif;a.querySelector('.raw').href=e.originals[0];a.querySelector('.current-name').textContent=e.title;a.querySelector('.current-effect').textContent=e.summary;a.querySelector('.current-native').textContent='실제 게임 메뉴: '+e.native;a.querySelectorAll('.power').forEach(p=>p.classList.toggle('selected-power',Number(p.dataset.tier)===e.tier))}"
assert old in doc
doc=doc.replace(old,new)
assert doc.count('class=\"power ')+doc.count('class=\"power\"')==66
(out/'index.html').write_text(doc,encoding='utf-8')
result=dict(status='passed',gods=22,successfulInvocations=len(entries),rawScreenshots=len(entries)*3,
    abilitySummaries=66,allCapturedChoicesNamed=True,nativeCapture=proof,contactPages=pages,source='Actual native SDL framebuffers; field crops only; no composited VFX',
    gallery=out.relative_to(root).as_posix()+'/index.html',entries=entries)
(run/'gallery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='entries'},ensure_ascii=False,indent=2))
