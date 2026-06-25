document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("dashToggle");
  const sidebar = document.getElementById("dashSidebar");

  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close sidebar when clicking outside on mobile
    sidebar.addEventListener("click", (e) => {
      if (e.target === sidebar) {
        sidebar.classList.remove("open");
      }
    });

    // Close sidebar after selecting a nav item
    sidebar.querySelectorAll(".dash-nav-item").forEach((item) => {
      item.addEventListener("click", () => {
        if (window.innerWidth < 768) {
          sidebar.classList.remove("open");
        }
      });
    });
  }
});
