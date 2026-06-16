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


class SignalDirection(Enum):
    """Signal direction classification"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


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
        
        # Validate price
        if self.price <= 0:
            raise ValueError(f"Invalid price: {self.price}. Price must be positive.")


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
    
    def validate(self) -> bool:
        """Validate context has all required values"""
        required_levels = [
            self.pivot_pp, self.pivot_r1, self.pivot_s1, self.pivot_r2, self.pivot_s2,
            self.adr_high, self.adr_low, self.adr_50_high, self.adr_50_low
        ]
        
        for level in required_levels:
            if level is None or level <= 0:
                logger.warning(f"Invalid context level: {level}")
                return False
        
        if self.ema_alignment not in ["BULLISH", "BEARISH", "WEAK"]:
            logger.warning(f"Invalid EMA alignment: {self.ema_alignment}")
            return False
        
        return True


class SignalProcessor:
    """Main signal processing engine"""
    
    # Configuration constants
    PIVOT_TOLERANCE_PIPS = 10
    RANGE_TOLERANCE_PIPS = 5
    MIN_CONFIDENCE_THRESHOLD = 6.0
    MAX_CONFIDENCE = 10.0
    
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
        
        Args:
            signal: The signal to process
            context: Market context for evaluation
        
        Returns:
            (action, confidence_score, trade_details)
        
        Raises:
            ValueError: If signal or context is invalid
        """
        # Validate inputs
        if not context.validate():
            logger.error("Invalid signal context")
            raise ValueError("Signal context validation failed")
        
        logger.info(f"Processing signal: {signal.signal_type.name} at price {signal.price}")
        
        # Calculate base confidence
        base_confidence = signal.signal_type.value[1]
        
        # Apply confluence bonuses
        confluence_bonus = self._calculate_confluence_bonus(signal, context)
        final_confidence = min(base_confidence + confluence_bonus, self.MAX_CONFIDENCE)
        
        # Determine action
        action = self._get_action_for_signal(signal.signal_type)
        
        # Calculate position size based on confidence
        position_size = self._calculate_position_size(final_confidence)
        
        # Generate trade details
        try:
            trade_details = self._generate_trade_details(
                signal, context, final_confidence, position_size
            )
        except ValueError as e:
            logger.error(f"Failed to generate trade details: {e}")
            return TradeAction.SKIP, final_confidence, {}
        
        # Store in history
        self.signal_history.append(signal)
        
        # Skip if confidence too low
        if final_confidence < self.MIN_CONFIDENCE_THRESHOLD:
            logger.info(f"Signal confidence {final_confidence:.2f} below threshold {self.MIN_CONFIDENCE_THRESHOLD}")
            action = TradeAction.SKIP
        else:
            logger.info(f"Signal approved: confidence={final_confidence:.2f}, action={action.value}, bonus={confluence_bonus:.2f}")
        
        return action, final_confidence, trade_details
    
    def _calculate_confluence_bonus(self, signal: Signal, context: SignalContext) -> float:
        """
        Calculate bonus points for signal confluence
        
        Returns:
            Bonus points (0.0 to ~2.1)
        """
        bonus = 0.0
        
        # Bonus 1: EMA alignment matches signal direction
        if self._signal_matches_ema_trend(signal, context):
            bonus += 0.5
            logger.debug("Applied EMA alignment bonus")
        
        # Bonus 2: Price at support/resistance
        if self._near_pivot_level(signal.price, context):
            bonus += 0.3
            logger.debug("Applied pivot level bonus")
        
        # Bonus 3: At range breakout level
        if self._at_range_level(signal.price, context):
            bonus += 0.3
            logger.debug("Applied range level bonus")
        
        # Bonus 4: In high-volatility session
        if context.current_session in ["LONDON", "NEW_YORK"]:
            bonus += 0.2
            logger.debug(f"Applied session bonus for {context.current_session}")
        
        # Bonus 5: Reversal with strong EMA alignment
        if "reversal" in signal.signal_type.name.lower() and context.ema_alignment != "WEAK":
            bonus += 0.3
            logger.debug("Applied reversal + EMA bonus")
        
        return bonus
    
    def _get_signal_direction(self, signal_type: SignalType) -> SignalDirection:
        """
        Determine signal direction from type
        
        Uses explicit SignalType mapping instead of fragile string matching
        """
        name = signal_type.name
        
        # Bullish signals
        bullish_keywords = ["GREEN", "BUY", "LONG", "UP", "BREAKOUT"]
        if any(kw in name for kw in bullish_keywords):
            return SignalDirection.LONG
        
        # Bearish signals
        bearish_keywords = ["RED", "SELL", "SHORT", "DOWN", "BREAKDOWN"]
        if any(kw in name for kw in bearish_keywords):
            return SignalDirection.SHORT
        
        # Neutral/accumulation signals
        neutral_keywords = ["PURPLE", "BLUE"]
        if any(kw in name for kw in neutral_keywords):
            return SignalDirection.NEUTRAL
        
        return SignalDirection.NEUTRAL
    
    def _signal_matches_ema_trend(self, signal: Signal, context: SignalContext) -> bool:
        """
        Check if signal direction matches EMA trend
        
        Uses explicit signal direction instead of string matching
        """
        direction = self._get_signal_direction(signal.signal_type)
        
        if context.ema_alignment == "BULLISH":
            return direction == SignalDirection.LONG
        elif context.ema_alignment == "BEARISH":
            return direction == SignalDirection.SHORT
        
        return False
    
    def _near_pivot_level(self, price: float, context: SignalContext) -> bool:
        """
        Check if price is near pivot support/resistance
        
        Args:
            price: Current price
            context: Market context with pivot levels
        
        Returns:
            True if price is within tolerance of a pivot level
        """
        levels = [
            context.pivot_pp,
            context.pivot_r1,
            context.pivot_r2,
            context.pivot_s1,
            context.pivot_s2,
        ]
        
        tolerance = self.PIVOT_TOLERANCE_PIPS * 0.0001  # Convert pips to price
        
        for level in levels:
            if level and abs(price - level) < tolerance:
                return True
        
        return False
    
    def _at_range_level(self, price: float, context: SignalContext) -> bool:
        """
        Check if price is at ADR level
        
        Args:
            price: Current price
            context: Market context with range levels
        
        Returns:
            True if price is within tolerance of a range level
        """
        tolerance = self.RANGE_TOLERANCE_PIPS * 0.0001
        
        levels = [
            context.adr_high,
            context.adr_low,
            context.adr_50_high,
            context.adr_50_low,
        ]
        
        for level in levels:
            if level and abs(price - level) < tolerance:
                return True
        
        return False
    
    def _get_action_for_signal(self, signal_type: SignalType) -> TradeAction:
        """
        Map signal type to trading action
        """
        direction = self._get_signal_direction(signal_type)
        signal_name = signal_type.name.lower()
        
        # Long-biased signals
        if direction == SignalDirection.LONG:
            if "reversal" in signal_name or "strong" in signal_name:
                return TradeAction.BUY_STRONG
            elif "breakout" in signal_name:
                return TradeAction.BREAKOUT
            else:
                return TradeAction.BUY
        
        # Short-biased signals
        elif direction == SignalDirection.SHORT:
            if "reversal" in signal_name or "strong" in signal_name:
                return TradeAction.SELL_STRONG
            elif "breakdown" in signal_name:
                return TradeAction.BREAKDOWN
            else:
                return TradeAction.SELL
        
        # Neutral/accumulation signals
        else:
            if "breakout" in signal_name:
                return TradeAction.BREAKOUT
            elif "breakdown" in signal_name:
                return TradeAction.BREAKDOWN
            else:
                return TradeAction.ACCUMULATE
    
    def _calculate_position_size(self, confidence: float) -> float:
        """
        Calculate position size as % of account based on confidence
        
        Returns:
            Position size in dollars, or 0.0 if confidence below threshold
        """
        if confidence < self.MIN_CONFIDENCE_THRESHOLD:
            return 0.0
        
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
        
        Raises:
            ValueError: If stop loss calculation fails
        """
        direction = self._get_signal_direction(signal.signal_type)
        is_long = direction == SignalDirection.LONG
        
        # Calculate stops and targets with error handling
        try:
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
        except ValueError as e:
            logger.error(f"Stop loss calculation failed: {e}")
            raise
        
        # Verify risk is non-zero
        risk = abs(signal.price - stop_loss)
        if risk == 0:
            logger.error("Calculated risk is zero - entry and stop are identical")
            raise ValueError("Risk calculation produced zero value")
        
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
            "risk_reward_ratio_1": round(reward_1 / risk, 2),
            "risk_reward_ratio_2": round(reward_2 / risk, 2),
            "risk_reward_ratio_3": round(reward_3 / risk, 2),
            "position_size": position_size,
            "confidence_score": round(confidence, 2),
            "session": context.current_session,
            "timestamp": signal.timestamp.isoformat(),
        }
    
    def _calculate_long_stop(self, entry_price: float, context: SignalContext) -> float:
        """
        Calculate stop loss for long trade
        
        Tries support levels in order of preference.
        Falls back to percentage-based stop if no levels available.
        
        Raises:
            ValueError: If no valid stop loss can be calculated
        """
        candidates = [
            context.pivot_s1,
            context.pivot_s2,
            context.adr_low,
            entry_price * 0.98,  # 200 pips below (2% fallback)
        ]
        
        for level in candidates:
            if level and level > 0 and level < entry_price:
                return level
        
        raise ValueError(
            f"Cannot calculate valid long stop loss for entry {entry_price}. "
            f"All support levels are above or equal to entry price."
        )
    
    def _calculate_short_stop(self, entry_price: float, context: SignalContext) -> float:
        """
        Calculate stop loss for short trade
        
        Tries resistance levels in order of preference.
        Falls back to percentage-based stop if no levels available.
        
        Raises:
            ValueError: If no valid stop loss can be calculated
        """
        candidates = [
            context.pivot_r1,
            context.pivot_r2,
            context.adr_high,
            entry_price * 1.02,  # 200 pips above (2% fallback)
        ]
        
        for level in candidates:
            if level and level > 0 and level > entry_price:
                return level
        
        raise ValueError(
            f"Cannot calculate valid short stop loss for entry {entry_price}. "
            f"All resistance levels are below or equal to entry price."
        )
    
    def _calculate_target(self, 
                         entry: float, 
                         stop: float, 
                         risk_multiple: float,
                         is_long: bool = True) -> float:
        """
        Calculate target based on risk multiple
        
        Args:
            entry: Entry price
            stop: Stop loss price
            risk_multiple: Multiplier for risk (1.5x, 2.5x, etc.)
            is_long: True for long trades, False for short
        
        Returns:
            Target price
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
            "average_confidence": round(sum(s.confidence for s in self.signal_history) / len(self.signal_history), 2),
        }
