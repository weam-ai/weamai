import CommonInput from '@/widgets/CommonInput';
import ValidationError from '@/widgets/ValidationError';
import Label from '@/widgets/Label';
import { isEmptyObject } from '@/utils/common';
import TooltipIcon from '@/icons/TooltipIcon';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';


const BrandProfile =
    ({ register, watch, setValue, getValues, errors }) => {
        const websites = watch('brandProfile.website') || [];
        const scrapeSummaries = watch('brandProfile.summaries') || {};
        const addNewTextInput = () => {
            setValue('brandProfile.website', [...getValues('brandProfile.website'), '']);
        };

        const removeInput = (index) => {
            const newItems = [...getValues('brandProfile.website')];
            newItems.splice(index, 1);
            setValue('brandProfile.website', newItems);
        };

        return (
            <div className="brand-additional-info">
                <div className="relative mb-4 flex-1">
                    <Label title={'Brand Name'} htmlFor={'brand-name'} required={false} />
                    <CommonInput
                        placeholder={'Brand Name'}
                        {...register('brandProfile.name')}
                        value={watch('brandProfile.name')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'brandProfile.name'}
                    />
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Brand Slogan/Tagline'}
                        htmlFor={'brand-slogan'}
                        required={false}
                    />
                    <CommonInput
                        placeholder={'Brand Slogan/Tagline'}
                        {...register('brandProfile.tagline')}
                        value={watch('brandProfile.tagline')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'brandProfile.tagline'}
                    />
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Brand Mission'}
                        htmlFor={'brand-mission'}
                        required={false}
                    />
                     <textarea
                        className="default-form-input"
                        placeholder="Brand Mission"
                        {...register('brandProfile.mission')}
                        value={watch('brandProfile.mission')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'brandProfile.mission'}
                    />
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Brand Values'}
                        htmlFor={'brand-values'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Brand Values"
                        {...register('brandProfile.values')}
                        value={watch('brandProfile.values')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'brandProfile.values'}
                    />
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Target Audience'}
                        htmlFor={'target-audience'}
                        required={false}
                    />
                    <CommonInput
                        placeholder={'Target Audience'}
                        {...register('brandProfile.audience')}
                        value={watch('brandProfile.audience')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'brandProfile.audience'}
                    />
                </div>
                <div className="relative mb-4 flex-1">
                    <Label title={'Industry'} htmlFor={'industry-input'} required={false} />
                    <CommonInput
                        placeholder={'Industry'}
                        {...register('brandProfile.industry')}
                        value={watch('brandProfile.industry')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'brandProfile.industry'}
                    />
                </div>
                {/* <div className="relative mb-4">
                    <Label title={'Website'} htmlFor={'website-url'} required={false} />
                    {websites.map((_, index) => (
                        <div className="goal-input-wrap relative mt-2.5" key={index}>
                            <CommonInput
                                className={'default-form-input !pr-10'}
                                {...register(`brandProfile.website.${index}`)}
                                value={watch(`brandProfile.website.${index}`)}
                            />
                            <ValidationError
                                errors={errors}
                                field={`brandProfile.website.${index}`}
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
                    <ValidationError errors={errors} field={'brandProfile.website'} />

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
                        <Label title={'Summaries'} htmlFor={'Summaries'} required={false} className='text-font-16 font-semibold mb-2 text-b2 inline-block' />
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                <button >
                                    <TooltipIcon width={20} height={20} className={'w-5 h-5 object-cover inline-block fill-b7'} />
                                </button>
                                </TooltipTrigger>
                                <TooltipContent className="border-none">
                                <p>This will contain a summary derived from the scraped data of your website.</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                            
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
                                                {...register(`brandProfile.summaries.${key}.summary`)}
                                                value={watch(`brandProfile.summaries.${key}.summary`)}
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

export default BrandProfile;
