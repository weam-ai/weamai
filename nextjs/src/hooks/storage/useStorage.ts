import commonApi from '@/api';
import { MODULE_ACTIONS, MODULES, DEFAULT_SORT, CURRENCY } from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import Toast from '@/utils/toast';
import { useState } from 'react';

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
    
    return { 
        getStorage, storageDetails, setStorageDetails, 
        updateStorage, getPendingStorageRequest, storageRequestList,
        loading, totalRecords, approveStorageRequest, declineStorageRequest,
        productPrice, dataLoading
    };
};

export default useStorage;
