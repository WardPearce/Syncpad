#!/bin/sh
ROOT_DIR=./

# Replace env vars in JavaScript and HTML files served by NGINX
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_MCAPTCHA_ENABLED_PLACEHOLDER|'"$VITE_MCAPTCHA_ENABLED"'|g' {} +
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_MCAPTCHA_API_PLACEHOLDER|'"$VITE_MCAPTCHA_API"'|g' {} +
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_MCAPTCHA_SITE_KEY_PLACEHOLDER|'"$VITE_MCAPTCHA_SITE_KEY"'|g' {} +
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_THEME_PLACEHOLDER|'"$VITE_THEME"'|g' {} +
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_SITE_NAME_PLACEHOLDER|'"$VITE_SITE_NAME"'|g' {} +
find "$ROOT_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i 's|VITE_BLOCKSTREAM_API_PLACEHOLDER|'"$VITE_BLOCKSTREAM_API"'|g' {} +
