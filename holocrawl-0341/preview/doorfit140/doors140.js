(function(root){'use strict';
function solids(m){return m.cells;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='horizontal'){q.drawImage(opened?im.opened:im.closed,x,y);return;}
 q.drawImage(base,x,y,32,32,x,y,32,32);
 // North/south wall ends anchor the portal; the leaves are viewed obliquely along the wall.
 q.fillStyle='#293735';q.fillRect(x,y,32,3);q.fillRect(x,y+29,32,3);
 q.fillStyle='#70837e';q.fillRect(x,y,32,1);q.fillRect(x,y+29,32,1);
 q.fillStyle='#9aa9a1';q.fillRect(x+10,y+1,5,2);q.fillRect(x+10,y+29,5,2);
 if(opened){
  // Both leaves swing east at the two hinges, clearing the left/right passage in the centre.
  for(const yy of [2,25]){q.fillStyle='#233333';q.fillRect(x+12,y+yy,17,5);q.fillStyle='#637e7f';q.fillRect(x+13,y+yy,14,3);q.fillStyle='#9aacaa';q.fillRect(x+13,y+yy,14,1);q.fillStyle='#3d646c';q.fillRect(x+16,y+yy+1,9,1);q.fillStyle='#344b4a';q.fillRect(x+14,y+yy+3,14,1);}
 }else{
  q.fillStyle='rgba(0,0,0,.28)';q.fillRect(x+23,y+3,3,26);
  for(const yy of [2,17]){q.fillStyle='#263937';q.fillRect(x+10,y+yy,14,13);q.fillStyle='#6f8988';q.fillRect(x+12,y+yy,10,12);q.fillStyle='#a1b2aa';q.fillRect(x+12,y+yy,1,12);q.fillRect(x+13,y+yy,8,1);q.fillStyle='#34535b';q.fillRect(x+14,y+yy+2,6,7);q.fillStyle='#4d747b';q.fillRect(x+15,y+yy+3,4,5);q.fillStyle='#334a4b';q.fillRect(x+21,y+yy+1,2,11);}
  q.fillStyle='#c2b88d';q.fillRect(x+18,y+14,3,1);q.fillRect(x+18,y+17,3,1);
 }
}root.DoorFit140={solids,direction,draw};})(globalThis);