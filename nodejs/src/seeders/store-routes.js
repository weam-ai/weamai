const dbService = require('../utils/dbService');
const Role = require('../models/role');
const Permission = require('../models/permission');
const PermissionRole = require('../models/permissionRole');
const { ROLE_TYPE } = require('../config/constants/common');

async function storeModules(route, role) {
    try {
        const modulePromises = route.descriptor.map(async (descriptor) => {
            let findPermission = await dbService.getDocumentByQuery(Permission, { route_name: descriptor });
            const data = {
                route_name: descriptor,
                module: descriptor.substring(0, descriptor.indexOf('.')),
                uri: route.path,
            }
            if (!findPermission) {
                findPermission = await dbService.createDocument(Permission, data);
            }

            const permissionRoleData = {
                permission_id: findPermission._id,
                role_id: role._id,
            }

            const findPermissionRole = await dbService.getDocumentByQuery(PermissionRole, permissionRoleData);
            if (!findPermissionRole) {
                await dbService.createDocument(PermissionRole, permissionRoleData);
            }

            return data;
        })
        return Promise.all(modulePromises);
    } catch (error) {
        logger.error('Error in storeModules function ', error);
    }
}

async function store(routeList) {
    if (!routeList || !routeList.length) {
        return;
    }

    try {
        let defaultRole = await dbService.getDocumentByQuery(Role, { code: ROLE_TYPE.SUPER_ADMIN });
        if (!defaultRole) {
            defaultRole = await Role.findOneAndUpdate({ code: ROLE_TYPE.SUPER_ADMIN }, { code: ROLE_TYPE.SUPER_ADMIN }, { new: true, upsert: true });
        }

        await Promise.all(
            routeList.map(async (route) => {
                const desCondition =
                    route.hasOwnProperty('descriptor') &&
                    Array.isArray(route.descriptor) &&
                    route.descriptor.length > 0 &&
                    route.descriptor[0] !== undefined &&
                    route.descriptor[0] !== null;

                if (desCondition) {
                    await storeModules(route, defaultRole);
                }
            }),
        );

        logger.info('Store routes completed!');
    } catch (error) {
        logger.error('Error Store routes failed !')
    }
}

module.exports = {
    store
}