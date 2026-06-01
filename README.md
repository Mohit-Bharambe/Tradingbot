# Binance Futures Testnet Trading Bot

Project Overview
- Lightweight, modular Python trading bot scaffold targeting Binance Futures Testnet (USDT-M).
- Provides a CLI to place MARKET and LIMIT orders with structured logging, input validation, and robust error handling.
- Intended as an interview assignment / starter kit for backend engineers.

Features
- Place MARKET and LIMIT orders (BUY / SELL).
- Argparse-based CLI.
- Input validation with clear error messages.
- Structured logging to `logs/trading.log` and console.
- Clean separation: client (API), orders (business logic), validators, CLI.
- Safe: reads API credentials from environment or `.env` (do not commit secrets).

Installation

1. Clone repository
   git clone <repo-url>
   cd binance-futures-bot

2. Create and activate virtual environment (Windows)
   PowerShell:
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
   CMD:
     python -m venv .venv
     .\.venv\Scripts\activate

3. Install dependencies
   python -m pip install --upgrade pip
   pip install -r requirements.txt

Environment Setup

- Copy `.env.example` to `.env` (do NOT commit `.env`).
- Populate:
  BINANCE_API_KEY=your_testnet_api_key
  BINANCE_API_SECRET=your_testnet_api_secret

API Key Setup (Binance Futures Testnet)
1. Visit: https://testnet.binancefuture.com and create an account.
2. Navigate to API Management (Testnet) and create an API key.
3. Enable "Enable Futures" / trading permissions for the test key.
4. Copy API key & secret into `.env` or set environment variables:
   PowerShell:
     $env:BINANCE_API_KEY="..."
     $env:BINANCE_API_SECRET="..."
   (Session-only; prefer `.env` for local dev)

Folder Structure
- bot/
  - client.py         # Binance client wrapper (testnet endpoint, requests/python-binance support)
  - orders.py         # Order placement and response formatting
  - validators.py     # Input validation (symbol, side, type, qty, price)
  - logging_config.py # Structured logging helpers
  - exceptions.py     # Custom exceptions
  - utils.py          # Helpers (signing, timestamp)
- cli.py              # CLI entrypoint (argparse)
- test_connection.py  # Simple connectivity/credentials test
- requirements.txt
- .env.example
- logs/trading.log    # Generated at runtime (ignored by git)

How To Run

1. Test connectivity (reads API key from env/.env or pass `--api-key`):
   python test_connection.py --api-key YOUR_TESTNET_KEY

2. MARKET order example:
   python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

3. LIMIT order example:
   python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 40000

What the CLI prints
- Order Summary (echoed inputs)
- Order Response (orderId, status, executedQty, avgPrice)
- Success / Failure message
- Full raw responses and errors are logged to `logs/trading.log`

Logging
- Logs are written to `logs/trading.log` (RotatingFileHandler).
- Logged events: API requests/responses (headers redacted), validation failures, exceptions, order results.
- Timestamps use ISO-like format; logs are suitable for shipping to centralized log systems.

Assumptions
- Testnet base URL: https://testnet.binancefuture.com
- Quantities are expressed in contract/base asset units (verify symbol filters via exchangeInfo).
- `.env` or environment variables are used for credentials.
- This project is for testnet only; do not use mainnet credentials here.

Future Improvements
- Per-symbol exchangeInfo validation (stepSize, tickSize, minNotional).
- Rate-limit handling with automatic backoff using headers (X-MBX-USED-WEIGHT).
- Retry policy tuned per error codes.
- Unit tests + CI integration with HTTP mocking.
- Add more order types (STOP-LIMIT, OCO) and a dry-run/simulation mode.
- Optional lightweight UI or interactive CLI prompts.

Security Notes
- Never commit API keys or `.env` to source control.
- Redact secrets in logs; logging helpers already redact API headers.
- Use separate keys for testnet and mainnet.

Contact / License
- MIT-style starter code (adjust as needed). Add repository license and contributor info as appropriate.