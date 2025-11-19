"""
WiFi Decoder - Interprets and enriches WiFi network information.
"""

import re
from typing import Optional, Tuple
from .models import (
    WiFiNetwork,
    SecurityType,
    FrequencyBand,
    WiFiStandard
)


class WiFiDecoder:
    """Decodes and enriches WiFi network information."""

    # OUI (Organizationally Unique Identifier) database for vendor lookup
    # This is a small subset - in production, use a full OUI database
    OUI_DATABASE = {
        "00:00:0C": "Cisco",
        "00:01:42": "Cisco",
        "00:03:6B": "Cisco",
        "00:1A:A0": "Dell",
        "00:14:22": "Dell",
        "00:0C:29": "VMware",
        "00:50:56": "VMware",
        "00:1C:42": "Parallels",
        "08:00:27": "VirtualBox",
        "00:17:88": "Philips Hue",
        "B8:27:EB": "Raspberry Pi",
        "DC:A6:32": "Raspberry Pi",
        "E4:5F:01": "Raspberry Pi",
        "AC:BC:32": "Apple",
        "00:1F:F3": "Apple",
        "28:CF:E9": "Apple",
        "3C:22:FB": "Apple",
        "70:56:81": "Apple",
        "00:1E:C2": "Apple",
        "00:50:F2": "Microsoft",
        "00:15:5D": "Microsoft Hyper-V",
        "00:03:FF": "Microsoft",
        "94:65:9C": "Intel",
        "00:1B:21": "Intel",
        "00:1E:67": "Intel",
        "3C:97:0E": "Intel",
        "7C:5C:F8": "Intel",
        "00:26:C7": "Intel",
        "F8:FF:C2": "Apple",
        "00:23:12": "Apple",
        "00:25:00": "Apple",
        "00:26:08": "Apple",
        "00:26:B0": "Apple",
        "00:26:BB": "Apple",
        "18:AF:8F": "Apple",
        "24:A2:E1": "Apple",
        "28:6A:B8": "Apple",
        "34:C0:59": "Apple",
        "40:6C:8F": "Apple",
        "44:D8:84": "Apple",
        "5C:F9:38": "Apple",
        "60:03:08": "Apple",
        "68:A8:6D": "Apple",
        "70:DE:E2": "Apple",
        "78:31:C1": "Apple",
        "78:CA:39": "Apple",
        "7C:D1:C3": "Apple",
        "84:FC:FE": "Apple",
        "88:66:A5": "Apple",
        "8C:58:77": "Apple",
        "8C:FA:BA": "Apple",
        "98:03:D8": "Apple",
        "98:FE:94": "Apple",
        "9C:04:EB": "Apple",
        "9C:20:7B": "Apple",
        "A4:5E:60": "Apple",
        "A8:86:DD": "Apple",
        "A8:96:8A": "Apple",
        "AC:87:A3": "Apple",
        "B0:34:95": "Apple",
        "B8:E8:56": "Apple",
        "BC:52:B7": "Apple",
        "C0:63:94": "Apple",
        "C8:1E:E7": "Apple",
        "C8:6F:1D": "Apple",
        "C8:B5:B7": "Apple",
        "CC:25:EF": "Apple",
        "D0:23:DB": "Apple",
        "D4:F4:6F": "Apple",
        "D8:1D:72": "Apple",
        "D8:9E:3F": "Apple",
        "DC:2B:2A": "Apple",
        "E0:F5:C6": "Apple",
        "E4:8B:7F": "Apple",
        "E8:06:88": "Apple",
        "F0:24:75": "Apple",
        "F0:99:BF": "Apple",
        "F0:D1:A9": "Apple",
        "F4:5C:89": "Apple",
        "F8:1E:DF": "Apple",
        "10:DD:B1": "Apple",
        "14:10:9F": "Apple",
        "14:5A:05": "Apple",
        "1C:36:BB": "Apple",
        "20:78:F0": "Apple",
        "80:00:6E": "Apple",
        "80:92:9F": "Apple",
        "20:C9:D0": "Apple",
        "24:F0:94": "Apple",
        "2C:BE:08": "Apple",
        "2C:F0:EE": "Apple",
        "30:63:6B": "Apple",
        "38:0F:4A": "Apple",
        "38:C9:86": "Apple",
        "3C:15:C2": "Apple",
        "3C:E0:72": "Apple",
        "40:30:04": "Apple",
        "48:74:6E": "Apple",
        "48:D7:05": "Apple",
        "50:32:75": "Apple",
        "54:26:96": "Apple",
        "54:72:4F": "Apple",
        "54:9F:13": "Apple",
        "54:AE:27": "Apple",
        "54:EA:A8": "Apple",
        "58:1F:AA": "Apple",
        "58:55:CA": "Apple",
        "60:C5:47": "Apple",
        "60:D9:C7": "Apple",
        "60:F8:1D": "Apple",
        "64:20:0C": "Apple",
        "64:76:BA": "Apple",
        "64:9A:BE": "Apple",
        "64:A3:CB": "Apple",
        "64:B0:A6": "Apple",
        "64:E6:82": "Apple",
        "6C:40:08": "Apple",
        "6C:70:9F": "Apple",
        "6C:94:F8": "Apple",
        "6C:C2:6B": "Apple",
        "70:11:24": "Apple",
        "70:3E:AC": "Apple",
        "70:48:0F": "Apple",
        "70:73:CB": "Apple",
        "70:A2:B3": "Apple",
        "70:CD:60": "Apple",
        "70:EC:E4": "Apple",
        "74:E1:B6": "Apple",
        "74:E2:F5": "Apple",
        "78:67:D7": "Apple",
        "78:6C:1C": "Apple",
        "78:7E:61": "Apple",
        "78:9F:70": "Apple",
        "78:A3:E4": "Apple",
        "78:FD:94": "Apple",
        "7C:01:91": "Apple",
        "7C:04:D0": "Apple",
        "7C:11:BE": "Apple",
        "7C:6D:62": "Apple",
        "7C:C3:A1": "Apple",
        "7C:F0:5F": "Apple",
        "80:49:71": "Apple",
        "80:82:23": "Apple",
        "80:E6:50": "Apple",
        "84:29:99": "Apple",
        "84:38:35": "Apple",
        "84:78:8B": "Apple",
        "84:85:06": "Apple",
        "84:89:AD": "Apple",
        "84:8E:0C": "Apple",
        "84:A1:34": "Apple",
        "84:B1:53": "Apple",
        "84:FC:AC": "Apple",
        "88:19:08": "Apple",
        "88:1F:A1": "Apple",
        "88:53:95": "Apple",
        "88:63:DF": "Apple",
        "88:6B:6E": "Apple",
        "88:C6:63": "Apple",
        "88:CB:87": "Apple",
        "88:E8:7F": "Apple",
        "20:A2:E4": "NETGEAR",
        "00:1B:2F": "NETGEAR",
        "00:1E:2A": "NETGEAR",
        "00:1F:33": "NETGEAR",
        "00:22:3F": "NETGEAR",
        "00:24:B2": "NETGEAR",
        "00:26:F2": "NETGEAR",
        "08:36:C9": "NETGEAR",
        "08:BD:43": "NETGEAR",
        "10:0C:6B": "NETGEAR",
        "10:0D:7F": "NETGEAR",
        "20:0C:C8": "NETGEAR",
        "20:4E:7F": "NETGEAR",
        "28:80:88": "NETGEAR",
        "28:C6:8E": "NETGEAR",
        "2C:B0:5D": "NETGEAR",
        "30:46:9A": "NETGEAR",
        "00:18:E7": "TP-Link",
        "00:1D:0F": "TP-Link",
        "00:21:27": "TP-Link",
        "00:23:CD": "TP-Link",
        "00:25:86": "TP-Link",
        "00:27:19": "TP-Link",
        "14:CC:20": "TP-Link",
        "14:CF:92": "TP-Link",
        "18:A6:F7": "TP-Link",
        "1C:3B:F3": "TP-Link",
        "24:69:68": "TP-Link",
        "30:B5:C2": "TP-Link",
        "54:C8:0F": "TP-Link",
        "5C:89:9A": "TP-Link",
        "60:32:B1": "TP-Link",
        "64:66:B3": "TP-Link",
        "64:70:02": "TP-Link",
        "6C:5A:B0": "TP-Link",
        "70:4F:57": "TP-Link",
        "74:DA:38": "TP-Link",
        "78:44:76": "TP-Link",
        "00:90:A9": "Linksys",
        "00:06:25": "Linksys",
        "00:0C:41": "Linksys",
        "00:0F:66": "Linksys",
        "00:12:17": "Linksys",
        "00:14:BF": "Linksys",
        "00:16:B6": "Linksys",
        "00:18:39": "Linksys",
        "00:18:F8": "Linksys",
        "00:1A:70": "Linksys",
        "00:1C:10": "Linksys",
        "00:1D:7E": "Linksys",
        "00:1E:E5": "Linksys",
        "00:21:29": "Linksys",
        "00:22:6B": "Linksys",
        "00:23:69": "Linksys",
        "00:24:01": "Linksys",
        "00:25:9C": "Linksys",
        "08:86:3B": "Belkin",
        "14:91:82": "Belkin",
        "30:23:03": "Belkin",
        "94:10:3E": "Belkin",
        "94:44:52": "Belkin",
        "B4:75:0E": "Belkin",
        "C0:56:27": "Belkin",
        "C4:41:1E": "Belkin",
        "EC:1A:59": "Belkin",
        "00:0C:43": "Ralink",
        "00:17:A5": "Ralink",
        "00:1C:51": "Ralink",
        "00:E0:4C": "Realtek",
        "00:1A:3F": "Google",
        "3C:5A:B4": "Google",
        "54:60:09": "Google",
        "58:CB:52": "Google",
        "94:EB:2C": "Google",
        "A4:77:33": "Google",
        "F4:F5:D8": "Google",
        "F4:F5:E8": "Google",
        "00:12:FB": "Samsung",
        "00:15:99": "Samsung",
        "00:15:B9": "Samsung",
        "00:16:32": "Samsung",
        "00:16:6B": "Samsung",
        "00:16:6C": "Samsung",
        "00:17:C9": "Samsung",
        "00:17:D5": "Samsung",
        "00:18:AF": "Samsung",
        "00:1A:8A": "Samsung",
        "00:1B:98": "Samsung",
        "00:1C:43": "Samsung",
        "00:1D:25": "Samsung",
        "00:1D:F6": "Samsung",
        "00:1E:7D": "Samsung",
        "00:1F:CC": "Samsung",
        "00:21:19": "Samsung",
        "00:21:4C": "Samsung",
        "00:21:D1": "Samsung",
        "00:21:D2": "Samsung",
        "00:23:39": "Samsung",
        "00:23:3A": "Samsung",
        "00:23:99": "Samsung",
        "00:23:D6": "Samsung",
        "00:23:D7": "Samsung",
        "00:24:54": "Samsung",
        "00:24:90": "Samsung",
        "00:24:91": "Samsung",
        "00:24:E9": "Samsung",
        "00:25:66": "Samsung",
        "00:25:67": "Samsung",
        "00:26:37": "Samsung",
        "00:26:5D": "Samsung",
        "00:26:5F": "Samsung",
        "08:08:C2": "Samsung",
        "08:37:3D": "Samsung",
        "08:D4:2B": "Samsung",
        "08:EC:A9": "Samsung",
        "08:FD:0E": "Samsung",
        "0C:14:20": "Samsung",
        "0C:71:5D": "Samsung",
        "0C:89:10": "Samsung",
        "0C:DF:A4": "Samsung",
        "10:1D:C0": "Samsung",
        "10:30:47": "Samsung",
        "10:D5:42": "Samsung",
        "14:49:E0": "Samsung",
        "14:56:8E": "Samsung",
        "14:89:FD": "Samsung",
        "14:A3:64": "Samsung",
        "14:B4:84": "Samsung",
        "18:1E:78": "Samsung",
        "18:22:7E": "Samsung",
        "18:3A:2D": "Samsung",
        "18:3F:47": "Samsung",
        "18:46:17": "Samsung",
        "18:67:B0": "Samsung",
        "18:83:BF": "Samsung",
        "18:89:5B": "Samsung",
        "18:D2:76": "Samsung",
        "1C:5A:3E": "Samsung",
        "1C:62:B8": "Samsung",
        "1C:66:AA": "Samsung",
        "20:13:E0": "Samsung",
        "20:55:31": "Samsung",
        "20:64:32": "Samsung",
        "20:6E:9C": "Samsung",
        "20:D3:90": "Samsung",
        "24:4B:03": "Samsung",
        "24:4B:81": "Samsung",
        "24:C6:96": "Samsung",
        "24:DB:ED": "Samsung",
        "28:27:BF": "Samsung",
        "28:98:7B": "Samsung",
        "28:BA:B5": "Samsung",
        "28:CC:01": "Samsung",
        "2C:44:01": "Samsung",
        "2C:AE:2B": "Samsung",
        "30:19:66": "Samsung",
        "30:96:FB": "Samsung",
        "30:C7:AE": "Samsung",
        "30:CD:A7": "Samsung",
        "30:D6:C9": "Samsung",
        "34:23:BA": "Samsung",
        "34:AA:8B": "Samsung",
        "34:BE:00": "Samsung",
        "34:C3:AC": "Samsung",
        "38:01:95": "Samsung",
        "38:0A:94": "Samsung",
        "38:16:D1": "Samsung",
        "38:2D:D1": "Samsung",
        "3C:5A:37": "Samsung",
        "3C:62:00": "Samsung",
        "3C:8B:FE": "Samsung",
        "40:0E:85": "Samsung",
        "40:16:3B": "Samsung",
        "40:D3:AE": "Samsung",
        "44:4E:1A": "Samsung",
        "44:6D:6C": "Samsung",
        "44:78:3E": "Samsung",
        "48:44:F7": "Samsung",
        "48:A7:4E": "Samsung",
        "4C:3C:16": "Samsung",
        "4C:BC:A5": "Samsung",
        "50:01:BB": "Samsung",
        "50:32:37": "Samsung",
        "50:56:BF": "Samsung",
        "50:85:69": "Samsung",
        "50:A4:C8": "Samsung",
        "50:B7:C3": "Samsung",
        "50:C8:E5": "Samsung",
        "50:CC:F8": "Samsung",
        "50:F0:D3": "Samsung",
        "50:FC:9F": "Samsung",
        "54:40:AD": "Samsung",
        "54:88:0E": "Samsung",
        "54:92:BE": "Samsung",
        "54:9B:12": "Samsung",
        "58:C3:8B": "Samsung",
    }

    # 2.4 GHz channel to frequency mapping
    CHANNEL_FREQ_2_4_GHZ = {
        1: 2412, 2: 2417, 3: 2422, 4: 2427, 5: 2432,
        6: 2437, 7: 2442, 8: 2447, 9: 2452, 10: 2457,
        11: 2462, 12: 2467, 13: 2472, 14: 2484
    }

    # 5 GHz channel to frequency mapping
    CHANNEL_FREQ_5_GHZ = {
        36: 5180, 40: 5200, 44: 5220, 48: 5240,
        52: 5260, 56: 5280, 60: 5300, 64: 5320,
        100: 5500, 104: 5520, 108: 5540, 112: 5560,
        116: 5580, 120: 5600, 124: 5620, 128: 5640,
        132: 5660, 136: 5680, 140: 5700, 144: 5720,
        149: 5745, 153: 5765, 157: 5785, 161: 5805,
        165: 5825
    }

    # 6 GHz channel to frequency mapping (WiFi 6E)
    CHANNEL_FREQ_6_GHZ = {
        1: 5955, 5: 5975, 9: 5995, 13: 6015, 17: 6035,
        21: 6055, 25: 6075, 29: 6095, 33: 6115, 37: 6135,
        41: 6155, 45: 6175, 49: 6195, 53: 6215, 57: 6235,
        61: 6255, 65: 6275, 69: 6295, 73: 6315, 77: 6335,
        81: 6355, 85: 6375, 89: 6395, 93: 6415, 97: 6435,
        101: 6455, 105: 6475, 109: 6495, 113: 6515, 117: 6535,
        121: 6555, 125: 6575, 129: 6595, 133: 6615, 137: 6635,
        141: 6655, 145: 6675, 149: 6695, 153: 6715, 157: 6735,
        161: 6755, 165: 6775, 169: 6795, 173: 6815, 177: 6835,
        181: 6855, 185: 6875, 189: 6895, 193: 6915, 197: 6935,
        201: 6955, 205: 6975, 209: 6995, 213: 7015, 217: 7035,
        221: 7055, 225: 7075, 229: 7095, 233: 7115
    }

    @classmethod
    def decode_vendor(cls, bssid: str) -> Optional[str]:
        """
        Decode vendor from BSSID (MAC address) using OUI lookup.

        Args:
            bssid: MAC address in format "XX:XX:XX:XX:XX:XX"

        Returns:
            Vendor name or None if not found
        """
        if not bssid:
            return None

        # Normalize MAC address format
        mac = bssid.upper().replace("-", ":")

        # Get OUI (first 3 octets)
        oui = ":".join(mac.split(":")[:3])

        return cls.OUI_DATABASE.get(oui)

    @classmethod
    def frequency_to_channel(cls, frequency_mhz: int) -> Tuple[int, FrequencyBand]:
        """
        Convert frequency to channel number and band.

        Args:
            frequency_mhz: Frequency in MHz

        Returns:
            Tuple of (channel_number, frequency_band)
        """
        # Check 2.4 GHz band
        for channel, freq in cls.CHANNEL_FREQ_2_4_GHZ.items():
            if freq == frequency_mhz:
                return channel, FrequencyBand.BAND_2_4_GHZ

        # Check 5 GHz band
        for channel, freq in cls.CHANNEL_FREQ_5_GHZ.items():
            if freq == frequency_mhz:
                return channel, FrequencyBand.BAND_5_GHZ

        # Check 6 GHz band
        for channel, freq in cls.CHANNEL_FREQ_6_GHZ.items():
            if freq == frequency_mhz:
                return channel, FrequencyBand.BAND_6_GHZ

        # Estimate band based on frequency range
        if 2400 <= frequency_mhz <= 2500:
            return 0, FrequencyBand.BAND_2_4_GHZ
        elif 5150 <= frequency_mhz <= 5925:
            return 0, FrequencyBand.BAND_5_GHZ
        elif 5925 <= frequency_mhz <= 7125:
            return 0, FrequencyBand.BAND_6_GHZ

        return 0, FrequencyBand.UNKNOWN

    @classmethod
    def channel_to_frequency(cls, channel: int, band: FrequencyBand = None) -> int:
        """
        Convert channel number to frequency.

        Args:
            channel: Channel number
            band: Optional frequency band hint

        Returns:
            Frequency in MHz
        """
        # Try 2.4 GHz first
        if channel in cls.CHANNEL_FREQ_2_4_GHZ:
            return cls.CHANNEL_FREQ_2_4_GHZ[channel]

        # Try 5 GHz
        if channel in cls.CHANNEL_FREQ_5_GHZ:
            return cls.CHANNEL_FREQ_5_GHZ[channel]

        # Try 6 GHz
        if channel in cls.CHANNEL_FREQ_6_GHZ:
            return cls.CHANNEL_FREQ_6_GHZ[channel]

        return 0

    @classmethod
    def dbm_to_quality(cls, dbm: int) -> int:
        """
        Convert signal strength in dBm to quality percentage.

        Uses a reasonable conversion formula:
        - -30 dBm = 100% (excellent)
        - -90 dBm = 0% (unusable)

        Args:
            dbm: Signal strength in dBm

        Returns:
            Quality percentage (0-100)
        """
        if dbm >= -30:
            return 100
        elif dbm <= -90:
            return 0
        else:
            # Linear interpolation between -30 and -90
            return int((dbm + 90) * (100 / 60))

    @classmethod
    def quality_to_dbm(cls, quality: int) -> int:
        """
        Convert quality percentage to approximate dBm.

        Args:
            quality: Quality percentage (0-100)

        Returns:
            Approximate signal strength in dBm
        """
        # Reverse of dbm_to_quality
        return int(-90 + (quality * 60 / 100))

    @classmethod
    def decode_security_type(cls, security_string: str) -> SecurityType:
        """
        Decode security type from various string formats.

        Args:
            security_string: Security string from scanner output

        Returns:
            SecurityType enum value
        """
        security_lower = security_string.lower()

        # Check for Enterprise authentication
        if "enterprise" in security_lower or "802.1x" in security_lower:
            if "wpa3" in security_lower:
                return SecurityType.WPA3_ENTERPRISE
            elif "wpa2" in security_lower:
                return SecurityType.WPA2_ENTERPRISE
            else:
                return SecurityType.WPA_ENTERPRISE

        # Check for WPA3
        if "wpa3" in security_lower:
            if "wpa2" in security_lower:
                return SecurityType.WPA2_WPA3
            return SecurityType.WPA3

        # Check for WPA2
        if "wpa2" in security_lower:
            if "wpa" in security_lower and "wpa2" in security_lower:
                # Check if both WPA and WPA2 are mentioned
                if security_lower.index("wpa") != security_lower.index("wpa2"):
                    return SecurityType.WPA_WPA2
            return SecurityType.WPA2

        # Check for WPA
        if "wpa" in security_lower:
            return SecurityType.WPA

        # Check for WEP
        if "wep" in security_lower:
            return SecurityType.WEP

        # Check for Open/None
        if "open" in security_lower or "none" in security_lower or security_lower == "":
            return SecurityType.OPEN

        return SecurityType.UNKNOWN

    @classmethod
    def decode_wifi_standard(cls, frequency_mhz: int, info_string: str = "") -> WiFiStandard:
        """
        Determine WiFi standard based on frequency and other info.

        Args:
            frequency_mhz: Frequency in MHz
            info_string: Additional info string that may contain standard hints

        Returns:
            WiFiStandard enum value
        """
        info_lower = info_string.lower()

        # Check for explicit standard mentions
        if "wifi 7" in info_lower or "802.11be" in info_lower or "be" in info_lower:
            return WiFiStandard.BE
        if "wifi 6e" in info_lower or "6ghz" in info_lower:
            return WiFiStandard.AX_6E
        if "wifi 6" in info_lower or "802.11ax" in info_lower or "ax" in info_lower:
            return WiFiStandard.AX
        if "wifi 5" in info_lower or "802.11ac" in info_lower or "ac" in info_lower:
            return WiFiStandard.AC
        if "wifi 4" in info_lower or "802.11n" in info_lower:
            return WiFiStandard.N
        if "802.11g" in info_lower:
            return WiFiStandard.G
        if "802.11a" in info_lower:
            return WiFiStandard.A
        if "802.11b" in info_lower:
            return WiFiStandard.B

        # Infer from frequency
        if frequency_mhz > 5925:  # 6 GHz band
            return WiFiStandard.AX_6E
        elif frequency_mhz > 5000:  # 5 GHz band
            # Could be a, n, ac, or ax - assume at least n
            return WiFiStandard.N
        elif frequency_mhz > 2400:  # 2.4 GHz band
            # Could be b, g, n, or ax - assume at least g
            return WiFiStandard.G

        return WiFiStandard.UNKNOWN

    @classmethod
    def get_channel_width_options(cls, band: FrequencyBand) -> list:
        """
        Get available channel width options for a frequency band.

        Args:
            band: Frequency band

        Returns:
            List of available channel widths in MHz
        """
        if band == FrequencyBand.BAND_2_4_GHZ:
            return [20, 40]
        elif band == FrequencyBand.BAND_5_GHZ:
            return [20, 40, 80, 160]
        elif band == FrequencyBand.BAND_6_GHZ:
            return [20, 40, 80, 160, 320]
        return [20]

    @classmethod
    def is_dfs_channel(cls, channel: int) -> bool:
        """
        Check if a 5 GHz channel requires DFS (Dynamic Frequency Selection).

        DFS channels are shared with radar systems and require special handling.

        Args:
            channel: Channel number

        Returns:
            True if DFS channel
        """
        dfs_channels = {52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144}
        return channel in dfs_channels

    @classmethod
    def decode_encryption_cipher(cls, security_string: str) -> Optional[str]:
        """
        Extract encryption cipher from security string.

        Args:
            security_string: Security string from scanner

        Returns:
            Cipher name (e.g., "CCMP", "TKIP")
        """
        security_upper = security_string.upper()

        ciphers = []
        if "CCMP" in security_upper or "AES" in security_upper:
            ciphers.append("CCMP")
        if "TKIP" in security_upper:
            ciphers.append("TKIP")
        if "GCMP" in security_upper:
            ciphers.append("GCMP")

        if ciphers:
            return "/".join(ciphers)
        return None
