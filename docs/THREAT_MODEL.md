# Architecture Revision 2 - Threat model

Design requirements only; none of these controls has implementation evidence. Untrusted sources include all customer JSON/text, model/generator/judge outputs, tool metadata and CI requests. Trusted reviewed fixture authority is separate from conversational text. Platform operators, provider, identity and backup systems are distinct trust domains.

All initial numerical limits and targets are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**.

Assets: tenant inputs/evidence/identities, platform keys, canonical evaluation integrity, budget ledger/capacity, backups/deletion records. Boundaries: browser-web, tenant-tenant, app-DB, scheduler-tenant context, data-interpreter, worker-simulator, worker-provider, runtime-secrets, production-staging and backup-restore. An LLM judge is not a security boundary; a fully compromised trusted application/DBA is a disclosed residual.

| ID | Threat / correction in R2 | Verification / residual |
|---|---|---|
| TM-01 | IDOR or pooled tenant context leakage: authz + explicit transaction wrapper + RLS + composite project/tenant FKs | G-02; app compromise can select another context |
| TM-02 | Member/token escalation: server action matrix, recent auth, last-owner lock, bounded scopes | G-02/G-13; compromised owner retains own-tenant authority |
| TM-03 | Secret leakage: worker-only injection, safe serializer/SDK exceptions, no debug/admin/dumps | G-04/G-18; unknown pasted secrets may evade detection |
| TM-04 | Data becomes executable: fixed dict simulator, no imports/eval/SQL/templates/files/network handles | G-03; dependency RCE remains residual |
| TM-05 | Schema/state resource attack: whitelist before validator, no refs/regex, bytes/nodes/depth/pointer/time caps | G-03/G-14; parser defects require updates |
| TM-06 | Direct or provider-mediated SSRF: fixed gateways plus positive text wire allowlist | G-03; allowed provider sees selected data; gateway compromise residual |
| TM-07 | Judge injection/false evidence: persisted shown subset, total precedence, advisory proposal, corpus gate | G-07; limited corpus does not prove generalization |
| TM-08 | Generator/oracle poisoning: deterministic coverage/validation, weak-test probes, human review, no auto-publish | G-07; reviewers can miss bad tests |
| TM-09 | Runaway spend: admission/dispatch ledger, no hidden retries, known/unknown settlement, kill switches | G-06/G-21; accepted calls can bill after cancel |
| TM-10 | Noisy tenant/storage exhaustion: fair groups, queue/rate/trace quotas/headroom and bounded worker model | G-14/G-20; shared host/DB contention remains |
| TM-11 | Stale/duplicate worker: job-first locks, epochs, parent arbitration, recovery/quarantine | G-05; external duplicate billing may occur |
| TM-12 | Uninspectable/tampered trace: persisted dependency closure, gap/flag checks, canonical pointer constraints | G-05/G-07; DBA changes not cryptographically prevented |
| TM-13 | Stored XSS/exfil: escaped text, CSP, no mark_safe/customer templates/remote images | G-13; browser/framework vulnerability residual |
| TM-14 | Sessions/CI compromise: OIDC, CSRF, expiries, scopes, revocation eligibility guard | G-02/G-13; identity outage/compromise residual |
| TM-15 | Deleted-data resurrection: protected minimal ledger before purge, replay before exposure | G-09/G-15; backup expiry/downloads disclosed |
| TM-16 | CI/supply-chain compromise: locked builds, pinned actions, no PR secrets, reviewed promotion | G-10/G-13; scans/signatures not proof of harmlessness |
| TM-17 | Host/runtime compromise: non-root bounded containers, deny paths, no socket/host creds, patch/rebuild | G-03/G-18; shared kernel is not hostile-code isolation |
| TM-18 | Backup/operator abuse: managed PITR, no app-host full export key, audited expiring MFA break-glass | G-09/G-18; region/account compromise not covered by RPO/RTO |

## Retained 25 adversarial questions

Every numbered answer is RELEASE BLOCKER until corresponding control evidence exists, with residual risk above; storage/host expansion remains SCALE-TRIGGERED and stronger audit tamper evidence HARDENING.

| # | Challenge | Required answer and AC path |
|---|---|---|
| 1 | Another tenant's information? | Route/worker/RLS/FK/pool negatives, uniform404; AC-009/017 |
| 2 | Malicious agent reaches production infrastructure? | Pure mock-only registry/no credentials or real adapters; AC-002/020 |
| 3 | Generated URL SSRF? | Text-only allowlist plus worker deny proof; AC-020 |
| 4 | Secrets in traces? | Canary serialization, required evidence uncertainty on redaction; AC-013/025 |
| 5 | Secrets in logs? | Safe exceptions, no debug/wire/environ dumps; AC-013/037 |
| 6 | Unlimited cost? | Atomic funded dispatch, finite limits/attempts, conservative unknown settlement; AC-012/034 |
| 7 | Worker dies halfway? | Fenced abandonment, clean bounded retry; AC-015 |
| 8 | Job twice? | Unique logical identity and epoch/canonical constraints; AC-010 |
| 9 | Provider unavailable? | Bounded retry/breaker, honest ERROR/INCOMPLETE; AC-011 |
| 10 | History changes after edits? | Immutable triggers/manifests; explicit deletion markers; AC-014 |
| 11 | Agent manipulates evaluator? | Rules precede judge, shown references, corpus; AC-021/036 |
| 12 | Metadata manipulates generation? | Inventory, validator and human suite review; AC-008/021 |
| 13 | Unsupported conclusion? | Persisted dependencies, total truth table and uncertainty; AC-022/025 |
| 14 | Customer exhausts capacity? | Fair groups/admission/storage/headroom/load; AC-027/038 |
| 15 | DB can restore? | Timed isolated managed restore with deletion replay; AC-030 |
| 16 | Broken release rollback? | Previous compatible digest/config and staging drill; AC-031 |
| 17 | Failed migration recovery? | Short locks, inspect partial state, forward repair; AC-031 |
| 18 | Diagnose run failure? | Safe IDs, typed reasons and ordered evidence; AC-007/029 |
| 19 | Sensitive actions audited? | Atomic insert or rollback from earliest mutation; AC-028 |
| 20 | Dangerous effects simulated? | Authorized and denied effects stay in fixture memory; AC-002/006 |
| 21 | Raw credential reaches prompt? | Secret values excluded from input DTO, all-phase canaries; AC-013 |
| 22 | Malformed response corrupts state? | Safe bounded parser, pure candidate transition before fenced commit; AC-035 |
| 23 | Cancellation inconsistent? | Two phases, global lock order, parent winner, late-usage-only path; AC-019 |
| 24 | Concurrent edits lost? | If-Match + immutable atomic snapshots; AC-018 |
| 25 | Secure without evidence? | Every gate NOT RUN, explicit residual/approval; AC-040 |

## Final Revision 2 adversarial desk check

These are specification inspections, not executed security tests. Each attack has an explicit future fault test in TEST_STRATEGY.

| Attack | Reconciled design outcome |
|---|---|
| Pooled connection A -> B after exception | LOCAL rolls back; wrapper/checkout guard and B context; no session SET; lazy queries forbidden |
| Stale lease completion | Owner/epoch/DB expiry inside same transaction rejects evidence/pointer; usage settles separately |
| Cancellation/finalize ABBA | Cancel holds parent only then commits; child cleanup uses Job-first order; reducer never locks children |
| Duplicate job delivery | Unique logical key, lock/epoch and canonical membership constraint; distinct possible paid calls counted |
| Judge-driven false PASS | Advisory cannot satisfy required semantics; blocking needs approved validated scope; hard rule failure wins |
| Truncated-evidence PASS | Required dependency flags/gaps/absence stop PASS/PARTIAL; citation-only completeness insufficient |
| Provider feature/content escape | Recursive positive wire allowlist rejects unknown field/part/tool/path/header before gateway |
| Worker direct egress | Internal network plus host restrictions and fixed gateways; prove host/DNS/IPv6 and failover, not merely public curl |
| Unknown reservation leakage | Timed estimated consumption removes pending hold; late corrections idempotent; aggregate credit not guessed per tenant |
| Clarification flow | Exact/sequential fixture script plus separate scoped grant; prose Yes alone changes no authority |
| Maximum evaluation | Cardinality/profile/funding validation, group-based derived deadline, token/event/storage arithmetic; reject unaffordable full profile visibly |
| Audit write fails | Sensitive action and audit same DB transaction roll back; no later best-effort audit |

Self-review also corrected aggregate-billing attribution, canonical pointer FK (not cross-table CHECK), evidence dependency closure, snapshot chunk event counts, gateway host exposure, first-live-probe dependency cycles and expired-evidence CI behavior. Human decisions remain open; these fixes are design decisions, not passing gates.
