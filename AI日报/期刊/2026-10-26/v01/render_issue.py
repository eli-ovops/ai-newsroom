#!/usr/bin/env python3
"""This issue only: reuse master build/export and detail Page, with local content layouts."""
from pathlib import Path
import importlib.util, json, base64, sys
from PIL import Image

ISSUE = Path(__file__).resolve().parent
DAILY = ISSUE.parents[2]
spec = importlib.util.spec_from_file_location('daily_details', DAILY / 'render_details.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m, C = d.m, d.C
OUT = ISSUE / 'output'
NAMES = ['01-cover', '02-minimax', '03-gpu', '04-tv', '05-pathos']

def photo(x, y, w):
    raw = (ISSUE / 'assets/aerial-home.jpg').read_bytes()
    return f'<image x="{x}" y="{y}" width="{w}" height="{w * 9 / 16}" href="data:image/jpeg;base64,{base64.b64encode(raw).decode()}"/>'

def cover(data):
    # Use the original masthead, grid, headline metrics, paper, date and pagination.
    # Only substitute content-relevant art in the four original illustration slots.
    original_image, original_text = m.image, m.text
    def issue_image(name, x, y, theme):
        if name == 'neural-sphere':
            return '<g transform="translate(690 455) scale(1.1)">' + original_image('video-layers', 0, 0, theme) + '</g>' + original_text('社区项目', 789, 698, 34, fill=C)
        if name == 'video-layers':
            return original_text('看任务', 815, 856, 46, fill=C) + original_text('作者测试', 817, 921, 28, 'regular')
        if name == 'code-layers':
            return photo(798, 998, 249)
        if name == 'city':
            return original_text('研发合作', 807, 1223, 38, fill=C) + original_text('10.23公告', 807, 1284, 29, 'regular')
        return original_image(name, x, y, theme)
    def issue_text(s, x, y, size, key='cn', **kwargs):
        if s == data['exampleNotice']:
            size = 26
        return original_text(s, x, y, size, key, **kwargs)
    m.image, m.text = issue_image, issue_text
    try:
        result = m.build(data, '01-cover')
    finally:
        m.image, m.text = original_image, original_text
    return result

def minimax(data):
    p = d.Page(data, 2, 5)
    p.t('11', 40, 678, 174, fill=C)
    p.t('项社区项目', 298, 693, 48)
    p.block(['参考图视频、服务部署、工作流', '集中到一份索引，按需求找入口。'], 300, 771, 36, 54)
    p.parts.append(d.line(915))
    p.t('按设备与版本选方案', 40, 954, 39, fill=C)
    p.t('GPU  ·  云端TPU  ·  Apple Silicon', 40, 1020, 43)
    p.block(['部分项目仍在预览或实验阶段。', '速度、硬件配置和模型条款，要对应具体项目。'], 40, 1111, 36, 55)
    p.finish(OUT, '02-minimax')

def gpu(data):
    p = d.Page(data, 3, 5)
    rows = data['tests']
    for i, row in enumerate(rows):
        y = 666 + i * 167
        p.t(row['value'], 40, y + 28, row['valueSize'], fill=C if i < 2 else d.INK, maxw=295)
        p.t(row['label'], 367, y + 7, 38, maxw=680)
        p.block(row['lines'], 367, y + 66, 31, 44, maxw=680)
        p.parts.append(d.line(y + 151))
    p.block(['依赖Linux、具体显卡与驱动，不等于所有AI任务提速，', '更不是显存翻倍。'], 40, 1167, 32, 40)
    p.finish(OUT, '03-gpu')

def tv(data):
    p = d.Page(data, 4, 5)
    p.parts.append(photo(40, 663, 620))
    p.t('Aerial', 706, 671, 54)
    p.block(['应用 · 壁纸 · 屏保', '组成新的电视桌面'], 706, 752, 31, 45, maxw=341)
    p.t('10.26版本更新', 706, 888, 32, fill=C, maxw=341)
    p.block(['既有开源方案', '并非今天首次出现'], 706, 945, 30, 44, maxw=341)
    p.t('作者项目截图 · pengchujin / Aerial', 40, 1031, 27, 'regular', fill=d.GREY)
    p.parts.append(d.line(1077))
    p.t('只换桌面，不会去掉所有广告', 40, 1100, 36, fill=C)
    p.block(['固件开机广告、各App视频广告仍在。需机型支持、', '电脑电视同网，并由机主允许ADB调试与安装。'], 40, 1155, 34, 45)
    p.finish(OUT, '04-tv')

def pathos(data):
    p = d.Page(data, 5, 5)
    p.tag('10月23日公布 · 研发合作', 662)
    for i, step in enumerate(data['steps']):
        x = [40, 395, 750][i]
        p.t(f'{i + 1:02d}', x, 750, 70, 'serif', fill=C)
        p.t(step['title'], x, 846, 38, maxw=297)
        p.block(step['lines'], x, 911, 33, 48, maxw=297)
        if i < 2:
            p.t('→', x + 280, 770, 48, 'regular')
    p.parts.append(d.line(1032))
    p.t('尚未公布这项合作的疗效或新药上市结果', 40, 1070, 39, maxw=1007)
    p.block(['公告计划覆盖数十万神经疾病患者的数据，', '不等于这些人已参加阿尔茨海默病治疗试验。'], 40, 1150, 35, 52)
    p.finish(OUT, '05-pathos')

def main():
    OUT.mkdir(exist_ok=True)
    m.OUT = OUT
    content = json.loads((ISSUE / 'content.json').read_text())
    details = json.loads((ISSUE / 'details.json').read_text())
    targets = sys.argv[1:] or NAMES
    assert set(targets) <= set(NAMES)
    result = cover(content) if '01-cover' in targets else {'status': 'unchanged; previous render retained'}
    for renderer, item, name in zip([minimax, gpu, tv, pathos], details, NAMES[1:]):
        if name not in targets:
            continue
        item.update(issueDate=content['date'], weekday='星期一')
        renderer(item)
    m.export(targets)
    for name in targets:
        im = Image.open(OUT / f'{name}.png')
        assert im.size == (1086, 1448)
        im.resize((390, 520), Image.Resampling.LANCZOS).save(OUT / f'{name}-390.png')
    (OUT / 'render-check.json').write_text(json.dumps({'cover': result, 'pages': NAMES, 'last_exported': targets, 'size': [1086, 1448], 'master_reused': True, 'detail_Page_reused': True, 'new_fonts': False, 'reextracted_assets': False, 'browser_closed': True, 'visual_review': 'See delivery.json for actual review scope'}, ensure_ascii=False, indent=2))
    print(json.dumps({'exported': targets, 'output': str(OUT)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
