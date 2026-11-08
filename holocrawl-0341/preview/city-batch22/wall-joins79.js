// One shared surface rule for thick walls, one-cell branches and isolated pillars.
// The cap is the wall footprint shifted four pixels left and fourteen pixels up.
// Looking across a tile edge therefore never switches to a different wall family.
function cityWallSurface79(solid, x, y, px, py) {
 const dx=px>=28?1:0,dy=py>=18?1:0;
 if(solid(x+dx,y+dy))return 'cap';
 return dx&&!solid(x+1,y)||dx&&dy&&solid(x,y+1)?'side':'front';
}
const joinedCityWallSprites79=new Map();
function joinedCityWallSprite79(map,x,y){
 const solid=(xx,yy)=>isWall(feature(map,xx,yy))||isDoor(feature(map,xx,yy));
 const n=solid(x,y-1),e=solid(x+1,y),s=solid(x,y+1),w=solid(x-1,y),se=solid(x+1,y+1);
 const sx=hash(map.seed,x,y)%8*32,key=[sx,+n,+e,+s,+w,+se].join(':');
 if(joinedCityWallSprites79.has(key))return joinedCityWallSprites79.get(key);
 const sprite=document.createElement('canvas');sprite.width=sprite.height=32;
 const c=sprite.getContext('2d');c.drawImage(images.wall,sx,0,32,32,0,0,32,32);
 const pixels=c.getImageData(0,0,32,32),d=pixels.data,cap=[35,37,33];
 for(let py=0;py<32;py++)for(let px=0;px<32;px++){
  const i=(py*32+px)*4,surface=cityWallSurface79(solid,x,y,px,py);
  for(let k=0;k<3;k++){
   if(surface==='cap')d[i+k]=Math.round(cap[k]*.86+d[i+k]*.14);
   else if(surface==='side')d[i+k]=Math.round(d[i+k]*.56);
  }
  // Shade only exposed outer boundaries, never a seam between joined cells.
  let shade=1;
  if(!n&&py===0)shade*=.80;
  if(!w&&px===0)shade*=.80;
  if(!e&&px===31)shade*=.78;
  if(!s&&py===31)shade*=.72;
  for(let k=0;k<3;k++)d[i+k]=Math.round(d[i+k]*shade);
  d[i+3]=255;
 }
 c.putImageData(pixels,0,0);joinedCityWallSprites79.set(key,sprite);return sprite;
}
const cityTileBeforeJoins79=tile;
tile=function(c,map,x,y,px,py,t,style='fit',forceState=null,oldWall=wallOld){
 const f=feature(map,x,y);
 if(style==='fit'&&!oldWall&&isWall(f)&&!f.includes('clear_')&&f!=='crystal_wall'){
  c.save();c.imageSmoothingEnabled=false;c.drawImage(joinedCityWallSprite79(map,x,y),px,py,t,t);c.restore();return;
 }
 return cityTileBeforeJoins79(c,map,x,y,px,py,t,style,forceState,oldWall);
};
