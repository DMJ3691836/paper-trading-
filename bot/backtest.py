#!/usr/bin/env python3
"""
Backtesting Engine for Historical Signal Testing
Optimize position sizing and validate signal performance
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import statistics

from signal_processor import SignalProcessor, Signal, SignalContext, SignalType
from trading_engine import PaperTradingEngine, Trade


@dataclass
class BacktestResult:
    """Result of a backtest run"""
    total_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    pnl_percent: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: timedelta
    best_trade: float
    worst_trade: float
    
    def to_dict(self) -> Dict:
        return {
            "total_trades": self.total_trades,
            "win_rate": round(self.win_rate, 2),
            "profit_factor": round(self.profit_factor, 2),
            "total_pnl": round(self.total_pnl, 2),
            "pnl_percent": round(self.pnl_percent, 2),
            "sharpe_ratio": round(self.sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            "avg_trade_duration_hours": self.avg_trade_duration.total_seconds() / 3600,
            "best_trade": round(self.best_trade, 2),
            "worst_trade": round(self.worst_trade, 2),
        }


class BacktestData:
    """Historical data for backtesting"""
    
    def __init__(self, symbol: str, csv_file: str):
        """
        Load historical OHLCV data from CSV
        Expected columns: timestamp, open, high, low, close, volume
        """
        self.symbol = symbol
        self.df = pd.read_csv(csv_file)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df = self.df.sort_values('timestamp')
    
    def get_bar(self, timestamp: datetime) -> Optional[Dict]:
        """Get OHLCV data for timestamp"""
        match = self.df[self.df['timestamp'] == timestamp]
        if match.empty:
            return None
        
        row = match.iloc[0]
        return {
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'volume': row['volume'],
        }
    
    def get_bars_range(self, start: datetime, end: datetime) -> List[Dict]:
        """Get OHLCV data range"""
        mask = (self.df['timestamp'] >= start) & (self.df['timestamp'] <= end)
        bars = self.df[mask]
        
        return [{
            'timestamp': row['timestamp'],
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'volume': row['volume'],
        } for _, row in bars.iterrows()]


class Backtester:
    """Main backtesting engine"""
    
    def __init__(self, initial_balance: float = 10000, risk_per_trade: float = 0.02):
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.engine = None
        self.signal_processor = SignalProcessor(initial_balance)
    
    def run_backtest(self, 
                    data: BacktestData,
                    signals: List[Dict],
                    confidence_threshold: float = 6.0) -> BacktestResult:
        """
        Run backtest on historical data with given signals
        
        signals format: [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "signal": "GREEN_VECTOR",
                "price": 1.0850,
                "indicators": {...}
            }
        ]
        """
        self.engine = PaperTradingEngine(self.initial_balance)
        self.engine.initial_balance = self.initial_balance
        
        balance_history = [self.initial_balance]
        trade_durations = []
        all_trades_pnl = []
        
        # Convert signals to timestamped events
        signal_events = {}
        for sig in signals:
            ts = datetime.fromisoformat(sig['timestamp'])
            signal_events[ts] = sig
        
        # Process signals in chronological order
        for sig_timestamp in sorted(signal_events.keys()):
            sig_data = signal_events[sig_timestamp]
            
            try:
                # Parse signal
                signal_type = SignalType[sig_data['signal']]
                price = sig_data['price']
                indicators = sig_data.get('indicators', {})
                
                # Build context
                context = self._build_context(indicators)
                
                # Create signal object
                signal = Signal(
                    symbol=data.symbol,
                    signal_type=signal_type,
                    price=price,
                    timestamp=sig_timestamp,
                    confidence=signal_type.value[1],
                    metadata=indicators
                )
                
                # Process signal
                action, confidence, trade_details = self.signal_processor.process_signal(signal, context)
                
                # Execute trade if confidence sufficient
                if action.name != "SKIP" and confidence >= confidence_threshold:
                    trade = Trade(
                        symbol=data.symbol,
                        direction="LONG" if "BUY" in action.name else "SHORT",
                        entry_price=trade_details['entry_price'],
                        stop_loss=trade_details['stop_loss'],
                        target_1=trade_details['target_1'],
                        target_2=trade_details['target_2'],
                        target_3=trade_details['target_3'],
                        position_size=trade_details['position_size'],
                        signal_type=trade_details['signal_type'],
                        confidence_score=confidence,
                        opened_at=sig_timestamp,
                    )
                    
                    self.engine.open_trade(trade)
                    all_trades_pnl.append(trade)  # Track for later analysis
                
                # Update balance history
                balance_history.append(self.engine.balance)
            
            except (KeyError, ValueError) as e:
                print(f"Error processing signal {sig_data['signal']}: {e}")
                continue
        
        # Close any remaining trades at last price
        if self.engine.active_trades:
            last_signal_ts = max(signal_events.keys())
            last_bar = data.get_bar(last_signal_ts)
            if last_bar:
                for trade in self.engine.active_trades[:]:
                    self.engine.close_trade(
                        self.engine.active_trades.index(trade),
                        last_bar['close'],
                        "BACKTEST_END"
                    )
        
        # Calculate metrics
        return self._calculate_metrics(balance_history, self.engine.closed_trades)
    
    def _build_context(self, indicators: Dict) -> SignalContext:
        """Build SignalContext from indicators"""
        from signal_processor import SignalContext
        
        ema_5 = indicators.get('ema_5', 0)
        ema_13 = indicators.get('ema_13', 0)
        ema_50 = indicators.get('ema_50', 0)
        ema_200 = indicators.get('ema_200', 0)
        price = indicators.get('price', 0)
        
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
            pivot_pp=indicators.get('pivot_pp', 0),
            pivot_r1=indicators.get('pivot_r1', 0),
            pivot_r2=indicators.get('pivot_r2', 0),
            pivot_s1=indicators.get('pivot_s1', 0),
            pivot_s2=indicators.get('pivot_s2', 0),
            adr_high=indicators.get('adr_high', 0),
            adr_low=indicators.get('adr_low', 0),
            adr_50_high=indicators.get('adr_50_high', 0),
            adr_50_low=indicators.get('adr_50_low', 0),
            current_session=indicators.get('session'),
            psy_hi=indicators.get('psy_hi'),
            psy_lo=indicators.get('psy_lo'),
        )
    
    def _calculate_metrics(self, balance_history: List[float], trades: List) -> BacktestResult:
        """Calculate backtest performance metrics"""
        
        if not trades:
            return BacktestResult(
                total_trades=0,
                win_rate=0,
                profit_factor=0,
                total_pnl=0,
                pnl_percent=0,
                sharpe_ratio=0,
                max_drawdown=0,
                avg_trade_duration=timedelta(0),
                best_trade=0,
                worst_trade=0,
            )
        
        # Calculate win rate
        winners = [t for t in trades if t.pnl > 0]
        win_rate = (len(winners) / len(trades)) * 100 if trades else 0
        
        # Calculate profit factor
        total_wins = sum(t.pnl for t in trades if t.pnl > 0)
        total_losses = abs(sum(t.pnl for t in trades if t.pnl < 0))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Calculate total P&L
        total_pnl = sum(t.pnl for t in trades)
        pnl_percent = (total_pnl / self.initial_balance) * 100
        
        # Calculate Sharpe ratio
        returns = [(balance_history[i] - balance_history[i-1]) / balance_history[i-1] 
                  for i in range(1, len(balance_history))]
        sharpe_ratio = self._calculate_sharpe(returns) if returns else 0
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown(balance_history)
        
        # Calculate average trade duration
        durations = [(t.closed_at - t.opened_at) for t in trades if t.closed_at]
        avg_duration = (sum(durations, timedelta()) / len(durations)) if durations else timedelta(0)
        
        # Best and worst trades
        best_trade = max(t.pnl for t in trades) if trades else 0
        worst_trade = min(t.pnl for t in trades) if trades else 0
        
        return BacktestResult(
            total_trades=len(trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_pnl=total_pnl,
            pnl_percent=pnl_percent,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            avg_trade_duration=avg_duration,
            best_trade=best_trade,
            worst_trade=worst_trade,
        )
    
    def _calculate_sharpe(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0
        
        mean_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns)
        
        if std_dev == 0:
            return 0
        
        return (mean_return - risk_free_rate / 252) / std_dev * (252 ** 0.5)
    
    def _calculate_max_drawdown(self, balance_history: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not balance_history:
            return 0
        
        max_balance = balance_history[0]
        max_dd = 0
        
        for balance in balance_history:
            if balance > max_balance:
                max_balance = balance
            
            dd = (max_balance - balance) / max_balance
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100


def run_example_backtest():
    """
    Example backtest with sample data
    """
    # Sample signals from 1 week
    sample_signals = [
        {
            "timestamp": "2024-01-15T08:00:00Z",
            "signal": "GREEN_VECTOR",
            "price": 1.0850,
            "indicators": {
                "ema_5": 1.0860, "ema_13": 1.0855, "ema_50": 1.0845, "ema_200": 1.0820,
                "pivot_pp": 1.0835, "pivot_r1": 1.0880, "pivot_r2": 1.0910,
                "pivot_s1": 1.0805, "pivot_s2": 1.0775,
                "adr_high": 1.0890, "adr_low": 1.0740, "adr_50_high": 1.0815, "adr_50_low": 1.0815,
                "session": "LONDON", "psy_hi": 1.0950, "psy_lo": 1.0700
            }
        },
        {
            "timestamp": "2024-01-15T12:00:00Z",
            "signal": "RED_TO_GREEN_REVERSAL",
            "price": 1.0865,
            "indicators": {
                "ema_5": 1.0875, "ema_13": 1.0870, "ema_50": 1.0855, "ema_200": 1.0830,
                "pivot_pp": 1.0835, "pivot_r1": 1.0880, "pivot_r2": 1.0910,
                "pivot_s1": 1.0805, "pivot_s2": 1.0775,
                "adr_high": 1.0890, "adr_low": 1.0740, "adr_50_high": 1.0815, "adr_50_low": 1.0815,
                "session": "NEW_YORK", "psy_hi": 1.0950, "psy_lo": 1.0700
            }
        },
    ]
    
    # Create backtester
    bt = Backtester(initial_balance=10000, risk_per_trade=0.02)
    
    # Run backtest
    # In real scenario, you would load historical CSV data
    print("Sample backtest signals created")
    print(f"Total signals: {len(sample_signals)}")
    
    return sample_signals


if __name__ == "__main__":
    signals = run_example_backtest()
    print(json.dumps(signals, indent=2))
