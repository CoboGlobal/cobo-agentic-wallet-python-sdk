# WETH Wrapping

If the wallet holds native ETH but the swap needs WETH, wrap it first.

## Procedure

```bash
WALLET_UUID="<wallet_uuid>"
WALLET_ADDR="<wallet_addr>"
WETH="<weth_address>"     # see chain table in SKILL.md
ROUTER="<router_address>" # see chain table in SKILL.md
CHAIN="<chain_id>"

WRAP_AMOUNT="0.01"  # amount of ETH to wrap — adjust to the user's needs

# Step 1: deposit() — wrap ETH → WETH (selector 0xd0e30db0, no arguments)
DEPOSIT_RESULT=$(caw --format json tx call \
  --contract "$WETH" \
  --calldata 0xd0e30db0 \
  --value "$WRAP_AMOUNT" \
  --chain "$CHAIN" \
  --src-addr "$WALLET_ADDR")

DEPOSIT_TX_ID=$(echo "$DEPOSIT_RESULT" | jq -r '.result.id // .id')

# Step 2: Wait for confirmation before approving
echo "Waiting for deposit to confirm..."
while true; do
  STATUS=$(caw --format json tx get "$DEPOSIT_TX_ID" 2>/dev/null \
    | jq -r '.result.status // .status // ""' 2>/dev/null)
  [ "$STATUS" = "Completed" ] && break
  [ "$STATUS" = "Failed" ]    && { echo "Deposit failed, aborting"; exit 1; }
  sleep 5
done

# Step 3: Approve router to spend WETH (one-time)
APPROVE=$(caw util abi encode \
  --method "approve(address,uint256)" \
  --args "[\"$ROUTER\", \"115792089237316195423570985008687907853269984665640564039457584007913129639935\"]")

caw --format json tx call \
  --contract "$WETH" \
  --calldata "$APPROVE" \
  --chain "$CHAIN" \
  --src-addr "$WALLET_ADDR"
```

## WETH contract addresses

| Network | WETH Address |
|---------|-------------|
| Sepolia | `0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14` |
| Ethereum | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| Base | `0x4200000000000000000000000000000000000006` |
| Arbitrum | `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1` |
