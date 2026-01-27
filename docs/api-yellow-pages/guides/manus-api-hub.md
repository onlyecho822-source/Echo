# 🔌 Using Manus API Hub

**How to access Yahoo Finance, DataBank, and other APIs through Manus**

---

## 📊 Overview

Manus API Hub provides pre-integrated access to premium APIs without requiring separate API keys or accounts. All APIs are accessible through a unified Python client with your Manus token.

### Benefits
- ✅ **No separate API keys** - Use your Manus token for all APIs
- ✅ **Generous rate limits** - Higher limits than free tiers
- ✅ **Pre-configured** - No setup required
- ✅ **Type-safe** - Python client with error handling
- ✅ **Unified billing** - One subscription for multiple APIs

---

## 🚀 Quick Start

### 1. Import the API Client

```python
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

client = ApiClient()
```

### 2. Call an API

```python
# Get stock data from Yahoo Finance
response = client.call_api('YahooFinance/get_stock_chart', query={
    'symbol': 'AAPL',
    'region': 'US',
    'interval': '1d',
    'range': '1mo'
})

# Extract data
result = response['chart']['result'][0]
meta = result['meta']
print(f"Current Price: ${meta['regularMarketPrice']:.2f}")
```

That's it! No API keys, no authentication setup, no rate limit management.

---

## 📚 Available APIs

### 1. Yahoo Finance

**Namespace:** `YahooFinance/`

#### Endpoints

##### `get_stock_chart`
Get historical price data and current quotes.

**Parameters:**
- `symbol` (string, required) - Stock ticker (e.g., 'AAPL', 'GOOGL')
- `region` (string, required) - Market region (e.g., 'US', 'GB', 'JP')
- `interval` (string, required) - Time interval ('1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo')
- `range` (string, required) - Time range ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
- `includeAdjustedClose` (boolean, optional) - Include adjusted close prices
- `events` (string, optional) - Include events ('div', 'split', 'div,split')

**Example:**
```python
response = client.call_api('YahooFinance/get_stock_chart', query={
    'symbol': 'TSLA',
    'region': 'US',
    'interval': '1d',
    'range': '1y',
    'includeAdjustedClose': True,
    'events': 'div,split'
})

# Access data
result = response['chart']['result'][0]
timestamps = result['timestamp']
quotes = result['indicators']['quote'][0]

for i in range(len(timestamps)):
    print(f"Date: {timestamps[i]}, Close: ${quotes['close'][i]:.2f}")
```

##### `get_stock_insights`
Get company analysis, technical indicators, and research reports.

**Parameters:**
- `symbol` (string, required) - Stock ticker

**Example:**
```python
response = client.call_api('YahooFinance/get_stock_insights', query={
    'symbol': 'AAPL'
})

# Access insights
if 'insights' in response:
    insights = response['insights']
    print(f"Company: {response.get('companyName', 'N/A')}")
    print(f"Insights: {insights}")
```

---

### 2. DataBank (World Bank)

**Namespace:** `DataBank/`

#### Endpoints

##### `indicator_list`
Get a list of all World Development Indicators.

**Parameters:**
- `q` (string, optional) - Search query to filter indicators
- `page` (integer, optional) - Page number (default: 1)
- `pageSize` (integer, optional) - Items per page (default: 10, max: 100)

**Example:**
```python
response = client.call_api('DataBank/indicator_list', query={
    'q': 'GDP',
    'page': 1,
    'pageSize': 10
})

# Access indicators
indicators = response.get('data', [])
for indicator in indicators:
    print(f"ID: {indicator['id']}")
    print(f"Name: {indicator['name']}")
    print(f"Description: {indicator.get('sourceNote', 'N/A')[:100]}...")
    print("---")
```

##### `indicator_detail`
Get detailed information about a specific indicator.

**Parameters:**
- `indicatorCode` (string, required, path parameter) - Indicator code (e.g., 'NY.GDP.MKTP.CD')

**Example:**
```python
response = client.call_api('DataBank/indicator_detail', 
                          path_params={'indicatorCode': 'NY.GDP.MKTP.CD'})

print(f"Indicator: {response.get('indicatorName')}")
print(f"Description: {response.get('longDescription')}")
print(f"Source: {response.get('sourceOrganization')}")
```

---

## 💡 Best Practices

### 1. Error Handling

Always wrap API calls in try-except blocks:

```python
def safe_api_call(api_name, **kwargs):
    try:
        response = client.call_api(api_name, **kwargs)
        return response
    except Exception as e:
        print(f"API call failed: {str(e)}")
        return None

# Use it
data = safe_api_call('YahooFinance/get_stock_chart', query={
    'symbol': 'AAPL',
    'region': 'US',
    'interval': '1d',
    'range': '1mo'
})

if data:
    # Process data
    pass
else:
    # Handle error
    pass
```

### 2. Response Validation

Check if the response contains expected data:

```python
response = client.call_api('YahooFinance/get_stock_chart', query={
    'symbol': 'AAPL',
    'region': 'US',
    'interval': '1d',
    'range': '1mo'
})

if response and 'chart' in response and 'result' in response['chart']:
    result = response['chart']['result'][0]
    # Process result
else:
    print("Unexpected response format")
```

### 3. Caching

Cache API responses to reduce calls:

```python
import json
import os
from datetime import datetime, timedelta

class ManusAPICache:
    def __init__(self, cache_dir='./cache', ttl_hours=24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, api_name, params):
        # Create unique cache key
        key = f"{api_name}_{hash(str(params))}"
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, api_name, params):
        cache_path = self._get_cache_path(api_name, params)
        
        if not os.path.exists(cache_path):
            return None
        
        # Check if cache is still valid
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - mtime > self.ttl:
            os.remove(cache_path)
            return None
        
        with open(cache_path, 'r') as f:
            return json.load(f)
    
    def set(self, api_name, params, data):
        cache_path = self._get_cache_path(api_name, params)
        with open(cache_path, 'w') as f:
            json.dump(data, f)

# Use it
cache = ManusAPICache(ttl_hours=24)

def cached_api_call(api_name, **kwargs):
    # Try cache first
    cached_data = cache.get(api_name, kwargs)
    if cached_data:
        return cached_data
    
    # Call API
    data = client.call_api(api_name, **kwargs)
    
    # Cache result
    cache.set(api_name, kwargs, data)
    
    return data

# This will use cache if available
response = cached_api_call('YahooFinance/get_stock_chart', query={
    'symbol': 'AAPL',
    'region': 'US',
    'interval': '1d',
    'range': '1mo'
})
```

### 4. Batch Processing

Process multiple symbols efficiently:

```python
import time

def batch_fetch_stocks(symbols, delay=0.5):
    """
    Fetch data for multiple stocks with rate limiting
    
    Args:
        symbols: List of stock symbols
        delay: Delay between requests in seconds
    
    Returns:
        Dictionary mapping symbols to their data
    """
    results = {}
    
    for symbol in symbols:
        try:
            response = client.call_api('YahooFinance/get_stock_chart', query={
                'symbol': symbol,
                'region': 'US',
                'interval': '1d',
                'range': '1mo'
            })
            
            if response and 'chart' in response:
                results[symbol] = response['chart']['result'][0]
            
            # Rate limiting
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error fetching {symbol}: {str(e)}")
            results[symbol] = None
    
    return results

# Fetch multiple stocks
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
data = batch_fetch_stocks(symbols)

for symbol, stock_data in data.items():
    if stock_data:
        meta = stock_data['meta']
        print(f"{symbol}: ${meta['regularMarketPrice']:.2f}")
```

---

## 🔧 Advanced Usage

### 1. Custom API Client Wrapper

Create a wrapper class for cleaner code:

```python
class ManusFinanceAPI:
    def __init__(self):
        import sys
        sys.path.append('/opt/.manus/.sandbox-runtime')
        from data_api import ApiClient
        self.client = ApiClient()
    
    def get_stock_price(self, symbol, region='US'):
        """Get current stock price"""
        response = self.client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': region,
            'interval': '1d',
            'range': '1d'
        })
        
        if response and 'chart' in response:
            result = response['chart']['result'][0]
            return result['meta']['regularMarketPrice']
        return None
    
    def get_historical_prices(self, symbol, days=30, region='US'):
        """Get historical prices"""
        response = self.client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': region,
            'interval': '1d',
            'range': f'{days}d'
        })
        
        if response and 'chart' in response:
            result = response['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            return [
                {
                    'date': timestamps[i],
                    'open': quotes['open'][i],
                    'high': quotes['high'][i],
                    'low': quotes['low'][i],
                    'close': quotes['close'][i],
                    'volume': quotes['volume'][i]
                }
                for i in range(len(timestamps))
            ]
        return []
    
    def get_indicator(self, indicator_code):
        """Get World Bank indicator details"""
        response = self.client.call_api('DataBank/indicator_detail',
                                       path_params={'indicatorCode': indicator_code})
        return response

# Use it
api = ManusFinanceAPI()

# Get current price
price = api.get_stock_price('AAPL')
print(f"AAPL: ${price:.2f}")

# Get historical prices
history = api.get_historical_prices('AAPL', days=7)
for day in history:
    print(f"Date: {day['date']}, Close: ${day['close']:.2f}")

# Get economic indicator
gdp = api.get_indicator('NY.GDP.MKTP.CD')
print(f"GDP Indicator: {gdp.get('indicatorName')}")
```

### 2. Async API Calls

For high-performance applications, use async:

```python
import asyncio
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

async def fetch_stock_async(client, symbol):
    """Async wrapper for API call"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': 'US',
            'interval': '1d',
            'range': '1d'
        })
    )
    return symbol, response

async def fetch_multiple_stocks(symbols):
    """Fetch multiple stocks concurrently"""
    client = ApiClient()
    tasks = [fetch_stock_async(client, symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    return dict(results)

# Use it
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
results = asyncio.run(fetch_multiple_stocks(symbols))

for symbol, data in results.items():
    if data and 'chart' in data:
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        print(f"{symbol}: ${price:.2f}")
```

---

## 🎯 Integration Examples

### EchoNate Nexus Integration

```python
class EchoNateMarketData:
    def __init__(self):
        import sys
        sys.path.append('/opt/.manus/.sandbox-runtime')
        from data_api import ApiClient
        self.client = ApiClient()
    
    def get_market_signal(self, symbol):
        """Generate market signal from Yahoo Finance data"""
        response = self.client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': 'US',
            'interval': '1d',
            'range': '1mo'
        })
        
        if not response or 'chart' not in response:
            return None
        
        result = response['chart']['result'][0]
        quotes = result['indicators']['quote'][0]
        closes = quotes['close']
        
        # Calculate simple moving averages
        sma_5 = sum(closes[-5:]) / 5
        sma_20 = sum(closes[-20:]) / 20
        
        # Generate signal
        if sma_5 > sma_20:
            direction = 'bullish'
        elif sma_5 < sma_20:
            direction = 'bearish'
        else:
            direction = 'neutral'
        
        return {
            'symbol': symbol,
            'current_price': closes[-1],
            'sma_5': sma_5,
            'sma_20': sma_20,
            'direction': direction,
            'confidence': abs(sma_5 - sma_20) / sma_20 * 100
        }

# Use it
market_data = EchoNateMarketData()
signal = market_data.get_market_signal('AAPL')

if signal:
    print(f"Symbol: {signal['symbol']}")
    print(f"Price: ${signal['current_price']:.2f}")
    print(f"Direction: {signal['direction']}")
    print(f"Confidence: {signal['confidence']:.2f}%")
```

---

## 📊 Rate Limits & Quotas

### Current Limits
- **Yahoo Finance:** Generous limits, suitable for most applications
- **DataBank:** Generous limits, suitable for research applications

### Best Practices
1. **Cache aggressively** - Financial data doesn't change every second
2. **Batch requests** - Fetch multiple symbols in sequence with delays
3. **Use appropriate intervals** - Don't fetch 1-minute data if you need daily
4. **Monitor usage** - Track your API calls to avoid hitting limits

### If You Hit Rate Limits
1. **Implement exponential backoff**
2. **Cache more aggressively**
3. **Reduce request frequency**
4. **Contact Manus support** for higher limits

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Error
```python
# Error: ModuleNotFoundError: No module named 'data_api'

# Solution: Add runtime path
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
```

#### 2. Empty Response
```python
# Check if API returned data
if response and 'chart' in response and 'result' in response['chart']:
    result = response['chart']['result'][0]
else:
    print("No data returned - check symbol and parameters")
```

#### 3. Invalid Symbol
```python
# Yahoo Finance requires correct symbol format
# Use uppercase: 'AAPL' not 'aapl'
# Check symbol exists on Yahoo Finance website first
```

#### 4. Region Mismatch
```python
# Use correct region for international stocks
# US stocks: region='US'
# UK stocks: region='GB'
# Japanese stocks: region='JP'
```

---

## 📚 Resources

- **Manus Documentation:** Check internal docs for updates
- **Yahoo Finance:** https://finance.yahoo.com/ (to verify symbols)
- **World Bank Data:** https://data.worldbank.org/ (to find indicator codes)

---

**Last Updated:** January 27, 2026  
**Maintained by:** Echo Universe Team
