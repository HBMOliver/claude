// Invoice Bot admin panel: confirmations and "select all". Everything works without it.
document.addEventListener('click', function (e) {
  var t = e.target.closest('[data-confirm]');
  if (t && !window.confirm(t.getAttribute('data-confirm'))) e.preventDefault();
});
document.addEventListener('change', function (e) {
  if (e.target.matches('[data-select-all]')) {
    document.querySelectorAll('input[name=ids]').forEach(function (c) { c.checked = e.target.checked; });
  }
});
