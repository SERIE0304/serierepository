const STORAGE_KEY = 'shaanai-tasks';
const TIME_KEY = 'shaanai-timecards';
const STAFF_KEY = 'shaanai-staff';
const STATUSES = ['未着手', '進行中', '完了'];
const HOURLY_RATE = 1100;
const WEEKDAY = ['日','月','火','水','木','金','土'];

let currentMonth = new Date();
currentMonth.setDate(1);

// ── スタッフ管理 ─────────────────────────────
const DEFAULT_STAFF = [
  { name: '芹江匡晋', role: '代表取締役' },
  { name: '芹江恵',   role: '取締役' },
  { name: '小筆',     role: 'スタッフ' },
];

// ── 事業所 ───────────────────────────────────
const BUSINESSES = ['フィットネスジム', 'なんだパンダ', '旅館', 'レストランUra no kado'];

function populateBusinessSelects() {
  const selects = ['filterBusiness', 'timeBusinessFilter', 'taskBusiness', 'timeBusinessSelect'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const first = el.options[0];
    el.innerHTML = '';
    el.appendChild(first);
    BUSINESSES.forEach(b => {
      const opt = document.createElement('option');
      opt.value = b;
      opt.textContent = b;
      el.appendChild(opt);
    });
  });
}

function loadStaff() {
  try {
    const s = JSON.parse(localStorage.getItem(STAFF_KEY));
    return s && s.length > 0 ? s : DEFAULT_STAFF;
  } catch { return DEFAULT_STAFF; }
}
function saveStaff(list) { localStorage.setItem(STAFF_KEY, JSON.stringify(list)); }

function getStaffNames() { return loadStaff().map(s => s.name); }

function populateStaffSelects() {
  const staff = loadStaff();
  const selects = ['filterAssignee', 'timeStaffFilter', 'taskAssignee', 'timeStaffSelect'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const first = el.options[0];
    el.innerHTML = '';
    el.appendChild(first);
    staff.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.name;
      opt.textContent = `${s.name}（${s.role}）`;
      el.appendChild(opt);
    });
  });
}

function renderStaffPage() {
  const staff = loadStaff();
  const el = document.getElementById('staffListEl');
  el.innerHTML = '';
  staff.forEach((s, i) => {
    const row = document.createElement('div');
    row.className = 'staff-item';
    row.innerHTML = `
      <div>
        <span class="staff-item-name">▶ ${escapeHtml(s.name)}</span>
        <span class="staff-item-role">（${escapeHtml(s.role)}）</span>
      </div>
      ${i >= DEFAULT_STAFF.length
        ? `<button class="btn-danger" onclick="removeStaff(${i})">削除</button>`
        : '<span style="color:#4444aa;font-size:0.7rem;">固定</span>'}
    `;
    el.appendChild(row);
  });
}

function addStaff() {
  const name = document.getElementById('newStaffName').value.trim();
  const role = document.getElementById('newStaffRole').value.trim() || 'スタッフ';
  if (!name) { alert('名前を入力してください'); return; }
  const staff = loadStaff();
  if (staff.find(s => s.name === name)) { alert('同じ名前のスタッフが既にいます'); return; }
  staff.push({ name, role });
  saveStaff(staff);
  document.getElementById('newStaffName').value = '';
  document.getElementById('newStaffRole').value = '';
  populateStaffSelects();
  renderStaffPage();
}

function removeStaff(idx) {
  if (!confirm('このスタッフを削除しますか？')) return;
  const staff = loadStaff();
  staff.splice(idx, 1);
  saveStaff(staff);
  populateStaffSelects();
  renderStaffPage();
}

// ── ユーティリティ ───────────────────────────
function generateId() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }
function escapeHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function isOverdue(d) { return d ? new Date(d) < new Date(new Date().toDateString()) : false; }
function formatDate(d) {
  if (!d) return '';
  const dt = new Date(d);
  return `${dt.getMonth()+1}/${dt.getDate()}`;
}

// ── タスク ───────────────────────────────────
function loadTasks() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; } }
function saveTasks(t) { localStorage.setItem(STORAGE_KEY, JSON.stringify(t)); }

function renderBoard() {
  const tasks = loadTasks();
  const filter = document.getElementById('filterAssignee').value;
  const bizFilter = document.getElementById('filterBusiness').value;
  STATUSES.forEach(status => {
    const list = document.getElementById(`list-${status}`);
    const countEl = document.getElementById(`count-${status}`);
    const filtered = tasks.filter(t => t.status === status && (!filter || t.assignee === filter) && (!bizFilter || t.business === bizFilter));
    countEl.textContent = filtered.length;
    list.innerHTML = '';
    filtered.forEach(t => list.appendChild(createCard(t)));
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
      ${task.business ? `<span class="tag tag-business">${escapeHtml(task.business)}</span>` : ''}
      <span class="tag tag-priority-${task.priority}">${task.priority}</span>
      ${task.dueDate ? `<span class="tag tag-due${overdue?' overdue':''}">${overdue?'⚠ ':''}${formatDate(task.dueDate)}</span>` : ''}
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
  document.getElementById('taskId').value = task?.id || '';
  document.getElementById('taskTitle').value = task?.title || '';
  document.getElementById('taskAssignee').value = task?.assignee || '';
  document.getElementById('taskBusiness').value = task?.business || '';
  document.getElementById('taskPriority').value = task?.priority || '中';
  document.getElementById('taskDueDate').value = task?.dueDate || '';
  document.getElementById('taskStatus').value = task?.status || '未着手';
  document.getElementById('taskMemo').value = task?.memo || '';
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
  const data = {
    id: id || generateId(),
    title: document.getElementById('taskTitle').value.trim(),
    assignee: document.getElementById('taskAssignee').value,
    business: document.getElementById('taskBusiness').value,
    priority: document.getElementById('taskPriority').value,
    dueDate: document.getElementById('taskDueDate').value,
    status: document.getElementById('taskStatus').value,
    memo: document.getElementById('taskMemo').value.trim(),
    createdAt: id ? (tasks.find(t => t.id === id)?.createdAt || new Date().toISOString()) : new Date().toISOString(),
  };
  if (id) { const i = tasks.findIndex(t => t.id === id); if (i !== -1) tasks[i] = data; }
  else tasks.push(data);
  saveTasks(tasks); closeModal(); renderBoard();
});

document.getElementById('filterAssignee').addEventListener('change', renderBoard);
document.getElementById('filterBusiness').addEventListener('change', renderBoard);

// ── タブ切り替え ─────────────────────────────
function switchTab(tab) {
  ['task','time','staff'].forEach(t => {
    document.getElementById(`page-${t}`).style.display = t === tab ? '' : 'none';
    document.getElementById(`tab-${t}`).classList.toggle('active', t === tab);
  });
  document.getElementById('openModalBtn').style.display = tab === 'task' ? '' : 'none';
  if (tab === 'time') renderTimeCard();
  if (tab === 'staff') renderStaffPage();
}

// ── タイムカード ─────────────────────────────
function loadTimecards() { try { return JSON.parse(localStorage.getItem(TIME_KEY)) || []; } catch { return []; } }
function saveTimecards(tc) { localStorage.setItem(TIME_KEY, JSON.stringify(tc)); }

function changeMonth(dir) {
  currentMonth.setMonth(currentMonth.getMonth() + dir);
  renderTimeCard();
}

function renderTimeCard() {
  const y = currentMonth.getFullYear();
  const m = currentMonth.getMonth();
  const staff = document.getElementById('timeStaffFilter').value;
  const biz = document.getElementById('timeBusinessFilter').value;
  document.getElementById('monthLabel').textContent = `${y}年${m+1}月`;

  const all = loadTimecards().filter(tc => {
    const d = new Date(tc.date);
    return d.getFullYear() === y && d.getMonth() === m && (!staff || tc.staff === staff) && (!biz || tc.business === biz);
  });

  // 月合計
  const totalBar = document.getElementById('timeTotalBar');
  const totalH = all.reduce((s, tc) => s + tc.hours, 0);
  totalBar.innerHTML = `<div class="total-bar-inner">
    <span class="total-label">${escapeHtml(staff || '全スタッフ')} ${y}年${m+1}月</span>
    <span class="total-hours">${totalH}時間</span>
    <span class="total-pay">¥${(totalH * HOURLY_RATE).toLocaleString()}</span>
  </div>`;

  // 日付カレンダー
  const cal = document.getElementById('timeCalendar');
  cal.innerHTML = '';
  const daysInMonth = new Date(y, m+1, 0).getDate();
  const today = new Date().toISOString().slice(0, 10);

  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    const dow = new Date(dateStr).getDay();
    const recs = all.filter(tc => tc.date === dateStr);
    const isToday = dateStr === today;

    const row = document.createElement('div');
    row.className = `cal-row${isToday?' today':''}${recs.length>0?' has-record':''}`;

    let recHtml = recs.map(tc => `
      <div class="cal-rec">
        ${!staff ? `<span class="tag tag-assignee">${escapeHtml(tc.staff)}</span>` : ''}
        ${tc.business ? `<span class="tag tag-business">${escapeHtml(tc.business)}</span>` : ''}
        <span class="cal-hours">${tc.hours}h</span>
        <span class="cal-pay">¥${(tc.hours*HOURLY_RATE).toLocaleString()}</span>
        <span class="${tc.lock==='yes'?'lock-yes':'lock-no'}">${tc.lock==='yes'?'🔑✓':'🔑✗'}</span>
        ${tc.memo?`<span class="cal-memo">${escapeHtml(tc.memo)}</span>`:''}
        <button class="btn-edit" onclick="openTimeModal('${tc.id}')">編集</button>
      </div>`).join('');

    row.innerHTML = `
      <div class="cal-date ${dow===0?'sun':dow===6?'sat':''}">
        <span class="cal-day">${d}</span>
        <span class="cal-week">${WEEKDAY[dow]}</span>
      </div>
      <div class="cal-content">${recHtml}</div>
      <button class="cal-add" onclick="openTimeModal(null,'${dateStr}')">＋</button>`;
    cal.appendChild(row);
  }
}

// 時間ボタン
function buildHourButtons(selected = null) {
  const c = document.getElementById('hourButtons');
  c.innerHTML = '';
  for (let h = 0.5; h <= 12; h += 0.5) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hour-btn' + (h === selected ? ' selected' : '');
    btn.textContent = `${h}h`;
    btn.onclick = () => selectHours(h);
    c.appendChild(btn);
  }
}

function selectHours(h) {
  document.getElementById('timeHours').value = h;
  document.getElementById('hourDisplay').textContent = `${h}時間 ＝ ¥${(h*HOURLY_RATE).toLocaleString()}`;
  document.querySelectorAll('.hour-btn').forEach(b => b.classList.toggle('selected', parseFloat(b.textContent) === h));
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
  const staffFilter = document.getElementById('timeStaffFilter').value;

  document.getElementById('timeModalTitle').textContent = record ? '勤務記録 編集' : '勤務記録 追加';
  document.getElementById('timeId').value = record?.id || '';

  const date = record?.date || dateStr || new Date().toISOString().slice(0,10);
  document.getElementById('timeDate').value = date;

  const staffName = record?.staff || staffFilter || '';
  document.getElementById('timeStaff').value = staffName;
  document.getElementById('timeStaffSelect').value = staffName;

  const bizFilter = document.getElementById('timeBusinessFilter').value;
  document.getElementById('timeBusinessSelect').value = record?.business || bizFilter || '';

  const d = new Date(date);
  document.getElementById('timeInfo').textContent =
    `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日（${WEEKDAY[d.getDay()]}）`;

  document.getElementById('timeMemo').value = record?.memo || '';
  document.getElementById('timeLock').value = record?.lock || '';
  document.getElementById('lockYes').className = 'lock-btn' + (record?.lock==='yes' ? ' selected-yes' : '');
  document.getElementById('lockNo').className = 'lock-btn' + (record?.lock==='no' ? ' selected-no' : '');
  document.getElementById('deleteTimeBtn').style.display = record ? 'inline-block' : 'none';

  buildHourButtons(record?.hours || null);
  if (record) {
    document.getElementById('timeHours').value = record.hours;
    document.getElementById('hourDisplay').textContent = `${record.hours}時間 ＝ ¥${(record.hours*HOURLY_RATE).toLocaleString()}`;
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
  const staff = document.getElementById('timeStaffSelect').value || document.getElementById('timeStaff').value;
  if (!staff) { alert('スタッフを選択してください'); return; }
  const business = document.getElementById('timeBusinessSelect').value;
  if (!business) { alert('事業所を選択してください'); return; }
  const id = document.getElementById('timeId').value;
  const tcs = loadTimecards();
  const data = { id: id || generateId(), date: document.getElementById('timeDate').value, staff, business, hours, lock, memo: document.getElementById('timeMemo').value.trim() };
  if (id) { const i = tcs.findIndex(tc => tc.id === id); if (i !== -1) tcs[i] = data; }
  else tcs.push(data);
  saveTimecards(tcs); closeTimeModal(); renderTimeCard();
});

// ── 初期化 ───────────────────────────────────
populateStaffSelects();
populateBusinessSelects();
renderBoard();
