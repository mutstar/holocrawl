function drawTheaterDecor(g,origin,gen2Entrance){
 const ox=origin.x*32,oy=origin.y*32;
 const box=(x,y,w,h,color)=>{g.fillStyle=color;g.fillRect(ox+x,oy+y,w,h)};
 // Recessed projection screen on the north wall; stage floor stays clear.
 box(40,1,176,30,'#171c1b');box(42,2,172,28,'#665b4c');
 box(46,3,164,26,'#252c2b');box(49,5,158,21,'#b3bab0');
 box(51,6,154,18,'#c8cec1');box(51,6,154,2,'#d5d9ca');
 box(51,23,154,1,'#a4afa5');box(49,26,158,2,'#101715');
 // Sparse cloth seams and a dim projected star, no light over actors.
 box(73,8,1,13,'#bec5ba');box(184,8,1,13,'#bec5ba');
 box(126,10,3,10,'#b3c2b9');box(122,14,11,2,'#b3c2b9');
 box(125,12,5,6,'#b3c2b9');
 for(const x of [34,211]){
  box(x,2,11,28,'#2b161b');box(x+1,3,8,25,'#672a36');
  box(x+2,3,2,22,'#813744');box(x+7,3,2,24,'#48212c');
  box(x-1,1,13,2,'#8b7956');
 }
 // Restore the approved Gen2 theater identity from theater-wall31.
 // Exact sprite crops: Ayame mask + Subaru duck, Choco winged heart.
 // The source door is omitted so the functional two-tile doors remain intact.
 g.drawImage(gen2Entrance,0,0,24,32,ox+36,oy+224,24,32);
 g.drawImage(gen2Entrance,72,0,24,32,ox+196,oy+224,24,32);
 // Burgundy side trim sits on the blocked wall tiles beside both doors.
 for(const x of [89,160]){
  box(x,231,7,25,'#25171b');box(x+1,233,5,23,'#6b2d3a');
  box(x+2,234,1,20,'#8a4250');box(x,230,7,2,'#9a8254');
 }
 // Low marquee header: above the door artwork, leaves the threshold legible.
 box(88,224,80,8,'#151b19');box(89,224,78,1,'#a38b5b');
 box(90,226,76,5,'#542a32');box(91,231,74,1,'#92794e');
 // A subdued theater lintel replaces the generic LIVE lettering.
 box(116,227,24,2,'#8b4b59');box(121,227,14,1,'#b27872');
 for(const x of [92,98,104,110,145,151,157,163])box(x,227,1,2,'#e0b969');
 for(const x of [79,173]){
  box(x,235,5,10,'#242523');box(x+1,236,3,2,'#a68a56');
  box(x+1,239,3,4,'#d4ae63');box(x+2,239,1,3,'#f0d39a');
  box(x+1,244,3,1,'#746044');
 }
}
