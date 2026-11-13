function createStageEntrance(art) {
  return art.sprite(32, 32, ctx => {
    const paint = (color, x, y, width, height) => {
      ctx.fillStyle = color;
      ctx.fillRect(x, y, width, height);
    };

    paint('#272b2c', 2, 2, 28, 28);
    paint('#353f45', 3, 3, 26, 26);
    paint('#698089', 3, 3, 26, 1);
    paint('#51646c', 4, 4, 24, 2);
    paint('#12191d', 6, 6, 20, 21);
    paint('#0c1114', 7, 7, 18, 11);

    for (let step = 0; step < 5; step++) {
      const x = 10 - step;
      const y = 12 + step * 3;
      const width = 32 - 2 * x;
      paint(['#273238', '#34434a', '#3f5058', '#4a5c65', '#566971'][step], x, y, width, 2);
      paint('#19242a', x, y + 2, width, 1);
    }
    for (const x of [3, 26]) {
      paint('#29343a', x, 7, 3, 19);
      paint('#789097', x + 1, 7, 1, 15);
      paint('#40565e', x, 22, 3, 4);
      for (const y of [23, 26]) paint('#bd9954', x, y, 3, 1);
    }
    paint('#819198', 6, 27, 20, 1);
    paint('#476364', 12, 4, 8, 2);
    paint('#b3d1be', 14, 4, 4, 1);
  });
}
