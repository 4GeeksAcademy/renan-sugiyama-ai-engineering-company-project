import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@nexova/telemetry"],
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
