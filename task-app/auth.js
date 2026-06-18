let currentProfile = null;

const setupScreen = document.getElementById('setupScreen');
const loginScreen = document.getElementById('loginScreen');
const appRoot = document.getElementById('appRoot');

function showScreen(name) {
  setupScreen.style.display = name === 'setup' ? '' : 'none';
  loginScreen.style.display = name === 'login' ? '' : 'none';
  appRoot.style.display = name === 'app' ? '' : 'none';
}

function errMsg(err) {
  if (err.code === 'auth/wrong-password' || err.code === 'auth/invalid-credential') return 'パスワードが間違っています';
  if (err.code === 'auth/user-not-found') return 'パスワードが間違っています';
  if (err.code === 'auth/email-already-in-use') return 'このメールアドレスは既に使われています';
  if (err.code === 'auth/weak-password') return 'パスワードは6文字以上で入力してください';
  return 'エラーが発生しました：' + err.message;
}

auth.onAuthStateChanged(user => {
  if (!user) {
    db.ref('meta/setupDone').once('value').then(snap => {
      showScreen(snap.val() ? 'login' : 'setup');
    });
    return;
  }
  db.ref('staff/' + user.uid).once('value').then(snap => {
    const profile = snap.val();
    if (!profile) { auth.signOut(); return; }
    currentProfile = { uid: user.uid, ...profile };
    document.getElementById('loginUserLabel').textContent = `${profile.name}（${profile.role}）`;
    document.getElementById('openModalBtn').style.display = '';
    showScreen('app');
    if (window.onAuthReady) window.onAuthReady();
  });
});

document.getElementById('setupBtn').addEventListener('click', () => {
  const name = document.getElementById('setupName').value.trim();
  const email = document.getElementById('setupEmail').value.trim();
  const password = document.getElementById('setupPassword').value;
  const errEl = document.getElementById('setupError');
  errEl.textContent = '';
  if (!name || !email || !password) { errEl.textContent = '全ての項目を入力してください'; return; }
  if (password.length < 6) { errEl.textContent = 'パスワードは6文字以上で入力してください'; return; }
  auth.createUserWithEmailAndPassword(email, password).then(cred => {
    const uid = cred.user.uid;
    return Promise.all([
      db.ref('staff/' + uid).set({ name, role: '代表取締役', email, password, isAdmin: true }),
      db.ref('staffPublic/' + uid).set({ name, role: '代表取締役' }),
      db.ref('passwords/' + password).set(email),
      db.ref('meta/setupDone').set(true),
    ]);
  }).catch(err => { errEl.textContent = errMsg(err); });
});

document.getElementById('loginBtn').addEventListener('click', () => {
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';
  if (!password) { errEl.textContent = 'パスワードを入力してください'; return; }
  db.ref('passwords/' + password).once('value').then(snap => {
    const email = snap.val();
    if (!email) { errEl.textContent = 'パスワードが間違っています'; return; }
    auth.signInWithEmailAndPassword(email, password).catch(err => { errEl.textContent = errMsg(err); });
  });
});

document.getElementById('logoutBtn').addEventListener('click', () => {
  auth.signOut();
  showScreen('login');
});

function addStaffAccount(name, role, email, password, isAdmin = false) {
  return secondaryAuth.createUserWithEmailAndPassword(email, password).then(cred => {
    const uid = cred.user.uid;
    return Promise.all([
      db.ref('staff/' + uid).set({ name, role, email, password, isAdmin }),
      db.ref('staffPublic/' + uid).set({ name, role }),
      db.ref('passwords/' + password).set(email),
    ]).then(() => secondaryAuth.signOut());
  });
}

function removeStaffAccount(uid) {
  return db.ref('staff/' + uid).once('value').then(snap => {
    const data = snap.val();
    return Promise.all([
      db.ref('staff/' + uid).remove(),
      db.ref('staffPublic/' + uid).remove(),
      data?.password ? db.ref('passwords/' + data.password).remove() : Promise.resolve(),
    ]);
  });
}
