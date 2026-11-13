function drawFestivalProps230(makeCanvas) {
 const ink='#30231e', wood='#6b4937', oak='#9b704e', edge='#be9064';
 const red='#9f5950', darkRed='#6e403b', cream='#d9c3a0', shade='#ab8c6a';
 function sprite(width,height,paint){
  const tile=makeCanvas(width,height),ctx=tile.getContext('2d');
  const rect=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  function shape(color,x,y,rows){
   rows.forEach((row,dy)=>{
    for(const run of row.matchAll(/#+/g))rect(color,x+run.index,y+dy,run[0].length,1);
   });
  }
  function post(x,y,h){rect(ink,x,y,4,h);rect(wood,x+1,y,2,h-1);rect(oak,x+1,y,1,h-2);}
  function lamp(x,y,color){
   rect(wood,x+4,y,1,3);
   shape(ink,x,y+2,['..#####..','.#######.','#########','#########','#########','#########','.#######.','..#####..','...###...']);
   rect(color,x+1,y+4,7,4);rect(color,x+2,y+3,5,6);
   rect(color===red?'#c17a67':'#e6d1a9',x+2,y+4,5,1);
   rect(color===red?darkRed:shade,x+2,y+7,5,1);
  }
  function wheel(x,y){
   shape(ink,x,y,['..####..','.######.','########','###..###','###..###','###..###','###..###','###..###','########','.######.','..####..']);
   rect(oak,x+1,y+3,1,5);rect(wood,x+6,y+3,1,5);
   rect(oak,x+2,y+2,4,1);rect(oak,x+2,y+8,4,1);
   rect(wood,x+3,y+3,2,5);rect(edge,x+3,y+5,2,1);
  }
  paint({rect,shape,post,lamp,wheel});
  return tile;
 }
 return {
  'lantern-string':sprite(128,32,({rect,lamp})=>{
   const heights=[7,10,12,13,12,10,7];
   heights.forEach((y,i)=>{
    const x=9+i*16;
    rect(i===0||i===6?oak:wood,x,y,i===6?14:16,1);
    if(i<6)rect(wood,x+15,Math.min(y,heights[i+1]),1,Math.abs(y-heights[i+1])+1);
   });
   for(const [x,y,color] of [[16,8,red],[38,11,cream],[60,13,red],[82,12,cream],[104,10,red]])lamp(x,y,color);
  }),
  nobori:sprite(32,48,({rect,shape,post})=>{
   post(10,3,40);rect(edge,9,2,6,2);rect(ink,8,43,8,3);rect(oak,9,43,6,1);
   rect(ink,13,7,13,26);rect(darkRed,14,8,11,24);
   rect(red,15,9,8,19);rect('#b96e5b',16,9,6,2);
   shape(cream,16,13,['..##...','.####..','##..##.','.####..','..##...','..##...','..##...']);
   rect(cream,15,26,7,1);rect(darkRed,20,29,3,4);rect(red,16,29,3,3);
  }),
  'mask-rack':sprite(64,48,({rect,shape,post})=>{
   post(4,15,28);post(55,15,28);
   rect(ink,3,13,58,5);rect(oak,4,13,56,2);rect(edge,6,13,52,1);
   rect(wood,4,39,55,3);rect(oak,5,39,54,1);
   const masks=[
    [11,cream,['#.....#','##...##','#######','#######','.#####.','..###..','...#...']],
    [27,'#b86d5c',['#.....#','##...##','#######','#######','#######','.#####.','..###..']],
    [43,'#c6b8a0',['..###..','.#####.','#######','#######','#######','.#####.','..###..']]
   ];
   masks.forEach(([x,color,rows])=>{
    rect(oak,x+3,17,1,4);shape(ink,x+1,21,rows);shape(color,x,20,rows);
    rect(ink,x+1,23,2,1);rect(ink,x+4,23,2,1);rect(darkRed,x+3,25,1,1);
   });
  }),
  taiko:sprite(32,32,({rect,shape})=>{
   rect(ink,8,23,3,7);rect(ink,21,23,3,7);rect(wood,10,25,12,2);
   rect(oak,9,24,1,5);rect(oak,22,24,1,5);
   const drum=['...########...','..##########..','.############.','##############','##############','##############','##############','##############','##############','##############','.############.','..##########..','...########...'];
   shape(ink,8,6,drum);shape(darkRed,9,7,drum);shape(ink,6,9,drum);
   shape(shade,7,9,drum);rect(cream,9,12,10,7);rect(cream,11,10,6,11);
   rect('#efe0b9',11,11,5,1);rect(darkRed,20,11,2,9);
  }),
  yagura:sprite(96,112,({rect,shape,post,lamp})=>{
   post(16,5,89);post(76,5,89);
   rect(ink,9,10,16,4);rect(oak,10,10,14,2);rect(ink,72,10,16,4);rect(oak,73,10,14,2);
   lamp(7,14,cream);lamp(81,14,cream);
   rect(ink,17,37,63,5);rect(oak,18,37,61,2);
   for(const x of [24,35,48,61,72])post(x,40,14);
   rect(wood,16,49,65,6);rect(oak,17,49,63,2);
   shape(darkRed,29,42,['..#####..','.#######.','#########','#########','#########','.#######.','..#####..']);
   rect(cream,31,43,5,5);
   rect(ink,12,56,72,39);rect(wood,14,57,68,36);
   for(const y of [59,64,69,74]){rect(oak,15,y,66,3);rect(edge,16,y,64,1);}
   rect(ink,12,77,72,4);rect(edge,14,77,68,2);
   for(const x of [15,60]){
    rect(darkRed,x,82,21,19);rect(red,x+1,82,19,15);
    rect(cream,x+5,82,4,16);rect(cream,x+14,82,4,16);rect(shade,x+5,95,4,3);
   }
   for(let i=0;i<6;i++){
    const x=38-i,y=81+i*4,w=20+i*2;
    rect(ink,x,y,w,5);rect(wood,x+1,y+1,w-2,4);rect(oak,x+1,y+1,w-2,2);
   }
   rect(ink,13,100,19,3);rect(ink,63,100,20,3);
  }),
  'collapsed-yagura':sprite(96,72,({rect,shape,post,lamp})=>{
   post(17,7,45);rect(ink,11,9,14,4);rect(oak,12,9,12,2);lamp(7,13,cream);
   rect(wood,20,26,16,3);rect(edge,20,26,12,1);
   shape(ink,32,25,['##..','###.','.###','..##','...#']);
   // The right half of the platform drops toward the floor.
   for(let x=15;x<83;x++){
    const drop=Math.max(0,Math.floor((x-38)/3));
    const y=34+drop;
    rect(ink,x,y,1,13);
    rect(wood,x,y+1,1,10);
    if(x<37||x>43){rect(oak,x,y+1,1,2);rect(edge,x,y+1,1,1);}
    rect(oak,x,y+6,1,1);
   }
   for(const [x,y,h] of [[17,46,14],[23,46,17],[29,47,13],[60,52,12],[66,53,11],[72,55,9]]){
    rect(darkRed,x,y,6,h);
    rect((x===23||x===66)?cream:red,x+1,y,5,h-3);
    rect(shade,x+1,y+h-4,2,1);
   }
   for(const [x,y,w] of [[37,49,17],[36,53,19],[34,57,22],[32,61,24]]){
    rect(ink,x,y,w,5);rect(wood,x+1,y+1,w-2,3);rect(oak,x+1,y+1,w-4,1);
   }
   for(let x=52;x<86;x++){
    const y=57+Math.floor((x-52)/5);
    rect(ink,x,y+1,1,5);rect(wood,x,y,1,4);rect(oak,x,y,1,1);
   }
   rect(wood,13,62,14,2);rect(oak,12,62,11,1);rect(wood,65,68,11,2);
   rect(ink,80,61,8,4);rect(shade,82,61,5,2);rect(darkRed,77,64,4,2);
  }),
  bench:sprite(64,32,({rect,post})=>{
   post(10,17,11);post(50,17,11);
   rect(ink,3,12,58,11);rect(darkRed,4,13,56,8);
   rect(red,6,12,52,6);rect('#b97764',7,12,49,2);
   rect(darkRed,6,17,52,1);rect(wood,5,21,54,1);
  }),
  'festival-cart':sprite(64,64,({rect,shape,wheel})=>{
   for(const x of [19,43]){
    rect(ink,x,43,4,17);rect(wood,x+1,43,2,16);rect(oak,x+1,53,1,5);
   }
   rect(ink,11,29,42,17);rect(wood,12,29,40,15);
   rect(oak,13,30,38,4);rect(edge,14,30,36,1);
   rect(darkRed,16,25,29,5);rect(red,18,23,25,6);
   shape(shade,18,13,['..######..','.########.','##########','##########','##########','.########.','..######..']);
   rect(cream,20,15,6,4);rect(darkRed,21,20,6,7);
   rect('#5e6172',33,16,11,11);rect('#89808c',34,16,9,2);rect('#7a707f',36,19,7,5);
   rect(ink,9,36,46,3);rect(edge,10,36,44,1);rect(oak,14,40,36,2);
   wheel(7,34);wheel(49,34);
  })
 };
}
