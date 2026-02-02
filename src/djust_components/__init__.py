"""
djust-components: Reusable UI components for djust.

Add 'djust_components' to INSTALLED_APPS, then use:

    {% load djust_components %}
    {% modal id="confirm" title="Are you sure?" %}
        <p>This action cannot be undone.</p>
    {% endmodal %}
"""

__version__ = "0.1.0"

default_app_config = "djust_components.apps.DjustComponentsConfig"
