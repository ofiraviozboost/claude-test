# Generating the Hebrew-RTL PDF report

This project's PDF reports are plain HTML rendered by the sandbox's
pre-installed headless Chromium — there's no weasyprint or playwright
python/node package available, and LibreOffice's `soffice` renders styled
HTML tables poorly, so don't reach for either.

## The HTML

Write a standalone `.html` file with:

- `<html lang="he" dir="rtl">` and `text-align: right` on `body`.
- Font stack that actually has Hebrew glyphs on this box:
  `"DejaVu Sans", "FreeSans", "Liberation Sans", Arial, sans-serif`. Don't
  reach for a webfont — there's no network fetch in the print step and these
  system fonts already cover Hebrew.
- Three intro cards side by side (מה בדקנו / מה באים לפתור / מה הממצא אומר)
  above the table — keeps the "why" visible without making the reader hunt
  for it. Each is a `.intro-card` div with a bold `.k` label and a `.v` body.
- The data table with a dark header row, alternating row shading, and the
  total row visually distinct (dark background, bold, matching the header).
  Gap/exception numbers get a `.gap-cell` red bold style so the number that
  matters is the one that jumps out.
- A short `.note` block under the table listing what got filtered out and
  why (classification fixes, unified sibling projects, non-relevant
  investments) — the reader needs to see what's *not* in the number as much
  as what is.

See the CSS in this file's sibling audit session for the exact rule set if
you want to start from a known-good copy — the pattern above is what to
reproduce, not to reinvent per run.

## Converting to PDF

```bash
/opt/pw-browsers/chromium-*/chrome-linux/chrome \
  --headless --disable-gpu --no-sandbox --disable-software-rasterizer \
  --print-to-pdf=output.pdf --print-to-pdf-no-header --no-pdf-header-footer \
  file:///absolute/path/to/report.html
```

(The `chromium-*` glob resolves to something like `chromium-1194` — check
with `find /opt/pw-browsers -maxdepth 1 -iname 'chromium-*'` if it's moved.)

DBus warnings on stderr are harmless noise in this sandbox — ignore them as
long as the PDF file gets written.

## Verifying it before sending

There's no `pdftoppm`/`gs`/PyMuPDF in this sandbox to rasterize the PDF
itself, so verify the **HTML** instead, with the same Chromium binary in
screenshot mode, and Read the resulting PNG to eyeball it:

```bash
/opt/pw-browsers/chromium-*/chrome-linux/chrome \
  --headless --disable-gpu --no-sandbox --disable-software-rasterizer \
  --screenshot=preview.png --window-size=1240,1754 \
  file:///absolute/path/to/report.html
```

Check RTL layout (project names hugging the right edge, numbers reading
right-to-left across the row), Hebrew glyphs rendering instead of tofu boxes,
and that the whole table fits without an awkward page break before sending.
