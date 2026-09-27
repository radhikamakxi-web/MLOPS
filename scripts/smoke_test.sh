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

webhook_count_before=$(docker compose logs --no-color ml-api 2>&1 \
    | grep -c "Webhook sent:" || true)

echo "3. Predict (rooms=3)"
prediction=$(curl -sf -X POST "${API_BASE}/predict" \
    -H "Content-Type: application/json" \
    -d '{"rooms": 3}')
printf '%s\n' "${prediction}"
if ! grep -Eq '"predicted_price"[[:space:]]*:' <<<"${prediction}"; then
    echo "Prediction response is missing predicted_price." >&2
    exit 1
fi
if ! grep -Eq '"model_version"[[:space:]]*:[[:space:]]*"0\.1\.0"' <<<"${prediction}"; then
    echo "Prediction response has an unexpected model_version." >&2
    exit 1
fi

echo "4. Invalid prediction must return HTTP 422"
status_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${API_BASE}/predict" \
    -H "Content-Type: application/json" \
    -d '{"rooms": -1}')
test "${status_code}" = "422"

echo "5. Webhook receiver is reachable"
curl -sf "${WEBHOOK_BASE}/get" >/dev/null

echo "6. Verify webhook delivery in Compose logs"
webhook_sent=false
for attempt in {1..10}; do
    api_logs=$(docker compose logs --no-color --since 2m ml-api 2>&1)
    webhook_count=$(printf '%s\n' "${api_logs}" \
        | grep -c "Webhook sent:" || true)
    if (( webhook_count > webhook_count_before )); then
        webhook_sent=true
        break
    fi
    sleep 1
done

if [[ "${webhook_sent}" != "true" ]]; then
    echo "Webhook delivery was not confirmed. Recent ml-api logs:" >&2
    printf '%s\n' "${api_logs}" >&2
    exit 1
fi
echo "Webhook delivery was logged successfully."

echo "Smoke test completed."