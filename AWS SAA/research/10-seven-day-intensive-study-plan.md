# AWS SAA-C03 — 7-Day Intensive Study Plan

**Built for:** an 11+ year cross-cloud (AWS/GCP/Azure/Kubernetes) architect who already holds CKAD and
does not need cloud fundamentals explained — this plan spends 100% of its time on AWS-specific
service boundaries, trade-offs, and exam pattern-recognition, using the study materials already
built in this repo (`AWS SAA/research/*` and `AWS SAA/domain*-*.md`). No new material is created by
this plan — every block cites an exact existing file/section.

## How domain weight maps to day allocation

| Days | Domain | Official Weight | Why this many days |
|---|---|---|---|
| Day 1 + Day 2 | Domain 1 — Design Secure Architectures | **30%** | Highest-weighted domain *and* the highest-confusion-risk domain (IAM policy evaluation, KMS vs IAM policy interplay, Object Lock, Cognito) per `research/01-exam-snapshot-and-priority-matrix.md` §6 — gets the most days, the most questions (120 total), and is the only domain re-swept in full on Day 6's trap-mastery pass. |
| Day 3 + Day 4 | Domain 2 — Design Resilient Architectures | 26% | Second-highest weight; Domain 1+2 together are 56% of the scored exam, which is why they consume 4 of the week's 6 content days. |
| Day 5 | Domain 3 — Design High-Performing Architectures | 24% | Officially near-tied with Domain 2, but the priority matrix rates it the *lowest* average confusion-risk domain ("mostly a know-the-right-service-for-the-job exercise") — one intensive day is sufficient depth. |
| Day 6 | Domain 4 — Design Cost-Optimized Architectures | 20% | Lowest weight — paired with the cross-domain distractor/trap/dilemma library so the lightest domain still gets a full heavy day. |
| Day 7 | Integration | All | Data-driven remediation of whatever Days 1–6 revealed as weak, plus the final readiness mock. |

## Standing protocols used every day (defined once, referenced daily)

**Mistake-tracker protocol (used in every "Review Incorrect Answers" block):** For every question
you get wrong — in question-practice sets, rapid-fire, or mocks — log four things in a running
notes file: (1) the topic tag, (2) the one-sentence reason you picked the wrong answer, (3) the
"decisive difference" sentence that would have saved you (look it up), (4) which trap/distractor
category it matches in `research/06a-distractor-patterns.md` or `research/06c-exam-traps.md` (all
50 traps). If a miss doesn't already have a one-line rule in `research/03-one-line-architect-rules.md`,
write one in the same "If X, then Y instead of Z" format and append it — you are extending your own
cheat sheet all week.

**Weak-area drill protocol:** At the end of each day's question practice, tally misses by sub-topic
tag. Whichever sub-topic has the most misses gets the day's dedicated Weak Area Drill slot: a quick
re-read of its source section, then a re-attempt of the missed questions plus a handful of fresh
ones on the same sub-topic. Day 7's entire refresh/comparison/practice load is this protocol applied
across the whole week using the mistake tracker as input.

**Time discipline:** Question-practice blocks assume ~1.5–2 min/question for someone at this
experience level (read scenario, eliminate distractors, answer) plus inline explanation reading.
Mock exams are run as a hard 130-minute timer with no notes, exactly like exam day, followed by a
separate untimed review pass.

---

## Day 1 — Domain 1, Part A: Identity, Access & Organizational Guardrails

**Knowledge Refresh (60 min)**
- `research/05d-security-iam-mastery.md` — sections "IAM Fundamentals: Users, Groups, Roles",
  "Policy Types & Structure", "Policy Evaluation Logic", "STS, AssumeRole, Cross-Account Access",
  "Federation & IAM Identity Center", "Permission Boundaries vs SCPs vs Resource Policies", "AWS
  Organizations & SCPs" (~40 min).
- `research/01-exam-snapshot-and-priority-matrix.md` §6 — re-read the P0 rows for "IAM", "STS /
  cross-account access / AssumeRole", "IAM Identity Center / SCPs / Organizations" (~10 min).
- `research/03-one-line-architect-rules.md` rules #1–21 (IAM/STS/root-account rules) — read once for
  rapid recall (~10 min).

**Architecture Comparison (60 min)** — for each pair, say the decisive-difference sentence out loud
before checking the source (pull trigger phrases from `research/03-trigger-word-dictionary.md`
entries under "cross-account", "federation", "least privilege", "revoke"):
1. IAM Role vs IAM User/long-term keys vs resource-based policy — who authenticates how.
2. Permission Boundaries vs SCPs vs identity/resource policies (`05d`'s disambiguation table).
3. IAM Identity Center vs SAML federation vs Cognito Identity Pools — workforce vs customer identity.
4. STS AssumeRole vs AssumeRoleWithSAML vs AssumeRoleWithWebIdentity.
5. Evaluation precedence when an SCP deny, a permission boundary, and an identity-policy allow all
   overlap on the same action.

**Question Practice:** 40 questions —
- All 20 in `AWS SAA/domain1-iam-access-management-questions.md`.
- Question Bank Q1–20 (Domain 1) in `research/07-question-bank.md` — this exact range is
  IAM/STS/Organizations/federation content only.

**Review Incorrect Answers (20 min):** Standard mistake-tracker protocol above. Cross-check any miss
against `research/06c-exam-traps.md` Trap 4 (hardcoded IAM keys) and any IAM-tagged pattern in
`research/06a-distractor-patterns.md`.

**Weak Area Drill (30 min):** Tally misses by sub-topic (policy evaluation / STS session chaining /
permission boundaries vs SCP / federation). Re-read that sub-topic's `05d` section once more, then
re-attempt the missed questions plus 5 fresh ones from the same Domain 1 Q1–20 pool style.

**Rapid-Fire block:** "Security & IAM" section of `research/08-rapid-fire-questions.md` — all 20,
timed under 45 sec/question.

**Mock Exam:** None — first content day.

**Total Daily Time:** ~4.5 hours.

---

## Day 2 — Domain 1, Part B: Data Protection, Network & Detective Security (heaviest content day)

This is the single densest day of the week by design — Domain 1 is the exam's largest domain (30%)
and this completes it.

**Knowledge Refresh (60 min, run as two 30-minute halves)**
- *Data protection (30 min):* `research/05d-security-iam-mastery.md` sections "KMS: Managed Keys,
  Key Policies, Envelope Encryption, Rotation" and "Secrets Manager vs Systems Manager Parameter
  Store"; cross-check S3 encryption facts in `research/02-service-comparison-matrix.md` → Storage →
  "S3 vs EBS vs EFS — Core Comparison" encryption row and "S3 Storage Classes" section.
- *Network & detective security (30 min):* `05d` sections "WAF vs Shield vs Firewall Manager",
  "ACM", "CloudTrail", "AWS Config", "GuardDuty", "Macie", "Security Hub", "Cognito: User Pools vs
  Identity Pools", and "Cross-Cutting Exam Heuristics" (Detect vs Prevent vs Respond); plus
  `research/05a-networking-mastery.md` "Security Groups vs NACLs" table.

**Architecture Comparison (60 min)** — 8 pairs, ~7–8 min each (use
`research/03-trigger-word-dictionary.md` entries for "encrypt", "detect", "compliance", "malicious
IP", "DDoS" to anchor each):
1. SSE-S3 vs SSE-KMS vs SSE-C vs client-side encryption (KMS request-rate-limit gotcha at scale).
2. Secrets Manager vs SSM Parameter Store SecureString (rotation is the deciding factor).
3. S3 Object Lock Governance mode vs Compliance mode.
4. Security Groups vs NACLs (stateful/allow-only vs stateless/allow+deny, instance vs subnet level).
5. WAF vs Shield Standard vs Shield Advanced.
6. GuardDuty vs Macie vs Security Hub vs Inspector (threat detection vs PII discovery vs posture
   aggregation vs vulnerability scanning).
7. Cognito User Pools vs Identity Pools (authentication directory vs temporary AWS credential vending).
8. CloudTrail vs AWS Config (who/when actor vs current-state/compliance drift).

**Question Practice:** 80 questions, run as two blocks matching the refresh split —
- *AM block:* all 20 in `AWS SAA/domain1-secure-architectures-practice.md` (KMS/Secrets/S3) +
  Question Bank Q21–40 in `research/07-question-bank.md` (same KMS/Secrets/S3 range).
- *PM block:* all 20 in `AWS SAA/domain1-network-identity-security-questions.md` (SG/NACL/WAF/
  GuardDuty/Cognito) + Question Bank Q41–60 (same network/detective-security range).

**Review Incorrect Answers (30 min):** Standard protocol. Add any new KMS/S3/SG-NACL one-liners to
`research/03-one-line-architect-rules.md`.

**Weak Area Drill (30–40 min):** KMS-key-policy-vs-IAM-policy interplay and S3 Object Lock
governance/compliance are flagged "Confusion Risk: High" in the priority matrix and are the two
facts most likely to trip up a non-AWS-native architect. Re-derive rule #17 (KMS cross-account
access) from `03-one-line-architect-rules.md` from memory before checking it; if wrong, spend the
remaining time re-running only KMS/Object-Lock-tagged questions from today's Q21–40 set.

**Rapid-Fire block:** "Networking" section of `research/08-rapid-fire-questions.md` (20 Qs) — chosen
because SG/NACL/VPC-security content overlaps this category.

**Mock Exam:** Mock Exam 1 (*Foundation/medium baseline*, `research/09-mock-exam-1.md`) — full 65Q,
130-minute timer, one sitting, then a separate untimed review pass. Domain 1 (Q1–20 of the mock) is
now fully studied, so this gives an early whole-exam diagnostic baseline and flags exactly which
Domain 2–4 gaps to prioritize before those days.

**Total Daily Time:** ~7 hours (the week's heaviest day — split into two sessions if needed).

---

## Day 3 — Domain 2, Part A: Resilience, Fault Tolerance & Disaster Recovery

**Knowledge Refresh (60 min)**
- `research/05g-ha-dr-mastery.md` — full file: "Availability Zones & Failure Domains", "Regional vs
  Global Services", "Multi-AZ Architecture Patterns", "Multi-Region Architecture", "Auto Scaling —
  Exam Decision Points", "Eliminating Single Points of Failure", and "DR Strategies — Backup &
  Restore, Pilot Light, Warm Standby, Multi-Site Active-Active" including its "Quick Classification
  Heuristic for Ambiguous Wording".
- `research/02-service-comparison-matrix.md` → Databases → "4. Multi-AZ vs Read Replica".

**Architecture Comparison (60 min):**
1. Multi-AZ vs Read Replica (availability/failover vs read-scaling — the #1 cross-cloud confusion).
2. RDS classic Multi-AZ (non-readable standby) vs Aurora Multi-AZ (readable replicas) vs Aurora
   Global Database.
3. ASG health check type: EC2 status check vs ELB health check vs custom/Lambda-based.
4. Backup & Restore vs Pilot Light vs Warm Standby vs Multi-Site Active-Active — RTO/RPO ladder and
   cost ladder.
5. Lambda reserved vs provisioned vs unreserved concurrency (resilience/throttling angle).

**Question Practice:** 34 questions —
- All 17 in `AWS SAA/domain2-resilient-architectures-questions.md` (ASG, Lambda resilience, DR
  strategy selection).
- Question Bank Q61–86 (first half of the 52 Domain 2 questions) in `research/07-question-bank.md`.

**Review Incorrect Answers (20 min):** Standard protocol. Specifically check any Multi-AZ miss
against `research/06c-exam-traps.md` Trap 1 ("Multi-AZ mistaken for a read-scaling feature") — the
single most common Domain 2 trap for candidates from other clouds.

**Weak Area Drill (30 min):** DR-strategy selection (matching RTO/RPO wording to the 4 named
strategies) is the highest-confusion Domain 2 item for candidates without AWS-specific DR
experience. Re-read `research/04-architecture-patterns.md` → "Security & Disaster Recovery
Patterns" section and redo any DR-strategy questions missed today.

**Rapid-Fire block:** "Compute & Serverless" section of `research/08-rapid-fire-questions.md` (20
Qs) — overlaps ASG/Lambda-resilience content.

**Mock Exam:** None today.

**Total Daily Time:** ~4.5 hours.

---

## Day 4 — Domain 2, Part B: Load Balancing, DNS Routing & Decoupled/Event-Driven Architectures

**Knowledge Refresh (60 min)**
- `research/05f-serverless-messaging-mastery.md` — full file, especially "Decoupling Deep-Dive: SQS
  vs SNS vs EventBridge vs Kinesis", "Step Functions", "Event-Driven Architectural Patterns".
- `research/02-service-comparison-matrix.md` → Networking "1. ALB vs NLB vs Gateway Load Balancer"
  and "2. Route 53 Routing Policies"; and the full Messaging section (items 1–6).
- Quick re-skim of `research/05g-ha-dr-mastery.md` → "Elastic Load Balancing — ALB vs NLB vs GWLB"
  and "Route 53 for Failover & DNS-Based HA" (already read Day 3 — this is reinforcement only).

**Architecture Comparison (60 min):**
1. ALB vs NLB vs Gateway Load Balancer.
2. Route 53 routing policies: simple / weighted / latency / failover / geolocation / geoproximity /
   multivalue.
3. SQS vs SNS vs EventBridge (point-to-point vs pub-sub vs schema-aware event bus/routing).
4. SQS Standard vs FIFO.
5. Kinesis Data Streams/Data Firehose vs SQS (ordered replay/streaming vs simple queue).
6. Step Functions vs EventBridge (orchestration vs choreography).
7. VPC Peering vs Transit Gateway (hub-and-spoke at scale).

**Question Practice:** 35 questions —
- All 18 in `AWS SAA/domain2-ha-loadbalancing-routing-questions.md`.
- All 17 in `research/07a-domain2-decoupling-questions.md`.
- (Question Bank Q87–112 — the remaining half of Domain 2's 52 bank questions — is this week's
  overflow buffer if time remains or for Day 7 remediation.)

**Review Incorrect Answers (20 min):** Standard protocol. Check any fan-out/DLQ/ordering miss
against `research/06a-distractor-patterns.md` Example B (SNS→SQS fan-out vs. polling anti-pattern).

**Weak Area Drill (30 min):** Route 53 routing-policy selection and the SNS-vs-EventBridge boundary
are the two highest-confusion Domain 2 items per the priority matrix. Re-drill the
`research/03-trigger-word-dictionary.md` entries for "fan-out", "decouple", "geoproximity", and
"failover routing".

**Rapid-Fire block:** "Messaging, Migration & Cost" section of `research/08-rapid-fire-questions.md`
(20 Qs).

**Mock Exam:** Mock Exam 2 (*Realistic exam level*, `research/09-mock-exam-2.md`) — full 65Q timed.
Domains 1 and 2 (56% of the exam) are now both complete, so this is a clean mid-week checkpoint.

**Total Daily Time:** ~7 hours.

---

## Day 5 — Domain 3: High-Performing Architectures — Compute, Storage, Database & Network Performance

**Knowledge Refresh (60 min)**
- `research/05e-compute-scaling-mastery.md` — "EC2 Instance Families", "ECS vs EKS vs Fargate
  Scaling Behavior", "Lambda Concurrency & Scaling Model", "DynamoDB & Aurora Scaling" (~30 min).
- `research/05b-storage-mastery.md` and `research/05c-database-mastery.md` — skim specifically for
  performance facts: EBS io2 Block Express, EFS Max I/O vs General Purpose throughput mode, DAX vs
  ElastiCache, RDS Proxy connection pooling (~20 min).
- `research/05h-global-cost-performance-mastery.md` — "CloudFront + Global Accelerator — Combined
  and Contrasted", "Route 53 Routing Policies — When Each Wins" (~10 min).

**Architecture Comparison (60 min):**
1. EC2 vs Lambda (compute-selection logic, `research/02-service-comparison-matrix.md` → Compute #1).
2. ECS vs EKS vs Fargate (operational model + scaling behavior, Compute #3–4).
3. EBS volume types decision tree (gp3 / io2 Block Express / st1 / sc1).
4. EFS vs FSx family.
5. DynamoDB DAX vs ElastiCache (microsecond item-cache vs general-purpose cache).
6. ElastiCache Redis vs Memcached.
7. CloudFront vs Global Accelerator.
8. Direct Connect vs Site-to-Site VPN (latency/performance framing, not the hybrid-cost framing —
   that returns on Day 6).

**Question Practice:** 32 questions —
- All 16 in `AWS SAA/domain3-performance-questions.md` (S3/EBS/EFS/RDS-Aurora/DAX/ElastiCache).
- All 16 in `research/07-domain3-performance-questions.md` (CloudFront/Global Accelerator/Direct
  Connect/Transit Gateway/Route 53 latency routing).

**Review Incorrect Answers (20 min):** Standard protocol. Check any CloudFront-vs-Global-Accelerator
miss specifically against `research/06c-exam-traps.md` Trap 6.

**Weak Area Drill (30 min):** Domain 3 is the lowest average confusion-risk domain overall — the two
genuinely high-confusion items are CloudFront vs Global Accelerator and DAX vs ElastiCache. Spend
the full 30 minutes re-running only those two comparisons against 5 fresh Domain 3 questions pulled
from Question Bank Q113–160 in `research/07-question-bank.md`.

**Rapid-Fire block:** "Storage & Database" section of `research/08-rapid-fire-questions.md` (20 Qs).

**Mock Exam:** Mock Exam 3 (*Realistic level with difficult distractors*,
`research/09-mock-exam-3.md`) — full 65Q timed.

**Total Daily Time:** ~7 hours.

---

## Day 6 — Domain 4: Cost-Optimized Architectures + Cross-Domain Distractor & Trap Mastery

**Knowledge Refresh (60 min)**
- `research/05h-global-cost-performance-mastery.md` — cost-focused sections: "EC2 Purchase Models —
  Decision Boundary", "Savings Plans vs Spot — the Real Trade-off", "Auto Scaling for Cost", "Lambda
  Cost Reasoning", "S3 Storage Classes & Lifecycle", "DynamoDB Capacity Modes", "RDS/Aurora Scaling
  Cost Reasoning", "NAT Gateway Cost Traps", "VPC Endpoints for Cost Savings", "Data Transfer Cost
  Reasoning".
- `research/02-service-comparison-matrix.md` → Compute "6. EC2 Purchasing Options" and its
  "Cross-cutting cost-optimization exam heuristic (Domain 4, 20%)" callout; Storage "5. S3 Standard
  vs Intelligent-Tiering (Deep Dive)".

**Architecture Comparison (60 min):**
1. On-Demand vs Reserved Instances vs Savings Plans (Compute vs EC2 Instance) vs Spot.
2. S3 lifecycle transitions across storage classes (Standard → IA → Intelligent-Tiering → Glacier
   tiers → Deep Archive) with the retrieval-time/cost trade-off at each step.
3. DynamoDB On-Demand vs Provisioned capacity (+ Application Auto Scaling).
4. NAT Gateway vs VPC Gateway/Interface Endpoint — the cost angle (see `06c` Trap 2).
5. Aurora Serverless v2 vs provisioned Aurora vs standard RDS (cost-scaling).
6. Savings Plans vs Reserved Instances — flexibility vs discount-depth trade-off.

**Question Practice:** 40 questions —
- All 20 in `AWS SAA/domain4-cost-optimization-questions.md`.
- All 20 in `AWS SAA/domain4-storage-database-networking-cost-questions.md`.

**Review Incorrect Answers (20 min):** Standard protocol.

**Weak Area Drill — Full Distractor & Trap Sweep (60 min, expanded today in place of a single-topic
drill):** This is the week's cumulative "how AWS tricks you" pass, covering all domains at once:
- Read all of `research/06a-distractor-patterns.md` start to finish.
- Read all 50 traps in `research/06c-exam-traps.md` (both 25-trap batches).
- Work all 50 dilemmas in `research/06b-two-answer-dilemmas.md`, timed — these are deliberately in
  the two-plausible-answers format that mirrors the exam's hardest question type.
- Pull your full mistake-tracker log from Days 1–5 and re-tag every miss against a specific
  trap/distractor pattern number. Anything that doesn't map to a documented pattern is a genuine
  personal blind spot — flag it for extra attention on Day 7.

**Rapid-Fire block (expanded, 30 min):** Re-run only the questions you got wrong across all 5
categories of `research/08-rapid-fire-questions.md` on Days 1–5, plus a fresh full pass of whichever
single category had your lowest Day 1–5 accuracy.

**Mock Exam:** Mock Exam 4 (*Harder than the real exam*, `research/09-mock-exam-4.md`) — full 65Q
timed. All four domains are now covered, and this is deliberately the hardest of the five mocks,
taken on the day with the freshest cross-domain trap awareness.

**Total Daily Time:** ~8 hours — the week's peak-load day by design (full domain + the entire
distractor/trap/dilemma library + the hardest mock). Split into two sessions (e.g., AM content, PM
mock) if a single sitting isn't realistic.

---

## Day 7 — Final Integration, Weak-Area Remediation & Exam Readiness

Nothing here is pre-scripted by topic — it is entirely driven by what your mistake tracker and Mock
Exams 1–4's domain sub-scores show as your weakest areas.

**Knowledge Refresh (60 min):** No new material. Re-read your own mistake-tracker log end-to-end,
then re-read all ~104 rules in `research/03-one-line-architect-rules.md` once straight through, and
skim every "Common Traps" callout box in `research/02-service-comparison-matrix.md` for the one or
two domains where your Day 1–6 accuracy was lowest.

**Architecture Comparison (60 min):** Re-drill only the comparison pairs you got wrong at least once
this week, pulled from the mistake tracker. Highest-probability candidates based on typical
cross-cloud blind spots: SG vs NACL, KMS key policy vs IAM policy interplay, ALB vs NLB vs GWLB, the
S3 storage-class/lifecycle chain, SNS vs EventBridge, Multi-AZ vs Read Replica, NAT Gateway vs VPC
Endpoint. For each, say the decisive-difference sentence from memory before checking the source.

**Question Practice:** 20–25 targeted questions pulled by tag from whichever single domain scored
lowest across Mock Exams 1–4 (check each mock's per-domain breakdown) — draw from that domain's
still-unused rows in `research/07-question-bank.md` (e.g., the Domain 2 Q87–112 overflow from Day 4,
or any Domain 3/4 rows not reached on Days 5–6).

**Review Incorrect Answers (15 min):** Final pass — anything still missed today goes onto a one-page
"exam-morning" list of the 10–15 facts you keep getting wrong, to re-read right before the exam.

**Weak Area Drill (20 min):** Work through the 5 diagram-critique exercises in
`research/04-diagram-critique-exercises.md` tagged closest to your weakest domain (all 20 exercises
are there if you haven't touched this file yet — Exercises 6–9, 11–12, 17–18 skew security;
1–2, 10, 16, 19–20 skew resilience; 3–5, 13–15 skew performance).

**Rapid-Fire block:** Full 100-question timed sweep of `research/08-rapid-fire-questions.md` as a
final speed-recall calibration — target under 30 minutes at >90% accuracy; whichever category falls
short is your last focused review before the exam.

**Mock Exam:** Mock Exam 5 (*Final readiness assessment*, `research/09-mock-exam-5.md`) — full 65Q,
under full exam conditions (130-minute hard timer, one sitting, no notes). Scoring benchmark: since
these are unscaled 65-question mocks at full difficulty (harder on average than the live exam's mix
of 50 scored + 15 unscored pretest items), treat **≥80% raw correct (52/65)** as a strong go signal
against the real 720/1000 (~72%) pass bar. Below that, use the per-domain breakdown to pick a single
domain for one more focused evening review pass before exam day.

**Total Daily Time:** ~6.5 hours.

---

## Week-at-a-glance

| Day | Domain Focus | Weight Represented | Mock | Est. Total Time |
|---|---|---|---|---|
| 1 | Domain 1A — Identity, Access, Org Guardrails | 30% | — | ~4.5 h |
| 2 | Domain 1B — Data Protection, Network/Detective Security | 30% | Mock 1 (Foundation) | ~7 h |
| 3 | Domain 2A — Resilience, Fault Tolerance, DR | 26% | — | ~4.5 h |
| 4 | Domain 2B — Load Balancing, Routing, Decoupling | 26% | Mock 2 (Realistic) | ~7 h |
| 5 | Domain 3 — High-Performing Architectures | 24% | Mock 3 (Hard distractors) | ~7 h |
| 6 | Domain 4 — Cost Optimization + Trap Mastery | 20% | Mock 4 (Harder than real) | ~8 h |
| 7 | Integration, Remediation, Final Readiness | All | Mock 5 (Final readiness) | ~6.5 h |

**Total week commitment: ~44.5 hours.** This is deliberately intensive (well above the ~30–35 hour
baseline estimate in `research/01-exam-snapshot-and-priority-matrix.md`) because it fully exhausts
every study artifact already built (200-question bank, 100 rapid-fire questions, 50 patterns, 50
dilemmas, 50 traps, 5 mocks) rather than sampling from them. If time is tight, the safest place to
compress is the Question Bank supplement counts on Days 1–2 and 4–5 (keep the dedicated
domain-practice files in full; those are the most tightly scoped to each day's exact topic) — do not
cut Day 6's trap/distractor sweep or any of the 5 mocks.
