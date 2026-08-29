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
    <h1>{c['n']}</h1>
    <div class="cover-tags">{tags}
    </div>
  </div>
</header>'''


def facts(c):
    rows = ''.join(f'\n  <div class="fact"><span>{k}</span><b>{v}</b></div>'
                   for k, v in c['facts'])
    return f'<div class="facts" data-n="{len(c["facts"])}">{rows}\n</div>'


def task(c):
    bodies = '\n      '.join(f'<p class="body">{p}</p>' for p in c['body'])
    pains = ''
    if c.get('pains'):
        items = ''.join(
            f'\n    <div class="pain"><span>{i+1:02d}</span><div>{p}</div></div>'
            for i, p in enumerate(c['pains']))
        pains = ('\n\n  <div class="pains rv" style="margin-top:clamp(40px,5vw,70px)">'
                 f'{items}\n  </div>')
    return f'''<section id="task">
  <div class="sec-head rv">
    <div><span class="sec-idx">01 — контекст</span><h2 class="sec-title">задача</h2></div>
    <span class="mono">{SECTORS[c['s']]}</span>
  </div>

  <div class="two">
    <p class="lead rv">{c['lead']}</p>
    <div class="rv">
      {bodies}
    </div>
  </div>{pains}
</section>'''


def work(c):
    steps = ''.join(
        f'''\n    <div class="step rv"><span class="step-n">{i+1:02d}</span>
      <h3>{h}</h3>
      <p>{t}</p></div>''' for i, (h, t) in enumerate(c['steps']))
    return f'''<section id="work">
  <div class="sec-head rv">
    <div><span class="sec-idx">02 — работа</span><h2 class="sec-title">что сделали</h2></div>
    <span class="mono">{len(c['steps'])} решени{'е' if len(c['steps']) == 1 else 'я' if len(c['steps']) < 5 else 'й'}</span>
  </div>

  <div class="steps">{steps}
  </div>
</section>'''


def result(c):
    if c.get('res'):
        items = ''.join(f'\n    <div class="res-i"><b>{n}</b><span>{t}</span></div>'
                        for n, t in c['res'])
        block = f'\n  <div class="res rv">{items}\n  </div>'
    else:
        items = ''.join(
            f'\n    <div><span>{i+1:02d}</span><div>{t}</div></div>'
            for i, t in enumerate(c['out']))
        block = f'\n  <div class="outcome rv">{items}\n  </div>'
    tail = ''
    if c.get('tail'):
        tail = ('\n\n  <p class="body rv" style="margin-top:clamp(34px,4vw,54px);'
                f'max-width:62ch">{c["tail"]}</p>')
    return f'''<section id="result">
  <div class="sec-head rv">
    <div><span class="sec-idx">03 — итог</span><h2 class="sec-title">результат</h2></div>
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
  <img src="{c['img']}" alt="">
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
        body = '\n\n'.join([cover(c), facts(c), task(c), work(c),
                            result(c), live(c), nxt(CASES[(i + 1) % len(CASES)])])
        page = (SHELL.replace('{{TITLE}}', esc(c['title']))
                     .replace('{{DESC}}',  esc(c['desc']))
                     .replace('{{CONTENT}}', body))
        open(os.path.join(SRC, c['file']), 'w', encoding='utf-8').write(page)
        made += 1

    print(f'  страниц проектов собрано: {made}')
    print(f'  собраны руками и не тронуты: '
          f'{", ".join(c["slug"] for c in CASES if c.get("made"))}')
    off = [c['slug'] for c in CASES if not c.get('url')]
    print(f'  без публичной ссылки ({len(off)}): {", ".join(off)}')


if __name__ == '__main__':
    main()
