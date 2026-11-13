function createFestivalWoodArch({canvas,g,texture,profile}){
 const {w,h,canvasW,xOffset}=profile.frame;
 const rim=2,jamb=1;
 function makeSprite(open){
  const c=canvas(w,h),q=g(c);
  for(let x=0;x<w;x++){
   const top=profile.archTop(x),edge=top+rim;
   q.fillStyle='#987452';q.fillRect(x,top,1,1);
   q.fillStyle='#745136';q.fillRect(x,top+1,1,1);
   if(x<jamb||x>=w-jamb){
    q.fillStyle='#76573d';
    q.fillRect(x,edge,1,h-edge);
   }
  }
  q.save();q.beginPath();
  for(let x=jamb;x<w-jamb;x++){
   const y=profile.archTop(x)+rim;
   q.rect(x,y,1,h-y);
  }
  q.clip();
  if(open){
   // Folded leaves hug the jambs. The center and threshold show the real floor.
   for(const x of [jamb,w-jamb-2]){
    q.fillStyle='#4c3224';q.fillRect(x,0,2,h);
    q.fillStyle='#8a6242';q.fillRect(x===jamb?x:x+1,0,1,h-1);
   }
  }else{
   // Use just the planks and handles. The old rectangular lintel and sill
   // would read as a smaller door sitting inside the arch.
   q.drawImage(texture,4,8,24,22,jamb,rim,w-2*jamb,h-rim);
  }
  q.restore();
  return c;
 }
 const sprites=[makeSprite(false),makeSprite(true)];
 return function drawWoodArch(q,map,door,open,base){
  const offset=profile.direction(map,door)==='horizontal'?(canvasW-w)/2:xOffset;
  profile.drawWallReturns(q,map,door,base,offset);
  q.drawImage(sprites[Number(open)],door.x*canvasW+offset,door.y*h);
 };
}
