(function () {
  'use strict';
  const get=id=>document.getElementById(id),course=get('course'),branchCanvas=get('branch-canvas');
  const keys={ArrowUp:'up',w:'up',ArrowDown:'down',s:'down',ArrowLeft:'left',a:'left',ArrowRight:'right',d:'right'};
  const ids=Object.keys(MegaBranch209.maps),storageKey='holocrawl-megacircuit-branches05';
  let circuit=MegaCircuit209.reset(),states=Object.fromEntries(ids.map(id=>[id,MegaBranch209.reset(id)])),active='plaza';
  try{
    const saved=JSON.parse(sessionStorage.getItem(storageKey)||'null');
    if(saved?.version===1||saved?.version===2||saved?.version===3){
      const valid=s=>s&&Number.isInteger(s.pos?.x)&&Number.isInteger(s.pos?.y)&&Number.isInteger(s.turn)&&s.turn>=0;
      if(saved.version===1&&valid(saved.circuit)){
        const p=saved.circuit.pos;
        const wasDoorApproach=p.y<=3&&MegaBranch209.doors.some(d=>p.x>=d.x&&p.x<d.x+d.w);
        if(!wasDoorApproach)saved.circuit.pos={x:p.x,y:p.y+4};
      }
      if(valid(saved.circuit)&&['track','approach','gate'].includes(MegaCircuit209.terrain(saved.circuit.pos.x,saved.circuit.pos.y))&&Number.isInteger(saved.circuit.laps)&&Number.isInteger(saved.circuit.sector)){
        circuit={...circuit,...saved.circuit};
      }
      for(const id of ids){const s=saved.states?.[id];if(valid(s)&&MegaBranch209.terrain(id,s.pos.x,s.pos.y)!=='wall')states[id]={...states[id],...s};}
      if(saved.version<3)states.coaster={...states.coaster,pos:{...MegaBranch209.maps.coaster.start}};
    }
  }catch{}
  function save(){try{sessionStorage.setItem(storageKey,JSON.stringify({version:3,circuit,states}));}catch{}}
  function returnAnchor(id){
    const d=MegaBranch209.doors.find(d=>d.id===id);
    circuit={...circuit,pos:{x:d.x+1,y:3},message:d.name+' 층에서 돌아왔어요.'};
  }
  function render(){
    if(active==='circuit'){
      MegaCircuit209.draw(course,circuit);
      get('score').textContent=circuit.turn+'턴 · '+circuit.laps+'바퀴';
      get('course-message').textContent=circuit.message;
    }else if(ids.includes(active)){
      const map=MegaBranch209.maps[active],state=states[active];
      get('branch-title').textContent=map.title;get('branch-description').textContent=map.description;
      branchCanvas.setAttribute('aria-label',map.title);MegaBranch209.draw(branchCanvas,active,state);
      get('branch-score').textContent=map.w+'×'+map.h+'칸 · '+state.turn+'턴'+(state.visitedBeacon?' · 별빛 표식 발견':'');
      get('branch-message').textContent=state.message;
    }
  }
  function showView(focus,initial=false){
    const hash=location.hash.slice(1),next=hash==='circuit'||ids.includes(hash)?hash:'plaza';
    if(ids.includes(active)&&next==='circuit')returnAnchor(active);
    if(ids.includes(next)&&next!==active){
      returnAnchor(next);
      if(!initial)states[next]={...states[next],pos:{...MegaBranch209.maps[next].start},message:'아래 문으로 메가서킷에 돌아갈 수 있어요.'};
    }
    active=next;get('plaza').hidden=active!=='plaza';get('circuit-floor').hidden=active!=='circuit';
    get('branch-floor').hidden=!ids.includes(active);render();save();
    if(focus)(active==='plaza'?get('enter'):active==='circuit'?course:branchCanvas).focus();
  }
  function move(direction){
    if(active==='circuit'){
      circuit=MegaCircuit209.step(circuit,direction);
      const portal=MegaCircuit209.portalAt(circuit.pos);
      if(portal){location.hash=portal.id;return;}
    }else if(ids.includes(active)){
      states[active]=MegaBranch209.step(active,states[active],direction);
      if(MegaBranch209.terrain(active,states[active].pos.x,states[active].pos.y)==='return'){location.hash='circuit';return;}
    }else return;
    render();save();
  }
  window.addEventListener('hashchange',()=>showView(true));
  get('reset').onclick=()=>{circuit=MegaCircuit209.reset();render();save();course.focus();};
  get('branch-reset').onclick=()=>{if(!ids.includes(active))return;states[active]={...states[active],pos:{...MegaBranch209.maps[active].start},message:'이 층 입구로 돌아왔어요.'};render();save();branchCanvas.focus();};
  for(const button of document.querySelectorAll('[data-move],[data-branch-move]'))button.onclick=()=>move(button.dataset.move||button.dataset.branchMove);
  for(const id of ['circuit-floor','branch-floor'])get(id).addEventListener('keydown',event=>{
    if(event.ctrlKey||event.metaKey||event.altKey)return;
    const direction=keys[event.key]||keys[event.key.toLowerCase()];
    if(direction){event.preventDefault();move(direction);}
  });
  // A read-only snapshot is useful for checking return anchors and independent levels.
  window.MegaBranchNavigation209={getState:()=>JSON.parse(JSON.stringify({active,circuit,states}))};
  showView(location.hash!=='#plaza',true);
})();
