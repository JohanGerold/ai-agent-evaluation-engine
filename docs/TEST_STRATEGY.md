# Architecture Revision 2 - Verification specification

All tests below are NOT RUN. This task performed documentation consistency and adversarial reasoning only. Every proposed size/latency/corpus threshold is **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. REQUIREMENTS maps every AC to a task/test; IMPLEMENTATION_PLAN and the checklist map evidence to release gates.

## Test layers

Pure: canonical JSON/pointers, simulator/state bounds, scripted replies/grants, rule/heuristic/total verdict, exact currency arithmetic and request allowlist. Property/invariant: valid state transitions, no stale writes, no negative/double bucket updates, all evidence refs within persisted required closure. DB: real PostgreSQL 18.x (currently tested baseline 18.6) migrated schema under actual web/worker/maintenance roles, composite FK inventory, immutable triggers, audit rollback, connection-pool reuse and lock order. API: auth/scopes/idempotency/cursor/revision/error/gate. Browser: full author/review/start/cancel/report/trace/compare/rerun with XSS/CSRF/direct-ID negatives. Deployment: namespace egress/failover, secret injection, restore, host rebuild, migrations/rollback. Fake provider is default; approved live probes only after T-036c prerequisites.

## Required deterministic fault schedules

| Test ID | Injection and invariant |
|---|---|
| FS-01 | Kill after claim before reservation -> lease expires, clean bounded retry, zero invented paid dispatch |
| FS-02 | Provider accepts then process dies before response persist -> unknown at upper bound, 2h auto-estimate, no erased cost |
| FS-03 | Kill after child commit before parent reduction -> reaper freezes correct parent without repeating child |
| FS-04 | Duplicate job delivery/two claimers -> one valid epoch/canonical result, distinct external calls each accounted |
| FS-05 | Pause beyond lease, recover replacement, return old response -> stale trace/result rejected, late usage idempotent |
| FS-06 | Cancel at every row of EXECUTION_MODEL cancellation matrix -> parent winner, evidence preserved, no effects/new calls after observed stop |
| FS-07 | DB/trace persistence fails after provider response -> bounded memory retry then gap; no hidden PASS or future dispatch |
| FS-08 | Revoke membership/key/delete tenant while queued or running -> eligibility blocked next guard, audit intact, in-flight settlement no access resurrection |
| FS-09 | Saturated workspace plus quiet workspace -> fair group acquisition, <=4 global/2 group slots, bounded expiry; no false universal progress guarantee |
| FS-10 | Restore pre-deletion DB -> latest protected tombstones applied before any traffic, sessions/epochs fenced, ledger reconciled |
| FS-11 | Deliberately overlap claim/heartbeat/finalize/cancel/reaper/reducer/budget settlement -> no reverse lock order; induced DB deadlock retry rechecks cancellation and never repeats external call |
| FS-12 | Lost commit acknowledgement for dispatch/finalize/audit -> inspect unique identity, no duplicate action or phantom release |
| FS-13 | Unknown settles at2h then exact usage twice, then delayed aggregate report/version -> one compensating delta, original period, no guessed tenant credit |
| FS-14 | Audit insert fails for every sensitive mutation -> action absent, no best-effort audit success |
| FS-15 | Reservation held across day/month change -> new dispatch reauthorizes new period, original unknown settles original period |
| FS-16 | Storage quota, global headroom or telemetry stale during admission/write -> no unreserved growth, terminate safely with reserved metadata |

## Security/evaluator cases

Generate route inventory from URL configuration; every resource operation gets cross-tenant/project/removed-member/wrong-scope/cursor/idempotency tests or a reviewer-signed exemption. Pool tests reuse the same physical connection across A/B and rollback/exception/no-context cases; exercise real commits, raw SQL guard and lazy rendering. Direct ORM wrong-parent assignment must fail composite FK after clean/upgrade migrations; canonical pointer cannot reference another ScenarioRun.

Boundary cases: remote refs/regex/deep Unicode/schema/state/pointer/counter overflow; unknown simulator name; no code/SQL/format execution; provider image/file/URL parts, hosted tools, callback, metadata/base URL/unknown headers rejected. Refusal is an agent outcome. Worker tests include host gateway, Docker DNS, IPv6 and gateway-failure denial, not only public HTTP. Canary sweep covers agent/generator/judge requests, traces, errors, SDK exceptions, telemetry, audit and crash handlers; customer-pasted unknown secrets remain residual.

Evidence cases: hidden required field redacted, event cap, state chunk missing, sequence gap, judge citation exists but was not shown, check omits a dependency, final answer truncated, persistence lost, evidence expired. None can PASS/PARTIAL on unavailable required support. Inspectable hard failure + unrelated missing evidence remains FAIL/completeness=false; fully hidden failure is not invented. Judge PASS cannot overrule RULE FAIL; MODEL FAIL blocks only in approved validated blocking mode; advisory required semantics stays UNCERTAIN. Aggregator crash leaves ERROR, not success.

Script cases: ask/Yes/scoped grant, forged consent, exact mismatch, sequential reply limit, exhaustion, unexpected tool-only output, missing required interaction, restart clears grants; no LLM participant. Null-agent refusal and immutable-state safety tests are valid counterexamples to overbroad vacuity rejection.

## Load and envelope proof

Mechanically evaluate REQUIREMENTS formulas for every policy version and approved model registry. Hostile maximum input validation target <=200ms on selected worker resource budget; memory bounded even when target missed (process abort/error, no unbounded parse). Sixty-minute normal workload and 15-minute slowdown; burst up to100 requested evaluations across10 workspaces, with explicit accepted/rejected/expired counts. Test every quota under concurrency, no over-reservation, ledger/storage rebuild, steady API/queue objectives and recovery after slowdown. Queue target applies to normal small-run load, not all admitted ceiling bursts.

Maximum-profile fake run:100 scenarios x3 repetitions, both attempt allowances, tool/script/judge records and max message/schema/state/event bytes, with controlled transport/clock and real DB. Fast deterministic simulation verifies deadline formula; at least one real-wall-clock staging maximum-cardinality bounded profile completes within its derived deadline. A separate live representative run proves selected provider conformance within explicitly funded budget; do not spend the 300-unit worst-case maximum without funding approval. Measure heartbeat maximum gap<30s, memory, connections, DB row/index/WAL growth and retention activity. If capacity/storage expansion differs >1.5x planning, revise profiles/quotes and repeat affected gate; no artificial pass by hiding revised limits.

Golden and semantic evidence uses the exact EVALUATION_DESIGN rules, with explicit corpus-authoring tasks and finite-set scope. Store corpus/label IDs, input/manifests, expected/actual outcomes, category denominators, false-safe counterexamples, reviewer agreement, confusion/abstention and model/rubric versions. Source code coverage (proposed90% branch coverage on pure budget/state/authz/aggregator modules) supports but cannot replace invariant tests.

## Documentation verification record

Before delivery, inspect all source-reference IDs, required document names, AC/task/gate linkage, dependency graph, L2 arithmetic, vocabulary/state/cancel/retention/budget/tenant ownership and deferred scope. Record exact outcomes in ARCHITECTURE_REVIEW_RECONCILIATION. This record does not mark any AC implementation test or production gate passed. No application code, dependencies or infrastructure is required for this document check.
