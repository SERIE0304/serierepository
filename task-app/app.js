const STORAGE_KEY = 'shaanai-tasks';
const STATUSES = ['未着手', '進行中', '完了'];
const HOURLY_RATE = 1100;
const WEEKDAY = ['日','月','火','水','木','金','土'];

let currentMonth = new Date();
currentMonth.setDate(1);

// ── 事業所 ───────────────────────────────────
const BUSINESSES = ['フィットネスジム', 'なんだパンダ', '旅館', 'レストランUra no kado'];

function populateBusinessSelects() {
  const selects = ['taskBusiness', 'timeBusinessSelect'];
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

// ── スタッフ管理（Firebase） ─────────────────
let staffCache = []; // [{uid, name, role}] from staffPublic, readable by all logged-in users
let fullStaffCache = []; // [{uid, name, role, email, password, isAdmin}] admin only

function getStaffNames() { return staffCache.map(s => s.name); }

function populateStaffSelects() {
  const list = currentProfile && currentProfile.isAdmin ? staffCache : staffCache.filter(s => s.uid === currentProfile?.uid);

  const withPlaceholder = ['filterAssignee', 'taskAssignee', 'timeStaffSelect'];
  withPlaceholder.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const first = el.options[0];
    el.innerHTML = '';
    el.appendChild(first);
    staffCache.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.name;
      opt.textContent = `${s.name}（${s.role}）`;
      el.appendChild(opt);
    });
  });

  const timeSelectEl = document.getElementById('timeStaffSelect');
  if (timeSelectEl && currentProfile && !currentProfile.isAdmin) {
    timeSelectEl.value = currentProfile.name;
    timeSelectEl.disabled = true;
    document.getElementById('timeStaff').value = currentProfile.uid;
  } else if (timeSelectEl) {
    timeSelectEl.disabled = false;
  }

  const filterEl = document.getElementById('timeStaffFilter');
  if (filterEl) {
    const prev = filterEl.value;
    filterEl.innerHTML = '';
    list.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.uid;
      opt.textContent = `${s.name}（${s.role}）`;
      filterEl.appendChild(opt);
    });
    filterEl.value = list.find(s => s.uid === prev) ? prev : (list[0]?.uid || '');
    filterEl.disabled = !currentProfile?.isAdmin && list.length <= 1;
  }
}

function renderStaffPage() {
  const el = document.getElementById('staffListEl');
  const addBox = document.getElementById('addStaffBox');
  el.innerHTML = '';

  if (!currentProfile?.isAdmin) {
    addBox.style.display = 'none';
    const self = fullStaffCache.find(s => s.uid === currentProfile?.uid) || currentProfile;
    const row = document.createElement('div');
    row.className = 'staff-item';
    row.innerHTML = `
      <div>
        <span class="staff-item-name">▶ ${escapeHtml(self.name)}</span>
        <span class="staff-item-role">（${escapeHtml(self.role)}）</span>
      </div>`;
    el.appendChild(row);
    return;
  }

  addBox.style.display = '';
  fullStaffCache.forEach(s => {
    const row = document.createElement('div');
    row.className = 'staff-item';
    row.innerHTML = `
      <div>
        <span class="staff-item-name">▶ ${escapeHtml(s.name)}</span>
        <span class="staff-item-role">（${escapeHtml(s.role)}）</span>
        <div style="color:#aaddff;font-size:0.72rem;">${escapeHtml(s.email)} ／ PW: ${escapeHtml(s.password)}</div>
      </div>
      ${s.uid !== currentProfile.uid
        ? `<button class="btn-danger" onclick="removeStaff('${s.uid}')">削除</button>`
        : '<span style="color:#4444aa;font-size:0.7rem;">本人</span>'}
    `;
    el.appendChild(row);
  });
}

function addStaff() {
  const name = document.getElementById('newStaffName').value.trim();
  const role = document.getElementById('newStaffRole').value.trim() || 'スタッフ';
  const email = document.getElementById('newStaffEmail').value.trim();
  const password = document.getElementById('newStaffPassword').value;
  const errEl = document.getElementById('addStaffError');
  errEl.textContent = '';
  if (!name || !email || !password) { errEl.textContent = '名前・メール・パスワードを入力してください'; return; }
  if (password.length < 6) { errEl.textContent = 'パスワードは6文字以上で入力してください'; return; }
  addStaffAccount(name, role, email, password).then(() => {
    document.getElementById('newStaffName').value = '';
    document.getElementById('newStaffRole').value = '';
    document.getElementById('newStaffEmail').value = '';
    document.getElementById('newStaffPassword').value = '';
  }).catch(err => { errEl.textContent = err.message || 'エラーが発生しました'; });
}

function removeStaff(uid) {
  if (!confirm('このスタッフを削除しますか？')) return;
  removeStaffAccount(uid);
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

// ── タスク（ローカル保存） ───────────────────
function loadTasks() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; } }
function saveTasks(t) { localStorage.setItem(STORAGE_KEY, JSON.stringify(t)); }

function renderBoard() {
  const tasks = loadTasks();
  const filter = document.getElementById('filterAssignee').value;
  STATUSES.forEach(status => {
    const list = document.getElementById(`list-${status}`);
    const countEl = document.getElementById(`count-${status}`);
    const filtered = tasks.filter(t => t.status === status && (!filter || t.assignee === filter));
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

// ── タイムカード（Firebase） ─────────────────
let timecardCache = []; // [{id, staffUid, date, business, hours, lock, memo}]

function listenTimecards() {
  const ref = currentProfile.isAdmin ? db.ref('timecards') : db.ref('timecards/' + currentProfile.uid);
  ref.on('value', snap => {
    const val = snap.val() || {};
    const records = [];
    if (currentProfile.isAdmin) {
      Object.keys(val).forEach(staffUid => {
        Object.keys(val[staffUid] || {}).forEach(id => {
          records.push({ id, staffUid, ...val[staffUid][id] });
        });
      });
    } else {
      Object.keys(val).forEach(id => {
        records.push({ id, staffUid: currentProfile.uid, ...val[id] });
      });
    }
    timecardCache = records;
    if (document.getElementById('page-time').style.display !== 'none') renderTimeCard();
  });
}

function staffNameByUid(uid) {
  const s = staffCache.find(s => s.uid === uid);
  return s ? s.name : '';
}

function changeMonth(dir) {
  currentMonth.setMonth(currentMonth.getMonth() + dir);
  renderTimeCard();
}

function renderTimeCard() {
  const y = currentMonth.getFullYear();
  const m = currentMonth.getMonth();
  const filterUid = document.getElementById('timeStaffFilter').value;
  document.getElementById('monthLabel').textContent = `${y}年${m+1}月`;

  const all = timecardCache.filter(tc => {
    const d = new Date(tc.date);
    return d.getFullYear() === y && d.getMonth() === m && (!filterUid || tc.staffUid === filterUid);
  });

  // 月合計
  const totalBar = document.getElementById('timeTotalBar');
  const totalH = all.reduce((s, tc) => s + tc.hours, 0);
  totalBar.innerHTML = `<div class="total-bar-inner">
    <span class="total-label">${escapeHtml(staffNameByUid(filterUid) || '全スタッフ')} ${y}年${m+1}月</span>
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
        ${currentProfile.isAdmin ? `<span class="tag tag-assignee">${escapeHtml(staffNameByUid(tc.staffUid))}</span>` : ''}
        ${tc.business ? `<span class="tag tag-business">${escapeHtml(tc.business)}</span>` : ''}
        <span class="cal-hours">${tc.hours}h</span>
        <span class="cal-pay">¥${(tc.hours*HOURLY_RATE).toLocaleString()}</span>
        <span class="${tc.lock==='yes'?'lock-yes':'lock-no'}">${tc.lock==='yes'?'🔑✓':'🔑✗'}</span>
        ${tc.memo?`<span class="cal-memo">${escapeHtml(tc.memo)}</span>`:''}
        <button class="btn-edit" onclick="openTimeModal('${tc.staffUid}','${tc.id}')">編集</button>
      </div>`).join('');

    row.innerHTML = `
      <div class="cal-date ${dow===0?'sun':dow===6?'sat':''}">
        <span class="cal-day">${d}</span>
        <span class="cal-week">${WEEKDAY[dow]}</span>
      </div>
      <div class="cal-content">${recHtml}</div>
      <button class="cal-add" onclick="openTimeModal(null,null,'${dateStr}')">＋</button>`;
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

function openTimeModal(staffUidOrNull, idOrNull, dateStr) {
  const record = (staffUidOrNull && idOrNull)
    ? timecardCache.find(tc => tc.staffUid === staffUidOrNull && tc.id === idOrNull)
    : null;

  document.getElementById('timeModalTitle').textContent = record ? '勤務記録 編集' : '勤務記録 追加';
  document.getElementById('timeId').value = record?.id || '';

  const date = record?.date || dateStr || new Date().toISOString().slice(0,10);
  document.getElementById('timeDate').value = date;

  const defaultUid = currentProfile.isAdmin
    ? (document.getElementById('timeStaffFilter').value || currentProfile.uid)
    : currentProfile.uid;
  const staffUid = record?.staffUid || defaultUid;
  document.getElementById('timeStaff').value = staffUid;
  document.getElementById('timeStaffSelect').value = staffNameByUid(staffUid);

  document.getElementById('timeBusinessSelect').value = record?.business || '';

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
  const staffUid = document.getElementById('timeStaff').value;
  if (!id || !confirm('この記録を削除しますか？')) return;
  db.ref('timecards/' + staffUid + '/' + id).remove();
  closeTimeModal();
});

timeForm.addEventListener('submit', e => {
  e.preventDefault();
  const hours = parseFloat(document.getElementById('timeHours').value);
  if (!hours) { alert('勤務時間を選択してください'); return; }
  const lock = document.getElementById('timeLock').value;
  if (!lock) { alert('鍵の確認を選択してください'); return; }
  let staffUid = document.getElementById('timeStaff').value;
  if (!currentProfile.isAdmin) staffUid = currentProfile.uid;
  if (!staffUid) { alert('スタッフを選択してください'); return; }
  const business = document.getElementById('timeBusinessSelect').value;
  if (!business) { alert('事業所を選択してください'); return; }
  const id = document.getElementById('timeId').value || generateId();
  const data = { date: document.getElementById('timeDate').value, business, hours, lock, memo: document.getElementById('timeMemo').value.trim() };
  db.ref('timecards/' + staffUid + '/' + id).set(data);
  closeTimeModal();
});

// ── 初期化 ───────────────────────────────────
populateBusinessSelects();
renderBoard();

window.onAuthReady = function() {
  const staffRef = currentProfile.isAdmin ? db.ref('staff') : null;
  db.ref('staffPublic').on('value', snap => {
    const val = snap.val() || {};
    staffCache = Object.keys(val).map(uid => ({ uid, ...val[uid] }));
    populateStaffSelects();
    if (document.getElementById('page-staff').style.display !== 'none') renderStaffPage();
  });
  if (currentProfile.isAdmin) {
    db.ref('staff').on('value', snap => {
      const val = snap.val() || {};
      fullStaffCache = Object.keys(val).map(uid => ({ uid, ...val[uid] }));
      if (document.getElementById('page-staff').style.display !== 'none') renderStaffPage();
    });
  }
  listenTimecards();
};
