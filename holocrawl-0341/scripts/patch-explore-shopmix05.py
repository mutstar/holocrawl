from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01'
p=out/'app.js';s=p.read_text(encoding='utf-8')
if '// Shop mix and shutters05' not in s:
 s=s.replace("type:fixtures[0].type==='acrylic-window'?'acrylic-rack':'shirt-stack'", "type:frontDisplayType(fixtures[0].type,shop)")
 s=s.replace(' const reached=reach(start,blocked);', ' addWallShutters(shop,baseline,sp);\n const reached=reach(start,blocked);')
 s+='''
// Shop mix and shutters05: alternate the front goods, use wall-only shutters, preserve crate locations.
function frontDisplayType(wall,shop){if(wall==='acrylic-window')return 'shirt-stack';const pool=['acrylic-rack','hoodie-rack','keychain-hooks','badge-trays','plush-basket'];return pool[hash(m.seed+':front05:'+placementSeed,shop.x,shop.y)%pool.length];}
function addWallShutters(shop,reachable,sp){const candidates=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-3;x++)if(isWall(feature(m,x,y))&&isWall(feature(m,x+1,y))&&feature(m,x,y+1)==='floor'&&feature(m,x+1,y+1)==='floor'&&(reachable.has(x+','+(y+1))||reachable.has((x+1)+','+(y+1)))&&sp.every(p=>Math.max(Math.abs(p.x-x),Math.abs(p.y-y))>2))candidates.push({x,y});const random=rng(m.seed+':shutters05:'+placementSeed),pool=shuffled(candidates,random);if(shop)pool.sort((a,b)=>{const score=p=>(p.y===shop.y&&Math.abs(p.x-shop.x)<=10?-100:0)+Math.hypot(p.x-shop.x,p.y-shop.y);return score(a)-score(b);});for(const type of ['closed-shutter','half-shutter']){const p=pool.find(p=>!fixtures.some(f=>MerchCatalog.find(a=>a.id===f.type).kind==='wall'&&f.y===p.y&&p.x<f.x+3&&p.x+3>f.x));if(p)fixtures.push({type,...p});}}
// Scale only the existing crate drawing: remove empty margins and fill its one-cell footprint.
if(!MarketStock._cityBoxLarge05){const originalStockDraw=MarketStock.draw;MarketStock.draw=(c,p,map,images,t,mix=0)=>{if(p.type==='delivery-boxes'){c.save();c.imageSmoothingEnabled=false;c.drawImage(images['clean-delivery-boxes'],3,6,26,26,p.x*t,p.y*t,t,t);c.restore();return;}return originalStockDraw(c,p,map,images,t,mix);};MarketStock._cityBoxLarge05=true;}
'''
 p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('app.js?v=fresh04','app.js?v=shopmix05');p.write_text(s,encoding='utf-8')
print('Cross-category front displays, two wall shutters, crates 26px→32px installed.')
