// Atlas input preparation only: reuse approved artwork and browser drawing rules.
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const root=path.resolve(__dirname,'..'),rl=path.join(root,'engine/upstream/crawl-ref/source/rltiles'),out=path.join(rl,'holocrawl');fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await b.newPage();await p.goto('http://127.0.0.1:8797/street-vision01/');await p.waitForFunction(()=>window.previewReady);
 const assets=await p.evaluate(async()=>{
   const load=s=>new Promise((r,j)=>{let i=new Image;i.onload=()=>r(i);i.onerror=j;i.src='assets/'+s});
   const [ref,floor,up,down,fence]=await Promise.all(['scene-reference.png','cement-reference.png','stairs-up12-32.png','stairs-down06-32.png','fence-cutout32.png'].map(load));
   const result={},c=document.createElement('canvas');c.width=c.height=32;let ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;
   function start(){ctx.clearRect(0,0,32,32);ctx.filter='none';}
   function tex(im,r,x=0,y=0,w=32,h=32){ctx.drawImage(im,...r,x,y,w,h);}
   function save(name){result[name]=c.toDataURL('image/png').split(',')[1];}
   for(const [n,r]of [[0,[270,150,32,32]],[1,[285,153,32,32]],[2,[160,300,32,32]],[3,[260,300,32,32]]]){start();tex(floor,r);save('holo_street_floor'+n);}
   for(let decor=0;decor<5;decor++)for(let mask=0;mask<16;mask++){
     start();tex(ref,[112,54,16,16]);ctx.fillStyle='rgba(11,13,15,.60)';ctx.fillRect(0,0,32,32);
     if(mask&4){ctx.filter='brightness(1.35)';tex(ref,[130,62,24,25],0,32*.08,32,32*.92);ctx.filter='none';ctx.fillStyle='#625d54';ctx.fillRect(0,32*.27,32,1);ctx.fillStyle='#171714';ctx.fillRect(0,32*.94,32,32*.06);}
     if(mask&8){ctx.fillStyle='#5c574d';ctx.fillRect(0,0,32*.06,32);}if(mask&2){ctx.fillStyle='#3e3b34';ctx.fillRect(32*.94,0,32*.06,32);}if(mask&1){ctx.fillStyle='#35332c';ctx.fillRect(0,0,32,32*.05);}
     ctx.filter='brightness(1.35)';
     if(decor===1)tex(ref,[289,34,37,19],0,4,32,19);
     if(decor===2){ctx.filter='none';ctx.beginPath();ctx.moveTo(3,4);ctx.lineTo(19,4);ctx.lineTo(19,27);ctx.strokeStyle='#222526';ctx.lineWidth=4;ctx.stroke();ctx.strokeStyle='#92938b';ctx.lineWidth=2;ctx.stroke();ctx.fillStyle='#535750';ctx.fillRect(16,12,5,2);ctx.fillRect(16,21,5,2);}
     if(decor===3)tex(ref,[294,86,22,16],4,9,23,17);if(decor===4)tex(ref,[183,31,32,12],0,5,32,12);
     ctx.filter='none';save('holo_street_wall'+(mask+decor*16));
   }
   const whole=document.createElement('canvas');whole.width=128;whole.height=64;const wc=whole.getContext('2d');wc.imageSmoothingEnabled=false;wc.drawImage(ref,326,57,105,73,0,0,128,64);
   for(let y=0;y<2;y++)for(let x=0;x<4;x++){start();ctx.drawImage(whole,x*32,y*32,32,32,0,0,32,32);save('holo_street_wall'+(80+y*4+x));}
   for(const[name,im]of [['up12',up],['down06',down]]){start();ctx.drawImage(im,0,0);save('holo_street_'+name);}
   start();ctx.drawImage(fence,0,10,32,22);save('holo_street_fence');return result;
 });
 for(const[name,data]of Object.entries(assets))fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(data,'base64'));
 for(const[type,names]of [['floor',Array.from({length:4},(_,i)=>'holo_street_floor'+i)],['wall',Array.from({length:88},(_,i)=>'holo_street_wall'+i)],['feat',['holo_street_up12','holo_street_down06','holo_street_fence']]]){
   const file=path.join(rl,'dc-'+type+'.txt'),marker='# HOLOCRAWL STREET01';let text=fs.readFileSync(file,'utf8');text=text.split(marker)[0].trimEnd();
   fs.writeFileSync(file,text+'\n\n'+marker+'\n%sdir holocrawl\n%back none\n%rim 0\n%shrink 0\n%weight 10\n'+names.map(n=>n+' '+n.toUpperCase()).join('\n')+'\n');
 }
 console.log('Prepared '+Object.keys(assets).length+' approved terrain atlas inputs.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
