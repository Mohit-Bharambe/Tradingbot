"""
Application configuration.
"""
from __future__ import annotations

# Binance API
BINANCE_FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"
BINANCE_FUTURES_MAINNET_URL = "https://fapi.binance.com"
BASE_URL = BINANCE_FUTURES_TESTNET_URL

# API Settings
RECV_WINDOW = 5000
TIMEOUT = 10
MAX_RETRIES = 3

# Trading Defaults
DEFAULT_LEVERAGE = 1
MAX_LEVERAGE = 125
DEFAULT_MARGIN_TYPE = "isolated"  # isolated or cross

# Risk Management
DEFAULT_RISK_PERCENT = 2.0  # Risk 2% of balance per trade
MAX_POSITION_SIZE = 0.5     # Max 50% of balance in one position

# Logging
LOG_DIR = "logs"
LOG_FILE = "bot.log"
LOG_LEVEL = "INFO"

# Feature Flags
ENABLE_STRATEGY_MODULE = True
ENABLE_RISK_CALCULATOR = True
ENABLE_PNL_REPORTS = True