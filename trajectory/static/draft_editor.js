const form = document.querySelector('[data-draft-editor]');
const container = form.querySelector('[data-milestones]');
const status = form.querySelector('[data-editor-status]');
let dirty = Boolean(form.querySelector('[role="alert"]'));

function renameFields(node, prefix, selector) {
  node.querySelectorAll(selector).forEach((input) => {
    const name = prefix + input.dataset.key;
    input.name = name;
    input.id = name;
    input.closest('.field').querySelector('label').htmlFor = name;
  });
}

function refresh() {
  const milestones = [...container.children];
  form.elements.milestone_count.value = milestones.length;
  milestones.forEach((milestone, mi) => {
    milestone.querySelector('legend [data-number]').textContent = mi + 1;
    renameFields(milestone, `m${mi}_`, ':scope > .field [data-key]');
    const tasks = [...milestone.querySelector('[data-tasks]').children];
    const count = milestone.querySelector('[data-task-count]');
    count.name = `m${mi}_task_count`;
    count.value = tasks.length;
    tasks.forEach((task, ti) => {
      task.querySelector('[data-number]').textContent = ti + 1;
      renameFields(task, `m${mi}_t${ti}_`, '[data-key]');
      task.querySelector('[data-action="up-task"]').disabled = ti === 0;
      task.querySelector('[data-action="down-task"]').disabled = ti === tasks.length - 1;
      task.querySelector('[data-action="remove-task"]').disabled = tasks.length <= 1;
    });
    milestone.querySelector('[data-action="add-task"]').disabled = tasks.length >= 5;
    milestone.querySelector('[data-action="up-milestone"]').disabled = mi === 0;
    milestone.querySelector('[data-action="down-milestone"]').disabled = mi === milestones.length - 1;
    milestone.querySelector('[data-action="remove-milestone"]').disabled = milestones.length <= 1;
  });
  form.querySelector('[data-action="add-milestone"]').disabled = milestones.length >= 4;
}

form.addEventListener('input', () => { dirty = true; });
form.addEventListener('click', (event) => {
  const button = event.target.closest('[data-action]');
  if (!button) return;
  const [operation, kind] = button.dataset.action.split('-');
  const parent = kind === 'task' ? button.closest('[data-milestone]').querySelector('[data-tasks]') : container;
  const node = button.closest(kind === 'task' ? '[data-task]' : '[data-milestone]');
  if (operation === 'add') {
    const copy = document.querySelector(`#${kind}-template`).content.cloneNode(true);
    parent.append(copy);
    parent.lastElementChild.querySelector('input:not([type="hidden"])').focus();
  } else if (operation === 'remove') {
    if (parent.children.length <= 1) return;
    const next = node.nextElementSibling || node.previousElementSibling;
    node.remove();
    next.querySelector('input:not([type="hidden"])').focus();
  } else if (operation === 'up' && node.previousElementSibling) {
    parent.insertBefore(node, node.previousElementSibling);
  } else if (operation === 'down' && node.nextElementSibling) {
    parent.insertBefore(node.nextElementSibling, node);
  }
  dirty = true;
  refresh();
  if (operation === 'up' || operation === 'down') {
    node.querySelector('input:not([type="hidden"])').focus();
  }
  status.textContent = 'Draft changed. Save it before reviewing for approval.';
});
form.addEventListener('submit', () => {
  refresh();
  dirty = false;
  form.querySelector('button[type="submit"]').disabled = true;
  status.textContent = 'Saving draft...';
});
window.addEventListener('beforeunload', (event) => {
  if (dirty) { event.preventDefault(); event.returnValue = ''; }
});
window.addEventListener('pageshow', () => {
  form.querySelector('button[type="submit"]').disabled = false;
  refresh();
});
refresh();
