"""
Base client for Solana blockchain interactions.
Provides common functionality for all domain-specific managers.
"""
from typing import Optional
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from ..plugins.event_bus import EventBus

class BaseSolanaClient:
    """Base client class providing common Solana interaction functionality."""
    
    def __init__(self, private_key_base58: str, rpc_url: str):
        """
        Initialize the base Solana client.
        
        Args:
            private_key_base58: Base58 encoded private key
            rpc_url: Solana RPC endpoint URL
        """
        self.connection = AsyncClient(rpc_url)
        self.wallet = Keypair.from_base58_string(private_key_base58)
        self.rpc_url = rpc_url
        self.event_bus = EventBus()
        
    @property
    def public_key(self) -> Pubkey:
        """Get the public key of the wallet."""
        return self.wallet.pubkey()
        
    async def send_transaction(self, transaction: VersionedTransaction) -> str:
        """
        Send a transaction and emit related events.
        
        Args:
            transaction: Transaction to send
            
        Returns:
            str: Transaction signature
        """
        try:
            # Emit pre-transaction event
            self.event_bus.publish(
                "transaction_sending",
                wallet=str(self.public_key),
                timestamp=datetime.now().isoformat()
            )
            
            # Send transaction
            signature = await self.connection.send_transaction(transaction)
            
            # Emit transaction submitted event
            self.event_bus.publish(
                "transaction_submitted",
                signature=signature,
                wallet=str(self.public_key),
                timestamp=datetime.now().isoformat()
            )
            
            # Wait for confirmation
            await self.connection.confirm_transaction(signature)
            
            # Emit confirmation event
            self.event_bus.publish(
                "transaction_confirmed",
                signature=signature,
                wallet=str(self.public_key),
                timestamp=datetime.now().isoformat()
            )
            
            return signature
            
        except Exception as e:
            # Emit transaction failed event
            self.event_bus.publish(
                "transaction_failed",
                error=str(e),
                wallet=str(self.public_key),
                timestamp=datetime.now().isoformat()
            )
            raise
        
    async def close(self):
        """Close the RPC connection."""
        await self.connection.close()
        
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"{self.__class__.__name__}(public_key={self.public_key}, rpc_url={self.rpc_url})"
