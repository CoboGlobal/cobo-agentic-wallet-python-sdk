# Complete Swap Cycle (Buy + Sell)

A full round-trip: approve WETH → swap WETH→USDC → approve USDC → swap USDC→WETH.

Adapt the variables for your target chain using the chain table in SKILL.md.

```bash
#!/bin/bash
# dex_swap_cycle.sh — Complete DEX swap round-trip

set -e

WALLET_UUID="<wallet_uuid>"
WALLET_ADDR="<wallet_addr>"
CHAIN="ETH"
ROUTER="0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
WETH="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
FEE="500"

approve() {
  local TOKEN=$1
  local CALLDATA=$(caw util abi encode \
    --method "approve(address,uint256)" \
    --args "[\"$ROUTER\", \"115792089237316195423570985008687907853269984665640564039457584007913129639935\"]")
  caw --format json tx call \
    --contract "$TOKEN" \
    --calldata "$CALLDATA" \
    --chain "$CHAIN" \
    --src-addr "$WALLET_ADDR"
}

swap() {
  local TOKEN_IN=$1 TOKEN_OUT=$2 AMOUNT_IN=$3 MIN_OUT=${4:-0}
  local CALLDATA=$(caw util abi encode \
    --method "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))" \
    --args "[\"$TOKEN_IN\", \"$TOKEN_OUT\", \"$FEE\", \"$WALLET_ADDR\", \"$AMOUNT_IN\", \"$MIN_OUT\", \"0\"]")
  caw --format json tx call \
    --contract "$ROUTER" \
    --calldata "$CALLDATA" \
    --chain "$CHAIN" \
    --src-addr "$WALLET_ADDR"
}

echo "=== DEX Swap Cycle ==="

echo "[1/4] Approving WETH..."
approve "$WETH"
sleep 30

echo "[2/4] Swapping 0.01 WETH → USDC..."
swap "$WETH" "$USDC" "10000000000000000"
sleep 30

echo "[3/4] Approving USDC..."
approve "$USDC"
sleep 30

echo "[4/4] Swapping 15 USDC → WETH..."
swap "$USDC" "$WETH" "15000000"  # 15 USDC (6 decimals)

echo "DEX swap cycle complete."
```

## Notes

- Adjust `sleep 30` based on the chain's confirmation time (L2 chains are faster).
- Set `MIN_OUT` to a non-zero value on mainnet for slippage protection.
- Each `approve()` only needs to run once per token — subsequent swaps can skip it.
