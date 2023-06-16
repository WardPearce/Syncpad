import Ajv, { type ErrorObject } from "ajv";
import schema from "./client/schema.json";

const ajv = new Ajv({ allErrors: true, strict: false });
ajv.addSchema(schema, "schema.json");

class ValidationException extends Error {
  constructor(errors: string) {
    const message = `Validation failed:\n${errors}`;
    super(message);
    this.name = "ValidationException";
  }
}

export function validateData(route: string, method: string, data: unknown): void {
  if (!(route in schema.paths)) {
    throw new ValidationException(`Route '${route}' not found in schema.`);
  }

  const routeInfo = schema.paths[route];

  if (!(method in routeInfo)) {
    throw new ValidationException(`Method '${method}' not found for route '${route}' in schema.`);
  }

  const validate = ajv.compile(routeInfo[method]);
  const isValid = validate(data) as boolean;

  if (!isValid) {
    const errors: string = formatErrors(validate.errors ?? []);
    throw new ValidationException(errors);
  }
}

function formatErrors(errors: ErrorObject[]): string {
  const formattedErrors = errors.map((error) => `• ${error.instancePath} ${error.message}`);
  return formattedErrors.join('\n');
}
