from pathlib import Path
from PIL import Image, ImageSequence

HERE = Path(__file__).resolve().parent
source = Image.open(HERE / 'batman-source.gif')
poses = [frame.convert('RGBA') for frame in ImageSequence.Iterator(source)]
bounds = [pose.getbbox() for pose in poses]
box = (min(b[0] for b in bounds), min(b[1] for b in bounds), max(b[2] for b in bounds), max(b[3] for b in bounds))
scale = 76 / (box[3] - box[1])
size = (round((box[2] - box[0]) * scale), 76)
poses = [pose.crop(box).resize(size, Image.Resampling.NEAREST) for pose in poses]
# One palette across every frame; reserve index 255 for transparency.
strip = Image.new('RGB', (size[0] * len(poses), size[1]))
for i, pose in enumerate(poses):
    strip.paste(pose.convert('RGB'), (i * size[0], 0))
palette = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
frames = []
width, height, count, delay = 800, 92, 120, 50
for i in range(count):
    canvas = Image.new('RGBA', (width, height))
    x = round(-size[0] + (width + size[0]) * i / (count - 1))
    pose = poses[(i * delay // 100) % len(poses)]
    canvas.alpha_composite(pose, (x, height - size[1] - 6))
    indexed = canvas.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
    indexed.paste(255, mask=canvas.getchannel('A').point(lambda a: 255 if a < 128 else 0))
    indexed.info['transparency'] = 255
    frames.append(indexed)
frames[0].save(HERE / 'batman-run.gif', save_all=True, append_images=frames[1:], duration=delay, loop=0, transparency=255, disposal=2, optimize=False)
preview = Image.new('RGB', (800, 204), 'white')
preview.paste('#0d1117', (0, 102, 800, 204))
for y in (0, 102):
    preview.paste(poses[2], (330, y + 10), poses[2])
preview.save(HERE / 'batman-preview.png')
result = Image.open(HERE / 'batman-run.gif')
print(f'{result.size}, {result.n_frames} frames, {sum(f.info.get("duration",0) for f in ImageSequence.Iterator(result))} ms, {(HERE / "batman-run.gif").stat().st_size} bytes')
