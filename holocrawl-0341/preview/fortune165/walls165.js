(function(root){'use strict';let atlas,rects,planes,pending;const cache=new Map(),dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function load(){if(pending)return pending;return pending=Promise.all([new Promise((r,j)=>{const im=new Image();im.onload=()=>r(im);im.onerror=j;im.src='../wall-height121/wall22.png';}),fetch('../wall-height121/rects121.json').then(r=>r.json()),fetch('../wall-height121/planes121.json').then(r=>r.json())]).then(([a,r,p])=>{atlas=a;rects=r;planes=p;});}
function maskAt(cells,w,h,x,y){let n=0;dirs.forEach(([dx,dy],i)=>{const xx=x+dx,yy=y+dy;if(xx>=0&&yy>=0&&xx<w&&yy<h&&cells[yy*w+xx]===0)n|=1<<i;});return n;}
function tile(mask,x,y){const phase=(x+2*y)%4,key=mask+':'+phase;if(cache.has(key))return cache.get(key);const c=document.createElement('canvas');c.width=c.height=32;const q=c.getContext('2d');q.drawImage(atlas,...rects[mask+':0'],0,0,32,32);const a=q.getImageData(0,0,32,32),front=planes[String(mask)];
for(let py=0;py<32;py++)for(let px=0;px<32;px++){const i=(py*32+px)*4;if(!a.data[i+3])continue;const l=(a.data[i]+a.data[i+1]+a.data[i+2])/3;let color;
if(l<30)color=[25,35,41];else if(l>110)color=l>136?[164,193,187]:[115,153,150];else if(front[py*32+px]==='1'){const v=100+Math.round(l/6)*2;color=[v,v+9,v+7];if((py===17||py===27)&&px>3&&px<28)color=[83,105,105];if(phase===0&&py>=12&&py<=14&&px>=12&&px<=18)color=[88,175,166];}else{const v=Math.round(l/8);color=[30+v,45+v,52+v];}for(let k=0;k<3;k++)a.data[i+k]=color[k];}
q.putImageData(a,0,0);cache.set(key,c);return c;}
function wall(q,cells,w,h,x,y,t=32){q.drawImage(tile(maskAt(cells,w,h,x,y),x,y),x*t,y*t,t,t);}
root.FortuneWall165={load,wall,tile,maskAt};
})(globalThis);
