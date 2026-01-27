# 💰 Financial & Market Data APIs

**APIs for stock prices, forex, cryptocurrency, economic indicators, and market data**

---

## 📊 Overview

Financial APIs provide access to real-time and historical market data, economic indicators, company fundamentals, and trading information. These APIs are essential for:

- **Market signal detection** (EchoNate Nexus)
- **Portfolio tracking and analysis**
- **Economic research and forecasting**
- **Trading algorithm development**
- **Financial education and visualization**

---

## 🌟 Featured APIs

### 1. Yahoo Finance API (via Manus API Hub)

**Status:** ✅ Available via Manus  
**Free Tier:** Yes  
**Rate Limit:** Generous  
**Authentication:** Manus token  
**Documentation:** Internal Manus API Hub

#### What It Provides
- Real-time stock quotes
- Historical price data (OHLCV)
- Company fundamentals
- Financial statements
- Analyst recommendations
- Market news and insights

#### Endpoints
- `YahooFinance/get_stock_chart` - Historical price data
- `YahooFinance/get_stock_insights` - Company analysis and metrics

#### Use Cases
- **EchoNate Nexus:** Correlate alternative data signals with market movements
- **Portfolio tracking:** Monitor stock performance
- **Market research:** Analyze company fundamentals

#### Example (Python)
```python
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

client = ApiClient()

# Get stock chart for Apple
response = client.call_api('YahooFinance/get_stock_chart', query={
    'symbol': 'AAPL',
    'region': 'US',
    'interval': '1d',
    'range': '1mo'
})

# Extract price data
result = response['chart']['result'][0]
meta = result['meta']
print(f"Current Price: ${meta['regularMarketPrice']:.2f}")
```

---

### 2. Alpha Vantage

**Website:** https://www.alphavantage.co/  
**Free Tier:** ✅ Yes (25 requests/day)  
**Rate Limit:** 25 API calls/day (free), 500/day (premium)  
**Authentication:** API Key  
**Documentation:** https://www.alphavantage.co/documentation/

#### What It Provides
- Stock time series data (intraday, daily, weekly, monthly)
- Technical indicators (SMA, EMA, RSI, MACD, etc.)
- Forex exchange rates
- Cryptocurrency prices
- Economic indicators (GDP, inflation, unemployment)
- Company fundamentals

#### Endpoints
- `TIME_SERIES_DAILY` - Daily stock prices
- `TIME_SERIES_INTRADAY` - Intraday prices (1min, 5min, 15min, 30min, 60min)
- `FX_DAILY` - Forex exchange rates
- `DIGITAL_CURRENCY_DAILY` - Cryptocurrency prices
- `OVERVIEW` - Company fundamentals

#### Use Cases
- **EchoNate Nexus:** Technical analysis and indicator calculation
- **Forex tracking:** Currency exchange rate monitoring
- **Crypto analysis:** Digital currency price tracking

#### Example (cURL)
```bash
# Get daily stock prices for IBM
curl 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=YOUR_API_KEY'

# Get real-time forex rate (USD to EUR)
curl 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey=YOUR_API_KEY'
```

---

### 3. CoinGecko API

**Website:** https://www.coingecko.com/en/api  
**Free Tier:** ✅ Yes (50 calls/minute)  
**Rate Limit:** 50 calls/min (free), 500 calls/min (paid)  
**Authentication:** None (free tier), API Key (paid)  
**Documentation:** https://www.coingecko.com/en/api/documentation

#### What It Provides
- 10,000+ cryptocurrency prices
- Market cap and volume data
- Historical price data
- Exchange data
- DeFi data
- NFT data
- Trending coins

#### Endpoints
- `/simple/price` - Current price of coins
- `/coins/{id}/market_chart` - Historical market data
- `/coins/markets` - List of coins with market data
- `/exchanges` - Exchange information
- `/trending` - Trending search coins

#### Use Cases
- **EchoNate Nexus:** Cryptocurrency market signal detection
- **Crypto portfolio:** Track cryptocurrency holdings
- **Market analysis:** Analyze crypto market trends

#### Example (Python)
```python
import requests

# Get current price of Bitcoin and Ethereum
url = 'https://api.coingecko.com/api/v3/simple/price'
params = {
    'ids': 'bitcoin,ethereum',
    'vs_currencies': 'usd',
    'include_24hr_change': 'true'
}

response = requests.get(url, params=params)
data = response.json()

print(f"Bitcoin: ${data['bitcoin']['usd']:,.2f} ({data['bitcoin']['usd_24h_change']:.2f}%)")
print(f"Ethereum: ${data['ethereum']['usd']:,.2f} ({data['ethereum']['usd_24h_change']:.2f}%)")
```

---

### 4. Federal Reserve Economic Data (FRED)

**Website:** https://fred.stlouisfed.org/  
**Free Tier:** ✅ Yes  
**Rate Limit:** 120 requests/minute  
**Authentication:** API Key (free)  
**Documentation:** https://fred.stlouisfed.org/docs/api/fred/

#### What It Provides
- 800,000+ economic time series
- US economic indicators (GDP, inflation, unemployment, etc.)
- Federal Reserve data
- International economic data
- Regional economic data

#### Endpoints
- `/series/observations` - Get data for a specific series
- `/series/search` - Search for economic series
- `/category/series` - Get series in a category
- `/releases` - Get economic releases

#### Use Cases
- **EchoNate Nexus:** Correlate economic indicators with market movements
- **Economic research:** Analyze macroeconomic trends
- **Policy analysis:** Track Federal Reserve actions

#### Example (cURL)
```bash
# Get GDP data
curl 'https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key=YOUR_API_KEY&file_type=json'

# Get unemployment rate
curl 'https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key=YOUR_API_KEY&file_type=json'
```

---

### 5. IEX Cloud

**Website:** https://iexcloud.io/  
**Free Tier:** ✅ Yes (50,000 messages/month)  
**Rate Limit:** Based on message credits  
**Authentication:** API Token  
**Documentation:** https://iexcloud.io/docs/api/

#### What It Provides
- Real-time and delayed stock quotes
- Historical prices
- Company information
- Financial statements
- News
- Market data

#### Endpoints
- `/stock/{symbol}/quote` - Real-time quote
- `/stock/{symbol}/chart/{range}` - Historical prices
- `/stock/{symbol}/company` - Company information
- `/stock/{symbol}/news` - Company news

#### Use Cases
- **EchoNate Nexus:** Real-time market data integration
- **Stock analysis:** Company fundamental research
- **News tracking:** Monitor company-specific news

#### Example (Python)
```python
import requests

API_TOKEN = 'YOUR_IEX_TOKEN'
symbol = 'AAPL'

# Get real-time quote
url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote'
params = {'token': API_TOKEN}

response = requests.get(url, params=params)
quote = response.json()

print(f"{quote['companyName']}")
print(f"Price: ${quote['latestPrice']}")
print(f"Change: {quote['change']} ({quote['changePercent']:.2f}%)")
```

---

## 🆓 Free Alternatives

### 6. Twelve Data

**Website:** https://twelvedata.com/  
**Free Tier:** ✅ Yes (800 API calls/day)  
**Features:** Stocks, forex, crypto, ETFs, indices

### 7. Finnhub

**Website:** https://finnhub.io/  
**Free Tier:** ✅ Yes (60 API calls/minute)  
**Features:** Real-time data, company fundamentals, news

### 8. Polygon.io

**Website:** https://polygon.io/  
**Free Tier:** ✅ Yes (5 API calls/minute)  
**Features:** Stocks, options, forex, crypto

### 9. Marketstack

**Website:** https://marketstack.com/  
**Free Tier:** ✅ Yes (100 requests/month)  
**Features:** 70,000+ stock tickers, 50+ exchanges

### 10. Quandl (Nasdaq Data Link)

**Website:** https://data.nasdaq.com/  
**Free Tier:** ✅ Yes (limited datasets)  
**Features:** Alternative data, economic data, financial data

---

## 📈 Comparison Table

| API | Free Tier | Rate Limit | Stocks | Forex | Crypto | Economic | Auth |
|-----|-----------|------------|--------|-------|--------|----------|------|
| Yahoo Finance (Manus) | ✅ | Generous | ✅ | ✅ | ✅ | ❌ | Manus |
| Alpha Vantage | ✅ | 25/day | ✅ | ✅ | ✅ | ✅ | API Key |
| CoinGecko | ✅ | 50/min | ❌ | ❌ | ✅ | ❌ | None |
| FRED | ✅ | 120/min | ❌ | ❌ | ❌ | ✅ | API Key |
| IEX Cloud | ✅ | 50k msg/mo | ✅ | ❌ | ❌ | ❌ | Token |
| Twelve Data | ✅ | 800/day | ✅ | ✅ | ✅ | ❌ | API Key |
| Finnhub | ✅ | 60/min | ✅ | ✅ | ✅ | ❌ | API Key |
| Polygon.io | ✅ | 5/min | ✅ | ✅ | ✅ | ❌ | API Key |

---

## 🎯 Recommendations by Use Case

### Real-Time Market Signals (EchoNate Nexus)
1. **Yahoo Finance (Manus)** - Best overall, generous limits
2. **Finnhub** - Good real-time data, 60 calls/min
3. **IEX Cloud** - Reliable, 50k messages/month

### Historical Analysis
1. **Alpha Vantage** - Excellent technical indicators
2. **Yahoo Finance (Manus)** - Comprehensive historical data
3. **Twelve Data** - Good coverage, 800 calls/day

### Cryptocurrency
1. **CoinGecko** - Best free crypto API, 50 calls/min
2. **Alpha Vantage** - Good for major coins
3. **Yahoo Finance (Manus)** - Major crypto pairs

### Economic Data
1. **FRED** - Best economic data, 120 calls/min
2. **Alpha Vantage** - Key economic indicators
3. **World Bank (Manus)** - Global economic data

---

## 💡 Integration Tips

### 1. Caching
Cache API responses to reduce calls:
```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_stock_price(symbol, timestamp):
    # timestamp rounded to 5 minutes for caching
    return fetch_from_api(symbol)

# Use with 5-minute cache
price = get_stock_price('AAPL', int(time.time() / 300))
```

### 2. Rate Limiting
Implement rate limiting to stay within quotas:
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                time.sleep(sleep_time)
            
            self.calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper

# Limit to 25 calls per day (Alpha Vantage free tier)
@RateLimiter(max_calls=25, period=86400)
def fetch_stock_data(symbol):
    return alpha_vantage_api.get(symbol)
```

### 3. Error Handling
Handle API errors gracefully:
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session()
response = session.get('https://api.example.com/data')
```

---

## 📚 Resources

### Learning
- [Investopedia API Guide](https://www.investopedia.com/terms/a/application-programming-interface.asp)
- [Financial APIs Comparison](https://rapidapi.com/blog/best-stock-api/)
- [Building Trading Algorithms](https://www.quantstart.com/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Insomnia](https://insomnia.rest/) - API client
- [RapidAPI](https://rapidapi.com/) - API marketplace

### Communities
- [r/algotrading](https://www.reddit.com/r/algotrading/) - Algorithmic trading
- [QuantConnect Community](https://www.quantconnect.com/forum) - Quant finance
- [Stack Overflow - Finance](https://stackoverflow.com/questions/tagged/finance) - Q&A

---

**Last Updated:** January 27, 2026  
**Maintained by:** Echo Universe Team
