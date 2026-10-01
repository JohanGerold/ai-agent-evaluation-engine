# Architecture Revision 2 - API and permissions

Architecture proposal only. `/api/v1/workspaces/{wid}` is the tenant prefix. All numbers are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. Identity -> active membership -> action -> same-workspace/project resource is mandatory, with SECURITY's tenant transaction wrapper. IDs are never authority.

## Common contracts

Bounded JSON only. Safe errors `{error:{code,message,fields},request_id}`: 400 malformed, 401 bad identity, 403 forbidden action within authorized scope, 404 missing/inaccessible reference, 409 state/idempotency/model unavailable, 412 stale revision, 413 size, 415 type, 422 incompatible DSL/profile, 429 admission quota, 503 required dependency unavailable. No SQL/provider secrets/raw output in errors. Signed scope/filter-bound cursors, default 50/max100. Mutable PATCH requires If-Match; no published-content PATCH. Expensive start/generation/publish/rerun requires scoped Idempotency-Key retained >=7 days; same body returns original resource, changed body 409. Token issuance never replays token secret.

| Action | Owner | Member | CI |
|---|---|---|---|
| Workspace read / all project content | Yes | Yes | Only published/run data in bound project |
| Rename, quota/retention within maximum | Yes | No | No |
| Invite/revoke/transfer, issue/revoke CI | Recent-auth owner, last-owner protection | No | No |
| Project/agent/scenario edit and publish | Yes | Yes | No |
| Start / rerun | Yes | Yes | evaluation:start in bound project |
| Cancel | Any own-workspace run | Any own-workspace run | evaluation:cancel, token-created run only |
| Reports / comparison | Both runs authorized | Both runs authorized | evaluation:read, bound project |
| Trace | Yes | Yes | Denied by default; explicit trace:read only |
| Audit read | Own workspace | No | No |
| Workspace delete | Recent auth + typed confirmation | No | No |
| Provider secret plaintext | Never | Never | Never |

Platform operator access is separate and audited, not a third tenant role. Invitations use owner-copied links initially; no email service dependency. Identity provider owns recovery, no local password scheme.

## Routes

| Operation | Contract / atomicity |
|---|---|
| POST projects; POST projects/{pid}/agents; PATCH agents/{id} | Bounded catalog/draft and revision; workspace uniqueness, audit sensitive mutations |
| POST agents/{id}/versions | label+expected draft revision ->201 immutable ID/hash; full DSL/model/profile validation + snapshot + audit |
| POST projects/{pid}/scenario-generations | approved version+categories+count ->202 job; reservation, quota, audit; validated drafts only |
| POST projects/{pid}/scenario-drafts; PATCH scenario-drafts/{id} | Typed DSL including script/authority; 201/200 revision; no execution |
| POST test-suites/{id}/versions | drafts[{id,revision}]+policy+review acknowledgement ->201 hash; same-project copies; weak-test warnings explicitly acknowledged |
| POST projects/{pid}/evaluation-quotes | version IDs+repetitions+profile -> quote ID/expiry/hash, units, deadlines, token/money/storage maxima and available capacity; no model calls; server rate-card version |
| POST projects/{pid}/evaluations | quote ID+matching inputs+budget mode/cap ->202 durable ID, QUEUED, units, poll URL, manifest hash; atomic eligibility/idempotency/hold/run/children/jobs/audit |
| GET evaluations/{id}; GET evaluations/{id}/report | execution status, termination, progress, verdict counts, required completeness, current evidence availability, exact/estimated/unknown cost, scope; provisional flag until terminal |
| POST evaluations/{id}/cancel | reason ->202 CANCELLING; terminal ->200 existing state, cancel_applied:false; phase-1 parent+audit then asynchronous child cleanup |
| GET scenario-runs/{id}/trace | Cursor and attempt selector; canonical vs abandoned clearly separated; 410 expired, 404 unauthorized |
| POST projects/{pid}/comparisons | baseline/candidate/policy -> diff, deciding evidence kinds, repetition count, changed axes and compatible/confounded status; zero new model calls |
| POST evaluations/{id}/reruns | subset/repetitions/new quote ->202 new evaluation; 410 purged input, 409 unavailable model; old manifest immutable |
| GET evaluations/{id}/gate | Gate truth table below; current availability assessed; no new model calls |
| POST api-credentials | project/scopes/expiry -> token shown once, safe prefix/ID; recent auth, safe audit |
| POST members/invitations; POST invitations/{token}/accept | Verified target, hashed one-use, expiry, rate limits, atomic audit; no owner role input |
| DELETE members/{user_id} | Last-owner lock; token revocation and dispatch eligibility revocation atomic with audit; cancellation fan-out after commit |
| DELETE workspace | typed confirmation+revision ->202 deletion ID; immediate access block, cancel, tombstone/audit, protected export before purge |

Quote is advisory until start transaction revalidates prices, inputs, permissions, periods, storage and budgets. Expired or changed quote ->409 re-quote, no silent budget increase. Full-envelope admission requires all declared maxima funded; exploratory mode explicitly permits INCOMPLETE when cap hits. CI tokens cannot increase workspace/platform caps; preauthorized project budget policy bounds starts. Full maximum cardinality is not a promise of maximum-cost affordability.

Representative start: `{agent_version_id, suite_version_id, repetitions:1, quote_id, budget_mode:"full_envelope", max_cost_usd:"owner-approved-exact-decimal"}`. The textual money placeholder is illustrative, not a valid request value; implementation schema uses bounded decimal money. Response includes planned_scenario_runs, deadline_policy_version and queue_expires_at; execution_deadline_at is assigned once a group is allocated.

Gate response: `{gate:PASS|FAIL|INCONCLUSIVE,reasons,blocking_case_ids,completeness,evidence_available,comparison_compatibility,semantic_mode,deciding_evidence_kinds,scope}`. EVALUATION_DESIGN is authoritative: known supported blocking failure ->FAIL even with incomplete work; otherwise incomplete/uncertain/cancel/error/unavailable ->INCONCLUSIVE; only complete allowed outcomes ->PASS. CLI exits 0/1/2. No gate-name change to NO_BLOCKING_FINDINGS; scope and provenance prevent ambiguity without breaking vocabulary.

## Internal interfaces and versioning

ModelProvider accepts immutable text-v1 DTO/deadline/dispatch ID, returns typed text/function calls/refusal/usage/error; no credentials in prompt DTO. Simulator accepts fixture/state/call and returns pure candidate delta and events. RuleEvaluator/HeuristicDetector accept persisted evidence and return versioned findings. Judge request builder accepts trusted rubric and persisted sanitized excerpts. JobStore claim/renew/finalize and UsageGateway reserve/settle enforce EXECUTION_MODEL transactions, not caller conventions. No provider use outside the shared gateway.

Additive optional API fields are allowed; new required fields or changed meaning need versioned contract and proposed 90-day migration notice. This is a preimplementation revision, so there are no deployed v1 clients to migrate. Route inventory generated from URL configuration drives negative tenant/scope/cursor/idempotency tests or explicit reviewed exemptions. Include cross-project references, removed memberships, last-owner/invite races and trace revocation.
