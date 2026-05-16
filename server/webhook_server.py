#!/usr/bin/env python3
"""
TradingView Webhook Server
Receives alerts from TradingView and processes signals
"""

from flask import Flask, request, jsonify
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

from bot.signal_processor import SignalProcessor, Signal, SignalType, SignalContext, TradeAction

load_dotenv()

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize
processor = SignalProcessor(account_balance=10000)
active_trades = {}


@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """
    Receive TradingView alerts
    Format: SIGNAL_TYPE|SYMBOL|PRICE|VOLUME|MA5|MA13|MA50|MA200
    """
    try:
        data = request.json
        alert_message = data.get('message', '')
        
        logger.info(f"📊 Received alert: {alert_message}")
        
        # Parse message
        parts = alert_message.split('|')
        if len(parts) < 8:
            logger.warning(f"Invalid alert format: {alert_message}")
            return jsonify({"error": "Invalid alert format"}), 400
        
        signal_name, symbol, price, volume, ma5, ma13, ma50, ma200 = parts[:8]
        
        # Convert to floats
        try:
            price = float(price)
            volume = float(volume)
            ma5 = float(ma5)
            ma13 = float(ma13)
            ma50 = float(ma50)
            ma200 = float(ma200)
        except ValueError:
            logger.error(f"Failed to parse numeric values: {parts}")
            return jsonify({"error": "Invalid numeric values"}), 400
        
        # Create context
        context = SignalContext(
            ema_alignment=_determine_ema_alignment(ma5, ma13, ma50, ma200),
            current_ema_5=ma5,
            current_ema_13=ma13,
            current_ema_50=ma50,
            current_ema_200=ma200,
            pivot_pp=0.0,
            pivot_r1=0.0,
            pivot_s1=0.0,
            pivot_r2=0.0,
            pivot_s2=0.0,
            adr_high=0.0,
            adr_low=0.0,
            adr_50_high=0.0,
            adr_50_low=0.0,
            current_session=_get_current_session(),
        )
        
        # Map signal
        signal_type = _map_signal_type(signal_name)
        
        # Create signal
        signal = Signal(
            symbol=symbol,
            signal_type=signal_type,
            price=price,
            timestamp=datetime.now(),
            confidence=signal_type.value[1],
            metadata={
                "volume": volume,
                "source": "TradingView",
            }
        )
        
        # Process signal
        action, confidence, trade_details = processor.process_signal(signal, context)
        
        logger.info(f"✅ Signal processed: {signal_name} → {action.value} "
                   f"(Confidence: {confidence:.2f})")
        
        # Log trade details if action taken
        if action != TradeAction.SKIP:
            logger.info(f"💰 Trade Details:")
            logger.info(f"   Entry: {trade_details['entry_price']:.5f}")
            logger.info(f"   Stop: {trade_details['stop_loss']:.5f}")
            logger.info(f"   Target 1: {trade_details['target_1']:.5f}")
            logger.info(f"   Position Size: ${trade_details['position_size']:.2f}")
            
            # Store trade
            active_trades[symbol] = {
                "action": action.value,
                "confidence": confidence,
                "details": trade_details,
                "created_at": datetime.now().isoformat(),
            }
        
        return jsonify({
            "status": "success",
            "signal": signal_name,
            "action": action.value,
            "confidence": confidence,
            "trade_details": trade_details,
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_trades": len(active_trades),
    }), 200


@app.route('/trades', methods=['GET'])
def get_trades():
    """Get all active trades"""
    return jsonify({
        "total": len(active_trades),
        "trades": active_trades,
    }), 200


@app.route('/trade/<symbol>', methods=['GET'])
def get_trade(symbol):
    """Get specific trade"""
    if symbol in active_trades:
        return jsonify(active_trades[symbol]), 200
    return jsonify({"error": "Trade not found"}), 404


@app.route('/trade/<symbol>', methods=['DELETE'])
def close_trade(symbol):
    """Close trade"""
    if symbol in active_trades:
        del active_trades[symbol]
        logger.info(f"Trade closed: {symbol}")
        return jsonify({"status": "closed"}), 200
    return jsonify({"error": "Trade not found"}), 404


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get signal statistics"""
    stats = processor.get_signal_statistics()
    stats["active_trades"] = len(active_trades)
    return jsonify(stats), 200


def _determine_ema_alignment(ma5, ma13, ma50, ma200):
    """Determine EMA alignment from moving averages"""
    bullish_count = sum([ma5 > ma13, ma13 > ma50, ma50 > ma200])
    bearish_count = sum([ma5 < ma13, ma13 < ma50, ma50 < ma200])
    
    if bullish_count >= 3:
        return "BULLISH"
    elif bearish_count >= 3:
        return "BEARISH"
    else:
        return "WEAK"


def _map_signal_type(signal_name):
    """Map TradingView signal name to SignalType enum"""
    mapping = {
        "GREEN_VECTOR": SignalType.GREEN_VECTOR,
        "RED_VECTOR": SignalType.RED_VECTOR,
        "EMA_BULLISH": SignalType.EMA_BULLISH_ALIGN,
        "EMA_BEARISH": SignalType.EMA_BEARISH_ALIGN,
        "PIVOT_BOUNCE": SignalType.PIVOT_BOUNCE_R1,
        "BREAKOUT_UP": SignalType.ADR_HIGH_REACHED,
        "BREAKOUT_DOWN": SignalType.ADR_LOW_REACHED,
    }
    return mapping.get(signal_name, SignalType.DAILY_OPEN_CROSS)


def _get_current_session():
    """Determine current FX trading session"""
    hour = datetime.now().hour
    
    if 8 <= hour < 17:
        return "LONDON"
    elif 13 <= hour < 22:
        return "NEW_YORK"
    elif 0 <= hour < 9:
        return "TOKYO"
    elif 21 <= hour < 24 or 0 <= hour < 2:
        return "SYDNEY"
    else:
        return "OVERLAP"


if __name__ == '__main__':
    logger.info("🚀 Trading Bot Webhook Server Starting...")
    logger.info(f"Flask running on 0.0.0.0:5000")
    logger.info("Send POST to /webhook/tradingview to process signals")
    app.run(host='0.0.0.0', port=5000, debug=False)
