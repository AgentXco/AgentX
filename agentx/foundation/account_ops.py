"""Account operations manager for Solana blockchain."""
import logging
import math
from typing import Optional, List, Dict, Any
from datetime import datetime

from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address, transfer_checked

from .base_client import BaseSolanaClient
from .errors import AccountNotFoundError, InsufficientFundsError, TransactionError, AccountError
from .config import config
from ..types import TransferResult

logger = logging.getLogger(__name__)

class AccountOps(BaseSolanaClient):
    """Manager class for account-related operations."""
    
    async def get_balance(self, mint: Optional[str] = None) -> float:
        """
        Get the balance of SOL or an SPL token.
        
        Args:
            mint: Optional SPL token mint address. If not provided, returns SOL balance.
            
        Returns:
            Balance as a float in UI units
            
        Raises:
            Exception: If the balance check fails
        """
        try:
            # Emit balance check started event
            self.event_bus.publish(
                "balance_check_started",
                mint=str(mint) if mint else "SOL",
                timestamp=datetime.now().isoformat()
            )
            
            if not mint:
                response = await self.connection.get_balance(
                    self.public_key,
                    commitment=Confirmed
                )
                balance = response.value / config.get("LAMPORTS_PER_SOL")
            else:
                response = await self.connection.get_token_account_balance(
                    Pubkey.from_string(mint),
                    commitment=Confirmed
                )
                if response.value is None:
                    balance = 0.0
                else:
                    balance = float(response.value.ui_amount or 0)
                    
            # Emit balance check completed event
            self.event_bus.publish(
                "balance_check_completed",
                mint=str(mint) if mint else "SOL",
                balance=balance,
                timestamp=datetime.now().isoformat()
            )
            
            return balance
            
        except Exception as e:
            # Emit balance check failed event
            self.event_bus.publish(
                "balance_check_failed",
                mint=str(mint) if mint else "SOL",
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
            if "Account not found" in str(e):
                raise AccountNotFoundError(f"Account not found: {str(e)}")
            raise TransactionError(f"Failed to get balance: {str(e)}")
            
    async def transfer(
        self,
        destination: str,
        amount: float,
        mint: Optional[str] = None
    ) -> TransferResult:
        """
        Transfer SOL or SPL tokens to another address.
        
        Args:
            destination: Recipient's public key
            amount: Amount to transfer
            mint: Optional token mint address (None for SOL transfers)
            
        Returns:
            TransferResult containing transfer details
            
        Raises:
            Exception: If the transfer fails
        """
        try:
            # Convert addresses to Pubkey objects
            dest_pubkey = Pubkey.from_string(destination)
            mint_pubkey = Pubkey.from_string(mint) if mint else None
            
            # Emit transfer started event
            self.event_bus.publish(
                "transfer_started",
                destination=destination,
                amount=amount,
                mint=str(mint) if mint else "SOL",
                timestamp=datetime.now().isoformat()
            )
            
            if mint_pubkey:
                # SPL token transfer
                spl_client = AsyncToken(
                    self.connection,
                    mint_pubkey,
                    TOKEN_PROGRAM_ID,
                    self.wallet
                )
                
                # Get token info
                mint_info = await spl_client.get_mint_info()
                token_decimals = mint_info.decimals
                tokens = math.floor(amount * (10 ** token_decimals))
                
                # Get associated token accounts
                source_ata = get_associated_token_address(self.public_key, mint_pubkey)
                dest_ata = get_associated_token_address(dest_pubkey, mint_pubkey)
                
                # Build transfer instruction
                transfer_ix = transfer_checked(
                    amount=tokens,
                    decimals=token_decimals,
                    program_id=TOKEN_PROGRAM_ID,
                    owner=self.public_key,
                    source=source_ata,
                    dest=dest_ata,
                    mint=mint_pubkey,
                )
                
                # Build and send transaction
                transaction = Transaction().add(transfer_ix)
                signature = await self.send_transaction(transaction)
                
            else:
                # Native SOL transfer
                transaction = Transaction().add(
                    Transaction(
                        from_pubkey=self.public_key,
                        to_pubkey=dest_pubkey,
                        lamports=int(amount * config.get("LAMPORTS_PER_SOL"))
                    )
                )
                signature = await self.send_transaction(transaction)
                
            # Create transfer result
            result = TransferResult(
                signature=str(signature),
                from_address=str(self.public_key),
                to_address=destination,
                amount=amount,
                token=str(mint) if mint else "SOL"
            )
            
            # Emit transfer completed event
            self.event_bus.publish(
                "transfer_completed",
                result=result.__dict__,
                timestamp=datetime.now().isoformat()
            )
            
            return result
            
        except Exception as e:
            # Emit transfer failed event
            self.event_bus.publish(
                "transfer_failed",
                destination=destination,
                amount=amount,
                mint=str(mint) if mint else "SOL",
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
            if "insufficient funds" in str(e).lower():
                raise InsufficientFundsError(f"Insufficient funds for transfer: {str(e)}")
            if "Account not found" in str(e):
                raise AccountNotFoundError(f"Account not found: {str(e)}")
            raise TransactionError(f"Transfer failed: {str(e)}")
            
    async def burn_and_close_account(self, mint: str) -> str:
        """
        Burn tokens and close the token account.
        
        Args:
            mint: Token mint address
            
        Returns:
            Transaction signature
            
        Raises:
            AccountError: If burn/close operation fails
        """
        try:
            # Convert mint to Pubkey
            mint_pubkey = Pubkey.from_string(mint)
            
            # Create SPL token client
            spl_client = AsyncToken(
                self.connection,
                mint_pubkey,
                TOKEN_PROGRAM_ID,
                self.wallet
            )
            
            # Get associated token account
            token_account = get_associated_token_address(
                self.public_key,
                mint_pubkey
            )
            
            # Build burn instruction
            burn_ix = spl_client.burn(
                source=token_account,
                mint=mint_pubkey,
                owner=self.public_key,
                amount=0,  # Burning 0 tokens is sufficient for closing
                multi_signers=None
            )
            
            # Build close instruction
            close_ix = spl_client.close_account(
                account=token_account,
                dest=self.public_key,
                owner=self.public_key,
                multi_signers=None
            )
            
            # Build and send transaction
            transaction = Transaction().add(burn_ix).add(close_ix)
            signature = await self.send_transaction(transaction)
            
            return str(signature)
            
        except Exception as e:
            raise AccountError(f"Failed to burn and close account: {str(e)}")
        
    async def burn_and_close_multiple(self, mints: List[str]) -> List[str]:
        """
        Burn tokens and close multiple token accounts.
        
        Args:
            mints: List of token mint addresses
            
        Returns:
            List of transaction signatures
            
        Raises:
            Exception: If any burn/close operation fails
        """
        signatures = []
        for mint in mints:
            signature = await self.burn_and_close_account(mint)
            signatures.append(signature)
        return signatures
