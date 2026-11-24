// The exposed feeders continue below the walkable mesh at the same height.
function drawFeederTrench(p, width, wallEnd) {
  p('#292f32',0,0,width,64);
  p('#5f655f',0,0,width,2);
  p('#1e2528',0,4,width,7);
  for (const [y,body,light] of [[17,'#805c47','#a37c59'],[32,'#496566','#74908a'],[44,'#635f53','#8e8972']]) {
    p('#202729',0,y+3,width,6);
    p(body,0,y,width,6);
    p(light,0,y+1,width,1);
    for (let x=13;x<width;x+=32) {
      p('#394245',x,y-2,5,10);
      p('#93988a',x+1,y-2,2,8);
    }
    if (wallEnd) {
      const left=wallEnd==='left', socket=left?0:width-5;
      p('#242b2b',socket,y-3,5,12);
      p('#5e6862',socket,y-2,5,10);
      p(body,socket,y,5,6);
      p('#93988a',left?4:width-5,y-2,1,10);
    }
  }
  p('#171e21',0,54,width,5);
  p('#6d7066',0,60,width,2);
  p('#474c48',0,62,width,2);
}

function drawTowerGrate(paint, grate, x, y) {
  const {across} = grate;
  const p = across ? (color,u,v,w,h) => paint(color,v,u,h,w) : paint;
  const col = across ? y-grate.y : x-grate.x;
  const row = across ? x-grate.x : y-grate.y;
  const width = across ? grate.depth : grate.width;
  const depth = across ? grate.width : grate.depth;
  // The short access cover shows the middle of the same two-tile cable bed.
  const offset = depth===1 ? 16 : row*32;
  drawFeederTrench((color,left,top,w,h)=>{
    const start=Math.max(0,top-offset), end=Math.min(32,top+h-offset);
    if (end>start) p(color,left,start,w,end-start);
  },32);
  for(let u=2;u<32;u+=8) {
    p('#424d50',u,0,3,32);
    p('#7e8986',u,0,1,32);
  }
  for(let v=4;v<32;v+=10) p('#626d6a',0,v,32,2);
  for(const end of [0,29]) {
    if (row !== (end===0 ? 0 : depth-1)) continue;
    p('#697370',0,end,32,3);
    p('#8b9388',0,end,32,1);
  }
  if (col===0 || col===width-1) {
    const edge=col===0?1:27;
    p('#3c4242',edge,0,4,32);
    p('#a39469',edge+1,0,2,32);
    for (const v of [2,23]) p('#575e5c',edge,v,4,5);
  }
}

function drawTowerWalkway(p, ending, x, y) {
  const grate = ending.grates.find(g => x>=g.x && x<g.x+g.width && y>=g.y && y<g.y+g.depth);
  if (grate) {
    drawTowerGrate(p,grate,x,y);
    return;
  }
  // Broad steel sheets span several cells. Alternate the treads in map coordinates.
  const band = Math.floor(y / 2);
  const plate = Math.floor((x + band) / 3);
  p((band + plate) % 3 === 0 ? '#505557' : '#4e5355', 0, 0, 32, 32);
  const wear = StreetGen.random(`tower-treads:${x},${y}`);
  for (let row = 0; row < 4; row++) {
    const offset = row % 2 === 0 ? 3 : 11;
    for (const u of [offset, offset + 16]) {
      if (wear() < .18) continue;
      const v = row*8 + 3;
      const tip = row % 2 === 0 ? u+2 : u;
      const foot = row % 2 === 0 ? u : u+2;
      p('#636969', tip, v, 2, 1);
      p('#5e6363', u+1, v+1, 2, 1);
      p('#464b4c', foot, v+2, 2, 1);
    }
  }
  if (y % 2 === 0) p('#43494b', 0, 0, 32, 1);
  if ((x + band) % 3 === 0) {
    p('#43494b', 0, 0, 1, 32);
    if (y % 2 === 0) p('#77796e', 3, 3, 2, 1);
  }
  if (wear() < .20) {
    const u = 3 + Math.floor(wear()*18), v = 3 + Math.floor(wear()*21);
    p('#5d554e', u, v, 7, 2);
    p('#75665a', u+1, v, 3, 1);
  }
  // Room thresholds stay flush; the edging follows only walls.
  if (endingTile(ending,x-1,y) === '#') p('#6b706c', 0, 0, 2, 32);
  if (endingTile(ending,x+1,y) === '#') p('#626865', 30, 0, 2, 32);
  if (endingTile(ending,x,y-1) === '#') p('#6b706c', 0, 0, 32, 2);
  if (endingTile(ending,x,y+1) === '#') p('#626865', 0, 30, 32, 2);
}

const towerConcreteCracks = {
  seam: {
    origin:[2,16],
    rows:['          ---', '      ---oooo----', '   ---ooosssooooo--', '--ooosssssooo--', 'oooooo---', '---'],
    grasses:[[8,20,4],[15,18,6]],
  },
  corner: {
    origin:[2,13],
    rows:['------','osssso---','ossssssoo--','oosssssssso---',' oosssssssoooo---',
      '  oosssssssoorrll--','   ooossssoorrll','     oooooorrll','       oorrll','        rrll'],
    grasses:[[6,17,8],[12,19,6],[15,17,4]],
  },
  split: {
    origin:[3,11],
    rows:['                 --','               --oo','              -ossr','            --ossr',
      '          --osssr','       ---osssrr','     --oosssrr','    -osssrr','  --osorr','--oorr','---'],
    grasses:[[12,17,7],[17,15,4]],
  },
};

function drawTowerFloorCrack(p, {kind, flip}) {
  const {origin:[ox,oy], rows, grasses} = towerConcreteCracks[kind];
  const colors = {'-':'#323534',o:'#4b4439',s:'#665e48',r:'#565654',l:'#757673'};
  const dot = (color,x,y,w,h) => p(color,flip ? 32-x-w : x,y,w,h);
  const fissure = kind === 'corner' ? [[16,20,3],[19,21,3],[21,22,3],[24,23,3],[22,20,1],[23,18,1]]
    : kind === 'seam' ? [[19,17,3],[21,15,4],[24,14,2],[25,13,3]]
    : [[20,11,3],[22,10,2],[23,9,3],[24,11,2],[26,12,3]];
  for (const [x,y,w] of fissure) dot('#303334',x,y,w,1);
  rows.forEach((row,dy) => {
    [...row].forEach((tone,dx) => {
      if (tone !== ' ') dot(colors[tone],ox+dx,oy+dy,1,1);
    });
  });
  if (kind === 'corner') {
    dot('#343737',19,24,4,2);
    dot('#767874',19,23,3,2);
    dot('#646562',24,26,2,1);
  }
  for (const [x,y,h] of grasses) {
    dot('#424c3c',x-2,y-1,6,2);
    for (const [lean,height,color] of [[-3,h-2,'#677551'],[1,h,'#849069'],[4,h-3,'#73835d']]) {
      for (let i=0;i<height;i++) {
        const dx=Math.round(lean*i/(height-1 || 1));
        dot(color,x+dx,y-i,i<height/2 ? 2 : 1,1);
      }
    }
  }
}

// Equipment is drafted on a two-pixel grid so silhouettes stay legible in the tall vault overview.
function drawTowerScenery(paint, {kind, width, wallEnd}) {
  const p = (color,x,y,w,h) => paint(color,2*x,2*y,2*w,2*h);
  const line = (color,x,y,endX,endY,weight=1) => {
    const steps = Math.max(Math.abs(endX-x), Math.abs(endY-y));
    for (let i=0; i<=steps; i++) {
      p(color, Math.round(x+(endX-x)*i/steps), Math.round(y+(endY-y)*i/steps), weight, weight);
    }
  };
  const dark='#2e3537', iron='#586365', edge='#8a9690', glint='#a8b1a2';
  const amber='#bc9966', ochre='#8a6d4e', teal='#729e98';
  const rust='#805e50', bare='#9e9481', stain='#495353';
  switch (kind) {
    case 'feeder-trench':
      drawFeederTrench(paint,width*32,wallEnd);
      break;
    case 'inspection-hatch': {
      drawFeederTrench(paint,width*32);
      // Raised hinged cover behind the open junction box; a tester rests on the right.
      p(dark,1,12,32,17); p('#6d756d',2,13,30,13);
      p('#262e30',4,14,26,10); p('#414948',4,23,26,2);
      p(dark,3,1,27,12); p('#778177',4,1,25,10);
      p('#515c56',6,3,21,6); p('#91998a',6,2,20,1);
      p('#9e875d',7,4,6,3); p('#4b4c42',8,5,3,1);
      for (const x of [19,22,25]) p('#67736a',x,4,1,4);
      for (const x of [7,22]) { p(iron,x,10,4,4); p(edge,x,11,4,1); }
      for (const [x,c] of [[7,amber],[14,teal],[21,'#a77b66']]) {
        p(iron,x-1,15,5,4); p(glint,x,15,3,1);
        line(c,x+1,18,x+1,21); line(c,x+1,21,x+4,24);
      }
      p('#373a35',33,17,12,10); p(ochre,34,16,10,8);
      p(dark,35,17,8,4); p('#8fafa0',36,18,5,2);
      p('#ccb180',36,22,2,1); p('#a39063',41,22,1,1);
      line('#252d2c',37,24,36,29); line('#252d2c',36,29,30,30);
      line('#252d2c',30,30,22,24);
      p(rust,3,26,5,1); p(bare,29,16,1,4);
      break;
    }
    case 'bench': {
      // Tool outlines on a pegboard; the vise grips the front corner of the worktop.
      p(dark,2,2,44,19); p('#615e50',3,3,42,14);
      for (let x=5;x<43;x+=4) for (const y of [5,9,13]) p('#4e5048',x,y,1,1);
      for (const [x,y] of [[8,6],[16,5],[23,7]]) {
        p(edge,x,y,1,6); p(edge,x-1,y-1,1,2); p(edge,x+1,y-1,1,2); p(glint,x,y+5,1,1);
      }
      p(ochre,30,5,2,9); p(edge,27,5,8,2);
      p(dark,3,18,42,12); p('#93795a',2,17,44,6); p('#b4976d',3,17,42,1);
      p(iron,5,24,2,6); p(iron,40,24,2,6); p('#635a49',10,24,20,4);
      p(dark,33,20,7,4); p(teal,32,18,3,4); p(teal,37,17,2,4); p(edge,39,21,4,1);
      p('#795f48',5,17,7,2); p('#b29975',8,19,6,1);
      p('#705e4d',22,20,6,1); p(rust,40,26,2,4); p(bare,32,19,2,1);
      break;
    }
    case 'reel':
      p(dark,2,12,28,3); p(ochre,4,4,16,8);
      for (const x of [3,17]) { p(iron,x,3,4,10); p(edge,x,2,3,2); }
      for (const x of [8,11,14]) p('#554e44',x,4,1,8);
      p('#444641',20,9,5,2); p('#444641',24,10,2,3); p(ochre,25,12,5,1);
      p(rust,3,8,3,4); p(bare,18,4,2,2); p('#9a805f',10,5,3,2);
      break;
    case 'tool-cart':
      p(iron,2,3,3,1); p(iron,2,4,1,4);
      p(dark,3,6,11,7); p('#87645a',4,6,9,6); p(bare,4,5,9,1);
      for (const y of [7,10]) p('#b4a286',6,y,4,1);
      p(rust,11,10,2,2); p(dark,4,13,2,2); p(dark,11,13,2,2);
      break;
    case 'transformer':
      p(dark,1,23,46,8); p('#666957',2,21,44,6); p(amber,3,21,41,1);
      p(iron,4,12,40,10); p(edge,4,12,39,2);
      for (const x of [7,20,33]) {
        p(ochre,x+2,3,3,11); p(glint,x+2,2,3,2);
        for (const y of [5,8,11]) { p('#574e46',x,y,8,2); p('#bc9369',x,y,7,1); }
      }
      for (let x=7;x<=39;x+=4) p(dark,x,16,2,6);
      for (const x of [6,36]) { p(dark,x,25,5,4); p(edge,x+1,25,3,1); }
      p(rust,7,13,5,2); p(rust,8,15,2,7); p('#6e5b4c',10,20,2,4);
      p(stain,34,12,6,2); p('#aa9071',21,8,3,1); p(rust,35,26,7,2);
      break;
    case 'breakers':
      p(dark,1,4,14,26); p('#767767',2,4,12,24); p(edge,3,4,10,1);
      p(dark,4,7,8,5); p('#a5a18a',5,8,6,3); p(dark,8,8,1,2);
      for (const x of [4,9]) {
        p('#343e3c',x,15,3,8); p(ochre,x+1,17,1,4);
        p(amber,x, x===4 ? 16 : 19,3,2);
      }
      p(rust,2,24,3,4); p(bare,4,25,2,1); p(stain,8,25,5,1);
      break;
    case 'scope':
      p(dark,2,4,44,24); p(iron,3,3,42,21); p(edge,4,3,40,1);
      p(dark,5,6,25,14); p('#354f52',6,7,23,11);
      for (const x of [10,15,20,25]) p('#405f60',x,7,1,11);
      p('#405f60',6,12,22,1);
      const wave=[[7,14],[10,14],[12,11],[14,15],[17,8],[19,16],[22,12],[24,13],[26,10],[28,10]];
      for (let i=1;i<wave.length;i++) line('#91b6a1',...wave[i-1],...wave[i]);
      for (const y of [7,14]) for (const x of [32,39]) {
        p(dark,x,y,4,5); p(edge,x,y,3,3); p(amber,x+1,y,1,2);
      }
      p('#677877',1,22,46,5); p(edge,2,22,44,1); p(dark,5,27,3,4); p(dark,39,27,3,4);
      p(stain,7,22,8,1); p(bare,9,23,5,1); p(stain,39,14,3,3); p(dark,40,15,1,1);
      break;
    case 'relay-racks':
      for (const x of [1,17,33]) {
        p(dark,x,1,14,14); p(iron,x+1,2,12,11);
        for (const y of [3,7,11]) { p(dark,x+2,y,10,2); p(x===33 ? stain : teal,x+3,y,2,1); p(edge,x+7,y,4,1); }
      }
      p(rust,2,11,2,3); p(bare,18,2,3,1);
      break;
    case 'dish': {
      p(dark,15,42,48,5); p(iron,16,41,46,4); p(edge,17,41,43,1);
      line(iron,20,42,37,28,3); line(iron,58,42,39,28,3);
      line(edge,21,41,38,28); line(edge,41,30,58,41); line(iron,29,36,50,36,2);
      // A tilted rim and offset bowl give the dish depth; all struts meet at its feed horn.
      const end=[72,12], start=[5,22];
      for (let x=start[0];x<=end[0];x++) {
        const t=(x-start[0])/(end[0]-start[0]), arc=Math.sqrt(Math.max(0,1-(2*t-1)**2));
        const axis=start[1]+(end[1]-start[1])*t;
        const top=Math.round(axis-8*arc), near=Math.round(axis+8*arc), back=Math.round(axis+15*arc);
        p('#37464a',x,top,1,back-top+2);
        p('#606e72',x,top,1,near-top+1); p('#929e9e',x,top,1,1);
        p('#556065',x,near,1,Math.max(1,back-near)); p('#b0b8ad',x,near,1,1);
        if ((x>=13 && x<=21) || (x>=55 && x<=59)) {
          const depth = x>=15 && x<=18 ? 3 : 1;
          p(rust,x,near,1,depth);
        }
      }
      line('#536165',22,17,29,23); line('#536165',29,23,44,22);
      p('#76807c',22,16,4,1); p('#717977',54,16,4,2);
      for (const [x,y] of [[6,22],[35,25],[71,12]]) line('#829190',x,y,43,5);
      p(dark,41,2,6,4); p('#aa8275',41,1,5,3); p('#c3a390',42,1,3,1);
      p('#424b4e',35,30,8,5); p(edge,36,31,5,1); p(rust,18,41,8,2);
      break;
    }
    case 'feeder':
      p(dark,2,21,28,8); p(iron,3,18,26,8); p(edge,4,18,24,2);
      for (const [x,h] of [[6,10],[14,16],[22,12]]) {
        p(dark,x,18-h,3,h); p(edge,x,18-h,1,h);
        p('#b08488',x-1,16-h,5,2); p('#97747c',x-2,13,7,2);
      }
      p(stain,21,19,5,2); p(rust,4,24,4,3); p(bare,5,18,4,1);
      break;
  }
}
