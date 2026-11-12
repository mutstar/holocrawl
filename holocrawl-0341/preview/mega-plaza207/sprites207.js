(function () {
  'use strict';
  const ink='#242530', trim='#94a2aa', dark='#35434e', lamp='#e0bb83';
  const colors=['#bc879b','#a6b18b','#83b3bd','#c5a175','#a892b8'];
  const pixel=(g,x,y)=>(c,dx,dy,w,h)=>{g.fillStyle=c;g.fillRect(x+dx,y+dy,w,h);};
  const atlas=new Map(), cabinets={};
  const artSize={coaster:[12,5],platform:[6,2]};
  async function load() {
    for(const [id,file] of [['capsule','kong'],['crane','crane']]){
      const image=new Image();
      image.src='../arcade-plaza191/assets/'+file+'-native.png';
      cabinets[id]=image;
    }
    await Promise.all(Object.values(cabinets).map(image=>image.decode()));
  }

  function enlarged(g,p,x,y) {
    const [w,h]=artSize[p.id];
    if(!atlas.has(p.id)){
      const sprite=document.createElement('canvas'); sprite.width=w*32; sprite.height=h*32;
      CoasterSprites206.draw(sprite.getContext('2d'),{id:p.id,x:0,y:0});
      atlas.set(p.id,sprite);
    }
    const sprite=atlas.get(p.id);
    const drawnHeight=p.id==='coaster'?Math.round(sprite.height*4/3):p.h*32;
    g.drawImage(sprite,x,y+(p.h*32-drawnHeight),p.w*32,drawnHeight);
  }

  function capsule(r) {
    r('rgba(0,0,0,.26)',11,116,173,10);
    r(ink,7,27,177,93); r('#594954',10,29,171,89);
    r('#8e6c7f',10,30,171,3); r('#715365',12,35,167,36);
    r('#7b6070',17,39,158,27); r('#937483',17,39,158,1);
    for(let x=22;x<172;x+=12)r('#6a5362',x,42,1,24);
    r(ink,5,68,181,15); r('#a58191',7,68,177,10); r('#ccb0a9',7,68,177,2);
    for(let x=10;x<181;x+=18)r('#806878',x,70,9,8);
    r('#423944',11,83,169,30); r('#78656a',11,112,169,3);
    // Small side dispensers flank the original Capsule Kong machine.
    for(const [i,x] of [15,43,122,150].entries()){
      r(ink,x,79,27,34); r('#776878',x+2,82,23,29); r('#34464f',x+4,83,19,16);
      r('#62777d',x+5,84,17,2);
      [[7,89],[13,90],[17,94],[8,94]].forEach(([dx,y],j)=>{
        r(colors[(i+j)%colors.length],x+dx,y,5,4);r('#d0c0ae',x+dx+1,y,2,1);
      });
      r('#4b4656',x+4,100,19,9); r(lamp,x+8,102,4,2);r('#312f3c',x+16,103,5,3);
    }
    r(ink,78,17,34,24); r('#ac8496',80,18,30,20); r('#644958',82,20,26,16);
    r('#ebceaa',87,23,16,9);r('#c891a5',87,28,16,4);
    r('#644958',87,22,2,2);r('#644958',101,31,2,2);
  }

  function crane(r) {
    r('rgba(0,0,0,.28)',9,143,145,10);
    r(ink,6,28,148,119); r(dark,8,29,144,116);
    r('#46616c',10,31,140,48); r('#73929c',10,31,140,2);
    r('#567780',13,38,134,1);
    r('#3d5866',18,41,124,27); r('#4c6976',21,43,118,1);
    r(ink,5,72,150,11); r('#688e96',6,73,148,7); r('#9bb6b4',6,73,148,2);
    r('#282e39',10,83,140,54);
    for(const [i,x] of [13,58,103].entries()){
      r('#607f89',x,84,41,56); r('#354c58',x+3,86,35,36);
      r('#486673',x+4,87,33,2);r('#52717d',x+4,89,1,28);
      const hook=x+15+7*i;
      r(trim,hook,88,2,12); r(trim,hook-3,99,8,2);
      r('#adb6b0',hook-4,100,2,4);r('#adb6b0',hook+4,100,2,4);
      for(const [j,dx] of [7,15,26].entries()){
        const c=colors[(i+j+1)%colors.length], y=112+(j%2)*2;
        r(c,x+dx,y,9,7);r(c,x+dx+1,y-3,2,4);r(c,x+dx+6,y-3,2,4);
        r(ink,x+dx+2,y+2,1,1);r(ink,x+dx+6,y+2,1,1);
      }
      r('#34434e',x+2,125,37,12); r('#729299',x+2,124,37,2);
      r('#b88b9e',x+6,127,3,4);r(lamp,x+17,128,3,2);r(ink,x+25,128,10,6);
    }
    r('#a36484',6,73,148,3);
    r(ink,63,17,34,25);r('#a36484',65,18,30,21);r('#415664',67,20,26,17);
    r('#d5d1b8',73,24,14,2);r('#d5d1b8',79,25,2,7);
    r('#d5d1b8',75,30,10,2);r('#d5d1b8',74,31,2,3);r('#d5d1b8',84,31,2,3);
  }

  function bench(r){
    r('rgba(0,0,0,.27)',5,23,54,5);
    for(const x of [8,51])r(ink,x,11,5,15);
    r('#4a525c',6,7,52,6);r('#9097a0',6,7,52,1);
    r('#5c606b',6,16,52,5);r('#848895',6,16,52,1);
  }

  function draw(g,p) {
    const x=p.x*32,y=p.y*32,r=pixel(g,x,y);
    if(artSize[p.id]) enlarged(g,p,x,y);
    else if(p.id==='capsule'){
      capsule(r);
      g.drawImage(cabinets.capsule,x+69,y+62,54,54);
    }
    else if(p.id==='crane'){
      crane(r);
      g.drawImage(cabinets.crane,x+48,y+77,64,64);
    }
    else if(p.id==='bench')bench(r);
    else CoasterSprites206.draw(g,p);
  }
  function gate(g,p) {
    const r=pixel(g,p.x*32,p.y*32);
    r('#677a88',0,29,96,2);r('#424f61',0,31,96,1);
    for(const x of [0,84]){
      r(ink,x,8,12,21);r('#62677f',x+1,9,10,19);r('#ad92bf',x+1,9,10,2);
      r(lamp,x+4,13,4,2);r('#9c86aa',x+1,26,10,2);
    }
    for(const x of [22,41,60])r('#aaa08c',x,22,13,2);
  }
  window.PlazaSprites207={load,draw,gate};
})();
