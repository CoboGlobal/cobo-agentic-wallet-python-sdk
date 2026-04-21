"""Canonical tool metadata shared by toolkit and MCP layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    """Framework-agnostic tool metadata."""

    name: str
    description: str
    parameters: dict[str, Any]


_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        name="list_wallets",
        description="List wallets accessible to the caller. Use this tool to discover wallet UUIDs required by other tools such as get_balance and transfer_tokens.",
        parameters={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Maximum number of wallets to return per page; optional, defaults to 50, maximum 200",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of wallets to skip before returning results; optional, defaults to 0",
                },
                "include_archived": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to include archived wallets in results; optional, defaults to false",
                },
            },
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="get_wallet",
        description="Get wallet metadata and status for a specific wallet.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet to retrieve; obtain from list_wallets",
                },
                "include_spend_summary": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to include delegation spend summaries in the response.",
                },
            },
            "required": ["wallet_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="list_wallet_addresses",
        description="List the on-chain addresses that belong to a wallet.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet whose addresses to list; obtain from list_wallets",
                }
            },
            "required": ["wallet_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="get_balance",
        description="Get token balances for a specific wallet.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet whose balances to retrieve; obtain from list_wallets",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Optional chain identifier to filter balances to a single network.",
                },
                "token_id": {
                    "type": "string",
                    "description": "Optional token identifier to filter balances to a single asset.",
                },
                "force_refresh": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to bypass cached balances and refresh from upstream.",
                },
            },
            "required": ["wallet_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="submit_pact",
        description="Submit a pact for owner approval so the runtime can receive scoped authority for a task.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_id": {
                    "type": "string",
                    "description": "UUID of the wallet this pact is scoped to; obtain from list_wallets",
                },
                "intent": {
                    "type": "string",
                    "description": "Concise description of the task the runtime intends to perform, used for owner review",
                },
                "original_intent": {
                    "type": "string",
                    "description": "Optional user-provided wording before the runtime refined the intent.",
                },
                "spec": {
                    "type": "object",
                    "description": (
                        "PactSpec payload. At least one policy and one completion_condition "
                        "are required. Each policy's ``rules`` object is validated per ``type`` "
                        "(transfer / contract_call / message_sign); the schema below is the "
                        "union of all three shapes — only include the keys that apply to the "
                        "policy ``type`` you declare. Pact policies are always ALLOW; use "
                        "``deny_if`` (empty ``{}`` = blacklist) and ``review_if`` for blocks "
                        "and soft reviews. Canonical field names: ``contract_addr`` (not "
                        "``contract_address``), ``function_id`` (not ``function_signature``)."
                    ),
                    "properties": {
                        "policies": {
                            "type": "array",
                            "minItems": 1,
                            "description": (
                                "Policy objects governing which operations the pact authorizes; "
                                "at least one policy is required."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Short identifier for this policy.",
                                    },
                                    "type": {
                                        "type": "string",
                                        "enum": ["transfer", "contract_call", "message_sign"],
                                        "description": "Which canonical operation this policy gates.",
                                    },
                                    "rules": {
                                        "type": "object",
                                        "description": (
                                            "Rule envelope. Pact-scoped policies only accept "
                                            '``effect: "allow"``; use ``deny_if`` / ``review_if`` '
                                            "for hard-blocks and soft-reviews. Fields inside "
                                            "``when`` / ``deny_if`` / ``review_if`` depend on the "
                                            "policy ``type`` — see each sub-schema's description."
                                        ),
                                        "properties": {
                                            "effect": {
                                                "type": "string",
                                                "enum": ["allow"],
                                                "default": "allow",
                                                "description": (
                                                    "Only ``allow`` is supported for pact "
                                                    "policies. To block matching operations, "
                                                    "set ``deny_if: {}`` (unconditional deny) "
                                                    "or populate ``deny_if`` with per-tx or "
                                                    "rolling-window thresholds."
                                                ),
                                            },
                                            "always_review": {
                                                "type": "boolean",
                                                "default": False,
                                                "description": (
                                                    "If true, every matching operation requires "
                                                    "owner approval regardless of amount. Can be "
                                                    "combined with ``when.*`` scope filters."
                                                ),
                                            },
                                            "when": {
                                                "type": "object",
                                                "description": (
                                                    "Allow-list scope filters. Include only the "
                                                    "keys that apply to the policy ``type``: "
                                                    "transfer → chain_in / token_in / "
                                                    "destination_address_in. contract_call (EVM) "
                                                    "→ chain_in / target_in / params_match. "
                                                    "contract_call (Solana) → chain_in / "
                                                    "program_in / program_all_in. message_sign "
                                                    "→ chain_in / primary_type_in / "
                                                    "source_address_in / domain_match / "
                                                    "message_match."
                                                ),
                                                "properties": {
                                                    "chain_in": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                        "description": (
                                                            "Allowed Cobo chain IDs (e.g. "
                                                            "'SETH', 'BASE_ETH', 'SOL'). Applies "
                                                            "to all three policy types."
                                                        ),
                                                    },
                                                    "token_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "token_id": {"type": "string"},
                                                            },
                                                            "required": ["chain_id", "token_id"],
                                                        },
                                                        "description": (
                                                            "transfer-only. Allowed tokens as "
                                                            "{chain_id, token_id} pairs. Each "
                                                            "token is its own list element — "
                                                            "never join multiple IDs into one "
                                                            "string."
                                                        ),
                                                    },
                                                    "destination_address_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "address": {"type": "string"},
                                                            },
                                                            "required": ["chain_id", "address"],
                                                        },
                                                        "description": (
                                                            "transfer-only. Allowed destination "
                                                            "addresses as {chain_id, address} "
                                                            "pairs."
                                                        ),
                                                    },
                                                    "target_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "contract_addr": {
                                                                    "type": "string",
                                                                    "description": (
                                                                        "EVM contract address. "
                                                                        "Canonical field name — "
                                                                        "do NOT use "
                                                                        "``contract_address``."
                                                                    ),
                                                                },
                                                                "function_id": {
                                                                    "type": "string",
                                                                    "description": (
                                                                        "Optional EVM function "
                                                                        "selector (4-byte hex "
                                                                        "like ``0xa9059cbb`` or "
                                                                        "canonical signature). "
                                                                        "Canonical field name — "
                                                                        "do NOT use "
                                                                        "``function_signature``. "
                                                                        "Required at least once "
                                                                        "when ``params_match`` is "
                                                                        "set."
                                                                    ),
                                                                },
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "contract_addr",
                                                            ],
                                                        },
                                                        "description": (
                                                            "contract_call (EVM only). Allowed "
                                                            "contract/function targets."
                                                        ),
                                                    },
                                                    "program_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "program_id": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "program_id",
                                                            ],
                                                        },
                                                        "description": (
                                                            "contract_call (Solana only). At "
                                                            "least one listed program_id must "
                                                            "appear in the transaction."
                                                        ),
                                                    },
                                                    "program_all_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "program_id": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "program_id",
                                                            ],
                                                        },
                                                        "description": (
                                                            "contract_call (Solana only). All "
                                                            "listed program_ids must appear in "
                                                            "the transaction."
                                                        ),
                                                    },
                                                    "params_match": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "param_name": {"type": "string"},
                                                                "op": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "eq",
                                                                        "neq",
                                                                        "in",
                                                                        "not_in",
                                                                        "lte",
                                                                        "gte",
                                                                        "lt",
                                                                        "gt",
                                                                    ],
                                                                },
                                                                "value": {
                                                                    "description": (
                                                                        "Scalar for most ops; "
                                                                        "list for ``in`` / "
                                                                        "``not_in``."
                                                                    ),
                                                                },
                                                            },
                                                            "required": [
                                                                "param_name",
                                                                "op",
                                                                "value",
                                                            ],
                                                        },
                                                        "description": (
                                                            "contract_call (EVM only). Decoded "
                                                            "calldata parameter constraints. "
                                                            "Requires rules.function_abis and "
                                                            "at least one target_in.function_id."
                                                        ),
                                                    },
                                                    "primary_type_in": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                        "description": (
                                                            "message_sign-only. Allowed EIP-712 "
                                                            "primary types."
                                                        ),
                                                    },
                                                    "source_address_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "address": {"type": "string"},
                                                            },
                                                            "required": ["chain_id", "address"],
                                                        },
                                                        "description": (
                                                            "message_sign-only. Allowed signer "
                                                            "source addresses."
                                                        ),
                                                    },
                                                    "domain_match": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "param_name": {"type": "string"},
                                                                "op": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "eq",
                                                                        "neq",
                                                                        "in",
                                                                        "not_in",
                                                                    ],
                                                                },
                                                                "value": {},
                                                            },
                                                            "required": [
                                                                "param_name",
                                                                "op",
                                                                "value",
                                                            ],
                                                        },
                                                        "description": (
                                                            "message_sign-only. EIP-712 domain "
                                                            "field constraints (e.g. "
                                                            "{param_name: 'name', op: 'eq', "
                                                            "value: 'Permit2'})."
                                                        ),
                                                    },
                                                    "message_match": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "param_name": {"type": "string"},
                                                                "op": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "eq",
                                                                        "neq",
                                                                        "in",
                                                                        "not_in",
                                                                        "lte",
                                                                        "gte",
                                                                        "lt",
                                                                        "gt",
                                                                    ],
                                                                },
                                                                "value": {},
                                                            },
                                                            "required": [
                                                                "param_name",
                                                                "op",
                                                                "value",
                                                            ],
                                                        },
                                                        "description": (
                                                            "message_sign-only. EIP-712 message "
                                                            "body field constraints."
                                                        ),
                                                    },
                                                },
                                            },
                                            "deny_if": {
                                                "type": "object",
                                                "description": (
                                                    "Hard-block conditions. Empty object "
                                                    "``{}`` = unconditional deny (blacklist "
                                                    "pattern for this ``when`` scope). "
                                                    "Otherwise combine per-tx caps with "
                                                    "rolling-window usage_limits. "
                                                    "``deny_if`` takes precedence over "
                                                    "``review_if`` when both match."
                                                ),
                                                "properties": {
                                                    "amount_gt": {
                                                        "type": "string",
                                                        "description": (
                                                            "transfer / contract_call only. "
                                                            "Per-tx token-unit cap, e.g. "
                                                            "'0.002'. Amounts strictly greater "
                                                            "are denied."
                                                        ),
                                                    },
                                                    "amount_usd_gt": {
                                                        "type": "string",
                                                        "description": (
                                                            "transfer / contract_call only. "
                                                            "Per-tx USD cap, e.g. '500'. Only "
                                                            "applies to tokens with price "
                                                            "data; tokens without price data "
                                                            "bypass USD checks entirely."
                                                        ),
                                                    },
                                                    "usage_limits": {
                                                        "type": "object",
                                                        "description": (
                                                            "Rolling-window cumulative caps. "
                                                            "Each window is its own object "
                                                            "with the same inner shape — set "
                                                            "at least one window with at "
                                                            "least one metric. ``amount_*`` "
                                                            "and ``tx_count_gt`` apply to "
                                                            "transfer and contract_call; "
                                                            "``request_count_gt`` is "
                                                            "message_sign-only."
                                                        ),
                                                        "properties": {
                                                            "rolling_1h": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "amount_gt": {"type": "string"},
                                                                    "amount_usd_gt": {
                                                                        "type": "string"
                                                                    },
                                                                    "tx_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                    "request_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                },
                                                            },
                                                            "rolling_24h": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "amount_gt": {"type": "string"},
                                                                    "amount_usd_gt": {
                                                                        "type": "string"
                                                                    },
                                                                    "tx_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                    "request_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                },
                                                            },
                                                            "rolling_7d": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "amount_gt": {"type": "string"},
                                                                    "amount_usd_gt": {
                                                                        "type": "string"
                                                                    },
                                                                    "tx_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                    "request_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                },
                                                            },
                                                            "rolling_30d": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "amount_gt": {"type": "string"},
                                                                    "amount_usd_gt": {
                                                                        "type": "string"
                                                                    },
                                                                    "tx_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                    "request_count_gt": {
                                                                        "type": "integer",
                                                                        "minimum": 1,
                                                                    },
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            "review_if": {
                                                "type": "object",
                                                "description": (
                                                    "Soft-block conditions — matching "
                                                    "operations require owner approval before "
                                                    "executing. Mix amount thresholds with "
                                                    "scope filters (same shape as ``when``). "
                                                    "message_sign does not support amount "
                                                    "thresholds — use scope filters or "
                                                    "``always_review`` instead."
                                                ),
                                                "properties": {
                                                    "amount_gt": {
                                                        "type": "string",
                                                        "description": (
                                                            "transfer / contract_call only. "
                                                            "Per-tx token-unit threshold."
                                                        ),
                                                    },
                                                    "amount_usd_gt": {
                                                        "type": "string",
                                                        "description": (
                                                            "transfer / contract_call only. "
                                                            "Per-tx USD threshold."
                                                        ),
                                                    },
                                                    "chain_in": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                    "token_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "token_id": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "token_id",
                                                            ],
                                                        },
                                                    },
                                                    "destination_address_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "address": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "address",
                                                            ],
                                                        },
                                                    },
                                                    "target_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "contract_addr": {"type": "string"},
                                                                "function_id": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "contract_addr",
                                                            ],
                                                        },
                                                    },
                                                    "program_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "program_id": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "program_id",
                                                            ],
                                                        },
                                                    },
                                                    "program_all_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "program_id": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "program_id",
                                                            ],
                                                        },
                                                    },
                                                    "params_match": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "param_name": {"type": "string"},
                                                                "op": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "eq",
                                                                        "neq",
                                                                        "in",
                                                                        "not_in",
                                                                        "lte",
                                                                        "gte",
                                                                        "lt",
                                                                        "gt",
                                                                    ],
                                                                },
                                                                "value": {},
                                                            },
                                                            "required": [
                                                                "param_name",
                                                                "op",
                                                                "value",
                                                            ],
                                                        },
                                                    },
                                                    "primary_type_in": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                    "source_address_in": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "chain_id": {"type": "string"},
                                                                "address": {"type": "string"},
                                                            },
                                                            "required": [
                                                                "chain_id",
                                                                "address",
                                                            ],
                                                        },
                                                    },
                                                    "domain_match": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "param_name": {"type": "string"},
                                                                "op": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "eq",
                                                                        "neq",
                                                                        "in",
                                                                        "not_in",
                                                                    ],
                                                                },
                                                                "value": {},
                                                            },
                                                            "required": [
                                                                "param_name",
                                                                "op",
                                                                "value",
                                                            ],
                                                        },
                                                    },
                                                    "message_match": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "param_name": {"type": "string"},
                                                                "op": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "eq",
                                                                        "neq",
                                                                        "in",
                                                                        "not_in",
                                                                        "lte",
                                                                        "gte",
                                                                        "lt",
                                                                        "gt",
                                                                    ],
                                                                },
                                                                "value": {},
                                                            },
                                                            "required": [
                                                                "param_name",
                                                                "op",
                                                                "value",
                                                            ],
                                                        },
                                                    },
                                                },
                                            },
                                            "function_abis": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": [
                                                                "function",
                                                                "constructor",
                                                                "fallback",
                                                                "receive",
                                                                "event",
                                                                "error",
                                                            ],
                                                        },
                                                        "selector": {
                                                            "type": "string",
                                                            "description": (
                                                                "4-byte selector hex "
                                                                "(``0xa9059cbb``) or canonical "
                                                                "function signature."
                                                            ),
                                                        },
                                                        "inputs": {
                                                            "type": "array",
                                                            "items": {"type": "object"},
                                                            "description": (
                                                                "Each input entry must include "
                                                                "``name`` (str) and ``type`` "
                                                                "(str)."
                                                            ),
                                                        },
                                                        "name": {"type": "string"},
                                                    },
                                                    "required": ["type", "selector"],
                                                },
                                                "description": (
                                                    "contract_call (EVM only). ABI entries "
                                                    "used to decode calldata for "
                                                    "``params_match``. Required when "
                                                    "``when.params_match`` or "
                                                    "``review_if.params_match`` is set."
                                                ),
                                            },
                                        },
                                        "required": ["effect"],
                                    },
                                },
                                "required": ["name", "type", "rules"],
                            },
                        },
                        "completion_conditions": {
                            "type": "array",
                            "minItems": 1,
                            "description": (
                                "Conditions that close the pact; at least one is required. "
                                "``threshold`` semantics depend on ``type`` (seconds for "
                                "time_elapsed, count for tx_count, decimal string for amount_*)."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "time_elapsed",
                                            "tx_count",
                                            "amount_spent",
                                            "amount_spent_usd",
                                            "manual",
                                        ],
                                    },
                                    "threshold": {
                                        "type": "string",
                                        "description": "Stringified threshold interpreted per ``type``.",
                                    },
                                },
                                "required": ["type"],
                            },
                        },
                        "execution_plan": {
                            "type": "string",
                            "description": "Optional markdown outline of how the runtime will execute the pact.",
                        },
                    },
                    "required": ["policies", "completion_conditions"],
                },
                "name": {
                    "type": "string",
                    "description": "Optional short pact name for display in owner-facing UI.",
                },
            },
            "required": ["wallet_id", "intent", "spec"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="get_pact",
        description="Get the latest status and details for a pact.",
        parameters={
            "type": "object",
            "properties": {
                "pact_id": {
                    "type": "string",
                    "description": "UUID of the pact to retrieve; obtain from submit_pact or list_pacts",
                }
            },
            "required": ["pact_id"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="list_pacts",
        description="List pacts visible to the caller, optionally filtered by status or wallet.",
        parameters={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Optional pact status filter such as ACTIVE or PENDING_APPROVAL.",
                },
                "wallet_id": {
                    "type": "string",
                    "description": "Optional wallet UUID to scope pact results.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Maximum number of pacts to return per page; optional, defaults to 50.",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of pacts to skip before returning results; optional, defaults to 0.",
                },
            },
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="transfer_tokens",
        description="Transfer tokens from a Cobo wallet to a destination address. Organisation spending policies are enforced; the transfer may require approval before it is executed.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the source wallet from which tokens will be transferred; obtain from list_wallets",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Chain identifier that must match the token's network exactly, e.g. ETH, SETH, BSC_BNB. Do NOT guess; obtain from list_supported_chains or wallet address info.",
                },
                "dst_addr": {
                    "type": "string",
                    "description": "On-chain destination address that will receive the tokens",
                },
                "token_id": {
                    "type": "string",
                    "description": "Cobo token identifier for the asset to transfer, e.g. ETH_USDT; obtain from get_balance or list_supported_tokens",
                },
                "amount": {
                    "type": "string",
                    "description": "Amount to transfer as a decimal string in the token's native unit, e.g. '1.5'",
                },
                "fee": {
                    "type": "object",
                    "description": "Optional fee configuration object (e.g. gas price overrides); omit to use the platform default fee",
                },
                "pact_id": {
                    "type": "string",
                    "description": "pact_id returned by submit_pact; pass it whenever this transfer falls under an active pact so the toolkit routes the call through the pact-scoped API key (required for agent/operator principals). Omit only for owner-level direct transfers.",
                },
            },
            "required": ["wallet_uuid", "chain_id", "dst_addr", "token_id", "amount"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="contract_call",
        description="Call a smart contract from a wallet. Policy rules and owner review thresholds are enforced before execution.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet initiating the contract call; obtain from list_wallets",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Chain identifier for the contract call, for example BASE_ETH.",
                },
                "contract_addr": {
                    "type": "string",
                    "description": "Target contract address. Optional for chains that use instruction-based payloads.",
                },
                "value": {
                    "type": "string",
                    "default": "0",
                    "description": "Native asset value to send with the call, expressed as a decimal string.",
                },
                "calldata": {
                    "type": "string",
                    "description": "Encoded calldata for EVM contract calls.",
                },
                "instructions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional chain-specific instruction objects, for example Solana instructions.",
                },
                "address_lookup_table_accounts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional Solana address lookup table accounts.",
                },
                "request_id": {
                    "type": "string",
                    "description": "Caller-supplied idempotency key for this contract call request.",
                },
                "fee": {
                    "type": "object",
                    "description": "Optional fee configuration object.",
                },
                "src_addr": {
                    "type": "string",
                    "description": "Optional source address when the wallet has multiple addresses on the same chain.",
                },
                "sponsor": {
                    "type": "boolean",
                    "description": "Optional flag to request sponsored gas when supported.",
                },
                "gas_provider": {
                    "type": "string",
                    "description": "Optional gas provider identifier when sponsored gas is supported.",
                },
                "description": {
                    "type": "string",
                    "description": "Optional human-readable description for auditability.",
                },
                "pact_id": {
                    "type": "string",
                    "description": "pact_id returned by submit_pact; pass it whenever this contract call falls under an active pact so the toolkit routes the call through the pact-scoped API key (required for agent/operator principals). Omit only for owner-level direct calls.",
                },
            },
            "required": ["wallet_uuid", "chain_id"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="message_sign",
        description="Sign a message or typed data with the wallet without broadcasting an on-chain transaction.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet whose key will sign the message; obtain from list_wallets",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Chain identifier for the signing context, e.g. ETH or BASE_ETH",
                },
                "destination_type": {
                    "type": "string",
                    "description": "Destination/signing mode, for example EIP-712 typed data.",
                },
                "eip712_typed_data": {
                    "type": "object",
                    "description": "Typed-data payload for EIP-712 signing flows.",
                },
                "source_address": {
                    "type": "string",
                    "description": "Optional source address when the wallet has multiple addresses on the same chain.",
                },
                "description": {
                    "type": "string",
                    "description": "Optional human-readable description for the signing request.",
                },
                "sync": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to wait for a synchronous signing result when supported.",
                },
                "request_id": {
                    "type": "string",
                    "description": "Caller-supplied idempotency key for this signing request.",
                },
                "pact_id": {
                    "type": "string",
                    "description": "pact_id returned by submit_pact; pass it whenever this signing call falls under an active pact so the toolkit routes the call through the pact-scoped API key (required for agent/operator principals). Omit only for owner-level direct signs.",
                },
            },
            "required": ["wallet_uuid", "chain_id"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="payment",
        description="Submit a payment request such as x402 or MPP using the wallet as the payment instrument.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet to use as the payment instrument; obtain from list_wallets",
                },
                "protocol": {
                    "type": "string",
                    "description": "Payment protocol identifier such as x402 or mpp.",
                },
                "request_id": {
                    "type": "string",
                    "description": "Caller-supplied idempotency key for this payment request.",
                },
                "x402_payment_required": {
                    "type": "string",
                    "description": "Raw x402 Payment-Required header value when using x402 flows.",
                },
                "mpp_www_authenticate": {
                    "type": "string",
                    "description": "Raw WWW-Authenticate header value when using MPP flows.",
                },
                "mpp_session": {
                    "type": "object",
                    "description": "Optional MPP session payload when continuing an existing session.",
                },
                "pact_id": {
                    "type": "string",
                    "description": "pact_id returned by submit_pact; pass it whenever this payment falls under an active pact so the toolkit routes the call through the pact-scoped API key (required for agent/operator principals). Omit only for owner-level direct payments.",
                },
            },
            "required": ["wallet_uuid", "protocol"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="estimate_transfer_fee",
        description="Estimate the network fee for a token transfer before submitting it.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the source wallet; obtain from list_wallets",
                },
                "dst_addr": {
                    "type": "string",
                    "description": "On-chain destination address that would receive the tokens",
                },
                "amount": {
                    "type": "string",
                    "description": "Transfer amount as a decimal string in the token's native unit, e.g. '1.5'",
                },
                "token_id": {
                    "type": "string",
                    "description": "Token identifier for the asset being transferred.",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Optional chain identifier when the token ID alone is insufficient.",
                },
                "src_addr": {
                    "type": "string",
                    "description": "Optional source address when the wallet has multiple addresses on the same chain.",
                },
                "pact_id": {
                    "type": "string",
                    "description": "pact_id returned by submit_pact; pass it whenever the estimate is for a transfer that will run under an active pact. Omit for owner-level estimates.",
                },
            },
            "required": ["wallet_uuid", "dst_addr", "amount"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="estimate_contract_call_fee",
        description="Estimate the network fee for a contract call before submitting it.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet that would initiate the call; obtain from list_wallets",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Chain identifier for the contract call, e.g. ETH or BASE_ETH",
                },
                "contract_addr": {
                    "type": "string",
                    "description": "Target contract address. Optional for instruction-based chains.",
                },
                "value": {
                    "type": "string",
                    "default": "0",
                    "description": "Native asset value to send with the call, expressed as a decimal string.",
                },
                "calldata": {
                    "type": "string",
                    "description": "Encoded calldata for EVM contract calls.",
                },
                "instructions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional chain-specific instruction objects.",
                },
                "address_lookup_table_accounts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional Solana address lookup table accounts.",
                },
                "src_addr": {
                    "type": "string",
                    "description": "Optional source address when the wallet has multiple addresses on the same chain.",
                },
                "pact_id": {
                    "type": "string",
                    "description": "pact_id returned by submit_pact; pass it whenever the estimate is for a call that will run under an active pact. Omit for owner-level estimates.",
                },
            },
            "required": ["wallet_uuid", "chain_id"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="list_transactions",
        description="List transactions associated with a wallet, optionally filtered by status. Returns both incoming and outgoing transactions in reverse-chronological order.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet whose transactions to list; obtain from list_wallets",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Maximum number of transactions to return per page; optional, defaults to 50, maximum 200",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of transactions to skip before returning results; optional, defaults to 0",
                },
                "status": {
                    "type": "string",
                    "description": "Filter transactions by status; optional, valid values include PENDING, SUCCESS, FAILED — omit to return all statuses",
                },
            },
            "required": ["wallet_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="list_transaction_records",
        description="List persisted transaction records for a wallet, including transfers, contract calls, deposits, and payments.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet whose transaction records to list; obtain from list_wallets",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Maximum number of records to return per page; optional, defaults to 50.",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip before returning results; optional, defaults to 0.",
                },
                "status": {
                    "type": "string",
                    "description": "Optional transaction status filter.",
                },
                "record_type": {
                    "type": "string",
                    "description": "Optional record type filter such as transfer or contract_call.",
                },
                "token_id": {
                    "type": "string",
                    "description": "Optional token identifier filter.",
                },
                "chain_id": {
                    "type": "string",
                    "description": "Optional chain identifier filter.",
                },
                "address_id": {
                    "type": "string",
                    "description": "Optional wallet address identifier filter.",
                },
            },
            "required": ["wallet_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="get_transaction_record",
        description="Get a single transaction record by its record UUID.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet that owns the record; obtain from list_wallets",
                },
                "record_uuid": {
                    "type": "string",
                    "description": "UUID of the transaction record to retrieve; obtain from list_transaction_records",
                },
            },
            "required": ["wallet_uuid", "record_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="get_transaction_record_by_request_id",
        description="Look up a transaction record by the caller-supplied idempotency request ID.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet that owns the record; obtain from list_wallets",
                },
                "request_id": {
                    "type": "string",
                    "description": "Idempotency key originally supplied when the transaction was submitted",
                },
            },
            "required": ["wallet_uuid", "request_id"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="list_recent_addresses",
        description="List recently used destination addresses for a wallet.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_uuid": {
                    "type": "string",
                    "description": "UUID of the wallet whose recent destination addresses to list; obtain from list_wallets",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 20,
                    "description": "Maximum number of recent addresses to return; optional, defaults to 20.",
                },
            },
            "required": ["wallet_uuid"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="get_audit_logs",
        description="Query the organisation audit log, returning records of actions performed by operators on wallets. Supports filtering by wallet, principal, action type, result, and time range using cursor-based pagination.",
        parameters={
            "type": "object",
            "properties": {
                "wallet_id": {
                    "type": "string",
                    "description": "Filter logs to a specific wallet; optional, obtain the ID from list_wallets",
                },
                "principal_id": {
                    "type": "string",
                    "description": "Filter logs to a specific operator or user who performed the action; optional",
                },
                "action": {
                    "type": "string",
                    "description": "Filter logs by action type, e.g. TRANSFER, CREATE_DELEGATION; optional",
                },
                "result": {
                    "type": "string",
                    "description": "Filter logs by outcome; optional, valid values: SUCCESS, FAILURE",
                },
                "start_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Return only logs at or after this ISO 8601 timestamp; optional",
                },
                "end_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Return only logs at or before this ISO 8601 timestamp; optional",
                },
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor from the previous response; optional, omit for the first page",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Maximum number of log entries to return per page; optional, defaults to 50, maximum 200",
                },
            },
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="create_delegation",
        description="Create a delegation that grants an operator scoped permissions on a wallet. Use this tool to authorise another party to perform limited actions (e.g. transfer up to a spending limit) without giving full wallet access.",
        parameters={
            "type": "object",
            "properties": {
                "operator_id": {
                    "type": "string",
                    "description": "ID of the operator (agent or user) being granted the delegation",
                },
                "wallet_id": {
                    "type": "string",
                    "description": "ID of the wallet the operator is being granted access to; obtain from list_wallets",
                },
                "permissions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "One or more permission strings to grant, e.g. ['TRANSFER', 'VIEW_BALANCE']; at least one is required",
                },
                "constraints": {
                    "type": "object",
                    "description": "Optional constraints that narrow the delegation, e.g. spending limits or allowed token types; omit for unconstrained permissions",
                },
                "expires_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 timestamp after which the delegation expires; optional, omit for a non-expiring delegation",
                },
            },
            "required": ["operator_id", "wallet_id", "permissions"],
            "additionalProperties": False,
        },
    ),
)

_TOOL_SPEC_BY_NAME = {spec.name: spec for spec in _TOOL_SPECS}


def list_tool_specs() -> tuple[ToolSpec, ...]:
    """Return all canonical tool metadata."""

    return _TOOL_SPECS


def get_tool_spec(name: str) -> ToolSpec:
    """Lookup metadata by tool name."""

    return _TOOL_SPEC_BY_NAME[name]
