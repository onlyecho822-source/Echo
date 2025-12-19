# Support Guide

## Getting Help

### 1. Documentation
Start with the README.md for basic setup and usage.

### 2. GitHub Discussions
Ask questions, share use cases, and connect with the community:  
https://github.com/nathanpoinsette/echo-git-sync/discussions

### 3. GitHub Issues
Report bugs or request features:  
https://github.com/nathanpoinsette/echo-git-sync/issues

### 4. Email Support
For private inquiries: support@nathanpoinsette.com

## Common Issues

### "Permission denied" error
**Solution:** Ensure SSH keys are configured for all remotes.
```bash
ssh -T git@github.com
ssh -T git@gitlab.com
ssh -T git@codeberg.org
```

### Sync fails for one remote
**Solution:** Run status check to identify the failing remote.
```bash
./bin/status.sh
```

### Hash mismatch after sync
**Solution:** This indicates file corruption or tampering. Re-sync from a trusted source.

### Slow sync performance
**Solution:** Ensure good network connection. Consider reducing number of remotes or using parallel execution.

## Response Times
- **Community (GitHub):** Best effort, usually within 24-48 hours
- **Email:** Within 48 hours for general inquiries
- **Security Issues:** Within 24 hours

## Self-Service Resources
- README.md - Setup and usage
- ROADMAP.md - Upcoming features
- SECURITY.md - Security best practices
- CONTRIBUTING.md - How to contribute

## Feature Requests
We welcome feature requests! Please:
1. Check existing discussions/issues first
2. Describe your use case
3. Explain why it benefits the community
4. Be patient - we're a small team

## Commercial Support
For enterprise support, SLAs, and custom features, contact: enterprise@nathanpoinsette.com

