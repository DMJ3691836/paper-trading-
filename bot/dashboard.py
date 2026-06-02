#!/usr/bin/env python3
"""
Live Trading Dashboard
Provides real-time monitoring UI
"""

from flask import Blueprint, render_template, jsonify
import json
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def index():
    """
    Main dashboard HTML
    """
    return render_template('dashboard.html')


@dashboard_bp.route('/api/stats')
def get_stats():
    """
    Get current trading statistics
    """
    # This would be populated from trading engine
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "account_balance": 10000,
        "total_pnl": 0,
        "win_rate": 0,
        "active_trades": 0,
        "daily_trades": 0,
    })


@dashboard_bp.route('/api/signals')
def get_signals():
    """
    Get recent signals
    """
    # Read from signals.log
    signals = []
    try:
        with open('signals.log', 'r') as f:
            lines = f.readlines()[-50:]  # Last 50 signals
            for line in lines:
                signals.append(json.loads(line))
    except:
        pass
    
    return jsonify(signals)


@dashboard_bp.route('/api/trades')
def get_trades():
    """
    Get recent trades
    """
    # This would be populated from trading engine
    return jsonify({
        "active": [],
        "closed": []
    })
