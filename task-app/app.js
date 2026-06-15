const STORAGE_KEY = 'shaanai-tasks';
const STATUSES = ['未着手', '進行中', '完了'];

function loadTasks() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveTasks(tasks) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function isOverdue(dueDate) {
  if (!dueDate) return false;
  return new Date(dueDate) < new Date(new Date().toDateString());
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function renderBoard() {
  const tasks = loadTasks();
  const filterAssignee = document.getElementById('filterAssignee').value;

  STATUSES.forEach(status => {
    const list = document.getElementById(`list-${status}`);
    const countEl = document.getElementById(`count-${status}`);
    const filtered = tasks.filter(t =>
      t.status === status && (!filterAssignee || t.assignee === filterAssignee)
    );
    countEl.textContent = filtered.length;
    list.innerHTML = '';
    filtered.forEach(task => {
      list.appendChild(createCard(task));
    });
  });
}

function createCard(task) {
  const overdue = isOverdue(task.dueDate) && task.status !== '完了';
  const card = document.createElement('div');
  card.className = `task-card priority-${task.priority}${overdue ? ' overdue' : ''}`;
  card.innerHTML = `
    <div class="task-title">${escapeHtml(task.title)}</div>
    <div class="task-meta">
      ${task.assignee ? `<span class="tag tag-assignee">${escapeHtml(task.assignee)}</span>` : ''}
      <span class="tag tag-priority-${task.priority}">${task.priority}</span>
      ${task.dueDate ? `<span class="tag tag-due${overdue ? ' overdue' : ''}">${overdue ? '⚠ ' : ''}${formatDate(task.dueDate)}</span>` : ''}
    </div>
    ${task.memo ? `<div class="task-memo">${escapeHtml(task.memo)}</div>` : ''}
  `;
  card.addEventListener('click', () => openModal(task));
  return card;
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// モーダル
const overlay = document.getElementById('modalOverlay');
const form = document.getElementById('taskForm');

function openModal(task = null) {
  document.getElementById('modalTitle').textContent = task ? 'タスク編集' : 'タスク追加';
  document.getElementById('taskId').value = task ? task.id : '';
  document.getElementById('taskTitle').value = task ? task.title : '';
  document.getElementById('taskAssignee').value = task ? task.assignee : '';
  document.getElementById('taskPriority').value = task ? task.priority : '中';
  document.getElementById('taskDueDate').value = task ? task.dueDate : '';
  document.getElementById('taskStatus').value = task ? task.status : '未着手';
  document.getElementById('taskMemo').value = task ? task.memo : '';
  document.getElementById('deleteTaskBtn').style.display = task ? 'inline-block' : 'none';
  overlay.classList.add('active');
  document.getElementById('taskTitle').focus();
}

function closeModal() {
  overlay.classList.remove('active');
  form.reset();
}

document.getElementById('openModalBtn').addEventListener('click', () => openModal());
document.getElementById('closeModalBtn').addEventListener('click', closeModal);
document.getElementById('cancelBtn').addEventListener('click', closeModal);
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });

document.getElementById('deleteTaskBtn').addEventListener('click', () => {
  const id = document.getElementById('taskId').value;
  if (!id || !confirm('このタスクを削除しますか？')) return;
  const tasks = loadTasks().filter(t => t.id !== id);
  saveTasks(tasks);
  closeModal();
  renderBoard();
});

form.addEventListener('submit', e => {
  e.preventDefault();
  const id = document.getElementById('taskId').value;
  const tasks = loadTasks();
  const taskData = {
    id: id || generateId(),
    title: document.getElementById('taskTitle').value.trim(),
    assignee: document.getElementById('taskAssignee').value,
    priority: document.getElementById('taskPriority').value,
    dueDate: document.getElementById('taskDueDate').value,
    status: document.getElementById('taskStatus').value,
    memo: document.getElementById('taskMemo').value.trim(),
    createdAt: id ? (tasks.find(t => t.id === id)?.createdAt || new Date().toISOString()) : new Date().toISOString(),
  };

  if (id) {
    const idx = tasks.findIndex(t => t.id === id);
    if (idx !== -1) tasks[idx] = taskData;
  } else {
    tasks.push(taskData);
  }

  saveTasks(tasks);
  closeModal();
  renderBoard();
});

document.getElementById('filterAssignee').addEventListener('change', renderBoard);

// 初期表示
renderBoard();
