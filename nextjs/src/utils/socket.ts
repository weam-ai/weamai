"use client";
import { LINK } from "@/config/config";
import { useEffect, useMemo, useState } from 'react';
import io, { Socket } from 'socket.io-client';
import { getCurrentUser } from "./handleAuth";

const SOCKET_SERVER_URL = LINK.SOCKET_CONNECTION_URL; // Replace with your socket server URL

const useSocket = (): Socket | null => {
  const [socket, setSocket] = useState<Socket | null>(null);

  const user = useMemo(() => getCurrentUser(), []);
  useEffect(() => {
    const newSocket = io(SOCKET_SERVER_URL, { withCredentials: true, transports: ['websocket'], path: '/napi/socket.io' });

     // Handle socket errors
     newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });
    
    newSocket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    const handleUncaughtError = (error: ErrorEvent) => {
      console.error('Uncaught error:', error.message);
      if (newSocket && newSocket.connected) {
        newSocket.emit('client_error', {
          type: 'uncaught_error',
          message: error.message,
          stack: error.error?.stack,
          userId: user?._id
        });
      }
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      if (newSocket && newSocket.connected) {
        newSocket.emit('client_error', {
          type: 'unhandled_promise',
          message: event.reason?.message || String(event.reason),
          stack: event.reason?.stack,
          userId: user?._id
        });
      }
    };

    // Add event listeners
    window.addEventListener('error', handleUncaughtError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    setSocket(newSocket);

    // Clean up function
    return () => {
      window.removeEventListener('error', handleUncaughtError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      newSocket.disconnect();
    };
  }, []);

  return socket;
};

export default useSocket;
