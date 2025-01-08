"""Type definitions for trading operations."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradeResult:
    """Result of a trading operation."""
    transaction_signature: str
    input_amount: float
    output_amount: float
    price_impact: float
    fee_amount: Optional[float] = None
