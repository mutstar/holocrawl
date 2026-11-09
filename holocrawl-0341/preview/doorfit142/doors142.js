(function(root){'use strict';const cache=new WeakMap();
function solids(m){if(cache.has(m))return cache.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='vertical')a[d.y*m.w+d.x]=0;cache.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 // Keep141 wall reveals. Recess the ordinary door inside the visible wall rails.
 q.save();q.beginPath();q.rect(x+3,y,26,32);q.clip();
 q.fillStyle='#2d3b39';q.fillRect(x+3,y,26,32);q.drawImage(base,x+5,y+2,22,28,x+5,y+2,22,28);
 q.fillStyle='#859791';q.fillRect(x+3,y,26,2);q.fillRect(x+3,y,1,32);q.fillRect(x+28,y,1,32);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+4,y,24,32);
 q.restore();
}root.DoorFit142={solids,direction,draw};})(globalThis);