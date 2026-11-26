// Coordinates are native pixels at 32 px per cell.
// Front edge at (x,y); each row of the top recedes a pixel to the right.
function mailCase(p,x,y,w,h,depth,top,front,side) {
  for (let n=depth; n>0; n--) {
    p(top,x+n,y-n,w,1);
    p(side,x+w+n-1,y-n+1,1,h);
  }
  p(front,x,y,w,h);
}

function mailCastShadow(p,x,y,w,reach) {
  for (let n=0; n<reach; n++) {
    const shift=Math.floor(n*1.4);
    p(n<reach-2 ? '#201e204c' : '#211e202c',x+shift,y+n,w,1);
  }
  p('#211d1d70',x,y,w,2);
}

function drawFanEnvelope(p, x, y, paper, seal, size = 1) {
  const dot = (c, dx, dy, w, h) => p(c, x+dx*size, y+dy*size, w*size, h*size);
  dot('#62564e', 1, 1, 12, 8);
  dot(paper, 0, 0, 12, 8);
  for (let step = 0; step < 3; step++) {
    dot('#9d8b7c', 2*step, step, 2, 1);
    dot('#9d8b7c', 10-2*step, step, 2, 1);
  }
  dot(seal, 5, 3, 2, 2);
}

function mailBundle(p, x, y, sheets, paper, seal) {
  const h=sheets*3;
  mailCastShadow(p,x+2,y+12+h,22,3);
  mailCase(p,x,y+11,23,h,6,paper,'#b1a18b','#83786c');
  for (let i=2; i<h; i+=3) {
    p('#e0ceb0',x+(i%2),y+11+i,21,1);
  }
  for (let i=0; i<5; i++) {
    p('#a6907e',x+5+i,y+5+i,2,1);
    p('#a6907e',x+23-i*2,y+5+i,2,1);
  }
  p(seal,x+10,y+9,3,2);
  for(let i=0;i<6;i++) p('#ac8968',x+16+i,y+10-i,2,1);
  p('#795d4a',x+16,y+11,2,h);
}

function drawMailSack(p, x, y, cloth, light) {
  const bands = [[10,0,13,4],[13,4,9,3],[10,7,15,3],[7,10,20,4],
    [4,14,26,5],[2,19,30,11],[3,30,29,5],[6,35,24,3]];
  mailCastShadow(p,x+5,y+35,24,7);
  for (const [dx,dy,w,h] of bands) {
    p(cloth,x+dx,y+dy,w,h);
    const shade=Math.max(2,Math.floor(w/4));
    p('#382b314a',x+dx+w-shade,y+dy,shade,h);
  }
  p(light,x+10,y+12,4,4); p(light,x+6,y+16,5,12);
  p('#594d475c',x+17,y+10,3,9); p('#594d475c',x+20,y+17,3,7);
  p('#584a414f',x+7,y+31,19,3); p('#64554a',x+9,y+35,18,2);
  p('#5d4941',x+11,y+5,13,3); p('#c4a782',x+12,y+5,10,1);
  p('#ddcaaa',x+17,y+8,7,9); p('#9b7b66',x+19,y+12,3,1);
}

function drawMailFixture(p, placement) {
  if (placement === 'wall') {
    p('#4c433e',3,10,58,14); p('#92755b',4,10,55,2);
    for (const x of [7,25,43]) {
      p('#382f2d',x,13,14,7); p('#b19e83',x+2,17,10,2);
    }
    return;
  }
  mailCastShadow(p,5,25,51,4);
  mailCase(p,2,18,52,8,6,'#a08262','#71553f','#534337');
  p('#ba9673',3,18,50,1); p('#897053',5,23,46,2);
  drawFanEnvelope(p,7,8,'#cfbfa9','#a8595f');
  drawFanEnvelope(p,19,6,'#d2b0ab','#9c636a');
  drawFanEnvelope(p,38,9,'#b0c3bb','#667f76');
}

function drawMailScenery(p, {kind, y: row}) {
  if (kind === 'postbox') {
    // Japanese pillar box: domed cap, hooded slot and pale postal mark.
    mailCastShadow(p,14,54,33,11);
    mailCase(p,11,54,35,5,5,'#a0937e','#74695e','#514b45');
    p('#56423b',16,50,31,4); p('#794039',16,17,32,35);
    p('#ac5349',18,17,24,33); p('#c5725c',19,18,5,30);
    p('#92473f',37,19,6,31); p('#673936',44,18,3,31);
    p('#ab594a',15,9,33,9); p('#cb7960',18,7,26,6);
    p('#df9473',22,5,16,3); p('#904c43',43,10,5,7);
    p('#7f433c',13,16,37,3); p('#db9777',14,15,35,2);
    p('#654139',20,21,23,8); p('#392a29',22,23,18,4);
    p('#915747',19,19,23,4); p('#d99673',20,19,21,1);
    p('#ac725d',22,28,18,1);
    p('#e5d4b5',25,32,13,2); p('#e5d4b5',25,36,13,2);
    p('#e5d4b5',30,38,3,7); p('#7e443c',20,48,22,2);
  } else if (kind === 'sorting-desk') {
    mailCastShadow(p,12,45,169,10);
    for (const x of [21,175]) p('#4a4036',x,26,5,18);
    p('#63503e',12,45,154,4); p('#8e7356',13,44,153,1);
    for (const x of [9,92,164]) {
      mailCastShadow(p,x,54,7,5);
      mailCase(p,x,34,5,21,3,'#84684c','#816349','#4c3f34');
    }
    mailCase(p,2,30,169,8,17,'#a78665','#785b46','#574437');
    p('#c49d76',2,30,168,2); p('#584435',4,37,165,2);
    p('#967454',16,23,142,1); p('#b79a75',46,24,59,1);
    mailBundle(p,19,9,3,'#d8c9ae','#a55859');
    drawFanEnvelope(p,57,16,'#bdcfc7','#698e8a');
    drawFanEnvelope(p,77,14,'#d2b0ba','#985e78');
    p('#534742',111,18,14,9); p('#8a524a',114,10,8,10);
    p('#c38976',113,9,10,4);
    mailBundle(p,143,10,2,'#c5b4cb','#897494');
  } else if (kind === 'sacks') {
    drawMailSack(p,13,4,'#90826a','#afa183');
    drawMailSack(p,45,12,'#7b8977','#9aa68a');
    drawMailSack(p,4,23,'#a28c71','#beac89');
    drawFanEnvelope(p,70,50,'#c7b4bd','#94677d');
  } else if (kind === 'bundles') {
    mailBundle(p,3,3,3,'#d6c5a8','#af6267');
    mailBundle(p,38,5,2,row%2 ? '#acbfbb' : '#c8b3c8','#846d8e');
    drawFanEnvelope(p,75,17,'#dfd1b9','#ab6b67');
  } else if (kind === 'pigeonholes') {
    mailCastShadow(p,6,54,146,7);
    mailCase(p,2,10,149,45,7,'#a88b69','#5b483b','#4d3d33');
    p('#b09070',3,10,146,2);
    for (let i=0; i<7; i++) for (let j=0; j<2; j++) {
      const x=7+i*21, y=13+j*19;
      p('#705542',x,y,20,17); p('#342e2a',x+1,y+1,17,12);
      p('#564739',x+3,y+4,15,9);
      if ((i+j)%4) {
        p(['#c8ba9e','#afaeb7','#bda598'][i%3],x+3,y+8,13,4);
        p('#d9ceb3',x+3,y+8,11,1);
      }
      p('#aa8b66',x+1,y+14,18,2);
    }
  } else if (kind === 'dispatch-cart') {
    mailCastShadow(p,16,52,65,9);
    for (const x of [13,71]) {
      mailCastShadow(p,x+1,60,8,4);
      p('#363a39',x,53,10,8); p('#8b938e',x+2,55,4,3);
    }
    p('#484e4c',6,15,81,36); p('#99826b',9,17,75,27);
    mailBundle(p,12,9,2,'#dac6ad','#af6468');
    drawMailSack(p,47,4,'#9c8772','#bba78e');
    mailCase(p,6,36,72,16,9,'#91a49a','#687c79','#475e5b');
    p('#a4b6a9',6,36,71,2); p('#4a605c',8,49,68,3);
    drawFanEnvelope(p,40,37,'#d7c9af','#9d635c');
    p('#9aa8a1',4,13,3,39); p('#93a49d',86,7,3,44);
    p('#696e66',85,6,9,3);
  }
}

function drawScatteredMail(p, x, y) {
  if (y===9 && x===7) drawFanEnvelope(p,4,2,'#cebda4','#a86368');
  if (y===9 && x===8) drawFanEnvelope(p,0,13,'#b7c6bd','#75918a');
  if (y===12 && x===23) drawFanEnvelope(p,15,0,'#d9c1bd','#9a6973');
}
