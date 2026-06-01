"""
Order placement helpers for Binance Futures Testnet with robust error handling.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from decimal import Decimal, InvalidOperation

from .logging_config import get_logger
from .exceptions import APIError

logger = get_logger("orders")


def _to_decimal(v: Any) -> Optional[Decimal]:
    if v is None or v == "":
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _compute_avg_price_from_fills(fills: Any) -> Optional[Decimal]:
    """
    Compute volume-weighted average price from fills list if available.
    fills expected to be a list of dicts with keys: price, qty
    """
    if not fills or not isinstance(fills, (list, tuple)):
        return None
    total_notional = Decimal("0")
    total_qty = Decimal("0")
    for f in fills:
        price = _to_decimal(f.get("price"))
        qty = _to_decimal(f.get("qty")) or _to_decimal(f.get("executedQty"))
        if price is None or qty is None:
            continue
        total_notional += price * qty
        total_qty += qty
    if total_qty == 0:
        return None
    try:
        return (total_notional / total_qty).quantize(Decimal("0.00000001"))
    except (InvalidOperation, ZeroDivisionError):
        return None


def _format_response(raw: Dict[str, Any]) -> Dict[str, Optional[Any]]:
    """
    Normalize order response to contain primitives useful for CLI/logging.
    """
    order_id = raw.get("orderId") or raw.get("order_id") or raw.get("id")
    status = raw.get("status") or raw.get("orderStatus") or raw.get("state")
    executed_qty = _to_decimal(raw.get("executedQty") or raw.get("cumQty") or raw.get("executed_qty"))
    avg_price = _to_decimal(raw.get("avgPrice")) or _compute_avg_price_from_fills(raw.get("fills"))
    return {
        "orderId": order_id,
        "status": status,
        "executedQty": str(executed_qty) if executed_qty is not None else None,
        "avgPrice": str(avg_price) if avg_price is not None else None,
        "raw": raw,
    }


def _refresh_order_status(client, symbol: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    order_id = raw.get("orderId")
    if order_id is None:
        return raw
    try:
        refreshed = client.get_order(symbol=symbol, order_id=int(order_id))
        return refreshed
    except Exception as exc:
        logger.warning("Could not refresh order status for orderId=%s: %s", order_id, exc)
        return raw


def _call_client_place(client, method: str, **kwargs) -> Dict[str, Any]:
    """
    Uniform client invocation with error mapping.
    Accepts a client implementing place_market_order/place_limit_order/place_order.
    """
    if method == "MARKET":
        if hasattr(client, "place_market_order"):
            return client.place_market_order(symbol=kwargs["symbol"], side=kwargs["side"], quantity=kwargs["quantity"])
        return client.place_order(symbol=kwargs["symbol"], side=kwargs["side"], order_type="MARKET", quantity=kwargs["quantity"])
    if method == "LIMIT":
        if hasattr(client, "place_limit_order"):
            return client.place_limit_order(
                symbol=kwargs["symbol"],
                side=kwargs["side"],
                quantity=kwargs["quantity"],
                price=kwargs["price"],
                timeInForce=kwargs.get("timeInForce", "GTC"),
            )
        return client.place_order(
            symbol=kwargs["symbol"],
            side=kwargs["side"],
            order_type="LIMIT",
            quantity=kwargs["quantity"],
            price=kwargs["price"],
            timeInForce=kwargs.get("timeInForce", "GTC"),
        )
    raise APIError("Unsupported order method")


def place_market_order(client, symbol: str, side: str, quantity: float) -> Dict[str, Optional[Any]]:
    """
    Place a MARKET order via provided client.
    """
    logger.info("Placing MARKET order: symbol=%s side=%s quantity=%s", symbol, side, quantity)
    try:
        raw = _call_client_place(client, "MARKET", symbol=symbol, side=side, quantity=quantity)
        raw = _refresh_order_status(client, symbol, raw)
        formatted = _format_response(raw)
        logger.info("Market order result: orderId=%s status=%s executedQty=%s avgPrice=%s",
                    formatted["orderId"], formatted["status"], formatted["executedQty"], formatted["avgPrice"])
        return formatted
    except APIError:
        raise
    except Exception as e:
        logger.exception("Unexpected error placing MARKET order")
        raise APIError(str(e))


def place_limit_order(client, symbol: str, side: str, quantity: float, price: float, timeInForce: str = "GTC") -> Dict[str, Optional[Any]]:
    """
    Place a LIMIT order via provided client.
    """
    logger.info("Placing LIMIT order: symbol=%s side=%s quantity=%s price=%s tif=%s",
                symbol, side, quantity, price, timeInForce)
    try:
        raw = _call_client_place(
            client,
            "LIMIT",
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
        )
        raw = _refresh_order_status(client, symbol, raw)
        formatted = _format_response(raw)
        logger.info("Limit order result: orderId=%s status=%s executedQty=%s avgPrice=%s",
                    formatted["orderId"], formatted["status"], formatted["executedQty"], formatted["avgPrice"])
        return formatted
    except APIError:
        raise
    except Exception as e:
        logger.exception("Unexpected error placing LIMIT order")
        raise APIError(str(e))