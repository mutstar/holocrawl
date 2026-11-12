(function () {
  'use strict';
  const ink = '#272531', purple = '#675583', violet = '#9e83bb', shine = '#cfb3df';
  const teal = '#52918c', steel = '#425563', edge = '#8da6ac', gold = '#d6ac64';

  function pen(context,x,y) {
    const rect = (color,dx,dy,w,h) => {
      context.fillStyle = color;
      context.fillRect(x + dx,y + dy,w,h);
    };
    // Integer pixels keep the rail outline crisp at native dungeon scale.
    function line(color,x0,y0,x1,y1,width=1) {
      const dx = Math.abs(x1-x0), dy = -Math.abs(y1-y0), sx = x0<x1 ? 1 : -1, sy = y0<y1 ? 1 : -1;
      let error = dx+dy;
      for (;;) {
        rect(color,x0-Math.floor(width/2),y0-Math.floor(width/2),width,width);
        if (x0===x1 && y0===y1) break;
        const twice = 2*error;
        if (twice>=dy) { error+=dy; x0+=sx; }
        if (twice<=dx) { error+=dx; y0+=sy; }
      }
    }
    return {rect,line};
  }

  function coaster({rect:r,line:l}) {
    const runs = [
      [[21,123],[35,116],[48,100],[62,68],[76,42],[91,33],[113,33],[128,41],[146,63],
        [162,101],[180,123],[201,132],[344,132],[358,126],[370,111]],
      [[369,88],[358,74],[342,67],[314,67],[299,71],[286,83],[273,99],[254,106],[219,106]]
    ];
    const feet = [[40,110],[65,61],[91,33],[116,35],[145,62],[174,116],[203,132],[254,132],
      [310,132],[344,132],[352,72],[316,67],[287,82],[256,105],[226,106]];
    for (const [x,y] of feet) {
      r('rgba(0,0,0,.22)',x-9,149,24,5);
      r('#31343d',x-7,145,14,6);
      r(ink,x-3,y+7,7,139-y);
      r(steel,x-2,y+7,4,138-y);
      r('#657483',x-2,y+7,1,136-y);
      if (y<110) {
        l('#343741',x,y+20,x+14,y+40,3);
        l(steel,x,y+20,x+14,y+40,1);
      }
      r('#62616c',x-6,145,12,1);
    }
    for (const points of [...runs].reverse()) {
      for (let i=1;i<points.length;i++) {
        const [x,y]=points[i-1], [nx,ny]=points[i];
        l(ink,x,y+2,nx,ny+2,15);
        l('#524460',x,y+2,nx,ny+2,11);
      }
      for (let i=1;i<points.length;i++) {
        const [x,y]=points[i-1], [nx,ny]=points[i];
        const n=Math.max(1,Math.round(Math.hypot(nx-x,ny-y)/9));
        for(let j=0;j<n;j++){
          const ax=Math.round(x+(nx-x)*j/n), ay=Math.round(y+(ny-y)*j/n);
          l('#897395',ax,ay-4,ax,ay+8,2);
        }
      }
      for (const [dy,shade] of [[-4,violet],[4,purple]]) {
        for (let i=1;i<points.length;i++) {
          const [x,y]=points[i-1], [nx,ny]=points[i];
          l(shade,x,y+dy,nx,ny+dy,3);
          if (dy<0) l(shine,x,y+dy-1,nx,ny+dy-1,1);
        }
      }
    }
    // Exposed ends and stopped train with individual seat backs.
    for (const [x,y] of [[370,111],[369,88]]) {
      r(ink,x-2,y-8,6,17); r(gold,x,y-6,2,13);
    }
    for (const x of [233,262,291]) {
      r(ink,x,108,24,19); r(ink,x+3,104,13,6); r(ink,x+3,126,5,5); r(ink,x+16,126,5,5);
      r('#263943',x+2,113,21,12); r(teal,x+2,114,21,7);
      r('#b5d6c7',x+3,114,19,2); r('#94688e',x+5,106,10,7);
      r('#c195ae',x+5,106,10,2); r('#25363c',x+15,109,6,5);
      r(gold,x+20,118,3,2); r('#879099',x+4,127,3,2); r('#879099',x+17,127,3,2);
      if(x!==291) r('#64636c',x+24,122,5,2);
    }
  }

  const artists = {
    coaster,
    platform({rect:r}) {
      r('#272e38',1,4,190,50);
      r('#58636e',4,7,184,34);
      for (let x=5;x<187;x+=12) {
        r('#646e78',x,8,1,33);
        r('#4a525f',x,14,11,1);
      }
      r(gold,4,8,184,3); r('#38424e',4,42,184,11); r(edge,4,41,184,2);
      for (const x of [14,61,108,155]) {
        r('#414753',x,45,25,12); r('#72787e',x,44,25,2); r('#626a71',x,48,25,2);
        for (let dx=0;dx<25;dx+=7) r('#ab8757',x+dx,44,4,2);
      }
    },
    maintenance({rect:r}) {
      r('rgba(0,0,0,.26)',7,49,51,7); r('#29343a',6,23,51,29); r('#4e696e',8,22,47,5);
      r('#587478',9,28,26,21); r('#384b50',35,28,18,21);
      r(edge,9,27,44,1); r('#233138',14,32,17,3); r(gold,18,36,9,2);
      for (let y=32;y<46;y+=4) r('#637779',41,y,8,1);
      r('#805f4d',11,14,18,7); r('#b58a68',12,14,16,1); r(ink,16,12,8,3);
    },
    console({rect:r}) {
      r('rgba(0,0,0,.24)',7,54,21,5); r('#303842',8,27,17,29);
      r('#55626d',5,23,22,17); r(edge,5,23,22,1);
      r('#243842',8,26,13,8); r(teal,10,28,8,3);
      r('#c5d8b0',10,28,5,1); r('#a76963',23,29,2,2); r(gold,9,36,3,2);
    },
    queue({rect:r}) {
      r('rgba(0,0,0,.19)',4,22,120,3);
      r(ink,7,12,113,4); r(violet,7,12,113,1);
      for (const x of [6,44,82,119]) {
        r(ink,x-2,8,5,15); r(edge,x,9,2,12); r(gold,x-1,8,4,2);
        r('#69767f',x-2,22,6,2);
      }
    }
  };

  function door(context,entry,opened) {
    const {rect:r,line:l}=pen(context,entry.x*32,entry.y*32);
    r('#35404d',0,1,64,9); r(edge,0,0,64,2); r(purple,3,3,58,5);
    l(shine,27,6,31,3); l(shine,31,3,35,6); l(shine,35,6,39,4);
    for (const x of [5,56]) { r('#435663',x,10,3,20); r('#79a39f',x,11,1,11); }
    if (!opened) {
      r(ink,8,10,48,20);
      for (const x of [9,33]) {
        r(steel,x,11,22,18); r('#556d78',x+1,12,20,3); r('#28404c',x+3,16,16,7);
        r('#80aaa8',x+4,16,14,1); r(gold,x===9?28:34,24,2,3);
      }
    }
    r(edge,0,30,64,1); r('#3a4652',0,31,64,1);
  }

  window.CoasterSprites206 = {draw:(context,p)=>artists[p.id](pen(context,p.x*32,p.y*32)),door};
})();
