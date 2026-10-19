const form = document.querySelector('[data-goal-form]');
let dirty = false;
form.addEventListener('input', () => { dirty = true; });
form.addEventListener('submit', () => {
  dirty = false;
  form.querySelector('button[type="submit"]').disabled = true;
  form.querySelector('[data-save-status]').textContent = 'Saving...';
});
window.addEventListener('beforeunload', (event) => {
  if (dirty) { event.preventDefault(); event.returnValue = ''; }
});
window.addEventListener('pageshow', () => {
  form.querySelector('button[type="submit"]').disabled = false;
  form.querySelector('[data-save-status]').textContent = '';
});
