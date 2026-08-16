# AWS SAA-C03 — GO / NO-GO READINESS GATE

> **File-reference correction:** this plan was drafted referencing per-domain question files (e.g. `domain1-iam-access-management-questions.md`, `domain2-resilient-architectures-questions.md`) that do not exist as separate files. All 200 practice questions live in a single consolidated file, **`07-question-bank.md`**, organized by domain in this order:
> - Domain 1 (Design Secure Architectures): Questions 1-60
> - Domain 2 (Design Resilient Architectures): Questions 61-112
> - Domain 3 (Design High-Performing Architectures): Questions 113-160
> - Domain 4 (Design Cost-Optimized Architectures): Questions 161-200
>
> Wherever this plan names a per-domain question file, use the matching question-number range in `07-question-bank.md` instead. Rapid-fire questions are genuinely split by section within the single file `08-rapid-fire-questions.md` (Security & IAM 1-20, Networking 21-40, Storage & Database 41-60, Compute & Serverless 61-80, Messaging/Migration/Cost 81-100).


> Purpose: replace "I feel ready" with numbers you can actually fail against. Every threshold
> below is deliberately set with a safety margin above the 720/1000 (~72%) official pass bar,
> because (a) mock exams you wrote/curated yourself tend to run 5–10 points easier than the real
> item bank once you've seen the explanations, and (b) the real exam's 15 unscored pretest
> questions are indistinguishable from scored ones and can be unusually hard — you want slack to
> absorb both effects.

## 0. How to use this gate

Run it **after** you've been through all of: the 8 domain mastery deep-dives, the 104 one-line
rules, the 50 architecture patterns + 20 diagram exercises, the distractor/dilemma/trap training,
and at least one full pass through the 200-question bank and the 100 rapid-fire questions. Then
work through the 5 mock exams in sequence, scoring each honestly (see §4 for what "honest scoring"
means for someone with a pattern-matching-prone 11-year background). Do not re-take a mock you've
already seen the answers to and count it as a fresh data point — that measures memory, not
readiness.

---

## 1. Mock Exam Score Thresholds

| Requirement | Threshold | Why |
|---|---|---|
| Minimum attempts before judging readiness | **At least 3 of the 5 mock exams**, taken on separate sessions (not same day back-to-back) | One good score is noise; three establishes a trend and tests retention after a gap, which the real exam also requires (you won't sit it minutes after your last study session) |
| Minimum score, **each** of the last 3 mocks attempted | **≥ 80% (52/65)** | 720/1000 ≈ 72% scored-equivalent; 80% raw on a self-authored bank should map to comfortably-above-pass on the real, harder, professionally-calibrated item bank |
| Minimum score, **most recent** mock (the one right before booking) | **≥ 85% (56/65)** | This is your "book it" number — it should be your best or near-best result, not your average, showing an upward or stable trend rather than decay |
| Maximum spread across your last 3 attempts | **≤ 10 percentage points** | A 95% / 68% / 90% pattern means you're inconsistent (guessing well on some, not others) — that's a NO-GO signal even if the average clears 80% |
| Timing | **Finish with ≥ 15 minutes left on the clock**, on at least 2 of the last 3 mocks, without rushing the last 10 questions | 130 min / 65 Q = 2 min/question; real exam has denser scenario text than most home-built banks, so you need a demonstrated buffer, not just a completed run |

**Hard rule:** If any single one of the last 3 mocks scores below 75% (48/65 or fewer), treat that
as a reset — do not average it away. Diagnose why (a specific domain collapse? a timing crash? a
misread pattern?) and re-run the gate from a clean mock.

---

## 2. P0 Topic Accuracy (Domain 1: Security 30%, Domain 2: Resilience 26% — 56% of the exam)

Because Domains 1 and 2 are P0 and together are more than half the scored exam, they get a
**higher bar than the overall pass average**, not the same one.

| Topic cluster | Minimum accuracy | Source material to test against |
|---|---|---|
| IAM policy evaluation logic (explicit deny, boundaries, SCPs, resource policies, cross-account trust) | **≥ 90%** | `domain1-iam-access-management-questions.md`, `05d-security-iam-mastery.md` |
| KMS (key policies vs. IAM, envelope encryption, key rotation, grants) | **≥ 90%** | `05d-security-iam-mastery.md`, question bank Domain 1 items |
| Security service selection (GuardDuty/Macie/WAF/Shield/Inspector/Security Hub — "which service does X") | **≥ 85%** | `05d-security-iam-mastery.md`, `domain1-network-identity-security-questions.md`, `03-trigger-word-dictionary.md`, `06c-exam-traps.md` |
| VPC/network security (SG vs. NACL statefulness, VPC endpoints, Transit Gateway vs. Peering) | **≥ 90%** | `domain1-network-identity-security-questions.md`, `05a-networking-mastery.md` |
| Decoupling & resilience patterns (SQS/SNS/EventBridge, Multi-AZ/Multi-Region, failover, DR strategies) | **≥ 85%** | `domain2-resilient-architectures-questions.md`, `05f-serverless-messaging-mastery.md`, `05g-ha-dr-mastery.md` |
| **Combined Domain 1 + Domain 2 questions across all 5 mocks** | **≥ 88% overall** | Tag and tally by domain per mock, don't eyeball it |

If any single P0 cluster is below its bar, that cluster alone is a NO-GO regardless of overall
mock score — a strong Domain 3/4 result cannot compensate for a weak Domain 1 on the real
compensatory-but-heavily-weighted scoring model in practice, because Domain 1 is nearly a third of
all scored questions.

---

## 3. Domain-Specific Performance Bars (Networking / Storage / Database / HA-DR)

These four are called out separately because they're the highest-density "AWS-specific vocabulary
over familiar concepts" areas — exactly where 11 years of GCP/Azure/K8s intuition is most likely
to mislead via false-friend pattern matching (e.g., assuming an ALB behaves like a K8s Ingress
controller, or that VPC peering transitivity works like a mesh).

| Domain | Minimum accuracy | Notes |
|---|---|---|
| **Networking** (VPC, subnets, routing, NAT vs. IGW, VPN/Direct Connect, Transit Gateway, Route 53 routing policies, CloudFront) | **≥ 88%** | This is the area most contaminated by multi-cloud false-friend errors — score it in isolation from `05a-networking-mastery.md` and the networking-tagged mock questions |
| **Storage** (S3 storage classes + lifecycle, EBS vs. EFS vs. FSx, storage gateway, snapshot/backup mechanics) | **≥ 85%** | Numeric/pricing-adjacent recall (retrieval times, minimum storage durations) is a common silent-fail area — wrong-but-plausible answers here rarely "feel" wrong |
| **Database** (RDS Multi-AZ vs. read replicas, Aurora specifics, DynamoDB capacity modes/GSI-LSI, ElastiCache, migration tooling) | **≥ 85%** | Watch specifically for Multi-AZ (HA, not scaling) vs. read replica (scaling, not automatic failover) confusion — this is the single most common SAA trap pattern |
| **HA / DR** (RTO/RPO-driven strategy selection: backup-restore, pilot light, warm standby, multi-site active-active; Multi-AZ vs. Multi-Region) | **≥ 88%** | Every HA/DR question is really "match the RTO/RPO number in the scenario to the cheapest strategy that meets it" — score this as a distinct skill, not folded into Domain 2 generally |

Compute the above by filtering your question-bank and mock-exam results by tag/keyword, not by
memory or gut feel. If your tooling doesn't tag questions, manually bucket each missed question
into one of these four (plus "other") as you review mocks — this bucketing itself is valuable
diagnostic signal.

---

## 4. The "Explain, Don't Recognize" Requirement

This is the single most important qualitative gate for an experienced engineer, because 11 years
of adjacent-cloud pattern recognition makes it dangerously easy to select the correct answer on a
*familiar-looking* option shape without actually knowing the AWS-specific reason it's correct —
which fails silently on mocks (you get credit) and catastrophically on the real exam the moment
the distractor options are rephrased or reordered.

**The test:** For every question you get right in a mock or the question bank, without looking at
the explanation, you must be able to say out loud (or write one sentence) covering both:

1. **Why the correct answer is correct** — the specific AWS mechanism (e.g., "NACLs are stateless
   so the ephemeral-port return traffic needs an explicit inbound rule"), not just "that's the one
   that fits the scenario."
2. **Why each wrong answer is wrong** — the specific reason it fails, not "it's not the best fit."
   Distinguish between wrong-because-technically-broken (e.g., wildcard principal is a security
   hole) vs. wrong-because-suboptimal-but-technically-valid (e.g., NAT instance vs. NAT gateway —
   works, but wrong for the stated requirement).

**Threshold:** Self-audit a random sample of **20 already-correctly-answered questions** (mix of
mock exam + question bank) using this test. You need to pass the "explain all 4 options" bar on
**≥ 90% (18/20)** of them. Any question where you got the right answer but can't explain why a
specific distractor is wrong counts as a **fail on this audit**, even though it counts as correct
on the mock score — this is intentionally a stricter, independent check that catches
pattern-matched luck the raw score hides.

If you're below 18/20: your mock scores are overstating your real readiness. Go back through the
`06a-distractor-patterns.md`, `06b-two-answer-dilemmas.md`, and `06c-exam-traps.md` material
specifically, since these were built to force exactly this kind of reasoning, and re-run the audit
on a fresh sample before trusting your mock scores again.

---

## 5. READINESS SCORECARD

Self-score each cell honestly using the guidance below. Do this once per domain, after your third
mock exam attempt at the earliest (scoring earlier just measures how much material you've read,
not how ready you are).

| Domain | Knowledge (1–5) | Scenario Accuracy | Speed | Confidence |
|---|---|---|---|---|
| Domain 1: Secure Architectures (30%) | | | | |
| Domain 2: Resilient Architectures (26%) | | | | |
| Domain 3: High-Performing Architectures (24%) | | | | |
| Domain 4: Cost-Optimized Architectures (20%) | | | | |
| Networking (cross-domain) | | | | |
| Storage (cross-domain) | | | | |
| Database (cross-domain) | | | | |
| HA/DR (cross-domain) | | | | |

### How to score each column

**Knowledge (1–5 scale)**
- **1–2:** You'd need to look up the relevant service/feature to answer even a basic recall
  question (e.g., which storage class fits which access pattern).
- **3:** You recall the right service/feature most of the time but sometimes confuse
  boundary cases (e.g., mixing up when to use Transit Gateway vs. Peering).
- **4:** You reliably recall service boundaries and can state the "one-line rule" for this
  domain from `03-one-line-architect-rules.md` from memory, unprompted.
- **5:** You can explain the underlying AWS mechanism well enough to predict how an unfamiliar
  variant of a scenario in this domain would resolve, not just recall a memorized rule.

**Scenario Accuracy (use % from your tagged mock/bank results, then map)**
- **Low:** < 75% correct on this domain's tagged questions across your mocks + bank.
- **Medium:** 75–87%.
- **High:** ≥ 88% — and you pass the §4 "explain both directions" audit on this domain's questions.

**Speed**
- **Low:** You regularly need > 2.5 min/question on this domain's scenarios, or you skip and
  return to more than 1 in 5 of them.
- **Medium:** You average close to the 2 min/question budget but occasionally need to reread
  the scenario twice.
- **High:** You can identify the trigger words (per `03-trigger-word-dictionary.md`) and eliminate
  2 of 4 options within 30–45 seconds on most questions in this domain, leaving time to deliberate
  on the genuinely hard ones.

**Confidence**
- **Low:** You second-guess your answer after selecting it more than half the time in this domain.
- **Medium:** You second-guess occasionally, mostly on the genuinely ambiguous two-answer-dilemma
  style questions (which is normal and expected even at readiness).
- **High:** You commit to an answer and move on for routine questions in this domain, reserving
  deliberation only for questions you can identify as intentionally close-call (the 50 dilemmas
  category), not for questions you're simply unsure about.

---

## 6. Overall Classification Bands

Compute your overall band from the **worst-offending signal**, not an average — a single RED
signal in a P0 domain overrides three GREEN signals elsewhere, because the real exam won't average
your Domain 1 weakness away either.

### 🔴 RED — Not Ready

Concrete symptoms (any one of these is sufficient to stay RED):
- Fewer than 3 mock exams completed, or most recent mock score below 75% (48/65 or fewer).
- Any of the five §2 P0 sub-clusters (IAM, KMS, security service selection, VPC/network security,
  decoupling & resilience) below 80% — well under its own 85–90% bar — or the combined Domain 1+2
  score below 80%.
- Any of Networking, Storage, Database, or HA/DR tagged accuracy below 75% in §3.
- On the §4 explain-audit, you pass fewer than 14/20 (70%) — meaning a large share of your
  "correct" answers are pattern-matched guesses, not reasoned answers.
- You can recall *that* a rule exists (e.g., "NACLs are stateless") but cannot apply it to a novel
  scenario phrased differently than the one you memorized it from.

**What to do:** Return to the domain mastery deep-dives and one-line rules for the specific weak
domain(s); do not schedule the exam or take another mock until the specific gap is closed and
re-tested in isolation.

### 🟡 AMBER — Possible but Risky

Concrete symptoms (this is the "you could pass, but you're gambling with $150 and a 14-day
cooldown" zone):
- Overall mock average is in the 75–84% range with a spread greater than 10 points across your
  last 3 attempts (e.g., 90% / 78% / 82%) — inconsistency, not a floor problem.
- All five §2 P0 sub-clusters clear 80% (above the RED floor) but at least one hasn't reached its
  own §2 bar (90% for IAM/KMS/VPC-network-security, 85% for security-service-selection and
  decoupling-&-resilience), or the combined Domain 1+2 score sits at 80–87% (below the 88% floor);
  you're passing them, not mastering them.
- One of Networking/Storage/Database/HA-DR sits below its own §3 bar (Networking and HA/DR: 88%;
  Storage and Database: 85%) but no lower than 75%, while the other three individually clear their
  bars — an isolated soft spot rather than a systemic gap.
- §4 explain-audit lands at 15–17/20 (75–85%) — you reason correctly most of the time but still
  have a meaningful tail of lucky guesses that a rephrased distractor would expose.
- Timing is inconsistent: you finish comfortably on straightforward mocks but crash against the
  clock (< 5 min left, or guessing on the last 5–8 questions) on scenario-dense mocks.

**What to do:** Identify the *specific* isolated weak point (usually one domain or one skill —
timing, or one topic cluster) and drill it specifically with the relevant material, then retake
one fresh mock (not one you've seen) to confirm the fix before booking. Do not book "hoping it
averages out" — AMBER means you have a diagnosed, fixable gap, not a green light.

### 🟢 GREEN — Strong Chance of Passing

Concrete symptoms (all should be true, not just most):
- Last 3 mocks all ≥ 80%, most recent ≥ 85%, spread ≤ 10 points, and you finished each with
  ≥ 15 minutes to spare without rushing.
- All five §2 P0 sub-cluster bars are met (IAM ≥ 90%, KMS ≥ 90%, security service selection ≥ 85%,
  VPC/network security ≥ 90%, decoupling & resilience patterns ≥ 85%), the combined Domain 1+2
  score is ≥ 88%, and all four cross-domain bars (Networking ≥ 88%, Storage ≥ 85%, Database ≥ 85%,
  HA/DR ≥ 88%) in §3 are met simultaneously — no single weak pocket left unaddressed.
- §4 explain-audit ≥ 18/20: you can articulate why each wrong answer is wrong, not just which
  answer is right, on a near-random sample.
- On the 50 two-answer dilemmas and 50 exam traps specifically, you're catching the trap/distinguishing
  the two plausible answers correctly at a rate within 5 percentage points of your overall mock
  average (e.g., an 87% mock average should come with ≥ 82% on this 100-item set, not 60–65%) —
  this confirms your strong average isn't being propped up by easy questions alone.

**What to do:** Book the exam. Do one light final review pass (one-line rules + trigger-word
dictionary skim) within 48 hours of the exam date, but avoid cramming new material that could
introduce last-minute doubt into an already-solid mental model.
