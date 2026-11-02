# HARBOR CITY ARCHIVES — Interim Static Site (Revision 2)

**Status:** LOCAL PREVIEW / NOT DEPLOYED. Back up the current live website before replacing any files.

This package is a static, responsive public archive for HarborCityUSA.com. It is compatible with GitHub Pages or a typical static web host. It does not require a database or server-side code to display books. The catalog works without JavaScript; the Kit subscription form loads from Kit when online.

## Publishing this site

When deployment is authorized, upload `index.html`, `catalog.json`, and the `assets/` folder to the actual public web root. Do not upload the original 40 MB cover masters; the web covers inside `assets/covers` are already optimized. Verify the active GitHub Pages repository and DNS setup first; GoDaddy may be only the domain registrar.

The `https://harborcityusa.com/assets/harbor-city-archive-share.jpg` Open Graph image URL becomes valid after these files are deployed to that domain. In an offline preview, chat or social link cards cannot resolve the production URL.

## Source of truth / adding books

`catalog.json` is the master data source for titles, subtitles, pen names, series numbers, Kindle/paperback/hardcover statuses, ASINs, available cover paths, short descriptions, audience labels, and future connected-record arrays. Data originated from the user's Nov. 2026 KDP Bookshelf export, with audience categories conservatively derived from the SHIVA reading-pipeline inventory; these should receive an editorial review.

To regenerate the raw HTML and Book JSON-LD after editing `catalog.json`, run:

```
python3 build_revision.py
```

Python 3 with `beautifulsoup4` and `Pillow` is required for the provided generator, but NOT for viewing or hosting the final site. `base_index.html` contains the original interim site scaffold. The generator creates `index.html`, the social share image, and the favicon. For an expanded catalog, add a shelf definition and any verified excerpt to `build_revision.py`; eventually it will be cleaner to move shelf metadata to `series.json`.

## Functional behavior

- 32 book cards and all available Amazon links are present in raw HTML, not created client-side.
- Every title has a `schema.org/Book` JSON-LD declaration with author, series and canonical Amazon link.
- Reader pathway cards, recent filings, format links, optional filing order and manuscript excerpt panels work without JavaScript.
- JavaScript adds book search, series/author/audience filters, random record selection, and automatically expires the “NEWLY RECOVERED” stamp after 30 days. With JavaScript disabled, all records remain browsable; time-sensitive stamps are not displayed.
- “Recently filed” is based on the latest KDP format-submission date available. It must NOT be mistaken for original publication date.
- `The Eighth File` Kindle is labeled preorder according to the supplied Nov. 2026 KDP record; confirm its current status at deployment.
- `The Unbreakable Fool` appears live in the KDP export, but the author previously indicated a pause/rewrite. Decide whether it should be publicly promoted before deployment.

## Mailing form & pending editorial decisions

1. **Filing notices**: Kit public embed is installed once in the correspondence section (UID `3011d17545`) using the supplied official script. The archive site does not store emails itself. Confirm live signup, email confirmation, imprint tags, and unsubscribe flow after staging/deployment. A working internet connection is needed for the Kit form; the local offline preview cannot verify email delivery.
2. **Next filing**: Short Shocks weekly cadence is known, but no verified next title/date was supplied. Current text clearly marks the next record unconfirmed.
3. **Analytics**: Not installed; choose a privacy-friendly provider and verify its setup before adding scripts.
4. **Connected records**: Future-ready `connectedRecords` arrays are empty. Add only verified relationships from the manuscripts or canon bible, and avoid revealing major plot connections prematurely.
5. **Cover artwork**: The CLH Armor Grimoire Edition still needs its actual cover JPG/WebP. A “COVER PENDING INTAKE” placeholder appears in its place.
6. **Descriptions**: Titles without a grounded one-line hook display “Summary awaiting intake.” Additional book blurbs can be added to `catalog.json` as they are verified.
7. **Audience badges**: Editorial mapping is Middle Grade (Short Shocks), Teen (Vault Chronicles), YA (Receipt Society), Adult (Harbor Pier, Hydrogen Tapestry, Boy in the Balloon, Ire), Picture Book (Armor). Review this for parent-facing precision.

## Testing already performed

Local Chromium DOM/interactivity tests at 320, 390 and 1280 CSS pixels report no JavaScript errors and no page-level horizontal overflow. Search returns one result for `afk kid`, and the empty result notice appears only after a zero-result query. In no-JavaScript mode, 32 book titles and 56 direct Amazon format links remain present and available in the document. A sample of small-text/background combinations was adjusted above 4.5:1 contrast; a full automated WCAG audit, keyboard screen-reader pass, and public social-card preview still need to occur before deployment.

## Files

- `index.html`: production static page
- `catalog.json`: canonical structured book records
- `assets/covers/*.webp`: optimized book fronts
- `assets/harbor-city-archive-share.jpg`: 1200x630 social card
- `assets/favicon.svg`: archive mark
- `build_revision.py`: reproducible page generator
- `base_index.html`: scaffold kept for regenerating
- `COVER_MANIFEST.csv`: image correspondence list

## Filing Notices configuration

- Official public Kit embed: `<script async data-uid="3011d17545" src="https://harbor-city-archives.kit.com/3011d17545/index.js"></script>`
- Sending identity, as configured by site owner: `Harbor City Archives <records@harborcityusa.com>`
- Editor-side checkboxes/tags: CL Vault, CL Seawall, CL Harbor, CL Ire, CL Armor.
- The newsletter form is added by `build_revision.py`, so future page regenerations retain it.
- Before sending campaigns, confirm the organization's physical mailing address in Kit, the live form's success/confirmation behavior, and privacy disclosures.
- Do not add the form a second time; the footer links to `#filing-notices`.
