# Field Kit

One web app for Xplore field techs: start a job, take stamped photos, scan serials that are logged in stock as deployed on the job's SA-#, and generate FSL completion comments.

## Files

| File | What it is |
|---|---|
| `index.html` | Home: profile (name + dealer), current job card, New Job, Inventory |
| `camera.html` | Field Cam, with Field Kit hooks |
| `stock.html` | Stock Tracker, with Field Kit hooks |
| `comments.html` | FSL Comments Generator, with Field Kit hooks |
| `toolkit.js` | Shared bridge: profile sync, current job, serial → stock deployments, per-job comment drafts |
| `sw.js` | Offline support for all pages |
| `build.py` | Rebuilds the three tool pages from new standalone versions |

## Hosting

GitHub Pages, e.g. `https://xploreforms.github.io/FieldKit/`. Hosting on the same `xploreforms.github.io` domain as the current Stock Tracker means the phone's existing stock history is already there when a tech opens Field Kit.

## Updating a tool

Keep developing Field Cam, Stock Tracker and the Comments Generator on their own. When one changes, run:

```
python3 build.py path/to/fieldcam.html path/to/stocktracker.html path/to/fslcomments.html
```

That rewrites `camera.html`, `stock.html` and `comments.html` with the Field Kit hooks applied. If a hook can't find its spot in the new version, the script stops and names it. Bump `CACHE` in `sw.js` after any change so phones pick up the new files.
