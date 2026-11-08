(function(root){
 'use strict';
 let old=false,atlas,tiles,door;
 const images={};
 const loadImage=url=>new Promise((resolve,reject)=>{const a=new Image();a.onload=()=>resolve(a);a.onerror=()=>reject(Error(url));a.src=url;});
 function recolor(image,kind){
  const c=document.createElement('canvas');c.width=image.width;c.height=image.height;
  const g=c.getContext('2d',{willReadFrequently:true});g.drawImage(image,0,0);
  const im=g.getImageData(0,0,c.width,c.height),a=im.data;
  for(let i=0;i<a.length;i+=4){if(!a[i+3])continue;const r=a[i],b=a[i+2],green=a[i+1],hi=Math.max(r,green,b),lo=Math.min(r,green,b),l=.2126*r+.7152*green+.0722*b;
   // Warm masonry, steel frames and neutral packaging join material92.
   // Saturated sign/merch pixels retain hue, with only a small value change.
   const neutral=hi-lo<48||r>green*1.03&&green>=b&&hi-lo<78;
   const px=(i/4)%c.width,py=Math.floor(i/4/c.width);
   const awning=['cafe','goods-shop'].includes(kind)&&py>c.height*.26&&py<c.height*.54&&px>c.width*.1&&px<c.width*.9&&r>green*1.12&&green>b;
   const paper=['delivery-boxes','open-carton','paper-rubbish','poster-rolls','shopping-bags'].includes(kind)&&r>green&&green>b;
   if(awning){a[i]=r*.98;a[i+1]=green*.98;a[i+2]=b*.98;}
   else if(paper){a[i]=Math.min(255,l*1.08+5);a[i+1]=Math.min(255,l*.99+3);a[i+2]=Math.min(255,l*.86+4);}
   else if(neutral){a[i]=Math.min(255,l*.84+2);a[i+1]=Math.min(255,l*.99+4);a[i+2]=Math.min(255,l*1.08+7);}
   else{a[i]=r*.94;a[i+1]=green*.96;a[i+2]=b*.98;}
  }
  g.putImageData(im,0,0);return c;
 }
 function prepare(original){for(const p of root.MerchCatalog||[])images[p.id]=recolor(original[p.id],p.id);if(original.fence)images.fence=recolor(original.fence,'fence');}
 const dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
 function wall(ctx,cells,w,h,x,y,t,v=0){let mask=0;dirs.forEach(([dx,dy],bit)=>{const nx=x+dx,ny=y+dy;if(nx>=0&&ny>=0&&nx<w&&ny<h&&cells[ny*w+nx]===0)mask|=1<<bit;});ctx.drawImage(atlas,...tiles[`${mask}:${v}`],x*t,y*t,t,t);}
 async function load(){[tiles,atlas,door]=await Promise.all([fetch('wall92.json').then(r=>r.json()),loadImage('../native-play107/assets/wall.png'),loadImage('../basic-doors101/glass-double-closed32.png')]);}
 function exitDoor(ctx,d,t){ctx.drawImage(door,(d.x+1)*t,(d.y+1)*t,t,t);ctx.fillStyle='#b5d6df';ctx.fillRect((d.x+1)*t+t*.3,(d.y+1)*t-t*.12,t*.4,Math.max(1,t/16));}
 root.Market108={load,prepare,recolor,wall,exitDoor,images,isOld:()=>old,setOld:v=>old=Boolean(v)};
})(globalThis);
