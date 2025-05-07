// public/firebase-messaging-sw.js

importScripts("https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging.js");

const firebaseConfig = {
  apiKey: "BOcuiDKdmO3MvcvW3fMgglBfEho_lQ0-iNeQjFq-qSyr1KKbKtXCf4kKNZeAErHvrRcHtnVb21awn4U65wrDVzw",
  authDomain: "stock-tracker-3903e.firebaseapp.com",
  projectId: "stock-tracker-3903e",
  storageBucket: "stock-tracker-3903e.appspot.com",
  messagingSenderId: "826452625990",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};

// ✅ Initialize Firebase in service worker
firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

// ✅ Handle background push notifications
messaging.onBackgroundMessage((payload) => {
  console.log("📩 Background message received:", payload);
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
    icon: "/stock-icon.png"
  });
});