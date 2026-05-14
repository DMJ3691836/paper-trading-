#!/usr/bin/env python3
"""
Webhook Handler for TradingView Integration
Receives and processes alerts from Traders Reality + FX Sessions indicators
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
from typing import Dict, Any

from signal_processor import SignalProcessor, Signal, SignalContext, SignalType, TradeAction
from trading_engine import PaperTradingEngine, Trade

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize components
signal_processor = SignalProcessor(account_balance=10000)
trading_engine = PaperTradingEngine(initial_balance=10000)

# Global state
last_signals = {}  # symbol -> last signal received


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    Main webhook endpoint for TradingView alerts
    
    Expected JSON format:
    {
        "symbol": "EURUSD",
        "signal": "GREEN_VECTOR",
        "price": 1.0850,
        "time": "2024-05-14T12:30:00Z",
        "indicators": {
            "pvsra_color": "green",
            "volume_multiple": 1.8,
            "ema_5": 1.0860,
            "ema_13": 1.0855,
            "ema_50": 1.0845,
            "ema_200": 1.0820,
            "pivot_pp": 1.0835,
            "pivot_r1": 1.0880,
            "pivot_r2": 1.0910,
            "pivot_s1": 1.0805,
            "pivot_s2": 1.0775,
            "adr_high": 1.0890,
            "adr_low": 1.0740,
            "adr_50_high": 1.0815,
            "adr_50_low": 1.0815,
            "session": "LONDON",
            "psy_hi": 1.0950,
            "psy_lo": 1.0700
        }
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required = ["symbol", "signal", "price"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Parse signal
        symbol = data["symbol"]
        signal_name = data["signal"]
        price = float(data["price"])
        
        logger.info(f"Received signal: {signal_name} for {symbol} at {price}")
        
        # Get signal type
        try:
            signal_type = SignalType[signal_name]
        except KeyError:
            logger.warning(f"Unknown signal type: {signal_name}")
            return jsonify({"error": f"Unknown signal type: {signal_name}"}), 400
        
        # Parse indicators
        indicators = data.get("indicators", {})
        
        # Build signal context
        context = _build_signal_context(symbol, indicators)
        
        # Create signal object
        signal = Signal(
            symbol=symbol,
            signal_type=signal_type,
            price=price,
            timestamp=datetime.fromisoformat(data.get("time", datetime.utcnow().isoformat())),
            confidence=signal_type.value[1],
            metadata=indicators
        )
        
        # Process signal
        action, confidence, trade_details = signal_processor.process_signal(signal, context)
        
        # Execute trade if action warrants
        trade_result = None
        if action != TradeAction.SKIP and confidence >= 6.0:
            trade_result = _execute_trade(
                symbol, 
                action, 
                trade_details, 
                confidence
            )
        
        # Log signal
        _log_signal(symbol, signal_name, price, confidence, action, trade_result)
        
        # Store last signal
        last_signals[symbol] = {
            "signal": signal_name,
            "price": price,
            "confidence": confidence,
            "action": action.value,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        response = {
            "status": "received",
            "symbol": symbol,
            "signal": signal_name,
            "confidence_score": round(confidence, 2),
            "action": action.value,
            "trade_executed": trade_result is not None,
        }
        
        if trade_result:
            response["trade"] = trade_result
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods=["GET"])
def get_status():
    """
    Get current status of trading engine and last signals
    """
    return jsonify({
        "account_balance": trading_engine.balance,
        "active_trades": len(trading_engine.active_trades),
        "closed_trades": len(trading_engine.closed_trades),
        "total_pnl": trading_engine.get_total_pnl(),
        "win_rate": trading_engine.get_win_rate(),
        "last_signals": last_signals,
        "signal_stats": signal_processor.get_signal_statistics(),
    }), 200


@app.route("/trades", methods=["GET"])
def get_trades():
    """
    Get all trades
    """
    return jsonify({
        "active": [t.to_dict() for t in trading_engine.active_trades],
        "closed": [t.to_dict() for t in trading_engine.closed_trades],
    }), 200


@app.route("/test", methods=["POST"])
def test_webhook():
    """
    Test webhook with sample data
    """
    test_data = {
        "symbol": "EURUSD",
        "signal": "GREEN_VECTOR",
        "price": 1.0850,
        "time": datetime.utcnow().isoformat() + "Z",
        "indicators": {
            "pvsra_color": "green",
            "volume_multiple": 1.8,
            "ema_5": 1.0860,
            "ema_13": 1.0855,
            "ema_50": 1.0845,
            "ema_200": 1.0820,
            "pivot_pp": 1.0835,
            "pivot_r1": 1.0880,
            "pivot_r2": 1.0910,
            "pivot_s1": 1.0805,
            "pivot_s2": 1.0775,
            "adr_high": 1.0890,
            "adr_low": 1.0740,
            "adr_50_high": 1.0815,
            "adr_50_low": 1.0815,
            "session": "LONDON",
            "psy_hi": 1.0950,
            "psy_lo": 1.0700
        }
    }
    
    # Send as JSON
    response = request.app.test_client().post(
        "/webhook",
        json=test_data,
        content_type="application/json"
    )
    
    return jsonify({
        "test_data_sent": test_data,
        "response": json.loads(response.data),
    }), 200


def _build_signal_context(symbol: str, indicators: Dict) -> SignalContext:
    """
    Build SignalContext from webhook indicators
    """
    # Determine EMA alignment
    ema_5 = indicators.get("ema_5", 0)
    ema_13 = indicators.get("ema_13", 0)
    ema_50 = indicators.get("ema_50", 0)
    ema_200 = indicators.get("ema_200", 0)
    price = indicators.get("price", 0)  # Will be overridden by signal price
    
    if ema_5 > ema_13 > ema_50 > ema_200 > price:
        ema_alignment = "BULLISH"
    elif ema_5 < ema_13 < ema_50 < ema_200 < price:
        ema_alignment = "BEARISH"
    else:
        ema_alignment = "WEAK"
    
    return SignalContext(
        ema_alignment=ema_alignment,
        current_ema_5=ema_5,
        current_ema_13=ema_13,
        current_ema_50=ema_50,
        current_ema_200=ema_200,
        pivot_pp=indicators.get("pivot_pp", 0),
        pivot_r1=indicators.get("pivot_r1", 0),
        pivot_r2=indicators.get("pivot_r2", 0),
        pivot_s1=indicators.get("pivot_s1", 0),
        pivot_s2=indicators.get("pivot_s2", 0),
        adr_high=indicators.get("adr_high", 0),
        adr_low=indicators.get("adr_low", 0),
        adr_50_high=indicators.get("adr_50_high", 0),
        adr_50_low=indicators.get("adr_50_low", 0),
        current_session=indicators.get("session", None),
        psy_hi=indicators.get("psy_hi", None),
        psy_lo=indicators.get("psy_lo", None),
    )


def _execute_trade(symbol: str, action: TradeAction, trade_details: Dict, confidence: float) -> Dict:
    """
    Execute trade via trading engine
    """
    trade = Trade(
        symbol=symbol,
        direction="LONG" if "BUY" in action.name else "SHORT",
        entry_price=trade_details["entry_price"],
        stop_loss=trade_details["stop_loss"],
        target_1=trade_details["target_1"],
        target_2=trade_details["target_2"],
        target_3=trade_details["target_3"],
        position_size=trade_details["position_size"],
        signal_type=trade_details["signal_type"],
        confidence_score=confidence,
    )
    
    trading_engine.open_trade(trade)
    
    return trade.to_dict()


def _log_signal(symbol: str, signal_name: str, price: float, confidence: float, 
                action: TradeAction, trade_result: Any):
    """
    Log signal to file
    """
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "signal": signal_name,
        "price": price,
        "confidence": confidence,
        "action": action.value,
        "trade_executed": trade_result is not None,
    }
    
    with open("signals.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000, debug=True)
