function drawGardenTrack(p, track, x, y) {
  const col=x-track.x, row=y-track.y;
  if (col<0 || row<0 || col>=track.width || row>=track.depth) return;
  const rail=col===0?8:22;
  if (y===track.crossingY) {
    // Infill level with the rail heads lets the cart cross the camera track.
    p('#545c50',0,1,32,30);
    for (const seam of [10,21]) p('#424a40',0,seam,32,1);
    for (const end of [3,27]) p('#778071',col===0?2:27,end,3,1);
  } else {
    p('#393c35',col===0?6:0,17,26,4);
  }
  const top=row===0?6:0, bottom=row===track.depth-1?24:32;
  p('#343b37',rail,top,4,bottom-top);
  p('#969a86',rail,top,1,bottom-top);
  p('#676e64',rail+1,top,2,bottom-top);
  p('#a79b76',rail-1,17,2,2);
  if (row===0 || row===track.depth-1) p('#8d7759',rail-2,row===0?5:23,8,3);
}

const gardenSpriteOrigins = {
  'glasshouse':[0,0], 'water-tank':[192,448],
  'dolly-camera':[160,192], 'potting-bench':[64,256],
  'plant-cart':[0,320], 'seed-drawers':[96,320], 'seed-cabinet':[0,384],
};

function drawPlantingRows(layer, width, flowering) {
  const rect = (color,x,y,w,h) => {
    layer.fillStyle = color;
    layer.fillRect(x,y,w,h);
  };
  // Work in double pixels so the soil and leaves read at dungeon zoom.
  layer.scale(2,2);
  const span = width*16;
  // Connect the ridges with recessed earth, stepping the ends into the yard.
  rect('#494035',5,6,span-10,37);
  rect('#494035',3,10,span-6,29);
  rect('#494035',2,18,span-4,12);
  for (let row=0; row<3; row++) {
    const y = 4+row*15;
    const left = [4,2,5][row], right = span-[4,6,3][row];
    for (let x=left; x<right; x++) {
      const end = Math.min(x-left,right-1-x);
      const taper = Math.max(0,4-end);
      const rise = Math.floor((x+row*9)/17)%3===1 ? 1 : 0;
      const top = y+rise+taper;
      const foot = y+11-Math.floor(taper/2);
      rect('#463c32',x,top,1,foot-top+1);
      rect('#65503c',x,top,1,foot-top-1);
      if (end>1) rect('#796249',x,top,1,Math.min(4,foot-top-2));
    }
    for (let i=0, x=left+8; x<right-6; i++, x+=13) {
      const gap = (i+row*3)%7===4;
      if (gap) {
        rect('#584635',x,y+5,3,1);
        continue;
      }
      const stem = y+4;
      rect('#414834',x-1,stem,3,2);
      rect('#526344',x-3,stem-2,3,2);
      rect('#728051',x-4,stem-3,3,2);
      rect('#657649',x+1,stem-3,2,3);
      rect('#87915e',x+2,stem-4,2,2);
      if ((i+2*row)%3===0) {
        rect('#667b50',x-1,stem-5,2,4);
        rect('#8b976c',x-1,stem-6,1,2);
      }
      if (flowering && (i+row)%3===1) {
        rect(row===1?'#c0a575':'#ac8886',x,stem-5,2,2);
      }
    }
  }
}

function drawGardenTools(layer) {
  const palette = {
    k:'#30312e', s:'#4e5552', m:'#808c86', h:'#b2b4a0',
    g:'#6a847b', l:'#95a499', d:'#4e6663',
    w:'#85654a', b:'#b5946d', t:'#624b3a', e:'#916d4e',
  };
  const stamp = (x,y,rows) => {
    rows.forEach((row,dy) => Array.from(row).forEach((pixel,dx) => {
      if (pixel==='.') return;
      layer.fillStyle=palette[pixel];
      layer.fillRect((x+dx)*2,(y+dy)*2,2,2);
    }));
  };
  // Lay the spade diagonally behind the barrow, with floor showing between them.
  stamp(2,0,[
    '.............hhh','............ms.s','............m..s',
    '............bms','...........bw','..........bw','.........bw',
    '........bw','....hh.bw','...hmmbw','..hmmmms','..hmmms',
    '..mmms','..ms',
  ]);
  // Far handle, stand, and the single wheel sit behind the metal tray.
  stamp(17,10,[
    '.........bbb','.......bbwww','.....bbww','...bbww','.bbww','bww',
  ]);
  stamp(16,21,['m...s','sm..s','.m..s','.ms.s','..mss','..sss']);
  stamp(1,23,[
    '..kkkk','.ksssskk','kssmmmsk','ksmhhmsk',
    'ksmhbmsk','kssmmssk','.kssssk','..kkkk',
  ]);
  stamp(5,21,['......mm','....mms','...mms','..mms','.mms','ms']);
  stamp(4,12,[
    '.........eee','......eeettttee','....metttttetttmm',
    '..hmttttttttttttml','hhllllllllllllllll',
    'mgggggggggggggggds','.mgggggggggggggds',
    '..mgggggggggggdds','...mgggggggggdds',
    '....mgggggggddk','.....sddddddsk','......ssssssk',
  ]);
  stamp(16,15,[
    '............bbb','..........bbwww','........bbwww',
    '......bbww','....bbww','..bbww','mmww','ss',
  ]);
}

function drawGardenScenery(layer, atlas, {kind,width,depth,flowering}) {
  if (kind==='wheelbarrow-spade') {
    drawGardenTools(layer);
    return;
  }
  if (kind==='planting-rows') {
    drawPlantingRows(layer,width,flowering);
    return;
  }
  const [sx,sy]=gardenSpriteOrigins[kind];
  const w=width*32, h=depth*32;
  layer.drawImage(atlas,sx,sy,w,h,0,0,w,h);
}

function drawGardenYard(layer, ending) {
  const fill=(color,x,y,w,h)=>{
    layer.fillStyle=color;
    layer.fillRect(x,y,w,h);
  };
  layer.save();
  layer.translate(6*32,10*32);
  // Keep the shared supply on the door side and the passages between houses clear.
  const pipe=(x1,y1,x2,y2)=>{
    const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.abs(x2-x1),h=Math.abs(y2-y1);
    fill('#303a34',x,y+1,w+4,h+4);
    fill('#546c60',x,y,w+3,h+3);
    fill('#819182',x,y,w+1,h+1);
  };
  pipe(274,52,295,52);pipe(274,52,274,104);pipe(274,104,326,104);
  pipe(326,104,326,308);
  for (const house of ending.scenery.filter(s=>s.kind==='glasshouse')) {
    const inlet=(house.x+house.width-6)*32-12, row=(house.y-10)*32+48;
    const trunk=row<104?274:326;
    pipe(inlet,row+4,trunk,row+4);
    fill('#918469',trunk,row+3,3,4);
  }
  layer.restore();
}
