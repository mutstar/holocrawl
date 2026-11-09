(function(root){'use strict';const cache=new WeakMap(),sprites=new Map();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home)a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
const archTop=x=>Math.round(10*(1-Math.sqrt(Math.max(0,1-Math.pow((x-13.5)/13.5,2))))),openingTop=x=>archTop(x)+3;
function sprite(opened){if(sprites.has(opened))return sprites.get(opened);const c=document.createElement('canvas');c.width=32;c.height=36;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 // No baked background or rectangular shadow: keep every pixel outside the arch transparent.
 for(let x=0;x<28;x++){const y=archTop(x);q.fillStyle='#65757b';q.fillRect(x,y,1,36-y);q.fillStyle='#96a4a7';q.fillRect(x,y+1,1,2);q.fillStyle='#c3cbc7';q.fillRect(x,y,1,1);}
 q.fillStyle='#7c888d';q.fillRect(0,archTop(0)+1,1,35-archTop(0));q.fillStyle='#747d81';q.fillRect(27,archTop(27)+1,1,35-archTop(27));
 // Separate steel hardware on the bright arch, distinct from the dark iron leaves.
 q.fillStyle='#d0d4cb';for(const x of [3,8,19,24])q.fillRect(x,archTop(x)+1,1,1);for(const y of [18,30]){q.fillRect(1,y,1,1);q.fillRect(26,y,1,1);}
 // An integer stair-step arch aperture preserves hard pixel edges.
 q.save();q.beginPath();q.moveTo(2,36);q.lineTo(2,openingTop(2));for(let x=2;x<26;x++){q.lineTo(x,openingTop(x));q.lineTo(x+1,openingTop(x));}q.lineTo(26,36);q.closePath();q.clip();q.clearRect(0,0,28,36);
 const leaf=document.createElement('canvas');leaf.width=opened?4:12;leaf.height=33;const p=leaf.getContext('2d');
 if(opened){p.fillStyle='#2a3c46';p.fillRect(0,0,4,33);p.fillStyle='#74898e';p.fillRect(0,0,1,31);p.fillStyle='#435f6d';p.fillRect(1,1,2,30);p.fillStyle='#aeb8b4';p.fillRect(2,21,1,3);}
 else{p.fillStyle='#35454e';p.fillRect(0,0,12,33);p.fillStyle='#75858c';p.fillRect(0,0,1,32);p.fillStyle='#22343a';p.fillRect(11,0,1,33);
  p.fillStyle='#263a44';p.fillRect(2,7,8,21);p.fillStyle='#445b66';p.fillRect(3,8,6,19);p.fillStyle='#607782';p.fillRect(3,8,1,18);
  for(const y of [10,25]){p.fillStyle='#243840';p.fillRect(0,y,11,3);p.fillStyle='#7f9096';p.fillRect(0,y,11,1);p.fillStyle='#4f666f';p.fillRect(0,y+1,11,1);p.fillStyle='#bdc5bf';p.fillRect(2,y+1,1,1);p.fillRect(8,y+1,1,1);}
  p.fillStyle='#293c42';p.fillRect(8,19,3,6);p.fillStyle='#aeb8b4';p.fillRect(9,20,2,4);p.fillStyle='#667575';p.fillRect(10,21,1,2);
 }
 q.drawImage(leaf,2,3);q.save();q.translate(26,3);q.scale(-1,1);q.drawImage(leaf,0,0);q.restore();q.restore();
 sprites.set(opened,c);return c;}
const capCache=new WeakMap();let canonical;
function measure(image,sx,sy,source){const pixels=image.getContext('2d').getImageData(sx,sy,1,12).data;let h=0;for(;h<12;h++){const i=h*4,r=pixels[i],g=pixels[i+1],b=pixels[i+2];if(pixels[i+3]!==255||r<90||g<100||b<100||Math.abs(r-g)>=30||Math.abs(g-b)>=25)break;}return h>0&&h<12?{image,sx,sy,h,source}:null;}
function fallbackCap(){if(canonical)return canonical;const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');q.translate(-32,-32);WallHeight121.wall(q,new Uint8Array([1,1,1,0,0,0,0,0,0]),3,3,1,1,32,0);canonical=measure(c,16,0,{kind:'native-wall-atlas'});if(!canonical)throw Error('Native gray wall cap not found');return canonical;}
function capProfile(m,d,base){if(!base)return fallbackCap();let entries=capCache.get(base);if(!entries){entries=new Map();capCache.set(base,entries);}const key=d.x+','+d.y;if(entries.has(key))return entries.get(key);
 for(const yy of [d.y+1,d.y,d.y+2,d.y-1])for(const dx of [1,-1,2,-2,0]){const xx=d.x+dx;if(xx<1||xx>=m.w-1||yy<1||yy>=m.h-1||m.cells[yy*m.w+xx]!==0||m.cells[(yy-1)*m.w+xx]===0||(m.home&&xx>=m.home.x&&xx<m.home.x+m.home.w&&yy>=m.home.y&&yy<m.home.y+m.home.h))continue;const p=measure(base,xx*32+16,yy*32,{kind:'adjacent-wall',x:xx,y:yy});if(p){entries.set(key,p);return p;}}
 const p=fallbackCap();entries.set(key,p);return p;
}
function horizontalReturns(q,m,d,base){
 if(!base||direction(m,d)!=='horizontal')return;
 const x=d.x*32,y=d.y*32;
 // Join wall mass to the outside of the unchanged arch. Never cover the aperture.
 // Each return copies the actual neighboring wall edge at its original vertical scale.
 for(let px=0;px<32;px++){
  const top=px<28?Math.max(0,archTop(px)-4):32;
  const sx=px<14?x-1:x+32;
  if(top>0)q.drawImage(base,sx,y,1,top,x+px,y,1,top);
  if(px>=28)q.drawImage(base,sx,y,1,32,x+px,y,1,32);
 }
 // Mitre the native coping down to the curved shoulder, leaving no dark slit
 // between the straight wall rail and the unchanged silver arch.
 const p=capProfile(m,d,base);
 for(let px=0;px<32;px++){
  const end=px<28?Math.max(0,archTop(px)-4):Math.max(0,archTop(27)-4);
  const h=Math.min(p.h,end);
  if(h>0)q.drawImage(p.image,p.sx,p.sy+p.h-h,1,h,x+px,y+end-h,1,h);
 }
}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 horizontalReturns(q,m,d,base);
 // Wall shoulders belong to the map, not the transparent door asset. Extend only the real rails.
 if(direction(m,d)==='vertical'&&base){for(let px=0;px<28;px++){const h=Math.max(0,archTop(px)-4);if(h>0)q.drawImage(base,x+px,y-1,1,1,x+px,y,1,h);}}
 // The door ends at the original wall boundary. Never paint a floor strip beneath the closed leaves.
 // A translucent cast shadow follows the side post, never an opaque rectangular matte.
 for(let dx=0;dx<4;dx++){q.fillStyle='rgba(0,0,0,'+(.28-dx*.05)+')';q.fillRect(x+28+dx,y+6,1,26);}
 q.drawImage(sprite(opened),x,y-4);
 // Copy the actual native gray rail profile at1:1 vertical scale: thickness and shading stay identical.
 const p=capProfile(m,d,base);q.drawImage(p.image,p.sx,p.sy,1,p.h,x,y+32,28,p.h);
}
root.DoorFit152={solids,direction,draw,sprite,horizontalReturns,capProfile,archTop,openingTop,frame:{w:28,h:36,canvasW:32,xOffset:0,yOffset:-4,leafWidth:12,closedSeamWidth:2,closedSeamOpaque:true,mirroredInterior:true,grayRight:27,shadowStart:28,shadowWidth:4,archRise:10,material:'solid iron',transparentExterior:true,shadowInSprite:false,nativeWallReturns:true,openBottom:true,flushThreshold:null,archMaterial:'silver steel',leafMaterial:'dark iron plate',bottomAtWallBoundary:true,wallSill:{w:28,h:"native-wall-cap",yOffset:32,source:"actual native wall pixels; no independent thickness"}}};})(globalThis);