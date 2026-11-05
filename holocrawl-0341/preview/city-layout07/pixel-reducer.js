(function(root){
'use strict';
function bounds(image,threshold=200){let x0=image.width,y0=image.height,x1=-1,y1=-1;for(let y=0;y<image.height;y++)for(let x=0;x<image.width;x++)if(image.data[(y*image.width+x)*4+3]>threshold){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}if(x1<0)throw Error('Empty sprite');return{x:x0,y:y0,w:x1-x0+1,h:y1-y0+1};}
// Premultiplied-alpha area integration avoids missing thin features during reduction.
function area(image,width,height,rect={x:0,y:0,w:image.width,h:image.height}){
 const out={width,height,data:new Uint8ClampedArray(width*height*4)},sx=rect.w/width,sy=rect.h/height;
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
   const left=rect.x+x*sx,right=left+sx,top=rect.y+y*sy,bottom=top+sy;let a=0,r=0,g=0,b=0;
   for(let yy=Math.floor(top);yy<Math.ceil(bottom);yy++)for(let xx=Math.floor(left);xx<Math.ceil(right);xx++){
     if(xx<0||yy<0||xx>=image.width||yy>=image.height)continue;
     const weight=(Math.min(right,xx+1)-Math.max(left,xx))*(Math.min(bottom,yy+1)-Math.max(top,yy)),i=(yy*image.width+xx)*4,alpha=image.data[i+3]*weight;
     a+=alpha;r+=image.data[i]*alpha;g+=image.data[i+1]*alpha;b+=image.data[i+2]*alpha;
   }
   const i=(y*width+x)*4;if(a>0){out.data[i]=r/a;out.data[i+1]=g/a;out.data[i+2]=b/a;out.data[i+3]=a/(sx*sy);}
 }
 return out;
}
function quantize(image,count=18,alphaCutoff=92){
 const out={width:image.width,height:image.height,data:new Uint8ClampedArray(image.data)},hist=new Map();
 for(let i=0;i<out.data.length;i+=4){if(out.data[i+3]<alphaCutoff){out.data.fill(0,i,i+4);continue;}out.data[i+3]=255;const c=[out.data[i],out.data[i+1],out.data[i+2]],key=c.join(',');if(!hist.has(key))hist.set(key,{c,n:0});hist.get(key).n++;}
 const points=[...hist.values()].sort((a,b)=>b.n-a.n);if(!points.length)return out;
 const distance=(a,b)=>(a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2;
 const palette=[points[0].c.slice()];
 while(palette.length<Math.min(count,points.length)){let best=null,score=-1;for(const p of points){const s=Math.min(...palette.map(c=>distance(p.c,c)))*Math.sqrt(p.n);if(s>score){best=p.c;score=s;}}palette.push(best.slice());}
 for(let round=0;round<8;round++){
   const bins=palette.map(()=>[0,0,0,0]);for(const p of points){let k=0,d=Infinity;palette.forEach((c,i)=>{const next=distance(p.c,c);if(next<d){d=next;k=i;}});for(let j=0;j<3;j++)bins[k][j]+=p.c[j]*p.n;bins[k][3]+=p.n;}
   palette.forEach((c,i)=>{if(bins[i][3])for(let j=0;j<3;j++)c[j]=Math.round(bins[i][j]/bins[i][3]);});
 }
 for(let i=0;i<out.data.length;i+=4){if(!out.data[i+3])continue;const c=[out.data[i],out.data[i+1],out.data[i+2]];let best=palette[0],d=Infinity;for(const p of palette){const next=distance(c,p);if(next<d){best=p;d=next;}}out.data.set(best,i);}
 return out;
}
function contrast(image,strength=.3){
 const out={width:image.width,height:image.height,data:new Uint8ClampedArray(image.data)};
 for(let y=0;y<image.height;y++)for(let x=0;x<image.width;x++){
   const i=(y*image.width+x)*4;if(image.data[i+3]<92)continue;const total=[0,0,0];let count=0;
   for(const[dx,dy]of [[-1,0],[1,0],[0,-1],[0,1]]){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=image.width||ny>=image.height)continue;const n=(ny*image.width+nx)*4;if(image.data[n+3]<92)continue;for(let c=0;c<3;c++)total[c]+=image.data[n+c];count++;}
   if(count)for(let c=0;c<3;c++)out.data[i+c]=image.data[i+c]+strength*(image.data[i+c]-total[c]/count);
 }
 return out;
}
function read(image){const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);return ctx.getImageData(0,0,canvas.width,canvas.height);}
function canvas(image){const c=document.createElement('canvas');c.width=image.width;c.height=image.height;c.getContext('2d').putImageData(new ImageData(image.data,image.width,image.height),0,0);return c;}
const api={bounds,area,contrast,quantize,read,canvas};root.PixelReducer=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
