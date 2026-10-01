# Architecture Revision 2 - Dependency-ordered implementation plan

T-001 is APPROVED (Product Owner sign-off recorded 2 October 2026). T-002 is authorized and its foundation implementation is PARTIAL pending unavailable build/CI verification; see [T-002 evidence](evidence/T-002.md). T-003a and downstream ER-gated tasks remain BLOCKED pending D-07 ER assignment. All other implementation tasks remain NOT STARTED. Suffixes split baseline tasks without losing traceability; T-003, T-017, T-020, T-021, T-022, T-023, T-029, T-030, T-034 and T-036 are parent labels, not additional executable tasks. Rows below are in a valid topological order; listed dependencies are mandatory. Every task inherits applicable architecture contracts and its AC negative tests. All numbers/targets remain **PROPOSED - UNMEASURED UNTIL BENCHMARKED**.

Files below are future paths, not files created now. Each completion record must link source SHA, test command/result and reviewer; fake-provider evidence never passes a live/deployment gate. Every sensitive mutation from its first introduction follows T-004b atomic audit, tenant wrapper and permission checks. Experienced reviewer pairs on T-003a/b, T-013, T-017a/b, T-020a/b, T-022b, T-023a/b, T-034a/b, T-036a/b/c and first restore; review is not deferred to launch.

## Foundation, DSL and immutable inputs

| Task / purpose | Dependencies | ACs | Future output / tests and stopping point |
|---|---|---|---|
| T-001 Approve Revision 2 and open decisions | None | AC-040 | APPROVED (Product Owner sign-off 2 Oct 2026); D-01..13 recorded in PROJECT_BRIEF.md; D-07 amended: reviewer assignment required before T-003a begins (T-002 explicitly allowed to proceed without ER) |
| T-002 Minimal repository, offline CI and safe foundation | T-001 | AC-029, AC-031, AC-037, AC-043 | app/tests/manifests/lockfile/local fake DB runtime/CI; structured logs+IDs+exception scrubbing, startup debug/admin/cookie/role/policy checks, import boundary lint, migration timeout convention; clean build and synthetic secret/debug rejection; no live keys |
| T-003a Tenant tables, wrapper and composite constraints | T-002, ER assignment (D-07) | AC-009, AC-017, AC-018 | tenancy/models/migrations; mandatory ER gate (real named reviewer assigned/available before start); explicit transaction wrapper, simple+composite FK inventory/reverse SQL, project constraints; clean+upgrade migrated schema introspection, wrong-tenant/project failures |
| T-003b RLS, bootstrap roles and pooling guards | T-003a | AC-009, AC-017, AC-043 | Enable/force RLS before any feature exposure; actual-role grants, auth bootstrap function, null-context guard; physical connection reuse/rollback/autocommit/thread/lazy-read failures; no auth-table access for worker |
| T-004b Audit module and mutation convention | T-003b | AC-028 | operations/audit + migration; append-only redacted audit, atomic service boundary, bootstrap/operator events; forced insert failure rolls back action; required before T-004/T-005 |
| T-004 OIDC/session lifecycle | T-004b | AC-016, AC-028, AC-037 | identity integration; in-process fake IdP fixture with fixed synthetic signing keys/JWKS and callback errors; issuer/audience/signature/state/nonce/PKCE/replay/logout/expiry tests. Staging real IdP validation deferred to T-036b |
| T-005 Roles, invitations and revocation | T-004 | AC-009, AC-016, AC-017, AC-028 | permission services; last-owner race, verified invite one-use, owner/member matrix; dispatch control revocation epoch and cancellation intent, end-to-end cancellation verified in T-022b |
| T-006 Scoped CI credentials | T-005 | AC-016, AC-017, AC-028, AC-032 | token hash/scopes/expiry/revocation; trace denied by default, no cookie fallback, worker denied SELECT; no secret replay |
| T-007b Freeze DSL v1 and limits fixtures | T-001, T-002 | AC-008, AC-020, AC-035, AC-041, AC-042 | docs/spec + schemas/fixtures for agent/scenario/suite/mock/assertion/authority/script/pointers/canonicalization; approve D-01/02/04 semantics, normalization vectors and L2 arithmetic; no execution module invents its own DSL |
| T-008 Bounded agent/schema validator | T-003b, T-007b | AC-020, AC-035, AC-042 | catalog validator; whitelist before schema library, static/aggregate request/model compatibility; unknown fields/refs/regex/depth/UTF-8 bombs rejected. Proposed <=200ms validation of maximum 1MiB hostile input on chosen CPU measured later; parsing and validation independently bounded |
| T-007 Immutable agents | T-005, T-008 | AC-014, AC-018, AC-028 | catalog agent publish + DB immutability triggers; hash vectors, If-Match/duplicate-label/tamper tests; content stays immutable |
| T-009 Scenario drafts and scripts | T-007, T-007b | AC-008, AC-018, AC-041 | catalog scenario API; typed authority, paths, scripts/grants, revisions, static oracle warnings; forged consent/mismatch/oversize validation |
| T-010 Immutable suite publication | T-009 | AC-008, AC-014, AC-018, AC-028 | snapshot service/policy; same-project FKs, review acknowledgement, mixed revision/case/ordinal conflicts. Publication remains unavailable to users until weak-test probes T-010b integrated |

## Deterministic engine, evidence and accounting

| Task / purpose | Dependencies | ACs | Future output / tests and stopping point |
|---|---|---|---|
| T-011 Pure simulator | T-008, T-010 | AC-002, AC-006, AC-020, AC-035 | fixed registry, bounded pointer/state transformations, attempt before policy; denied/allowed deletion/money/email remain in-memory, rollback candidate on limits |
| T-012 Faults and sequential batches | T-011 | AC-003, AC-035 | failure-on-N, fixed sequences/malformed payload, virtual latency; identical fixtures yield identical state/event order |
| T-013 Persisted redacted evidence | T-003b, T-004b, T-012 | AC-007, AC-013, AC-025 | trace schema/serializer/chunks/sequence counter; 112-event/808KiB maximum fixture, redaction/gap/ref/expiry metadata, canaries, failed persistence and commit-ack loss |
| T-014 Pure deterministic rules | T-013 | AC-002, AC-004, AC-006, AC-022 | evaluator required dependencies and sufficient failure evidence; state/authority/structured claim checks with persisted refs |
| T-014b Author deterministic golden corpus | T-007b, T-014 | AC-001, AC-003, AC-008, AC-021, AC-022, AC-036, AC-041 | Explicit owner authors >=100 independent expected fixtures, >=30 safety, scripts, incomplete evidence, denied-success claims, legitimate retries and oracle counterexamples; versioned labels separate from implementation output |
| T-015 Loop/retry heuristics | T-014b | AC-001, AC-003 | 8 unchanged tuple stop, versioned threshold; pagination/state-change negatives; alternate-pattern misses documented as known limits, not claimed detections |
| T-016 Total verdict/gate policy core | T-015, T-014b, T-001 | AC-022, AC-023, AC-025, AC-036 | Pure exhaustive truth table incl blocking/advisory MODEL FAIL, missing dependencies, optional zero/some/all, evaluator error; no default PASS. Product D-01 resolved before freeze |
| T-017a Ledger, estimator and atomic budgets | T-013, T-003b, T-004b | AC-012, AC-034 | usage models/locks/rates/byte bound/holds; exact rounding, concurrent boundary/period transfer/known settlement tests, no double-counted admission+dispatch |
| T-017b Unknown settlement and integrity | T-017a | AC-012, AC-029, AC-034, AC-044 | 2h auto-estimate, idempotent late adjustments, platform aggregate reports, bucket rebuild, kill guards; midnight/repeated import/unattributable credit tests; no live report API needed, fake exports suffice |
| T-018 Provider interface and fake transport | T-008, T-017b | AC-011, AC-035 | typed text-v1 DTO/errors/refusal/usage; deterministic fake transport and controllable clock, no network requirement |
| T-019 Offline approved provider adapter | T-018 | AC-011, AC-012, AC-020, AC-035 | Exact wire positive allowlist and fixed endpoint, output/framing bound conformance, SDK retries/redirects off, error canaries; fake HTTP only; exact model capabilities/rate inputs require verified registry |
| T-020a Durable queue, group fairness and claim | T-003b, T-017b | AC-010, AC-027 | narrow Job/group/counters, restricted cross-tenant functions, Job-first claim, round-robin workspace admission, slot limits; two claimers, saturated tenant/quiet tenant, backlog expiry |
| T-020b Heartbeat, fencing and worker supervision | T-020a | AC-010, AC-015, AC-029 | four processes/heartbeat connections/supervisor, owner+epoch+DB-clock checks, quarantine; pause/expiry/late heartbeat, no stale resurrection, bounded retry |
| T-021a Pure fixed loop and user script | T-012, T-016, T-018, T-007b | AC-001, AC-002, AC-006, AC-012, AC-035, AC-041 | fake provider/in-memory trace sink only; clarify->Yes->scoped grant, forged consent, mismatch/exhaustion, tool/refusal/byte/call/deadline cases |
| T-010b Publication weak-test probes | T-010, T-021a | AC-008, AC-018 | curated null/action fake probes, legitimate refusal/invariant exceptions and persisted human dispositions; integrates with publish before workflow is exposed |
| T-021b Fenced persistence integration | T-021a, T-013, T-020b | AC-010, AC-012, AC-019, AC-025 | runner with transaction boundary/state-memory commit handling, lease/cancel/dispatch guards, persisted dependency reads; DB outage stops effects/dispatch |
| T-035 Admission/rate/storage controls | T-017b, T-020b, T-010b | AC-012, AC-027, AC-042 | quote, request/workspace/global caps, trace holds/headroom, generation quota, no client cap escalation; concurrent admissions, stale telemetry, fair progress; fairness already part of queue |
| T-022a Durable start and idempotency | T-005, T-010b, T-021b, T-035 | AC-019, AC-028, AC-032 | browser-session start/quote/202 transaction; lost ack/body conflict/storage+budget rollback. No dependency on T-006 for browser flow |
| T-022b Two-phase cancel and revocation | T-022a | AC-016, AC-019, AC-028, AC-044 | parent-only cancel intent, standard-order child cleanup, control guards; queued/dispatch/response/evaluation/finalize races and audit-failure rollback |
| T-023a Canonical finalize | T-022b, T-016 | AC-010, AC-014, AC-015, AC-019 | same-ScenarioRun pointer FK/write-once trigger, full fence/parent winner, cancelled partial result; stale/duplicate/commit-ack/deadlock retry tests |
| T-023b Reaper and parent reducer | T-023a | AC-010, AC-015, AC-019 | independent ID discovery/recovery/reduction, parent-only lock, bounded attempts and absolute deadlines; child-commit crash, cancelled children, queue expiry, abandoned costs |
| T-024 Bounded semantic judge (fake first) | T-016, T-018, T-023b | AC-021, AC-022, AC-025, AC-036 | no-tool request from persisted shown subset; strict structured output/repair, mode snapshot, invalid/unshown refs and model drift, advisory cannot satisfy required semantics |
| T-024b Author/label semantic corpus | T-007b, T-001 | AC-021, AC-036 | Owner and two labelers produce >=200 held-out synthetic cases with calibration separation/adjudication/provenance. Required before T-042S/Option-A launch; may be deferred only under approved Option B |
| T-025 Queued generation | T-009, T-018, T-020b, T-035 | AC-008, AC-021 | bounded drafts/inventory/provenance, invalid/duplicate/partial output and metadata injection; fake only, no dependency on judge implementation |

## Controlled staging and user workflows

| Task / purpose | Dependencies | ACs | Future output / tests and stopping point |
|---|---|---|---|
| T-034a Secret plumbing with dummy keys | T-002, T-004b, T-019 | AC-013, AC-043 | tmpfs/secret aliases, role separation, no wire/debug/core/env dumps; local normal/error/crash canaries, no paid request |
| T-036a Local network and container proof | T-019, T-034a | AC-020, AC-037 | infra Compose/proxy/fixed relay/collector/firewall; worker namespace deny probes, dummy allowed endpoint, resource kill; reviewer pairs; no staging dependency |
| T-036b Authorized staging and egress proof | T-036a, T-035, T-001 | AC-016, AC-020, AC-037, AC-043 | Requires explicit spending/region/platform/privacy approval; synthetic staging DB/IdP; real private DB failover/denial/proxy paths with dummy model transport, signed network evidence; no model key or live call |
| T-034b Staging key injection / access proof | T-034a, T-036b | AC-013, AC-043 | Approved secret store/key injected without dispatch; web cannot read, known canaries scrubbed, revocation control tested offline. Live rotation probe deferred |
| T-036c First authorized live staging probe | T-019, T-017b, T-035, T-034b, T-036b, T-023b | AC-011, AC-012, AC-013, AC-020, AC-035 | Explicit approved model/privacy/rate/budget plus safe injection/network evidence; one bounded call, billed usage and output bound, rotation probe, fail-closed route. This is the first real-provider task |
| T-026 Component reports and metrics | T-023b, T-024, T-017b | AC-023, AC-034 | exact 80/10/5/3/2 arithmetic, empty/incomplete/all-fail, deduplicated labels, abandoned/unknown costs, scope and evidence availability |
| T-027 Case comparisons | T-026 | AC-005, AC-023 | exact95/100 transitions, equal aggregate/different failed cases, model-kind and repeat labels, incompatible manifests/returned judge drift |
| T-028 Replay and rerun | T-022a, T-026 | AC-007, AC-024 | zero ModelCalls/reservation mutations on replay, new IDs on rerun, expired/purged/model retired error tests |
| T-029a Catalog UI | T-005, T-007, T-009 | AC-018, AC-033, AC-037 | escaped project/agent/scenario forms, CSRF/stale edits/direct URL negatives |
| T-029b Review/publication UI | T-029a, T-010b, T-025 | AC-008, AC-018, AC-033 | oracle/script/authority review, coverage/probe warnings and explicit acknowledgement; no admin tool dependency |
| T-030a Run/report/compare UI | T-026, T-027, T-029b | AC-019, AC-023, AC-033 | separate execution/verdict/completeness, no run score/severity color, model and scope labels; poll/reconnect/cancel |
| T-030b Trace/rerun UI | T-030a, T-028 | AC-007, AC-024, AC-025, AC-033 | bounded trace/attempt selector, abandoned/expired/redacted visibility, no auto-fetch; browser E2E |
| T-031 CI contract/example | T-006, T-022a, T-027, T-016 | AC-032 | OpenAPI+minimal client, explicit scopes, persist returned ID; PASS/FAIL/INCONCLUSIVE exit mapping and retry/expiry tests |

## Operations and evidence

| Task / purpose | Dependencies | ACs | Future output / tests and stopping point |
|---|---|---|---|
| T-032 Audit coverage verification | T-006, T-010b, T-022b | AC-028 | Generated sensitive-action inventory and per-action forced audit failure; verifies early mechanism, not retrofits it |
| T-033 Retention/deletion | T-023b, T-028, T-032 | AC-025, AC-026, AC-028 | batch purge/storage release, minimal protected export/tombstone, immediate block; deletion/run/export-failure/restore replay tests; no privileged full backup |
| T-037 Dashboards, alerts and integrity jobs | T-023b, T-026, T-032, T-036c, T-017b | AC-029, AC-034 | health split, ledger/canonical detector, safe correlation, real primary+backup delivery; logs already exist from T-002 |
| T-038 Promotion and migration compatibility | T-030b, T-031, T-036c, T-037 | AC-031, AC-037 | immutable CI digest, bootstrap/migration role, expand/contract, drain; partial migration and previous-image rollback evidence |
| T-039 Managed restore and host rebuild | T-033, T-034b, T-036c, T-038 | AC-026, AC-030 | isolated timed PITR, latest deletion ledger/key recovery, roles/constraints/stale sessions/jobs/accounting; measured RPO/RTO, no app-host full-export credentials |
| T-040 Full security negatives | T-030b, T-032, T-034b, T-036c, T-038 | AC-009, AC-013, AC-017, AC-020, AC-037, AC-043 | URL-generated inventory, actual-role pool/FK tests, web/schema/egress/canaries/break-glass, reviewer sign-off |
| T-041 Durability/accounting fault schedules | T-023b, T-024, T-035, T-037 | AC-010, AC-011, AC-012, AC-015, AC-019, AC-025, AC-034 | All TEST_STRATEGY schedules + cancellation lock audit, unknown settlement/late aggregate reports; inspect tables, not just HTTP; incremental subset ran with T-023 |
| T-042D Deterministic and advisory release validation | T-014b, T-015, T-016, T-024, T-025 | AC-008, AC-021, AC-022, AC-036, AC-041 | >=100/30 corpus100%, generator coverage and advisory injection/citation safety, finite-set report and pinned versions |
| T-042S Blocking semantic validation (conditional) | T-024b, T-024, T-036c | AC-021, AC-036 | Held-out live judge outputs, category confusion/recall/agreement/abstention; required for Option A or later promotion; no calibration on held-out labels |
| T-043 Capacity, limits and storage benchmark | T-033, T-035, T-037, T-041, T-036c | AC-027, AC-034, AC-038, AC-042 | steady60min, slowdown15min, 100-run admission burst, max300-unit bounded fake profile, separately funded live representative profile; heartbeat gap<30s, measured rows/index/WAL/connection use, limits arithmetic |
| T-044 All incident drills and kill switches | T-037, T-039, T-041, T-043 | AC-029, AC-039, AC-044 | All eleven containment/recovery exercises, global/workspace/key stop within one heartbeat, primary/backup and break-glass evidence; no secrets in notes |
| T-045 Production go/no-go | T-031, T-038, T-039, T-040, T-041, T-042D, T-043, T-044; T-042S if Option A | AC-040 (coverage audit AC-001..044) | All G-01..21 and applicable G-07 subgates, current model/price/privacy/identity fit, clean smoke, signed residuals. No-go if any required evidence missing |

## Milestones and proof ownership

Foundation through T-010: offline identity/tenant/DSL/immutable inputs, publication gated until T-010b. Deterministic/durable engine through T-025: fake providers only. Secret/network tasks are an explicit staging branch; T-036c alone opens live integration after controls. User workflow tasks can use fake transport regardless of live branch progress. Operations gather evidence, then T-045 is a separate launch decision.

T-042 means parent label for T-042D/T-042S, not an undefined hidden task. Conditional T-024b/T-042S remain in backlog even under Option B; they are not needed for advisory launch but cannot be skipped when changing policy. Plan dependency analysis must resolve each suffix exactly, detect cycles, and verify every task has ACs and every AC has a test/evidence path. Infrastructure not yet available is an explicit output of authorized T-036b, never assumed by an earlier local task. No paid provisioning is authorized simply by architecture acceptance.
