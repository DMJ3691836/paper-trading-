#!/usr/bin/env python3
"""
Complete Signal Processor for Traders Reality + FX Sessions Integration
Processes all 30+ trading signals with confluence scoring
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """All signal types by tier"""
    # Tier 1: PVSRA Vectors
    GREEN_VECTOR = ("pvsra", 8.5, "green_vector")
    RED_VECTOR = ("pvsra", 8.5, "red_vector")
    BLUE_VECTOR = ("pvsra", 7.0, "blue_vector")
    PURPLE_VECTOR = ("pvsra", 7.0, "purple_vector")
    
    # Tier 2: Reversals
    RED_TO_GREEN_REVERSAL = ("reversal", 9.5, "red_to_green_reversal")
    GREEN_TO_RED_REVERSAL = ("reversal", 9.5, "green_to_red_reversal")
    BLUE_TO_RED = ("reversal", 8.5, "blue_to_red")
    RED_TO_BLUE = ("reversal", 8.5, "red_to_blue")
    GREEN_TO_PURPLE = ("reversal", 8.0, "green_to_purple")
    PURPLE_TO_GREEN = ("reversal", 8.0, "purple_to_green")
    BLUE_TO_PURPLE = ("reversal", 7.5, "blue_to_purple")
    PURPLE_TO_BLUE = ("reversal", 7.5, "purple_to_blue")
    
    # Tier 3: EMA Alignment
    EMA_BULLISH_ALIGN = ("ema", 8.0, "ema_bullish_align")
    EMA_BEARISH_ALIGN = ("ema", 8.0, "ema_bearish_align")
    EMA_WEAK_ALIGN = ("ema", 5.5, "ema_weak_align")
    
    # Tier 4: Pivot Bounces
    PIVOT_BOUNCE_PP = ("pivot", 7.0, "pivot_bounce_pp")
    PIVOT_BOUNCE_R1 = ("pivot", 7.5, "pivot_bounce_r1")
    PIVOT_BOUNCE_R2 = ("pivot", 7.0, "pivot_bounce_r2")
    PIVOT_BOUNCE_S1 = ("pivot", 7.5, "pivot_bounce_s1")
    PIVOT_BOUNCE_S2 = ("pivot", 7.0, "pivot_bounce_s2")
    PIVOT_BOUNCE_R3 = ("pivot", 6.5, "pivot_bounce_r3")
    PIVOT_BOUNCE_S3 = ("pivot", 6.5, "pivot_bounce_s3")
    
    # Tier 5: ADR Breakouts
    ADR_HIGH_REACHED = ("range", 7.5, "adr_high_reached")
    ADR_LOW_REACHED = ("range", 7.5, "adr_low_reached")
    ADR_50_HIGH_REACHED = ("range", 7.0, "adr_50_high_reached")
    ADR_50_LOW_REACHED = ("range", 7.0, "adr_50_low_reached")
    AWR_HIGH_REACHED = ("range", 8.0, "awr_high_reached")
    AWR_LOW_REACHED = ("range", 8.0, "awr_low_reached")
    AMR_HIGH_REACHED = ("range", 7.0, "amr_high_reached")
    AMR_LOW_REACHED = ("range", 7.0, "amr_low_reached")
    RD_HIGH_REACHED = ("range", 7.0, "rd_high_reached")
    RD_LOW_REACHED = ("range", 7.0, "rd_low_reached")
    RW_HIGH_REACHED = ("range", 7.0, "rw_high_reached")
    RW_LOW_REACHED = ("range", 7.0, "rw_low_reached")
    
    # Tier 6: Psy Levels
    PSY_HI_CROSSOVER = ("psy", 6.5, "psy_hi_crossover")
    PSY_HI_CROSSUNDER = ("psy", 6.5, "psy_hi_crossunder")
    PSY_LO_CROSSOVER = ("psy", 6.5, "psy_lo_crossover")
    PSY_LO_CROSSUNDER = ("psy", 6.5, "psy_lo_crossunder")
    
    # Tier 7: Daily Open
    DAILY_OPEN_CROSS = ("level", 5.5, "daily_open_cross")
    
    # Tier 8: FX Sessions
    LONDON_SESSION_START = ("session", 6.0, "london_session_start")
    LONDON_SESSION_END = ("session", 6.0, "london_session_end")
    NEW_YORK_SESSION_START = ("session", 6.0, "new_york_session_start")
    NEW_YORK_SESSION_END = ("session", 6.0, "new_york_session_end")
    TOKYO_SESSION_START = ("session", 6.0, "tokyo_session_start")
    TOKYO_SESSION_END = ("session", 6.0, "tokyo_session_end")
    SYDNEY_SESSION_START = ("session", 6.0, "sydney_session_start")
    SYDNEY_SESSION_END = ("session", 6.0, "sydney_session_end")
    
    # Opening Range Breakouts
    OR_R1_BREAKOUT = ("or", 7.5, "or_r1_breakout")
    OR_R2_BREAKOUT = ("or", 7.0, "or_r2_breakout")
    OR_S1_BREAKDOWN = ("or", 7.5, "or_s1_breakdown")
    OR_S2_BREAKDOWN = ("or", 7.0, "or_s2_breakdown")
    
    # Session Levels
    LONDON_HIGH_CROSSED = ("session_level", 7.0, "london_high_crossed")
    LONDON_LOW_CROSSED = ("session_level", 7.0, "london_low_crossed")
    NY_HIGH_CROSSED = ("session_level", 7.0, "ny_high_crossed")
    NY_LOW_CROSSED = ("session_level", 7.0, "ny_low_crossed")
    TOKYO_HIGH_CROSSED = ("session_level", 7.0, "tokyo_high_crossed")
    TOKYO_LOW_CROSSED = ("session_level", 7.0, "tokyo_low_crossed")
    SYDNEY_HIGH_CROSSED = ("session_level", 7.0, "sydney_high_crossed")
    SYDNEY_LOW_CROSSED = ("session_level", 7.0, "sydney_low_crossed")


class TradeAction(Enum):
    """Trading actions"""
    BUY = "BUY"
    SELL = "SELL"
    BUY_STRONG = "BUY_STRONG"
    SELL_STRONG = "SELL_STRONG"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    ACCUMULATE = "ACCUMULATE"
    TAKE_PROFIT = "TAKE_PROFIT"
    ADD = "ADD"
    CLOSE = "CLOSE"
    SKIP = "SKIP"


@dataclass
class Signal:
    """Single signal from indicator"""
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: datetime
    confidence: float
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SignalContext:
    """Context for signal evaluation"""
    ema_alignment: str  # "BULLISH", "BEARISH", "WEAK"
    current_ema_5: float
    current_ema_13: float
    current_ema_50: float
    current_ema_200: float
    pivot_pp: float
    pivot_r1: float
    pivot_s1: float
    pivot_r2: float
    pivot_s2: float
    adr_high: float
    adr_low: float
    adr_50_high: float
    adr_50_low: float
    current_session: Optional[str] = None
    psy_hi: Optional[float] = None
    psy_lo: Optional[float] = None


class SignalProcessor:
    """Main signal processing engine"""
    
    # Bonus points for signal combinations
    CONFLUENCE_BONUSES = {
        ("pvsra", "reversal"): 0.5,  # Vector reversal
        ("pvsra", "ema"): 0.3,  # Vector + EMA alignment
        ("reversal", "pivot"): 0.3,  # Reversal at pivot
        ("range", "session"): 0.2,  # Range break + session
    }
    
    POSITION_SIZE_MULTIPLIERS = {
        (9, 10): 2.5,  # Max confidence
        (8, 8.9): 2.0,
        (7, 7.9): 1.5,
        (6, 6.9): 1.0,
        (0, 5.9): 0.0,  # Skip
    }
    
    def __init__(self, account_balance: float = 10000):
        self.account_balance = account_balance
        self.risk_per_trade = 0.02  # 2% risk
        self.signal_history: List[Signal] = []
    
    def process_signal(self, 
                      signal: Signal, 
                      context: SignalContext) -> Tuple[TradeAction, float, Dict]:
        """
        Process incoming signal and generate trade action
        
        Returns:
            (action, confidence_score, trade_details)
        """
        logger.info(f"Processing signal: {signal.signal_type.name}")
        
        # Calculate base confidence
        base_confidence = signal.signal_type.value[1]
        
        # Apply confluence bonuses
        confluence_bonus = self._calculate_confluence_bonus(signal, context)
        final_confidence = min(base_confidence + confluence_bonus, 10.0)
        
        # Determine action
        action = self._get_action_for_signal(signal.signal_type)
        
        # Calculate position size based on confidence
        position_size = self._calculate_position_size(final_confidence)
        
        # Generate trade details
        trade_details = self._generate_trade_details(
            signal, context, final_confidence, position_size
        )
        
        # Store in history
        self.signal_history.append(signal)
        
        # Skip if confidence too low
        if final_confidence < 6.0:
            action = TradeAction.SKIP
        
        return action, final_confidence, trade_details
    
    def _calculate_confluence_bonus(self, signal: Signal, context: SignalContext) -> float:
        """
        Calculate bonus points for signal confluence
        """
        bonus = 0.0
        signal_category = signal.signal_type.value[0]
        
        # Bonus 1: EMA alignment matches signal direction
        if self._signal_matches_ema_trend(signal, context):
            bonus += 0.5
        
        # Bonus 2: Price at support/resistance
        if self._near_pivot_level(signal.price, context):
            bonus += 0.3
        
        # Bonus 3: At range breakout level
        if self._at_range_level(signal.price, context):
            bonus += 0.3
        
        # Bonus 4: In high-volatility session
        if context.current_session in ["LONDON", "NEW_YORK"]:
            bonus += 0.2
        
        # Bonus 5: Multiple signal categories active
        if "reversal" in str(signal.signal_type) and context.ema_alignment != "WEAK":
            bonus += 0.3
        
        return bonus
    
    def _signal_matches_ema_trend(self, signal: Signal, context: SignalContext) -> bool:
        """
        Check if signal direction matches EMA trend
        """
        signal_name = signal.signal_type.name.lower()
        
        if context.ema_alignment == "BULLISH":
            return "buy" in signal_name or "up" in signal_name or "long" in signal_name
        elif context.ema_alignment == "BEARISH":
            return "sell" in signal_name or "down" in signal_name or "short" in signal_name
        
        return False
    
    def _near_pivot_level(self, price: float, context: SignalContext, tolerance_pips: float = 10) -> bool:
        """
        Check if price is near pivot support/resistance
        """
        levels = [
            context.pivot_pp,
            context.pivot_r1,
            context.pivot_r2,
            context.pivot_s1,
            context.pivot_s2,
        ]
        
        tolerance = tolerance_pips * 0.0001  # Convert pips to price
        
        for level in levels:
            if abs(price - level) < tolerance:
                return True
        
        return False
    
    def _at_range_level(self, price: float, context: SignalContext, tolerance_pips: float = 5) -> bool:
        """
        Check if price is at ADR level
        """
        tolerance = tolerance_pips * 0.0001
        
        levels = [
            context.adr_high,
            context.adr_low,
            context.adr_50_high,
            context.adr_50_low,
        ]
        
        for level in levels:
            if abs(price - level) < tolerance:
                return True
        
        return False
    
    def _get_action_for_signal(self, signal_type: SignalType) -> TradeAction:
        """
        Map signal type to trading action
        """
        signal_name = signal_type.name.lower()
        
        if "green" in signal_name or "buy" in signal_name or "long" in signal_name:
            if "strong" in signal_name or "reversal" in signal_name:
                return TradeAction.BUY_STRONG
            elif "breakout" in signal_name:
                return TradeAction.BREAKOUT
            else:
                return TradeAction.BUY
        
        elif "red" in signal_name or "sell" in signal_name or "short" in signal_name:
            if "strong" in signal_name or "reversal" in signal_name:
                return TradeAction.SELL_STRONG
            elif "breakdown" in signal_name:
                return TradeAction.BREAKDOWN
            else:
                return TradeAction.SELL
        
        elif "purple" in signal_name or "blue" in signal_name:
            return TradeAction.ACCUMULATE
        
        elif "breakout" in signal_name:
            return TradeAction.BREAKOUT
        
        elif "breakdown" in signal_name:
            return TradeAction.BREAKDOWN
        
        return TradeAction.SKIP
    
    def _calculate_position_size(self, confidence: float) -> float:
        """
        Calculate position size as % of account based on confidence
        """
        for (min_conf, max_conf), multiplier in self.POSITION_SIZE_MULTIPLIERS.items():
            if min_conf <= confidence <= max_conf:
                return (self.account_balance * self.risk_per_trade * multiplier) / 100
        
        return 0.0
    
    def _generate_trade_details(self,
                               signal: Signal,
                               context: SignalContext,
                               confidence: float,
                               position_size: float) -> Dict:
        """
        Generate complete trade details
        """
        signal_name = signal.signal_type.name.lower()
        
        # Determine direction
        is_long = any(x in signal_name for x in ["green", "buy", "long", "up", "breakout"])
        
        # Calculate stops and targets
        if is_long:
            stop_loss = self._calculate_long_stop(signal.price, context)
            target_1 = self._calculate_target(signal.price, stop_loss, 1.5, is_long=True)
            target_2 = self._calculate_target(signal.price, stop_loss, 2.5, is_long=True)
            target_3 = self._calculate_target(signal.price, stop_loss, 3.5, is_long=True)
        else:
            stop_loss = self._calculate_short_stop(signal.price, context)
            target_1 = self._calculate_target(signal.price, stop_loss, 1.5, is_long=False)
            target_2 = self._calculate_target(signal.price, stop_loss, 2.5, is_long=False)
            target_3 = self._calculate_target(signal.price, stop_loss, 3.5, is_long=False)
        
        risk = abs(signal.price - stop_loss)
        reward_1 = abs(target_1 - signal.price)
        reward_2 = abs(target_2 - signal.price)
        reward_3 = abs(target_3 - signal.price)
        
        return {
            "signal_type": signal.signal_type.name,
            "symbol": signal.symbol,
            "direction": "LONG" if is_long else "SHORT",
            "entry_price": signal.price,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "target_3": target_3,
            "risk_pips": risk * 10000,
            "reward_pips_1": reward_1 * 10000,
            "reward_pips_2": reward_2 * 10000,
            "reward_pips_3": reward_3 * 10000,
            "risk_reward_ratio_1": reward_1 / risk if risk > 0 else 0,
            "risk_reward_ratio_2": reward_2 / risk if risk > 0 else 0,
            "risk_reward_ratio_3": reward_3 / risk if risk > 0 else 0,
            "position_size": position_size,
            "confidence_score": round(confidence, 2),
            "session": context.current_session,
            "timestamp": signal.timestamp.isoformat(),
        }
    
    def _calculate_long_stop(self, entry_price: float, context: SignalContext) -> float:
        """
        Calculate stop loss for long trade
        """
        # Try support levels in order
        candidates = [
            context.pivot_s1,
            context.pivot_s2,
            context.adr_low,
            entry_price * 0.99,  # 100 pips below
        ]
        
        for level in candidates:
            if level < entry_price:
                return level
        
        return entry_price * 0.98
    
    def _calculate_short_stop(self, entry_price: float, context: SignalContext) -> float:
        """
        Calculate stop loss for short trade
        """
        # Try resistance levels in order
        candidates = [
            context.pivot_r1,
            context.pivot_r2,
            context.adr_high,
            entry_price * 1.01,  # 100 pips above
        ]
        
        for level in candidates:
            if level > entry_price:
                return level
        
        return entry_price * 1.02
    
    def _calculate_target(self, 
                         entry: float, 
                         stop: float, 
                         risk_multiple: float,
                         is_long: bool = True) -> float:
        """
        Calculate target based on risk multiple
        """
        risk = abs(entry - stop)
        reward = risk * risk_multiple
        
        if is_long:
            return entry + reward
        else:
            return entry - reward
    
    def get_signal_statistics(self) -> Dict:
        """
        Return statistics on processed signals
        """
        if not self.signal_history:
            return {"total_signals": 0}
        
        by_type = {}
        for signal in self.signal_history:
            sig_type = signal.signal_type.value[0]
            by_type[sig_type] = by_type.get(sig_type, 0) + 1
        
        return {
            "total_signals": len(self.signal_history),
            "signals_by_type": by_type,
            "average_confidence": sum(s.confidence for s in self.signal_history) / len(self.signal_history),
        }
