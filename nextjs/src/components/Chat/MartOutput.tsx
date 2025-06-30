import { useState } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus as dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import CopyToClipboard from 'react-copy-to-clipboard';
import CopyIcon from '@/icons/CopyIcon';
import CheckIcon from '@/icons/CheckIcon';
import { useEffect } from 'react';

const CodeBlock = (props) => {
    const { children, className, node, ...rest } = props;
    const isInline = !className;
    const match = /language-(\w+)/.exec(className || '');
    const language = match?.input?.replace('language-', '');

    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
    };
    if (isInline) {
        const text = Array.isArray(children) ? children.join('') : children;
        return (
            <code
                className="px-1 py-0.5 rounded bg-[#ECECEC] text-[#2D2D2D] text-sm font-mono"
                {...props}
            >
                {text}
            </code>
        );
    }

    return (
        <>
            {match ? (
                <>
                    <div className="flex justify-between px-3 align-middle pt-1">
                        <p className="language-text">{language}</p>
                        <CopyToClipboard text={children} onCopy={handleCopy}>
                            <div className="flex">
                                {copied ? (
                                    <span className="language-text">
                                        <CheckIcon
                                            width={12}
                                            height={12}
                                            className="mr-2 inline-block [&>path]:fill-gray-200"
                                        />
                                        Copied!
                                    </span>
                                ) : (
                                    <span className="cursor-pointer language-text">
                                        <CopyIcon
                                            width={15}
                                            height={15}
                                            className="mr-2 inline-block [&>path]:fill-gray-200"
                                        />
                                        copy
                                    </span>
                                )}
                            </div>
                        </CopyToClipboard>
                    </div>
                    <SyntaxHighlighter
                        PreTag="div"
                        language={match[1]}
                        style={dark}
                        wrapLines={true}
                        wrapLongLines={true}
                    >
                        {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                </>
            ) : (
                <code {...rest} className={className}>
                    {children}
                </code>
            )}
        </>
    );
};

export const MarkOutPut = (assisnantResponse: string) => {
    return (
        <div className="markdown w-full mx-auto flex-1 overflow-y-auto prose">
            <Markdown
                remarkPlugins={[remarkGfm]}
                components={{
                    // Override how links <a> are rendered
                    code: CodeBlock,
                    a: ({ children, href, ...props }) => {
                        // children is normally an array of strings/elements
                        // e.g. if the markdown is [1](https://google.com)
                        // the displayed text is '1'
                        const linkText = children[0];

                        // Check if linkText is purely numeric (like "1", "2", "3"...)
                        const isNumericRef = /^\d+$/.test(linkText);

                        // If numeric, style as a circle
                        if (isNumericRef) {
                            return (
                                <a
                                    href={href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center justify-center 
                               size-[18px] text-font-12 bg-b12 mr-1 mb-1 text-sm font-medium 
                               rounded-full 
                               text-b2"
                                    {...props}
                                >
                                    {linkText}
                                </a>
                            );
                        }

                        // Otherwise, render normal link
                        return (
                            <a
                                href={href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 underline"
                                {...props}
                            >
                                {children}
                            </a>
                        );
                    },
                }}
            >
                {assisnantResponse}
            </Markdown>
        </div>
    );
};
