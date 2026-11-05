function showMerchType(type){
 stop();stage=4;overview=false;const pool=[...map.marketWalls,...map.marketProps].filter(p=>p.type===type);if(!pool.length)return false;
 const fixture=pool[Math.floor(pool.length/2)],choices=[];
 for(let y=Math.max(1,fixture.y-3);y<=Math.min(map.h-2,fixture.y+3);y++)for(let x=Math.max(1,fixture.x-3);x<=Math.min(map.w-2,fixture.x+3);x++)if(map.cells[y*map.w+x]===G.FLOOR)choices.push({x,y,score:Math.abs(x-fixture.x)+Math.abs(y-fixture.y-2)});
 choices.sort((a,b)=>a.score-b.score);if(!choices.length)return false;player={x:choices[0].x,y:choices[0].y};updateVision();draw();$('stockInfo').textContent=MarketStock.describe(fixture,map,stockMix);return true;
}
$('acrylicView').onclick=()=>showMerchType('acrylic-window');$('shirtView').onclick=()=>showMerchType('shirt-window');$('trashView').onclick=()=>showMerchType('trash-bags');
