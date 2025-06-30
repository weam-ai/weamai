import commonApi from '@/api';
import { useState } from 'react';
import { MODULE_ACTIONS, DEFAULT_SORT } from '@/utils/constant';
import { FavoriteItemsType } from '@/types/common';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';

const useFavorite = () => {
    const [loading, setLoading] = useState(false);
    const [favorites, setFavorites] = useState([]);
    const [searchCache, setSearchCache] = useState<Map<string, FavoriteItemsType[]>>(new Map());
    const brains = useSelector((store: RootState) => store.brain.combined);
    
    const getFavoriteList = async (searchValue = '') => {
        try {
            if (!brains.length) return;
            if (searchCache.has(searchValue)) {
                setFavorites(searchCache.get(searchValue));
                return;
            }
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.FAVORITE_LIST,
                data: {
                    options: {
                        pagination: false,
                        sort: {
                            createdAt: DEFAULT_SORT,
                        },
                    },
                    query: {
                        search: searchValue,
                        brainIds: brains.map((brain) => brain._id),
                    }
                },
            });
            
            setFavorites(response.data);  
            setSearchCache((prev: Map<string, FavoriteItemsType[]>) => { 
                const newCache = new Map(prev);
                newCache.set(searchValue, response.data);
                return newCache;
            })        
            return response;
        } catch (error) {
            console.error("Error fetching favorite list: ", error);
        } finally {
            setLoading(false);
        }
    };

    return {
        loading,
        favorites,
        getFavoriteList,
    };
};

export default useFavorite;