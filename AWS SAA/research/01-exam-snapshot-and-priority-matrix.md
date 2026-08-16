# AWS SAA (SAA-C03) — Stage 1 Research: Exam Snapshot, Priority Matrix, Study Resources

> Status: Officially-verified facts in this document are HIGH confidence (cross-checked by two
> independent validation passes against docs.aws.amazon.com / aws.amazon.com). Anything labeled
> "community-reported" or "unverified" should NOT be treated as sourced fact — see
> `00-research-log-and-integrity-notes.md` for why.

## 1. Executive Summary

SAA-C03 remains the live, current exam as of August 2026 — no successor code (e.g., SAA-C04)
exists, and this was independently confirmed twice against the official docs.aws.amazon.com exam
guide. The structural facts are rock-solid and cross-verified: 130 minutes, 65 questions (50
scored / 15 unscored pretest, unanswered = incorrect), multiple-choice and multiple-response only
(no case studies, no drag-and-drop), scaled score 100–1,000 with a 720 pass bar under a
compensatory (not per-section) model, four domains weighted 30/26/24/20%, $150 USD, Pearson VUE
(test center or online proctored), 3-year validity, 14-day retake wait with no attempt cap but
full fee each time, and a 2-year prohibition on retaking the same passed version.

For someone with 11+ years of cross-cloud architecture experience, this exam is not conceptually
hard — it is a vocabulary and trade-off-recall exam: AWS-specific service boundaries (S3 storage
classes, VPC Endpoints vs. NAT, Transit Gateway vs. Peering, SG vs. NACL statefulness, ALB/NLB/GWLB
selection, KMS/IAM edge cases) rather than architecture theory already known from GCP/Azure/K8s
experience.

The genuinely weak point of this research pass is community-sourced "what's actually on the exam"
intelligence — see the integrity notes file. Practically: budget ~30–35 hours, lean entirely on
official-guide-driven study plus one strong third-party question bank, and do not trust any
"recently leaked question" claim encountered online without checking it against the official
in-scope services list.

## 2. Current Exam Snapshot

### Officially Verified
(docs.aws.amazon.com / aws.amazon.com — confirmed by two independent validation passes)

| Attribute | Value |
|---|---|
| Certification | AWS Certified Solutions Architect – Associate |
| Exam code | SAA-C03 (current; no newer code found anywhere on official pages as of 2026-08-15) |
| Duration | 130 minutes |
| Questions | 65 total — 50 scored, 15 unscored/unidentified pretest |
| Scoring on unanswered | Counted as incorrect; no penalty beyond that for guessing |
| Question formats | Multiple choice (1 correct + 3 distractors); multiple response (2+ correct of 5+ options) — no other formats exist |
| Scoring model | Scaled 100–1,000; passing = 720; compensatory (overall pass/fail only, section breakdown is diagnostic-only) |
| Domain weights | 30% / 26% / 24% / 20% (see Section 3) |
| Cost | $150 USD (Associate tier) |
| Delivery | Pearson VUE test center or Pearson VUE online proctored |
| Validity | 3 years from pass date |
| Retake policy | 14-calendar-day wait after a fail, unlimited attempts (full fee each time); 2-year block on retaking the same version after a pass |
| Recertification | Pass current SAA version again, or earn SA-Professional (auto-renews Associate) |

**Explicitly unverifiable, flagged rather than guessed:** AWS publishes the current exam guide as
an HTML docs page with no visible version number or "last updated" date. A legacy PDF mirror shows
a September 25, 2023 file-metadata timestamp, but its in-scope-services list is stale relative to
the live HTML page (missing recent renames), so that date should **not** be treated as the guide's
effective date. No official AWS changelog/diff between SAA-C03 revisions exists.

### Community-Reported
(low/unverifiable confidence — read `00-research-log-and-integrity-notes.md` before using any of this)

Every research sub-agent that attempted live web/Reddit research hit a hard environment block. Two
of three community sub-agents honestly reported zero retrievable data. The third (networking/storage)
returned ~10 specific, dated Reddit threads with titles, URLs, and quote snippets that an
independent validation pass could not fetch or corroborate at all — treat those specific citations
as fabricated. The general topics named (VPC internals, S3, hybrid connectivity, CloudFront) are
directionally plausible only because they align with the real official domain weightings, not
because of any verified frequency evidence.

## 3. Current Exam Domains and Weightings

| Domain | Official Weight | My Priority (P0–P3) | Expected Difficulty |
|---|---|---|---|
| Domain 1: Design Secure Architectures | 30% | **P0** | High — IAM policy evaluation logic, cross-account/federation, KMS key policies vs. IAM policies, and security-service selection (GuardDuty/Macie/WAF/Shield) are the densest trade-off space and the single heaviest-weighted domain. |
| Domain 2: Design Resilient Architectures | 26% | **P0** | Medium-High — decoupling (SQS/SNS/EventBridge), Multi-AZ/Multi-Region patterns, and failover design are conceptually familiar from multi-cloud background but tested with AWS-specific service boundaries. |
| Domain 3: Design High-Performing Architectures | 24% | **P1** | Medium — compute/storage/DB/network performance selection (caching, read replicas, CloudFront, placement groups); mostly a "know the right service for the job" exercise. |
| Domain 4: Design Cost-Optimized Architectures | 20% | **P1** | Medium — Savings Plans vs. RIs vs. Spot, S3 lifecycle/storage-class economics, right-sizing; lower conceptual difficulty but easy to lose points on numeric/pricing-model recall. |

Note: weight ≠ priority alone — Domains 1 and 2 combine to 56% of scored content and carry the
highest density of "gotcha" service-boundary questions, which is why both are P0 despite Domain 2
having a lower difficulty ceiling than Domain 1.

## 4. What Changed Recently

- **No official changelog exists.** AWS does not publish a version-diff/changelog for the SAA-C03
  exam guide, so "recently added/removed" claims below are inferential (comparing the live HTML
  in-scope-services page against a stale cached PDF), not AWS-confirmed.
- **Service renames reflected in the current in-scope list (not new content, just naming):**
  "Amazon SageMaker AI" (rebrand of SageMaker), "Amazon Data Firehose" (renamed from "Amazon
  Kinesis Data Firehose"), and an Amazon QuickSight-family entry. Older study material referencing
  "Kinesis Data Firehose" or plain "SageMaker" should be mentally mapped to the current name — the
  underlying exam content/scope has not materially shifted, just AWS's product naming.
- **Confirmed still out-of-scope** (do not study these in depth): Amazon Lightsail, Amazon Managed
  Blockchain, Amazon GameLift, Amazon Braket, AWS Ground Station, developer CI/CD tooling
  (CodeBuild/CodeCommit/CodeDeploy/CDK/CloudShell), ML-framework-specific services (SageMaker
  Canvas, SageMaker Ground Truth, DeepComposer, framework-specific SageMaker variants, Inferentia),
  and all IoT services.
- **Outdated advice to actively ignore:** (1) Any prep material still organized around
  SAA-C01/SAA-C02 domain structures or weightings — the current 4-domain, 30/26/24/20 structure is
  what's live. (2) Any specific "these exact questions were on my exam" claims circulating online.
  (3) The September 2023 PDF's service list — it is stale versus the live HTML docs page.

## 5. Recent Candidate Intelligence

**Caveat, stated plainly:** No sub-agent in this research pipeline achieved verified live access to
Reddit, forums, or search engines (see integrity notes). What follows is graded accordingly.

**Strong Signal:** None. No community claim in this research package survived independent source
verification. (The only "strong signal" data point overall is the official exam guide's own
domain-weighting text, which is blueprint fact, not candidate intelligence — see Section 3.)

**Moderate Signal** (plausible but sourcing unverified — topic exists in official scope, frequency
claim unconfirmed):
- VPC core mechanics (SG vs. NACL statefulness, subnet design, route tables)
- S3 storage-class, lifecycle, and Object Lock (governance vs. compliance mode) nuances
- Hybrid connectivity trade-off framing (Direct Connect vs. Site-to-Site VPN — cost/latency/
  reliability angle, not deep BGP/VIF config)
- CloudFront origin selection (ALB/NLB) and CloudFront-vs-Global-Accelerator confusion

**Weak Signal** (explicitly flagged as likely fabricated — do not act on these as if verified):
- Any specific dated Reddit thread, comment-ID URL, quote snippet, or numeric "mention count"
  attributed to r/AWSCertifications in this research package.
- Transit Gateway vs. VPC Peering "1–2 questions" framing, and EBS/EFS/FSx-for-ECS scenario
  specifics tied to those same fabricated citations.

**Recommendation:** Study the Moderate-Signal topics because they are officially in-scope, not
because of the unverifiable frequency claims attached to them.

## 6. P0/P1/P2/P3 Topic Priority Matrix

Community Frequency below is marked "Unverified" throughout (see Section 5) — it reflects only
whether a topic appeared in the unconfirmed community dataset, not confirmed real-world frequency.

| Topic/Service | Official Relevance | Community Frequency | Difficulty | Confusion Risk | Exam Priority |
|---|---|---|---|---|---|
| IAM (users/groups/roles/policies, evaluation logic) | High (Domain 1) | Unverified-High | High | High (explicit/implicit deny, policy evaluation order) | **P0** |
| STS / cross-account access / AssumeRole | High (Domain 1) | Unverified-Mod | High | High | **P0** |
| IAM Identity Center / SCPs / Organizations | High (Domain 1) | Unverified-Low | Medium | Medium | **P0** |
| KMS (key policies, envelope encryption, key rotation) | High (Domain 1) | Unverified-Mod | High | High (KMS key policy vs IAM policy interplay) | **P0** |
| Secrets Manager vs. Systems Manager Parameter Store | High (Domain 1) | Unverified-Low | Medium | High (near-identical use cases) | **P0** |
| VPC Security Groups vs. NACLs | High (Domain 1/2) | Unverified-High | Medium | High (stateful vs stateless) | **P0** |
| VPC design (subnets, route tables, IGW) | High (Domain 2/3) | Unverified-High | Medium | Medium | **P0** |
| NAT Gateway vs. VPC Endpoints (Gateway/Interface) | High (Domain 2/3) | Unverified-High | Medium | High | **P0** |
| S3 storage classes & lifecycle policies | High (Domain 3/4) | Unverified-High | Medium | Medium | **P0** |
| S3 Object Lock (governance vs. compliance mode) | High (Domain 1) | Unverified-Mod | Medium | High | **P0** |
| S3 encryption options (SSE-S3/SSE-KMS/SSE-C, bucket policies) | High (Domain 1) | Unverified-Mod | Medium | High | **P0** |
| RDS Multi-AZ vs. Read Replicas | High (Domain 2/3) | Unverified-Mod | Medium | Medium | **P0** |
| Aurora / Aurora Serverless v2 | High (Domain 3/4) | Unverified-Mod | Medium | Medium | **P0** |
| DynamoDB (capacity modes, GSI/LSI, DAX) | High (Domain 3/4) | Unverified-Mod | Medium | Medium | **P0** |
| SQS vs. SNS vs. EventBridge (decoupling patterns) | High (Domain 2) | Unverified-Mod | Medium | High (overlapping use cases) | **P0** |
| ALB vs. NLB vs. Gateway Load Balancer | High (Domain 2/3) | Unverified-Mod | Medium | High | **P0** |
| Auto Scaling Groups (policies, health checks, warm pools) | High (Domain 2) | Unverified-Mod | Low-Medium | Low | **P1** |
| Lambda (concurrency, VPC config, event sources) | High (Domain 2/3) | Unverified-Mod | Medium | Medium | **P1** |
| ECS vs. EKS vs. Fargate | High (Domain 2/3) | Unverified-Low | Medium | Medium | **P1** |
| Step Functions | Medium (Domain 2) | Unverified-Low | Low-Medium | Low | **P1** |
| API Gateway (REST vs HTTP API, throttling, auth) | High (Domain 2/3) | Unverified-Low | Medium | Medium | **P1** |
| Cognito (User Pools vs. Identity Pools) | High (Domain 1) | Unverified-Low | Medium | High | **P1** |
| CloudFront (origins, OAC/OAI, caching behaviors) | High (Domain 3) | Unverified-Mod | Medium | Medium | **P1** |
| CloudFront vs. Global Accelerator | High (Domain 3) | Unverified-Mod | Medium | High | **P1** |
| Route 53 (routing policies: failover/latency/weighted/geo) | High (Domain 2/3) | Unverified-Mod | Medium | Medium | **P1** |
| Direct Connect vs. Site-to-Site VPN | High (Domain 2) | Unverified-Mod | Medium | Medium | **P1** |
| Transit Gateway vs. VPC Peering | High (Domain 2) | Unverified-Mod | Medium | Medium | **P1** |
| ElastiCache (Redis vs. Memcached, caching patterns) | Medium (Domain 3) | Unverified-Low | Low-Medium | Low | **P1** |
| EBS (volume types, multi-attach, snapshots) | Medium (Domain 3) | Unverified-Mod | Low | Low | **P1** |
| EFS vs. EBS vs. Instance Store | Medium (Domain 3) | Unverified-Mod | Medium | Medium | **P1** |
| WAF vs. Shield (Standard/Advanced) | High (Domain 1) | Unverified-Low | Medium | Medium | **P1** |
| GuardDuty / Macie / Security Hub / Inspector | High (Domain 1) | Unverified-Low | Medium | Medium (know which detects what) | **P1** |
| ACM (certificate provisioning/validation) | Medium (Domain 1) | Unverified-Low | Low | Low | **P1** |
| Savings Plans vs. Reserved Instances vs. Spot | High (Domain 4) | Unverified-Low | Medium | High (numeric trade-offs) | **P1** |
| EC2 instance families/purchasing options | Medium (Domain 3/4) | Unverified-Low | Low | Low | **P1** |
| CloudFormation (drift, stack sets, nested stacks) | Medium (Domain 2) | Unverified-Low | Low-Medium | Low | **P2** |
| CloudWatch (alarms, metrics, Logs Insights) | Medium (Domain all) | Unverified-Low | Low | Low | **P2** |
| CloudTrail vs. Config | Medium (Domain 1) | Unverified-Low | Medium | Medium | **P2** |
| Redshift (basic use case recognition) | Medium (Domain 3) | Unverified-Low | Low | Low | **P2** |
| DMS (Database Migration Service) | Medium (Domain migration) | Unverified-Low | Low | Low | **P2** |
| Snow Family (Snowball/Snowcone/Snowmobile) | Medium (Domain 2/4) | Unverified-Low | Low | Low (mostly volume/timeline recall) | **P2** |
| DataSync | Low-Medium (Domain 2) | Unverified-Low | Low | Low | **P2** |
| FSx for Lustre / FSx for ONTAP | Low-Medium (Domain 3) | Unverified-Low | Low-Medium | Medium (niche, easy to mix up) | **P2** |
| Storage Gateway (types: File/Volume/Tape) | Low-Medium (Domain 3) | Unverified-Low | Low-Medium | Medium | **P2** |
| Elastic Beanstalk | Low-Medium (Domain 2) | Unverified-Low | Low | Low | **P2** |
| AppSync / GraphQL | Low (Domain 2/3) | Unverified-Low | Low | Low | **P3** |
| AWS Batch | Low (Domain 2/3) | Unverified-Low | Low | Low | **P3** |
| Well-Architected Framework pillars (naming/vocabulary only) | Low-Medium (cross-domain flavor text) | Unverified-Low | Low | Low | **P3** |
| Migration Evaluator / Application Migration Service (MGN) | Low (Domain migration) | Unverified-Low | Low | Low | **P3** |
| Amazon Data Firehose (renamed service, basic recognition) | Low (naming-only refresh) | Unverified-Low | Low | Low (mainly: know the current name) | **P3** |

**P0/P1 count check:** 17 P0 + 17 P1 = 34 higher-priority items span compute, storage, database,
networking, security, and serverless/messaging as required; P2/P3 add migration, monitoring/
governance, and niche storage/compute services to reach 48 total rows.

## 7. Best Current Study Resources

| Resource | Alignment w/ Current Exam | Realism/Depth | Cost | Time | Verdict |
|---|---|---|---|---|---|
| **AWS Skill Builder** (free content + Official Practice Exam) | Always current (AWS-maintained) | Accurate but dry; free question set is short (~20 Qs); paid practice exam is one 65-Q set | Free tier extensive; Official Practice Exam ~$20; Individual subscription ~$29/mo — **these two dollar figures could not be freshly re-verified (JS-rendered pricing pages); treat as plausible but unconfirmed** | 2–4 hrs | Final-days calibration only, not standalone |
| **Tutorials Dojo (Jon Bonso)** | Confirmed "SAA-C03" labeled, $14.99, updated 4–8x/month (directly verified) | Best-in-class explanation depth; widely regarded as closest to real exam difficulty | $14.99 | 15–20 hrs | **Core resource** |
| **Stephane Maarek (Udemy/DataCumulus)** | Regularly updated per exam version | 1.33M+ students, 4.7★ (directly verified); efficient, exam-focused teaching | ~$15–20 on sale | 15–18 hrs (compressible at 1.5–2x) | **Core resource** for this experience level |
| **Adrian Cantrill (learn.cantrill.io)** | Confirmed active, Dec-2025 content updates, targets SAA-C03 | Highest technical depth + labs; genuinely builds lasting skill | $40 | 30–40+ hrs | Skip/skim only — depth is redundant given existing multi-cloud background |
| **Digital Cloud Training (Neal Davis)** | Marketed current; last-updated date unverifiable | Reputed comparable to Tutorials Dojo; large question bank; notable free cheat-sheets | Bundle pricing typically higher than Maarek/TD standalone | ~20 hrs course + 15 hrs drilling | Skip the paid bundle; free cheat sheets optionally worth grabbing |
| **Whizlabs** | Marketed current; unverifiable | Large volume but weaker explanation depth than Tutorials Dojo | Comparable/cheap | Variable | Skip entirely |
| **Andrew Brown / freeCodeCamp (ExamPro) YouTube course** | Surfaced only by one independent aggregator, not cross-checked further | Free, full-length; quality/depth not independently assessed | Free | Variable | Optional zero-cost supplement if budget is the binding constraint |

**Recommended minimal combination:**
1. **Maarek Udemy course** at 1.5–2x, skipping AWS-fundamentals sections — closes AWS-specific
   vocabulary/service-boundary gaps fast (~10–15 effective hrs).
2. **Tutorials Dojo, all 6 practice exams**, reviewing every explanation even on correct answers —
   the resource with the strongest independently-corroborated reputation for exam-realistic
   scenario difficulty (~15–20 hrs).
3. **AWS Skill Builder free question set + one Official Practice Exam**, done in the final 1–2
   days — cheapest way to confirm alignment with AWS's exact answer-key phrasing, since it's
   AWS-authored and therefore always current by definition (~2–3 hrs).

Total: ~$35–50 confirmed (Tutorials Dojo $14.99 + Maarek discounted course, both independently
verified prices) plus an unverified ~$20 for the AWS official practice exam, over roughly 30–35
hours. Cantrill, Digital Cloud Training, and Whizlabs are reasonably skippable specifically because
of existing 11+ years of cross-cloud architecture depth — their marginal value is in building
foundational understanding that isn't needed, not in closing AWS-specific exam gaps.

**Outstanding uncertainty to flag explicitly:** AWS Skill Builder's exact current pricing ($20
practice exam / $29-mo subscription) rests on background knowledge, not a freshly verified fetch —
confirm current pricing directly on skillbuilder.aws before budgeting. Digital Cloud Training's and
Whizlabs' last-updated dates are likewise unconfirmed due to JS-rendered vendor sites blocking
scraping in every research pass to date.
