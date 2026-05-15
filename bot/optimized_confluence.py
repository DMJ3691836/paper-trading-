#!/usr/bin/env python3
"""
Optimized Confluence Bonus System v2
Enhanced confluence calculations with configurable multipliers and advanced scoring
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class ConfluenceCategory(Enum):
    """Confluence categories for organizing bonus logic"""
    TREND_ALIGNMENT = "trend"
    SUPPORT_RESISTANCE = "sr"
    VOLUME = "volume"
    MOMENTUM = "momentum"
    SESSION = "session"
    VOLATILITY = "volatility"
    CORRELATION = "correlation"


@dataclass
class ConfluenceBonus:
    """Individual confluence bonus configuration"""
    category: ConfluenceCategory
    name: str
    base_bonus: float  # 0.0 to 1.0
    max_bonus: float  # Cap for this bonus
    weight: float = 1.0  # Multiplier for calculation
    enabled: bool = True
    
    def calculate(self, strength: float = 1.0) -> float:
        """Calculate actual bonus with strength factor"""
        if not self.enabled:
            return 0.0
        bonus = self.base_bonus * strength * self.weight
        return min(bonus, self.max_bonus)


@dataclass
class OptimizedConfluenceSystem:
    """Advanced confluence bonus system with configurable parameters"""
    
    bonuses: Dict[str, ConfluenceBonus] = field(default_factory=dict)
    max_total_bonus: float = 2.5  # Maximum total bonus applied
    convergence_threshold: int = 3  # Min signals for convergence bonus
    convergence_bonus_multiplier: float = 0.1  # Per converged signal
    decay_factor: float = 0.9  # Reduce bonus impact over repeated signals
    signal_memory: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default bonuses"""
        self._init_default_bonuses()
    
    def _init_default_bonuses(self):
        """Initialize standard bonuses"""
        self.bonuses = {
            "ema_bullish_match": ConfluenceBonus(
                category=ConfluenceCategory.TREND_ALIGNMENT,
                name="EMA Bullish Match",
                base_bonus=0.5,
                max_bonus=0.5,
                weight=1.0
            ),
            "ema_bearish_match": ConfluenceBonus(
                category=ConfluenceCategory.TREND_ALIGNMENT,
                name="EMA Bearish Match",
                base_bonus=0.5,
                max_bonus=0.5,
                weight=1.0
            ),
            "pivot_confluence": ConfluenceBonus(
                category=ConfluenceCategory.SUPPORT_RESISTANCE,
                name="Pivot Confluence",
                base_bonus=0.3,
                max_bonus=0.3,
                weight=1.0
            ),
            "range_level": ConfluenceBonus(
                category=ConfluenceCategory.SUPPORT_RESISTANCE,
                name="Range Level Hit",
                base_bonus=0.3,
                max_bonus=0.3,
                weight=1.0
            ),
            "london_session": ConfluenceBonus(
                category=ConfluenceCategory.SESSION,
                name="London Session",
                base_bonus=0.2,
                max_bonus=0.2,
                weight=1.5  # Higher volatility
            ),
            "newyork_session": ConfluenceBonus(
                category=ConfluenceCategory.SESSION,
                name="New York Session",
                base_bonus=0.2,
                max_bonus=0.2,
                weight=1.5
            ),
            "tokyo_session": ConfluenceBonus(
                category=ConfluenceCategory.SESSION,
                name="Tokyo Session",
                base_bonus=0.1,
                max_bonus=0.1,
                weight=0.8  # Lower volatility
            ),
            "sydney_session": ConfluenceBonus(
                category=ConfluenceCategory.SESSION,
                name="Sydney Session",
                base_bonus=0.1,
                max_bonus=0.1,
                weight=0.8
            ),
            "reversal_ema_strength": ConfluenceBonus(
                category=ConfluenceCategory.TREND_ALIGNMENT,
                name="Reversal with Strong EMA",
                base_bonus=0.3,
                max_bonus=0.3,
                weight=1.0
            ),
            "volume_confirmation": ConfluenceBonus(
                category=ConfluenceCategory.VOLUME,
                name="Volume Confirmation",
                base_bonus=0.2,
                max_bonus=0.2,
                weight=1.0
            ),
            "momentum_extreme": ConfluenceBonus(
                category=ConfluenceCategory.MOMENTUM,
                name="Momentum Extreme",
                base_bonus=0.2,
                max_bonus=0.25,
                weight=1.0
            ),
        }
    
    def calculate_total_bonus(self, active_bonuses: List[str], 
                             strengths: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate total confluence bonus from active bonuses
        
        Args:
            active_bonuses: List of bonus keys that should be applied
            strengths: Optional dict of strength factors per bonus
        
        Returns:
            Total bonus (capped at max_total_bonus)
        """
        if strengths is None:
            strengths = {}
        
        total = 0.0
        applied_categories = set()
        
        for bonus_key in active_bonuses:
            if bonus_key not in self.bonuses:
                continue
            
            bonus = self.bonuses[bonus_key]
            strength = strengths.get(bonus_key, 1.0)
            bonus_value = bonus.calculate(strength)
            
            # Reduce bonus if same category already applied
            if bonus.category in applied_categories:
                bonus_value *= 0.5  # 50% reduction for same category
            
            total += bonus_value
            applied_categories.add(bonus.category)
        
        # Apply convergence bonus if multiple signals converged
        if len(active_bonuses) >= self.convergence_threshold:
            convergence_bonus = (len(active_bonuses) - self.convergence_threshold + 1) * self.convergence_bonus_multiplier
            total += min(convergence_bonus, 0.5)  # Cap convergence bonus
        
        # Apply decay factor if signal appears frequently
        decay = self._calculate_decay(active_bonuses)
        total *= decay
        
        # Cap at maximum
        return min(total, self.max_total_bonus)
    
    def _calculate_decay(self, active_bonuses: List[str]) -> float:
        """
        Calculate decay factor based on signal history
        Prevents over-weighting repeated signal patterns
        """
        # Convert bonuses to hashable type
        bonus_signature = tuple(sorted(active_bonuses))
        
        # Track occurrences
        occurrences = self.signal_memory.count(str(bonus_signature))
        
        # Apply decay (first = 1.0, second = 0.9, third = 0.81, etc.)
        decay = pow(self.decay_factor, occurrences)
        
        # Store for history (keep last 100)
        self.signal_memory.append(str(bonus_signature))
        if len(self.signal_memory) > 100:
            self.signal_memory = self.signal_memory[-100:]
        
        return decay
    
    def add_custom_bonus(self, key: str, bonus: ConfluenceBonus):
        """Add custom bonus configuration"""
        self.bonuses[key] = bonus
    
    def disable_bonus(self, key: str):
        """Disable specific bonus"""
        if key in self.bonuses:
            self.bonuses[key].enabled = False
    
    def enable_bonus(self, key: str):
        """Enable specific bonus"""
        if key in self.bonuses:
            self.bonuses[key].enabled = True
    
    def adjust_weight(self, key: str, new_weight: float):
        """Adjust weight multiplier for bonus"""
        if key in self.bonuses:
            self.bonuses[key].weight = new_weight
    
    def get_active_bonuses_report(self, active_bonuses: List[str]) -> Dict:
        """Generate report of active bonuses"""
        report = {
            "total_bonuses": len(active_bonuses),
            "by_category": {},
            "details": []
        }
        
        for bonus_key in active_bonuses:
            if bonus_key in self.bonuses:
                bonus = self.bonuses[bonus_key]
                category = bonus.category.value
                
                if category not in report["by_category"]:
                    report["by_category"][category] = 0
                report["by_category"][category] += 1
                
                report["details"].append({
                    "name": bonus.name,
                    "category": category,
                    "base_bonus": bonus.base_bonus
                })
        
        return report


# Preset configurations for different trading styles
class ConfluencePresets:
    """Pre-configured confluence systems for different strategies"""
    
    @staticmethod
    def aggressive() -> OptimizedConfluenceSystem:
        """Aggressive trading - high bonus thresholds"""
        system = OptimizedConfluenceSystem()
        system.max_total_bonus = 3.0
        system.convergence_threshold = 2  # Trigger faster
        system.convergence_bonus_multiplier = 0.15  # Higher bonus
        return system
    
    @staticmethod
    def conservative() -> OptimizedConfluenceSystem:
        """Conservative trading - high confluence requirements"""
        system = OptimizedConfluenceSystem()
        system.max_total_bonus = 1.5
        system.convergence_threshold = 4  # Require more signals
        system.convergence_bonus_multiplier = 0.05  # Lower bonus
        return system
    
    @staticmethod
    def balanced() -> OptimizedConfluenceSystem:
        """Balanced trading - moderate confluence"""
        system = OptimizedConfluenceSystem()
        system.max_total_bonus = 2.0
        system.convergence_threshold = 3
        system.convergence_bonus_multiplier = 0.1
        return system
    
    @staticmethod
    def scalping() -> OptimizedConfluenceSystem:
        """Fast scalping - quick signals with lower thresholds"""
        system = OptimizedConfluenceSystem()
        system.max_total_bonus = 2.5
        system.convergence_threshold = 2
        system.convergence_bonus_multiplier = 0.2
        system.decay_factor = 0.7  # Faster decay to vary trades
        return system
    
    @staticmethod
    def swing_trading() -> OptimizedConfluenceSystem:
        """Swing trading - patient, higher confluence"""
        system = OptimizedConfluenceSystem()
        system.max_total_bonus = 2.5
        system.convergence_threshold = 4
        system.convergence_bonus_multiplier = 0.15
        system.decay_factor = 0.95  # Slower decay
        return system


# Example usage patterns
CONFLUENCE_STRATEGIES = {
    "high_probability": {
        "min_active_bonuses": 3,
        "min_confidence": 7.5,
        "min_bonus": 0.5,
        "description": "Only trade when 3+ confluence factors align"
    },
    "value_trading": {
        "min_active_bonuses": 2,
        "min_confidence": 7.0,
        "min_bonus": 0.3,
        "description": "Trade with 2+ confluence factors"
    },
    "opportunistic": {
        "min_active_bonuses": 1,
        "min_confidence": 6.5,
        "min_bonus": 0.2,
        "description": "Trade with any confluence bonus"
    },
}
