# SAA-C03 Domain 1 Practice Questions — Design Secure Architectures (30% weight)

Focus areas: KMS (customer vs AWS managed keys, key policies, envelope encryption, rotation), Secrets Manager vs Systems Manager Parameter Store, S3 security (bucket policies, Object Lock governance/compliance, SSE-S3/SSE-KMS/SSE-C, access points), encryption in transit vs at rest.

These are **original practice questions** written for personal study, based on publicly documented AWS service behavior as of 2026 and the official SAA-C03 exam guide scope. They are **not** reproductions of any real, leaked, or dumped exam content.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A 6-person startup is about to provision its primary customer database on Amazon RDS for PostgreSQL, ahead of signing a prospective enterprise customer whose security questionnaire requires that "data at rest be encrypted," but does not require the startup to control the key policy, define a custom rotation schedule, or share the key with any other AWS account. The team has no dedicated security engineer, is extremely cost-sensitive, and wants the fastest path to satisfying this one line item before the deal closes next week — and the database has not been created yet, so there is no existing unencrypted instance to migrate.

**Options:**
A. Create the new RDS instance with encryption at rest enabled at launch time, using the AWS managed key (`aws/rds`).
B. Create a customer managed KMS key with a custom key policy restricting usage to specific IAM roles, and use it for RDS encryption.
C. Note in the response that RDS "supports" encryption and leave it disabled, since the requirement only asks about capability, not current configuration.
D. Implement application-level encryption of each database column before writing to RDS, using a key generated and stored by the application itself.

**Correct answer(s):** A

**Why correct:** The AWS managed key is free, requires zero key-policy configuration, and satisfies "data at rest is encrypted" immediately — exactly matching a requirement with no custom control, rotation, or sharing needs. Enabling it is a one-time checkbox at launch (`--storage-encrypted` with the default `aws/rds` key), which fits the "fastest path" constraint. Note that RDS encryption can only be set at instance creation — an already-running, unencrypted RDS instance cannot have encryption toggled on in place; the only path for an existing instance is snapshot it, copy the snapshot with encryption enabled, and restore a new instance from that copy. Since this database has not been created yet, that limitation doesn't apply here.

**Why each wrong option is wrong:** B adds unnecessary key-policy management overhead and cost for a requirement that never asked for custom key control. C fails the stated requirement outright since the questionnaire asks about actual configuration, not theoretical capability. D introduces major application complexity, breaks native RDS indexing/query features, and is wildly disproportionate to a simple at-rest encryption requirement.

**Trigger words:** "no dedicated security engineer," "extremely cost-sensitive," "does not require... control the key policy," "fastest path," "has not been created yet."

**Underlying architectural principle:** Reach for an AWS managed key whenever the requirement is simply "encryption at rest enabled" with no need for custom key policies, rotation schedules, or cross-account sharing — reserve customer managed keys (CMKs) for scenarios that explicitly need that control. Also remember RDS encryption at rest can only be configured at creation time; converting an existing unencrypted instance always requires a snapshot-copy-restore cycle, never an in-place toggle.

---

### Question 2 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A Lambda function's execution role has an identity-based IAM policy granting `kms:Decrypt` on a specific KMS key ARN. A developer testing from the CLI with an IAM user that has the identical `kms:Decrypt` permission on the same key can successfully decrypt objects, but the Lambda function fails every invocation with `AccessDeniedException` when calling the same `Decrypt` API on the same key. The customer managed key (CMK) was originally created by a different platform team using a CloudFormation template. No CloudTrail events show any explicit Deny statements from an SCP or permissions boundary.

**Options:**
A. Update the CMK's key policy to explicitly allow the Lambda execution role's ARN to call `kms:Decrypt` (or verify the key policy includes the default "Enable IAM User Permissions" statement delegating control to IAM policies).
B. Attach the `AdministratorAccess` managed policy to the Lambda execution role to eliminate any possible permission gap.
C. Switch the encryption key from the customer managed key to an AWS managed key so Lambda no longer needs any key-policy configuration.
D. Increase the Lambda function's memory and timeout settings, since `AccessDeniedException` typically indicates the function is being throttled before it can complete the KMS call.

**Correct answer(s):** A

**Why correct:** A KMS key policy is the root of access control for that key — an IAM identity policy allow is necessary but never sufficient by itself. Since the CMK was created outside the Lambda team's control, its key policy likely omits the Lambda role (or lacks the default statement delegating to IAM), so KMS denies the call regardless of what the identity policy says.

**Why each wrong option is wrong:** B grants unrelated, overly broad permissions that violate least privilege and doesn't address the actual dual-gate root cause (though it would coincidentally work, it is not the correct/secure fix). C avoids the problem rather than fixing it and removes the deliberate custom control the platform team presumably created the CMK for. D misdiagnoses the error entirely — `AccessDeniedException` is an authorization error, not a performance/timeout symptom.

**Trigger words:** "customer managed key," "created by a different... team," "identical `kms:Decrypt` permission," "AccessDeniedException" despite matching IAM policy.

**Underlying architectural principle:** For KMS, both the caller's IAM identity policy AND the key's own resource-based key policy must allow the action — an allow on one side without the other results in denial, identical in shape to the S3 bucket-policy-plus-IAM-policy interplay.

---

### Question 3 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A fintech company runs Amazon RDS for MySQL and must rotate the master database password every 30 days as part of a PCI-DSS control, without writing or maintaining any custom rotation Lambda code. The company only has about five secrets total to manage, cost is a secondary concern relative to reducing operational burden, and the security team wants rotation to be natively integrated with RDS so a failed rotation doesn't lock the application out of the database.

**Options:**
A. Store the credential in AWS Secrets Manager and enable its native RDS rotation, which provisions and manages the required rotation Lambda function automatically.
B. Store the credential in Systems Manager Parameter Store as a `SecureString`, and build a custom Lambda function triggered by an EventBridge scheduled rule every 30 days to rotate it.
C. Store the credential in Parameter Store Standard tier as plaintext, and set a calendar reminder for the DBA team to rotate it manually every 30 days.
D. Store the credential in an S3 object encrypted with SSE-KMS, and rotate it manually by re-uploading a new object every 30 days.

**Correct answer(s):** A

**Why correct:** Secrets Manager has native, built-in rotation integration for RDS/Aurora/DocumentDB/Redshift that provisions the rotation Lambda and coordinates safely with the database engine, requiring no custom rotation code from the team.

**Why each wrong option is wrong:** B requires the team to build and maintain their own rotation Lambda and scheduling — exactly what they explicitly want to avoid. C relies on a manual, error-prone human process with no automation, failing the "rotate every 30 days" control reliably. D has no rotation mechanism at all, no RDS integration, and no automatic credential distribution to the application.

**Trigger words:** "rotate... every 30 days," "without writing or maintaining any custom rotation Lambda code," "natively integrated with RDS."

**Underlying architectural principle:** Choose Secrets Manager over Parameter Store whenever the requirement is automatic, native rotation of database (or other supported service) credentials — Parameter Store has no built-in rotation engine.

---

### Question 4 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A healthcare analytics company replicates objects from an S3 bucket in Account A (us-east-1), encrypted with SSE-KMS using a customer managed key owned by Account A, to a disaster-recovery bucket in Account B (eu-west-1) using S3 Cross-Region Replication. Compliance requires the replicated copies to be encrypted with a separate customer managed key that Account B fully controls, and RPO must stay near-zero so replication cannot silently skip encrypted objects. After enabling the replication rule, the team notices SSE-KMS-encrypted objects are not appearing in the destination bucket at all, while unencrypted test objects replicate fine.

**Options:**
A. Grant the replication IAM role permission to use both CMKs (`kms:Decrypt` on the source key, `kms:Encrypt` on the destination key), update both key policies to allow that role, and explicitly configure the replication rule to encrypt replicas using Account B's destination KMS key.
B. Take no further action — SSE-KMS-encrypted objects replicate automatically once Cross-Region Replication is enabled, so the issue must be an unrelated networking problem.
C. Convert all source objects to SSE-S3 before enabling replication, since objects encrypted with SSE-KMS can never be replicated cross-account.
D. Export the source CMK's key material from Account A and import it into a new CMK in Account B so both accounts share identical key material.
E. (not applicable — single-answer)

**Correct answer(s):** A

**Why correct:** S3 replication of SSE-KMS-encrypted objects requires explicit additional configuration: the replication rule must specify a destination encryption key, and the replication role needs permission on both the source and destination CMKs, with both key policies granting that role access — none of which happens automatically just by enabling CRR.

**Why each wrong option is wrong:** B is factually incorrect — SSE-KMS objects are the documented exception that do not replicate under default settings without extra KMS configuration, which is precisely why the test objects (unencrypted) succeeded while the KMS ones silently failed. C is unnecessary since SSE-KMS objects absolutely can be replicated with correct configuration. D is not how AWS KMS works — a CMK's key material generated by AWS cannot be exported/extracted this way (only imported, externally-sourced key material can be re-imported, and this isn't a valid cross-account key-sharing mechanism).

**Trigger words:** "encrypted with SSE-KMS," "separate customer managed key that Account B fully controls," "not appearing in the destination bucket... while unencrypted test objects replicate fine."

**Underlying architectural principle:** SSE-KMS-encrypted objects require explicit KMS key permissions and a destination-key configuration on the replication rule itself — they are not replicated "for free" the way SSE-S3 or unencrypted objects are.

---

### Question 5 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A small photo-sharing startup stores user-uploaded images in S3 and needs encryption at rest enabled for basic due diligence. The team does not need to audit individual decrypt calls, does not need a custom key rotation schedule, and has no plan to share encryption keys across AWS accounts. They want the lowest-cost, lowest-operational-overhead option available.

**Options:**
A. Enable default bucket encryption using SSE-S3 (Amazon S3 managed keys).
B. Enable default bucket encryption using SSE-KMS with a newly created customer managed key and a custom rotation schedule.
C. Require every client application to supply its own encryption key on each request using SSE-C.
D. Implement client-side encryption in the mobile app before any image is uploaded to S3.

**Correct answer(s):** A

**Why correct:** SSE-S3 provides encryption at rest with zero key management overhead and no additional cost, which is exactly sufficient when there is no requirement to audit key usage, control a key policy, or rotate on a custom schedule.

**Why each wrong option is wrong:** B introduces KMS request costs and key-policy management for a requirement that explicitly doesn't need that control. C requires every client to manage and transmit its own key on every request, adding significant operational and security burden for no stated benefit. D requires building and maintaining a client-side encryption/key-management system, far exceeding what "basic due diligence" requires.

**Trigger words:** "does not need to audit," "no custom key rotation schedule," "no plan to share... across AWS accounts," "lowest-cost, lowest-operational-overhead."

**Underlying architectural principle:** SSE-S3 is the correct default whenever a scenario needs "encryption at rest" with no additional control, audit, or sharing requirements — adding SSE-KMS, SSE-C, or client-side encryption without such a requirement is over-engineering.

---

### Question 6 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retail brokerage firm must retain trade confirmation records in S3 for 6 years to satisfy SEC Rule 17a-4, which mandates that records be stored in a non-rewriteable, non-erasable format that cannot be altered or deleted by any party — including the firm's own system administrators and AWS account root user — before the retention period expires. The firm still needs to be able to upload new versions of ongoing records and wants old, expired versions to eventually age out automatically once compliant.

**Options:**
A. Enable S3 Object Lock in Compliance mode with a 6-year retention period and versioning enabled on the bucket.
B. Enable S3 Object Lock in Governance mode with a 6-year retention period, and remove `s3:BypassGovernanceRetention` from every IAM policy in the account.
C. Enable versioning and S3 MFA Delete on the bucket, and rely on a restrictive bucket policy denying `s3:DeleteObject` to all principals.
D. Apply a Legal Hold to every object in the bucket, with no retention period set, and instruct administrators not to remove the hold for 6 years.

**Correct answer(s):** A

**Why correct:** Compliance mode is the only Object Lock mode that guarantees no principal — including the root user — can shorten retention or delete/overwrite a locked version before the retention period expires, which directly satisfies the "cannot be altered by any party, including administrators" requirement of SEC 17a-4.

**Why each wrong option is wrong:** B's protection depends entirely on IAM permissions staying correctly configured forever; a future misconfiguration, or granting `s3:BypassGovernanceRetention` to an over-privileged role, lets that role delete or overwrite locked objects before the retention period ends, which does not meet an "including administrators/root" bar. C's bucket policy can be modified or deleted by an account administrator at any time, so it provides no true WORM guarantee. D's Legal Hold has no fixed retention/expiration behavior and depends on humans never removing it — it's designed for indefinite litigation holds, not a defined 6-year regulatory retention schedule.

**Trigger words:** "cannot be altered or deleted by any party, including... AWS account root user," "SEC Rule 17a-4," "non-rewriteable, non-erasable."

**Underlying architectural principle:** When a scenario says protection must hold even against administrators or the root user, only S3 Object Lock Compliance mode (among S3-native controls) provides that guarantee — Governance mode and bucket-policy-based deletion prevention both remain overridable by sufficiently privileged identities.

---

### Question 7 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A defense contractor's compliance program requires that a specific S3 bucket only ever contain objects encrypted with one designated customer managed KMS key. Any upload attempt that explicitly specifies SSE-S3 or a different KMS key must be rejected outright by S3 — not silently re-encrypted or allowed through — while uploads that omit an encryption header entirely are acceptable, since the bucket's default encryption is expected to transparently apply the designated CMK to them. A recent internal audit found that an application team had explicitly requested SSE-S3 on some uploads and those objects were accepted anyway, even though the bucket's default encryption was already set to the designated CMK. The team needs a combination of controls that closes this gap without breaking legitimate uploads that already specify the correct key (or that omit the header and rely on the default).

**Options:**
A. Configure the bucket's default encryption setting to SSE-KMS using the designated customer managed key.
B. Add a bucket policy statement that denies `s3:PutObject` unless the request's `x-amz-server-side-encryption` header equals `aws:kms` and its `x-amz-server-side-encryption-aws-kms-key-id` header matches the designated CMK's ARN exactly.
C. Enable S3 Object Lock in Governance mode on the bucket.
D. Rely solely on the bucket's default encryption setting, since S3 always overrides any client-specified encryption header with the bucket default.
E. Enable S3 Transfer Acceleration on the bucket so that all in-flight objects are automatically encrypted using the designated CMK before storage.

**Correct answer(s):** A, B

**Why correct:** Default encryption (A) ensures uploads that omit encryption headers entirely are encrypted with the correct CMK — which the requirement accepts — but it does not stop a client from explicitly requesting a different algorithm or key — that gap is exactly what the audit exposed. Only an explicit deny condition in the bucket policy (B) can guarantee rejection of any PUT that explicitly names a non-compliant algorithm or key, which is what's needed together with the default setting to fully close the gap.

**Why each wrong option is wrong:** C's Object Lock controls write-once-read-many retention behavior and has nothing to do with which encryption key is used. D is factually wrong and is the root cause of the audit finding — default encryption does not override an explicitly specified encryption header, it only applies when no header is present. E is unrelated; Transfer Acceleration is a network-path performance feature for faster uploads over the AWS backbone, it does not perform or enforce any encryption.

**Trigger words:** "explicitly specifies SSE-S3 or a different KMS key... rejected outright," "explicitly requested SSE-S3... accepted anyway, even though the bucket's default encryption was already set," "combination of controls."

**Underlying architectural principle:** Default bucket encryption only fills in a *missing* encryption specification; enforcing a specific key against *explicit* client overrides requires a bucket policy condition that denies non-compliant requests outright.

---

### Question 8 [Priority: P2] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media post-production studio handles content under contracts that require the studio itself — not AWS — to generate, hold, and control every encryption key used, down to supplying the exact key material on each individual request. The studio still wants Amazon S3 to perform the actual server-side encryption and decryption operations rather than encrypting content in their own application before upload, and is willing to transmit the key material over HTTPS with every PUT and GET request.

**Options:**
A. Use SSE-C (server-side encryption with customer-provided keys), supplying the key material in the request headers for every upload and download.
B. Use SSE-S3 with S3-managed keys, which already satisfies "the studio controls the key" since AWS manages it on their behalf.
C. Use SSE-KMS with a customer managed key, since a CMK gives the studio full control over the key policy.
D. Use client-side encryption with a custom encryption library, encrypting objects before they ever leave the studio's application.

**Correct answer(s):** A

**Why correct:** SSE-C is the specific S3 encryption mode designed for exactly this requirement: the customer supplies and manages the key material entirely outside AWS, providing it on each request, while S3 still performs the actual server-side encrypt/decrypt work — AWS never stores the key.

**Why each wrong option is wrong:** B is the opposite of the requirement — with SSE-S3 the key is fully AWS-managed and never touched by the customer at all. C still leaves the key stored and managed inside AWS KMS, not held/supplied directly by the studio per request as required. D means AWS never performs the encryption at all (S3 only ever sees ciphertext), which contradicts the explicit requirement that S3 perform the encryption operation.

**Trigger words:** "the studio itself... must generate, hold, and control every encryption key," "supplying the exact key material on each individual request," "wants Amazon S3 to perform the actual... encryption."

**Underlying architectural principle:** SSE-C is the narrow answer for "customer supplies the key per request, but AWS still does the encryption work" — distinct from SSE-KMS (AWS holds the key, customer controls the policy) and client-side encryption (AWS never sees the key or the plaintext).

---

### Question 9 [Priority: P3] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A real-time ad-tech bidding platform ingests millions of small JSON objects per minute into an S3 bucket encrypted with SSE-KMS using a single customer managed key, which is also used by several other buckets across the account for compliance-driven audit consistency. During a traffic surge, application logs begin showing `ThrottlingException: Rate exceeded for GenerateDataKey` on a growing percentage of S3 PUT and GET requests. Compliance mandates continued use of a customer managed KMS key with full CloudTrail audit logging of key usage, ruling out any change that removes KMS from the encryption path, and engineering wants a fix deployable within hours, not a redesign.

**Options:**
A. Request a KMS request-rate quota increase for the account/Region via AWS Support or Service Quotas, and/or reduce the number of `GenerateDataKey` calls needed per object by using data key caching (for example, via the AWS Encryption SDK).
B. Change the bucket's default encryption from SSE-KMS to SSE-S3 to eliminate all KMS API calls from the request path.
C. Enable S3 Transfer Acceleration on the bucket, since it reduces the number of KMS `GenerateDataKey` calls required per object.
D. Migrate all objects to SSE-C so the application supplies its own key material and bypasses the KMS API entirely.

**Correct answer(s):** A

**Why correct:** The throttling is a documented KMS API request-rate quota limitation: cryptographic operations like `GenerateDataKey`, `Encrypt`, and `Decrypt` on symmetric keys share a single quota per AWS account per Region (not a quota scoped to an individual CMK), and that quota is exactly what a traffic surge can exceed. The correct, compliant fix is to raise that account/Region quota via Service Quotas or AWS Support, and/or reduce the number of calls needed through data key caching — not to abandon the encryption approach the compliance requirement mandates. Note that splitting traffic across multiple CMKs would not by itself relieve this throttling, since the quota is shared across all symmetric keys in the account and Region regardless of how many distinct CMKs are involved.

**Why each wrong option is wrong:** B directly violates the compliance mandate to keep a customer managed KMS key with audit logging in the encryption path. C is irrelevant — Transfer Acceleration optimizes network transfer routing and has no effect on the number of KMS API calls generated per object. D also abandons KMS entirely (violating compliance) and additionally shifts significant key-management burden onto the application at a scale where it would be operationally very difficult.

**Trigger words:** "ThrottlingException: Rate exceeded for GenerateDataKey," "rules out any change that removes KMS from the encryption path," "fix deployable within hours, not a redesign."

**Underlying architectural principle:** High-throughput SSE-KMS workloads can hit KMS's own shared, per-account-per-Region API request-rate quota (independent of S3's request limits, and not a per-key quota — spreading requests across multiple CMKs does not increase the available throughput); the fix is a quota increase and/or reducing call volume via data key caching, never switching encryption type when compliance requires KMS.

---

### Question 10 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A large enterprise consolidates finance, marketing, and data-science datasets into a single shared S3 bucket to reduce storage sprawl. Each of the three teams needs a distinct set of permissions scoped to its own prefix within the bucket (finance: read/write to `/finance/*` only; marketing: read-only to `/marketing/*`; data science: read-only across all three prefixes for cross-team analytics), and the security team wants each team's access managed and audited independently without constructing one increasingly complex, hard-to-review bucket policy that has to be edited every time a team's needs change.

**Options:**
A. Create a separate S3 Access Point for each team, scoped to the relevant prefix(es), with an access point policy defining that team's specific permissions, optionally layered under a minimal baseline bucket policy for defense-in-depth.
B. Continue using a single bucket policy, adding a new, clearly labeled statement block for each team as requirements evolve.
C. Split the shared bucket into three separate buckets — one per team — and use S3 Cross-Region Replication to keep data science's read access synchronized with the other two.
D. Attach only IAM identity-based policies to each team's roles referencing the shared bucket ARN and prefix conditions, with no other bucket-level controls.

**Correct answer(s):** A

**Why correct:** S3 Access Points are purpose-built for exactly this scenario — multiple teams/applications needing distinct permission sets to a shared bucket — giving each team its own named access point, DNS endpoint, and independently manageable policy, without one monolithic bucket policy growing unmanageable.

**Why each wrong option is wrong:** B is the exact anti-pattern the team wants to avoid — a single bucket policy that keeps growing and becomes harder to review and audit as more teams are added. C introduces unnecessary architectural complexity (three buckets plus replication) to solve what is fundamentally an access-management problem, not a data-partitioning one, and CRR doesn't provide live read-through access, only asynchronous copies. D ignores that resource-level controls are still valuable for defense-in-depth and doesn't provide the clean, per-team management boundary (separate policy, separate endpoint) that Access Points offer.

**Trigger words:** "distinct set of permissions scoped to its own prefix," "managed and audited independently," "increasingly complex, hard-to-review bucket policy."

**Underlying architectural principle:** Use S3 Access Points when multiple applications or teams need differentiated access to a shared bucket at scale — they decompose one unwieldy bucket policy into multiple independently manageable, named policies.

---

### Question 11 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A payment processor handling cardholder data under PCI-DSS must guarantee that absolutely no request to a specific S3 bucket ever succeeds over plain HTTP, regardless of which IAM principal makes the request, including principals the security team may not yet know about (contractors, forgotten service accounts, future roles). An internal review found that some legacy scripts were still occasionally reaching the bucket over unencrypted HTTP by using an S3 SDK path that didn't default to TLS.

**Options:**
A. Add a bucket policy statement that denies all S3 actions on the bucket and its objects when the condition `aws:SecureTransport` is `false`.
B. Enable default encryption (SSE-KMS) on the bucket, which also enforces that all connections to the bucket use TLS.
C. Attach an IAM policy to every known IAM user and role denying `s3:GetObject` and `s3:PutObject` whenever the request is made over HTTP.
D. Enable S3 Object Lock in Compliance mode, which rejects any request that does not arrive over an encrypted channel.
E. (not applicable — single-answer)

**Correct answer(s):** A

**Why correct:** A resource-based bucket policy with a `Deny` on `aws:SecureTransport: false` is evaluated against every single request to that bucket regardless of the calling principal's identity — including principals not yet created — because it's enforced at the resource level, not per-identity.

**Why each wrong option is wrong:** B is a common misconception — at-rest encryption settings have no effect on the transport protocol used to reach the bucket; SSE-KMS does not force TLS. C only protects the identities the security team remembers to update, failing exactly the "principals we don't yet know about" requirement, and is an operationally fragile, per-principal approach compared to a single resource-level rule. D's Object Lock governs write-once-read-many retention behavior for object versions, not the transport protocol of the connection.

**Trigger words:** "no request... ever succeeds over plain HTTP, regardless of which IAM principal," "principals the security team may not yet know about," "occasionally reaching the bucket over unencrypted HTTP."

**Underlying architectural principle:** To enforce encryption in transit universally and future-proof against unknown principals, use a resource-based policy condition (`aws:SecureTransport`) on the bucket itself rather than per-identity IAM policies, which only cover principals you remember to configure.

---

### Question 12 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A platform team is documenting KMS key rotation behavior for an internal security runbook ahead of a compliance audit, covering a mix of symmetric customer managed keys, an asymmetric CMK used for code signing, an HMAC key used for message authentication, a CMK created from imported external key material, and several AWS managed keys used by default service encryption. They need to identify exactly two statements below that are factually accurate to include in the runbook.

**Options:**
A. Automatic key rotation is only supported for symmetric encryption customer managed keys — the asymmetric and HMAC keys require a manual rotation process instead.
B. The rotation period for a customer managed key with automatic rotation enabled can now be configured to a custom interval (roughly 90 to 2560 days) rather than being fixed at exactly 365 days.
C. When a CMK's key material rotates, the previous key material is deleted immediately, so any ciphertext encrypted under the prior key version becomes permanently undecryptable.
D. AWS managed keys (`aws/service-name`) are never rotated automatically and must be rotated manually by the account owner on their own schedule.
E. Enabling automatic rotation on a CMK created from imported key material causes KMS to automatically generate and import fresh key material for that CMK every rotation period.

**Correct answer(s):** A, B

**Why correct:** A is accurate — automatic rotation only applies to symmetric encryption CMKs; asymmetric and HMAC key types are excluded and require manual rotation (create new key/material and cut over). B is accurate — AWS now allows configuring a custom rotation period (roughly 90–2560 days) for CMKs with automatic rotation enabled, rather than a fixed 365-day cycle.

**Why each wrong option is wrong:** C is false — KMS retains all previous key material internally after rotation, transparently using the correct historical version to decrypt old ciphertext; nothing becomes undecryptable due to rotation. D is false — AWS managed keys ARE rotated automatically on a fixed yearly cadence by AWS; the customer simply cannot configure or disable that rotation. E is false — imported key material does not support automatic rotation at all; keeping it current requires manually importing new key material into a new key (or new key version) and updating aliases.

**Trigger words:** "asymmetric CMK... HMAC key... CMK created from imported external key material," "exactly two statements... are factually accurate."

**Underlying architectural principle:** Automatic KMS rotation is scoped narrowly to symmetric CMKs on a configurable (not fixed) schedule, retains old key material for decrypting historical ciphertext, and never applies to asymmetric keys, HMAC keys, imported key material, or AWS managed keys' rotation mechanism (which is automatic but not customer-configurable).

---

### Question 13 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An engineering organization manages several hundred non-secret configuration values for its microservices — feature flags, service endpoint URLs, timeout thresholds — organized hierarchically (e.g., `/app/prod/checkout/timeout-ms`, `/app/staging/checkout/timeout-ms`). Values change infrequently, don't require automatic rotation, and the team wants tight integration with their existing CloudFormation stacks and SSM Automation documents, while keeping cost as close to zero as possible given the sheer number of values involved.

**Options:**
A. Store the values as `SecureString` and `String` parameters in AWS Systems Manager Parameter Store (Standard tier), organized under a hierarchical naming structure.
B. Store each value as an individual secret in AWS Secrets Manager, since it provides stronger encryption guarantees than Parameter Store.
C. Hard-code the values as environment variables baked into each service's container image at build time.
D. Store the values as items in a DynamoDB table with a partition key representing the hierarchical path.

**Correct answer(s):** A

**Why correct:** Parameter Store's Standard tier is free, natively supports hierarchical naming (`/app/prod/...`), integrates directly with CloudFormation and SSM documents, and is purpose-built for exactly this kind of high-volume, infrequently-changing, non-rotated configuration data.

**Why each wrong option is wrong:** B would incur a per-secret cost multiplied across several hundred values for capability (rotation, fine-grained resource policies) the requirement never asks for, making it needlessly expensive. C requires rebuilding and redeploying every container image just to change a single config value, eliminating any runtime flexibility. D works technically but requires building custom read/write tooling and IAM access patterns from scratch, duplicating functionality Parameter Store already provides natively and integrates with CloudFormation out of the box.

**Trigger words:** "organized hierarchically," "don't require automatic rotation," "tight integration with... CloudFormation... SSM Automation," "cost as close to zero as possible."

**Underlying architectural principle:** Parameter Store is the cost-efficient, hierarchical answer for high-volume configuration data without rotation needs; Secrets Manager is reserved for secrets that specifically need native automatic rotation or fine-grained cross-account secret sharing.

---

### Question 14 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A global SaaS company runs an active-active application in us-east-1 and eu-west-1, backed by a DynamoDB Global Table replicated between the two regions. Before writing any record, the application itself performs client-side envelope encryption of the sensitive payload (generating a data key via KMS and encrypting the payload with it) — the ciphertext, not the plaintext, is what's actually stored in the item and replicated by DynamoDB Global Tables. The company requires that failover between regions be near-instantaneous: whichever region's application servers receive traffic must be able to decrypt any record immediately — including records originally encrypted by application servers in the other region — using a purely local KMS API call, with no cross-region call and no re-encryption/conversion step of any kind.

**Options:**
A. Create an AWS KMS multi-Region key, replicate it into eu-west-1, and have the application call the local replica key directly (via the AWS Encryption SDK or native `GenerateDataKey`/`Decrypt` calls) for envelope encryption in whichever region is handling the request — so a data key generated against the key in one region can be decrypted locally against its replica in the other region, with no cross-region call.
B. Create two independent, single-region customer managed keys — one in each region — and use AWS Database Migration Service to re-encrypt data with the target region's key immediately upon failover.
C. Use the AWS managed key for DynamoDB (`aws/dynamodb`) in both regions, since AWS managed keys are global resources automatically available and identical in every region.
D. Use a single-region customer managed key created in us-east-1, and grant the eu-west-1 application role cross-region access to it via a permissive key policy statement, so eu-west-1 servers call the us-east-1 key directly for every decrypt.

**Correct answer(s):** A

**Why correct:** AWS KMS multi-Region keys are sets of related keys — one primary and one or more replicas — that share the same key ID and underlying key material across regions. A data key wrapped by the key in one region can be unwrapped by its replica in another region with a purely local KMS call and no re-encryption step, which is exactly the "encrypt once, decrypt anywhere, instantly" property this failover design needs. AWS documents this specifically for client-side/application-level encryption and active-active, multi-region architectures — it's a property of the application (or the AWS Encryption SDK) calling the key directly, not something DynamoDB's own transparent server-side encryption-at-rest layer automatically inherits just because an MRK happens to sit underneath it (most AWS services that manage their own encryption-at-rest, including S3's default-encryption-plus-replication path, still perform their normal decrypt-and-re-encrypt-at-the-destination behavior even when the configured key is technically a multi-Region key).

**Why each wrong option is wrong:** B introduces an explicit re-encryption step via DMS at failover time, directly violating the "no re-encryption/conversion step" and "near-instantaneous" requirements. C is factually incorrect — AWS managed keys are independent, region-scoped resources with independent key material per region, not a single shared global key, so `aws/dynamodb` in eu-west-1 cannot decrypt something wrapped under `aws/dynamodb` in us-east-1. D is technically possible to configure (a KMS API call can be addressed to a key's home region from anywhere with network connectivity and permissions), but it reintroduces the exact cross-region call the design is trying to eliminate, adds latency, and — critically — creates a hard dependency on us-east-1's availability: if us-east-1 is the region experiencing the outage that triggered failover, eu-west-1 could lose the ability to decrypt anything at all, the opposite of resilient failover.

**Trigger words:** "active-active," "client-side envelope encryption," "no cross-region call and no re-encryption/conversion step," "near-instantaneous... whichever region."

**Underlying architectural principle:** KMS multi-Region keys let an application encrypt with one regional key and decrypt with its interoperable replica in another region using only local API calls — this benefit applies to how the *application* (or the AWS Encryption SDK) directly calls KMS for envelope encryption. Most AWS services that transparently manage their own encryption-at-rest (S3 default encryption plus replication, DynamoDB's own SSE) still perform their usual decrypt-and-re-encrypt-at-the-destination behavior even when the underlying key is a multi-Region key, so multi-Region keys don't automatically make *those* managed-replication paths re-encryption-free — only direct, application-level key usage reliably gets that property.

---

### Question 15 [Priority: P1] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A telehealth SaaS platform stores electronic protected health information (ePHI) subject to HIPAA. Traffic flows from patient browsers to an Application Load Balancer, then to EC2 application servers, which write clinical notes into an S3 bucket. The security team requires that ePHI be encrypted at rest using a customer managed key that they can disable at any moment to instantly and completely revoke all access to stored data, and that all network traffic carrying ePHI — from the browser all the way to storage — be encrypted, with no segment of the path ever carrying plaintext ePHI over the network. Cost and RTO are not primary constraints for this particular design decision; correctness of the security control is. Select the two actions that together satisfy both requirements.

**Options:**
A. Configure HTTPS-only listeners on the ALB using an ACM-issued certificate, configure the ALB's target group to use HTTPS as the backend protocol (so the ALB re-encrypts traffic to the EC2 instances rather than forwarding it as plain HTTP), and add a bucket policy statement denying any S3 request where `aws:SecureTransport` is `false` — ensuring every network hop carrying ePHI (browser-to-ALB, ALB-to-EC2, and EC2-to-S3) is TLS-encrypted end to end.
B. Set the S3 bucket's default encryption to SSE-KMS using a customer managed key whose key policy restricts `kms:Decrypt` to only the application's EC2 instance role, so the security team can disable the key at any time to immediately block all data access.
C. Configure the ALB in raw TCP pass-through mode so encrypted traffic reaches the EC2 instances without the ALB terminating TLS at all, eliminating the need to manage a certificate.
D. Rely on the default encryption AWS automatically applies to all new S3 buckets (SSE-S3), since it already satisfies HIPAA's at-rest encryption expectations without any additional key management.
E. Store clinical notes in S3 without encryption, relying entirely on IAM policies to restrict access, since HIPAA's Security Rule addresses access control rather than encryption specifically.

**Correct answer(s):** A, B

**Why correct:** A guarantees encryption in transit across all three hops (browser-to-ALB via TLS termination, ALB-to-EC2 via an HTTPS backend/target-group protocol so the ALB re-encrypts before forwarding, and EC2-to-S3 enforced via the `aws:SecureTransport` deny condition), while B guarantees at-rest encryption under a customer managed key whose disablement instantly cuts off `kms:Decrypt` for every consumer, satisfying the "instantly and completely revoke all access" requirement — something only a CMK the security team controls can provide.

**Why each wrong option is wrong:** C is not achievable with an Application Load Balancer — raw TCP pass-through without TLS termination is an NLB (Layer 4) capability, not an ALB (Layer 7) one, and removing certificate management doesn't address the stated encryption or key-control requirements anyway. D fails the explicit "customer managed key they can disable to instantly revoke access" requirement, since SSE-S3 uses an AWS-controlled key the customer cannot disable or control. E fails the at-rest encryption requirement outright by leaving ePHI unencrypted, which does not meet the security team's explicit mandate regardless of how HIPAA's addressable specifications are interpreted elsewhere.

**Trigger words:** "customer managed key that they can disable... to instantly and completely revoke all access," "no segment of the path ever carrying plaintext ePHI over the network," "correctness of the security control is [the primary constraint]."

**Underlying architectural principle:** Meeting a combined "instant revocation" plus "true end-to-end transit encryption" requirement needs two independent controls — a customer managed KMS key (for at-rest, revocable-by-disable) and enforced TLS at *every* hop (client-facing ALB HTTPS listener, an HTTPS backend/target-group protocol so the ALB-to-instance leg isn't silently downgraded to plain HTTP, and a bucket-level `aws:SecureTransport` deny for the application-to-S3 leg) — neither control alone satisfies both halves of the requirement, and it's easy to forget the ALB's backend leg since ALBs default to HTTP there unless explicitly configured otherwise.

---

### Question 16 [Priority: P2] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A logistics company needs to share a database credential secret with a trusted partner's Lambda function running in the partner's own AWS account, so the partner's function can query a shared reporting database. The company does not want to duplicate the secret into the partner's account, does not want to create any IAM users for the partner, and needs the ability to revoke the partner's access instantly by removing a single policy statement if the partnership ends.

**Options:**
A. Attach a resource-based policy to the AWS Secrets Manager secret granting the partner account's specific IAM role ARN `secretsmanager:GetSecretValue`, and update the secret's encryption key policy (if a customer managed key is used) to also grant that role `kms:Decrypt`.
B. Export the secret's plaintext value and share it with the partner over an encrypted email so they can store it in their own Secrets Manager instance.
C. Create an IAM user in the logistics company's account scoped only to that secret, and issue the partner a long-lived access key.
D. Store the value in a Systems Manager Parameter Store `SecureString` instead, since Parameter Store has stronger native cross-account resource-based policy support than Secrets Manager.
E. (not applicable — single-answer)

**Correct answer(s):** A

**Why correct:** Secrets Manager secrets support native resource-based (secret) policies that can name a specific external account's principal, enabling direct cross-account access to a single secret with no duplication, no shared credentials, and instant revocation by removing the policy statement — and if a CMK protects the secret, the key policy must grant the same principal decrypt access as well.

**Why each wrong option is wrong:** B creates a duplicated, unmanaged copy of the secret with no central revocation point and introduces an insecure sharing channel. C reintroduces exactly the long-lived-credential-sharing pattern the company wants to avoid, with none of the auditability of resource-based cross-account access. D is factually backwards — Secrets Manager, not Parameter Store, has the more mature native cross-account resource-based policy support for secret sharing.

**Trigger words:** "does not want to duplicate the secret," "no IAM users for the partner," "revoke the partner's access instantly by removing a single policy statement."

**Underlying architectural principle:** Cross-account access to a single, specific secret without duplicating it or issuing credentials is achieved via a resource-based (secret) policy on the Secrets Manager secret — paired with the KMS key policy if a CMK is used — rather than any IAM-user-and-key-sharing pattern.

---

### Question 17 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A pharmaceutical company's compliance mandate requires that every object in a specific S3 bucket be encrypted with one designated customer managed KMS key — CMK "alpha." Any upload attempt that explicitly specifies a different key or SSE-S3 must be rejected outright by S3 itself; uploads that omit an encryption specification entirely are acceptable, since the bucket's default encryption — already configured to use CMK alpha — fills that in automatically. During an incident review, the security team discovers that a misconfigured internal tool has been successfully uploading objects encrypted with CMK "beta" (a different customer managed key the tool's IAM role also happens to have permission to use) by explicitly specifying that key on each PUT request.

**Options:**
A. Add a bucket policy statement denying `s3:PutObject` unless the request's `x-amz-server-side-encryption` header equals `aws:kms` and its `x-amz-server-side-encryption-aws-kms-key-id` header exactly matches CMK alpha's ARN.
B. Revoke the misconfigured tool's IAM role's `s3:PutObject` permission entirely on that bucket, since removing the tool's write access is the most direct fix.
C. Re-save the bucket's default encryption setting to CMK alpha again, since default encryption settings can silently degrade over time and need periodic reapplication.
D. Enable S3 Object Lock in Governance mode on the bucket to prevent uploads that don't match the compliance-designated key.

**Correct answer(s):** A

**Why correct:** Default bucket encryption only applies when a request omits an encryption specification — it does not override or block a request that explicitly names a different key, which is exactly how CMK beta got through. Only an explicit deny condition scoped to CMK alpha's ARN in the bucket policy will reject any PUT that doesn't specify exactly that key, closing the gap regardless of what the calling role's IAM permissions otherwise allow.

**Why each wrong option is wrong:** B only stops this one specific tool and doesn't create a durable, bucket-wide guarantee against any future misconfigured client explicitly specifying the wrong key. C is based on a false premise — default encryption settings don't "degrade" and re-saving it would not have prevented an explicit key override in the first place. D's Object Lock governs WORM retention/deletion behavior for object versions, not which encryption key is permitted on upload.

**Trigger words:** "explicitly specifying that key on each PUT request," "successfully uploading objects encrypted with CMK 'beta'... even though the bucket's default encryption was already configured to use CMK alpha."

**Underlying architectural principle:** Enforcing that only one specific KMS key is ever accepted for uploads requires an explicit bucket-policy deny keyed on the KMS key ARN header — default encryption alone never blocks an explicitly specified alternate key or algorithm.

---

### Question 18 [Priority: P2] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A pharmaceutical company must retain clinical trial documents in S3 for 10 years under FDA regulation, with an absolute mandate that not even the company's own AWS account root user can delete the documents or shorten their retention period before the 10 years elapse. Separately, to protect against ransomware and insider threats within the primary AWS account, the company also wants an independent, equally immutable copy of every document maintained in a completely separate AWS account owned by an external compliance auditor, so a compromise of the primary account cannot affect the auditor's copy. Select the two actions that together satisfy both requirements.

**Options:**
A. Enable versioning and S3 Object Lock in Compliance mode with a 10-year retention period on the primary bucket.
B. Configure S3 Replication (Same-Region or Cross-Region) from the primary bucket to a bucket in the auditor's separate AWS account, with the destination bucket also configured with versioning and Object Lock in Compliance mode, using the replication owner override option (`AccessControlTranslation`) so the auditor's account owns the replicated objects.
C. Enable S3 Object Lock in Governance mode on the primary bucket, and grant the compliance team's role `s3:BypassGovernanceRetention` so they retain a documented, centrally audited way to manage exceptions.
D. Add an S3 lifecycle rule that transitions objects older than 30 days to S3 Glacier Deep Archive in the auditor's AWS account to reduce long-term storage cost.
E. Attach an IAM permissions boundary to every role and user in the primary account that denies `s3:DeleteObject`, ensuring even the root user cannot remove the documents.

**Correct answer(s):** A, B

**Why correct:** Compliance mode (A) is the only Object Lock mode that blocks deletion or retention-shortening by every principal, including the root user, satisfying the first requirement on the primary bucket. Replication to a bucket in the auditor's own account with the owner override option and its own Compliance-mode Object Lock configuration (B) creates the independently owned, equally immutable second copy needed to survive a compromise of the primary account.

**Why each wrong option is wrong:** C explicitly grants a bypass permission, which directly contradicts an "absolute mandate" that no one — including administrators — can override the retention, and Governance mode's protection depends entirely on that permission staying restricted. D is not a valid mechanism for placing a copy into a different AWS account — S3 lifecycle rules operate within the same bucket/account and cannot target a bucket owned by another account, so it fails the "separate AWS account" requirement entirely. E is ineffective because IAM permissions boundaries do not apply to (and cannot restrict) the AWS account root user, which directly fails the "not even the root user" requirement — one of several documented cases where root remains unrestricted by an IAM-layer control.

**Trigger words:** "not even the company's own AWS account root user," "completely separate AWS account owned by an external compliance auditor," "a compromise of the primary account cannot affect the auditor's copy."

**Underlying architectural principle:** Achieving both "immutable even against root" and "immutable, independently-owned off-account copy" requires layering S3 Object Lock Compliance mode on both the primary bucket and a cross-account replica (with the replication owner override option) — permissions boundaries and Governance-mode bypasses cannot satisfy a "not even root/admins" requirement.

---

### Question 19 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company is launching a new public-facing web application behind an Application Load Balancer and wants all browser traffic encrypted end-to-end using a certificate that is free and renews automatically with no manual intervention. They also want any request that arrives on plain HTTP to be automatically redirected to HTTPS, and want to avoid any custom certificate-management process for a small internal team with no PKI experience.

**Options:**
A. Request a public TLS certificate through AWS Certificate Manager (ACM), attach it to an HTTPS listener on the ALB, and add a listener rule that redirects HTTP:80 traffic to HTTPS:443.
B. Generate a self-signed certificate using OpenSSL and upload it to IAM for use as the ALB's certificate.
C. Configure only an HTTP listener on the ALB, and enable an "Enforce HTTPS" flag on the target group to upgrade connections automatically.
D. Store a certificate as a Secrets Manager secret and reference the secret ARN directly in the ALB's target group configuration.

**Correct answer(s):** A

**Why correct:** ACM issues free public certificates that auto-renew with zero manual steps, and attaching one to an ALB HTTPS listener plus a redirect rule for the HTTP listener is the standard, fully managed pattern for end-to-end encrypted traffic with automatic HTTP-to-HTTPS redirection.

**Why each wrong option is wrong:** B requires manual certificate generation and renewal, and browsers will show trust warnings for a self-signed certificate, defeating the "free, auto-renewing" and end-user-trust requirements. C describes a non-existent ALB feature — there is no target-group-level flag that "enforces HTTPS" on an HTTP-only listener; TLS termination requires an actual HTTPS listener with a certificate. D is not how ALB certificates work — target groups don't reference certificates via Secrets Manager ARNs; certificates are attached directly to HTTPS/TLS listeners, typically sourced from ACM (or IAM for imported certs).

**Trigger words:** "free and renews automatically with no manual intervention," "avoid any custom certificate-management process," "no PKI experience."

**Underlying architectural principle:** ACM-issued public certificates attached to an ALB HTTPS listener, paired with an HTTP-to-HTTPS redirect rule, is the standard zero-maintenance pattern for enforcing encryption in transit on a public web application.

---

### Question 20 [Priority: P3] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A defense contractor imported its own externally generated key material into a KMS customer managed key (BYOK) to satisfy a regulatory requirement about key provenance, and separately maintains an asymmetric CMK used to sign software release artifacts. Security policy requires periodically refreshing the cryptographic material behind both keys, but the team must retain the ability to decrypt data encrypted under the older material (for the imported-material key) and verify signatures created with the older material (for the asymmetric key) after each refresh. A junior engineer proposes simply toggling on "automatic key rotation" in the KMS console for both keys to satisfy the policy.

**Options:**
A. For the imported-material CMK, import new key material into the same key and perform on-demand rotation (`kms:RotateKeyOnDemand`) so the key ID/ARN never changes and KMS automatically retains the prior key material to decrypt data encrypted before the rotation. For the asymmetric signing CMK — which supports neither automatic nor on-demand rotation — manually create a new CMK, use a key alias to point new signing operations at it going forward, and keep the original CMK enabled and available to verify signatures created before the cutover.
B. Enable the automatic key rotation toggle on both keys — as of 2026, KMS extended automatic rotation support to all key types, including imported key material and asymmetric keys.
C. Delete the old CMK immediately once new key material is imported, since retaining old, "rotated-out" key material anywhere is itself a compliance risk.
D. Configure AWS Certificate Manager to manage rotation of the underlying KMS key material automatically on the team's behalf.

**Correct answer(s):** A

**Why correct:** Neither imported key material nor asymmetric keys support *automatic* rotation. Imported (`EXTERNAL` origin) symmetric key material does, however, support *on-demand* rotation: you import new key material into the existing key (placing it in a "pending rotation" state) and then call `RotateKeyOnDemand`, which rotates in place — same key ID, same ARN, no application changes — while KMS keeps the previous key material available to decrypt older ciphertext. Asymmetric CMKs support neither automatic nor on-demand rotation at all, so refreshing the signing key's material requires the fully manual pattern: create a new CMK, cut new signing traffic over to it via an alias, and retain the original CMK (still enabled) so old signatures remain verifiable.

**Why each wrong option is wrong:** B is factually false — KMS automatic rotation remains unsupported for imported key material and asymmetric (and HMAC) keys; the junior engineer's proposal would silently fail to achieve anything for either key. C is unsafe — deleting the old key material immediately, without first ensuring nothing still needs to decrypt old ciphertext or verify old signatures, breaks that access with no recovery path (KMS key deletion is deliberately delayed/irreversible-after-waiting-period for this reason). D is not a real capability — ACM manages TLS certificates, not KMS key material, and has no role in KMS key rotation.

**Trigger words:** "imported its own externally generated key material," "asymmetric CMK used to sign," "retain the ability to decrypt... and verify signatures created with the older material," "simply toggling on 'automatic key rotation.'"

**Underlying architectural principle:** Automatic key rotation is available only for symmetric CMKs; on-demand rotation additionally covers symmetric CMKs with imported key material (rotate in place via `RotateKeyOnDemand` after importing new material — same key ID, old material retained automatically for decryption). Asymmetric keys, HMAC keys, and custom-key-store keys support neither and must be refreshed via the fully manual create-new-key-and-alias-over process, always while deliberately retaining the old key to preserve access to data or signatures created under it.

---

*End of Domain 1 practice set (20 questions). Distribution: 3 Easy, 8 Medium, 6 Hard, 3 Very Hard; 4 Multiple-Response, 16 Single-Answer. Original content for personal study — not sourced from or reproducing any real/leaked SAA-C03 exam questions.*
