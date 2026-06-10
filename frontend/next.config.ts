import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  experimental: {},
  images: {
    remotePatterns: [],
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000/api/v1";

    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
