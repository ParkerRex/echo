import { defineConfig } from '@tanstack/react-start/config';
import viteTsConfigPaths from 'vite-tsconfig-paths';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    tsr: {
        appDirectory: 'app',
    },
    vite: {
        plugins: [
            // this is the plugin that enables path aliases
            viteTsConfigPaths({
                projects: ['./tsconfig.json'],
            }),
            tailwindcss(),
        ],
        server: {
            // Proxy API requests to the backend Flask app
            proxy: {
                '/api': {
                    target: 'http://localhost:8080',
                    changeOrigin: true,
                    secure: false,
                },
            },
        },
        build: {
            // Configure assets including CSS
            assetsDir: 'public',
            cssCodeSplit: false,
        },
        css: {
            // Make sure PostCSS processes Tailwind correctly
            postcss: {
                plugins: [], // PostCSS plugins are loaded from postcss.config.js
            },
        },
    },
});