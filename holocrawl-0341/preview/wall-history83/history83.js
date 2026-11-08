(async()=>{
 const manifest=await(await fetch('manifest.json')).json(),images=new Map();let full=false,selected;
 await Promise.all(manifest.stages.map(stage=>new Promise((resolve,reject)=>{
  const image=new Image();image.onload=()=>{images.set(stage.id,image);resolve();};image.onerror=()=>reject(Error(stage.image));image.src=`${stage.image}?v=${stage.sha256.slice(0,12)}`;
 })));
 const latest=manifest.stages.find(stage=>stage.latest),history=manifest.stages.filter(stage=>!stage.latest);
 const grid=document.getElementById('history'),targets=[];
 const draw=(canvas,id)=>{
  const image=images.get(id),r=manifest.crop;
  canvas.width=full?manifest.mapWidth*32:r.width*32;canvas.height=full?manifest.mapHeight*32:r.height*32;
  const c=canvas.getContext('2d');c.imageSmoothingEnabled=false;
  if(full)c.drawImage(image,0,0);else c.drawImage(image,r.x*32,r.y*32,r.width*32,r.height*32,0,0,canvas.width,canvas.height);
 };
 const redraw=()=>{for(const [canvas,id]of targets)draw(canvas,id);if(selected){draw(document.getElementById('old-large'),selected.id);draw(document.getElementById('new-large'),latest.id);}};
 const open=stage=>{
  selected=stage;document.getElementById('old-title').textContent=stage.title;document.getElementById('old-note').textContent=stage.note;
  draw(document.getElementById('old-large'),stage.id);draw(document.getElementById('new-large'),latest.id);document.getElementById('comparison').showModal();
 };
 history.forEach((stage,index)=>{
  const article=document.createElement('article'),badge=document.createElement('span'),title=document.createElement('h2'),button=document.createElement('button'),canvas=document.createElement('canvas'),note=document.createElement('p'),tools=document.createElement('div'),compare=document.createElement('button');
  badge.className='badge old';badge.textContent=`이전 벽 ${String(index+1).padStart(2,'0')}`;title.textContent=stage.title;
  button.className='image-button';button.setAttribute('aria-label',`${stage.title} 최신과 비교`);canvas.setAttribute('aria-label',stage.title);button.append(canvas);button.onclick=()=>open(stage);
  note.textContent=stage.note;tools.className='tools';compare.textContent='최신과 나란히 보기';compare.onclick=()=>open(stage);tools.append(compare);
  article.append(badge,title,button,note,tools);grid.append(article);targets.push([canvas,stage.id]);
 });
 targets.push([document.getElementById('latest'),latest.id]);
 for(const name of ['crop','full'])document.getElementById(name).onclick=()=>{
  full=name==='full';document.getElementById('crop').setAttribute('aria-pressed',!full);document.getElementById('full').setAttribute('aria-pressed',full);redraw();
 };
 document.getElementById('close').onclick=()=>document.getElementById('comparison').close();
 document.getElementById('count').textContent=`이전 ${history.length}종 + 최신 1종`;
 document.getElementById('latest-title').textContent=latest.title;
 document.getElementById('summary').textContent=`같은 랜덤 지도·같은 바닥·같은 확대 위치에서 벽만 비교합니다. 시드 ${manifest.seed}.`;
 redraw();window.wallHistory83={manifest,getMode:()=>full?'full':'crop'};window.ready=true;
})().catch(error=>{document.getElementById('summary').textContent=`불러오기 실패: ${error.message}`;throw error;});
