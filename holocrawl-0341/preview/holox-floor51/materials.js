// Iron plate material; same neighbour-driven bevel construction as city-batch22/connectedWallSprite.
// Only wall cells are painted. The original city floor remains untouched.
const LabMaterials={objectBrightness:1.25,objectSaturation:1.15,cache:new Map(),
 mask(map,x,y){
  const solid=(x,y)=>x<0||y<0||x>=map.w||y>=map.h||['#','+'].includes(map.rows[y][x]);
  let mask=0;[[0,-1],[1,0],[0,1],[-1,0],[1,-1],[1,1],[-1,1],[-1,-1]].forEach(([dx,dy],i)=>{if(solid(x+dx,y+dy))mask|=1<<i});return mask;
 },
 sprite(image,mask){
  if(this.cache.has(mask))return this.cache.get(mask);
  if(!this.source){const s=document.createElement('canvas');s.width=s.height=32;s.getContext('2d').drawImage(image,0,0);this.source=s.getContext('2d').getImageData(0,0,32,32).data}
  if(!this.steelRows){this.steelRows=Array.from({length:32},(_,y)=>[0,1,2].map(k=>{let sum=0;for(let x=0;x<32;x++)sum+=this.source[(y*32+x)*4+k];return sum/32}))}
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),p=g.createImageData(32,32),d=p.data;
  const n=!!(mask&1),e=!!(mask&2),s=!!(mask&4),w=!!(mask&8),se=!!(mask&32);
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){
   // A continuous dark upper wall mass, a south face, and a narrow east face.
   // Diagonal occupancy turns the inner corner instead of leaving a cap seam.
   const east=x<28||e,south=y<16||s,diagonal=x<28?(y<16||s):y<16?e:se;
   const side=!east||(south&&!diagonal),front=!south;
   const uv=(y*32+x)*4,i=(y*32+x)*4;
   let factor=side?1.0:front?1.40:.72;
   if(front&&y===16)factor*=1.25;
   if(front&&(y===18||y===28))factor*=.78;
   if(side&&x===28)factor*=1.14;
   if(side&&x===31&&!e)factor*=.77;
   if(front&&y===31&&!s)factor*=.66;
   if(!side&&!front&&(!n&&y===0||!w&&x===0))factor*=.75;
   for(let k=0;k<3;k++)d[i+k]=Math.round((this.source[uv+k]*.4+this.steelRows[y][k]*.6)*factor);
   // Tiny bolts belong to exposed panel faces, never across joined cap edges.
   if(front&&(y===20||y===21)&&(x===5||x===6||x===24||x===25))for(let k=0;k<3;k++)d[i+k]=Math.max(27,d[i+k]+(y===20?-24:12));
   d[i+3]=255;
  }
  g.putImageData(p,0,0);this.cache.set(mask,c);return c;
 },
 insetCache:new Map(),
 insetWall(image,mask,theme,part){
  const key=mask+':'+theme+':'+part;
  if(this.insetCache.has(key))return this.insetCache.get(key);
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
  g.drawImage(this.sprite(image,mask),0,0);
  // The original cap (y0..15), east bevel, outside border and wall height survive.
  // All worktop/cabinet details are cut INTO the exposed wall face, y17..29.
  const paint=(x,y,w,h,color)=>{g.fillStyle=color;g.fillRect(x-part*32,y,w,h)};
  g.save();g.beginPath();g.rect(0,17,(mask&2)?32:28,13);g.clip();
  const pink=theme==='koyori',body=pink?'#a46d83':'#703345',lit=pink?'#c08ca0':'#914958';
  paint(2,17,58,13,'#20292f');paint(3,18,56,10,'#34404a');
  // Small inset work ledge, not the top and feet of a free-standing table.
  paint(4,21,54,2,pink?'#c8bebd':'#9ca4a6');paint(4,23,54,1,'#1f2930');
  paint(4,24,26,5,body);paint(32,24,26,5,body);
  paint(5,24,24,1,lit);paint(33,24,24,1,lit);
  paint(23,26,4,1,pink?'#ded2bf':'#b8a06d');paint(35,26,4,1,pink?'#ded2bf':'#b8a06d');
  // A recessed sink, short faucet and two vials fit entirely below the cap line.
  paint(8,20,12,3,'#65727a');paint(10,21,8,1,'#25333a');paint(16,18,2,3,'#a7b0b0');paint(17,18,3,1,'#8d9a9e');
  paint(43,18,3,3,pink?'#ce8ba5':'#879c91');paint(50,18,3,3,pink?'#9bbab8':'#879c91');
  paint(43,17,3,1,'#a5acaa');paint(50,17,3,1,'#a5acaa');
  paint(3,29,56,1,'#19232a');g.restore();this.insetCache.set(key,c);return c;
 },
 plaqueCache:new Map(),
 plaqueWall(image,mask,part,plaque){
  const key=mask+':'+part;if(this.plaqueCache.has(key))return this.plaqueCache.get(key);
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(this.sprite(image,mask),0,0);
  g.save();g.beginPath();g.rect(0,17,(mask&2)?32:28,13);g.clip();g.drawImage(plaque,-part*32,17,64,12);g.restore();this.plaqueCache.set(key,c);return c;
 },
 entranceWall(image,mask,side,part){
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
  g.drawImage(this.sprite(image,mask),0,0);
  const rect=(x,y,w,h,color)=>{g.fillStyle=color;g.fillRect(x-part*32,y,w,h)};
  // One architectural section per side: cap, recessed cable channel and door jamb.
  // No independent nameplates or five member icons; the centre remains open floor.
  rect(0,16,64,14,'#4c435d');rect(0,16,64,1,'#a5a3b5');rect(0,17,64,2,'#69617c');
  rect(0,29,64,2,'#262c34');rect(0,31,64,1,'#171e26');
  if(side==='left'){
   // A short branching conduit runs into a small engraved facility mark.
   rect(3,28,49,1,'#272a34');rect(5,27,41,1,'#9f92b4');rect(43,21,11,2,'#292b36');
   rect(42,22,3,3,'#51505f');
   // The X is cut directly into the metal, not mounted on a framed badge.
   const letters=['101/101/111/101/101','010/101/101/101/010','100/100/100/100/111','010/101/101/101/010'];
   letters.forEach((a,k)=>a.split('/').forEach((row,y)=>[...row].forEach((p,x)=>{if(p==='1')rect(6+k*4+x,21+y,1,1,'#e6dcf5')})));
   for(let i=0;i<7;i++){rect(24+i,21+i,2,1,'#171d27');rect(33-i,21+i,2,1,'#171d27');rect(24+i,20+i,1,1,'#f1d8ff');rect(33-i,20+i,1,1,'#f1d8ff')}
   // Chamfered, horn-like inner jamb is part of the entrance wall silhouette.
   rect(53,8,9,22,'#242a34');rect(52,9,2,19,'#b6aec5');rect(54,10,7,18,'#665b79');
   rect(55,12,3,13,'#292532');rect(55,12,3,12,'#77529c');rect(56,13,2,10,'#d9a9ff');rect(56,14,1,8,'#f2dfff');rect(59,7,3,24,'#aaa5ba');rect(61,7,2,24,'#272e36');
   rect(52,5,7,3,'#292e38');rect(54,4,5,2,'#b9a8cf');rect(57,2,3,3,'#77628d');
   rect(53,26,8,2,'#d3b977');rect(55,28,7,2,'#37323b');rect(52,18,2,2,'#f0daef');
  }else{
   rect(4,8,9,22,'#242a34');rect(12,9,2,19,'#b6aec5');rect(5,10,7,18,'#665b79');
   rect(8,12,3,13,'#292532');rect(8,12,3,12,'#77529c');rect(8,13,2,10,'#d9a9ff');rect(9,14,1,8,'#f2dfff');rect(3,7,2,24,'#aaa5ba');rect(1,7,2,24,'#272e36');
   rect(6,5,7,3,'#292e38');rect(6,4,5,2,'#b9a8cf');rect(5,2,3,3,'#77628d');
   rect(5,26,8,2,'#d3b977');rect(3,28,7,2,'#37323b');rect(12,18,2,2,'#f0daef');
   // Research access reader, recessed in the wall instead of a separate decoration.
   rect(24,20,15,7,'#252b34');rect(25,20,13,1,'#a9acb6');rect(26,22,4,2,'#bce6d6');
   rect(32,22,4,1,'#c6a8e0');rect(32,24,4,1,'#a38cb9');rect(25,26,13,1,'#181f29');
   rect(39,24,23,2,'#272a34');rect(40,24,22,1,'#9f92b4');
  }
  return c;
 },
 drawEntrance(g,origin,vault,images,map){
  if(!vault.entranceDecor)return;
  for(const [x,y]of vault.entranceDecor.wallCells){const left=x<6,part=left?x-4:x-7,mx=origin.x+x,my=origin.y+y;g.drawImage(this.entranceWall(images.labWall,this.mask(map,mx,my),left?'left':'right',part),mx*32,my*32)}
 },
 draw(g,origin,vault,images,map){
  for(let y=0;y<vault.height;y++)for(let x=0;x<vault.width;x++)if(vault.rows[y][x]==='#'){
   const mx=origin.x+x,my=origin.y+y,mask=this.mask(map,mx,my);
   const fixture=vault.fixtures.find(a=>a.mount==='wall'&&a.y===y&&x>=a.x&&x<a.x+a.w);
   const sprite=fixture?(fixture.render==='wall-plaque'?this.plaqueWall(images.labWall,mask,x-fixture.x,images.luiPanel):this.insetWall(images.labWall,mask,fixture.theme,x-fixture.x)):this.sprite(images.labWall,mask);
   g.drawImage(sprite,mx*32,my*32);
  }
  this.drawEntrance(g,origin,vault,images,map);
 }
};
