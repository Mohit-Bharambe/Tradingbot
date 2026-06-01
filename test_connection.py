import os
import argparse
from dotenv import load_dotenv
import requests
from bot.logging_config import get_logger

load_dotenv()
logger = get_logger("test_connection")
BASE = "https://testnet.binancefuture.com"

def test_server_time():
    r = requests.get(BASE + "/fapi/v1/time", timeout=10)
    r.raise_for_status()
    return r.json()

def test_listen_key(api_key: str):
    headers = {"X-MBX-APIKEY": api_key}
    r = requests.post(BASE + "/fapi/v1/listenKey", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api-key", help="Testnet API key")
    args = p.parse_args()
    api_key = args.api_key or os.getenv("BINANCE_API_KEY")
    if not api_key:
        logger.error("Missing API key")
        raise SystemExit(1)
    try:
        logger.info("Testing server time...")
        print(test_server_time())
        logger.info("Testing listenKey (validates API key permissions)...")
        print(test_listen_key(api_key))
        logger.info("Connection tests succeeded")
    except Exception as e:
        logger.exception("Connection test failed: %s", e)
        raise SystemExit(1)

if __name__ == "__main__":
    main()