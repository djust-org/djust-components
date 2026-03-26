"""Django views for the component gallery."""

from django.http import HttpResponse
from django.template import Template, Context
from django.templatetags.static import static

from .registry import get_gallery_data


GALLERY_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>djust-components Gallery</title>
    <link rel="stylesheet" href="{{ component_css_url }}">
    <link rel="stylesheet" href="{{ component_classes_css_url }}">
    <style>
        /* ── Reset & Base ── */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg: #ffffff;
            --bg-card: #f9fafb;
            --text: #111827;
            --text-muted: #6b7280;
            --border: #e5e7eb;
            --accent: #3b82f6;
            --radius: 8px;
            --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

            /* Component CSS variables (minimal set for rendering) */
            --foreground: 0 0% 9%;
            --background: 0 0% 100%;
            --primary: 221 83% 53%;
            --primary-foreground: 0 0% 100%;
            --secondary: 210 40% 96%;
            --secondary-foreground: 215 25% 27%;
            --muted: 210 40% 96%;
            --muted-foreground: 215 16% 47%;
            --accent-hue: 210 40% 96%;
            --destructive: 0 84% 60%;
            --border-color: 214 32% 91%;
            --ring: 221 83% 53%;
            --success: 142 76% 36%;
            --warning: 38 92% 50%;
            --danger: 0 84% 60%;
            --info: 199 89% 48%;
        }

        [data-theme="dark"] {
            --bg: #0f172a;
            --bg-card: #1e293b;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
            --border: #334155;
            --accent: #60a5fa;

            --foreground: 210 40% 98%;
            --background: 222 47% 11%;
            --primary: 217 91% 60%;
            --primary-foreground: 0 0% 100%;
            --secondary: 217 33% 17%;
            --secondary-foreground: 210 40% 98%;
            --muted: 217 33% 17%;
            --muted-foreground: 215 20% 65%;
            --accent-hue: 217 33% 17%;
            --destructive: 0 63% 31%;
            --border-color: 217 33% 17%;
            --ring: 224 76% 48%;
            --success: 142 76% 36%;
            --warning: 38 92% 50%;
            --danger: 0 63% 31%;
            --info: 199 89% 48%;
        }

        body {
            font-family: var(--font);
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        /* ── Layout ── */
        .gallery-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            background: var(--bg);
            z-index: 100;
        }

        .gallery-header h1 {
            font-size: 1.25rem;
            font-weight: 600;
        }

        .gallery-header h1 span {
            color: var(--text-muted);
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
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text);
            border-radius: var(--radius);
            cursor: pointer;
            font-size: 0.8rem;
        }

        .gallery-toolbar button:hover {
            border-color: var(--accent);
        }

        .gallery-toolbar button.active {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .gallery-body {
            display: flex;
            min-height: calc(100vh - 57px);
        }

        /* ── Sidebar ── */
        .gallery-sidebar {
            width: 220px;
            border-right: 1px solid var(--border);
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
            color: var(--text-muted);
            padding: 8px 16px 4px;
            margin-top: 8px;
        }

        .gallery-sidebar a {
            display: block;
            padding: 4px 16px;
            color: var(--text);
            text-decoration: none;
            font-size: 0.85rem;
        }

        .gallery-sidebar a:hover {
            background: var(--bg-card);
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
            border-bottom: 1px solid var(--border);
        }

        /* ── Component Card ── */
        .component-card {
            border: 1px solid var(--border);
            border-radius: var(--radius);
            margin-bottom: 24px;
            overflow: hidden;
        }

        .component-card-header {
            padding: 12px 16px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .component-card-header .tag-badge {
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            background: var(--accent);
            color: white;
            font-weight: 500;
        }

        .variant-section {
            padding: 16px;
            border-bottom: 1px solid var(--border);
        }

        .variant-section:last-child {
            border-bottom: none;
        }

        .variant-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 8px;
            font-weight: 500;
        }

        .variant-preview {
            padding: 16px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: auto;
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
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 6px 10px;
            cursor: pointer;
            color: var(--text);
        }
    </style>
</head>
<body>
    <header class="gallery-header">
        <h1>djust-components<span>Gallery</span></h1>
        <div class="gallery-toolbar">
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
        function toggleTheme() {
            const html = document.documentElement;
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('djust-gallery-theme', next);
            document.getElementById('theme-toggle').textContent = next === 'dark' ? '☀️' : '🌙';
        }

        // Restore saved theme
        (function() {
            const saved = localStorage.getItem('djust-gallery-theme');
            if (saved) {
                document.documentElement.setAttribute('data-theme', saved);
                document.getElementById('theme-toggle').textContent = saved === 'dark' ? '☀️' : '🌙';
            }
        })();

        function setPreview(mode, e) {
            const main = document.querySelector('.gallery-content');
            main.classList.remove('mobile', 'tablet', 'desktop');
            main.classList.add(mode);
            document.querySelectorAll('.gallery-toolbar button:not(.theme-toggle)').forEach(b => b.classList.remove('active'));
            if (e && e.target) e.target.classList.add('active');
        }
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
    html = GALLERY_TEMPLATE.replace("{{ component_css_url }}", static("djust_components/components.css"))
    html = html.replace("{{ component_classes_css_url }}", static("djust_components/components-classes.css"))
    html = html.replace("{{ sidebar_html }}", sidebar_html)
    html = html.replace("{{ content_html }}", content_html)

    return HttpResponse(html)
