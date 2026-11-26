function createStageDoorArt(sprite) {
  const {frame, archTop, openingTop} = DoorFit159;
  const inset = (frame.canvasW - frame.w) / 2;

  function door(palette, paintLeaves, open = false) {
    return sprite(frame.canvasW, frame.h, ctx => {
      const paint = (color, x, y, width, height) => {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, width, height);
      };
      for (let column = 0; column < frame.w; column++) {
        const x = inset + column;
        const top = archTop(column);
        const opening = openingTop(column);
        paint(palette.jamb, x, top, 1, frame.h - top);
        paint(palette.trim, x, top + 1, 1, opening - top - 1);
        let rimHeight = 1;
        if (palette.continuousRim) {
          const outer = column < frame.w/2 ? column-1 : column+1;
          rimHeight = outer<0 || outer>=frame.w ? frame.h-top : Math.max(1,archTop(outer)-top+1);
        }
        paint(palette.edge, x, top, 1, rimHeight);
      }
      for (const x of [inset + 1, inset + frame.w - 2]) {
        paint(palette.trim, x, 12, 1, 19);
        if (!palette.continuousRim) {
          for (const y of [15, 26]) paint(palette.edge, x + (x < frame.canvasW / 2 ? 1 : -1), y, 1, 1);
        }
      }

      ctx.save();
      ctx.beginPath();
      for (let column = 4; column < frame.w - 4; column++) {
        const y = openingTop(column);
        ctx.rect(inset + column, y, 1, frame.h - y);
      }
      ctx.clip();
      if (open) ctx.clearRect(0, 0, frame.canvasW, frame.h);
      else paint(palette.plate, 6, 0, 20, frame.h);
      paintLeaves(paint);
      if (!open) {
        paint(palette.seam, 15, 2, 2, 29);
        paint(palette.trim, 6, frame.h - 1, 20, 1);
      }
      ctx.restore();
    });
  }

  const equipment = door({edge: '#8e8678', trim: '#696357', jamb: '#4d4a43', plate: '#555149', seam: '#302c26'}, p => {
    for (const x of [7, 18]) {
      p('#3a3833', x, 8, 7, 20);
      p('#6a6458', x, 8, 7, 1);
      p('#5b574e', x + 1, 10, 5, 16);
      for (const y of [11, 14, 17]) {
        p('#3b3831', x + 1, y, 5, 1);
        p('#777063', x + 1, y + 1, 5, 1);
      }
      p('#7e7668', x + 1, 25, 1, 1);
      p('#7e7668', x + 5, 25, 1, 1);
    }
    p('#35322d', 11, 20, 4, 4);
    p('#9d8860', 12, 21, 3, 1);
    p('#35322d', 17, 20, 4, 4);
    p('#9d8860', 17, 21, 3, 1);
  });

  const dock = door({edge: '#aba99a', trim: '#77766a', jamb: '#494942', plate: '#57574f', seam: '#292d2b'}, p => {
    for (const y of [8, 13, 24, 28]) {
      p('#42453f', 6, y, 20, 1);
      p('#67675a', 6, y + 1, 20, 1);
    }
    p('#2e322e', 6, 16, 20, 7);
    for (const x of [6, 17]) {
      p('#a18a56', x, 17, 9, 5);
      for (const offset of [2, 7]) for (let row = 0; row < 5; row++) {
        const left = x + offset - row;
        p('#494739', Math.max(x, left), 17 + row, left < x ? 1 : 2, 1);
      }
      p('#beaa77', x + 4, 17, 3, 1);
      p('#aaa595', x + 2, 26, 1, 1);
      p('#aaa595', x + 6, 26, 1, 1);
    }
    p('#343630', 12, 22, 3, 3);
    p('#858476', 13, 22, 1, 2);
    p('#343630', 17, 22, 3, 3);
    p('#858476', 18, 22, 1, 2);
  });

  const enamel = {edge:'#a4b5a9', trim:'#889d90', jamb:'#536b66', plate:'#97aaa0', seam:'#4b6663', continuousRim:true};
  const ward = door(enamel, p => {
    for(const x of [7,18]) {
      p('#526c6b',x,8,7,10);p('#7c9698',x+1,9,5,7);p('#acc1b8',x+1,9,2,5);
      p('#66847e',x,23,7,4);p('#c3c5af',x,23,7,1);
    }
    p('#ddd9be',12,19,2,3);p('#ddd9be',18,19,2,3);
  });
  const wardOpen = door(enamel, p => {
    for(const x of [6,23]) {
      p(enamel.plate,x,7,3,25);p(enamel.seam,x+1,9,1,10);
      p('#c3c5af',x,23,3,2);
    }
  }, true);
  return {equipment, dock, ward, wardOpen};
}
