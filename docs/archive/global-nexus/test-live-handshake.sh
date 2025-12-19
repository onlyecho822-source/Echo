#!/bin/bash
# Live Global Handshake Benchmark Test
# NO SANDBOX - REAL CONNECTIONS ONLY

echo "🌐 LIVE GLOBAL HANDSHAKE BENCHMARK"
echo "=================================="
echo "Started: $(date -u)"
echo ""

# Real cloud provider endpoints
declare -A TARGETS=(
  ["AWS-US-East"]="54.239.25.192"
  ["AWS-EU-West"]="52.16.0.2"
  ["AWS-AP-Southeast"]="46.51.191.1"
  ["Azure-US-East"]="20.42.65.92"
  ["Azure-EU-West"]="20.50.2.1"
  ["GCP-US-Central"]="35.202.0.1"
  ["GCP-EU-West"]="35.205.0.1"
  ["GitHub-CDN"]="140.82.114.4"
  ["Cloudflare-CDN"]="1.1.1.1"
  ["Google-DNS"]="8.8.8.8"
)

RESULTS_FILE="global-nexus/state/handshake-results.json"
mkdir -p global-nexus/state

echo "[" > $RESULTS_FILE

FIRST=true
for REGION in "${!TARGETS[@]}"; do
  IP="${TARGETS[$REGION]}"
  
  echo "Testing $REGION ($IP)..."
  
  # HTTP test
  START=$(date +%s%N)
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 5 http://$IP 2>/dev/null || echo "TIMEOUT")
  END=$(date +%s%N)
  HTTP_LATENCY=$(( (END-START)/1000000 ))
  
  # Ping test
  PING_RESULT=$(ping -c 3 -W 2 $IP 2>/dev/null | grep 'avg' | awk -F'/' '{print $5}' || echo "TIMEOUT")
  
  # DNS test
  DNS_RESULT=$(dig +short $IP @8.8.8.8 2>/dev/null | head -1 || echo "FAILED")
  
  SUCCESS="false"
  [ "$HTTP_CODE" != "TIMEOUT" ] && SUCCESS="true"
  
  # Write JSON result
  if [ "$FIRST" = false ]; then
    echo "," >> $RESULTS_FILE
  fi
  FIRST=false
  
  cat >> $RESULTS_FILE << EOF
  {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "region": "$REGION",
    "ip": "$IP",
    "http_code": "$HTTP_CODE",
    "http_latency_ms": $HTTP_LATENCY,
    "ping_avg_ms": "$PING_RESULT",
    "dns_result": "$DNS_RESULT",
    "success": $SUCCESS
  }
EOF
  
  echo "  ✓ HTTP: $HTTP_CODE ($HTTP_LATENCY ms)"
  echo "  ✓ Ping: $PING_RESULT ms"
  echo ""
done

echo "]" >> $RESULTS_FILE

# Generate summary
TOTAL=$(jq 'length' $RESULTS_FILE)
SUCCESSFUL=$(jq '[.[] | select(.success == true)] | length' $RESULTS_FILE)
SUCCESS_RATE=$(echo "scale=2; $SUCCESSFUL * 100 / $TOTAL" | bc)
AVG_LATENCY=$(jq '[.[] | select(.http_latency_ms > 0) | .http_latency_ms] | add / length' $RESULTS_FILE)

echo "=================================="
echo "📊 BENCHMARK RESULTS"
echo "=================================="
echo "Total Endpoints: $TOTAL"
echo "Successful: $SUCCESSFUL"
echo "Success Rate: ${SUCCESS_RATE}%"
echo "Avg Latency: ${AVG_LATENCY}ms"
echo ""
echo "Completed: $(date -u)"
echo ""
echo "Full results saved to: $RESULTS_FILE"
