(function(root){'use strict';let settings;const cache=new Map(),make=()=>{const c=document.createElement('canvas');c.width=c.height=32;return c;};
function configure(s){settings=s;cache.clear();}
function floors(){return settings.floorTiles.map(base=>{const c=make(),q=c.getContext('2d');q.drawImage(base,0,0);q.fillStyle='rgba(158,146,119,.25)';q.fillRect(0,0,32,32);return c;});}
function wall(mask){if(cache.has(mask))return cache.get(mask);const c=make(),q=c.getContext('2d'),{wall:atlas,rects}=settings;q.drawImage(atlas,...rects[mask+':0'],0,0,32,32);q.globalCompositeOperation='source-atop';q.fillStyle='rgba(188,176,145,.18)';q.fillRect(0,0,32,32);q.globalCompositeOperation='source-over';cache.set(mask,c);return c;}
function paint(q,m){if(!m.home)return;const h=m.home,x=h.x*32,y=h.y*32;
q.fillStyle='#536961';q.fillRect(x+2*32+6,y+4*32+3,5*32-12,4*32-6);q.strokeStyle='#8a846a';q.lineWidth=1;q.strokeRect(x+2*32+8.5,y+4*32+5.5,5*32-17,4*32-11);
// Just two small, worn mint windows; no full-height columns or ornate facade.
for(const wx of [3,9]){const xx=x+wx*32;q.fillStyle='#282f2d';q.fillRect(xx+5,y+12,22,17);q.fillStyle='#628a7f';q.fillRect(xx+7,y+13,18,14);q.fillStyle='#455e58';q.fillRect(xx+15,y+13,2,14);q.fillRect(xx+7,y+19,18,2);q.fillStyle='#938a72';q.fillRect(xx+4,y+28,24,2);}
}
function door(open){const key='door:'+open;if(cache.has(key))return cache.get(key);const c=make(),q=c.getContext('2d');q.fillStyle='#292b29';q.fillRect(3,2,26,30);q.fillStyle='#9b927b';q.fillRect(4,3,24,29);q.fillStyle='#45413a';q.fillRect(7,6,18,26);
if(open){q.clearRect(8,7,16,25);q.fillStyle='#74604a';q.fillRect(7,7,3,25);q.fillRect(23,7,2,25);}else{q.fillStyle='#77614b';q.fillRect(8,7,16,24);q.fillStyle='#39372f';q.fillRect(15,7,2,24);q.fillStyle='#bca77a';q.fillRect(13,20,1,3);q.fillRect(18,20,1,3);}q.fillStyle='#455b57';q.fillRect(7,2,18,4);q.fillStyle='#b2b6a0';q.fillRect(11,3,2,2);q.fillRect(15,3,2,2);q.fillRect(19,3,2,2);cache.set(key,c);return c;}
root.HomeMaterial134={configure,floors,wall,paint,door};})(globalThis);