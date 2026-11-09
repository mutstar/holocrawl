(function(root){'use strict';const cache=new Map();let settings;
 const make=(w=32,h=32)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
 function configure(s){settings=s;cache.clear();}
 function floors(){return Array.from({length:8},(_,n)=>{const c=make(),q=c.getContext('2d'),rng=StreetGen.random('home-marble133:'+n);q.fillStyle=['#b9b39f','#bcb5a1','#b7b09c','#bcb6a2'][n%4];q.fillRect(0,0,32,32);q.fillStyle='#989683';q.fillRect(0,0,32,1);q.fillRect(0,0,1,32);q.fillStyle='#c9c1aa';q.fillRect(1,1,31,1);for(let i=0;i<12;i++){q.fillStyle=rng()<.5?'#b1ac98':'#c2baa4';q.fillRect(2+Math.floor(rng()*27),3+Math.floor(rng()*26),1+Math.floor(rng()*3),1);}if(n%3===0){q.fillStyle='#c9c1ac';const y=7+n;q.fillRect(15,y,5,1);q.fillRect(19,y+1,3,1);q.fillRect(21,y+2,2,1);}return c;});}
 function wall(mask){if(cache.has('wall:'+mask))return cache.get('wall:'+mask);const c=make(),q=c.getContext('2d',{willReadFrequently:true}),{wall:atlas,rects,planes}=settings;q.drawImage(atlas,...rects[`${mask}:0`],0,0,32,32);const a=q.getImageData(0,0,32,32);
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){const i=(y*32+x)*4;if(!a.data[i+3])continue;const l=(a.data[i]+a.data[i+1]+a.data[i+2])/3,front=planes[String(mask)][y*32+x]==='1';let col=front?[214+l*.11,207+l*.10,182+l*.08]:[155+l*.14,168+l*.12,157+l*.10];if(l<37)col=[43+l*.22,56+l*.20,61+l*.22];if(front&&(y===11||y===28))col=[239,232,206];if(front&&(y===14||y===30))col=[155,156,135];for(let k=0;k<3;k++)a.data[i+k]=col[k];}q.putImageData(a,0,0);cache.set('wall:'+mask,c);return c;}
 function window(q,x,y){q.fillStyle='#344f50';q.fillRect(x+3,y+7,26,23);q.fillStyle='#78ac99';q.fillRect(x+4,y+7,24,22);q.fillStyle='#c1dfd5';q.fillRect(x+7,y+10,18,15);q.fillStyle='#649182';q.fillRect(x+15,y+9,2,18);q.fillRect(x+6,y+17,20,2);q.fillStyle='#f0e8ce';q.fillRect(x+2,y+28,28,2);q.fillStyle='#7d8c7d';q.fillRect(x+3,y+30,26,1);}
 function paint(q,m){const h=m.home;if(!h)return;const x=h.x*32,y=h.y*32;
  // The common hall has marble, a central mint rug, a red foyer rug and a low tatami area.
  q.save();q.beginPath();q.rect(x+32,y+32,15*32,11*32);q.clip();
  q.fillStyle='#80a39b';q.fillRect(x+5*32+3,y+4*32+3,6*32-6,6*32-6);q.strokeStyle='#ccbe8f';q.lineWidth=2;q.strokeRect(x+5*32+7,y+4*32+7,6*32-14,6*32-14);q.strokeStyle='#a7b8a4';q.lineWidth=1;q.strokeRect(x+5*32+12.5,y+4*32+12.5,6*32-25,6*32-25);
  q.fillStyle='#514638';q.fillRect(x+32+2,y+7*32+3,5*32-4,4*32-3);q.fillStyle='#b08853';q.fillRect(x+32+4,y+7*32+3,5*32-8,4*32-7);q.fillStyle='#718564';q.fillRect(x+32+9,y+7*32+7,5*32-18,4*32-17);q.strokeStyle='#566c53';q.lineWidth=1;for(let j=0;j<3;j++)q.strokeRect(x+32+10.5+j*46,y+7*32+9.5,44,4*32-23);
  q.fillStyle='#988458';q.beginPath();q.arc(x+8.5*32,y+11.7*32,51,0,2*Math.PI);q.fill();q.fillStyle='#8e3d3d';q.beginPath();q.arc(x+8.5*32,y+11.7*32,46,0,2*Math.PI);q.fill();q.fillStyle='#c2a45d';for(const dx of [-13,0,13]){q.beginPath();q.moveTo(x+8.5*32+dx,y+11.7*32-8);q.lineTo(x+8.5*32+dx+4,y+11.7*32);q.lineTo(x+8.5*32+dx,y+11.7*32+8);q.lineTo(x+8.5*32+dx-4,y+11.7*32);q.fill();}
  q.fillStyle='#8fa8a0';q.fillRect(x+7*32+4,y+2*32+3,3*32-8,2*32-6);q.strokeStyle='#c4bc93';q.strokeRect(x+7*32+6.5,y+2*32+5.5,3*32-13,2*32-11);q.restore();
  for(const wx of [1,15])window(q,x+wx*32,y);for(const wx of [2,5,11,14])window(q,x+wx*32,y+12*32);
  for(const wx of [0,16]){q.fillStyle='#b4b89f';q.fillRect(x+wx*32+9,y+4,14,12*32+25);q.fillStyle='#e4dcc1';q.fillRect(x+wx*32+11,y+5,10,12*32+24);q.fillStyle='#d0c39c';q.fillRect(x+wx*32+9,y+12*32+22,14,4);}
 }
 function door(open){const key='door:'+open;if(cache.has(key))return cache.get(key);const c=make(),q=c.getContext('2d');q.imageSmoothingEnabled=false;
  q.fillStyle='#d6cbaa';q.beginPath();q.ellipse(16,10,13,9,0,Math.PI,0);q.lineTo(29,32);q.lineTo(3,32);q.fill();q.fillStyle='#44382d';q.beginPath();q.ellipse(16,10,11,7,0,Math.PI,0);q.lineTo(27,32);q.lineTo(5,32);q.fill();
  if(open){q.clearRect(8,12,16,20);q.clearRect(12,5,8,27);q.fillStyle='#71503a';q.fillRect(5,11,3,20);q.fillRect(24,11,3,20);q.fillStyle='#b49156';q.fillRect(7,12,1,18);q.fillRect(24,12,1,18);}else{q.fillStyle='#805d40';q.beginPath();q.ellipse(16,10,10,6,0,Math.PI,0);q.lineTo(26,31);q.lineTo(6,31);q.fill();q.fillStyle='#4d3b2d';q.fillRect(15,4,2,27);q.strokeStyle='#b29360';q.lineWidth=1;for(const dx of [8.5,18.5])q.strokeRect(dx,13.5,5,13);q.fillStyle='#ddbd72';q.fillRect(13,21,1,3);q.fillRect(18,21,1,3);}cache.set(key,c);return c;
 }
 root.HomeMaterial133={configure,floors,wall,paint,door};
})(globalThis);
