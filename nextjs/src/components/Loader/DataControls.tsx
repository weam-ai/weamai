type DataControlsProps = {
    items: number;
}

export function DataControls({ items = 1 }: DataControlsProps) {
    return (
        <div role="status" className="w-full animate-pulse lg:px-5 px-3 overflow-x-auto">
            <div className="h-9 bg-b11 dark:bg-black w-full mb-4"></div>
            {
                Array.from({ length: items }).map((_, index) => (
                    <div className='flex w-full gap-3 items-center' key={index}>
                        <div className="h-2 rounded-lg bg-b11 dark:bg-black mb-2.5 w-1/3 "></div>
                        <div className="h-2 rounded-lg bg-b11 dark:bg-black mb-2.5 flex-1"></div>
                        <div className="h-2 rounded-lg bg-b11 dark:bg-black mb-2.5 flex-1"></div>
                        <div className="h-2 rounded-lg bg-b11 dark:bg-black mb-2.5 w-3/12"></div>
                        <div className='ml-auto flex gap-3'>
                            <div className="h-4 w-4 rounded-sm bg-b11 dark:bg-black mb-2.5 flex-1"></div>
                            <div className="h-4 w-4 rounded-sm bg-b11 dark:bg-black mb-2.5 flex-1"></div>
                        </div>
                    </div>
                ))
            }
        </div>
    )
}

export function StorageLoader() {
    return (
        <div role="status" className="w-full animate-pulse lg:px-5 px-3 flex gap-3 md:items-center md:flex-row flex-col">
            <div className="h-[150px] bg-b11 dark:bg-black mb-4 md:flex-1 rounded-lg w-full"></div>
            <div className='flex-1 flex flex-col justify-center items-center'>
                <div className="h-2 rounded-lg bg-b11 dark:bg-black mb-3 w-1/2"></div>
                <div className="h-9 rounded-lg bg-b11 dark:bg-black mb-2.5 w-3/4"></div>
            </div>
        </div>
    )
}