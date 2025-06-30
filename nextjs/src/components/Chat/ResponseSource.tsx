import React from 'react';

const ResponseSource = ({ m }) => {
    return (
        <div className="bg-ligheter px-4 py-2 mt-4 rounded-10">
            <div className="font-semibold text-font-14">
                The answer is sourced from [Document Name].
            </div>
        </div>
    );
};

export default ResponseSource;
