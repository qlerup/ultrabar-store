"""Original Studio drive icon, matching the geometric Studio icon family."""
from pathlib import Path
from PIL import Image, ImageDraw
im=Image.new('RGB',(1024,1024),'#192325');d=ImageDraw.Draw(im)
d.rectangle((196,160,828,816),fill='#263c3b',outline='#94d9bb',width=24)
d.ellipse((304,236,720,652),outline='#94d9bb',width=28)
d.ellipse((466,398,558,490),fill='#eef6f2')
d.line([(512,444),(690,600)],fill='#b8adff',width=34)
d.rectangle((260,710,624,742),fill='#94d9bb')
d.rectangle((260,710,506,742),fill='#b8adff')
d.ellipse((704,706,744,746),fill='#94d9bb')
im.resize((512,512),Image.Resampling.LANCZOS).save(Path(__file__).with_name('icon.png'),optimize=True)
