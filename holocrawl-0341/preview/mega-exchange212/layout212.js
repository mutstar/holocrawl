(function () {
  const w = 25, h = 19, offset = 3;
  const dirs = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
  const index = (x,y) => y * w + x;
  const at = item => ({...item,x:item.x + offset,y:item.y + offset});

  function generate(mode) {
    const cells = Array(w * h).fill(1);
    const inner = cells.map(() => false), building = inner.slice();
    for (const [x,y,width,height] of [[4,1,11,3],[1,5,17,5],[3,10,13,1]]) {
      for (let dy = 0; dy < height; dy++) for (let dx = 0; dx < width; dx++) {
        inner[index(x + offset + dx,y + offset + dy)] = true;
      }
    }
    if (mode === 'attached') cells.fill(0,0,(offset + 1) * w);
    for (let i = 0; i < inner.length; i++) {
      if (!inner[i]) continue;
      cells[i] = 1;
      for (const [dx,dy] of dirs) {
        const neighbor = index(i % w + dx,Math.floor(i / w) + dy);
        if (!inner[neighbor]) {
          cells[neighbor] = 0;
          building[neighbor] = true;
        }
      }
    }
    const entry = at({x:8,y:11,w:2,h:1});
    const stockroom = at({x:8,y:4,w:2,h:1});
    const doorway = [index(entry.x,entry.y),index(entry.x+1,entry.y)];
    for (const i of [...doorway,index(stockroom.x,stockroom.y),index(stockroom.x+1,stockroom.y)]) cells[i] = 1;
    const props = [
      {id:'vault',label:'대형 금고',x:8,y:1,w:3,h:2},
      {id:'coinCabinet',label:'코인 선반',x:5,y:1,w:2,h:2},
      {id:'coinCabinet',label:'예비 코인 선반',x:12,y:1,w:2,h:2},
      {id:'teller',label:'코인 교환 창구',x:3,y:6,w:4,h:1},
      {id:'teller',label:'경품 수령 창구',x:12,y:6,w:4,h:1,prizes:true},
      {id:'sign',label:'교환 안내판',x:2,y:8,w:1,h:1},
      {id:'bench',label:'대기 벤치',x:13,y:9,w:3,h:1},
      {id:'rail',label:'대기줄 난간',x:4,y:8,w:3,h:1}
    ].map(at);
    const open = cells.slice();
    for (const prop of props) for (let dy = 0; dy < prop.h; dy++) for (let dx = 0; dx < prop.w; dx++) {
      open[index(prop.x+dx,prop.y+dy)] = 0;
    }
    return {w,h,cells,inner,building,props,entry,stockroom,doorway,open,
      runner:at({x:8,y:5,w:2,h:6}),start:{x:entry.x,y:entry.y+2}};
  }
  window.ExchangeLayout212 = {generate,dirs,index};
})();
