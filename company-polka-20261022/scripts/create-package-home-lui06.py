from pathlib import Path
r=Path(__file__).resolve().parents[1]
t=(r/'scripts/package-company-polka01.py').read_text(encoding='utf-8-sig')
start=t.index('r=Path(__file__)');end=t.index("assert not archive.exists()")
t=t[:start]+"r=Path(__file__).resolve().parents[1];name='HOLOCRAWL_HOME_2026-10-22_LUI_ATTACK06';(r/'exports').mkdir(exist_ok=True);stage=r/'exports'/name;archive=Path.home()/'Desktop'/(name+'.zip');proofdir=r/'analysis/native/home-lui-handoff06';stage.mkdir();proofdir.mkdir()\ncompany_readme=(r/'START_HERE_HOME.md').read_text(encoding='utf-8')\n"+t[end:]
t=t.replace("analysis/native/lamy-banquet-vfx05/checkpoint-manifest.json","analysis/native/lui-attack06/checkpoint-manifest.json")
start=t.index("polka=read(r/'analysis/native/polka-review01/validation.json')");end=t.index('# Resolve every',start)
t=t[:start]+t[end:]
t=t.replace("def evidence_ok(p):", "selected.update('polka-vfx05 polka-leap02 polka-vfx07 koyori-tube02 koyori-tier3-border01 koyori-five-critical04 lui-ganmo-sharp01 lui-attack06'.split())\n\ndef evidence_ok(p):")
t=t.replace("print('Stage copied. Running relocated game", "for launch in ['OPEN_VFX_REVIEW.cmd','OPEN_GALLERY.cmd']:copy(r/launch,launch)\nprint('Stage copied. Running relocated game")
t=t.replace("currentGod='polka'", "currentGod='lui'")
start=t.index('# The Polka review and all referenced choices');end=t.index('files=sorted(',start)
t=t[:start]+"assert read(stage/'VFX_DRAFT_STATUS.json')['tierApprovals']['koyori']['approved']==[1,3,5]\nassert read(stage/'analysis/native/lui-attack06/checkpoint-manifest.json')['status']=='passed'\nassert (stage/'analysis/previews/lui-attack06/attack.gif').is_file()\nassert sha(stage/'runtime/tiles01/HoloCrawl.exe')==sha(r/'runtime/tiles01/HoloCrawl.exe')\n"+t[end:]
t=t.replace("version='company-polka-review01'", "version='home-lui-attack06'").replace("entry='START_HERE_COMPANY.md'", "entry='START_HERE_HOME.md'").replace("review='analysis/previews/all-gods-vfx-draft04/index.html'", "review='analysis/previews/lui-review01/index.html'").replace("next='Polka tiers1/3/5 feedback pending; Lamy fully approved'", "next='Review Lui two-talon native attack GIF; then tier3 after approval. 15 gods approved.'")
# Check actual src/href references in the active relocated page too.
anchor="write(stage/'PREVIEW_LINK_VALIDATION.json'"
pos=t.index(anchor)
t=t[:pos]+"active=stage/'analysis/previews/lui-review01/index.html';active_html=active.read_text(encoding='utf-8');local_refs=re.findall(r'(?:src|href)=\"([^\"]+)\"',active_html);assert all((active.parent/ref.split('#')[0]).is_file() for ref in local_refs if ref and not ref.startswith(('http:', 'https:', '#')));\n"+t[pos:]
(r/'scripts/package-home-lui06.py').write_text(t,encoding='utf-8')
print('Latest portable package script prepared.')
