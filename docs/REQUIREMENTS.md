# Architecture Revision 2 - Requirements

Status: proposed architecture only, 1 October 2026. All initial numerical limits and targets are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**; product approval and production evidence are separate.

## Acceptance criteria

Stable AC-001 through AC-040 retain their baseline intent with the explicit corrections below. The table provides an implementation and test path for every criterion; all tests are specifications, NOT RUN. Task details and dependencies are in IMPLEMENTATION_PLAN.

| AC | Required observable outcome | Implementation / verification path |
|---|---|---|
| AC-001 | Eight consecutive identical tool/arguments/state tuples flag probable loop and stop; changing state/pagination are negative examples; hard limits independent | T-015, T-021a; golden loop fixtures, T-042 |
| AC-002 | Unauthorized destructive intent is persisted before denial; no real effects; guard success never erases unsafe attempt | T-011, T-014; authority goldens, T-040 |
| AC-003 | Injected tool failure and provider outage are distinct; bounded recovery with evidence | T-012, T-015, T-019; T-041 |
| AC-004 | Failed state transition plus structured success claim fails deterministically; prose judgment stays MODEL | T-014, T-024; T-042 |
| AC-005 | Same-suite 95/100 baseline comparison lists exact newly failing case IDs, evidence kind, changed axes and repetition counts | T-027; paired comparison fixtures |
| AC-006 | Fixture authority alone authorizes effects; text claiming consent cannot grant it | T-011, T-014, T-021a; forged-consent tests |
| AC-007 | Authorized paginated ordered trace exposes messages, calls, states, errors, findings, gaps and expiry; no hidden reasoning | T-013, T-028, T-030b; trace round trip / E2E |
| AC-008 | Generated/manual scenarios validated, coverage gaps visible, human review required before immutable publication | T-009, T-010, T-025, T-029b; T-042 |
| AC-009 | Every route, nested reference, worker path, cursor, count and comparison denies other tenants using actual runtime DB roles | T-003a/b, T-005; generated route inventory T-040 |
| AC-010 | Duplicate delivery/stale epoch cannot overwrite canonical results; distinct paid dispatches remain distinct | T-020a/b, T-023a/b; T-041 |
| AC-011 | Timeout/429/5xx/protocol error use bounded classified retries, breaker and honest infrastructure status; no silent failover | T-018, T-019; T-041 |
| AC-012 | Reserve before dispatch under all relevant call/token/money caps; no negative/double counters or bypass | T-017a/b, T-035; concurrent ledger schedules T-041 |
| AC-013 | Platform canaries absent from prompts/traces/logs/errors/telemetry; worker-only key and rotation/revoke verified | T-002, T-013, T-034; T-040 |
| AC-014 | Immutable input hashes/manifests and prior results survive edits; deletion explicitly marks unavailable history | T-007, T-010, T-023a, T-033; DB tampering tests |
| AC-015 | Worker death preserves committed children, fences attempts, recovers at most once with accounted uncertainty | T-020b, T-023b; T-041 |
| AC-016 | OIDC/session expiry/logout/revocation correct; removed principal's tokens revoked and queued/running work cancelled at next guard | T-004, T-005, T-006, T-022b; revocation races |
| AC-017 | Owner/member/CI matrix enforced; no last-owner removal, scope escalation or worker access to auth tables | T-003b, T-005, T-006; T-040 |
| AC-018 | If-Match stale writes return 412; DB protects published content; publication snapshots revisions atomically | T-007, T-009, T-010; concurrency and migration tests |
| AC-019 | Durable 202 start; two-phase cancellation preserves committed evidence and stops future dispatch/effects at guards | T-022a/b, T-023a; cancellation matrix T-041 |
| AC-020 | No customer code/import/regex/ref/fetch; worker direct egress fails; only allowlisted text request surface | T-008, T-011, T-019, T-036a/b; T-040 |
| AC-021 | Judge/generator injection cannot change authority, budgets or publication; invalid refs/outputs yield uncertainty | T-024, T-025; adversarial corpus T-042 |
| AC-022 | Total precedence includes semantic FAIL under approved blocking policy, missing evidence, errors and partials; provenance retained | T-016; exhaustive truth table T-042 |
| AC-023 | Counts/denominators/missing units, safety intent, unknown cost, scope statement and evidence kinds; no run score/color implying safety | T-026, T-027, T-030a, T-031; worked arithmetic and UI review |
| AC-024 | Replay creates zero ModelCalls/reservations; rerun creates new run and budget authorizations | T-028; DB before/after assertions |
| AC-025 | Persisted evidence dependency closure determines completeness; redaction/truncation/missing required data forbids PASS/PARTIAL | T-013, T-016, T-033; T-041/T-042 |
| AC-026 | Immediate deletion access revocation; protected tombstone before purge; restore replay prevents resurrection | T-033, T-039; export failure and restore tests |
| AC-027 | Fair bounded queue, tenant/global admission and retained-trace quotas preserve progress without oversubscription | T-020a, T-035; adversarial load T-043 |
| AC-028 | Every sensitive mutation and safe audit event commit or roll back together; credentials never appear in audit | T-004b, T-032; failure injection at each mutation |
| AC-029 | Early sanitized correlation logs/startup validation; readiness separates DB, worker, provider; named alert delivery | T-002, T-037, T-044; incident reconstruction |
| AC-030 | Isolated managed restore and host rebuild meet approved RPO/RTO with deletions, RLS, sessions and stale jobs checked | T-039; timed measured drill |
| AC-031 | Reproducible digest, compatible migrations, failed-migration repair and prior-image rollback proven | T-002, T-038; deployment drill |
| AC-032 | Project-scoped expiring CI token, idempotency, cursors, error DTOs and total gate; no green on unknown/infra | T-006, T-022a, T-031; CI contract tests |
| AC-033 | UI covers author/review/publish/start/cancel/report/trace/compare/rerun without admin | T-029a/b, T-030a/b; browser E2E |
| AC-034 | ModelCall/ledger idempotency, versioned rates, timed unknown settlement, late corrections and aggregate reconciliation | T-017a/b, T-037; ledger rebuild T-041 |
| AC-035 | Bounded strict parsing rejects malformed tools/provider output with preserved safe evidence and unchanged state | T-008, T-012, T-018, T-019; hostile inputs |
| AC-036 | Versioned deterministic corpus and applicable semantic gate; finite-set performance disclosed, no assumed generalization | T-014b, T-024b, T-042 |
| AC-037 | Escaping/CSP/CSRF, locked build, no unsafe debug/admin, restricted containers and safe CI | T-002, T-036a/b, T-038, T-040 |
| AC-038 | Approved steady/burst/max-profile load, quota boundaries and heartbeat jitter measured; replace estimates | T-043 |
| AC-039 | All eleven major runbooks exercised before release; real primary/backup owners | T-044 |
| AC-040 | Named architecture/product/reviewer/operations decisions and linked AC/gate evidence before launch | T-001, T-045 |
| AC-041 | Clarification script is deterministic, bounded and separate from authority; missing/mismatched replies are honest outcomes | T-007b, T-009, T-021a; clarification corpus |
| AC-042 | Envelope arithmetic and adversarial maximum serialization/event/storage/deadline tests remain coherent | T-007b, T-008, T-035, T-043 |
| AC-043 | Admin/debug absent; audited expiring break-glass; unsafe startup rejected; operator consoles MFA | T-002, T-034, T-040 |
| AC-044 | Global stop, workspace pause and key revocation stop new dispatch at every guard, with bounded in-flight charges | T-017b, T-022b, T-034, T-044 |

## Derived operating profile L2

These are interacting ceilings, not entitlements to unlimited transcript growth. Compatibility validation checks the whole serialized request, not each tool independently. Inputs that cannot fit the first request are rejected before publication/start. Later transcript exhaustion is explicit INCOMPLETE/UNCERTAIN unless an independently evidenced failure exists. No silent context truncation or summarizing LLM is allowed.

| Dimension | Proposed L2 limit and response |
|---|---|
| Input | JSON only, 1 MiB HTTP body; no files/archives; 413/415 |
| Agent tools | 20 tools; each input/output schema pair <=2 KiB; all tool definitions including descriptions <=6 KiB; total static provider-visible content <=8 KiB |
| Schema / state | Schema depth 8, 100 properties/tool, 1,000 total nodes; no refs/regex; state <=64 KiB, depth 8, pointer <=8 segments/256 UTF-8 bytes; transition result <=4 KiB |
| Conversation | Initial request plus appended messages/tool results/script replies <=8 KiB serialized; exact final request variable fields <=16 KiB; <=64 messages; stop before overflowing |
| Provider tokens | Conservative input estimate <=20,480 (16,384 bytes + 4,096 framing allowance); output <=1,024 billable tokens including reasoning; chosen model must support input + output >=21,504 |
| Agent execution | 8 logical turns; max 2 transport dispatches/turn; 16 tool calls/attempt, sequential; <=2 judge dispatches total/attempt including repair; <=18 total dispatches/attempt |
| Recovery | <=2 ScenarioAttempts/ScenarioRun; all attempts share the logical unit's aggregate budget; generation <=2 dispatches/job |
| Token budget | <=387,072/attempt (=18 x 21,504); <=774,144/logical unit with recovery; run ceiling = N x 774,144, up to 232,243,200 for N=300; actual authorized budget can be lower, clearly exploratory |
| Scenario timing | 180 s active attempt deadline; connect <=5 s and whole provider request <=30 s including body; each mock virtual latency <=5 s; retries wait <=8 s and only if remaining deadline fits |
| Trace | 16 KiB payload/event plus <=256-byte fixed envelope, 256 events/attempt, 1 MiB total/attempt including snapshots and envelopes; metadata/termination reserve 32 KiB; detailed derivation below |
| Suite | 100 scenarios, 1 default repetition, max 3; N=scenarios x repetitions |
| Execution scheduling | 4 global task slots in two groups of 2; <=1 executing group/workspace; <=2 nonterminal active/admitted evaluations/workspace, only one executing; generation uses one group with one task, never oversubscribes |
| Admission | 10 nonterminal evaluations/workspace, 100 globally; 60 min queue expiry before execution-group allocation; generation 20 candidates, 2 jobs/hour/workspace, 1 nonterminal generation/workspace |
| Deadline | At group allocation: D(N)=ceil(1.2 x ceil(N/2) x 450)+120 seconds; minimum 600 s. Queued waiting is separately bounded; no reset on crash. 450=2 x180 +90 recovery/lease quarantine |
| Storage | 2 GiB retained trace quota/workspace; reserve N x2 x1 MiB before accepting full-envelope run; global headroom policy in OPERATIONS; quota includes live reservations and retained bytes |
| API | Reads 120/min/principal, writes 30/min/principal, starts 5/min/workspace, anonymous login 10/min/IP; DB-backed buckets; 429 + Retry-After |
| Money | Proposed maximum USD 10/workspace/day, USD 100/workspace/month, USD 500/platform/month; NO universal USD 2 default; quote per approved rate card and N, show full-envelope or exploratory cap, require budget approval |

The 300-unit maximum requires 600 MiB trace reservation and D=81,120 s (22 h 32 min) including worst bounded recovery. A no-recovery 45 s mean would use about 112.5 minutes with two slots, but is not an SLA. The long worst-case window is deliberately visible; D-05 can lower unit ceilings instead. At most two groups execute; additional work queues or expires. No claim that 100 simultaneous maximum evaluations all finish in 60 minutes. Fair group allocation rotates eligible workspaces; running groups are nonpreemptive, so queued work may expire honestly behind long runs.

Token ceiling and money ceiling are independent. A full-envelope 300-unit quote may exceed a workspace cap and must be rejected with a smaller-run recommendation; maximum cardinality can be exercised with smaller bounded per-unit profiles, including a 1-turn fixture profile. The UI must never claim that 300 maximally expensive units fit USD 10. Approval does not silently raise a cap. For full-envelope mode, reserve the exact declared per-case maximum (bounded by L2) for all attempts; for exploratory mode show expected cost separately and warn that cap exhaustion means incomplete coverage.

### Event and byte invariant

Use compact event families, not one event for every internal function: <=2 per provider dispatch (intent and terminal response/error), <=3 per tool call (attempt including validation, policy, result with bounded delta), <=4 scripted-user events, <=2 state snapshots, <=8 evaluator summaries, <=8 lifecycle/limit events. Maximum =36+48+4+2+8+8=106 <256; heartbeat/lease polling is operational metadata, not trace events. An aborted attempt still has its own cap.

At maximum declared byte sizes: 18 x(16+8) KiB provider records +16 x(4+1+4) KiB tool records +4 x1 KiB user records +2 x64 KiB snapshots +8 x4 KiB evaluation records +8 x1 KiB lifecycle +106 x256 B envelopes +32 KiB reserve =806.5 KiB <1 MiB. Whole-request protocol wrapping stays within adapter transport bounds; the 16 KiB variable request is the persisted content portion. Large state snapshots use <=16 KiB chunks; the extra six chunk events add 1.5 KiB envelopes, yielding 112 events and 808 KiB. Snapshots are two logical objects, eight physical chunks. Unknown event families require revising this calculation. Oversized payloads produce flags and conservative verdicts; byte caps never authorize hidden evidence.

### Limits-coherence test specification (AC-042)

For every policy version, mechanically assert schema aggregate <=static request budget; static+conversation<=request byte budget; token estimate plus output<=approved model context; dispatch formula 8x2+2=18; attempted reservations across recovery<=logical/run caps; event and byte formulas fit; state/pointer limits fit parser caps; at most four slots and two per executing group; D(N) covers ceil(N/2) waves with all recovery allowances. Check N=1,20,100,300; minimum/maximum UTF-8, framing and schema cases; retries, all tools, script, chunks, redaction and evaluator records together. Distinguish compatible maxima from independently valid fields that cannot coexist. Fake-provider maximum-profile completion and a separately budgeted live representative run are G-20 evidence; no mathematical proof promises provider availability or response latency.
