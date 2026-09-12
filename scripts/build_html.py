#!/usr/bin/env python3
"""마크다운 → 단일 HTML. 다이어그램은 SVG 를 인라인해 자체 완결로 만든다."""
import re, html, sys, os, base64

def esc(t): return html.escape(t, quote=False)

def inline(t):
    # [텍스트](URL) 링크를 자리표시자로 빼둔다 (escape 로 URL 이 망가지지 않게)
    links = []
    def stash(m):
        links.append((m.group(1), m.group(2)))
        return f'\x00LINK{len(links)-1}\x00'
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', stash, t)
    t = esc(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    # [1] 각주 → 출처 앵커
    t = re.sub(r'\[(\d+)\]', r'<a class="ref" href="#src-\1">[\1]</a>', t)
    # 남은 맨 URL → 링크
    t = re.sub(r'(?<![">\x00])(https?://[^\s<]+)', r'<a href="\1">\1</a>', t)
    # 원문에 쓴 HTML 엔티티는 살려둔다 (esc 로 &amp; 가 된 것을 되돌림)
    t = t.replace('&amp;nbsp;', '&nbsp;')
    for i, (txt, url) in enumerate(links):
        t = t.replace(f'\x00LINK{i}\x00', f'<a href="{html.escape(url, quote=True)}">{esc(txt)}</a>')
    return t

def slug(t):
    return re.sub(r'[^\w가-힣]+', '-', t).strip('-').lower()

def convert(md, imgdir):
    lines = md.split('\n'); out=[]; toc=[]; i=0; n=len(lines)
    in_sources = False   # 출처 절에서만 src- 앵커를 만든다 (각주 링크 충돌 방지)
    while i < n:
        s = lines[i].strip()
        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', s)
        if m:
            alt, fn = m.group(1), m.group(2)
            svg = os.path.join(imgdir, os.path.splitext(fn)[0] + '.svg')
            if os.path.exists(svg):
                body = open(svg).read()
                body = re.sub(r'<\?xml[^>]*\?>', '', body)
                body = re.sub(r'<!DOCTYPE[^>]*>', '', body)
                out.append(f'<figure class="diagram">{body}<figcaption>{esc(alt)}</figcaption></figure>')
            else:
                out.append(f'<figure class="diagram"><img src="{fn}" alt="{esc(alt)}"><figcaption>{esc(alt)}</figcaption></figure>')
            i+=1; continue
        if s.startswith('```'):
            j=i+1; buf=[]
            while j<n and not lines[j].strip().startswith('```'):
                buf.append(lines[j]); j+=1
            out.append('<pre><code>%s</code></pre>' % esc('\n'.join(buf)))
            i=j+1; continue

        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            lv, txt = len(m.group(1)), m.group(2)
            if lv == 1:
                out.append(f'<h1>{inline(txt)}</h1>')
            else:
                sid = slug(txt)
                if lv == 2:
                    toc.append((sid, txt))
                    in_sources = txt.strip().startswith('출처')
                out.append(f'<h{lv} id="{sid}">{inline(txt)}</h{lv}>')
            i+=1; continue
        if s.startswith('---') and set(s) <= set('-'):
            out.append('<hr>'); i+=1; continue
        if s.startswith('>'):
            buf=[]
            while i<n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip()); i+=1
            parts = [x for x in buf if x]
            # 선두 이모지로 콜아웃 종류를 판별해 색을 입힌다
            kind = 'info'
            for mark, k in (('✅','ok'), ('⚠️','warn'), ('🔴','bad'), ('📌','info')):
                if parts and parts[0].lstrip().startswith(mark): kind = k; break
            # 줄마다 inline 을 먼저 돌린 뒤 <br> 로 잇는다 (br 이 escape 되지 않도록)
            html_txt = '<br>'.join(inline(x) for x in parts)
            out.append(f'<blockquote class="cal-{kind}">{html_txt}</blockquote>'); continue
        if s.startswith('|'):
            rows=[]
            while i<n and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i+=1
            cells=[[c.strip() for c in r.strip('|').split('|')] for r in rows]
            head=None; body=cells
            if len(cells)>=2 and set(cells[1][0].replace(' ','')) <= set('-:'):
                head, body = cells[0], cells[2:]
                # 헤더가 전부 빈 칸이면 헤더 행을 만들지 않는다 (빈 회색 띠 방지)
                if not any(c.strip() for c in head): head = None
            t=['<div class="tw"><table>']
            if head: t.append('<thead><tr>'+''.join(f'<th>{inline(c)}</th>' for c in head)+'</tr></thead>')
            t.append('<tbody>')
            def cell(c):
                s = c.lstrip()
                cls = ''
                if s.startswith('✅') or s.startswith('🟢'): cls = ' class="v-ok"'
                elif s.startswith('❌') or s.startswith('🔴'): cls = ' class="v-no"'
                elif s.startswith('⚠️') or s.startswith('🟡'): cls = ' class="v-mid"'
                return f'<td{cls}>{inline(c)}</td>'
            for r in body: t.append('<tr>'+''.join(cell(c) for c in r)+'</tr>')
            t.append('</tbody></table></div>')
            out.append(''.join(t)); continue
        if re.match(r'^[-*]\s+', s):
            items=[]
            while i<n and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*]\s+','',lines[i].strip())); i+=1
            out.append('<ul>'+''.join(f'<li>{inline(x)}</li>' for x in items)+'</ul>'); continue
        if re.match(r'^\d+\.\s+', s):
            items=[]; start=None
            while i<n and re.match(r'^\s*\d+\.\s+', lines[i]):
                num = re.match(r'^\s*(\d+)\.', lines[i]).group(1)
                if start is None: start = num
                items.append((num, re.sub(r'^\s*\d+\.\s+','',lines[i].strip()))); i+=1
            if in_sources:
                lis = ''.join(f'<li id="src-{num}">{inline(x)}</li>' for num,x in items)
            else:
                lis = ''.join(f'<li>{inline(x)}</li>' for _,x in items)
            out.append(f'<ol start="{start}">{lis}</ol>'); continue
        if not s: i+=1; continue
        buf=[]
        while i<n and lines[i].strip() and not re.match(r'^(#|\||>|```|[-*]\s|\d+\.\s|!\[|---)', lines[i].strip()):
            buf.append(lines[i].strip()); i+=1
        if buf:
            out.append('<p>'+'<br>'.join(inline(x) for x in buf)+'</p>')
        else:
            i += 1   # 어떤 분기도 소비하지 못한 줄 — 무한 루프 방지
    return '\n'.join(out), toc

CSS = """
:root{--ink:#1F2D3D;--muted:#5A6B7D;--line:#DFE5EC;--bg:#FFFFFF;--accent:#2F6FB5;
--ok-bg:#E8F5E9;--ok-bd:#3B8C4E;--warn-bg:#FFF8E6;--warn-bd:#C9A227;}
*{box-sizing:border-box}
body{margin:0;background:#F4F6F9;color:var(--ink);
font-family:"Apple SD Gothic Neo","Noto Sans KR",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;
font-size:16px;line-height:1.75;-webkit-font-smoothing:antialiased}
.page{max-width:1040px;margin:0 auto;background:var(--bg);padding:64px 72px 96px;
box-shadow:0 1px 3px rgba(16,32,52,.08),0 12px 32px rgba(16,32,52,.06)}
h1{font-size:2.05rem;line-height:1.3;letter-spacing:-.02em;margin:0 0 28px;padding-bottom:20px;border-bottom:3px solid var(--ink)}
h2{font-size:1.4rem;letter-spacing:-.01em;margin:56px 0 18px;padding-top:8px;scroll-margin-top:20px}
h3{font-size:1.1rem;margin:32px 0 12px}
p{margin:0 0 16px}
hr{border:0;border-top:1px solid var(--line);margin:44px 0}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(47,111,181,.3);word-break:break-all}
a:hover{border-bottom-color:var(--accent)}
a.ref{border:0;font-size:.8em;vertical-align:super;font-weight:600;padding:0 1px}
code{background:#F0F3F7;border:1px solid #E2E8F0;border-radius:4px;padding:1px 5px;font-size:.88em;
font-family:"SF Mono",Menlo,Consolas,monospace;word-break:break-all}
strong{font-weight:700}
pre{margin:0 0 22px;padding:18px 22px;background:#F7F9FC;border:1px solid var(--line);
border-radius:10px;overflow-x:auto;line-height:1.7}
pre code{background:none;border:0;padding:0;font-size:.87rem;color:#25374B;white-space:pre}
ul,ol{margin:0 0 18px;padding-left:26px}
li{margin:0 0 8px}
ol li{padding-left:4px}
blockquote{margin:26px 0;padding:20px 26px;border-left:5px solid;border-radius:0 10px 10px 0;font-size:.97rem}
blockquote.cal-ok{background:#F1F9F2;border-color:#2F7D42}
blockquote.cal-ok strong{color:#1D5C2E}
blockquote.cal-warn{background:#FFF8E6;border-color:#C9A227}
blockquote.cal-warn strong{color:#6B5405}
blockquote.cal-bad{background:#FDF0EE;border-color:#D64545}
blockquote.cal-bad strong{color:#9B2C2C}
blockquote.cal-info{background:#F0F5FB;border-color:#3A78BF}
blockquote.cal-info strong{color:#1F4E82}
/* 제목 바로 아래 목적 문장 */
h1 + p{font-size:1.12rem;line-height:1.65;color:#33465C;margin:0 0 26px;
padding:16px 22px;background:#F7F9FC;border:1px solid var(--line);border-radius:10px}
h1 + p strong{color:var(--ink)}
.tw{overflow-x:auto;margin:0 0 24px;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:.92rem;line-height:1.6}
th{background:#F7F9FC;text-align:left;font-weight:700;color:#33465C;
padding:13px 16px;border-bottom:2px solid var(--line);white-space:nowrap}
td{padding:13px 16px;border-bottom:1px solid #EDF1F6;vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#FAFCFE}
td:first-child{font-weight:600;color:#25374B}
/* 판정 셀 — 선두 기호로 배경을 입혀 눈으로 스캔되게 한다 */
td.v-ok{background:#F2FAF3}
td.v-no{background:#FDF2F0}
td.v-mid{background:#FFFBF0}
figure.diagram{margin:32px 0;padding:28px 24px;background:#FBFCFE;
border:1px solid var(--line);border-radius:12px;text-align:center}
figure.diagram svg{max-width:100%;height:auto}
figure.diagram img{max-width:100%;height:auto}
figcaption{margin-top:18px;font-size:.85rem;color:var(--muted);letter-spacing:.01em}
nav.toc{margin:0 0 8px;padding:22px 26px;background:#F7F9FC;border:1px solid var(--line);border-radius:10px}
nav.toc b{display:block;font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:12px}
nav.toc ul{margin:0;padding-left:18px;columns:2;column-gap:36px;list-style:none}
nav.toc ul li::before{content:"›";color:#9AA9BA;margin-right:8px}
nav.toc li{margin:0 0 7px;break-inside:avoid}
nav.toc a{border:0;color:#33465C;font-size:.93rem}
nav.toc a:hover{color:var(--accent)}
@media print{body{background:#fff}.page{box-shadow:none;max-width:none;padding:0}
h2{page-break-after:avoid}figure.diagram,.tw,blockquote{page-break-inside:avoid}nav.toc{page-break-after:always}}
@media (max-width:880px){.page{padding:36px 22px 64px}nav.toc ol{columns:1}}
"""

if __name__ == '__main__':
    md_path, out_path, imgdir = sys.argv[1], sys.argv[2], sys.argv[3]
    md = open(md_path).read()
    title = re.search(r'^#\s+(.*)$', md, re.M).group(1)
    body, toc = convert(md, imgdir)
    tocht = ''
    if toc:
        # 제목에 이미 번호가 있으면 목차에서 중복 번호를 붙이지 않는다
        lis = ''.join(f'<li><a href="#{sid}">{esc(t)}</a></li>' for sid,t in toc)
        tocht = f'<nav class="toc"><b>목차</b><ul>{lis}</ul></nav>'
    # 목적 문장·메타표 다음(첫 <hr>)에 목차를 넣는다 — 결론이 목차보다 먼저 보이게
    if '<hr>' in body:
        body = body.replace('<hr>', tocht + '\n<hr>', 1)
    else:
        body = body.replace('</h1>', '</h1>\n' + tocht, 1)
    doc = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style></head>
<body><div class="page">{body}</div></body></html>"""
    open(out_path,'w').write(doc)
    print(f'{out_path}  ({len(doc):,} bytes, 목차 {len(toc)}개 절)')
