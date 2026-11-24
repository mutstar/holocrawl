function drawArchiveReel(p, cx, cy, scale) {
  const disk = (color, x, y, radius) => {
    for (let dy=-radius; dy<=radius; dy++) {
      const half=Math.floor(Math.sqrt((radius+0.25)**2-dy**2));
      p(color,x-half,y+dy,2*half+1,1);
    }
  };
  const radius=Math.floor(scale*3.5);
  disk('#3d3933',cx,cy+2,radius);
  disk('#b1a995',cx,cy,radius);
  disk('#958c79',cx,cy,radius-2);
  for (const [dx,dy] of [[0,-2],[2,-0.5],[1.25,1.75],[-1.25,1.75],[-2,-0.5]]) {
    disk('#423f38',cx+Math.round(dx*scale),cy+Math.round(dy*scale),scale-1);
  }
  disk('#c4b9a1',cx,cy,2);
  p('#4b4841',cx,cy,1,1);
}

function drawArchiveCan(p, x, bottom, count, label) {
  for (let i=0; i<count; i++) {
    const y=bottom-i*5-5;
    p('#504e49',x+1,y+2,21,5);
    p('#817f73',x,y+1,23,3);
    p('#a7a397',x+3,y,17,1);
    p('#686b65',x+3,y+4,18,1);
    p(label,x+13,y+2,5,2);
  }
}

function drawFilmArchiveScenery(p, {kind,width,y,bank}) {
  const span=width*32;
  // The upper-left light leaves a soft tile-coloured shadow and a tight contact edge.
  const contact=(x,base,w) => {
    p('#231f1a32',x+2,base-1,w+2,4);
    p('#211d186c',x,base-1,w,2);
  };
  if (kind==='film-cart') {
    for (const x of [10,48]) {
      // Interrupted caster marks run out into the aisle in the direction of travel.
      p('#29272050',x+3,29,2,9);
      p('#99866a30',x+5,33,1,5);
      p('#29272038',x+2,40,2,5);
      contact(x,30,7);
    }
    p('#777d71',7,14,46,6);
    p('#575e55',53,14,4,6);
    for (const x of [10,48]) {
      p('#343432',x,24,7,6);
      p('#898980',x+2,25,3,3);
    }
    p('#424946',5,20,53,5);
    p('#889086',5,19,53,2);
    p('#777f77',53,5,3,15);
    p('#aeaa97',52,3,9,3);
    drawArchiveCan(p,7,18,2,'#b39373');
    drawArchiveCan(p,29,18,1,'#949f92');
    return;
  }
  if (kind==='film-cabinets') {
    // Floor channels for the bank of movable storage cabinets.
    for (const x of [11,span-15]) {
      p('#302e29',x,2,5,66);
      p('#77746a',x+1,3,2,64);
      p('#514e46',x-2,65,9,3);
      p('#969083',x+1,65,2,1);
    }
    for (let unit=0; unit<3; unit++) {
      const x=unit*74+2, top=unit===2?14:3;
      contact(x+2,60,69);
      p('#25231e36',x+69,top+9,5,53-top);
      p('#343937',x,top+2,72,59-top);
      p('#778074',x+2,top,65,10);
      p('#8a9281',x+2,top,65,1);
      p('#505b54',x+67,top+1,4,54-top);
      p('#444c45',x+4,56,64,3);
      for (const offset of [3,36]) {
        const door=x+offset;
        p('#57625c',door,top+11,30,44-top);
        p('#819083',door+1,top+11,1,42-top);
        p('#a99e83',door+10,top+15,11,3);
        p('#454e49',door+8,top+21,15,2);
        p('#454e49',door+8,top+25,15,2);
        p('#bac0ae',door+(offset===3?25:4),top+31,2,6);
      }
    }
    return;
  }
  if (kind==='packing-table') {
    p('#24221d30',13,43,108,10);
    for (const x of [12,108]) {
      contact(x,49,4);
      p('#504d44',x,39,4,10);
    }
    for (const x of [8,114]) contact(x,56,5);
    p('#454039',4,42,119,5);
    for (const x of [8,114]) p('#655d4f',x,42,5,14);
    p('#88745d',4,21,119,21);
    p('#aa9374',4,21,119,2);
    p('#735f4d',4,38,119,4);
    p('#625545',119,24,4,18);
    drawArchiveCan(p,10,33,2,'#959f91');
    p('#554b40',53,11,48,22);
    p('#967e60',55,11,44,4);
    p('#71644e',57,16,40,14);
    drawArchiveReel(p,74,25,3);
    p('#89745b',51,28,52,11);
    for (const x of [55,94]) p('#555650',x,28,4,11);
    p('#c1b297',70,31,13,5);
    return;
  }
  if (kind==='reel-bin') {
    // Slotted return bins: edge-on reels and a few empty slots expose the dividers.
    const x=3, w=span-7, top=bank===0?19:13;
    contact(x+3,61,w-6);
    p('#484239',x+3,top+39,w-6,61-top-39);
    p('#41413b',x,top+4,w,37);
    p('#8d806c',x+2,top,w-4,5);
    p('#504a40',x+3,top+5,w-6,25);
    const loaded=bank===0?[0,1,2,5]:[2,3,4,6];
    for (let slot=0; slot<7; slot++) {
      const sx=x+7+slot*15;
      p('#766e60',sx,top+9,2,21);
      if (!loaded.includes(slot)) continue;
      p('#59605a',sx+4,top+2,8,28);
      p('#a7a698',sx+5,top,5,28);
      p('#797f74',sx+8,top+3,3,26);
    }
    p('#71634f',x+1,top+28,w-2,12);
    p('#a59376',x+1,top+28,w-2,2);
    p('#b6ab91',x+11,top+32,14,4);
    if (bank===1) drawArchiveReel(p,span-24,37,3);
    return;
  }
  if (kind==='inspection-bench') {
    // A strip leaves the supply reel, crosses the lit gate and winds onto the take-up reel.
    p('#24221d38',11,49,109,7);
    for (const x of [9,111]) contact(x,58,6);
    p('#55524a',9,47,6,11);
    p('#55524a',111,47,6,11);
    p('#51473d',4,24,119,26);
    p('#8e7a61',4,22,119,22);
    p('#ab9575',4,22,119,2);
    p('#675649',5,44,117,5);
    p('#484a46',10,25,100,15);
    p('#8c8c7e',17,19,9,10);
    p('#8c8c7e',88,19,9,10);
    drawArchiveReel(p,20,17,4);
    drawArchiveReel(p,92,17,4);
    p('#b9ad90',46,28,29,12);
    p('#493e35',30,30,54,7);
    for (let x=32; x<83; x+=6) {
      p('#c9b591',x,30,2,1);
      p('#c9b591',x,36,2,1);
      p('#84624b',x,32,4,3);
    }
    p('#353a38',109,28,9,11);
    p('#b69368',111,30,4,3);
    return;
  }
  contact(3,61,span-8);
  for (const x of [5,span-14]) {
    p('#49463d',x-2,58,11,5);
    p('#817a68',x-1,61,9,1);
    p('#a29a84',x+2,61,2,1);
  }
  p('#312e2b',2,6,span-4,55);
  p('#766f60',3,1,span-9,8);
  p('#958a77',4,1,span-10,1);
  p('#514d44',span-6,3,4,54);
  p('#524f47',4,58,span-10,2);
  const labels=['#a39375','#9d8477','#879991'];
  for (let bay=0; bay<width/2; bay++) {
    const x=bay*64, pattern=bay+Math.floor(y/5);
    for (let tier=0; tier<2; tier++) {
      const bottom=29+tier*25;
      p('#423e38',x+5,bottom-19,55,20);
      if ((pattern+tier)%4===0) {
        drawArchiveReel(p,x+19,bottom-10,3);
      } else {
        drawArchiveCan(p,x+7,bottom,2+(pattern+tier)%2,labels[pattern%3]);
      }
      drawArchiveCan(p,x+34,bottom,1+(pattern+2*tier)%3,labels[(pattern+1)%3]);
      p('#797369',x+3,bottom+1,60,3);
      p('#57534b',x+3,bottom+4,60,1);
    }
    p('#66675e',x+2,9,3,50);
    p('#918c7e',x+2,9,1,49);
  }
  p('#63655c',span-5,7,3,52);
}
