"""
Foundation module providing core functionality for Solana blockchain operations.
Exposes domain-specific managers for different blockchain operations.
"""
from typing import Optional

from solders.pubkey import Pubkey  # type: ignore

from .account_ops import AccountOps
from .base_client import BaseSolanaClient
from .token_ops import TokenOps
from .trading_ops import TradingOps
from agentx.constants import DEFAULT_OPTIONS
from agentx.types import PumpfunTokenOptions
from agentx.utils.meteora_dlmm.types import ActivationType


# Re-export BaseSolanaClient as the main client interface
__all__ = ['BaseSolanaClient']
