#!/bin/sh
ROOT_DIR=./

# Replace env vars in JavaScript and HTML files served by NGINX
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_API_SCHEMA_URL_PLACEHOLDER|'"$VITE_API_SCHEMA_URL"'|g' {} +
