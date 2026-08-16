# Security & IAM Mastery (SAA-C03 — Domain 1: Design Secure Architectures, 30%)

## IAM Fundamentals: Users, Groups, Roles

- **Users** = long-term identity, static credentials (password + optional access keys). Exam distractor: any scenario mentioning "application running on EC2 needs to call S3" — **never** the answer is "create an IAM user and store access keys on the instance." Correct answer is always an **IAM role** attached via instance profile.
- **Groups** = collections of users for policy attachment. Cannot be nested, cannot be an identity used by a resource — a group is never a principal in a trust policy.
- **Roles** = identity with no long-term credentials; assumed via STS, produces temporary credentials. Trigger phrase "cross-account," "EC2 needs access," "Lambda needs to call," "federated user," "third-party auditor" → role, always.
- **Key exam boundary**: roles have a **trust policy** (who can assume — the "AssumeRolePolicyDocument") AND **permission policies** (what they can do once assumed). Confusing these two is a classic wrong-answer trap — trust policy ≠ permissions policy.

## Policy Types & Structure

- **Identity-based policies**: attached to user/group/role. Answers "what can this identity do."
- **Resource-based policies**: attached to the resource itself (S3 bucket policy, KMS key policy, Lambda resource policy, SQS/SNS policy, ECR repo policy, VPC endpoint policy, Secrets Manager resource policy). **Only these support specifying a principal from another AWS account without that account assuming a role** — this is the key exam decision point for cross-account S3/KMS access: you can grant access via bucket/key policy alone, no role assumption needed, unlike EC2/Lambda-style access which requires a role.
- Not every service supports resource-based policies — EC2 instances, EBS volumes do not. If exam scenario involves granting cross-account access to a service with no resource policy support, the answer is a **cross-account IAM role**.
- **Permissions boundary**: a managed policy that sets the *maximum* permissions an identity can have — it never grants permissions by itself, only caps them. Used when delegating IAM user/role creation to developers so they can't self-escalate to admin. Distractor: don't confuse with SCPs (org-wide) or with a regular attached policy (grants, doesn't cap).
- **Session policies**: passed inline when calling `AssumeRole`/`AssumeRoleWithSAML`/`AssumeRoleWithWebIdentity`/`GetFederationToken`; further restrict (never expand) the role's permissions for that session only.

## Policy Evaluation Logic

Exam loves a multi-policy scenario and asks "what is the effective permission." Memorize the order:
1. Default: **implicit deny**.
2. Evaluate all applicable policies: identity-based, resource-based, permissions boundaries, SCPs, session policies (in a role assumption).
3. **Explicit DENY anywhere always wins** — overrides any ALLOW, no exceptions.
4. If no explicit deny and at least one ALLOW exists across the applicable policy set → allowed.
5. Cross-account: **both** sides need to allow it — identity policy on caller's side AND resource policy (or role trust) on the resource's side. Missing either = access denied, even if each individually looks permissive.
6. SCPs and permissions boundaries **never grant** — they only filter down. An SCP allowing S3 does nothing if the identity policy doesn't also grant S3.

Exam trigger: "user has an explicit Deny in one policy and Allow in another, what happens?" → Deny wins, always, no exceptions (including deny in SCP, boundary, resource policy, or identity policy).

## STS, AssumeRole, Cross-Account Access

- **STS** issues temporary credentials (access key, secret key, session token) with a defined expiration. Duration behavior differs by call: for the `AssumeRole*` family, the session is capped by the target role's **max session duration** setting (configurable 1–12 hours, default 1 hour if the role owner didn't raise it, and default 1 hour if `DurationSeconds` is unspecified in the call). `GetFederationToken` and `GetSessionToken`, by contrast, support a wider range — 15 minutes up to 36 hours. Don't collapse all STS calls into a single "15 min–12 hr" rule on the exam; know that the role-assumption family tops out at 12 hours while federation-token calls can go up to 36.
- **AssumeRole**: for IAM principals (users/roles) in same or trusted account. Requires target role's trust policy to name the calling account/principal, and caller needs `sts:AssumeRole` permission on the target role ARN.
- **AssumeRoleWithSAML**: for enterprise federation (on-prem AD via ADFS/SAML IdP) — no per-user IAM identity needed.
- **AssumeRoleWithWebIdentity**: for OIDC-based federation (Google/Facebook/Cognito-backed identities) — largely superseded operationally by using **Cognito Identity Pools** as the abstraction layer in application scenarios.
- **Cross-account pattern (the classic exam question)**: Account A user needs access to Account B resource. Answer: create a role in Account B with a trust policy naming Account A (or a specific IAM principal in A), Account A user calls `sts:AssumeRole` on that role's ARN, gets temp creds scoped to B. This is preferred over resource-based-policy-only approaches when the target service lacks resource policies (EC2, most compute) or when you want centralized, auditable, time-boxed access.
- **External ID**: required addition to trust policy when a **third party** (SaaS vendor, MSP) assumes a role into your account — prevents the "confused deputy" problem. Exam trigger phrase: "third-party SaaS tool needs access to your AWS account" → cross-account role + External ID condition, not access keys shared with the vendor.

## Federation & IAM Identity Center

- **IAM Identity Center (successor to AWS SSO)**: the answer whenever the scenario is "**multiple AWS accounts** + **workforce/employee** single sign-on," especially with AWS Organizations already in play. Integrates with external IdPs (Okta, Azure AD, on-prem AD via AD Connector) and assigns **permission sets** (mapped to IAM roles) per account.
- **SAML 2.0 federation (direct, no Identity Center)**: answer when it's a **single account**, existing enterprise IdP, and you want federated users to get a role via `AssumeRoleWithSAML` — often phrased as "avoid creating individual IAM users for each employee."
- **Cognito**: the answer whenever the scenario is a **customer-facing application** (mobile/web app end users), not workforce identity. Never choose Cognito for "employees need to manage AWS resources" — that's Identity Center or SAML federation.
- **Decision rule**: workforce + AWS console/CLI/API access → Identity Center or SAML. Customer-facing app users needing temp AWS creds or app-level auth → Cognito.

## Cognito: User Pools vs Identity Pools

- **User Pools** = the **directory/authentication** layer — sign-up, sign-in, MFA, password policies, hosted UI, JWT tokens (ID token, access token). Answer when the requirement is "authenticate app users" or "manage user directory for a mobile app." Supports social IdPs (Google, Facebook, Apple) and SAML/OIDC as federated providers *into* the pool.
- **Identity Pools (Federated Identities)** = the **authorization** layer — exchanges a User Pool token (or social/SAML token) for **temporary AWS credentials** via STS, scoped by IAM roles, to let the app call AWS services directly (e.g., upload to S3 from a mobile app).
- **Exam boundary**: need login/session management only → User Pool alone. Need the app to directly call AWS APIs (S3, DynamoDB) with temp creds after login → User Pool + Identity Pool together. "Guest/unauthenticated access to AWS resources" → Identity Pool supports unauthenticated roles, User Pool does not apply.

## Permission Boundaries vs SCPs vs Resource Policies (disambiguation table)

| Mechanism | Scope | Can Grant? | Typical Use |
|---|---|---|---|
| Identity policy | Single user/role | Yes | Baseline permission grant |
| Resource policy | Single resource | Yes (incl. cross-account) | S3/KMS/SQS/SNS cross-account, no role needed |
| Permissions boundary | Single user/role (cap only) | No | Delegated admin — prevent privilege escalation |
| SCP | Entire OU/account in Organizations | No | Org-wide guardrails (e.g., deny leaving region, deny disabling CloudTrail) |

Trigger: "prevent even the root user/account admins from doing X across all accounts" → **SCP**, not a permissions boundary (boundary is per-identity, doesn't touch root or other identities in the account).

## AWS Organizations & SCPs

- SCPs apply to **all IAM users and roles in an account, including the account root user** — the one place root isn't untouchable.
- SCPs use the same **explicit deny beats allow** logic, and by default an OU with an SCP attached restricts to only what's explicitly allowed if you replace the default `FullAWSAccess` policy.
- Common exam scenarios: "prevent all accounts in the Sandbox OU from launching resources outside us-east-1" → SCP with a `Deny` + region condition. "Enforce that CloudTrail cannot be disabled by any account" → SCP deny on `cloudtrail:StopLogging`/`DeleteTrail`.
- **Consolidated billing + centralized logging/security** (Security Hub, GuardDuty, Config aggregator, CloudTrail org trail) is the standard "multi-account landing zone" pattern — know that an **organization trail** in the management account captures all member account activity automatically.

## KMS: Managed Keys, Key Policies, Envelope Encryption, Rotation

- **AWS owned keys**: free, not visible/manageable by you, used as default encryption for many services. Not in scope for exam decisions.
- **AWS managed keys** (`aws/service-name`): free, auto-rotated yearly, key policy not editable, used when a service default-encrypts and you don't need custom control.
- **Customer managed keys (CMK)**: you control the key policy, rotation, and can enable **cross-account** or **multi-region** use. Choose CMK whenever the scenario says "need to control who can use the key," "need to share encrypted data across accounts," "need audit trail of key usage separate from AWS defaults," or "need to disable/rotate/delete on your own schedule."
- **Key policy is mandatory and is the root of access control for a KMS key** — even if IAM identity policy grants `kms:Decrypt`, access is denied unless the key policy also allows it (or delegates to IAM via the `"Enable IAM User Permissions"` root statement). This dual-gate is a favorite exam trap identical in shape to S3 bucket policy + IAM policy interplay.
- **Envelope encryption**: KMS `GenerateDataKey` returns a plaintext data key (used to encrypt actual data client-side/by the service) and an encrypted copy of that data key (stored alongside the ciphertext). KMS itself never touches your large payload — only encrypts/decrypts small data keys. This is why KMS has a payload size limit for direct `Encrypt` calls, and why SDKs and services like S3/EBS/RDS use envelope encryption automatically.
- **Rotation**: automatic rotation available for CMKs (opt-in, symmetric encryption keys only) — the default rotation cadence is every 365 days, and it is now configurable (roughly 90–2560 days) rather than fixed at exactly one year. Rotation keeps old key material available to decrypt old ciphertext, transparent to callers. Asymmetric and HMAC keys, and imported key material, do **not** support automatic rotation — manual rotation (new key + re-encrypt or alias swap) is required. Exam trigger: "need to rotate a key you imported yourself" → manual process, not automatic rotation toggle.
- **Multi-Region keys**: for DR/global apps needing the same key material in multiple regions without re-encrypting data on failover — the modern pattern for envelope-encrypted replicated data (e.g., DynamoDB Global Tables, cross-region S3 replication with SSE-KMS), used instead of maintaining separate independent per-region keys.

## Secrets Manager vs Systems Manager Parameter Store

| | Secrets Manager | Parameter Store |
|---|---|---|
| Cost | Paid per secret + API calls | Standard tier free; Advanced tier paid |
| **Automatic rotation** | Native, built-in (Lambda rotation functions, direct integration with RDS/Aurora/Redshift/DocumentDB) | No native rotation — must build your own via Lambda + EventBridge |
| Cross-account sharing | Native resource policy support | Limited/no native cross-account |
| Size limit | Larger (up to ~64KB) | Standard tier smaller (~4KB), Advanced tier larger (~8KB) |
| Use case | Database credentials, API keys needing rotation | Config values, feature flags, non-sensitive or infrequently-rotated secrets, hierarchical config (`/app/prod/db/host`) |

**Decision rule**: exam phrase "automatically rotate database credentials" → Secrets Manager, unconditionally. "Store configuration/environment values cheaply" or "hierarchical parameter structure" → Parameter Store. Both support KMS encryption at rest and IAM-based access control; Parameter Store also integrates directly with CloudFormation and SSM documents for config injection.

## WAF vs Shield vs Firewall Manager (disambiguation)

- **WAF**: Layer 7 (HTTP/HTTPS) filtering — rules for SQL injection, XSS, rate-based rules, geo-blocking, IP reputation lists. Attaches to **CloudFront, ALB, API Gateway, AppSync, Cognito User Pools, Verified Access**. Never attaches to NLB (Layer 4) or raw EC2 without a supported front door.
- **Shield Standard**: automatic, free, always-on, protects against common **Layer 3/4** DDoS (SYN floods, reflection attacks). It is not limited to just CloudFront/Route 53/ELB — it automatically covers **all AWS customers' resources**, with particular relevance to EC2 (behind an Elastic IP), Elastic Load Balancing, CloudFront, Route 53, and AWS Global Accelerator.
- **Shield Advanced**: paid, adds Layer 7 DDoS protection, 24/7 DDoS Response Team (DRT) access, cost protection (credits for scaling costs incurred during an attack), and integrates with WAF for advanced automatic mitigations. Covers the same resource types as Standard (EC2/EIP, ELB, CloudFront, Route 53, Global Accelerator) with enhanced, resource-specific protection. Exam trigger: "need proactive DRT engagement," "need cost protection against DDoS-driven scaling charges," "financial services company needing enhanced DDoS SLA" → Shield Advanced, not Standard.
- **Firewall Manager**: centralizes WAF rule/Shield Advanced/security group management **across accounts in an Organization** — trigger phrase "enforce WAF rules consistently across all accounts/all new resources" → Firewall Manager, not manually attaching WAF web ACLs per account.

## ACM (AWS Certificate Manager)

- Free public TLS certs, auto-renewal, but only usable with **integrated services**: CloudFront, ALB/NLB (via listener), API Gateway (edge/regional), Elastic Beanstalk. **Cannot export the private key** — so cannot use an ACM public cert directly on a self-managed EC2 web server or on-prem server.
- For EC2/self-managed workloads needing a cert with exportable private key → **ACM Private CA** (paid) issuing to a private trust chain, or bring your own cert imported into ACM (import supports third-party certs but still no export after import, and you must manually renew imported certs — ACM doesn't auto-renew certs it didn't issue).
- Cross-region note: ACM certs used with CloudFront must be requested in **us-east-1** regardless of where your distribution's origin lives — classic exam gotcha.

## CloudTrail

- Records **API-level activity** (who did what, when, from where) — management events (control plane) by default, data events (S3 object-level, Lambda invoke) require explicit configuration and cost extra.
- Exam trigger phrases: "who deleted this resource," "audit API calls," "compliance requires record of all account activity" → CloudTrail, not Config (which tracks *state/configuration*, not *who acted*) and not VPC Flow Logs (which is network traffic metadata, not API calls).
- **Organization trail** aggregates all member accounts' events into one S3 bucket in the management account — required pattern for centralized multi-account audit.
- Log file integrity validation (digest files + SHA-256 hashing) is the mechanism to prove logs haven't been tampered with — cite this when the question asks about ensuring trail log integrity for forensics/compliance.
- CloudTrail alone does not alert — pair with **CloudWatch Logs + metric filters + alarms**, or EventBridge, for "notify me when root login occurs" type requirements.

## AWS Config

- Tracks **resource configuration state and change history**, evaluates against **Config Rules** (managed or custom Lambda-backed) for compliance drift. Answer whenever the scenario says "detect when a security group was changed to allow 0.0.0.0/0," "ensure all EBS volumes are encrypted," "continuously assess compliance against a baseline," or "remediate non-compliant resources automatically" (via Config **remediation actions** using SSM Automation documents).
- Distinguish from CloudTrail: Config = "what does this resource look like now vs. before, is it compliant" (state); CloudTrail = "who made the API call that changed it" (action/actor). A question combining both ("who disabled encryption and when did the resource become non-compliant") wants you to name **both** services together.
- **Conformance packs** = packaged sets of Config rules + remediations deployable across an Organization for a compliance framework — the multi-account/org-wide answer.

## GuardDuty

- **Threat detection** via ML/anomaly analysis on VPC Flow Logs, DNS logs, CloudTrail events, S3 data events, EKS audit logs, RDS login activity, Lambda network activity — the core detection sources are agentless (enable-and-go, no infrastructure to deploy). Note the exception: optional **Runtime Monitoring** protection plans (EKS, ECS/Fargate, EC2) do install a lightweight security agent to inspect runtime behavior — know this distinction if the exam contrasts "agentless log analysis" against "runtime protection."
- Answer for: "detect compromised EC2 instance communicating with a crypto-mining pool," "detect anomalous API calls indicating a compromised IAM credential," "detect S3 bucket enumeration/exfiltration behavior," "detect unusual RDS login attempts."
- **Not** a preventive/blocking control — it's detective only. If the exam wants automated remediation, pair GuardDuty findings → EventBridge → Lambda (e.g., auto-quarantine an instance by changing its security group) — a common architecture question.
- Org-wide delegated administrator pattern applies here too (designate one account to manage GuardDuty across all member accounts).

## Macie

- **Sensitive data discovery in S3** specifically — uses ML to find and classify PII, financial data, credentials in S3 objects. Trigger phrase: "identify PII stored in S3 buckets," "data classification for compliance (GDPR/HIPAA/PCI)." Scope is S3-only for data scanning — not a general DLP across all services. Don't confuse with Config (which checks bucket *configuration*, e.g., public access, not *content*).

## Security Hub

- **Aggregation and posture management** layer — collects findings from GuardDuty, Macie, Inspector, Config, Firewall Manager, IAM Access Analyzer, and third-party tools into one normalized dashboard (ASFF format), runs automated checks against standards (CIS AWS Foundations, PCI DSS, AWS Foundational Security Best Practices, NIST).
- Answer when the scenario wants a **single pane of glass for security posture across accounts/services** or "continuously check against CIS benchmark." It does not itself detect threats (that's GuardDuty) or scan data (Macie) or scan for software vulnerabilities on instances/containers/Lambda (that's **Inspector**, worth knowing even though it's not in your list — exam sometimes contrasts Security Hub's aggregation role against Inspector's vulnerability-scanning role).
- Org-wide delegated administrator model, same as GuardDuty/Macie.

## Cross-Cutting Exam Heuristics

- **"No credentials to manage / no long-term keys"** → role + STS, always, for any compute-to-service or service-to-service pattern.
- **"Least privilege" + "prevent privilege escalation by delegated admins"** → permissions boundary.
- **"Across all accounts in the org, prevent/enforce X unconditionally, including for admins"** → SCP.
- **"Cross-account access to a specific resource, no compute involved"** → resource-based policy (S3 bucket policy, KMS key policy) if the service supports it; otherwise cross-account role.
- **"Detect vs. Prevent vs. Respond"**: GuardDuty/Macie/Config = detect; SCP/IAM/security groups/NACLs/WAF = prevent; EventBridge+Lambda automation off Config/GuardDuty findings = respond.
- **"Encrypt but I need to control/audit/rotate/share the key"** → CMK, not AWS managed key.
- **"Rotate database creds automatically"** → Secrets Manager, not Parameter Store.
- **"Third-party accessing my account"** → cross-account role + External ID condition.
