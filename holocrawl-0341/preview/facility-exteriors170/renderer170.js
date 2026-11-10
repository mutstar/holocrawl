(async()=>{'use strict';
const load=async u=>{const im=new Image();im.src=u;await im.decode();return im;},cv=(w,h)=>Object.assign(document.createElement('canvas'),{width:w,height:h}),pixels=im=>{const c=cv(im.width,im.height),q=c.getContext('2d');q.drawImage(im,0,0);return q.getImageData(0,0,c.width,c.height).data;};
const [manifest,rects,planes,atlas]=await Promise.all([fetch('manifest.json').then(r=>r.json()),fetch('../wall-height121/rects121.json').then(r=>r.json()),fetch('../wall-height121/planes121.json').then(r=>r.json()),load('../wall-height121/wall22.png')]);
const textures={},dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]],cache=new Map(),outputs=[];
await Promise.all(['metal','brick','plaster','tile','concrete','rock'].map(async id=>{const im=await load('assets/'+id+'-native.png'),d=pixels(im);let sum=0;for(let i=0;i<d.length;i+=4)sum+=(d[i]+d[i+1]+d[i+2])/3;textures[id]={w:im.width,h:im.height,d,mean:sum/(im.width*im.height)};}));
function tile(mask,x,y,theme){const tex=textures[theme.material],key=JSON.stringify([mask,x%4,y%2,theme]);if(cache.has(key))return cache.get(key);const c=cv(32,32),q=c.getContext('2d');q.drawImage(atlas,...rects[mask+':0'],0,0,32,32);const a=q.getImageData(0,0,32,32),face=planes[String(mask)];
 for(let py=0;py<32;py++)for(let px=0;px<32;px++){const i=(py*32+px)*4,l=(a.data[i]+a.data[i+1]+a.data[i+2])/3;if(l<30||l>110)continue;const front=face[py*32+px]==='1',ti=((((y*32+py)%tex.h)*tex.w)+(x*32+px)%tex.w)*4,tl=(tex.d[ti]+tex.d[ti+1]+tex.d[ti+2])/3,delta=(tl-tex.mean)*(front?.62:.16),base=front?theme.face:theme.top;let col=base.map(v=>v+delta+(front?0:(l-39)*.12));
 if(front&&theme.wood&&py>=23){const seam=(x*32+px)%32===0;col=seam?[66,58,47]:[109+delta*.3,87+delta*.3,64+delta*.3];}
 if(front&&(py===11||py===29))col=theme.accent.map((v,k)=>v*.65+theme.face[k]*.35);
 if(front&&py===31)col=[61,67,65];
 for(let k=0;k<3;k++)a.data[i+k]=Math.max(0,Math.min(255,Math.round(col[k])));}
 q.putImageData(a,0,0);cache.set(key,c);return c;}
for(const m of manifest.maps){const [data,closed,opened,decal]=await Promise.all([fetch(m.sourceMap).then(r=>r.json()),load(m.sourceClosed),load(m.sourceOpen),load(m.decal)]),o=m.origin,rows=data.rows,visual=rows.map(r=>r.split(''));
 for(let y=1;y<o.height-1;y++)for(let x=1;x<o.width-1;x++)if('#G'.includes(visual[o.y+y][o.x+x]))visual[o.y+y][o.x+x]='.';
 const shell=[];for(let y=0;y<o.height;y++)for(let x=0;x<o.width;x++)if(rows[o.y+y][o.x+x]==='#'&&(x===0||y===0||x===o.width-1||y===o.height-1)){const gx=o.x+x,gy=o.y+y;let mask=0;dirs.forEach(([dx,dy],i)=>{const xx=gx+dx,yy=gy+dy;if(yy>=0&&yy<visual.length&&xx>=0&&xx<visual[yy].length&&'#+G'.includes(visual[yy][xx]))mask|=1<<i;});shell.push({x:x+1,y:y+1,gx,gy,mask});}
 // The outdoor ground has a fence, not a masonry perimeter. Keep every fence pixel;
 // theme only the already existing dungeon walls in its one-cell context margin.
 if(m.facility==='fantasy')for(let y=-1;y<=o.height;y++)for(let x=-1;x<=o.width;x++){if(x!==-1&&y!==-1&&x!==o.width&&y!==o.height)continue;const gx=o.x+x,gy=o.y+y;if(rows[gy]?.[gx]!=='#')continue;let mask=0;dirs.forEach(([dx,dy],i)=>{const xx=gx+dx,yy=gy+dy;if(visual[yy]?.[xx]&&'#+G'.includes(visual[yy][xx]))mask|=1<<i;});shell.push({x:x+1,y:y+1,gx,gy,mask,context:true});}
 const rendered={};for(const [state,im]of [['closed',closed],['open',opened]]){const c=cv(im.width,im.height),q=c.getContext('2d');q.imageSmoothingEnabled=false;q.drawImage(im,0,0);for(const s of shell)q.drawImage(tile(s.mask,s.gx,s.gy,m.theme),s.x*32,s.y*32);q.drawImage(decal,32,32);rendered[state]=c;}
 const before=pixels(closed),after=pixels(rendered.closed);let changed=0,outside=0,doorChanges=0;const mask=new Uint8Array(closed.width*closed.height);for(const s of shell)for(let py=0;py<32;py++)mask.fill(1,(s.y*32+py)*closed.width+s.x*32,(s.y*32+py)*closed.width+s.x*32+32);
 for(let i=0;i<mask.length;i++)if([0,1,2,3].some(k=>before[i*4+k]!==after[i*4+k])){changed++;if(!mask[i])outside++;}
 for(const d of m.facilityDoors){const x=(d.x-o.x+1)*32,y=(d.y-o.y+1)*32;for(let py=0;py<32;py++)for(let px=0;px<d.width*32;px++){const i=((y+py)*closed.width+x+px)*4;if([0,1,2,3].some(k=>before[i+k]!==after[i+k]))doorChanges++;}}
 const members=m.memberDetails.map(member=>{let box=member.box;if(!box&&member.cell){const[x,y]=member.cell,[w,h]=member.size;box=[x*32,y*32,(x+w)*32,(y+h)*32];}if(!box)return{id:member.id,checked:false};let diff=0;for(let y=box[1]+32;y<box[3]+32;y++)for(let x=box[0]+32;x<box[2]+32;x++){const i=(y*closed.width+x)*4;if([0,1,2,3].some(k=>before[i+k]!==after[i+k]))diff++;}return{id:member.id,diff};});
 const section=document.createElement('section'),h=document.createElement('h2');h.textContent=m.name+' · '+m.theme.label;section.append(h,rendered.closed);document.getElementById('fields').append(section);
 outputs.push({id:m.facility,name:m.name,theme:m.theme,shell,rendered,checks:{changedPixels:changed,changedOutsideShell:outside,doorPixelChanges:doorChanges,memberDetails:members}});
}
document.getElementById('status').textContent='9곳 렌더 완료 · 지형과 내부 보존';window.FacilityExteriors170={outputs,manifest,tile,textures,atlas,rects};window.exteriors170Ready=true;
})().catch(e=>{document.getElementById('status').textContent=e.message;console.error(e);});
