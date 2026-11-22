"""Generate the package icon using two hinged numeral plates."""
from pathlib import Path
from PIL import Image, ImageDraw

image = Image.new("RGB", (512, 512), "#191c1d")
draw = ImageDraw.Draw(image)
for x in (38, 265):
    draw.rounded_rectangle((x, 115, x + 207, 395), radius=18, fill="#3b3e40")
    draw.rounded_rectangle((x, 250, x + 207, 395), radius=18, fill="#313437")
    draw.rectangle((x, 250, x + 207, 279), fill="#313437")
ink = "#f5f0df"
draw.polygon([(84,208),(132,164),(166,164),(166,343),(131,343),(131,210),(104,232)], fill=ink)
draw.rounded_rectangle((311,163,427,345), radius=46, fill=ink)
draw.rounded_rectangle((343,192,395,315), radius=20, fill="#373a3b")
for x in (38,265):
    draw.rectangle((x,252,x+207,258), fill="#131616")
draw.rounded_rectangle((40,79,100,87), radius=4, fill="#dfb37b")
image.save(Path(__file__).with_name("icon.png"), optimize=True)
