import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getAccessToken } from '@/actions/serverApi';
import { setCreditInfoAction } from "@/lib/slices/chat/chatSlice";
import { RootState } from "@/lib/store";
export function useSubscriptionSSE() {
  const [sessionData, setSessionData] = useState(null);
  // const dispatch = useDispatch();
  // const creditInfo = useSelector((state: RootState) => state.chat.creditInfo);
  
  // useEffect(() => {
  //   const initConnection = async () => {
  //     try {
  //       // Get initial session
  //       const token = await getAccessToken()
  //       setSessionData(token);

  //       // Get the token
      
  //       if (!token) {
  //         console.error('No refresh token found');
  //         return;
  //       }

  //       // Create EventSource with token in URL
  //       const eventSource = new EventSource(
  //         `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/web/payment/sse/subscriptionEvent?authorization=jwt ${token}`, 
  //         { withCredentials: true }
  //       );

  //       // Connection opened
  //       eventSource.onopen = () => {
  //         console.log('SSE Connection opened successfully');
  //       };

  //       // Connection error
  //       eventSource.onerror = (error) => {
  //         console.error('SSE Connection error:', error);
  //         eventSource.close();
  //         setTimeout(initConnection, 5000);
  //       };

  //       // Receive message
  //       eventSource.onmessage = async (event) => {
  //         try {
  //           const {data} = JSON.parse(event.data);
  //           if (data) {
  //             dispatch(setCreditInfoAction({ ...creditInfo, subscriptionStatus: data?.status, msgCreditLimit: data?.msgCreditLimit, msgCreditUsed: data?.msgCreditUsed }))
  //           }
  //         } catch (error) {
  //           console.error('Error processing subscription update:', error);
  //         }
  //       };

  //       // Cleanup function
  //       return () => {
  //         console.log('Closing SSE connection');
  //         eventSource.close();
  //       };
  //     } catch (error) {
  //       console.error('Error initializing SSE:', error);
        
        
  //       const errorHandler = (event: ErrorEvent) => {
  //         console.warn('Global error caught:', event);
  //         event.preventDefault(); 
  //         return true;  
  //       };
        
        
  //       const rejectionHandler = (event: PromiseRejectionEvent) => {
  //         console.warn('Unhandled promise rejection:', event.reason);
  //         event.preventDefault(); 
  //         return true; 
  //       };
        
  //       window.addEventListener('error', errorHandler);
  //       window.addEventListener('unhandledrejection', rejectionHandler);
        
  //       setTimeout(() => {
  //         window.removeEventListener('error', errorHandler);
  //         window.removeEventListener('unhandledrejection', rejectionHandler);
          
  //         initConnection().catch(err => console.error('Reconnection failed:', err));
  //       }, 5000);
  //     }
  //   };

  //   initConnection().catch(error => {
  //     console.error('Initial connection failed:', error);
  //   });
  // }, [dispatch]); 

  // return sessionData;
} 