"""Component gallery -- visual QA tool for djust-components.

Provides auto-discovery of all registered template tags and component classes,
paired with curated example data, rendered into a self-contained HTML gallery
with light/dark mode toggle and responsive preview controls.

Usage via management command::

    python manage.py component_gallery              # Serve on port 8765
    python manage.py component_gallery --port 9000  # Custom port
    python manage.py component_gallery --dry-run    # List components and exit

Submodules:
    registry    Auto-discovery of template tags and component classes
    examples    Curated example data for every component
    views       Django view that renders the gallery page
"""

from .registry import discover_component_classes, discover_template_tags, get_gallery_data
from .views import gallery_view

__all__ = [
    "discover_component_classes",
    "discover_template_tags",
    "get_gallery_data",
    "gallery_view",
]
