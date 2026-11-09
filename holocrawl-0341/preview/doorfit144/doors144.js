(function(root){'use strict';const cache=new WeakMap(),sprites=new Map();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function sprite(opened){if(sprites.has(opened))return sprites.get(opened);const c=document.createElement('canvas');c.width=32;c.height=36;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 // Native wall rails span0..27;28..31 are the east-facing shadow, not part of the frame.
 for(const [dx,color]of [[28,'#57696f'],[29,'#3c4f54'],[30,'#2c363c'],[31,'#2f393f']]){q.fillStyle=color;q.fillRect(dx,0,1,36);}
 q.fillStyle='#273b39';q.fillRect(0,0,28,36);q.clearRect(2,3,24,32);
 q.fillStyle='#718a85';q.fillRect(0,0,28,3);q.fillRect(0,3,2,32);q.fillRect(26,3,2,32);
 q.fillStyle='#9ca9aa';q.fillRect(0,0,28,1);q.fillStyle='#7c888d';q.fillRect(0,1,1,34);q.fillStyle='#747d81';q.fillRect(27,1,1,34);
 q.fillStyle='#465c58';q.fillRect(1,2,26,1);q.fillRect(1,35,26,1);
 if(opened){for(const x of [2,22]){q.fillStyle='#304b4d';q.fillRect(x,3,4,32);q.fillStyle='#91a9a2';q.fillRect(x,3,1,31);q.fillStyle='#5f8182';q.fillRect(x+1,5,2,27);q.fillStyle='#bdbe9c';q.fillRect(x+1,24,1,3);}}
 else{for(const x of [2,15]){q.fillStyle='#314b4c';q.fillRect(x,3,11,32);q.fillStyle='#648386';q.fillRect(x+1,4,9,30);q.fillStyle='#93a9a4';q.fillRect(x+1,4,1,29);q.fillRect(x+2,4,7,1);q.fillStyle='#adc0b4';q.fillRect(x+3,7,5,1);q.fillStyle='#28494f';q.fillRect(x+2,8,7,13);q.fillStyle='#426b76';q.fillRect(x+3,9,5,11);q.fillStyle='#729095';q.fillRect(x+3,9,1,10);q.fillStyle='#45696b';q.fillRect(x+2,23,7,1);q.fillStyle='#587574';q.fillRect(x+2,25,7,7);}
  q.fillStyle='#c4c59b';q.fillRect(11,24,1,4);q.fillRect(16,24,1,4);
 }
 sprites.set(opened,c);return c;}
function draw(q,m,d,opened){q.drawImage(sprite(opened),d.x*32,d.y*32-4);}
root.DoorFit144={solids,direction,draw,sprite,frame:{w:28,h:36,canvasW:32,xOffset:0,yOffset:-4,leafWidth:11,grayRight:27,shadowStart:28,shadowWidth:4}};})(globalThis);