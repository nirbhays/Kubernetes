# Service Comparison Matrix — Audit Log

Each of the 6 categories in `02-service-comparison-matrix.md` was reviewed by an independent auditor agent before inclusion. This log summarizes what the audit caught — evidence the validation pass found real technical errors, not just a rubber stamp. Total: **48 issues** across 6 categories.

## Compute — 8 issues

1. Compute Savings Plans discount claim was backwards — stated as "similar/slightly better" than RIs when it's actually a *lower* discount ceiling traded for flexibility.
2. Fargate GPU support was described as an improving/ambiguous limitation, when it's actually a flat, permanent hard limit (no GPU support at all).
3. "Fargate Savings Plans" was invented as a distinct product name — the correct term is Compute Savings Plans (which span EC2/Fargate/Lambda).
4. Firecracker cold-start time was given an invented precise figure ("tens of seconds") — softened to a qualitative, variable description.
5. ECS task IAM roles were said to be per-container — corrected to per-task-definition (shared by all containers in that task).
6. "Same scaling ceiling" for ECS vs. EKS was an unsupported blanket assertion — softened to "comparable in practice."
7. EC2 billing phrasing ("billed per-second, instance-hour based") was internally inconsistent — clarified as billed per-second, rate quoted hourly.
8. RI/Spot discount percentages (~72%, ~90%) lacked a variability caveat — flagged as illustrative, not guaranteed figures.

## Storage — 9 issues

1. EBS "availability" figures (99.8–99.9%, 99.999%) were actually durability/AFR figures, mislabeled as availability, and contradicted another section of the same draft.
2. S3 "99.99% availability SLA" conflated the 99.99% design target with the actual contractual SLA of 99.9%.
3. FSx for Windows was claimed as the "only" FSx option with AD integration — false, FSx for NetApp ONTAP also supports AD integration.
4. EFS throughput modes were incomplete — missing the distinct "Elastic Throughput" mode (separate from Provisioned) added in 2022.
5. gp2 IOPS description ("16,000 ... burst to 3,000") was muddled/ambiguous about baseline vs. burst behavior.
6. Elastic Volumes "one modification per 6 hours" cooldown is outdated — AWS relaxed this; specific number removed.
7. "128 KB minimum billable object size" was overgeneralized to all Glacier tiers without verification — softened for Glacier Flexible/Deep Archive.
8. Missing mention that S3 has applied SSE-S3 encryption by default to all new objects since January 2023.
9. FSx for Lustre/OpenZFS "millions of IOPS" figures were vendor-marketing ceilings presented as guaranteed specs — relabeled as best-case maximums.

## Databases — 9 issues

1. GSI/Global Tables consistency claim was self-contradictory (implied a recent change to a behavior that "always" existed).
2. Factually wrong claim that DAX serves strongly consistent reads from cache — corrected: those reads bypass the cache entirely.
3. DAX + Transactions API support was hedged as version-dependent — corrected: it's an unconditional, hard limitation.
4. Aurora "~20% higher" pricing vs. RDS was an unverifiable fixed figure — softened to "typically somewhat higher, not an official constant."
5. "Aurora Serverless v2 cannot scale to zero" was repeated 3x and is outdated since AWS added zero-ACU capability.
6. RDS "64 TiB" storage ceiling was overgeneralized — doesn't hold for SQL Server (lower, edition-dependent limits).
7. Aurora replica lag "<10ms" was stated as a hard number — softened to "typical, not guaranteed, can grow under heavy write load."
8. Inconsistent framing of whether Aurora is "part of RDS" or a separate alternative across two sections — clarified with a terminology note.
9. "<30s failover" was attributed solely to Aurora as an exam signal — noted that RDS Multi-AZ DB Cluster also offers comparable fast failover.

## Networking — 8 issues

1. CloudFront + Global Accelerator "isn't typical" together was understated — GA doesn't support CloudFront as an endpoint type at all; it's architecturally not possible.
2. CloudFront "600+ edge locations" was an unnecessary, moving marketing figure — softened to "hundreds of edge locations."
3. Route 53 Simple routing health-check cell was garbled/unparseable — rewritten as a clear, correct statement (no automatic failover).
4. Weighted routing "0–255" weight bound was an unverifiable numeric limit — flagged and softened.
5. Gateway Load Balancer pricing was oversimplified as a flat per-GB model — corrected to GWLB-hours + GLCU-hours.
6. NAT Gateway "100 Gbps" ceiling was stated as fact without caveat — flagged as a figure that has changed before and should be verified.
7. ALB "no static IP" fix was presented inconsistently — one section named only Global Accelerator, another correctly allowed NLB-in-front too; aligned.
8. "Blue-green" was loosely bundled with "canary" as a weighted-routing use case — blue-green is a full cutover, not a gradual shift; removed from that row.

## Messaging — 7 issues

1. SQS FIFO pricing was stated as "same as Standard" — wrong; FIFO carries a real ~25% per-request premium over Standard.
2. FIFO throughput was described as scaling per Message Group ID — corrected: the 300/3,000 TPS ceiling is a fixed per-queue limit, not something Message Group ID count multiplies.
3. SNS filter-policy limitation cited a garbled, invented "10 attributes" figure — removed and described qualitatively instead.
4. SNS was said to filter only on message attributes, not content — outdated; SNS added message-body (payload) filtering in 2022.
5. EventBridge Scheduler was called a "successor" to cron/rate-based EventBridge rules — wrong; it's an additional capability, not a replacement.
6. SNS DLQs were described as needed only for non-SQS subscribers — clarified that DLQs are configurable per-subscription for any protocol.
7. SNS "12.5M+ subscriptions/topic" was stated as a fixed architectural fact — softened to "very high, per current AWS quotas," since it's a revisable service quota.

## Migration — 7 issues

1. DataSync "10 Gbps per agent" was presented as a fixed spec — softened to a variable, conditional throughput description.
2. Snowmobile capacity was understated as "10PB+" — AWS's actual published per-unit capacity is up to 100PB; the 10PB figure was actually the separate "use Snowball Edge instead" threshold.
3. Babelfish (SQL Server compatibility layer) was incorrectly paired with an Oracle→Aurora PostgreSQL migration example.
4. MGN's "free during replication" claim omitted the 90-day-per-server limit, after which an hourly fee applies.
5. DataSync's incremental transfer was misleadingly compared favorably to rsync — rsync actually does finer-grained block-level deltas; DataSync re-copies whole changed files.
6. DataSync pricing was mischaracterized as a "one-time cost model," contradicting the same document's mention of recurring scheduled tasks.
7. An unverifiable claim that "SAA-C03 refreshes have started including DMS Serverless" was flagged and softened — the underlying DMS Serverless fact is accurate, but exam-content-inclusion claims can't be verified.
