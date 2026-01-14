/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
  },
  // Netlify compatibility
  output: 'standalone',
}

module.exports = nextConfig

