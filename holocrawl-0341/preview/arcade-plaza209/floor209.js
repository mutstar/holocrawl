(function () {
  'use strict';

  const cache = new Map();

  function tile(x,y) {
    const variant = RandomFloor.index('ARCADE-FLOOR209',0,x,y);
    const parity = (x+y)&1;
    const key = parity+':'+variant;
    if(cache.has(key))return cache.get(key);
    const canvas=document.createElement('canvas');
    canvas.width=canvas.height=32;
    const q=canvas.getContext('2d');
    const fill=(color,x,y,w,h)=>{q.fillStyle=color;q.fillRect(x,y,w,h);};
    const colors=parity?['#383449','#39354b','#373448','#39354a']:['#302d40','#312e42','#322e41','#302e40'];
    fill(colors[variant%4],0,0,32,32);
    // Low-contrast carpet-tile joints, worn fibres and sparse arcade inlays.
    fill(parity?'#302d40':'#292739',0,31,32,1);
    fill(parity?'#302d40':'#292739',31,0,1,32);
    fill(parity?'#3d394f':'#353146',1,1,29,1);
    for(let k=0;k<7;k++){
      const px=3+(variant*7+k*13)%25,py=4+(variant*11+k*7)%23;
      fill(parity?'#3e394e':'#373246',px,py,2,1);
    }
    if(variant===0){
      fill('#795c80',15,11,3,11);
      fill('#795c80',11,15,11,3);
      fill('#997693',15,14,3,2);
    }else if(variant===1){
      for(let row=0;row<5;row++){
        const inset=Math.abs(row-2)*2;
        fill('#48737c',11+inset,11+row*2,10-inset*2,2);
      }
      fill('#79a5a5',15,11,2,2);
    }else if(variant===2 && parity){
      fill('#706580',10,11,3,9);
      fill('#706580',10,18,10,3);
      fill('#9b7a7b',21,10,2,2);
    }
    cache.set(key,canvas);
    return canvas;
  }

  function contains(map,x,y) {
    if(map.inner[y*map.w+x])return true;
    return map.doors.some(door=>x>=door.x && x<door.x+door.w && y>=door.y && y<door.y+door.h);
  }

  function draw(q,map,x,y) {
    const px=x*32,py=y*32;
    q.drawImage(tile(x-map.origin.x,y-map.origin.y),px,py);
    const fill=(color,a,b,w,h)=>{q.fillStyle=color;q.fillRect(px+a,py+b,w,h);};
    const wall=(dx,dy)=>!map.cells[(y+dy)*map.w+x+dx];
    // A subdued double border follows the actual wall outline, including bends.
    if(wall(0,-1)){fill('#292938',0,0,32,4);fill('#6a526f',0,4,32,2);fill('#41475b',0,7,32,1);}
    if(wall(0,1)){fill('#292938',0,28,32,4);fill('#6a526f',0,26,32,2);fill('#41475b',0,24,32,1);}
    if(wall(-1,0)){fill('#292938',0,0,4,32);fill('#6a526f',4,0,2,32);fill('#41475b',7,0,1,32);}
    if(wall(1,0)){fill('#292938',28,0,4,32);fill('#6a526f',26,0,2,32);fill('#41475b',24,0,1,32);}
    // A continuous finish-line strip sits immediately in front of the race gate.
    const gate=map.circuit;
    if(y===gate.y+gate.h && x>=gate.x && x<gate.x+gate.w){
      fill('#263d4b',0,0,32,17);
      fill('#689b9f',0,0,32,2);
      for(let row=0;row<2;row++)for(let col=0;col<4;col++){
        fill((row+col)%2?'#354551':'#a2aca8',col*8,3+row*5,8,5);
      }
      fill('#689b9f',0,14,32,2);
    }
  }

  window.ArcadeFloor209={contains,draw,tile};
})();
