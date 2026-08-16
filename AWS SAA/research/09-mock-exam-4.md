# AWS SAA-C03 Mock Exam 4

*Difficulty: Harder than the real exam.*

These are 65 original practice questions (not real or leaked exam content). Each question is self-contained with its correct answer(s) and explanation inline — no separate answer key is needed.

---

### Question 1 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company's data engineering team members belong to an IAM group `DataEngineers` that has a policy attached allowing `s3:*` on a specific analytics bucket. Separately, the security team attached a policy directly to one user in that group, `svc-etl`, which explicitly denies `s3:DeleteObject` on all resources for compliance reasons. The `svc-etl` user now needs to run a nightly ETL job that deletes temporary staging objects from the analytics bucket, but every delete call fails with `AccessDenied`. DevOps is confused because the group policy clearly allows `s3:*`.
**Options:**
A. IAM evaluates all applicable policies together, and an explicit Deny always overrides any Allow, so the identity-based deny attached directly to `svc-etl` takes precedence regardless of the group's Allow policy
B. S3 bucket policies always take precedence over IAM identity-based policies, so the bucket must contain a hidden deny
C. Because `svc-etl` is in the `DataEngineers` group, group policies are ignored whenever any policy is attached directly to the user
D. IAM policies are evaluated in alphabetical order by policy name, and the deny policy happens to sort before the group's allow policy
**Correct answer(s):** A
**Explanation:** IAM's policy evaluation logic combines every identity-based, resource-based, and boundary policy that applies to a request, and an explicit Deny in any one of them always wins over an Allow. Option C is the most tempting distractor because people assume "most specific policy wins," but IAM does not work that way — it aggregates all statements and only an explicit Deny short-circuits the evaluation.

### Question 2 [Domain: 1] [Type: Single-Answer]
**Scenario:** ThirdPartySaaS Inc. runs a monitoring dashboard product and needs read-only access to pull CloudWatch metrics from a customer's AWS account. The customer's security team is worried about the "confused deputy" problem, where a malicious third party could trick ThirdPartySaaS's service into acting on the wrong customer account by reusing a role ARN. The solution must not involve distributing any long-term credentials and must let the customer revoke access independently at any time.
**Options:**
A. Create a cross-account IAM role in the customer's account with a trust policy scoped to ThirdPartySaaS's specific AWS account ID, and require a unique `sts:ExternalId` condition that ThirdPartySaaS must supply on every `sts:AssumeRole` call
B. Create an IAM user for ThirdPartySaaS in the customer account and share long-term access keys via encrypted email
C. Enable AWS account root user access for ThirdPartySaaS and rotate the root password monthly
D. Create a CloudWatch resource-based policy allowing ThirdPartySaaS's account root ARN with no additional conditions
**Correct answer(s):** A
**Explanation:** Scoping the trust policy to the specific external account and enforcing a unique `ExternalId` is the AWS-documented mitigation for the confused deputy problem in third-party cross-account access scenarios. Option B is tempting because it "works," but long-lived shared keys cannot be centrally revoked or rotated safely and violate the no-long-term-credentials requirement.

### Question 3 [Domain: 1] [Type: Single-Answer]
**Scenario:** Company A wants to share an EBS snapshot, encrypted with a customer managed KMS key (CMK) in Company A's account, with Company B for a server migration. Company B needs to copy the snapshot into their own account and launch an EBS volume from it. Simply modifying the snapshot's permissions to add Company B's account ID as a user is not enough — Company B still gets `AccessDeniedException` when trying to copy the snapshot.
**Options:**
A. Modify the CMK's key policy to grant Company B's account (or a specific role) `kms:CreateGrant`, `kms:Decrypt`, and `kms:DescribeKey`, in addition to sharing the snapshot with Company B's account ID; Company B can then copy the snapshot and create a volume
B. Add a wildcard `Principal: "*"` to the CMK key policy so any account can decrypt the snapshot
C. Export the KMS key material using `GetParametersForImport` and import it into a new CMK in Company B's account
D. Simply sharing the snapshot is sufficient; KMS decrypt permissions are not required because encryption is transparent across accounts
**Correct answer(s):** A
**Explanation:** Cross-account sharing of a KMS-encrypted snapshot always requires updating the CMK's key policy to grant the target account decrypt/grant permissions, in addition to the EC2-level snapshot sharing — both layers must independently authorize the access. Option D is the common trap: engineers assume sharing the snapshot resource is enough, forgetting that the underlying CMK is a completely separate resource with its own access control.

### Question 4 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company uses AWS Secrets Manager to automatically rotate an RDS MySQL master password every 30 days via the built-in rotation Lambda function. The Lambda function runs inside private subnets with no NAT Gateway and no internet gateway, and every rotation attempt now fails with a timeout. The team wants to fix this while keeping monthly costs as low as possible and avoiding any path through the public internet.
**Options:**
A. Create a VPC interface endpoint for Secrets Manager (`secretsmanager`) in the private subnets, attach appropriate security groups, and enable private DNS so the rotation Lambda can reach the Secrets Manager API privately
B. Move the rotation Lambda function into a public subnet and assign it a public IP address
C. Increase the Lambda function's timeout to the 15-minute maximum
D. Disable automatic rotation and rotate the credentials manually every 30 days through the console
**Correct answer(s):** A
**Explanation:** A VPC interface endpoint (AWS PrivateLink) gives Lambda private, low-cost connectivity to the Secrets Manager API without a NAT Gateway or public internet exposure, directly resolving the timeout. Option C is tempting but useless here — the function isn't slow, it has no network path to the Secrets Manager endpoint at all, so it will simply time out again regardless of the limit.

### Question 5 [Domain: 1] [Type: Single-Answer]
**Scenario:** A two-tier application has web servers in subnet A and an RDS database in subnet B. The security groups are correctly configured: the web tier's SG allows outbound 3306 to the DB SG, and the DB SG allows inbound 3306 from the web tier SG. The network ACL on subnet B allows inbound TCP 3306 from subnet A's CIDR, but its outbound rules only permit TCP port 3306 to 0.0.0.0/0. Web servers report that MySQL connections hang and eventually time out.
**Options:**
A. Add an outbound rule on subnet B's NACL allowing TCP ports 1024–65535 to subnet A's CIDR, because NACLs are stateless and return traffic uses ephemeral source ports that must be explicitly permitted
B. Add an outbound rule on subnet B's NACL allowing TCP port 3306 to 0.0.0.0/0 a second time with a lower rule number
C. Remove the NACL from subnet B entirely and rely only on the security groups
D. Change the RDS security group to allow all outbound traffic to 0.0.0.0/0
**Correct answer(s):** A
**Explanation:** Because NACLs are stateless, return traffic from the database back to the client uses a random high ephemeral port, so the NACL's outbound rules must explicitly allow the ephemeral port range, not just the application port. Option D is a common but incorrect fix since the DB's outbound security group rule isn't the bottleneck — the stateless NACL is dropping the return packets before the security group is even consulted.

### Question 6 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A public-facing login API behind Amazon API Gateway is experiencing two distinct attack patterns: automated SQL injection attempts against the login form, and slow, distributed credential-stuffing traffic originating from a large pool of residential proxy IP addresses (so each individual IP sends very few requests). The security team wants to mitigate both threats using AWS WAF while minimizing false positives for legitimate users and avoiding excessive operational overhead.
**Options:**
A. Attach the AWS Managed Rules SQL Database rule group to block common SQL injection patterns
B. Add a rate-based rule limiting requests per 5-minute window per source IP
C. Attach the AWS WAF Bot Control managed rule group (or Account Takeover Prevention) to detect and block automated bot and credential-stuffing behavior across many low-volume IPs
D. Add a geographic match rule that blocks every country except the company's headquarters location
E. Add an IP set match rule that allow-lists only the corporate office's IP range
**Correct answer(s):** A, C
**Explanation:** The SQL Database managed rule group directly addresses the injection attempts, while Bot Control (or ATP) is purpose-built to fingerprint and block distributed, low-and-slow credential-stuffing traffic that a simple per-IP rate limit would miss. Option B is the most tempting distractor, but because each proxy IP stays under typical rate thresholds, a rate-based rule alone is largely ineffective against this specific distributed pattern.

### Question 7 [Domain: 1] [Type: Single-Answer]
**Scenario:** Amazon GuardDuty EKS Runtime Monitoring generates a `CryptoCurrency:Kubernetes/BitcoinTool.B` finding indicating that a container in a production EKS cluster is mining cryptocurrency. The security team wants the affected pod isolated automatically within seconds, without waiting for an analyst to review a dashboard, while still preserving evidence and notifying the on-call team.
**Options:**
A. Create an Amazon EventBridge rule matching that specific GuardDuty finding type, which invokes a Lambda function to automatically isolate the affected pod/node (e.g., apply a restrictive Kubernetes NetworkPolicy or cordon the node) and publish an SNS notification to the security team
B. Wait for the weekly GuardDuty summary email and manually terminate the pod once someone reviews it
C. Disable GuardDuty EKS Protection so the noisy alerts stop appearing
D. Configure AWS CloudTrail to automatically block the API call that originally created the pod
**Correct answer(s):** A
**Explanation:** EventBridge natively receives GuardDuty findings in near real time and can trigger automated Lambda-based remediation, which is the standard pattern for sub-minute containment without human intervention. Option C is a dangerous distractor — disabling the detection capability removes visibility into the ongoing compromise rather than remediating it.

### Question 8 [Domain: 1] [Type: Single-Answer]
**Scenario:** A mobile photo-sharing app needs users to sign up and sign in with email/password and enforce MFA, and it also needs to let each authenticated user upload photos directly to a shared S3 bucket, but only into an S3 prefix matching their own user ID, using short-lived credentials rather than embedding any static AWS keys in the app.
**Options:**
A. Use an Amazon Cognito User Pool for sign-up, sign-in, and MFA, then federate authenticated users into a Cognito Identity Pool that vends temporary IAM credentials, using policy variables (e.g., `${cognito-identity.amazonaws.com:sub}`) in the IAM role to scope each user to their own S3 prefix
B. Use only a Cognito Identity Pool, since it natively provides username/password sign-in and MFA on its own
C. Create an individual IAM user for every app user and embed each user's long-term access keys in the mobile app binary
D. Use the Cognito User Pool alone and call the S3 API directly using the User Pool's JWT ID token as SigV4 credentials
**Correct answer(s):** A
**Explanation:** User Pools handle authentication and MFA, while Identity Pools are the component that exchanges an authenticated identity for temporary, scoped IAM credentials — combining them is the standard CKAD/SAA pattern for this use case. Option B is a common misconception: Identity Pools only broker AWS credentials for already-authenticated identities and have no built-in user directory or password/MFA management.

### Question 9 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A large enterprise delegates IAM administration in each business-unit AWS account to local "delegated admins" who can create IAM roles for their own teams. Central security requires that no role created by a delegated admin can ever exceed a security baseline — no `iam:*` actions, no regions outside two approved regions, and no ability to disable CloudTrail — even if a delegated admin mistakenly attaches an overly broad policy like `AdministratorAccess` to a new role.
**Options:**
A. Set an IAM permissions boundary that the delegated admin must attach whenever calling `iam:CreateRole`, ensuring any role they create can never exceed the boundary's maximum permissions
B. Rely on delegated admins to manually review every policy they attach before publishing it
C. Apply a Service Control Policy (SCP) at the OU level in AWS Organizations that explicitly denies `iam:*` outside allowed actions, restricts allowed Regions, and denies `cloudtrail:StopLogging`/`cloudtrail:DeleteTrail`, regardless of any IAM policy inside the member account
D. Grant delegated admins `AdministratorAccess` but require them to use MFA when calling the API
E. Apply a resource-based policy on the CloudTrail trail that only affects the trail itself
**Correct answer(s):** A, C
**Explanation:** Permissions boundaries cap what a delegated admin can grant to the roles they create, while an OU-level SCP provides an organization-wide backstop that no IAM policy inside the account — including `AdministratorAccess` — can ever override; together they guarantee the baseline. Option D is the tempting-but-wrong choice because MFA only affects authentication strength, not the scope of what an `AdministratorAccess`-holding principal is authorized to do.

### Question 10 [Domain: 1] [Type: Single-Answer]
**Scenario:** A financial application encrypts sensitive records with a customer managed KMS key in `us-east-1` before writing them to DynamoDB, which is configured as a Global Table replicating to `us-west-2` for disaster recovery. During a simulated regional failover of `us-east-1`, the application in `us-west-2` must be able to decrypt the replicated ciphertext locally without making any cross-Region API call back to `us-east-1` (which may be unreachable during a real outage).
**Options:**
A. Create a KMS multi-Region key with a primary key in `us-east-1` and a replica key in `us-west-2` that share the same key material and key ID, allowing ciphertext encrypted in one Region to be decrypted using the replica key in the other Region with no cross-Region call
B. Use a single-Region CMK in `us-east-1` and configure the `us-west-2` application to call across Regions to decrypt during failover
C. Use `GetParametersForImport` to export the CMK's key material and manually import it into an identical CMK created independently in `us-west-2`
D. Switch to AWS-owned keys, which are automatically replicated to every Region by default
**Correct answer(s):** A
**Explanation:** KMS multi-Region keys are purpose-built for exactly this DR scenario — the replica key shares key material and key ID with the primary, so ciphertext can be decrypted in the replica Region without any dependency on the primary Region being available. Option B defeats the entire purpose of the failover design, since it reintroduces a hard dependency on the very Region that has failed.

### Question 11 [Domain: 1] [Type: Single-Answer]
**Scenario:** A cost-conscious startup needs to store roughly 500 static, non-sensitive configuration values (feature flags, service endpoints) and 10 database credentials that must rotate automatically every 30 days without any custom rotation code. The team wants to minimize monthly spend while still meeting the automatic-rotation requirement.
**Options:**
A. Store the 500 static configuration values in AWS Systems Manager Parameter Store (Standard tier, no additional charge), and store the 10 database credentials in AWS Secrets Manager to use its built-in automatic rotation
B. Store all 510 values in Secrets Manager for consistency, accepting the per-secret monthly charge on every value
C. Store all 510 values in Parameter Store and write a custom Lambda rotation function, since Parameter Store has no native RDS rotation integration
D. Store the database credentials as plaintext environment variables in the EC2 launch template for simplicity
**Correct answer(s):** A
**Explanation:** Parameter Store Standard is free and well-suited to static, non-rotating configuration, while Secrets Manager's native rotation integration with RDS is the most cost-effective way to satisfy the automatic-rotation requirement for only the credentials that truly need it. Option B is tempting for "consistency" but needlessly incurs per-secret charges on 500 values that never need Secrets Manager's rotation capability.

### Question 12 [Domain: 1] [Type: Single-Answer]
**Scenario:** Application servers in subnet A need to query an RDS instance in subnet B on port 3306. The network ACL attached to subnet B has an inbound rule allowing TCP 3306 from subnet A's CIDR, and its outbound rules allow only TCP port 3306 to subnet A's CIDR — no other outbound rule exists. Connections from the app servers consistently hang and time out even though the security groups on both sides are configured correctly.
**Options:**
A. Add an outbound rule on subnet B's NACL allowing TCP ports 1024–65535 to subnet A's CIDR, since NACLs are stateless and the database's response traffic will use a random high-numbered ephemeral port
B. Add an outbound rule allowing TCP port 3306 to 0.0.0.0/0 instead of subnet A's CIDR
C. Delete subnet B's NACL and use the VPC's default NACL instead
D. Add an inbound rule on subnet A's NACL allowing all traffic from subnet B
**Correct answer(s):** A
**Explanation:** Because NACLs evaluate inbound and outbound traffic independently with no connection state, the ephemeral port range used by the database's replies must be explicitly permitted outbound, which is missing here. Option D looks plausible but is irrelevant — the failure is on the outbound side of subnet B's NACL, not the inbound side of subnet A's.

### Question 13 [Domain: 1] [Type: Multiple-Response]
**Scenario:** In an AWS Organization, the root OU has the default `FullAWSAccess` SCP. A "Security" OU has an additional SCP attached that denies `ec2:RunInstances` for any instance type outside the `t3` family and restricts operations to two approved Regions. A developer in a member account under the Security OU has an IAM policy directly attached granting `AdministratorAccess`.
**Options:**
A. SCPs never grant permissions by themselves — they only define the maximum available permissions for accounts in the OU, so the developer still needs an IAM Allow to actually perform any action
B. Because the developer has `AdministratorAccess` in IAM, they can launch any EC2 instance type in any Region, since IAM identity policies override SCPs
C. The developer can only launch `t3`-family instances in the two approved Regions, even with `AdministratorAccess`, because the SCP caps the maximum permissions available account-wide
D. SCPs apply only to the AWS account root user, not to IAM users or roles within the member account
E. If a role in a different OU without this SCP is assumed instead, the Region and instance-type restriction would no longer apply to this same account's resources
**Correct answer(s):** A, C
**Explanation:** SCPs act as a permissions guardrail on top of (not a replacement for) IAM policies, so the developer's `AdministratorAccess` is still capped by whatever the SCP allows, regardless of how permissive the identity policy is. Option B is the most tempting wrong answer because it inverts the actual evaluation order — SCPs always take precedence as the outer boundary, and IAM policies can never expand beyond what an SCP permits.

### Question 14 [Domain: 1] [Type: Single-Answer]
**Scenario:** A public API behind API Gateway is receiving a large volume of suspicious traffic almost entirely from one country, but a legitimate business partner's office is also located in that same country and must retain full access. The security team wants to block the bulk of the malicious country-based traffic while explicitly preserving access for the partner's known IP range, and also wants protection against future volumetric spikes from anywhere.
**Options:**
A. Create an AWS WAF rule using a Geographic match statement combined with a NOT statement referencing an IP set of the partner's trusted IP range (so the partner is excluded from the geo-block), and add a rate-based rule as an additional layer against volumetric spikes
B. Add a plain geographic match rule blocking the entire country; AWS WAF automatically allow-lists known business IP ranges within any blocked country
C. Block the traffic at the Route 53 level using latency-based routing records
D. Disable API Gateway throttling entirely and rely solely on the origin server's own rate limiting
**Correct answer(s):** A
**Explanation:** Combining a geographic match with a NOT/IP-set exception lets you block a whole country while carving out a specific trusted range, and layering a rate-based rule adds protection against future volumetric attacks from any source. Option B is a fabrication — AWS WAF has no automatic mechanism that whitelists "business IP ranges," so a plain geo-block would also block the partner.

### Question 15 [Domain: 1] [Type: Single-Answer]
**Scenario:** A security team wants two independent protections without building custom scanning infrastructure: automatically scan EBS volumes attached to EC2 instances whenever GuardDuty raises a suspicious finding about that instance, and automatically scan every new object uploaded to a user-upload S3 bucket for malware before the application processes it.
**Options:**
A. Enable both GuardDuty Malware Protection for EC2 (automatically scans EBS volumes when a relevant finding occurs) and GuardDuty Malware Protection for S3 (scans newly uploaded objects and tags the results), avoiding any custom scanning infrastructure
B. Enable Amazon Inspector only, since it fully replaces GuardDuty Malware Protection for both EC2 and S3
C. Manually install ClamAV on every EC2 instance and Lambda function, since GuardDuty cannot scan for malware at all
D. Enable GuardDuty S3 Protection (data event monitoring) alone, since it inherently scans object contents for malware
**Correct answer(s):** A
**Explanation:** GuardDuty Malware Protection for EC2 and Malware Protection for S3 are two distinct, purpose-built features that satisfy each requirement respectively without any custom scanning code. Option D is a common confusion — S3 Protection (data event monitoring for suspicious API activity) is a separate capability from Malware Protection for S3, which is the one that actually inspects object contents.

### Question 16 [Domain: 1] [Type: Single-Answer]
**Scenario:** A financial services mobile app must satisfy a compliance requirement to challenge users with additional MFA verification only when Amazon Cognito detects an anomalous sign-in, such as a new device or an unfamiliar location, while allowing frictionless sign-in for recognized devices to avoid degrading the user experience.
**Options:**
A. Enable Amazon Cognito User Pool advanced security features (adaptive authentication / threat protection), which evaluates sign-in risk and automatically prompts for additional MFA only when risk indicators (new device, unfamiliar IP, etc.) are detected
B. Set the User Pool's MFA setting to "Required" so every sign-in, regardless of risk, always triggers an MFA challenge
C. Disable MFA entirely and rely only on a strong password policy to meet the compliance requirement
D. Implement a custom Lambda pre-authentication trigger that unconditionally denies sign-in from any IP address not seen before
**Correct answer(s):** A
**Explanation:** Cognito's adaptive authentication feature is specifically designed to apply risk-based, step-up MFA challenges only when anomalies are detected, satisfying both the compliance requirement and the low-friction UX goal. Option B is the tempting simple fix, but it fails the "frictionless for recognized devices" requirement by forcing MFA on every single sign-in.

### Question 17 [Domain: 1] [Type: Single-Answer]
**Scenario:** Company A (Account 111122223333) hosts an S3 bucket encrypted with SSE-KMS using a customer managed key that also lives in Account 111122223333. Company B (Account 444455556666) has a nightly batch job that assumes a specific IAM role to read certain objects from that bucket. Access must never rely on long-term credentials, must be independently auditable, and must be revocable without affecting any other cross-account relationships Company A has.
**Options:**
A. Add Company B's specific IAM role ARN to the S3 bucket policy allowing `s3:GetObject`, add that same role ARN to the CMK's key policy allowing `kms:Decrypt`, and attach an IAM policy in Account 444455556666 to that role permitting `s3:GetObject` on the bucket/objects and `kms:Decrypt` on the CMK's ARN — all three must align
B. Adding the role to the S3 bucket policy alone is sufficient, since KMS automatically trusts any principal already permitted by the bucket policy
C. Set the CMK's key policy to allow `Principal: "*"` for `kms:Decrypt` to simplify the setup, relying on the bucket policy to restrict access by account
D. Share the CMK's raw key material with Account 444455556666 so they can create an identical key locally for decryption
**Correct answer(s):** A
**Explanation:** Because the bucket policy, the CMK key policy, and the requesting account's own IAM policy are all independently evaluated, cross-account decrypt access to an SSE-KMS object requires all three pieces to explicitly authorize the same principal — missing any one results in `AccessDenied`. Option B is the classic trap: many engineers forget that KMS key policies are a completely separate authorization boundary from S3 bucket policies.

### Question 18 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A 40-account AWS Organization wants to give its workforce centralized access to multiple AWS accounts using their existing on-premises Active Directory credentials, avoid creating individual IAM users per employee, map job roles to scoped permission sets across accounts, and periodically confirm that no former employees or role changes have left stale over-privileged access in place.
**Options:**
A. Enable AWS IAM Identity Center, connect it to the on-premises Active Directory via AWS Directory Service AD Connector, and define permission sets assigned to AD groups that map to job roles for each target account
B. Create an IAM user in the Organizations management account for every employee and distribute credentials via a shared spreadsheet
C. Periodically review and audit IAM Identity Center permission set assignments, removing stale assignments for offboarded employees or employees who changed roles
D. Grant every employee the `AdministratorAccess` permission set in every account to eliminate access-denied support tickets
E. Store each employee's AWS credentials as a custom attribute in on-premises Active Directory for retrieval by scripts
**Correct answer(s):** A, C
**Explanation:** IAM Identity Center with AD Connector is the AWS-recommended pattern for federating an existing on-prem directory into multi-account, role-based temporary access, and periodic access reviews are essential to prevent privilege creep and stale access. Option D is the tempting shortcut that eliminates support tickets but directly violates least-privilege and would fail any compliance audit.

### Question 19 [Domain: 1] [Type: Single-Answer]
**Scenario:** A regulated healthcare company runs Lambda functions in private subnets with no NAT Gateway and no internet gateway. These functions must call Secrets Manager, KMS, and CloudWatch Logs APIs, and compliance mandates that this traffic must never traverse the public internet under any circumstances, while keeping monthly infrastructure cost as low as possible.
**Options:**
A. Create VPC interface endpoints (AWS PrivateLink) for Secrets Manager, KMS, and CloudWatch Logs within the VPC's private subnets, enable private DNS, and allow inbound HTTPS (443) from the Lambda functions' security group on each endpoint's security group
B. Add a NAT Gateway in every Availability Zone so the Lambda functions can reach these services over their public endpoints
C. Move the Lambda functions into a public subnet and assign each an Elastic IP so they can reach the AWS service public endpoints directly
D. Use a single Gateway endpoint that covers Secrets Manager, KMS, and CloudWatch Logs, since all AWS services support Gateway endpoints
**Correct answer(s):** A
**Explanation:** Interface endpoints (PrivateLink) keep traffic to Secrets Manager, KMS, and CloudWatch Logs entirely within the AWS network and are the correct compliance-safe, cost-effective solution — cheaper than a multi-AZ NAT Gateway and fully private. Option D is factually wrong: Gateway endpoints only exist for S3 and DynamoDB, so Secrets Manager, KMS, and CloudWatch Logs require interface endpoints instead.

### Question 20 [Domain: 1] [Type: Single-Answer]
**Scenario:** A regulated financial company must retain sole, exclusive control of the cryptographic key material used to sign transactions, meeting an audit requirement for a FIPS 140-2 Level 3 validated, single-tenant hardware security boundary that AWS itself cannot access. The same company also needs to issue internal TLS certificates for microservices that must chain up to its existing on-premises root certificate authority, which internal clients already trust.
**Options:**
A. Provision AWS CloudHSM and configure it as a KMS custom key store so the company retains sole control of key material within a single-tenant, FIPS 140-2 Level 3 validated HSM, and configure AWS Certificate Manager Private CA as a subordinate CA chained to the on-premises root CA to issue trusted internal certificates
B. Use standard AWS KMS customer managed keys, which are already validated at FIPS 140-2 Level 3 and give the customer exclusive control of the underlying key material
C. Use the public AWS Certificate Manager service to issue all internal microservice certificates instead of building a private CA hierarchy
D. Store the transaction-signing keys as Secrets Manager secrets to achieve hardware-backed isolation equivalent to an HSM
**Correct answer(s):** A
**Explanation:** CloudHSM provides single-tenant, FIPS 140-2 Level 3 validated hardware where the customer holds exclusive control of key material (unlike shared KMS HSMs), and AWS Private CA supports being configured as a subordinate CA under an existing on-prem root, satisfying both requirements. Option B is the key trap: default AWS KMS backing HSMs are validated at FIPS 140-2 Level 2 overall (Level 3 for certain security features only), not the full Level 3 boundary the audit requires, and AWS — not the customer — controls the underlying key material.

### Question 21 [Domain: 2] [Type: Single-Answer]
**Scenario:** A retail company runs three microservices (catalog, cart, checkout) behind a single Application Load Balancer spanning 3 AZs, using host-based and path-based routing to keep costs down versus deploying separate load balancers per team. The security team now requires OWASP Top 10 protection plus independent rate limiting per URI path (e.g., `/checkout` needs stricter limits than `/catalog`), and compliance logging requires the true client IP to be preserved end-to-end. The architecture team wants a solution that adds no new load balancers.
**Options:**
A. Deploy a separate Network Load Balancer for each microservice and attach AWS Shield Advanced to each.
B. Attach an AWS WAF Web ACL with rate-based rule statements scoped to each URI path to the existing ALB, relying on the ALB-inserted X-Forwarded-For header for client IP logging.
C. Enable AWS Shield Advanced only, since ALB does not support WAF integration for per-path rate limiting.
D. Replace the ALB with an Amazon API Gateway HTTP API for all three microservices to get native WAF support at lower cost.
**Correct answer(s):** B
**Explanation:** ALB natively integrates with AWS WAF, and rate-based rule statements can use a scope-down statement to target specific URI paths within a single Web ACL, while ALB (a Layer 7 proxy) automatically inserts X-Forwarded-For for client IP visibility — meeting all constraints with zero new load balancers. Option C is factually wrong (WAF-on-ALB path scoping is a core, well-documented feature), and A/D introduce unnecessary new infrastructure and cost — D is additionally flawed because AWS WAF integrates with API Gateway REST APIs, not HTTP APIs, so it would not even deliver the "native WAF support" it claims.

### Question 22 [Domain: 2] [Type: Single-Answer]
**Scenario:** A financial services company is integrating with a banking partner that requires all traffic to originate from a small set of allow-listed static IP addresses. The integration also mandates end-to-end TLS encryption terminated only at the backend instances (PCI compliance forbids decryption at any intermediary), and the platform must sustain millions of requests per second at sub-millisecond added latency across 3 AZs.
**Options:**
A. Application Load Balancer with AWS Global Accelerator providing static IPs, terminating TLS at the ALB.
B. Network Load Balancer with an Elastic IP address assigned per AZ, using a TCP listener so TLS traffic passes through untouched to the backend targets.
C. Classic Load Balancer with a static Elastic IP and TLS termination at the load balancer.
D. Network Load Balancer terminating TLS at the load balancer with an ACM certificate, then re-encrypting to targets using self-signed certificates.
**Correct answer(s):** B
**Explanation:** NLB supports assigning a static Elastic IP per AZ and, using a TCP (not TLS) listener, passes encrypted traffic through untouched — satisfying both the static-IP allow-listing requirement and the strict end-to-end encryption mandate at massive scale/low latency. A and D terminate TLS at the load balancer, breaking the "encryption only at instances" compliance requirement, and CLB does not support direct EIP assignment.

### Question 23 [Domain: 2] [Type: Single-Answer]
**Scenario:** An enterprise security team wants to insert a fleet of third-party IDS/IPS virtual appliances inline for all traffic across dozens of spoke VPCs connected via AWS Transit Gateway, without modifying route tables per application team as new VPCs are onboarded. The appliance fleet must scale horizontally behind a single logical inspection point, and the solution must support the appliances' native flow-encapsulation protocol.
**Options:**
A. Deploy an internal Network Load Balancer in each VPC forwarding to the firewall EC2 instances using manually configured UDP GENEVE encapsulation.
B. Deploy Gateway Load Balancer endpoints (GWLBe) in each spoke VPC, routing traffic through them to a centralized Gateway Load Balancer fronting the firewall appliance fleet, using the GENEVE protocol.
C. Deploy AWS Network Firewall instead, since Gateway Load Balancer cannot integrate with third-party firewall appliances.
D. Place an Application Load Balancer in front of the firewall fleet and expose it to spoke VPCs via AWS PrivateLink.
**Correct answer(s):** B
**Explanation:** Gateway Load Balancer combined with GWLB endpoints is the purpose-built AWS pattern for centralized, transparent, horizontally-scalable inline inspection of third-party appliances using GENEVE, requiring no per-app route table changes beyond the endpoint route. C is false — the AWS Marketplace Partner ecosystem (Palo Alto, Fortinet, etc.) is built specifically on GWLB; A recreates GWLB's plumbing manually without its scaling/health-check/flow-symmetry guarantees.

### Question 24 [Domain: 2] [Type: Single-Answer]
**Scenario:** A team is rolling out API v2 gradually, sending 95% of traffic to v1 and 5% to v2 using Route 53 weighted routing. They want the system to automatically shift 100% of traffic back to v1, without any manual intervention, if the v2 fleet becomes unhealthy — while still allowing them to manually adjust the weighted split during normal operation.
**Options:**
A. Create two weighted records (weight 95 for v1, weight 5 for v2), each associated with its own Route 53 health check; unhealthy weighted records are automatically excluded from DNS responses.
B. Create a single failover routing policy record set with v2 as primary and v1 as secondary.
C. Use latency-based routing records for v1 and v2, and manually trigger Route 53 Application Recovery Controller if v2 fails.
D. Use a multivalue answer routing policy returning both v1 and v2 IPs, encoding the intended weight split in a TXT record.
**Correct answer(s):** A
**Explanation:** Weighted routing supports per-record health checks; when a weighted record's health check fails, Route 53 stops returning it, automatically shifting 100% of traffic to the remaining healthy record while preserving the ability to manually tune weights. Failover routing (B) is all-or-nothing and defeats the intended gradual canary split, and multivalue answer (D) has no concept of weighting.

### Question 25 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A global media company is choosing Route 53 routing policies for a new interactive service used in the US, EU, and APAC. Two hard requirements exist: (1) all traffic originating in the EU must be served exclusively from the EU endpoint regardless of latency, due to data-residency law, and (2) the team separately wants the ability to intentionally shift a small, adjustable percentage of overall traffic toward a newly launched APAC region to load-test its capacity, independent of where clients are physically located.
**Options:**
A. Latency-based routing alone can guarantee that EU-origin traffic is only ever served from the EU endpoint, satisfying the compliance requirement.
B. Geolocation routing can be configured to strictly map all EU-based users to the EU endpoint regardless of measured latency, satisfying the data-residency requirement.
C. Geoproximity routing (via Route 53 traffic flow) can apply a bias value to a region's records to gradually shift a percentage of traffic between regions, independent of the client's location.
D. Weighted routing must be used to satisfy data residency, since it is the only policy that allocates traffic by continent.
E. Multivalue answer routing guarantees compliance because it returns multiple healthy IP addresses, letting the client select the nearest one.
**Correct answer(s):** B, C
**Explanation:** Geolocation strictly maps client geography to a fixed endpoint, which is what data-residency compliance actually requires (latency-based, A, could route an EU user to a non-EU region if it's "faster," failing compliance). Geoproximity's bias setting is specifically designed to shift traffic volume between regions independent of geography, matching the APAC capacity-test requirement. D and E misrepresent weighted and multivalue policies, neither of which is geography-aware.

### Question 26 [Domain: 2] [Type: Single-Answer]
**Scenario:** An order-validation Lambda function consumes from a standard SQS queue. A small number of malformed messages ("poison pills") repeatedly fail processing and get returned to the queue after each visibility timeout expires, consuming Lambda invocations and slowing overall throughput — even though the vast majority of messages have no ordering dependency on each other. The team needs failed messages isolated after a fixed number of retries, without losing them, and without impacting throughput of healthy messages.
**Options:**
A. Reduce the queue's visibility timeout to 0 seconds so failed messages become immediately available for reprocessing by another invocation.
B. Configure a redrive policy with `maxReceiveCount=3` pointing to a dead-letter queue, with a DLQ retention period long enough to support later investigation.
C. Migrate to a FIFO queue using a single message group ID for all orders to serialize processing and prevent poison pills from blocking other messages.
D. Manually delete messages from the console whenever Lambda logs an error, to unblock the queue.
**Correct answer(s):** B
**Explanation:** A redrive policy with a maxReceiveCount automatically isolates messages that repeatedly fail into a DLQ after N attempts, preserving them for investigation while healthy messages continue processing unaffected (standard queues already process messages in parallel). Option C would make things worse — a single message group ID in FIFO serializes processing of all orders, meaning a poison pill would now block every subsequent message, not fewer.

### Question 27 [Domain: 2] [Type: Single-Answer]
**Scenario:** An e-commerce platform needs a single "order placed" event to trigger three independent downstream actions: update inventory via an SQS-backed service, send a confirmation email via a Lambda function, and stream the event into an analytics data lake via Kinesis Data Firehose. Each consumer must scale, retry, and fail independently of the others, and the team wants to avoid writing custom fan-out or retry logic in the order service itself.
**Options:**
A. Publish the event directly and synchronously to three separate SQS queues from the order service.
B. Publish the event once to an SNS topic with three subscriptions: an SQS queue, a Lambda function, and a Kinesis Data Firehose delivery stream.
C. Use a single SQS queue with three separate consumer applications long-polling it, each processing every message.
D. Use EventBridge Pipes to connect the order service directly to each of the three targets with no intermediary.
**Correct answer(s):** B
**Explanation:** SNS's fan-out pattern delivers one published message to multiple independent, differently-typed subscribers (SQS, Lambda, and native Firehose subscriptions are all supported), giving each consumer its own retry/scaling behavior with no custom code in the publisher. Option C is wrong because a single SQS message is delivered to and consumed by only one consumer, not replicated to all three; A pushes fan-out complexity and coupling back into the order service.

### Question 28 [Domain: 2] [Type: Single-Answer]
**Scenario:** A large enterprise with ~50 AWS accounts under AWS Organizations wants to centralize GuardDuty and CloudTrail-derived security events from every member account into one security account, where automated remediation Lambda functions run. Member accounts must not be granted any direct IAM access to the remediation resources in the security account, and the design should use AWS-native event routing rather than custom polling.
**Options:**
A. Configure a custom EventBridge event bus in each member account and replicate events to the security account via S3 cross-account replication, which the security account polls.
B. Create a central custom event bus in the security account with a resource-based policy granting each member account `PutEvents` permission, and configure rules in each member account that forward relevant events to that central bus ARN.
C. Configure cross-account SNS subscriptions from each member account's topic directly to a single Lambda function in the security account.
D. Enable AWS Control Tower only; it aggregates all account events automatically with no EventBridge configuration required.
**Correct answer(s):** B
**Explanation:** The documented cross-account event aggregation pattern is a central custom bus with a resource policy allowing `PutEvents` from member accounts, paired with per-account rules forwarding matching events (e.g., GuardDuty findings, which are emitted to EventBridge natively) to that bus — with no cross-account IAM roles needed. A introduces unnecessary polling latency and complexity, and D is false; Control Tower does not eliminate the need to configure event aggregation. C is not a defensible alternative either: GuardDuty's native event delivery is via EventBridge, not SNS, so this option would first require standing up a custom EventBridge-to-SNS bridge in every account just to reach the same starting point as B, while also creating a single-Lambda fan-in bottleneck across 50 accounts — more custom plumbing for no benefit.

### Question 29 [Domain: 2] [Type: Single-Answer]
**Scenario:** An IoT platform ingests telemetry that spikes unpredictably from near-zero to 500,000 records/second several times per day. Three independent applications must each read the entire stream at their own pace: a fraud-detection service requiring sub-second, dedicated-throughput delivery, a real-time dashboard, and an archival job writing to S3. The team wants to avoid manually managing shard counts as throughput fluctuates.
**Options:**
A. Kinesis Data Streams in Provisioned mode with a fixed 500 shards, with all three applications using standard `GetRecords` polling.
B. Kinesis Data Streams in On-Demand mode, with the fraud-detection application configured as an Enhanced Fan-Out (EFO) consumer and the other two using standard shared-throughput consumers.
C. Amazon SQS standard queue with three separate polling groups, one per application.
D. Amazon Kinesis Data Firehose with three separate delivery streams, one per application, each buffering for 60 seconds.
**Correct answer(s):** B
**Explanation:** On-Demand mode automatically scales shard capacity for unpredictable spiky throughput with no manual shard management, and Enhanced Fan-Out gives the latency-sensitive fraud consumer a dedicated 2 MB/s-per-shard pipe with ~70 ms latency, while the other two consumers share standard throughput at lower cost. SQS does not support multiple independent consumers each reading the full ordered stream, and Firehose's buffering model is unsuitable for sub-second custom stream processing.

### Question 30 [Domain: 2] [Type: Multiple-Response]
**Scenario:** An architecture team is debating messaging services for an order pipeline. Requirements: (1) content-based filtering so only "high-value order" events are delivered to a fraud-review Lambda, while every event still flows to a data lake via Firehose; (2) strict per-customer message ordering for a separate payment-settlement process; (3) the ability to replay historical events going back multiple years for debugging, using a configured retention/archive setting rather than relying on any default behavior. Select the two accurate statements.
**Options:**
A. Amazon SNS supports message filtering policies so that only messages matching a specific attribute (e.g., `orderValue > threshold`) are delivered to a given subscriber, while other subscribers still receive every message.
B. Amazon SQS FIFO queues, using a `MessageGroupId` set to the customer ID, satisfy the strict per-customer ordering requirement for payment settlement.
C. Amazon EventBridge only supports a fixed 24-hour replay window with no way to extend it, so Kinesis Data Streams with 365-day retention must be used instead for multi-year replay.
D. Amazon SNS FIFO topics do not support message filtering, so all filtering logic must be implemented inside each Lambda subscriber.
E. Amazon EventBridge stores all events on its event bus indefinitely by default, requiring no additional configuration to support multi-year replay.
**Correct answer(s):** A, B
**Explanation:** SNS filter policies genuinely allow subscriber-specific delivery based on message attributes (A), and SQS FIFO's `MessageGroupId` guarantees strict ordering within each group, which per-customer settlement needs (B). C is wrong because EventBridge archives can be configured with retention up to indefinite (not fixed at 24 hours), and E is wrong because EventBridge does not retain events indefinitely by default — a configured archive is required, contradicting "no additional configuration." (D is also false — SNS message filtering is supported on both standard and FIFO topics — but is not one of the two selected statements.)

### Question 31 [Domain: 2] [Type: Single-Answer]
**Scenario:** A SaaS analytics platform sees a highly predictable traffic surge every weekday at 9:00 AM when EU customers log in. New EC2 instances take about 12 minutes to bootstrap (install agents, warm local caches) before they can serve traffic. Despite a target-tracking policy reacting quickly to rising CPU, users experience elevated latency for the first 10–12 minutes after 9:00 AM every day. The team wants to eliminate this recurring lag without permanently over-provisioning capacity 24/7.
**Options:**
A. Permanently raise the Auto Scaling group's minimum capacity to match the 9:00 AM peak.
B. Configure Predictive Scaling in forecast-and-scale mode to proactively launch capacity ahead of the known daily 9:00 AM pattern, combined with a Warm Pool so new instances are pre-initialized and ready to enter service instantly.
C. Rely solely on a target-tracking policy based on ALB `RequestCountPerTarget` with a shorter cooldown period to react faster.
D. Switch exclusively to EC2 Spot Instances to reduce cost enough to justify running at peak capacity around the clock.
**Correct answer(s):** B
**Explanation:** Predictive scaling learns recurring daily/weekly load patterns and scales ahead of time, while a warm pool keeps pre-bootstrapped instances in a stopped/ready state so they enter service almost instantly when needed — eliminating the 12-minute lag at a fraction of the cost of running peak capacity continuously. C is still purely reactive (it only scales after the spike starts, so it can't eliminate a bootstrap-time lag), and A/D both keep unnecessary capacity running full-time.

### Question 32 [Domain: 2] [Type: Single-Answer]
**Scenario:** A budget-constrained company runs a monolithic order-management system on EC2 and RDS in a single region. Leadership accepts an RTO of roughly 30–60 minutes and an RPO of about 15 minutes for a full regional outage, but insists that standby infrastructure cost during normal operations be minimal, while the production database must be continuously replicated to the DR region.
**Options:**
A. Multi-Site active-active, running full-scale application stacks simultaneously in both regions behind Route 53 weighted routing.
B. Pilot Light: continuously replicate the database to the DR region (e.g., a cross-region read replica), keep minimal or no application servers running there, and use AMIs/Infrastructure-as-Code to rapidly launch the full application stack and promote the replica when disaster is declared.
C. Backup and Restore: copy nightly RDS snapshots and EC2 AMIs to the DR region, restoring the full environment from scratch only when a disaster is declared.
D. Warm Standby, with a scaled-down but continuously running application fleet in the DR region that auto-scales up during failover.
**Correct answer(s):** B
**Explanation:** Pilot Light matches the stated RPO (~15 min, via continuous DB replication) and RTO (~30–60 min, via rapid app-tier provisioning at failover time) while keeping idle costs minimal since only the database tier runs continuously. Backup and Restore (C) typically yields RTO/RPO measured in hours, too slow for the stated targets, while Warm Standby (D) costs more than the stated budget by keeping the app fleet running continuously.

### Question 33 [Domain: 2] [Type: Single-Answer]
**Scenario:** A healthcare SaaS company has a contractual SLA requiring RTO ≤ 5 minutes and RPO ≤ 1 minute for a full regional failure, but must keep costs meaningfully lower than a full active-active deployment. Brief reduced-capacity performance for the first few minutes after failover, while Auto Scaling ramps up, is acceptable.
**Options:**
A. Multi-Site active-active, running full production capacity continuously in both regions.
B. Pilot Light, with only a database replica running continuously and application servers launched from an AMI at failure time.
C. Warm Standby: run a scaled-down (e.g., 10–20% capacity) but fully functional copy of the production stack continuously in the DR region with continuous data replication (e.g., Aurora Global Database or DynamoDB Global Tables), paired with Route 53 health-check-based failover and Auto Scaling to expand capacity within minutes.
D. Backup and Restore, using cross-region AWS Backup copy jobs scheduled hourly.
**Correct answer(s):** C
**Explanation:** Warm Standby keeps a functioning (if scaled-down) stack live at all times, so failover only requires a DNS/health-check switch plus a scale-up — achievable within minutes, meeting the 5-minute RTO and near-continuous replication meeting the 1-minute RPO. Pilot Light (B) would typically miss the 5-minute RTO because the application tier must be built from scratch at failure time, and Backup and Restore (D) has an RTO measured in hours.

### Question 34 [Domain: 2] [Type: Single-Answer]
**Scenario:** A global fintech trading platform's trade-matching engine requires near-zero RTO and RPO for a full regional failure — essentially no acceptable downtime or data loss — and the business is willing to accept the highest infrastructure cost to achieve it. Both regions must actively serve live production traffic under normal conditions, with automatic traffic shifting away from a failed region within seconds.
**Options:**
A. Warm Standby, with a 50%-capacity replica in the second region that scales to 100% upon failover.
B. Multi-Site (active-active): both regions run at full production capacity simultaneously, using a globally distributed multi-region write-capable database (e.g., DynamoDB Global Tables) and Route 53 health-check-based failover routing (or Application Recovery Controller) to shift traffic within seconds.
C. Pilot Light with automated CloudFormation stacks that fully deploy the application in under 10 minutes upon failure.
D. Backup and Restore combined with cross-region snapshots taken every 5 minutes.
**Correct answer(s):** B
**Explanation:** Only Multi-Site active-active, paired with a multi-writer global database and second-scale DNS/health-check failover, achieves near-zero RTO and RPO, because both regions are already serving live, up-to-date traffic. All other options introduce a data-lag or provisioning/scale-up delay (minutes to hours) that is incompatible with "near-zero."

### Question 35 [Domain: 2] [Type: Single-Answer]
**Scenario:** An internal nightly batch-reporting system is not customer-facing and reruns from source data every night. The business accepts an RTO and RPO of up to 24 hours for a disaster and wants DR readiness to cost close to nothing during normal operations.
**Options:**
A. Warm Standby, continuously running a scaled-down fleet in the DR region.
B. Pilot Light, with a continuously replicated database running in the DR region.
C. Backup and Restore: use AWS Backup to copy daily snapshots (EC2 AMIs, RDS/EBS snapshots) cross-region, provisioning and restoring resources from these backups only if a disaster is declared.
D. Multi-Site active-active across two regions.
**Correct answer(s):** C
**Explanation:** Backup and Restore has the lowest ongoing infrastructure cost of the four classic DR strategies (paying only for backup storage between disasters) and comfortably meets the generous 24-hour RTO/RPO tolerance for a non-critical batch workload. The other three strategies all carry continuous compute costs that are unjustified given the stated requirements.

### Question 36 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A solutions architect is training junior engineers on the four classic AWS DR strategies — Backup and Restore, Pilot Light, Warm Standby, and Multi-Site active-active — with respect to their relative cost and recovery characteristics. Select the two statements below that are accurate.
**Options:**
A. Backup and Restore typically has the lowest ongoing infrastructure cost of the four strategies but the longest RTO, since resources must be provisioned and restored from backups only after a disaster is declared.
B. Pilot Light and Warm Standby both require zero pre-provisioned resources running in the DR region prior to failover; the only difference between them is which database engine is used.
C. Multi-Site active-active generally provides the lowest RTO/RPO among the four strategies, but at the highest steady-state cost, because full production capacity runs in more than one region simultaneously.
D. Warm Standby always has a longer RTO than Pilot Light, because it keeps only a database-tier replica running rather than application servers.
E. All four strategies require Amazon Route 53 as the DNS failover mechanism; none of them can be implemented without it.
**Correct answer(s):** A, C
**Explanation:** A and C correctly describe the standard cost-versus-recovery-speed spectrum across the four strategies, from cheapest/slowest (Backup and Restore) to most expensive/fastest (Multi-Site). B is wrong because Pilot Light keeps a database replica running continuously and Warm Standby keeps a full (scaled-down) stack running — neither has "zero" pre-provisioned resources; D reverses the actual relationship (Warm Standby recovers faster than Pilot Light, not slower); E is wrong since Route 53 is the common choice but not the only option (e.g., Global Accelerator or Application Recovery Controller can also drive failover).

### Question 37 [Domain: 2] [Type: Single-Answer]
**Scenario:** A retail checkout service runs on EC2 behind an ALB, backed by an RDS MySQL Multi-AZ database, spread across only 2 Availability Zones in one region, with an Auto Scaling group configured for min 2 / max 10. During an outage affecting one of the two AZs, checkout latency spiked severely for about 90 seconds, even though RDS Multi-AZ failover completed successfully and the ASG eventually launched replacement instances in the healthy AZ. Investigation shows: the ALB kept routing some traffic to now-unreachable targets until its default health check thresholds (2 failed checks × 30s interval) marked them unhealthy, and losing one of only two AZs instantly removed half the fleet's capacity headroom while new instances took time to launch and pass health checks. Any fix must minimize added cost and must not alter the existing RPO=0 guarantee from Multi-AZ RDS.
**Options:**
A. Migrate the database to a multi-region Aurora Global Database and adopt a Warm Standby DR strategy, since Multi-AZ alone cannot handle AZ failures.
B. Reduce the ALB's health check interval toward its 5-second minimum (the unhealthy threshold is already at its floor value of 2 and cannot be lowered further) to detect failed targets faster, and expand the Auto Scaling group to span a third Availability Zone with baseline capacity increased so the surviving AZs already carry enough headroom to absorb a full AZ's worth of traffic without waiting on new instance launches.
C. Replace the ALB with a Network Load Balancer to eliminate health-check-related latency entirely during AZ failures.
D. Set the Auto Scaling group's minimum capacity equal to its maximum capacity (10) at all times to guarantee headroom for any AZ failure.
**Correct answer(s):** B
**Explanation:** B directly targets both root causes at low incremental cost: shrinking the health check interval (ALB supports intervals as low as 5 seconds, versus the 30-second default already in use; note the unhealthy threshold count is already at its AWS-enforced minimum of 2 and cannot be reduced further) shrinks the window during which traffic is routed to dead targets, and a third AZ with adequate baseline headroom means surviving capacity absorbs the lost AZ's load immediately, with no change to the RDS Multi-AZ configuration or its RPO=0 guarantee. A is an expensive, unrelated over-correction for a single-AZ (not regional) event; C is wrong because NLB health checks run on a comparable fixed 10s/30s cadence and switching load balancer types doesn't address the capacity-headroom problem; D fixes headroom but runs max capacity permanently, violating the cost-minimization requirement.

### Question 38 [Domain: 3] [Type: Single-Answer]
**Scenario:** A media company runs a fleet of on-demand EC2 instances performing video transcoding, a CPU-bound batch workload that runs 24/7 at consistently high CPU utilization (>90%). They currently use m6i.4xlarge (general purpose) instances but are being throttled by CPU during peak batch windows even though memory utilization stays below 20%. They want to reduce cost per transcoded minute while maintaining current throughput, and are open to a different CPU architecture if it lowers cost without requiring application changes (the transcoding software is already compiled for both x86_64 and ARM64).
**Options:**
A. Switch to R6i memory-optimized instances to get more memory headroom
B. Switch to C7g compute-optimized Graviton instances
C. Switch to T3 unlimited burstable instances to allow CPU bursting
D. Enable EC2 Auto Scaling with the same m6i instance type to add more instances
**Correct answer(s):** B
**Explanation:** Compute-optimized C7g (Graviton3) instances deliver high sustained CPU performance per dollar, and since the software already supports ARM64, cost drops with zero rearchitecting. R6i adds unneeded memory when memory isn't the bottleneck (A wrong), and T3 Unlimited's surcharge model is designed for bursty workloads, not sustained 90%+ CPU (C is tempting but costly). D scales horizontally without improving per-instance cost/performance.

### Question 39 [Domain: 3] [Type: Single-Answer]
**Scenario:** A financial trading application on EC2 requires an EBS volume delivering consistent sub-millisecond latency, up to 256,000 IOPS, and 4,000 MB/s throughput, with 99.999% durability. It must attach to a Nitro-based instance. Performance is the primary requirement, though cost is a secondary consideration.
**Options:**
A. gp3 volume with provisioned IOPS up to 16,000
B. io2 Block Express volume
C. Instance store NVMe SSD
D. st1 throughput-optimized HDD
**Correct answer(s):** B
**Explanation:** io2 Block Express is the only EBS option supporting up to 256,000 IOPS, 4,000 MB/s, sub-millisecond latency, and 99.999% durability. gp3 tops out at 16,000 IOPS/1,000 MB/s. Instance store offers comparable raw speed but is ephemeral and fails the durability requirement (tempting but wrong), and st1 is optimized for throughput, not high IOPS/low latency.

### Question 40 [Domain: 3] [Type: Single-Answer]
**Scenario:** A genomics research firm runs a highly parallel workload with 5,000 EC2 instances/containers concurrently reading and writing small files to a shared EFS file system. Aggregate throughput matters more than any single client's latency, and the workload must scale beyond 500,000 IOPS with unpredictable, spiky demand.
**Options:**
A. General Purpose performance mode with Bursting throughput
B. Max I/O performance mode with Elastic throughput
C. General Purpose performance mode with Provisioned throughput
D. Max I/O performance mode with Bursting throughput
**Correct answer(s):** B
**Explanation:** Max I/O mode is built for highly parallel access from thousands of clients, scaling aggregate IOPS/throughput far beyond General Purpose mode's ceiling; Elastic throughput automatically scales to match unpredictable, spiky aggregate demand without capacity planning. General Purpose (A, C) throttles operations/sec at this scale despite better per-file latency. Bursting throughput (D) depends on file-system-size-based credits and can't sustain 500K+ IOPS.

### Question 41 [Domain: 3] [Type: Multiple-Response]
**Scenario:** An e-commerce platform wants an in-memory caching layer in front of DynamoDB for a session store and a leaderboard feature. Requirements: automatic Multi-AZ failover for HA, the ability to shard data across multiple nodes for horizontal scale, and native support for complex data structures like sorted sets for ranking the leaderboard. (Select TWO.)
**Options:**
A. Use ElastiCache for Memcached
B. Use ElastiCache for Redis (cluster mode enabled) with Multi-AZ
C. Use DAX in front of DynamoDB instead
D. Use Redis sorted sets (ZADD/ZRANGE) for the leaderboard
E. Use Memcached's built-in list data type for leaderboard ranking
**Correct answer(s):** B, D
**Explanation:** Redis cluster mode enabled provides both sharding and Multi-AZ automatic failover, and Redis natively implements sorted sets—purpose-built for leaderboards. Memcached (A, E) has no persistence, no automatic failover, and no rich data types (it has no "list" type at all), and DAX (C) only accelerates DynamoDB's own API calls—it has no generic sorted-set ranking capability.

### Question 42 [Domain: 3] [Type: Single-Answer]
**Scenario:** An ad-tech company uses DynamoDB for a bidding system requiring microsecond read latency on eventually-consistent GetItem calls, with occasional strongly consistent reads needed for a finance reconciliation job. They want a caching layer that requires no rewrite of query logic beyond swapping the client endpoint.
**Options:**
A. ElastiCache for Redis as a lazy-loading cache in front of DynamoDB
B. DynamoDB Accelerator (DAX)
C. DAX cannot be used because strongly consistent reads are required for reconciliation
D. CloudFront with DynamoDB as the origin
**Correct answer(s):** B
**Explanation:** DAX is API-compatible with DynamoDB, requiring only an endpoint change, and delivers microsecond latency for eventually consistent reads while transparently passing strongly consistent read requests through to the underlying table. C is a tempting distractor—DAX doesn't cache strongly consistent reads, but it still supports them via passthrough, so it isn't disqualified. Redis (A) would require rewriting the data-access layer, and CloudFront (D) doesn't front databases.

### Question 43 [Domain: 3] [Type: Single-Answer]
**Scenario:** A global media streaming company serves video segments from an S3 origin via CloudFront to millions of users worldwide. During flash-crowd events for live sports, S3 origin request rates spike dramatically and throttle, even with CloudFront caching, because many edge locations independently experience a cache miss for the same newly-published segment at nearly the same instant.
**Options:**
A. Increase the CloudFront cache TTL only
B. Enable CloudFront Origin Shield
C. Switch the origin from S3 to an EC2-hosted origin with Auto Scaling
D. Manually add more CloudFront edge locations via a custom domain
**Correct answer(s):** B
**Explanation:** Origin Shield adds a consolidated regional caching layer between edge locations and the origin, deduplicating simultaneous first-time cache misses before they reach S3—directly solving this "thundering herd" pattern. Raising TTL (A) doesn't help with the very first, simultaneous misses of newly published content. Switching origins (C) adds cost and complexity without solving the fan-in problem, and edge locations (D) aren't something you provision manually.

### Question 44 [Domain: 3] [Type: Single-Answer]
**Scenario:** A gaming company runs UDP-based multiplayer game servers behind NLBs in two regions (us-east-1, eu-west-1). They need fast, health-check-driven regional failover (seconds, not minutes), consistent low-latency routing to the nearest healthy endpoint via static anycast IPs (required for corporate firewall allowlisting), and the traffic is not HTTP-cacheable.
**Options:**
A. Amazon CloudFront with two origins and origin failover
B. AWS Global Accelerator with endpoint groups in both regions
C. Route 53 latency-based routing with health checks
D. Application Load Balancer cross-zone load balancing
**Correct answer(s):** B
**Explanation:** Global Accelerator provides static anycast IPs for firewall allowlisting, supports non-HTTP/UDP traffic via NLB, and performs fast automated health-check failover at the network layer (seconds). CloudFront (A) is HTTP/HTTPS-only and can't carry UDP game traffic. Route 53 (C) is tempting since it also fails over, but DNS-based failover is slower due to client/resolver TTL caching and provides no static IP. D is single-region only.

### Question 45 [Domain: 3] [Type: Single-Answer]
**Scenario:** A serverless application uses Lambda functions to query an RDS for MySQL database. Under bursty traffic, Lambda concurrency spikes to thousands of concurrent executions, each opening a new database connection and exhausting max_connections, causing failures. The team cannot migrate to Aurora Serverless due to a licensing requirement to remain on RDS MySQL Multi-AZ.
**Options:**
A. Increase the RDS instance size to raise max_connections
B. Use RDS Proxy in front of the RDS MySQL instance
C. Set Lambda reserved concurrency to 1 to serialize database access
D. Use DAX in front of RDS MySQL
**Correct answer(s):** B
**Explanation:** RDS Proxy pools and multiplexes connections, letting thousands of Lambda invocations share a much smaller pool of real database connections—directly solving connection exhaustion without changing database engine. Increasing instance size (A) only raises the ceiling temporarily and is costly, not a structural fix. Reserved concurrency of 1 (C) fixes connections but destroys throughput. DAX (D) only works with DynamoDB, not RDS.

### Question 46 [Domain: 3] [Type: Single-Answer]
**Scenario:** A SaaS company's primary Aurora MySQL cluster in us-east-1 serves read/write traffic. Expanding to APAC, they need read latency under 20ms for dashboard queries from Singapore-based users, plus disaster recovery with an RPO under 1 second and RTO under 1 minute if us-east-1 fails entirely.
**Options:**
A. Create a cross-region Aurora Read Replica in ap-southeast-1
B. Use Aurora Global Database with a secondary cluster in ap-southeast-1
C. Use DynamoDB Global Tables instead
D. Use RDS for MySQL with a cross-region read replica and manual promotion
**Correct answer(s):** B
**Explanation:** Aurora Global Database replicates across regions with typically sub-second lag via dedicated storage-level replication, serves low-latency local reads in the secondary region, and supports managed failover in under a minute. A standard cross-region Read Replica (A) has higher, less predictable lag and requires manual/scripted promotion, failing the RTO. DynamoDB Global Tables (C) would require abandoning relational MySQL entirely, and D has even slower failover than A.

### Question 47 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A media company needs to upload large (multi-GB to multi-TB) video master files from an on-premises studio in Sydney to an S3 bucket in ap-southeast-2, and separately needs end users worldwide to download large files from that bucket as fast as possible. Select TWO techniques that directly improve throughput for these use cases.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket for uploads
B. Use the S3 Multipart Upload API to parallelize large file uploads
C. Enable S3 Versioning to improve throughput
D. Enable Requester Pays on the bucket
E. Change the bucket's storage class to S3 Glacier Instant Retrieval
**Correct answer(s):** A, B
**Explanation:** Transfer Acceleration routes transfers through CloudFront edge locations over the AWS backbone, speeding up both the Sydney studio's long-distance uploads and worldwide end users' downloads (it accelerates GET as well as PUT/POST requests, not uploads only), while Multipart Upload parallelizes chunks of large files to fully utilize available bandwidth and improve upload resilience. Versioning (C) is a data-protection feature with no throughput effect, Requester Pays (D) is a billing feature, and Glacier Instant Retrieval (E) is an archival class poorly suited to high-throughput frequent access.

### Question 48 [Domain: 3] [Type: Single-Answer]
**Scenario:** A financial services firm runs a tightly-coupled HPC risk-simulation workload across 20 EC2 instances requiring extremely low inter-node latency and high (10+ Gbps) throughput between nodes, all within a single Availability Zone. A separate team runs a distributed logging cluster of 30 instances where nodes should be spread across distinct underlying racks/hardware to minimize correlated hardware failure, even within the same AZ.
**Options:**
A. Cluster placement group for HPC; Partition placement group for the logging cluster
B. Spread placement group for HPC; Cluster placement group for the logging cluster
C. Cluster placement group for HPC; Spread placement group for the logging cluster
D. Partition placement group for both workloads
**Correct answer(s):** A
**Explanation:** Cluster placement groups pack instances onto the same underlying hardware within one AZ for the lowest latency and highest throughput networking, ideal for tightly-coupled HPC. Partition placement groups spread instances across distinct logical partitions (separate racks/power/network), reducing correlated failure, and scale beyond the 7-instance-per-AZ cap of Spread groups—making them the right fit for the 30-node logging cluster. Spread groups (B, C) are limited to 7 instances per AZ, disqualifying the logging use case.

### Question 49 [Domain: 3] [Type: Single-Answer]
**Scenario:** A pharmaceutical company runs an MPI-based molecular dynamics simulation across a cluster of c6gn instances requiring very low-latency, high-bandwidth inter-node communication beyond what standard ENA enhanced networking provides—specifically the ability to bypass the OS kernel for inter-instance communication.
**Options:**
A. Enable Enhanced Networking with ENA on all instances
B. Attach an Elastic Fabric Adapter (EFA) to the instances
C. Use jumbo frames (9001 MTU) on the VPC
D. Place instances in a Spread placement group
**Correct answer(s):** B
**Explanation:** EFA is a network interface purpose-built for HPC/MPI applications, providing OS-bypass communication (via libfabric) between instances—exactly the kernel-bypass requirement described, typically paired with a cluster placement group. Standard ENA (A) improves networking but still traverses the normal OS network stack. Jumbo frames (C) reduce per-packet overhead but don't provide OS-bypass. Spread placement group (D) is the wrong grouping strategy for latency-sensitive tightly-coupled HPC.

### Question 50 [Domain: 3] [Type: Single-Answer]
**Scenario:** A social media application's DynamoDB table uses "post_id" as its partition key. During a viral event, one specific post_id receives a disproportionate share of read traffic ("hot partition"), causing ThrottlingException errors even though the table's overall provisioned RCUs are far from fully consumed at the table level.
**Options:**
A. Enable DynamoDB Auto Scaling to increase table-wide RCUs
B. Redesign the table to add a random or calculated suffix to the hot item's key to distribute its access pattern, combined with DAX for read caching
C. Switch the table to on-demand capacity mode only
D. Enable DynamoDB Streams
**Correct answer(s):** B
**Explanation:** A single partition has a physical throughput ceiling regardless of overall table capacity, so the fix requires sharding the hot key's access pattern (random/calculated suffix fan-out) combined with caching the hot item via DAX. Auto Scaling (A) raises table-wide capacity but doesn't relieve a single partition's ceiling. On-demand mode (C) includes adaptive capacity that helps somewhat but can still throttle under an extreme single-item hot spot—a partial mitigation, not a full fix—and Streams (D) is unrelated to read throughput.

### Question 51 [Domain: 3] [Type: Single-Answer]
**Scenario:** A manufacturing company needs to migrate 400TB of historical sensor data from an on-premises data center to S3 as a one-time migration; their current internet uplink is only 100 Mbps shared with other business traffic. Separately, once migrated, they need ongoing, consistent, low-latency, high-throughput (10 Gbps) private connectivity for a permanent hybrid workload.
**Options:**
A. Use AWS Snowball Edge for the one-time 400TB migration; provision AWS Direct Connect for ongoing hybrid connectivity
B. Use S3 Transfer Acceleration for the one-time migration; use a Site-to-Site VPN for ongoing connectivity
C. Use AWS DataSync over the existing 100 Mbps link for the migration; use Direct Connect for ongoing connectivity
D. Use Snowball Edge for both the one-time migration and the ongoing hybrid connectivity
**Correct answer(s):** A
**Explanation:** At 100 Mbps, moving 400TB over the internet would take months even with acceleration, making Snowball Edge's physical transfer the correct choice for the bulk one-time migration, while Direct Connect delivers the dedicated, consistent 10 Gbps low-latency link needed for ongoing hybrid operations. DataSync (C) is still bottlenecked by the shared 100 Mbps link. Snowball Edge (D) is a batch/physical device, not a solution for ongoing persistent connectivity.

### Question 52 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A latency-sensitive API backed by Lambda (Java runtime) experiences unacceptable cold-start spikes in p99 response time during predictable but recurring morning traffic surges from 8-9 AM daily. The team wants to eliminate cold starts during that known window and improve general execution performance, without overprovisioning cost 24/7. (Select TWO.)
**Options:**
A. Increase the Lambda function's allocated memory (which also increases proportional CPU)
B. Enable Provisioned Concurrency with an Application Auto Scaling schedule to scale up before 8 AM and down after 9 AM
C. Convert the function to use a larger ephemeral /tmp storage size
D. Switch the Lambda runtime to a container image to avoid cold starts entirely
E. Set Reserved Concurrency equal to Provisioned Concurrency at all times, 24/7
**Correct answer(s):** A, B
**Explanation:** Scheduled Provisioned Concurrency pre-initializes execution environments specifically for the known 8-9 AM window, eliminating cold starts only when needed and avoiding 24/7 cost; increasing memory proportionally increases CPU, directly reducing execution and JVM warmup time for Java. Larger /tmp storage (C) has no effect on cold starts or compute performance. Container images (D) do not eliminate cold starts—large images can actually worsen them. Setting Reserved Concurrency 24/7 (E) removes the cost-saving schedule benefit and doesn't itself pre-warm environments outside the provisioned window.

### Question 53 [Domain: 3] [Type: Single-Answer]
**Scenario:** A retail company runs its HTTPS storefront behind ALBs in three regions, using Route 53 latency-based routing with health checks for global distribution. During regional outages, some users experience up to 60 seconds of failed requests because ISP resolvers and corporate clients ignore the low configured TTL and cache stale records. They want faster failover at reasonable cost and are fine continuing to use HTTP/HTTPS-only ALBs (no UDP requirement).
**Options:**
A. Lower the Route 53 record TTL to 0 seconds
B. Add AWS Global Accelerator in front of the regional ALBs
C. Replace Route 53 with a single CloudFront distribution using one origin
D. Switch to Route 53 geolocation routing instead of latency-based routing
**Correct answer(s):** B
**Explanation:** Global Accelerator uses static anycast IPs and performs network-layer, health-check-based failover within seconds, completely bypassing DNS TTL/caching issues since clients never need to re-resolve DNS to fail over. Lowering TTL to 0 (A) doesn't guarantee compliance since many resolvers/proxies ignore it—exactly the stated problem. CloudFront with one origin (C) removes multi-region failover entirely, and geolocation routing (D) is just a different routing policy that doesn't address failover speed.

### Question 54 [Domain: 4] [Type: Single-Answer]
**Scenario:** A biotech research company runs nightly genomic sequencing analysis batch jobs on GPU-backed EC2 instances (p3.2xlarge). Jobs run for 3-6 hours, checkpoint every 10 minutes to S3, and can resume from the last checkpoint if interrupted. The workload is not time-critical (it can complete anytime within a 12-hour window), but the company wants to minimize compute cost while maintaining access to sufficient GPU capacity across the fleet. The security team also requires that all data at rest be encrypted with a customer-managed KMS key.
**Options:**
A. Launch a single On-Demand p3.2xlarge instance with EBS encryption enabled using a customer-managed KMS key.
B. Purchase a 1-year Standard Reserved Instance for p3.2xlarge and enable default EBS encryption.
C. Use EC2 Spot Instances via a Spot Fleet request spanning multiple GPU instance types and Availability Zones with the capacity-optimized allocation strategy, encrypting EBS volumes with a customer-managed KMS key.
D. Purchase a 1-year EC2 Instance Savings Plan for the p3 instance family in a single Availability Zone.
**Correct answer(s):** C
**Explanation:** Spot Instances offer up to ~90% savings over On-Demand and are ideal for fault-tolerant, checkpointed, non-time-critical batch jobs; diversifying across instance types/AZs with the capacity-optimized strategy maximizes available interruptible capacity, and KMS encryption with a customer-managed key satisfies the security requirement. Option A is a single instance with no capacity diversification and pays full On-Demand price. Option B fails the encryption requirement outright — "default EBS encryption" uses the AWS-managed key (`aws/ebs`) unless a customer-managed key has been explicitly set as the account default, and a single Reserved Instance also does nothing to broaden GPU capacity access. Option D (Savings Plan) reduces cost versus On-Demand but far less than Spot, doesn't address encryption, and Savings Plans/Reserved Instances are billing constructs, not capacity strategies, so they don't improve GPU capacity availability the way Spot Fleet diversification does.

### Question 55 [Domain: 4] [Type: Single-Answer]
**Scenario:** A media streaming startup allows users to upload video clips. Newly uploaded clips are viewed heavily within the first few days, then usage drops off unpredictably — some clips go viral again months later while most are never viewed again. The platform ingests over 50,000 new objects per day, and the team cannot predict which objects will need frequent access. They want a storage strategy that automatically minimizes cost as access patterns change, without manual lifecycle scripting and without added retrieval latency if an object suddenly becomes popular again.
**Options:**
A. Store all objects in S3 Standard and rely on CloudFront caching to reduce S3 GET costs.
B. Configure an S3 Lifecycle rule to transition objects to S3 Standard-IA after 30 days and S3 Glacier Flexible Retrieval after 90 days.
C. Store objects in S3 Intelligent-Tiering, allowing AWS to automatically move objects between access tiers based on usage patterns.
D. Store objects in S3 One Zone-IA to reduce cost, since video re-encoding pipelines can regenerate lost clips if needed.
**Correct answer(s):** C
**Explanation:** S3 Intelligent-Tiering is purpose-built for unknown or changing access patterns, automatically moving objects between frequent- and infrequent-access tiers with no retrieval latency or fee for those tiers, exactly matching the "sudden popularity" behavior described. Option A never reduces S3 storage cost since everything stays in Standard. Option B's rigid time-based lifecycle would penalize a clip that regains popularity by leaving it in a slower/costlier Glacier tier, which doesn't match the unpredictable-repopularity requirement. Option D trades away multi-AZ resilience for a modest storage discount and still doesn't adapt automatically to changing access patterns.

### Question 56 [Domain: 4] [Type: Single-Answer]
**Scenario:** A startup is launching a new mobile app backed by DynamoDB. They have no historical traffic data, expect potentially viral spikes from social features, and cannot predict read/write volume in advance. Engineering wants to avoid throttling during unexpected spikes and avoid both manually managing capacity and paying for idle provisioned throughput during quiet periods.
**Options:**
A. Provisioned capacity mode with Auto Scaling configured between a low minimum and high maximum RCU/WCU.
B. Provisioned capacity mode with capacity purchased via a 1-year Reserved Capacity plan.
C. On-Demand capacity mode.
D. Provisioned capacity mode with a manually set high fixed RCU/WCU to cover worst-case spikes.
**Correct answer(s):** C
**Explanation:** On-Demand mode instantly accommodates unpredictable spikes without capacity planning or throttling risk, billing per request unit consumed — ideal for a brand-new workload with unknown patterns. Auto Scaling (A) reacts to CloudWatch alarms with a lag and can still throttle during a sudden viral spike, making it less suitable than On-Demand for this specific unpredictability. Reserved Capacity (B) commits to a fixed throughput level for a 1-year term, which contradicts the "cannot predict volume" requirement, and a manually fixed high ceiling (D) guarantees paying for idle capacity during quiet periods.

### Question 57 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs EC2 instances in private subnets that read and write several TB of data per day to S3 buckets in the same region. Traffic currently routes through a NAT Gateway to reach S3's public endpoint, and the NAT Gateway's per-GB data processing charges have become a significant line item on the monthly bill. Security policy requires that instances never traverse the public internet to reach S3. The team wants to cut cost without weakening security or reducing throughput.
**Options:**
A. Replace the NAT Gateway with a fleet of NAT Instances to lower the hourly cost.
B. Create a Gateway VPC Endpoint for S3 and update the route table so S3 traffic no longer traverses the NAT Gateway.
C. Increase the NAT Gateway's bandwidth allocation to improve throughput and amortize cost.
D. Move the EC2 instances to public subnets with security groups restricting inbound traffic.
**Correct answer(s):** B
**Explanation:** A Gateway VPC Endpoint for S3 routes traffic privately within the AWS network at no per-GB data processing charge for the endpoint itself, eliminating NAT Gateway costs for S3 traffic while keeping traffic off the public internet. Option A still incurs data processing charges (and adds operational burden) without removing the security concern of traversing a NAT path unnecessarily. Option C doesn't reduce cost at all — it increases it. Option D might reduce NAT cost but violates the explicit security requirement by exposing instances to the internet via public subnets, regardless of security group rules.

### Question 58 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A company runs a steady baseline of EC2 workloads for the next 3 years across multiple instance families (m5, c5, r5) and multiple regions, with the flexibility to shift workloads between instance families as needs change and possibly move some workloads to Fargate or Lambda in the future. Finance wants the maximum possible discount for guaranteed usage, while engineering wants the freedom to change instance type, size, OS, tenancy, and compute platform without losing that discount. Select the TWO purchasing options that together best satisfy both requirements.
**Options:**
A. Purchase Standard Reserved Instances for each specific instance type and region combination.
B. Purchase Compute Savings Plans with a 3-year term.
C. Purchase Convertible Reserved Instances that can be exchanged for different instance attributes.
D. Purchase EC2 Instance Savings Plans scoped to a single instance family per region.
E. Rely entirely on On-Demand pricing to preserve maximum flexibility.
**Correct answer(s):** B, C
**Explanation:** Compute Savings Plans automatically apply to any instance family, size, OS, tenancy, region, and even Fargate/Lambda usage, giving maximum flexibility with a strong discount for a 3-year commitment — this is the piece that covers the possible future move to serverless compute. Convertible Reserved Instances complement this by covering the guaranteed steady-state EC2 baseline at a higher discount than a Compute Savings Plan would provide, while still letting the team exchange instance family, OS, or tenancy as needs evolve (though, unlike Compute Savings Plans, they cannot be exchanged onto Fargate or Lambda). Standard RIs (A) and single-family Savings Plans (D) lock in specific instance types/families and would forfeit the discount benefit if workloads shift as described, while On-Demand (E) sacrifices the discount entirely.

### Question 59 [Domain: 4] [Type: Single-Answer]
**Scenario:** A healthcare company must retain medical imaging records for 10 years for regulatory compliance. Records are accessed frequently for the first 60 days after creation (active patient care). Between 60 days and 2 years, records are rarely accessed but occasionally needed within minutes for follow-up care. After 2 years, records are essentially never accessed except during rare compliance audits, where retrieval must complete within 12 hours. The company wants to minimize storage cost across the full 10-year period while meeting these retrieval needs, with data encrypted at rest and all access logged.
**Options:**
A. Store all objects in S3 Standard for the full 10 years with S3 Object Lock in compliance mode.
B. Use a lifecycle policy to transition objects to S3 Standard-IA at 60 days, then to S3 Glacier Flexible Retrieval at 2 years, using SSE-KMS encryption with S3 access logging/CloudTrail enabled.
C. Use a lifecycle policy to transition objects directly to S3 Glacier Deep Archive at 60 days to achieve maximum savings.
D. Store all objects in S3 One Zone-IA for the entire retention period to reduce cost, since imaging files can be regenerated from source systems if needed.
**Correct answer(s):** B
**Explanation:** Standard-IA provides millisecond retrieval for the 60-day-to-2-year "occasionally needed within minutes" window at lower storage cost than Standard, and Glacier Flexible Retrieval (minutes with expedited, or a few hours with standard/bulk tiers) comfortably meets the 12-hour audit SLA thereafter, with SSE-KMS and CloudTrail satisfying the security/audit requirement. Option A never reduces cost across 10 years since it never leaves Standard. Option C skips straight to Deep Archive at 60 days, whose standard retrieval time (up to 12 hours) would violate the "within minutes" follow-up-care requirement during the 60-day-to-2-year window. Option D fails the durability/resiliency expectation for compliance-critical records since One Zone-IA has no cross-AZ redundancy.

### Question 60 [Domain: 4] [Type: Single-Answer]
**Scenario:** A gaming leaderboard application uses DynamoDB with a table receiving extremely read-heavy traffic (95% reads, 5% writes) against the same "hot" set of leaderboard items, which are re-read thousands of times per second during peak events. Read latency must stay under 1 millisecond, and provisioned RCU costs are growing rapidly as traffic scales, even though the underlying data changes only a few times per second. The team wants to cut DynamoDB read costs and improve latency without significantly redesigning application data-access code.
**Options:**
A. Switch the table to On-Demand capacity mode to automatically scale with read traffic.
B. Increase provisioned RCUs further and enable DynamoDB Auto Scaling to keep up with peak demand.
C. Add Amazon DynamoDB Accelerator (DAX) as an in-memory caching layer in front of the table.
D. Enable DynamoDB Streams and build a separate Lambda-based cache triggered on writes.
**Correct answer(s):** C
**Explanation:** DAX is a fully managed, DynamoDB-API-compatible in-memory cache that drops read latency to microseconds and drastically reduces RCU consumption for hot-key, read-heavy workloads, requiring only an endpoint change on the client. On-Demand (A) and Auto Scaling (B) would still meter and bill for capacity on every repeated read of the same unchanging hot items, failing to address the actual cost/latency driver. Option D would work eventually but requires substantial custom build-and-maintain effort, directly conflicting with the "without significantly redesigning application data-access code" requirement.

### Question 61 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company is migrating a large on-premises data warehouse workload to AWS and needs to transfer 20 TB of data monthly between its data center and its VPC on an ongoing basis, in addition to steady-state application traffic. The current Site-to-Site VPN over the internet suffers from inconsistent throughput and rising data transfer charges. The company needs a consistent, high-bandwidth, low-latency, cost-predictable private connection, must maintain connectivity if the primary link fails, and requires all data in transit to remain encrypted for compliance.
**Options:**
A. Increase the number of Site-to-Site VPN tunnels to load-balance traffic and reduce per-tunnel cost.
B. Provision an AWS Direct Connect dedicated connection as the primary path, with a Site-to-Site VPN as failover, and layer IPsec VPN/MACsec over the Direct Connect connection for encryption in transit.
C. Use AWS Snowball devices monthly to physically transfer the 20 TB, eliminating network transfer cost entirely.
D. Migrate entirely to AWS Storage Gateway in cached volume mode to avoid Direct Connect setup costs.
**Correct answer(s):** B
**Explanation:** Direct Connect provides consistent, high-bandwidth, low-latency connectivity at lower per-GB data transfer pricing than internet-based VPN for large recurring transfers, and pairing it with a VPN failover path satisfies resiliency; since Direct Connect traffic is not encrypted by default, adding IPsec (over a public/transit VIF) or MACsec (at the physical connection level on supported dedicated ports) meets the compliance requirement. Option A doesn't fix the underlying inconsistent-throughput/internet-routing problem. Snowball (C) suits one-time or infrequent bulk migrations, not a recurring monthly transfer combined with an always-available resilient network connection, and Snowball still doesn't address ongoing steady-state application traffic. Option D just relocates the same connectivity problem into a gateway appliance without solving bandwidth, latency, or failover.

### Question 62 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs a self-managed relational database on EC2 requiring a sustained 16,000 IOPS and 700 MB/s throughput. Their previous io1 configuration required over-provisioning IOPS just to reach adequate throughput, driving up cost. The database also underpins a mission-critical financial ledger requiring 99.999% volume durability, and the team wants to provision IOPS and throughput independently of volume size to avoid overpaying.
**Options:**
A. Continue using io1 volumes and provision additional IOPS to meet the throughput requirement.
B. Migrate to gp3 volumes, independently provisioning 16,000 IOPS and 700 MB/s throughput without over-provisioning storage size.
C. Migrate to st1 throughput-optimized HDD volumes to lower cost while meeting the throughput requirement.
D. Migrate to io2 Block Express volumes, which support high IOPS/throughput independent of size and 99.999% durability.
E. Use instance store (ephemeral) volumes to eliminate EBS costs entirely.
**Correct answer(s):** D
**Explanation:** io2 Block Express decouples IOPS (up to 256,000) and throughput (up to 4,000 MB/s) from volume size and is the only option meeting the strict 99.999% annual durability requirement for the financial ledger. gp3 (B) does decouple IOPS/throughput from size at lower cost and can technically hit 16,000 IOPS/700 MB/s, but like io1 and other non-io2 volume types it is only designed for 99.8%-99.9% durability, failing the explicit 99.999% requirement. Option A (io1) shares that same 99.8%-99.9% durability ceiling and doesn't solve the over-provisioning problem. Option C (st1) is HDD-based and cannot deliver the required IOPS. Option E (instance store) provides no persistence at all, which is unacceptable for a financial ledger.

### Question 63 [Domain: 4] [Type: Single-Answer]
**Scenario:** A retail company's order-processing database has highly variable load: near-zero traffic overnight, moderate traffic during business hours, and unpredictable 10x spikes during flash sales that can be announced with only a few hours' notice. The database currently runs on a provisioned Aurora MySQL cluster sized for peak flash-sale load, sitting idle/over-provisioned most of the time. The team wants to pay only for capacity actually used, automatically scale within seconds during sudden spikes, and retain Multi-AZ high availability without manual instance resizing.
**Options:**
A. Purchase Reserved Instances sized for peak flash-sale capacity to get a discount on the over-provisioned baseline.
B. Migrate to Aurora Serverless v2 with a Multi-AZ deployment, configured with an appropriate minimum and maximum ACU range.
C. Downsize the provisioned instance for average load and manually resize the cluster before each flash sale.
D. Move the database to DynamoDB On-Demand mode to eliminate capacity planning entirely.
**Correct answer(s):** B
**Explanation:** Aurora Serverless v2 scales compute in fine-grained ACU increments within seconds in response to load, supports Multi-AZ for HA, and bills only for capacity actually consumed — precisely fitting a highly variable, unpredictable workload. Reserved Instances (A) lock in payment for peak capacity around the clock regardless of actual usage, directly contradicting "pay only for capacity actually used." Manual resizing (C) cannot react in time to flash sales announced only hours in advance and still causes availability risk during the resize. Option D requires a full data-model and engine migration away from a relational database, which is a far more disruptive change than the requirement calls for.

### Question 64 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A global SaaS company serves static assets (JS/CSS/images) and cacheable API responses to users worldwide from an S3 bucket and an Application Load Balancer, both located only in us-east-1. Users in Asia-Pacific and Europe report slow load times, and data transfer-out costs from S3 and the ALB directly to the internet have grown substantially as the global user base increased. The company wants to reduce both global latency and origin data transfer costs, without duplicating infrastructure in every region. Select TWO actions that best achieve this.
**Options:**
A. Put Amazon CloudFront in front of both the S3 bucket and the ALB, caching static assets and cacheable API responses at edge locations worldwide.
B. Enable S3 Transfer Acceleration on the bucket for all downstream user traffic instead of using a CDN.
C. Configure appropriate Cache-Control headers/TTLs so CloudFront can serve repeat requests from edge caches without forwarding to the origin.
D. Replicate the S3 bucket and deploy duplicate ALBs and application stacks in every AWS region where users are located.
E. Switch the S3 bucket's storage class to S3 Glacier Instant Retrieval to lower per-GB data transfer pricing.
**Correct answer(s):** A, C
**Explanation:** Fronting both origins with CloudFront serves cached content from edge locations near users (cutting latency), while data transferred from an AWS origin such as S3 or an ALB to CloudFront is not charged, and CloudFront's own data-transfer-out-to-internet pricing is typically lower than transferring directly out of S3/EC2 at volume — so cache hits never even reach the origin, and the traffic that does is cheaper. Correctly set TTLs are what let CloudFront actually serve repeat requests from cache rather than re-fetching from the origin on every request, which is what actually realizes the cost and latency benefit. S3 Transfer Acceleration (B) only speeds up uploads into S3 via edge locations and doesn't cache or reduce cost for distributing content to end users. Duplicating infrastructure per region (D) directly contradicts the "without duplicating infrastructure" requirement. Storage class changes (E) have no effect on data transfer pricing or latency to end users.

### Question 65 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company's AWS bill has grown steadily. A cost review reveals dozens of EC2 instances across accounts averaging under 10% CPU utilization over the past 60 days, several unattached EBS volumes left over from terminated instances, and multiple idle Elastic Load Balancers with no registered healthy targets. The FinOps team wants an ongoing, low-effort way to continuously surface specific rightsizing and cleanup opportunities like these across the entire AWS Organization, backed by real utilization data, rather than performing manual one-off audits.
**Options:**
A. Manually review CloudWatch CPUUtilization graphs for every instance once per quarter.
B. Enable AWS Compute Optimizer across the organization to continuously analyze utilization metrics and generate rightsizing recommendations, and review AWS Trusted Advisor's cost optimization checks for idle/unattached resources.
C. Set AWS Budgets alerts to notify when monthly spend exceeds a fixed threshold.
D. Enable Cost Explorer's default reports only, without configuring any additional tools.
**Correct answer(s):** B
**Explanation:** AWS Compute Optimizer continuously analyzes historical CloudWatch utilization metrics to generate specific instance-type rightsizing recommendations, while Trusted Advisor's cost optimization checks automatically and ongoingly flag idle load balancers, unattached EBS volumes, and low-utilization EC2 instances — exactly the low-effort, continuous, data-backed approach requested. Option A is manual, infrequent, and doesn't scale across an Organization. AWS Budgets (C) only alerts on spend crossing a threshold after the fact and does not identify which specific resources to rightsize or remove. Cost Explorer's default reports (D) show spend trends but don't surface per-resource rightsizing or idle-resource recommendations the way Compute Optimizer and Trusted Advisor do.
