"""
DataTableMixin — server-side data table logic for djust LiveViews.

Provides automatic sort, search, filter, select, and pagination event handlers
that pair with the ``{% data_table %}`` template tag and ``DataTableHandler``
Rust handler.

Usage::

    class UserListView(DataTableMixin, LiveView):
        table_model = User
        table_columns = [
            {"key": "username", "label": "Username", "sortable": True, "filterable": True},
            {"key": "email", "label": "Email", "sortable": True},
        ]
        table_page_size = 25
        table_default_sort = "username"
        table_searchable_fields = ["username", "email"]

        def mount(self, **kwargs):
            self.init_table_state()
            self.refresh_table()

        def get_template_context(self):
            ctx = super().get_template_context()
            ctx.update(self.get_table_context())
            return ctx
"""

import math

__all__ = ["DataTableMixin"]


class DataTableMixin:
    """Mixin for LiveViews that provides automatic data table event handlers."""

    # ── Class-level configuration ──
    table_model = None
    table_queryset = None
    table_columns = []
    table_page_size = 25
    table_default_sort = ""
    table_default_sort_desc = False
    table_searchable_fields = []
    table_row_key = "id"
    table_selectable = False

    # Event name configuration (overridable)
    table_sort_event = "table_sort"
    table_search_event = "table_search"
    table_filter_event = "table_filter"
    table_select_event = "table_select"
    table_page_event = "table_page"

    # Phase 2 class-level configuration
    table_editable_columns = []
    table_edit_event = "table_cell_edit"
    table_resizable = False
    table_reorderable = False
    table_reorder_event = "table_reorder"
    table_frozen_left = 0
    table_frozen_right = 0
    table_column_visibility = False
    table_visibility_event = "table_visibility"
    table_density = "comfortable"
    table_density_toggle = False
    table_density_event = "table_density"
    table_responsive_cards = False
    table_editable_rows = False
    table_edit_row_event = "table_row_edit"
    table_save_row_event = "table_row_save"
    table_cancel_row_event = "table_row_cancel"

    def init_table_state(self):
        """Initialize instance state. Call from mount()."""
        self.table_sort_by = self.table_default_sort
        self.table_sort_desc = self.table_default_sort_desc
        self.table_search_query = ""
        self.table_filters = {}
        self.table_selected_rows = []
        self.table_page = 1
        self.table_total_pages = 1
        self.table_rows = []
        self.table_loading = False
        # Phase 2 state
        self.table_editing_rows = []
        self.table_column_order = [
            col.get("key", col) if isinstance(col, dict) else col
            for col in self.table_columns
        ]
        self.table_visible_columns = list(self.table_column_order)
        self.table_current_density = self.table_density

    # ── Event Handlers ──

    def on_table_sort(self, value, **kwargs):
        """Handle sort event: toggle direction or switch column."""
        column = str(value)
        if self.table_sort_by == column:
            self.table_sort_desc = not self.table_sort_desc
        else:
            self.table_sort_by = column
            self.table_sort_desc = False

    def on_table_search(self, value, **kwargs):
        """Handle search event: update query, reset to page 1."""
        self.table_search_query = str(value)
        self.table_page = 1

    def on_table_filter(self, value, column=None, **kwargs):
        """Handle filter event: set or clear per-column filter, reset to page 1."""
        if column is None:
            column = kwargs.get("data-column", kwargs.get("data_column", ""))
        column = str(column)
        value = str(value)
        if value:
            self.table_filters[column] = value
        else:
            self.table_filters.pop(column, None)
        self.table_page = 1

    def on_table_select(self, value, **kwargs):
        """Handle selection event: toggle row or select/deselect all."""
        value = str(value)
        if value == "__all__":
            # Toggle all visible rows
            if self.table_selected_rows:
                self.table_selected_rows = []
            else:
                self.table_selected_rows = [
                    str(row.get(self.table_row_key, ""))
                    for row in self.table_rows
                ]
        else:
            if value in self.table_selected_rows:
                self.table_selected_rows.remove(value)
            else:
                self.table_selected_rows.append(value)

    def on_table_page(self, value, **kwargs):
        """Handle page event: navigate to page number."""
        try:
            self.table_page = int(value)
        except (ValueError, TypeError):
            pass

    # ── Phase 2 Event Handlers ──

    def on_table_cell_edit(self, value, **kwargs):
        """Handle inline cell edit. value is JSON: {row_key, column, value}."""
        import json
        try:
            data = json.loads(str(value)) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            return
        if isinstance(data, dict):
            self.handle_cell_edit(
                row_key=data.get("row_key", ""),
                column=data.get("column", ""),
                value=data.get("value", ""),
            )

    def handle_cell_edit(self, row_key, column, value):
        """Override this to persist inline cell edits. Called by on_table_cell_edit."""
        pass

    def on_table_reorder(self, value, **kwargs):
        """Handle column reorder. value is comma-separated column keys."""
        new_order = [k.strip() for k in str(value).split(",") if k.strip()]
        if new_order:
            self.table_column_order = new_order

    def on_table_visibility(self, value, **kwargs):
        """Handle column visibility toggle. value is comma-separated visible keys."""
        visible = [k.strip() for k in str(value).split(",") if k.strip()]
        self.table_visible_columns = visible

    def on_table_density(self, value, **kwargs):
        """Handle density toggle. value is 'compact', 'comfortable', or 'spacious'."""
        val = str(value)
        if val in ("compact", "comfortable", "spacious"):
            self.table_current_density = val

    def on_table_row_edit(self, value, **kwargs):
        """Handle entering row edit mode."""
        row_id = str(value)
        if row_id not in self.table_editing_rows:
            self.table_editing_rows.append(row_id)

    def on_table_row_save(self, value, **kwargs):
        """Handle saving an edited row. Override handle_row_save to persist."""
        row_id = str(value)
        self.handle_row_save(row_id, kwargs)
        if row_id in self.table_editing_rows:
            self.table_editing_rows.remove(row_id)

    def on_table_row_cancel(self, value, **kwargs):
        """Handle cancelling row edit."""
        row_id = str(value)
        if row_id in self.table_editing_rows:
            self.table_editing_rows.remove(row_id)

    def handle_row_save(self, row_key, data):
        """Override this to persist row edits. Called by on_table_row_save."""
        pass

    # ── Context Generation ──

    def get_table_context(self):
        """Return a dict suitable for the {% data_table %} template tag."""
        return {
            "rows": self.table_rows,
            "columns": self.table_columns,
            "sort_by": self.table_sort_by,
            "sort_desc": self.table_sort_desc,
            "sort_event": self.table_sort_event,
            "selectable": self.table_selectable,
            "selected_rows": self.table_selected_rows,
            "select_event": self.table_select_event,
            "row_key": self.table_row_key,
            "search": bool(self.table_searchable_fields),
            "search_query": self.table_search_query,
            "search_event": self.table_search_event,
            "search_debounce": 300,
            "filters": self.table_filters,
            "filter_event": self.table_filter_event,
            "loading": self.table_loading,
            "empty_title": "No data",
            "empty_description": "",
            "empty_icon": "",
            "paginate": self.table_page_size > 0,
            "page": self.table_page,
            "total_pages": self.table_total_pages,
            "page_event": self.table_page_event,
            "striped": False,
            "compact": False,
            # Phase 2
            "editable_columns": self.table_editable_columns,
            "edit_event": self.table_edit_event,
            "resizable": self.table_resizable,
            "reorderable": self.table_reorderable,
            "reorder_event": self.table_reorder_event,
            "frozen_left": self.table_frozen_left,
            "frozen_right": self.table_frozen_right,
            "column_visibility": self.table_column_visibility,
            "visibility_event": self.table_visibility_event,
            "density": self.table_current_density,
            "density_toggle": self.table_density_toggle,
            "density_event": self.table_density_event,
            "responsive_cards": self.table_responsive_cards,
            "editable_rows": self.table_editable_rows,
            "edit_row_event": self.table_edit_row_event,
            "save_row_event": self.table_save_row_event,
            "cancel_row_event": self.table_cancel_row_event,
            "editing_rows": self.table_editing_rows,
        }

    # ── Queryset Pipeline ──

    def get_table_queryset(self):
        """Return the base queryset."""
        if self.table_queryset is not None:
            return self.table_queryset
        if self.table_model is not None:
            return self.table_model.objects.all()
        return []

    def _apply_table_search(self, qs):
        """Apply global search across searchable fields."""
        if not self.table_search_query or not self.table_searchable_fields:
            return qs
        from django.db.models import Q
        q = Q()
        for field in self.table_searchable_fields:
            q |= Q(**{f"{field}__icontains": self.table_search_query})
        return qs.filter(q)

    def _apply_table_filters(self, qs):
        """Apply per-column filters."""
        for col_key, value in self.table_filters.items():
            if value:
                qs = qs.filter(**{f"{col_key}__icontains": value})
        return qs

    def _apply_table_sort(self, qs):
        """Apply sort ordering."""
        if not self.table_sort_by:
            return qs
        order = f"-{self.table_sort_by}" if self.table_sort_desc else self.table_sort_by
        return qs.order_by(order)

    def _apply_table_pagination(self, qs):
        """Slice queryset for current page and set total_pages."""
        if self.table_page_size <= 0:
            return qs
        total = qs.count()
        self.table_total_pages = max(1, math.ceil(total / self.table_page_size))
        start = (self.table_page - 1) * self.table_page_size
        end = start + self.table_page_size
        return qs[start:end]

    def refresh_table(self):
        """Run the full pipeline: queryset -> search -> filter -> sort -> paginate -> serialize."""
        qs = self.get_table_queryset()
        qs = self._apply_table_search(qs)
        qs = self._apply_table_filters(qs)
        qs = self._apply_table_sort(qs)
        qs = self._apply_table_pagination(qs)
        # Serialize to list of dicts
        self.table_rows = list(qs.values()) if hasattr(qs, "values") else list(qs)
