# AWS SAA-C03 Mock Exam 2

*Difficulty: Realistic exam level.*

These are 65 original practice questions (not real or leaked exam content). Each question is self-contained with its correct answer(s) and explanation inline — no separate answer key is needed.

---

### Question 1 [Domain: 1] [Type: Single-Answer]
**Scenario:** A developer, Maria, belongs to two IAM groups. Group "S3FullAccess" attaches a policy that allows `s3:*` on `arn:aws:s3:::project-bucket/*`. Group "S3Restricted" attaches a policy with an explicit `Deny` on `s3:DeleteObject` for all resources (`*`). Maria runs `aws s3 rm s3://project-bucket/report.pdf`.
**Options:**
A. The delete succeeds because the resource-specific Allow takes precedence over a wildcard Deny
B. The delete succeeds because IAM evaluates group policies in alphabetical order and applies the last one
C. The delete is denied because an explicit Deny always overrides any Allow in IAM policy evaluation
D. The delete succeeds because only the most recently attached policy is evaluated
**Correct answer(s):** C
**Explanation:** IAM's evaluation logic is: default deny → explicit allow → explicit deny wins. An explicit `Deny` anywhere in any applicable policy always overrides an `Allow`, regardless of specificity. Option A is the tempting distractor because many candidates assume "more specific" policies win, but that rule doesn't apply between Allow and Deny statements — explicit Deny is absolute.

### Question 2 [Domain: 1] [Type: Single-Answer]
**Scenario:** Northwind hires a SaaS monitoring vendor, MetricSphere, to pull CloudWatch metrics from Northwind's AWS account via a cross-account IAM role. MetricSphere manages similar roles for hundreds of other customers. Northwind's security team is concerned about the "confused deputy" problem, where MetricSphere's own service could be tricked into assuming a role belonging to a different customer than intended.
**Options:**
A. Require MetricSphere to pass a unique `ExternalId` when calling `sts:AssumeRole`, and add a `Condition` on `sts:ExternalId` in the role's trust policy
B. Issue MetricSphere an IAM user with long-term access keys instead of a role
C. Attach an SCP that denies all actions for every account except MetricSphere's account ID
D. Enable MFA Delete on the role's trust policy
E. Trust only MetricSphere's AWS account ID in the trust policy, with no further conditions
**Correct answer(s):** A
**Explanation:** The `ExternalId` condition is AWS's documented mechanism for third-party cross-account access precisely to prevent the confused deputy problem. Option E is the most tempting wrong answer since trusting the account ID looks sufficient, but without the ExternalId condition, MetricSphere's shared service could still be manipulated into assuming the wrong customer's role.

### Question 3 [Domain: 1] [Type: Single-Answer]
**Scenario:** An administrator creates a customer managed KMS key and edits its key policy to grant `kms:Decrypt` only to one specific IAM role, removing the default statement that grants the account root full access. Other administrators later attach IAM policies granting additional users `kms:Decrypt` on this key, but those users still receive Access Denied.
**Options:**
A. KMS keys can only ever be used by the principal that created them
B. Without a statement granting the account (root) permissions in the key policy, IAM identity-based policies alone cannot grant access — the key policy is the authoritative resource policy for KMS
C. KMS requires MFA to be enabled on every IAM user before any decrypt operation succeeds
D. The key must first be converted into a multi-Region key before IAM policies can apply
**Correct answer(s):** B
**Explanation:** KMS key policies are unusual in that IAM policies only work in combination with the key policy delegating permission to the account (typically via the root ARN); if that delegation is removed, only principals explicitly named in the key policy have access. Option A is tempting but wrong — KMS access is governed by policy, not by who created the key.

### Question 4 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company stores an Amazon RDS for MySQL master password in Secrets Manager and needs it automatically rotated every 30 days with zero manual intervention and no application downtime.
**Options:**
A. Store the password in Systems Manager Parameter Store as a SecureString and rotate it via a scheduled cron job
B. Enable automatic rotation on the secret using the built-in Secrets Manager RDS rotation Lambda function template
C. Use AWS Config rules to flag passwords older than 30 days for manual rotation
D. Store the password as a plaintext environment variable inside the RDS parameter group
**Correct answer(s):** B
**Explanation:** Secrets Manager provides native, built-in rotation templates for RDS that handle credential rotation and connection updates automatically with no custom scripting. Parameter Store (option A) has no built-in rotation engine and would require significant custom automation, making it a poor fit for "zero manual intervention."

### Question 5 [Domain: 1] [Type: Single-Answer]
**Scenario:** Web servers in a private subnet must accept inbound HTTPS (443) traffic only from an ALB in a public subnet and return responses to it. The team configures the subnet's Network ACL with an inbound rule allowing TCP 443 from the ALB subnet's CIDR, followed by the default deny-all rule. After deployment, the web servers' responses never reach the ALB.
**Options:**
A. NACLs are stateless, so an outbound rule allowing the ephemeral port range (1024–65535) back to the ALB subnet must also be added
B. The web servers' security group is blocking the return traffic
C. NACL rule numbers must be sequential with no gaps or return traffic is silently dropped
D. The ALB's security group lacks an inbound rule for port 443
**Correct answer(s):** A
**Explanation:** Unlike security groups, NACLs are stateless — return traffic must be explicitly permitted by a separate outbound rule, typically for the ephemeral port range. Option B is tempting since SGs are also involved in connectivity, but SGs are stateful and would automatically allow the return traffic once the inbound request was allowed.

### Question 6 [Domain: 1] [Type: Single-Answer]
**Scenario:** An application behind an ALB is experiencing repeated automated login attempts from a small number of source IPs. The security team wants to automatically block any single IP address that sends more than 1,000 requests to the `/login` path within a 5-minute window, while leaving all other traffic unaffected, with minimal operational overhead.
**Options:**
A. Create an AWS WAF rate-based rule scoped to the `/login` URI, associate it with the ALB's Web ACL, and set the block action
B. Add a security group rule that limits the number of connections per source IP
C. Enable AWS Shield Advanced, which automatically blocks IPs exceeding a request threshold
D. Write a custom Lambda function triggered by CloudWatch alarms that adds offending IPs to a Network ACL deny rule
**Correct answer(s):** A
**Explanation:** AWS WAF rate-based rules are purpose-built for this exact use case — they track request rate per IP over a rolling window and can be scoped to specific URI paths with minimal setup. Option D would technically work but requires substantial custom automation, failing the "least operational overhead" requirement.

### Question 7 [Domain: 1] [Type: Single-Answer]
**Scenario:** Amazon GuardDuty generates a finding of type `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration`, indicating that temporary credentials issued to an EC2 instance's IAM role were used from an external IP address never associated with that instance.
**Options:**
A. Ignore the finding, since GuardDuty findings involving instance roles are always false positives
B. Rotate the KMS key used to encrypt the instance's EBS volume
C. Immediately revoke the instance's active credentials (e.g., by isolating/terminating the instance or attaching a deny-all policy to the role) and begin an incident investigation
D. Disable GuardDuty in the affected region to stop further alerts
**Correct answer(s):** C
**Explanation:** This finding indicates likely credential theft and exfiltration, requiring immediate containment (revoking/rotating the exposed credentials, isolating the instance) followed by forensic investigation. Rotating the EBS encryption key (B) does nothing to stop misuse of already-exfiltrated IAM credentials.

### Question 8 [Domain: 1] [Type: Single-Answer]
**Scenario:** A mobile app must let users sign up and sign in with email/password including optional MFA, and after login, obtain temporary AWS credentials scoped to an IAM role so the app can upload photos directly to an S3 bucket.
**Options:**
A. Use a Cognito User Pool for authentication, and a Cognito Identity Pool (federated identities) configured to accept the User Pool as an identity provider, mapped to an IAM role that grants S3 access
B. Use a Cognito Identity Pool alone, since it natively handles both authentication and authorization
C. Use a Cognito User Pool alone, relying on its built-in IAM role attachment feature
D. Create an individual IAM user with long-term access keys embedded in the app for each end user
**Correct answer(s):** A
**Explanation:** User Pools handle authentication (sign-up/sign-in, MFA), while Identity Pools exchange the resulting tokens for temporary, scoped AWS credentials — this is the standard combined pattern. Option C is tempting because User Pools are the "front door," but they have no mechanism on their own to issue temporary AWS credentials.

### Question 9 [Domain: 1] [Type: Single-Answer]
**Scenario:** Within a single shared AWS account, a platform team wants to let application teams create their own IAM roles for their Lambda functions, but must guarantee that no role an application team creates can ever be granted `iam:*`, `s3:DeleteBucket`, or `organizations:*` permissions — no matter what policy is attached to it later. The platform team's own administrative access must remain unaffected.
**Options:**
A. Attach an SCP to the account that denies those three actions for all principals
B. Require `iam:CreateRole` calls to always specify a permissions boundary policy that caps the maximum permissions any role application teams create can ever have
C. Add a resource-based policy to each Lambda function restricting its own permissions
D. Use a tag-based IAM condition combined with GuardDuty findings to flag over-permissioned roles after the fact
**Correct answer(s):** B
**Explanation:** A permissions boundary sets the maximum permissions a role can have regardless of what identity-based policy is later attached to it, which is exactly the delegated-administration pattern this scenario requires. Option A is the tempting distractor, but an SCP applies account-wide to every principal — including the platform team itself — violating the requirement that platform team admin access remain unaffected.

### Question 10 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A data engineering team designs a client-side envelope encryption workflow for large files (up to 10 GB) before uploading them to S3, using a KMS customer managed key (CMK) and the `GenerateDataKey` API, since KMS `Encrypt`/`Decrypt` calls are limited to 4 KB of data. Select the statements that correctly describe this workflow.
**Options:**
A. The application calls `kms:GenerateDataKey` to receive both a plaintext data key and an encrypted copy of it, encrypts the file locally with the plaintext key, then discards the plaintext key and stores only the encrypted data key alongside the ciphertext
B. To decrypt later, the application calls `kms:Decrypt` on the stored encrypted data key to retrieve the plaintext data key, then uses it locally to decrypt the file
C. The plaintext data key must also be uploaded to S3 in a separate object so KMS can validate it during future decryption
D. KMS directly encrypts the entire 10 GB file using the CMK, with no local encryption library involved
E. The CMK itself never leaves AWS KMS; only the (wrapped) data key is exchanged with the client
**Correct answer(s):** A, B, E
**Explanation:** This is the standard envelope encryption pattern: KMS generates and wraps a data key, the client encrypts data locally with the plaintext key and discards it, and the CMK never leaves KMS. Option C is the tempting wrong answer — storing the plaintext data key anywhere defeats the entire purpose of envelope encryption.

### Question 11 [Domain: 1] [Type: Single-Answer]
**Scenario:** Account A owns an S3 bucket named `shared-data`. An IAM role in Account B needs read access to it. Account A's team adds a bucket policy granting `s3:GetObject` to Account B's role ARN. Users assuming that role in Account B still receive Access Denied when reading objects.
**Options:**
A. Account B's role also needs an identity-based IAM policy explicitly allowing `s3:GetObject` on the bucket resource — cross-account access requires permissions granted on both sides
B. The bucket must be made public for cross-account access to function
C. Account A must remove the bucket policy and rely solely on legacy ACLs instead
D. Cross-account S3 access is impossible without AWS Resource Access Manager (RAM)
**Correct answer(s):** A
**Explanation:** For cross-account resource access, both the resource-based policy (in Account A) and an identity-based policy (in Account B) must explicitly allow the action — a bucket policy alone is not sufficient for principals outside the resource-owning account's implicit trust. RAM (option D) is used for sharing specific resource types like subnets or TGWs, not for granting S3 object-level cross-account access.

### Question 12 [Domain: 1] [Type: Single-Answer]
**Scenario:** A startup needs to store 200 non-sensitive configuration values (feature flags, timeouts) and 5 database credentials that require automatic rotation, while minimizing cost.
**Options:**
A. Store all 205 values in Secrets Manager for consistency
B. Store the 200 configuration values in Systems Manager Parameter Store (standard tier, no charge) and the 5 database credentials in Secrets Manager with automatic rotation enabled
C. Store everything in Parameter Store SecureString parameters, since Parameter Store also supports rotation Lambdas identical to Secrets Manager
D. Store credentials inside EC2 user data scripts and configuration values in an S3 bucket
**Correct answer(s):** B
**Explanation:** Parameter Store's standard tier is free and well-suited to non-sensitive configuration, while Secrets Manager provides native automatic rotation needed for the database credentials — using each service for its strength minimizes cost. Option C is a common misconception: Parameter Store has no built-in automatic rotation engine comparable to Secrets Manager's.

### Question 13 [Domain: 1] [Type: Single-Answer]
**Scenario:** In an AWS Organization, a member account administrator attaches an IAM policy granting a developer full `ec2:*` permissions. However, the management account has an SCP attached to the OU containing this account that denies `ec2:RunInstances` for any instance type other than `t3.micro` or `t3.small`. The developer attempts to launch an `m5.large` instance.
**Options:**
A. The instance launches because IAM Allow policies within the member account override SCPs
B. The launch is denied because SCPs define the maximum available permissions for the entire account, and no IAM policy within the account can exceed that boundary
C. The instance launches because SCPs only restrict actions taken by the organization's management account itself
D. The developer can request an SCP exception via a support ticket, which AWS auto-approves for single instances
**Correct answer(s):** B
**Explanation:** SCPs act as guardrails that define the maximum permissions available in an account; even an `Allow *` IAM policy cannot grant access to an action an applicable SCP denies. Option A reflects a common misunderstanding — SCPs and IAM policies are evaluated together, and SCPs always cap what IAM can grant, never the reverse.

### Question 14 [Domain: 1] [Type: Single-Answer]
**Scenario:** EC2 instances sit in a private subnet with no internet gateway or NAT gateway, reaching S3 via a Gateway VPC endpoint. Security requires that these instances can access only the company's own `app-data` bucket and no other S3 bucket in any AWS account, including public ones.
**Options:**
A. Rely on the default endpoint policy, which already restricts access to buckets owned by the same account
B. Attach a custom VPC endpoint policy that allows S3 actions only on the `app-data` bucket ARN, in addition to any relevant IAM and bucket policies
C. Add a Network ACL rule that blocks traffic to all S3 IP address ranges except one
D. This isn't achievable because Gateway endpoints route all S3 traffic identically regardless of destination bucket
**Correct answer(s):** B
**Explanation:** VPC endpoint policies can be scoped down to specific resource ARNs, and combined with IAM/bucket policies, they enforce that traffic through the endpoint can only reach the approved bucket. Option A is wrong because the default endpoint policy allows access to all S3 resources, not just same-account buckets.

### Question 15 [Domain: 1] [Type: Single-Answer]
**Scenario:** A 5,000-employee enterprise uses Okta as its corporate identity provider and wants employees to sign in once and access multiple AWS accounts within its AWS Organization using role-based permission sets, without provisioning individual IAM users in every account.
**Options:**
A. Create an IAM user per employee in the management account and configure cross-account roles manually
B. Use AWS IAM Identity Center (successor to AWS SSO), federated with Okta via SAML 2.0, assigning permission sets to groups across accounts
C. Use Cognito User Pools federated with Okta to grant AWS Management Console access
D. Distribute long-term IAM access keys to employees through a shared internal spreadsheet
**Correct answer(s):** B
**Explanation:** IAM Identity Center is purpose-built for centralized workforce SSO across multiple AWS accounts using SAML-based external IdPs, with permission sets mapped to accounts/groups. Cognito (option C) is designed for customer-facing application identity, not AWS Console/CLI access for workforce users.

### Question 16 [Domain: 1] [Type: Multiple-Response]
**Scenario:** The security team wants to automatically move any EC2 instance flagged by GuardDuty with a high-severity finding (e.g., malware communicating with a known command-and-control IP) into a quarantine security group with no outbound rules, without any human intervention. Select the two components required in this automated remediation pipeline.
**Options:**
A. An Amazon EventBridge rule matching GuardDuty finding events with severity at or above a defined threshold
B. An AWS Lambda function, triggered by the EventBridge rule, that calls the EC2 API to modify the instance's security groups to the quarantine group
C. A GuardDuty malware protection agent manually installed on every EC2 instance
D. An AWS Config conformance pack that evaluates instance tags once every 24 hours
E. A CloudTrail Insights dashboard reviewed manually each morning by the SOC team
**Correct answer(s):** A, B
**Explanation:** GuardDuty findings flow into EventBridge as events, which can trigger a Lambda function to perform automated remediation via the EC2 API — this is the standard "detect and auto-remediate" pattern. Option D is the tempting distractor because AWS Config is also a security/compliance tool, but its 24-hour evaluation cadence is far too slow for near-real-time isolation of an active threat.

### Question 17 [Domain: 1] [Type: Single-Answer]
**Scenario:** A B2B SaaS company's custom web application must let each enterprise customer's employees authenticate using that customer's own Azure AD (SAML 2.0) identity provider, then receive temporary AWS credentials scoped to that specific customer's isolated resources (e.g., a per-tenant S3 prefix).
**Options:**
A. Use Amazon Cognito Identity Pools configured with each customer's SAML IdP as an authentication provider, mapping SAML attributes to IAM roles for tenant isolation
B. Require every enterprise customer to manually create IAM users for each of their employees
C. Use AWS IAM Identity Center for these external, customer-owned identities, since it is designed for consumer-facing multi-tenant apps
D. Store each customer's Azure AD credentials directly in Secrets Manager and validate them within application code
**Correct answer(s):** A
**Explanation:** Cognito Identity Pools natively support SAML 2.0 federation and can map identity/attribute claims to different IAM roles, enabling scoped, temporary, per-tenant AWS credentials. Option C is the tempting distractor, but IAM Identity Center is intended for an organization's own workforce access to AWS accounts, not for federating external customers' end users into a multi-tenant SaaS app.

### Question 18 [Domain: 1] [Type: Single-Answer]
**Scenario:** A subnet's Network ACL has these inbound rules: Rule 100 allows TCP port 80 from `0.0.0.0/0`; Rule 90 denies TCP port 80 from `203.0.113.0/24`; and the default rule `*` denies all traffic. A request arrives on port 80 from `203.0.113.5`.
**Options:**
A. The request is allowed because Rule 100 is the primary rule and lower-numbered rules are only tiebreakers
B. The request is denied because NACL rules are evaluated in ascending numeric order, and Rule 90 (deny) is evaluated and matched before Rule 100 (allow)
C. The request is allowed because the more specific CIDR block always wins regardless of rule number
D. The request is denied only because the default NACL denies all inbound traffic unless explicitly modified
**Correct answer(s):** B
**Explanation:** NACLs evaluate rules strictly in ascending order by rule number and stop at the first match; since Rule 90 is evaluated before Rule 100 and matches the source, the traffic is denied. Option D is wrong because in this scenario the explicit deny rule (90) — not the default catch-all — is what actually determines the outcome.

### Question 19 [Domain: 1] [Type: Multiple-Response]
**Scenario:** An e-commerce company running a public web application on an ALB and CloudFront wants comprehensive protection against both network/transport-layer DDoS attacks and application-layer attacks (SQL injection, XSS, credential stuffing), along with attack diagnostics and cost protection during large-scale attacks. Select the three correct statements.
**Options:**
A. AWS Shield Standard is automatically enabled at no additional cost for all AWS customers and protects against common network/transport layer (layer 3/4) DDoS attacks
B. AWS WAF should be deployed on CloudFront/ALB with managed rule groups (SQLi, XSS, bot control) to protect against application-layer (layer 7) attacks; it is a separate service from Shield
C. Shield Standard alone includes SQL injection and XSS protection, making WAF unnecessary
D. Shield Advanced offers no meaningful benefit over Shield Standard beyond a nicer dashboard
E. Subscribing to Shield Advanced provides DDoS cost protection (credits for scaling charges incurred during an attack) and 24/7 access to the AWS DDoS Response Team (DRT)
**Correct answer(s):** A, B, E
**Explanation:** Shield Standard is free and automatic for L3/L4 protection, WAF is the correct tool for L7 application attacks, and Shield Advanced adds cost protection plus DRT access — together they form the layered defense the scenario requires. Option C is the tempting wrong answer, since candidates often assume Shield covers everything, but Shield does not inspect or filter application-layer content like SQL injection payloads.

### Question 20 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A security engineer must write an IAM policy statement that only allows certain sensitive console actions to succeed when the request (1) originates from the corporate office CIDR range and (2) the calling user has authenticated with MFA in the current session. Select the two condition elements that correctly enforce these two requirements.
**Options:**
A. `"Condition": {"IpAddress": {"aws:SourceIp": "203.0.113.0/24"}}`
B. `"Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}`
C. `"Condition": {"StringEquals": {"aws:RequestedRegion": "us-east-1"}}`
D. `"Condition": {"Null": {"aws:TokenIssueTime": "true"}}`
E. `"Condition": {"DateGreaterThan": {"aws:CurrentTime": "2026-01-01T00:00:00Z"}}`
**Correct answer(s):** A, B
**Explanation:** `aws:SourceIp` with the `IpAddress` operator restricts by source network, and `aws:MultiFactorAuthPresent` with the `Bool` operator enforces that the session was authenticated with MFA — together they satisfy both stated requirements. Option D is a plausible-looking distractor since `aws:TokenIssueTime` does relate to session credentials, but the `Null` check only tests whether the key exists (useful for detecting temporary vs. long-term credentials), not whether MFA was actually used.

### Question 21 [Domain: 2] [Type: Single-Answer]
**Scenario:** A fintech company runs a critical order-matching database on an Amazon RDS for PostgreSQL Multi-AZ instance (single non-readable standby). During peak trading hours, read replicas suffer from replication lag that causes stale price data to be served. The team also wants failover time to stay under 35 seconds and wants the standby capacity to be usable for read traffic instead of sitting idle.
**Options:**
A. Keep the current RDS Multi-AZ DB instance deployment and add more read replicas
B. Migrate to an RDS Multi-AZ DB cluster deployment with two readable standby instances
C. Convert to a Single-AZ instance with a cross-region read replica for reads
D. Enable RDS Proxy in front of the existing Multi-AZ instance
E. Migrate to an RDS Global Database deployment for PostgreSQL

**Correct answer(s):** B
**Explanation:** RDS Multi-AZ DB cluster deployments provide two readable standby instances behind a dedicated reader endpoint, using synchronous replication with quorum-based commits and typically under 35 seconds of automated failover — solving both the readable-capacity and fast-failover requirements. RDS Proxy (D) improves connection handling and failover speed for the app tier but adds no read capacity; RDS Global Database (E) is an Aurora-only feature, not available for standard RDS for PostgreSQL.

### Question 22 [Domain: 2] [Type: Single-Answer]
**Scenario:** An e-commerce platform is being re-architected into microservices. Incoming HTTPS traffic must be routed to different backend target groups based on URL path (`/cart`, `/catalog`, `/checkout`), must support WebSocket connections for a live chat feature, and needs native integration with AWS WAF for request filtering.
**Options:**
A. Network Load Balancer
B. Application Load Balancer
C. Classic Load Balancer
D. Gateway Load Balancer

**Correct answer(s):** B
**Explanation:** ALB operates at Layer 7, supporting path-based routing, WebSockets, HTTP/2, and native AWS WAF integration — matching every requirement. NLB operates at Layer 4 and cannot perform path-based routing or attach directly to WAF, making it unsuitable despite its strong performance characteristics.

### Question 23 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company runs its primary application stack in us-east-1 and maintains a pilot-light DR environment in us-west-2. They want DNS to normally resolve only to the us-east-1 endpoint, and automatically shift all traffic to the us-west-2 endpoint only when health checks against the primary fail.
**Options:**
A. Weighted routing policy
B. Latency-based routing policy
C. Failover routing policy with health checks
D. Geolocation routing policy

**Correct answer(s):** C
**Explanation:** Route 53 failover routing is purpose-built for active-passive configurations, automatically routing to the secondary record only when the primary's associated health check reports unhealthy. Weighted and latency-based routing would send some traffic to us-west-2 under normal conditions, which doesn't meet the "only during failure" requirement.

### Question 24 [Domain: 2] [Type: Multiple-Response]
**Scenario:** An order-processing pipeline requires messages for each customer to be processed in strict order and without duplicate delivery to downstream systems. The team currently uses an SQS Standard queue, which occasionally delivers messages out of order and more than once, so they are migrating to SQS FIFO. Select two statements that correctly describe how FIFO addresses these specific requirements.
**Options:**
A. FIFO queues support up to 3,000 messages/sec per API action when using batching
B. FIFO queues provide exactly-once processing via 5-minute deduplication combined with strict ordering per message group
C. FIFO queues automatically scale to the same unlimited throughput as Standard queues
D. FIFO queues replicate messages across regions to preserve global ordering
E. Ordering in a FIFO queue is guaranteed only within messages that share the same MessageGroupId, not across the entire queue

**Correct answer(s):** B, E
**Explanation:** FIFO's deduplication window plus message-group-scoped ordering directly solves the duplicate-delivery and per-customer ordering problems described. Option A is a true throughput fact but doesn't address the ordering/duplication requirement being asked about; C is false (FIFO has lower throughput limits than Standard), and D is false since SQS has no cross-region ordering feature.

### Question 25 [Domain: 2] [Type: Single-Answer]
**Scenario:** A web tier's Auto Scaling group needs to automatically add or remove instances so that average CPU utilization across the group stays near 50%, with minimal ongoing manual tuning of thresholds by the operations team.
**Options:**
A. Simple scaling policy
B. Step scaling policy
C. Target tracking scaling policy
D. Scheduled scaling action

**Correct answer(s):** C
**Explanation:** Target tracking policies work like a thermostat, automatically adjusting capacity to keep a specified metric (e.g., average CPU) at a target value, requiring minimal manual tuning. Simple and step scaling require manually defined thresholds and adjustment amounts, and scheduled scaling doesn't respond to actual utilization at all.

### Question 26 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company wants a low-cost disaster recovery approach for on-premises VMware workloads, targeting an RPO of seconds to minutes, while avoiding the cost of running full-scale recovery instances continuously. Recovery instances should only be launched in AWS at the time of an actual failover.
**Options:**
A. Pilot light using manually updated AMIs refreshed weekly
B. AWS Elastic Disaster Recovery (DRS) with continuous block-level replication to a low-cost staging area
C. AWS Backup with daily backup jobs to Amazon S3
D. Warm standby with a fully running duplicate production environment

**Correct answer(s):** B
**Explanation:** AWS DRS continuously replicates block-level changes from source servers into a lightweight staging area, enabling launch of fully provisioned recovery instances within minutes and an RPO measured in seconds — far better than a manually refreshed pilot light AMI. Warm standby (D) would meet the RTO/RPO goals but contradicts the requirement to avoid running full-scale instances continuously.

### Question 27 [Domain: 2] [Type: Single-Answer]
**Scenario:** When an order event occurs, three independent downstream processes must each receive a copy of every event: an inventory-update Lambda function, an email-notification service polling an SQS queue, and an archival process polling a separate SQS queue. Each consumer must get every message independently, without competing for the same message.
**Options:**
A. A single SQS queue polled by all three applications
B. An SNS topic with three subscribers: two SQS queues and one Lambda function
C. An EventBridge scheduled rule invoking each service in sequence
D. A Kinesis Data Stream with three consumer applications sharing one shard

**Correct answer(s):** B
**Explanation:** This is the classic SNS fan-out pattern: publishing once to an SNS topic delivers an independent copy of the message to every subscriber. A single shared SQS queue (A) would have consumers compete for messages, so each message is processed only once overall, not once per service.

### Question 28 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A microservices team wants to decouple an order-producing service from multiple independent consumers (billing, shipping, analytics) using an event-driven architecture. They need content-based filtering on event payloads, the ability to route events to both AWS services and third-party SaaS applications, and a way to discover/document the structure of events flowing through the system. Select three capabilities that make Amazon EventBridge a better fit than plain SNS for this design.
**Options:**
A. A built-in event bus with advanced content-based filtering rules on event payloads
B. A schema registry with automatic schema discovery for events
C. Guaranteed strict FIFO ordering across all consumers of the event bus
D. Native integrations with SaaS partner event sources
E. A contractual sub-millisecond message delivery SLA

**Correct answer(s):** A, B, D
**Explanation:** EventBridge offers rich content-based filtering, a schema registry for discovering and versioning event structures, and built-in SaaS partner event source integrations — capabilities SNS lacks, and each maps directly to one of the three stated requirements (filtering, SaaS routing, schema discovery). There is no guaranteed FIFO ordering across an EventBridge bus (C) and no sub-millisecond delivery SLA (E) is published by AWS.

### Question 29 [Domain: 2] [Type: Single-Answer]
**Scenario:** A real-time clickstream analytics platform ingests millions of events per second from a web application. Multiple independent analytics applications need to consume and, when needed, replay the same raw event data within a 7-day retention window for different purposes (fraud detection, personalization, reporting).
**Options:**
A. An SQS Standard queue with all consumer applications polling it
B. An SQS FIFO queue with per-consumer message groups
C. Kinesis Data Streams with enhanced fan-out for each consumer
D. An SNS topic with each consumer subscribed directly

**Correct answer(s):** C
**Explanation:** Kinesis Data Streams retains data for up to 7 days and allows multiple independent consumers to read and replay from any point in the stream, which enhanced fan-out optimizes for low-latency parallel consumption. SQS deletes a message once it's consumed, making native replay impossible at this scale without significant added complexity.

### Question 30 [Domain: 2] [Type: Single-Answer]
**Scenario:** An application runs active-active in eu-west-1 and ap-southeast-1. During a canary release, the team wants to gradually shift approximately 10% of overall traffic to a newly deployed eu-west-1 stack while both regions remain healthy and serving traffic.
**Options:**
A. Failover routing policy
B. Weighted routing policy
C. Geolocation routing policy
D. Multi-value answer routing policy

**Correct answer(s):** B
**Explanation:** Weighted routing lets you assign relative weights to multiple healthy records, enabling controlled, gradual traffic shifting such as a 10/90 canary split. Failover routing only activates the secondary on health-check failure and doesn't support proportional traffic splitting between healthy endpoints.

### Question 31 [Domain: 2] [Type: Single-Answer]
**Scenario:** New instances launched by an Auto Scaling group need to complete custom bootstrap validation and software installation, remaining out of service until validation passes, before they begin receiving traffic. During scale-in, instances must also run a cleanup script and finish draining connections before being terminated.
**Options:**
A. Rely solely on a user data script executed at launch
B. Configure Auto Scaling lifecycle hooks (Pending:Wait and Terminating:Wait)
C. Use scheduled scaling actions to control instance timing
D. Use a warm pool with no lifecycle hooks configured

**Correct answer(s):** B
**Explanation:** Lifecycle hooks let you pause an instance in a Pending or Terminating wait state so custom actions (validation, cleanup) can complete before the instance transitions to InService or is terminated. A plain user data script (A) runs at boot but provides no mechanism to hold the instance out of service until an external validation step confirms success.

### Question 32 [Domain: 2] [Type: Single-Answer]
**Scenario:** During rolling deployments, an Auto Scaling group behind an Application Load Balancer terminates old instances as new ones come online. Users report dropped requests because in-flight transactions on outgoing instances are cut off before completing.
**Options:**
A. Increase the ALB idle timeout setting
B. Configure a deregistration delay (connection draining) on the target group
C. Enable sticky sessions on the target group
D. Increase the Auto Scaling group's default cooldown period

**Correct answer(s):** B
**Explanation:** Deregistration delay keeps a target in a "draining" state for a configurable period, allowing in-flight requests to complete before the instance is fully deregistered and terminated. Idle timeout (A) controls how long the ALB keeps an idle client connection open and doesn't affect deregistration behavior.

### Question 33 [Domain: 2] [Type: Single-Answer]
**Scenario:** A trading platform requires an RTO of a few minutes and an RPO near zero. The business is willing to pay for a scaled-down, but fully functional, duplicate environment continuously running in a second region that can be rapidly scaled up during a failover event.
**Options:**
A. Backup and restore
B. Pilot light
C. Warm standby
D. Multi-site active-active

**Correct answer(s):** C
**Explanation:** Warm standby keeps a scaled-down but fully functional copy of the production environment running at all times, allowing it to be quickly scaled up to full capacity — matching a minutes-level RTO at moderate cost. Pilot light (B) only keeps core data services running continuously and requires provisioning application servers from scratch during failover, resulting in a longer RTO than described here.

### Question 34 [Domain: 2] [Type: Single-Answer]
**Scenario:** A compliance mandate requires automated, centrally managed backup policies spanning EBS volumes, RDS databases, DynamoDB tables, and EFS file systems, with backups copied to a second region and retained for 7 years, using minimal custom scripting.
**Options:**
A. Custom Lambda functions triggered by EventBridge that call each service's native snapshot API
B. AWS Backup with a backup plan including a cross-region copy rule and lifecycle retention
C. Manual snapshots taken and reviewed quarterly by the operations team
D. Amazon S3 Cross-Region Replication configured on each service's underlying storage

**Correct answer(s):** B
**Explanation:** AWS Backup provides a single, centralized service to define backup plans, schedules, cross-region copy rules, and long-term lifecycle retention across all the listed services without custom code. Option A could technically work but requires significant custom development and maintenance that AWS Backup already provides out of the box.

### Question 35 [Domain: 2] [Type: Single-Answer]
**Scenario:** A consumer application repeatedly fails to process certain malformed messages from an SQS queue, causing them to be redelivered indefinitely and degrading overall queue throughput. The team wants poison-pill messages isolated after 5 failed processing attempts for later investigation, without losing the messages.
**Options:**
A. Increase the visibility timeout to an indefinite value
B. Configure a dead-letter queue with a redrive policy maxReceiveCount of 5
C. Purge the entire queue on a daily schedule
D. Enable long polling on the queue

**Correct answer(s):** B
**Explanation:** A redrive policy pointing to a dead-letter queue automatically moves a message there after it has been received the configured number of times without successful deletion, isolating problem messages while preserving them for investigation. Increasing visibility timeout indefinitely (A) only delays reprocessing and doesn't remove poison-pill messages from the main queue's flow.

### Question 36 [Domain: 2] [Type: Single-Answer]
**Scenario:** A production RDS for MySQL database runs in us-east-1. The company wants the ability to promote a database in eu-central-1 to a standalone writable primary within minutes during a regional outage, while also using that eu-central-1 database to serve low-latency reads to EU customers day-to-day — without migrating to Aurora.
**Options:**
A. A Multi-AZ deployment confined to us-east-1
B. A cross-region read replica in eu-central-1, promotable to a standalone instance during failover
C. Nightly manual cross-region snapshot copies
D. AWS DMS continuous replication into a separate RDS instance in eu-central-1

**Correct answer(s):** B
**Explanation:** RDS cross-region read replicas serve local read traffic during normal operation and can be promoted to a standalone writable instance within minutes during a DR event, meeting both requirements natively. AWS DMS (D) could achieve similar replication but adds unnecessary operational overhead compared to the built-in cross-region read replica feature.

### Question 37 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A team configures Amazon S3 Cross-Region Replication (CRR) from a bucket in us-east-1 to a bucket in ap-southeast-2 to protect static assets for disaster recovery. After creating the replication rule, no objects are replicating. Select two prerequisites that must be satisfied for S3 CRR to function.
**Options:**
A. Versioning must be enabled on both the source and destination buckets
B. An IAM role granting Amazon S3 permission to replicate objects on your behalf must be configured
C. Both buckets must belong to the same AWS account
D. The destination bucket must use the S3 Standard storage class exclusively
E. The source and destination buckets must share the identical bucket name

**Correct answer(s):** A, B
**Explanation:** S3 CRR requires versioning enabled on both the source and destination buckets, plus an IAM role that authorizes S3 to perform the replication. CRR supports replication across different AWS accounts (making C false) and allows the destination to use a different storage class than the source (making D false); bucket names must be globally unique, so identical names (E) is neither required nor typically possible.

### Question 38 [Domain: 3] [Type: Single-Answer]
**Scenario:** A media company runs a batch video-encoding pipeline that is heavily CPU-bound. The workload needs high per-vCPU compute performance at the lowest possible cost, and does not need large amounts of memory or local storage.
**Options:**
A. R6g memory-optimized instances
B. C7g compute-optimized instances (Graviton3)
C. T3 burstable general-purpose instances
D. I4i storage-optimized instances

**Correct answer(s):** B
**Explanation:** The C-family compute-optimized instances are built for CPU-bound workloads like media encoding, and the Graviton3-based C7g offers strong price/performance. T3 instances (C) are burstable and unsuitable for sustained, heavy CPU load, and R6g/I4i are optimized for memory and storage-heavy workloads respectively, not raw compute.

### Question 39 [Domain: 3] [Type: Single-Answer]
**Scenario:** A self-managed OLTP database on EC2 requires a consistent 64,000 IOPS with sub-millisecond latency, and the storage must provide 99.999% durability regardless of the volume's size.
**Options:**
A. EBS gp3 volume
B. EBS io2 Block Express volume
C. EBS st1 (throughput-optimized HDD) volume
D. EC2 instance store (NVMe SSD)

**Correct answer(s):** B
**Explanation:** io2 Block Express volumes support up to 256,000 IOPS with sub-millisecond latency and 99.999% durability, independent of volume size, meeting all stated requirements. gp3 tops out at 16,000 IOPS, well short of the requirement, and instance store is ephemeral and non-durable, failing the durability requirement entirely.

### Question 40 [Domain: 3] [Type: Single-Answer]
**Scenario:** An application needs an in-memory session store that supports data persistence, Multi-AZ replication for high availability, pub/sub messaging, and complex data structures such as sorted sets to power a real-time leaderboard.
**Options:**
A. ElastiCache for Memcached
B. ElastiCache for Redis
C. DynamoDB Accelerator (DAX)
D. Amazon MQ

**Correct answer(s):** B
**Explanation:** Redis natively supports persistence, replication/HA, pub/sub, and rich data structures like sorted sets, matching every stated requirement. Memcached (A) is simpler, multi-threaded, and lacks persistence, replication, and advanced data structures.

### Question 41 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company hosts private video content in an S3 bucket that must be accessible only through its CloudFront distribution. Direct requests to the S3 bucket URL must be blocked, and the team wants to use the current AWS-recommended access-restriction mechanism instead of the older, legacy approach.
**Options:**
A. Make the bucket public and rely on CloudFront caching alone
B. Configure Origin Access Control (OAC) and restrict the bucket policy to the CloudFront distribution
C. Grant public-read access via a bucket ACL
D. Configure Lambda@Edge to validate every request against an IAM policy

**Correct answer(s):** B
**Explanation:** Origin Access Control (OAC) is AWS's current recommended mechanism for restricting S3 origin access to only a specific CloudFront distribution, replacing the older Origin Access Identity (OAI). Making the bucket public (A) or using a public-read ACL (C) would allow direct S3 access, violating the requirement.

### Question 42 [Domain: 3] [Type: Single-Answer]
**Scenario:** A gaming company runs a latency-sensitive multiplayer backend on EC2 across two regions, using a mix of TCP and UDP traffic that is not cacheable HTTP content. They need static anycast IP addresses and fast automatic failover across regions and AZs at the network layer.
**Options:**
A. Amazon CloudFront
B. AWS Global Accelerator
C. Route 53 latency-based routing alone
D. An Application Load Balancer with cross-zone load balancing

**Correct answer(s):** B
**Explanation:** Global Accelerator provides static anycast IP addresses and operates at the network layer, supporting both TCP and UDP traffic with fast automatic failover across regions and AZs — ideal for non-HTTP, non-cacheable game traffic. CloudFront is designed for cacheable HTTP(S) content delivery and is not suited to generic TCP/UDP multiplayer traffic.

### Question 43 [Domain: 3] [Type: Single-Answer]
**Scenario:** A read-heavy DynamoDB table serves repeated read requests on a small set of "hot" keys. Current single-digit-millisecond read latency is too slow for the use case, which requires microsecond-level response times, and the team wants an in-memory cache with an API compatible with existing DynamoDB code, avoiding a major application rewrite.
**Options:**
A. ElastiCache for Redis with custom application-level caching logic
B. DynamoDB Accelerator (DAX)
C. DynamoDB Global Tables
D. Increasing the table's provisioned read capacity units

**Correct answer(s):** B
**Explanation:** DAX is a DynamoDB-compatible, in-memory caching layer that requires minimal code changes and delivers microsecond read latency for cached items, directly solving the stated requirement. ElastiCache (A) would work technically but requires building and maintaining custom cache-aside logic, unlike DAX's drop-in compatibility.

### Question 44 [Domain: 3] [Type: Single-Answer]
**Scenario:** A SaaS company has users in the US and Asia. Writes must remain in us-east-1, but the team wants sub-second cross-region replication so ap-northeast-1 users get low-latency local reads, plus the ability to promote the secondary region to a full read/write primary within about a minute during a regional DR event.
**Options:**
A. An Aurora Read Replica within the same region as the primary
B. Aurora Global Database with a secondary region
C. An RDS for MySQL cross-region read replica
D. DynamoDB Global Tables

**Correct answer(s):** B
**Explanation:** Aurora Global Database uses dedicated, purpose-built storage-based replication that typically achieves sub-second cross-region lag and supports promoting a secondary region to full read/write in about a minute. A standard RDS cross-region read replica (C) usually has higher, less predictable replication lag and a slower promotion process, not meeting the stated latency and RTO targets.

### Question 45 [Domain: 3] [Type: Single-Answer]
**Scenario:** A media platform's global user base uploads large video files directly to a single S3 bucket in us-east-1. Users in Australia and India report significantly slower upload speeds than users in North America. The team wants to improve upload performance without restructuring the application or creating regional buckets.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket
B. Enable S3 Cross-Region Replication to buckets in each region
C. Change the bucket's storage class to S3 One Zone-IA
D. Put CloudFront in front of the bucket using default cache settings

**Correct answer(s):** A
**Explanation:** S3 Transfer Acceleration routes uploads through the nearest CloudFront edge location onto the optimized AWS backbone network, meaningfully improving upload speed for geographically distant users with no architectural changes. Cross-Region Replication (B) only helps after data has already landed in the source bucket and doesn't speed up the initial long-haul upload.

### Question 46 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A big-data analytics workload runs on Amazon EFS mounted concurrently across hundreds of EC2 instances performing highly parallelized, high-throughput I/O. The default file system configuration is causing throughput bottlenecks under this heavy concurrent load. Select two configuration changes that would improve performance for this specific highly parallel workload.
**Options:**
A. Switch the Performance Mode to Max I/O for higher aggregate throughput and IOPS at slightly higher per-operation latency
B. Switch the Throughput Mode to Elastic (or Provisioned) to decouple throughput from the amount of data stored
C. Switch the storage class to One Zone-IA for faster reads
D. Switch the Performance Mode to General Purpose for the lowest per-operation latency under high parallelism
E. Convert the file system to use EFS Infrequent Access exclusively

**Correct answer(s):** A, B
**Explanation:** Max I/O mode is designed for workloads with very high levels of parallel access, trading slightly higher per-operation latency for much higher aggregate throughput, and Elastic/Provisioned throughput mode removes the throughput-to-storage-size coupling of Bursting mode. General Purpose mode (D) favors lower latency at lower parallelism and is the opposite of what's needed, while storage class options (C, E) affect cost and durability tiering, not raw throughput scaling.

### Question 47 [Domain: 3] [Type: Single-Answer]
**Scenario:** A latency-sensitive API backed by AWS Lambda experiences noticeable cold-start delays for an infrequently invoked function during sudden traffic spikes at the start of business hours, causing the p99 latency SLA to be violated.
**Options:**
A. Increase the Lambda function's memory allocation only
B. Enable Provisioned Concurrency for the function
C. Convert the function to a Lambda@Edge function
D. Increase the function's reserved concurrency limit only

**Correct answer(s):** B
**Explanation:** Provisioned Concurrency keeps a specified number of execution environments pre-initialized and ready to respond immediately, eliminating cold starts during predictable traffic spikes. Reserved concurrency (D) only caps or guarantees the maximum number of concurrent executions and does nothing to pre-warm environments against cold starts.

### Question 48 [Domain: 3] [Type: Single-Answer]
**Scenario:** A tightly coupled HPC workload using MPI requires the lowest possible network latency and highest throughput between EC2 instances, with all instances located within a single Availability Zone, and the team accepts the increased risk of correlated hardware failure this creates.
**Options:**
A. Spread placement group
B. Partition placement group
C. Cluster placement group
D. Default (no placement group)

**Correct answer(s):** C
**Explanation:** Cluster placement groups pack instances close together within a single AZ on the same underlying hardware, minimizing network latency and maximizing throughput — ideal for tightly coupled HPC/MPI workloads. Spread placement groups instead maximize fault isolation by keeping instances on distinct hardware, which increases latency and doesn't fit this use case.

### Question 49 [Domain: 3] [Type: Single-Answer]
**Scenario:** A financial services firm requires consistent, predictable sub-10ms network latency and dedicated 10 Gbps bandwidth between its on-premises data center and a VPC for a low-latency trading application. Encryption of data in transit is a secondary concern compared to latency consistency.
**Options:**
A. AWS Site-to-Site VPN over the public internet
B. AWS Direct Connect
C. VPC Peering
D. Transit Gateway routed through a NAT gateway to the internet

**Correct answer(s):** B
**Explanation:** Direct Connect provides a dedicated, private physical network connection with consistent, predictable latency and guaranteed bandwidth, unaffected by public internet congestion. Site-to-Site VPN (A) traverses the public internet, making it unable to guarantee consistent low latency or dedicated bandwidth.

### Question 50 [Domain: 3] [Type: Single-Answer]
**Scenario:** A REST API backed by AWS Lambda serves largely repeated read-only GET requests for a product catalog that changes only a few times per day. The team wants to reduce backend Lambda invocations and response latency without requiring any client-side changes.
**Options:**
A. Enable API Gateway response caching with a TTL matched to the data's change frequency
B. Increase the Lambda function's reserved concurrency
C. Convert the REST API to a WebSocket API
D. Place an Application Load Balancer in front of API Gateway

**Correct answer(s):** A
**Explanation:** API Gateway caching stores responses at the API Gateway layer for a configurable TTL, serving repeated identical requests directly from the cache and reducing both backend invocations and latency, with zero client-side changes. Increasing concurrency (B) only helps Lambda handle more simultaneous invocations but does nothing to reduce redundant invocations for identical data.

### Question 51 [Domain: 3] [Type: Single-Answer]
**Scenario:** EC2 instances in a private subnet with no NAT gateway or internet gateway need low-latency, high-throughput access to Amazon S3 and DynamoDB without traversing the public internet, and the team wants to avoid any additional hourly endpoint charges.
**Options:**
A. An Interface VPC endpoint (AWS PrivateLink) for both services
B. A Gateway VPC endpoint for both S3 and DynamoDB
C. A NAT Gateway with a route to an internet gateway
D. VPC Peering to a shared-services VPC that has internet access

**Correct answer(s):** B
**Explanation:** S3 and DynamoDB both support Gateway VPC endpoints, which route traffic via a prefix list entry in the route table at no hourly or per-GB charge, and keep traffic entirely on the AWS network. Interface endpoints (A) do work for many services but incur hourly and data processing charges and aren't necessary since Gateway endpoints are supported and free for these two specific services.

### Question 52 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A team is redesigning storage for a self-managed NoSQL database cluster on EC2 that requires extremely high random IOPS (500,000+) with very low latency. The application replicates data across multiple cluster nodes itself, so the loss of a single node's local data on stop/terminate is acceptable. Select two storage options well suited to this specific workload.
**Options:**
A. EBS gp3 volumes at baseline 3,000 IOPS
B. EC2 instance store (NVMe SSD) for maximum local IOPS and lowest latency
C. EBS io2 Block Express volumes for guaranteed high IOPS with volume-level durability
D. Amazon S3 Standard for direct database file storage
E. Amazon EFS with Bursting throughput mode

**Correct answer(s):** B, C
**Explanation:** Instance store delivers the highest possible IOPS and lowest latency since it's physically attached to the host — acceptable here because the application already handles durability via cross-node replication — while io2 Block Express is the right choice when guaranteed high IOPS with volume-level durability is required. gp3's baseline IOPS (A) is far too low for this requirement, and S3/EFS (D, E) are not designed for low-latency block-level database storage.

### Question 53 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A global retail web application built on ALB, EC2 Auto Scaling, and RDS is experiencing high read latency for users located far from the primary region, and repeated identical database queries for popular product pages are overloading the database during flash sales. Select two changes that would most directly address these specific performance issues.
**Options:**
A. Add Amazon CloudFront in front of the application to cache static and cacheable dynamic content closer to global users
B. Add ElastiCache in front of RDS to cache frequently repeated read query results
C. Increase the RDS instance's allocated storage size
D. Replace the Application Load Balancer with a Network Load Balancer
E. Enable S3 Versioning on the application's static asset bucket

**Correct answer(s):** A, B
**Explanation:** CloudFront reduces latency for geographically distant users by serving cacheable content from edge locations, and ElastiCache offloads repeated, identical read queries from RDS during traffic spikes. Increasing RDS storage size (C) doesn't improve query latency or IOPS, and switching to an NLB (D) would sacrifice needed Layer 7 features while doing nothing to address caching or database load.

### Question 54 [Domain: 4] [Type: Single-Answer]
**Scenario:** A media company runs nightly video-transcoding batch jobs that take about 6 hours, checkpoint progress every few minutes, and can tolerate being interrupted and resumed later. The workload currently runs on On-Demand EC2 instances, costing roughly $50,000/month. Leadership wants to cut compute costs by up to 90% and is not willing to make a multi-year financial commitment.
**Options:**
A. Purchase 3-year All Upfront Reserved Instances for the transcoding fleet
B. Migrate the transcoding jobs to Spot Instances using an EC2 Auto Scaling group spanning multiple instance types and Availability Zones
C. Purchase a 3-year Compute Savings Plan sized to current usage
D. Move the workload to On-Demand Capacity Reservations

**Correct answer(s):** B
**Explanation:** Spot Instances offer up to 90% savings versus On-Demand and are ideal for fault-tolerant, checkpointed, interruptible batch jobs; diversifying across instance types/AZs via Auto Scaling minimizes interruption impact and improves capacity availability. Reserved Instances and Savings Plans require long-term financial commitments the team wants to avoid and don't discount as deeply as Spot for this workload; Capacity Reservations cost the same as On-Demand and add no savings.

### Question 55 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs a steady-state fleet of m5 EC2 instances 24/7 and plans to increasingly adopt Fargate and Lambda over the next three years. It wants to commit to a 3-year hourly spend to maximize discount, but wants the freedom to shift spend across EC2 instance families, sizes, operating systems, tenancy, and eventually onto Fargate/Lambda without losing the discount.
**Options:**
A. Standard Reserved Instances (3-year, All Upfront)
B. Convertible Reserved Instances (3-year)
C. Compute Savings Plans (3-year)
D. Scheduled Reserved Instances

**Correct answer(s):** C
**Explanation:** Compute Savings Plans automatically apply to any EC2 instance family/size/OS/tenancy/region and also to Fargate and Lambda usage, giving maximum flexibility while retaining near-RI-level discounts. Convertible RIs allow instance-family changes but only cover EC2, not Fargate or Lambda, making them less flexible for this roadmap.

### Question 56 [Domain: 4] [Type: Single-Answer]
**Scenario:** A financial services firm must retain audit log objects in S3 for 7 years. Logs are occasionally accessed in the first 30 days, rarely accessed between day 30 and day 90, and after 90 days are almost never accessed but must be retrievable within about 12 hours if regulators request them. The firm wants to minimize storage cost over the full retention period while meeting the retrieval SLA.
**Options:**
A. Transition objects to S3 Standard-IA at 0 days, then to S3 Glacier Deep Archive at 90 days, and expire at 7 years
B. Transition objects to S3 Standard-IA at 30 days, then to S3 Glacier Flexible Retrieval at 90 days, and expire at 7 years
C. Transition objects directly to S3 Glacier Deep Archive at 30 days, and expire at 7 years
D. Keep all objects in S3 Standard for the full 7 years, then expire them

**Correct answer(s):** B
**Explanation:** Standard is appropriate for the occasionally-accessed first 30 days (and S3 does not allow transitioning objects to Standard-IA/One Zone-IA before they have spent a minimum of 30 days in Standard, which rules out Option A's day-0 transition). Standard-IA then correctly covers the rarely-accessed 30–90 day window at a lower storage cost than Standard while keeping millisecond, no-extra-wait access. At day 90, moving to Glacier Flexible Retrieval is the lowest-cost class whose Standard retrieval tier (3–5 hours) comfortably and safely meets the 12-hour regulator SLA for the almost-never-accessed tail. Option C skips the Standard-IA tier entirely and pushes data straight into Glacier Deep Archive at day 30, which is too aggressive: it exposes the "rarely accessed" 30–90 day objects to Deep Archive's much slower retrieval (up to 12 hours on the Standard tier, 48 hours on Bulk, with no expedited option) at a point when they may still need reasonably prompt access — the storage savings aren't worth that risk so early in the object's life.

### Question 57 [Domain: 4] [Type: Single-Answer]
**Scenario:** A SaaS company stores user-uploaded files whose access patterns are unpredictable and change over time — some files are hot for a few weeks then go cold indefinitely, others are accessed sporadically with no clear pattern. The small platform team has no time to design or maintain custom lifecycle transition rules and wants storage costs optimized automatically without adding retrieval latency for objects that are still actively accessed.
**Options:**
A. Store all objects in S3 Standard-IA
B. Enable S3 Intelligent-Tiering on the bucket
C. Store all objects in S3 One Zone-IA
D. Tag objects by access date and run a nightly Lambda function to move them between storage classes

**Correct answer(s):** B
**Explanation:** S3 Intelligent-Tiering automatically monitors access patterns and moves objects between frequent, infrequent, and archive access tiers with no retrieval fees or performance impact for the frequent/infrequent tiers, exactly matching unpredictable access patterns with zero operational overhead. S3 Standard-IA charges a per-GB retrieval fee, which would penalize objects that turn out to still be accessed frequently.

### Question 58 [Domain: 4] [Type: Single-Answer]
**Scenario:** A startup is launching a new mobile app whose traffic pattern is completely unknown and could spike unpredictably if the app goes viral. The engineering team wants to avoid throttling and does not want to spend time on capacity planning during launch; they plan to revisit capacity mode once traffic patterns stabilize over the following months.
**Options:**
A. Provisioned capacity with a manually set high fixed throughput
B. Provisioned capacity with Application Auto Scaling configured between low and high thresholds
C. DynamoDB On-Demand capacity mode
D. Purchase upfront provisioned throughput reservations sized for peak traffic

**Correct answer(s):** C
**Explanation:** On-Demand mode instantly accommodates unpredictable, spiky traffic with no capacity planning and per-request billing, which is exactly what an unknown viral launch pattern requires. Provisioned mode with Auto Scaling still reacts to load with a delay, risking throttling during a sudden traffic surge before scaling catches up.

### Question 59 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A logging platform's DynamoDB tables receive predictable, steady write throughput and have grown to multi-terabyte size, but only about 5% of items are ever read again after 30 days. The tables currently run in On-Demand mode, and the team wants to reduce both throughput costs and storage costs given the predictable traffic and mostly-cold data. (Select TWO.)
**Options:**
A. Switch the tables from On-Demand to Provisioned capacity mode with Application Auto Scaling enabled
B. Change the table class to DynamoDB Standard-Infrequent Access (Standard-IA)
C. Enable DynamoDB Accelerator (DAX) in front of the tables
D. Enable point-in-time recovery (PITR) on the tables
E. Convert the tables into DynamoDB global tables replicated to two additional Regions

**Correct answer(s):** A, B
**Explanation:** Provisioned mode with Auto Scaling is cheaper than On-Demand for steady, predictable traffic, and the Standard-IA table class lowers storage costs (with a throughput price trade-off) for tables where most data is infrequently accessed. DAX improves read latency but adds cluster cost rather than reducing it, and PITR and global tables both increase cost rather than optimize it.

### Question 60 [Domain: 4] [Type: Single-Answer]
**Scenario:** EC2 instances in a private subnet need outbound access only to Amazon S3 and DynamoDB in the same Region. All of that traffic currently routes through a NAT Gateway, and the team has noticed significant NAT Gateway data processing charges on the monthly bill. They want to eliminate this cost for S3/DynamoDB traffic specifically without changing the instances' network isolation.
**Options:**
A. Replace the NAT Gateway with a self-managed NAT instance
B. Create Gateway VPC Endpoints for S3 and DynamoDB and update the route table
C. Create Interface VPC Endpoints (AWS PrivateLink) for S3 and DynamoDB
D. Request an increase to the NAT Gateway's bandwidth quota

**Correct answer(s):** B
**Explanation:** Gateway VPC Endpoints for S3 and DynamoDB have no hourly charge and no data processing charge, and routing this traffic through them removes it from the NAT Gateway entirely, directly cutting cost. Interface Endpoints do incur hourly and per-GB data processing charges, making them more expensive than Gateway Endpoints for these two specific services.

### Question 61 [Domain: 4] [Type: Single-Answer]
**Scenario:** A three-tier application is deployed across three Availability Zones, with a backend microservice replicated in each AZ. Frontend app servers call the microservice frequently, and the billing team has flagged unexpectedly high inter-AZ data transfer charges. The team wants to reduce this cost without reducing the application's multi-AZ availability.
**Options:**
A. Consolidate all application tiers into a single Availability Zone
B. Configure app servers to preferentially call the microservice replica running in their own AZ, using zonal-affinity routing
C. Deploy a NAT Gateway in every Availability Zone
D. Enable S3 Transfer Acceleration for traffic between the application tiers

**Correct answer(s):** B
**Explanation:** Routing requests to a same-AZ replica avoids the inter-AZ data transfer charge on that traffic while still keeping replicas in every AZ for availability. Consolidating into a single AZ would also eliminate the charge but at the cost of losing multi-AZ resilience, violating the stated requirement.

### Question 62 [Domain: 4] [Type: Single-Answer]
**Scenario:** An internal reporting database is used heavily during business hours on weekdays but sits nearly idle nights and weekends, averaging roughly 40% overall utilization. It currently runs on a provisioned db.r5.xlarge RDS instance around the clock. The team wants costs to track actual usage without building custom start/stop automation.
**Options:**
A. Purchase a 1-year All Upfront Reserved Instance for the db.r5.xlarge instance
B. Migrate the database to Aurora Serverless v2 and configure Auto Scaling with a low minimum capacity
C. Manually stop and start the RDS instance every day using a scheduled script
D. Run the database on RDS using EC2 Spot Instances

**Correct answer(s):** B
**Explanation:** Aurora Serverless v2 automatically scales capacity up and down (down to a very low minimum ACU) based on actual load, so cost tracks the intermittent usage pattern without manual scheduling logic. A Reserved Instance still bills for 24/7 capacity regardless of the idle nights and weekends, and RDS does not offer a Spot pricing option.

### Question 63 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company has grown organically to hundreds of EC2 instances, EBS volumes, Lambda functions, and Auto Scaling groups. The infrastructure team suspects many resources are over-provisioned but has no hard data to justify resizing them. They want automated, ML-driven recommendations based on actual historical CloudWatch utilization across all of these resource types.
**Options:**
A. AWS Trusted Advisor cost optimization checks
B. AWS Compute Optimizer
C. AWS Cost Explorer rightsizing recommendations
D. Amazon CloudWatch dashboards

**Correct answer(s):** B
**Explanation:** AWS Compute Optimizer analyzes historical CloudWatch metrics with machine learning to produce detailed rightsizing recommendations across EC2, EBS, Lambda, and Auto Scaling groups. Cost Explorer's rightsizing recommendations cover EC2 only, and Trusted Advisor's low-utilization checks are more limited in scope and depth, so neither matches the breadth Compute Optimizer provides.

### Question 64 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A media startup serves images and video directly from a single S3 bucket in us-east-1 to end users worldwide. The bill shows high data transfer OUT charges from S3 to the internet, and users in Asia and Europe report slow load times. The company wants to reduce data transfer costs and improve global performance without duplicating content management overhead. (Select TWO.)
**Options:**
A. Put Amazon CloudFront in front of the S3 bucket as its origin
B. Configure CloudFront with Origin Access Control (OAC) and make the S3 bucket private so it is only reachable through CloudFront
C. Enable S3 Transfer Acceleration for all content downloads
D. Use S3 Cross-Region Replication to copy the bucket into every AWS Region
E. Request an increase to the S3 bucket's provisioned request rate

**Correct answer(s):** A, B
**Explanation:** Fronting the bucket with CloudFront caches content at edge locations worldwide, reducing both latency for distant users and the volume of expensive data transfer OUT directly from S3, and OAC plus a private bucket is the recommended secure pattern that ensures all traffic (and its cost benefit) flows through CloudFront rather than bypassing it via direct S3 requests. Transfer Acceleration is designed to speed up uploads into S3 over long distances, not global content delivery to readers, and Cross-Region Replication multiplies storage cost across regions without providing edge caching; S3 also has no "provisioned request rate" setting to increase.

### Question 65 [Domain: 4] [Type: Single-Answer]
**Scenario:** An enterprise transfers approximately 50TB per month between its on-premises data center and AWS. It currently uses a Site-to-Site VPN over the public internet, resulting in high data transfer charges and inconsistent latency. The company is willing to commit to a dedicated network connection to reduce the total cost of ownership for this steady, high-volume, long-term data transfer need.
**Options:**
A. Keep the Site-to-Site VPN and add a second tunnel purely for redundancy
B. Provision an AWS Direct Connect dedicated connection with a private virtual interface
C. Place AWS Global Accelerator between the on-premises network and AWS
D. File a support ticket to increase the VPN Gateway's bandwidth quota

**Correct answer(s):** B
**Explanation:** Direct Connect offers lower, more predictable per-GB data transfer rates than internet-based VPN transfer for sustained high-volume traffic, plus consistent latency and dedicated bandwidth, making it the most cost-effective choice at this volume. Global Accelerator optimizes routing for end-user traffic into AWS over the AWS global network using Anycast IPs; it is not a mechanism for private on-premises-to-AWS connectivity or for reducing this kind of data transfer cost.
