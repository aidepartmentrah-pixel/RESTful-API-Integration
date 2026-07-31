import os
import sys
import urllib.request

port = os.environ.get("API_PORT", "8000")
url = f"http://localhost:{port}/api/directory/v1/health"

try:
    with urllib.request.urlopen(url, timeout=3) as response:
        sys.exit(0 if response.status == 200 else 1)
except Exception:
    sys.exit(1)
