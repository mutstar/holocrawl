// The lab entrance uses the same door state and vision rules as city doors.
const LabSecurityDoor = {
  source: '../holox-floor55/',

  install(layout, vault) {
    const { x, y } = vault.entranceDecor.opening;
    const worldX = layout.origin.x + x;
    const worldY = layout.origin.y + y;
    const markDoor = (row, column) => row.slice(0, column) + '+' + row.slice(column + 1);
    vault.rows[y] = markDoor(vault.rows[y], x);
    vault.legend['+'] = 'holox_security_door';
    layout.map.rows[worldY] = markDoor(layout.map.rows[worldY], worldX);
    vault.connectors[0].type = 'security_door';

    // Recess one round light into the existing exposed wall face on each side.
    LabMaterials.drawEntrance = (context, origin, room, images) => {
      context.imageSmoothingEnabled = false;
      for (const side of [-1, 1]) {
        const left = (origin.x + x + side) * 32;
        const top = (origin.y + y) * 32;
        context.drawImage(images.entrance, 8, 12, 14, 14, left + 10, top + 17, 11, 11);
      }
    };
    return { x: worldX, y: worldY };
  },

  draw(context, position, open) {
    context.save();
    context.translate(position.x * 32, position.y * 32);
    const rect = (color, x, y, width, height) => {
      context.fillStyle = color;
      context.fillRect(x, y, width, height);
    };

    // Dark jambs and a low sill frame the door. The center stays floor when open.
    rect('#171621', 0, 1, 4, 30);
    rect('#171621', 28, 1, 4, 30);
    rect('#76608e', 1, 3, 1, 25);
    rect('#76608e', 30, 3, 1, 25);
    rect('#332d42', 3, 29, 26, 2);
    rect('#62526e', 4, 29, 24, 1);

    if (!open) {
      rect('#181924', 4, 1, 24, 28);
      rect('#383746', 5, 3, 22, 24);
      rect('#242330', 15, 3, 2, 24);
      for (const y of [7, 12, 21, 26]) {
        rect('#20202c', 5, y, 22, 1);
        rect('#4a4655', 5, y + 1, 10, 1);
        rect('#4a4655', 17, y + 1, 10, 1);
      }
      rect('#24212d', 6, 24, 20, 2);
      for (const x of [7, 11, 19, 23]) rect('#987825', x, 24, 2, 1);

      // Pixel-stepped violet frame and a small X on the locking plate.
      for (const x of [5, 26]) rect('#8856ad', x, 6, 1, 17);
      rect('#a276c2', 6, 4, 20, 1);
      rect('#8856ad', 6, 5, 2, 1);
      rect('#8856ad', 24, 5, 2, 1);
      rect('#201b2a', 11, 13, 10, 8);
      for (let i = 0; i < 5; i++) {
        rect('#b990dc', 13 + i, 14 + i, 1, 1);
        rect('#b990dc', 17 - i, 14 + i, 1, 1);
      }
    } else {
      rect('#3d354a', 2, 4, 3, 23);
      rect('#3d354a', 27, 4, 3, 23);
      rect('#a879cc', 3, 6, 1, 18);
      rect('#a879cc', 28, 6, 1, 18);
    }
    context.restore();
  },
};
window.holoxSecurityDoor = LabSecurityDoor;
