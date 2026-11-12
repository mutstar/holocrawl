(function(){
  'use strict';
  // A longer native-pixel ride, not a resized copy of the 206 miniature.
  function draw(q,p){
    const ox=p.x*32,oy=p.y*32;
    const r=(c,x,y,w,h)=>{q.fillStyle=c;q.fillRect(ox+x,oy+y,w,h);};
    function line(c,x,y,ex,ey,width=1){
      const dx=Math.abs(ex-x),dy=-Math.abs(ey-y),sx=x<ex?1:-1,sy=y<ey?1:-1;let error=dx+dy;
      for(;;){r(c,x-Math.floor(width/2),y-Math.floor(width/2),width,width);if(x===ex&&y===ey)break;const twice=2*error;if(twice>=dy){error+=dy;x+=sx;}if(twice<=dx){error+=dx;y+=sy;}}
    }
    const upper=[[24,210],[49,193],[72,147],[96,83],[122,42],[148,24],[174,21],[198,32],[222,64],[246,117],[271,190],[296,223],
      [320,215],[344,177],[368,136],[392,111],[416,108],[440,123],[466,160],[491,201],[516,221],
      [542,211],[566,184],[590,171],[614,177],[640,199],[664,224],[690,234],[752,234],[787,227],[812,210]];
    const front=[[812,210],[825,224],[822,242],[804,255],[784,263],[60,263],[38,253],[24,235],[24,210]];
    // Feet sit at one ground plane; the second rail hides their lower ends.
    const supports=upper.filter((_,i)=>i%2===0).concat([[174,21],[416,108],[590,171],[752,234],[812,210]]);
    for(const [x,y] of supports){
      r('rgba(0,0,0,.22)',x-7,281,18,4);r('#30333c',x-6,277,13,5);
      r('#272631',x-3,y+7,7,270-y);r('#455766',x-2,y+7,4,269-y);r('#7b8892',x-2,y+7,1,267-y);
      if(y<190){line('#2b303b',x,y+24,x+17,y+52,3);line('#526476',x,y+24,x+17,y+52);}
      r('#7a7882',x-5,277,11,1);
    }
    for(let x=66;x<794;x+=48){r('#30333c',x-5,278,13,5);r('#425563',x,268,4,11);r('#89959d',x,268,1,10);}
    function rail(points){
      for(let i=1;i<points.length;i++){
        const [x,y]=points[i-1],[nx,ny]=points[i];line('#272531',x,y+2,nx,ny+2,15);line('#524460',x,y+2,nx,ny+2,11);
      }
      let distance=0,nextTie=0;
      for(let i=1;i<points.length;i++){
        const [x,y]=points[i-1],[nx,ny]=points[i],length=Math.hypot(nx-x,ny-y);
        while(nextTie<=distance+length){const t=(nextTie-distance)/length,px=Math.round(x+(nx-x)*t),py=Math.round(y+(ny-y)*t);line('#8d769e',px,py-4,px,py+8,2);nextTie+=10;}
        distance+=length;
      }
      for(let i=1;i<points.length;i++){
        const [x,y]=points[i-1],[nx,ny]=points[i];
        line('#9e83bb',x,y-4,nx,ny-4,3);line('#cfb3df',x,y-5,nx,ny-5);line('#675583',x,y+4,nx,ny+4,3);
      }
    }
    rail(upper);rail(front);
    // Five stopped cars beside the platform, retaining the established palette.
    for(const x of [450,479,508,537,566]){
      r('#272531',x,239,24,19);r('#272531',x+3,235,13,6);r('#272531',x+3,257,5,5);r('#272531',x+16,257,5,5);
      r('#263943',x+2,244,21,12);r('#52918c',x+2,245,21,7);r('#b5d6c7',x+3,245,19,2);
      r('#94688e',x+5,237,10,7);r('#c195ae',x+5,237,10,2);r('#25363c',x+15,240,6,5);
      r('#d6ac64',x+20,249,3,2);r('#879099',x+4,258,3,2);r('#879099',x+17,258,3,2);
      if(x!==566)r('#64636c',x+24,253,5,2);
    }
  }
  window.LongCoaster209={draw};
})();
