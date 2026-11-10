(function(root){'use strict';
function rect(q,color,x,y,w,h){q.fillStyle=color;q.fillRect(x,y,w,h);}
function plinth(q,x,y,w,h,top,trim){rect(q,'#17292d',x,y+2,w,h-1);rect(q,top,x+2,y,w-4,h-5);rect(q,'#435b60',x+2,y+h-5,w-4,4);rect(q,trim,x+2,y+h-6,w-4,1);rect(q,'#20383c',x,y+5,2,h-5);rect(q,'#61797a',x+w-2,y+4,2,h-4);}
function ground(q,m){
 // The approach becomes a broad floor runner, not a diagram connecting exhibits.
for(let y=5;y<=10;y++)for(let x=7;x<=9;x++){rect(q,'rgba(80,119,115,.22)',x*32,y*32,32,32);if(x===7)rect(q,'#52716f',x*32+2,y*32,1,32);if(x===9)rect(q,'#52716f',x*32+29,y*32,1,32);}
const s=m.fixtures.find(f=>f.id==='stage'),x=s.x*32,y=s.y*32,w=s.w*32,h=s.h*32;
plinth(q,x,y,w,h,'#31474c','#759b98');
// Shallow horizontal floor panels give the shared stage a single continuous surface.
for(let px=x+8;px<x+w-4;px+=32){rect(q,'#3c5357',px,y+4,1,h-12);rect(q,'#253d43',px+1,y+4,1,h-12);}
rect(q,'#5c7a7c',x+3,y,w-6,2);rect(q,'#20383f',x+3,y+2,w-6,2);
// Three central steps project only into the already passable main aisle.
for(let n=0;n<3;n++){rect(q,['#64817f','#526d70','#3d595f'][n],7*32,(s.y+s.h)*32-3+n*2,3*32,2);}
for(const f of m.fixtures.filter(f=>['workbench','reception'].includes(f.id))){const xx=f.x*32,yy=f.y*32,ww=f.w*32,hh=f.h*32;plinth(q,xx,yy,ww,hh,f.id==='workbench'?'#414c4f':'#526b6b',f.id==='workbench'?'#8d8274':'#8bb9b2');
// Back panel meets the wall/adjacent stage rather than leaving separate silhouettes floating.
rect(q,'#172e35',xx,yy,ww,8);rect(q,'#647a79',xx+1,yy,ww-2,2);for(let bx=xx+7;bx<xx+ww-4;bx+=16){rect(q,'#273c41',bx,yy+3,9,3);}
if(f.id==='reception'){rect(q,'#344e55',xx+3,yy+9,25,hh-16);for(const off of [13,29,45]){rect(q,'#788f8d',xx+5,yy+off,21,10);rect(q,'#263e47',xx+6,yy+off+2,19,7);rect(q,'#a7b9ae',xx+13,yy+off+3,6,1);}rect(q,'#8eb9b3',xx,yy+3,2,hh-7);}
}
}
function front(q,m){
const s=m.fixtures.find(f=>f.id==='stage'),sx=s.x*32,sy=(s.y+s.h)*32-6,sw=s.w*32;
rect(q,'#1c353c',sx,sy,sw,6);rect(q,'#7faaa5',sx+1,sy,sw-2,1);rect(q,'#475f63',sx+2,sy+2,sw-4,3);for(let dx=12;dx<sw-8;dx+=28){rect(q,'#223b43',sx+dx,sy+2,15,2);}
for(const f of m.fixtures.filter(f=>['workbench','reception'].includes(f.id))){const x=f.x*32,y=(f.y+f.h)*32-7,w=f.w*32;rect(q,'#1b2f35',x,y,w,7);rect(q,f.id==='workbench'?'#8d8274':'#8bb9b2',x,y,w,1);rect(q,'#3f555a',x+2,y+2,w-4,3);for(let dx=10;dx<w-8;dx+=22){rect(q,'#1b3037',x+dx,y+2,14,2);rect(q,'#80938e',x+dx+4,y+2,5,1);}}

}
root.FortuneFixtures166={ground,front};
})(globalThis);
