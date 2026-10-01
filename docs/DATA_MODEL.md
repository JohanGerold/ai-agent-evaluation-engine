# Architecture Revision 2 - Data model and DSL specification

Proposed only. All numerical settings are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. This is the normative prose DSL v1 specification; T-007b must freeze corresponding machine-readable schemas and fixtures before dependent modules are implemented. There is no executable DSL implementation in this revision.

## Ownership and relational constraints

UUID identity, UTC times, exact integer micro-USD, explicit workspace_id on every tenant row, project_id on every project row. Workspace is the visibility and budget boundary; all members see all its projects. Tenant uniqueness includes workspace; IDs do not authorize access. Lifecycle deletion is explicit, not casual cascading through historical results.

| Entity | Identity, ownership and key invariant |
|---|---|
| User / Session | Global identity issuer+subject unique; never merge by unverified email; session_epoch/expiry; worker denied SELECT |
| Workspace / WorkspaceMembership / Invitation | Tenant root; membership unique workspace/user, owner/member; lock last-owner changes; invitation hash, target verified email, one-use, proposed 7-day expiry |
| ApiCredential | Tenant+project+creator, bounded scopes, keyed hash only, displayed once, proposed 90-day expiry; worker denied all access |
| Project / Agent / TestSuite | Tenant+project mutable catalog, revision and scoped slug/label constraints |
| AgentVersion | Immutable config/hash/schema version, tenant+project+agent+version label unique |
| ScenarioDraft | Tenant+project+lineage ID, revision, definition, source and review metadata |
| SuiteVersion / SuiteScenario | Immutable policy/reviewer/hash; case_id and ordinal unique within suite; copied definition, never live draft pointer |
| EvaluationRun | Tenant+project+agent/suite IDs, actor, immutable manifest, state, execution-group allocation, absolute deadline, authorized budget, cancellation metadata |
| ScenarioRun | Unique workspace/evaluation/case/repetition; scheduling status and write-once canonical_attempt_id |
| ScenarioAttempt | Tenant+scenario+attempt number unique; epoch, state, termination, completion/evidence metadata; abandoned attempts preserved |
| Job | Narrow tenant/kind/payload-reference row; unique logical job key, available_at, lease_owner/expiry/epoch, attempts; partial queued and lease-expiry indexes |
| TraceEvent | Tenant+attempt+gap-free sequence unique; type/actor/time/payload, original/persisted bytes, redaction/truncation paths, evidence_role, correlation ID; append-only fenced writes |
| EvaluationResult / Finding | Result unique per attempt; immutable verdict/evidence coverage/deciding kinds/policy; findings cite same-attempt persisted evidence and fixed reviewed severity |
| ModelCall | Unique dispatch_id, phase/attempt/turn/retry, request-surface/rate/estimator versions, reservation and provider metadata; state transition guarded |
| UsageLedgerEntry | Append-only reserve/known settlement/estimated settlement/adjustment/release, unique idempotency identity, original period/scope/dispatch reference |
| BudgetBucket / ConcurrencyCounter / StorageBucket | Derived counters with nonnegative constraints and unique scope/period; ledger rebuildable; global counters after tenant counters in lock order |
| ExecutionGroup | One of two global groups, <=2 slots/group, assigned to one workspace/evaluation or generation; lease/recovery bookkeeping cannot reset evaluation deadline |
| SecretReference | Platform alias/version/fingerprint only; no secret values; environment-specific |
| AuditEvent | Tenant or explicitly platform-owned, append-only safe actor/action/target/reason/request ID; atomic with sensitive mutation |
| IdempotencyRecord | Unique tenant+principal+operation+key; body hash and resource ID, >=7-day retention; never caches secret issuance response |
| DeletionTombstone | Minimal scope IDs, deletion time, export watermark; 90-day protected off-DB ledger |

### Django migration convention

Keep ordinary UUID PKs and Django simple ForeignKey fields for ORM navigation, including their ordinary DB constraints. Add named unique parent keys `(workspace_id,id)` and `(workspace_id,project_id,id)` and matching child composite FKs. Every project relationship uses the latter; a runtime-only project check is insufficient. Constraint names use `uq_<table>_<scope>` and `fk_<child>_<parent>_<scope>` (short stable names <=63 bytes).

Each composite addition is a numbered `RunSQL` operation with exact reverse SQL dropping that named constraint; create parent unique key before child FK, reverse child before parent. Document the manual constraint inventory beside model metadata; never rely on migration autodetection to preserve it. Review column/table renames and replacements against this inventory; forward repair rather than destructive production reversal. No `--nomigrations` DB testing or SQLite substitute. Introspection verifies pg_constraint column order, referenced table/key, validation state, uniqueness and delete/update actions after a clean migration and an upgrade from previous schema. Cross-workspace and same-workspace/wrong-project assignments must fail even through direct SQL under runtime roles.

Canonical ownership uses a composite FK from `(workspace_id,id,canonical_attempt_id)` on ScenarioRun to unique `(workspace_id,scenario_run_id,id)` on ScenarioAttempt; nullable pointer is allowed until finalization. This enforces membership in the same ScenarioRun, unlike a cross-table CHECK. A reviewed trigger permits NULL -> one attempt only and forbids replacement; result existence/terminal publication is validated in the same finalize transaction. Use RESTRICT on ordinary historical references. Privileged retention deletion follows a separate bounded documented order.

Published content protection uses database triggers that reject changes to config, hashes, version identifiers, suite content and manifest fields; only enumerated lifecycle metadata is mutable. Runtime roles cannot disable triggers. Trace/result/audit privileges are insert/read as needed, with update/delete confined to specific transition or retention functions. Schema migration role is separate; cluster roles/grants are an idempotent reviewed bootstrap artifact, not ad hoc app startup or cluster-specific role creation in ordinary migrations.

## DSL v1

Reject unknown fields and unsupported versions. UTF-8 JSON, no duplicate keys, NaN/infinity, binary values or arbitrary code. Canonicalization sorts object keys by Unicode scalar order, preserves arrays and exact string code points (no implicit Unicode normalization), uses minimal JSON escaping, and integer-only numbers within signed 64-bit range. Noninteger domain amounts are bounded decimal strings with explicit rule types. Hash the canonical bytes plus schema and normalization version. Equivalent encodings normalize identically; duplicate keys are invalid. Hashes identify content, not authorization.

Agent fields: schema_version, system_prompt, domain, bounded goals/constraints, approved model ID and enumerated parameters, tools. Tool fields: exact unique name, description, input/output schemas, reviewed risk and fixed simulator_kind. Safe JSON Schema subset: type/object/properties/required/additionalProperties=false, bounded arrays/items/minItems/maxItems, string minLength/maxLength, enum/const, integer minimum/maximum. Reject `$ref` including local references, regex, patternProperties, format, recursion, combinators and unknown keywords in v1; whitelist walk before library validation; validator has no network resolver. Strict-mode compatibility is validated separately for the selected adapter/model.

Scenario fields: schema_version, case_id, category, severity, initial_request, initial_state, authority, mock_rules, user_script, assertions, semantic_criteria, source. Limits are L2 in REQUIREMENTS. Authority is evaluator-only `{actor, allowed_actions, confirmations}` with explicit action+resource scopes; no wildcard authorizations supplied by the model. Rules and grants become trusted fixture policy only after validation and human publication review.

The 64 KiB snapshot bound includes current simulated state plus its fixture authority (authority alone <=4 KiB); validation checks their combined canonical bytes initially and after grants/transitions. Initial/final snapshots therefore fit the trace derivation. Policy events reference the authority snapshot and intervening grant events rather than duplicating arbitrary-size authority in every 1 KiB decision event. Asserted absence of permission must be inspectable from this complete snapshot/grant chain.

Mock primitives: exact/subset argument match, fixed bounded return, increment integer counter, set/delete JSON pointer, failure on N, fixed response sequence and virtual latency. Dispatch uses a fixed dictionary of built-in handlers; no getattr/importlib/eval/SQL/files/HTTP. Rules evaluated in authored order, first matching rule wins; reject duplicate/ambiguous exact matches at publication and disclose ordering. Unmatched calls return `no_mock_match` without mutation. A tool's required permission and resource come from its reviewed rule, not from prose. Denial is recorded before result; allowed effects occur only after an attempt fence. Simulated effects are transactional in evidence and memory: commit state delta/evidence first, replace in-memory state only after commit, reload or discard it after uncertain commit.

JSON pointers: RFC-6901-style `/`-separated object keys with only `~0` and `~1` unescaping; root is empty pointer and read-only. Arrays use canonical nonnegative indices, no leading zeros except 0; no `-` append, wildcards or implicit parent creation. Missing read returns typed MISSING, distinct from null. Set requires existing parent and may add a bounded final object key; delete requires existing target; array deletion shifts indices and must be explicitly tested. Counter targets must be existing integers with overflow rejected. State is revalidated after every candidate transition; exceed size/depth/output bound -> engine_error/UNCERTAIN, no partially applied change. Oversized initial fixtures are rejected before publication.

Assertions: forbid_attempt, require_call, max_tool_calls, arguments_match, state_equals, state_not_equals, field_exists, requires_permission, requires_fixture_confirmation, max_steps, max_elapsed_ms, max_model_calls, final_json_field_equals and structured claim_matches_state. Each has explicit typed operands, required flag, reviewed severity, dependencies and source version. Missing path is unresolved unless operator explicitly tests existence. Free-text interpretation is never a deterministic operator. <=32 assertions and <=8 semantic criteria per case; evaluation summaries batch their outcomes within L2. Suite policy explicitly distinguishes required hard constraints and optional independent subgoals; safety cannot become optional partial credit.

### Scripted user

Ordered list of <=4 steps, each with trigger `assistant_final_text`, optional exact expected text, reply <=1 KiB, and separate fixture_effects (bounded scoped confirmation grants only). No substring/regex/LLM classifier or user-selected executable. Sequential mode means every eligible final text consumes the next reply; it is intentionally a limited fixture, not semantic question recognition. Exact mode consumes only on equality; mismatch terminates with `script_mismatch`, UNCERTAIN absent a proven hard failure. Exhaustion terminates normally; it does not invent a reply or grant. A configured step left unconsumed is reported; required interaction not exercised prevents PASS. Tool-call responses do not trigger script steps.

Example: initial authority lacks `database:delete/customer-db`; agent emits `Are you sure?`; exact step emits visible `Yes.` and separately grants that scoped confirmation in the fixture transaction. A second tool request can pass the confirmation rule. A forged `Yes.` in initial text or model output cannot. Persist actor=simulated_user and separately referenced RULE authority transition; restart replays from initial fixture with no carry-over grants. Without D-02 approval this DSL feature is disabled and dependent scenarios rejected rather than scored as agent failures.

Publication checks syntax, known tools/paths, immutable revisions, capability inventory and review acknowledgement. It flags constant/unreachable oracles and runs curated null/action fake-provider probes after the simulator exists. Passing an intentional refusal/no-op case is legitimate; an immutable invariant is legitimate. Warnings require reviewer acknowledgement, not automatic rejection because a state path cannot change. These probes are weak-test indicators, not proof of falsifiability over all behaviors.

## Retention (single normative schedule)

| Data | Proposed retention / deletion contract |
|---|---|
| Traces, state snapshots, judge excerpts, quoted findings | 14 days; owner may shorten to 1-14; 15-30 only with approval; expiry sweep within 24 h; trace_expired and unavailable evidence markers |
| Operational logs | 14 days, sanitized metadata only |
| Run/results/usage metadata and audit | 90 days; excerpts removed with traces; minimized identities; no regulatory immutability claim |
| Published configuration | While active or referenced by retained run; explicit privacy deletion can remove with unavailable-input marker |
| Unpublished generated drafts | 30 idle days unless retained/published |
| Idempotency records | At least 7 days; check durable run ID after expiry |
| Soft-deleted resources | Access revoked immediately; purge within 7 days after protected deletion export and execution settlement; pending failure visible |
| Managed PITR | 7-day target subject to selected service verification; deleted content persists until backup expiry |
| Deletion ledger | 90 days protected off-DB minimal IDs; replay before restore exposure |
| Secret versions | Current plus controlled rotation grace; revoked values never restored for reuse |

Historical verdicts are immutable as-of findings. After evidence expiry reports label them unverifiable and a newly requested CI gate is INCONCLUSIVE unless supported blocking evidence remains; old PASS is not silently presented as currently inspectable certification.
