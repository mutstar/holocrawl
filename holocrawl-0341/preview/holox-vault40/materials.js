const LabMaterials={objectBrightness:1.32,objectSaturation:1.08,
 draw(g,origin,vault,images){
  const ox=origin.x*32,oy=origin.y*32;
  for(let y=0;y<vault.height;y++)for(let x=0;x<vault.width;x++){
   const ch=vault.rows[y][x],px=ox+x*32,py=oy+y*32;
   if(ch==='#'){
    const above=vault.rows[y-1]?.[x]==='#',below=vault.rows[y+1]?.[x]==='#';
    const side=(x===0||x===8||x===3)&&y>0&&y<8&&above&&below;
    if(side){
     // Side faces use the panel body continuously; avoid repeating a horizontal
     // top cap down the wall, which made the perimeter look striped.
     g.drawImage(images.labWall,0,11,32,18,px,py,32,32);
     const edge=x===8?25:0;
     g.drawImage(images.labWall,0,0,7,7,px+edge,py,7,32);
    }else g.drawImage(images.labWall,px,py,32,32);
   }
   else if(ch!=='+'){
    g.drawImage(images.labFloor,px,py,32,32);
    // Work areas share the lab floor rather than outdoor asphalt.
    if(x>=4&&y<=4){g.fillStyle='rgba(104,134,124,.07)';g.fillRect(px,py,32,32)}
   }
  }
  // Flush floor markings integrate equipment into working areas.
  const mark=(x,y,w,h,color)=>{g.fillStyle=color;g.fillRect(ox+x,oy+y,w,h)};
  for(let x=132;x<251;x+=12){mark(x,153,5,2,'#99916c');mark(x+1,155,5,1,'#575b4e')}
  // Recessed rubber mats in storage/guard areas; no new obstructions.
  for(const m of [{x:1,y:6,w:2,h:1,c:'#414c4b'},{x:4,y:6,w:2,h:1,c:'#4b5042'}]){
   mark(m.x*32+2,m.y*32+15,m.w*32-4,15,m.c);
   for(let i=5;i<m.w*32-4;i+=5)mark(m.x*32+i,m.y*32+18,1,10,'#303a36');
  }
  // A few short scuffs connect furnishings to the old lab floor.
  for(const [x,y] of [[67,76],[154,109],[221,138],[83,216],[184,217]]){mark(x,y,7,1,'#767c6e');mark(x+2,y+2,3,1,'#4c5952')}
 }
};
