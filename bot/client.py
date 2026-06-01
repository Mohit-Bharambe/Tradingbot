"""
Extended Binance Futures Testnet client wrapper.
"""
from __future__ import annotations

import os
import time
import hmac
import hashlib
import urllib.parse
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter, Retry

from .exceptions import APIError
from .logging_config import get_logger, log_api_request, log_api_response
from .stop_loss_manager import StopLossManager

logger = get_logger("client")
DEFAULT_FUTURES_TESTNET_BASE = "https://testnet.binancefuture.com"


class BinanceClient:
    """Extended Binance Futures Testnet client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = DEFAULT_FUTURES_TESTNET_BASE,
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
        self._session.mount("https://", HTTPAdapter(max_retries=retries))

        # Initialize client-side stop loss/take profit manager
        self.stop_loss_manager = StopLossManager(
            get_price_func=lambda symbol: float(self.get_ticker_price(symbol).get("price", 0)),
            execute_order_func=self._execute_market_order,
        )
        self.stop_loss_manager.start_monitoring()

    def connect(self) -> bool:
        """Verify connectivity to testnet."""
        try:
            url = f"{self.base_url}/fapi/v1/time"
            log_api_request(logger, "GET", url)
            resp = self._session.get(url, timeout=self.timeout)
            log_api_response(logger, resp)
            resp.raise_for_status()
            logger.info("Connected to Binance Futures Testnet")
            return True
        except Exception as e:
            logger.error("Connection failed: %s", e)
            raise APIError(f"Connection failed: {e}")

    def _get_server_time(self) -> int:
        """Fetch server time in milliseconds."""
        try:
            url = f"{self.base_url}/fapi/v1/time"
            r = self._session.get(url, timeout=self.timeout)
            r.raise_for_status()
            return int(r.json().get("serverTime"))
        except Exception:
            logger.warning("Could not fetch server time; using local time")
            return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature."""
        qs = urllib.parse.urlencode(params, doseq=True)
        return hmac.new(self.api_secret.encode(), qs.encode(), hashlib.sha256).hexdigest()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request.
        
        For GET: params go in URL query string.
        For POST/DELETE: params go in request body as form-encoded data.
        """
        url = f"{self.base_url}{path}"
        params = params or {}
        
        # Log request (redact sensitive data)
        log_params = dict(params)
        if "signature" in log_params:
            log_params["signature"] = "<REDACTED>"
        log_api_request(
            logger, 
            method, 
            url, 
            headers=headers, 
            params=log_params if method.upper() == "GET" else None, 
            body=log_params if method.upper() != "GET" else None
        )
        
        try:
            if method.upper() == "GET":
                response = self._session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                response = self._session.request(
                    method=method,
                    url=url,
                    data=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            
            log_api_response(logger, response)
            response.raise_for_status()
            return response.json()
        
        except requests.HTTPError as e:
            try:
                body = response.json()
            except Exception:
                body = response.text if response is not None else str(e)
            logger.error("HTTP error: %s", body)
            raise APIError(f"API Error: {body}")
        
        except requests.Timeout:
            logger.error("Request timeout")
            raise APIError("Request timeout")
        
        except requests.RequestException as e:
            logger.exception("Network error")
            raise APIError(f"Network error: {e}")

    def _signed_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make signed request (adds timestamp and signature)."""
        if not self.api_key or not self.api_secret:
            raise APIError("API key and secret are required for signed requests")

        params = params.copy() if params else {}
        params["timestamp"] = self._get_server_time()
        params["signature"] = self._sign(params)
        
        logger.debug(
            "Signed request: symbol=%s side=%s type=%s",
            params.get("symbol"),
            params.get("side"),
            params.get("type"),
        )
        
        headers = {"X-MBX-APIKEY": self.api_key}
        return self._request(method, path, params=params, headers=headers)

    def _wait_for_order_fill(
        self,
        symbol: str,
        order_id: int,
        max_wait_seconds: int = 5,
        poll_interval: float = 0.5,
    ) -> Dict[str, Any]:
        """Poll order status until FILLED, CANCELED, or timeout."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            try:
                order = self.get_order(symbol, order_id)
                status = order.get("status")
                
                if status in ("FILLED", "CANCELED", "REJECTED", "EXPIRED"):
                    logger.info("Order reached terminal state: %s", status)
                    return order
                
                time.sleep(poll_interval)
            except Exception as e:
                logger.warning("Error polling order status: %s", e)
                time.sleep(poll_interval)
        
        logger.warning("Order status poll timeout after %s seconds", max_wait_seconds)
        try:
            return self.get_order(symbol, order_id)
        except Exception as e:
            logger.error("Failed to fetch final order status: %s", e)
            return {"orderId": order_id, "status": "UNKNOWN", "error": str(e)}

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stopPrice: Optional[float] = None,
        timeInForce: str = "GTC",
        wait_for_fill: bool = True,
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            order_type: MARKET, LIMIT
            quantity: Order quantity
            price: Price for LIMIT orders
            stopPrice: Stop price for stop orders
            timeInForce: GTC, IOC, FOK, GTX (for LIMIT orders)
            wait_for_fill: Poll order status until filled
        
        Returns:
            Order details dict
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(quantity),
        }
        
        if order_type == "LIMIT":
            if price is None:
                raise APIError("price required for LIMIT orders")
            params["price"] = str(price)
            params["timeInForce"] = timeInForce
        
        if stopPrice is not None:
            params["stopPrice"] = str(stopPrice)
        
        logger.info("Placing %s order: %s %s qty=%s", order_type, side, symbol, quantity)
        response = self._signed_request("POST", "/fapi/v1/order", params=params)
        
        if order_type == "MARKET" and wait_for_fill and response.get("orderId"):
            order_id = response.get("orderId")
            logger.info("Market order placed, waiting for fill...")
            response = self._wait_for_order_fill(symbol, order_id)
        
        return response

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order."""
        params = {"symbol": symbol, "orderId": order_id}
        logger.info("Cancelling order: %s id=%s", symbol, order_id)
        return self._signed_request("DELETE", "/fapi/v1/order", params=params)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status."""
        params = {"symbol": symbol, "orderId": order_id}
        return self._signed_request("GET", "/fapi/v1/order", params=params)

    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Get open orders."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        result = self._signed_request("GET", "/fapi/v1/openOrders", params=params)
        return result if isinstance(result, list) else []

    def get_all_orders(self, symbol: Optional[str] = None, limit: int = 100) -> list:
        """Get all orders."""
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        result = self._signed_request("GET", "/fapi/v1/allOrders", params=params)
        return result if isinstance(result, list) else []

    def get_balance(self) -> list:
        """Get account balance."""
        result = self._signed_request("GET", "/fapi/v2/balance")
        return result if isinstance(result, list) else []

    def get_positions(self) -> list:
        """Get open positions."""
        result = self._signed_request("GET", "/fapi/v2/positionRisk")
        return result if isinstance(result, list) else []

    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker price."""
        params = {"symbol": symbol}
        return self._request("GET", "/fapi/v1/ticker/price", params=params)

    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage for symbol."""
        params = {"symbol": symbol, "leverage": leverage}
        logger.info("Setting leverage: %s leverage=%sx", symbol, leverage)
        return self._signed_request("POST", "/fapi/v1/leverage", params=params)

    def _execute_market_order(self, symbol: str, side: str, quantity: float) -> None:
        """
        Execute market order (called by stop loss manager when target is hit).
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
        """
        try:
            self.place_order(symbol, side, "MARKET", quantity, wait_for_fill=False)
            logger.info("Market order executed: %s %s qty=%s", side, symbol, quantity)
        except Exception as e:
            logger.error("Failed to execute market order: %s", e)