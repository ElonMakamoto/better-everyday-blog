(function () {
  var toggle = document.getElementById("theme-toggle");
  if (!toggle) return;
  function updateButton() {
    var isDark = document.documentElement.getAttribute("data-theme") === "dark";
    toggle.setAttribute("aria-pressed", String(isDark));
    toggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    var icon = toggle.querySelector(".theme-icon");
    var label = toggle.querySelector(".theme-label");
    if (icon) icon.textContent = isDark ? "☀" : "☾";
    if (label) label.textContent = isDark ? "Light" : "Dark";
  }
  toggle.addEventListener("click", function () {
    var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    document.documentElement.style.colorScheme = next;
    try { window.localStorage.setItem("better-everyday-theme", next); } catch (err) {}
    updateButton();
  });
  updateButton();
})();
