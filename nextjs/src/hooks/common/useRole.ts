import commonApi from '@/api';
import { MODULES, MODULE_ACTIONS } from '@/utils/constant';
import { useState } from 'react';

const useRole = () => {
    const [roles, setRoles] = useState([]);

    const getRoles = async (filter) => {
        let query = {}
        if (filter) {
            query = {
                ...filter
            }
        }
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.ROLE,
                common: true,
                data: {
                    query
                }
            })
            setRoles(response.data)

        } catch (error) {
            console.log('error: ', error);
        }
    }

    return {
        getRoles,
        roles
    }
};

export default useRole;
