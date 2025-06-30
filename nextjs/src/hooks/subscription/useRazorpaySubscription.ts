import commonApi from "@/api";
import { DEFAULT_SORT, MODULE_ACTIONS } from "@/utils/constant";
import { useState } from "react";
import { useDispatch } from "react-redux";
import { setReloadSubscription } from '@/lib/slices/subscription/subscriptionSlice';
import { getCurrentUser } from '@/utils/handleAuth';
import { MODULES } from '@/utils/constant';

export const useRazorpaySubscription = () => {

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [validCoupon, setValidCoupon] = useState(false);
    const [razorpaySubscriptionData, setRazorpaySubscriptionData] = useState(null);
    const [invoiceList, setInvoiceList] = useState(null);
    const [totalRecords, setTotalRecords] = useState(0);
    const [razorpayPaymentMethodData, setRazorpayPaymentMethodData] = useState(null);
    const dispatch = useDispatch();

    const createRazorpayOrder = async (payload) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE_RAZORPAY_ORDER,
                data:payload
            });
            return response?.data;
        } catch (error) {
            console.error("🚀 ~ createRazorpayOrder ~ error:", error)
        } finally {
            setLoading(false);
        }
    }

    const createRazorpaySubscription = async (payload) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE_RAZORPAY_SUBSCRIPTION,
                data:payload
            });
            return response;
        } catch (error) {
            console.error("🚀 ~ createRazorpaySubscription ~ error:", error)
        } finally {
            setLoading(false);
        }
    }

    const fetchRazorpayPlan = async () => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_RAZORPAY_PLAN
            });
            return response?.data;
        } catch (error) {
            console.error("🚀 ~ fetchRazorpayPlan ~ error:", error)
        } finally {
            setLoading(false);
        }
    }
    
    const verifyRazorpayPayment = async (payload) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.VERIFY_RAZORPAY_PAYMENT,
                data:payload
            });
            dispatch(setReloadSubscription(true));
            return response?.data;
        } catch (error) {
            console.error("🚀 ~ verifyRazorpayPayment ~ error:", error)
        }
    }

    const fetchRazorpaySubscription = async () => {
        setLoading(true);
        try {       
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_RAZORPAY_SUBSCRIPTION,
               
            });
           
            setRazorpaySubscriptionData(response?.data);
        } catch (error) {
            console.error("🚀 ~ fetchRazorpaySubscription ~ error:", error)
            setRazorpaySubscriptionData(null);
        }finally{
            setLoading(false);
        }
    }

    const updateRazorpaySubscription = async (payload) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE_RAZORPAY_SUBSCRIPTION,
                data:payload
            });
            dispatch(setReloadSubscription(true));
            return response;
        } catch (error) {
            console.error("🚀 ~ updateRazorpaySubscription ~ error:", error)
        } finally {
            setLoading(false);
        }
    }

    const getRazorpayInvoiceList = async (search, limit=10, offset=0, sort = '-1', sortby = 'id',isPagination=true) => {
        setLoading(true);
        try {

            const user = getCurrentUser();

            const query = {
                'company.id': user?.company?.id,
                search: search, 
                searchColumns: ["invoiceNo"]
            };


            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.INVOICE,
                common: true,
                data: {
                    options: {
                        ...(isPagination && { offset: offset, limit: limit }),
                        sort: {
                            createdAt: DEFAULT_SORT,
                        },
                        query,
                    },
                },
            });

            setInvoiceList(response?.data);
            setTotalRecords(response?.data?.paginator?.itemCount);
            return response;
        } catch (error) {
            console.error("🚀 ~ getRazorpayInvoiceList ~ error:", error)
        }finally{
            setLoading(false);
        }
    }

    const cancelRazorpaySubscription = async (payload) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CANCEL_RAZORPAY_SUBSCRIPTION,
                data:payload
            });

            dispatch(setReloadSubscription(true));
            return response;
        } catch (error) {
            console.error("🚀 ~ cancelRazorpaySubscription ~ error:", error)
        } finally {
            setLoading(false);
        }
    }

    const updateRazorpayCard = async (payload) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE_RAZORPAY_CARD,
                data:payload
            });
            return response;
        } catch (error) {
            console.error("🚀 ~ updateRazorpayCard ~ error:", error)
        } finally {
            setLoading(false);  
        }
    }

    const getRazorpayPaymentMethod = async () => {
        try {
            const response = await commonApi({
                action:  MODULE_ACTIONS.GET_RAZORPAY_PAYMENT_METHOD
            })
            setRazorpayPaymentMethodData(response?.data);
            return response;
        } catch (error) {
            console.error("🚀 ~ getRazorpayPaymentMethod ~ error:", error)
        }
    }

    const unCancelRazorpaySubscription = async (payload) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UNCANCEL_RAZORPAY_SUBSCRIPTION,
                data:payload    
            });
            return response;
        } catch (error) {
            console.error("🚀 ~ unCancelRazorpaySubscription ~ error:", error)
        } finally {
            setLoading(false);
        }
    }
    
                
    return {
        loading,
        fetchRazorpayPlan,
        createRazorpaySubscription,
        createRazorpayOrder,
        verifyRazorpayPayment,
        validCoupon,
        setValidCoupon,
        fetchRazorpaySubscription,
        razorpaySubscriptionData,
        updateRazorpaySubscription,
        getRazorpayInvoiceList,
        invoiceList,
        cancelRazorpaySubscription,
        totalRecords,
        updateRazorpayCard,
        getRazorpayPaymentMethod,
        razorpayPaymentMethodData,
        unCancelRazorpaySubscription
    }
}