"""Tests for descriptor-based component classes.

Covers:
- Descriptor protocol basics (__set_name__, __get__, __set__)
- Event handler auto-registration and routing
- Each component's state defaults and event handling
- Rehydration from plain dicts (post-serialization)
- Inheritance of descriptors across subclasses
- JSON serialization round-trip
"""

import json

from djust_components.descriptors import (
    Accordion,
    Tabs,
    Modal,
    Collapsible,
    Sheet,
    Dropdown,
    Tooltip,
    Carousel,
)
from djust_components.mixins.base import TypedState


# ──────────────────────────────────────────────────────────────────────
# Helpers — build view classes inline to test descriptor protocol
# ──────────────────────────────────────────────────────────────────────


def _make_view_class(**descriptors):
    """Create a fresh view class with the given descriptor attributes."""
    return type("TestView", (), descriptors)


# ══════════════════════════════════════════════════════════════════════
# 1. Descriptor basics
# ══════════════════════════════════════════════════════════════════════


class TestDescriptorBasics:
    """Core descriptor protocol tests."""

    def test_set_name_registers_descriptor(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        assert "faq" in View._component_descriptors
        assert isinstance(View._component_descriptors["faq"], Accordion)

    def test_instance_access_returns_typed_state(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        state = obj.faq
        assert isinstance(state, TypedState)
        assert state.active == "q1"

    def test_component_id_matches_attr_name(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        assert obj.faq["component_id"] == "faq"
        assert obj.faq.get("component_id") == "faq"

    def test_two_instances_independent_state(self):
        View = _make_view_class(
            faq=Accordion(active="q1"),
            settings=Accordion(active="s1"),
        )
        a = View()
        b = View()
        a.faq = {"active": "q2"}
        assert a.faq.active == "q2"
        assert b.faq.active == "q1"
        assert a.settings.active == "s1"

    def test_dict_assignment_converts_to_typed_state(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        obj.faq = {"active": "q2", "multiple": True}
        assert isinstance(obj.faq, TypedState)
        assert obj.faq.active == "q2"
        assert obj.faq.multiple is True
        assert obj.faq["component_id"] == "faq"

    def test_class_level_access_returns_descriptor(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        assert isinstance(View.faq, Accordion)

    def test_multiple_descriptors_registered(self):
        View = _make_view_class(
            faq=Accordion(),
            nav=Tabs(),
            confirm=Modal(),
        )
        assert set(View._component_descriptors.keys()) == {"faq", "nav", "confirm"}


# ══════════════════════════════════════════════════════════════════════
# 2. Event handler auto-registration
# ══════════════════════════════════════════════════════════════════════


class TestEventHandlerRegistration:
    """Event handler auto-registration and routing."""

    def test_event_handler_exists_on_class(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        assert hasattr(View, "accordion_toggle")
        assert callable(View.accordion_toggle)

    def test_event_handler_updates_state(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        obj.accordion_toggle(value="q2", component_id="faq")
        assert obj.faq.active == "q2"

    def test_single_instance_auto_resolution(self):
        """When only one instance exists, component_id can be empty."""
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        obj.accordion_toggle(value="q2")
        assert obj.faq.active == "q2"

    def test_multiple_instances_require_component_id(self):
        """With multiple instances, empty component_id does nothing."""
        View = _make_view_class(
            faq=Accordion(active="q1"),
            settings=Accordion(active="s1"),
        )
        obj = View()
        obj.accordion_toggle(value="x")  # no component_id, 2 instances
        assert obj.faq.active == "q1"  # unchanged
        assert obj.settings.active == "s1"  # unchanged

    def test_different_event_names_for_different_components(self):
        View = _make_view_class(
            faq=Accordion(),
            nav=Tabs(),
            confirm=Modal(),
        )
        assert hasattr(View, "accordion_toggle")
        assert hasattr(View, "set_tab")
        assert hasattr(View, "toggle_modal")

    def test_event_handler_toggle_back(self):
        """Toggle accordion same value closes it."""
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        obj.accordion_toggle(value="q1", component_id="faq")
        assert obj.faq.active == ""


# ══════════════════════════════════════════════════════════════════════
# 3. Per-component tests
# ══════════════════════════════════════════════════════════════════════


class TestAccordion:
    def test_defaults(self):
        View = _make_view_class(faq=Accordion())
        obj = View()
        assert obj.faq.active == ""
        assert obj.faq.multiple is False

    def test_toggle_opens(self):
        View = _make_view_class(faq=Accordion())
        obj = View()
        View._component_descriptors["faq"]._handle_event(obj.faq, value="q1")
        assert obj.faq.active == "q1"

    def test_toggle_closes(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        View._component_descriptors["faq"]._handle_event(obj.faq, value="q1")
        assert obj.faq.active == ""

    def test_multiple_mode(self):
        View = _make_view_class(faq=Accordion(multiple=True))
        obj = View()
        desc = View._component_descriptors["faq"]
        # Ensure active starts as a list
        obj.faq.active = []
        desc._handle_event(obj.faq, value="q1")
        assert "q1" in obj.faq.active
        desc._handle_event(obj.faq, value="q2")
        assert "q1" in obj.faq.active
        assert "q2" in obj.faq.active
        desc._handle_event(obj.faq, value="q1")
        assert "q1" not in obj.faq.active
        assert "q2" in obj.faq.active

    def test_json_round_trip(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        data = json.loads(json.dumps(dict(obj.faq)))
        assert data["active"] == "q1"
        assert data["component_id"] == "faq"


class TestTabs:
    def test_defaults(self):
        View = _make_view_class(nav=Tabs())
        obj = View()
        assert obj.nav.active == ""

    def test_set_tab(self):
        View = _make_view_class(nav=Tabs())
        obj = View()
        View._component_descriptors["nav"]._handle_event(obj.nav, value="settings")
        assert obj.nav.active == "settings"

    def test_event_handler(self):
        View = _make_view_class(nav=Tabs(active="overview"))
        obj = View()
        obj.set_tab(value="settings", component_id="nav")
        assert obj.nav.active == "settings"

    def test_json_round_trip(self):
        View = _make_view_class(nav=Tabs(active="overview"))
        obj = View()
        data = json.loads(json.dumps(dict(obj.nav)))
        assert data["active"] == "overview"


class TestModal:
    def test_defaults(self):
        View = _make_view_class(confirm=Modal())
        obj = View()
        assert obj.confirm.is_open is False

    def test_toggle_open(self):
        View = _make_view_class(confirm=Modal())
        obj = View()
        View._component_descriptors["confirm"]._handle_event(obj.confirm)
        assert obj.confirm.is_open is True

    def test_toggle_close(self):
        View = _make_view_class(confirm=Modal())
        obj = View()
        desc = View._component_descriptors["confirm"]
        desc._handle_event(obj.confirm)
        desc._handle_event(obj.confirm)
        assert obj.confirm.is_open is False

    def test_event_handler(self):
        View = _make_view_class(confirm=Modal())
        obj = View()
        obj.toggle_modal(component_id="confirm")
        assert obj.confirm.is_open is True

    def test_json_round_trip(self):
        View = _make_view_class(confirm=Modal())
        obj = View()
        data = json.loads(json.dumps(dict(obj.confirm)))
        assert data["is_open"] is False


class TestCollapsible:
    def test_defaults(self):
        View = _make_view_class(details=Collapsible())
        obj = View()
        assert obj.details.is_open is False

    def test_toggle(self):
        View = _make_view_class(details=Collapsible())
        obj = View()
        View._component_descriptors["details"]._handle_event(obj.details)
        assert obj.details.is_open is True

    def test_event_handler(self):
        View = _make_view_class(details=Collapsible())
        obj = View()
        obj.toggle_collapsible(component_id="details")
        assert obj.details.is_open is True

    def test_json_round_trip(self):
        View = _make_view_class(details=Collapsible())
        obj = View()
        data = json.loads(json.dumps(dict(obj.details)))
        assert data["is_open"] is False


class TestSheet:
    def test_defaults(self):
        View = _make_view_class(sidebar=Sheet())
        obj = View()
        assert obj.sidebar.is_open is False
        assert obj.sidebar.side == "right"

    def test_custom_side(self):
        View = _make_view_class(sidebar=Sheet(side="left"))
        obj = View()
        assert obj.sidebar.side == "left"

    def test_toggle(self):
        View = _make_view_class(sidebar=Sheet())
        obj = View()
        View._component_descriptors["sidebar"]._handle_event(obj.sidebar)
        assert obj.sidebar.is_open is True

    def test_event_handler(self):
        View = _make_view_class(sidebar=Sheet())
        obj = View()
        obj.toggle_sheet(component_id="sidebar")
        assert obj.sidebar.is_open is True

    def test_json_round_trip(self):
        View = _make_view_class(sidebar=Sheet(side="left"))
        obj = View()
        data = json.loads(json.dumps(dict(obj.sidebar)))
        assert data["side"] == "left"
        assert data["is_open"] is False


class TestDropdown:
    def test_defaults(self):
        View = _make_view_class(menu=Dropdown())
        obj = View()
        assert obj.menu.is_open is False

    def test_toggle(self):
        View = _make_view_class(menu=Dropdown())
        obj = View()
        View._component_descriptors["menu"]._handle_event(obj.menu)
        assert obj.menu.is_open is True

    def test_client_tier(self):
        assert Dropdown.Meta.tier == "client"

    def test_event_handler(self):
        View = _make_view_class(menu=Dropdown())
        obj = View()
        obj.toggle_dropdown(component_id="menu")
        assert obj.menu.is_open is True

    def test_json_round_trip(self):
        View = _make_view_class(menu=Dropdown())
        obj = View()
        data = json.loads(json.dumps(dict(obj.menu)))
        assert data["is_open"] is False


class TestTooltip:
    def test_defaults(self):
        View = _make_view_class(hint=Tooltip())
        obj = View()
        assert obj.hint.is_visible is False

    def test_toggle(self):
        View = _make_view_class(hint=Tooltip())
        obj = View()
        View._component_descriptors["hint"]._handle_event(obj.hint)
        assert obj.hint.is_visible is True

    def test_client_tier(self):
        assert Tooltip.Meta.tier == "client"

    def test_event_handler(self):
        View = _make_view_class(hint=Tooltip())
        obj = View()
        obj.toggle_tooltip(component_id="hint")
        assert obj.hint.is_visible is True

    def test_json_round_trip(self):
        View = _make_view_class(hint=Tooltip())
        obj = View()
        data = json.loads(json.dumps(dict(obj.hint)))
        assert data["is_visible"] is False


class TestCarousel:
    def test_defaults(self):
        View = _make_view_class(slides=Carousel())
        obj = View()
        assert obj.slides.active == 0
        assert obj.slides.total == 0

    def test_go_to_slide(self):
        View = _make_view_class(slides=Carousel(total=5))
        obj = View()
        View._component_descriptors["slides"]._handle_event(obj.slides, value="3")
        assert obj.slides.active == 3

    def test_wraps_around(self):
        View = _make_view_class(slides=Carousel(total=3))
        obj = View()
        View._component_descriptors["slides"]._handle_event(obj.slides, value="5")
        assert obj.slides.active == 2  # 5 % 3

    def test_invalid_value_ignored(self):
        View = _make_view_class(slides=Carousel(total=3))
        obj = View()
        View._component_descriptors["slides"]._handle_event(obj.slides, value="abc")
        assert obj.slides.active == 0

    def test_zero_total_stays_zero(self):
        View = _make_view_class(slides=Carousel(total=0))
        obj = View()
        View._component_descriptors["slides"]._handle_event(obj.slides, value="2")
        assert obj.slides.active == 0

    def test_event_handler(self):
        View = _make_view_class(slides=Carousel(total=5))
        obj = View()
        obj.carousel_go(value="2", component_id="slides")
        assert obj.slides.active == 2

    def test_json_round_trip(self):
        View = _make_view_class(slides=Carousel(total=5, active=2))
        obj = View()
        # Access to initialise state
        _ = obj.slides
        data = json.loads(json.dumps(dict(obj.slides)))
        assert data["active"] == 2
        assert data["total"] == 5


# ══════════════════════════════════════════════════════════════════════
# 4. Rehydration
# ══════════════════════════════════════════════════════════════════════


class TestRehydration:
    """After djust serialization, state becomes a plain dict. Verify rehydration."""

    def test_plain_dict_rehydrates_to_typed_state(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        # Simulate djust deserialization: replace TypedState with plain dict
        obj.__dict__["_component_faq"] = {"active": "q2", "multiple": False}
        state = obj.faq
        assert isinstance(state, TypedState)
        assert state.active == "q2"
        assert state["component_id"] == "faq"

    def test_rehydrated_state_is_cached(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        obj.__dict__["_component_faq"] = {"active": "q2"}
        state1 = obj.faq
        state2 = obj.faq
        assert state1 is state2  # Same object, cached

    def test_rehydrated_state_handles_events(self):
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        obj.__dict__["_component_faq"] = {"active": "q1"}
        obj.accordion_toggle(value="q1", component_id="faq")
        assert obj.faq.active == ""  # Toggled off


# ══════════════════════════════════════════════════════════════════════
# 5. Inheritance
# ══════════════════════════════════════════════════════════════════════


class TestInheritance:
    """Subclass inherits parent's descriptors."""

    def test_subclass_inherits_descriptors(self):
        Parent = _make_view_class(faq=Accordion(active="q1"))

        class Child(Parent):
            pass

        assert "faq" in Child._component_descriptors
        obj = Child()
        assert obj.faq.active == "q1"

    def test_subclass_can_add_descriptors(self):
        Parent = _make_view_class(faq=Accordion())

        class Child(Parent):
            nav = Tabs(active="overview")

        assert "faq" in Child._component_descriptors
        assert "nav" in Child._component_descriptors
        obj = Child()
        assert obj.faq.active == ""
        assert obj.nav.active == "overview"

    def test_subclass_does_not_affect_parent(self):
        Parent = _make_view_class(faq=Accordion())

        class Child(Parent):
            nav = Tabs()

        assert "nav" not in Parent._component_descriptors
        assert "nav" in Child._component_descriptors

    def test_subclass_instances_independent(self):
        Parent = _make_view_class(faq=Accordion(active="q1"))

        class Child(Parent):
            pass

        p = Parent()
        c = Child()
        p.faq = {"active": "q2"}
        assert p.faq.active == "q2"
        assert c.faq.active == "q1"


# ══════════════════════════════════════════════════════════════════════
# 6. Render caching (task 5.4)
# ══════════════════════════════════════════════════════════════════════


class TestRenderCaching:
    """Dirty flag and render cache tests for TypedState."""

    def test_dirty_flag_detected_by_sync(self):
        """Mutating state sets _dirty=True."""
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        state = obj.faq
        # Force clean
        object.__setattr__(state, "_dirty", False)
        assert state._dirty is False
        # Mutate
        state.active = "q2"
        assert state._dirty is True

    def test_clean_state_keeps_cached_html(self):
        """When _dirty=False, _cached_html is preserved."""
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        state = obj.faq
        # Simulate a successful render cycle
        object.__setattr__(state, "_dirty", False)
        object.__setattr__(state, "_cached_html", "<div>cached</div>")
        # Access state without mutation — cache should remain
        _ = state.active
        assert state._cached_html == "<div>cached</div>"
        assert state._dirty is False

    def test_mutation_clears_cache(self):
        """Mutating state clears _cached_html."""
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        state = obj.faq
        object.__setattr__(state, "_cached_html", "<div>old</div>")
        object.__setattr__(state, "_dirty", False)
        # Mutate
        state.active = "q2"
        assert state._cached_html is None
        assert state._dirty is True

    def test_same_value_keeps_clean(self):
        """Setting the same value does not mark dirty."""
        View = _make_view_class(faq=Accordion(active="q1"))
        obj = View()
        state = obj.faq
        object.__setattr__(state, "_dirty", False)
        object.__setattr__(state, "_cached_html", "<div>cached</div>")
        # Set same value
        state.active = "q1"
        assert state._dirty is False
        assert state._cached_html == "<div>cached</div>"

    def test_render_hash_initially_none(self):
        """_render_hash starts as None."""
        View = _make_view_class(faq=Accordion())
        obj = View()
        assert obj.faq._render_hash is None


# ══════════════════════════════════════════════════════════════════════
# 7. Dependency tracking (task 6.5)
# ══════════════════════════════════════════════════════════════════════


class TestDependencyTracking:
    """Tests for _component_descriptors registry and dep map concepts."""

    def test_component_descriptors_registry_built(self):
        """_component_descriptors is populated on class definition."""
        View = _make_view_class(
            faq=Accordion(),
            nav=Tabs(),
            confirm=Modal(),
        )
        assert hasattr(View, "_component_descriptors")
        assert len(View._component_descriptors) == 3
        assert "faq" in View._component_descriptors
        assert "nav" in View._component_descriptors
        assert "confirm" in View._component_descriptors

    def test_unreferenced_components_detectable(self):
        """We can identify descriptors not in a dep map."""
        View = _make_view_class(
            faq=Accordion(),
            nav=Tabs(),
            sidebar=Sheet(),
        )
        # Simulate a template that only references faq and nav
        template_deps = {"faq", "nav"}
        all_descriptors = set(View._component_descriptors.keys())
        unreferenced = all_descriptors - template_deps
        assert unreferenced == {"sidebar"}

    def test_dep_map_intersection(self):
        """Cross-referencing template deps with descriptors gives used components."""
        View = _make_view_class(
            faq=Accordion(),
            nav=Tabs(),
        )
        # Simulate template deps that include non-component vars
        template_deps = {"faq", "nav", "items", "title"}
        component_names = set(View._component_descriptors.keys())
        used_components = component_names & template_deps
        assert used_components == {"faq", "nav"}

    def test_empty_descriptors_registry(self):
        """Class with no descriptors has no registry."""
        View = type("EmptyView", (), {})
        assert not hasattr(View, "_component_descriptors")


# ══════════════════════════════════════════════════════════════════════
# 8. Client/server tier system (task 7.6)
# ══════════════════════════════════════════════════════════════════════


class TestTierSystem:
    """Tests for tier declaration, optimistic rules, and client-tier behavior."""

    def test_tier_declaration_client(self):
        """Dropdown and Tooltip declare tier='client'."""
        assert Dropdown.Meta.tier == "client"
        assert Tooltip.Meta.tier == "client"

    def test_tier_declaration_server_default(self):
        """Server-tier components either have no tier or no Meta.tier."""
        # Accordion has no tier attribute — defaults to server
        assert not hasattr(Accordion.Meta, "tier")

    def test_optimistic_rule_format(self):
        """Accordion can have an optimistic_rule with action/target/class keys."""
        # Verify the rule structure if present
        rule = getattr(Accordion.Meta, "optimistic_rule", None)
        if rule is not None:
            assert "action" in rule
            assert "target" in rule
            assert "class" in rule

    def test_client_tier_still_has_event(self):
        """Client-tier components still have Meta.event for server-path fallback."""
        assert hasattr(Dropdown.Meta, "event")
        assert Dropdown.Meta.event == "toggle_dropdown"
        assert hasattr(Tooltip.Meta, "event")
        assert Tooltip.Meta.event == "toggle_tooltip"

    def test_client_tier_handler_registered(self):
        """Client-tier components still register handlers on the view class."""
        View = _make_view_class(menu=Dropdown(), hint=Tooltip())
        assert hasattr(View, "toggle_dropdown")
        assert hasattr(View, "toggle_tooltip")

    def test_client_tier_handler_works(self):
        """Client-tier handlers still work server-side for testing."""
        View = _make_view_class(menu=Dropdown())
        obj = View()
        assert obj.menu.is_open is False
        obj.toggle_dropdown(component_id="menu")
        assert obj.menu.is_open is True

    def test_tier_serializable(self):
        """Tier declaration can be read for serialization to client."""
        View = _make_view_class(menu=Dropdown(), faq=Accordion())
        tiers = {}
        for name, desc in View._component_descriptors.items():
            meta = getattr(desc.__class__, "Meta", None)
            tiers[name] = getattr(meta, "tier", "server")
        assert tiers == {"menu": "client", "faq": "server"}
