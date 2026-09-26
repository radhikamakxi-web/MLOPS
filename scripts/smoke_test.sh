#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
WEBHOOK_BASE="${WEBHOOK_BASE:-http://localhost:8080}"

echo "1. Health check"
curl -sf "${API_BASE}/health"
echo

echo "2. Model info"
curl -sf "${API_BASE}/model/info"
echo

echo "3. Predict (rooms=3)"
curl -sf -X POST "${API_BASE}/predict" \
    -H "Content-Type: application/json" \
    -d '{"rooms": 3}'
echo

echo "4. Invalid prediction must return HTTP 422"
status_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${API_BASE}/predict" \
    -H "Content-Type: application/json" \
    -d '{"rooms": -1}')
test "${status_code}" = "422"

echo "5. Webhook receiver is reachable"
curl -sf "${WEBHOOK_BASE}/get" >/dev/null
echo "Receiver responded successfully. See API logs for webhook delivery status."

echo "Smoke test completed."