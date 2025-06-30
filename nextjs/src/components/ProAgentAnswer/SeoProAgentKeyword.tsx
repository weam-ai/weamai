'use client';
import React, {
    useCallback,
    useEffect,
    useState,
    useRef
} from 'react';
import ScrollToBottomButton from '@/components/ScrollToBottomButton';
import MoveLeftIcon from '@/icons/MoveLeftIcon';
import Toast from '@/utils/toast';
import useProAgent from '@/hooks/conversation/useProAgent';
import { SeoKeywordLoader, SeoTopicLoader } from '../Loader/SeoArticleGenerationLoader';
import { keywordCheckBoxType, ProAgentDataResponseType } from '@/types/proAgents';
import SeoPrimaryKeyword from './SeoPrimaryKeyword';

type checkedType = (keywordCheckBoxType & { checked?: boolean, originalFromRight?: boolean });

type SeoProAgentKeywordProps = {
    isLoading: boolean;
    leftList: checkedType[];
    rightList: checkedType[];
    setLeftList: (leftList: checkedType[]) => void;
    setRightList: (rightList: checkedType[]) => void;
    setSelectedKeywords: (selectedKeywords: string[]) => void;
    messageId: string;
    setTopicName: (topicName: string) => void;
    proAgentData: ProAgentDataResponseType;
    primaryKeyword: string;
    setPrimaryKeyword: (primaryKeyword: string) => void;
}

const SeoProAgentKeyword = ({
    isLoading,
    leftList,
    rightList,
    setLeftList,
    setRightList,
    setSelectedKeywords,
    messageId, 
    setTopicName, 
    proAgentData, 
    primaryKeyword,
    setPrimaryKeyword
}: SeoProAgentKeywordProps) => {
    const contentRef = useRef(null);
    const { generateSeoTopicName, isLoading: isTopicGenerationLoading } = useProAgent();
    const [shouldScrollToBottom, setShouldScrollToBottom] = useState(true);
    const [showPrimaryKeyword, setShowPrimaryKeyword] = useState(false);


    const scrollToBottom = useCallback(() => {
        if (contentRef.current && shouldScrollToBottom) {
            contentRef.current.scrollTop = contentRef.current.scrollHeight;
        }
    }, [shouldScrollToBottom]);

    useEffect(() => {
        const handleScroll = () => {
            if (contentRef.current) {
                const { scrollTop, scrollHeight, clientHeight } =
                    contentRef.current;
                const isAtBottom =
                    Math.abs(scrollHeight - scrollTop - clientHeight) < 10;
                setShouldScrollToBottom(isAtBottom);
            }
        };

        if (contentRef.current) {
            contentRef.current.addEventListener('scroll', handleScroll);
            scrollToBottom();
        }

        return () => {
            if (contentRef.current) {
                contentRef.current.removeEventListener('scroll', handleScroll);
            }
        };
    }, [scrollToBottom]);

    useEffect(() => {
        scrollToBottom();
    }, [scrollToBottom]);

    useEffect(() => {
        if(proAgentData.hasOwnProperty('step3')){
            setLeftList(proAgentData?.step2?.targeted_volumes);
            setRightList(proAgentData?.step2?.recommended_volumes);
        }
    }, [proAgentData]);

    const handleCheck = (item: checkedType, fromLeft: boolean) => {
        if (!fromLeft) {
          setRightList(rightList.filter((i) => i.id !== item.id));
          setLeftList([...leftList, { ...item, checked: true, originalFromRight: true }]);
        } else {
          if (item.originalFromRight) {
            if (item.checked) {
              setLeftList(leftList.filter((i) => i.id !== item.id));
              setRightList([...rightList, { ...item, checked: false }]);
            } else {
              setLeftList(leftList.map((i) => i.id === item.id ? { ...i, checked: true } : i));
            }
          } else {
            setLeftList(leftList.map((i) => i.id === item.id ? { ...i, checked: !i.checked } : i));
          }
        }
    };

    const renderList = (list: checkedType[], fromLeft: boolean) =>
        list.map((item) => {
            return (
                <div key={item.id} className="my-3 pl-6">
                    <input
                        className="input-checkbox"
                        type="checkbox"
                        id={item.id}
                        checked={item.checked}
                        onChange={() => handleCheck(item, fromLeft)}
                    />
                    <label
                        className={`inline-block ps-[0.15rem] hover:cursor-pointer font-bold text-font-14 ${
                            fromLeft ? 'text-white' : 'text-b2'
                        }`}
                        htmlFor={item.id}
                    >
                        {item.keyword}
                    </label>
                    <p
                        className={`text-font-14 ${
                            fromLeft ? 'text-b10' : 'text-b5'
                        }`}
                    >
                        Search Volume: <span>{item.search_volume}</span> | Competition:
                        <span> {item.competition}</span>
                    </p>
                </div>
            );
    });
    
    const handleKeywords = async () => {
        if (!primaryKeyword) {
            Toast('Please select primary keyword', 'error'); 
            return;
        }
            const secondaryKeywords = leftList?.reduce((acc, item) => {
                if(item.checked){
                    acc.push(item.keyword);
                }
                return acc;
            }, []);
            const response = await generateSeoTopicName({ messageId, secondaryKeywords, primaryKeyword });
            if (response) {
                setTopicName(response.data.topics);
                setSelectedKeywords(secondaryKeywords);
            }
    };

    const handlePrimaryKeyword = useCallback(() => {
        const checkedCount = leftList?.find((item) => item?.checked);
        if (!checkedCount) {
            Toast('Please select at least one keyword', 'error'); 
            return;
        } else {
            setShowPrimaryKeyword(true);
        }
    }, [leftList]);

    return (
        <div className="flex flex-col flex-1 h-full relative overflow-hidden">
            <div
                ref={contentRef}
                className="pb-8 pt-4 mt-[68px]123 h-full overflow-y-auto w-full relative"
            >
                <div className="chat-item w-full px-4 lg:py-3 py-2 lg:gap-6 m-auto md:max-w-[32rem] lg:max-w-[40rem] xl:max-w-[48.75rem]">
                    {isLoading &&
                        <SeoKeywordLoader />
                    }
                    {
                        isTopicGenerationLoading &&
                            <SeoTopicLoader />
                    }
                    {!isLoading && !isTopicGenerationLoading && (
                        <>
                            {leftList?.length > 0 ?
                                <> 
                                    {
                                        !showPrimaryKeyword && (
                                            <>
                                                <div className='mx-auto'>
                                                    <p className='text-font-14 text-center mb-2'>Check a box to use a keyword in your content. Uncheck it to remove the keyword.</p>
                                                    <MoveLeftIcon width={40} height={40} className='w-10 h-auto fill-b2 mx-auto' />
                                                </div>
                                                <div className="relative bg-white text-b2 mx-auto flex gap-x-5">
                                                    <div className="border p-5 rounded-md w-1/2 shadow-2xl bg-b2">
                                                        <p className="font-bold text-font-14 text-white mb-5">Targeted Keywords</p>
                                                        {leftList?.length > 0 ? renderList(leftList, true) : <NoKeywordsFound />}
                                                    </div>
                                                    <div className="border p-5 rounded-md w-1/2">
                                                        <p className="font-bold text-font-14 mb-5">Recommended Keywords</p>
                                                        {rightList?.length > 0 ? renderList(rightList, false) : <NoKeywordsFound />}
                                                    </div>
                                                </div>
                                            </>
                                        )
                                    }
                                    {showPrimaryKeyword && 
                                        <>
                                            <SeoPrimaryKeyword selectedKeywords={leftList?.reduce((acc, item) => {
                                                if(item.checked){
                                                    acc.push(item.keyword);
                                                }
                                                return acc;
                                            }, [])} setPrimaryKeyword={setPrimaryKeyword} primaryKeyword={primaryKeyword} />
                                            <div className="flex justify-center gap-3 mt-5">
                                                <button className="btn btn-outline-black" 
                                                    onClick={handleKeywords}
                                                    disabled={isTopicGenerationLoading}
                                                >
                                                    Save
                                                </button>
                                            </div>
                                        </>
                                    }
                                    {
                                        !showPrimaryKeyword && (
                                            <div className="flex justify-center gap-3 mt-5">
                                                <button className="btn btn-outline-black" onClick={handlePrimaryKeyword}>
                                                    Next
                                                </button>
                                            </div>
                                        )
                                    }
                                </>
                                : <NoKeywordsFound />
                            }
                        </>
                    )}                    
                </div>
            </div>
            {!isLoading && (
                <>
                    <ScrollToBottomButton contentRef={contentRef} />
                </>
            )}            
        </div>
    );
};

const NoKeywordsFound = () => {
    return (
        <div className='mx-auto'>
            <p className='text-font-14 text-left'>No keywords found</p>
        </div>
    );
}

export default SeoProAgentKeyword;
