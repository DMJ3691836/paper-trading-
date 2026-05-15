#!/usr/bin/env python3
"""
SIGNAL PROCESSOR EXAMPLES & USAGE GUIDE
Complete examples for testing, integrating, and optimizing the signal processor
"""

from datetime import datetime
from bot.signal_processor import (
    SignalProcessor, Signal, SignalType, SignalContext, TradeAction
)
from bot.extended_signals import CustomSignal, ExtendedSignalType
from bot.optimized_confluence import ConfluencePresets


# ============================================================================
# EXAMPLE 1: Basic Signal Processing
# ============================================================================

def example_1_basic_processing():
    """Basic signal processing workflow"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Signal Processing")
    print("="*70)
    
    # Initialize processor
    processor = SignalProcessor(account_balance=10000)
    
    # Create signal context
    context = SignalContext(
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
    
    # Create signal
    signal = Signal(
        symbol="EURUSD",
        signal_type=SignalType.GREEN_VECTOR,
        price=1.0950,
        timestamp=datetime.now(),
        confidence=8.5,
    )
    
    # Process signal
    action, confidence, details = processor.process_signal(signal, context)
    
    # Print results
    print(f"Signal: {signal.signal_type.name}")
    print(f"Action: {action.value}")
    print(f"Final Confidence: {confidence:.2f}/10.0")
    print(f"Position Size: ${details['position_size']:.2f}")
    print(f"Entry: {details['entry_price']:.5f}")
    print(f"Stop Loss: {details['stop_loss']:.5f}")
    print(f"Target 1: {details['target_1']:.5f} (RR: {details['risk_reward_ratio_1']:.2f})")
    print(f"Target 2: {details['target_2']:.5f} (RR: {details['risk_reward_ratio_2']:.2f})")
    print(f"Target 3: {details['target_3']:.5f} (RR: {details['risk_reward_ratio_3']:.2f})")


# ============================================================================
# EXAMPLE 2: Processing Multiple Signal Types
# ============================================================================

def example_2_multiple_signals():
    """Process different signal types with confluence"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Multiple Signal Types with Confluence")
    print("="*70)
    
    processor = SignalProcessor(account_balance=10000)
    
    context = SignalContext(
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
    )
    
    # Different signal types
    signals = [
        Signal(SignalType.GREEN_VECTOR, "EURUSD", 1.0950, datetime.now(), 8.5),
        Signal(SignalType.PIVOT_BOUNCE_R1, "EURUSD", 1.0930, datetime.now(), 7.5),
        Signal(SignalType.EMA_BULLISH_ALIGN, "EURUSD", 1.0945, datetime.now(), 8.0),
        Signal(SignalType.RED_TO_GREEN_REVERSAL, "EURUSD", 1.0935, datetime.now(), 9.5),
    ]
    
    print(f"Processing {len(signals)} signals...\n")
    
    for signal in signals:
        action, confidence, details = processor.process_signal(signal, context)
        print(f"Signal: {signal.signal_type.name:<30} | "
              f"Confidence: {confidence:.2f} | "
              f"Action: {action.value:<15} | "
              f"Position: ${details['position_size']:.2f}")
    
    # Get statistics
    stats = processor.get_signal_statistics()
    print(f"\nTotal Signals Processed: {stats['total_signals']}")
    print(f"Average Confidence: {stats['average_confidence']:.2f}")
    print(f"Signals by Type: {stats['signals_by_type']}")


# ============================================================================
# EXAMPLE 3: Extended Signal Types (Volume, Momentum, Trend)
# ============================================================================

def example_3_extended_signals():
    """Using extended signal types"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Extended Signal Types")
    print("="*70)
    
    # Volume signal
    print("\n1. Volume Signal:")
    volume_signal, vol_conf = CustomSignal.create_volume_signal("BUY", volume_increase=2.5)
    print(f"   Type: {volume_signal.signal_type.name}")
    print(f"   Confidence: {vol_conf:.2f}")
    print(f"   Indicators: {volume_signal.indicators_used}")
    
    # Momentum signal (RSI)
    print("\n2. Momentum Signal (RSI):")
    momentum_signal, mom_conf = CustomSignal.create_momentum_signal(rsi_value=85)
    print(f"   Type: {momentum_signal.signal_type.name}")
    print(f"   Confidence: {mom_conf:.2f}")
    print(f"   RSI Value: {momentum_signal.metadata['indicator_value']}")
    
    # Trend signal (MA Cluster)
    print("\n3. Trend Signal (MA Cluster):")
    trend_signal, trend_conf = CustomSignal.create_trend_signal(
        price=1.0950,
        ma5=1.0945,
        ma13=1.0940,
        ma50=1.0920,
        ma200=1.0880
    )
    print(f"   Type: {trend_signal.signal_type.name}")
    print(f"   Confidence: {trend_conf:.2f}")
    print(f"   Price vs MA5: {trend_signal.metadata['ma5']}")
    
    # MACD signal
    print("\n4. MACD Signal:")
    macd_signal, macd_conf = CustomSignal.create_macd_signal(
        macd_line=0.0050,
        signal_line=0.0030,
        histogram=0.0020
    )
    print(f"   Type: {macd_signal.signal_type.name}")
    print(f"   Confidence: {macd_conf:.2f}")
    print(f"   Histogram: {macd_signal.metadata['histogram']}")
    
    # Fibonacci signal
    print("\n5. Fibonacci Signal:")
    fib_signal, fib_conf = CustomSignal.create_fibonacci_signal(
        price=1.0915,
        swing_high=1.1000,
        swing_low=1.0800,
        direction="retrace"
    )
    if fib_signal:
        print(f"   Type: {fib_signal.signal_type.name}")
        print(f"   Confidence: {fib_conf:.2f}")
        print(f"   Fib Level: {fib_signal.metadata['fib_level']}")
    else:
        print("   No Fibonacci level hit")
    
    # Composite signal
    print("\n6. Composite Signal (Multiple Indicators):")
    composite_signal, comp_conf = CustomSignal.create_composite_signal([
        ("pvsra", 8.5),
        ("volume", 7.5),
        ("momentum", 7.0),
    ])
    print(f"   Type: {composite_signal.signal_type.name}")
    print(f"   Confidence: {comp_conf:.2f}")
    print(f"   Component Signals: {len(composite_signal.indicators_used)}")


# ============================================================================
# EXAMPLE 4: Optimized Confluence System
# ============================================================================

def example_4_confluence_optimization():
    """Using optimized confluence system"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Optimized Confluence System")
    print("="*70)
    
    # Create different preset systems
    presets = {
        "Aggressive": ConfluencePresets.aggressive(),
        "Conservative": ConfluencePresets.conservative(),
        "Balanced": ConfluencePresets.balanced(),
        "Scalping": ConfluencePresets.scalping(),
        "Swing Trading": ConfluencePresets.swing_trading(),
    }
    
    # Define active bonuses for a trade setup
    active_bonuses = [
        "ema_bullish_match",
        "pivot_confluence",
        "london_session",
        "reversal_ema_strength",
    ]
    
    print(f"Active Bonuses: {', '.join(active_bonuses)}\n")
    
    for name, system in presets.items():
        total_bonus = system.calculate_total_bonus(active_bonuses)
        base_confidence = 7.5
        final_confidence = min(base_confidence + total_bonus, 10.0)
        
        print(f"{name:<15} | "
              f"Bonus: +{total_bonus:.2f} | "
              f"Base: {base_confidence:.1f} → "
              f"Final: {final_confidence:.2f}")
    
    # Detailed report
    print("\n" + "-"*70)
    print("Detailed Report (Balanced System):")
    print("-"*70)
    
    balanced = ConfluencePresets.balanced()
    report = balanced.get_active_bonuses_report(active_bonuses)
    
    print(f"Total Active Bonuses: {report['total_bonuses']}")
    print(f"By Category:")
    for category, count in report['by_category'].items():
        print(f"  - {category}: {count}")


# ============================================================================
# EXAMPLE 5: Position Sizing by Confidence
# ============================================================================

def example_5_position_sizing():
    """Position sizing based on confidence levels"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Position Sizing by Confidence")
    print("="*70)
    
    processor = SignalProcessor(account_balance=10000)
    
    confidence_levels = [5.5, 6.5, 7.5, 8.5, 9.0, 9.5, 10.0]
    
    print(f"Account Balance: ${processor.account_balance}")
    print(f"Risk per Trade: {processor.risk_per_trade*100}%\n")
    
    print(f"{'Confidence':<12} | {'Action':<8} | {'Multiplier':<12} | {'Position Size':<15}")
    print("-" * 50)
    
    for conf in confidence_levels:
        position_size = processor._calculate_position_size(conf)
        
        if conf < 6.0:
            action = "SKIP"
        elif conf < 7.0:
            action = "Small"
        elif conf < 8.0:
            action = "Medium"
        elif conf < 9.0:
            action = "Large"
        else:
            action = "Max"
        
        # Calculate multiplier
        for (min_c, max_c), mult in processor.POSITION_SIZE_MULTIPLIERS.items():
            if min_c <= conf <= max_c:
                multiplier = mult
                break
        
        print(f"{conf:<12.1f} | {action:<8} | {multiplier:<12.1f}x | ${position_size:<14.2f}")


# ============================================================================
# EXAMPLE 6: Stop Loss and Target Calculation
# ============================================================================

def example_6_stops_and_targets():
    """Calculate stops and targets for long/short trades"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Stop Loss & Target Calculations")
    print("="*70)
    
    processor = SignalProcessor()
    
    context = SignalContext(
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
    )
    
    # LONG Trade
    print("\nLONG Trade (entry at 1.0950):")
    print("-" * 50)
    entry_long = 1.0950
    stop_long = processor._calculate_long_stop(entry_long, context)
    target1 = processor._calculate_target(entry_long, stop_long, 1.5, is_long=True)
    target2 = processor._calculate_target(entry_long, stop_long, 2.5, is_long=True)
    target3 = processor._calculate_target(entry_long, stop_long, 3.5, is_long=True)
    
    risk = abs(entry_long - stop_long)
    print(f"Entry:       {entry_long:.5f}")
    print(f"Stop Loss:   {stop_long:.5f}")
    print(f"Risk:        {risk*10000:.0f} pips")
    print(f"\nTargets:")
    print(f"  Target 1:  {target1:.5f} (RR: 1.5:1, {abs(target1-entry_long)*10000:.0f} pips)")
    print(f"  Target 2:  {target2:.5f} (RR: 2.5:1, {abs(target2-entry_long)*10000:.0f} pips)")
    print(f"  Target 3:  {target3:.5f} (RR: 3.5:1, {abs(target3-entry_long)*10000:.0f} pips)")
    
    # SHORT Trade
    print("\n\nSHORT Trade (entry at 1.0950):")
    print("-" * 50)
    entry_short = 1.0950
    stop_short = processor._calculate_short_stop(entry_short, context)
    target1 = processor._calculate_target(entry_short, stop_short, 1.5, is_long=False)
    target2 = processor._calculate_target(entry_short, stop_short, 2.5, is_long=False)
    target3 = processor._calculate_target(entry_short, stop_short, 3.5, is_long=False)
    
    risk = abs(entry_short - stop_short)
    print(f"Entry:       {entry_short:.5f}")
    print(f"Stop Loss:   {stop_short:.5f}")
    print(f"Risk:        {risk*10000:.0f} pips")
    print(f"\nTargets:")
    print(f"  Target 1:  {target1:.5f} (RR: 1.5:1, {abs(target1-entry_short)*10000:.0f} pips)")
    print(f"  Target 2:  {target2:.5f} (RR: 2.5:1, {abs(target2-entry_short)*10000:.0f} pips)")
    print(f"  Target 3:  {target3:.5f} (RR: 3.5:1, {abs(target3-entry_short)*10000:.0f} pips)")


# ============================================================================
# EXAMPLE 7: Trading Strategy Simulation
# ============================================================================

def example_7_strategy_simulation():
    """Simulate a complete trading strategy"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Strategy Simulation")
    print("="*70)
    
    processor = SignalProcessor(account_balance=10000)
    confluence_system = ConfluencePresets.balanced()
    
    # Trading context for LONDON session
    context = SignalContext(
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
    )
    
    # Signal sequence
    signals = [
        ("GREEN_VECTOR", 1.0950),
        ("PIVOT_BOUNCE_R1", 1.0930),
        ("EMA_BULLISH_ALIGN", 1.0945),
    ]
    
    total_trades = 0
    total_risk_pips = 0
    avg_rr = 0
    
    print(f"\nTrading Setup Analysis:")
    print(f"Session: {context.current_session}")
    print(f"EMA Alignment: {context.ema_alignment}\n")
    
    for sig_name, price in signals:
        signal_type = getattr(SignalType, sig_name)
        signal = Signal(
            symbol="EURUSD",
            signal_type=signal_type,
            price=price,
            timestamp=datetime.now(),
            confidence=signal_type.value[1],
        )
        
        action, confidence, details = processor.process_signal(signal, context)
        
        if action != TradeAction.SKIP:
            total_trades += 1
            total_risk_pips += details["risk_pips"]
            avg_rr += details["risk_reward_ratio_1"]
            
            print(f"Signal: {sig_name}")
            print(f"  → Action: {action.value} (Confidence: {confidence:.2f})")
            print(f"  → Entry: {details['entry_price']:.5f} | "
                  f"Stop: {details['stop_loss']:.5f} | "
                  f"Target: {details['target_1']:.5f}")
            print(f"  → Risk: {details['risk_pips']:.0f} pips | "
                  f"RR Ratio: {details['risk_reward_ratio_1']:.2f}:1")
            print()
    
    print("-" * 70)
    print(f"Summary:")
    print(f"  Valid Trade Setups: {total_trades}")
    if total_trades > 0:
        print(f"  Average Risk: {total_risk_pips/total_trades:.0f} pips")
        print(f"  Average R/R: {avg_rr/total_trades:.2f}:1")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("SIGNAL PROCESSOR - COMPREHENSIVE EXAMPLES")
    print("="*70)
    
    example_1_basic_processing()
    example_2_multiple_signals()
    example_3_extended_signals()
    example_4_confluence_optimization()
    example_5_position_sizing()
    example_6_stops_and_targets()
    example_7_strategy_simulation()
    
    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
