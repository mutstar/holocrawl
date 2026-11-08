(async()=>{
 const manifest=await(await fetch('manifest.json')).json();let scene=0,style=manifest.styles[0].id,zoom=manifest.defaultZoom;
 const sceneNav=document.getElementById('sceneNav'),styleNav=document.getElementById('styleNav');
 for(const [i,s] of manifest.scenes.entries()){const b=document.createElement('button');b.textContent=s.label;b.dataset.scene=i;b.onclick=()=>{scene=i;draw()};sceneNav.append(b)}
 for(const s of manifest.styles){const b=document.createElement('button');b.textContent=s.label;b.dataset.style=s.id;b.onclick=()=>{style=s.id;draw()};styleNav.append(b)}
 function draw(){const s=manifest.scenes[scene];document.querySelectorAll('[data-state]').forEach(img=>{img.src=s.images[style][img.dataset.state];img.style.width=`${s.width*zoom}px`});
  document.querySelectorAll('[data-scene]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.scene)===scene)));
  document.querySelectorAll('[data-style]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.style===style)));
  document.querySelectorAll('[data-zoom]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.zoom)===zoom)));
  document.getElementById('status').textContent=`${s.label} · ${zoom===1?'원본 크기':zoom+'배 확대'} · 같은 위치의 닫힘과 열림`;
 }
 document.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>{zoom=Number(b.dataset.zoom);draw()});draw();window.doorReview96={manifest,getView:()=>({scene,style,zoom})};window.ready=true;
})().catch(error=>{document.getElementById('status').textContent=error.message;throw error});
