import React from 'react';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import Label from '@/widgets/Label';

type SeoPrimaryKeywordProps = {
    selectedKeywords: string[];
    setPrimaryKeyword: (keyword: string) => void;
    primaryKeyword: string;
}

const SeoPrimaryKeyword = ({ selectedKeywords, setPrimaryKeyword, primaryKeyword }: SeoPrimaryKeywordProps) => {
    return (
        <div className="primary-keyword">
            <p className="text-font-14 text-center font-bold">
            Choose one keyword as your Primary Keyword; the rest will be Secondary Keywords.
            </p>
            <div className="primary-keyword mt-5">
                <RadioGroup
                    defaultValue="comfortable"
                    className="flex items-center flex-wrap gap-x-3 justify-center"
                    value={primaryKeyword}
                    onValueChange={setPrimaryKeyword}
                >
                {
                    selectedKeywords?.map((keyword, index) => (
                        <div className="flex items-center justify-center space-x-2" key={index}>
                            <RadioGroupItem value={keyword} id={`primary-${index}`} />
                            <Label
                                className="mb-0 text-font-14"
                                htmlFor={`primary-${index}`}
                                title={keyword}
                                required={false}
                            />
                        </div>
                    ))
                }
                </RadioGroup>
            </div>
        </div>
    );
};

export default SeoPrimaryKeyword;
