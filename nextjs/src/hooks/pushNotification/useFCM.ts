import { useEffect } from "react";
// import useFCMToken from "./useFCMToken";
// import { messaging } from "@/config/firebase";
// import { onMessage } from "firebase/messaging";
// import { NotificationToast } from '@/utils/toast';

const useFCM = () => {
  // const fcmToken = useFCMToken();
  // useEffect(() => {
  //   if (typeof window !== "undefined" && "serviceWorker" in navigator) {
  //     try {
  //       const fcmmessaging = messaging();
  //       const unsubscribe = onMessage(fcmmessaging, (payload) => {
  //         NotificationToast(payload.notification, payload.data);
  //       });
  //       return () => unsubscribe();
  //     } catch (error) {
  //       console.log(error, '-error');
  //     }
  //   }
  // }, [fcmToken]);
  // return { fcmToken };
  
  // Return null token when FCM is disabled
  return { fcmToken: null };
};

export default useFCM;
