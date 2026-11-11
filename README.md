# Field Kit

One web app for Xplore field techs. **Start New SA** is the main way in: Field Cam (SA-#, job type, platform, technology, photos, serial scans), then Field Notes (prefilled), then an SA summary with Complete SA. Field Cam and Field Notes can also be opened on their own for one-time use (small tiles under "Without an SA" on the menu); Field Stock is a regular tool on the menu.

See `HANDOFF.md` for the decisions already made, what's open, and the release checklist. Read it before changing anything.

| File | What it is |
|---|---|
| `index.html` | Field Kit menu, first-launch setup, settings, New SA screen, SA summary, SA history |
| `fieldcam.html` | Field Cam: stamped job photos, serial scanning |
| `fieldstock.html` | Field Stock: stock tracking synced to the tech's Google Sheet, and Manual Order Request (`#order`, its own page) |
| `fieldnotes.html` | Field Notes: FSL completion comments |
| `fieldkit.js` | Shared by every page: the tech's details and appearance copied into every tool, setup redirect, Back-button helper |
| `fieldkit-jobs.js` | The SA flow: the SA store and 7-day history, handing the SA between tools, prefilling Field Notes, equipment slots, logging scanned serials in Field Stock as deployed |
| `fieldkit-catalog.js` | Equipment catalogue: every item's SKU, plain name, product family, category, serial patterns and known serials. Shared by Field Stock and the SA flow |
| `manifest.webmanifest`, `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` | What lets phones install Field Kit as an app |
| `fieldkit.css` | The shared look: colours (light, dark, black), fonts, the header, paste-icon boxes |
| `version.js` | Field Kit's version number and last-updated time. Change it on every release |
| `sw.js` | Offline support and updates for every page |
| `icon.svg`, `favicon-32.png`, `apple-touch-icon.png` | App icon |

These files are the source. There is no build step. Field Cam, Field Stock and Field Notes are developed here, not as separate projects.

## Start New SA

1. **New SA** (`index.html#new-job`) asks for the SA-#, job type, platform (Fibre, Fixed Wireless, Satellite, VAS Only), drop (Fibre installs and conversions) and Technology (Fibre FTX/ATX/CTX, Fixed Wireless FWN/LTE, Satellite HJ3/HJ2/HTJ/HV2/HTV, VAS Only XWR/XWH/XTV). Start SA creates the SA and its Field Cam job, and Field Cam opens (`fieldcam.html#job`). The platform lists are duplicated from Field Cam's `PLATFORMS` as `NJ_PLATS` in `index.html`, and the technologies are `NJ_TECH`; change both places together.
2. Each serial scanned is logged in Field Stock as deployed on the SA's SA-# (sealed like Field Stock's own entries, so History Check stays Verified). The catalogue identifies the item; a serial that fits several differently named items, or none, asks which. Taking a serial off the SA, changing the SA-#, or an outcome other than Complete voids the entry. Google Sheets gets it the next time Field Stock is open.
3. Once every photo is saved to the phone, Field Notes opens (`#job`) with job type, platform, technology, drop, outcome and the matching picture checklist ticked, scrolled to the first question still to answer.
4. Copying the comment opens the SA summary (`index.html#job`): photos, the comment (Copy Again, Edit), equipment (Remove, Pick Item), and Complete SA.

Install, Conversion and Repair SAs have equipment slots (on repairs every slot is optional). Conversions and repairs also have a Recovered section: equipment taken back from the customer is logged in Field Stock as received from Recovery on the SA's SA-#, and Field Cam's scanner has a Deploy / Recovery switch on those SAs (installs always deploy). The slots for what each platform normally deploys are set in `slotSet()` and `slotIds()` in `fieldkit-jobs.js`: Fixed Wireless (mount, surge, radio, router, XWH, XTV), Fibre (drop for Drop Required / Drop Only, NID, ONT, router, XWH, XTV) and Satellite (trimast, AzEl, dish, modem, TRIA). Choices are picked in Field Cam's SA sheet or the summary and logged in Field Stock too; serials fill slots as they're scanned. XWH and XTV get one slot per unit Field Notes says was installed, and the mount and drop length are shared with Field Notes. Catalogue items with `FK-` ids are placeholders: replace them with real part numbers.

The tech can leave at any point; the SA stays open until Complete SA. SAs stay in SA history (bottom of the menu, closed until tapped) for 7 days and can be reopened. An SA never mixes with work done in a tool on its own: `fieldkit-jobs.js` swaps the SA's Field Cam job and Field Notes form in and out.

## Catalogue and ordering

`fieldkit-catalog.js` came from Curtis's equipment and serial workbooks. A SKU's `id` is its part number and must never change (logged entries use it); its `name` is the plain-language name techs see. Items that share a name are one item to techs. Manual orders go by **product family** (`fam` / `famName`), not SKU: some families must be ordered by model, some by family only, and some items can't be ordered (rules at the top of the order code in `fieldstock.html`, see `HANDOFF.md`).

## First launch and settings

Setup runs on the menu page before anything else: about you, accounts and shipping, then connecting Google Sheets (skippable for now). Every tool reads those details, so techs never type them again. The gear button on the menu opens Settings to change any of it. Tools opened before setup is finished send the tech back to the menu.

## Hosting

GitHub Pages, `https://xploreforms.github.io/FieldKit/`. On the same `xploreforms.github.io` domain as the old Stock Tracker, Field Cam and Field Notes sites, each tool keeps the data already saved on the phone. Google sign-in needs this site's address allowed in the Google Cloud project behind Field Stock's sign-in.

## Releasing a change

Change `version.js` (the version number and the updated time, in real Eastern time) every time you push. Phones check for a new version whenever Field Kit opens, comes back on screen, gets signal back, and every 5 minutes. They switch over on their own on the menu, right after a tool opens, or when the app goes into the background; in the middle of a tool an Update Now bar shows. When online, pages always load fresh from the site. Any new file goes in `sw.js`'s `FILES`.

## Adding a tool or link

Main tools go in the `TOOLS` list in `index.html` (currently Field Cam and Field Notes, shown under "Without an SA"); the Tools section (Field Stock, Inventory, Manual Order Request, RMA Request, Compass) is the `LINKS` list just below it.
