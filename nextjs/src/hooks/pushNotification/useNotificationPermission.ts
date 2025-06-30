"use client";
import { useEffect, useState } from "react";

const useNotificationPermissionStatus = () => {
  const [permission, setPermission] = useState(() => {
    if (typeof Notification === 'undefined') {
      return 'unsupported';
    }
    return Notification.permission;
  });

  const requestPermission = async () => {
    if (typeof Notification !== 'undefined' && Notification.requestPermission) {
      const permissionResult = await Notification.requestPermission();
      setPermission(permissionResult);
    } else {
      console.warn("Notification API is not supported in this environment.");
      setPermission('unsupported');
    }
  };

  useEffect(() => {
    if (typeof Notification !== 'undefined') {
      setPermission(Notification.permission);
    }
  }, []);

  return { permission, requestPermission };
};

export default useNotificationPermissionStatus;
