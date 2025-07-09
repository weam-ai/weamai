"use client";
import { useEffect, useState } from "react";
// import { getToken, isSupported } from "firebase/messaging";
// import { messaging } from "@/config/firebase";
// import useNotificationPermission from "./useNotificationPermission";
// import { LocalStorage } from '@/utils/localstorage';
// import useLogin from "../auth/useLogin";
// import { FIREBASE } from "@/config/config";

const useFCMToken = () => {
  // const { permission, requestPermission } = useNotificationPermission();
  // const [fcmToken, setFcmToken] = useState(null);

  // const {fcmTokenSaveInDb} = useLogin();

  // useEffect(() => {
  //   const retrieveToken = async () => {
  //     if (typeof window !== "undefined" && "serviceWorker" in navigator) {
  //       if (permission === "granted") {
  //         const localFCMToken = LocalStorage.get('fcm-token');
  //         if (localFCMToken) {
  //           setFcmToken(fcmToken);
  //         } else {
  //           const isFCMSupported = await isSupported();
  //           if (!isFCMSupported) return;
  //           const fcmToken = await getToken(messaging(), {
  //             vapidKey: FIREBASE.VAPID_KEY
  //           });
  //           LocalStorage.set('fcm-token',fcmToken);
  //           await fcmTokenSaveInDb();
  //           setFcmToken(fcmToken);
  //         }
  //       } else {
  //         LocalStorage.remove('fcm-token')
  //         requestPermission();
  //       }
  //     }
  //   };
  //   retrieveToken();
  // }, [permission]);

  // return fcmToken;
  
  // Return null when FCM is disabled
  return null;
};

export default useFCMToken;
