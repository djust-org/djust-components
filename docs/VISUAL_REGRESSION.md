# Visual Regression Testing (VRT)

Visual regression tests capture screenshots of every component in the gallery and compare them against committed baselines. Any pixel-level drift flags a diff for human review.

## Baseline Source: Component Gallery

The component gallery (`manage.py component_gallery`) serves every registered component with example data on a single page. This is the sole source of truth for VRT screenshots.

```bash
python manage.py component_gallery --port 8765
```

The gallery renders all template-tag components and Python component classes using the examples defined in `gallery/examples.py`.

## Screenshot Matrix

Each component is captured across a matrix of **2 color modes x 3 breakpoints = 6 screenshots**:

| Breakpoint | Width  | Suffix    |
|-----------|--------|-----------|
| Mobile    | 375px  | `mobile`  |
| Tablet    | 768px  | `tablet`  |
| Desktop   | 1280px | `desktop` |

| Color Mode | Suffix  |
|-----------|---------|
| Light     | `light` |
| Dark      | `dark`  |

Screenshot filenames follow the pattern:
```
baselines/<component-slug>-<mode>-<breakpoint>.png
# e.g. baselines/badge-light-mobile.png
```

## Capturing Baselines Locally

Use the provided helper script:

```bash
# Capture all baselines (starts gallery automatically)
bash scripts/capture-vrt-baselines.sh

# Or with a custom port
VRT_PORT=9000 bash scripts/capture-vrt-baselines.sh
```

The script:
1. Starts the component gallery server in the background
2. Waits for the server to be ready
3. Runs Playwright to screenshot each component section at every breakpoint/mode combination
4. Stops the gallery server
5. Writes PNGs to `baselines/`

### Prerequisites

```bash
npm install -D @playwright/test
npx playwright install chromium
```

## Playwright Commands (Manual)

If you prefer running Playwright directly:

```bash
# Start gallery in one terminal
python manage.py component_gallery --port 8765

# Capture a single full-page screenshot (light, desktop)
npx playwright screenshot \
  --viewport-size="1280,720" \
  http://localhost:8765 \
  baselines/gallery-light-desktop.png

# Dark mode (uses prefers-color-scheme media)
npx playwright screenshot \
  --viewport-size="1280,720" \
  --color-scheme=dark \
  http://localhost:8765 \
  baselines/gallery-dark-desktop.png

# Mobile viewport
npx playwright screenshot \
  --viewport-size="375,812" \
  http://localhost:8765 \
  baselines/gallery-light-mobile.png
```

## CI Integration

The GitHub Actions workflow (`.github/workflows/vrt.yml`) runs on every PR that modifies CSS or template files:

1. **Install** -- Python deps, Playwright, Chromium
2. **Serve** -- Start component gallery on port 8765
3. **Capture** -- Screenshot the gallery at all 6 matrix combinations
4. **Compare** -- If baselines exist in `baselines/`, pixel-diff against them
5. **Artifact** -- Upload diff images as workflow artifacts on failure

### Reviewing Failures

When VRT fails in CI:
1. Download the `vrt-diffs` artifact from the failed workflow run
2. Open the diff images -- changed pixels are highlighted in red
3. If the change is intentional, update baselines locally and commit:
   ```bash
   bash scripts/capture-vrt-baselines.sh
   git add baselines/
   git commit -m "test: update VRT baselines"
   ```
4. If the change is unintentional, fix the regression and re-push

## Updating Baselines

After intentional visual changes (new components, CSS tweaks, theme updates):

```bash
# Re-capture all baselines
bash scripts/capture-vrt-baselines.sh

# Review the changes
git diff --stat baselines/

# Commit updated baselines
git add baselines/
git commit -m "test: update VRT baselines for <reason>"
```

## Directory Structure

```
djust-components/
  baselines/                  # Committed PNG baselines (git-tracked)
    gallery-light-mobile.png
    gallery-light-tablet.png
    gallery-light-desktop.png
    gallery-dark-mobile.png
    gallery-dark-tablet.png
    gallery-dark-desktop.png
  scripts/
    capture-vrt-baselines.sh  # Local baseline capture helper
  .github/workflows/
    vrt.yml                   # CI workflow
  docs/
    VISUAL_REGRESSION.md      # This file
```

## Design Decisions

- **Full-page screenshots** rather than per-component isolation: the gallery already lays out every component, so full-page captures catch layout interactions and spacing regressions that isolated shots would miss.
- **Playwright over Puppeteer/Cypress**: Playwright has first-class support for color-scheme emulation, viewport control, and headless Chromium -- everything VRT needs with no extra config.
- **No pixel-diff threshold**: diffs use exact comparison. Any change requires explicit baseline update. This prevents silent drift.
- **Baselines committed to git**: keeps baselines versioned alongside the code that produced them. LFS is recommended if the baselines directory grows large.
