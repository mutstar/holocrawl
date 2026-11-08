// Re-render preserved wall implementations on the same current native floor.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),output=path.join(root,'preview/wall-history83');
const native=JSON.parse(fs.readFileSync(path.join(root,'preview/city-random82/map.json'),'utf8'));
const stages=[
 {id:'original',title:'초기 · 갈색 전면',file:'scripts/wall-volume01-before02.js',original:true,note:'얇은 벽 입체감 수정 전'},
 {id:'volume01',title:'입체감 01',file:'scripts/wall-volume01-before02.js',note:'한 줄 벽의 윗면·옆면 추가'},
 {id:'gray02',title:'회색 콘크리트 02',file:'scripts/wall-volume02-before03.js',note:'갈색 정면 대신 회색 재질'},
 {id:'connected03',title:'연결 벽 통일 03',file:'scripts/wall-volume03-before04.js',note:'모서리·갈림길을 같은 재질로 통일'},
 {id:'corner04',title:'모서리 정렬 04',file:'scripts/wall-volume04-before05.js',note:'대각 모서리와 옆면 명암 수정'},
 {id:'wear05',title:'균열 추가 05',file:'scripts/wall-wear05-before06.js',note:'초기 균열·마모 변형'},
 {id:'wear06',title:'자연스러운 잔금 06',file:'scripts/wall-palette-gray-before08.js',note:'균열의 모양과 대비를 자연스럽게 수정'},
 {id:'local10',title:'갈색 복원 · 국소 벽 10',file:'scripts/wall-local10-before11.js',note:'기존 큰 벽을 유지하고 얇은 벽만 수정'},
 {id:'local11',title:'국소 벽 11',file:'scripts/wall-local11-before13.js',note:'상하로 이어지는 얇은 벽의 연결 수정'},
 {id:'cap13',title:'어두운 윗면 13',file:'scripts/wall-local13-before20.js',note:'한 칸 벽도 큰 벽과 같은 어두운 윗면'},
 {id:'shade20',title:'ㄱ자 명암 20',file:'preview/city-batch22/wall-volume.js',note:'동쪽 옆면 명암을 조정한 기존 도시 벽'},
 {id:'depth80',title:'전역 명암 80 · 되돌린 안',file:'preview/city-batch22/wall-volume.js',extra:'analysis/city-wall81/edge-preview80.js',note:'모든 벽의 위·왼쪽에 추가 명암을 넣었던 시안'},
 {id:'join79',title:'연결 수정 79 · 이전 기본 벽',file:'preview/city-batch22/wall-joins79.js',saved:'preview/wall-history83/assets/join79.png',note:'접합부 재수정 전 기본 벽'},
 {id:'latest',title:'최신 · 접합부 수정 84',note:'윗면 돌출 제거 · 안쪽 측면 연결',latest:true},
];
const digest=buffer=>crypto.createHash('sha256').update(buffer).digest('hex');
(async()=>{
 fs.mkdirSync(path.join(output,'assets'),{recursive:true});
 // Find one crop with plenty of corners, narrow walls and floor for all versions.
 let crop={x:20,y:20,width:22,height:16},best=-Infinity;
 const wall=(x,y)=>native.rows[y]?.[x]==='#';
 for(let y=3;y<native.height-19;y++)for(let x=3;x<native.width-25;x++){
  let score=0,open=0;
  for(let yy=y;yy<y+16;yy++)for(let xx=x;xx<x+22;xx++){
   if(!wall(xx,yy)){open++;continue;}
   const n=wall(xx,yy-1),e=wall(xx+1,yy),s=wall(xx,yy+1),w=wall(xx-1,yy),count=+n+e+s+w;
   if(count===0)score+=14;else if(count===1)score+=7;else if(count===2&&!(n&&s||e&&w))score+=4;else if(count===3)score+=1;
  }
  if(open<100||open>290)continue;if(score>best){best=score;crop={x,y,width:22,height:16};}
 }
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  let cursor=0;const checks=[];
  async function worker(){
   while(cursor<stages.length){
    const stage=stages[cursor++],page=await browser.newPage();
    try{
     if(stage.latest||stage.saved){
      const bytes=fs.readFileSync(path.join(root,stage.saved||'preview/city-random82/full-map.png'));
      stage.image=`assets/${stage.id}.png`;fs.writeFileSync(path.join(output,stage.image),bytes);stage.sha256=digest(bytes);continue;
     }
     const body=fs.readFileSync(path.join(root,stage.file),'utf8');
     stage.sourceSha256=digest(Buffer.from(body));
     await page.route('**/city-batch22/wall-volume.js*',route=>route.fulfill({contentType:'application/javascript',body}));
     await page.goto(`${previewURL}/city-batch22/?map=0&placement=5110521`);
     await page.waitForFunction(()=>window.ready,{},{timeout:20000});
     if(stage.extra){stage.extraSha256=digest(fs.readFileSync(path.join(root,stage.extra)));await page.addScriptTag({path:path.join(root,stage.extra)});}
     const result=await page.evaluate(async({native,original})=>{
      fixtures=[];fences=[];mounted=[];wallRuns.clear();
      const previousRun=wallRun;wallRun=(...args)=>{const run=previousRun(...args);run.decor=-1;return run;};drawHorizontalPipe09=()=>{};
      if(original)wallVolumeEnabled=false;
      const load=src=>new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=reject;image.src=src;});
      const atlas={};for(const name of ['floor','wall','feat'])atlas[name]=await load(`../city-random82/assets/${name}.png?v=${native.seed}`);
      const canvas=document.createElement('canvas');canvas.width=native.width*32;canvas.height=native.height*32;
      const c=canvas.getContext('2d');c.imageSmoothingEnabled=false;
      const draw=(index,x,y)=>{const t=native.palette[index];c.drawImage(atlas[t.atlas],t.sx,t.sy,t.width,t.height,x*32+t.dx,y*32+t.dy,t.width,t.height);};
      for(let y=0;y<native.height;y++)for(let x=0;x<native.width;x++){const i=y*native.width+x;draw(native.floors[i],x,y);draw(native.features[i],x,y);}
      const before=c.getImageData(0,0,canvas.width,canvas.height).data;
      const palette=['floor','rock_wall','closed_door','granite_statue'];
      const map={seed:String(native.seed),w:native.width,h:native.height,palette,rows:native.rows.map(row=>[...row].map(f=>f==='#'?1:f==='+'?2:f==='G'?3:0))};
      for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++)if(native.rows[y][x]==='#'){
       c.save();c.beginPath();c.rect(x*32,y*32,32,32);c.clip();
       (original?originalCityTile:tile)(c,map,x,y,x*32,y*32,32,'fit',false,false);c.restore();
      }
      const after=c.getImageData(0,0,canvas.width,canvas.height).data;let outside=0;
      for(let y=0;y<map.h;y++)for(let x=0;x<map.w;x++)if(native.rows[y][x]!=='#'){
       for(let py=0;py<32;py++)for(let px=0;px<32;px++){const i=((y*32+py)*canvas.width+x*32+px)*4;if([0,1,2,3].some(k=>before[i+k]!==after[i+k]))outside++;}
      }
      if(outside)throw Error('A wall renderer changed non-wall pixels: '+outside);
      return {png:canvas.toDataURL().split(',')[1],nonWallPixelsChanged:outside};
     },{native,original:!!stage.original});
     const bytes=Buffer.from(result.png,'base64');stage.image=`assets/${stage.id}.png`;stage.sha256=digest(bytes);
     fs.writeFileSync(path.join(output,stage.image),bytes);checks.push({id:stage.id,nonWallPixelsChanged:result.nonWallPixelsChanged});
     console.log(`Rendered ${stage.id} on seed ${native.seed}.`);
    }finally{await page.close();}
   }
  }
  await Promise.all([worker(),worker()]);
  fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify({seed:native.seed,mapWidth:native.width,mapHeight:native.height,crop,
   sourceMapSha256:digest(fs.readFileSync(path.join(root,'preview/city-random82/map.json'))),
   description:'Preserved wall renderers reconstructed on the same current native map. Floor and non-wall features are identical.',stages},null,2)+'\n');
  fs.writeFileSync(path.join(output,'validation.json'),JSON.stringify({status:'passed',stages:stages.length,reconstructed:checks.length,nonWallPixelsChanged:0,checks},null,2)+'\n');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
