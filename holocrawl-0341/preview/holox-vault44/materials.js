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
 draw(g,origin,vault,images,map){
  for(let y=0;y<vault.height;y++)for(let x=0;x<vault.width;x++)if(vault.rows[y][x]==='#'){
   const mx=origin.x+x,my=origin.y+y;
   g.drawImage(this.sprite(images.labWall,this.mask(map,mx,my)),mx*32,my*32);
  }
 }
};
