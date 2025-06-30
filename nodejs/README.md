# Weam

# Environment
  - main (production): The main branch is used for stable releases and production deployments.
  - staging (QA): Staging environment for testing features before deployment to production.
  - development (development): Development branch for ongoing development work.

# Branching Strategy
  - feature/branch-name: Create new features or developments from the main branch.
  - bugfix/branch-name: Address bugs from either main or staging, depending on the situation.
  - hotfix/branch-name: Immediate fixes created from the main branch.
    
# Branch names should be meaningful, possibly including keywords like "payment" or "feature/payment".

# Installing Node Modules with pnpm
  1. Install pnpm globally if not already installed: npm install -g pnpm
  2. Install dependencies: pnpm install

# Notes:
  Advantages of pnpm:
    - Disk space efficient: Uses a single storage for all projects to save disk space.
    - Faster installations: Uses hard links and parallel installation to reduce installation time.
    - Network efficient: Downloads packages in parallel, saving bandwidth.
    - Compatibility: pnpm works with package.json and pnpm-lock.yaml similar to npm or yarn, but with its own optimizations.

# Running the Node.js Application with PM2
  1. Install PM2 globally if not already installed: npm install pm2 -g
  2. Start your application in production mode: pm2 start appname
