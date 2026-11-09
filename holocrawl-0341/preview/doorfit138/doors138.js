(function(root){'use strict';
function solids(m){return m.cells;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 // Only the doorway between north/south wall tiles gains a continuous outer frame.
 q.fillStyle='#2d3b39';q.fillRect(x,y,32,32);q.drawImage(base,x+2,y+2,28,28,x+2,y+2,28,28);
 q.fillStyle='#859791';q.fillRect(x,y,32,2);q.fillRect(x,y,2,32);q.fillRect(x+30,y,2,32);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+2,y,28,32);
}root.DoorFit138={solids,direction,draw};})(globalThis);