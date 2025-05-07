wrk.method = "POST"
wrk.body = '{"fields": ["login"], "value": "ajohnson"}'
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Authorization"] = "Bearer <TOKEN>"
