/* Existing native concrete wall geometry is the court boundary; these are ground details. */
(function(root){'use strict';
function paint(q,f,m,floors){const o=m.o,inside=(x,y)=>x>=0&&y>=0&&x<f.w&&y<f.h&&f.inside[y*f.w+x];
 // The access path uses the very same cement tiles as the street, at their world phase.
 const start=(o.y+f.oldEntry.y+f.contentShift[1]-1)*32+16,end=(m.entry.y+1)*32;
 q.save();q.beginPath();q.rect(m.entry.x*32,start,32,end-start);q.clip();
 for(let y=Math.floor(start/32);y<=m.entry.y;y++)q.drawImage(floors[RandomFloor.index('FACILITY171',0,m.entry.x,y)%floors.length],m.entry.x*32,y*32);q.restore();
 // Only paint inward from each grass edge, leaving the existing wall/coping untouched.
 for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(inside(x,y))for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]])if(!inside(x+dx,y+dy)){
  if(x+dx===f.entry.x&&y+dy===f.entry.y)continue;
  const px=(o.x+x)*32,py=(o.y+y)*32;
  q.fillStyle='#535f60';if(dx)q.fillRect(px+(dx>0?26:0),py,6,32);else q.fillRect(px,py+(dy>0?26:0),32,6);
  q.fillStyle='#788582';if(dx)q.fillRect(px+(dx>0?26:5),py,1,32);else q.fillRect(px,py+(dy>0?26:5),32,1);
  q.fillStyle='#65736f';if(dx)q.fillRect(px+(dx>0?27:1),py,4,32);else q.fillRect(px,py+(dy>0?27:1),32,4);
 }
}
root.CourtEdge173={paint};
})(globalThis);
