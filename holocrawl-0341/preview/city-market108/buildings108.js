(async()=>{
 const load=url=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error(url));i.src=url;});
 const ids=['live-shop','goods-shop','cafe'],names=['라이브숍 입구','굿즈숍','작은 카페'];
 const old=await Promise.all(ids.map(id=>load(`../market-worn27/assets/${id}-96.png`))),fresh=old.map((im,i)=>Market108.recolor(im,ids[i]));
 const floor=await load('../city-market02/assets/cement-reference.png'),tiles=RandomFloor.variants(floor);
 const body=await load('../city-market02/assets/body.png');
 await Market108.load();
 const cards=document.getElementById('cards');ids.forEach((id,i)=>{const a=document.createElement('article');a.innerHTML=`<h2>${names[i]}</h2><p>수정 전27</p><canvas id="old${i}" width="96" height="64"></canvas><p>새 청회색 골조</p><canvas id="new${i}" width="96" height="64"></canvas>`;cards.append(a);for(const [prefix,im]of[['old',old[i]],['new',fresh[i]]])document.getElementById(prefix+i).getContext('2d').drawImage(im,0,0);});
 const c=document.getElementById('street'),g=c.getContext('2d');
 function draw(){g.imageSmoothingEnabled=false;const w=34,h=14,cells=Array.from({length:w*h},(_,i)=>Math.floor(i/w)<=5?0:1);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(cells[y*w+x]===0)Market108.wall(g,cells,w,h,x,y,32,(x+y)%8);else g.drawImage(tiles[RandomFloor.index('market25',4,x,y)],x*32,y*32);
  for(let i=0;i<3;i++){const x=[3,15,27][i]*32;g.drawImage(document.getElementById('before').checked?old[i]:fresh[i],x+3,4*32+4,90,56);}
  g.drawImage(body,17*32,8*32,32,32);
 }
 document.getElementById('before').onchange=draw;draw();window.buildings108Ready=true;
})().catch(e=>{document.body.append('불러오기 실패: '+e.message);throw e;});
