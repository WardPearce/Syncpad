import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import openapiSchema from './client/schema.json';

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

export const ajvValidator = ajv.compile(openapiSchema);
