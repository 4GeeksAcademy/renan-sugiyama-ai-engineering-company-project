import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const telemetrySrc = new URL("../../../packages/telemetry/src", import.meta.url)
  .pathname;

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "NEXT_PUBLIC_");

  return {
    plugins: [react()],
    resolve: {
      alias: [
        {
          find: "@nexova/telemetry/context",
          replacement: `${telemetrySrc}/context.ts`,
        },
        { find: "@nexova/telemetry", replacement: `${telemetrySrc}/index.ts` },
      ],
    },
    // The shared telemetry package reads a Next.js-style env var.
    define: {
      "process.env.NEXT_PUBLIC_TELEMETRY_ENDPOINT": JSON.stringify(
        env.NEXT_PUBLIC_TELEMETRY_ENDPOINT ?? "",
      ),
    },
    server: { fs: { allow: ["../../.."] } },
  };
});
