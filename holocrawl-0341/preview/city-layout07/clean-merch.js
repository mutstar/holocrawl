(function(root){
'use strict';
const stock=root.MarketStock,reducer=root.PixelReducer,old={make:stock.makeSprites,draw:stock.draw,sprite:stock.getSprite,shirt:stock.getShirt};
let quality='clean';const originals={},bodies={},tees={};
const members=Object.fromEntries(stock.members.map(m=>[m.id,m])),catalog=Object.fromEntries(stock.catalog.map(p=>[p.id,p]));
function memberSprite(id,width,height){
 const key=id+'_'+width+'x'+height;if(bodies[key])return bodies[key];
 const art=reducer.canvas(reducer.quantize(reducer.contrast(reducer.area(originals[id],width-2,height-3)),12,68));
 const c=document.createElement('canvas');c.width=width;c.height=height;const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;
 ctx.drawImage(art,1,0);ctx.fillStyle='#66777c';ctx.fillRect(1,height-2,width-2,2);ctx.fillStyle='#94a6aa';ctx.fillRect(2,height-2,Math.max(1,width-4),1);
 return bodies[key]=c;
}
function shirtSprite(id,width,height){const key=id+'_'+width+'x'+height;if(tees[key])return tees[key];return tees[key]=reducer.canvas(reducer.quantize(reducer.area(reducer.read(old.shirt(id)),width,height),8,96));}
stock.makeSprites=images=>{old.make(images);for(const m of stock.members){originals[m.id]=reducer.read(images['member-'+m.id]);memberSprite(m.id,16,24);}};
stock.draw=(ctx,fixture,map,images,t,mix=0)=>{
 if(quality==='original')return old.draw(ctx,fixture,map,images,t,mix);
 const meta=catalog[fixture.type],x=fixture.x*t,y=fixture.y*t,scale=t/32;ctx.drawImage(images['clean-'+meta.id],x,y,meta.kind==='wall'?2*t:t,t);
 if(!['acrylic','shirts'].includes(meta.content))return;
 const ids=stock.select(map.seed,map.floorNumber,fixture,mix);ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);ctx.imageSmoothingEnabled=false;
 if(meta.content==='acrylic'){
   const positions=meta.kind==='wall'?[[10,8,12,18],[26,8,12,18],[42,8,12,18]]:[[3,6,8,13],[12,6,8,13],[21,6,8,13]];
   ids.forEach((id,i)=>{const[x,y,w,h]=positions[i];ctx.drawImage(memberSprite(id,w,h),x,y);});
 }else if(meta.kind==='wall')ids.forEach((id,i)=>ctx.drawImage(shirtSprite(id,13,13),9+i*16,11));
 else ids.forEach((id,i)=>{ctx.fillStyle=members[id].color;ctx.fillRect(3+i*8,13+i*3,8,4);ctx.drawImage(shirtSprite(id,10,10),3+i*8,8+i*3);});
 ctx.restore();
};
stock.getSprite=id=>quality==='original'?old.sprite(id):memberSprite(id,16,24);
stock.getShirt=id=>quality==='original'?old.shirt(id):shirtSprite(id,16,16);
stock.setQuality=value=>{if(!['clean','original'].includes(value))throw Error('Unknown pixel quality');quality=value;};
stock.getQuality=()=>quality;
})(globalThis);
