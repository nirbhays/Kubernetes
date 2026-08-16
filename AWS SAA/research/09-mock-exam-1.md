# AWS SAA-C03 Mock Exam 1

*Difficulty: Foundation/medium baseline.*

These are 65 original practice questions (not real or leaked exam content). Each question is self-contained with its correct answer(s) and explanation inline — no separate answer key is needed.

---

### Question 1 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company has a "Payments" AWS account and a "Reporting" AWS account, both part of the same AWS Organization. An application running on EC2 instances in the Reporting account needs to read objects from an S3 bucket owned by the Payments account. The security team requires that no long-term credentials be stored on the EC2 instances and that access be easily revocable.
**Options:**
A. Create an IAM user in the Payments account, generate access keys, and store them in the EC2 instance's user data
B. Create an IAM role in the Payments account with a trust policy allowing the Reporting account, attach a bucket-read policy, and have the EC2 instances assume the role via STS
C. Make the S3 bucket public and restrict access using the bucket's ACL to the Reporting account's CIDR range
D. Copy the S3 bucket's objects to a bucket in the Reporting account nightly using a scheduled Lambda function
**Correct answer(s):** B
**Explanation:** A cross-account IAM role with a trust policy lets the Reporting account's EC2 instances (via an instance profile assuming the role, or direct STS AssumeRole) obtain temporary credentials with no long-term secrets stored anywhere, and the role can be revoked or its trust policy edited instantly. Option A violates the no-long-term-credentials requirement and is a common wrong answer because it "works" but fails the security requirement.

### Question 2 [Domain: 1] [Type: Single-Answer]
**Scenario:** A developer has full `kms:*` permissions granted via an IAM policy attached to their user. Despite this, when they try to use a specific customer managed KMS key to decrypt data, they receive an `AccessDenied` error. No SCPs are in place.
**Options:**
A. IAM policies alone are sufficient for KMS keys and the error must be caused by an expired IAM session
B. The key's key policy does not grant this principal permission, and unlike most AWS resources, KMS requires both the identity-based policy AND the key policy to allow the action
C. The developer's IAM policy has a typo and must be missing the `kms:Decrypt` action even though they believe it has `kms:*`
D. KMS keys ignore key policies entirely once an IAM policy grants `kms:*`
**Correct answer(s):** B
**Explanation:** KMS is one of the few services where the resource policy (key policy) is evaluated in addition to identity-based policies — the effective permission is the intersection, so the key policy must explicitly allow the IAM principal (or delegate to IAM via the standard default statement). Option A is wrong because IAM policies alone are never sufficient for KMS keys unless the key policy also delegates control to IAM.

### Question 3 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company stores a database password in AWS Secrets Manager and wants it automatically rotated every 30 days without any application downtime or manual intervention, using a native integration with Amazon RDS for MySQL.
**Options:**
A. Store the password in Systems Manager Parameter Store as a SecureString and write a cron job on an EC2 instance to rotate it
B. Enable automatic rotation on the secret in Secrets Manager using the built-in RDS MySQL single-user rotation Lambda function template, and set the rotation interval to 30 days
C. Manually rotate the password every 30 days using the RDS console and update the secret value by hand
D. Store the password in a KMS-encrypted S3 object and use S3 Event Notifications to trigger rotation
**Correct answer(s):** B
**Explanation:** Secrets Manager provides native, AWS-managed Lambda rotation templates for RDS engines (single-user or alternating-user), enabling fully automated, scheduled rotation with no application downtime when combined with connection retry logic. Option A is a tempting distractor since Parameter Store can hold secrets, but it lacks Secrets Manager's built-in rotation orchestration.

### Question 4 [Domain: 1] [Type: Single-Answer]
**Scenario:** A solutions architect is troubleshooting connectivity to an EC2 instance in a private subnet. The instance's security group allows inbound traffic on port 443 from 0.0.0.0/0, but the associated Network ACL only has a default DENY rule for all inbound and outbound traffic beyond the default allow rules that were removed. Clients cannot reach the instance at all.
**Options:**
A. Security groups are stateless, so return traffic is being blocked
B. Network ACLs are stateless, so even though inbound port 443 might be allowed, the ephemeral return traffic on outbound will be blocked unless explicitly permitted
C. Security groups always override NACLs, so the NACL configuration is irrelevant
D. NACLs only apply to traffic between subnets, not to traffic from the internet
**Correct answer(s):** B
**Explanation:** NACLs are stateless, so both the inbound request AND the outbound response (typically on ephemeral ports 1024-65535) must be explicitly allowed; a NACL with no inbound/outbound rules beyond a DENY will block all traffic. Option A is incorrect because security groups are stateful — they automatically allow return traffic for permitted connections.

### Question 5 [Domain: 1] [Type: Single-Answer]
**Scenario:** An e-commerce site running behind an Application Load Balancer has recently experienced repeated SQL injection attempts targeting its login form, identified in ALB access logs. The company wants to block these malicious requests before they reach the application, without modifying application code.
**Options:**
A. Add a Network ACL rule to block traffic on port 443
B. Attach an AWS WAF web ACL to the ALB with a rule group that includes the AWS Managed Rules SQL Database (SQLi) rule set
C. Enable GuardDuty on the account to automatically block SQL injection traffic
D. Configure the security group on the ALB to deny traffic from the source IPs seen in the logs
**Correct answer(s):** B
**Explanation:** AWS WAF inspects HTTP request content (headers, body, URI) and can attach to an ALB; the AWS Managed Rules SQLi rule group is purpose-built to detect and block SQL injection patterns. GuardDuty (option C) is a threat detection service that generates findings — it does not inspect or block HTTP payloads inline.

### Question 6 [Domain: 1] [Type: Multiple-Response]
**Scenario:** Amazon GuardDuty has generated a high-severity finding indicating that an EC2 instance in the production VPC is communicating with a known cryptocurrency-mining command-and-control domain. The security team needs to both contain the immediate threat and improve automated response for future findings. (Select TWO.)
**Options:**
A. Isolate the affected EC2 instance by moving it to a quarantine security group with no inbound or outbound rules (so no traffic is allowed in or out), then perform forensic analysis
B. Delete the GuardDuty detector to stop further false positives
C. Create an EventBridge rule that triggers a Lambda function to automatically isolate instances and notify the security team whenever a similar high-severity GuardDuty finding occurs
D. Disable VPC Flow Logs to reduce the noise causing the finding
E. Ignore the finding since GuardDuty findings are informational only and require no action
**Correct answer(s):** A, C
**Explanation:** Immediate containment via moving the instance to an isolation security group with no allow rules (security groups are allow-only — an empty rule set implicitly blocks all traffic, since security groups do not support explicit deny rules) stops further C2 communication while preserving the instance for forensics, and an EventBridge-triggered Lambda automates detection-to-response for future findings. Deleting the detector or disabling Flow Logs (B, D) removes visibility rather than addressing the threat, and treating findings as purely informational (E) ignores an active compromise indicator.

### Question 7 [Domain: 1] [Type: Single-Answer]
**Scenario:** A mobile application needs to let users sign up and sign in using email/password or through Google and Facebook social login, and after authentication the app needs temporary AWS credentials to upload photos directly to an S3 bucket.
**Options:**
A. Use a single Cognito User Pool to handle both authentication and issue temporary AWS credentials directly
B. Use a Cognito User Pool for authentication (including social identity provider federation) and a Cognito Identity Pool to exchange the User Pool tokens for temporary AWS credentials via STS
C. Use IAM Identity Center (AWS SSO) configured with Google and Facebook as external identity providers
D. Create individual IAM users for each mobile app user and rotate their access keys periodically
**Correct answer(s):** B
**Explanation:** Cognito User Pools handle user directory, authentication, and social/SAML federation, while Cognito Identity Pools (Federated Identities) exchange the resulting tokens for temporary, scoped AWS credentials via STS — this is the standard two-part Cognito pattern. Option A is a common mistake: User Pools alone authenticate users but do not directly grant AWS resource access.

### Question 8 [Domain: 1] [Type: Single-Answer]
**Scenario:** A platform team allows application developers to create their own IAM roles for their Lambda functions but is concerned developers might accidentally (or intentionally) grant these roles excessive permissions such as full S3 or IAM access. They want a guardrail that caps the maximum permissions any role a developer creates can ever have, regardless of what policy is attached to it.
**Options:**
A. Attach an IAM permissions boundary to the developer's IAM user/role that limits the maximum permissions any IAM entity they create can have
B. Use AWS Config rules to alert after the fact when an overly permissive role is detected
C. Require developers to submit a ticket for every IAM policy change
D. Attach a resource-based policy to each Lambda function limiting its permissions
**Correct answer(s):** A
**Explanation:** A permissions boundary is a managed policy that sets the maximum permissions an IAM entity can have (and any roles/users it creates), acting as a preventive guardrail rather than a detective control. AWS Config (option B) only detects violations after they occur, which does not meet the "cap the maximum permissions" preventive requirement.

### Question 9 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A global company needs to encrypt data in Amazon S3 buckets replicated across us-east-1, eu-west-1, and ap-southeast-1 regions, and wants each region's application to be able to encrypt/decrypt using the same underlying key material without making cross-region API calls to KMS (which would add latency and a regional dependency). (Select TWO.)
**Options:**
A. Use AWS KMS multi-Region keys, creating a primary key in one region and replica keys in the other regions that share the same key material and Key ID
B. Use a single-region KMS key in us-east-1 and configure S3 Cross-Region Replication to call KMS in us-east-1 from every region
C. Enable S3 Bucket Keys in each region's bucket to reduce the number of KMS API calls to the replicated multi-Region key
D. Use AWS Certificate Manager to generate a shared symmetric key usable across all three regions
E. Disable encryption on the replicated objects and rely solely on TLS in transit
**Correct answer(s):** A, C
**Explanation:** KMS multi-Region keys let each region's replica key independently encrypt/decrypt with shared key material without cross-region calls, and enabling S3 Bucket Keys reduces per-object KMS API calls/costs on top of that. Option B defeats the purpose by forcing every region to call back to us-east-1, reintroducing the latency and dependency the company wants to avoid.

### Question 10 [Domain: 1] [Type: Single-Answer]
**Scenario:** A three-tier application has web servers in a public subnet and application servers in a private subnet. The security team wants to ensure the application servers can only receive traffic on port 8080 from the web tier's security group, regardless of the web servers' changing IP addresses as instances scale in and out.
**Options:**
A. Add an inbound rule to the application servers' NACL allowing port 8080 from the web subnet's CIDR block
B. Add an inbound rule to the application servers' security group that references the web servers' security group ID as the source, allowing port 8080
C. Hardcode the current web server IP addresses into the application security group's inbound rules
D. Use a NAT Gateway between the web and application tiers to mask IP addresses
**Correct answer(s):** B
**Explanation:** Security groups support referencing another security group ID as the source, which automatically covers any instance (current or future) that belongs to that security group, making it ideal for dynamic/auto-scaled fleets. Option C is the common but fragile mistake — hardcoded IPs break as instances scale or are replaced.

### Question 11 [Domain: 1] [Type: Single-Answer]
**Scenario:** A team needs to store a database connection string that includes a password, requires automatic rotation with native RDS integration, and needs fine-grained resource-based policies for cross-account access. Budget is not a primary concern, but functionality is.
**Options:**
A. AWS Systems Manager Parameter Store Standard tier
B. AWS Secrets Manager
C. AWS Systems Manager Parameter Store Advanced tier
D. Amazon S3 with SSE-KMS encryption
**Correct answer(s):** B
**Explanation:** Secrets Manager natively supports automatic rotation with built-in Lambda templates for RDS and supports resource-based policies for cross-account sharing, which Parameter Store's Advanced tier does not natively provide (rotation must be self-built via Lambda and EventBridge). S3 (option D) is not designed as a secrets management service and lacks native rotation.

### Question 12 [Domain: 1] [Type: Single-Answer]
**Scenario:** Account A owns an S3 bucket containing shared datasets. Account B needs read-only access to specific prefixes within that bucket. The security team wants access controlled centrally by Account A without creating any IAM users or roles in Account B, and Account A must be able to revoke access at any time by editing a single policy document.
**Options:**
A. Have Account A create an IAM role that Account B's users assume via AssumeRole
B. Attach a bucket policy in Account A that grants the specific Account B account/principal read access to the designated prefixes
C. Enable S3 Cross-Region Replication to copy the objects into a bucket in Account B
D. Make the bucket public and rely on obscure prefix names for security
**Correct answer(s):** B
**Explanation:** An S3 bucket policy (a resource-based policy) lets Account A grant a specific external account or principal direct read access to defined prefixes — Account B's existing principals use their own credentials with no role-assumption step, no role ARN to manage, and no additional IAM configuration required in Account B. Access is fully centralized and instantly revocable by editing the single bucket policy document in Account A. Option A also enables cross-account access, but it requires Account B's principals to explicitly call `sts:AssumeRole` and depends on IAM permissions/configuration in Account B to permit that call — introducing the kind of decentralized, cross-account IAM dependency the security team explicitly wants to avoid, so it is a weaker fit than the bucket policy.

### Question 13 [Domain: 1] [Type: Single-Answer]
**Scenario:** A public-facing web application is being hit by a Layer 7 HTTP flood from thousands of unique IP addresses, each sending an abnormally high number of requests per minute, degrading application performance. The security team wants to automatically throttle offending IPs.
**Options:**
A. Enable AWS Shield Advanced only, which automatically blocks all Layer 7 floods without configuration
B. Create an AWS WAF rate-based rule on the associated web ACL that tracks requests per 5-minute window per IP and blocks IPs exceeding the defined threshold
C. Add a Network ACL deny rule for each offending IP address as it appears in the logs
D. Increase the Auto Scaling group's maximum capacity to absorb the extra load
**Correct answer(s):** B
**Explanation:** A WAF rate-based rule automatically tracks request rates per source IP over a rolling 5-minute window and can block/CAPTCHA IPs that exceed the threshold, which is purpose-built for L7 HTTP flood mitigation. Option A is a distractor — Shield Advanced provides DDoS protection and cost protection but relies on WAF rules for this kind of granular, automatic per-IP rate limiting.

### Question 14 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A security team wants to expand their Amazon GuardDuty deployment beyond basic VPC Flow Log and DNS log analysis to also detect suspicious activity targeting their Amazon EKS clusters and potential malware on EC2 instances and container workloads. (Select TWO.)
**Options:**
A. Enable GuardDuty EKS Protection to monitor Kubernetes audit logs for suspicious API activity
B. Enable GuardDuty Malware Protection to scan EBS volumes attached to EC2 instances and container workloads for malware
C. Enable AWS Config to natively detect malware signatures on EBS volumes
D. Rely on VPC Flow Logs alone, since they already capture all container-level malware activity
E. Enable AWS Trusted Advisor's security checks to scan Kubernetes audit logs
**Correct answer(s):** A, B
**Explanation:** GuardDuty EKS Protection analyzes Kubernetes audit logs for anomalous API calls, and GuardDuty Malware Protection performs agentless scanning of EBS volumes for EC2/container workloads when a relevant finding suggests compromise. AWS Config (C) and Trusted Advisor (E) are not malware/Kubernetes audit log detection tools, and VPC Flow Logs (D) only capture network metadata, not malware signatures or Kubernetes API activity.

### Question 15 [Domain: 1] [Type: Single-Answer]
**Scenario:** A large enterprise uses an on-premises Active Directory Federation Services (AD FS) setup as its identity provider and wants employees to log into a custom web application hosted on AWS using their existing corporate credentials via SAML 2.0, without duplicating user accounts in Cognito.
**Options:**
A. Create a Cognito User Pool and configure a SAML identity provider federation with AD FS, then use hosted UI or SDK to redirect users to AD FS for authentication
B. Manually create a matching IAM user in AWS for every Active Directory user
C. Use Amazon Cognito Sync to copy the Active Directory user database into Cognito
D. Configure Amazon Cognito to accept plaintext Active Directory passwords via a custom Lambda trigger
**Correct answer(s):** A
**Explanation:** Cognito User Pools support SAML 2.0 federation, allowing users to authenticate against an external IdP like AD FS while Cognito issues standard tokens (and, combined with an Identity Pool, temporary AWS credentials) without duplicating the user directory. Options B and C are wrong because they involve unnecessary and unscalable manual/duplicate account management rather than true federation.

### Question 16 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company using AWS Organizations wants to ensure that no account in its "Sandbox" organizational unit can ever launch resources outside the us-east-1 region, even if an account administrator in that OU has full IAM/AdministratorAccess permissions.
**Options:**
A. Attach an IAM policy to every user in the Sandbox accounts denying actions outside us-east-1
B. Attach a Service Control Policy (SCP) to the Sandbox OU that denies all actions unless the request region is us-east-1
C. Configure AWS Config rules to flag resources created outside us-east-1
D. Use IAM Access Analyzer to automatically delete resources created outside us-east-1
**Correct answer(s):** B
**Explanation:** SCPs are the only mechanism here that set an account-wide permission ceiling enforced even against full administrators — an SCP denying all actions when the request region is not us-east-1 will override any IAM policy including AdministratorAccess. Option A fails because a Sandbox admin with IAM permissions could simply modify or remove the IAM policy, since IAM policies don't cap what an account administrator can ultimately change.

### Question 17 [Domain: 1] [Type: Single-Answer]
**Scenario:** A third-party auditing vendor needs to decrypt a small set of specific S3 objects encrypted with a customer managed KMS key for exactly 48 hours during an audit, after which access must automatically expire without the security team needing to manually revoke or edit the key policy.
**Options:**
A. Add the vendor's IAM role ARN permanently to the key policy and remember to remove it after 48 hours
B. Create a temporary KMS grant for the vendor's principal scoped to the required decrypt operation, and require the vendor to access it through an assumed IAM role whose permissions policy includes a `DateLessThan` condition on `aws:CurrentTime` set 48 hours out, so access automatically stops working at that time regardless of how many times the session is refreshed
C. Share the KMS key's raw key material with the vendor via encrypted email
D. Disable the KMS key entirely after 48 hours to block all access, including from internal applications
**Correct answer(s):** B
**Explanation:** KMS grants provide a way to delegate temporary, fine-grained permissions on a key programmatically without editing the key policy. Because an individual STS `AssumeRole` session is capped at the role's configured maximum session duration (up to 12 hours), it cannot by itself span the full 48-hour window without being refreshed — so a time-bound IAM condition (`aws:CurrentTime` `DateLessThan`) on the vendor's permissions policy is what guarantees access automatically and permanently expires at the 48-hour mark, even if the vendor's application keeps refreshing its session or the grant is never explicitly retired. Option A technically works but requires manual policy edits and remembering to revoke, which fails the "automatically expire" requirement.

### Question 18 [Domain: 1] [Type: Multiple-Response]
**Scenario:** An architect is designing network security controls for a VPC hosting a three-tier application and wants to apply defense-in-depth. The design must include both a mechanism for filtering traffic at the subnet boundary (stateless, rule-numbered, can explicitly deny) and a mechanism for filtering traffic at the instance/ENI level (stateful, allow-only). (Select TWO.)
**Options:**
A. Network ACLs — stateless, evaluated in rule number order, support explicit ALLOW and DENY rules, applied at the subnet level
B. Security Groups — stateful, support only ALLOW rules (no explicit deny), applied at the instance/ENI level
C. AWS WAF — stateless, applied at the subnet level, supports explicit deny of Layer 3 traffic
D. IAM policies — stateful, applied at the ENI level, support explicit deny of network traffic
E. Route tables — stateful, used to explicitly deny traffic between subnets
**Correct answer(s):** A, B
**Explanation:** Network ACLs are the correct stateless, rule-numbered, subnet-level control supporting explicit allow/deny, while security groups are the correct stateful, instance/ENI-level, allow-only control — together they form the classic AWS defense-in-depth network layering. WAF (C) operates at Layer 7 HTTP on resources like ALB/CloudFront/API Gateway, not as a subnet-level L3/L4 filter, and route tables (E) direct traffic paths but do not perform allow/deny filtering.

### Question 19 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company has 50 AWS accounts under AWS Organizations and wants to share a central Amazon VPC subnet, a Transit Gateway, and specific License Manager configurations across many accounts without creating cross-account IAM roles for every resource and every account pair.
**Options:**
A. Use AWS Resource Access Manager (RAM) to share the subnet, Transit Gateway, and License Manager configuration with the Organization or specific OUs
B. Create a cross-account IAM role in each of the 50 accounts trusting the central account for every shared resource
C. Copy the VPC subnet configuration manually into each of the 50 accounts
D. Use AWS Control Tower exclusively, since it automatically shares all resources across accounts by default
**Correct answer(s):** A
**Explanation:** AWS Resource Access Manager (RAM) is purpose-built to share supported resources (subnets, Transit Gateways, License Manager configurations, and more) across accounts or an entire Organization/OU without needing per-account IAM role setups. Option B would technically be possible for some access patterns but does not scale well and isn't how native resource sharing (like a subnet or Transit Gateway attachment) is actually implemented in AWS.

### Question 20 [Domain: 1] [Type: Single-Answer]
**Scenario:** A developer's application, running under an IAM role attached to an EC2 instance, receives `AccessDenied` when calling `s3:PutObject` on a bucket. The attached IAM policy on the role explicitly allows `s3:PutObject` on that exact bucket ARN with no conditions, and there is no SCP restricting S3 in the account.
**Options:**
A. IAM role policies never apply to EC2 instances, only to Lambda functions
B. The S3 bucket has a bucket policy with an explicit Deny statement for this principal or action, which overrides the Allow in the identity-based policy
C. The instance must be restarted for new IAM role permissions to take effect
D. EC2 instances cannot call S3 APIs; they require an S3 VPC endpoint policy at minimum
**Correct answer(s):** B
**Explanation:** In AWS policy evaluation, an explicit Deny in any applicable policy (including a bucket policy) always overrides an Allow elsewhere, so a bucket policy denying the action/principal would produce this exact symptom despite the identity policy allowing it. Option C is a common misconception — IAM role permission changes take effect immediately for temporary credentials refreshed via the instance metadata service, no restart required.

### Question 21 [Domain: 2] [Type: Single-Answer]
**Scenario:** A retail company runs its order-processing database on a single Amazon RDS for MySQL instance in one Availability Zone. During a recent AZ-level network disruption, the database became unavailable for over an hour, causing checkout failures. Management wants automatic failover to another AZ with minimal downtime and without requiring application-side connection-string changes during failover.
**Options:**
A. Enable Multi-AZ deployment for the RDS instance
B. Create a cross-Region read replica and promote it manually during outages
C. Take hourly manual DB snapshots and restore from the latest snapshot when an outage occurs
D. Move the database to a single large EC2 instance with EBS Multi-Attach
**Correct answer(s):** A
**Explanation:** RDS Multi-AZ maintains a synchronously replicated standby in another AZ and automatically fails over the same DNS endpoint, requiring no application changes. Read replicas (B) are asynchronous and require manual promotion, introducing delay and potential data loss; snapshot restore (C) has a much longer RTO.

### Question 22 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company deploys a new application version behind an Application Load Balancer, with EC2 instances managed by an Auto Scaling group. The new instances take about 90 seconds to fully initialize the application before they can respond to health checks. The Auto Scaling group is currently terminating and replacing these instances before they finish starting up, causing an endless replacement loop.
**Options:**
A. Increase the ALB target group's deregistration delay
B. Increase the Auto Scaling group's health check grace period
C. Reduce the ALB idle timeout value
D. Switch the target group's health check protocol from HTTP to TCP
**Correct answer(s):** B
**Explanation:** The health check grace period tells the Auto Scaling group to wait a specified time after instance launch before acting on health check failures, giving the app time to initialize. Deregistration delay (A) controls connection draining on removal, not startup behavior, so it does not address the premature termination issue.

### Question 23 [Domain: 2] [Type: Single-Answer]
**Scenario:** A SaaS company runs its application in a primary AWS Region with a fully provisioned standby stack in a secondary Region. They want DNS to automatically route users to the secondary Region's endpoint only if the primary Region's endpoint fails health checks, and revert automatically once the primary recovers.
**Options:**
A. Route 53 weighted routing policy
B. Route 53 failover routing policy with health checks
C. Route 53 geolocation routing policy
D. Route 53 multivalue answer routing policy
**Correct answer(s):** B
**Explanation:** Failover routing policy with associated health checks is purpose-built for active-passive DR, automatically directing traffic to the secondary record when the primary fails and back once healthy. Weighted (A) is for percentage-based traffic splitting, not health-based failover.

### Question 24 [Domain: 2] [Type: Single-Answer]
**Scenario:** A ticket-booking web application experiences sudden traffic spikes during flash sales, and the backend fulfillment service (which writes to a relational database) cannot keep up, causing the web tier to time out and crash. The company wants the web tier to remain responsive regardless of backend processing speed.
**Options:**
A. Increase the web tier EC2 instance size
B. Insert an Amazon SQS queue between the web tier and the fulfillment service
C. Add more read replicas to the relational database
D. Enable RDS Multi-AZ for the fulfillment database
**Correct answer(s):** B
**Explanation:** SQS decouples the producer (web tier) from the consumer (fulfillment service), letting the web tier enqueue requests instantly while the backend processes at its own sustainable pace. Scaling instance size (A) or adding read replicas (C) does not solve the fundamental coupling problem causing cascading failures.

### Question 25 [Domain: 2] [Type: Multiple-Response]
**Scenario:** An e-commerce platform needs to notify three independent systems whenever a new order is placed: an order-fulfillment service that consumes from a queue, an analytics pipeline that consumes from a separate queue, and a Lambda function that sends a confirmation email. The architecture team proposes publishing a single event to an SNS topic with an SQS queue and a Lambda function subscribed to it. Select TWO benefits of this fan-out pattern.
**Options:**
A. Each subscriber receives the message independently, so a failure in one subscriber does not block the others
B. New subscribers can be added later without modifying the order-placement code
C. SNS guarantees strict ordering of messages across all subscribers
D. It eliminates the need for retry logic on any subscriber
E. It reduces the storage cost of the underlying order database
**Correct answer(s):** A, B
**Explanation:** The fan-out pattern delivers a single published message to multiple independent subscribers, isolating failures and allowing new consumers to be attached without touching the publisher. Standard SNS does not guarantee cross-subscriber ordering (C), and subscribers can still fail and require their own retry/DLQ handling (D).

### Question 26 [Domain: 2] [Type: Single-Answer]
**Scenario:** An operations team needs to trigger a Lambda function every night at 2 AM UTC to clean up expired temporary records, and separately wants to react automatically whenever a third-party SaaS partner (integrated via a partner event source) sends a "shipment.created" event. They want a single fully managed service to handle both the scheduled trigger and the partner event routing.
**Options:**
A. Set up a cron job on an EC2 instance to invoke both workflows
B. Use Amazon EventBridge with a scheduled rule and a partner event bus rule
C. Use an SQS delay queue with a 24-hour delivery delay
D. Use AWS Step Functions Standard Workflows exclusively
**Correct answer(s):** B
**Explanation:** EventBridge natively supports scheduled (cron/rate) rules and partner event buses that ingest events from supported SaaS integrations, routing both to Lambda targets without managing servers. An EC2 cron job (A) reintroduces the operational burden the team is trying to avoid.

### Question 27 [Domain: 2] [Type: Single-Answer]
**Scenario:** A media company ingests real-time clickstream data from millions of website visitors. Multiple independent consumer applications (a real-time dashboard, a fraud-detection engine, and a data lake loader) each need to read and reprocess the same stream of events independently, and event order must be preserved per user session.
**Options:**
A. Amazon SQS Standard queue
B. Amazon SQS FIFO queue
C. Amazon Kinesis Data Streams
D. Amazon SNS topic with multiple subscribers
**Correct answer(s):** C
**Explanation:** Kinesis Data Streams retains data for a configurable window and allows multiple independent consumers to read the same records at their own pace while preserving per-partition-key order. SQS (A/B) removes messages once consumed by a single consumer group, making true multi-consumer independent replay impractical.

### Question 28 [Domain: 2] [Type: Single-Answer]
**Scenario:** A web application's Auto Scaling group needs to automatically add or remove EC2 instances to keep average CPU utilization close to 50% across the fleet, without an engineer manually defining CloudWatch alarm thresholds.
**Options:**
A. Simple scaling policy
B. Scheduled scaling policy
C. Target tracking scaling policy
D. Step scaling policy
**Correct answer(s):** C
**Explanation:** Target tracking scaling policies let you specify a target metric value (e.g., 50% average CPU) and AWS automatically manages the necessary CloudWatch alarms and scaling adjustments. Step and simple scaling (A, D) require manually defined alarm thresholds and scaling amounts.

### Question 29 [Domain: 2] [Type: Single-Answer]
**Scenario:** A startup wants a disaster recovery strategy for its application in a secondary Region that minimizes ongoing cost. They are willing to accept an RTO of around 10-15 minutes. Their plan is to keep a small, always-on replica of the core database running in the DR Region, with AMIs and launch templates pre-configured, but no application servers running until a disaster is declared.
**Options:**
A. Backup and restore
B. Pilot light
C. Multi-site active-active
D. Warm standby
**Correct answer(s):** B
**Explanation:** Pilot light keeps only the most critical core components (like a database replica) running continuously, while other resources are quickly launched from pre-built templates/AMIs during an actual disaster. Warm standby (D) would keep a scaled-down but fully functional application stack running at all times, which is more than described here.

### Question 30 [Domain: 2] [Type: Single-Answer]
**Scenario:** A financial services firm requires an RTO of under two minutes for its trading application. They maintain a fully functional, scaled-down version of the entire application stack continuously running in a secondary Region, ready to be scaled up immediately if the primary Region fails.
**Options:**
A. Pilot light
B. Backup and restore
C. Warm standby
D. Single-Region deployment with Multi-AZ only
**Correct answer(s):** C
**Explanation:** Warm standby maintains a scaled-down but fully operational replica of the whole stack running continuously, enabling fast scale-up and failover with minimal RTO. Pilot light (A) only keeps core data services running and requires provisioning the rest of the stack during failover, resulting in a longer RTO.

### Question 31 [Domain: 2] [Type: Single-Answer]
**Scenario:** A small business wants the lowest-cost disaster recovery approach for its internal reporting application. They can tolerate an RTO of up to 24 hours and an RPO of up to 12 hours. They plan to use AWS Backup to periodically copy backups to another Region and restore infrastructure from AWS CloudFormation templates only if a disaster occurs.
**Options:**
A. Multi-site active-active
B. Warm standby
C. Pilot light
D. Backup and restore
**Correct answer(s):** D
**Explanation:** Backup and restore is the lowest-cost DR strategy, relying on periodic backups and infrastructure-as-code templates to rebuild the environment on demand, matching the long RTO/RPO tolerance described. Pilot light (C) requires some always-on core infrastructure, which isn't mentioned here.

### Question 32 [Domain: 2] [Type: Single-Answer]
**Scenario:** A DevOps team wants to gradually shift 10% of production traffic to a new application version deployed to a separate set of servers, while the remaining 90% continues to hit the existing stable version, to validate the new version's stability before a full rollout.
**Options:**
A. Route 53 latency-based routing
B. Route 53 weighted routing
C. Route 53 geoproximity routing
D. Route 53 simple routing with two A records
**Correct answer(s):** B
**Explanation:** Weighted routing allows assigning relative weights to different resource record sets, enabling controlled percentage-based canary traffic splitting. Latency-based routing (A) routes based on lowest latency per user location, not a defined percentage split.

### Question 33 [Domain: 2] [Type: Single-Answer]
**Scenario:** A gaming company needs a load balancer for a custom TCP-based protocol (not HTTP/HTTPS) that must handle millions of requests per second, provide a static IP address per Availability Zone for firewall allowlisting, and preserve the original client source IP address.
**Options:**
A. Application Load Balancer
B. Network Load Balancer
C. Classic Load Balancer
D. Amazon API Gateway
**Correct answer(s):** B
**Explanation:** Network Load Balancer operates at Layer 4, supports ultra-high throughput, provides static IPs per AZ, and preserves the source IP by default. Application Load Balancer (A) operates at Layer 7 and is designed for HTTP/HTTPS traffic, not arbitrary TCP protocols.

### Question 34 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A global SaaS provider wants to run its application actively in two Regions simultaneously, serving users from whichever Region is closest, with automatic rerouting if one Region becomes unhealthy, and with the database layer replicating writes bidirectionally between Regions with low latency. Select TWO components that best support this active-active multi-Region design.
**Options:**
A. Route 53 latency-based routing with health checks across both Regional endpoints
B. Amazon Aurora Global Database configured for single-writer, single-Region only
C. DynamoDB global tables for multi-Region active-active data replication
D. A single Regional Application Load Balancer with no DNS-level routing
E. RDS Multi-AZ standby instance in the same Region as the primary
**Correct answer(s):** A, C
**Explanation:** Latency-based Route 53 routing with health checks directs each user to the nearest healthy Region, and DynamoDB global tables provide multi-Region, multi-active write replication needed for true active-active designs. Aurora Global Database in single-writer mode (B) only supports one Region for writes, and RDS Multi-AZ (E) provides AZ-level, not Region-level, resilience.

### Question 35 [Domain: 2] [Type: Single-Answer]
**Scenario:** A payment-processing worker consumes messages from an SQS queue, but a small number of malformed messages cause the worker to fail processing repeatedly, and these messages keep getting redelivered indefinitely, consuming worker capacity that should go toward valid messages.
**Options:**
A. Reduce the queue's visibility timeout to zero
B. Enable long polling on the queue
C. Configure a dead-letter queue with a maxReceiveCount redrive policy
D. Increase the message retention period to 14 days
**Correct answer(s):** C
**Explanation:** A dead-letter queue with a maxReceiveCount redrive policy automatically isolates messages after a defined number of failed processing attempts, preventing poison-pill messages from looping indefinitely. Reducing visibility timeout to zero (A) would make messages immediately reprocessable, worsening the loop rather than fixing it.

### Question 36 [Domain: 2] [Type: Single-Answer]
**Scenario:** Before an Auto Scaling group terminates an EC2 instance during scale-in, the operations team needs the instance to first deregister itself from an internal monitoring system and flush in-memory metrics to persistent storage, taking up to 60 seconds to complete.
**Options:**
A. Increase the health check grace period
B. Add a termination lifecycle hook to the Auto Scaling group
C. Enable termination protection on the instance
D. Set a longer cooldown period on the scaling policy
**Correct answer(s):** B
**Explanation:** A termination lifecycle hook pauses an instance in the "Terminating:Wait" state, giving custom scripts time to perform cleanup actions before the instance is actually terminated. Health check grace period (A) applies to instance launch, not termination.

### Question 37 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A company runs its web application on a single large EC2 instance in one Availability Zone, backed by a single RDS database instance with no standby. Recent AZ-level issues caused full application outages. The team wants to significantly improve fault tolerance with architectural changes. Select TWO changes that would most directly improve resilience.
**Options:**
A. Deploy EC2 instances across multiple Availability Zones behind an Application Load Balancer using an Auto Scaling group
B. Enable Multi-AZ for the RDS instance
C. Replace the single large EC2 instance with an even larger instance type in the same AZ
D. Store all user session state only in local instance memory
E. Disable automated backups to reduce database load
**Correct answer(s):** A, B
**Explanation:** Spreading compute across multiple AZs with an ALB and Auto Scaling group, combined with RDS Multi-AZ for the database, removes single points of failure at the AZ level. Using a larger instance in the same AZ (C) is vertical scaling and does nothing to address AZ-level failure risk.

### Question 38 [Domain: 3] [Type: Single-Answer]
**Scenario:** A media company runs a CPU-intensive batch video-transcoding pipeline on EC2. The workload is highly parallelizable across vCPUs but does not require large amounts of memory or GPU acceleration. They want an EC2 instance family optimized to minimize cost per vCPU for this compute-bound workload.
**Options:**
A. Memory-optimized (R-family) instances
B. Compute-optimized (C-family) instances
C. Storage-optimized (I-family) instances
D. General purpose (T-family) burstable instances
**Correct answer(s):** B
**Explanation:** Compute-optimized instances provide the highest ratio of vCPU performance to cost, ideal for CPU-bound, parallelizable workloads like video transcoding. T-family burstable instances (D) are designed for workloads with occasional spikes, not sustained high CPU usage, and would throttle under continuous load.

### Question 39 [Domain: 3] [Type: Single-Answer]
**Scenario:** A financial trading application requires an EBS volume delivering up to 256,000 IOPS and sub-millisecond, consistent latency for its transactional database, with the ability to scale IOPS independently of volume size.
**Options:**
A. gp3 General Purpose SSD
B. io2 Block Express
C. st1 Throughput Optimized HDD
D. sc1 Cold HDD
**Correct answer(s):** B
**Explanation:** io2 Block Express volumes support up to hundreds of thousands of IOPS with sub-millisecond latency and 99.999% durability, designed for the most demanding transactional workloads. gp3 (A) tops out at a much lower IOPS ceiling and is not designed for this extreme performance tier.

### Question 40 [Domain: 3] [Type: Single-Answer]
**Scenario:** A big data team runs a temporary Spark cluster on EC2 for a batch analytics job that reads raw input from S3, performs intermediate shuffle/scratch writes, and outputs final results back to S3. They need extremely high IOPS and throughput for the scratch data, and losing that scratch data on instance stop is acceptable since it can be regenerated from the original S3 input.
**Options:**
A. Amazon EBS gp3 volumes with provisioned throughput
B. Instance store (NVMe SSD) volumes
C. Amazon EFS with General Purpose performance mode
D. Amazon S3 as the scratch storage layer
**Correct answer(s):** B
**Explanation:** Instance store volumes are physically attached NVMe SSDs offering very high IOPS/throughput ideal for ephemeral scratch data, and their data loss on stop/terminate is acceptable here since results are reproducible. S3 (D) has much higher latency and is unsuitable as a low-latency scratch filesystem for shuffle operations.

### Question 41 [Domain: 3] [Type: Multiple-Response]
**Scenario:** An application uploads large media files (several GB each) from an on-premises data center to an S3 bucket over the public internet, and users worldwide report slow, inconsistent upload speeds. Select TWO changes that would improve upload performance.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket to route uploads through CloudFront edge locations
B. Use the S3 multipart upload API to upload large objects in parallel parts
C. Disable S3 versioning on the bucket
D. Reduce each uploaded object to fragments smaller than 1 KB
E. Enable S3 Object Lock in compliance mode
**Correct answer(s):** A, B
**Explanation:** Transfer Acceleration uses CloudFront's global edge network to speed up long-distance uploads, and multipart upload splits large objects into parts uploaded in parallel, both directly improving throughput for large cross-continent uploads. Disabling versioning (C) has no meaningful effect on upload speed.

### Question 42 [Domain: 3] [Type: Single-Answer]
**Scenario:** A SaaS analytics company runs a reporting dashboard that executes heavy, complex read-only queries against the same RDS PostgreSQL instance that handles the application's transactional writes. Report queries are slowing down write performance for the core application during business hours.
**Options:**
A. Enable RDS Multi-AZ for the database
B. Create one or more RDS read replicas and point the reporting dashboard to them
C. Increase the storage volume size of the primary instance
D. Enable automated backups with a longer retention window
**Correct answer(s):** B
**Explanation:** Read replicas offload read-heavy query traffic, such as reporting workloads, from the primary instance, isolating their performance impact from transactional writes. Multi-AZ (A) is for availability/failover, not read scaling, since the standby is not readable in single-standby configurations by default.

### Question 43 [Domain: 3] [Type: Single-Answer]
**Scenario:** A mobile gaming company stores player leaderboard data in DynamoDB. During peak play hours, leaderboard read requests spike into the millions per minute, and the team needs microsecond-level read latency without re-architecting their DynamoDB data model.
**Options:**
A. Amazon ElastiCache for Memcached in front of DynamoDB
B. Amazon DynamoDB Accelerator (DAX)
C. DynamoDB on-demand capacity mode alone
D. Amazon RDS read replicas
**Correct answer(s):** B
**Explanation:** DAX is a purpose-built, fully managed in-memory cache specifically for DynamoDB, delivering microsecond read latency without any application logic changes to the data model. Generic ElastiCache (A) would require custom application-level cache-aside logic and additional integration work.

### Question 44 [Domain: 3] [Type: Single-Answer]
**Scenario:** A web application needs a managed in-memory caching layer for user session data that supports Multi-AZ automatic failover, data persistence for durability, and pub/sub messaging for real-time notifications between application servers.
**Options:**
A. Amazon ElastiCache for Memcached
B. Amazon ElastiCache for Redis
C. Amazon DynamoDB Accelerator (DAX)
D. Amazon S3 with a caching proxy
**Correct answer(s):** B
**Explanation:** ElastiCache for Redis supports Multi-AZ with automatic failover, optional data persistence, and native pub/sub messaging, meeting all stated requirements. Memcached (A) is simpler, multi-threaded, and lacks persistence, replication, and pub/sub capabilities.

### Question 45 [Domain: 3] [Type: Single-Answer]
**Scenario:** A global news website serves static images and videos from an S3 origin to users worldwide. During peak traffic events, origin request volume to S3 spikes significantly, increasing latency and cost. The team wants to reduce the number of requests that reach the S3 origin while improving global content delivery speed.
**Options:**
A. Increase the number of S3 prefixes used for the media files
B. Deploy Amazon CloudFront in front of the S3 origin with Origin Shield enabled
C. Move all media files to EBS-backed EC2 instances
D. Enable S3 Cross-Region Replication to every AWS Region
**Correct answer(s):** B
**Explanation:** CloudFront caches content at edge locations close to users, and enabling Origin Shield adds an additional centralized caching layer that further reduces the number of requests hitting the origin. Cross-Region replication (D) creates copies of data but does nothing to cache or reduce request volume at the edge.

### Question 46 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A real-time multiplayer game uses a custom UDP-based protocol and needs static anycast IP addresses that clients can hardcode, along with fast automatic rerouting to a healthy AWS Region if the primary Regional endpoint becomes degraded. The team is evaluating AWS Global Accelerator for this use case. Select THREE accurate statements.
**Options:**
A. Global Accelerator provides two static anycast IP addresses that remain constant even as backend endpoints change
B. Global Accelerator supports both TCP and UDP traffic, not just HTTP/HTTPS
C. Global Accelerator caches content at edge locations to reduce origin load, similar to CloudFront
D. Global Accelerator can only be used with Application Load Balancer endpoints
E. Global Accelerator continuously monitors endpoint health and automatically reroutes traffic away from unhealthy endpoints within about 30 seconds
**Correct answer(s):** A, B, E
**Explanation:** Global Accelerator provides two static anycast IP addresses that stay constant regardless of backend endpoint changes (A), supports both TCP and UDP traffic rather than being limited to HTTP/HTTPS (B), and continuously health-checks endpoints, rerouting traffic away from unhealthy ones within roughly 30 seconds (E) — together these directly satisfy the static-IP, UDP-protocol, and fast-failover requirements in this scenario. Global Accelerator does not cache content (C) — that is a CloudFront capability, not a Global Accelerator one — and it supports Network Load Balancers, EC2 instances, and Elastic IPs as endpoints in addition to Application Load Balancers, so it is not limited to ALBs (D).

### Question 47 [Domain: 3] [Type: Single-Answer]
**Scenario:** A scientific research team runs a tightly-coupled HPC simulation across many EC2 instances using MPI, requiring the lowest possible network latency and highest throughput between instances, all located within a single Availability Zone.
**Options:**
A. Spread placement group
B. Partition placement group
C. Cluster placement group
D. No placement group, using default instance placement
**Correct answer(s):** C
**Explanation:** Cluster placement groups pack instances close together within a single AZ on the same underlying hardware/network segment, minimizing inter-instance latency and maximizing network throughput for tightly-coupled HPC workloads. Spread placement groups (A) instead maximize physical separation for fault isolation, which is the opposite goal.

### Question 48 [Domain: 3] [Type: Single-Answer]
**Scenario:** A genomics company runs a large-scale MPI-based simulation across hundreds of EC2 instances in a cluster placement group. Despite the placement group, network latency between instances is still a bottleneck for the OS-level networking stack during high-frequency inter-node communication.
**Options:**
A. Switch to Elastic Load Balancing between the instances
B. Enable Elastic Fabric Adapter (EFA) on the instances
C. Attach additional Elastic Network Interfaces (ENIs) to each instance
D. Move the workload to Amazon ECS with Fargate
**Correct answer(s):** B
**Explanation:** EFA provides OS-bypass networking capability that enables lower and more consistent latency for tightly-coupled HPC/MPI applications, which standard ENIs cannot achieve. Adding regular ENIs (C) increases network interfaces but does not bypass the OS networking stack for reduced latency.

### Question 49 [Domain: 3] [Type: Single-Answer]
**Scenario:** A global application needs to serve read queries with low latency to users in North America, Europe, and Asia-Pacific, with each Region's replica staying within about one second of the primary write Region, plus the ability to promote a secondary Region to full read/write within one minute during a Regional disaster.
**Options:**
A. RDS read replicas within a single Region
B. Amazon Aurora Global Database
C. DynamoDB with a single table in one Region
D. Amazon RDS Multi-AZ deployment
**Correct answer(s):** B
**Explanation:** Aurora Global Database replicates data across Regions with typical lag under one second and supports promoting a secondary Region to full read/write in under a minute during disaster recovery. RDS Multi-AZ (D) operates only within a single Region and does not provide cross-Region low-latency read replicas.

### Question 50 [Domain: 3] [Type: Single-Answer]
**Scenario:** EC2 instances in a private subnet with no internet access need to read and write objects to an S3 bucket frequently. Traffic is currently routed through a NAT Gateway, adding both data processing charges and extra network hops that increase latency.
**Options:**
A. Add a route to an Internet Gateway from the private subnet
B. Create a VPC Gateway Endpoint for Amazon S3 and update the route table
C. Launch a NAT instance instead of a NAT Gateway
D. Use AWS Direct Connect to reach S3
**Correct answer(s):** B
**Explanation:** A Gateway Endpoint for S3 provides private, direct routing to S3 within the AWS network, avoiding NAT Gateway data processing charges and reducing latency, without exposing the subnet to the internet. Adding an Internet Gateway route (A) would require public IPs and expose instances unnecessarily, which also doesn't align with the private subnet requirement.

### Question 51 [Domain: 3] [Type: Single-Answer]
**Scenario:** A manufacturing company needs to continuously replicate large volumes of sensor data from its on-premises data center to AWS with consistent, predictable low-latency throughput. Their current site-to-site VPN connection over the public internet suffers from variable latency and occasional packet loss that disrupts replication.
**Options:**
A. Increase the number of VPN tunnels for redundancy
B. Set up an AWS Direct Connect dedicated connection
C. Switch replication to use Amazon S3 Transfer Acceleration
D. Use AWS Global Accelerator between the data center and AWS
**Correct answer(s):** B
**Explanation:** Direct Connect provides a dedicated, private network connection between on-premises infrastructure and AWS, delivering consistent bandwidth and lower, more predictable latency than internet-based VPN connections. Adding more VPN tunnels (A) improves redundancy but does not fix the fundamental variability of routing over the public internet.

### Question 52 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A company is redesigning its data architecture and needs to select the right purpose-built AWS database for two distinct workloads: (1) sub-millisecond key-value lookups for a high-traffic product catalog, and (2) complex analytical queries with joins and aggregations across petabytes of historical sales data for business intelligence. Select TWO correct service-to-workload pairings.
**Options:**
A. Amazon DynamoDB for the sub-millisecond key-value product catalog lookups
B. Amazon Redshift for the petabyte-scale analytical BI queries
C. Amazon RDS for MySQL for the petabyte-scale analytical BI queries
D. Amazon ElastiCache for Memcached as the primary system of record for sales data
E. Amazon Neptune for the key-value product catalog lookups
**Correct answer(s):** A, B
**Explanation:** DynamoDB is purpose-built for low-latency key-value access at scale, and Redshift is a purpose-built columnar data warehouse optimized for large-scale analytical queries with joins and aggregations. RDS for MySQL (C) is a general-purpose relational database not optimized for petabyte-scale OLAP analytics, and Memcached (D) is a volatile cache, not a durable system of record.

### Question 53 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company needs to migrate approximately 200 TB of archival data from its on-premises data center to Amazon S3. Their available internet bandwidth is only 10 Mbps, which would take many months to transfer online, and the migration must complete within one week.
**Options:**
A. Use S3 Transfer Acceleration over the existing internet connection
B. Order an AWS Snowball Edge Storage Optimized device to physically transfer the data
C. Increase the number of parallel S3 multipart uploads
D. Set up a new Direct Connect connection for the migration
**Correct answer(s):** B
**Explanation:** At 10 Mbps, transferring 200 TB online would take roughly 5 years of continuous transfer, not the one week available, making a physical Snowball Edge device the practical solution to meet the deadline regardless of upload optimizations. Direct Connect (D) requires lead time to provision (often weeks) and still depends on available bandwidth, which doesn't solve the immediate timeline constraint.

### Question 54 [Domain: 4] [Type: Single-Answer]
**Scenario:** A biotech research firm runs genome-sequencing analysis jobs that read input files from S3 and process them in parallel across hundreds of EC2 instances. The jobs are stateless, checkpoint their progress to S3 every five minutes, and can resume from the last checkpoint if interrupted. The workload runs sporadically — sometimes idle for days — and the team wants to minimize compute cost while allowing some flexibility in completion time.
**Options:**
A. Purchase Reserved Instances for the entire fleet to lock in a lower hourly rate
B. Launch the fleet using Spot Instances with a diversified instance type allocation strategy
C. Use On-Demand Instances exclusively to guarantee capacity availability
D. Purchase Dedicated Hosts to reduce per-instance licensing costs
**Correct answer(s):** B
**Explanation:** Spot Instances can save up to 90% versus On-Demand and are ideal for fault-tolerant, checkpointed, interruptible batch workloads; diversifying across instance pools reduces interruption impact. Reserved Instances require steady, predictable usage to pay off, but this workload sits idle for days at a time, making an RI commitment wasteful. Dedicated Hosts solve licensing/compliance needs, not cost minimization for interruptible batch work.

### Question 55 [Domain: 4] [Type: Single-Answer]
**Scenario:** A financial services company runs a self-managed PostgreSQL database on a single m5.2xlarge EC2 instance that has operated 24/7 for over a year and is expected to run unchanged in the same instance family and Region for at least three more years. Budget has been approved for a three-year commitment, and the team wants the maximum possible discount, with no anticipated need to change instance family, size, OS, or Region.
**Options:**
A. Convertible Reserved Instance, 3-year term, No Upfront
B. Standard Reserved Instance, 3-year term, All Upfront
C. Compute Savings Plan, 1-year term
D. On-Demand Instances with Auto Scaling
**Correct answer(s):** B
**Explanation:** A Standard RI with a 3-year term and All Upfront payment delivers the deepest discount available for a workload with fixed, unchanging attributes, since no flexibility is required. Convertible RIs trade discount depth for the ability to change instance attributes, a feature not needed here; a 1-year Compute Savings Plan ignores the available 3-year commitment and offers a shallower discount than a matched 3-year Standard RI.

### Question 56 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company migrating an on-premises Windows Server workload to AWS holds existing Microsoft Server and SQL Server licenses tied to physical cores and sockets, which must be used under Bring-Your-Own-License (BYOL) terms. The team needs visibility into the underlying host's socket and core counts to remain license-compliant while also minimizing cost.
**Options:**
A. On-Demand Instances using License Included Windows AMIs
B. Reserved Instances (Standard, 1-year)
C. Dedicated Hosts with a Host Reservation
D. Spot Instances
E. Compute Savings Plans
**Correct answer(s):** C
**Explanation:** Dedicated Hosts expose physical socket and core counts required for BYOL license compliance, and purchasing a Host Reservation reduces the cost compared to On-Demand Dedicated Hosts. License Included AMIs bundle new license costs into the instance price, conflicting with the BYOL requirement, while standard RIs, Spot, and Savings Plans operate at the instance level and don't guarantee dedicated physical hardware visibility.

### Question 57 [Domain: 4] [Type: Single-Answer]
**Scenario:** An e-commerce company stores application logs in S3. Logs are accessed frequently during the first 30 days for troubleshooting, occasionally accessed for analytics between day 30 and day 90, and must be retained for 7 years for compliance but are essentially never accessed after day 90 except for rare audits that can tolerate retrieval within 12 hours. The company wants to minimize storage cost while meeting these needs.
**Options:**
A. Keep all logs in S3 Standard for the full 7 years
B. Transition to S3 Standard-IA after 30 days, then to S3 Glacier Flexible Retrieval after 90 days, and expire objects after 7 years
C. Move all logs to S3 Glacier Deep Archive immediately upon upload
D. Configure S3 Cross-Region Replication to a second bucket using S3 One Zone-IA
**Correct answer(s):** B
**Explanation:** This lifecycle matches the access pattern precisely: Standard for frequent early access, Standard-IA for occasional access days 30–90, and Glacier Flexible Retrieval (with retrieval options up to ~12 hours) for the long, rarely-accessed compliance period. Keeping everything in Standard is far more expensive than needed, and moving straight to Deep Archive would break the day 30–90 analytics use case since Deep Archive retrieval takes far longer than 12 hours.

### Question 58 [Domain: 4] [Type: Single-Answer]
**Scenario:** A SaaS analytics company stores customer-uploaded datasets with highly unpredictable access patterns — some files are accessed daily for weeks then never again, while others sit untouched for months before being reprocessed. The team cannot predict which category a given file will fall into and wants an automated solution that minimizes storage cost without adding operational overhead or risking retrieval delays for the customer-facing application.
**Options:**
A. S3 Standard-IA for all objects
B. S3 Glacier Instant Retrieval for all objects
C. S3 Intelligent-Tiering
D. Manually tag objects and run a nightly Lambda function to move them between storage classes
**Correct answer(s):** C
**Explanation:** S3 Intelligent-Tiering automatically moves objects between access tiers based on observed usage, with no retrieval fees and millisecond access in its frequent/infrequent tiers, requiring zero operational effort. Standard-IA charges a retrieval fee and only pays off for known infrequent-access patterns, which doesn't fit here, and a manual Lambda-based tagging pipeline reintroduces exactly the operational overhead the company wants to avoid.

### Question 59 [Domain: 4] [Type: Single-Answer]
**Scenario:** A hospital network must retain patient imaging records for 10 years to satisfy regulations. Records are almost never accessed after the first six months, and on the rare occasion a legal request requires retrieval, the compliance team has confirmed a retrieval time of up to 12 hours is acceptable. The hospital wants the lowest possible storage cost for this archive.
**Options:**
A. S3 Glacier Instant Retrieval
B. S3 Glacier Flexible Retrieval
C. S3 Glacier Deep Archive
D. S3 Standard-IA
**Correct answer(s):** C
**Explanation:** S3 Glacier Deep Archive is the lowest-cost S3 storage class, built for data accessed once or twice a year with a standard retrieval time of up to 12 hours, matching both the cost goal and the acceptable delay. Glacier Instant Retrieval costs more because it guarantees millisecond access, which isn't required, and Standard-IA is significantly pricier than any Glacier tier for rarely-accessed archival data.

### Question 60 [Domain: 4] [Type: Single-Answer]
**Scenario:** A startup is launching a new mobile app backed by DynamoDB. Traffic in the first few months is expected to be extremely unpredictable — a viral marketing campaign could spike load 50x, or usage could stay flat for weeks — and the small engineering team doesn't want to spend time forecasting or tuning scaling policies. They need a capacity mode that avoids throttling while paying only for actual usage.
**Options:**
A. Provisioned capacity with manual scaling
B. Provisioned capacity with Application Auto Scaling
C. On-Demand capacity mode
D. Reserved Capacity
**Correct answer(s):** C
**Explanation:** On-Demand capacity mode scales instantly to handle unpredictable spikes with pay-per-request pricing and requires no capacity planning, which is ideal for a brand-new, volatile workload. Provisioned capacity with Auto Scaling still reacts to CloudWatch alarms with a delay and can throttle during a sudden 50x spike, and Reserved Capacity requires committing upfront to a steady provisioned throughput level, which is unsuitable for unknown traffic.

### Question 61 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A logistics company runs a DynamoDB table in Provisioned capacity mode supporting a fleet-tracking dashboard. Traffic follows a highly predictable daily pattern — high during business hours, near-zero overnight — and has remained stable for over a year. The company wants to reduce its DynamoDB bill without switching to On-Demand mode.
**Options:**
A. Enable Application Auto Scaling on the table's read/write capacity to track the predictable daily traffic pattern
B. Analyze a full year of stable CloudWatch throughput metrics and lower the table's provisioned capacity baseline (minimum RCU/WCU) to remove persistent over-provisioning
C. Switch the table's billing mode to On-Demand for maximum elasticity
D. Delete and recreate the table every night to reset capacity units
E. Enable DynamoDB Accelerator (DAX) as the primary means of reducing the bill
**Correct answer(s):** A, B
**Explanation:** Auto Scaling adjusts provisioned throughput within its configured bounds to match the known daily pattern, avoiding over-provisioning during off-peak hours. Complementing this, right-sizing the provisioned capacity baseline from a full year of stable CloudWatch metrics removes persistent excess capacity that loose Auto Scaling min/max bounds alone wouldn't catch. Switching to On-Demand is explicitly excluded by the scenario; deleting and recreating the table nightly is destructive and not a supported cost strategy; DAX primarily reduces read latency and can lower RCU consumption, but it adds its own node costs and isn't the primary lever for this predictable, provisioned workload.

### Question 62 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs application servers in private subnets that frequently read and write objects to S3 and read items from DynamoDB. This traffic currently routes through a NAT Gateway to reach the public endpoints for S3 and DynamoDB, and the team has noticed that NAT Gateway data processing charges make up a significant portion of the monthly bill. They want to reduce this cost while keeping the servers private.
**Options:**
A. Replace the NAT Gateway with a NAT Instance
B. Create a Gateway VPC Endpoint for S3 and DynamoDB and update the route tables
C. Move the application servers to public subnets
D. Increase the NAT Gateway's bandwidth allocation
**Correct answer(s):** B
**Explanation:** Gateway VPC Endpoints for S3 and DynamoDB route traffic privately within the AWS network at no additional per-GB processing charge, directly eliminating NAT Gateway fees for that traffic. A NAT Instance can lower cost somewhat but reintroduces management overhead and bandwidth limits while still incurring data charges, and moving servers to public subnets increases security exposure and isn't a valid cost-optimization practice.

### Question 63 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company serves a static marketing website globally through CloudFront but has confirmed via analytics that over 95% of viewers are located in North America and Europe. The company wants to reduce CloudFront costs without meaningfully impacting performance for its actual user base.
**Options:**
A. Disable CloudFront caching and serve content directly from the S3 origin
B. Configure the CloudFront distribution to use the Price Class that includes only North America and Europe edge locations
C. Switch from CloudFront to a single-Region S3 static website endpoint
D. Enable Origin Shield in every AWS Region
**Correct answer(s):** B
**Explanation:** CloudFront Price Classes let you restrict which edge locations serve content; selecting the North America and Europe price class avoids paying for the most expensive, rarely-used edge locations while still serving nearly all real users from nearby edges. Disabling caching removes CloudFront's core benefit and increases origin load and latency, while dropping CloudFront entirely for a single-Region S3 endpoint removes CDN caching and can increase latency and data transfer cost for the remaining global visitors.

### Question 64 [Domain: 4] [Type: Single-Answer]
**Scenario:** A manufacturing company transfers roughly 10 TB of sensor data per day from its on-premises data center to AWS for analytics, a volume expected to keep growing. It currently uses a Site-to-Site VPN over the internet and has found data transfer costs and inconsistent throughput increasingly problematic. The company is willing to make a longer-term commitment to reduce both cost and variability for this steady, high-volume, ongoing transfer.
**Options:**
A. Increase the number of Site-to-Site VPN tunnels for higher aggregate throughput
B. Provision an AWS Direct Connect dedicated connection with a private virtual interface
C. Use AWS Snowball devices shipped daily to transfer the data
D. Enable S3 Transfer Acceleration for the uploads
**Correct answer(s):** B
**Explanation:** Direct Connect provides a dedicated, private connection with consistent throughput and lower per-GB transfer rates than internet-based paths, making it the most cost-effective and reliable choice for a steady, high-volume, ongoing workload. Adding more VPN tunnels doesn't resolve the underlying internet dependency or high egress cost, Snowball is meant for periodic bulk or one-time migrations rather than continuous daily transfer, and Transfer Acceleration optimizes public-internet uploads via CloudFront edges but doesn't provide a dedicated, cost-stable connection.

### Question 65 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A three-tier web application is deployed across multiple Availability Zones within a single Region for high availability. The compute tier communicates heavily with both a database tier and an S3 bucket used for shared assets. The company has noticed a large portion of its monthly bill comes from data transfer charges and wants to reduce these costs without reducing the application's availability.
**Options:**
A. Create a Gateway VPC Endpoint for S3 to eliminate NAT Gateway/internet data processing charges for S3 traffic
B. Consolidate all resources into a single Availability Zone to eliminate cross-AZ data transfer charges
C. Deploy a database read replica in each Availability Zone and configure application servers to read from the replica in their own AZ
D. Enable AWS Global Accelerator for all internal service-to-service traffic
E. Right-size EC2 instances to reduce compute costs
**Correct answer(s):** A, C
**Explanation:** A Gateway VPC Endpoint removes data processing charges for S3 traffic that would otherwise cross a NAT Gateway or the internet, and per-AZ read replicas keep frequent read traffic within the same AZ (intra-AZ transfer is free) while preserving multi-AZ redundancy. Consolidating into a single AZ would cut cross-AZ costs but directly reduces availability, which the scenario rules out; Global Accelerator optimizes external client traffic entering the AWS network rather than internal service-to-service traffic and adds its own costs; right-sizing lowers compute spend but doesn't target data transfer charges specifically.
