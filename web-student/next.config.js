/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',

  // Image optimization
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
