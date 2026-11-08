# Field Kit

One web app for Xplore field techs. **Start New Job** is the main way in: Field Cam (SA-#, job type, platform, photos, serial scans), then Field Notes (prefilled), then a job summary with Complete Job. The tools can also be opened on their own for one-time use.

| File | What it is |
|---|---|
| `index.html` | Field Kit menu |
| `fieldcam.html` | Field Cam: stamped job photos |
| `fieldstock.html` | Field Stock: stock tracking, synced to the tech's Google Sheet |
| `fieldnotes.html` | Field Notes: FSL completion comments |
| `fieldkit.js` | Shared by every page: the tech's details and appearance, copied into every tool; sends unfinished setups to the menu |
| `fieldkit-jobs.js` | Start New Job: the job store and 7-day job history, handing the job between the tools, prefilling Field Notes, and logging scanned serials in Field Stock as deployed |
| `fieldkit-catalog.js` | Equipment list and serial patterns, shared by Field Stock and jobs |
| `fieldkit.css` | The Field Kit look: colours (light, dark, black), fonts and the shared header. Each tool maps its own colour names to these in a `fk-look` style block |
| `version.js` | Field Kit's version number and last-updated time. Change it on every release |
| `sw.js` | Offline support and updates for every page |
| `icon.svg`, `favicon-32.png`, `apple-touch-icon.png` | App icon |

These files are the source. Field Cam, Field Stock and Field Notes are developed here now, not as separate projects.

## Start New Job

1. Start New Job asks for the SA-#, job type, platform, drop (Fibre) and VAS service on the menu page (`index.html#new-job`). Start Job creates the job and its Field Cam job, and Field Cam opens straight into the camera (`fieldcam.html#job`). Those lists are duplicated from Field Cam's `PLATFORMS` as `NJ_PLATS` in `index.html`; change both together.
2. Each serial scanned is logged in Field Stock as deployed on the job's SA-# (sealed like Field Stock's own entries, so History Check stays Verified). A serial that fits several items, or none, asks which item it is. Taking a serial off the job, changing the SA-# or an outcome other than Complete voids the entry. Google Sheets gets it the next time Field Stock is open.
3. Once every photo is saved to the phone, Field Notes opens (`#job`) with job type, platform, drop, outcome and the matching picture checklist ticked.
4. Copying the comment opens the job summary (`index.html#job`): photos, the comment (Copy Again, Edit), equipment (Remove, Pick Item), and Complete Job.

Install and Conversion jobs have equipment slots for what that platform normally deploys (set in `slotSet()` and `slotIds()` in `fieldkit-jobs.js`): Fixed Wireless (mount, surge, radio, router, XWH, XTV), Fibre (drop for Drop Required / Drop Only, NID, ONT, router, XWH, XTV) and Satellite (trimast, AzEl, dish, modem, TRIA). Choices are picked in Field Cam's job sheet or the summary and logged in Field Stock too; serials fill slots as they're scanned. XWH and XTV get one slot per unit Field Notes says was installed, and the drop length is shared with Field Notes. Catalogue items with `FK-` ids are placeholders: replace them with real part numbers.

The tech can leave at any point; the job stays open until Complete Job. Jobs stay in Job history (at the bottom of the menu, closed until tapped) for 7 days and can be reopened. A job never mixes with work done in a tool on its own: `fieldkit-jobs.js` swaps the job's Field Cam job and Field Notes form in and out.

## First launch and settings

Setup runs on the menu page before anything else: about you, accounts and shipping, appearance, then connecting Google Sheets. Every tool reads those details, so techs never type them again. The gear button on the menu opens Settings to change any of it. Tools opened before setup is finished send the tech back to the menu.

## Hosting

GitHub Pages, e.g. `https://xploreforms.github.io/FieldKit/`. On the same `xploreforms.github.io` domain as the old Stock Tracker, Field Cam and Field Notes sites, each tool keeps the data already saved on the phone. Google sign-in needs this site's address allowed in the Google Cloud project behind Field Stock's sign-in.

## Releasing a change

Change `version.js` (the version number and the updated time) every time you push. Phones check for a new version whenever Field Kit opens, comes back on screen, gets signal back, and every 5 minutes. They switch over on their own on the menu, right after a tool opens, or when the app goes into the background; in the middle of a tool an Update Now bar shows. When online, pages always load fresh from the site.

## Adding a tool or link

Main tools go in the `TOOLS` list in `index.html`; smaller links (Compass, Inventory, Manual Order Request, RMA Request) go in `LINKS` just below it.
