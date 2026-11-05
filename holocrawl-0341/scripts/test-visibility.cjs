const assert=require('assert'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),V=require('../preview/street-vision01/visibility.js');
const fixtures=require('../analysis/visibility01/native-fixtures.json');
let compared=0;for(const f of fixtures.cases){const w=f.rows[0].length,h=f.rows.length;const mask=V.compute(w,h,{x:f.source[0],y:f.source[1]},(x,y)=>f.rows[y][x]==='#'?2:f.rows[y][x]==='~'?1:0,f.radius);for(let y=0;y<h;y++)for(let x=0;x<w;x++){assert.strictEqual(mask[y*w+x],Number(f.visible[y][x]),`native mismatch fixture${f.id} at${x},${y}`);compared++;}}
const w=25,h=25,source={x:12,y:12},clear=()=>0;
const mask=V.compute(w,h,source,clear);assert.strictEqual(mask.reduce((a,b)=>a+b,0),225);assert(mask[19*w+19]);assert(!mask[20*w+12]);
let blocked=V.compute(w,h,source,(x,y)=>x===13?2:0);assert(blocked[12*w+13]);assert(!blocked[12*w+14]);
let corner=V.compute(w,h,source,(x,y)=>(x===13&&y===12||x===12&&y===13)?2:0);assert(corner[13*w+13]);
const memory=new V.Memory(w,h),cells=new Uint8Array(w*h).fill(1);memory.update(cells,source);const previously=memory.visible.slice();memory.update(cells,{x:22,y:22});assert(previously[12*w+12]&&!memory.visible[12*w+12]&&memory.explored[12*w+12]);cells[12*w+12]=0;assert.strictEqual(memory.renderCells(cells)[12*w+12],1,'Hidden terrain changes leaked');
const small={w:7,h:3,cells:new Uint8Array(21).fill(1)};const explored=new Uint8Array(21);for(let x=0;x<3;x++)explored[7+x]=1;assert.strictEqual(V.knownRoute(small,{x:0,y:1},{x:6,y:1},explored).length,0);assert(V.knownRoute(small,{x:0,y:1},{x:2,y:1},explored).length);
const result={status:'passed',nativeFixtureCases:fixtures.cases.length,comparedCells:compared,nativeMaskMatches:true,range7Square:true,wallBlocksBehind:true,wallFaceVisible:true,diagonalGapVisible:true,transparentFenceUsesClearOpacity:true,exploredMemoryPersists:true,hiddenTerrainNotUpdated:true,pathCannotUseUnknownCells:true};fs.writeFileSync(path.join(root,'analysis/visibility01/logic-validation.json'),JSON.stringify(result,null,2));console.log(result);
