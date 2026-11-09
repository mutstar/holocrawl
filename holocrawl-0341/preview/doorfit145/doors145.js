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
 // Draw one leaf and mirror it exactly: equal margins, glass panels and centre seam.
 const leaf=document.createElement('canvas');leaf.width=opened?4:12;leaf.height=32;const p=leaf.getContext('2d');
 if(opened){p.fillStyle='#304b4d';p.fillRect(0,0,4,32);p.fillStyle='#91a9a2';p.fillRect(0,0,1,31);p.fillStyle='#5f8182';p.fillRect(1,2,2,27);p.fillStyle='#bdbe9c';p.fillRect(2,21,1,3);}
 else{p.fillStyle='#648386';p.fillRect(0,0,12,32);p.fillStyle='#7e9998';p.fillRect(0,0,12,1);p.fillStyle='#94aaa5';p.fillRect(0,1,1,30);p.fillStyle='#4c696b';p.fillRect(11,0,1,32);
  p.fillStyle='#adc0b4';p.fillRect(3,3,6,1);p.fillStyle='#3e5b60';p.fillRect(2,5,8,14);p.fillStyle='#426b76';p.fillRect(3,6,6,12);p.fillStyle='#729095';p.fillRect(3,6,1,11);
  p.fillStyle='#7b9390';p.fillRect(1,20,10,1);p.fillStyle='#4d6a6b';p.fillRect(2,23,8,7);p.fillStyle='#587574';p.fillRect(3,24,6,5);p.fillStyle='#c4c59b';p.fillRect(10,22,1,4);
 }
 q.drawImage(leaf,2,3);q.save();q.translate(26,3);q.scale(-1,1);q.drawImage(leaf,0,0);q.restore();
 sprites.set(opened,c);return c;}
function draw(q,m,d,opened){q.drawImage(sprite(opened),d.x*32,d.y*32-4);}
root.DoorFit145={solids,direction,draw,sprite,frame:{w:28,h:36,canvasW:32,xOffset:0,yOffset:-4,leafWidth:12,closedSeamWidth:2,closedSeamOpaque:true,mirroredInterior:true,grayRight:27,shadowStart:28,shadowWidth:4}};})(globalThis);