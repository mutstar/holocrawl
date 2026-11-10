/* Existing native concrete wall geometry is the court boundary; these are ground details. */
(function(root){'use strict';
function paint(q,f,m,floors){const o=m.o,inside=(x,y)=>x>=0&&y>=0&&x<f.w&&y<f.h&&f.inside[y*f.w+x];
 // Only paint inward from each grass edge, leaving the existing wall/coping untouched.
 for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(inside(x,y))for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]])if(!inside(x+dx,y+dy)){
  if(x+dx===f.entry.x&&y+dy===f.entry.y)continue;
  const px=(o.x+x)*32,py=(o.y+y)*32;
  q.fillStyle='#535f60';if(dx)q.fillRect(px+(dx>0?26:0),py,6,32);else q.fillRect(px,py+(dy>0?26:0),32,6);
  q.fillStyle='#788582';if(dx)q.fillRect(px+(dx>0?26:5),py,1,32);else q.fillRect(px,py+(dy>0?26:5),32,1);
  q.fillStyle='#65736f';if(dx)q.fillRect(px+(dx>0?27:1),py,4,32);else q.fillRect(px,py+(dy>0?27:1),32,4);
 }
}
root.CourtEdge174={paint};
})(globalThis);
