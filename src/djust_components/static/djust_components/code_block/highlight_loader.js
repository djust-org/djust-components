/**
 * highlight_loader.js — Lazy-loads highlight.js from CDN for djust code_block components.
 *
 * Checks window.__djcHljsLoaded to avoid duplicate loading.
 * Runs hljs.highlightAll() on all unhighlighted blocks once the library is ready.
 * Intended to be referenced by the code_block templatetag when highlight=True.
 */
(function () {
  "use strict";

  if (window.__djcHljsLoaded) {
    // Already loaded — just highlight any new blocks
    if (window.hljs) {
      document.querySelectorAll('pre code[class^="language-"]').forEach(function (el) {
        if (!el.dataset.highlighted) {
          window.hljs.highlightElement(el);
          el.dataset.highlighted = "true";
        }
      });
    }
    return;
  }

  window.__djcHljsLoaded = true;

  // Determine theme from the first code-block on the page
  var firstBlock = document.querySelector('.code-block[data-highlight]');
  var theme = (firstBlock && firstBlock.dataset.highlight) || "github-dark";

  // Insert theme CSS
  var link = document.createElement("link");
  link.rel = "stylesheet";
  link.href =
    "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/styles/" +
    theme +
    ".min.css";
  document.head.appendChild(link);

  // Insert highlight.js core
  var script = document.createElement("script");
  script.src =
    "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/highlight.min.js";
  script.onload = function () {
    document.querySelectorAll('pre code[class^="language-"]').forEach(function (el) {
      if (!el.dataset.highlighted) {
        window.hljs.highlightElement(el);
        el.dataset.highlighted = "true";
      }
    });
  };
  document.head.appendChild(script);
})();
