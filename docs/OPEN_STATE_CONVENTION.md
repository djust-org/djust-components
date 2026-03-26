# Open-State Convention

All toggleable components in djust-components use the **`data-open` HTML attribute** to signal open/closed state. This replaces the earlier mixed approach where some components used CSS classes (`.component-open`) and others used data attributes.

## The Rule

> A toggleable component is open when its root (or relevant wrapper) element has the `data-open` attribute present. It is closed when the attribute is absent.

```css
/* CSS targets the attribute presence, not a specific value */
.popover-wrapper[data-open] .popover { opacity: 1; visibility: visible; }
```

```js
// JS toggles the attribute
el.setAttribute('data-open', '');   // open
el.removeAttribute('data-open');    // close
```

## Why `data-open` over CSS Classes

1. **Semantic** -- `data-open` describes state; CSS classes describe styling. Mixing the two (`.popover-open`) conflates concerns.
2. **CSS attribute selectors** -- `[data-open]` is a single, grep-able pattern. No need to remember per-component class names.
3. **JavaScript consistency** -- `dataset.open` / `hasAttribute('data-open')` is the same API everywhere.
4. **Server rendering** -- Server-side open state is expressed as `data-open` or `data-open="true"`, which is a standard HTML boolean attribute pattern.

## Components Covered

| Component            | Wrapper Element Selector         | Notes |
|----------------------|----------------------------------|-------|
| Sheet / Drawer       | `.sheet-overlay`, `.sheet-*`     | `data-open="true"` |
| Command Palette      | `.palette-overlay`, `.palette`   | `data-open="true"` |
| Context Menu         | `.ctx-menu`                      | `dataset.open` set/deleted in JS |
| Split Button         | `.split-btn-menu`                | `data-open="true"/"false"` |
| Dropdown (#4)        | `.dj-dropdown`                   | Boolean `data-open` attribute |
| Dropdown Menu        | `.dj-dropdown-menu`              | Boolean `data-open` attribute |
| Popover              | `.popover-wrapper`               | Boolean `data-open` attribute |
| Popconfirm           | `.dj-popconfirm-wrapper`         | Boolean `data-open` attribute |
| Notification Popover | `.dj-notif-popover`              | Boolean `data-open` attribute |
| Dropdown (legacy)    | `.dropdown-menu`                 | `data-open="true"` |

## Adding a New Toggleable Component

1. **CSS**: Use `[data-open]` attribute selector on the wrapper:
   ```css
   .my-component[data-open] .my-component__panel { display: block; }
   ```
2. **Python (server-rendered open state)**: Emit `data-open` when the component should start open:
   ```python
   open_attr = ' data-open' if is_open else ""
   f'<div class="my-component"{open_attr}>...'
   ```
3. **JS (client-side toggle)**: Use `setAttribute`/`removeAttribute`:
   ```js
   if (el.hasAttribute('data-open')) {
       el.removeAttribute('data-open');
   } else {
       el.setAttribute('data-open', '');
   }
   ```

## Migration Notes (v2.1)

The following components were migrated from CSS class toggle to `data-open`:

- **Popover**: `.popover-open` class on `.popover-wrapper`
- **Popconfirm**: `.dj-popconfirm-open` class on `.dj-popconfirm-wrapper`
- **Notification Popover**: `.dj-notif-popover--open` class on `.dj-notif-popover`
- **Dropdown (#4)**: `.dj-dropdown--open` class on `.dj-dropdown`
- **Dropdown Menu**: `.dj-dropdown-menu--open` class on `.dj-dropdown-menu`

If you have custom CSS targeting the old class names, update your selectors to use `[data-open]` instead.
