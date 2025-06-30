import React, { useState } from 'react';
import TabGptList from './TabGptList';
import Close from '@/icons/Close';

const AtreChatList = ({onSelectMenu, selectedContext, setUploadedFile, setText, closeSearch}) => {
    const [searchValue, setSearchValue] = useState('');
    const handleInputChanges = (e) => setSearchValue(e.target.value);
    return (
        <div className="chat-search-list z-[11] flex flex-col absolute bottom-full mb-2.5 w-full lg:max-w-[740px] bg-b15 shadow-[0_7px_15px_0_rgba(0,0,0,0.07)] border border-b11 rounded-10">
            <div className="search-gpt pt-3 px-2.5">
                <input
                    type="text"
                    name="searchgpt"
                    id="searchgpt"
                    placeholder="Search recent and pinned GPTs"
                    className="w-full px-2.5 bg-transparent text-font-16 font-semibold text-b2 placeholder:text-b7  outline-none"
                    onChange={handleInputChanges}
                    value={searchValue}
                />
                <button onClick={closeSearch} className='absolute top-3 right-3 p-1 size-5'>
                    <Close height={12} width={12} className="size-3 fill-b2 object-contain" />
                </button>
            </div>
            {/* <TabGptList search={searchValue} handleInputChanges={handleInputChanges} onSelect={onSelectMenu} selectedContext={selectedContext} setUploadedFile={setUploadedFile} setText={setText} fileInputRef={fileInputRef}/> */}
        </div>
    );
};

export default AtreChatList;
