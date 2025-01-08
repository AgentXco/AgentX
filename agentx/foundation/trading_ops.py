"""Trading operations manager for Solana blockchain."""
import base64
from typing import Optional, Dict, Any
from datetime import datetime

import aiohttp
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from .base_client import BaseSolanaClient
from .errors import QuoteError, SwapError, PriceError, APIError, TransactionError
from .config import config
from ..types.trade_result import TradeResult

class TradingOps(BaseSolanaClient):
    """Manager class for trading-related operations."""
    
    async def execute_trade(
        self,
        output_mint: str,
        input_amount: float,
        input_mint: Optional[str] = None,
        slippage_bps: Optional[int] = None
    ) -> TradeResult:
        """
        Execute a trade between tokens using Jupiter Exchange.
        
        Args:
            output_mint: Target token mint address
            input_amount: Amount to swap (in token decimals)
            input_mint: Source token mint address (default: USDC)
            slippage_bps: Slippage tolerance in basis points (default: 300 = 3%)
            
        Returns:
            TradeResult containing transaction details
            
        Raises:
            Exception: If the swap fails
        """
        try:
            # Emit pre-trade event
            self.event_bus.publish(
                "trade_initiated",
                input_mint=str(input_mint or config.get("TOKENS")["USDC"]),
                output_mint=str(output_mint),
                input_amount=input_amount,
                timestamp=datetime.now().isoformat()
            )
            
            # Build quote URL
            quote_url = (
                f"{config.get('JUP_API_URL')}/quote?"
                f"inputMint={input_mint or config.get('TOKENS')['USDC']}"
                f"&outputMint={output_mint}"
                f"&amount={int(input_amount * config.get('LAMPORTS_PER_SOL'))}"
                f"&slippageBps={slippage_bps or config.get('DEFAULT_SLIPPAGE_BPS')}"
                f"&onlyDirectRoutes=true"
                f"&maxAccounts=20"
            )

            async with aiohttp.ClientSession() as session:
                # Get quote
                async with session.get(quote_url) as quote_response:
                    if quote_response.status != 200:
                        raise QuoteError(f"Failed to fetch quote: {quote_response.status}")
                    quote_data = await quote_response.json()
                    
                    # Emit quote received event
                    self.event_bus.publish(
                        "trade_quote_received",
                        quote_data=quote_data,
                        timestamp=datetime.now().isoformat()
                    )

                # Get swap transaction
                async with session.post(
                    f"{config.get('JUP_API_URL')}/swap",
                    json={
                        "quoteResponse": quote_data,
                        "userPublicKey": str(self.public_key),
                        "wrapAndUnwrapSol": True,
                        "dynamicComputeUnitLimit": True,
                        "prioritizationFeeLamports": "auto",
                    },
                ) as swap_response:
                    if swap_response.status != 200:
                        raise SwapError(f"Failed to fetch swap transaction: {swap_response.status}")
                    swap_data = await swap_response.json()

            # Deserialize and sign transaction
            swap_transaction_buf = base64.b64decode(swap_data["swapTransaction"])
            transaction = VersionedTransaction.deserialize(swap_transaction_buf)

            latest_blockhash = await self.connection.get_latest_blockhash()
            transaction.message.recent_blockhash = latest_blockhash.value.blockhash
            transaction.sign([self.wallet])

            # Send transaction
            signature = await self.send_transaction(transaction)
            
            # Create trade result
            result = TradeResult(
                transaction_signature=str(signature),
                input_amount=input_amount,
                output_amount=float(quote_data["outAmount"]) / config.get("LAMPORTS_PER_SOL"),
                price_impact=float(quote_data.get("priceImpactPct", 0))
            )
            
            # Emit trade completed event
            self.event_bus.publish(
                "trade_completed",
                result=result.__dict__,
                timestamp=datetime.now().isoformat()
            )
            
            return result

        except Exception as e:
            # Emit trade failed event
            self.event_bus.publish(
                "trade_failed",
                error=str(e),
                input_mint=str(input_mint or config.get("TOKENS")["USDC"]),
                output_mint=str(output_mint),
                input_amount=input_amount,
                timestamp=datetime.now().isoformat()
            )
            raise
            
    async def get_token_price(self, mint_address: str) -> float:
        """
        Get the current price of a token in USDC.
        
        Args:
            mint_address: Token mint address to get price for
            
        Returns:
            float: Token price in USDC
            
        Raises:
            Exception: If price fetch fails
        """
        url = f"https://api.jup.ag/price/v2?ids={mint_address}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise APIError(f"Failed to fetch price: {response.status}")

                    data = await response.json()
                    price = data.get("data", {}).get(mint_address, {}).get("price")

                    if not price:
                        raise PriceError("Price data not available for the given token.")

                    return float(price)
                    
        except Exception as e:
            raise Exception(f"Price fetch failed: {str(e)}")
