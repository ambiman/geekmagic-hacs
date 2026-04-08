# Changes vs upstream (adrienbrault/geekmagic-hacs)

This fork contains the following additions and fixes on top of the upstream project.

---

## New Features

### Picture Widget — Multi-Image Cycling (`fix: cycle picture widget images using module-level state`)

The Picture widget can now reliably cycle through multiple images across screen refreshes.

**Problem fixed:** The cycle index was stored on the coordinator instance, which gets
recreated whenever Home Assistant encounters an aiohttp "Session is closed" error.
This caused the widget to always display only the first configured image.

**Fix:** Cycle indices are now stored in a module-level dict (`_PICTURE_CYCLE_STATE`)
that survives coordinator restarts. Additionally, single-source slots no longer reset
the shared counter (the `(idx+1) % 1 == 0` arithmetic bug).

---

### Entity Widget — Configurable Icon Layout (`feat: add horizontal icon layout option to Entity widget`)

A new **"Icon Layout"** option is available in the Entity widget configuration:

| Option | Description |
|--------|-------------|
| `auto` *(default)* | Automatically selects based on slot aspect ratio: portrait → horizontal, landscape → stacked |
| `stacked` | Original behaviour: icon top, value middle, label bottom |
| `horizontal` | Icon on the left, label + value on the right |

**Why this matters:** In narrow grid cells (e.g. a 3-column layout produces ~80 px wide
slots), the stacked layout gives the value text only ~40 px of height. The horizontal
layout gives it ~85 px, resulting in a significantly larger and more readable font.

---

## Bug Fixes

### Media Selector Value Storage (`fix: store raw ha-selector media value without frontend conversion`)

The `ha-selector[media]` component returns a dict `{"media_content_id": "..."}` instead
of a plain string URL. The integration now stores the raw value and normalises it at
render time, preventing a `'dict' object has no attribute 'startswith'` error in the
picture widget preview.

### Local Media Source URL Decoding

Filenames with spaces or special characters in the HA media library (e.g.
`IMG 0150.jpg`) are now correctly decoded (`urllib.parse.unquote`) before the path is
resolved on the filesystem.

---

## Minor Improvements

- `style:` Minor code quality fixes across several files (`maxsplit=1`, `or`-shorthand,
  import ordering)
- `PictureWidget.__init__` now logs a warning for unrecognised `image_paths` entry
  formats instead of silently ignoring them
