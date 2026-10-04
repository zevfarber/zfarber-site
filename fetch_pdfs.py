#!/usr/bin/env python3
"""Download the 17 PDFs still hosted on the old Wix site into docs/pdf/.
Run from the repo root after a build: python3 fetch_pdfs.py"""
import os, re, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, 'docs', 'pdf'), exist_ok=True)
with open(os.path.join(HERE, 'site', 'pdf-list.txt'), encoding='utf-8') as f:
    for line in f:
        if not line.startswith('http'): continue
        url, dest = [s.strip() for s in line.split(' -> ', 1)]
        path = os.path.join(HERE, dest)
        if os.path.exists(path): print('have', dest); continue
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, 'wb') as out:
            out.write(r.read())
        print('saved', dest)
