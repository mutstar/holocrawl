(function () {
  function pixel(c,color,x,y,w,h) {
    c.fillStyle = color;
    c.fillRect(x,y,w,h);
  }
  function panel(c,x,y,w,h,face) {
    pixel(c,'#19242a',x,y,w,h);
    pixel(c,face,x+2,y+2,w-4,h-4);
    pixel(c,'#a6b7a8',x+2,y+2,w-4,1);
  }
  function coin(c,x,y,size) {
    pixel(c,'#a78348',x+2,y,size-4,size);
    pixel(c,'#a78348',x,y+2,size,size-4);
    pixel(c,'#dfbc72',x+2,y+2,size-4,size-4);
    pixel(c,'#9b7948',x+Math.floor(size/2),y+3,1,size-6);
  }
  function vault(c) {
    pixel(c,'#282f34',6,9,85,53);
    panel(c,4,4,88,55,'#576771');
    panel(c,13,9,70,43,'#6f8589');
    panel(c,22,13,52,35,'#50616a');
    pixel(c,'#99aca8',23,15,50,2);
    pixel(c,'#9aafa8',45,20,5,21);
    pixel(c,'#9aafa8',37,28,21,5);
    coin(c,43,26,9);
    for (const y of [17,37]) pixel(c,'#adb5a4',18,y,6,5);
    pixel(c,'#38454b',6,56,84,4);
  }
  function teller(c,p) {
    pixel(c,'#282f34',4,11,122,21);
    panel(c,3,8,122,22,'#566e69');
    pixel(c,'#ae9470',5,15,118,6);
    pixel(c,'#d2b789',5,15,118,1);
    for (const x of [7,66]) {
      panel(c,x,2,54,12,'#648b91');
      pixel(c,'#8eaaa8',x+3,4,44,1);
      pixel(c,'#acc1b6',x+7,6,2,5);
      pixel(c,'#354b4d',x+1,22,50,5);
    }
    for (const x of [45,79]) {
      if (p.prizes) {
        panel(c,x,10,12,9,'#a97f92');
        pixel(c,'#ddbe95',x+6,11,1,7);
      } else {
        coin(c,x,11,8);
      }
    }
  }
  function rail(c) {
    pixel(c,'#79684f',11,13,74,2);
    for (const x of [8,45,82]) {
      pixel(c,'#2d3737',x,21,9,4);
      pixel(c,'#ac9671',x+3,11,3,12);
      pixel(c,'#d1b587',x+2,10,5,3);
    }
  }
  function sign(c) {
    panel(c,5,5,22,18,'#647575');
    coin(c,12,9,8);
    pixel(c,'#6b7d76',14,23,4,7);
  }
  function gate(c,p,open,staff=false) {
    c.save();
    c.translate(p.x*32,p.y*32);
    if (!open) {
      panel(c,4,0,56,30,'#4c6367');
      panel(c,7,4,24,22,'#577c80');
      panel(c,33,4,24,22,'#577c80');
      coin(c,26,8,12);
    }
    for (const x of [0,59]) {
      pixel(c,'#a48e6a',x,-5,5,35);
      pixel(c,'#d6bb8d',x+1,-5,1,34);
    }
    panel(c,0,-12,64,13,staff?'#566b70':'#927951');
    if (!staff) {
      coin(c,27,-11,10);
    } else {
      pixel(c,'#abc1bb',21,-7,22,2);
    }
    pixel(c,'#a7a99c',0,30,64,2);
    c.restore();
  }
  const sprites = {vault,teller,rail,sign};
  function draw(c,p) {
    if (!sprites[p.id]) {
      MegaSlotSprites211.draw(c,p);
      return;
    }
    c.save();
    c.translate(p.x*32,p.y*32);
    sprites[p.id](c,p);
    c.restore();
  }
  window.ExchangeSprites212 = {draw,gate};
})();
