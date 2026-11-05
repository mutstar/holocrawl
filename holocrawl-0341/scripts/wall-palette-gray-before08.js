// Rendering-only candidate: original terrain and collision cells remain unchanged.
let wallVolumeEnabled=true;
function thinWallShape(map,x,y){
 const solid=(x,y)=>isWall(feature(map,x,y))||isDoor(feature(map,x,y));
 const n=solid(x,y-1),e=solid(x+1,y),s=solid(x,y+1),w=solid(x-1,y);
 return{n,e,s,w,se:solid(x+1,y+1),thin:(!n&&!s)||(!e&&!w)};
}
const originalCityTile=tile;
const concreteWallTextures=new Map();
function concreteWallTexture(sx,tone){
 const key=sx+':'+tone;if(concreteWallTextures.has(key))return concreteWallTextures.get(key);
 const canvas=document.createElement('canvas');canvas.width=canvas.height=32;const c=canvas.getContext('2d');
 c.drawImage(images.wall,sx,0,32,32,0,0,32,32);const pixels=c.getImageData(0,0,32,32),d=pixels.data;
 for(let i=0;i<d.length;i+=4){const l=d[i]*.299+d[i+1]*.587+d[i+2]*.114,v=Math.max(tone-18,Math.min(tone+16,tone+(l-58)*.48));d[i]=v;d[i+1]=v+1;d[i+2]=v;}
 c.putImageData(pixels,0,0);concreteWallTextures.set(key,canvas);return canvas;
}
function drawThinWall(c,map,x,y,px,py,t,shape){
 const q=t/32,sx=hash(map.seed,x,y)%8*32;
 c.save();c.imageSmoothingEnabled=false;
 // Desaturated concrete on every face; retain the existing low-resolution grain.
 const textureRect=(xx,yy,ww,hh,tone)=>{c.drawImage(concreteWallTexture(sx,tone),xx,yy,ww,hh,px+xx*q,py+yy*q,ww*q,hh*q);};
 const line=(color,x,y,w,h)=>{c.fillStyle=color;c.fillRect(px+x*q,py+y*q,w*q,h*q)};
 if(!shape.n&&!shape.s){
  textureRect(0,0,32,16,91);
  textureRect(0,16,32,15,62);
  line('#424641',0,0,32,1);line('#454943',0,16,32,1);line('#242924',0,30,32,2);
  // Short irregular edge flecks replace the uninterrupted bright metal-like trim.
  const h=hash(map.seed,x+103,y);for(let n=0;n<3;n++){const xx=(h+n*11)%30;line(n===1?'#767a73':'#4c5149',xx,14+(n%2),2,1);}
  if(!shape.w){textureRect(0,16,3,14,48);line('#292e29',0,1,1,29);line('#575d54',1,2,1,12);line('#3b4138',1,1,2,1);}
  if(!shape.e){textureRect(27,16,4,14,43);line('#242a24',31,1,1,30);line('#464c43',27,16,1,14);line('#41473e',29,1,2,1);}
 }else{
  // A narrow north/south wall has a continuous top and a visible side face.
  textureRect(0,0,25,32,91);textureRect(25,0,7,32,43);
  line('#424841',0,0,1,32);line('#555b52',24,0,1,32);line('#242a24',31,0,1,32);
  const h=hash(map.seed,x,y+103);line('#6e746a',22,h%28,2,2);line('#50574d',23,(h+11)%29,2,1);
  if(!shape.n){line('#363d34',0,0,32,1);}
  if(!shape.s){textureRect(0,17,25,14,62);line('#242a24',0,31,32,1);}
 }
 c.restore();
}

// One four-neighbour tile family for pillars, ends, corners, junctions and solid masses.
// Joined edges are open: outlines are drawn only on exposed perimeter edges.
const connectedWallSprites=new Map();
function wallWearVariant(map,x,y){const h=hash(map.seed,x+2081,y+701);return h%10<6?0:1+Math.floor(h/10)%7;}
function stampConcreteWear(d,variant,seed){
 if(!variant)return;
 const random=rng('concrete-wear06:'+seed+':'+variant),strength=new Map();
 const put=(x,y,amount)=>{x=Math.round(x);y=Math.round(y);if(x<2||x>29||y<2||y>29)return;const pos=y*32+x;strength.set(pos,Math.max(strength.get(pos)||0,amount));};
 if(variant<=4){
  // Each fissure grows along a seeded direction with gradual bends; no repeated symbols.
  const angle=[0,1.25,.75,-.32,1.65][variant]+(random()-.5)*.5,startX=6+random()*12,startY=5+random()*9,length=13+Math.floor(random()*12);
  const trace=(x,y,angle,length,depth)=>{let bend=0;for(let n=0;n<length;n++){bend=bend*.75+(random()-.5)*.2;angle+=bend;x+=Math.cos(angle)*.7;y+=Math.sin(angle)*.7;const fade=Math.sin(Math.PI*(n+1)/(length+1)),amount=(7+random()*6)*fade;put(x,y,amount);put(x+1,y,amount*.18);if(depth&&n===Math.floor(length*.55))trace(x,y,angle-.65-random()*.4,6+Math.floor(random()*5),0);}};
  trace(startX,startY,angle,length,variant===2?1:0);
 }else{
  // Broken granular patches and pitting, without an outlined ring or a uniform rim.
  const cx=9+random()*12,cy=8+random()*14,rx=variant===5?7:4,ry=variant===5?4:6;
  for(let y=3;y<29;y++)for(let x=3;x<29;x++){const radius=((x-cx)/rx)**2+((y-cy)/ry)**2;if(radius<1&&random()<(1-radius)*.65)put(x,y,(variant===7?5:8)*(1-radius)+random()*4);}
 }
 for(const[pos,drop]of strength){const i=pos*4;for(let k=0;k<3;k++)d[i+k]=Math.max(30,Math.round(d[i+k]-drop));}
}
function connectedWallSprite(map,x,y,shape,forcedVariant=null){
 const variant=forcedVariant??wallWearVariant(map,x,y),h=hash(map.seed,x+77,y+307);
 const sx=hash(map.seed,x,y)%8*32,key=[sx,+shape.n,+shape.e,+shape.s,+shape.w,+shape.se,variant,variant?h:0].join(':');
 if(connectedWallSprites.has(key))return connectedWallSprites.get(key);
 const sprite=document.createElement('canvas');sprite.width=sprite.height=32;const c=sprite.getContext('2d');
 const top=concreteWallTexture(sx,91).getContext('2d').getImageData(0,0,32,32).data,pixels=c.createImageData(32,32),d=pixels.data;
 for(let py=0;py<32;py++)for(let px=0;px<32;px++){
  // Sample the entire 4x16 bevel footprint, including the diagonal cell.
  // The diagonal test turns the inner corner with the wall instead of leaving a ledge.
  const east=px<28||shape.e,south=py<16||shape.s,diagonal=px<28?(py<16||shape.s):py<16?shape.e:shape.se;
  const side=!east||(south&&!diagonal),front=!south;
  let tone=side?70:front?62:91;
  if(side&&px===31&&!shape.e)tone=55;
  if(front&&py===31&&!shape.s)tone=48;
  if(!side&&!front&&(!shape.n&&py===0||!shape.w&&px===0))tone-=9;
  const i=(py*32+px)*4,grain=top[i]-91;d[i]=tone+grain;d[i+1]=tone+grain+1;d[i+2]=tone+grain;d[i+3]=255;
 }
 stampConcreteWear(d,variant,h);
 c.putImageData(pixels,0,0);connectedWallSprites.set(key,sprite);return sprite;
}
function connectedConcreteWall(c,map,x,y,px,py,t,shape,decorate=true){
 const q=t/32;
 c.save();c.imageSmoothingEnabled=false;
 c.drawImage(connectedWallSprite(map,x,y,shape),px,py,t,t);
 // Keep approved wall equipment on walls backed by a larger wall mass.
 if(decorate&&!shape.s&&shape.n){
  const run=wallRun(map,x,y),plan=wallPipeSpan09(map,x,y);
  if(plan&&Array.from({length:plan.length},(_,i)=>thinWallShape(map,plan.start+i,y).n).every(Boolean))drawHorizontalPipe09(c,map,x,y,px,py,t);
  if(x===run.decor&&!isDoor(feature(map,x-1,y))&&!isDoor(feature(map,x+1,y))&&!fixtures.some(p=>MerchCatalog.find(a=>a.id===p.type).kind==='wall'&&p.y===y&&x>=p.x&&x<p.x+2)){
   const kind=hash(map.seed,x+431,y)%4;
   if(kind===0)texture(c,[289,34,37,19],px+2*q,py+9*q,27*q,14*q);
   if(kind===2)texture(c,[294,86,22,16],px+5*q,py+8*q,22*q,16*q);
   if(kind===3)c.drawImage(images.wallCabinet08,px,py,t,t);
  }
 }
 c.restore();
}
const originalCityWallFace=wallFace,originalCityWallSides=wallSides;
wallFace=function(c,map,x,y,px,py,t,old=false){
 if(wallVolumeEnabled&&!old){connectedConcreteWall(c,map,x,y,px,py,t,thinWallShape(map,x,y));return;}
 return originalCityWallFace(c,map,x,y,px,py,t,old);
};
wallSides=function(c,map,x,y,px,py,t){
 if(!wallVolumeEnabled)return originalCityWallSides(c,map,x,y,px,py,t);
 const q=t/32,sx=hash(map.seed,x,y)%8*32;c.save();c.imageSmoothingEnabled=false;
 for(const[dx,offset,tone]of[[-1,0,62],[1,29,70]])if(!isWall(feature(map,x+dx,y)))c.drawImage(concreteWallTexture(sx,tone),offset,0,3,32,px+offset*q,py,3*q,t);
 c.restore();
};
tile=function(c,map,x,y,px,py,t,style='fit',forceState=null,oldWall=wallOld){
 const f=feature(map,x,y),shape=thinWallShape(map,x,y);
 if(wallVolumeEnabled&&style==='fit'&&!oldWall&&isWall(f)&&!f.includes('clear_')&&f!=='crystal_wall'){connectedConcreteWall(c,map,x,y,px,py,t,shape);return;}
 return originalCityTile(c,map,x,y,px,py,t,style,forceState,oldWall);
};
