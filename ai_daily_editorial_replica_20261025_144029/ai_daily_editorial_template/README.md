# AI 日报总结封面

固定画布 1086 × 1448。此包为排版示例，不包含真实当日新闻。固定报头和四组拼贴从用户参考图提取；所有日期、星期、分类、新闻、页脚由 JSON 重新排版。

## 每天怎么改

1. 修改 `config/baseline.json`。`date` 填 `YYYY-MM-DD`；年月、日和星期由该字段统一计算，时区为 `Asia/Shanghai`，不会自动改成运行当天。
2. 第一条修改 `headlineLines` 的两行，其余三条修改 `headline`。`category` 是分类。`illustration` 可选 `neural-sphere`、`video-layers`、`code-layers`、`city`。保持四条。
3. `theme` 设 `reference` 或 `deep-purple`；主题值集中在 `config/themes.json`。深紫主色为 `#481C8E`，插图按同色相保留明暗。
4. `readMinutes` 为人工配置的阅读时间；不是自动统计值。`pageIndex`、`pageCount`、`footerHint`、`exampleNotice` 可独立修改。发布真实消息时需自行核实内容，再修改“排版示例”提示。
5. 在本目录执行：

```bash
python3 build.py --config config/baseline.json
```

输出在 `output/custom.png`、`output/[REDACTED_EMAIL]`，以及同名 SVG/HTML。全套示例可用 `python3 build.py` 重建。

标题太长会明确报错，保留全文，不擅自改写。第一条建议第一行不超过四个全角字、第二行七个；短讯约十至十一个全角字，混合英文按实际宽度判断。短讯仅在 59–68px 范围调整字号；仍过长请压缩措辞。`headlineLines` 存在时优先于 `headline`。不需要改坐标。

## 文件

- `output/reference.png`：原尺寸基准；`[REDACTED_EMAIL]`：2172 × 2896。
- `output/deep-purple.png`：深紫版；`replacement.png`：10月26日星期一、四条新示例及新分类。
- `comparison/side-by-side.png`：左原图、右复刻；`overlay-50.png`：同尺寸50%叠加；`phone-three-versions.png`：360px宽手机阅读检查。
- `assets/`：独立透明插图、固定品牌报头、纸面纹理及提取坐标。
- `fonts/`：开源 Noto CJK Black/Regular、Noto Serif Display、Anton 及许可/来源。原字体身份未知；Noto Serif Display Black 为原变量字体的实例。
- `analysis/`：字体候选对照、尺寸/溢出/重复导出检查；`VISUAL-DIFFERENCES.md`：差异说明。

## 环境和导出

本机已使用 Python 3、Pillow、fontTools、Playwright 和 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` 实际完成导出，具体版本见 `analysis/checks.json`。未安装全局依赖、未联网加载字体、未启动HTTP服务。缺少 Python 依赖时可在本目录 `.venv` 内安装 `requirements.txt`；不需要 Playwright 另下浏览器。

渲染为一次性本地文件渲染，临时浏览器目录位于本任务 `analysis/browser-tmp`，完成后关闭浏览器。字体逐字检查后生成矢量轮廓，无运行时字体回退；JSON 是日常编辑入口，SVG 内文字轮廓由脚本重新生成。2倍图让文字/线条更清晰，但不会恢复原插图不存在的细节。

参考图原件只读，SHA见 `analysis/checks.json`。原插图使用范围以用户持有的权利为准；本包不对原图权属作额外声明。
