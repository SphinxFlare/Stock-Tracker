// src/Settings/FirebaseConfig.jsx

// src/Settings/FirebaseConfig.jsx
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

// ✅ Replace with your actual Firebase configuration
const firebaseConfig = {
  apiKey: "BOcuiDKdmO3MvcvW3fMgglBfEho_lQ0-iNeQjFq-qSyr1KKbKtXCf4kKNZeAErHvrRcHtnVb21awn4U65wrDVzw",
  authDomain: "stock-tracker-3903e.firebaseapp.com",
  projectId: "stock-tracker-3903e",
  storageBucket: "stock-tracker-3903e.appspot.com",
  messagingSenderId: "826452625990",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// ✅ Request Notification Permission and Get Token
export const requestNotificationPermission = async () => {
  try {
    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
      console.warn("⚠️ Notification permission denied.");
      return null;
    }

    console.log("✅ Notification permission granted.");
    return getFCMToken();
  } catch (error) {
    console.error("❌ Error requesting notification permission:", error);
  }
};

// ✅ Get FCM Token
export const getFCMToken = async () => {
  try {
    console.log("⚡ Requesting FCM Token...");
    const token = await getToken(messaging, {
      vapidKey: "BOcuiDKdmO3MvcvW3fMgglBfEho_lQ0-iNeQjFq-qSyr1KKbKtXCf4kKNZeAErHvrRcHtnVb21awn4U65wrDVzw"
    });

    if (token) {
      console.log("✅ FCM Token:", token);
      return token;
    } else {
      console.warn("⚠️ No FCM token received. Make sure notifications are enabled.");
    }
  } catch (error) {
    console.error("❌ Error getting FCM token:", error);
  }
};

// ✅ Function to listen for incoming FCM messages
export const listenForMessages = () => {
  onMessage(messaging, (payload) => {
    console.log("🔔 New Notification:", payload);

    // ✅ Show a browser notification
    if (payload.notification) {
      new Notification(payload.notification.title, {
        body: payload.notification.body,
        icon: "/stock-icon.png"
      });
    }
  });
};

// ✅ Register the service worker
if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("/firebase-messaging-sw.js")
    .then((registration) => {
      console.log("✅ Service Worker registered successfully:", registration);
    })
    .catch((error) => {
      console.error("❌ Service Worker registration failed:", error);
    });
}