
// Terrain decoration is drawn in map space, separate from unchanged merchandise sprites.
function groundFixtures(){
 const aprons=[[26,3,5,2],[23,7,3,2],[29,17,4,2]];
 for(const[x,y,w,h]of aprons){const px=x*32,py=y*32;ctx.fillStyle='rgba(162,155,135,.075)';ctx.fillRect(px+3,py+2,w*32-6,h*32-5);ctx.fillStyle='rgba(25,28,24,.20)';ctx.fillRect(px+4,py+h*32-4,w*32-9,1);for(let a=0;a<w;a++){ctx.fillRect(px+a*32+2,py+5,1,h*32-13);ctx.fillStyle='rgba(170,165,148,.12)';ctx.fillRect(px+a*32+3,py+6,1,h*32-15);ctx.fillStyle='rgba(25,28,24,.20)';}}
 for(const p of fixtures){const meta=MerchCatalog.find(a=>a.id===p.type),px=p.x*32,py=p.y*32;if(meta.kind==='wall')continue;
  const loose=['paper-rubbish','trash-bags','shopping-bags','poster-rolls'].includes(p.type);
  ctx.fillStyle='rgba(21,24,20,.20)';ctx.fillRect(px+5,py+25,24,5);ctx.fillRect(px+8,py+30,17,1);
  ctx.fillStyle='rgba(155,148,127,.16)';for(let n=0;n<9;n++){const xx=3+(n*11+p.x*7)%27,yy=23+(n*7+p.y)%9;ctx.fillRect(px+xx,py+yy,1+(n%3===0?1:0),1);}
  if(!loose){ctx.fillStyle='rgba(15,18,15,.48)';ctx.fillRect(px+7,py+28,19,2);}
 }
}
function fixtureFeet(p){const a=MerchCatalog.find(a=>a.id===p.type);if(a.kind==='wall')return;const c=document.createElement('canvas');c.width=c.height=32;const cc=c.getContext('2d');MarketStock.draw(cc,{type:p.type,x:0,y:0},m,images,32,mix);const d=cc.getImageData(0,0,32,32).data;let bottom=0;for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(d[(y*32+x)*4+3]>128)bottom=Math.max(bottom,y);ctx.fillStyle='rgba(12,15,12,.52)';for(let x=0;x<32;x++)if(d[(bottom*32+x)*4+3]>128)ctx.fillRect(p.x*32+x,p.y*32+bottom+1,1,1);}
function groundStair(c,up,px,py,t){const s=t/32;c.save();
 // Worn mortar extends into the surrounding cement; no enclosing badge or platform.
 c.fillStyle='rgba(26,29,25,.33)';for(const[x,y,w,h]of [[5,25,20,3],[3,23,3,3],[24,21,3,4]])c.fillRect(px+x*s,py+y*s,w*s,h*s);
 c.fillStyle='rgba(146,140,125,.23)';for(const[x,y,w,h]of [[3,27,7,1],[9,29,11,1],[24,24,4,1],[5,6,3,1]])c.fillRect(px+x*s,py+y*s,w*s,h*s);
 c.drawImage(up?images.groundUp:images.groundDown,px,py,t,t);c.restore();}
function drawDetails(){const d=$('details'),c=d.getContext('2d'),old=grounded;c.imageSmoothingEnabled=false;c.fillStyle='#141c17';c.fillRect(0,0,d.width,d.height);const views=[{name:'굿즈 매대',x:26,y:2,w:5,h:5},{name:'올라가는 계단',x:3,y:5,w:5,h:3},{name:'내려가는 계단',x:18,y:23,w:5,h:3}];for(let row=0;row<3;row++){for(let j=0;j<2;j++){grounded=!!j;draw();const x=j*448+58,y=row*232+30;c.drawImage(canvas,views[row].x*32,views[row].y*32,160,96,x,y,320,192);c.fillStyle='#c8d8c9';c.font='14px sans-serif';c.fillText(views[row].name+' · '+(j?'수정 후':'수정 전'),x,y-10);}}grounded=old;draw();}
