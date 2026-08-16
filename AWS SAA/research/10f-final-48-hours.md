# AWS SAA-C03 — FINAL 48 HOURS BEFORE THE EXAM

> **File-reference correction:** this plan was drafted referencing per-domain question files (e.g. `domain1-iam-access-management-questions.md`, `domain2-resilient-architectures-questions.md`) that do not exist as separate files. All 200 practice questions live in a single consolidated file, **`07-question-bank.md`**, organized by domain in this order:
> - Domain 1 (Design Secure Architectures): Questions 1-60
> - Domain 2 (Design Resilient Architectures): Questions 61-112
> - Domain 3 (Design High-Performing Architectures): Questions 113-160
> - Domain 4 (Design Cost-Optimized Architectures): Questions 161-200
>
> Wherever this plan names a per-domain question file, use the matching question-number range in `07-question-bank.md` instead. Rapid-fire questions are genuinely split by section within the single file `08-rapid-fire-questions.md` (Security & IAM 1-20, Networking 21-40, Storage & Database 41-60, Compute & Serverless 61-80, Messaging/Migration/Cost 81-100).


*Assumes all core study materials in `AWS SAA/research/` are already built and have been worked
through at least once. This is a revision/consolidation plan, not a first-pass learning plan —
if any file below is still unread, that's a signal to push the exam date, not to cram it now.*

---

## 1. 48 HOURS BEFORE (Day −2 — the last "heavy" day)

This is the last day it's safe to do real cognitive work: one final timed mock, then convert every
miss into a targeted re-read. After today, everything is passive review only.

**Morning — one final timed mock exam (~130-minute block, done in one sitting, no pausing):**
- Pick whichever of `09-mock-exam-1.md` through `09-mock-exam-5.md` is least-drilled so far and run
  it under real conditions: 130 minutes, 65 questions, no notes, no lookups.
- This is diagnostic, not a new-content session — its only job is to surface which P0/P1 rows in
  `01-exam-snapshot-and-priority-matrix.md` (Section 6) are still shaky.

**Afternoon — turn every wrong/guessed answer into a targeted fix (~2–3h):**
- For every miss, trace it back to its domain and re-read the matching deep-dive:
  `05a-networking-mastery.md`, `05b-storage-mastery.md`, `05c-database-mastery.md`,
  `05d-security-iam-mastery.md`, `05e-compute-scaling-mastery.md`,
  `05f-serverless-messaging-mastery.md`, `05g-ha-dr-mastery.md`,
  `05h-global-cost-performance-mastery.md`.
- Cross-check any missed service-boundary question (e.g. ALB vs NLB, RDS vs Aurora, SQS vs SNS vs
  EventBridge) against `02-service-comparison-matrix.md` — read only the relevant "X vs Y" section,
  not the whole 1,284-line file.
- Re-read the full P0 row list in `01-exam-snapshot-and-priority-matrix.md` §6 (16 P0 items: IAM,
  STS/AssumeRole, Identity Center/SCPs, KMS, Secrets Manager vs Parameter Store, SG vs NACL, VPC
  design, NAT vs VPC Endpoints, S3 storage classes, S3 Object Lock, S3 encryption, RDS Multi-AZ vs
  Read Replicas, Aurora, DynamoDB, SQS/SNS/EventBridge, ALB/NLB/GWLB) — self-quiz out loud on each
  one before checking the answer.

**Evening — full read-through of the two densest recall assets (~1.5–2h, no new questions):**
- `03-one-line-architect-rules.md` — all 104 rules, top to bottom, one read, at pace. This is the
  single highest-density recall asset in the whole repo.
- `03-trigger-word-dictionary.md` — skim every trigger phrase heading ("most cost-effective,"
  "least operational overhead," "highly available," "decouple," etc.) and the "services that should
  immediately enter your mind" list under each; skip the worked example scenarios if time is tight.
- `06c-exam-traps.md` — read all 50 trap names + "correct mental model" line only.

---

## 2. 24 HOURS BEFORE (Day −1 — lighter, no new full mock)

The goal today is recognition speed, not new problem-solving. Everything is shorter, lower-stakes,
and stops well before evening.

- **Rapid-fire pass (~60–75 min):** `08-rapid-fire-questions.md` — all 100 items. These are
  designed for fast pattern-matching, not deep scenario reasoning, which is exactly the right
  intensity for this close to the exam.
- **Two-answer dilemma skim (~20–25 min):** `06b-two-answer-dilemmas.md` (the consolidated set of
  all 50 — the top-level `dilemmas-batch1.md` is an earlier, superseded draft covering only the
  first 25 of these same dilemmas verbatim, so skip it and don't burn time re-reading duplicates).
  Don't re-solve the scenarios, just read each "decisive difference (one sentence)" line. That
  sentence is the entire point of the exercise.
- **Re-open only your own miss list**, not new material: go back to whichever mock (from
  `09-mock-exam-*.md`) or the `07-question-bank.md` 200-question set produced wrong answers earlier
  in your prep, and re-read just those explanations. If you don't have a tracked miss list, skip
  this rather than re-running a full set cold.
- **One more skim of `03-one-line-architect-rules.md`** (10–15 min) — second exposure in 24 hours
  is what moves it from "recognized" to "automatic."
- **Domain-specific top-ups only where weak:** if one domain still feels soft, pick just one matching
  top-level file for a short targeted pass — not all of them, and not more than one domain today:
  Domain 1 → `domain1-secure-architectures-practice.md`, `domain1-iam-access-management-questions.md`,
  or `domain1-network-identity-security-questions.md`; Domain 2 →
  `domain2-resilient-architectures-questions.md` or `domain2-ha-loadbalancing-routing-questions.md`;
  Domain 3 → `domain3-performance-questions.md`; Domain 4 → `domain4-cost-optimization-questions.md`
  or `domain4-storage-database-networking-cost-questions.md`.
- **Stop studying by early evening.** Do something unrelated. Sleep is part of the prep plan, not a
  concession to it — pattern-recognition speed (which is what this exam actually tests) degrades
  with sleep debt faster than raw recall does.

---

## 3. EXAM MORNING (keep this short — 20–30 minutes total, no new material)

- Normal breakfast, no caffeine spike beyond your usual routine.
- One top-to-bottom skim of `03-one-line-architect-rules.md` (~10 min) — last full pass.
- One skim of the P0 topic *names only* in `01-exam-snapshot-and-priority-matrix.md` §6 (~3 min) —
  just the left column, not the full table.
- One skim of the 50 trap *titles* in `06c-exam-traps.md` (~5 min) — headings only, as a final
  "don't fall for this" priming pass.
- Confirm logistics: ID matches registration name exactly, Pearson VUE check-in time/location (or
  for OPI: room scan, no other devices/paper in the room, stable connection, webcam positioned),
  arrive/log in early.
- **Do zero practice questions and take zero mock exam this morning.** There is no diagnostic value
  left to extract, only time pressure and risk of a bad-mood-inducing miss right before the real
  thing.

---

## 4. 30 MINUTES BEFORE (highest-value glance only)

Pick from this list only — do not open anything not on it:

- **`01-exam-snapshot-and-priority-matrix.md` §6, P0 column, names only** — a 1–2 minute glance at
  the 16 P0 topic names to prime which domain each question is likely probing.
- **`03-one-line-architect-rules.md`, the classic confusion-pair rules specifically** — rules 13,
  17, 20–23 (encryption/Secrets Manager/Parameter Store), 24–27 (SG/NACL/Gateway vs Interface
  Endpoint), 36–42 (S3 storage-class/lifecycle/Object Lock), 54–61 (RDS Multi-AZ/Read Replica/
  Aurora), 82–90 (ALB/NLB/GWLB/Route 53 routing policies), 96–101 (SQS/SNS/EventBridge/Kinesis).
  These are the highest-density "two plausible answers, one right one" pairs in the whole set.
- **`03-trigger-word-dictionary.md` — phrase headings only**, as a final priming read (not the
  worked scenarios): "most cost-effective," "least operational overhead," "highly available,"
  "fault-tolerant," "decouple," "minimal code changes."
- Breathe. Do not start reading a new section, do not open the service comparison matrix (too
  long for this window), and do not check phone/forums.

---

## 5. WHAT NOT TO DO in the final 24 hours

- **Don't start any new topic outside the P0/P1 matrix.** Per `01-exam-snapshot-and-priority-matrix.md`
  §6, AppSync/GraphQL, AWS Batch, Migration Evaluator/MGN, and Amazon Data Firehose naming are
  explicitly **P3** — reading about them now trades your highest-value remaining minutes for your
  lowest-value remaining content.
- **Don't take a 6th (or any new) full mock exam cold within 24 hours.** There's no time left to
  properly review wrong answers, and a bad cold-mock score this close to the exam is far more
  likely to be noise/fatigue than signal — it will only add stress, not information.
- **Don't cram Well-Architected Framework pillar names/trivia.** The priority matrix explicitly
  rates this **P3, Low-Medium relevance, "cross-domain flavor text only."** It is not worth minutes
  this close to the exam.
- **Don't chase unverified "community-reported" exam-dump claims.** `00-research-log-and-integrity-notes.md`
  and §5 of the priority matrix explicitly flag that no community-sourced "recently seen on my
  exam" claim in this research package survived independent verification, and at least one batch of
  specific Reddit citations was flagged as likely fabricated. Don't let a forum post override the
  official-guide-based material you already built.
- **Don't re-run the full 200-question bank (`07-question-bank.md`) or all 5 mocks again from
  scratch.** You've already extracted the diagnostic value from that material; re-doing
  known-good/already-correct questions burns rest time without closing any new gap.
- **Don't try to memorize exact pricing/numeric trivia** (precise Glacier retrieval hour windows,
  exact Savings Plan discount percentages, etc.). The exam tests relative trade-off ordering
  ("cheaper than," "faster than," "more durable than"), not exact figures — time is far better
  spent re-reading the one-line rules than drilling numbers.
- **Don't pull a late night or push study past a fixed cutoff the evening before.** The skill this
  exam actually rewards — spotting the one wrong distractor among four plausible-sounding options —
  degrades with sleep debt faster than raw fact recall does.
- **Don't second-guess the internal materials against new external sources at this stage.** Given
  the confirmed service renames (SageMaker → SageMaker AI, Kinesis Data Firehose → Amazon Data
  Firehose) and the stale-PDF-vs-live-HTML-guide issue documented in
  `01-exam-snapshot-and-priority-matrix.md`, a hastily-Googled "refresher" 24–48h out is more likely
  to introduce outdated info than to add value.
- **Don't switch primary study source at the last minute** (e.g. suddenly opening Cantrill's labs
  or a new Udemy section). §7 of the priority matrix already scoped Cantrill/Digital Cloud
  Training/Whizlabs as skip/skim-only *specifically* for someone with 11+ years of cross-cloud
  experience — that verdict doesn't change under time pressure.
- **Don't over-study fundamentals already owned from GCP/Azure/Kubernetes/IaC experience** (what is
  a VPC, what is a load balancer, what is IAM conceptually). Every remaining minute belongs to
  AWS-specific service-boundary trivia — SG vs NACL statefulness, Gateway vs Interface endpoint,
  KMS key policy vs IAM policy interplay — not architecture theory you've already internalized
  elsewhere.
