PORT="${PORT:-8080}"
python3.9 -m uvicorn chatpilot.server:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload