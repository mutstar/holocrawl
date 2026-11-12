(function () {
  'use strict';
  // All coordinates are native pixels; no smooth scaling or image resampling.
  function rect(c,col,x,y,w,h) { c.fillStyle=col; c.fillRect(x,y,w,h); }
  function line(c,col,x,y,w) { rect(c,col,x,y,w,1); }
  function panel(c,x,y,w,h,face='#66574c') {
    rect(c,'#20262a',x,y,w,h); rect(c,face,x+2,y+2,w-4,h-5);
    line(c,'#b2a383',x+3,y+2,w-6); rect(c,'#373332',x+2,y+h-5,w-4,3);
  }
  function card(c,x,y,color,flip=false) {
    rect(c,'#222930',x,y,9,13); rect(c,flip?'#586d82':'#d7d4b7',x+1,y+1,7,10);
    if(flip){rect(c,'#8fa0ae',x+3,y+3,3,6);return;}
    rect(c,color,x+4,y+3,1,1); rect(c,color,x+3,y+4,3,3); rect(c,color,x+4,y+7,1,1);
    rect(c,color,x+2,y+2,1,1); rect(c,color,x+6,y+9,1,1);
  }
  function shadow(c,x,y,w,h) { rect(c,'rgba(12,16,19,.32)',x+2,y+3,w,h); }
  function chair(c,p) {
    const x=6,y=7; shadow(c,x,y+5,20,16);
    panel(c,x,y+5,20,17,'#8a565f'); rect(c,'#b17a7e',x+3,y+8,14,7);
    rect(c,'#514548',x+1,y+20,3,4);rect(c,'#514548',x+16,y+20,3,4);
    if(p.facing==='south') panel(c,x-1,y-4,22,9,'#84505a');
    else if(p.facing==='north') panel(c,x-1,y+17,22,8,'#84505a');
    else if(p.facing==='east') panel(c,x-3,y+1,7,22,'#84505a');
    else panel(c,x+17,y+1,7,22,'#84505a');
  }
  function table(c) {
    shadow(c,5,12,86,77);
    rect(c,'#25272a',5,16,86,66); rect(c,'#25272a',11,9,74,79);
    rect(c,'#58483d',8,17,80,62);rect(c,'#58483d',14,12,68,73);
    rect(c,'#a8966a',9,17,78,58);rect(c,'#a8966a',15,13,66,65);
    rect(c,'#39685d',14,20,68,52);rect(c,'#39685d',20,17,56,59);
    rect(c,'#45756a',19,22,58,45);rect(c,'#2b564f',20,65,56,7);
    line(c,'#769283',23,24,50);line(c,'#284d48',23,63,50);
    // Four card trays and a small shared draw/discard area.
    for(let k=0;k<3;k++){ card(c,33+k*10,18,'#7a4156'); card(c,33+k*10,60,'#427f8b'); }
    for(let k=0;k<2;k++){card(c,17,33+k*14,'#a88843',true);card(c,70,33+k*14,'#5c6194',true);}
    card(c,37,39,'#a46564',true); card(c,49,40,'#865783');
    rect(c,'#c4b380',56,54,5,2); rect(c,'#a4804d',56,56,5,2);
    line(c,'#8e7957',17,80,62);line(c,'#3b3732',17,84,62);
  }
  function cards(c) {
    shadow(c,5,7,86,53);panel(c,4,4,88,56,'#544b48');
    rect(c,'#2b3034',9,9,78,40);
    for(const y of [12,30]) {
      for(let n=0;n<7;n++) {const colors=['#758ca0','#996572','#b09a68','#6d8b78'];
        rect(c,colors[n%4],12+n*10,y,7,13);line(c,'#cac0a0',12+n*10,y+2,7);
        rect(c,'#d1c3a2',14+n*10,y+5,3,4);}
      line(c,'#9a8766',10,y+15,76);
    }
    line(c,'#9d8966',8,52,80);rect(c,'#73604a',9,55,78,4);
  }
  function board(c) {
    shadow(c,6,7,84,51);panel(c,5,4,86,52,'#9b8968');
    rect(c,'#293539',10,9,76,38);
    for(let n=0;n<4;n++) {
      rect(c,['#b28b73','#7da7a4','#a38cba','#b9ac72'][n],16,14+n*7,5,4);
      line(c,'#9dada6',25,15+n*7,24+n*3);line(c,'#657d7b',60,15+n*7,17);
    }
    rect(c,'#383537',13,56,4,5);rect(c,'#383537',79,56,4,5);
  }
  function reception(c) {
    shadow(c,4,17,88,42);panel(c,4,16,88,43,'#665443');
    rect(c,'#9a845f',6,17,84,20);line(c,'#c4ad7b',8,18,80);
    rect(c,'#4a403b',10,42,34,11);rect(c,'#4a403b',50,42,34,11);
    line(c,'#a39070',23,47,10);line(c,'#a39070',63,47,10);
    panel(c,60,7,22,18,'#5d7b76'); rect(c,'#b3c7b2',65,10,12,8);
    rect(c,'#36463e',65,19,12,3);card(c,15,19,'#9a596b');card(c,27,19,'#9a596b',true);
    rect(c,'#c2ac75',43,24,8,3);rect(c,'#7b674b',43,27,8,2);
  }
  function bench(c) {
    shadow(c,5,7,86,23);panel(c,4,5,88,12,'#845765');
    panel(c,4,15,88,12,'#976777');
    for(let n=1;n<3;n++)rect(c,'#69474f',4+n*29,17,2,6);
    rect(c,'#b59b73',4,12,4,9);rect(c,'#b59b73',88,12,4,9);
    rect(c,'#363538',10,26,4,4);rect(c,'#363538',82,26,4,4);
  }
  function drinks(c) {
    shadow(c,5,14,53,45);panel(c,4,13,55,46,'#64716b');
    rect(c,'#a2a997',6,14,51,17);line(c,'#ccd0b2',7,15,49);
    panel(c,9,4,22,24,'#526066');rect(c,'#b1aaa0',13,7,14,10);
    rect(c,'#252e35',16,12,7,8);rect(c,'#bdb398',18,22,5,5);
    for(const x of [37,47]) {rect(c,'#d0c7a6',x,22,6,8);rect(c,'#475f5a',x+1,23,4,3);}
    rect(c,'#3a4948',10,38,43,14);line(c,'#a3ac93',27,42,10);
  }
  function plant(c) {
    shadow(c,8,20,17,10);panel(c,9,19,15,11,'#9f8464');
    for(const [x,y,w,h] of [[5,9,9,7],[16,7,11,8],[10,2,10,9],[12,11,9,10]]) {
      rect(c,'#304f4a',x,y,w,h);rect(c,'#6a8b6a',x+1,y+1,w-3,3);
    }
    rect(c,'#607854',15,11,2,10);
  }
  function door(c,p,open) {
    c.save();c.translate(p.x*32,p.y*32);
    // Two identical metal leaves, built into a continuous threshold.
    rect(c,'#222b31',0,-10,64,10);
    if(!open) rect(c,'#222b31',0,0,64,32);
    rect(c,'#a18e68',0,-8,5,39);rect(c,'#a18e68',59,-8,5,39);
    rect(c,'#d0bd8c',1,-8,2,37);rect(c,'#d0bd8c',61,-8,2,37);
    if(open){
      rect(c,'#687679',5,0,5,29);rect(c,'#687679',54,0,5,29);
    }else{
      for(const x of [6,33]) {
        rect(c,'#627675',x,0,25,30);rect(c,'#91a29a',x+2,2,21,25);
        rect(c,'#395450',x+4,4,17,21);rect(c,'#7b9387',x+6,6,13,17);
        rect(c,'#ceb97e',x+(x===6?19:4),16,2,7);
      }
      rect(c,'#293639',31,0,2,30);
    }
    rect(c,'#79634b',3,-12,58,10);line(c,'#bdab7c',5,-12,54);
    panel(c,20,-19,24,15,'#857155');
    rect(c,'#d5cfad',25,-17,7,9);rect(c,'#a25b78',27,-14,3,3);
    rect(c,'#e0d9b5',32,-15,7,9);rect(c,'#4b8490',34,-12,3,3);
    rect(c,'#a3a99b',0,29,64,3);c.restore();
  }
  const renderers={table,cards,board,reception,bench,drinks,plant,chair};
  function draw(c,p){c.save();c.translate(p.x*32,p.y*32);renderers[p.id](c,p);c.restore();}
  window.PokajanSprites210={draw,door};
})();
