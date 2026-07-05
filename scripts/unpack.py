#!/usr/bin/env python3
"""Extract a bundled index.html (design-canvas export) into separate files."""

import base64
import gzip
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMAGE_NAMES = {
    "7dbb3cd1-693a-45f5-aa8d-c9c214d4de5c": "hero.jpg",
    "1cee1e62-3f2d-4148-915d-5154cc82b780": "story-together.jpg",
    "3fc13dc1-8c24-46f6-b22d-c05c1b987712": "story-anton.jpg",
    "d923659e-0933-44fa-96dc-20557a0eba3f": "story-helen.jpg",
}
JS_NAMES = {
    "53296ed4-8f22-4e73-80a9-3f8e1c453f8f": "dc-runtime.js",
    "17ea3016-659e-46b4-a34c-d8f4f124dbd7": "image-slot.js",
}


def decode_entry(entry):
    raw = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        raw = gzip.decompress(raw)
    return raw


def unpack(bundled_path=None):
    bundled_path = bundled_path or os.path.join(ROOT, "index.bundled.html")
    if not os.path.exists(bundled_path):
        bundled_path = os.path.join(ROOT, "index.html")
        if 'type="__bundler/manifest"' not in open(bundled_path).read():
            sys.exit("No bundled index.html found. Pass path to bundled file.")

    with open(bundled_path) as f:
        html = f.read()

    manifest = json.loads(
        re.search(r'<script type="__bundler/manifest">\s*(.*?)\s*</script>', html, re.DOTALL).group(1)
    )
    template = json.loads(
        re.search(r'<script type="__bundler/template">\s*(.*?)\s*</script>', html, re.DOTALL).group(1)
    )

    uuid_to_path = {}
    for d in ["assets/images", "assets/fonts", "css", "js"]:
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)

    for uid, entry in manifest.items():
        raw = decode_entry(entry)
        mime = entry["mime"]
        if mime == "image/jpeg":
            rel = f"assets/images/{IMAGE_NAMES.get(uid, uid + '.jpg')}"
        elif mime == "font/woff2":
            rel = f"assets/fonts/{uid}.woff2"
        elif mime == "text/javascript":
            rel = f"js/{JS_NAMES.get(uid, uid + '.js')}"
        elif mime == "application/json":
            rel = ".image-slots.state.json"
        else:
            continue
        uuid_to_path[uid] = rel
        with open(os.path.join(ROOT, rel), "wb") as f:
            f.write(raw)

    out = template
    for uid, path in sorted(uuid_to_path.items(), key=lambda x: -len(x[0])):
        out = out.replace(uid, path)

    styles = re.findall(r"<style>(.*?)</style>", out, re.DOTALL)
    fonts_css = styles[0].strip().replace('url("assets/fonts/', 'url("../assets/fonts/') if styles else ""
    site_css = styles[1].strip() if len(styles) > 1 else ""

    with open(os.path.join(ROOT, "css/fonts.css"), "w") as f:
        f.write(fonts_css + "\n")
    with open(os.path.join(ROOT, "css/site.css"), "w") as f:
        f.write(site_css + "\n")

    out = re.sub(r"<style>.*?</style>\s*", "", out, flags=re.DOTALL, count=2)

    comp_match = re.search(r'(<script type="text/x-dc".*?</script>)', out, re.DOTALL)
    comp_script = comp_match.group(1) if comp_match else ""
    if comp_match:
        out = out[: comp_match.start()] + out[comp_match.end() :]

    app_match = re.search(r"class Component extends DCLogic \{.*?\n\}", comp_script, re.DOTALL)
    app_js = app_match.group(0) + "\n" if app_match else ""
    with open(os.path.join(ROOT, "js/app.js"), "w") as f:
        f.write(app_js)

    helmet_links = """<meta charset="utf-8">
<title>Anton &amp; Helen — Birthday Party</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
<link rel="stylesheet" href="css/fonts.css">
<link rel="stylesheet" href="css/site.css">
<script src="js/dc-runtime.js"></script>
<script src="js/image-slot.js"></script>"""

    out = re.sub(r"<helmet>.*?</helmet>", f"<helmet>\n{helmet_links}\n</helmet>", out, flags=re.DOTALL)
    out = re.sub(
        r"(<head>\s*<meta charset=\"utf-8\">\s*<meta name=\"viewport\"[^>]*>\s*)\s*<script src=\"js/dc-runtime\.js\"></script>\s*",
        r"\1",
        out,
    )

    if comp_match and app_js:
        props_match = re.search(r'data-props="(\{.*?\})"', comp_script, re.DOTALL)
        props = props_match.group(1).replace("&quot;", '"') if props_match else "{}"
        dc_script = f'<script type="text/x-dc" data-dc-script="" data-props=\'{props}\'>\n{app_js}</script>'
        out = out.replace("</body></html>", dc_script + "\n</body></html>")

    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(out)

    print(f"Unpacked {bundled_path} → {ROOT}")


if __name__ == "__main__":
    unpack(sys.argv[1] if len(sys.argv) > 1 else None)
