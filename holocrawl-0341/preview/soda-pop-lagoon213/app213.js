(async function () {
  const map = LagoonMap213, art = LagoonArt213;
  const get = id => document.getElementById(id);
  const canvas = get('coast'), context = canvas.getContext('2d');
  const tile = 32;
  canvas.width = map.width*tile;
  canvas.height = map.height*tile;
  context.imageSmoothingEnabled = false;

  async function load(url) {
    const image = new Image();
    image.src = url;
    await image.decode();
    return image;
  }
  const [sand,rocks,shallow,deep,up,down] = await Promise.all([
    Promise.all(Array.from({length:8},(_,i)=>load('assets/sand'+(i+1)+'.png'))),
    Promise.all(Array.from({length:4},(_,i)=>load('assets/shoals_wall'+(i+1)+'.png'))),
    load('../native-water02/assets/crawl-water/shoals_shallow_water0.png'),
    load('../native-water02/assets/crawl-water/shoals_deep_water0.png'),
    load('assets/shoals_stairs_up.png'),
    load('assets/shoals_stairs_down.png')
  ]);
  const maps = [map.generate(false),map.generate(true)];
  let high = false;
  let position = [...map.entry];
  const terrain = () => maps[Number(high)];
  const board = document.createElement('canvas');
  board.width = canvas.width;
  board.height = canvas.height;
  const ground = board.getContext('2d');
  ground.imageSmoothingEnabled = false;

  function shore(tilemap,x,y) {
    const px = x*tile, py = y*tile;
    const isSand = (tx,ty) => tilemap[ty]?.[tx] === 'sand';
    for (const [dx,dy] of map.steps) {
      if (!isSand(x+dx,y+dy)) continue;
      if (dx) {
        art.fill(ground,'#b1c6a8',px+(dx<0?0:30),py+4,2,24);
        art.fill(ground,'#82afa4',px+(dx<0?3:28),py+10,1,11);
      } else {
        art.fill(ground,'#b1c6a8',px+4,py+(dy<0?0:30),24,2);
        art.fill(ground,'#82afa4',px+10,py+(dy<0?3:28),11,1);
      }
    }
  }
  function drawGround() {
    const tilemap = terrain();
    tilemap.forEach((row,y)=>row.forEach((type,x)=>{
      const px=x*tile, py=y*tile, variant=map.hash(x,y);
      if (type === 'deck' || type === 'fixture') {
        art.deck(ground,px,py,(x>=23 && y<=8) || (y===12 && x>=6 && x<=8),variant);
        return;
      }
      if (type === 'sand' || type === 'rock') {
        ground.drawImage(sand[variant%sand.length],px,py,tile,tile);
        if (type === 'rock') ground.drawImage(rocks[variant%rocks.length],px,py,tile,tile);
        return;
      }
      ground.save();
      ground.translate(px+16,py+16);
      ground.scale(variant&1?-1:1,variant&2?-1:1);
      ground.drawImage(type==='deep'?deep:shallow,-16,-16,tile,tile);
      ground.restore();
      if (type === 'shallow') shore(tilemap,x,y);
    }));
    for (const point of map.landmarks) art.landmark(ground,point);
    ground.drawImage(up,map.entry[0]*tile,map.entry[1]*tile,tile,tile);
    ground.drawImage(down,map.exit[0]*tile,map.exit[1]*tile,tile,tile);
  }
  function redraw(message='') {
    context.drawImage(board,0,0);
    art.player(context,position[0]*tile,position[1]*tile);
    if (get('labels').checked) {
      context.font = 'bold 16px system-ui';
      context.textAlign = 'center';
      for (const point of map.landmarks) {
        const x=(point.x+point.w/2)*tile, y=point.y*tile-21;
        const width=Math.ceil(context.measureText(point.name).width)+16;
        art.fill(context,'#1b3037',x-width/2,y,width,21);
        context.fillStyle='#e0e9d9';
        context.fillText(point.name,x,y+16);
      }
    }
    get('tide').textContent = high ? '썰물로 전환' : '밀물로 전환';
    get('status').textContent = (high?'밀물':'썰물') + (message?' · '+message:'');
  }
  get('tide').onclick = () => {
    if (!map.walkable(maps[Number(!high)],...position)) {
      redraw('지금 발밑이 잠겨요. 다른 칸으로 이동해 주세요.');
      return;
    }
    high = !high;
    drawGround();
    redraw();
  };
  get('reset').onclick = () => {
    position = [...map.entry];
    redraw('입구');
    canvas.focus();
  };
  get('labels').onchange = () => redraw();
  canvas.addEventListener('keydown',event=>{
    const direction = ['ArrowUp','ArrowRight','ArrowDown','ArrowLeft'].indexOf(event.key);
    if (direction < 0) return;
    event.preventDefault();
    const [dx,dy] = map.steps[direction];
    const next = [position[0]+dx,position[1]+dy];
    if (!map.walkable(terrain(),...next)) {
      redraw(terrain()[next[1]]?.[next[0]]==='deep'?'깊은 물은 건널 수 없어요.':'막힌 칸');
      return;
    }
    position = next;
    const atExit = next.every((n,i)=>n===map.exit[i]);
    redraw(atExit?'다음 층 계단에 도착했어요.':terrain()[next[1]][next[0]]==='shallow'?'얕은 물':'');
  });
  drawGround();
  redraw('입구');
  get('tide').disabled = get('reset').disabled = false;
})().catch(error=>{
  console.error(error);
  document.getElementById('status').textContent = '지도를 불러오지 못했어요.';
});
