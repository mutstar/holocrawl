from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'preview/city-explore01'
p=out/'terrain.js';s=p.read_text(encoding='utf-8')
if 'if(kind===0||kind===2)' not in s:
 s=s.replace("c.fillStyle='rgba(8,12,9,.45)';c.fillRect(px+4*s,py+24*s,24*s,s);", "if(kind===0||kind===2){c.fillStyle='rgba(8,12,9,.45)';c.fillRect(px+4*s,py+24*s,24*s,s);}")
a=s.index('  if(kind===1)');b=s.index('\n  if(kind===2)',a)
s=s[:a]+"  if(kind===1)c.drawImage(images.wallPipe07,px,py,t,t);"+s[b:]
s=s.replace("if(kind===3)texture(c,[183,31,32,12],px+1*s,py+9*s,30*s,12*s);", "if(kind===3)c.drawImage(images.wallCabinet07,px,py,t,t);")
p.write_text(s,encoding='utf-8')
p=out/'boot.js';s=p.read_text(encoding='utf-8')
if 'wallPipe07:' not in s:s=s.replace('const sources={',"const sources={wallPipe07:'assets/wall-pipe07-32.png',wallCabinet07:'assets/wall-cabinet07-32.png',")
p.write_text(s,encoding='utf-8')
p=out/'index.html';s=p.read_text(encoding='utf-8').replace('terrain.js?v=wall-decor02','terrain.js?v=wall-equipment07').replace('boot.js?v=crates03','boot.js?v=wall-equipment07');p.write_text(s,encoding='utf-8')
print('Only pipe and cabinet replaced; accepted AC/vent branches and gameplay preserved.')
