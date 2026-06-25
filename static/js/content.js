document.addEventListener("click", (e) => {
  // ── Collapse button ──────────────────────────────
  const collapseBtn = e.target.closest(".thread-collapse-btn");
  if (collapseBtn) {
    const thread = collapseBtn.closest(".thread");
    const children = thread.querySelector(".thread-children");
    const preview = children ? children.querySelector(".thread-collapsed-preview") : null;
    const collapsed = thread.classList.toggle("collapsed");

    // Swap icon
    const icon = collapseBtn.querySelector("i");
    if (collapsed) {
      icon.className = "bi bi-plus-circle";
    } else {
      icon.className = "bi bi-dash-circle";
    }

    if (collapsed) {
      // Count visible child threads
      const childThreads = children ? children.querySelectorAll(":scope > .thread:not(.collapsed)") : [];
      const count = childThreads.length;
      if (count > 0 && preview) {
        const countEl = preview.querySelector(".thread-collapsed-count");
        if (countEl) countEl.textContent = count + " " + (count === 1 ? "reply" : "replies");
        preview.style.display = "";
      }
    } else {
      if (preview) preview.style.display = "none";
    }
    return;
  }

  // ── Expand button ────────────────────────────────
  const expandBtn = e.target.closest(".thread-expand-btn");
  if (expandBtn) {
    const thread = expandBtn.closest(".thread");
    thread.classList.remove("collapsed");
    const preview = expandBtn.closest(".thread-collapsed-preview");
    if (preview) preview.style.display = "none";
    return;
  }
});

// Auto-expand comment textarea
const commentInputs = document.querySelectorAll(".comment-input-row textarea");
commentInputs.forEach((input) => {
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 150) + "px";
  });
});
