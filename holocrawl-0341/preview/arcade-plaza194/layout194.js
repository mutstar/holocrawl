(function(){'use strict';
function generate(mode){const m=ArcadeLayout191.generate(mode);m.sideWallCaps=[];
 for(const e of m.entrances.slice(1))for(const dy of [-1,1]){const x=e.x,y=e.y+dy,i=y*m.w+x;m.cells[i]=0;m.building[i]=true;m.open[i]=0;m.sideWallCaps.push({x,y});}
 m.openings=m.openings.filter(p=>!m.sideWallCaps.some(c=>c.x===p.x&&c.y===p.y));
 m.doors=[{id:'main',x:m.entry.x-1,y:m.entry.y,w:3,h:1},...m.entrances.slice(1).map((e,i)=>({id:i?'right':'left',x:e.x,y:e.y,w:1,h:1}))];return m;
}
window.ArcadeLayout194={generate,distances:ArcadeLayout191.distances,dirs:ArcadeLayout191.dirs};})();
