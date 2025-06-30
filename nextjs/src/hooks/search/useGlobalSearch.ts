import commonApi from '@/api';
import { useState } from 'react';
import { MODULE_ACTIONS } from '@/utils/constant';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';
const useGlobalSearch = () => {
    const [loading, setLoading] = useState(false);
    const [searchResults, setSearchResults] = useState([]);
    const [searchResultCache, setSearchResultCache] = useState<Map<string, any[]>>(new Map());
    const combinedBrain = useSelector((store: RootState) => store?.brain?.combined); 
    
    const getGlobalSearch = async (searchValue = '', combinedBrain) => {
        const brainIds = combinedBrain.map((brain) => brain._id);
        // Check if results exist in cache
        // if (searchResultCache.has(searchValue)) {
        //     setSearchResults(searchResultCache.get(searchValue));
        //     return;
        // }
        
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.GLOBAL_SEARCH,
                data: {
                    query: {
                        search: searchValue,
                        'brains': brainIds                        
                    },
                }
            });

            // if(!searchValue){
            //     setSearchResultCache(prev => new Map([...prev.entries(), [searchValue, response?.data]]));
            // }
            
            setSearchResults(response?.data);
            return response?.data;
        } catch (error) {
            console.error("Error fetching global search: ", error);
        } finally {
            setLoading(false);
        }
    }

    return {
        loading,
        searchResults,
        getGlobalSearch,
        setSearchResults,
        searchResultCache,
        setSearchResultCache
    };
};

export default useGlobalSearch;