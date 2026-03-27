---
name: evm-defi-dex-swap
dependencies:
  - cobo-agentic-wallet
description: |
  Execute EVM DEX token swaps via Uniswap V3 using Cobo Agentic Wallet (`caw` CLI).
  Supports Ethereum, Base, Arbitrum, Optimism, Polygon mainnet and Sepolia testnet.
  Use when: user wants to swap tokens on a DEX, buy/sell WETH, USDC, ETH, trade token pairs on Uniswap, or mentions "dex swap", "uniswap swap", "swap tokens on EVM/Base/Arbitrum", "trade USDC for ETH", "buy WETH", "sell USDC", "token swap on chain".
  Also triggers for: "exchange tokens", "convert WETH to USDC", "uniswap v3", "swap on mainnet/testnet".
  NOT for: Solana DEX swaps, CEX/centralized exchange trades, cross-chain bridges, or non-Uniswap protocols.
---

# EVM DEX Swap (Uniswap V3)

Swap tokens on-chain via Uniswap V3 `exactInputSingle` using the `caw` CLI.

This skill depends on **cobo-agentic-wallet** for wallet operations. The wallet must be onboarded (`caw onboard` complete) and hold sufficient token balance before executing swaps.

## Chain selection

Match the user's requested chain to the configuration below. If the user doesn't specify a chain, ask which one they want.

| Network | Chain ID | Router | WETH | USDC | Default Fee |
|---------|----------|--------|------|------|-------------|
| Sepolia | `SETH` | `0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E` | `0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14` | `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238` | `3000` |
| Ethereum | `ETH` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | `500` |
| Base | `BASE` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | `0x4200000000000000000000000000000000000006` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | `500` |
| Arbitrum | `ARBITRUM` | `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45` | `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1` | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` | `500` |

**Fee tiers**: `100` (0.01% stable pairs), `500` (0.05% blue-chip), `3000` (0.3% standard), `10000` (1% exotic). Use the fee tier matching the deployed pool — sending to a non-existent pool reverts.

## Workflow

### 1. Pre-flight checks

Before swapping, verify the wallet state:

```bash
# Check balance — confirm the input token is available
caw --format json wallet balance

# If user holds native ETH but needs WETH, wrap it first — see references/weth-wrapping.md
```

If the wallet holds native ETH instead of WETH, read [references/weth-wrapping.md](./references/weth-wrapping.md) for the wrapping procedure before continuing.

### 2. Set variables

Look up the correct values from the chain table above and set them before running any commands:

```bash
WALLET_ADDR="<wallet_addr>"   # from `caw --format json address list`
CHAIN="<chain_id>"            # e.g. ETH, BASE, ARBITRUM, SETH
ROUTER="<router_address>"    # from chain table
TOKEN_IN="<token_in_address>" # e.g. WETH address
TOKEN_OUT="<token_out_address>" # e.g. USDC address
FEE="<fee_tier>"              # e.g. 500
AMOUNT_IN="<amount_in_wei>"   # token amount in smallest unit
AMOUNT_OUT_MIN="<min_out>"    # slippage protection — see notes
```

### 3. Approve token (one-time per token)

The Uniswap Router needs ERC-20 approval to spend the input token. This only needs to happen once per token.

```bash
APPROVE_CALLDATA=$(caw util abi encode \
  --method "approve(address,uint256)" \
  --args "[\"$ROUTER\", \"115792089237316195423570985008687907853269984665640564039457584007913129639935\"]")

caw --format json tx call \
  --contract "$TOKEN_IN" \
  --calldata "$APPROVE_CALLDATA" \
  --chain "$CHAIN" \
  --src-addr "$WALLET_ADDR"
```

### 4. Execute swap

```bash
SWAP_CALLDATA=$(caw util abi encode \
  --method "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))" \
  --args "[\"$TOKEN_IN\", \"$TOKEN_OUT\", \"$FEE\", \"$WALLET_ADDR\", \"$AMOUNT_IN\", \"$AMOUNT_OUT_MIN\", \"0\"]")

caw --format json tx call \
  --contract "$ROUTER" \
  --calldata "$SWAP_CALLDATA" \
  --chain "$CHAIN" \
  --src-addr "$WALLET_ADDR"

# Check transaction status
caw --format json tx get <tx_id>
```

**Example — swap 0.01 WETH → USDC on Ethereum:**

```bash
CHAIN="ETH"
ROUTER="0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
WETH="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# Approve WETH (one-time)
APPROVE=$(caw util abi encode --method "approve(address,uint256)" --args "[\"$ROUTER\", \"115792089237316195423570985008687907853269984665640564039457584007913129639935\"]")
caw --format json tx call --contract "$WETH" --calldata "$APPROVE" --chain "$CHAIN" --src-addr "$WALLET_ADDR"

# Swap 0.01 WETH (10000000000000000 wei) → USDC
# NOTE: amount_out_min is "0" here for demo only — on mainnet with real value, always set a non-zero minimum
SWAP=$(caw util abi encode --method "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))" --args "[\"$WETH\", \"$USDC\", \"500\", \"$WALLET_ADDR\", \"10000000000000000\", \"0\", \"0\"]")
caw --format json tx call --contract "$ROUTER" --calldata "$SWAP" --chain "$CHAIN" --src-addr "$WALLET_ADDR"
```

## Important notes

- **Slippage protection**: On mainnet, set `amount_out_min` to reject unfavorable fills (e.g. `expected_amount * 0.995` for 0.5% slippage). Never use `0` on mainnet for real value.
- **`--format json`**: Use on all `caw` commands for parseable output.
- **Status lifecycle**: `Submitted → PendingScreening → Broadcasting → Confirming → Completed`
- **Gas**: Cobo Gasless sponsors gas by default. On L2 (Arbitrum, Optimism), gas costs are much lower.
- **Error handling**: If a swap is denied by policy, check the `suggestion` field in the error — see the parent skill's [error-handling](../cobo-agentic-wallet/references/error-handling.md).

## Reference

| Topic | Read |
|-------|------|
| WETH wrapping (native ETH → WETH) | [references/weth-wrapping.md](./references/weth-wrapping.md) |
| Complete buy+sell swap cycle script | [references/swap-cycle.md](./references/swap-cycle.md) |
