// Coordinates in the landmark sprites are native map pixels (32 per cell).
const serverSoilTiles = new Map();

function isServerTrail(x, y) {
  return (x >= 20 && x <= 22 && y >= 14) ||
    (x >= 5 && x <= 38 && y >= 14 && y <= 15) ||
    (x >= 31 && x <= 32 && y >= 15 && y <= 25) ||
    (x >= 16 && x <= 32 && y >= 24 && y <= 25) ||
    (x >= 5 && x <= 7 && y >= 5 && y <= 18) ||
    (y >= 4 && y <= 5 && x >= 5 && x <= 38);
}

function drawServerGround(layer, ending, x, y) {
  const dirt = isServerTrail(x,y);
  const variant = ((x*17 ^ y*29 ^ x*y*3) >>> 0) % 12;
  const key = variant + (dirt ? 12 : 0);
  if (!serverSoilTiles.has(key)) {
    const tile = document.createElement('canvas');
    tile.width = tile.height = 32;
    const g = tile.getContext('2d');
    const rand = StreetGen.random('server-soil-' + key);
    const tones = dirt ? ['#806448','#876a4e','#735a42','#96795b','#6b5b4c'] :
      ['#66784c','#708152','#576c45','#788a58','#63754c'];
    g.fillStyle = dirt ? '#80654b' : '#64794e';
    g.fillRect(0,0,32,32);
    for (let i=0; i<45; i++) {
      const col = 2*Math.floor(rand()*16), row = 2*Math.floor(rand()*16);
      g.fillStyle = tones[Math.floor(rand()*tones.length)];
      const w = 2+2*Math.floor(rand()*3);
      g.fillRect(col,row,w,2);
      if (i%3 === 0) g.fillRect(col+2,row+2,w-2,2);
    }
    serverSoilTiles.set(key,tile);
  }
  layer.drawImage(serverSoilTiles.get(key),0,0);
  const south = endingTile(ending,x,y+1);
  if (dirt || !isServerTrail(x,y+1) || south === '#' || south === ' ') return;
  layer.fillStyle='#71573f';
  layer.fillRect(0,26,32,6);
  for (let col=0; col<32; col+=4) {
    const drop=(variant+col/4*3)%4;
    layer.fillStyle='#536940'; layer.fillRect(col,25,4,1+drop);
    layer.fillStyle=drop%2 ? '#876d4e' : '#614f3d';
    layer.fillRect(col+1,29+drop%2,3,2);
  }
}

// The back edge rises to the right. The visible roof catches light; the right wall is in shade.
function serverBlockFaces(p, x, y, w, h, depth, roof, side) {
  for (let step=1; step<=depth; step++) {
    p(roof,x+step*2,y-step,w,1);
    p(side,x+w+(step-1)*2,y-step+1,2,h);
  }
}

// Base bounds and cast length in pixels. Open gates cast separate tower shadows.
const serverCastProfiles = {
  'sora-station': [[3,57,120,8]], pekodam:[[7,118,79,17]],
  aquamarine:[[2,92,218,3]], 'rabbit-office':[[4,55,115,10]],
  'sakura-tree':[[71,82,19,9],[35,82,89,15]],
  'menya-botan':[[5,56,84,9]], babel:[[7,117,80,21]],
  pekoland:[[8,83,25,12],[94,83,25,12]],
  'diamond-rack':[[5,54,69,5],[85,53,28,6]], creeper:[[7,30,15,5]],
};

function drawServerShadows(layer, scenery) {
  for (const item of scenery) {
    for (const [left,base,width,length] of serverCastProfiles[item.kind] ?? []) {
      const x = item.x*32+left, y = item.y*32+base;
      for (let row=0;row<length;row++) {
        const offset = Math.floor(row*1.5);
        layer.fillStyle = row < 3 ? '#21282674' : row < length-2 ? '#222a2856' : '#26302b34';
        layer.fillRect(x+offset,y+row,width-Math.floor(row/2),1);
      }
    }
  }
}

function serverPixels(p, x, y, scale, colors, rows) {
  rows.forEach((row, dy) => {
    for (let dx = 0; dx < row.length; dx++) {
      const color = colors[row[dx]];
      if (color) p(color, x+dx*scale, y+dy*scale, scale, scale);
    }
  });
}

function serverSign(p, x, y, letters, color, scale = 1) {
  const glyphs = {
    A:['010','101','111','101','101'], D:['110','101','101','101','110'],
    E:['111','100','110','100','111'], K:['101','110','100','110','101'],
    L:['100','100','100','100','111'], N:['1001','1101','1101','1011','1001'],
    O:['111','101','101','101','111'], P:['110','101','110','100','100'],
    R:['110','101','110','101','101'], S:['111','100','111','001','111'],
  };
  for (const letter of letters) {
    const glyph = glyphs[letter];
    serverPixels(p,x,y,scale,{'1':color},glyph);
    x += (glyph[0].length+1)*scale;
  }
}

const serverLandmarks = {
  'sora-station'(p) {
    serverBlockFaces(p,3,46,118,10,4,'#a79578','#574a3e');
    serverBlockFaces(p,1,13,117,9,5,'#a0adad','#43525b');
    p('#413e39',3,47,122,13); p('#927a5f',3,45,122,10);
    p('#c4af81',4,53,120,2);
    for (const x of [12,107]) {
      p('#685a4d',x,19,6,29); p('#a08b70',x,21,2,26);
    }
    p('#414f58',1,13,125,10); p('#768b9a',6,7,114,9);
    p('#92a4ac',10,5,106,4); p('#bba681',3,21,122,2);
    p('#4a5158',36,20,56,19); p('#9aabb2',38,21,52,15);
    p('#43596b',40,23,48,11); serverSign(p,49,24,'SORA','#e1d7b6',2);
    p('#645440',21,41,27,3); p('#8d7558',21,38,27,3);
    p('#6a5749',23,43,3,4); p('#6a5749',43,43,3,4);
  },
  pekodam(p) {
    serverBlockFaces(p,6,113,80,8,4,'#979991','#494d4c');
    p('#454746',6,113,84,9); p('#767876',8,110,78,5);
    serverBlockFaces(p,29,18,32,12,3,'#b4c3c2','#677883');
    serverBlockFaces(p,49,38,22,11,3,'#90a6b2','#415668');
    const c={w:'#c5c8bd',s:'#929c9d',b:'#597d99',h:'#89aab7',n:'#495561',
      p:'#bb9394',y:'#bfaa70',r:'#aa735f',d:'#384149'};
    serverPixels(p,8,1,4,c,[
      '     ws    sw','     wp    pw','     wp    pw','     ws    sw',
      '     bwwwwwsb','     bhwwwshb','      ydddy','      ssrss',
      '  hhbbnsssn bbhh',' hhbbbhbbbhbbbbbh',' bsssnbyyybnnsssb','  wwsbbbsbbbswws',
      '  wws bbnbb  wws','  ssn ssnss  ssn','  bbn bsssb  bbn',
      '  bbd sbnbs  dbb','  nnd ww ww  dnn','      ww ww',
      '     bbs sbb','     bbs sbb','     nns snn','    wwss ssww',
      '    wwss ssww','    wsss sssw','    bbbb bbbb','   bbrrb brrbb',
      '  nnrrrb brrrnn',
    ]);
    p('#6b7f88',58,38,7,11); p('#4f6270',66,47,5,16);
    p('#777f80',46,77,5,15); p('#d7d7c7',23,89,4,8);
  },
  aquamarine(p) {
    // An inset dock gives the ship a waterline within the dry set.
    p('#4b5350',1,60,222,35); p('#405d62',4,62,216,31);
    for(const [x,y,w] of [[7,78,19],[46,87,29],[149,85,19],[188,72,26]])
      p('#688488',x,y,w,2);
    p('#696052',2,91,219,3);
    for(let row=0; row<7; row++) p('#253d437f',48+2*row,77+row,129-row*3,1);
    for (const [x,height] of [[66,46],[112,56],[157,40]]) {
      const top=65-height;
      p('#5c4e40',x,top,4,height); p('#a28a64',x,top,1,height);
      p('#986153',x+3,top,19,6); p('#724e49',x+13,top+5,9,3);
      const w=height-9;
      p('#685a4a',x-Math.floor(w/2),top+12,w+3,3);
      for(let row=0;row<17;row++){
        const margin=Math.floor(row/5);
        p(row>13?'#a59c87':'#c3bba4',x-Math.floor(w/2)+margin,top+15+row,w-margin*2,1);
      }
      p('#777466',x-1,top+16,2,14);
      for(let row=0;row<16;row++) {
        const fold=Math.floor(row/4);
        p('#998f7d',x+Math.floor(w/2)-8,top+15+row,7-fold,1);
      }
    }
    p('#7c5949',34,56,145,15); p('#a38360',31,55,151,3);
    p('#987557',163,48,22,11); p('#bd9b74',161,47,25,3);
    for (let y=0;y<14;y++) p(y<4?'#79604e':'#53463d',26+y*2,65+y,166-y*3,1);
    for(let x=51;x<=151;x+=16) p('#373838',x,61,6,5);
    for(let i=0;i<15;i++) p('#9b8467',16+i*2,48+i,4,2);
  },
  'sakura-tree'(p) {
    p('#535b46',10,77,139,13); p('#667153',14,74,130,12);
    p('#685649',72,38,16,44); p('#8b7461',72,52,5,26);
    for(let i=0;i<13;i++){
      p('#715d50',49+i*2,34+i*2,7,5);
      p('#776452',83+i*2,56-i*2,6,4);
    }
    for(const [x,y,w,h] of [[7,32,42,20],[24,18,46,27],[54,7,55,29],[86,18,45,25],[113,31,38,22],[42,32,55,20],[75,31,44,17]]){
      serverBlockFaces(p,x,y,w-4,h,3,'#d5b1b8','#886d7d');
      p('#936f7e',x,y+5,w,h); p('#ba929e',x,y,w-4,h);
      p('#cfacb4',x+4,y,w-11,4); p('#d7b7bd',x+7,y+7,5,3);
      p('#a38190',x+w-12,y+h-6,8,3);
    }
    for(const [x,y] of [[31,72],[54,79],[102,77],[126,68]]) p('#be99a5',x,y,4,2);
  },
  'menya-botan'(p) {
    serverBlockFaces(p,7,24,78,30,4,'#b1997e','#665343');
    serverBlockFaces(p,4,16,82,8,4,'#9a998a','#4c4e48');
    p('#44413b',4,55,89,6); p('#806b54',7,23,82,32);
    p('#535550',4,15,88,10); p('#797a6b',8,12,79,5);
    p('#423d37',13,28,68,22); p('#b69c79',9,46,79,4);
    for(const x of [14,31,48]){p('#975e56',x,24,15,13);p('#bf9a84',x+6,27,3,6);}
    p('#796154',67,19,15,3); p('#bb8763',68,22,13,15); p('#c5ad85',70,25,9,3);
    for(const x of [18,43,65]){p('#b9b4a0',x,42,11,2);p('#8b8b7f',x+2,44,7,2);}
    // Oversized bowl and raised chopsticks above the shopfront.
    p('#d0c8ae',24,8,38,3);p('#a39e8c',27,11,32,4);p('#b8af97',33,15,20,3);
    p('#b99b63',28,7,30,2);
    for(let i=0;i<8;i++){p('#bba37c',48+i,7-i,8,1);p('#a38b66',57+i,7-i,6,1);}
  },
  babel(p) {
    for(const [x,y,w,h] of [[6,91,84,29],[13,66,70,27],[21,43,54,25],[29,24,38,21],[36,10,24,16]]){
      serverBlockFaces(p,x,y,w-3,h,4,'#b4a58b','#665d51');
      p('#776b5f',x,y,w,h); p('#988c78',x+2,y+2,w-5,h-4);
      for(let col=x+6;col<x+w-5;col+=12){p('#57534e',col,y+7,6,h-10);p('#71685e',col-1,y+9,1,h-12);}
      p('#b0a28b',x-2,y,w+4,3);
      for(let i=0;i<w;i+=4) p('#b1a28a',x+i,y+h-4-Math.floor(i/w*9),4,3);
      p('#46423a46',x+w-12,y+3,10,h-3);
      p('#554d414a',x+2,y+3,w-14,2);
    }
    p('#766453',46,2,3,9);p('#ae6a61',49,2,10,5);
  },
  pekoland(p) {
    for(const x of [8,94]){
      serverBlockFaces(p,x,40,25,43,4,'#cbb9b1','#897980');
      serverBlockFaces(p,x-4,34,31,7,3,'#b99daf','#766578');
      p('#837581',x,40,26,46);p('#c0acaa',x+2,41,21,40);
      p('#98a7a7',x+1,69,23,6);p('#635267',x+8,54,8,11);
      p('#826c83',x-4,33,34,8);p('#ab95a4',x,25,26,9);p('#c3aabe',x+5,17,16,9);
      p('#a99878',x+11,7,2,12);p('#b98183',x+13,7,9,5);
    }
    p('#766578',30,41,68,16);p('#ae909c',30,40,68,4);
    serverSign(p,46,46,'PEKOLAND','#ecdbb8');
    for(const x of [50,68]){p('#bcb8aa',x,15,8,24);p('#c4989b',x+2,19,3,15);}
    p('#c8c4b7',48,32,31,9);
    p('#9b836f',34,78,59,4);p('#c1a49a',34,81,59,3);
  },
  creeper(p) {
    serverPixels(p,5,0,2,{g:'#718a53',l:'#97a96c',s:'#526f46',d:'#334335',k:'#202726'},[
      'llllglggs','glgggllgs','gkkggkkgs','gkkggkkss','sggkkgggs','ggkkkkgls','lgkggkggs','ssggggsss',
      '  gglgs','  slggs','  gggls','  gsggs','  gggss',' lgg ggs',' sgg sgs',' ddd ddd',
    ]);
  },
  'diamond-rack'(p) {
    p('#49453d',3,54,122,7); p('#8a765c',4,52,119,5);
    for (const x of [7, 69]) p('#74614d',x,41,4,12);
    p('#50463e',4,10,72,37);p('#806b52',5,9,70,3);
    for(const x of [8,31,54]){p('#65574b',x,15,19,24);p('#473f39',x+1,16,17,22);}
    const colors={h:'#9b7854',b:'#604f3f',t:'#55a9a5',l:'#9bdcd0',d:'#326e72',w:'#a8906c',s:'#534b46'};
    serverPixels(p,8,16,2,colors,[' llllt','    tlt','    htlt','   hb tl','  hb   t',' hb','hb']);
    serverPixels(p,33,16,2,colors,['      l','     lt','    ltd','   ltd','t ltd',' ttd',' hdt','hb  t']);
    serverPixels(p,56,17,2,colors,['    lt','   lttl','  htllll','  bhtltt','  hb ttd',' hb   d','hb']);
    // The visible wooden neck and crossbar distinguish the full set from a wearer.
    p('#685641',96,12,4,40);p('#a68e69',85,19,27,3);
    serverPixels(p,81,4,2,colors,[
      '    lllllll','    ltttttd','    ltdddtd','    td   td','      ww',
      '  llltt tttlll','  ltttlllttttd','  tddttttttddd','     tttttd',
      '     ltldtd','     tttttd','     dddddd','     lttttd','     lttttd',
      '     ttd td','     ttd td','     ttd td','     ddd dd','     www ww',
      '    lttt ltt','    tttd ttd','    dddd ddd',
    ]);
    p('#766b5b',85,48,30,4);p('#9e9784',83,51,34,3);
  },
};
