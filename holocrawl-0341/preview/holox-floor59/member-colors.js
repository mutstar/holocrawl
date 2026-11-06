// Use a common painted-metal palette for the three freestanding fixtures.
// Keep the original sprite alpha and assign accent shades at render time.
const memberColors = new Map();
const accentColors = {
  laplus(r, g, b) {
    if (b > r + 2 && r > g + 13) return [12, -5, 27]; // Violet seal.
    if (r - g > 14 && g - b > 12) return [10, 3, -9]; // Worn brass chain.
    return null;
  },
  chloe(r, g, b) {
    if (r - g > 18 && r - b > 15) return [31, -8, -2]; // Deep red equipment marks.
    return null;
  },
  iroha(r, g, b) {
    if (g >= r - 4 && g - b >= 14) return [-3, 14, -7]; // Muted green banner.
    if (r - g > 14 && g - b > 12) return [8, 3, -9]; // Aged metal fittings.
    return null;
  },
};

LabMaterials.memberSprite = function (image, id) {
  const accent = accentColors[id];
  if (!accent) return null;
  if (memberColors.has(id)) return memberColors.get(id);

  const canvas = document.createElement('canvas');
  canvas.width = image.naturalWidth;
  canvas.height = image.naturalHeight;
  const context = canvas.getContext('2d');
  context.drawImage(image, 0, 0);
  const pixels = context.getImageData(0, 0, canvas.width, canvas.height);
  const data = pixels.data;
  for (let i = 0; i < data.length; i += 4) {
    if (!data[i + 3]) continue;
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    const tint = accent(r, g, b) ?? [0, -3, 8];
    // Lift the metal faces while keeping the deepest outlines dark.
    const midtoneLift = Math.min(9, Math.max(0, (luminance - 30) * 0.3));
    const shade = 26 + (luminance - 28) * 1.12 + midtoneLift;
    for (let channel = 0; channel < 3; channel++) data[i + channel] = shade + tint[channel];
  }
  context.putImageData(pixels, 0, 0);
  memberColors.set(id, canvas);
  return canvas;
};
