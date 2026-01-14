# Netlify config for when Roadie is in elm/roadie subfolder
[build]
  base = "roadie/frontend"
  command = "cd roadie/frontend && npm run build"
  publish = "roadie/frontend/.next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NODE_VERSION = "18"

