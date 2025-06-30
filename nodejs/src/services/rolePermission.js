const Permission = require('../models/permission');
const PermissionRole = require('../models/permissionRole');
const Role = require('../models/role');
const User = require('../models/user');
const dbService = require('../utils/dbService');
const { groupBy, pick } = require('../utils/helper');

async function permit (req) {
    try {
        if (!req.roleId) {
            throw new Error(_localize('auth.roleNotProvide', req));
        }
        if (req.route.hasOwnProperty('o')) {
            const permission = await Permission.findOne({
                route_name: req.route['o'],
            });

            if (permission) {
                const permissionExist = await PermissionRole.findOne({
                    permission_id: permission.id,
                    role_id: req.roleId,
                });

                return !!permissionExist;
            }
        }
        return false;
    } catch (error) {
        handleError(error, 'Error in permit function');
    }
}

async function getPermission (req) {
    try {
        const user = await dbService.getDocumentByQuery(User, { _id: req.params.id }, { roleId: 1 });
        if (!user) {
            return false;
        }

        const roleCheck = await dbService.getDocumentByQuery(Role, { _id: user.roleId }, { code: 1 });
        const permissionRole = await PermissionRole.find({ role_id: roleCheck._id }, { permission_id: 1 });
        const permissionRoleIds = permissionRole.map(permission => permission.permission_id);

        let findPermit = await Permission.find({ _id: { $in: permissionRoleIds } }, { route_name: 1, module: 1 });
        findPermit = groupBy(findPermit, 'module');

        const rolePermission = {};
        rolePermission.roleId = roleCheck._id;
        rolePermission.roleCode = roleCheck.code;

        Object.keys(findPermit).map((objectKey) => {
            rolePermission[objectKey] = findPermit[objectKey].map(obj => obj.route_name.split('.')[1]);
            return objectKey;
        });

        return rolePermission;

    } catch (error) {
        handleError(error, 'Error in role permission service get permission function');
    }
}

async function updatePermission (req) {
    try {
        const { roleId, permissionIds } = req.body;
        const roleCheck = await dbService.getDocumentByQuery(Role, { _id: roleId }, { code: 1 });
        if (!roleCheck) {
            return false;
        }

        await PermissionRole.deleteMany({ role_id: roleCheck._id, canDel: true });

        const allPermission = await Permission.find({}, { _id: 1 });

        await Promise.all(permissionIds.map(async (permissionId) => {
            const permission = allPermission.find(element => element._id.equals(permissionId));
            if (permission) {
                const data = {
                    permission_id: permissionId,
                    role_id: roleId
                }

                const permissionRole = await PermissionRole.findOne(data);
                if (!permissionRole) {
                    PermissionRole.create(data);
                }
            }
        }));

        return true;
    } catch (error) {
        handleError(error, 'Error in update permission function');
    }
}

async function getAll (_req) {
    try {
        const result = await Permission.find();
        if (result.length) {
            return result;
        }
        return false;
    } catch (error) {
        handleError(error, 'Error in get all permission');
    }
}

async function getByRole (req) {
    try {
        const permissions = await Permission.find();
        const modulePromises = await Promise.all(permissions.map(async (permission) => {
            const permissionRole = await PermissionRole.findOne({
                role_id: req.params.id,
                permission_id: permission._id,
            })

            const obj = {
                ...pick(permission, ['_id', 'route_name', 'module']),
                selected: !!permissionRole
            }

            obj.route_name = permission.route_name.split('.')[1];
            return obj;
        }))

        return groupBy(modulePromises, 'module');
    } catch (error) {
        handleError(error, 'Error in getByRole function');
    }
}

module.exports = {
    permit,
    getPermission,
    updatePermission,
    getAll,
    getByRole
}