"""
Risk management utilities.
"""
from __future__ import annotations

from typing import Dict, Any
from config import DEFAULT_RISK_PERCENT, MAX_POSITION_SIZE


def calculate_position_size(
    balance: float,
    risk_percent: float = DEFAULT_RISK_PERCENT,
    stop_loss_distance: float = 0.02,  # 2% distance
) -> Dict[str, float]:
    """
    Calculate recommended position size based on risk management rules.
    
    Args:
        balance: Account balance
        risk_percent: Percentage of balance to risk per trade
        stop_loss_distance: Distance to stop loss as decimal (0.02 = 2%)
    
    Returns:
        dict with keys: position_size, max_quantity, risk_amount
    """
    risk_amount = balance * (risk_percent / 100)
    position_size = risk_amount / stop_loss_distance
    max_quantity = (balance * (MAX_POSITION_SIZE / 100)) / 100  # Assume price ~100 for BTC
    
    return {
        "position_size": position_size,
        "max_quantity": min(position_size, max_quantity),
        "risk_amount": risk_amount,
    }


def validate_leverage(leverage: int, max_leverage: int = 125) -> bool:
    """Validate leverage is within acceptable range."""
    return 1 <= leverage <= max_leverage


def calculate_liquidation_price(
    entry_price: float,
    quantity: float,
    leverage: int,
    side: str = "LONG",
) -> float:
    """Calculate estimated liquidation price."""
    if side.upper() == "LONG":
        return entry_price * (1 - (1 / leverage))
    else:
        return entry_price * (1 + (1 / leverage))