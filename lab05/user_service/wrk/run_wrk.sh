#!/bin/bash

TOKEN="${1:-$TOKEN}"
if [ -z "$TOKEN" ]; then
  echo "Укажите JWT-токен: ./run_wrk.sh <token>"
  exit 1
fi

URL_NO_CACHE="http://localhost:8000/users/search"
URL_CACHE="http://localhost:8000/users-redis/cached-search"
BODY='{"fields": ["login"], "value": "ajohnson"}'
FIELDS_LABEL="login:ajohnson"
THREADS_LIST=(1 5 10)
CONNECTIONS=10
DURATION=10s

LUA_SCRIPT="wrk_payload.lua"
cat > $LUA_SCRIPT <<EOF
wrk.method = "POST"
wrk.body = '$BODY'
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Authorization"] = "Bearer $TOKEN"
EOF

run_test() {
  ENDPOINT=$1
  LABEL=$2
  for T in "${THREADS_LIST[@]}"; do
    echo "Тест [$LABEL] с $T потоками:"
    wrk -t$T -c$CONNECTIONS -d$DURATION -s $LUA_SCRIPT $ENDPOINT
    echo
  done
}

echo "Тест без кэша:"
run_test $URL_NO_CACHE "NO_CACHE"

echo "Тест с кэшем:"
run_test $URL_CACHE "CACHE"
