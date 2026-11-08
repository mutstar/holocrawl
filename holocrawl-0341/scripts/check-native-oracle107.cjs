const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const LOS=require('../preview/city-layout07/visibility.js');
const root=path.resolve(__dirname,'../analysis/native-play107-01',process.argv[2]||'suite-01');
let maps=0,frames=0,cells=0,mismatches=0,walk=0,blocked=0,doors=0,doorLOS=0,corners=0,cornerAllowed=0;
for(const dir of fs.readdirSync(root,{withFileTypes:true}).filter(d=>d.isDirectory()&&(d.name==='random168'||d.name.startsWith('forced-')))){
 for(const name of fs.readdirSync(path.join(root,dir.name)).filter(n=>n.startsWith('probe-')&&n.endsWith('.json'))){
  const p=JSON.parse(fs.readFileSync(path.join(root,dir.name,name)));assert.equal(p.status,'passed');maps++;
  for(const f of p.frames){const h=f.visible.length,w=f.visible[0].length;
   const js=LOS.compute(w,h,{x:f.player[0],y:f.player[1]},(x,y)=>Number(f.opacity[y][x]),7);
   for(let i=0;i<js.length;i++){cells++;if(js[i]!==Number(f.visible[Math.floor(i/w)][i%w]))mismatches++}frames++;
  }
  walk+=p.walkCommands;blocked+=p.blockedCommands;doors+=p.doorCommands;doorLOS+=p.doorLosPairs;corners+=p.diagonalCornerTested;cornerAllowed+=p.diagonalCornerAllowed;
 }
}
const result={status:mismatches?'failed':'passed',maps,nativeLosFrames:frames,comparedCells:cells,mismatches,nativeWalkCommands:walk,nativeBlockedCommands:blocked,nativeDoorOpenStepPairs:doors,nativeDoorLosPairs:doorLOS,diagonalCornerCases:corners,diagonalCornerAllowed:cornerAllowed};
fs.writeFileSync(path.join(root,'oracle-validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));assert.equal(mismatches,0);assert.equal(maps,177);
