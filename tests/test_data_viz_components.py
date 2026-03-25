"""Tests for data visualization components — template tags, component classes, and XSS."""
import types
import sys

# Stub djust before importing components
_stub = types.ModuleType("djust")


class _Component:
    def __init__(self, **kwargs):
        pass

    def __html__(self):
        return self._render_custom()

    def __str__(self):
        return self._render_custom()


class _LV:
    pass


_stub.Component = _Component
_stub.LiveView = _LV
sys.modules.setdefault("djust", _stub)

# Stub djust.decorators
_dec_stub = types.ModuleType("djust.decorators")


def _event_handler(fn):
    return fn


_dec_stub.event_handler = _event_handler
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

from django.template import Template, Context
import pytest

from djust_components.components import (
    BarChart,
    LineChart,
    PieChart,
    Sparkline,
    Heatmap,
    Treemap,
    CalendarHeatmap,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Bar Chart — Template Tag
# ===========================================================================

class TestBarChartTag:
    def test_basic(self):
        html = render('{% bar_chart data=d labels=l %}', {
            "d": [10, 20, 30], "l": ["A", "B", "C"]
        })
        assert "dj-bar-chart" in html
        assert "dj-bar-chart__bar" in html
        assert "<svg" in html

    def test_with_title(self):
        html = render('{% bar_chart data=d title="Sales" %}', {"d": [10, 20]})
        assert "Sales" in html
        assert "dj-bar-chart__title" in html

    def test_empty_data(self):
        html = render('{% bar_chart data=d %}', {"d": []})
        assert "dj-bar-chart" in html
        assert "<svg></svg>" in html

    def test_custom_class(self):
        html = render('{% bar_chart data=d class="extra" %}', {"d": [5]})
        assert "extra" in html

    def test_labels_in_output(self):
        html = render('{% bar_chart data=d labels=l %}', {
            "d": [10, 20], "l": ["Mon", "Tue"]
        })
        assert "Mon" in html
        assert "Tue" in html

    def test_show_values(self):
        html = render('{% bar_chart data=d %}', {"d": [42]})
        assert "42" in html

    def test_aria_label(self):
        html = render('{% bar_chart data=d %}', {"d": [1]})
        assert 'role="img"' in html
        assert 'aria-label=' in html

    def test_variable_data(self):
        html = render('{% bar_chart data=d %}', {"d": [100, 200, 300]})
        assert "dj-bar-chart__bar" in html


class TestBarChartClass:
    def test_basic_render(self):
        c = BarChart(data=[10, 20, 30], labels=["A", "B", "C"])
        html = str(c)
        assert "dj-bar-chart" in html
        assert "dj-bar-chart__bar" in html

    def test_title(self):
        c = BarChart(data=[10], title="Revenue")
        html = str(c)
        assert "Revenue" in html

    def test_custom_color(self):
        c = BarChart(data=[10], color="#ff0000")
        html = str(c)
        assert "#ff0000" in html

    def test_empty(self):
        c = BarChart(data=[])
        html = str(c)
        assert "dj-bar-chart" in html


# ===========================================================================
# Line Chart — Template Tag
# ===========================================================================

class TestLineChartTag:
    def test_basic(self):
        html = render('{% line_chart series=s labels=l %}', {
            "s": [{"name": "Rev", "data": [10, 20, 30]}],
            "l": ["Jan", "Feb", "Mar"],
        })
        assert "dj-line-chart" in html
        assert "dj-line-chart__line" in html

    def test_with_title(self):
        html = render('{% line_chart series=s title="Trend" %}', {
            "s": [{"name": "A", "data": [1, 2]}]
        })
        assert "Trend" in html

    def test_multiple_series(self):
        html = render('{% line_chart series=s %}', {
            "s": [
                {"name": "A", "data": [1, 2, 3]},
                {"name": "B", "data": [3, 2, 1]},
            ]
        })
        assert html.count("dj-line-chart__line") == 2

    def test_empty_series(self):
        html = render('{% line_chart series=s %}', {"s": []})
        assert "<svg></svg>" in html

    def test_dots(self):
        html = render('{% line_chart series=s %}', {
            "s": [{"name": "A", "data": [1, 2, 3]}]
        })
        assert "dj-line-chart__dot" in html

    def test_legend(self):
        html = render('{% line_chart series=s %}', {
            "s": [{"name": "Revenue", "data": [1, 2]}]
        })
        assert "Revenue" in html

    def test_custom_class(self):
        html = render('{% line_chart series=s class="wide" %}', {
            "s": [{"name": "A", "data": [1]}]
        })
        assert "wide" in html


class TestLineChartClass:
    def test_basic_render(self):
        c = LineChart(series=[{"name": "A", "data": [10, 20, 30]}])
        html = str(c)
        assert "dj-line-chart__line" in html

    def test_area_mode(self):
        c = LineChart(series=[{"name": "A", "data": [10, 20]}], area=True)
        html = str(c)
        assert "dj-line-chart__area" in html


# ===========================================================================
# Pie / Donut Chart — Template Tag
# ===========================================================================

class TestPieChartTag:
    def test_basic(self):
        html = render('{% pie_chart segments=s %}', {
            "s": [
                {"label": "A", "value": 60},
                {"label": "B", "value": 40},
            ]
        })
        assert "dj-pie-chart" in html
        assert "dj-pie-chart__segment" in html

    def test_with_title(self):
        html = render('{% pie_chart segments=s title="Share" %}', {
            "s": [{"label": "X", "value": 100}]
        })
        assert "Share" in html

    def test_donut(self):
        html = render('{% pie_chart segments=s donut=True %}', {
            "s": [{"label": "A", "value": 50}, {"label": "B", "value": 50}]
        })
        assert "dj-pie-chart__segment" in html

    def test_labels_shown(self):
        html = render('{% pie_chart segments=s %}', {
            "s": [{"label": "Big", "value": 80}, {"label": "Small", "value": 20}]
        })
        assert "dj-pie-chart__pct" in html

    def test_empty_segments(self):
        html = render('{% pie_chart segments=s %}', {"s": []})
        assert "<svg></svg>" in html

    def test_legend(self):
        html = render('{% pie_chart segments=s %}', {
            "s": [{"label": "Desktop", "value": 60}]
        })
        assert "Desktop" in html

    def test_custom_class(self):
        html = render('{% pie_chart segments=s class="round" %}', {
            "s": [{"label": "A", "value": 100}]
        })
        assert "round" in html


class TestPieChartClass:
    def test_basic_render(self):
        c = PieChart(segments=[{"label": "A", "value": 60}, {"label": "B", "value": 40}])
        html = str(c)
        assert "dj-pie-chart__segment" in html

    def test_donut_mode(self):
        c = PieChart(segments=[{"label": "A", "value": 50}], donut=True)
        html = str(c)
        assert "dj-pie-chart" in html


# ===========================================================================
# Sparkline — Template Tag
# ===========================================================================

class TestSparklineTag:
    def test_basic_line(self):
        html = render('{% sparkline data=d %}', {"d": [3, 7, 4, 8, 2]})
        assert "dj-sparkline" in html
        assert "dj-sparkline__line" in html

    def test_bar_variant(self):
        html = render('{% sparkline data=d variant="bar" %}', {"d": [3, 7, 4]})
        assert "dj-sparkline__bar" in html

    def test_area_variant(self):
        html = render('{% sparkline data=d variant="area" %}', {"d": [1, 3, 2]})
        assert "dj-sparkline__area" in html
        assert "dj-sparkline__line" in html

    def test_empty_data(self):
        html = render('{% sparkline data=d %}', {"d": []})
        assert "<svg></svg>" in html

    def test_custom_color(self):
        html = render('{% sparkline data=d color="#ff0000" %}', {"d": [1, 2, 3]})
        assert "#ff0000" in html

    def test_custom_class(self):
        html = render('{% sparkline data=d class="inline" %}', {"d": [1]})
        assert "inline" in html

    def test_span_wrapper(self):
        """Sparklines use <span> not <div> for inline use."""
        html = render('{% sparkline data=d %}', {"d": [1, 2]})
        assert "<span" in html


class TestSparklineClass:
    def test_basic_render(self):
        c = Sparkline(data=[3, 7, 4, 8])
        html = str(c)
        assert "dj-sparkline__line" in html

    def test_bar_variant(self):
        c = Sparkline(data=[1, 2, 3], variant="bar")
        html = str(c)
        assert "dj-sparkline__bar" in html


# ===========================================================================
# Heatmap — Template Tag
# ===========================================================================

class TestHeatmapTag:
    def test_basic(self):
        html = render('{% heatmap data=d x_labels=x y_labels=y %}', {
            "d": [[1, 2], [3, 4]],
            "x": ["A", "B"],
            "y": ["Row1", "Row2"],
        })
        assert "dj-heatmap" in html
        assert "dj-heatmap__cell" in html

    def test_with_title(self):
        html = render('{% heatmap data=d title="Activity" %}', {
            "d": [[1, 2], [3, 4]]
        })
        assert "Activity" in html

    def test_labels(self):
        html = render('{% heatmap data=d x_labels=x y_labels=y %}', {
            "d": [[5]], "x": ["Col"], "y": ["Row"],
        })
        assert "Col" in html
        assert "Row" in html

    def test_empty_data(self):
        html = render('{% heatmap data=d %}', {"d": []})
        assert "<svg></svg>" in html

    def test_values_shown(self):
        html = render('{% heatmap data=d %}', {"d": [[42]]})
        assert "42" in html

    def test_custom_class(self):
        html = render('{% heatmap data=d class="grid" %}', {"d": [[1]]})
        assert "grid" in html


class TestHeatmapClass:
    def test_basic_render(self):
        c = Heatmap(data=[[1, 2], [3, 4]], x_labels=["A", "B"], y_labels=["R1", "R2"])
        html = str(c)
        assert "dj-heatmap__cell" in html

    def test_color_interpolation(self):
        color = Heatmap._interpolate_color("#000000", "#ffffff", 0.5)
        # Should be roughly middle gray
        assert color.startswith("#")
        r = int(color[1:3], 16)
        assert 120 <= r <= 136  # ~127


# ===========================================================================
# Treemap — Template Tag
# ===========================================================================

class TestTreemapTag:
    def test_basic(self):
        html = render('{% treemap data=d %}', {
            "d": [
                {"name": "JS", "size": 45},
                {"name": "Python", "size": 30},
            ]
        })
        assert "dj-treemap" in html
        assert "dj-treemap__cell" in html

    def test_with_title(self):
        html = render('{% treemap data=d title="Languages" %}', {
            "d": [{"name": "Rust", "size": 10}]
        })
        assert "Languages" in html

    def test_custom_keys(self):
        html = render('{% treemap data=d value_key="count" label_key="lang" %}', {
            "d": [{"lang": "Go", "count": 20}]
        })
        assert "Go" in html

    def test_empty_data(self):
        html = render('{% treemap data=d %}', {"d": []})
        assert "<svg></svg>" in html

    def test_labels_in_cells(self):
        html = render('{% treemap data=d %}', {
            "d": [{"name": "Big", "size": 100}]
        })
        assert "dj-treemap__label" in html

    def test_custom_class(self):
        html = render('{% treemap data=d class="viz" %}', {
            "d": [{"name": "A", "size": 10}]
        })
        assert "viz" in html


class TestTreemapClass:
    def test_basic_render(self):
        c = Treemap(data=[{"name": "A", "size": 50}, {"name": "B", "size": 50}])
        html = str(c)
        assert "dj-treemap__cell" in html

    def test_custom_keys(self):
        c = Treemap(data=[{"label": "X", "count": 10}], value_key="count", label_key="label")
        html = str(c)
        assert "X" in html


# ===========================================================================
# Calendar Heatmap — Template Tag
# ===========================================================================

class TestCalendarHeatmapTag:
    def test_basic(self):
        html = render('{% calendar_heatmap data=d year=2026 %}', {
            "d": {"2026-01-01": 3, "2026-06-15": 7},
        })
        assert "dj-calendar-heatmap" in html
        assert "dj-calendar-heatmap__cell" in html

    def test_with_title(self):
        html = render('{% calendar_heatmap data=d year=2026 title="Contributions" %}', {
            "d": {"2026-01-01": 1}
        })
        assert "Contributions" in html

    def test_month_labels(self):
        html = render('{% calendar_heatmap data=d year=2026 %}', {
            "d": {}
        })
        assert "Jan" in html
        assert "Dec" in html

    def test_day_labels(self):
        html = render('{% calendar_heatmap data=d year=2026 %}', {
            "d": {}
        })
        assert "Mon" in html
        assert "Wed" in html
        assert "Fri" in html

    def test_empty_data(self):
        html = render('{% calendar_heatmap data=d year=2026 %}', {"d": {}})
        assert "dj-calendar-heatmap__cell" in html  # Still renders empty grid

    def test_custom_class(self):
        html = render('{% calendar_heatmap data=d year=2026 class="contrib" %}', {
            "d": {}
        })
        assert "contrib" in html

    def test_aria_label(self):
        html = render('{% calendar_heatmap data=d year=2026 %}', {"d": {}})
        assert 'role="img"' in html

    def test_color_levels(self):
        """Cells with data should get colored (not the empty color)."""
        html = render('{% calendar_heatmap data=d year=2026 %}', {
            "d": {"2026-03-15": 10}
        })
        # The cell for 2026-03-15 should have a non-empty color
        assert "#216e39" in html or "#30a14e" in html or "#40c463" in html or "#9be9a8" in html


class TestCalendarHeatmapClass:
    def test_basic_render(self):
        c = CalendarHeatmap(data={"2026-01-01": 5}, year=2026)
        html = str(c)
        assert "dj-calendar-heatmap__cell" in html

    def test_empty_data(self):
        c = CalendarHeatmap(data={}, year=2026)
        html = str(c)
        assert "dj-calendar-heatmap" in html


# ===========================================================================
# XSS Tests
# ===========================================================================

class TestXSSEscaping:
    """Verify that user-controlled values are properly escaped."""

    XSS_SCRIPT = '<script>alert("xss")</script>'
    XSS_ATTR = '" onmouseover="alert(1)"'

    def test_bar_chart_title_xss(self):
        html = render('{% bar_chart data=d title=t %}', {
            "d": [10], "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&#" in html

    def test_bar_chart_label_xss(self):
        html = render('{% bar_chart data=d labels=l %}', {
            "d": [10], "l": [self.XSS_SCRIPT],
        })
        assert "<script>" not in html

    def test_bar_chart_class_xss(self):
        html = render('{% bar_chart data=d class=c %}', {
            "d": [10], "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    def test_line_chart_title_xss(self):
        html = render('{% line_chart series=s title=t %}', {
            "s": [{"name": "A", "data": [1]}], "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_line_chart_series_name_xss(self):
        html = render('{% line_chart series=s %}', {
            "s": [{"name": self.XSS_SCRIPT, "data": [1, 2]}],
        })
        assert "<script>" not in html

    def test_line_chart_label_xss(self):
        html = render('{% line_chart series=s labels=l %}', {
            "s": [{"name": "A", "data": [1]}], "l": [self.XSS_SCRIPT],
        })
        assert "<script>" not in html

    def test_pie_chart_title_xss(self):
        html = render('{% pie_chart segments=s title=t %}', {
            "s": [{"label": "A", "value": 100}], "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_pie_chart_label_xss(self):
        html = render('{% pie_chart segments=s %}', {
            "s": [{"label": self.XSS_SCRIPT, "value": 100}],
        })
        assert "<script>" not in html

    def test_sparkline_class_xss(self):
        html = render('{% sparkline data=d class=c %}', {
            "d": [1, 2], "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html

    def test_heatmap_title_xss(self):
        html = render('{% heatmap data=d title=t %}', {
            "d": [[1]], "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_heatmap_xlabel_xss(self):
        html = render('{% heatmap data=d x_labels=x %}', {
            "d": [[1]], "x": [self.XSS_SCRIPT],
        })
        assert "<script>" not in html

    def test_heatmap_ylabel_xss(self):
        html = render('{% heatmap data=d y_labels=y %}', {
            "d": [[1]], "y": [self.XSS_SCRIPT],
        })
        assert "<script>" not in html

    def test_treemap_title_xss(self):
        html = render('{% treemap data=d title=t %}', {
            "d": [{"name": "A", "size": 10}], "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_treemap_label_xss(self):
        html = render('{% treemap data=d %}', {
            "d": [{"name": self.XSS_SCRIPT, "size": 100}],
        })
        assert "<script>" not in html

    def test_calendar_heatmap_title_xss(self):
        html = render('{% calendar_heatmap data=d year=2026 title=t %}', {
            "d": {}, "t": self.XSS_SCRIPT,
        })
        assert "<script>" not in html

    def test_calendar_heatmap_class_xss(self):
        html = render('{% calendar_heatmap data=d year=2026 class=c %}', {
            "d": {}, "c": self.XSS_ATTR,
        })
        assert 'onmouseover' not in html or '&quot;' in html
