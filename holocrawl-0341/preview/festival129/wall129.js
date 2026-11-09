globalThis.createFestivalWall129=function({canvas,g,wall,rects,planes,tex}){
 // One reflected material field spans the wall; lighting never changes per cell.
 const fold=n=>{const p=((n%128)+128)%128;return p<64?p:127-p;};
 const wallCache=new Map();
 function agedWall(mask,variant=0,worldX=0,worldY=0){
  const key=`${mask}:${variant}:${((worldX%4)+4)%4}:${((worldY%4)+4)%4}`;if(wallCache.has(key))return wallCache.get(key);
  const c=canvas(32,32),q=g(c),rect=rects[`${mask}:0`];q.drawImage(wall,...rect,0,0,32,32);const d=q.getImageData(0,0,32,32),front=planes[String(mask)];
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){
   const i=(y*32+x)*4;if(!d.data[i+3])continue;
   const old=[d.data[i],d.data[i+1],d.data[i+2]],lum=old[0]*.2126+old[1]*.7152+old[2]*.0722;
   if(front[y*32+x]==='1'){
    const tx=fold(worldX*32+x+variant*7),ty=fold(worldY*32+y+variant*11),j=(ty*64+tx)*4;
    const shade=.82*(.99-Math.max(0,y-10)*.0045);
    for(let k=0;k<3;k++)d.data[i+k]=Math.round(tex[j+k]*shade);
   }else{
    d.data[i]=Math.round(lum*.98);d.data[i+1]=Math.round(lum*.88);d.data[i+2]=Math.round(lum*.75);
   }
  }
  q.putImageData(d,0,0);wallCache.set(key,c);return c;
 }
 return agedWall;
};
