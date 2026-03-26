"""Django views for the component gallery."""

from django.http import HttpResponse
from django.template import Template, Context
from django.templatetags.static import static

from .registry import get_gallery_data


def _get_theme_css(preset="default", design_system="material", mode="light"):
    """Generate theme CSS from djust-theming, or return empty string if unavailable."""
    try:
        from djust_theming.manager import ThemeState, generate_css_for_state
        state = ThemeState(
            theme=design_system,
            preset=preset,
            mode=mode,
            resolved_mode=mode,
        )
        return generate_css_for_state(state)
    except Exception:
        return ""


def _get_theme_options():
    """Get available presets and design systems from djust-theming."""
    try:
        from djust_theming.presets import THEME_PRESETS
        from djust_theming.theme_packs import DESIGN_SYSTEMS
        presets = sorted(THEME_PRESETS.keys())
        systems = sorted(DESIGN_SYSTEMS.keys())
        return presets, systems
    except Exception:
        return ["default"], ["material"]


GALLERY_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" data-theme="{{ html_mode }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>djust-components Gallery</title>
    <style data-djust-theme>{{ theme_css }}</style>
    <link rel="stylesheet" href="{{ theming_base_css_url }}">
    <link rel="stylesheet" href="{{ component_css_url }}">
    <link rel="stylesheet" href="{{ component_classes_css_url }}">
    <style>
        /* ── Reset & Base ── */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        /* No :root color tokens here — they come from djust-theming's
           <style data-djust-theme> and base.css loaded above. */

        body {
            font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
        }

        /* ── Layout ── */
        .gallery-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 24px;
            border-bottom: 1px solid var(--color-border);
            position: sticky;
            top: 0;
            background: var(--color-bg);
            z-index: 100;
        }

        .gallery-header h1 {
            font-size: 1.25rem;
            font-weight: 600;
        }

        .gallery-header h1 span {
            color: var(--color-text-secondary);
            font-weight: 400;
            font-size: 0.875rem;
            margin-left: 8px;
        }

        .gallery-toolbar {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .gallery-toolbar button {
            padding: 6px 12px;
            border: 1px solid var(--color-border);
            background: var(--color-bg-subtle);
            color: var(--color-text);
            border-radius: var(--radius-md, 8px);
            cursor: pointer;
            font-size: 0.8rem;
        }

        .gallery-toolbar button:hover {
            border-color: var(--color-primary);
        }

        .gallery-toolbar button.active {
            background: var(--color-primary);
            color: hsl(var(--primary-foreground));
            border-color: var(--color-primary);
        }

        .gallery-body {
            display: flex;
            min-height: calc(100vh - 57px);
        }

        /* ── Sidebar ── */
        .gallery-sidebar {
            width: 220px;
            border-right: 1px solid var(--color-border);
            padding: 16px 0;
            position: sticky;
            top: 57px;
            height: calc(100vh - 57px);
            overflow-y: auto;
            flex-shrink: 0;
        }

        .gallery-sidebar h3 {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-text-secondary);
            padding: 8px 16px 4px;
            margin-top: 8px;
        }

        .gallery-sidebar a {
            display: block;
            padding: 4px 16px;
            color: var(--color-text);
            text-decoration: none;
            font-size: 0.85rem;
        }

        .gallery-sidebar a:hover {
            background: var(--color-bg-subtle);
        }

        /* ── Content ── */
        .gallery-content {
            flex: 1;
            padding: 24px;
            max-width: 960px;
        }

        .category-section {
            margin-bottom: 48px;
        }

        .category-section h2 {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--color-border);
        }

        /* ── Component Card ── */
        .component-card {
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md, 8px);
            margin-bottom: 24px;
            overflow: hidden;
        }

        .component-card-header {
            padding: 12px 16px;
            background: var(--color-bg-subtle);
            border-bottom: 1px solid var(--color-border);
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .component-card-header .tag-badge {
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: var(--radius-sm, 4px);
            background: var(--color-primary);
            color: hsl(var(--primary-foreground));
            font-weight: 500;
        }

        .variant-section {
            padding: 16px;
            border-bottom: 1px solid var(--color-border);
        }

        .variant-section:last-child {
            border-bottom: none;
        }

        .variant-label {
            font-size: 0.75rem;
            color: var(--color-text-secondary);
            margin-bottom: 8px;
            font-weight: 500;
        }

        .variant-preview {
            padding: 16px;
            background: var(--color-bg);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md, 8px);
            overflow: hidden;
            /* Contain fixed-position overlays (modals, lightbox, sheets, etc.) */
            position: relative;
            transform: translateZ(0);  /* creates new containing block for position:fixed children */
            min-height: 60px;
            max-height: 500px;
            overflow-y: auto;
            z-index: 0;
        }

        /* Tame overlays: transform containment makes position:fixed behave as absolute.
           Also cap z-index so overlays don't escape their card. */
        .variant-preview .modal-overlay,
        .variant-preview .sheet-overlay,
        .variant-preview .sheet,
        .variant-preview .palette-overlay,
        .variant-preview .palette-dialog,
        .variant-preview .fab-container,
        .variant-preview .toast-container,
        .variant-preview .dj-connection-status,
        .variant-preview .dj-toast-container,
        .variant-preview .dj-confirm-dialog-backdrop,
        .variant-preview .dj-sidebar,
        .variant-preview .dj-sidebar__backdrop,
        .variant-preview .dj-bottom-sheet__backdrop,
        .variant-preview .dj-cookie-consent--bottom,
        .variant-preview .dj-cookie-consent--top,
        .variant-preview .dj-export-dialog__backdrop,
        .variant-preview .dj-lightbox,
        .variant-preview .dj-tour__overlay,
        .variant-preview .dj-tour__popover,
        .variant-preview .palette {
            position: absolute !important;
        }

        /* ── Responsive Preview Controls ── */
        .preview-container {
            transition: max-width 0.3s ease;
        }

        .preview-container.mobile { max-width: 375px; }
        .preview-container.tablet { max-width: 768px; }
        .preview-container.desktop { max-width: none; }

        /* ── Theme Toggle ── */
        .theme-toggle {
            font-size: 1.1rem;
            background: none;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md, 8px);
            padding: 6px 10px;
            cursor: pointer;
            color: var(--color-text);
        }

        .gallery-toolbar select {
            padding: 6px 8px;
            border: 1px solid var(--color-border);
            background: var(--color-bg-subtle);
            color: var(--color-text);
            border-radius: var(--radius-md, 8px);
            font-size: 0.8rem;
            cursor: pointer;
        }

        .gallery-toolbar label {
            font-size: 0.7rem;
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .toolbar-group {
            display: flex;
            align-items: center;
            gap: 4px;
        }
    </style>
</head>
<body>
    <header class="gallery-header">
        <h1>djust-components<span>Gallery</span></h1>
        <div class="gallery-toolbar">
            <div class="toolbar-group">
                <label>Design</label>
                <select id="design-system" onchange="changeTheme()">{{ design_system_options }}</select>
            </div>
            <div class="toolbar-group">
                <label>Preset</label>
                <select id="preset" onchange="changeTheme()">{{ preset_options }}</select>
            </div>
            <button onclick="setPreview('mobile', event)">Mobile</button>
            <button onclick="setPreview('tablet', event)">Tablet</button>
            <button class="active" onclick="setPreview('desktop', event)">Desktop</button>
            <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Toggle dark mode">🌙</button>
        </div>
    </header>

    <div class="gallery-body">
        <nav class="gallery-sidebar">
            {{ sidebar_html }}
        </nav>
        <main class="gallery-content preview-container desktop">
            {{ content_html }}
        </main>
    </div>

    <script>
        function setCookie(name, value) {
            document.cookie = name + '=' + value + ';path=/;max-age=31536000;SameSite=Lax';
        }

        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            setCookie('gallery_mode', next);
            window.location = window.location.pathname;
        }

        function changeTheme() {
            setCookie('gallery_ds', document.getElementById('design-system').value);
            setCookie('gallery_preset', document.getElementById('preset').value);
            setCookie('gallery_mode', document.documentElement.getAttribute('data-theme') || 'light');
            window.location = window.location.pathname;
        }

        // Set dark mode icon based on current mode
        (function() {
            const mode = document.documentElement.getAttribute('data-theme');
            document.getElementById('theme-toggle').textContent = mode === 'dark' ? '☀️' : '🌙';
        })();

        function setPreview(mode, e) {
            const main = document.querySelector('.gallery-content');
            main.classList.remove('mobile', 'tablet', 'desktop');
            main.classList.add(mode);
            document.querySelectorAll('.gallery-toolbar button:not(.theme-toggle)').forEach(b => b.classList.remove('active'));
            if (e && e.target) e.target.classList.add('active');
        }

        /* ── Gallery interactivity shim ──
           Handles dj-click / dj-change events client-side so components
           work in the static gallery without a LiveView WebSocket. */
        /* Use capture phase so we fire before inline onclick="stopPropagation()" */
        document.addEventListener('click', function(e) {
            const el = e.target.closest('[dj-click]');
            if (!el) return;

            /* Skip if element also has an inline onclick — it already handles itself */
            if (el.hasAttribute('onclick')) return;

            const action = el.getAttribute('dj-click');
            const value = el.getAttribute('data-value') || '';
            const preview = el.closest('.variant-preview');
            if (!preview) return;

            // ── Accordion ──
            if (action === 'accordion_toggle') {
                const item = el.closest('.dj-accordion-item');
                if (item) {
                    item.classList.toggle('dj-accordion-item--open');
                    const chevron = el.querySelector('.dj-accordion__chevron');
                    if (chevron) chevron.classList.toggle('dj-accordion__chevron--open');
                }
            }

            // ── Tabs ──
            if (action === 'set_tab') {
                const tabs = el.closest('.dj-tabs');
                if (tabs) {
                    tabs.querySelectorAll('.dj-tab').forEach(t => t.classList.remove('dj-tab--active'));
                    el.classList.add('dj-tab--active');
                    const pane = tabs.querySelector('.dj-tabs__pane');
                    if (pane) pane.textContent = value.charAt(0).toUpperCase() + value.slice(1) + ' content.';
                }
            }

            // ── Dropdown / Dropdown Menu ──
            if (action === 'toggle_dropdown' || action === 'dropdown_toggle') {
                const dd = el.closest('.dj-dropdown, .dj-dropdown-menu');
                if (dd) dd.classList.toggle('dj-dropdown--open');
            }

            // ── Modal close ──
            if (action === 'close_modal') {
                const backdrop = preview.querySelector('.dj-modal-backdrop, .modal-overlay');
                if (backdrop) backdrop.style.display = 'none';
            }

            // ── Sheet close ──
            if (action === 'close_sheet') {
                const overlay = preview.querySelector('.sheet-overlay, .dj-sheet-overlay');
                const sheet = preview.querySelector('.sheet');
                if (overlay) { overlay.style.opacity = '0'; overlay.style.visibility = 'hidden'; }
                if (sheet) sheet.style.transform = 'translateX(100%)';
            }

            // ── Generic toggle (split button, context menu, notification popover, etc.) ──
            if (action.startsWith('toggle_')) {
                const wrapper = el.closest('[class*="split-button"], [class*="context-menu"], [class*="notification-popover"], [class*="popconfirm"]');
                if (wrapper) wrapper.classList.toggle('is-open');
            }

            // ── Dismiss / close actions ──
            if (action.startsWith('dismiss_') || action === 'close') {
                const target = el.closest('[class*="toast"], [class*="alert"], [class*="banner"], [class*="announcement"]');
                if (target) target.style.display = 'none';
            }
        }, true); /* ← capture phase */

        // ── Switch / checkbox dj-change shim ──
        document.addEventListener('change', function(e) {
            const el = e.target.closest('[dj-change]');
            if (!el) return;
            // Switches are just checkboxes — the CSS handles the visual toggle
            // No extra JS needed since the checkbox state changes natively
        });

        // ── Accordion: add CSS for open/closed state ──
        (function() {
            const style = document.createElement('style');
            style.textContent = `
                .dj-accordion-item .dj-accordion__content { max-height: 0; overflow: hidden; transition: max-height 0.25s ease, padding 0.25s ease; padding: 0 1rem; }
                .dj-accordion-item--open .dj-accordion__content { max-height: 500px; padding: 0.75rem 1rem; }
                .dj-accordion__chevron { transition: transform 0.2s ease; display: inline-block; }
                .dj-accordion__chevron--open { transform: rotate(0deg); }
                .dj-accordion-item:not(.dj-accordion-item--open) .dj-accordion__chevron { transform: rotate(-90deg); }
                .dj-dropdown--open .dj-dropdown__menu { display: block !important; }
                .dj-dropdown__menu { display: none; }
            `;
            document.head.appendChild(style);
        })();
    </script>
</body>
</html>
"""


def gallery_view(request):
    """Render the full component gallery page.

    Builds a self-contained HTML page with:
    - Sidebar navigation grouped by component category
    - Each component rendered with all its example variants
    - Light/dark mode toggle (persisted to localStorage)
    - Responsive preview controls (mobile/tablet/desktop)

    Template tag examples are rendered through the Django template engine.
    Component class examples are rendered by calling their ``_render_custom()`` method.

    Args:
        request: Django HttpRequest.

    Returns:
        HttpResponse with the complete gallery HTML page.
    """
    # Read theme parameters from cookies (persisted by client JS)
    design_system = request.COOKIES.get("gallery_ds", "material")
    preset = request.COOKIES.get("gallery_preset", "default")
    mode = request.COOKIES.get("gallery_mode", "light")

    # Generate theme CSS
    theme_css = _get_theme_css(preset=preset, design_system=design_system, mode=mode)
    presets, systems = _get_theme_options()

    # Build <option> tags for dropdowns
    ds_options = "".join(
        f'<option value="{s}"{"selected" if s == design_system else ""}>{s.replace("_", " ").title()}</option>'
        for s in systems
    )
    preset_options = "".join(
        f'<option value="{p}"{"selected" if p == preset else ""}>{p.replace("_", " ").title()}</option>'
        for p in presets
    )

    data = get_gallery_data()
    categories = data["categories"]

    # Build sidebar HTML
    sidebar_parts = []
    for cat_label, components in sorted(categories.items()):
        sidebar_parts.append(f'<h3>{cat_label}</h3>')
        for comp in components:
            anchor = comp["name"].lower().replace(" ", "-")
            sidebar_parts.append(f'<a href="#{anchor}">{comp["label"]}</a>')
    sidebar_html = "\n".join(sidebar_parts)

    # Build content HTML
    content_parts = []
    for cat_label, components in sorted(categories.items()):
        content_parts.append(f'<section class="category-section" id="cat-{cat_label.lower()}">')
        content_parts.append(f'<h2>{cat_label}</h2>')

        for comp in components:
            anchor = comp["name"].lower().replace(" ", "-")
            comp_type = "tag" if comp["type"] == "tag" else "class"
            content_parts.append(f'<div class="component-card" id="{anchor}">')
            content_parts.append(
                f'<div class="component-card-header">'
                f'{comp["label"]}'
                f'<span class="tag-badge">{comp_type}</span>'
                f'</div>'
            )

            for variant in comp["variants"]:
                rendered = ""
                if comp["type"] == "tag":
                    try:
                        tpl_str = variant["template"]
                        t = Template("{% load djust_components %}" + tpl_str)
                        rendered = t.render(Context(variant.get("context", {})))
                    except Exception as exc:
                        rendered = f'<div style="color:red;">Render error: {exc}</div>'
                elif comp["type"] == "class":
                    try:
                        rendered = variant["render"]()
                    except Exception as exc:
                        rendered = f'<div style="color:red;">Render error: {exc}</div>'

                content_parts.append(f'<div class="variant-section">')
                content_parts.append(f'<div class="variant-label">{variant["name"]}</div>')
                content_parts.append(f'<div class="variant-preview">{rendered}</div>')
                content_parts.append('</div>')

            content_parts.append('</div>')
        content_parts.append('</section>')

    content_html = "\n".join(content_parts)

    # Render the full page (using simple string substitution, not Django template,
    # to avoid conflicts with the {{ }} in the gallery template itself)
    # Resolve static URLs and theme CSS
    theming_base_url = ""
    try:
        theming_base_url = static("djust_theming/css/base.css")
    except Exception:
        pass

    html = GALLERY_TEMPLATE.replace("{{ html_mode }}", mode)
    html = html.replace("{{ theme_css }}", theme_css)
    html = html.replace("{{ theming_base_css_url }}", theming_base_url)
    html = html.replace("{{ component_css_url }}", static("djust_components/components.css"))
    html = html.replace("{{ component_classes_css_url }}", static("djust_components/components-classes.css"))
    html = html.replace("{{ design_system_options }}", ds_options)
    html = html.replace("{{ preset_options }}", preset_options)
    html = html.replace("{{ sidebar_html }}", sidebar_html)
    html = html.replace("{{ content_html }}", content_html)

    return HttpResponse(html)
