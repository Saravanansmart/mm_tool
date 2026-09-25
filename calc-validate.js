// Shared numeric-input guard for calculator pages.
// Enforces each input's own declared min/max so out-of-range values cannot reach
// the maths and render NaN, Infinity or negative currency.
(function (global) {
  'use strict';

  function labelFor(el) {
    var lab = document.querySelector('label[for="' + el.id + '"]');
    return (lab ? lab.textContent : el.id).replace(/\s*\(.*$/, '').replace(/[:*]\s*$/, '').trim();
  }

  function show(box, messages) {
    if (!box) return;
    box.textContent = '';
    messages.forEach(function (msg, idx) {
      if (idx > 0) box.appendChild(document.createElement('br'));
      box.appendChild(document.createTextNode(msg));
    });
    box.style.display = messages.length ? 'block' : 'none';
  }

  // ids: array of input ids to check. errorId: id of the inline error container.
  // Returns true when every value is present, numeric and within its declared bounds.
  global.validateNumericBounds = function (ids, errorId, resultsId) {
    var errors = [];
    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (!el || el.disabled || el.type === 'select-one' || el.type === 'checkbox') return;
      var raw = String(el.value).trim();
      var name = labelFor(el);
      if (raw === '') { errors.push(name + ' is required.'); return; }
      var v = Number(raw);
      if (!isFinite(v)) { errors.push(name + ' must be a number.'); return; }
      if (el.min !== '' && v < Number(el.min)) {
        errors.push(name + ' must be at least ' + Number(el.min).toLocaleString('en-IN') + '.');
      }
      if (el.max !== '' && v > Number(el.max)) {
        errors.push(name + ' cannot exceed ' + Number(el.max).toLocaleString('en-IN') + '.');
      }
    });
    show(document.getElementById(errorId), errors);
    if (errors.length && resultsId) {
      var card = document.getElementById(resultsId);
      if (card) card.classList.add('hidden');
    }
    return errors.length === 0;
  };
})(window);
