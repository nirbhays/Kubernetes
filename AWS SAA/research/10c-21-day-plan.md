# AWS SAA-C03 — 21-Day Study Plan

> **File-reference correction:** this plan was drafted referencing per-domain question files (e.g. `domain1-iam-access-management-questions.md`, `domain2-resilient-architectures-questions.md`) that do not exist as separate files. All 200 practice questions live in a single consolidated file, **`07-question-bank.md`**, organized by domain in this order:
> - Domain 1 (Design Secure Architectures): Questions 1-60
> - Domain 2 (Design Resilient Architectures): Questions 61-112
> - Domain 3 (Design High-Performing Architectures): Questions 113-160
> - Domain 4 (Design Cost-Optimized Architectures): Questions 161-200
>
> Wherever this plan names a per-domain question file, use the matching question-number range in `07-question-bank.md` instead. Rapid-fire questions are genuinely split by section within the single file `08-rapid-fire-questions.md` (Security & IAM 1-20, Networking 21-40, Storage & Database 41-60, Compute & Serverless 61-80, Messaging/Migration/Cost 81-100).

*Spaced repetition + progressive difficulty (L1 recognition → L5 distractor-heavy), built on your existing materials in `AWS SAA/research/`*

## Week 1 — Foundation, Domain 1 (Security, 30%) & Domain 2 Start (Resilience, 26%)

**Day 1** — Orientation & exam map. Read `01-exam-snapshot-and-priority-matrix.md` fully + skim `02-service-comparison-matrix.md`. Establishes P0/P1 service priorities so the next 20 days are targeted, not generic (L1).

**Day 2** — Service recognition drill. Read `03-trigger-word-dictionary.md`, then self-quiz all 104 rules in `03-one-line-architect-rules.md` (cover-the-answer method). Anchors keyword→service mapping from Day 1's map (L1).

**Day 3** — Domain 1a: IAM & access management. Read `05d-security-iam-mastery.md` (IAM half) + complete all of `domain1-iam-access-management-questions.md`. First deep dive, starts with the highest-weighted domain (L2).

**Day 4** — Domain 1b: network/data security. Finish `05d-security-iam-mastery.md` + complete `domain1-network-identity-security-questions.md` and all of `domain1-secure-architectures-practice.md`. Extends Day 3's IAM base into KMS/VPC security (L2).

**Day 5 — MOCK EXAM 1 (baseline, easiest set).** Full timed run of `09-mock-exam-1.md` (130 min, 65Q). Log every miss into a mistake tracker by domain — this is your Week-1 checkpoint on Domain 1.

**Day 6** — Domain 2a: HA & load balancing. Read `05g-ha-dr-mastery.md` + `domain2-ha-loadbalancing-routing-questions.md`. Directly remediates any Mock 1 resilience gaps (L2/L3).

**Day 7** — Domain 2b: DR strategy & decoupling. Read `05f-serverless-messaging-mastery.md` + complete `domain2-resilient-architectures-questions.md` and `07a-domain2-decoupling-questions.md`. Builds on Day 6's HA foundation with async/loose-coupling patterns (L3).

## Week 2 — Architecture Synthesis & Domain 3 (Performance, 24%)

**Day 8** — Whole-architecture patterns, part 1. Work `04-architecture-patterns.md` items 1–25 + 10 of the `04-diagram-critique-exercises.md`. Forces synthesis of Domains 1+2 into full designs instead of single-service recall (L3).

**Day 9** — Whole-architecture patterns, part 2. Finish patterns 26–50 + remaining 10 diagram exercises; skim `05e-compute-scaling-mastery.md` and `05b-storage-mastery.md`. Rounds out pattern fluency across compute/storage before Mock 2 (L3).

**Day 10 — MOCK EXAM 2 (moderate).** Full timed run of `09-mock-exam-2.md`. Deep review; re-tag weak domains in your tracker for spaced repetition later.

**Day 11** — Domain 3a: compute/storage performance. Deep read `05b-storage-mastery.md` and `05e-compute-scaling-mastery.md` (both skimmed Day 9) + first half of `domain3-performance-questions.md`. Targets whatever Mock 2 flagged, opens Domain 3 (L3).

**Day 12** — Domain 3b: database & caching performance. Read `05c-database-mastery.md` + finish `domain3-performance-questions.md` + `07-domain3-performance-questions.md`. Extends Day 11's compute/storage lens into the DB tier (L4).

**Day 13** — Domain 3 wrap + global networking. Read `05a-networking-mastery.md` + performance half of `05h-global-cost-performance-mastery.md`, plus 25 Domain-3-tagged questions from `07-question-bank.md`. First scenario-heavy (L4) day.

**Day 14 — MOCK EXAM 3 (harder, distractor-heavy).** Full timed run of `09-mock-exam-3.md`. Review, then interleave-review your missed Day 3–4 (security) and Day 6–7 (resilience) questions to force spaced repetition of older material.

## Week 3 — Domain 4 (Cost, 20%), Distractor Mastery & Final Gate

**Day 15** — Domain 4a: cost optimization core. Read cost half of `05h-global-cost-performance-mastery.md` + complete `domain4-cost-optimization-questions.md`. Last domain introduced deliberately last — typically fastest for your background (L3).

**Day 16** — Domain 4b: storage/DB/network cost tradeoffs. Complete `domain4-storage-database-networking-cost-questions.md` + 25 Domain-4 items from `07-question-bank.md`. Builds cross-domain cost-vs-performance/security tradeoff reasoning on Day 15 (L4).

**Day 17** — Distractor training begins. Read `06a-distractor-patterns.md` fully + work through 25 of the 50 `06b-two-answer-dilemmas.md` plus `dilemmas-batch1.md`. Trains elimination technique for the exam's hardest question type (L5).

**Day 18 — MOCK EXAM 4 (near-exam difficulty, heavy distractors).** Full timed run of `09-mock-exam-4.md`. Same-day deep review, then finish the remaining 25 two-answer dilemmas held over from Day 17 (L5).

**Day 19** — Exam traps + speed drilling. Read all 50 in `06c-exam-traps.md`, then run all 100 `08-rapid-fire-questions.md` under a strict 60-minute clock. Sharpens the ~2-min/question pacing (130 min ÷ 65 questions) and trap recognition right before the final mocks (L5).

**Day 20** — Full-spectrum spaced repetition. Rapid re-pass of the 104 one-line rules + trigger word dictionary, then pull 50 targeted questions from `07-question-bank.md` focused on your single weakest domain across Mocks 1–4. Consolidates all prior days into weak-point remediation (L5).

**Day 21 — MOCK EXAM 5 (final gate, hardest/highest distractor density).** Full timed run of `09-mock-exam-5.md` under strict exam conditions (130 min, 65Q, no notes, no pausing). Light review only — no new material. AWS's official score is a scaled 100–1000 (pass at 720) that is *not* a straight percentage of correct answers, and the exact conversion isn't published — so don't chase "720" on a mock. Treat a consistent 80%+ raw score here, with no domain badly lagging, as your readiness signal instead of a bare pass.

---

## RECOMMENDED PLAN FOR THIS CANDIDATE

**14 days is the most reasonable timeline**, not 7 or 21. Your 11+ years of multi-cloud architecture and CKAD hold means concepts like HA, decoupling, IaC, autoscaling, and defense-in-depth need no re-teaching — you can compress the Level 1–2 material into roughly half the time shown. However, 7 days is too aggressive given the sheer volume of AWS-specific trivia that transferable cloud experience does *not* cover — exact service limits, naming/API quirks, and the 100 exam-traps-and-two-answer-dilemmas (50 apiece in `06c-exam-traps.md` and `06b-two-answer-dilemmas.md`) that are purpose-built to catch experienced multi-cloud engineers who pattern-match to GCP/Azure equivalents. 21 days is unnecessarily long and risks diminishing returns/over-studying fundamentals you already know cold, diluting focus during the highest-value final stretch (Domains 3–4 and distractor training).

**14-day compression map** (collapses only the low-yield "re-teach fundamentals" days; keeps every mock and every new-content day intact):

- New Day 1 = old Days 1–2 combined (exam map, trigger words, and the 104 one-line rules in a single sitting — keyword recognition doesn't need a full day at your level)
- New Day 2 = old Day 3 (IAM deep dive, unchanged)
- New Day 3 = old Day 4 (network/data security, unchanged)
- New Day 4 = old Day 5 (Mock 1 — unchanged, do not skip)
- New Day 5 = old Days 6–7 combined (HA/DR/decoupling — recognition exercise, not new learning, for your background)
- New Day 6 = old Days 8–9 combined (architecture-pattern synthesis — skim/pattern-match fast, don't drill from scratch)
- New Day 7 = old Day 10 (Mock 2, unchanged)
- New Days 8–14 = old Days 11–21 unchanged (Domain 3, Domain 4, distractor training, and Mocks 3–5 stay at full length — this is the AWS-specific trivia and hardest-question-type training your multi-cloud background doesn't already cover)

This gives you enough spaced repetition on AWS-specific gotchas without wasting time relearning cloud architecture principles you already teach others.
