(function(root){'use strict';const cache=new WeakMap(),sprites=new Map();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function sprite(opened){if(sprites.has(opened))return sprites.get(opened);const c=document.createElement('canvas');c.width=32;c.height=36;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 q.fillStyle='#273b39';q.fillRect(0,0,32,36);q.clearRect(3,3,26,32);
 q.fillStyle='#718a85';q.fillRect(0,0,32,3);q.fillRect(0,3,3,32);q.fillRect(29,3,3,32);
 q.fillStyle='#a0b0a5';q.fillRect(0,0,32,1);q.fillRect(0,1,1,34);q.fillRect(31,1,1,34);
 q.fillStyle='#465c58';q.fillRect(1,2,30,1);q.fillRect(2,3,1,32);q.fillRect(29,3,1,32);q.fillRect(1,35,30,1);
 if(opened){for(const x of [3,25]){q.fillStyle='#304b4d';q.fillRect(x,3,4,32);q.fillStyle='#91a9a2';q.fillRect(x,3,1,31);q.fillStyle='#5f8182';q.fillRect(x+1,5,2,27);q.fillStyle='#bdbe9c';q.fillRect(x+1,24,1,3);}}
 else{for(const x of [3,17]){q.fillStyle='#314b4c';q.fillRect(x,3,12,32);q.fillStyle='#648386';q.fillRect(x+1,4,10,30);q.fillStyle='#93a9a4';q.fillRect(x+1,4,1,29);q.fillRect(x+2,4,8,1);q.fillStyle='#adc0b4';q.fillRect(x+3,7,6,1);q.fillStyle='#28494f';q.fillRect(x+2,8,8,13);q.fillStyle='#426b76';q.fillRect(x+3,9,6,11);q.fillStyle='#729095';q.fillRect(x+3,9,1,10);q.fillStyle='#45696b';q.fillRect(x+2,23,8,1);q.fillStyle='#587574';q.fillRect(x+2,25,8,7);}
  q.fillStyle='#c4c59b';q.fillRect(13,24,1,4);q.fillRect(18,24,1,4);
 }
 sprites.set(opened,c);return c;}
function draw(q,m,d,opened){q.drawImage(sprite(opened),d.x*32,d.y*32-4);}
root.DoorFit143={solids,direction,draw,sprite,frame:{w:32,h:36,yOffset:-4,leafWidth:12}};})(globalThis);