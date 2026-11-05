from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'preview/city-explore01/terrain.js'
s=p.read_text(encoding='utf-8')
s=s.replace('decor:end-start>=7?start+2+h%(end-start-4):-1','decor:end-start>=4?start+1+h%(end-start-2):-1')
a=s.index(' // One mounted fixture') if ' // One mounted fixture' in s else s.index(' if(gx===run.decor')
b=s.index('\n}',a)
s=s[:a]+''' // One mounted fixture per sufficiently long wall run; avoid door frames and shop windows.
 if(gx===run.decor&&!isDoor(feature(m,gx,gy))&&!isDoor(feature(m,gx-1,gy))&&!isDoor(feature(m,gx+1,gy))&&!fixtures.some(p=>MerchCatalog.find(a=>a.id===p.type).kind==='wall'&&p.y===gy&&gx>=p.x&&gx<p.x+2)){
  const kind=hash(m.seed,gx+431,gy)%4;
  c.fillStyle='rgba(8,12,9,.45)';c.fillRect(px+4*s,py+24*s,24*s,s);
  if(kind===0)texture(c,[289,34,37,19],px+2*s,py+9*s,27*s,14*s);
  if(kind===1){c.lineJoin='miter';c.strokeStyle='#242b26';c.lineWidth=4*s;c.beginPath();c.moveTo(px+5*s,py+4*s);c.lineTo(px+19*s,py+4*s);c.lineTo(px+19*s,py+28*s);c.stroke();c.strokeStyle='#979b8e';c.lineWidth=2*s;c.stroke();c.fillStyle='#545e51';c.fillRect(px+16*s,py+12*s,6*s,2*s);c.fillRect(px+16*s,py+22*s,6*s,2*s);}
  if(kind===2)texture(c,[294,86,22,16],px+5*s,py+8*s,22*s,16*s);
  if(kind===3)texture(c,[183,31,32,12],px+1*s,py+9*s,30*s,12*s);
 }
'''+s[b:]
p.write_text(s,encoding='utf-8')
p=root/'preview/city-explore01/index.html';s=p.read_text(encoding='utf-8').replace('src="terrain.js"','src="terrain.js?v=wall-decor02"');p.write_text(s,encoding='utf-8')
print('Four existing mounted fixture types connected; progression and map data unchanged.')
