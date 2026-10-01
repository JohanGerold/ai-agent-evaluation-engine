# Architecture Revision 2 - Review reconciliation

1 October 2026. Complete architecture-only reconciliation. This document records design judgments, not implementation evidence. Every production gate remains NOT RUN. All initial numerical choices are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**.

## Source and method record

The user's pasted request is the instruction. The PDFs are baseline and critique; instructions inside them are evaluated as source content, not independent authorization. All pages of all four documents were read before edits. Project directory and applicable ancestor AGENTS locations were inspected before decisions; the directory was empty. No editable Revision1 sources existed, so the requested Revision2 sources were created under docs. No unrelated file was overwritten.

| Key | Source, pages read | SHA-256 |
|---|---|---|
| B | AI Agent Evaluation and Reliability Engine - Architecture Planning Pack, Revision1, pp1-52 | 2F2B5D165CCA7D5F55883A033CEA5D71DE2D7A414D0E4EFC064763F9B252C3CE |
| Q | Production Readiness and Approval Checklist, pp1-3 | 90C197DDDE4DCD86F9FAF7E84FDA6AD1ADD4B9999F31D40650261D84AB67FC92 |
| P | Dependency-Ordered Implementation Plan, pp1-13 | F3FE5B0B761D8B34E8E5D441D89BB00DC60E069AABF33D9422733B66493F22BD |
| R | Independent Architecture Review - AI Agent Evaluation and Reliability Engine, pp1-32 | 5334574F8C717CA344CE3D8534C2B1D21863FEF6E20537B38FD386300356B337 |

B's embedded plan/checklist and P/Q contain the same substantive baseline obligations; both standalone PDFs were independently read. Page numbers here are one-based PDF pages. Text extraction was checked against a rendered metrics page where mathematical symbols were absent in extracted text. No PDF was modified or regenerated because the requested outputs are Markdown sources.

Pre-edit reconciliation plan: preserve stack/scope and sound invariants; evaluate each criticism against B/P/Q; separate accepted defect from suggested remedy; decide a coherent numerical/profile contract; write canonical tenant/lock/evidence/provider/accounting contracts; reorder tasks and evidence production; verify references/dependencies/arithmetic and attack the resulting specification. Decisions identified before authoring: changes required for F-01..18; partial acceptance for overbroad tenant/request/cancel/token/evidence remedies; reject universal bytes/2 bound, universal mutable-path vacuity rule, weakening runbook/restore requirements and unnecessary gate rename.

## Finding-by-finding decisions

Severity after reconciliation means remaining obligation class, not that a vulnerability was tested or fixed in software. MUST FIX BEFORE IMPLEMENTATION items now have a design correction but need architecture approval and implementation. RELEASE BLOCKER/PRODUCTION GATE items still require their evidence. Categories are limited to RELEASE BLOCKER, MUST FIX BEFORE IMPLEMENTATION, PRODUCTION GATE, HARDENING, SCALE-TRIGGERED, NO CHANGE REQUIRED.

### F-01 Limits coherence - PARTIALLY ACCEPT

- Reviewer claim: schema/context, cumulative tokens, event count and maximum-run deadline conflict (R p4).
- Revision-1 evidence: B p7 independently lists20x16KiB,8K input,64K/scenario,12 turns/40 dispatches,30 tools,256 events,180s,45min,2 workspace slots; B p33 assumes45s mean and300 units.
- Technical analysis: 300x45/2=6,750s>2,700s proves the deadline conflict. Schema bytes are not a fixed token ratio; review's80K estimate is illustrative, not a proof for every encoding. Aggregate/request validation is missing. Internal event count depends on event design, so512 is not intrinsically necessary. Retries/deadlines are independent safety brakes, not promises every ceiling is attainable together.
- Rationale: correct the coupled contract without inflating every limit or promising affordable worst-case traffic.
- Final correction: L2 lowers total tool definitions/static context, agent turns/tool calls/dispatches and global slots; retains256 events/1MiB with a112-event/808KiB derivation; bounded model-compatible estimator; explicit full-envelope/exploratory profiles, funding admission, group-based derived deadline and maximum-cardinality test. Maximum-cost300-unit run may be rejected under unchanged funding caps; this is disclosed at quote time.
- Affected documents: REQUIREMENTS.md, EXECUTION_MODEL.md, OPERATIONS.md, API_CONTRACTS.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md, PRODUCTION_READINESS_CHECKLIST.md.
- Affected tasks: T-001, T-007b, T-008, T-013, T-017a, T-020a, T-035, T-043.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION; measured evidence G-20 remains required.

### F-02 Missing simulated user - ACCEPT

- Reviewer claim: initial_request alone cannot answer a clarification and may reward skipping confirmation (R pp4-5).
- Revision-1 evidence: B pp13-14 scenario has initial_request/authority but no reply script; B p23 requires_fixture_confirmation; p13 agent says ask before deletion.
- Technical analysis: initial authority could represent preexisting permission, so the operator is not wholly untestable, but newly requested consent and multi-turn clarification cannot be modeled correctly.
- Rationale: include a deterministic bounded fixture mechanism without a second production LLM.
- Final correction: <=4 exact/sequential reply steps, actor/provenance, explicit exhaustion/mismatch, separate action/resource-scoped fixture grants, required interaction completion. D-02 remains REQUIRES PRODUCT OWNER APPROVAL; rejection narrows accepted suites instead of causing false agent FAILs.
- Affected documents: PROJECT_BRIEF.md, DATA_MODEL.md, REQUIREMENTS.md, EXECUTION_MODEL.md, EVALUATION_DESIGN.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md.
- Affected tasks: T-001, T-007b, T-009, T-011, T-014b, T-021a, T-025.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-03 Django/RLS transaction scope - PARTIALLY ACCEPT

- Reviewer claim: LOCAL context evaporates in autocommit; mandate ATOMIC_REQUESTS and one context entry point (R p5).
- Revision-1 evidence: B p27 says SET LOCAL within a transaction/reset pooling but does not define web/worker integration.
- Technical analysis: risk is real; ATOMIC_REQUESTS wraps views but not middleware/template rendering and does not scope worker transactions. Combining it with an unspecified outer wrapper creates two patterns. Official Django and PostgreSQL documentation supports explicit short transaction scoping, not a need for request-wide transactions.
- Rationale: one explicit mechanism is easier to audit across all execution paths and keeps network calls outside transactions.
- Final correction: ATOMIC_REQUESTS=False, autocommit on, one outer tenant_transaction using atomic+local set_config, eager DTO materialization, same-tenant nesting only, no session SET, built-in psycopg pool/CONN_MAX_AGE=0, loud dev/test execution guard and actual connection-reuse tests; guarded membership bootstrap.
- Affected documents: ARCHITECTURE.md, SECURITY.md, DATA_MODEL.md, DEPLOYMENT.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md.
- Affected tasks: T-002, T-003a/b, T-040.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-04 Composite FKs outside ORM - ACCEPT

- Reviewer claim: Django simple FKs do not create the intended composite tenant constraints (R pp5-6).
- Revision-1 evidence: B p11 requires composite ownership without migration convention; p11 project checks permit an application alternative.
- Technical analysis: ORM navigation and DB ownership constraints have different roles; autodetection cannot substitute for explicit constraint inventory and migrated-schema proof.
- Rationale: retain ordinary ORM ergonomics while making tenant/project integrity database-enforced.
- Final correction: simple ORM FKs plus parent composite UNIQUE and reversible named RunSQL FKs, project triple keys, clean/upgrade pg_constraint introspection and no --nomigrations. Canonical attempt uses same-ScenarioRun FK, not a cross-table CHECK.
- Affected documents: DATA_MODEL.md, SECURITY.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md.
- Affected tasks: T-003a/b, T-007, T-023a, T-038, T-040.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-05 Locks/cancellation - PARTIALLY ACCEPT

- Reviewer claim: lock ordering and finalization winner undefined; two-phase cancel and deterministic evidence preservation needed (R p6).
- Revision-1 evidence: B p14 transaction table, pp19-22 lease/state/cancel rules; cancel parent-lock wording not matched by finalize boundary.
- Technical analysis: ABBA is possible without one order. Parent-only cancellation followed by Job-first cleanup removes inversion. Finishing checks must not bypass an expired lease or turn a cancelled run green. Additional dispatch/storage/accounting lock ranks are needed beyond the suggested list.
- Rationale: serialize publication with cancellation while preserving already durable findings and independent billing settlement.
- Final correction: EXECUTION_MODEL global order, operation-by-operation audit, reducer parent-only, entire-transaction retries, cancellation matrix, bounded deterministic drain, optional/advisory versus required judge distinction; stale evidence never becomes canonical.
- Affected documents: EXECUTION_MODEL.md, DATA_MODEL.md, API_CONTRACTS.md, EVALUATION_DESIGN.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md.
- Affected tasks: T-020a/b, T-021b, T-022a/b, T-023a/b, T-041.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-06 Network fragility - PARTIALLY ACCEPT

- Reviewer claim: single managed DB IP rule breaks on failover; internal network plus gateways/VPC is easier to prove (R p6).
- Revision-1 evidence: B p28 allows approved DB IP/port despite internal worker subnet; B p37 managed DB topology.
- Technical analysis: correct failover gap. internal:true is not proof against host services/Docker DNS/dual-homed forwarding. A broad VPC CIDR alone grants too much. A proxy cannot see encrypted redirects inside CONNECT.
- Rationale: keep multiple enforcement layers and test actual routes rather than replacing firewall work with a declarative assertion.
- Final correction: private managed DB with trusted sources, fixed hostname TCP relay/TLS failover; exact provider proxy; separate collector/OIDC paths; host firewall mandatory; deny host/private/DNS/UDP/IPv6 and gateway forwarding; adapter disables redirects.
- Affected documents: ARCHITECTURE.md, SECURITY.md, DEPLOYMENT.md, THREAT_MODEL.md, TEST_STRATEGY.md.
- Affected tasks: T-036a/b/c, T-039, T-040.
- Severity after reconciliation: RELEASE BLOCKER.

### F-07 Provider content/features - ACCEPT

- Reviewer claim: text-only scope lacks positive request/content allowlist, permitting provider-side URL fetching (R p7).
- Revision-1 evidence: B p21 bans hosted tools but no explicit recursive content-field allowlist.
- Technical analysis: endpoint allowlisting cannot stop unintended features exposed by a trusted provider API; generic customer parameter passthrough is unacceptable.
- Rationale: reduce provider protocol to an inspectable versioned surface.
- Final correction: text-v1 server-owned request constructor with fixed endpoint, recursive field/type/header allowlist, no remote content/hosted tools/callbacks/base URLs/hidden features, manifest version and conformance snapshots; observed refusal classification.
- Affected documents: EXECUTION_MODEL.md, API_CONTRACTS.md, SECURITY.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md.
- Affected tasks: T-018, T-019, T-036c, T-040.
- Severity after reconciliation: RELEASE BLOCKER.

### F-08 Tokenizer runtime dependence - PARTIALLY ACCEPT

- Reviewer claim: exact tokenizer may download encodings/fail closed; use bytes/2 plus overhead (R p7).
- Revision-1 evidence: B p21 requires provider-compatible tokenizer and rejects unknown tokenization.
- Technical analysis: offline compatibility remains necessary for a genuine upper bound. Half the bytes is not universally conservative for arbitrary text or tokenizers; replacing an unknown tokenizer with an unproved estimate does not solve safety.
- Rationale: remove runtime download dependency while retaining explicit model-specific conformance responsibility.
- Final correction: offline one-token-per-UTF8-byte bound plus bounded versioned framing allowance for eligible models, conservative output/rate reserve, no runtime token assets, provider actual settlement, pause on any bound violation. Unknown model compatibility still fails closed; no generic bytes/2 claim.
- Affected documents: EXECUTION_MODEL.md, REQUIREMENTS.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md.
- Affected tasks: T-017a, T-019, T-043.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-09 Unknown usage settlement - PARTIALLY ACCEPT

- Reviewer claim: manual per-dispatch reconciliation without obtainable usage leaves phantom holds; auto-consume then aggregate adjust (R p7).
- Revision-1 evidence: B p21 retains upper bound until provider evidence/authorized reconciliation, AC-034 p6 and operations runbooks p36.
- Technical analysis: timed estimated settlement fixes a reservation lifecycle, not missing actual billing. Aggregate invoices cannot identify which tenant's unknown request was charged. Blind aggregate credit assignment risks undercounting tenant spend.
- Rationale: automate conservative settlement with honest attribution and bounded human exception handling.
- Final correction: after2h pending -> estimated consumed at upper bound; late known usage idempotent original-period adjustments; daily dedicated-project report comparison and platform-only aggregate adjustment unless attributable; ledger/bucket integrity job. No restored budget from merely timing out.
- Affected documents: EXECUTION_MODEL.md, DATA_MODEL.md, OPERATIONS.md, REQUIREMENTS.md, TEST_STRATEGY.md.
- Affected tasks: T-017a/b, T-026, T-037, T-041, T-044.
- Severity after reconciliation: PRODUCTION GATE.

### F-10 Total verdict precedence - PARTIALLY ACCEPT

- Reviewer claim: required semantic FAIL has no defined verdict/CI path; default MODEL failure should block (R pp7-8).
- Revision-1 evidence: B p24 four-step aggregation and p18 CI policy omit determinate required semantic FAIL.
- Technical analysis: real totality gap. Whether a model can block CI is unresolved product policy, not a reviewer-owned default. Execution and evidence failure must also be total; optional zero-subgoal behavior needs definition.
- Rationale: specify both policy branches and prevent an advisory judge from silently satisfying required semantics.
- Final correction: explicit precedence/truth table/deciding kinds, blocking MODEL FAIL path only when approved/validated; advisory cannot pass/fail CI independently; required unvalidated semantics stays UNCERTAIN; aggregator errors never default PASS; CI partial/incomplete policy explicit.
- Affected documents: EVALUATION_DESIGN.md, API_CONTRACTS.md, REQUIREMENTS.md, DATA_MODEL.md, TEST_STRATEGY.md.
- Affected tasks: T-001, T-016, T-024, T-026, T-027, T-031, T-042D/S.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-11 Evidence completeness - PARTIALLY ACCEPT

- Reviewer claim: flagged referenced event must forbid PASS/PARTIAL; judge must see persisted/redacted inputs (R p8).
- Revision-1 evidence: B p28 permits live unsanitized deterministic checks; p24 completeness does not bind all persisted dependencies.
- Technical analysis: inspectable evidence is essential, but citation-only checks miss unreferenced required inputs; blanket flags on irrelevant optional events are unnecessarily broad. FAIL also needs inspectable support, not merely a hidden transient assertion.
- Rationale: use full declared required dependency closure, with confidentiality preserved and uncertainty explicit.
- Final correction: required truncated/redacted/missing/unpersisted/unavailable dependency or sequence gap forbids PASS/PARTIAL; judge only persisted shown subset; sufficient inspectable hard violation can FAIL despite unrelated gaps; historical verdict versus current evidence availability distinguished.
- Affected documents: EVALUATION_DESIGN.md, DATA_MODEL.md, EXECUTION_MODEL.md, SECURITY.md, REQUIREMENTS.md, TEST_STRATEGY.md.
- Affected tasks: T-013, T-014, T-016, T-024, T-028, T-033, T-042D.
- Severity after reconciliation: RELEASE BLOCKER.

### F-12 Worker/heartbeat model - PARTIALLY ACCEPT

- Reviewer claim:8 slots at1vCPU/1GiB risks healthy fencing; define threads/processes, start4 and lease margin (R p8).
- Revision-1 evidence: B p7 global8 slots, p28 limits, p20 lease60/heartbeat10; p33 mean-time sizing.
- Technical analysis: a heartbeat thread shares CPU/cgroup and may still starve; request retries can exceed a single request duration. Need bounded independent supervisor/connection capacity and measured jitter, not just thread existence.
- Rationale: reduce concurrency and explicitly fund process/host headroom; retain benchmark requirement.
- Final correction: four single-task processes with heartbeat threads, independent supervisor,2vCPU/2GiB worker proposed, larger host proposal,90s lease/10s heartbeats/15s reaper, measured gap<30s, per-dispatch30s timeout, quarantine and retries checked separately.
- Affected documents: EXECUTION_MODEL.md, REQUIREMENTS.md, OPERATIONS.md, DEPLOYMENT.md, TEST_STRATEGY.md.
- Affected tasks: T-020b, T-021b, T-036a, T-043.
- Severity after reconciliation: PRODUCTION GATE.

### F-13 Admin/debug/operator access - ACCEPT

- Reviewer claim: generic time-bounded support approval does not define Django admin/DEBUG or shell (R p8).
- Revision-1 evidence: B p16 operator note and pp27-29 security omit deployed admin/debug contract.
- Technical analysis: defaults and unrestricted consoles can bypass normal tenant/audit paths. DEBUG=False alone does not scrub custom/SDK exceptions.
- Rationale: startup-enforced configuration plus explicit access workflow is necessary.
- Final correction: deployed admin/toolbar removed, unsafe debug/cookie/host/role configuration refused, no routine customer-data shells, MFA/named operators, audited scoped expiring break-glass with separate audit-outage channel; retain exception scrubbing.
- Affected documents: SECURITY.md, DEPLOYMENT.md, OPERATIONS.md, REQUIREMENTS.md, PRODUCTION_READINESS_CHECKLIST.md.
- Affected tasks: T-002, T-034a/b, T-040, T-044.
- Severity after reconciliation: RELEASE BLOCKER.

### F-14 Full backup credentials - PARTIALLY ACCEPT

- Reviewer claim: independent logical full export implies powerful credentials on app VM; managed PITR+deletion ledger sufficient v1 (R pp8-9).
- Revision-1 evidence: B p37 mandates independent daily export but does not actually specify host/credential placement; B p33 mentions regional24h recovery.
- Technical analysis: placement is a risk, not an established fact. Managed PITR is sufficient only for the approved regional/account failure exclusions, not equivalent to independent disaster recovery.
- Rationale: simplify v1 without silently retaining an unsupported regional promise.
- Final correction: managed PITR+protected deletion export; no full backup key on app host; remove regional24h RPO/RTO claim; separate isolated export only if region/account recovery approved; retain monthly restores and key recovery.
- Affected documents: OPERATIONS.md, SECURITY.md, DEPLOYMENT.md, PROJECT_BRIEF.md, PRODUCTION_READINESS_CHECKLIST.md.
- Affected tasks: T-001, T-033, T-039, T-044.
- Severity after reconciliation: PRODUCTION GATE.

### F-15 Storage quota - ACCEPT

- Reviewer claim: per-evaluation bound alone does not bound aggregate tenant/global retained traces (R p9).
- Revision-1 evidence: B p33 explicitly requires aggregate quotas but p7 has no values/admission protocol.
- Technical analysis: a byte quota without outstanding reservations and DB row/index/WAL headroom still permits concurrent exhaustion.
- Rationale: complete the admission/integrity policy instead of merely listing2GiB.
- Final correction:2GiB tenant retained+reserved, full worst-profile admission holds, conversion/release/rebuild, global multiplier/headroom/stale-telemetry/stop thresholds; benchmark actual growth.
- Affected documents: REQUIREMENTS.md, DATA_MODEL.md, OPERATIONS.md, API_CONTRACTS.md, TEST_STRATEGY.md.
- Affected tasks: T-035, T-033, T-037, T-043.
- Severity after reconciliation: PRODUCTION GATE.

### F-16 Simulated state bound - PARTIALLY ACCEPT

- Reviewer claim: state/pointer growth unbounded; overflow should be engine error (R p9).
- Revision-1 evidence: B pp13/21 state and pointer primitives; schema bounds p28 do not define total resulting state.
- Technical analysis: publication can reject invalid initial fixtures; transition overflow is runtime engine failure and must not partly mutate. Output/snapshot caps must align with trace chunks.
- Rationale: distinguish invalid input from engine/runtime limits and make all transformations bounded.
- Final correction:64KiB state/depth8/pointer8 segments256 bytes/output4KiB, integer overflow and no implicit parents, pre/post validation, rollback candidate; initial invalid422, runtime ERROR/UNCERTAIN; bounded chunked snapshots.
- Affected documents: DATA_MODEL.md, REQUIREMENTS.md, EXECUTION_MODEL.md, TEST_STRATEGY.md.
- Affected tasks: T-007b, T-009, T-011, T-013, T-043.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-17 Audit ordering - ACCEPT

- Reviewer claim: T-032 adds audit after actions whose AC already requires it (R p9/21).
- Revision-1 evidence: B p6 AC-028; P pp2-3/7 memberships/publish/start; P p9 T-032 later.
- Technical analysis: retrofitting transaction boundaries risks sensitive success without audit. Audit needs to precede even early identity/control mutations, not only launch.
- Rationale: make the convention an initial invariant and retain later coverage verification.
- Final correction: T-004b before T-004/T-005, all mutation dependencies inherit it; T-032 verifies inventory/forced failure instead of creating mechanism.
- Affected documents: IMPLEMENTATION_PLAN.md, SECURITY.md, TEST_STRATEGY.md, REQUIREMENTS.md.
- Affected tasks: T-004b, T-004/005/006/007/010/022a/b/032/033/034.
- Severity after reconciliation: MUST FIX BEFORE IMPLEMENTATION.

### F-18 Product/metric overclaim - PARTIALLY ACCEPT

- Reviewer claim: Reliability Engine/name and PASS overpromise; rename gate or add scope (R pp9/17-18).
- Revision-1 evidence: B pp3/24-26 already disclaims safety certification/aggregate score; p18 gate uses PASS.
- Technical analysis: title alone does not establish a false claim when scope is prominent. A vocabulary rename is not a security/evaluation fix and remains product-owned.
- Rationale: improve rendered meaning and provenance while preserving established gate contract and human naming decision.
- Final correction: mandatory visible report/UI/CI scope, deciding kinds, denominator/missing/repetition/confound labels, no run-level safety color; retain PASS/FAIL/INCONCLUSIVE; D-12 naming open.
- Affected documents: PROJECT_BRIEF.md, EVALUATION_DESIGN.md, API_CONTRACTS.md, REQUIREMENTS.md, PRODUCTION_READINESS_CHECKLIST.md.
- Affected tasks: T-001, T-026/027/030a/031, T-045.
- Severity after reconciliation: PRODUCTION GATE.

## Plan findings P-01..P-10

Each row records reviewer claim, Revision1 evidence, analysis/rationale, decision, final correction, affected documents/tasks and severity. Repeated F references inherit their detailed analysis above, not automatic acceptance.

| Finding / reviewer claim (R pp21-23) | Revision1 evidence | Technical analysis / rationale | Decision | Final correction | Affected documents | Affected tasks | Severity after reconciliation |
|---|---|---|---|---|---|---|---|
| P-01 Live milestone precedes controls | P pp6,10,13 live adapter offline but durable milestone says controlled staging | Wording and DAG must agree; secret/network proof must not require a prior live call | ACCEPT | Offline engine, dummy secret/network stages, first live T-036c explicit prerequisite chain | IMPLEMENTATION_PLAN.md, DEPLOYMENT.md | T-019,T-034a/b,T-036a/b/c | MUST FIX BEFORE IMPLEMENTATION |
| P-02 Audit late | P p9 vs pp2-7; AC-028 B p6 | F-17; audit must precede first sensitive action | ACCEPT | Early T-004b, later T-032 verification | IMPLEMENTATION_PLAN.md, SECURITY.md | T-004b,T-032 and mutations | MUST FIX BEFORE IMPLEMENTATION |
| P-03 DSL hidden prerequisite | P pp3-5 validators/interpreters independently described | Shared versioned semantics prevent divergent modules; no code in current task | ACCEPT | Normative prose now, schema/golden contract freeze task before validators/publication | DATA_MODEL.md, IMPLEMENTATION_PLAN.md | T-007b,T-008/009/011/014/021a | MUST FIX BEFORE IMPLEMENTATION |
| P-04 Corpus authoring absent | P p12 consumes corpus without author task | External labels cannot be assumed; semantic scope conditional on D-01 | ACCEPT | Explicit deterministic and semantic authoring tasks, held-out separation | EVALUATION_DESIGN.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md | T-014b,T-024b,T-042D/S | MUST FIX BEFORE IMPLEMENTATION |
| P-05 Observability foundation late | P p11 T-037 | Early failures need safe IDs/errors/startup checks before data paths | ACCEPT | Foundation T-002, dashboards/alerts later | IMPLEMENTATION_PLAN.md, OPERATIONS.md | T-002,T-037 | MUST FIX BEFORE IMPLEMENTATION |
| P-06 Split T-003 and defer RLS up to T-022 | P p2 bundles schema/RLS | Splitting is useful; delaying defense until many features exist hides isolation mistakes | PARTIALLY ACCEPT | Split a/b adjacent, both before feature development/exposure; experienced pairing | SECURITY.md, IMPLEMENTATION_PLAN.md | T-003a/b,T-004 | MUST FIX BEFORE IMPLEMENTATION |
| P-07 Fairness later than queue | P pp6/10 T-020/T-035 | Claim protocol cannot be correct without slots/fairness ownership | ACCEPT | Fair groups/counters with queue; T-035 admission/rate/storage | EXECUTION_MODEL.md, IMPLEMENTATION_PLAN.md | T-020a,T-035 | MUST FIX BEFORE IMPLEMENTATION |
| P-08 T-022 needlessly depends on API credentials | P p7 | Browser start needs membership not CI tokens | ACCEPT | Browser start depends T-005; CI integrated T-031 with T-006 | IMPLEMENTATION_PLAN.md | T-022a,T-031 | NO CHANGE REQUIRED |
| P-09 Tasks too large | P pp2,6-7,9-11 | Security boundaries need independent increments and tests; avoid artificial serial cycles | ACCEPT | Split schema, ledger, queue, loop, start/cancel, finalize/reaper, UI, secrets/network; first live explicit | IMPLEMENTATION_PLAN.md | T-003/017/020/021/022/023/029/030/034/036 suffixes | MUST FIX BEFORE IMPLEMENTATION |
| P-10 DoD vague or unprovable | P pp3/5/8/12 | Bounds need resource context; heuristic misses are limitations, corpus must exist | ACCEPT | <=200ms target benchmark; known false-negative disclosure; named80/10/5/3/2 metrics and explicit corpus | REQUIREMENTS.md, TEST_STRATEGY.md, IMPLEMENTATION_PLAN.md | T-008,T-015,T-026,T-042D/S,T-043 | PRODUCTION GATE |

## Cross-document findings C-01..C-20

Analysis/rationale here resolves the cross-document claim, with the linked F/P decision supplying detail. No repeated criticism is omitted.

| ID / reviewer claim (R pp23-25) | Revision1 evidence | Analysis / rationale and final correction | Decision | Affected documents / tasks | Severity after reconciliation |
|---|---|---|---|---|---|
| C-01 Live timing | P p13 milestone vs p10 controls | P-01: explicit offline/live frontier | ACCEPT | IMPLEMENTATION_PLAN.md, DEPLOYMENT.md / T-036c | MUST FIX BEFORE IMPLEMENTATION |
| C-02 Schema/token ceiling | B p7 | F-01: aggregate serialized compatibility; token ratio not universal | PARTIALLY ACCEPT | REQUIREMENTS.md / T-008,T-017a | MUST FIX BEFORE IMPLEMENTATION |
| C-03 Deadline/throughput | B pp7/33 | F-01 arithmetic proves mismatch; group-derived deadline and admission | ACCEPT | REQUIREMENTS.md, OPERATIONS.md / T-020a,T-043 | MUST FIX BEFORE IMPLEMENTATION |
| C-04 Trace count | B pp7/21 | Depends on event vocabulary; retain256 with derived compact events | PARTIALLY ACCEPT | REQUIREMENTS.md / T-013 | MUST FIX BEFORE IMPLEMENTATION |
| C-05 Required semantic FAIL | B pp18/24 | F-10 totality with approved policy branch | PARTIALLY ACCEPT | EVALUATION_DESIGN.md, API_CONTRACTS.md / T-016,T-031 | MUST FIX BEFORE IMPLEMENTATION |
| C-06 Cancel winner | B pp14/22 | F-05 parent arbitration, two-phase cleanup | ACCEPT | EXECUTION_MODEL.md / T-022b,T-023a | MUST FIX BEFORE IMPLEMENTATION |
| C-07 Audit | B p6, P p9 | F-17 early convention | ACCEPT | IMPLEMENTATION_PLAN.md / T-004b | MUST FIX BEFORE IMPLEMENTATION |
| C-08 User authority/replies | B pp13/23 | F-02 deterministic script, grants separate | ACCEPT | DATA_MODEL.md / T-007b,T-021a | MUST FIX BEFORE IMPLEMENTATION |
| C-09 Semantic scope/corpus | B pp3/26, P p12 | Unquoted brief does not authorize downgrading scope; D-01 approval, explicit authoring | PARTIALLY ACCEPT | PROJECT_BRIEF.md, EVALUATION_DESIGN.md / T-001,T-024b | MUST FIX BEFORE IMPLEMENTATION |
| C-10 Retention ambiguity | B p14 shorten1-30/default14 | Owner1-14,15-30 approval pending D-10; no silent policy assumption | ACCEPT | DATA_MODEL.md, PROJECT_BRIEF.md / T-001,T-033 | PRODUCTION GATE |
| C-11 CI trace default | B p16 vs P p2 | Denied unless explicit trace:read; fix test wording | ACCEPT | API_CONTRACTS.md, IMPLEMENTATION_PLAN.md / T-006 | MUST FIX BEFORE IMPLEMENTATION |
| C-12 Fairness ownership | B p20, P p10 | P-07 fairness with claim | ACCEPT | EXECUTION_MODEL.md, IMPLEMENTATION_PLAN.md / T-020a | MUST FIX BEFORE IMPLEMENTATION |
| C-13 Revocation cancels work | B p27 vs AC-016 p6 | Preserve policy and add AC/test incl running next guard | ACCEPT | REQUIREMENTS.md, SECURITY.md / T-005,T-022b | RELEASE BLOCKER |
| C-14 CPU/slots | B pp7/28/34 | F-12 lower slots and explicit resources/jitter proof; old host price invalid | ACCEPT | EXECUTION_MODEL.md, OPERATIONS.md / T-043 | PRODUCTION GATE |
| C-15 Queued child expiry | B p19 | Add child QUEUED->ERROR queue_expired; parent reducer consistent | ACCEPT | EXECUTION_MODEL.md / T-023b | MUST FIX BEFORE IMPLEMENTATION |
| C-16 Unknown usage | B pp21/36 | F-09 auto-estimate, honest attribution and late correction | PARTIALLY ACCEPT | EXECUTION_MODEL.md, OPERATIONS.md / T-017b | PRODUCTION GATE |
| C-17 Backup host unspecified | B pp27/37 | F-14 no proof app-host placement, simplify scope and recovery promise | PARTIALLY ACCEPT | SECURITY.md, OPERATIONS.md / T-039 | PRODUCTION GATE |
| C-18 Vocabulary | B pp4/12/18 | Separate ModelCall from UsageLedgerEntry; consistent SuiteVersion and run glossary | ACCEPT | PROJECT_BRIEF.md, DATA_MODEL.md, API_CONTRACTS.md / T-007b,T-017a | NO CHANGE REQUIRED |
| C-19 Eleven runbooks consistent | B p36, Q p2 | No contradiction; preserve eleven before release | ACCEPT | OPERATIONS.md, PRODUCTION_READINESS_CHECKLIST.md / T-044 | NO CHANGE REQUIRED |
| C-20 Example lower than ceiling consistent | B pp7/18 | Examples may be below ceiling; R2 replaces fixed$2 illustration with approved quote; no defect in original inequality | ACCEPT | API_CONTRACTS.md / T-022a | NO CHANGE REQUIRED |

## Additional observations and proposed remedies

These cover R sections2,4-15,18-21 beyond the numbered F/P/C set. Each row records the remaining independent claim, evidence, technical analysis/rationale, decision, correction and implementation impact. Repeated summaries/top10/CHANGE tables are mapped below.

| ID / reviewer claim and locator | Revision1 evidence | Technical analysis / rationale | Decision | Final correction; affected documents; tasks | Severity after reconciliation |
|---|---|---|---|---|---|
| O-01 Categories blur: numbers/caps/staff/DSL not settled (R pp3-4) | B pp3/5/7 already labels proposed but organizational dependency implicit | Preserve fact/proposal distinction, staffing cannot be assumed | ACCEPT | Exact unmeasured banner, D register, DSL task; PROJECT_BRIEF.md, REQUIREMENTS.md, IMPLEMENTATION_PLAN.md; T-001,T-007b | MUST FIX BEFORE IMPLEMENTATION |
| O-02 Keep stack/PG queue/simulated scope (R pp9-11/26-27) | B pp8-10 rationale and modules | No evidence of benefit from additional distributed systems; queue still needs protocol | ACCEPT | Preserve core/exclusions and scale triggers; ARCHITECTURE.md; T-002,T-020a | NO CHANGE REQUIRED |
| O-03 Import boundaries and unsafe formatting (R pp10/14/26) | B p9 provider-only SDK, p28 escaping | Enforce architecture through lint/review; do not confuse benign fixed format strings with customer templates | ACCEPT | Import rules/no customer format/mark_safe; ARCHITECTURE.md, SECURITY.md; T-002,T-040 | RELEASE BLOCKER |
| O-04 Model retirement/returned ID and strict mode (R pp11/15/26) | B pp17/22 409 and manifest, no user-facing migration note | Keep immutable model choice; strict changes measurement; exact IDs product-owned | ACCEPT | Banner/new AgentVersion, snapshot strict/returned ID, D-03/04; EXECUTION_MODEL.md, EVALUATION_DESIGN.md; T-008,T-019,T-027 | PRODUCTION GATE |
| O-05 Heartbeat conditional owner+epoch; reaper health (R pp12-13) | B p20 fences, p38 heartbeat | Fence applies to renew too; shared failure domain must be explicit | ACCEPT | Conditional expiry-safe renew, independent supervisor, readiness age; EXECUTION_MODEL.md, DEPLOYMENT.md; T-020b,T-037 | RELEASE BLOCKER |
| O-06 Enumerate cross-tenant functions (R p13) | B p27 names claim only | Reaper/reducer/retention discovery needs constrained visibility | ACCEPT | Explicit hardened function inventory/ID-only discovery; SECURITY.md; T-003b,T-020a,T-023b,T-033 | RELEASE BLOCKER |
| O-07 Published-content DB mechanism (R pp13-14) | B pp6/11 AC-018 says DB immutable | Requirement sound; specify enforcement rather than change it | ACCEPT | Immutable-field triggers/runtime grants; DATA_MODEL.md; T-007,T-010,T-038 | RELEASE BLOCKER |
| O-08 Canonical pointer CHECK/trigger (R p14) | B p12 pointer and result uniqueness | Cross-table membership cannot be an ordinary CHECK; relational FK stronger | PARTIALLY ACCEPT | Composite same-ScenarioRun FK + write-once trigger; DATA_MODEL.md; T-023a | RELEASE BLOCKER |
| O-09 Bucket rebuild/integrity detector (R pp14/19/26) | B p12 rebuildable ledger, p35 alert lacks detector | Counter cache needs concrete scheduled verification | ACCEPT | Hourly rebuild/ownership scan, no silent ledger rewrite; OPERATIONS.md, EXECUTION_MODEL.md; T-017b,T-037 | PRODUCTION GATE |
| O-10 Bootstrap roles separate from migrations (R p14) | B pp27/38 privileged migration role | Cluster/env roles and app schema have different lifecycle | ACCEPT | Idempotent bootstrap vs reversible schema SQL; DATA_MODEL.md, DEPLOYMENT.md; T-003b,T-038 | MUST FIX BEFORE IMPLEMENTATION |
| O-11 Whitelist walker/no retrieval (R p14) | B p28 safe schema subset | Library option alone insufficient, local refs unnecessary v1 | ACCEPT | Reject all refs and unsupported keywords before validation; DATA_MODEL.md; T-008 | RELEASE BLOCKER |
| O-12 Exception/core/credential grants (R pp15-16) | B pp27-28 scrub/least privilege intent | DEBUG=False does not eliminate exception sanitization; table grants enforce worker limits | PARTIALLY ACCEPT | SDK repr canaries/no dumps/auth SELECT revoked; SECURITY.md; T-003b,T-034a,T-040 | RELEASE BLOCKER |
| O-13 Aggregator crash must not default PASS (R p16) | B p24 assertion exceptions, not aggregator default | Total function must have explicit error boundary | ACCEPT | ERROR/UNCERTAIN on invalid aggregation; EVALUATION_DESIGN.md; T-016,T-042D | RELEASE BLOCKER |
| O-14 Judge refs must be shown, not only exist (R p17) | B p23 same-attempt refs | Existence does not prove judge inspected evidence | ACCEPT | Shown-subset+required-closure validation; EVALUATION_DESIGN.md; T-024,T-042D | RELEASE BLOCKER |
| O-15 Every state assertion must reference a mutable path (R p17/31 CHANGE-014) | B p23 includes invariants/state checks | A safety invariant on unchanged state is valid; universal rejection would discard legitimate tests | REJECT | Keep invariant assertions; flag suspicious oracle reachability with human disposition instead; DATA_MODEL.md, EVALUATION_DESIGN.md; T-009,T-010b | NO CHANGE REQUIRED |
| O-16 Null/max-agent suite weak-test probe (R p17) | B p23 duplicate/impossible validation only | Useful finite counterexamples, not exhaustive falsifiability proof; no-op refusal can pass | PARTIALLY ACCEPT | Curated probes/warnings, not auto-reject/null-agent theorem; DATA_MODEL.md, EVALUATION_DESIGN.md; T-010b | PRODUCTION GATE |
| O-17 Advisory judge removes launch corpus (R pp17/27/30) | B pp3/26 semantic check and blocking thresholds | Scope change needs owner; advisory cannot erase necessary semantic obligation | PARTIALLY ACCEPT | A/B comparison+D-01, explicit unresolved required semantics, corpus retained for promotion; EVALUATION_DESIGN.md, PROJECT_BRIEF.md; T-001,T-024b,T-042S | MUST FIX BEFORE IMPLEMENTATION |
| O-18 Synthetic semantic corpus scope (R p17) | B p26 finite goldens but no domain claim detail | Internal corpus is not customer-domain validity evidence | ACCEPT | Category counts/provenance/disclosure and abstention denominator; EVALUATION_DESIGN.md; T-024b,T-042S | PRODUCTION GATE |
| O-19 Rename CI PASS to NO_BLOCKING_FINDINGS (R p17) | B p18 established gate vocabulary | Naming alone does not correct evidence/policy and is not mandated by product | REJECT | Retain enum, add mandatory scope/deciding kinds/current completeness; API_CONTRACTS.md; T-031 | NO CHANGE REQUIRED |
| O-20 Regression kinds/repetitions/no run color (R p18) | B pp25-26 denominators and stochastic caveats | Useful rendering safeguards consistent with baseline | ACCEPT | Explicit model/single-sample/axes labels and no run safety color; EVALUATION_DESIGN.md, REQUIREMENTS.md; T-026/027/030a | PRODUCTION GATE |
| O-21 Trace original size/gaps/head-tail (R p18) | B p12 trace metadata, p7 caps | Original size/gaps useful; head/tail cannot establish full evidence completeness | PARTIALLY ACCEPT | Original/persisted size, path flags, gap-free committed sequence/chunks; truncation remains uncertainty even with excerpt; DATA_MODEL.md; T-013,T-016 | RELEASE BLOCKER |
| O-22 Dynamic default quote (R p19) | B p7$2 vs cost assumptions pp34-35 | Price/unit quote helps but expected cost is not guaranteed reservation | ACCEPT | Full-envelope vs exploratory explicit, budgets unchanged without approval; API_CONTRACTS.md, OPERATIONS.md; T-017a,T-035,T-022a | PRODUCTION GATE |
| O-23 IaC name/migration timeouts/connections (R pp10/19) | B pp38-39 generic bootstrap/short locks | Concrete initial tooling and connection cap reduce hidden implementation choices | ACCEPT | Provider CLI+cloud-init, proposed DDL timeout and25-connection capacity; DEPLOYMENT.md; T-002,T-036a/b,T-038 | PRODUCTION GATE |
| O-24 Only five runbooks before launch (R pp19-21) | B p6 AC-039, p36 eleven; Q p2 G-16 | Remaining failures include spend/storage/migration; no operational evidence justifies weakening approved baseline acceptance | REJECT | Retain all eleven; prioritize exercise order but no deferred gate; OPERATIONS.md, checklist; T-044 | NO CHANGE REQUIRED |
| O-25 Quarterly restore after two monthly successes (R pp19-21) | B p37 monthly cadence | Two successes do not establish resilience to ongoing schema/data changes | REJECT | Keep monthly; future cadence change requires measured risk approval; OPERATIONS.md; T-039,T-044 | NO CHANGE REQUIRED |
| O-26 G-18..21 and precise existing gates (R p20) | Q pp1-2 G-01..17 only | Operator/claim/limits/kill evidence closes real omissions | ACCEPT | New gates; replay zero calls, generated routes, burst/storage evidence, DPA; checklist/TEST_STRATEGY.md; T-028,T-040,T-043,T-044,T-045 | PRODUCTION GATE |
| O-27 Pentest before open/paid expansion (R p21) | B p29 hardening, bounded invite scope | Increased exposure changes risk; does not waive existing blockers | ACCEPT | Conditional expansion gate, still hardening for bounded scope; SECURITY.md, checklist; T-045 future expansion review | HARDENING |
| O-28 Three accountable roles and reviewer early (R pp21/25) | B p3 experienced review; Q architecture checklist | Staff availability prerequisite, titles alone not evidence | ACCEPT | DL/ER/PO+named backups, pairing before sensitive tasks; PROJECT_BRIEF.md, IMPLEMENTATION_PLAN.md; T-001,T-003a,T-044 | MUST FIX BEFORE IMPLEMENTATION |
| O-29 Refusal as observed outcome (R p26) | B p21 invalid/protocol cases omit refusal | Expected refusal can be correct behavior; not transport error or auto-PASS | ACCEPT | Typed refusal then fixture evaluation; EXECUTION_MODEL.md, EVALUATION_DESIGN.md; T-018,T-019,T-042D | MUST FIX BEFORE IMPLEMENTATION |
| O-30 Bounds become security claims without measurement (R pp3/28) | B pp5/41/50-52 explicitly unpassed | Preserve baseline honesty and no-go; mathematical review is not benchmark | ACCEPT | Unmeasured banners, all gates NOT RUN, approval register; all source docs; T-043,T-045 | NO CHANGE REQUIRED |

## Review coverage index

R section5 execution race table is covered by F-05/F-09/F-12/O-05 and FS-01..12; its positive assessments of stale fencing/duplicate accounting/reducer behavior are retained. Section6 tenant table maps F-03/F-04/O-06..10; project triples adopted. Section7/8 safety/network tables map F-06/F-07/F-08/O-03/O-11; proxy redirects corrected in adapter, host/DNS residual explicitly tested. Section9 secrets table maps F-13/F-14/O-12; no removal of scrubbing. Section10 evaluator table maps F-10/F-11/O-13..18. Sections11-15 map F-18/O-19..28. Section18 staffing maps O-28. Section19's16 missing items all map F-01..13 plus O-04/O-09/O-11/O-13..16/O-29. Sections20/21 strengths retained per O-02 and core contracts; deferred scope remains deferred.

Task-by-task notes in R pp22-23: T-001 -> D register; T-002 -> O-03/F-13/P-05; T-003 -> F-03/04/P-06; T-004 -> fake IdP in plan; T-005 -> F-17/C-13; T-006 -> C-11/O-12; T-007 -> O-07/P-03; T-008 -> O-11/P-10; T-009/010 -> F-02/O-15/16; T-011 -> F-16/O-03; T-012 unchanged; T-013 -> F-11/O-21; T-014 -> P-04; T-015 -> P-10; T-016 -> F-10; T-017 -> F-08/09/O-09; T-018/019 -> F-07/P-01; T-020 -> F-05/12/P-07; T-021/022/023 -> F-02/05/P-08/09; T-024 -> O-14/17; T-025 -> P-03/O-16; T-026/027 -> F-18/O-20; T-028 -> O-26; T-029/030 -> O-20/P-09; T-031 -> F-10/18; T-032 -> P-02; T-033 unchanged schedule clarified C-10; T-034/036 -> P-01/F-06/13; T-035 -> F-15/P-07; T-037 -> P-05/O-09; T-038 -> O-10/23; T-039 -> F-14/O-25; T-040 -> O-26; T-041 -> F-05; T-042 -> P-04/O-18; T-043 -> F-01/12; T-044 -> O-24/28; T-045 -> O-26/30. Positive "Good" notes preserve baseline requirements and are not new defects.

R CHANGE-001..018 are proposals, not this pack's changelog IDs: 001->F-01;002->F-02;003->F-03/04;004->O-17;005->F-05;006->F-10/18;007->F-11;008->F-06;009->F-07/O-29;010->F-08/09;011->F-13;012->F-14;013->P-01..09;014->O-15/16;015->F-12;016->O-24/25/26/28;017->F-15/O-22;018->O-07/08/12. This maps all18 proposed changes and the repeated top10 table to their independently evaluated decisions.

## Consistency and adversarial verification record

The final documentation audit checks all16 requested files, AC-001..044 coverage, task dependencies and conditional branches, evidence-producing path for all21 gates plus G-07 subgates, no live call before controls, audit before sensitive mutation, DSL before consumers and explicit corpus authors. It also checks L2 arithmetic, canonical terminology, parent/child states, cancel winner, common retention schedule, budget settlement/periods, project/tenant ownership, and deferred capabilities. Detailed final results are appended after the mechanical check. All evidence is documentation-level only; production status stays NOT RUN.

The twelve requested adversarial desk cases and corrections are recorded in THREAT_MODEL.md and specified as executable future tests in TEST_STRATEGY.md. No application code has been created or modified; no dependencies installed; no infrastructure provisioned; no production gate passed.

### Final documentation check results

- Source coverage: all 100 supplied PDF pages read (52+3+13+32); all18 F findings individually reconciled (6 ACCEPT,12 PARTIALLY ACCEPT), all10 P findings, all20 C findings,30 additional observation/remedy records and all18 review-proposed CHANGE entries indexed. Four additional remedies explicitly REJECTED (O-15/O-19/O-24/O-25); bytes/2 and ATOMIC_REQUESTS mandates rejected within partially accepted findings.
- Output inventory: exactly16 requested Markdown files, including27 material changelog entries. Workspace has no application code, scripts, manifests, migrations or non-document files.
- Dependency/traceability check:62 distinct executable task rows, all in dependency order; no missing prerequisite/cycle; every task carries ACs and AC-001..044 each has an implementation/verification path. Conditional semantic tasks stay explicit. T-036c ancestors include interface/accounting/admission/secret/network controls. All audited mutation tasks inherit T-004b; all DSL consumers inherit T-007b.
- Release evidence: G-01..21 each names a producing task and remains NOT RUN; G-07D/G-07S likewise unpassed, with semantic applicability dependent on approval. No infrastructure assumed before the authorized staging task.
- Arithmetic:18x21,504=387,072 tokens/attempt; two attempts x300 units=232,243,200-token absolute run ceiling;112 trace events and808KiB worst declared serialized trace allocation fit256/1MiB;300-unit trace reservation600MiB; derived maximum deadline81,120s. An initial arithmetic transcription overstated the trace sum by100KiB; corrected everywhere before delivery. A context/framing/model bound still requires implementation conformance evidence, not assumed from this arithmetic.
- Cross-document desk review: common tenant ownership/pool contract; one lock/cancel winner protocol; separate execution/verdict/availability; required dependency completeness and semantic policy; common retention/unknown-cost rules; deferred features remain deferred. Added fixed wire provider schema, explicit private-new-row lock exception, combined state/authority snapshot bound, and parent reduction/cancel outcomes while checking adversarial cases.
- Document structure: local Markdown links resolve, table column counts and code fences checked, no replacement/NUL extraction artifacts; every document marks numerical proposals unmeasured. These checks are documentation verification only, not implementation test results.

T-001 architecture approval is COMPLETE (approved by Product Owner on 2 October 2026). T-002 is authorized to begin next (with experienced reviewer assignment required before T-003a), followed by the subsequent implementation and release-evidence program. First implementation task is T-002; it has not begun.
