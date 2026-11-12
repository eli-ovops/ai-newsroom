from pathlib import Path
import importlib.util,json,hashlib
from PIL import Image

ISSUE=Path(__file__).resolve().parent
ROOT=ISSUE.parents[2]
spec=importlib.util.spec_from_file_location('detail_renderer',ROOT/'render_details.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
out=ISSUE/'output';cover=json.loads((ISSUE/'content.json').read_text())
d=json.loads((ISSUE/'details.json').read_text())[0]
dt=r.m.datetime.fromisoformat(cover['date']).replace(tzinfo=r.m.ZoneInfo(cover['timezone']))
d['issueDate']=cover['date'];d['weekday']='星期'+'一二三四五六日'[dt.weekday()]
r.m.OUT=out;r.model_page(d,out);r.m.export(['02-kimi'])
names=['01-cover','02-kimi','03-openai','04-codex','05-teams']
contact=Image.new('RGB',(390*5,520),'white')
for i,n in enumerate(names):
    p=out/(n+'.png');thumb=Image.open(p).resize((390,520),Image.Resampling.LANCZOS)
    contact.paste(thumb,(i*390,0))
    if n=='02-kimi':thumb.save(out/(n+'-390.png'))
    if n!='02-kimi':assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((ISSUE.parent/'v02/output'/p.name).read_bytes()).digest()
contact.save(out/'phone-contact.png')
print('Kimi page exported. Four other PNGs hash-identical to v02.')
