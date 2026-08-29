#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка папки docs/ — того, что GitHub Pages отдаёт как сайт.

Папка называется docs/, а не site/, потому что Pages умеет брать сайт либо
из корня репозитория, либо из docs/. Второе позволяет держать исходники,
скрипты и готовый сайт в одном репозитории.

Что делает:
  1. раскладывает страницы по чистым адресам: ohmy-web.html → web/index.html
  2. переписывает все внутренние ссылки под новую структуру
  3. переводит пути к картинкам в абсолютные (страницы теперь во вложенных папках)
  4. копирует img/, og/, favicon.svg, robots.txt, sitemap.xml
  5. кладёт CNAME и .nojekyll

Порядок запуска:
    python3 build-seo.py     # мета-теги, карта сайта, картинки соцсетей
    python3 build-site.py    # раскладка под GitHub Pages

Повторный запуск безопасен: docs/ пересобирается с нуля.
"""

import os, re, shutil

DOMAIN = 'ohmy.design'
# Пока домен не привязан, файла CNAME в сборке быть не должно: Pages подхватит
# его сразу и уведёт адрес на непривязанный домен — превью станет недоступным.
# Ставим True в тот же день, когда правим DNS.
DOMAIN_LIVE = False
ROOT   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.join(ROOT, 'исходники')   # страницы и ресурсы
OUT    = os.path.join(ROOT, 'docs')        # то, что отдаёт GitHub Pages

# файл → путь в репозитории
ROUTES = {
 'ohmy-site.html':       'index.html',
 'ohmy-services.html':   'services/index.html',
 'ohmy-web.html':        'web/index.html',
 'ohmy-ai.html':         'ai/index.html',
 'ohmy-brand.html':      'brand/index.html',
 'ohmy-care.html':       'care/index.html',
 'ohmy-projects.html':   'projects/index.html',
 'ohmy-case.html':       'projects/den-zakazchika/index.html',
 'ohmy-case-abp2b.html': 'projects/abp2b/index.html',
 'ohmy-case-tish.html':  'projects/tish/index.html',
 'ohmy-studio.html':     'studio/index.html',
 'ohmy-journal.html':    'journal/index.html',
 'ohmy-article.html':    'journal/swiss-grid/index.html',
 'ohmy-contacts.html':   'contacts/index.html',
 'ohmy-privacy.html':    'privacy/index.html',
 'ohmy-404.html':        '404.html',          # GitHub Pages подхватывает сам
}

# файл → адрес, на который должны указывать ссылки
LINKS = {f: ('/' if p == 'index.html'
             else '/404.html' if p == '404.html'
             else '/' + p[:-len('index.html')])
         for f, p in ROUTES.items()}


def rewrite(html: str) -> str:
    # ссылки между страницами, вместе с якорями: ohmy-site.html#dir → /#dir
    for f, url in LINKS.items():
        html = html.replace(f'href="{f}#', f'href="{url}#')
        html = html.replace(f'href="{f}"',  f'href="{url}"')
        # имя файла в одинарных кавычках: адреса в js-данных каталога
        # и журнала — cs:'…', url:'…', запасной вариант в функции href()
        html = html.replace(f"'{f}'", f"'{url}'")
    # локальные картинки — в абсолютные пути, страницы лежат во вложенных папках
    html = re.sub(r'(src|href)="(?!https?:|//|/|#|mailto:|tel:)(img/|og/)',
                  r'\1="/\2', html)
    # то же для путей в JS-данных каталога проектов
    html = html.replace("img:'img/", "img:'/img/")
    return html


def main():
    # не удаляем папку целиком: на смонтированных дисках unlink может быть
    # запрещён. Просто перезаписываем файлы поверх.
    os.makedirs(OUT, exist_ok=True)

    # ---- страницы ----
    for src, dst in ROUTES.items():
        path = os.path.join(OUT, dst)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        html = open(os.path.join(SRC, src), encoding='utf-8').read()
        open(path, 'w', encoding='utf-8').write(rewrite(html))

    # ---- ресурсы ----
    for folder in ('img', 'og'):
        s = os.path.join(SRC, folder)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(OUT, folder), dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('_*', '.DS_Store'))
    for f in ('favicon.svg', 'robots.txt', 'sitemap.xml'):
        p = os.path.join(SRC, f)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(OUT, f))

    # ---- служебное для GitHub Pages ----
    cname = os.path.join(OUT, 'CNAME')
    if DOMAIN_LIVE:
        open(cname, 'w').write(DOMAIN + '\n')
    elif os.path.exists(cname):
        os.remove(cname)
    # без .nojekyll Pages прогоняет всё через Jekyll и игнорирует папки на «_»
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')

    # ---- отчёт ----
    files = sum(len(fs) for _, _, fs in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(r, f))
               for r, _, fs in os.walk(OUT) for f in fs)
    print(f'  docs/ собрана: {files} файлов, {size//1024} КБ\n')
    for r, _, fs in sorted(os.walk(OUT)):
        rel = os.path.relpath(r, OUT)
        if fs:
            print(f'  {"." if rel == "." else rel}/')
            for f in sorted(fs):
                print(f'      {f}')


if __name__ == '__main__':
    main()
