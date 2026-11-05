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
 entrancePlaque(image,mask,id){
  const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d');g.imageSmoothingEnabled=false;
  g.drawImage(this.sprite(image,mask),0,0);
  const rect=(x,y,w,h,color)=>{g.fillStyle=color;g.fillRect(x,y,w,h)};
  // A shallow relief attached to the front of the existing wall: no floor collision.
  rect(3,12,26,18,'#161e27');rect(4,13,24,16,'#626b75');rect(5,14,22,14,'#303943');
  rect(6,14,20,1,'#929597');rect(6,27,20,1,'#1d252d');
  for(const x of [5,26]){rect(x,15,1,1,'#bbb39c');rect(x,25,1,1,'#bbb39c')}
  const palettes={laplus:['#b794e0','#6e518f','#ddd1ed'],lui:['#e698a0','#a44860','#ecd0bb'],koyori:['#e8b4cd','#b872a0','#e9dedb'],chloe:['#e0e2df','#b94559','#171d26'],iroha:['#c0d89c','#72965e','#dedacc']};
  const colors=palettes[id];
  const glyphs={
   laplus:['a.............a','aa...........aa','.aa.........aa.','..aaa.....aaa..','....aa...aa....','.....bbbbb.....','....bccbccb....','....bc...cb....','.....bbbbb.....','.......c.......','......ccc......'],
   lui:['a.............a','aa...........aa','.aaa.......aaa.','..abaaa.aaaba..','...abaaaaaba...','....abbbbba....','.....abbaa.....','......abb......','.......b.......','......ccc......','.....cc.cc.....'],
   koyori:['......ccc......','......c.c......','......c.c......','.....cc.cc.....','.....c...c.....','....c..a..c....','...c..aaa..c...','..c..aaaaa..c..','..c.aaaaaaa.c..','...bbbbbbbbb...','....ccccccc....'],
   chloe:['....bbbbbbb....','...b.......b...','......ccc......','....aaaaaaa....','...aacaaaacaa..','..aacccacccaa..','..aaaaaaaaaaa..','...aaaaaaaaa...','....ccccccc....','.....bb.bb.....','....bb...bb....'],
   iroha:['...baaaa.......','...baaaa.....c.','...baaa.....cc.','...baa.....cc..','...b......cc...','...b.....cc....','...b..a.cc.....','...b...ac......','...b..c.aa.....','...b.cc........','..bbb..........']};
  glyphs[id].forEach((row,y)=>[...row].forEach((p,x)=>{if(p!=='.')rect(9+x,16+y,1,1,colors['abc'.indexOf(p)])}));
  return c;
 },
 drawEntrance(g,origin,vault,images,map){
  const decor=vault.entranceDecor;if(!decor)return;
  for(const a of decor.plaques){const x=origin.x+a.x,y=origin.y+a.y;g.drawImage(this.entrancePlaque(images.labWall,this.mask(map,x,y),a.id),x*32,y*32)}
  // A worn metal X set into the walkable threshold, never a closed door.
  const e=decor.emblem,x=(origin.x+e.x)*32,y=(origin.y+e.y)*32;
  const rect=(a,b,w,h,color)=>{g.fillStyle=color;g.fillRect(x+a,y+b,w,h)};
  rect(5,18,22,12,'#232c32');rect(6,18,20,1,'#79838a');rect(6,29,20,1,'#111b23');
  for(let i=0;i<8;i++){rect(9+i,20+i,2,1,'#d1c28a');rect(21-i,20+i,2,1,'#d1c28a')}
  rect(15,23,3,2,'#e3d6a9');rect(3,19,1,10,'#817858');rect(28,19,1,10,'#817858');
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
