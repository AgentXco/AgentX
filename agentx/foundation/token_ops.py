"""Token operations manager for Solana blockchain."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import requests
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import CreateAccountParams, create_account
from solders.transaction import Transaction
from spl.token.constants import MINT_LEN, TOKEN_PROGRAM_ID
from spl.token.instructions import initialize_mint

from .base_client import BaseSolanaClient
from .errors import TokenDeploymentError, TokenMetadataError, APIError, TransactionError
from .config import config
from ..types import JupiterTokenData

logger = logging.getLogger(__name__)

class TokenOps(BaseSolanaClient):
    """Manager class for token-related operations."""
    
    async def deploy_token(
        self,
        decimals: int = 9,
        initial_supply: float = 1000
    ) -> Dict[str, str]:
        """
        Deploy a new SPL token.
        
        Args:
            decimals: Number of decimals for the token (default: 9)
            initial_supply: Initial token supply (default: 1000)
            
        Returns:
            Dictionary containing mint address and transaction signature
            
        Raises:
            Exception: If token deployment fails
        """
        try:
            # Generate new mint keypair
            mint = Keypair()
            logger.info(f"Generated mint address: {mint.pubkey()}")
            
            # Emit token deployment started event
            self.event_bus.publish(
                "token_deployment_started",
                mint_address=str(mint.pubkey()),
                decimals=decimals,
                initial_supply=initial_supply,
                timestamp=datetime.now().isoformat()
            )
            
            # Get minimum balance for rent exemption
            lamports = await self.connection.get_minimum_balance_for_rent_exemption(MINT_LEN)
            
            # Create account instruction
            create_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=self.public_key,
                    to_pubkey=mint.pubkey(),
                    lamports=lamports,
                    space=MINT_LEN,
                    program_id=TOKEN_PROGRAM_ID,
                )
            )
            
            # Initialize mint instruction
            initialize_mint_ix = initialize_mint(
                program_id=TOKEN_PROGRAM_ID,
                mint=mint.pubkey(),
                decimals=decimals,
                mint_authority=self.public_key,
                freeze_authority=self.public_key,
            )
            
            # Build and send transaction
            transaction = Transaction()
            transaction.add(create_account_ix, initialize_mint_ix)
            
            signature = await self.send_transaction(transaction)
            
            result = {
                "mint": str(mint.pubkey()),
                "signature": str(signature)
            }
            
            # Emit token deployed event
            self.event_bus.publish(
                "token_deployed",
                result=result,
                timestamp=datetime.now().isoformat()
            )
            
            return result
            
        except Exception as e:
            # Emit token deployment failed event
            self.event_bus.publish(
                "token_deployment_failed",
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
            if isinstance(e, TransactionError):
                raise e
            raise TokenDeploymentError(f"Token deployment failed: {str(e)}")
        
    async def get_token_data(self, mint_address: str) -> Optional[JupiterTokenData]:
        """
        Get token metadata and information from Jupiter API.
        
        Args:
            mint_address: Token mint address to query
            
        Returns:
            JupiterTokenData if found, None otherwise
            
        Raises:
            Exception: If token data fetch fails
        """
        try:
            if not mint_address:
                raise ValueError("Mint address is required")
                
            response = requests.get(
                "https://tokens.jup.ag/tokens?tags=verified",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            for token in data:
                if token.get("address") == mint_address:
                    return JupiterTokenData(
                        address=token.get("address"),
                        symbol=token.get("symbol"),
                        name=token.get("name"),
                    )
            return None
            
        except Exception as e:
            if isinstance(e, requests.RequestException):
                raise APIError(f"API request failed: {str(e)}")
            raise TokenMetadataError(f"Error fetching token data: {str(e)}")
            
    async def get_token_address_from_ticker(self, ticker: str) -> Optional[str]:
        """
        Get token mint address from ticker symbol using DexScreener API.
        
        Args:
            ticker: Token ticker symbol
            
        Returns:
            Token mint address if found, None otherwise
        """
        try:
            response = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={ticker}")
            response.raise_for_status()
            
            data = response.json()
            if not data.get("pairs"):
                return None
                
            solana_pairs = [
                pair for pair in data["pairs"]
                if pair.get("chainId") == "solana"
            ]
            solana_pairs.sort(key=lambda x: x.get("fdv", 0), reverse=True)
            
            solana_pairs = [
                pair for pair in solana_pairs
                if pair.get("baseToken", {}).get("symbol", "").lower() == ticker.lower()
            ]
            
            if solana_pairs:
                return solana_pairs[0].get("baseToken", {}).get("address")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching token address from DexScreener: {str(e)}")
            return None
