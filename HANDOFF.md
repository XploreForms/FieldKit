# Field Kit — handoff note

Paste the "First message" section into a new Claude chat to pick up where this left off. The rest is reference.

---

## First message (paste this)

> I'm Curtis Gibbons, Manager, Installation Technicians at Xplore. Continue work on **Field Kit**, a mobile web app for my field techs. Code is in the GitHub repo **XploreForms/FieldKit** (branch `main`), live at **https://xploreforms.github.io/FieldKit/** (GitHub Pages). Read `README.md` and `HANDOFF.md` in the repo first.
>
> How I work:
> - When I ask for **options**, only show options (images/mockups) until I pick one. Don't implement early.
> - When I ask for a change, make it, test it, **bump both lines in `version.js`**, and **push to `main`** yourself. Then tell me briefly what changed.
> - For anything visual, show me before/after or a screenshot.
> - My techs use phones (mostly Android/Samsung and iPhone), so everything must work and fit on a phone first.

---

## What Field Kit is

One installable web app (PWA) with three tools and a guided job flow:

- **Start New Job** (main way in): New Job screen on the menu (SA-#, job type, platform, drop, VAS service) → **Field Cam** (photos + scanned equipment) → **Field Notes** (FSL completion comments, prefilled) → **Job summary** (photos, comments, equipment, outcome, Complete Job). Jobs stay in **Job history** (bottom of menu, collapsed) for 7 days.
- **Tools – one time use**: Field Cam, Field Stock, Field Notes on their own. A job never mixes with one-time-use work.
- **More**: Compass, Inventory (Dealer Portal), Manual Order Request (`fieldstock.html#order`), RMA Request.
- **Settings** (gear): profile, shipping options, theme, Google Sheets backup.

## Files

| File | What it is |
|---|---|
| `index.html` | Menu, first-launch setup (3 steps), settings, New Job screen, job summary, job history |
| `fieldcam.html` | Field Cam (labelled, compressed, stamped photos; serial scanning; equipment slots in job mode) |
| `fieldstock.html` | Field Stock (receive, deploy, transfer, RMA, recycle, return; tamper-evident history; Google Sheets sync; manual order) |
| `fieldnotes.html` | Field Notes (FSL completion comment generator) |
| `fieldkit.js` | Shared: profile/prefs sync into each tool, setup redirect, theme, sessions (8 h), slim header on scroll, service worker + aggressive updates |
| `fieldkit-jobs.js` | Job flow: job store, hand-offs between tools, Field Notes prefill, equipment slots, deploy/recovery logging into Field Stock (sealed), model picker |
| `fieldkit-catalog.js` | Equipment catalogue (SKUs, groups, serial patterns) shared by Field Stock and jobs |
| `fieldkit.css` | Shared look (Barlow fonts, colours, header, tokens per theme) |
| `version.js` | **Change both lines every release** (`version`, `updated`) — phones update from this |
| `sw.js` | Service worker (offline + updates). Add any new file to `FILES`. |
| `manifest.webmanifest`, `icon-*.png`, `icon.svg`, `favicon-32.png`, `apple-touch-icon.png` | Install + icons |

No build step. Edit files, bump `version.js`, push.

## Release checklist

1. Make the change.
2. Test in a phone-sized browser (Playwright on `python3 -m http.server`; seed `localStorage` with `fieldkit.profile`, `fieldkit.setupDone`, and `techstock.gs` connected so setup screens don't block).
3. Bump `version.js` (both lines).
4. New file? Add it to `sw.js` `FILES`.
5. Push to `main`. GitHub Pages publishes in ~1 minute; phones update themselves.

## Decisions already made (keep these)

**Look & layout**
- One theme for all tools (light default; dark; black). Changed only in Field Kit settings.
- Headers: page-colour, no green bar or Xplore logo, 560px column on desktop. Headers are pinned and **always full size** (app tile, title, line under it); they don't go slim on scroll (tried shrink-on-scroll and always-slim in 1.12.7–1.12.9, Curtis chose full size). The fk-slim styles remain in the CSS, unused. Field Cam's bar is slim by design.
- Menu cards are a uniform 72px, two lines, nothing cut off. Home header shows **name only** (no dealer). Field Stock header also name only.
- In-progress job card uses the **truck with work-order lines** icon; restart button is the circular arrow with a two-tap "Tap to start new".
- No version numbers inside the tools; version only shows on the menu footer.

**Profile / setup**
- Step 1: Your Name, Work Email (@xplore.ca), Work Phone Number, **Xplore Approver Email**. Only the approver email has hint text: "Approves your manual order requests and is CC'd on your transfer requests." The approver is CC'd on every transfer email (with both techs).
- Step 2: Dealer Name (format **Location XCI Tech**, e.g. Cambridge XCI Tech), **SAP Dealer Account #** (exactly 6 digits), **Salesforce Dealer Account #** (exactly 7 digits; both boxes take digits only and stop at the limit), shipping address, **Ship to Purolator depot hold for pickup** (checkbox, no hint text), **Default Shipping Instructions** (optional, ≤300 chars, no hint text). Both shipping options go into every manual order email.
- Step 3: Google Sheets backup (required). Settings has **Sync Now** (signs in if needed, Field Stock syncs, returns to settings).
- **Paste is always a clipboard icon inside the box** (no "Paste" buttons): `.fk-inwrap` + `.fk-pastein` in `fieldkit.css`; used for the SA-# on New SA and in Field Cam, Field Stock's SA boxes, and every serial box in an SA.
- Name and dealer can only be changed in Field Kit settings (not in Field Cam). **Grid lines** live in Field Cam's own settings.

**Job flow**
- New SA screen collects SA-# (auto "SA-", 7 digits only, Paste finds it in copied text), job type, platform, drop (Fibre installs/conversions), VAS service. Outcome starts as Complete (no note about it on the New SA screen).
- **Wording: the guided flow calls a job an "SA" (service appointment)**: Start New SA, New SA, Start SA, SA summary, Complete SA, SA history, SA start/end cards. "Job type" stays (it matches Field Notes / FSL). One-time-use Field Cam still says "job" in its own screens.
- Tapping the unfinished SA on the menu always opens its **SA home (summary)**, never the tool it was last in.
- Field Cam's **SA START card** shows the time the SA was started (`started` on the Field Cam job); the END card is just after the last photo.
- In a job, the way back in Field Cam and Field Notes reads **‹ SA-#######** (the job's SA number), and Field Cam's job pill drops its own SA-# so it isn't shown twice.
- In a job, Field Cam has no "New Job"/"Start Next Job"; saving all photos goes straight to Field Notes.
- **Back** (phone Back button, or "‹ Field Kit" / "‹ SA-#######") in Field Cam and Field Notes goes straight to the menu, or the job summary in a job (`FieldKit.goHome` in `fieldkit.js`). Field Cam closes an open panel/scanner first. Tools hand over to each other with `location.replace` (including links between them, e.g. Field Cam's "Go to Field Notes"), and the menu records `fieldkit.cameFrom` (sessionStorage) when it opens a tool, so going home is a real history Back.
- Copying comments in Field Notes goes to the job summary. Outcome can be changed in Field Cam (chip ▾) or the summary; Field Notes follows and copied comments get "Needs update".
- Complete Job asks for a second tap if photos aren't saved, comments aren't copied, or required slots are empty.

**Equipment slots** (`slotSet()` / `slotIds()` in `fieldkit-jobs.js`)
- Install & Conversion: Fixed Wireless = Mount, Surge (always Deployed), Radio, Router, XWH, XTV. Fibre Existing Drop = NID, ONT, Router, XWH, XTV. Fibre Drop Required/Only = Drop, NID, ONT, Router, XWH, XTV. Satellite (SurfBeam) = Trimast, AzEl, Dish, Modem, TRIA.
- Repair: same slots by platform, **all optional** (Fibre repair gets every fibre slot).
- Choices read **Deployed / Not Needed** (Trimast/AzEl/Dish also "Reused existing"). **Mount** (stock tracking): J-Arm, Gable Mount, Bipod, Tripod. Gable Mount and Tripod show a **"Deployed 10ft pole"** tick (on by default). A **"New mount not required"** tick on the right of the Mount heading opts out (reused existing, or on a tower; nothing logged). Bipod still logs its 5ft pole. Once answered, Mount folds to one line like Surge ("✓ Mount … Tripod + 10ft pole ▾"); tapping it opens the choices again until the answer changes. **Field Notes' fixed wireless Mount Type matches**: J-Arm, Gable Mount, Bipod, Tripod, Tower, Other, with ticks for **Side stays** (J-Arm), **10ft pole** (Gable Mount, Tripod; ticked when picked) and Reused existing mount. Comment reads e.g. "Mount: New tripod + 10ft pole", "Mount: New j-arm with side stays". It fills the slot: type (+ pole tick), Tower or Reused existing mount → No new mount. Old combined answers are mapped. Side stays aren't tracked. Old saved answers are mapped (`MOUNT_OLD`).
- Field Notes' Mount Type (and its Reused existing mount tick) and drop length fill the slots (a hand-picked slot sticks until the Notes answer changes). XWH/XTV get one slot per unit Field Notes says (none until then, unless scanned).
- Serials: scan, type, or paste (clipboard icon **inside** the S/N box); **Add** puts a typed serial in (so does Done / tapping away); typed into a slot narrows the model; picker asks when ambiguous.
- **XWH / XTV slots only appear** once Field Notes says how many were installed, or one is scanned/typed. No empty "If installed" slot.
- SA home: no "Also logged in Field Stock: …" line under equipment, and no "You can leave any time…" line above Complete SA.
- Cannot Complete / Not Required: **no equipment deployed** (entries voided; serials kept in case it changes back).
- Conversions & repairs have a **Recovered** section; Field Cam's scanner has a **Deploy / Recovery** switch (installs always deploy). Recovered items log as Receive → Recovery on the job's SA-#.
- Everything logged is sealed like Field Stock's own entries so **History Check stays Verified**.

**Field Cam photo rules** (`PHOTO_RULES` in `fieldcam.html`)
- Fixed Wireless: Install Overview, Line of Sight, CPE & Mount, Indoor Cable Run are each their own photo.
- Satellite: Install Overview, Line of Sight, Dish & Mount, Indoor Cable Run are each their own photo.
- Fibre Existing Drop: Indoor Cable Run alone; ONT Placement + Router Placement only with each other.
- Fibre Drop Required: MPT, Install Overview, Drop Route, Indoor Cable Run alone; ONT + Router only with each other.

**Field Notes**
- Focus ring stays inside boxes. Keyboard closes after 3 RSRP digits / 2 SINR digits.

## Open items / to do

- **Placeholder part numbers** in `fieldkit-catalog.js` (ids starting `FK-`): Bi-pod Mount, Gable Mount, Tripod Mount, 10ft Pole, 5ft Pole, Side Stays, Satellite Pole Mount, 1000M drop. Replace with real part numbers before techs rely on them (changing an id later orphans old entries).
- Not yet decided: photo rules for **Fibre Drop Only** (MPT, Drop Route); whether Install Overview should be alone on **Fibre Existing Drop**; whether the **job summary header** should use the truck icon too.
- Field Cam still shows its own generic "Install" tip in settings (harmless).

## Gotchas

- Install/manifest/icon tags must stay in `<head>` (Android refused to install when they were in `<body>`).
- Pushing needs the **Claude GitHub App** installed on the XploreForms org; connecting GitHub alone only gives read access.
- `localStorage` keys are shared across tools on the same origin (`fieldkit.*`, `techstock.*`, `fieldcam.*`, `xplore_fsl_*`). Don't rename keys without migrating.
- Google sign-in can't run inside the Claude artifact preview; test Sheets on the real site.
