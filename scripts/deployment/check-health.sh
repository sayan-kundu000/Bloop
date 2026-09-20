#!/usr/bin/env bash
# Bloop Cloud Health Verification Script (Linux / macOS)
TARGET_URL=${1:-"http://localhost:8000"}
HEALTH_ENDPOINT="$TARGET_URL/api/v1/health"

echo "Pinging health endpoint: $HEALTH_ENDPOINT..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT")
HTTP_BODY=$(echo "$RESPONSE" | sed '$d')
HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "Service is HEALTHY (HTTP 200)!"
    echo "$HTTP_BODY"
    exit 0
else
    echo "Health check failed with HTTP status $HTTP_STATUS"
    exit 1
fi
