#!/usr/bin/env python3
"""마크다운 → Confluence storage XHTML.

기존 md2conf.py 와 다른 점은 두 가지뿐이다.
  1. [텍스트](URL) 를 실제 <a href> 하이퍼링크로 변환한다.
  2. 콜아웃(인용문)을 선두 이모지에 따라 tip/note/warning/info 매크로로 나눠 색을 달리한다.
나머지(표·목록·이미지·제목)는 동일하게 처리한다.
"""
import re, html, sys

def esc(t): return html.escape(t, quote=False)

def inline(t):
    # 링크를 먼저 자리표시자로 빼둔다 (escape 로 URL 이 망가지지 않게)
    links = []
    def stash(m):
        links.append((m.group(1), m.group(2)))
        return f'\x00LINK{len(links)-1}\x00'
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', stash, t)

    t = esc(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    # storage format 은 XML 로 파싱된다 — &nbsp; 는 미정의 엔티티라 수치 참조를 쓴다
    t = t.replace('&amp;nbsp;', '&#160;')

    # 남은 맨 URL 도 링크로
    t = re.sub(r'(?<![">\x00])(https?://[^\s<]+)',
               lambda m: f'<a href="{html.escape(m.group(1), quote=True)}">{m.group(1)}</a>', t)

    for i, (txt, url) in enumerate(links):
        a = f'<a href="{html.escape(url, quote=True)}">{esc(txt)}</a>'
        t = t.replace(f'\x00LINK{i}\x00', a)
    return t

MACRO = {'ok':'tip', 'warn':'note', 'bad':'warning', 'info':'info'}

def convert(md):
    lines = md.split('\n'); out=[]; i=0; n=len(lines)
    while i < n:
        L = lines[i]; s = L.strip()

        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', s)
        if m:
            out.append('<p><ac:image ac:width="900" ac:alt="%s"><ri:attachment ri:filename="%s" /></ac:image></p>'
                       % (html.escape(m.group(1), quote=True), m.group(2)))
            i+=1; continue

        if s.startswith('```'):
            j=i+1; buf=[]
            while j<n and not lines[j].strip().startswith('```'):
                buf.append(lines[j]); j+=1
            out.append('<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[%s]]></ac:plain-text-body></ac:structured-macro>'
                       % '\n'.join(buf))
            i=j+1; continue

        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            lv = len(m.group(1))
            if lv == 1: i+=1; continue      # 제목은 페이지 title 로 별도 처리
            out.append('<h%d>%s</h%d>' % (lv, inline(m.group(2)), lv))
            i+=1; continue

        if s.startswith('---') and set(s) <= set('-'):
            out.append('<hr />'); i+=1; continue

        if s.startswith('>'):
            buf=[]
            while i<n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip()); i+=1
            parts=[x for x in buf if x]
            kind='info'
            for mark,k in (('✅','ok'), ('⚠️','warn'), ('🔴','bad'), ('📌','info')):
                if parts and parts[0].lstrip().startswith(mark): kind=k; break
            inner = ''.join('<p>%s</p>' % inline(x) for x in parts)
            out.append('<ac:structured-macro ac:name="%s"><ac:rich-text-body>%s</ac:rich-text-body></ac:structured-macro>'
                       % (MACRO[kind], inner))
            continue

        if s.startswith('|'):
            rows=[]
            while i<n and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip()); i+=1
            cells=[[c.strip() for c in r.strip('|').split('|')] for r in rows]
            head=None; body=cells
            if len(cells)>=2 and set(cells[1][0].replace(' ','')) <= set('-:'):
                head, body = cells[0], cells[2:]
                if not any(c.strip() for c in head):   # 빈 헤더 행은 만들지 않는다
                    head, body = None, cells[:1]+cells[2:]
            t=['<table><tbody>']
            if head:
                t.append('<tr>'+''.join('<th>%s</th>'%inline(c) for c in head)+'</tr>')
            for r in body:
                t.append('<tr>'+''.join('<td>%s</td>'%inline(c) for c in r)+'</tr>')
            t.append('</tbody></table>')
            out.append(''.join(t)); continue

        if re.match(r'^[-*]\s+', s):
            items=[]
            while i<n and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*]\s+','',lines[i].strip())); i+=1
            out.append('<ul>'+''.join('<li>%s</li>'%inline(x) for x in items)+'</ul>'); continue

        if re.match(r'^\d+\.\s+', s):
            items=[]
            while i<n and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(re.sub(r'^\s*\d+\.\s+','',lines[i].strip())); i+=1
            out.append('<ol>'+''.join('<li>%s</li>'%inline(x) for x in items)+'</ol>'); continue

        if not s: i+=1; continue

        buf=[]
        while i<n and lines[i].strip() and not re.match(r'^(#|\||>|```|[-*]\s|\d+\.\s|!\[|---)', lines[i].strip()):
            buf.append(lines[i].strip()); i+=1
        if buf:
            out.append('<p>%s</p>' % '<br />'.join(inline(x) for x in buf))
    return '\n'.join(out)

if __name__ == '__main__':
    md = open(sys.argv[1]).read()
    title = re.search(r'^#\s+(.*)$', md, re.M).group(1)
    open(sys.argv[2],'w').write(convert(md))
    print(title)
