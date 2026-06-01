"""
Command handlers for CLI subcommands.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import sys
import time

from .client import BinanceClient
from .exceptions import APIError
from .formatters import (
    format_balance,
    format_positions,
    format_ticker,
    format_open_orders,
    format_account_summary,
    format_pnl,
    print_header,
)
from .logging_config import get_logger

logger = get_logger("commands")


class CommandHandler:
    """Handler for CLI subcommands."""
    
    def __init__(self, client: BinanceClient):
        self.client = client
    
    def handle_ticker(self, symbol: str) -> None:
        """Display ticker price."""
        try:
            data = self.client.get_ticker_price(symbol)
            format_ticker(data)
            logger.info("Ticker fetched: %s", symbol)
        except APIError as e:
            logger.error("Error fetching ticker: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_balance(self) -> None:
        """Display account balance."""
        try:
            data = self.client.get_balance()
            format_balance(data)
            logger.info("Balance fetched")
        except APIError as e:
            logger.error("Error fetching balance: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_positions(self) -> None:
        """Display open positions."""
        try:
            data = self.client.get_positions()
            format_positions(data)
            logger.info("Positions fetched")
        except APIError as e:
            logger.error("Error fetching positions: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_open_orders(self, symbol: str) -> None:
        """Display open orders."""
        try:
            data = self.client.get_open_orders(symbol)
            format_open_orders(data)
            logger.info("Open orders fetched: %s", symbol)
        except APIError as e:
            logger.error("Error fetching open orders: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_market_buy(self, symbol: str, quantity: float) -> None:
        """Place market buy order."""
        try:
            data = self.client.place_order(symbol, "BUY", "MARKET", quantity, wait_for_fill=True)
            print_header("ORDER EXECUTED")
            print(f"Order ID: {data.get('orderId')}")
            print(f"Symbol: {data.get('symbol')}")
            print(f"Side: {data.get('side')}")
            print(f"Status: {data.get('status')}")
            print(f"Quantity: {data.get('origQty')}")
            print(f"Executed: {data.get('executedQty')}")
            if data.get('avgPrice'):
                print(f"Avg Price: {data.get('avgPrice')}")
            logger.info("Market BUY order executed: %s qty=%s status=%s", symbol, quantity, data.get('status'))
        except APIError as e:
            logger.error("Error placing order: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_market_sell(self, symbol: str, quantity: float) -> None:
        """Place market sell order."""
        try:
            data = self.client.place_order(symbol, "SELL", "MARKET", quantity, wait_for_fill=True)
            print_header("ORDER EXECUTED")
            print(f"Order ID: {data.get('orderId')}")
            print(f"Symbol: {data.get('symbol')}")
            print(f"Side: {data.get('side')}")
            print(f"Status: {data.get('status')}")
            print(f"Quantity: {data.get('origQty')}")
            print(f"Executed: {data.get('executedQty')}")
            if data.get('avgPrice'):
                print(f"Avg Price: {data.get('avgPrice')}")
            logger.info("Market SELL order executed: %s qty=%s status=%s", symbol, quantity, data.get('status'))
        except APIError as e:
            logger.error("Error placing order: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_limit_buy(self, symbol: str, quantity: float, price: float) -> None:
        """Place limit buy order."""
        try:
            data = self.client.place_order(symbol, "BUY", "LIMIT", quantity, price=price, wait_for_fill=False)
            print_header("ORDER PLACED")
            print(f"Order ID: {data.get('orderId')}")
            print(f"Symbol: {data.get('symbol')}")
            print(f"Side: {data.get('side')}")
            print(f"Type: {data.get('type')}")
            print(f"Status: {data.get('status')}")
            print(f"Price: {data.get('price')}")
            print(f"Quantity: {data.get('origQty')}")
            logger.info("Limit BUY order placed: %s qty=%s price=%s status=%s", symbol, quantity, price, data.get('status'))
        except APIError as e:
            logger.error("Error placing order: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_limit_sell(self, symbol: str, quantity: float, price: float) -> None:
        """Place limit sell order."""
        try:
            data = self.client.place_order(symbol, "SELL", "LIMIT", quantity, price=price, wait_for_fill=False)
            print_header("ORDER PLACED")
            print(f"Order ID: {data.get('orderId')}")
            print(f"Symbol: {data.get('symbol')}")
            print(f"Side: {data.get('side')}")
            print(f"Type: {data.get('type')}")
            print(f"Status: {data.get('status')}")
            print(f"Price: {data.get('price')}")
            print(f"Quantity: {data.get('origQty')}")
            logger.info("Limit SELL order placed: %s qty=%s price=%s status=%s", symbol, quantity, price, data.get('status'))
        except APIError as e:
            logger.error("Error placing order: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_cancel_order(self, symbol: str, order_id: int) -> None:
        """Cancel an order."""
        try:
            data = self.client.cancel_order(symbol, order_id)
            print_header("ORDER CANCELLED")
            print(f"Order ID: {data.get('orderId')}")
            print(f"Status: {data.get('status')}")
            logger.info("Order cancelled: %s id=%s", symbol, order_id)
        except APIError as e:
            logger.error("Error cancelling order: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_leverage(self, symbol: str, leverage: int) -> None:
        """Set leverage for symbol."""
        try:
            data = self.client.set_leverage(symbol, leverage)
            print_header("LEVERAGE UPDATED")
            print(f"Symbol: {symbol}")
            print(f"Leverage: {data.get('leverage')}x")
            logger.info("Leverage set: %s leverage=%sx", symbol, leverage)
        except APIError as e:
            logger.error("Error setting leverage: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_stop_loss(self, symbol: str, side: str, quantity: float, price: float) -> None:
        """Place stop loss order."""
        try:
            # Create a virtual order ID
            order_id = int(time.time() * 1000) % 1000000
            
            self.client.stop_loss_manager.add_stop_loss(
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                stop_price=price,
            )
            
            print_header("STOP LOSS ORDER PLACED")
            print(f"Order ID: {order_id}")
            print(f"Symbol: {symbol}")
            print(f"Side: {side}")
            print(f"Stop Price: {price}")
            print(f"Quantity: {quantity}")
            print(f"Status: ACTIVE (client-side monitoring)")
            logger.info("Stop loss order placed: %s qty=%s stopPrice=%s", symbol, quantity, price)
        except APIError as e:
            logger.error("Error placing stop loss: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_take_profit(self, symbol: str, side: str, quantity: float, price: float) -> None:
        """Place take profit order."""
        try:
            # Create a virtual order ID
            order_id = int(time.time() * 1000) % 1000000
            
            self.client.stop_loss_manager.add_take_profit(
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                profit_price=price,
            )
            
            print_header("TAKE PROFIT ORDER PLACED")
            print(f"Order ID: {order_id}")
            print(f"Symbol: {symbol}")
            print(f"Side: {side}")
            print(f"Take Profit Price: {price}")
            print(f"Quantity: {quantity}")
            print(f"Status: ACTIVE (client-side monitoring)")
            logger.info("Take profit order placed: %s qty=%s profitPrice=%s", symbol, quantity, price)
        except APIError as e:
            logger.error("Error placing take profit: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_account_summary(self) -> None:
        """Display account summary."""
        try:
            balance = self.client.get_balance()
            positions = self.client.get_positions()
            orders = self.client.get_all_orders()
            format_account_summary(balance, positions, orders)
            logger.info("Account summary fetched")
        except APIError as e:
            logger.error("Error fetching account summary: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_history(self, symbol: str) -> None:
        """Display trade history."""
        try:
            data = self.client.get_all_orders(symbol)
            format_open_orders(data[-10:])  # Last 10 orders
            logger.info("Trade history fetched: %s", symbol)
        except APIError as e:
            logger.error("Error fetching history: %s", e)
            print(f"Error: {e}")
            sys.exit(1)
    
    def handle_pnl(self, symbol: Optional[str] = None) -> None:
        """Display PnL report."""
        try:
            data = self.client.get_all_orders(symbol) if symbol else []
            format_pnl(data)
            logger.info("PnL report generated")
        except APIError as e:
            logger.error("Error generating PnL report: %s", e)
            print(f"Error: {e}")
            sys.exit(1)