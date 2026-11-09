from pathlib import Path
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];src=r/'engine/campaign-crawl/crawl-ref/source';run=r/'analysis/native/lamy-hud01';run.mkdir();(run/'before').mkdir()
changed=['status.h','status.cc','holo-campaign.cc','holo-campaign-test.cc']
for n in changed:shutil.copy2(src/n,run/'before'/n)
preserved={str(p.relative_to(src)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(src.glob('*.cc'))+list(src.glob('*.h'))+list((src/'rltiles/holo').glob('*.png')) if p.name not in changed};(run/'preserved-files.json').write_text(json.dumps(preserved,indent=2),encoding='utf-8')
p=src/'status.h';s=p.read_text(encoding='utf-8').replace('STATUS_LAST_STATUS = STATUS_HEAVENLY_STORM','STATUS_HOLO_LAMY,\n    STATUS_LAST_STATUS = STATUS_HOLO_LAMY');p.write_text(s,encoding='utf-8')
p=src/'status.cc';s=p.read_text(encoding='utf-8').replace('#include "status.h"','#include "status.h"\n#include "holo-campaign.h"\n#include "holo-worship.h"\n#include "holo-batch-internal.h"')
needle='    switch (status)\n    {';assert needle in s
s=s.replace(needle,needle+'''
    case STATUS_HOLO_LAMY:
    {
        if (!holo_campaign::active() || holo_worship::current()!="lamy")
            return false;
        const auto &ls=holo_batch::s;
        const int amount=max(0,min(100,ls.resource));
        const int remaining=max(0,(ls.five_end-you.elapsed_time+9)/10);
        // Current combat thresholds: new caster design remains a proposal.
        const char *stage=remaining>0?"Banquet":amount>60?"Drunk":amount>=20?"Tipsy":"Sober";
        inf.light_colour=remaining>0?LIGHTMAGENTA:amount>60?LIGHTRED:amount>=20?LIGHTCYAN:LIGHTGREY;
        inf.light_text=remaining>0?make_stringf("Banquet %dt",remaining):make_stringf("%s %d/100",stage,amount);
        inf.short_text=make_stringf("Lamy: %s, intoxication %d/100",stage,amount);
        inf.long_text=remaining>0?make_stringf("Snow banquet: %d turns remaining; intoxication %d/100.",remaining,amount):make_stringf("Lamy intoxication: %d/100 (%s).",amount,stage);
        return true;
    }
''',1);p.write_text(s,encoding='utf-8')
p=src/'holo-campaign.cc';s=p.read_text(encoding='utf-8').replace('refresh();deliver_supplies();int next=', 'refresh();deliver_supplies();if(holo_worship::current()=="lamy")you.redraw_status_lights=true;int next=');p.write_text(s,encoding='utf-8')
p=src/'holo-campaign-test.cc';s=p.read_text(encoding='utf-8').replace('#include "status.h"','')
s=s.replace('#include "AppHdr.h"','#include "AppHdr.h"\n#include "status.h"')
needle='    if(const char *shots=getenv("HOLOCRAWL_TOWA_CROSSFIRE_REVIEW")) {';assert needle in s
block=r'''    if(const char *shots=getenv("HOLOCRAWL_LAMY_HUD_REVIEW")) {
        fixture("lamy");const int amounts[]={12,40,80,0};const char *names[]={"sober","tipsy","drunk","banquet"};
        const char *labels[]={"Sober 12/100","Tipsy 40/100","Drunk 80/100","Banquet 6t"};
        const int colours[]={LIGHTGREY,LIGHTCYAN,LIGHTRED,LIGHTMAGENTA};
        for(int i=0;i<4;++i) {
            holo_batch::s.resource=amounts[i];holo_batch::s.five_end=i==3?you.elapsed_time+60:0;
            status_info info;require(fill_status_info(STATUS_HOLO_LAMY,info) && info.light_text==labels[i] && info.light_colour==colours[i],"Lamy HUD label/colour");
            const auto before=signature();holo_visual::capture(std::string(shots)+"/lamy-"+names[i]+".png");require(before==signature(),"Lamy HUD rendering mutated gameplay");
        }
        you.elapsed_time+=10;status_info info;require(fill_status_info(STATUS_HOLO_LAMY,info) && info.light_text=="Banquet 5t","Lamy HUD live countdown");
        fixture("towa");require(!fill_status_info(STATUS_HOLO_LAMY,info),"Lamy status leaked to another god");
        std::ofstream(dir+"/lamy-hud.json")<<"{\"status\":\"passed\",\"states\":4,\"countdown\":true,\"otherGodHidden\":true,\"renderingStateUnchanged\":true,\"combatRedesignApplied\":false}\n";
    }
'''
s=s.replace(needle,block+needle,1);p.write_text(s,encoding='utf-8')
s=(r/'scripts/capture-towa-crossfire02.ps1').read_text(encoding='utf-8').replace('towa-crossfire02','lamy-hud01').replace('$env:HOLOCRAWL_TOWA_SHOT_REVIEW=$shots;$env:HOLOCRAWL_TOWA_CROSSFIRE_REVIEW=$shots;','$env:HOLOCRAWL_LAMY_HUD_REVIEW=$shots;').replace(',Env:HOLOCRAWL_TOWA_SHOT_REVIEW','');(r/'scripts/capture-lamy-hud01.ps1').write_text(s,encoding='utf-8')
