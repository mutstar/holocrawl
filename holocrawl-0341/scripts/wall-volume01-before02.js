// Rendering-only candidate: original terrain and collision cells remain unchanged.
let wallVolumeEnabled=true;
function thinWallShape(map,x,y){
 const solid=(x,y)=>isWall(feature(map,x,y))||isDoor(feature(map,x,y));
 const n=solid(x,y-1),e=solid(x+1,y),s=solid(x,y+1),w=solid(x-1,y);
 return{n,e,s,w,thin:(!n&&!s)||(!e&&!w)};
}
const originalCityTile=tile;
function drawThinWall(c,map,x,y,px,py,t,shape){
 const q=t/32,sx=hash(map.seed,x,y)%8*32;
 c.save();c.imageSmoothingEnabled=false;
 // Concrete texture is reused, with a lighter upper surface and a dark front.
 const textureRect=(xx,yy,ww,hh,light)=>{c.drawImage(images.wall,sx,0,32,32,px+xx*q,py+yy*q,ww*q,hh*q);c.fillStyle=light;c.fillRect(px+xx*q,py+yy*q,ww*q,hh*q);};
 const line=(color,x,y,w,h)=>{c.fillStyle=color;c.fillRect(px+x*q,py+y*q,w*q,h*q)};
 if(!shape.n&&!shape.s){
  textureRect(0,0,32,10,'rgba(143,147,138,.36)');
  textureRect(0,10,32,21,'rgba(27,31,29,.18)');
  line('#85867a',0,1,32,1);line('#393b35',0,9,32,1);line('#1d211d',0,30,32,2);
  if(!shape.w){line('#252923',0,2,1,29);line('#696b60',1,2,1,7);textureRect(1,10,3,20,'rgba(11,17,13,.26)');}
  if(!shape.e){textureRect(27,10,4,20,'rgba(9,15,12,.42)');line('#1c211c',31,2,1,29);line('#4b4f44',27,10,1,20);}
 }else{
  // A narrow north/south wall has a continuous top and a visible side face.
  textureRect(0,0,25,32,'rgba(143,147,138,.32)');textureRect(25,0,7,32,'rgba(12,18,14,.34)');
  line('#767a6b',1,0,1,32);line('#42483c',24,0,1,32);line('#1c211b',31,0,1,32);
  if(!shape.n){line('#1c211b',0,0,32,1);line('#85867a',2,1,23,1);}
  if(!shape.s){textureRect(0,23,25,8,'rgba(21,27,21,.26)');line('#1c211b',0,31,32,1);}
 }
 c.restore();
}
tile=function(c,map,x,y,px,py,t,style='fit',forceState=null,oldWall=wallOld){
 const f=feature(map,x,y),shape=thinWallShape(map,x,y);
 if(wallVolumeEnabled&&style==='fit'&&!oldWall&&f.includes('wall')&&!f.includes('clear_')&&f!=='crystal_wall'&&shape.thin){drawThinWall(c,map,x,y,px,py,t,shape);return;}
 return originalCityTile(c,map,x,y,px,py,t,style,forceState,oldWall);
};
