#!/usr/bin/env python3
"""
Paper Trading Engine
Manages trades, P&L, and performance tracking
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
import json


@dataclass
class Trade:
    """Individual trade record"""
    symbol: str
    direction: str  # "LONG" or "SHORT"
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    position_size: float
    signal_type: str
    confidence_score: float
    opened_at: datetime = None
    closed_at: Optional[datetime] = None
    close_price: Optional[float] = None
    close_reason: Optional[str] = None  # "TARGET_1", "TARGET_2", "TARGET_3", "STOP_LOSS", "MANUAL"
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    def __post_init__(self):
        if self.opened_at is None:
            self.opened_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["opened_at"] = self.opened_at.isoformat()
        if self.closed_at:
            data["closed_at"] = self.closed_at.isoformat()
        return data
    
    def close(self, close_price: float, reason: str):
        """Close trade and calculate P&L"""
        self.close_price = close_price
        self.closed_at = datetime.utcnow()
        self.close_reason = reason
        
        if self.direction == "LONG":
            self.pnl = (close_price - self.entry_price) * self.position_size
            self.pnl_percent = ((close_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            self.pnl = (self.entry_price - close_price) * self.position_size
            self.pnl_percent = ((self.entry_price - close_price) / self.entry_price) * 100


class PaperTradingEngine:
    """Paper trading engine"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.active_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
    
    def open_trade(self, trade: Trade) -> bool:
        """
        Open a new trade
        """
        # Check if enough balance
        if trade.position_size > self.balance:
            return False
        
        # Deduct position size from balance
        self.balance -= trade.position_size
        self.active_trades.append(trade)
        
        return True
    
    def close_trade(self, trade_idx: int, close_price: float, reason: str):
        """
        Close an active trade
        """
        if 0 <= trade_idx < len(self.active_trades):
            trade = self.active_trades.pop(trade_idx)
            trade.close(close_price, reason)
            self.closed_trades.append(trade)
            
            # Return position size + P&L to balance
            self.balance += trade.position_size + trade.pnl
    
    def update_trade_on_price_movement(self, price: float) -> List[Dict]:
        """
        Check active trades against current price for exits
        Returns list of closed trades
        """
        closed = []
        trades_to_close = []
        
        for idx, trade in enumerate(self.active_trades):
            # Check if different symbol
            # This is simplified - in production, track by symbol
            
            # Check targets
            if trade.direction == "LONG":
                if price >= trade.target_3:
                    trades_to_close.append((idx, price, "TARGET_3"))
                elif price >= trade.target_2:
                    trades_to_close.append((idx, price, "TARGET_2"))
                elif price >= trade.target_1:
                    trades_to_close.append((idx, price, "TARGET_1"))
                elif price <= trade.stop_loss:
                    trades_to_close.append((idx, price, "STOP_LOSS"))
            
            else:  # SHORT
                if price <= trade.target_3:
                    trades_to_close.append((idx, price, "TARGET_3"))
                elif price <= trade.target_2:
                    trades_to_close.append((idx, price, "TARGET_2"))
                elif price <= trade.target_1:
                    trades_to_close.append((idx, price, "TARGET_1"))
                elif price >= trade.stop_loss:
                    trades_to_close.append((idx, price, "STOP_LOSS"))
        
        # Close trades (in reverse order to maintain indices)
        for idx, close_price, reason in reversed(trades_to_close):
            self.close_trade(idx, close_price, reason)
            closed.append((idx, close_price, reason))
        
        return closed
    
    def get_total_pnl(self) -> float:
        """
        Get total P&L from all closed trades
        """
        return sum(t.pnl for t in self.closed_trades if t.pnl is not None)
    
    def get_pnl_percent(self) -> float:
        """
        Get total P&L as percentage of initial balance
        """
        if self.initial_balance == 0:
            return 0
        return (self.get_total_pnl() / self.initial_balance) * 100
    
    def get_win_rate(self) -> float:
        """
        Get win rate of closed trades
        """
        if not self.closed_trades:
            return 0
        
        winners = sum(1 for t in self.closed_trades if t.pnl > 0)
        return (winners / len(self.closed_trades)) * 100
    
    def get_average_winner(self) -> float:
        """
        Get average profit per winning trade
        """
        winners = [t for t in self.closed_trades if t.pnl > 0]
        if not winners:
            return 0
        return sum(t.pnl for t in winners) / len(winners)
    
    def get_average_loser(self) -> float:
        """
        Get average loss per losing trade
        """
        losers = [t for t in self.closed_trades if t.pnl < 0]
        if not losers:
            return 0
        return sum(t.pnl for t in losers) / len(losers)
    
    def get_profit_factor(self) -> float:
        """
        Get profit factor (total wins / total losses)
        """
        winners = sum(t.pnl for t in self.closed_trades if t.pnl > 0)
        losers = abs(sum(t.pnl for t in self.closed_trades if t.pnl < 0))
        
        if losers == 0:
            return 0 if winners == 0 else float('inf')
        
        return winners / losers
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive trading statistics
        """
        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "total_pnl": self.get_total_pnl(),
            "pnl_percent": round(self.get_pnl_percent(), 2),
            "total_trades": len(self.closed_trades),
            "active_trades": len(self.active_trades),
            "win_rate": round(self.get_win_rate(), 2),
            "average_winner": round(self.get_average_winner(), 2),
            "average_loser": round(self.get_average_loser(), 2),
            "profit_factor": round(self.get_profit_factor(), 2),
        }
    
    def export_trades(self, filename: str = "trades.json"):
        """
        Export all trades to JSON file
        """
        data = {
            "statistics": self.get_statistics(),
            "active_trades": [t.to_dict() for t in self.active_trades],
            "closed_trades": [t.to_dict() for t in self.closed_trades],
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)
