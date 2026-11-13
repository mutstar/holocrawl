const BacklaneWallStructures = [
  [
    {type: 'shutter', name: '노점 준비실 셔터', x: 2, width: 3},
    {type: 'lanterns', name: '초롱 보관칸', x: 8, width: 3},
    {type: 'carts', name: '수레 반입구', x: 14, width: 4},
  ],
  [
    {type: 'canopies', name: '천막 보관칸', x: 2, width: 3},
    {type: 'workbench', name: '수리 작업대', x: 8, width: 3},
    {type: 'loading', name: '화물 셔터', x: 14, width: 4},
  ],
];

function drawBacklaneWallStructure(ctx, {type, width}, x, y) {
  const span = width * 32 - 6;
  ctx.save();
  ctx.translate(x + 3, y + 3);
  const paint = (color, left, top, w, h) => {
    ctx.fillStyle = color;
    ctx.fillRect(left, top, w, h);
  };

  // The sill ends inside the wall cell. The concrete between bays stays visible.
  paint('#594a39', 0, 1, span, 27);
  paint('#8f795e', 1, 0, span - 2, 2);
  paint('#aa9474', 2, 0, span - 4, 1);
  paint('#2b241d', 4, 4, span - 8, 22);
  paint('#171613', 5, 5, span - 10, 4);
  paint('#74614b', 1, 3, 2, 24);
  paint('#3b3127', span - 3, 3, 2, 24);

  if (type === 'shutter' || type === 'loading') {
    const loading = type === 'loading';
    paint(loading ? '#514f43' : '#555047', 7, 7, span - 14, 18);
    for (let row = 8; row <= 24; row += 4) {
      paint('#292824', 7, row, span - 14, 1);
      paint(loading ? '#6d6858' : '#777065', 8, row + 1, span - 16, 1);
    }
    paint('#342e27', span / 2 - 5, 20, 10, 3);
    paint('#958773', span / 2 - 3, 20, 6, 1);
    if (loading) {
      for (const left of [5, span - 9]) {
        paint('#8d7046', left, 6, 4, 19);
        for (let row = 8; row < 24; row += 5) paint('#43392c', left, row, 4, 2);
      }
    } else {
      paint('#8f6f4e', 12, 5, 12, 6);
      paint('#c6ad7b', 13, 6, 10, 3);
      paint('#574638', 16, 7, 3, 1);
    }
  } else if (type === 'lanterns') {
    paint('#75604a', 8, 8, span - 16, 2);
    for (let i = 0; i < 4; i++) {
      const left = 12 + i * 18;
      paint('#b19a73', left + 4, 9, 1, 3);
      paint('#482d27', left + 1, 12, 8, 11);
      paint(i === 1 ? '#cda367' : '#9e5945', left, 14, 10, 7);
      paint(i === 1 ? '#efd299' : '#b87556', left + 2, 13, 5, 9);
      paint('#77553d', left + 3, 22, 4, 2);
    }
  } else if (type === 'carts') {
    for (const left of [15, 62]) {
      paint('#403126', left + 1, 14, 33, 8);
      paint('#836448', left + 2, 13, 32, 3);
      paint('#ad8657', left + 3, 13, 29, 1);
      paint('#6e513a', left + 4, 18, 24, 3);
      paint('#8b7456', left + 30, 11, 8, 2);
      for (const offset of [5, 23]) {
        paint('#1b1916', left + offset, 20, 6, 5);
        paint('#6a5a47', left + offset + 2, 21, 2, 2);
      }
    }
  } else if (type === 'canopies') {
    paint('#5f4e3e', 8, 12, span - 16, 2);
    paint('#6f5a43', 8, 21, span - 16, 2);
    const colors = ['#985d4a', '#a18451', '#64705d'];
    for (const [index, color] of colors.entries()) {
      const left = 11 + index * 24;
      paint(color, left, 7, 18, 5);
      paint(color, left + 3, 15, 18, 6);
      paint('#44362b', left + 4, 10, 12, 1);
      paint('#c5ac7d', left + 11, 7, 2, 5);
      paint('#b49c74', left + 14, 15, 2, 6);
    }
  } else if (type === 'workbench') {
    paint('#494036', 8, 9, span - 16, 9);
    paint('#947753', 7, 18, span - 14, 3);
    paint('#504032', 11, 22, 25, 3);
    paint('#504032', span - 36, 22, 25, 3);
    for (const left of [14, 28, 48, 67]) {
      paint('#9d9b88', left, 10, 2, 6);
      paint('#695442', left - 1, 14, 4, 3);
    }
    paint('#b09b75', 58, 16, 10, 2);
  }

  paint('#544333', 3, 25, span - 6, 2);
  paint('#91785c', 2, 27, span - 4, 1);
  ctx.restore();
}
