# Display/Layout Primitives — Implementation Plan

## Components

### 1. Scroll Area (#62)
- **Tag**: `{% scroll_area max_height="400px" %}...{% endscroll_area %}`
- **Node**: `ScrollAreaNode` — block tag with `max_height`, `custom_class` kwargs
- **CSS**: `.dj-scroll-area` with custom scrollbar styling (`::-webkit-scrollbar`, `scrollbar-width`)
- **CSS vars**: `--dj-scroll-area-max-height`, `--dj-scroll-area-thumb`, `--dj-scroll-area-track`
- **XSS**: Escape `max_height` and `custom_class` in attributes

### 2. Callout / Blockquote (#67)
- **Tag**: `{% callout type="info" title="Note" %}...{% endcallout %}`
- **Node**: `CalloutNode` — block tag with `type` (info/warning/danger/success/default), `title`, `icon`, `custom_class`
- **CSS**: `.dj-callout`, `.dj-callout--info/warning/danger/success` with colored left border, icon area
- **CSS vars**: `--dj-callout-border-width`, `--dj-callout-bg`, `--dj-callout-fg`
- **XSS**: Escape `title`, `type`, `icon`, `custom_class`

### 3. Aspect Ratio (#116)
- **Tag**: `{% aspect_ratio ratio="16/9" %}...{% endaspect_ratio %}`
- **Node**: `AspectRatioNode` — block tag with `ratio`, `custom_class`
- **CSS**: `.dj-aspect-ratio` using `aspect-ratio` CSS property
- **XSS**: Escape `ratio` and `custom_class`

### 4. Description List (#134)
- **Tag**: `{% description_list items=items layout="horizontal" %}`
- **Node**: `DescriptionListNode` — self-closing tag with `items` (list of dicts with `term`/`detail`), `layout` (vertical/horizontal), `custom_class`
- **CSS**: `.dj-dl`, `.dj-dl--horizontal` with grid layout
- **XSS**: Escape all `term` and `detail` values

### 5. Sticky Header (#171)
- **Tag**: `{% sticky_header %}...{% endsticky_header %}`
- **Node**: `StickyHeaderNode` — block tag with `offset` (top offset), `z_index`, `custom_class`
- **CSS**: `.dj-sticky-header` with `position: sticky`, shadow-on-scroll via `IntersectionObserver` or pure CSS
- **CSS vars**: `--dj-sticky-header-bg`, `--dj-sticky-header-shadow`, `--dj-sticky-header-z`
- **XSS**: Escape `offset`, `z_index`, `custom_class`

## Files Modified

1. `src/djust_components/templatetags/djust_components.py` — 5 new Node classes + 5 `@register.tag` functions
2. `src/djust_components/static/djust_components/components.css` — CSS for all 5 components
3. `tests/test_components.py` — Test classes for all 5 components + XSS coverage
4. `CHANGELOG.md` — Document new components

## Test Plan

- Functional tests: render with defaults, render with all options, variable resolution
- XSS tests: script-tag injection in text params, attribute-breaking injection in HTML attributes
- Edge cases: empty content, missing optional params
