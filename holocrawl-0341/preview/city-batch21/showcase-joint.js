// Short masonry jambs connect a recessed wall showcase to the adjacent wall face.
let showcaseJointEnabled=true;
const drawBeforeShowcaseJoint19=MarketStock.draw;
MarketStock.draw=function(c,p,map,images,t,mix=0){
 const result=drawBeforeShowcaseJoint19(c,p,map,images,t,mix);
 if(!showcaseJointEnabled||!['acrylic-window','shirt-window'].includes(p.type))return result;
 const s=t/32;
 for(const side of [-1,1]){
  const x=side===1?p.x+2:p.x-1,y=p.y,f=feature(map,x,y);
  if(!isWall(f)||f.includes('clear_')||isWall(feature(map,x,y+1)))continue;
  const run=wallRun(map,x,y),sx=((x-run.start+run.phase)%8)*32,offset=side===1?0:29;
  c.save();c.imageSmoothingEnabled=false;
  // A narrow shaded reveal, without a bright pillar beside the dark wall cap.
  c.drawImage(images.wall,sx+offset,0,3,32,(x*32+offset)*s,y*t,3*s,t);
  c.fillStyle='rgba(9,15,11,.32)';c.fillRect((x*32+offset)*s,y*t,3*s,t);
  c.fillStyle='rgba(14,18,14,.50)';c.fillRect((side===1?x*32:x*32+31)*s,y*t+s,s,30*s);
  c.fillStyle='#252923';c.fillRect((x*32+offset)*s,y*t+31*s,3*s,s);
  c.restore();
 }
 return result;
};
