"""Tests for AI trust/transparency components — template tags, component classes, and XSS."""
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


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Approval Gate — Template Tag
# ===========================================================================

class TestApprovalGate:
    def test_basic_render(self):
        html = render('{% approval_gate message="Delete 47 records?" risk="high" approve_event="confirm" reject_event="cancel" %}')
        assert "dj-approval" in html
        assert "dj-approval--high" in html
        assert "Delete 47 records?" in html
        assert 'dj-click="confirm"' in html
        assert 'dj-click="cancel"' in html

    def test_risk_levels(self):
        for risk in ("low", "medium", "high", "critical"):
            html = render(f'{{% approval_gate message="test" risk="{risk}" %}}')
            assert f"dj-approval--{risk}" in html

    def test_invalid_risk_defaults_to_medium(self):
        html = render('{% approval_gate message="test" risk="bogus" %}')
        assert "dj-approval--medium" in html

    def test_custom_labels(self):
        html = render(
            '{% approval_gate message="Deploy?" approve_label="Deploy Now" reject_label="Abort" %}'
        )
        assert "Deploy Now" in html
        assert "Abort" in html

    def test_default_labels(self):
        html = render('{% approval_gate message="test" %}')
        assert "Approve" in html
        assert "Reject" in html

    def test_role_alert(self):
        html = render('{% approval_gate message="test" %}')
        assert 'role="alert"' in html

    def test_risk_label_displayed(self):
        html = render('{% approval_gate message="test" risk="critical" %}')
        assert "Critical Risk" in html

    def test_icon_rendered(self):
        html = render('{% approval_gate message="test" risk="high" %}')
        assert "dj-approval__icon" in html
        assert "<svg" in html

    def test_custom_class(self):
        html = render('{% approval_gate message="test" class="my-gate" %}')
        assert "my-gate" in html


# ===========================================================================
# Approval Gate — Component Class
# ===========================================================================

class TestApprovalGateClass:
    def test_basic_render(self):
        from djust_components.components.approval_gate import ApprovalGate
        gate = ApprovalGate(
            message="Delete records?",
            risk="high",
            approve_event="confirm",
            reject_event="cancel",
        )
        html = gate._render_custom()
        assert "dj-approval--high" in html
        assert "Delete records?" in html
        assert 'dj-click="confirm"' in html
        assert 'dj-click="cancel"' in html

    def test_invalid_risk(self):
        from djust_components.components.approval_gate import ApprovalGate
        gate = ApprovalGate(risk="invalid")
        html = gate._render_custom()
        assert "dj-approval--medium" in html

    def test_custom_labels(self):
        from djust_components.components.approval_gate import ApprovalGate
        gate = ApprovalGate(approve_label="Yes", reject_label="No")
        html = gate._render_custom()
        assert "Yes" in html
        assert "No" in html


# ===========================================================================
# Source Citation — Template Tag
# ===========================================================================

class TestSourceCitation:
    def test_basic_render(self):
        html = render('{% source_citation index="1" title="API Docs" url=url relevance=rel %}',
                       {"url": "https://docs.example.com", "rel": 0.92})
        assert "dj-citation" in html
        assert "[1]" in html
        assert "API Docs" in html
        assert "https://docs.example.com" in html
        assert "Relevance: 92%" in html

    def test_marker_index(self):
        html = render('{% source_citation index="3" title="Test" %}')
        assert "[3]" in html

    def test_no_url(self):
        html = render('{% source_citation index="1" title="Local Source" %}')
        assert "dj-citation__url" not in html
        assert "Local Source" in html

    def test_no_relevance(self):
        html = render('{% source_citation index="1" title="Test" %}')
        assert "dj-citation__relevance" not in html

    def test_popover_structure(self):
        html = render('{% source_citation index="1" title="Test" %}')
        assert "dj-citation__popover" in html
        assert "dj-citation__marker" in html

    def test_custom_class(self):
        html = render('{% source_citation index="1" title="T" class="my-cite" %}')
        assert "my-cite" in html


# ===========================================================================
# Source Citation — Component Class
# ===========================================================================

class TestSourceCitationClass:
    def test_basic_render(self):
        from djust_components.components.source_citation import SourceCitation
        cite = SourceCitation(index=2, title="Docs", url="https://example.com", relevance=0.85)
        html = cite._render_custom()
        assert "[2]" in html
        assert "Docs" in html
        assert "https://example.com" in html
        assert "Relevance: 85%" in html

    def test_no_url_no_relevance(self):
        from djust_components.components.source_citation import SourceCitation
        cite = SourceCitation(index=1, title="Just a title")
        html = cite._render_custom()
        assert "dj-citation__url" not in html
        assert "dj-citation__relevance" not in html


# ===========================================================================
# Model Selector — Template Tag
# ===========================================================================

class TestModelSelector:
    def test_basic_render(self):
        models = [
            {"value": "gpt-4", "label": "GPT-4", "description": "Most capable",
             "context_window": "128k", "tier": "premium"},
            {"value": "gpt-3.5", "label": "GPT-3.5", "tier": "standard"},
        ]
        html = render(
            '{% model_selector name="model" options=models value="gpt-4" %}',
            {"models": models},
        )
        assert "dj-model-sel" in html
        assert "GPT-4" in html
        assert "Most capable" in html
        assert "128k" in html
        assert "dj-model-sel__tier--premium" in html
        assert "Premium" in html

    def test_placeholder_when_no_selection(self):
        html = render(
            '{% model_selector name="model" options=models %}',
            {"models": []},
        )
        assert "dj-model-sel__placeholder" in html
        assert "Select a model..." in html

    def test_custom_placeholder(self):
        html = render(
            '{% model_selector name="model" options=models placeholder="Pick one" %}',
            {"models": []},
        )
        assert "Pick one" in html

    def test_disabled(self):
        html = render(
            '{% model_selector name="model" options=models disabled=True %}',
            {"models": []},
        )
        assert "dj-model-sel--disabled" in html
        assert "disabled" in html

    def test_label(self):
        html = render(
            '{% model_selector name="model" options=models label="Choose model" %}',
            {"models": []},
        )
        assert "Choose model" in html
        assert "dj-model-sel__label" in html

    def test_hidden_input(self):
        html = render(
            '{% model_selector name="model" options=models value="gpt-4" %}',
            {"models": [{"value": "gpt-4", "label": "GPT-4"}]},
        )
        assert 'name="model"' in html
        assert 'value="gpt-4"' in html

    def test_role_combobox(self):
        html = render(
            '{% model_selector name="model" options=models %}',
            {"models": []},
        )
        assert 'role="combobox"' in html
        assert 'role="listbox"' in html

    def test_custom_class(self):
        html = render(
            '{% model_selector name="m" options=models class="my-sel" %}',
            {"models": []},
        )
        assert "my-sel" in html

    def test_tier_badges(self):
        models = [
            {"value": "a", "label": "A", "tier": "free"},
            {"value": "b", "label": "B", "tier": "enterprise"},
        ]
        html = render(
            '{% model_selector name="m" options=models %}',
            {"models": models},
        )
        assert "dj-model-sel__tier--free" in html
        assert "Free" in html
        assert "dj-model-sel__tier--enterprise" in html
        assert "Enterprise" in html


# ===========================================================================
# Model Selector — Component Class
# ===========================================================================

class TestModelSelectorClass:
    def test_basic_render(self):
        from djust_components.components.model_selector import ModelSelector
        sel = ModelSelector(
            name="model",
            options=[
                {"value": "gpt-4", "label": "GPT-4", "description": "Best", "tier": "premium"},
            ],
            value="gpt-4",
        )
        html = sel._render_custom()
        assert "dj-model-sel" in html
        assert "GPT-4" in html
        assert "Best" in html
        assert "Premium" in html

    def test_empty_options(self):
        from djust_components.components.model_selector import ModelSelector
        sel = ModelSelector(name="model")
        html = sel._render_custom()
        assert "dj-model-sel__placeholder" in html


# ===========================================================================
# Token Counter — Template Tag
# ===========================================================================

class TestTokenCounter:
    def test_basic_render(self):
        html = render('{% token_counter current=tokens max=max_tokens %}',
                       {"tokens": 1500, "max_tokens": 4096})
        assert "dj-token" in html
        assert "dj-token--ok" in html
        assert "1,500 / 4,096" in html
        assert 'role="meter"' in html

    def test_warn_threshold(self):
        html = render('{% token_counter current=tokens max=max_tokens %}',
                       {"tokens": 2800, "max_tokens": 4096})
        assert "dj-token--warn" in html

    def test_danger_threshold(self):
        html = render('{% token_counter current=tokens max=max_tokens %}',
                       {"tokens": 3600, "max_tokens": 4096})
        assert "dj-token--danger" in html

    def test_zero_max(self):
        html = render('{% token_counter current=tokens max=max_tokens %}',
                       {"tokens": 100, "max_tokens": 0})
        assert "dj-token--ok" in html
        assert "width:0.0%" in html

    def test_aria_attributes(self):
        html = render('{% token_counter current=tokens max=max_tokens %}',
                       {"tokens": 500, "max_tokens": 2000})
        assert 'aria-valuenow="500"' in html
        assert 'aria-valuemax="2000"' in html
        assert 'aria-label="Token usage"' in html

    def test_custom_label(self):
        html = render('{% token_counter current=tokens max=max_tokens label="Tokens used" %}',
                       {"tokens": 100, "max_tokens": 1000})
        assert "Tokens used" in html

    def test_custom_class(self):
        html = render('{% token_counter current=tokens max=max_tokens class="my-counter" %}',
                       {"tokens": 100, "max_tokens": 1000})
        assert "my-counter" in html

    def test_bar_width(self):
        html = render('{% token_counter current=tokens max=max_tokens %}',
                       {"tokens": 500, "max_tokens": 1000})
        assert "width:50.0%" in html


# ===========================================================================
# Token Counter — Component Class
# ===========================================================================

class TestTokenCounterClass:
    def test_basic_render(self):
        from djust_components.components.token_counter import TokenCounter
        tc = TokenCounter(current=1500, max=4096)
        html = tc._render_custom()
        assert "dj-token" in html
        assert "dj-token--ok" in html
        assert "1,500 / 4,096" in html

    def test_percentage(self):
        from djust_components.components.token_counter import TokenCounter
        tc = TokenCounter(current=50, max=100)
        assert tc.percentage == 50.0

    def test_threshold_class(self):
        from djust_components.components.token_counter import TokenCounter
        assert TokenCounter(current=50, max=100).threshold_class == "dj-token--ok"
        assert TokenCounter(current=70, max=100).threshold_class == "dj-token--warn"
        assert TokenCounter(current=90, max=100).threshold_class == "dj-token--danger"

    def test_zero_max(self):
        from djust_components.components.token_counter import TokenCounter
        tc = TokenCounter(current=100, max=0)
        assert tc.percentage == 0

    def test_exceeds_max(self):
        from djust_components.components.token_counter import TokenCounter
        tc = TokenCounter(current=200, max=100)
        assert tc.percentage == 100


# ===========================================================================
# XSS Escaping
# ===========================================================================

class TestAITrustXSS:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Approval Gate XSS ---

    def test_approval_message_xss(self):
        html = render(
            '{% approval_gate message=bad risk="high" %}',
            {"bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_approval_approve_event_xss(self):
        html = render(
            '{% approval_gate message="test" approve_event=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_approval_reject_event_xss(self):
        html = render(
            '{% approval_gate message="test" reject_event=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_approval_approve_label_xss(self):
        html = render(
            '{% approval_gate message="test" approve_label=bad %}',
            {"bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_approval_reject_label_xss(self):
        html = render(
            '{% approval_gate message="test" reject_label=bad %}',
            {"bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_approval_class_xss(self):
        html = render(
            '{% approval_gate message="test" class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Source Citation XSS ---

    def test_citation_title_xss(self):
        html = render(
            '{% source_citation index="1" title=bad %}',
            {"bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_citation_url_xss(self):
        html = render(
            '{% source_citation index="1" title="T" url=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_citation_class_xss(self):
        html = render(
            '{% source_citation index="1" title="T" class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Model Selector XSS ---

    def test_model_sel_name_xss(self):
        html = render(
            '{% model_selector name=bad options=models %}',
            {"bad": self.XSS_ATTR, "models": []},
        )
        self._assert_attr_escaped(html)

    def test_model_sel_event_xss(self):
        models = [{"value": "a", "label": "A"}]
        html = render(
            '{% model_selector name="m" options=models event=bad %}',
            {"bad": self.XSS_ATTR, "models": models},
        )
        self._assert_attr_escaped(html)

    def test_model_sel_label_xss(self):
        html = render(
            '{% model_selector name="m" options=models label=bad %}',
            {"bad": self.XSS, "models": []},
        )
        self._assert_no_script(html)

    def test_model_sel_option_label_xss(self):
        models = [{"value": "a", "label": self.XSS}]
        html = render(
            '{% model_selector name="m" options=models %}',
            {"models": models},
        )
        self._assert_no_script(html)

    def test_model_sel_option_desc_xss(self):
        models = [{"value": "a", "label": "A", "description": self.XSS}]
        html = render(
            '{% model_selector name="m" options=models %}',
            {"models": models},
        )
        self._assert_no_script(html)

    def test_model_sel_class_xss(self):
        html = render(
            '{% model_selector name="m" options=models class=bad %}',
            {"bad": self.XSS_ATTR, "models": []},
        )
        self._assert_attr_escaped(html)

    # --- Token Counter XSS ---

    def test_token_label_xss(self):
        html = render(
            '{% token_counter current=tokens max=max_tokens label=bad %}',
            {"tokens": 10, "max_tokens": 100, "bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_token_class_xss(self):
        html = render(
            '{% token_counter current=tokens max=max_tokens class=bad %}',
            {"tokens": 10, "max_tokens": 100, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ===========================================================================
# Rust Handler Tests
# ===========================================================================

class TestRustHandlers:
    def test_approval_gate_handler(self):
        from djust_components.rust_handlers import ApprovalGateHandler
        h = ApprovalGateHandler()
        result = h.render(['message="Delete 47?"', 'risk="high"', 'approve_event="ok"'], {})
        s = str(result)
        assert "dj-approval--high" in s
        assert "Delete 47?" in s
        assert 'dj-click="ok"' in s

    def test_approval_gate_invalid_risk(self):
        from djust_components.rust_handlers import ApprovalGateHandler
        h = ApprovalGateHandler()
        result = h.render(['risk="bogus"'], {})
        assert "dj-approval--medium" in str(result)

    def test_source_citation_handler(self):
        from djust_components.rust_handlers import SourceCitationHandler
        h = SourceCitationHandler()
        result = h.render(['index="2"', 'title="Docs"', 'url="https://x.com"', 'relevance="0.9"'], {})
        s = str(result)
        assert "[2]" in s
        assert "Docs" in s
        assert "https://x.com" in s
        assert "Relevance: 90%" in s

    def test_model_selector_handler(self):
        from djust_components.rust_handlers import ModelSelectorHandler
        h = ModelSelectorHandler()
        models = [
            {"value": "gpt-4", "label": "GPT-4", "tier": "premium", "context_window": "128k"},
        ]
        result = h.render(['name="model"', 'options=models', 'value="gpt-4"'], {"models": models})
        s = str(result)
        assert "GPT-4" in s
        assert "Premium" in s
        assert "128k" in s

    def test_token_counter_handler(self):
        from djust_components.rust_handlers import TokenCounterHandler
        h = TokenCounterHandler()
        result = h.render(['current="1500"', 'max="4096"'], {})
        s = str(result)
        assert "dj-token--ok" in s
        assert "1,500 / 4,096" in s

    def test_token_counter_handler_danger(self):
        from djust_components.rust_handlers import TokenCounterHandler
        h = TokenCounterHandler()
        result = h.render(['current="3800"', 'max="4096"'], {})
        assert "dj-token--danger" in str(result)

    # --- Rust handler XSS ---

    def test_approval_handler_message_xss(self):
        from djust_components.rust_handlers import ApprovalGateHandler
        h = ApprovalGateHandler()
        result = h.render(['message=bad'], {"bad": "<script>alert(1)</script>"})
        s = str(result)
        assert "<script>" not in s
        assert "&lt;script&gt;" in s

    def test_approval_handler_event_xss(self):
        from djust_components.rust_handlers import ApprovalGateHandler
        h = ApprovalGateHandler()
        result = h.render(['approve_event=bad'], {"bad": '" onmouseover="alert(1)" x="'})
        s = str(result)
        assert '" onmouseover="' not in s
        assert "&quot;" in s

    def test_citation_handler_title_xss(self):
        from djust_components.rust_handlers import SourceCitationHandler
        h = SourceCitationHandler()
        result = h.render(['index="1"', 'title=bad'], {"bad": "<script>alert(1)</script>"})
        s = str(result)
        assert "<script>" not in s
        assert "&lt;script&gt;" in s

    def test_citation_handler_url_xss(self):
        from djust_components.rust_handlers import SourceCitationHandler
        h = SourceCitationHandler()
        result = h.render(['index="1"', 'title="T"', 'url=bad'], {"bad": '" onmouseover="alert(1)" x="'})
        s = str(result)
        assert '" onmouseover="' not in s
        assert "&quot;" in s

    def test_model_selector_handler_xss(self):
        from djust_components.rust_handlers import ModelSelectorHandler
        h = ModelSelectorHandler()
        models = [{"value": "a", "label": "<script>alert(1)</script>"}]
        result = h.render(['name="m"', 'options=models'], {"models": models})
        s = str(result)
        assert "<script>" not in s
        assert "&lt;script&gt;" in s

    def test_token_counter_handler_label_xss(self):
        from djust_components.rust_handlers import TokenCounterHandler
        h = TokenCounterHandler()
        result = h.render(['current="10"', 'max="100"', 'label=bad'], {"bad": "<script>alert(1)</script>"})
        s = str(result)
        assert "<script>" not in s
        assert "&lt;script&gt;" in s
