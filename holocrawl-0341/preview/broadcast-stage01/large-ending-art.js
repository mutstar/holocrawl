// All scenery is drawn on the same 32 px grid as the dock floor.
function drawLargeEndingScenery(p, {kind, y: tileY}) {
  function box(x,y,w,h,depth,top,face,side) {
    for (let n=depth;n>0;n--) {
      p(top,x+n,y-n,w,1);
      p(side,x+w+n-1,y-n+1,1,h);
    }
    p(face,x,y,w,h);
  }
  function disc(cx,cy,rx,ry,color) {
    for(let y=-ry;y<=ry;y++) {
      const dx=Math.floor(rx*Math.sqrt(1-y*y/(ry*ry)));
      p(color,cx-dx,cy+y,dx*2+1,1);
    }
  }
  if(kind==='costumes') {
    p('#23202566',4,53,151,8);
    for(const x of [8,142]) {p('#65706b',x,9,4,44);p('#84857a',x-4,53,14,2);p('#393b3c',x-3,56,5,3);}
    p('#aca899',8,8,138,3);
    const colors=['#976f76','#798888','#a78b72','#777788','#927d89'];
    for(let i=0;i<6;i++){
      const x=14+i*20, hem=37+(i%3)*5;
      p('#aba497',x+7,11,2,5);p('#796a60',x+3,15,11,3);
      p(colors[(i+tileY)%5],x+2,18,13,hem-18);
      p(colors[(i+tileY)%5],x,20,17,8);
      p('#493f474a',x+10,26,4,hem-25);p('#dcc9b988',x+3,19,3,7);
    }
  } else if(kind==='wardrobe-case' || kind==='mix-desk') {
    const w=kind==='wardrobe-case'?80:111;
    p('#26232766',6,51,w+5,7);
    box(3,17,w,34,9,'#8b9189','#535f60','#404949');
    if(kind==='wardrobe-case'){
      for(const x of [9,67]) p('#abb0a3',x,17,4,34);
      p('#c4b78e',20,24,15,9);p('#726d61',23,28,8,2);
    } else {
      for(let x=8;x<w-5;x+=24){
        p('#303b40',x,21,19,16);p('#698983',x+2,23,15,6);
        for(let j=0;j<3;j++) p(j===0?'#bc976b':'#838e87',x+j*5,40,3,3);
      }
    }
  } else if(kind==='drive-wheel' || kind==='cable-drum') {
    const gear=kind==='drive-wheel', cx=gear?47:31, rx=gear?38:23;
    box(4,46,2*cx-8,10,5,'#91816d','#63584e','#453f39');
    disc(cx+4,32,rx,21,'#474748');disc(cx,28,rx,21,gear?'#978671':'#9b8066');
    disc(cx,28,rx-5,16,gear?'#4d5555':'#584e44');
    for(let i=0;i<8;i++){
      const angle=i*Math.PI/4;
      for(let n=6;n<rx-4;n+=2) p(gear?'#8b8070':'#807262',cx+Math.round(n*Math.cos(angle)),28+Math.round(n*.52*Math.sin(angle)),3,2);
    }
    disc(cx,28,6,4,'#b3a084');
  } else if(kind==='foley-door') {
    p('#25202266',5,54,53,7);box(3,54,48,5,6,'#968267','#6d5945','#463b33');
    box(7,8,36,46,4,'#ad9370','#80654d','#554b3d');
    for(const y of [13,32]) {p('#554c40',11,y,27,14);p('#947759',13,y+2,23,10);}
    p('#baa77b',33,31,8,3);
  } else if(kind==='boom') {
    p('#25232866',9,52,46,7);
    for(let i=0;i<12;i++){p('#92958a',29-i,44+i,3,2);p('#646e68',31+i,44+i,3,2);}
    p('#747e75',30,14,3,32);
    for(let i=0;i<18;i++) p('#a6aa9d',17+i*2,21-i,3,2);
    p('#434a49',48,3,10,5);p('#7c8580',50,3,6,2);
  }
}

function drawLargeEndingGround(p,ending,x,y) {
  const {id}=ending;
  if(id==='family-bakery') {
    drawBakeryGround(p,ending,x,y);
  } else if(id==='fubuki-er') {
    drawHospitalGround(p,x,y);
  } else if(id==='foley') {
    if(y<10||y>15||x<6||x>38) return;
    if(x<=14) {
      p('#635d52',0,0,32,32);
      for(let i=0;i<15;i++){const dx=(i*17+x*13+y*7)%30,dy=(i*i*3+i*11+x*7)%30;
        p(i%3?'#817a67':'#544f48',dx,dy,3+i%4,2); }
    } else if(x>=21&&x<=29) {
      p('#806b55',0,0,32,32);
      for(let row=0;row<32;row+=8){p('#5b5043',0,row,32,1);p('#a38b69',2,row+1,21,1);}
    } else if(x>=34) {
      p('#596261',0,0,32,32);
      for(let j=2;j<32;j+=8) for(let i=2;i<32;i+=8) p('#89908a',i+(j%16===2?0:3),j,3,2);
    }
  } else if(id==='oozora-police') {
    drawPoliceGround(p,x,y);
  }
}
