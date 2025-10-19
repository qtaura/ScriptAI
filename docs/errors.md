# API Errors and Security Events

ScriptAI surfaces clear, structured errors across the API and records security events when request signing is enabled. This page documents common error types, expected HTTP statuses, and where they originate in the codebase.

## Conventions
- Responses use JSON `{ "error": "message" }`.
- `X-Request-ID` is echoed in responses and propagated in logs.
- Errors are recorded via `MonitoringManager.log_error(error_type, error_message, context, request_id)`.

## Error Types

### rate_limit_exceeded
- Status: `429 Too Many Requests`
- Source: per-IP rate limiting handled by `_handle_rate_limit` in `app.py`.
- Response: `{ "error": "Rate limit exceeded. Try again later." }`
- Logging: includes `client_ip` and limiter context.

### adapter_error
- Status: typically `502 Bad Gateway`
- Source: provider-specific failures during generation or fallback (e.g., API down, quota exceeded).
- Response: `{ "error": "Upstream provider error" }` (message may vary by adapter)
- Logging: includes `model`, provider error details, and fallback context when enabled.

### unexpected_error
- Status: `500 Internal Server Error`
- Source: unhandled exceptions in `/generate` or `/generate-stream` routes.
- Response: `{ "error": "An unexpected error occurred" }`
- Logging: includes exception details and request identifiers.

### upstream_error
- Status: `502 Bad Gateway`
- Source: upstream provider returned an error or an invalid response during streaming or generation.
- Response: `{ "error": "Upstream error" }`
- Logging: includes adapter/provider context.

### boom (test-only)
- Status: `500`
- Source: `ExplodingAdapter` in tests to simulate unhandled adapter exceptions (`tests/test_app.py`).
- Response: `{ "error": "An unexpected error occurred" }`
- Note: not expected in production.

## Security Events (Request Signing)
When `REQUEST_SIGNATURE_SECRET` (or `SIGNING_SECRET`) is configured, incoming write requests can be validated using HMAC-SHA256.

Generated with base string `v1:{timestamp}:{body}` and compared against header:
- `X-Signature: v1=<hex>`
- `X-Signature-Timestamp: <epoch_seconds>`

Security events are recorded via `SecurityManager.log_security_event(event_type, details, client_ip)`.

### Event Types
- `signature_missing_secret` — server not configured with a signing secret.
- `signature_missing` — missing `X-Signature` header.
- `signature_missing_timestamp` — missing `X-Signature-Timestamp` header.
- `signature_bad_format` — signature header not in `v1=<hex>` format.
- `signature_bad_timestamp` — timestamp invalid/unparseable.
- `signature_timestamp_out_of_window` — timestamp too old/new compared to allowed window.
- `signature_internal_error` — internal error during verification.
- `signature_mismatch` — HMAC does not match the request payload.

### Status Codes
- Missing/invalid headers, bad timestamp, or mismatch: `401 Unauthorized`
- Bad format: `400 Bad Request`
- Internal verification error: `500 Internal Server Error`

## Logging Fields
- `error_type` — canonical label (e.g., `rate_limit_exceeded`, `adapter_error`).
- `error_message` — short description or provider message.
- `context` — details such as `model`, `client_ip`, fallback attempts, provider response.
- `request_id` — unique ID propagated across request lifecycle.

## Examples

Rate limit exceeded:
```json
{ "error": "Rate limit exceeded. Try again later." }
```

Unexpected error:
```json
{ "error": "An unexpected error occurred" }
```

Upstream provider error:
```json
{ "error": "Upstream error" }
```

## See Also
- `monitoring.py` — `MonitoringManager.log_error`
- `security.py` — request signing and `log_security_event`
- `app.py` — `/generate` and `/generate-stream` error handling paths