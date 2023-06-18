/// <reference types="vite/client" />

interface ImportMetaEnv {
  VITE_API_SCHEMA_URL: string;
}

declare module '@stoplight/elements' {
  export const API: any;
}
