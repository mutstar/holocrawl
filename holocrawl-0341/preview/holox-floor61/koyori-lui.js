(() => {
  const installPrevious = LabSecurityDoor.install;
  const consolePosition = { x: 5, y: 1 };
  LabSecurityDoor.install = function (layout, vault) {
    const door = installPrevious.call(this, layout, vault);
    const lui = vault.stations.find(station => station.id === 'lui');
    const koyori = vault.stations.find(station => station.id === 'koyori');
    Object.assign(lui, {
      ...consolePosition, w: 1, h: 1, sprite: true, kind: 'floor-console',
      name: '붉은 매 관제 단말',
      motif: '버건디 몸체에 황동으로 테를 두른 관제 단말. 푸른 감시 화면 아래에 붉은 매 문장이 새겨져 있다.',
    });
    Object.assign(koyori, {
      name: '분홍 시약 연구대',
      motif: '흰 실험용 서랍과 싱크, 분홍 플라스크와 청록색 시험관이 벽 안쪽에 들어간 연구대.',
    });
    vault.fixtures = vault.fixtures.filter(fixture =>
      fixture.id !== 'lab-counter-back' && fixture.id !== 'lui-command-plaque');
    const setTile = (rows, x, y, tile) => {
      rows[y] = rows[y].slice(0, x) + tile + rows[y].slice(x + 1);
    };
    setTile(vault.rows, lui.x, lui.y, 'F');
    setTile(layout.map.rows, layout.origin.x + lui.x, layout.origin.y + lui.y, 'F');
    return door;
  };

  const pixelTile = () => {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 32;
    return canvas;
  };
  const painter = context => (color, x, y, w, h = 1) => {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
  };

  const previousInset = LabMaterials.insetWall;
  const themedBenches = new Map();
  LabMaterials.insetWall = function (image, mask, theme, half, sides) {
    if (theme !== 'koyori') return previousInset.call(this, image, mask, theme, half, sides);
    const key = `${mask}:${half}:${sides}`;
    if (themedBenches.has(key)) return themedBenches.get(key);
    const tile = pixelTile();
    const g = tile.getContext('2d');
    g.drawImage(previousInset.call(this, image, mask, theme, half, sides), 0, 0);
    const left = sides.includes('w') && !(mask & 8) ? 4 : 0;
    const right = sides.includes('e') && !(mask & 2) ? 28 : 32;
    g.beginPath();
    g.rect(left, 12, right - left, 17);
    g.clip();
    g.translate(-half * 32, 0);
    const px = painter(g);

    // White enamel cabinets and a pale worktop; keep the dark recessed frame.
    px('#c6bfcd', 6, 22, 52);
    px('#ded8e2', 26, 22, 29);
    for (const x of [8, 35]) {
      px('#aca4b3', x, 24, 20, 4);
      px('#d0c8d4', x, 24, 20, 2);
      px('#735067', x + 7, 25, 6);
      px('#cb7eaa', x + 8, 25, 4);
    }
    px('#f7e6ef', 18, 17, 4);
    px('#e2d5e5', 18, 18, 2, 2);

    // Dark glass outline, a narrow neck, and a bright pink liquid line.
    px('#302632', 40, 14, 15, 8);
    px('#6f4863', 40, 16, 7, 6);
    px('#e7a5c8', 42, 13, 3, 3);
    px('#f9d4e7', 42, 13, 4);
    px('#c56f9d', 41, 17, 5, 2);
    px('#e987be', 40, 19, 7, 2);
    px('#ffb9df', 41, 18, 4);
    px('#fcd5ea', 41, 19, 1);
    px('#78bac2', 49, 16, 3, 5);
    px('#c6e9e9', 49, 15, 3);
    px('#b78aa5', 48, 21, 6);
    // A small pink paw stamp on the center panel.
    px('#d28cb6', 29, 24, 1);
    px('#d28cb6', 31, 23, 1);
    px('#d28cb6', 33, 24, 1);
    px('#e8a7ce', 30, 25, 3, 2);

    themedBenches.set(key, tile);
    return tile;
  };

  const previousMemberSprite = LabMaterials.memberSprite;
  let commandConsole;
  LabMaterials.memberSprite = function (original, id) {
    if (id !== 'lui') return previousMemberSprite.call(this, original, id);
    if (commandConsole) return commandConsole;
    commandConsole = pixelTile();
    const px = painter(commandConsole.getContext('2d'));
    px('#262229', 4, 28, 25, 3);
    px('#28202a', 5, 9, 22, 19);
    px('#704454', 6, 13, 20, 14);
    px('#ab6b74', 6, 14, 2, 12);
    px('#52303e', 23, 14, 3, 12);
    px('#3c2a35', 10, 16, 12, 9);
    px('#b7845c', 6, 26, 20);
    px('#d4ab78', 7, 26, 7);
    px('#593748', 7, 27, 18);

    // Sloped monitor and a short row of keys.
    px('#2a222d', 9, 4, 14, 10);
    px('#c19871', 10, 5, 12);
    px('#936a54', 8, 7, 16, 5);
    px('#293e49', 10, 6, 12, 5);
    px('#48616b', 11, 7, 10, 3);
    px('#9bc5cb', 12, 8, 2);
    px('#79a3b2', 14, 9, 3);
    px('#bce0de', 17, 8, 2);
    px('#a07764', 7, 12, 18, 2);
    px('#dac09f', 11, 12, 2);
    px('#dad3ba', 15, 12, 2);
    px('#e2a16e', 21, 12, 2);

    // Swept wings and a pointed tail, engraved on the front face.
    px('#c96877', 9, 17, 2);
    px('#c96877', 21, 17, 2);
    px('#ed9e92', 10, 18, 4);
    px('#ed9e92', 18, 18, 4);
    px('#d97a7f', 11, 19, 10);
    px('#b84f63', 12, 20, 8);
    px('#e9938d', 15, 17, 2, 4);
    px('#f3b4a4', 16, 17, 2);
    px('#c65f70', 15, 21, 2, 3);
    return commandConsole;
  };
})();
