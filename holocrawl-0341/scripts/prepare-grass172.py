"""Palette/size export of the built-in generated turf material."""
from pathlib import Path
from PIL import Image
D=Path(__file__).resolve().parents[1]/'preview/facility-shapes172/assets'
im=Image.open(D/'grass-source.png').convert('RGB')
im=im.resize((32,32),Image.Resampling.BOX).quantize(colors=8,dither=Image.Dither.NONE).convert('RGB')
im.resize((64,64),Image.Resampling.NEAREST).save(D/'grass-native.png')
print('Exported64x64 turf on32x32 logical grid,8colors')
