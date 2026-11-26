// Each strip covers four cells. The wall atlas supplies the silhouette, coping and light.
const endingWallMaterials = {
  'family-bakery': ['#988574',p=>{
    p('#716256',0,22,128,10); p('#aa947b',0,21,128,2);
    for(const x of [5,39,69,102]) {p('#574d47',x,24,2,8);p('#8a7765',x+2,24,14,1);}
    p('#6c5750',0,28,128,1);
  }],
  'fubuki-er': ['#9baba0',p=>{
    p('#657e78',0,19,128,13); p('#b6b9a4',0,18,128,2);
    p('#475d59',0,23,128,4); p('#8c9a88',0,23,128,1);
    for(const x of [22,67,103]) p('#83958c',x,9,1,9);
    p('#605f54',74,23,8,2); p('#586e68',15,28,24,1);
  }],
  foley: ['#716552',p=>{
    for(let x=0;x<128;x+=8){const h=5+(x%24)/2;p('#a08a69',x,12,4,h);p('#4d473e',x+4,13,2,h);}
    p('#49483f',0,28,128,4);
  }],
  'oozora-police': ['#7f898a',p=>{
    p('#384d5a',0,19,128,13); p('#a99c79',0,19,128,2);
    for(const x of [11,74]) {p('#616e72',x,8,1,11);p('#53616a',x+22,24,2,8);}
    p('#273b45',0,29,128,3); p('#8d9490',43,11,14,1);
  }],
  flood: ['#536f72', (p) => {
    for (const x of [10,49,91]) {
      p('#3a5559',x,9,2,20); p('#728283',x+2,10,1,18);
      p('#788789',x-3,13,2,2); p('#738181',x-3,23,2,2);
    }
    p('#384f55',0,24,128,8); p('#65817c',0,24,128,2);
    p('#778f85',24,23,29,1); p('#536f6f',79,26,20,2);
  }],
  street: ['#926e57', (p) => {
    for (const [y,offset] of [[9,3],[16,20],[24,7]]) {
      p('#5c5046',0,y,128,2);
      for (let x=offset; x<128; x+=32) {
        p('#635246',x,y+2,2,6); p('#aa8366',x+3,y+2,16,1);
      }
    }
    p('#776757',63,17,27,6); p('#807264',71,23,14,3);
  }],
  live: ['#675461', (p) => {
    for (let x=0; x<128; x+=16) {
      p('#4b414e',x,8,3,20); p('#796473',x+4,9,2,18);
      for(let y=13; y<23; y+=4) p('#584a57',x+9,y,3,1);
    }
    p('#3c3940',0,26,128,6); p('#957e66',0,26,128,2);
  }],
  office: ['#959786', (p) => {
    p('#68756c',0,21,128,2); p('#606a63',0,23,128,9);
    for (const x of [18,78]) {
      p('#777e73',x,9,1,12); p('#adb09c',x+1,9,1,12);
    }
    p('#535b56',0,29,128,3); p('#7c7769',48,23,9,2);
  }],
  tower: ['#516173', (p) => {
    p('#34424d',0,10,128,3); p('#879295',0,10,128,1);
    for(let x=0; x<128; x+=32) {
      for(let n=0; n<8; n++) {
        p('#35434f',x+2*n,13+n*2,4,3);
        p('#899297',x+2*n,12+n*2,3,2);
        p('#778790',x+28-2*n,12+n*2,3,2);
      }
    }
    p('#384651',0,28,128,4); p('#91999a',0,28,128,1);
  }],
  garden: ['#547568', (p) => {
    for(let x=0; x<128; x+=32) {
      p('#76948b',x+2,10,28,2); p('#66867e',x+4,12,24,9);
      for(let n=0;n<5;n++) p('#8da99c',x+16-2*n,12+n,5,1);
      p('#3f554b',x,8,3,22); p('#919a80',x+1,8,1,20);
    }
    p('#3f5146',0,24,128,8); p('#8b9479',0,24,128,2);
  }],
  archive: ['#75716a', (p) => {
    for(const x of [6,70]) {
      p('#494a48',x,9,2,22); p('#989385',x+2,9,1,21);
      p('#484b49',x+9,13,23,9);
      for(const y of [14,17,20]) p('#8a897b',x+11,y,19,1);
      p('#b2a688',x+40,15,10,4); p('#786e5e',x+41,17,6,1);
    }
    p('#555551',0,27,128,5);
  }],
  mirror: ['#786776', (p) => {
    for(let x=0;x<128;x+=32) {
      p('#493e4c',x,10,2,20); p('#a08b93',x+2,11,1,17);
      p('#615260',x+5,14,23,12); p('#897482',x+6,15,21,10);
    }
    p('#50434e',0,27,128,5); p('#aa9179',0,27,128,1);
  }],
  rail: ['#726348', (p) => {
    p('#5c7649',0,8,128,8);
    for (let x=0;x<128;x+=8) {
      const drop=[2,5,0,3,6,1,4,2][(x/8)%8];
      p('#698253',x,13,8,drop+2); p('#846d4e',x+2,22+drop%3,4,3);
      p('#5c5140',x+4,27-drop,3,3);
    }
    for (let x=0;x<128;x+=32) p('#5d5640',x,16,1,15);
  }],
  'fan-mail': ['#94775e', (p) => {
    p('#6a5144',0,19,128,13);
    for (let x=0; x<128; x+=12) {
      p('#4e3f39',x,22,1,9); p('#80634e',x+1,22,1,8);
    }
    p('#674940',0,16,128,5); p('#a26354',0,16,128,3);
    for (const x of [11,83]) {
      p('#69584c',x,9,15,5); p('#c1ae8d',x+1,9,13,4);
      p('#897863',x+3,11,7,1);
    }
  }],
};

function createEndingWallArt(sprite, planes) {
  const strips = new Map(), tiles = new WeakMap();
  return function endingWallTile(id, base, mask, x) {
    const phase = x % 4;
    const key = id + phase;
    if (!tiles.has(base)) tiles.set(base, new Map());
    const variants = tiles.get(base);
    if (variants.has(key)) return variants.get(key);
    if (!strips.has(id)) {
      const [face, draw] = endingWallMaterials[id];
      const strip = sprite(128,32,ctx => {
        const p = (color,x,y,w,h) => { ctx.fillStyle=color; ctx.fillRect(x,y,w,h); };
        p(face,0,0,128,32);
        draw(p);
      });
      strips.set(id,strip.getContext('2d').getImageData(0,0,128,32).data);
    }
    const pattern = strips.get(id), front = planes[String(mask)];
    const tile = sprite(32,32,ctx => {
      ctx.drawImage(base,0,0);
      const image = ctx.getImageData(0,0,32,32), pixels=image.data;
      for(let i=0;i<1024;i++) {
        const at=i*4, row=i>>5;
        if (!pixels[at+3]) continue;
        if (front[i]==='1') {
          const sample=(row*128 + phase*32 + i%32)*4;
          const relief=(pixels[at+1]-(row>20?69:row===20?98:85))*.65;
          for(let c=0;c<3;c++) pixels[at+c]=pattern[sample+c]+relief;
        } else if (id==='fubuki-er') {
          // The atlas puts side walls and corner returns on the cap plane. Carry
          // the ward's enamel through that plane while retaining its moulded rim.
          const relief = pixels[at+1] - 26;
          pixels[at]   = 64 + relief * 1.48;
          pixels[at+1] = 84 + relief * 1.35;
          pixels[at+2] = 80 + relief * 1.28;
        } else {
          // Tint exposed cap edges (including vertical returns), keeping the atlas shading.
          const tint=pixels[at+1]>45 ? .29 : .065;
          for(let c=0;c<3;c++) pixels[at+c]+=tint*(pattern[c]-80);
        }
      }
      ctx.putImageData(image,0,0);
    });
    variants.set(key,tile);
    return tile;
  };
}
