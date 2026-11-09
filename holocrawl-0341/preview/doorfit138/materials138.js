(function(root){'use strict';const cache=new Map();let settings;
 const make=(w=32,h=32)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
 function configure(s){settings=s;cache.clear();}
 function floors(){return settings.floorTiles.map(base=>{const c=make(),q=c.getContext('2d');q.drawImage(base,0,0);q.fillStyle='rgba(168,158,132,.40)';q.fillRect(0,0,32,32);return c;});}
 function wall(mask){if(cache.has('wall:'+mask))return cache.get('wall:'+mask);const c=make(),q=c.getContext('2d',{willReadFrequently:true}),{wall:atlas,rects,planes}=settings;q.drawImage(atlas,...rects[`${mask}:0`],0,0,32,32);const a=q.getImageData(0,0,32,32);
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){const i=(y*32+x)*4;if(!a.data[i+3])continue;const l=(a.data[i]+a.data[i+1]+a.data[i+2])/3,front=planes[String(mask)][y*32+x]==='1';let col=front?[204+l*.11,198+l*.10,177+l*.08]:[91+l*.14,107+l*.12,103+l*.10];if(l<37)col=[43+l*.22,56+l*.20,61+l*.22];if(front&&(y===11||y===28))col=[234,226,202];if(front&&(y===14||y===30))col=[169,164,140];for(let k=0;k<3;k++)a.data[i+k]=col[k];}q.putImageData(a,0,0);cache.set('wall:'+mask,c);return c;}
 function window(q,x,y){q.fillStyle='#344f50';q.fillRect(x+3,y+7,26,23);q.fillStyle='#78ac99';q.fillRect(x+4,y+7,24,22);q.fillStyle='#c1dfd5';q.fillRect(x+7,y+10,18,15);q.fillStyle='#649182';q.fillRect(x+15,y+9,2,18);q.fillRect(x+6,y+17,20,2);q.fillStyle='#f0e8ce';q.fillRect(x+2,y+28,28,2);q.fillStyle='#7d8c7d';q.fillRect(x+3,y+30,26,1);}
 function paint(q,m){const h=m.home;if(!h)return;const x=h.x*32,y=h.y*32;
  // A compact central lounge rather than a room-filling palace set.
  q.fillStyle='#647a70';q.fillRect(x+2*32+5,y+4*32+2,5*32-10,5*32-4);q.strokeStyle='#a29a78';q.lineWidth=1;q.strokeRect(x+2*32+8.5,y+4*32+5.5,5*32-17,5*32-11);
  for(const wx of [3,9])window(q,x+wx*32,y);
  for(const wx of [2,10])window(q,x+wx*32,y+10*32);
  // Low stone threshold meets the entry sprite and has the same one-cell passage.
  q.fillStyle='#8d8977';q.fillRect(x+5*32+3,y+10*32+29,3*32-6,3);
  for(const wx of [4,8]){const xx=x+wx*32;q.fillStyle='#303c3a';q.fillRect(xx+11,y+10*32+14,10,13);q.fillStyle='#c9b27a';q.fillRect(xx+13,y+10*32+16,6,8);q.fillStyle='#e1d2a4';q.fillRect(xx+14,y+10*32+17,3,2);}
 }
 function door(open){const key='door:'+open;if(cache.has(key))return cache.get(key);const c=make(),q=c.getContext('2d');q.imageSmoothingEnabled=false;
  q.fillStyle='#d6cbaa';q.beginPath();q.ellipse(16,10,13,9,0,Math.PI,0);q.lineTo(29,32);q.lineTo(3,32);q.fill();q.fillStyle='#44382d';q.beginPath();q.ellipse(16,10,11,7,0,Math.PI,0);q.lineTo(27,32);q.lineTo(5,32);q.fill();
  if(open){q.clearRect(8,12,16,20);q.clearRect(12,5,8,27);q.fillStyle='#71503a';q.fillRect(5,11,3,20);q.fillRect(24,11,3,20);q.fillStyle='#b49156';q.fillRect(7,12,1,18);q.fillRect(24,12,1,18);}else{q.fillStyle='#805d40';q.beginPath();q.ellipse(16,10,10,6,0,Math.PI,0);q.lineTo(26,31);q.lineTo(6,31);q.fill();q.fillStyle='#4d3b2d';q.fillRect(15,4,2,27);q.strokeStyle='#b29360';q.lineWidth=1;for(const dx of [8.5,18.5])q.strokeRect(dx,13.5,5,13);q.fillStyle='#ddbd72';q.fillRect(13,21,1,3);q.fillRect(18,21,1,3);}cache.set(key,c);return c;
 }
 root.HomeMaterial138={configure,floors,wall,paint,door};
})(globalThis);
