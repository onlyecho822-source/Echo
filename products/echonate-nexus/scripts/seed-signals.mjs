#!/usr/bin/env node
/**
 * Signal Seeding Script
 * Pulls live data from all APIs and creates signals in the database
 */

import mysql from 'mysql2/promise';

const DATABASE_URL = process.env.DATABASE_URL;

async function fetchUSGSEarthquakes() {
  console.log('[USGS] Fetching earthquake data...');
  const res = await fetch('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson');
  const data = await res.json();
  
  const significant = data.features.filter(f => f.properties.mag >= 5.0);
  
  if (significant.length > 0) {
    const strongest = significant.reduce((a, b) => 
      a.properties.mag > b.properties.mag ? a : b
    );
    
    return {
      signalType: 'seismic',
      source: 'USGS',
      sourceUrl: 'https://earthquake.usgs.gov',
      targetTicker: 'TRV',
      targetSector: 'Insurance',
      direction: 'bearish',
      strength: Math.min(strongest.properties.mag / 10, 1).toFixed(2),
      confidence: '0.75',
      title: `M${strongest.properties.mag.toFixed(1)} Earthquake - Insurance Impact`,
      summary: `Significant seismic activity detected at ${strongest.properties.place}`,
      rationale: `M${strongest.properties.mag.toFixed(1)} earthquake detected at ${strongest.properties.place}. Historical correlation shows insurance stocks decline 0.12% average following M5.0+ events due to claims uncertainty.`,
      rawData: JSON.stringify({
        magnitude: strongest.properties.mag,
        location: strongest.properties.place,
        depth: strongest.geometry.coordinates[2],
        time: new Date(strongest.properties.time).toISOString()
      })
    };
  }
  return null;
}

async function fetchHealthData() {
  console.log('[HEALTH] Fetching COVID data...');
  const res = await fetch('https://disease.sh/v3/covid-19/all');
  const data = await res.json();
  
  return {
    signalType: 'health',
    source: 'disease.sh',
    sourceUrl: 'https://disease.sh',
    targetTicker: 'PFE',
    targetSector: 'Pharmaceuticals',
    direction: 'bullish',
    strength: Math.min(data.critical / 100000, 1).toFixed(2),
    confidence: '0.65',
    title: `COVID Critical Cases: ${data.critical.toLocaleString()}`,
    summary: `Global health data indicates elevated pharmaceutical demand`,
    rationale: `${data.critical.toLocaleString()} critical COVID cases globally. Elevated critical care demand historically correlates with pharmaceutical sector strength.`,
    rawData: JSON.stringify({
      critical: data.critical,
      active: data.active,
      todayCases: data.todayCases,
      todayDeaths: data.todayDeaths
    })
  };
}

async function fetchCryptoData() {
  console.log('[CRYPTO] Fetching market data...');
  const res = await fetch('https://api.coingecko.com/api/v3/global');
  const data = await res.json();
  
  const marketCapChange = data.data.market_cap_change_percentage_24h_usd;
  
  return {
    signalType: 'crypto',
    source: 'CoinGecko',
    sourceUrl: 'https://coingecko.com',
    targetTicker: 'COIN',
    targetSector: 'Crypto/Fintech',
    direction: marketCapChange > 0 ? 'bullish' : 'bearish',
    strength: Math.min(Math.abs(marketCapChange) / 10, 1).toFixed(2),
    confidence: '0.60',
    title: `Crypto Market ${marketCapChange > 0 ? 'Up' : 'Down'} ${Math.abs(marketCapChange).toFixed(2)}%`,
    summary: `24-hour crypto market movement indicates ${marketCapChange > 0 ? 'risk-on' : 'risk-off'} sentiment`,
    rationale: `Crypto market ${marketCapChange > 0 ? 'up' : 'down'} ${Math.abs(marketCapChange).toFixed(2)}% in 24h. ${marketCapChange > 0 ? 'Risk-on sentiment' : 'Risk-off sentiment'} typically correlates with ${marketCapChange > 0 ? 'bullish' : 'bearish'} crypto-adjacent equities.`,
    rawData: JSON.stringify({
      totalMarketCap: data.data.total_market_cap.usd,
      marketCapChange24h: marketCapChange,
      btcDominance: data.data.market_cap_percentage.btc
    })
  };
}

async function fetchForexData() {
  console.log('[FOREX] Fetching exchange rates...');
  const res = await fetch('https://open.er-api.com/v6/latest/USD');
  const data = await res.json();
  
  const jpyRate = data.rates.JPY;
  
  return {
    signalType: 'forex',
    source: 'ExchangeRate-API',
    sourceUrl: 'https://open.er-api.com',
    targetTicker: 'FXY',
    targetSector: 'Currency ETF',
    direction: jpyRate > 150 ? 'bullish' : 'neutral',
    strength: '0.45',
    confidence: '0.55',
    title: `USD/JPY at ${jpyRate.toFixed(2)}`,
    summary: `Yen ${jpyRate > 150 ? 'weakness' : 'strength'} creates currency positioning opportunity`,
    rationale: `USD/JPY at ${jpyRate.toFixed(2)}. ${jpyRate > 150 ? 'Yen weakness may trigger BOJ intervention opportunity' : 'Strong yen indicates risk-off sentiment'}. Currency ETF positioning.`,
    rawData: JSON.stringify({
      usdJpy: jpyRate,
      eurUsd: 1 / data.rates.EUR,
      gbpUsd: 1 / data.rates.GBP
    })
  };
}

async function fetchSentimentData() {
  console.log('[SENTIMENT] Fetching Reddit WSB data...');
  try {
    const res = await fetch('https://www.reddit.com/r/wallstreetbets/top.json?limit=25&t=day', {
      headers: { 'User-Agent': 'EchoSignal/1.0' }
    });
    const data = await res.json();
    
    let bullish = 0, bearish = 0;
    const tickers = [];
    
    data.data.children.forEach(post => {
      const title = post.data.title.toLowerCase();
      if (title.includes('bull') || title.includes('calls') || title.includes('moon')) bullish++;
      if (title.includes('bear') || title.includes('puts') || title.includes('crash')) bearish++;
      
      const tickerMatch = post.data.title.match(/\$([A-Z]{1,5})/g);
      if (tickerMatch) tickers.push(...tickerMatch);
    });
    
    const ratio = (bullish + 1) / (bearish + 1);
    
    return {
      signalType: 'sentiment',
      source: 'Reddit/WSB',
      sourceUrl: 'https://reddit.com/r/wallstreetbets',
      targetTicker: ratio > 2 ? 'UVXY' : 'SPY',
      targetSector: ratio > 2 ? 'Volatility' : 'Index',
      direction: ratio > 2 ? 'bullish' : 'neutral',
      strength: Math.min(Math.abs(ratio - 1) / 5, 1).toFixed(2),
      confidence: '0.50',
      title: `WSB Sentiment Ratio: ${ratio.toFixed(2)}`,
      summary: `Social sentiment analysis: ${bullish} bullish vs ${bearish} bearish posts`,
      rationale: `WSB sentiment ratio ${ratio.toFixed(2)} (${bullish} bullish / ${bearish} bearish). ${ratio > 2 ? 'Elevated bullishness - consider volatility hedge' : 'Balanced sentiment - no strong signal'}.`,
      rawData: JSON.stringify({
        bullishCount: bullish,
        bearishCount: bearish,
        ratio: ratio,
        topTickers: [...new Set(tickers)].slice(0, 5)
      })
    };
  } catch (e) {
    console.log('[SENTIMENT] Reddit fetch failed:', e.message);
    return null;
  }
}

async function fetchWeatherData() {
  console.log('[WEATHER] Fetching weather data...');
  const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=29.76&longitude=-95.36&current=temperature_2m,wind_speed_10m&timezone=America/Chicago');
  const data = await res.json();
  
  const windSpeed = data.current.wind_speed_10m;
  const temp = data.current.temperature_2m;
  
  return {
    signalType: 'solar', // using solar as closest to weather/environmental
    source: 'Open-Meteo',
    sourceUrl: 'https://open-meteo.com',
    targetTicker: 'XLE',
    targetSector: 'Energy',
    direction: windSpeed > 30 || temp > 35 ? 'bullish' : 'neutral',
    strength: '0.40',
    confidence: '0.55',
    title: `Houston Weather: ${temp}°C, ${windSpeed} km/h`,
    summary: `Energy corridor weather conditions ${windSpeed > 30 ? 'elevated' : 'normal'}`,
    rationale: `Houston energy corridor: ${temp}°C, ${windSpeed} km/h winds. ${windSpeed > 30 ? 'Elevated wind speeds may impact operations' : 'Normal conditions'}.`,
    rawData: JSON.stringify({
      temperature: temp,
      windSpeed: windSpeed,
      location: 'Houston, TX'
    })
  };
}

async function main() {
  console.log('=== ECHO SIGNAL SEEDER ===');
  console.log('Connecting to database...');
  
  const connection = await mysql.createConnection(DATABASE_URL);
  
  const signalGenerators = [
    fetchUSGSEarthquakes,
    fetchHealthData,
    fetchCryptoData,
    fetchForexData,
    fetchSentimentData,
    fetchWeatherData
  ];
  
  const newSignals = [];
  
  for (const generator of signalGenerators) {
    try {
      const signal = await generator();
      if (signal) {
        newSignals.push(signal);
      }
    } catch (e) {
      console.error(`Error in ${generator.name}:`, e.message);
    }
  }
  
  if (newSignals.length > 0) {
    console.log(`\nInserting ${newSignals.length} signals...`);
    
    for (const signal of newSignals) {
      const now = new Date();
      const expires = new Date(Date.now() + 24 * 60 * 60 * 1000);
      
      await connection.execute(
        `INSERT INTO signals (signalType, source, sourceUrl, targetTicker, targetSector, direction, strength, confidence, title, summary, rationale, rawData, createdAt, expiresAt) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          signal.signalType,
          signal.source,
          signal.sourceUrl,
          signal.targetTicker,
          signal.targetSector,
          signal.direction,
          signal.strength,
          signal.confidence,
          signal.title,
          signal.summary,
          signal.rationale,
          signal.rawData,
          now,
          expires
        ]
      );
      console.log(`  ✓ ${signal.signalType.toUpperCase()} → ${signal.targetTicker} (${signal.direction}, ${(parseFloat(signal.confidence) * 100).toFixed(0)}%)`);
    }
  } else {
    console.log('\nNo signals generated.');
  }
  
  await connection.end();
  console.log('\n=== SEEDING COMPLETE ===');
}

main().catch(console.error);
