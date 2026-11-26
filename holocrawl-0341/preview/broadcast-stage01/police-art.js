// The emblems are original low-resolution precinct patches. Paint all edges on the tile grid.
function policePolygon(p, color, points) {
  const ys = points.map(point => point[1]);
  for (let y = Math.min(...ys); y < Math.max(...ys); y++) {
    const cuts = [];
    for (let i = 0; i < points.length; i++) {
      const [x1,y1] = points[i], [x2,y2] = points[(i+1)%points.length];
      if ((y1 > y+0.5) !== (y2 > y+0.5))
        cuts.push(Math.round(x1 + (y+0.5-y1)*(x2-x1)/(y2-y1)));
    }
    cuts.sort((a,b)=>a-b);
    for (let i=0;i<cuts.length;i+=2) p(color,cuts[i],y,cuts[i+1]-cuts[i],1);
  }
}

function drawPoliceGround(p,x,y) {
  if (x>=25 && x<=36 && y<=7) {
    p(y<=5?'#5665674a':'#77705e38',0,0,32,32);
    if (y===5) {
      p('#444e50',0,25,32,3);
      p('#8a8f82',0,25,32,1);
    }
  } else if (x>=25 && y>=17 && y<=30) {
    p('#353d4048',0,0,32,32);
    if (x>=30 && x<=36 && [20,24].includes(y)) p('#ad9c7380',0,14,32,3);
    if (x===30 && y>=20 && y<=24) p('#ad9c7380',2,y===20?14:0,3,y===24?17:y===20?18:32);
    if (x>=28 && x<32 && y===27) {
      p('#3b403e',0,9,32,9);
      for(let i=0;i<32;i+=6) p('#818983',i,10,3,7);
    }
  } else if(y>=20 && y<27 && x<=23) {
    if((x+y)%2===0) p('#92999419',0,0,32,32);
    if(x===5 || y===26) p('#53646a55',0,0,32,32);
  } else if(y<=7) {
    p('#56514332',0,0,32,32);
  }
}

function drawPoliceScenery(p,{kind,width,depth,bedding}) {
  const w=width*32,h=depth*32;
  const ink='#283238',steel='#64757b',edge='#98a39e',blue='#405863',paper='#d4c9ac';
  const poly=(color,points)=>policePolygon(p,color,points);
  const shadow=(x,y,sw,sh)=>p('#151c2199',x,y,sw,sh);
  const cabinet=(x,y,cw,ch,face)=>{
    shadow(x+4,y+5,cw,ch);
    p(ink,x,y,cw,ch);p(face,x+2,y+2,cw-4,ch-5);
    p(edge,x+2,y+1,cw-4,2);p('#38444a',x+3,y+ch-6,cw-5,4);
  };
  const monitor=(x,y)=>{
    p(ink,x+11,y+16,4,6);p(ink,x+4,y+20,19,3);
    p(ink,x,y,28,18);p('#78888a',x+1,y+1,26,2);
    p('#476471',x+3,y+4,22,10);p('#89aaa7',x+5,y+6,10,2);p('#617e81',x+5,y+10,16,1);
  };
  const drawer=(x,y,cw)=>{
    p('#3d4b50',x,y,cw,12);p('#718084',x+1,y+1,cw-2,10);
    p('#b3b2a1',x+cw/2-4,y+3,8,2);p(ink,x+cw/2-3,y+5,6,2);
  };
  if(kind==='cell-divider') {
    // Edge-on return from the rear wall to the front grille.
    shadow(10,1,10,h);
    p('#35414a',5,0,8,h);p('#818f91',6,0,3,h);
    for(let y=0;y<h;y+=16) {
      p('#262f34',8,y,8,5);p('#a5afaa',6,y,5,2);
    }
    p('#566469',14,0,3,h);
  } else if(kind==='cell-grille') {
    // The rightmost tile of each bay is the open doorway. Its leaf is slid to the left.
    shadow(8,24,w-5,6);
    for(let x=11;x<w;x+=10) {
      p('#273239',x,1,5,25);p('#849392',x,2,2,22);
      p('#48585f',x+2,3,2,20);
    }
    p('#37454b',5,0,w-5,5);p('#a0aaa5',5,0,w-5,2);
    p('#435057',5,20,w-5,4);p('#85928e',6,20,w-6,1);
    for(const x of [5,w-32,w-5]) {
      p('#303b40',x,0,6,28);p('#939e99',x,1,2,25);
      p('#525e60',x-1,26,8,3);
    }
    p('#738487',w-32,5,30,2);p('#6e7c7c',w-32,17,30,2);
    p('#333d40',w-10,10,9,7);p('#b29b6c',w-9,11,7,4);p(ink,w-6,12,2,3);
  } else if(kind==='cell-cot') {
    shadow(6,13,25,44);shadow(8,56,21,5);
    // Open tubular headboard behind the higher end of the mattress.
    for(const x of [2,27]) {
      p(ink,x,3,3,55);p('#889796',x,3,1,12);
      p(ink,x,56,3,6);p('#58666a',x,56,1,4);
    }
    p(ink,4,2,24,4);p(edge,4,2,24,1);
    for(const x of [8,15,22]) p(steel,x,6,2,7);
    p('#525b5c',4,11,23,45);p('#929387',5,12,22,42);
    p('#c5c2af',5,12,21,39);p('#d5d0ba',6,12,19,2);
    const dx=bedding===2?1:0;
    poly('#8d9086',[[7+dx,18],[9+dx,16],[22+dx,16],[25+dx,19],[23+dx,25],[9+dx,25]]);
    poly('#ded8bf',[[7+dx,17],[10+dx,15],[21+dx,15],[24+dx,17],[23+dx,22],[20+dx,23],[9+dx,22]]);
    p('#f0e7cc',10+dx,16,10,2);
    const [cloth,fold,hem]=[
      ['#647887','#8899a0',28],['#8c7669','#ad9783',40],['#71816e','#97a18a',31],
    ][bedding];
    const slip=bedding===2?5:0;
    poly(cloth,[[4,hem+slip],[12,hem+slip],[15,hem],[26,hem],[28,hem+3],[28,54],[25,56],[4,54]]);
    poly(fold,[[4,hem+slip],[12,hem+slip],[15,hem],[26,hem],[26,hem+3],[16,hem+3],[13,hem+slip+3],[4,hem+slip+3]]);
    p('#454f51',26,hem+6,2,48-hem);p('#535d5d',6,53,19,2);
    p(ink,3,55,26,3);p('#919d98',4,55,23,1);
  } else if(kind.endsWith('-crest')) {
    const duck=kind==='subaru-crest';
    cabinet(0,4,w-3,h-8,blue);
    p('#63757a',3,8,w-9,5);p('#334953',3,16,w-9,32);
    for(const left of [7,88]) {
      for(let i=0;i<3;i++) p(i===1?'#b4a47e':'#687a7c',left,26+i*5,30-i*4,2);
    }
    // Deep lip, stepped shield and two different heraldic silhouettes.
    poly('#222d34',[[37,7],[89,7],[89,37],[83,46],[65,58],[45,48],[37,37]]);
    poly('#bdad82',[[38,5],[87,5],[87,35],[81,44],[63,55],[45,44],[38,34]]);
    poly(duck?'#3e657b':'#803e41',[[41,8],[84,8],[84,34],[78,42],[63,51],[47,41],[41,33]]);
    if(duck) {
      poly('#c8cebd',[[48,27],[54,28],[55,20],[61,16],[69,17],[73,22],[73,30],[70,36],[64,41],[53,39],[49,35]]);
      poly('#e3debd',[[55,25],[61,20],[69,21],[71,25],[70,30],[62,33],[56,31]]);
      poly('#d7a253',[[68,27],[80,26],[77,31],[69,32]]);
      p(ink,66,23,3,3);
      poly('#293c53',[[51,18],[55,12],[66,11],[71,15],[73,18],[76,19],[76,21],[52,21]]);
      p('#738aaa',55,14,12,2);p('#dbc584',61,15,4,4);p('#d3b26a',53,19,20,2);
      p('#98b5bd',53,34,8,2);
    } else {
      for(const x of [47,68]) {
        poly('#2c3039',[[x,15],[x+3,11],[x+10,11],[x+14,16],[x+12,23],[x+4,24],[x,20]]);
        p('#bc7373',x+4,15,6,5);
      }
      poly('#e2cbb4',[[48,24],[63,18],[78,24],[77,37],[64,45],[49,37]]);
      poly('#d46959',[[50,25],[62,20],[76,24],[64,30]]);
      poly('#b04747',[[50,27],[63,32],[63,42],[51,36]]);
      poly('#833c43',[[65,32],[76,27],[75,36],[65,42]]);
      p('#f4ddba',61,24,4,3);
      for(const [x,y] of [[52,29],[58,35],[68,34],[72,30],[68,38]]) p('#e8d2b1',x,y,3,3);
    }
    for(const x of [5,w-11]) for(const y of [10,49]) p('#abb1a7',x,y,2,2);
  } else if(kind==='cruiser') {
    shadow(7,50,147,29);shadow(27,76,108,6);
    poly(ink,[[2,44],[10,34],[36,30],[59,14],[106,14],[126,29],[145,32],[156,41],[155,66],[146,71],[13,71],[3,64]]);
    poly('#d0cfc1',[[5,44],[14,36],[39,32],[58,17],[106,17],[125,32],[145,35],[152,41],[151,55],[5,55]]);
    poly('#59747c',[[43,32],[61,19],[71,19],[66,33]]);
    poly('#455c68',[[76,19],[103,19],[119,32],[74,32]]);
    p('#8eafb0',56,27,9,2);p('#798f90',80,21,18,2);
    p('#354451',8,49,143,14);p('#84939a',8,48,141,2);
    p('#e2d9af',5,41,13,5);p('#a85a50',144,40,9,5);
    for(const x of [24,118]) {
      poly('#222a30',[[x,54],[x+5,49],[x+16,49],[x+21,54],[x+21,69],[x+16,74],[x+5,74],[x,69]]);
      p('#778187',x+6,55,10,12);p('#46525a',x+9,58,5,6);
    }
    p('#333f44',68,11,27,6);p('#b65952',69,10,10,5);p('#bcbbb0',79,11,5,4);p('#6388ae',84,10,10,5);
    poly('#ceb57b',[[77,38],[88,38],[88,46],[83,50],[78,46]]);
    p('#6e7575',65,36,2,12);p('#737c7b',99,36,2,12);
    p('#535c63',70,37,6,2);p('#58646a',104,37,6,2);
  } else if(kind==='case-board') {
    cabinet(5,4,w-10,52,'#926f53');
    for(const [x,y] of [[13,10],[38,26],[62,13],[93,19]]) {
      p('#614e44',x+2,y+2,19,23);p(paper,x,y,19,22);
      p('#788482',x+3,y+4,12,9);p('#90836e',x+3,y+16,9,2);p('#aa514e',x+8,y,3,3);
    }
  } else if(kind==='interview-table') {
    for(const y of [6,71]) {
      shadow(47,y+4,34,17);p(ink,45,y,32,19);p('#667672',48,y+3,26,12);
      p('#89918a',48,y+(y===6?1:14),26,3);
    }
    cabinet(12,28,102,38,'#736b5a');
    p('#a19579',15,30,96,20);p(paper,39,34,15,11);p('#9b917d',42,38,8,2);
    p(ink,81,39,13,6);p('#b25f51',83,40,3,2);
    p('#3b4546',24,32,5,9);p('#414d4c',26,28,10,3);p('#d8c693',33,29,8,3);
  } else if(kind==='observation-glass') {
    cabinet(0,1,w-4,h-5,'#455962');
    for(let i=0;i<3;i++) {
      const x=4+i*51;p('#60777d',x,4,48,17);p('#526871',x,15,48,6);
      poly('#899d9d',[[x+10,5],[x+17,5],[x+6,17],[x,17]]);
      p(edge,x+48,4,2,19);
    }
  } else if(kind==='front-desk' || kind==='radio-desk') {
    cabinet(2,15,w-7,43,blue);p('#8f8b77',3,15,w-9,17);p('#beb196',5,16,w-14,2);
    for(let x=13;x<w-24;x+=40) drawer(x,38,33);
    monitor(22,6);
    if(kind==='radio-desk') {
      cabinet(79,9,62,24,'#485458');
      for(let i=0;i<4;i++){p('#9ba196',84+i*13,16,9,2);p('#6e998a',84+i*13,21,3,3);}
      p(ink,132,1,2,13);
    } else {
      p('#525856',85,21,20,5);p(paper,121,20,18,9);
      p('#353c3c',173,17,17,8);p('#a5926c',174,15,14,5);
    }
  } else if(kind==='waiting-bench') {
    for(const x of [12,98]) p(ink,x,20,5,9);
    for(let x=4;x<120;x+=39) {
      shadow(x+3,8,36,17);p(ink,x,3,36,20);p('#5f7881',x+2,4,32,10);
      p('#829596',x+2,4,32,2);p('#495d65',x+2,16,32,5);
    }
  } else if(kind==='motor-lockers') {
    for(let x=3;x<w-10;x+=30) {
      cabinet(x,4,28,53,'#58686b');
      for(let i=0;i<3;i++) p('#394a50',x+5,11+i*3,17,1);
      p('#c1b699',x+6,24,10,4);p(ink,x+21,32,2,6);
    }
  } else if(kind==='booking') {
    cabinet(3,4,w-7,45,'#bcb6a3');
    for(let i=0;i<7;i++) p('#6b706c',7,9+i*5,i%2?15:w-18,1);
    p(ink,35,34,13,7);p(steel,39,31,6,5);p(ink,39,40,3,17);
    p('#424d52',11,54,49,4);
  } else if(kind==='gun-rack') {
    cabinet(1,1,w-6,h-6,'#838476');
    // Faded pegboard lets the dark silhouettes read against the station floor.
    for(let y=8;y<51;y+=8) for(let x=8;x<w-9;x+=8) p('#6d7269',x,y,2,1);
    p(steel,105,5,3,49);
    for(const [y,length,stock] of [[9,91,'#75513c'],[25,85,'#424b50'],[41,94,'#796047']]) {
      p('#b5ac90',25,y+3,3,8);p('#b5ac90',74,y+2,3,8);
      poly(ink,[[10,y+3],[24,y+3],[30,y],[length,y],[length,y+4],[57,y+4],
        [56,y+7],[44,y+7],[42,y+12],[37,y+11],[38,y+6],[28,y+6],[17,y+12],[10,y+12]]);
      poly(stock,[[11,y+5],[23,y+5],[32,y+2],[39,y+2],[39,y+5],[27,y+5],[16,y+10],[11,y+10]]);
      p('#909a97',43,y, length-44,1);p('#565d5b',55,y+2,18,3);
    }
    for(const y of [10,26,42]) {
      poly(ink,[[117,y],[143,y],[143,y+4],[129,y+4],[126,y+12],[119,y+12],[121,y+4],[117,y+4]]);
      p('#59656a',118,y,24,2);p('#695c4c',122,y+6,3,4);
    }
  } else if(kind==='patrol-gear') {
    shadow(4,h-14,w-6,10);
    for(const x of [5,62,116]) {
      p(ink,x,14,5,h-24);p(steel,x,14,2,h-27);
    }
    for(const y of [29,62]) {p(ink,3,y,w-9,6);p(steel,3,y,w-9,2);}
    p('#434c4d',2,h-16,w-7,9);p(edge,4,h-17,w-10,2);
    // Open U-shaped heads above the crossbar, with a visible gap between the prongs.
    for(const [x,y] of [[19,6],[45,10]]) {
      p('#39494d',x,y+17,4,64);p('#c0c6b9',x,y+15,2,63);
      for(const side of [-1,1]) {
        for(const [offset,dy,len] of [[10,0,8],[8,7,4],[6,10,4],[3,13,3],[0,15,3]]) {
          const px=x+side*offset;
          p('#3a494c',px-1,y+dy,5,len+2);p('#c6cbbd',px,y+dy,3,len);
        }
      }
      p('#67787a',x-1,y+23,5,4);
    }
    for(const [x,y] of [[58,40],[69,37]]) {
      p('#89928c',x,y,4,38);p('#293438',x+1,y+1,4,38);
      p('#252e33',x-1,y+12,8,3);p('#565d58',x+1,y+3,2,8);
    }
    for(const [x,y,c] of [[91,24,'#4e6470'],[77,35,'#455862']]) {
      poly(ink,[[x+4,y],[x+24,y],[x+28,y+5],[x+27,y+39],[x+22,y+47],[x+7,y+47],[x+1,y+40],[x,y+6]]);
      poly(c,[[x+5,y+2],[x+22,y+2],[x+25,y+5],[x+24,y+38],[x+20,y+44],[x+8,y+44],[x+3,y+39],[x+2,y+6]]);
      p('#95a3a2',x+3,y+6,2,31);p(ink,x+6,y+7,16,8);p('#819a9e',x+8,y+9,12,3);
      p('#a5aaa0',x+8,y+23,13,2);p('#7a8785',x+11,y+27,7,1);
    }
  }
}
