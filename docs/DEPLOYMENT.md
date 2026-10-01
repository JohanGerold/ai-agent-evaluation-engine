# Architecture Revision 2 - Deployment and network contract

Architecture only; nothing provisioned or installed. Numerical sizes/timeouts are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. D-08 region, D-11 platform and infrastructure spending require explicit decisions before provisioning tasks.

## Environments and topology

Local: Compose-equivalent fake provider and real PostgreSQL migration tests, synthetic data/dummy credentials, no real model key. Staging: separate VM/private managed DB/identity/provider project/secrets, same enforcement shape, synthetic fixtures and approved small budget. Production: separate credentials and approved region, no staging access to production DB/secrets. Never copy customer traces into staging.

Reference services: Caddy ingress; web; four-slot worker container plus independently supervised reaper; provider CONNECT proxy; fixed PostgreSQL TCP relay; local telemetry collector; restricted OIDC egress for web. Use reviewed Compose network definitions and provider CLI + cloud-init/bootstrap recipes as initial IaC, all versioned and reproducible; do not assume unsupported cloud firewall features.

Worker attaches only to an `internal:true` bridge. It can connect to exact internal proxy/relay/collector service ports; deny all other internal services, host gateway, link-local/metadata, LAN/private/public destinations, UDP, direct DNS and IPv6 using host/container enforcement. Internal network is one layer; Docker DNS/host routes and dual-homed containers must be explicitly tested. Web has separate ingress/identity paths and cannot reach provider key/service. No gateway container enables general IP forwarding, SOCKS, user-controlled CONNECT-to-DB or arbitrary TCP tunneling.

| Gateway | Allowed exit / validation |
|---|---|
| Provider proxy | Exact approved provider hostname:443 only, no wildcard/numeric hosts; resolve on proxy, validate all A/AAAA public answers; certificate verified in worker adapter; no other HTTPS hosts |
| DB relay | One configured managed private DB hostname:port, within approved DB subnet/VPC and trusted source VM; refresh DNS on reconnect/failover; no client-selected target; end-to-end PostgreSQL TLS hostname verification uses original server name |
| Collector | Fixed telemetry destination, field/size/rate allowlist; no customer URL or arbitrary log forwarding; bounded spool, no canonical evidence dependency |
| Web identity egress | Exact OIDC hosts/paths as supported by integration, separate from model proxy; no general internet route |

Managed DB private endpoint and trusted-source rules restrict inbound to app relay/approved migration/restore jobs. A VPC CIDR rule alone is insufficient outbound authority: the relay still fixes destination hostname and port. Failover changes IP through DNS without manual firewall widening; private range validation, TLS verification and reconnect test required. If the selected service lacks this private topology, block deployment choice or design an equally constrained alternative and review it. Host firewall remains mandatory defense in depth, not dismissed because `internal:true` exists.

From inside the worker namespace prove: direct public IPv4/IPv6 TCP, arbitrary UDP/DNS, alternate DNS, host bridge ports, metadata, loopback services, private ranges, numeric CONNECT, wrong ports/hosts, unusual URL forms and proxy-free SDK traffic fail; approved provider text request succeeds only via proxy; DB succeeds only via fixed relay; direct DB/public DB route fails; telemetry carries sanitized metadata only. Kill proxy/relay and prove fail-closed behavior. Exercise DB failover and every A/AAAA validation path without widening rules. Repeat after Docker/kernel/network updates. These are future G-03/G-20 tests, not claims already established.

## Runtime, connections and health

Immutable OCI digest with Python/Django patch compatibility verified at build; web and workers same engine contract. Non-root, read-only root, no caps/socket/privileged mounts, no-new-privileges, core dumps off, bounded tmpfs/PIDs/CPU/memory per EXECUTION_MODEL. No package installation at runtime. Worker task+heartbeat connections separate, bounded per-process pool max2 (8 total), supervisor max2, web aggregate max8, maintenance max2 =20 runtime connections; reserve 5 DB connections for migrations/operations =25 capacity minimum. Pool minima0; no double pooling; role-specific limits. Actual DB tier must support this with headroom before approval.

Startup refusal covers DEBUG/admin/toolbar, allowed hosts/cookies/CSRF, supported schema/DSL/surface versions, safe non-owner runtime roles/RLS, no session tenant defaults, configured egress policy hash, valid rate/estimator/model registry, necessary secrets and DB availability. Report readiness depends on DB/config; execution readiness additionally on worker/supervisor heartbeat, breaker, key state, group capacity and kill switches. Liveness is local process health, not paid provider probing. Restricted dependency details only to operators.

## Ordered delivery

T-002 creates offline foundation; T-019 only fake HTTP adapter conformance. T-034a installs/test dummy secret plumbing. T-036a proves local topology without real key; T-036b provisions authorized staging and proves denial paths with dummy transport. T-034b then injects staging credential and proves access separation/canary handling without dispatch. T-036c is the first permitted paid model call, requiring T-017a/b accounting, T-019 interface/allowlist, T-035 admission, T-034b safe injection, T-036b signed egress proof and approved model/privacy/funding. Rotation's live probe occurs there, not earlier. All preceding engine/generator/judge tasks remain fake-provider-only. No circular prerequisite between secret proof and network proof.

CI: protected PR -> formatting/type/lint/schema and pure fixtures -> real migrated PostgreSQL/runtime-role tests -> secret/dependency/image/browser/security tests -> single pinned build with source SHA/digest/SBOM -> authorized staging deploy -> migration compatibility/fault/egress/corpus/load/restore evidence -> human go/no-go. PR jobs receive no production secrets; deploy credentials short-lived. Lockfiles/actions/images pinned; critical/high exploitable defects block release.

## Migrations and rollback

Separate bootstrap role/grants from app migrations; deployment migration credential never mounted on web/worker. Expand-compatible schema first, resumable idempotent data batches, delayed contract removal. Composite constraints/RLS/functions use reviewed SQL with reverse SQL and explicit inventory. Proposed migration lock_timeout=5s and statement_timeout=5min for ordinary DDL; concurrent indexes/large batches require explicit per-migration override and partial-failure recovery notes, never global indefinite timeouts. Test clean schema and prior-version upgrade, runtime FK/RLS introspection, old/new code compatibility and failure midway.

Pause claims and drain attempts before engine changes; do not resume an old attempt under new engine semantics. Retain previous compatible image/config/network definitions; rollback image only when schema compatible, no blind down migration. Rebuild compromised host from IaC and rotate accessible secrets. Post-deploy smoke verifies auth/tenant deny, fake small evaluation/report/cancel, egress, safe audit/usage; separately approved bounded provider probe. Observe errors/queue/spend for 30 minutes; record digest/schema/config/test evidence and approver.
