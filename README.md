# zfarber.com

Static site for Zev I. Farber. No framework; Python generates the HTML.

- `site/build.py`, `site/build_helpers.py` — generator
- `site/style.css`, `site/img/` — copied into `dist/` on build
- `harvest/*.txt` — link lists that populate the archive pages (`title | url`, `## headings`, `> blurbs`)
- `site/pdf-list.txt` — PDFs still on the old Wix host; `fetch_pdfs.py` downloads them into `dist/pdf/`
- `dist/` — build output (committed, so Netlify can also deploy without building)

Build: `python3 site/build.py --site` (from anywhere). Then `python3 fetch_pdfs.py` once.

Netlify: publish directory `dist`; forms on speaking/contact pages use Netlify Forms (`data-netlify`), notifications to zevfarber@gmail.com. `dist/_redirects` maps old Wix paths and PDF URLs to the new pages.
