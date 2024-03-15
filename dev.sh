PORT="${PORT:-8080}"
python -m uvicorn chatpilot.server:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
