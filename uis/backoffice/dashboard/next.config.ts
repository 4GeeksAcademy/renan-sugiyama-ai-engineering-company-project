import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@nexova/telemetry"],
  turbopack: {
    // Must include packages/ so the linked @nexova/telemetry can be resolved.
    root: new URL("../../..", import.meta.url).pathname,
  },
};

export default nextConfig;
