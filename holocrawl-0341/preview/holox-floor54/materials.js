// holoX black armour:52 artwork palette/port, neighbour-driven native wall geometry.
// Only wall cells are painted. The original city floor remains untouched.
const LabMaterials={objectBrightness:1.25,objectSaturation:1.15,cache:new Map(),
 mask(map,x,y){
  const solid=(x,y)=>x>=0&&y>=0&&x<map.w&&y<map.h&&['#','+'].includes(map.rows[y][x]);
  let mask=0;[[0,-1],[1,0],[0,1],[-1,0],[1,-1],[1,1],[-1,1],[-1,-1]].forEach(([dx,dy],i)=>{if(solid(x+dx,y+dy))mask|=1<<i});return mask;
 },
 sidesFor(map,x,y){
  const inside=(x,y)=>x>=0&&y>=0&&x<map.w&&y<map.h&&map.rows[y][x]!=='#';
  const east=inside(x+1,y),west=inside(x-1,y);
  if(east||west)return(east?'e':'')+(west?'w':'');
  // Carry the inner-facing orientation around a corner from the adjacent room.
  const de=inside(x+1,y-1)||inside(x+1,y+1),dw=inside(x-1,y-1)||inside(x-1,y+1);
  return de&&!dw?'e':dw&&!de?'w':'e';
 },
 faceAt(mask,x,y,sides='e'){
  const e=!!(mask&2),s=!!(mask&4),w=!!(mask&8),se=!!(mask&32),sw=!!(mask&64);
  if(sides.includes('e')&&x>=28&&(!e||y>=16&&s&&!se))return'east';
  if(sides.includes('w')&&x<4&&(!w||y>=16&&s&&!sw))return'west';
  return !s&&y>=16?'south':'cap';
 },
 sprite(image,mask,port=false,sides='e'){
  const key=mask+':'+port+':'+sides;if(this.cache.has(key))return this.cache.get(key);
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d'),p=g.createImageData(32,32),d=p.data;
  const n=!!(mask&1),e=!!(mask&2),s=!!(mask&4),w=!!(mask&8);
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){
   const face=this.faceAt(mask,x,y,sides),grain=((x%4)*3+(y%4)*2)%5-2;
   let color=face==='south'?[48,45,59]:face==='east'||face==='west'?[29,28,39]:[43,41,54];
   color=color.map(v=>v+grain);
   if(face==='south'){
    if(y===16)color=[116,110,132];
    if(y===17)color=[71,65,83];
    if(y===18)color=[29,27,39];
    if(y===27)color=[83,76,99];
    if(y===28)color=[24,23,33];
    if(y===29||y===30)color=(x+3*(y-29))%8<4?(y===29?[220,179,44]:[181,137,30]):[31,29,38];
    if(y===31)color=[19,19,28];
   }else if(face==='east'||face==='west'){
    const edge=face==='east'?x:31-x;
    if(edge===28)color=[92,79,113];
    if(edge===29||edge===30)color=(y+3*(edge-29))%8<4?[181,137,30]:[27,25,36];
    if(edge===31)color=[17,17,26];
   }else{
    // Exposed upper edges only: joined caps never receive repeated tile outlines.
    if(!n&&y===0||!w&&x===0||!e&&x===31)color=[26,24,37];
    if(!n&&y===1||!w&&x===1||!e&&x===30)color=[102,84,125];
    if(!n&&y===2||!w&&x===2||!e&&x===29)color=[66,56,82];
    // Small machined chamfers where the outer outline changes direction.
    if(!n&&!w&&x+y<4)color=[27,25,37];
    if(!n&&!e&&(31-x)+y<4)color=[27,25,37];
    if(!w&&!s&&x+(31-y)<3)color=[27,25,37];
   }
   const i=(y*32+x)*4;d.set([...color,255],i);
  }
  g.putImageData(p,0,0);
  if(port&&!s&&e&&w){
   // Reuse a round window from52 artwork, entirely within the exposed front face.
   g.imageSmoothingEnabled=false;g.drawImage(image,8,12,14,14,10,17,11,11);
  }
  this.cache.set(key,c);return c;
 },
 insetCache:new Map(),
 insetWall(image,mask,theme,part,sides='e'){
  const key=mask+':'+theme+':'+part+':'+sides;
  if(this.insetCache.has(key))return this.insetCache.get(key);
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
  g.drawImage(this.sprite(image,mask,false,sides),0,0);
  // The original cap (y0..15), east bevel, outside border and wall height survive.
  // All worktop/cabinet details are cut INTO the exposed wall face, y17..29.
  const paint=(x,y,w,h,color)=>{g.fillStyle=color;g.fillRect(x-part*32,y,w,h)};
  g.save();g.beginPath();g.rect(sides.includes('w')&&!(mask&8)?4:0,17,32-(sides.includes('w')&&!(mask&8)?4:0)-(sides.includes('e')&&!(mask&2)?4:0),13);g.clip();
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
 plaqueWall(image,mask,part,plaque,sides='e'){
  const key=mask+':'+part+':'+sides;if(this.plaqueCache.has(key))return this.plaqueCache.get(key);
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(this.sprite(image,mask,false,sides),0,0);
  g.save();g.beginPath();g.rect(sides.includes('w')&&!(mask&8)?4:0,17,32-(sides.includes('w')&&!(mask&8)?4:0)-(sides.includes('e')&&!(mask&2)?4:0),13);g.clip();g.drawImage(plaque,-part*32,17,64,12);g.restore();this.plaqueCache.set(key,c);return c;
 },
 drawEntrance(g,origin,vault,images,map){
  if(!vault.entranceDecor)return;
  // Shared wall body/face heights on both sides. Only a recessed jamb light is added.
  const y=origin.y+8;
  for(const [tx,px]of [[5,28],[7,3]]){
   const x=origin.x+tx;g.fillStyle='#93869f';g.fillRect(x*32+(tx===5?27:4),y*32+16,1,12);
   g.fillStyle='#32273f';g.fillRect(x*32+px,y*32+17,1,11);
   g.fillStyle='#bd85ee';g.fillRect(x*32+px,y*32+19,1,7);
   g.fillStyle='#ead8f6';g.fillRect(x*32+px,y*32+20,1,2);
  }
 },
 draw(g,origin,vault,images,map){
  for(let y=0;y<vault.height;y++)for(let x=0;x<vault.width;x++)if(vault.rows[y][x]==='#'){
   const mx=origin.x+x,my=origin.y+y,wallMap={w:vault.width,h:vault.height,rows:vault.rows},mask=this.mask(wallMap,x,y),sides=this.sidesFor(wallMap,x,y);
   const fixture=vault.fixtures.find(a=>a.mount==='wall'&&a.y===y&&x>=a.x&&x<a.x+a.w);
   const sprite=fixture?(fixture.render==='wall-plaque'?this.plaqueWall(images.labWall,mask,x-fixture.x,images.luiPanel,sides):this.insetWall(images.labWall,mask,fixture.theme,x-fixture.x,sides)):this.sprite(images.labWall,mask,(x+y)%3!==0,sides);
   g.drawImage(sprite,mx*32,my*32);
  }
  this.drawEntrance(g,origin,vault,images,map);
 }
};
