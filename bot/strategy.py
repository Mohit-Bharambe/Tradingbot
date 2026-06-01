"""
Simple trading strategies.
"""
from __future__ import annotations

from typing import List, Optional, Literal
from enum import Enum


class Signal(Enum):
    """Trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


def get_ema(prices: List[float], period: int = 12) -> Optional[float]:
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: List of prices
        period: EMA period
    
    Returns:
        EMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    k = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = price * k + ema * (1 - k)
    
    return ema


def ema_crossover_signal(
    short_prices: List[float],
    long_prices: List[float],
    short_period: int = 12,
    long_period: int = 26,
) -> Signal:
    """
    Generate trading signal from EMA crossover.
    
    Args:
        short_prices: Recent prices for short EMA
        long_prices: Longer history for long EMA
        short_period: Short EMA period
        long_period: Long EMA period
    
    Returns:
        Signal enum (BUY, SELL, HOLD)
    """
    short_ema = get_ema(short_prices, short_period)
    long_ema = get_ema(long_prices, long_period)
    
    if short_ema is None or long_ema is None:
        return Signal.HOLD
    
    if short_ema > long_ema:
        return Signal.BUY
    elif short_ema < long_ema:
        return Signal.SELL
    else:
        return Signal.HOLD