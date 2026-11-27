// All dimensions are native pixels. The gate's center is the walkable entry tile.
function drawGarageShutter(p) {
  const poly=(c,pts)=>policePolygon(p,c,pts);
  const dark='#343039', trim='#97899e';
  p(dark,-22,-4,76,10); p('#786b80',-21,-4,74,2);
  for(const x of [-19,36]) {
    p('#504b50',x,6,15,24); p('#827d78',x,6,2,23);
    for(let y=11;y<28;y+=5)p('#655f60',x+3,y,11,2);
  }
  for(const x of [-2,31]) {p(dark,x,5,3,26); p(trim,x,6,1,24);}
  poly(dark,[[-7,-2],[-8,-16],[2,-13],[9,-8],[22,-8],[34,-16],[37,-11],[36,0]]);
  poly('#887596',[[-4,-3],[-5,-12],[6,-7],[23,-6],[33,-12],[32,-2]]);
  p('#b59ab4',-3,-10,3,3);p('#c0a6ba',29,-9,3,3);
  p('#c6b895',8,-4,3,2);p('#c6b895',21,-4,3,2);p('#564957',14,-2,4,2);
  for(let y=4;y<=10;y+=3){p('#514956',1,y,30,3);p(trim,2,y,28,1);}
}

function drawGarageGround(p,x,y) {
  if(x>=14 && x<=33 && y>=3 && y<=12) {
    p('#343d4045',0,0,32,32);
    if(x===17||x===26) {
      if(y>=4 && y<=8)p('#ab956860',x===17?24:6,0,3,32);
    }
    if(y===8 && x>=18 && x<=25)p('#ab956870',0,27,32,3);
    // A recessed service trench is visible between and below the raised wheels.
    if(x>=19 && x<=22 && y>=6 && y<=8) {
      const left=x===19?9:0, right=x===22?24:32;
      const top=y===6?20:0, bottom=y===8?17:32;
      p('#363737',left,top,right-left,bottom-top);
      if(x===19 || x===22)p('#716d60',x===19?9:22,top,2,bottom-top);
      if(y===8){
        p('#767263',left,16,right-left,2);
        for(let i=left+2;i<right-2;i+=8)p('#50524c',i,3,3,11);
      }
    }
    if(y===9 && x>=18 && x<=24 && x%2===0){
      p('#393936',6,9,15,4);p('#414340',3,12,11,3);p('#6b6960',17,9,4,1);
    }
    if(y===6 && x>=26 && x<=28) p('#46423c',0,19,32,2);
  } else if(x>=16 && x<=35 && y>=15 && y<=21) {
    p('#48626652',0,0,32,32); p('#80938b28',0,0,32,1);
    if(y===20) {
      p('#414b49',0,11,32,8);p('#88938b',0,11,32,1);
      for(let i=2;i<32;i+=6)p('#68716b',i,13,2,4);
    }
    // The loose hose runs from the reel down to the trench drain.
    if(x===28 && y>=17 && y<=20) {
      const bend=[12,19,25,18][y-17];
      p('#353e40',bend,y===17?13:0,3,y===17?19:y===20?12:32);
      if(y<20) {
        const next=[19,25,18][y-17];
        p('#353e40',Math.min(bend,next),29,Math.abs(next-bend)+3,3);
      }
    }
    if((x===27 && y===18)||(x===29 && y===19)){p('#505d5e',3,20,21,4);p('#697a79',7,20,11,1);}
  } else if(x>=4 && x<=8 && y>=17 && y<=23) {
    if(x===5 || x===7){
      for(let i=2;i<32;i+=8) {
        const dx=x===5?19:5;
        p('#34353576',dx,i,7,3);p('#41413d88',dx+4,i+3,4,2);
      }
    }
  } else if(x>=39 && y<=10) {
    p('#88775d34',0,0,32,32);
  } else if((y===17||y===18) && x>9 && x<16) {
    for(let i=2;i<32;i+=9)p('#3c3a3a65',i,16,5,2);
  }
}

// Hand-placed clusters on a 2 px grid. Dots leave the underlying floor visible.
const garageInks = {
  k:'#26292c', d:'#393c3c', s:'#515854', m:'#78817c', h:'#b1b6a5',
  v:'#574957', p:'#80657e', l:'#ad8fa5', w:'#d0cbb4',
  b:'#435a63', a:'#668694', i:'#9db8b6',
  r:'#714d43', t:'#a36c52', y:'#b59963', n:'#796953', g:'#819b83',
};
function drawGarageScenery(p,{kind,width,depth}) {
  const W=width*16,H=depth*16;
  const rect=(c,x,y,w,h)=>p(garageInks[c]||c,x*2,y*2,w*2,h*2);
  function stamp(x,y,pattern) {
    const rows=Array.isArray(pattern)?pattern:pattern.split('/');
    rows.forEach((row,j)=>{
      for(let i=0;i<row.length;) {
        const c=row[i];let end=i+1;
        while(row[end]===c)end++;
        if(c!=='.')rect(c,x+i,y+j,end-i,1);
        i=end;
      }
    });
  }
  function shadow(x,y,w) {
    rect('#22232468',x+2,y,w-2,3);rect('#25252548',x+w-4,y+2,6,2);
  }
  function casework(x,y,w,h,face) {
    rect('k',x,y+2,w,h-2);rect('s',x+1,y,w-3,3);rect('h',x+2,y,w-6,1);
    rect(face,x+1,y+3,w-4,h-5);rect('d',x+w-3,y+2,2,h-3);
  }
  const wheel='..ddddd../.dssmssdk/dskdddkdk/ksdmmmdsk/ksdmhmdsk/kddmmmdsk/.dkdddkd./..dkkkd..';
  const hub='..nnn../.nmhmn./nmkkhmn/nhmdmhn/.nmhmn./..nnn..';
  const motor='....mmmmm...../.mmhmhmhmd..../.sdsdsdsds.mm./kdmmmmmmmsdsmk/ksmhdhdhdssdkk/kmsssssssmdsk./.dsdndndsdsk../..kkdddkkk....';
  const rice='...wwww.../..wwhwww../.whwwwhww./wwwdddwhww/whwkkkwwhw/.hhkkkhhh.';
  const shadowFoot=H-4;
  if(kind==='lift') {
    shadow(8,41,76);
    for(const x of [9,77]){
      rect('d',x-2,40,10,3);rect('m',x-2,39,9,2);
      rect('k',x,7,6,33);rect('t',x+1,8,3,30);rect('y',x+1,8,1,24);
      for(const y of [12,17,22,27])rect('k',x+3,y,2,1);
      rect('m',x,30,7,3);
    }
    // Paired swing arms tuck under the pinch welds; the car casts its own shadow below.
    rect('k',14,29,65,3);rect('n',15,28,64,2);rect('y',20,27,8,1);rect('y',67,27,6,1);
    rect('s',19,40,39,1);rect('d',19,41,46,1);
    // Bonnet open on the left; engine visible behind the headlamps.
    stamp(15,7,'...vk........../..vlpk........./.vlpppk......../.vpppvpk......./..vppvvpkk...../...vvpvvvpkk.../....vvvppvvpk../.....kkkkkvvvk./..........kkkdk');
    stamp(15,16,motor);
    stamp(14,6,[
      '..........................kkkkkkkkkkkkkkkk',
      '........................kllllllplplplpppppk',
      '......................kvliiiiiilppppppppplpk',
      '.....................kpaaiiaaabvbbbaaabbbvvpk',
      '...................kvpaiaaaaabkvbaaaabbbbbvvpk',
      '..................kvpaaaaaaabkvbaaaabbbbbbbvvpk',
      '.................kvpaaaaaabbkvvbbaabbbbbbbbbbvpk',
      '................kvpbbbbbbbbkvvvbbbbbbbbbbbbbbvvpk',
      '...............kpppppppppppppplpppppppppppppppvvpk',
      '..............kllllplpppppppppppppppvpppppplpppvvpk',
      '.............kvppppppppppppppppppppvppppppppppvvvpk',
      '.............kvvppppppppppppppppkkpvppppkkppppvvvpk',
      '.............kvvvppppppppppppppppppvppppppppppvrrpk',
      '..............vvvvvppppppppppppppppvppppppppppvvvvk',
    ]);
    // Fender, sill and short rear deck meet the cabin at full pixel boundaries.
    rect('v',14,21,65,4);rect('p',17,20,58,2);
    rect('p',67,17,9,4);rect('l',67,17,7,1);rect('v',76,19,4,5);
    rect('d',14,24,66,3);rect('v',34,24,31,2);rect('l',35,23,25,1);
    rect('k',16,26,8,2);rect('m',15,25,6,1);rect('d',79,23,2,3);
    rect('h',15,21,6,1);rect('w',15,22,4,2);rect('r',77,20,3,2);
    rect('k',24,23,10,5);stamp(24,22,hub);
    rect('k',65,22,11,6);stamp(66,21,wheel);
    stamp(22,36,wheel);rect('m',34,42,5,1);rect('s',38,40,2,3);
    rect('d',56,38,10,2);rect('n',58,37,6,1);
  } else if(kind==='tools'||kind==='keys') {
    const keys=kind==='keys';
    const w=W-3;shadow(1,shadowFoot,w-2);
    casework(1,1,w,keys?12:21,keys?'n':'s');
    for(let x=5;x<w-4;x+=5)for(let y=5;y<(keys?11:18);y+=4)rect('d',x,y,1,1);
    if(keys){
      for(const [x,c] of [[6,'p'],[14,'y'],[21,'a']])stamp(x,4,'hh/hd/.m/.m/.'+c);
    }else{
      for(const [x,y] of [[7,5],[15,4],[24,6]])stamp(x,y,'m.m/hmh/.m./.m./.s./.s.');
      stamp(36,5,'h..h/.mm./.dd./.tt./.tt./t..t');
      stamp(48,5,'...mm/.mmm./.m.../.m.../.m.../.s...');
      rect('n',0,21,w+1,3);rect('h',1,21,w-3,1);rect('d',2,24,3,6);rect('d',w-5,24,3,6);
      stamp(8,18,'hh..hh/mmkkmm/.dssd./..dd..');
    }
  } else if(kind==='roller-chest'||kind==='diagnostics'||kind==='paint-cart'){
    const diagnostic=kind==='diagnostics',paint=kind==='paint-cart';
    const y=paint?5:diagnostic?19:7, w=W-6,ht=paint?8:17;
    shadow(2,y+ht,w);casework(2,y,w,ht,paint?'a':diagnostic?'s':'r');
    for(let row=y+4;row<y+ht-2;row+=4){rect('k',4,row,w-6,1);rect('m',6,row+1,w-11,1);}
    for(const x of [5,w-2]){rect('k',x,y+ht,3,3);rect('s',x,y+ht,2,1);}
    if(diagnostic){
      rect('d',12,14,4,6);casework(4,4,22,12,'b');rect('k',6,7,16,7);
      stamp(7,8,'........g...../..g....g.g..../gg.gg.g...ggg./.....g........');
      rect('d',2,22,2,14);rect('d',0,35,3,2);
    }else if(paint){
      for(const [x,c] of [[5,'a'],[12,'w'],[19,'b']]){rect('k',x,1,5,5);rect(c,x+1,2,3,3);rect('h',x,1,4,1);}
    }else{stamp(7,4,'...mm.....mm/..msmmmmmmm./..mm........');rect('d',W-4,9,3,2);}
  } else if(kind==='tyres'){
    for(const [x,y] of [[2,21],[3,16],[2,11],[26,22],[25,17]]){
      stamp(x,y,'...ssssssssss.../.ssmmddddddmmss./dmmddkkkkkkddmmd/kdssssssssssssdk/kdsdsdsdsdsdsdsk/.dkddddddddddkd./...kkkkkkkkkk...');
    }
  } else if(kind==='compressor'){
    shadow(2,25,39);
    stamp(4,11,[
      '......mmmmmmmmmmmmmmmmmmmm',
      '...mhhhhhhhhmmmmmmmmmmmmmmdm',
      '..mtttttttttttttttttttttttsdm',
      '.sttttttttttttttttrrrrrrrrtsdm',
      'stttrrrrrrrtrrrrrrrrrrrrrrrtsdk',
      'sttrrrrrrrrtrrrrrrrrrrrrrrrtsdk',
      '.strrrrddddtrrrrrrrdddddddtsdk',
      '..sddddddddsddddddddddddddsdk',
      '...kkkdddddkkkdddddddddkkkkk',
    ]);
    stamp(12,5,motor);stamp(30,7,'mhhm/hddh/h.sh/mhhm/..s.');
    stamp(8,21,wheel);rect('s',30,23,5,3);rect('k',29,26,7,2);
    rect('d',36,16,4,2);rect('k',39,17,2,8);rect('d',41,24,4,2);
  } else if(kind==='engine-hoist'){
    shadow(2,40,40);
    stamp(21,19,motor);stamp(24,24,'sshsshhsshs/sdsmmdsmmds/.dkdkkdkdk.');
    for(let t=0;t<31;t++){rect('n',4+Math.floor(t/4),37-t,3,2);rect('y',4+Math.floor(t/4),37-t,1,2);}
    for(let t=0;t<23;t++)rect(t%6===0?'y':'n',11+t,7-Math.floor(t/5),2,3);
    for(let y=6;y<18;y+=2)rect('m',32+(y%4===0?1:0),y,1,2);
    stamp(27,15,'....m..../...m.m.../..m...m../.m.....m./m.......m');
    rect('n',3,38,34,2);rect('y',3,38,22,1);rect('d',5,40,4,2);rect('d',34,40,4,2);
  } else if(kind==='paint-shell') {
    shadow(7,29,48);
    // A stripped hatchback in primer on trestles, with glass masked in brown paper.
    stamp(5,9,[
      '..................sssssssssssssssssss',
      '...............ssshhhmmmmmmmmmmhhmmmds',
      '..............smnnnnyynsnnnyyyynnnhmmms',
      '............smnnnnyynnsnnnyyyynnnhmmms',
      '...........smnnnyynnnsnnnyyynnnnhmmss',
      '..........smnnyynnnnsnnnyynnnnnhmmss',
      '.........smnyynnnnnsnnnynnnnnnhmmss',
      '......ssmmhhhmmhhhhmmhhhmhhmmmmmmmmmssss',
      '..ssmmmaaaaaaaaammmmmmmmmmmmmmshmmmmmmmms',
      '.smaaaaaaaaaaaaaaammmmmmmmmmmmmshmmmmmmmmms',
      'smaaaabaaabaaaaaaaaammmmmmmmmmmshmmmmmmmmds',
      'saaaabkkkkbaaaaaaaabaaaammmmmmmshmmmmdkkkds',
      'dabbkk....kkbaaaaaaabaaaaammmmmshmmdkk...kk',
      '.ddk........kdddddddbddddddddddddddk......k',
    ]);
    rect('s',16,22,28,2);rect('d',13,24,35,2);
    for(const x of [14,46])stamp(x,24,'..ss../..tt../.tnnt./.t..t./tt..tt');

  } else if(kind==='paint-door'){
    shadow(2,27,41);
    stamp(4,3,[
      '.......ssssssssssssssssssssss',
      '......shhmmmmmmmmmmmmmmmmmmhhs',
      '.....smynnyynnnnnnyyyyyynnnnmhs',
      '....smnnyynnynnnnyyyynnnnnnnnmhs',
      '...smnnyynnnnnnnyyynnnnnnnnnnmhs',
      '..smnnyynnnnnnnyyynnnnnnnnnnnnmhs',
      'smmhhhhhhmmmhhhmmmmmmhhhhmmmhhhhhhs',
      'siaaaaaaaaaaaaaammmmnnnnnnnnnnnmms',
      'saaaaaaaaabaaaaaaammmnnnnnnnkkkmms',
      'saaaaaabbaabaaaaaaammmmnnnnnnnnmms',
      'saaaaaabaaaaaaaaaaaammmnnnnnnnnmms',
      '.sbaaaaaaaaaaaaaaammmnnnnnnnnnmms',
      '.ssbbbbbbbbbbbbbbbmmmmnnnnnnnmms',
      '..dddddddddddddddddddddddddddds',
    ]);
    for(const x of [8,35]){rect('k',x,17,2,9);rect('m',x,17,1,8);rect('m',x-3,25,7,2);}
  } else if(kind==='wash-reel'){
    shadow(1,26,38);
    casework(2,4,22,22,'a');
    stamp(4,6,[
      '....sssssss',
      '..smmmmmmmms',
      '.smdddddddsms',
      '.smdaaaaadsmms',
      'smdabbbbadmsms',
      'smdabmmabdmssm',
      'smdabmmabdmssm',
      'smdabbbbadmsms',
      '.smdabbbadmsm',
      '.ssmddddddms',
      '..ssmmmmmms',
      '....ssssss',
    ]);
    rect('k',13,18,2,8);rect('d',14,25,24,2);rect('s',35,22,3,4);rect('m',37,21,6,2);
  } else if(kind==='onigiri-counter'){
    shadow(3,26,54);casework(3,12,55,15,'v');rect('n',2,11,56,4);rect('h',4,11,52,1);
    rect('p',5,17,30,5);rect('d',40,17,12,6);
    stamp(9,6,rice);casework(40,4,12,8,'b');rect('i',42,7,7,2);
    stamp(23,10,'..hhhhh/wwwwww./.mms...');
  } else if(kind==='parts-rack'||kind==='bins'){
    const w=W-4;
    shadow(1,27,w);
    if(kind==='bins'){
      for(const [x,y] of [[1,16],[14,16],[12,5]]){
        casework(x,y,14,11,'n');rect('y',x+6,y+1,2,6);rect('w',x+2,y+4,4,2);
      }
    }else{
      rect('d',3,3,w-4,24);
      stamp(5,5,motor);stamp(43,14,motor);
      for(const [x,y] of [[28,12],[59,2]])stamp(x,y,wheel);
      for(const [x,y] of [[29,4],[5,17],[65,17]]){rect('n',x,y,9,6);rect('h',x+2,y+2,3,1);}
      for(const y of [13,26]){rect('s',1,y,w,3);rect('m',2,y,w-2,1);}
      for(const x of [1,w-1]){rect('k',x,1,2,30);rect('m',x,1,1,26);}
    }
  }
}
