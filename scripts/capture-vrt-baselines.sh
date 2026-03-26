#!/usr/bin/env bash
# capture-vrt-baselines.sh — Capture VRT baseline screenshots from the component gallery.
#
# Prerequisites:
#   npm install -D @playwright/test
#   npx playwright install chromium
#
# Usage:
#   bash scripts/capture-vrt-baselines.sh
#   VRT_PORT=9000 bash scripts/capture-vrt-baselines.sh

set -euo pipefail

PORT="${VRT_PORT:-8765}"
BASELINES_DIR="baselines"
GALLERY_PID=""

cleanup() {
    if [ -n "$GALLERY_PID" ]; then
        echo "Stopping gallery server (PID $GALLERY_PID)..."
        kill "$GALLERY_PID" 2>/dev/null || true
        wait "$GALLERY_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "==> Starting component gallery on port ${PORT}..."
python manage.py component_gallery --port "$PORT" &
GALLERY_PID=$!

echo "==> Waiting for gallery to be ready..."
for i in $(seq 1 30); do
    if curl -s "http://localhost:${PORT}" > /dev/null 2>&1; then
        echo "    Gallery is ready."
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: Gallery did not start within 30 seconds." >&2
        exit 1
    fi
    sleep 1
done

mkdir -p "$BASELINES_DIR"

echo "==> Capturing baselines..."

BREAKPOINTS="mobile:375:812 tablet:768:1024 desktop:1280:720"
MODES="light dark"

for mode in $MODES; do
    for bp in $BREAKPOINTS; do
        bp_name="${bp%%:*}"
        rest="${bp#*:}"
        width="${rest%%:*}"
        height="${rest#*:}"

        color_flag=""
        if [ "$mode" = "dark" ]; then
            color_flag="--color-scheme=dark"
        fi

        outfile="${BASELINES_DIR}/gallery-${mode}-${bp_name}.png"

        npx playwright screenshot \
            --viewport-size="${width},${height}" \
            $color_flag \
            --full-page \
            --wait-for-timeout=2000 \
            "http://localhost:${PORT}" \
            "$outfile"

        echo "    Captured ${outfile} (${width}x${height}, ${mode})"
    done
done

echo ""
echo "==> Done. Baselines written to ${BASELINES_DIR}/:"
ls -lh "$BASELINES_DIR"/*.png
echo ""
echo "To commit: git add ${BASELINES_DIR}/ && git commit -m 'test: update VRT baselines'"
