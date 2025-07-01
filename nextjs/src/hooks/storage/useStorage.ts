import commonApi from '@/api';
import { MODULE_ACTIONS, MODULES, DEFAULT_SORT, CURRENCY } from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import Toast from '@/utils/toast';
import { useState } from 'react';
import { STRIPE_STORAGE_PRICE_ID, STRIPE_STORAGE_PRICE_ID_IND } from '@/config/config';
import { isIndiaByTimezone } from '@/utils/helper';

type ConfirmStoragePaymentPayload = {
    paymentIntentId: string;
    storageRequestId: string;
    updatedStorageSize: number;
}

const useStorage = () => {
    const [storageDetails, setStorageDetails] = useState(null);
    const [storageRequestList, setStorageRequestList] = useState(null);
    const [loading, setLoading] = useState(false);
    const [totalRecords, setTotalRecords] = useState(0);
    const [productPrice, setProductPrice] = useState(null);
    const [dataLoading, setDataLoading] = useState(null);
    
    const getStorage = async() => {
        try{
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_STORAGE
            })
            setStorageDetails(response.data);

        } catch (error) {
            console.error('Error fetching storage: ', error);
        }
    }

    const updateStorage = async (payload) => { 
        try { 
            const response = await commonApi({
                action: MODULE_ACTIONS.INCREASE_STORAGE,
                data: payload                
            })
            
            Toast(response.message); 
            
        } catch (error) {
            console.error('Error updating storage: ', error);
        } finally {
            
        }
    }
    
    const getPendingStorageRequest = async ( status, search, limit=10, offset=0, sort = '-1', sortby = 'id',isPagination=true) => {
        try{
            setLoading(true);
            
        const currentUser = getCurrentUser();
        const companyId = getCompanyId(currentUser); 
            
        const query = {
            status: { $eq: status },
            'company.id': companyId
        };
        
        const response = await commonApi({
            action: MODULE_ACTIONS.LIST,
            prefix: MODULE_ACTIONS.ADMIN_PREFIX,
            module: MODULES.STORAGE_REQUEST,
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
        setStorageRequestList(response.data);
            setTotalRecords(response?.paginator?.itemCount || 0);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching pending storage request: ', error);
        } finally {
            setLoading(false);
        }
    }

    const approveStorageRequest = async (payload) => {
        try{
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.APPROVE_STORAGE_REQUEST,
                data: payload
            })  
            console.log(response);
            if(response?.code=='SUCCESS'){
                Toast(response?.message);
            }
            return response;
        } catch (error) {
            console.error('Error approving storage request: ', error);
        } finally {
            setLoading(false);
        }
    }

    const declineStorageRequest = async (payload) => {
        try{
            const response = await commonApi({
                action: MODULE_ACTIONS.DECLINE_STORAGE_REQUEST,
                data: payload
        })  
            Toast(response?.message);
        } catch (error) {
            console.error('Error declining storage request: ', error);
        } finally {
            setLoading(false);
        }
    }

    // const getStorageProductPrice = async (currency) => {
    //     try{
    //         setDataLoading(true);
    //         let priceId = '';
    //         if(currency){
    //         priceId = (currency === CURRENCY.INR) ? STRIPE_STORAGE_PRICE_ID_IND : STRIPE_STORAGE_PRICE_ID;
    //     } else {
    //         priceId = isIndiaByTimezone() ? STRIPE_STORAGE_PRICE_ID_IND : STRIPE_STORAGE_PRICE_ID;
    //     }
            
    //     const response = await commonApi({
    //         action: MODULE_ACTIONS.GET_PRODUCT_PRICE,
    //         parameters:[priceId]
    //     });

    //         setProductPrice(response?.data);
    //         setDataLoading(false);
    //     } catch (error) {
    //         console.error('Error fetching storage product price: ', error);
    //     } finally {
    //         setDataLoading(false);
    //     }
    // }

    // const getRazorpayStoragePrice = async () => {
    //     try{
    //         setLoading(true);
    //         const response = await commonApi({
    //             action: MODULE_ACTIONS.GET_RAZORPAY_STORAGE_PRICE
    //         })
    //         setRazorpayStoragePrice(response?.data);

    //     } catch (error) {
    //         console.error('Error fetching razorpay storage price: ', error);
    //     } finally {
    //         setLoading(false);
    //     }
        
    // }

    // const razorpayStorageApprove = async (payload) => {
    //     try{
    //         setLoading(true);
    //         const response = await commonApi({
    //             action: MODULE_ACTIONS.RAZORPAY_STORAGE_APPROVE,
    //             data: payload
    //         })
           
    //         return response;
    //     } catch (error) {
    //         console.error('Error approving razorpay storage payment: ', error);
    //     } finally {
    //         setLoading(false);
    //     }
    // }

    // const verifyRazorpayStoragePayment = async (payload,storageRequestId,updatedStorageSize) => {
    //     try{
    //         const response = await commonApi({
    //             action: MODULE_ACTIONS.VERIFY_RAZORPAY_STORAGE_PAYMENT,
    //             data: {
    //                 ...payload,
    //                 storageRequestId,
    //                 updatedStorageSize
    //             }
    //         })
    //         return response;
    //     } catch (error) {
    //         console.error('Error verifying razorpay storage payment: ', error);
    //     } finally {
    //         setLoading(false);
    //     }
    // }

    const confirmStoragePayment = async (payload: ConfirmStoragePaymentPayload) => {
        try{
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.CONFIRM_STORAGE_PAYMENT,
                data: payload
            })
            return response;
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }
    

    return { 
        getStorage, storageDetails, setStorageDetails, 
        updateStorage, getPendingStorageRequest, storageRequestList,
        loading, totalRecords, approveStorageRequest, declineStorageRequest,
        productPrice, dataLoading, confirmStoragePayment
    };
};

export default useStorage;
