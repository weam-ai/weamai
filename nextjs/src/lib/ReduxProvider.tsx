'use client';

import { Provider } from 'react-redux';
import store from './store';

type ReduxProviderProps = {
    children: React.ReactNode;
};

const ReduxProvider = ({ children }: ReduxProviderProps) => {
    return <Provider store={store}>{children}</Provider>;
};

export default ReduxProvider;
