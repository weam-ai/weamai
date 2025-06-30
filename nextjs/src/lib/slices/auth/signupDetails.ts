const { createSlice } = require('@reduxjs/toolkit');

const signupDetails = createSlice({
    name: 'signup',
    initialState: {
        details: {},
        summary: {},
        countryList: [],
        stateList: [],
        cityList: [],
        payment: {},
        plan: {
            price: 0
        }
    },
    reducers: {
        addDetails: (state, action) => {
            state.details = action.payload;
        },
        addSummary: (state, action) => {
            state.summary = action.payload
        },
        cacheCountry: (state, action) => {
            state.countryList = action.payload
        },
        cacheState: (state, action) => {
            state.stateList = action.payload
        },
        cacheCity: (state, action) => {
            state.cityList = action.payload
        },
        addPayment: (state, action) => {
            state.payment = action.payload
        },
        addPlan: (state, action) => {
            state.plan.price = action.payload
        }
    },
});

export const { addDetails, addSummary, cacheCity, cacheCountry, cacheState, addPayment, addPlan } = signupDetails.actions;

export default signupDetails.reducer;
