# Architecture Revision 2 - Operations and recovery

Proposed only. All objectives, capacities, periods and thresholds are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. None is a customer commitment or approved purchase.

## Ownership and objectives

Map responsibilities to three named roles: Development lead (delivery/operations with a named backup), Experienced reviewer (independent security/DB/network/evaluator review), Product owner (scope/privacy/budget/claims). One person may cover compatible duties, but cannot substitute self-approval for independent sensitive-boundary review. Reviewer participation must be assigned before T-003a begins (T-002 is permitted without ER); T-044 assigns primary/backup on-call humans.

| Objective | Proposed measurement |
|---|---|
| Metadata API availability / latency | 99.5% monthly eligible success, p95 <500 ms under approved workload; platform failures included |
| Queue | p95 <60 s under normal small-run load and available capacity; all-conditions wait/expiry separately reported; no max-burst promise |
| Terminal correctness | >=99% admitted evaluations reach honest terminal state within their applicable queue/execution deadline +120 s |
| Useful coverage | >=95% planned units have complete required checks under normal provider operation; outages remain in raw counts |
| Worker recovery / cancellation | Reaper detects expired lease within 15 s; bounded recovery decision within 120 s; normal cancel visible terminal <=60 s, crash case <=120 s where DB available |
| Recovery | RPO <=15 min, RTO <=4 h for app-host loss/recoverable DB failure with managed PITR accessible; must measure |

No region-loss/cloud-account-loss recovery commitment. Dropping independent full exports removes Revision 1's unsupported 24-hour regional RPO/RTO proposal; D-13 must approve a separate regional recovery design if needed.

## Capacity and cost

Demand model remains 50 developers, 10 workspaces, 20 evaluations/day x20 scenarios =400 units/day, typical 45 s occupied slot time. Four slots give theoretical 320 units/hour, 160/hour at a 50% planning utilization; group allocation and provider limits may lower this. Typical 20-unit service estimate with two slots is 7.5 min, excluding queueing. A 300-unit run at that mean is 112.5 min. REQUIREMENTS gives the much longer bounded recovery deadline and 600 MiB maximum retained-trace reservation; never advertise the mean as a guarantee.

At 50 KiB trace payload/unit, 400/day produces ~19.5 MiB/day and ~273 MiB over 14 days before recovery/row/index/WAL overhead. Use 3x as an initial disk expansion factor only; T-043 replaces it. Two attempts and ceiling traffic are separately modelled. Proposed worker allocation is 2 vCPU/2 GiB on a 4 vCPU/8 GiB host; re-quote cloud/DB/identity/network costs after D-08/D-11. The old 2-vCPU host price is not reused for the larger host. No model IDs or old rate-card examples are represented as current approved prices.

Per-workspace retained-trace quota: 2 GiB including retained bytes and reservations. Full-envelope admission reserves N x2 x1 MiB atomically; each write converts reservation to retained bytes, unused holds released at terminalization; purge releases retained usage only after confirmed deletion. Reaper reconciles holds for crashed work. Global storage admission uses measured DB used bytes + 3x outstanding trace reservations + 20% configured DB capacity safety reserve <= provisioned capacity; global storage counter locks after tenant counters. At >=70% actual utilization warn; at >=80% stop new trace-producing admission; at >=85% stop fresh provider dispatch after a bounded evidence/settlement drain. Resume only below75% and with reconciled capacity. Existing work cannot assume all free disk; reserve termination/ledger metadata. Stale storage telemetry >5 min blocks new admission. These controls may reject a burst well before 100 queued runs, which is an upper bound, not a target accepted count.

Model quote = sum of declared input/output ceilings x approved exact rates with upward micro-USD rounding, recovery, retry, judge and generation separated. Typical estimates are informational and never replace the hard authorized envelope. Daily/monthly/platform caps in REQUIREMENTS may reject full maxima. Unknown usage consumes conservative estimates after automatic settlement; aggregate vendor credits are not falsely attributed to tenants. Daily ledger/bucket comparison and provider aggregate reconciliation follow EXECUTION_MODEL. Provider billing is not a guaranteed real-time cap.

## Observability and integrity

T-002 establishes structured JSON logs, request/correlation IDs, safe exceptions and startup validation. Logs contain safe event/type/time/engine/run/attempt/dispatch IDs and timings, no prompts, arguments, raw email, keys, authorization or query-bearing URLs. Metrics use low-cardinality component/status/provider labels; no customer strings. Local collector has a field allowlist, size/rate bound and fixed destination.

T-037 adds service, execution and usage/integrity dashboards; synthetic alerts must reach primary and backup. Proposed alerts: three failed minute readiness probes or >5%5xx/5min; queue p95>60s/15min and oldest>5min; supervisor heartbeat absent30s or execution heartbeat gap>20s; provider >20% transport failures of >=20 calls/5min; any stale canonical write/unsupported PASS/ledger divergence; spend50/80/100%; storage thresholds above; missing deletion export immediately; backup status stale24h; overdue restore drill. Provider outage leaves report-read readiness intact but execution readiness false.

Integrity worker: hourly ledger-to-bucket rebuild-and-compare, canonical pointer/result ownership and terminal-child/parent convergence check, expired reservations and storage-hold checks; daily billing comparison when reports are available. Detection stops relevant new dispatch and alerts; never silently repairs historical verdicts. Corrections are auditable append-only transitions. Clock and period reconciliation are UTC.

## Backup and restore

Production-v1 uses encrypted managed PITR with proposed 7-day window, plus immediate protected export of minimal deletion tombstones before purge eligibility. No full-backup/BYPASSRLS credential or object-store full-backup access on app VM. The deletion export credential may write only its append-only minimal ledger destination, not read all backups. Managed backup existence is not restore evidence. Independent full export is deferred until an approved regional/account recovery requirement, then run from a separate isolated maintenance job with separate credentials.

On deletion export failure, deny access immediately, show pending deletion, retain safe tombstone and alert; never report full deletion complete. Restore must obtain the latest protected deletion ledger; if unavailable/stale beyond accepted export watermark, keep restored DB isolated. Monthly restore drills remain required; reject weakening cadence merely because two earlier drills passed.

Restore procedure: pause public traffic/claims; record recovery point and possible loss; restore into isolated private DB; verify schema/counts/hashes, managed backup accessibility and secret-store key recovery; replay protected tombstones and purge affected scopes; expire restored sessions/tokens; fence pre-restore epochs, disable old workers, retain/reconcile ambiguous dispatches; validate tenant roles/composite constraints, ledger and fake-provider safety cases; approve repointing; prove egress and perform explicitly budgeted smoke probe before resuming. Measure against realistic data, including trace overhead. Host rebuild uses IaC, immutable digest and approved secret aliases, with no durable user state on host.

## Incident runbooks - all eleven before release

Every incident records UTC time, digest/config version and safe IDs. Contain, preserve evidence, diagnose, recover, validate and record action owner. No customer content or credentials in incident chat. All eleven require staging exercises; minor tabletop-only treatment needs explicit approved scope and does not replace restore/rollback/kill tests.

| Incident | Containment / diagnosis | Recovery / proof |
|---|---|---|
| Provider outage | Breaker/pause, classify429/5xx/network; retain deadlines | Same-model bounded probe then gradual resume; preserve INCOMPLETE |
| Runaway evaluation | Cancel, workspace/global kill if guards fail, inspect dispatch ledger | Fix limiter, fake loop test, reconcile billable calls before resume |
| Worker backlog | Inspect group fairness, oldest wait, DB locks, provider quotas | Fix bottleneck; scale only with approved headroom; quiet tenant progresses |
| Worker crash loop | Pause claims, preserve safe logs, check OOM/parse/DB | Known digest/reduced concurrency, fence old epochs, canonical checks |
| Database outage | API not ready, no reservations or dispatch | Restore connectivity/PITR with deletion replay and ledger checks |
| Failed deployment | Freeze rollout, stop incompatible workers | Compatible prior digest/config, smoke and egress test |
| Failed migration | Stop release, identify committed steps/locks | Roll back uncommitted transaction or reviewed forward repair; restore last resort |
| Compromised provider key | Kill dispatch, revoke provider key, safe audit | Rotate/restart, canaries and budgeted probe; reconcile old calls |
| Unexpected spend | Global/workspace pause, compare rates/retries/unknowns | Audited cause/correction, explicit funding decision; no ledger deletion |
| Trace storage growth | Stop admission, inspect purge and size/counter drift | Repair bounded purge, headroom reconciliation and restore-time check |
| Identity outage | No auth bypass; normal existing sessions only | Restore config/service; login/logout/recovery/step-up probes |

Global kill, workspace pause and credential revoke checks occur before every dispatch and at 10s heartbeat; G-21 measures cessation within one heartbeat for workers with DB access. DB loss itself blocks dispatch. Already-authorized external calls can bill and must settle.
