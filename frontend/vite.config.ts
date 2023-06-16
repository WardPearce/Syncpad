import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';
import viteCompression from "vite-plugin-compression";
import topLevelAwait from "vite-plugin-top-level-await";
import wasm from "vite-plugin-wasm";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    svelte(),
    wasm(),
    topLevelAwait(),
    viteCompression({ algorithm: "brotliCompress" })
  ]
});
