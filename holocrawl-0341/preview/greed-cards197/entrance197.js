(function(){'use strict';
const glyph={C:['01111','11000','11000','11000','11000','11000','01111'],A:['01110','11011','11011','11111','11011','11011','11011'],S:['01111','11000','11000','01110','00011','00011','11110'],I:['111','010','010','010','010','010','111'],N:['11001','11001','11101','10111','10011','10011','10011'],O:['01110','11011','11011','11011','11011','11011','01110']};
function suit(q,x,y,type,color){q.fillStyle=color;const f=(a,b,w,h)=>q.fillRect(x+a,y+b,w,h);if(type==='diamond'){f(3,0,2,2);f(1,2,6,4);f(3,6,2,2);}else if(type==='heart'){f(0,0,3,3);f(5,0,3,3);f(1,2,6,3);f(2,5,4,1);f(3,6,2,2);}else if(type==='club'){f(2,0,4,3);f(0,3,4,3);f(4,3,4,3);f(3,5,2,3);}else{f(3,0,2,2);f(1,2,6,2);f(0,4,8,2);f(3,5,2,3);}}
function fixtures(q,m){GreedFixtures196.fixtures(q,m);const x=m.entry.x*32,y=m.entry.y*32,f=(c,a,b,w,h)=>{q.fillStyle=c;q.fillRect(x+a,y+b,w,h);};
 // Both plaques sit on the vertical faces of the existing entrance wall tiles.
 for(const a of [-30,76]){f('#302b35',a,12,18,18);f('#9c865e',a,12,18,1);f('#6c5a4a',a,29,18,1);}
 suit(q,x-29,y+17,'spade','#d1c3a0');suit(q,x-21,y+17,'heart','#ad6c79');suit(q,x+77,y+17,'diamond','#ad6c79');suit(q,x+85,y+17,'club','#d1c3a0');
 for(const a of [-10,64]){f('#34313b',a,10,10,22);f('#ac956a',a+1,10,8,20);f('#63523f',a+3,11,4,18);f('#dcc596',a+2,10,6,1);for(const b of [14,21,27])f('#d3bd8c',a+4,b,2,2);f('#463b37',a,30,10,2);}
}
function runner(q,m){const x=m.entry.x*32,y=(m.entry.y+1)*32;q.fillStyle='#49313a';q.fillRect(x+3,y,58,28);q.fillStyle='#714452';q.fillRect(x+5,y,54,26);q.fillStyle='#ad926b';q.fillRect(x+4,y,1,26);q.fillRect(x+59,y,1,26);q.fillRect(x+5,y+25,54,1);q.fillStyle='#8e6a5d';for(let a=7;a<58;a+=4)q.fillRect(x+a,y+27,2,2);}
function door(q,m,opened){const x=m.entry.x*32,y=m.entry.y*32,f=(c,a,b,w,h)=>{q.fillStyle=c;q.fillRect(x+a,y+b,w,h);};
 // The marquee and door still fit the accepted32px total tile height.
 f('#342c34',0,0,64,10);f('#bc9d68',0,0,64,1);f('#6d5545',0,1,64,9);f('#292731',2,2,60,7);f('#d4bc8c',0,9,64,1);
 let tx=16;for(const c of 'CASINO'){const g=glyph[c];q.fillStyle='#e0cb9d';for(let yy=0;yy<7;yy++)for(let xx=0;xx<g[yy].length;xx++)if(g[yy][xx]==='1')q.fillRect(x+tx+xx,y+2+yy,1,1);tx+=g[0].length+1;}
 for(const a of [5,11,52,58])f('#e0c38b',a,4,2,2);
 f('#c8ac78',0,10,3,20);f('#c8ac78',61,10,3,20);f('#65503f',3,10,2,20);f('#65503f',59,10,2,20);
 // A closed pair of burgundy panels; the open state reveals the original floor.
 if(!opened){for(let n=0;n<2;n++){const a=5+n*27;f('#573241',a,10,27,20);f('#955c6a',a+1,11,25,1);f('#3f2c37',a+1,12,25,17);f('#6d3e4e',a+2,13,23,15);f('#b59766',a+6,13,14,14);f('#dacead',a+7,14,12,12);suit(q,x+a+9,y+16,n?'diamond':'spade',n?'#9b4c5b':'#2c303a');f('#b4a07d',a+22,19,2,6);f('#1f242f',31,10,2,20);}}else{
 f('#6d3e4e',5,10,3,20);f('#6d3e4e',56,10,3,20);
 }
 f('#8d7860',0,30,64,1);f('#48444a',0,31,64,1);
}
window.CasinoEntrance197={tile:GreedFixtures196.tile,fixtures,runner,door,collision:GreedFixtures196.collision};})();
