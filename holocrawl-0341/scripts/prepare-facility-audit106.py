"""Seven-facility/30-member audit, four local product-detail visibility repairs."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'preview/city-facilities105';OUT=ROOT/'preview/city-facilities106'
AUDIT=ROOT/'preview/facility-member-audit106';OUT.mkdir(parents=True,exist_ok=True)
prior=json.loads((SRC/'manifest.json').read_text(encoding='utf-8'))
plan=json.loads((AUDIT/'plan.json').read_text(encoding='utf-8'))
roster=plan['roster'];assert sum(map(len,roster.values()))==30
motifs={
 'mountain':['암벽 부조 · 긴 머리와 별 장식','암벽 부조 · 단발과 안경','암벽 부조 · 긴 생머리','암벽 부조 · 분홍 머리와 무녀 옷','암벽 부조 · 푸른 머리와 체크 의상'],
 'dining':['장미 꽃병','거미 라면','흰여우 찻주전자','에비프라이온 접시'],
 'fantasy':['방패 타격 연습대','해적기 결승 표지','노우사기 훈련 표적','궁술 연습대'],
 'wheel':['천사 날개·고리 곤돌라','왕관 곤돌라','양뿔·양 귀 곤돌라','악마 귀·날개 곤돌라'],
 'market':['설야월 술병·눈꽃 라벨','복숭아 젤리','흰 사자 컵라면','서커스 팝콘'],
 'holox':['뿔·사슬 봉인 격납고','붉은 매 관제 단말','분홍 시약 연구대','잠수 장비 거치대','카타나·검문기'],
 'dev':['연주용 건반','CEO 접수대','노멘 전시대','반펜 연습 코너']}
fixed={('dining','haato'),('market','lamy'),('market','nene'),('market','botan')}
edits={'dining':[(103,96,120,105)],'market':[(43,51,54,63),(69,169,86,183),(200,75,217,90)]}

def repairs(im,id):
    d=ImageDraw.Draw(im)
    if id=='dining':
        # Eight jointed legs read separately from the remaining noodle pixels.
        ink=(38,26,32);light=(96,48,49)
        for y,dy in [(97,-1),(98,-2),(100,2),(101,3)]:
            d.line([(110,y),(107,y+dy),(104,y+dy)],fill=ink)
            d.line([(114,y),(117,y+dy),(119,y+dy)],fill=ink)
        d.ellipse((110,97,114,102),fill=ink);d.rectangle((111,96,113,98),fill=ink)
        d.point((111,97),fill=light);d.point((113,97),fill=light)
    if id=='market':
        # Blue bottle retained. An eight-armed snowflake replaces the tiny plus.
        d.rectangle((43,51,53,62),fill=(216,232,222))
        star=['....b....','.b..b..b.','..b.b.b..','...bbb...','bbbbbbbbb','...bbb...','..b.b.b..','.b..b..b.','....b....']
        for y,row in enumerate(star):
            for x,c in enumerate(row):
                if c=='b':d.point((44+x,52+y),fill=(68,119,151))
        # Peach jelly stays in the same crate/product: two lobes, seam, leaf.
        d.rectangle((69,172,85,182),fill=(236,199,144))
        d.line((70,173,84,173),fill=(255,226,177))
        d.ellipse((72,174,78,180),fill=(238,146,127));d.ellipse((77,174,83,180),fill=(231,127,112))
        d.polygon([(73,178),(82,178),(78,181)],fill=(238,146,127))
        d.line((78,175,77,179),fill=(188,93,92));d.line((74,175,76,175),fill=(255,195,162))
        d.line((78,173,79,171),fill=(93,104,63));d.polygon([(79,172),(80,169),(84,170),(82,172)],fill=(125,154,76))
        # A stepped white mane around a small face distinguishes the lion cup.
        d.rectangle((204,75,212,77),fill=(224,221,200));d.rectangle((201,78,215,85),fill=(224,221,200))
        d.rectangle((203,85,213,87),fill=(218,215,193));d.rectangle((205,87,211,89),fill=(198,200,178))
        for x in [202,212]:d.rectangle((x,76,x+2,79),fill=(238,230,206));d.point((x+1,78),fill=(123,132,108))
        d.rectangle((205,79,211,85),fill=(242,230,202))
        for x in [205,211]:d.point((x,81),fill=(58,69,61))
        d.rectangle((208,83,209,83),fill=(90,84,66));d.point((208,85),fill=(126,118,91))

manifest={**prior,'revision':106,'title':'잔향도시 · 고정지형 멤버 요소 점검',
 'styles':[{'id':'new106','label':'멤버 요소 점검·보완'},{'id':'previous105','label':'보완 전105'}],
 'defaultSample':3,'maps':[],'memberAudit':'member-audit.json'}
checks=[];audit=[];cards=[]
for m in prior['maps']:
    id=m['facility'];o=m['origin'];x0,y0=o['x']*32,o['y']*32;w,h=o['width'],o['height']
    data=json.loads((SRC/m['map']).read_text());local=[r[o['x']:o['x']+w] for r in data['rows'][o['y']:o['y']+h]]
    allowed=np.zeros((h*32,w*32),bool)
    for box in edits.get(id,[]):allowed[box[1]:box[3],box[0]:box[2]]=True
    blocked=np.repeat(np.repeat(np.array([[c in '#G' for c in row] for row in local]),32,0),32,1)
    assert not np.any(allowed&~blocked)
    outputs={}
    for state,name in [('closed',m['images']['new105']),('open',m['openImage'])]:
        im=Image.open(SRC/name).convert('RGBA');before=np.array(im);scene=im.crop((x0,y0,x0+w*32,y0+h*32));repairs(scene,id)
        a=np.array(scene);old=before[y0:y0+h*32,x0:x0+w*32];assert np.array_equal(a[~allowed],old[~allowed])
        im.paste(scene,(x0,y0));im.convert('RGB').save(OUT/f'{id}-{state}106.png');outputs[state]=scene
        im.crop((max(0,x0-32),max(0,y0-32),min(im.width,x0+w*32+32),min(im.height,y0+h*32+48))).convert('RGB').save(OUT/f'{id}-detail-{state}.png')
    members=[]
    for i,(key,name,box) in enumerate(roster.get(id,[])):
        motif=motifs[id][i];status='visibility-improved' if (id,key) in fixed else 'retained'
        crop=outputs['closed'].crop(box);crop.save(OUT/f'{id}-{key}-detail.png')
        before=Image.open(AUDIT/f'{id}-{key}-before.png').convert('RGBA');same=np.array_equal(np.array(crop),np.array(before))
        assert same==((id,key) not in fixed),(id,key,same)
        entry={'id':key,'name':name,'motif':motif,'box':box,'present':True,'decision':status,'detailImage':f'{id}-{key}-detail.png',
          'unchangedFrom105':same,'evidence':'Visual review at native scale and3x crop against original facility motif data.'}
        members.append({'id':key,'name':name+' · '+motif,'box':box,'auditDecision':status});audit.append({'facility':id,**entry});cards.append((id,name,crop,status))
    shutil.copy2(SRC/m['images']['new105'],OUT/f'{id}-previous105.png');shutil.copy2(SRC/m['map'],OUT/m['map'])
    assert (OUT/m['map']).read_bytes()==(SRC/m['map']).read_bytes()
    manifest['maps'].append({**m,'images':{'new106':f'{id}-closed106.png','previous105':f'{id}-previous105.png'},'openImage':f'{id}-open106.png',
      'memberDetails':members or m['memberDetails']})
    checks.append({'facility':id,'auditedMembers':len(members),'geometryUnchanged':True,'editsOnlyOnExistingInteriorBlockedCells':True,
      'outsideFourDetailBoxesUnchanged':True,'walls105AndDoors105Unchanged':True,'mapSha256':hashlib.sha256((OUT/m['map']).read_bytes()).hexdigest()})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheet=Image.new('RGB',(1360,2560),'#151c20');d=ImageDraw.Draw(sheet)
for i,id in enumerate(roster):
    m=next(m for m in manifest['maps'] if m['facility']==id);x=i%2*680;y=i//2*640
    d.text((x+12,y+6),m['name'],font=font,fill='#e4ece6');o=m['origin']
    im=Image.open(OUT/m['images']['new106']).crop((o['x']*32,o['y']*32,(o['x']+o['width'])*32,(o['y']+o['height'])*32))
    sheet.paste(im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST),(x+22,y+36))
sheet.save(OUT/'seven-facilities.png')
sheet=Image.new('RGB',(1200,1500),'#151c20');d=ImageDraw.Draw(sheet)
for i,(id,name,im,status) in enumerate(cards):
    x=i%5*240;y=i//5*250;d.text((x+8,y+5),id+' / '+name,font=font,fill='#efd28d' if status=='visibility-improved' else '#e1eae4')
    im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST);sheet.paste(im,(x+(240-im.width)//2,y+38))
sheet.save(OUT/'all-member-crops.png')
board=Image.new('RGB',(960,500),'#151c20');bd=ImageDraw.Draw(board)
for i,(fac,key) in enumerate([('dining','haato'),('market','lamy'),('market','nene'),('market','botan')]):
    entry=next(e for e in audit if e['facility']==fac and e['id']==key)
    for row,(label,path) in enumerate([('이전',AUDIT/f'{fac}-{key}-before.png'),('보완',OUT/entry['detailImage'])]):
        x=i*240;y=row*250;bd.text((x+10,y+5),entry['name']+' · '+label,font=font,fill='#e8cc91' if row else '#bdcec3')
        im=Image.open(path).convert('RGB');im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
        board.paste(im,(x+(240-im.width)//2,y+38))
board.save(OUT/'four-details-before-after.png')
assert len(audit)==30 and sum(a['decision']=='visibility-improved' for a in audit)==4
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'member-audit.json').write_text(json.dumps({'facilities':7,'members':30,'missing':0,'retained':26,'improved':4,'checks':audit,
 'scope':'Existing project roster only. Artistic visibility review, not user recognition testing or campaign validation.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'status':'passed','facilities':9,'auditedFacilities':7,'auditedMembers':30,'improved':4,'checks':checks,
 'nativeIntegration':False},indent=2)+'\n')
print('Audited30 member motifs:26 preserved pixel-identically,4 local visibility improvements; all9 map geometries preserved.')
