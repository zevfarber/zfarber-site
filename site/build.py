#!/usr/bin/env python3
"""Build zfarber.com (static). Usage: python3 build.py [--artifact]
--artifact: index.html emitted as a fragment (no doctype/html/head/body) for the Claude artifact; other pages are full documents published as files.
v2, 27 Sept 2026: the person first. Menu = About + topics (Religion, Bible, Halakha, Israel, Fiction).
Projects row = Prisma + TheTorah.com (live offers). Atlas alone as the one ask (funders and partners).
Products = books, course, Lectorium (beta). Every topic page ends with a hire-my-time verb.
"""
import re, sys, os, base64, html, shutil
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_helpers.py'), encoding='utf-8').read())

with open(os.path.join(ROOT, 'style.css'), encoding='utf-8') as f:
    CSS = f.read()

NAV = [('about.html', 'About'), ('religion.html', 'Religion'), ('bible.html', 'Bible'), ('halakha.html', 'Halakha'),
       ('israel.html', 'Israel'), ('fiction.html', 'Fiction')]

SOCIAL = [('LinkedIn', 'https://il.linkedin.com/in/zev-farber-3a9a586b'),
          ('Facebook', 'https://www.facebook.com/Zev.Israel.Farber/'),
          ('X / Twitter', 'https://twitter.com/FarberZev'),
          ('YouTube', 'https://www.youtube.com/@zev.i.farber')]

LINKS = {
    'torah_news': 'https://preview.mailerlite.com/webforms/landing/i9y0l8',
    'torah_author': 'https://www.thetorah.com/author/zev-farber',
    'prisma_list': 'https://prisma.guide/#signup',
    'prisma_journal': 'https://prismaguide.substack.com',
    'youtube': 'https://www.youtube.com/@zev.i.farber',
    'toi': 'https://blogs.timesofisrael.com/author/zev-farber/',
    'first_kings': 'https://www.amazon.com/dp/1009526332',
    'joshua': 'https://www.amazon.com/dp/3110338882',
    'judah': 'https://www.amazon.com/dp/0884143473',
    'brain': 'https://www.amazon.com/dp/1592644066',
    'organ': 'https://www.amazon.com/dp/1592644074',
    'two_wrongs': 'https://www.amazon.com/dp/B0BFJDSZH5',
    'doing': 'https://www.amazon.com/dp/B0CQW157D3',
    'airplane': 'https://www.amazon.com/dp/B0DFMWHQ78',
    'udemy': 'https://www.udemy.com/course/developmental-editing/',
    'lectorium': 'https://zevfarber.github.io/Lectorium/',
    'paintedwolf': 'https://paintedwolfpub.com/',
    'zevtime': 'https://open.spotify.com/show/6oFNoVtmnxMtt45odiofsA',
    'beyond': 'https://seekprophecy.substack.com/p/beyond-orthodoxy',
    'homosexuality': 'https://www.amazon.com/dp/B0HLL5H786',
}

DESCS = {
    'index.html': 'Zev I. Farber — Bible scholar, rabbi, founder and director of Prisma, Senior Editor at TheTorah.com, novelist as Z. I. Farber.',
    'about.html': 'About Zev I. Farber: positions, degrees, press.',
    'bible.html': 'Essays by Zev Farber on the Torah, Joshua and Judges, the holidays, theology, and Jewish education.',
    'halakha.html': 'Zev Farber on halakha: medical ethics, women, LGBTQ, conversion, and responsa.',
    'israel.html': "Zev Farber's commentary on Israel at the Times of Israel, 2011 to the present.",
    'religion.html': 'Zev Farber on religion in general: synergistic religion, Prisma, and the YouTube channel.',
    'fiction.html': 'Novels and stories by Z. I. Farber.',
    'books.html': 'Books by Zev I. Farber and Z. I. Farber, a course on editing, and Lectorium.',
    'speaking.html': 'Lectures, courses, and scholar-in-residence weekends with Rabbi Dr. Zev Farber.',
    'consulting.html': 'Private conversations on religious and theological questions with Rabbi Dr. Zev Farber.',
    'contact.html': 'Contact Zev I. Farber.',
}

def shell(page, title, body, fragment=False, body_class=''):
    CUR = ' aria-current="page"'
    nav = ''.join(f'<a href="{h}"{CUR if h == page else ""}>{t}</a>' for h, t in NAV)
    head = f'''<title>{esc(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300..700;1,8..60,300..700&family=Archivo:wght@400;500;600&display=swap">
<style>{CSS}</style>'''
    social = ' · '.join(f'<a href="{u}">{n}</a>' for n, u in SOCIAL)
    wrapper_open = f'<div class="site {body_class}">' if body_class else '<div class="site">'
    doc = f'''{head}
{wrapper_open}
<nav><div class="wrap"><a class="brand" href="index.html">Zev I. Farber</a><div class="menu">{nav}</div></div></nav>
{body}
<footer><div class="wrap"><span>© 2026 Zev I. Farber · <a href="contact.html">Contact</a> · <a href="speaking.html">Speaking</a> · <a href="consulting.html">Consulting</a> · <a href="books.html">Books</a> · Photographs by Tamar Hersko</span><span class="soc">{social}</span></div></footer>
</div>'''
    if fragment:
        return doc
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(DESCS.get(page, DESCS['index.html']))}">
<link rel="canonical" href="https://zfarber.com/{'' if page == 'index.html' else page}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(DESCS.get(page, DESCS['index.html']))}">
<meta property="og:image" content="https://zfarber.com/img/hero.jpg">
{head}
</head>
<body>
{doc[len(head)+1:]}
</body>
</html>'''

# ---------- pieces ----------
NOTE = lambda t: f'<p class="note"><b>Placeholder</b>{t}</p>'

def sec_head(label, h2, body_html=''):
    lab = f'<div class="label">{esc(label)}</div>' if label else ''
    return f'<div class="sec-head"><div>{lab}<h2>{h2}</h2></div><div class="body">{body_html}</div></div>'

def section(label, h2, body='', intro=''):
    return f'<section class="block"><div class="wrap">{sec_head(label, h2, intro)}{body}</div></section>'

def paper(*sections):
    return '<div class="paper">' + ''.join(sections) + '</div>'

def page_header(label, h1, lead='', photo=None, box=''):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    photo_html = f'<div class="phead-photo"><img src="img/{photo}.jpg" alt=""></div>' if photo else ''
    box_html = f'<div class="pbox-wrap">{box}</div>' if box else ''
    return f'<header class="phead{" has-box" if box else ""}"><div class="phead-text">{box_html}<div class="phead-bottom"><div class="label">{esc(label)}</div><h1>{h1}</h1>{lead_html}</div></div>{photo_html}</header>'

def actions(label, h2, primary, secondary=(), note=''):
    """Dark closing strip. primary=(text, href); secondary=[(text, href)]. Verbs only."""
    t, h = primary
    sec = ''.join(f'<a class="act-link" href="{esc(u)}">{esc(x)} →</a>' for x, u in secondary)
    note_html = f'<p class="act-note">{note}</p>' if note else ''
    return f'''<section class="actions"><div class="wrap"><div class="act">
<div><div class="label">{esc(label)}</div><h2>{h2}</h2>{note_html}</div>
<div class="act-btns"><a class="btn primary" href="{esc(h)}">{esc(t)}</a>{sec}</div>
</div></div></section>'''

PRISMA_BLOCK = f'''<article class="proj prisma">
  <div class="logo"><img src="img/prisma-logo.png" alt="Prisma"></div>
  <div class="role">Founder and Director</div>
  <h3>Prisma</h3>
  <p>Teachers from the world's religions, for people who want to learn from them without joining them. A podcast, a journal, and a growing library.</p>
  <div class="proj-acts"><a class="btn small" href="{LINKS['prisma_list']}">Join the mailing list</a><a class="btn small" href="{LINKS['prisma_journal']}">Subscribe to the Journal</a><a class="more" href="https://prisma.guide">prisma.guide →</a></div>
</article>'''
TORAH_BLOCK = f'''<article class="proj thetorah">
  <div class="logo"><img src="img/thetorah-logo-white.svg" alt="TheTorah.com"></div>
  <div class="role">Senior Editor and Fellow</div>
  <h3>TheTorah.com</h3>
  <p>Academic study of the Torah for a religious readership, with essays by hundreds of scholars. I have edited the site for over a decade and write for it regularly.</p>
  <div class="proj-acts"><a class="btn small" href="{LINKS['torah_news']}">Get the newsletter</a><a class="more" href="{LINKS['torah_author']}">My essays →</a></div>
</article>'''

ATLAS_BAND = f'''<section class="atlas band"><div class="wrap">
  <div>
    <div class="label">In development</div>
    <h2>HolyLand Historical Atlas</h2>
    <p>An interactive, trilingual historical atlas of the land, built by Jewish and Arab scholars together, from the ancient period to the present.</p>
  </div>
  <div class="ask">
    <div class="label">Looking for</div>
    <p>Funders and partners.</p>
    <a class="btn primary" href="contact.html">Partner in the Atlas</a>
  </div>
</div></section>'''

def cover(href, img, title):
    return f'<a class="cover" href="{esc(href)}" title="{esc(title)}"><img src="img/{img}" alt="{esc(title)}"></a>'

SHELF = f'''<section class="band band-2 shelf"><div class="wrap">
  <div class="label">Books</div>
  <div class="shelf-groups">
    <div class="group"><div class="label">Bible and history</div><div class="covers">
      {cover(LINKS['first_kings'], 'cover-firstkings.jpg', "The Bible's First Kings")}
      {cover(LINKS['joshua'], 'cover-joshua.jpg', 'Images of Joshua in the Bible and Their Reception')}
      {cover(LINKS['judah'], 'cover-judah.jpg', 'Archaeology and History of Eighth-Century Judah')}
    </div></div>
    <div class="group"><div class="label">Halakha</div><div class="covers">
      {cover(LINKS['homosexuality'], 'cover-homosexuality.jpg', 'Homosexual Relationships and Orthodox Judaism')}
      {cover(LINKS['brain'], 'cover-brain.jpg', 'Halakhic Realities: Brain Death')}
      {cover(LINKS['organ'], 'cover-organ.jpg', 'Halakhic Realities: Organ Donation')}
    </div></div>
    <div class="group"><div class="label">Fiction · Z. I. Farber</div><div class="covers">
      {cover(LINKS['two_wrongs'], 'cover-twowrongs.jpg', 'Two Wrongs')}
      {cover(LINKS['doing'], 'cover-doing.jpg', 'Doing What It Takes')}
      {cover(LINKS['airplane'], 'cover-airplane.jpg', 'The Airplane Predator')}
    </div></div>
  </div>
  <p class="shelf-foot"><a class="more" href="books.html">All books, with details →</a></p>
</div></section>'''

PRESS = '''<section class="band"><div class="wrap">
  <div class="label">Press</div>
  <div class="press">
    <a href="https://www.tabletmag.com/sections/belief/articles/reconciling-biblical-criticism"><b>Tablet</b><span>Reconciling Modern Biblical Scholarship With Traditional Orthodox Belief</span></a>
    <a href="https://www.haaretz.com/israel-news/.premium-these-orthodox-jews-are-challenging-commonly-held-beliefs-about-the-torah-1.8100279"><b>Haaretz</b><span>These Orthodox Jews Are Challenging Commonly Held Beliefs About the Torah</span></a>
    <a href="https://www.thejc.com/judaism/features/the-rabbi-behind-the-american-jacobs-affair-1.57127"><b>The Jewish Chronicle</b><span>The Rabbi Behind the American Jacobs Affair</span></a>
    <a href="https://www.ynet.co.il/articles/0,7340,L-5551005,00.html"><b>Ynet</b><span lang="he" dir="rtl">המהפכה השקטה</span></a>
    <a href="https://academic.oup.com/mj/article-abstract/37/2/165/3789884"><b>Modern Judaism</b><span>Is Modern Orthodoxy Moving Towards an Acceptance of Biblical Criticism?</span></a>
  </div>
</div></section>'''

HIRE = actions('In person or online', 'Lectures, scholar-in-residence weekends, and private conversations',
               ('Book a lecture', 'speaking.html'), [('Talk something through', 'consulting.html'), ('Write to me', 'contact.html')])


PRISMA_BOX = f'''<div class="pbox prisma">
  <div class="logo"><img src="img/prisma-logo.png" alt="Prisma"></div>
  <div class="role">Founder and Director</div>
  <div class="pbox-acts"><a class="btn small" href="{LINKS['prisma_list']}">Join the mailing list</a><a class="btn small" href="{LINKS['prisma_journal']}">Subscribe to the Journal</a><a class="more" href="https://prisma.guide">prisma.guide →</a></div>
</div>'''
TORAH_BOX = f'''<div class="pbox thetorah">
  <div class="logo"><img src="img/thetorah-logo-white.svg" alt="TheTorah.com"></div>
  <div class="role">Senior Editor and Fellow</div>
  <div class="pbox-acts"><a class="btn small" href="{LINKS['torah_news']}">Get the newsletter</a><a class="more" href="{LINKS['torah_author']}">My essays →</a></div>
</div>'''
ATLAS_BOX = f'''<div class="pbox atlas">
  <div class="wordmark">HolyLand Historical Atlas</div>
  <div class="role">In development · looking for funders and partners</div>
  <div class="pbox-acts"><a class="btn small primary" href="contact.html">Partner in the Atlas</a></div>
</div>'''

PRISMA_SIG = '<a class="sig prisma" href="https://prisma.guide"><img src="img/prisma-logo.png" alt="Prisma"></a>'
TORAH_SIG = f'<a class="sig thetorah" href="{LINKS["torah_author"]}"><img src="img/thetorah-logo-white.svg" alt="TheTorah.com"></a>'
ATLAS_SIG = '<a class="sig atlas" href="contact.html"><span class="wordmark">HolyLand Historical Atlas</span><span class="tag-dev">In development</span></a>'

def proj_band(block):
    return f'<section class="band proj-band"><div class="wrap"><div class="projects one">{block}</div></div></section>'

def prow(tile_style, small, name, meta, text, verb_text, verb_href, linked=True):
    tile = (f'<a class="cover tile pw" href="{verb_href}" {tile_style}><small>{small}</small>{name}</a>' if linked
            else f'<span class="cover tile pw" {tile_style}><small>{small}</small>{name}</span>')
    verb = f'<a class="btn small" href="{verb_href}">{verb_text}</a>' if linked and verb_text else ''
    return f'<article class="prow">{tile}<div><div class="label">{meta}</div><h3>{name}</h3><p>{text}</p>{verb}</div></article>'

TILE = lambda img: f'style="background-image:linear-gradient(0deg,rgba(0,0,0,.85) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,0) 70%),url(img/{img})"'
PROJECTS = f'''<section class="band projects-band"><div class="wrap">
  <div class="label">Projects</div>
  <div class="prows">
    {prow(TILE('lectorium.jpg'), 'App · in beta', 'Lectorium', 'Reading app · in beta', "Read the world's classic texts in their original languages, with the apparatus carrying whatever the reader cannot yet. Grimm and Perrault, Homer and Ovid, the Daodejing, Hammurabi, Beowulf, and more.", '', '', linked=False)}
    {prow(TILE('paintedwolf.jpg'), 'Publisher', 'Painted Wolf Adventure Classics', 'Painted Wolf · publisher', 'Complete works of classic adventure authors, with comprehensive author bio and survey of works, reprinted with easy-to-read modern formatting, beginning with H. Rider Haggard.', 'Browse the series', LINKS['paintedwolf'])}
    {prow(TILE('udemy.jpg'), 'Course', 'Developmental Editing', 'Udemy · video course', 'Developmental editing, mainly for non-fiction, for editors and for writers editing their own work.', 'Buy on Udemy', LINKS['udemy'])}
    {prow(TILE('zevtime.jpg'), 'Podcast', 'Zevtime Stories', 'Spotify · bedtime stories', "I have six kids. I read all of them the same bedtime stories: Oz, Winnie the Pooh, Alice in Wonderland, and other classics. Now my children are older and are having children of their own, so I am doing one more set of reading, for all my grandchildren now and to come, and any other children who wish to listen and enjoy these fun stories the way my kids did.", 'Listen on Spotify', LINKS['zevtime'])}
  </div>
</div></section>'''

pages = {}

# ---------- HOME ----------
pages['index.html'] = ('Zev Farber', f'''
<header class="hero">
  <div class="hero-text">
    <h1>Zev I.<br><em>Farber</em></h1>
    <blockquote class="epigraph"><p>“The reasonable man adapts himself to the world; the unreasonable one persists in trying to adapt the world to himself. Therefore, all progress depends on the unreasonable man.”</p><cite>George Bernard Shaw, “Maxims for Revolutionists”</cite></blockquote>
  </div>
  <div class="hero-photo"><img src="img/hero.jpg" alt="Zev Farber"></div>
</header>

<section class="band"><div class="wrap">
  <div class="label">Where I work</div>
  <div class="projects">
    {PRISMA_BLOCK}
    {TORAH_BLOCK}
  </div>
</div></section>

{ATLAS_BAND}

{SHELF}

{PROJECTS}

{PRESS}

{HIRE}
''')

# ---------- ABOUT ----------
ab = page_header('Rabbi · Ph.D. · Dayan', 'Zev I. Farber', '', photo='about')
ab += paper(
    section('Positions', 'Current work', f'''<div class="prose">
<p><b>Prisma</b> — founder and director. A podcast, journal, and library of teaching from the world's religions. <a href="https://prisma.guide">prisma.guide</a></p>
<p><b>TheTorah.com</b> — Senior Editor and Fellow, Academic Torah Institute. <a href="{LINKS['torah_author']}">Essays</a></p>
</div>'''),
    section('Education', 'Degrees and ordination', '''<div class="prose">
<p>Ph.D., Emory University, Jewish Religious Cultures and Hebrew Bible.</p>
<p>M.A., Hebrew University of Jerusalem, Jewish History (biblical period).</p>
<p>B.A., Touro College, Psychology.</p>
<p>Rabbinic ordination (<em>yoreh yoreh</em>), Yeshivat Chovevei Torah.</p>
<p>Advanced ordination (<em>yadin yadin</em>), Yeshivat Chovevei Torah.</p>
</div>'''),
    section('Press', 'Coverage and discussion', render_list(parse('media'), two_col=True)))
ab += actions('Contact', 'Write to me', ('Write to me', 'contact.html'),
              [('Speaking', 'speaking.html'), ('Consulting', 'consulting.html'), ('Books', 'books.html')],
              note='For speaking, consultation, press, Prisma, the Atlas, or the books.')
pages['about.html'] = ('About · Zev Farber', ab)

# ---------- BIBLE ----------
b = page_header('Bible', 'Essays on the <em>Hebrew Bible</em>',
    f'Most of these appeared at <a href="{LINKS["torah_author"]}">TheTorah.com</a>; academic papers are on Academia.edu; a few pieces are in Hebrew at the Hartman Institute blog. Grouped by book and by subject.', photo='bible', box=TORAH_SIG)
b += proj_band(TORAH_BLOCK)
b += paper(
    section('Torah', 'Genesis to Deuteronomy', render_list(parse('torah'))),
    section('Joshua and Judges', 'Joshua and Judges', render_list(parse('joshua-judges')), f'<p>The subject of my doctoral work and of <a href="{LINKS["joshua"]}"><em>Images of Joshua in the Bible and Their Reception</em></a>.</p>'),
    section('Holidays', 'The festivals', render_list(parse('holidays'))),
    section('Theology', 'Torah, history, and belief', render_list(parse('theology')), '<p>What "Torah from heaven" can mean for a reader who accepts that the Torah has a history. Start with <a href="https://www.thetorah.com/article/torah-is-from-heaven-what-do-we-really-mean">Torah is From Heaven: What Do We Mean?</a></p>'),
    section('Education', 'Teaching Torah with the scholarship in view', render_list(parse('education'))),
    section('Academic', 'Articles, chapters, edited volumes, and reference works', render_list(parse('academic-bible')), '<p>Peer-reviewed articles and book chapters, two journal volumes I edited, and entries in reference works. Items without a link are in print only.</p>'),
    section('My Jewish Learning', 'Shorter pieces', render_list(parse('mjl')), '<p>Short essays written for <a href="https://www.myjewishlearning.com/author/rabbi-dr-zev-farber/">My Jewish Learning</a>.</p>'))
b += actions('Next', "Buy <em>The Bible's First Kings</em>", ("Buy The Bible's First Kings", LINKS['first_kings']),
             [('Get the TheTorah.com newsletter', LINKS['torah_news']), ('Book a lecture', 'speaking.html')],
             note='Uncovering the story of Saul, David, and Solomon, with Avraham Faust. Cambridge University Press, 2025.')
pages['bible.html'] = ('Bible · Zev Farber', b)

# ---------- HALAKHA ----------
h = page_header('Halakha', 'Jewish <em>law</em>',
    'Twenty years of writing on halakha: medical ethics, the status of women, LGBTQ Jews, conversion, and responsa for Jewish Values Online. Some pieces below are PDFs of articles first published elsewhere.', photo='halakha')
h += paper(
    section('Books', 'Three books', f'''<div class="books">
  <article class="book">{cover(LINKS['homosexuality'], 'cover-homosexuality.jpg', 'Homosexual Relationships and Orthodox Judaism')}<div><h3><a href="{LINKS['homosexuality']}">Homosexual Relationships and Orthodox Judaism</a></h3><div class="meta">Painted Wolf · 2026</div></div></article>
  <article class="book">{cover(LINKS['brain'], 'cover-brain.jpg', 'Halakhic Realities: Brain Death')}<div><h3><a href="{LINKS['brain']}">Halakhic Realities: Collected Essays on Brain Death</a></h3><div class="meta">Maggid · editor</div></div></article>
  <article class="book">{cover(LINKS['organ'], 'cover-organ.jpg', 'Halakhic Realities: Organ Donation')}<div><h3><a href="{LINKS['organ']}">Halakhic Realities: Collected Essays on Organ Donation</a></h3><div class="meta">Maggid · editor</div></div></article>
</div>'''),
    section('', 'Halakha For All', render_list(parse('beyond'), two_col=False)),
    section('Medical ethics', 'Brain death, organ donation, autopsies', render_list(parse('medical-ethics'))),
    section('Women', 'Agunah, modesty, prayer', render_list(parse('women-s-issues'))),
    section('LGBTQ', 'LGBTQ Jews and Orthodoxy', render_list(parse('lgbtq'))),
    section('Conversion', 'Conversion', render_list(parse('conversion'))),
    section('Abuse and advocacy', 'Sexual abuse in the community', render_list(parse('social-advocacy'))),
    section('Responsa', 'Questions and answers', render_list(parse('question-answer')), '<p>Short answers written for <a href="http://www.jewishvaluesonline.org">Jewish Values Online</a>.</p>'),
    section('Academic', 'Articles and chapters', render_list(parse('academic-halakha'))))
h += actions('Next', 'Buy <em>Homosexual Relationships and Orthodox Judaism</em>', ('Buy the book', LINKS['homosexuality']),
             [('Halakhic Realities volumes', LINKS['brain']), ('Book a lecture', 'speaking.html')])
pages['halakha.html'] = ('Halakha · Zev Farber', h)

# ---------- ISRAEL ----------
i = page_header('Israel', 'Commentary on <em>Israel</em>', f'Op-eds at the <a href="{LINKS["toi"]}">Times of Israel</a> since 2011, with a few pieces elsewhere. Newest first.', photo='israel')
i += ATLAS_BAND
i += paper('<section class="block"><div class="wrap">' + render_list(parse('israel')) + '</div></section>')
i += actions('Next', 'Follow the commentary', ('Follow at the Times of Israel', LINKS['toi']),
             [('Partner in the Atlas', 'contact.html'), ('Book a lecture', 'speaking.html')])
pages['israel.html'] = ('Israel · Zev Farber', i)

# ---------- RELIGION ----------
r = page_header('Religion', 'Synergistic <em>religion</em>',
    'For most of history, religions have competed with each other over which of them, if any, has the truth. In contrast, I see religions as expressions of deep metaphorical and mythic truths, which can be explored together as different facets of a prism, unique but mutually reinforcing, and never collapsed into one. This is the idea behind Prisma.', photo='religion', box=PRISMA_SIG)
r += proj_band(PRISMA_BLOCK)
r += paper(
    section('', 'Prisma Talks', '<ul class="arch"><li><a href="https://www.youtube.com/watch?v=ID345_Hxmbk">Introduction to Judaism</a><small>Prisma Guide, YouTube</small></li><li><a href="https://www.youtube.com/watch?v=BJjUWywqcqM">Founder\'s Statement</a><small>Prisma Guide, YouTube</small></li></ul>'),
    section('', 'Thinking Out Loud about Synergistic Religion', render_list(parse('religion-youtube'), two_col=False), f'<p><a href="{LINKS["youtube"]}">The channel →</a></p>'),
    section('', 'Theology', '<ul class="arch"><li><a href="https://www.thetorah.com/article/torah-is-from-heaven-what-do-we-really-mean">Torah is From Heaven: What Do We Mean?</a><small>TheTorah.com, 2019</small></li><li><a href="https://www.thetorah.com/series/avraham-avinu-is-my-father-thoughts-on-torah-history-and-judaism">Avraham Avinu is My Father: Thoughts on Torah, History, and Judaism</a><small>TheTorah.com series</small></li><li><a href="/pdf/God-Consciousness-and-the-Problem-of-Anthropopathism.pdf">God, Consciousness, and the Problem of Anthropopathism</a><small>PDF</small></li></ul>'))
r += actions('Next', 'Watch, join, or talk it through', ('Watch the channel', LINKS['youtube']),
             [('Join the Prisma mailing list', LINKS['prisma_list']), ('Book a lecture', 'speaking.html'), ('Talk something through', 'consulting.html')])
pages['religion.html'] = ('Religion · Zev Farber', r)

# ---------- FICTION ----------
f_ = page_header('Z. I. Farber', 'Fiction', 'Crime novels and stories, published under the name Z.&nbsp;I.&nbsp;Farber. Paperback and Kindle.', photo='fiction')
fic_items = parse('fiction-2')
FIC_COVERS = {'Two Wrongs': 'cover-twowrongs.jpg', 'Doing What It Takes': 'cover-doing.jpg', 'The Airplane Predator': 'cover-airplane.jpg'}
f_ += '<section class="band"><div class="wrap"><div class="fiction">'
cur = None
for it in fic_items:
    if it[0] == 'h2':
        if cur: f_ += '</div></article>'
        cur = it[1]
        f_ += f'<article class="novel"><div class="cover"><img src="img/{FIC_COVERS.get(cur, "")}" alt="{esc(cur)}"></div><div><h3>{esc(cur)}</h3>'
    elif it[0] == 'blurb':
        f_ += f'<p>{esc(it[1])}</p>'
    elif it[0] == 'link':
        f_ += f'<a class="btn primary" href="{esc(clean_amazon(it[2]))}">Buy on Amazon</a>'
if cur: f_ += '</div></article>'
f_ += '</div></div></section>'
f_ += actions('Next', 'Book clubs', ('Book a video meeting', 'contact.html'), [('All books', 'books.html')],
              note='Video meetings with book clubs reading the novels. Discussion material for clubs available upon request.')
pages['fiction.html'] = ('Fiction · Z. I. Farber', f_)

# ---------- BOOKS ----------
bk = page_header('Books', 'Books, and <em>other things I made</em>', 'Biblical history and Jewish law under my own name; fiction as Z.&nbsp;I.&nbsp;Farber; a course on editing; Lectorium, a reading app in beta; and Painted Wolf, a press for classic adventure fiction.', photo='books')
def book(href, img, title, meta, verb='Buy', extra=''):
    t = f'<a href="{href}">{title}</a>' if href else title
    cov = cover(href, img, title) if img and href else (f'<div class="cover tile soon"><small>{esc(extra or "Forthcoming")}</small></div>' if not img else f'<div class="cover"><img src="img/{img}" alt="{esc(title)}"></div>')
    btn = f'<a class="btn small" href="{href}">{esc(verb)}</a>' if href else ''
    return f'<article class="book">{cov}<div><h3>{t}</h3><div class="meta">{meta}</div>{btn}</div></article>'
bk += paper(
    section('Scholarship', 'Bible and history', '<div class="books">' +
        book(LINKS['first_kings'], 'cover-firstkings.jpg', "The Bible's First Kings: Uncovering the Story of Saul, David, and Solomon", 'Cambridge University Press · 2025 · with Avraham Faust · finalist, AAP PROSE Award') +
        book(LINKS['joshua'], 'cover-joshua.jpg', 'Images of Joshua in the Bible and Their Reception', 'De Gruyter, BZAW 457 · 2016') +
        book(LINKS['judah'], 'cover-judah.jpg', 'Archaeology and History of Eighth-Century Judah', 'SBL Press · 2018 · edited with Jacob L. Wright') + '</div>'),
    section('Law', 'Jewish law', '<div class="books">' +
        book(LINKS['homosexuality'], 'cover-homosexuality.jpg', 'Homosexual Relationships and Orthodox Judaism', 'Painted Wolf · 2026 · paperback, hardcover, and Kindle') +
        book(LINKS['brain'], 'cover-brain.jpg', 'Halakhic Realities: Collected Essays on Brain Death', 'Maggid · 2015 · editor') +
        book(LINKS['organ'], 'cover-organ.jpg', 'Halakhic Realities: Collected Essays on Organ Donation', 'Maggid · 2017 · editor') + '</div>'),
    section('Fiction', 'As Z. I. Farber', '<div class="books">' +
        book(LINKS['two_wrongs'], 'cover-twowrongs.jpg', 'Two Wrongs', 'Novel · paperback and Kindle') +
        book(LINKS['doing'], 'cover-doing.jpg', 'Doing What It Takes', 'Novel · paperback and Kindle') +
        book(LINKS['airplane'], 'cover-airplane.jpg', 'The Airplane Predator', 'Short story · Kindle') + '</div>', '<p><a href="fiction.html">Descriptions →</a></p>'),
    section('Also', 'A course, an app, and a press', '<div class="books">' +
        f'<article class="book"><a class="cover tile pw" href="{LINKS["udemy"]}" style="background-image:linear-gradient(0deg,rgba(0,0,0,.85) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,0) 70%),url(img/udemy.jpg)"><small>Course</small>Developmental Editing</a><div><h3><a href="{LINKS["udemy"]}">Developmental Editing: How to Find the Narrative Arc</a></h3><div class="meta">Udemy · video course</div><p>Developmental editing, mainly for non-fiction, for editors and for writers editing their own work.</p><a class="btn small" href="{LINKS["udemy"]}">Buy on Udemy</a></div></article>' +
        f'<article class="book"><span class="cover tile pw" style="background-image:linear-gradient(0deg,rgba(0,0,0,.88) 0%,rgba(0,0,0,.45) 45%,rgba(20,22,30,.25) 100%),url(img/lectorium.jpg)"><small>App · in beta</small>Lectorium</span><div><h3>Lectorium</h3><div class="meta">Reading app · in beta</div><p>Read the world\'s classic texts in their original languages, with the apparatus carrying whatever the reader cannot yet. Grimm and Perrault, Homer and Ovid, the Daodejing, Hammurabi, Beowulf, and more.</p></div></article>' +
        f'<article class="book"><a class="cover tile pw" href="{LINKS["paintedwolf"]}" style="background-image:linear-gradient(0deg,rgba(0,0,0,.85) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,0) 70%),url(img/paintedwolf.jpg)"><small>Publisher</small>Painted Wolf</a><div><h3><a href="{LINKS["paintedwolf"]}">Painted Wolf Adventure Classics</a></h3><div class="meta">Painted Wolf · publisher</div><p>Complete works of classic adventure authors, with comprehensive author bio and survey of works, reprinted with easy-to-read modern formatting, beginning with H. Rider Haggard.</p><a class="btn small" href="{LINKS["paintedwolf"]}">Browse the series</a></div></article>' + '</div>'))
pages['books.html'] = ('Books · Zev Farber', bk)

# ---------- SPEAKING ----------
sp = page_header('Speaking', 'Lectures, courses, and <em>scholar-in-residence weekends</em>', photo='speaking')
sp += paper(
    section('Topics', 'What I talk about', '''<div class="topics">
  <div class="topic"><h3>The Bible in history</h3><p>What the Bible looks like when it is read alongside archaeology and the ancient Near East: Saul, David, and Solomon; the Exodus; Joshua and the conquest; Judah in the eighth century.</p></div>
  <div class="topic"><h3>Being religious without classical faith</h3><p>Practicing Judaism after biblical criticism. What "Torah from heaven" can mean for someone who accepts that the Torah has a history, and why observance can come first and belief follow.</p></div>
  <div class="topic"><h3>Beyond Orthodoxy: how halakha is decided</h3><p>Who decides Jewish law, on what authority, and how that has changed. Cases: agunah, women in ritual, conversion, medical ethics. See <a href="''' + LINKS['beyond'] + '''">Beyond Orthodoxy</a>.</p></div>
  <div class="topic"><h3>Synergistic religion</h3><p>Religions as expressions of mythic and metaphorical truth rather than as rival factual claims: different facets of a prism, unique but mutually reinforcing, without collapsing them into one. The idea behind Prisma.</p></div>
  <div class="topic"><h3>Halakha and homosexuality</h3><p>The biblical and rabbinic sources, the Orthodox community's responses over the past forty years, and the halakhic category of <em>ʾônēs</em> (duress). Based on my book <em>Homosexual Relationships and Orthodox Judaism</em> (2026).</p></div>
  <div class="topic"><h3>Anything in the archives</h3><p>I also lecture on any subject I have written about: see the <a href="bible.html">Bible</a>, <a href="halakha.html">halakha</a>, and <a href="religion.html">religion</a> pages.</p></div>
</div>'''),
    '''<section class="block contact"><div class="wrap">
  <div><div class="label">Inquiries</div><h2 class="h2">About an event</h2><p class="muted">If you are planning a program, a note with the date, place, and audience is enough to start. Talks can be shaped to the room. A one-page bio, a print-quality photo, and a short introduction for the host are available on request.</p></div>
  <form name="speaking" method="POST" action="/thanks.html" data-netlify="true" netlify-honeypot="bot-field">
    <input type="hidden" name="form-name" value="speaking"><p hidden><label>Leave this empty: <input name="bot-field"></label></p>
    <div class="two"><div class="field"><label for="sname">Name</label><input id="sname" name="name"></div><div class="field"><label for="sorg">Organization</label><input id="sorg" name="org"></div></div>
    <div class="field"><label for="semail">Email</label><input id="semail" name="email" type="email"></div>
    <div class="field"><label for="smsg">About the event</label><textarea id="smsg" name="message"></textarea></div>
    <div><button class="btn primary" type="submit">Send</button></div>
  </form>
</div></section>''')
pages['speaking.html'] = ('Speaking · Zev Farber', sp)

# ---------- CONSULTING ----------
co = page_header('Consulting', 'Private <em>conversations</em>', '', photo='consulting')
co += paper('''<section class="block"><div class="wrap"><div class="sec-head"><div></div>
<div class="body prose">
  <h3>Who this is for</h3>
  <p>People working out their religious or theological beliefs, or in a religious quandary, who want to talk it through with someone who has been through it himself.</p>
  <h3>What it is</h3>
  <p>Serious, unhurried time, by appointment, in person or online. Text study where it helps. No fixed program.</p>
  <h3>Background</h3>
  <p>A Ph.D. in Hebrew Bible, rabbinic ordination, and many years of working these questions out for myself.</p>
  <h3>How to begin</h3>
  <p><a href="contact.html">Write to me</a> with a few lines about what you are thinking through.</p>
</div></div></div></section>''')
pages['consulting.html'] = ('Consulting · Zev Farber', co)

# ---------- CONTACT ----------
ct = page_header('Contact', 'Write <em>to me</em>', 'For speaking, scholar-in-residence weekends, press, Prisma partnerships, the Atlas, consultation, readings, or the books.', photo='contact')
ct += '''<div class="paper"><section class="block contact"><div class="wrap">
  <div><div class="label">Elsewhere</div><p class="links">''' + '<br>'.join(f'<a href="{u}">{n}</a>' for n, u in SOCIAL + [('TheTorah.com', LINKS['torah_author']), ('Prisma', 'https://prisma.guide')]) + '''</p></div>
  <form name="contact" method="POST" action="/thanks.html" data-netlify="true" netlify-honeypot="bot-field">
    <input type="hidden" name="form-name" value="contact"><p hidden><label>Leave this empty: <input name="bot-field"></label></p>
    <div class="two"><div class="field"><label for="fn">First name</label><input id="fn" name="first"></div><div class="field"><label for="ln">Last name</label><input id="ln" name="last"></div></div>
    <div class="field"><label for="em">Email</label><input id="em" name="email" type="email"></div>
    <div class="field"><label for="msg">Message</label><textarea id="msg" name="message"></textarea></div>
    <div><button class="btn primary" type="submit">Send</button></div>
  </form>
</div></section></div>'''
pages['contact.html'] = ('Contact · Zev Farber', ct)

# ---------- THANKS / 404 ----------
pages['thanks.html'] = ('Thank you · Zev Farber', page_header('Sent', 'Thank <em>you</em>', 'Your message is on its way. I read everything and answer what I can.', photo='contact') + '<div class="paper"><section class="block"><div class="wrap"><p><a class="more" href="index.html">Back to the site →</a></p></div></section></div>')
pages['404.html'] = ('Page not found · Zev Farber', page_header('404', 'No such <em>page</em>', 'That address is from the old site, or mistyped.', photo='books') + '<div class="paper"><section class="block"><div class="wrap"><p><a class="more" href="index.html">Home →</a> &nbsp; <a class="more" href="bible.html">Bible →</a> &nbsp; <a class="more" href="halakha.html">Halakha →</a> &nbsp; <a class="more" href="books.html">Books →</a></p></div></section></div>')

# ---------- write ----------
BODY_CLASS = {'fiction.html': 'noir'}
for name, (title, body) in pages.items():
    frag = ARTIFACT and not SITE and name == 'index.html'
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(shell(name, title, body, fragment=frag, body_class=BODY_CLASS.get(name, '')))
img_out = os.path.join(OUT, 'img')
if os.path.isdir(img_out):
    shutil.rmtree(img_out)
shutil.copytree(os.path.join(ROOT, 'img'), img_out)
if SITE:
    base = 'https://zfarber.com/'
    urls = [base] + [base + n for n in pages if n not in ('index.html', '404.html', 'thanks.html')]
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write('User-agent: *\nAllow: /\nSitemap: https://zfarber.com/sitemap.xml\n')
    # redirects from the old Wix site
    old = {'/bible': '/bible.html', '/torah': '/bible.html', '/joshua-judges': '/bible.html', '/holidays': '/bible.html',
           '/theology': '/bible.html', '/education': '/bible.html', '/jewish-values': '/halakha.html',
           '/medical-ethics': '/halakha.html', '/women-s-issues': '/halakha.html', '/lgbtq': '/halakha.html',
           '/social-advocacy': '/halakha.html', '/conversion': '/halakha.html', '/question-answer': '/halakha.html',
           '/israel': '/israel.html', '/features': '/about.html', '/fiction-2': '/fiction.html', '/fiction': '/fiction.html',
           '/contact': '/contact.html', '/lectures': '/speaking.html', '/books': '/books.html', '/about': '/about.html',
           '/media': '/about.html', '/in-the-media': '/about.html'}
    lines = [f'{k}  {v}  301' for k, v in old.items()]
    for u, p in sorted(PDF_MAP.items()):
        lines.append(f'{u.replace("https://www.zfarber.com", "")}  {p}  301')
    with open(os.path.join(OUT, '_redirects'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(ROOT, 'pdf-list.txt'), 'w', encoding='utf-8') as f:
        f.write('# old Wix URL -> new path (download each, save under dist/pdf/)\n' + '\n'.join(f'{u} -> dist{p}' for u, p in sorted(PDF_MAP.items())) + '\n')
    os.makedirs(os.path.join(OUT, 'pdf'), exist_ok=True)
print('built', len(pages), 'pages ->', OUT, '(artifact mode)' if ARTIFACT else '(site mode)' if SITE else '')
