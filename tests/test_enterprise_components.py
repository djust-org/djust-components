"""Tests for v2.0 Batch 4 — Enterprise + Specialized components: template tags, component classes, and XSS."""
from django.template import Template, Context
import pytest

from djust_components.components import (
    CalendarView,
    GanttChart,
    DiffViewer,
    PivotTable,
    OrgChart,
    ComparisonTable,
    MasonryGrid,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Calendar View — Template Tag
# ===========================================================================

class TestCalendarViewTag:
    def test_basic(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {
            "e": [{"date": "2026-03-25", "title": "Meeting"}],
        })
        assert "dj-calendar" in html
        assert "March" in html
        assert "2026" in html
        assert "Meeting" in html

    def test_empty_events(self):
        html = render('{% calendar events=e month=1 year=2026 %}', {"e": []})
        assert "dj-calendar" in html
        assert "January" in html

    def test_day_numbers(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {"e": []})
        assert "dj-calendar__daynum" in html

    def test_role_grid(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {"e": []})
        assert 'role="grid"' in html

    def test_custom_class(self):
        html = render('{% calendar events=e month=1 year=2026 class="wide" %}', {"e": []})
        assert "wide" in html

    def test_multiple_events_same_day(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {
            "e": [
                {"date": "2026-03-25", "title": "A"},
                {"date": "2026-03-25", "title": "B"},
            ],
        })
        assert "A" in html
        assert "B" in html

    def test_overflow_events(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {
            "e": [
                {"date": "2026-03-01", "title": "A"},
                {"date": "2026-03-01", "title": "B"},
                {"date": "2026-03-01", "title": "C"},
                {"date": "2026-03-01", "title": "D"},
            ],
        })
        assert "+1 more" in html

    def test_event_color(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {
            "e": [{"date": "2026-03-25", "title": "X", "color": "#ff0000"}],
        })
        assert "#ff0000" in html


class TestCalendarViewClass:
    def test_basic_render(self):
        c = CalendarView(
            events=[{"date": "2026-03-25", "title": "Test"}],
            month=3, year=2026,
        )
        html = str(c)
        assert "dj-calendar" in html
        assert "Test" in html
        assert "March" in html

    def test_empty(self):
        c = CalendarView(events=[], month=1, year=2026)
        html = str(c)
        assert "dj-calendar" in html

    def test_custom_class(self):
        c = CalendarView(events=[], month=1, year=2026, custom_class="extra")
        html = str(c)
        assert "extra" in html


# ===========================================================================
# Gantt Chart — Template Tag
# ===========================================================================

class TestGanttChartTag:
    def test_basic(self):
        html = render('{% gantt_chart tasks=t %}', {
            "t": [
                {"name": "Design", "start": 0, "duration": 3},
                {"name": "Develop", "start": 2, "duration": 5},
            ],
        })
        assert "dj-gantt" in html
        assert "dj-gantt__bar" in html
        assert "Design" in html
        assert "Develop" in html

    def test_empty_tasks(self):
        html = render('{% gantt_chart tasks=t %}', {"t": []})
        assert "dj-gantt" in html
        assert "<svg></svg>" in html

    def test_with_title(self):
        html = render('{% gantt_chart tasks=t title="Timeline" %}', {
            "t": [{"name": "A", "start": 0, "duration": 2}],
        })
        assert "Timeline" in html
        assert "dj-gantt__title" in html

    def test_aria_label(self):
        html = render('{% gantt_chart tasks=t %}', {
            "t": [{"name": "A", "start": 0, "duration": 1}],
        })
        assert 'role="img"' in html
        assert 'aria-label=' in html

    def test_custom_class(self):
        html = render('{% gantt_chart tasks=t class="wide" %}', {
            "t": [{"name": "A", "start": 0, "duration": 1}],
        })
        assert "wide" in html

    def test_progress(self):
        html = render('{% gantt_chart tasks=t %}', {
            "t": [{"name": "A", "start": 0, "duration": 4, "progress": 0.5}],
        })
        assert "dj-gantt__progress" in html

    def test_svg_structure(self):
        html = render('{% gantt_chart tasks=t %}', {
            "t": [{"name": "A", "start": 0, "duration": 2}],
        })
        assert "<svg" in html
        assert "</svg>" in html


class TestGanttChartClass:
    def test_basic_render(self):
        c = GanttChart(tasks=[
            {"name": "Design", "start": 0, "duration": 3},
        ])
        html = str(c)
        assert "dj-gantt" in html
        assert "Design" in html

    def test_empty(self):
        c = GanttChart(tasks=[])
        html = str(c)
        assert "<svg></svg>" in html

    def test_title(self):
        c = GanttChart(tasks=[{"name": "A", "start": 0, "duration": 1}], title="Plan")
        html = str(c)
        assert "Plan" in html


# ===========================================================================
# Diff Viewer — Template Tag
# ===========================================================================

class TestDiffViewerTag:
    def test_basic_split(self):
        html = render('{% diff_viewer old=o new=n %}', {
            "o": "Hello\nWorld",
            "n": "Hello\nEarth",
        })
        assert "dj-diff" in html
        assert "dj-diff--split" in html
        assert "dj-diff__pane--old" in html
        assert "dj-diff__pane--new" in html

    def test_unified_mode(self):
        html = render('{% diff_viewer old=o new=n mode="unified" %}', {
            "o": "A\nB",
            "n": "A\nC",
        })
        assert "dj-diff--unified" in html
        assert "dj-diff__unified" in html

    def test_line_numbers(self):
        html = render('{% diff_viewer old=o new=n %}', {
            "o": "Line1\nLine2",
            "n": "Line1\nLine2",
        })
        assert "dj-diff__num" in html

    def test_added_line(self):
        html = render('{% diff_viewer old=o new=n %}', {
            "o": "A",
            "n": "A\nB",
        })
        assert "dj-diff__line--add" in html

    def test_deleted_line(self):
        html = render('{% diff_viewer old=o new=n %}', {
            "o": "A\nB",
            "n": "A",
        })
        assert "dj-diff__line--del" in html

    def test_custom_titles(self):
        html = render('{% diff_viewer old=o new=n title_old="Before" title_new="After" %}', {
            "o": "X",
            "n": "Y",
        })
        assert "Before" in html
        assert "After" in html

    def test_custom_class(self):
        html = render('{% diff_viewer old=o new=n class="wide" %}', {
            "o": "A",
            "n": "A",
        })
        assert "wide" in html

    def test_empty_diff(self):
        html = render('{% diff_viewer old=o new=n %}', {"o": "", "n": ""})
        assert "dj-diff" in html


class TestDiffViewerClass:
    def test_basic_render(self):
        c = DiffViewer(old="Hello\nWorld", new="Hello\nEarth")
        html = str(c)
        assert "dj-diff" in html
        assert "dj-diff__pane--old" in html

    def test_unified(self):
        c = DiffViewer(old="A", new="B", mode="unified")
        html = str(c)
        assert "dj-diff--unified" in html

    def test_empty(self):
        c = DiffViewer(old="", new="")
        html = str(c)
        assert "dj-diff" in html


# ===========================================================================
# Pivot Table — Template Tag
# ===========================================================================

PIVOT_DATA = [
    {"category": "A", "quarter": "Q1", "revenue": 100},
    {"category": "A", "quarter": "Q2", "revenue": 150},
    {"category": "B", "quarter": "Q1", "revenue": 200},
    {"category": "B", "quarter": "Q2", "revenue": 250},
]


class TestPivotTableTag:
    def test_basic(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" %}', {
            "d": PIVOT_DATA,
        })
        assert "dj-pivot" in html
        assert "dj-pivot__cell" in html
        assert "Q1" in html
        assert "Q2" in html
        assert "100" in html

    def test_totals(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" %}', {
            "d": PIVOT_DATA,
        })
        assert "Total" in html
        assert "dj-pivot__grand-total" in html

    def test_with_title(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" title="Report" %}', {
            "d": PIVOT_DATA,
        })
        assert "Report" in html
        assert "dj-pivot__title" in html

    def test_empty_data(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" %}', {
            "d": [],
        })
        assert "dj-pivot" in html
        assert "dj-pivot__table" in html

    def test_custom_class(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" class="report" %}', {
            "d": PIVOT_DATA,
        })
        assert "report" in html

    def test_role_grid(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" %}', {
            "d": PIVOT_DATA,
        })
        assert 'role="grid"' in html

    def test_agg_count(self):
        html = render('{% pivot_table data=d rows="category" cols="quarter" values="revenue" agg="count" %}', {
            "d": PIVOT_DATA,
        })
        assert "dj-pivot__cell" in html
        # Each cell should have count=1
        assert ">1<" in html


class TestPivotTableClass:
    def test_basic_render(self):
        c = PivotTable(data=PIVOT_DATA, rows="category", cols="quarter", values="revenue")
        html = str(c)
        assert "dj-pivot" in html
        assert "100" in html

    def test_empty(self):
        c = PivotTable(data=[], rows="x", cols="y", values="z")
        html = str(c)
        assert "dj-pivot" in html

    def test_avg_aggregation(self):
        c = PivotTable(
            data=[
                {"x": "a", "y": "b", "v": 10},
                {"x": "a", "y": "b", "v": 20},
            ],
            rows="x", cols="y", values="v", agg="avg",
        )
        html = str(c)
        assert "15" in html


# ===========================================================================
# Org Chart — Template Tag
# ===========================================================================

ORG_NODES = [
    {"id": "ceo", "name": "Alice Smith", "title": "CEO"},
    {"id": "cto", "name": "Bob Jones", "title": "CTO", "parent": "ceo"},
    {"id": "dev1", "name": "Carol Lee", "title": "Developer", "parent": "cto"},
]


class TestOrgChartTag:
    def test_basic(self):
        html = render('{% org_chart nodes=n root="ceo" %}', {"n": ORG_NODES})
        assert "dj-org" in html
        assert "Alice Smith" in html
        assert "Bob Jones" in html
        assert "Carol Lee" in html

    def test_role_tree(self):
        html = render('{% org_chart nodes=n root="ceo" %}', {"n": ORG_NODES})
        assert 'role="tree"' in html

    def test_hierarchy(self):
        html = render('{% org_chart nodes=n root="ceo" %}', {"n": ORG_NODES})
        assert "dj-org__children" in html

    def test_auto_root(self):
        html = render('{% org_chart nodes=n %}', {"n": ORG_NODES})
        assert "Alice Smith" in html

    def test_empty(self):
        html = render('{% org_chart nodes=n %}', {"n": []})
        assert "dj-org" in html

    def test_custom_class(self):
        html = render('{% org_chart nodes=n root="ceo" class="wide" %}', {"n": ORG_NODES})
        assert "wide" in html

    def test_initials(self):
        html = render('{% org_chart nodes=n root="ceo" %}', {"n": ORG_NODES})
        assert "dj-org__initials" in html
        assert "AS" in html  # Alice Smith initials

    def test_horizontal(self):
        html = render('{% org_chart nodes=n root="ceo" direction="horizontal" %}', {"n": ORG_NODES})
        assert "dj-org--horizontal" in html


class TestOrgChartClass:
    def test_basic_render(self):
        c = OrgChart(nodes=ORG_NODES, root="ceo")
        html = str(c)
        assert "dj-org" in html
        assert "Alice Smith" in html

    def test_empty(self):
        c = OrgChart(nodes=[])
        html = str(c)
        assert "dj-org" in html

    def test_auto_root(self):
        c = OrgChart(nodes=ORG_NODES)
        html = str(c)
        assert "Alice Smith" in html


# ===========================================================================
# Comparison Table — Template Tag
# ===========================================================================

PLANS = [
    {"name": "Free", "price": "$0/mo"},
    {"name": "Pro", "price": "$19/mo", "highlighted": True},
    {"name": "Enterprise", "price": "Contact us"},
]
FEATURES = [
    {"name": "Users", "values": ["1", "10", "Unlimited"]},
    {"name": "API Access", "values": [False, True, True]},
    {"name": "SSO", "values": [False, False, True]},
]


class TestComparisonTableTag:
    def test_basic(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert "dj-compare" in html
        assert "Free" in html
        assert "Pro" in html
        assert "Enterprise" in html

    def test_feature_names(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert "Users" in html
        assert "API Access" in html

    def test_boolean_values(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert "dj-compare__check" in html
        assert "dj-compare__cross" in html

    def test_highlighted(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert "dj-compare__plan--highlighted" in html

    def test_prices(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert "$0/mo" in html
        assert "$19/mo" in html

    def test_empty_plans(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": [], "f": FEATURES,
        })
        assert "dj-compare" in html

    def test_custom_class(self):
        html = render('{% comparison_table plans=p features=f class="pricing" %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert "pricing" in html

    def test_role_grid(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": PLANS, "f": FEATURES,
        })
        assert 'role="grid"' in html


class TestComparisonTableClass:
    def test_basic_render(self):
        c = ComparisonTable(plans=PLANS, features=FEATURES)
        html = str(c)
        assert "dj-compare" in html
        assert "Free" in html

    def test_empty(self):
        c = ComparisonTable(plans=[], features=[])
        html = str(c)
        assert "dj-compare" in html

    def test_boolean_rendering(self):
        c = ComparisonTable(
            plans=[{"name": "A"}],
            features=[{"name": "F", "values": [True]}],
        )
        html = str(c)
        assert "dj-compare__check" in html


# ===========================================================================
# Masonry Grid — Template Tag
# ===========================================================================

class TestMasonryGridTag:
    def test_basic(self):
        html = render('{% masonry_grid items=it columns=3 %}', {
            "it": [
                {"content": "<p>Card 1</p>", "height": 200},
                {"content": "<p>Card 2</p>", "height": 150},
            ],
        })
        assert "dj-masonry" in html
        assert "dj-masonry__item" in html
        assert "Card 1" in html

    def test_empty_items(self):
        html = render('{% masonry_grid items=it %}', {"it": []})
        assert "dj-masonry" in html

    def test_columns(self):
        html = render('{% masonry_grid items=it columns=4 %}', {
            "it": [{"content": "A"}, {"content": "B"}, {"content": "C"}, {"content": "D"}],
        })
        assert "--dj-masonry-columns: 4" in html

    def test_gap(self):
        html = render('{% masonry_grid items=it gap=24 %}', {
            "it": [{"content": "A"}],
        })
        assert "--dj-masonry-gap: 24px" in html

    def test_custom_class(self):
        html = render('{% masonry_grid items=it class="gallery" %}', {
            "it": [{"content": "A"}],
        })
        assert "gallery" in html

    def test_role_list(self):
        html = render('{% masonry_grid items=it %}', {
            "it": [{"content": "A"}],
        })
        assert 'role="list"' in html

    def test_column_distribution(self):
        html = render('{% masonry_grid items=it columns=2 %}', {
            "it": [{"content": "A", "height": 100}, {"content": "B", "height": 100}],
        })
        assert html.count("dj-masonry__col") == 2


class TestMasonryGridClass:
    def test_basic_render(self):
        c = MasonryGrid(items=[{"content": "<p>Hello</p>"}], columns=3)
        html = str(c)
        assert "dj-masonry" in html
        assert "Hello" in html

    def test_empty(self):
        c = MasonryGrid(items=[])
        html = str(c)
        assert "dj-masonry" in html

    def test_columns(self):
        c = MasonryGrid(items=[{"content": "A"}], columns=4)
        html = str(c)
        assert "--dj-masonry-columns: 4" in html


# ===========================================================================
# XSS Tests
# ===========================================================================

class TestXSSEscaping:
    """Verify that user-controlled values are properly escaped."""

    XSS_SCRIPT = '<script>alert("xss")</script>'
    XSS_ATTR = '" onmouseover="alert(1)"'

    # Calendar View
    def test_calendar_event_title_xss(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {
            "e": [{"date": "2026-03-25", "title": self.XSS_SCRIPT}],
        })
        assert "<script>" not in html

    def test_calendar_class_xss(self):
        html = render('{% calendar events=e month=3 year=2026 class=c %}', {
            "e": [], "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    def test_calendar_event_color_xss(self):
        html = render('{% calendar events=e month=3 year=2026 %}', {
            "e": [{"date": "2026-03-25", "title": "X", "color": self.XSS_ATTR}],
        })
        assert 'onmouseover' not in html or '&quot;' in html

    # Gantt Chart
    def test_gantt_title_xss(self):
        html = render('{% gantt_chart tasks=t title=x %}', {
            "t": [{"name": "A", "start": 0, "duration": 1}], "x": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_gantt_task_name_xss(self):
        html = render('{% gantt_chart tasks=t %}', {
            "t": [{"name": self.XSS_SCRIPT, "start": 0, "duration": 1}],
        })
        assert "<script>" not in html

    def test_gantt_class_xss(self):
        html = render('{% gantt_chart tasks=t class=c %}', {
            "t": [{"name": "A", "start": 0, "duration": 1}], "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    # Diff Viewer
    def test_diff_title_old_xss(self):
        html = render('{% diff_viewer old=o new=n title_old=t %}', {
            "o": "A", "n": "B", "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_diff_content_xss(self):
        html = render('{% diff_viewer old=o new=n %}', {
            "o": self.XSS_SCRIPT, "n": "safe",
        })
        assert "<script>" not in html

    def test_diff_class_xss(self):
        html = render('{% diff_viewer old=o new=n class=c %}', {
            "o": "A", "n": "A", "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    # Pivot Table
    def test_pivot_title_xss(self):
        html = render('{% pivot_table data=d rows="x" cols="y" values="v" title=t %}', {
            "d": [{"x": "a", "y": "b", "v": 1}], "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_pivot_row_value_xss(self):
        html = render('{% pivot_table data=d rows="x" cols="y" values="v" %}', {
            "d": [{"x": self.XSS_SCRIPT, "y": "b", "v": 1}],
        })
        assert "<script>" not in html

    def test_pivot_col_value_xss(self):
        html = render('{% pivot_table data=d rows="x" cols="y" values="v" %}', {
            "d": [{"x": "a", "y": self.XSS_SCRIPT, "v": 1}],
        })
        assert "<script>" not in html

    # Org Chart
    def test_org_name_xss(self):
        html = render('{% org_chart nodes=n %}', {
            "n": [{"id": "1", "name": self.XSS_SCRIPT, "title": "CEO"}],
        })
        assert "<script>" not in html

    def test_org_title_xss(self):
        html = render('{% org_chart nodes=n %}', {
            "n": [{"id": "1", "name": "Alice", "title": self.XSS_SCRIPT}],
        })
        assert "<script>" not in html

    def test_org_class_xss(self):
        html = render('{% org_chart nodes=n class=c %}', {
            "n": [{"id": "1", "name": "A", "title": "B"}], "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    # Comparison Table
    def test_compare_plan_name_xss(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": [{"name": self.XSS_SCRIPT}],
            "f": [{"name": "F", "values": ["x"]}],
        })
        assert "<script>" not in html

    def test_compare_feature_name_xss(self):
        html = render('{% comparison_table plans=p features=f %}', {
            "p": [{"name": "A"}],
            "f": [{"name": self.XSS_SCRIPT, "values": ["x"]}],
        })
        assert "<script>" not in html

    def test_compare_class_xss(self):
        html = render('{% comparison_table plans=p features=f class=c %}', {
            "p": [{"name": "A"}],
            "f": [{"name": "F", "values": ["x"]}],
            "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    # Masonry Grid
    def test_masonry_class_xss(self):
        html = render('{% masonry_grid items=it class=c %}', {
            "it": [{"content": "A"}], "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    def test_masonry_item_class_xss(self):
        html = render('{% masonry_grid items=it %}', {
            "it": [{"content": "A", "class": self.XSS_ATTR}],
        })
        assert 'onmouseover' not in html or '&quot;' in html
