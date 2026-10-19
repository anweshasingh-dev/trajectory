const form = document.querySelector('[data-generation-form]');
if (form) {
  form.addEventListener('submit', () => {
    form.querySelector('button').disabled = true;
    form.querySelector('[data-generation-status]').textContent = 'Generating proposal... Your saved goal remains available.';
  });
  window.addEventListener('pageshow', () => {
    form.querySelector('button').disabled = false;
    form.querySelector('[data-generation-status]').textContent = 'Uses a local model. Generation may take up to two minutes.';
  });
}
