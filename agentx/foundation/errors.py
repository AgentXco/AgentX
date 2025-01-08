"""Custom exceptions for the AgentX framework."""

class AgentXError(Exception):
    """Base exception class for all AgentX errors."""
    pass

class TransactionError(AgentXError):
    """Raised when a blockchain transaction fails."""
    pass

class InsufficientFundsError(TransactionError):
    """Raised when an account has insufficient funds for a transaction."""
    pass

class TokenError(AgentXError):
    """Base class for token-related errors."""
    pass

class TokenDeploymentError(TokenError):
    """Raised when token deployment fails."""
    pass

class TokenMetadataError(TokenError):
    """Raised when fetching token metadata fails."""
    pass

class TradingError(AgentXError):
    """Base class for trading-related errors."""
    pass

class QuoteError(TradingError):
    """Raised when fetching a trade quote fails."""
    pass

class SwapError(TradingError):
    """Raised when a swap transaction fails."""
    pass

class PriceError(TradingError):
    """Raised when fetching token price fails."""
    pass

class AccountError(AgentXError):
    """Base class for account-related errors."""
    pass

class AccountNotFoundError(AccountError):
    """Raised when an account is not found."""
    pass

class NetworkError(AgentXError):
    """Base class for network-related errors."""
    pass

class RPCError(NetworkError):
    """Raised when an RPC request fails."""
    pass

class APIError(NetworkError):
    """Raised when an API request fails."""
    pass
