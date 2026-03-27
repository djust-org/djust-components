## 1. TypedState Foundation

- [x] 1.1 Add `_dirty` flag tracking to TypedState `__setitem__` (set True on value change, skip for same-value)
- [x] 1.2 Add `_cached_html` and `_render_hash` attributes to TypedState for render caching
- [x] 1.3 Add tests: dirty flag on mutation, same-value stays clean, from_dict rehydration idempotent
- [x] 1.4 Update TypedState docstrings to document the dirty/cache contract

## 2. Descriptor Protocol on LiveComponent

- [ ] 2.1 Add `__set_name__` to LiveComponent — stores attr name, storage key, builds `_component_descriptors` registry on owner class
- [ ] 2.2 Add `__get__` to LiveComponent — returns TypedState from `obj.__dict__["_component_{name}"]`, lazy-creates with defaults, rehydrates plain dicts
- [ ] 2.3 Add `__set__` to LiveComponent — accepts plain dict, converts to State class
- [ ] 2.4 Add `State` inner class pattern — AccordionState, TabsState, ModalState, etc. as inner classes on each component
- [ ] 2.5 Inject `component_id` into state dict on access (equals attribute name)
- [ ] 2.6 Add tests: descriptor on LiveView class, per-instance isolation, inheritance, dict assignment, rehydration round-trip

## 3. Auto Event Handler Registration

- [ ] 3.1 Add `Meta.event` to each component class (e.g., `event = "accordion_toggle"`)
- [ ] 3.2 Implement `_make_event_handler()` that creates a handler routing by `component_id`
- [ ] 3.3 Register handler on owner class via `__set_name__` (skip if method already exists)
- [ ] 3.4 Implement single-instance auto-resolution (empty component_id → sole instance of that type)
- [ ] 3.5 Add tests: auto-registration, user override precedence, multi-instance routing, single-instance fallback

## 4. Component Classes (P0)

- [ ] 4.1 Create `Accordion` LiveComponent with State(active, multiple), toggle method, Meta(event, tier)
- [ ] 4.2 Create `Tabs` LiveComponent with State(active), set method
- [ ] 4.3 Create `Modal` LiveComponent with State(is_open), open/close/toggle methods
- [ ] 4.4 Create `Collapsible` LiveComponent with State(is_open), toggle method
- [ ] 4.5 Create `Sheet` LiveComponent with State(is_open, side), open/close methods
- [ ] 4.6 Create `Dropdown` LiveComponent with State(is_open), toggle/close methods, Meta(tier="client")
- [ ] 4.7 Create `Tooltip` LiveComponent with State(is_visible), show/hide methods, Meta(tier="client")
- [ ] 4.8 Create `Carousel` LiveComponent with State(active, total), prev/next/go methods
- [ ] 4.9 Add tests for each component: state defaults, methods, serialization, tier declaration

## 5. Render Caching

- [ ] 5.1 Add dirty-flag check to `_sync_state_to_rust` or `get_context_data` — skip render for clean components
- [ ] 5.2 Store cached HTML on TypedState keyed by state hash
- [ ] 5.3 Clear cache and dirty flag after successful render
- [ ] 5.4 Add tests: clean component skips render, dirty component re-renders, cache invalidation on mutation

## 6. Dependency Tracking

- [ ] 6.1 Call `extract_template_variables()` at mount time, store result as `_template_deps`
- [ ] 6.2 Cross-reference `_template_deps` with `_component_descriptors` to identify referenced components
- [ ] 6.3 Use dep map + dirty flags in `_sync_state_to_rust` to skip syncing unreferenced/clean components
- [ ] 6.4 Cache dep map per template content hash
- [ ] 6.5 Add tests: dep map built correctly, unreferenced components excluded, cache hit on repeated mount

## 7. Client/Server Tier System

- [ ] 7.1 Add `Meta.tier` and `Meta.optimistic_rule` to component classes
- [ ] 7.2 Serialize optimistic rules to JSON and include in mount response metadata
- [ ] 7.3 Client JS: parse optimistic rules, apply DOM change on event before WebSocket send
- [ ] 7.4 Client JS: for client-tier components, skip WebSocket send entirely
- [ ] 7.5 Add `dj-update="ignore"` to client-tier component wrapper divs
- [ ] 7.6 Add tests: tier declaration, optimistic rule format, client-tier no-server-event

## 8. Gallery Proof-of-Concept

- [ ] 8.1 Refactor LayoutGalleryView to use descriptor-based components instead of mixins
- [ ] 8.2 Refactor remaining category views (Form, Data, Overlay, etc.)
- [ ] 8.3 Update gallery templates to use `{{ faq.active }}` / `{{ faq.component_id }}` pattern
- [ ] 8.4 Update gallery tests for descriptor-based views
- [ ] 8.5 Verify accordion/tabs/modal interactivity works end-to-end in browser

## 9. Migration & Documentation

- [ ] 9.1 Mark DEP-001 mixins as deprecated in docstrings and CHANGELOG
- [ ] 9.2 Update DEP-002 spec with any changes discovered during implementation
- [ ] 9.3 Write migration guide: mixin → descriptor (with before/after examples)
- [ ] 9.4 Update package exports in `__init__.py`
- [ ] 9.5 Update CHANGELOG.md with feat: entry
