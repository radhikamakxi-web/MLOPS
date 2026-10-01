#!/usr/bin/env bash
# End-to-end smoke test for the Docker Compose stack.
#
# This script exercises the running API and verifies that webhooks are
# delivered. Run it from the project root after `docker compose up --build`.
# It is a Bash script, so use WSL, Git Bash, or a Linux/macOS terminal.

# Bash strict mode:
# -e: exit immediately if a command fails.
# -u: treat unset variables as an error.
# -o pipefail: propagate errors through pipelines.
set -euo pipefail

# Allow overriding the default URLs via environment variables. This makes it
# easy to point the smoke test at a different host or port.
API_BASE="${API_BASE:-http://localhost:8000}"
WEBHOOK_BASE="${WEBHOOK_BASE:-http://localhost:8080}"

echo "1. Health check"
# -s: silent progress meter. -f: fail on HTTP 4xx/5xx.
curl -sf "${API_BASE}/health"
echo

echo "2. Model info"
curl -sf "${API_BASE}/model/info"
echo

# Count how many "Webhook sent:" log lines exist before the prediction.
# `|| true` prevents the script from exiting if grep finds zero matches.
webhook_count_before=$(docker compose logs --no-color ml-api 2>&1 \
    | grep -c "Webhook sent:" || true)

echo "3. Predict (rooms=3)"
prediction=$(curl -sf -X POST "${API_BASE}/predict" \
    -H "Content-Type: application/json" \
    -d '{"rooms": 3}')
printf '%s\n' "${prediction}"

# Validate that the response contains the expected fields.
if ! grep -Eq '"predicted_price"[[:space:]]*:' <<<"${prediction}"; then
    echo "Prediction response is missing predicted_price." >&2
    exit 1
fi
if ! grep -Eq '"model_version"[[:space:]]*:[[:space:]]*"0\.1\.0"' <<<"${prediction}"; then
    echo "Prediction response has an unexpected model_version." >&2
    exit 1
fi

echo "4. Invalid prediction must return HTTP 422"
# -o /dev/null discards the body; -w "%{http_code}" prints only the status.
status_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${API_BASE}/predict" \
    -H "Content-Type: application/json" \
    -d '{"rooms": -1}')
# `test` is the same as `[ ... ]`; it exits non-zero if the condition fails.
test "${status_code}" = "422"

echo "5. Webhook receiver is reachable"
curl -sf "${WEBHOOK_BASE}/get" >/dev/null

echo "6. Verify webhook delivery in Compose logs"
webhook_sent=false
# Retry up to 10 times because background tasks are asynchronous.
for attempt in {1..10}; do
    # --since 2m limits the log volume we inspect.
    api_logs=$(docker compose logs --no-color --since 2m ml-api 2>&1)
    webhook_count=$(printf '%s\n' "${api_logs}" \
        | grep -c "Webhook sent:" || true)
    # If the new count is higher than before, the webhook was logged.
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