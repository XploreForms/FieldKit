"""Bundle Field Kit (repo main) into one self-contained HTML preview for a claude.ai artifact.
Each page runs in a full-screen srcdoc iframe; links between pages are routed by the shell."""
import json, re, pathlib, sys

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).resolve().parent.parent))
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/fk-shots/fieldkit-preview.html")
PAGES = ["index", "fieldcam", "fieldnotes", "fieldstock"]
read = lambda f: (SRC / f).read_text(encoding="utf-8")
version = re.search(r'version:\s*"([^"]+)"', read("version.js")).group(1)

PREAMBLE = r"""<base href="about:srcdoc"><script>
/* Field Kit preview: pretend to be the Claude preview so Google sign-in shows "Website only",
   and send links between tools to the preview shell. */
window.claude = window.claude || { use: function () {} };
(function () {
  var TOOLS = /^(index|fieldcam|fieldnotes|fieldstock)\.html(#.*)?$/;
  window.__fkNav = function (u) {
    u = String(u || "");
    if (TOOLS.test(u)) { parent.postMessage({ fkNav: u }, "*"); return; }
    if (/^https?:|^mailto:|^tel:/.test(u)) { window.open(u, "_blank"); return; }
  };
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest && e.target.closest("a[href]");
    if (!a || e.defaultPrevented) return;
    var h = a.getAttribute("href") || "";
    if (TOOLS.test(h)) { e.preventDefault(); __fkNav(h); }
    else if (/^https?:/.test(h)) { e.preventDefault(); window.open(h, "_blank"); }
  }, false);
  /* history inside the preview frame: hash-only URLs, made absolute against this frame (about:srcdoc) so no
     browser resolves them against the outer page; if a browser still refuses (Safari is strict), carry on anyway
     so the screen still changes (e.g. Start New Job). */
  ["pushState", "replaceState"].forEach(function (m) {
    var orig = history[m];
    history[m] = function (st, t, u) {
      if (typeof u === "string") {
        var base = String(location.href).split("#")[0];
        if (u.charAt(0) === "#") u = base + u;
        else if (u === "" || /^(about:srcdoc|srcdoc)?(\?.*)?$/.test(u)) u = base;
      }
      try { return orig.call(history, st, t, u); } catch (e) { try { return orig.call(history, st, t); } catch (e2) {} }
    };
  });
  var h = "__FK_HASH__";
  if (h) { try { history.replaceState(null, "", h); } catch (e) {} if (location.hash !== h) try { location.hash = h; } catch (e) {} }
})();
</script>"""


def inline_fonts(css):
    """The preview's pages run from srcdoc, so bundled fonts go in as data: URLs (1.20.76)."""
    import base64
    def sub(m):
        return 'url("data:font/woff;base64,' + base64.b64encode((SRC / m.group(1)).read_bytes()).decode() + '")'
    return re.sub(r'url\("(fonts/[^"]+\.woff)"\)', sub, css)

def inline_js(m):
    attrs, src = m.group(1) + m.group(3), m.group(2)
    js = read(src).replace("</script", "<\\/script")
    return f"<script{attrs}>\n{js}\n</script>"


def build(page):
    html = read(page + ".html")
    # drop install bits and file icons (they can't load from a single file); keep data: icons
    html = re.sub(r'<link rel="(?:icon|apple-touch-icon|manifest|shortcut icon)"[^>]*href="(?!data:)[^"]*"[^>]*>\n?', "", html)
    html = re.sub(r'<script src="https://accounts\.google\.com/gsi/client"[^>]*></script>\n?', "", html)
    html = html.replace('<link rel="stylesheet" href="fieldkit.css">', "<style>\n" + inline_fonts(read("fieldkit.css")) + "\n</style>")
    html = re.sub(r'<link rel="preload" href="fonts/[^"]+"[^>]*>\n?', "", html)   # the fonts are inside the CSS here
    html = re.sub(r'<script((?:\s+[a-z-]+="[^"]*")*?)\s+src="([a-z-]+\.js)"((?:\s+[a-z-]+="[^"]*")*)\s*></script>', inline_js, html)
    # navigation between tools goes through the shell
    html = re.sub(r'location\.href\s*=(?!=)\s*([^;\n]+?)\s*;', r'__fkNav(\1);', html)
    html = re.sub(r'location\.(?:replace|assign)\(', '__fkNav(', html)
    html = html.replace("location.pathname + location.search", 'location.href.split("#")[0]')
    html = re.sub(r'<head>', "<head>\n" + PREAMBLE, html, count=1)
    assert "__fkNav" in html and not re.search(r'^<script src="[a-z-]+\.js"', html, re.M), page
    return html


pages = {p + ".html": build(p) for p in PAGES}
data = json.dumps(pages).replace("</", "<\\/")

SHELL = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Field Kit {version} preview</title>
<style>
  :root {{ --bg: #F2F5F3; color-scheme: light; box-sizing: border-box; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #0B1715; color-scheme: dark; }} }}
  :root[data-theme="dark"] {{ --bg: #0B1715; color-scheme: dark; }}
  html, body {{ height: 100%; margin: 0; }}
  body {{ background: var(--bg); }}
  iframe {{ display: block; width: 100%; height: 100%; border: 0; background: var(--bg); }}
  /* big screens: the same phone-sized frame as frame.html on the live site (1.20.61) */
  @media (min-width:600px) and (min-height:700px) {{
    body {{ display: grid; place-items: center; background: #D6E0DC; }}
    iframe {{ width: 412px; height: min(calc(100vh - 48px), 915px); border-radius: 28px; box-shadow: 0 18px 50px rgba(0,40,30,.22), 0 2px 8px rgba(0,40,30,.12); }}
  }}
</style>
</head><body>
<iframe id="fk" title="Field Kit" allow="camera; geolocation; clipboard-read; clipboard-write; fullscreen"></iframe>
<script id="fkPages" type="application/json">{data}</script>
<script>
(function () {{
  var PAGES = JSON.parse(document.getElementById("fkPages").textContent);
  var frame = document.getElementById("fk");
  function go(u) {{
    var m = /^([a-z]+\\.html)(#.*)?$/.exec(u) || [];
    var page = PAGES[m[1]] ? m[1] : "index.html", hash = m[2] || "";
    frame.srcdoc = PAGES[page].replace('"__FK_HASH__"', JSON.stringify(hash));
  }}
  addEventListener("message", function (e) {{ if (e.source === frame.contentWindow && e.data && e.data.fkNav) go(e.data.fkNav); }});
  go("index.html");
}})();
</script>
</body></html>
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(SHELL, encoding="utf-8")
print(OUT, f"{OUT.stat().st_size/1e6:.2f} MB", "version", version)
