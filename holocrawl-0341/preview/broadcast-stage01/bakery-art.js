// Local coordinates keep the shop boards, exterior paving and chapel runner continuous.
function drawBakeryGround(p,ending,x,y) {
  const grain=StreetGen.random(`bakery-floor:${x},${y}`);
  const chipX=Math.floor(grain()*19)+3, chipY=Math.floor(grain()*16)+7;
  if (x>=31 && y<=16) {
    p(grain()<.42 ? '#77726bad' : '#80786dab',0,0,32,32);
    p('#514f4959',0,31,32,1); p('#51494153',31,0,1,31);
    if (x>=37 && x<=39 && y>=5 && y<=15) {
      p('#7c5256df',0,0,32,32);
      if(x!==38) {
        const edge=x===37?2:28;
        p('#a59173',edge,0,2,32);
        if(y%3===1) {
          p('#67575a',edge,10,2,7);p('#756461',edge-1,16,4,3);
        }
      }
      // Across the walking lane the nap has worn away in short, irregular streaks.
      if (x===38 || grain()<.32) {
        p('#93716d7a',chipX,chipY,5,2);p('#ac8c7d59',chipX+4,chipY+1,5,1);
      }
      if(y===15) {p('#99876e',0,28,32,2);for(let i=2;i<32;i+=5)p('#ad98796b',i,30,2,2);}
    } else if(grain()<.12) {
      for(let i=0;i<4;i++) p('#514c478c',chipX+i*2,chipY+i,3,1);
      p('#92897c85',chipX+6,chipY+4,3,1);
    }
  } else if (x<=20 && y<=19) {
    if(y<8) {
      p((x+y)%2?'#847e69a8':'#68675ba8',0,0,32,32);
      p('#55544b88',0,31,32,1);p('#5c594f80',31,0,1,32);
      if(y>=3 && y<=6 && x<9) p('#49403430',0,0,32,32);
    } else {
      for(let n=0;n<4;n++) {
        const row=y*4+n, joint=(row*19)%75;
        const board=Math.floor((x*32+joint)/75);
        p(['#72604cbd','#79664fbc','#695a49b8','#756453bd'][(row+board)%4],0,n*8,32,8);
        p('#493f357a',0,n*8+7,32,1);
        const seam=(75-(x*32+joint)%75)%75;
        if(seam<32) {p('#52463a',seam,n*8,1,7);if(seam<29)p('#94826a',seam+2,n*8+2,1,1);}
        if(grain()<.46) p('#b2966e48',chipX,n*8+3,4+Math.floor(grain()*8),1);
      }
    }
  } else {
    for(let n=0;n<2;n++) {
      const off=(n*13+y*7)%32;
      p('#625e56a0',0,n*16+1,32,14);p('#79726685',off,n*16+2,Math.min(9,32-off),1);
      p('#514f4b',off,n*16+1,1,15);
    }
    if(x===26 && y>=16 && y<=21) {
      p('#565753',24,0,8,32);
      if(y===20) for(let n=3;n<31;n+=4) p('#353d3d',24,n,7,2);
    }
  }
  // A few mineral grains, not an opaque replacement for the dock's mottled concrete.
  for(let n=0;n<5;n++) {
    const dx=Math.floor(grain()*29),dy=Math.floor(grain()*30);
    p(n%2?'#c2ad8c25':'#29282835',dx,dy,1+Math.floor(grain()*3),1);
  }
  if(y===7 && x>=11 && x<=13) {
    for(let i=0;i<10;i++) p('#b4a99366',Math.floor(grain()*25),Math.floor(grain()*9),2+Math.floor(grain()*5),1);
  }
  if(x===25 && y>=16 && y<=20) {
    for(const dx of [6,22]) for(const dy of [3,14,26]) p('#3f41404a',dx,dy,3,5);
  }
  if(x===37 && y===6) {
    for(let i=0;i<5;i++) p(i%2?'#ad8b84':'#ab9d86',Math.floor(grain()*28),Math.floor(grain()*26),3,2);
  }
  if(endingTile(ending,x,y-1)==='#') {p('#201f224a',0,0,32,3);p('#29242423',0,3,32,3);}
  if(endingTile(ending,x-1,y)==='#') p('#28232539',0,0,3,32);
}

function drawBakeryScenery(p,{kind,width,depth,x:tileX}) {
  const w=width*32, h=depth*32;
  function box(x,y,span,height,d,top,face,side) {
    for(let n=d;n>0;n--) {
      p(top,x+n,y-n,span,1);p(side,x+span+n-1,y-n+1,1,height);
    }
    p(face,x,y,span,height);
  }
  function oval(x,y,rx,ry,color) {
    for(let dy=-ry;dy<=ry;dy++) {
      const extent=Math.floor(rx*Math.sqrt(1-dy*dy/(ry*ry)));
      p(color,x-extent,y+dy,2*extent+1,1);
    }
  }
  function loaf(x,y,s=1) {
    p('#795237',x+2*s,y+4*s,16*s,6*s);
    p('#b77e48',x,y+3*s,19*s,5*s);p('#d9aa69',x+3*s,y,13*s,6*s);
    for(const offset of [5,10,15]) p('#a67446',x+offset*s,y+s,2*s,3*s);
  }
  function baguette(x,y) {
    for(let i=0;i<28;i++) {
      const thick=Math.min(6,2+i,29-i), top=y-Math.floor(i/3);
      p('#85603f',x+i,top,1,thick+2);
      p(i%7<2?'#e2c08a':'#c6945c',x+i,top,1,thick);
    }
  }
  function buns(x,y) {
    for(const [dx,dy] of [[1,2],[12,0],[8,7]]) {
      oval(x+dx,y+dy,6,4,'#956c47');oval(x+dx-1,y+dy-1,5,3,'#ce9d68');
      p('#e1bc88',x+dx-2,y+dy-3,3,1);
    }
  }
  function bloom(x,y,color) {
    p('#59684e',x-5,y,10,5);p('#748267',x+2,y-3,5,4);
    p(color,x-2,y-4,4,8);p(color,x-4,y-2,8,4);p('#cfa774',x-1,y-1,2,2);
  }
  function shadow(x,y,span,length) {
    for(let dy=0;dy<length;dy++) p(dy<3?'#29242577':'#29242544',x+dy,y+dy,span,1);
  }
  if(kind==='bakery-window') {
    shadow(5,56,w-12,6);
    box(2,25,w-10,32,6,'#9c805f','#796049','#4f443b');
    p('#495956',6,27,w-19,21);
    for(let x=11,i=0;x<w-24;x+=32,i++) {
      if(i%3===0) buns(x+4,37);
      else if(i%3===1) baguette(x-2,40);
      else loaf(x,37);
      p('#9eafa850',x+7,29,12,2);p('#aec3b957',x+4,31,10,1);
      p('#b49166',x+23,26,3,23);
    }
    p('#bd9972',3,49,w-13,3);
    for(let x=2,i=0;x<w-6;x+=16,i++) {
      const span=Math.min(16,w-6-x),cream=i%2===0;
      const hem=(i+tileX)%7===0?3:6+(i%3);
      for(let n=0;n<11;n++) p(cream?'#b7a88d':'#945e54',x+Math.floor((10-n)/2),7+n,span,1);
      p(cream?'#928773':'#734d47',x,18,span,hem);
      p(cream?'#ae9e85':'#98695b',x+2,17+hem,Math.max(1,span-4),2);
      if(i%4===2) {p('#65564a',x+6,20,2,hem-1);p('#b49879',x+8,19,1,4);}
    }
    p('#6b5847',30,49,13,2);p('#a48a69',38,52,16,1);
    if(tileX===3) {
      // A thick wooden bread slice hangs from the entrance-side awning post.
      const sx=w-54;
      p('#4a4941',sx-3,5,53,4);p('#af9d7c',sx+7,5,2,10);p('#af9d7c',sx+37,5,2,10);
      oval(sx+23,26,23,12,'#694936');p('#694936',sx+5,26,36,24);
      oval(sx+22,23,22,12,'#ba8253');p('#ba8253',sx+4,24,35,23);
      oval(sx+21,23,18,8,'#e1c292');p('#d5b789',sx+8,24,27,18);
      for(const [dx,dy] of [[12,21],[29,27],[16,34],[26,38]]) p('#b39268',sx+dx,dy,3,2);
    }
  } else if(kind==='bread-baskets') {
    shadow(6,52,111,8);
    for(const x of [10,103]) box(x,39,6,15,3,'#987f5a','#70553e','#534437');
    box(3,36,111,9,8,'#aa8760','#7b5f45','#594737');
    for(const x of [9,61]) {
      box(x,33,42,7,5,'#ad8656','#98724c','#644f39');
      for(let n=2;n<39;n+=6)p('#c09b6a',x+n,34,2,4);
    }
    for(const [x,y] of [[12,30],[15,23],[20,16]]) baguette(x,y);
    buns(70,20);buns(84,24);
    p('#c7bb9e',43,38,8,5);p('#c7bb9e',93,38,8,5);
  } else if(kind==='cooling-rack') {
    shadow(5,52,83,7);
    for(const x of [6,78]) {p('#494c49',x,7,4,48);p('#343837',x+1,55,6,4);}
    for(const y of [15,30,46]){
      box(4,y,78,3,6,'#949387','#636961','#494d49');
      for(const x of [11,36,59]) loaf(x,y-9);
    }
  } else if(kind==='bakery-counter'||kind==='kneading-table') {
    shadow(7,h-12,w-18,7);
    for(const x of [8,w-20]) box(x,h-25,6,14,3,'#8e775b','#785e45','#584837');
    box(3,30,w-17,15,11,'#ae9775','#82674e','#594a3d');
    p('#624f40',4,39,w-20,3);p('#bba17b',21,32,17,1);p('#655040',w-45,33,13,1);
    if(kind==='bakery-counter') {
      for(let x=12;x<w-30;x+=44) {
        box(x,26,33,3,5,'#94724c','#71563c','#614c39');
        if(x===12) baguette(x+2,24);
        else if(x===56) buns(x+7,17);
        else loaf(x+4,15);
      }
      p('#81978e48',5,14,w-20,19);
      p('#9ba99b',w-48,15,7,1);p('#77867d',w-44,16,3,2);p('#77867d',w-42,18,2,2);
      p('#c3cbb9',6,13,w-22,2);p('#87968a',5,15,3,18);p('#87968a',w-19,15,3,18);
    } else {
      oval(39,23,17,7,'#cbb89a');p('#ab8963',72,16,27,5);p('#d2ad7c',68,15,32,3);
    }
  } else if(kind==='bread-oven') {
    shadow(7,83,139,8);
    // The masonry rises from the rear of the oven into the north wall face.
    p('#5c5048',17,-5,132,29);
    for(const y of [-4,6,16]) {
      p('#867261',18,y,130,8);
      for(let x=22+(y===6?13:0);x<147;x+=27) p('#64574c',x,y,2,8);
    }
    box(8,29,132,55,12,'#988270','#735c50','#514741');
    for(let row=0;row<5;row++) {
      p('#5c5047',9,32+row*10,130,2);
      for(let x=18+row%2*15;x<136;x+=30) p('#605046',x,23+row*10,2,9);
    }
    const rx=23;
    for(const cx of [46,103]) {
      oval(cx,61,rx,21,'#ac8a69');oval(cx,63,rx-5,16,'#3b3633');
      for(let i=0;i<6;i++) {
        const a=(i+1)*Math.PI/7, bx=Math.round(cx+Math.cos(a)*(rx-2)),by=Math.round(61-Math.sin(a)*20);
        p('#705c4c',bx,by,2,4);
      }
      p('#423a354d',cx-12,35,18,4);p('#40393365',cx-8,38,15,3);
      p('#3b3430',cx-rx+5,61,2*rx-9,14);p('#bf8355',cx-rx+7,71,2*rx-14,3);
    }
    box(8,79,133,6,4,'#a99578','#6a594b','#57483f');
    box(113,-9,17,38,5,'#a79a84','#796c5e','#5b5148');
  } else if(kind==='family-aprons') {
    p('#604f43',2,8,89,6);
    for(const [i,color] of ['#b47960','#65786b','#8c9fad'].entries()) {
      const x=6+i*29;p('#b9ab8e',x+9,9,2,6);
      p(color,x+6,16,11,13);p(color,x+2,27,20,20);p('#51474455',x+17,29,5,18);
      p('#d6c3a7',x+6,31,11,2);
    }
  } else if(kind==='bread-van') {
    shadow(8,78,139,10);
    for(const x of [33,121]) {oval(x,73,11,12,'#343538');oval(x,73,5,6,'#92928a');}
    box(5,35,98,34,10,'#d1bfa1','#b7a383','#8c7963');
    box(108,47,34,23,7,'#bcae92','#a38e73','#776756');
    box(109,34,24,17,6,'#c4b69a','#617876','#4e605f');
    p('#a35f51',5,57,98,7);p('#a35f51',108,57,33,5);loaf(33,39,2);
    p('#d8bc82',136,57,8,4);
    p('#73695a',6,66,95,3);p('#96816a',12,62,14,3);p('#775f50',81,63,8,3);
    p('#d6c4a6',76,44,14,1);p('#82786a',102,41,2,24);
    p('#86938a',111,36,13,2);p('#5a5c55',114,54,7,2);
  } else if(kind==='pew') {
    shadow(7,24,w-16,5);
    for(const x of [7,w-17]) p('#605044',x,18,6,8);
    box(4,15,w-14,7,5,'#aa8762','#866747','#66503d');
    box(4,7,w-14,8,3,'#b69a75','#936f51','#624d3e');
    p('#80674e',25+(tileX%3)*13,7,16,2);p('#c5a580',66,15,11,1);
  } else if(kind==='chapel-flowers') {
    shadow(8,57,17,5);
    oval(16,56,10,3,'#745f4a');oval(15,55,9,2,'#ad9776');
    p('#79664f',14,31,5,24);p('#bea684',14,32,2,22);
    oval(16,51,4,3,'#a88d68');
    for(const [y,span] of [[23,20],[26,16],[29,10],[32,6]]) {
      p('#958165',16-span/2,y,span,3);p('#c4ac85',16-span/2,y,span-3,1);
    }
    // Layer roses into one broad bouquet with a scalloped edge above the narrow bowl.
    oval(16,18,14,8,'#687761');
    for(const [x,y,petal,light] of [
      [7,16,'#bcae95','#dfd3b8'],[14,11,'#c7b99f','#eadcc3'],
      [22,13,'#a78380','#d2a9a2'],[25,20,'#c1b197','#e6d4b8'],
      [16,21,'#b58e89','#ddb2a8'],[9,22,'#bcac96','#e4d5bd']
    ]) {
      oval(x,y,4,4,petal);p(light,x-3,y-2,5,2);p(light,x-3,y,2,2);
      p('#8e776975',x+1,y+1,2,2);
    }
    // The two ivory bow tails face the pews.
    const ribbon=(x,y,w,h,color)=>p(color,tileX===31?x:32-x-w,y,w,h);
    ribbon(9,26,6,3,'#c5b8a7');ribbon(19,25,6,4,'#e1d3bb');
    ribbon(15,27,5,4,'#d7c7ad');
    for(let n=0;n<13;n++){
      ribbon(14-Math.floor(n/3),31+n,3,1,'#c7b8a2');
      ribbon(19+Math.floor(n/4),30+n,3,1,'#e0ceb4');
    }
  } else if(kind==='altar') {
    shadow(6,84,w-22,6);
    box(2,83,w-17,6,7,'#c0b6a4','#988f83','#726e67');
    const cx=w/2-3;
    for(let i=0;i<146;i++){
      const t=Math.PI*i/145, x=Math.round(cx+77*Math.cos(t)),y=Math.round(52-43*Math.sin(t));
      p('#8b7766',x,y,6,8);p('#d4c7ac',x,y,4,5);
    }
    for(const x of [cx-77,cx+77]) {p('#a79b84',x,51,7,28);p('#e1d3b7',x,52,3,25);}
    // Two soft folds of ceremony voile gathered at the arch's crown and side ties.
    for(let side of [-1,1]) for(let i=0;i<71;i++) {
      const bx=cx+side*i, by=14+Math.round(28*i/70+9*Math.sin(Math.PI*i/70));
      p('#d2c6b18c',bx,by,1,6);
      p('#e4d6bc',bx,by+5,1,1);
    }
    for(let i=0;i<=12;i++){
      const t=Math.PI*i/12, bx=Math.round(cx+77*Math.cos(t)),by=Math.round(51-43*Math.sin(t));
      if(i===3||i===9){p('#706d55',bx,by+1,4,7);continue;}
      bloom(bx,by,i%3?'#bb9692':'#d2c1a7');
      if(i<=2 || i>=10 || i===6) bloom(bx-4,by+5,i%2?'#d6c7b0':'#bc9292');
      if(i===8||i===11){p('#727b60',bx+3,by+2,2,8);p('#a98c86',bx+3,by+9,4,3);}
    }
    box(58,69,100,10,6,'#e5d4b8','#c7b7a1','#a29887');
    for(const x of [65,145]) {p('#ac9271',x,54,4,13);p('#ead5a6',x+1,51,2,4);}
    for(const x of [32,181]) {
      box(x-8,74,15,7,3,'#ad9b7e','#87745f','#675b51');
      p('#74826a',x-2,55,4,18);
      for(const [dx,dy,c] of [[-7,3,'#ad8587'],[5,1,'#d7c6b0'],[-2,-4,'#c49b97'],[0,7,'#d4b7aa']]) {
        bloom(x+dx,60+dy,c);
      }
    }
  }
}
