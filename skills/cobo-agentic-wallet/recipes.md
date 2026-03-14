# Recipes

Common usage scenarios and workflows. Each recipe below covers a specific operation. For detailed, multi-step scenarios see the linked files.

## Transfer tokens

```bash
caw --format json tx transfer <wallet_uuid> \
  --to 0x1234...abcd --token USDC --amount 10 --chain BASE \
  --request-id pay-invoice-1001
```

## Check wallet balance

```bash
caw --format json wallet balance <wallet_uuid>
```

## List recent transactions

```bash
caw --format json tx list <wallet_uuid> --limit 20
```

## Estimate fee before transfer

```bash
caw --format json tx estimate-transfer-fee <wallet_uuid> \
  --to 0x1234...abcd --token USDC --amount 10 --chain BASE
```

## Contract call

```bash
caw --format json tx call <wallet_uuid> \
  --contract 0xContractAddr --calldata 0x... --chain ETH
```

## Handle policy denial

When denied, check the `suggestion` field and retry with adjusted parameters.

## Monitor pending approvals

When a transaction returns HTTP 202, poll with `caw pending get <operation_id>`.

## Detailed Scenarios

- [Policy Management](./recipes/policy-management.md) — Create, test, and troubleshoot policies
- [Error Handling](./recipes/error-handling.md) — Common errors, policy denials, and recovery patterns
- [EVM DeFi — Aave V3](./recipes/evm-defi-aave.md) — Supply collateral, borrow, repay, and withdraw on Aave V3 (Sepolia)
- [EVM DeFi — DEX Swap](./recipes/evm-defi-dex-swap.md) — Token swap via Uniswap V3 `exactInputSingle` on EVM
- [EVM DeFi — DCA](./recipes/evm-defi-dca.md) — Repeated fixed-size swaps at timed intervals on EVM
- [EVM DeFi — Grid Trading](./recipes/evm-defi-grid-trading.md) — Buy/sell ladder at preset price levels on EVM
- [Solana DeFi — DEX Swap](./recipes/solana-defi-dex-swap.md) — Token swap on Solana via Jupiter V6 (mainnet) or Memo+Transfer simulation (devnet)
- [Solana DeFi — DCA](./recipes/solana-defi-dca.md) — Repeated fixed-size purchases at timed intervals on Solana
- [Solana DeFi — Grid Trading](./recipes/solana-defi-grid-trading.md) — Buy/sell ladder at preset price levels on Solana
- [Solana DeFi — Prediction Market](./recipes/solana-defi-prediction-market.md) — Long/Short stake positions on Solana

