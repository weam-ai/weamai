const joi = require("joi");
const { userSchemaKeys, teamSchemaKeys } = require("./commonref");

const createWorkspaceKeys = joi.object({
  title: joi.string().required(),
  users: joi
    .array()
    .items(
      joi
        .object({
          ...userSchemaKeys,
          roleCode: joi.string().required(),
        })
        .optional()
    )
    .optional(),

  teams: joi
    .array()
    .items(
      joi
        .object({
          ...teamSchemaKeys,
        })
        .optional()
    )
    .optional(),
});

const updateWorkspaceKeys = joi.object({
  title: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
});

const addWorkSpaceUserKeys = joi.object({
  workspaceId: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
  companyId: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
  users: joi
    .array()
    .items(
      joi
        .object({
          ...userSchemaKeys,
          roleCode: joi.string().required(),
        })
        .required()
    )
    .required(),
});

const deleteWorkSpaceUserKeys = joi.object({
    user_id: joi
        .string()
        .regex(/^[0-9a-fA-F]{24}$/)
        .required(),
    sharedBrains: joi
        .array()
        .items(joi.object().unknown(true))
        .required(),
});

module.exports = {
  createWorkspaceKeys,
  updateWorkspaceKeys,
  addWorkSpaceUserKeys,
  deleteWorkSpaceUserKeys,
};
