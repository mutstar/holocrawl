(async()=>{
 const manifest=await(await fetch('manifest.json')).json();let direction='horizontal',state='closed',zoom=4;
 function draw(){document.querySelectorAll('[data-variant]').forEach(img=>{img.src=manifest.images[direction][state][img.dataset.variant];img.style.width=`${96*zoom}px`});
  for(const [kind,value] of [['direction',direction],['state',state],['zoom',zoom]])document.querySelectorAll(`button[data-${kind}]`).forEach(b=>b.setAttribute('aria-pressed',String(b.dataset[kind]===String(value))));
  document.getElementById('status').textContent=`${direction==='horizontal'?'가로 벽':'세로 벽'} · ${state==='closed'?'닫힘':'열림'} · ${zoom===1?'원본 크기':zoom+'배 확대'}`;
 }
 document.querySelectorAll('button[data-direction]').forEach(b=>b.onclick=()=>{direction=b.dataset.direction;draw()});
 document.querySelectorAll('button[data-state]').forEach(b=>b.onclick=()=>{state=b.dataset.state;draw()});
 document.querySelectorAll('button[data-zoom]').forEach(b=>b.onclick=()=>{zoom=Number(b.dataset.zoom);draw()});
 draw();window.basicDoor98={manifest,getView:()=>({direction,state,zoom})};window.ready=true;
})().catch(e=>{document.getElementById('status').textContent=e.message;throw e});
