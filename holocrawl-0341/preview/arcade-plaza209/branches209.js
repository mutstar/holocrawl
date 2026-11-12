(function () {
  'use strict';
  const doors=[
    {id:'coaster',name:'롤러코스터',color:'#b49acb',x:6,y:0,w:3,h:2,number:1},
    {id:'bumper',name:'범퍼카 차고',color:'#d4ac70',x:13,y:0,w:3,h:2,number:2},
    {id:'maze',name:'네온 미로',color:'#7cc6be',x:20,y:0,w:3,h:2,number:3}
  ];
  const directions={up:[0,-1],right:[1,0],down:[0,1],left:[-1,0]};
  const wallNeighbors=[...Object.values(directions),[-1,-1],[1,-1],[-1,1],[1,1]];
  const backgrounds=new Map();
  const cell=(m,x,y)=>y*m.w+x;

  function room(w,h) {
    const floor=Array(w*h).fill(false);
    for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++){
      if(x+y<4||w-1-x+y<4||x+h-1-y<4||w-1-x+h-1-y<4)continue;
      floor[y*w+x]=true;
    }
    const entry={x:Math.floor(w/2)-1,y:h-1,w:3,h:1};
    for(let x=entry.x;x<entry.x+entry.w;x++)floor[entry.y*w+x]=true;
    return {w,h,floor,open:floor.slice(),props:[],entry,start:{x:entry.x+1,y:h-2}};
  }
  function block(m,p){
    m.props.push(p);
    for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)m.open[cell(m,x,y)]=false;
  }
  function coasterMap() {
    const m=room(35,22);
    Object.assign(m,{id:'coaster',title:'롤러코스터 · 별도 층',description:'매표 부스와 짐 보관·휴게 공간, 지그재그 대기줄과 탑승장, 정비 구역을 둘러볼 수 있습니다. 아래 문으로 나가면 메가서킷 레일 아치 앞으로 돌아갑니다.'});
    for(const p of [
      {id:'coaster-long',x:4,y:3,w:27,h:9},
      {id:'platform',x:18,y:12,w:6,h:2},
      {id:'console',x:25,y:12,w:1,h:2},
      {id:'baggage-lockers',x:3,y:13,w:5,h:2},
      {id:'waiting-bench',x:3,y:17,w:3,h:1},
      {id:'waiting-bench',x:3,y:19,w:3,h:1},
      {id:'waste-bin',x:7,y:19,w:1,h:1},
      {id:'ticket-booth',x:10,y:17,w:3,h:3},
      {id:'queue-rail',x:18,y:15,w:8,h:1},
      {id:'queue-rail',x:16,y:17,w:8,h:1},
      {id:'queue-side',x:15,y:14,w:1,h:5},
      {id:'queue-side',x:26,y:14,w:1,h:5},
      {id:'coaster-workbench',x:28,y:13,w:4,h:2},
      {id:'spare-wheels',x:29,y:16,w:2,h:2},
      {id:'spare-track',x:28,y:19,w:4,h:1}
    ])block(m,p);
    return m;
  }
  function bumperMap() {
    const m=room(29,19);
    Object.assign(m,{id:'bumper',title:'범퍼카 차고 · 별도 층',description:'양옆 충전 주차칸과 중앙 점검 구역, 뒤쪽 공구·타이어 선반, 입구의 접수·대기 공간을 둘러보세요. 아래 문으로 메가서킷에 돌아갑니다.'});
    for(const [x,y,color] of [[5,5,'#ba7d94'],[13,7,'#80b7b0'],[21,5,'#b69c67'],[5,9,'#9384b9'],[21,9,'#749aae']])block(m,{id:'car',x,y,w:2,h:2,color});
    for(const y of [5,9]){
      block(m,{id:'garage-charger',x:2,y,w:2,h:2,side:'right'});
      block(m,{id:'garage-charger',x:25,y,w:2,h:2,side:'left'});
    }
    block(m,{id:'booth',x:12,y:1,w:5,h:2});
    for(const p of [
      {id:'garage-workbench',x:3,y:1,w:4,h:2},
      {id:'tyre-shelf',x:20,y:1,w:3,h:2},
      {id:'battery-rack',x:24,y:1,w:2,h:3},
      {id:'tool-trolley',x:9,y:4,w:2,h:2},
      {id:'floor-jack',x:9,y:8,w:1,h:1},
      {id:'safety-cone',x:10,y:12,w:1,h:1},
      {id:'safety-cone',x:18,y:12,w:1,h:1},
      {id:'garage-seats',x:3,y:14,w:3,h:1},
      {id:'garage-seats',x:3,y:16,w:3,h:1},
      {id:'waiting-table',x:7,y:15,w:2,h:1},
      {id:'drinks-machine',x:9,y:14,w:2,h:3},
      {id:'garage-reception',x:18,y:15,w:4,h:2},
      {id:'garage-seats',x:24,y:16,w:3,h:1},
      {id:'fire-cabinet',x:26,y:14,w:1,h:2}
    ])block(m,p);
    return m;
  }
  function mazeMap() {
    const m=room(29,21);
    Object.assign(m,{id:'maze',title:'네온 미로 · 별도 층',description:'청록·보라 네온 테두리와 반사광이 비치는 유리벽 미로. 오른쪽 위 별빛 표식을 찾아보고, 아래 출구로 돌아가세요.'});
    // No isolated maintenance strip behind the sealed north wall.
    for(let x=0;x<m.w;x++)m.floor[cell(m,x,1)]=false;
    for(let y=2;y<=16;y++)for(let x=2;x<=26;x++)m.floor[cell(m,x,y)]=false;
    let seed=20905;
    const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
    const stack=[{x:13,y:15}],seen=new Set(['13,15']);
    m.floor[cell(m,13,15)]=true;
    while(stack.length){
      const p=stack[stack.length-1];
      const options=Object.values(directions).map(([dx,dy])=>({x:p.x+dx*2,y:p.y+dy*2}))
        .filter(n=>n.x>=3&&n.x<=25&&n.y>=3&&n.y<=15&&!seen.has(n.x+','+n.y));
      if(!options.length){stack.pop();continue;}
      const n=options[Math.floor(random()*options.length)];
      seen.add(n.x+','+n.y);m.floor[cell(m,n.x,n.y)]=true;
      m.floor[cell(m,(n.x+p.x)/2,(n.y+p.y)/2)]=true;stack.push(n);
    }
    // A few cross-links give routes back to the entrance without dead-end overload.
    for(const [x,y] of [[6,5],[12,9],[18,13],[22,7]])m.floor[cell(m,x,y)]=true;
    m.floor[cell(m,13,16)]=true;
    m.open=m.floor.slice();m.beacon={x:25,y:3};
    return m;
  }
  const maps={coaster:coasterMap(),bumper:bumperMap(),maze:mazeMap()};
  function terrain(id,x,y){
    const m=maps[id];
    if(!m||x<0||y<0||x>=m.w||y>=m.h||!m.open[cell(m,x,y)])return 'wall';
    const e=m.entry;
    return x>=e.x&&x<e.x+e.w&&y===e.y?'return':'floor';
  }
  const reset=id=>({pos:{...maps[id].start},turn:0,visitedBeacon:false,message:'아래 문으로 메가서킷에 돌아갈 수 있어요.'});
  function step(id,state,direction){
    const delta=directions[direction];if(!delta)return state;
    const pos={x:state.pos.x+delta[0],y:state.pos.y+delta[1]};
    if(terrain(id,pos.x,pos.y)==='wall')return {...state,message:'벽이나 시설이 있는 칸이에요.'};
    const beacon=maps[id].beacon;
    const reached=Boolean(beacon&&pos.x===beacon.x&&pos.y===beacon.y);
    return {...state,pos,turn:state.turn+1,visitedBeacon:state.visitedBeacon||reached,message:reached?'별빛 표식을 찾았어요! 아래 출구로 돌아가세요.':''};
  }
  function gate(q,d,compact=false){
    if(!compact){themedGate(q,d);return;}
    const x=d.x*32,y=d.y*32,w=d.w*32,h=compact?32:64;
    const f=(c,a,b,ww,hh)=>{q.fillStyle=c;q.fillRect(x+a,y+b,ww,hh);};
    f('#242838',0,0,w,h);f('#647186',1,1,w-2,h-2);f('#a0a6b7',1,1,w-2,2);
    f('#303749',6,7,w-12,h-11);f(d.color,5,5,w-10,3);
    const top=compact?10:24,leaf=(w-20)/2;
    for(const px of [9,11+leaf]){
      f('#536779',px,top,leaf,h-top-4);f('#84999f',px,top,leaf,2);
      f('#253c4a',px+3,top+5,leaf-6,h-top-13);f(d.color,px+4,top+5,leaf-8,2);
    }
    f('#c9bd92',w/2-5,h-15,2,6);f('#c9bd92',w/2+3,h-15,2,6);
    f('#b0b3b1',0,h-3,w,2);
  }
  function themedGate(q,d){
    const x=d.x*32,y=d.y*32;
    const f=(c,a,b,w,h)=>{q.fillStyle=c;q.fillRect(x+a,y+b,w,h);};
    // Draw in native pixels: all three entrances occupy the same 3×2 tiles.
    const line=(c,points,size=2)=>{
      for(let i=1;i<points.length;i++){
        let [a,b]=points[i-1];const [endA,endB]=points[i];
        const dx=Math.abs(endA-a),dy=-Math.abs(endB-b),sx=a<endA?1:-1,sy=b<endB?1:-1;let error=dx+dy;
        while(true){f(c,a,b,size,size);if(a===endA&&b===endB)break;const twice=2*error;if(twice>=dy){error+=dy;a+=sx;}if(twice<=dx){error+=dx;b+=sy;}}
      }
    };
    if(d.id==='coaster'){
      // A miniature coaster rail forms the crown, supported by steel columns.
      f('#252938',8,24,80,38);f('#5d4e78',16,23,64,36);
      f('#2c3044',20,27,56,31);
      for(const a of [24,34,44,54,64]){f('#75658d',a,28,4,29);f('#ad98ba',a,28,1,27);}
      f('#9983ae',19,34,58,3);f('#9983ae',19,49,58,3);f('#282e3c',47,26,2,33);
      for(const a of [9,79]){f('#28313e',a,18,8,44);f('#87959e',a+1,20,5,39);f('#bac2bb',a+1,20,1,37);f('#4a5868',a+5,23,2,36);}
      const rail=[[5,20],[10,12],[21,5],[35,2],[48,4],[61,11],[73,17],[87,17]];
      line('#242735',rail,5);
      for(const [a,b]of rail){f('#b3a2bf',a,b+1,2,8);}
      line('#b7a0cb',rail);line('#78608f',rail.map(([a,b])=>[a,b+6]));
      // Small parked car silhouette identifies the ride without a sign.
      f('#31313f',47,5,16,8);f('#bf7f9f',49,5,13,5);f('#e0b5bf',50,5,10,1);
      f('#d7c59f',50,11,3,3);f('#d7c59f',59,11,3,3);
      f('#313440',6,60,84,4);f('#a4a4ad',8,60,80,2);
    }else if(d.id==='bumper'){
      // Industrial shutter, broad bumper rails, and a compact car emblem.
      f('#252c35',4,5,88,59);f('#797763',6,6,84,56);f('#b2a480',6,6,84,3);
      f('#383b3e',10,10,76,13);f('#252d36',15,23,66,37);
      f('#777a78',18,24,60,34);
      for(let b=25;b<57;b+=6){f('#a0a397',19,b,58,2);f('#4b565a',19,b+4,58,2);}
      f('#333e43',41,51,14,4);f('#c2b58d',43,51,10,2);
      for(const a of [8,81]){
        f('#343b40',a,24,7,34);
        for(let b=25;b<56;b+=8){f('#d2ae6b',a,b,3,4);f('#d2ae6b',a+3,b+3,3,4);}
        f('#98a6a4',a,57,7,3);
      }
      f('#b39767',36,14,24,6);f('#d6bc88',39,12,18,7);
      f('#293c43',42,11,12,4);f('#96b7b4',43,12,10,2);
      f('#242d34',34,19,28,3);f('#b2c2ba',34,19,28,1);
      f('#b6bcab',58,8,1,7);f('#8fb9a9',65,14,4,3);
      f('#26353b',4,60,88,4);f('#b0ad94',6,60,84,2);
    }else{
      // Faceted glass surround with two different maze paths across the leaves.
      f('#243341',8,15,80,47);f('#243341',16,7,64,8);f('#243341',26,3,44,4);
      line('#91c5c0',[[10,59],[10,16],[19,7],[28,5],[66,5],[76,9],[84,17],[84,59]],3);
      line('#486d82',[[16,59],[16,20],[25,13],[68,13],[78,22],[78,59]],3);
      f('#2e4c5c',21,21,54,38);f('#5a8d98',21,21,25,35);f('#527e8c',49,21,26,35);
      f('#263b4b',46,20,3,39);f('#82b6bc',22,22,23,2);f('#82b6bc',50,22,24,2);
      line('#b1d7cc',[[26,53],[26,30],[39,30],[39,39],[32,39],[32,48],[42,48]],2);
      line('#a4c8d3',[[69,53],[69,43],[56,43],[56,28],[69,28],[69,35],[62,35]],2);
      f('#bd95bf',10,29,3,9);f('#bd95bf',84,29,3,9);
      f('#cfddcc',42,49,2,5);f('#cfddcc',51,49,2,5);
      f('#344555',7,59,82,5);f('#96b7bb',9,60,78,2);
    }
  }
  function wall(q,m,x,y){
    const px=x*32,py=y*32;
    const f=(c,a,b,w,h)=>{q.fillStyle=c;q.fillRect(px+a,py+b,w,h);};
    const floor=(xx,yy)=>xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&m.floor[cell(m,xx,yy)];
    f(m.id==='maze'?'#303c50':'#343f50',0,0,32,32);
    if(floor(x,y-1))f('#7a8c99',0,0,32,3);
    if(floor(x-1,y))f('#738391',0,0,3,32);
    if(floor(x+1,y))f('#202b3a',29,0,3,32);
    if(floor(x,y+1)){
      f('#56697c',0,9,32,21);f('#95a6ad',0,8,32,3);f('#222b39',0,30,32,2);
      if(m.id==='maze'){f('#3b6370',4,14,24,11);f('#7cb6b4',4,14,24,2);f('#5b8190',5,17,2,6);}
      else {f('#3c4a5c',4,16,24,9);f('#758997',5,16,2,2);f('#758997',25,16,2,2);}
    }
  }
  function prop(q,p){
    const x=p.x*32,y=p.y*32,f=(c,a,b,w,h)=>{q.fillStyle=c;q.fillRect(x+a,y+b,w,h);};
    if(p.id==='car'){
      f('#212735',6,48,53,6);f('#1b2330',3,27,58,23);f('#202736',9,22,46,33);
      f('#52606b',6,29,52,17);f(p.color,8,27,48,16);f(p.color,12,24,40,23);
      f('#c0c7ba',12,27,38,2);f('#293542',20,22,25,13);f('#758b91',22,24,19,4);
      f('#172530',17,37,11,7);f('#99b5b2',19,38,7,2);f('#bb9b66',9,36,4,3);
      f('#a3b1b4',46,5,2,21);f('#34444c',48,5,2,21);f('#d6c48f',43,2,9,3);
    }else if(p.id==='charger'){
      f('#242d36',4,45,55,7);f('#4f606c',6,13,49,35);f('#9b967f',6,13,49,3);
      f('#223943',12,20,23,14);f('#89b9b2',15,23,15,5);f('#d2b177',41,24,6,6);
      f('#273740',48,36,11,3);f('#273740',56,36,3,16);
    }else if(p.id==='bench'){
      f('#27333a',3,26,58,5);f('#6e6b69',3,10,58,6);f('#a7a18b',3,10,58,2);
      f('#898170',3,21,58,5);f('#4a555c',7,16,3,14);f('#4a555c',54,16,3,14);
    }else if(p.id==='booth'){
      f('#26323e',2,5,156,56);f('#63727b',4,7,152,52);f('#a9b8b0',4,7,152,3);
      f('#314855',9,16,142,26);f('#5f8790',12,19,136,20);f('#a7c5bf',12,19,136,2);
      for(const a of [47,88,129])f('#9aa9aa',a,17,3,23);
      f('#d0ae73',7,44,146,4);f('#394957',7,48,146,10);
    }
  }
  function build(id){
    const m=maps[id],canvas=document.createElement('canvas');canvas.width=m.w*32;canvas.height=m.h*32;
    const q=canvas.getContext('2d');q.imageSmoothingEnabled=false;q.fillStyle='#1d2830';q.fillRect(0,0,canvas.width,canvas.height);
    for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){
      const i=cell(m,x,y),px=x*32,py=y*32;
      if(m.floor[i]){
        if(id==='bumper')q.drawImage(ArcadeFloor209.tile(x,y),px,py);
        else {q.fillStyle=id==='maze'?((x+y)%2?'#2c303f':'#303544'):((x+y)%2?'#414d59':'#45515d');q.fillRect(px,py,32,32);
          q.fillStyle=id==='maze'?'#393d50':'#53606a';q.fillRect(px+4+(x*5+y)%15,py+9+(x+y*7)%14,3,1);}
      }else if(id!=='maze'&&wallNeighbors.some(([dx,dy])=>x+dx>=0&&y+dy>=0&&x+dx<m.w&&y+dy<m.h&&m.floor[cell(m,x+dx,y+dy)]))wall(q,m,x,y);
    }
    if(id==='maze')MazeGlass209.draw(q,m);
    if(id==='bumper')BumperGarage209.ground(q,m);
    if(id==='coaster')CoasterProps209.ground(q);
    for(const p of m.props){
      if(p.id==='coaster-long')LongCoaster209.draw(q,p);
      else if(id==='coaster'&&CoasterProps209.has(p.id))CoasterProps209.draw(q,p);
      else if(id==='coaster')CoasterSprites206.draw(q,p);
      else if(id==='bumper'&&BumperGarage209.has(p.id))BumperGarage209.draw(q,p);
      else prop(q,p);
    }
    if(id==='maze'){
      const x=m.beacon.x*32,y=m.beacon.y*32;
      q.fillStyle='#586e7c';q.fillRect(x+6,y+22,20,5);q.fillStyle='#caabd8';q.fillRect(x+13,y+6,6,17);
      q.fillRect(x+8,y+11,16,7);q.fillStyle='#ece0cc';q.fillRect(x+14,y+11,4,7);
    }
    gate(q,{...m.entry,color:doors.find(d=>d.id===id).color},true);
    return canvas;
  }
  function draw(canvas,id,state){
    const m=maps[id];if(!backgrounds.has(id))backgrounds.set(id,build(id));
    if(canvas.width!==m.w*32)canvas.width=m.w*32;if(canvas.height!==m.h*32)canvas.height=m.h*32;
    canvas.style.width=m.w*32+'px';
    const q=canvas.getContext('2d');q.imageSmoothingEnabled=false;q.drawImage(backgrounds.get(id),0,0);
    const x=state.pos.x*32,y=state.pos.y*32;q.fillStyle='#1d2933';q.fillRect(x+6,y+24,20,5);
    q.fillStyle='#73b99d';q.fillRect(x+6,y+27,20,2);q.fillStyle='#c1e4d4';q.fillRect(x+11,y+10,10,14);
    q.fillStyle='#eff0d6';q.fillRect(x+13,y+7,6,6);q.fillStyle='#548d88';q.fillRect(x+13,y+16,6,5);
  }
  window.MegaBranch209={doors,maps,terrain,reset,step,draw,gate};
})();
