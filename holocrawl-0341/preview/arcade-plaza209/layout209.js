(function () {
  'use strict';

  function generate(mode) {
    const map = ArcadeLayout194.generate(mode);
    const {x,y} = map.origin;
    const photo = {id:'photo',label:'메가프리',x:x+6,y:y+1,w:3,h:3};
    map.props.push(photo);
    for(let row=photo.y;row<photo.y+photo.h;row++) {
      for(let col=photo.x;col<photo.x+photo.w;col++) map.open[row*map.w+col]=0;
    }
    // A closed, wall-mounted gateway, with a clear approach one row below it.
    map.circuit = {label:'메가서킷 대문',x:x+12,y:y-1,w:4,h:3};
    for(let row=map.circuit.y;row<map.circuit.y+map.circuit.h;row++) {
      for(let col=map.circuit.x;col<map.circuit.x+map.circuit.w;col++) {
        const index=row*map.w+col;
        map.cells[index]=0;
        map.building[index]=true;
        map.inner[index]=false;
        map.open[index]=0;
      }
    }
    map.servicePoints.push(
      {id:'photo',x:photo.x+1,y:photo.y+photo.h},
      {id:'circuit',x:map.circuit.x+1,y:map.circuit.y+map.circuit.h},
    );
    return map;
  }

  window.ArcadeLayout209 = {...ArcadeLayout194,generate};
})();
