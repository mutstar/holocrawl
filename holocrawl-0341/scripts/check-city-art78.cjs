// Catch regressions where the native preview silently falls back to legacy art.
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const { chromium, executablePath, previewURL } = require('./portable-browser-tools.cjs');

const root = path.resolve(__dirname, '..');
const preview = path.join(root, 'preview/native-city77');
const revision = JSON.parse(fs.readFileSync(path.join(preview, 'manifest.json'), 'utf8')).artRevision;
const sprites = path.join(root, 'migration/engine0341-city77/overlay/crawl-ref/source/rltiles/holocrawl');
const cases = new Map();
let floors = 0;
for (const seed of [77001, 77002, 77003]) {
  for (let depth = 1; depth <= 14; depth++) {
    const name = `map-${seed}-${depth}.json`;
    const before = JSON.parse(fs.readFileSync(path.join(root, 'analysis/native-city77-final07', name), 'utf8'));
    const after = JSON.parse(fs.readFileSync(path.join(preview, 'maps', name), 'utf8'));
    assert.deepEqual(after.rows, before.rows);
    assert.deepEqual(after.origin, before.origin);
    assert.equal(after.facility, before.facility);
    assert.deepEqual(after.doors.map(({x,y}) => [x,y]), before.doors.map(({x,y}) => [x,y]));
    const insideFacility = (x, y) => after.origin && x >= after.origin.x && y >= after.origin.y &&
      x < after.origin.x + after.origin.width && y < after.origin.y + after.origin.height;
    const solid = (x, y) => '#G+'.includes(after.rows[y]?.[x] || '#');
    const neighbours = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
    for (let y = 1; y < after.height - 1; y++) {
      for (let x = 1; x < after.width - 1; x++) {
        if (insideFacility(x, y) || after.rows[y][x] !== '#') continue;
        const tile = after.palette[after.features[y * after.width + x]];
        if (tile.atlas !== 'wall') continue;
        // Exclude the facility boundary, whose transparent furniture has its own feature types.
        if (neighbours.some(([dx,dy]) => insideFacility(x + dx, y + dy))) continue;
        const mask = neighbours.reduce((result, [dx,dy], bit) => result | (solid(x + dx, y + dy) ? 1 << bit : 0), 0);
        const variant = (seed ^ Math.imul(x, 374761393) ^ Math.imul(y, 668265263)) & 7;
        const file = `holo_city_wall78_${mask}_${variant}.png`;
        cases.set(file, { tile, file });
      }
    }
    if (after.origin) {
      const { x, y, width, height } = after.origin;
      for (let dx = 0; dx < width; dx++) {
        const tile = after.palette[after.features[(y + height - 1) * after.width + x + dx]];
        const file = `holo_facility_${after.facility}_${(height - 1) * width + dx}.png`;
        cases.set(file, { tile, file });
      }
    }
    floors++;
  }
}

(async () => {
  const browser = await chromium.launch({ executablePath, headless: true });
  try {
    const page = await browser.newPage();
    await page.goto(`${previewURL}/native-city77/?seed=77001&floor=1`);
    await page.waitForFunction(() => window.ready);
    const comparisons = [...cases.values()].map(entry => ({ ...entry,
      expected: 'data:image/png;base64,' + fs.readFileSync(path.join(sprites, entry.file)).toString('base64') }));
    const pixelChecks = await page.evaluate(async ({ comparisons, revision }) => {
      const load = source => new Promise((resolve, reject) => {
        const image = new Image(); image.onload = () => resolve(image); image.onerror = reject; image.src = source;
      });
      const atlases = {};
      for (const name of ['floor', 'wall']) atlases[name] = await load(`assets/${name}.png?v=${revision}`);
      const canvas = document.createElement('canvas'); canvas.width = canvas.height = 32;
      const context = canvas.getContext('2d');
      for (const { tile, file, expected } of comparisons) {
        context.clearRect(0, 0, 32, 32);
        context.drawImage(await load(expected), 0, 0);
        const reference = context.getImageData(0, 0, 32, 32).data;
        context.clearRect(0, 0, 32, 32);
        context.drawImage(atlases[tile.atlas], tile.sx, tile.sy, tile.width, tile.height,
          tile.dx, tile.dy, tile.width, tile.height);
        const actual = context.getImageData(0, 0, 32, 32).data;
        for (let index = 0; index < reference.length; index++) {
          if (reference[index] !== actual[index]) throw Error(`Native art mismatch: ${file}, channel ${index}`);
        }
      }
      return comparisons.length;
    }, { comparisons, revision });
    const result = { status: 'passed', geometryPreservedFloors: floors, nativeAtlasPixelComparisons: pixelChecks,
      artRevision: revision, source: 'Continuous city wall surfaces and reviewed facility entrance sprites' };
    fs.writeFileSync(path.join(preview, `art${revision}-validation.json`), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
