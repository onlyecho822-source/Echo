# HackerNews Post

**Title:** Show HN: Echo Git Sync – Multi-provider git redundancy

**Body:**

I built a simple bash tool to sync git repos across multiple providers (GitHub, GitLab, Codeberg, self-hosted).

Why: After seeing developers lose access to GitHub accounts, I wanted code redundancy without complex infrastructure.

How it works:
- Parallel push to all configured remotes
- Pre-flight connectivity checks
- SHA-256 integrity verification
- Pure bash + git (zero dependencies)

Would love feedback on the approach!

Link: github.com/onlyecho822-source/Echo/tree/main/echo-git-sync

