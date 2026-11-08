(function(root){
 'use strict';
 const ink='#1a242b',metal='#4d6571',top='#7c929b',side='#354953',paper='#806b50',paperTop='#a58b67',paperSide='#61513f';
 const clamp=n=>Math.max(0,Math.min(255,Math.round(n)));
 function shade(hex,f){const s=hex.slice(1);return '#'+[0,2,4].map(i=>clamp(parseInt(s.slice(i,i+2),16)*f).toString(16).padStart(2,'0')).join('');}
 function paint(g,f,map,mix){
  const rect=(x,y,w,h,c)=>{g.fillStyle=c;g.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h));};
  const poly=(points,c)=>{g.fillStyle=c;const minY=Math.max(0,Math.floor(Math.min(...points.map(p=>p[1])))),maxY=Math.min(32,Math.ceil(Math.max(...points.map(p=>p[1]))));
   for(let y=minY;y<maxY;y++){const xs=[];for(let i=0,j=points.length-1;i<points.length;j=i++){const a=points[i],b=points[j],cy=y+.5;if((a[1]>cy)!==(b[1]>cy))xs.push(a[0]+(cy-a[1])*(b[0]-a[0])/(b[1]-a[1]));}xs.sort((a,b)=>a-b);for(let i=0;i+1<xs.length;i+=2){const x=Math.ceil(xs[i]-.5),end=Math.ceil(xs[i+1]-.5);g.fillRect(x,y,end-x,1);}}
  };
  // Shared projection: visible top face, south face and narrow east side.
  function box(x,y,w,h,d,front=metal,roof=top,east=side){
   poly([[x,y],[x+3,y-d],[x+w,y-d],[x+w+3,y],[x+w+3,y+h-2],[x+w,y+h],[x,y+h]],ink);
   rect(x+1,y,w-1,h-1,front);poly([[x+1,y-1],[x+4,y-d+1],[x+w-1,y-d+1],[x+w+1,y-1]],roof);
   poly([[x+w,y],[x+w+2,y-1],[x+w+2,y+h-3],[x+w,y+h-1]],east);rect(x+2,y,w-3,1,shade(roof,.86));
  }
  const ids=MarketStock.select(map.seed,map.floorNumber,f,mix),members=Object.fromEntries(MarketMembers.map(m=>[m.id,m])),colors=ids.map(id=>members[id].color);
  switch(f.type){
   case 'delivery-boxes':
    box(3,20,12,9,4,paper,paperTop,paperSide);box(16,18,11,10,4,paper,paperTop,paperSide);box(9,10,12,9,4,paper,paperTop,paperSide);
    for(const[x,y]of[[8,20],[20,18],[14,10]]){rect(x,y,2,7,'#b19d7c');rect(x+1,y-3,1,3,'#c0ad8d');}rect(5,24,3,2,'#c4b694');break;
   case 'open-carton':
    box(7,18,18,11,5,paper,paperSide,paperSide);poly([[8,17],[12,13],[25,13],[27,17],[23,21],[10,21]],'#302e28');
    poly([[8,16],[3,14],[1,19],[7,22],[12,19]],paperTop);poly([[25,15],[29,13],[31,19],[26,22],[22,19]],'#97805d');
    poly([[11,13],[13,9],[26,9],[25,14]],'#9d8562');poly([[10,20],[22,20],[25,25],[12,26]],'#ae936c');rect(11,26,13,2,paper);break;
   case 'acrylic-rack':
    rect(5,15,2,14,ink);rect(25,15,2,14,ink);box(4,23,22,5,4,metal,top,side);rect(4,8,23,3,ink);rect(6,10,1,13,metal);rect(25,10,1,13,metal);
    ids.forEach((id,i)=>g.drawImage(MarketStock.getSprite(id),6+i*7,10,6,12));rect(5,23,20,1,'#8ca2aa');break;
   case 'shirt-stack':
    colors.forEach((c,i)=>{const x=4+i*3,y=24-i*5;box(x,y,17,4,3,shade(c,.56),shade(c,.78),shade(c,.4));rect(x+7,y-2,3,1,shade(c,.49));rect(x+2,y+2,12,1,shade(c,.43));});break;
   case 'hoodie-rack':
    rect(5,6,2,22,side);rect(26,6,2,22,side);rect(4,5,24,2,top);rect(3,28,7,1,ink);rect(23,28,7,1,ink);
    ['#75858c','#526875','#89969a'].forEach((c,i)=>{const x=7+i*6;poly([[x,10],[x+3,8],[x+6,11],[x+7,18],[x+5,19],[x+5,25],[x,25],[x,19],[x-2,18]],ink);poly([[x+1,11],[x+3,10],[x+5,12],[x+5,23],[x+1,23]],c);rect(x+2,13,2,2,shade(c,.65));rect(x+1,22,4,1,shade(c,.72));});break;
   case 'plush-basket':
    box(4,22,23,6,5,metal,side,side);
    ['#a9a99a','#b7a998','#8d9da2'].forEach((c,i)=>{const x=6+i*7,y=13+(i%2)*2;rect(x+1,y-3,2,5,c);rect(x+5,y-3,2,5,c);poly([[x,y],[x+7,y],[x+8,y+6],[x+5,y+10],[x+1,y+9],[x-1,y+4]],ink);rect(x+1,y+1,5,7,c);rect(x+2,y+3,1,1,ink);rect(x+5,y+3,1,1,ink);});rect(5,24,21,1,top);for(let x=7;x<26;x+=4)rect(x,25,1,3,side);break;
   case 'poster-rolls':
    box(6,23,17,5,4,paper,paperTop,paperSide);for(const[x,y,h]of[[7,12,13],[13,8,16],[19,13,12]]){rect(x,y,5,h,ink);rect(x+1,y,3,h-1,'#b8ab8f');rect(x+1,y,3,2,'#d0c3a4');rect(x+3,y+2,1,h-3,'#827961');}rect(6,23,17,2,'#795e4b');break;
   case 'keychain-hooks':
    box(5,25,20,3,3,metal,top,side);rect(6,7,2,19,side);rect(24,7,2,19,side);rect(6,6,20,2,top);
    for(let y=11;y<24;y+=6){rect(8,y-1,16,1,metal);for(let x=9;x<24;x+=5){rect(x,y,1,2,'#9babb0');rect(x-1,y+2,3,3,(x+y)%3?'#9c9476':'#8b9eaa');rect(x,y+2,1,1,'#c1c6bb');}}break;
   case 'badge-trays':
    box(4,19,23,9,5,metal,side,side);for(let row=0;row<3;row++)for(let col=0;col<4;col++){const x=7+col*5,y=17+row*4;rect(x,y,3,3,'#202d35');rect(x,y,2,2,['#af8392','#a69d78','#799da8','#aaa5a0'][(row+col)%4]);}rect(5,27,20,1,top);break;
   case 'shopping-bags':
    for(const[x,y,w,h,c]of[[4,19,10,9,'#a39376'],[12,14,11,13,'#9b8b71'],[21,20,7,8,'#566c75']]){rect(x+2,y-4,w-4,5,ink);rect(x+3,y-3,w-6,3,'#465055');box(x,y,w,h,2,c,shade(c,1.1),shade(c,.69));rect(x+Math.floor(w/2)-1,y+4,2,2,'#c8b5b3');}break;
   case 'delivery-cart':
    rect(8,27,4,3,ink);rect(24,27,4,3,ink);box(5,23,22,4,4,metal,top,side);rect(5,7,2,17,side);rect(5,6,15,2,top);rect(18,7,2,11,metal);box(11,19,11,4,3,side,metal,ink);break;
   case 'folding-crates':
    box(4,18,23,10,5,side,metal,ink);rect(6,19,19,7,'#263a44');for(let x=7;x<26;x+=5)rect(x,19,1,7,metal);rect(5,22,21,1,metal);rect(6,16,18,1,top);rect(8,27,16,1,metal);break;
   case 'trash-bags':
    for(const[x,y,w,h,c]of[[4,20,13,9,'#38474b'],[14,16,14,12,'#303f44'],[8,10,12,14,'#435157']]){poly([[x+w/2,y],[x+w-2,y+3],[x+w,y+h-3],[x+w-3,y+h],[x+2,y+h],[x,y+h-4],[x+2,y+3]],ink);poly([[x+w/2,y+1],[x+w-3,y+4],[x+w-2,y+h-3],[x+3,y+h-1],[x+2,y+h-4]],c);rect(x+w/2-1,y-2,2,3,c);rect(x+3,y+5,1,4,shade(c,1.23));}break;
   case 'paper-rubbish':
    for(const[x,y,w,h,c]of[[4,22,10,5,'#a39274'],[12,16,9,7,'#81745d'],[19,24,10,4,'#9c8a6a'],[8,27,9,3,'#b1a184'],[21,18,6,5,'#a4977a']]){poly([[x,y+1],[x+w-3,y],[x+w,y+h-2],[x+3,y+h]],ink);poly([[x+1,y+1],[x+w-3,y+1],[x+w-1,y+h-2],[x+3,y+h-1]],c);rect(x+3,y+2,2,1,shade(c,.72));}break;
   case 'recycling-bins':
    box(4,16,11,12,4,metal,top,side);box(17,16,10,12,4,metal,'#a18d51',side);rect(7,15,5,2,ink);rect(20,15,4,2,ink);rect(7,21,4,3,'#778e98');rect(20,21,4,3,'#9a8b61');rect(6,26,7,1,side);rect(19,26,6,1,side);break;
   default:throw Error('Unstyled floor fixture: '+f.type);
  }
 }
 const cache=new Map();
 function sprite(f,map,mix){const key=`${map.seed}:${map.floorNumber}:${f.type}:${f.x},${f.y}:${mix}`;if(cache.has(key))return cache.get(key);const c=document.createElement('canvas');c.width=c.height=32;const g=c.getContext('2d',{willReadFrequently:true});g.imageSmoothingEnabled=false;paint(g,f,map,mix);
  // A little material grain keeps the simplified faces from becoming flat UI
  // icons. Do not touch silhouettes or add the old high-frequency speckling.
  if(['delivery-boxes','open-carton','shopping-bags','paper-rubbish','folding-crates','recycling-bins'].includes(f.type)){
   const im=g.getImageData(0,0,32,32),a=im.data;for(let y=0;y<32;y++)for(let x=0;x<32;x++){const k=(y*32+x)*4,n=(Math.imul(x+17,374761393)^Math.imul(y+29,668265263))>>>0;if(a[k+3]&&Math.max(a[k],a[k+1],a[k+2])>65&&n%13===0){const d=n%2?5:-5;for(let j=0;j<3;j++)a[k+j]=clamp(a[k+j]+d);}}g.putImageData(im,0,0);
  }
  if(cache.size>500)cache.clear();cache.set(key,c);return c;}
 function draw(ctx,f,map,images,t,mix){
  const meta=MerchCatalog.find(m=>m.id===f.type);
  if(meta.kind==='wall'||document.getElementById('beforeFloor113').checked||document.getElementById('beforeScene112').checked||Market108.isOld())return Scene112.draw(ctx,f,map,images,t,mix);
  ctx.save();ctx.translate(f.x*t,f.y*t);ctx.scale(t/32,t/32);ctx.imageSmoothingEnabled=false;
  // Cast shadow extends to the southeast; the dark contact strip sits under
  // the feet. Both fit the same32px cell and never paint a neighbouring wall.
  for(const[y,x,w,a]of[[25,5,20,.12],[26,4,23,.2],[27,4,25,.27],[28,5,25,.32],[29,7,23,.27],[30,11,17,.18],[31,15,10,.1]]){ctx.fillStyle=`rgba(6,12,17,${a})`;ctx.fillRect(x,y,w,1);}
  ctx.fillStyle='rgba(4,9,13,.48)';ctx.fillRect(6,27,20,2);
  ctx.drawImage(sprite(f,map,mix),0,0);ctx.restore();
 }
 root.Scene113={draw,sprite};
})(globalThis);
