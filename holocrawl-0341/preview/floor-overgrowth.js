// Transparent 32px floor details. Coordinate hashing keeps wear stable through redraws and zoom.
const FloorOvergrowth = (() => {
  const materials = {
    stone:  {cut: ['#292d2ce0', '#917e6799'], green: ['#414c35', '#637549', '#899266']},
    tile:   {cut: ['#232b30e8', '#a2a59a99'], green: ['#3a4940', '#62775a', '#91a57d']},
    wood:   {cut: ['#382a24e8', '#b09770b8'], green: ['#4b5036', '#727b4c', '#9da06b']},
    metal:  {cut: ['#242d30ed', '#aba99aaf'], green: ['#3b4840', '#647559', '#8f9b72']},
    carpet: {cut: ['#292630de', '#a8948194'], green: ['#45483a', '#68734e', '#939b6e']},
    earth:  {cut: ['#343629c9', '#9b896791'], green: ['#435631', '#708146', '#a4ab64']},
    sand:   {cut: ['#766448bb', '#d3bd90b0'], green: ['#586343', '#85935c', '#adb47a']},
    water:  {cut: ['#153f4aa8', '#79a7a68c'], green: ['#305754', '#528577', '#85aa88']},
    deep:   {cut: ['#10323ba0', '#538a9394'], green: ['#31504b', '#58796a', '#83937c']},
  };
  // Each drawing starts at the root of the plant. Positive y points down the screen.
  function damage(material, shape, put) {
    const [dark, light] = materials[material].cut;
    const d = (x,y,w,h=1) => put(dark,x,y,w,h);
    const l = (x,y,w,h=1) => put(light,x,y,w,h);
    const {reach, fissure} = shape;
    switch (material) {
      case 'wood':
        d(-reach,0,reach+7); d(4,-1,5); l(0,1,6);
        d(-reach+2,1,4); l(-reach-2,2,4); d(7,-2,3); break;
      case 'metal':
        d(-6,0,9,2); d(2,-2,2,3); d(4,-2,reach); l(-5,2,6);
        l(4,-3,reach-2); d(6,3,2); break;
      case 'carpet':
        d(-4,-1,9,3); d(-6,0,2); d(3,-2,4);
        for (let i=0;i<reach;i+=2) l(-5+i,2+(i%3),2);
        l(6,-3,3); l(8,-2,1); break;
      case 'water': case 'deep':
        d(-5,1,9); l(-7,2,4); l(4,0,reach-2); d(7,-1,3); break;
      case 'earth': case 'sand':
        d(-5,0,8,2); l(-5,2,3); d(4,-2,3); l(6,-1,2);
        d(-reach,3,2); l(2,4,2); break;
      default:
        if (fissure==='corner') {
          // A loose corner casts a short shadow across the joint.
          d(-5,-2,7,2); d(-3,0,9,2); d(3,2,4); d(6,3,4);
          l(-5,-3,6); l(2,-1,3); d(-7,1,3); l(-8,3,2); break;
        }
        if (fissure==='chip') {
          // A small chip exposes soil between two intact slabs.
          d(-4,-2,6,2); d(-5,0,10,2); d(-2,2,5); l(-5,2,3);
          d(5,-2,2); l(5,-3,2); l(7,3,2); break;
        }
        d(-3,0,6,2); d(2,-1,3); d(4,-3,2,2); d(6,-4,reach-2); l(4,-1,2);
        d(-5,2,3); l(-3,2,4); d(-7,3,3);
        if (material==='tile') { d(-7,4,1,3); l(-6,5,1,2); }
        else { d(-9,4,3); l(-9,5,2); }
        if (fissure==='fork') { d(2,2,1,3); d(3,5,3); l(4,6,2); }
    }
  }
  // Roots anchor the blades to the damaged surface. In deep water the same slot
  // uses a floating silhouette, with the longer leaves trailing across the surface.
  const shapes = [
    {x:13, y:19, root:3, reach:5, fissure:'line',
      blades:['....h..','....m..','h..mm..','.m.m.h.','.mdmdm.','..ddd..'],
      floating:['..hm.....','..dm..hm.','.....dd..']},
    {x:18, y:13, root:3, reach:8, fissure:'corner',
      blades:['......h..','.....hm..','h....m..h','.m..mm.hm','..mdm.mm.','...ddmd..','....dd...'],
      floating:['.hm......','..dm..hh.','......md.']},
    {x:12, y:14, root:3, reach:4, fissure:'chip',
      blades:['......hh.','.....hmm.','..hh.md..','...mmd...','....dd...'],
      floating:['..hhh..','..mmd..','....dh.']},
    {x:17, y:21, root:3, reach:6, fissure:'fork',
      blades:['...h.....','...mh....','h..mm..h.','.mdmd.hm.','..mddmm..','...ddd...'],
      floating:['..hm...hh','..dm...md','.....h...']},
    // Low runner with a small second shoot.
    {x:14, y:17, root:5, reach:7, fissure:'corner',
      blades:['..h.......h','..mh.....hm','hh.md...md.','.mmd.h.dm..','...dmdmd..h','....ddddmm.'],
      floating:['hh........h','mmd.....hm.','..dmm..md..','.....dd....']},
    // Two broad leaves curling out in opposite directions.
    {x:18, y:21, root:5, reach:4, fissure:'chip',
      blades:['.......hhh','......hmmm','......mmd.','.hh..md...','hmmm.md...','.mmmdm....','...mdd....','....dd....'],
      floating:['.hh...hhh','hmmm.hmmm','.mdm.mmd.','...ddd...']},
    // A spear-like blade above two shorter side shoots.
    {x:14, y:21, root:5, reach:5, fissure:'line',
      blades:['......h','......h','.....hm','.....hm','.....mm','.....mm','..h..mm','..mh.md..h','...m.md.hm','...mdmd.m','....mddmd','....mddd','.....dd'],
      floating:['..........hh','........hmm.','.....hhmd...','..hhmd......','.mmd........']},
    // Long bent leaf. The tip turns downward on the far side of the stem.
    {x:13, y:20, root:4, reach:7, fissure:'fork',
      blades:['........hhh','......hhmmmh','.....hmm...m','.....mm....m','....hm.....d','....mm','....md','.h..md','.mh.md..hh','..m.md.hm.','..mdmdmd..','...mddd...','....dd....'],
      floating:['.......hhhh..','.....hmdd.mmh','...hmd.....md','.hmd.........','.dd..........']},
    // A pair of seed heads and one broken stalk.
    {x:15, y:22, root:5, reach:6, fissure:'chip',
      blades:['...h','..hhm','..hmm','...md','...m.....h','...m....hhm','...m....hmm','....m...md','....m...m','....m..m','..h.m..m','..m.md.m','...mmdmd','....mdd','.....dd'],
      floating:['..hh......hh.','.hmmd....hmmd','...md...mm...','....md.md....','.....dd......']},
    // A windblown fan with gaps between the blades at native resolution.
    {x:16, y:20, root:6, reach:8, fissure:'corner',
      blades:['.........hh','........hm','.......hm.....h','.......mm....hm','......hm....hm','..h...mm...hm','...m..md...mm','.h.mm.md..mm','..m.mdmd.hm','...m.mddmd','....mdddd','.....ddd'],
      floating:['...........hhh','.......hh.hmm.','......hm.md...','..hh.mdmd.....','...mddd.......']},
  ];
  const sprites = new Map();
  function sprite(material, variant, mirror=false) {
    const id = material+':'+variant+':'+mirror;
    if (sprites.has(id)) return sprites.get(id);
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const shape = shapes[variant];
    const {x:cx, y:cy} = shape;
    function put(color,x,y,w,h) {
      ctx.fillStyle=color; ctx.fillRect(mirror ? 32-cx-x-w : cx+x,cy+y,w,h);
    }
    damage(material,shape,put);
    const pattern = material==='deep' ? shape.floating : shape.blades;
    const [d,m,h] = materials[material].green;
    const ink = {d,m,h};
    pattern.forEach((row,y) => [...row].forEach((ch,x) => {
      if (ink[ch]) put(ink[ch],x-shape.root,y-pattern.length+1,1,1);
    }));
    sprites.set(id,canvas);
    return canvas;
  }
  let lastSeed, salt;
  function hash(x,y) {
    let n = salt ^ Math.imul(x,0x85ebca6b) ^ Math.imul(y,0xc2b2ae35);
    n = Math.imul(n ^ n>>>16,0x7feb352d);
    n = Math.imul(n ^ n>>>15,0x846ca68b);
    return (n ^ n>>>16)>>>0;
  }
  function draw(ctx,material,seed,x,y,px=x*32,py=y*32,size=32) {
    if (seed!==lastSeed || salt===undefined) {
      salt=2166136261;
      for (const c of String(seed)) salt=Math.imul(salt^c.charCodeAt(0),16777619);
      lastSeed=seed;
    }
    const n=hash(x,y);
    // Select sparse local minima so adjacent squares never both grow a tuft.
    if (n>=0x12000000 || n>=hash(x-1,y) || n>=hash(x+1,y) || n>=hash(x,y-1) || n>=hash(x,y+1)) return;
    const variant = (n >>> 1) % shapes.length;
    ctx.drawImage(sprite(material,variant,Boolean(n&1)),px,py,size,size);
  }
  // Fixed rooms share the same cell mask. Rugs sit on top of the room's primary floor.
  function room(ctx,map,seed,interior, rug=map.rug || map.runner) {
    for(let y=0;y<map.h;y++) for(let x=0;x<map.w;x++) {
      const i=y*map.w+x;
      if(!map.cells[i]) continue;
      let kind=map.inner && !map.inner[i] ? 'stone' : interior;
      if(rug && x>=rug.x && x<rug.x+rug.w && y>=rug.y && y<rug.y+rug.h) kind='carpet';
      draw(ctx,kind,seed,x,y);
    }
  }
  return {draw,sprite,room};
})();
