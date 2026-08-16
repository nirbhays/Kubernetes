# AWS SAA-C03 Mock Exam 3

*Difficulty: Realistic level with difficult distractors.*

These are 65 original practice questions (not real or leaked exam content). Each question is self-contained with its correct answer(s) and explanation inline — no separate answer key is needed.

---

### Question 1 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company's security team wants to ensure that a developer, who has an IAM policy granting `iam:*` permissions for delegated administration, cannot escalate their own privileges beyond a defined set of permissions no matter what policies they attach to themselves. The team wants a hard ceiling on the developer's effective permissions that cannot be bypassed even if the developer creates new IAM policies. Which mechanism should be used?

**Options:**
A. Attach a Service Control Policy (SCP) directly to the developer's IAM user
B. Set a permissions boundary on the developer's IAM user
C. Create a resource-based policy on every resource the developer can access
D. Add a deny statement to the developer's existing identity-based policy

**Correct answer(s):** B
**Explanation:** A permissions boundary is a managed policy attached to an IAM user or role that sets the maximum permissions that identity can ever have, regardless of what identity-based policies are later attached — perfect for constraining a delegated admin. SCPs (option A) are attached to AWS Organizations accounts/OUs, not to individual IAM principals, so this is the most tempting but incorrect distractor.

### Question 2 [Domain: 1] [Type: Single-Answer]
**Scenario:** A financial services company encrypts objects in S3 using an AWS KMS customer managed key (CMK). An external auditor, who has an IAM role with `kms:Decrypt` and `s3:GetObject` permissions granted via an identity-based policy, still cannot decrypt the objects. The KMS key was created by the security team using the default key policy behavior disabled (i.e., no statement granting account-wide IAM permissions).
**Options:**
A. The auditor's IAM role needs `kms:*` instead of `kms:Decrypt`
B. The KMS key policy must also explicitly grant the auditor's role permission to use the key
C. S3 bucket policies always override KMS permissions
D. KMS keys cannot be used with IAM roles, only IAM users

**Correct answer(s):** B
**Explanation:** For a customer managed KMS key, both the key policy AND the IAM identity policy must grant access — an IAM policy alone is insufficient unless the key policy delegates permission management to IAM. Option A is a tempting distractor since it looks like a permissions issue, but broadening the IAM action doesn't help because the key policy is the missing piece.

### Question 3 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company stores a database credential in AWS Secrets Manager and needs the credential to be automatically rotated every 30 days without any application downtime, using a Lambda function that AWS Secrets Manager manages. The database is Amazon RDS for MySQL. Which approach requires the least custom implementation effort?

**Options:**
A. Write a custom Lambda rotation function from scratch and schedule it with Amazon EventBridge
B. Use one of the AWS-provided Secrets Manager rotation function templates for RDS credential rotation and enable automatic rotation
C. Store the credential in Systems Manager Parameter Store with a SecureString type and rotate it manually every 30 days
D. Use IAM database authentication instead of storing a credential at all

**Correct answer(s):** B
**Explanation:** Secrets Manager provides prebuilt Lambda rotation function templates for RDS (including MySQL) that implement the four-step rotation strategy (createSecret, setSecret, testSecret, finishSecret) with no application downtime, requiring only deployment and enabling rotation. Option D is a plausible alternative in real design discussions, but it changes the architecture entirely rather than satisfying the stated requirement of rotating a stored credential.

### Question 4 [Domain: 1] [Type: Single-Answer]
**Scenario:** A three-tier application runs in a VPC with public subnets for the load balancer and private subnets for application servers. Traffic must flow from the internet, through the ALB, to EC2 instances on port 8080, and instances must be able to make outbound HTTPS calls to third-party APIs. The security team wants the EC2 instances' inbound rules to allow traffic only from the ALB's security group, without needing to know the ALB's IP addresses.

**Options:**
A. Create an inbound rule on the EC2 security group referencing the ALB's security group ID as the source, on port 8080
B. Create an inbound NACL rule on the private subnet referencing the ALB's security group ID
C. Create an inbound rule on the EC2 security group allowing the ALB's public subnet CIDR range on port 8080
D. Create an outbound rule on the ALB security group only, since security groups are stateless

**Correct answer(s):** A
**Explanation:** Security groups support referencing another security group as the source/destination, which dynamically includes any ENI associated with that group regardless of IP changes — ideal for ALB-to-EC2 traffic. Option C is a very plausible distractor since CIDR-based rules also work, but it fails if the ALB scales into new subnets or its subnet IP ranges change, and it doesn't match the requirement of avoiding IP dependency; also NACLs (option B) cannot reference security group IDs at all.

### Question 5 [Domain: 1] [Type: Single-Answer]
**Scenario:** An application behind an Application Load Balancer is experiencing a Layer 7 DDoS-style attack where a single IP address is sending an abnormally high volume of HTTP requests per five-minute period, degrading performance for legitimate users. The security team wants to automatically block IPs that exceed a request threshold, while still allowing normal traffic through.

**Options:**
A. Create a Network ACL rule to deny the attacking IP range
B. Attach an AWS WAF Web ACL to the ALB with a rate-based rule
C. Enable AWS Shield Advanced, which automatically blocks all high-volume IPs by default
D. Configure the ALB security group to deny traffic from any IP exceeding 100 requests/second

**Correct answer(s):** B
**Explanation:** AWS WAF rate-based rules track the request rate from individual IP addresses over a rolling 5-minute window and can automatically block IPs that exceed a defined threshold, which directly matches the requirement. Shield Advanced (option C) helps with DDoS mitigation and cost protection but does not automatically rate-limit by IP out of the box — it typically works together with WAF rate-based rules, making it a tempting but incorrect standalone answer.

### Question 6 [Domain: 1] [Type: Multiple-Response]
**Scenario:** Amazon GuardDuty has generated a finding of type `UnauthorizedAccess:EC2/TorIPCaller` and another of type `CryptoCurrency:EC2/BitcoinTool.B!DNS` for an EC2 instance in the production account. The security team needs to both contain the immediate threat and improve future detection. (Select TWO.)

**Options:**
A. Isolate the affected EC2 instance by moving it to a restrictive security group and taking a forensic snapshot before further investigation
B. Immediately terminate the AWS account root user credentials
C. Enable GuardDuty's EKS Protection feature, which will automatically remediate any EC2-related findings
D. Review the instance's IAM role and rotate any credentials that may have been compromised
E. Disable GuardDuty to stop further alert noise while investigating

**Correct answer(s):** A, D
**Explanation:** Isolating the compromised instance (preserving evidence via snapshot) and rotating any potentially exposed credentials are standard incident response steps for a compromised EC2 instance flagged for Tor traffic and cryptomining activity. Option C is a tempting distractor because EKS Protection sounds related to threat detection, but it targets EKS clusters specifically and GuardDuty does not auto-remediate findings of any kind.

### Question 7 [Domain: 1] [Type: Single-Answer]
**Scenario:** A mobile application needs to let users sign in using their existing Google and Facebook accounts, and after authentication the app needs to obtain temporary AWS credentials to upload photos directly to an S3 bucket. Which combination of Cognito components should be used?

**Options:**
A. Cognito User Pool only, using its built-in credentials to call S3 APIs directly
B. Cognito Identity Pool only, configured with Google and Facebook as SAML providers
C. Cognito User Pool for authentication federation with Google/Facebook, combined with a Cognito Identity Pool to exchange the resulting tokens for temporary IAM credentials
D. IAM Identity Center configured with Google and Facebook as external identity providers

**Correct answer(s):** C
**Explanation:** Cognito User Pools handle user authentication and can federate with social identity providers like Google and Facebook, while Cognito Identity Pools exchange the resulting identity tokens for temporary AWS credentials via STS to access services like S3. Option B is a plausible-sounding distractor, but Identity Pools consume OIDC tokens from social providers (or User Pools), not SAML, and using them alone skips the authentication/user-management layer entirely.

### Question 8 [Domain: 1] [Type: Single-Answer]
**Scenario:** Company A has an S3 bucket in Account 111111111111 containing shared analytics data. Company B's data science team, in Account 222222222222, needs read-only access to specific objects in that bucket using their own IAM roles, without creating any IAM users in Account A. Which approach is the AWS-recommended way to grant this cross-account access?

**Options:**
A. Create an IAM user in Account A, generate access keys, and share them with Account B's team
B. Add a bucket policy in Account A granting `s3:GetObject` to the specific IAM role ARN in Account B, and ensure Account B's role has a policy allowing the S3 actions
C. Make the S3 bucket public and rely on a strong, hard-to-guess bucket name for security
D. Create an IAM group in Account B and add cross-account trust to Account A's root user

**Correct answer(s):** B
**Explanation:** Cross-account S3 access is properly granted using a resource-based bucket policy in the owning account that references the specific principal ARN in the trusted account, combined with a permissions policy in the trusted account — both sides must allow the action. Option A directly contradicts the stated requirement of not creating IAM users in Account A, and it also relies on long-lived shared credentials, a well-known anti-pattern compared to the resource-policy approach.

### Question 9 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A security engineer is designing a KMS key policy for a customer managed key that will be used to encrypt data across two AWS accounts: Account A (key owner) and Account B (needs to use the key for encrypt/decrypt operations from an application role). The engineer wants to follow least-privilege and AWS best practices. (Select TWO.)

**Options:**
A. In Account A's key policy, grant `kms:*` to Account B's root user (instead of the specific application role) so any principal in Account B can use the key without further configuration
B. In Account A's key policy, add a statement granting `kms:Encrypt` and `kms:Decrypt` to the specific IAM role ARN in Account B
C. In Account B, create an IAM policy on the application role allowing the same `kms:Encrypt`/`kms:Decrypt` actions on the key's ARN
D. Share the KMS key's private key material with Account B so it can perform encryption locally
E. Rely solely on the key policy in Account A; no IAM policy is needed in Account B

**Correct answer(s):** B, C
**Explanation:** Cross-account KMS access requires the key policy in the owning account to grant the external account's specific principal permission for the exact actions needed, AND the external account must have an IAM policy granting that principal the same permission — both are required. Option A is a tempting distractor because granting broad access to an entire account's root is a common shortcut, but it violates least privilege by exposing the key to every principal in Account B and by granting unrestricted `kms:*` instead of only the needed Encrypt/Decrypt actions. Option E is incorrect because cross-account access always requires an explicit IAM policy in the calling account as well; option D is invalid since KMS never exports key material for symmetric CMKs.

### Question 10 [Domain: 1] [Type: Single-Answer]
**Scenario:** A large enterprise uses AWS Organizations with dozens of member accounts. The security team wants to prevent any account in the "Sandbox" OU from ever disabling AWS CloudTrail or leaving the AWS Organization, even if an account administrator has full `AdministratorAccess` in that account. What should they implement?

**Options:**
A. An IAM permissions boundary applied to every user and role in the Sandbox accounts
B. A Service Control Policy attached to the Sandbox OU that denies `cloudtrail:StopLogging`, `cloudtrail:DeleteTrail`, and `organizations:LeaveOrganization`
C. A resource-based policy on the CloudTrail trail denying stop/delete actions
D. An AWS Config rule that flags but does not prevent these actions

**Correct answer(s):** B
**Explanation:** SCPs applied at the OU level set the maximum permissions for all accounts in that OU, and an explicit Deny in an SCP overrides even `AdministratorAccess`, making it the correct guardrail for this multi-account requirement. Option A is a tempting distractor because permissions boundaries also cap permissions, but they must be applied individually to each principal and can be modified by a full admin within the account, so they can't reliably guarantee an organization-wide, un-bypassable restriction.

### Question 11 [Domain: 1] [Type: Multiple-Response]
**Scenario:** An architect is deciding between AWS Secrets Manager and Systems Manager Parameter Store for storing sensitive configuration values across an application. Which statements accurately describe key differences between the two services? (Select TWO.)

**Options:**
A. Secrets Manager supports built-in automatic rotation with Lambda functions for supported databases; Parameter Store does not have this native capability
B. Parameter Store Standard tier parameters are free, while Secrets Manager charges per secret per month plus API call charges
C. Parameter Store encrypts all parameters with KMS by default, even String type parameters
D. Secrets Manager cannot be accessed using IAM policies, only resource policies
E. Parameter Store SecureString parameters cannot be referenced from ECS task definitions

**Correct answer(s):** A, B
**Explanation:** Secrets Manager's native automatic rotation with Lambda and its higher cost structure compared to Parameter Store Standard's free tier are well-documented, real differentiators between the two services. Option C is a tempting distractor because SecureString parameters are KMS-encrypted, but plain String type parameters are stored unencrypted, so "all parameters" is incorrect. Option E is also false — ECS task definitions can reference SecureString parameters from Parameter Store as secrets.

### Question 12 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company's network team notices that an EC2 instance in a private subnet is intermittently unable to complete outbound HTTPS connections to an external API, even though the security group has an outbound rule allowing this traffic (and, since security groups are stateful, the return traffic is automatically permitted). The subnet's Network ACL has a rule allowing outbound TCP 443 but the team suspects the issue lies in the NACL configuration for return traffic. What is the most likely cause?

**Options:**
A. The NACL is missing an inbound rule allowing the ephemeral port range (1024-65535) for return traffic
B. Security groups do not support outbound HTTPS traffic to the internet
C. The NACL's outbound rule for port 443 is being evaluated in the wrong order
D. NAT Gateway does not support NACLs, so ephemeral ports don't apply

**Correct answer(s):** A
**Explanation:** Because NACLs are stateless, return traffic from an external server (originating on a random ephemeral port back to the instance) must be explicitly allowed by an inbound rule covering the ephemeral port range, unlike security groups which automatically allow return traffic. Option C is a tempting distractor because NACL rule order does matter, but the scenario describes intermittent failure typical of a missing ephemeral-port rule rather than a rule-ordering conflict.

### Question 13 [Domain: 1] [Type: Single-Answer]
**Scenario:** A web application has recently been the target of SQL injection attempts identified in ALB access logs. The security team wants to block these malicious requests before they reach the application, with minimal custom rule-writing effort, while continuing to allow legitimate traffic.

**Options:**
A. Add a NACL rule blocking all traffic containing the string "SELECT" or "UNION"
B. Associate an AWS WAF Web ACL with the ALB and enable the AWS Managed Rules "SQL Database" rule group
C. Configure the ALB listener to reject any request with a query string longer than 200 characters
D. Enable GuardDuty S3 Protection to inspect and block SQL injection payloads

**Correct answer(s):** B
**Explanation:** AWS WAF's managed rule groups, including the SQL Database rule group, provide preconfigured protection against common SQL injection patterns without requiring custom rule authoring, and can be attached directly to an ALB. Option D is a clearly irrelevant but tempting-sounding distractor since GuardDuty is a threat detection service focused on account/workload activity, not an inline web traffic filter, and S3 Protection specifically analyzes S3 data events, not HTTP payloads to an ALB.

### Question 14 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company operates a multi-account AWS environment managed through AWS Organizations. The security team wants a single, centralized view of GuardDuty findings across all 40 member accounts without having to log into each account individually, and wants new accounts added to the organization to be automatically enrolled in GuardDuty monitoring.

**Options:**
A. Manually enable GuardDuty in each account and email findings to a shared distribution list
B. Designate a delegated GuardDuty administrator account, enable it for the organization, and configure auto-enable for new accounts
C. Use AWS Config aggregators to collect GuardDuty findings from all accounts into one dashboard
D. Create a cross-account IAM role in each account that the security team assumes to check GuardDuty findings individually

**Correct answer(s):** B
**Explanation:** GuardDuty supports a delegated administrator account model within AWS Organizations, allowing centralized visibility of findings across all member accounts and automatic enrollment of new accounts when auto-enable is configured. Option D is a tempting distractor because assuming roles is a legitimate cross-account pattern, but it still requires manually checking each account rather than providing the required centralized, automated view.

### Question 15 [Domain: 1] [Type: Single-Answer]
**Scenario:** An enterprise customer wants their employees to sign in to a custom web application using their existing corporate Active Directory Federation Services (AD FS) credentials via SAML 2.0, and after authentication, the application should receive temporary AWS credentials scoped to specific S3 prefixes matching each employee's department. Which service combination best fits this requirement?

**Options:**
A. Cognito User Pools configured with a SAML identity provider, federated to a Cognito Identity Pool with IAM roles mapped via custom attributes
B. IAM users created for each employee with policies scoped by department
C. AWS Directory Service (Simple AD) integrated directly with S3 bucket policies
D. Amazon Cognito Sync to replicate department-based access rules to each client device

**Correct answer(s):** A
**Explanation:** Cognito User Pools can federate with SAML 2.0 identity providers like AD FS, and a linked Cognito Identity Pool can map authenticated users to IAM roles (including using custom attributes/claims for fine-grained, per-department access) to issue scoped temporary credentials. Option B is a tempting but poor-practice distractor since creating individual IAM users for every employee doesn't scale and abandons federation entirely, violating the requirement to use existing AD FS credentials.

### Question 16 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A SaaS provider needs to allow each of its enterprise customers (each running their own separate AWS account) to grant the provider's central AWS account read-only access to specific resources in the customer's account, without the customer ever sharing long-term credentials. The design must also allow each customer to independently revoke access at any time. (Select TWO.)

**Options:**
A. Have each customer create an IAM role in their account with a trust policy allowing the provider's specific AWS account ID (and ideally an External ID) to assume it
B. Have each customer share their AWS account root user password with the provider
C. Attach a read-only permissions policy to the cross-account role, scoped to only the required resources
D. Have the provider create IAM users in each customer account using the customer's root credentials
E. Ask each customer to disable MFA on their root account so the provider's automation can log in directly

**Correct answer(s):** A, C
**Explanation:** The standard secure cross-account access pattern is a customer-owned IAM role with a trust policy scoped to the provider's account (plus an External ID to prevent confused-deputy issues) and a tightly scoped permissions policy — this lets the customer revoke access anytime by deleting/modifying the role. Option D is a tempting distractor since it involves IAM, but requiring the customer's root credentials to create users is both insecure and operationally the opposite of least-privilege, temporary access.

### Question 17 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company wants to enforce that IAM users can only perform sensitive actions, such as deleting an S3 bucket or terminating an EC2 instance, when they have authenticated using multi-factor authentication (MFA), regardless of which IAM policy would otherwise allow the action. Which approach achieves this?

**Options:**
A. Enable MFA on the root account only, since IAM user actions inherit root account MFA settings
B. Attach an IAM policy statement with a `Deny` effect on the sensitive actions, using a condition key of `aws:MultiFactorAuthPresent` set to `false`
C. Require MFA at the VPC security group level for API calls
D. Use AWS Config to automatically revoke IAM permissions if MFA is not detected within 24 hours

**Correct answer(s):** B
**Explanation:** Adding a Deny statement conditioned on `aws:MultiFactorAuthPresent: false` is the standard IAM pattern to enforce that sensitive API calls are blocked unless the caller authenticated with MFA, regardless of other Allow statements. Option A is a tempting distractor because root MFA is important, but IAM user permissions and MFA enforcement are entirely independent of the root account's MFA configuration.

### Question 18 [Domain: 1] [Type: Single-Answer]
**Scenario:** A global company operates active-active application deployments in us-east-1 and eu-west-1 and needs to encrypt data with the exact same KMS key material in both regions so that ciphertext encrypted in one region can be decrypted in the other without re-encrypting or calling across regions during normal operation. Which KMS feature satisfies this requirement?

**Options:**
A. Create a single-region KMS key in us-east-1 and grant eu-west-1 resources cross-region access via VPC peering
B. Use AWS KMS multi-Region keys, creating a primary key in one region and replica keys in the other
C. Use AWS Certificate Manager to issue a shared certificate usable in both regions
D. Enable S3 Cross-Region Replication, which automatically re-encrypts objects with region-local keys transparently

**Correct answer(s):** B
**Explanation:** KMS multi-Region keys let you create a primary key and replica keys in different regions that share the same key material and key ID, allowing data encrypted in one region to be decrypted in another without cross-region API calls. Option A is a tempting distractor because VPC peering does enable network connectivity, but standard single-region KMS keys cannot be used for API calls from another region's resources without cross-region calls, and peering doesn't replicate key material at all.

### Question 19 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company's incident response runbook requires that whenever GuardDuty detects an `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` finding, the affected IAM role's credentials should be automatically revoked within minutes, without waiting for manual analyst review, to limit the blast radius. Which architecture achieves this automated response?

**Options:**
A. Configure GuardDuty to email the security team distribution list, who will manually revoke credentials
B. Create an EventBridge rule matching the specific GuardDuty finding type that triggers a Lambda function to attach a deny-all policy or revoke the role's active sessions
C. Enable AWS Config conformance packs to periodically audit and fix IAM role credentials once per day
D. Use CloudTrail Insights to detect the finding and manually rotate keys within 24 hours

**Correct answer(s):** B
**Explanation:** GuardDuty findings are published to EventBridge, so a rule can match the specific finding type and invoke a Lambda function to take immediate automated remediation action, such as revoking active sessions or attaching a restrictive IAM policy — satisfying the "within minutes, no manual review" requirement. Option C is a tempting distractor since AWS Config conformance packs do perform compliance checks, but they operate on a periodic evaluation cycle (not real-time) and are meant for drift detection/remediation, not immediate incident response to a specific security finding.

### Question 20 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A security team is reviewing an EC2-based architecture and wants to reduce the attack surface using layered, defense-in-depth network security controls. The application tier should only accept traffic from the load balancer, database instances should never be reachable from the internet, and any anomalous outbound connections to known malicious IPs should be automatically flagged. (Select TWO.)

**Options:**
A. Place database instances in private subnets with security groups allowing inbound traffic only from the application tier's security group
B. Enable GuardDuty to detect and alert on communication with known malicious IP addresses using threat intelligence feeds
C. Place database instances in public subnets but restrict access using only a complex, non-guessable master password
D. Rely exclusively on IAM policies to prevent network-level access to the database instances
E. Disable VPC Flow Logs to reduce noise and simplify the security review

**Correct answer(s):** A, B
**Explanation:** Placing databases in private subnets with security groups scoped to the application tier enforces network isolation, while GuardDuty's threat intelligence-based detection automatically flags outbound traffic to known malicious IPs, together forming layered defense-in-depth. Option D is a tempting distractor because IAM policies are a critical control plane safeguard, but they do not control network-level (data plane) reachability of a database instance, so they cannot substitute for proper subnet/security group isolation.

### Question 21 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company runs a critical PostgreSQL database on Amazon RDS in a single Availability Zone. During a recent AZ outage, the database was unavailable for over an hour while the team manually restored it from a snapshot. The company wants to minimize downtime for future AZ-level failures with the least amount of application changes and minimal ongoing administrative effort.
**Options:**
A. Convert the RDS instance to a Multi-AZ deployment
B. Create a read replica in a different Availability Zone and manually promote it during outages
C. Migrate the database to Amazon Aurora Serverless v2 in a single AZ
D. Take more frequent manual snapshots and automate the restore script
**Correct answer(s):** A
**Explanation:** Multi-AZ RDS deployments maintain a synchronously replicated standby in another AZ and automatically fail over within about 60-120 seconds, requiring no application changes since the endpoint stays the same. Option B is the tempting distractor because it uses a different AZ, but read replicas use asynchronous replication and require manual intervention and a DNS/endpoint change, resulting in longer downtime and possible data loss.

### Question 22 [Domain: 2] [Type: Single-Answer]
**Scenario:** A gaming company runs a TCP-based multiplayer backend that requires extremely low latency and the ability to preserve client source IP addresses for anti-cheat logging. Traffic volume can spike to millions of packets per second, and the team wants a load balancer that can handle this scale while exposing static IP addresses per Availability Zone.
**Options:**
A. Application Load Balancer with sticky sessions enabled
B. Network Load Balancer
C. Amazon CloudFront with a custom origin
D. Classic Load Balancer with cross-zone load balancing enabled
**Correct answer(s):** B
**Explanation:** Network Load Balancer operates at Layer 4, handles millions of requests per second with ultra-low latency, preserves the source IP address, and provides a static IP per subnet/AZ. The tempting distractor is the Application Load Balancer, but ALB operates at Layer 7 (HTTP/HTTPS), does not natively support raw TCP source IP preservation without proxy protocol workarounds, and is not designed for this packet-rate scale.

### Question 23 [Domain: 2] [Type: Multiple-Response]
**Scenario:** An e-commerce platform needs order events to simultaneously trigger an inventory update Lambda function, a billing SQS queue for asynchronous processing, and a real-time analytics Kinesis Data Firehose stream. The architecture must decouple the order service from all downstream consumers so that adding future consumers requires no changes to the order service itself.
**Options:**
A. Have the order service publish each event directly to every downstream service's API
B. Publish events to an SNS topic and configure each consumer as a subscription (fan-out pattern)
C. Use a single SQS standard queue and have all consumers poll it
D. Use Amazon EventBridge with a custom event bus and rules routing to each target
E. Store events in an S3 bucket and have consumers poll for new objects every second
**Correct answer(s):** B, D
**Explanation:** SNS fan-out lets one publish reach multiple independent subscribers (Lambda, SQS, and even a Kinesis Data Firehose delivery stream) without the producer knowing about consumers, and EventBridge similarly decouples producers from consumers via rule-based routing to multiple targets (including Lambda, SQS, and Firehose) with additional filtering capability. Option C is a tempting distractor since SQS decouples producers from consumers, but a single standard queue only delivers each message to one consumer, so it cannot fan out to three independent downstream systems.

### Question 24 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company hosts its website on two identical fleets of EC2 instances behind separate Application Load Balancers in two different AWS Regions. They want Route 53 to send all traffic to the primary region's ALB, and automatically shift all traffic to the secondary region's ALB only if the primary ALB fails health checks.
**Options:**
A. Weighted routing policy with equal weights on both records
B. Failover routing policy with primary and secondary records
C. Latency-based routing policy across both regions
D. Multi-value answer routing policy with health checks enabled
**Correct answer(s):** B
**Explanation:** Failover routing policy is purpose-built for active-passive DR: Route 53 sends traffic to the primary record while it passes health checks and automatically shifts to the secondary record when the primary fails. Weighted routing is a tempting distractor for traffic splitting, but it does not model an active-passive primary/secondary relationship - it would continue sending some traffic to a failed weighted record unless weights are manually adjusted.

### Question 25 [Domain: 2] [Type: Single-Answer]
**Scenario:** A solutions architect configured a Route 53 health check that monitors an ALB endpoint over HTTPS on port 443 with a specific path. The health check is reporting the endpoint as unhealthy, but when the architect manually browses to the same URL, it loads successfully every time. The ALB's security group currently only allows inbound traffic from the corporate office CIDR range.
**Options:**
A. The health check interval is set too high
B. Route 53 health checkers originate from AWS IP ranges that are not permitted by the ALB's security group
C. The domain's TTL value is too low, causing stale health status
D. Route 53 health checks require the target to be in the same region as the hosted zone
**Correct answer(s):** B
**Explanation:** Route 53 health checkers run from a published set of AWS IP ranges worldwide, and if the security group only allows the corporate CIDR, those checker requests are blocked, causing false "unhealthy" results despite the endpoint working fine for the office. TTL (option C) affects DNS caching by resolvers, not the health check evaluation itself, making it a plausible-sounding but incorrect distractor.

### Question 26 [Domain: 2] [Type: Single-Answer]
**Scenario:** An IoT company ingests telemetry from 500,000 sensors, with data needing to be consumed by three separate applications: a real-time dashboard, a fraud detection engine, and a long-term analytics pipeline, each processing the same records independently and needing to replay data from the last 24 hours if needed. Ordering within each sensor's data stream must be preserved.
**Options:**
A. Amazon SQS FIFO queue with visibility timeout tuning
B. Amazon SQS standard queue with three separate consumers
C. Amazon Kinesis Data Streams with three separate consumer applications using enhanced fan-out
D. Amazon SNS topic with three Lambda subscriptions
**Correct answer(s):** C
**Explanation:** Kinesis Data Streams retains data for a configurable period (up to 24 hours by default, longer with extended retention) allowing multiple independent consumers to read and replay the same records at their own pace while preserving per-shard (per-partition-key) ordering. SQS FIFO is a tempting distractor because it preserves ordering, but a single FIFO message is deleted once processed by one consumer, so it cannot support three independent consumers replaying the same data.

### Question 27 [Domain: 2] [Type: Single-Answer]
**Scenario:** A DevOps team wants to trigger a Lambda function every night at 2 AM UTC to run a database cleanup job, and separately wants to automatically invoke a different Lambda function whenever an EC2 instance changes state to "terminated" anywhere in the account, without writing custom polling code.
**Options:**
A. Use CloudWatch Alarms for both requirements
B. Use Amazon EventBridge scheduled rules for the cron job and an EventBridge rule matching EC2 state-change events for the second requirement
C. Use AWS Step Functions with a wait state for the cron job and SNS for EC2 termination
D. Use an SQS delay queue for the cron job and CloudTrail for EC2 termination
**Correct answer(s):** B
**Explanation:** EventBridge natively supports cron/rate-based scheduled rules and also receives EC2 state-change notifications as native AWS service events, so a single rule with an event pattern matching "terminated" state can invoke the target Lambda without custom polling. CloudWatch Alarms (option A) are designed for metric threshold breaches, not for scheduling jobs or reacting to discrete state-change events, making it an inadequate though plausible-sounding choice.

### Question 28 [Domain: 2] [Type: Multiple-Response]
**Scenario:** An Auto Scaling group backs a stateless web tier that experiences a predictable traffic spike every day at 9 AM and unpredictable spikes throughout the day tied to CPU utilization. The team wants the group to proactively add capacity before the known 9 AM spike and also reactively scale based on real-time CPU load throughout the day.
**Options:**
A. Configure a scheduled scaling action for 9 AM
B. Configure a target tracking scaling policy based on average CPU utilization
C. Configure only a simple scaling policy triggered by a CloudWatch alarm
D. Configure a predictive scaling policy only, and remove all other policies
E. Increase the minimum capacity permanently to cover the daily peak
**Correct answer(s):** A, B
**Explanation:** Scheduled scaling handles the known, predictable 9 AM spike by pre-provisioning capacity at a specific time, while target tracking scaling continuously adjusts capacity to maintain the desired CPU utilization for unpredictable spikes; these two combine well and can coexist. Option E is tempting since it "solves" the daily peak, but permanently raising minimum capacity wastes cost during off-peak hours and does not address unpredictable spikes.

### Question 29 [Domain: 2] [Type: Single-Answer]
**Scenario:** An application running on Auto Scaling group instances needs to download a 2 GB dataset and complete a warm-up script before it can start accepting traffic; instances that skip this step return errors to end users. Currently, newly launched instances are added to the load balancer target group immediately after passing the EC2 status checks, before the warm-up finishes.
**Options:**
A. Increase the Auto Scaling group's health check grace period only
B. Add a lifecycle hook for the "Pending" state to delay the instance from entering "InService" until warm-up completes
C. Reduce the ALB's deregistration delay to zero
D. Configure a longer cooldown period on the Auto Scaling group
**Correct answer(s):** B
**Explanation:** A lifecycle hook on the launch transition puts the instance into a "Pending:Wait" state, holding it out of service until the warm-up script signals completion via CompleteLifecycleAction, ensuring it only joins the target group when ready. The health check grace period (option A) only delays when ASG health checks start being evaluated, but it does not prevent the ALB from routing traffic to the instance during that grace period once it's registered.

### Question 30 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company has an Application Load Balancer with two Availability Zones enabled, but Zone A has 8 registered targets while Zone B has only 2 registered targets due to an uneven Auto Scaling distribution. The team notices the 2 targets in Zone B are receiving disproportionately high traffic per instance compared to Zone A's targets.
**Options:**
A. Disable sticky sessions on the target group
B. Cross-zone load balancing is already enabled by default for ALB and distributes evenly across all targets regardless of AZ, so the issue lies elsewhere
C. Manually rebalance targets by moving instances between subnets
D. Switch to a Network Load Balancer to fix the imbalance automatically
**Correct answer(s):** B
**Explanation:** For Application Load Balancers, cross-zone load balancing is always enabled and cannot be turned off, meaning the ALB distributes requests evenly across all registered targets in all enabled AZs regardless of how many targets are in each zone - so uneven distribution per instance in this scenario would stem from a different cause (e.g., target health or connection draining), not AZ target count. Option D is a tempting distractor because NLB is a valid load balancer type, but NLB has cross-zone load balancing disabled by default, which would actually make this specific imbalance worse, not better.

### Question 31 [Domain: 2] [Type: Single-Answer]
**Scenario:** A payment processing application uses an SQS standard queue to receive transaction messages. Occasionally, a malformed message causes the consumer Lambda function to fail repeatedly, and that message gets redelivered and reprocessed indefinitely, consuming compute resources and delaying other messages behind it in visibility timeout cycles.
**Options:**
A. Reduce the queue's visibility timeout to 0 seconds
B. Configure a dead-letter queue with a maxReceiveCount and redirect failed messages there after repeated failures
C. Enable long polling on the queue
D. Convert the standard queue to a FIFO queue
**Correct answer(s):** B
**Explanation:** A dead-letter queue with a maxReceiveCount automatically moves a message that has failed processing a specified number of times out of the main queue, isolating the poison-pill message so it stops blocking throughput and can be inspected separately. Enabling long polling (option C) reduces empty responses and API costs but has no effect on repeatedly failing message redelivery.

### Question 32 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company is migrating traffic gradually from an old application stack to a new one. They want 90% of DNS resolutions to continue pointing to the old stack's endpoint and 10% to route to the new stack's endpoint, adjusting the split gradually over the following weeks as confidence grows, without using any additional AWS services.
**Options:**
A. Latency-based routing policy
B. Weighted routing policy
C. Geolocation routing policy
D. Multi-value answer routing policy
**Correct answer(s):** B
**Explanation:** Weighted routing lets you assign relative weights to multiple records for the same domain name, controlling the percentage of DNS responses directed to each endpoint, which is exactly suited for a gradual canary-style migration. Latency-based routing (option A) is tempting because it also distributes traffic across records, but it routes based on lowest network latency to the user, not a controllable percentage split.

### Question 33 [Domain: 2] [Type: Single-Answer]
**Scenario:** A financial services firm requires a recovery time objective (RTO) and recovery point objective (RPO) of near-zero for its core trading platform. The business is willing to pay for fully duplicated infrastructure running continuously in two regions, with a global database solution that supports writes accepted in either region and automatic traffic routing away from a failed region.
**Options:**
A. Backup and restore
B. Pilot light
C. Warm standby
D. Multi-region active-active
**Correct answer(s):** D
**Explanation:** Multi-region active-active deployment runs full production capacity in multiple regions simultaneously with data replicated bidirectionally (e.g., via DynamoDB global tables or Aurora Global Database), achieving near-zero RTO/RPO since failover just means redirecting traffic to already-running infrastructure. Warm standby (option C) is a tempting distractor since it also runs infrastructure in a second region, but it runs at reduced capacity that must scale up during failover, resulting in higher RTO than true active-active.

### Question 34 [Domain: 2] [Type: Single-Answer]
**Scenario:** A mid-sized company is designing a disaster recovery strategy for a moderately critical internal reporting application. Leadership has approved a budget that avoids running full duplicate compute in a second region continuously, but wants failover to complete within about 10-15 minutes if the primary region fails, with only core infrastructure components kept running at minimal scale in the DR region.
**Options:**
A. Backup and restore
B. Pilot light
C. Warm standby
D. Multi-region active-active
E. Single-region Multi-AZ only, with no cross-region DR
**Correct answer(s):** B
**Explanation:** Pilot light keeps only the core, hardest-to-rebuild components (typically the database) replicated and running at minimal scale in the DR region, with the rest of the stack launched and scaled up quickly on failover - this matches both the 10-15 minute RTO target and the explicit constraint that only "core infrastructure components" run continuously. Warm standby (option C) is a tempting distractor because it also avoids full-scale duplicate compute, but it requires a scaled-down version of the *entire* application stack (not just core infrastructure) running at all times, which goes beyond what this budget-constrained scenario describes. Backup and restore (option A) is a tempting distractor as a lower-cost DR option, but it typically has an RTO measured in hours, not minutes, since infrastructure must be provisioned from scratch during recovery.

### Question 35 [Domain: 2] [Type: Single-Answer]
**Scenario:** A media company needs an uploaded video file event to simultaneously trigger a transcoding Lambda function, send a notification email to the content team via an existing distribution list, and push a message to a mobile push notification service, all from a single S3 upload event with minimal custom integration code.
**Options:**
A. Configure three separate S3 event notifications, one for each destination type
B. Configure a single S3 event notification to an SNS topic, then subscribe Lambda, email, and a mobile push endpoint to that topic
C. Configure S3 to invoke Lambda directly, and have that Lambda function fan out to email and push notifications
D. Use S3 Event Notifications to SQS and have three consumers poll it independently
**Correct answer(s):** B
**Explanation:** S3 event notifications can publish to a single SNS topic, and SNS natively supports fan-out to multiple heterogeneous subscriber types (Lambda, email, and mobile push/SMS) in parallel without custom code. Option A is a tempting distractor since S3 does support multiple event notification configurations, but S3 event notifications cannot directly target email or mobile push endpoints - only SNS, SQS, Lambda, and EventBridge are valid direct destinations.

### Question 36 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company's VPC has private subnets in two Availability Zones, each with resources that need outbound internet access for patching. Currently, a single NAT Gateway exists in AZ-A's public subnet, and route tables in both AZs point to it. During a recent AZ-A network event, private subnet resources in AZ-B also lost internet connectivity even though AZ-B itself was unaffected.
**Options:**
A. Replace the NAT Gateway with a NAT instance for better resilience
B. Deploy a NAT Gateway in each AZ's public subnet and update each AZ's route table to use its own local NAT Gateway
C. Add a second Elastic IP to the existing NAT Gateway
D. Enable cross-zone load balancing on the NAT Gateway
**Correct answer(s):** B
**Explanation:** NAT Gateways are AZ-scoped resources, so best practice for high availability is one NAT Gateway per AZ with each AZ's private route table pointing to its own local NAT Gateway, preventing a single AZ issue from taking down internet access for other AZs. NAT instances (option A) are a tempting-sounding alternative, but they are generally less resilient than managed NAT Gateways and still would need one per AZ plus custom failover scripting, not "better resilience" as a drop-in swap.

### Question 37 [Domain: 2] [Type: Single-Answer]
**Scenario:** A web application currently stores user session data in memory on individual EC2 instances behind an ALB. The team wants to enable the Auto Scaling group to freely terminate and launch instances during scaling events without logging users out or losing their shopping cart contents, and they want sub-millisecond latency for session lookups.
**Options:**
A. Enable ALB sticky sessions as the sole solution
B. Store session state in Amazon ElastiCache for Redis and have instances retrieve it on each request
C. Store session state in Amazon S3 with versioning enabled
D. Store session state in local instance store volumes with periodic EBS snapshots
**Correct answer(s):** B
**Explanation:** Moving session state to an external, low-latency in-memory store like ElastiCache for Redis decouples session data from any specific instance, letting the Auto Scaling group scale in/out freely while preserving sessions and meeting sub-millisecond latency needs. ALB sticky sessions (option A) is a tempting distractor since it keeps a user pinned to one instance, but it does not survive that instance being terminated during a scale-in event, causing session loss.

### Question 38 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company runs a compute-intensive video encoding workload that is highly parallelizable and benefits from the highest available vCPU clock speeds and price-performance ratio, but does not need large amounts of memory per vCPU. They currently use general-purpose M-family instances and are dissatisfied with encoding throughput per dollar.
**Options:**
A. Switch to R-family memory-optimized instances
B. Switch to C-family compute-optimized instances, considering Graviton-based variants for better price-performance
C. Switch to X-family instances for high memory-to-vCPU ratio
D. Switch to T-family burstable instances to save cost
**Correct answer(s):** B
**Explanation:** C-family instances are optimized for compute-bound workloads with a high vCPU-to-memory ratio, and Graviton-based (e.g., C7g) variants typically offer significantly better price-performance for parallelizable workloads like video encoding. T-family burstable instances (option D) are tempting due to lower baseline cost, but they are designed for bursty, low-average-CPU workloads and would throttle under sustained high-CPU encoding, hurting throughput.

### Question 39 [Domain: 3] [Type: Single-Answer]
**Scenario:** A financial application requires an EBS volume that can sustain 180,000 IOPS with consistent sub-millisecond latency for a mission-critical transactional database, exceeding what standard provisioned IOPS volumes can offer alone. The workload runs on a Nitro-based EC2 instance type that supports the required throughput.
**Options:**
A. gp3 volume with maximum provisioned IOPS
B. io2 Block Express volume
C. Instance store (NVMe SSD) volume
D. st1 throughput-optimized HDD volume
**Correct answer(s):** B
**Explanation:** io2 Block Express volumes support up to 256,000 IOPS and sub-millisecond latency, specifically designed for the most demanding, latency-sensitive transactional workloads, and require Nitro-based instances, which matches this scenario. gp3 (option A) is a tempting distractor since it's provisionable, but its maximum IOPS ceiling (16,000) falls far short of the 180,000 IOPS requirement.

### Question 40 [Domain: 3] [Type: Single-Answer]
**Scenario:** A retail company stores product catalog images in S3 that are accessed extremely frequently by their website with unpredictable, spiky access patterns, and latency-sensitive first-byte retrieval is critical to page load performance. Access frequency doesn't vary enough to justify tiering complexity, and the objects need to remain immediately available at all times.
**Options:**
A. S3 Glacier Instant Retrieval
B. S3 Standard
C. S3 Intelligent-Tiering with the Archive Access tier enabled
D. S3 One Zone-Infrequent Access
**Correct answer(s):** B
**Explanation:** S3 Standard provides the lowest latency and highest throughput for frequently accessed data with millisecond first-byte latency and doesn't add tiering overhead, making it ideal for consistently hot, latency-sensitive catalog images. S3 Intelligent-Tiering (option C) is a tempting distractor as a "smart" cost-optimizer, but enabling the Archive Access tiers introduces retrieval delays of hours for objects that get moved to archive tiers, which is unacceptable for a website needing consistent immediate availability.

### Question 41 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A gaming leaderboard application needs an in-memory data store that can perform complex sorted-set operations for ranking players in real time, and separately the team also wants automatic Multi-AZ failover with minimal application-level changes for high availability. They are evaluating Amazon ElastiCache for Redis.
**Options:**
A. Redis supports rich data structures such as sorted sets, which are ideal for leaderboard ranking use cases
B. ElastiCache for Redis supports Multi-AZ with automatic failover to a replica when Multi-AZ is enabled on a replication group (with cluster mode enabled or disabled)
C. ElastiCache for Redis is a fully relational database supporting complex SQL joins
D. ElastiCache for Memcached provides built-in Multi-AZ automatic failover out of the box
E. ElastiCache Global Datastore provides multi-master, active-active writes across AWS Regions without any additional application-level conflict resolution
**Correct answer(s):** A, B
**Explanation:** Redis's native sorted-set data structure is purpose-built for leaderboard ranking, and ElastiCache for Redis replication groups support Multi-AZ with automatic failover to a read replica if the primary fails. Option D is a tempting distractor because Memcached is also a valid ElastiCache engine, but Memcached is a simple, multi-threaded key-value cache with no built-in replication or Multi-AZ failover support. Option E is a tempting distractor because Global Datastore is a real cross-region feature of ElastiCache for Redis, but it replicates from a single primary region to read-only secondary regions - it is not multi-master/active-active, so writes in secondary regions are not supported without additional application-level work.

### Question 42 [Domain: 3] [Type: Single-Answer]
**Scenario:** A news website serves both highly dynamic personalized content (which must never be cached) and static assets like images and CSS files (which rarely change) from the same domain through Amazon CloudFront. Currently, a single default cache behavior applies the same short TTL to all requests, causing unnecessary origin load for static assets and stale personalization risk is not actually a concern since dynamic content already has proper cache-control headers.
**Options:**
A. Increase the default cache behavior's TTL for all paths uniformly
B. Create separate cache behaviors with different path patterns (e.g., /static/*) and configure longer TTLs specifically for static asset paths
C. Disable caching entirely across the whole distribution to avoid stale content issues
D. Switch from CloudFront to Global Accelerator for better caching control
**Correct answer(s):** B
**Explanation:** CloudFront cache behaviors let you apply different caching rules per path pattern, so static assets under a specific path can get long TTLs to reduce origin load while dynamic paths retain their existing short/no-cache settings, optimizing performance without risking stale personalized content. Global Accelerator (option D) is a tempting distractor as another AWS edge service, but it improves network routing/performance to origins and does not provide content caching capabilities like CloudFront.

### Question 43 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company runs a UDP-based real-time voice communication application with backend endpoints in three AWS Regions. They need to route users to the closest healthy endpoint based on network performance, want static anycast IP addresses for firewall allowlisting at client sites, and do not need HTTP-layer content caching since the traffic isn't cacheable.
**Options:**
A. Amazon CloudFront with multiple origins
B. AWS Global Accelerator
C. Route 53 latency-based routing only
D. Application Load Balancer with cross-region routing
**Correct answer(s):** B
**Explanation:** AWS Global Accelerator provides static anycast IP addresses, routes traffic over the AWS global network to the closest healthy endpoint based on performance, and supports both TCP and UDP, making it ideal for non-cacheable, latency-sensitive real-time traffic like voice. CloudFront (option A) is a tempting distractor as an edge-routing service, but it is an HTTP/HTTPS content delivery service and does not support arbitrary UDP protocols.

### Question 44 [Domain: 3] [Type: Single-Answer]
**Scenario:** A reporting dashboard application generates heavy, complex read-only SQL queries against a production RDS MySQL database, and these queries are beginning to degrade performance for the primary application's transactional writes. The reporting queries can tolerate results that are a few seconds behind the latest writes.
**Options:**
A. Increase the RDS instance's storage IOPS
B. Create one or more RDS read replicas and point the reporting dashboard to a read replica endpoint
C. Enable Multi-AZ deployment for the primary database
D. Migrate to a larger instance class for the primary database
**Correct answer(s):** B
**Explanation:** RDS read replicas offload read-only query traffic from the primary instance using asynchronous replication, which is well-suited for reporting workloads that can tolerate slight replication lag, directly solving the contention problem. Multi-AZ (option C) is a tempting distractor since it also creates a secondary copy, but the Multi-AZ standby is not readable for query offloading in standard RDS (only used for failover), so it would not relieve the reporting load.

### Question 45 [Domain: 3] [Type: Single-Answer]
**Scenario:** An adtech platform uses DynamoDB to serve bid requests requiring microsecond-level read latency at extremely high request rates for a relatively small, frequently repeated set of hot keys. Even with on-demand capacity and DynamoDB's typical single-digit millisecond latency, the application's SLA is not being consistently met during peak traffic.
**Options:**
A. Switch the table to provisioned capacity mode with auto scaling
B. Enable DynamoDB Accelerator (DAX) in front of the table as an in-memory cache
C. Add a global secondary index to speed up reads
D. Increase the table's read capacity units significantly
**Correct answer(s):** B
**Explanation:** DAX is a fully managed, in-memory caching layer specifically for DynamoDB that can reduce response times from single-digit milliseconds to microseconds for read-heavy workloads with hot keys, without application logic changes beyond the DAX client. Increasing read capacity or switching capacity modes (options A and D) are tempting since they add throughput, but they don't change DynamoDB's inherent millisecond-level latency floor, so they won't achieve microsecond response times.

### Question 46 [Domain: 3] [Type: Single-Answer]
**Scenario:** A DynamoDB table storing IoT sensor readings uses "deviceType" as the partition key, and one device type accounts for 95% of all writes across millions of devices. The team is experiencing throttling errors and uneven performance despite having ample overall provisioned throughput on the table.
**Options:**
A. Increase the table's provisioned write capacity units further
B. Redesign the partition key to include a more granular, high-cardinality attribute such as deviceId, or use a composite/sharded key
C. Convert the table to use DynamoDB Streams
D. Add a local secondary index on deviceType
**Correct answer(s):** B
**Explanation:** The root cause is a hot partition from low-cardinality partition key design; using a higher-cardinality attribute (like deviceId) or a sharded/composite key spreads writes evenly across partitions, resolving the throttling. Simply increasing provisioned capacity (option A) is a tempting quick fix, but DynamoDB throughput is distributed per-partition, so extra overall capacity doesn't help if writes keep concentrating on the same few partitions.

### Question 47 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A company running a MySQL-compatible relational workload on RDS is evaluating a migration to Amazon Aurora to improve performance and resilience. They are specifically interested in features that would benefit read scaling and storage-level durability without significant application rewrite.
**Options:**
A. Aurora storage automatically replicates data six ways across three Availability Zones
B. Aurora supports up to 15 low-latency read replicas that share the same underlying storage as the primary
C. Aurora requires a complete rewrite of SQL queries to a proprietary query language
D. Aurora Replicas typically have single-digit millisecond replica lag due to shared storage architecture
E. Aurora only supports a single Availability Zone deployment
**Correct answer(s):** A, B, D
**Explanation:** Aurora's distributed storage layer replicates six copies across three AZs for durability, it supports up to 15 read replicas sharing that same storage layer (versus RDS MySQL's 5 replica limit) for strong read scaling, and because replicas share the same underlying storage volume as the primary, replication lag is typically in the single-digit millisecond range - all three benefits apply with no query rewrite needed since Aurora is MySQL/PostgreSQL wire-compatible. Option C is a clear distractor since Aurora requires no proprietary query language, and option E is also false since Aurora is explicitly designed to span three Availability Zones.

### Question 48 [Domain: 3] [Type: Single-Answer]
**Scenario:** A high-performance computing (HPC) workload running tightly-coupled MPI jobs across multiple EC2 instances requires the lowest possible inter-instance network latency and highest throughput, as nodes constantly exchange data during computation. The instances will all be launched in a single Availability Zone.
**Options:**
A. Spread placement group
B. Cluster placement group
C. Partition placement group
D. Launch instances across multiple Availability Zones for redundancy
**Correct answer(s):** B
**Explanation:** Cluster placement groups pack instances close together within a single AZ on the same underlying hardware/network spine, minimizing inter-instance latency and maximizing network throughput, which is ideal for tightly-coupled HPC/MPI workloads. Spread placement groups (option A) are a tempting distractor as a placement group type, but they intentionally place instances on distinct hardware to reduce correlated failure risk, which increases rather than decreases inter-instance latency.

### Question 49 [Domain: 3] [Type: Single-Answer]
**Scenario:** A media rendering farm needs a shared file system accessible concurrently by hundreds of Linux EC2 instances, requiring sustained throughput in the multiple GB/s range with sub-millisecond latencies for large video file processing, exceeding what General Purpose EFS performance mode typically delivers.
**Options:**
A. Amazon EFS with General Purpose performance mode
B. Amazon EFS with Max I/O performance mode
C. Amazon FSx for Lustre configured for high throughput
D. Amazon S3 with Transfer Acceleration enabled
**Correct answer(s):** C
**Explanation:** FSx for Lustre is purpose-built for high-performance computing and media workloads requiring sustained sub-millisecond latencies and throughput scaling into multiple GB/s, far exceeding typical EFS throughput ceilings. EFS Max I/O (option B) is a tempting distractor because it's designed for higher aggregate throughput and IOPS than General Purpose mode, but it trades off higher per-operation latency and is still generally lower peak throughput than a properly sized FSx for Lustre file system for this scale.

### Question 50 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company needs a dedicated, private, high-bandwidth (10 Gbps) network connection between its on-premises data center and AWS for a data replication workload requiring consistent low latency and bypassing the public internet entirely. They can tolerate a multi-week setup lead time for the physical connection.
**Options:**
A. AWS Site-to-Site VPN
B. AWS Direct Connect
C. AWS Client VPN
D. A NAT Gateway with an internet-facing route
**Correct answer(s):** B
**Explanation:** Direct Connect provides a dedicated private physical network connection (available at 1, 10, or 100 Gbps) between on-premises and AWS with consistent, predictable low latency, bypassing the public internet entirely - matching the bandwidth and privacy requirements. Site-to-Site VPN (option A) is a tempting distractor as a quick-to-provision hybrid connectivity option, but it traverses the public internet over IPsec tunnels and cannot guarantee the same consistent throughput/latency as a dedicated Direct Connect circuit.

### Question 51 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company runs network-intensive EC2 instances and wants to maximize network throughput and packets-per-second performance between instances within the same VPC. They are using a current-generation instance type but are unsure whether they're getting the maximum possible network performance available for that instance family.
**Options:**
A. Enable enhanced networking (ENA - Elastic Network Adapter) on the instance, if not already active
B. Attach an additional Elastic IP address to the instance
C. Increase the instance's EBS volume size
D. Enable detailed CloudWatch monitoring on the instance
**Correct answer(s):** A
**Explanation:** Enhanced networking via the Elastic Network Adapter (ENA) provides higher bandwidth, higher packet-per-second performance, and lower inter-instance latency than standard networking, and it's available (often enabled by default) on most current-generation instance types. Adding an Elastic IP (option B) is a tempting-sounding networking change, but it only provides a static public IP address and has no effect on network throughput or packet processing performance.

### Question 52 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A solutions architect is optimizing network performance for a latency-sensitive distributed application running across multiple EC2 instances within a single VPC and Region. The team wants to both reduce inter-instance latency for tightly-coupled compute nodes and reduce data transfer costs and latency for instances accessing S3 and DynamoDB without traversing the public internet.
**Options:**
A. Place tightly-coupled instances in a cluster placement group within a single AZ
B. Configure VPC Gateway Endpoints for S3 and DynamoDB
C. Route all S3 and DynamoDB traffic through a NAT Gateway for consistency
D. Enable VPC Flow Logs to improve throughput
E. Disable enhanced networking to reduce CPU overhead
**Correct answer(s):** A, B
**Explanation:** A cluster placement group minimizes inter-instance latency for tightly-coupled nodes, and VPC Gateway Endpoints allow private, low-latency access to S3 and DynamoDB entirely within the AWS network, avoiding NAT Gateway hops, internet traversal, and associated data transfer charges. Option C is a tempting distractor since NAT Gateway does provide connectivity, but routing S3/DynamoDB traffic through it adds unnecessary latency and per-GB processing costs compared to a purpose-built gateway endpoint.

### Question 53 [Domain: 3] [Type: Single-Answer]
**Scenario:** A global photo-sharing application allows users worldwide to upload large image and video files directly to a single S3 bucket located in us-east-1. Users in Asia-Pacific and Europe report significantly slower upload speeds and frequent timeouts compared to users in North America, and the team wants to improve upload performance without deploying regional buckets or restructuring their application.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket and have distant clients upload via the acceleration endpoint
B. Enable S3 Cross-Region Replication to regions near the affected users
C. Increase the S3 bucket's default request rate limits
D. Switch the bucket's storage class to S3 Standard-Infrequent Access
**Correct answer(s):** A
**Explanation:** S3 Transfer Acceleration routes uploads through CloudFront's globally distributed edge locations over the optimized AWS backbone network to the bucket, significantly speeding up long-distance uploads without any bucket restructuring. Cross-Region Replication (option B) is a tempting distractor since it does place data closer to distant regions, but it only replicates existing objects after they land in the source bucket - it does not accelerate the actual upload of new objects from distant clients into the bucket.

### Question 54 [Domain: 4] [Type: Single-Answer]
**Scenario:** A media company runs a nightly video transcoding batch job. The number of worker nodes varies each night, and jobs are checkpointed so they can resume from where they left off if interrupted. The workload currently runs on On-Demand EC2 instances, and the finance team has asked the platform team to cut EC2 spend as much as possible without changing the architecture.
**Options:**
A. Purchase Standard Reserved Instances sized for the average nightly worker count
B. Run the workers on Spot Instances using a Spot Fleet spanning multiple instance types and AZs
C. Purchase Dedicated Hosts for the transcoding fleet
D. Purchase Compute Savings Plans covering the peak nightly usage

**Correct answer(s):** B
**Explanation:** The workload is fault-tolerant (checkpointed) and time-flexible, which is exactly what Spot Instances are designed for, offering up to 90% savings; diversifying across instance types/AZs via Spot Fleet reduces interruption risk. Compute Savings Plans is tempting since it also saves money and covers flexible compute, but it requires a 1- or 3-year commitment on usage that here is variable and can be eliminated entirely with Spot, making it less cost-optimal than Spot for this specific interruptible, variable workload.

### Question 55 [Domain: 4] [Type: Single-Answer]
**Scenario:** An application writes logs to an S3 bucket in the S3 Standard storage class. Logs are accessed frequently for the first 30 days for debugging, occasionally accessed for compliance audits for up to a year, and must be retained for 7 years total to satisfy regulations, with virtually no access expected after the first year. The team wants to minimize storage cost while meeting the retention requirement.
**Options:**
A. Create a lifecycle rule: Standard for 0–30 days, transition to Standard-IA at day 30, transition to S3 Glacier Flexible Retrieval at day 365, expire objects at 7 years
B. Leave all objects in S3 Standard for the full 7 years
C. Transition all objects to S3 One Zone-IA immediately and keep them there for 7 years
D. Enable S3 Intelligent-Tiering on the bucket and take no further action

**Correct answer(s):** A
**Explanation:** Since the access pattern is known and predictable (hot for 30 days, warm for a year, then cold), an explicit lifecycle policy moving data through Standard-IA and then Glacier Flexible Retrieval before final expiration minimizes cost precisely for this known pattern. Intelligent-Tiering is a plausible alternative since it also reduces cost automatically, but it adds a small monthly monitoring fee per object and is best suited to unpredictable access patterns — here the pattern is well understood, so an explicit lifecycle policy is cheaper and simpler.

### Question 56 [Domain: 4] [Type: Single-Answer]
**Scenario:** A startup is launching a new mobile app. Traffic is highly unpredictable and could spike 100x if the app goes viral, but could also stay flat for months. The team has no historical data to plan capacity and wants to avoid throttling while keeping DynamoDB costs proportional to actual usage.
**Options:**
A. Provisioned capacity mode with Application Auto Scaling enabled
B. On-Demand capacity mode
C. Provisioned capacity mode with Reserved Capacity purchased upfront
D. Provisioned capacity mode set to the maximum expected throughput at all times

**Correct answer(s):** B
**Explanation:** On-Demand mode requires no capacity planning, scales instantly to handle sudden traffic spikes, and bills per request, making it ideal for a brand-new workload with unknown and highly volatile traffic. Provisioned capacity with Auto Scaling is a plausible alternative, but Auto Scaling reacts to CloudWatch alarms with a lag and target-tracking cooldowns, so it can throttle requests during a sudden 100x spike and is less cost-efficient than On-Demand until a stable baseline is known.

### Question 57 [Domain: 4] [Type: Single-Answer]
**Scenario:** EC2 instances in a private subnet perform heavy data processing against objects in S3. All traffic currently routes through a NAT Gateway, and the data processing charges on the NAT Gateway have become a significant portion of the monthly bill. The security team requires that the instances remain in a private subnet with no direct internet exposure.
**Options:**
A. Deploy additional NAT Gateways in each AZ to distribute the load
B. Create a Gateway VPC Endpoint for S3 and update the route table
C. Assign public IP addresses to the instances and route traffic through an Internet Gateway
D. Provision an AWS Direct Connect connection for the S3 traffic

**Correct answer(s):** B
**Explanation:** A Gateway VPC Endpoint for S3 routes S3 traffic privately within the AWS network at no additional per-GB charge, eliminating the NAT Gateway data processing fee for that traffic while keeping instances private. Direct Connect is a tempting distractor because it also keeps traffic off the public internet, but it's designed for hybrid on-premises-to-AWS connectivity, involves substantial fixed costs, and is unnecessary overkill for traffic that stays entirely within AWS.

### Question 58 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company has steady baseline compute usage spread across several EC2 instance families and sizes, and it also runs workloads on Fargate and Lambda. Over the next 3 years, the company plans to modernize and may shift workloads between instance families, regions, and compute platforms. It wants the largest possible discount while retaining flexibility to change compute types.
**Options:**
A. Standard Reserved Instances
B. Convertible Reserved Instances
C. Compute Savings Plans
D. EC2 Instance Savings Plans

**Correct answer(s):** C
**Explanation:** Compute Savings Plans apply automatically across any EC2 instance family, size, OS, tenancy, and region, as well as Fargate and Lambda usage, giving the broadest flexibility while still discounting rates. EC2 Instance Savings Plans is a very plausible distractor since it offers a slightly higher discount than Compute Savings Plans, but the commitment is locked to a specific instance family in a specific region and does not cover Fargate or Lambda, which conflicts with the stated need to shift across families and platforms.

### Question 59 [Domain: 4] [Type: Single-Answer]
**Scenario:** A financial services firm must retain transaction records for 10 years to satisfy regulatory requirements. The records are almost never accessed except in rare legal discovery cases, and a retrieval time of up to 12 hours is acceptable when they are needed. The firm wants the lowest possible ongoing storage cost.
**Options:**
A. S3 Standard-IA
B. S3 Glacier Flexible Retrieval
C. S3 Glacier Deep Archive
D. S3 One Zone-IA

**Correct answer(s):** C
**Explanation:** S3 Glacier Deep Archive offers the lowest per-GB storage cost of any S3 class, and its standard retrieval tier (up to 12 hours) fits the stated retrieval tolerance exactly. Glacier Flexible Retrieval is a plausible distractor because it's also designed for archival data, but its standard retrieval time (3–5 hours) and higher storage price aren't needed here, since the workload can tolerate a longer 12-hour retrieval and should default to the cheapest option.

### Question 60 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A three-tier application runs across multiple Availability Zones within a VPC. The cost team has flagged high charges from NAT Gateway data processing (for calls to AWS services like S3 and DynamoDB) and from serving static assets directly to internet users. The company must maintain its current multi-AZ high-availability design. Select the two actions that would reduce these costs without reducing availability.
**Options:**
A. Create VPC Endpoints (Gateway for S3/DynamoDB, Interface for other AWS services) so traffic bypasses the NAT Gateway
B. Serve static assets through Amazon CloudFront to cache content at edge locations and reduce origin data transfer
C. Consolidate all application resources into a single Availability Zone
D. Deploy additional NAT Gateways in every AZ to spread out the processing load
E. Assign an Elastic IP directly to every private EC2 instance

**Correct answer(s):** A, B
**Explanation:** VPC Endpoints eliminate NAT Gateway data processing charges for AWS API traffic, and CloudFront reduces both data transfer costs and origin load by caching static content at the edge — neither compromises multi-AZ availability. Consolidating into a single AZ is a very tempting distractor because it would indeed cut inter-AZ transfer costs, but it directly violates the requirement to maintain the current high-availability design.

### Question 61 [Domain: 4] [Type: Single-Answer]
**Scenario:** A mature analytics platform has a DynamoDB table with consistent, predictable high-volume read/write traffic that has remained stable for over a year and is expected to continue for at least 3 more years. The table currently uses On-Demand capacity mode, and per-request costs have grown significant enough that the finance team wants a cheaper billing model for this specific, steady workload.
**Options:**
A. Enable DynamoDB Accelerator (DAX) in front of the table
B. Switch to Provisioned capacity mode and size read/write capacity to the steady baseline throughput
C. Keep On-Demand mode but enable auto scaling
D. Enable DynamoDB Streams on the table

**Correct answer(s):** B
**Explanation:** For a long-term, steady, predictable throughput pattern, moving from On-Demand to Provisioned capacity mode (sized to the known baseline) is the correct cost lever: Provisioned's hourly per-capacity-unit pricing is substantially cheaper than On-Demand's per-request pricing once the throughput profile is stable and understood. (Note: DynamoDB Reserved Capacity — which previously let customers prepay Provisioned capacity for an additional discount — was retired by AWS in 2024 and is no longer available for new purchase, so Provisioned mode itself, without a Reserved Capacity purchase, is the actionable optimization today.) DAX is a plausible distractor because it does reduce cost for read-heavy workloads by caching results and offloading reads, but it addresses read latency/throughput offload rather than the underlying billing model, so it doesn't directly solve the core capacity-mode cost problem described.

### Question 62 [Domain: 4] [Type: Single-Answer]
**Scenario:** A relational database on EC2 requires roughly 14,000 IOPS and 900 MB/s throughput from its attached EBS volume. It currently uses a gp2 volume, and the team has had to massively over-provision the volume size just to earn enough baseline IOPS through gp2's size-based performance formula, driving up storage costs. The application is not so latency-critical that it requires io2's sub-millisecond consistency guarantees.
**Options:**
A. Migrate to an io2 Block Express volume
B. Migrate to a gp3 volume and provision IOPS and throughput independently of volume size
C. Continue increasing the gp2 volume size to raise the IOPS ceiling
D. Switch to instance store (ephemeral) volumes

**Correct answer(s):** B
**Explanation:** gp3 lets you provision IOPS (up to 16,000) and throughput (up to 1,000 MB/s) independently of the volume's storage size, so the team can right-size the volume to its actual capacity needs while still meeting the 14,000 IOPS/900 MB/s targets at a much lower cost than an oversized gp2 volume. io2 Block Express is a tempting distractor because it can also deliver this performance, but it costs more per provisioned IOPS and is intended for workloads needing io2's higher durability and sub-millisecond consistency, which isn't required here.

### Question 63 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A serverless order-processing application runs on AWS Lambda with steady, high-volume invocation traffic throughout the day. All functions currently run on the x86_64 architecture with a uniform 1,750 MB memory allocation regardless of actual need, and Lambda costs have grown significantly. Cold starts are not currently a concern. Select three actions that would reduce Lambda costs for this steady-state workload.
**Options:**
A. Right-size each function's memory allocation using profiling tools and CloudWatch metrics
B. Migrate functions to the arm64 (Graviton2) architecture where compatible
C. Enable Provisioned Concurrency on all functions
D. Increase memory allocation to the 10,240 MB maximum for all functions
E. Purchase Compute Savings Plans to cover the steady-state Lambda usage

**Correct answer(s):** A, B, E
**Explanation:** Right-sizing memory eliminates paying for unused compute, arm64/Graviton2 typically offers better price-performance than x86_64, and Compute Savings Plans discount steady, predictable Lambda usage — all three directly reduce cost without harming performance. Provisioned Concurrency is a tempting-sounding "optimization" but actually adds a continuous cost for keeping execution environments warm and is unnecessary here since cold starts aren't a stated problem, so it would increase, not decrease, spend.

### Question 64 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs a production PostgreSQL database on an RDS db.r6g.xlarge Multi-AZ instance that has operated continuously with stable, predictable load for over a year, and the company plans to keep this exact configuration running for at least 3 more years. The team wants to reduce costs for this specific instance while keeping operations as simple as possible.
**Options:**
A. Migrate the database to Aurora Serverless v2
B. Purchase a 3-year, All Upfront RDS Reserved Instance for that instance class
C. Keep On-Demand pricing and rely only on storage auto scaling
D. Migrate the database to self-managed PostgreSQL on EC2

**Correct answer(s):** B
**Explanation:** For a known, stable, long-running instance configuration, a 3-year All Upfront Reserved Instance provides the deepest discount with no architectural changes or added operational complexity. Aurora Serverless v2 is a plausible distractor since it can also reduce costs by scaling capacity to match demand, but it's optimized for variable or unpredictable workloads and introduces migration effort and complexity that isn't justified for a workload that is already steady and predictable.

### Question 65 [Domain: 4] [Type: Single-Answer]
**Scenario:** A FinOps team wants automated, machine-learning-based rightsizing recommendations across EC2 instances, EBS volumes, Lambda functions, and Auto Scaling groups, based on historical utilization metrics, to identify consistently over-provisioned resources across the organization's accounts.
**Options:**
A. AWS Trusted Advisor
B. AWS Compute Optimizer
C. AWS Cost Explorer
D. AWS Budgets

**Correct answer(s):** B
**Explanation:** AWS Compute Optimizer uses machine learning on CloudWatch utilization metrics to generate detailed rightsizing recommendations specifically for EC2, EBS, Lambda, and Auto Scaling groups. Trusted Advisor is a tempting distractor because it does include a "Low Utilization Amazon EC2 Instances" cost-optimization check, but that check is a simpler threshold-based rule with limited resource coverage and depth compared to Compute Optimizer's ML-driven, multi-service recommendations.
