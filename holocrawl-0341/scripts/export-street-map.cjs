// Keep the approved browser generator authoritative during the first native floor pass.
const fs=require('fs'),path=require('path');
const G=require('../preview/street-vision01/generator.js');
function hash(seed,x,y){let n=Math.imul(x+19,374761393)^Math.imul(y+73,668265263);for(const c of seed)n=Math.imul(n^c.charCodeAt(0),1274126177);return(n^(n>>>13))>>>0;}
function generate(seed){
 if(!/^[A-Za-z0-9_-]{1,80}$/.test(seed))throw Error('Use an ASCII seed of 1-80 letters/digits/_/-.');
 const m=G.generate(seed,80,70,'floor');m.enemies=[];m.items=[];
 const walk=(x,y)=>x>=0&&y>=0&&x<m.w&&y<m.h&&m.cells[y*m.w+x]!==G.WALL;
 const terrain=Array.from(m.cells,c=>c===G.WALL?'#':c===G.BARRIER?'|':'.');
 terrain[m.upstairs.y*m.w+m.upstairs.x]='<';terrain[m.exit.y*m.w+m.exit.x]='>';
 const floors=[],walls=[];
 for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){
   floors.push(hash(seed,x,y)%4);
   let mask=(walk(x,y-1)?1:0)|(walk(x+1,y)?2:0)|(walk(x,y+1)?4:0)|(walk(x-1,y)?8:0),decor=0;
   const p=m.prefab,inPrefab=x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h;
   if(!inPrefab&&m.cells[y*m.w+x]===G.WALL&&walk(x,y+1)&&x>1&&x<m.w-2&&y>0&&y<m.h-1&&m.cells[y*m.w+x-1]===G.WALL&&m.cells[y*m.w+x+1]===G.WALL&&x%3===1&&hash(seed,x,y)%100<68)decor=1+hash(seed,x+431,y)%4;
   walls.push(inPrefab?80+(y-p.y)*4+x-p.x:mask+decor*16);
 }
 const rows=[];for(let y=0;y<m.h;y++)rows.push(terrain.slice(y*m.w,(y+1)*m.w).join(''));
 const text=['HCSTREET1',seed,`${m.w} ${m.h}`,...rows,floors.join(' '),walls.join(' ')].join('\n')+'\n';
 return{map:m,terrain,floors,walls,text};
}
if(require.main===module){const seed=process.argv[2]||'CITY-NATIVE-001',out=path.resolve(process.argv[3]||'runtime/street01/maps/current.hcmap');const data=generate(seed);fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,data.text);fs.writeFileSync(out+'.json',JSON.stringify({seed,width:80,height:70,upstairs:data.map.upstairs,downstairs:data.map.exit,validation:data.map.validation,enemies:0,items:0,generator:'preview/street-vision01/generator.js'},null,2)+'\n');console.log(out);}
module.exports={generate};
