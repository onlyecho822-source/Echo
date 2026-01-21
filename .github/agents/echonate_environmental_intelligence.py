#!/usr/bin/env python3
"""
ECHONATE ENVIRONMENTAL INTELLIGENCE LAYER
=========================================
Collects climate, air quality, water quality, and sentiment data
for cross-domain correlation with market signals.

Primary Sources (No API Key Required):
- NASA POWER API: Solar irradiance, temperature
- Reddit Public API: Market sentiment from WSB
- Open-Meteo: Weather data
- ISS Position: Space tracking

∇θ Phoenix Global Nexus
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import hashlib
import sys

class EnvironmentalIntelligence:
    """Environmental data collector for market correlation."""
    
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.results = {
            "timestamp": self.timestamp,
            "agent": "ZETA-Environmental",
            "domain": "Environmental Intelligence",
            "sources": {},
            "signals": [],
            "correlations": []
        }
    
    def _fetch_json(self, url, headers=None):
        """Fetch JSON from URL with error handling."""
        try:
            req = urllib.request.Request(url)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            return {"error": str(e)}
    
    def collect_nasa_power(self):
        """Collect solar irradiance and temperature from NASA POWER."""
        print("[ZETA] Collecting NASA POWER climate data...")
        
        # Get last 7 days of data for Houston (energy hub)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        url = (
            f"https://power.larc.nasa.gov/api/temporal/daily/point?"
            f"parameters=ALLSKY_SFC_SW_DWN,T2M,PRECTOTCORR&community=RE&"
            f"longitude=-95.37&latitude=29.76&"
            f"start={start_date.strftime('%Y%m%d')}&"
            f"end={end_date.strftime('%Y%m%d')}&format=JSON"
        )
        
        data = self._fetch_json(url)
        
        if "error" not in data:
            params = data.get("properties", {}).get("parameter", {})
            solar = params.get("ALLSKY_SFC_SW_DWN", {})
            temp = params.get("T2M", {})
            precip = params.get("PRECTOTCORR", {})
            
            # Filter out missing values (-999)
            valid_solar = [v for v in solar.values() if v > 0]
            valid_temp = [v for v in temp.values() if v > -900]
            
            self.results["sources"]["nasa_power"] = {
                "status": "success",
                "location": "Houston, TX (Energy Hub)",
                "solar_irradiance_avg": round(sum(valid_solar)/len(valid_solar), 2) if valid_solar else None,
                "temperature_avg_c": round(sum(valid_temp)/len(valid_temp), 2) if valid_temp else None,
                "solar_data": solar,
                "temp_data": temp
            }
            
            # Generate signal if solar is significantly above/below average
            if valid_solar:
                avg_solar = sum(valid_solar) / len(valid_solar)
                if avg_solar > 5.0:  # High solar irradiance
                    self.results["signals"].append({
                        "type": "SOLAR_HIGH",
                        "target": "FSLR,ENPH,SPWR",
                        "direction": "LONG",
                        "strength": min(0.5, (avg_solar - 5.0) / 2),
                        "rationale": f"Solar irradiance {avg_solar:.2f} kW-hr/m²/day above threshold"
                    })
                elif avg_solar < 3.0:  # Low solar
                    self.results["signals"].append({
                        "type": "SOLAR_LOW",
                        "target": "UNG,KOLD",
                        "direction": "LONG",
                        "strength": min(0.4, (3.0 - avg_solar) / 2),
                        "rationale": f"Low solar {avg_solar:.2f} → increased natural gas demand"
                    })
            
            print(f"   Solar Avg: {self.results['sources']['nasa_power']['solar_irradiance_avg']} kW-hr/m²/day")
            print(f"   Temp Avg: {self.results['sources']['nasa_power']['temperature_avg_c']}°C")
        else:
            self.results["sources"]["nasa_power"] = {"status": "error", "error": data["error"]}
            print(f"   ❌ Error: {data['error']}")
    
    def collect_reddit_sentiment(self):
        """Collect market sentiment from r/wallstreetbets."""
        print("[ZETA] Collecting Reddit WSB sentiment...")
        
        url = "https://www.reddit.com/r/wallstreetbets/top.json?limit=25&t=day"
        headers = {"User-Agent": "EchoNate/1.0 Environmental Intelligence"}
        
        data = self._fetch_json(url, headers)
        
        if "error" not in data and "data" in data:
            posts = data.get("data", {}).get("children", [])
            
            # Analyze sentiment
            bullish_keywords = ["moon", "calls", "long", "buy", "bull", "rocket", "yolo", "gain"]
            bearish_keywords = ["puts", "short", "sell", "bear", "crash", "loss", "dump"]
            
            total_score = 0
            bullish_score = 0
            bearish_score = 0
            tickers_mentioned = {}
            
            for post in posts:
                p = post.get("data", {})
                title = p.get("title", "").lower()
                score = p.get("score", 0)
                total_score += score
                
                # Count sentiment
                for kw in bullish_keywords:
                    if kw in title:
                        bullish_score += score
                        break
                for kw in bearish_keywords:
                    if kw in title:
                        bearish_score += score
                        break
                
                # Extract tickers ($ followed by letters)
                import re
                tickers = re.findall(r'\$([A-Z]{1,5})\b', p.get("title", ""))
                for t in tickers:
                    tickers_mentioned[t] = tickers_mentioned.get(t, 0) + score
            
            # Calculate sentiment ratio
            sentiment_ratio = bullish_score / max(bearish_score, 1)
            
            self.results["sources"]["reddit_wsb"] = {
                "status": "success",
                "posts_analyzed": len(posts),
                "total_engagement": total_score,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "sentiment_ratio": round(sentiment_ratio, 2),
                "top_tickers": dict(sorted(tickers_mentioned.items(), key=lambda x: -x[1])[:5]),
                "top_posts": [
                    {"title": p["data"]["title"][:80], "score": p["data"]["score"]}
                    for p in posts[:5]
                ]
            }
            
            # Generate sentiment signal
            if sentiment_ratio > 2.0:
                self.results["signals"].append({
                    "type": "WSB_BULLISH",
                    "target": "MEME_BASKET",
                    "direction": "CAUTION",
                    "strength": min(0.6, (sentiment_ratio - 1) / 5),
                    "rationale": f"WSB sentiment ratio {sentiment_ratio:.1f} - extreme bullishness often precedes correction"
                })
            elif sentiment_ratio < 0.5:
                self.results["signals"].append({
                    "type": "WSB_BEARISH",
                    "target": "MEME_BASKET",
                    "direction": "WATCH",
                    "strength": min(0.4, (1 - sentiment_ratio) / 2),
                    "rationale": f"WSB sentiment ratio {sentiment_ratio:.1f} - extreme fear may signal bottom"
                })
            
            print(f"   Posts: {len(posts)}, Sentiment Ratio: {sentiment_ratio:.2f}")
            print(f"   Top Tickers: {list(tickers_mentioned.keys())[:5]}")
        else:
            self.results["sources"]["reddit_wsb"] = {"status": "error", "error": str(data.get("error", "Unknown"))}
            print(f"   ❌ Error fetching Reddit data")
    
    def collect_forex(self):
        """Collect forex rates for currency correlation."""
        print("[ZETA] Collecting Forex rates...")
        
        url = "https://open.er-api.com/v6/latest/USD"
        data = self._fetch_json(url)
        
        if "error" not in data and "rates" in data:
            rates = data["rates"]
            key_pairs = {
                "EUR": rates.get("EUR"),
                "GBP": rates.get("GBP"),
                "JPY": rates.get("JPY"),
                "CNY": rates.get("CNY"),
                "CHF": rates.get("CHF"),
                "AUD": rates.get("AUD"),
                "CAD": rates.get("CAD")
            }
            
            self.results["sources"]["forex"] = {
                "status": "success",
                "base": "USD",
                "rates": key_pairs,
                "timestamp": data.get("time_last_update_utc")
            }
            
            # DXY proxy calculation (simplified)
            dxy_proxy = (
                (1/rates["EUR"]) * 0.576 +
                rates["JPY"] * 0.136 +
                (1/rates["GBP"]) * 0.119 +
                rates["CAD"] * 0.091 +
                (1/rates["CHF"]) * 0.036 +
                (1/rates["AUD"]) * 0.042
            )
            
            self.results["sources"]["forex"]["dxy_proxy"] = round(dxy_proxy, 4)
            print(f"   EUR: {rates['EUR']:.4f}, JPY: {rates['JPY']:.2f}, GBP: {rates['GBP']:.4f}")
        else:
            self.results["sources"]["forex"] = {"status": "error"}
            print("   ❌ Error fetching forex")
    
    def collect_iss_position(self):
        """Track ISS position (demonstrates real-time space data capability)."""
        print("[ZETA] Tracking ISS position...")
        
        url = "http://api.open-notify.org/iss-now.json"
        data = self._fetch_json(url)
        
        if "error" not in data and "iss_position" in data:
            pos = data["iss_position"]
            self.results["sources"]["iss"] = {
                "status": "success",
                "latitude": float(pos["latitude"]),
                "longitude": float(pos["longitude"]),
                "timestamp": data.get("timestamp")
            }
            print(f"   ISS Position: {pos['latitude']}, {pos['longitude']}")
        else:
            self.results["sources"]["iss"] = {"status": "error"}
    
    def generate_correlations(self):
        """Generate cross-domain correlations."""
        print("[ZETA] Generating cross-domain correlations...")
        
        # Solar → Energy correlation
        if self.results["sources"].get("nasa_power", {}).get("status") == "success":
            solar_avg = self.results["sources"]["nasa_power"].get("solar_irradiance_avg", 0)
            if solar_avg:
                self.results["correlations"].append({
                    "source": "NASA_POWER",
                    "target_sector": "SOLAR_ENERGY",
                    "correlation_type": "POSITIVE",
                    "strength": min(0.8, solar_avg / 6),
                    "tickers": ["FSLR", "ENPH", "SPWR", "TAN"]
                })
        
        # Sentiment → Volatility correlation
        if self.results["sources"].get("reddit_wsb", {}).get("status") == "success":
            sentiment = self.results["sources"]["reddit_wsb"].get("sentiment_ratio", 1)
            if sentiment > 1.5 or sentiment < 0.7:
                self.results["correlations"].append({
                    "source": "REDDIT_WSB",
                    "target_sector": "VOLATILITY",
                    "correlation_type": "POSITIVE" if abs(sentiment - 1) > 0.5 else "NEUTRAL",
                    "strength": min(0.6, abs(sentiment - 1) / 2),
                    "tickers": ["VIX", "UVXY", "SVXY"]
                })
        
        print(f"   Generated {len(self.results['correlations'])} correlations")
    
    def create_provenance_hash(self):
        """Create SHA-256 hash of all collected data for audit trail."""
        data_string = json.dumps(self.results["sources"], sort_keys=True)
        self.results["provenance"] = {
            "hash": hashlib.sha256(data_string.encode()).hexdigest(),
            "algorithm": "SHA-256",
            "timestamp": self.timestamp
        }
    
    def run(self):
        """Execute full environmental intelligence collection."""
        print("=" * 60)
        print("ZETA AGENT - ENVIRONMENTAL INTELLIGENCE")
        print(f"Time: {self.timestamp}")
        print("=" * 60)
        print()
        
        self.collect_nasa_power()
        self.collect_reddit_sentiment()
        self.collect_forex()
        self.collect_iss_position()
        self.generate_correlations()
        self.create_provenance_hash()
        
        print()
        print("=" * 60)
        print(f"[ZETA] Collection complete")
        print(f"   Sources: {len(self.results['sources'])}")
        print(f"   Signals: {len(self.results['signals'])}")
        print(f"   Correlations: {len(self.results['correlations'])}")
        print(f"   Provenance: {self.results['provenance']['hash'][:16]}...")
        print("=" * 60)
        
        return self.results


if __name__ == "__main__":
    agent = EnvironmentalIntelligence()
    results = agent.run()
    
    # Output JSON for GitHub Actions
    print()
    print("=== JSON OUTPUT ===")
    print(json.dumps(results, indent=2))
