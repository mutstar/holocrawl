(function (root) {
 const wood = ['#36271e','#5b402e','#79573b','#946c49'];
 const cloth = ['#412b32','#633b43','#8a5355','#ac7370'];
 const straw = ['#403427','#65523b','#907654','#a8906a'];

 function line(ctx,x,y,endX,endY,color,size=1){
  const dx=Math.abs(endX-x),dy=-Math.abs(endY-y);
  const sx=x<endX?1:-1,sy=y<endY?1:-1;
  let error=dx+dy;
  ctx.fillStyle=color;
  for(;;){
   ctx.fillRect(x,y,size,size);
   if(x===endX&&y===endY)break;
   const twice=2*error;
   if(twice>=dy){error+=dy;x+=sx;}
   if(twice<=dx){error+=dx;y+=sy;}
  }
 }

 const debris=[
  {id:'broken-booth',name:'부서진 가판대',footW:2,footH:1,draw(q){
   line(q,10,24,53,24,wood[0],4);
   line(q,12,25,15,11,wood[1],3);
   line(q,48,23,53,12,wood[1],3);
   line(q,11,13,35,17,wood[0],5);
   line(q,12,13,32,16,wood[3],2);
   line(q,36,19,53,13,wood[0],5);
   line(q,39,18,52,13,wood[2],2);
   line(q,18,23,32,26,wood[2],2);
   line(q,31,22,43,27,wood[1],3);
   line(q,7,27,10,26,wood[2]);
   line(q,55,26,59,28,wood[1]);
  }},
  {id:'torn-bunting',name:'찢어진 축제 천',footW:1,footH:1,draw(q){
   line(q,23,17,27,25,wood[2],2);
   q.fillStyle=cloth[0];q.fillRect(6,23,19,5);q.fillRect(9,20,13,4);
   q.fillStyle=cloth[2];q.fillRect(8,22,11,3);q.fillRect(11,20,6,2);q.fillRect(18,24,6,2);
   q.fillStyle=cloth[3];q.fillRect(11,21,5,1);
  }},
  {id:'lantern-scraps',name:'꺼진 초롱 조각',footW:1,footH:1,draw(q){
   q.fillStyle=straw[0];q.fillRect(5,23,8,4);
   q.fillStyle=straw[2];q.fillRect(6,22,5,3);q.fillRect(10,25,3,1);
   q.fillStyle=cloth[0];q.fillRect(15,22,11,5);q.fillRect(18,19,7,3);
   q.fillStyle=cloth[2];q.fillRect(16,23,9,3);q.fillRect(19,20,5,3);
   q.fillStyle=cloth[3];q.fillRect(20,20,4,1);
  }},
  {id:'collapsed-handcart',name:'쓰러진 빈 수레',footW:2,footH:1,draw(q){
   line(q,39,22,54,13,wood[1],3);
   line(q,40,22,54,13,wood[3]);
   line(q,13,15,40,19,wood[0],7);
   line(q,14,15,40,19,wood[3],2);
   line(q,16,19,39,22,wood[2],2);
   q.fillStyle=wood[0];q.fillRect(15,21,10,7);
   q.fillStyle=wood[2];q.fillRect(17,21,6,1);q.fillRect(16,22,2,5);q.fillRect(23,22,1,5);q.fillRect(18,27,5,1);
   q.fillStyle=wood[3];q.fillRect(19,24,2,2);
  }}
 ];
 root.FestivalDebris130=debris;
 if(typeof module!=='undefined'&&module.exports)module.exports=debris;
})(globalThis);
