document.querySelectorAll(".switch-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const searchInput = document.querySelector(".search-input");

        // Update HTMX route
        searchInput.setAttribute("hx-get", btn.dataset.target);
        htmx.process(searchInput);

        // Update placeholder
        if (btn.dataset.placeholder) {
            searchInput.placeholder = btn.dataset.placeholder;
        }

        // Swap primary/ghost classes between buttons
        document.querySelectorAll(".switch-btn").forEach(b => {
            b.classList.remove("btn-primary", "btn-ghost");
            b.classList.add(b === btn ? "btn-primary" : "btn-ghost");
        });

        // Re-search immediately if there's a query
        const q = searchInput.value.trim();
        if (q) {
            htmx.trigger(searchInput, "keyup");
        }
        searchInput.focus();
    });
});
