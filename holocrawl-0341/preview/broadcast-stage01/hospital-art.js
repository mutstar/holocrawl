function drawHospitalGround(p,x,y) {
  if (x>=1 && x<=6 && y>=4 && y<=11) {
    // Muted oak boards with staggered seams run from wall to wall.
    p('#776958',0,0,32,32);
    for(let j=0;j<32;j+=8) {
      p('#675d51',0,j,32,1);
      const board=x*3+y+j/8;
      if(board%3===0) p('#62594f',8+j/2,j,1,8);
      if(board%4===0) p('#837360',2,j+3,12,1);
    }
  } else if (y<9) {
    p('#6a928b59',0,0,32,32);
    p('#44595577',0,0,32,1);p('#44595577',0,1,1,31);
  } else if (y>=30 && x>=19) {
    p('#343c3d50',0,0,32,32);
    if (x>=23 && x<=26 && [31,35].includes(y)) p('#b9ad825c',0,14,32,3);
  } else if (y<36 && ((x+y)%2===0)) {
    p('#a4b8a21c',0,0,32,32);
  }
}

function drawHospitalScenery(p,{kind,width}) {
  const w=width*32,ink='#293b3d',steel='#617775',light='#a6b3a7',cream='#dbdcca';
  const mint='#86a59b',blue='#86bcca',pink='#cf9da9';
  const shadow=(x,y,sw,sh)=>p('#18212870',x,y,sw,sh);
  const box=(x,y,bw,bh,face)=>{
    shadow(x+3,y+4,bw,bh);p(ink,x,y,bw,bh);
    p(face,x+2,y+2,bw-4,bh-5);p(light,x+2,y+1,bw-4,2);
  };
  const paw=(x,y,c,s)=>{
    const rows=['.##.##.','###.###','.##.##.','...#...','#.###.#','#######','.#####.'];
    rows.forEach((row,j)=>Array.from(row).forEach((v,i)=>{if(v==='#')p(c,x+s*i,y+s*j,s,s);}));
  };
  const screen=(x,y)=>{
    box(x,y,29,20,'#2d4248');
    for(const [dx,dy,len] of [[4,12,6],[10,10,2],[12,6,2],[14,11,2],[16,14,2],[18,11,7]]) p('#a3c1a6',x+dx,y+dy,len,2);
    p('#7d9695',x+12,y+20,4,4);p(ink,x+7,y+24,16,2);
  };
  const bed=(x,y,sheet)=>{
    shadow(x+5,y+7,23,50);
    for(const xp of [x+1,x+25]) {p(ink,xp,y+1,3,54);p(light,xp,y+1,1,45);}
    p(steel,x+2,y+1,24,3);p(light,x+3,y+1,22,1);
    p('#9caaa1',x+4,y+8,21,41);p(cream,x+4,y+8,20,37);
    p('#88968c',x+7,y+13,15,8);p('#ece8ce',x+7,y+11,15,8);p('#f4eed9',x+9,y+10,10,2);
    p(sheet,x+3,y+25,23,24);p('#b7c7b9',x+3,y+24,23,3);
    p('#506663',x+23,y+28,3,21);p(steel,x+1,y+50,27,4);
    for(const xp of [x+3,x+22]) p(ink,xp,y+54,4,4);
  };
  if(kind==='director-portrait') {
    box(15,0,60,59,'#927e5d');p('#c4b38d',18,3,54,52);
    p('#4f6666',21,6,48,46);
    const portrait=[
      '..w..........w..','..ww........ww..','..wpw..mw..wpw..',
      '..wpwwmwwwwwpw..','...wwmmwwwwww...','..wwmmwwwswwww..',
      '..wwwwwwssssww..','.wwwsasasasswww.','.wwwsksssksswww.',
      '..wwssssssssww..','...wwssppssww...','....wwssssww....',
      '...wwwbkmbwww...','..wwwwbkmbwwww..','.wwwbwwmmwwbwww.',
    ];
    const colors={w:cream,p:'#c5a5a0',m:mint,b:'#647b80',k:ink,s:'#d3b99e',a:'#877d71'};
    portrait.forEach((row,y)=>Array.from(row).forEach((c,x)=>{if(colors[c])p(colors[c],21+x*3,7+y*3,3,3);}));
    box(84,10,31,38,'#806f55');p('#cfc7a9',87,13,25,30);
    p('#847659',92,18,15,2);p('#a19881',91,23,17,1);p('#a19881',92,26,14,1);
    p('#a26651',102,32,5,5);p('#af8e69',103,37,3,3);
  } else if(kind==='director-desk') {
    // The high-backed chair rises above the desktop. Its arms sit behind the wood top.
    box(48,1,31,32,'#526967');p('#748b7d',51,5,24,2);
    p(ink,44,22,6,10);p(ink,77,22,6,10);
    shadow(7,36,w-10,23);p('#53453b',5,31,w-12,24);
    p('#92755a',7,37,w-17,14);
    for(const x of [8,93]) {
      p('#694f40',x,38,23,12);p('#b8a07a',x+8,41,8,2);p('#403d37',x,50,5,9);
    }
    p('#473f39',2,25,w-6,13);p('#ab8d6d',3,24,w-8,10);
    p('#c5ab86',4,24,w-10,2);p('#987b5e',5,27,19,1);
    p('#556e64',43,25,38,9);p('#d9d5b9',53,25,17,7);p('#9d9b86',56,27,10,1);
    p(ink,17,23,13,5);p('#879388',20,15,3,9);
    p('#677e6c',15,13,15,5);p('#e0c995',16,18,14,2);
    p('#a69c81',96,20,9,8);p(cream,96,20,9,2);p('#67594b',98,21,5,2);p(light,105,22,3,4);
  } else if(kind==='fox-sign') {
    box(1,3,90,53,'#4a6968');p('#77918a',5,7,82,2);
    for(const x of [6,76]) {p('#a9a58c',x,22,10,2);p('#829b91',x,27,10,2);}
    // Ears, cheek tufts and a teal forelock above a doctor's bag.
    const crest=['.w.......w.','.ww..m..ww.','.wcwwmwwcw.','..wwmmwww..','.wwwmwwwww.','ww.kwwwk.ww','.wwwwkwwww.','...wwwww...'];
    crest.forEach((r,j)=>Array.from(r).forEach((v,i)=>{const c={w:cream,c:'#bf9d98',m:mint,k:ink}[v];if(c)p(c,27+i*3,9+j*3,3,3);}));
    p(ink,31,33,27,17);p('#879f94',33,35,23,12);p(cream,42,36,5,10);p(cream,39,39,11,4);
  } else if(kind==='ambulance') {
    shadow(5,60,117,18);
    // Broad box body, raised roof, sloping cab and a continuous faded vermilion stripe.
    p(ink,4,19,74,51);p(ink,74,31,19,39);p(ink,90,39,13,31);p(ink,100,46,12,24);p(ink,110,50,13,17);
    p('#c8cbbb',6,21,69,41);p('#e3dfc8',7,21,67,4);
    p('#aebcb2',76,34,15,29);p('#c6ccbd',90,42,10,21);p('#c1c6b6',100,49,10,14);p('#adb9b0',109,53,12,10);
    p('#466068',78,36,10,15);p('#68858a',89,43,8,8);
    p('#aa6358',6,51,68,5);p('#ad6b5f',75,55,45,4);
    p('#45565a',14,26,20,13);p('#809594',16,28,16,8);
    p('#4e6669',40,26,27,22);paw(44,30,blue,1);paw(56,34,pink,1);
    p('#677a79',37,25,2,36);p(cream,113,51,7,3);
    for(const x of [16,91]) {p(ink,x,58,16,15);p(ink,x+3,72,10,3);p(steel,x+4,62,8,8);p(light,x+6,64,4,4);}
    p(ink,22,14,27,6);p('#c88579',23,13,9,5);p(cream,32,14,6,4);p('#8baebc',38,13,10,5);
  } else if(kind==='nurses' || kind==='admissions') {
    const twin=kind==='nurses';
    box(3,14,w-9,42,'#768d85');p('#b5b7a1',5,15,w-14,16);p('#d1cbb1',6,15,w-16,2);
    for(let x=9;x<w-28;x+=36) {p('#5a706d',x,36,31,14);p('#8c9d91',x+2,38,27,10);p(ink,x+11,39,10,2);}
    screen(12,3);p(cream,48,20,14,7);
    if(twin) {
      screen(108,3);
      for(const [x,c] of [[59,blue],[84,pink]]) {p(ink,x-2,31,19,20);paw(x,33,c,2);}
    } else {p('#665f52',91,19,19,10);p('#c7b69b',93,18,15,6);}
  } else if(kind==='curtain') {
    p(steel,2,2,w-4,3);p(light,3,2,w-6,1);
    for(let x=6;x<w*0.66;x+=7) {
      const len=18+Math.floor(x/7)%3*2;p('#b6c1af',x,6,7,len);
      p('#819c93',x+4,7,3,len-1);p(steel,x+1,4,2,3);
    }
    p(steel,w-6,4,2,24);p(ink,w-10,27,9,3);
  } else if(kind==='bed') {
    bed(1,2,'#7b9c96');
  } else if(kind==='waiting') {
    for(const x of [3,33,63]) {
      shadow(x+2,8,28,16);p(ink,x,4,28,18);p('#869d93',x+2,5,24,9);
      p('#556e69',x+2,16,24,5);p(ink,x+4,21,3,5);p(ink,x+20,21,3,5);
    }
  } else if(kind==='gurney') {
    shadow(6,15,54,12);
    for(const x of [9,48]) {p(steel,x,20,3,7);p(ink,x-1,25,6,4);}
    box(3,5,54,15,'#c9c9b4');p('#e1dfca',6,7,12,8);p('#89a39c',22,7,32,9);
    for(const x of [4,55]) p(steel,x,2,2,17);p(light,7,19,47,2);
  } else if(kind==='monitor') {
    box(6,31,47,22,'#859991');screen(13,4);
    p(steel,24,29,4,5);p(cream,12,36,16,5);p('#455954',32,38,14,8);
    for(const x of [10,44]) p(ink,x,51,5,5);
  } else if(kind==='supply') {
    box(2,3,w-8,51,'#495e60');
    for(const y of [10,30]) {
      for(let i=0;i<5;i++) {
        const x=9+i*15,hh=8+i%3*2;
        p(i%2?'#a5b6aa':'#c2bba3',x,y+13-hh,9,hh);p('#ddd6b9',x+1,y+12-hh,7,2);
      }
      p(steel,5,y+14,w-15,3);
    }
  } else if(kind==='operating') {
    // Offset the lamp and its wheeled base from the table to keep both silhouettes legible.
    shadow(9,72,72,10);p(ink,12,72,25,5);p(steel,22,25,4,49);
    p(steel,24,21,18,5);p(light,23,21,17,2);
    bed(52,22,'#648f86');p(steel,48,52,6,13);p(steel,78,52,6,13);
    const disc=(cx,cy,r,c)=>{for(let j=-r;j<=r;j++){const span=Math.floor(Math.sqrt(r*r-j*j));p(c,cx-span,cy+j,span*2+1,1);}};
    disc(41,19,17,ink);disc(41,18,15,'#abb8a7');disc(41,18,12,'#7a8f82');
    for(const [x,y] of [[36,13],[46,13],[41,22]]) {disc(x,y,4,'#e5dfad');p('#faf0c4',x-1,y-2,3,3);}
  }
}
