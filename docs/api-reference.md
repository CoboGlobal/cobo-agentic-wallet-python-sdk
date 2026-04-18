# API Reference

> **Auto-generation**: A full backend API reference can be generated from the
> OpenAPI schema once the backend environment is available:
>
> ```bash
> cd cobo-agent-wallet-sdk
> uv run python scripts/generate_api_reference.py --openapi-url http://localhost:8000/api/v1/openapi.json
> ```
>
> The reference below documents the **SDK client surface** (Python classes and
> methods), which is what recipe and integration authors interact with directly.

---

## WalletAPIClient

Async HTTP client for the Cobo Agent Wallet REST API.

### Constructor

```python
WalletAPIClient(
    *,
    base_url: str,
    api_key: str,
    timeout: float = 30.0,
    max_retries: int = 3,
    retry_backoff: float = 1.0,
    http_client: httpx.AsyncClient | None = None,
)
```

| Parameter       | Type                          | Default | Description                       |
|-----------------|-------------------------------|---------|-----------------------------------|
| `base_url`      | `str`                         | —       | API base URL                      |
| `api_key`       | `str`                         | —       | `X-API-Key` header value          |
| `timeout`       | `float`                       | 30.0    | Request timeout in seconds        |
| `max_retries`   | `int`                         | 3       | Retry count on 5xx errors         |
| `retry_backoff` | `float`                       | 1.0     | Exponential backoff multiplier    |
| `http_client`   | `httpx.AsyncClient` or `None` | `None`  | Custom httpx client (for testing) |

### Context Manager

```python
async with WalletAPIClient(base_url="...", api_key="...") as client:
    wallets = await client.list_wallets()
```

### Methods

#### `ping() -> Any`

Health check. No authentication required.

#### `list_wallets(*, offset=0, limit=50, include_archived=False) -> Any`

List available wallets.

| Parameter          | Type   | Default | Description              |
|--------------------|--------|---------|--------------------------|
| `offset`           | `int`  | 0       | Pagination offset        |
| `limit`            | `int`  | 50      | Max results (1–200)      |
| `include_archived` | `bool` | False   | Include archived wallets |

#### `get_wallet(wallet_uuid=None, *, uuid=None) -> Any`

Get wallet details by UUID.

#### `create_wallet(*, name, wallet_type=None, metadata=None) -> Any`

Create a new wallet.

| Parameter     | Type             | Default | Description   |
|---------------|------------------|---------|---------------|
| `name`        | `str`            | —       | Wallet name   |
| `wallet_type` | `str` or `None`  | `None`  | Wallet type   |
| `metadata`    | `dict` or `None` | `None`  | Custom metadata |

#### `get_balance(wallet_uuid=None, *, uuid=None) -> Any`

Alias for `get_wallet()` — the backend embeds balance in the wallet response.

#### `transfer(wallet_uuid=None, *, chain_id, dst_addr, amount, token_id, request_id=None, fee=None, uuid=None) -> Any`

Transfer tokens. **Raises `PolicyDeniedError`** on policy violation.

| Parameter    | Type             | Default | Description         |
|--------------|------------------|---------|---------------------|
| `chain_id`   | `str`            | —       | Blockchain identifier |
| `dst_addr`   | `str`            | —       | Destination address |
| `amount`     | `str`            | —       | Transfer amount     |
| `token_id`   | `str`            | —       | Token identifier    |
| `request_id` | `str` or `None`  | `None`  | Idempotency key     |
| `fee`        | `dict` or `None` | `None`  | Fee configuration   |

#### `estimate_fee(wallet_uuid=None, *, chain_id, dst_addr, amount, token_id, uuid=None) -> Any`

Estimate transfer fee.

#### `list_transactions(wallet_uuid=None, *, offset=0, limit=50, status=None, uuid=None) -> Any`

List wallet transactions with optional status filter.

#### `create_delegation(*, operator_id, wallet_id, permissions, policies=None, expires_at=None) -> Any`

Create an operator delegation.

| Parameter     | Type             | Default | Description                          |
|---------------|------------------|---------|--------------------------------------|
| `operator_id` | `str` (UUID)    | —       | Operator principal UUID              |
| `wallet_id`   | `str` (UUID)    | —       | Target wallet UUID                   |
| `permissions` | `list[str]`     | —       | e.g. `["write:transfer"]`            |
| `policies`    | `list` or `None` | `None` | Inline delegation policies            |
| `expires_at`  | `str` or `None`  | `None` | Expiration datetime (ISO 8601)       |

Valid permission values (from backend `DelegationPermission` enum):
`viewer`, `operator`, `read:wallet`, `write:wallet`, `write:transfer`.

#### `list_delegations(*, operator_id=None, wallet_id=None, status=None, offset=0, limit=50) -> Any`

List delegations with optional filters.

#### `revoke_delegation(delegation_id) -> Any`

Revoke (delete) a delegation.

#### `get_audit_logs(*, wallet_id=None, principal_id=None, action=None, result=None, start_time=None, end_time=None, cursor=None, limit=50) -> Any`

Query audit logs with cursor pagination.

| Parameter      | Type                         | Default | Description                |
|----------------|------------------------------|---------|----------------------------|
| `wallet_id`    | `str` or `None`              | `None`  | Filter by wallet           |
| `principal_id` | `str` or `None`              | `None`  | Filter by principal        |
| `action`       | `str` or `None`              | `None`  | Filter by action type      |
| `result`       | `str` or `None`              | `None`  | `"allowed"` or `"denied"`  |
| `start_time`   | `datetime`, `str`, or `None` | `None`  | Start of time range        |
| `end_time`     | `datetime`, `str`, or `None` | `None`  | End of time range          |
| `cursor`       | `str` or `None`              | `None`  | Pagination cursor          |
| `limit`        | `int`                        | 50      | Max results (1–200)        |

#### `create_policy(*, scope, name, type="contract_call", owner_id=None, wallet_id=None, delegation_id=None, rules=None, priority=0, is_active=True) -> Any`

Create a new policy rule.

| Parameter      | Type             | Default | Description                              |
|----------------|------------------|---------|------------------------------------------|
| `scope`        | `str`            | —       | Policy scope (**required**) - `"global"`, `"wallet"`, or `"delegation"` |
| `name`         | `str`            | —       | Policy name                              |
| `type`         | `str`            | `"contract_call"` | Policy type                   |
| `owner_id`     | `str` or `None`  | `None`  | **Required for `scope="global"`**        |
| `wallet_id`    | `str` or `None`  | `None`  | **Required for `scope="wallet"/"delegation"`** |
| `delegation_id`| `str` or `None`  | `None`  | **Required for `scope="delegation"`**    |
| `rules`        | `dict` or `None` | `None`  | Policy rules configuration               |
| `priority`     | `int`            | 0       | Policy priority                          |
| `is_active`    | `bool`           | True    | Whether policy is active                 |

#### `create_principal(*, external_id, principal_type, name, metadata=None) -> Any`

Create a principal (human owner or AI agent).

#### `create_api_key(*, principal_id, name, scopes=None) -> Any`

Create an API key for a principal.

#### `create_address(wallet_uuid=None, *, chain_id, uuid=None) -> Any`

Create an address for a wallet on a specific chain.

#### `contract_call(wallet_uuid=None, *, chain_id, contract_addr, calldata, value="0", token_id=None, function_id=None, decoded_params=None, request_id=None, fee=None, uuid=None) -> Any`

Submit a smart contract call. **Raises `PolicyDeniedError`** on policy violation.

| Parameter        | Type             | Default | Description            |
|------------------|------------------|---------|------------------------|
| `chain_id`       | `str`            | —       | Blockchain identifier  |
| `contract_addr`  | `str`            | —       | Contract address       |
| `calldata`       | `str`            | —       | Encoded call data      |
| `value`          | `str`            | `"0"`   | ETH value (wei)        |
| `token_id`       | `str` or `None`  | `None`  | Token identifier       |
| `function_id`    | `str` or `None`  | `None`  | Function name/selector |
| `decoded_params` | `dict` or `None` | `None`  | Decoded function params |
| `request_id`     | `str` or `None`  | `None`  | Idempotency key        |
| `fee`            | `dict` or `None` | `None`  | Fee configuration      |

#### `estimate_contract_call_fee(wallet_uuid=None, *, chain_id, contract_addr, calldata, value="0", token_id=None, function_id=None, decoded_params=None, uuid=None) -> Any`

Estimate smart contract call fee.

| Parameter        | Type             | Default | Description            |
|------------------|------------------|---------|------------------------|
| `chain_id`       | `str`            | —       | Blockchain identifier  |
| `contract_addr`  | `str`            | —       | Contract address       |
| `calldata`       | `str`            | —       | Encoded call data      |
| `value`          | `str`            | `"0"`   | ETH value (wei)        |
| `token_id`       | `str` or `None`  | `None`  | Token identifier       |
| `function_id`    | `str` or `None`  | `None`  | Function name/selector |
| `decoded_params` | `dict` or `None` | `None`  | Decoded function params |

#### `get_transaction(wallet_uuid=None, *, transaction_id, uuid=None) -> Any`

Get transaction details by ID.

| Parameter        | Type | Default | Description         |
|------------------|------|---------|---------------------|
| `transaction_id` | `str` | —       | Transaction UUID    |

#### `create_policy(*, scope, name, policy_type, rules, wallet_id=None, delegation_id=None, priority=0, is_active=True) -> Any`

Create a policy.

| Parameter       | Type             | Default | Description             |
|-----------------|------------------|---------|-------------------------|
| `scope`         | `str`            | —       | Policy scope (**required**) |
| `name`          | `str`            | —       | Policy name (**required**) |
| `policy_type`   | `str`            | —       | Policy type (**required**) |
| `rules`         | `dict`           | —       | Policy rule payload (**required**) |
| `wallet_id`     | `str` or `None`  | `None`  | Wallet UUID (scope-dependent) |
| `delegation_id` | `str` or `None`  | `None`  | Delegation UUID (scope-dependent) |
| `priority`      | `int`            | `0`     | Policy priority |
| `is_active`     | `bool`           | `True`  | Initial active status |

**Scope Requirements**:
- `scope="global"`: both `wallet_id` and `delegation_id` must be `None`.
- `scope="wallet"`: `wallet_id` is required and `delegation_id` must be `None`.
- `scope="delegation"`: `delegation_id` is required and `wallet_id` must be `None`.

#### `list_policies(*, scope, wallet_id=None, delegation_id=None, policy_type=None, include_inactive=None, offset=None, limit=None) -> Any`

List policies with optional filters. Scope determines which policies are returned and what additional parameters are required.

| Parameter         | Type             | Default | Description               |
|-------------------|------------------|---------|---------------------------|
| `scope`           | `str`            | —       | Policy scope (**required**) - one of: `"global"`, `"wallet"`, or `"delegation"` |
| `wallet_id`       | `str` or `None`  | `None`  | Wallet UUID (**required for `scope="wallet"` and `scope="delegation"`**) |
| `delegation_id`   | `str` or `None`  | `None`  | **Required for `scope="delegation"`** - Delegation UUID |
| `policy_type`     | `str` or `None`  | `None`  | Optional policy type filter |
| `include_inactive`| `bool` or `None` | `None`  | Include inactive policies |
| `offset`          | `int` or `None`  | `None`  | Pagination offset         |
| `limit`           | `int` or `None`  | `None`  | Max results (1–200)       |

**Scope Requirements**:
- `scope="global"`: Returns global policies owned by current principal.
- `scope="wallet"`: Returns wallet-level policies for `wallet_id` (must provide `wallet_id`).
- `scope="delegation"`: Returns delegation-level policies for `wallet_id` + `delegation_id` (must provide both).

#### `get_policy(*, policy_id) -> Any`

Get policy details by ID.

#### `update_policy(*, policy_id, name=None, rules=None, priority=None, is_active=None) -> Any`

Update a policy (partial update supported).

| Parameter  | Type             | Default | Description      |
|------------|------------------|---------|------------------|
| `name`     | `str` or `None`  | `None`  | Policy name      |
| `rules`    | `dict` or `None` | `None`  | Policy rules     |
| `priority` | `int` or `None`  | `None`  | Policy priority  |
| `is_active`| `bool` or `None` | `None`  | Active flag      |

#### `deactivate_policy(*, policy_id) -> Any`

Delete (disable) a policy.

#### `dry_run_policy(*, wallet_id, operation_type, amount, chain_id, delegation_id=None, token_id=None, dst_addr=None, contract_addr=None, calldata=None, principal_id=None) -> Any`

Dry-run a policy evaluation without executing the operation. Returns policy evaluation result with `effect` field indicating decision outcome. May return 4xx on authentication, authorization, or validation failures.

| Parameter        | Type             | Default | Description                |
|------------------|------------------|---------|----------------------------|
| `operation_type` | `str`            | —       | `"transfer"` or `"contract_call"` (**required**) |
| `amount`         | `str`            | —       | Transfer amount (**required**) |
| `chain_id`       | `str`            | —       | Blockchain identifier (**required**) |
| `delegation_id`  | `str` or `None`  | `None`  | Delegation UUID            |
| `token_id`       | `str` or `None`  | `None`  | Token identifier           |
| `dst_addr`       | `str` or `None`  | `None`  | Destination address (required for transfer) |
| `contract_addr`  | `str` or `None`  | `None`  | Contract address (required for contract_call) |
| `calldata`       | `str` or `None`  | `None`  | Encoded call data          |
| `principal_id`   | `str` or `None`  | `None`  | Principal UUID             |

**Response Fields** (on 200 OK):
- `effect`: Policy decision outcome - `"allow"` (approved), `"require_approval"` (pending approval), or `"deny"` (denied)
- `reason`: Human-readable explanation
- `denied_by_policy_id`: UUID of denying policy (if `effect="deny"`)
- `approval_trigger_policy_id`: UUID of approval-triggering policy (if `effect="require_approval"`)
- `applicable_limits`: List of applicable spending limits
- `tier_evaluations`: Tier evaluation details
- `details`: Additional context

---

## AgentWalletToolkit

Framework-agnostic tool definitions.

### Constructor

```python
AgentWalletToolkit(client: WalletAPIClient)
```

### `get_tools() -> list[ToolDefinition]`

Returns 7 canonical tool definitions:

| Tool                | Required Parameters                                                          |
|---------------------|------------------------------------------------------------------------------|
| `list_wallets`      | —                                                                            |
| `get_balance`       | `wallet_uuid`                                                                |
| `transfer_tokens`   | `wallet_uuid`, `dst_addr`, `token_id`, `amount`                              |
| `list_transactions` | `wallet_uuid`                                                                |
| `get_audit_logs`    | —                                                                            |
| `create_delegation` | `operator_id`, `wallet_id`, `permissions`                                    |

### ToolDefinition

```python
@dataclass(frozen=True)
class ToolDefinition:
    name: str                    # Unique tool ID
    description: str             # Human/LLM description
    parameters: dict[str, Any]   # JSON Schema
    handler: ToolHandler         # async callable
```

---

## Error Hierarchy

### APIError

Base exception for all API failures.

```python
class APIError(Exception):
    message: str
    status_code: int
    response_body: dict[str, Any] | None
```

### Subclasses

| Class                 | HTTP Status | Description        |
|-----------------------|-------------|--------------------|
| `AuthenticationError` | 401         | Invalid API key    |
| `NotFoundError`       | 404         | Resource not found |
| `ServerError`         | 5xx         | Server-side error  |
| `PolicyDeniedError`   | 403         | Policy violation   |

### PolicyDeniedError

```python
class PolicyDeniedError(APIError):
    denial: PolicyDenial   # Structured denial info
```

### PolicyDenial

```python
@dataclass(frozen=True)
class PolicyDenial:
    code: str                     # e.g., "TRANSFER_LIMIT_EXCEEDED"
    reason: str                   # Human-readable reason
    details: dict[str, Any]       # Structured context
    suggestion: str | None        # Retry guidance for LLM
    raw_response: dict[str, Any]  # Original 403 body
```

#### `PolicyDenial.from_response(body: dict) -> PolicyDenial`

Parse a 403 response body. Handles both simple (`{"error": "string"}`) and
structured (`{"error": {"code": ..., "reason": ..., ...}}`) formats.

---

## Framework Integration Entry Points

| Framework     | Import Path                                    | Main Class/Function            |
|---------------|------------------------------------------------|--------------------------------|
| **LangChain** | `cobo_agentic_wallet.integrations.langchain`     | `CoboAgentWalletToolkit`       |
| **OpenAI**    | `cobo_agentic_wallet.integrations.openai`        | `create_cobo_agent()`          |
| **CrewAI**    | `cobo_agentic_wallet.integrations.crewai`        | `CoboAgentWalletCrewAIToolkit` |
| **Agno**      | `cobo_agentic_wallet.integrations.agno`          | `CoboAgentWalletTools`         |
