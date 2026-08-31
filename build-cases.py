#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка страниц проектов из cases.py.

Зачем генератор, а не двадцать шесть файлов руками: страницы отличаются
только содержанием. Шапка, подвал, стили и скрипты у них общие, и любая
правка навигации иначе означала бы двадцать шесть одинаковых замен.

  оболочка   build-assets/case-shell.html   — снята с ohmy-case-tish.html
  данные     cases.py
  результат  исходники/ohmy-case-<slug>.html

Три страницы (День Заказчика, АБП2Б, ТИШЬ) собраны руками до генератора
и помечены made:True — их файлы не трогаем.

Порядок запуска:
    python3 build-cases.py   # страницы проектов
    python3 build-seo.py     # мета-теги и карта сайта
    python3 build-site.py    # раскладка под GitHub Pages

Повторный запуск безопасен: файлы переписываются целиком.
"""

import os, re
from cases import CASES
from typo import typo

ROOT  = os.path.dirname(os.path.abspath(__file__))
SRC   = os.path.join(ROOT, 'исходники')
SHELL = open(os.path.join(ROOT, 'build-assets', 'case-shell.html'),
             encoding='utf-8').read()

SECTORS = {'industry':'промышленность и наука', 'event':'события и форумы',
           'it':'ит и технологии', 'city':'город и архитектура',
           'med':'медицина и здоровье', 'service':'ритейл и услуги'}


def esc(t):
    """кавычки в мета-теги; сам текст пишем мы, разметку в нём не экранируем"""
    return t.replace('"', '&quot;')


def domain(url):
    """адрес для показа человеку: без схемы, без www, punycode — в кириллицу"""
    d = re.sub(r'^https?://', '', url).rstrip('/')
    d = re.sub(r'^www\.', '', d)
    host, _, path = d.partition('/')
    try:
        host = host.encode('ascii').decode('idna')
    except Exception:
        pass
    return host + ('/' + path if path else '')


def cover(c):
    tags = ''.join(f'\n      <span class="tag{" on" if i == 0 else ""}">{t}</span>'
                   for i, t in enumerate(c['tags']))
    return f'''<header class="cover">
  <img src="{c['img']}" alt="{esc(c['n'])}">
  <div class="cover-in">
    <a class="crumb" href="ohmy-projects.html">← все проекты</a>
    <h1>{typo(c['n'])}</h1>
    <div class="cover-tags">{tags}
    </div>
  </div>
</header>'''


def facts(c):
    """Паспорт проекта. Значение None — это просьба поставить сюда адрес
       сайта: он живёт в одном месте, и в паспорте его дублировать нечем."""
    rows = ''
    for k, v in c['facts']:
        if v is None:
            v = (f'<a href="{c["url"]}" target="_blank" rel="noopener" class="fact-live">'
                 f'{domain(c["url"])}<i>↗</i></a>') if c.get('url') else c['nolive']
        else:
            v = typo(v)
        rows += f'\n  <div class="fact"><span>{k}</span><b>{v}</b></div>'
    return f'<div class="facts" data-n="{len(c["facts"])}">{rows}\n</div>'


def ink(hexc):
    """Текст на фирменной плашке: берём чёрный или белый по светлоте цвета.
       Плашки показывают палитру клиента, и подпись обязана читаться на всех."""
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5))
    f = lambda u: u/12.92 if u <= .03928 else ((u+.055)/1.055) ** 2.4
    lum = .2126*f(r) + .7152*f(g) + .0722*f(b)
    return ('#1E1E1E', .55) if lum > .35 else ('#FCFCFC', .6)


def ident(c, n):
    """Знак и палитра. Показываем цвета клиента как они есть, поэтому
       плашки не зависят от темы сайта — иначе это была бы наша палитра."""
    d = c['ident']
    marks = ''
    for bg, src, alt, label in d['marks']:
        col, op = ink(bg)
        marks += (f'\n    <div class="mark" style="background:{bg}">'
                  f'<img src="img/cases/{c["slug"]}/{src}" alt="{esc(alt)}" loading="lazy">'
                  f'<span style="color:{col};opacity:{op}">{label}</span></div>')
    cols = ''
    for hexc, name, note in d['colors']:
        cols += (f'\n    <div class="pal-i"><div class="pal-c" style="background:{hexc}"></div>'
                 f'<div class="pal-h">{hexc}</div><div class="pal-n">{name}</div>'
                 f'<p class="pal-t">{typo(note)}</p></div>')
    photo = ''
    if d.get('photo'):
        src, alt, cap, kind = d['photo']
        photo = (f'\n\n  <figure class="frame full rv" style="margin-top:clamp(38px,4.5vw,66px)">'
                 f'<div class="frame-i"><img src="img/cases/{c["slug"]}/{src}" '
                 f'alt="{esc(alt)}" loading="lazy"></div>'
                 f'<figcaption>{cap}<i>{kind}</i></figcaption></figure>')
    return f'''<section id="ident">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — знак</span><h2 class="sec-title">фирменный стиль</h2></div>
    <span class="mono">{len(d["marks"])} начертания</span>
  </div>

  <p class="lead rv" style="max-width:64ch">{typo(d["lead"])}</p>

  <div class="marks rv">{marks}
  </div>

  <div class="pal">{cols}
  </div>{photo}
</section>'''


def shots(c, n):
    """Носители. Фотографию и макет подписываем по-разному: выдавать
       рендер за напечатанное — то же самое, что придумать цифру."""
    items = ''
    for src, alt, cap, kind, size in c['shots']:
        items += (f'\n    <figure class="frame rv{" full" if size == "full" else ""}">'
                  f'<div class="frame-i"><img src="img/cases/{c["slug"]}/{src}" '
                  f'alt="{esc(alt)}" loading="lazy"></div>'
                  f'<figcaption>{cap}<i>{kind}</i></figcaption></figure>')
    live = sum(1 for *_, k, _s in c['shots'] if k == 'фото')
    return f'''<section id="shots">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — носители</span><h2 class="sec-title">как это живёт</h2></div>
    <span class="mono">{live} с площадки</span>
  </div>

  <div class="frames">{items}
  </div>
</section>'''


def task(c, n):
    bodies = '\n      '.join(f'<p class="body">{typo(p)}</p>' for p in c['body'])
    pains = ''
    if c.get('pains'):
        items = ''.join(
            f'\n    <div class="pain"><span>{i+1:02d}</span><div>{typo(p)}</div></div>'
            for i, p in enumerate(c['pains']))
        pains = ('\n\n  <div class="pains rv" style="margin-top:clamp(40px,5vw,70px)">'
                 f'{items}\n  </div>')
    return f'''<section id="task">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — контекст</span><h2 class="sec-title">задача</h2></div>
    <span class="mono">{SECTORS[c['s']]}</span>
  </div>

  <div class="two">
    <p class="lead rv">{typo(c['lead'])}</p>
    <div class="rv">
      {bodies}
    </div>
  </div>{pains}
</section>'''


def work(c, n):
    steps = ''.join(
        f'''\n    <div class="step rv"><span class="step-n">{i+1:02d}</span>
      <h3>{typo(h)}</h3>
      <p>{typo(t)}</p></div>''' for i, (h, t) in enumerate(c['steps']))
    return f'''<section id="work">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — работа</span><h2 class="sec-title">что сделали</h2></div>
    <span class="mono">{len(c['steps'])} решени{'е' if len(c['steps']) == 1 else 'я' if len(c['steps']) < 5 else 'й'}</span>
  </div>

  <div class="steps">{steps}
  </div>
</section>'''


def result(c, n):
    if c.get('res'):
        items = ''.join(f'\n    <div class="res-i"><b>{v}</b><span>{t}</span></div>'
                        for v, t in c['res'])
        block = f'\n  <div class="res rv">{items}\n  </div>'
    else:
        items = ''.join(
            f'\n    <div><span>{i+1:02d}</span><div>{typo(t)}</div></div>'
            for i, t in enumerate(c['out']))
        block = f'\n  <div class="outcome rv">{items}\n  </div>'
    tail = ''
    if c.get('tail'):
        tail = ('\n\n  <p class="body rv" style="margin-top:clamp(34px,4vw,54px);'
                f'max-width:62ch">{typo(c["tail"])}</p>')
    return f'''<section id="result">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — итог</span><h2 class="sec-title">результат</h2></div>
    <span class="mono">что можно проверить</span>
  </div>
{block}{tail}
</section>'''


def live(c):
    """Ссылка на работающий сайт. Раньше карточка каталога уводила наружу —
       теперь наружу ведёт только эта строка, и только если адрес рабочий."""
    if c.get('url'):
        return f'''<a class="live rv" href="{c['url']}" target="_blank" rel="noopener">
  <div class="live-l"><span>смотреть работу</span><b>{domain(c['url'])}</b></div>
  <span class="live-a">↗</span>
</a>'''
    return f'''<div class="live off rv">
  <div class="live-l"><span>публичной ссылки нет</span><b>{c['nolive']}</b></div>
</div>'''


def nxt(c):
    return f'''<a class="next" href="{c['file']}">
  <img src="{c['img']}" alt="" loading="lazy">
  <div class="next-in">
    <span class="mono">следующий проект</span>
    <h2>{c['n']} <span class="next-arrow">↗</span></h2>
  </div>
</a>'''


def main():
    made = 0
    for i, c in enumerate(CASES):
        if c.get('made'):
            continue
        # Разделы нумеруются по факту: у проекта с фотографиями их пять,
        # у обычного — три, и подписи не должны разъезжаться
        chain = [task]
        if c.get('ident'):
            chain.append(ident)
        chain.append(work)
        if c.get('shots'):
            chain.append(shots)
        chain.append(result)
        mid = [f(c, k + 1) for k, f in enumerate(chain)]
        body = '\n\n'.join([cover(c), facts(c)] + mid +
                            [live(c), nxt(CASES[(i + 1) % len(CASES)])])
        # Блок связи в оболочке подписан «04 — связь». Разделов на странице
        # теперь бывает и пять, поэтому номер досчитываем здесь
        page = (SHELL.replace('{{TITLE}}', esc(c['title']))
                     .replace('{{DESC}}',  esc(c['desc']))
                     .replace('{{CONTENT}}', body)
                     .replace('04 — связь', f'{len(chain) + 1:02d} — связь'))
        open(os.path.join(SRC, c['file']), 'w', encoding='utf-8').write(page)
        made += 1

    print(f'  страниц проектов собрано: {made}')
    print(f'  собраны руками и не тронуты: '
          f'{", ".join(c["slug"] for c in CASES if c.get("made"))}')
    off = [c['slug'] for c in CASES if not c.get('url')]
    print(f'  без публичной ссылки ({len(off)}): {", ".join(off)}')


if __name__ == '__main__':
    main()
