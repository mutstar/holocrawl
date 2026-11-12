(function () {
  'use strict';
  const width=29,height=21,tile=32,trackOffset=128;
  const left=272,right=656,centerY=272+trackOffset,start={x:9,y:17};
  const moves={up:[0,-1],right:[1,0],down:[0,1],left:[-1,0]};
  let background;
  function distance(px,py) {
    return Math.hypot(px-Math.max(left,Math.min(right,px)),py-centerY);
  }
  function terrain(x,y) {
    if(x<1||x>=width-1||y<1||y>=height-1)return 'wall';
    if(y===1&&MegaBranch209.doors.some(d=>x>=d.x&&x<d.x+d.w))return 'gate';
    if(x>=3&&x<=25&&y>=2&&y<=3)return 'approach';
    if(x===14&&y>=4&&y<=5)return 'approach';
    const radius=distance(x*tile+16,y*tile+16);
    return radius>=112&&radius<=196?'track':'grass';
  }
  const reset=()=>({pos:{...start},direction:'right',turn:0,sector:0,laps:0,
    message:'오른쪽으로 출발해 트랙을 한 바퀴 돌아보세요.'});
  function step(state,direction) {
    if(!moves[direction])return state;
    const [dx,dy]=moves[direction];
    const pos={x:state.pos.x+dx,y:state.pos.y+dy};
    if(!['track','approach','gate'].includes(terrain(pos.x,pos.y)))return {...state,message:'트랙이나 문 앞 통로로 이동하세요.'};
    let sector=state.sector,laps=state.laps,message='';
    // Ordered sectors prevent backing across the line from counting a lap.
    const onTrack=terrain(pos.x,pos.y)==='track';
    if(onTrack&&sector===0&&pos.x>=24)sector=1;
    else if(onTrack&&sector===1&&pos.y<=7)sector=2;
    else if(onTrack&&sector===2&&pos.x<=4)sector=3;
    if(onTrack&&sector===3&&state.pos.x===9&&pos.x===10&&pos.y>=16){
      laps++;sector=0;message=laps+'바퀴 완주! 계속 달릴 수 있어요.';
    }
    return {pos,direction,turn:state.turn+1,sector,laps,message};
  }
  // Continuous stripe spacing along the straights and both curved ends.
  function along(px,py,radius) {
    const straight=right-left;
    if(px>=left&&px<=right)return py<centerY?px-left:straight+Math.PI*radius+right-px;
    if(px>right)return straight+(Math.atan2(py-centerY,px-right)+Math.PI/2)*radius;
    let angle=Math.atan2(py-centerY,px-left);
    if(angle<Math.PI/2)angle+=Math.PI*2;
    return 2*straight+Math.PI*radius+(angle-Math.PI/2)*radius;
  }
  function buildBackground() {
    const canvas=document.createElement('canvas');
    canvas.width=width*tile;canvas.height=height*tile;
    const q=canvas.getContext('2d');
    const fill=(color,x,y,w,h)=>{q.fillStyle=color;q.fillRect(x,y,w,h);};
    // Native 2px steps retain the pixel-art look on the curved kerbs.
    for(let y=0;y<canvas.height;y+=2)for(let x=0;x<canvas.width;x+=2){
      const r=distance(x+1,y+1),grain=((x*13+y*7)^(x*y))>>>0;
      let color;
      if(r<100){
        color=Math.floor(y/32)%2?'#3e5448':'#42594b';
        if(grain%43===0)color='#516452';
      }else if(r<112||r>=196&&r<208){
        color=Math.floor(along(x,y,r<112?106:202)/16)%2?'#b8b6a5':'#9b555c';
        if(r<102||r>=206)color='#343c40';
      }else if(r<196){
        color=grain%23===0?'#424852':grain%19===0?'#343b46':'#3b424d';
        if(r<115||r>=193)color='#9caaa7';
        if(r>=153&&r<156&&along(x,y,154)%32<17)color='#98a6a2';
      }else color=grain%41===0?'#48564d':'#35463e';
      fill(color,x,y,2,2);
    }
    for(let y=0;y<height;y++)for(let x=0;x<width;x++){
      if(x!==0&&y!==0&&x!==width-1&&y!==height-1)continue;
      const px=x*tile,py=y*tile;
      fill('#242c35',px,py,32,32);fill('#3b4853',px+1,py+3,30,22);
      fill('#6e818a',px,py+2,32,2);fill('#505e6c',px+2,py+5,1,17);
      fill('#495b68',px,py+27,32,2);
    }
    q.save();q.translate(0,trackOffset);
    for(let row=0;row<14;row++)for(let col=0;col<2;col++){
      fill((row+col)%2?'#29313c':'#d3ceba',320+col*6,386+row*6,6,6);
    }
    for(const y of [394,442])for(let x=350+(y===442?16:0);x<486;x+=48){
      fill('#7b8788',x,y,22,1);fill('#7b8788',x,y+14,22,1);fill('#7b8788',x+21,y,1,15);
    }
    const arrow=(x,y,rotation)=>{
      q.save();q.translate(x,y);q.rotate(rotation);
      fill('#9ba9a4',-8,-2,14,4);
      for(let i=0;i<4;i++)fill('#9ba9a4',2+i*2,-8+i*2,2,16-i*4);
      q.restore();
    };
    arrow(574,410,0);arrow(794,272,-Math.PI/2);
    arrow(452,130,Math.PI);arrow(132,272,Math.PI/2);
    // Muted infield lettering is painted into the grass.
    const glyphs={M:['10001','11011','10101','10001','10001'],E:['11111','10000','11110','10000','11111'],G:['01111','10000','10111','10001','01111'],A:['01110','10001','11111','10001','10001'],C:['01111','10000','10000','10000','01111'],I:['11111','00100','00100','00100','11111'],R:['11110','10001','11110','10100','10010'],U:['10001','10001','10001','10001','01110'],T:['11111','00100','00100','00100','00100']};
    let dx=334;
    for(const letter of 'MEGA CIRCUIT'){
      if(letter!==' ')glyphs[letter].forEach((row,yy)=>[...row].forEach((pixel,xx)=>{
        if(pixel==='1')fill('#869b88',dx+xx*4,254+yy*4,4,4);
      }));
      dx+=24;
    }
    fill('#68867f',374,288,72,2);fill('#896e82',466,288,72,2);
    q.restore();
    // The doors share a separate north forecourt. A two-tile grass buffer
    // keeps its floor and labels outside the unchanged racing oval.
    fill('#303a4b',3*32,2*32,23*32,2*32);
    for(let y=2;y<=3;y++)for(let x=3;x<=25;x++){
      fill((x+y)%2?'#434c5c':'#3e4858',x*32+1,y*32+1,30,30);
      fill('#515c69',x*32+5,y*32+7,7,1);
    }
    fill('#7c8b97',3*32,4*32-3,23*32,3);
    fill('#7c8b97',3*32,2*32,2,2*32);fill('#7c8b97',26*32-2,2*32,2,2*32);
    // Only the short access path reaches the outer kerb, never the road itself.
    fill('#424d5c',14*32,4*32-3,32,2*32+3);
    fill('#89959b',14*32,4*32,2,2*32);fill('#89959b',15*32-2,4*32,2,2*32);
    for(const y of [4,5])fill('#657480',14*32+6,y*32+15,20,2);
    return canvas;
  }
  function draw(canvas,state) {
    if(!background)background=buildBackground();
    const q=canvas.getContext('2d');q.imageSmoothingEnabled=false;q.drawImage(background,0,0);
    for(const door of MegaBranch209.doors)MegaBranch209.gate(q,door);
    const x=state.pos.x*tile,y=state.pos.y*tile;
    q.fillStyle='#243438';q.fillRect(x+8,y+25,16,3);
    q.fillStyle='#72ad9a';q.fillRect(x+7,y+27,18,2);
    q.fillStyle='#b1e2d1';q.fillRect(x+11,y+11,10,13);
    q.fillStyle='#e0f3d9';q.fillRect(x+13,y+8,6,5);
    q.fillStyle='#438376';q.fillRect(x+13,y+16,6,5);
  }
  const portalAt=pos=>pos.y===1?MegaBranch209.doors.find(d=>pos.x>=d.x&&pos.x<d.x+d.w):undefined;
  window.MegaCircuit209={width,height,tile,terrain,reset,step,draw,portalAt};
})();
