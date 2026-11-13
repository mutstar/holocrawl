function drawFestivalStalls227(makeCanvas) {
 const outline='#2a201c', wood='#654331', lightWood='#ae8056';
 const colors={
  takoyaki:['#d58d50','#b57040','#784837','#e3b77c','#5b627c'],
  yakisoba:['#d2b165','#af914d','#75603b','#ead5a1','#7c8c5a'],
  ringoame:['#d195a0','#b47082','#764b59','#edcdb1','#e4bca9'],
  goldfish:['#789dbc','#507a9d','#3d5674','#c2d6d7','#9cb6c6'],
  shooting:['#bc746c','#9b4f53','#65393e','#dfb59a','#c88173'],
  'shaved-ice':['#b4d5d7','#6aa1ac','#457581','#d1e4d8'],
  'cotton-candy':['#e1b67e','#c68b66','#9b5d54','#efd4b1'],
  'grilled-onigiri':['#a98dbb','#7e6394','#534661','#d8c9c4'],
  'ring-toss':['#bb655b','#a03f48','#693640','#e1b377'],
  'omikuji':['#b26958','#8f473f','#613637','#e2c7a1']
 };
 function drawStall(id,paint) {
  const canvas=makeCanvas(96,64),ctx=canvas.getContext('2d');
  ctx.imageSmoothingEnabled=false;
  const rect=(color,x,y,w,h)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  const shape=(color,x,y,rows,pixel=1)=>{
   for(let row=0;row<rows.length;row++)for(let col=0;col<rows[row].length;col++){
    if(rows[row][col]==='#')rect(color,x+col*pixel,y+row*pixel,pixel,pixel);
   }
  };
  const [roof,cloth,shade,trim,accent]=colors[id];
  let grain=[...id].reduce((value,char)=>Math.imul(value^char.charCodeAt(0),16777619),2166136261);
  const next=()=>{grain=(Math.imul(grain,1664525)+1013904223)>>>0;return grain/4294967296;};
  rect(outline,10,24,76,38);
  rect('#4a3329',15,25,66,25);
  rect('#392922',17,26,62,13);
  rect('#644b38',17,44,62,5);
  for(const x of [11,81]){
   rect(wood,x,23,4,39);
   rect(lightWood,x+1,27,1,30);
   rect('#362720',x,56,4,1);
  }
  rect('#3c2c25',7,48,82,6);
  rect(lightWood,8,48,80,2);
  rect('#805b40',9,50,78,2);
  rect(shade,15,54,66,6);
  rect(cloth,16,55,64,3);
  for(const x of [20,32,45,60,74])rect(shade,x,55,1,5);
  rect(wood,13,60,70,1);

  for(let y=5;y<24;y++){
   const inset=Math.max(0,Math.floor((23-y)/2));
   rect(outline,6+inset,y,84-2*inset,1);
   if(y>5&&y<23)rect(y<9?roof:cloth,8+inset,y,80-2*inset,1);
  }
  for(let y=7;y<=21;y++){
   const inset=Math.floor((22-y)/3);
   const stripe=accent||(id==='ring-toss'?'#526f9b':id==='omikuji'?'#a35647':roof);
   rect(stripe,18+inset,y,9,1);
   rect(stripe,69-inset,y,9,1);
  }
  rect(trim,10,21,76,1);
  rect(shade,8,24,80,4);
  for(let x=8;x<88;x+=8){
   rect(cloth,x,24,6,4+(x%3===0?1:0));
   rect(trim,x,26,5,1);
  }
  for(let i=0;i<24;i++){
   const y=8+Math.floor(next()*13),inset=Math.floor((23-y)/2);
   const x=11+inset+Math.floor(next()*(72-2*inset));
   if(x>=38&&x<58)continue;
   rect(i%3===0?trim:i%3===1?shade:roof,x,y,1+Math.floor(next()*4),1);
  }
  const tornX=12+Math.floor(next()*9)*8;
  ctx.clearRect(tornX,27,2,3);
  rect(shade,tornX+1,25,1,2);
  for(let i=0;i<12;i++){
   const x=17+Math.floor(next()*61),y=55+Math.floor(next()*4);
   rect(i%3===0?trim:shade,x,y,i%3===0?1:2,1);
  }
  paint({rect,shape,trim,shade});
  return canvas;
 }
 return {
  takoyaki:drawStall('takoyaki',({rect,shape})=>{
   shape('#664438',39,8,['.....##.','..#####.','.#####..','######..','.####...'],2);
   shape('#e8ad69',39,7,['.....##.','..#####.','.#####..','######..','.####...'],2);
   rect('#ad5642',51,7,5,3);rect('#f1d29b',42,13,4,2);
   rect('#382c28',19,36,42,12);rect('#8a6c59',20,36,40,1);
   for(const y of [38,43])for(const x of [24,33,42,51]){
    shape('#825237',x,y,['.###.','#####','#####','.###.']);
    rect('#d6a06a',x+1,y,3,2);
   }
   rect('#bfa482',66,43,11,4);rect('#e5c69a',66,43,11,1);
  }),
  yakisoba:drawStall('yakisoba',({rect,shape})=>{
   shape('#e6d9af',40,8,['..###..','.#####.','.#####.','#######','.#####.'],2);
   rect('#556644',43,7,8,3);rect('#687a50',42,9,11,2);
   rect('#4e4034',49,12,1,1);rect('#d89a53',50,14,6,3);
   rect('#382c27',18,36,47,12);rect('#92715b',19,36,45,1);
   shape('#825637',23,38,['..############..','.################','#################','.##############..'],2);
   for(const [x,y,w] of [[29,39,6],[43,39,8],[25,42,8],[37,43,7],[50,42,6]])rect('#cba167',x,y,w,1);
   rect('#829166',34,40,3,2);rect('#9d9c61',48,43,4,2);
   rect('#af6e55',68,41,7,6);rect('#dbc1a0',68,40,7,2);
  }),
  ringoame:drawStall('ringoame',({rect,shape})=>{
   const apple=['.##.##.','#######','#######','.#####.','..###..'];
   shape('#83434b',41,10,apple,2);shape('#db7b83',41,9,apple,2);
   rect('#66704c',48,7,5,2);rect('#ecd0b4',43,12,2,2);
   rect('#8c654c',19,45,58,3);
   for(const [i,x] of [22,34,46,58,70].entries()){
    const y=i%2===0?34:37;
    rect('#c7a47e',x+3,y+4,1,46-y-4);
    shape('#783f46',x,y,apple);shape('#c96d74',x,y-1,apple);rect('#e5a0a0',x+1,y,2,1);
   }
  }),
  goldfish:drawStall('goldfish',({rect,shape})=>{
   shape('#e1e4d9',39,8,['..##....','..####.#','#######.','.#######','..####.#'],2);
   rect('#587791',41,12,9,2);rect('#3f5367',43,14,1,1);
   rect('#355467',17,37,55,10);rect('#96bfc8',18,37,53,2);
   rect('#568eab',20,39,49,6);rect('#679fba',24,40,12,1);rect('#75a8bb',48,44,16,1);
   for(const [x,y] of [[24,41],[36,43],[51,40],[61,43]])shape('#df9b66',x,y,['.##.','####']);
   shape('#e1d9bf',73,36,['.##.','####','####','.##.']);rect('#b89c78',75,40,1,7);
  }),
  shooting:drawStall('shooting',({rect,shape})=>{
   shape('#eed8b5',40,8,['#.....#','##...##','.#####.','#######','.#####.','..###..'],2);
   rect('#664547',44,14,1,1);rect('#664547',49,14,1,1);
   rect('#b27462',48,16,7,4);rect('#e7bea0',48,16,7,1);
   rect('#805844',18,39,61,2);rect('#644736',18,45,61,2);
   for(const [x,y,color] of [[23,33,'#c6a271'],[37,32,'#be776c'],[52,34,'#88968a'],[66,32,'#b78078']]){
    rect('#382a26',x,y,8,8);rect(color,x+1,y+1,6,6);rect('#d9b998',x+1,y+3,6,1);
   }
   rect('#ba9a78',29,44,24,2);rect('#80614a',44,46,7,2);
  }),
  'shaved-ice':drawStall('shaved-ice',({rect,shape})=>{
   shape('#355766',39,8,['...##...','..####..','########','.######.','..####..'],2);
   shape('#edf2dc',41,8,['..#...','.###..','#####.','.####.'],2);
   rect('#7db7c6',44,14,6,2);
   rect('#35444b',19,32,20,15);rect('#8cabb0',21,32,16,12);
   rect('#c4d9d0',22,33,11,3);rect('#536b72',22,39,13,2);
   rect('#7699a3',29,42,5,4);rect('#ba875f',38,35,4,2);
   for(const [x,body] of [[45,'#b15e71'],[53,'#759aaf'],[61,'#8b9f72'],[69,'#c18d62']]){
    rect('#362b2b',x,35,5,12);rect('#d0bda0',x+1,35,3,2);
    rect(body,x+1,38,3,7);rect('#b7a995',x+1,41,3,1);
   }
  }),
  'cotton-candy':drawStall('cotton-candy',({rect,shape})=>{
   const puff=['..###..','.#####.','#######','#######','.#####.','..###..'];
   shape('#9b6254',39,7,puff,2);shape('#f2dcba',41,7,puff,2);
   rect('#815638',47,18,2,3);
   for(const [x,y,color] of [[20,32,'#e5b0ae'],[31,29,'#e6d5ae'],[42,33,'#d5b6cb']]){
    rect('#be926b',x+4,y+6,1,47-y-6);shape('#71504a',x,y,puff);
    shape(color,x+1,y,puff);rect('#efe2cf',x+3,y+1,2,1);
   }
   rect('#5c4e55',54,37,21,9);rect('#aca4a0',53,36,23,4);
   rect('#d0bbae',56,37,17,2);rect('#846f78',59,41,12,5);
  }),
  'grilled-onigiri':drawStall('grilled-onigiri',({rect,shape})=>{
   const rice=['...##...','..####..','.######.','########','.######.'];
   shape('#59434e',39,8,rice,2);shape('#e4d4bc',39,7,rice,2);
   rect('#46414a',45,13,4,4);
   rect('#302626',20,36,43,12);rect('#776865',21,37,41,1);
   for(let x=23;x<60;x+=5)rect('#69574b',x,38,1,8);
   for(const x of [25,37,49]){
    shape('#966449',x,39,rice);shape('#dbb780',x,38,rice);
    rect('#5c5048',x+3,41,2,2);rect('#966845',x+1,42,2,1);
   }
   rect('#423530',68,35,6,11);rect('#a9837b',69,37,4,6);rect('#d2b58d',69,35,4,2);
  }),
  'ring-toss':drawStall('ring-toss',({rect,shape})=>{
   const ring=['.###.','##.##','#...#','##.##','.###.'];
   shape('#6c3c43',42,8,ring,2);shape('#e9c588',42,7,ring,2);
   rect('#8a5e45',18,43,61,3);rect('#47302a',18,46,61,2);
   for(const [x,y,paint] of [[25,34,'#b56559'],[36,39,'#c6a268'],[48,31,'#6684a4'],[59,36,'#aa6d85'],[71,38,'#b38c62']]){
    rect('#3c2d2a',x,y,4,45-y);rect(paint,x+1,y,2,44-y);
    rect('#ddc092',x+1,y,2,1);
   }
   shape('#d69b70',26,42,['.#####.','##...##','.#####.']);
   shape('#779fb2',54,44,['.#####.','##...##','.#####.']);
   shape('#b97789',66,42,['.#####.','##...##','.#####.']);
  }),
  'omikuji':drawStall('omikuji',({rect,shape})=>{
   shape('#ead1aa',39,8,['########','.######.','########','..#..#..','..#..#..'],2);
   rect('#3a2c27',20,35,18,11);rect('#9b7650',22,33,14,12);
   rect('#c59a62',24,33,10,2);rect('#392b27',27,33,5,1);
   rect('#e8cf9f',25,38,8,5);rect('#9a5a48',27,39,4,2);
   rect('#b78a61',45,32,2,15);rect('#a87c55',75,32,2,15);
   rect('#cba77f',47,34,28,1);rect('#cba77f',48,40,26,1);
   for(const [x,y] of [[49,34],[56,35],[63,34],[70,35],[53,40],[61,41],[68,40]]){
    rect('#ddc9ac',x,y,3,3);rect('#f2e0c0',x+1,y-1,1,4);
   }
  })
 };
}
