const fs=require('fs'),path=require('path'),crypto=require('crypto');const R=path.resolve(__dirname,'..'),old=path.join(R,'preview/fortune165'),D=path.join(R,'preview/fortune166');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const specs=JSON.parse(fs.readFileSync(path.join(old,'prompts.json'),'utf8')).assets,hashes={};for(const s of specs){const n=s.id+'-native.png',src=path.join(old,'assets',n);fs.copyFileSync(src,path.join(D,'assets',n));hashes[n]=crypto.createHash('sha256').update(fs.readFileSync(src)).digest('hex');}
const read=n=>fs.readFileSync(path.join(old,n),'utf8');let app=read('app165.js').replaceAll('FortuneLayout165','FortuneLayout166').replaceAll('FortuneArt165','FortuneArt166').replaceAll('fortune165Ready','fortune166Ready');
const a=app.indexOf('function drawWires()'),b=app.indexOf('function drawEntrance()');app=app.slice(0,a)+app.slice(b);
app=app.replace('drawWires();drawEntrance();','FortuneFixtures166.ground(q,m);drawEntrance();');
app=app.replace("for(const p of m.props)drawProp(p);for(const k", "for(const p of m.props)drawProp(p);FortuneFixtures166.front(q,m);for(const k");
app=app.replace('다섯 장치를 잇는 중계 로비','뒤쪽 무대 · 왼쪽 작업대 · 오른쪽 안내 부스');
fs.writeFileSync(path.join(D,'app166.js'),app);
let html=read('index.html').replaceAll('165','166').replace('<h1>포춘 네트워크 · Myth 중계 로비</h1>','<h1>포춘 네트워크 · 무대와 작업 공간</h1>');
html=html.replace('13×11칸의 넓은 로비와 짧은 진입 통로. 청록색 둥근 입구·LED 중계 데스크를 두고, Myth 5명의 장치를 둘레에 연결했습니다. 다섯 멤버 장치는 모두 64×64px입니다.','소품 도트는 유지하고 공간을 다시 묶었습니다. 뒤쪽은 칼리·키아라와 공용 데스크가 있는 무대, 왼쪽은 이나·아메의 공용 작업대, 오른쪽은 구라 안내 부스입니다. 입구에서 무대까지 중앙 통로를 비웠습니다.');
html=html.replace('바닥 연결선은 통행 가능한 장식입니다.','바닥의 연결선 도식은 없앴습니다. 무대와 중앙 통로는 걸을 수 있고, 작업대·부스는 통과할 수 없습니다.');
html=html.replace('입구·장치 도트만 크게 보기 →','유지한 입구·장치 도트 보기 →').replace('href="assets.html"','href="../fortune165/assets.html"');
html=html.replace('<details>','<p><a href="../fortune165/">이전165 배치 비교</a></p><details>');
html=html.replace('내장 imagegen 제작 프롬프트','기존 도트 제작 프롬프트').replace('href="prompts.json"','href="../fortune165/prompts.json"');
html=html.replace('src="layout166.js"','src="../fortune165/layout165.js"></script><script src="layout166.js"');
html=html.replace('src="walls166.js"','src="../fortune165/walls165.js"').replace('<script src="app166.js">','<script src="fixtures166.js"></script><script src="app166.js">');
fs.writeFileSync(path.join(D,'index.html'),html);
fs.writeFileSync(path.join(D,'plan.json'),JSON.stringify({revision:166,base:165,status:'user-review',scope:'Spatial composition and integrated fixtures; no sprite regeneration',footprint:[13,11],boundaryCellsChanged:false,collisionsChangedForFixtures:true,approvedPromise164SourceHashes:JSON.parse(read('plan.json')).approvedPromise164SourceHashes,unchangedNativeSprites:hashes,zones:['shared rear stage: calli/hub/kiara','shared west workbench: ina/ame','east reception: gura','open three-cell main aisle'],removed:'floor network diagram and detached five-corner arrangement',nativeIntegrated:false},null,2)+'\n');
console.log(JSON.stringify({revision:166,unchangedNativeSprites:7,newAISprites:0}));
