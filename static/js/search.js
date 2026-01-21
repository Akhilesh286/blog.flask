let currentRoute = "/search-people";  // default route

document.querySelectorAll(".switch-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        
        // Update current route
        currentRoute = btn.dataset.target;
        
        // Make HTMX input use the new routeconst 
        searchInput = document.getElementById("search");
        searchInput.setAttribute("hx-get", currentRoute);
        searchInput.focus()
        
        // rescan
        htmx.process(searchInput);
        
        // Update active button styles
        document.querySelectorAll(".switch-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
     });
});
