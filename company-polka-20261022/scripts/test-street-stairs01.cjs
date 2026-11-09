const fs=require('fs');const path=require('path');const assert=require('assert');
const base=path.resolve(__dirname,'../analysis/previews/street-stairs01');const g=require(path.join(base,'generator.js'));
const hashes=new Set();let minimum=1e9,maximum=0;
for(let i=0;i<500;i++){
 const m=g.generate('review-'+i),v=g.validate(m);assert(v.ok);minimum=Math.min(minimum,v.exitDistance);maximum=Math.max(maximum,v.exitDistance);
 assert.strictEqual(v.walkable,v.reached);assert(m.rooms.length>=3);assert(m.prefab);assert(['wall','floor'].includes(m.exitType));if(m.exitType==='floor'){for(let yy=m.exit.y-1;yy<=m.exit.y+1;yy++)for(let xx=m.exit.x-1;xx<=m.exit.x+1;xx++)assert.strictEqual(m.cells[yy*m.w+xx],g.FLOOR);}else assert(m.exitDoor);assert(m.enemies.every(e=>g.distances(m,m.start).dist[e.y*m.w+e.x]>=8));
 assert.strictEqual(m.path[0].x,m.start.x);assert.strictEqual(m.path.at(-1).y,m.exit.y);
 for(let j=1;j<m.path.length;j++)assert.strictEqual(Math.abs(m.path[j].x-m.path[j-1].x)+Math.abs(m.path[j].y-m.path[j-1].y),1);
 for(let y=m.prefab.y;y<m.prefab.y+m.prefab.h;y++)for(let x=m.prefab.x;x<m.prefab.x+m.prefab.w;x++)assert.strictEqual(m.cells[y*m.w+x],g.WALL);
 const again=g.generate('review-'+i);assert.deepStrictEqual(m,again);hashes.add(Buffer.from(m.cells).toString('base64'));
}
assert.strictEqual(hashes.size,500);
const proof={status:'passed',seeds:500,uniqueMaps:hashes.size,sameSeedDeterministic:true,allWalkableConnected:true,allExitsReachable:true,solidOuterBoundary:true,validPrefabFootprints:true,enemyStartSafetyDistance:8,shortestExitDistanceRange:[minimum,maximum],scope:'Independent JS prototype; not Crawl native dungeon generator.'};
fs.writeFileSync(path.join(base,'generator-validation.json'),JSON.stringify(proof,null,2));console.log(JSON.stringify(proof));


