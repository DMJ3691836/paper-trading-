#!/usr/bin/env python3
"""
Extended Signal Types for Advanced Trading
20+ additional signal types covering: Volume, Momentum, Trend, Correlation, Fibonacci, etc.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ExtendedSignalType(Enum):
    """Extended signal types (Tiers 9-20)"""
    
    # Tier 9: Volume Analysis
    VOLUME_SURGE = ("volume", 7.5)
    VOLUME_CLIMAX = ("volume", 8.0)
    VOLUME_DIVERGENCE = ("volume", 7.5)
    OBV_BULLISH_CROSS = ("volume", 7.0)
    OBV_BEARISH_CROSS = ("volume", 7.0)
    
    # Tier 10: Momentum
    RSI_EXTREME_HIGH = ("momentum", 7.5)
    RSI_EXTREME_LOW = ("momentum", 7.5)
    RSI_CENTERLINE_CROSS = ("momentum", 6.5)
    MACD_BULLISH_CROSS = ("momentum", 8.0)
    MACD_BEARISH_CROSS = ("momentum", 8.0)
    CCI_EXTREME = ("momentum", 7.0)
    STOCHASTIC_OVERBOUGHT = ("momentum", 7.0)
    STOCHASTIC_OVERSOLD = ("momentum", 7.0)
    
    # Tier 11: Trend Analysis
    MA_CLUSTER_BULLISH = ("trend", 8.5)
    MA_CLUSTER_BEARISH = ("trend", 8.5)
    MA_SLOPE_STEEP = ("trend", 7.5)
    ICHIMOKU_BULLISH_SIGNAL = ("trend", 8.0)
    ICHIMOKU_BEARISH_SIGNAL = ("trend", 8.0)
    ADX_STRONG_TREND = ("trend", 7.5)
    
    # Tier 12: Support/Resistance
    SR_BREAK_UP = ("sr", 7.5)
    SR_BREAK_DOWN = ("sr", 7.5)
    SR_BOUNCE_UP = ("sr", 7.0)
    SR_BOUNCE_DOWN = ("sr", 7.0)
    SR_ZONE_CONFLUENCE = ("sr", 8.0)
    
    # Tier 13: Correlation
    PAIR_ALIGNMENT = ("correlation", 7.5)
    PAIR_DIVERGENCE = ("correlation", 7.0)
    USD_STRENGTH_EXTREME = ("correlation", 7.5)
    
    # Tier 14: Fibonacci
    FIBONACCI_RETRACEMENT = ("fibonacci", 7.5)
    FIBONACCI_EXTENSION = ("fibonacci", 7.0)
    FIBONACCI_BOUNCE = ("fibonacci", 7.5)
    
    # Tier 15: Elliott Wave
    WAVE_COMPLETE = ("elliott", 7.5)
    WAVE_REVERSAL = ("elliott", 8.0)
    
    # Tier 16: Order Flow
    ORDER_CLIMAX = ("order_flow", 8.0)
    ORDER_DIVERGENCE = ("order_flow", 7.5)
    BUY_IMBALANCE = ("order_flow", 7.5)
    SELL_IMBALANCE = ("order_flow", 7.5)
    
    # Tier 17: Camarilla Levels
    CAMARILLA_BREAKOUT = ("camarilla", 7.0)
    CAMARILLA_BOUNCE = ("camarilla", 7.0)
    
    # Tier 18: ML & Pattern Recognition
    ML_BULLISH_PATTERN = ("ml_pattern", 7.5)
    ML_BEARISH_PATTERN = ("ml_pattern", 7.5)
    ANOMALY_DETECTED = ("ml_pattern", 6.5)


@dataclass
class ExtendedSignal:
    """Extended signal with additional metadata"""
    symbol: str
    signal_type: ExtendedSignalType
    price: float
    timestamp: datetime
    confidence: float
    direction: str  # "BUY", "SELL", "NEUTRAL"
    indicators_used: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CustomSignal:
    """Factory for creating extended signals"""
    
    @staticmethod
    def create_volume_signal(direction: str, 
                            volume_increase: float = 1.5,
                            obv_status: Optional[str] = None) -> Tuple[ExtendedSignal, float]:
        """
        Create volume-based signal
        
        Args:
            direction: "BUY" or "SELL"
            volume_increase: Volume multiplier vs average (1.5 = 50% above average)
            obv_status: Optional OBV trend ("bullish", "bearish", "neutral")
        
        Returns:
            (signal, confidence)
        """
        confidence = 6.0
        
        if volume_increase >= 2.0:
            signal_type = ExtendedSignalType.VOLUME_CLIMAX
            confidence = 8.0
        elif volume_increase >= 1.5:
            signal_type = ExtendedSignalType.VOLUME_SURGE
            confidence = 7.5
        else:
            signal_type = ExtendedSignalType.VOLUME_DIVERGENCE
            confidence = 6.5
        
        if obv_status == "bullish":
            confidence += 0.5
            signal_type = ExtendedSignalType.OBV_BULLISH_CROSS
        elif obv_status == "bearish":
            confidence += 0.5
            signal_type = ExtendedSignalType.OBV_BEARISH_CROSS
        
        signal = ExtendedSignal(
            symbol="EURUSD",
            signal_type=signal_type,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=min(confidence, 10.0),
            direction=direction,
            indicators_used=["VOLUME", "OBV"],
            metadata={
                "volume_increase": volume_increase,
                "obv_status": obv_status,
            }
        )
        
        return signal, min(confidence, 10.0)
    
    @staticmethod
    def create_momentum_signal(rsi_value: float,
                              macd_status: Optional[str] = None,
                              stoch_value: Optional[float] = None) -> Tuple[ExtendedSignal, float]:
        """
        Create momentum-based signal (RSI, MACD, Stochastic)
        
        Args:
            rsi_value: RSI value (0-100)
            macd_status: Optional MACD status ("bullish_cross", "bearish_cross", None)
            stoch_value: Optional Stochastic value (0-100)
        
        Returns:
            (signal, confidence)
        """
        confidence = 6.0
        direction = "NEUTRAL"
        
        # RSI analysis
        if rsi_value > 70:
            signal_type = ExtendedSignalType.RSI_EXTREME_HIGH
            direction = "SELL"
            confidence = 7.5
        elif rsi_value < 30:
            signal_type = ExtendedSignalType.RSI_EXTREME_LOW
            direction = "BUY"
            confidence = 7.5
        elif 45 <= rsi_value <= 55:
            signal_type = ExtendedSignalType.RSI_CENTERLINE_CROSS
            confidence = 6.5
        else:
            signal_type = ExtendedSignalType.MACD_BULLISH_CROSS if rsi_value > 50 else ExtendedSignalType.MACD_BEARISH_CROSS
            confidence = 6.0
        
        # MACD confirmation
        if macd_status == "bullish_cross":
            signal_type = ExtendedSignalType.MACD_BULLISH_CROSS
            direction = "BUY"
            confidence = 8.0
        elif macd_status == "bearish_cross":
            signal_type = ExtendedSignalType.MACD_BEARISH_CROSS
            direction = "SELL"
            confidence = 8.0
        
        # Stochastic confirmation
        if stoch_value is not None:
            if stoch_value > 80:
                signal_type = ExtendedSignalType.STOCHASTIC_OVERBOUGHT
                direction = "SELL"
                confidence = 7.0
            elif stoch_value < 20:
                signal_type = ExtendedSignalType.STOCHASTIC_OVERSOLD
                direction = "BUY"
                confidence = 7.0
        
        signal = ExtendedSignal(
            symbol="EURUSD",
            signal_type=signal_type,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=min(confidence, 10.0),
            direction=direction,
            indicators_used=["RSI", "MACD", "STOCHASTIC"],
            metadata={
                "rsi": rsi_value,
                "macd_status": macd_status,
                "stochastic": stoch_value,
            }
        )
        
        return signal, min(confidence, 10.0)
    
    @staticmethod
    def create_trend_signal(price: float,
                           ma5: float,
                           ma13: float,
                           ma50: float,
                           ma200: float) -> Tuple[ExtendedSignal, float]:
        """
        Create trend signal from MA cluster analysis
        
        Args:
            price: Current price
            ma5, ma13, ma50, ma200: Moving average values
        
        Returns:
            (signal, confidence)
        """
        confidence = 0.0
        direction = "NEUTRAL"
        
        # Check MA alignment
        bullish_count = sum([
            ma5 > ma13,
            ma13 > ma50,
            ma50 > ma200,
        ])
        
        bearish_count = sum([
            ma5 < ma13,
            ma13 < ma50,
            ma50 < ma200,
        ])
        
        # Price position
        price_above_all = price > max(ma5, ma13, ma50, ma200)
        price_below_all = price < min(ma5, ma13, ma50, ma200)
        
        if bullish_count == 3:
            signal_type = ExtendedSignalType.MA_CLUSTER_BULLISH
            direction = "BUY"
            confidence = 8.5
        elif bearish_count == 3:
            signal_type = ExtendedSignalType.MA_CLUSTER_BEARISH
            direction = "SELL"
            confidence = 8.5
        elif bullish_count >= 2:
            signal_type = ExtendedSignalType.ADX_STRONG_TREND
            direction = "BUY"
            confidence = 7.5
        elif bearish_count >= 2:
            signal_type = ExtendedSignalType.ADX_STRONG_TREND
            direction = "SELL"
            confidence = 7.5
        else:
            signal_type = ExtendedSignalType.MA_SLOPE_STEEP
            confidence = 6.0
        
        # Boost if price above/below all MAs
        if price_above_all:
            confidence = min(confidence + 1.0, 10.0)
            direction = "BUY"
        elif price_below_all:
            confidence = min(confidence + 1.0, 10.0)
            direction = "SELL"
        
        signal = ExtendedSignal(
            symbol="EURUSD",
            signal_type=signal_type,
            price=price,
            timestamp=datetime.now(),
            confidence=confidence,
            direction=direction,
            indicators_used=["MA5", "MA13", "MA50", "MA200"],
            metadata={
                "ma5": ma5,
                "ma13": ma13,
                "ma50": ma50,
                "ma200": ma200,
                "bullish_alignment": bullish_count,
                "bearish_alignment": bearish_count,
            }
        )
        
        return signal, confidence
    
    @staticmethod
    def create_macd_signal(macd_line: float,
                          signal_line: float,
                          histogram: float) -> Tuple[ExtendedSignal, float]:
        """
        Create MACD-based signal
        
        Args:
            macd_line: MACD line value
            signal_line: Signal line value
            histogram: MACD histogram value
        
        Returns:
            (signal, confidence)
        """
        confidence = 6.5
        direction = "NEUTRAL"
        
        if histogram > 0.001:  # MACD above signal
            signal_type = ExtendedSignalType.MACD_BULLISH_CROSS
            direction = "BUY"
            confidence = 8.0 if histogram > 0.005 else 7.5
        elif histogram < -0.001:  # MACD below signal
            signal_type = ExtendedSignalType.MACD_BEARISH_CROSS
            direction = "SELL"
            confidence = 8.0 if histogram < -0.005 else 7.5
        else:  # Near crossover
            signal_type = ExtendedSignalType.MACD_BULLISH_CROSS
            confidence = 6.0
        
        signal = ExtendedSignal(
            symbol="EURUSD",
            signal_type=signal_type,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=confidence,
            direction=direction,
            indicators_used=["MACD"],
            metadata={
                "macd_line": macd_line,
                "signal_line": signal_line,
                "histogram": histogram,
            }
        )
        
        return signal, confidence
    
    @staticmethod
    def create_fibonacci_signal(price: float,
                               swing_high: float,
                               swing_low: float,
                               direction: str = "retrace") -> Tuple[Optional[ExtendedSignal], float]:
        """
        Create Fibonacci signal (retracement or extension)
        
        Args:
            price: Current price
            swing_high: Recent swing high
            swing_low: Recent swing low
            direction: "retrace" for retracement, "extend" for extension
        
        Returns:
            (signal or None, confidence)
        """
        fib_levels = [0.236, 0.382, 0.500, 0.618, 0.786]
        range_size = swing_high - swing_low
        
        if direction == "retrace":
            signal_type = ExtendedSignalType.FIBONACCI_RETRACEMENT
            for level in fib_levels:
                fib_price = swing_high - (range_size * level)
                if abs(price - fib_price) < range_size * 0.01:  # Within 1% of level
                    confidence = 7.5 if level in [0.382, 0.618] else 7.0
                    signal = ExtendedSignal(
                        symbol="EURUSD",
                        signal_type=signal_type,
                        price=price,
                        timestamp=datetime.now(),
                        confidence=confidence,
                        direction="BUY",
                        indicators_used=["FIBONACCI"],
                        metadata={
                            "fib_level": level,
                            "fib_price": fib_price,
                        }
                    )
                    return signal, confidence
        
        else:  # extension
            signal_type = ExtendedSignalType.FIBONACCI_EXTENSION
            extension_levels = [1.618, 2.618, 3.618]
            for level in extension_levels:
                fib_price = swing_high + (range_size * level)
                if abs(price - fib_price) < range_size * 0.01:
                    confidence = 7.0
                    signal = ExtendedSignal(
                        symbol="EURUSD",
                        signal_type=signal_type,
                        price=price,
                        timestamp=datetime.now(),
                        confidence=confidence,
                        direction="SELL",
                        indicators_used=["FIBONACCI"],
                        metadata={
                            "fib_level": level,
                            "fib_price": fib_price,
                        }
                    )
                    return signal, confidence
        
        return None, 0.0
    
    @staticmethod
    def create_composite_signal(component_signals: List[Tuple[str, float]]) -> Tuple[ExtendedSignal, float]:
        """
        Create signal from multiple indicator confluence
        
        Args:
            component_signals: List of (signal_type, confidence) tuples
        
        Returns:
            (signal, total_confidence)
        """
        total_confidence = sum(conf for _, conf in component_signals) / len(component_signals)
        
        # Bonus for convergence
        convergence_bonus = min(len(component_signals) * 0.2, 1.0)
        total_confidence = min(total_confidence + convergence_bonus, 10.0)
        
        # Determine buy/sell based on components
        direction = "BUY" if total_confidence > 5.0 else "SELL"
        
        signal = ExtendedSignal(
            symbol="EURUSD",
            signal_type=ExtendedSignalType.ML_BULLISH_PATTERN,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=total_confidence,
            direction=direction,
            indicators_used=[sig[0].upper() for sig in component_signals],
            metadata={
                "component_signals": component_signals,
                "component_count": len(component_signals),
                "average_confidence": sum(conf for _, conf in component_signals) / len(component_signals),
            }
        )
        
        return signal, total_confidence


# Pre-built signal combinations for common setups
SIGNAL_COMBOS = {
    "bullish_momentum": [
        ("volume", 7.5),
        ("momentum", 8.0),
        ("trend", 8.5),
    ],
    "bearish_reversal": [
        ("volume", 8.0),
        ("momentum", 7.5),
        ("order_flow", 8.0),
    ],
    "breakout_setup": [
        ("trend", 7.5),
        ("sr", 8.0),
        ("volume", 7.5),
    ],
    "support_bounce": [
        ("sr", 7.5),
        ("momentum", 7.0),
        ("fibonacci", 7.5),
    ],
}
