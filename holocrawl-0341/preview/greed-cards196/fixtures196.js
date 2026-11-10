(function(){'use strict';
function fixtures(q,m){GreedFixtures195.fixtures(q,{...m,furniture:m.furniture.filter(p=>p.id!=='lectern')});const f=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
 function eye(x,y){f('#aa8950',x+3,y,12,2);f('#d0b775',x+1,y+2,16,2);f('#c7ab67',x,y+4,18,2);f('#d0b775',x+1,y+6,16,2);f('#aa8950',x+3,y+8,12,2);f('#252632',x+5,y+2,8,6);f('#e4c986',x+7,y+2,4,6);f('#292735',x+8,y+2,2,6);}
 // Member emblems belong to the existing wall face and safe hardware.
 const px=(m.origin.x+6)*32,py=m.origin.y*32;f('#292a35',px-9,py+11,50,20);f('#a79a7e',px-9,py+11,50,1);f('#5a5354',px-9,py+30,50,1);f('#d0c6b0',px-5,py+16,9,10);f('#32323e',px+28,py+16,9,10);eye(px+7,py+16);
 for(const p of m.furniture){const x=p.x*32,y=p.y*32;if(p.id==='safe'){f('#3c424b',x+6,y+7,19,18);eye(x+6,y+11);}else if(p.id==='chair'){f('#252832',x+10,y+12,6,13);f('#c5bcaa',x+16,y+12,6,13);f('#938d86',x+10,y+24,12,1);}else if(p.id==='lectern'){
 f('#232730',x+5,y+27,23,4);f('#59474c',x+13,y+14,5,15);f('#9a8c6b',x+12,y+24,7,2);f('#443b41',x+3,y+9,26,12);f('#d3c7ac',x+4,y+8,11,11);f('#eee1c6',x+5,y+8,9,2);f('#c1b69e',x+16,y+8,11,11);f('#e1d3b8',x+17,y+8,9,2);f('#7f7567',x+15,y+9,1,11);f('#948c7b',x+6,y+13,7,1);f('#948c7b',x+18,y+13,7,1);f('#252833',x+24,y+3,4,12);f('#31333f',x+22,y+5,4,6);f('#b09c71',x+23,y+14,2,5);f('#e4d7bc',x+24,y+18,4,3);
 }}
}
window.GreedFixtures196={tile:GreedFixtures195.tile,fixtures,door:GreedFixtures195.door,collision:GreedFixtures195.collision};})();
