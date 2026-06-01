import time
import hmac
import hashlib
import urllib.parse
from typing import Dict

def timestamp_ms() -> int:
    return int(time.time() * 1000)

def sign(params: Dict[str, any], secret: str) -> str:
    query = urllib.parse.urlencode(params, doseq=True)
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()