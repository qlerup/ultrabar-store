"""Original Studio system monitor icon in the shared geometric icon family."""
from pathlib import Path
from PIL import Image,ImageDraw
im=Image.new('RGB',(1024,1024),'#192325');d=ImageDraw.Draw(im)
d.rectangle((216,216,808,808),fill='#263c3b',outline='#94d9bb',width=24)
for x in (304,440,576,712):
 d.rectangle((x-12,140,x+12,216),fill='#94d9bb');d.rectangle((x-12,808,x+12,884),fill='#94d9bb')
for y in (304,440,576,712):
 d.rectangle((140,y-12,216,y+12),fill='#94d9bb');d.rectangle((808,y-12,884,y+12),fill='#94d9bb')
d.rectangle((320,486,404,704),fill='#b8adff');d.rectangle((470,336,554,704),fill='#94d9bb');d.rectangle((620,410,704,704),fill='#84bdf2')
im.resize((512,512),Image.Resampling.LANCZOS).save(Path(__file__).with_name('icon.png'),optimize=True)
