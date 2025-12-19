# Security Policy

## Reporting a Vulnerability
Please report security issues directly to security@nathanpoinsette.com or via a private GitHub Vulnerability Report. Do not open public issues for security exploits.

## Response Timeline
- **Acknowledgment:** Within 24 hours
- **Initial Assessment:** Within 72 hours
- **Fix Timeline:** Depends on severity (critical: 7 days, high: 14 days, medium: 30 days)

## No Warranty
As stated in the MIT License, this software is provided "as is." The user assumes all responsibility for the configuration of their remote URLs. We are not responsible for data loss caused by misconfiguration.

## Integrity Verification
We encourage all users to run `./bin/verify-integrity.sh` after cloning to ensure the codebase matches the published SHA-256 hash.

## Security Best Practices
1. **Review remote URLs** before running sync-all.sh
2. **Use SSH keys** instead of HTTPS passwords
3. **Verify integrity** after every update
4. **Test in dry-run mode** before production use
5. **Keep git updated** to latest stable version

## Known Limitations
- Relies on git's security model
- No built-in encryption (use git-crypt if needed)
- Assumes trusted network connection
- User responsible for remote authentication

## Security Features
- ✅ Pre-flight connectivity checks
- ✅ SHA-256 integrity verification
- ✅ No external dependencies
- ✅ Open source (auditable)
- ✅ No data collection

## Hall of Fame
We recognize security researchers who responsibly disclose vulnerabilities:
- (None yet - be the first!)

