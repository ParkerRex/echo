import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8080',
                changeOrigin: true,
                secure: false,
            },
        },
    },
    test: {
        environment: "jsdom",
        globals: true,
        setupFiles: [],
        coverage: {
            reporter: ["text", "html"],
        },
        include: ["app/components/**/*.test.{ts,tsx}"],
    },
});
