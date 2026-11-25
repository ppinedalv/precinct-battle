# Builds the iPhone home-screen icons from the Precinct Battle logo (eagle + badge centre on a black tile).
import sys
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
logo = Image.open(src).convert('RGBA')
badge = logo.crop((448, 0, 776, 400))            # eagle + POLICE star badge
m = Image.new('L', badge.size, 0); md = ImageDraw.Draw(m)  # keep the wings on top, only the shield below (drops the T / B letters and gold bars)
md.rectangle((0, 0, badge.width, 112), fill=255)
md.polygon([(x-448, y) for x, y in [(512,112),(730,112),(730,140),(724,175),(722,285),(708,330),(660,375),(615,398),(570,375),(522,330),(508,285),(506,175),(500,140)]], fill=255)
badge.putalpha(Image.composite(badge.getchannel('A'), m, m))
S = 1024
bg = Image.new('RGBA', (S, S))
# plain black tile: the logo's own dark shading around the badge is near-black, so it blends in with no visible edges
bg.paste((0, 0, 0, 255), (0, 0, S, S))
h = 900; w = round(badge.width * h / badge.height)
b = badge.resize((w, h), Image.LANCZOS)
bg.alpha_composite(b, ((S - w)//2, (S - h)//2 + 10))
rgb = bg.convert('RGB')                          # iOS icons must be opaque
for n in (1024, 512, 192, 180):
    rgb.resize((n, n), Image.LANCZOS).save(f'{out}/icon-{n}.png', optimize=True)
