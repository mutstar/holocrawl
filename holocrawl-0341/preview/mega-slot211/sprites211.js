(function () {
  'use strict';
  const colors=[{body:'#607b80',edge:'#8eb1af',lit:'#b4d7c4'},
    {body:'#7c627d',edge:'#b99ab0',lit:'#dfb8cb'},
    {body:'#877256',edge:'#b5a17b',lit:'#e5cb8c'}];
  function r(c,col,x,y,w,h){c.fillStyle=col;c.fillRect(x,y,w,h);}
  function panel(c,x,y,w,h,col){r(c,'#20252b',x,y,w,h);r(c,col,x+2,y+2,w-4,h-4);r(c,'#b0a286',x+2,y+2,w-4,1);}
  function shadow(c,x,y,w,h){r(c,'rgba(10,13,20,.35)',x+2,y+3,w,h);}
  function icon(c,x,y,type,col,scale=1){
    const shapes=[['..###..','....##.','...##..','..##...','.##....','.##....','.##....'],
      ['...#...','..###..','#######','.#####.','..###..','.##.##.','.#...#.'],
      ['..###..','.#####.','.#####.','.#####.','#######','.......','..###..']];
    shapes[type%3].forEach((row,dy)=>[...row].forEach((p,dx)=>{if(p==='#')r(c,col,x+dx*scale,y+dy*scale,scale,scale);}));
  }
  function reels(c,x,y,cellW,cellH,seed,large=false){
    panel(c,x-3,y-3,cellW*3+6,cellH+6,'#403a42');
    for(let n=0;n<3;n++){
      r(c,'#ded8bb',x+n*cellW,y,cellW-2,cellH);
      r(c,'#b4b29c',x+n*cellW,y,cellW-2,2);r(c,'#f0e5c5',x+n*cellW,y+3,cellW-2,1);
      const scale=large?2:1;
      icon(c,x+n*cellW+Math.floor((cellW-2-7*scale)/2),y+Math.floor((cellH-7*scale)/2),(seed+n)%3,['#945469','#4b7c79','#a37d39'][(seed+n)%3],scale);
      r(c,'#9b9785',x+n*cellW,y+cellH-2,cellW-2,2);
    }
  }
  function slot(c,p){
    const col=colors[p.variant];shadow(c,7,7,46,53);
    panel(c,8,7,44,52,col.body);panel(c,11,2,38,13,col.body);
    r(c,p.worn?'#6f7772':col.edge,13,4,34,1);
    icon(c,26,5,1,p.worn?'#969b89':col.lit);
    r(c,'#2a3038',12,18,36,24);reels(c,15,22,11,15,p.variant);
    r(c,col.edge,11,42,38,10);r(c,'#35434a',13,43,34,7);
    for(let n=0;n<3;n++){r(c,['#d9bc79','#92b5a7','#b58398'][n],17+n*10,45,5,3);}
    r(c,'#28313a',20,53,20,4);r(c,'#abb5a7',20,53,20,1);
    r(c,'#b1b5a3',53,20,2,21);r(c,'#52656a',51,38,4,4);r(c,'#c18b8c',51,16,6,6);r(c,'#e4b4a4',52,16,3,2);
    r(c,'#414747',11,60,39,3);
    // A few chips in the casing, kept away from the three readable reel windows.
    if(p.worn){r(c,'#3c474e',9,50,4,2);r(c,'#55565c',44,10,4,3);}
  }
  function mega(c){
    shadow(c,7,8,113,53);panel(c,7,8,113,51,'#6f616f');
    panel(c,19,2,88,12,'#8b7656');r(c,'#c1a975',22,4,82,1);
    for(const x of [33,59,85])icon(c,x,5,1,'#d9c893');
    r(c,'#35313d',13,17,100,31);reels(c,33,20,21,23,0,true);
    for(const x of [15,108])for(let y=20;y<=42;y+=7)r(c,y%2?'#d0bd86':'#a19cb5',x,y,3,3);
    r(c,'#b09a6f',12,49,103,6);r(c,'#4a5155',26,50,75,4);
    for(const x of [36,61,86])r(c,'#cbb584',x,50,6,3);
    r(c,'#242e34',50,57,28,3);r(c,'#84938e',50,57,28,1);
    r(c,'#48434b',13,61,102,2);
  }
  function stool(c){
    c.translate(14,0);
    shadow(c,9,12,17,16);r(c,'#4c5558',15,15,3,12);r(c,'#92968a',16,16,1,10);
    r(c,'#303740',9,26,16,3);r(c,'#858d85',11,26,12,1);
    panel(c,8,7,18,12,'#8d617a');r(c,'#b18d9c',11,9,12,3);
  }
  function sign(c){
    shadow(c,7,6,49,52);panel(c,7,5,49,49,'#897557');r(c,'#2c353c',12,10,39,36);
    r(c,'#c6ad74',26,14,12,11);r(c,'#6f6549',29,17,6,5);r(c,'#dfca91',28,15,8,1);
    r(c,'#abb7aa',17,31,29,2);r(c,'#718d85',17,37,24,2);
    r(c,'#4b4346',12,54,4,8);r(c,'#4b4346',47,54,4,8);
  }
  function coinCabinet(c){
    shadow(c,6,7,50,53);panel(c,6,5,50,55,'#63716b');r(c,'#333f41',11,10,40,34);
    for(let row=0;row<2;row++)for(let n=0;n<4;n++){
      const x=13+n*9,y=15+row*16;r(c,'#91774a',x,y,7,9);r(c,'#d0b37a',x,y,7,2);r(c,'#b49b64',x,y+4,7,1);
    }
    r(c,'#9d9e8d',10,29,42,2);r(c,'#a5a28d',11,45,40,2);r(c,'#3b4848',12,49,38,7);r(c,'#c1b38a',27,51,9,2);
  }
  function counter(c){
    shadow(c,3,7,90,23);panel(c,3,6,90,25,'#755f51');r(c,'#b49d70',5,7,86,10);r(c,'#d0b887',7,7,82,1);
    for(const x of [10,38,66]){r(c,'#4f4442',x,20,22,7);r(c,'#b7a07c',x+8,22,6,1);}
    panel(c,65,0,21,13,'#5c7f7b');r(c,'#c5c8a5',69,3,13,5);
    for(const x of [16,29,42]){r(c,'#8b7147',x,8,8,5);r(c,'#dfc18a',x,8,8,2);}
  }
  function bench(c){
    shadow(c,5,8,86,21);panel(c,4,5,88,12,'#795d73');panel(c,4,15,88,12,'#96718b');
    for(const x of [33,62])r(c,'#604a61',x,17,2,6);
    r(c,'#b3a17b',4,12,4,9);r(c,'#b3a17b',88,12,4,9);r(c,'#383840',10,26,4,4);r(c,'#383840',82,26,4,4);
  }
  function bin(c){shadow(c,10,12,14,17);panel(c,9,9,15,20,'#566968');r(c,'#8d9b8e',8,8,17,4);r(c,'#29363e',12,9,9,2);}
  function door(c,p,opened){
    c.save();c.translate(p.x*32,p.y*32);
    r(c,'#252632',0,-11,64,11);if(!opened)r(c,'#242b34',0,0,64,31);
    for(const x of [0,59]){r(c,'#9f8b6a',x,-10,5,40);r(c,'#c7b48c',x+1,-10,2,39);}
    if(opened){r(c,'#7b7285',5,0,5,29);r(c,'#7b7285',54,0,5,29);}
    else for(const x of [6,33]){
      r(c,'#6e667c',x,0,25,30);r(c,'#a19ba3',x+2,2,21,25);r(c,'#454254',x+4,4,17,21);
      icon(c,x+9,8,1,'#ad9c78');r(c,'#d0b78b',x+(x===6?19:4),19,2,6);
    }
    panel(c,3,-14,58,14,'#8c785d');
    for(let n=0;n<3;n++){r(c,'#d8d2b4',17+n*11,-12,9,10);icon(c,18+n*11,-11,0,'#9b667a');}
    r(c,'#a7a799',0,29,64,3);c.restore();
  }
  const render={slot,mega,stool,sign,coinCabinet,counter,bench,bin};
  function draw(c,p){c.save();c.translate(p.x*32,p.y*32);render[p.id](c,p);c.restore();}
  window.MegaSlotSprites211={draw,door};
})();
