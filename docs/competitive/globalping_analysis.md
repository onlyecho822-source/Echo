# Globalping Competitive Analysis

**URL:** https://globalping.io/
**Category:** Internet infrastructure monitoring and benchmarking platform
**Developer:** jsDelivr team

## Overview

Globalping is a free, open-source platform that allows anyone to run networking commands (ping, traceroute, dig, curl, mtr) on probes distributed globally. It is developed by the jsDelivr CDN team with over 10 years of experience in global content delivery.

## Network Scale

- **3,268 connected probes** worldwide
- **666 different cities**
- **111 different countries**
- Community-powered probe network

## Core Capabilities

### Supported Network Tests
1. **Ping** - Latency testing
2. **Traceroute** - Network path tracing
3. **DNS Resolve (dig)** - DNS query testing
4. **HTTP/HTTPS (curl)** - Web endpoint testing
5. **MTR** - Combined ping + traceroute
6. **TCP Ping** - TCP connection testing

### Location Selection ("Magic API")
Users can specify test locations using natural language:
- Countries, continents, cities
- US states, regions (e.g., "Western Europe")
- ASNs, ISP names
- Tags: "eyeball" or "datacenter"
- Cloud region names (e.g., "us-east-2")

## Business Model

**Free and Open Source:**
- All components are open source on GitHub
- Generous free limits for all users
- Higher limits for GitHub Sponsors
- Funded by jsDelivr organization and sponsors

**Hardware Probe Program:**
- $10/month GitHub sponsorship gets you a hardware probe
- Plug-and-play device for home/office networks
- No 24/7 computer required
- Fully secure, no LAN access

## Integration Options

1. **Web Interface** - Interactive testing dashboard
2. **CLI Tool** - Command-line interface for scripting
3. **REST API** - Free API for custom integrations
4. **Slack App** - Run tests from Slack
5. **Discord App** - Run tests from Discord
6. **GitHub Bot** - Automated testing in CI/CD

## Use Cases (Per Globalping)

- Optimize anycast networks
- Monitor global latency
- Debug routing issues
- Check for censorship in different countries
- Benchmark CDN providers
- Compare DNS providers globally
- Troubleshoot networking problems

## Technical Architecture

**Probe Network:**
- Community-contributed probes
- Docker/Podman containers
- Works on x86 and ARM architectures
- Runs in host network mode
- Auto-restart capability

**Security & Privacy:**
- Minimizes public information exposure
- Blocks harmful and abusive domains/IPs
- Hardware probes have no LAN access
- No open ports
- Open-source firmware

## Strengths

1. **Massive scale** - 3,268 probes globally
2. **Free and open source** - No cost barrier
3. **Easy to use** - Natural language location selection
4. **Multiple interfaces** - Web, CLI, API, Slack, Discord
5. **Community-powered** - Sustainable through contributions
6. **Credible team** - jsDelivr has 10+ years CDN experience
7. **Comprehensive tests** - All major network commands

## Weaknesses/Gaps

1. **No dependency mapping** - Tests individual targets, doesn't map relationships
2. **No historical analysis** - Point-in-time tests, not continuous monitoring
3. **No change verification** - Doesn't track before/after changes
4. **No falsifiable pods** - Results aren't cryptographically sealed
5. **No supply chain modeling** - Doesn't map organizational dependencies
6. **Limited to network layer** - Doesn't analyze application dependencies
7. **No TAFT methodology** - Tests are manual, not systematic continuous loops
8. **Community-dependent** - Probe coverage depends on volunteer contributions

## Relevance to Echo

Globalping is the **closest competitor** to Echo's Dependency Mapping Probe in terms of:
- Global probe network
- Network path tracing (traceroute)
- Open-source approach
- Free access model

However, Globalping is fundamentally different from Echo in purpose and architecture.

### Key Differences: Globalping vs. Echo

| Aspect | Globalping | Echo |
|--------|-----------|------|
| **Purpose** | Ad-hoc network testing | Systematic dependency mapping |
| **Data Model** | Ephemeral test results | Immutable, signed pods |
| **Analysis** | Individual tests | Correlation across tests |
| **Focus** | Network debugging | Systemic risk visibility |
| **Methodology** | Manual testing | TAFT continuous loops |
| **Output** | Test results | Dependency graphs |
| **Verification** | None | Cryptographic signatures |
| **Knowledge** | Transient | Permanent, queryable |

### What Globalping Does Well (That Echo Should Learn From)

1. **Simplicity** - The "magic API" for location selection is brilliant
2. **Community model** - Sustainable through volunteer probes
3. **Multiple interfaces** - Web, CLI, API, Slack, Discord
4. **Open source** - Builds trust and contributions
5. **Hardware probes** - Lowers barrier for participation

### What Echo Does That Globalping Doesn't

1. **Dependency mapping** - Correlates tests to reveal relationships
2. **Immutable records** - Cryptographically signed pods
3. **Continuous monitoring** - TAFT loops, not one-off tests
4. **Change verification** - Before/after baselines
5. **Supply chain modeling** - Maps organizational dependencies
6. **Falsifiable hypotheses** - Each test is a scientific claim
7. **Knowledge compounding** - Builds permanent library

## Strategic Positioning

**Globalping is a tool. Echo is a knowledge system.**

Globalping provides the ability to run tests. Echo provides the ability to understand systemic risk through those tests. They are complementary, not competitive.

**Potential Collaboration:**
Echo could potentially use Globalping's probe network as one source of vantage points, while adding its own unique value through:
- Systematic test orchestration
- Dependency correlation
- Immutable record-keeping
- Continuous TAFT loops
- Supply chain risk modeling

## Conclusion

Globalping validates the market demand for global network visibility and proves that a community-powered, open-source model can achieve massive scale (3,268 probes). However, it operates at the "test execution" layer, not the "systemic insight" layer.

Echo's opportunity is to build on top of the testing capabilities (whether Globalping's or its own) to create the **dependency mapping and risk analysis layer** that the market needs but doesn't yet have.
