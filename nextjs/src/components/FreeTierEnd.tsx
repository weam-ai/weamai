'use client';
import { FEATURES_WEAM } from '@/utils/constant';
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import PurpleTick from '@/icons/PurpleTick';
import React, { useEffect, useState, useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import routes from '@/utils/routes';
import { useSelector } from 'react-redux';
import { freeTrialDaysLeft, isFreeTierSubscription } from '@/utils/common';
import { RootState } from '@/lib/store';
import { getCurrentUser } from '@/utils/handleAuth';
import { PERMISSIONS } from '@/utils/permission';
import { hasPermission } from '@/utils/permission';
import { LINK } from '@/config/config';

export const FreeTierEnd = () => {
    const [open, setOpen] = useState(false);

    const router = useRouter();
    const pathname = usePathname();
    const creditInfo = useSelector((store: RootState) => store.chat.creditInfo);
    const user = useMemo(() => getCurrentUser(), []);
    useEffect(() => {
        if (
            (creditInfo?.freeTrialStartDate &&
                freeTrialDaysLeft(creditInfo) === 0) ||
                isFreeTierSubscription(creditInfo?.subscriptionStatus) && creditInfo.msgCreditUsed >= creditInfo.msgCreditLimit
            // (creditInfo?.subscriptionStatus == undefined || creditInfo?.subscriptionStatus == null)
        ) {
            setOpen(true);
        } else {
            setOpen(false);
        }
    }, [pathname, creditInfo]);

    if (
        pathname === routes.settingSubscription ||
        pathname === "/settings/reports" ||
        pathname === routes.testSubscription
    ) {
        return null;
    }

    return (
        <>
            {Object.keys(creditInfo).length > 0 && (
                <Dialog open={open}>
                    <DialogContent className="md:max-w-[700px] max-w-[calc(100%-30px)] py-7 border-none" showCloseButton={false}>
                        <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
                            <DialogTitle className="font-bold text-font-20 flex justify-center">
                                Your Free Trial Has Ended
                            </DialogTitle>
                            <DialogDescription className="text-center text-xs text-gray-500">
                                Thanks for giving Weam a try!
                            </DialogDescription>
                        </DialogHeader>

                        <div className="px-5 md:px-10 py-5 rounded-b-10">
                            <FeatureList />
                        </div>

                        <div className="flex justify-center mt-4 gap-2">
                            <button
                                type="button"
                                className="px-5 py-3 btn btn-outline-gray"
                                onClick={(e) => {
                                    e.preventDefault();
                                    window.open(
                                        LINK.WEAM_PRICING_URL,
                                        '_blank',
                                        'noopener,noreferrer'
                                    );
                                }}
                            >
                                Learn More
                            </button>

                            {hasPermission(
                                user?.roleCode,
                                PERMISSIONS.UPGRADE_PLAN
                            ) && (
                                <button
                                    type="button"
                                    className="px-5 py-3 btn btn-blue text-white rounded-md hover:bg-blue-700"
                                    onClick={() =>
                                        router.push(routes.settingSubscription)
                                    }
                                >
                                    Upgrade Now
                                </button>
                            )}
                        </div>

                        <DialogFooter className="flex justify-center mt-4 font-semibold">
                            {hasPermission(
                                user?.roleCode,
                                PERMISSIONS.UPGRADE_PLAN
                            ) ? (
                                <>
                                    Need help?{' '}
                                    <a
                                        href={LINK.FRESHDESK_SUPPORT_URL}
                                        className="text-md text-b text-purple ml-1"
                                        target="_blank"
                                    >
                                        Contact our support team
                                    </a>
                                </>
                            ) : (
                                'Please contact your admin to upgrade the plan for uninterrupted Weam usage.'
                            )}
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            )}
        </>
    );
};

export default function FeatureList() {
    return (
        <div className="bg-purple/10 p-5 md:p-10 rounded-[10px] shadow-lg max-w-2xl mx-auto max-h-[60vh] overflow-y-auto border-1 border-gray-900/20">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                {FEATURES_WEAM.map((feature, index) => (
                    <FeatureItem key={index} title={feature.title}>
                        {feature.description}
                    </FeatureItem>
                ))}
            </div>
        </div>
    );
}

function FeatureItem({
    title,
    children,
}: {
    title: string;
    children: React.ReactNode;
}) {
    return (
        <div className="flex items-start space-x-3">
            <span className="text-purple-600 text-xl mt-1">
                <PurpleTick
                    height={14}
                    width={14}
                    className="fill-purple"
                    fill="#6637EC"
                />
            </span>
            <div>
                <h3 className="font-semibold text-gray-900">{title}</h3>
                <p className="text-gray-600 hidden md:block">{children}</p>
            </div>
        </div>
    );
}
