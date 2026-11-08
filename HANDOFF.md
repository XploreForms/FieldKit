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
- Headers: page-colour, no green bar or Xplore logo, 560px column on desktop. Headers are pinned; once scrolled they go **slim with the title centred** and "‹ Field Kit" / "‹ Job" always visible.
- Menu cards are a uniform 72px, two lines, nothing cut off. Home header shows **name only** (no dealer). Field Stock header also name only.
- In-progress job card uses the **truck with work-order lines** icon; restart button is the circular arrow with a two-tap "Tap to start new".
- No version numbers inside the tools; version only shows on the menu footer.

**Profile / setup**
- Step 1: Your Name, Work Email (@xplore.ca), Mobile Number, **Xplore Approver Email**. Only the approver email has hint text: "Approves your manual order requests and is CC'd on your transfer requests." The approver is CC'd on every transfer email (with both techs).
- Step 2: Dealer Name (format **Location XCI Tech**, e.g. Cambridge XCI Tech), SAP # (6 digits), Salesforce # (7 digits), shipping address, **Ship to a Purolator depot and hold for pickup** (checkbox), **Default Shipping Instructions** (optional, ≤300 chars). Both shipping options go into every manual order email.
- Step 3: Google Sheets backup (required). Settings has **Sync Now** (signs in if needed, Field Stock syncs, returns to settings).
- Name and dealer can only be changed in Field Kit settings (not in Field Cam). **Grid lines** live in Field Cam's own settings.

**Job flow**
- New Job screen collects SA-# (auto "SA-", 7 digits only, Paste finds it in copied text), job type, platform, drop (Fibre installs/conversions), VAS service. Outcome starts as Complete.
- In a job, Field Cam has no "New Job"/"Start Next Job"; saving all photos goes straight to Field Notes.
- Copying comments in Field Notes goes to the job summary. Outcome can be changed in Field Cam (chip ▾) or the summary; Field Notes follows and copied comments get "Needs update".
- Complete Job asks for a second tap if photos aren't saved, comments aren't copied, or required slots are empty.

**Equipment slots** (`slotSet()` / `slotIds()` in `fieldkit-jobs.js`)
- Install & Conversion: Fixed Wireless = Mount, Surge (always Deployed), Radio, Router, XWH, XTV. Fibre Existing Drop = NID, ONT, Router, XWH, XTV. Fibre Drop Required/Only = Drop, NID, ONT, Router, XWH, XTV. Satellite (SurfBeam) = Trimast, AzEl, Dish, Modem, TRIA.
- Repair: same slots by platform, **all optional** (Fibre repair gets every fibre slot).
- Choices read **Deployed / Not Needed** (Trimast/AzEl/Dish also "Reused existing"). Mount options match Field Notes exactly: J-Arm, J-Arm + Side Stays, Gable Mount + 10ft Pole, Bipod + 5ft Pole, Tripod + 10ft Pole, Tower, Not Needed.
- Field Notes' Mount Type and drop length fill the slots (a hand-picked slot sticks until the Notes answer changes). XWH/XTV get one slot per unit Field Notes says.
- Serials: scan, type, or **Paste**; typed into a slot narrows the model; picker asks when ambiguous.
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
