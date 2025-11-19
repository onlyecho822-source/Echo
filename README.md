# Echo

Hybrid intelligence framework that integrates resonant computation, ethical design, and adaptive systems engineering into a single organism.

## Echo Civilization - Phoenix Phase

### Overview

This repository is part of the Echo Civilization framework — a lawful, harmonic, multi-agent intelligence ecosystem built for transparency, adaptability, and resilience.

### Subsystems

- **Echo Operating System:** Core orchestration kernel.
- **Echo Vault:** Secure identity & state management layer.
- **Echo Engines:** Modular resonance engines (EchoFree, EchoLex, EchoCore).

---

## WiFi Scanner & Decoder

A cross-platform WiFi network scanner and decoder that can detect and analyze wireless networks globally.

### Features

- **Cross-Platform Support**: Works on Linux, macOS, and Windows
- **Network Detection**: Scans for all available WiFi networks
- **Signal Analysis**: Shows signal strength in dBm and quality percentage
- **Security Detection**: Identifies security types (Open, WEP, WPA, WPA2, WPA3)
- **Frequency Bands**: Supports 2.4 GHz, 5 GHz, and 6 GHz (WiFi 6E)
- **Vendor Identification**: Decodes manufacturer from MAC address
- **Channel Analysis**: Shows channel usage and recommendations
- **Multiple Output Formats**: Table, JSON, CSV, and quiet modes

### Installation

```bash
# Clone the repository
git clone https://github.com/echo-civilization/wifi-scanner.git
cd Echo

# Install the package
pip install -e .

# Or run directly
python -m wifi_scanner
```

### Usage

```bash
# Basic scan
wifi-scanner

# Verbose output with all details
wifi-scanner -v

# JSON output for programmatic use
wifi-scanner --json

# Show only 5 GHz networks
wifi-scanner --band 5ghz

# Show only secured networks
wifi-scanner --secure

# Channel usage analysis
wifi-scanner --channel-usage

# Vendor statistics
wifi-scanner --vendor-stats

# Filter by minimum signal strength
wifi-scanner --min-signal -70

# CSV export
wifi-scanner --csv > networks.csv
```

### Command-Line Options

```
Output Options:
  -v, --verbose         Show detailed information for each network
  --json                Output results in JSON format
  --csv                 Output results in CSV format
  -q, --quiet           Minimal output (SSID and signal only)

Filter Options:
  --band {2.4ghz,5ghz,6ghz,all}  Filter by frequency band
  --open                Show only open (unencrypted) networks
  --secure              Show only secured (encrypted) networks
  --hidden              Include hidden networks
  --min-signal DBM      Minimum signal strength in dBm

Sort Options:
  --sort {signal,ssid,channel,security}  Sort results by field
  --reverse             Reverse sort order

Scanner Options:
  -i, --interface       Wireless interface to use

Analysis Options:
  --channel-usage       Show channel usage analysis
  --vendor-stats        Show vendor statistics
```

### Example Output

```
Scanning on interface: wlan0
Scanning for WiFi networks...

SSID                    Signal    Ch  Band      Security
=====================================================
MyHomeNetwork           -45dBm     6  2.4 GHz   WPA2
Office_5G               -52dBm    36  5 GHz     WPA2
CoffeeShop              -68dBm    11  2.4 GHz   Open
Neighbor_WiFi           -72dBm     1  2.4 GHz   WPA/WPA2

Total: 4 networks found
```

### Platform Notes

- **Linux**: Uses `nmcli`, `iw`, or `iwlist`. May require `sudo` for full scan.
- **macOS**: Uses the `airport` utility or `system_profiler`.
- **Windows**: Uses `netsh wlan show networks`.

### Python API

```python
from wifi_scanner import WiFiScanner, WiFiDecoder, FrequencyBand

# Create scanner
scanner = WiFiScanner()

# Scan for networks
networks = scanner.scan()

# Process results
for network in networks:
    print(f"{network.ssid}: {network.signal_strength_dbm}dBm")
    print(f"  Security: {network.security_type.value}")
    print(f"  Channel: {network.channel} ({network.frequency_band.value})")
    print(f"  Vendor: {network.vendor}")

# Filter by band
networks_5ghz = scanner.filter_by_band(FrequencyBand.BAND_5_GHZ)

# Sort by signal strength
sorted_networks = scanner.sort_by_signal(networks)
```

### Decoded Information

The decoder provides rich information about each network:

- **SSID**: Network name
- **BSSID**: MAC address of access point
- **Signal Strength**: In dBm (-30 to -100)
- **Signal Quality**: Percentage (0-100%)
- **Channel**: WiFi channel number
- **Frequency**: In MHz
- **Frequency Band**: 2.4 GHz, 5 GHz, or 6 GHz
- **Security Type**: Open, WEP, WPA, WPA2, WPA3, Enterprise variants
- **Encryption Cipher**: CCMP, TKIP, GCMP
- **WiFi Standard**: 802.11 a/b/g/n/ac/ax/be
- **Vendor**: Manufacturer from OUI database
- **DFS Channels**: Identifies radar-shared channels

---

### Documentation

All reference materials and design notes are under `/docs/`.

### Author

∇θ Operator: Nathan Poinsette
Founder • Archivist • Systems Engineer
