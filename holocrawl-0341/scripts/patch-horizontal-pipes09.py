from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01'
p=out/'terrain.js';s=p.read_text(encoding='utf-8')
if 'function wallPipeSpan09(' not in s:
 a=s.index('function wallFace(')
 s=s[:a]+'''function wallPipeSpan09(m,x,y){const run=wallRun(m,x,y);if(Object.prototype.hasOwnProperty.call(run,'pipe09'))return run.pipe09;run.pipe09=null;const anchor=run.decor;if(anchor<0||hash(m.seed,anchor+431,y)%4!==1)return null;
 const allowed=xx=>xx>=run.start&&xx<run.end&&isWall(feature(m,xx,y))&&!isDoor(feature(m,xx,y+1))&&!isDoor(feature(m,xx-1,y))&&!isDoor(feature(m,xx+1,y))&&!fixtures.some(p=>MerchCatalog.find(a=>a.id===p.type).kind==='wall'&&p.y===y&&xx>=p.x&&xx<p.x+2);
 if(!allowed(anchor))return null;let left=anchor,right=anchor;while(allowed(left-1))left--;while(allowed(right+1))right++;if(right-left+1<3)return null;const length=Math.min(right-left+1,3+hash(m.seed,run.start+59,y)%3),start=Math.max(left,Math.min(right-length+1,anchor-Math.floor(length/2)));return run.pipe09={start,length,end:start+length,y};}
function drawHorizontalPipe09(c,m,x,y,px,py,t){const plan=wallPipeSpan09(m,x,y);if(!plan||x<plan.start||x>=plan.end)return;const offset=x-plan.start,part=offset===0?0:offset===plan.length-1?2:1;c.drawImage(images.wallPipeHorizontal09,part*32,0,32,32,px,py,t,t);}
'''+s[a:]
 s=s.replace(' // One mounted fixture per sufficiently long wall run; avoid door frames and shop windows.', ' drawHorizontalPipe09(c,m,gx,gy,px,py,t);\n // One mounted fixture per sufficiently long wall run; avoid door frames and shop windows.')
s=s.replace('if(kind===1)c.drawImage(images.wallPipe08,px,py,t,t);','if(kind===1){}')
p.write_text(s,encoding='utf-8')
p=out/'boot.js';s=p.read_text(encoding='utf-8')
if 'wallPipeHorizontal09:' not in s:s=s.replace('const sources={',"const sources={wallPipeHorizontal09:'assets/wall-pipe-horizontal09-96.png',")
p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('wall-equipment08','wall-equipment09');p.write_text(s,encoding='utf-8')
print('Horizontal connected piping spans 3–5 safe wall tiles; cabinets and accepted equipment retained.')
