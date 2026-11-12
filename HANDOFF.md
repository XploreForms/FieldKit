# Field Kit — handoff note

Current as of **Field Kit 1.20.13** (Nov 10, 2026). Paste the "First message" into a new Claude chat to pick up where this left off. The rest is reference: what exists, the decisions Curtis already made (keep them), what's still open, and the traps.

---

## First message (paste this)

> I'm Curtis Gibbons, Manager, Installation Technicians at Xplore. Continue work on **Field Kit**, a mobile web app for my field techs. Code is in the GitHub repo **XploreForms/FieldKit** (branch `main`), live at **https://xploreforms.github.io/FieldKit/** (GitHub Pages). Read `CLAUDE.md` in the repo first (then `HANDOFF.md` only as needed).
>
> How I work:
> - When I ask for **options**, only show options (images/mockups) until I pick one. Don't implement early.
> - When I ask for a change, make it, test it on a phone-sized screen, **bump both lines in `version.js`** (use the real Eastern time), and **push to `main`** yourself. Then update the **Field Kit preview artifact** and tell me briefly what changed. Don't send before/after pictures or zip files; the preview artifact is how I try things.
> - My techs use phones (mostly Android/Samsung and iPhone), so everything must work and fit on a phone first.
> - I often dictate by voice, so read my messages for meaning. If something is ambiguous and a wrong guess would be costly, ask one short question; otherwise decide and tell me what you assumed.
> - Anything I ask for outside the app (charts, spreadsheets, documents) uses Xplore's brand: Poppins, Primary Green `#5CBC5D`, Secondary Green `#012929`, Promo Orange `#FFB21C` as a rare accent only, white backgrounds.

### Before the first change (new account checklist)

1. **Push access.** Reading the repo is not enough. Either install the **Claude GitHub App** on the XploreForms org (repo FieldKit), or use a fine-grained personal access token (Contents: read and write, FieldKit only, short expiry). Push with `git push https://x-access-token:<token>@github.com/XploreForms/FieldKit.git main:main` and never write the token into a file. The previous account used a token pasted into chat; Curtis should delete it at github.com/settings/personal-access-tokens.
2. **The old account's Claude artifacts do not carry over** (the Field Kit preview, the test-serials page, the old stock-names tool). Rebuild the preview with `dev/build_preview.py` (see `dev/README.md`).
3. **Check what's waiting on Curtis** in "Open items" below, especially the refined inventory list.

---

## What Field Kit is

One installable web app (PWA), no build step, hosted on GitHub Pages. The main way in is **Start New SA** (SA = service appointment, one per customer job):

**New SA** (SA-#, job type, platform, drop for Fibre, Technology) → **Field Cam** (stamped photos, scanned equipment) → **Field Notes** (FSL completion comment, prefilled from the SA) → **SA summary / home** (photos, comment, equipment, outcome, Complete SA). SAs stay in **SA history** (bottom of the menu, collapsed) for 7 days.

The home screen (1.20.27) **fills the screen with no scrolling** on any phone: header (bigger: 58px logo, Field Kit, name, dealer, **clock = SA History** on its own page `#history`, gear = Settings), the one-line "Google backup is off · Connect" banner when needed, then **Tools as 2-across tiles that share the leftover height** (Field Stock, Inventory, Manual Order, RMA, Compass, and a **Field Cam** tile = photos without an SA, same colour as the others since 1.20.36). When Field Cam has pictures in progress its tile says "In progress · N photos" and has a **New** button (two taps, same size both times; round icon in compact layouts) that starts a fresh set; the old pictures stay saved. Since 1.20.33 the layout is fitted by **`fitHome()`** (index.html): it sets the menu's height from the real visible window (`innerHeight`/`visualViewport`, not CSS vh/dvh, which come out wrong after a refresh when the phone's page zoom / text size is above 100%) and picks the biggest layout that fits with nothing cut off: stacked roomy → stacked → side-by-side roomy → side-by-side → compact 2-line → compact 1-line → no descriptions. Runs on load, resize, fonts ready, pageshow and after the menu paints. Don't go back to CSS-only height rules, and at the bottom (thumb) **Start New SA** or the SA in progress (progress chips, **Open SA**, **New** — fixed width so "Tap again" doesn't resize it). Field Notes without an SA is gone.
- SA summary's Pictures button says **Take Pictures** until every required picture is taken; **Save Pictures** only when they're all taken but some aren't saved; otherwise Open Pictures (1.20.39).
- **Start SA opens the SA summary**, not the camera (1.20.27).
- **Names inside an SA**: Field Cam is **Pictures** (was "Photos" in 1.20.27–34), Field Notes is **Comments** (headers, page titles, SA summary buttons, toasts). Field Stock keeps its name. On its own, Field Cam stays "Field Cam".


## Files

| File | What it is |
|---|---|
| `index.html` | Menu, first-launch setup (3 steps), settings, New SA screen, SA summary, SA history, the menu page's Back-button handling |
| `fieldcam.html` | Field Cam: labelled, compressed, stamped photos; serial scanning; equipment slots in SA mode; photo lists per job (`PHOTOS`, `SETUP`, `PHOTO_RULES`) |
| `fieldstock.html` | Field Stock: Log (receive, deploy, transfer, RMA, recycle), stock list, tamper-evident History, Count, Google Sheets sync, **Manual Order Request** (`#order`) |
| `fieldnotes.html` | Field Notes: FSL completion comment generator |
| `fieldkit.js` | Shared: profile/prefs into each tool, setup redirect, theme, sessions (8 h), `goHome`, SA-# keyboard close, service worker registration and updates |
| `fieldkit-jobs.js` | SA flow: SA store, hand-offs between tools, Field Notes prefill, equipment slots, deploy/recovery logging into Field Stock (sealed), model picker, `tempDrop`, `devicePhoto` |
| `fieldkit-catalog.js` | Equipment catalogue (see below) |
| `fieldkit.css` | Shared look (colours per theme, header, paste-icon boxes); the unused `fk-slim` styles are still there |
| `version.js` | **Change both lines every release.** Phones update from this |
| `sw.js` | Service worker (offline + updates). **Add any new file to `FILES`** |
| `manifest.webmanifest`, `icon-*.png`, `icon.svg`, `favicon-32.png`, `apple-touch-icon.png` | Install + icons |

**The catalogue** (`fieldkit-catalog.js`) was generated from Curtis's two workbooks (FieldKit_Equipment_Catalogue.xlsx, FieldKit_Serial_Lookup.xlsx, inventory exports 2026-11-09): each SKU has `id` (the part number, **never change one**: logged entries use it), `name` (his plain-language name, shown everywhere), `desc` (system description), `fam` / `famName` (system Product Family and its plain name), `group` (category), `serial`, `platforms` (technology codes). Also serial rules R01–R22, 494 known serials (`KNOWN`, checked first), `ORDER_EXTRA` (order-only lines). Helpers: `match(serial)`, `firstOfName()`. Items Field Kit added itself (not in his workbooks) are flagged `extra`: mounts, poles, side stays, the 1000 m drop, XTV guides, the HC210 2 W radio. The one-off generator is `dev/catalogue/gen.py`; editing the JS directly is fine.

## Release checklist

1. Make the change.
2. Test on a phone-sized screen (Playwright + Chromium against `python3 -m http.server`; see `dev/README.md`). Seed `localStorage` with `fieldkit.profile`, `fieldkit.setupDone`, and `techstock.gs` connected so setup screens don't block. Run the earlier tests for anything you touched; they have caught real breakage (once a start-up error that would have broken Field Stock).
3. Bump `version.js`: `version` and `updated`. `updated` must be the **real** time: `TZ=America/Toronto date +%Y-%m-%dT%H:%M:%S%:z`. Don't estimate. The menu footer shows it in Eastern time with EST/EDT.
4. New file? Add it to `sw.js` `FILES`.
5. Commit and push to `main`. GitHub Pages publishes in about a minute; phones update themselves.
6. Rebuild and publish the preview artifact.
7. Update this note if you changed a decision.

## Decisions already made (keep these)

### Look and layout
- One theme for all tools (light default; dark; black), changed only in Field Kit settings.
- Headers (1.20.20, Curtis picked option C; centring the title was tried in 1.20.30 and **reverted**): **one row**, pinned: the way back is **just a big arrow** `‹` (44px tap box, same size in every tool and in Field Cam's camera bar; no "Field Kit" or SA-# text since 1.20.31; inside an SA it still goes to the SA summary, and Field Cam's bar shows the SA-# next to the job instead), small 28px app tile, title at 1.2rem, nothing under the title (the SA summary keeps its job line under the SA-#). About 52px tall. Shared styles: `.fk-row`, `.fk-chev` in `fieldkit.css`. Earlier tries: full size (1.12–1.20.19), shrink-on-scroll and the no-tile slim bar (1.12.7–1.12.9). Settings uses it too (the arrow replaces the old Done button). The home menu keeps its own header; Field Cam's job screen (without an SA) uses it too (`.camhead`); its camera bar is slim by design (its back link uses the same arrow).
- Menu: Start New SA card is 96px tall and the biggest thing on it; tool tiles 72px; two lines, nothing cut off. Home header shows **name only** (no dealer); Field Stock header too.
- The in-progress SA card shows progress chips under the SA: **Photos x/y** (required photos, from Field Cam's `need`/`missing`), **Comments** (✓ when copied), **Equip. x/y** (slots filled). Green = done, orange = photos not saved or comments need updating.
- The in-progress SA card uses the **truck with work-order lines** icon. Its restart is a full-width button inside the card, under the SA: circular arrow + "Start a new SA", two taps ("Tap again to start new", resets after 4 s). Field Cam/Field Notes tiles show an "In progress" badge and a small restart button on the corner.
- No version numbers inside the tools; the version shows only on the menu footer.
- **Paste is always a clipboard icon inside the box**, no "Paste" buttons (`.fk-inwrap` + `.fk-pastein`): SA-# boxes and every serial box.

### Profile and setup
- Step 1: Your Name, Work Email (@xplore.ca), **Work Phone Number**, **Xplore Approver Email**. Only the approver email has hint text ("Approves your manual order requests and is CC'd on your transfer requests"). The approver is CC'd on every transfer email, with both techs.
- Step 2: Dealer Name (format **Location XCI Tech**, e.g. Cambridge XCI Tech), **SAP Dealer Account #** (exactly 6 digits), **Salesforce Dealer Account #** (exactly 7 digits); both boxes take digits only and stop at the limit. Shipping address, **Ship to Purolator depot hold for pickup** (checkbox, no hint), **Default Shipping Instructions** (optional, ≤300 chars, no hint). Both shipping options go into every manual order email.
- Step 3: Google Sheets backup. **"For now" it can be skipped** ("Skip for Now"); the menu then shows the "Google backup is off" banner with Connect. Curtis said "for now": plan to make it required again before final rollout. Settings has **Sync Now**.
- Name and dealer change only in Field Kit settings. Grid lines live in Field Cam's own settings.
- Every SA-# box closes the keyboard once the 7th digit is typed (`SA_BOXES` in `fieldkit.js`).
- Field Stock's header status pill (Sign in, Waiting, Not backed up, Synced…) is a button that opens Field Kit settings at the Google Sheets card (`index.html#backup`).
- The footer time is always Eastern with EST/EDT, whatever the phone's zone.

### The SA flow
- Wording: the guided flow says **SA** everywhere (Start New SA, Start SA, SA summary, Complete SA, SA history, SA START/END cards). **"Job type"** stays (it matches Field Notes/FSL). One-time-use Field Cam still says "job".
- New SA screen: SA-# (auto "SA-", 7 digits, the clipboard icon finds it in copied text), job type, platform (Fibre / Fixed Wireless / Satellite / **VAS Only**), drop (Fibre installs and conversions), **Technology** (required for every platform): Fibre FTX / ATX / CTX; Fixed Wireless FWN / LTE; Satellite HJ3 / HJ2 / HTJ / HV2 / HTV; VAS Only XWR / XWH / XTV. Outcome starts as Complete, with no note about it on this screen. Until a platform is picked, a greyed **Technology** placeholder shows ("Pick a platform first"). Drop appears only once Install/Conversion and Fibre are picked (no placeholder).
- Technology is saved as `tech` and shown after the platform ("Install · Fixed Wireless · LTE", `withTech`). It carries into Field Notes: a Technology row in the Job section (also in the comment's title line), the Fixed Wireless Platform question (FWN/LTE, kept in step with Technology), and a VAS repair's Equipment Serviced tick. Field Notes still saves VAS Only internally as "Value Added Services" (`PLAT_SHOW`).
- Tapping the unfinished SA on the menu always opens its **SA home (summary)**, never the tool it was last in.
- In an SA, Field Cam has no "New job"/"Start next job"; saving all photos goes straight to Field Notes. The back link in Field Cam and Field Notes is the arrow only (goes to the SA summary); Field Cam's job pill shows the SA-# (1.20.31).
- Copying comments in Field Notes goes to the SA summary. The outcome can be changed in Field Cam (chip on the picture ▾) or the summary; Field Notes follows and copied comments get "Needs update". Complete SA asks for a second tap if photos aren't saved, comments aren't copied, or required slots are empty.
- **Back button** (Android):
  - On the menu page (`index.html`, bottom of its script): from the SA page, New SA, Settings or setup, Back always goes to the home screen. On the home screen the first Back toasts "Press back again to close Field Kit" and the next closes the app. Uses a spare history entry (armed on the first tap) plus the Navigation API (`navigation.traverseTo` the first entry of the visit); without that API it just shows the menu.
  - In Field Cam and Field Notes: Back (and the back link) goes to the menu, or the SA summary in an SA (`FieldKit.goHome`). Field Cam closes an open panel/scanner first. Tools hand over with `location.replace`, and `goHome` only does a real history Back when `document.referrer` is the menu, so copying comments always lands on the SA page even if the phone kept Field Cam in history.
- **Scan from the SA page** opens Field Cam straight into the scanner (`fieldkit.scanReturn` in sessionStorage). A slot's Scan returns to the SA page after one serial; **Scan More** returns when the tech taps Done; cancelling returns too. If the scanner can't start, Field Cam stays open.
- The SA START card shows the time the SA was started (`started`); the END card is just after the last photo.
- Field Notes in an SA: scrolls past the already-answered questions to the first one still to answer (`skipAnswered`, once on arrival, not if the tech already scrolled or tapped); and answering the last required question glides down to the finished comment (`finishedCheck`; after a typed answer it waits for the keyboard to close).

### Equipment slots (`slotSet()` / `slotIds()` in `fieldkit-jobs.js`)
- Install and Conversion: Fixed Wireless = Mount, Surge (always Deployed), Radio, Router, XWH, XTV. Fibre Existing Drop = NID, ONT, Router, XWH, XTV. Fibre Drop Required/Only = Drop, NID, ONT, Router, XWH, XTV. Satellite = Trimast, AzEl, Dish, Modem, TRIA (the SurfBeam parts: see Open items).
- Repair: same slots by platform, **all optional** (Fibre repair gets every fibre slot).
- Choices read **Deployed / Not Needed** (Trimast/AzEl/Dish also "Reused existing").
- **Mount**: J-Arm, Gable Mount, Bipod, Tripod. Gable Mount and Tripod show a **"Deployed 10ft pole"** tick (on by default). **"New mount not required"** (tick on the right of the Mount heading) opts out (reused existing, or on a tower; nothing logged). Bipod still logs its 5ft pole. Once answered, Mount folds to one line like Surge; tapping it reopens the choices until the answer changes. Side stays aren't tracked. Old saved answers are mapped (`MOUNT_OLD`).
- **Field Notes' fixed wireless Mount Type matches**: J-Arm, Gable Mount, Bipod, Tripod, Tower, Other, with ticks for Side stays (J-Arm), 10ft pole (Gable Mount/Tripod, ticked when picked) and Reused existing mount. The comment reads e.g. "Mount: New tripod + 10ft pole". It fills the slot: type (+ pole tick); Tower or Reused existing mount → No new mount. A hand-picked slot sticks until the Notes answer changes. Drop length is shared the same way.
- XWH/XTV slots appear only once Field Notes says how many were installed, or one is scanned/typed (one slot per unit).
- Serials: scan, type, or paste; **Add** puts a typed serial in (Done or tapping away also does); a serial typed into a slot narrows the model; the picker asks only when ambiguous. Items sharing a plain name never ask.
- Cannot Complete / Not Required: **no equipment deployed** (entries voided; serials kept in case it changes back).
- Conversions and repairs have a **Recovered** section; Field Cam's scanner has a Deploy / Recovery switch (installs always deploy). Recovered items log as Receive → Recovery on the SA's SA-#.
- Everything logged is sealed like Field Stock's own entries, so **History Check stays Verified**. Don't write to Field Stock's events any other way.
- SA home: no "Also logged in Field Stock…" line under equipment and no "You can leave any time…" line above Complete SA.

### Field Cam: photos and scanning
- (1.20.39) **No pop-up after each picture**; only the too blurry / too dark warning (with Retake) still shows.
- (1.20.39) **"To label (n)" is the first tile in the label grid** (orange), not a row of its own.
- (1.20.39) **Gallery shows only the current job/SA** (no Previous jobs). Unsaved pictures from an earlier set stay on the phone until auto-clean, but aren't listed.
- (1.20.39) **No sideways/landscape mode** outside full screen: turning the phone doesn't reshape the frame (`frameTurn` is 0 unless `fc-fs`); saved pictures are still turned upright.
- (1.20.39) Without an SA: **no start/end cards**, and once every picture is saved a sheet offers **Finish & Go Home** (ends the set, back to the menu) or Keep shooting.
- (1.20.40) SA start/end divider cards say **"Divider · Do Not Upload"**.
- (1.20.39) Barcode scanner: **no white box**; a dark vignette fading to a clear middle; the red line turns green/orange on hit/miss.
- (1.20.35) **Labels sit at the bottom**, right above the shutter (deck `justify-content:flex-end`).
- Field Cam settings no longer have a Text size option (1.20.38; always normal).
- Viewfinder buttons, top to bottom: **HQ, Flash, Scanner, Full screen** (1.20.36).
- (1.20.35) **Full screen** button (corners icon): hides the bar and labels, asks for fullscreen + landscape lock (Android), the picture fills the screen (480×360 vs 360×270 on a 360px phone); its own shutter and ✕ on the right; **one picture, then back to normal** (`enterFs`/`exitFs`, class `fc-fs`; `applyRot` doesn't counter-rotate while full screen). iPhone can't lock landscape: it says "Turn your phone sideways" and the sideways logic gives a tall 3:4 frame.
- (1.20.35) **Imported screenshots** (PNG, or "Screenshot" in the file name) are labelled **Screenshot** automatically unless a label was picked first, in an SA and without one.
- (1.20.26, 1.20.29) **Field Cam without an SA = "quick" photos** (`job.quick`, `isQuick`): titled **Field Cam** in the top bar; **no SA-#** asked; it opens straight into the camera (iPhone shows one Open Camera tap first, needed for motion access); **no New Job** button and no "next job" sheet after saving (one running set of photos); no job type, platform or outcome; no required photos; photos are never "to label" (they save as "Photo"), but a label can still be added (Other…, Label/Change). The stamp has no Job row. **Field Notes without an SA is gone** from the menu (Curtis's call).
- (1.20.23) The **outcome** is a dark chip on the picture, top-left under the SA-# (`.vf>.outbtn`), not its own row; tapping it opens the outcome sheet. The **GPS dot is hidden** from the top bar (location problems still show as a message). The row under the picture only shows when it has To label / New Job. Toasts (HQ on/off, scans) show just under the top bar.
- (1.20.24) The **viewfinder never crops**: it shows exactly the 4:3 photo area (contain, `measureVf`), anchored to the **top** right under the bar, and since 1.20.34 **no black band**: `measureVf` sizes the viewfinder to the picture's height (smaller only if the labels + shutter need the room) and the deck (labels, then the shutter at the bottom) takes the rest. Zoom buttons sit on the picture, 10px above its bottom edge. Field Cam's top bar is 56px with the back arrow at the same spot as the other tools; without an SA it shows the camera tile + "Field Cam" title like the other tools' headers. It used to fill up to a square and crop the sides.
- Required photos per job come from `PHOTOS` (generated originally from Curtis's Outcomes and Photo Lists tools; hand-edited since).
- **Serial number photos** (Install and Conversion, Complete): Fibre adds ONT SN, XWR SN, XWH SN (optional), XTV SN (optional); Fixed Wireless adds CPE SN, XWR SN, XWH SN (opt), XTV SN (opt); Satellite adds Modem SN, TRIA SN, XWR SN, XWH SN (opt). Each is always its own photo (`SN_LABELS`) and tapping one opens the barcode scanner. VAS installs need one photo named after the Technology (XWR SN, XWH SN or XTV SN). The optional "VAS" label is gone from installs and conversions (repairs keep it). The older "ONT Placement" / "Router Placement" / "Modem Placement" / "PoE Placement" labels still exist beside the SN ones.
- **A scan labels its own photo** as the device photo the SA needs (`devicePhoto`, by the item's catalogue family: any CPE → CPE SN, router → XWR SN, ONT → ONT SN, modem → Modem SN, TRIA → TRIA SN, XWH → XWH SN, XTV → XTV SN), so it ticks that photo. If the SA's list doesn't have it, or it's a Recovery scan, the label stays "<item> SN". Old photos labelled ONT/XWR/XWH/XTV or "Device SN" are moved onto the SN tiles on load (`fixSnPhotos`; they're marked unsaved because the stamp changed).
- **Temp drops:** a temp drop is used when the job is *completed* but the drop couldn't be buried, so it is **not** a Cannot Complete reason in Field Cam. In Field Notes' Drop Route, a buried span's tick is **Temp Drop Deployed** (comment: "Buried (Temp Drop Deployed)"). Ticking it adds **Temp drop form** to Field Notes' required pictures and a required **Temp Drop Form** photo to the Fibre SA's Field Cam list (`FieldKit.job.tempDrop()`; `photosOf` adds the tile; solo photo).
- `PHOTO_RULES`: Fixed Wireless: Install Overview, Line of Sight, CPE & Mount, Indoor Cable Run each their own photo. Satellite: Install Overview, Line of Sight, Dish & Mount, Indoor Cable Run each their own. Fibre Existing Drop: Indoor Cable Run alone; ONT Placement + Router Placement only with each other. Fibre Drop Required: MPT, Install Overview, Drop Route, Indoor Cable Run alone; ONT + Router only with each other.
- Messages about the label just picked ("… is always its own photo") show at the **top of the viewfinder** (`vfHint`). The **Other…** typing box (`#otherBar`) is moved to the top of the page when opened so it shows above the photo sorter and sheets.
- Scanning: no instruction panel or Done button; results and problems show as a short toast; leave with the scan button or Back. The photo button and Save button never move when scan mode starts (the Deploy/Recovery switch is `div.scanmode`, scoped on purpose).
- Saving photos says "Compressing N photos…" then "Compressing and saving 3 of N…".

### Field Notes look and Recovery
- Field Notes matches New SA: choices sit in one joined group (white box, thin outline, picked = Superior Green), question labels small and grey, section titles uppercase like the menu's TOOLS, no subtitle under the title.
- Job type includes **Recovery** (all platforms): Equipment Recovered (ticks per platform), Recovered Equipment (RMA / recycled / Other), Cable Entry Hole (Fixed Wireless and Satellite), comments, lawn sign. A Recovery SA prefills it (`NOTE_TYPE.REC`).

### Field Stock
- No hint box above the item list on Receive, Deploy or Recycle (Transfer and RMA still have one).
- No version line in Field Stock (versions only on the menu footer).
- History hides voided entries; they're only under the last filter chip, **Voided** (still kept and sealed for History Check).
- Always opens on the **Log** tab (renamed from "Logs"); the last tab isn't restored. Manual Order Request opens as its **own page** (`fieldstock.html#order` adds `html.order-only`, hiding Field Stock's tab bar, status pill and sync banner).
- Names and categories come from the catalogue. Items sharing a plain name are one item to techs: one row in the stock list (counts added), one entry in pickers (the three Nokia XS-010X ONTs; the TRIA - 1 Watt radios). Known serials identify the exact model first, then the patterns.
- **Deploy can pick any item by hand**, serialized too: the serial is tapped from this phone's stock or typed, and must match the item. Receive/Transfer/RMA/Recycle still list only items without serials by hand.
- **Manual orders go by product family**, not SKU. `ORDER_PICK` families (Router, 5G High Gain CPE, ONT, Drop cable, TV box, Aerial kit, AzEl, Trimast, Dish): no "any model", the tech must choose a model. `ORDER_FAMILY_ONLY` (5G CPE, LTE CPE – CAT12 2.5 / 3.5 GHz): by family, no model choice. `ORDER_HIDE`: CAT4. Items whose system description starts "NLA" (e.g. the Zyxel EMG6726 router) are left off. Other families have one item and order as it. Order-only lines (`ORDER_EXTRA`): Adtran 411 ONT, Nova remote, two aerial kits. The email shows the family, system codes, and the chosen model.
- Max per order line is 20 (10 for J-Arm and High Gain).
- Drop names stay long ("Drop - 300m - Evolv Dielectric Drop PushLok Tech") because more drop types are coming.

### Compass link
On Android the menu's Compass link is an `intent://` "view this address" link (`appHref` in `index.html`) so the installed Compass web app takes it, otherwise the phone's browser opens it; never Field Kit's in-app browser tab. iPhone can't hand a link to a home-screen web app, so it opens as before. Inventory and RMA Request open as normal links.

## Open items

**Waiting on Curtis**
- **The refined inventory list.** He has `FieldKit_Inventory_List.xlsx` (59 items; he edits Plain name, Category, Notes). When he returns it and says "apply the inventory list": update `name` / `group` (and `GROUPS` order) in `fieldkit-catalog.js` from the sheet, never change an `id`, add new rows as new items, test Field Stock + an SA + the order form, bump, push.
- **Real part numbers** for the placeholders (ids starting `FK-`): Bi-pod Mount, Gable Mount, Tripod Mount, 10ft Pole, 5ft Pole, Side Stays, Satellite Pole Mount, 1000M drop. Changing an id later orphans old entries.

**Not done yet (he asked to wait)**
- Filtering SA equipment and pickers by the SA's Technology using the workbook's platform codes. Several codes are unconfirmed (CAB, CCW, CTX, XHP, XWR); the Zyxel EMG6726 has none. Satellite SA slots still use the Viasat (SurfBeam) parts even on Hughes technologies, which this filtering would fix.
- HV2 modem and transceiver are off the order form for now.

**Clean-up and reminders**
- **Google Sheets backup is skippable "for now"** (see Profile and setup). Make it required again at final rollout.

**To confirm with Curtis**
- The Zyxel router (NLA) is off the order form; ok?
- Field Notes' Cannot Complete reason list still has "Temp Drop Required" (from the Cannot Complete JotForm). Should it go?
- The old "ONT Placement" / "Router Placement" / "Modem Placement" / "PoE Placement" photo labels still sit beside the new SN ones. Replace them?
- CPE SN / Modem SN / TRIA SN naming (he only named ONT, XWR, XWH, XTV).
- Fibre Drop Only photo rules (MPT, Drop Route); whether Install Overview should be alone on Fibre Existing Drop; whether the SA summary header should use the truck icon.
- Should Receive/Transfer also pick serialized items by hand?

**Things only a real phone can confirm** (the test browser has no camera or GPS)
- Compass on Android (with and without the Compass web app installed; if Android shows an "open with" chooser instead of going straight in, adjust).
- A real scan from the SA page returning correctly, and a real photo ticking its SN tile.
- The Back-button behaviors on a Samsung (the warning needs one tap on the screen first; iPhones have no Back button).
- The smooth/instant behaviors on an iPhone.

**Minor**
- Field Cam still shows its own generic "Install" tip in settings (harmless).

## Gotchas

- Install/manifest/icon tags must stay in `<head>` (Android refused to install when they were in `<body>`).
- Pushing needs the Claude GitHub App on the XploreForms org or a token; connecting GitHub alone only gives read access.
- `localStorage` keys are shared across tools on the same origin (`fieldkit.*`, `techstock.*`, `fieldcam.*`, `xplore_fsl_*`). Don't rename keys without migrating. Short-lived `sessionStorage` keys: `fieldkit.cameFrom`, `fieldkit.scanReturn`, `fieldkit.backTo`.
- Don't change a catalogue `id`; don't write Field Stock entries without sealing them (History Check).
- A script that uses a `const` before its declaration breaks the whole page silently (it happened with the order form's cleanup). Always load every page in a test after editing and print page errors.
- Google sign-in can't run inside the Claude artifact preview; test Sheets on the real site. The preview wrapper (`dev/build_preview.py`) stubs `window.claude` so setup shows "Website only", routes links between pages through the shell (`__fkNav`), and tolerates browsers that refuse history changes in a frame.
- Field Stock's data lives on each phone (plus the tech's own Google Sheet). Nothing you do from here can read or change a tech's stock.
- Curtis's voice-dictated messages can have transcription oddities ("gable mount and bipod and tripod").
