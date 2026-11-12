#!/usr/bin/env python3
"""One-shot editorial pages using the existing master assets and font outlines."""
from pathlib import Path
import argparse,importlib.util,json,html
from PIL import Image

HERE=Path(__file__).resolve().parent
MASTER=HERE.parent/'ai_daily_editorial_replica_20261025_144029'
spec=importlib.util.spec_from_file_location('daily_master',MASTER/'build.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
C=m.THEMES['reference']['accent']
INK='#080808';GREY='#505050'

def line(y,x1=40,x2=1047,weight=1.5):
    return f'<path d="M{x1} {y}H{x2}" fill="none" stroke="#141414" stroke-width="{weight}"/>'

class Page:
    def __init__(self,data,index,total):
        self.data=data;self.parts=[];a=self.parts.append
        a(f'<svg xmlns="http://www.w3.org/2000/svg" width="1086" height="1448" viewBox="0 0 1086 1448"><title>{html.escape(data["title"])}</title>')
        a(f'<defs><linearGradient id="purple"><stop stop-color="{C}"/><stop offset="1" stop-color="{m.THEMES["reference"]["shadow"]}"/></linearGradient></defs>')
        a(m.image('paper',0,0,'reference'))
        a(m.text('AI DAILY',45,20,23,spacing=17))
        a('<g transform="translate(40 46) scale(.55)">'+m.image('masthead',0,0,'reference')+'</g>')
        a('<path d="M756 39V144" stroke="#181818" stroke-width="1.5"/>')
        self.t(data['issueDate'].replace('-','.'),788,45,42,'cn',maxw=260)
        a('<rect x="788" y="107" width="259" height="35" fill="url(#purple)"/>')
        self.t(data['weekday'],801,114,24,'regular',fill='#ffffff')
        a(line(167,weight=4));a(line(178))
        self.t(f'{index-1:02d}',41,210,70,'serif')
        a('<path d="M142 211V257" stroke="#111" stroke-width="1.5"/>')
        labelw=max(160,m.width(data['category'],30)+34)
        a(f'<rect x="166" y="212" width="{labelw}" height="46" fill="url(#purple)"/>')
        self.t(data['category'],183,221,30,fill='#fff')
        for i,s in enumerate(data['titleLines']):self.t(s,40,292+i*112,88,maxw=1006)
        a(f'<path d="M64 514Q180 502 292 509" stroke="{C}" fill="none" stroke-width="7" stroke-linecap="round"/>')
        self.block(data['summary'],40,548,35,49)
        self.index=index;self.total=total

    def t(self,s,x,y,size=36,font='cn',fill=INK,maxw=None):
        self.parts.append(m.text(s,x,y,size,font,fill=fill,maxw=maxw))

    def block(self,lines,x,y,size=36,step=49,font='regular',fill=INK,maxw=1006):
        for i,s in enumerate(lines):self.t(s,x,y+i*step,size,font,fill,maxw)

    def tag(self,s,y,x=40):
        w=m.width(s,30)+32
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="45" fill="url(#purple)"/>')
        self.t(s,x+16,y+9,30,fill='#fff')

    def finish(self,out,name):
        self.parts.append(line(1254))
        self.block(self.data['sourceLines'],40,1276,29,42,fill=GREY)
        self.parts.append(line(1368,weight=3.5));self.parts.append(line(1376))
        self.t(self.data['footer'].format(date=self.data['issueDate'].replace('-','.')),40,1398,19,'regular')
        self.parts.append('<path d="M910 1390V1422" stroke="#111" stroke-width="1.5"/>')
        self.t(f'{self.index:02d}',937,1393,33,'serif')
        self.t('/',984,1390,34,fill=C);self.t(f'{self.total:02d}',1006,1396,28,'date')
        self.parts.append('</svg>');svg=''.join(self.parts)
        (out/f'{name}.svg').write_text(svg)
        (out/f'{name}.html').write_text('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:1086px;height:1448px;overflow:hidden}svg{display:block}</style>'+svg)

def model_page(d,out):
    p=Page(d,2,5)
    p.parts.append('<g transform="translate(795 205) scale(.41)">'+m.image('neural-sphere',0,0,'reference')+'</g>')
    p.tag(d['chartTitle'],656)
    rows=d.get('benchmarkRows',[{'label':'Claude Opus 5.5','value':66.4,'brand':'anthropic'},{'label':'Kimi K3.1 Pro','value':65.7,'brand':'kimi'},{'label':'GPT-6 Astra','value':58.2,'brand':'openai'}])
    for i,row in enumerate(sorted(rows,key=lambda r:r['value'],reverse=True)):
        label=row['label'];value=row['value'];is_kimi=row['brand']=='kimi';y=729+i*77
        logo=HERE/'assets/logos'/f'{row["brand"]}.png'
        encoded=m.base64.b64encode(logo.read_bytes()).decode()
        p.parts.append(f'<image x="43" y="{y-3}" width="48" height="48" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{encoded}"/>')
        p.t(label,105,y+5,30,'regular',maxw=278)
        p.parts.append(f'<rect x="395" y="{y}" width="535" height="43" fill="#e6e3e9"/>')
        p.parts.append(f'<rect x="395" y="{y}" width="{535*value/100}" height="43" fill="{C if is_kimi else "#171717"}"/>')
        p.t(f'{value:.1f}%',942,y+2,32,'cn',fill=C if is_kimi else INK,maxw=105)
    for x,v in [(395,'0'),(662.5,'50'),(930,'100%')]:p.t(v,x-5,965,24,'regular',fill=GREY)
    p.block(d['condition'],40,1012,33,46)
    p.parts.append(line(1116));p.t(d['actionTitle'],40,1140,33,fill=C)
    p.block(d['action'],40,1188,32,44)
    p.finish(out,'02-kimi')

def security_page(d,out):
    p=Page(d,3,5)
    p.parts.append('<g transform="translate(822 211) scale(.60)">'+m.image('code-layers',0,0,'reference')+'</g>')
    p.tag(d['timelineTitle'],656)
    p.parts.append(f'<path d="M81 745V1043" stroke="{C}" stroke-width="3"/>')
    for i,e in enumerate(d['events']):
        y=735+i*148
        p.parts.append(f'<circle cx="81" cy="{y+19}" r="11" fill="{C}"/>')
        p.t(e['date'],120,y,42,'cn',fill=C,maxw=235)
        p.t(e['title'],385,y+1,36,maxw=662)
        p.t(e['body'],385,y+55,31,'regular',maxw=662)
    p.parts.append(line(1135));p.t(d['conditionTitle'],40,1159,32,fill=C)
    p.block(d['condition'],40,1205,31,40)
    p.finish(out,'03-openai')

def cli_page(d,out):
    p=Page(d,4,5)
    p.parts.append('<rect x="40" y="660" width="1007" height="236" fill="#f0eaf8"/>')
    p.t(d['featureLabel'],66,683,30,fill=C)
    p.t('10',65,738,121,'cn')
    p.t(d['slotsLabel'],258,781,41,'cn')
    p.t('/presets',652,759,65,'cn',maxw=370)
    p.t(d['featureNote'],67,850,31,'regular')
    p.t(d['moreTitle'],40,944,34,fill=C)
    for i,e in enumerate(d['more']):
        y=1004+i*101
        p.t(e['title'],40,y,35)
        p.t(e['body'],325,y+2,32,'regular',maxw=722)
        p.parts.append(line(y+73))
    p.block(d['condition'],40,1212,29,39)
    p.finish(out,'04-codex')

def teams_page(d,out):
    p=Page(d,5,5)
    p.tag(d['flowTitle'],656)
    for i,e in enumerate(d['steps']):
        x=[40,395,750][i]
        p.t(f'{i+1:02d}',x,734,70,'serif',fill=C)
        p.t(e['title'],x,827,38,maxw=297)
        p.block(e['body'],x,890,32,47,maxw=297)
        if i<2:p.t('→',x+280,753,48,'regular')
    p.parts.append(line(1014))
    p.t(d['boundary'],40,1048,41,maxw=1007)
    p.t(d['conditionTitle'],40,1144,32,fill=C)
    p.block(d['condition'],40,1191,32,44)
    p.finish(out,'05-teams')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--issue-dir',required=True);args=ap.parse_args()
    issue=Path(args.issue_dir).resolve();out=issue/'output';out.mkdir(exist_ok=True)
    data=json.loads((issue/'details.json').read_text());cover=json.loads((issue/'content.json').read_text())
    m.OUT=out;m.build(cover,'01-cover')
    dt=m.datetime.fromisoformat(cover['date']).replace(tzinfo=m.ZoneInfo(cover['timezone']))
    for renderer,d in zip([model_page,security_page,cli_page,teams_page],data):
        d['issueDate']=cover['date'];d['weekday']='星期'+'一二三四五六日'[dt.weekday()]
        renderer(d,out)
    names=['01-cover','02-kimi','03-openai','04-codex','05-teams'];m.export(names)
    contact=Image.new('RGB',(390*5,520),'white')
    for i,n in enumerate(names):
        im=Image.open(out/f'{n}.png');assert im.size==(1086,1448)
        thumb=im.resize((390,520),Image.Resampling.LANCZOS);thumb.save(out/f'{n}-390.png');contact.paste(thumb,(390*i,0))
    contact.save(out/'phone-contact.png')
    print(json.dumps({'pages':names,'dimensions':[1086,1448],'new_fonts':False,'reextracted_assets':False,'browser_closed':True}))
