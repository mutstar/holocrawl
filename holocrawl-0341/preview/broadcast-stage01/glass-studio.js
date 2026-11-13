const glassStudioSize = {width: 8, height: 6};

function placeGlassStudio(map, avoid) {
  const {w, h, cells, seed} = map;
  const {width, height} = glassStudioSize;
  const isFloor = (x, y) => cells[y * w + x] === StreetGen.FLOOR;
  const random = StreetGen.random(seed + ':glass-studio');
  const candidates = [];
  const anchors = [map.start, map.upstairs, map.exit];
  for (let y = 2; y < h - height - 1; y++) for (let x = 2; x < w - width - 1; x++) {
    if (anchors.some(p => p.x >= x - 1 && p.x <= x + width && p.y >= y - 1 && p.y <= y + height)) continue;
    if (avoid.some(stage => x < stage.x + stage.width + 1 && x + width > stage.x - 1
        && y < stage.y + 5 && y + height > stage.y - 2)) continue;
    let clear = true;
    for (let dy = -1; dy <= height && clear; dy++) for (let dx = -1; dx <= width; dx++) {
      if (!isFloor(x + dx, y + dy)) { clear = false; break; }
    }
    if (clear) candidates.push({x, y, rank: random()});
  }
  candidates.sort((a, b) => a.rank - b.rank);
  const site = candidates[0];
  if (!site) return null;
  const door = {x: site.x + width - 1, y: site.y + Math.floor(height / 2)};
  const glass = [];
  for (let dy = 0; dy < height; dy++) for (let dx = 0; dx < width; dx++) {
    const x = site.x + dx;
    const y = site.y + dy;
    if (dx > 0 && dx < width - 1 && dy > 0 && dy < height - 1) continue;
    if (x !== door.x || y !== door.y) glass.push({x, y});
  }
  return {x: site.x, y: site.y, door, glass};
}

function createGlassStudioArt(art, mixer, microphone) {
  const {width, height} = glassStudioSize;
  const panel = '#45545c';
  const mullion = '#647982';
  const highlight = '#a1bac2';
  return art.sprite(width * 32, height * 32, ctx => {
    const paint = (color, x, y, w, h) => {
      ctx.fillStyle = color;
      ctx.fillRect(x, y, w, h);
    };
    const left = 15;
    const right = width * 32 - 17;
    const top = 17;
    const bottom = height * 32 - 16;
    const doorCenter = Math.floor(height / 2) * 32 + 16;
    const doorTop = doorCenter - 12;
    const doorBottom = doorCenter + 12;
    const span = right - left;

    paint('#171e2380', left + 2, bottom + 3, span + 4, 4);
    paint('#39464d', left, top, span, bottom - top);
    for (let y = top + 16; y < bottom; y += 16) paint('#343f46', left + 4, y, span - 8, 1);
    paint('#505653', 53, 91, 145, 58);
    paint('#4a504f', 55, 93, 141, 54);
    paint('#686c5d', 54, 91, 143, 1);

    // Desk, monitor bank, and a rehearsal mic are visible through the front glass.
    paint('#22292f', 60, 38, 128, 36);
    paint('#697577', 61, 37, 126, 2);
    paint('#4a5457', 61, 39, 126, 30);
    ctx.drawImage(mixer.tile, 60, 38);
    for (const x of [74, 108, 142]) {
      paint('#161e25', x, 23, 27, 19);
      paint('#36535e', x + 2, 25, 23, 12);
      paint('#597e83', x + 3, 26, 20, 1);
      paint('#8fbda9', x + 5, 29, 4, 1);
      paint('#8fbda9', x + 9, 30, 4, 1);
      paint('#8fbda9', x + 13, 28, 5, 1);
      paint('#be8b58', x + 21, 38, 2, 1);
      paint('#252e34', x + 10, 42, 8, 3);
    }
    paint('#1e272e', 112, 80, 22, 18);
    paint('#585f65', 115, 83, 16, 9);
    paint('#363d46', 114, 93, 18, 5);
    ctx.drawImage(microphone.tile, 136, 113);

    const glassFront = bottom - 27;
    const paneColor = '#a2d5df1a';
    const reflection = '#d5edf184';
    const shadow = '#232f36';
    const sideDepth = 8;

    function sidePane(edge, inner, start, end) {
      paint(paneColor, Math.min(edge, inner), start, sideDepth, end - start);
      paint(panel, edge, start, 2, end - start);
      paint('#8ba6af', inner, start, 1, end - start);
      for (let y = start + 30; y < end - 7; y += 32) {
        paint(mullion, Math.min(edge, inner), y, sideDepth + 1, 1);
      }
    }
    sidePane(left, left + sideDepth, top + 4, bottom);
    sidePane(right, right - sideDepth, top + 4, doorTop);
    sidePane(right, right - sideDepth, doorBottom, bottom);
    paint(panel, left, top, span + 2, 4);
    paint('#81939b', left + 1, top, span, 1);
    paint(shadow, left + 2, top + 3, span - 2, 1);

    paint(paneColor, left + 2, glassFront + 2, span - 2, bottom - glassFront - 2);
    paint(panel, left, glassFront, span + 2, 2);
    paint(highlight, left + 1, glassFront, span, 1);
    paint(shadow, left, bottom - 2, span + 2, 5);
    paint('#7c9099', left + 1, bottom - 2, span, 1);
    for (let x = left; x <= right; x += 32) {
      paint(mullion, x, glassFront + 1, 2, bottom - glassFront - 2);
    }
    for (const x of [left + 10, left + 105, right - 25]) {
      for (let step = 0; step < 7; step++) paint(reflection, x + step * 2, glassFront + 13 - step, 2, 1);
      for (let step = 0; step < 3; step++) paint('#b3d4db55', x + 10 + step * 2, glassFront + 14 - step, 2, 1);
    }

    paint('#515c5d', right - 6, doorTop, 14, doorBottom - doorTop);
    paint(highlight, right - 5, doorTop, 8, 2);
    paint(highlight, right - 5, doorBottom - 2, 8, 2);
    paint('#8b7752', right + 6, doorTop + 2, 1, doorBottom - doorTop - 4);
    paint('#d5a963', right, doorTop - 1, 3, 1);
    paint('#d5a963', right, doorBottom, 3, 1);
  });
}
