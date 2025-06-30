'use client';
import React, { useState, useMemo } from 'react';
import {
    freeTrialDaysLeft,
    isEmptyObject,
    isSubscriptionActive,
} from '@/utils/common';
import {
    AI_MODEL_CODE,
} from '@/utils/constant';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedAIModal } from '@/lib/slices/aimodel/assignmodelslice';
import { RootState } from '@/lib/store';
import { useSearchParams } from 'next/navigation';
import { modelNameConvert } from '@/utils/common';
import { AiModalType } from '@/types/aimodels';
import { usePathname } from 'next/navigation';
import CircularProgress from './CircularProgress';
import { FREE_TRIAL } from '@/config/config';
import UserModalPopOver from './UserModalPopOver';

export const useDefaultModel = (aiModals) => {
    const selectedAIModal = useSelector(
        (store: RootState) => store.assignmodel.selectedModal
    );
    const findModel = aiModals.find(
        (el) => el.name === AI_MODEL_CODE.DEFAULT_OPENAI_SELECTED
    );
    const selectedModel = isEmptyObject(selectedAIModal)
        ? findModel
            ? findModel
            : aiModals[0]
        : selectedAIModal;
    const selectedModelName = selectedModel.name;
    const selectedModelCode = selectedModel.bot.code;
    return { selectedModelName, selectedModelCode, selectedModel };
};

const HomeAiModel = ({ aiModals }) => {
    const [open, setOpen] = useState(false);
    const dispatch = useDispatch();
    const queryParams = useSearchParams();
    const pathname = usePathname();

    const agent = queryParams.get('agent');
    const b = queryParams.get('b');
    const model = queryParams.get('model');

    const selectedAIModal = useSelector(
        (store: RootState) => store.assignmodel.selectedModal
    );
    const creditInfo = useSelector((store: RootState) => store.chat.creditInfo);
    const freeDaysLeft = useMemo(() => freeTrialDaysLeft(creditInfo), [creditInfo]);

    const handleModelChange = (model: AiModalType) => {
        setOpen(false);
        if (agent) return;
        const modelName = modelNameConvert(model.bot.code, model.name);
        history.pushState(null, '', `${pathname}?b=${b}&model=${modelName}`);
        dispatch(setSelectedAIModal(model));
    };

    const shouldShowProgress = useMemo(() => {
        return creditInfo?.freeTrialStartDate &&
               Object.keys(creditInfo).length > 0 &&
               !isSubscriptionActive(creditInfo.subscriptionStatus);
    }, [ creditInfo]);
    
    return (
        <>
            {aiModals?.length > 0 && model ? (
                 <div className="top-header md:h-[68px] min-h-[68px] flex md:border-b-0 border-b border-b10  items-center md:justify-between py-2 lg:pl-[15px] pl-[50px] pr-[15px]">
                    <div className="flex items-center">
                        <UserModalPopOver
                            open={open}
                            setOpen={setOpen}
                            selectedAIModal={selectedAIModal}
                            handleModelChange={handleModelChange}
                            userModals={aiModals}
                        />
                    </div>

                    {shouldShowProgress && (
                        <div className="flex items-center">
                            <CircularProgress
                                value={freeDaysLeft}
                                max={parseInt(FREE_TRIAL.DAYS)}
                                width={40}
                            />
                        </div>
                    )}
                </div>
            ) : null}
        </>
    );
};

export default HomeAiModel;
