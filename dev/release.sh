#!/usr/bin/env bash
# One-step release: bump version.js (patch), check every page loads, commit, push to main, build the preview.
# usage: dev/release.sh "what changed (one line)" ["extra commit trailer lines"]
set -e
cd "$(dirname "$0")/.."
MSG="$1"; TRAILER="$2"; [ -n "$MSG" ] || { echo 'usage: dev/release.sh "what changed"'; exit 1; }
OLD=$(sed -n 's/.*version: "\([^"]*\)".*/\1/p' version.js)
NEW=$(echo "$OLD" | awk -F. '{print $1"."$2"."$3+1}')
NOW=$(TZ=America/Toronto date +%Y-%m-%dT%H:%M:%S%:z)
sed -i "s/version: \"$OLD\", updated: \"[^\"]*\"/version: \"$NEW\", updated: \"$NOW\"/" version.js
OUT=$(bash dev/run.sh dev/check.py); echo "$OUT"
if echo "$OUT" | grep -v '\[\]$' | grep -q .; then echo "PAGE ERRORS: not pushing"; git checkout version.js; exit 1; fi
git add -A
git commit -q -m "Field Kit $NEW: $MSG" ${TRAILER:+-m "$TRAILER"}
git push -q origin HEAD:main 2>&1 | grep -v -i "moved\|new location\|github.com/XploreForms" || true
python3 dev/build_preview.py . /tmp/fk-shots/fieldkit-preview.html
echo "Released $NEW -> publish /tmp/fk-shots/fieldkit-preview.html to the preview artifact"
