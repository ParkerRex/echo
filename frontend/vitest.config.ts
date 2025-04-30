import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()],
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
