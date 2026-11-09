// A facility facade and a modest lounge, between ornate133 and sparse134.
const fs=require('fs'),path=require('path'),R=path.resolve(__dirname,'..'),S=path.join(R,'preview/holohome134'),D=path.join(R,'preview/holohome135');
fs.mkdirSync(D,{recursive:true});
let gen=fs.readFileSync(path.join(S,'generator134.js'),'utf8').replaceAll('134','135').replace('restrained lounge','distinct facade with modest lounge');
gen=gen.replace("m.props=[prop('sofa',3,4,3,1),prop('coffee',4,6,2,1),prop('tv',9,3,2,2,{source:[0,0,60,96]}),prop('planter',1,8,2,1)];", "m.props=[prop('sofa',3,4,3,1),prop('coffee',4,6,2,1),prop('sofa',3,8,3,1),prop('bookcase',1,3,2,1),prop('tv',9,4,3,2),prop('planter',1,8,2,1),prop('planter',10,8,2,1)];");
fs.writeFileSync(path.join(D,'generator135.js'),gen);
let material=fs.readFileSync(path.join(R,'preview/holohome133/materials133.js'),'utf8').replaceAll('133','135');
// Retain the approved tile silhouette and dark contours, with worn ivory front faces.
material=material.replace("[214+l*.11,207+l*.10,182+l*.08]","[172+l*.11,165+l*.10,144+l*.08]").replace('[155+l*.14,168+l*.12,157+l*.10]','[91+l*.14,107+l*.12,103+l*.10]').replace('[239,232,206]','[209,199,172]').replace('[155,156,135]','[129,127,108]');
const f0=material.indexOf(' function floors()'),f1=material.indexOf(' function wall(',f0);
material=material.slice(0,f0)+` function floors(){return settings.floorTiles.map(base=>{const c=make(),q=c.getContext('2d');q.drawImage(base,0,0);q.fillStyle='rgba(168,158,132,.40)';q.fillRect(0,0,32,32);return c;});}\n`+material.slice(f1);
const p0=material.indexOf(' function paint('),p1=material.indexOf(' function door(',p0);
material=material.slice(0,p0)+` function paint(q,m){const h=m.home;if(!h)return;const x=h.x*32,y=h.y*32;
  // A compact central lounge rather than a room-filling palace set.
  q.fillStyle='#647a70';q.fillRect(x+2*32+5,y+4*32+2,5*32-10,5*32-4);q.strokeStyle='#a29a78';q.lineWidth=1;q.strokeRect(x+2*32+8.5,y+4*32+5.5,5*32-17,5*32-11);
  for(const wx of [3,9])window(q,x+wx*32,y);
  for(const wx of [2,10])window(q,x+wx*32,y+10*32);
  // Low stone threshold meets the entry sprite and has the same one-cell passage.
  q.fillStyle='#8d8977';q.fillRect(x+5*32+3,y+10*32+29,3*32-6,3);
  for(const wx of [4,8]){const xx=x+wx*32;q.fillStyle='#303c3a';q.fillRect(xx+11,y+10*32+14,10,13);q.fillStyle='#c9b27a';q.fillRect(xx+13,y+10*32+16,6,8);q.fillStyle='#e1d2a4';q.fillRect(xx+14,y+10*32+17,3,2);}
 }\n`+material.slice(p1);
fs.writeFileSync(path.join(D,'materials135.js'),material);
let app=fs.readFileSync(path.join(S,'app134.js'),'utf8').replaceAll('134','135');
app=app.replace("['stairs','sofa','coffee','tv','planter']","['stairs','entrance','sofa','coffee','tv','planter','bookcase']");
app=app.replace("things.push({type:'player'", "if(m.home)things.push({type:'entrance',x:m.home.x+5,y:m.home.y+9.5,bottom:(m.home.y+11)*32});things.push({type:'player'");
app=app.replace("$('landing').onclick=", "$('entry').onclick=()=>{current=1;const m=get().map;focus({x:m.entrance.x,y:m.entrance.y+1});};$('landing').onclick=");
fs.writeFileSync(path.join(D,'app135.js'),app);
let html=fs.readFileSync(path.join(S,'index.html'),'utf8').replaceAll('134','135').replace('홀로홈 · 기존 던전에 맞춘 소박한 라운지','홀로홈 · 고유 입구와 아담한 공용 라운지').replace('큰 계단·창·기둥은 덜어내고 파란 소파, 작은 테이블, TV와 화분만 남겼습니다.','전용 아치 입구·양옆 조명·민트 창틀과 낡은 상아색 외벽을 살렸습니다. 내부는 파란 소파 두 개, 작은 테이블·책장·TV로 꾸몄습니다.');
html=html.replace('<button id="landing">','<button id="entry">입구 가까이</button><button id="landing">');
const a=html.indexOf('<div class="cards">'),b=html.indexOf('<footer>',a);
html=html.slice(0,a)+'<div class="cards"><section class="card"><h2>고정지형다운 입구·외벽</h2><p>상아색 몰딩과 민트 창틀, 남색 포인트의 전용 아치 입구·작은 벽 조명. 입구와 외벽이 같은 높이로 이어집니다.</p><p><a href="entrance-closed135.png">닫힌 입구 확대</a> · <a href="entrance-open135.png">열린 입구 확대</a></p></section><section class="card"><h2>공용 라운지의 특징만</h2><p>마주 보는 파란 소파·작은 테이블·책장·TV·화분. 거대한 양갈래 계단·발코니·기둥은 넣지 않았습니다.</p><p>13×11칸과1층 확정 출현, 중앙 뒤쪽 전용 내려가는 계단·2층 왕복 유지.</p></section></div><p><a href="../holohome133/">장식이 많았던133</a> · <a href="../holohome134/">너무 단순했던134</a> · <a href="../facility-exteriors124/">기존 고정지형들과 비교</a></p>'+html.slice(b);
fs.writeFileSync(path.join(D,'index.html'),html);
let check=fs.readFileSync(path.join(R,'scripts/check-holohome134.cjs'),'utf8').replaceAll('134','135').replace("['stairs','sofa','coffee','tv','planter']","['stairs','entrance','sofa','coffee','tv','planter','bookcase']").replace('assert.equal(assets.length,5)','assert.equal(assets.length,7)');
// Test both open states and source rectangles used as a sprite-atlas region.
check=check.replace("await save('home135.png',2);",`const facade=await p.evaluate(()=>{const a=holoHome135,m=a.getMap(),c=document.getElementById('field');a.stop();a.getState().opened.delete(m.doors.find(d=>d.entrance).id);a.draw();const x=(m.home.x+4-(m.home.x-3))*32,y=(m.home.y+9-(m.home.y-2))*32;const crop=()=>{const o=document.createElement('canvas');o.width=160;o.height=128;const g=o.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(c,x,y,160,128,0,0,160,128);return o.toDataURL();};const closed=crop();a.getState().opened.add(m.doors.find(d=>d.entrance).id);a.draw();const opened=crop();a.getState().opened.delete(m.doors.find(d=>d.entrance).id);a.draw();for(const prop of m.props){if(prop.source){const [sx,sy,w,h]=prop.source,im=a.images[prop.type];if(sx<0||sy<0||sx+w>im.width||sy+h>im.height)throw Error('sprite source overflow');}}return{closed,opened};});assert.notEqual(facade.closed,facade.opened);for(const state of ['closed','opened'])fs.writeFileSync(path.join(D,'entrance-'+(state==='opened'?'open':state)+'135.png'),Buffer.from(facade[state].split(',')[1],'base64'));await save('home135.png',2);`);
check=check.replace('restrainedLounge:true','balancedFacility:true,entranceOpenCloseChangesPixels:true');
fs.writeFileSync(path.join(R,'scripts/check-holohome135.cjs'),check);
fs.writeFileSync(path.join(D,'art135.json'),JSON.stringify({revision:135,mode:'existing-native-sprites-and-code-native-materials',reference:'../holohome133/prompts.json',newImageGeneration:false,footprint:[13,11],kept:['custom entrance','mint windows','aged ivory facade','two blue sofas','coffee table','bookcase','TV','planters'],omitted:['grand staircase backdrop','balcony','giant columns','kotatsu','noticeboard'],nativeIntegrated:false},null,2)+'\n');
console.log('Built balanced HoloHome135 and open/closed facade checks.');
