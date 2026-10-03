#!/usr/bin/env python3
"""Helpers for build.py (zfarber.com). Data lives in ../harvest/*.txt."""
import re, sys, os, base64, html, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
HARVEST = os.path.join(ROOT, '..', 'harvest')
ARTIFACT = '--artifact' in sys.argv
SITE = '--site' in sys.argv
OUT = os.path.join(ROOT, '..', 'dist') if SITE else os.path.join(ROOT, 'dist')  # site mode builds to repo-root dist/
PDF_MAP = {}  # old Wix url -> /pdf/slug.pdf (filled by build.py)
os.makedirs(OUT, exist_ok=True)

# ---------- data ----------
def parse(name):
    """Return list of ('h2', text) | ('h3', text) | ('link', title, url) | ('blurb', text)."""
    items = []
    with open(os.path.join(HARVEST, name + '.txt'), encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip():
                continue
            if line.startswith('### '):
                items.append(('h3', line[4:].strip()))
            elif line.startswith('## '):
                items.append(('h2', line[3:].strip()))
            elif line.startswith('> '):
                items.append(('blurb', line[2:].strip()))
            elif ' | ' in line:
                t, u = line.rsplit(' | ', 1)
                items.append(('link', t.strip(), u.strip()))
    return items

def clean_amazon(u):
    m = re.search(r'amazon\.com/.*?/dp/([A-Z0-9]{10})', u)
    return f'https://www.amazon.com/dp/{m.group(1)}' if m else u

def is_hebrew(s):
    return bool(re.search(r'[֐-׿]', s))

def esc(s):
    return html.escape(s, quote=True)

def strip_prefix(t):
    return re.sub(r'^(ACADEMIC|Book|Q&A|Film Review):\s*', '', t)

def tag_for(t, u):
    if t.startswith('ACADEMIC:') or 'academia.edu' in u or 'mdpi.com' in u or 'academic.oup.com' in u:
        return 'paper'
    if t.startswith('Q&A:') or 'jewishvaluesonline' in u:
        return 'Q&A'
    if '.pdf' in u:
        return 'PDF'
    if 'hartman.org.il' in u:
        return 'Hebrew'
    if 'youtube.com' in u:
        return 'video'
    if 'amazon.com' in u:
        return 'book'
    return ''

def slugify(t):
    t = strip_prefix(t)
    t = re.sub(r"[’'\"]", '', t)
    t = re.sub(r'[^A-Za-z0-9]+', '-', t).strip('-')
    return t[:70].rstrip('-')

def link_li(t, u):
    tag = tag_for(t, u)
    title = strip_prefix(t)
    u = clean_amazon(u)
    if 'zfarber.com/_files/' in u:
        PDF_MAP.setdefault(u, '/pdf/' + slugify(t) + '.pdf')
        if SITE:
            u = PDF_MAP[u]
    attrs = ' lang="he" dir="rtl"' if is_hebrew(title) else ''
    tagh = f' <span class="tag">{esc(tag)}</span>' if tag else ''
    if u in ('—', '-', 'NOTFOUND'):
        return f'<li><span class="nolink"{attrs}>{esc(title)}</span>{tagh}</li>'
    return f'<li><a href="{esc(u)}"{attrs}>{esc(title)}</a>{tagh}</li>'

def render_list(items, wrap_h2='h3', wrap_h3='h4', two_col=True):
    """Items -> HTML with headings and <ul>s. A '##' directly before a '###' is swapped so the book name leads."""
    fixed = []
    i = 0
    while i < len(items):
        if items[i][0] == 'h2' and i + 1 < len(items) and items[i + 1][0] == 'h3':
            fixed.append(items[i + 1]); fixed.append(items[i]); i += 2
        else:
            fixed.append(items[i]); i += 1
    out = []
    ul_open = False
    def close():
        nonlocal ul_open
        if ul_open:
            out.append('</ul>'); ul_open = False
    for it in fixed:
        if it[0] in ('h2', 'h3'):
            close()
            tag = wrap_h2 if it[0] == 'h2' else wrap_h3
            out.append(f'<{tag}>{esc(it[1].title() if it[1].isupper() else it[1])}</{tag}>')
        elif it[0] == 'link':
            if not ul_open:
                out.append(f'<ul class="arch{" cols" if two_col else ""}">'); ul_open = True
            out.append(link_li(it[1], it[2]))
        elif it[0] == 'blurb':
            close()
            out.append(f'<p class="blurb">{esc(it[1])}</p>')
    close()
    return '\n'.join(out)
