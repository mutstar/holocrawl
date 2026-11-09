(function(root){'use strict';
function solids(m){return m.cells;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 // The reference's low rectangular door is seated inside a full-height structural portal.
 // The lintel reaches the north wall; side piers meet the south wall. No world-cell changes.
 q.drawImage(base,x,y,32,32,x,y,32,32);
 q.fillStyle='#283634';q.fillRect(x,y,32,32);
 q.drawImage(base,x+4,y+10,24,22,x+4,y+10,24,22);
 q.fillStyle='#5f7372';q.fillRect(x+1,y+1,30,3);q.fillRect(x+1,y+4,3,28);q.fillRect(x+28,y+4,3,28);
 q.fillStyle='#99a8a1';q.fillRect(x,y,32,1);q.fillRect(x+1,y+1,30,1);q.fillRect(x+1,y+4,1,28);q.fillRect(x+30,y+4,1,28);
 q.fillStyle='#3b4e4e';q.fillRect(x+4,y+4,24,6);q.fillStyle='#768985';q.fillRect(x+4,y+8,24,2);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+3,y+10,26,22);
}root.DoorFit139={solids,direction,draw};})(globalThis);