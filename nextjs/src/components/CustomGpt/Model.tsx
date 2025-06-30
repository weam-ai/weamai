import React, { useEffect } from 'react';
import Select from 'react-select';
import Label from '@/widgets/Label';
import ArrowBack from '@/icons/ArrowBack';
import ArrowNext from '@/icons/ArrowNext';
import useAssignModalList from '@/hooks/aiModal/useAssignModalList';
import { modalSelectionKeys } from '@/schema/customgpt';
import { useFormik } from "formik";
import FormikError from '@/widgets/FormikError';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import TooltipIcon from '@/icons/TooltipIcon';
import { AI_MODAL_NAME, API_TYPE_OPTIONS } from '@/utils/constant';
import { getDisplayModelName } from '@/utils/helper';

const CUSTOM_BOT_IGNORE_MODAL = [
    AI_MODAL_NAME.SONAR,
    AI_MODAL_NAME.SONAR_REASONING_PRO
];

const Model = ({ onNext, onPrev, customGptData, setCustomGptData }) => {
    const { userModalList, userModals } = useAssignModalList();
    const formik = useFormik({
        initialValues: customGptData,
        validationSchema: modalSelectionKeys,
        onSubmit: async ({ responseModel, maxItr, itrTimeDuration, imageEnable }) => {
            setCustomGptData({ ...customGptData, responseModel, maxItr, itrTimeDuration, imageEnable });
            onNext();
        },
    });


    const {
        errors,
        touched,
        values,
        handleSubmit,
        setFieldValue,
    } = formik;

    useEffect(() => {
        userModalList();
    }, []);

    return (
        <>
        {userModals && <div>
            <form onSubmit={handleSubmit}>
                <div className="relative mb-5">
                <div className="flex items-center">
                        <Label htmlFor={'model'} title={'Model'} />
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <span className="cursor-pointer mb-2 ml-1 inline-block">
                                        <TooltipIcon
                                            width={15}
                                            height={15}
                                            className={
                                                'w-[15px] h-[15px] object-cover inline-block fill-b7'
                                            }
                                        />
                                    </span>
                                </TooltipTrigger>
                                <TooltipContent className="border-none">
                                    <p className="text-font-14">{`Select the model for generating responses for your agents.`}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </div>
                    <Select
                        options={userModals?.reduce((accumulator, current) => {
                            if (!CUSTOM_BOT_IGNORE_MODAL.includes(current.name) && !current.isDisable) {
                                accumulator.push({
                                    value: getDisplayModelName(current.name),
                                    label: getDisplayModelName(current.name),
                                    id: current._id,
                                    company: current.company,
                                    isDisabled:current.isDisable || false,
                                    provider: current?.provider,
                                    bot: current.bot,
                                    name: current.name,
                                })
                            }
                            return accumulator;
                        }, [])}
                        id="model"
                        className="react-select-container"
                        classNamePrefix="react-select"
                        name="responseModel"
                        onChange={(value)=>{
                            setFieldValue('responseModel',value);
                        }}
                        value={values.responseModel}
                        isOptionDisabled={(option)=> option.isDisabled}
                        styles={{
                            option: (provided, option) => ({
                              ...provided,
                              cursor: option.isDisabled ? 'not-allowed' : 'pointer',
                            })
                          }}
                    />
                    {touched.responseModel && <FormikError errors={errors} field={'responseModel'} />}

                    {values.responseModel?.bot?.code === API_TYPE_OPTIONS.OPEN_AI && (
                        <div className="mt-4">
                            <Label htmlFor={'imageEnable'} title={'Capabilities'} required={false} />
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    className="form-checkbox h-4 w-4 text-blue-600"
                                    checked={values?.imageEnable || false}
                                    onChange={(e) => setFieldValue('imageEnable', e.target.checked)}
                                />
                                <span className="ml-2">Image Generation</span>
                            </label>
                        </div>
                    )}

                </div>
                <div className="flex justify-between mt-5">
                    <button
                        type="button"
                        onClick={onPrev}
                        className="btn btn-outline-gray"
                    >
                        <ArrowBack
                            className="me-2.5 inline-block align-middle -mt-0.5 fill-b15"
                            width="14"
                            height="12"
                        />
                        Previous
                    </button>
                    <button type="submit" className="btn btn-blue">
                        Next
                        <ArrowNext
                            width="14"
                            height="12"
                            className="fill-b15 ms-2.5 inline-block align-middle -mt-0.5"
                        />
                    </button>
                </div>
            </form>
        </div>}
        </>
    );
};

export default Model;
