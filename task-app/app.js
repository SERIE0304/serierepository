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

const WEEKDAY = ['日','月','火','水','木','金','土'];

function renderTimeCard() {
  const y = currentMonth.getFullYear();
  const m = currentMonth.getMonth();
  const staff = document.getElementById('timeStaffFilter').value;

  document.getElementById('monthLabel').textContent = `${y}年${m + 1}月`;

  const all = loadTimecards().filter(tc => {
    const d = new Date(tc.date);
    return d.getFullYear() === y && d.getMonth() === m && (!staff || tc.staff === staff);
  });

  // 月合計バー
  const totalBar = document.getElementById('timeTotalBar');
  if (all.length > 0) {
    const totalH = all.reduce((s, tc) => s + tc.hours, 0);
    const totalPay = totalH * HOURLY_RATE;
    totalBar.innerHTML = `
      <div class="total-bar-inner">
        <span class="total-label">${staff || '全スタッフ'} 合計</span>
        <span class="total-hours">${totalH} 時間</span>
        <span class="total-pay">¥${totalPay.toLocaleString()}</span>
      </div>`;
  } else {
    totalBar.innerHTML = `<div class="total-bar-inner"><span class="total-label">記録なし</span></div>`;
  }

  // 日付カレンダー（その月の日数分）
  const cal = document.getElementById('timeCalendar');
  cal.innerHTML = '';
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const today = new Date().toISOString().slice(0, 10);

  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    const dayOfWeek = new Date(dateStr).getDay();
    const recs = all.filter(tc => tc.date === dateStr);
    const totalH = recs.reduce((s, tc) => s + tc.hours, 0);
    const isToday = dateStr === today;
    const isSun = dayOfWeek === 0;
    const isSat = dayOfWeek === 6;

    const row = document.createElement('div');
    row.className = 'cal-row' + (isToday ? ' today' : '') + (recs.length > 0 ? ' has-record' : '');

    let recHtml = '';
    if (recs.length > 0) {
      recs.forEach(tc => {
        const lockIcon = tc.lock === 'yes' ? '🔑✓' : '🔑✗';
        const lockClass = tc.lock === 'yes' ? 'lock-yes' : 'lock-no';
        recHtml += `
          <div class="cal-rec">
            ${staff ? '' : `<span class="tag tag-assignee">${escapeHtml(tc.staff)}</span>`}
            <span class="cal-hours">${tc.hours}h</span>
            <span class="cal-pay">¥${(tc.hours * HOURLY_RATE).toLocaleString()}</span>
            <span class="${lockClass}">${lockIcon}</span>
            ${tc.memo ? `<span class="cal-memo">${escapeHtml(tc.memo)}</span>` : ''}
            <button class="btn-edit" onclick="openTimeModal('${tc.id}')">編集</button>
          </div>`;
      });
    }

    row.innerHTML = `
      <div class="cal-date ${isSun ? 'sun' : isSat ? 'sat' : ''}">
        <span class="cal-day">${d}</span>
        <span class="cal-week">${WEEKDAY[dayOfWeek]}</span>
      </div>
      <div class="cal-content">${recHtml}</div>
      <button class="cal-add" onclick="openTimeModal(null,'${dateStr}')">＋</button>
    `;
    cal.appendChild(row);
  }
}

// 時間ボタン生成
function buildHourButtons(selected = null) {
  const container = document.getElementById('hourButtons');
  container.innerHTML = '';
  for (let h = 0.5; h <= 12; h += 0.5) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hour-btn' + (h === selected ? ' selected' : '');
    btn.textContent = `${h}h`;
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

function selectLock(val) {
  document.getElementById('timeLock').value = val ? 'yes' : 'no';
  document.getElementById('lockYes').className = 'lock-btn' + (val ? ' selected-yes' : '');
  document.getElementById('lockNo').className = 'lock-btn' + (!val ? ' selected-no' : '');
}

// タイムカードモーダル
const timeOverlay = document.getElementById('timeModalOverlay');
const timeForm = document.getElementById('timeForm');

function openTimeModal(idOrNull, dateStr) {
  const tcs = loadTimecards();
  const record = idOrNull ? tcs.find(tc => tc.id === idOrNull) : null;
  const staff = document.getElementById('timeStaffFilter').value;

  document.getElementById('timeModalTitle').textContent = record ? '勤務記録 編集' : '勤務記録 追加';
  document.getElementById('timeId').value = record ? record.id : '';

  const date = record ? record.date : (dateStr || new Date().toISOString().slice(0, 10));
  document.getElementById('timeDate').value = date;

  const d = new Date(date);
  const staffName = record ? record.staff : staff;
  document.getElementById('timeStaff').value = staffName;
  document.getElementById('timeInfo').textContent =
    `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日（${WEEKDAY[d.getDay()]}）　${staffName || ''}`;

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
  const lock = document.getElementById('timeLock').value;
  if (!lock) { alert('鍵の確認を選択してください'); return; }
  const staff = document.getElementById('timeStaff').value;
  if (!staff) { alert('スタッフを選択してください'); return; }
  const id = document.getElementById('timeId').value;
  const tcs = loadTimecards();
  const data = {
    id: id || generateId(),
    date: document.getElementById('timeDate').value,
    staff,
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
