"""Shared test infrastructure for djust-components.

This module centralises the boilerplate that every test file previously
duplicated:

1. **djust module stub** — djust requires a Rust/maturin build that is not
   available in the test virtualenv.  We inject minimal stubs for
   ``djust.LiveView``, ``djust.Component``, and ``djust.decorators``
   *before* any ``djust_components`` import can trigger the real import.

2. **Django settings.configure()** — called exactly once per process so
   that Django's template engine, apps registry, and in-memory SQLite
   database are ready.

3. **Common fixtures** — ``render`` helper for template-tag tests.
"""

import sys
import types

import pytest

# ──────────────────────────────────────────────────────────────────────
# 1.  djust stubs  (must run before ANY djust_components import)
# ──────────────────────────────────────────────────────────────────────

_djust_stub = types.ModuleType("djust")


class _LiveViewBase:
    """Minimal stand-in for djust.LiveView."""

    def get_context_data(self, **kwargs):
        return {}


class _ComponentBase:
    """Minimal stand-in for djust.Component."""

    def __init__(self, *args, **kwargs):
        pass

    def _render_custom(self):
        return "<div>stub</div>"

    def render(self):
        return self._render_custom()

    def __str__(self):
        return self._render_custom()

    def __html__(self):
        return self._render_custom()


_djust_stub.LiveView = _LiveViewBase
_djust_stub.Component = _ComponentBase
sys.modules.setdefault("djust", _djust_stub)

# djust.decorators
_decorators_stub = types.ModuleType("djust.decorators")


def _event_handler(fn=None, **kwargs):
    """No-op stand-in for @event_handler; returns the function unchanged."""
    if fn is not None:
        return fn

    def _decorator(f):
        return f

    return _decorator


_decorators_stub.event_handler = _event_handler
sys.modules.setdefault("djust.decorators", _decorators_stub)

# ──────────────────────────────────────────────────────────────────────
# 2.  Django minimal configuration
# ──────────────────────────────────────────────────────────────────────

import django  # noqa: E402
from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.staticfiles",
            "djust_components",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {"context_processors": []},
            }
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        STATIC_URL="/static/",
    )
    django.setup()

# ──────────────────────────────────────────────────────────────────────
# 3.  Common fixtures
# ──────────────────────────────────────────────────────────────────────

from django.template import Template, Context  # noqa: E402


@pytest.fixture()
def render():
    """Return a helper that renders a template string through the djust_components tag library."""

    def _render(template_str, ctx=None):
        t = Template("{% load djust_components %}" + template_str)
        return t.render(Context(ctx or {}))

    return _render
