(function(){'use strict';const cache=new Map();
function tile(mask,x,y,inward){if(!inward)return CasinoEntrance197.tile(mask,x,y);const key=[mask,x%4,y%2].join(':');if(cache.has(key))return cache.get(key);const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');q.drawImage(CasinoEntrance197.tile(mask,x,y),0,0);const a=q.getImageData(0,0,32,32),plane=FacilityMaterial171.planes[String(mask)];
 for(let py=21;py<=29;py++)for(let px=0;px<32;px++){if(plane[py*32+px]!=='1')continue;const i=(py*32+px)*4,col=py===21?[139,117,91]:py===29?[65,45,54]:px===1||px===30?[69,47,57]:[94+(px+y)%3,60+(px+y)%3,73+(px+y)%3];for(let k=0;k<3;k++)a.data[i+k]=col[k];}q.putImageData(a,0,0);cache.set(key,c);return c;}
function rug(q,m){const x=(m.origin.x+4)*32,y=(m.origin.y+5)*32,f=(col,a,b,w,h)=>{q.fillStyle=col;q.fillRect(x+a,y+b,w,h);};
 f('#482f3b',4,4,152,120);f('#683c4d',7,7,146,114);for(let py=11;py<119;py+=4)for(let px=11;px<151;px+=4)if((px*13+py*7)%19<4)f('#6d4050',px,py,1,1);
 f('#ad926b',5,4,150,1);f('#ad926b',5,122,150,1);f('#ad926b',4,5,1,117);f('#ad926b',155,5,1,117);f('#8d6a5d',8,8,144,1);f('#8d6a5d',8,118,144,1);f('#8d6a5d',8,9,1,109);f('#8d6a5d',151,9,1,109);
}
function fixtures(q,m){CasinoEntrance197.fixtures(q,m);const f=(col,x,y,w,h)=>{q.fillStyle=col;q.fillRect(x,y,w,h);};for(const p of m.furniture){const x=p.x*32,y=p.y*32;if(p.id==='chair'){f('#6d3e4e',x+10,y+12,12,13);f('#2a2c35',x+10,y+12,2,12);f('#c8bfad',x+20,y+12,2,12);f('#8e5c6d',x+12,y+13,8,2);f('#462f3b',x+12,y+23,8,2);}else if(p.id==='bench'){f('#714452',x+5,y+13,54,8);f('#956573',x+5,y+13,54,2);f('#51343f',x+5,y+20,54,2);f('#c1b59d',x+5,y+15,1,5);f('#302b34',x+58,y+15,1,5);}}
}
window.WineRoom198={tile,rug,fixtures,runner:CasinoEntrance197.runner,door:CasinoEntrance197.door,collision:CasinoEntrance197.collision};})();
