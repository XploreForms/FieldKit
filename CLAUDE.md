# Field Kit — working notes for Claude

Read this file first. It's kept short on purpose. `HANDOFF.md` holds the full list of decisions; read it only when a change touches one of those decisions.

## Curtis's preferences
- When he asks for **options**: show options only (mockups or screenshots) and build nothing until he picks one.
- When he asks for a **change**: make it, test it, release it with `dev/release.sh`, and republish the preview artifact. Then tell him in a line or two what changed.
- Don't send before/after screenshots unless he asks; the preview artifact is how he tries changes.
- Design for phones first.
- His messages are often voice-dictated, so read past transcription slips.

## Save time and usage (do this every time)
- **Don't read whole pages.** They run to 3,000+ lines. Run `grep -n "/\* [=-]\{3,\}" <file>` to list a file's sections, then read only the section you need using offset/limit. To find a specific function, grep for it.
- **Release in one step:** `dev/release.sh "what changed" "Co-Authored-By: …"`. The script:
  - bumps `version.js` (patch number and time)
  - loads all four pages and refuses to push if any page throws an error
  - commits and pushes to `main`
  - builds `/tmp/fk-shots/fieldkit-preview.html`

  After it finishes, publish that preview file to the Field Kit preview artifact.
- **Test narrowly:** run `dev/run.sh dev/check.py` for page errors, and only the one or two `dev/tests/*.py` near the change. `dev/README.md` lists them by area. Old tests may need their selectors updated.
- **Screenshots:** only for your own checking (360×780), and only when the change is visual. Don't send them unless he asks.
- **Batch:** when Curtis sends several small changes, ship them as a single release.

## Map (section headers to grep for)
| File | Main sections |
|---|---|
| `index.html` | menu content (TOOLS, LINKS) · jobs (New SA `NJ_*`, job summary, outcome) · details checks · Google Sheets · first-launch setup · settings · Back button |
| `fieldcam.html` | JOBS · camera, zoom, orientation, location · stamp · image pipeline · capture · file names/downloads · serial number scanning · job picker · top bar/chips (`PHOTO_RULES`, labels) · sheets |
| `fieldnotes.html` | theme CSS · helpers/state · field pieces · fibre / fixed wireless & satellite / VAS / repair questions · cannot complete · not required · the form · validation · output (the comment text) |
| `fieldstock.html` | catalogue · storage · tamper-evident history (`seal*`) · stock view · log form · save an entry · transfer email · manual order request · history and History Check · details · Excel backup · quarterly count · Google Sheets sync |
| `fieldkit-jobs.js` | job store · Cam/Notes swap · equipment slots (`slotSet`, `slotIds`) · Notes prefill · back link · identify serial and log to Field Stock (sealed) |
| `fieldkit.js` | profile and prefs sync · theme · sessions · updates · SA-# boxes · back link |
| `fieldkit-catalog.js` | `FK_CATALOG` (never change an `id`) |
| `fieldkit.css` | shared look and per-theme tokens |

## Rules that break things if missed
- Every release bumps `version.js` (the script does this). A new app file also has to be added to `FILES` in `sw.js`.
- Install, manifest and icon tags stay in `<head>`.
- Never rename `localStorage` keys (`fieldkit.*`, `techstock.*`, `fieldcam.*`, `xplore_fsl_*`), and never write Field Stock entries without sealing them.
- Using a `const` before its declaration silently kills the whole page, so always run `dev/check.py`.
- `dev/` is tooling only. Nothing in the app loads it, and the service worker doesn't cache it.
