const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium, executablePath, previewURL } = require('./portable-browser-tools.cjs');

const preview = path.resolve(__dirname, '../preview');
const previous = path.join(preview, 'holox-floor54');
const output = path.join(preview, 'holox-floor55');
const read = (directory, file) => JSON.parse(fs.readFileSync(path.join(directory, file), 'utf8'));

async function build() {
  const vault = read(output, 'vault.json');
  assert.equal(vault.rows.length, vault.height);
  assert(vault.rows.every(row => row.length === vault.width));
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage();
    await page.goto(previewURL + '/city-batch22/?map=0&placement=5110521');
    await page.waitForFunction(() => window.ready);
    for (let index = 0; index < 3; index++) {
      const file = `scenario-${index}.json`;
      const scenario = read(previous, file);
      const { x, y } = scenario.origin;
      const oldTerrain = new URL(scenario.terrain, previewURL + '/holox-floor54/').href;
      scenario.map.rows = scenario.map.rows.map((row, index) => {
        const replacement = vault.rows[index - y];
        return replacement ? row.slice(0, x) + replacement + row.slice(x + vault.width) : row;
      });
      scenario.patches.forEach(patch => { patch.file = '../holox-floor54/' + patch.file; });
      scenario.terrain = `terrain-${index}.png`;
      const png = await page.evaluate(async ({ scenario, oldTerrain, width, height }) => {
        const background = new Image();
        background.src = oldTerrain;
        await background.decode();
        m = scenario.map;
        maps[selected] = m;
        fixtures = [];
        fences = [];
        mounted = [];
        opened.clear();
        wallRuns.clear();
        const canvas = document.createElement('canvas');
        canvas.width = m.w * 32;
        canvas.height = m.h * 32;
        const context = canvas.getContext('2d');
        context.imageSmoothingEnabled = false;
        context.drawImage(background, 0, 0);
        for (let y = scenario.origin.y; y < scenario.origin.y + height; y++) {
          for (let x = scenario.origin.x; x < scenario.origin.x + width; x++) {
            tile(context, m, x, y, x * 32, y * 32, 32);
          }
        }
        return canvas.toDataURL().split(',')[1];
      }, { scenario, oldTerrain, width: vault.width, height: vault.height });
      fs.writeFileSync(path.join(output, scenario.terrain), Buffer.from(png, 'base64'));
      fs.writeFileSync(path.join(output, file), JSON.stringify(scenario, null, 2) + '\n');
    }
  } finally {
    await browser.close();
  }
}

build().catch(error => { console.error(error); process.exitCode = 1; });
