(function(root){
 'use strict';
 let atlas,rects,lookup,pending;
 const dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]],front=10;
 async function load(){if(pending)return pending;pending=Promise.all([fetch('../wall-height121/rects121.json').then(r=>r.json()),fetch('../wall-height121/native-lookup121.json').then(r=>r.json()),new Promise((r,j)=>{const im=new Image();im.onload=()=>r(im);im.onerror=j;im.src='../wall-height121/wall22.png';})]).then(a=>{[rects,lookup,atlas]=a;});return pending;}
 function wall(ctx,cells,w,h,x,y,t,v=0){let mask=0;dirs.forEach(([dx,dy],bit)=>{const nx=x+dx,ny=y+dy;if(nx>=0&&ny>=0&&nx<w&&ny<h&&cells[ny*w+nx]===0)mask|=1<<bit;});ctx.drawImage(atlas,...rects[`${mask}:${v}`],x*t,y*t,t,t);}
 function nativeTile(ctx,t,x,y,s){if(t.atlas!=='wall')return false;const r=lookup[`${t.sx},${t.sy}`];if(!r)return false;ctx.drawImage(atlas,...r,x,y,32*s,32*s);return true;}
 function dims(m){return[m.width||m.w,m.height||m.h];}
 function solid(m,x,y){const[w,h]=dims(m);return x>=0&&y>=0&&x<w&&y<h&&(m.rows?'#+G'.includes(m.rows[y][x]):m.cells[y*w+x]===0);}
 function isWall(m,x,y){const[w,h]=dims(m);return x>=0&&y>=0&&x<w&&y<h&&(m.rows?m.rows[y][x]==='#':m.cells[y*w+x]===0);}
 function frontPixel(m,x,y,px,py){if(!isWall(m,x,y)||solid(m,x,y+1)||py<front||py>31)return false;return solid(m,x+1,y)||px<29+Math.floor((py-front)*3/21);}
 function allowed(m,f,x,y){return y>=front+1&&y<=30&&frontPixel(m,f.x+Math.floor(x/32),f.y,x%32,y);}
 function installMarket(){Market108.wall=wall;}
 root.WallHeight121={load,wall,nativeTile,solid,isWall,frontPixel,allowed,installMarket,front,height:22};
})(globalThis);
