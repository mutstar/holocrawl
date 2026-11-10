(function(){'use strict';function fixtures(q,m){RavenFixtures199.fixtures(q,{...m,furniture:m.furniture.filter(p=>p.id!=='score')});const f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);},o=m.origin;
for(const p of m.furniture)if(p.id==='score'){const x=p.x*32,y=p.y*32;f('#202939',x+5,y+27,23,4);f('#62748e',x+14,y+14,3,15);f('#283348',x+3,y+6,26,16);f('#ddd9c8',x+5,y+7,22,12);f('#aaaeb6',x+15,y+7,1,12);for(const row of [11,14,17]){f('#7b8190',x+6,y+row,7,1);f('#7b8190',x+18,y+row,7,1);}f('#313a4c',x+10,y+9,1,7);f('#313a4c',x+8,y+14,3,2);f('#313a4c',x+21,y+8,1,7);f('#313a4c',x+19,y+13,3,2);f('#668abe',x+24,y+7,2,5);}
// A new flush plaque covers the old one, within the actual22px wall face.
const x=(o.x+10)*32+8,y=o.y*32+11;f('#242e42',x,y,80,20);f('#8e9fb9',x,y,80,1);f('#4d6386',x,y+19,80,1);
// One long horn and one short, squared horn echo Nerissa's asymmetric silhouette.
f('#93a6c8',x+8,y+3,3,3);f('#5f77a1',x+6,y+6,3,5);f('#334969',x+9,y+9,8,6);f('#1f2838',x+10,y+7,4,7);f('#8e9fb9',x+60,y+9,7,3);f('#425978',x+59,y+12,8,4);
for(const [dx,dy,w]of [[19,9,12],[17,11,12],[15,13,11]]){f('#456da6',x+dx,y+dy,w,2);f('#7899cb',x+dx+2,y+dy,w-5,1);}f('#aebed7',x+40,y+4,2,11);f('#aebed7',x+41,y+4,10,2);f('#aebed7',x+49,y+4,2,9);f('#cad4e2',x+35,y+13,7,3);f('#cad4e2',x+44,y+11,7,3);
// Penlights belong to a small interior wall holder, not a new floor obstacle.
const bx=(o.x+7)*32,by=(o.y+1)*32+12;f('#263348',bx+1,by,30,19);f('#7e91ad',bx+1,by,30,1);for(let i=0;i<3;i++){const px=bx+6+i*8;f('#596c88',px,by+11,3,7);f(['#789dd6','#d1d8e3','#577db8'][i],px-1,by+4,5,8);f('#abc1e0',px,by+4,3,1);}f('#485d7b',bx+2,by+17,28,2);
}
window.RavenFixtures200={tile:RavenFixtures199.tile,flooring:RavenFixtures199.flooring,fixtures,door:RavenFixtures199.door,collision:RavenFixtures199.collision};})();
