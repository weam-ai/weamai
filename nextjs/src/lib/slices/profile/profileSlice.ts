import { createSlice } from '@reduxjs/toolkit';

const profileSlice = createSlice({
    name: 'profile',
    initialState: {
        profileImg: ''
    },
    reducers: {
        setProfileImgAction: (state, action) => {
            state.profileImg = action.payload;
        }
    },
});

export const {
    setProfileImgAction
} = profileSlice.actions;

export default profileSlice.reducer;
