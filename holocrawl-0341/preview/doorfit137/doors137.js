(function(root){'use strict';const maps=new WeakMap();
function solids(m){if(maps.has(m))return maps.get(m);const a=Uint8Array.from(m.cells);for(const d of m.doors)if(!d.home&&direction(m,d)==='horizontal')a[d.y*m.w+d.x]=0;maps.set(m,a);return a;}
function direction(m,d){const wall=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]===0;return wall(d.x-1,d.y)&&wall(d.x+1,d.y)?'horizontal':'vertical';}
function draw(q,m,d,opened,im,base){const x=d.x*32,y=d.y*32;
 if(direction(m,d)==='vertical'){q.fillStyle='#2d3b39';q.fillRect(x,y,32,32);q.drawImage(base,x+2,y+2,28,28,x+2,y+2,28,28);q.fillStyle='#859791';q.fillRect(x,y,32,2);q.fillRect(x,y,2,32);q.fillRect(x+30,y,2,32);q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+2,y,28,32);return;}
 // Ordinary doors are structural openings. Include them when adjoining wall silhouettes are selected.
 WallHeight121.wall(q,solids(m),m.w,m.h,d.x,d.y,32,0);
 // Cut the aperture back to the original floor, retaining the wall shoulders and lintel.
 q.drawImage(base,x+4,y+11,24,21,x+4,y+11,24,21);
 q.fillStyle='#273431';q.fillRect(x+2,y+10,2,22);q.fillRect(x+28,y+10,2,22);
 q.fillStyle='#859791';q.fillRect(x+3,y+10,1,22);q.fillRect(x+28,y+10,1,22);
 q.drawImage(opened?im.opened:im.closed,0,0,32,32,x+3,y+10,26,22);
}
root.DoorFit137={solids,direction,draw};})(globalThis);