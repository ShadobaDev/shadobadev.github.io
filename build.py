"""Generates a static site (_site/) from public GitHub repositories.

Static HTML instead of fetch() in the browser: Google sees repo links immediately.
Run locally: python build.py  -> open _site/index.html
"""
import json, os, urllib.request
from datetime import date
from html import escape
from pathlib import Path

USER = "ShadobaDev"
NAME = "ShadobaDev"
EMAIL = "shadobadev@gmail.com"
SITE = f"https://{USER.lower()}.github.io/"
TAGLINE = "C, C++ and Python developer. Tools for comic and webtoon creators."


def fetch_repos():
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        repos = json.load(r)
    # only own, non-archived repos with a description; skip the site's own repo
    return [r for r in repos if r["description"] and not r["fork"] and not r["archived"]
            and r["name"].lower() != f"{USER.lower()}.github.io"]


def card(r):
    topics = "".join(f"<li>{escape(t)}</li>" for t in r.get("topics", []))
    lang = f'<span class="lang">{escape(r["language"])}</span>' if r["language"] else ""
    home = f' · <a href="{escape(r["homepage"])}">demo</a>' if r.get("homepage") else ""
    return f"""<article>
  <h3><a href="{escape(r['html_url'])}">{escape(r['name'])}</a></h3>
  <p>{escape(r['description'])}</p>
  <p class="meta">{lang} ★ {r['stargazers_count']}{home}</p>
  {f'<ul class="topics">{topics}</ul>' if topics else ''}
</article>"""


def ld_json(repos):
    data = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": SITE,
        "mainEntity": {
            "@type": "Person", "name": NAME, "email": f"mailto:{EMAIL}", "url": SITE,
            "sameAs": [f"https://github.com/{USER}"],
        },
        "hasPart": [{
            "@type": "SoftwareSourceCode", "name": r["name"], "description": r["description"],
            "codeRepository": r["html_url"], "programmingLanguage": r["language"],
            "author": {"@type": "Person", "name": NAME},
        } for r in repos],
    }
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


def page(repos):
    names = ", ".join(r["name"] for r in repos)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NAME} – open source project portfolio</title>
<meta name="description" content="{escape(TAGLINE)} Projects: {escape(names)}.">
<link rel="canonical" href="{SITE}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{NAME} – portfolio">
<meta property="og:description" content="{escape(TAGLINE)}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="https://github.com/{USER}.png">
<script type="application/ld+json">{ld_json(repos)}</script>
<style>
:root {{ color-scheme: light dark; --fg:#1f2328; --mute:#59636e; --bg:#fff; --card:#f6f8fa; --line:#d1d9e0; --acc:#0969da; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fg:#e6edf3; --mute:#9198a1; --bg:#0d1117; --card:#151b23; --line:#3d444d; --acc:#4493f8; }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font:16px/1.6 system-ui, sans-serif; color:var(--fg); background:var(--bg); }}
main {{ max-width:860px; margin:0 auto; padding:48px 16px; }}
header {{ display:flex; gap:20px; align-items:center; flex-wrap:wrap; margin-bottom:40px; }}
header img {{ width:96px; height:96px; border-radius:50%; }}
h1 {{ margin:0; font-size:2rem; }}
a {{ color:var(--acc); }}
.lead {{ margin:4px 0; color:var(--mute); }}
.grid {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); }}
article {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:16px; }}
article h3 {{ margin:0 0 8px; font-size:1.1rem; overflow-wrap:anywhere; }}
article p {{ margin:0 0 8px; }}
.meta {{ color:var(--mute); font-size:.9rem; }}
.lang {{ margin-right:8px; }}
.topics {{ list-style:none; padding:0; margin:0; display:flex; flex-wrap:wrap; gap:6px; }}
.topics li {{ font-size:.8rem; padding:0 8px; border-radius:999px; border:1px solid var(--line); }}
footer {{ margin-top:48px; color:var(--mute); font-size:.85rem; }}
</style>
</head>
<body>
<main>
<header>
  <img src="https://github.com/{USER}.png?size=192" alt="{NAME} avatar" width="96" height="96">
  <div>
    <h1>{NAME}</h1>
    <p class="lead">{escape(TAGLINE)}</p>
    <p class="lead"><a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="https://github.com/{USER}" rel="me">github.com/{USER}</a></p>
  </div>
</header>
<h2>Projects</h2>
<section class="grid">
{chr(10).join(card(r) for r in repos)}
</section>
<footer>Updated {date.today().isoformat()}</footer>
</main>
</body>
</html>
"""


def main():
    repos = fetch_repos()
    out = Path("_site")
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page(repos), encoding="utf-8")
    (out / "googleb60ec623b69e2eb9.html").write_text("google-site-verification: googleb60ec623b69e2eb9.html", encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"<url><loc>{SITE}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n</urlset>\n",
        encoding="utf-8")
    assert repos and f"mailto:{EMAIL}" in (out / "index.html").read_text(encoding="utf-8")
    print(f"OK: {len(repos)} repos -> {out.resolve()}")


if __name__ == "__main__":
    main()
