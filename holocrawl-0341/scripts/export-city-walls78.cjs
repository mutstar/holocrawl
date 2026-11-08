// Bake city-batch22 colours plus the art79 junction correction into native tiles.
// Keep wall78 tile names and declaration order so stored tile IDs stay stable.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium, executablePath, previewURL } = require('./portable-browser-tools.cjs');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'migration/engine0341-city77/overlay/crawl-ref/source');
const images = path.join(output, 'rltiles/holocrawl');
const variants = 8;

(async () => {
  const browser = await chromium.launch({ executablePath, headless: true });
  try {
    const page = await browser.newPage();
    await page.goto(`${previewURL}/city-batch22/?map=0&placement=5110521`);
    await page.waitForFunction(() => window.ready);
    await page.addScriptTag({ path: path.join(root, 'preview/city-batch22/wall-joins79.js') });
    await page.addScriptTag({ path: path.join(root, 'preview/city-batch22/wall-corners84.js') });
    const results = await page.evaluate(variants => {
      fixtures = [];
      fences = [];
      mounted = [];
      wallRuns.clear();
      const result = [];
      const neighbours = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
      const sprite = document.createElement('canvas');
      sprite.width = sprite.height = 32;
      const context = sprite.getContext('2d');
      for (let variant = 0; variant < variants; variant++) {
        for (let mask = 0; mask < 256; mask++) {
          const map = { seed: `approved-city-wall78-${variant}`, w: 5, h: 5,
            palette: ['floor', 'rock_wall'], rows: Array.from({ length: 5 }, () => Array(5).fill(0)) };
          map.rows[2][2] = 1;
          for (const [index, [dx, dy]] of neighbours.entries()) {
            if (mask & (1 << index)) map.rows[2 + dy][2 + dx] = 1;
          }
          wallRuns.clear();
          context.clearRect(0, 0, 32, 32);
          tile(context, map, 2, 2, 0, 0, 32, 'fit', false, false);
          const pixels = context.getImageData(0, 0, 32, 32).data;
          for (let index = 3; index < pixels.length; index += 4) {
            if (pixels[index] !== 255) throw Error(`Transparent wall ${mask}/${variant}`);
          }
          result.push({ mask, variant, thin: isLocalThinWall(map, 2, 2),
            png: sprite.toDataURL().split(',')[1] });
        }
      }
      return result;
    }, variants);
    fs.mkdirSync(images, { recursive: true });
    const declarations = [];
    for (const result of results) {
      const name = `holo_city_wall78_${result.mask}_${result.variant}`;
      fs.writeFileSync(path.join(images, `${name}.png`), Buffer.from(result.png, 'base64'));
      declarations.push(`${name} ${name.toUpperCase()}`);
    }
    fs.writeFileSync(path.join(output, 'rltiles/holo-wall78.txt'),
      '\n# HOLOCRAWL WALL78\n%sdir holocrawl\n%back none\n%rim 0\n%shrink 0\n%weight 10\n' + declarations.join('\n') + '\n');
    const sources = ['terrain.js', 'wall-volume.js', 'wall-joins79.js', 'wall-corners84.js'].map(file => ({
      file: `preview/city-batch22/${file}`,
      sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'preview/city-batch22', file))).digest('hex'),
    }));
    fs.writeFileSync(path.join(output, 'holo34-wall78.json'), JSON.stringify({
      source: 'Art84 corner continuity: remove diagonal cap tongues and complete west-facing L joins, retaining art79 height and material.',
      artRevision: 84,
      neighbours: ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
      masks: 256, variants, tiles: results.length, allTilesOpaque: true, sources,
      thinMasks: results.filter(result => result.variant === 0 && result.thin).map(result => result.mask),
    }, null, 2) + '\n');
    console.log(`Exported ${results.length} native wall sprites with art84 corner joins.`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
