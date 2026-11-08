(function(root){
 'use strict';
 let cachedMap,cachedLevel,layer,stats;
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 function random(seed){let n=2166136261;for(const c of seed)n=Math.imul(n^c.charCodeAt(0),16777619);return()=>{n+=0x6D2B79F5;let t=Math.imul(n^(n>>>15),1|n);t^=t+Math.imul(t^(t>>>7),61|t);return((t^(t>>>14))>>>0)/4294967296;};}
 function create(map,floor,hash){
  const W=map.w*32,H=map.h*32,base=document.createElement('canvas');base.width=W;base.height=H;
  const bg=base.getContext('2d',{willReadFrequently:true});
  for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++)if(map.cells[y*map.w+x]===0)Market108.wall(bg,map.cells,map.w,map.h,x,y,32,hash(x,y)%8);
  const original=bg.getImageData(0,0,W,H).data,damage=new Uint8ClampedArray(W*H*4),age=clamp(floor-4,0,3);
  let rejectedFloor=0,painted=0,cracks=0,chips=0;
  // Each crack uses the same seeded anchor and first segments at every age.
  // Increasing age extends it and admits extra anchors rather than shuffling it.
  function pixel(x,y,color,chip=false){x=Math.round(x);y=Math.round(y);if(x<0||y<0||x>=W||y>=H)return;
   const k=(y*W+x)*4;if(map.cells[Math.floor(y/32)*map.w+Math.floor(x/32)]!==0){rejectedFloor++;return;}
   const bright=Math.max(original[k],original[k+1],original[k+2]);
   // Coping is frozen material92 (>85). Keep its outer outline continuous;
   // only separately placed, two-pixel inset chips may mark the coping itself.
   if(!chip&&bright>85)return;
   if(chip&&(bright<86||x%32===0||y%32===0||x%32===31||y%32===31))return;
   if(!damage[k+3])painted++;
   damage[k]=color[0];damage[k+1]=color[1];damage[k+2]=color[2];damage[k+3]=255;
  }
  function line(a,b,ink,edge,wide=false){
   let x=Math.round(a[0]),y=Math.round(a[1]);const ex=Math.round(b[0]),ey=Math.round(b[1]),dx=Math.abs(ex-x),sx=x<ex?1:-1,dy=-Math.abs(ey-y),sy=y<ey?1:-1;let err=dx+dy;
   const normal=Math.abs(b[0]-a[0])>Math.abs(b[1]-a[1])?[0,1]:[1,0];
   for(;;){if(edge)pixel(x+normal[0],y+normal[1],edge);pixel(x,y,ink);if(wide)pixel(x-normal[0],y-normal[1],ink);if(x===ex&&y===ey)break;const e=2*err;if(e>=dy){err+=dy;x+=sx;}if(e<=dx){err+=dx;y+=sy;}}
  }
  const density=[.12,.17,.23,.29][age],growth=[.38,.53,.76,1];
  const styles={hairline:0,wandering:0,branching:0,split:0},angles=Array(12).fill(0),lengths=[];
  for(let gy=0;gy<H;gy+=64)for(let gx=0;gx<W;gx+=64){
   const rng=random(`${map.seed}:fracture110:${gx},${gy}`);if(rng()>density)continue;
   const roll=rng(),kind=roll<.28?'hairline':roll<.61?'wandering':roll<.88?'branching':'split';
   let p=[gx+rng()*64,gy+rng()*64],angle=rng()*Math.PI*2;const initialAngle=angle;
   const count=(kind==='hairline'?5:kind==='split'?11:9)+Math.floor(rng()*5),scale=.55+rng()*1.1,points=[p],heads=[];
   const shade=Math.floor(rng()*9),ink=[16+shade,22+shade,26+shade],edge=kind==='hairline'&&rng()<.55?null:[46+shade,59+shade,66+shade];
   // An independent walker gives variable turns and spacing. It is rotated
   // freely, without mirroring a fixed Y-shaped stencil or a fixed diagonal.
   for(let j=0;j<count;j++){
    const step=(kind==='hairline'?1.7+rng()*2.8:2+rng()*5.5)*scale;
    angle+=(rng()-.5)*(kind==='split'?.62:kind==='wandering'?1.8:1.35);
    if(kind==='split'&&rng()<.2)angle+=(rng()-.5)*1.7;
    heads.push(angle);p=[p[0]+Math.cos(angle)*step,p[1]+Math.sin(angle)*step];points.push(p);
   }
   // Branch origins, handedness, spread and length are chosen independently.
   // All ages share the same full path and only reveal a longer prefix.
   const branches=[],branchCount=kind==='branching'?1+Math.floor(rng()*4):kind==='wandering'&&rng()<.3?1:0;
   for(let k=0;k<branchCount;k++){
    const at=1+Math.floor(rng()*(count-2)),hand=rng()<.5?-1:1;
    let q=points[at],a=heads[at-1]+hand*(.55+rng()*1.8);const branch=[q],n=2+Math.floor(rng()*5);
    for(let j=0;j<n;j++){a+=(rng()-.5)*1.1;const step=(1.5+rng()*4.5)*scale;q=[q[0]+Math.cos(a)*step,q[1]+Math.sin(a)*step];branch.push(q);}
    branches.push({at,points:branch});
   }
   const steps=Math.max(2,Math.ceil(count*growth[age])),start=painted;let length=0;
   for(let j=1;j<=steps;j++){const a=points[j-1],b=points[j];length+=Math.hypot(b[0]-a[0],b[1]-a[1]);line(a,b,ink,edge,age===3&&kind==='split'&&j>2&&j<steps-1);}
   if(age>=1)for(const branch of branches)if(branch.at<steps-1){
    const n=Math.max(1,Math.ceil((branch.points.length-1)*growth[age]));
    for(let j=1;j<=n;j++)line(branch.points[j-1],branch.points[j],ink,edge&&age>=2?edge:null);
   }
   if(painted>start){cracks++;styles[kind]++;angles[Math.floor(initialAngle/(Math.PI*2)*12)%12]++;lengths.push(length);}
  }
  // Sparse inset nicks at the inside of a rim. No alpha holes and no floor
  // rubble are introduced, so silhouettes and collision stay unchanged.
  if(age>=2)for(let y=1;y<map.h-1;y++)for(let x=1;x<map.w-1;x++)if(map.cells[y*map.w+x]===0){
   const rng=random(`${map.seed}:rim109:${x},${y}`);if(rng()>(age===2?.045:.085))continue;
   const candidates=[];if(map.cells[y*map.w+x-1]!==0)candidates.push([x*32+2,y*32+6+Math.floor(rng()*8)]);
   if(map.cells[(y-1)*map.w+x]!==0)candidates.push([x*32+7+Math.floor(rng()*16),y*32+2]);
   if(map.cells[(y+1)*map.w+x]!==0)candidates.push([x*32+7+Math.floor(rng()*16),y*32+16]);
   if(!candidates.length)continue;const p=candidates[Math.floor(rng()*candidates.length)],start=painted;
   pixel(p[0],p[1],[55,67,73],true);pixel(p[0]+1,p[1],[68,80,85],true);if(painted>start)chips++;
  }
  layer=document.createElement('canvas');layer.width=W;layer.height=H;layer.getContext('2d').putImageData(new ImageData(damage,W,H),0,0);
  stats={floor,cracks,chips,paintedPixels:painted,rejectedFloorCandidates:rejectedFloor,width:W,height:H,styles,orientationBins:angles,mainLengthRange:[Math.min(...lengths),Math.max(...lengths)]};cachedMap=map;cachedLevel=floor;
 }
 function draw(ctx,map,t,floor,hash){if(document.getElementById('noWear').checked)return;const selection=document.getElementById('wearLevel').value;floor=selection==='auto'?floor:Number(selection);if(cachedMap!==map||cachedLevel!==floor)create(map,floor,hash);ctx.drawImage(layer,0,0,map.w*t,map.h*t);}
 root.Wear110={draw,getStats:()=>({...stats}),getLayer:()=>layer};
})(globalThis);
