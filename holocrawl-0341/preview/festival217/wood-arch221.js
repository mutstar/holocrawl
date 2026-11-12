function createFestivalWoodArch({canvas,g,texture,profile}){
 const {w,h}=profile.frame;
 const rim=2,jamb=1;
 function makeSprite(open, width){
  const c=canvas(width,h),q=g(c);
  const archTop=x=>profile.archTop(Math.round(x*(w-1)/(width-1)));
  for(let x=0;x<width;x++){
   const top=archTop(x),edge=top+rim;
   q.fillStyle='#987452';q.fillRect(x,top,1,1);
   q.fillStyle='#745136';q.fillRect(x,top+1,1,1);
   if(x<jamb||x>=width-jamb){
    q.fillStyle='#76573d';
    q.fillRect(x,edge,1,h-edge);
   }
  }
  q.save();q.beginPath();
  for(let x=jamb;x<width-jamb;x++){
   const y=archTop(x)+rim;
   q.rect(x,y,1,h-y);
  }
  q.clip();
  if(open){
   // Folded leaves hug the jambs. The center and threshold show the real floor.
   for(const x of [jamb,width-jamb-2]){
    q.fillStyle='#4c3224';q.fillRect(x,0,2,h);
    q.fillStyle='#8a6242';q.fillRect(x===jamb?x:x+1,0,1,h-1);
   }
  }else{
   // Use just the planks and handles. The old rectangular lintel and sill
   // would read as a smaller door sitting inside the arch.
   q.drawImage(texture,4,8,24,22,jamb,rim,width-2*jamb,h-rim);
  }
  q.restore();
  return c;
 }
 const acrossPassage=[makeSprite(false,32),makeSprite(true,32)];
 const alongPassage=[makeSprite(false,w),makeSprite(true,w)];
 return function drawWoodArch(q,map,door,open,base){
  const x=door.x*32,y=door.y*32;
  if(profile.direction(map,door)==='horizontal'){
   // The posts span the passage. Adjacent wall coping ends at its own tile.
   q.drawImage(acrossPassage[Number(open)],x,y);
   return;
  }
  for(let px=0;px<w;px++){
   const top=profile.archTop(px);
   if(!top)continue;
   const dx=x+profile.frame.xOffset+px;
   q.drawImage(base,dx,y-1,1,1,dx,y,1,top);
  }
  for(let dx=0;dx<32-w;dx++){
   q.fillStyle=`rgba(24,17,13,${.25-dx*.05})`;
   q.fillRect(x+w+dx,y+profile.frame.archRise,1,h-profile.frame.archRise);
  }
  q.drawImage(alongPassage[Number(open)],x+profile.frame.xOffset,y);
 };
}
