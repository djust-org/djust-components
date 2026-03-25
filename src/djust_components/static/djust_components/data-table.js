/**
 * djust-components Data Table Pro — Client-side enhancements.
 *
 * Handles column resize, column reorder, column visibility toggle,
 * and inline cell editing activation. These features run entirely
 * in the browser — no server round-trip for drag/resize operations.
 *
 * Auto-initializes on DOMContentLoaded and observes for dynamically
 * inserted tables (djust LiveView patches).
 */
(function () {
  "use strict";

  // ── Column Resize ──────────────────────────────────────────────

  function initResize(wrapper) {
    if (wrapper._dtResize) return;
    wrapper._dtResize = true;

    const table = wrapper.querySelector("table.data-table");
    if (!table) return;

    const headers = table.querySelectorAll("th[data-resizable]");
    headers.forEach(function (th) {
      const handle = document.createElement("div");
      handle.className = "data-table-resize-handle";
      th.appendChild(handle);

      let startX, startWidth;

      handle.addEventListener("mousedown", function (e) {
        e.preventDefault();
        e.stopPropagation();
        startX = e.clientX;
        startWidth = th.offsetWidth;
        handle.classList.add("resizing");

        function onMove(ev) {
          const dx = ev.clientX - startX;
          const newWidth = Math.max(40, startWidth + dx);
          th.style.width = newWidth + "px";
          th.style.minWidth = newWidth + "px";
        }

        function onUp() {
          handle.classList.remove("resizing");
          document.removeEventListener("mousemove", onMove);
          document.removeEventListener("mouseup", onUp);
        }

        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
      });
    });
  }

  // ── Column Reorder ─────────────────────────────────────────────

  function initReorder(wrapper) {
    if (wrapper._dtReorder) return;
    wrapper._dtReorder = true;

    const table = wrapper.querySelector("table.data-table");
    if (!table) return;

    const headerRow = table.querySelector("thead tr");
    if (!headerRow) return;

    const draggableHeaders = headerRow.querySelectorAll("th[draggable='true']");
    if (!draggableHeaders.length) return;

    let dragSrc = null;

    draggableHeaders.forEach(function (th) {
      th.addEventListener("dragstart", function (e) {
        dragSrc = th;
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", th.cellIndex);
        th.style.opacity = "0.5";
      });

      th.addEventListener("dragover", function (e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        th.classList.add("drag-over");
      });

      th.addEventListener("dragleave", function () {
        th.classList.remove("drag-over");
      });

      th.addEventListener("drop", function (e) {
        e.preventDefault();
        th.classList.remove("drag-over");
        if (dragSrc === th) return;

        var fromIdx = dragSrc.cellIndex;
        var toIdx = th.cellIndex;

        // Reorder all rows
        var allRows = table.querySelectorAll("tr");
        allRows.forEach(function (row) {
          var cells = Array.from(row.children);
          if (fromIdx < cells.length && toIdx < cells.length) {
            var moved = cells[fromIdx];
            if (fromIdx < toIdx) {
              row.insertBefore(moved, cells[toIdx].nextSibling);
            } else {
              row.insertBefore(moved, cells[toIdx]);
            }
          }
        });

        // Fire reorder event if the wrapper has an event name
        var reorderEvent = wrapper.getAttribute("data-reorder-event");
        if (reorderEvent) {
          var newOrder = Array.from(headerRow.querySelectorAll("th[data-col-key]"))
            .map(function (h) { return h.getAttribute("data-col-key"); })
            .filter(Boolean)
            .join(",");
          // Use djust pushEvent if available via dj-click simulation
          var hiddenBtn = wrapper.querySelector(".data-table-reorder-trigger");
          if (hiddenBtn) {
            hiddenBtn.setAttribute("data-value", newOrder);
            hiddenBtn.click();
          }
        }
      });

      th.addEventListener("dragend", function () {
        th.style.opacity = "";
        draggableHeaders.forEach(function (h) {
          h.classList.remove("drag-over");
        });
      });
    });
  }

  // ── Column Visibility ──────────────────────────────────────────

  function initVisibility(wrapper) {
    if (wrapper._dtVisibility) return;
    wrapper._dtVisibility = true;

    var btn = wrapper.querySelector(".data-table-visibility-btn");
    var menu = wrapper.querySelector(".data-table-visibility-menu");
    if (!btn || !menu) return;

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      menu.classList.toggle("open");
    });

    document.addEventListener("click", function () {
      menu.classList.remove("open");
    });

    menu.addEventListener("click", function (e) {
      e.stopPropagation();
    });

    var checkboxes = menu.querySelectorAll("input[type='checkbox']");
    checkboxes.forEach(function (cb) {
      cb.addEventListener("change", function () {
        var colKey = cb.getAttribute("data-col-key");
        var table = wrapper.querySelector("table.data-table");
        if (!table || !colKey) return;

        // Find column index
        var headers = table.querySelectorAll("thead tr:first-child th");
        var colIdx = -1;
        headers.forEach(function (th, idx) {
          if (th.getAttribute("data-col-key") === colKey) colIdx = idx;
        });
        if (colIdx === -1) return;

        var display = cb.checked ? "" : "none";
        // Toggle header
        headers[colIdx].style.display = display;
        // Toggle filter row if present
        var filterRow = table.querySelector("thead tr:nth-child(2)");
        if (filterRow && filterRow.children[colIdx]) {
          filterRow.children[colIdx].style.display = display;
        }
        // Toggle body cells
        table.querySelectorAll("tbody tr").forEach(function (row) {
          if (row.children[colIdx]) {
            row.children[colIdx].style.display = display;
          }
        });

        // Fire visibility event
        var visEvent = wrapper.getAttribute("data-visibility-event");
        if (visEvent) {
          var visible = [];
          checkboxes.forEach(function (c) {
            if (c.checked) visible.push(c.getAttribute("data-col-key"));
          });
          var trigger = wrapper.querySelector(".data-table-visibility-trigger");
          if (trigger) {
            trigger.setAttribute("data-value", visible.join(","));
            trigger.click();
          }
        }
      });
    });
  }

  // ── Density Toggle ─────────────────────────────────────────────

  function initDensity(wrapper) {
    if (wrapper._dtDensity) return;
    wrapper._dtDensity = true;

    var btns = wrapper.querySelectorAll(".data-table-density-btn");
    if (!btns.length) return;

    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var table = wrapper.querySelector("table.data-table");
        if (!table) return;

        var density = btn.getAttribute("data-density");
        // Remove all density classes
        table.classList.remove("data-table-compact", "data-table-spacious");
        if (density === "compact") {
          table.classList.add("data-table-compact");
        } else if (density === "spacious") {
          table.classList.add("data-table-spacious");
        }

        // Update active state
        btns.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
      });
    });
  }

  // ── Inline Cell Editing (activation) ───────────────────────────

  function initInlineEdit(wrapper) {
    if (wrapper._dtInlineEdit) return;
    wrapper._dtInlineEdit = true;

    var table = wrapper.querySelector("table.data-table");
    if (!table) return;

    table.addEventListener("click", function (e) {
      var td = e.target.closest("td[data-editable='true']");
      if (!td || td.querySelector("input")) return;

      var currentValue = td.textContent.trim();
      var colKey = td.getAttribute("data-col-key");
      var rowKey = td.closest("tr").getAttribute("data-row-key");
      var editEvent = wrapper.getAttribute("data-edit-event");

      td.classList.add("data-table-cell-editing");
      var input = document.createElement("input");
      input.type = "text";
      input.value = currentValue;
      td.textContent = "";
      td.appendChild(input);
      input.focus();
      input.select();

      function finish(save) {
        var newValue = input.value;
        td.classList.remove("data-table-cell-editing");
        td.textContent = save ? newValue : currentValue;

        if (save && newValue !== currentValue && editEvent) {
          // Fire edit event via hidden trigger
          var trigger = wrapper.querySelector(".data-table-edit-trigger");
          if (trigger) {
            trigger.setAttribute("data-value", JSON.stringify({
              row_key: rowKey,
              column: colKey,
              value: newValue
            }));
            trigger.click();
          }
        }
      }

      input.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter") { ev.preventDefault(); finish(true); }
        if (ev.key === "Escape") { ev.preventDefault(); finish(false); }
      });

      input.addEventListener("blur", function () {
        // Small delay to allow keydown to fire first
        setTimeout(function () {
          if (td.querySelector("input")) finish(false);
        }, 100);
      });
    });
  }

  // ── Init all features on a wrapper ─────────────────────────────

  function initDataTable(wrapper) {
    if (wrapper.hasAttribute("data-resizable")) initResize(wrapper);
    if (wrapper.hasAttribute("data-reorderable")) initReorder(wrapper);
    if (wrapper.querySelector(".data-table-visibility-btn")) initVisibility(wrapper);
    if (wrapper.querySelector(".data-table-density-btn")) initDensity(wrapper);
    if (wrapper.hasAttribute("data-edit-event")) initInlineEdit(wrapper);
  }

  function initAll() {
    document.querySelectorAll(".data-table-wrapper").forEach(initDataTable);
  }

  // Init on load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }

  // Re-init on djust LiveView patches (MutationObserver)
  var observer = new MutationObserver(function (mutations) {
    var shouldInit = false;
    mutations.forEach(function (m) {
      if (m.addedNodes.length) shouldInit = true;
    });
    if (shouldInit) initAll();
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();
