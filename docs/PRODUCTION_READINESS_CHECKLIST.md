# Architecture Revision 2 - Production readiness and approval

ARCHITECTURE PROPOSED; NOT IMPLEMENTED; NOT PRODUCTION-READY. Every production gate is NOT RUN. Numerical thresholds are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. Writing a specification is not evidence of a working control.

## Architecture approval

- [x] T-001 approved Revision 2, explicit scope, stack, and D-01..13 decision deadlines (Product Owner approval recorded 2 October 2026).
- [x] Semantic policy (Option B advisory first) and scripted-user inclusion explicitly approved by Product Owner; no implied product choice.
- [ ] Experienced reviewer named before sensitive work (mandatory gate before T-003a; T-002 permitted without ER); operator/backup named before operational tasks.
- [x] Approved model IDs/strict mode/estimator/rates and operating profiles recorded as provisional directions/proposed benchmark profiles; final settings deferred to documented task deadlines.
- [x] Region/platform/privacy/funding provisional directions approved by Product Owner; final authorizations deferred to documented task deadlines.
- [x] SLO/RPO/RTO/retention and product claims reviewed; working title and scope statement approved; SLO/RPO/RTO explicitly unmeasured design targets requiring benchmark evidence.

## Release gates

Accountable roles: DL=Development lead with named operations backup; ER=Experienced reviewer; PO=Product owner. A title alone is not an assigned person.

| Gate | Required measurable evidence / producing path | Accountable | Status |
|---|---|---|---|
| G-01 Threat review | All TM controls, zero unresolved high/critical release defects; residual owner/rationale/expiry; T-040/T-045 | ER | NOT RUN |
| G-02 Tenant isolation | URL-generated negatives, actual-role RLS/composite FK/project/pool/rollback tests incl worker auth-table denial; T-003a/b/T-040 | DL + ER | NOT RUN |
| G-03 Execution effects/egress | Pure simulated effects; recursive text allowlist; namespace direct/private/metadata/DNS/IPv6/host/gateway and DB-failover proof; T-011/T-019/T-036a/b/c/T-040 | ER | NOT RUN |
| G-04 Secrets | Zero platform canaries across all normal/crash sinks; web/worker separation, rotation/revoke; unknown pasted-secret limitation explicit; T-013/T-034a/b/T-036c/T-040 | DL + ER | NOT RUN |
| G-05 Durability | FS-01..16 applicable schedules, lock/cancel arbitration, zero stale canonical writes/duplicate results/unaccounted possible dispatches; T-041 | DL + ER | NOT RUN |
| G-06 Cost bounds | Concurrent funded reservations, no double admission charge, estimator bound, unknown auto-settlement/late/aggregate/period handling; T-017a/b/T-035/T-041 | DL + PO | NOT RUN |
| G-07 Evaluation correctness | G-07D mandatory; G-07S mandatory for Option A or any later canonical semantic promotion; selected mode explicit; T-042D/T-042S | ER + PO | NOT RUN |
| G-07D Deterministic/advisory | >=100 goldens including>=30 safety,100% expected outcomes, zero known false-safe on finite safety set; advisory injection/citation/completeness tests; T-014b/T-042D | ER | NOT RUN |
| G-07S Blocking semantics | >=200 held-out labels/two labelers, stated agreement/recall/abstention and all category denominators; returned model/rubric pinned, synthetic scope disclosed; T-024b/T-042S | ER + PO | NOT RUN |
| G-08 Reproducibility | Immutable manifest; replay yields zero ModelCalls and zero reservation changes, rerun new IDs/reservations; T-007/T-010/T-028 | DL | NOT RUN |
| G-09 Recovery | Timed managed restore + host rebuild at realistic data; deletion replay/current ledger, stale sessions/jobs, tenant/ledger checks and approved RPO/RTO; T-039 | DL + ER | NOT RUN |
| G-10 Release/rollback | Digest/config evidence, clean/upgrade migrations, constraint inventory, partial failure repair and compatible rollback; T-038 | DL + ER | NOT RUN |
| G-11 Observability | Safe incident reconstruction, integrity detector actually triggers, dashboards and primary/backup synthetic alerts; T-037/T-044 | DL | NOT RUN |
| G-12 Provider failures | Bounded retry/breaker/refusal/protocol/outage handling, no hidden failover; T-019/T-036c/T-041 | DL | NOT RUN |
| G-13 Web/supply chain | CSRF/XSS/session and restricted image tests, pinned builds/scans, zero unmitigated critical/high exploitable findings; T-002/T-038/T-040 | ER | NOT RUN |
| G-14 Capacity | Normal steady/slowdown plus100-request burst admission, fair groups, bounded memory/connections/heartbeat, measured trace/index/WAL multiplier or revised plans; T-043 | DL | NOT RUN |
| G-15 Retention/privacy | DATA_MODEL schedule, purge/export/restore tests, customer/provider/backup retention and DPA/data-location decisions recorded; store=false not zero-retention claim; T-033/T-039/T-045 | PO + ER | NOT RUN |
| G-16 Operability | All eleven runbooks exercised, monthly restore cadence assigned, real primary+backup; T-044 | DL | NOT RUN |
| G-17 Acceptance coverage | Every AC-001..044 has implementation/test evidence, every task linked, no missing feature/security path; T-045 | DL + PO | NOT RUN |
| G-18 Operator access | Admin/DEBUG/toolbar absent, unsafe startup rejected, MFA/named consoles, expiring audited break-glass and audit-outage route; T-002/T-034/T-040 | ER | NOT RUN |
| G-19 Claim language | Scope+evidence kind rendered on report/UI/CI, no run score/safety color, model/single-sample/denominator limits explicit; T-026/T-030a/T-031/T-045 | PO | NOT RUN |
| G-20 Limits coherence | L2 arithmetic/serialization fixtures and measured max-cardinality staging run within declared deadline; full-expense profile funding explicitly checked; T-007b/T-043 | DL + ER | NOT RUN |
| G-21 Kill switches | Global execution stop, workspace pause and key revoke block new dispatch within one heartbeat; in-flight charges preserved; T-022b/T-034/T-044 | DL + ER | NOT RUN |

Under approved Option B, G-07S is recorded as NOT RUN / not applicable to advisory launch, with approval evidence; it is never marked passed. G-07D and advisory safeguards remain mandatory. T-001 is approved; implementation tasks begin with T-002; all production gates remain NOT RUN.

## Approval record

| Decision | Person | Date | State / evidence |
|---|---|---|---|
| Architecture accepted | Product Owner | 2 October 2026 | APPROVED (T-001 approved; implementation authorized starting with T-002) |
| Product / semantic / data-processing limits | Product Owner | 2 October 2026 | APPROVED / PROVISIONALLY DIRECTED (D-01..13 recorded in PROJECT_BRIEF.md) |
| Security residuals | Unassigned | Not approved | Gate evidence pending |
| Operations and budget | Unassigned | Not approved | Benchmarks/restore/drills pending |
| Bounded production launch | Unassigned | Not approved | T-045 pending |

External pentest and stronger audit tamper evidence are hardening after baseline for invite-only scope; pentest becomes prerequisite before open onboarding/paid expansion. Extra hosts, object traces, broker and standby are scale-triggered. Remote agents/code/real tools/BYOK need a new design. Never defer a known tenant leak, unbounded spend, real destructive path, missing restore or false-safe evaluator defect as hardening. Stop after this architecture revision; T-002 has not begun.
