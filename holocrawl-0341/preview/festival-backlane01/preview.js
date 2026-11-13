(async function () {
  const status = document.getElementById('status');
  const wallRoot = '../wall-height121/';
  const atlas = new Image();
  atlas.src = `${wallRoot}wall22.png`;
  async function readJson(name) {
    const response = await fetch(`${wallRoot}${name}`);
    if (!response.ok) throw Error(name);
    return response.json();
  }

  try {
    const [rects, planes] = await Promise.all([readJson('rects121.json'), readJson('planes121.json'), atlas.decode()]);
    const art = createBacklaneSurfaces(atlas, rects, planes);
    const container = document.getElementById('floors');
    const template = document.getElementById('floor-preview');
    const neighbors = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]];
    const layout = [
      '####################',
      '####################',
      '##...#.....#......##',
      '##................##',
      '##......##.........#',
      '###...............##',
      '####################',
    ];

    function wallMask(x, y) {
      return neighbors.reduce((mask, [dx, dy], bit) =>
        layout[y + dy]?.[x + dx] === '#' ? mask | (1 << bit) : mask, 0);
    }

    for (const floor of [1, 2]) {
      const section = template.content.cloneNode(true);
      section.querySelector('h2').textContent = `${floor}층 · 노점 준비 골목`;
      const canvas = section.querySelector('.room');
      canvas.width = layout[0].length * art.size;
      canvas.height = layout.length * art.size;
      canvas.setAttribute('aria-label', `축제 뒷길 ${floor}층 벽 매립 구조물 배치 예시`);
      const ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = false;
      ctx.fillStyle = '#211f1b';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      for (const [y, row] of layout.entries()) {
        for (const [x, cell] of [...row].entries()) {
          const sprite = cell === '#' ? art.wallTile(floor, wallMask(x, y), x, y) : art.floorTile(floor, x, y);
          ctx.drawImage(sprite, x * art.size, y * art.size);
        }
      }

      const structureList = section.querySelector('.structures');
      for (const structure of BacklaneWallStructures[floor - 1]) {
        drawBacklaneWallStructure(ctx, structure, structure.x * art.size, art.size);
        const item = document.createElement('li');
        item.textContent = `${structure.name} · ${structure.width}칸`;
        structureList.append(item);
      }

      const [floorSample, wallSample] = section.querySelectorAll('figure canvas');
      floorSample.getContext('2d').drawImage(art.floorTile(floor, 4, 3), 0, 0);
      wallSample.getContext('2d').drawImage(art.wallTile(floor, wallMask(4, 1), 4, 1), 0, 0);
      container.append(section);
    }
    status.hidden = true;
  } catch (error) {
    status.textContent = '기본 타일을 불러오지 못했습니다.';
    throw error;
  }
})();
