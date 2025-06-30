'use client';

import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { EXPIRED_SUBSCRIPTION_MESSAGE, FREE_TIER_END_MESSAGE, SUBSCRIPTION_STATUS } from '@/utils/constant';
import Close from '@/icons/Close';
import { isCreditLimitExceeded } from '@/utils/common';
import { RootState } from '@/lib/store';
const SubscriptionBanner = () => {
    const { subscriptionStatus, msgCreditLimit, msgCreditUsed } = useSelector(
        (state:RootState) => state.chat.creditInfo
    );

    const [isVisible, setIsVisible] = useState(true);

    const handleClose = () => {
        setIsVisible(false);
    };

    const renderMessage = () => {
        if (!subscriptionStatus && isCreditLimitExceeded(msgCreditLimit,msgCreditUsed)) {
            return FREE_TIER_END_MESSAGE;
        }
        if ([SUBSCRIPTION_STATUS.EXPIRED, SUBSCRIPTION_STATUS.CANCELED].includes(subscriptionStatus)) {
            return EXPIRED_SUBSCRIPTION_MESSAGE;
        }
        return null;
    };

    const message = renderMessage();

   return (
        isVisible &&
        message && (
            <div className="text-red-500 bg-yellow-200 py-3 flex items-center justify-between text-center md:text-left max-md:text-font-12 max-md:pl-4">
                <span className="ml-4">{message}</span>
                <button
                    onClick={handleClose}
                    className="ml-4 text-red-600 hover:text-red-800 mr-4"
                >
                    <Close className={'fill-black size-4'} />
                </button>
            </div>
        )
    );
};

export default SubscriptionBanner;
