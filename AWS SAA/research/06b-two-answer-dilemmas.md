# AWS SAA-C03 — 50 Two-Answer Dilemmas

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
**Scenario:** A retail company's VPC has a public subnet with a web tier and a private subnet with an application tier. The security team wants to explicitly deny all inbound traffic entering either subnet from a specific set of malicious external IP ranges, with the block enforced at the subnet boundary regardless of how any individual instance's security group is configured, and without having to audit and update every instance's security group rules whenever the malicious range list changes.
**Option A:** Add explicit deny rules for the malicious CIDR ranges in the subnet's Network ACL, ordered before the allow rules.
**Option B:** Update every instance's security group to remove any allow rule that overlaps with the malicious CIDR ranges.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Only NACLs support explicit deny rules evaluated at the subnet boundary independently of each instance's security group, letting the team block the ranges in one place instead of auditing and maintaining every instance's rules individually.

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
**Scenario:** A company wants developers to be able to launch EC2 instances only of specific approved instance types, only from an approved AMI, and only with a specific set of tags, across all member accounts in their AWS Organization, and wants this enforced even if a developer has AdministratorAccess in their own account.
**Option A:** Attach a Service Control Policy (SCP) at the OU level that denies ec2:RunInstances unless the request matches the approved instance types, AMI, and required tags.
**Option B:** Create an IAM permissions boundary with the same conditions and attach it to every IAM role and user that can call ec2:RunInstances.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** SCPs apply to every principal in the member accounts they're attached to, including each account's root user, while permissions boundaries must be attached individually to every principal and can be altered or removed by an account admin.

---

### Dilemma 9
**Scenario:** A gaming company runs a UDP-based multiplayer backend on EC2 instances and needs a static IP address that can fail over quickly to a standby instance in another AZ if health checks fail, without changing client-side configuration or relying on DNS TTL-dependent failover.
**Option A:** Allocate an Elastic IP, associate it with a Network Load Balancer, and let the NLB route to healthy targets across AZs.
**Option B:** Allocate an Elastic IP and write a Lambda function triggered by CloudWatch Alarms to re-associate the EIP to the standby instance when the primary fails a health check.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** An NLB natively supports UDP, provides a static IP per AZ, and automatically fails targets in and out of service based on its own configurable health checks with no custom automation, whereas manually re-associating an EIP depends on an alarm evaluation period plus a separate re-association step, adding extra detection and failover latency.

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
**Scenario:** A company needs to connect its on-premises data center, which generates a stable 500 Mbps of traffic to AWS for asynchronous database replication, to a VPC using a dynamically routed connection. The replication workload can tolerate the variable latency of an internet-based path, but the team still wants redundant, BGP-based routing rather than a single static tunnel. The company has a hard 6-month go-live deadline and wants to avoid the lead time, upfront hardware, and cost of provisioning a dedicated physical circuit.
**Option A:** Set up an AWS Site-to-Site VPN connection over the internet with BGP routing over redundant tunnels.
**Option B:** Provision a Direct Connect dedicated connection with a private virtual interface to the VPC.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Site-to-Site VPN can be stood up within hours with no physical circuit lead time or dedicated hardware cost, comfortably meeting the deadline and cost constraints for a workload that doesn't have a hard low-jitter requirement, whereas Direct Connect's ordering and installation lead time (commonly several weeks to a few months) and higher upfront cost are unnecessary here.

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
**Option A:** Verify the tag was actually applied to the specific EC2 instance resource (not just visible in the console cache) and confirm the IAM policy's condition key correctly matches the resource tag for the ec2:StopInstances action.
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
**The decisive difference (one sentence):** RDS Read Replicas are explicitly designed for offloading read traffic with their own endpoint, while the classic Multi-AZ standby instance is not accessible for direct reads and exists purely for failover.

---

### Dilemma 22
**Scenario:** A company wants to allow its EC2 instances in a private subnet to access Amazon S3 and DynamoDB without routing traffic over the public internet or through a NAT Gateway, in order to reduce data transfer costs and avoid any exposure to the internet, while keeping the solution fully managed with no additional compute to maintain.
**Option A:** Create a Gateway VPC Endpoint for S3 and DynamoDB and update the private subnet's route table to use it.
**Option B:** Create an Interface VPC Endpoint (powered by AWS PrivateLink) for S3 and DynamoDB in the private subnet.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** Gateway Endpoints for S3 and DynamoDB are free and configured entirely through route table entries; DynamoDB has no Interface Endpoint option at all, and although S3 also supports Interface Endpoints, choosing one here would add unnecessary hourly and per-GB PrivateLink charges for a requirement a free Gateway Endpoint already fully satisfies.

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

### Dilemma 26
**Scenario:** A media company stores 50 TB of archived video project files that are accessed unpredictably — sometimes a file is retrieved twice in the same week, sometimes not for eight months. All data currently lives in S3 Standard, and the finance team wants storage costs cut without any engineering effort to classify or move objects. Retrieval latency must remain in milliseconds when files are accessed. No object should ever become permanently unavailable due to an Availability Zone failure.
**Option A:** Move the data to S3 One Zone-IA to cut costs, since access is infrequent and it stores data more cheaply than S3 Standard or Standard-IA.
**Option B:** Move the data to S3 Intelligent-Tiering, letting AWS automatically shift objects between access tiers based on observed usage patterns.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** S3 One Zone-IA stores data in a single AZ and can lose objects entirely in an AZ failure, which violates the durability requirement, while Intelligent-Tiering keeps multi-AZ resilience and automates tiering with no lifecycle rule authoring.

### Dilemma 27
**Scenario:** A fintech company runs a heavily transactional PostgreSQL workload on RDS that requires consistent sub-millisecond storage latency and sustained 20,000 IOPS regardless of burst credit balance. The volume size is only 200 GB, so baseline IOPS from capacity alone won't reach the target. The team wants to provision IOPS independently of volume size and avoid any throughput variability.
**Option A:** Use EBS gp3 volumes and provision the additional IOPS above the included baseline.
**Option B:** Use EBS io2 volumes, which are purpose-built for high, consistent IOPS on critical database workloads.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** gp3 tops out at 16,000 provisioned IOPS per volume — below the required 20,000 — and is not designed for the highest, most consistent-latency tier, while io2 (including io2 Block Express) supports up to 256,000 IOPS with 99.999% durability, matching the workload's strict consistency requirement.

### Dilemma 28
**Scenario:** An engineering firm needs a shared file system for a fleet of Windows EC2 instances running a legacy CAD application that depends on SMB protocol features, Active Directory-based access control, and Distributed File System (DFS) namespaces. Multiple engineers across departments must access the same share concurrently with native Windows file permissions enforced.
**Option A:** Deploy Amazon EFS and mount it on the Windows instances using an NFS client.
**Option B:** Deploy Amazon FSx for Windows File Server, joined to the existing AWS Managed Microsoft AD.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** EFS speaks NFS and has no native SMB or Windows ACL/DFS support, while FSx for Windows File Server is purpose-built with full SMB, NTFS permissions, and DFS namespace compatibility.

### Dilemma 29
**Scenario:** A compliance team must retain 7 years of financial audit logs that are essentially never read except during a regulatory audit, which happens roughly once every two to three years and allows several hours of retrieval lead time. The company wants the absolute lowest per-GB storage cost and is fine waiting up to 12 hours for data when the rare retrieval event occurs.
**Option A:** Store the logs in S3 Glacier Flexible Retrieval using Standard retrieval tier.
**Option B:** Store the logs in S3 Glacier Deep Archive.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Both retrieval times fit within the tolerated window, but Deep Archive is priced roughly 4x cheaper per GB than Flexible Retrieval, and since absolute lowest cost is the stated priority, Deep Archive's 12-hour standard retrieval window still comfortably fits an access pattern that only occurs once every few years.

### Dilemma 30
**Scenario:** A manufacturing company wants to replace an aging on-premises file server with cloud storage but must keep a local cache of frequently accessed files for low-latency access by factory floor applications, while the full dataset lives durably in AWS. Applications on-premises use standard SMB and NFS file shares and cannot be rewritten to call S3 APIs directly.
**Option A:** Deploy AWS Storage Gateway in Volume Gateway mode to present iSCSI block volumes backed by S3.
**Option B:** Deploy AWS Storage Gateway in File Gateway mode to present NFS/SMB file shares backed by S3.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** The requirement is file-based SMB/NFS access with local caching of hot files, which is exactly File Gateway's design, whereas Volume Gateway exposes iSCSI block storage, not file shares.

### Dilemma 31
**Scenario:** An e-commerce company runs its production database on RDS MySQL and needs protection against an entire Availability Zone outage with automatic failover and zero data loss (synchronous replication) for its transactional workload. The team separately also wants to offload read-heavy reporting queries so they don't compete with production writes.
**Option A:** Configure an RDS Read Replica in a different AZ and route both writes and reporting reads to it during an outage.
**Option B:** Configure Multi-AZ deployment for synchronous failover protection, and add one or more Read Replicas for reporting query offload.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Read Replicas use asynchronous replication and are not an HA/failover mechanism, so only Multi-AZ provides the synchronous, zero-data-loss automatic failover the availability requirement demands, while replicas separately solve the read-scaling need.

### Dilemma 32
**Scenario:** A SaaS company operating an Aurora MySQL database wants to serve read traffic to users in three continents with sub-second local read latency in each region, and needs the ability to promote a secondary region to full read/write within about a minute if the primary region fails.
**Option A:** Create RDS Cross-Region Read Replicas in each target region pointing back to the Aurora primary.
**Option B:** Enable Aurora Global Database with secondary regions attached to the global cluster.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Aurora Global Database uses dedicated storage-layer replication with typical lag under 1 second and can promote a secondary region in under a minute via managed planned failover, while cross-region read replicas replicate at the MySQL binlog layer with higher lag and a much slower manual promotion process.

### Dilemma 33
**Scenario:** A startup's traffic is extremely spiky and unpredictable — near zero for days, then a 100x burst during a marketing campaign lasting a few hours. The team has no reliable way to forecast these bursts in advance and wants to avoid both throttling during spikes and paying for idle provisioned capacity.
**Option A:** Use DynamoDB Provisioned Capacity with Application Auto Scaling configured on a target utilization metric.
**Option B:** Use DynamoDB On-Demand capacity mode.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Auto Scaling reacts to sustained CloudWatch utilization changes over minutes and can throttle sudden unpredictable spikes, whereas On-Demand instantly accommodates up to double the previous peak traffic (once that peak has been sustained for 30 minutes) with no capacity planning at all.

### Dilemma 34
**Scenario:** A gaming company needs a single DynamoDB table's data actively writable from application servers in the US, Europe, and Asia simultaneously, with each region seeing the other regions' writes within roughly a second, and automatic conflict resolution for concurrent writes to the same item.
**Option A:** Enable DynamoDB Streams in each region and write custom Lambda functions to replicate changes to tables in the other regions.
**Option B:** Enable DynamoDB Global Tables across the three regions.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Global Tables provide fully managed multi-active replication with built-in last-writer-wins conflict resolution, while a DIY Streams+Lambda approach requires building and maintaining custom replication and conflict-handling logic that AWS already offers natively.

### Dilemma 35
**Scenario:** A social media backend needs a sub-millisecond in-memory cache to store leaderboard data using sorted sets, needs pub/sub messaging for real-time notifications, and requires automatic failover with a replicated cluster if the primary node fails. High availability is a hard requirement.
**Option A:** Use Amazon ElastiCache for Memcached for its simple, multi-threaded architecture.
**Option B:** Use Amazon ElastiCache for Redis with Multi-AZ and automatic failover enabled.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Memcached has no replication, persistence, pub/sub, or advanced data structures like sorted sets, while Redis natively supports all of these plus Multi-AZ automatic failover.

### Dilemma 36
**Scenario:** A serverless application uses Lambda functions that scale to thousands of concurrent executions, each opening its own connection to an RDS PostgreSQL database. The database is now hitting its maximum connection limit and throwing connection errors during traffic spikes, even though CPU and memory utilization on the DB instance remain low.
**Option A:** Upgrade the RDS instance to a larger instance class to raise the maximum connection limit.
**Option B:** Add Amazon RDS Proxy in front of the database to pool and share connections across Lambda invocations.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** The bottleneck is connection count, not compute capacity, and RDS Proxy solves that directly by pooling and multiplexing connections, whereas a larger instance only raises the ceiling temporarily while wasting money on unneeded CPU/memory.

### Dilemma 37
**Scenario:** An analytics dashboard performs the same handful of complex, expensive DynamoDB queries thousands of times per minute from many concurrent users, and product needs response times in the microsecond range for these specific hot queries without changing the application's data model.
**Option A:** Place Amazon ElastiCache for Redis in front of DynamoDB and manually implement cache-aside logic in the application.
**Option B:** Add DynamoDB Accelerator (DAX) as a caching layer in front of the table.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** DAX is a DynamoDB-API-compatible, write-through cache that requires minimal code changes and delivers microsecond reads, while a generic Redis cache-aside pattern requires substantially more custom application logic to keep in sync.

### Dilemma 38
**Scenario:** A company runs a fixed, steady-state fleet of EC2 instances, Fargate tasks, and Lambda functions across three accounts, with total compute spend fairly predictable over the next 3 years. They want the largest possible discount and don't want to be locked into specific instance families or regions, since their architecture team frequently changes instance types and may shift workloads to serverless.
**Option A:** Purchase Standard Reserved Instances for each instance family and size currently in use.
**Option B:** Purchase a Compute Savings Plan covering the committed hourly spend.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Standard RIs apply only to EC2 (and select other provisioned services) and cannot cover Fargate or Lambda usage at all, and are further locked to a specific instance family and region, while Compute Savings Plans apply automatically across instance family, size, OS, region, and to Fargate and Lambda usage alike — a direct fit for a team whose spend spans all three and whose instance choices change often.

### Dilemma 39
**Scenario:** A data science team runs large nightly batch jobs that process petabytes of log data over 4-6 hours, are fully fault-tolerant via checkpointing, and can restart from the last checkpoint if interrupted. Cost minimization is the top priority, and job timing has some flexibility.
**Option A:** Run the batch jobs on Reserved Instances purchased for the compute fleet.
**Option B:** Run the batch jobs on Spot Instances, using a fleet with diversified instance types.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Fault-tolerant, checkpointable, interruption-tolerant batch workloads are the textbook Spot use case that can save up to 90% over On-Demand, while Reserved Instances save meaningfully less and require a 1-3 year commitment regardless of whether the batch capacity is actually used every night.

### Dilemma 40
**Scenario:** An operations team manages an S3 bucket with millions of objects whose access patterns are highly varied and unknown in advance, and they want ongoing cost optimization without writing or maintaining lifecycle transition rules based on object age, while also wanting protection against paying retrieval fees for objects that turn out to still be frequently accessed.
**Option A:** Write S3 Lifecycle rules that transition objects to S3 Standard-IA after 30 days and Glacier after 90 days.
**Option B:** Enable S3 Intelligent-Tiering on the bucket.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Intelligent-Tiering monitors actual per-object access patterns and moves objects between tiers automatically with no retrieval fees, whereas fixed-age Lifecycle rules can incorrectly demote still-hot objects and incur unnecessary retrieval charges.

### Dilemma 41
**Scenario:** A cloud operations manager wants an ongoing, automated mechanism to receive specific EC2, EBS, and Lambda rightsizing recommendations based on actual historical CloudWatch utilization metrics (CPU, memory via CloudWatch agent, network) to reduce over-provisioned resources across hundreds of accounts.
**Option A:** Review AWS Trusted Advisor's cost optimization checks across the accounts.
**Option B:** Review AWS Compute Optimizer's rightsizing recommendations across the accounts.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Compute Optimizer uses machine learning on detailed historical utilization metrics to generate specific instance-type and size rightsizing recommendations, while Trusted Advisor's cost checks are simpler threshold-based flags (e.g., idle instances) without ML-driven sizing analysis.

### Dilemma 42
**Scenario:** A backend team runs a fleet of stateless, horizontally-scaled web servers on EC2 that handle steady, predictable baseline traffic 24/7. The application is already compiled for multiple CPU architectures via a portable build pipeline, and management wants to reduce the compute bill without introducing interruption risk since this is customer-facing production traffic with an SLA.
**Option A:** Migrate the fleet to Spot Instances to take advantage of steep discounts.
**Option B:** Migrate the fleet to Graviton (arm64)-based instances of an equivalent size.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Spot Instances can be reclaimed with two minutes' notice and are unsuitable for SLA-bound steady production traffic, while Graviton instances offer up to ~40% better price-performance with no interruption risk, fitting the always-on, SLA-sensitive requirement.

### Dilemma 43
**Scenario:** A mid-size company needs a disaster recovery strategy for its critical order-processing system with an RTO of about 10 minutes and an RPO of a few minutes. Budget constraints rule out running a fully duplicated, always-on production-scale environment in the DR region, but the team needs core infrastructure already running and ready to scale up quickly.
**Option A:** Implement a pilot light strategy, keeping only core database replication and minimal always-on infrastructure in the DR region.
**Option B:** Implement a warm standby strategy, running a scaled-down but fully functional version of the entire stack in the DR region at all times.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Pilot light typically needs tens of minutes to hours to scale application-tier infrastructure up from near-zero, while warm standby keeps the full stack already running at reduced capacity, which is what reliably achieves a 10-minute RTO.

### Dilemma 44
**Scenario:** A healthcare company must ensure zero downtime and zero data loss even during a complete regional AWS outage, with users transparently served from whichever region is healthy at any given moment. The compliance team has approved essentially unlimited budget for this specific system given the regulatory risk of any downtime.
**Option A:** Implement a backup and restore DR strategy with cross-region snapshot copies taken every few hours.
**Option B:** Implement a multi-site active-active strategy with full production stacks live and serving traffic in two or more regions simultaneously.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Backup and restore has RTO/RPO measured in hours and cannot meet a zero-downtime, zero-data-loss requirement, while multi-site active-active is the only strategy on the DR spectrum that achieves near-zero RTO and RPO by running live in multiple regions concurrently.

### Dilemma 45
**Scenario:** A company runs dozens of EC2 instances and RDS databases across 15 AWS accounts under AWS Organizations and needs a centrally managed, policy-driven backup solution with consistent retention schedules, cross-region copy, and cross-account backup vault protection against accidental or malicious deletion in the source account.
**Option A:** Configure Amazon EventBridge rules to trigger a Lambda function that creates EBS/RDS snapshots and copies them to another account's snapshot repository.
**Option B:** Configure AWS Backup with organization-wide backup policies and cross-account backup vaults.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** AWS Backup natively provides centralized, policy-based scheduling, cross-region/cross-account copy, and vault lock protections across an entire Organization, while a custom EventBridge/Lambda pipeline requires building and maintaining all of that orchestration and security logic manually.

### Dilemma 46
**Scenario:** A retail company runs its web application behind Application Load Balancers in two separate regions for disaster recovery. They need DNS-level automatic failover so that if health checks against the primary region's ALB fail, traffic is automatically redirected to the secondary region's ALB, with the ability to define which region is primary.
**Option A:** Configure Route 53 failover routing policy with health checks on each regional ALB endpoint.
**Option B:** Configure AWS Global Accelerator with endpoint groups in both regions.
**Best answer:** A
**Second-best distractor:** B
**The decisive difference (one sentence):** The requirement explicitly calls for DNS-level failover with a designated primary/secondary relationship, which is exactly Route 53's failover routing policy, while Global Accelerator routes traffic at the network layer through static anycast IP addresses rather than DNS resolution, making it a different mechanism even though it also supports health-check-driven rerouting.

### Dilemma 47
**Scenario:** An order-processing system requires that each customer's orders be processed in the exact sequence they were placed, and no order may ever be processed twice even under high concurrency and retries. Message throughput is moderate (a few hundred messages per second per customer group).
**Option A:** Use an SQS Standard queue with a client-side sequence number embedded in each message body.
**Option B:** Use an SQS FIFO queue with message group IDs per customer and deduplication enabled.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** SQS Standard provides best-effort, not guaranteed, ordering and can deliver duplicates, while FIFO queues guarantee strict per-message-group ordering and exactly-once processing through built-in deduplication.

### Dilemma 48
**Scenario:** An e-commerce platform needs a new order event to simultaneously trigger an inventory update service, a shipping notification service, and a fraud detection service, and also wants the ability to route different event types to different targets based on content filtering rules without writing custom routing code, plus native integration with dozens of AWS service events and third-party SaaS event sources.
**Option A:** Publish the order event to an SNS topic with three SQS queue subscriptions, one per consuming service.
**Option B:** Publish the order event to Amazon EventBridge and define rules that route to each target based on event content.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** EventBridge provides native content-based filtering/routing rules and built-in integrations with many AWS services and SaaS partners out of the box, whereas SNS fan-out to SQS requires each subscribing queue to filter or the consumer application to implement content-based routing logic itself.

### Dilemma 49
**Scenario:** An IoT platform ingests telemetry from 500,000 devices continuously, and multiple independent downstream consumers (real-time analytics, long-term storage, and anomaly detection) each need to read and replay the exact same stream of records independently, with the ability to reprocess the last 24 hours of data if a consumer has a bug.
**Option A:** Use Amazon SQS Standard queues, with one queue per downstream consumer, fed by a fan-out from the ingestion layer.
**Option B:** Use Amazon Kinesis Data Streams, letting each consumer read independently via its own iterator/position in the stream.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** SQS deletes a message once consumed and offers no native replay, while Kinesis retains records for a configurable window (up to 365 days with extended retention) and allows multiple independent consumers to read and replay the same data at their own pace.

### Dilemma 50
**Scenario:** A loan approval workflow involves a strict sequence of steps — credit check, fraud scoring, manual review (which can pause for up to 5 days waiting on a human), and final decision — with built-in visual tracking of exactly which step each application is on, automatic retries with backoff per step, and the ability to branch logic based on each step's output.
**Option A:** Chain the steps using SQS queues and Lambda functions, where each Lambda processes its stage and pushes to the next queue.
**Option B:** Model the entire workflow as an AWS Step Functions state machine, using a Wait/Task Token pattern for the manual review pause.
**Best answer:** B
**Second-best distractor:** A
**The decisive difference (one sentence):** Step Functions natively provides visual per-execution state tracking, built-in retry/backoff and branching logic, and long-running human-approval waits via task tokens, all of which a hand-rolled SQS/Lambda chain would need to build and maintain from scratch.
