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


class _LiveComponentBase:
    """Minimal stand-in for djust.components.base.LiveComponent.

    Implements the descriptor protocol (__set_name__, __get__, __set__) and
    event handler auto-registration so that descriptor-based components can
    be tested without a Rust/maturin build.
    """

    template_name = None
    template = None
    component_id = None

    def __init__(self, component_id=None, **kwargs):
        self._descriptor_defaults = kwargs
        self._descriptor_attr_name = None
        self._descriptor_storage_key = None
        self._mounted = False
        self._parent = None
        self._parent_callback = None
        if component_id is not None or not kwargs:
            self.component_id = component_id or self.__class__.__name__.lower()
            if hasattr(self, "mount") and callable(self.mount):
                self.mount(**kwargs)
            self._mounted = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __set_name__(self, owner, name):
        self._descriptor_attr_name = name
        self._descriptor_storage_key = f"_component_{name}"
        if not hasattr(owner, "_component_descriptors"):
            owner._component_descriptors = {}
        elif "_component_descriptors" not in owner.__dict__:
            owner._component_descriptors = dict(owner._component_descriptors)
        owner._component_descriptors[name] = self

        meta = getattr(self.__class__, "Meta", None)
        event_name = getattr(meta, "event", None)
        if event_name and not hasattr(owner, event_name):
            setattr(owner, event_name, self._make_event_handler(event_name))

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        state_cls = getattr(self.__class__, "State", None)
        if state_cls is None:
            return self
        state = obj.__dict__.get(self._descriptor_storage_key)
        if state is None:
            state = state_cls(**self._descriptor_defaults)
            state["component_id"] = self._descriptor_attr_name
            obj.__dict__[self._descriptor_storage_key] = state
        elif isinstance(state, dict) and not isinstance(state, state_cls):
            state = state_cls.from_dict(state)
            state["component_id"] = self._descriptor_attr_name
            obj.__dict__[self._descriptor_storage_key] = state
        return state

    def __set__(self, obj, value):
        state_cls = getattr(self.__class__, "State", None)
        if state_cls is not None and isinstance(value, dict) and not isinstance(value, state_cls):
            value = state_cls.from_dict(value)
            if self._descriptor_attr_name:
                value["component_id"] = self._descriptor_attr_name
        if self._descriptor_storage_key:
            obj.__dict__[self._descriptor_storage_key] = value
        else:
            obj.__dict__[self._descriptor_attr_name or "component"] = value

    def _make_event_handler(self, event_name):
        component_type = type(self)

        def handler(view_self, value="", component_id="", **kwargs):
            if not component_id:
                descriptors = getattr(type(view_self), "_component_descriptors", {})
                matches = [n for n, d in descriptors.items() if isinstance(d, component_type)]
                if len(matches) == 1:
                    component_id = matches[0]
            if not component_id:
                return
            state = getattr(view_self, component_id, None)
            if state is None:
                return
            descriptor = getattr(type(view_self), component_id, None)
            if descriptor and hasattr(descriptor, "_handle_event"):
                descriptor._handle_event(state, value=value, **kwargs)

        handler.__name__ = event_name
        handler.__qualname__ = event_name
        return handler

    def _handle_event(self, state, **kwargs):
        pass

    def mount(self, **kwargs):
        pass

    def get_context_data(self):
        return {}


_djust_stub.LiveView = _LiveViewBase
_djust_stub.Component = _ComponentBase
sys.modules.setdefault("djust", _djust_stub)

# djust.components.base
_components_stub = types.ModuleType("djust.components")
_components_base_stub = types.ModuleType("djust.components.base")
_components_base_stub.LiveComponent = _LiveComponentBase
_components_stub.base = _components_base_stub
sys.modules.setdefault("djust.components", _components_stub)
sys.modules.setdefault("djust.components.base", _components_base_stub)

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
