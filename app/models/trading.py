from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class Candle:
    """
    Represents a price candle
    """
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: int
    
    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish (close > open)"""
        return self.close > self.open
    
    @property
    def is_bearish(self) -> bool:
        """Check if candle is bearish (close < open)"""
        return self.close < self.open
    
    @property
    def body_size(self) -> float:
        """Get the size of the candle body"""
        return abs(self.close - self.open)
    
    @property
    def upper_shadow(self) -> float:
        """Get the size of the upper shadow"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_shadow(self) -> float:
        """Get the size of the lower shadow"""
        return min(self.open, self.close) - self.low
    
    @property
    def range(self) -> float:
        """Get the total range of the candle"""
        return self.high - self.low

@dataclass
class Trade:
    """
    Represents a binary options trade
    """
    asset: str
    amount: float
    direction: str  # 'CALL' or 'PUT'
    expiration: int  # in minutes
    timestamp: datetime = field(default_factory=datetime.now)
    order_id: Optional[str] = None
    status: str = 'pending'  # 'pending', 'open', 'closed'
    result: Optional[str] = None  # 'WIN', 'LOSS', None if pending
    profit_loss: Optional[float] = None
    
    @property
    def is_win(self) -> bool:
        """Check if trade is a win"""
        return self.result == 'WIN'
    
    @property
    def is_loss(self) -> bool:
        """Check if trade is a loss"""
        return self.result == 'LOSS'
    
    @property
    def is_pending(self) -> bool:
        """Check if trade is pending"""
        return self.result is None

@dataclass
class TradingSession:
    """
    Represents a trading session
    """
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    initial_balance: float = 0
    final_balance: Optional[float] = None
    trades: List[Trade] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    
    @property
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.end_time is None
    
    @property
    def profit_loss(self) -> Optional[float]:
        """Calculate profit/loss for the session"""
        if self.final_balance is not None and self.initial_balance > 0:
            return self.final_balance - self.initial_balance
        return None
    
    @property
    def profit_loss_percentage(self) -> Optional[float]:
        """Calculate profit/loss percentage for the session"""
        if self.profit_loss is not None and self.initial_balance > 0:
            return (self.profit_loss / self.initial_balance) * 100
        return None
    
    @property
    def win_count(self) -> int:
        """Count winning trades"""
        return sum(1 for trade in self.trades if trade.is_win)
    
    @property
    def loss_count(self) -> int:
        """Count losing trades"""
        return sum(1 for trade in self.trades if trade.is_loss)
    
    @property
    def win_rate(self) -> Optional[float]:
        """Calculate win rate"""
        total = self.win_count + self.loss_count
        if total > 0:
            return (self.win_count / total) * 100
        return None
    
    def end_session(self, final_balance: float) -> None:
        """End the trading session"""
        self.end_time = datetime.now()
        self.final_balance = final_balance

@dataclass
class TechnicalAnalysis:
    """
    Represents technical analysis results
    """
    asset: str
    timestamp: datetime = field(default_factory=datetime.now)
    indicators: Dict[str, Any] = field(default_factory=dict)
    signal: str = 'NEUTRAL'  # 'CALL', 'PUT', or 'NEUTRAL'
    strength: float = 0  # 0-100%
    
    @property
    def is_strong_signal(self) -> bool:
        """Check if signal is strong (>70%)"""
        return self.signal != 'NEUTRAL' and self.strength > 70