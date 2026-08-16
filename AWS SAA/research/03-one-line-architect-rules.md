# AWS SAA-C03 — One-Line Architect Rules

*These are quick-recall heuristics for exam pattern-matching, not absolute rules — real-world architecture decisions always depend on context, cost, and exceptions that a one-liner can't capture.*

1. If an EC2 instance needs to call AWS APIs, attach an IAM role instead of storing long-term access keys on the instance.
2. If a third party or another AWS account needs access to your resources, use a cross-account IAM role with a trust policy rather than sharing IAM user credentials.
3. If granting a third-party SaaS vendor cross-account access, require an ExternalId condition in the trust policy to prevent the confused-deputy problem.
4. If you need to limit the maximum permissions a delegated administrator can grant to others, attach a permissions boundary to the IAM role/user they manage.
5. If workforce users need single sign-on across many AWS accounts, use AWS IAM Identity Center rather than creating individual IAM users per account.
6. If an on-prem Active Directory must federate into AWS, use SAML 2.0 federation with STS AssumeRoleWithSAML, or AWS Directory Service AD Connector, which proxies sign-in requests to your on-prem AD without replicating directory data into AWS.
7. If a mobile or web app needs users to sign in with Google/Facebook/Apple and get temporary AWS credentials, use Amazon Cognito Identity Pools (which call STS under the hood) instead of embedding IAM keys in the app.
8. If access requirements depend on user attributes (department, project tags) rather than fixed roles, use attribute-based access control (ABAC) with IAM/resource tags instead of maintaining many near-duplicate roles.
9. If you need short-lived, auto-expiring credentials for a specific task, use STS AssumeRole with a limited session duration rather than issuing IAM user access keys.
10. If you must guarantee the root user is never used for daily operations, enable MFA on root, remove its access keys, and delegate work to IAM roles/Identity Center users (root is still required for a handful of account-level tasks, e.g., closing the account).
11. If you need account-wide guardrails that even account admins cannot override (e.g., "never leave this region"), use Service Control Policies (SCPs) in AWS Organizations rather than IAM policies alone.
12. If sensitive IAM actions (e.g., deleting a bucket) should require an extra factor, add an aws:MultiFactorAuthPresent condition to the IAM policy.
13. If you need encryption at rest with the least operational overhead and no need to control the key, use SSE-S3/AWS-owned keys at no extra charge; if you need to control the key policy, enable audit trails, or manage key rotation, use SSE-KMS with a customer managed key (CMK) — note SSE-KMS can hit KMS request-rate limits on very high-throughput workloads.
14. If you need automatic yearly rotation of the cryptographic material behind a KMS key, enable automatic rotation on a symmetric customer managed KMS key (not supported for asymmetric/HMAC keys or keys with manually imported material).
15. If you must supply and control your own key material for regulatory reasons while still using KMS APIs, import key material into a KMS key rather than letting AWS generate it.
16. If you need a single-tenant, FIPS 140-2 Level 3 validated hardware device where you manage the full key lifecycle outside AWS's shared KMS infrastructure, use CloudHSM instead of KMS.
17. If a resource encrypted with a customer managed KMS key must be accessed from another AWS account, the KMS key policy must explicitly grant that account/principal access in addition to the consumer's IAM policy (both are evaluated together, not either/or).
18. If you need the same logical KMS key usable across multiple regions without re-encrypting data on migration, use KMS multi-Region keys (they share key material but remain distinct key resources per region, not one literal global key).
19. If an application needs to encrypt large payloads client-side without sending the plaintext to KMS, use envelope encryption via GenerateDataKey rather than calling Encrypt directly on the data.
20. If database credentials must rotate automatically on a schedule, use Secrets Manager rather than Parameter Store or hardcoded credentials — it has built-in Lambda rotation logic for RDS, Aurora, Redshift, and DocumentDB, letting you rotate without redeploying application code.
21. If you only need to store plain or encrypted configuration values (feature flags, non-rotating API keys) at low/no cost without native rotation workflows, use SSM Parameter Store SecureString.
22. If secrets must be organized hierarchically per environment/app and referenced by path (e.g., /prod/app/db-password), use Parameter Store's path-based hierarchy.
23. If you need cross-account access to a specific secret, share it via a Secrets Manager resource policy rather than duplicating the secret in each account; for cross-region access, use Secrets Manager's multi-Region secret replication instead.
24. If EC2 instances in a subnet need stateful, instance-level inbound/outbound filtering, use Security Groups (return traffic is automatically allowed).
25. If you need stateless, subnet-level filtering with explicit ordered allow and deny rules (including denying a specific bad-actor IP), use a Network ACL, since Security Groups cannot express explicit deny rules.
26. If you need private connectivity from a VPC to S3 or DynamoDB without traversing the public internet or a NAT Gateway, use a Gateway VPC Endpoint (route-table based, no hourly charge).
27. If you need private connectivity from a VPC to most other AWS services (e.g., SNS, SQS, KMS, Secrets Manager, SSM, Kinesis) or a partner SaaS over PrivateLink, use an Interface VPC Endpoint (backed by an ENI) instead of routing through a NAT Gateway, not a Gateway endpoint.
28. If you need to centrally inspect/filter traffic between VPCs, to on-prem, or to the internet with stateful rules, use AWS Network Firewall (or a Gateway Load Balancer for third-party virtual appliances) rather than relying on SGs/NACLs alone.
29. If you need to protect a public web app from common exploits like SQL injection or XSS at Layer 7, put AWS WAF in front of CloudFront/ALB/API Gateway.
30. If you need to rate-limit abusive clients or block/allow by country, use a WAF rate-based rule or geo-match rule rather than building this logic in the application.
31. Every AWS account and internet-facing resource is already covered by Shield Standard for free automatic network/transport-layer DDoS mitigation; only move to Shield Advanced when you need cost protection, 24/7 DRT support, and enhanced detection for large/complex attacks.
32. If you need automated, continuous threat detection from VPC Flow Logs, DNS logs, and CloudTrail (e.g., compromised credentials, crypto-mining, port scanning) without deploying agents, use GuardDuty.
33. If you need to discover and classify sensitive data such as PII stored in S3 buckets, use Macie rather than manually auditing bucket contents.
34. If you need a single pane of glass to aggregate and prioritize findings from GuardDuty, Macie, Inspector, and WAF/third-party tools across accounts, use Security Hub.
35. If you need to scan EC2 instances and container images for software vulnerabilities and unintended network exposure, use Inspector rather than GuardDuty (GuardDuty detects active threats/behavior; Inspector assesses vulnerabilities and configuration exposure).
36. If data access patterns are unknown or unpredictable, use S3 Intelligent-Tiering (automatically moves objects between access tiers with no retrieval fees, only a small monitoring fee per object); for known cold data, use lifecycle rules into Glacier instead.
37. If an object is accessed infrequently but needs millisecond retrieval, use S3 Standard-IA for multi-AZ resilience or One Zone-IA only if the data is easily reproducible (it lives in a single AZ and is lost if that AZ fails).
38. If archived data must be retrievable within minutes and accessed rarely, use S3 Glacier Instant Retrieval; if retrieval can tolerate minutes-to-hours and access is a few times a year, use Glacier Flexible Retrieval.
39. If data is archived for years with almost no retrieval and cost must be minimized, use S3 Glacier Deep Archive (standard retrieval within about 12 hours, bulk retrieval up to 48 hours).
40. If objects need automatic transitions between storage classes over time, configure S3 Lifecycle rules instead of scripting manual moves.
41. If compliance mandates objects cannot be deleted or overwritten even by the root account, use S3 Object Lock in Compliance mode (Governance mode can still be bypassed by users with special IAM permissions).
42. If objects must exist in another AWS region for DR, latency, or compliance, enable S3 Cross-Region Replication (only applies to objects created after replication is enabled; use S3 Batch Replication to backfill existing objects).
43. If EC2 needs block storage optimized for high, consistent IOPS on a single instance (e.g., large transactional DB), use Provisioned IOPS SSD (io2 Block Express) rather than gp3.
44. If an EBS volume must be attached to multiple EC2 instances simultaneously, use EBS Multi-Attach (limited to io1/io2 within a single AZ, and requires a cluster-aware file system — standard ext4/xfs will corrupt data).
45. If you need cost-effective, incremental backups of EBS volumes, use EBS Snapshots (stored in S3; each snapshot after the first only captures changed blocks).
46. If an EC2 instance must move to a different Availability Zone, snapshot its EBS volume and restore the snapshot as a new volume in the target AZ (EBS volumes cannot span or move between AZs directly).
47. If multiple EC2 instances or containers across AZs need shared, POSIX-compliant file storage, use EFS instead of EBS (EBS is single-instance/single-AZ except Multi-Attach within one AZ).
48. If EFS files are accessed infrequently, enable EFS Lifecycle Management to EFS-IA to reduce storage cost automatically.
49. If EFS throughput must scale predictably and independently of the amount of data stored, use Provisioned Throughput mode (Bursting mode ties throughput credits to storage size).
50. If a Windows workload needs a native SMB file share with Active Directory integration, use FSx for Windows File Server rather than EFS (EFS is Linux/NFS only).
51. If a workload needs high-performance, low-latency scratch storage for HPC or machine learning, use FSx for Lustre, optionally linked directly to an S3 bucket as its data repository.
52. If migrating an on-premises NetApp ONTAP environment to AWS with existing NFS/SMB/snapshot workflows, use FSx for NetApp ONTAP to minimize re-architecture.
53. If a Linux workload needs high IOPS, snapshots, and compression similar to on-prem ZFS, use FSx for OpenZFS.
54. If a relational database requires automatic HA within a Region, think RDS Multi-AZ (failover is automatic but takes roughly 60–120 seconds; in the standard Multi-AZ DB instance deployment the standby is not readable — use the newer Multi-AZ DB cluster deployment if you need a readable standby).
55. If a relational database needs to scale read throughput, add RDS Read Replicas (replication is asynchronous, so replicas can lag behind the primary and should not be used for strongly consistent reads).
56. If RDS needs a DR strategy across regions, use a cross-region Read Replica and promote it manually during an outage (this is a manual DR action, not an automatic failover).
57. If RDS storage usage grows unpredictably and downtime from manual resizing is unacceptable, enable RDS Storage Auto Scaling.
58. If you need a MySQL/PostgreSQL-compatible database with higher throughput, storage that auto-scales up to 128 TiB, and faster recovery than RDS, choose Aurora over standard RDS.
59. If an Aurora cluster fails over, application connections should use the cluster's Reader/Writer endpoints rather than instance endpoints, since Aurora promotes a replica to writer in as little as ~30 seconds and updates the endpoint automatically.
60. If a workload has unpredictable or intermittent traffic and you want the database to scale capacity automatically (including to near-zero), use Aurora Serverless v2 rather than provisioned Aurora instances.
61. If you need cross-region disaster recovery for Aurora with typical replication lag under one second and read scaling worldwide, use Aurora Global Database (secondary region clusters are read-only until explicitly promoted).
62. If an application needs a fully managed NoSQL key-value/document store with single-digit millisecond latency at virtually any scale, think DynamoDB rather than RDS/Aurora.
63. If DynamoDB traffic is spiky or unpredictable, use On-Demand capacity mode; if traffic is steady and forecastable, use Provisioned capacity with Application Auto Scaling for lower cost.
64. If an application needs microsecond read latency on top of DynamoDB, add DAX as an in-memory cache in front of it (DAX write-through still persists writes to DynamoDB, so it does not reduce write latency).
65. If DynamoDB data needs active-active replication across regions for global low-latency access and resilience, use DynamoDB Global Tables (replication is asynchronous/eventually consistent between regions).
66. If an application must react to item-level inserts/updates/deletes in DynamoDB (e.g., trigger a Lambda), enable DynamoDB Streams.
67. If you need a simple, high-throughput cache with no persistence or replication requirements, use ElastiCache for Memcached; if you need persistence, complex data structures, pub/sub, or replication with automatic failover, use ElastiCache for Redis/Valkey.
68. If a cache tier must survive node failure without manual intervention, deploy ElastiCache for Redis/Valkey with Multi-AZ automatic failover enabled (cluster mode is optional and used for sharding/scaling, not a requirement for HA; Memcached has no built-in replication, so a node failure loses that node's cached data).
69. If you need a petabyte-scale data warehouse for OLAP-style analytics across billions of rows, think Redshift rather than RDS/Aurora/DynamoDB (those are optimized for OLTP, not large-scale aggregation).
70. If you need to query data that lives in S3 without first loading it into a Redshift cluster, use Redshift Spectrum.
71. If Redshift compute demand is unpredictable or workloads are intermittent, use Redshift Serverless instead of sizing and managing a provisioned cluster.
72. If a workload is short-term, unpredictable, or cannot tolerate interruption, use On-Demand EC2 instances (you pay a premium for that flexibility, no commitment).
73. If a workload runs steady-state for 1–3 years, use Reserved Instances or Compute Savings Plans for the discount (Savings Plans are more flexible across instance family/region/OS; RIs can be resold on the RI Marketplace but are otherwise rigid).
74. If a workload is fault-tolerant, stateless, and can be interrupted (batch, CI/CD, big data, rendering), use Spot Instances for up to ~90% savings (AWS reclaims capacity with only a 2-minute interruption notice).
75. If compliance requires visibility/control of the physical server (per-socket/core BYOL licensing), use EC2 Dedicated Hosts; if you only need hardware isolation without that visibility, use cheaper Dedicated Instances instead.
76. If compute is short-lived (≤15 minutes), event-driven, and bursty, use Lambda so you never manage servers or idle capacity.
77. If a job needs to run longer than 15 minutes, needs a custom kernel/OS, or needs persistent local state, use ECS/EKS/Fargate or EC2 instead of Lambda.
78. If containers must run without managing or patching the underlying EC2 fleet, use Fargate (you trade some cost/control for zero infrastructure management).
79. When choosing a container orchestrator, use ECS for simpler AWS-native operations and use EKS when Kubernetes-standard APIs, existing K8s tooling, or multi-cloud portability are required.
80. If scaling should react to a single target metric (CPU, ALB request count), use Auto Scaling target-tracking policies for the simplest self-correcting behavior.
81. If demand follows a known recurring pattern (daily/seasonal spikes), add Auto Scaling scheduled or predictive scaling so capacity is ready ahead of the spike (reactive scaling alone lags behind sudden demand).
82. If routing needs to be layer-7 aware (host/path-based rules, WebSockets, HTTP/2, container-based target routing), use an Application Load Balancer.
83. If you need ultra-low latency, a static IP per AZ, or must handle extreme volumes of raw TCP/UDP traffic, use a Network Load Balancer instead of an ALB.
84. If third-party virtual appliances (firewalls, IDS/IPS, deep packet inspection) must sit transparently inline with traffic, use a Gateway Load Balancer.
85. If DNS should send users to the lowest-latency healthy region, use Route 53 latency-based routing (this optimizes for network latency, not physical distance — that's geoproximity/geolocation).
86. If you need automatic DNS-level failover to a secondary site during an outage, use Route 53 failover routing with health checks (failover is not instant — client-side DNS TTL caching adds delay).
87. If you need to canary or A/B test by sending a percentage of traffic to a new version, use Route 53 weighted routing.
88. If content must be restricted or localized based on the requester's country for legal/compliance reasons, use Route 53 geolocation routing (not the same as latency-based routing).
89. If static or dynamic web content needs to be cached close to users worldwide to cut latency and origin load, put CloudFront in front of S3/ALB/custom origins.
90. If you need to accelerate non-HTTP TCP/UDP traffic, or want static anycast IPs with fast regional failover for TCP/UDP apps, use Global Accelerator (CloudFront is optimized for cacheable HTTP/S content; Global Accelerator improves routing over the AWS global network instead).
91. If instances in a private subnet need outbound-only internet access, use a managed NAT Gateway rather than a self-managed NAT instance (NAT Gateway scales automatically but is AZ-scoped — deploy one per AZ for HA).
92. If two VPCs need direct private connectivity and traffic won't need to transit a third network, use VPC Peering (peering is non-transitive — it does not chain automatically across peered VPCs).
93. If many VPCs and on-premises networks need transitive routing through one hub, use Transit Gateway instead of building a full mesh of VPC peering connections.
94. If you need a consistent, dedicated, high-bandwidth, low-latency link to on-premises, use Direct Connect (the connection is private but not encrypted by default — layer a VPN over DX if encryption in transit is required).
95. If you need an encrypted connection to on-premises that can be provisioned quickly without dedicated hardware, use Site-to-Site VPN (often deployed as a backup path for Direct Connect since it traverses the public internet with variable throughput).
96. If consumers can tolerate at-least-once delivery and occasional out-of-order messages in exchange for nearly unlimited throughput, use SQS Standard queues.
97. If strict message order and exactly-once processing are required, use SQS FIFO queues (throughput is capped per message group unless high-throughput FIFO mode is enabled).
98. If one message must reach many independent subscriber types (email, SMS, Lambda, HTTP, SQS), use SNS pub/sub as the fan-out mechanism.
99. If events must be routed from many AWS services and third-party SaaS sources using content-based filtering and a schema registry, use EventBridge rather than SNS.
100. If you must ingest and process massive real-time data streams with custom consumer logic, ordering per shard, and replay capability, use Kinesis Data Streams (you manage shard capacity and consumer checkpointing yourself).
101. If streaming data just needs reliable near-real-time delivery into S3, Redshift, or OpenSearch without writing consumer code, use Kinesis Data Firehose instead of Data Streams.
102. If a process involves multiple steps with branching, retries, and error handling across Lambda/ECS/other services, orchestrate it with Step Functions instead of chaining functions manually.
103. When selecting a DR strategy, match cost to RTO/RPO along the spectrum: Backup & Restore (cheapest, hours-long RTO) → Pilot Light (core services always on, minutes-to-hours RTO) → Warm Standby (scaled-down full stack running, low-minutes RTO) → Multi-Site Active/Active (near-zero RTO/RPO, highest cost).
104. If idle or oversized compute is driving cost, use AWS Compute Optimizer or Cost Explorer rightsizing recommendations before purchasing additional Reserved Instances or Savings Plans commitments.