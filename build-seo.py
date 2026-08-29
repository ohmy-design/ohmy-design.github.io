#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Служебная сборка сайта ohmy.design.

Делает четыре вещи:
  1. sitemap.xml и robots.txt по карте страниц
  2. картинки для соцсетей 1200×630 — генерируются из палитр и знаков,
     тех же, что в журнале и на странице «креатив»
  3. favicon.svg
  4. проставляет во все страницы canonical, Open Graph, Twitter Card,
     мета-теги языка и микроразметку организации

Запуск:  python3 build-seo.py
Повторный запуск безопасен: старые теги заменяются, а не дублируются.
"""

import os, re, glob, math
from datetime import date

from cases import CASES

SITE   = 'https://ohmy.design'
TODAY  = date.today().isoformat()
ROOT   = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(ROOT, 'исходники')   # страницы-исходники лежат здесь

# ---------------------------------------------------------------- карта
# файл → (адрес на боевом сайте, приоритет, частота обновления,
#          заголовок для картинки, подпись)
PAGES = {
 'ohmy-site.html':       ('/',                      '1.0','weekly',
    'проектируем облик\nи механику бизнеса',        'студия дизайна и автоматизации'),
 'ohmy-services.html':   ('/services',              '0.9','monthly',
    'направления',                                  'состав работ и цены'),
 'ohmy-web.html':        ('/web',                   '0.9','monthly',
    'веб',                                          'сайты и цифровые продукты'),
 'ohmy-ai.html':         ('/ai',                    '0.9','monthly',
    'ai-автоматизации',                             'боты, ассистенты, интеграции'),
 'ohmy-brand.html':      ('/brand',                 '0.9','monthly',
    'креатив',                                      'бренд, айдентика, арт-дирекшн'),
 'ohmy-care.html':       ('/care',                  '0.9','monthly',
    'сопровождение',                                'чтобы запущенное работало'),
 'ohmy-projects.html':   ('/projects',              '0.9','weekly',
    'проекты',                                      '29 работ с 2018 года'),
 'ohmy-studio.html':     ('/studio',                '0.8','monthly',
    'студия',                                       'команда, метод, процесс'),
 'ohmy-journal.html':    ('/journal',               '0.8','weekly',
    'ohmy.journal',                                 'о дизайне, ux и визуальной культуре'),
 'ohmy-article.html':    ('/journal/swiss-grid',    '0.6','yearly',
    'Швейцарская сетка\nв эпоху скролла',           'ohmy.journal · 9 мин'),
 'ohmy-contacts.html':   ('/contacts',              '0.8','monthly',
    'контакты',                                     'обсудить задачу'),
 'ohmy-privacy.html':    ('/privacy',               '0.2','yearly', None, None),
 'ohmy-404.html':        (None,                     None, None,     None, None),
}

# Страницы проектов — из cases.py. Подпись под картинкой для соцсетей
# собирается из направлений работы, чтобы не держать её в двух местах.
_T = {'web':'сайт', 'brand':'айдентика', 'care':'сопровождение'}
for _c in CASES:
    _title, _sub = _c.get('seo', (None, None))
    PAGES[_c['file']] = (f"/projects/{_c['slug']}", '0.7', 'yearly',
                         _title or _c['n'],
                         _sub or 'кейс · ' + ' + '.join(_T[t] for t in _c['t']))

# ------------------------------------------------- палитры и знаки (как в журнале)
PALETTES = [
 ('#1A0F0A','#B3300F','#FF4A1C','#FFD9C2'),
 ('#07211E','#0E7A66','#23D3B0','#DFF7F0'),
 ('#0A1330','#2452C9','#4D9DFF','#E2ECFF'),
 ('#21071A','#A31159','#FF3D80','#FFE0EC'),
 ('#101E08','#4E8C12','#A8E01F','#F0FBD8'),
 ('#150A28','#6B33C7','#C77DFF','#F0E4FF'),
 ('#1E1205','#B8720C','#FFB020','#FFEDCC'),
 ('#0F1012','#3A3A46','#84848E','#F2F0EC'),
]

def fnv(s: str) -> int:
    """тот же хеш, что на сайте: FNV-1a с лавинной финализацией"""
    h = 2166136261
    for ch in s:
        h ^= ord(ch); h = (h * 16777619) & 0xFFFFFFFF
    h ^= h >> 15; h = (h * 2246822507) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 3266489909) & 0xFFFFFFFF
    h ^= h >> 16
    return h

# --------------------------------------------------------------- картинки
def draw_marks(d, kind, cx, cy, r, fg, ac):
    """знаки из той же грамматики форм, что на сайте"""
    box = (cx-r, cy-r, cx+r, cy+r)
    if kind == 0:
        d.ellipse(box, fill=fg); d.rectangle((cx, cy-r, cx+r, cy), fill=ac)
    elif kind == 1:
        d.ellipse(box, outline=fg, width=int(r*.30))
        d.ellipse((cx-r*.30, cy-r*.30, cx+r*.30, cy+r*.30), fill=ac)
    elif kind == 2:
        d.pieslice(box, 180, 360, fill=fg)
        d.pieslice((cx-r, cy-r+r*.18, cx+r, cy+r+r*.18), 0, 180, fill=ac)
    elif kind == 3:
        d.ellipse(box, outline=fg, width=int(r*.20))
        d.ellipse((cx-r*.66, cy-r*.66, cx+r*.66, cy+r*.66), outline=ac, width=int(r*.20))
        d.ellipse((cx-r*.30, cy-r*.30, cx+r*.30, cy+r*.30), outline=fg, width=int(r*.20))
    elif kind == 4:
        d.rectangle((cx-r*.18, cy-r, cx+r*.18, cy+r), fill=fg)
        d.rectangle((cx-r, cy-r*.18, cx+r, cy+r*.18), fill=ac)
    elif kind == 5:
        q = r*.48
        d.ellipse((cx-r, cy-r, cx-r+q*2, cy-r+q*2), fill=fg)
        d.ellipse((cx+r-q*2, cy-r, cx+r, cy-r+q*2), fill=ac)
        d.ellipse((cx-r, cy+r-q*2, cx-r+q*2, cy+r), fill=ac)
        d.ellipse((cx+r-q*2, cy+r-q*2, cx+r, cy+r), fill=fg)
    elif kind == 6:
        d.polygon([(cx, cy-r), (cx+r, cy+r), (cx-r, cy+r)], fill=fg)
        d.ellipse((cx-r*.36, cy+r*.06, cx+r*.36, cy+r*.78), fill=ac)
    else:
        for i, y in enumerate((-r*.62, 0, r*.62)):
            w = r if i != 1 else r*.62
            d.rectangle((cx-r, cy+y-r*.16, cx-r+w*2, cy+y+r*.16),
                        fill=ac if i == 1 else fg)

# страницы, которым палитра назначена жёстко: у главной и направлений
# картинка — часть узнаваемости, случайный цвет тут неуместен
FIXED = {'/':0, '/web':2, '/ai':1, '/brand':5, '/care':6, '/projects':7, '/journal':3}

# Шрифт для картинок соцсетей — Onest, тот же, что на сайте. Лежит в
# build-assets/, чтобы сборка не зависела от того, что установлено в системе.
# Файл переменный: начертание выбирается через set_variation_by_name.
FONT = os.path.join(ROOT, 'build-assets', 'Onest.ttf')

def font_face():
    if not os.path.exists(FONT):
        raise SystemExit('  нет build-assets/Onest.ttf — скачайте переменный Onest\n'
                         '  с fonts.google.com/specimen/Onest и положите туда')
    return FONT

def og_image(path, title, sub, seed):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    pi = FIXED.get(seed, fnv(seed+'#p') % len(PALETTES))
    p  = PALETTES[pi]
    mk = fnv(seed+'#m') % 8
    lay= fnv(seed+'#l') % 3

    im = Image.new('RGB', (W, H), p[0]); d = ImageDraw.Draw(im)
    # подложка — те же три композиции, что на сайте
    band = Image.new('RGB', (W, H), p[1]); mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    if lay == 0:
        md.rectangle((0, 0, W//3, H), fill=128); md.rectangle((W*2//3, 0, W, H), fill=128)
    elif lay == 1:
        md.rectangle((0, int(H*.28), W, int(H*.72)), fill=128)
    else:
        md.rectangle((0, 0, W//2, H//2), fill=128); md.rectangle((W//2, H//2, W, H), fill=128)
    im.paste(band, (0, 0), mask); d = ImageDraw.Draw(im)

    draw_marks(d, mk, W-190, 150, 78, p[3], p[2])

    face = font_face()
    def F(weight, size):
        f = ImageFont.truetype(face, size)
        try:                       # Onest — переменный шрифт, начертание выбирается
            f.set_variation_by_name(weight)
        except Exception:
            pass                   # статический шрифт: начертание уже в файле
        return f
    def fit(text, size, weight='SemiBold'):
        f = F(weight, size)
        while size > 26 and d.textlength(max(text.split('\n'), key=len), font=f) > W-230:
            size -= 4; f = F(weight, size)
        return f

    lines = (title or '').split('\n')
    ft = fit(title or '', 92 if len(lines) == 1 and len(title) < 16 else 66)
    y = H - 150 - len(lines)*(ft.size+10)
    for ln in lines:
        d.text((78, y), ln, font=ft, fill=p[3]); y += ft.size + 10

    if sub:
        fs = F('Regular', 30)
        d.text((78, y + 14), sub, font=fs, fill=p[2])

    fl = F('Bold', 27)
    d.text((78, 66), 'ohmy.design', font=fl, fill=p[3])

    im.save(path, 'PNG', optimize=True)
    return os.path.getsize(path)

# ------------------------------------------------------------------ теги
BLOCK = re.compile(r'\n?<!-- seo:start -->.*?<!-- seo:end -->', re.S)

ORG = f'''{{"@context":"https://schema.org","@type":"Organization",
"name":"ohmy.design","url":"{SITE}/",
"description":"Студия дизайна и автоматизации для бизнеса",
"email":"hi@ohmy.design","telephone":"+7-931-709-93-07",
"address":{{"@type":"PostalAddress","addressLocality":"Санкт-Петербург","addressCountry":"RU"}},
"foundingDate":"2018","sameAs":["https://t.me/ohmy_design"]}}'''

def inject(fname, url, og_name):
    s = open(fname, encoding='utf-8').read()
    s = BLOCK.sub('', s)                                # прошлый прогон

    title = re.search(r'<title>(.*?)</title>', s, re.S).group(1).strip()
    m = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
    desc = m.group(1).strip() if m else ''

    tags = ['<!-- seo:start -->']
    if url:
        tags.append(f'<link rel="canonical" href="{SITE}{url}">')
    tags += [
      '<meta property="og:type" content="website">',
      '<meta property="og:site_name" content="ohmy.design">',
      '<meta property="og:locale" content="ru_RU">',
      f'<meta property="og:title" content="{title}">',
      f'<meta property="og:description" content="{desc}">',
    ]
    if url:
        tags.append(f'<meta property="og:url" content="{SITE}{url}">')
    if og_name:
        tags += [
          f'<meta property="og:image" content="{SITE}/og/{og_name}">',
          '<meta property="og:image:width" content="1200">',
          '<meta property="og:image:height" content="630">',
          f'<meta property="og:image:alt" content="{title}">',
          '<meta name="twitter:card" content="summary_large_image">',
          f'<meta name="twitter:title" content="{title}">',
          f'<meta name="twitter:description" content="{desc}">',
          f'<meta name="twitter:image" content="{SITE}/og/{og_name}">',
        ]
    tags += [
      '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
      '<meta name="theme-color" content="#131317">',
    ]
    if fname == 'ohmy-site.html':
        tags.append('<script type="application/ld+json">' + ORG + '</script>')
    tags.append('<!-- seo:end -->')

    s = s.replace('</head>', '\n'.join(tags) + '\n</head>', 1)
    open(fname, 'w', encoding='utf-8').write(s)


def main():
    os.chdir(OUTDIR)
    os.makedirs('og', exist_ok=True)

    # ---- картинки ----
    made = 0
    for f, (url, *_rest) in PAGES.items():
        title, sub = _rest[2], _rest[3]
        if not title:
            continue
        name = (url.strip('/').replace('/', '-') or 'index') + '.png'
        size = og_image(os.path.join('og', name), title, sub, url)
        print(f'  og/{name:26} {size//1024:>4} КБ')
        made += 1

    # ---- favicon ----
    open('favicon.svg', 'w', encoding='utf-8').write(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
      '<rect width="64" height="64" rx="12" fill="#131317"/>'
      '<circle cx="32" cy="32" r="17" fill="none" stroke="#F2F0EC" stroke-width="7"/>'
      '<circle cx="32" cy="32" r="5" fill="#FF4A1C"/></svg>')

    # ---- мета-теги ----
    for f, (url, *_rest) in PAGES.items():
        title = _rest[2]
        og = ((url.strip('/').replace('/', '-') or 'index') + '.png') if title else None
        inject(f, url, og)

    # ---- sitemap ----
    rows = []
    for f, (url, pri, freq, *_r) in PAGES.items():
        if not url:
            continue
        rows.append(f'  <url>\n    <loc>{SITE}{url}</loc>\n'
                    f'    <lastmod>{TODAY}</lastmod>\n'
                    f'    <changefreq>{freq}</changefreq>\n'
                    f'    <priority>{pri}</priority>\n  </url>')
    open('sitemap.xml', 'w', encoding='utf-8').write(
      '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + '\n'.join(rows) + '\n</urlset>\n')

    # ---- robots ----
    open('robots.txt', 'w', encoding='utf-8').write(
      'User-agent: *\n'
      'Allow: /\n'
      'Disallow: /*?\n\n'
      'User-agent: Yandex\n'
      'Allow: /\n'
      f'Clean-param: utm_source&utm_medium&utm_campaign&utm_term&utm_content\n\n'
      f'Sitemap: {SITE}/sitemap.xml\n')

    print(f'\n  картинок: {made} · страниц в карте: {len(rows)} · favicon.svg · robots.txt')

if __name__ == '__main__':
    main()
