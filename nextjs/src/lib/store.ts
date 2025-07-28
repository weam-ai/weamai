import { configureStore, Middleware } from '@reduxjs/toolkit';
import detailReducer from './slices/auth/signupDetails';
import workspaceReducer from './slices/workspace/workspacelist';
import brainReducer from './slices/brain/brainlist';
import modalSliceReducer from './slices/modalSlice';
import aiModalReducer from './slices/aimodel/aimodel';
import chatReducer from './slices/chat/chatSlice';
import assignModelReducer from './slices/aimodel/assignmodelslice';
import conversationReducer from './slices/aimodel/conversation';
import promptSlice from './slices/prompt/promptSlice';
import profileSlice from './slices/profile/profileSlice';
import notificationSlice from './slices/notificationSlice';
import subscriptionReducer from './slices/subscription/subscriptionSlice';
import mcpReducer from './slices/mcpSlice';

const errorLoggerMiddleware: Middleware = ((store) => next => action => {
    try {
        return next(action);
    } catch (err) {
        console.error('Redux Error:', err);
    }
})

const store = configureStore({
    reducer: {
        signup: detailReducer,
        workspacelist: workspaceReducer,
        brain: brainReducer,
        modalSlice : modalSliceReducer,
        aiModal: aiModalReducer,
        chat: chatReducer,
        assignmodel: assignModelReducer,
        conversation: conversationReducer,
        prompt: promptSlice,
        profile: profileSlice,
        notification: notificationSlice,
        subscription: subscriptionReducer,
        mcp: mcpReducer
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(errorLoggerMiddleware)
});

export type RootState = ReturnType<typeof store.getState>;
export type ActionPayload = typeof store.dispatch;
export default store;
