(function(){'use strict';const cache=new Map();
function sprite(opened){
 if(cache.has(opened))return cache.get(opened);const c=document.createElement('canvas');c.width=96;c.height=32;const q=c.getContext('2d');q.imageSmoothingEnabled=false;
 const f=(col,x,y,w,h)=>{q.fillStyle=col;q.fillRect(x,y,w,h);};
 // Flush32px frame; both leaves and rails stay inside the three entrance cells.
 f('#252b3e',0,0,96,4);f('#9b9eb1',0,0,96,1);f('#6d758c',0,1,96,2);f('#34394f',0,3,96,1);
 f('#66677e',0,4,5,26);f('#66677e',91,4,5,26);f('#a0a3b8',0,4,1,26);f('#a0a3b8',95,4,1,26);
 f('#3d415b',3,4,2,26);f('#3d415b',91,4,2,26);
 f('#b881aa',2,6,1,10);f('#83b8c3',93,6,1,10);
 q.save();q.beginPath();q.rect(5,4,86,26);q.clip();
 function leaf(right){q.save();q.translate(right?96:0,0);if(right)q.scale(-1,1);q.translate(opened?-38:0,0);
  f('#272f43',5,4,43,26);f('#7b899e',5,4,43,1);f('#65788b',6,5,41,24);f('#24474e',8,7,37,15);
  f('#325c62',9,8,35,2);f('#2c5158',9,10,35,11);f('#466f75',12,10,2,10);f('#507e83',14,9,6,2);f('#3d6970',28,14,10,1);
  f('#789b9f',7,6,1,16);f('#91b1b3',8,6,37,1);f('#83929d',7,22,38,2);f('#333c53',7,24,38,4);
  for(let x=13;x<40;x+=8)f('#52637a',x,25,4,1);
  f('#252b40',46,4,2,26);f('#afbdc0',43,12,2,7);f('#465a6b',42,13,1,6);q.restore();}
 leaf(false);leaf(true);q.restore();
 f('#687489',0,30,96,1);f('#424b63',0,31,96,1);
 f('#253348',43,1,10,2);f(opened?'#86bea9':'#b48cab',45,1,6,1);
 cache.set(opened,c);return c;
}
function draw(q,m,opened){q.drawImage(sprite(opened),(m.entry.x-1)*32,m.entry.y*32);}
function collision(m,opened){const open=m.open.slice();if(!opened)for(let dx=-1;dx<=1;dx++)open[m.entry.y*m.w+m.entry.x+dx]=0;return{...m,open};}
window.ArcadeDoor193={sprite,draw,collision};})();
