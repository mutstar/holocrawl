// Paint each half of a 64px bench inside its two neighboring wall tiles.
const benchTiles = new Map();
LabMaterials.insetWall = function (image, mask, theme, half, sides) {
  const key = `${mask}:${theme}:${half}:${sides}`;
  if (benchTiles.has(key)) return benchTiles.get(key);

  const tile = document.createElement('canvas');
  tile.width = tile.height = 32;
  const context = tile.getContext('2d');
  context.imageSmoothingEnabled = false;
  context.drawImage(this.sprite(image, mask, false, sides), 0, 0);

  const left = sides.includes('w') && !(mask & 8) ? 4 : 0;
  const right = sides.includes('e') && !(mask & 2) ? 28 : 32;
  context.save();
  context.beginPath();
  context.rect(left, 12, right - left, 17);
  context.clip();
  context.translate(-half * 32, 0);
  const rect = (color, x, y, w, h) => {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
  };

  // The recessed bay shares the wall's dark armor and violet-gray edges.
  rect('#211e2a', 2, 12, 60, 17);
  rect('#55495f', 4, 12, 56, 1);
  rect('#393541', 4, 13, 56, 10);
  rect('#2e2b37', 4, 13, 56, 2);
  rect('#252430', 4, 21, 56, 2);
  rect('#54505d', 5, 22, 54, 2);
  rect('#797280', 5, 22, 54, 1);
  rect('#312b39', 5, 24, 54, 4);
  rect('#494252', 8, 24, 20, 3);
  rect('#494252', 36, 24, 20, 3);
  rect('#211e2b', 5, 28, 54, 1);
  rect('#504357', 3, 14, 2, 13);
  rect('#504357', 59, 14, 2, 13);

  if (theme === 'koyori') {
    // Sink in the worktop and two sample vials at the back.
    rect('#92909b', 11, 20, 14, 3);
    rect('#343544', 13, 21, 10, 2);
    rect('#ada8ae', 18, 17, 2, 4);
    rect('#ada8ae', 18, 17, 4, 1);
    rect('#232431', 41, 20, 13, 2);
    rect('#a45e81', 43, 16, 3, 5);
    rect('#cf96b2', 43, 16, 3, 1);
    rect('#56828a', 49, 15, 3, 6);
    rect('#9ebdc0', 49, 15, 3, 1);
    rect('#925d78', 15, 25, 7, 1);
    rect('#925d78', 43, 25, 7, 1);
  } else {
    // Angled analysis monitor and a flush keyboard for Lui's station.
    rect('#1b1d27', 13, 14, 16, 7);
    rect('#476269', 15, 15, 12, 4);
    rect('#91abad', 17, 16, 5, 1);
    rect('#607f82', 17, 18, 8, 1);
    rect('#6c6372', 18, 20, 6, 1);
    rect('#938790', 35, 20, 13, 2);
    rect('#42394a', 37, 20, 9, 1);
    rect('#89505e', 15, 25, 7, 1);
    rect('#89505e', 43, 25, 7, 1);
  }

  context.restore();
  benchTiles.set(key, tile);
  return tile;
};
