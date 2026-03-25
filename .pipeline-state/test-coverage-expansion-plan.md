# Test Coverage Expansion Plan

## Problem
Only 5 of 52 components have Python component class tests, and only the original 12 have template tag tests. 40+ Rust handler classes have zero direct handler-level test coverage.

## Current Coverage

### Already tested in test_rust_handlers.py (render + CSS):
- ModalHandler, PopoverHandler, CollapsibleHandler, SheetHandler, CommandPaletteHandler
- ContextMenuHandler, SplitPaneHandler, KbdHandler, CopyButtonHandler, RatingHandler
- CodeBlockHandler, PaletteItemHandler, ContextMenuItemHandler

### Template tag tests in test_components.py:
- Modal, Tabs, Accordion, Dropdown, Tooltip, Card, Progress, Badge, Avatar, Toast

### Template tag CSS tests in test_css_batch3/4:
- Combobox, ColorPicker, DatePicker, FileDropzone, NotificationCenter, TreeView
- Gauge, Carousel, VirtualList, KanbanBoard, TableOfContents, RichTextEditor, SplitPane

### Component class tests in test_component_classes.py:
- Badge, StatusDot, Button, Card, Markdown

## Plan: 4 Batches

### Batch 1: Untested Rust Handler Rendering (33 handlers)
Test file: `tests/test_rust_handler_coverage.py`

Block handlers to test:
- CardHandler, TabsHandler, AccordionHandler, AccordionItemHandler
- DropdownHandler, AlertHandler, FormGroupHandler
- TimelineHandler, TimelineItemHandler, TooltipHandler

Inline handlers to test:
- ToastContainerHandler, ProgressHandler, BadgeHandler, PaginationHandler
- AvatarHandler, SpinnerHandler, SkeletonHandler, BreadcrumbHandler
- EmptyStateHandler, DividerHandler, SwitchHandler, StatCardHandler
- TagChipHandler, StepperHandler, DjButtonHandler, DjInputHandler
- DjSelectHandler, DjTextareaHandler, DjCheckboxHandler, DjRadioHandler

Delegating handlers (call template tag functions):
- ComboboxHandler, GaugeHandler, NotificationCenterHandler, TreeViewHandler
- ColorPickerHandler, CarouselHandler, DatePickerHandler, FileDropzoneHandler
- VirtualListHandler, KanbanBoardHandler, TableOfContentsHandler, RichTextEditorHandler

### Batch 2: Form Component Interaction
Test dj-* attribute emission for form handlers:
- DjInputHandler: dj-input event
- DjSelectHandler: dj-change event
- DjTextareaHandler: dj-input event
- DjCheckboxHandler: dj-change event
- DjRadioHandler: dj-change event
- SwitchHandler: dj-change event
- ComboboxHandler: dj-* events via delegation

### Batch 3: Complex Component State
- DataTableHandler: basic render, empty state, sort indicators
- StepperHandler: active step, complete steps
- AccordionItemHandler: open/closed states, aria-expanded
- BreadcrumbHandler: active item, links

### Batch 4: Edge Cases
- Empty data for all handlers (missing params, None values)
- XSS payloads in user-supplied text for all handlers that accept text params
- Type coercion edge cases (string "0", empty string, None)

## Implementation
All tests go in a single new file: `tests/test_rust_handler_coverage.py`
Pattern: instantiate handler, call .render() with args, assert HTML output.
