# Changelog

## 0.1.40

- Bumped OpenAPI document version to 1.3.0

### New models
- `PactRemaining` — tracks remaining quota for an active pact: `tx_count_remaining`, `usd_remaining`, `time_remaining_seconds`
- `RecentTxSummary` — compact transaction record used for recent-activity enrichment: `id`, `request_id`, `status`, `operation_type`, `created_at`

### Model updates
- **`PactSummary`**: added `remaining: PactRemaining` field exposing live quota; `expires_at` is now a required field
- **`PactPublicRead`**: added `recent_txs: List[RecentTxSummary]` — up to 5 most-recent transactions submitted under the pact, newest first
- **`SearchRecipesRequest`**: added optional `wallet_id` — when provided, active pacts referencing each matched recipe are embedded as `matching_pacts` in the result
- **`UserTransactionRead`**: added `fee` (provider fee details) and `cobo_transaction_id` fields; `transaction_hash` is now a required field
- **`UserTransactionData`**: added `cobo_transaction_id`; `instructions` items are no longer nullable
- **`AuditLogRead`**: `principal_id`, `wallet_id`, `resource_type`, `resource_id`, and `error` are now required fields with descriptions
- **`ApiKeyPublicRead`**: `expires_at`, `last_used_at`, and `revoked_at` are now required fields with descriptions
- **`WalletRead` / `WalletDetailRead`**: `cobo_wallet_id` is now a required field
- **`WalletPairInitiateRead` / `WalletPairRead`**: `claimer_principal_id` is now a required field
- **`PendingOperationRead`**: `request_id`, `delegation_id`, and `policy_decision` are now required fields

### API changes
- **`search_recipes`**: now accepts an optional `wallet_id` parameter (mirrors the model update above)

### Enum changes
- **`SuggestionKey`**: removed `WALLET_PAIR_WALLET_NOT_FOUND` and `PACT_REVOKE_SUCCESS` values

## 0.1.39

- Bumped OpenAPI document version to 1.2.4
- **Pact**: `submit_pact` now accepts an optional `recipe_slugs` parameter to associate pact templates at submission time
- **Recipe**: replaced the full recipe-library API surface with the focused method:
  - `search_recipes` — `query` is now optional (defaults to `""`)
- **Transaction**: `list_recent_addresses` and `list_recent_addresses_by_user` accept a new optional `token_id` filter
- **Models added**: `WalletPairTokenPurpose`
- **README**: added AI coding-agent setup section (`npx skills add` for the CAW developer skill)

## 0.1.34

- Initial release of the Python SDK
- `WalletAPIClient` — async client for wallet, pact, transaction, and audit operations
- Tools: `list_wallets`, `get_wallet`, `list_wallet_addresses`, `get_balance`, `submit_pact`, `get_pact`, `list_pacts`, `transfer_tokens`, `contract_call`, `message_sign`, `payment`, `estimate_transfer_fee`, `estimate_contract_call_fee`, `list_transactions`, `list_transaction_records`, `get_transaction_record`, `get_transaction_record_by_request_id`, `list_recent_addresses`, `get_audit_logs`, `create_delegation`
- MCP server: `python -m cobo_agentic_wallet.mcp` with `AGENT_WALLET_INCLUDE_TOOLS` / `AGENT_WALLET_EXCLUDE_TOOLS` env support
- Framework integrations: LangChain, OpenAI Agents SDK, Agno, CrewAI
- `include_tools` / `exclude_tools` filtering on `AgentWalletToolkit`
