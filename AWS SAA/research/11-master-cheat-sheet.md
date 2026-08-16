# AWS SAA-C03 — Master Cheat Sheet

*Final-review compression. Each line is a trigger → service mapping, not an explanation. Cross-reference the mastery docs (05a–05h) and one-line rules (03) if a line here doesn't click.*

## Messaging

- **Choose SQS when** you need point-to-point decoupling with competing consumers pulling from a durable queue and no replay requirement.
- **Choose SQS FIFO when** strict ordering and exactly-once processing is required within a message group.
- **Choose SNS when** one event must be pushed to many independent subscribers (simple topic-based fan-out), typically fronting per-subscriber SQS queues for durability.
- **Choose SNS → SQS fan-out when** multiple downstream systems must each durably and independently process the same event without one slow consumer blocking or losing messages for the others.
- **Choose SNS FIFO + SQS FIFO when** you need fan-out *and* strict per-group ordering/deduplication together.
- **Choose EventBridge when** you need content-based routing across many event types/targets, schema discovery, cross-account/cross-service routing, SaaS partner event sources, or scheduled (cron-like) invocation.
- **Choose Kinesis Data Streams when** multiple independent consumers must replay/re-read the same ordered stream at their own pace (clickstream, IoT telemetry, real-time analytics).
- **Choose Kinesis Data Firehose when** you need managed, near-real-time delivery of streaming data into S3/Redshift/OpenSearch without writing consumer code.
- **Choose MSK when** the workload is already built on Kafka APIs/tooling and migrating off Kafka semantics isn't practical.
- **Choose Step Functions over direct Lambda-to-Lambda calls when** a workflow needs branching, retries/backoff, human-approval waits, or an auditable execution history.
- **Choose Step Functions Standard when** the workflow is long-running (up to about a year) and needs exactly-once, auditable execution.
- **Choose Step Functions Express when** you need high-volume, short-duration, at-least-once event processing.

## Serverless

- **Choose Lambda when** compute is short-lived, event-driven, and bursty, and you want zero server/idle-capacity management.
- **Choose a Lambda in a VPC when** it must reach a VPC-only resource (RDS, ElastiCache, private ALB/EC2, on-prem over VPN/DX); otherwise leave it outside the VPC.
- **Choose a Gateway/Interface VPC endpoint over a NAT Gateway when** a VPC-attached Lambda only needs to reach AWS service APIs (S3/DynamoDB via Gateway endpoint; most other services via Interface endpoint).
- **Choose Reserved Concurrency when** you need to cap a function to protect a downstream system, or guarantee it capacity away from other functions in the account pool.
- **Choose Provisioned Concurrency when** a latency-sensitive, synchronous workload (user-facing API) cannot tolerate cold starts.
- **Choose SnapStart when** you want to cut cold-start time without paying for standing provisioned concurrency (originally Java-focused, now also available for other supported runtimes — verify current runtime support if it matters to the question).
- **Choose an async destination (or DLQ) when** a Lambda invoked asynchronously (S3, SNS, EventBridge) needs a durable place to route events after retries are exhausted.
- **Choose `ReportBatchItemFailures` when** an SQS-triggered Lambda partially fails a batch and you don't want to reprocess the messages that already succeeded.
- **Choose API Gateway HTTP API when** the requirement is a cost-optimized simple proxy (Lambda/HTTP backend) needing basic JWT/IAM auth.
- **Choose API Gateway REST API when** you need per-client usage plans/API keys or full request/response VTL mapping templates (these remain REST-only).
- **Choose a Lambda authorizer when** auth logic is custom (non-Cognito OIDC/OAuth provider, legacy identity system, custom token format).
- **Choose Fargate over Lambda when** the workload is long-running, sustained-high-throughput, or needs a container runtime/execution duration Lambda can't accommodate.
- **Choose Aurora Serverless v2 when** a relational workload has intermittent, unpredictable, or highly variable demand and standing provisioned capacity would be wasted.
- **Choose DynamoDB On-Demand when** traffic is spiky/unpredictable or the application is new without traffic history.
- **Choose EventBridge Scheduler/rules over Step Functions when** the requirement is purely a cron-like scheduled invocation.

## Migration

- **Choose AWS DMS when** the source is a live, running database and you need minimal-downtime migration or ongoing replication via Change Data Capture (CDC), including feeding a data lake/analytics target.
- **Choose SCT alongside DMS when** the migration is heterogeneous (different source/target engines, e.g., Oracle → Aurora) and schema/stored-procedure/SQL-dialect conversion is needed.
- **Choose AWS DataSync when** migrating files/objects (NFS/SMB shares, home directories, media) into S3/EFS/FSx, especially for large one-time or scheduled incremental transfers with metadata preservation — not for live database migration.
- **Choose AWS Application Migration Service (MGN) when** you need lift-and-shift rehost of entire physical/virtual/other-cloud servers into EC2 via continuous block-level replication with a test-before-cutover step; this has superseded the deprecated Server Migration Service.
- **Choose Snowcone when** you need a small, ruggedized device for edge locations with limited data volume, optionally running edge compute, with the option to ship back or send data over the network via DataSync.
- **Choose Snowball Edge when** you need mid-scale offline data transfer or on-device edge compute/ML at a site with insufficient network bandwidth for the data volume.
- **Choose Snowmobile only when** the migration is data-center-scale (many petabytes to exabyte-scale) — for anything smaller, prefer multiple Snowball Edge devices.
- **Choose AWS Transfer Family when** you need managed SFTP/FTPS/FTP endpoints backed by S3 or EFS for partner file exchange.
- **Choose Direct Connect for ongoing migration/replication traffic when** the volume is large and sustained over time and a private, consistent-bandwidth link is needed; choose Snow Family instead when on-prem bandwidth or timeline makes network transfer impractical for a one-time bulk move.
- **Choose a follow-up DataSync incremental sync after a Snow Family transfer when** on-prem data changed between sealing the device and completion of the AWS-side import.

## Disaster Recovery

- **Choose Backup and Restore when** budget is the primary constraint and hours of downtime/data loss are acceptable — only backups (S3/EBS/RDS snapshots, AWS Backup) exist in the DR Region, no standing compute.
- **Choose Pilot Light when** only the data/replication tier runs continuously in the DR Region and the application/compute tier is provisioned from templates/AMIs on failover.
- **Choose Warm Standby when** a full but scaled-down stack (including the app tier) already runs in the DR Region and failover just means scaling it up.
- **Choose Multi-Site Active-Active when** near-zero RTO/RPO is required and full-capacity stacks in 2+ Regions are already serving live traffic simultaneously.
- **Choose Aurora Global Database when** a relational workload needs cross-Region DR with low replication lag and fast secondary-Region promotion (secondary Regions are read-only until promoted).
- **Choose DynamoDB Global Tables when** a NoSQL workload needs multi-Region, multi-writer (active-active) replication with eventual, last-writer-wins conflict resolution.
- **Choose Route 53 failover routing + health checks when** you need automatic DNS-level failover to a secondary/DR endpoint.
- **Choose Route 53 Application Recovery Controller when** the requirement emphasizes a regularly tested, audited failover process beyond a basic health-check failover record.
- **Choose cross-Region snapshot/AMI/CRR copy when** the DR strategy is Backup and Restore or Pilot Light and you need the data layer reproducible in the second Region without continuous replication.
- **Choose a lower Route 53 TTL when** clients keep resolving to the failed endpoint for too long after a DNS-based failover.

## High Availability

- **Choose a Multi-AZ Auto Scaling Group behind an ELB when** compute must survive the loss of a single Availability Zone.
- **Choose RDS Multi-AZ (instance deployment) when** you need automatic failover to a synchronous standby without app changes, but don't need the standby to be readable.
- **Choose RDS Multi-AZ DB Cluster deployment when** you need readable standby instances (offload reads via the reader endpoint) plus faster failover than the classic Multi-AZ instance deployment.
- **Choose RDS Read Replicas when** the goal is scaling read throughput, not HA — asynchronous replication means replicas can lag and aren't a substitute for Multi-AZ.
- **Choose Aurora over standard RDS when** the workload needs the fastest in-Region failover and storage-level self-healing replication across AZs for a relational engine.
- **Choose one NAT Gateway per AZ when** private subnets in each AZ must remain independent of a NAT Gateway failure or an AZ outage elsewhere.
- **Choose an ALB when** you need Layer 7 content-based routing (path/host/header) or Lambda targets.
- **Choose an NLB when** you need a static IP per AZ, client source-IP preservation without extra config, or extreme-performance Layer 4 TCP/UDP/TLS handling.
- **Choose a Gateway Load Balancer when** you need to transparently insert and scale third-party virtual security appliances (firewalls, IDS/IPS) in the traffic path.
- **Choose ElastiCache for Redis/Valkey with Multi-AZ automatic failover when** the cache tier must survive node failure without manual intervention (Memcached has no built-in replication).
- **Choose ELB health checks on the ASG (not just default EC2 status checks) when** you need unhealthy-but-still-running application instances replaced automatically.
- **Choose Target Tracking scaling when** you want the default, simplest auto-scaling policy; choose Scheduled Scaling when traffic is predictable by time of day; choose Predictive Scaling when there's a recurring historical demand pattern to scale ahead of.
- **Rely on S3 Standard/Standard-IA and EFS Standard's built-in multi-AZ redundancy when** the question implies "does this need Multi-AZ configuration" — no toggle needed, unlike EBS (single-AZ, needs snapshots to move across AZs) or S3 One Zone-IA (deliberately single-AZ).

## Cost Optimization

- **Choose On-Demand EC2 when** the workload is unpredictable, short-term, or cannot commit to a term.
- **Choose Reserved Instances/Savings Plans when** the workload runs steady-state and you can commit to a 1- or 3-year term; prefer Savings Plans when you need flexibility across instance family/region or coverage of Fargate/Lambda; prefer an AZ-scoped Reserved Instance when you need a guaranteed capacity reservation.
- **Choose Spot Instances when** the workload is fault-tolerant, stateless, and interruptible (batch, CI/CD, rendering) — combine with mixed-instance/Capacity Rebalancing in an ASG to reduce interruption risk.
- **Choose a blended strategy (Savings Plans/RI for baseline + On-Demand for variable delta + Spot for flexible burst) when** a workload has both a steady floor and a bursty ceiling.
- **Choose Dedicated Hosts when** licensing is tied to physical sockets/cores (BYOL) or compliance requires host-level visibility; choose Dedicated Instances when you only need hardware isolation without that visibility.
- **Choose S3 Intelligent-Tiering when** access patterns are unknown/unpredictable and you want cost savings without retrieval-time tradeoffs.
- **Choose S3 Lifecycle rules when** the access-pattern aging curve (hot → warm → cold) is known and predictable — cheaper and simpler than Intelligent-Tiering in that case.
- **Choose S3 Glacier Deep Archive when** data is retained for compliance with almost no expected retrieval and cost must be minimized; choose Glacier Instant Retrieval when archived data still needs millisecond access.
- **Choose a Gateway VPC Endpoint (S3/DynamoDB) or Interface VPC Endpoint (most other services) when** private-subnet traffic to AWS services is unnecessarily traversing (and being billed through) a NAT Gateway.
- **Choose increasing Lambda memory when** it proportionally reduces execution duration enough to lower total invocation cost, despite the higher per-ms rate.
- **Choose DynamoDB Provisioned capacity with Auto Scaling over On-Demand when** traffic is steady/forecastable and consistent high utilization makes provisioned cheaper.
- **Choose right-sizing (via CloudWatch/Compute Optimizer) before purchasing Reserved Instances/Savings Plans when** committing to a term — size first, then commit.
- **Choose Instance Scheduler/scheduled scaling when** non-production environments can be shut down or scaled to a floor outside business hours.
- **Choose AWS Budgets when** the requirement is alerting on spend thresholds; choose Trusted Advisor/Compute Optimizer when the requirement is identifying idle/underutilized/over-provisioned resources.
- **Choose CloudFront with tuned TTLs/cache-control when** the goal is reducing both origin load and data-transfer cost for globally distributed content.

## Performance

- **Choose CloudFront when** the bottleneck is delivering cacheable HTTP(S) content (static assets, video) closer to users.
- **Choose Global Accelerator when** the workload is non-HTTP/non-cacheable (gaming, VoIP, custom TCP/UDP), needs static anycast IPs for firewall allow-listing, or needs fast network-layer regional failover.
- **Choose DAX when** the bottleneck is DynamoDB read latency at microsecond scale — it does not help write latency or fix hot-partition throttling (that's a key-design problem).
- **Choose ElastiCache (Redis/Memcached) as a cache-aside layer when** repeated identical queries are hammering RDS/Aurora.
- **Choose RDS Read Replicas when** the bottleneck is read throughput on a relational database, not writes.
- **Choose RDS Proxy when** connection exhaustion occurs under high concurrency (classic Lambda-to-RDS pattern of many short-lived connections).
- **Choose S3 Transfer Acceleration when** the bottleneck is large file *uploads* to a single bucket from geographically distant clients — this is not a general content-delivery (download) fix.
- **Choose EFS when** multiple Linux instances/containers need shared, concurrent, multi-AZ POSIX file storage; choose FSx for Windows File Server when the same need is Windows/SMB-based; choose FSx for Lustre when the requirement is HPC/ML scratch storage needing very high throughput.
- **Choose a cluster placement group (optionally with Elastic Fabric Adapter) when** tightly-coupled instances need the lowest inter-instance network latency/highest throughput within a single AZ.
- **Choose Provisioned Concurrency when** the performance problem is specifically Lambda cold-start latency on a latency-sensitive path (not a cost-optimization scenario).
- **Choose a larger/compute-optimized instance family when** a workload is compute-bound and cannot be horizontally distributed (statefulness prevents scale-out).
- **Choose API Gateway caching when** the same API responses are being recomputed repeatedly for identical requests.

## Global Architecture

- **Choose Route 53 latency-based routing when** the goal is purely lowest network latency to the nearest healthy Region/endpoint.
- **Choose Route 53 geolocation routing when** traffic must be served from a specific Region for legal/compliance/content-licensing reasons, regardless of latency.
- **Choose Route 53 geoproximity routing when** you need to shift traffic bias between Regions without a hard geographic restriction.
- **Choose Route 53 weighted routing when** the requirement is percentage-based canary/blue-green/A-B traffic shifting.
- **Choose Route 53 failover routing when** the requirement is binary primary/secondary DR routing with health checks.
- **Choose Route 53 multivalue answer routing when** you need simple client-side load balancing with health-checked DNS answers, without a full load balancer.
- **Choose Aurora Global Database when** a relational workload needs low-latency cross-Region reads and fast DR promotion, understanding writes are single-primary-Region (write forwarding, where available, is MySQL-Compatible only, not PostgreSQL).
- **Choose DynamoDB Global Tables when** the workload needs true multi-Region active-active writes with local low-latency read/write in each Region.
- **Choose CloudFront + Global Accelerator together when** an application mixes cacheable HTTP content (CloudFront) with dynamic/non-HTTP traffic needing fast regional failover and static IPs (Global Accelerator).
- **Choose S3 Cross-Region Replication when** objects must exist durably in another Region for DR/latency/compliance; add S3 Multi-Region Access Points when you need a single endpoint that automatically routes to the best/failover Region.
- **Remember IAM, Route 53, CloudFront, and WAF-for-CloudFront are global services when** designing multi-Region DR — never plan to "replicate" them per Region; treat regional services (EC2, RDS, Lambda, VPC, ELB, EBS) as the ones that must be explicitly deployed per Region.
- **Choose Direct Connect (optionally with a VPN backup) when** a global/hybrid architecture needs consistent, high-volume, low-latency private connectivity to on-premises rather than routing over the public internet.
