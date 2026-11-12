# dev/ — tooling (not part of the app)

- `dev/run.sh <script.py>`: serve the app on localhost:8765, run the script, stop.
- `dev/check.py`: load all four pages, print page errors (`[]` = clean).
- `dev/release.sh "msg" ["trailers"]`: bump, check, commit, push, build preview to `/tmp/fk-shots/`.
- `dev/build_preview.py [repo] [out.html]`: one-file preview for the Claude artifact.
- Tests drive Chromium at 360x780 with touch and seed `fieldkit.profile`, `fieldkit.setupDone`, `techstock.gs`. Screenshots go to `/tmp/fk-shots/`. No camera/GPS in tests (fake BarcodeDetector).
- `catalogue/`, `inventory-xlsx/`, `test-serials/`: one-off generators (paths inside may need adjusting). `test-serials/test-serials.html` = fake serials + barcodes for real-phone testing.

## Tests by area (`tests/`)
Not an organised suite: grab the ones near what you changed.

| Area | Scripts |
|---|---|
| Whole-app walk-through (setup → menu → New SA → Field Cam → Notes → Stock → order) | `t5.py`, `t5_strict.py` (browser refuses history changes), `t1.py`–`t4.py` (early setup and New SA steps) |
| Setup and settings | `t3.py`, `t7.py`, `t8.py` (SAP/Salesforce digits), `t9.py` (Purolator box), `tskip.py` (skip Google Sheets), `tfoot.py` (footer time zone), `tpill.py` (Field Stock status pill), `tkb.py` (keyboard closes at 7 digits), `tp.py` (clipboard icon) |
| Menu and SA card | `tmenu.py`, `tmenu2.py`, `tcard.py`, `t2tap.py` (restart button), `tcompass.py` (Compass links), `topt.py` (SA-first mockups, obsolete) |
| Back button and navigation | `tb.py`, `tb2.py`, `tb3.py` (Field Cam/Notes → SA home), `tbk.py` (menu page warn then close), `tsa.py` (back link shows the SA-#) |
| SA equipment slots and mount | `tl.py`, `tl2.py`, `tc.py`, `tc2.py`, `tm.py`–`tm3.py`, `tn.py` (Field Notes mount question) |
| Technology | `ttech.py`, `tvas.py`, `tfn.py` (carries into Field Notes) |
| Photos and scanning in Field Cam | `tsn.py` (SN tiles, solo, scanner), `tdev.py`, `tdev2.py` (scan labels per platform), `tscanfix.py`, `tfixsn.py` (old labels repaired), `ts2.py` (scan from SA page returns), `tsc.py`, `tshift.py` (scan mode, nothing shifts), `tother.py` (Other… box), `tcam3.py` (viewfinder hint), `tsave.py` (Compressing toast), `ttd.py` (Temp Drop Deployed), `ttemp.py` |
| Field Notes behaviour | `tskip2.py` (scrolls past answered), `tfin.py` (scrolls to the comment when done) |
| Field Stock | `tlog.py` (opens on Log), `tdeploy.py` (pick any item by hand), `tcat.py` (bundled names, one stock row), `tord.py`, `tord2.py`, `torder3.py`, `tordshot.py` (order form, email, own page), `tappr.py`, `t6.py` (transfer email CC) |
| Test inventory (removed from the app) | `tstate.py`, `ttest.py`, `tclean.py` (the clean-up that removed it) |
| Header experiments (obsolete: Curtis chose full-size headers) | `tj.py`–`tj3.py`, `tf.py`, `ts.py` |
| Side by side (one-app rebuild) | `tside.py` (Field Cam / Comments inside an SA vs on their own, a second page loading alongside, migration) |
| Other | `tchk.py` (prints page errors on load), `tsv.py` (checks every barcode on the test-serials page scans), `tsb.py`, `tsb2.py` (runs the preview in a sandboxed frame), `tnm.py`–`tnm3.py` (the old stock-names tool, obsolete), `tstate.py`, `shotset.py` |

