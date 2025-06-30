import { useCallback, useRef, DependencyList } from 'react';

const useIntersectionObserver = <T extends HTMLElement>(
    callback: () => void,
    deps: DependencyList
) => {
    const observer = useRef<IntersectionObserver | null>(null);

    const targetRef = useCallback(
        (node: T) => {
            if (deps.every(Boolean)) {
                observer.current?.disconnect();
                observer.current = new IntersectionObserver((entries) => {
                    if (entries[0].isIntersecting) {
                        callback();
                        observer.current?.disconnect();
                    }
                });
                if (node) observer.current?.observe(node);
            }
        },
        [callback, deps]
    );

    return targetRef;
};

export default useIntersectionObserver;
