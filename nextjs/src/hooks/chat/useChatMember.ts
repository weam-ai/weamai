import commonApi from '@/api';
import { chatMemberListAction, setChatInfoAction, setFavouriteAction } from '@/lib/slices/chat/chatSlice';
import { MODULES, MODULE_ACTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { useSelector, useDispatch } from 'react-redux';
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
import { addMemberChatKeys } from '@/schema/chatmember';
import { getCurrentUser } from '@/utils/handleAuth';
import { setChatMessageAction } from '@/lib/slices/aimodel/conversation';
import { useState } from 'react';

const defaultValue:any = {
    members:[],
}

const useChatMember = () => {
    const chatmembers = useSelector((store:any) => store.chat.members);
    const favourite = useSelector((store:any) => store.chat.favourite);
    const [chatList, setChatList] = useState([])
    const [loading, setLoading] = useState(false)
    const dispatch = useDispatch();

    const user = getCurrentUser();

    const {
        register,
        handleSubmit,
        formState: { errors },
        control,
        setValue:setFormValue,
        reset
    } = useForm({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        defaultValues:defaultValue,
        resolver: yupResolver(addMemberChatKeys)
    })

    const getChatMembers = async (chatId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_MEMBER,
                common: true,
                data: {
                    options: {
                        pagination: false,
                    },
                    query: {
                        chatId: chatId,
                        teamId:{$exists:false},
                    }
                }
            });
            dispatch(chatMemberListAction(response.data));
            const data = response.data.find((el) => el.chatId == chatId && el.user.id == user._id)
            dispatch(setFavouriteAction(data?.isFavourite))
        } catch (error) {
            console.log('error: ', error);
        }
    };

    const favouriteChat = async (payload, chatId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.PARTIAL,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_MEMBER,
                common: true,
                data: {
                    isFavourite: payload
                },
                parameters: [chatId]
            })
            dispatch(setFavouriteAction(response.data.isFavourite))
            Toast(response.message);
        } catch (error) {
            console.log('error: ', error);
        }
    }

    const addChatMember = async (members) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_MEMBER,
                common: true,
                data: {
                    members,
                    isBulk: true
                }
            })
            const addedMember = chatmembers.concat(response.data);
            dispatch(chatMemberListAction(addedMember));
        } catch (error) {
            console.log('error: ', error);
        }
    }

    const removeChatMember = async (id) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_MEMBER,
                common: true,
                parameters: [id]
            })
            Toast(response.message);
            const remove = chatmembers.filter(member => member._id !== id)
            dispatch(chatMemberListAction(remove));
        } catch (error) {
            console.log('error: ', error);
        }
    }

    const socketChatMembers = async ({chatMembers,chatId}) => {
        setLoading(true)
        if (!chatMembers) return;
        try {
            dispatch(chatMemberListAction(chatMembers.data));
            const data = chatMembers.data.find((el) => el?.chatId == chatId && el.user.id == user._id)
            dispatch(setFavouriteAction(data?.isFavourite))
            dispatch(setChatMessageAction(data?.title));
            setChatList(data?.title);
            dispatch(setChatInfoAction(data));
           
        } catch (error) {
            console.log('error: socketChatMembers', error);
        }finally{
            setLoading(false)
        }
    };

    return {
        chatmembers,
        getChatMembers,
        favourite,
        favouriteChat,
        addChatMember,
        removeChatMember,
        register, 
        handleSubmit, 
        errors,
        control, 
        setFormValue, 
        reset,
        socketChatMembers,
        chatList,
        loading
    };
};

export default useChatMember;
