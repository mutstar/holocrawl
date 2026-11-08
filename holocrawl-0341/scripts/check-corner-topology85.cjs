// Screen-space regressions: inside turns must meet a visible face, not a cap gap.
const fs=require('fs'),path=require('path');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const root=path.resolve(__dirname,'..'),output=path.join(root,'analysis/native-corner-audit85');
(async()=>{
 const browser=await chromium.launch({executablePath,headless:true});
 try{
  const page=await browser.newPage();await page.goto(`${previewURL}/city-batch22/?map=0&placement=5110521`);
  await page.waitForFunction(()=>window.ready);
  await page.addScriptTag({path:path.join(root,'preview/city-batch22/wall-joins79.js')});
  await page.addScriptTag({path:path.join(root,'preview/city-batch22/wall-corners84.js')});
  const result=await page.evaluate(()=>{
   const directions=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
   const totals={},failures=[],baselineFailures=[];
   function expect(rule,mask,x,y,solid,expected){
    totals[rule]=(totals[rule]||0)+1;
    const current=cityWallSurface84(solid,1,1,x,y),before=cityWallSurface79(solid,1,1,x,y);
    if(current!==expected)failures.push({rule,mask,pixel:[x,y],expected,actual:current});
    if(before!==expected)baselineFailures.push({rule,mask,pixel:[x,y],expected,actual:before});
   }
   for(let mask=0;mask<256;mask++){
    const cells=new Set(['1,1']);directions.forEach(([dx,dy],i)=>{if(mask&(1<<i))cells.add(`${1+dx},${1+dy}`);});
    const solid=(x,y)=>cells.has(`${x},${y}`),n=solid(1,0),e=solid(2,1),s=solid(1,2),w=solid(0,1);
    // Includes all four rotations of the 3-of-4 L shape among the 256 masks.
    if(!s&&e)for(let y=18;y<32;y++)for(let x=28;x<32;x++)expect('front_reaches_inside_turn',mask,x,y,solid,'front');
    if(!e)for(let y=0;y<32;y++)for(let x=28;x<32;x++)expect('east_face_not_truncated_by_diagonal',mask,x,y,solid,'side');
    if((n||s)&&!w)for(let y=0;y<18;y++)for(let x=0;x<3;x++)expect('west_face_reaches_upper_join',mask,x,y,solid,'west');
    if(s&&!solid(0,2))for(let y=18;y<32;y++)for(let x=0;x<3;x++)expect('west_face_reaches_lower_join',mask,x,y,solid,'west');
    expect('interior_cap_height_retained',mask,16,17,solid,'cap');
    if(!s)expect('front_height_retained',mask,16,18,solid,'front');
   }
   return {status:failures.length?'failed':'passed',neighbourMasks:256,assertions:Object.values(totals).reduce((a,b)=>a+b,0),
    rules:totals,violations:failures,baseline79Violations:baselineFailures.length,baselineExamples:baselineFailures.slice(0,12)};
  });
  fs.writeFileSync(path.join(output,'topology-validation.json'),JSON.stringify(result,null,2)+'\n');
  if(result.status!=='passed')throw Error(`Corner regressions: ${result.violations.length}`);
  if(!result.baseline79Violations)throw Error('Regression checks failed to detect the previous broken joins');
  console.log(JSON.stringify({status:result.status,masks:result.neighbourMasks,assertions:result.assertions,violations:result.violations.length,previousVersionViolations:result.baseline79Violations}));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
