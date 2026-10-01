# Architecture Revision 2 - Execution, accounting and cancellation

Proposed only; every numerical setting is **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. REQUIREMENTS owns the L2 profile. At-least-once job execution with fenced canonical publication does not imply exactly-once provider execution.

## States and winner rules

EvaluationRun: QUEUED -> RUNNING on execution-group allocation; QUEUED -> CANCELLING on cancel, or ERROR on queue expiry/invalid manifest; RUNNING -> CANCELLING; RUNNING -> COMPLETED / INCOMPLETE / ERROR by reducer; CANCELLING -> CANCELLED when every child terminal. Cancel of a terminal parent is a no-op returning its existing status. The queued cancellation is briefly CANCELLING until child cleanup, with no dispatch permitted.

ScenarioRun: QUEUED -> RUNNING on claim; QUEUED -> ERROR on queue_expired/parent deadline; QUEUED -> CANCELLED; RUNNING -> EVALUATING when agent phase ends; RUNNING/EVALUATING -> QUEUED after fencing an abandoned attempt when recovery allowed; RUNNING/EVALUATING -> ERROR on unrecoverable engine/provider failure; EVALUATING -> COMPLETED on full evaluation; RUNNING/EVALUATING -> CANCELLED or INCOMPLETE with an evidence-backed partial result where available. INCOMPLETE covers limits or missing required evaluation, even if a known rule establishes FAIL. Terminal states never restart; a rerun is a new EvaluationRun.

ScenarioAttempt: ACTIVE -> EVALUATING -> FINALIZED, or ACTIVE/EVALUATING -> ABANDONED/FENCED. Terminal ScenarioRun may point to a finalized partial result on CANCELLED/INCOMPLETE/ERROR; status and verdict stay separate. No canonical pointer to abandoned evidence. A child ERROR without enough evidence has verdict UNCERTAIN, not FAIL. Reducer crash does not alter committed children.

Reducer takes only the parent lock; reads immutable terminal child snapshots without locking them. Every child finalize takes the parent lock, so while reducer holds it terminal publication is serialized. If any child nonterminal, leave parent unchanged. Otherwise cancellation accepted -> CANCELLED; all children COMPLETED with required evaluation available -> COMPLETED; some usable results but unavailable children/checks -> INCOMPLETE; no usable results and infrastructure failure -> ERROR. FAIL verdict alone is not infrastructure failure. Parent summary freezes at terminal commit; later billing adjustments are a separate current usage view, not a rewritten verdict.

## One lock order

All row-locking operations, including implicit writes and FK checks, must follow this hierarchy. Within a rank acquire sorted stable UUID/key order; never escalate to an earlier rank. Precreate counter rows where possible. No SQL helper hides a reverse acquisition.

1. Job.
2. ScenarioRun.
3. ScenarioAttempt.
4. EvaluationRun (generation uses its analogous parent).
5. ModelCall / dispatch accounting row, sorted dispatch ID.
6. Tenant/run/scenario BudgetBucket and StorageBucket, sorted `(workspace_id, scope_rank, period_start, id)` with scope_rank scenario -> evaluation -> workspace-day -> workspace-month; then platform BudgetBucket by period.
7. Tenant concurrency counters, then global concurrency counters / ExecutionGroup scheduler row last, in stable ID order.

Audit/trace/ledger inserts use unique owned identities and cannot acquire locks on earlier unrelated mutable rows. Membership/control mutation uses its own owner/membership locks, writes cancellation intent/outbox metadata, commits, then cancels children in separate transactions; it never holds membership locks while acquiring jobs. Dispatch/claim eligibility uses an authorized revocation epoch snapshot plus a DB control guard; sensitive principal revocation writes that guard atomically. Schema/foreign-key lock effects must be included in T-041 schedules.

Creating a wholly new unpublished run/job/child subtree is not a lock-order reversal: its rows are not visible to other transactions until the one admission commit. This exemption does not apply to preexisting rows or follow-up mutations. Referenced immutable configuration is checked before budget/counter locks; no mutable parent/child update is allowed while holding admission counters. The privileged claim function executes inside the same authorized tenant transaction after ID-only discovery; it does not install a second session context.

| Path | Ordered locks and transaction boundary |
|---|---|
| Group admission | Read candidate IDs optimistically; lock candidate parent, budget/storage as needed, then group/counters; recheck eligible, allocate or roll back; never hold group then lock parent |
| Claim | Select eligible Job with SKIP LOCKED -> child -> new attempt -> parent -> counters; recheck group ownership/control/deadline; claim and reserve slot atomically; failed admission rolls back epoch |
| Heartbeat | Job -> child -> attempt -> parent; conditional on owner+epoch+unexpired lease+nonterminal; cancellation permits drain renewal only, never dispatch permission |
| Pre-dispatch / tool effect | Job -> child -> attempt -> parent -> dispatch (if any) -> budget/counters as needed; check fence and stop conditions, persist intent/reservation/effects; commit before network |
| Finalize | Job -> child -> attempt -> parent -> dispatch/budget/counters; re-read cancellation and lease, commit final trace/result/pointer, close job, release eligible resources atomically |
| Cancel phase 1 | Parent ONLY plus new audit insert: mark CANCELLING and commit; no child/job locks |
| Cancel phase 2 | One child's standard order per transaction; queued children terminalize; active workers observe stop; never parent-first child traversal |
| Reaper | Discover IDs without row locks, then standard Job-first order for each expired attempt; bump epoch, preserve abandoned trace, settle resource quarantine, decide bounded recovery |
| Parent reduction | Parent only; never calls child-finalize inline; repeatable from independent supervisor |
| Late usage / auto-settle | ModelCall -> budget buckets; no later attempt/parent/job lock; cannot publish trace or verdict |
| Quota/kill control | Control/budget rows only, commit before fan-out; never hold global counters while acquiring tenant jobs |

Deadlock/serialization failure retries restart the entire short DB transaction, re-read cancellation/epoch/budget and inspect committed dispatch IDs; never repeat an external call as a DB retry. Bounded 3 DB retries with jitter within operation deadline, then typed retryable failure. This does not make lock-order violations acceptable.

## Leases, worker model and isolation

Four execution processes, one task per process, each with a dedicated heartbeat thread and its own short-lived DB transaction connection. A fifth small supervisor/reaper process runs independently of task CPU work; same image and management-command family. Start with a worker container budget of 2 vCPU, 2 GiB, 128 PIDs, 64 MiB tmpfs on a proposed 4 vCPU/8 GiB app host, leaving web/proxy/collector headroom. These are capacity recommendations, not purchase authorization. Per-process bounded data prevents one task holding all traces in RAM; loaded snapshots have size caps. Process isolation reduces GIL contention; a heartbeat thread is not proof against cgroup CPU starvation.

Lease=90 s, heartbeat interval=10 s, reaper=15 s, whole provider request<=30 s, maximum actual mock wait=0 (latency is simulated); 90 >=2 x(30+5). Retries renew/check between individual dispatches and never turn one lease into permission for an unbounded logical call. DB clock defines expiry/deadlines. Late heartbeat cannot resurrect expired epoch. All DB writes use short lock/statement timeouts; heartbeat delay >20 s alerts and prevents fresh dispatch until renewal. T-043 must show maximum heartbeat gap <30 s under full CPU/memory/DB contention; if not, reduce concurrency or revise lease/profile before release.

After lease loss the worker stops; late results cannot write evidence or canonical state. An old provider call's concurrency occupancy is quarantined until its recorded 30 s request deadline plus 10 s grace or confirmed completion; do not release simply on lease loss. Monetary uncertainty lasts under the separate settlement policy. Recovery begins clean initial fixture, no resumed guesses, at most two total attempts; the logical unit's call/token/spend envelope includes both. Evaluation-group recovery must preserve its original absolute deadline. Reaper remains independently supervised; web reports supervisor heartbeat age and execution readiness without misclassifying report-read health.

## Cancellation matrix

All stop reasons (user cancel, revoked principal, workspace deletion/pause, global kill, deadline) are checked at claim, heartbeat, before each dispatch, before each tool effect and before finalize. Cancellation after a successful pre-dispatch transaction can race one already-authorized in-flight call per active child; no architecture claim of zero extra charge.

| Cancellation point | Required behavior |
|---|---|
| Queued | Parent CANCELLING commits with audit; child cleanup marks CANCELLED, releases unspent envelope/storage, no provider dispatch |
| Before provider dispatch | Standard guard refuses reservation/dispatch; preserve recorded findings |
| During provider call | No new calls; bounded call may return/bill; settle usage and record safe response if lease still valid; no follow-on tool effects |
| After provider response | Persist valid bounded evidence, halt effects; evaluate only available evidence |
| During deterministic evaluation | Finish bounded pure checks over already persisted evidence, preserving valid FAILs; no new effects; cap local drain at 5 s, then ERROR/UNCERTAIN if unfinished |
| During semantic evaluation | No fresh judge/repair call; already-dispatched judge may finish within its deadline; missing required judgment -> UNCERTAIN, except known hard failure wins; optional/advisory missing judge cannot make canonical PASS by itself |
| Before finalize | Parent lock arbitrates. If cancellation committed first, finalize child as CANCELLED with any valid result; never discard deterministic evidence merely because status is cancelled |
| After child commit | Keep committed child result/status; cancellation affects remaining children only |
| Before parent reduction | If cancel acquires nonterminal parent first, parent ultimately CANCELLED even if all children committed; if reducer made parent terminal first, cancel no-op. Child winners unchanged |

Cancellation does not bypass epoch/lease/evidence checks. A stale worker cannot use the evidence-preservation rule to publish after fencing; only existing persisted abandoned evidence and independent usage settlement survive.

## Provider surface `text-v1`

One adapter-owned fixed HTTPS host/path, TLS verification, no redirects, no SDK retries, no streaming, bounded connect/whole-body timeout, compressed and decompressed byte limits. No arbitrary base URL or SDK passthrough dictionary. Agent/generator/judge all pass the same constructor/validator. The following logical fields map only to the concrete wire surface below:

| Allowed field | Constraint |
|---|---|
| model | Server registry exact approved ID |
| messages/input | Enumerated system/developer/user/assistant text roles; text strings only; assistant function call and tool-result records with bounded IDs, JSON arguments/output serialized as text |
| tools | Agent phase only; local function definitions from validated immutable tool schemas; no provider-hosted tools; judge/generator omit tools |
| tool_choice / parallel behavior | Server-owned local-function policy; sequential simulation; no customer override |
| max_output_tokens | Adapter's tested billable-output cap, including reasoning; unsupported models rejected |
| temperature / seed | Only if explicitly supported and approved in model registry, finite bounded values; otherwise absent |
| store / stream | Fixed false; background is not an allowed wire field |
| response format | Server-owned bounded structured schema for generator/judge only, validated provider compatibility |

The proposed concrete wire surface is `text-v1.chat-1`: POST `https://api.openai.com/v1/chat/completions`. Top-level allowlist: model, messages, tools, tool_choice, parallel_tool_calls, max_completion_tokens, store, stream, n, service_tier, response_format, temperature, seed. Fix n=1, store=false, stream=false and service_tier=default. Agent phase uses parallel_tool_calls=true to permit a bounded returned batch; the platform still applies all simulated calls sequentially in recorded order. Judge/generator omit this field. Optional temperature/seed are omitted unless model registry approves them. No background field. The API documents a completion cap including reasoning tokens; model eligibility still needs conformance proof ([OpenAI request reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)).

Nested allowed shapes are application policy: messages contain only role and string content, with assistant tool_calls limited to id/type=function/function{name,arguments}, or tool-role tool_call_id and string content. Assistant content may be null only alongside tool_calls. Roles system/developer are constructed by the platform from approved templates/configuration, not accepted as raw customer message objects. Tools contain only type=function and function{name,description,parameters,strict}; parameters follow the DSL schema whitelist. tool_choice is the fixed server policy auto or none. Judge/generator omit tools and use response_format with type=json_schema and json_schema{name,strict,schema} only. Every string/array/object is bounded by L2; no content-part arrays are accepted. These restrictions deliberately exclude otherwise valid provider features.

Allowed request headers are adapter-generated Authorization, Content-Type=application/json, Accept=application/json, fixed User-Agent, dispatch-derived X-Client-Request-Id and necessary fixed-host HTTP framing headers. Accept-Encoding is identity; there are no caller headers, beta/feature headers or SDK diagnostic passthrough. Response transport caps are 256 KiB on received and decoded bytes; persisted response content cap is8KiB, with truncation flags and required-evidence consequences. Any SDK-injected extra header fails offline conformance until explicitly reviewed as a surface version change.

Positive recursive field/type allowlist rejects everything else, including images, audio/video, file IDs/URLs, remote content parts, callbacks/webhooks, arbitrary metadata/user fields, conversation IDs, previous-response IDs, search, connectors, hosted code/shell, computer/browser tools and provider feature headers. URL-like strings inside text are inert text. T-019 verifies this surface against the approved model; an incompatible model/region requires a new reviewed surface version, not runtime fallback or arbitrary endpoint configuration. Manifest records surface version and schema digest; conformance snapshots recursively compare every outbound key/content type and HTTP path/header against it. Refusal is an OBSERVED agent outcome evaluated against fixture expectations, not automatic PASS or transport ERROR. Malformed protocol is an infrastructure error.

## Reservation and settlement

No runtime tokenizer downloads. Estimate from exact constructed canonical UTF-8 variable input: one token per byte plus a versioned conservative framing allowance (4,096 for the bounded 64-message/tool surface); only approved models whose tokenizer/framing bound is substantiated by offline adapter evidence are eligible. Bytes/2 is not a universal upper bound. Unknown estimator compatibility or unknown price blocks dispatch; exact tokenizers are optional offline conformance aids, not runtime dependencies. Input estimate is conservative, not claimed exact. Provider-reported usage settles known usage. If reported usage exceeds bound, consume actual cost, pause model/dispatch, alert bound violation; never conceal overspend by clamping it. This is a release-blocking estimator failure.

Use integer micro-USD rounded UP per charge component, undiscounted rate card, all billable output/reasoning categories and no assumed cache discount. An evaluation admission hold authorizes a user-approved token/money envelope in all relevant buckets. Dispatch moves funds from that hold to a dispatch reservation, rather than charging it twice; a smaller exploratory budget can stop the run. Generation and judge use the same gateway. Required judge allowance is partitioned before agent spending in Option A. Distinct possible provider requests always get separate dispatch IDs and reservations; SDK hidden retries forbidden.

Before network, commit dispatch identity, exact request hash/version, deadline, attempt fence, request-intent evidence and reservations. States: RESERVED_NOT_SENT -> SENT -> KNOWN_SETTLED or UNKNOWN_PENDING; proved-unsent -> RELEASED; ambiguous crash after reservation is UNKNOWN_PENDING unless transport evidence proves unsent. On duplicate acknowledgement inspect ModelCall; do not assume provider exactly-once deduplication.

UNKNOWN_PENDING auto-settles after 2 hours to ESTIMATED_CONSUMED at its upper bound, releasing reservation and increasing estimated consumed by the same amount. It does NOT return spending power or claim actual billed usage. This removes permanent phantom reservations while conservatively charging the uncertainty. Late exact usage creates an idempotent compensating ledger entry against original period buckets; no negative counters, no double settlement, no terminal verdict changes. Reserve across UTC day/month boundaries against the period of dispatch; transfer admission holds to the new period with cap checks before later dispatch. A run crossing a period boundary can stop honestly if the new period has no budget.

Daily aggregate reconciliation uses an approved provider usage/billing export fetched by a separate operator/control-plane job, not by expanding worker egress. Dedicated provider project/key and currency/time-window alignment are required; delayed reports remain pending. Compare known+estimated ledger charges with provider aggregate and maintain one idempotent audited platform adjustment per report/version/window. Never distribute aggregate credits to arbitrary tenants or fabricate per-dispatch actuals. Attributable corrections alone change tenant spend; unresolved aggregate variance stays platform-level, escalates and can pause dispatch. Scheduled ledger-to-bucket rebuild-and-compare detects drift without silently overwriting authoritative entries. Settlements retain reservation creation periods even after midnight.

## Reproducibility

Manifest snapshots immutable agent/suite/case hashes, DSL/normalization/surface/estimator/rate versions, requested and returned model IDs, parameters, strict mode, prompt/rule/heuristic/judge policy and versions, engine digest, limits, script, repetitions and credential alias/version only. Model ID unavailable -> 409 at start, report banner and republish new AgentVersion; no mutation or silent substitute. Returned judge ID drift invalidates blocking eligibility and marks comparison confounded. Trace replay is display-only, no ModelCall or reservation mutation. Rerun creates new IDs and authorized budgets; exact engine replay only with complete recorded/fake responses and the same contract, never a promise of stochastic reproducibility.
