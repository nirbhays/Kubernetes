# Storage Mastery — AWS SAA-C03

## S3: Bucket Policies vs IAM Policies

**Decision boundary:** IAM policies attach to principals (users/roles) and control what that principal can do across AWS. Bucket policies attach to the resource and control who can access *that bucket*, including cross-account principals that have no IAM identity in your account. If the question involves **cross-account access without creating IAM users in the other account**, or you need to grant access to an anonymous/public principal (`Principal: "*"`), the answer is a bucket policy (or ACL, rarely correct in 2026 exams).

**Evaluation logic (trigger for "access denied" scenarios):** Effective permission = explicit Deny anywhere (SCP, IAM, bucket policy, resource ACL) always wins; otherwise union of Allows from IAM policy AND bucket policy. A classic distractor: "user has full IAM S3 access but still gets 403" → bucket policy has an explicit Deny (often via missing `aws:SourceVpce`/`aws:SourceIp` condition) or **Block Public Access** settings at account/bucket level overriding an ACL/policy that would otherwise allow public access. Always check Block Public Access first when the scenario says public access "isn't working as configured."

**Cross-account pattern to memorize:** Bucket owner ≠ object owner problem — when Account A uploads objects into Account B's bucket, Account B can't read them unless bucket owner enforced ownership is set (see Object Ownership) or the uploader applies `bucket-owner-full-control` ACL. This exact scenario appears repeatedly as "cross-account uploads, receiving account can't access objects."

## Object Ownership

**S3 Object Ownership: "Bucket owner enforced"** is now the default and effectively the only answer the exam wants for new buckets — it disables ACLs entirely, meaning object/bucket permissions are governed solely by IAM + bucket policies. If you see a scenario about cross-account writes causing ownership/ACL headaches, the fix is enabling **Bucket owner enforced** rather than fiddling with canned ACLs. Legacy answers involving `bucket-owner-full-control` ACL are for older exam questions/existing buckets with ACLs still enabled — recognize both but default to bucket-owner-enforced as the modern best practice answer.

## Encryption: SSE-S3 vs SSE-KMS vs Client-Side

| Type | Key management | When it's the answer |
|---|---|---|
| **SSE-S3 (SSE-AES256)** | AWS-managed, no visibility/control | "Encryption at rest, no auditing/rotation control needed, simplest/cheapest" |
| **SSE-KMS** | CMK in KMS, you control policy, get CloudTrail audit trail | Trigger words: "audit key usage," "control who can decrypt," "rotate keys," "separate access control layer independent of S3," "compliance requires key usage logging" |
| **SSE-C** | Customer supplies key per-request, AWS doesn't store it | Rare on exam; "customer must manage own keys but wants AWS to do encryption" |
| **Client-side encryption** | Encrypt before upload, AWS never sees plaintext or key | Trigger: "AWS must never have access to unencrypted data or keys," strictest data sovereignty/compliance requirement |

**Critical gotcha:** SSE-KMS has a **request-rate quota tied to KMS API limits** (GenerateDataKey/Decrypt calls) — high-throughput workloads hitting `ThrottlingException` on S3 GET/PUT is a known exam scenario; the fix is requesting a KMS quota increase, not switching encryption type. Also: **default bucket encryption** (SSE-S3 or SSE-KMS) can be set at bucket level so objects are encrypted even without per-request headers — if a question says "ensure all future uploads are encrypted without app changes," the answer is a bucket default encryption policy, not a bucket policy that *denies* unencrypted PUTs (that's the belt-and-suspenders answer when "enforce," not just "ensure," is the wording — deny-if-missing-header bucket policy condition `s3:x-amz-server-side-encryption`).

## Versioning

Versioning is prerequisite for: Object Lock, cross-region/same-region replication, and MFA Delete. Once enabled, **cannot be disabled**, only suspended. Exam trigger: "protect against accidental deletion/overwrite" → versioning (delete creates a delete marker, doesn't destroy data). Distractor to reject: versioning is NOT a backup/DR solution by itself for cross-region — that requires replication layered on top. Versioning + lifecycle rules together answer "reduce storage cost of old versions while keeping protection" (transition/expire noncurrent versions).

## Lifecycle Rules

Two independent action families: **transition actions** (move current/noncurrent versions between storage classes on a schedule) and **expiration actions** (delete objects/versions, or clean up incomplete multipart uploads). Exam trigger phrase "clean up incomplete multipart uploads after N days" → `AbortIncompleteMultipartUpload` lifecycle rule — commonly the correct answer to "S3 storage costs increasing unexpectedly despite no new object growth" (orphaned multipart parts still bill for storage).

Transition constraints to remember directionally: you can't transition INTO S3 Standard from an IA/cheaper class, and there are minimum storage duration charges on IA/Glacier tiers (early deletion/transition incurs a charge) — if a question describes objects churned or deleted within days of transitioning to Glacier and cost is *higher* than expected, that's the answer (minimum duration penalty).

## Replication: CRR vs SRR

Both require versioning enabled on source **and** destination. Both are **not retroactive** — only replicates objects written after replication is configured (existing objects need S3 Batch Replication to backfill, a common correct answer for "replicate existing objects").

- **CRR (Cross-Region Replication):** trigger words — regulatory/compliance data residency in multiple regions, lowest-latency read access for global users, disaster recovery to a separate region.
- **SRR (Same-Region Replication):** trigger words — aggregating logs from multiple buckets into one, maintaining copies under a different account for isolation (e.g., ransomware/insider-threat protection with different ownership), compliance requiring data replicas within the same jurisdiction/region.

By default replication is **one-way, non-chained** (won't replicate objects that were themselves replicated in, unless replica modification sync / bi-directional replication is explicitly enabled — recognize this as the answer to "objects replicated to bucket B don't propagate to bucket C" or "changes made directly in destination bucket aren't syncing back").

Replication does not replicate: objects encrypted with SSE-C, objects existing before replication was enabled (without Batch Replication), or (unless configured) objects encrypted with SSE-KMS (needs additional KMS key permissions/config explicitly enabled).

## Storage Classes

| Class | Decision trigger |
|---|---|
| **S3 Standard** | Frequent access, unknown/unpredictable access pattern, low latency required |
| **S3 Intelligent-Tiering** | Trigger words: "unknown or changing access patterns," "automatically optimize cost without performance impact or retrieval fees" — this is the exam's favorite "just pick this when unsure" answer for cost-optimization domain questions |
| **S3 Standard-IA** | Infrequent access but needs millisecond retrieval, e.g., backups, DR secondary copies |
| **S3 One Zone-IA** | Infrequent access, **re-creatable data**, cost-sensitive, tolerant of AZ loss — trigger: "secondary copy that can be regenerated" |
| **S3 Glacier Instant Retrieval** | Archive accessed quarterly-ish but needs millisecond retrieval |
| **S3 Glacier Flexible Retrieval** | Archive, retrieval in minutes-to-hours acceptable, occasional access (few times/year) |
| **S3 Glacier Deep Archive** | Trigger: "lowest cost," "retained 7-10 years for compliance," retrieval measured in hours acceptable |
| **S3 Express One Zone** | Trigger: "single-digit millisecond latency," "high-performance/frequently accessed workloads e.g. ML training data, interactive analytics" — single-AZ, directory bucket, distinct namespace from general purpose buckets |

Exam pattern: "minimize cost of unpredictable access patterns without performance/retrieval fee risk" → Intelligent-Tiering, not manual lifecycle rules (manual lifecycle rules are the answer when the access pattern is *known and predictable*, e.g., "logs accessed for 30 days then rarely").

## Presigned URLs

Grant temporary access using the **permissions of the principal that generated the URL** — if that IAM user/role loses permissions or the credentials expire, the URL stops working even before its own expiry. Trigger words: "allow a user without AWS credentials to upload/download a specific object temporarily," "mobile app needs to upload directly to S3 without exposing IAM credentials," "time-limited access to private object." Distractor: presigned URLs are not for granting *ongoing* or *role-based* access — that's IAM/bucket policy territory.

**Expiration mechanics (frequently misstated — memorize precisely):** SigV4 presigned URLs have a **hard protocol maximum of 7 days (604,800 seconds)** via the `X-Amz-Expires` parameter — this is an AWS Signature Version 4 limit, not something adjustable via IAM/bucket policy, and it applies regardless of whether the URL was signed with long-term IAM user credentials or a role. Separately, when the URL is signed using **STS temporary credentials**, the URL's *effective* validity is also capped by the credential/session expiration — whichever is sooner. So a presigned URL generated with an `ExpiresIn` of 6 days but signed by a role session that expires in 1 hour will stop working in 1 hour, even though the requested expiration was longer.

## Multipart Upload

Trigger words: "large object upload" — AWS recommends multipart upload for objects **larger than 100 MB**, and it is **mandatory for objects larger than 5 GB** (a single PutObject request is capped at 5 GB; overall max object size is 5 TB, only reachable via multipart), "improve upload reliability over unstable networks," "parallelize upload for performance," "resume upload after failure." Pairs with **S3 Transfer Acceleration** for the performance domain (see below). Remember `AbortIncompleteMultipartUpload` lifecycle rule cleans up failed/abandoned parts — cost-optimization domain link.

## Transfer Acceleration

Uses CloudFront edge locations to speed up uploads over long distances via optimized network paths (not caching). Exam trigger: "users/offices geographically distant from the bucket's region uploading large files, need faster transfer." Distinguish from CloudFront (CloudFront accelerates *reads/distribution* of content broadly with caching; Transfer Acceleration specifically accelerates *uploads/downloads to/from S3* over the AWS backbone). Not effective (and exam expects you to reject it) when source and bucket are already in the same/nearby region — the "compare speed" tool is used to validate before adopting it.

## Event Notifications

S3 events (`s3:ObjectCreated:*`, `s3:ObjectRemoved:*`, etc.) target **SNS, SQS, or Lambda** (and EventBridge for advanced routing/filtering). Decision boundary:
- **Lambda** direct target: simple, single downstream action, e.g., thumbnail generation, direct processing.
- **SNS**: fan-out to multiple subscribers/multiple downstream systems.
- **SQS**: need buffering/decoupling, downstream consumer processes at its own pace, need retry/DLQ semantics.
- **EventBridge**: need advanced filtering (e.g., only certain prefixes/metadata) or routing to many AWS service targets, or need to combine S3 events with other event sources into one rule engine.

Trigger: "need to filter events based on object metadata/content type before triggering downstream action, or route to multiple different AWS services with complex matching" → EventBridge over native S3 event notifications.

## Object Lock: Governance vs Compliance Mode

Both require versioning enabled and are WORM (write-once-read-many). Decision boundary is **who can bypass the lock**:
- **Governance mode:** users with `s3:BypassGovernanceRetention` IAM permission can shorten/remove retention or delete the object/version. Trigger: "prevent accidental deletion, but allow authorized admins to override in exceptional cases."
- **Compliance mode:** *nobody*, including the root/account owner, can shorten retention or delete before the retention period expires — not even AWS can. Trigger words: "regulatory requirement," "cannot be altered by any user including administrators," "SEC 17a-4 / financial/legal compliance retention."

Also covers **Legal Hold** — independent of retention periods, can be applied/removed by any authorized user regardless of mode, doesn't have an expiration date; trigger: "indefinite hold pending litigation, unrelated to a fixed retention schedule."

## Static Website Hosting

There are **two distinct, mutually exclusive integration patterns** with CloudFront, and conflating them is a common exam trap:

1. **Bucket used as an "S3 origin" (REST API endpoint), static website hosting feature left OFF.** This is the pattern that supports **Origin Access Control (OAC)** — the current recommended replacement for the legacy OAI. Exam trigger for "serve a static site securely without making the bucket public" → CloudFront + OAC + a bucket policy scoped to allow only that CloudFront distribution, with S3 Block Public Access left ON. Since the S3 website-hosting feature (index/error document redirects) isn't in play here, equivalent behavior (default root object, SPA/error routing) is configured on the CloudFront distribution itself.
2. **Bucket's S3 static website hosting endpoint used as a "custom origin."** This endpoint is HTTP-only (no HTTPS, no SigV4 signing support), so it **cannot use OAC or OAI at all** — CloudFront custom origins can't present the request signature these mechanisms require. If a scenario insists on keeping the website-hosting feature's redirect/error-document behavior behind CloudFront, the bucket policy must instead be scoped defensively (e.g., a shared secret via a custom CloudFront origin header checked in the bucket policy) or accept that the bucket needs broader read access — OAC/OAI are not valid answers in this configuration.

Reject "OAI" as the best answer for pattern 1 in 2026-era questions unless the question is clearly testing legacy knowledge — OAC is AWS's current guidance there. Note: S3 website endpoints don't support HTTPS natively — need CloudFront in front for TLS, which is itself a common trigger ("static site must support HTTPS"), and is only achievable cleanly via pattern 1.

## Access Points

Trigger words: "multiple applications/teams need different permission sets to the same shared bucket," "simplify managing access at scale for a bucket with many diverse use cases," "each application needs a distinct access path/policy." Each access point has its own DNS name and policy, scoped to a specific path/prefix or full bucket, layered on top of (not replacing) the bucket policy — both must allow. **Multi-Region Access Points** are the answer for "single global endpoint routing S3 requests to the lowest-latency replica across regions" combined with CRR.

## VPC Endpoints for S3

**Gateway endpoint** (free) vs **Interface endpoint (PrivateLink)** (hourly + data charge): Gateway endpoints only support S3 and DynamoDB, route via a prefix list in the route table, and only work within the same region, not reachable from on-premises/VPN/Direct Connect. Trigger: "EC2 in private subnet needs S3 access without internet gateway/NAT, cost-sensitive, same-region" → Gateway endpoint. Trigger: "access S3 privately **from on-premises via Direct Connect/VPN**, or from a different region, or need the endpoint reachable via a private IP for security-group-based control" → Interface endpoint. A very common cost-optimization distractor: using an Interface endpoint for S3 when a Gateway endpoint would suffice (same-region only, EC2-only) — Gateway is "free" and the better/cheaper answer whenever its constraints are satisfiable.

---

## EBS: Volume Types

| Type | Trigger words |
|---|---|
| **gp3** | Default modern general-purpose SSD; baseline 3,000 IOPS/125 MiB/s **independent of volume size**, IOPS/throughput provisioned separately and cheaper than gp2 for same performance — correct answer whenever the question just says "general purpose," "boot volume," "cost-effective," without an extreme IOPS/latency requirement |
| **gp2** | Legacy; IOPS scale with volume size (3 IOPS/GB, burst via credits) — recognize as the "why is my small gp2 volume slow" root cause (IOPS credit/burst exhaustion), answer is resize or migrate to gp3/io-family |
| **io2 Block Express / io2 / io1** | Trigger: "sub-millisecond latency," "mission-critical low-latency database," "highest IOPS," "99.999% durability," multi-attach requirement |
| **st1 (Throughput Optimized HDD)** | Trigger: "big data," "large sequential I/O," "data warehouse," "log processing" — cannot be a boot volume |
| **sc1 (Cold HDD)** | Trigger: "infrequently accessed," "lowest cost HDD," cold data — cannot be a boot volume |

Distractor pattern: a question describing a relational database needing consistent high IOPS at low cost should map to **gp3** (provision IOPS/throughput independently) rather than jumping straight to io2 — io2/io2 Block Express is reserved for explicit "highest performance / sub-ms latency / mission-critical" language, not just "database."

## EBS Snapshots

Snapshots are stored in S3 (not visible/manageable directly as S3 objects), **incremental** after the first full snapshot — only changed blocks since the last snapshot are stored, which is the standard justification for "cost-efficient backup strategy" answers. Snapshots are region-scoped; copying a snapshot to another region is the mechanism for **cross-region DR of EBS volumes** (trigger: "recover EBS volume in a different region after disaster"). Fast Snapshot Restore (FSR) eliminates the latency penalty of first-access-post-restore ("initialize"/lazy-load) — trigger: "newly created volume from snapshot has degraded performance on first read, need to eliminate this" → FSR, or alternatively pre-warm by reading all blocks.

Snapshots can be automated via **Amazon Data Lifecycle Manager (DLM)** or AWS Backup — trigger: "automate snapshot creation/retention/deletion policy across many volumes" → DLM (EBS/EC2-focused) or AWS Backup (cross-service, centralized policy, needed when the question spans EBS+RDS+DynamoDB+EFS together).

## EBS Encryption

Encryption uses KMS; enabling **"encryption by default"** at the account/region level ensures all new volumes and snapshots are encrypted without per-resource action — trigger: "ensure all future EBS volumes are encrypted without relying on developers to remember." You **cannot directly encrypt an existing unencrypted volume in place** — the pattern is: snapshot → copy snapshot with encryption enabled → create new volume from encrypted snapshot → swap. This exact multi-step flow is a frequent exam answer sequence. Encrypted snapshots can only be shared cross-account by also sharing the CMK key permissions.

## Resizing (Elastic Volumes)

You can increase volume size, change volume type, and modify IOPS/throughput **while the volume is in-use/attached**, with no downtime for the modification submission itself — but the OS must still extend the file system/partition afterward (a step candidates forget: modifying the EBS volume ≠ the OS seeing the extra space). Cannot decrease volume size — the only path to shrink is snapshot → create new smaller volume → migrate data. Trigger: "increase EBS volume size without downtime" → Elastic Volumes modify-in-place, distractor answers involving detach/reattach or snapshot-recreate are unnecessary extra steps here (that pattern is reserved for shrinking or changing AZ, see below).

## AZ Constraints

EBS volumes are **AZ-locked** — cannot attach to an instance in a different AZ. Trigger: "move an EBS volume to a different AZ" or "instance in AZ-b needs a volume currently in AZ-a" → snapshot the volume, create a new volume from the snapshot in the target AZ, attach. This is one of the most repeated SAA-C03 questions. Also relevant to multi-AZ HA architecture questions: EBS itself is not multi-AZ resilient — that's why RDS Multi-AZ / instance store / EFS are alternatives when cross-AZ durability of the storage layer itself (not just the compute) is required.

## Performance

IOPS and throughput scale with provisioned values (gp3/io2) or volume size (gp2); EBS-optimized instances (default on current-gen types) provide dedicated bandwidth between EC2 and EBS separate from general network throughput — trigger: "EBS performance bottleneck despite instance not being network-saturated" → check EBS-optimization/dedicated bandwidth allocation, or upgrade instance type/volume provisioned IOPS. RAID 0 striping across multiple EBS volumes is the answer when a single volume's max IOPS/throughput ceiling is insufficient even after choosing io2 Block Express — recognize this pattern for "need performance beyond a single volume's maximum."

## EC2 Attachment Behavior

Root/boot volumes: by default `DeleteOnTermination=true` (deleted when instance terminates) unless explicitly changed — trigger: "ensure boot volume persists after instance termination for forensic/audit purposes" → modify the DeleteOnTermination attribute to false before termination. Additional (non-root) EBS volumes default to `DeleteOnTermination=false`. Multi-attach (io1/io2 only) allows a single volume to attach to multiple instances in the **same AZ** simultaneously — requires cluster-aware file system (not general-purpose file sharing; a common wrong-answer trap where candidates pick multi-attach EBS instead of EFS for standard shared-storage requirements).

---

## EFS

## Use Cases

Trigger words: "shared file storage across multiple EC2/Linux instances or AZs," "POSIX-compliant file system," "container/Lambda shared persistent storage," "content management/web serving shared across a fleet," "Linux workloads requiring simultaneous read/write from many clients." EFS is NFS-based Linux-only (no native Windows support — Windows shared file needs **FSx for Windows File Server**, a frequent distractor when the OS is Windows). If the question specifies Windows + shared file system, EFS is wrong regardless of other matching criteria.

## Multi-AZ Behavior

EFS is inherently regional and multi-AZ by design — mount targets are created per-AZ, data is redundantly stored across multiple AZs automatically, no manual replication/config needed for that base durability. This is the built-in differentiator vs EBS in HA scenarios: trigger "shared storage that survives AZ failure without extra configuration" → EFS (Standard storage class), not EBS (single-AZ) or S3 (object, not a mountable file system for POSIX workloads needing low-latency file semantics). For DR across regions, **EFS Replication** (managed cross-region replication) is the answer, analogous to CRR for S3.

## Performance / Throughput Modes

- **Throughput modes:** *Bursting* (throughput scales with storage size, burst credit model — trigger: "cost-effective, moderate/variable usage") vs *Provisioned* (fixed throughput independent of storage size, set explicitly — trigger: "high throughput needed but storage size is small," "consistent throughput regardless of data volume") vs *Elastic* (auto-scales throughput up/down with workload, no capacity planning — trigger: "unpredictable/spiky workloads, pay only for what's used, don't want to manage throughput mode manually" — this is the modern default recommended answer for "not sure, minimize management overhead" questions).
- **Performance modes:** *General Purpose* (default, lowest latency, correct for most workloads including web serving/CMS/home directories) vs *Max I/O* (higher aggregate throughput/IOPS at the cost of slightly higher per-operation latency — trigger: "highly parallelized workloads, large number of instances/clients accessing concurrently, big data/media processing at scale"). Distractor: don't pick Max I/O just because a workload is "high performance" — the exam-specific trigger is *highly parallel, many concurrent clients*, not raw single-client speed (General Purpose wins there).

## Lifecycle Policies (EFS)

EFS lifecycle management automatically transitions files not accessed for a set period into **EFS-IA** (Infrequent Access) or **EFS Archive** storage class, and (if configured) can transition files back to Standard on access — trigger: "reduce EFS storage cost for files that are rarely accessed but still need standard file-system semantics and occasional low-latency access." This is the direct EFS analog to S3 lifecycle rules and is a cost-optimization domain favorite. Note: this is officially just "EFS Lifecycle Management" — there is no separately branded "EFS Intelligent-Tiering" product the way S3 has one; don't expect that exact term on the exam.

## EFS vs EBS vs S3

| Dimension | EBS | EFS | S3 |
|---|---|---|---|
| Attachment model | Single instance (or multi-attach io1/io2, same AZ, cluster-aware FS only) | Many instances, many AZs, concurrently | Not a file system — object API (HTTP), no OS-level mount semantics without extra tooling (Mountpoint for S3 / S3 File Gateway) |
| AZ scope | Single AZ | Multi-AZ native | Regional (multi-AZ durability inherent) |
| Protocol | Block device | NFS (POSIX) | REST/HTTPS object API |
| OS support | Linux/Windows | Linux only (Windows → FSx) | OS-agnostic (application-level access) |
| Scaling | Manual resize, fixed provisioned capacity | Elastic, grows/shrinks automatically with usage, no pre-provisioning | Effectively unlimited, no provisioning |
| Exam trigger | "boot volume," "database data files," "single-instance low-latency block storage" | "shared Linux file system across fleet/AZs/containers" | "static assets," "data lake," "backup target," "unstructured object data," "durable event-driven storage" |

Common trap: a question describing "multiple EC2 instances across AZs need to read/write the same files simultaneously" — candidates default to EBS Multi-Attach (wrong: same-AZ only, needs cluster-aware FS, not general-purpose) instead of EFS (correct: native multi-AZ POSIX shared access). Another trap: "store and share large unstructured media files across a global application, no need for POSIX file locking/directory semantics" → S3, not EFS — EFS is over-engineered/costlier when true object storage semantics suffice and no traditional file-system mount is truly required by the application.
