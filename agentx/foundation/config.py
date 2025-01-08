"""Configuration management for the AgentX framework."""
import os
from typing import Any, Optional

class Config:
    """Configuration manager for the AgentX framework."""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        if not self._config:
            self._load_env_vars()
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Network configuration
        self._config["LAMPORTS_PER_SOL"] = int(os.getenv("AGENTX_LAMPORTS_PER_SOL", 1_000_000_000))
        self._config["DEFAULT_COMMITMENT"] = os.getenv("AGENTX_DEFAULT_COMMITMENT", "confirmed")
        self._config["RPC_URL"] = os.getenv("AGENTX_RPC_URL", "https://api.mainnet-beta.solana.com")
        
        # Trading configuration
        self._config["DEFAULT_SLIPPAGE_BPS"] = int(os.getenv("AGENTX_DEFAULT_SLIPPAGE_BPS", 300))
        self._config["JUP_API_URL"] = os.getenv("AGENTX_JUP_API_URL", "https://quote-api.jup.ag/v6")
        
        # Token configuration
        self._config["DEFAULT_TOKEN_DECIMALS"] = int(os.getenv("AGENTX_DEFAULT_TOKEN_DECIMALS", 9))
        self._config["DEFAULT_TOKEN_SUPPLY"] = float(os.getenv("AGENTX_DEFAULT_TOKEN_SUPPLY", 1000))
        
        # Common token addresses
        self._config["TOKENS"] = {
            "SOL": os.getenv("AGENTX_SOL_ADDRESS", "So11111111111111111111111111111111111111112"),
            "USDC": os.getenv("AGENTX_USDC_ADDRESS", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
            "USDT": os.getenv("AGENTX_USDT_ADDRESS", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),
            "USDS": os.getenv("AGENTX_USDS_ADDRESS", "USDSwr9ApdHk5bvJKMjzff41FfuX8bSxdKcR81vTwcA"),
            "jitoSOL": os.getenv("AGENTX_JITOSOL_ADDRESS", "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn"),
            "bSOL": os.getenv("AGENTX_BSOL_ADDRESS", "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1"),
            "mSOL": os.getenv("AGENTX_MSOL_ADDRESS", "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So"),
            "BONK": os.getenv("AGENTX_BONK_ADDRESS", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
        }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        instance = cls()
        return instance._config.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        instance = cls()
        instance._config[key] = value
    
    @classmethod
    def reload(cls):
        """Reload configuration from environment variables."""
        instance = cls()
        instance._config.clear()
        instance._load_env_vars()

# Create singleton instance
config = Config()
