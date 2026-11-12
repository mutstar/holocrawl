(function () {
  function fill(c,color,x,y,w,h) {
    c.fillStyle = color;
    c.fillRect(x,y,w,h);
  }
  function shape(c,color,points) {
    c.fillStyle = color;
    c.beginPath();
    c.moveTo(...points[0]);
    for (const point of points.slice(1)) c.lineTo(...point);
    c.closePath();
    c.fill();
  }
  function deck(c,x,y,horizontal,variant) {
    fill(c,'#42382f',x,y,32,32);
    for (let board=0;board<4;board++) {
      const offset=board*8, color=['#8d6c50','#99765a','#a17c59'][(variant+board)%3];
      if (horizontal) {
        fill(c,color,x,y+offset,32,7);
        fill(c,'#b18e69',x+2,y+offset,28,1);
        fill(c,'#765943',x+6+(variant+board*7)%19,y+offset+3,6,1);
      } else {
        fill(c,color,x+offset,y,7,32);
        fill(c,'#b18e69',x+offset,y+2,1,28);
        fill(c,'#765943',x+offset+3,y+6+(variant+board*7)%19,1,6);
      }
    }
  }
  function fish(c) {
    fill(c,'#533f35',4,25,86,37);
    fill(c,'#a98462',8,30,79,28);
    for (const x of [12,37,65]) fill(c,'#d2ad7d',x,33,2,24);
    fill(c,'#2b474d',35,36,25,22);
    fill(c,'#759d99',39,38,17,16);
    fill(c,'#ddba83',37,46,21,3);
    fill(c,'#2f5057',3,3,90,29);
    fill(c,'#457780',6,4,84,21);
    for (const x of [7,20,33,46,59,72,85]) fill(c,'#6e9b9c',x,6,2,17);
    fill(c,'#b5b18c',4,26,88,3);
    fill(c,'#284854',29,6,38,16);
    shape(c,'#b6dbcb',[[36,14],[42,10],[53,10],[58,14],[53,18],[42,18],[36,15],[32,18],[32,10]]);
    fill(c,'#405c61',51,13,2,2);
    fill(c,'#7b583d',67,46,15,13);
    fill(c,'#c09d66',68,48,13,2);
  }
  function stage(c) {
    fill(c,'#373a44',4,22,184,72);
    fill(c,'#625572',9,21,174,65);
    fill(c,'#453e56',14,27,164,54);
    fill(c,'#88769a',17,31,158,2);
    for (const x of [16,164]) {
      fill(c,'#232b36',x,42,12,32);
      fill(c,'#72818d',x+3,47,6,6);
      fill(c,'#546479',x+3,60,6,8);
    }
    fill(c,'#aaa28e',82,56,28,3);
    fill(c,'#aaa28e',94,40,3,17);
    fill(c,'#d5c3ab',92,37,7,5);
    fill(c,'#7b4f6f',5,8,182,16);
    for (let i=0;i<13;i++) {
      fill(c,i%2?'#bd819d':'#d0ad95',6+i*14,9,13,10);
    }
    fill(c,'#d6b88d',6,21,180,2);
    for (const x of [28,54,80,106,132,158]) fill(c,'#e2cc9e',x,81,6,3);
    for (const x of [12,174]) fill(c,'#9c879d',x,18,5,67);
    fill(c,'#9a7789',79,89,34,5);
  }
  function ship(c) {
    fill(c,'#1b3949',18,102,217,13);
    const hull = [[5,65],[17,52],[36,42],[202,42],[225,51],[252,68],[236,85],[215,106],[35,106],[14,91]];
    shape(c,'#4a302a',hull);
    shape(c,'#89624b',[[9,65],[24,54],[40,45],[201,45],[225,55],[247,68],[227,84],[214,99],[38,99],[18,88]]);
    fill(c,'#573f37',35,96,183,5);
    for (const y of [53,62,71,80,89]) fill(c,'#6e503f',33,y,189,1);
    fill(c,'#ae8760',38,47,166,2);
    fill(c,'#b58b63',38,92,166,3);
    for (const x of [28,62,99,153,187,219]) fill(c,'#c5a06b',x,94,5,6);
    fill(c,'#4b3835',42,57,42,26);
    fill(c,'#92705c',45,57,36,19);
    fill(c,'#a95c62',46,56,34,6);
    fill(c,'#d0ad74',52,65,6,5);
    fill(c,'#d0ad74',68,65,6,5);
    fill(c,'#ae8863',124,8,5,67);
    shape(c,'#6e3d4e',[[82,13],[174,13],[166,42],[162,55],[87,55],[92,36]]);
    shape(c,'#ad626f',[[86,16],[168,16],[161,44],[157,51],[92,51],[97,36]]);
    fill(c,'#c88888',100,18,57,2);
    fill(c,'#dbc0a7',120,25,13,11);
    fill(c,'#dbc0a7',123,35,7,4);
    fill(c,'#874b58',123,29,2,2);
    fill(c,'#874b58',129,29,2,2);
    fill(c,'#68444d',126,6,20,6);
    fill(c,'#dbc084',172,66,14,11);
    fill(c,'#7d5a49',174,71,10,2);
  }
  const props = {fish,stage,ship};
  function landmark(c,point) {
    c.save();
    c.translate(point.x*32,point.y*32);
    props[point.type](c);
    c.restore();
  }
  function player(c,x,y) {
    fill(c,'#243736',x+8,y+25,17,4);
    fill(c,'#263c51',x+9,y+12,14,14);
    fill(c,'#4d8e9b',x+10,y+13,12,11);
    fill(c,'#e5c38d',x+13,y+7,7,7);
    fill(c,'#26374a',x+10,y+5,13,4);
    fill(c,'#a9c4b7',x+11,y+6,11,2);
    fill(c,'#eed098',x+12,y+16,8,2);
    fill(c,'#d9e6d2',x+22,y+15,2,9);
  }
  window.LagoonArt213 = {fill,deck,landmark,player};
})();
