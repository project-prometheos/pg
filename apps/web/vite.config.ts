import { defineConfig } from 'vite';

import react from '@vitejs/plugin-react';

// NOTE: KaTeX fonts were failing to load with paths like
//   /node_modules/.vite/deps/fonts/KaTeX_Main-Regular.woff2
// in the browser console ("downloadable font: rejected by sanitizer").
// This happens because the KaTeX CSS was pre-bundled into .vite/deps and its
// relative `fonts/` references no longer point at the real location, leading to
// 404s that the browser then rejects as invalid fonts.
// By excluding 'katex' from optimizeDeps, Vite serves
// /node_modules/katex/dist/katex.min.css directly so that the original
// relative font URLs resolve to existing files at
// /node_modules/katex/dist/fonts/*.woff2.
// If this alone does not resolve the issue, a fallback is to manually import
// the fonts with `?url` and define @font-face rules, or to use the CDN CSS.

export default defineConfig({
	server: {
		port: 5173,
		proxy: {
			'/api': 'http://localhost:8000',
		},
	},
	plugins: [react()],
	optimizeDeps: {
		exclude: ['katex'],
	},
});
