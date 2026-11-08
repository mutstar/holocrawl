// Export the reviewed browser artwork and collision data for the native engine.
const fs = require('fs');
const path = require('path');
const { chromium, executablePath, previewURL } = require('./portable-browser-tools.cjs');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'migration/engine0341-city77/overlay/crawl-ref/source');
const entries = [
  ['mountain', 'jp-facilities76/?site=mountain&map=2'],
  ['dining', 'jp-facilities76/?site=dining&map=2'],
  ['theater', 'theater-vault57/'],
  ['gamers', 'gamers-station64/?map=2'],
  ['fantasy', 'fantasy-ground67/?map=2'],
  ['wheel', 'wheel-plaza71/?map=2'],
  ['market', 'jp-facilities76/?site=market&map=2'],
  ['holox', 'holox-floor62/?map=2'],
  ['dev', 'jp-facilities76/?site=dev&map=2'],
];

(async () => {
  const browser = await chromium.launch({ executablePath, headless: true });
  const catalog = [];
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const [id, url] of entries) {
      await page.goto(`${previewURL}/${url}`);
      await page.waitForFunction(() => window.ready && window.vaultReview);
      await page.addScriptTag({ path: path.join(root, 'preview/native-city77/entrances78.js') });
      const data = await page.evaluate(id => {
        const review = window.vaultReview;
        const { vault, layout } = review;
        const origin = layout.origin;
        // Suppress test loot and the player while capturing only the scenery.
        for (const key of Object.keys(vault.rewardOptions)) vault.rewardOptions[key] = [];
        const originalDrawImage = CanvasRenderingContext2D.prototype.drawImage;
        CanvasRenderingContext2D.prototype.drawImage = function (source, ...args) {
          if (source instanceof HTMLImageElement && /\/(body|boots|armour|helmet|sword)\.png$/.test(source.src)) return;
          return originalDrawImage.call(this, source, ...args);
        };
        const originalFillRect = CanvasRenderingContext2D.prototype.fillRect;
        CanvasRenderingContext2D.prototype.fillRect = function (...args) {
          if (this.fillStyle === '#91edbd') return;
          return originalFillRect.apply(this, args);
        };
        const room = document.createElement('canvas');
        room.width = vault.width * 32;
        room.height = vault.height * 32;
        const roomContext = room.getContext('2d');
        const crop = document.createElement('canvas');
        crop.width = crop.height = 32;
        const context = crop.getContext('2d');
        const capture = () => {
          review.draw();
          const source = document.getElementById('closeup');
          roomContext.imageSmoothingEnabled = false;
          roomContext.drawImage(source, 0, 0, room.width, room.height);
          window.drawNativeEntrance78(roomContext, id, vault.rows);
          const tiles = [];
          for (let y = 0; y < vault.height; y++) {
            for (let x = 0; x < vault.width; x++) {
              context.clearRect(0, 0, 32, 32);
              context.imageSmoothingEnabled = false;
              context.drawImage(room, x * 32, y * 32, 32, 32, 0, 0, 32, 32);
              tiles.push(crop.toDataURL().split(',')[1]);
            }
          }
          return tiles;
        };
        const rows = vault.rows.map((row, y) => [...row].map((_, x) => {
          const cell = layout.map.rows[origin.y + y][origin.x + x];
          if (cell === '+') return '+';
          if (review.pass(origin.x + x, origin.y + y)) return '.';
          if ((layout.opaqueChars || ['#', 'C']).includes(cell)) return '#';
          return cell === 'G' ? 'G' : 'F';
        }).join(''));
        const closed = capture();
        const doors = [];
        for (let y = 0; y < vault.height; y++) {
          for (let x = 0; x < vault.width; x++) {
            if (rows[y][x] !== '+') continue;
            const target = { x: origin.x + x, y: origin.y + y };
            for (const next of review.route(target).slice(1)) {
              const state = review.getState();
              review.move(next.x - state.player.x, next.y - state.player.y);
              const after = review.getState();
              if (after.player.x !== next.x || after.player.y !== next.y) {
                review.move(next.x - after.player.x, next.y - after.player.y);
              }
            }
            if (!review.getState().opened.includes(`${target.x},${target.y}`)) throw Error('Door not opened');
            doors.push(y * vault.width + x);
          }
        }
        const opened = capture();
        return { name: vault.name, width: vault.width, height: vault.height, rows, doors, closed, opened };
      }, id);
      const tilesDirectory = path.join(output, 'rltiles/holocrawl');
      fs.mkdirSync(tilesDirectory, { recursive: true });
      for (const [index, png] of data.closed.entries()) {
        fs.writeFileSync(path.join(tilesDirectory, `holo_facility_${id}_${index}.png`), Buffer.from(png, 'base64'));
      }
      for (const index of data.doors) {
        fs.writeFileSync(path.join(tilesDirectory, `holo_facility_${id}_${index}_open.png`), Buffer.from(data.opened[index], 'base64'));
      }
      const { closed, opened, ...metadata } = data;
      catalog.push({ id, url, ...metadata });
      console.log(`Exported ${id}: ${data.width}x${data.height}, ${data.doors.length} doors`);
    }
    if (errors.length) throw Error(errors.join('\n'));
    fs.writeFileSync(path.join(output, 'holo34-facilities.inc'), catalog.map(entry =>
      `{"${entry.id}", ${entry.width}, ${entry.height}, {${entry.rows.map(row => JSON.stringify(row)).join(', ')}}},`
    ).join('\n') + '\n');
    fs.writeFileSync(path.join(output, 'holo34-facilities.json'), JSON.stringify(catalog, null, 2) + '\n');
    const tiles = catalog.flatMap(entry => Array.from({ length: entry.width * entry.height }, (_, index) => {
      const name = `holo_facility_${entry.id}_${index}`;
      return [name, ...(entry.doors.includes(index) ? [`${name}_open`] : [])];
    }).flat());
    fs.writeFileSync(path.join(output, 'rltiles/holo-city77.txt'),
      '\n# HOLOCRAWL CITY77\n%sdir holocrawl\n%back none\n%rim 0\n%shrink 0\n%weight 10\n' +
      tiles.map(name => `${name} ${name.toUpperCase()}`).join('\n') + '\n');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
