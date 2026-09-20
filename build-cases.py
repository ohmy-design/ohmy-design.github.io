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


MOTION_JS = """<script>
(function(){
  var fig=document.currentScript.previousElementSibling; if(!fig) return;
  var cv=fig.querySelector('canvas'); if(!cv) return;
  var still=window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches;
  var gl=!still&&(cv.getContext('webgl',{antialias:false,alpha:false})||null);
  if(!gl){fig.classList.add('is-still');return}
  var vs='attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
  var fs='precision highp float;uniform vec2 uR;uniform float uT;uniform vec2 uM;'+
  'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}'+
  'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);'+
  'return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),f.x),f.y);}'+
  'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<3;i++){v+=a*n(p);p=p*2.02+vec2(3.1,1.7);a*=.5;}return v;}'+
  'void main(){vec2 uv=gl_FragCoord.xy/uR;vec2 p=(uv-.5)*vec2(uR.x/uR.y,1.)*1.05+(uM-.5)*.3;float t=uT*.05;'+
  'vec2 q=vec2(fbm(p+vec2(0.,t)),fbm(p+vec2(5.2,1.3)-t));'+
  'vec2 r=vec2(fbm(p+2.*q+vec2(1.7,9.2)+t*1.3),fbm(p+2.*q+vec2(8.3,2.8)-t));'+
  'float f=fbm(p+2.4*r);'+
  'vec3 peri=vec3(.58,.55,.83),deep=vec3(.50,.46,.68),cream=vec3(.925,.898,.863),shade=vec3(.33,.31,.53),peach=vec3(.94,.85,.80);'+
  'vec3 c=mix(peri,deep,smoothstep(.3,.6,f));'+
  'c=mix(c,cream,smoothstep(.5,.72,r.x*1.15));'+
  'c=mix(c,shade,smoothstep(.55,.95,q.y)*.5*(1.-smoothstep(.4,.9,r.x)));'+
  'c=mix(c,peach,smoothstep(.0,.6,1.-uv.y)*smoothstep(.5,.9,f)*.55);'+
  'float g=h(gl_FragCoord.xy+floor(uT*10.)*17.)-.5;c+=g*.14;gl_FragColor=vec4(c,1.);}';
  function sh(t,src){var o=gl.createShader(t);gl.shaderSource(o,src);gl.compileShader(o);return gl.getShaderParameter(o,gl.COMPILE_STATUS)?o:null}
  var v=sh(gl.VERTEX_SHADER,vs),f=sh(gl.FRAGMENT_SHADER,fs); if(!v||!f){fig.classList.add('is-still');return}
  var pr=gl.createProgram();gl.attachShader(pr,v);gl.attachShader(pr,f);gl.linkProgram(pr);
  if(!gl.getProgramParameter(pr,gl.LINK_STATUS)){fig.classList.add('is-still');return}
  gl.useProgram(pr);var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  var a=gl.getAttribLocation(pr,'a');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
  var uR=gl.getUniformLocation(pr,'uR'),uT=gl.getUniformLocation(pr,'uT'),uM=gl.getUniformLocation(pr,'uM');
  var mx=.5,my=.5,cx=.5,cy=.5,on=false,t0=performance.now();
  function size(){var k=Math.min(window.devicePixelRatio||1,1.5),w=Math.min(fig.clientWidth*k,1600);
    cv.width=Math.round(w);cv.height=Math.round(w*fig.clientHeight/fig.clientWidth);gl.viewport(0,0,cv.width,cv.height)}
  function frame(now){if(!on)return;cx+=(mx-cx)*.04;cy+=(my-cy)*.04;
    gl.uniform2f(uR,cv.width,cv.height);gl.uniform1f(uT,(now-t0)/1000);gl.uniform2f(uM,cx,cy);
    gl.drawArrays(gl.TRIANGLE_STRIP,0,4);requestAnimationFrame(frame)}
  fig.addEventListener('pointermove',function(e){var r=fig.getBoundingClientRect();mx=(e.clientX-r.left)/r.width;my=1-(e.clientY-r.top)/r.height});
  size();window.addEventListener('resize',size);
  fig.classList.add('is-live');
  new IntersectionObserver(function(es){on=es[0].isIntersecting;if(on)requestAnimationFrame(frame)}).observe(fig);
})();
</script>"""


def ident(c, n):
    """Знак и палитра. Показываем цвета клиента как они есть, поэтому
       плашки не зависят от темы сайта — иначе это была бы наша палитра.
       Раздел гибкий: знаков может не быть (сайт без логотипа), а к палитре
       добавляются плитки визуалов и анимированный блок."""
    d = c['ident']
    marks_html = ''
    if d.get('marks'):
        marks = ''
        for bg, src, alt, label in d['marks']:
            col, op = ink(bg)
            marks += (f'\n    <div class="mark" style="background:{bg}">'
                      f'<img src="img/cases/{c["slug"]}/{src}" alt="{esc(alt)}" loading="lazy">'
                      f'<span style="color:{col};opacity:{op}">{label}</span></div>')
        marks_html = f'\n\n  <div class="marks rv" data-n="{len(d["marks"])}">{marks}\n  </div>'
    cols = ''
    for hexc, name, note in d.get('colors', []):
        cols += (f'\n    <div class="pal-i"><div class="pal-c" style="background:{hexc}"></div>'
                 f'<div class="pal-h">{hexc}</div><div class="pal-n">{name}</div>'
                 f'<p class="pal-t">{typo(note)}</p></div>')
    pal = f'\n\n  <div class="pal" data-n="{len(d["colors"])}">{cols}\n  </div>' if cols else ''
    motion = ''
    if d.get('motion'):
        m = d['motion']
        motion = (f'\n\n  <figure class="motion rv"><canvas class="motion-cv"></canvas>'
                  f'<img class="motion-poster" src="img/cases/{c["slug"]}/{m["poster"]}" alt="" loading="lazy">'
                  f'<div class="motion-word" aria-hidden="true">{m["word"]}</div>'
                  f'<figcaption>{m["caption"]}<i>анимация</i></figcaption></figure>\n  {MOTION_JS}')
    tiles = ''
    if d.get('tiles'):
        items = ''.join(f'\n    <figure class="tile"><img src="img/cases/{c["slug"]}/{src}" '
                        f'alt="{esc(alt)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'
                        for src, alt, cap in d['tiles'])
        tiles = f'\n\n  <div class="tiles rv" data-n="{len(d["tiles"])}">{items}\n  </div>'
    photo = ''
    if d.get('photo'):
        src, alt, cap, kind = d['photo']
        ratio = f' style="aspect-ratio:{d["ratio"]}"' if d.get('ratio') else ''
        photo = (f'\n\n  <figure class="frame full rv" style="margin-top:clamp(38px,4.5vw,66px)">'
                 f'<div class="frame-i"><img src="img/cases/{c["slug"]}/{src}" '
                 f'alt="{esc(alt)}" loading="lazy"{ratio}></div>'
                 f'<figcaption>{cap}<i>{kind}</i></figcaption></figure>')
    note = ''
    if d.get('note'):
        note = ('\n\n  <p class="body rv" style="margin-top:clamp(18px,2vw,28px);'
                f'max-width:64ch">{typo(d["note"])}</p>')
    n_marks = len(d.get('marks', []))
    word = 'начертание' if n_marks == 1 else 'начертания' if n_marks < 5 else 'начертаний'
    mono = d.get('mono') or f'{n_marks} {word}'
    return f"""<section id="ident">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — {d.get('idx', 'знак')}</span><h2 class="sec-title">{d.get('title', 'фирменный стиль')}</h2></div>
    <span class="mono">{mono}</span>
  </div>

  <p class="lead rv" style="max-width:64ch;margin-top:clamp(28px,3.4vw,48px)">{typo(d["lead"])}</p>{note}{marks_html}{motion}{pal}{tiles}{photo}
</section>"""


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
    k = len(c['shots'])
    ex = 'пример' if k % 10 == 1 and k != 11 else 'примера' if k % 10 in (2, 3, 4) and k not in (12, 13, 14) else 'примеров'
    mono = f'{live} с площадки' if live else f'{k} {ex} из брендбука'
    return f'''<section id="shots">
  <div class="sec-head rv">
    <div><span class="sec-idx">{n:02d} — носители</span><h2 class="sec-title">как это живёт</h2></div>
    <span class="mono">{mono}</span>
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


def result(c, n, extra=''):
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
{block}{tail}{extra}
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


TINT = '''<style>
#work,#result{background:var(--bg-2)}
#result{padding-bottom:clamp(70px,9vw,150px)}
#result .live{margin:clamp(28px,3.4vw,52px) 0 0}
#result .live:hover{background:var(--bg)}
</style>'''


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
        tail_blocks = [live(c), nxt(CASES[(i + 1) % len(CASES)])]
        head_blocks = [cover(c), facts(c)]
        if c.get('tint'):
            # ритм страницы: «что сделали» и «результат» на серо-белой подложке,
            # ссылка на сайт уходит внутрь итога и остаётся на его подложке
            mid[-1] = result(c, len(chain), '\n\n  ' + tail_blocks.pop(0))
            head_blocks.insert(0, TINT)
        body = '\n\n'.join(head_blocks + mid + tail_blocks)
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
