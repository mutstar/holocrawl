"""Collect the requested merchandise roster and small official-art source sprites.

Art processing is limited to alpha bounds and nearest-neighbour size conversion.
The acrylic base/outline and T-shirts are rendered by browser code, not painted
into the official source art. Colour references are not claimed as official hex.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image
from io import BytesIO
import json,re,html,unicodedata,shutil

r=Path(__file__).resolve().parents[1];audit=r/'analysis/market02';out=r/'preview/city-market02';assets=out/'assets/members'
audit.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40)as response:return response.read()
        except Exception:
            if attempt==2:raise
def norm(text):return re.sub(r'[\s・･\[\]「」（）()]+','',unicodedata.normalize('NFKC',html.unescape(text))).lower()
page=(audit/'official-roster.html').read_text(encoding='utf-8')
section=page[page.index('<ul class="talent_list'):];section=section[:section.index('</ul>')]
colors={}
color_source='https://vtubernews.com/datalist-0009/'
color_page=(audit/'member-color-reference.html').read_text(encoding='utf-8')
for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',color_page,re.S):
    color=re.search(r'#[0-9a-fA-F]{6}\b',row)
    if color:
        cells=re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.S)
        if cells:colors[norm(re.sub('<[^>]*>','',cells[0]))]=color[0]
members=[]
for block in re.findall(r'<li\b[^>]*>(.*?)</li>',section,re.S):
    u=re.search(r'<a href="([^"]+)"',block);n=re.search(r'<h3>(.*?)<span>(.*?)</span>',block,re.S)
    if not(u and n):continue
    slug=u[1].rstrip('/').split('/')[-1]
    if slug in ['friend-a','harusaki-nodoka']:continue
    name=html.unescape(n[1].strip());jp=html.unescape(n[2].strip())
    status='alum' if '[Alum]' in name else 'affiliate' if '[Affiliate]' in name else 'active'
    name=re.sub(r'^\[[^]]+\]\s*','',name)
    members.append(dict(id=slug,name=name,nameJa=jp,status=status,profile=u[1]))
# Former JP members whose pages no longer appear in the live directory.
for slug,name,jp in [('yozora-mel','Yozora Mel','夜空メル'),('uruha-rushia','Uruha Rushia','潤羽るしあ'),('mano-aloe','Mano Aloe','魔乃アロエ')]:
    members.append(dict(id=slug,name=name,nameJa=jp,status='former',profile='https://hololive.hololivepro.com/en/talents/'+slug+'/'))
def work(member):
    cache=audit/(member['id']+'.json')
    if cache.exists() and (assets/(member['id']+'.png')).exists():return json.loads(cache.read_text(encoding='utf-8'))
    try:
        profile=fetch(member['profile']).decode('utf-8')
        tags=re.findall(r'<img\b[^>]*>',profile,re.S)
        candidates=[]
        for tag in tags:
            if ('全身画像' in tag or 'pr-img' in tag or 'full_body' in tag):
                url=re.search(r'\bsrc=["\']([^"\']+)',tag)
                if url and url[1] not in candidates:candidates.append(html.unescape(url[1]))
        if not candidates:raise RuntimeError('No full-body image on official profile')
    except Exception as exc:
        # The old official image URLs are still hosted after some profile removals.
        known={'yozora-mel':['https://static.wikitide.net/hololivewiki/9/9f/Yozora_Mel_-_Full_Illustration_01-2.png'],
               'uruha-rushia':['https://static.wikitide.net/hololivewiki/4/46/Uruha_Rushia_-_Full_Illustration_01.png'],
               'mano-aloe':['https://static.wikitide.net/hololivewiki/a/a9/Mano_Aloe_-_Full_Illustration_01.png']}
        if member['id'] not in known:raise
        candidates=known[member['id']]
        if member['id']=='yozora-mel' and (audit/'mel-cutout.png').exists():
            candidates=[(audit/'mel-cutout.png').as_uri()]+candidates
    errors=[];image=None
    for url in candidates:
        try:
            raw=fetch(url);candidate=Image.open(BytesIO(raw)).convert('RGBA')
            if candidate.getchannel('A').getextrema()[0]!=0:raise RuntimeError('Source has no transparent silhouette')
            image=candidate;source=url;break
        except Exception as exc:errors.append(str(exc))
    if image is None:raise RuntimeError(member['id']+': '+'; '.join(errors))
    bounds=image.getchannel('A').point(lambda v:255 if v>128 else 0).getbbox();sprite=image.crop(bounds)
    sprite.thumbnail((64,112),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(64,112));canvas.alpha_composite(sprite,((64-sprite.width)//2,112-sprite.height))
    canvas.save(assets/(member['id']+'.png'))
    color=colors.get(norm(member['nameJa']))
    source_note=color_source
    if not color:
        # Explicitly provisional artwork-derived hue for members absent from the colour table.
        samples=[]
        for rr,gg,bb,aa in sprite.getdata():
            hi=max(rr,gg,bb);lo=min(rr,gg,bb)
            if aa>220 and hi>65 and hi-lo>45:samples.append((rr//32*32,gg//32*32,bb//32*32))
        from collections import Counter
        rgb=Counter(samples).most_common(1)[0][0] if samples else (120,150,175)
        color='#' + ''.join(f'{min(235,max(45,v)):02x}' for v in rgb);source_note='provisional hue sampled from official character artwork'
    member.update(image='assets/members/'+member['id']+'.png',artSource=source,color=color,colorSource=source_note,colorStatus='representative preview colour; not a claim of official brand hex')
    if member['id']=='yozora-mel':
        member.update(originalArtSource='https://hololive.wiki/wiki/Yozora_Mel',processing='Background extracted with built-in image_gen, then nearest resize')
    cache.write_text(json.dumps(member,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return member
completed={};errors={}
with ThreadPoolExecutor(max_workers=5)as pool:
    future_map={pool.submit(work,m):m for m in members}
    for future in as_completed(future_map):
        member=future_map[future]
        try:completed[member['id']]=future.result();print('OK '+member['id'],flush=True)
        except Exception as exc:errors[member['id']]=str(exc);print('FAIL '+member['id']+' '+str(exc),flush=True)
roster=[completed[m['id']]for m in members if m['id']in completed]
for member in roster:
    if member['id']=='mano-aloe':
        member.update(color='#E76BA8',colorSource='provisional pink based on character costume, pending art review')
        (audit/(member['id']+'.json')).write_text(json.dumps(member,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=dict(scope='JP EN ID DEV_IS including affiliates/alumni/former; no staff or Holostars',source='https://hololive.hololivepro.com/en/talents/',members=roster,expected=len(members),errors=errors)
(audit/'roster-fetch.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'members.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'members.js').write_text('globalThis.MarketMembers='+json.dumps(roster,ensure_ascii=False)+';\nif(typeof module!=="undefined"&&module.exports)module.exports=globalThis.MarketMembers;\n',encoding='utf-8')
print(f'Collected {len(roster)}/{len(members)} members; failures: '+json.dumps(errors,ensure_ascii=False))
if errors:raise SystemExit(1)
