"""
Cross-platform WiFi Scanner implementation.
"""

import subprocess
import platform
import re
import os
from typing import List, Optional
from datetime import datetime

from .models import WiFiNetwork, SecurityType, FrequencyBand
from .decoder import WiFiDecoder


class WiFiScanner:
    """
    Cross-platform WiFi network scanner.

    Supports Linux, macOS, and Windows platforms.
    """

    def __init__(self, interface: Optional[str] = None):
        """
        Initialize the WiFi scanner.

        Args:
            interface: Optional wireless interface name (e.g., "wlan0", "en0")
                      If not specified, will attempt to auto-detect.
        """
        self.interface = interface
        self.platform = platform.system().lower()
        self._last_scan: List[WiFiNetwork] = []

    def scan(self) -> List[WiFiNetwork]:
        """
        Scan for available WiFi networks.

        Returns:
            List of WiFiNetwork objects with decoded information.

        Raises:
            OSError: If scanning fails or is not supported on this platform.
            PermissionError: If elevated privileges are required.
        """
        if self.platform == "linux":
            networks = self._scan_linux()
        elif self.platform == "darwin":  # macOS
            networks = self._scan_macos()
        elif self.platform == "windows":
            networks = self._scan_windows()
        else:
            raise OSError(f"Unsupported platform: {self.platform}")

        # Enrich networks with decoded information
        for network in networks:
            if network.bssid:
                network.vendor = WiFiDecoder.decode_vendor(network.bssid)

        self._last_scan = networks
        return networks

    def get_interface(self) -> Optional[str]:
        """
        Get the wireless interface being used.

        Returns:
            Interface name or None if not detected.
        """
        if self.interface:
            return self.interface

        if self.platform == "linux":
            return self._get_linux_interface()
        elif self.platform == "darwin":
            return self._get_macos_interface()
        elif self.platform == "windows":
            return self._get_windows_interface()

        return None

    def _get_linux_interface(self) -> Optional[str]:
        """Detect wireless interface on Linux."""
        try:
            # Try to find wireless interfaces
            result = subprocess.run(
                ["ls", "/sys/class/net"],
                capture_output=True,
                text=True,
                timeout=5
            )
            interfaces = result.stdout.strip().split()

            for iface in interfaces:
                wireless_path = f"/sys/class/net/{iface}/wireless"
                if os.path.exists(wireless_path):
                    return iface

            # Fallback: check for common wireless interface names
            for common in ["wlan0", "wlp2s0", "wlp3s0", "wifi0"]:
                if common in interfaces:
                    return common

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        return None

    def _get_macos_interface(self) -> Optional[str]:
        """Detect wireless interface on macOS."""
        try:
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse output to find Wi-Fi interface
            lines = result.stdout.split("\n")
            for i, line in enumerate(lines):
                if "Wi-Fi" in line or "AirPort" in line:
                    # Next line with "Device:" contains the interface
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if "Device:" in lines[j]:
                            return lines[j].split(":")[-1].strip()

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        return "en0"  # Default macOS WiFi interface

    def _get_windows_interface(self) -> Optional[str]:
        """Detect wireless interface on Windows."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse output to find interface name
            for line in result.stdout.split("\n"):
                if "Name" in line and ":" in line:
                    return line.split(":", 1)[1].strip()

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        return None

    def _scan_linux(self) -> List[WiFiNetwork]:
        """Scan for WiFi networks on Linux."""
        networks = []

        # Try nmcli first (NetworkManager)
        try:
            networks = self._scan_linux_nmcli()
            if networks:
                return networks
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        # Try iw scan
        try:
            networks = self._scan_linux_iw()
            if networks:
                return networks
        except (FileNotFoundError, subprocess.SubprocessError, PermissionError):
            pass

        # Try iwlist as fallback
        try:
            networks = self._scan_linux_iwlist()
            if networks:
                return networks
        except (FileNotFoundError, subprocess.SubprocessError, PermissionError):
            pass

        return networks

    def _scan_linux_nmcli(self) -> List[WiFiNetwork]:
        """Scan using nmcli (NetworkManager CLI)."""
        result = subprocess.run(
            [
                "nmcli", "-t", "-f",
                "SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY,MODE",
                "device", "wifi", "list", "--rescan", "yes"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise subprocess.SubprocessError(f"nmcli failed: {result.stderr}")

        networks = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            # nmcli -t uses : as separator, but BSSID also contains :
            # Format: SSID:BSSID:CHAN:FREQ:SIGNAL:SECURITY:MODE
            parts = line.split(":")

            if len(parts) < 12:  # BSSID has 6 parts with :
                continue

            ssid = parts[0]
            # BSSID is parts[1:7] joined
            bssid = ":".join(parts[1:7])
            channel = int(parts[7]) if parts[7].isdigit() else 0
            freq_str = parts[8]  # e.g., "2437 MHz"
            freq_mhz = int(re.search(r"\d+", freq_str).group()) if freq_str else 0
            signal = int(parts[9]) if parts[9].isdigit() else 0
            security = parts[10] if len(parts) > 10 else ""

            # Determine frequency band
            _, band = WiFiDecoder.frequency_to_channel(freq_mhz)

            network = WiFiNetwork(
                ssid=ssid,
                bssid=bssid.upper(),
                signal_strength_dbm=WiFiDecoder.quality_to_dbm(signal),
                signal_quality_percent=signal,
                channel=channel,
                frequency_mhz=freq_mhz,
                frequency_band=band,
                security_type=WiFiDecoder.decode_security_type(security),
                is_hidden=not ssid,
                raw_data={"source": "nmcli", "raw_line": line}
            )

            networks.append(network)

        return networks

    def _scan_linux_iw(self) -> List[WiFiNetwork]:
        """Scan using iw command."""
        interface = self.get_interface()
        if not interface:
            raise OSError("No wireless interface found")

        # iw scan requires root privileges
        result = subprocess.run(
            ["iw", "dev", interface, "scan"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            if "Operation not permitted" in result.stderr:
                raise PermissionError("iw scan requires root privileges")
            raise subprocess.SubprocessError(f"iw scan failed: {result.stderr}")

        networks = []
        current_network = None

        for line in result.stdout.split("\n"):
            line = line.strip()

            # New BSS (network) entry
            if line.startswith("BSS "):
                if current_network:
                    networks.append(current_network)

                bssid_match = re.search(r"BSS ([0-9a-fA-F:]{17})", line)
                bssid = bssid_match.group(1).upper() if bssid_match else ""

                current_network = WiFiNetwork(
                    ssid="",
                    bssid=bssid,
                    signal_strength_dbm=-100,
                    signal_quality_percent=0,
                    channel=0,
                    frequency_mhz=0,
                    frequency_band=FrequencyBand.UNKNOWN,
                    raw_data={"source": "iw"}
                )

            elif current_network:
                # Parse network properties
                if line.startswith("SSID:"):
                    current_network.ssid = line.split(":", 1)[1].strip()
                    current_network.is_hidden = not current_network.ssid

                elif line.startswith("freq:"):
                    freq = int(re.search(r"\d+", line).group())
                    current_network.frequency_mhz = freq
                    channel, band = WiFiDecoder.frequency_to_channel(freq)
                    current_network.channel = channel
                    current_network.frequency_band = band

                elif line.startswith("signal:"):
                    dbm_match = re.search(r"-?\d+", line)
                    if dbm_match:
                        dbm = int(dbm_match.group())
                        current_network.signal_strength_dbm = dbm
                        current_network.signal_quality_percent = WiFiDecoder.dbm_to_quality(dbm)

                elif "WPA" in line or "RSN" in line:
                    if "WPA2" in line or "RSN" in line:
                        current_network.security_type = SecurityType.WPA2
                    else:
                        current_network.security_type = SecurityType.WPA

                elif line.startswith("* Group cipher:"):
                    current_network.encryption_cipher = line.split(":")[-1].strip()

        # Don't forget the last network
        if current_network:
            networks.append(current_network)

        return networks

    def _scan_linux_iwlist(self) -> List[WiFiNetwork]:
        """Scan using iwlist command (legacy)."""
        interface = self.get_interface()
        if not interface:
            raise OSError("No wireless interface found")

        result = subprocess.run(
            ["iwlist", interface, "scan"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            if "Operation not permitted" in result.stderr:
                raise PermissionError("iwlist scan requires root privileges")
            raise subprocess.SubprocessError(f"iwlist scan failed: {result.stderr}")

        networks = []
        current_network = None

        for line in result.stdout.split("\n"):
            line = line.strip()

            # New cell (network) entry
            if "Cell" in line and "Address:" in line:
                if current_network:
                    networks.append(current_network)

                bssid_match = re.search(r"Address:\s*([0-9A-Fa-f:]{17})", line)
                bssid = bssid_match.group(1).upper() if bssid_match else ""

                current_network = WiFiNetwork(
                    ssid="",
                    bssid=bssid,
                    signal_strength_dbm=-100,
                    signal_quality_percent=0,
                    channel=0,
                    frequency_mhz=0,
                    frequency_band=FrequencyBand.UNKNOWN,
                    raw_data={"source": "iwlist"}
                )

            elif current_network:
                if "ESSID:" in line:
                    ssid_match = re.search(r'ESSID:"([^"]*)"', line)
                    if ssid_match:
                        current_network.ssid = ssid_match.group(1)
                        current_network.is_hidden = not current_network.ssid

                elif "Channel:" in line:
                    channel_match = re.search(r"Channel:(\d+)", line)
                    if channel_match:
                        current_network.channel = int(channel_match.group(1))

                elif "Frequency:" in line:
                    freq_match = re.search(r"Frequency:(\d+\.?\d*)", line)
                    if freq_match:
                        # Convert GHz to MHz
                        freq_ghz = float(freq_match.group(1))
                        freq_mhz = int(freq_ghz * 1000)
                        current_network.frequency_mhz = freq_mhz
                        _, band = WiFiDecoder.frequency_to_channel(freq_mhz)
                        current_network.frequency_band = band

                elif "Quality=" in line:
                    quality_match = re.search(r"Quality[=:](\d+)/(\d+)", line)
                    if quality_match:
                        quality = int(quality_match.group(1))
                        max_quality = int(quality_match.group(2))
                        current_network.signal_quality_percent = int(quality * 100 / max_quality)

                    dbm_match = re.search(r"Signal level[=:](-?\d+)", line)
                    if dbm_match:
                        current_network.signal_strength_dbm = int(dbm_match.group(1))

                elif "Encryption key:" in line:
                    if "off" in line.lower():
                        current_network.security_type = SecurityType.OPEN

                elif "IE:" in line:
                    if "WPA2" in line:
                        current_network.security_type = SecurityType.WPA2
                    elif "WPA" in line:
                        if current_network.security_type == SecurityType.WPA2:
                            current_network.security_type = SecurityType.WPA_WPA2
                        else:
                            current_network.security_type = SecurityType.WPA

        if current_network:
            networks.append(current_network)

        return networks

    def _scan_macos(self) -> List[WiFiNetwork]:
        """Scan for WiFi networks on macOS."""
        # Try using airport utility
        airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

        if os.path.exists(airport_path):
            return self._scan_macos_airport(airport_path)

        # Fallback to system_profiler
        return self._scan_macos_system_profiler()

    def _scan_macos_airport(self, airport_path: str) -> List[WiFiNetwork]:
        """Scan using macOS airport utility."""
        result = subprocess.run(
            [airport_path, "-s"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise subprocess.SubprocessError(f"airport scan failed: {result.stderr}")

        networks = []
        lines = result.stdout.strip().split("\n")

        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue

            # Parse airport output format
            # SSID BSSID RSSI CHANNEL HT CC SECURITY
            parts = line.split()
            if len(parts) < 7:
                continue

            # Find BSSID (MAC address pattern)
            bssid_idx = -1
            for i, part in enumerate(parts):
                if re.match(r"[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}", part):
                    bssid_idx = i
                    break

            if bssid_idx < 0:
                continue

            ssid = " ".join(parts[:bssid_idx]) if bssid_idx > 0 else ""
            bssid = parts[bssid_idx].upper()
            rssi = int(parts[bssid_idx + 1]) if parts[bssid_idx + 1].lstrip("-").isdigit() else -100
            channel_str = parts[bssid_idx + 2]

            # Parse channel (may include bandwidth info like "36,+1")
            channel = int(re.search(r"\d+", channel_str).group()) if channel_str else 0

            # Security is usually the last field
            security = parts[-1] if len(parts) > bssid_idx + 3 else ""

            # Determine frequency from channel
            freq_mhz = WiFiDecoder.channel_to_frequency(channel)
            _, band = WiFiDecoder.frequency_to_channel(freq_mhz)

            network = WiFiNetwork(
                ssid=ssid,
                bssid=bssid,
                signal_strength_dbm=rssi,
                signal_quality_percent=WiFiDecoder.dbm_to_quality(rssi),
                channel=channel,
                frequency_mhz=freq_mhz,
                frequency_band=band,
                security_type=WiFiDecoder.decode_security_type(security),
                is_hidden=not ssid,
                raw_data={"source": "airport", "raw_line": line}
            )

            networks.append(network)

        return networks

    def _scan_macos_system_profiler(self) -> List[WiFiNetwork]:
        """Scan using system_profiler (limited info)."""
        result = subprocess.run(
            ["system_profiler", "SPAirPortDataType", "-json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise subprocess.SubprocessError(f"system_profiler failed: {result.stderr}")

        # Note: system_profiler provides limited WiFi scan info
        # It mainly shows the current connection
        # For full scan, airport -s is preferred

        return []

    def _scan_windows(self) -> List[WiFiNetwork]:
        """Scan for WiFi networks on Windows."""
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise subprocess.SubprocessError(f"netsh scan failed: {result.stderr}")

        networks = []
        current_network = None

        for line in result.stdout.split("\n"):
            line = line.strip()

            # New network entry
            if line.startswith("SSID") and ":" in line and "BSSID" not in line:
                if current_network and current_network.bssid:
                    networks.append(current_network)

                ssid = line.split(":", 1)[1].strip()
                current_network = WiFiNetwork(
                    ssid=ssid,
                    bssid="",
                    signal_strength_dbm=-100,
                    signal_quality_percent=0,
                    channel=0,
                    frequency_mhz=0,
                    frequency_band=FrequencyBand.UNKNOWN,
                    is_hidden=not ssid,
                    raw_data={"source": "netsh"}
                )

            elif current_network:
                if line.startswith("BSSID"):
                    bssid = line.split(":", 1)[1].strip().upper()
                    if current_network.bssid and bssid != current_network.bssid:
                        # New BSSID for same SSID - create new network entry
                        networks.append(current_network)
                        current_network = WiFiNetwork(
                            ssid=current_network.ssid,
                            bssid=bssid,
                            signal_strength_dbm=-100,
                            signal_quality_percent=0,
                            channel=0,
                            frequency_mhz=0,
                            frequency_band=FrequencyBand.UNKNOWN,
                            is_hidden=current_network.is_hidden,
                            raw_data={"source": "netsh"}
                        )
                    else:
                        current_network.bssid = bssid

                elif "Signal" in line:
                    signal_match = re.search(r"(\d+)%", line)
                    if signal_match:
                        quality = int(signal_match.group(1))
                        current_network.signal_quality_percent = quality
                        current_network.signal_strength_dbm = WiFiDecoder.quality_to_dbm(quality)

                elif "Channel" in line and ":" in line:
                    channel_match = re.search(r":\s*(\d+)", line)
                    if channel_match:
                        channel = int(channel_match.group(1))
                        current_network.channel = channel
                        freq_mhz = WiFiDecoder.channel_to_frequency(channel)
                        current_network.frequency_mhz = freq_mhz
                        _, band = WiFiDecoder.frequency_to_channel(freq_mhz)
                        current_network.frequency_band = band

                elif "Authentication" in line:
                    auth = line.split(":", 1)[1].strip()
                    current_network.authentication = auth
                    current_network.security_type = WiFiDecoder.decode_security_type(auth)

                elif "Encryption" in line:
                    cipher = line.split(":", 1)[1].strip()
                    current_network.encryption_cipher = cipher

        # Don't forget the last network
        if current_network and current_network.bssid:
            networks.append(current_network)

        return networks

    def get_last_scan(self) -> List[WiFiNetwork]:
        """
        Get results from the last scan without rescanning.

        Returns:
            List of WiFiNetwork objects from last scan.
        """
        return self._last_scan

    def sort_by_signal(self, networks: Optional[List[WiFiNetwork]] = None) -> List[WiFiNetwork]:
        """
        Sort networks by signal strength (strongest first).

        Args:
            networks: Networks to sort, or None to use last scan results.

        Returns:
            Sorted list of networks.
        """
        if networks is None:
            networks = self._last_scan

        return sorted(networks, key=lambda n: n.signal_strength_dbm, reverse=True)

    def filter_by_band(
        self,
        band: FrequencyBand,
        networks: Optional[List[WiFiNetwork]] = None
    ) -> List[WiFiNetwork]:
        """
        Filter networks by frequency band.

        Args:
            band: Frequency band to filter by.
            networks: Networks to filter, or None to use last scan results.

        Returns:
            Filtered list of networks.
        """
        if networks is None:
            networks = self._last_scan

        return [n for n in networks if n.frequency_band == band]

    def filter_by_security(
        self,
        security_types: List[SecurityType],
        networks: Optional[List[WiFiNetwork]] = None
    ) -> List[WiFiNetwork]:
        """
        Filter networks by security type.

        Args:
            security_types: List of security types to include.
            networks: Networks to filter, or None to use last scan results.

        Returns:
            Filtered list of networks.
        """
        if networks is None:
            networks = self._last_scan

        return [n for n in networks if n.security_type in security_types]
