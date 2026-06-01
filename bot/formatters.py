"""
Output formatting utilities for clean CLI display.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from decimal import Decimal


def print_header(title: str, width: int = 50) -> None:
    """Print formatted header."""
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width)


def print_table(headers: List[str], rows: List[List[str]], widths: Optional[List[int]] = None) -> None:
    """Print formatted table."""
    if not widths:
        widths = [max(len(h), max(len(row[i]) if i < len(row) else 0 for row in rows)) + 2 for i, h in enumerate(headers)]

    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))

    for row in rows:
        print(" | ".join(str(v).ljust(w) for v, w in zip(row, widths)))


def format_balance(balance_data: Dict[str, Any]) -> str:
    """Format balance response for display."""
    output = []
    print_header("ACCOUNT BALANCE")
    
    headers = ["Asset", "Balance", "Available"]
    rows = []
    
    for asset in balance_data:
        if asset.get("balance") or asset.get("availableBalance"):
            rows.append([
                asset.get("asset", "N/A"),
                f"{float(asset.get('balance', 0)):.2f}",
                f"{float(asset.get('availableBalance', 0)):.2f}",
            ])
    
    if rows:
        print_table(headers, rows)
    else:
        print("No balances found.")
    return ""


def format_positions(positions_data: List[Dict[str, Any]]) -> str:
    """Format positions response for display."""
    active_positions = [p for p in positions_data if float(p.get("positionAmt", 0)) != 0]
    
    if not active_positions:
        print("\nNo open positions.")
        return ""
    
    print_header("OPEN POSITIONS")
    
    for pos in active_positions:
        print(f"\nSymbol: {pos.get('symbol', 'N/A')}")
        side = "LONG" if float(pos.get("positionAmt", 0)) > 0 else "SHORT"
        print(f"Side: {side}")
        print(f"Quantity: {pos.get('positionAmt', 'N/A')}")
        print(f"Entry Price: {pos.get('entryPrice', 'N/A')}")
        print(f"Mark Price: {pos.get('markPrice', 'N/A')}")
        print(f"Unrealized PnL: {pos.get('unRealizedProfit', 'N/A')}")
        print(f"ROE%: {pos.get('roe', 'N/A')}")
    
    return ""


def format_ticker(ticker_data: Dict[str, Any]) -> str:
    """Format ticker response for display."""
    print_header(f"TICKER: {ticker_data.get('symbol', 'N/A')}")
    print(f"Price: {ticker_data.get('price', 'N/A')}")
    return ""


def format_order_summary(order: Dict[str, Any]) -> str:
    """Format single order for display."""
    return f"""
Order ID: {order.get('orderId', 'N/A')}
Symbol: {order.get('symbol', 'N/A')}
Type: {order.get('type', 'N/A')}
Side: {order.get('side', 'N/A')}
Status: {order.get('status', 'N/A')}
Quantity: {order.get('origQty', 'N/A')}
Executed: {order.get('executedQty', 'N/A')}
Price: {order.get('price', 'N/A')}
Avg Price: {order.get('avgPrice', 'N/A')}
"""


def format_open_orders(orders_data: List[Dict[str, Any]]) -> str:
    """Format open orders response for display."""
    if not orders_data:
        print("\nNo open orders.")
        return ""
    
    print_header(f"OPEN ORDERS ({len(orders_data)})")
    
    headers = ["Order ID", "Symbol", "Type", "Side", "Qty", "Price", "Status"]
    rows = []
    
    for o in orders_data:
        rows.append([
            str(o.get('orderId', 'N/A')),
            o.get('symbol', 'N/A'),
            o.get('type', 'N/A'),
            o.get('side', 'N/A'),
            f"{float(o.get('origQty', 0)):.4f}",
            f"{float(o.get('price', 0)):.2f}" if o.get('price') else "MARKET",
            o.get('status', 'N/A'),
        ])
    
    print_table(headers, rows)
    return ""


def format_account_summary(balance: List[Dict], positions: List[Dict], orders: List[Dict]) -> str:
    """Format account summary for display."""
    print_header("ACCOUNT SUMMARY")
    
    # Total balance
    total_balance = sum(float(b.get('balance', 0)) for b in balance)
    total_available = sum(float(b.get('availableBalance', 0)) for b in balance)
    
    # Unrealized PnL
    total_unrealized = sum(float(p.get('unRealizedProfit', 0)) for p in positions)
    
    # Active positions and orders
    active_positions = len([p for p in positions if float(p.get('positionAmt', 0)) != 0])
    open_orders = len([o for o in orders if o.get('status') == 'NEW'])
    
    print(f"Wallet Balance: {total_balance:.2f}")
    print(f"Available Balance: {total_available:.2f}")
    print(f"Total Unrealized PnL: {total_unrealized:.2f}")
    print(f"Open Positions: {active_positions}")
    print(f"Open Orders: {open_orders}")
    
    return ""


def format_pnl(trades_history: List[Dict[str, Any]]) -> str:
    """Format PnL report for display."""
    print_header("PNL REPORT")
    
    total_realized = sum(float(t.get('realizedProfit', 0)) for t in trades_history)
    
    print(f"Total Realized PnL: {total_realized:.2f}")
    print(f"Trades: {len(trades_history)}")
    
    return ""