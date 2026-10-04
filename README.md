# zfarber.com

Static site for Zev I. Farber. No framework; Python generates the HTML. Hosted on GitHub Pages from `docs/`.

- `site/build.py`, `site/build_helpers.py` — generator
- `site/style.css`, `site/img/` — copied into `docs/` on build
- `harvest/*.txt` — link lists that populate the archive pages (`title | url`, `## headings`, `> blurbs`)
- `docs/` — build output, committed; GitHub Pages serves it. Also holds `pdf/` (17 PDFs from the old site), forwarding pages at the old Wix paths, copies of the PDFs at their old `_files/ugd/` addresses, `.nojekyll`, `sitemap.xml`, `robots.txt`, `404.html`.
- `fetch_pdfs.py` — re-downloads the PDFs into `docs/pdf/` if ever needed (list in `site/pdf-list.txt`)

Build: `python3 site/build.py --site`, then commit and push; GitHub Pages publishes `docs/` from `main`.

Forms (Speaking, Contact) post to Formspree; the endpoint is the `FORMSPREE` constant near the top of `site/build.py`. Submissions arrive by email at zevfarber@gmail.com.
