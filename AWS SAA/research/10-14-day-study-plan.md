# AWS SAA-C03 — 14-Day Spaced-Repetition Study Plan

**Candidate profile:** 11+ years cloud/platform/DevOps (AWS/GCP/Azure/K8s), CKAD-certified. Gaps are AWS-specific service boundaries, not architecture fundamentals.

**Exam:** 130 min, 65 Q (50 scored / 15 unscored), scaled 100–1000, pass = 720.
**Domain weights:** D1 Secure 30% · D2 Resilient 26% · D3 High-Performing 24% · D4 Cost-Optimized 20%.

**Design principles applied:**
- **Spaced repetition on the 104 one-line rules** (`03-one-line-architect-rules.md`): introduced in 6 new chunks (Days 1–6, ~15/day) plus a final chunk on Day 7, then reviewed *cumulatively, in full,* every single day from Day 8–14 — the classic expanding-interval recall curve.
- **Front-loaded refresh, back-loaded simulation:** all 8 mastery deep-dives, all 50 architecture patterns, and all domain-specific question sets are consumed by Day 12; Days 7/9/11/13/14 are checkpoint mocks with progressively tighter pacing (130→125→120→115→130 min) to build a time buffer, then confirm true exam pace on the final dress rehearsal.
- **Domain-weight-proportional time:** Domains 1–2 (56% combined, rated P0 in the priority matrix) get 4 of the first 6 refresh days; Domains 3–4 (44%, rated P1) get 2 of the first 6 days.
- **Every named resource is used exactly once as "new," then recycled for review:** no resource is wasted, none is repeated as if unseen.

---

## Day-by-Day Plan

### Day 1 — Domain 1 Foundations: Identity & Access (IAM / STS / Organizations)
| Field | Detail |
|---|---|
| Domain refresh | `research/05d-security-iam-mastery.md` (IAM, STS, AssumeRole, Organizations/SCPs) + `research/02-service-comparison-matrix.md` (IAM vs. IAM Identity Center vs. STS rows) |
| Architecture pattern focus | `research/04-architecture-patterns.md` Patterns 1–4 (identity federation / cross-account patterns) |
| Practice questions | 20 Q — `domain1-iam-access-management-questions.md` (all) |
| Wrong-answer analysis | Tag each miss against the P0–P3 matrix in `research/01-exam-snapshot-and-priority-matrix.md`; if a P0 topic was missed, re-derive IAM policy evaluation order (explicit deny > explicit allow > implicit deny) from scratch on paper before continuing |
| Timed block | Final 10 of the 20 Qs at **2:00/question** (exam-pace baseline) |
| Memory-review touchpoint | One-line rules 1–15 (new) + Trigger-word dictionary (`03-trigger-word-dictionary.md`) Domain 1 identity terms |

### Day 2 — Domain 1: Network, Data & Detective Security
| Field | Detail |
|---|---|
| Domain refresh | `research/05a-networking-mastery.md` (SG vs. NACL) + remaining `05d-security-iam-mastery.md` (KMS, Secrets Manager vs. Parameter Store, GuardDuty/Macie/WAF/Shield) |
| Architecture pattern focus | Patterns 5–9 (data protection / network security patterns) |
| Practice questions | 20 Q — `domain1-network-identity-security-questions.md` |
| Wrong-answer analysis | Start a running "confusable pairs" log (Secrets Manager vs. Parameter Store, NACL vs. SG, KMS key policy vs. IAM policy); cross-check every miss against `02-service-comparison-matrix.md` |
| Timed block | All 20 Qs at **1:45/question** |
| Memory-review touchpoint | One-line rules 16–30 (new) + re-review 1–15; trigger words Domain 1 network/encryption section |

### Day 3 — Domain 2: High Availability, Load Balancing & Routing
| Field | Detail |
|---|---|
| Domain refresh | `research/05g-ha-dr-mastery.md` (Multi-AZ, ASG, ELB types) + `05a-networking-mastery.md` (Route 53 routing policies) |
| Architecture pattern focus | Patterns 10–15 (HA / multi-AZ patterns) |
| Practice questions | 18 Q — `domain2-ha-loadbalancing-routing-questions.md` |
| Wrong-answer analysis | For each miss, redraw the architecture from memory and mark which failure domain it tests (AZ / Region / service) |
| Timed block | All 18 Qs at **1:45/question** |
| Memory-review touchpoint | One-line rules 31–45 (new) + re-review 1–30; trigger words Domain 2 HA section |

### Day 4 — Domain 2: Decoupling, Messaging & Disaster Recovery
| Field | Detail |
|---|---|
| Domain refresh | `research/05f-serverless-messaging-mastery.md` (SQS/SNS/EventBridge/Kinesis) + `05g-ha-dr-mastery.md` continued (backup/restore, pilot light, warm standby, multi-site) |
| Architecture pattern focus | Patterns 16–21 (decoupling + DR patterns) |
| Practice questions | 17 Q — `research/07a-domain2-decoupling-questions.md` |
| Wrong-answer analysis | Classify every miss as "wrong service" vs. "wrong DR tier" vs. "misread RTO/RPO number"; log to a running mistake tracker |
| Timed block | All 17 Qs at **1:45/question** |
| Memory-review touchpoint | One-line rules 46–60 (new) + re-review 1–45; trigger words Domain 2 decoupling/DR section |

### Day 5 — Domain 3: Compute & Storage Performance
| Field | Detail |
|---|---|
| Domain refresh | `research/05e-compute-scaling-mastery.md` (EC2 families, ASG policies, Lambda concurrency) + `05b-storage-mastery.md` (S3 classes, EBS types, EFS/FSx) |
| Architecture pattern focus | Patterns 22–28 (compute/storage performance patterns) |
| Practice questions | 16 Q — `domain3-performance-questions.md` |
| Wrong-answer analysis | Split misses into "numeric recall gap" (IOPS/throughput/latency) vs. "conceptual service-choice gap"; numeric gaps go straight onto a flashcard |
| Timed block | All 16 Qs at **1:45/question** |
| Memory-review touchpoint | One-line rules 61–75 (new) + re-review 1–60; trigger words Domain 3 compute/storage section |

### Day 6 — Domain 3 Database/Global Performance + Domain 4 Cost
| Field | Detail |
|---|---|
| Domain refresh | `research/05c-database-mastery.md` (RDS/Aurora/DynamoDB, read replicas, caching) + `05h-global-cost-performance-mastery.md` (CloudFront, Global Accelerator, Savings Plans vs. RI vs. Spot) |
| Architecture pattern focus | Patterns 29–35 (caching/database + cost patterns) — closes out all 8 mastery deep-dives |
| Practice questions | 20 Q — `domain4-storage-database-networking-cost-questions.md` |
| Wrong-answer analysis | Flag every cost-related miss separately (pricing-model confusion = "easy points to lose"); re-derive the comparison from `02-service-comparison-matrix.md` |
| Timed block | All 20 Qs at **1:45/question** |
| Memory-review touchpoint | One-line rules 76–90 (new) + re-review 1–75; trigger words Domain 4 cost section |

### Day 7 — ✅ CHECKPOINT: MOCK EXAM 1 (Full Simulation)
| Field | Detail |
|---|---|
| Domain refresh | None new — 5-minute skim of the P0 list in `01-exam-snapshot-and-priority-matrix.md` only |
| Architecture pattern focus | Flashcard recall pass over Pattern **titles only** for 1–35 (no reading, pure recall test) |
| Practice questions | **65 Q — `research/09-mock-exam-1.md`**, done cold, no notes |
| Wrong-answer analysis | Score per domain and compare against the 30/26/24/20 weighting to find the domain most under-performing *relative to its weight*; build a ranked "Day 7 gap list" (miss count × domain weight) |
| Timed block | Full 65 Qs in **130 minutes (2:00/question, exact exam pace)** |
| Memory-review touchpoint | One-line rules 91–104 (final new chunk) + full cumulative flash pass over 1–104 in the evening |

### Day 8 — Remediation Day 1 (Domain 1 bias, per Day 7 gap list)
| Field | Detail |
|---|---|
| Domain refresh | Re-read only the mastery doc(s) tied to your top 2 gap-list items (from `05a`–`05h`) |
| Architecture pattern focus | Patterns 36–42, deliberately re-checked against Mock 1 misses |
| Practice questions | 20 Q — `domain1-secure-architectures-practice.md` |
| Wrong-answer analysis | For every Mock 1 miss, find and re-solve the matching question type here; if still wrong, escalate same evening to the Domain 1 section of `research/07-question-bank.md` |
| Timed block | All 20 Qs at **1:30/question** (pace tightening begins) |
| Memory-review touchpoint | Diagrams 1–5 — `research/04-diagram-critique-exercises.md`, untimed talk-aloud critique — plus full one-line rules 1–104 flash pass |

### Day 9 — ✅ CHECKPOINT: MOCK EXAM 2 (Pace Check)
| Field | Detail |
|---|---|
| Domain refresh | Full pass of `03-trigger-word-dictionary.md` (10 min, all domains) — pure reinforcement, no new material |
| Architecture pattern focus | Flashcard recall, Patterns 1–42, one-line trigger only |
| Practice questions | **65 Q — `research/09-mock-exam-2.md`** |
| Wrong-answer analysis | Repeat the Day 7 domain-vs-weight gap analysis; diff directly against the Day 7 gap list — persistent misses become the top priority for remaining days |
| Timed block | Full 65 Qs in **125 minutes (1:55/question)** — slightly faster than exam pace |
| Memory-review touchpoint | Full cumulative one-line rules 1–104 flash pass (evening) |

### Day 10 — Distractor & Trap Training (Domain 4 + Domain 2 remediation)
| Field | Detail |
|---|---|
| Domain refresh | `research/06a-distractor-patterns.md`, full read — the "cheat sheet" for how AWS constructs wrong answers |
| Architecture pattern focus | Patterns 43–50 — completes all 50 patterns |
| Practice questions | **50 Q — `research/06b-two-answer-dilemmas.md`** (all 50 two-answer dilemmas) |
| Wrong-answer analysis | For every dilemma missed, write the exact discriminating detail in the stem that should have ruled out the wrong pick — trains stem-reading, not service recall |
| Timed block | All 50 dilemmas at **2:15/question** (deliberately slower — these are harder than average) |
| Memory-review touchpoint | `research/06c-exam-traps.md` — all 50 traps read end-to-end, untimed, as a pattern-recognition cheat sheet |

### Day 11 — ✅ CHECKPOINT: MOCK EXAM 3 (Speed Build)
| Field | Detail |
|---|---|
| Domain refresh | Full pass of `02-service-comparison-matrix.md` (10 min) — final full re-read before pure drilling begins |
| Architecture pattern focus | Flashcard recall, all 50 pattern titles, target under 8 minutes |
| Practice questions | **65 Q — `research/09-mock-exam-3.md`** |
| Wrong-answer analysis | Domain-vs-weight gap analysis again; also tag each miss "knowledge gap" vs. "fell for a trap" (cross-ref Day 10's trap list) to check if distractor training is working |
| Timed block | Full 65 Qs in **120 minutes (1:50/question)** |
| Memory-review touchpoint | One-line rules 1–104 cumulative flash pass + trigger-word spot-check on any domain scoring below 70% |

### Day 12 — Speed & Synthesis Day (Rapid-Fire + Diagrams)
| Field | Detail |
|---|---|
| Domain refresh | 5-minute skim each of `05a`, `05e`, `05h` — only sections tied to lingering gap-list items |
| Architecture pattern focus | Diagrams 6–20 — `research/04-diagram-critique-exercises.md` (remaining 15), each a 90-second "spot the anti-pattern" drill |
| Practice questions | **100 Q — `research/08-rapid-fire-questions.md`** (all 5 sections: Security & IAM, Networking, Storage & Database, Compute & Serverless, Messaging/Migration/Cost) |
| Wrong-answer analysis | Rapid-fire misses are pure recall failures — anything missed goes straight onto a "must-memorize before Day 14" index-card list |
| Timed block | 100 Qs at **0:45/question** (forces instinctive recall, not analysis) |
| Memory-review touchpoint | One-line rules 1–104 cumulative flash pass (should now be near-automatic) |

### Day 13 — ✅ CHECKPOINT: MOCK EXAM 4 (Exam-Day Dress Rehearsal)
| Field | Detail |
|---|---|
| Domain refresh | None — 5-minute review of the Day 12 "must-memorize" index cards only |
| Architecture pattern focus | None new — pure simulation day |
| Practice questions | **65 Q — `research/09-mock-exam-4.md`**, taken at the same time of day as the scheduled real exam, same environment rules (no notes, one screen, visible timer) |
| Wrong-answer analysis | Final domain-vs-weight gap check; any domain still below its proportional pass threshold becomes the *only* thing reviewed on Day 14 morning |
| Timed block | Full 65 Qs in **115 minutes (1:46/question)** — maximum buffer-building pace |
| Memory-review touchpoint | One-line rules cumulative pass, but spoken/written aloud instead of read silently (active recall — strongest spacing effect before the real exam) |

### Day 14 — ✅ CHECKPOINT: MOCK EXAM 5 (Final Simulation) + Exam-Ready Consolidation
| Field | Detail |
|---|---|
| Domain refresh | 5-minute final skim of the P0 list in `01-exam-snapshot-and-priority-matrix.md` (morning only) |
| Architecture pattern focus | Flashcard recall of all 50 pattern titles, target under 6 minutes, zero misses |
| Practice questions | **65 Q — `research/09-mock-exam-5.md`**, run as the literal dress rehearsal at the real exam start time if known |
| Wrong-answer analysis | Light-touch only — confirm the score is comfortably above the 720-equivalent threshold and above the weakest domain's proportional share; do **not** deep-dive new content this late, just confirm no P0 topic was missed |
| Timed block | Full 65 Qs in **130 minutes (2:00/question, real exam pace)**, full dress-rehearsal conditions |
| Memory-review touchpoint | Final cumulative pass over one-line rules 1–104 + trigger-word dictionary — only if a genuine gap surfaced; otherwise rest before the real exam |

---

## Resource Coverage Checklist (every named asset, mapped to its day)

| Resource | Day(s) used |
|---|---|
| `01-exam-snapshot-and-priority-matrix.md` (P0–P3) | 1 (tag misses), 7, 14 |
| `02-service-comparison-matrix.md` | 1, 2, 6, 11 |
| `03-trigger-word-dictionary.md` | Daily (domain section Days 1–6; full pass Days 9, 11, 14) |
| `03-one-line-architect-rules.md` (104 rules) | New chunks Days 1–7; full cumulative review Days 8–14 |
| `04-architecture-patterns.md` (50 patterns) | New: Days 1(1-4),2(5-9),3(10-15),4(16-21),5(22-28),6(29-35),8(36-42),10(43-50); flashcard recall Days 7,9,11,14 |
| `04-diagram-critique-exercises.md` (20 exercises) | 1–5 on Day 8; 6–20 on Day 12 |
| `05a`–`05h` mastery deep-dives (8 docs) | 1(05d), 2(05a+05d), 3(05g+05a), 4(05f+05g), 5(05e+05b), 6(05c+05h); spot-review 12 |
| `06a-distractor-patterns.md` | 10 |
| `06b-two-answer-dilemmas.md` (50) | 10 |
| `06c-exam-traps.md` (50) | 10 |
| `07-question-bank.md` (200) | 8 (escalation source) |
| `07a-domain2-decoupling-questions.md` (17) | 4 |
| `08-rapid-fire-questions.md` (100) | 12 |
| `09-mock-exam-1.md` … `09-mock-exam-5.md` | 7, 9, 11, 13, 14 |
| `domain1-iam-access-management-questions.md` (20) | 1 |
| `domain1-network-identity-security-questions.md` (20) | 2 |
| `domain1-secure-architectures-practice.md` (20) | 8 |
| `domain2-ha-loadbalancing-routing-questions.md` (18) | 3 |
| `domain2-resilient-architectures-questions.md` (17) | remediation reserve (use if Domain 2 is on the Day 9/11 gap list) |
| `domain3-performance-questions.md` (16) | 5 |
| `domain4-cost-optimization-questions.md` (20) | remediation reserve (use if Domain 4 is on the Day 9/11 gap list) |
| `domain4-storage-database-networking-cost-questions.md` (20) | 6 |

**Two files are held in reserve** (`domain2-resilient-architectures-questions.md`, `domain4-cost-optimization-questions.md`) specifically to slot into whichever remediation day (8 or 10) your Mock 1/2 gap analysis flags as weakest — this keeps the plan adaptive without adding new days.
