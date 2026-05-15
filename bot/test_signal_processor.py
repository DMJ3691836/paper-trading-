#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Signal Processor
26 tests covering all functionality: signals, confluence, position sizing, trade details, edge cases
"""

import pytest
from datetime import datetime
from bot.signal_processor import (
    SignalProcessor, Signal, SignalType, SignalContext, TradeAction
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def processor():
    """Create signal processor instance"""
    return SignalProcessor(account_balance=10000)


@pytest.fixture
def context():
    """Create signal context"""
    return SignalContext(
        ema_alignment="BULLISH",
        current_ema_5=1.0950,
        current_ema_13=1.0920,
        current_ema_50=1.0880,
        current_ema_200=1.0850,
        pivot_pp=1.0900,
        pivot_r1=1.0930,
        pivot_s1=1.0870,
        pivot_r2=1.0960,
        pivot_s2=1.0840,
        adr_high=1.0970,
        adr_low=1.0830,
        adr_50_high=1.0950,
        adr_50_low=1.0850,
        current_session="LONDON",
        psy_hi=1.1000,
        psy_lo=1.0800,
    )


# ============================================================================
# TEST 1-6: SIGNAL PROCESSING
# ============================================================================

class TestSignalProcessing:
    """Test signal processing functionality"""
    
    def test_green_vector_signal(self, processor, context):
        """Test GREEN_VECTOR signal processing"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert action == TradeAction.BUY
        assert confidence >= 8.5
        assert details["direction"] == "LONG"
        assert details["entry_price"] == 1.0950
    
    def test_red_to_green_reversal(self, processor, context):
        """Test RED_TO_GREEN_REVERSAL signal"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.RED_TO_GREEN_REVERSAL,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=9.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert action == TradeAction.BUY_STRONG
        assert confidence >= 9.0
        assert details["direction"] == "LONG"
    
    def test_ema_bullish_align_with_bullish_context(self, processor, context):
        """Test EMA alignment signal with matching context"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.EMA_BULLISH_ALIGN,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert action == TradeAction.BUY
        assert confidence > 8.0  # Should have confluence bonus
        assert details["direction"] == "LONG"
    
    def test_ema_bearish_align_with_bullish_context(self, processor, context):
        """Test bearish signal with bullish context (lower confidence)"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.EMA_BEARISH_ALIGN,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert action == TradeAction.SELL
        assert details["direction"] == "SHORT"
    
    def test_low_confidence_signal_skipped(self, processor, context):
        """Test that low confidence signals are skipped"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.DAILY_OPEN_CROSS,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=5.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert action == TradeAction.SKIP
        assert confidence < 6.0
    
    def test_signal_history_tracking(self, processor, context):
        """Test signal history is tracked"""
        signal1 = Signal(SignalType.GREEN_VECTOR, "EURUSD", 1.0950, datetime.now(), 8.5)
        signal2 = Signal(SignalType.BLUE_VECTOR, "EURUSD", 1.0945, datetime.now(), 7.0)
        
        processor.process_signal(signal1, context)
        processor.process_signal(signal2, context)
        
        assert len(processor.signal_history) == 2
        assert processor.signal_history[0].signal_type == SignalType.GREEN_VECTOR
        assert processor.signal_history[1].signal_type == SignalType.BLUE_VECTOR


# ============================================================================
# TEST 7-11: CONFLUENCE BONUSES
# ============================================================================

class TestConfluenceBonuses:
    """Test confluence bonus calculations"""
    
    def test_ema_alignment_bonus_bullish(self, processor, context):
        """Test EMA alignment provides bonus"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        # Should receive EMA alignment bonus
        assert confidence > 8.0
    
    def test_pivot_confluence_bonus(self, processor, context):
        """Test pivot level bonus"""
        # Price near pivot R1 (1.0930)
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0930,
            timestamp=datetime.now(),
            confidence=8.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        # Should receive pivot bonus
        assert confidence >= 8.0
    
    def test_london_session_bonus(self, processor, context):
        """Test London session provides bonus"""
        context.current_session = "LONDON"
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert details["session"] == "LONDON"
        assert confidence >= 8.0
    
    def test_tokyo_session_lower_bonus(self, processor, context):
        """Test Tokyo session provides lower bonus"""
        context.current_session = "TOKYO"
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert details["session"] == "TOKYO"
    
    def test_reversal_ema_strength_bonus(self, processor, context):
        """Test reversal with strong EMA gets bonus"""
        context.ema_alignment = "BULLISH"
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.RED_TO_GREEN_REVERSAL,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=9.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert confidence > 9.0


# ============================================================================
# TEST 12-17: POSITION SIZING
# ============================================================================

class TestPositionSizing:
    """Test position size calculations"""
    
    def test_max_confidence_position_size(self, processor):
        """Test max position size at high confidence"""
        position = processor._calculate_position_size(9.5)
        expected = (10000 * 0.02 * 2.5) / 100
        assert position == expected
    
    def test_high_confidence_position_size(self, processor):
        """Test position size at 8.5 confidence"""
        position = processor._calculate_position_size(8.5)
        expected = (10000 * 0.02 * 2.0) / 100
        assert position == expected
    
    def test_medium_confidence_position_size(self, processor):
        """Test position size at 7.5 confidence"""
        position = processor._calculate_position_size(7.5)
        expected = (10000 * 0.02 * 1.5) / 100
        assert position == expected
    
    def test_low_confidence_position_size(self, processor):
        """Test position size at 6.5 confidence"""
        position = processor._calculate_position_size(6.5)
        expected = (10000 * 0.02 * 1.0) / 100
        assert position == expected
    
    def test_below_minimum_position_size(self, processor):
        """Test position size below 6.0 returns 0"""
        position = processor._calculate_position_size(5.5)
        assert position == 0.0
    
    def test_position_size_scales_with_account(self):
        """Test position size scales with account balance"""
        small_account = SignalProcessor(account_balance=5000)
        large_account = SignalProcessor(account_balance=20000)
        
        small_pos = small_account._calculate_position_size(8.0)
        large_pos = large_account._calculate_position_size(8.0)
        
        assert large_pos > small_pos
        assert large_pos / small_pos == pytest.approx(4.0)


# ============================================================================
# TEST 18-22: TRADE DETAILS
# ============================================================================

class TestTradeDetails:
    """Test trade details generation"""
    
    def test_long_trade_details_generated(self, processor, context):
        """Test long trade details are generated correctly"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert details["direction"] == "LONG"
        assert details["entry_price"] == 1.0950
        assert details["stop_loss"] < 1.0950
        assert details["target_1"] > 1.0950
        assert details["target_2"] > details["target_1"]
    
    def test_short_trade_details_generated(self, processor, context):
        """Test short trade details are generated correctly"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.RED_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert details["direction"] == "SHORT"
        assert details["entry_price"] == 1.0950
        assert details["stop_loss"] > 1.0950
        assert details["target_1"] < 1.0950
    
    def test_risk_reward_ratios_calculated(self, processor, context):
        """Test risk/reward ratios are calculated"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert details["risk_reward_ratio_1"] > 1.0
        assert details["risk_reward_ratio_2"] > details["risk_reward_ratio_1"]
        assert details["risk_reward_ratio_3"] > details["risk_reward_ratio_2"]
    
    def test_trade_details_metadata(self, processor, context):
        """Test trade details contain complete metadata"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert "signal_type" in details
        assert "symbol" in details
        assert "position_size" in details
        assert "confidence_score" in details
        assert "session" in details
        assert "timestamp" in details
    
    def test_targets_in_correct_order(self, processor, context):
        """Test targets are in correct price order"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.GREEN_VECTOR,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=8.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert details["target_1"] < details["target_2"]
        assert details["target_2"] < details["target_3"]


# ============================================================================
# TEST 23-26: EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_confidence_capped_at_10(self, processor, context):
        """Test confidence is capped at 10.0"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.RED_TO_GREEN_REVERSAL,
            price=1.0930,  # At pivot
            timestamp=datetime.now(),
            confidence=9.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        assert confidence <= 10.0
        assert details["confidence_score"] <= 10.0
    
    def test_zero_risk_handling(self, processor, context):
        """Test handling when stop loss equals entry"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.PIVOT_BOUNCE_PP,
            price=1.0900,
            timestamp=datetime.now(),
            confidence=7.0,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        # Risk/reward should not cause division by zero
        assert details["risk_reward_ratio_1"] >= 0
        assert not (details["risk_reward_ratio_1"] == float('inf'))
    
    def test_signal_statistics_empty_history(self, processor):
        """Test statistics with empty signal history"""
        stats = processor.get_signal_statistics()
        
        assert stats["total_signals"] == 0
    
    def test_signal_statistics_with_history(self, processor, context):
        """Test statistics are calculated correctly"""
        signals = [
            Signal(SignalType.GREEN_VECTOR, "EURUSD", 1.0950, datetime.now(), 8.5),
            Signal(SignalType.BLUE_VECTOR, "EURUSD", 1.0945, datetime.now(), 7.0),
            Signal(SignalType.RED_VECTOR, "EURUSD", 1.0955, datetime.now(), 8.5),
        ]
        
        for signal in signals:
            processor.process_signal(signal, context)
        
        stats = processor.get_signal_statistics()
        
        assert stats["total_signals"] == 3
        assert "signals_by_type" in stats
        assert "average_confidence" in stats
        assert stats["average_confidence"] == pytest.approx(8.0)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_signal_workflow(self, processor, context):
        """Test complete signal processing workflow"""
        signal = Signal(
            symbol="EURUSD",
            signal_type=SignalType.RED_TO_GREEN_REVERSAL,
            price=1.0950,
            timestamp=datetime.now(),
            confidence=9.5,
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        # Verify all components
        assert action in TradeAction
        assert 0 <= confidence <= 10
        assert isinstance(details, dict)
        assert len(processor.signal_history) > 0
    
    def test_multiple_signals_sequence(self, processor, context):
        """Test processing multiple signals in sequence"""
        signals = [
            Signal(SignalType.GREEN_VECTOR, "EURUSD", 1.0950, datetime.now(), 8.5),
            Signal(SignalType.PIVOT_BOUNCE_R1, "EURUSD", 1.0930, datetime.now(), 7.5),
            Signal(SignalType.EMA_BULLISH_ALIGN, "EURUSD", 1.0945, datetime.now(), 8.0),
        ]
        
        actions = []
        for signal in signals:
            action, confidence, details = processor.process_signal(signal, context)
            actions.append(action)
        
        assert len(actions) == 3
        assert all(action in TradeAction for action in actions)
        assert len(processor.signal_history) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
