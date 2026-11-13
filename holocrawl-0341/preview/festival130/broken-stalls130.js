function drawBrokenFestivalStall(canvas, intact, type) {
 const tile=canvas(96,32), ctx=tile.getContext('2d');
 ctx.imageSmoothingEnabled=false;
 const source=canvas(96,64).getContext('2d');
 source.drawImage(intact,0,0);
 const color=(x,y)=>{
  const [r,g,b]=source.getImageData(x,y,1,1).data;
  return `rgb(${Math.round(r*.79)},${Math.round(g*.79)},${Math.round(b*.79)})`;
 };
 const canvasColor=color(32,15),foldColor=color(33,24),stripe=color(24,16);
 const rect=(fill,x,y,w,h)=>{ctx.fillStyle=fill;ctx.fillRect(x,y,w,h);};
 const tilt=['yakisoba','goldfish','cotton-candy','ring-toss'].includes(type)?-1:1;
 const clothY=column=>9+Math.floor(column/8)*tilt+(tilt<0?5:0);

 // Short beams and the collapsed counter sit at ground level.
 for(let i=0;i<29;i++){
  const y=20+Math.floor(i/6);
  rect('#352820',8+i,y+1,1,4);
  rect('#86664a',8+i,y,1,2);
 }
 for(let i=0;i<33;i++){
  const y=27-Math.floor(i/6);
  rect('#423028',52+i,y,1,4);
  rect(i<25?'#89694e':'#a17d5b',52+i,y,1,1);
 }
 rect('#644b38',24,23,43,3);
 rect('#9a7656',26,23,39,1);
 rect('#4e392e',22,27,3,3);
 rect('#6f5340',69,25,5,2);
 rect('#80644b',77,29,7,1);

 // The canopy is torn, but its color and a piece of the original sign survive.
 for(let column=0;column<53;column++){
  const y=clothY(column),x=19+column;
  const torn=column<6?3-Math.floor(column/2):column>43?Math.floor((column-43)/2):0;
  const height=11-torn-(column%13<2?2:0);
  rect('#372924',x,y,1,height+2);
  rect(canvasColor,x,y+1,1,height);
  rect(foldColor,x,y+height,1,1);
  if((column>=8&&column<16)||(column>=38&&column<44))rect(stripe,x,y+2,1,height-2);
 }
 ctx.globalAlpha=.84;
 ctx.drawImage(intact,38,7,20,13,37,clothY(23),16,10);
 ctx.globalAlpha=1;
 rect('#403128',29,clothY(10)+4,4,1);
 rect('#403128',31,clothY(12)+5,3,1);
 rect('#403128',60,clothY(41)+5,4,1);
 rect('#5e4735',63,clothY(44)+6,3,1);
 return tile;
}
