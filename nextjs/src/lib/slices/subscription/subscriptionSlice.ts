import { createSlice } from '@reduxjs/toolkit';

type InitialStateProps = {
    paymentStatus: boolean,
    modalStatus: boolean,
    reloadSubscription: boolean
}

const initialState: InitialStateProps = {
    paymentStatus: false,
    modalStatus: false,
    reloadSubscription: false
}

const subscription = createSlice({
    name: 'subscription',
    initialState,
    reducers: {
        setPaymentStatus: (state, action) => {
            state.paymentStatus = action.payload;
        },
        setModalStatus: (state, action) => {
            state.modalStatus = action.payload;
        },
        setReloadSubscription: (state, action) => {
            state.reloadSubscription = action.payload;
        }
    },
});

export const {
    setPaymentStatus,
    setModalStatus,
    setReloadSubscription
} = subscription.actions;

export default subscription.reducer; 