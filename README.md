# AgentX ⚡️

**AgentX** is a **domain-focused** toolkit for seamless **Solana** blockchain interactions. It provides specialized managers for tasks like **token transfers**, **trading**, **staking**, **NFT operations**, and more. Built with an emphasis on **modularity**, it also integrates with **LangChain** for more powerful, automated workflows.

---

## Overview ✨

AgentX is organized into activity-specific domains—**trading**, **tokens**, **accounts**, **network**, **DeFi**, **NFTs**, etc.—each managed through its own specialized module. This **domain-driven approach** keeps things clean, extensible, and easy to maintain.

### Core Layers

1. **Foundation Layer**  
   - **Configuration Management**: Adjust settings across environments  
   - **Error Handling**: Centralized logic for handling exceptions  
   - **Event System**: Simplified event-driven pattern  
   - **Base Client**: Low-level client for Solana RPC calls

2. **Domain Managers**  
   - **Trading**: Swaps, pricing, liquidity operations  
   - **Tokens**: Deploy SPL tokens, transfers, metadata  
   - **Accounts**: Balance checks, account actions  
   - **Network**: TPS monitoring, faucet management  
   - **DeFi**: Staking, lending, other yield strategies  
   - **NFT**: NFT-specific operations

---

## Plugin Architecture 🔐

AgentX supports a **plugin system**, letting you add new features without changing the core code. Just register your plugin, and it’s ready to use.

---

## Installation & Configuration ⚙️

### Install via `pip`:

```bash
pip install agentx
```

### Or install from source:

```bash
git clone https://github.com/yourusername/agentx.git
cd agentx
pip install -e .
```

### Configuration

Set environment variables or use a `.env` file:

```bash
AGENTX_RPC_URL="https://api.mainnet-beta.solana.com"
AGENTX_COMMITMENT="confirmed"
AGENTX_DEFAULT_SLIPPAGE_BPS="100"
AGENTX_JUP_API_URL="https://price.jup.ag/v4"
AGENTX_DEFAULT_TOKEN_DECIMALS="9"
AGENTX_DEFAULT_TOKEN_SUPPLY="1000000000"
```

Override in code:

```python
from agentx import Client

client = Client(
    private_key="your-base58-private-key",
    config={
        "RPC_URL": "https://api.mainnet-beta.solana.com",
        "DEFAULT_SLIPPAGE_BPS": "100"
    }
)
```

---

## Key Features 🚀

- **🪙 Token Operations**  
  - Transfer SOL or SPL tokens  
  - Deploy new SPL tokens  
  - Stake SOL  
  - Faucet requests  
  - Burn and close token accounts (individually or in batches)

- **💱 Trading**  
  - Integrate with Jupiter Exchange  
  - Customizable slippage  
  - Direct route trading  
  - Buy/sell tokens leveraging Raydium liquidity

- **🏦 DeFi**  
  - Lend assets with Lulo  
  - Stake tokens (like SOL) for rewards

- **🔗 LangChain Integration**  
  - Plug into existing LangChain workflows  
  - Seamless blockchain tools (balances, transfers, etc.)

- **📊 Network & Performance**  
  - Fetch real-time Solana TPS  
  - Monitor network status

- **🟩 NFT**  
  - Mint, update, and manage NFTs (where applicable)

- **🎉 Fun Tokens**  
  - Launch “Pump & Fun” tokens with custom settings

- **💧 Meteora DLMM Pools**  
  - Create and configure Meteora DLMM liquidity pools

---

## Quick Start ⚡️

```python
import asyncio
from agentx import Client
from agentx.activities.trading import TradingManager
from agentx.activities.tokens import TokenManager
from agentx.activities.accounts import AccountManager

async def main():
    # Configure the client
    client = Client(
        private_key="your-base58-private-key",
        config={
            "RPC_URL": "https://api.mainnet-beta.solana.com",
            "DEFAULT_SLIPPAGE_BPS": "100",
        },
    )

    # Create domain managers
    trading = TradingManager(client)
    tokens = TokenManager(client)
    accounts = AccountManager(client)

    # Deploy a token
    new_token = await tokens.deploy_token(decimals=9)
    print(f"Deployed token: {new_token}")

    # Make a trade
    trade_sig = await trading.execute_trade(output_mint="target_token", input_amount=1.0)
    print(f"Trade Signature: {trade_sig}")

    # Check balance
    balance = await accounts.get_balance()
    print(f"Wallet balance: {balance}")

asyncio.run(main())
```

---

## More Examples 📒

### Getting Token Price

```python
import asyncio
from agentx import Client
from agentx.activities.trading import TradingManager

async def main():
    client = Client(private_key="your-base58-private-key")
    trading = TradingManager(client)

    price = await trading.fetch_price("FKMKctiJnbZKL16pCmR7ig6bvjcMJffuUMjB97YD7LJs")
    print(f"Token Price: {price} USDC")

asyncio.run(main())
```

### Swapping Tokens

```python
import asyncio
from agentx import Client
from agentx.activities.trading import TradingManager
from solders.pubkey import Pubkey

async def main():
    client = Client(private_key="your-base58-private-key")
    trading = TradingManager(client)

    # Example of performing a token swap
    signature = await trading.execute_trade(
        output_mint=Pubkey.from_string("target-token-mint"),
        input_amount=100,
        input_mint=Pubkey.from_string("source-token-mint"),
        slippage_bps=300
    )
    print(f"Swap Signature: {signature}")

asyncio.run(main())
```

### Lending

```python
import asyncio
from agentx import Client
from agentx.activities.defi import DeFiManager

async def main():
    client = Client(private_key="your-base58-private-key")
    defi = DeFiManager(client)

    signature = await defi.lend_assets(amount=100)
    print(f"Lending Transaction: {signature}")

asyncio.run(main())
```

### Staking SOL

```python
import asyncio
from agentx import Client
from agentx.activities.defi import DeFiManager

async def main():
    client = Client(private_key="your-base58-private-key")
    defi = DeFiManager(client)

    stake_sig = await defi.stake(amount=1)
    print(f"Staking Signature: {stake_sig}")

asyncio.run(main())
```

### Faucet Request

```python
import asyncio
from agentx import Client
from agentx.activities.network import NetworkManager

async def main():
    client = Client(private_key="your-base58-private-key")
    network = NetworkManager(client)

    response = await network.request_faucet_funds()
    print(f"Faucet Response: {response}")

asyncio.run(main())
```

### Network TPS

```python
import asyncio
from agentx import Client
from agentx.activities.network import NetworkManager

async def main():
    client = Client(private_key="your-base58-private-key")
    network = NetworkManager(client)

    tps = await network.get_tps()
    print(f"Current Solana TPS: {tps}")

asyncio.run(main())
```

### Token Data

```python
import asyncio
from agentx import Client
from agentx.activities.tokens import TokenManager

async def main():
    client = Client(private_key="your-base58-private-key")
    tokens = TokenManager(client)

    sol_info = await tokens.get_token_data_by_ticker("SOL")
    print(f"SOL Info: {sol_info}")

    token_info = await tokens.get_token_data_by_address("example-mint-address")
    print(f"Token Info: {token_info}")

asyncio.run(main())
```

---

## Plugin System 🔐

Easily extend AgentX with custom plugins. Here’s a sample:

```python
from agentx.plugins import Plugin, register_plugin
from agentx.foundation.base_client import BaseSolanaClient

@register_plugin
class MyPlugin(Plugin):
    def __init__(self, client: BaseSolanaClient):
        super().__init__(client)

    async def custom_feature(self, param):
        # Your custom code goes here
        self.emit("custom_event_occurred", {"data": param})
        return "Feature Complete"
```

---

## Domain Managers 🐂

- **TradingManager**: Market operations (swaps, liquidity, prices)  
- **TokenManager**: SPL token creation, transfers, metadata  
- **AccountManager**: Balance checks, account operations  
- **NetworkManager**: TPS readings, faucet usage  
- **DeFiManager**: Yield strategies, lending, staking  
- **NFTManager**: NFT minting and updates (if relevant)

---

## Security Reminder 🔒

Be cautious with private keys. Store them securely, and never commit them to a public repository.

---

## Contributing 🤝

We appreciate contributions! Feel free to open issues, submit pull requests, and help improve AgentX.

---

## License ⚖️

Distributed under the **MIT License**.

