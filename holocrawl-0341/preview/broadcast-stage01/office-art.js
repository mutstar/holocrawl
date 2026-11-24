function drawOfficeFloor(p, x, y) {
  if (y >= 13) return;
  const random = StreetGen.random(`office-wear:${x},${y}`);
  const meeting = x < 8 && y <= 9;
  const carpet = !meeting && x >= 10 && x <= 17 && y >= 7 && y <= 10;
  if (carpet) {
    p('#556b6a', 0, 0, 32, 32);
    if (x === 10 || x === 17) p('#81918a', x === 10 ? 3 : 27, 0, 2, 32);
    if (y === 7 || y === 10) p('#81918a', 0, y === 7 ? 3 : 27, 32, 2);
    if (random() < .35) {
      const u = 5 + Math.floor(random()*16), v = 5 + Math.floor(random()*20);
      p('#60716b', u, v, 7, 2);
      p('#64766e', u+3, v-1, 6, 1);
    }
    if (y === 10 && x === 13) {
      p('#686f63', 11, 27, 14, 2);
      p('#4f615d', 16, 27, 6, 3);
    }
  } else if (meeting) {
    p('#717575a8', 0, 0, 32, 32);
    p('#565e5d', 0, 31, 32, 1);
    p('#565e5d', 31, 0, 1, 31);
    if (random() < .12) {
      const u = 6 + Math.floor(random()*17);
      p('#59605c', u, 29, 5, 2);
      p('#616661', u+4, 27, 3, 2);
    }
  } else {
    for (const v of [0, 16]) {
      p((y + x + v / 16) % 3 ? '#937c5ebf' : '#9b8262c7', 0, v, 32, 16);
      p('#645b4e', 0, v + 15, 32, 1);
      if ((x + y + v / 16) % 3 === 0) p('#6c6050', v === 0 ? 8 : 24, v, 1, 15);
      const byDisplay = (x === 14 || x === 15) && (y === 2 || y === 3);
      if (random() < (byDisplay ? .9 : .26)) {
        const u = 2 + Math.floor(random()*12), row = v + 4 + Math.floor(random()*7);
        const span = (byDisplay ? 10 : 4) + Math.floor(random()*7);
        p('#a49478a6', u, row, span, 2);
        p('#a8987b8c', u+3, row-1, span-3, 1);
        p('#776a58', u+2, row+1, Math.floor(span/2), 1);
      }
      if (random() < .1) {
        const u = 2 + Math.floor(random()*16);
        p('#665948', u, v+14, 6, 1);
        p('#736452', u+5, v+13, 4, 1);
      }
    }
  }
  // Flush metal joins at the two openings in the meeting-room partition.
  if (x === 7 && (y === 5 || y === 6)) {
    p('#716e62',29,0,3,32);
    p('#9a9582',30,1,1,30);
  }
  if (y === 10 && (x === 4 || x === 5)) {
    p('#716e62',0,0,32,3);
    p('#9a9582',1,1,30,1);
  }
  // Shards stay at the jambs, leaving the walkable centre visibly clear.
  if (x === 13 || x === 14) {
    if (y === 12 || y === 11) {
      const u = x === 13 ? 2 : 25;
      p('#769e9d', u, 19, 5, 2);
      p('#afd1c6', u + 2, 17, 3, 2);
      p('#87abaa', u + 1, 6, 2, 3);
      if (x === 13 && y === 12) {
        // The cyan tip of the decal is still attached to this fallen piece of glass.
        for (let row = 0; row < 9; row++) {
          const edge = 1 + Math.floor(row / 3);
          const span = 14 - row;
          p('#465b5c', edge + 1, 23 + row, span, 1);
          p('#90b7b1', edge, 22 + row, span, 1);
          p('#44afb2', edge + 1, 22 + row, span - 4, 1);
        }
      }
    }
  }
}

function drawOfficeScenery(p, {kind, width, depth, snappedDesk}) {
  const w = width * 32, h = depth * 32;
  const dark = '#343b3c', wood = '#9c785a', oak = '#b69973';
  if (kind.startsWith('window-')) {
    const left = kind === 'window-left';
    // Stepped fracture at the loose edge. Draw the decal only on surviving glass.
    for (let y = 2; y < 29; y++) {
      const bites = [3, 7, 14, 19, 13, 9, 12, 5, 3];
      const bite = bites[Math.min(8, Math.floor((y - 2) / 3))];
      const a = left ? 0 : bite, b = left ? w - bite : w;
      p(y < 16 ? '#52787d' : '#42646b', a, y, b-a, 1);
      p('#a5c3b9', left ? b-2 : a, y, 2, 1);
      for (const u of [18, 49, 82]) {
        const at = u - Math.floor(y / 2);
        if (at > a && at + 3 < b) p('#749396', at, y, 3, 1);
      }
      if (left && y >= 5 && y <= 25) {
        const length = Math.min(5 + Math.min(y - 5, 25 - y) * 4, b - 59);
        const split = 10 + Math.floor((24 - y) / 4) + (y >= 13 && y < 17 ? 3 : 0);
        p('#72d1c8', 59, y, Math.min(split, length), 1);
        p('#aadfd2', 59, y, Math.min(length, 2 + Math.floor((25-y)/5)), 1);
        if (length > split + 3) p('#43a9b0', 59 + split + 3, y, length - split - 3, 1);
      }
    }
    for (const u of left ? [0, 31] : [32, 60]) {
      p('#3a4a4b', u, 1, 4, 29);
      p('#91a09a', u, 2, 1, 26);
    }
    p(dark, left ? 0 : 4, 28, w-4, 4);
    p('#adb1a0', left ? 0 : 4, 28, w-4, 2);
    p('#8e9990', left ? 0 : 4, 0, w-4, 2);
  } else if (kind.startsWith('sofa-')) {
    const left = kind === 'sofa-left', back = left ? 1 : 23;
    p('#333c3b', 2, 3, 29, h-4);
    p('#49666b', 3, 2, 26, h-7);
    for (const v of [8, 32]) {
      p('#739092', 6, v, 20, 23);
      p('#859c9b', 7, v+1, 18, 2);
      p('#5e7c7e', left ? 7 : 22, v+3, 3, 18);
    }
    p('#516e73', back, 4, 7, h-10);
    p('#92a8a3', back+1, 4, 2, h-12);
    for (const v of [1,h-9]) {
      p('#496368', 2, v, 27, 7);
      p('#8aa09b', 3, v, 25, 2);
    }
  } else if (kind === 'tea-table' || kind === 'conference') {
    const big = kind === 'conference', inset = big ? 12 : 2;
    if (big) for (const v of [8, 37, 66]) {
      for (const u of [1, w-13]) {
        p(dark,u,v,12,20); p('#627478',u+1,v+2,10,14);
        p('#91a2a0',u+2,v+2,8,2);
      }
    }
    p('#383630', inset, 5, w-2*inset, h-8);
    p(wood, inset+1, 3, w-2*inset-2, h-10);
    p(oak, inset+2, 3, w-2*inset-4, 3);
    p('#c7c3a9', inset+5, big ? 17 : 10, big ? 10 : 7, big ? 14 : 8);
    p('#858d84', inset+6, big ? 20 : 12, 4, 1);
    p('#535a56', w-inset-10, big ? 58 : 17, 5, 5);
    p('#d5c6a3', w-inset-10, big ? 57 : 16, 4, 3);
  } else if (kind === 'workstations') {
    for (let row = 3; row < 38; row++) {
      const cut = snappedDesk ? Math.max(0, Math.floor((row - 17) / 3) * 3) : 0;
      p(row >= 34 ? dark : wood, 3, row, w - 8 - cut, 1);
      if (cut > 0 && row < 34) p('#c6a173', w - 7 - cut, row, 2, 1);
    }
    p(oak, 4, 3, w-10, 2);
    if (snappedDesk) {
      for (const [u,v,len] of [[107,30,5],[111,28,4],[114,26,4]]) p('#654f40',u,v,len,2);
      p('#66513e',113,42,10,3); p('#c29f72',116,41,7,2);
    }
    for (const u of [15,76]) {
      p('#535650',u+14,19,4,4); p(dark,u+8,22,16,2);
      if (!snappedDesk && u === 15) {
        // One edge of the screen rests on the desk after the stand has sheared.
        for (let col = 0; col < 30; col++) {
          const sag = Math.floor(col / 5);
          p('#313c40',u+col,4+sag,1,15);
          if (col >= 2 && col < 28) p('#415256',u+col,6+sag,1,10);
        }
      } else {
        p('#313c40',u,5,30,15); p('#577177',u+2,7,26,10);
        p('#69878a',u+3,8,16,1); p('#cdaf79',u+26,18,2,1);
        if (snappedDesk && u === 76) {
          for (const [dx,dy,len] of [[20,7,3],[18,9,3],[16,11,3],[13,13,4],[11,15,3],[19,12,3],[21,13,3]]) {
            p('#a0b4ad',u+dx,dy,len,1);
          }
        }
      }
      p('#4a4e4d',u+3,26,23,5); p('#858c80',u+4,27,20,1);
      p(dark,u+8,40,19,17); p('#647a7c',u+9,39,17,13);
      p('#97a6a0',u+10,39,15,2); p(dark,u+16,55,3,5);
      p(dark,u+10,59,15,2);
    }

  } else if (kind === 'yagoo-display') {
    drawOfficeMemorial(p);
  } else if (kind === 'whiteboard') {
    p(dark, 6, 3, w-12, 22); p('#c1c4ac', 8, 5, w-16, 16);
    for (const [u,v,n] of [[16,9,20],[18,13,13],[49,10,6],[57,14,11]]) p('#778a80',u,v,n,2);
    for (const u of [83,94,105]) p('#c49b7d',u,8,7,7);
    for (const u of [14,w-18]) p('#626a64',u,24,3,5);
  } else if (kind === 'fallen-chair') {
    p('#453e37', 3, 21, 25, 5); p('#333d40', 5, 12, 9, 11);
    p('#657d80', 4, 9, 10, 11); p('#8a9b96', 4, 9, 8, 2);
    p('#53676b', 12, 15, 9, 5); p('#a3a596', 20, 14, 3, 8);
    p(dark, 22, 11, 5, 4); p(dark, 22, 21, 6, 3);
  } else if (kind === 'files') {
    p(dark, 3, 2, 25, h-5);
    for (const v of [4,31]) {
      p('#737c75', 5,v,21,25); p('#a0a294',6,v,19,2);
      p('#3f4848',11,v+7,10,3); p('#c8bd9c',13,v+14,7,4);
    }
  } else if (kind === 'plant') {
    p(dark, 10, 22, 14, 8); p('#aa9476', 9, 20, 15, 7);
    p('#c9af86', 8, 19, 17, 3); p('#68654b',14,10,3,10);
    for (const [u,v] of [[4,9],[14,5],[18,12],[9,14],[9,4]]) {
      p('#43594c',u,v,9,7); p('#6e8667',u+1,v,7,3);
    }
  }
}

function drawOfficeMemorial(p) {
  // A low cabinet against the back wall, using the desks' wood and filing cabinet trim.
  p('#494942', 2, 7, 60, 22);
  p('#92775b', 2, 5, 59, 14);
  p('#ad9270', 3, 5, 57, 2);
  p('#715f4f', 3, 19, 57, 8);
  p('#4b4940', 31, 20, 1, 6);
  for (const x of [27, 34]) p('#aa9677', x, 21, 3, 1);
  p('#a38b6b', 8, 10, 8, 1);
  p('#796650', 50, 14, 6, 1);
  // A flaked right corner exposes the cabinet top below the slab.
  p('#655c4d', 21, 15, 22, 2);
  p('#646c63', 20, 13, 22, 3);
  p('#838a7b', 21, 11, 19, 3);
  p('#919586', 22, 11, 7, 1);
  p('#707668', 38, 13, 5, 1);
  p('#575e55', 36, 14, 3, 1);
  p('#575e55', 34, 15, 3, 1);

  // Hand-pixelled for this scale. The missing cheek cuts into the outer contour.
  const stone = {d:'#515953', m:'#788077', s:'#979c8c', l:'#abb09e'};
  const head = [
    '      mmmmm     ',
    '    mmsssmmdm   ',
    '   mssmmmssmmd  ',
    '  mssmmssmmdsmd ',
    '  msmssmmssldmd ',
    ' dmssmmsslllssd ',
    ' dmsmmslllllsmd ',
    ' dmsssllllsdsm  ',
    '  dssddllsddm   ',
    '  mslssllslm    ',
    '  mslllsmslm    ',
    '   slsssmslmd   ',
    '   ssmdsssdms   ',
    '    slmllmms    ',
    '     ssmmss     ',
    '      mssm      ',
  ];
  head.forEach((row,y) => {
    [...row].forEach((tone,x) => {
      if (tone !== ' ') p(stone[tone], 24+x, y-18, 1, 1);
    });
  });
  p(stone.m, 30,-2,5,3);
  p(stone.s, 27,0,11,2);
  p(stone.d, 27,2,11,1);
  p(stone.m, 28,3,9,8);
  for (const x of [29,33]) p(stone.s, x,3,1,7);
  p(stone.d, 34,6,3,1);
  p(stone.d, 32,7,3,1);
  p(stone.d, 31,8,2,2);
  p(stone.s, 26,11,13,2);
  p(stone.d, 25,13,15,1);
  p('#535751', 28,16,9,2);
  p('#9c8c6d', 29,16,6,1);
  p(stone.m, 44,13,3,2);
  p(stone.s, 44,13,2,1);
  p('#777b6e', 42,17,2,1);
}

function officeExitControl(source, map, {x,y}) {
  const ctx = source.getContext('2d'), px=x*32, py=y*32;
  const threshold = ctx.getImageData(px,py,32,32);
  function setOpen(open) {
    map.cells[y*map.w+x] = open ? StreetGen.FLOOR : StreetGen.BARRIER;
    ctx.putImageData(threshold,px,py);
    const p = (color,u,v,w,h) => { ctx.fillStyle=color; ctx.fillRect(px+u,py+v,w,h); };
    p('#414a49',0,1,32,3);
    for (const u of [0,29]) p('#879087',u,2,3,29);
    p('#544c40',3,4,open ? 5 : 26,27);
    if (!open) {
      p('#9c8467',5,5,22,24); p('#455b60',8,7,16,9);
      p('#788e8e',9,8,14,2); p('#d3bb86',21,21,5,2);
    } else p('#b09672',4,5,2,24);
  }
  setOpen(false);
  return setOpen;
}
