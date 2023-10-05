import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import topLevelAwait from "vite-plugin-top-level-await";
import wasm from "vite-plugin-wasm";

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    minify: false,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  plugins: [
    svelte(),
    wasm(),
    topLevelAwait(),
    VitePWA({
      manifest: {
        name: "Purplix.io",
        short_name: "Purplix",
        description: "Not completed",
        icons: [
          {
            src: "/android-icon-192x192.png",
            sizes: "192x192",
            type: "image/png",
            density: "4.0"
          }
        ],
        background_color: "#161418",
        theme_color: "#8749f4"
      }
    })
  ],
  optimizeDeps: {
    exclude: ["svelte-navigator"]
  }
},
);
