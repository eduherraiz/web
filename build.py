"""Generate the site from content.json.

Usage: python3 build.py            # generate
       python3 build.py --check    # also check every link answers (needs network)

Output, per language (es at the root, the others under /<lang>/):
  index.html                 home
  ars-magna-lab/index.html   why the name

Only live projects are listed: an entry without links is skipped. When a
project's site dies, point it to its repo instead of removing it.
Texts are {"es": ..., "en": ..., "ca": ...} or a plain string when they don't change.
"""
import json
import math
import sys
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://www.eduherraiz.com/"
LANG_NAMES = {"es": "Español", "en": "English", "ca": "Català"}
WORK_NAMES = {"nagarro": "Nagarro", "apsl": "APSL"}


def t(v, lang):
    return v[lang] if isinstance(v, dict) else v


def ext(url):
    return f'<a href="{escape(url)}" rel="noopener">'


def base(lang):
    return "" if lang == "es" else f"{lang}/"


def figure_a(size, letters=False):
    # Llull's Figura A: nine principles B..K joined by chords, same geometry as the channel banner
    c, r = 100, 74
    pts = [(c + r * math.cos(i * 2 * math.pi / 9 - math.pi / 2), c + r * math.sin(i * 2 * math.pi / 9 - math.pi / 2)) for i in range(9)]
    chords = "".join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>'
                     for i, a in enumerate(pts) for b in pts[i + 1:])
    if letters:
        nodes = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11"/><text x="{x:.1f}" y="{y + 4.5:.1f}">{ch}</text>'
                        for (x, y), ch in zip(pts, "BCDEFGHIK"))
        rings = '<circle class="ring2" cx="100" cy="100" r="92"/>'
    else:
        nodes = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12"/>' for x, y in pts)
        rings = ""
    return (f'<svg class="wheel{" big" if letters else ""}" width="{size}" height="{size}" viewBox="0 0 200 200" aria-hidden="true">'
            f'{rings}<g class="chords">{chords}</g><circle class="ring" cx="100" cy="100" r="{r}"/>'
            f'<g class="dots">{nodes}</g><circle class="hub" cx="100" cy="100" r="5"/></svg>')


def shell(c, lang, path, title, description, body):
    """path: page path inside a language, '' for home or 'ars-magna-lab/'."""
    here = base(lang) + path
    prefix = "../" * here.count("/")
    langs = c["langs"]
    nav = " ".join(
        f'<a href="{prefix}{base(l)}{path}" hreflang="{l}" lang="{l}"{" aria-current=page" if l == lang else ""}>{l.upper()}</a>'
        for l in langs)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{base(l)}{path}">' for l in langs)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="author" content="{c["name"]}">
<meta name="google-site-verification" content="uFsWpgshuLZI64z67QiCd8z1NHCkqKld4V2fwli7oxQ">
<link rel="canonical" href="{SITE}{here}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{SITE}{path}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:image" content="{SITE}assets/edu.png">
<meta property="og:url" content="{SITE}{here}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<main>
  <nav class="lang" aria-label="{LANG_NAMES[lang]}">{nav}</nav>
{body}
  <footer>© {c["name"]} · {escape(c["ui"][lang]["footer"])}</footer>
</main>
</body>
</html>
"""


def project(p, lang, prefix):
    meta = " · ".join(x for x in [p.get("year", ""), t(p.get("tags", ""), lang)] if x)
    links = " ".join(f'{ext(u)}{escape(t(k, lang))}</a>' for k, u in p["links"])
    img = (f'<a class="thumb" href="{escape(p["links"][0][1])}" rel="noopener" tabindex="-1">'
           f'<img src="{prefix}assets/projects/{p["image"]}" width="160" height="120" alt="" loading="lazy"></a>') if p.get("image") else ""
    return f"""      <li class="proj">
        {img}
        <div>
          <div class="proj-head"><h4>{escape(t(p["name"], lang))}</h4><span class="meta">{escape(meta)}</span></div>
          <p>{escape(p[lang])}</p>
          <p class="links">{links}</p>
        </div>
      </li>"""


def home(c, lang):
    ui = c["ui"][lang]
    L = c["links"]
    prefix = "../" * base(lang).count("/")
    months = ui["months"].split()
    news = "\n".join(
        f'      <li><span class="date">{months[int(n["date"][5:]) - 1]} {n["date"][:4]}</span>'
        f'{ext(n["url"])}{escape(n[lang])}</a></li>' for n in c["news"])
    projects = "\n".join(project(p, lang, prefix) for p in c["projects"] if p.get("links"))
    work = escape(ui["work_text"])
    for k, urls in c["work_links"].items():
        work = work.replace("{" + k + "}", f'{ext(t(urls, lang))}{WORK_NAMES[k]}</a>')
    body = f"""
  <header class="hero">
    <img class="portrait" src="{prefix}assets/edu.png" width="132" height="132" alt="{c["name"]}">
    <div>
      <h1>{c["name"]}</h1>
      <p class="tagline">{escape(ui["tagline"])}</p>
      <p class="social">{ext(L["github"])}GitHub</a> {ext(L["linkedin"])}LinkedIn</a> {ext(L["youtube"])}YouTube</a> <a href="mailto:{c["email"]}">{c["email"]}</a></p>
    </div>
  </header>

  <section class="ars">
    <h2>{figure_a(30)}<span>Ars Magna Lab</span></h2>
    <p>{escape(ui["ars_intro"])}</p>
    <p class="more"><a href="ars-magna-lab/">{ui["why_link"]} →</a> {ext(L["youtube"])}{ui["ars_link"]} →</a></p>
    <h3>{ui["news"]}</h3>
    <ul class="news">
{news}
    </ul>
  </section>

  <section>
    <h2>{ui["projects"]}</h2>
    <ul class="projects">
{projects}
    </ul>
  </section>

  <section>
    <h2>{ui["work"]}</h2>
    <p>{work} {ext(L["linkedin"])}LinkedIn →</a></p>
  </section>

  <section>
    <h2>{ui["contact"]}</h2>
    <p>{escape(ui["contact_text"])} <a href="mailto:{c["email"]}">{c["email"]}</a></p>
  </section>
"""
    return shell(c, lang, "", ui["title"], ui["description"], body)


def name_page(c, lang):
    ui = c["ui"][lang]
    n = c["name_page"][lang]
    paras = lambda ps: "\n".join(f"    <p>{escape(p)}</p>" for p in ps)
    body = f"""
  <article class="essay">
    <p class="back"><a href="../">← {ui["back"]}</a></p>
    <h1>{escape(n["title"])}</h1>
    <p class="lead">{escape(n["lead"])}</p>
    <figure>{figure_a(260, letters=True)}</figure>
{paras(n["body"])}
    <h2>{escape(n["lab_title"])}</h2>
{paras(n["lab"])}
    <p class="back"><a href="../">← {ui["back"]}</a></p>
  </article>
"""
    return shell(c, lang, "ars-magna-lab/", f'{n["title"]} · {c["name"]}', n["lead"], body)


def check(c):
    urls = [n["url"] for n in c["news"]]
    urls += [u for p in c["projects"] for _, u in p.get("links", [])]
    urls += [t(us, l) for us in c["work_links"].values() for l in c["langs"]]
    urls += list(c["links"].values())
    bad = []
    for u in dict.fromkeys(urls):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            code = urllib.request.urlopen(req, timeout=15).status
        except Exception as e:
            code = getattr(e, "code", None) or type(e).__name__
        # LinkedIn answers 999 to bots; the link itself is fine
        if code not in (200, 999):
            bad.append(f"  {code}  {u}")
    print("\n".join(["enlaces caídos:"] + bad) if bad else "todos los enlaces responden")
    return not bad


def main():
    c = json.loads((ROOT / "content.json").read_text())
    if "--check" in sys.argv and not check(c):
        sys.exit(1)
    out = []
    for lang in c["langs"]:
        for rel, html in ((base(lang) + "index.html", home(c, lang)),
                          (base(lang) + "ars-magna-lab/index.html", name_page(c, lang))):
            f = ROOT / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(html)
            out.append(rel)
    print(", ".join(out))


if __name__ == "__main__":
    main()
