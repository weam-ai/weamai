import CommonInput from '@/widgets/CommonInput';
import Label from '@/widgets/Label';
import ValidationError from '@/widgets/ValidationError';
import { isEmptyObject } from '@/utils/common';

const ProductProfile =
    ({ register, watch, setValue, getValues, errors }) => {
        const websites = watch('productInfo.website') || [];
        const scrapeSummaries = watch('productInfo.summaries') || {};
        const addNewTextInput = () => {
            setValue('productInfo.website', [...getValues('productInfo.website'), '']);
        };

        const removeInput = (index) => {
            const newItems = [...getValues('productInfo.website')];
            newItems.splice(index, 1);
            setValue('productInfo.website', newItems);
        };

        return (
            <div className="brand-additional-info">
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Product Name'}
                        htmlFor={'product-name'}
                        required={false}
                    />
                    <CommonInput
                        placeholder={'Product Name'}
                        {...register('productInfo.name')}
                        value={watch('productInfo.name')}
                    />
                    <ValidationError
                        errors={errors}
                        field={'productInfo.name'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Product Category'}
                        htmlFor={'product-category'}
                        required={false}
                    />
                    <CommonInput
                        placeholder={'Product Category'}
                        {...register('productInfo.category')}
                        value={watch('productInfo.category')}
                    />

                    <ValidationError
                        errors={errors}
                        field={'productInfo.category'}
                    ></ValidationError>
                </div>

                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Product Description'}
                        htmlFor={'product-description'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Product Description"
                        {...register('productInfo.description')}
                        value={watch('productInfo.description')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'productInfo.description'}
                    ></ValidationError>
                </div>
                
                <div className="relative mb-4 flex-1">
                    <Label title={'USP'} htmlFor={'usp'} required={false} />
                    <textarea
                        className="default-form-input"
                        placeholder="USP"
                        {...register('productInfo.usp')}
                        value={watch('productInfo.usp')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'productInfo.usp'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label title={'SKUS'} htmlFor={'SKUS'} required={false} />
                    <textarea
                        className="default-form-input"
                        placeholder="SKUS"
                        {...register('productInfo.skus')}
                        value={watch('productInfo.skus')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'productInfo.skus'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label
                        title={'Specification'}
                        htmlFor={'specification'}
                        required={false}
                    />
                    <textarea
                        className="default-form-input"
                        placeholder="Specification"
                        {...register('productInfo.specification')}
                        value={watch('productInfo.specification')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'productInfo.specification'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label title={'Benifits'} htmlFor={'benifits'} required={false} />
                    <textarea
                        className="default-form-input"
                        placeholder="Benifits"
                        {...register('productInfo.benifits')}
                        value={watch('productInfo.benifits')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'productInfo.benifits'}
                    ></ValidationError>
                </div>
                <div className="relative mb-4 flex-1">
                    <Label title={'Usage'} htmlFor={'usage'} required={false} />
                    <textarea
                        className="default-form-input"
                        placeholder="Usage"
                        {...register('productInfo.usage')}
                        value={watch('productInfo.usage')}
                    ></textarea>
                    <ValidationError
                        errors={errors}
                        field={'productInfo.usage'}
                    ></ValidationError>
                </div>
                {/* <div className="relative mb-4">
                    <Label title={'Website'} htmlFor={'website-url'} required={false} />
                    {websites.map((_, index) => (
                        <div className="goal-input-wrap relative mt-2.5" key={index}>
                            <CommonInput
                                className={'default-form-input !pr-10'}
                                {...register(`productInfo.website.${index}`)}
                                value={watch(`productInfo.website.${index}`)}
                            />
                            <ValidationError
                                errors={errors}
                                field={`productInfo.website.${index}`}
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
                    <ValidationError errors={errors} field={'productInfo.website'} />

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
                                    const matchingEntry = Object.entries(scrapeSummaries).find(([_key, ele] :any) => ele.website === current);
                                    if (matchingEntry) {
                                        const [key] = matchingEntry;
                                        accumulator.push(
                                            <CommonInput
                                                className={'mb-2 default-form-input'}                                            
                                                key={key}
                                                placeholder={'Summaries'}
                                                {...register(`productInfo.summaries.${key}.summary`)}
                                                value={watch(`productInfo.summaries.${key}.summary`)}
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

export default ProductProfile;
