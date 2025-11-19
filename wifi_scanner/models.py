"""
Data models for WiFi network information.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import datetime


class SecurityType(Enum):
    """WiFi security/encryption types."""
    OPEN = "Open"
    WEP = "WEP"
    WPA = "WPA"
    WPA2 = "WPA2"
    WPA3 = "WPA3"
    WPA_WPA2 = "WPA/WPA2"
    WPA2_WPA3 = "WPA2/WPA3"
    WPA_ENTERPRISE = "WPA-Enterprise"
    WPA2_ENTERPRISE = "WPA2-Enterprise"
    WPA3_ENTERPRISE = "WPA3-Enterprise"
    UNKNOWN = "Unknown"


class FrequencyBand(Enum):
    """WiFi frequency bands."""
    BAND_2_4_GHZ = "2.4 GHz"
    BAND_5_GHZ = "5 GHz"
    BAND_6_GHZ = "6 GHz"
    UNKNOWN = "Unknown"


class WiFiStandard(Enum):
    """WiFi standards (802.11 variants)."""
    LEGACY = "802.11 (Legacy)"
    A = "802.11a"
    B = "802.11b"
    G = "802.11g"
    N = "802.11n (WiFi 4)"
    AC = "802.11ac (WiFi 5)"
    AX = "802.11ax (WiFi 6)"
    AX_6E = "802.11ax (WiFi 6E)"
    BE = "802.11be (WiFi 7)"
    UNKNOWN = "Unknown"


@dataclass
class WiFiNetwork:
    """Represents a detected WiFi network with decoded information."""

    # Basic identifiers
    ssid: str
    bssid: str  # MAC address of access point

    # Signal information
    signal_strength_dbm: int  # in dBm (e.g., -50)
    signal_quality_percent: int  # 0-100%

    # Channel and frequency
    channel: int
    frequency_mhz: int
    frequency_band: FrequencyBand
    channel_width_mhz: Optional[int] = None

    # Security
    security_type: SecurityType = SecurityType.UNKNOWN
    encryption_cipher: Optional[str] = None  # e.g., "CCMP", "TKIP"
    authentication: Optional[str] = None  # e.g., "PSK", "802.1X"

    # Additional info
    wifi_standard: WiFiStandard = WiFiStandard.UNKNOWN
    is_hidden: bool = False
    supports_wps: bool = False

    # Metadata
    vendor: Optional[str] = None  # Decoded from BSSID
    country_code: Optional[str] = None

    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    # Raw data for debugging
    raw_data: dict = field(default_factory=dict)

    def __str__(self) -> str:
        """Human-readable string representation."""
        ssid_display = self.ssid if self.ssid else "<Hidden Network>"
        return (
            f"{ssid_display} | "
            f"{self.signal_strength_dbm} dBm ({self.signal_quality_percent}%) | "
            f"Ch {self.channel} ({self.frequency_band.value}) | "
            f"{self.security_type.value}"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "signal_strength_dbm": self.signal_strength_dbm,
            "signal_quality_percent": self.signal_quality_percent,
            "channel": self.channel,
            "frequency_mhz": self.frequency_mhz,
            "frequency_band": self.frequency_band.value,
            "channel_width_mhz": self.channel_width_mhz,
            "security_type": self.security_type.value,
            "encryption_cipher": self.encryption_cipher,
            "authentication": self.authentication,
            "wifi_standard": self.wifi_standard.value,
            "is_hidden": self.is_hidden,
            "supports_wps": self.supports_wps,
            "vendor": self.vendor,
            "country_code": self.country_code,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }

    @property
    def signal_bars(self) -> int:
        """Convert signal quality to 0-4 bars."""
        if self.signal_quality_percent >= 80:
            return 4
        elif self.signal_quality_percent >= 60:
            return 3
        elif self.signal_quality_percent >= 40:
            return 2
        elif self.signal_quality_percent >= 20:
            return 1
        return 0

    @property
    def is_secure(self) -> bool:
        """Check if network uses encryption."""
        return self.security_type not in [SecurityType.OPEN, SecurityType.WEP]
