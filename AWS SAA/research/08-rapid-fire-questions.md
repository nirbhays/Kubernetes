# AWS SAA-C03 — 100 Rapid-Fire Questions

These test instant service recognition (10-30 second answer time), organized by topic area.

## Security & IAM

1. Rotate a database password automatically every 30 days with built-in Lambda rotation support?
   Answer: Secrets Manager — native automatic rotation with Lambda rotation functions; Parameter Store lacks this built-in capability.

2. Store a simple non-sensitive application config value for free, no rotation needed?
   Answer: SSM Parameter Store (Standard tier) — free, hierarchical key-value storage ideal for plain config, no need for Secrets Manager's cost/rotation features.

3. Grant a Lambda function in Account A permission to write to an S3 bucket in Account B?
   Answer: S3 bucket policy on Account B's bucket granting `s3:PutObject` to the Lambda execution role's ARN (Account A), combined with an identity-based policy on that role allowing the same action — the resource-based bucket policy is what bridges the account boundary. No new "cross-account role" needs to be created or assumed for this pattern; that mechanism (assumed roles) is for the External ID / assume-role scenario in Q13, not a straightforward cross-account S3 write.

4. Encrypt EBS volumes with a key you fully control, including manual rotation and disabling?
   Answer: KMS Customer Managed Key (CMK) — gives full control over key policy, rotation schedule, and ability to disable/revoke, unlike AWS-managed keys.

5. Let mobile app users sign in with Google or Facebook and get temporary AWS credentials?
   Answer: Cognito Identity Pools (Federated Identities) — federates external IdPs and vends temporary IAM credentials via STS.

6. Add user sign-up, sign-in, and MFA to a web app without building your own auth backend?
   Answer: Cognito User Pools — fully managed user directory with built-in sign-up/sign-in, MFA, and token issuance.

7. Protect a public web application from SQL injection and XSS at the edge?
   Answer: AWS WAF — layer 7 web ACL with managed rule groups filters malicious HTTP requests before they reach the app.

8. Defend against a large-scale volumetric DDoS attack on an internet-facing ELB?
   Answer: AWS Shield Advanced — provides enhanced DDoS protection, near real-time visibility, and cost protection for Shield Advanced-covered resources.

9. Continuously detect compromised EC2 instances or suspicious API calls across an account?
   Answer: GuardDuty — managed threat detection analyzing VPC Flow Logs, DNS logs, and CloudTrail for anomalous/malicious activity.

10. Discover and classify PII like credit card numbers sitting in S3 buckets?
    Answer: Macie — ML-powered service that scans S3 for sensitive data and reports findings.

11. Allow an on-premises application to assume an AWS role without long-lived access keys?
    Answer: IAM Role with SAML 2.0 / IAM Identity Provider federation — enables temporary STS credentials instead of storing static keys.

12. Need envelope encryption with an audit trail of every key usage for compliance?
    Answer: KMS — every Encrypt/Decrypt/GenerateDataKey call is logged to CloudTrail, satisfying audit requirements.

13. Give a third-party SaaS vendor temporary, limited access to specific resources in your account?
    Answer: Cross-account IAM role with an External ID — trust policy plus External ID condition prevents the confused deputy problem.

14. Restrict which IAM principals can use a specific KMS key, separate from IAM policy?
    Answer: KMS Key Policy — the resource-based policy attached to the key is the primary access control gate for KMS.

15. Store and retrieve database credentials that need automatic rotation for RDS?
    Answer: Secrets Manager — has native RDS integration for automated credential rotation.

16. Enforce that all S3 uploads must be encrypted with a specific customer-managed key?
    Answer: S3 Bucket Policy with a condition on `s3:x-amz-server-side-encryption-aws-kms-key-id` — denies PutObject requests that don't specify the required CMK.

17. Give temporary read-only access to a contractor for 8 hours without creating a permanent user?
    Answer: IAM Role assumed via STS with a session duration limit — temporary credentials expire automatically, no standing access.

18. Need FIPS 140-2 validated hardware key storage with single-tenant control of the HSM?
    Answer: CloudHSM — dedicated, single-tenant hardware security module for the strictest key custody/compliance needs, unlike shared KMS.

19. Block requests from a list of known malicious IP addresses at the CDN layer?
    Answer: AWS WAF IP set rule on CloudFront — an IP-based block rule in a web ACL filters traffic before it hits the origin.

20. Enable an application to call AWS APIs from an on-prem server using your corporate Active Directory identity?
    Answer: SAML 2.0 federation (AD FS trusting AWS) with an IAM role — the application calls `sts:AssumeRoleWithSAML` using AD-issued SAML assertions to obtain temporary credentials. IAM Identity Center (AWS SSO) with AD Connector is built for human interactive sign-in to the AWS access portal/console, not for a server application making programmatic API calls, so it isn't the right fit here.

## Networking

21. Private subnet EC2 instances need outbound internet access to download OS patches, but must not be reachable from the internet?
    Answer: NAT Gateway — provides outbound-only internet access for private subnets while blocking unsolicited inbound connections.

22. VPC needs a resource that allows direct, two-way internet connectivity for public subnet instances?
    Answer: Internet Gateway — horizontally scaled, redundant VPC component enabling bidirectional internet traffic for public subnets.

23. Need stateful, instance-level traffic filtering that automatically allows return traffic?
    Answer: Security Group — stateful firewall attached to ENIs; return traffic is automatically allowed regardless of outbound/inbound rules.

24. Need to explicitly deny traffic from a specific IP range at the subnet level?
    Answer: Network ACL — stateless, subnet-level firewall that supports both allow and deny rules, unlike Security Groups.

25. Rule evaluation order matters and rules are processed by numbered priority until a match is found?
    Answer: Network ACL — rules are evaluated in ascending rule-number order, stopping at the first match.

26. Access S3 from a private subnet without traversing the internet or using a NAT Gateway?
    Answer: Gateway VPC Endpoint — provides private, no-cost route-table-based connectivity to S3 and DynamoDB only.

27. Private, non-internet connectivity to KMS, Secrets Manager, or other supported AWS APIs from within a VPC?
    Answer: Interface VPC Endpoint (AWS PrivateLink) — ENI-based endpoint with private IPs for most AWS service APIs.

28. Connect thousands of VPCs and on-prem networks through a single scalable hub without managing a full mesh?
    Answer: Transit Gateway — regional hub-and-spoke router simplifying connectivity between many VPCs and on-prem sites.

29. Connect exactly two VPCs directly with non-overlapping CIDRs, no transitive routing needed?
    Answer: VPC Peering — one-to-one private connection between two VPCs; does not support transitive routing.

30. Need consistent, dedicated, low-latency private connectivity from on-prem data center to AWS, bypassing the public internet entirely?
    Answer: Direct Connect — dedicated physical network connection offering predictable bandwidth and lower latency than internet-based VPN.

31. Need encrypted connectivity to AWS set up in minutes over the public internet as a stopgap or backup link?
    Answer: Site-to-Site VPN — IPsec-encrypted tunnel over the internet, quick to provision, often used as DX backup.

32. Route users to the closest healthy regional endpoint based on latency?
    Answer: Route 53 Latency-based Routing — routes queries to the region with the lowest measured latency for the user.

33. Automatically fail over DNS to a backup site when health checks detect the primary is down?
    Answer: Route 53 Failover Routing — active-passive DNS failover driven by Route 53 health checks.

34. Cache and serve static/dynamic content from edge locations close to global end users?
    Answer: CloudFront — CDN that caches content at edge locations to reduce latency and origin load.

35. Improve performance and availability of a non-HTTP TCP/UDP application (e.g., gaming, VoIP) for global users using static anycast IPs?
    Answer: Global Accelerator — routes traffic over the AWS global network using static anycast IPs, ideal for non-HTTP protocols.

36. Distribute HTTP/HTTPS traffic across targets with content-based routing (path/host-based rules)?
    Answer: Application Load Balancer — Layer 7 load balancer supporting path- and host-based routing rules.

37. Handle millions of requests per second with ultra-low latency, preserving client source IP for TCP/UDP traffic?
    Answer: Network Load Balancer — Layer 4 load balancer for extreme performance and static IP support per AZ.

38. Deploy and scale third-party virtual appliances (firewalls, IDS/IPS) transparently in line with traffic?
    Answer: Gateway Load Balancer — combines a transparent network gateway with load balancing to distribute traffic to virtual appliances using GENEVE encapsulation.

39. Need weighted DNS routing to gradually shift traffic percentage during a canary deployment?
    Answer: Route 53 Weighted Routing — distributes DNS responses across resources based on assigned weight proportions.

40. VPC design requires isolating public-facing resources from private backend resources while still allowing controlled outbound access?
    Answer: Public/Private Subnet Architecture with IGW + NAT Gateway — public subnet routes via IGW, private subnet routes outbound via NAT.

## Storage & Database

41. Frequently accessed data with unpredictable, sudden request spikes where retrieval fees would erode any potential storage savings, still needing millisecond retrieval?
    Answer: S3 Standard — designed for frequently accessed data with high durability, availability, and performance at no retrieval fee. (Note: Standard does NOT have the lowest per-GB storage price — IA/Glacier tiers are cheaper to store in — but for genuinely frequent access it wins on total cost because it has zero retrieval fees.)

42. Data accessed once a month, needs millisecond retrieval, cost matters more than S3 Standard?
    Answer: S3 Standard-IA — millisecond access like Standard but cheaper storage with a per-GB retrieval fee, ideal for infrequent access.

43. Same as above but data can tolerate loss of an entire AZ (non-critical, reproducible data)?
    Answer: S3 One Zone-IA — stores data in a single AZ at lower cost, suitable for infrequently accessed, recreatable data.

44. Access pattern is unknown or changing, want automatic cost optimization without performance impact?
    Answer: S3 Intelligent-Tiering — automatically moves objects between access tiers based on usage patterns, no retrieval fees.

45. Archive data accessed once or twice a year, retrieval within minutes to hours acceptable?
    Answer: S3 Glacier Flexible Retrieval — low-cost archival storage with retrieval times from minutes (expedited) to hours (standard/bulk).

46. Archive data needing the same performance as S3 Standard (millisecond retrieval) for rarely accessed data, e.g. once a quarter?
    Answer: S3 Glacier Instant Retrieval — archive-tier pricing with millisecond retrieval for rarely accessed data. (Note: the "replaces on-premises tape libraries" tagline belongs to S3 Glacier Deep Archive, not Instant Retrieval — Deep Archive's 12+ hour retrieval is what makes it comparable to tape.)

47. Long-term archive (7-10+ years), compliance data, retrieval time of 12+ hours is fine, absolute lowest cost?
    Answer: S3 Glacier Deep Archive — cheapest S3 storage class, designed for long-term retention rarely if ever accessed; positioned by AWS as a tape-library replacement.

48. Need a block storage volume attached to a single EC2 instance for a database's low-latency disk?
    Answer: EBS — network-attached block storage tied to one AZ, typically attached to one instance at a time, ideal for low-latency transactional workloads.

49. Need a shared file system mounted concurrently by hundreds of Linux EC2 instances across multiple AZs?
    Answer: EFS — fully managed, elastic NFS file system natively supporting concurrent multi-AZ access.

50. Need durable object storage accessible via HTTP(S) API from anywhere, not mounted as a filesystem?
    Answer: S3 — object storage accessed via REST API/SDK, decoupled from compute, virtually unlimited scale.

51. Need high-performance Windows shared file storage with SMB support?
    Answer: FSx for Windows File Server — managed native Windows file system with SMB protocol and AD integration.

52. Production database needs automatic failover to a standby in another AZ during an outage, no read scaling required?
    Answer: RDS Multi-AZ — synchronous replication to a standby in another AZ with automatic failover for high availability.

53. Read-heavy reporting workload overwhelming the primary RDS instance, need to offload read traffic?
    Answer: RDS Read Replica — asynchronous replica(s) that serve read traffic, scaling reads horizontally (cross-region supported for MySQL, MariaDB, and PostgreSQL).

54. Need both high availability AND read scaling for a MySQL-compatible relational database at cloud scale?
    Answer: Aurora — MySQL/PostgreSQL-compatible engine with 6-way replicated storage across 3 AZs plus up to 15 low-latency read replicas.

55. Relational workload with unpredictable, spiky traffic where you don't want to manage capacity/instances at all?
    Answer: Aurora Serverless — on-demand, auto-scaling Aurora configuration that scales capacity based on load.

56. Need microsecond read latency caching layer in front of DynamoDB specifically?
    Answer: DAX — in-memory cache purpose-built for DynamoDB, reducing read latency from milliseconds to microseconds.

57. Need a general-purpose in-memory cache/session store for a web app, compatible with Redis or Memcached APIs?
    Answer: ElastiCache — managed in-memory data store for caching, session management, and low-latency lookups.

58. Need sub-10ms key-value lookups at massive scale with flexible schema, serverless NoSQL?
    Answer: DynamoDB — fully managed, serverless NoSQL database with single-digit-ms performance at any scale.

59. Need to run complex analytical SQL queries across petabytes of structured data from many sources for BI dashboards?
    Answer: Redshift — petabyte-scale columnar data warehouse optimized for complex OLAP analytical queries.

60. Need automatic in-memory caching layer for a leaderboard requiring sub-millisecond latency and sorted sets?
    Answer: ElastiCache for Redis — supports rich data structures like sorted sets, ideal for real-time leaderboards at sub-ms latency.

## Compute & Serverless

61. Steady-state, predictable 24/7 workload for 1-3 years, want max discount?
    Answer: Reserved Instances (Standard) — a long-term, all-upfront commitment trades flexibility for the deepest EC2 discounts (up to ~72% off On-Demand); Convertible RIs give up some of that discount in exchange for the ability to change instance families, so Standard is the one that maximizes discount.

62. Interruptible batch job, fault-tolerant, willing to lose the instance with 2-min warning for up to 90% off?
    Answer: Spot Instances — bid on spare EC2 capacity at steep discount, accepting reclaim risk.

63. Unpredictable short-term workload, no upfront commitment, pay standard rate only when running?
    Answer: On-Demand Instances — no commitment, billed per second with no long-term contract.

64. Need guaranteed capacity reservation in a specific AZ without committing to a specific instance purchase model?
    Answer: On-Demand Capacity Reservations — reserves capacity in an AZ, decoupled from billing discounts.

65. Regulatory requirement to run on physically dedicated hardware for compliance/licensing (BYOL)?
    Answer: Dedicated Hosts — physical server dedicated to you, visibility into sockets/cores for per-socket licensing.

66. Want instance isolation from other tenants but don't care about physical server visibility?
    Answer: Dedicated Instances — runs on hardware dedicated to a single customer, billed hourly.

67. Containerized app, team wants zero server/cluster management, just run containers?
    Answer: Fargate — serverless compute engine for containers, no EC2 instances to provision or patch.

68. Team already has deep Kubernetes expertise and wants a managed control plane with full K8s API compatibility?
    Answer: EKS — managed Kubernetes control plane, portable across on-prem/other clouds via standard K8s API.

69. Simple containerized microservices, team wants AWS-native orchestration without learning Kubernetes?
    Answer: ECS — AWS's own container orchestrator, simpler learning curve, tight AWS integration.

70. Need fine-grained control over underlying EC2 instances (custom AMI, GPU, placement groups) for containers?
    Answer: ECS/EKS on EC2 launch type — self-managed worker nodes give full control over instance configuration.

71. Code runs only in response to events (file upload, API call), sub-15-min duration, want zero idle cost?
    Answer: Lambda — event-driven, pay-per-invocation serverless compute with no charge when idle.

72. Long-running (hours), stateful, or requires custom OS-level dependencies not fitting a function's runtime/time limits?
    Answer: EC2 (or ECS/EKS) — Lambda's 15-min max duration and stateless model rule it out for long/stateful workloads.

73. Scale EC2 fleet based on CPU utilization or custom CloudWatch metric automatically?
    Answer: EC2 Auto Scaling with target tracking policy — adds/removes instances to hold a metric at target value.

74. Need to scale ahead of a known traffic spike (e.g., Black Friday) before demand actually hits?
    Answer: Scheduled Scaling (Auto Scaling) — pre-provisions capacity at a specified time based on predictable patterns.

75. Want to scale multiple services (ECS, DynamoDB, Aurora, etc.) together based on the same demand signal?
    Answer: Application Auto Scaling — unified scaling API across many AWS services (ECS, DynamoDB, Aurora, EMR, SageMaker, EC2 Spot Fleet, etc.); note it does not manage standard EC2 Auto Scaling Groups, which are handled by the separate EC2 Auto Scaling service.

76. Need a fully managed RESTful/HTTP front door for Lambda functions with throttling, auth, and versioning?
    Answer: API Gateway — managed API layer handling routing, throttling, auth, and stage-based deployment for backend integrations.

77. Need to expose a WebSocket API for real-time bidirectional client-server communication?
    Answer: API Gateway (WebSocket API) — manages persistent connections and routes messages to backend integrations like Lambda.

78. Orchestrate a multi-step workflow with retries, error handling, and parallel branches across several Lambda functions?
    Answer: Step Functions — visual state machine coordinates distributed tasks with built-in retry/catch logic.

79. Need to coordinate a long-running human approval step in the middle of an automated workflow?
    Answer: Step Functions (with callback pattern / Task Token) — pauses execution until an external signal resumes it.

80. Throttle and cache API responses per client, and require API key-based usage plans/quotas?
    Answer: API Gateway — built-in usage plans, API keys, throttling, and response caching per stage.

## Messaging, Migration & Cost

81. Millions of messages need buffering between a producer and a slow consumer, order doesn't matter?
    Answer: SQS Standard — fully managed queue decouples producer/consumer and scales throughput with at-least-once delivery.

82. One event must trigger multiple independent subscriber systems simultaneously (email, Lambda, SQS)?
    Answer: SNS — pub/sub fan-out pushes a single message to many subscribers in parallel.

83. Need to route events from 100+ SaaS/third-party sources and AWS services based on content-based rules?
    Answer: EventBridge — schema-aware event bus with rule-based routing across AWS and SaaS integrations.

84. Real-time clickstream data from millions of devices must be ingested and processed by multiple analytics consumers with replay capability?
    Answer: Kinesis Data Streams — durable, ordered, replayable stream supporting multiple concurrent consumer applications.

85. Strict message ordering and exactly-once processing required for financial transactions in a queue?
    Answer: SQS FIFO — guarantees ordering within a message group, and exactly-once processing (no duplicates) via deduplication across the queue.

86. Need to transform and load streaming data into S3/Redshift without managing servers?
    Answer: Kinesis Data Firehose — fully managed delivery stream that batches, transforms, and loads data to destinations automatically.

87. Application needs a lightweight, serverless way to react to AWS resource state changes (e.g., EC2 state change)?
    Answer: EventBridge — natively consumes AWS service events without polling infrastructure.

88. One-time migration of 500TB from an on-prem data center with limited network bandwidth?
    Answer: Snowball Edge — physical device ships petabyte-scale data offline, avoiding slow network transfer.

89. Need continuous, incremental sync of on-prem NFS/SMB file data to S3 over the network?
    Answer: DataSync — automates and accelerates online transfer with built-in scheduling and validation.

90. On-prem application needs low-latency local access to files while data is also durably stored in S3?
    Answer: Storage Gateway (File Gateway) — caches frequently used data locally while backing it with S3.

91. Migrating a 10PB on-prem data lake with no viable network option, even with Snowball?
    Answer: Snowmobile — shipping-container-scale exabyte data transfer for the largest migrations.

92. Need to migrate a production Oracle database to Aurora with minimal downtime and ongoing replication during cutover?
    Answer: AWS DMS — continuous data replication enables near-zero-downtime database migration.

93. Database migration also requires converting schema/code from one engine (Oracle) to a different engine (PostgreSQL)?
    Answer: AWS SCT (Schema Conversion Tool) — converts schema and application code for heterogeneous migrations, paired with DMS for data.

94. On-prem backup process still uses tape drives and needs a cloud-native replacement?
    Answer: Storage Gateway (Tape Gateway/VTL) — presents a virtual tape library backed by S3/Glacier.

95. Workload is fault-tolerant, flexible on timing, and can be interrupted — how to cut compute cost up to 90%?
    Answer: Spot Instances — bid on spare EC2 capacity at steep discounts for interruptible workloads.

96. Steady-state, predictable 24/7 compute usage for 1-3 years — cheapest pricing model?
    Answer: Reserved Instances / Savings Plans — commit to usage in exchange for significant discounts over On-Demand.

97. S3 objects have unpredictable or changing access patterns and you want automatic cost savings without lifecycle rules?
    Answer: S3 Intelligent-Tiering — automatically moves objects between access tiers based on usage patterns.

98. Compliance archive data accessed maybe once a year, cost is the only priority, retrieval time irrelevant?
    Answer: S3 Glacier Deep Archive — lowest-cost storage class for rarely accessed, long-term retention data.

99. Need automated recommendations on right-sizing EC2/EBS/Lambda to eliminate over-provisioning costs?
    Answer: AWS Compute Optimizer — ML-based analysis recommends optimal resource configurations to cut waste.

100. Need to decouple microservices where the same order event must fan out to inventory, billing, and shipping queues independently?
     Answer: SNS + SQS fan-out — SNS topic publishes once, delivering to multiple SQS queues for independent, durable processing per consumer.
</content>
</invoke>
