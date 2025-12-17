# Echo Git Sync

**A production-ready utility for maintaining synchronized Git repositories across multiple providers.**

It solves the "Single Point of Failure" problem for developers by ensuring code exists simultaneously on GitHub, GitLab, Codeberg, and self-hosted servers.

## Features
- **🔄 Parallel Sync:** Push to multiple remotes simultaneously with atomic error handling.
- **🔐 Integrity Verification:** Generate deterministic SHA-256 checksums of the codebase.
- **🛡️ Connection Testing:** Automatically validates remote URLs before adding them.
- **⚡ Zero Dependencies:** Written in pure Bash. Runs anywhere Git runs.

## Quick Start

```bash
# 1. Add Remotes
./bin/add-remote.sh codeberg git@codeberg.org:user/repo.git

# 2. Sync to All
./bin/sync-all.sh

# 3. Verify Integrity
./bin/verify-integrity.sh
```

## License

MIT License.
