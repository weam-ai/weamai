// public/firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey: 'AIzaSyBJAnDC3nwmj2nmqZhIX2ufTpJXwNL2y3k',
  authDomain: 'weam-ai.firebaseapp.com',
  projectId: 'weam-ai',
  storageBucket: 'weam-ai.appspot.com',
  messagingSenderId: '919707575721',
  appId: '1:919707575721:web:e516d10c84887b8975d0b8',
  measurementId: 'G-ZBRX9MDN05'
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();


messaging.onBackgroundMessage(function (payload) {
  if (!("Notification" in self)) {
    // Check if the browser supports notifications
    console.log("This browser does not support desktop notification");
  } else if (Notification.permission === 'granted') {
    self.registration.showNotification(payload.notification.title, {
      body: payload.notification.body,
      data: { url: payload.data?.deepLink },
      requireInteraction: true,
      actions: [{ action: 'open_url', title: 'Open' }]
    });
  }
});
// Add click handler for the notification
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const urlToOpen = event.notification.data?.url;
  if (urlToOpen) {
    clients.openWindow(urlToOpen);
  }
});

