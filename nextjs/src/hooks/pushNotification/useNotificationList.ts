import commonApi from '@/api';
import { setUnreadNotification, setUnreadCount } from '@/lib/slices/notificationSlice';
import { DEFAULT_LIMIT, DEFAULT_SORT, MODULES, MODULE_ACTIONS } from '@/utils/constant';
import { getCurrentUser } from '@/utils/handleAuth';
import { useState } from 'react'
import { useSelector } from 'react-redux';
import { useDispatch } from 'react-redux';

const useNotificationList = () => {
    const [loading, setLoading] = useState(false);
    const [notificationData, setNotificationData] = useState([]);
    const dispatch = useDispatch();
    const unreadcount = useSelector((store:any) => store.notification.unreadcount);
    
    const getNotificationList = async () => {
        try {
            setLoading(true);
            const userinfo = getCurrentUser();
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.NOTIFICATION,
                common: true,
                data: {
                    options: {
                        // offset: 0,
                        // limit: DEFAULT_LIMIT,
                        sort: { createdAt: DEFAULT_SORT },
                        pagination: false
                    },
                    query: {
                        'user.id': userinfo._id
                    }
                }
            })
            setNotificationData(response.data);
            const unread = response.data.filter(el => !el.isRead )
            dispatch(setUnreadNotification(unread));
            dispatch(setUnreadCount(unread.length));
        } catch (error) {
            console.error('error: ', error);
        } finally {
            setLoading(false);
        }
    }

    const removeAllNotification = async () => {
        try {
            await commonApi({
                action: MODULE_ACTIONS.DELETE_ALL_NOTIFICATION
            })
            setNotificationData([]);
            dispatch(setUnreadNotification([]));
            dispatch(setUnreadCount(0));
        } catch (error) {
            console.error('error: ', error);
        }
    }

    const markReadNotification = async (payload) => {
        try {
            await commonApi({
                action: MODULE_ACTIONS.MARK_ALL_NOTIFICATION,
                data: payload
            })
            dispatch(setUnreadNotification([]));
        } catch (error) {
            console.error('error: ', error);
        }
    }

    const unreadNotificationCount = async () => {
        try {
            setLoading(true);
            const userinfo = getCurrentUser();
            const response = await commonApi({
                action: MODULE_ACTIONS.UNREAD_NOTIFICATION_COUNT                
            })
            dispatch(setUnreadCount(response.data));
        } catch (error) {
            console.error('error: ', error);
        } finally {
            setLoading(false);
        }
    }

    return {
        loading,
        notificationData,
        getNotificationList,
        removeAllNotification,
        markReadNotification,
        unreadNotificationCount,
        unreadcount
    }
}

export default useNotificationList