"""
Command-line interface for the WiFi Scanner.
"""

import argparse
import json
import sys
from typing import List, Optional

from .models import WiFiNetwork, FrequencyBand, SecurityType
from .scanner import WiFiScanner
from .decoder import WiFiDecoder


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="wifi-scanner",
        description="WiFi Scanner and Decoder - Detect and analyze wireless networks globally",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Basic scan with table output
  %(prog)s -v                 # Verbose output with all details
  %(prog)s --json             # JSON output for programmatic use
  %(prog)s --band 5ghz        # Show only 5 GHz networks
  %(prog)s --sort signal      # Sort by signal strength
  %(prog)s --open             # Show only open networks
  %(prog)s --secure           # Show only secured networks
        """
    )

    # Output format options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed information for each network"
    )
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    output_group.add_argument(
        "--csv",
        action="store_true",
        help="Output results in CSV format"
    )
    output_group.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Minimal output (SSID and signal only)"
    )

    # Filter options
    filter_group = parser.add_argument_group("Filter Options")
    filter_group.add_argument(
        "--band",
        choices=["2.4ghz", "5ghz", "6ghz", "all"],
        default="all",
        help="Filter by frequency band (default: all)"
    )
    filter_group.add_argument(
        "--open",
        action="store_true",
        help="Show only open (unencrypted) networks"
    )
    filter_group.add_argument(
        "--secure",
        action="store_true",
        help="Show only secured (encrypted) networks"
    )
    filter_group.add_argument(
        "--hidden",
        action="store_true",
        help="Include hidden networks"
    )
    filter_group.add_argument(
        "--min-signal",
        type=int,
        default=-100,
        metavar="DBM",
        help="Minimum signal strength in dBm (default: -100)"
    )

    # Sort options
    sort_group = parser.add_argument_group("Sort Options")
    sort_group.add_argument(
        "--sort",
        choices=["signal", "ssid", "channel", "security"],
        default="signal",
        help="Sort results by field (default: signal)"
    )
    sort_group.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse sort order"
    )

    # Scanner options
    scanner_group = parser.add_argument_group("Scanner Options")
    scanner_group.add_argument(
        "-i", "--interface",
        help="Wireless interface to use (auto-detected if not specified)"
    )
    scanner_group.add_argument(
        "--no-rescan",
        action="store_true",
        help="Use cached results if available"
    )

    # Analysis options
    analysis_group = parser.add_argument_group("Analysis Options")
    analysis_group.add_argument(
        "--channel-usage",
        action="store_true",
        help="Show channel usage analysis"
    )
    analysis_group.add_argument(
        "--vendor-stats",
        action="store_true",
        help="Show vendor statistics"
    )

    return parser


def format_signal_bar(quality_percent: int) -> str:
    """Format signal strength as visual bars."""
    bars = quality_percent // 20
    return "█" * bars + "░" * (5 - bars)


def print_table(networks: List[WiFiNetwork], verbose: bool = False):
    """Print networks in a formatted table."""
    if not networks:
        print("No networks found.")
        return

    # Determine column widths
    ssid_width = max(20, max(len(n.ssid or "<Hidden>") for n in networks))
    ssid_width = min(ssid_width, 32)  # Cap at 32 chars

    # Header
    if verbose:
        print(f"{'SSID':<{ssid_width}}  {'BSSID':<17}  {'Signal':>6}  {'Ch':>3}  {'Band':<8}  {'Security':<15}  {'Vendor'}")
        print("=" * (ssid_width + 80))
    else:
        print(f"{'SSID':<{ssid_width}}  {'Signal':>8}  {'Ch':>3}  {'Band':<8}  {'Security':<12}")
        print("=" * (ssid_width + 45))

    # Networks
    for network in networks:
        ssid_display = network.ssid if network.ssid else "<Hidden>"
        if len(ssid_display) > ssid_width:
            ssid_display = ssid_display[:ssid_width-3] + "..."

        signal_display = f"{network.signal_strength_dbm}dBm"

        if verbose:
            vendor = network.vendor or "Unknown"
            print(
                f"{ssid_display:<{ssid_width}}  "
                f"{network.bssid:<17}  "
                f"{signal_display:>6}  "
                f"{network.channel:>3}  "
                f"{network.frequency_band.value:<8}  "
                f"{network.security_type.value:<15}  "
                f"{vendor}"
            )
        else:
            print(
                f"{ssid_display:<{ssid_width}}  "
                f"{signal_display:>8}  "
                f"{network.channel:>3}  "
                f"{network.frequency_band.value:<8}  "
                f"{network.security_type.value:<12}"
            )

    print(f"\nTotal: {len(networks)} networks found")


def print_quiet(networks: List[WiFiNetwork]):
    """Print minimal output."""
    for network in networks:
        ssid = network.ssid if network.ssid else "<Hidden>"
        print(f"{ssid}: {network.signal_strength_dbm}dBm ({network.signal_quality_percent}%)")


def print_json(networks: List[WiFiNetwork]):
    """Print networks as JSON."""
    data = [network.to_dict() for network in networks]
    print(json.dumps(data, indent=2))


def print_csv(networks: List[WiFiNetwork]):
    """Print networks as CSV."""
    # Header
    print("SSID,BSSID,Signal_dBm,Signal_Percent,Channel,Frequency_MHz,Band,Security,Vendor")

    # Data rows
    for network in networks:
        ssid = network.ssid.replace(",", ";") if network.ssid else ""
        vendor = (network.vendor or "").replace(",", ";")
        print(
            f'"{ssid}",'
            f"{network.bssid},"
            f"{network.signal_strength_dbm},"
            f"{network.signal_quality_percent},"
            f"{network.channel},"
            f"{network.frequency_mhz},"
            f"{network.frequency_band.value},"
            f"{network.security_type.value},"
            f'"{vendor}"'
        )


def print_channel_usage(networks: List[WiFiNetwork]):
    """Print channel usage analysis."""
    print("\n--- Channel Usage Analysis ---\n")

    # 2.4 GHz channels
    channels_2_4 = {i: 0 for i in range(1, 15)}
    # 5 GHz channels
    channels_5 = {}

    for network in networks:
        if network.frequency_band == FrequencyBand.BAND_2_4_GHZ:
            if network.channel in channels_2_4:
                channels_2_4[network.channel] += 1
        elif network.frequency_band == FrequencyBand.BAND_5_GHZ:
            if network.channel not in channels_5:
                channels_5[network.channel] = 0
            channels_5[network.channel] += 1

    print("2.4 GHz Band:")
    for ch in [1, 6, 11]:  # Non-overlapping channels
        count = channels_2_4[ch]
        bar = "█" * count
        print(f"  Ch {ch:2}: {bar} ({count} networks)")

    print("\n  Other 2.4 GHz channels:")
    for ch in [2, 3, 4, 5, 7, 8, 9, 10, 12, 13]:
        count = channels_2_4[ch]
        if count > 0:
            print(f"  Ch {ch:2}: {'█' * count} ({count})")

    if channels_5:
        print("\n5 GHz Band:")
        for ch in sorted(channels_5.keys()):
            count = channels_5[ch]
            bar = "█" * count
            dfs = " (DFS)" if WiFiDecoder.is_dfs_channel(ch) else ""
            print(f"  Ch {ch:3}: {bar} ({count} networks){dfs}")

    # Recommendations
    print("\nRecommendations:")
    min_2_4 = min(channels_2_4[ch] for ch in [1, 6, 11])
    best_2_4 = [ch for ch in [1, 6, 11] if channels_2_4[ch] == min_2_4]
    print(f"  Best 2.4 GHz channel(s): {', '.join(map(str, best_2_4))} ({min_2_4} networks)")

    if channels_5:
        min_5 = min(channels_5.values())
        best_5 = [ch for ch, count in channels_5.items() if count == min_5]
        print(f"  Least crowded 5 GHz channel(s): {', '.join(map(str, best_5[:3]))} ({min_5} networks)")


def print_vendor_stats(networks: List[WiFiNetwork]):
    """Print vendor statistics."""
    print("\n--- Vendor Statistics ---\n")

    vendors = {}
    for network in networks:
        vendor = network.vendor or "Unknown"
        if vendor not in vendors:
            vendors[vendor] = 0
        vendors[vendor] += 1

    # Sort by count
    sorted_vendors = sorted(vendors.items(), key=lambda x: x[1], reverse=True)

    for vendor, count in sorted_vendors[:15]:  # Top 15
        bar = "█" * count
        print(f"  {vendor:<20}: {bar} ({count})")

    if len(sorted_vendors) > 15:
        print(f"\n  ... and {len(sorted_vendors) - 15} more vendors")


def apply_filters(
    networks: List[WiFiNetwork],
    args: argparse.Namespace
) -> List[WiFiNetwork]:
    """Apply filters to network list based on arguments."""
    result = networks

    # Band filter
    if args.band != "all":
        band_map = {
            "2.4ghz": FrequencyBand.BAND_2_4_GHZ,
            "5ghz": FrequencyBand.BAND_5_GHZ,
            "6ghz": FrequencyBand.BAND_6_GHZ,
        }
        band = band_map.get(args.band)
        if band:
            result = [n for n in result if n.frequency_band == band]

    # Security filter
    if args.open:
        result = [n for n in result if n.security_type == SecurityType.OPEN]
    elif args.secure:
        result = [n for n in result if n.security_type != SecurityType.OPEN]

    # Hidden networks filter
    if not args.hidden:
        result = [n for n in result if n.ssid]

    # Signal strength filter
    result = [n for n in result if n.signal_strength_dbm >= args.min_signal]

    return result


def apply_sort(
    networks: List[WiFiNetwork],
    args: argparse.Namespace
) -> List[WiFiNetwork]:
    """Sort network list based on arguments."""
    if args.sort == "signal":
        key = lambda n: n.signal_strength_dbm
        reverse = not args.reverse  # Strongest first by default
    elif args.sort == "ssid":
        key = lambda n: (n.ssid or "").lower()
        reverse = args.reverse
    elif args.sort == "channel":
        key = lambda n: n.channel
        reverse = args.reverse
    elif args.sort == "security":
        key = lambda n: n.security_type.value
        reverse = args.reverse
    else:
        return networks

    return sorted(networks, key=key, reverse=reverse)


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        # Initialize scanner
        scanner = WiFiScanner(interface=args.interface)

        # Get interface info
        interface = scanner.get_interface()
        if not args.json and not args.csv and not args.quiet:
            if interface:
                print(f"Scanning on interface: {interface}")
            print("Scanning for WiFi networks...\n")

        # Perform scan
        networks = scanner.scan()

        if not networks:
            if args.json:
                print("[]")
            elif args.csv:
                print("No networks found")
            else:
                print("No WiFi networks found.")
                print("\nPossible reasons:")
                print("  - WiFi interface is disabled")
                print("  - No networks in range")
                print("  - Insufficient permissions (try with sudo)")
            return 0

        # Apply filters
        networks = apply_filters(networks, args)

        # Apply sorting
        networks = apply_sort(networks, args)

        # Output results
        if args.json:
            print_json(networks)
        elif args.csv:
            print_csv(networks)
        elif args.quiet:
            print_quiet(networks)
        else:
            print_table(networks, verbose=args.verbose)

        # Additional analysis
        if args.channel_usage:
            print_channel_usage(scanner.get_last_scan())

        if args.vendor_stats:
            print_vendor_stats(scanner.get_last_scan())

        return 0

    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        print("Try running with elevated privileges (sudo).", file=sys.stderr)
        return 1

    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nScan cancelled.")
        return 130

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
