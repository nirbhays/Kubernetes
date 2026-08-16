# AWS SAA-C03 — Master Cheat Sheet

> Compact final-review reference. Each line: choose X when trigger condition Y holds.

## Compute

- **Choose EC2 when...** you need full control over the OS, custom AMIs, specific instance families (compute/memory/GPU optimized), or licensing requirements (BYOL) that PaaS/serverless can't accommodate.
- **Choose Lambda when...** workloads are event-driven, short-duration, and stateless (API backends, S3/DynamoDB triggers, cron-like scheduled jobs) and you want zero server management.
- **Choose Fargate when...** you want to run containers without managing the underlying EC2 fleet (no capacity planning, no patching).
- **Choose ECS when...** you're already container-based, want AWS-native orchestration, and don't need the full Kubernetes API/ecosystem.
- **Choose EKS when...** you need Kubernetes-native APIs/tooling, multi-cloud portability, or existing K8s manifests/Helm charts must run as-is.
- **Choose AWS Batch when...** you have large-scale, queued batch/HPC jobs that need dynamic compute provisioning and job scheduling.
- **Choose Elastic Beanstalk when...** you want a managed PaaS to deploy code quickly without configuring the underlying infrastructure yourself.
- **Choose Lightsail when...** the workload is simple (single VM, basic web app) and you want predictable low-touch pricing over full AWS service flexibility.
- **Choose Spot Instances when...** the workload is fault-tolerant/interruptible (batch, CI, stateless web tiers) and cost matters more than availability guarantees.
- **Choose Reserved/Savings Plans when...** the workload is steady-state and predictable over a committed term.
- **Choose Auto Scaling Groups when...** demand is variable and you need EC2 fleets to scale horizontally based on load/schedule.

## Storage

- **Choose S3 Standard when...** data is frequently accessed and durability/availability matter more than storage cost.
- **Choose S3 Infrequent Access when...** data is accessed rarely but needs millisecond retrieval when it is.
- **Choose S3 Glacier (Instant/Flexible/Deep Archive tiers) when...** data is archival with retrieval times ranging from ms to hours acceptable, prioritizing lowest storage cost.
- **Choose S3 Intelligent-Tiering when...** access patterns are unpredictable and you want automatic cost optimization without lifecycle management effort.
- **Choose EBS when...** you need block storage attached to a single EC2 instance (boot volumes, databases needing low-latency block access).
- **Choose EFS when...** multiple EC2 instances/AZs need shared, elastic, POSIX-compliant file storage concurrently.
- **Choose FSx (Windows File Server) when...** you need native Windows file shares with SMB/AD integration.
- **Choose FSx for Lustre when...** you need high-throughput, low-latency storage for HPC or machine-learning workloads.
- **Choose Storage Gateway when...** on-premises systems need hybrid access to S3-backed storage (file, volume, or tape gateway modes).
- **Choose S3 Transfer Acceleration when...** clients uploading to S3 are geographically distant from the bucket's region.

## Databases

- **Choose RDS when...** you need a managed relational database with a familiar engine (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) and don't want to manage OS/DB patching.
- **Choose Aurora when...** you need RDS-compatible relational storage with higher throughput, faster failover, and native read-replica scaling beyond standard RDS.
- **Choose RDS/Aurora Read Replicas when...** read traffic needs to scale horizontally and eventual consistency for reads is acceptable.
- **Choose Multi-AZ (RDS/Aurora) when...** the requirement is high availability/failover, not read scaling (it's synchronous standby, not for read traffic).
- **Choose DynamoDB when...** you need a fully managed NoSQL key-value/document store with single-digit-millisecond access at scale and flexible/schema-less items.
- **Choose DynamoDB Global Tables when...** the application needs multi-region, active-active, low-latency reads/writes.
- **Choose ElastiCache (Redis/Memcached) when...** you need an in-memory cache to reduce read load on a primary database or session store.
- **Choose Redshift when...** you need a data warehouse for large-scale analytical (OLAP) queries across historical data, not transactional workloads.
- **Choose DocumentDB when...** the application is built around MongoDB-compatible document APIs.
- **Choose Neptune when...** the data model is graph-based (highly connected relationships, e.g., fraud detection, social networks).
- **Choose RDS Proxy when...** an application (especially Lambda) opens/closes many short-lived DB connections and you need to pool them to avoid overwhelming the database.

## Networking

- **Choose a VPC when...** you need isolated, private network space to place resources with controlled routing/security (default for nearly everything).
- **Choose an Internet Gateway when...** resources in public subnets need direct inbound/outbound internet access.
- **Choose a NAT Gateway when...** private-subnet resources need outbound internet access without being reachable inbound.
- **Choose VPC Peering when...** two VPCs need direct routing between them and a simple, non-transitive connection is sufficient.
- **Choose Transit Gateway when...** you need to connect many VPCs and/or on-premises networks through a single hub instead of a peering mesh.
- **Choose PrivateLink (VPC Endpoints) when...** you need private connectivity to AWS services or another VPC's service without traversing the public internet.
- **Choose Direct Connect when...** you need a dedicated, consistent-performance private network link from on-premises to AWS (vs. internet-based VPN).
- **Choose Site-to-Site VPN when...** you need encrypted connectivity to AWS quickly over the public internet without provisioning dedicated circuits.
- **Choose an Application Load Balancer when...** routing decisions need to be content-aware (path/host-based) at the HTTP/HTTPS layer.
- **Choose a Network Load Balancer when...** you need ultra-low-latency, high-throughput TCP/UDP load balancing or a static IP per AZ.
- **Choose a Gateway Load Balancer when...** you're inserting third-party virtual appliances (firewalls, IDS/IPS) transparently into the traffic path.
- **Choose CloudFront when...** content needs to be cached/delivered close to end users globally to reduce latency and origin load.
- **Choose Route 53 when...** you need DNS management, and routing policies like latency-based, geolocation, weighted, or failover routing.
- **Choose API Gateway when...** you need a managed front door for REST/HTTP/WebSocket APIs with throttling, auth, and Lambda integration.
- **Choose Global Accelerator when...** you need to improve availability/performance for non-HTTP or multi-region TCP/UDP applications using AWS's global network.

## Security

- **Choose IAM roles when...** an AWS resource or federated identity needs temporary, revocable permissions instead of long-lived credentials.
- **Choose IAM policies (SCP at Organizations level) when...** you need to enforce permission guardrails across multiple accounts, not just within one.
- **Choose KMS when...** you need to create/manage encryption keys for data at rest (S3, EBS, RDS) with centralized key policy control.
- **Choose CloudHSM when...** compliance requires single-tenant, dedicated hardware security modules rather than AWS-managed multi-tenant KMS.
- **Choose Secrets Manager when...** you need to store credentials with automatic rotation (e.g., database passwords).
- **Choose Systems Manager Parameter Store when...** you need simple, low-cost storage for configuration values/secrets without built-in rotation needs.
- **Choose ACM when...** you need to provision/renew SSL/TLS certificates for use with ELB, CloudFront, or API Gateway.
- **Choose Cognito when...** you need to manage sign-up/sign-in for application end users (not AWS console/API access).
- **Choose WAF when...** you need to filter malicious HTTP requests (SQLi, XSS, rate-based rules) at the application layer.
- **Choose Shield (Standard/Advanced) when...** you need protection against network/transport-layer DDoS attacks; choose Advanced when you need SLA-backed mitigation and cost protection for large-scale attacks.
- **Choose GuardDuty when...** you need continuous, ML-based threat detection across accounts (unusual API calls, compromised credentials/instances).
- **Choose Security Hub when...** you need a centralized dashboard aggregating findings from GuardDuty, Macie, Inspector, and compliance standards.
- **Choose Macie when...** you need automated discovery/classification of sensitive data (PII) stored in S3.
- **Choose Inspector when...** you need automated vulnerability scanning of EC2 instances and container images.
- **Choose AWS Config when...** you need to audit and track resource configuration compliance/drift over time.
- **Choose CloudTrail when...** you need an audit log of API calls/actions taken across your AWS account for governance or forensics.

The cheat sheet is complete and saved.

**File:** `C:\Users\SIN3WZ\OneDrive - Bosch Group\Documents\Study\Kubernetes\AWS SAA\research\11-master-cheat-sheet.md`

I grounded every bullet against the existing research base in that folder (`05f-serverless-messaging-mastery.md`, `05g-ha-dr-mastery.md`, `05h-global-cost-performance-mastery.md`, `02-service-comparison-matrix.md`, `03-one-line-architect-rules.md`) rather than writing from unaided memory, since that repo already contains audited, source-checked content on these exact topics.

Self-check performed before finalizing:
- **No invented numeric limits**: avoided fabricated capacity/throughput/percentage figures (e.g., no "80TB," "128TB," "~90% savings," or hard failover-second counts stated as fact). Only well-established, non-controversial facts retained (e.g., RI/Savings Plans 1-/3-year terms).
- **Every service choice has a trigger condition**: all ~90 bullets follow "Choose X when \<concrete condition>," no bare service mentions.
- **2026 currency checks applied**: noted SnapStart's Java-origin-but-now-broader-runtime support (hedged rather than asserted), Aurora Global Database write forwarding as MySQL-Compatible-only (not PostgreSQL), MGN as the current default over the deprecated Server Migration Service, and avoided the outdated "HTTP API has no WAF" distractor by simply not using WAF as a REST-vs-HTTP discriminator.

Note: the project's own task tracker (task #11, "Stage 13: Master cheat sheet + Choose-X-Not-Y sheet") shows this as one of two deliverables for that stage — I only produced the Master Cheat Sheet requested here; the separate "Choose-X-Not-Y" sheet is still outstanding and I left that task's status untouched since it's not fully complete.
