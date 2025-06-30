import { RESPONSE_STATUS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { useEffect, useRef, useState, useTransition } from 'react';

const useServerAction = <P extends unknown[], R>(action: (...args: P) => Promise<R>, onFinished?:(R | undefined)): [(...args: P) => Promise<R | undefined>, boolean] => {
    const [isPending, startTransition] = useTransition();
    const [result, setResult] = useState<R>();
    const [finished, setFinished] = useState(false);
    const resolver = useRef<(value?: R | PromiseLike<R>) => void>();
    const onFinishRef = useRef(onFinished);
    useEffect(() => {
        if (!finished) return;
        if (onFinishRef.current) onFinishRef.current(result);
        resolver.current?.(result);
    }, [result, finished]);

    const runAction = async (...args: P): Promise<R | undefined> => {
        startTransition(() => {
            action(...args).then((data: any) => {
                if ([RESPONSE_STATUS.UNPROCESSABLE_CONTENT, RESPONSE_STATUS.BAD_REQUEST,RESPONSE_STATUS.ERROR].includes(data?.status)) {
                    Toast(data.message, 'error');
                    return;
                }
                setResult(data);
                setFinished(true);
            });
        });

        return new Promise((resolve) => {
            resolver.current = resolve;
        });
    };

    return [runAction, isPending];
};

export default useServerAction;
