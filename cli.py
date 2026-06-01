"""
Professional CLI with argparse subcommands.
"""
from __future__ import annotations

import os
import sys
import argparse
from dotenv import load_dotenv
from pathlib import Path
import requests

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from bot.client import BinanceClient
from bot.commands import CommandHandler
from bot.exceptions import APIError
from bot.logging_config import get_logger

logger = get_logger("cli")


def init_client() -> BinanceClient:
    """Initialize and connect Binance client."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        logger.error("Missing API credentials")
        print("Error: API credentials not configured. Set BINANCE_API_KEY and BINANCE_API_SECRET.")
        sys.exit(1)
    
    client = BinanceClient(api_key=api_key, api_secret=api_secret)
    try:
        client.connect()
    except APIError as e:
        logger.error("Failed to connect: %s", e)
        print(f"Error: {e}")
        sys.exit(1)
    
    return client


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py ticker BTCUSDT
  python cli.py balance
  python cli.py market-buy BTCUSDT 0.001
  python cli.py limit-buy BTCUSDT 0.001 70000
  python cli.py cancel BTCUSDT 123456789
  python cli.py leverage BTCUSDT 10
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Ticker
    ticker_parser = subparsers.add_parser("ticker", help="Get ticker price")
    ticker_parser.add_argument("symbol", help="Symbol e.g., BTCUSDT")
    
    # Balance
    subparsers.add_parser("balance", help="Show account balance")
    
    # Positions
    subparsers.add_parser("positions", help="Show open positions")
    
    # Open Orders
    open_orders_parser = subparsers.add_parser("open-orders", help="Show open orders")
    open_orders_parser.add_argument("symbol", help="Symbol e.g., BTCUSDT")
    
    # Market Buy
    market_buy_parser = subparsers.add_parser("market-buy", help="Place market buy order")
    market_buy_parser.add_argument("symbol", help="Symbol")
    market_buy_parser.add_argument("quantity", type=float, help="Quantity")
    
    # Market Sell
    market_sell_parser = subparsers.add_parser("market-sell", help="Place market sell order")
    market_sell_parser.add_argument("symbol", help="Symbol")
    market_sell_parser.add_argument("quantity", type=float, help="Quantity")
    
    # Limit Buy
    limit_buy_parser = subparsers.add_parser("limit-buy", help="Place limit buy order")
    limit_buy_parser.add_argument("symbol", help="Symbol")
    limit_buy_parser.add_argument("quantity", type=float, help="Quantity")
    limit_buy_parser.add_argument("price", type=float, help="Price")
    
    # Limit Sell
    limit_sell_parser = subparsers.add_parser("limit-sell", help="Place limit sell order")
    limit_sell_parser.add_argument("symbol", help="Symbol")
    limit_sell_parser.add_argument("quantity", type=float, help="Quantity")
    limit_sell_parser.add_argument("price", type=float, help="Price")
    
    # Cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel order")
    cancel_parser.add_argument("symbol", help="Symbol")
    cancel_parser.add_argument("order_id", type=int, help="Order ID")
    
    # Leverage
    leverage_parser = subparsers.add_parser("leverage", help="Set leverage")
    leverage_parser.add_argument("symbol", help="Symbol")
    leverage_parser.add_argument("leverage", type=int, help="Leverage (1-125)")
    
    # Stop Loss
    stop_loss_parser = subparsers.add_parser("stop-loss", help="Place stop loss order")
    stop_loss_parser.add_argument("symbol", help="Symbol")
    stop_loss_parser.add_argument("side", help="BUY or SELL")
    stop_loss_parser.add_argument("quantity", type=float, help="Quantity")
    stop_loss_parser.add_argument("price", type=float, help="Stop price")
    
    # Take Profit
    take_profit_parser = subparsers.add_parser("take-profit", help="Place take profit order")
    take_profit_parser.add_argument("symbol", help="Symbol")
    take_profit_parser.add_argument("side", help="BUY or SELL")
    take_profit_parser.add_argument("quantity", type=float, help="Quantity")
    take_profit_parser.add_argument("price", type=float, help="Take profit price")
    
    # Summary
    subparsers.add_parser("summary", help="Show account summary")
    
    # History
    history_parser = subparsers.add_parser("history", help="Show trade history")
    history_parser.add_argument("symbol", nargs="?", help="Symbol (optional)")
    
    # PnL
    pnl_parser = subparsers.add_parser("pnl", help="Show PnL report")
    pnl_parser.add_argument("symbol", nargs="?", help="Symbol (optional)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Initialize client
    client = init_client()
    handler = CommandHandler(client)
    
    # Route commands
    try:
        if args.command == "ticker":
            handler.handle_ticker(args.symbol)
        elif args.command == "balance":
            handler.handle_balance()
        elif args.command == "positions":
            handler.handle_positions()
        elif args.command == "open-orders":
            handler.handle_open_orders(args.symbol)
        elif args.command == "market-buy":
            handler.handle_market_buy(args.symbol, args.quantity)
        elif args.command == "market-sell":
            handler.handle_market_sell(args.symbol, args.quantity)
        elif args.command == "limit-buy":
            handler.handle_limit_buy(args.symbol, args.quantity, args.price)
        elif args.command == "limit-sell":
            handler.handle_limit_sell(args.symbol, args.quantity, args.price)
        elif args.command == "cancel":
            handler.handle_cancel_order(args.symbol, args.order_id)
        elif args.command == "leverage":
            handler.handle_leverage(args.symbol, args.leverage)
        elif args.command == "stop-loss":
            handler.handle_stop_loss(args.symbol, args.side, args.quantity, args.price)
        elif args.command == "take-profit":
            handler.handle_take_profit(args.symbol, args.side, args.quantity, args.price)
        elif args.command == "summary":
            handler.handle_account_summary()
        elif args.command == "history":
            handler.handle_history(args.symbol)
        elif args.command == "pnl":
            handler.handle_pnl(args.symbol)
    except Exception as e:
        logger.exception("Command failed")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()