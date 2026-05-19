/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      { source: "/dtp", destination: "/", permanent: false },
      { source: "/traffic-preview", destination: "/login", permanent: false },
    ]
  },
  webpack: (config, { dev }) => {
    if (dev) {
      config.cache = false
    }
    return config
  },
}

module.exports = nextConfig
