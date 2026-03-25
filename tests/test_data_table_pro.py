"""Tests for Data Table Pro Phase 1 — Core Interactivity.

Covers:
  A. Rust handler (DataTableHandler) enhancements
  B. Template tag (data_table) context passthrough
  C. DataTableMixin for LiveViews
  D. CSS class definitions
"""
import types
import sys

# Stub djust before Django setup (djust requires Rust build not available in test venv)
_stub = types.ModuleType("djust")


class _LV:
    pass


class _Comp:
    pass


_stub.LiveView = _LV
_stub.Component = _Comp

# Stub djust.decorators with event_handler
_dec_stub = types.ModuleType("djust.decorators")


def _event_handler(fn):
    fn._is_event_handler = True
    return fn


_dec_stub.event_handler = _event_handler
sys.modules.setdefault("djust", _stub)
sys.modules.setdefault("djust.decorators", _dec_stub)

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "djust_components",
        ],
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": []},
        }],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    django.setup()

import pytest
from djust_components.rust_handlers import DataTableHandler


# ─── Fixtures ───

SAMPLE_COLUMNS = [
    {"key": "name", "label": "Name"},
    {"key": "email", "label": "Email"},
]

SAMPLE_ROWS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]


def _render(**kwargs):
    """Helper: render DataTableHandler with keyword args."""
    handler = DataTableHandler()
    # Build args list like the Rust engine would pass them
    args = []
    context = {}
    for k, v in kwargs.items():
        context[k] = v
        args.append(f"{k}={k}")
    return handler.render(args, context)


# ===========================================================================
# A. Rust Handler Tests
# ===========================================================================


class TestDataTableBackwardCompat:
    """Existing minimal usage must produce identical output."""

    def test_basic_table_structure(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-wrapper" in html
        assert '<table class="data-table">' in html
        assert "<thead>" in html
        assert "<tbody>" in html

    def test_all_headers_sortable_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'class="sortable' in html
        assert 'dj-click="table_sort"' in html

    def test_all_rows_rendered(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "Alice" in html
        assert "Bob" in html
        assert "Charlie" in html

    def test_sort_arrow_ascending(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       sort_by="name", sort_desc=False)
        # The active column should have an up arrow
        assert "active" in html

    def test_sort_arrow_descending(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       sort_by="name", sort_desc=True)
        assert "active" in html


class TestDataTableARIA:
    """ARIA attributes for accessibility."""

    def test_grid_role_on_container(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'role="grid"' in html

    def test_aria_label_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'aria-label="Data table"' in html

    def test_aria_sort_ascending(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       sort_by="name", sort_desc=False)
        assert 'aria-sort="ascending"' in html

    def test_aria_sort_descending(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       sort_by="name", sort_desc=True)
        assert 'aria-sort="descending"' in html

    def test_aria_sort_none_on_unsorted(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       sort_by="name")
        # The email column should have aria-sort="none"
        assert 'aria-sort="none"' in html

    def test_aria_busy_when_loading(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       loading=True)
        assert 'aria-busy="true"' in html


class TestDataTableSelection:
    """Row selection with checkboxes."""

    def test_no_checkboxes_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'type="checkbox"' not in html

    def test_checkboxes_when_selectable(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True)
        assert 'type="checkbox"' in html

    def test_select_all_checkbox_in_header(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True)
        assert 'aria-label="Select all rows"' in html

    def test_row_checkbox_with_event(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, select_event="my_select")
        assert 'dj-click="my_select"' in html

    def test_selected_rows_aria(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, selected_rows=[1, 2])
        assert 'aria-selected="true"' in html
        assert 'aria-selected="false"' in html

    def test_row_key_custom(self):
        rows = [{"uid": "a1", "name": "Alice"}, {"uid": "b2", "name": "Bob"}]
        html = _render(rows=rows, columns=[{"key": "name", "label": "Name"}],
                       selectable=True, row_key="uid",
                       selected_rows=["a1"])
        assert 'data-value="a1"' in html
        assert 'aria-selected="true"' in html

    def test_select_all_checkbox_data_value(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True)
        assert 'data-value="__all__"' in html


class TestDataTableSearch:
    """Global search input."""

    def test_no_search_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'role="searchbox"' not in html

    def test_search_input_rendered(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       search=True)
        assert 'role="searchbox"' in html
        assert 'data-table-search' in html

    def test_search_debounce(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       search=True, search_debounce=500)
        assert 'dj-debounce="500"' in html

    def test_search_default_debounce(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       search=True)
        assert 'dj-debounce="300"' in html

    def test_search_value_prefilled(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       search=True, search_query="alice")
        assert 'value="alice"' in html

    def test_search_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       search=True, search_event="my_search")
        assert 'dj-input="my_search"' in html

    def test_search_aria_label(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       search=True)
        assert 'aria-label="Search table"' in html


class TestDataTableFilters:
    """Per-column filters."""

    def test_no_filters_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-filter" not in html

    def test_text_filter_rendered(self):
        cols = [
            {"key": "name", "label": "Name", "filterable": True},
            {"key": "email", "label": "Email"},
        ]
        html = _render(rows=SAMPLE_ROWS, columns=cols)
        assert "data-table-filter" in html
        assert 'aria-label="Filter Name"' in html

    def test_select_filter_rendered(self):
        cols = [
            {"key": "status", "label": "Status", "filterable": True,
             "filter_type": "select",
             "filter_options": [
                 {"value": "active", "label": "Active"},
                 {"value": "inactive", "label": "Inactive"},
             ]},
        ]
        html = _render(rows=[], columns=cols)
        assert "<select" in html
        assert "Active" in html
        assert "Inactive" in html

    def test_filter_event_custom(self):
        cols = [{"key": "name", "label": "Name", "filterable": True}]
        html = _render(rows=SAMPLE_ROWS, columns=cols, filter_event="my_filter")
        assert 'dj-input="my_filter"' in html

    def test_filter_values_prefilled(self):
        cols = [{"key": "name", "label": "Name", "filterable": True}]
        html = _render(rows=SAMPLE_ROWS, columns=cols,
                       filters={"name": "alice"})
        assert 'value="alice"' in html


class TestDataTableLoading:
    """Loading / skeleton state."""

    def test_loading_shows_skeleton(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       loading=True)
        assert "skeleton" in html

    def test_loading_hides_rows(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       loading=True)
        assert "Alice" not in html


class TestDataTableEmpty:
    """Empty state when no rows."""

    def test_empty_default_message(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS)
        assert "No data" in html

    def test_empty_custom_title(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS,
                       empty_title="No users found")
        assert "No users found" in html

    def test_empty_custom_description(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS,
                       empty_description="Try adjusting your filters")
        assert "Try adjusting your filters" in html

    def test_empty_role_status(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS)
        assert 'role="status"' in html


class TestDataTablePagination:
    """Pagination controls."""

    def test_no_pagination_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "pagination" not in html.lower() or "data-table-pagination" not in html

    def test_pagination_rendered(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       paginate=True, page=1, total_pages=5)
        assert "Page 1 of 5" in html

    def test_pagination_prev_disabled_on_first(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       paginate=True, page=1, total_pages=5)
        # The prev button should be disabled
        assert "disabled" in html

    def test_pagination_next_disabled_on_last(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       paginate=True, page=5, total_pages=5)
        # Count disabled buttons - both arrows should NOT be disabled,
        # but next should be
        assert "disabled" in html

    def test_pagination_not_shown_single_page(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       paginate=True, page=1, total_pages=1)
        assert "data-table-pagination" not in html

    def test_pagination_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       paginate=True, page=2, total_pages=5,
                       page_event="my_page")
        assert 'dj-click="my_page"' in html

    def test_pagination_aria_navigation(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       paginate=True, page=1, total_pages=5)
        assert 'role="navigation"' in html
        assert 'aria-label="Table pagination"' in html


class TestDataTableStyling:
    """Striped and compact variants."""

    def test_striped_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       striped=True)
        assert "data-table-striped" in html

    def test_compact_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       compact=True)
        assert "data-table-compact" in html

    def test_no_extra_classes_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-striped" not in html
        assert "data-table-compact" not in html


class TestDataTableColumnWidth:
    """Column width support."""

    def test_column_width_applied(self):
        cols = [{"key": "name", "label": "Name", "width": "200px"}]
        html = _render(rows=SAMPLE_ROWS, columns=cols)
        assert 'style="width:200px"' in html


class TestDataTableXSS:
    """XSS escaping for user-controlled values."""

    def test_xss_in_search_query(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS,
                       search=True, search_query='<script>alert("xss")</script>')
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_in_empty_title(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS,
                       empty_title='<img src=x onerror=alert(1)>')
        # The angle brackets must be escaped so it's not rendered as HTML
        assert "<img" not in html
        assert "&lt;" in html

    def test_xss_in_cell_value(self):
        rows = [{"id": 1, "name": '<script>alert("xss")</script>'}]
        cols = [{"key": "name", "label": "Name"}]
        html = _render(rows=rows, columns=cols)
        assert "<script>" not in html

    def test_xss_in_column_label(self):
        cols = [{"key": "name", "label": '<img src=x onerror=alert(1)>'}]
        html = _render(rows=[], columns=cols)
        assert "<img" not in html
        assert "&lt;" in html

    def test_xss_in_filter_option_label(self):
        cols = [{"key": "status", "label": "Status", "filterable": True,
                 "filter_type": "select",
                 "filter_options": [{"value": "x", "label": '<script>xss</script>'}]}]
        html = _render(rows=[], columns=cols)
        assert "<script>" not in html


class TestDataTableColumnSortable:
    """Sortable flag per column."""

    def test_nonsortable_column_no_click(self):
        cols = [
            {"key": "name", "label": "Name", "sortable": True},
            {"key": "email", "label": "Email", "sortable": False},
        ]
        html = _render(rows=SAMPLE_ROWS, columns=cols)
        # "Email" header should NOT have dj-click
        # Split by </th> to check individual headers
        parts = html.split("</th>")
        name_th = [p for p in parts if "Name" in p][0]
        email_th = [p for p in parts if "Email" in p][0]
        assert "dj-click" in name_th
        assert "dj-click" not in email_th

    def test_all_sortable_by_default(self):
        """Columns without explicit sortable flag default to True."""
        cols = [{"key": "name", "label": "Name"}]
        html = _render(rows=SAMPLE_ROWS, columns=cols)
        assert "sortable" in html


# ===========================================================================
# B. Template Tag Tests
# ===========================================================================


class TestDataTableTemplateTag:
    """Template tag passes all new params to context."""

    def test_context_has_new_params(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            selectable=True, selected_rows=[1],
            search=True, search_query="test",
        )
        assert ctx["selectable"] is True
        assert ctx["selected_rows"] == [1]
        assert ctx["search"] is True
        assert ctx["search_query"] == "test"

    def test_default_values(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(rows=[], columns=[])
        assert ctx["selectable"] is False
        assert ctx["selected_rows"] == []
        assert ctx["search"] is False
        assert ctx["search_query"] == ""
        assert ctx["loading"] is False
        assert ctx["paginate"] is False
        assert ctx["striped"] is False
        assert ctx["compact"] is False
        assert ctx["empty_title"] == "No data"
        assert ctx["row_key"] == "id"

    def test_backward_compat_context(self):
        """Old-style call produces same keys as before."""
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            sort_by="name", sort_desc=True,
            sort_event="sort", page=2, total_pages=5,
            prev_event="prev", next_event="next",
        )
        assert ctx["rows"] == SAMPLE_ROWS
        assert ctx["columns"] == SAMPLE_COLUMNS
        assert ctx["sort_by"] == "name"
        assert ctx["sort_desc"] is True
        assert ctx["sort_event"] == "sort"
        assert ctx["page"] == 2
        assert ctx["total_pages"] == 5
        assert ctx["prev_event"] == "prev"
        assert ctx["next_event"] == "next"

    def test_all_new_params_in_context(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            selectable=True, selected_rows=[1],
            select_event="sel", row_key="uid",
            search=True, search_query="q", search_event="srch",
            search_debounce=500,
            filters={"name": "x"}, filter_event="flt",
            loading=True, empty_title="Empty",
            empty_description="Desc", empty_icon="!",
            paginate=True, page_event="pg",
            striped=True, compact=True,
        )
        assert ctx["select_event"] == "sel"
        assert ctx["row_key"] == "uid"
        assert ctx["search_debounce"] == 500
        assert ctx["filters"] == {"name": "x"}
        assert ctx["filter_event"] == "flt"
        assert ctx["loading"] is True
        assert ctx["empty_title"] == "Empty"
        assert ctx["empty_description"] == "Desc"
        assert ctx["empty_icon"] == "!"
        assert ctx["paginate"] is True
        assert ctx["page_event"] == "pg"
        assert ctx["striped"] is True
        assert ctx["compact"] is True


# ===========================================================================
# C. DataTableMixin Tests
# ===========================================================================


class TestDataTableMixinInit:
    """Mixin state initialization."""

    def test_default_state(self):
        from djust_components.mixins.data_table import DataTableMixin
        mixin = DataTableMixin()
        mixin.init_table_state()
        assert mixin.table_sort_by == ""
        assert mixin.table_sort_desc is False
        assert mixin.table_search_query == ""
        assert mixin.table_filters == {}
        assert mixin.table_selected_rows == []
        assert mixin.table_page == 1
        assert mixin.table_total_pages == 1
        assert mixin.table_rows == []
        assert mixin.table_loading is False

    def test_custom_defaults(self):
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            table_default_sort = "name"
            table_default_sort_desc = True
            table_page_size = 10

        m = MyMixin()
        m.init_table_state()
        assert m.table_sort_by == "name"
        assert m.table_sort_desc is True


class TestDataTableMixinSort:
    """Sort event handler."""

    def test_sort_sets_column(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_sort("name")
        assert m.table_sort_by == "name"
        assert m.table_sort_desc is False

    def test_sort_toggles_direction(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_sort("name")
        assert m.table_sort_desc is False
        m.on_table_sort("name")
        assert m.table_sort_desc is True

    def test_sort_resets_on_new_column(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_sort("name")
        m.on_table_sort("name")  # now desc
        m.on_table_sort("email")  # new column -> asc
        assert m.table_sort_by == "email"
        assert m.table_sort_desc is False


class TestDataTableMixinSearch:
    """Search event handler."""

    def test_search_sets_query(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_search("alice")
        assert m.table_search_query == "alice"

    def test_search_resets_page(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_page = 3
        m.on_table_search("test")
        assert m.table_page == 1


class TestDataTableMixinFilter:
    """Filter event handler."""

    def test_filter_sets_value(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_filter("active", column="status")
        assert m.table_filters["status"] == "active"

    def test_filter_resets_page(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_page = 3
        m.on_table_filter("test", column="name")
        assert m.table_page == 1

    def test_filter_empty_removes(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_filter("active", column="status")
        m.on_table_filter("", column="status")
        assert "status" not in m.table_filters


class TestDataTableMixinSelect:
    """Selection event handler."""

    def test_select_toggles_on(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_select("1")
        assert "1" in m.table_selected_rows

    def test_select_toggles_off(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_select("1")
        m.on_table_select("1")
        assert "1" not in m.table_selected_rows

    def test_select_all(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_rows = [{"id": 1}, {"id": 2}, {"id": 3}]
        m.on_table_select("__all__")
        assert len(m.table_selected_rows) == 3

    def test_deselect_all(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_rows = [{"id": 1}, {"id": 2}, {"id": 3}]
        m.table_selected_rows = ["1", "2", "3"]
        m.on_table_select("__all__")
        assert len(m.table_selected_rows) == 0


class TestDataTableMixinPage:
    """Pagination event handler."""

    def test_page_sets_number(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_page("3")
        assert m.table_page == 3


class TestDataTableMixinContext:
    """get_table_context returns complete dict for template tag."""

    def test_context_keys(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert "rows" in ctx
        assert "columns" in ctx
        assert "sort_by" in ctx
        assert "sort_desc" in ctx
        assert "selectable" in ctx
        assert "selected_rows" in ctx
        assert "search" in ctx
        assert "search_query" in ctx
        assert "paginate" in ctx
        assert "page" in ctx
        assert "total_pages" in ctx
        assert "loading" in ctx
        assert "filters" in ctx
        assert "striped" in ctx
        assert "compact" in ctx

    def test_context_values_match_state(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_selectable = True
        m.table_searchable_fields = ["name"]
        m.init_table_state()
        m.table_sort_by = "name"
        m.table_sort_desc = True
        m.table_search_query = "alice"
        ctx = m.get_table_context()
        assert ctx["sort_by"] == "name"
        assert ctx["sort_desc"] is True
        assert ctx["search_query"] == "alice"
        assert ctx["selectable"] is True
        assert ctx["search"] is True  # because searchable_fields is set


class TestDataTableMixinQueryset:
    """Queryset pipeline helpers."""

    def test_apply_table_sort_ascending(self):
        from djust_components.mixins.data_table import DataTableMixin

        class FakeQS(list):
            def order_by(self, *args):
                self._ordered = args
                return self

        m = DataTableMixin()
        m.init_table_state()
        m.table_sort_by = "name"
        m.table_sort_desc = False
        qs = FakeQS()
        result = m._apply_table_sort(qs)
        assert result._ordered == ("name",)

    def test_apply_table_sort_descending(self):
        from djust_components.mixins.data_table import DataTableMixin

        class FakeQS(list):
            def order_by(self, *args):
                self._ordered = args
                return self

        m = DataTableMixin()
        m.init_table_state()
        m.table_sort_by = "name"
        m.table_sort_desc = True
        qs = FakeQS()
        result = m._apply_table_sort(qs)
        assert result._ordered == ("-name",)

    def test_apply_table_sort_no_sort(self):
        from djust_components.mixins.data_table import DataTableMixin

        class FakeQS(list):
            def order_by(self, *args):
                self._ordered = args
                return self

        m = DataTableMixin()
        m.init_table_state()
        m.table_sort_by = ""
        qs = FakeQS()
        result = m._apply_table_sort(qs)
        assert result is qs  # unchanged

    def test_apply_table_search(self):
        from djust_components.mixins.data_table import DataTableMixin

        class FakeQS(list):
            def filter(self, *args, **kwargs):
                self._filtered = (args, kwargs)
                return self

        m = DataTableMixin()
        m.table_searchable_fields = ["name", "email"]
        m.init_table_state()
        m.table_search_query = "alice"
        qs = FakeQS()
        result = m._apply_table_search(qs)
        # Should have called filter with a Q object
        assert hasattr(result, "_filtered")
        assert len(result._filtered[0]) == 1  # one Q object

    def test_apply_table_pagination(self):
        from djust_components.mixins.data_table import DataTableMixin

        class FakeQS(list):
            def __init__(self, items):
                super().__init__(items)

            def count(self):
                return len(self)

            def __getitem__(self, key):
                if isinstance(key, slice):
                    result = FakeQS(super().__getitem__(key))
                    return result
                return super().__getitem__(key)

        m = DataTableMixin()
        m.table_page_size = 2
        m.init_table_state()
        m.table_page = 1
        qs = FakeQS(list(range(5)))
        result = m._apply_table_pagination(qs)
        assert len(result) == 2
        assert m.table_total_pages == 3  # ceil(5/2)


# ===========================================================================
# D. CSS Tests
# ===========================================================================


class TestDataTableCSS:
    """CSS class definitions exist."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        import pathlib
        css_path = pathlib.Path(__file__).parent.parent / "src" / "djust_components" / "static" / "djust_components" / "components.css"
        self.css = css_path.read_text()

    def test_container_class(self):
        assert ".data-table-container" in self.css

    def test_search_class(self):
        assert ".data-table-search" in self.css

    def test_striped_class(self):
        assert ".data-table-striped" in self.css

    def test_compact_class(self):
        assert ".data-table-compact" in self.css

    def test_selected_row_highlight(self):
        assert 'aria-selected="true"' in self.css

    def test_existing_wrapper_unchanged(self):
        assert ".data-table-wrapper" in self.css

    def test_filter_class(self):
        assert ".data-table-filter" in self.css

    def test_checkbox_class(self):
        assert ".data-table-checkbox" in self.css


# ===========================================================================
# E. Export Tests
# ===========================================================================


class TestExports:
    def test_mixin_importable(self):
        from djust_components import DataTableMixin
        assert DataTableMixin is not None

    def test_mixin_in_all(self):
        import djust_components
        assert "DataTableMixin" in djust_components.__all__


# ===========================================================================
# F. Phase 2 — Inline Cell Editing
# ===========================================================================


class TestInlineCellEditing:
    """Inline editing on individual cells."""

    def test_editable_cells_have_data_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"])
        assert 'data-editable="true"' in html

    def test_non_editable_cells_no_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"])
        # Split by rows and check email cells don't have data-editable
        parts = html.split("</tr>")
        for p in parts:
            if "alice@example.com" in p:
                # The email td should not be editable
                email_td_idx = p.find("alice@example.com")
                preceding = p[:email_td_idx]
                # Check that the td containing email does not have data-editable
                last_td = preceding.rfind("<td")
                td_tag = preceding[last_td:] if last_td >= 0 else ""
                assert 'data-editable="true"' not in td_tag

    def test_edit_event_on_wrapper(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"])
        assert 'data-edit-event="table_cell_edit"' in html

    def test_edit_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"], edit_event="my_edit")
        assert 'data-edit-event="my_edit"' in html

    def test_hidden_trigger_present(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"])
        assert "data-table-edit-trigger" in html

    def test_no_editable_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'data-editable="true"' not in html

    def test_editable_cell_has_col_key(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"])
        assert 'data-col-key="name"' in html


# ===========================================================================
# G. Phase 2 — Column Resize
# ===========================================================================


class TestColumnResize:
    """Column resize via drag handles."""

    def test_resizable_attr_on_wrapper(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       resizable=True)
        assert 'data-resizable="true"' in html

    def test_no_resizable_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'data-resizable' not in html

    def test_header_has_resizable_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       resizable=True)
        # Each th should have data-resizable
        parts = html.split("</th>")
        th_parts = [p for p in parts if "<th" in p and "Name" in p]
        assert len(th_parts) > 0
        assert 'data-resizable="true"' in th_parts[0]


# ===========================================================================
# H. Phase 2 — Column Reorder
# ===========================================================================


class TestColumnReorder:
    """Column reorder via drag-and-drop."""

    def test_reorderable_attr_on_wrapper(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       reorderable=True)
        assert 'data-reorderable="true"' in html

    def test_headers_draggable(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       reorderable=True)
        assert 'draggable="true"' in html

    def test_headers_have_col_key(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       reorderable=True)
        assert 'data-col-key="name"' in html
        assert 'data-col-key="email"' in html

    def test_reorder_trigger_present(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       reorderable=True)
        assert "data-table-reorder-trigger" in html

    def test_reorder_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       reorderable=True, reorder_event="my_reorder")
        assert 'data-reorder-event="my_reorder"' in html

    def test_no_reorderable_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert 'draggable="true"' not in html


# ===========================================================================
# I. Phase 2 — Frozen Columns
# ===========================================================================


class TestFrozenColumns:
    """Frozen left/right columns with position:sticky."""

    def test_frozen_left_class(self):
        cols = [
            {"key": "id", "label": "ID"},
            {"key": "name", "label": "Name"},
            {"key": "email", "label": "Email"},
        ]
        rows = [{"id": 1, "name": "Alice", "email": "a@b.com"}]
        html = _render(rows=rows, columns=cols, frozen_left=1)
        assert "data-table-frozen-left" in html

    def test_frozen_right_class(self):
        cols = [
            {"key": "id", "label": "ID"},
            {"key": "name", "label": "Name"},
            {"key": "email", "label": "Email"},
        ]
        rows = [{"id": 1, "name": "Alice", "email": "a@b.com"}]
        html = _render(rows=rows, columns=cols, frozen_right=1)
        assert "data-table-frozen-right" in html

    def test_scroll_wrapper(self):
        cols = [{"key": "name", "label": "Name"}]
        html = _render(rows=SAMPLE_ROWS, columns=cols, frozen_left=1)
        assert "data-table-scroll" in html

    def test_no_scroll_wrapper_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-scroll" not in html

    def test_no_frozen_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-frozen-left" not in html
        assert "data-table-frozen-right" not in html


# ===========================================================================
# J. Phase 2 — Column Visibility
# ===========================================================================


class TestColumnVisibility:
    """Column visibility dropdown toggle."""

    def test_visibility_dropdown_present(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       column_visibility=True)
        assert "data-table-visibility-btn" in html
        assert "data-table-visibility-menu" in html

    def test_visibility_items_per_column(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       column_visibility=True)
        assert "data-table-visibility-item" in html
        # Should have one checkbox per column
        assert html.count("data-table-visibility-item") == 2

    def test_visibility_trigger_present(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       column_visibility=True)
        assert "data-table-visibility-trigger" in html

    def test_no_visibility_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-visibility-btn" not in html

    def test_visibility_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       column_visibility=True, visibility_event="my_vis")
        assert 'data-visibility-event="my_vis"' in html


# ===========================================================================
# K. Phase 2 — Density Toggle
# ===========================================================================


class TestDensityToggle:
    """Density toggle between compact/comfortable/spacious."""

    def test_density_toggle_buttons(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       density_toggle=True)
        assert "data-table-density-toggle" in html
        assert "Compact" in html
        assert "Comfortable" in html
        assert "Spacious" in html

    def test_density_default_comfortable_active(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       density_toggle=True)
        # The comfortable button should be active
        parts = html.split("</button>")
        comfortable_btn = [p for p in parts if "Comfortable" in p][0]
        assert "active" in comfortable_btn

    def test_density_compact_applies_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       density="compact")
        assert "data-table-compact" in html

    def test_density_spacious_applies_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       density="spacious")
        assert "data-table-spacious" in html

    def test_density_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       density_toggle=True, density_event="my_density")
        assert 'dj-click="my_density"' in html

    def test_no_density_toggle_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-density-toggle" not in html


# ===========================================================================
# L. Phase 2 — Responsive Card Collapse
# ===========================================================================


class TestResponsiveCards:
    """Responsive card mode for narrow viewports."""

    def test_responsive_wrapper_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       responsive_cards=True)
        assert "data-table-responsive" in html

    def test_cells_have_data_label(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       responsive_cards=True)
        assert 'data-label="Name"' in html
        assert 'data-label="Email"' in html

    def test_no_responsive_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-responsive" not in html
        assert "data-label=" not in html


# ===========================================================================
# M. Phase 2 — Editable Row Mode
# ===========================================================================


class TestEditableRowMode:
    """Full row edit mode with Edit/Save/Cancel buttons."""

    def test_edit_button_per_row(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True)
        assert "Edit</button>" in html
        # Should have one Edit button per row
        assert html.count("Edit</button>") == 3

    def test_actions_column_header(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True)
        assert "Actions</th>" in html

    def test_editing_row_has_inputs(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True, editing_rows=[1])
        # The editing row should have input elements
        parts = html.split("</tr>")
        editing_row = [p for p in parts if "data-table-row-editing" in p]
        assert len(editing_row) > 0
        assert '<input type="text"' in editing_row[0]

    def test_editing_row_has_save_cancel(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True, editing_rows=[1])
        assert "Save</button>" in html
        assert "Cancel</button>" in html

    def test_non_editing_rows_still_have_edit(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True, editing_rows=[1])
        # Other rows should still have Edit button
        assert "Edit</button>" in html

    def test_edit_row_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True, edit_row_event="my_edit_row")
        assert 'dj-click="my_edit_row"' in html

    def test_save_row_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True, editing_rows=[1],
                       save_row_event="my_save")
        assert 'dj-click="my_save"' in html

    def test_cancel_row_event_custom(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_rows=True, editing_rows=[1],
                       cancel_row_event="my_cancel")
        assert 'dj-click="my_cancel"' in html

    def test_no_editable_rows_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "Edit</button>" not in html
        assert "Actions</th>" not in html

    def test_empty_state_colspan_includes_actions(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS,
                       editable_rows=True)
        # colspan should be 3 (2 columns + 1 actions)
        assert 'colspan="3"' in html


# ===========================================================================
# N. Phase 2 — Mixin Phase 2 Handlers
# ===========================================================================


class TestMixinPhase2Init:
    """Phase 2 mixin state initialization."""

    def test_editing_rows_init(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        assert m.table_editing_rows == []

    def test_column_order_init(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        assert m.table_column_order == ["name", "email"]

    def test_visible_columns_init(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        assert m.table_visible_columns == ["name", "email"]

    def test_density_init(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        assert m.table_current_density == "comfortable"


class TestMixinCellEdit:
    """Inline cell edit handler."""

    def test_cell_edit_calls_handler(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            def __init__(self):
                self.edit_log = []
            def handle_cell_edit(self, row_key, column, value):
                self.edit_log.append((row_key, column, value))

        m = MyMixin()
        m.init_table_state()
        m.on_table_cell_edit(json.dumps({"row_key": "1", "column": "name", "value": "New"}))
        assert m.edit_log == [("1", "name", "New")]

    def test_cell_edit_ignores_bad_json(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_cell_edit("not json")  # Should not raise


class TestMixinReorder:
    """Column reorder handler."""

    def test_reorder_updates_order(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.on_table_reorder("email,name")
        assert m.table_column_order == ["email", "name"]


class TestMixinVisibility:
    """Column visibility handler."""

    def test_visibility_updates(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.on_table_visibility("name")
        assert m.table_visible_columns == ["name"]


class TestMixinDensity:
    """Density toggle handler."""

    def test_density_sets_compact(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_density("compact")
        assert m.table_current_density == "compact"

    def test_density_sets_spacious(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_density("spacious")
        assert m.table_current_density == "spacious"

    def test_density_ignores_invalid(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_density("invalid")
        assert m.table_current_density == "comfortable"


class TestMixinRowEdit:
    """Row edit mode handlers."""

    def test_row_edit_adds_to_editing(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_row_edit("1")
        assert "1" in m.table_editing_rows

    def test_row_cancel_removes(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_row_edit("1")
        m.on_table_row_cancel("1")
        assert "1" not in m.table_editing_rows

    def test_row_save_removes_and_calls_handler(self):
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            def __init__(self):
                self.saved = []
            def handle_row_save(self, row_key, data):
                self.saved.append(row_key)

        m = MyMixin()
        m.init_table_state()
        m.on_table_row_edit("1")
        m.on_table_row_save("1")
        assert "1" not in m.table_editing_rows
        assert m.saved == ["1"]


class TestMixinPhase2Context:
    """get_table_context includes Phase 2 fields."""

    def test_context_has_phase2_keys(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert "editable_columns" in ctx
        assert "edit_event" in ctx
        assert "resizable" in ctx
        assert "reorderable" in ctx
        assert "frozen_left" in ctx
        assert "frozen_right" in ctx
        assert "column_visibility" in ctx
        assert "density" in ctx
        assert "density_toggle" in ctx
        assert "responsive_cards" in ctx
        assert "editable_rows" in ctx
        assert "editing_rows" in ctx

    def test_context_defaults_preserve_phase1(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert ctx["editable_columns"] == []
        assert ctx["resizable"] is False
        assert ctx["reorderable"] is False
        assert ctx["frozen_left"] == 0
        assert ctx["frozen_right"] == 0
        assert ctx["column_visibility"] is False
        assert ctx["density"] == "comfortable"
        assert ctx["density_toggle"] is False
        assert ctx["responsive_cards"] is False
        assert ctx["editable_rows"] is False
        assert ctx["editing_rows"] == []


# ===========================================================================
# Phase 3 — Row Expansion
# ===========================================================================


class TestRowExpansion:
    """Row expansion with detail rows."""

    def test_expand_column_header(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True)
        assert "data-table-expand-col" in html

    def test_expand_button_per_row(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True)
        assert "data-table-expand-btn" in html
        assert html.count("data-table-expand-btn") == 3

    def test_expand_event_fires(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True, expand_event="my_expand")
        assert 'dj-click="my_expand"' in html

    def test_expanded_row_has_detail(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True, expanded_rows=[1])
        assert "data-table-detail-row" in html
        assert "data-table-detail-content" in html

    def test_collapsed_row_no_detail(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True, expanded_rows=[])
        assert "data-table-detail-row" not in html

    def test_aria_expanded_true(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True, expanded_rows=[1])
        assert 'aria-expanded="true"' in html

    def test_aria_expanded_false(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       expandable=True, expanded_rows=[])
        assert 'aria-expanded="false"' in html

    def test_no_expand_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-expand-col" not in html
        assert "data-table-expand-btn" not in html


# ===========================================================================
# Phase 3 — Bulk Actions
# ===========================================================================


class TestBulkActions:
    """Bulk action toolbar when rows selected."""

    def test_bulk_bar_shows_when_selected(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, selected_rows=[1],
                       bulk_actions=[{"key": "delete", "label": "Delete"}])
        assert "data-table-bulk-bar" in html
        assert "1 selected" in html
        assert "Delete" in html

    def test_bulk_bar_hidden_when_none_selected(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, selected_rows=[],
                       bulk_actions=[{"key": "delete", "label": "Delete"}])
        assert "data-table-bulk-bar" not in html

    def test_bulk_action_event(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, selected_rows=[1],
                       bulk_actions=[{"key": "delete", "label": "Delete"}],
                       bulk_action_event="my_bulk")
        assert 'dj-click="my_bulk"' in html

    def test_multiple_bulk_actions(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, selected_rows=[1, 2],
                       bulk_actions=[
                           {"key": "delete", "label": "Delete"},
                           {"key": "archive", "label": "Archive"},
                       ])
        assert "Delete" in html
        assert "Archive" in html
        assert "2 selected" in html

    def test_no_bulk_actions_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       selectable=True, selected_rows=[1])
        assert "data-table-bulk-bar" not in html


# ===========================================================================
# Phase 3 — Export
# ===========================================================================


class TestExport:
    """Export buttons in toolbar."""

    def test_export_buttons_rendered(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       exportable=True)
        assert "data-table-export-btn" in html
        assert "Export CSV" in html
        assert "Export JSON" in html

    def test_export_event(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       exportable=True, export_event="my_export")
        assert 'dj-click="my_export"' in html

    def test_custom_export_formats(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       exportable=True, export_formats=["csv"])
        assert "Export CSV" in html
        assert "Export JSON" not in html

    def test_no_export_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-export-btn" not in html


# ===========================================================================
# Phase 3 — Row Grouping
# ===========================================================================


class TestRowGrouping:
    """Row grouping by column value."""

    def test_group_headers_rendered(self):
        rows = [
            {"id": 1, "name": "Alice", "dept": "Eng"},
            {"id": 2, "name": "Bob", "dept": "Eng"},
            {"id": 3, "name": "Charlie", "dept": "Sales"},
        ]
        cols = [{"key": "name", "label": "Name"}, {"key": "dept", "label": "Dept"}]
        html = _render(rows=rows, columns=cols, group_by="dept")
        assert "data-table-group-header" in html
        assert "Eng" in html
        assert "Sales" in html

    def test_group_counts(self):
        rows = [
            {"id": 1, "name": "Alice", "dept": "Eng"},
            {"id": 2, "name": "Bob", "dept": "Eng"},
            {"id": 3, "name": "Charlie", "dept": "Sales"},
        ]
        cols = [{"key": "name", "label": "Name"}, {"key": "dept", "label": "Dept"}]
        html = _render(rows=rows, columns=cols, group_by="dept")
        assert "(2)" in html  # Eng count
        assert "(1)" in html  # Sales count

    def test_collapsed_group_hides_rows(self):
        rows = [
            {"id": 1, "name": "Alice", "dept": "Eng"},
            {"id": 2, "name": "Bob", "dept": "Sales"},
        ]
        cols = [{"key": "name", "label": "Name"}, {"key": "dept", "label": "Dept"}]
        html = _render(rows=rows, columns=cols, group_by="dept",
                       collapsed_groups=["Eng"])
        assert "data-table-group-collapsed" in html
        # Alice's row should be hidden (not rendered)
        assert "Alice" not in html
        assert "Bob" in html

    def test_group_toggle_event(self):
        rows = [{"id": 1, "name": "Alice", "dept": "Eng"}]
        cols = [{"key": "name", "label": "Name"}, {"key": "dept", "label": "Dept"}]
        html = _render(rows=rows, columns=cols, group_by="dept",
                       group_toggle_event="my_toggle")
        assert 'dj-click="my_toggle"' in html

    def test_no_grouping_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-group-header" not in html


# ===========================================================================
# Phase 3 — Custom Cell Renderers
# ===========================================================================


class TestCellRenderers:
    """Custom cell renderers via cell_template."""

    def test_badge_renderer(self):
        cols = [{"key": "status", "label": "Status", "cell_template": "badge"}]
        rows = [{"id": 1, "status": "Active"}]
        html = _render(rows=rows, columns=cols)
        assert "cell-renderer-badge" in html
        assert 'data-value="Active"' in html

    def test_progress_renderer(self):
        cols = [{"key": "progress", "label": "Progress", "cell_template": "progress"}]
        rows = [{"id": 1, "progress": "75"}]
        html = _render(rows=rows, columns=cols)
        assert "cell-renderer-progress" in html

    def test_avatar_renderer(self):
        cols = [{"key": "initials", "label": "User", "cell_template": "avatar"}]
        rows = [{"id": 1, "initials": "AB"}]
        html = _render(rows=rows, columns=cols)
        assert "cell-renderer-avatar" in html

    def test_no_renderer_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "cell-renderer" not in html


# ===========================================================================
# Phase 3 — Keyboard Navigation
# ===========================================================================


class TestKeyboardNav:
    """Keyboard navigation attributes."""

    def test_keyboard_nav_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       keyboard_nav=True)
        assert 'data-keyboard-nav="true"' in html
        assert 'tabindex="0"' in html

    def test_no_keyboard_nav_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-keyboard-nav" not in html


# ===========================================================================
# Phase 3 — Virtual Scrolling
# ===========================================================================


class TestVirtualScroll:
    """Virtual scrolling attributes."""

    def test_virtual_scroll_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       virtual_scroll=True)
        assert 'data-virtual-scroll="true"' in html

    def test_virtual_row_height(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       virtual_scroll=True, virtual_row_height=50)
        assert 'data-virtual-row-height="50"' in html

    def test_virtual_buffer(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       virtual_scroll=True, virtual_buffer=10)
        assert 'data-virtual-buffer="10"' in html

    def test_no_virtual_scroll_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-virtual-scroll" not in html


# ===========================================================================
# Phase 3 — Server-Side Mode
# ===========================================================================


class TestServerMode:
    """Server-side mode attribute."""

    def test_server_mode_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       server_mode=True)
        assert 'data-server-mode="true"' in html

    def test_no_server_mode_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-server-mode" not in html


# ===========================================================================
# Phase 3 — Faceted Filtering
# ===========================================================================


class TestFacetedFiltering:
    """Faceted filtering with counts."""

    def test_facet_counts_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       facets=True, facet_counts={"name": {"Alice": 1, "Bob": 1}})
        assert "data-facet-counts" in html

    def test_no_facets_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-facet-counts" not in html


# ===========================================================================
# Phase 3 — State Persistence
# ===========================================================================


class TestStatePersistence:
    """State persistence via localStorage key."""

    def test_persist_key_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       persist_key="user_table")
        assert 'data-persist-key="user_table"' in html

    def test_no_persist_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-persist-key" not in html


# ===========================================================================
# Phase 3 — Column Pinning
# ===========================================================================


class TestColumnPinning:
    """Column pinning via per-column config."""

    def test_pinned_left(self):
        cols = [
            {"key": "id", "label": "ID", "pinned": "left"},
            {"key": "name", "label": "Name"},
        ]
        rows = [{"id": 1, "name": "Alice"}]
        html = _render(rows=rows, columns=cols)
        assert "data-table-pinned-left" in html

    def test_pinned_right(self):
        cols = [
            {"key": "name", "label": "Name"},
            {"key": "actions", "label": "Actions", "pinned": "right"},
        ]
        rows = [{"id": 1, "name": "Alice", "actions": "..."}]
        html = _render(rows=rows, columns=cols)
        assert "data-table-pinned-right" in html

    def test_no_pinning_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-pinned-left" not in html
        assert "data-table-pinned-right" not in html


# ===========================================================================
# Phase 3 — Print-Friendly Mode
# ===========================================================================


class TestPrintMode:
    """Print-friendly mode."""

    def test_printable_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       printable=True)
        assert "data-table-printable" in html

    def test_no_printable_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-printable" not in html


# ===========================================================================
# Phase 3 — Column Statistics
# ===========================================================================


class TestColumnStats:
    """Column statistics footer."""

    def test_stats_footer_rendered(self):
        cols = [
            {"key": "name", "label": "Name"},
            {"key": "score", "label": "Score", "stats": True},
        ]
        rows = [
            {"id": 1, "name": "Alice", "score": 90},
            {"id": 2, "name": "Bob", "score": 80},
        ]
        stats = {"score": {"min": 80, "max": 90, "avg": 85, "sum": 170, "count": 2}}
        html = _render(rows=rows, columns=cols, column_stats=stats)
        assert "data-table-stats-row" in html
        assert "80" in html  # min
        assert "90" in html  # max
        assert "85" in html  # avg

    def test_no_stats_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-stats-row" not in html


# ===========================================================================
# Phase 3 — Mixin Event Handlers
# ===========================================================================


class TestMixinExpand:
    """Row expansion mixin handler."""

    def test_expand_toggles_on(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_expand("1")
        assert "1" in m.table_expanded_rows

    def test_expand_toggles_off(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_expand("1")
        m.on_table_expand("1")
        assert "1" not in m.table_expanded_rows


class TestMixinBulkAction:
    """Bulk action mixin handler."""

    def test_bulk_action_calls_handler(self):
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            def __init__(self):
                self.actions = []
            def handle_bulk_action(self, action, selected):
                self.actions.append((action, selected))

        m = MyMixin()
        m.init_table_state()
        m.table_selected_rows = ["1", "2"]
        m.on_table_bulk_action("delete")
        assert m.actions == [("delete", ["1", "2"])]


class TestMixinExport:
    """Export mixin handler."""

    def test_export_csv(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.table_rows = SAMPLE_ROWS
        m.on_table_export("csv")
        assert hasattr(m, "table_export_data")
        assert "Alice" in m.table_export_data
        assert m.table_export_format == "csv"

    def test_export_json(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.table_rows = SAMPLE_ROWS
        m.on_table_export("json")
        data = json.loads(m.table_export_data)
        assert len(data) == 3
        assert data[0]["name"] == "Alice"


class TestMixinGrouping:
    """Grouping mixin handlers."""

    def test_group_sets_column(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_group("dept")
        assert m.table_current_group_by == "dept"

    def test_group_toggle(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.on_table_group_toggle("Eng")
        assert "Eng" in m.table_collapsed_groups
        m.on_table_group_toggle("Eng")
        assert "Eng" not in m.table_collapsed_groups

    def test_group_rows_helper(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_current_group_by = "dept"
        rows = [
            {"name": "Alice", "dept": "Eng"},
            {"name": "Bob", "dept": "Sales"},
            {"name": "Charlie", "dept": "Eng"},
        ]
        groups = m._group_rows(rows)
        assert len(groups) == 2
        assert groups[0][0] == "Eng"
        assert len(groups[0][1]) == 2
        assert groups[1][0] == "Sales"
        assert len(groups[1][1]) == 1


class TestMixinFacets:
    """Facet counts helper."""

    def test_get_facet_counts(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = [
            {"key": "status", "label": "Status", "filterable": True},
            {"key": "name", "label": "Name"},
        ]
        m.init_table_state()
        m.table_rows = [
            {"status": "active", "name": "Alice"},
            {"status": "active", "name": "Bob"},
            {"status": "inactive", "name": "Charlie"},
        ]
        counts = m.get_facet_counts()
        assert counts["status"]["active"] == 2
        assert counts["status"]["inactive"] == 1


class TestMixinColumnStats:
    """Column statistics helper."""

    def test_get_column_stats(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = [
            {"key": "name", "label": "Name"},
            {"key": "score", "label": "Score", "stats": True},
        ]
        m.init_table_state()
        m.table_rows = [
            {"name": "Alice", "score": 90},
            {"name": "Bob", "score": 80},
            {"name": "Charlie", "score": 100},
        ]
        stats = m.get_column_stats()
        assert stats["score"]["min"] == 80
        assert stats["score"]["max"] == 100
        assert stats["score"]["avg"] == 90.0
        assert stats["score"]["sum"] == 270
        assert stats["score"]["count"] == 3

    def test_stats_empty_column(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = [
            {"key": "score", "label": "Score", "stats": True},
        ]
        m.init_table_state()
        m.table_rows = [{"score": "not_a_number"}]
        stats = m.get_column_stats()
        assert stats["score"]["count"] == 0


class TestMixinServerMode:
    """Server mode skips client pipeline."""

    def test_server_mode_calls_refresh_server(self):
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            table_server_mode = True
            def __init__(self):
                self.server_called = False
            def refresh_table_server(self):
                self.server_called = True

        m = MyMixin()
        m.init_table_state()
        m.refresh_table()
        assert m.server_called


class TestMixinPhase3Init:
    """Phase 3 mixin state initialization."""

    def test_expanded_rows_init(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        assert m.table_expanded_rows == []

    def test_collapsed_groups_init(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        assert m.table_collapsed_groups == []


class TestMixinPhase3Context:
    """get_table_context includes Phase 3 fields."""

    def test_context_has_phase3_keys(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert "expandable" in ctx
        assert "expanded_rows" in ctx
        assert "bulk_actions" in ctx
        assert "exportable" in ctx
        assert "group_by" in ctx
        assert "keyboard_nav" in ctx
        assert "virtual_scroll" in ctx
        assert "server_mode" in ctx
        assert "facets" in ctx
        assert "persist_key" in ctx
        assert "printable" in ctx
        assert "column_stats" in ctx

    def test_context_defaults(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert ctx["expandable"] is False
        assert ctx["expanded_rows"] == []
        assert ctx["bulk_actions"] == []
        assert ctx["exportable"] is False
        assert ctx["group_by"] == ""
        assert ctx["keyboard_nav"] is False
        assert ctx["virtual_scroll"] is False
        assert ctx["server_mode"] is False
        assert ctx["facets"] is False
        assert ctx["persist_key"] == ""
        assert ctx["printable"] is False
        assert ctx["column_stats"] == {}


# ===========================================================================
# Phase 3 — Template Tag
# ===========================================================================


class TestTemplateTagPhase3:
    """Template tag includes Phase 3 params."""

    def test_phase3_params_in_context(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            expandable=True, expanded_rows=[1],
            bulk_actions=[{"key": "delete", "label": "Delete"}],
            exportable=True, export_formats=["csv"],
            group_by="name", keyboard_nav=True,
            virtual_scroll=True, virtual_row_height=50,
            server_mode=True, facets=True,
            persist_key="test", printable=True,
            column_stats={"name": {"count": 3}},
        )
        assert ctx["expandable"] is True
        assert ctx["expanded_rows"] == [1]
        assert ctx["bulk_actions"] == [{"key": "delete", "label": "Delete"}]
        assert ctx["exportable"] is True
        assert ctx["export_formats"] == ["csv"]
        assert ctx["group_by"] == "name"
        assert ctx["keyboard_nav"] is True
        assert ctx["virtual_scroll"] is True
        assert ctx["virtual_row_height"] == 50
        assert ctx["server_mode"] is True
        assert ctx["facets"] is True
        assert ctx["persist_key"] == "test"
        assert ctx["printable"] is True
        assert ctx["column_stats"] == {"name": {"count": 3}}

    def test_phase3_defaults(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(rows=[], columns=[])
        assert ctx["expandable"] is False
        assert ctx["expanded_rows"] == []
        assert ctx["bulk_actions"] == []
        assert ctx["exportable"] is False
        assert ctx["export_formats"] == ["csv", "json"]
        assert ctx["group_by"] == ""
        assert ctx["keyboard_nav"] is False
        assert ctx["virtual_scroll"] is False
        assert ctx["virtual_row_height"] == 40
        assert ctx["virtual_buffer"] == 5
        assert ctx["server_mode"] is False
        assert ctx["facets"] is False
        assert ctx["facet_counts"] == {}
        assert ctx["persist_key"] == ""
        assert ctx["printable"] is False
        assert ctx["column_stats"] == {}


# ===========================================================================
# Phase 3 — CSS
# ===========================================================================


class TestPhase3CSS:
    """Phase 3 CSS class definitions exist."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        import pathlib
        css_path = pathlib.Path(__file__).parent.parent / "src" / "djust_components" / "static" / "djust_components" / "components.css"
        self.css = css_path.read_text()

    def test_expand_classes(self):
        assert ".data-table-expand-btn" in self.css
        assert ".data-table-detail-row" in self.css

    def test_bulk_action_classes(self):
        assert ".data-table-bulk-bar" in self.css
        assert ".data-table-bulk-btn" in self.css

    def test_export_classes(self):
        assert ".data-table-export-btn" in self.css

    def test_group_classes(self):
        assert ".data-table-group-header" in self.css
        assert ".data-table-group-toggle" in self.css

    def test_cell_renderer_classes(self):
        assert ".cell-renderer-badge" in self.css
        assert ".cell-renderer-progress" in self.css
        assert ".cell-renderer-avatar" in self.css

    def test_pinned_classes(self):
        assert ".data-table-pinned-left" in self.css
        assert ".data-table-pinned-right" in self.css

    def test_stats_classes(self):
        assert ".data-table-stats-row" in self.css
        assert ".data-table-stats-cell" in self.css

    def test_print_rules(self):
        assert "@media print" in self.css
        assert ".data-table-printable" in self.css


# ===========================================================================
# O. Phase 2 — Template Tag Phase 2 Params
# ===========================================================================


class TestTemplateTagPhase2:
    """Template tag passes Phase 2 params."""

    def test_phase2_defaults(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(rows=[], columns=[])
        assert ctx["editable_columns"] == []
        assert ctx["resizable"] is False
        assert ctx["reorderable"] is False
        assert ctx["frozen_left"] == 0
        assert ctx["frozen_right"] == 0
        assert ctx["column_visibility"] is False
        assert ctx["density"] == "comfortable"
        assert ctx["density_toggle"] is False
        assert ctx["responsive_cards"] is False
        assert ctx["editable_rows"] is False
        assert ctx["editing_rows"] == []

    def test_phase2_all_params(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            editable_columns=["name"], edit_event="my_edit",
            resizable=True, reorderable=True, reorder_event="my_reorder",
            frozen_left=1, frozen_right=1,
            column_visibility=True, visibility_event="my_vis",
            density="compact", density_toggle=True, density_event="my_density",
            responsive_cards=True,
            editable_rows=True, edit_row_event="my_edit_row",
            save_row_event="my_save", cancel_row_event="my_cancel",
            editing_rows=["1"],
        )
        assert ctx["editable_columns"] == ["name"]
        assert ctx["edit_event"] == "my_edit"
        assert ctx["resizable"] is True
        assert ctx["reorderable"] is True
        assert ctx["reorder_event"] == "my_reorder"
        assert ctx["frozen_left"] == 1
        assert ctx["frozen_right"] == 1
        assert ctx["column_visibility"] is True
        assert ctx["visibility_event"] == "my_vis"
        assert ctx["density"] == "compact"
        assert ctx["density_toggle"] is True
        assert ctx["density_event"] == "my_density"
        assert ctx["responsive_cards"] is True
        assert ctx["editable_rows"] is True
        assert ctx["edit_row_event"] == "my_edit_row"
        assert ctx["save_row_event"] == "my_save"
        assert ctx["cancel_row_event"] == "my_cancel"
        assert ctx["editing_rows"] == ["1"]


# ===========================================================================
# P. Phase 2 — CSS Tests
# ===========================================================================


class TestPhase2CSS:
    """Phase 2 CSS class definitions exist."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        import pathlib
        css_path = pathlib.Path(__file__).parent.parent / "src" / "djust_components" / "static" / "djust_components" / "components.css"
        self.css = css_path.read_text()

    def test_frozen_left_class(self):
        assert ".data-table-frozen-left" in self.css

    def test_frozen_right_class(self):
        assert ".data-table-frozen-right" in self.css

    def test_spacious_class(self):
        assert ".data-table-spacious" in self.css

    def test_scroll_class(self):
        assert ".data-table-scroll" in self.css

    def test_resize_handle(self):
        assert ".data-table-resize-handle" in self.css

    def test_cell_editing_class(self):
        assert ".data-table-cell-editing" in self.css

    def test_toolbar_class(self):
        assert ".data-table-toolbar" in self.css

    def test_visibility_dropdown(self):
        assert ".data-table-visibility-dropdown" in self.css

    def test_density_toggle(self):
        assert ".data-table-density-toggle" in self.css

    def test_row_actions(self):
        assert ".data-table-row-actions" in self.css

    def test_row_editing(self):
        assert ".data-table-row-editing" in self.css

    def test_responsive_class(self):
        assert ".data-table-responsive" in self.css

    def test_container_query(self):
        assert "@container" in self.css

    def test_media_fallback(self):
        assert "@media (max-width: 640px)" in self.css


# ===========================================================================
# Q. Phase 2 — XSS Tests for new features
# ===========================================================================


class TestPhase2XSS:
    """XSS escaping for Phase 2 user-controlled values."""

    def test_xss_in_edit_event(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       editable_columns=["name"],
                       edit_event='"><script>xss</script>')
        assert "<script>xss</script>" not in html

    def test_xss_in_reorder_event(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       reorderable=True,
                       reorder_event='"><script>xss</script>')
        assert "<script>xss</script>" not in html

    def test_xss_in_density(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       density='"><script>xss</script>')
        assert "<script>xss</script>" not in html


# ===========================================================================
# Phase 4 — Column Type Formatters
# ===========================================================================


NUMERIC_COLUMNS = [
    {"key": "name", "label": "Name"},
    {"key": "amount", "label": "Amount", "type": "number"},
]

NUMERIC_ROWS = [
    {"id": 1, "name": "Alice", "amount": 1234567},
    {"id": 2, "name": "Bob", "amount": 89.5},
]


class TestColumnTypeFormatters:
    """Column type auto-formatting."""

    def test_number_formatting(self):
        cols = [{"key": "val", "label": "Value", "type": "number"}]
        rows = [{"id": 1, "val": 1234567}]
        html = _render(rows=rows, columns=cols)
        assert "1,234,567" in html

    def test_number_with_decimals(self):
        cols = [{"key": "val", "label": "Value", "type": "number", "decimals": 2}]
        rows = [{"id": 1, "val": 1234.5}]
        html = _render(rows=rows, columns=cols)
        assert "1,234.50" in html

    def test_currency_formatting(self):
        cols = [{"key": "price", "label": "Price", "type": "currency"}]
        rows = [{"id": 1, "price": 42.5}]
        html = _render(rows=rows, columns=cols)
        assert "$42.50" in html

    def test_currency_custom_symbol(self):
        cols = [{"key": "price", "label": "Price", "type": "currency", "currency_symbol": "EUR "}]
        rows = [{"id": 1, "price": 100}]
        html = _render(rows=rows, columns=cols)
        assert "EUR 100.00" in html

    def test_percentage_formatting(self):
        cols = [{"key": "pct", "label": "%", "type": "percentage"}]
        rows = [{"id": 1, "pct": 85.123}]
        html = _render(rows=rows, columns=cols)
        assert "85.1%" in html

    def test_boolean_formatting_true(self):
        cols = [{"key": "active", "label": "Active", "type": "boolean"}]
        rows = [{"id": 1, "active": True}]
        html = _render(rows=rows, columns=cols)
        assert "Yes" in html

    def test_boolean_formatting_false(self):
        cols = [{"key": "active", "label": "Active", "type": "boolean"}]
        rows = [{"id": 1, "active": False}]
        html = _render(rows=rows, columns=cols)
        assert "No" in html

    def test_boolean_custom_labels(self):
        cols = [{"key": "active", "label": "Active", "type": "boolean",
                 "true_label": "On", "false_label": "Off"}]
        rows = [{"id": 1, "active": "1"}]
        html = _render(rows=rows, columns=cols)
        assert "On" in html

    def test_date_passthrough(self):
        """Date type with string value passes through as-is."""
        cols = [{"key": "dt", "label": "Date", "type": "date"}]
        rows = [{"id": 1, "dt": "2024-01-15"}]
        html = _render(rows=rows, columns=cols)
        assert "2024-01-15" in html

    def test_type_class_on_td(self):
        cols = [{"key": "val", "label": "Value", "type": "number"}]
        rows = [{"id": 1, "val": 42}]
        html = _render(rows=rows, columns=cols)
        assert "data-table-type-number" in html

    def test_currency_type_class(self):
        cols = [{"key": "val", "label": "Value", "type": "currency"}]
        rows = [{"id": 1, "val": 42}]
        html = _render(rows=rows, columns=cols)
        assert "data-table-type-currency" in html

    def test_boolean_type_class(self):
        cols = [{"key": "val", "label": "Value", "type": "boolean"}]
        rows = [{"id": 1, "val": True}]
        html = _render(rows=rows, columns=cols)
        assert "data-table-type-boolean" in html

    def test_no_type_no_class(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-type-" not in html

    def test_invalid_number_passthrough(self):
        cols = [{"key": "val", "label": "Value", "type": "number"}]
        rows = [{"id": 1, "val": "not_a_number"}]
        html = _render(rows=rows, columns=cols)
        assert "not_a_number" in html


# ===========================================================================
# Phase 4 — Footer Aggregation Row
# ===========================================================================


class TestFooterAggregation:
    """Footer aggregation row."""

    def test_sum_aggregation(self):
        cols = [{"key": "name", "label": "Name"}, {"key": "score", "label": "Score"}]
        rows = [
            {"id": 1, "name": "Alice", "score": 90},
            {"id": 2, "name": "Bob", "score": 80},
        ]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "sum"})
        assert "data-table-footer-row" in html
        assert "170" in html

    def test_avg_aggregation(self):
        cols = [{"key": "score", "label": "Score"}]
        rows = [{"id": 1, "score": 90}, {"id": 2, "score": 80}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "avg"})
        assert "85" in html

    def test_count_aggregation(self):
        cols = [{"key": "score", "label": "Score"}]
        rows = [{"id": 1, "score": 90}, {"id": 2, "score": 80}, {"id": 3, "score": 70}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "count"})
        assert "3" in html

    def test_min_aggregation(self):
        cols = [{"key": "score", "label": "Score"}]
        rows = [{"id": 1, "score": 90}, {"id": 2, "score": 80}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "min"})
        assert "data-table-footer-agg" in html

    def test_max_aggregation(self):
        cols = [{"key": "score", "label": "Score"}]
        rows = [{"id": 1, "score": 90}, {"id": 2, "score": 80}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "max"})
        assert "data-table-footer-agg" in html

    def test_agg_label_shown(self):
        cols = [{"key": "score", "label": "Score"}]
        rows = [{"id": 1, "score": 90}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "sum"})
        assert "data-table-agg-label" in html
        assert "Sum:" in html

    def test_no_footer_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-footer-row" not in html

    def test_no_footer_when_empty_rows(self):
        cols = [{"key": "score", "label": "Score"}]
        html = _render(rows=[], columns=cols, footer_aggregations={"score": "sum"})
        assert "data-table-footer-row" not in html

    def test_agg_type_attr(self):
        cols = [{"key": "score", "label": "Score"}]
        rows = [{"id": 1, "score": 90}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "avg"})
        assert 'data-agg-type="avg"' in html

    def test_non_aggregated_columns_empty(self):
        cols = [{"key": "name", "label": "Name"}, {"key": "score", "label": "Score"}]
        rows = [{"id": 1, "name": "Alice", "score": 90}]
        html = _render(rows=rows, columns=cols, footer_aggregations={"score": "sum"})
        # The name column should have an empty td
        parts = html.split("data-table-footer-row")
        assert len(parts) >= 2


# ===========================================================================
# Phase 4 — Conditional Row/Cell Styling
# ===========================================================================


class TestConditionalStyling:
    """Conditional row and cell styling."""

    def test_row_class_map_applies(self):
        cols = [{"key": "name", "label": "Name"}, {"key": "status", "label": "Status"}]
        rows = [
            {"id": 1, "name": "Alice", "status": "active"},
            {"id": 2, "name": "Bob", "status": "inactive"},
        ]
        rcm = {"status": {"active": "row-success", "inactive": "row-danger"}}
        html = _render(rows=rows, columns=cols, row_class_map=rcm)
        assert "row-success" in html
        assert "row-danger" in html

    def test_row_class_map_no_match(self):
        cols = [{"key": "name", "label": "Name"}, {"key": "status", "label": "Status"}]
        rows = [{"id": 1, "name": "Alice", "status": "unknown"}]
        rcm = {"status": {"active": "row-success"}}
        html = _render(rows=rows, columns=cols, row_class_map=rcm)
        assert "row-success" not in html

    def test_cell_class_string(self):
        cols = [{"key": "name", "label": "Name", "cell_class": "highlight"}]
        rows = [{"id": 1, "name": "Alice"}]
        html = _render(rows=rows, columns=cols)
        assert "highlight" in html

    def test_cell_class_dict(self):
        cols = [{"key": "status", "label": "Status",
                 "cell_class": {"active": "cell-green", "inactive": "cell-red"}}]
        rows = [
            {"id": 1, "status": "active"},
            {"id": 2, "status": "inactive"},
        ]
        html = _render(rows=rows, columns=cols)
        assert "cell-green" in html
        assert "cell-red" in html

    def test_cell_class_dict_no_match(self):
        cols = [{"key": "status", "label": "Status",
                 "cell_class": {"active": "cell-green"}}]
        rows = [{"id": 1, "status": "unknown"}]
        html = _render(rows=rows, columns=cols)
        assert "cell-green" not in html

    def test_no_row_class_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "row-success" not in html
        assert "row-danger" not in html

    def test_row_class_map_xss(self):
        cols = [{"key": "status", "label": "Status"}]
        rows = [{"id": 1, "status": "bad"}]
        rcm = {"status": {"bad": '"><script>xss</script>'}}
        html = _render(rows=rows, columns=cols, row_class_map=rcm)
        assert "<script>xss</script>" not in html

    def test_cell_class_xss(self):
        cols = [{"key": "name", "label": "Name",
                 "cell_class": '"><script>xss</script>'}]
        rows = [{"id": 1, "name": "Alice"}]
        html = _render(rows=rows, columns=cols)
        assert "<script>xss</script>" not in html


# ===========================================================================
# Phase 4 — Multi-Level Column Headers
# ===========================================================================


class TestMultiLevelHeaders:
    """Multi-level grouped column headers."""

    def test_column_group_row_rendered(self):
        cols = [
            {"key": "jan", "label": "Jan"},
            {"key": "feb", "label": "Feb"},
            {"key": "mar", "label": "Mar"},
        ]
        groups = [{"label": "Q1", "columns": ["jan", "feb", "mar"]}]
        rows = [{"id": 1, "jan": 10, "feb": 20, "mar": 30}]
        html = _render(rows=rows, columns=cols, column_groups=groups)
        assert "data-table-column-group" in html
        assert "Q1" in html

    def test_colspan_matches_group_size(self):
        cols = [
            {"key": "jan", "label": "Jan"},
            {"key": "feb", "label": "Feb"},
            {"key": "mar", "label": "Mar"},
        ]
        groups = [{"label": "Q1", "columns": ["jan", "feb", "mar"]}]
        rows = [{"id": 1, "jan": 10, "feb": 20, "mar": 30}]
        html = _render(rows=rows, columns=cols, column_groups=groups)
        assert 'colspan="3"' in html

    def test_ungrouped_columns_have_rowspan(self):
        cols = [
            {"key": "name", "label": "Name"},
            {"key": "jan", "label": "Jan"},
            {"key": "feb", "label": "Feb"},
        ]
        groups = [{"label": "Q1", "columns": ["jan", "feb"]}]
        rows = [{"id": 1, "name": "Alice", "jan": 10, "feb": 20}]
        html = _render(rows=rows, columns=cols, column_groups=groups)
        assert 'rowspan="2"' in html

    def test_group_header_row_class(self):
        cols = [{"key": "jan", "label": "Jan"}, {"key": "feb", "label": "Feb"}]
        groups = [{"label": "Q1", "columns": ["jan", "feb"]}]
        rows = [{"id": 1, "jan": 10, "feb": 20}]
        html = _render(rows=rows, columns=cols, column_groups=groups)
        assert "data-table-group-header-row" in html

    def test_no_group_header_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-column-group" not in html
        assert "data-table-group-header-row" not in html

    def test_multiple_groups(self):
        cols = [
            {"key": "jan", "label": "Jan"},
            {"key": "feb", "label": "Feb"},
            {"key": "jul", "label": "Jul"},
            {"key": "aug", "label": "Aug"},
        ]
        groups = [
            {"label": "H1", "columns": ["jan", "feb"]},
            {"label": "H2", "columns": ["jul", "aug"]},
        ]
        rows = [{"id": 1, "jan": 10, "feb": 20, "jul": 30, "aug": 40}]
        html = _render(rows=rows, columns=cols, column_groups=groups)
        assert "H1" in html
        assert "H2" in html
        assert html.count('colspan="2"') == 2

    def test_column_group_xss(self):
        cols = [{"key": "jan", "label": "Jan"}]
        groups = [{"label": '<script>xss</script>', "columns": ["jan"]}]
        rows = [{"id": 1, "jan": 10}]
        html = _render(rows=rows, columns=cols, column_groups=groups)
        assert "<script>xss</script>" not in html


# ===========================================================================
# Phase 4 — Row Drag-and-Drop Reorder
# ===========================================================================


class TestRowDragReorder:
    """Row drag-and-drop reorder."""

    def test_drag_handle_rendered(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, row_drag=True)
        assert "data-table-drag-handle" in html
        assert "data-table-grip" in html

    def test_drag_handle_per_row(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, row_drag=True)
        assert html.count("data-table-grip") == 3

    def test_drag_col_header(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, row_drag=True)
        assert "data-table-drag-col" in html

    def test_wrapper_has_drag_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, row_drag=True)
        assert 'data-row-drag="true"' in html

    def test_drag_event_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       row_drag=True, row_drag_event="my_drag")
        assert 'data-row-drag-event="my_drag"' in html

    def test_drag_trigger_present(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, row_drag=True)
        assert "data-table-drag-trigger" in html

    def test_grip_is_draggable(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, row_drag=True)
        assert 'draggable="true"' in html

    def test_no_drag_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-drag-handle" not in html
        assert "data-table-grip" not in html
        assert 'data-row-drag' not in html

    def test_drag_colspan_in_empty_state(self):
        html = _render(rows=[], columns=SAMPLE_COLUMNS, row_drag=True)
        # colspan should include drag column: 2 cols + 1 drag = 3
        assert 'colspan="3"' in html


# ===========================================================================
# Phase 4 — Copy Row/Selection
# ===========================================================================


class TestCopyRows:
    """Copy selected rows to clipboard."""

    def test_copy_button_rendered(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, copyable=True)
        assert "data-table-copy-btn" in html
        assert "Copy</button>" in html

    def test_copy_attr_on_wrapper(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, copyable=True)
        assert 'data-copyable="true"' in html

    def test_copy_event_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       copyable=True, copy_event="my_copy")
        assert 'data-copy-event="my_copy"' in html

    def test_copy_format_attr(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       copyable=True, copy_format="tsv")
        assert 'data-copy-format="tsv"' in html

    def test_copy_trigger_present(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS, copyable=True)
        assert "data-table-copy-trigger" in html

    def test_no_copy_by_default(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-copy-btn" not in html
        assert 'data-copyable' not in html

    def test_copy_event_xss(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
                       copyable=True, copy_event='"><script>xss</script>')
        assert "<script>xss</script>" not in html


# ===========================================================================
# Phase 4 — Mixin Event Handlers
# ===========================================================================


class TestMixinRowDrag:
    """Row drag mixin handler."""

    def test_drag_reorders_rows(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_rows = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, {"id": 3, "name": "C"}]
        m.on_table_row_drag(json.dumps({"old_index": 0, "new_index": 2}))
        assert m.table_rows[0]["name"] == "B"
        assert m.table_rows[2]["name"] == "A"

    def test_drag_calls_handler(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            def __init__(self):
                self.drags = []
            def handle_row_drag(self, old_index, new_index):
                self.drags.append((old_index, new_index))

        m = MyMixin()
        m.init_table_state()
        m.table_rows = [{"id": 1}, {"id": 2}, {"id": 3}]
        m.on_table_row_drag(json.dumps({"old_index": 0, "new_index": 1}))
        assert m.drags == [(0, 1)]

    def test_drag_ignores_bad_json(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_rows = [{"id": 1}]
        m.on_table_row_drag("not json")  # Should not raise

    def test_drag_ignores_out_of_bounds(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.init_table_state()
        m.table_rows = [{"id": 1}, {"id": 2}]
        m.on_table_row_drag(json.dumps({"old_index": 5, "new_index": 0}))
        assert m.table_rows == [{"id": 1}, {"id": 2}]


class TestMixinCopy:
    """Copy mixin handler."""

    def test_copy_generates_csv(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_copy_format = "csv"
        m.init_table_state()
        m.table_rows = SAMPLE_ROWS
        m.table_selected_rows = ["1", "2"]
        m.on_table_copy("[]")
        # Empty list => copies selected rows
        m.handle_copy(["1", "2"])
        assert hasattr(m, "table_copy_data")
        assert "Alice" in m.table_copy_data
        assert "Bob" in m.table_copy_data

    def test_copy_tsv(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_copy_format = "tsv"
        m.init_table_state()
        m.table_rows = SAMPLE_ROWS
        m.handle_copy(["1"])
        assert "\t" in m.table_copy_data

    def test_copy_all_when_empty_keys(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_copy_format = "csv"
        m.init_table_state()
        m.table_rows = SAMPLE_ROWS
        m.handle_copy([])
        assert "Alice" in m.table_copy_data
        assert "Charlie" in m.table_copy_data


class TestMixinFormatCell:
    """Cell value formatting helper."""

    def test_format_number(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        col = {"key": "val", "type": "number"}
        assert m._format_cell_value(1234567, col) == "1,234,567"

    def test_format_currency(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        col = {"key": "val", "type": "currency", "currency_symbol": "$"}
        assert m._format_cell_value(42.5, col) == "$42.50"

    def test_format_percentage(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        col = {"key": "val", "type": "percentage"}
        assert m._format_cell_value(85.5, col) == "85.5%"

    def test_format_boolean_true(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        col = {"key": "val", "type": "boolean"}
        assert m._format_cell_value(True, col) == "Yes"

    def test_format_boolean_false(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        col = {"key": "val", "type": "boolean"}
        assert m._format_cell_value(False, col) == "No"

    def test_format_no_type(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        col = {"key": "val"}
        assert m._format_cell_value("hello", col) == "hello"


class TestMixinFooterAggregations:
    """Footer aggregation helper."""

    def test_sum_aggregation(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_footer_aggregations = {"score": "sum"}
        m.init_table_state()
        m.table_rows = [{"score": 90}, {"score": 80}]
        result = m.get_footer_aggregations()
        assert result["score"] == 170

    def test_avg_aggregation(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_footer_aggregations = {"score": "avg"}
        m.init_table_state()
        m.table_rows = [{"score": 90}, {"score": 80}]
        result = m.get_footer_aggregations()
        assert result["score"] == 85.0

    def test_count_aggregation(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_footer_aggregations = {"score": "count"}
        m.init_table_state()
        m.table_rows = [{"score": 90}, {"score": 80}, {"score": 70}]
        result = m.get_footer_aggregations()
        assert result["score"] == 3

    def test_min_aggregation(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_footer_aggregations = {"score": "min"}
        m.init_table_state()
        m.table_rows = [{"score": 90}, {"score": 80}]
        result = m.get_footer_aggregations()
        assert result["score"] == 80

    def test_max_aggregation(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_footer_aggregations = {"score": "max"}
        m.init_table_state()
        m.table_rows = [{"score": 90}, {"score": 80}]
        result = m.get_footer_aggregations()
        assert result["score"] == 90

    def test_empty_values(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_footer_aggregations = {"score": "sum"}
        m.init_table_state()
        m.table_rows = [{"score": "not_a_number"}]
        result = m.get_footer_aggregations()
        assert result["score"] == ""


class TestMixinRowClass:
    """Row class helper."""

    def test_dict_row_class_map(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_row_class_map = {"status": {"active": "row-green", "inactive": "row-red"}}
        assert m.get_row_class({"status": "active"}) == "row-green"
        assert m.get_row_class({"status": "inactive"}) == "row-red"
        assert m.get_row_class({"status": "unknown"}) == ""

    def test_callable_row_class_map(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_row_class_map = lambda row: "highlight" if row.get("score", 0) > 50 else ""
        assert m.get_row_class({"score": 90}) == "highlight"
        assert m.get_row_class({"score": 20}) == ""


# ===========================================================================
# Phase 4 — Mixin Context
# ===========================================================================


class TestMixinPhase4Context:
    """get_table_context includes Phase 4 fields."""

    def test_context_has_phase4_keys(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert "footer_aggregations" in ctx
        assert "row_class_map" in ctx
        assert "column_groups" in ctx
        assert "row_drag" in ctx
        assert "row_drag_event" in ctx
        assert "copyable" in ctx
        assert "copy_event" in ctx
        assert "copy_format" in ctx

    def test_context_defaults(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert ctx["footer_aggregations"] == {}
        assert ctx["row_class_map"] == {}
        assert ctx["column_groups"] == []
        assert ctx["row_drag"] is False
        assert ctx["copyable"] is False
        assert ctx["copy_format"] == "csv"


# ===========================================================================
# Phase 4 — Template Tag
# ===========================================================================


class TestTemplateTagPhase4:
    """Template tag includes Phase 4 params."""

    def test_phase4_params_in_context(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            footer_aggregations={"score": "sum"},
            row_class_map={"status": {"active": "green"}},
            column_groups=[{"label": "Q1", "columns": ["jan"]}],
            row_drag=True, row_drag_event="my_drag",
            copyable=True, copy_event="my_copy",
            copy_format="tsv",
        )
        assert ctx["footer_aggregations"] == {"score": "sum"}
        assert ctx["row_class_map"] == {"status": {"active": "green"}}
        assert ctx["column_groups"] == [{"label": "Q1", "columns": ["jan"]}]
        assert ctx["row_drag"] is True
        assert ctx["row_drag_event"] == "my_drag"
        assert ctx["copyable"] is True
        assert ctx["copy_event"] == "my_copy"
        assert ctx["copy_format"] == "tsv"

    def test_phase4_defaults(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(rows=[], columns=[])
        assert ctx["footer_aggregations"] == {}
        assert ctx["row_class_map"] == {}
        assert ctx["column_groups"] == []
        assert ctx["row_drag"] is False
        assert ctx["row_drag_event"] == "table_row_drag"
        assert ctx["copyable"] is False
        assert ctx["copy_event"] == "table_copy"
        assert ctx["copy_format"] == "csv"


# ===========================================================================
# Phase 4 — CSS Tests
# ===========================================================================


class TestPhase4CSS:
    """Phase 4 CSS class definitions exist."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        import pathlib
        css_path = pathlib.Path(__file__).parent.parent / "src" / "djust_components" / "static" / "djust_components" / "components.css"
        self.css = css_path.read_text()

    def test_footer_row_class(self):
        assert ".data-table-footer-row" in self.css

    def test_footer_agg_class(self):
        assert ".data-table-footer-agg" in self.css

    def test_agg_label_class(self):
        assert ".data-table-agg-label" in self.css

    def test_type_number_class(self):
        assert ".data-table-type-number" in self.css

    def test_type_currency_class(self):
        assert ".data-table-type-currency" in self.css

    def test_type_boolean_class(self):
        assert ".data-table-type-boolean" in self.css

    def test_column_group_class(self):
        assert ".data-table-column-group" in self.css

    def test_drag_handle_class(self):
        assert ".data-table-drag-handle" in self.css

    def test_grip_class(self):
        assert ".data-table-grip" in self.css

    def test_copy_btn_class(self):
        assert ".data-table-copy-btn" in self.css


# ===========================================================================
# Phase 5 — Data Import & Computed
# ===========================================================================


# ── 5A. CSV/JSON Import ──


NUMERIC_COLUMNS = [
    {"key": "name", "label": "Name"},
    {"key": "score", "label": "Score"},
]

NUMERIC_ROWS = [
    {"id": 1, "name": "Alice", "score": 90},
    {"id": 2, "name": "Bob", "score": 60},
    {"id": 3, "name": "Charlie", "score": 30},
]


class TestMixinImportCSV:
    """CSV import via mixin."""

    def test_import_csv_preview(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_import_preview = True
        m.init_table_state()
        csv_data = "name,email\nDave,dave@example.com\nEve,eve@example.com"
        m.on_table_import(json.dumps({"format": "csv", "data": csv_data}))
        assert m.table_import_pending is True
        assert len(m.table_import_preview_data) == 2
        assert m.table_import_preview_data[0]["name"] == "Dave"

    def test_import_csv_confirm(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_import_preview = True
        m.init_table_state()
        m.table_rows = list(SAMPLE_ROWS)
        csv_data = "name,email\nDave,dave@example.com"
        m.on_table_import(json.dumps({"format": "csv", "data": csv_data}))
        assert m.table_import_pending is True
        m.on_table_import(json.dumps({"confirm": True}))
        assert m.table_import_pending is False
        assert len(m.table_rows) == 4  # 3 original + 1 imported
        assert m.table_rows[-1]["name"] == "Dave"

    def test_import_csv_no_preview(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_import_preview = False
        m.init_table_state()
        m.table_rows = []
        csv_data = "name,email\nDave,dave@example.com"
        m.on_table_import(json.dumps({"format": "csv", "data": csv_data}))
        assert m.table_import_pending is False
        assert len(m.table_rows) == 1

    def test_import_csv_bad_data(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.on_table_import(json.dumps({"format": "csv", "data": ""}))
        assert m.table_import_pending is False
        assert len(m.table_import_preview_data) == 0

    def test_import_bad_json_string(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.on_table_import("not json")  # Should not raise


class TestMixinImportJSON:
    """JSON import via mixin."""

    def test_import_json_array(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_import_preview = True
        m.init_table_state()
        json_data = json.dumps([
            {"name": "Dave", "email": "dave@example.com"},
            {"name": "Eve", "email": "eve@example.com"},
        ])
        m.on_table_import(json.dumps({"format": "json", "data": json_data}))
        assert m.table_import_pending is True
        assert len(m.table_import_preview_data) == 2

    def test_import_json_not_array(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.on_table_import(json.dumps({"format": "json", "data": '{"not": "array"}'}))
        assert len(m.table_import_errors) == 1
        assert "array" in m.table_import_errors[0].lower()

    def test_import_unsupported_format(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        m.on_table_import(json.dumps({"format": "xml", "data": "<x/>"}))
        assert len(m.table_import_errors) == 1
        assert "unsupported" in m.table_import_errors[0].lower()

    def test_import_filters_unknown_columns(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_import_preview = True
        m.init_table_state()
        json_data = json.dumps([{"name": "Dave", "unknown_col": "val"}])
        m.on_table_import(json.dumps({"format": "json", "data": json_data}))
        assert len(m.table_import_preview_data) == 1
        assert "unknown_col" not in m.table_import_preview_data[0]

    def test_import_custom_handler(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin

        class MyMixin(DataTableMixin):
            def __init__(self):
                self.imported = []
            def handle_import(self, rows):
                self.imported = rows

        m = MyMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.table_import_preview = False
        m.init_table_state()
        csv_data = "name,email\nDave,dave@example.com"
        m.on_table_import(json.dumps({"format": "csv", "data": csv_data}))
        assert len(m.imported) == 1
        assert m.imported[0]["name"] == "Dave"


# ── 5B. Computed Columns ──


class TestMixinComputedColumns:
    """Computed column evaluation."""

    def test_basic_arithmetic(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = [
            {"key": "margin", "label": "Margin", "expression": "revenue - cost"},
        ]
        rows = [{"revenue": 100, "cost": 40}, {"revenue": 200, "cost": 80}]
        result = m.evaluate_computed_columns(rows)
        assert result[0]["margin"] == 60
        assert result[1]["margin"] == 120

    def test_multiplication(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = [
            {"key": "total", "label": "Total", "expression": "qty * price"},
        ]
        rows = [{"qty": 5, "price": 10}]
        result = m.evaluate_computed_columns(rows)
        assert result[0]["total"] == 50

    def test_division(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = [
            {"key": "rate", "label": "Rate", "expression": "hits / attempts"},
        ]
        rows = [{"hits": 75, "attempts": 100}]
        result = m.evaluate_computed_columns(rows)
        assert result[0]["rate"] == 0.75

    def test_no_computed_columns(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = []
        rows = [{"a": 1}]
        result = m.evaluate_computed_columns(rows)
        assert result == rows

    def test_bad_expression(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = [
            {"key": "bad", "label": "Bad", "expression": "1 / 0"},
        ]
        rows = [{"a": 1}]
        result = m.evaluate_computed_columns(rows)
        assert result[0]["bad"] == ""

    def test_unsafe_expression_rejected(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = [
            {"key": "evil", "label": "Evil", "expression": "__import__('os')"},
        ]
        rows = [{"a": 1}]
        result = m.evaluate_computed_columns(rows)
        assert result[0]["evil"] == ""

    def test_preserves_original_data(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_computed_columns = [
            {"key": "double", "label": "Double", "expression": "x * 2"},
        ]
        rows = [{"x": 5}]
        result = m.evaluate_computed_columns(rows)
        assert result[0]["x"] == 5
        assert result[0]["double"] == 10


class TestHandlerComputedColumns:
    """Handler renders computed column headers and cells."""

    def test_computed_column_header_rendered(self):
        html = _render(
            rows=[{"id": 1, "revenue": 100, "cost": 40, "margin": 60}],
            columns=[
                {"key": "revenue", "label": "Revenue"},
                {"key": "cost", "label": "Cost"},
            ],
            computed_columns=[
                {"key": "margin", "label": "Margin", "expression": "revenue - cost"},
            ],
        )
        assert "data-table-computed-header" in html
        assert "Margin" in html

    def test_computed_column_cell_rendered(self):
        html = _render(
            rows=[{"id": 1, "revenue": 100, "cost": 40, "margin": 60}],
            columns=[
                {"key": "revenue", "label": "Revenue"},
                {"key": "cost", "label": "Cost"},
            ],
            computed_columns=[
                {"key": "margin", "label": "Margin"},
            ],
        )
        assert "data-table-computed" in html
        assert ">60<" in html


# ── 5C. Cell Merge / Colspan ──


class TestMixinCellMerge:
    """Cell merge helper in mixin."""

    def test_get_cell_merge_default(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        row = {"name": "Alice"}
        assert m.get_cell_merge(row, "name") == 1

    def test_get_cell_merge_with_data(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        row = {"name": "Alice", "_merge": {"name": 2}}
        assert m.get_cell_merge(row, "name") == 2
        assert m.get_cell_merge(row, "email") == 1

    def test_get_cell_merge_custom_key(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_cell_merge_key = "_span"
        row = {"name": "Alice", "_span": {"name": 3}}
        assert m.get_cell_merge(row, "name") == 3

    def test_get_cell_merge_no_dict(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        row = {"name": "Alice", "_merge": "not a dict"}
        assert m.get_cell_merge(row, "name") == 1


class TestHandlerCellMerge:
    """Handler renders colspan for merged cells."""

    def test_colspan_rendered(self):
        html = _render(
            rows=[{"id": 1, "a": "merged", "b": "val", "_merge": {"a": 2}}],
            columns=[
                {"key": "a", "label": "A"},
                {"key": "b", "label": "B"},
            ],
        )
        assert 'colspan="2"' in html
        assert "data-table-merged" in html

    def test_merged_cell_skipped(self):
        html = _render(
            rows=[{"id": 1, "a": "merged", "b": "hidden", "_merge": {"a": 2}}],
            columns=[
                {"key": "a", "label": "A"},
                {"key": "b", "label": "B"},
            ],
        )
        # b cell value should not appear since it's merged
        assert ">hidden<" not in html

    def test_no_merge_key(self):
        html = _render(
            rows=[{"id": 1, "a": "val1", "b": "val2"}],
            columns=[
                {"key": "a", "label": "A"},
                {"key": "b", "label": "B"},
            ],
        )
        assert "colspan" not in html


# ── 5D. Column Expressions ──


class TestMixinExpressionFilter:
    """Expression filter evaluation."""

    def test_greater_than(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(100, "> 50") is True
        assert m.evaluate_expression_filter(30, "> 50") is False

    def test_greater_equal(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(50, ">= 50") is True
        assert m.evaluate_expression_filter(49, ">= 50") is False

    def test_less_than(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(30, "< 50") is True
        assert m.evaluate_expression_filter(50, "< 50") is False

    def test_less_equal(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(50, "<= 50") is True
        assert m.evaluate_expression_filter(51, "<= 50") is False

    def test_equals(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(50, "= 50") is True
        assert m.evaluate_expression_filter(51, "= 50") is False

    def test_not_equals(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(50, "!= 50") is False
        assert m.evaluate_expression_filter(51, "!= 50") is True

    def test_contains(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter("active user", 'contains "active"') is True
        assert m.evaluate_expression_filter("inactive", 'contains "ACTIVE"') is True
        assert m.evaluate_expression_filter("pending", 'contains "active"') is False

    def test_startswith(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter("active", 'startswith "act"') is True
        assert m.evaluate_expression_filter("inactive", 'startswith "act"') is False

    def test_endswith(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter("active", 'endswith "ive"') is True
        assert m.evaluate_expression_filter("pending", 'endswith "ive"') is False

    def test_between(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter(50, "between 10 and 100") is True
        assert m.evaluate_expression_filter(10, "between 10 and 100") is True
        assert m.evaluate_expression_filter(100, "between 10 and 100") is True
        assert m.evaluate_expression_filter(5, "between 10 and 100") is False

    def test_empty(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter("", "empty") is True
        assert m.evaluate_expression_filter(None, "empty") is True
        assert m.evaluate_expression_filter("val", "empty") is False

    def test_not_empty(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter("val", "not empty") is True
        assert m.evaluate_expression_filter("", "not empty") is False

    def test_empty_expression_passes_all(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        assert m.evaluate_expression_filter("anything", "") is True


class TestMixinApplyExpressionFilters:
    """Apply expression filters to row sets."""

    def test_filter_rows(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        m.table_active_expressions = {"score": "> 50"}
        rows = [
            {"name": "Alice", "score": 90},
            {"name": "Bob", "score": 60},
            {"name": "Charlie", "score": 30},
        ]
        result = m.apply_expression_filters(rows)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"

    def test_no_active_expressions(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        rows = [{"name": "Alice", "score": 90}]
        result = m.apply_expression_filters(rows)
        assert result == rows

    def test_multiple_expressions(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        m.table_active_expressions = {
            "score": "> 50",
            "name": 'contains "Alice"',
        }
        rows = [
            {"name": "Alice", "score": 90},
            {"name": "Bob", "score": 60},
        ]
        result = m.apply_expression_filters(rows)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"


class TestMixinExpressionEvent:
    """Expression event handler."""

    def test_set_expression(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        m.on_table_expression(json.dumps({"column": "score", "expression": "> 50"}))
        assert m.table_active_expressions == {"score": "> 50"}

    def test_clear_expression(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        m.table_active_expressions = {"score": "> 50"}
        m.on_table_expression(json.dumps({"column": "score", "expression": ""}))
        assert "score" not in m.table_active_expressions

    def test_expression_resets_page(self):
        import json
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        m.table_page = 5
        m.on_table_expression(json.dumps({"column": "score", "expression": "> 50"}))
        assert m.table_page == 1

    def test_bad_json_ignored(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = NUMERIC_COLUMNS
        m.init_table_state()
        m.on_table_expression("not json")  # Should not raise


class TestHandlerExpressionFilters:
    """Handler renders expression filter inputs."""

    def test_expression_row_rendered(self):
        html = _render(
            rows=NUMERIC_ROWS,
            columns=NUMERIC_COLUMNS,
            column_expressions={"score": "> 50"},
        )
        assert "data-table-expression-row" in html
        assert "data-table-expression" in html

    def test_expression_value_preserved(self):
        html = _render(
            rows=NUMERIC_ROWS,
            columns=NUMERIC_COLUMNS,
            column_expressions={"score": "Expression..."},
            active_expressions={"score": "> 50"},
        )
        assert 'value="&gt; 50"' in html or 'value="> 50"' in html

    def test_no_expression_no_row(self):
        html = _render(rows=NUMERIC_ROWS, columns=NUMERIC_COLUMNS)
        assert "data-table-expression-row" not in html


# ── 5E. Conditional Formatting Presets ──


class TestMixinConditionalFormatting:
    """Conditional formatting helpers."""

    def test_data_bar(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "data_bar", "min": 0, "max": 100},
        ]
        result = m.get_conditional_formatting(75, "score")
        assert result["type"] == "data_bar"
        assert result["percent"] == 75.0

    def test_data_bar_clamped(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "data_bar", "min": 0, "max": 100},
        ]
        result = m.get_conditional_formatting(150, "score")
        assert result["percent"] == 100.0

    def test_color_scale(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "color_scale", "min": 0, "max": 100,
             "colors": ["#ff0000", "#00ff00"]},
        ]
        result = m.get_conditional_formatting(50, "score")
        assert result["type"] == "color_scale"
        assert result["color"].startswith("#")

    def test_color_scale_at_min(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "color_scale", "min": 0, "max": 100,
             "colors": ["#ff0000", "#00ff00"]},
        ]
        result = m.get_conditional_formatting(0, "score")
        assert result["color"] == "#ff0000"

    def test_color_scale_at_max(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "color_scale", "min": 0, "max": 100,
             "colors": ["#ff0000", "#00ff00"]},
        ]
        result = m.get_conditional_formatting(100, "score")
        assert result["color"] == "#00ff00"

    def test_icon_set(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "icon_set", "min": 0, "max": 100,
             "icons": ["\u25bc", "\u25b6", "\u25b2"],
             "thresholds": [33, 66]},
        ]
        low = m.get_conditional_formatting(20, "score")
        assert low["icon"] == "\u25bc"
        mid = m.get_conditional_formatting(50, "score")
        assert mid["icon"] == "\u25b6"
        high = m.get_conditional_formatting(80, "score")
        assert high["icon"] == "\u25b2"

    def test_no_matching_column(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "other", "type": "data_bar", "min": 0, "max": 100},
        ]
        result = m.get_conditional_formatting(50, "score")
        assert result == {}

    def test_non_numeric_value(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "data_bar", "min": 0, "max": 100},
        ]
        result = m.get_conditional_formatting("abc", "score")
        assert result == {}

    def test_three_color_scale(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_conditional_formatting = [
            {"column": "score", "type": "color_scale", "min": 0, "max": 100,
             "colors": ["#ff0000", "#ffff00", "#00ff00"]},
        ]
        mid = m.get_conditional_formatting(50, "score")
        assert mid["type"] == "color_scale"
        assert mid["color"].startswith("#")


class TestHandlerConditionalFormatting:
    """Handler renders conditional formatting in cells."""

    def test_data_bar_rendered(self):
        html = _render(
            rows=[{"id": 1, "score": 75}],
            columns=[{"key": "score", "label": "Score"}],
            conditional_formatting=[
                {"column": "score", "type": "data_bar", "min": 0, "max": 100},
            ],
        )
        assert "data-table-cf-data-bar" in html
        assert "data-table-data-bar" in html
        assert "width:75" in html

    def test_color_scale_rendered(self):
        html = _render(
            rows=[{"id": 1, "score": 50}],
            columns=[{"key": "score", "label": "Score"}],
            conditional_formatting=[
                {"column": "score", "type": "color_scale", "min": 0, "max": 100,
                 "colors": ["#ff0000", "#00ff00"]},
            ],
        )
        assert "data-table-cf-color-scale" in html
        assert "background-color:#" in html

    def test_icon_set_rendered(self):
        html = _render(
            rows=[{"id": 1, "score": 20}],
            columns=[{"key": "score", "label": "Score"}],
            conditional_formatting=[
                {"column": "score", "type": "icon_set", "min": 0, "max": 100,
                 "icons": ["\u25bc", "\u25b6", "\u25b2"],
                 "thresholds": [33, 66]},
            ],
        )
        assert "data-table-cf-icon-set" in html
        assert "data-table-cf-icon" in html

    def test_no_formatting(self):
        html = _render(
            rows=[{"id": 1, "score": 75}],
            columns=[{"key": "score", "label": "Score"}],
        )
        assert "data-table-cf" not in html


# ── Phase 5 — Handler Import Rendering ──


class TestHandlerImport:
    """Handler renders import toolbar and preview."""

    def test_import_button_rendered(self):
        html = _render(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            importable=True,
        )
        assert "data-table-import" in html
        assert "data-table-import-btn" in html
        assert "Import CSV" in html
        assert "Import JSON" in html

    def test_import_file_input(self):
        html = _render(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            importable=True,
        )
        assert "data-table-import-file" in html

    def test_import_preview_rendered(self):
        html = _render(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            importable=True,
            import_pending=True,
            import_preview_data=[{"name": "Dave", "email": "dave@example.com"}],
        )
        assert "data-table-import-preview" in html
        assert "1 rows ready to import" in html
        assert "data-table-import-confirm" in html
        assert "data-table-import-cancel" in html

    def test_import_errors_rendered(self):
        html = _render(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            importable=True,
            import_errors=["Row 1: no matching columns"],
        )
        assert "data-table-import-errors" in html
        assert "Row 1: no matching columns" in html

    def test_no_import_no_button(self):
        html = _render(rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS)
        assert "data-table-import" not in html

    def test_import_wrapper_attrs(self):
        html = _render(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            importable=True,
        )
        assert 'data-importable="true"' in html
        assert 'data-import-event="table_import"' in html


# ── Phase 5 — Mixin Context ──


class TestMixinPhase5Context:
    """get_table_context includes Phase 5 fields."""

    def test_context_has_phase5_keys(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        for key in [
            "importable", "import_event", "import_formats", "import_preview",
            "import_preview_data", "import_errors", "import_pending",
            "computed_columns", "cell_merge_key",
            "column_expressions", "expression_event", "active_expressions",
            "conditional_formatting",
        ]:
            assert key in ctx, f"Missing key: {key}"

    def test_context_defaults(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        m.table_columns = SAMPLE_COLUMNS
        m.init_table_state()
        ctx = m.get_table_context()
        assert ctx["importable"] is False
        assert ctx["import_formats"] == ["csv", "json"]
        assert ctx["import_preview"] is True
        assert ctx["import_preview_data"] == []
        assert ctx["import_errors"] == []
        assert ctx["import_pending"] is False
        assert ctx["computed_columns"] == []
        assert ctx["cell_merge_key"] == "_merge"
        assert ctx["column_expressions"] == {}
        assert ctx["active_expressions"] == {}
        assert ctx["conditional_formatting"] == []


# ── Phase 5 — Template Tag ──


class TestTemplateTagPhase5:
    """Template tag includes Phase 5 params."""

    def test_phase5_params_in_context(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(
            rows=SAMPLE_ROWS, columns=SAMPLE_COLUMNS,
            importable=True,
            import_event="my_import",
            import_formats=["csv"],
            import_preview=False,
            import_preview_data=[{"name": "X"}],
            import_errors=["err"],
            import_pending=True,
            computed_columns=[{"key": "c", "expression": "a+b"}],
            cell_merge_key="_span",
            column_expressions={"score": "> 50"},
            expression_event="my_expr",
            active_expressions={"score": "> 50"},
            conditional_formatting=[{"column": "score", "type": "data_bar"}],
        )
        assert ctx["importable"] is True
        assert ctx["import_event"] == "my_import"
        assert ctx["import_formats"] == ["csv"]
        assert ctx["import_preview"] is False
        assert ctx["import_preview_data"] == [{"name": "X"}]
        assert ctx["import_errors"] == ["err"]
        assert ctx["import_pending"] is True
        assert ctx["computed_columns"] == [{"key": "c", "expression": "a+b"}]
        assert ctx["cell_merge_key"] == "_span"
        assert ctx["column_expressions"] == {"score": "> 50"}
        assert ctx["expression_event"] == "my_expr"
        assert ctx["active_expressions"] == {"score": "> 50"}
        assert ctx["conditional_formatting"] == [{"column": "score", "type": "data_bar"}]

    def test_phase5_defaults(self):
        from djust_components.templatetags.djust_components import data_table
        ctx = data_table(rows=[], columns=[])
        assert ctx["importable"] is False
        assert ctx["import_formats"] == ["csv", "json"]
        assert ctx["computed_columns"] == []
        assert ctx["column_expressions"] == {}
        assert ctx["conditional_formatting"] == []


# ── Phase 5 — CSS Tests ──


class TestPhase5CSS:
    """Phase 5 CSS class definitions exist."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        import pathlib
        css_path = pathlib.Path(__file__).parent.parent / "src" / "djust_components" / "static" / "djust_components" / "components.css"
        self.css = css_path.read_text()

    def test_import_btn_class(self):
        assert ".data-table-import-btn" in self.css

    def test_import_errors_class(self):
        assert ".data-table-import-errors" in self.css

    def test_import_preview_class(self):
        assert ".data-table-import-preview" in self.css

    def test_import_confirm_class(self):
        assert ".data-table-import-confirm" in self.css

    def test_computed_header_class(self):
        assert ".data-table-computed-header" in self.css

    def test_computed_cell_class(self):
        assert ".data-table-computed" in self.css

    def test_merged_class(self):
        assert ".data-table-merged" in self.css

    def test_expression_class(self):
        assert ".data-table-expression" in self.css

    def test_expression_row_class(self):
        assert ".data-table-expression-row" in self.css

    def test_cf_data_bar_class(self):
        assert ".data-table-cf-data-bar" in self.css

    def test_data_bar_class(self):
        assert ".data-table-data-bar" in self.css

    def test_cf_color_scale_class(self):
        assert ".data-table-cf-color-scale" in self.css

    def test_cf_icon_set_class(self):
        assert ".data-table-cf-icon-set" in self.css

    def test_cf_icon_class(self):
        assert ".data-table-cf-icon" in self.css


# ── Phase 5 — Color Interpolation ──


class TestColorInterpolation:
    """Test _interpolate_color helper on mixin."""

    def test_two_colors_midpoint(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        result = m._interpolate_color(["#000000", "#ffffff"], 0.5)
        # Should be roughly #7f7f7f or #808080
        assert result.startswith("#")
        assert len(result) == 7

    def test_two_colors_start(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        result = m._interpolate_color(["#ff0000", "#00ff00"], 0.0)
        assert result == "#ff0000"

    def test_two_colors_end(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        result = m._interpolate_color(["#ff0000", "#00ff00"], 1.0)
        assert result == "#00ff00"

    def test_three_colors(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        result = m._interpolate_color(["#ff0000", "#ffff00", "#00ff00"], 0.5)
        assert result.startswith("#")

    def test_single_color(self):
        from djust_components.mixins.data_table import DataTableMixin
        m = DataTableMixin()
        result = m._interpolate_color(["#ff0000"], 0.5)
        assert result == "#ff0000"
