"""Tests for per-component interactive mixins."""

import json

import pytest


# ─── ComponentMixin Base ───


class TestComponentMixinBase:
    """Tests for the ComponentMixin base class."""

    def test_instances_attr(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        assert m._instances_attr() == "widget_instances"

    def test_get_instances_returns_empty_dict_when_none(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        assert m._get_instances() == {}

    def test_get_instances_returns_dict_when_set(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        m.widget_instances = {"a": {"val": 1}}
        assert m._get_instances() == {"a": {"val": 1}}

    def test_get_instance_returns_state(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        m.widget_instances = {"a": {"val": 1}}
        assert m._get_instance("a") == {"val": 1}

    def test_get_instance_returns_empty_for_unknown(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        m.widget_instances = {"a": {"val": 1}}
        assert m._get_instance("unknown") == {}

    def test_init_instances_creates_dict(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        result = m._init_instances()
        assert result == {}
        assert m.widget_instances == {}

    def test_init_instances_idempotent(self):
        from djust_components.mixins.base import ComponentMixin

        class TestMixin(ComponentMixin):
            component_name = "widget"
            widget_instances = None

        m = TestMixin()
        m.widget_instances = {"a": {"val": 1}}
        result = m._init_instances()
        assert result == {"a": {"val": 1}}


# ─── TypedState Dirty Tracking ───


class TestTypedStateDirtyFlag:
    def test_mutation_sets_dirty(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = ""

        s = MyState()
        object.__setattr__(s, "_dirty", False)
        s.active = "q1"
        assert s._dirty is True

    def test_same_value_stays_clean(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = "q1"

        s = MyState(active="q1")
        object.__setattr__(s, "_dirty", False)
        s.active = "q1"
        assert s._dirty is False

    def test_mutation_clears_cached_html(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = ""

        s = MyState()
        object.__setattr__(s, "_cached_html", "<div>cached</div>")
        s.active = "q2"
        assert s._cached_html is None

    def test_from_dict_rehydration_idempotent(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = ""

        original = MyState(active="q1")
        rehydrated = MyState.from_dict(original)
        assert rehydrated is original

    def test_from_dict_converts_plain_dict(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = ""

        result = MyState.from_dict({"active": "q1"})
        assert isinstance(result, MyState)
        assert result.active == "q1"

    def test_dirty_flag_after_init(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = ""

        s = MyState(active="q1")
        assert s._dirty is True  # new state is dirty (needs first render)

    def test_json_serialization_preserves_values(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            active: str = ""
            multiple: bool = False

        s = MyState(active="q1", multiple=True)
        data = json.loads(json.dumps(s))
        assert data == {"active": "q1", "multiple": True}

    def test_render_hash_cleared_on_mutation(self):
        from djust_components.mixins.base import TypedState

        class MyState(TypedState):
            count: int = 0

        s = MyState()
        object.__setattr__(s, "_render_hash", "abc123")
        s.count = 5
        assert s._cached_html is None


# ─── AccordionMixin ───


class TestAccordionMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        assert m.accordion_instances == {"faq": {"active": "q1", "multiple": False}}

    def test_init_multiple_instances(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        m.init_accordion("help")
        assert "faq" in m.accordion_instances
        assert "help" in m.accordion_instances
        assert m.accordion_instances["faq"]["active"] == "q1"
        assert m.accordion_instances["help"]["active"] == ""

    def test_toggle_opens_item(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq")
        m.accordion_toggle(value="q1", component_id="faq")
        assert m.accordion_instances["faq"]["active"] == "q1"

    def test_toggle_closes_item(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        m.accordion_toggle(value="q1", component_id="faq")
        assert m.accordion_instances["faq"]["active"] == ""

    def test_toggle_switches_item(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        m.accordion_toggle(value="q2", component_id="faq")
        assert m.accordion_instances["faq"]["active"] == "q2"

    def test_toggle_ignores_unknown_component_id(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq")
        m.accordion_toggle(value="q1", component_id="unknown")
        assert m.accordion_instances["faq"]["active"] == ""

    def test_multiple_mode(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", multiple=True)
        m.accordion_toggle(value="q1", component_id="faq")
        m.accordion_toggle(value="q2", component_id="faq")
        assert "q1" in m.accordion_instances["faq"]["active"]
        assert "q2" in m.accordion_instances["faq"]["active"]

    def test_multiple_mode_toggle_off(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", multiple=True)
        m.accordion_toggle(value="q1", component_id="faq")
        m.accordion_toggle(value="q1", component_id="faq")
        assert "q1" not in m.accordion_instances["faq"]["active"]

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        ctx = m.get_accordion_ctx("faq")
        assert ctx == {
            "active": "q1",
            "event": "accordion_toggle",
            "component_id": "faq",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        m.init_accordion("help", multiple=True)
        m.accordion_toggle(value="a", component_id="help")
        serialized = json.dumps(m.accordion_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.accordion_instances

    def test_routes_by_component_id(self):
        from djust_components.mixins.accordion import AccordionMixin

        m = AccordionMixin()
        m.init_accordion("faq", active="q1")
        m.init_accordion("help")
        m.accordion_toggle(value="h1", component_id="help")
        assert m.accordion_instances["faq"]["active"] == "q1"
        assert m.accordion_instances["help"]["active"] == "h1"


# ─── TabsMixin ───


class TestTabsMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        assert m.tabs_instances == {"nav": {"active": "overview"}}

    def test_init_multiple_instances(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        m.init_tabs("settings", active="general")
        assert "nav" in m.tabs_instances
        assert "settings" in m.tabs_instances

    def test_set_tab(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        m.set_tab(value="settings", component_id="nav")
        assert m.tabs_instances["nav"]["active"] == "settings"

    def test_set_tab_ignores_unknown_component_id(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        m.set_tab(value="settings", component_id="unknown")
        assert m.tabs_instances["nav"]["active"] == "overview"

    def test_routes_by_component_id(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        m.init_tabs("settings", active="general")
        m.set_tab(value="billing", component_id="settings")
        assert m.tabs_instances["nav"]["active"] == "overview"
        assert m.tabs_instances["settings"]["active"] == "billing"

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        ctx = m.get_tabs_ctx("nav")
        assert ctx == {
            "active": "overview",
            "event": "set_tab",
            "component_id": "nav",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.tabs import TabsMixin

        m = TabsMixin()
        m.init_tabs("nav", active="overview")
        serialized = json.dumps(m.tabs_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.tabs_instances


# ─── ModalMixin ───


class TestModalMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm")
        assert m.modal_instances == {"confirm": {"is_open": False}}

    def test_init_open(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm", is_open=True)
        assert m.modal_instances["confirm"]["is_open"] is True

    def test_init_multiple_instances(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm")
        m.init_modal("delete")
        assert "confirm" in m.modal_instances
        assert "delete" in m.modal_instances

    def test_open_modal(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm")
        m.open_modal(component_id="confirm")
        assert m.modal_instances["confirm"]["is_open"] is True

    def test_close_modal(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm", is_open=True)
        m.close_modal(component_id="confirm")
        assert m.modal_instances["confirm"]["is_open"] is False

    def test_toggle_modal(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm")
        m.toggle_modal(component_id="confirm")
        assert m.modal_instances["confirm"]["is_open"] is True
        m.toggle_modal(component_id="confirm")
        assert m.modal_instances["confirm"]["is_open"] is False

    def test_ignores_unknown_component_id(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm")
        m.open_modal(component_id="unknown")
        assert m.modal_instances["confirm"]["is_open"] is False

    def test_routes_by_component_id(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm")
        m.init_modal("delete")
        m.open_modal(component_id="delete")
        assert m.modal_instances["confirm"]["is_open"] is False
        assert m.modal_instances["delete"]["is_open"] is True

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm", is_open=True)
        ctx = m.get_modal_ctx("confirm")
        assert ctx == {
            "is_open": True,
            "open_event": "open_modal",
            "close_event": "close_modal",
            "toggle_event": "toggle_modal",
            "component_id": "confirm",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.modal import ModalMixin

        m = ModalMixin()
        m.init_modal("confirm", is_open=True)
        serialized = json.dumps(m.modal_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.modal_instances


# ─── CollapsibleMixin ───


class TestCollapsibleMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("details")
        assert m.collapsible_instances == {"details": {"is_open": False}}

    def test_init_open(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("details", is_open=True)
        assert m.collapsible_instances["details"]["is_open"] is True

    def test_init_multiple_instances(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("a")
        m.init_collapsible("b")
        assert "a" in m.collapsible_instances
        assert "b" in m.collapsible_instances

    def test_toggle(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("details")
        m.toggle_collapsible(component_id="details")
        assert m.collapsible_instances["details"]["is_open"] is True
        m.toggle_collapsible(component_id="details")
        assert m.collapsible_instances["details"]["is_open"] is False

    def test_ignores_unknown_component_id(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("details")
        m.toggle_collapsible(component_id="unknown")
        assert m.collapsible_instances["details"]["is_open"] is False

    def test_routes_by_component_id(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("a")
        m.init_collapsible("b")
        m.toggle_collapsible(component_id="a")
        assert m.collapsible_instances["a"]["is_open"] is True
        assert m.collapsible_instances["b"]["is_open"] is False

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("details", is_open=True)
        ctx = m.get_collapsible_ctx("details")
        assert ctx == {
            "is_open": True,
            "event": "toggle_collapsible",
            "component_id": "details",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.collapsible import CollapsibleMixin

        m = CollapsibleMixin()
        m.init_collapsible("details", is_open=True)
        serialized = json.dumps(m.collapsible_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.collapsible_instances


# ─── SheetMixin ───


class TestSheetMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings")
        assert m.sheet_instances == {"settings": {"is_open": False, "side": "right"}}

    def test_init_with_options(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("nav", is_open=True, side="left")
        assert m.sheet_instances["nav"]["is_open"] is True
        assert m.sheet_instances["nav"]["side"] == "left"

    def test_init_invalid_side_defaults(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings", side="top")
        assert m.sheet_instances["settings"]["side"] == "right"

    def test_init_multiple_instances(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("a")
        m.init_sheet("b")
        assert "a" in m.sheet_instances
        assert "b" in m.sheet_instances

    def test_open_sheet(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings")
        m.open_sheet(component_id="settings")
        assert m.sheet_instances["settings"]["is_open"] is True

    def test_close_sheet(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings", is_open=True)
        m.close_sheet(component_id="settings")
        assert m.sheet_instances["settings"]["is_open"] is False

    def test_ignores_unknown_component_id(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings")
        m.open_sheet(component_id="unknown")
        assert m.sheet_instances["settings"]["is_open"] is False

    def test_routes_by_component_id(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("a")
        m.init_sheet("b")
        m.open_sheet(component_id="b")
        assert m.sheet_instances["a"]["is_open"] is False
        assert m.sheet_instances["b"]["is_open"] is True

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings", is_open=True, side="left")
        ctx = m.get_sheet_ctx("settings")
        assert ctx == {
            "is_open": True,
            "side": "left",
            "open_event": "open_sheet",
            "close_event": "close_sheet",
            "component_id": "settings",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.sheet import SheetMixin

        m = SheetMixin()
        m.init_sheet("settings", is_open=True, side="left")
        serialized = json.dumps(m.sheet_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.sheet_instances


# ─── DropdownMixin ───


class TestDropdownMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("actions")
        assert m.dropdown_instances == {"actions": {"is_open": False}}

    def test_init_multiple_instances(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("a")
        m.init_dropdown("b")
        assert "a" in m.dropdown_instances
        assert "b" in m.dropdown_instances

    def test_toggle_dropdown(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("actions")
        m.toggle_dropdown(component_id="actions")
        assert m.dropdown_instances["actions"]["is_open"] is True
        m.toggle_dropdown(component_id="actions")
        assert m.dropdown_instances["actions"]["is_open"] is False

    def test_close_dropdown(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("actions", is_open=True)
        m.close_dropdown(component_id="actions")
        assert m.dropdown_instances["actions"]["is_open"] is False

    def test_ignores_unknown_component_id(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("actions")
        m.toggle_dropdown(component_id="unknown")
        assert m.dropdown_instances["actions"]["is_open"] is False

    def test_routes_by_component_id(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("a")
        m.init_dropdown("b")
        m.toggle_dropdown(component_id="b")
        assert m.dropdown_instances["a"]["is_open"] is False
        assert m.dropdown_instances["b"]["is_open"] is True

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("actions", is_open=True)
        ctx = m.get_dropdown_ctx("actions")
        assert ctx == {
            "is_open": True,
            "toggle_event": "toggle_dropdown",
            "close_event": "close_dropdown",
            "component_id": "actions",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.dropdown import DropdownMixin

        m = DropdownMixin()
        m.init_dropdown("actions", is_open=True)
        serialized = json.dumps(m.dropdown_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.dropdown_instances


# ─── TooltipMixin ───


class TestTooltipMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("help")
        assert m.tooltip_instances == {"help": {"is_visible": False}}

    def test_init_multiple_instances(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("a")
        m.init_tooltip("b")
        assert "a" in m.tooltip_instances
        assert "b" in m.tooltip_instances

    def test_show_tooltip(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("help")
        m.show_tooltip(component_id="help")
        assert m.tooltip_instances["help"]["is_visible"] is True

    def test_hide_tooltip(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("help", is_visible=True)
        m.hide_tooltip(component_id="help")
        assert m.tooltip_instances["help"]["is_visible"] is False

    def test_ignores_unknown_component_id(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("help")
        m.show_tooltip(component_id="unknown")
        assert m.tooltip_instances["help"]["is_visible"] is False

    def test_routes_by_component_id(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("a")
        m.init_tooltip("b")
        m.show_tooltip(component_id="b")
        assert m.tooltip_instances["a"]["is_visible"] is False
        assert m.tooltip_instances["b"]["is_visible"] is True

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("help", is_visible=True)
        ctx = m.get_tooltip_ctx("help")
        assert ctx == {
            "is_visible": True,
            "show_event": "show_tooltip",
            "hide_event": "hide_tooltip",
            "component_id": "help",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.tooltip import TooltipMixin

        m = TooltipMixin()
        m.init_tooltip("help", is_visible=True)
        serialized = json.dumps(m.tooltip_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.tooltip_instances


# ─── CarouselMixin ───


class TestCarouselMixin:
    def test_init_creates_instance(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", total=5)
        assert m.carousel_instances == {"gallery": {"active": 0, "total": 5}}

    def test_init_with_active(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", active=2, total=5)
        assert m.carousel_instances["gallery"]["active"] == 2

    def test_init_multiple_instances(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("a", total=3)
        m.init_carousel("b", total=5)
        assert "a" in m.carousel_instances
        assert "b" in m.carousel_instances

    def test_carousel_next(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", total=3)
        m.carousel_next(component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 1

    def test_carousel_next_wraps(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", active=2, total=3)
        m.carousel_next(component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 0

    def test_carousel_prev(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", active=1, total=3)
        m.carousel_prev(component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 0

    def test_carousel_prev_wraps(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", active=0, total=3)
        m.carousel_prev(component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 2

    def test_carousel_go(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", total=5)
        m.carousel_go(value="3", component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 3

    def test_carousel_go_out_of_range(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", total=3)
        m.carousel_go(value="5", component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 0  # unchanged

    def test_carousel_go_invalid_value(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", total=3)
        m.carousel_go(value="abc", component_id="gallery")
        assert m.carousel_instances["gallery"]["active"] == 0  # unchanged

    def test_ignores_unknown_component_id(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", total=3)
        m.carousel_next(component_id="unknown")
        assert m.carousel_instances["gallery"]["active"] == 0

    def test_routes_by_component_id(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("a", total=3)
        m.init_carousel("b", total=5)
        m.carousel_next(component_id="b")
        assert m.carousel_instances["a"]["active"] == 0
        assert m.carousel_instances["b"]["active"] == 1

    def test_get_ctx_returns_correct_state(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", active=2, total=5)
        ctx = m.get_carousel_ctx("gallery")
        assert ctx == {
            "active": 2,
            "total": 5,
            "prev_event": "carousel_prev",
            "next_event": "carousel_next",
            "go_event": "carousel_go",
            "component_id": "gallery",
        }

    def test_state_is_json_serializable(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("gallery", active=2, total=5)
        serialized = json.dumps(m.carousel_instances)
        deserialized = json.loads(serialized)
        assert deserialized == m.carousel_instances

    def test_zero_total_no_crash(self):
        from djust_components.mixins.carousel import CarouselMixin

        m = CarouselMixin()
        m.init_carousel("empty", total=0)
        m.carousel_next(component_id="empty")
        m.carousel_prev(component_id="empty")
        assert m.carousel_instances["empty"]["active"] == 0


# ─── Template Tag component_id Tests ───


class TestTemplateTagComponentId:
    """Verify component_id emits data-component-id on dj-click elements."""

    def test_accordion_component_id(self, render):
        html = render(
            '{% accordion id="faq" active="q1" event="accordion_toggle" component_id="my-faq" %}'
            '{% accordion_item id="q1" title="Question 1" %}Answer{% endaccordion_item %}'
            '{% endaccordion %}'
        )
        assert 'data-component-id="my-faq"' in html

    def test_accordion_no_component_id(self, render):
        html = render(
            '{% accordion id="faq" active="q1" %}'
            '{% accordion_item id="q1" title="Q1" %}A{% endaccordion_item %}'
            '{% endaccordion %}'
        )
        assert "data-component-id" not in html

    def test_tabs_component_id(self, render):
        html = render(
            '{% tabs id="nav" active="t1" event="set_tab" component_id="my-tabs" %}'
            '{% tab id="t1" label="Tab1" %}Content{% endtab %}'
            '{% endtabs %}'
        )
        assert 'data-component-id="my-tabs"' in html

    def test_tabs_no_component_id(self, render):
        html = render(
            '{% tabs id="nav" active="t1" %}'
            '{% tab id="t1" label="Tab1" %}Content{% endtab %}'
            '{% endtabs %}'
        )
        assert "data-component-id" not in html

    def test_modal_component_id(self, render):
        html = render(
            '{% modal id="confirm" title="Sure?" open=True close_event="close_modal" component_id="my-modal" %}'
            'Content'
            '{% endmodal %}',
            ctx={"True": True},
        )
        assert 'data-component-id="my-modal"' in html

    def test_dropdown_component_id(self, render):
        html = render(
            '{% dropdown id="menu" label="Menu" open=True toggle_event="toggle_dropdown" component_id="my-dd" %}'
            '<a>Item</a>'
            '{% enddropdown %}',
            ctx={"True": True},
        )
        assert 'data-component-id="my-dd"' in html

    def test_collapsible_component_id(self, render):
        html = render(
            '{% collapsible trigger="Show" event="toggle_collapsible" component_id="my-coll" %}'
            'Content'
            '{% endcollapsible %}'
        )
        assert 'data-component-id="my-coll"' in html

    def test_sheet_component_id(self, render):
        html = render(
            '{% sheet title="Settings" close_event="close_sheet" component_id="my-sheet" %}'
            'Content'
            '{% endsheet %}'
        )
        assert 'data-component-id="my-sheet"' in html

    def test_tooltip_component_id(self, render):
        html = render(
            '{% tooltip text="Help text" component_id="my-tip" %}'
            'Hover me'
            '{% endtooltip %}'
        )
        assert 'data-component-id="my-tip"' in html

    def test_carousel_component_id(self, render):
        html = render(
            '{% carousel images=imgs active=0 component_id="my-carousel" %}',
            ctx={"imgs": [{"src": "a.jpg"}, {"src": "b.jpg"}]},
        )
        assert 'data-component-id="my-carousel"' in html

    def test_component_id_is_escaped(self, render):
        html = render(
            '{% accordion id="faq" active="q1" component_id=xss %}'
            '{% accordion_item id="q1" title="Q1" %}A{% endaccordion_item %}'
            '{% endaccordion %}',
            ctx={"xss": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&#" in html or "&quot;" in html


# ─── Multi-Mixin Composition ───


class TestMultiMixinComposition:
    """Test using multiple mixins on the same object (simulates LiveView)."""

    def test_accordion_and_tabs_coexist(self):
        from djust_components.mixins.accordion import AccordionMixin
        from djust_components.mixins.tabs import TabsMixin

        class MyView(AccordionMixin, TabsMixin):
            pass

        v = MyView()
        v.init_accordion("faq", active="q1")
        v.init_tabs("nav", active="overview")

        v.accordion_toggle(value="q2", component_id="faq")
        v.set_tab(value="settings", component_id="nav")

        assert v.accordion_instances["faq"]["active"] == "q2"
        assert v.tabs_instances["nav"]["active"] == "settings"

    def test_all_mixins_coexist(self):
        from djust_components.mixins import (
            AccordionMixin, TabsMixin, ModalMixin,
            CollapsibleMixin, SheetMixin, DropdownMixin,
            TooltipMixin, CarouselMixin,
        )

        class MyView(
            AccordionMixin, TabsMixin, ModalMixin,
            CollapsibleMixin, SheetMixin, DropdownMixin,
            TooltipMixin, CarouselMixin,
        ):
            pass

        v = MyView()
        v.init_accordion("acc1")
        v.init_tabs("tabs1")
        v.init_modal("modal1")
        v.init_collapsible("coll1")
        v.init_sheet("sheet1")
        v.init_dropdown("dd1")
        v.init_tooltip("tip1")
        v.init_carousel("car1", total=3)

        # Each has its own instances dict
        assert v.accordion_instances is not None
        assert v.tabs_instances is not None
        assert v.modal_instances is not None
        assert v.collapsible_instances is not None
        assert v.sheet_instances is not None
        assert v.dropdown_instances is not None
        assert v.tooltip_instances is not None
        assert v.carousel_instances is not None

    def test_all_state_json_serializable(self):
        from djust_components.mixins import (
            AccordionMixin, TabsMixin, ModalMixin,
            CollapsibleMixin, SheetMixin, DropdownMixin,
            TooltipMixin, CarouselMixin,
        )

        class MyView(
            AccordionMixin, TabsMixin, ModalMixin,
            CollapsibleMixin, SheetMixin, DropdownMixin,
            TooltipMixin, CarouselMixin,
        ):
            pass

        v = MyView()
        v.init_accordion("acc1", active="q1", multiple=True)
        v.init_tabs("tabs1", active="overview")
        v.init_modal("modal1", is_open=True)
        v.init_collapsible("coll1", is_open=True)
        v.init_sheet("sheet1", is_open=True, side="left")
        v.init_dropdown("dd1", is_open=True)
        v.init_tooltip("tip1", is_visible=True)
        v.init_carousel("car1", active=2, total=5)

        # All instances dicts should be JSON-serializable
        for attr in [
            "accordion_instances", "tabs_instances", "modal_instances",
            "collapsible_instances", "sheet_instances", "dropdown_instances",
            "tooltip_instances", "carousel_instances",
        ]:
            data = getattr(v, attr)
            serialized = json.dumps(data)
            deserialized = json.loads(serialized)
            assert deserialized == data, f"{attr} is not JSON round-trip safe"


# ─── Package Exports ───


class TestPackageExports:
    """Verify mixins are accessible from top-level package."""

    def test_imports_from_package(self):
        from djust_components import (
            ComponentMixin,
            AccordionMixin,
            TabsMixin,
            ModalMixin,
            CollapsibleMixin,
            SheetMixin,
            DropdownMixin,
            TooltipMixin,
            CarouselMixin,
        )

        assert ComponentMixin is not None
        assert AccordionMixin is not None
        assert TabsMixin is not None
        assert ModalMixin is not None
        assert CollapsibleMixin is not None
        assert SheetMixin is not None
        assert DropdownMixin is not None
        assert TooltipMixin is not None
        assert CarouselMixin is not None

    def test_imports_from_mixins_subpackage(self):
        from djust_components.mixins import (
            ComponentMixin,
            AccordionMixin,
            TabsMixin,
            ModalMixin,
            CollapsibleMixin,
            SheetMixin,
            DropdownMixin,
            TooltipMixin,
            CarouselMixin,
        )

        assert ComponentMixin is not None
        assert AccordionMixin is not None
