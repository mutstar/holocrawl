/* Small native-pixel entrance fitted to the existing one-tile passage. */
(function(root){'use strict';
function prepare(f,a){const [sx,sy]=f.sourceOffset;
 for(const state of ['sourceClosedClean','sourceOpenClean']){const c=a[state],q=c.getContext('2d'),d=q.getImageData(0,0,c.width,c.height);
  // Remove the old gray wedge/shadow beneath the track; keep its beige running surface.
  for(let y=(f.oldEntry.y-1)*32;y<f.oldEntry.y*32;y++)for(let x=f.oldEntry.x*32;x<(f.oldEntry.x+1)*32;x++){const i=((sy+y)*c.width+sx+x)*4,r=d.data[i],g=d.data[i+1],b=d.data[i+2];if(r>65&&g>65&&b>50&&Math.abs(r-g)<12&&r-b<35)d.data[i+3]=0;}
  q.putImageData(d,0,0);
 }
}
function paint(q,f,m){const x=m.entry.x*32,y=m.entry.y*32,join=(m.o.y+f.contentShift[1]+f.oldEntry.y-1)*32-6;
 // A narrow dirt approach grows directly from the running track; marks begin below the junction.
 const shades=['#978169','#9b836a','#a08971','#9d876e'];
 for(let yy=join;yy<y+29;yy++)for(let xx=x+6;xx<x+26;xx++){q.fillStyle=shades[((xx*13+yy*7)>>>1)%4];q.fillRect(xx,yy,1,1);}
 q.fillStyle='#c5b597';q.fillRect(x+6,join+8,1,y+29-join-8);q.fillRect(x+25,join+8,1,y+29-join-8);
 // The sill stays inside the original wall tile and meets the street at the same level.
 q.fillStyle='#7d8b87';q.fillRect(x+2,y+29,28,1);q.fillStyle='#5c6e6d';q.fillRect(x+2,y+30,28,1);q.fillStyle='#384a4e';q.fillRect(x+2,y+31,28,1);
 // Posts sit on the two existing wall cells, leaving all32px of passage available.
 for(const px of [x-6,x+32]){q.fillStyle='#33474d';q.fillRect(px,y+3,6,29);q.fillStyle='#5c7377';q.fillRect(px+1,y+5,4,25);q.fillStyle='#8d9a96';q.fillRect(px,y+3,6,3);q.fillStyle='#b0bcb5';q.fillRect(px,y+3,6,1);q.fillStyle='#a0aaa3';q.fillRect(px+1,y+6,1,23);q.fillStyle='#394e53';q.fillRect(px,y+30,6,2);}
}
root.CourtEntrance174={prepare,paint};
})(globalThis);
