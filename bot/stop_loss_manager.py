"""
Client-side stop loss and take profit order management.
"""
from __future__ import annotations

import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from .logging_config import get_logger

logger = get_logger("stop_loss_manager")


@dataclass
class StopLossOrder:
    """Stop loss order tracker."""
    order_id: int
    symbol: str
    side: str
    quantity: float
    stop_price: float
    created_at: float
    triggered: bool = False


@dataclass
class TakeProfitOrder:
    """Take profit order tracker."""
    order_id: int
    symbol: str
    side: str
    quantity: float
    stop_price: float
    created_at: float
    triggered: bool = False


class StopLossManager:
    """Manages client-side stop loss and take profit orders."""
    
    def __init__(self, get_price_func: Callable, execute_order_func: Callable):
        """
        Args:
            get_price_func: Function to get current price (symbol) -> float
            execute_order_func: Function to execute market order (symbol, side, qty) -> None
        """
        self.get_price = get_price_func
        self.execute_order = execute_order_func
        self.stop_losses: Dict[int, StopLossOrder] = {}
        self.take_profits: Dict[int, TakeProfitOrder] = {}
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def add_stop_loss(
        self,
        order_id: int,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
    ) -> StopLossOrder:
        """Add a stop loss order."""
        order = StopLossOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            stop_price=stop_price,
            created_at=time.time(),
        )
        
        with self._lock:
            self.stop_losses[order_id] = order
        
        logger.info(
            "Added stop loss: orderId=%s symbol=%s side=%s qty=%s stopPrice=%s",
            order_id, symbol, side, quantity, stop_price
        )
        return order
    
    def add_take_profit(
        self,
        order_id: int,
        symbol: str,
        side: str,
        quantity: float,
        profit_price: float,
    ) -> TakeProfitOrder:
        """Add a take profit order."""
        order = TakeProfitOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            stop_price=profit_price,
            created_at=time.time(),
        )
        
        with self._lock:
            self.take_profits[order_id] = order
        
        logger.info(
            "Added take profit: orderId=%s symbol=%s side=%s qty=%s profitPrice=%s",
            order_id, symbol, side, quantity, profit_price
        )
        return order
    
    def start_monitoring(self) -> None:
        """Start monitoring thread."""
        if self._running:
            logger.warning("Monitor already running")
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Stop loss monitor started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring thread."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        logger.info("Stop loss monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Monitor loop - check prices and trigger orders."""
        while self._running:
            try:
                self._check_stop_losses()
                self._check_take_profits()
                time.sleep(1)  # Check every 1 second
            except Exception as e:
                logger.exception("Error in monitor loop: %s", e)
    
    def _check_stop_losses(self) -> None:
        """Check if any stop losses should be triggered."""
        with self._lock:
            orders = list(self.stop_losses.values())
        
        for order in orders:
            if order.triggered:
                continue
            
            try:
                price = self.get_price(order.symbol)
                
                # For SELL position (SHORT): trigger if price <= stop_price
                # For BUY position (LONG): trigger if price <= stop_price
                should_trigger = False
                
                if order.side == "SELL":
                    # Short position - stop loss at lower price
                    should_trigger = price <= order.stop_price
                else:
                    # Long position - stop loss at lower price
                    should_trigger = price <= order.stop_price
                
                if should_trigger:
                    logger.info(
                        "STOP LOSS TRIGGERED: orderId=%s symbol=%s price=%s stopPrice=%s",
                        order.order_id, order.symbol, price, order.stop_price
                    )
                    
                    # Reverse side to close position
                    trigger_side = "SELL" if order.side == "BUY" else "BUY"
                    self.execute_order(order.symbol, trigger_side, order.quantity)
                    
                    with self._lock:
                        order.triggered = True
            
            except Exception as e:
                logger.warning("Error checking stop loss %s: %s", order.order_id, e)
    
    def _check_take_profits(self) -> None:
        """Check if any take profits should be triggered."""
        with self._lock:
            orders = list(self.take_profits.values())
        
        for order in orders:
            if order.triggered:
                continue
            
            try:
                price = self.get_price(order.symbol)
                
                # For SELL position (SHORT): trigger if price >= stop_price
                # For BUY position (LONG): trigger if price >= stop_price
                should_trigger = False
                
                if order.side == "SELL":
                    # Short position - take profit at higher price
                    should_trigger = price >= order.stop_price
                else:
                    # Long position - take profit at higher price
                    should_trigger = price >= order.stop_price
                
                if should_trigger:
                    logger.info(
                        "TAKE PROFIT TRIGGERED: orderId=%s symbol=%s price=%s profitPrice=%s",
                        order.order_id, order.symbol, price, order.stop_price
                    )
                    
                    # Reverse side to close position
                    trigger_side = "SELL" if order.side == "BUY" else "BUY"
                    self.execute_order(order.symbol, trigger_side, order.quantity)
                    
                    with self._lock:
                        order.triggered = True
            
            except Exception as e:
                logger.warning("Error checking take profit %s: %s", order.order_id, e)
    
    def get_active_stops(self) -> Dict[str, Any]:
        """Get all active stop loss orders."""
        with self._lock:
            return {
                "stop_losses": [
                    {
                        "id": o.order_id,
                        "symbol": o.symbol,
                        "side": o.side,
                        "quantity": o.quantity,
                        "stopPrice": o.stop_price,
                        "triggered": o.triggered,
                    }
                    for o in self.stop_losses.values()
                    if not o.triggered
                ],
                "take_profits": [
                    {
                        "id": o.order_id,
                        "symbol": o.symbol,
                        "side": o.side,
                        "quantity": o.quantity,
                        "profitPrice": o.stop_price,
                        "triggered": o.triggered,
                    }
                    for o in self.take_profits.values()
                    if not o.triggered
                ],
            }