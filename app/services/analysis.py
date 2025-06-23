import numpy as np
import pandas as pd
import logging
from flask import current_app as app
from app.api.iqoption import iq_api

logger = logging.getLogger(__name__)

def analyze_asset(asset, timeframe=60):
    """
    Analyze an asset using multiple technical indicators
    
    Returns:
        dict: Analysis results with entry signals
    """
    try:
        # Get candles data
        candles = iq_api.get_candles(asset, timeframe, 100)
        if not candles:
            logger.error(f"Failed to get candles for {asset}")
            return None
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(candles)
        
        # Calculate indicators
        signals = {}
        
        # RSI
        signals['rsi'] = calculate_rsi(df)
        
        # MACD
        signals['macd'] = calculate_macd(df)
        
        # Volume analysis
        signals['volume'] = analyze_volume(df)
        
        # Candlestick patterns
        signals['patterns'] = detect_candlestick_patterns(df)
        
        # Determine overall signal
        signals['overall'] = determine_overall_signal(signals)
        
        return signals
        
    except Exception as e:
        logger.error(f"Error analyzing {asset}: {str(e)}")
        return None

def calculate_rsi(df, period=None):
    """
    Calculate RSI (Relative Strength Index)
    """
    period = period or app.config['RSI_PERIOD']
    overbought = app.config['RSI_OVERBOUGHT']
    oversold = app.config['RSI_OVERSOLD']
    
    # Calculate price changes
    delta = df['close'].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Get the latest RSI value
    latest_rsi = rsi.iloc[-1]
    
    # Determine signal
    if latest_rsi < oversold:
        signal = 'CALL'  # Oversold, potential buy
    elif latest_rsi > overbought:
        signal = 'PUT'   # Overbought, potential sell
    else:
        signal = 'NEUTRAL'
        
    return {
        'value': latest_rsi,
        'signal': signal,
        'overbought': latest_rsi > overbought,
        'oversold': latest_rsi < oversold
    }

def calculate_macd(df):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    """
    fast = app.config['MACD_FAST']
    slow = app.config['MACD_SLOW']
    signal_period = app.config['MACD_SIGNAL']
    
    # Calculate EMAs
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    
    # Calculate MACD line and signal line
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    # Get latest values
    latest_macd = macd_line.iloc[-1]
    latest_signal = signal_line.iloc[-1]
    latest_histogram = histogram.iloc[-1]
    prev_histogram = histogram.iloc[-2] if len(histogram) > 1 else 0
    
    # Determine signal
    if latest_macd > latest_signal and latest_histogram > 0 and latest_histogram > prev_histogram:
        signal = 'CALL'  # Bullish
    elif latest_macd < latest_signal and latest_histogram < 0 and latest_histogram < prev_histogram:
        signal = 'PUT'   # Bearish
    else:
        signal = 'NEUTRAL'
        
    return {
        'macd': latest_macd,
        'signal': signal,
        'histogram': latest_histogram,
        'crossover': latest_macd > latest_signal
    }

def analyze_volume(df):
    """
    Analyze volume patterns
    """
    # Calculate average volume
    avg_volume = df['volume'].rolling(window=10).mean()
    latest_volume = df['volume'].iloc[-1]
    
    # Volume ratio
    volume_ratio = latest_volume / avg_volume.iloc[-1] if not pd.isna(avg_volume.iloc[-1]) else 1
    
    # Price change
    price_change = df['close'].iloc[-1] - df['open'].iloc[-1]
    
    # Determine signal based on volume and price
    if volume_ratio > 1.5 and price_change > 0:
        signal = 'CALL'  # High volume + price increase = bullish
    elif volume_ratio > 1.5 and price_change < 0:
        signal = 'PUT'   # High volume + price decrease = bearish
    else:
        signal = 'NEUTRAL'
        
    return {
        'volume': latest_volume,
        'avg_volume': avg_volume.iloc[-1] if not pd.isna(avg_volume.iloc[-1]) else 0,
        'volume_ratio': volume_ratio,
        'signal': signal
    }

def detect_candlestick_patterns(df):
    """
    Detect common candlestick patterns
    """
    patterns = {}
    
    # Get the last few candles
    last_candles = df.iloc[-3:].copy()
    
    # Calculate candle properties
    last_candles['body_size'] = abs(last_candles['close'] - last_candles['open'])
    last_candles['upper_shadow'] = last_candles.apply(
        lambda x: x['high'] - max(x['open'], x['close']), axis=1
    )
    last_candles['lower_shadow'] = last_candles.apply(
        lambda x: min(x['open'], x['close']) - x['low'], axis=1
    )
    last_candles['is_bullish'] = last_candles['close'] > last_candles['open']
    
    # Latest candle
    latest = last_candles.iloc[-1]
    
    # Doji pattern (small body, shadows on both sides)
    body_to_range_ratio = latest['body_size'] / (latest['high'] - latest['low']) if (latest['high'] - latest['low']) > 0 else 0
    patterns['doji'] = body_to_range_ratio < 0.1
    
    # Hammer/Hanging Man (small body, long lower shadow, small upper shadow)
    lower_shadow_ratio = latest['lower_shadow'] / latest['body_size'] if latest['body_size'] > 0 else 0
    upper_shadow_ratio = latest['upper_shadow'] / latest['body_size'] if latest['body_size'] > 0 else 0
    patterns['hammer'] = (lower_shadow_ratio > 2) and (upper_shadow_ratio < 0.5)
    
    # Engulfing pattern (current candle engulfs previous candle)
    if len(last_candles) >= 2:
        prev = last_candles.iloc[-2]
        patterns['bullish_engulfing'] = (
            latest['is_bullish'] and 
            not prev['is_bullish'] and
            latest['open'] < prev['close'] and
            latest['close'] > prev['open']
        )
        patterns['bearish_engulfing'] = (
            not latest['is_bullish'] and 
            prev['is_bullish'] and
            latest['open'] > prev['close'] and
            latest['close'] < prev['open']
        )
    
    # Determine overall pattern signal
    signal = 'NEUTRAL'
    if patterns.get('bullish_engulfing', False) or (patterns.get('hammer', False) and latest['is_bullish']):
        signal = 'CALL'
    elif patterns.get('bearish_engulfing', False) or (patterns.get('hammer', False) and not latest['is_bullish']):
        signal = 'PUT'
    
    patterns['signal'] = signal
    return patterns

def determine_overall_signal(signals):
    """
    Determine overall trading signal based on all indicators
    """
    # Count signals
    call_count = sum(1 for k, v in signals.items() if isinstance(v, dict) and v.get('signal') == 'CALL')
    put_count = sum(1 for k, v in signals.items() if isinstance(v, dict) and v.get('signal') == 'PUT')
    
    # Determine strength (0-100%)
    total_indicators = len(signals) - 1  # Exclude 'overall'
    
    if call_count > put_count:
        signal = 'CALL'
        strength = (call_count / total_indicators) * 100
    elif put_count > call_count:
        signal = 'PUT'
        strength = (put_count / total_indicators) * 100
    else:
        signal = 'NEUTRAL'
        strength = 0
        
    return {
        'signal': signal,
        'strength': strength,
        'call_count': call_count,
        'put_count': put_count
    }