function drawLiveShowGround(paint, {stage, steps, frontAisle, audience, lobby, aisles, gateBanks, houseEntry, seatRows}, x, y) {
  const covers = area => x >= area.x && x < area.x + area.width && y >= area.y && y < area.y + area.depth;
  if (covers(stage)) {
    const stageFront = y === stage.y + stage.depth - 1;
    const col = x - stage.x;
    const left = stageFront && col === 0 ? 10 : 0;
    const right = stageFront && col === stage.width - 1 ? 22 : 32;
    paint(['#5d5459', '#60565b', '#5a5157'][(x * 7 + y) % 3], left, 0, right - left, 32);
    for (const seam of [7, 15, 23]) paint('#4b444d', left, seam, right - left, 1);
    paint('#6c6166', left + 4, 10, 9, 1);
    paint('#534b50', right - 12, 19, 6, 1);
    if (stageFront) {
      const hasSteps = x >= steps.x && x < steps.x + steps.width;
      paint('#302e38', left, 23, right - left, 9);
      paint('#676678', left, 24, right - left, 2);
      if (!hasSteps) paint(col % 3 === 1 ? '#859d98' : '#565a67', left + 3, 25, right - left - 6, 1);
      if (col % 2 === 0 && !hasSteps) paint('#242833', left + 5, 28, 8, 2);
    }
    return;
  }
  if (covers(steps)) {
    const last = y === steps.y + steps.depth - 1;
    const left = x === steps.x ? 3 : 0;
    const right = x === steps.x + steps.width - 1 ? 29 : 32;
    paint(last ? '#4c4651' : '#59515d', left, 0, right - left, last ? 23 : 32);
    for (const line of last ? [9, 19] : [8, 20, 30]) {
      paint('#34333e', left, line, right - left, 3);
      paint('#797383', left, line, right - left, 1);
    }
    return;
  }
  if (covers(frontAisle)) {
    paint('#414451', 0, 0, 32, 32);
    paint('#494b58', 0, 0, 1, 32);
    if (y === frontAisle.y + frontAisle.depth - 1) {
      paint('#575665', 0, 26, 32, 2);
      paint('#363642', 0, 29, 32, 3);
    }
    return;
  }
  if (covers(audience) || covers(houseEntry)) {
    const crossAisle = y === 15 || y === 16;
    const isAisle = covers(houseEntry) || crossAisle || aisles.some(aisle => x >= aisle.x && x < aisle.x + aisle.width);
    paint(isAisle ? '#373d4b' : '#49444f', 0, 0, 32, 32);
    if (seatRows.includes(y) && !isAisle) {
      paint('#5e5460', 0, 1, 32, 1);
      paint('#37333d', 0, 27, 32, 5);
      paint('#6c6066', 0, 27, 32, 1);
    }
    if (isAisle) {
      if (!crossAisle || y === 16) paint('#323642', 0, 28, 32, 2);
      if (covers(houseEntry) && y === houseEntry.y+houseEntry.depth-1) {
        const edge=x===houseEntry.x?2:26;
        paint('#515e61',edge,16,4,12);
        paint('#9aaea0',edge+1,17,2,7);
      }
      if (y % 2 === 0 && (x === 2 || x === 10 || x === 13 || x === 21)) {
        paint('#252d38', 6, 24, 19, 3);
        paint(y === 16 ? '#5f6665' : '#7d9995', 7, 24, 11, 1);
      }
    }
    return;
  }
  const bank = gateBanks.find(covers);
  if (bank) {
    paint('#42434e', 0, 8, 32, 18);
    paint('#777075', 0, 9, 32, 1);
    paint('#383944', 0, 25, 32, 1);
    paint('#7e7b67', 3, 25, 5, 1);
    paint('#7e7b67', 16, 25, 5, 1);
    if (x === bank.x) paint('#383944', 0, 8, 2, 18);
    if (x === bank.x + bank.width - 1) paint('#383944', 30, 8, 2, 18);
  }
  if (covers(lobby) && x > lobby.x && x < lobby.x + lobby.width - 1) {
    paint((x + y) % 3 ? '#544550' : '#584951', 0, 0, 32, 32);
    if (x === lobby.x + 1 || x === lobby.x + lobby.width - 2) {
      const edge = x === lobby.x + 1 ? 3 : 26;
      paint('#79626a', edge, 0, 2, 32);
      paint('#48434c', edge + 2, 0, 1, 32);
    }
    for (const [dx, dy] of [[5, 9], [20, 20], [9, 26]]) paint('#63505a', dx, dy, 3, 1);
  }
}

function drawLiveShowScenery(paint, {kind, width, y}) {
  if (kind === 'screen') {
    drawLiveShowScreens(paint, width * 32);
  } else if (kind === 'speakers') {
    for (const left of [7, 33]) {
      paint('#24242c', left, 4, 24, 24);
      paint('#737281', left + 1, 4, 21, 2);
      paint('#383740', left + 3, 7, 18, 17);
      for (const top of [8, 16]) {
        paint('#262832', left + 5, top, 14, 6);
        paint('#53505d', left + 7, top + 1, 10, 1);
      }
      paint('#726458', left + 19, 21, 2, 2);
    }
  } else if (kind === 'seats') {
    for (let col = 0; col < width; col++) drawLiveShowSeat(paint, col * 32, (col + y) % 3 === 0);
  } else if (kind === 'floor-light') {
    paint('#2929319c', 5, 20, 23, 7);
    paint('#31323b', 5, 15, 23, 9);
    paint('#606272', 7, 15, 18, 2);
    paint('#252833', 9, 9, 15, 12);
    paint('#767184', 10, 8, 11, 2);
    paint('#393c4d', 11, 10, 11, 8);
    paint('#768b89', 11, 10, 6, 2);
    paint('#565670', 16, 12, 5, 4);
  } else if (kind === 'turnstile') {
    drawLiveShowTurnstile(paint);
  } else if (kind === 'ticket-booth') {
    drawLiveShowTicketBooth(paint);
  } else if (kind === 'belt') {
    drawLiveShowBelt(paint, width * 32, y === 38);
  } else if (kind === 'bench') {
    paint('#292631a0', 5, 19, 54, 9);
    paint('#39333d', 7, 13, 50, 13);
    paint('#71636b', 8, 13, 48, 7);
    paint('#9c8888', 9, 13, 46, 1);
    paint('#4e444b', 8, 20, 48, 3);
    for (const left of [10, 52]) paint('#625c65', left, 23, 3, 4);
  }
}

function drawLiveShowScreens(paint, span) {
  paint('#25242b91', 8, 31, span - 16, 28);
  paint('#2e2c35', 4, 9, span - 8, 9);
  paint('#615e6c', 5, 9, span - 10, 1);
  paint('#484554', 5, 16, span - 10, 1);
  for (let x = 8; x < span - 11; x += 12) {
    paint('#53515c', x, 11, 2, 4);
    paint('#666374', x + 2, 14, 3, 1);
  }
  const main = span / 2 - 88;
  for (const [left, width, top] of [[12, 80, 24], [main, 176, 17], [span - 92, 80, 24]]) {
    paint('#222630', left, top, width, 52 - top);
    paint('#756d81', left, top, width, 2);
    paint('#3b3c4c', left + 3, top + 3, width - 6, 45 - top);
    for (let p = left + 11; p <= left + width - 9; p += 16) paint('#343643', p, top + 4, 1, 42 - top);
    paint('#515061', left + 8, top + 6, width - 23, 1);
    paint('#627072', left + width - 8, 48, 3, 1);
    for (const x of [left + 7, left + width - 10]) paint('#343741', x, 51, 5, 6);
  }
  for (const [x, lens] of [[45, '#7f7189'], [125, '#738b88'], [253, '#7f7189'], [329, '#738b88']]) {
    paint('#272934', x, 12, 11, 12);
    paint('#726e7a', x + 1, 13, 9, 3);
    paint(lens, x + 3, 20, 5, 2);
  }
  for (const x of [5, span - 11]) {
    paint('#2a2832', x, 16, 6, 33);
    paint('#67656e', x + 1, 18, 1, 25);
    paint('#899b95', x + 3, 19, 1, 7);
    paint('#7b728a', x + 3, 30, 1, 4);
  }
}

function drawLiveShowSeat(paint, x, faded) {
  paint('#252430ab', x + 2, 15, 28, 10);
  paint('#33282f', x + 3, 5, 26, 16);
  paint(faded ? '#775760' : '#855960', x + 5, 5, 22, 7);
  paint(faded ? '#93747b' : '#a4787b', x + 6, 5, 20, 1);
  paint('#5e424d', x + 7, 13, 18, 6);
  paint('#936974', x + 8, 14, 16, 1);
  for (const side of [3, 26]) {
    paint('#454049', x + side, 10, 3, 12);
    paint('#777078', x + side, 12, 2, 1);
  }
  paint('#36303b', x + 7, 21, 18, 2);
}

function drawLiveShowTurnstile(paint) {
  paint('#252733a8', 4, 19, 26, 8);
  paint('#363743', 6, 8, 15, 17);
  paint('#777880', 7, 8, 13, 5);
  paint('#a3a09b', 8, 8, 11, 1);
  paint('#515461', 8, 13, 11, 10);
  paint('#333942', 11, 10, 7, 3);
  paint('#a67b63', 12, 11, 5, 1);
  paint('#9b9e93', 19, 16, 11, 2);
  paint('#646963', 20, 18, 9, 1);
  paint('#868980', 21, 18, 2, 5);
  paint('#92928f', 19, 23, 3, 1);
}

function drawLiveShowTicketBooth(paint) {
  paint('#26252e9d', 3, 26, 58, 32);
  paint('#33323e', 5, 13, 54, 39);
  paint('#7b7280', 6, 14, 52, 2);
  paint('#51505d', 7, 17, 50, 28);
  paint('#303644', 11, 23, 40, 12);
  paint('#566c71', 12, 23, 38, 7);
  paint('#7c908c', 13, 24, 12, 1);
  paint('#3e4954', 31, 22, 2, 14);
  paint('#8a7d80', 8, 36, 48, 3);
  paint('#3e3844', 10, 39, 44, 9);
  paint('#b29e81', 41, 37, 8, 2);
  paint('#655b69', 13, 48, 36, 2);
}

function drawLiveShowBelt(paint, span, torn) {
  for (let x = 9; x < span - 4; x += 32) {
    paint('#302b36a0', x - 4, 19, 13, 6);
    paint('#403f49', x - 4, 18, 12, 5);
    paint('#8b8388', x - 3, 18, 10, 1);
    paint('#827b82', x, 8, 3, 12);
    paint('#b0a1a4', x - 1, 7, 5, 2);
    if (x + 32 >= span - 4) continue;
    if (torn && x >= span / 2 - 52 && x < span / 2 - 20) {
      paint('#8e585d', x + 3, 8, 5, 2);
      paint('#784951', x + 8, 10, 6, 2);
      paint('#6e474f', x + 14, 12, 8, 2);
      paint('#784951', x + 22, 10, 6, 2);
      paint('#8e585d', x + 28, 8, 4, 2);
    } else {
      paint('#724750', x + 3, 8, 29, 3);
      paint('#a96d70', x + 3, 8, 28, 1);
    }
  }
}
