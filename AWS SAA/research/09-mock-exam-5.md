# AWS SAA-C03 Mock Exam 5

*Difficulty: Final readiness assessment.*

These are 65 original practice questions (not real or leaked exam content). Each question is self-contained with its correct answer(s) and explanation inline — no separate answer key is needed.

---

### Question 1 [Domain: 1] [Type: Single-Answer]
**Scenario:** A platform team wants to let individual engineering-team leads create IAM roles for their own teams' Lambda functions without involving central security for every request. However, security mandates that no matter what permissions a team lead attaches to a role they create, that role must never be able to call `iam:*` actions or access the production `finance-data` S3 bucket. The solution must scale as new roles are created over time without ongoing manual review.
**Options:**
A. Attach a Service Control Policy to the account that denies `iam:*` and access to the finance-data bucket for every principal
B. Grant team leads an IAM policy that allows `iam:CreateRole` only when the request specifies an approved permissions boundary policy (enforced via the `iam:PermissionsBoundary` condition key), so every role they create is automatically capped by that boundary regardless of the identity-based policy later attached to it
C. Use AWS IAM Access Analyzer to scan roles weekly and manually revoke any excess permissions found
D. Create the roles only with the `ReadOnlyAccess` AWS managed policy attached
**Correct answer(s):** B
**Explanation:** A permissions boundary sets the maximum permissions an IAM principal can have; by granting team leads `iam:CreateRole` only when they attach an AWS-approved boundary policy (enforced structurally via the `iam:PermissionsBoundary` condition key, not merely as an unenforced process requirement), even an overly broad identity-based policy on a new role is automatically capped — and this scales to every future role without manual review. Option A (an account-wide SCP) is tempting because it also restricts permissions, but it requires AWS Organizations and would apply to every principal in the account, including the central security team's own roles that legitimately need `iam:*` access — making it a blunter, less-delegated control than a boundary scoped only to the roles team leads create.

### Question 2 [Domain: 1] [Type: Single-Answer]
**Scenario:** A SaaS vendor (Account 999999999999) needs to be granted temporary, auditable access to resources inside each of its customers' AWS accounts in order to run a monitoring integration. Each customer will create an IAM role in their own account that the vendor's application assumes via `sts:AssumeRole`. The vendor is concerned about the "confused deputy" problem, where another one of its customers could trick it into assuming a role in a different customer's account.
**Options:**
A. Require each customer to embed the vendor's AWS account root credentials into the trust policy
B. Have each customer include a unique `sts:ExternalId` condition in the role's trust policy, and require the vendor's application to pass that same value on every `AssumeRole` call
C. Have the vendor create a separate IAM user with long-term access keys in each customer account
D. Configure the customer's role trust policy with a wildcard `Principal: "*"`
**Correct answer(s):** B
**Explanation:** The `sts:ExternalId` condition is AWS's documented mitigation for the confused-deputy problem in third-party cross-account access, ensuring the vendor can only assume a given customer's role using the unique ID that customer issued. Option D is tempting for "simplicity" but a wildcard principal would let any AWS account assume the role, which is a severe security gap.

### Question 3 [Domain: 1] [Type: Single-Answer]
**Scenario:** A central security team manages a customer managed KMS key ("alias/finance-key") used to encrypt sensitive S3 objects. The key currently uses the default key policy, which delegates all permission management to IAM policies in the account. The security team is worried that an application team could attach an overly permissive IAM policy granting `kms:Decrypt` on this key to a role without the security team's knowledge or approval, since IAM policies alone can currently grant that access.
**Options:**
A. Enable automatic annual key rotation on the CMK
B. Replace the default key policy with a custom key policy that removes the blanket IAM-delegation statement and explicitly lists only the security-approved principals allowed to use the key
C. Add a resource-based policy to every IAM role in the account
D. Migrate the key material to AWS CloudHSM
**Correct answer(s):** B
**Explanation:** For a customer managed key, the key policy is the primary access-control document; removing the default "allow IAM policies to control access" statement and explicitly naming approved principals means IAM alone can no longer grant access — both the key policy AND an IAM policy must allow it. Key rotation (A) is a good practice but has nothing to do with restricting who can use the key.

### Question 4 [Domain: 1] [Type: Single-Answer]
**Scenario:** An application team stores their Amazon RDS for MySQL database credentials in AWS Secrets Manager. Compliance requires the database password to be rotated automatically every 30 days with zero application downtime, and the team wants to avoid writing and maintaining custom rotation code.
**Options:**
A. Enable Secrets Manager's built-in rotation for the secret and select the AWS-provided rotation Lambda function template for Amazon RDS credentials, with a 30-day rotation schedule
B. Manually update the secret value every 30 days using the Secrets Manager console
C. Store the credentials in Systems Manager Parameter Store as a SecureString and set a CloudWatch alarm to remind the team to rotate it
D. Rotate the RDS master password using an EC2 instance cron job that calls `modify-db-instance`, independent of Secrets Manager
**Correct answer(s):** A
**Explanation:** Secrets Manager provides pre-built Lambda rotation function templates for RDS, Redshift, and DocumentDB that handle the alternating-user rotation strategy safely with no downtime, requiring only a schedule to be configured. Option D would work technically but duplicates AWS-managed functionality with custom, unmanaged code and breaks the single source of truth in Secrets Manager.

### Question 5 [Domain: 1] [Type: Single-Answer]
**Scenario:** EC2 instances in a private subnet initiate outbound HTTPS requests (port 443) to a third-party licensing API on the internet via a NAT gateway. The subnet's custom network ACL has only two non-default rules: an inbound rule allowing TCP 443 from 0.0.0.0/0, and an outbound rule allowing TCP 443 to 0.0.0.0/0. The instances' security group allows all outbound traffic and has no explicit inbound rules beyond the default. The instances can send requests but never receive a response from the licensing API.
**Options:**
A. Add an inbound network ACL rule allowing TCP traffic on the ephemeral port range (1024–65535) from 0.0.0.0/0, since NACLs are stateless and the response arrives on an ephemeral port, not 443
B. Add an inbound security group rule allowing TCP 443 from 0.0.0.0/0
C. Replace the NAT gateway with a NAT instance
D. Add an outbound network ACL rule allowing TCP 1024–65535
**Correct answer(s):** A
**Explanation:** Network ACLs are stateless, so return traffic must be explicitly permitted; because the instance initiated the connection from an ephemeral source port, the API's response arrives back at that same ephemeral port and is blocked by the NACL's implicit deny. Option B is a common wrong guess, but security groups are stateful and already automatically allow the return traffic for an established outbound connection.

### Question 6 [Domain: 1] [Type: Single-Answer]
**Scenario:** A public-facing web application behind an Application Load Balancer is receiving repeated SQL injection and cross-site scripting attack attempts identified in the application logs. The security team needs to block these common web exploits quickly, using AWS-maintained rule logic rather than writing and maintaining custom detection signatures themselves.
**Options:**
A. Enable AWS WAF on the ALB and associate the AWS Managed Rules "Core rule set (CRS)" and "SQL database" managed rule groups
B. Enable AWS Shield Advanced on the ALB
C. Modify the ALB's security group to deny inbound traffic from 0.0.0.0/0
D. Enable Amazon GuardDuty on the account
**Correct answer(s):** A
**Explanation:** AWS WAF's Managed Rules provide continuously updated, pre-built rule groups (including a SQL injection-focused rule group and a general core rule set covering XSS) that can be attached to an ALB in minutes. Shield Advanced (B) is tempting because it's also a "security" service, but it protects against network/transport-layer and application-layer DDoS, not injection-style web exploits.

### Question 7 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company is enabling Amazon GuardDuty for the first time across its AWS account. Before turning it on, a team member asks whether they first need to manually enable and configure VPC Flow Logs, DNS query logging, and AWS CloudTrail management event logging delivered to an S3 bucket, since GuardDuty is described as analyzing these data sources for threats.
**Options:**
A. Yes — all three log sources must be manually enabled and configured to deliver to an S3 bucket that GuardDuty then reads from
B. No — GuardDuty independently and directly consumes VPC Flow Logs, DNS query logs, and CloudTrail management events internally as part of its foundational data sources; no manual logging setup is required
C. Only CloudTrail must be manually enabled; the other two are unnecessary for GuardDuty
D. GuardDuty requires an AWS Config recorder to be enabled and configured first
**Correct answer(s):** B
**Explanation:** GuardDuty's foundational protection automatically and directly ingests VPC Flow Logs, DNS logs, and CloudTrail management events behind the scenes at no extra logging configuration cost — you simply enable GuardDuty itself. Option A is a common misconception since these are separate loggable AWS features elsewhere, but GuardDuty does not depend on you having them independently configured.

### Question 8 [Domain: 1] [Type: Single-Answer]
**Scenario:** A mobile application needs users to sign up and sign in with a username and password (including forgot-password flows and optional social login), and once authenticated, the app must upload photos directly from the device to an Amazon S3 bucket using temporary, scoped AWS credentials rather than embedding any long-term AWS keys in the app.
**Options:**
A. Use an Amazon Cognito user pool for sign-up/sign-in, and use an Amazon Cognito identity pool to exchange the user pool tokens for temporary IAM credentials scoped for S3 access
B. Use only an Amazon Cognito identity pool for both authentication and AWS credential vending
C. Use only an Amazon Cognito user pool, and hardcode an IAM user's access keys in the app for S3 uploads
D. Create an individual IAM user for every app user and rotate their access keys periodically
**Correct answer(s):** A
**Explanation:** Cognito user pools handle the authentication (sign-up, sign-in, password recovery, federation), while Cognito identity pools take the resulting tokens and vend short-lived, least-privilege AWS credentials via STS — this is the standard "user pool + identity pool" pattern for mobile apps needing direct AWS access. Option B is incorrect because identity pools alone don't provide a managed user directory or sign-up/sign-in UI — they need an identity source such as a user pool.

### Question 9 [Domain: 1] [Type: Single-Answer]
**Scenario:** A company uses AWS Organizations with a "Sandbox" OU containing dozens of developer accounts. Developers in these accounts have `AdministratorAccess` for experimentation, but the company mandates that EC2 instances must never be launched outside the `us-east-1` region in any Sandbox account, even by an account administrator.
**Options:**
A. Attach an IAM permissions boundary limiting `ec2:RunInstances` to `us-east-1` on every IAM role in every Sandbox account
B. Attach a Service Control Policy to the Sandbox OU that denies `ec2:RunInstances` unless the request's region equals `us-east-1`
C. Create an AWS Config rule with automatic remediation that terminates non-compliant instances after they launch
D. Apply a tag policy across the Sandbox OU restricting the `region` tag value
**Correct answer(s):** B
**Explanation:** An SCP attached at the OU level sets a permissions guardrail that applies to every principal in every account under that OU — including administrators — and cannot be overridden by IAM policies within the accounts. Option A is tempting but a permissions boundary is an account-local IAM control that an account's own administrator could remove or bypass, so it cannot reliably enforce an org-wide guardrail across many accounts.

### Question 10 [Domain: 1] [Type: Multiple-Response]
**Scenario:** Account A owns an S3 bucket named `shared-reports` whose objects are encrypted with a customer managed KMS key (`alias/shared-key`), also owned by Account A. An IAM role named `DataReader` in Account B needs to call `s3:GetObject` on objects in that bucket. Currently, calls from `DataReader` fail with access denied errors. What must the Account A security team configure to grant this access correctly? (Select TWO)
**Options:**
A. Add a bucket policy statement on `shared-reports` granting `s3:GetObject` to the ARN of the `DataReader` role in Account B
B. Add a statement to the `alias/shared-key` key policy granting the `DataReader` role in Account B `kms:Decrypt` (and `kms:DescribeKey`)
C. Enable S3 Cross-Region Replication from `shared-reports` to a bucket in Account B
D. Add a Service Control Policy in Account B allowing `kms:Decrypt` on all resources
E. Change the bucket's block public access settings to allow public read
**Correct answer(s):** A, B
**Explanation:** Cross-account access to an encrypted object requires both an S3 resource policy (or ACL) granting the object access itself, and a KMS key policy statement granting the external account's principal permission to use the key to decrypt — both the resource owner's grants are needed since neither IAM policy alone in Account B can grant access to another account's resources. Option C is a common distractor, but replication creates a separate copy of the data and does nothing to grant the existing role access to the original bucket.

### Question 11 [Domain: 1] [Type: Single-Answer]
**Scenario:** A security team suspects that over time, some IAM roles in their account may have accumulated resource-based policies or trust relationships that grant access to external AWS accounts or the public, without anyone tracking it centrally. They want an automated way to continuously identify which resources in the account are accessible from outside the account or organization, without writing custom scripts.
**Options:**
A. Enable AWS IAM Access Analyzer, which continuously analyzes resource-based policies and generates findings for any access granted to external principals
B. Run AWS Trusted Advisor's cost optimization checks weekly
C. Enable GuardDuty's S3 Protection feature
D. Manually review CloudTrail logs for every `PutBucketPolicy` and `PutRolePolicy` API call
**Correct answer(s):** A
**Explanation:** IAM Access Analyzer uses automated reasoning to evaluate resource-based policies (S3 buckets, IAM roles, KMS keys, Lambda functions, etc.) and produces findings whenever a resource is accessible from outside a defined zone of trust — exactly the continuous, automated visibility the team wants. Option C is a plausible-sounding distractor, but GuardDuty's S3 Protection detects suspicious *activity* against S3 data, not overly permissive policy configurations.

### Question 12 [Domain: 1] [Type: Multiple-Response]
**Scenario:** An architect is evaluating AWS KMS multi-Region keys to support an application that encrypts data in `us-east-1` and needs a disaster recovery replica application in `eu-west-1` to be able to decrypt that same data without cross-region KMS API calls during a regional failover. Which of the following statements about multi-Region KMS keys are correct? (Select TWO)
**Options:**
A. A multi-Region key's primary key and its replica keys share the same key ID and the same underlying key material
B. Data encrypted using a replica key in one Region can be decrypted using the related replica key in a different Region, without needing to re-encrypt the data or call KMS in the original Region
C. Key policies, grants, and resource tags are automatically and instantly synchronized across all replica keys by AWS KMS
D. An existing single-Region KMS key can be converted into a multi-Region key at any time by calling `UpdateKeyDescription`
E. Multi-Region keys eliminate the need for envelope encryption when encrypting objects larger than 4 KB
**Correct answer(s):** A, B
**Explanation:** Multi-Region keys are designed so that primary and replica keys share key ID and key material, allowing ciphertext produced by one regional replica to be decrypted by another without any cross-region call or re-encryption — ideal for DR scenarios. Option C is the most tempting wrong answer, but AWS explicitly requires you to manage key policies, grants, and tags independently on each replica key, since they are not automatically kept in sync.

### Question 13 [Domain: 1] [Type: Single-Answer]
**Scenario:** Account A stores a database credential secret named `prod/db-creds` in AWS Secrets Manager. An application running in Account B needs to retrieve this secret at runtime, but the security team wants to avoid duplicating or copying the secret into Account B, and wants to grant access using a native Secrets Manager capability tied specifically to that one secret.
**Options:**
A. Export the secret value and store it as a plaintext environment variable in Account B's application configuration
B. Attach a resource-based (secret) policy to `prod/db-creds` granting the Account B IAM role `secretsmanager:GetSecretValue`, and ensure the encryption key's policy also allows that role to decrypt
C. Create an IAM user in Account A and share its long-term access keys with the Account B team
D. Use Amazon Cognito identity pools to federate Account B's application into Account A
**Correct answer(s):** B
**Explanation:** Secrets Manager supports attaching a resource-based policy directly to an individual secret, which is the native mechanism for granting another AWS account's principal permission to retrieve that specific secret's value (paired with the KMS key policy allowing decryption — which requires the secret to use a customer managed key, since an AWS managed key's policy cannot be edited to add an external account). Option A defeats the purpose of using Secrets Manager entirely by reintroducing a hardcoded, unmanaged credential.

### Question 14 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A security engineer enables Amazon GuardDuty's foundational protection in an account that runs workloads on Amazon EKS and stores data in Amazon S3. She wants to know which of the following protections are NOT automatically included with foundational protection and instead must be separately enabled as additional GuardDuty protection plans. (Select TWO)
**Options:**
A. S3 Protection (monitoring S3 data plane events for suspicious access patterns)
B. Analysis of VPC Flow Logs for network-based threat indicators
C. Analysis of CloudTrail management events for suspicious API activity
D. EKS Protection (monitoring Kubernetes audit logs and runtime activity for threats)
E. Analysis of DNS query logs for connections to known malicious domains
**Correct answer(s):** A, D
**Explanation:** GuardDuty's foundational protection automatically includes VPC Flow Logs, CloudTrail management events, and DNS query log analysis at no separate enablement step, but S3 Protection and EKS Protection are distinct, separately-enabled protection plans that add monitoring of S3 data events and Kubernetes audit/runtime activity, respectively. Options B, C, and E are tempting since they sound like "extra" features, but they are actually part of the always-on foundational data sources.

### Question 15 [Domain: 1] [Type: Single-Answer]
**Scenario:** An enterprise customer wants employees to authenticate through their existing corporate SAML 2.0 identity provider (Okta) and then be granted temporary AWS credentials so a custom internal web application can call AWS APIs directly on their behalf, scoped to only the permissions each employee's department requires. The company does not want to build or manage its own user directory.
**Options:**
A. Configure an Amazon Cognito identity pool with the corporate Okta SAML IdP as an authentication provider, mapping SAML attributes to IAM roles for fine-grained, role-based temporary credentials
B. Create an IAM user for every employee and have Okta provision long-term access keys
C. Configure an Amazon Cognito user pool alone, since it can directly vend temporary IAM credentials
D. Use AWS Directory Service to create a new managed Active Directory and re-create every employee as a new user
**Correct answer(s):** A
**Explanation:** Cognito identity pools natively support SAML 2.0 identity providers as an authentication source and can map SAML assertion attributes to different IAM roles, enabling department-scoped temporary credentials without building a separate user store. Option C is a common mix-up, but a Cognito user pool issues its own authentication tokens and does not itself vend AWS credentials — that is the identity pool's role.

### Question 16 [Domain: 1] [Type: Single-Answer]
**Scenario:** A three-tier application has a web-tier security group (`sg-web`) and an application-tier security group (`sg-app`). The application tier should only accept traffic on port 8080 from instances in the web tier, and the architecture must remain correct even as web-tier instances are scaled in and out with changing private IP addresses.
**Options:**
A. Add an inbound rule to `sg-app` allowing TCP 8080 from the web tier's current private IP CIDR range, and update it manually whenever the range changes
B. Add an inbound rule to `sg-app` allowing TCP 8080 with the source set to `sg-web` (the security group ID) rather than an IP range
C. Add an inbound rule to `sg-app` allowing TCP 8080 from 0.0.0.0/0 and rely on the application to reject unauthorized callers
D. Add an outbound rule to `sg-web` allowing TCP 8080 to 0.0.0.0/0
**Correct answer(s):** B
**Explanation:** Security groups allow you to specify another security group as the source of an inbound rule, which automatically covers any instance associated with that group regardless of IP address changes from scaling — the recommended approach for tier-to-tier traffic. Option A would work initially but is fragile and requires ongoing manual maintenance as instances are replaced or the range changes.

### Question 17 [Domain: 1] [Type: Single-Answer]
**Scenario:** An application running on EC2 instances in a private subnet (no NAT gateway, no internet access) needs to call the Secrets Manager API to retrieve database credentials at startup. The security team requires that this traffic never traverse the public internet, even via a NAT device.
**Options:**
A. Create an interface VPC endpoint (AWS PrivateLink) for Secrets Manager in the VPC, and update the security group and endpoint policy to allow the application to reach it privately
B. Attach an internet gateway to the private subnet's route table just for Secrets Manager traffic
C. Deploy a NAT gateway in the private subnet and restrict its route to only the Secrets Manager service CIDR
D. Move the EC2 instances into the public subnet so they can reach Secrets Manager directly
**Correct answer(s):** A
**Explanation:** An interface VPC endpoint powered by AWS PrivateLink lets resources in a private subnet reach supported AWS service APIs like Secrets Manager entirely over the AWS private network, without any internet gateway or NAT device involved. Option C is tempting since NAT gateways do provide internet egress, but traffic through a NAT gateway still traverses the public internet path to reach the Secrets Manager public endpoint, which violates the requirement.

### Question 18 [Domain: 1] [Type: Single-Answer]
**Scenario:** A retail company's public API, fronted by an Application Load Balancer, is experiencing a credential-stuffing attack where a small number of source IPs are sending an abnormally high volume of login requests per minute, degrading service for legitimate users. The security team wants to automatically throttle or block clients that exceed a defined request threshold within a 5-minute window, without permanently blocking legitimate traffic sources.
**Options:**
A. Create an AWS WAF rate-based rule on the web ACL associated with the ALB, blocking IPs that exceed the configured request threshold within the evaluation window
B. Add a security group rule limiting the number of connections per source IP
C. Enable AWS Shield Advanced, which automatically rate-limits all HTTP requests by default
D. Configure a network ACL deny rule for each offending IP address as it is identified manually
**Correct answer(s):** A
**Explanation:** AWS WAF rate-based rules are purpose-built to automatically track request rates per client IP and block or challenge those exceeding a threshold within a rolling time window, which directly and automatically addresses credential stuffing/application-layer abuse. Option D could technically work but is a manual, reactive process that doesn't scale and doesn't automatically adapt as attacking IPs change.

### Question 19 [Domain: 1] [Type: Single-Answer]
**Scenario:** A security team has identified a specific external IP address that is repeatedly attempting to scan every EC2 instance across several subnets in a VPC. They want to explicitly deny all traffic from this single IP address at the broadest possible scope, affecting every instance in the affected subnets, using a construct that supports explicit deny rules (not just allow rules).
**Options:**
A. Add a deny rule for the IP address to the security group attached to each affected instance
B. Add a deny rule for the IP address to the network ACL associated with the affected subnets
C. Add the IP address to an S3 bucket policy deny statement
D. Create an IAM policy with an explicit deny for the IP address using a condition key
**Correct answer(s):** B
**Explanation:** Network ACLs operate at the subnet level and support explicit allow and deny rules, making them well suited to blocking a known-bad IP address across every instance in one or more subnets with a single rule. Option A is a common wrong choice because security groups only support allow rules (there is no explicit "deny" rule in a security group) — you can only omit a permission, not explicitly block a specific address.

### Question 20 [Domain: 1] [Type: Multiple-Response]
**Scenario:** A security team is designing the trust policy for an `AuditRole` in Account A, which will be assumed by federated users coming through Account B's identity provider for read-only auditing. Beyond restricting the trust policy's `Principal` to Account B's specific role ARN, the team wants to add conditions that further reduce the risk of the role being misused if the trusting principal's own credentials were somehow compromised or reused unexpectedly. Which two conditions should be added to the trust policy?
**Options:**
A. A condition requiring `sts:ExternalId` to equal a specific, pre-shared unique value known only to Account A and Account B
B. A condition requiring `aws:MultiFactorAuthPresent` to equal `true` for the assuming session
C. A `NotAction` element excluding `sts:AssumeRole` from the policy
D. An `Action` element granting `s3:GetObject` directly in the trust policy
E. A `Resource` element listing every S3 bucket in Account A
**Correct answer(s):** A, B
**Explanation:** Adding a unique `sts:ExternalId` mitigates confused-deputy risk, and requiring `aws:MultiFactorAuthPresent` ensures the assuming session itself was established with MFA, both of which tighten the conditions under which the role can be assumed. Options D and E are incorrect because a trust policy only governs *who* can assume the role via `sts:AssumeRole` — it is not the place to define what the role can *do* once assumed (that belongs in the role's permissions policy).

### Question 21 [Domain: 2] [Type: Single-Answer]
**Scenario:** A retail company runs its order database on Amazon RDS for MySQL with a Multi-AZ deployment. During a routine maintenance window, the underlying host of the primary instance experiences a hardware failure. The application connects to the database using the RDS instance endpoint. The company wants to understand what happens without any manual intervention.
**Options:**
A. RDS automatically promotes the standby replica and updates the DNS CNAME record to point to the new primary, typically completing failover within one to two minutes
B. The application must be reconfigured with a new connection string pointing to the standby instance's IP address
C. An administrator must manually initiate a failover using the RDS console or CLI before the standby becomes usable
D. RDS creates a new read replica and promotes it to become the primary instance
**Correct answer(s):** A
**Explanation:** RDS Multi-AZ deployments automatically detect the failure and fail over to the standby in another AZ, updating the DNS CNAME so the application's existing endpoint resolves to the new primary with no manual steps required. Option C is the tempting distractor because manual failover is possible via "reboot with failover," but it is not required for automatic recovery from an actual instance failure.

### Question 22 [Domain: 2] [Type: Single-Answer]
**Scenario:** An Application Load Balancer distributes traffic to a target group of EC2 instances running a Java web application that takes about 45 seconds to fully initialize after starting. Operators notice that newly launched instances are marked healthy and receive traffic prematurely before the application is ready, causing intermittent 502 errors during scale-out events.
**Options:**
A. Increase the ALB idle timeout value
B. Configure a longer health check interval and increase the "healthy threshold" count so instances need more consecutive successful checks
C. Set the health check grace period appropriately and adjust the health check path/interval so checks don't begin evaluating traffic readiness until initialization completes
D. Switch the load balancer type from Application Load Balancer to Network Load Balancer
**Correct answer(s):** C
**Explanation:** Using an appropriate health check grace period (in the Auto Scaling group) combined with a correctly tuned ALB health check interval and threshold ensures instances aren't marked "in service" until they've actually finished initializing. Option A is a distractor since idle timeout only affects long-lived connections, not health check timing during startup.

### Question 23 [Domain: 2] [Type: Single-Answer]
**Scenario:** An order-processing microservice needs to notify three independent downstream systems — inventory management, shipping, and analytics — whenever a new order is placed. Each downstream system must receive every message reliably, process it at its own pace, and be able to be added or removed without impacting the others or the order service.
**Options:**
A. Publish order events to an SNS topic with separate SQS queues subscribed for each downstream system
B. Have the order service call each downstream system's API directly via synchronous HTTP requests
C. Write order events to a single SQS standard queue that all three systems poll
D. Use a single SQS FIFO queue and have each downstream system consume from it in round-robin fashion
**Correct answer(s):** A
**Explanation:** The SNS fan-out pattern lets one published message be delivered to multiple independent SQS queues, giving each subscriber its own durable, decoupled queue to process at its own pace. Option C is the tempting wrong answer because a single shared queue would cause each message to be consumed by only one of the three systems, not all of them.

### Question 24 [Domain: 2] [Type: Single-Answer]
**Scenario:** A financial services company runs its primary application stack in the us-east-1 region and maintains a fully provisioned, identical standby stack in us-west-2 for disaster recovery. The company wants DNS to automatically route all customer traffic to us-west-2 only if health checks against the us-east-1 endpoint fail, and to route back once us-east-1 recovers.
**Options:**
A. Configure a Route 53 weighted routing policy with equal weights for both endpoints
B. Configure a Route 53 failover routing policy with the us-east-1 endpoint as primary and us-west-2 as secondary, both associated with health checks
C. Configure a Route 53 latency-based routing policy across both regions
D. Configure a Route 53 geolocation routing policy directing all traffic to the nearest region
**Correct answer(s):** B
**Explanation:** Failover routing policy is purpose-built for active-passive DR: Route 53 continuously monitors the primary via health checks and automatically shifts DNS answers to the secondary when the primary is unhealthy, then reverts when it recovers. Weighted routing (A) would send traffic to both regions simultaneously regardless of health, which doesn't meet the active-passive requirement.

### Question 25 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company runs a web tier behind an Auto Scaling group and wants the number of running instances to automatically adjust so that the average CPU utilization across the group stays close to 50%, without the operations team having to define specific CloudWatch alarm thresholds or step adjustments manually.
**Options:**
A. Simple scaling policy with a fixed CPU threshold alarm
B. Scheduled scaling action based on anticipated daily traffic patterns
C. Target tracking scaling policy set to maintain average CPU utilization at 50%
D. Step scaling policy with multiple CPU threshold tiers
**Correct answer(s):** C
**Explanation:** Target tracking scaling policies let you specify a target metric value (like 50% average CPU), and Auto Scaling automatically creates and manages the necessary CloudWatch alarms and scaling adjustments to maintain it. Step scaling (D) could also work but requires manually defining multiple threshold tiers, which is exactly the manual effort the scenario says the team wants to avoid.

### Question 26 [Domain: 2] [Type: Single-Answer]
**Scenario:** A startup wants a cost-effective disaster recovery strategy for its application in a secondary AWS region. It can tolerate an RTO of several hours. The plan is to replicate the database continuously to the secondary region and keep only a minimal set of core infrastructure (like the DB instance) running there, while compute resources remain defined as templates/AMIs that would be launched and scaled up only when a disaster is declared.
**Options:**
A. Multi-site active-active
B. Warm standby
C. Pilot light
D. Backup and restore
**Correct answer(s):** C
**Explanation:** Pilot light keeps only the most critical core components (typically the database) continuously running/replicated in the DR region, while the rest of the environment is provisioned from templates and scaled up on-demand during an actual disaster, striking a low-cost balance with a moderate RTO. Warm standby (B) is the tempting distractor, but it keeps a scaled-down but fully functional copy of the entire stack always running, not just the database.

### Question 27 [Domain: 2] [Type: Single-Answer]
**Scenario:** A clickstream analytics platform ingests millions of website events per second. Three separate downstream applications — real-time dashboards, fraud detection, and a data lake loader — each need to independently consume and process the entire event stream in order, and one of them needs the ability to replay events from up to 24 hours ago after a bug fix.
**Options:**
A. Amazon SQS Standard queue
B. Amazon SQS FIFO queue
C. Amazon Kinesis Data Streams
D. Amazon SNS topic with Lambda subscribers
**Correct answer(s):** C
**Explanation:** Kinesis Data Streams allows multiple independent consumer applications to read the same ordered stream of records concurrently and supports configurable retention (up to 365 days) enabling replay, which matches all three requirements. SQS FIFO (B) preserves order but each message is consumed and deleted by effectively one logical consumer group, and it has no built-in replay capability.

### Question 28 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company integrates with several third-party SaaS partners and also needs to react to internal AWS service events (like EC2 state changes). It wants a single, serverless event bus that can filter incoming events by content and route matching events to different targets such as Lambda functions, Step Functions, and SQS queues, without writing custom polling logic.
**Options:**
A. Amazon SNS with multiple topics
B. Amazon EventBridge with event buses and content-based rules
C. Amazon SQS with a single queue polled by all target applications
D. AWS Step Functions with a Choice state
**Correct answer(s):** B
**Explanation:** EventBridge is designed specifically for ingesting events from AWS services and third-party SaaS partners, and its rules support content-based pattern matching to route events to multiple heterogeneous targets. SNS (A) supports message filtering too, but it does not natively integrate with SaaS partner event sources the way EventBridge's partner event buses do.

### Question 29 [Domain: 2] [Type: Single-Answer]
**Scenario:** A financial trading application requires extremely low-latency TCP connections and needs a fixed set of static IP addresses that the company's clients can whitelist in their firewalls. The traffic is not HTTP/HTTPS-based.
**Options:**
A. Application Load Balancer
B. Network Load Balancer
C. Classic Load Balancer
D. Amazon CloudFront
**Correct answer(s):** B
**Explanation:** Network Load Balancer operates at the transport layer, supports ultra-low latency TCP/UDP traffic, and provides a static IP address (or Elastic IP) per Availability Zone, meeting both requirements. ALB (A) is the common wrong choice, but it operates at Layer 7 for HTTP/HTTPS and does not provide static IPs.

### Question 30 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A worker fleet consumes messages from an SQS standard queue to process image uploads. Operators notice that a small number of malformed messages are being received and retried repeatedly by workers, and are never successfully processed, consuming worker capacity indefinitely. Separately, some valid messages are being picked up by a second worker before the first worker finishes processing them.
**Options:**
A. Configure a dead-letter queue with a maxReceiveCount so repeatedly failing messages are moved out of the main queue after a set number of retries
B. Increase the queue's visibility timeout to be longer than the worker's typical message processing time
C. Convert the queue to an SNS topic
D. Decrease the message retention period to 60 seconds
E. Set ReceiveMessageWaitTimeSeconds to 0 to use short polling for faster message delivery
**Correct answer(s):** A, B
**Explanation:** A dead-letter queue with maxReceiveCount isolates poison-pill messages after repeated failures, and increasing the visibility timeout prevents a message from becoming visible to other consumers before the original worker finishes processing it. Option E is a distractor: short polling (wait time of 0) increases the chance of empty responses and duplicate reads across distributed queue servers, rather than solving the described problem.

### Question 31 [Domain: 2] [Type: Single-Answer]
**Scenario:** An enterprise needs an RTO of about 10 minutes for its critical order management system in case its primary region fails. It has decided to run a scaled-down but fully functional version of the entire application stack continuously in a second region, ready to be scaled up to full production capacity quickly when needed.
**Options:**
A. Backup and restore
B. Pilot light
C. Warm standby
D. Multi-site active-active
**Correct answer(s):** C
**Explanation:** Warm standby keeps a scaled-down, fully functional replica of the whole application running at all times in the second region, allowing a fast scale-up and much lower RTO than pilot light, while costing less than a full active-active deployment. Pilot light (B) is the tempting distractor, but it only keeps core data services running, not a fully functional (even if smaller) copy of the application tier, so it would take longer than 10 minutes to bring compute online.

### Question 32 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company is rolling out version 2 of its API and wants to gradually shift a small percentage of production traffic (starting at 10%) from the existing ALB (v1) to a new ALB (v2) using DNS, increasing the percentage over time while monitoring error rates, without requiring any client-side changes.
**Options:**
A. Route 53 simple routing policy
B. Route 53 weighted routing policy
C. Route 53 geoproximity routing policy
D. Route 53 multivalue answer routing policy
**Correct answer(s):** B
**Explanation:** Weighted routing lets you assign relative weights to multiple resource record sets pointing to different endpoints, enabling exactly the kind of gradual, controllable traffic-shifting canary pattern described. Multivalue answer routing (D) is a distractor because it returns multiple IP addresses for basic client-side load balancing/health checking, not proportional traffic-percentage control.

### Question 33 [Domain: 2] [Type: Single-Answer]
**Scenario:** A company has a single AWS Site-to-Site VPN connection linking its on-premises data center to its VPC. Although each VPN connection provisions two tunnels for redundancy on the AWS side, the company's on-premises customer gateway device itself is a single point of failure — if that physical device fails, connectivity is lost entirely. The company wants to eliminate this single point of failure without provisioning AWS Direct Connect.
**Options:**
A. Increase the VPN connection's bandwidth allocation
B. Provision a second Site-to-Site VPN connection terminating on a second, physically separate customer gateway device
C. Enable VPC Flow Logs on the VPN-attached subnet
D. Replace the virtual private gateway with an internet gateway
**Correct answer(s):** B
**Explanation:** Adding a second VPN connection through an entirely separate customer gateway device (ideally in a different physical location) removes the single point of failure on the customer side, while AWS already provides redundant tunnels on its end. Option D is nonsensical for this use case since an internet gateway does not provide encrypted, private connectivity.

### Question 34 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A solutions architect is redesigning a stateful web application that currently runs on a single EC2 instance in one Availability Zone, storing user session data in local instance memory. The company wants to redesign the architecture to survive the loss of an entire Availability Zone with minimal user impact.
**Options:**
A. Deploy EC2 instances across at least two Availability Zones behind an Application Load Balancer, managed by an Auto Scaling group
B. Store session state in a shared, external store such as ElastiCache or DynamoDB instead of local instance memory
C. Increase the size of the single EC2 instance to a larger instance type
D. Keep session data on local instance storage but enable EBS snapshots every hour
E. Deploy a single NAT Gateway in one AZ to reduce cost
**Correct answer(s):** A, B
**Explanation:** Spreading instances across multiple AZs behind an ALB/ASG provides AZ-level fault tolerance, and externalizing session state makes the application stateless so any instance can serve any user's requests after a failover. Vertically scaling a single instance (C) does nothing to protect against an entire AZ becoming unavailable.

### Question 35 [Domain: 2] [Type: Single-Answer]
**Scenario:** A healthcare company must retain backups of its EBS volumes, RDS databases, and DynamoDB tables, and compliance policy requires that copies of these backups automatically be replicated to a second AWS region shortly after each backup completes, across all these services from a single centralized policy.
**Options:**
A. Configure individual EBS snapshot lifecycle policies, RDS automated backups, and DynamoDB point-in-time recovery separately, each with manual cross-region copy scripts
B. Use AWS Backup with a backup plan that includes a cross-region copy rule covering all three resource types
C. Use AWS DataSync to replicate backup files between regions
D. Use S3 Cross-Region Replication on the default backup bucket
**Correct answer(s):** B
**Explanation:** AWS Backup provides a centralized backup plan across multiple supported services (EBS, RDS, DynamoDB, etc.) with a copy rule that automatically copies each recovery point to a destination region on a schedule. Option A would technically work but requires separate manual per-service scripting, which fails the requirement for a single centralized policy.

### Question 36 [Domain: 2] [Type: Single-Answer]
**Scenario:** A mobile gaming company operates a real-time leaderboard used by players in North America, Europe, and Asia. It needs an active-active multi-region database where players in each region can read and write leaderboard data with low local latency, and where updates made in one region automatically propagate to the others with conflict resolution handled by the database.
**Options:**
A. Amazon RDS with cross-region read replicas
B. Amazon DynamoDB with Global Tables
C. Amazon ElastiCache for Redis with cross-region replication groups
D. Amazon Aurora with a single writer instance and cross-region read replicas
**Correct answer(s):** B
**Explanation:** DynamoDB Global Tables provide fully managed, multi-active (multi-master) replication across regions with automatic last-writer-wins conflict resolution, allowing local reads and writes in every region. RDS cross-region read replicas (A) support only a single writable primary region, so writes in other regions aren't possible.

### Question 37 [Domain: 2] [Type: Multiple-Response]
**Scenario:** A media transcoding company runs a fault-tolerant batch processing fleet on EC2 behind an Auto Scaling group. To minimize cost, it wants to use Spot Instances heavily, but must remain resilient to Spot interruptions and avoid the fleet being drastically undersized if one particular instance type becomes scarce.
**Options:**
A. Configure the Auto Scaling group with a mixed instances policy specifying several compatible instance types and sizes
B. Use the capacity-optimized allocation strategy for Spot Instances to reduce interruption frequency
C. Run the entire fleet on a single Spot Instance type to simplify capacity planning
D. Disable Auto Scaling group health checks to prevent unnecessary replacements
E. Set the Spot allocation strategy to launch only in a single Availability Zone
**Correct answer(s):** A, B
**Explanation:** A mixed instances policy with multiple instance types diversifies the Spot capacity pools available to the fleet, and the capacity-optimized allocation strategy selects pools with the most available capacity to reduce interruption rates. Relying on a single instance type (C) or a single AZ (E) concentrates risk and increases the chance of large-scale simultaneous interruptions.

### Question 38 [Domain: 3] [Type: Single-Answer]
**Scenario:** A media company runs a batch video-encoding pipeline that is entirely CPU-bound, performing heavy computational transformations with minimal memory or storage I/O requirements. The company wants to select an EC2 instance family that maximizes price-performance for this specific workload.
**Options:**
A. Memory-optimized instances (R-family)
B. Storage-optimized instances (I-family)
C. Compute-optimized instances (C-family)
D. General-purpose instances (M-family)
**Correct answer(s):** C
**Explanation:** Compute-optimized (C-family) instances offer the highest ratio of vCPU performance per dollar, making them ideal for CPU-bound batch processing like video encoding. General-purpose instances (D) could technically run the workload but provide a less cost-effective balance of CPU versus other resources for a purely compute-bound task.

### Question 39 [Domain: 3] [Type: Single-Answer]
**Scenario:** A financial trading application running on EC2 requires a block storage volume capable of sustaining 64,000 IOPS and sub-millisecond latency for its transactional database, with extremely high durability requirements.
**Options:**
A. EBS gp3
B. EBS io2 Block Express
C. EBS st1
D. Instance store (NVMe SSD)
**Correct answer(s):** B
**Explanation:** io2 Block Express volumes support up to 256,000 IOPS and sub-millisecond latency with 99.999% durability, making them the appropriate choice for this extreme performance requirement. gp3 (A) tops out at a much lower maximum IOPS ceiling (16,000) and would not meet the 64,000 IOPS requirement.

### Question 40 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company hosts a single S3 bucket in the us-east-1 region where users worldwide upload large raw video files directly. Users in Asia and Europe report significantly slower upload speeds compared to users in North America. The company wants to improve upload performance globally without changing the bucket's region or restructuring the application.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket
B. Enable S3 Cross-Region Replication to regions closer to users
C. Switch the bucket's storage class to S3 Intelligent-Tiering
D. Create a CloudFront distribution in front of the bucket for uploads
**Correct answer(s):** A
**Explanation:** S3 Transfer Acceleration routes uploads through the nearest CloudFront edge location and over Amazon's optimized backbone network to the bucket's region, significantly improving upload speed for geographically distant users without any application restructuring. CloudFront (D) is designed to accelerate downloads/content delivery, not client-to-origin uploads.

### Question 41 [Domain: 3] [Type: Single-Answer]
**Scenario:** An application needs an in-memory caching layer that supports automatic Multi-AZ failover with a replica, data persistence options, and pub/sub messaging capabilities for real-time notifications between application components.
**Options:**
A. Amazon ElastiCache for Memcached
B. Amazon ElastiCache for Redis with Multi-AZ enabled
C. Amazon DynamoDB Accelerator (DAX)
D. Amazon RDS with a read replica
**Correct answer(s):** B
**Explanation:** ElastiCache for Redis supports replication, automatic Multi-AZ failover, optional data persistence, and native pub/sub messaging, matching all stated requirements. Memcached (A) is the common distractor, but it is a simpler multi-threaded cache with no built-in replication, persistence, or pub/sub support.

### Question 42 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company serves both static assets (images, CSS, JS) and a dynamic API from the same domain through a single CloudFront distribution. Static assets rarely change and should be cached for a long time at edge locations, while API responses are highly dynamic and should mostly bypass caching. Currently, both are getting the same caching behavior, causing stale API data.
**Options:**
A. Create two separate CloudFront distributions, one for each content type
B. Configure separate cache behaviors within the same distribution using distinct path patterns (e.g., /static/* and /api/*) with different TTL and caching policies
C. Disable caching entirely on the CloudFront distribution
D. Increase the default TTL for the entire distribution
**Correct answer(s):** B
**Explanation:** CloudFront cache behaviors let you define different path patterns within a single distribution, each with its own caching policy and TTL settings, so static content can be cached aggressively while API paths use minimal or no caching. Creating two separate distributions (A) would work but adds unnecessary operational complexity when path-based behaviors solve the problem within one distribution.

### Question 43 [Domain: 3] [Type: Single-Answer]
**Scenario:** A multiplayer game studio needs to improve network performance for a UDP-based real-time game engine used by players globally. The traffic is not HTTP/HTTPS, and the studio wants static anycast IP addresses that route player traffic onto the AWS global network backbone as close to the player as possible, with automatic failover between regional endpoints.
**Options:**
A. Amazon CloudFront
B. AWS Global Accelerator
C. Amazon Route 53 latency-based routing
D. Amazon API Gateway
**Correct answer(s):** B
**Explanation:** Global Accelerator provides static anycast IP addresses and optimizes network paths for both TCP and UDP traffic onto the AWS global backbone, with automatic health-check-based failover — exactly suited to a non-HTTP, latency-sensitive UDP game workload. CloudFront (A) is the tempting distractor, but it is an HTTP/HTTPS content delivery service and does not support arbitrary UDP traffic.

### Question 44 [Domain: 3] [Type: Single-Answer]
**Scenario:** An RDS PostgreSQL primary database is being overwhelmed by a mix of transactional writes from the application and heavy analytical reporting queries run by the BI team, causing slow response times for customer-facing transactions.
**Options:**
A. Enable Multi-AZ on the RDS instance
B. Create one or more RDS Read Replicas and direct the BI reporting queries to them
C. Increase the RDS instance's storage size
D. Enable automated backups with a shorter retention window
**Correct answer(s):** B
**Explanation:** Read Replicas offload read-only query traffic (like reporting) from the primary instance, freeing up its resources for transactional writes and improving overall performance. Multi-AZ (A) is a distractor because its standby is for failover/HA, not for serving read traffic in the standard synchronous Multi-AZ configuration.

### Question 45 [Domain: 3] [Type: Single-Answer]
**Scenario:** An application backed by DynamoDB experiences a read-heavy workload with many repeated lookups for the same set of "hot" items, and the application requires response times in the microsecond range that DynamoDB alone cannot consistently guarantee under this load.
**Options:**
A. Amazon ElastiCache for Redis in front of DynamoDB
B. DynamoDB Accelerator (DAX)
C. DynamoDB auto scaling
D. DynamoDB Global Tables
**Correct answer(s):** B
**Explanation:** DAX is a DynamoDB-native, in-memory caching layer purpose-built to reduce response times from milliseconds to microseconds for read-heavy workloads, and it requires minimal application changes since it's API-compatible with the DynamoDB SDK. ElastiCache (A) could also cache results but would require custom application logic to manage cache population and invalidation, unlike DAX's transparent integration.

### Question 46 [Domain: 3] [Type: Single-Answer]
**Scenario:** A machine learning team runs a shared file system accessed concurrently by hundreds of EC2 training instances. Throughput demand is highly unpredictable — bursting from near-zero to several GB/s during active training runs — and the team does not want to manually provision or pay for throughput capacity during idle periods.
**Options:**
A. Amazon EFS with Bursting Throughput mode
B. Amazon EFS with Elastic Throughput mode
C. Amazon EFS with Provisioned Throughput mode set to the maximum expected value
D. Amazon EBS Multi-Attach io2 volume
**Correct answer(s):** B
**Explanation:** EFS Elastic Throughput mode automatically scales throughput up and down instantly to match actual workload demand, and you pay only for the throughput actually used, ideal for highly variable, unpredictable access patterns. Provisioned Throughput mode (C) would meet peak demand but wastes money during idle periods since it's a fixed, pre-paid allocation.

### Question 47 [Domain: 3] [Type: Single-Answer]
**Scenario:** A research team runs a tightly-coupled HPC simulation using MPI across many EC2 instances within a single Availability Zone. The workload requires the lowest possible network latency and highest throughput between instances, and the team is willing to accept reduced fault tolerance in exchange for this performance.
**Options:**
A. Spread placement group
B. Partition placement group
C. Cluster placement group
D. Default (no placement group)
**Correct answer(s):** C
**Explanation:** Cluster placement groups pack instances close together within a single AZ to achieve low-latency, high-throughput networking, which is ideal for tightly-coupled HPC/MPI workloads. Spread placement groups (A) do the opposite — they spread instances across distinct underlying hardware to maximize fault isolation, at the cost of inter-instance network performance.

### Question 48 [Domain: 3] [Type: Single-Answer]
**Scenario:** Building on an existing cluster-placement-group HPC deployment, the research team wants to further minimize inter-node network latency and jitter for its tightly-coupled MPI application by bypassing the standard operating system networking stack for inter-instance communication.
**Options:**
A. Enable Enhanced Networking with the ENA driver only
B. Attach an Elastic Fabric Adapter (EFA) to the instances
C. Enable Jumbo Frames on the VPC subnet
D. Switch to instances with SR-IOV disabled
**Correct answer(s):** B
**Explanation:** Elastic Fabric Adapter (EFA) provides an OS-bypass networking interface specifically designed for tightly-coupled HPC and MPI workloads, delivering lower and more consistent latency than standard enhanced networking. Standard Enhanced Networking with ENA (A) improves throughput and PPS but still traverses the standard networking stack, not achieving the OS-bypass benefit EFA provides.

### Question 49 [Domain: 3] [Type: Single-Answer]
**Scenario:** A company runs a MySQL-compatible production database on Amazon Aurora and needs a disaster recovery solution that replicates data to a secondary AWS region with typical replication lag under one second, and allows promoting the secondary region to full read/write capability within about a minute if the primary region fails.
**Options:**
A. Aurora Global Database
B. Standard Aurora cross-region snapshot copy
C. Aurora Replicas within the same region
D. RDS automated backups with cross-region copy
**Correct answer(s):** A
**Explanation:** Aurora Global Database uses dedicated, purpose-built storage-level replication to achieve typical cross-region replication lag under one second, and supports fast promotion of a secondary region (typically under a minute) during a regional disaster. Cross-region snapshot copies (B) are periodic and would result in much higher data loss and recovery time than required.

### Question 50 [Domain: 3] [Type: Single-Answer]
**Scenario:** A latency-sensitive public API implemented with AWS Lambda behind API Gateway experiences noticeable response delays for a subset of requests immediately following traffic spikes, caused by cold starts as new execution environments are initialized.
**Options:**
A. Increase the Lambda function's memory allocation only
B. Enable Provisioned Concurrency for the Lambda function
C. Switch the Lambda function's architecture from x86_64 to arm64
D. Increase the API Gateway throttling limits
**Correct answer(s):** B
**Explanation:** Provisioned Concurrency keeps a specified number of execution environments pre-initialized and ready to respond immediately, eliminating cold-start latency for the configured capacity. Increasing memory (A) can shorten cold-start duration somewhat but does not eliminate the fundamental cold-start delay the way pre-warmed provisioned environments do.

### Question 51 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A big data processing job runs on an EC2 instance and requires very high-IOPS, low-latency temporary scratch storage during processing that does not need to survive an instance stop or termination. The final processed output, however, must be durably stored and made available to downstream applications for the long term.
**Options:**
A. Use an EBS gp3 volume for temporary scratch space
B. Use the instance's local instance store (NVMe SSD) for temporary scratch space
C. Use Amazon EFS for temporary scratch space
D. Store the final processed output in Amazon S3
E. Store the final processed output in the instance's local instance store
**Correct answer(s):** B, D
**Explanation:** Instance store volumes provide very high IOPS and low latency ideal for ephemeral scratch data, since the data loss on stop/terminate is acceptable per the scenario, while S3 provides the durable, long-term storage needed for final output that downstream applications can access. Storing final output on instance store (E) is incorrect because that data would be lost if the instance stops or terminates, violating the durability requirement.

### Question 52 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A global e-commerce company serves a web application to users worldwide, backed by an Amazon RDS database. Users report slow page loads for static assets, and the backend also experiences high read latency for frequently-accessed product data queried repeatedly from the database.
**Options:**
A. Deploy Amazon CloudFront in front of the application to cache static and cacheable content at edge locations
B. Deploy Amazon ElastiCache to cache frequently-accessed product query results, reducing repeated load on RDS
C. Enable DynamoDB Accelerator (DAX) in front of the RDS database
D. Deploy AWS Global Accelerator to cache database query results closer to users
E. Migrate all static assets into the RDS database as BLOBs for faster retrieval
**Correct answer(s):** A, B
**Explanation:** CloudFront reduces latency for static/cacheable content by serving it from edge locations closer to users, while ElastiCache reduces repeated read load on RDS by caching frequently-accessed query results in memory. DAX (C) is a distractor because it only works with DynamoDB, not RDS, so it cannot be used here.

### Question 53 [Domain: 3] [Type: Multiple-Response]
**Scenario:** A company runs EC2 instances in private subnets with no route to an internet gateway or NAT Gateway. These instances need low-latency, cost-effective access to Amazon S3 and Amazon DynamoDB within the same region, without incurring per-GB data processing charges or adding extra network hops.
**Options:**
A. Create a Gateway VPC Endpoint for Amazon S3
B. Create a Gateway VPC Endpoint for Amazon DynamoDB
C. Create an Interface VPC Endpoint (PrivateLink) for Amazon S3
D. Deploy a NAT Gateway in a public subnet and route traffic through it
E. Establish an AWS Direct Connect connection to the region
**Correct answer(s):** A, B
**Explanation:** Gateway VPC Endpoints for S3 and DynamoDB provide private, low-latency routing to these services within the same region entirely over the AWS network, with no hourly or per-GB data processing charges, unlike Interface Endpoints or NAT Gateways. Interface Endpoint for S3 (C) would technically work but incurs hourly and per-GB charges, making it less cost-effective than the free Gateway Endpoint for this same-region use case.

### Question 54 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs production workloads on EC2 across two AWS Regions, using a mix of instance families (M6i, C6i, R6i) that change periodically as workloads evolve. Finance has approved a 3-year commitment to reduce compute costs, but the platform team wants the discount to apply automatically regardless of instance family, size, OS, tenancy, or region, without manual exchange transactions. Which purchasing option best meets this requirement?

**Options:**
A. Standard Reserved Instances
B. Convertible Reserved Instances
C. Compute Savings Plans
D. EC2 Instance Savings Plans

**Correct answer(s):** C

**Explanation:** Compute Savings Plans automatically apply their discount to usage across any instance family, size, OS, tenancy, region, and even to Fargate and Lambda usage, requiring no manual action as workloads shift. EC2 Instance Savings Plans (D) are tempting because they offer a slightly higher discount, but they are locked to a specific instance family within a single region, which fails the multi-region flexibility requirement.

### Question 55 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company stores application logs in S3. Logs are accessed frequently for the first 30 days for debugging, then only occasionally for compliance audits for up to one year, and must be retained for 7 years total but almost never accessed after year one (retrieval within a few hours is acceptable if ever needed). The company wants to minimize storage cost while meeting these access patterns automatically.

**Options:**
A. Keep all objects in S3 Standard for the full 7 years
B. Transition to S3 Standard-IA after 30 days, then to S3 Glacier Flexible Retrieval after 365 days
C. Transition directly to S3 Glacier Deep Archive after creation
D. Enable S3 Intelligent-Tiering with no lifecycle rules and take no further action

**Correct answer(s):** B

**Explanation:** A lifecycle policy moving objects to Standard-IA after 30 days (matching the drop in access frequency) and then to Glacier Flexible Retrieval after 365 days (matching the shift to rare, hours-tolerant compliance access) minimizes cost at each stage while meeting retrieval-time needs. Option C is tempting for a 7-year retention requirement, but Deep Archive's 12+ hour retrieval time doesn't fit the frequent access needed in the first 30 days.

### Question 56 [Domain: 4] [Type: Single-Answer]
**Scenario:** A startup is launching a new mobile app on DynamoDB. The team has no historical traffic data, expects unpredictable spikes of up to 10x normal load during viral growth events, and wants to avoid both throttling and the operational overhead of capacity planning during the initial launch phase, even if it means paying a higher per-request rate temporarily.

**Options:**
A. Provisioned capacity with Application Auto Scaling
B. On-Demand capacity mode
C. Provisioned capacity with a fixed high RCU/WCU ceiling
D. Provisioned capacity with Reserved Capacity purchased upfront

**Correct answer(s):** B

**Explanation:** On-Demand mode instantly accommodates unpredictable spikes without any capacity planning and charges only per request, which is ideal for a launch with unknown traffic patterns. Option A is tempting, but Auto Scaling reacts to CloudWatch alarms with a delay of several minutes, meaning a sudden 10x spike could still cause throttling before scaling catches up.

### Question 57 [Domain: 4] [Type: Single-Answer]
**Scenario:** An application running on EC2 instances in a private subnet uploads several terabytes of data per day to an S3 bucket in the same Region. All traffic currently routes through a NAT Gateway, and the monthly bill shows significant NAT Gateway data processing charges as the primary cost driver. The team wants to eliminate this specific cost without changing the private subnet architecture.

**Options:**
A. Deploy a second NAT Gateway in another AZ to distribute the load
B. Increase the NAT Gateway's bandwidth allocation
C. Add a Gateway VPC Endpoint for S3 and update the route table
D. Replace the NAT Gateway with a NAT instance

**Correct answer(s):** C

**Explanation:** A Gateway VPC Endpoint for S3 routes traffic directly to S3 over the AWS network without traversing the NAT Gateway, eliminating the per-GB data processing charge entirely at no extra cost for the endpoint itself. Option A is tempting for availability, but it doubles NAT Gateway hourly and processing charges instead of eliminating them.

### Question 58 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A company wants to reduce EC2 costs by shifting eligible workloads to Spot Instances. Select the **two** workloads below that are best suited for Spot Instances.

**Options:**
A. A stateless batch video-transcoding job that checkpoints progress and can resume on a new instance if interrupted
B. A single-instance legacy monolith application that must run continuously with no redundancy
C. A CI/CD build-agent fleet that pulls jobs from a queue and can be replaced at any time
D. A primary relational database instance handling synchronous transactional writes
E. A real-time bidding system requiring guaranteed capacity within milliseconds

**Correct answer(s):** A, C

**Explanation:** Both the transcoding job and the CI/CD build agents are stateless, fault-tolerant, and can handle interruption with a two-minute warning, making them ideal Spot candidates that can cut compute costs significantly. Option D is a common wrong pick because databases require guaranteed, uninterrupted capacity and consistent availability, which Spot cannot reliably provide.

### Question 59 [Domain: 4] [Type: Single-Answer]
**Scenario:** A machine learning team stores training datasets in S3 that are easily and cheaply regenerated from an original source system if lost. The datasets are accessed only occasionally but must be retrievable within minutes when needed, and all processing occurs within a single Region. The team wants the lowest possible storage cost and accepts the reduced durability of single-AZ storage given the data is reproducible.

**Options:**
A. S3 Standard-IA
B. S3 One Zone-IA
C. S3 Glacier Instant Retrieval
D. S3 Intelligent-Tiering

**Correct answer(s):** B

**Explanation:** S3 One Zone-IA offers about 20% lower storage cost than Standard-IA by storing data in a single Availability Zone, which is an acceptable tradeoff here since the data is easily reproducible if that AZ is lost. Standard-IA (A) is tempting for its multi-AZ durability, but that added resilience is unnecessary cost given the source data can be regenerated.

### Question 60 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company runs a production MySQL database on an Amazon RDS db.r5.xlarge instance that operates 24/7 and is expected to run in exactly this configuration for the next three years without change. The company has capital available to pay the full cost upfront in exchange for the maximum possible discount.

**Options:**
A. On-Demand pricing
B. 1-year No Upfront Reserved Instance
C. 3-year All Upfront Reserved Instance
D. Migrate to Aurora Serverless v2

**Correct answer(s):** C

**Explanation:** A 3-year All Upfront Reserved Instance provides the deepest discount available for RDS when usage is stable and long-term, and paying upfront maximizes the savings since the company has the capital available. Option D is tempting as a modernization path, but Serverless v2 is priced for variable workloads and offers no benefit — and added complexity — for a database with a fixed, unchanging 24/7 workload.

### Question 61 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company currently has 3 VPCs in the same Region and same account that need full connectivity to each other, with modest and infrequent data transfer between them. There are no near-term plans to add more VPCs or accounts. The team wants the most cost-effective way to connect these VPCs.

**Options:**
A. AWS Transit Gateway
B. VPC Peering
C. AWS Direct Connect
D. Site-to-Site VPN

**Correct answer(s):** B

**Explanation:** VPC Peering has no hourly charge and only incurs standard data transfer rates, making it the most cost-effective choice for a small, static number of VPCs with light traffic. Transit Gateway (A) is tempting for its operational simplicity at scale, but its hourly per-attachment charge plus per-GB data processing fee adds unnecessary cost when only 3 VPCs are involved with no growth planned.

### Question 62 [Domain: 4] [Type: Single-Answer]
**Scenario:** An application team provisioned a 500 GB gp2 EBS volume purely to obtain higher baseline IOPS (gp2 IOPS scale with volume size), even though the application only occasionally needs bursts above the default 3,000 IOPS baseline. This oversizing is increasing storage costs unnecessarily. The team wants to right-size storage cost while independently controlling IOPS and throughput.

**Options:**
A. Increase the gp2 volume size further to raise baseline IOPS
B. Switch to a gp3 volume and provision IOPS and throughput independently of size
C. Switch to an io2 volume with provisioned IOPS matching peak demand
D. Move the data to instance store (ephemeral) volumes

**Correct answer(s):** B

**Explanation:** gp3 decouples IOPS and throughput from volume size, letting the team provision only the capacity and performance actually needed, which is both cheaper per-GB than gp2 and avoids paying for excess size just to get IOPS. io2 (C) is tempting for guaranteed high IOPS, but it costs more per-provisioned-IOPS than gp3 and is intended for latency-sensitive, high-durability workloads this use case doesn't require.

### Question 63 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company has run an Amazon ElastiCache for Redis cluster for two years with a consistently stable, predictable workload and no significant change in traffic expected going forward. The team wants a deeper cost discount than standard On-Demand node pricing offers, without changing the application's caching architecture.

**Options:**
A. Migrate to ElastiCache Serverless
B. Purchase ElastiCache Reserved Nodes for a 1- or 3-year term
C. Enable Multi-AZ with automatic failover
D. Add Amazon CloudFront in front of the application

**Correct answer(s):** B

**Explanation:** ElastiCache Reserved Nodes provide a significant discount over standard On-Demand node pricing in exchange for a 1- or 3-year commitment, which is ideal for a stable, predictable workload like this one. Migrating to ElastiCache Serverless (A) is tempting as a modernization path, but Serverless pricing is designed for variable workloads and offers no cost benefit — and adds unnecessary complexity — for a cluster with a fixed, unchanging workload.

### Question 64 [Domain: 4] [Type: Multiple-Response]
**Scenario:** A company uses Amazon EFS for a non-production development environment where redundancy across multiple Availability Zones is not required. Files are accessed heavily for the first 30 days after creation and then rarely afterward. The team wants to reduce storage costs. Select the **two** actions that would reduce cost for this environment.

**Options:**
A. Enable EFS Lifecycle Management to automatically transition files to EFS Infrequent Access after 30 days of no access
B. Create the file system using the One Zone storage class instead of Standard, since Multi-AZ redundancy isn't needed
C. Manually script a nightly job to copy old files to S3 and delete them from EFS
D. Increase the file system's provisioned throughput mode to Elastic
E. Disable Lifecycle Management and keep all files on EFS Standard indefinitely

**Correct answer(s):** A, B

**Explanation:** Lifecycle Management automatically moves rarely-accessed files to the cheaper IA storage class, and using the One Zone storage class (roughly half the cost of Standard) is appropriate since this dev environment doesn't need multi-AZ resilience. Option C is a tempting manual alternative, but it adds operational overhead and risk compared to EFS's built-in, automatic lifecycle transitions.

### Question 65 [Domain: 4] [Type: Single-Answer]
**Scenario:** A company has a large EC2 fleet and, based on CloudWatch metrics, suspects many instances are significantly over-provisioned for CPU and memory. The team wants an AWS-native tool that uses machine learning to analyze historical utilization and automatically recommend specific instance type and size changes (including across families) to reduce cost, without manually analyzing each instance's metrics.

**Options:**
A. AWS Trusted Advisor
B. AWS Compute Optimizer
C. AWS Cost Explorer
D. AWS Budgets

**Correct answer(s):** B

**Explanation:** AWS Compute Optimizer analyzes historical CloudWatch utilization data with machine learning and produces specific, actionable rightsizing recommendations across instance families for EC2, EBS, Lambda, and more. Trusted Advisor (A) is tempting since its cost optimization checks flag low-utilization instances, but it only provides a basic idle-instance alert rather than detailed, ML-driven rightsizing recommendations across instance types.
