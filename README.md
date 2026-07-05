# Anton & Helen — Birthday Party

Static site for [helen-tony.space](https://helen-tony.space/).

## Structure

```
index.html              Main page (HTML markup)
css/
  fonts.css             @font-face rules
  site.css              Layout, gallery, mobile tweaks
js/
  dc-runtime.js         Page runtime (countdown, tabs)
  image-slot.js         Gallery photo slots
  app.js                Component logic (also inlined in index.html)
assets/
  images/               hero.jpg, story-*.jpg
  fonts/                Local woff2 font files
.image-slots.state.json Gallery slot images (filled photos)
scripts/
  unpack.py             Re-extract from bundled export if needed
index.bundled.html      Original single-file export (backup)
```

## Edit

- **Text / layout** — edit `index.html`
- **Styles** — edit `css/site.css` or `css/fonts.css`
- **Countdown / tabs logic** — edit `js/app.js`, then copy the class into the `<script type="text/x-dc">` block at the bottom of `index.html`
- **Photos in story section** — replace files in `assets/images/`
- **Gallery photos** — managed via `.image-slots.state.json`

## Local preview

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy

Push to `main` — GitHub Pages serves from repo root.
