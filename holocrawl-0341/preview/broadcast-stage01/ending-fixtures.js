function drawEndingFixture(paint, id, placement, accent, wide = false) {
  if (id === 'mirror') {
    if (placement === 'wall') return;
    paint('#24232b70', 8, 26, 46, 3);
    for (const x of [12, 48]) paint('#554b50', x, 22, 3, 6);
    paint('#735e66', 9, 19, 45, 5);
    paint('#ad9090', 9, 19, 45, 2);
    if (wide) drawSmallDressingMirror(paint, 11, 2, 32, 17);
    else drawSmallDressingMirror(paint, 20, 5, 16, 14);
    paint('#675262', 46, 16, 4, 4);
    paint('#b7a699', 47, 14, 2, 2);
    return;
  }
  const palette = {
    flood: ['#68828a', '#455f65'], street: ['#a58765', '#645547'],
    live: ['#8b8699', '#54505f'], office: ['#a19c85', '#656b64'],
    tower: ['#8e9eac', '#525f70'], garden: ['#8d9d73', '#526854'],
    archive: ['#a6977d', '#645a50'],
    rail: ['#9a8667', '#615344'], power: ['#ad995d', '#6e6250'],
  };
  const [metal, body] = palette[id];
  const shadow = '#252a2b';
  if (placement === 'wall') {
    paint('#161a1c90', 5, 9, 54, 17);
    paint(body, 6, 10, 52, 13);
    paint(`${metal}bf`, 7, 10, 50, 1);
    paint(shadow, 8, 12, 48, 9);
    drawEndingWallEquipment(paint, id, metal, body, accent);
    return;
  }

  for (const x of [3, 51]) {
    paint(`${accent}75`, x, 4, 10, 1);
    paint(`${accent}75`, x === 3 ? x : x + 9, 4, 1, 5);
  }
  paint('#171a1b8c', 4, 24, 56, 5);
  paint(shadow, 7, 17, 50, 9);
  paint(body, 8, 18, 48, 6);
  paint(metal, 8, 18, 48, 1);
  for (const x of [9, 50]) paint(shadow, x, 23, 4, 6);
  drawEndingFloorEquipment(paint, id, metal, body, accent);
}

function drawEndingWallEquipment(p, id, metal, body, accent) {
  if (id === 'flood') {
    p(metal, 10, 16, 44, 3);
    p('#8ba3a3', 11, 16, 42, 1);
    for (const x of [17, 41]) {
      p('#39474c', x, 12, 5, 9);
      p(accent, x - 2, 12, 9, 2);
      p('#23363b', x + 1, 14, 2, 4);
    }
  } else if (id === 'street') {
    p('#735849', 10, 12, 44, 8);
    for (const [x, width] of [[12,10],[24,11],[37,14]]) {
      p('#bf9470', x, 13, width, 4);
      for (let stroke = x + 2; stroke < x + width - 1; stroke += 3) p('#765d4e', stroke, 14, 1, 2);
    }
  } else if (id === 'live') {
    p(body, 10, 13, 44, 6);
    for (const x of [14, 24, 34, 44]) {
      p('#31313b', x, 13, 6, 5);
      p(metal, x + 1, 14, 4, 1);
    }
    p(accent, 50, 15, 2, 2);
  } else if (id === 'office') {
    p('#6d7978', 10, 12, 44, 8);
    for (const y of [13, 16, 19]) p('#a5afa4', 11, y, 42, 1);
    p(body, 31, 12, 2, 9);
  } else if (id === 'tower') {
    p('#344856', 10, 12, 44, 8);
    for (const [x, h] of [[13,3],[19,5],[25,2],[31,6],[37,4],[43,2]]) p('#86acb0', x, 19 - h, 2, h);
    p(accent, 50, 14, 3, 3);
  } else if (id === 'garden') {
    p('#365346', 10, 14, 44, 5);
    p('#76a59a', 12, 13, 40, 1);
    for (const x of [14, 24, 36, 47]) {
      p(metal, x, 15, 2, 4);
      p('#a0b7a5', x - 1, 19, 4, 1);
    }
  } else if (id === 'archive') {
    for (const x of [12, 23, 35, 46]) {
      p('#4e5552', x, 12, 7, 8);
      p(metal, x + 1, 12, 5, 1);
      p('#a9aaa0', x + 2, 15, 3, 3);
      p('#404643', x + 3, 16, 1, 1);
    }
  } else if (id === 'rail') {
    p('#a58e72', 12, 17, 39, 1);
    p('#a58e72', 28, 14, 23, 1);
    p('#a58e72', 27, 15, 2, 2);
    for (const x of [18, 47]) p('#a2ad7e', x, 14, 2, 3);
    p('#c18468', 51, 15, 2, 2);
  } else {
    for (const x of [12, 22, 32, 42]) {
      p(body, x, 12, 8, 8);
      p(metal, x + 2, 14, 4, 2);
      p('#222a2b', x + 3, 16, 2, 3);
    }
    p('#9aa475', 52, 13, 2, 2);
  }
}

function drawEndingFloorEquipment(p, id, metal, body, accent) {
  const dark = '#2a3134';
  if (id === 'flood') {
    p('#465e65', 10, 10, 35, 8);
    p('#72a09d', 11, 10, 31, 1);
    p(body, 38, 6, 12, 13);
    p(metal, 40, 5, 7, 2);
    p('#2f4148', 16, 8, 12, 13);
    p('#6e8d90', 17, 8, 10, 4);
    p(accent, 18, 7, 7, 2);
    p('#869b91', 51, 12, 5, 2);
  } else if (id === 'street') {
    p('#514131', 11, 7, 41, 13);
    p('#a77e56', 13, 7, 37, 6);
    p('#c19c76', 14, 7, 34, 1);
    p('#785941', 15, 14, 33, 3);
    for (const x of [14, 45]) {
      p('#757e76', x, 15, 3, 9);
      p('#99988b', x - 2, 23, 7, 1);
    }
    p('#626e65', 20, 19, 13, 4);
  } else if (id === 'live') {
    p('#555162', 10, 11, 44, 8);
    p('#8a8397', 11, 11, 41, 1);
    p('#303843', 15, 7, 16, 7);
    p('#688080', 17, 8, 12, 4);
    for (const x of [34, 38, 42, 46]) {
      p(dark, x, 13, 2, 5);
      p(metal, x, 15 + x % 3, 2, 1);
    }
  } else if (id === 'tower') {
    p('#405261', 10, 5, 19, 15);
    p(metal, 11, 5, 17, 2);
    for (const y of [8, 12, 16]) {
      p('#252e3b', 12, y, 12, 2);
      p('#9cbead', 25, y, 2, 1);
    }
    p('#607985', 34, 10, 16, 6);
    p('#9aa8a8', 36, 9, 12, 2);
    p(accent, 44, 13, 3, 1);
    p('#465462', 40, 15, 3, 5);
  } else if (id === 'garden') {
    p('#685942', 10, 10, 44, 9);
    p('#a28f6a', 11, 10, 42, 1);
    for (const [x, y] of [[14,8],[23,5],[34,7],[44,5]]) {
      p('#5a7956', x, y, 8, 9);
      p('#81a273', x + 2, y, 5, 3);
      p('#b0a774', x + 2, y + 1, 2, 2);
      p('#524537', x + 1, 14, 7, 3);
    }
  } else if (id === 'archive') {
    p('#7d6954', 10, 11, 43, 8);
    p('#ad9675', 11, 11, 39, 1);
    for (const x of [16, 33]) {
      p('#363b3c', x, 7, 11, 8);
      p('#92928a', x + 1, 8, 9, 6);
      p('#555e5b', x + 4, 9, 3, 4);
      p('#d1b87a', x + 5, 10, 1, 2);
    }
    p('#817963', 40, 15, 10, 2);
  } else if (id === 'rail') {
    p('#393e3e', 8, 18, 49, 5);
    p('#655b47', 10, 9, 44, 10);
    p('#a17a54', 11, 8, 42, 4);
    p('#bc9870', 13, 8, 38, 1);
    for (const x of [15, 25, 35, 45]) {
      p('#2a3539', x, 12, 6, 6);
      p('#718882', x + 1, 13, 4, 3);
    }
    for (const x of [13, 48]) p('#262b2c', x, 21, 6, 4);
  } else {
    p('#504a38', 10, 9, 40, 11);
    p(metal, 11, 9, 38, 2);
    p('#262b2b', 15, 12, 22, 6);
    for (const x of [17, 21, 25, 29, 33]) p('#676f64', x, 13, 2, 4);
    p('#74765c', 40, 12, 7, 6);
    p('#a4a76d', 42, 13, 3, 2);
    p('#5f5644', 51, 11, 5, 9);
  }
}
function drawSmallDressingMirror(p, x, y, width, height) {
  p('#605457', x, y, width, height);
  p('#ad9b89', x, y, width, 1);
  p('#9b897c', x, y + 1, 1, height - 2);
  p('#86989e', x + 2, y + 2, width - 4, height - 4);
  p('#647881', x + 2, y + height - 6, width - 4, 4);
  for (let row = 2; row < height - 2; row++) {
    const glint = Math.floor(width * 0.7 - row * 0.6);
    const start = Math.max(2, glint);
    const end = Math.min(width - 2, glint + 3);
    if (end > start) p('#c5cfc9', x + start, y + row, end - start, 1);
  }
}

function drawModelRailScenery(p, {kind}) {
  if (serverLandmarks[kind]) {
    serverLandmarks[kind](p);
    return;
  }
  if (kind === 'minecart' || kind === 'ore-cart') {
    p('#313730', 4, 19, 24, 5);
    for (const x of [7, 22]) {
      p('#282b29', x, 20, 5, 5);
      p('#8c8c7f', x+1, 22, 2, 2);
    }
    p('#565c59', 3, 9, 26, 9);
    p('#6e7570', 5, 15, 22, 5);
    p('#a2a397', 2, 8, 28, 3);
    p('#353937', 5, 7, 22, 2);
    if (kind === 'ore-cart') {
      for (const [x,y] of [[7,4],[16,3],[12,0]]) {
        p('#555454', x, y, 9, 7);
        p('#88867b', x, y, 8, 2);
        p('#ae7765', x+3, y+3, 3, 2);
      }
    }
    return;
  }
  if (kind === 'carrot-beds') {
    for (const y of [11, 28, 45]) {
      p('#4c4132', 4, y, 84, 10);
      p('#7f6548', 4, y, 84, 2);
      p('#656445', 5, y+9, 82, 2);
      for (const x of [10,24,40,55,72]) {
        p('#b97c49', x+1,y+3,5,3);
        p('#976144', x+2,y+6,3,2);
        p('#768955', x+2,y-1,2,5);
        p('#66764d', x-1,y,3,2);
        p('#93a064', x+4,y-2,3,3);
      }
    }
    return;
  }
  if (kind === 'rabbit-office') {
    // Oak planks and an unfinished scaffold flank the quartz-block rabbit façade.
    p('#373b3170', 4, 57, 120, 5);
    serverBlockFaces(p,39,20,50,35,5,'#d6d7c6','#86948c');
    for (const x of [46,75]) serverBlockFaces(p,x,1,10,22,2,'#dcdecd','#8f9c93');
    p('#71604a', 5, 32, 65, 26);
    for (const y of [33,39,45,51]) p('#978264', 6,y,64,2);
    for (const x of [6,34,61]) p('#615440', x,32,4,26);
    p('#68756a', 3, 27, 68, 6);
    p('#919888', 5, 25, 66, 3);
    p('#454f4d', 13,36,16,12);
    p('#88a19b', 15,38,12,7);
    p('#bbcab5', 16,38,4,2);
    // The ears, cheeks and entrance are part of the same masonry.
    for (const x of [46,75]) {
      p('#a9afa5', x, 1, 11, 23);
      p('#c4c7b4', x, 1, 8, 23);
      p('#bd9794', x+2, 5, 4, 14);
    }
    p('#929d95', 41, 21, 51, 36);
    p('#c8cab8', 39, 20, 50, 32);
    p('#acb6aa', 39, 46, 50, 8);
    p('#4d5557', 48, 29, 5, 6);
    p('#4d5557', 75, 29, 5, 6);
    p('#ae8784', 61, 35, 6, 4);
    p('#9d8e7c', 54, 40, 21, 16);
    p('#4e443b', 57, 42, 15, 14);
    p('#8c7254', 58, 43, 6, 12);
    p('#b38f67', 62, 49, 2, 2);
    for (const x of [95,119]) p('#917658',x,22,3,35);
    for (const y of [26,40,53]) p('#a78f69',92,y,32,3);
    for (let i=0;i<12;i++) p('#80684e',96+i*2,39-i,3,2);
    return;
  }
  if (kind === 'moon-workbench') {
    // A crescent identifies the redstone rig even when its indicator lamp is dark.
    p('#5c5656', 10, 16, 4, 35);
    p('#564e65', 3, 4, 21, 20);
    p('#bfa773', 8,8,4,10);
    p('#bfa773', 12,15,5,4);
    p('#bfa773', 17,13,3,4);
    p('#deca8c', 10,7,3,3);
    p('#665440', 4, 44, 86, 12);
    p('#a68a65', 3, 42, 88, 4);
    for (const x of [8, 78]) p('#574a3c', x,53,5,7);
    p('#74766c', 24,34,23,8);
    p('#984d48', 26,31,3,6);
    p('#bc7361', 27,29,3,3);
    p('#99554e', 40,32,3,6);
    p('#9e5b51', 47,39,14,2);
    p('#9e5b51', 59,35,2,6);
    p('#504841', 63,23,17,18);
    for (const x of [65,72]) for (const y of [25,32]) p('#b78b55',x,y,5,5);
    return;
  }
  for (const [x,y] of [[1,10],[28,6]]) {
    p('#403b32', x,y,28,18);
    p('#95754b', x+1,y+2,26,15);
    p('#b39159', x+1,y+1,26,3);
    p('#594737', x+1,y+7,26,2);
    p('#b6b19a', x+12,y+6,3,6);
  }
}

const mannequinFigures = {
  standing: [
      '       SPPPS', '      SPLLLPS', '      PLLLPDS', '      PLLPJJS',
      '      SPLLJPS', '       SPPLS', '        SSS', '         PP',
      '      SPPLPPS', '    SPLLLLPPPDS', '   SPPLLLPPPSJJD', '   PSSPLLLPPSJD',
      '   PS PLLPPS', '  SPS SPLPPS', '  PS   PPLPS', '  PS   SPPS',
      '  DS   SPPS', ' SPD  SPPPPS', ' PP   PLLLPPS', ' PS   PLLPPPS',
      ' PS   SPLPPPS', ' D    SPS SPPS', '      PPS  PPS', '      PPS  PPS',
      '      PPS  SPS', '      PPD  SPS', '      DJS   PD', '      SPD   JD',
      '      PPS   PS', '     SPS    PPS', '     PPS    PPS', '     PPS    SPS',
      '     PS      PS', '     PS      PS', '     PS      PD', '    SPD      PD',
      '   SPPS     SPPS', '   SSSD     SSSS',],
  reaching: [
    '                  SPPLS', '                 PLLLPPS', '                 PLJDPPD',
    '                PLP  PPS', '                 PPPLPS', '                  PPPS',
    '                  SJD', '                SPPLPPS', '               SPLLLPPSJ',
    '              SPLLPPLPSD', '  LPS       SPPLJSPPLPS', '  PPPPLPSSPPLPPS  PLPPS',
    '    SSSPPPJPPSS   SPPS', '          SS      SPPS', '                  PPLPS',
    '                 SPPPPS', '                 PLPPPSD', '                 SPPS PPS',
    '                 PPS  PPS', '                 PPS   PPS', '                PPS    SPS',
    '                PPD     PPS', '                DJ      PPS', '               SPD       JD',
    '               PPS       SD', '               PS        PS', '              PPS        PPS',
    '              PS          PS', '              PS          PD', '             SPS          SPD',
    '           SPPLS         SPPS', '           SSSSD         SSSD',
  ],
  seated: [
    '      SLPP',
    '     SLLLPS',
    '     PLLLPPS',
    '     SPPSJPS',
    '      SPPLPS',
    '       DPPP',
    '     SSSDSS',
    '     PLLLPSSS',
    '    PPPPPLLPS',
    '   LPPPPPSDPSS',
    '   PPSPPPJJPPS',
    '   PPSPPPJDPSS',
    '    PSPPPPPPS',
    '    PSSPPPPSS',
    '    SDSPPPSSSSS',
    '    SPPSSPSSSSSPPPSSSS       SS',
    '     SPPPSPPPPSSSSPPPSSS    SSS',
    '       SPPLPPPPSSSSSSDSPPSSSSSS',
    '       SSPPSPPPPPSSSSDSSSPPPSSS',
    '        SSSSSPPPPPS SSSSSSSSSSS',
    '         S  SSSPPPPPS     S',
    '              SSPPPSD',
    '                SSPDPLP',
    '                  SSPPLL',
    '                    SPPPLP   P',
    '                     SSPPPPPPPP',
    '                       SSPPPPP',
    '                         SSSS',
  ],
  fallen: [
    '       SPPPS     S',
    '      SLLLPPS SLLLPPS',
    '      PLLPJDSDPPPPLLPS',
    '      SPPLPPDSPPPPPPPPS',
    '       DSPLPSSPPPPPPPPDSPSSS',
    '     PPPPSSSPSSSPPSSPSDSSPPSSS               P',
    'SSPPPSSSSSSSSSSSPPSSSSSSSSSSPPPSSSS         PPP',
    ' SSSSSSSSSSSSS  PPPS   SSSSSSSSPPPPDPPPP    PPP',
    '   S       PPPPPPDPS    SSSSSSSSSSSDPPPPPPPPPPP',
    '       PPPPPPPPSSDS           SSSSS SSSPPPPPPP',
    '        PPPPSSS            SSSDSS      SSSSSSP',
    '                         SSSDDSS',
    '                      SSSSDDSS',
    '                      SSSS',
    '                      SSS',
  ],
};

const mannequinResin = {L:'#cec9b6', P:'#aaa99a', S:'#80837d', D:'#555b5b', J:'#383d43'};

function drawDressingRoomScenery(p, {kind, pose = 'standing'}) {
  if (kind === 'broken-mannequin') {
    const figure = mannequinFigures[pose];
    const left = pose === 'standing' ? 4 : pose === 'fallen' ? 8 : 0;
    const bottom = pose === 'fallen' ? 24 : 29;
    if (pose === 'fallen') {
      p('#22232956', 15, 14, 13, 2);
      p('#22232949', 31, 17, 13, 2);
      p('#22232953', 48, 19, 6, 2);
    } else if (pose === 'seated') {
      p('#22232969', 7, 19, 8, 3);
      p('#22232952', 23, 20, 7, 2);
      p('#22232958', 24, 28, 6, 2);
    } else {
      p('#22232968', 7, 28, 21, 2);
    }
    for (const [y, row] of figure.entries()) {
      for (const [x, pixel] of [...row].entries()) {
        if (mannequinResin[pixel]) p(mannequinResin[pixel], left + x, bottom - figure.length + y, 1, 1);
      }
    }
    if (pose === 'standing') {
      p('#414648', 23, 23, 3, 3);
      p('#a7a79a', 24, 24, 3, 3);
      p('#8c8e83', 25, 26, 4, 2);
      p('#b0b0a0', 28, 27, 3, 2);
    }
    return;
  }
  if (kind === 'costume-rail') {
    p('#24252a80', 4, 27, 88, 3);
    for (const x of [7, 85]) {
      p('#343438', x, 4, 3, 23);
      p('#9b9794', x, 5, 1, 20);
      p('#524d50', x-3, 26, 9, 2);
      p('#28292b', x-2, 28, 3, 2);
    }
    p('#37343a', 7, 2, 81, 4);
    p('#a59b91', 8, 2, 79, 1);
    for (const [x, hem, cloth, light] of [
      [14, 24, '#655569', '#9b8091'], [29, 20, '#505b65', '#859598'],
      [49, 25, '#694f58', '#ae8886'], [65, 22, '#635f54', '#9b9580'],
    ]) {
      p('#b1a595', x+5, 4, 1, 4);
      p(light, x+2, 8, 8, 2);
      p(cloth, x, 10, 13, 6);
      p(cloth, x+2, 15, 9, hem-15);
      p(light, x+3, 10, 2, hem-12);
      p('#39373e', x+9, 14, 2, hem-14);
    }
    return;
  }
  if (kind === 'standing-mirror') {
    p('#26252c80', 8, 57, 47, 4);
    for (const x of [12, 45]) {
      p('#53494c', x, 44, 4, 14);
      p('#907b74', x-2, 57, 7, 2);
    }
    drawDressingMirror(p, 12, 2, 37, 52);
    return;
  }
  // A broad centre mirror and two hinged side mirrors sit on a shared counter.
  p('#29252d80', 2, 59, 156, 4);
  drawDressingMirror(p, 4, 6, 36, 43);
  drawDressingMirror(p, 39, 2, 82, 47);
  drawDressingMirror(p, 120, 6, 36, 43);
  for (const x of [8, 150]) for (const y of [10, 20, 30, 40]) {
    p('#8a7970', x-2, y-1, 6, 5);
    p('#ddc7a6', x-1, y, 4, 3);
  }
  p('#51464c', 2, 49, 156, 11);
  p('#a08a89', 2, 48, 156, 3);
  for (const x of [6, 130]) {
    p('#79686e', x, 52, 24, 8);
    p('#aa9992', x+8, 54, 8, 1);
  }
  p('#775965', 27, 43, 4, 6);
  p('#c3aea5', 28, 42, 2, 2);
  p('#3b3b43', 116, 45, 13, 4);
}

function drawPowerScenery(p, {kind}) {
  if (kind === 'switchboard') {
    p('#252925', 3, 6, 185, 24);
    for (let x = 5; x < 184; x += 36) {
      p('#505b52', x, 3, 34, 23);
      p('#899182', x, 3, 34, 2);
      p('#2d3735', x+3, 7, 27, 8);
      for (const offset of [5, 18]) {
        p('#bdb79c', x+offset, 8, 8, 5);
        p('#655648', x+offset+3, 10, 2, 3);
      }
      p('#323a36', x+4, 18, 18, 4);
      p('#ada076', x+10, 17, 4, 5);
      p('#87aa91', x+26, 18, 3, 3);
    }
    return;
  }
  // Both machines bolt to a concrete plinth; their upper silhouettes differ.
  p('#29282380', 5, 54, 184, 8);
  p('#4c4a40', 3, 48, 184, 10);
  p('#8a8270', 3, 47, 182, 3);
  p('#333630', 9, 41, 171, 6);
  if (kind === 'diesel') {
    p('#3f514b', 12, 13, 47, 30);
    p('#849481', 14, 10, 43, 5);
    for (let y = 18; y <= 36; y += 5) p('#263a35', 17, y, 36, 3);
    p('#56665c', 61, 22, 108, 20);
    p('#879081', 63, 21, 103, 3);
    for (const x of [69, 90, 111, 132]) {
      p('#3d4b43', x, 12, 15, 20);
      p('#899581', x+2, 11, 12, 5);
      p('#637966', x+1, 17, 12, 8);
      p('#474942', x+9, 30, 4, 10);
    }
    p('#9a8770', 73, 6, 83, 4);
    p('#796956', 152, 5, 6, 15);
    p('#525852', 158, 26, 18, 17);
    p('#b29f74', 164, 29, 5, 4);
  } else {
    p('#465152', 11, 19, 34, 23);
    p('#87938a', 14, 17, 29, 4);
    p('#8e806b', 44, 25, 16, 9);
    p('#4f4e44', 58, 13, 78, 30);
    for (const x of [61, 73, 85, 97, 109, 121]) {
      p('#71604e', x, 11, 10, 32);
      p('#b18c63', x+1, 12, 7, 5);
      p('#967552', x+1, 17, 7, 18);
      p('#634e41', x+2, 36, 7, 5);
    }
    p('#63716b', 137, 14, 32, 28);
    p('#94a093', 139, 12, 26, 5);
    for (const x of [143, 150, 157]) p('#3b4c48', x, 21, 3, 16);
    p('#4a554f', 174, 19, 6, 25);
    p('#b89157', 174, 18, 6, 4);
  }
  for (const x of [13, 173]) p('#b4ab92', x, 50, 3, 2);
}

function drawDressingMirror(p, x, y, w, h) {
  p('#39363f', x, y+2, w, h-2);
  p('#998b8d', x+2, y, w-4, h-2);
  p('#645963', x+3, y+2, w-6, h-5);
  p('#8799a1', x+4, y+3, w-8, h-7);
  p('#697c87', x+5, y+4, w-10, h-9);
  // Stepped silvering and a dim lower reflection keep the panes readable at map scale.
  const glassWidth = w-10;
  for (let row=0; row<h-9; row++) {
    const offset = Math.floor((h-10-row)/2);
    const streak = Math.min(7, glassWidth-offset);
    if (streak>0) p('#94a7ac', x+5+offset, y+4+row, streak, 1);
    if (offset+10<glassWidth) p('#82969d', x+15+offset, y+4+row, 2, 1);
  }
  p('#536570', x+5, y+h-11, glassWidth, 5);
  p('#bac1b9', x+5, y+3, glassWidth, 1);
}
