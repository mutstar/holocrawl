// Preserve the 18/14 cap/front height. A diagonal wall must not create a
// four-pixel cap tongue across an exposed front or truncate a visible side.
function cityWallSurface84(solid,x,y,px,py){
 const n=solid(x,y-1),e=solid(x+1,y),s=solid(x,y+1);
 if(py>=18&&!s)return px>=28&&!e?'side':'front';
 if(px>=28&&(!e||py>=18&&!solid(x+1,y+1)))return 'side';
 // Continue the small west-facing reveal through the inside of an L turn.
 // SW is tested at the lower part, where the cap meets the next wall row.
 if(px<3&&(n||s)&&!solid(x-1,y+(py>=18?1:0)))return 'west';
 return 'cap';
}
const cornerWallSprites84=new Map();
joinedCityWallSprite79=function(map,x,y){
 const solid=(xx,yy)=>isWall(feature(map,xx,yy))||isDoor(feature(map,xx,yy));
 const n=solid(x,y-1),e=solid(x+1,y),s=solid(x,y+1),w=solid(x-1,y);
 const sx=hash(map.seed,x,y)%8*32;
 const key=[sx,+n,+e,+s,+w,+solid(x+1,y+1),+solid(x-1,y+1)].join(':');
 if(cornerWallSprites84.has(key))return cornerWallSprites84.get(key);
 const sprite=document.createElement('canvas');sprite.width=sprite.height=32;
 const c=sprite.getContext('2d');c.drawImage(images.wall,sx,0,32,32,0,0,32,32);
 const pixels=c.getImageData(0,0,32,32),d=pixels.data,cap=[35,37,33];
 for(let py=0;py<32;py++)for(let px=0;px<32;px++){
  const i=(py*32+px)*4,surface=cityWallSurface84(solid,x,y,px,py);
  for(let k=0;k<3;k++){
   if(surface==='cap')d[i+k]=Math.round(cap[k]*.86+d[i+k]*.14);
   else if(surface==='side')d[i+k]=Math.round(d[i+k]*.56);
   else if(surface==='west')d[i+k]=Math.round(d[i+k]*.72);
  }
  let shade=1;
  if(!n&&py===0)shade*=.80;if(!w&&px===0)shade*=.80;
  if(!e&&px===31)shade*=.78;if(!s&&py===31)shade*=.72;
  for(let k=0;k<3;k++)d[i+k]=Math.round(d[i+k]*shade);
  d[i+3]=255;
 }
 c.putImageData(pixels,0,0);cornerWallSprites84.set(key,sprite);return sprite;
};
