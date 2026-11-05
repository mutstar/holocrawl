
// Terrain decoration is drawn in map space, separate from unchanged merchandise sprites.
function previousGroundFixtures(){
 const aprons=[[26,3,5,2],[23,7,3,2],[29,17,4,2]];
 for(const[x,y,w,h]of aprons){const px=x*32,py=y*32;ctx.fillStyle='rgba(162,155,135,.075)';ctx.fillRect(px+3,py+2,w*32-6,h*32-5);ctx.fillStyle='rgba(25,28,24,.20)';ctx.fillRect(px+4,py+h*32-4,w*32-9,1);for(let a=0;a<w;a++){ctx.fillRect(px+a*32+2,py+5,1,h*32-13);ctx.fillStyle='rgba(170,165,148,.12)';ctx.fillRect(px+a*32+3,py+6,1,h*32-15);ctx.fillStyle='rgba(25,28,24,.20)';}}
 for(const p of fixtures){const meta=MerchCatalog.find(a=>a.id===p.type),px=p.x*32,py=p.y*32;if(meta.kind==='wall')continue;
  const loose=['paper-rubbish','trash-bags','shopping-bags','poster-rolls'].includes(p.type);
  ctx.fillStyle='rgba(21,24,20,.20)';ctx.fillRect(px+5,py+25,24,5);ctx.fillRect(px+8,py+30,17,1);
  ctx.fillStyle='rgba(155,148,127,.16)';for(let n=0;n<9;n++){const xx=3+(n*11+p.x*7)%27,yy=23+(n*7+p.y)%9;ctx.fillRect(px+xx,py+yy,1+(n%3===0?1:0),1);}
  if(!loose){ctx.fillStyle='rgba(15,18,15,.48)';ctx.fillRect(px+7,py+28,19,2);}
 }
}
function previousFixtureFeet(p){const a=MerchCatalog.find(a=>a.id===p.type);if(a.kind==='wall')return;const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');MarketStock.draw(cc,{type:p.type,x:0,y:0},m,images,32,mix);const d=cc.getImageData(0,0,32,32).data;let bottom=0;for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(d[(y*32+x)*4+3]>128)bottom=Math.max(bottom,y);ctx.fillStyle='rgba(12,15,12,.52)';for(let x=0;x<32;x++)if(d[(bottom*32+x)*4+3]>128)ctx.fillRect(p.x*32+x,p.y*32+bottom+1,1,1);}
function previousGroundStair(c,up,px,py,t){const s=t/32;c.save();
 // Worn mortar extends into the surrounding cement; no enclosing badge or platform.
 c.fillStyle='rgba(26,29,25,.33)';for(const[x,y,w,h]of [[5,25,20,3],[3,23,3,3],[24,21,3,4]])c.fillRect(px+x*s,py+y*s,w*s,h*s);
 c.fillStyle='rgba(146,140,125,.23)';for(const[x,y,w,h]of [[3,27,7,1],[9,29,11,1],[24,24,4,1],[5,6,3,1]])c.fillRect(px+x*s,py+y*s,w*s,h*s);
 c.drawImage(up?images.groundUp:images.groundDown,px,py,t,t);c.restore();}

const footCache=new Map();
function propMask(p){const key=p.type+':'+mix;if(footCache.has(key))return footCache.get(key);const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');cc.imageSmoothingEnabled=false;MarketStock.draw(cc,{type:p.type,x:0,y:0},m,images,32,mix);const data=cc.getImageData(0,0,32,32).data;let bottom=0;for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(data[(y*32+x)*4+3]>128)bottom=Math.max(bottom,y);let left=32,right=0;for(let y=Math.max(0,bottom-5);y<=bottom;y++)for(let x=0;x<32;x++)if(data[(y*32+x)*4+3]>128){left=Math.min(left,x);right=Math.max(right,x);}const mask=document.createElement('canvas');mask.width=mask.height=32;const mc=mask.getContext('2d');mc.drawImage(c,0,0);mc.globalCompositeOperation='source-in';mc.fillStyle='#090e0b';mc.fillRect(0,0,32,32);const result={c,mask,bottom,left,right};footCache.set(key,result);return result;}
function groundFixtures(){for(const p of fixtures){const meta=MerchCatalog.find(a=>a.id===p.type);if(meta.kind==='wall')continue;const{x,y}=p,px=x*32,py=y*32,b=propMask(p),rubbish=['paper-rubbish','trash-bags','poster-rolls'].includes(p.type),height=rubbish?3:7;
 // A short cast shadow meets the exact foot level; no detached ellipse or floor rectangle.
 ctx.save();ctx.globalAlpha=rubbish?.35:.58;ctx.drawImage(b.mask,px+3,py+b.bottom-height+3,32,height);ctx.restore();
 ctx.fillStyle='rgba(7,12,8,.76)';ctx.fillRect(px+b.left,py+b.bottom,Math.max(1,b.right-b.left+1),2);
 ctx.fillStyle='rgba(12,18,13,.38)';ctx.fillRect(px+b.left+2,py+b.bottom+2,Math.max(1,b.right-b.left),1);
}}
function fixtureFeet(p){const meta=MerchCatalog.find(a=>a.id===p.type);if(meta.kind==='wall')return;const b=propMask(p);ctx.fillStyle='rgba(9,13,10,.68)';ctx.fillRect(p.x*32+b.left,p.y*32+b.bottom+1,b.right-b.left+1,1);}
const stairMasks={};
function groundStair(c,up,px,py,t){const s=t/32,im=up?images.groundUp:images.groundDown;c.save();c.imageSmoothingEnabled=false;if(up){if(!stairMasks.up){const mask=document.createElement('canvas');mask.width=mask.height=32;const cc=mask.getContext('2d');cc.drawImage(im,0,0);cc.globalCompositeOperation='source-in';cc.fillStyle='#080e0a';cc.fillRect(0,0,32,32);stairMasks.up=mask;}c.globalAlpha=.63;c.drawImage(stairMasks.up,px+4*s,py+23*s,t,10*s);c.globalAlpha=1;c.globalAlpha=.8;c.drawImage(stairMasks.up,0,24,32,8,px,py+25*s,t,8*s);c.globalAlpha=1;}c.drawImage(im,px,py,t,t);if(!up){c.strokeStyle='rgba(5,9,7,.80)';c.lineWidth=2*s;c.beginPath();c.arc(px+16*s,py+16*s,12*s,Math.PI*1.03,Math.PI*1.88);c.stroke();c.fillStyle='rgba(126,124,110,.22)';c.fillRect(px+9*s,py+29*s,8*s,s);}c.restore();}
