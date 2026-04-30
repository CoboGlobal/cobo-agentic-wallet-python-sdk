# Changelog

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
