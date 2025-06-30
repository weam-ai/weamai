import CommonInput from '@/widgets/CommonInput';
import Label from '@/widgets/Label';
import ValidationError from '@/widgets/ValidationError';
import { isEmptyObject } from '@/utils/common';

const CompanyProfile =
    ({ register, watch, setValue, getValues, errors }) => {
        const websites = watch('companyInfo.website') || [];
        const scrapeSummaries = watch('companyInfo.summaries') || {};

        const addNewTextInput = () => {
            setValue('companyInfo.website', [
                ...getValues('companyInfo.website'),
                '',
            ]);
        };

        const removeInput = (index) => {
            const newItems = [...getValues('companyInfo.website')];
            newItems.splice(index, 1);
            setValue('companyInfo.website', newItems);
        };

        return (
            <div className="brand-additional-info">
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Company Name'}
                        htmlFor={'company-name'}
                        required={false}
                    />
                    <CommonInput
                        placeholder={'Company Name'}
                        {...register('companyInfo.name')}
                        value={watch('companyInfo.name')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'companyInfo.name'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Company Slogan/Tagline'}
                        htmlFor={'company-slogan'}
                        required={false}
                    />
                    <CommonInput
                        placeholder={'Company Slogan/Tagline'}
                        {...register('companyInfo.tagline')}
                        value={watch('companyInfo.tagline')}
                    />

                    <ValidationError
                        errors={errors}
                        field={'companyInfo.tagline'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Company Mission'}
                        htmlFor={'company-mission'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Company Mission"
                        maxLength={400}
                        {...register('companyInfo.mission')}
                        value={watch('companyInfo.mission')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'companyInfo.mission'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Company Values'}
                        htmlFor={'company-values'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Company Values"
                        maxLength={400}
                        {...register('companyInfo.values')}
                        value={watch('companyInfo.values')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'companyInfo.values'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Company Overview'}
                        htmlFor={'company-overview'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Company Overview"
                        maxLength={400}
                        {...register('companyInfo.overview')}
                        value={watch('companyInfo.overview')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'companyInfo.overview'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Company Vision'}
                        htmlFor={'companyvision'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Company Vision"
                        maxLength={400}
                        {...register('companyInfo.vision')}
                        value={watch('companyInfo.vision')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'companyInfo.vision'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label title={'Industry'} htmlFor={'industry'} required={false} />
                    <CommonInput
                        placeholder={'Industry'}
                        {...register('companyInfo.industry')}
                        value={watch('companyInfo.industry')}
                    />

                    <ValidationError
                        errors={errors}
                        field={'companyInfo.industry'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label title={'Headquarter'} htmlFor={'headquarter'} required={false} />
                    <CommonInput
                        placeholder={'Headquarter'}
                        {...register('companyInfo.headquarter')}
                        value={watch('companyInfo.headquarter')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'companyInfo.headquarter'}
                    ></ValidationError>
                </div>
                {/* <div className="relative mb-4">
                    <Label title={'Website'} htmlFor={'website-url'} required={false} />
                    {websites.map((_, index) => (
                        <div className="goal-input-wrap relative mt-2.5" key={index}>
                            <CommonInput
                                className={'default-form-input !pr-10'}
                                {...register(`companyInfo.website.${index}`)}
                                value={watch(`companyInfo.website.${index}`)}
                            />
                            <ValidationError
                                errors={errors}
                                field={`companyInfo.website.${index}`}
                            />

                            {websites.length > 1 && index > 0 && (
                                <button
                                    type="button"
                                    className="goal-input-remove absolute top-0 right-0 h-[50px] p-3"
                                    onClick={() => removeInput(index)}
                                >
                                    <Image
                                        src={CloseIcon}
                                        width={12}
                                        height={12}
                                        alt="close"
                                    />
                                </button>
                            )}
                        </div>
                    ))}
                    <ValidationError errors={errors} field={'companyInfo.website'} />

                    <button
                        className="btn btn-gray mt-2.5"
                        type="button"
                        onClick={addNewTextInput}
                    >
                        <PlusRound
                            className="inline-block mr-2.5 [&>circle]:fill-b15 [&>path]:fill-w13"
                            width="22"
                            height="22"
                        />
                        Add
                    </button>
                </div> */}
                {
                    !isEmptyObject(scrapeSummaries) &&
                    <>
                        <div className="relative mb-4 flex-1">
                            <Label title={'Summaries'} htmlFor={'Summaries'} required={false} />
                            {
                                websites.reduce((accumulator, current) => {
                                    const matchingEntry = Object.entries(scrapeSummaries).find(([_key, ele]:any) => ele.website === current);
                                    if (matchingEntry) {
                                        const [key] = matchingEntry;
                                        accumulator.push(
                                            <CommonInput
                                                className={'mb-2 default-form-input'}
                                                key={key}
                                                placeholder={'Summaries'}
                                                {...register(`companyInfo.summaries.${key}.summary`)}
                                                value={watch(`companyInfo.summaries.${key}.summary`)}
                                            />
                                        )
                                        return accumulator
                                    }
                                }, [])
                            }
                        </div>

                    </>
                }
            </div>
        );
    }
;

export default CompanyProfile;
