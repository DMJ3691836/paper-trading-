#!/usr/bin/env python3
"""
Risk Management System
Enforces trading rules and position limits
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum


class RiskLevel(Enum):
    """Risk level classifications"""
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    HALT = "HALT"


@dataclass
class RiskLimits:
    """Risk management limits"""
    max_daily_loss: float = 500  # Max loss per day
    max_daily_loss_percent: float = 5.0  # Max loss as % of account
    max_consecutive_losses: int = 3  # Stop after N losses
    max_open_trades: int = 5  # Max simultaneous positions
    max_risk_per_trade: float = 2.0  # % of account risk per trade
    max_leverage: float = 1.0  # No leverage (1:1)
    min_win_rate_threshold: float = 40.0  # Minimum win rate to continue
    
    # Session limits
    max_trades_per_session: int = 3
    min_hold_time_minutes: int = 5
    max_hold_time_hours: int = 4
    
    # Equity limits
    min_account_equity: float = 100  # Stop if account below $100
    equity_stop_percent: float = 20  # Stop if equity down 20%
    
    # Confidence requirements
    min_signal_confidence: float = 6.0
    min_confluence_for_add: float = 7.5  # Higher confidence to add
    
    # Time restrictions
    trading_start_hour: int = 8  # 8:00 UTC (London open)
    trading_end_hour: int = 22  # 22:00 UTC (NY close)
    no_trade_hours: List[Tuple[int, int]] = None  # [(0, 6)] = no trades 0-6 UTC
    
    def __post_init__(self):
        if self.no_trade_hours is None:
            self.no_trade_hours = [(22, 8)]  # No Asian session


class RiskManager:
    """Main risk management engine"""
    
    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.trades_this_session = 0
        self.current_session_start = None
        self.trading_halted = False
        self.halt_reason = None
        self.last_trade_time = None
    
    def can_trade(self, 
                 current_balance: float,
                 active_trade_count: int,
                 win_rate: float,
                 current_time: datetime = None) -> Tuple[bool, str]:
        """
        Check if trading is allowed
        
        Returns:
            (allowed: bool, reason: str)
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Check if halted
        if self.trading_halted:
            return False, f"Trading halted: {self.halt_reason}"
        
        # Check minimum equity
        if current_balance < self.limits.min_account_equity:
            self.trading_halted = True
            self.halt_reason = "Account equity below minimum"
            return False, "Account equity below minimum"
        
        # Check equity stop
        if current_balance < self.limits.min_account_equity * (1 - self.limits.equity_stop_percent / 100):
            self.trading_halted = True
            self.halt_reason = "Equity stop loss triggered"
            return False, "Equity stop loss triggered"
        
        # Check daily loss limit
        if self.daily_loss > self.limits.max_daily_loss:
            return False, "Daily loss limit reached"
        
        if self.daily_loss > current_balance * (self.limits.max_daily_loss_percent / 100):
            return False, "Daily loss limit (%) reached"
        
        # Check consecutive losses
        if self.consecutive_losses >= self.limits.max_consecutive_losses:
            return False, f"Consecutive loss limit ({self.limits.max_consecutive_losses}) reached"
        
        # Check open positions
        if active_trade_count >= self.limits.max_open_trades:
            return False, f"Max open trades ({self.limits.max_open_trades}) reached"
        
        # Check win rate
        if win_rate < self.limits.min_win_rate_threshold:
            return False, f"Win rate ({win_rate:.1f}%) below minimum ({self.limits.min_win_rate_threshold}%)"
        
        # Check time restrictions
        if not self._is_trading_hour(current_time):
            return False, "Outside trading hours"
        
        # Check session trade limit
        if self.trades_this_session >= self.limits.max_trades_per_session:
            return False, f"Max trades per session ({self.limits.max_trades_per_session}) reached"
        
        return True, "OK"
    
    def validate_trade(self,
                      signal_confidence: float,
                      position_size: float,
                      account_balance: float,
                      active_trades: int,
                      current_time: datetime = None) -> Tuple[bool, str, RiskLevel]:
        """
        Validate individual trade parameters
        
        Returns:
            (valid: bool, reason: str, risk_level: RiskLevel)
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        risk_level = RiskLevel.SAFE
        
        # Check confidence
        if signal_confidence < self.limits.min_signal_confidence:
            return False, f"Signal confidence {signal_confidence:.1f} below minimum {self.limits.min_signal_confidence}", RiskLevel.WARNING
        
        # Check position size vs account
        position_percent = (position_size / account_balance) * 100
        if position_percent > self.limits.max_risk_per_trade:
            return False, f"Position size {position_percent:.1f}% exceeds max {self.limits.max_risk_per_trade}%", RiskLevel.WARNING
        
        # Calculate risk level
        if active_trades >= self.limits.max_open_trades - 1:
            risk_level = RiskLevel.CAUTION
        if self.consecutive_losses >= self.limits.max_consecutive_losses - 1:
            risk_level = RiskLevel.WARNING
        if self.daily_loss > account_balance * (self.limits.max_daily_loss_percent / 100) * 0.5:
            risk_level = RiskLevel.CRITICAL
        
        return True, "OK", risk_level
    
    def record_trade_closed(self, pnl: float, hold_time_minutes: int):
        """
        Record closed trade for tracking
        """
        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        self.daily_trades += 1
        self.trades_this_session += 1
        self.last_trade_time = datetime.utcnow()
    
    def reset_daily_counters(self):
        """
        Reset daily counters (call at market close/start of day)
        """
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.trades_this_session = 0
        self.current_session_start = datetime.utcnow()
    
    def reset_session_counters(self):
        """
        Reset session-specific counters
        """
        self.trades_this_session = 0
        self.current_session_start = datetime.utcnow()
    
    def get_risk_status(self, 
                       current_balance: float,
                       active_trades: int,
                       win_rate: float) -> Dict:
        """
        Get comprehensive risk status
        """
        can_trade, reason = self.can_trade(current_balance, active_trades, win_rate)
        
        daily_loss_percent = (self.daily_loss / current_balance) * 100 if current_balance > 0 else 0
        
        return {
            "can_trade": can_trade,
            "reason": reason,
            "trading_halted": self.trading_halted,
            "halt_reason": self.halt_reason,
            "daily_loss": round(self.daily_loss, 2),
            "daily_loss_percent": round(daily_loss_percent, 2),
            "consecutive_losses": self.consecutive_losses,
            "daily_trades": self.daily_trades,
            "session_trades": self.trades_this_session,
            "current_balance": round(current_balance, 2),
            "active_positions": active_trades,
            "win_rate": round(win_rate, 2),
        }
    
    def _is_trading_hour(self, current_time: datetime) -> bool:
        """
        Check if current time is within trading hours
        """
        hour = current_time.hour
        
        # Check no-trade windows
        for start, end in self.limits.no_trade_hours:
            if start < end:
                if start <= hour < end:
                    return False
            else:  # Wraps around midnight
                if hour >= start or hour < end:
                    return False
        
        # Check trading window
        if hour < self.limits.trading_start_hour or hour >= self.limits.trading_end_hour:
            return False
        
        return True
    
    def suggest_position_size(self,
                            account_balance: float,
                            risk_amount: float,
                            stop_loss_pips: float,
                            confidence_score: float) -> float:
        """
        Suggest appropriate position size based on risk
        
        Args:
            account_balance: Current account balance
            risk_amount: Max risk in dollars
            stop_loss_pips: Stop loss distance in pips
            confidence_score: Signal confidence (0-10)
        
        Returns:
            Recommended position size
        """
        # Base position size from risk
        base_position = risk_amount / (stop_loss_pips * 0.0001)
        
        # Adjust for confidence
        confidence_multiplier = confidence_score / 10.0
        
        # Max position size is max_risk_per_trade % of account
        max_position = account_balance * (self.limits.max_risk_per_trade / 100)
        
        suggested = base_position * confidence_multiplier
        
        return min(suggested, max_position)
    
    def get_remaining_risk_budget(self, current_balance: float) -> float:
        """
        Get remaining daily risk budget in dollars
        """
        daily_limit = current_balance * (self.limits.max_daily_loss_percent / 100)
        return max(0, daily_limit - self.daily_loss)
    
    def get_session_risk_level(self, 
                              current_balance: float,
                              initial_balance: float) -> RiskLevel:
        """
        Determine current session risk level
        """
        drawdown_percent = ((initial_balance - current_balance) / initial_balance) * 100
        
        if drawdown_percent > 20:
            return RiskLevel.HALT
        elif drawdown_percent > 15:
            return RiskLevel.CRITICAL
        elif drawdown_percent > 10:
            return RiskLevel.WARNING
        elif drawdown_percent > 5:
            return RiskLevel.CAUTION
        else:
            return RiskLevel.SAFE
