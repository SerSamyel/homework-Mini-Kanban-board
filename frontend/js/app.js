/**
 * Board rendering, task CRUD forms and drag-and-drop wiring.
 * Talks to the data layer only through window.kanbanApi (see api.js) —
 * replacing that file with a real fetch-based client is the only change
 * needed to point this UI at the FastAPI backend.
 */
(function () {
  const boardEl = document.getElementById('board');
  const columnTemplate = document.getElementById('column-template');
  const cardTemplate = document.getElementById('task-card-template');

  const modal = document.getElementById('task-modal');
  const form = document.getElementById('task-form');
  const titleInput = document.getElementById('task-title');
  const descriptionInput = document.getElementById('task-description');
  const modalTitle = document.getElementById('modal-title');
  const deleteBtn = document.getElementById('task-delete');
  const cancelBtn = document.getElementById('task-cancel');

  /** Editing state: null (creating) or the task being edited. */
  let editingTask = null;
  let activeColumnId = null;

  function renderBoard(board) {
    boardEl.innerHTML = '';
    board.columns
      .slice()
      .sort((a, b) => a.order - b.order)
      .forEach((column) => boardEl.appendChild(renderColumn(column)));
    wireSortable();
  }

  function renderColumn(column) {
    const node = columnTemplate.content.cloneNode(true);
    const section = node.querySelector('.column');
    const list = node.querySelector('.task-list');

    section.dataset.columnId = column.id;
    list.dataset.columnId = column.id;
    node.querySelector('.column__title').textContent = column.name;
    node.querySelector('.column__count').textContent = column.tasks.length;
    node.querySelector('[data-action="add-task"]').addEventListener('click', () => openCreateModal(column.id));

    column.tasks.forEach((task) => list.appendChild(renderCard(task)));

    return node;
  }

  function renderCard(task) {
    const node = cardTemplate.content.cloneNode(true);
    const card = node.querySelector('.task-card');
    card.dataset.taskId = task.id;
    node.querySelector('.task-card__title').textContent = task.title;
    node.querySelector('.task-card__description').textContent = task.description || '';
    card.addEventListener('click', () => openEditModal(task));
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') openEditModal(task);
    });
    return node;
  }

  function wireSortable() {
    document.querySelectorAll('.task-list').forEach((list) => {
      Sortable.create(list, {
        group: 'kanban',
        animation: 150,
        onEnd: handleDrop,
      });
    });
  }

  function handleDrop(evt) {
    const taskId = evt.item.dataset.taskId;
    const newColumnId = Number(evt.to.dataset.columnId);
    const newPosition = evt.newIndex;

    kanbanApi
      .updateTask(taskId, { column_id: newColumnId, position: newPosition })
      .then(() => reindexColumn(evt.to))
      .then(() => {
        if (evt.from !== evt.to) return reindexColumn(evt.from);
      })
      .catch((err) => {
        console.error('Failed to persist move, reloading board', err);
        loadBoard();
      });
  }

  /** After a drop, persist the sibling order of a column from current DOM order. */
  function reindexColumn(listEl) {
    const columnId = Number(listEl.dataset.columnId);
    const ids = Array.from(listEl.querySelectorAll('.task-card')).map((el) => el.dataset.taskId);
    return Promise.all(
      ids.map((id, index) => kanbanApi.updateTask(id, { column_id: columnId, position: index }))
    );
  }

  function openCreateModal(columnId) {
    editingTask = null;
    activeColumnId = columnId;
    modalTitle.textContent = 'Новая задача';
    deleteBtn.hidden = true;
    form.reset();
    showModal();
  }

  function openEditModal(task) {
    editingTask = task;
    activeColumnId = task.column_id;
    modalTitle.textContent = 'Редактировать задачу';
    deleteBtn.hidden = false;
    titleInput.value = task.title;
    descriptionInput.value = task.description || '';
    showModal();
  }

  function showModal() {
    modal.hidden = false;
    titleInput.focus();
  }

  function hideModal() {
    modal.hidden = true;
    editingTask = null;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    if (!title) return;

    const request = editingTask
      ? kanbanApi.updateTask(editingTask.id, { title, description })
      : kanbanApi.createTask({ title, description, column_id: activeColumnId });

    request.then(() => {
      hideModal();
      loadBoard();
    });
  });

  deleteBtn.addEventListener('click', () => {
    if (!editingTask) return;
    kanbanApi.deleteTask(editingTask.id).then(() => {
      hideModal();
      loadBoard();
    });
  });

  cancelBtn.addEventListener('click', hideModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) hideModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) hideModal();
  });

  function loadBoard() {
    return kanbanApi.getBoard().then(renderBoard);
  }

  loadBoard();
})();
