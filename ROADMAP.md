# djust-components Roadmap

## Status: 57 / 57 components shipped ✅

---

## ✅ Shipped — All 57 Components

### v1.0 — Original 12
| # | Component | Tag |
|---|-----------|-----|
| 1 | Modal | `{% modal %}...{% endmodal %}` |
| 2 | Tabs | `{% tabs %}...{% endtabs %}` |
| 3 | Accordion | `{% accordion %}...{% endaccordion %}` |
| 4 | Dropdown | `{% dropdown %}...{% enddropdown %}` |
| 5 | Toast Container | `{% toast_container toasts=toasts %}` |
| 6 | Tooltip | `{% tooltip %}...{% endtooltip %}` |
| 7 | Progress Bar | `{% progress value=65 %}` |
| 8 | Badge | `{% badge count=3 %}` |
| 9 | Card | `{% card %}...{% endcard %}` |
| 10 | Data Table | `{% data_table rows=rows columns=cols %}` |
| 11 | Pagination | `{% pagination current=page total=total %}` |
| 12 | Avatar | `{% avatar initials="AB" %}` |

### v1.1 — Tier 1 (Foundational Forms & Feedback)
| # | Component | Tag |
|---|-----------|-----|
| 13 | Alert / Banner | `{% alert type="info" %}...{% endalert %}` |
| 14 | Button | `{% dj_button label="Save" variant="primary" %}` |
| 15 | Input Field | `{% dj_input name="email" input_type="email" %}` |
| 16 | Select | `{% dj_select name="role" options=opts %}` |
| 17 | Checkbox | `{% dj_checkbox name="agree" label="..." %}` |
| 18 | Radio | `{% dj_radio name="plan" value="pro" current_value=plan %}` |
| 19 | Textarea | `{% dj_textarea name="bio" rows=4 %}` |
| 20 | Form Group | `{% form_group label="Name" %}...{% endform_group %}` |
| 21 | Spinner | `{% spinner size="md" %}` |
| 22 | Skeleton | `{% skeleton skeleton_type="card" lines=3 %}` |
| 23 | Breadcrumb | `{% breadcrumb items=items %}` |
| 24 | Empty State | `{% empty_state title="No results" %}` |
| 25 | Divider | `{% dj_divider label="or" %}` |

### v1.2 — Tier 2 + Tier 3 Core
| # | Component | Tag |
|---|-----------|-----|
| 26 | Switch / Toggle | `{% switch name="notifs" checked=True %}` |
| 27 | Stat / KPI Card | `{% stat_card label="Revenue" value="$12k" trend="+8%" %}` |
| 28 | Tag / Chip | `{% dj_tag label="Python" dismissible=True %}` |
| 29 | Timeline | `{% timeline %}...{% endtimeline %}` |
| 30 | Stepper | `{% stepper steps=steps active=1 %}` |
| 31 | Combobox | `{% combobox name="country" options=opts event="search" %}` |
| 32 | Popover | `{% popover trigger="Info" %}...{% endpopover %}` |
| 33 | Tree View | `{% tree_view nodes=nodes expand_event="expand" %}` |
| 34 | Code Block | `{% code_block language="python" code=snippet %}` |
| 35 | Notification Center | `{% notification_center notifications=notifs %}` |
| 36 | Rating / Stars | `{% rating value=4 max=5 %}` |
| 37 | Copy Button | `{% copy_button text="npm install djust" %}` |
| 38 | Kbd / Shortcut | `{% kbd keys="⌘K" %}` |
| 39 | Collapsible | `{% collapsible %}...{% endcollapsible %}` |
| 40 | Color Picker | `{% color_picker name="accent" value="#3B82F6" %}` |
| 41 | Sheet / Drawer | `{% sheet %}...{% endsheet %}` |
| 42 | Context Menu | `{% context_menu %}...{% endcontext_menu %}` |
| 43 | Gauge / Donut | `{% gauge value=72 max=100 label="CPU" %}` |
| 44 | Image Carousel | `{% carousel images=imgs active=0 %}` |
| 45 | Command Palette | `{% command_palette results=cmds %}` |

### v1.3 — Tier 3 Complex / Interactive
| # | Component | Tag |
|---|-----------|-----|
| 46 | Date Picker | `{% date_picker year=dp_year month=dp_month selected=dp_selected %}` |
| 47 | File Dropzone | `{% file_dropzone name="doc" accept=".pdf" max_size_mb=10 %}` |
| 48 | Split Pane | `{% split_pane direction="horizontal" %}...{% pane %}...{% endsplit_pane %}` |
| 49 | Table of Contents | `{% table_of_contents items=toc_items active=toc_active %}` |
| 50 | Virtual List | `{% virtual_list items=items total=500 load_more_event="load_more" %}` |
| 51 | Rich Text Editor | `{% rich_text_editor name="content" event="update_content" %}` |
| 52 | Kanban Board | `{% kanban_board columns=cols move_event="kanban_move" %}` (inline `{% for %}` recommended) |

---

## Milestone Summary

| Milestone | Components | Status |
|-----------|-----------|--------|
| **v1.0** — Original 12 | 1–12 | ✅ Done |
| **v1.1** — Tier 1 complete | 13–25 | ✅ Done |
| **v1.2** — Tier 2 + Tier 3 most | 26–45 | ✅ Done |
| **v1.3** — Remaining interactive | 46–52 | ✅ Done |
| **v1.4** — Polish + new components | TBD | 🔲 Next |

---

## v1.4 Candidates

### Quality improvements to existing components
| Component | Gap |
|-----------|-----|
| Virtual List | Rust handler list-of-dicts resolution — currently requires inline `{% for %}` workaround |
| Kanban Board | Same Rust handler issue — inline `{% for %}` workaround in place |
| Data Table | No column sorting, no row selection |
| Combobox | No multi-select mode |
| Date Picker | No date range selection |
| Code Block | No syntax highlighting (highlight.js not wired) |

### New components not yet built
| Component | Description | Priority |
|-----------|-------------|----------|
| **Mentions / @input** | Text input that triggers user lookup on `@` | High |
| **Drawer / Bottom Sheet** | Mobile-optimised slide-up variant | High |
| **Phone Input** | Flag + dial code + number with validation | Medium |
| **OTP Input** | 4/6 digit one-time code input boxes | Medium |
| **Number Stepper** | +/− input for numeric values | Medium |
| **Multi-select** | Checkbox list with search + tag output | Medium |
| **Data Grid** | Editable cells, column resize, freeze | High (complex) |
| **Chat Bubble** | Message thread UI (pairs with djust WS) | Medium |
| **Presence Avatars** | Stacked avatars showing who's online | Medium |
