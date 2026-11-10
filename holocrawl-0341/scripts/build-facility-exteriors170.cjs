const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.resolve(__dirname,'..'),P=path.join(R,'preview'),D=path.join(P,'facility-exteriors170');
fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const old=JSON.parse(fs.readFileSync(path.join(P,'facility-exteriors124/manifest.json'),'utf8'));
const themes={
 holox:{material:'metal',label:'남색·보라 금속 패널',face:[85,77,103],top:[34,33,46],accent:[142,113,170]},
 theater:{material:'brick',label:'낡은 자주빛 벽돌·황동 띠',face:[111,82,80],top:[43,34,39],accent:[151,128,90]},
 dev:{material:'metal',label:'청보라 방음 금속 패널',face:[76,75,100],top:[33,33,46],accent:[129,123,158]},
 dining:{material:'plaster',label:'따뜻한 회벽·목재 하단',face:[155,143,119],top:[48,47,42],accent:[160,133,94],wood:true},
 gamers:{material:'tile',label:'낡은 회녹색 역 타일',face:[112,128,123],top:[37,48,48],accent:[127,165,150]},
 fantasy:{material:'concrete',label:'올리브색 운동장 콘크리트',face:[109,116,103],top:[39,45,39],accent:[144,153,114]},
 wheel:{material:'metal',label:'바랜 보랏빛 놀이시설 패널',face:[111,103,120],top:[42,38,48],accent:[154,128,155]},
 market:{material:'tile',label:'세이지색 마트 타일',face:[107,129,114],top:[36,47,42],accent:[151,167,132]},
 mountain:{material:'rock',label:'회갈색 암석 외벽',face:[131,125,108],top:[47,48,42],accent:[157,148,119]}
};
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const maps=old.maps.map(m=>({...m,theme:themes[m.facility],sourceMap:'../city-facilities106/'+m.map,sourceClosed:'../facility-exteriors124/'+m.facility+'-closed124.png',sourceOpen:'../facility-exteriors124/'+m.facility+'-open124.png',decal:'../facility-exteriors124/'+m.decal,closed:m.facility+'-closed170.png',open:m.facility+'-open170.png'}));
const hashes={};for(const m of maps)for(const rel of [m.sourceMap,m.sourceClosed,m.sourceOpen,m.decal])hashes[rel]=hash(path.resolve(D,rel));
fs.writeFileSync(path.join(D,'manifest.json'),JSON.stringify({revision:170,maps,normalWall:121,frontHeight:22,geometryChanged:false,interiorChanged:false,sourceHashes:hashes,nativeIntegrated:false},null,2)+'\n');
console.log(JSON.stringify({revision:170,themedFacilities:maps.length,newMaterials:6}));
