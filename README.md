# Binance Futures Trading Bot

A professional Python trading bot for Binance Futures with market/limit orders, leverage control, and client-side stop loss/take profit management.

## Features

✅ **Order Management**
- Market Buy/Sell orders
- Limit Buy/Sell orders
- Cancel orders
- Order history tracking

✅ **Position Management**
- View open positions
- Set leverage (1-125x)
- Get account balance
- Real-time ticker prices

✅ **Risk Management**
- Client-side stop loss orders
- Client-side take profit orders
- Background price monitoring
- Automatic market order execution

✅ **Production Ready**
- Comprehensive logging
- Error handling
- Session retry logic
- API rate limiting support
- Testnet compatible

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/Mohit-Bharambe/Tradingbot.git
cd Tradingbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Create `.env` file in project root:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

2. Get API credentials from [Binance Testnet](https://testnet.binancefuture.com)

## Usage

### Market Orders

```bash
# Buy 0.001 BTC at market price
python cli.py market-buy BTCUSDT 0.001

# Sell 0.001 BTC at market price
python cli.py market-sell BTCUSDT 0.001
```

### Limit Orders

```bash
# Buy 0.001 BTC at 70,000 USDT
python cli.py limit-buy BTCUSDT 0.001 70000

# Sell 0.001 BTC at 75,000 USDT
python cli.py limit-sell BTCUSDT 0.001 75000
```

### Stop Loss & Take Profit

```bash
# Stop loss: If price drops to 71,000, sell 0.001 BTC
python cli.py stop-loss BTCUSDT SELL 0.001 71000

# Take profit: If price rises to 75,000, sell 0.001 BTC
python cli.py take-profit BTCUSDT SELL 0.001 75000
```

### Account Information

```bash
# Show balance
python cli.py balance

# Show open positions
python cli.py positions

# Show open orders
python cli.py open-orders BTCUSDT

# Show account summary
python cli.py summary

# Show trade history
python cli.py history BTCUSDT

# Show PnL report
python cli.py pnl BTCUSDT
```

### Leverage

```bash
# Set 10x leverage on BTCUSDT
python cli.py leverage BTCUSDT 10
```

### Get Ticker Price

```bash
# Get current BTC price
python cli.py ticker BTCUSDT
```

## Project Structure

```
binance-futures-bot/
├── bot/
│   ├── __init__.py
│   ├── client.py              # Binance API client
│   ├── commands.py            # CLI command handlers
│   ├── exceptions.py          # Custom exceptions
│   ├── logging_config.py      # Logging setup
│   └── stop_loss_manager.py   # Stop loss/take profit manager
├── cli.py                      # CLI entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Example env file
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Architecture

### Client-Side Stop Loss/Take Profit

Since Binance Futures Testnet has limited support for server-side stop loss orders, this bot implements **client-side monitoring**:

1. User places stop loss/take profit order via CLI
2. `StopLossManager` monitors current price in background thread
3. When price hits target, automatically executes market order
4. Order executes immediately with current market price

**Advantages:**
- Works on Testnet
- Guaranteed execution
- No API limitations
- Production-ready pattern

## API Reference

### BinanceClient

```python
from bot.client import BinanceClient

client = BinanceClient(api_key="...", api_secret="...")
client.connect()

# Place market order
response = client.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity=0.001
)

# Place limit order
response = client.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.001,
    price=70000
)

# Get balance
balance = client.get_balance()

# Get positions
positions = client.get_positions()

# Set leverage
client.set_leverage("BTCUSDT", 10)
```

### StopLossManager

```python
# Add stop loss
client.stop_loss_manager.add_stop_loss(
    order_id=123,
    symbol="BTCUSDT",
    side="SELL",
    quantity=0.001,
    stop_price=71000
)

# Add take profit
client.stop_loss_manager.add_take_profit(
    order_id=124,
    symbol="BTCUSDT",
    side="SELL",
    quantity=0.001,
    profit_price=75000
)

# Get active orders
active = client.stop_loss_manager.get_active_stops()
```

## Logging

All API requests and responses are logged to `logs/` directory with full details including:
- Request method and URL
- Request parameters (sanitized)
- Response status and body
- Timestamps
- Error details

View logs:
```bash
tail -f logs/bot.log
```

## Error Handling

The bot handles:
- Network timeouts
- API errors (with detailed messages)
- Rate limiting (automatic retry)
- Invalid parameters
- Connection failures

All errors are logged and displayed to user.

## Testing

```bash
# Test connection
python cli.py ticker BTCUSDT

# Test market order
python cli.py market-buy BTCUSDT 0.001

# Test stop loss
python cli.py stop-loss BTCUSDT SELL 0.001 71000

# View logs
tail -f logs/bot.log
```

## Limitations

- **Testnet Only**: Currently configured for Binance Futures Testnet
- **Stop Loss/Take Profit**: Client-side monitoring (not server-side)
- **Single Account**: One API key per instance

## Future Enhancements

- [ ] Production mainnet support
- [ ] Multiple trading strategies
- [ ] Database integration
- [ ] Web dashboard
- [ ] Automated trading algorithms
- [ ] Risk management profiles
- [ ] Backtesting framework

## Security

⚠️ **Important Security Notes:**

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment variables** for API credentials
3. **Restrict API key permissions** to Futures trading only
4. **Enable IP whitelist** on Binance for API key
5. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`

## Troubleshooting

### Connection Failed
```bash
# Check internet connection
# Verify API credentials in .env
# Ensure Binance Testnet is accessible
```

### Order Rejected
```bash
# Check order quantity meets minimum
# Verify symbol is correct (e.g., BTCUSDT)
# Ensure account has sufficient balance/margin
# Check account leverage settings
```

### Stop Loss Not Triggering
```bash
# Verify bot is running
# Check logs for errors
# Ensure price monitoring is active
# Confirm stop price is reasonable
```

## License

MIT License - See LICENSE file

## Support

For issues or questions:
1. Check logs: `logs/bot.log`
2. Review error messages in CLI output
3. Verify API credentials and network connection
4. Check Binance Futures Testnet status

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Author

Developed for Binance Futures Trading

---

**Disclaimer**: This bot is for educational purposes. Use at your own risk. Always test thoroughly on testnet before production use.