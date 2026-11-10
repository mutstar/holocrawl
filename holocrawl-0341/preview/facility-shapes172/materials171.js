(async()=>{'use strict';
const load=async u=>{const im=new Image();im.src=u;await im.decode();return im;},cv=(w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h}),pixels=im=>{const c=cv(im.width,im.height),q=c.getContext('2d');q.drawImage(im,0,0);return q.getImageData(0,0,c.width,c.height).data;};
const [manifest,rects,planes,atlas]=await Promise.all([fetch('../facility-exteriors170/manifest.json').then(r=>r.json()),fetch('../wall-height121/rects121.json').then(r=>r.json()),fetch('../wall-height121/planes121.json').then(r=>r.json()),load('../wall-height121/wall22.png')]);
const textures={},dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]],cache=new Map(),outputs=[];
await Promise.all(['metal','brick','plaster','tile','concrete','rock'].map(async id=>{const im=await load('../facility-exteriors170/assets/'+id+'-native.png'),d=pixels(im);let sum=0;for(let i=0;i<d.length;i+=4)sum+=(d[i]+d[i+1]+d[i+2])/3;textures[id]={w:im.width,h:im.height,d,mean:sum/(im.width*im.height)};}));
function tile(mask,x,y,theme){const tex=textures[theme.material],key=JSON.stringify([mask,x%4,y%2,theme]);if(cache.has(key))return cache.get(key);const c=cv(32,32),q=c.getContext('2d');q.drawImage(atlas,...rects[mask+':0'],0,0,32,32);const a=q.getImageData(0,0,32,32),face=planes[String(mask)];
 for(let py=0;py<32;py++)for(let px=0;px<32;px++){const i=(py*32+px)*4,l=(a.data[i]+a.data[i+1]+a.data[i+2])/3;if(l<30||l>110)continue;const front=face[py*32+px]==='1',ti=((((y*32+py)%tex.h)*tex.w)+(x*32+px)%tex.w)*4,tl=(tex.d[ti]+tex.d[ti+1]+tex.d[ti+2])/3,delta=(tl-tex.mean)*(front?.62:.16),base=front?theme.face:theme.top;let col=base.map(v=>v+delta+(front?0:(l-39)*.12));
 if(front&&theme.wood&&py>=23){const seam=(x*32+px)%32===0;col=seam?[66,58,47]:[109+delta*.3,87+delta*.3,64+delta*.3];}
 if(front&&(py===11||py===29))col=theme.accent.map((v,k)=>v*.65+theme.face[k]*.35);
 if(front&&py===31)col=[61,67,65];
 for(let k=0;k<3;k++)a.data[i+k]=Math.max(0,Math.min(255,Math.round(col[k])));}
 q.putImageData(a,0,0);cache.set(key,c);return c;}
window.FacilityMaterial171={tile,atlas,rects,planes};window.material171Ready=true;})().catch(e=>{console.error(e);window.material171Error=e.message;});
