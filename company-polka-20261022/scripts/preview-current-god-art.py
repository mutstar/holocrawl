"""Read-only contact sheets of current shipped tiles; no game assets modified."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import html,json,hashlib,re
root=Path(__file__).resolve().parents[1]
out=root/'analysis/previews/current-god-art';out.mkdir(parents=True,exist_ok=True)
tiles=root/'engine/campaign-crawl/crawl-ref/source/rltiles/holo'
native=root/'analysis/native/tiles01/wrath02-sdl01'
# Effect routing follows holo-visual::invocation/at and holo-sopia::visual_at.
# These are individual tile samples, not simulated in-engine field captures.
rows=[
 ('suisei','스이세이','comet', [('fx_warning','혜성 경고'),('fx_urgent','긴급 경고')],'혜성 낙하 · 고정 위치 경고'),
 ('miko','미코','shrine',[('fx_shrine','성역 장판')],'유지: 성역 범위'),
 ('aki','아키','garden',[('fx_garden','정원 장판'),('rose','장미 아군')],'유지: 정원 · 소환: 장미'),
 ('fubuki','후부키','foxflame',[('fox','여우 아군')],'소환: 여우'),
 ('ayame','아야메','oni',[('swordsman','징벌: 검사')],'검사는 배교 징벌용'),
 ('choco','초코','charm',[],'별도 지속 장판 없음'),
 ('korone','코로네','punch',[('hound','징벌: 사냥개')],'사냥개는 배교 징벌용'),
 ('okayu','오카유','sleep',[],'별도 지속 장판 없음'),
 ('pekora','페코라','carrotburst',[('carrot','당근 폭탄'),('fx_warning','폭발 경고')],'폭탄 설치 · 노랑→빨강 경고'),
 ('noel','노엘','shield',[('fx_shield','보호 표시')],'유지: 은빛 지휘 활성 시 보호 표시'),
 ('watame','와타메','shield',[('fx_shield','보호 표시')],'유지: 3성 보호 효과'),
 ('towa','토와','devil',[('fx_spotlight','장판')],'유지: 스포트라이트 범위'),
 ('lamy','라미','frost',[('fx_frost','5성 표시')],'유지: 5성 활성 시 본인 칸'),
 ('polka','폴카','circus',[],'별도 지속 장판 없음'),
 ('koyori','코요리','reagent',[('fx_slime','점액 장판')],'유지: 점액 범위'),
 ('lui','루이','ravenflight',[('raven','까마귀 아군')],'소환: 까마귀'),
 ('raden','라덴','exhibit',[('fx_exhibit','5성 표시')],'탈 제단 · 5성 활성 시 본인 칸'),
 ('hajime','하지메','rhythm',[('fx_rhythm','리듬 장판')],'유지: 5성 활성 시 주변 1칸'),
 ('su','스우','water',[('fx_water','물 장판')],'유지: 물길 · 5성 주변 수역'),
 ('vivi','비비','spotlight',[('fx_spotlight','5성 표시')],'유지: 5성 활성 시 본인 칸'),
 ('sopia','소피아','gravity',[('fx_orbit','고리'),('fx_gravity','중력장')],'유지: 주변 고리 · 중력장'),
 ('mela','메라','fire',[('fx_fire','도깨비불')],'유지: 5성 활성 시 본인 칸'),
]
skills=json.loads((root/'scripts/god-art-skills.json').read_text(encoding='utf-8'))
assert set(skills)=={r[0] for r in rows} and all(len(v)==3 for v in skills.values())
source=(root/'engine/campaign-crawl/crawl-ref/source/holo-campaign.cc').read_text(encoding='utf-8')
choices=source[source.index('std::vector<choice> choices('):source.index('bool pick(')]
native_choices={}
for g,body in re.findall(r'if\(g=="(\w+)"\)return (.*?);',choices):
    native_choices[g]=[dict(name=n,tier=int(t)) for n,t in re.findall(r'\{"([^"\n]+)",(-?\d+),',body)]
assert set(native_choices)==set(skills)
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/malgun'+('bd' if b else '')+'.ttf',n)
title=font(25,True);small=font(15);text=font(18);header=font(30,True)
def tile(name,frame):
    if name.startswith('fx_'):name+='_'+str(frame)
    elif name in ['rose','fox','raven','swordsman','hound'] and frame:name+='_1'
    return Image.open(tiles/(name+'.png')).convert('RGBA')
def sheet(items,part,frame):
    w=440;h=238;gap=16;top=112;cols=3;nrows=(len(items)+cols-1)//cols
    im=Image.new('RGBA',(cols*w+(cols+1)*gap,top+nrows*(h+gap)),(15,19,29,255));d=ImageDraw.Draw(im)
    d.text((20,15),'현재 게임 도트 — 제단 · 이펙트 · 장판',font=header,fill='#f2ecff')
    d.text((22,60),f'{part}/2   |   원본 32×32 · 최근접 확대 · 타일 견본 (실제 필드 화면은 별도)',font=text,fill='#bac5dc')
    for i,(g,name,fx,extras,note) in enumerate(items):
        x=gap+(i%cols)*(w+gap);y=top+(i//cols)*(h+gap)
        d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill='#202838',outline='#39485e')
        d.text((x+14,y+8),name,font=title,fill='#ffffff')
        for xx,label in [(20,'제단'),(140,'권능 사용 시 효과'),(264,'유지 / 소환 / 경고')]:d.text((x+xx,y+46),label,font=font(12) if label=='권능 사용 시 효과' else small,fill='#b9c8e1')
        im.alpha_composite(tile('altar_'+g,0).resize((96,96),Image.Resampling.NEAREST),(x+16,y+74))
        im.alpha_composite(tile('fx_'+fx,frame).resize((96,96),Image.Resampling.NEAREST),(x+136,y+74))
        d.text((x+139,y+174),'공통 타격' if fx=='impact' else {'comet':'혜성','shrine':'성역','garden':'정원','shield':'보호','spotlight':'스포트라이트','frost':'서리','exhibit':'전시','rhythm':'리듬','water':'물결','gravity':'중력','fire':'도깨비불','foxflame':'여우불','oni':'붉은 쌍검','charm':'유혹','punch':'연속 주먹','sleep':'수면','carrotburst':'당근 폭발','devil':'악마 날개','circus':'서커스','reagent':'시약 반응','ravenflight':'까마귀 지휘'}[fx],font=small,fill='#d3d9e8')
        for j,(asset,label) in enumerate(extras):
            xx=x+258+j*86
            im.alpha_composite(tile(asset,frame).resize((72,72),Image.Resampling.NEAREST),(xx,y+88))
            d.text((xx,y+174),label,font=small,fill='#ffc98c' if '징벌' in label else '#d3d9e8')
        if not extras:d.text((x+276,y+116),'없음',font=text,fill='#7d8ba4')
        d.text((x+14,y+208),note,font=small,fill='#b8c5dc')
    return im.convert('RGB')
for part,items in enumerate([rows[:12],rows[12:]],1):
    frames=[sheet(items,part,f) for f in range(2)]
    frames[0].save(out/f'gods-{part}.png')
    frames[0].save(out/f'gods-{part}.gif',save_all=True,append_images=frames[1:],duration=550,loop=0)
# Field crops come directly from frozen, tested SDL framebuffers, with no
# inserted effects. Layout/cropping only; keep native source images untouched.
examples=[('sanctuary','미코 · 성역'),('orbit-gravity','소피아 · 고리 / 중력장'),('garden-roses','아키 · 정원 / 장미'),('water-field','스우 · 물 장판'),('ghostfire','메라 · 도깨비불'),('bombs-urgent','페코라 · 폭탄 / 긴급 경고')]
im=Image.new('RGB',(1228,940),'#0f131d');d=ImageDraw.Draw(im)
d.text((18,12),'실제 SDL 게임 화면 — 필드 부분 발췌',font=header,fill='white')
for i,(name,label) in enumerate(examples):
    x=16+(i%3)*404;y=72+(i//3)*434
    d.text((x,y),label,font=text,fill='#e0e6f2')
    # Viewport center is near (371,340); preserve native pixel art at 2x.
    crop=Image.open(native/(name+'.png')).crop((275,244,467,436)).resize((384,384),Image.Resampling.NEAREST)
    im.paste(crop,(x,y+28))
im.save(out/'native-fields.png')
proof=dict(tileSize=32,source='shipped PNG tiles; original pixels preserved',individualTileSamples=True,nativeCrops=[n for n,_ in examples],godCount=len(rows),sharedImpactGods=[g for g,_,fx,_,_ in rows if fx=='impact'],rows=[dict(god=g,name=name,invocation=fx,extra=[a for a,_ in ex],note=note) for g,name,fx,ex,note in rows])
proof['abilities']=skills;proof['nativeMenuChoices']=native_choices
(out/'mapping.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
# Self-contained viewer: frame swapping is display-only and not game timing.
import base64
cards=[]
for g,name,fx,ex,note in rows:
    def img(asset,animated=False):
        paths=[tiles/((asset+'_'+str(f) if asset.startswith('fx_') else asset+('_1' if animated and f else ''))+'.png') for f in range(2)]
        if not animated and not asset.startswith('fx_'):paths=[tiles/(asset+'.png')]*2
        urls=['data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in paths]
        return '<img src="'+urls[0]+'" data-a="'+urls[0]+'" data-b="'+urls[1]+'">'
    abilities=''.join('<div class="skill"><div class="skill-title"><b class="tier">'+str(tier)+'성</b> <strong>'+html.escape(n)+'</strong><span class="kind">'+html.escape(kind)+'</span></div><p>'+html.escape(summary)+'</p><small>그림 연결: '+html.escape(visual)+'</small></div>' for tier,(n,kind,summary,visual) in zip([1,3,5],skills[g]))
    choices_html='<details><summary>실제 게임 메뉴 이름 · MP/신앙 비용</summary>'+''.join('<p><b>'+('기타' if c['tier'] not in [1,3,5] else str(c['tier'])+'성')+'</b> '+html.escape(c['name'])+'</p>' for c in native_choices[g])+'</details>'
    cards.append('<article><h2>'+name+'</h2><div class="samples"><section><h3>제단</h3>'+img('altar_'+g)+'</section><section><h3>권능 사용 시 효과'+(' · 공통' if fx=='impact' else '')+'</h3>'+img('fx_'+fx)+'</section><section><h3>유지 / 소환 / 경고</h3>'+(''.join(img(a,a in ['rose','fox','raven','swordsman','hound']) for a,_ in ex) or '<p>없음</p>')+'</section></div><p>'+html.escape(note)+'</p><div class="skills">'+abilities+'</div>'+choices_html+'</article>')
doc='''<!doctype html><meta charset="utf-8"><title>HoloCrawl 현재 도트 22신</title><style>body{background:#0f131d;color:#eef3ff;font:16px "Malgun Gothic",sans-serif;margin:24px}h1{margin-bottom:8px}button{background:#7e68c7;color:white;border:0;border-radius:8px;padding:10px 20px;cursor:pointer}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(410px,1fr));gap:16px}article{background:#202838;border:1px solid #39485e;border-radius:12px;padding:16px}h2{margin:0 0 16px}h3{font-size:13px;color:#b9c8e1}.samples{display:flex;gap:24px;min-height:155px}section:nth-child(3){flex:1}img{width:96px;height:96px;image-rendering:pixelated}section:nth-child(3) img{width:64px;height:64px}p{color:#b8c5dc;line-height:1.65}.native{width:min(100%,1228px);height:auto;image-rendering:pixelated}</style><h1>현재 게임 도트 · 22신</h1><p>제단 / 권능 사용 시 효과 / 유지 장판·소환물. 원본 32×32를 확대했습니다. 순간 효과는 신별로 구분합니다. 노엘·와타메는 보호빛을 공유합니다.<br>권능 사용 시 효과는 순간 시전 알림이며 공격 범위를 뜻하지 않습니다. 실제 장판·폭발 경고는 별도 표시입니다.<br>검사·사냥개는 배교 징벌용입니다. 아래 타일 견본은 실제 시전 화면과 구분합니다.</p><button onclick="playing=!playing;this.textContent=playing?'애니메이션 멈춤':'애니메이션 재생'">애니메이션 멈춤</button><p>두 프레임을 천천히 번갈아 표시합니다. 게임의 실제 효과 표시 속도와는 다릅니다.</p><main>'''+''.join(cards)+'''</main><h2 style="margin-top:32px">실제 게임 화면 · 필드 발췌</h2><img class="native" src="data:image/png;base64,'''+base64.b64encode((out/'native-fields.png').read_bytes()).decode()+'''"><script>let playing=true,frame=0;setInterval(()=>{if(!playing)return;frame^=1;document.querySelectorAll('[data-a]').forEach(i=>i.src=i.dataset[frame?'b':'a'])},550)</script>'''
doc=doc.replace('</style>','''.skill{border-top:1px solid #39485e;padding:12px 0}.skill p{margin:7px 0;color:#eef3ff}.skill small{color:#9babc5}.skill-title{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.tier{color:#ffd086}.kind{font-size:12px;border:1px solid #596b85;border-radius:5px;padding:2px 6px;color:#b8c5dc}details{border-top:1px solid #39485e;padding-top:12px}summary{cursor:pointer;color:#ccb9ff}details p{font-size:13px}article{align-self:start}</style>''')
doc=doc.replace('현재 게임 도트 · 22신','22신 제단 · 권능 · 이펙트 안내')
doc=doc.replace('<main>','<p><b>해금 신앙: 1성 30 / 3성 75 / 5성 120.</b> 자동 = 조건을 만족하면 작동, 사용 = 직접 사용. 한글명은 설계 명칭이며 펼치면 현재 영어 메뉴와 비용을 볼 수 있습니다. 회복·상태는 대상 조건과 판정에 따라 적용됩니다.</p><main>')
doc=doc.replace('<main>','<p><a href="../god-vfx-ingame/index.html">22신 실제 게임 화면 · 프레임 비교 · 원본 화면 보기</a></p><main>')
(out/'index.html').write_text(doc,encoding='utf-8')

def wrap_lines(s,f,width):
    lines=[];line=''
    for ch in s:
        if f.getlength(line+ch)>width:
            lines.append(line);line=ch
        else:line+=ch
    if line:lines.append(line)
    return lines

def skill_sheet(items,part):
    w=600;h=510;gap=18;top=116;cols=2;nrows=(len(items)+1)//2
    im=Image.new('RGBA',(cols*w+3*gap,top+nrows*(h+gap)),(15,19,29,255));d=ImageDraw.Draw(im)
    d.text((20,14),f'22신 권능 · 도트 연결표  {part}/4',font=header,fill='#f2ecff')
    d.text((22,59),'1성 신앙30 / 3성75 / 5성120 · 자동 가호와 직접 사용 구분',font=text,fill='#bac5dc')
    for i,(g,name,fx,extras,note) in enumerate(items):
        x=gap+(i%2)*(w+gap);y=top+(i//2)*(h+gap)
        d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill='#202838',outline='#39485e')
        d.text((x+16,y+8),name,font=title,fill='white')
        for xx,label in [(22,'제단'),(150,'권능 사용 시 효과'),(286,'유지 / 소환 / 경고')]:d.text((x+xx,y+44),label,font=font(12) if label=='권능 사용 시 효과' else small,fill='#b9c8e1')
        im.alpha_composite(tile('altar_'+g,0).resize((96,96),Image.Resampling.NEAREST),(x+16,y+68))
        im.alpha_composite(tile('fx_'+fx,0).resize((96,96),Image.Resampling.NEAREST),(x+146,y+68))
        for j,(asset,label) in enumerate(extras):
            xx=x+284+j*144
            im.alpha_composite(tile(asset,0).resize((80,80),Image.Resampling.NEAREST),(xx,y+76))
            d.text((xx,y+163),label,font=small,fill='#ffc98c' if '징벌' in label else '#d3d9e8')
        if not extras:d.text((x+300,y+112),'지속 장판 없음',font=text,fill='#8c9ab0')
        d.text((x+148,y+166),'공통 타격' if fx=='impact' else '권능 사용 시 효과',font=small,fill='#aab8ce')
        for k,(tier,(n,kind,summary,visual)) in enumerate(zip([1,3,5],skills[g])):
            yy=y+203+k*99
            d.line((x+14,yy-7,x+w-14,yy-7),fill='#39485e')
            label=f'{tier}성  {n}'
            d.text((x+16,yy),label,font=font(20,True),fill='#ffda9e')
            d.text((x+w-18-d.textlength(kind,font=small),yy+3),kind,font=small,fill='#a8c9f2')
            ls=wrap_lines(summary,text,w-32)
            assert len(ls)<=2,(g,n,summary)
            for l,line in enumerate(ls):d.text((x+16,yy+30+l*22),line,font=text,fill='#eef3ff')
            # At most one line for art mapping; fit the longest explicit notes.
            vf=next(f for f in (small,font(14),font(13),font(12)) if f.getlength('그림: '+visual)<=w-32)
            assert vf.getlength('그림: '+visual)<=w-32,(g,visual)
            d.text((x+16,yy+72),'그림: '+visual,font=vf,fill='#9eafc9')
    return im.convert('RGB')
for part,start in enumerate(range(0,len(rows),6),1):skill_sheet(rows[start:start+6],part).save(out/f'skills-{part}.png')
assert sum(len(v) for v in skills.values())==66
(out/'skills-validation.json').write_text(json.dumps(dict(status='passed',gods=22,tierSummaries=66,nativeMenuChoices=sum(map(len,native_choices.values())),pages=4,allTextFits=True,gameAssetsModified=False),indent=2)+'\n',encoding='utf-8')
print(str(out))
