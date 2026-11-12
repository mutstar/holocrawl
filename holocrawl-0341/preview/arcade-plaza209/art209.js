(function () {
  'use strict';

  function photoBooth() {
    const canvas=document.createElement('canvas');
    canvas.width=canvas.height=96;
    const context=canvas.getContext('2d');
    const fill=(color,x,y,w,h)=>{
      context.fillStyle=color;
      context.fillRect(x,y,w,h);
    };
    fill('#272532',3,85,90,9);
    fill('#2b2635',7,23,82,67);
    fill('#64536f',10,26,76,61);
    fill('#9e7fa2',10,26,76,4);
    fill('#514761',14,31,68,53);
    fill('#342d46',10,38,39,48);
    fill('#4a3f64',13,40,33,40);
    for(let x=14;x<47;x+=5)fill('#745d8c',x,42,2,37);
    fill('#aa89b8',14,42,30,2);
    fill('#9e769f',13,79,33,2);
    fill('#b597ae',51,39,31,38);
    fill('#403b54',54,42,25,19);
    fill('#657c83',56,44,21,15);
    fill('#9eccc4',57,45,17,2);
    fill('#d7bfa0',58,51,8,4);
    fill('#b990b5',68,51,6,4);
    fill('#41364a',56,65,16,6);
    fill('#f0d6b1',58,66,11,5);
    fill('#b995b6',60,67,7,2);
    fill('#5e435d',77,65,2,3);
    fill('#272532',19,14,58,22);
    fill('#a181a5',21,15,54,18);
    fill('#c7a9be',21,15,54,2);
    fill('#55445e',25,19,46,11);
    fill('#e8ccd1',39,20,18,9);
    fill('#e8ccd1',43,18,7,3);
    fill('#735b8c',45,21,6,6);
    fill('#b1d6d0',47,22,2,2);
    fill('#d4b9d1',31,22,3,3);
    fill('#d4b9d1',62,22,3,3);
    return canvas;
  }

  function circuitDoor(context,door) {
    const fill=(color,x,y,w,h)=>{
      context.fillStyle=color;
      context.fillRect(door.x*32+x,door.y*32+y,w,h);
    };
    // 128 x 96 native pixels: joined metal pillars, equal double leaves and
    // a racing gantry. No scaling of the former one-row door.
    fill('#202430',0,0,128,96);
    fill('#414555',2,2,124,92);
    fill('#747f94',2,2,124,3);
    fill('#9b9eb1',4,5,120,2);
    fill('#50596b',4,7,120,24);
    fill('#252e40',20,8,88,20);
    fill('#738696',22,8,84,2);
    fill('#254653',23,11,82,14);
    // A compact pixel-letter sign stays legible without label overlays.
    const glyphs={C:['111','100','100','100','111'],I:['111','010','010','010','111'],R:['110','101','110','101','101'],U:['101','101','101','101','111'],T:['111','010','010','010','010']};
    let dx=37;
    for(const letter of 'CIRCUIT'){
      glyphs[letter].forEach((row,yy)=>{
        [...row].forEach((pixel,xx)=>{if(pixel==='1')fill('#c6f0df',dx+xx*2,13+yy*2,2,2);});
      });
      dx+=8;
    }
    for(const start of [5,111])for(let row=0;row<4;row++)for(let col=0;col<3;col++){
      fill((row+col)%2?'#343946':'#d0c8ae',start+col*4,10+row*4,4,4);
    }
    fill('#829eaa',4,30,120,3);
    fill('#26303e',14,33,100,57);
    // Both pillars meet the existing wall coping and the single sill.
    for(const x of [2,114]){
      fill('#586777',x,33,12,57);
      fill('#9b9eb1',x,33,3,57);
      fill('#303c4a',x+9,33,3,57);
      fill('#2b3d49',x+4,40,4,35);
      fill('#76bfb8',x+4,42,3,29);
      fill('#c0e3ce',x+4,42,3,4);
      for(const y of [35,81])fill('#b3b7b4',x+5,y,2,2);
    }
    for(const x of [17,65]){
      fill('#758e96',x,35,46,53);
      fill('#adc1ba',x,35,46,2);
      fill('#354e5d',x+2,38,42,47);
      fill('#476b78',x+4,40,38,28);
      fill('#638e95',x+4,40,38,2);
      fill('#2a414e',x+4,70,38,13);
      fill('#526876',x+5,72,36,2);
      // Broad forward chevrons, matching the obstacle-course entry cue.
      for(let row=0;row<5;row++){
        const inset=row<3?row:4-row;
        fill('#d4bd7c',x+13+inset*3,47+row*3,9,3);
      }
    }
    fill('#1d303d',63,35,2,53);
    fill('#c1c5b1',58,71,3,9);
    fill('#c1c5b1',67,71,3,9);
    fill('#303b49',0,89,128,7);
    fill('#8e98a4',0,89,128,3);
    fill('#b0b4b4',1,89,126,1);
    for(let x=18;x<110;x+=12)fill('#bb9f68',x,93,6,2);
  }

  window.ArcadeArtAdditions209 = {photoBooth,circuitDoor};
})();
