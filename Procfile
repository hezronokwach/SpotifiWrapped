web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 api_app:create_app()
release: python -c "import os; os.makedirs('data', exist_ok=True); os.makedirs('logs', exist_ok=True)"
