# Architecture Revision 2 - Evaluation and evidence

Architecture only. All corpus thresholds and operating numbers are **PROPOSED - UNMEASURED UNTIL BENCHMARKED**. The evaluator must expose what was observed and what remains unverified.

## Semantic policy decision - REQUIRES PRODUCT OWNER APPROVAL

| Axis | Option A: canonical judge at launch | Option B: advisory first (recommended) |
|---|---|---|
| Safety | Can catch prose failures, but model false PASS/FAIL can affect release | Deterministic gate protected from model drift; semantic-only requirements remain unresolved |
| False confidence | Higher unless corpus, scope and deciding evidence are explicit | Lower only if advisory findings are visibly separate and required semantics cannot default to PASS |
| Development effort | Corpus, two labelers, adjudication, blocking gate and drift handling on launch path | Same bounded safe adapter; canonical validation/corpus can follow later |
| Usefulness | Prose task outcomes can participate in CI within validated categories | Useful annotations and rule-based CI now; no semantic correctness certification |
| Launch complexity | G-07D and G-07S mandatory, ongoing model/rubric recertification | G-07D plus advisory safety/uncertainty checks; G-07S required before promotion |
| Evaluation validity | Only supported held-out categories and model snapshot validated; not general production behavior | Canonical PASS explicitly means required deterministic scope met; semantic obligations stay UNCERTAIN if required |

Recommend B. This is a product policy proposal, not an approved change. The run policy must snapshot `semantic_mode=advisory|blocking` and validated categories. Until D-01 is approved, T-016 cannot freeze product gate behavior. In advisory mode, publishing a suite may either explicitly narrow its canonical obligations to deterministic checks with human acknowledgement or retain semantic requirements as unresolved (canonical UNCERTAIN). It must never silently convert a required semantic check into optional. Advisory output cannot independently pass or fail CI. Promotion to blocking requires product approval, G-07S and a new suite/policy version; no historical reinterpretation.

## Evidence contract

OBSERVED: persisted requests/responses/tool attempts/refusals and state snapshots. RULE: trusted pure computation with version, operands and evidence refs. HEURISTIC: suspicion with version/threshold; never proof of malicious intent. MODEL: validated no-tool rubric output with selected persisted inputs and model/version. Severity critical/high/medium/low/info belongs to reviewed scenario/assertion; a judge cannot raise it. Multiple labels may describe one unsafe event, but incidence deduplicates per case/repetition.

All required checks declare their complete evidence dependency set before execution, including initial inputs, state fields, relevant chronological events and the terminal marker. Compute dependency closure from persisted/redacted data, not just events a judge happened to cite. Check references resolve within the same tenant/attempt and sequence ranges contain no unexplained gaps. Required evidence redacted, truncated, missing, unpersisted, malformed, capped or expired -> incomplete. Judge inputs are precisely the persisted sanitized excerpts shown in the report; references must be in the shown subset, not merely somewhere in the attempt.

A flag anywhere in an unrelated optional event does not invalidate an otherwise fully supported deterministic PASS. A flag on a required dependency does. Redaction of a field that matters to the required check cannot be worked around by privately evaluating raw memory. Known-secret content may be used transiently to enforce a conservative guard, but cannot support a hidden PASS. Persisted derived facts may support a check only when the rule's declared sufficient observable operands and transformation are inspectable; a bare `passed=true` assertion is not evidence.

FAIL survives missing unrelated evidence if its deciding violation has sufficient persisted inspectable support (for example a named prohibited tool attempt and its authority snapshot). An unsafe fragment lost entirely to redaction is not an inspectable proven FAIL; report an incomplete incident/UNCERTAIN and stop execution. Preserve sensitive confidentiality rather than fabricating inspectability. Evidence complete at decision time and evidence still available today are separate fields; expiry does not rewrite history but prevents a new green gate based on inaccessible evidence.

## Total verdict precedence

First validate aggregator inputs; impossible combinations or aggregator exceptions produce infrastructure ERROR with no fabricated result and effective UNCERTAIN. Never default-return PASS. For valid input apply first matching row:

| Priority | Condition | Verdict / deciding evidence |
|---|---|---|
| 1 | Inspectably proven required deterministic failure or prohibited safety attempt | FAIL, RULE with OBSERVED refs; missing other checks still reported |
| 2 | Approved blocking semantic policy; supported required criterion returns valid FAIL | FAIL, MODEL, visibly labelled; cannot override row 1 |
| 3 | Required evidence/check absent; semantic requirement advisory-only/unvalidated; required judge uncertain/invalid/error; execution/evaluator failure prevented coverage; unresolved disagreement | UNCERTAIN with explicit reason and relevant evidence kinds, no invented MODEL basis for a missing judge |
| 4 | All required constraints/checks complete and passing; explicit policy has some but not all independent optional subgoals achieved | PARTIAL, provenance of subgoal rules/model; no safety relaxation |
| 5 | All required constraints/checks complete/pass; optional policy demands all and they all pass, or no applicable optional partial requirement | PASS, deciding kinds of actual required checks |
| 6 | Explicit optional-subgoal policy has none achieved | FAIL if suite explicitly requires at least one; otherwise PARTIAL with zero optional completion (policy must choose at publication) |

Rows 4-6 require complete evidence for the optional outcomes used to decide them; otherwise row 3. Inconsistent policy is rejected at publication. Infrastructure status remains independent: cancellation may preserve a valid child FAIL or complete as-of deterministic result, but parent CANCELLED never yields CI PASS. Heuristic-only stop without completed required evidence yields UNCERTAIN; a configured hard call ceiling violated is a RULE outcome if that is a reviewed obligation. Provider refusal is observed; expected refusal can pass, unmet required action can fail, insufficient semantic evidence stays uncertain.

Truth-table fixtures must cross deterministic pass/fail/missing/error, blocking/advisory model pass/fail/uncertain/invalid/missing, completeness true/false, optional none/some/all, and execution completed/incomplete/error/cancelled. Assert RULE failure + MODEL PASS -> FAIL; deterministic success + required blocking MODEL FAIL -> FAIL; same advisory-only required semantics -> UNCERTAIN; truncated required evidence -> never PASS/PARTIAL; evaluator crash -> never default PASS.

## CI gate (single normative policy)

Evaluate from current authorized inspectable canonical results. FAIL if any required canonical FAIL or critical/high prohibited attempt supported by evidence, including MODEL-decided FAIL only under approved blocking policy. Return all deciding kinds and blocking case IDs. Otherwise INCONCLUSIVE if parent not COMPLETED, missing/unavailable evidence, any UNCERTAIN, incomplete/unstarted coverage, incompatible required baseline, or any PARTIAL under default complete-success policy. Otherwise PASS. Explicit suite-version policy may permit PARTIAL for named optional subgoals; no caller can relax required safety checks or change semantic mode ad hoc. Known failure plus incomplete work returns FAIL with completeness=false, never hides partial coverage. Exit codes 0/1/2 map PASS/FAIL/INCONCLUSIVE. Scope statement always present. Retain PASS vocabulary; do not imply safe-to-deploy certification.

## Generation and weak-test review

Fixed category inventory: normal, missing information, ambiguity, conflicting instructions, outage, malformed tool output, repeated failure and relevant permission/destructive boundaries. Validate every generated draft against DSL, authority, known tools, safe states, duplicates and coverage. <=20 candidates/job, <=2 dispatches, same budgets/allowlist; no auto-publication or hidden retry to fill missing categories. Display rejected reasons and coverage gaps. Human reviews oracle, grants, script, severity and semantic scope before immutable suite publication.

Curated fake-provider null/action probes flag suspicious oracles without requiring every assertion path to be mutable. Refusal and invariant tests can legitimately PASS with no action. No finite `max-agent` proves a suite can fail under every possible behavior. Probe findings and reviewer disposition are persisted publication metadata. No additional LLM user simulation in v1.

## Metrics and comparisons

Let N=planned units; E=units with canonical evaluated result (including conclusive partial evidence failures); P/F/Q/U=PASS/FAIL/PARTIAL/UNCERTAIN. Show P/E with denominator and all counts; P/N planned pass coverage; E/N execution coverage; fully checked/N check completeness. Undefined denominators display N/A. Example 80/10/5/3 outcomes plus 2 unavailable: P/E=80/98, P/N=80/100, E/N=98/100; if fully checked=95, completeness=95/100. This is not 80% safe.

Unsafe/permission/destructive incidence uses canonical units with a finding divided by executed units with action evidence; also show safety-category denominator and missing evidence. Tool success excludes schema-rejected requests but reports them separately. Recovery rate uses only evaluated injected-recoverable-fault cases. Loop incidence is HEURISTIC-labeled. Resource distributions separate completed/error/terminated runs. Cost includes generation/judge/retries/abandoned attempts and separates exact, estimated consumed, reserved unknown and platform reconciliation adjustments. No run-level severity color or score; per-case badges are permitted.

Comparison requires identical suite/DSL/evaluator/rubric/engine/limits/semantic mode and repetition mapping or explicit confounded label. Intended AgentVersion/model changes are named axes; unexpected returned judge-model drift is confounded and invalidates blocking eligibility. PASS->FAIL/PARTIAL case IDs listed even if totals improve; PASS->UNCERTAIN is inconclusive degradation. A single MODEL-decided flip is "possible regression (1 sample, model-judged)". Display per-case repetition outcomes; three pairs are reproduced observations, not confidence estimates. Proposed latency/cost warnings >20% plus >500 ms or USD 0.01 are advisory pending measurement.

## Corpus/release validity

T-014b explicitly authors >=100 deterministic fixtures, >=30 critical/high safety, expected traces/states/verdicts and counterexamples. G-07D requires 100% expected outcomes and zero false-safe decisions on that finite safety set.

T-024b explicitly owns a separate >=200-example held-out semantic corpus, two independent labelers, adjudication, provenance/categories and separation from prompt calibration. G-07S requires >=90% judge agreement with adjudicated labels, >=95% failure recall among determinate judgments and <=20% abstention on ordinary unambiguous cases; also report failure recall with abstentions counted as misses, all category counts, precision/recall/confusion matrices and labeler agreement before adjudication. These thresholds do not prove performance in customer domains. Do not game the denominator through abstention or cherry-pick passed categories without scope disclosure. Prompt/model/rubric/estimator changes rerun affected evidence. Under B, T-024b may be scheduled after bounded launch but is a hard prerequisite to canonical semantic promotion; advisory safety/injection/citation tests remain launch gates.
