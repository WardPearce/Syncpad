import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import autoprefixer from 'autoprefixer';
import tailwind from 'tailwindcss';


const config = {
	kit: {
		adapter: adapter({
			fallback: 'index.html'
		})
	},
	preprocess: vitePreprocess({
		postcss: {
			plugins: [
				tailwind,
				autoprefixer
			]
		}
	})
};

export default config;
