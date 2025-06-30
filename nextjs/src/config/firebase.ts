"use client";
import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";
import { FIREBASE } from "./config";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: FIREBASE.API_KEY,
  authDomain: FIREBASE.AUTH_DOMAIN,
  projectId: FIREBASE.PROJECT_ID,
  storageBucket: FIREBASE.STORAGE_BUCKET,
  messagingSenderId: FIREBASE.MESSAGING_SENDER_ID,
  appId: FIREBASE.APP_ID
};

// Initialize Firebase
const firebaseapp = initializeApp(firebaseConfig);


export const messaging = () => getMessaging(firebaseapp);

export default firebaseapp;
