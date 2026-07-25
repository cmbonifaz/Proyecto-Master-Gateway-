import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Requerido para el build multi-etapa de Docker (genera .next/standalone)
  output: "standalone",
};

export default nextConfig;
