function createCurtainEntrance(art) {
  const {frame, archTop} = DoorFit159;
  const tile = frame.canvasW;
  const inset = (tile - frame.w) / 2;
  const width = 2 * (tile - inset);
  const center = tile * 2;
  const threshold = tile + frame.h - 1;

  return art.sprite(tile * 4, tile * 2, ctx => {
    const paint = (color, x, y, width, height) => {
      ctx.fillStyle = color;
      ctx.fillRect(x, y, width, height);
    };

    for (let column = 0; column < width; column++) {
      const x = tile + inset + column;
      const top = tile + archTop(Math.round(column * (frame.w - 1) / (width - 1)));
      const opening = top + 3;
      const edge = Math.min(column, width - 1 - column);
      paint('#a68b74', x, top, 1, 1);
      paint('#665348', x, top + 1, 1, opening - top - 1);
      if (edge < 3) {
        paint(edge === 1 ? '#87705f' : '#4d3e38', x, opening, 1, threshold - opening);
      } else {
        paint('#211c25', x, opening, 1, threshold - opening);
        // The folds fall away from the lit gap between the two curtains.
        const fold = ['#492731', '#713945', '#844653', '#512a38'][edge % 4];
        const end = Math.min(threshold - 2, tile + 36 - edge);
        if (edge < 20) paint(fold, x, opening, 1, end - opening);
        if (edge >= 16 && edge <= 19) {
          paint('#a37555', x, tile + 16 + (edge % 2), 1, 2);
        }
      }
    }
    paint('#584844', tile + inset, threshold, width, 1);
    const steps = [
      [48, 8, '#604738'], [51, 11, '#826049'],
      [55, 14, '#a27855'], [59, 17, '#c09567'],
    ];
    for (const [y, halfWidth, color] of steps) {
      paint('#362a2a', center - halfWidth, y + 1, halfWidth * 2, 2);
      paint(color, center - halfWidth, y, halfWidth * 2, 1);
    }

    for (const x of [22, 105]) {
      paint('#28282a', x - 3, 42, 8, 13);
      paint('#6b5545', x - 2, 43, 6, 10);
      paint('#ab7852', x - 1, 44, 4, 6);
      paint('#e0af79', x, 45, 2, 4);
      paint('#a3876b', x - 1, 52, 4, 1);
    }

    paint('#222629', center - 14, 22, 28, 10);
    paint('#765b48', center - 13, 23, 26, 7);
    paint('#403137', center - 12, 24, 24, 5);
    paint('#9f7a62', center - 10, 26, 5, 1);
    paint('#9f7a62', center + 5, 26, 5, 1);
    paint('#d2ab7c', center - 3, 25, 1, 1);
    paint('#d2ab7c', center + 2, 25, 1, 1);
    paint('#d2ab7c', center - 2, 26, 4, 1);
    paint('#d2ab7c', center - 1, 27, 2, 1);
  });
}
