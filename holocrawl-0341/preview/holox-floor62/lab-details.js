(() => {
  const innerDoor = { x: 3, y: 2 };
  const markDoor = (rows, x, y) => {
    rows[y] = rows[y].slice(0, x) + '+' + rows[y].slice(x + 1);
  };
  const installPrevious = LabSecurityDoor.install;
  LabSecurityDoor.install = function (layout, vault) {
    const entrance = installPrevious.call(this, layout, vault);
    markDoor(vault.rows, innerDoor.x, innerDoor.y);
    markDoor(layout.map.rows, layout.origin.x + innerDoor.x, layout.origin.y + innerDoor.y);
    vault.connectors.push({ ...innerDoor, direction: 'internal', type: 'security_door' });
    vault.interiorFeatures.find(feature => feature.id === 'service-cabinet').name = '봉인실 금고';
    vault.stations.find(station => station.id === 'laplus').motif =
      '양쪽의 작은 보라색 뿔과 황동 사슬이 밝은 핵을 가둔 격납고.';
    vault.stations.find(station => station.id === 'iroha').motif =
      '연녹색 검사등 옆에 은빛 곡날과 금색 코등이가 보이는 일본도를 세워두었다.';
    return entrance;
  };

  const painter = context => (color, x, y, w, h = 1) => {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
  };
  const sprite = (draw, width = 32) => {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = 32;
    const g = canvas.getContext('2d');
    draw(painter(g), g);
    return canvas;
  };

  LabSecurityDoor.drawInterior = function (g, origin, opened, terrain) {
    const x = origin.x + innerDoor.x;
    const y = origin.y + innerDoor.y;
    const isOpen = opened.has(x + ',' + y);
    // The baked snapshot has a wall here. Replace it with adjoining lab floor.
    g.drawImage(terrain, (x + 1) * 32, y * 32, 32, 32, x * 32, y * 32, 32, 32);
    g.save();
    g.translate(x * 32, y * 32);
    const px = painter(g);

    // This doorway joins the wall to its north and glass partition to its south.
    px('#242330', 3, 0, 26, 3);
    px('#4c4458', 6, 2, 20, 1);
    px('#292632', 10, 3, 12, 3);
    px('#292632', 10, 28, 12, 4);
    px('#a179c1', 10, 4, 12, 1);
    px('#986fb8', 11, 29, 10, 1);
    if (isOpen) {
      px('#665b6b', 13, 7, 2, 20);
      px('#51495c', 17, 7, 2, 20);
      for (const yy of [7, 11, 15, 19, 23]) px('#282530', 15, yy, 2, 2);
    } else {
      px('#1d1b26', 8, 5, 16, 24);
      px('#434052', 9, 6, 14, 21);
      px('#73578b', 9, 6, 2, 20);
      px('#ae88ca', 10, 7, 1, 18);
      px('#373342', 20, 7, 3, 20);
      for (const yy of [10, 15, 22]) {
        px('#282531', 11, yy, 9);
        px('#595164', 11, yy + 1, 9);
      }
      px('#302637', 13, 16, 7, 5);
      px('#c398df', 14, 17, 3, 2);
      px('#ead0f0', 14, 17, 2);
      px('#8e6a46', 11, 25, 7);
    }
    g.restore();
  };

  let safe;
  LabMaterials.featureSprite = function (original, id) {
    if (id !== 'service-cabinet') return original;
    safe ??= sprite(px => {
      px('#242126', 3, 28, 26, 3);
      px('#28232b', 4, 5, 24, 24);
      px('#817261', 5, 5, 22, 23);
      px('#a7987d', 6, 5, 19, 2);
      px('#65584f', 24, 7, 3, 20);
      px('#3e3333', 7, 8, 16, 18);
      px('#a28c6e', 8, 9, 14, 16);
      px('#625247', 9, 11, 12, 13);
      px('#887459', 10, 12, 10, 11);
      px('#b5a07f', 9, 10, 12);
      for (const y of [10, 21]) {
        px('#d1b186', 22, y, 3, 2);
        px('#8e7356', 22, y + 1, 3);
      }
      // Recessed combination wheel and bolt handle.
      px('#483b37', 10, 14, 7, 7);
      px('#c0ac88', 12, 14, 3, 7);
      px('#c0ac88', 10, 16, 7, 3);
      px('#e3c898', 12, 16, 3, 2);
      px('#5e4e44', 13, 17, 1, 2);
      px('#ddbb84', 18, 15, 2, 5);
      px('#a88d68', 6, 27, 18);
      px('#604e45', 7, 28, 4, 2);
      px('#604e45', 21, 28, 4, 2);
    });
    return safe;
  };

  const previousMemberSprite = LabMaterials.memberSprite;
  const members = new Map();
  LabMaterials.memberSprite = function (original, id) {
    if (id !== 'laplus' && id !== 'iroha') return previousMemberSprite.call(this, original, id);
    if (members.has(id)) return members.get(id);
    const base = previousMemberSprite.call(this, original, id);
    const updated = id === 'laplus' ? sprite((px, g) => {
      g.drawImage(base, 0, 0);
      // Mirrored, stepped horns curve out from the two clamps.
      for (const mirror of [false, true]) {
        const row = (color, x, y, w) => px(color, mirror ? 64 - x - w : x, y, w);
        const silhouette = [[6,3,2],[6,4,3],[6,5,4],[7,6,4],[7,7,5],[8,8,5],[9,9,5],[9,10,5],[10,11,4]];
        for (const [x,y,w] of silhouette) row('#252031', x, y, w);
        const inlay = [[7,4,1],[7,5,2],[8,6,2],[8,7,3],[9,8,3],[10,9,3],[10,10,3]];
        for (const [x,y,w] of inlay) row('#9475ae', x, y, w);
        row('#dcc4ec', 7, 5, 1);
        row('#c3a5dc', 8, 6, 1);
        row('#b394cc', 8, 7, 2);
        row('#6e5386', 11, 9, 2);
        row('#69537f', 11, 10, 2);
      }
    }, 64) : sprite((px, g) => {
      // Keep the check-in reader, and give the blade its own clear silhouette.
      g.drawImage(base, 0, 0, 22, 32, 0, 0, 17, 32);
      px('#26242d', 15, 28, 13, 3);
      px('#554a45', 16, 27, 12, 2);
      px('#89745e', 17, 27, 9);
      const blade = [[29,3],[29,4],[28,5],[28,6],[27,7],[27,8],[27,9],
        [26,10],[26,11],[26,12],[25,13],[25,14],[25,15],[24,16],[24,17],[23,18],[23,19],[22,20]];
      for (const [x,y] of blade) px('#22232b', x - 3, y, 5);
      for (const [x,y] of blade.slice(1)) {
        px('#aabac4', x - 2, y, 2);
        px('#edf0db', x, y, 1);
      }
      px('#eef2e2', 29, 3, 1);
      px('#80949b', 25, 11, 1, 2);
      px('#24222b', 19, 19, 7, 3);
      px('#b79a5e', 20, 19, 6);
      px('#e6ce8e', 21, 19, 4);
      px('#a78155', 19, 20, 5);
      px('#302936', 19, 21, 4, 3);
      px('#302936', 18, 24, 4, 3);
      px('#a2b594', 20, 21, 2);
      px('#738b70', 20, 23, 2);
      px('#a2b594', 19, 25, 2);
      px('#d4b681', 18, 26, 3);
    });
    members.set(id, updated);
    return updated;
  };
})();
