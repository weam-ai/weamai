import { createSlice } from '@reduxjs/toolkit';

const notificationSlice = createSlice({
    name: 'notification',
    initialState: {
        unread: [],
        unreadcount: 0
    },
    reducers: {
        setUnreadNotification: (state, action) => {
            state.unread = action.payload;
            // state.unread = [...state.unread, ...action.payload];
        },
        setUnreadCount: (state, action) => {
            state.unreadcount = action.payload
        }
    },
});

export const { setUnreadNotification, setUnreadCount } = notificationSlice.actions;

export default notificationSlice.reducer;
