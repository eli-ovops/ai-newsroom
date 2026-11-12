#!/usr/bin/env python3
"""Deterministic local SVG build + one-shot PNG export. No server/accounts/API."""
from pathlib import Path
import argparse,base64,json,hashlib,html,io,math
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image,ImageChops,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
W,H=1086,1448
THEMES=json.loads((ROOT/'config/themes.json').read_text())
FONT={}

def prepare():
    source=Image.open(ROOT/'reference/reference.png').convert('RGB')
    assert source.size==(W,H),source.size
    # Read-only source. Fixed decorative assets only, never the whole page background.
    boxes={'masthead':(35,70,774,276),'neural-sphere':(498,378,1086,768),'video-layers':(748,787,1054,966),'code-layers':(692,983,1054,1166),'city':(719,1176,1053,1365)}
    for name,box in boxes.items():
        im=source.crop(box).convert('RGBA');px=im.load()
        for y in range(im.height):
            for x in range(im.width):
                r,g,b,_=px[x,y]
                # White-unmatte: preserve grayscale/coloured light layers without a rectangular background.
                a=255-min(r,g,b)
                if a<13: px[x,y]=(0,0,0,0);continue
                f=lambda c:max(0,min(255,round((c-255+a)*255/a)))
                px[x,y]=(f(r),f(g),f(b),round((a-12)*255/243))
        if name=='neural-sphere':
            # These source pixels are occupied by headline ink, not recoverable sphere detail.
            ImageDraw.Draw(im).rectangle((0,245,174,347),fill=(0,0,0,0))
        im.save(ROOT/'assets'/f'{name}.png')
    strip=source.crop((2,0,30,H))
    paper=Image.new('RGB',(W,H))
    for x in range(0,W,28):paper.paste(strip if (x//28)%2==0 else strip.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(x,0))
    paper.save(ROOT/'assets/paper.png')
    f=TTFont(ROOT/'fonts/NotoSerifDisplay.ttf')
    instantiateVariableFont(f,{'wght':900,'wdth':100},inplace=True).save(ROOT/'fonts/NotoSerifDisplay-Black.ttf')
    return boxes

def font(key):
    if key not in FONT:
        names={'cn':'NotoSansCJKsc-Black.otf','date':'Anton-Regular.ttf','serif':'NotoSerifDisplay-Black.ttf','regular':'NotoSansCJKsc-Regular.otf'}
        f=TTFont(ROOT/'fonts'/names[key]);FONT[key]=(f,f.getGlyphSet(),f.getBestCmap(),f['head'].unitsPerEm)
    return FONT[key]

def width(s,size,key='cn',spacing=0):
    f,gs,cm,u=font(key)
    for c in s:
        if ord(c) not in cm: raise ValueError(f'Missing glyph {c!r} in {key}')
    return sum(f['hmtx'][cm[ord(c)]][0]*size/u for c in s)+max(0,len(s)-1)*spacing

def text(s,x,y,size,key='cn',fill='#080808',spacing=0,maxw=None):
    tw=width(s,size,key,spacing)
    if maxw and tw>maxw:raise ValueError(f'Title overflow: {s!r}, {tw:.1f}px > {maxw}px. Shorten headline or set explicit headlineLines; text is never dropped.')
    f,gs,cm,u=font(key);scale=size/u;parts=[];cursor=0;maxY=-1e9
    for c in s:
        gn=cm[ord(c)];bp=BoundsPen(gs);gs[gn].draw(bp)
        if bp.bounds:maxY=max(maxY,bp.bounds[3])
    baseline=y+max(0,maxY)*scale
    for c in s:
        gn=cm[ord(c)];pen=SVGPathPen(gs);gs[gn].draw(pen);path=pen.getCommands()
        if path:parts.append(f'<path d="{path}" transform="translate({x+cursor:.4f} {baseline:.4f}) scale({scale:.6f} {-scale:.6f})"/>')
        cursor+=f['hmtx'][gn][0]*scale+spacing
    return f'<g fill="{fill}" aria-label="{html.escape(s)}">'+''.join(parts)+'</g>'

def image(name,x,y,theme):
    im=Image.open(ROOT/'assets'/f'{name}.png').convert('RGBA')
    if theme=='deep-purple' and name!='paper':
        import colorsys
        target=tuple(int(THEMES[theme]['accent'][i:i+2],16)/255 for i in (1,3,5));th,ts,tv=colorsys.rgb_to_hsv(*target)
        pix=im.load()
        for yy in range(im.height):
            for xx in range(im.width):
                r,g,b,a=pix[xx,yy];hh,ss,vv=colorsys.rgb_to_hsv(r/255,g/255,b/255)
                if b>r*1.13 and b>g*1.15 and ss>.15:
                    nr,ng,nb=colorsys.hsv_to_rgb(th,ss*.82,max(0,min(1,vv*.83)))
                    pix[xx,yy]=(round(nr*255),round(ng*255),round(nb*255),a)
    bio=io.BytesIO();im.save(bio,format='PNG')
    return f'<image x="{x}" y="{y}" width="{im.width}" height="{im.height}" href="data:image/png;base64,{base64.b64encode(bio.getvalue()).decode()}"/>'

def build(data,name):
    theme=data['theme'];accent=THEMES[theme]['accent'];deep=THEMES[theme]['shadow'];dt=datetime.fromisoformat(data['date']).replace(tzinfo=ZoneInfo(data['timezone']))
    weekday='星期'+'一二三四五六日'[dt.weekday()]
    items=data['items'];assert len(items)==4,'Cover layout requires exactly four items.'
    lines=[]
    add=lines.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{html.escape(data["exampleNotice"])} {dt:%Y-%m-%d}</title>')
    add(f'<defs><linearGradient id="purple"><stop stop-color="{accent}"/><stop offset="1" stop-color="{deep}"/></linearGradient></defs>')
    add(image('paper',0,0,theme));add(image('masthead',35,70,theme))
    add(text('AI DAILY',46,29,36,spacing=30))
    add('<path d="M795 30V271" stroke="#151515" stroke-width="1.5"/>')
    add(text(dt.strftime('%Y.%m'),835,32,39,'regular'))
    add('<path d="M835 77H1047" stroke="#151515" stroke-width="1.5"/>')
    # Date uses true font outlines, no severe compression or fake strokes.
    add(text(dt.strftime('%d'),830,86,180,'cn',maxw=220))
    add('<rect x="835" y="234" width="212" height="36" fill="url(#purple)"/>')
    add(text(weekday,848,242,25,'regular',fill='white',spacing=4))
    for y,sw in [(287,4),(298,1.5),(373,1.5),(773,1.5),(972,1.5),(1169,1.5),(1368,3.5),(1376,1.3)]:add(f'<path d="M40 {y}H1047" stroke="#111" stroke-width="{sw}"/>')
    xx=40
    for s,c in [('今日 ', '#080808'),(str(len(items)),accent),(' 条 · ', '#080808'),(str(data['readMinutes']),accent),(' 分钟速览','#080808')]:
        add(text(s,xx,315,48.5,fill=c));xx+=width(s,48.5)
    add('<path d="M977 349l18-29m-2 29l18-29m-2 29l18-29m-2 29l18-29" fill="none" stroke="#111" stroke-width="1.6"/>')
    for i,it in enumerate(items):
        top=[416,800,1000,1196][i];labelx=[184,181,182,182][i];labely=[423,804,1004,1200][i]
        add(text(str(it['number']).zfill(2),42,top,69,'serif',maxw=101))
        add(f'<path d="M152 {labely}v46" stroke="#111" stroke-width="1.5"/>')
        lw=max(148,width(it['category'],30)+34)
        if lw>240:raise ValueError(f'Category too long: {it["category"]}')
        add(f'<rect x="{labelx}" y="{labely}" width="{lw:.1f}" height="46" fill="url(#purple)"/>')
        add(text(it['category'],labelx+18,labely+10,30,fill='#fff'))
        pos={'neural-sphere':(498,378),'video-layers':(748,787),'code-layers':(692,983),'city':(719,1176)}
        add(image(it['illustration'],*pos[it['illustration']],theme))
        if i==0:
            hl=it.get('headlineLines') or [it['headline']]
            if len(hl)!=2:raise ValueError('Headline 01 requires two explicit headlineLines.')
            add(text(hl[0],43,500,110,maxw=460));add(text(hl[1],43,631,88,maxw=640))
            add(f'<path d="M66 739Q143 724 213 733" fill="none" stroke="{accent}" stroke-width="8" stroke-linecap="round"/>')
        else:
            hl=it.get('headlineLines') or [it['headline']]
            if len(hl)>1:raise ValueError(f'Short item {i+1} must remain one line in this cover template.')
            sz=68;limit=[0,671,640,666][i]
            while width(hl[0],sz)>limit and sz>59:sz-=.5
            add(text(hl[0],43,[0,875,1074,1272][i],sz,maxw=limit))
    add(text(data['exampleNotice'],40,1398,18,'regular'))
    hint=data['footerHint'];add(text(hint,700,1395,23,'regular',maxw=183))
    add('<path d="M910 1390v32" stroke="#111" stroke-width="1.5"/>')
    add(text(f"{data['pageIndex']:02d}",937,1393,33,'serif'))
    add(text('/',984,1390,34,fill=accent));add(text(f"{data['pageCount']:02d}",1006,1396,28,'date'))
    add('</svg>');svg=''.join(lines)
    (ROOT/'output'/f'{name}.svg').write_text(svg)
    (ROOT/'output'/f'{name}.html').write_text('<!doctype html><html><meta charset="utf-8"><style>html,body{margin:0;width:1086px;height:1448px;overflow:hidden}svg{display:block}</style>'+svg+'</html>')
    return {'name':name,'date':dt.strftime('%Y-%m-%d'),'weekday':weekday,'theme':theme,'all_glyphs_outlined':True,'overflow':False}

def export(names):
    import os,tempfile
    tmp=ROOT/'analysis/browser-tmp';tmp.mkdir(exist_ok=True)
    os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True,args=['--disable-background-networking'])
        try:
            for name in names:
                for scale in ([1,2] if name in ('reference','custom') else [1]):
                    context=browser.new_context(viewport={'width':W,'height':H},device_scale_factor=scale)
                    page=context.new_page();page.goto((ROOT/'output'/f'{name}.html').as_uri(),wait_until='load')
                    page.evaluate('async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')
                    page.locator('svg').screenshot(path=str(ROOT/'output'/f'{name}{"@2x" if scale==2 else ""}.png'))
                    context.close()
        finally:browser.close()

def comparisons():
    a=Image.open(ROOT/'reference/reference.png').convert('RGB');b=Image.open(ROOT/'output/reference.png').convert('RGB')
    side=Image.new('RGB',(W*2,H));side.paste(a);side.paste(b,(W,0));side.save(ROOT/'comparison/side-by-side.png')
    Image.blend(a,b,.5).save(ROOT/'comparison/overlay-50.png')
    b.resize((360,480),Image.Resampling.LANCZOS).save(ROOT/'comparison/phone-360.png')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--config');args=ap.parse_args();prepare();checks=[]
    if args.config:
        d=json.loads(Path(args.config).read_text());checks.append(build(d,'custom'));names=['custom']
    else:
        d=json.loads((ROOT/'config/baseline.json').read_text());checks.append(build(d,'reference'))
        d['theme']='deep-purple';checks.append(build(d,'deep-purple'))
        d=json.loads((ROOT/'config/replacement.json').read_text());checks.append(build(d,'replacement'));names=['reference','deep-purple','replacement']
    export(names)
    if 'reference' in names:comparisons()
    (ROOT/'analysis/validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
    print(json.dumps(checks,ensure_ascii=False))
