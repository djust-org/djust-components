# Component Class Expansion Plan

## Pattern

Each component:
- Inherits from `djust.Component`
- Calls `super().__init__(**kwargs)` with all props
- Stores props as instance attributes
- Implements `_render_custom() -> str` returning HTML string
- Uses `html.escape()` on user-provided text values
- CSS classes follow `dj-{component}` / `dj-{component}-{variant}` convention
- Style-agnostic: uses CSS custom properties with sensible fallbacks

## 7 New Components

### 1. Alert (`alert.py`)
- Props: message, variant (info/success/warning/danger), dismissible, action (dismiss event), icon, custom_class
- Factory: `Alert.info()`, `Alert.success()`, `Alert.warning()`, `Alert.danger()`
- HTML: `<div class="dj-alert dj-alert-{variant}">` with optional dismiss button

### 2. StatCard (`stat_card.py`)
- Props: label, value, trend (up/down/flat), trend_value, icon, variant, custom_class
- HTML: `<div class="dj-stat-card">` with label/value/trend sections

### 3. Tag (`tag.py`)
- Props: label, variant (default/primary/success/info/warning/danger), size, dismissible, action (dismiss event), custom_class
- HTML: `<span class="dj-tag">` with optional dismiss button

### 4. Toast (`toast.py`)
- Props: message, type (info/success/warning/error), duration, dismissible, action, custom_class
- Factory: `Toast.success()`, `Toast.error()`, `Toast.warning()`, `Toast.info()`
- HTML: `<div class="dj-toast dj-toast-{type}">`

### 5. Progress (`progress.py`)
- Props: value, max, label, variant (default/success/info/warning/danger), size, show_value, custom_class
- HTML: `<div class="dj-progress">` with inner bar at percentage width

### 6. Spinner (`spinner.py`)
- Props: size (sm/md/lg), variant (default/primary/muted), label (sr-only text), custom_class
- HTML: `<span class="dj-spinner">` with optional screen-reader label

### 7. Switch (`switch.py`)
- Props: name, checked, label, disabled, action, custom_class
- Method: `toggle()` flips checked state
- HTML: `<label class="dj-switch">` with hidden checkbox and slider span

## Files to modify
- `src/djust_components/components/__init__.py` — add imports + __all__
- `src/djust_components/__init__.py` — no change needed (components are imported from subpackage)
- `tests/test_component_classes.py` — add test classes
- `CHANGELOG.md` — add entries under [Unreleased]
