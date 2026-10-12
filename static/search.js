(function () {
  var search = new URLSearchParams(window.location.search).get("q");
  if (!search) return;
  var field = document.querySelector(".header-search input[name='q']");
  if (field) field.value = search;
  var cards = Array.prototype.slice.call(document.querySelectorAll("#latest .card"));
  if (!cards.length) return;
  var target = search.trim().toLocaleLowerCase();
  var found = 0;
  cards.forEach(function (card) {
    var matches = card.textContent.toLocaleLowerCase().includes(target);
    card.hidden = !matches;
    if (matches) found++;
  });
  var status = document.getElementById("search-status");
  if (status) {
    status.hidden = false;
    status.textContent = found ? found + " article" + (found === 1 ? "" : "s") + " for “" + search + "”" : "No articles found for “" + search + "”. Try another search.";
  }
  var section = document.getElementById("latest");
  if (section && section.scrollIntoView) section.scrollIntoView({block:"start"});
})();
