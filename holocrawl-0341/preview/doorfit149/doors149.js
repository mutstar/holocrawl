(function(root){'use strict';const cache=new WeakMap(),sprites=new Map();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
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
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 // Wall shoulders belong to the map, not the transparent door asset. Extend only the real rails.
 if(direction(m,d)==='vertical'&&base){for(let px=0;px<28;px++){const h=Math.max(0,archTop(px)-4);if(h>0)q.drawImage(base,x+px,y-1,1,1,x+px,y,1,h);}}
 // The door ends at the original wall boundary. Never paint a floor strip beneath the closed leaves.
 // A translucent cast shadow follows the side post, never an opaque rectangular matte.
 for(let dx=0;dx<4;dx++){q.fillStyle='rgba(0,0,0,'+(.28-dx*.05)+')';q.fillRect(x+28+dx,y+6,1,26);}
 q.drawImage(sprite(opened),x,y-4);
}
root.DoorFit149={solids,direction,draw,sprite,archTop,openingTop,frame:{w:28,h:36,canvasW:32,xOffset:0,yOffset:-4,leafWidth:12,closedSeamWidth:2,closedSeamOpaque:true,mirroredInterior:true,grayRight:27,shadowStart:28,shadowWidth:4,archRise:10,material:'solid iron',transparentExterior:true,shadowInSprite:false,nativeWallReturns:true,openBottom:true,flushThreshold:null,archMaterial:'silver steel',leafMaterial:'dark iron plate',bottomAtWallBoundary:true}};})(globalThis);