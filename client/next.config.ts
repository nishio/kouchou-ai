import type { NextConfig } from "next";

const isStaticExport = process.env.NEXT_PUBLIC_OUTPUT_MODE === "export";

const nextConfig: NextConfig = {
  output: isStaticExport ? "export" : undefined,
  trailingSlash: isStaticExport ? true : undefined,
  assetPrefix: isStaticExport ? "." : undefined,
  experimental: {
    optimizePackageImports: ["@chakra-ui/react"],
  },
};

export default nextConfig;
