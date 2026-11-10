(function(){'use strict';const cache=new Map();
function sprite(opened){if(cache.has(opened))return cache.get(opened);const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d'),f=(col,x,y,w,h)=>{q.fillStyle=col;q.fillRect(x,y,w,h);};
 // Compact upright variant; reuse the main door palette and pane/handle design.
 f('#252b3e',0,0,32,4);f('#9b9eb1',0,0,32,1);f('#6d758c',0,1,32,2);f('#34394f',0,3,32,1);
 for(const x of [0,29]){f('#66677e',x,4,3,26);f('#a0a3b8',x===0?0:31,4,1,26);}f('#b881aa',1,6,1,10);f('#83b8c3',30,6,1,10);
 q.save();q.beginPath();q.rect(3,4,26,26);q.clip();
 function leaf(right){q.save();q.translate(right?32:0,0);if(right)q.scale(-1,1);q.translate(opened?-11:0,0);
 f('#272f43',3,4,13,26);f('#7b899e',3,4,13,1);f('#65788b',4,5,11,24);f('#24474e',5,7,9,15);f('#325c62',6,8,7,2);f('#2c5158',6,10,7,11);f('#466f75',7,10,1,10);f('#507e83',8,9,3,2);f('#3d6970',10,14,3,1);f('#91b1b3',5,6,9,1);f('#83929d',4,22,11,2);f('#333c53',4,24,11,4);f('#52637a',7,25,4,1);f('#252b40',15,4,1,26);f('#afbdc0',13,12,1,7);q.restore();}
 leaf(false);leaf(true);q.restore();f('#687489',0,30,32,1);f('#424b63',0,31,32,1);f(opened?'#86bea9':'#b48cab',14,1,4,1);cache.set(opened,c);return c;
}
function draw(q,m,opened){for(const d of m.doors)q.drawImage(d.id==='main'?ArcadeDoor193.sprite(opened.main):sprite(opened[d.id]),d.x*32,d.y*32);}
function collision(m,opened){const open=m.open.slice();for(const d of m.doors)if(!opened[d.id])for(let x=d.x;x<d.x+d.w;x++)open[d.y*m.w+x]=0;return{...m,open};}
window.ArcadeDoor194={sprite,draw,collision};})();
