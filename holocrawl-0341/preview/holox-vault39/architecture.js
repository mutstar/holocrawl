// All new architecture is clipped to existing opaque wall cells.
const LabArchitecture={objectBrightness:1.32,objectSaturation:1.08,
 fixtures:[{id:'north-observation',type:'window',x:1,y:0,w:3,h:1},
 {id:'north-pipes',type:'pipe',x:4,y:0,w:3,h:1},
 {id:'north-vent',type:'vent',x:7,y:0,w:1,h:1},
 {id:'west-cabinet',type:'cabinet',x:0,y:2,w:1,h:1},
 {id:'east-control',type:'panel',x:8,y:2,w:1,h:1},
 {id:'east-vent',type:'vent',x:8,y:5,w:1,h:1},
 {id:'interior-conduit',type:'pipe',x:3,y:4,w:3,h:1},
 {id:'south-observation',type:'window',x:2,y:8,w:2,h:1},
 {id:'entry-reader',type:'panel',x:5,y:8,w:1,h:1}],
 draw(g,origin,vault,images){
  const ox=origin.x*32,oy=origin.y*32,rect=(x,y,w,h,c)=>{g.fillStyle=c;g.fillRect(ox+x,oy+y,w,h)};
  g.save();g.beginPath();
  for(let y=0;y<vault.height;y++)for(let x=0;x<vault.width;x++)if(vault.rows[y][x]==='#')g.rect(ox+x*32,oy+y*32,32,32);
  g.clip();
  // Thin steel sill and panel seams keep the underlying concrete visible.
  for(let x=0;x<9;x++)for(const y of [0,8]){
   rect(x*32+1,y*32+27,30,3,'#444c4b');rect(x*32+2,y*32+27,28,1,'#707875');
   rect(x*32,y*32+2,1,24,'#272e2d');rect(x*32+2,y*32+3,1,22,'#5d6461');
  }
  for(const x of [0,8]){
   rect(x*32+13,32,7,224,'#292f2d');rect(x*32+14,32,4,224,'#60675f');rect(x*32+15,32,1,224,'#7c8170');
   for(let y=48;y<250;y+=32){rect(x*32+11,y,11,3,'#343b38');rect(x*32+11,y,11,1,'#91927c')}
  }
  for(const a of this.fixtures){
   const x=a.x*32,y=a.y*32,w=a.w*32;
   if(a.type==='window'){
    rect(x+3,y+5,w-6,21,'#242b29');rect(x+4,y+6,w-8,18,'#777d73');
    rect(x+6,y+8,w-12,14,'#293b3d');rect(x+7,y+9,w-14,2,'#63817f');
    rect(x+8,y+14,w-18,2,'#3c5555');rect(x+13,y+11,2,9,'#78908a');
    for(let j=32;j<w-8;j+=32){rect(x+j,y+7,3,17,'#727a70');rect(x+j+1,y+8,1,15,'#a2a493')}
    rect(x+5,y+24,w-10,2,'#1e2624');
   }else if(a.type==='pipe'){
    g.drawImage(images.labPipe,ox+x,oy+y,w,32);
   }else if(a.type==='cabinet'){
    g.drawImage(images.labCabinet,ox+x,oy+y,32,32);
   }else if(a.type==='vent'){
    rect(x+5,y+6,23,20,'#282e2b');rect(x+6,y+7,21,18,'#6a7067');
    for(let j=0;j<5;j++){rect(x+8,y+9+j*3,17,2,'#303b36');rect(x+8,y+9+j*3,17,1,'#929687')}
    rect(x+6,y+24,21,2,'#242d28');
   }else if(a.type==='panel'){
    rect(x+6,y+4,20,23,'#232d2a');rect(x+7,y+5,18,21,'#747b70');
    rect(x+9,y+7,14,9,'#253e3e');rect(x+10,y+8,10,2,'#7eaaa0');
    rect(x+11,y+12,4,2,'#546e68');rect(x+10,y+19,3,3,'#ac945b');rect(x+16,y+19,5,2,'#343c35');
   }
  }
  // Sparse practical lamps, no floor-wide glow or wall replacement.
  for(const [x,y] of [[111,5],[6,136],[270,105],[168,261]]){
   rect(x-2,y-2,14,7,'#272f2a');rect(x,y,10,2,'#c4c6a5');rect(x+1,y+2,8,1,'#929b81');
  }
  // Small deterministic chips break up clean panel edges against city concrete.
  for(const a of this.fixtures)for(let n=0;n<18;n++){
   const x=a.x*32+3+(n*17+a.x*5)%(a.w*32-6),y=a.y*32+4+(n*7+a.y*3)%23;
   rect(x,y,n%5===0?2:1,1,n%3===0?'rgba(154,144,114,.22)':'rgba(30,36,31,.22)');
  }
  g.restore();
 }
};
