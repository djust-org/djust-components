# djust-components Roadmap

> Current status: **52 components shipped** (handlers), CSS coverage at ~60%, v1.4 next

52 user-facing component tags (backed by 56 Rust handler classes) shipped across 4 milestones. **132 more planned** through v2.0 (**184 total**). **SCOPE FROZEN** — no new components until Quick Wins Sprint ships.

**Reality check**: All 52 have Rust handlers, but ~22 components from v1.2-v1.3 lack CSS styles, and only the original 12 have Django template tags. v1.4 focuses on closing these gaps + Data Table Pro Phases 1-3 + new simple components. Data Table Pro Phases 4-5 deferred to v1.5 to keep v1.4 shippable (~4 weeks).

<!-- Review pass history archived — see git history for details. -->

---

### Priority Matrix — What Moves the Needle Most

| Priority | Feature | Milestone |
|----------|---------|-----------|
| ~~**P0**~~ | ~~Modal (#1)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Tabs (#2)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Accordion (#3)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Dropdown (#4)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Toast Container (#5)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Tooltip (#6)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Progress Bar (#7)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Badge (#8)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Card (#9)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Data Table (#10)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Pagination (#11)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Avatar (#12)~~ ✅ | v1.0 |
| ~~**P0**~~ | ~~Alert / Banner (#13)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Button (#14)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Input Field (#15)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Select (#16)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Checkbox (#17)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Radio (#18)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Textarea (#19)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Form Group (#20)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Spinner (#21)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Skeleton (#22)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Breadcrumb (#23)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Empty State (#24)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Divider (#25)~~ ✅ | v1.1 |
| ~~**P0**~~ | ~~Switch / Toggle (#26)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Stat / KPI Card (#27)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Tag / Chip (#28)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Timeline (#29)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Stepper (#30)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Combobox (#31)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Popover (#32)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Tree View (#33)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Code Block (#34)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Notification Center (#35)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Rating / Stars (#36)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Copy Button (#37)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Kbd / Shortcut (#38)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Collapsible (#39)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Color Picker (#40)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Sheet / Drawer (#41)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Context Menu (#42)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Gauge / Donut (#43)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Image Carousel (#44)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Command Palette (#45)~~ ✅ | v1.2 |
| ~~**P0**~~ | ~~Date Picker (#46)~~ ✅ | v1.3 |
| ~~**P0**~~ | ~~File Dropzone (#47)~~ ✅ | v1.3 |
| ~~**P0**~~ | ~~Split Pane (#48)~~ ✅ | v1.3 |
| ~~**P0**~~ | ~~Table of Contents (#49)~~ ✅ | v1.3 |
| ~~**P0**~~ | ~~Virtual List (#50)~~ ✅ | v1.3 |
| ~~**P0**~~ | ~~Rich Text Editor (#51)~~ ✅ | v1.3 |
| ~~**P0**~~ | ~~Kanban Board (#52)~~ ✅ | v1.3 |
| **P0** | CSS Completion — 22 Unstyled Components (#CSS) | v1.4 |
| **P0** | Data Table Pro Phase 1 — Core Interactivity (#DTP-P1) | v1.4 |
| **P0** | Data Table Pro Phase 2 — Editing & Layout (#DTP-P2) | v1.4 |
| **P0** | Data Table Pro Phase 3 — Advanced Features (#DTP-P3) | v1.4 |
| **P0** | Fix Existing Component Gaps (#GAPS) | v1.4 |
| **P0** | Component Gallery (#GALLERY) | v1.4 |
| **P1** | Test Coverage Expansion (#TEST) | v1.4 |
| **P1** | Component Class Expansion (#CLASSES) | v1.4 |
| **P1** | Multi-select (#53) | v1.4 |
| **P1** | Data Grid (#54) | v1.4 |
| **P1** | OTP Input (#58) | v1.4 |
| **P1** | Number Stepper (#59) | v1.4 |
| **P1** | Toggle Group (#61) | v1.4 |
| **P1** | Scroll Area (#62) | v1.4 |
| **P1** | Tag Input (#63) | v1.4 |
| **P1** | Input Group (#64) | v1.4 |
| **P1** | Floating Action Button (#65) | v1.4 |
| **P1** | Label (#66) | v1.4 |
| **P1** | Callout / Blockquote (#67) | v1.4 |
| **P1** | Rich Select (#103) | v1.4 |
| **P1** | Loading Overlay (#104) | v1.4 |
| **P1** | Notification Badge (#105) | v1.4 |
| **P1** | Announcement Bar (#106) | v1.4 |
| **P1** | Segmented Progress (#107) | v1.4 |
| **P1** | Aspect Ratio (#116) | v1.4 |
| **P1** | Progress Circle (#124) | v1.4 |
| **P1** | Scroll to Top (#125) | v1.4 |
| **P1** | Status Indicator (#128) | v1.4 |
| **P1** | Streaming Text (#129) | v1.4 |
| **P1** | Split Button (#133) | v1.4 |
| **P1** | Description List (#134) | v1.4 |
| **P1** | Theme Toggle (#138) | v1.4 |
| **P1** | Code Snippet (#139) | v1.4 |
| **P1** | Responsive Image (#140) | v1.4 |
| **P1** | Relative Time (#146) | v1.4 |
| **P1** | Fieldset (#147) | v1.4 |
| **P1** | Copyable Text (#153) | v1.4 |
| **P1** | Sticky Header (#171) | v1.4 |
| **P1** | Connection Status Bar (#175) | v1.4 |
| **P1** | Live Counter (#176) | v1.4 |
| **P1** | Server Event Toast (#177) | v1.4 |
| **P1** | Icon System (#178) | v1.4 |
| **P1** | Page Header (#179) | v1.4 |
| **P2** | Quality & DX Improvements (#DX14) | v1.4 |
| **P0** | Django Form Renderer (#73) | v1.5 |
| **P0** | Django ModelForm Table (#74) | v1.5 |
| **P0** | Confirmation Dialog (#75) | v1.5 |
| **P0** | Popconfirm (#180) | v1.5 |
| **P0** | Slider / Range (#82) | v1.5 |
| **P0** | Search Input (#83) | v1.5 |
| **P0** | Password Input (#84) | v1.5 |
| **P0** | Autocomplete (#85) | v1.5 |
| **P0** | Data Table Pro Phase 4 — Data Presentation (#DTP-P4) | v1.5 |
| **P0** | Data Table Pro Phase 5 — Data Import & Computed (#DTP-P5) | v1.5 |
| **P1** | Sidebar Nav (#86) | v1.5 |
| **P1** | Toolbar (#87) | v1.5 |
| **P1** | Inline Edit (#88) | v1.5 |
| **P1** | Avatar Group (#89) | v1.5 |
| **P1** | Navigation Menu (#90) | v1.5 |
| **P1** | Hover Card (#91) | v1.5 |
| **P1** | Transfer List (#98) | v1.5 |
| **P1** | Dependent Select (#108) | v1.5 |
| **P1** | Currency Input (#109) | v1.5 |
| **P1** | Form Validation Display (#110) | v1.5 |
| **P1** | Wizard / Multi-step Form (#111) | v1.5 |
| **P1** | Bottom Sheet (#112) | v1.5 |
| **P1** | Infinite Scroll (#113) | v1.5 |
| **P1** | Time Picker (#117) | v1.5 |
| **P1** | Expandable Text (#118) | v1.5 |
| **P1** | Countdown / Timer (#126) | v1.5 |
| **P1** | Cookie Consent Banner (#127) | v1.5 |
| **P1** | Conversation Thread (#130) | v1.5 |
| **P1** | Model Selector (#131) | v1.5 |
| **P1** | Token Counter (#132) | v1.5 |
| **P1** | Page Alert / Banner (#142) | v1.5 |
| **P1** | Dropdown Menu (#143) | v1.5 |
| **P1** | Skeleton Factory (#144) | v1.5 |
| **P1** | Meter / Stacked Progress (#148) | v1.5 |
| **P1** | Feedback Widget (#149) | v1.5 |
| **P1** | Truncated List (#150) | v1.5 |
| **P1** | Content Loader / Suspense Boundary (#152) | v1.5 |
| **P1** | Approval Gate (#155) | v1.5 |
| **P1** | Source Citation (#156) | v1.5 |
| **P1** | Multimodal Input (#159) | v1.5 |
| **P1** | AI Thinking Indicator (#160) | v1.5 |
| **P1** | Export Dialog (#161) | v1.5 |
| **P1** | Import Wizard (#162) | v1.5 |
| **P1** | Audit Log Table (#163) | v1.5 |
| **P1** | Filter Bar (#166) | v1.5 |
| **P1** | App Shell (#167) | v1.5 |
| **P1** | Notification Popover (#168) | v1.5 |
| **P1** | Inline Markdown Preview (#169) | v1.5 |
| **P1** | Form Array (#170) | v1.5 |
| **P1** | Scroll Spy (#172) | v1.5 |
| **P1** | Chat Bubble (#55) | v1.5 |
| **P1** | Presence Avatars (#56) | v1.5 |
| **P1** | Mentions / @input (#57) | v1.5 |
| **P2** | Error Boundary (#174) | v1.5 |
| **P2** | Composition Guide (#COMP-GUIDE) | v1.5 |
| **P2** | Server-side Helpers Module (#HELPERS) | v1.5 |
| **P2** | Component Presets (#PRESETS) | v1.5 |
| **P1** | Sortable List (#67b) | v2.0 |
| **P1** | Calendar View (#68) | v2.0 |
| **P1** | Gantt Chart (#69) | v2.0 |
| **P1** | Image Cropper (#70) | v2.0 |
| **P1** | Signature Pad (#71) | v2.0 |
| **P1** | Diff Viewer (#72) | v2.0 |
| **P1** | Pivot Table (#119) | v2.0 |
| **P1** | Org Chart (#120) | v2.0 |
| **P1** | Sortable Grid (#173) | v2.0 |
| **P2** | Terminal (#73b) | v2.0 |
| **P2** | Markdown Editor (#74b) | v2.0 |
| **P2** | Chart / Sparkline (#75b) | v2.0 |
| **P2** | Map Picker (#76b) | v2.0 |
| **P2** | Tour / Onboarding Guide (#121) | v2.0 |
| **P2** | JSON Viewer (#122) | v2.0 |
| **P2** | Log Viewer (#123) | v2.0 |
| **P2** | Prompt Template Editor (#158) | v2.0 |
| **P2** | Voice Input Button (#164) | v2.0 |
| **P2** | File Tree (#165) | v2.0 |
| **P2** | Dashboard Grid (#93) | v2.0 |
| **P2** | Bar Chart (#94) | v2.0 |
| **P2** | Line Chart (#95) | v2.0 |
| **P2** | Pie / Donut Chart (#96) | v2.0 |
| **P2** | Heatmap (#97) | v2.0 |
| **P2** | Treemap (#100) | v2.0 |
| **P2** | Comparison Table (#101) | v2.0 |
| **P2** | Masonry Grid (#102) | v2.0 |
| **P2** | Cron Expression Input (#145) | v2.0 |
| **P2** | Calendar Heatmap (#135) | v2.0 |
| **P2** | Error Page (#136) | v2.0 |
| **P2** | Image Upload Preview (#137) | v2.0 |
| **P2** | Number Animation (#141) | v2.0 |
| **P2** | Ribbon Badge (#151) | v2.0 |
| **P2** | Resizable Panel (#114) | v2.0 |
| **P2** | Breadcrumb Dropdown (#115) | v2.0 |
| **P2** | Image Lightbox (#99) | v2.0 |
| **P2** | Data Card Grid (#92) | v2.0 |
| **P2** | Agent Step Card (#154) | v2.0 |
| **P2** | QR Code (#157) | v2.0 |
| **P3** | Cursors Overlay (#77) | v2.0 |
| **P3** | Live Indicators (#78) | v2.0 |
| **P3** | Collaborative Selection (#79) | v2.0 |
| **P3** | Activity Feed (#80) | v2.0 |
| **P3** | Voting / Reactions (#81) | v2.0 |
| **P0** | CSS Class Name Standardization (#CSS-CLASS-NAMES) | v2.2 |
| **P0** | Gallery CSS Reset Fix (#GALLERY-RESET) | v2.2 |
| **P0** | Gallery Examples for All Tags (#GALLERY-EXAMPLES) | v2.1 |
| **P0** | Shared Test Infrastructure (#TEST-INFRA) | v2.1 |
| **P1** | Code Quality — Split Monolithic Files (#CODE-SPLIT) | v2.1 |
| **P1** | ARIA Audit & Keyboard Navigation (#ARIA-AUDIT) | v2.1 |
| **P1** | JS Test Infrastructure (#JS-TESTS) | v2.1 |
| **P1** | Extract Shared Utilities (#SHARED-UTILS) | v2.1 |
| ~~**P2**~~ | ~~CSS Linting Rules (#CSS-LINT)~~ ✅ PR #61 | v2.1 |
| ~~**P2**~~ | ~~Visual Regression Tests (#VRT)~~ ✅ PR #62 | v2.1 |
| **P2** | Security Hardening Sweep (#SEC-SWEEP) | v2.1 |
| ~~**P2**~~ | ~~Python Builtin Shadowing Cleanup (#BUILTIN-SHADOW)~~ ✅ PR #61 | v2.1 |
| **P2** | Replace eval() in Computed Columns (#EVAL-REPLACE) | v2.1 |
| ~~**P3**~~ | ~~Component Open-State Standardization (#OPEN-STATE)~~ ✅ PR #63 | v2.1 |
| ~~**P3**~~ | ~~Real Django Integration Tests (#DJANGO-REAL-TESTS)~~ ✅ PR #63 | v2.1 |

---

## Completed

### v1.0 — Original 12
| # | Component | Tag | Template Tag | CSS |
|---|-----------|-----|:---:|:---:|
| 1 | Modal | `{% modal %}...{% endmodal %}` | ✅ | ✅ |
| 2 | Tabs | `{% tabs %}...{% endtabs %}` | ✅ | ✅ |
| 3 | Accordion | `{% accordion %}...{% endaccordion %}` | ✅ | ✅ |
| 4 | Dropdown | `{% dropdown %}...{% enddropdown %}` | ✅ | ✅ |
| 5 | Toast Container | `{% toast_container toasts=toasts %}` | ✅ | ✅ |
| 6 | Tooltip | `{% tooltip %}...{% endtooltip %}` | ✅ | ✅ |
| 7 | Progress Bar | `{% progress value=65 %}` | ✅ | ✅ |
| 8 | Badge | `{% badge count=3 %}` | ✅ | ✅ |
| 9 | Card | `{% card %}...{% endcard %}` | ✅ | ✅ |
| 10 | Data Table | `{% data_table rows=rows columns=cols %}` | ✅ | ✅ |
| 11 | Pagination | `{% pagination current=page total=total %}` | ✅ | ✅ |
| 12 | Avatar | `{% avatar initials="AB" %}` | ✅ | ✅ |

### v1.1 — Tier 1 (Foundational Forms & Feedback)
| # | Component | Tag | CSS |
|---|-----------|-----|:---:|
| 13 | Alert / Banner | `{% alert type="info" %}...{% endalert %}` | ✅ |
| 14 | Button | `{% dj_button label="Save" variant="primary" %}` | ✅ |
| 15 | Input Field | `{% dj_input name="email" input_type="email" %}` | ✅ |
| 16 | Select | `{% dj_select name="role" options=opts %}` | ✅ |
| 17 | Checkbox | `{% dj_checkbox name="agree" label="..." %}` | ✅ |
| 18 | Radio | `{% dj_radio name="plan" value="pro" current_value=plan %}` | ✅ |
| 19 | Textarea | `{% dj_textarea name="bio" rows=4 %}` | ✅ |
| 20 | Form Group | `{% form_group label="Name" %}...{% endform_group %}` | ✅ |
| 21 | Spinner | `{% spinner size="md" %}` | ✅ |
| 22 | Skeleton | `{% skeleton skeleton_type="card" lines=3 %}` | ✅ |
| 23 | Breadcrumb | `{% breadcrumb items=items %}` | ✅ |
| 24 | Empty State | `{% empty_state title="No results" %}` | ✅ |
| 25 | Divider | `{% dj_divider label="or" %}` | ✅ |

### v1.2 — Tier 2 + Tier 3 Core
| # | Component | Tag | CSS |
|---|-----------|-----|:---:|
| 26 | Switch / Toggle | `{% switch name="notifs" checked=True %}` | ✅ |
| 27 | Stat / KPI Card | `{% stat_card label="Revenue" value="$12k" trend="+8%" %}` | ✅ |
| 28 | Tag / Chip | `{% dj_tag label="Python" dismissible=True %}` | ✅ |
| 29 | Timeline | `{% timeline %}...{% endtimeline %}` | ✅ |
| 30 | Stepper | `{% stepper steps=steps active=1 %}` | ✅ |
| 31 | Combobox | `{% combobox name="country" options=opts event="search" %}` | ❌ |
| 32 | Popover | `{% popover trigger="Info" %}...{% endpopover %}` | ❌ |
| 33 | Tree View | `{% tree_view nodes=nodes expand_event="expand" %}` | ❌ |
| 34 | Code Block | `{% code_block language="python" code=snippet %}` | ❌ |
| 35 | Notification Center | `{% notification_center notifications=notifs %}` | ❌ |
| 36 | Rating / Stars | `{% rating value=4 max=5 %}` | ❌ |
| 37 | Copy Button | `{% copy_button text="npm install djust" %}` | ❌ |
| 38 | Kbd / Shortcut | `{% kbd keys="⌘K" %}` | ❌ |
| 39 | Collapsible | `{% collapsible %}...{% endcollapsible %}` | ❌ |
| 40 | Color Picker | `{% color_picker name="accent" value="#3B82F6" %}` | ❌ |
| 41 | Sheet / Drawer | `{% sheet %}...{% endsheet %}` | ❌ |
| 42 | Context Menu | `{% context_menu %}...{% endcontext_menu %}` | ❌ |
| 43 | Gauge / Donut | `{% gauge value=72 max=100 label="CPU" %}` | ❌ |
| 44 | Image Carousel | `{% carousel images=imgs active=0 %}` | ❌ |
| 45 | Command Palette | `{% command_palette results=cmds %}` | ❌ |

### v1.3 — Tier 3 Complex / Interactive
| # | Component | Tag | CSS |
|---|-----------|-----|:---:|
| 46 | Date Picker | `{% date_picker year=dp_year month=dp_month selected=dp_selected %}` | ❌ |
| 47 | File Dropzone | `{% file_dropzone name="doc" accept=".pdf" max_size_mb=10 %}` | ❌ |
| 48 | Split Pane | `{% split_pane direction="horizontal" %}...{% pane %}...{% endsplit_pane %}` | ❌ |
| 49 | Table of Contents | `{% table_of_contents items=toc_items active=toc_active %}` | ❌ |
| 50 | Virtual List | `{% virtual_list items=items total=500 load_more_event="load_more" %}` | ❌ |
| 51 | Rich Text Editor | `{% rich_text_editor name="content" event="update_content" %}` | ❌ |
| 52 | Kanban Board | `{% kanban_board columns=cols move_event="kanban_move" %}` (inline `{% for %}` recommended) | ❌ |

### Milestone Summary
| Milestone | Components | Handlers | CSS | Status |
|-----------|-----------|----------|-----|--------|
| **v1.0** — Original 12 | 1–12 | ✅ 12/12 | ✅ 12/12 | ✅ Done |
| **v1.1** — Tier 1 complete | 13–25 | ✅ 13/13 | ✅ 13/13 | ✅ Done |
| **v1.2** — Tier 2 + Tier 3 most | 26–45 | ✅ 20/20 | ⚠️ 5/20 | Handlers done, CSS needed |
| **v1.3** — Remaining interactive | 46–52 | ✅ 7/7 | ❌ 0/7 | Handlers done, CSS needed |
| **v1.4** — CSS completion + Data Table Pro (P1-3) + new components | 53–54, 58–67, 103–107, 116, 124–125, 128–129, 133–134, 138–140, 146–147, 153, 171, 175–179 | — | — | Next |
| **v1.5** — Data Table Pro (P4-5) + Django integration + forms + nav + AI | 55–57, 73–75, 82–85, 86–92, 98, 108–113, 117–118, 126–127, 130–132, 141–145, 148–150, 152, 155–156, 159–163, 166–170, 172, 174, 180 | — | — | After v1.4 |
| **v2.0** — Advanced interactive + data viz + collaboration + deferred v1.5 | 68–72, 77–81, 93–97, 99–102, 114–115, 119–123, 135–137, 151, 154, 157–158, 164–165, 173 | — | — | Planned |

---

### Milestone: v1.4 — CSS Completion + Data Table Pro + Polish

**Goal**: Make all 52 shipped components fully styled, upgrade Data Table to a feature-rich component, add high-value simple components, and close DX gaps.

**CSS Completion — 22 Unstyled Components** (#CSS) — 22 components render HTML from Rust handlers but have zero CSS in `components.css`. Users installing the library see unstyled markup for nearly half the components. This must be fixed before any new features.

| Batch | Components needing CSS | Complexity |
|-------|----------------------|-----------|
| **Batch 1** (simple inline) | Kbd, Copy Button, Rating, Code Block, Collapsible | Low — mostly typography/spacing |
| **Batch 2** (layout/overlay) | Popover, Sheet/Drawer, Context Menu, Command Palette | Medium — positioning, z-index, transitions |
| **Batch 3** (form controls) | Combobox, Color Picker, Date Picker, File Dropzone | Medium — input styling, dropdowns, drag states |
| **Batch 4** (data/complex) | Notification Center, Tree View, Gauge/Donut, Carousel, Virtual List, Kanban Board, Table of Contents, Split Pane, Rich Text Editor | High — custom layouts, SVG, scrolling, resize handles |

Approach: Follow the existing design system (CSS custom properties from djust-theming, `hsl(var(--token))` pattern, BEM-ish class naming). Each batch should include both light and dark mode styles. Use CSS `@layer components` for all new styles to avoid specificity conflicts with user CSS.

**Data Table Pro Phase 1 — Core Interactivity** (#DTP-P1) — Transform `{% data_table %}` into a feature-rich component rivaling AG Grid / TanStack Table.

| Feature | Description | djust Integration |
|---------|-------------|-------------------|
| **Column sorting** | Click header to sort asc/desc/none cycle | `dj-click` on `<th>` → `sort_event` with column key |
| **Row selection** | Checkbox column, select-all, shift-click range | `dj-click` → `select_event` with row IDs |
| **Column filtering** | Per-column text/select/date range filters | `dj-input` in header → `filter_event` with debounce |
| **Global search** | Single search box filtering all visible columns | `dj-input` with debounce → `search_event` |
| **Empty/loading states** | Skeleton rows while loading, empty state | Reuse existing `{% skeleton %}` and `{% empty_state %}` |
| **Pagination integration** | Built-in or composable with `{% pagination %}` | Optional `paginate=True` param |
| **Accessibility (ARIA)** | `role="grid"`, `aria-sort`, `aria-selected`, live region announcements | All ARIA attributes emitted by Rust handler. Keyboard: Enter to sort, Space to toggle selection. |

**Data Table Pro Phase 2 — Editing & Layout** (#DTP-P2) — Inline editing, column resize/reorder, frozen columns, visibility toggle, density toggle, responsive card collapse, editable row mode.

| Feature | Description | djust Integration |
|---------|-------------|-------------------|
| **Inline editing** | Click cell to edit, Enter/Escape to save/cancel | `dj-click` to activate, `dj-input` with `dj-keyup` |
| **Column resize** | Drag column borders to resize | Client-side JS (no server round-trip) |
| **Column reorder** | Drag headers to reorder | Client-side JS with `dj-click` to persist |
| **Frozen columns** | Pin left/right columns that don't scroll | CSS `position: sticky` with z-index layering |
| **Column visibility** | Dropdown toggle to show/hide columns | Client-side JS + `dj-click` to persist preference |
| **Density toggle** | Switch between compact/comfortable/spacious row height | Client-side CSS class toggle. Persist via `dj-click` event. |
| **Responsive card collapse** | On mobile, each row renders as a stacked card with "Label: Value" pairs | CSS `@container` query + Card component CSS reuse. |
| **Editable row mode** | Click "Edit" → all cells become form inputs. Save/Cancel buttons. | `editable_rows=True` param. Fires `edit_event` with full row data dict on save. |

**Data Table Pro Phase 3 — Advanced Features** (#DTP-P3) — Row expansion, bulk actions, export, row grouping, custom cell renderers, keyboard navigation, virtual scrolling, server-side mode, faceted filtering, state persistence, column pinning, print mode, column statistics.

| Feature | Description | djust Integration |
|---------|-------------|-------------------|
| **Row expansion** | Expandable detail rows | `dj-click` toggle → nested content slot |
| **Bulk actions** | Toolbar appears when rows selected | Conditional toolbar with action buttons |
| **Export** | CSV/JSON download of current view | `dj-click` → server generates file |
| **Row grouping** | Group rows by column value with collapse/expand + subtotals | Server-side grouping, `dj-click` to toggle groups |
| **Custom cell renderers** | Render badges, progress bars, avatars inside cells | `cell_template` param mapping column keys to component templates |
| **Keyboard navigation** | Arrow keys between cells, Enter to edit, Escape to cancel | Client-side JS, `dj-keydown` for server-side actions |
| **Virtual scrolling** | Render only visible rows for 10k+ datasets | Client-side JS, `dj-scroll` to load |
| **Server-side mode** | Explicit pattern for server-driven sort/filter/page | `server_mode=True` — all interactions fire events |
| **Faceted filtering** | Filter values with counts | `facets=True` or `facets=facet_data` |
| **State persistence** | Save/restore sort, filter, column visibility, column order, page size | `persist_key="user_table"` → fires `table_state_changed` event |
| **Column pinning** | Pin columns to left/right edge | CSS `position: sticky` per-column |
| **Print-friendly mode** | Expand all rows, remove interactive chrome | `@media print` CSS rules |
| **Column statistics** | Quick stats popover per column | `stats=True` in column config |

`DataTableMixin` design:

```python
class MyView(DataTableMixin, LiveView):
    table_model = Product  # auto-infers columns from model fields
    table_columns = [...]  # or explicit column config
    table_page_size = 25
    table_default_sort = "-created_at"
    table_searchable_fields = ["name", "description"]
    table_filterable_fields = {"status": "select", "price": "range"}
```

The mixin auto-generates `table_sort`, `table_filter`, `table_search`, `table_paginate` event handlers and populates `table_rows`, `table_columns`, `table_page`, `table_total_pages` in the template context.

~~**Fix Unregistered Rust Handlers** (#QW1)~~ ✅ — All 7 v1.3 handlers are registered via `.extend()` calls at `rust_handlers.py:1358-1387`. Verified pass 12.

**Fix Existing Component Gaps** (#GAPS) — Resolve known issues in shipped components:

| Component | Gap | Fix |
|-----------|-----|-----|
| **Virtual List** | Rust handler list-of-dicts resolution — requires inline `{% for %}` workaround | Resolve list-of-dicts in handler before template rendering |
| **Kanban Board** | Same Rust handler issue — inline `{% for %}` workaround | Same fix as Virtual List |
| **Combobox** | No multi-select mode | Add `multiple=True` param, render tags for selections |
| **Date Picker** | No date range selection | Add `range=True` param with start/end state |
| **Code Block** | No syntax highlighting | Wire highlight.js or Prism.js with lazy loading |

**Component Gallery** (#GALLERY) — A single Django view/page that renders every component with example data. Essential during CSS Batch 1-4 work. Should auto-discover all registered handlers, show light/dark mode side-by-side, show each size/variant, include a responsive preview panel, and ship as a management command (`python manage.py component_gallery`).

**Test Coverage Expansion** (#TEST) — Tests only cover the original 12 template tags + 5 component classes. 40 Rust-handler-only components have zero test coverage.

| Test batch | Components | Priority |
|-----------|-----------|----------|
| **Rust handler rendering** | All 40 untested handlers — verify HTML output, CSS classes, attribute handling | High |
| **Form component interaction** | Combobox, Color Picker, Date Picker, File Dropzone — verify `dj-*` attributes emit correct events | High |
| **Complex component state** | Kanban, Virtual List, Tree View, Split Pane — verify nested content, dynamic state | Medium |
| **Edge cases** | Empty data, missing params, XSS payloads in user-supplied text | Medium |

**Component Class Expansion** (#CLASSES) — Only 5 of 52 components have Python component classes. Add classes for commonly manipulated components:

| # | Class | Why |
|---|-------|-----|
| 1 | **Alert** | Dynamically show/dismiss alerts in event handlers |
| 2 | **StatCard** | Update KPI values reactively (dashboards) |
| 3 | **Tag/Chip** | Build tag lists programmatically (filters, categories) |
| 4 | **Toast** | `Toast.success("Saved!")` — cleaner than dict construction |
| 5 | **Progress** | Update progress bars from background task handlers |
| 6 | **Spinner** | Conditional loading states in event handlers |
| 7 | **Switch** | Toggle state management with `.toggle()` method |

**Multi-select** (#53) — `{% multi_select name="tags" options=opts %}`. Checkbox list with search + tag output. Needed everywhere: user roles, categories, filters.

**Data Grid** (#54) — `{% data_grid columns=cols rows=rows %}`. Editable cells, column resize, freeze — spreadsheet-like. Distinct from Data Table: grid is for editing, table is for display.

**OTP Input** (#58) — `{% otp_input name="code" digits=6 %}`. 4/6 digit one-time code input boxes. Auth flows are extremely common.

**Number Stepper** (#59) — `{% number_stepper name="qty" min=1 max=99 %}`. +/- input for numeric values. E-commerce, settings, any quantity picker.

**Toggle Group** (#61) — `{% toggle_group name="view" options=opts value=current %}`. Exclusive button group (like radio styled as segmented buttons). Single/multi mode. Every toolbar, filter bar, and view switcher needs this.

**Scroll Area** (#62) — `{% scroll_area max_height="400px" %}...{% endscroll_area %}`. Custom-styled scrollbar container. Cross-browser consistent thin scrollbars with hover reveal. Needed by Tree View, Virtual List, Command Palette, Notification Center, and any constrained-height panel.

**Tag Input** (#63) — `{% tag_input name="tags" suggestions=tags event="add_tag" %}`. Input that creates dismissible tags as you type, with optional autocomplete suggestions. Distinct from Multi-select (dropdown-based) — Tag Input is free-text with optional suggestions.

**Input Group** (#64) — `{% input_group %}{% input_addon icon="search" %}{% dj_input name="q" %}{% input_addon text=".com" %}{% endinput_group %}`. Input with prefix/suffix addons — icons, text, buttons, or dropdowns.

**Floating Action Button** (#65) — `{% fab icon="plus" event="create" position="bottom-right" %}`. Mobile-style FAB with optional speed-dial sub-actions on hover/click. Fixed positioning.

**Label** (#66) — `{% dj_label for="email" required=True %}Email{% enddj_label %}`. Accessible form label with `for` attribute binding, required indicator, optional help text tooltip.

**Callout / Blockquote** (#67) — `{% callout type="info" title="Note" %}...{% endcallout %}`. Styled content block with icon, colored left border. Types: info, warning, danger, success, tip. Distinct from Alert (dismissible, transient) — Callout is static content emphasis.

**Rich Select** (#103) — `{% rich_select name="assignee" options=opts %}`. Select dropdown where each option can include icons, images, descriptions, or badges alongside the label.

**Loading Overlay** (#104) — `{% loading_overlay active=is_loading %}...{% endloading_overlay %}`. Semi-transparent overlay with centered spinner that blocks interaction on its container.

**Notification Badge** (#105) — `{% notification_badge count=5 %}`. Small count badge overlaid on icons/buttons. Supports dot-only mode, max count (99+), and pulse animation.

**Announcement Bar** (#106) — `{% announcement_bar type="info" dismissible=True %}...{% endannouncement_bar %}`. Full-width sticky top bar for site-wide announcements. Dismissible with `dj-click`.

**Segmented Progress** (#107) — `{% segmented_progress steps=steps current=2 %}`. Multi-step progress bar with labeled segments. Shows completed/active/upcoming states. Distinct from Stepper (vertical/navigable) and Progress (single bar).

**Aspect Ratio** (#116) — `{% aspect_ratio ratio="16/9" %}...{% endaspect_ratio %}`. CSS-only container that enforces a fixed aspect ratio. Uses `aspect-ratio` CSS property with fallback.

**Progress Circle** (#124) — `{% progress_circle value=65 size="md" %}`. Circular/ring progress indicator using SVG `stroke-dasharray`. Sizes: sm (32px), md (48px), lg (64px).

**Scroll to Top** (#125) — `{% scroll_to_top threshold="300px" %}`. Floating button that appears after scrolling past threshold. Smooth scrolls to page top. Pure client-side.

**Status Indicator** (#128) — `{% status_indicator status="online" label="API" %}`. Colored dot with optional label and pulse animation. Status maps: online=green, degraded=yellow, offline=red, maintenance=blue.

**Streaming Text** (#129) — `{% streaming_text stream_event="stream_chunk" %}`. Renders text that arrives incrementally via WebSocket with optional typing cursor animation. Auto-scrolls container. Supports markdown rendering as chunks arrive. djust's WebSocket architecture makes this trivial.

**Split Button** (#133) — `{% split_button label="Save" event="save" options=secondary_actions %}`. Primary action button with dropdown arrow for secondary actions.

**Description List** (#134) — `{% description_list items=items layout="horizontal" %}`. Structured key-value display (`<dl>/<dt>/<dd>`) with horizontal or vertical layout, optional dividers, and responsive stacking.

**Theme Toggle** (#138) — `{% theme_toggle current="system" event="set_theme" %}`. Light/dark/system mode switcher with sun/moon/monitor icons. Reads `prefers-color-scheme`, stores preference in `localStorage`, applies `data-theme` to `<html>`.

**Code Snippet** (#139) — `{% code_snippet language="bash" code="pip install djust" %}`. Code Block + Copy Button composed together with styled container, language badge, and one-click copy.

**Responsive Image** (#140) — `{% responsive_image src=url alt="..." aspect_ratio="16/9" lazy=True %}`. `<picture>` element with `srcset`, native `loading="lazy"`, optional blur-up placeholder, and `aspect-ratio` to prevent CLS.

**Relative Time** (#146) — `{% relative_time datetime=created_at auto_update=True %}`. Displays "3 hours ago", "just now", "in 2 days" using `Intl.RelativeTimeFormat`. Auto-updates every minute via client-side interval.

**Fieldset** (#147) — `{% fieldset legend="Account Details" %}...{% endfieldset %}`. Styled `<fieldset>` with `<legend>`, optional description text, collapsible mode. WCAG accessibility requirement.

**Copyable Text** (#153) — `{% copyable_text %}your-api-key-here{% endcopyable_text %}`. Inline text span with click-to-copy and brief "Copied!" tooltip confirmation. For API keys, user IDs, URLs, config values displayed inline.

**Sticky Header** (#171) — `{% sticky_header %}...{% endsticky_header %}`. Wrapper that uses `position: sticky` with shadow-on-scroll effect via IntersectionObserver.

**Connection Status Bar** (#175) — `{% connection_status %}`. Slim bar showing WebSocket connection state: hidden when connected, yellow "Reconnecting..." when disconnected, green "Reconnected" flash on recovery. Hooks into djust's `client.js` reconnection lifecycle.

**Live Counter** (#176) — `{% live_counter value=active_users label="online" stream_event="counter_update" %}`. Animated counter that updates in real-time via WebSocket push. Number rolls/fades on change. Optional prefix/suffix, compact formatting (1.2K), and trend arrow.

**Server Event Toast** (#177) — `self.push_toast("Saved!", type="success")` Python API + auto-rendering via `{% toast_container %}`. Server-side Python helper on `LiveView` that pushes toast notifications via WebSocket. Sends a special `__toast__` event that the existing `toast_container` auto-renders.

**Icon System** (#178) — `{% icon name="check" size="md" set="heroicons" %}`. Shared icon rendering primitive. Renders SVG icons from bundled icon sets (Heroicons Outline by default, extensible). Also provides `_render_icon(name, size, attrs)` Python helper for use in Rust handlers — eliminates the current pattern of every handler embedding independent SVG `<path>` strings.

**Page Header** (#179) — `{% page_header title="Products" subtitle="Manage inventory" %}{% page_header_actions %}{% dj_button label="Add" %}{% endpage_header_actions %}{% endpage_header %}`. Structured page-level header with title, optional subtitle/description, optional breadcrumb slot, and right-aligned action buttons area.

**Quality & DX Improvements** (#DX14) — Cross-cutting improvements for v1.4:

| Improvement | Description |
|-------------|-------------|
| **ARIA compliance audit** | Verify all 52 components meet WCAG 2.1 AA |
| **Dark mode testing** | Verify all components render correctly with both light and dark tokens |
| **CSS `@layer` adoption** | Wrap all component CSS in `@layer djust-components` |
| **Container queries** | Components like Card, StatCard, Data Table should adapt to container width |
| **CSS size audit** | Consider splitting into per-component CSS files or tree-shaking |
| **RTL support** | Add `dir="rtl"` awareness — use logical properties |
| **Animation consistency** | Standardize enter/exit transitions with shared keyframes |
| **Toast UX upgrade** | Sonner-style UX: stacked toasts, swipe-to-dismiss, configurable position |
| **Django template tag parity** | Add template tags for components 13-52 (currently Rust handler only) |
| **Responsive testing strategy** | Define breakpoints tested for each component category |

---

### Milestone: v1.5 — Data Table Pro Advanced + Django Integration + Missing Form Essentials

**Goal**: Complete Data Table Pro, integrate deeply with Django's form system, fill missing form components, build app chrome (sidebar, nav, toolbar), and ship AI-ready components. Makes djust-components the obvious choice for Django developers building CRUD apps and dashboards.

**Data Table Pro Phase 4 — Data Presentation** (#DTP-P4) — Column type formatters, footer aggregation row, conditional row/cell styling, multi-level column headers, row drag-and-drop reorder, copy row/selection.

| Feature | Description |
|---------|-------------|
| **Column type formatters** | Declare column type (`number`, `currency`, `date`, `percentage`, `boolean`) and auto-format display |
| **Footer aggregation row** | Optional footer row showing sum, average, count, min, max per column |
| **Conditional row/cell styling** | Highlight rows or cells based on data values |
| **Multi-level column headers** | Grouped column headers (e.g., "Q1" spanning Jan/Feb/Mar sub-columns) |
| **Row drag-and-drop reorder** | Drag grip handle to reorder rows |
| **Copy row/selection** | Copy selected rows as CSV/TSV to clipboard |

**Data Table Pro Phase 5 — Data Import & Computed** (#DTP-P5) — CSV/JSON import, computed columns, cell merge/colspan, column expressions, conditional formatting presets.

| Feature | Description |
|---------|-------------|
| **CSV/JSON import** | Upload a file to populate table rows. Parse, validate, preview before confirming |
| **Computed columns** | Define virtual columns derived from other columns |
| **Cell merge / colspan** | Merge cells horizontally for grouped displays |
| **Column expressions** | Filter columns with expressions (`> 100`, `contains "active"`) |
| **Conditional formatting presets** | Data bars, color scales, icon sets |

**Django Form Renderer** (#73) — `{% dj_form form=form %}`. Auto-renders any Django `Form` or `ModelForm` using djust-components. Maps `CharField` → `dj_input`, `ChoiceField` → `dj_select`, `BooleanField` → `dj_checkbox`, etc. Handles errors, help text, required markers.

**Django ModelForm Table** (#74) — `{% model_table queryset=qs %}`. Auto-generates a Data Table Pro from a Django QuerySet. Infers columns from model fields, supports sorting/filtering/pagination out of the box.

**Confirmation Dialog** (#75) — `{% confirm_dialog message="Delete?" confirm_event="delete" %}`. Reusable yes/no modal pattern. Wraps existing Modal with standard confirm/cancel buttons, danger variant.

**Popconfirm** (#180) — `{% popconfirm message="Delete this item?" confirm_event="delete" cancel_event="cancel" %}...{% endpopconfirm %}`. Inline confirmation popover that appears next to the trigger element. Less disruptive than modal Confirmation Dialog. Positions: top, bottom, left, right (auto-detects).

**Slider / Range** (#82) — `{% slider name="price" min=0 max=100 value=50 %}`. Horizontal slider with optional range mode (two handles), step, tick marks.

**Search Input** (#83) — `{% search_input name="q" placeholder="Search..." event="search" %}`. Input with search icon, clear button, loading spinner state, debounced event.

**Password Input** (#84) — `{% password_input name="pwd" %}`. Input with show/hide toggle button, strength meter bar.

**Autocomplete** (#85) — `{% autocomplete name="city" source_event="search_cities" %}`. Input with dropdown suggestions fetched server-side on keystroke, debounced. Distinct from Combobox: server-driven results.

**Sidebar Nav** (#86) — `{% sidebar %}...{% endsidebar %}`. Collapsible sidebar with nested menu items, section headers, icons, active state, mobile drawer.

**Toolbar** (#87) — `{% toolbar %}...{% endtoolbar %}`. Horizontal action bar with grouped buttons, separators, overflow menu.

**Inline Edit** (#88) — `{% inline_edit value=title event="update_title" %}`. Click text to edit in-place. Shows input on click, saves on Enter/blur, cancels on Escape.

**Avatar Group** (#89) — `{% avatar_group users=users max=5 %}`. Stacked overlapping avatars with "+N" overflow count.

**Navigation Menu** (#90) — `{% nav_menu %}...{% endnav_menu %}`. Top horizontal navigation with dropdowns, mega-menu support, active route highlighting, mobile hamburger collapse.

**Hover Card** (#91) — `{% hover_card %}...{% endhover_card %}`. Rich content card that appears on hover. Delay-in/delay-out to prevent flickering. GitHub-style user hovercards.

**Transfer List** (#98) — `{% transfer_list name="perms" available=available selected=selected event="transfer" %}`. Dual-list picker with search, select-all, and move-between buttons.

**Dependent Select** (#108) — `{% dependent_select name="city" parent="country" source_event="load_cities" %}`. Cascading dropdown that reloads options when parent select changes. Shows spinner while loading.

**Currency Input** (#109) — `{% currency_input name="price" currency="USD" min=0 %}`. Numeric input with currency symbol prefix, thousand separators, and decimal formatting.

**Form Validation Display** (#110) — `{% form_errors form=form %}` or `{% field_error field=form.email %}`. Renders Django form validation errors with styled inline messages, field highlighting.

**Wizard / Multi-step Form** (#111) — `{% wizard steps=steps active=current %}...{% endwizard %}`. Form split across steps with per-step validation, progress indicator, back/next navigation.

**Bottom Sheet** (#112) — `{% bottom_sheet %}...{% endbottom_sheet %}`. Mobile-optimized drawer that slides up from the bottom with drag-to-dismiss. Falls back to standard Sheet on desktop.

**Infinite Scroll** (#113) — `{% infinite_scroll load_event="load_more" threshold="200px" %}...{% endinfinite_scroll %}`. Container that fires a server event when the user scrolls near the bottom. Shows loading spinner.

**Time Picker** (#117) — `{% time_picker name="start_time" value="14:30" event="set_time" %}`. Hour/minute selector with AM/PM toggle or 24h mode.

**Expandable Text** (#118) — `{% expandable_text max_lines=3 %}...{% endexpandable_text %}`. Truncates long text with CSS `line-clamp`, shows "Read more" / "Show less" toggle.

**Countdown / Timer** (#126) — `{% countdown target="2026-04-01T00:00:00" event="timer_done" %}`. Displays days/hours/minutes/seconds counting down to a target datetime. Optional server event on expiry.

**Cookie Consent Banner** (#127) — `{% cookie_consent accept_event="accept_cookies" %}`. GDPR/privacy-compliant cookie consent banner with accept/reject/customize options.

**Conversation Thread** (#130) — `{% conversation_thread messages=messages stream_event="new_message" %}`. Chat-style message thread with sender avatars, timestamps, message grouping, and streaming response indicator.

**Model Selector** (#131) — `{% model_selector name="model" options=models value=current %}`. Rich select with model metadata (name, description, context window, pricing tier badge).

**Token Counter** (#132) — `{% token_counter current=tokens max=max_tokens %}`. Compact progress display showing token usage vs limit. Color transitions as limit approaches.

**Page Alert / Banner** (#142) — `{% page_alert type="success" dismissible=True %}Saved!{% endpage_alert %}`. Full-width alert at the top of page content area. Auto-dismiss after timeout.

**Dropdown Menu** (#143) — `{% dropdown_menu %}{% menu_item label="Edit" event="edit" %}{% menu_divider %}{% menu_item label="Delete" variant="danger" event="delete" %}{% enddropdown_menu %}`. Structured menu with items, dividers, submenus, keyboard navigation.

**Skeleton Factory** (#144) — `{% skeleton_for component="data_table" columns=5 rows=10 %}`. Auto-generates matching skeleton loading states for specific components.

**Meter / Stacked Progress** (#148) — `{% meter segments=usage_data total=100 %}`. Multiple colored segments in a single horizontal bar showing proportional breakdown.

**Feedback Widget** (#149) — `{% feedback event="rate_response" mode="thumbs" %}`. Inline thumbs up/down or 1-5 star rating for content. Modes: `thumbs`, `stars`, `emoji`.

**Truncated List** (#150) — `{% truncated_list items=assignees max=3 %}`. Renders first N items with "+X more" overflow indicator. Click expands to show all.

**Content Loader / Suspense Boundary** (#152) — `{% await loading_event="data_loaded" %}{% skeleton_for component="data_table" %}{% endawait %}`. Wrapper that shows placeholder content until a server event signals data is ready.

**Approval Gate** (#155) — `{% approval_gate message="Delete 47 records?" risk="high" approve_event="confirm" reject_event="cancel" %}`. Inline confirmation card for AI agent actions needing human approval.

**Source Citation** (#156) — `{% source_citation index=1 title="API Docs" url=url relevance=0.92 %}`. Inline footnote marker with hover popover showing source details.

**Multimodal Input** (#159) — `{% multimodal_input name="message" accept_files=True accept_voice=True event="send" %}`. Combined text area + file attachment + optional voice input + send button.

**AI Thinking Indicator** (#160) — `{% thinking_indicator status="thinking" label="Analyzing data..." %}`. Animated status display with variants: `thinking`, `searching`, `generating`, `tool_use`.

**Export Dialog** (#161) — `{% export_dialog formats=formats columns=export_cols event="export" %}`. Modal with format picker, per-format options, column selection, progress indicator.

**Import Wizard** (#162) — `{% import_wizard accepted_formats=".csv,.xlsx" model_fields=fields event="import_data" %}`. Multi-step import flow: file upload, column mapping, validation preview, confirm.

**Audit Log Table** (#163) — `{% audit_log entries=entries stream_event="new_entry" %}`. Pre-configured Data Table for audit/activity logs with actor, action, target, timestamp, and expandable diff.

**Filter Bar** (#166) — `{% filter_bar %}{% filter_select name="status" options=statuses %}{% filter_date_range name="dates" %}{% filter_search name="q" %}{% endfilter_bar %}`. Horizontal bar composing multiple filter controls with responsive collapse and active filter count badge.

**App Shell** (#167) — `{% app_shell %}{% app_sidebar %}...{% endapp_sidebar %}{% app_header %}...{% endapp_header %}{% app_content %}...{% endapp_content %}{% endapp_shell %}`. Complete responsive layout wrapper.

**Notification Popover** (#168) — `{% notification_popover notifications=notifs unread_count=count mark_read_event="mark_read" %}`. Bell icon trigger with unread badge + popover notification list.

**Inline Markdown Preview** (#169) — `{% markdown_textarea name="content" preview=True %}`. Textarea with live markdown preview. Uses existing Markdown component class for rendering.

**Form Array** (#170) — `{% form_array name="items" min=1 max=10 add_event="add_row" remove_event="remove_row" %}...{% endform_array %}`. Dynamic add/remove form rows with reorder support.

**Scroll Spy** (#172) — `{% scroll_spy sections=section_ids active_event="section_changed" active_class="scroll-spy-active" %}`. Watches scroll position and fires server event when the active section changes.

**Chat Bubble** (#55) — `{% chat_bubble message=msg %}`. Message thread UI with sender/time/status. Natural fit for djust's WebSocket architecture.

**Presence Avatars** (#56) — `{% presence_avatars users=online_users %}`. Stacked avatar group with overflow count. Pairs with djust PresenceMixin.

**Mentions / @input** (#57) — `{% mentions_input name="msg" users=users %}`. Text input that triggers user lookup on `@`.

**Error Boundary** (#174) — `{% error_boundary fallback="Component failed to render" %}...{% enderror_boundary %}`. Wrapper that catches rendering errors in child components and shows a fallback UI.

**Composition Guide** (#COMP-GUIDE) — Document common component nesting patterns: Card → Tabs, Modal → Form, Toolbar → Data Table, Sidebar → Breadcrumb.

**Server-side Helpers Module** (#HELPERS) — `from djust_components.helpers import push_toast, confirm_action`. Python utilities that pair with component tags.

**Component Presets** (#PRESETS) — Allow `{% dj_button preset="danger-confirm" %}` that maps to predefined param sets.

---

### Milestone: v2.0 — Advanced Interactive Components

**Goal**: Complex components that make djust-components a comprehensive enterprise-grade library. Each requires significant client-side JS and careful djust integration.

**Sortable List** (#67b) — `{% sortable_list items=items move_event="reorder" %}`. Drag-and-drop reorderable list with grip handles. Server event on drop with old/new indices.

**Sortable Grid** (#173) — `{% sortable_grid items=items columns=3 move_event="reorder" %}`. Drag-and-drop reorderable grid (2D) with snap-to-grid.

**Calendar View** (#68) — `{% calendar events=events month=month year=year %}`. Month/week/day calendar with event slots. Click to create, drag to reschedule.

**Gantt Chart** (#69) — `{% gantt_chart tasks=tasks %}`. Timeline bar chart for project management. Drag to resize/move tasks.

**Image Cropper** (#70) — `{% image_cropper src=image_url crop_event="save_crop" %}`. Drag-to-crop with aspect ratio lock. Returns crop coordinates to server.

**Signature Pad** (#71) — `{% signature_pad name="sig" save_event="save_signature" %}`. Canvas-based signature capture. Returns base64 PNG to server.

**Diff Viewer** (#72) — `{% diff_viewer old=old_text new=new_text %}`. Side-by-side or unified text diff with line highlighting.

**Pivot Table** (#119) — `{% pivot_table data=data rows="category" cols="quarter" values="revenue" agg="sum" %}`. Drag-and-drop configurable pivot table.

**Org Chart** (#120) — `{% org_chart nodes=nodes root=ceo_id %}`. Hierarchical tree visualization with expandable/collapsible nodes.

**Terminal** (#73b) — `{% terminal output=lines %}`. Monospace terminal emulator look with ANSI color support.

**Markdown Editor** (#74b) — `{% markdown_editor name="content" preview=True %}`. Split-pane markdown editor with live preview.

**Chart / Sparkline** (#75b) — `{% sparkline data=values %}`. Lightweight inline chart (SVG-based, no external lib). Line, bar, area variants.

**Map Picker** (#76b) — `{% map_picker lat=lat lng=lng pick_event="set_location" %}`. Click-to-pick location on a map.

**Tour / Onboarding Guide** (#121) — `{% tour steps=tour_steps active=0 %}`. Step-by-step product tour with spotlight highlights.

**JSON Viewer** (#122) — `{% json_viewer data=json_data collapsed_depth=2 %}`. Interactive collapsible JSON tree display.

**Log Viewer** (#123) — `{% log_viewer lines=log_lines stream_event="new_logs" %}`. Monospace streaming log display with auto-scroll and filtering.

**Prompt Template Editor** (#158) — `{% prompt_editor template=template variables=vars event="save_prompt" %}`. Structured prompt editing with highlighted `{{variable}}` slots. Low-value candidate — extremely niche.

**Voice Input Button** (#164) — `{% voice_input event="transcribe" lang="en-US" %}`. Mic button with recording state animation and waveform visualization.

**File Tree** (#165) — `{% file_tree nodes=files selected=current_file event="select_file" %}`. Specialized Tree View for file browser UIs with file/folder icons and context menu.

**Dashboard Grid** (#93) — `{% dashboard_grid %}...{% enddashboard_grid %}`. CSS Grid-based layout with draggable, resizable widget panels.

**Bar Chart** (#94) — `{% bar_chart data=data labels=labels %}`. Pure SVG bar chart with hover tooltips.

**Line Chart** (#95) — `{% line_chart series=series labels=labels %}`. SVG line/area chart with multiple series.

**Pie / Donut Chart** (#96) — `{% pie_chart segments=segments %}`. SVG pie/donut with labels and hover.

**Heatmap** (#97) — `{% heatmap data=matrix x_labels=x y_labels=y %}`. Color-coded grid for frequency/density data.

**Treemap** (#100) — `{% treemap data=data value_key="size" label_key="name" %}`. Nested rectangles showing hierarchical data proportionally.

**Comparison Table** (#101) — `{% comparison_table plans=plans features=features %}`. SaaS pricing/feature comparison with highlight column.

**Masonry Grid** (#102) — `{% masonry_grid items=items columns=3 %}`. Pinterest-style layout where items of varying heights pack efficiently.

**Cron Expression Input** (#145) — `{% cron_input name="schedule" value="0 9 * * 1-5" event="set_schedule" %}`. Visual cron expression builder with human-readable description.

**Calendar Heatmap** (#135) — `{% calendar_heatmap data=activity_data year=2026 %}`. GitHub-style contribution/activity heatmap. Pure SVG.

**Error Page** (#136) — `{% error_page code=404 title="Not Found" %}`. Styled error page template with illustration slot and action buttons.

**Image Upload Preview** (#137) — `{% image_upload_preview name="photos" max=5 event="upload" %}`. File Dropzone variant with thumbnail preview grid.

**Number Animation** (#141) — `{% animated_number value=revenue prefix="$" duration=800 %}`. Animated counting from old value to new value.

**Ribbon Badge** (#151) — `{% ribbon text="Popular" variant="primary" position="top-right" %}`. Corner ribbon/banner overlaid on parent container.

**Resizable Panel** (#114) — `{% resizable_panel direction="horizontal" %}...{% endresizable_panel %}`. Container with drag-to-resize handle. Extends Split Pane.

**Breadcrumb Dropdown** (#115) — `{% breadcrumb_dropdown items=items %}`. Breadcrumb that collapses middle items into "..." dropdown on overflow.

**Image Lightbox** (#99) — `{% lightbox images=gallery active=0 %}`. Full-screen image viewer overlay with navigation and zoom.

**Data Card Grid** (#92) — `{% data_card_grid items=items columns=3 %}`. Filterable, sortable grid of cards as alternative to Data Table.

**Agent Step Card** (#154) — `{% agent_step tool="search_db" status="complete" %}Found 12 results{% endagent_step %}`. Collapsible card showing AI agent tool use.

**QR Code** (#157) — `{% qr_code data="https://example.com" size="md" error_correction="M" %}`. Pure SVG QR code generator.

**Cursors Overlay** (#77) — `{% cursors users=online_users %}`. Show other users' cursor positions in real-time (Google Docs style). Uses PresenceMixin.

**Live Indicators** (#78) — `{% live_indicator user=editing_user field="title" %}`. "Alice is typing..." indicators per field.

**Collaborative Selection** (#79) — `{% collab_selection users=users %}`. Highlight text/cells other users have selected.

**Activity Feed** (#80) — `{% activity_feed events=events stream=True %}`. Real-time activity stream that auto-appends new events via WebSocket.

**Voting / Reactions** (#81) — `{% reactions options=emojis counts=counts event="react" %}`. Slack-style emoji reactions with live count updates.

---

### Milestone: v2.2 — CSS Architecture & Gallery Quality

**Goal**: Fix the three root causes blocking component gallery quality: CSS class name mismatches, destructive gallery reset, and design system token flow. These must land before per-category styling work can be effective.

**CSS Class Name Standardization** (#CSS-CLASS-NAMES) — Template tags render BEM-prefixed classes (`dj-card__header`, `dj-accordion__trigger`, `dj-tabs__nav`) but `components.css` targets unprefixed names (`.card-header`, `.accordion-trigger`, `.tabs-nav`). Neither file matches the other. Fix by updating `components.css` selectors to match the rendered HTML. Audit all 188 components — for each, verify the CSS selector matches what the Rust handler / template tag actually outputs. This is the single biggest reason components appear unstyled. Estimated scope: ~150 selector renames across 2300 lines of CSS. The BEM aliases added in PR #66 are a temporary bridge — this task replaces them with proper selectors.

**Gallery CSS Reset Fix** (#GALLERY-RESET) — The gallery view's inline `<style>` includes `*, *::before, *::after { padding: 0; margin: 0; }` which strips all component internal padding (card bodies, accordion triggers, tab buttons, etc.). This aggressive reset fights with component CSS regardless of `@layer` specificity. Fix by replacing with a scoped reset that only targets gallery layout elements (`.gallery-header`, `.gallery-sidebar`, `.gallery-content`) and leaves `.variant-preview` children untouched. Components inside preview cards should inherit their own padding from `components.css` / `components-classes.css` without interference.

---

### Milestone: v2.1 — Quality, Infrastructure & Pipeline Lessons

**Goal**: Address recurring issues identified across 43 pipeline retrospectives (PRs #12–54). No new components — this milestone is entirely quality, testing, accessibility, and developer experience.

**Gallery Examples for All Tags** (#GALLERY-EXAMPLES) — Add curated examples to `gallery/examples.py` for all ~150 template tags that shipped without gallery entries. Update `gallery/registry.py` discovery test to be dynamic (assert `>= N` instead of exact set). Split `examples.py` into per-category files. Add `--output` flag to gallery command for static HTML export. This is the single largest quality gap — the gallery was built in PR #12 but examples weren't added alongside components in PRs #13–54.

**Shared Test Infrastructure** (#TEST-INFRA) — Create `tests/conftest.py` with shared Django `settings.configure()`, djust stub setup, and common fixtures. All 38 test files currently duplicate this boilerplate. Make gallery discovery test dynamic so it doesn't break when new component classes are added (broke 6 times during the pipeline).

**Code Quality — Split Monolithic Files** (#CODE-SPLIT) — Split `templatetags/djust_components.py` (6,000+ lines) into per-category modules (forms, data, layout, feedback, ai, integration). Re-register all tags in the main file for backward compatibility. Extract DataTableHandler sub-renderers (`_render_header`, `_render_body`, `_render_footer`, `_render_toolbar`) to keep render() under 100 lines. Move all `import json` from call-site to module level in `rust_handlers.py`.

**ARIA Audit & Keyboard Navigation** (#ARIA-AUDIT) — Comprehensive pass adding missing ARIA attributes identified in retrospectives: `role="menu"`/`role="menuitem"` on dropdowns (Split Button, Context Menu, Dropdown Menu), `:focus-within` alongside `:hover` for popover/tooltip triggers (Source Citation, HoverCard), `role="status"` on Status Indicator, `role="region"` on Scroll Area, `aria-live="polite"` on Announcement Bar, unique ARIA IDs per component instance (Confirmation Dialog), keyboard navigation for overflow menus (Toolbar), and `aria-expanded` on toggle triggers.

**JS Test Infrastructure** (#JS-TESTS) — Add Playwright-based smoke tests for client-side JS modules: `data-table.js` (resize, keyboard nav), `data-grid.js` (cell editing), sortable components (drag-and-drop), and interactive popovers (open/close). Ship missing JS hook files for components that declare `dj-hook` but have no corresponding JS (Countdown, InfiniteScroll, ScrollSpy, MarkdownTextarea).

**Extract Shared Utilities** (#SHARED-UTILS) — Create `src/djust_components/utils.py` with functions duplicated across files: `_format_cell` (mixin + rust_handlers), `_interpolate_color` (mixin + rust_handlers), `CURRENCY_SYMBOLS` (templatetags + rust_handlers + component class). Fix mutable class-level defaults (`table_bulk_actions = []`) to `None` + init pattern throughout DataTableMixin.

**CSS Linting Rules** (#CSS-LINT) — Add stylelint configuration to flag: hardcoded durations (should use `var(--duration-*)`), hardcoded colors (should use `hsl(var(--*))`), physical direction properties (`margin-left` instead of `margin-inline-start`), and undeclared custom properties. Integrate into pre-commit hooks.

**Visual Regression Tests** (#VRT) — Add Playwright screenshot comparison tests using the Component Gallery. Capture baseline screenshots for all components in light/dark mode at mobile/tablet/desktop widths. Run on CI to catch CSS regressions. This was the most-requested testing improvement across retrospectives.

**Security Hardening Sweep** (#SEC-SWEEP) — Fix remaining security gaps: escape `custom_class` in all component class `_render_custom()` methods (inconsistent with template tag escaping), add position allowlist to Toast container, validate AuditLog action values against allowlist before CSS class injection, add `:focus-within` CSS for keyboard accessibility on all hover-triggered components. Add pre-commit hook scanning for `mark_safe` inside `<script>` blocks. Document which block tags pass inner content unescaped by design.

**Python Builtin Shadowing Cleanup** (#BUILTIN-SHADOW) — Rename parameters that shadow Python builtins across template tags: `type` → `variant` or `kind` (Toast, Alert, Callout, Announcement Bar, Page Alert), `open` → `is_open` (Confirmation Dialog, Sheet, Command Palette, Popconfirm), `range` → `is_range` or `range_mode` (Date Picker, Slider), `min`/`max` → `min_val`/`max_val` (Slider, Number Stepper, Currency Input). Preserve old parameter names as deprecated aliases for backward compatibility.

**Replace eval() in Computed Columns** (#EVAL-REPLACE) — Replace the `eval()` call in DataTableMixin's computed column evaluation with an AST-based arithmetic parser. Current implementation uses a character allowlist and empty `__builtins__`, but `eval()` with `.` and `()` is inherently risky. A simple recursive-descent parser for `+`, `-`, `*`, `/`, `%`, parentheses, and column references would be safer and faster.

**Component Open-State Standardization** (#OPEN-STATE) — Standardize how toggleable components track open/closed state. Currently mixed between CSS class (`.component-open`) and data attribute (`[data-open]`). Pick one convention and apply across: Sheet/Drawer, Command Palette, Popover, Context Menu, Dropdown, Split Button, Notification Popover, Popconfirm. Document the chosen convention.

**Real Django Integration Tests** (#DJANGO-REAL-TESTS) — Add `django.test.TestCase`-based tests for Django Form Renderer and ModelForm Table using real Django Form/ModelForm instances (not mocks). Validate against actual Django field/widget behavior including `DurationField`, `IPAddressField`, `JSONField`, and `ArrayField` which are not covered by the current mock-based tests. Requires a minimal Django test project with `DATABASES` configured.

---

## Contributing

### Component Category Index

| Category | Components |
|----------|-----------|
| **Layout** | Modal, Card, Tabs, Accordion, Collapsible, Split Pane, Sheet/Drawer, Scroll Area *(v1.4)*, Aspect Ratio *(v1.4)*, Sticky Header *(v1.4)*, Page Header *(v1.4)*, Resizable Panel *(v2.0)*, Bottom Sheet *(v1.5)*, App Shell *(v1.5)*, Dashboard Grid *(v2.0)*, Masonry Grid *(v2.0)* |
| **Navigation** | Breadcrumb, Breadcrumb Dropdown *(v2.0)*, Stepper, Table of Contents, Command Palette, Pagination, Sidebar Nav *(v1.5)*, Navigation Menu *(v1.5)*, Filter Bar *(v1.5)*, Notification Popover *(v1.5)*, Scroll Spy *(v1.5)*, Tour/Onboarding Guide *(v2.0)* |
| **Data Display** | Data Table, Badge, Notification Badge *(v1.4)*, Avatar, Avatar Group *(v1.5)*, Stat Card, Timeline, Tree View, Code Block, Code Snippet *(v1.4)*, Gauge, Carousel, Rating, Kbd, Description List *(v1.4)*, Diff Viewer *(v2.0)*, Callout/Blockquote *(v1.4)*, Comparison Table *(v2.0)*, Segmented Progress *(v1.4)*, Expandable Text *(v1.5)*, JSON Viewer *(v2.0)*, Org Chart *(v2.0)*, Number Animation *(v2.0)*, Responsive Image *(v1.4)*, Relative Time *(v1.4)*, Truncated List *(v1.5)*, Ribbon Badge *(v2.0)*, Copyable Text *(v1.4)*, Meter/Stacked Progress *(v1.5)*, Live Counter *(v1.4)* |
| **Data Visualization** | Sparkline *(v2.0)*, Bar Chart *(v2.0)*, Line Chart *(v2.0)*, Pie/Donut Chart *(v2.0)*, Heatmap *(v2.0)*, Calendar Heatmap *(v2.0)*, Treemap *(v2.0)*, Pivot Table *(v2.0)* |
| **Forms** | Button, Split Button *(v1.4)*, Input, Select, Rich Select *(v1.4)*, Textarea, Checkbox, Radio, Switch, Toggle Group *(v1.4)*, Combobox, Color Picker, Date Picker, Time Picker *(v1.5)*, File Dropzone, Image Upload Preview *(v2.0)*, Rich Text Editor, Form Group, Fieldset *(v1.4)*, Label *(v1.4)*, Input Group *(v1.4)*, Tag Input *(v1.4)*, Slider/Range *(v1.5)*, Search Input *(v1.5)*, Password Input *(v1.5)*, Autocomplete *(v1.5)*, Multi-select *(v1.4)*, OTP Input *(v1.4)*, Number Stepper *(v1.4)*, Currency Input *(v1.5)*, Dependent Select *(v1.5)*, Transfer List *(v1.5)*, Form Validation Display *(v1.5)*, Form Array *(v1.5)*, Wizard / Multi-step Form *(v1.5)*, Cron Expression Input *(v2.0)* |
| **Feedback** | Alert, Page Alert/Banner *(v1.5)*, Toast, Server Event Toast *(v1.4)*, Progress, Progress Circle *(v1.4)*, Spinner, Skeleton, Skeleton Factory *(v1.5)*, Empty State, Notification Center, Loading Overlay *(v1.4)*, Announcement Bar *(v1.4)*, Confirmation Dialog *(v1.5)*, Popconfirm *(v1.5)*, Status Indicator *(v1.4)*, Connection Status Bar *(v1.4)*, Countdown/Timer *(v1.5)*, Error Page *(v2.0)*, Feedback Widget *(v1.5)*, Content Loader/Suspense *(v1.5)*, Error Boundary *(v1.5)* |
| **Interactive** | Dropdown, Dropdown Menu *(v1.5)*, Tooltip, Popover, Hover Card *(v1.5)*, Context Menu, Copy Button, Tag/Chip, Divider, Kanban Board, Virtual List, Infinite Scroll *(v1.5)*, Inline Edit *(v1.5)*, Toolbar *(v1.5)*, Floating Action Button *(v1.4)*, Sortable List *(v2.0)*, Sortable Grid *(v2.0)*, Image Lightbox *(v2.0)*, Scroll to Top *(v1.4)*, Theme Toggle *(v1.4)* |
| **AI / LLM** | Streaming Text *(v1.4)*, Conversation Thread *(v1.5)*, Model Selector *(v1.5)*, Token Counter *(v1.5)*, Feedback Widget *(v1.5)*, Agent Step Card *(v2.0)*, Approval Gate *(v1.5)*, Source Citation *(v1.5)*, Multimodal Input *(v1.5)*, AI Thinking Indicator *(v1.5)*, Prompt Template Editor *(v2.0)*, Voice Input Button *(v2.0)* |
| **Developer Tools** | Terminal *(v2.0)*, Log Viewer *(v2.0)*, JSON Viewer *(v2.0)*, File Tree *(v2.0)* |
| **Collaboration** | Chat Bubble *(v1.5)*, Presence Avatars *(v1.5)*, Mentions Input *(v1.5)*, Cursors Overlay *(v2.0)*, Live Indicators *(v2.0)*, Collaborative Selection *(v2.0)*, Activity Feed *(v2.0)*, Voting/Reactions *(v2.0)* |
| **Ecosystem** | Django Form Renderer *(v1.5)*, ModelForm Table *(v1.5)*, Confirmation Dialog *(v1.5)*, Popconfirm *(v1.5)*, Export Dialog *(v1.5)*, Import Wizard *(v1.5)*, Audit Log Table *(v1.5)*, Server-side helpers *(v1.5)*, Cookie Consent Banner *(v1.5)* |

### Quick Wins Sprint (1 Day → v1.4-alpha0)

**Why this exists:** Eight review passes have planned 173 components but built zero. This sprint is the absolute minimum to prove execution velocity: 4 items, 1 day, no excuses.

**Entry criteria:** None. Start now.
**Exit criteria:** All 4 items done, `v1.4-alpha0` tagged.
**Rule:** No planning, no design decisions, no new ideas. Just ship.

```
=== Quick Wins Sprint (1 calendar day) ===

[x]  QW-1. Fix 7 unregistered Rust handlers                                    ~15 min
     ✅ ALREADY DONE — verified pass 12: handlers registered at rust_handlers.py:1358-1387.
     All 7 (DatePicker, FileDropzone, VirtualList, KanbanBoard, TableOfContents,
     RichTextEditor, SplitPane) are in INLINE_HANDLERS/BLOCK_HANDLERS via .extend() calls.

[ ]  QW-2. CSS Batch 0 — 5 easiest unstyled components                         ~3 hours

     FILE: src/djust_components/static/djust_components/components.css
     (append to end of file)

     Kbd (#38):       .kbd { ... } — monospace, border, padding, border-radius
     Copy Button (#37): .copy-button { ... } — button reset + checkmark transition
     Collapsible (#39): .collapsible-trigger, .collapsible-panel — chevron rotate + max-height transition
     Rating (#36):    .rating, .rating-star { ... } — inline SVG stars, filled/empty states, hover
     Code Block (#34): .code-block { ... } — pre/code background, padding, overflow-x, line-numbers

     VERIFY: Open any test app, render each component, confirm styled output.

[ ]  QW-3. 3 trivial new handlers + CSS                                         ~2 hours

     FILE: src/djust_components/rust_handlers.py (add handler classes)
     FILE: src/djust_components/templatetags/djust_components.py (add template tags)
     FILE: src/djust_components/static/djust_components/components.css (add CSS)

     Label (#66):       LabelHandler + @register tag + CSS for .dj-label
     Fieldset (#147):   FieldsetHandler + @register tag + CSS for .fieldset, .fieldset > legend
     Copyable Text (#153): CopyableTextHandler + @register tag + CSS for .copyable-text

[ ]  QW-4. Run tests + tag v1.4-alpha0                                          ~30 min

     cd /Users/tip/Dropbox/online_projects/ai/djust_project/djust-components
     uv run pytest tests/ -x          # all 158 existing tests must pass
     # bump version in pyproject.toml to 1.4.0a0
     git add -A && git commit -m "feat: v1.4-alpha0 — fix handler registration, CSS batch 0, 3 new components"
     git tag v1.4-alpha0
     git push && git push --tags

          ──── RELEASE v1.4-alpha0 HERE (1 day) ────
```

**After the sprint:** Resume full v1.4 execution order starting at step 1 (Component Gallery). Use actual time from QW-1 through QW-4 to calibrate remaining estimates.

### v1.4 Execution Order

The recommended execution order for v1.4, optimized for maximum user-visible impact per unit of work. Scroll Area (#62) is moved early because 5+ complex components need it for their CSS. Toggle Group (#61) is simple and fills a constant gap in toolbars/filters.

#### Phased Release Strategy

v1.4 is split into two sub-releases to get value to users faster:

**v1.4-alpha (~2 weeks):** CSS completion + Component Gallery + architecture primitives.

**v1.4-beta (~2 more weeks):** New components + Data Table Pro.

```
=== v1.4-alpha: CSS Completion + Foundation (~11 days) ===

[ ]  1. Component Gallery (management command) — visual QA for all CSS work  ~1 day
[ ]  2. Icon System (#178) — shared icon primitive for all components         ~0.75 day
         Provides _render_icon() helper, replaces inline SVGs in handlers
[ ]  3. Z-Index token scale + Focus Trap primitive + Portal primitive         ~0.75 day
[ ]  4. Scroll Area component (#62) — needed by Batch 4 components           ~0.5 day
[ ]  5. Aspect Ratio (#116) + Status Indicator (#128) + Scroll to Top (#125) ~0.5 day
         + Relative Time (#146) + Callout (#67) + Description List (#134)
         + Sticky Header (#171) + Page Header (#179)
[ ]  6. Toggle Group (#61) + Progress Circle (#124)                          ~0.75 day
         + Theme Toggle (#138) — simple, instant value
[ ]  7. CSS Batch 2 (Popover, Sheet, Context Menu, Command Palette)          ~2 days
[ ]  8. CSS Batch 3 (Combobox, Color Picker, Date Picker, File Dropzone)     ~2 days
[ ]  9. CSS Batch 4 (remaining complex components — use Scroll Area)         ~2.5 days
         ──── RELEASE v1.4-alpha HERE (~11 days) ────

=== v1.4-beta: New Components + Data Table Pro (~18 days) ===

[ ] 10. Code Snippet (#139) + Responsive Image (#140) — compose existing     ~0.5 day
[ ] 11. Input Group (#64) + Split Button (#133) — form addon + action combo  ~0.75 day
[ ] 12. Data Table Pro Phase 1 — sorting + selection + filtering + search    ~3 days
         + ARIA + DataTableMixin (auto-generates event handlers from model)
[ ] 13. Streaming Text (#129) + Connection Status Bar (#175)                 ~1.5 days
         + Live Counter (#176) — djust-native real-time components
[ ] 14. Server Event Toast (#177) + Toast UX upgrade (Sonner-style)          ~1.5 days
         — promotes push_toast() from v1.5, ships with CSS polish
[ ] 15. Test coverage for all 40+ untested handlers                          ~2 days
[ ] 16. Component class expansion (Alert, StatCard, Tag, Toast, Progress)    ~1.5 days
[ ] 17. Data Table Pro Phase 2 — inline editing, resize, column visibility,  ~3.5 days
         density toggle, responsive card-collapse mode, editable row mode
[ ] 18. New components: Multi-select, OTP Input, Number Stepper              ~2 days
[ ] 19. New components: Tag Input (#63), Floating Action Button (#65)        ~1.5 days
[ ] 20. Rich Select (#103), Loading Overlay (#104), Notification Badge (#105) ~1.5 days
[ ] 21. Announcement Bar (#106), Segmented Progress (#107)                   ~1 day
[ ] 22. DnD primitive (~200 lines JS + keyboard fallback per WCAG 2.5.7)     ~1.5 days
[ ] 23. Data Table Pro Phase 3 — row expansion, bulk actions, export,
         faceted filtering, state persistence, column pinning, col stats     ~4 days
[ ] 24. Inter-component event bus protocol design                            ~0.5 day
[ ] 25. Keyboard Shortcut Framework                                          ~0.5 day
[ ] 26. ARIA audit + keyboard nav + WCAG 2.2 compliance                      ~2 days
[ ] 27. CSS @layer adoption + container queries + tree-shaking setup         ~1 day
         ──── RELEASE v1.4 stable (~32 days total) ────
```

**Note:** Data Table Pro Phases 4-5 moved to v1.5. Chat Bubble, Presence Avatars, Mentions Input moved to v1.5 collaboration batch.

### v1.5 Execution Order

```
=== v1.5-alpha: Data Table Pro + Django Integration (~20 days) ===

[ ]  1. Data Table Pro Phase 4 — column formatters, footer aggregation,
        conditional styling, multi-level headers, row DnD                    ~3 days
[ ]  2. Data Table Pro Phase 5 — CSV import, computed columns, cell merge,
        column expressions, conditional formatting presets                   ~3 days
[ ]  3. Confirmation Dialog + Popconfirm (#180) — modal + inline confirm     ~2 days
[ ]  4. Form Validation Display (#110) — inline errors + field highlighting  ~1 day
[ ]  5. Slider/Range + Search Input + Password Input (form essentials)       ~3 days
[ ]  6. Time Picker (#117) — pairs with Date Picker for datetime flows       ~1.5 days
[ ]  7. Django Form Renderer (maps Django Form fields to components)         ~3 days
[ ]  8. Form Array (#170) — dynamic add/remove form rows                    ~2 days
[ ]  9. Dependent Select (#108) + Currency Input (#109)                      ~2 days
[ ] 9b. Autocomplete (shares Combobox infrastructure)                        ~2 days

         ──── RELEASE v1.5-alpha HERE (~20 days) ────

=== v1.5-beta: App Chrome + AI Components (~25 days) ===

[ ] 10. Wizard / Multi-step Form (#111) — uses Segmented Progress           ~3 days
[ ] 11. Cookie Consent Banner (#127) — GDPR compliance                       ~1 day
[ ] 12. Transfer List (#98) — dual-list picker for admin UIs                 ~2 days
[ ] 13. Sidebar Nav + Navigation Menu + App Shell (#167) (full app chrome)   ~5 days
[ ] 14. Toolbar + Inline Edit + Filter Bar (#166)                            ~4 days
[ ] 15. Avatar Group + Hover Card + Notification Popover (#168)              ~3 days
[ ] 16. AI components: Conversation Thread (#130), Model Selector (#131),
        Token Counter (#132), Feedback Widget (#149),
        Approval Gate (#155), Source Citation (#156), Multimodal Input (#159),
        AI Thinking Indicator (#160) — complete AI app UI                   ~6 days
[ ] 16b. Chat Bubble (#55) + Presence Avatars (#56) + Mentions Input (#57)   ~2 days

         ──── RELEASE v1.5-beta HERE (~45 days) ────

=== v1.5 stable: Polish + remaining (~10 days) ===

[ ] 17. Countdown/Timer (#126) + Infinite Scroll (#113)                      ~2 days
[ ] 18. Expandable Text (#118) + Truncated List (#150)                       ~1 day
         + Inline Markdown Preview (#169) + Scroll Spy (#172)
[ ] 19. Skeleton Factory (#144) + Content Loader / Suspense (#152)           ~2 days
[ ] 20. Meter/Stacked Progress (#148) + Page Alert (#142) + Dropdown Menu (#143)  ~2.5 days
[ ] 21. Django ModelForm Table (builds on Data Table Pro + Form Renderer)    ~3 days
[ ] 22. Export Dialog (#161) + Import Wizard (#162)                          ~4 days
[ ] 23. Audit Log Table (#163) — specialized Data Table for compliance      ~2 days
[ ] 24. Server-side helpers module + component presets                       ~2 days
[ ] 25. Composition guide + documentation                                    ~1 day

         ──── RELEASE v1.5 stable (~55 days total) ────
```

### Moved from v1.5 to v2.0
These are valuable but not essential for the first year:
- Cron Expression Input (#145) — niche scheduling UI
- Calendar Heatmap (#135) — data viz, better in v2.0 with charts
- QR Code (#157) — useful but niche
- Image Upload Preview (#137) — File Dropzone is sufficient for v1.5
- Resizable Panel (#114) — Split Pane is sufficient
- Breadcrumb Dropdown (#115) — current Breadcrumb is sufficient
- Number Animation (#141) — polish, not essential
- Ribbon Badge (#151) — decorative
- Bottom Sheet (#112) — Sheet/Drawer covers this
- Image Lightbox (#99) — Carousel + Modal covers this
- Data Card Grid (#92) — card layout is easy to hand-build
- Agent Step Card (#154) — moved to v2.0 Collaboration Suite

### Architecture Improvements (v1.4 prerequisite)

Before scaling to 180+ components, three refactors will prevent technical debt from compounding:

#### 1. Shared Icon Rendering (`_render_icon()` helper)

**Current state**: Every handler that renders an icon embeds raw SVG `<path>` strings independently. AlertHandler has its own check/warning/info SVGs (~15 lines each). ToastContainerHandler duplicates the same icons. ButtonHandler has spinner SVG. RatingHandler has star SVG. CopyButtonHandler has clipboard/check SVGs.

**Problem**: (a) Inconsistent icon sizes/viewBoxes across components, (b) no user swappability, (c) bloated HTML.

**Solution**: Icon System component (#178) provides `_render_icon(name, size="md", **attrs)` that all handlers call. Icon set is a dict mapping `name → SVG markup`. Users can override via `DJUST_COMPONENTS_ICON_SET` setting.

#### 2. Shared ARIA & Event Attribute Helpers

**Current state**: Handlers build `dj-click`, `dj-input`, `aria-expanded`, `aria-controls`, `role` attributes with f-strings. Each handler independently implements the same patterns.

**Solution**: Extract `_event_attrs(click=None, input=None, change=None)` and `_aria_attrs(expanded=None, controls=None, role=None, label=None)` helpers.

#### 3. Handler Base Class (optional, v1.4-beta)

**Current state**: All 56 handlers are plain classes with a `render()` method. No shared initialization, no shared escaping, no shared argument parsing.

**Proposed**: `class InlineHandler` and `class BlockHandler` base classes that handle `_parse_args()`, provide `self.icon()`, `self.aria()`, `self.event_attrs()`, and auto-escape string values.

### Priority Rationale

**Why Icon System is in v1.4-alpha (before CSS batches):** CSS Batch 1-4 will add styles for 22 components, many of which render icons. If the Icon System ships first, CSS authors can style consistent `<svg class="icon icon-sm">` elements instead of arbitrary inline SVGs.

**Why Page Header is trivial but important:** It's ~25 lines of CSS but literally the first thing every developer builds when starting a new page.

**Why Popconfirm is in v1.5 (not v1.4):** It composes Popover positioning (which gets CSS in v1.4 Batch 2). Building it after Popover CSS is stable avoids rework.

**Why CSS completion is P0:** 22 components render unstyled HTML. This is the most embarrassing gap.

**Why Data Table Pro is P0 with 3 phases:** Every SaaS app has a data table. Phase 1 covers 80% of use cases.

**Why v1.5 exists between v1.4 and v2.0:** v2.0 contained several simple, high-value components (Confirmation Dialog, Toast from Event). v1.5 bridges the gap.

**Why test coverage is P1:** 40 untested handlers means regressions slip through silently.

**Why Toggle Group and Scroll Area are in v1.4:** Toggle Group fills a gap in every toolbar. Scroll Area is a primitive that 5+ unstyled components need for their CSS.

**Why Navigation Menu, Hover Card, and Data Card Grid are in v1.5:** They complete the app chrome story alongside Sidebar Nav and compose from existing primitives.
