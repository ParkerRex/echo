// app.config.ts
import { defineConfig } from "@tanstack/react-start/config";
import tsConfigPaths from "vite-tsconfig-paths";
var app_config_default = defineConfig({
  tsr: {
    appDirectory: "src",
    // Load environment variables from project root
    envDir: "../.."
  },
  vite: {
    plugins: [
      tsConfigPaths({
        projects: ["./tsconfig.json"]
      })
    ],
    // Ensure environment variables are available in both server and client contexts
    define: {
      // Server-side environment variables (available in SSR)
      "process.env.SUPABASE_URL": JSON.stringify(process.env.SUPABASE_URL),
      "process.env.SUPABASE_ANON_KEY": JSON.stringify(process.env.SUPABASE_ANON_KEY),
      "process.env.SUPABASE_JWT_SECRET": JSON.stringify(process.env.SUPABASE_JWT_SECRET)
    }
  }
});
export {
  app_config_default as default
};
