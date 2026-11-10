const fs=require('fs'),path=require('path');
const R=path.resolve(__dirname,'..'),P=path.join(R,'preview'),D=path.join(P,'facility-gallery169');
fs.mkdirSync(D,{recursive:true});
const registry=JSON.parse(fs.readFileSync(path.join(P,'facility-pool131/registry.json'),'utf8'));
const order=['mountain','dining','theater','fantasy','wheel','market','gamers','holox','dev'];
const cards=[{id:'home',name:'홀로홈',group:'1층 고정 시설',size:'13×11칸',image:'../holohome-final161/home.png',detail:'../holohome-final161/',revision:161}];
for(const id of order){const f=registry.facilities.find(f=>f.id===id);cards.push({id,name:f.name,group:f.member,size:`${f.origin.width}×${f.origin.height}칸`,image:f.preview,open:f.openPreview,detail:'../facility-exteriors124/#'+id,revision:124});}
cards.push({id:'promise',name:'프로미스 타워',group:'Promise',size:'11×11칸',image:'../promise168/field-closed168.png',open:'../promise168/field-open168.png',detail:'../promise168/',revision:168});
cards.push({id:'myth',name:'포춘 네트워크',group:'Myth',size:'13×11칸',image:'../fortune167/field-closed167.png',open:'../fortune167/field-open167.png',detail:'../fortune167/',revision:167});
for(const f of cards)for(const k of ['image','open'])if(f[k]&&!fs.existsSync(path.resolve(D,f[k])))throw Error('Missing '+f[k]);
fs.writeFileSync(path.join(D,'catalog.json'),JSON.stringify({revision:169,count:cards.length,scope:'Existing browser artwork only; no newly generated assets',cards},null,2)+'\n');
console.log(JSON.stringify({gallery:169,count:cards.length,ids:cards.map(f=>f.id)}));
