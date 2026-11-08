const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const { chromium, executablePath, previewURL } = require('./portable-browser-tools.cjs');

(async () => {
  const browser = await chromium.launch({ executablePath, headless: true });
  const output = path.resolve(__dirname, '../preview/native-city77');
  const artRevision = JSON.parse(fs.readFileSync(path.join(output, 'manifest.json'), 'utf8')).artRevision;
  const compareWallPreview = async page => page.evaluate(() => {
    const review = window.cityReview, canvas = document.getElementById('field');
    const c = canvas.getContext('2d'), map = review.getMap(), view = review.getView();
    const selection = review.getWallSelection();
    const cells = new Set(selection.cells.map(([x,y]) => `${x},${y}`));
    review.setWallPreviewEnabled(false);
    const before = c.getImageData(0, 0, canvas.width, canvas.height).data;
    review.setWallPreviewEnabled(true);
    const after = c.getImageData(0, 0, canvas.width, canvas.height).data;
    let changed = 0, outside = 0;
    for (let i = 0; i < before.length; i += 4) {
      if ([0,1,2,3].every(k => before[i+k] === after[i+k])) continue;
      changed++;
      const px = (i/4) % canvas.width, py = Math.floor(i/4/canvas.width);
      const x = Math.floor((px-view.offsetX)/view.scale/32+view.startX/32);
      const y = Math.floor((py-view.offsetY)/view.scale/32+view.startY/32);
      if (map.seed !== selection.seed || map.depth !== selection.depth || !cells.has(`${x},${y}`)) outside++;
    }
    return { changedPixels: changed, outsideSelectionChangedPixels: outside };
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const covered = new Set();
    let floors = 0, doorChecks = 0;
    for (const seed of [77001, 77002, 77003]) {
      await page.goto(`${previewURL}/native-city77/?seed=${seed}&floor=1`);
      await page.waitForFunction(() => window.ready);
      for (let depth = 1; depth <= 14; depth++) {
        await page.locator('#floor').selectOption(String(depth));
        await page.waitForFunction(({ seed, depth }) => window.cityReview.getMap().depth === depth &&
          window.cityReview.getMap().seed === seed, { seed, depth });
        const map = await page.evaluate(() => window.cityReview.getMap());
        const native = JSON.parse(fs.readFileSync(path.join(output, `maps/map-${seed}-${depth}.json`), 'utf8'));
        assert.deepEqual(map, native);
        if (artRevision >= 81 && (seed !== 77001 || depth !== 3))
          assert.equal((await compareWallPreview(page)).changedPixels, 0);
        const schedule = await page.evaluate(() => window.cityReview.getMaps().map(floor => floor.facility).filter(Boolean));
        assert.equal(new Set(schedule).size, schedule.length);
        assert.ok(schedule.length <= 9);
        if (map.facility && !covered.has(map.facility)) {
          covered.add(map.facility);
          await page.locator('#facility').click();
          for (const door of map.doors.filter(door => map.origin && door.x >= map.origin.x &&
            door.x < map.origin.x + map.origin.width && door.y >= map.origin.y &&
            door.y < map.origin.y + map.origin.height)) {
            const checked = await page.evaluate(target => {
              const review = window.cityReview;
              const route = review.route(target);
              if (route.length === 0) throw Error('Facility door unreachable from native stair');
              for (const next of route.slice(1)) {
                const before = review.getState().player;
                review.move(next.x - before.x, next.y - before.y);
                const after = review.getState().player;
                if (after.x !== next.x || after.y !== next.y) review.move(next.x - after.x, next.y - after.y);
              }
              return review.getState().opened.includes(`${target.x},${target.y}`);
            }, { x: door.x, y: door.y });
            assert.ok(checked);
            doorChecks++;
          }
          const before = await page.evaluate(() => window.cityReview.getState());
          await page.reload();
          await page.waitForFunction(() => window.ready);
          const after = await page.evaluate(() => window.cityReview.getState());
          assert.deepEqual(after.player, before.player);
          assert.deepEqual(after.opened, before.opened);
          assert.equal(after.turns, before.turns);
        }
        floors++;
      }
    }
    // Three random runs need not encounter all nine facilities. The native
    // 168-floor suite covers the complete catalog separately.
    const catalog = JSON.parse(fs.readFileSync(path.resolve(__dirname,
      '../migration/engine0341-city77/overlay/crawl-ref/source/holo34-facilities.json'), 'utf8'));
    const knownFacilities = new Set(catalog.map(facility => facility.id));
    for (const facility of covered) assert.ok(knownFacilities.has(facility));
    const visual = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
    await visual.goto(`${previewURL}/native-city77/?seed=77001&floor=1`);
    await visual.waitForFunction(() => window.ready);
    await visual.locator('#facility').click();
    await visual.screenshot({ path: path.join(output, 'restaurant-entrance.png'), fullPage: true });
    await visual.goto(`${previewURL}/native-city77/?seed=77001&floor=3`);
    await visual.waitForFunction(() => window.ready);
    await visual.locator('#facility').click();
    await visual.screenshot({ path: path.join(output, 'native-city.png'), fullPage: true });
    // Revisit the user's wall junctions in an isolated test profile.
    await visual.evaluate(target => {
      const review = window.cityReview;
      const route = review.route(target);
      if (!route.length) throw Error('Wall review area is unreachable');
      for (const next of route.slice(1)) {
        let current = review.getState().player;
        review.move(next.x - current.x, next.y - current.y);
        current = review.getState().player;
        if (current.x !== next.x || current.y !== next.y)
          review.move(next.x - current.x, next.y - current.y);
      }
    }, artRevision >= 80 ? { x: 31, y: 45 } : { x: 25, y: 30 });
    await visual.locator('#player').click();
    const wallScope = artRevision >= 81 ? await compareWallPreview(visual) : null;
    if (wallScope) {
      assert.ok(wallScope.changedPixels > 0);
      assert.equal(wallScope.outsideSelectionChangedPixels, 0);
      fs.writeFileSync(path.join(output, 'wall-selection81-validation.json'), JSON.stringify({
        status: 'passed', otherFloorsUnchanged: 41, ...wallScope,
      }, null, 2) + '\n');
    }
    await visual.screenshot({ path: path.join(output, `wall-joins${artRevision}.png`), fullPage: true });
    await visual.locator('#field').screenshot({ path: path.join(output, `wall-joins${artRevision}-field.png`) });
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(output, 'browser-validation.json'), JSON.stringify({
      status: 'passed', nativeSnapshotsChecked: floors, facilitiesCovered: covered.size,
      doorChecks, browserReloadKeepsState: true, mobileOverflow: false, pageErrors: errors,
    }, null, 2) + '\n');
    console.log(`Checked ${floors} native floors, ${covered.size} facilities, ${doorChecks} doors and browser reload.`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
