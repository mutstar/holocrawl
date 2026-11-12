(function(){
  'use strict';
  function draw(q,m){
    const floor=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.floor[y*m.w+x];
    const adjacent=[[0,-1],[1,0],[0,1],[-1,0],[-1,-1],[1,-1],[1,1],[-1,1]];
    const pane=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&!floor(x,y)&&adjacent.some(([dx,dy])=>floor(x+dx,y+dy));
    const cells=[];
    for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++)if(pane(x,y))cells.push({x,y,n:!pane(x,y-1),e:!pane(x+1,y),s:!pane(x,y+1),w:!pane(x-1,y)});
    const r=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(x,y,w,h);};
    // Pixel-width reflected light, rendered after the floor so no side loses its glow.
    for(const t of cells){
      const x=t.x*32,y=t.y*32;
      if(t.n&&floor(t.x,t.y-1)){r('rgba(58,213,208,.10)',x,y-4,32,4);r('rgba(90,232,218,.15)',x,y-2,32,2);}
      if(t.w&&floor(t.x-1,t.y)){r('rgba(58,213,208,.10)',x-4,y,4,32);r('rgba(90,232,218,.15)',x-2,y,2,32);}
      if(t.s&&floor(t.x,t.y+1)){r('rgba(170,105,231,.12)',x,y+32,32,4);r('rgba(192,135,246,.18)',x,y+32,32,2);}
      if(t.e&&floor(t.x+1,t.y)){r('rgba(170,105,231,.12)',x+32,y,4,32);r('rgba(192,135,246,.18)',x+32,y,2,32);}
    }
    for(const t of cells){
      const x=t.x*32,y=t.y*32;
      const f=(c,dx,dy,w,h)=>r(c,x+dx,y+dy,w,h);
      // The floor's checker and joints remain visible through the tinted pane.
      f((t.x+t.y)%2?'#2c303f':'#303544',0,0,32,32);
      f('#454b5b',0,30,32,1);f('#424857',30,0,1,32);
      f('#596071',4+(t.x*5+t.y)%15,9+(t.x+t.y*7)%14,3,1);
      f('rgba(77,190,198,.24)',0,0,32,32);
      f('rgba(128,105,198,.16)',0,18,32,14);
      f('rgba(148,222,220,.10)',0,3,32,5);
      // Broad, sparse diagonal reflections read as glass, not little inset windows.
      if((t.x+2*t.y)%3===0){
        for(let k=0;k<13;k++)f('rgba(194,239,233,.25)',6+k,7+k,3,1);
        for(let k=0;k<7;k++)f('rgba(206,221,249,.12)',5+k,17+k,2,1);
      }else if((t.x+t.y)%3===1){
        for(let k=0;k<5;k++)f('rgba(164,223,227,.18)',18+k,7+k,2,1);
      }
      // Continuous outer rails: cyan on the lit sides, violet on the opposite sides.
      // Shared tile edges are deliberately left open so L/T joints stay connected.
      if(t.n){f('#243e49',0,0,32,1);f('#b5f4eb',0,1,32,1);f('#60d8d3',0,2,32,2);f('rgba(87,220,210,.24)',0,4,32,2);}
      if(t.w){f('#243e49',0,0,1,32);f('#b5f4eb',1,0,1,32);f('#60d8d3',2,0,2,32);f('rgba(87,220,210,.24)',4,0,2,32);}
      if(t.s){f('#503e6e',0,28,32,1);f('#aa7edb',0,29,32,2);f('#dec0fa',0,31,32,1);f('rgba(178,121,232,.20)',0,26,32,2);}
      if(t.e){f('#503e6e',28,0,1,32);f('#aa7edb',29,0,2,32);f('#dec0fa',31,0,1,32);f('rgba(178,121,232,.20)',26,0,2,32);}
      // Small metal clamps only at exposed corners, not a stone frame around every tile.
      for(const [corner,dx,dy]of [[t.n&&t.w,0,0],[t.n&&t.e,29,0],[t.s&&t.w,0,29],[t.s&&t.e,29,29]]){
        if(corner){f('#526776',dx,dy,3,3);f('#c5d5d3',dx+1,dy+1,1,1);}
      }
    }
  }
  window.MazeGlass209={draw};
})();
