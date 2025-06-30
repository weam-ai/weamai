import commonApi from '@/api';
import { DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import { decodedObjectId } from '@/utils/helper';
import Toast from '@/utils/toast';
import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { APIResponseType, DefaultPaginationType, ObjectType, PaginatorType } from '@/types/common';
import { BrainDocType } from '@/types/brain';
import { getCurrentUser } from '@/utils/handleAuth';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';

const useBrainDocs = (b?: string) => {
    const router = useRouter();
    const [brainDocs, setBrainDocs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [paginator, setPaginator] = useState<PaginatorType>({});
    const brainId = useMemo(() => decodedObjectId(b), [b]);
    const [showFavorites, setShowFavorites] = useState(false);
    const currentUser = useMemo(() => getCurrentUser(), []);
    const selectedWorkSpace = useSelector((store: RootState) => store.workspacelist.selected);

    const getAllBrainDocs = async (searchValue = '', pagination: DefaultPaginationType = { offset: 0, limit: 10 }) => {
        if (!b) {
            setLoading(false);
            return;
        }
        try {
            setLoading(true);
            const finalFilterOptions = showFavorites 
                ? { favoriteByUsers: { $in: [currentUser._id] } }
                : '';

            const response: APIResponseType<BrainDocType[]> = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_DOCS,
                common: true,
                data: {
                    options: {
                        sort: { createdAt: DEFAULT_SORT },
                        populate: [
                            {
                                path: 'userId',
                                select: 'email profile fname lname'
                            }
                        ],
                        ...pagination,
                        select: 'brainId doc userId fileId embedding_api_key favoriteByUsers',
                    },
                    query: {
                        searchColumns: [SEARCH_AND_FILTER_OPTIONS.BRAIN_DOCS],
                        search: searchValue,
                        brainId: brainId,
                        ...finalFilterOptions
                    }
                }
            })

            if(showFavorites && pagination.offset === 0){
                setBrainDocs(response.data);
            } else if(pagination.offset === 0){
                setBrainDocs(response.data);
            } else {
                setBrainDocs((prev: BrainDocType[]) => [...prev, ...response.data]);
            }
            setPaginator(response.paginator as PaginatorType);
        } catch (error) {
            if(error?.response?.status===302){
                router.push('/')
            }
            console.error('error: ', error);
        } finally {
            setLoading(false);
        }
    }

    const deleteBrainDoc = async (id) => {
        try {
            const response = await commonApi({
                parameters: [id],
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_DOCS,
                common: true,
            })
            Toast(response.message);
            setBrainDocs(brainDocs.filter(doc => doc._id !== id));
        } catch (error) {
            console.error('error: ', error);
        }
    }

    const getTabDocList = async (searchValue: string, pagination: DefaultPaginationType = { offset: 0, limit: 10 }): Promise<BrainDocType[]> => {
        try {
            if (!selectedWorkSpace) return [];
            setLoading(true);
            const response: APIResponseType<BrainDocType[]> = await commonApi({
                action: MODULES.TAB_DOCUMENT_LIST,
                data: {
                    options: {
                        sort: { createdAt: DEFAULT_SORT },
                        ...pagination
                    },
                    query: {
                        searchColumns: [SEARCH_AND_FILTER_OPTIONS.BRAIN_DOCS],
                        search: searchValue,
                        workspaceId: selectedWorkSpace._id
                    }
                },
            }) 
            setBrainDocs((prev: BrainDocType[]) => [...prev, ...response.data]);
            setPaginator(response.paginator as PaginatorType);
            return response.data;
        } catch (error) {
            console.error('error: ', error);
        } finally {
            setLoading(false);
        }
    }

    const favouriteBrainDoc = async (payload, docId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.FAVORITE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.CHAT_DOCS,
                common: true,
                data: payload,
                parameters: [docId]
            });
            if (!payload.favorite && showFavorites) {
                setBrainDocs((prevList) => prevList.filter(doc => doc._id !== docId));
            }
            Toast(response.message);
        } catch (error) {
            console.log('error: ', error);
        }
    }

    return {
        brainDocs,
        getAllBrainDocs,
        loading,
        deleteBrainDoc,
        setLoading,
        paginator,
        getTabDocList,
        favouriteBrainDoc,
        showFavorites,
        setShowFavorites,
        setBrainDocs
    }
};

export default useBrainDocs;
