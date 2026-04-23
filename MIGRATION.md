# Migrating from `djust-components` to `djust.components`

This repo is deprecated. All functionality is now in the `djust` core package.

## 1. Replace the install

```diff
- pip install djust-components
+ pip install djust
```

## 2. Update imports

Grep-replace the top-level package name:

```bash
# macOS:
grep -rl 'djust_components' . | xargs sed -i '' 's/djust_components/djust.components/g'
# Linux:
grep -rl 'djust_components' . | xargs sed -i     's/djust_components/djust.components/g'
```

## 3. Import mapping

| Before                                       | After                                  |
| -------------------------------------------- | -------------------------------------- |
| `from djust_components import X`             | `from djust.components import X`       |
| `import djust_components`                    | `from djust import components`         |
| `'djust_components'` in `INSTALLED_APPS`     | `'djust.components'`                   |
| `{% load djust_components %}` (templatetag)  | `{% load djust_components %}` (same)   |

All public names (descriptor components `Accordion`, `Tabs`, `Modal`, `Collapsible`, `Sheet`, `Dropdown`, `Tooltip`, `Carousel`; mixins `ComponentMixin`, `DataTableMixin`, `AccordionMixin`, `TabsMixin`, `ModalMixin`, `CollapsibleMixin`, `SheetMixin`, `DropdownMixin`, `TooltipMixin`, `CarouselMixin`, `ServerEventToastMixin`; helpers `render_icon`, `push_toast`, `confirm_action`, `register_preset`, `get_preset`; views `TtydTerminalView`) are re-exported from `djust.components` with the same signatures.

## 4. Remove the old dep

Once imports are migrated and tests pass, remove `djust-components` from your `pyproject.toml` / `requirements.txt`. The shim package depends on `djust>=0.5.6rc1` so djust is already installed.
