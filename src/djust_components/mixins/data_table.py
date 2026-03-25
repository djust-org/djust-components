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
