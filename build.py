"""Generate index.html (es) and en/index.html from content.json.

Usage: python3 build.py            # generate
       python3 build.py --check    # also check every link answers (needs network)

Only live projects are listed: an entry without links is skipped. When a
project's site dies, point it to its repo instead of removing it.
Text fields can be "es|en" when the two languages differ; projects and news
carry "es" and "en" keys. Edit content.json, run this, commit both outputs.
"""
import json
import sys
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://www.eduherraiz.com/"
MONTHS = {"es": "ene feb mar abr may jun jul ago sep oct nov dic".split(),
          "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()}


def pick(text, lang):
    if "|" not in text:
        return text
    es, en = text.split("|", 1)
    return es if lang == "es" else en


def ext(url):
    return f'<a href="{escape(url)}" rel="noopener">'


def wheel(size=28):
    # Llull's Figura A in miniature, same geometry as the channel banner
    import math
    c, r = 50, 38
    pts = [(c + r * math.cos(i * 2 * math.pi / 9 - math.pi / 2), c + r * math.sin(i * 2 * math.pi / 9 - math.pi / 2)) for i in range(9)]
    chords = "".join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>'
                     for i, a in enumerate(pts) for b in pts[i + 1:])
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6"/>' for x, y in pts)
    return (f'<svg class="wheel" width="{size}" height="{size}" viewBox="0 0 100 100" aria-hidden="true">'
            f'<g class="chords">{chords}</g><circle class="ring" cx="50" cy="50" r="{r}"/><g class="dots">{dots}</g></svg>')


def date(d, lang, ui):
    y, m = d.split("-")
    return f"{MONTHS[lang][int(m) - 1]} {y}"


def project(p, lang, ui):
    meta = " · ".join(x for x in [p.get("year", ""), pick(p.get("tags", ""), lang)] if x)
    links = " ".join(f'{ext(u)}{escape(pick(k, lang))}</a>' for k, u in p.get("links", {}).items())
    return f"""      <li class="proj">
        <div class="proj-head"><h4>{escape(pick(p["name"], lang))}</h4><span class="meta">{escape(meta)}</span></div>
        <p>{escape(p[lang])}</p>{f'<p class="links">{links}</p>' if links else ''}
      </li>"""


def page(c, lang):
    ui = c["ui"][lang]
    L = c["links"]
    prefix = "" if lang == "es" else "../"
    news = "\n".join(
        f'      <li><span class="date">{date(n["date"], lang, ui)}</span>'
        + (f'{ext(n["url"])}{escape(n[lang])}</a>' if n.get("url") else f'<span>{escape(n[lang])}</span>')
        + "</li>" for n in c["news"])
    def plist(items):
        return '    <ul class="projects">\n' + "\n".join(project(p, lang, ui) for p in items if p.get("links")) + "\n    </ul>"
    groups = plist(c["projects"]["list"]) + f'\n    <h3>{ui["oss"]}</h3>\n' + plist(c["projects"]["oss"])
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(ui["title"])}</title>
<meta name="description" content="{escape(ui["description"])}">
<meta name="author" content="{c["name"]}">
<meta name="google-site-verification" content="uFsWpgshuLZI64z67QiCd8z1NHCkqKld4V2fwli7oxQ">
<link rel="canonical" href="{SITE}{'' if lang == 'es' else 'en/'}">
<link rel="alternate" hreflang="es" href="{SITE}">
<link rel="alternate" hreflang="en" href="{SITE}en/">
<link rel="alternate" hreflang="x-default" href="{SITE}">
<meta property="og:title" content="{escape(ui["title"])}">
<meta property="og:description" content="{escape(ui["description"])}">
<meta property="og:image" content="{SITE}assets/edu.png">
<meta property="og:url" content="{SITE}{'' if lang == 'es' else 'en/'}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<main>
  <nav class="lang"><a href="{ui["lang_href"]}" hreflang="{'en' if lang == 'es' else 'es'}">{ui["lang_switch"]}</a></nav>

  <header class="hero">
    <img class="portrait" src="{prefix}assets/edu.png" width="132" height="132" alt="{c["name"]}">
    <div>
      <h1>{c["name"]}</h1>
      <p class="tagline">{escape(ui["tagline"])}</p>
      <p class="social">{ext(L["github"])}GitHub</a> {ext(L["linkedin"])}LinkedIn</a> {ext(L["youtube"])}YouTube</a> <a href="mailto:{c["email"]}">{c["email"]}</a></p>
    </div>
  </header>

  <section class="ars">
    <h2>{wheel()}<span>Ars Magna</span></h2>
    <p>{escape(ui["ars_intro"])} {ext(L["youtube"])}{ui["ars_link"]} →</a></p>
    <h3>{ui["news"]}</h3>
    <ul class="news">
{news}
    </ul>
  </section>

  <section>
    <h2>{ui["projects"]}</h2>
{groups}
  </section>

  <section>
    <h2>{ui["work"]}</h2>
    <p>{escape(ui["work_text"])} {ext(L["linkedin"])}LinkedIn →</a></p>
  </section>

  <section>
    <h2>{ui["contact"]}</h2>
    <p>{escape(ui["contact_text"])} <a href="mailto:{c["email"]}">{c["email"]}</a></p>
  </section>

  <footer>© {c["name"]} · {escape(ui["footer"])}</footer>
</main>
</body>
</html>
"""


def check(c):
    urls = [n["url"] for n in c["news"] if n.get("url")]
    urls += [u for k in c["projects"] for p in c["projects"][k] for u in p.get("links", {}).values()]
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
    (ROOT / "index.html").write_text(page(c, "es"))
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en" / "index.html").write_text(page(c, "en"))
    print("index.html, en/index.html")


if __name__ == "__main__":
    main()
