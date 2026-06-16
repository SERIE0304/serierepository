const STORAGE_KEY = 'shaanai-tasks';
const TIME_KEY = 'shaanai-timecards';
const STATUSES = ['未着手', '進行中', '完了'];
const HOURLY_RATE = 1100;
const STAFF_LIST = ['代表取締役', '取締役', '社員', 'スタッフA', 'スタッフB'];

let currentMonth = new Date();
currentMonth.setDate(1);

// ── ユーティリティ ──────────────────────────
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function escapeHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
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

// ── タスク ──────────────────────────────────
function loadTasks() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; }
}
function saveTasks(tasks) { localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks)); }

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
    filtered.forEach(task => list.appendChild(createCard(task)));
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

// タスクモーダル
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

function closeModal() { overlay.classList.remove('active'); form.reset(); }

document.getElementById('openModalBtn').addEventListener('click', () => openModal());
document.getElementById('closeModalBtn').addEventListener('click', closeModal);
document.getElementById('cancelBtn').addEventListener('click', closeModal);
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });

document.getElementById('deleteTaskBtn').addEventListener('click', () => {
  const id = document.getElementById('taskId').value;
  if (!id || !confirm('このタスクを削除しますか？')) return;
  saveTasks(loadTasks().filter(t => t.id !== id));
  closeModal(); renderBoard();
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
  if (id) { const i = tasks.findIndex(t => t.id === id); if (i !== -1) tasks[i] = taskData; }
  else tasks.push(taskData);
  saveTasks(tasks); closeModal(); renderBoard();
});

document.getElementById('filterAssignee').addEventListener('change', renderBoard);

// ── タブ切り替え ────────────────────────────
function switchTab(tab) {
  document.getElementById('page-task').style.display = tab === 'task' ? '' : 'none';
  document.getElementById('page-time').style.display = tab === 'time' ? '' : 'none';
  document.getElementById('tab-task').classList.toggle('active', tab === 'task');
  document.getElementById('tab-time').classList.toggle('active', tab === 'time');
  document.getElementById('openModalBtn').style.display = tab === 'task' ? '' : 'none';
  if (tab === 'time') renderTimeCard();
}

// ── タイムカード ────────────────────────────
function loadTimecards() {
  try { return JSON.parse(localStorage.getItem(TIME_KEY)) || []; } catch { return []; }
}
function saveTimecards(tc) { localStorage.setItem(TIME_KEY, JSON.stringify(tc)); }

function changeMonth(dir) {
  currentMonth.setMonth(currentMonth.getMonth() + dir);
  renderTimeCard();
}

function renderTimeCard() {
  const y = currentMonth.getFullYear();
  const m = currentMonth.getMonth();
  document.getElementById('monthLabel').textContent =
    `${y}年${m + 1}月`;

  const all = loadTimecards().filter(tc => {
    const d = new Date(tc.date);
    return d.getFullYear() === y && d.getMonth() === m;
  });

  // スタッフ別集計
  const summaryEl = document.getElementById('timeSummary');
  summaryEl.innerHTML = '';
  STAFF_LIST.forEach(staff => {
    const records = all.filter(tc => tc.staff === staff);
    if (records.length === 0) return;
    const totalHours = records.reduce((s, tc) => s + tc.hours, 0);
    const totalPay = totalHours * HOURLY_RATE;
    const card = document.createElement('div');
    card.className = 'summary-card';
    card.innerHTML = `
      <div class="summary-name">${escapeHtml(staff)}</div>
      <div class="summary-hours">${totalHours}時間</div>
      <div class="summary-pay">¥${totalPay.toLocaleString()}</div>
    `;
    summaryEl.appendChild(card);
  });

  if (all.length === 0) {
    summaryEl.innerHTML = '<div class="no-records">▶ この月の記録はありません</div>';
  }

  // 履歴一覧（日付降順）
  const listEl = document.getElementById('timeList');
  listEl.innerHTML = '';
  const sorted = [...all].sort((a, b) => b.date.localeCompare(a.date));
  sorted.forEach(tc => {
    const row = document.createElement('div');
    row.className = 'time-row';
    const lockMark = tc.lock === 'yes'
      ? '<span class="time-row-lock lock-yes">🔑✓</span>'
      : '<span class="time-row-lock lock-no">🔑✗</span>';
    row.innerHTML = `
      <span class="time-row-date">${formatDate(tc.date)}</span>
      <span class="time-row-staff tag tag-assignee">${escapeHtml(tc.staff)}</span>
      <span class="time-row-hours">${tc.hours}h</span>
      <span class="time-row-pay">¥${(tc.hours * HOURLY_RATE).toLocaleString()}</span>
      ${lockMark}
      ${tc.memo ? `<span class="time-row-memo">${escapeHtml(tc.memo)}</span>` : '<span></span>'}
      <button class="btn-edit" onclick="editTimeRecord('${tc.id}')">編集</button>
    `;
    listEl.appendChild(row);
  });
}

// 時間ボタン生成（0.5刻み、0.5〜12）
function buildHourButtons(selected = null) {
  const container = document.getElementById('hourButtons');
  container.innerHTML = '';
  for (let h = 0.5; h <= 12; h += 0.5) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hour-btn' + (h === selected ? ' selected' : '');
    btn.textContent = h % 1 === 0 ? `${h}h` : `${h}h`;
    btn.onclick = () => selectHours(h);
    container.appendChild(btn);
  }
}

function selectHours(h) {
  document.getElementById('timeHours').value = h;
  document.getElementById('hourDisplay').textContent =
    `${h}時間 ＝ ¥${(h * HOURLY_RATE).toLocaleString()}`;
  document.querySelectorAll('.hour-btn').forEach(b => {
    b.classList.toggle('selected', parseFloat(b.textContent) === h);
  });
}

// 鍵選択
function selectLock(val) {
  document.getElementById('timeLock').value = val ? 'yes' : 'no';
  document.getElementById('lockYes').className = 'lock-btn' + (val ? ' selected-yes' : '');
  document.getElementById('lockNo').className = 'lock-btn' + (!val ? ' selected-no' : '');
}

// タイムカードモーダル
const timeOverlay = document.getElementById('timeModalOverlay');
const timeForm = document.getElementById('timeForm');

function openTimeModal(record = null) {
  document.getElementById('timeModalTitle').textContent = record ? '勤務記録 編集' : '勤務記録 追加';
  document.getElementById('timeId').value = record ? record.id : '';
  document.getElementById('timeDate').value = record ? record.date : new Date().toISOString().slice(0, 10);
  document.getElementById('timeStaff').value = record ? record.staff : '';
  document.getElementById('timeMemo').value = record ? record.memo : '';
  document.getElementById('timeLock').value = record ? (record.lock || '') : '';
  document.getElementById('lockYes').className = 'lock-btn' + (record?.lock === 'yes' ? ' selected-yes' : '');
  document.getElementById('lockNo').className = 'lock-btn' + (record?.lock === 'no' ? ' selected-no' : '');
  document.getElementById('deleteTimeBtn').style.display = record ? 'inline-block' : 'none';
  buildHourButtons(record ? record.hours : null);
  if (record) {
    document.getElementById('timeHours').value = record.hours;
    document.getElementById('hourDisplay').textContent =
      `${record.hours}時間 ＝ ¥${(record.hours * HOURLY_RATE).toLocaleString()}`;
  } else {
    document.getElementById('timeHours').value = '';
    document.getElementById('hourDisplay').textContent = '未選択';
  }
  timeOverlay.classList.add('active');
}

function closeTimeModal() { timeOverlay.classList.remove('active'); timeForm.reset(); }

function editTimeRecord(id) {
  const record = loadTimecards().find(tc => tc.id === id);
  if (record) openTimeModal(record);
}

timeOverlay.addEventListener('click', e => { if (e.target === timeOverlay) closeTimeModal(); });

document.getElementById('deleteTimeBtn').addEventListener('click', () => {
  const id = document.getElementById('timeId').value;
  if (!id || !confirm('この記録を削除しますか？')) return;
  saveTimecards(loadTimecards().filter(tc => tc.id !== id));
  closeTimeModal(); renderTimeCard();
});

timeForm.addEventListener('submit', e => {
  e.preventDefault();
  const hours = parseFloat(document.getElementById('timeHours').value);
  if (!hours) { alert('勤務時間を選択してください'); return; }
  const id = document.getElementById('timeId').value;
  const tcs = loadTimecards();
  const lock = document.getElementById('timeLock').value;
  if (!lock) { alert('鍵の確認を選択してください'); return; }
  const data = {
    id: id || generateId(),
    date: document.getElementById('timeDate').value,
    staff: document.getElementById('timeStaff').value,
    hours,
    lock,
    memo: document.getElementById('timeMemo').value.trim(),
  };
  if (id) { const i = tcs.findIndex(tc => tc.id === id); if (i !== -1) tcs[i] = data; }
  else tcs.push(data);
  saveTimecards(tcs); closeTimeModal(); renderTimeCard();
});

// ── 初期表示 ────────────────────────────────
renderBoard();
