"""Original Studio Clock icon, drawn from geometric primitives. Requires Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw
im=Image.new('RGB',(1024,1024),'#242235');d=ImageDraw.Draw(im)
d.ellipse((204,112,820,728),outline='#b8adff',width=40)
for box in [(500,152,524,200),(500,640,524,688),(244,408,292,432),(732,408,780,432)]:d.rectangle(box,fill='#b8adff')
d.line([(512,252),(512,420),(636,492)],fill='#f4f1ff',width=38)
d.ellipse((485,393,539,447),fill='#f4f1ff')
d.rectangle((292,808,732,840),fill='#b8adff');d.rectangle((372,884,652,908),fill='#9891b3')
im.resize((512,512),Image.Resampling.LANCZOS).save(Path(__file__).with_name('icon.png'),optimize=True)
