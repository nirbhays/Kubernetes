# AWS SAA-C03 Study System — Index

Built for an 11+ year cloud/platform engineer preparing for the current AWS Certified Solutions
Architect - Associate exam (SAA-C03: 130 min, 65 questions, 4 domains at 30/26/24/20%, pass at
720/1000). Start with `00` and `01` if you haven't already; otherwise jump to whatever stage you need.

| File | Contents |
|---|---|
| `00-research-log-and-integrity-notes.md` | What was verified vs. unverifiable, and the community-research integrity finding (read this once) |
| `01-exam-snapshot-and-priority-matrix.md` | Verified exam facts, domain weights, P0-P3 topic priority matrix, study resource recommendation |
| `02-service-comparison-matrix.md` | Compute/storage/database/networking/messaging/migration service comparisons |
| `02-audit-log.md` | Technical errors caught during Stage 2's validation pass |
| `03-trigger-word-dictionary.md` | 25 exam trigger phrases -> what they signal, distractors, practice question |
| `03-one-line-architect-rules.md` | 104 quick-recall "if X, think Y" rules with caveats |
| `04-architecture-patterns.md` | 50 numbered architecture patterns with ASCII diagrams |
| `04-diagram-critique-exercises.md` | 20 "spot the weakness, fix it" diagram exercises |
| `05a`-`05h` (8 files) | Domain mastery deep-dives: Networking, Storage, Database, Security & IAM, Compute & Scaling, Serverless & Messaging, HA & DR, Global/Cost/Performance |
| `06a-distractor-patterns.md` | How AWS constructs plausible-but-wrong answers, by pattern type |
| `06b-two-answer-dilemmas.md` | 50 "two answers look right, here's the tiebreaker" questions |
| `06c-exam-traps.md` | 50 named traps with the correct mental model for each |
| `07-question-bank.md` | 200 original questions, domain-weighted (Q1-60 Domain 1, Q61-112 Domain 2, Q113-160 Domain 3, Q161-200 Domain 4) |
| `08-rapid-fire-questions.md` | 100 instant service-recognition drills, by topic section |
| `09-mock-exam-1.md` .. `09-mock-exam-5.md` | 5 full 65-question mock exams, increasing difficulty (1=baseline, 5=final gate), inline answers/explanations |
| `10a-7-day-plan.md`, `10b-14-day-plan.md`, `10c-21-day-plan.md` | Study plans; `10c` also has the recommendation for which duration fits this candidate |
| `10d-exam-time-strategy.md` | Per-question time budget, flag/skip rules |
| `10e-question-reading-strategy.md` | How to read dense scenarios fast |
| `10f-final-48-hours.md` | 48h/24h/exam-morning/30-min-before plan, plus what NOT to do |
| `10g-readiness-scorecard.md` | GO/AMBER/NO-GO objective readiness criteria |
| `11a-master-cheat-sheet.md` | Compact "choose X when..." reference across all domains |
| `11b-choose-x-not-y.md` | 48 paired service-distinction cheat cards |

## Known limitations (see `00-research-log-and-integrity-notes.md` for full detail)

- **Live community/Reddit research was not achievable** in this environment (org policy blocks
  `WebSearch`; Reddit and search engines block direct/proxied fetches even with raw internet
  access confirmed working). One sub-agent fabricated fake Reddit citations during Stage 1 —
  caught and discarded. All "community frequency" labels in `01-exam-snapshot-and-priority-matrix.md`
  are marked "Unverified" accordingly; priority is driven by official exam-guide weight and
  technical confusion-risk, not real candidate-report frequency.
- A handful of specific claims in the domain-mastery files (Aurora Serverless v2 scale-to-zero,
  RDS Multi-AZ DB Cluster engine support, Aurora Multi-Master retirement) rely on trained
  knowledge rather than a fresh doc check, for the same reason — worth a quick manual spot-check.
- Every question bank / mock exam / dilemma / trap batch was independently audited for
  single-best-answer integrity before being filed; audit logs are kept where substantial (see
  `02-audit-log.md`).
