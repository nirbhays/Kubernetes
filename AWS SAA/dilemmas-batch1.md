# SAA-C03 Two-Answer Dilemmas — Batch 1 of 2
Focus: Security/IAM, Networking, Compute, General Architecture
Original practice content — not real exam questions.

---

### Dilemma 1
**Scenario:** A company runs a fleet of EC2 instances that need to call the S3 and DynamoDB APIs. A new engineer has been storing an IAM user's access key and secret key in a config file on each instance's root volume so the SDK can authenticate. A security audit has flagged this practice and asked for a fix that removes long-lived credentials from the instances entirely, with no application code changes to how credentials are loaded (the SDK's default credential chain is already in use).
**Option A:** Create an IAM role with the required S3 and DynamoDB permissions and attach it to the instances via an instance profile, then delete the IAM user's access keys.
**Option B:** Rotate the IAM user's access keys every 24 hours using AWS Secrets Manager automatic rotation, and update the config file via a scheduled SSM automation document.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** An instance profile role eliminates long-lived credentials on disk altogether, while key rotation only shortens their lifespan and still leaves static secrets present.

---

### Dilemma 2
**Scenario:** A financial services firm needs cross-account access so that a monitoring account can read CloudWatch metrics and logs from 40 member accounts in an AWS Organization. Security policy states that no long-term credentials may ever be shared between accounts, and access must be auditable per assumption event via CloudTrail.
**Option A:** Create an IAM role in each member account with a trust policy allowing the monitoring account to assume it, and have the monitoring tooling call sts:AssumeRole.
**Option B:** Create an IAM user in each member account, generate access keys, and store them encrypted in AWS Secrets Manager in the monitoring account for the tooling to retrieve.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Cross-account IAM roles use temporary STS credentials with a distinct AssumeRole CloudTrail event, satisfying "no long-term credentials" and per-event auditability, whereas IAM user keys are inherently long-lived.

---

### Dilemma 3
**Scenario:** A retail company's VPC has a public subnet with a web tier and a private subnet with an application tier. The security team wants to explicitly deny all inbound traffic from a specific set of malicious IP ranges at the subnet boundary, in addition to normal security group rules on individual instances, and wants the block to apply even to traffic between instances in the same subnet if sourced from those ranges.
**Option A:** Add explicit deny rules for the malicious CIDR ranges in the subnet's Network ACL, ordered before the allow rules.
**Option B:** Update every instance's security group to remove any allow rule that overlaps with the malicious CIDR ranges.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Only NACLs support explicit deny rules evaluated at the subnet level regardless of instance-level security group configuration, which is required to guarantee the block applies universally.

---

### Dilemma 4
**Scenario:** A media company hosts a global video-on-demand website. Users in Asia are reporting high latency when loading the site's static homepage assets (HTML, CSS, JS) even though the origin S3 bucket is in us-east-1. Dynamic API calls are fast enough already. The company wants to reduce latency for the static assets specifically with minimal operational overhead.
**Option A:** Put Amazon CloudFront in front of the S3 bucket with caching enabled for the static asset paths.
**Option B:** Enable S3 Cross-Region Replication to buckets in ap-southeast-1 and ap-northeast-1, and use Route 53 latency-based routing to direct users to the nearest bucket.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** CloudFront caches content at edge locations globally with a single configuration change, whereas cross-region replication requires managing multiple bucket copies and routing logic for what is fundamentally a caching problem.

---

### Dilemma 5
**Scenario:** An e-commerce company runs an Auto Scaling group of EC2 instances behind an Application Load Balancer. During flash sales, traffic spikes 10x within two minutes, and new instances take about 4 minutes to boot and warm up, causing a period of degraded performance before scaling catches up. The company wants to reduce the lag between demand spikes and available capacity.
**Option A:** Configure a scheduled scaling action to pre-provision extra capacity ahead of known flash sale start times, combined with target tracking scaling for organic spikes.
**Option B:** Switch the scaling policy from target tracking to simple scaling with a larger cooldown period so the ASG reacts more conservatively to spikes.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Scheduled scaling pre-provisions capacity before a known demand event, directly solving the boot-time lag, while a larger cooldown in simple scaling would make the ASG react more slowly, worsening the problem.

---

### Dilemma 6
**Scenario:** A healthcare startup stores patient records in an S3 bucket and must ensure that objects can never be permanently deleted for 7 years to satisfy compliance, even by an account administrator, while still allowing new versions of objects to be uploaded and old versions to eventually expire after the retention period.
**Option A:** Enable S3 Object Lock in Compliance mode with a 7-year retention period on the bucket, with versioning enabled.
**Option B:** Enable S3 Object Lock in Governance mode with a 7-year retention period, and remove s3:BypassGovernanceRetention permission from all IAM policies.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Compliance mode prevents even the root user from deleting or overwriting locked object versions during the retention period, whereas Governance mode's protection depends entirely on IAM permissions that could be misconfigured or later granted.

---

### Dilemma 7
**Scenario:** A company runs a three-tier application where the app tier in private subnets needs outbound internet access solely to download OS patches and call third-party APIs; it must never be reachable from the internet. The company operates in three Availability Zones and wants a highly available design without operating any patching servers themselves.
**Option A:** Deploy a NAT Gateway in each Availability Zone's public subnet and route each private subnet's default outbound traffic to the NAT Gateway in its own AZ.
**Option B:** Deploy a single NAT Instance on a t3.medium EC2 instance in one public subnet and route all private subnets' outbound traffic to it, with an Auto Scaling group of size 1 for recovery.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** A NAT Gateway per AZ is a managed, highly available service with no instances to patch, while a single NAT instance is a single point of failure and requires the company to operate and patch it themselves.

---

### Dilemma 8
**Scenario:** A company wants developers to be able to launch EC2 instances only of specific approved instance types, only from an approved AMI, and only with a specific set of tags, across all accounts in their AWS Organization, and wants this enforced even if a developer has AdministratorAccess in their own account.
**Option A:** Attach a Service Control Policy (SCP) at the OU level that denies ec2:RunInstances unless the request matches the approved instance types, AMI, and required tags.
**Option B:** Create an IAM permissions boundary with the same conditions and attach it to every IAM role and user that can call ec2:RunInstances.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** SCPs apply organization-wide and cap even administrator permissions including the root user, while permissions boundaries must be attached individually to every principal and can be altered by an account admin.

---

### Dilemma 9
**Scenario:** A gaming company runs a UDP-based multiplayer backend on EC2 instances and needs a static IP address that can fail over instantly to a standby instance in another AZ if health checks fail, without changing client-side configuration or DNS TTL-dependent failover.
**Option A:** Allocate an Elastic IP, associate it with a Network Load Balancer, and let the NLB route to healthy targets across AZs.
**Option B:** Allocate an Elastic IP and write a Lambda function triggered by CloudWatch Alarms to re-associate the EIP to the standby instance when the primary fails a health check.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** An NLB natively supports UDP, provides static IPs per AZ, and performs sub-second health-check-based failover without any custom automation, whereas manually re-associating an EIP introduces detection and re-association delay.

---

### Dilemma 10
**Scenario:** A company's data science team needs temporary access to a production S3 bucket for a one-time analysis job that will run for about 6 hours from an on-premises server that is not integrated with AWS SSO or IAM Identity Center. The security team insists no permanent credentials be created for this one-off task.
**Option A:** Have an existing IAM role assumed via sts:AssumeRole from an already-trusted identity, generating temporary credentials with a 6-hour session duration for the on-prem server to use.
**Option B:** Create a new IAM user scoped to only that S3 bucket, generate an access key, and instruct the team to delete the user manually after the job finishes.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Temporary STS credentials automatically expire after the session duration with no manual cleanup step, while an IAM user's access keys remain valid indefinitely until someone remembers to delete them.

---

### Dilemma 11
**Scenario:** A company runs a monolithic application on a single large EC2 instance and wants to modernize it to run as containers. They want to minimize the operational burden of managing container orchestration infrastructure, including patching and scaling the underlying compute, and their workloads have unpredictable, bursty traffic patterns.
**Option A:** Migrate the containers to Amazon ECS running on AWS Fargate.
**Option B:** Migrate the containers to Amazon ECS running on EC2 with an Auto Scaling group managing the cluster capacity.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Fargate removes the need to provision, patch, or scale underlying EC2 instances entirely, directly satisfying "minimize operational burden," whereas ECS on EC2 still requires managing the cluster's compute layer.

---

### Dilemma 12
**Scenario:** A company needs to connect its on-premises data center, which has a stable 500 Mbps of consistent traffic to AWS for database replication, to a VPC. The workload is sensitive to jitter and requires more consistent network performance than the public internet provides, but the company has a 6-month timeline and wants to avoid the lead time and cost of a dedicated physical circuit.
**Option A:** Set up an AWS Site-to-Site VPN connection over the internet with BGP routing.
**Option B:** Provision a Direct Connect dedicated connection with a private virtual interface to the VPC.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Site-to-Site VPN can be provisioned within hours with no physical circuit lead time, while Direct Connect typically takes weeks to months to install, making it unsuitable for the stated 6-month-inclusive timeline pressure and cost sensitivity.

---

### Dilemma 13
**Scenario:** A SaaS company's application stores user session data that must survive individual EC2 instance termination and be shared across all instances behind an Application Load Balancer, since the ALB does not guarantee session affinity to the same instance on every request in their current configuration. Access latency must remain in single-digit milliseconds.
**Option A:** Store session data in Amazon ElastiCache for Redis, shared across all instances.
**Option B:** Enable sticky sessions on the Application Load Balancer so each user always reaches the same instance that holds their session in local memory.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** ElastiCache provides a shared, durable session store accessible by any instance, while sticky sessions only pin a user to one instance and still lose session data entirely if that instance terminates.

---

### Dilemma 14
**Scenario:** A company runs a batch processing workload on EC2 that can tolerate interruption and restart, processing jobs from an SQS queue over an estimated continuous run of 14 months. The workload needs to run 24/7 during that period, and the company wants the lowest possible compute cost.
**Option A:** Purchase Reserved Instances (Standard, 1-year term) for the baseline EC2 capacity.
**Option B:** Run the workload entirely on Spot Instances with no On-Demand or Reserved capacity as a fallback.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** A known, continuous 24/7 need for over a year is exactly the steady-state scenario Reserved Instances are priced for, while pure Spot risks interruption-driven processing gaps despite the workload tolerating restarts, making cost-per-completed-job less predictable and potentially higher under sustained Spot price pressure.

---

### Dilemma 15
**Scenario:** A company wants to give a third-party SaaS analytics vendor secure, limited read access to specific objects in one of its S3 buckets. The vendor has its own AWS account, and the company does not want to create or manage any IAM users or share any credentials with the vendor directly.
**Option A:** Create a cross-account IAM role with a trust policy naming the vendor's AWS account ID and a bucket policy granting that role read access, then give the vendor the role ARN to assume.
**Option B:** Generate a set of pre-signed URLs for each object and email them to the vendor, regenerating them whenever they expire.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** A cross-account role scales to any number of objects and future additions without manual regeneration, while pre-signed URLs are per-object, time-limited, and require ongoing manual re-issuance as objects change.

---

### Dilemma 16
**Scenario:** A company runs a public-facing web application on EC2 instances in an Auto Scaling group behind an ALB, and has recently been hit by a Layer 7 HTTP flood attack targeting a specific login endpoint, distinct from generic volumetric DDoS traffic. They want to specifically rate-limit and filter malicious requests to that endpoint without writing custom traffic-inspection code.
**Option A:** Configure AWS WAF with a rate-based rule on the ALB targeting the login endpoint path.
**Option B:** Enable AWS Shield Advanced on the ALB and Auto Scaling group.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** AWS WAF's rate-based rules can inspect and throttle requests to a specific URL path at Layer 7, while Shield Advanced is designed for broader network and transport layer DDoS protection and does not provide path-specific rate limiting on its own.

---

### Dilemma 17
**Scenario:** A company's IAM policy grants a developer group access to start and stop EC2 instances, but only instances tagged Environment=Dev. A developer reports they cannot stop an instance tagged Environment=Dev that they themselves launched. Investigation shows the instance is missing the tag because it was applied after launch via a separate API call under a different set of credentials, and the IAM policy uses a condition on aws:ResourceTag.
**Option A:** Verify the tag was actually applied to the specific EC2 instance resource (not just visible in the console cache) and confirm the IAM policy's condition key matches ec2:ResourceTag/Environment for the ec2:StopInstances action correctly.
**Option B:** Add ec2:CreateTags to the developer group's allowed actions so they can retag the instance themselves before stopping it.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** The root cause is a tag/policy condition mismatch on the existing resource, so granting an unrelated CreateTags permission works around the symptom rather than fixing the authorization condition itself.

---

### Dilemma 18
**Scenario:** A company runs a multi-tier application where the web tier in public subnets must be reachable on port 443 from the internet, and the database tier in private subnets must only accept connections on port 3306 from the web tier's instances, never directly from the internet, even if a web tier instance's security group is later misconfigured to allow wider inbound access.
**Option A:** Set the database tier's security group inbound rule to reference the web tier's security group ID as the source on port 3306.
**Option B:** Set the database tier's security group inbound rule to allow the web tier's private subnet CIDR range as the source on port 3306.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Referencing a security group as the source ties access to actual group membership regardless of IP changes, while a CIDR-based rule would still allow any instance later launched in that subnet, including one unintentionally exposed, to reach the database.

---

### Dilemma 19
**Scenario:** A company needs to run a stateless REST API that receives highly unpredictable traffic, sometimes zero requests for hours and sometimes hundreds per second, and wants to pay only for actual compute time used with no idle infrastructure cost, while individual requests complete in under 2 seconds.
**Option A:** Build the API using AWS Lambda functions behind Amazon API Gateway.
**Option B:** Run the API on an ECS Fargate service with a minimum task count of 1 and target tracking scaling based on request count.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Lambda charges only for actual invocation time with zero cost during idle periods, while a Fargate service with a minimum of 1 task incurs continuous cost even with zero traffic.

---

### Dilemma 20
**Scenario:** A company's compliance team requires that all data written to a specific S3 bucket be encrypted at rest using a customer-managed KMS key that the security team fully controls, including the ability to disable the key to immediately revoke access to all objects in the bucket, and any attempt to upload without specifying that key must be rejected outright.
**Option A:** Set the bucket's default encryption to SSE-KMS with the customer-managed key, and add a bucket policy that denies s3:PutObject unless the request specifies that exact KMS key ARN.
**Option B:** Set the bucket's default encryption to SSE-KMS with the customer-managed key, and rely on default encryption to automatically apply the key to all uploads.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Only an explicit deny condition on the KMS key ARN guarantees rejection of uploads that don't use it, whereas default bucket encryption alone does not prevent a request from explicitly specifying a different key or algorithm.

---

### Dilemma 21
**Scenario:** A company operates in a single AWS Region across three Availability Zones and runs a relational database workload requiring strong read scalability for a reporting dashboard, automatic failover for the primary database, and minimal application changes to route read traffic separately from write traffic.
**Option A:** Deploy Amazon RDS with a Multi-AZ primary instance and add one or more Read Replicas for the reporting workload.
**Option B:** Deploy Amazon RDS with Multi-AZ enabled only, and point the reporting dashboard at the standby replica's endpoint during business hours.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** RDS Read Replicas are explicitly designed for offloading read traffic with their own endpoint, while the Multi-AZ standby is not accessible for reads and exists purely for failover.

---

### Dilemma 22
**Scenario:** A company wants to allow its EC2 instances in a private subnet to access Amazon S3 and DynamoDB without routing traffic over the public internet or through a NAT Gateway, in order to reduce data transfer costs and avoid any exposure to the internet, while keeping the solution fully managed with no additional compute to maintain.
**Option A:** Create a Gateway VPC Endpoint for S3 and DynamoDB and update the private subnet's route table to use it.
**Option B:** Create an Interface VPC Endpoint (powered by AWS PrivateLink) for S3 and DynamoDB in the private subnet.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** S3 and DynamoDB are the two services that use Gateway Endpoints, which are free and route-table-based, whereas Interface Endpoints for these services don't exist and would incur unnecessary per-hour and per-GB PrivateLink charges for other services that require them.

---

### Dilemma 23
**Scenario:** A company's application on EC2 needs to encrypt and decrypt small amounts of sensitive configuration data at application startup, calling the encryption service potentially thousands of times per minute across a fleet of 200 instances. The security team requires that the underlying cryptographic keys never leave AWS's control and that all key usage be logged.
**Option A:** Use AWS KMS with a customer-managed key and the Encrypt/Decrypt API calls from the application via the AWS SDK.
**Option B:** Use AWS CloudHSM to generate and store the keys, and have each instance connect directly to the CloudHSM cluster for every encrypt/decrypt operation.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** KMS is designed for exactly this kind of frequent, application-level encrypt/decrypt workload with built-in CloudTrail logging and no cluster management, while CloudHSM at that call volume across 200 instances adds unnecessary operational complexity and cost for a requirement KMS already satisfies (keys never leave AWS-managed HSMs).

---

### Dilemma 24
**Scenario:** A company is designing a VPC architecture where an application tier needs to reach an internal company API hosted in a different VPC owned by a partner business unit, in the same AWS Region, with private IP connectivity, no transitive routing to other VPCs, and no bandwidth bottleneck concerns since a small number of VPCs are involved.
**Option A:** Set up a VPC Peering connection between the two VPCs and update route tables on both sides.
**Option B:** Set up an AWS Transit Gateway and attach both VPCs to it.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** VPC Peering is the simpler, no-additional-cost solution for a single point-to-point connection between two VPCs, while Transit Gateway is justified when connecting many VPCs and needing transitive routing, neither of which applies here.

---

### Dilemma 25
**Scenario:** A company runs a critical order-processing application on EC2 behind an ALB and Auto Scaling group in one Region, and leadership now requires the ability to recover the entire application stack in a different Region within about 10 minutes of a Regional outage, accepting some additional monthly cost for reduced recovery time, but the company is not willing to pay for a fully duplicated, continuously running production-scale environment in the second Region.
**Option A:** Implement a warm standby disaster recovery strategy: run a scaled-down version of the full stack continuously in the secondary Region, and scale it up on failover.
**Option B:** Implement a pilot light disaster recovery strategy: keep only the database replicated and continuously running in the secondary Region, with AMIs pre-built for the application tier to launch on failover.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Warm standby keeps the full application stack already running at reduced scale so failover only requires scaling up, achieving a ~10-minute RTO, while pilot light still needs to launch and configure the entire application tier from scratch, typically taking longer.

---

*End of Batch 1 (25 dilemmas). Batch 2 will cover storage, databases, serverless/messaging, monitoring, and cost/migration scenarios.*
