function drawStreetSetGround(paint, ending, x, y) {
  const road=ending.road;
  const inBacklot=(tx,ty)=>road.backlot?.some(lane=>
    tx>=lane.x && tx<lane.x+lane.width && ty>=lane.y && ty<lane.y+lane.depth);
  if (inBacklot(x,y)) {
    const offset=(y%2)*32, panel=Math.floor((x*32+offset)/64);
    paint((panel+y)%3===0?'#71604d':'#695a49',0,0,32,32);
    if (inBacklot(x,y-1)) paint('#51483d',0,0,32,1);
    if ((x*32+offset)%64===0 && inBacklot(x-1,y)) {
      paint('#50463c',0,1,1,31);
      paint('#918069',3,3,2,1);
      paint('#918069',3,28,2,1);
    }
    paint('#756550',4+(x*7+y)%11,10+(x+y)%5,10,1);
    // Contact shading follows masonry faces, never the open ends of the boards.
    if (endingTile(ending,x,y-1)==='#') {
      paint('#241f1838',0,0,32,3);
      paint('#241f1820',0,3,32,2);
    }
    if (endingTile(ending,x-1,y)==='#') paint('#241f1838',0,0,3,32);
    if (endingTile(ending,x+1,y)==='#') paint('#241f1828',30,0,2,32);
    return;
  }
  const col = x - road.x;
  const row = y - road.y;
  if (col < 0 || col >= road.width || row < -1 || row > road.depth) return;
  if (row === -1 || row === road.depth) {
    paint('#68645b', 0, 0, 32, 32);
    paint('#4d4b44', 0, 0, 1, 32);
    paint('#514e46', 0, 15, 32, 1);
    paint('#4d4b44', col % 2 ? 11 : 21, 16, 1, 16);
    const curb = row === -1 ? 27 : 0;
    paint('#847b69', 0, curb, 32, 5);
    paint('#9a8e77', 0, curb, 32, 1);
    paint('#4b4941', 0, curb + 4, 32, 1);
    if (row===-1 && inBacklot(x,y-1)) {
      paint('#625e55',0,curb,32,5);
      paint('#57564f',0,curb+4,32,1);
    }
    if (row === -1 && col >= 16 && col <= 20) {
      for (const dash of [3, 16]) paint('#aa8654', dash, 20, 8, 2);
    }
    return;
  }

  paint('#424648', 0, 0, 32, 32);
  for (let n = 0; n < 10; n++) {
    const dx = (col * 17 + row * 7 + n * 13) % 30;
    const dy = (col * 11 + row * 13 + n * 7) % 31;
    paint(n % 3 === 0 ? '#4d5050' : '#383d40', dx, dy, n % 2 + 1, 1);
  }
  if (row === 1 && col > 1 && col < 29 && col % 4 === 0) {
    paint('#9a8b65', 0, 15, 30, 2);
    paint('#55564b', 6 + col % 9, 15, 3, 1);
    paint('#55564b', 24, 16, 2, 1);
  }
  if (col === 32 || col === 33) {
    const start = col === 32 ? 9 : 0;
    const width = col === 32 ? 23 : 18;
    for (const line of [5, 19]) paint('#888478', start, line, width, 5);
  }
  if (col <= 1) {
    const exposed = row === 0 ? 11 : row === 1 ? 18 : 12;
    const tear = col === 0 ? exposed : row === 1 ? 8 : 0;
    if (!tear) return;
    const top = col === 0 ? 0 : 15;
    const height = col === 0 ? 32 : 10;
    paint('#4f4438', 0, top, tear, height);
    for (let y = top + 2; y < top + height - 1; y += 7) {
      paint('#775f46', 0, y, tear - 1, 4);
      paint('#947951', 0, y, tear - 1, 1);
    }
    paint('#302d2a', tear - 1, top, 2, height);
    paint('#62615a', tear + 1, top, 1, height);
    if (col === 0 && row === 1) {
      paint('#4f4438', tear, 15, 32 - tear, 10);
      paint('#86694c', tear, 17, 32 - tear, 2);
      paint('#86694c', tear, 23, 32 - tear, 1);
    }
  }
}

function drawStreetSetScenery(paint, {kind, width}) {
  const span = width * 32;
  if (kind === 'bakery' || kind === 'cafe') {
    drawStreetSetFacade(paint, kind, span);
  } else if (kind === 'stripped') {
    paint('#272222a8', 8, 21, span - 16, 35);
    drawStreetSetBraces(paint, span, [13, 55, 101, 135]);
    paint('#68513e', 7, 19, 62, 34);
    paint('#a58357', 8, 19, 57, 22);
    paint('#7e5e42', 9, 24, 56, 2);
    paint('#5c4f45', 8, 43, 58, 10);
    paint('#d2a273', 9, 42, 30, 2);
    paint('#5b6360', 69, 29, 77, 4);
    paint('#9b9b85', 72, 29, 71, 1);
    for (const x of [73, 108, 141]) {
      paint('#343936', x, 32, 4, 22);
      paint('#6f7162', x, 33, 2, 18);
    }
    paint('#695347', 94, 48, 25, 5);
    paint('#ba9564', 96, 48, 20, 1);
  } else if (kind === 'signs') {
    paint('#241f1c86', 7, 9, 113, 44);
    for (const x of [12, 91]) {
      paint('#40362d', x, 10, 11, 46);
      paint('#9c7c53', x, 9, 11, 4);
      paint('#7d664a', x + 2, 13, 2, 39);
    }
    paint('#3b3029', 9, 16, 109, 17);
    paint('#6d5e49', 10, 16, 107, 2);
    for (const [x, w, color] of [[16, 27, '#665749'], [46, 28, '#75534f'], [76, 32, '#526b62']]) {
      paint(color, x, 20, w, 9);
      paint('#a39a79', x + 4, 23, w - 9, 2);
    }
    paint('#302a25', 14, 39, 93, 12);
    paint('#827151', 16, 39, 87, 8);
    paint('#6e5744', 26, 39, 3, 11);
    paint('#6e5744', 92, 39, 3, 11);
  } else if (kind === 'lumber') {
    drawStreetSetLumber(paint);
  } else if (kind === 'lift') {
    drawStreetSetLift(paint);
  } else if (kind === 'cases') {
    drawStreetSetCases(paint);
  } else if (kind === 'broken-camera') {
    drawStreetSetBrokenCamera(paint);
  } else if (kind === 'fallen-light') {
    drawStreetSetFallenLight(paint);
  } else if (kind === 'cable-reel') {
    drawStreetSetCableReel(paint);
  }
}

function drawStreetSetBraces(paint, span, posts) {
  paint('#4d3c2e', 5, 14, span - 10, 11);
  paint('#72573c', 6, 14, span - 12, 3);
  for (const x of posts) {
    paint('#3c322a', x - 3, 6, 18, 5);
    paint('#7c6347', x, 7, 11, 2);
    paint('#684c36', x, 8, 5, 22);
    for (let step = 0; step < 9; step++) paint('#a17b50', x + step, 8 + step, 3, 2);
    paint('#8f714c', x + 1, 10, 2, 11);
  }
}

function drawStreetSetFacade(paint, kind, span) {
  const bakery = kind === 'bakery';
  const panel = bakery ? '#526960' : '#704e4c';
  const cloth = bakery ? '#587365' : '#945f55';
  const pale = bakery ? '#97987a' : '#ba9e7d';
  const timber = bakery ? '#576357' : '#5f453e';
  const mid = span / 2;
  paint('#211f208a', 7, 40, span - 14, 22);
  drawStreetSetBraces(paint, span, [19, mid - 24, mid + 25, span - 32]);
  paint('#382c25', 3, 20, span - 6, 37);
  paint(panel, 5, 21, span - 10, 33);
  paint('#8a775b', 6, 20, span - 12, 2);
  for (const x of [8, mid - 39, mid + 38, span - 12]) {
    paint(timber, x, 33, 4, 23);
  }
  const windows = bakery ? [[18, 63], [span - 83, 63]] : [[14, 48], [span - 63, 48]];
  for (const [left, width] of windows) {
    paint('#221f20', left, 35, width, 17);
    paint(bakery ? '#475c58' : '#566361', left + 2, 35, width - 4, 12);
    paint('#86908a', left + 3, 36, width - 7, 1);
    paint('#3e4a47', left + Math.floor(width / 2), 36, 2, 12);
    paint('#9c805d', left, 50, width, 2);
    if (bakery) {
      for (const x of [left + 8, left + 17, left + 38, left + 49]) {
        paint('#ba9460', x, 44, 7, 3);
        paint('#91714d', x - 1, 46, 9, 2);
      }
    } else {
      paint('#827259', left + 5, 46, width - 10, 2);
      for (const x of [left + 9, left + 26]) paint('#b3aa8f', x, 43, 5, 3);
    }
  }
  paint('#252624', mid - 15, 33, 30, 24);
  paint(timber, mid - 13, 35, 26, 20);
  paint('#414b49', mid - 8, 36, 16, 10);
  paint('#aaa682', mid + 6, 48, 2, 3);
  const awningInset = bakery ? 7 : 24;
  for (let x = awningInset; x < span - awningInset; x += 8) {
    const stripe = (x - awningInset) % 16 === 0;
    paint(stripe ? cloth : pale, x, 27, Math.min(8, span - awningInset - x), stripe ? 10 : 9);
  }
  paint('#322c2980', awningInset, 34, span - awningInset * 2, 3);
  for (const x of [22, span - 30]) paint('#51483c', x, 30, 5, 1);
  paint('#3d332b', mid - 18, 15, 36, 13);
  paint(pale, mid - 16, 16, 32, 10);
  paint('#685441', mid - 14, 17, 28, 8);
  if (bakery) {
    paint('#ba915c', mid - 8, 19, 16, 4);
    paint('#d0ab70', mid - 6, 18, 12, 2);
    for (const x of [mid - 4, mid, mid + 4]) paint('#876344', x, 19, 1, 2);
  } else {
    paint('#d0b18b', mid - 5, 18, 9, 5);
    paint('#d0b18b', mid + 4, 19, 3, 3);
    paint('#685441', mid + 5, 20, 1, 1);
    paint('#b6926a', mid - 7, 23, 15, 1);
  }
  paint('#81735c', 5, 55, span - 10, 2);
  paint('#524837', 6, 57, span - 12, 2);
}

function drawStreetSetLumber(paint) {
  paint('#231f1d87', 4, 15, 86, 40);
  for (const y of [19, 43]) paint('#493b31', 8, y, 80, 8);
  for (const [x, y, w, shade] of [[9, 13, 70, '#a08157'], [16, 20, 68, '#8f704c'], [8, 27, 77, '#a68a61'],
    [12, 34, 68, '#765b43'], [10, 41, 73, '#9a7f59']]) {
    paint(shade, x, y, w, 6);
    paint('#594634', x + 1, y + 5, w - 2, 1);
    paint('#b3986d', x + 9, y + 1, Math.round(w / 3), 1);
  }
  for (const x of [25, 65]) paint('#625e4d', x, 12, 3, 38);
}

function drawStreetSetLift(paint) {
  paint('#27282698', 7, 24, 51, 55);
  paint('#303937', 9, 31, 46, 40);
  for (const x of [11, 47]) {
    paint('#292927', x, 62, 7, 10);
    paint('#827056', x + 2, 67, 4, 2);
  }
  paint('#9b7c49', 14, 39, 35, 22);
  paint('#c09b5b', 14, 39, 35, 2);
  paint('#705d43', 18, 46, 28, 11);
  for (let step = 0; step < 14; step++) {
    paint('#a38045', 17 + step, 40 - step, 4, 3);
    paint('#746347', 32 + step, 26 + step, 4, 3);
  }
  paint('#76796f', 13, 20, 40, 8);
  paint('#a1a290', 14, 20, 38, 2);
  paint('#3d4643', 16, 28, 34, 3);
  paint('#868d80', 16, 15, 2, 11);
  paint('#868d80', 48, 15, 2, 11);
  paint('#9f9b87', 16, 15, 34, 2);
}

function drawStreetSetCases(paint) {
  paint('#1e202291', 5, 12, 86, 42);
  for (const [x, y, width] of [[8, 12, 36], [48, 22, 39], [10, 36, 29]]) {
    paint('#292d30', x, y, width, 15);
    paint('#505c5d', x + 1, y + 1, width - 2, 10);
    paint('#90938a', x + 1, y + 1, width - 2, 1);
    paint('#888879', x + 3, y + 10, width - 6, 1);
    for (const corner of [x + 3, x + width - 5]) paint('#928a75', corner, y + 8, 2, 4);
    paint('#303a3c', x + Math.floor(width / 2) - 3, y + 4, 6, 3);
  }
}

function drawStreetSetBrokenCamera(paint) {
  paint('#242524a1', 7, 23, 49, 7);
  // The lens faces the player. Only the bent stand projects past the camera body.
  paint('#292c2c', 23, 22, 7, 8);
  for (let step = 0; step < 8; step++) {
    paint('#303434', 22 - step * 2, 24 + Math.floor(step / 2), 4, 3);
    paint('#858477', 22 - step * 2, 24 + Math.floor(step / 2), 3, 1);
  }
  paint('#626358', 32, 26, 9, 2);
  paint('#313534', 43, 28, 12, 3);
  paint('#8c8978', 44, 28, 10, 1);

  paint('#262727', 13, 11, 32, 15);
  paint('#686e65', 14, 11, 29, 12);
  paint('#9c9d87', 15, 11, 26, 2);
  paint('#494f48', 14, 22, 19, 3);
  paint('#353e3e', 17, 15, 9, 7);
  paint('#999a83', 17, 15, 8, 1);
  paint('#b38862', 22, 18, 2, 2);

  drawStreetSetFilmReel(paint, 12, 2);
  drawStreetSetFilmReel(paint, 26, 0);

  paint('#2a2e2f', 30, 12, 13, 16);
  paint('#2a2e2f', 28, 15, 17, 10);
  paint('#9ea79a', 31, 13, 11, 2);
  paint('#687d7e', 29, 16, 15, 8);
  paint('#61716f', 31, 24, 11, 2);
  paint('#243b44', 32, 16, 9, 8);
  paint('#476d77', 33, 16, 7, 6);
  paint('#a4c3bd', 33, 16, 4, 2);
  paint('#769d9c', 38, 20, 2, 2);
}

function drawStreetSetFilmReel(paint, x, y) {
  paint('#252929', x + 2, y, 10, 13);
  paint('#252929', x, y + 2, 14, 9);
  paint('#969585', x + 2, y + 1, 10, 11);
  paint('#aaa995', x + 3, y + 1, 7, 1);
  paint('#969585', x + 1, y + 3, 12, 7);
  for (const [dx, dy] of [[3, 3], [8, 3], [3, 8], [8, 8]]) {
    paint('#444944', x + dx, y + dy, 3, 2);
  }
  paint('#646b62', x + 6, y + 6, 2, 2);
}

function drawStreetSetFallenLight(paint) {
  paint('#22232396', 5, 19, 54, 9);
  paint('#373b38', 21, 17, 33, 4);
  paint('#858479', 22, 17, 31, 1);
  for (let step = 0; step < 9; step++) {
    paint('#3a3b37', 43 + step, 17 - step, 3, 2);
    paint('#797c71', 44 + step, 24 + Math.floor(step / 3), 3, 1);
  }
  paint('#242a2a', 7, 8, 22, 16);
  paint('#555e58', 8, 8, 18, 11);
  paint('#8b8b73', 10, 9, 13, 1);
  paint('#3b403a', 5, 10, 8, 12);
  paint('#79735d', 6, 11, 5, 9);
  paint('#ab9d79', 6, 11, 3, 3);
  paint('#aeb29b', 7, 16, 2, 3);
  paint('#343939', 17, 22, 3, 6);
  paint('#343939', 19, 26, 9, 2);
  paint('#9b7b5a', 28, 26, 3, 1);
  paint('#788f89', 6, 25, 2, 1);
}

function drawStreetSetCableReel(paint) {
  paint('#242321a0', 5, 20, 24, 8);
  paint('#343730', 6, 12, 17, 12);
  paint('#896f50', 7, 9, 14, 12);
  paint('#aa8c60', 9, 9, 9, 2);
  paint('#4a4236', 9, 12, 10, 7);
  paint('#343b3a', 10, 13, 8, 5);
  paint('#6e7469', 12, 14, 4, 2);
  paint('#373c39', 17, 18, 10, 3);
  paint('#373c39', 24, 20, 3, 5);
  paint('#8c7959', 24, 24, 4, 2);
}
