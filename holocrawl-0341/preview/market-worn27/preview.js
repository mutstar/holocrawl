(async()=>{const sources={floor:'../city-layout07/assets/cement-reference.png',wall:'../native-water02/assets/concrete-wall-surface256.png',body:'../city-layout07/assets/body.png',boots:'../city-layout07/assets/boots.png',armour:'../city-layout07/assets/armour.png',helmet:'../city-layout07/assets/helmet.png',sword:'../city-layout07/assets/sword.png',live:'assets/live-shop-96.png',goods:'assets/goods-shop-96.png',cafe:'assets/cafe-96.png'},images={};
await Promise.all(Object.entries(sources).map(async([key,src])=>{images[key]=await new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error(src));i.src=src;});}));
const c=document.getElementById('street'),ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;const patches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]],tiles=[];
for(let i=0;i<16;i++){const a=document.createElement('canvas');a.width=a.height=32;const ac=a.getContext('2d');ac.imageSmoothingEnabled=false;ac.translate(16,16);ac.rotate(i%4*Math.PI/2);ac.drawImage(images.floor,...patches[Math.floor(i/4)],-16,-16,32,32);tiles.push(a);}
for(let y=0;y<14;y++)for(let x=0;x<34;x++){
 if(y<4){ctx.fillStyle='#232521';ctx.fillRect(x*32,y*32,32,32);ctx.globalAlpha=.14;ctx.drawImage(images.wall,x%8*32,0,32,32,x*32,y*32,32,32);ctx.globalAlpha=1;}
 else if(y===4||y===5){ctx.drawImage(images.wall,(x+(y-4)*3)%8*32,0,32,32,x*32,y*32,32,32);ctx.fillStyle='#222522';if(y===4)ctx.fillRect(x*32,y*32,32,2);if(y===5)ctx.fillRect(x*32,y*32+30,32,2);}
 else ctx.drawImage(tiles[RandomFloor.index('market25',4,x,y)],x*32,y*32,32,32);
}
for(const[name,x]of[['live',3],['goods',15],['cafe',27]]){ctx.drawImage(images[name],x*32,4*32,96,64);ctx.fillStyle='rgba(8,13,9,.35)';ctx.fillRect(x*32+3,6*32,90,1);}
for(const[name,x]of[['body',17],['boots',17],['armour',17],['helmet',17],['sword',17]])ctx.drawImage(images[name],x*32,8*32,32,32);
window.ready=true;
})().catch(e=>{document.body.insertAdjacentText('beforeend','불러오기 오류: '+e.message);throw e;});
