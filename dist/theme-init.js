(function () {
  try {
    var stored = window.localStorage.getItem("better-everyday-theme");
    var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    var initial = stored === "light" || stored === "dark" ? stored : (prefersDark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", initial);
    document.documentElement.style.colorScheme = initial;
  } catch (err) {
    document.documentElement.setAttribute("data-theme", "light");
  }
})();
