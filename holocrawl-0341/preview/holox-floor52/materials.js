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
 entranceWall(image,mask,side,part,entrance){
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
  g.drawImage(this.sprite(image,mask),0,0);
  // The generated wall section fills existing wall cells only. Mirror the pair,
  // never the middle walkable passage. Ports and caution stripe belong to the wall.
  if(side==='left')g.drawImage(entrance,-part*32,0);
  else{g.save();g.translate(32,0);g.scale(-1,1);g.drawImage(entrance,-(1-part)*32,0);g.restore()}
  return c;
 },
 drawEntrance(g,origin,vault,images,map){
  if(!vault.entranceDecor)return;
  for(const [x,y]of vault.entranceDecor.wallCells){const left=x<6,part=left?x-4:x-7,mx=origin.x+x,my=origin.y+y;g.drawImage(this.entranceWall(images.labWall,this.mask(map,mx,my),left?'left':'right',part,images.entrance),mx*32,my*32)}
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
