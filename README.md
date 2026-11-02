# Harbor City Archives — temporary site with real covers

**This site is a draft. It has NOT been uploaded to GitHub or deployed to HarborCityUSA.com.**

## What's included

- `index.html`: publishable temporary landing page. It references the web-optimized images in `assets/covers/`.
- `assets/covers/*.webp`: 31 real Kindle cover images, resized to 480 pixels wide. Keep these paths intact.
- `catalog.json`: KDP-sourced structured catalog with 32 records, format statuses, ASINs, and cover paths.
- `index.template.html` + `build_site.py`: build system so book information only lives in the structured catalog.
- `COVER_MANIFEST.csv`: exact mapping from uploaded source files to published site assets.

The separate `harborcity_filler_with_covers.html` is a self-contained, larger **preview**, with images embedded in the HTML itself. It is *not* the recommended GitHub version; this ZIP is.

## Local preview

Unzip the folder, then open `index.html` in Chrome or Firefox. All covers are relative to `assets/covers/`, so if you only copy the HTML without the assets the images will not display.

For a local web server, from this directory run:

```sh
python3 -m http.server 8000
```

Then visit `http://localhost:8000/` on that computer.

## GitHub Pages, later

1. First identify the repository that currently serves HarborCityUSA.com and the publishing branch/folder.
2. Back up the current site (`index.html` and related assets) before overwriting anything.
3. Copy `index.html` and the **entire** `assets/covers/` directory from this package into the actual published directory.
4. Keep `.nojekyll` if the repository already uses it. Ensure domain configuration such as `CNAME` remains intact.
5. Commit to the branch only when you're ready. Don't change GoDaddy DNS settings unless the existing hosting configuration requires it.

The build-support files can also live in the repository, but GitHub Pages only needs `index.html` and the cover assets for this temporary page.

## Updating the catalog

Edit `catalog.json` and run:

```sh
python3 build_site.py
```

For a new cover, create a small WebP and put it in `assets/covers/`, then set the book's `cover` field to its relative path and rebuild. Preserve the original Kindle JPG in the publishing assets library. Use the cover manifest to keep matching exact rather than guessing by filename.

## Current editorial checks before public deployment

- KDP snapshot as provided November 1, 2026. Publication and format statuses may have changed.
- **The Eighth File**: listed as Kindle preorder for November 2, 2026 in the supplied snapshot. Verify the current live status before launch.
- **The Unbreakable Fool**: listed as Kindle live in the export, although the author has described holding it for rewriting. Confirm whether its site entry should be featured before launch.
- **The CLH Armor Series**: Kindle book is in catalog; front cover image is missing from uploaded assets. A typographic placeholder remains.
- **The QRA**: cover exists, but book is not in the supplied KDP catalog. It has intentionally **not** been displayed as a released title.
- Some book hooks are awaiting supplied blurbs and deliberately show an archive-pending note.
- All available ASINs link to `https://www.amazon.com/dp/<ASIN>`.

**Do not upload the 41 MB original `harborcity_covers.tar.gz` to GitHub Pages.** The lightweight copies replace it on the site, without modifying the original artwork.
