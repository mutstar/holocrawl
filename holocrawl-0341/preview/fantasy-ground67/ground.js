(() => {
  window.vaultTheme = {
    name: '3기생 운동장',
    vaultFile: './vault.json',
    defaultReward: 'weapon',
    assets: { weapon: '../theater-vault36/assets/reward-weapon.png' },
    startMessage: '남쪽 입구로 들어가 트랙과 줄넘기 구역을 둘러보세요.',
    walkMessage: '도타바타 그라운드를 둘러보는 중입니다.',
    stairsMessage: '기존 시작 계단에서 운동장까지 탐험합니다.',
    showLabels: '구역 표시',
    hideLabels: '구역 숨기기',
    blockedMessage: tile => tile === 'G' ? '운동장 펜스가 길을 막고 있습니다.' : undefined,
    inventory: ({ weapon = 0, scroll = 0, potion = 0 }) =>
      `획득  +2 숏소드 ${weapon}개 / 스크롤 ${scroll}장 / 포션 ${potion}개`,
  };

  const tileSize = 32;
  const art = document.createElement('canvas');
  const context = art.getContext('2d');
  const rect = (color, x, y, w, h = 1) => {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
  };
  const shade = (x, y) => {
    const seed = Math.imul(x + 37, 0x27d4eb2d) ^ Math.imul(y + 79, 0x165667b1);
    const mixed = Math.imul(seed ^ (seed >>> 16), 0x45d9f3b);
    return (mixed ^ (mixed >>> 16)) >>> 0;
  };

  function surface() {
    const grass = ['#47543c', '#4a573f', '#49563d', '#4b583f'];
    const wornGrass = ['#515840', '#555b42', '#535940', '#535a42'];
    const clay = ['#978169', '#9d876e', '#9b836a', '#a08971'];
    for (let y = 0; y < art.height; y++) {
      for (let x = 0; x < art.width; x++) {
        // A rounded rectangular track, with two lanes marked in worn chalk.
        const outerX = Math.max(0, 92 - x, x - 195);
        const outerY = Math.max(0, 91 - y, y - 182);
        const distance = Math.hypot(outerX, outerY);
        const texture = shade(x >> 1, y >> 1);
        const practiceArea = Math.hypot((x - 144) * .65, (y - 136) * 1.4);
        const worn = practiceArea < 24 + (texture % 6);
        let color = (worn ? wornGrass : grass)[texture >>> 30];
        if (distance <= 47 && distance >= 22) {
          color = clay[texture >>> 30];
          if (distance >= 46 || distance < 23 || (distance >= 33 && distance < 34.2)) {
            color = texture % 13 === 0 ? '#ac967b' : '#c5b597';
          }
        }
        rect(color, x, y, 1);
      }
    }
    // Paved approach lines up with the opening in the south fence.
    for (let y = 226; y < art.height; y++) {
      const inset = y < 236 ? Math.floor((236 - y) / 3) : 0;
      for (let x = 194 + inset; x <= 221 - inset; x++) {
        rect(['#747366', '#7b7a6b', '#706f62'][shade(x, y) % 3], x, y, 1);
      }
    }
    for (const y of [241, 252, 263, 274, 285]) rect('#625f55', 194, y, 28);
    rect('#8b8a74', 194, 237, 1, 51);
    rect('#5c6052', 221, 237, 1, 51);
  }

  function fence(vault) {
    const rail = (x, y, w, h) => {
      rect('#303a37', x, y, w, h);
      rect('#778271', x, y, w, 1);
    };
    for (const [row, cells] of vault.rows.entries()) {
      for (let col = 0; col < cells.length; col++) {
        if (cells[col] !== 'G') continue;
        const x = col * tileSize;
        const y = row * tileSize;
        const horizontal = row === 0 || row === vault.height - 1;
        const vertical = col === 0 || col === vault.width - 1;
        const isCorner = horizontal && vertical;
        if (horizontal) {
          const offset = isCorner && col === 0 ? 13 : 0;
          const length = isCorner && col > 0 ? 17 : tileSize - offset;
          rect('#37432f', x + offset, y + 22, length, 5);
          rail(x + offset, y + 13, length, 3);
          rail(x + offset, y + 19, length, 3);
          for (const localX of [5, 11, 20, 26]) {
            if (localX >= offset && localX < offset + length) {
              rect('#596452', x + localX, y + 13, 1, 9);
            }
          }
        }
        if (vertical) {
          const offset = isCorner && row === 0 ? 13 : 0;
          const length = isCorner && row > 0 ? 9 : tileSize - offset;
          rect('#36402e', x + 12, y + offset, 8, length);
          rect('#444f45', x + 14, y + offset, 4, length);
          rect('#78806e', x + 14, y + offset, 1, length);
        }
        const postX = x + 13;
        rect('#2e3630', postX, y + 9, 5, 15);
        rect('#6b7668', postX + 1, y + 9, 3, 13);
        rect('#a0a08a', postX + 1, y + 9, 3);
      }
    }
    for (const x of [186, 224]) {
      rect('#34372f', x, 266, 6, 14);
      rect('#757f70', x + 1, 266, 4, 12);
      rect('#b9a47c', x + 1, 268, 4, 2);
    }
  }

  function ropeArch() {
    const center = 144;
    // Stair-step rows preserve the silhouette of the blue climbing arch.
    const edge = [
      [28, 10, 5], [24, 15, 5], [20, 20, 5], [17, 25, 5],
      [14, 30, 6], [12, 36, 7], [10, 43, 8], [9, 51, 7],
    ];
    for (const [inset, top, height] of edge) {
      const left = 100 + inset;
      const right = 188 - inset;
      const width = right - left;
      if (top < 25) {
        rect('#263351', left, 64 + top, width, height);
        rect('#53689b', left + 1, 64 + top, width - 2, 2);
      } else {
        for (const x of [left, right - 9]) {
          rect('#25324d', x, 64 + top, 9, height);
          rect('#4d6297', x + 1, 64 + top, 6, height);
          rect('#7083ae', x + 1, 64 + top, 2, height);
        }
      }
    }
    for (const x of [108, 171]) {
      rect('#353b33', x - 3, 119, 15, 6);
      rect('#68726a', x - 2, 119, 13, 2);
      rect('#2d3544', x, 116, 9, 5);
    }
    for (const [color, x, y] of [
      ['#ba766a', 115, 96], ['#9a9b62', 111, 108], ['#8daa89', 122, 88],
      ['#9a9b62', 162, 88], ['#ba766a', 169, 100], ['#8daa89', 174, 111],
    ]) rect(color, x, y, 3, 2);

    // The emblem on top echoes the original ground's flexed-arm sign.
    rect('#29364c', center - 11, 76, 22, 12);
    rect('#8495b2', center - 10, 77, 20, 10);
    rect('#9d7b50', center - 6, 82, 12, 2);
    rect('#e5c48b', center - 7, 79, 5, 4);
    rect('#e5c48b', center - 5, 82, 9, 3);
    rect('#e5c48b', center, 80, 5, 4);
    rect('#d0b078', center - 3, 85, 8);
    // The slack rope sits below the arch and can be crossed.
    for (let x = 116; x <= 172; x++) {
      const sag = 4 - Math.floor(Math.abs(x - center) / 7);
      rect('#333f3c', x, 129 + sag, 1, 2);
      rect('#a6b5bb', x, 128 + sag, 1);
    }
    rect('#82694b', 114, 128, 4, 2);
    rect('#82694b', 170, 128, 4, 2);
  }

  // Fill pixel rows so diagonal edges stay crisp at native tile size.
  function propPainter(x, y) {
    return {
      block: (color, left, top, width, height = 1) =>
        rect(color, x + left, y + top, width, height),
      shape(color, points) {
        for (let row = 0; row < tileSize; row++) {
          const scanY = row + 0.5;
          const edges = [];
          for (let i = 0; i < points.length; i++) {
            const [ax, ay] = points[i];
            const [bx, by] = points[(i + 1) % points.length];
            if ((ay > scanY) === (by > scanY)) continue;
            edges.push(ax + (bx - ax) * (scanY - ay) / (by - ay));
          }
          edges.sort((a, b) => a - b);
          for (let i = 0; i < edges.length; i += 2) {
            const left = Math.ceil(edges[i] - 0.5);
            const right = Math.ceil(edges[i + 1] - 0.5);
            if (right > left) rect(color, x + left, y + row, right - left);
          }
        }
      },
    };
  }

  function noel(x, y) {
    // A padded stand and wide feet hold the shield at striking height.
    rect('rgba(32,30,26,.43)', x + 3, y + 28, 26, 3);
    rect('#454846', x + 8, y + 16, 16, 8);
    rect('#745b50', x + 8, y + 17, 16, 4);
    rect('#363e3d', x + 13, y + 20, 6, 10);
    rect('#777e70', x + 14, y + 21, 2, 7);
    rect('#343c3b', x + 6, y + 28, 21, 3);
    rect('#8d9688', x + 7, y + 28, 18);
    const { block, shape } = propPainter(x, y - 3);
    shape('#303640', [[4,7],[16,3],[28,7],[27,18],[24,23],[16,29],[8,23],[5,18]]);
    shape('#9aaeb8', [[5,8],[16,4],[27,8],[26,17],[23,22],[16,27],[9,22],[6,17]]);
    shape('#4c6473', [[8,9],[16,6],[24,9],[23,17],[21,21],[16,25],[11,21],[9,17]]);
    shape('#678493', [[9,9],[16,7],[16,24],[12,21],[10,17]]);
    shape('#536d7c', [[16,7],[23,10],[22,17],[20,21],[16,24]]);
    shape('#e6e6d7', [[6,8],[16,4],[24,7],[23,8],[16,6],[7,10]]);
    shape('#c7d7d8', [[6,9],[8,10],[9,17],[12,22],[16,25],[16,27],[10,23],[7,18]]);
    block('#f4e4b4', 15, 9, 2, 3);
    block('#e6cc91', 12, 12, 8, 2);
    block('#e6cc91', 15, 14, 2, 7);
    block('#f3e3ba', 15, 12, 2, 2);
    block('#ad946c', 17, 14, 1, 5);
    for (const [left, top] of [[7,10],[24,10],[9,18],[22,18],[15,24]]) {
      block('#d7d4b6', left, top, 2);
    }
  }

  function marine(x, y) {
    const { block, shape } = propPainter(x, y);
    // The marker stands beside a checkered finish stripe across both lanes.
    for (let row = 0; row < 2; row++) {
      for (let col = 0; col < 12; col++) {
        rect((row + col) % 2 ? '#6e6b5d' : '#ded0b0', x - 6 + col * 2, y + 25 + row * 2, 2, 2);
      }
    }
    block('rgba(33,27,24,.48)', 2, 28, 16, 3);
    block('#46362f', 4, 3, 4, 27);
    block('#b0845d', 5, 5, 2, 23);
    block('#e5bd7c', 4, 2, 4, 3);
    block('#343a3a', 2, 27, 11, 3);
    block('#a1a39a', 3, 27, 8);
    block('#6e7773', 3, 28, 8);
    shape('#33282e', [[7,5],[15,4],[23,6],[30,5],[28,13],[30,22],[23,24],[15,21],[7,23]]);
    shape('#4e3038', [[8,6],[15,5],[23,7],[28,6],[27,13],[29,21],[23,23],[15,20],[8,22]]);
    shape('#272932', [[9,8],[15,7],[23,9],[27,8],[26,13],[28,19],[23,21],[15,18],[9,20]]);
    shape('#ad5252', [[9,6],[15,5],[23,7],[28,6],[27,8],[23,9],[15,7],[9,8]]);
    shape('#8a454c', [[8,20],[15,18],[23,21],[28,19],[29,21],[23,23],[15,20],[8,22]]);
    shape('#b5b19e', [[12,15],[24,19],[24,21],[11,17]]);
    shape('#c8c3ad', [[22,15],[24,16],[13,21],[11,20]]);
    shape('#ece5cc', [[15,9],[21,9],[23,11],[23,15],[21,16],[21,18],[15,18],[15,16],[13,15],[13,11]]);
    block('#272932', 15, 12, 2, 2);
    block('#272932', 19, 12, 2, 2);
    block('#4e4445', 18, 14, 1, 2);
    block('#756b62', 17, 17, 1);
    block('#756b62', 19, 17, 1);
  }

  function pekora(x, y) {
    const { block, shape } = propPainter(x, y);
    block('rgba(35,29,23,.38)', 5, 28, 23, 3);
    block('#44504e', 14, 23, 5, 7);
    block('#81928a', 15, 25, 2, 4);
    block('#363e3d', 8, 28, 17, 3);
    block('#8c988c', 9, 28, 14);

    // The official mascot's broad white face and two carrot ear clips.
    shape('#3a3c37', [[8,11],[7,6],[7,3],[9,1],[12,1],[14,3],[15,10],[17,10],[18,3],[20,1],[23,1],[25,3],[25,6],[24,11],[27,14],[29,19],[29,23],[26,26],[22,27],[10,27],[5,25],[3,22],[3,18],[5,14]]);
    shape('#e3e4d8', [[9,11],[8,6],[8,3],[10,2],[12,2],[13,4],[14,11],[18,11],[19,4],[21,2],[23,2],[24,4],[24,6],[23,11],[26,15],[28,19],[28,23],[25,25],[21,26],[10,26],[6,24],[4,22],[4,18],[6,15]]);
    shape('#f0ede0', [[8,14],[12,11],[20,11],[24,14],[27,18],[27,21],[24,23],[21,24],[10,24],[6,22],[5,19]]);
    shape('#b8c4bf', [[4,21],[7,24],[12,25],[21,25],[26,23],[28,21],[28,23],[25,25],[21,26],[10,26],[6,24]]);
    block('#f3f0e4', 9, 4, 2, 4);
    block('#f3f0e4', 21, 4, 2, 4);

    for (const left of [5, 23]) {
      block('#50734d', left, 9, 4, 3);
      block('#76945c', left + 1, 9, 2);
    }
    shape('#b0663f', [[7,9],[10,8],[15,9],[13,11],[9,13],[7,12]]);
    shape('#b0663f', [[17,9],[22,8],[25,9],[25,12],[23,13],[19,11]]);
    block('#e59c55', 8, 9, 5, 2);
    block('#e59c55', 19, 9, 5, 2);
    for (const left of [11, 20]) {
      block('#4c382f', left, 15, 1, 3);
      block('#bd7547', left, 18, 1);
    }
    block('#534139', 12, 20, 1);
    block('#534139', 13, 21, 2);
    block('#534139', 15, 22, 3);
    block('#534139', 18, 21, 2);
    block('#534139', 20, 20, 1);
  }

  function flare(x, y) {
    const { block, shape } = propPainter(x, y);
    // The orange flag marks the archery bay beside its bow and arrow rack.
    for (const offset of [-18, -12, -6]) {
      block('#bbb298', offset, 19, 4, 2);
    }
    block('rgba(35,29,23,.43)', 3, 28, 28, 3);
    block('#3c4443', 4, 27, 24, 3);
    block('#889486', 5, 27, 21);
    block('#58402f', 15, 3, 3, 26);
    block('#b9946e', 16, 5, 1, 22);
    block('#dcba80', 15, 2, 3, 2);
    shape('#65402e', [[18,5],[24,6],[30,5],[28,11],[30,17],[24,18],[18,16]]);
    shape('#d77c43', [[18,6],[24,7],[29,6],[27,11],[29,16],[24,17],[18,15]]);
    shape('#f1a25f', [[18,6],[24,7],[29,6],[28,8],[24,9],[18,8]]);
    shape('#a85a37', [[18,14],[24,16],[28,15],[29,16],[24,17],[18,15]]);
    shape('#f4cc8a', [[23,9],[25,12],[24,15],[22,14],[21,12]]);
    block('#867456', 14, 28, 7, 2);
    block('#4e3c32', 22, 22, 7, 6);
    block('#9a7450', 23, 23, 4, 4);
    block('#dac9a5', 23, 20, 1, 4);
    block('#dac9a5', 26, 19, 1, 5);
    block('#b86b51', 22, 19, 2);
    block('#c9875d', 26, 18, 2);
    // Set the pale string behind the wooden curve so the open silhouette reads.
    block('#c2c6ae', 12, 5, 1, 22);
    shape('#4d382d', [[12,3],[14,4],[11,9],[7,13],[6,16],[7,19],[11,23],[14,27],[12,29],[8,25],[4,21],[3,17],[4,12],[8,8]]);
    shape('#b98556', [[12,4],[12,6],[10,9],[6,13],[5,17],[6,20],[10,24],[12,27],[11,27],[9,25],[5,21],[4,17],[5,13],[8,9]]);
    block('#eed29b', 9, 8, 2);
    block('#edc68c', 5, 13, 2);
    block('#4f5451', 4, 15, 3, 4);
    block('#b8aca0', 4, 16, 2);
    block('#b8aca0', 4, 18, 2);
    block('#dab782', 9, 24, 2);
  }

  const memberArt = { noel, marine, pekora, flare };
  window.holoxSecurityDoor = {
    source: '../holox-floor55/',
    install(layout, vault) {
      const { x, y } = layout.origin;
      for (const [row, cells] of vault.rows.entries()) {
        const outside = layout.map.rows[y + row];
        layout.map.rows[y + row] = outside.slice(0, x) + cells + outside.slice(x + vault.width);
      }
      art.width = vault.width * tileSize;
      art.height = vault.height * tileSize;
      surface();
      fence(vault);
      ropeArch();
      for (const station of vault.stations) {
        memberArt[station.id]?.(station.x * tileSize, station.y * tileSize);
      }
      return null;
    },
  };
  window.LabMaterials = {
    draw(target, origin) {
      target.drawImage(art, origin.x * tileSize, origin.y * tileSize);
    },
  };
})();
