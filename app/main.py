# app/main.py
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
