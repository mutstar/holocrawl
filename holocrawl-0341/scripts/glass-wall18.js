// Dedicated transparent glass art; collision and LOS continue to use terrain features.
let glassWallArtEnabled=true;
const tileBeforeGlass18=tile;
function drawGlassWall18(c,map,x,y,px,py,t){
 const s=t/32,glass=(xx,yy)=>feature(map,xx,yy).includes('clear_')&&isWall(feature(map,xx,yy));
 const n=glass(x,y-1),e=glass(x+1,y),south=glass(x,y+1),w=glass(x-1,y);
 c.save();c.imageSmoothingEnabled=false;
 c.drawImage(tiles[RandomFloor.index(map.seed,0,x,y)],px,py,t,t);
 c.fillStyle='rgba(157,209,217,.10)';c.fillRect(px,py,t,t);
 const line=(color,a,b,width,height)=>{c.fillStyle=color;c.fillRect(px+a*s,py+b*s,width*s,height*s)};
 // The connected panes share only a perimeter frame, rather than opaque square blocks.
 if(!n){line('#485d61',0,1,32,1);line('#adc4c5',0,2,32,1);line('rgba(197,229,229,.45)',1,3,30,1);}
 if(!south){line('#6c8689',0,29,32,1);line('#34494d',0,30,32,1);}
 if(!w){line('#486166',1,0,1,32);line('#9ab7ba',2,0,1,32);}
 if(!e){line('#738f93',29,0,1,32);line('#354c51',30,0,1,32);}
 // Broken paired highlights suggest a glass surface while leaving the floor visible.
 const h=hash(map.seed,x+97,y+83);
 if(h%3!==0){for(let a=0;a<9;a++){line('rgba(213,240,241,.52)',8+a,17-a,1,1);if(a<5)line('rgba(194,225,230,.27)',12+a,21-a,1,1);}}
 if((!n||!south)&&(!w||!e)){const xx=!w?1:28,yy=!n?1:28;line('#344a50',xx,yy,3,3);line('#bed0ce',xx+1,yy+1,1,1);}
 c.restore();
}
tile=function(c,map,x,y,px,py,t,style='fit',forceState=null,oldWall=wallOld){
 const f=feature(map,x,y);
 if(glassWallArtEnabled&&f.includes('clear_')&&isWall(f)){drawGlassWall18(c,map,x,y,px,py,t);return;}
 return tileBeforeGlass18(c,map,x,y,px,py,t,style,forceState,oldWall);
};
