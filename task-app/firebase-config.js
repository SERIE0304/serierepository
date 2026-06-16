const firebaseConfig = {
  apiKey: "AIzaSyDE95mMjMMDd9jlNRG2BpHts0LdOBNLLjg",
  authDomain: "serie-concerto.firebaseapp.com",
  databaseURL: "https://serie-concerto-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "serie-concerto",
  storageBucket: "serie-concerto.firebasestorage.app",
  messagingSenderId: "123048343625",
  appId: "1:123048343625:web:177b4e75ffe6b1e9ea6798",
  measurementId: "G-0XZW7PMGT0"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.database();

const secondaryApp = firebase.initializeApp(firebaseConfig, 'Secondary');
const secondaryAuth = secondaryApp.auth();
