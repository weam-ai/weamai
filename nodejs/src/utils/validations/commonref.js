const joi = require("joi");

const userSchemaKeys = {
  email: joi.string().email().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
  fname: joi.string().optional(),
  lname: joi.string().optional(),
};

const teamSchemaKeys = {
  teamUsers: joi.array().items(joi.object().unknown(true)).optional(),
  teamName: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const countrySchemaKeys = {
  nm: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const updateCountrySchemaKeys = {
  nm: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const stateSchemaKeys = {
  nm: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const updateStateSchemaKeys = {
  nm: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const profileSchemaKeys = {
  name: joi.string().required(),
  uri: joi.string().required(),
  mime_type: joi.string().required(),
  file_size: joi.string().required(),
};

const citySchemaKeys = {
  nm: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const updateCitySchemaKeys = {
  nm: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const companySchemaKeys = {
  name: joi.string().required(),
  slug: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
};

const botSchemaKeys = {
  title: joi.string().required(),
  code: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
  isShare: joi.boolean()
};

const brainSchemaKeys = {
  title: joi.string().required(),
  slug: joi.string().required(),
  id: joi
    .string()
    .regex(/^[0-9a-fA-F]{24}$/)
    .required(),
  isShare: joi.boolean()
};

module.exports = {
  userSchemaKeys,
  teamSchemaKeys,
  countrySchemaKeys,
  updateCountrySchemaKeys,
  stateSchemaKeys,
  updateStateSchemaKeys,
  profileSchemaKeys,
  citySchemaKeys,
  updateCitySchemaKeys,
  companySchemaKeys,
  botSchemaKeys,
  brainSchemaKeys,
};
