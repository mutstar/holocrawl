(function(){'use strict';
const cache=new Map(),theme={material:'metal',face:[66,68,87],top:[32,36,48],accent:[139,132,166]};
function tile(mask,x,y){
 const key=[mask,x%6,y%4].join(':');if(cache.has(key))return cache.get(key);
 const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');
 q.drawImage(FacilityMaterial171.tile(mask,x,y,theme),0,0);
 const pixels=q.getImageData(0,0,32,32),p=pixels.data,plane=FacilityMaterial171.planes[String(mask)];
 // Recolour native coping in place: its corners and edge coverage stay intact.
 for(let py=0;py<32;py++)for(let px=0;px<32;px++){
  const i=(py*32+px)*4,l=(p[i]+p[i+1]+p[i+2])/3;
  if(l>112){const col=l>140?[155,158,177]:[109,117,140];for(let k=0;k<3;k++)p[i+k]=col[k];}
  if(plane[py*32+px]!=='1')continue;
  // Panel joints and rivets remain on the vertical face, never on the floor.
  if((px===2||px===29)&&py>=14&&py<=26){p[i]=43;p[i+1]=47;p[i+2]=65;}
  if((px===5||px===26)&&(py===14||py===26)){p[i]=126;p[i+1]=134;p[i+2]=151;}
  if(py===18&&px>=9&&px<=22){p[i]=29;p[i+1]=34;p[i+2]=48;}
  if(py===19&&px>=10&&px<=21){const color=(x+y)%3===0?[179,108,154]:[103,174,184];for(let k=0;k<3;k++)p[i+k]=color[k];}
 }
 q.putImageData(pixels,0,0);cache.set(key,c);return c;
}
const glyphs={A:['01110','11011','11011','11111','11011','11011','11011'],R:['11110','11011','11011','11110','11100','11010','11011'],C:['01111','11000','11000','11000','11000','11000','01111'],D:['11110','11011','11011','11011','11011','11011','11110'],E:['11111','11000','11000','11110','11000','11000','11111']};
function fascia(q,m){
 // A flush 3-tile panel on the rear wall's22px face; no overhead prop.
 const x=(m.origin.x+9)*32-7,y=m.origin.y*32+11;
 const f=(col,a,b,w,h)=>{q.fillStyle=col;q.fillRect(x+a,y+b,w,h);};
 f('#232a3a',0,0,94,20);f('#8c91ac',0,0,94,1);f('#555e7b',0,19,94,1);f('#46445e',1,1,92,18);
 f('#212738',3,3,88,14);f('#75bbc5',3,3,2,14);f('#bd7da6',89,3,2,14);
 let dx=12;for(const letter of 'ARCADE'){const g=glyphs[letter];for(let yy=0;yy<7;yy++)for(let xx=0;xx<5;xx++)if(g[yy][xx]==='1')f(letter==='A'||letter==='E'?'#c7a5c7':'#a8d3d3',dx+xx*2,3+yy*2,2,2);dx+=12;}
}
window.ArcadeWall192={tile,fascia,theme};
})();
