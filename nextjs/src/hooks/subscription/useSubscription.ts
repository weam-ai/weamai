import { useState, useEffect } from 'react';
import commonApi from '@/api';
import { MODULE_ACTIONS, MODULES, DEFAULT_SORT, SUBSCRIPTION_STATUS, EXPIRED_SUBSCRIPTION_MESSAGE } from '@/utils/constant';
import Toast from '@/utils/toast';
import { useDispatch,useSelector } from 'react-redux';
import { setReloadSubscription } from '@/lib/slices/subscription/subscriptionSlice';
import { getCurrentUser } from '@/utils/handleAuth';
import { STRIPE_SUBSCRIPTION_PRICE_ID, STRIPE_SUBSCRIPTION_PRICE_ID_IND, STRIPE_TEST_PRICE_ID } from '@/config/config';
import { isIndiaByTimezone } from '@/utils/helper';
import { isCreditLimitExceeded } from '@/utils/common';
import { RootState } from '@/lib/store';
export const useSubscription = () => {
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dataLoading, setDataLoading] = useState(false);
    const [upcomingLoading, setUpcomingLoading] = useState(false);
    const [subscriptionData, setSubscriptionData] = useState({});
    const [upcomingInvoiceData, setUpcomingInvoiceData] = useState(null);
    const [paymentMethodData, setPaymentMethodData] = useState(null);
    const [invoiceList, setInvoiceList] = useState(null);
    const [productPrice, setProductPrice] = useState(null);
    const [validCoupon, setValidCoupon] = useState(false);
    const [totalRecords, setTotalRecords] = useState(0);
    
    const dispatch = useDispatch();
    const {subscriptionStatus,msgCreditLimit,msgCreditUsed} = useSelector((state: RootState) => state.chat.creditInfo);
    
    const fetchActiveSubscription = async (url:any) => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: url ?? MODULE_ACTIONS.GET_SUBSCRIPTION_DETAILS
                
            });

           
            setSubscriptionData(response?.data);
            
        } catch (err) {
            setError('Failed to fetch subscription details.');
            setSubscriptionData(null);
        } finally {
            setLoading(false);
        }
    };

    const getProductPrice = async (priceId) => {
        try {
            setDataLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_PRODUCT_PRICE,
                parameters:[priceId]
            });
            setProductPrice(response?.data);
            setDataLoading(false);
            return response?.data;        
        } catch (err) {
            setError('Failed to fetch product price.');
            setProductPrice(null);
            setDataLoading(false);
        }
    }

    const handleSubscription = async (payload) => {
        setLoading(true);
        
        try {
            const priceId = isIndiaByTimezone() ? STRIPE_SUBSCRIPTION_PRICE_ID_IND : STRIPE_SUBSCRIPTION_PRICE_ID;
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE_CUSTOMER,
                data: { ...payload , price_id: priceId }
            })

            if(response?.code == 'SUCCESS' && response?.data?.requiresAction === true){
                return response?.data;
            } else if(response?.code == 'SUCCESS'){
                dispatch(setReloadSubscription(true));
                Toast(response?.message);
                setLoading(false);
            }
            // return { success: true };

        } catch (err) {
            setError('An unexpected error occurred.');
            return { success: false };
        } finally {
            // setLoading(false);
        }
    };

    const testHandleSubscription = async (payload) => {
        setLoading(true);
        
        try {
            const priceId = STRIPE_TEST_PRICE_ID;
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE_CUSTOMER,
                data: { ...payload , price_id: priceId }
            })

            if(response?.code == 'SUCCESS' && response?.data?.requiresAction === true){
                return response?.data;
            } else if(response?.code == 'SUCCESS'){
                dispatch(setReloadSubscription(true));
                Toast(response?.message);
                setLoading(false);
            }

        } catch (err) {
            setError('An unexpected error occurred.');
            return { success: false };
        } finally {
            setLoading(false);
        }
    }
    

    const handle3dSubscription=async(payload)=>{
        setLoading(true);
        
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.HANDLE_3D_SECURE_SUBSCRIPTION,
                data: { ...payload  }
            })

            
            if(response?.code == 'SUCCESS'){
                dispatch(setReloadSubscription(true));
                Toast(response?.message);
            }
            // return { success: true };

        } catch (err) {
            setError('An unexpected error occurred.');
            return { success: false };
        } finally {
            setLoading(false);
        }
    }

    const cancelSubscription = async (payload) => {
        const response = await commonApi({
            action: MODULE_ACTIONS.CANCEL_SUBSCRIPTION,
            data: payload
        })
        
        dispatch(setReloadSubscription(true));
        if(response?.code == 'SUCCESS'){
            Toast(response?.message);
        }
    }

    const unCancelSubscription = async (payload) => {
        setDataLoading(true);
        const response = await commonApi({
            action: MODULE_ACTIONS.UNCANCEL_SUBSCRIPTION,
        })
        
        dispatch(setReloadSubscription(true));
        if(response?.code == 'SUCCESS'){
            Toast(response?.message);
        }
        setDataLoading(false);
    }

    const upcomingInvoice = async () => {
        setUpcomingLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UPCOMING_INVOICE
            });
            setUpcomingInvoiceData(response.data);
            
        } catch (err) {
            setError('Failed to fetch upcoming invoice.');
        } finally {
            setUpcomingLoading(false);
        }
    }

    const upgradeSubscription = async (payload) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.UPGRADE_SUBSCRIPTION,
                data: payload 
            });
            
            dispatch(setReloadSubscription(true));
            Toast(response.message);
        } catch (error) {
            return { success: false };
        } finally {
            setLoading(false);
        }
    }

    const updatePaymentMethod = async (payload) => {
        try {
            setLoading(true);
            
            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE_PAYMENT_METHOD,
                data: payload
            })
            
            Toast(response.message);

            // closeModal();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }    
    }

    const showDefaultPaymentMethod = async () => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.SHOW_DEFAULT_PAYMENT_METHOD
            })

            setPaymentMethodData(response.data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    const getInvoiceList = async (search, limit=10, offset=0, sort = '-1', sortby = 'id',isPagination=true) => {
        try {
            setLoading(true);
            
            const searchColumns = ['email', 'roleCode', 'fname', 'lname'];
            // const search = search;
            const user = getCurrentUser();
            
            const query = {
                'company.id': user?.company?.id,
                search: search, 
                searchColumns: ["invoiceNo","invoiceId"]
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
                    },
                    query,
                },
            });
            setInvoiceList(response.data);
            setTotalRecords(response?.data.paginator?.itemCount);
            setLoading(false);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const checkCouponCode = async (payload) => {
        const response = await commonApi({
            action: MODULE_ACTIONS.CHECK_COUPON_CODE,
            data: payload
        });

        if(!response.data.valid){
            Toast("Invalid Coupon Code",'error');
        }else{
            setValidCoupon(response.data);
            Toast(response.message);
        }
    }

    const freeSubscriptionChecker = () => {
        try {
            return subscriptionStatus;
        } catch (error) {
            console.error('error: useFreeSubscriptionChecker ', error);
        }
    }

    const isSubscriptionActive = () => {
        const checker = [SUBSCRIPTION_STATUS.EXPIRED,SUBSCRIPTION_STATUS.CANCELED]
        if (
            checker.includes(subscriptionStatus) ||
            (!subscriptionStatus && isCreditLimitExceeded(msgCreditLimit,msgCreditUsed))
        ) {
            Toast(EXPIRED_SUBSCRIPTION_MESSAGE, 'error');
            return false;
        }
        return true;
    }

    const getStripePlans = async () => {
        setLoading(true);
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_STRIPE_PLANS
            });
            return response?.data;
        } catch (error) {
            console.error("🚀 ~ getStripePlans ~ error:", error)
        } finally {
            setLoading(false);
        }
    }

    return {
        handleSubscription,
        testHandleSubscription,
        error,
        setError,
        loading,
        setLoading,
        getProductPrice,
        subscriptionData,
        fetchActiveSubscription,
        cancelSubscription,
        upcomingInvoice,
        upcomingInvoiceData,
        upcomingLoading,
        upgradeSubscription,
        updatePaymentMethod,
        showDefaultPaymentMethod,
        paymentMethodData,
        getInvoiceList,
        invoiceList,
        productPrice,
        checkCouponCode,
        validCoupon,
        setValidCoupon,
        freeSubscriptionChecker,
        isSubscriptionActive,
        totalRecords,
        dataLoading,
        unCancelSubscription,
        handle3dSubscription,
        getStripePlans       
    };
}; 