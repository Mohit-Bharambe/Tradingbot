from __future__ import annotations

from typing import Optional, Dict, Any
import math

from .exceptions import ValidationError

_VALID_SIDES = {"BUY", "SELL"}
_VALID_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize trading symbol.
    Returns uppercase symbol (e.g., 'BTCUSDT').
    Raises ValidationError on invalid input.
    """
    if symbol is None:
        raise ValidationError("symbol is required")
    if not isinstance(symbol, str):
        raise ValidationError("symbol must be a string")
    s = symbol.strip().upper()
    if not s:
        raise ValidationError("symbol must contain visible characters")
    if not s.isalnum():
        raise ValidationError("symbol must be alphanumeric (e.g., BTCUSDT)")
    if len(s) < 3:
        raise ValidationError("symbol is too short to be valid")
    return s


def validate_side(side: str) -> str:
    """
    Validate order side. Allowed values: BUY, SELL.
    Returns normalized uppercase side.
    """
    if side is None:
        raise ValidationError("side is required")
    if not isinstance(side, str):
        raise ValidationError("side must be a string (BUY or SELL)")
    s = side.strip().upper()
    if s not in _VALID_SIDES:
        raise ValidationError(f"side must be one of {_VALID_SIDES}")
    return s


def validate_order_type(order_type: str) -> str:
    """
    Validate order type. Allowed values: MARKET, LIMIT.
    Returns normalized uppercase order type.
    """
    if order_type is None:
        raise ValidationError("order type is required")
    if not isinstance(order_type, str):
        raise ValidationError("order type must be a string (MARKET or LIMIT)")
    t = order_type.strip().upper()
    if t not in _VALID_TYPES:
        raise ValidationError(f"order type must be one of {_VALID_TYPES}")
    return t


def validate_quantity(quantity: Any) -> float:
    """
    Validate quantity is a positive number. Returns quantity as float.
    """
    if quantity is None:
        raise ValidationError("quantity is required")
    try:
        q = float(quantity)
    except Exception:
        raise ValidationError("quantity must be a number")
    if not math.isfinite(q) or q <= 0:
        raise ValidationError("quantity must be a positive finite number")
    return q


def validate_price(price: Any, order_type: str) -> Optional[float]:
    """
    Validate price when required.
    - For LIMIT orders price is required and must be a positive finite number.
    - For MARKET orders price is ignored and None is returned.
    """
    ot = validate_order_type(order_type)
    if ot == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders")
        try:
            p = float(price)
        except Exception:
            raise ValidationError("price must be a number for LIMIT orders")
        if not math.isfinite(p) or p <= 0:
            raise ValidationError("price must be a positive finite number")
        return p
    # MARKET orders do not use price
    return None


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Any,
    price: Any = None,
) -> Dict[str, Any]:
    """
    Convenience validator that validates all common order inputs and
    returns a dict with normalized values:
      { "symbol": str, "side": str, "type": str, "quantity": float, "price": Optional[float] }
    Raises ValidationError on first failure.
    """
    sym = validate_symbol(symbol)
    sd = validate_side(side)
    ot = validate_order_type(order_type)
    qty = validate_quantity(quantity)
    pr = validate_price(price, ot)
    return {"symbol": sym, "side": sd, "type": ot, "quantity": qty, "price": pr}