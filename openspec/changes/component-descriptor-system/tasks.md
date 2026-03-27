## 1. TypedState Foundation

- [x] 1.1 Add `_dirty` flag tracking to TypedState `__setitem__` (set True on value change, skip for same-value)
- [x] 1.2 Add `_cached_html` and `_render_hash` attributes to TypedState for render caching
- [x] 1.3 Add tests: dirty flag on mutation, same-value stays clean, from_dict rehydration idempotent
- [x] 1.4 Update TypedState docstrings to document the dirty/cache contract

## 2. Descriptor Protocol on LiveComponent

- [x] 2.1 Add `__set_name__` to LiveComponent — stores attr name, storage key, builds `_component_descriptors` registry on owner class
- [x] 2.2 Add `__get__` to LiveComponent — returns TypedState from `obj.__dict__["_component_{name}"]`, lazy-creates with defaults, rehydrates plain dicts
- [x] 2.3 Add `__set__` to LiveComponent — accepts plain dict, converts to State class
- [x] 2.4 Add `State` inner class pattern — AccordionState, TabsState, ModalState, etc. as inner classes on each component
- [x] 2.5 Inject `component_id` into state dict on access (equals attribute name)
- [x] 2.6 Add tests: descriptor on LiveView class, per-instance isolation, inheritance, dict assignment, rehydration round-trip

## 3. Auto Event Handler Registration

- [x] 3.1 Add `Meta.event` to each component class (e.g., `event = "accordion_toggle"`)
- [x] 3.2 Implement `_make_event_handler()` that creates a handler routing by `component_id`
- [x] 3.3 Register handler on owner class via `__set_name__` (skip if method already exists)
- [x] 3.4 Implement single-instance auto-resolution (empty component_id → sole instance of that type)
- [x] 3.5 Add tests: auto-registration, user override precedence, multi-instance routing, single-instance fallback

## 4. Component Classes (P0)

- [x] 4.1 Create `Accordion` LiveComponent with State(active, multiple), toggle method, Meta(event, tier)
- [x] 4.2 Create `Tabs` LiveComponent with State(active), set method
- [x] 4.3 Create `Modal` LiveComponent with State(is_open), open/close/toggle methods
- [x] 4.4 Create `Collapsible` LiveComponent with State(is_open), toggle method
- [x] 4.5 Create `Sheet` LiveComponent with State(is_open, side), open/close methods
- [x] 4.6 Create `Dropdown` LiveComponent with State(is_open), toggle/close methods, Meta(tier="client")
- [x] 4.7 Create `Tooltip` LiveComponent with State(is_visible), show/hide methods, Meta(tier="client")
- [x] 4.8 Create `Carousel` LiveComponent with State(active, total), prev/next/go methods
- [x] 4.9 Add tests for each component: state defaults, methods, serialization, tier declaration

## 5. Render Caching

- [x] 5.1 Add dirty-flag check to `_sync_state_to_rust` or `get_context_data` — skip render for clean components
- [x] 5.2 Store cached HTML on TypedState keyed by state hash
- [x] 5.3 Clear cache and dirty flag after successful render
- [x] 5.4 Add tests: clean component skips render, dirty component re-renders, cache invalidation on mutation

## 6. Dependency Tracking

- [x] 6.1 Call `extract_template_variables()` at mount time, store result as `_template_deps`
- [x] 6.2 Cross-reference `_template_deps` with `_component_descriptors` to identify referenced components
- [x] 6.3 Use dep map + dirty flags in `_sync_state_to_rust` to skip syncing unreferenced/clean components
- [x] 6.4 Cache dep map per template content hash
- [x] 6.5 Add tests: dep map built correctly, unreferenced components excluded, cache hit on repeated mount

## 7. Client/Server Tier System

- [x] 7.1 Add `Meta.tier` and `Meta.optimistic_rule` to component classes
- [x] 7.2 Serialize optimistic rules to JSON and include in mount response metadata
- [x] 7.3 Client JS: parse optimistic rules, apply DOM change on event before WebSocket send
- [~] 7.4 Client JS: for client-tier components, skip WebSocket send entirely (deferred — requires djust core JS changes; TODO added to Dropdown/Tooltip Meta)
- [~] 7.5 Add `dj-update="ignore"` to client-tier component wrapper divs (deferred — requires djust core JS changes; TODO added to Dropdown/Tooltip Meta)
- [x] 7.6 Add tests: tier declaration, optimistic rule format, client-tier no-server-event

## 8. Gallery Proof-of-Concept

- [x] 8.1 Refactor LayoutGalleryView to use descriptor-based components instead of mixins
- [x] 8.2 Refactor remaining category views (Form, Data, Overlay, etc.)
- [x] 8.3 Update gallery templates to use `{{ faq.active }}` / `{{ faq.component_id }}` pattern
- [x] 8.4 Update gallery tests for descriptor-based views
- [~] 8.5 Verify accordion/tabs/modal interactivity works end-to-end in browser (requires running gallery server)

## 9. Migration & Documentation

- [x] 9.1 Mark DEP-001 mixins as deprecated in docstrings and CHANGELOG
- [x] 9.2 Update DEP-002 spec with any changes discovered during implementation
- [x] 9.3 Write migration guide: mixin → descriptor (with before/after examples)
- [x] 9.4 Update package exports in `__init__.py`
- [x] 9.5 Update CHANGELOG.md with feat: entry
