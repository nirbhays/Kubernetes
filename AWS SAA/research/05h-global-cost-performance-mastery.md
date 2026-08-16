# Global Architectures, Cost & Performance Optimization Mastery (SAA-C03)

## Multi-Region Architecture Patterns: Active-Active vs Active-Passive

**Decision boundary:** Active-passive (pilot light, warm standby, backup/restore) is a **Reliability/DR** answer — trigger words "RTO/RPO," "disaster recovery," "regional outage." Active-active is a **Performance + Reliability** answer — trigger words "global users," "low latency worldwide," "zero downtime failover," "no data loss across regions."

- **Pilot light**: core services (usually just DB replication) running in DR region, everything else scaled to zero. Cheapest, slowest RTO. Exam cue: "minimize cost" + "acceptable to wait minutes."
- **Warm standby**: scaled-down but fully functional stack in DR region. Middle RTO/cost. Cue: "reduced capacity is acceptable temporarily."
- **Multi-site active-active**: full capacity in 2+ regions, traffic distributed by Route 53. Lowest RTO (near-zero), highest cost. Cue: "no downtime," "active-active," "seamless failover."
- **Distractor**: Multi-AZ is NOT multi-region DR. If the question says "regional outage" or "entire AWS Region," Multi-AZ alone is always wrong — you need cross-region replication.

**Key exam trap**: "Multi-region for compliance/data residency" is not the same requirement as "multi-region for DR" or "multi-region for latency" — read the requirement driving the design, because the correct service (Route 53 policy, Aurora Global DB, S3 replication rules) differs by intent.

## Route 53 Routing Policies — When Each Wins

| Policy | Choose when... | Distractor to reject |
|---|---|---|
| **Latency-based** | "Route users to the region/endpoint with the lowest network latency" — pure performance ask | Geolocation (that's about *where the user is*, not *speed*) |
| **Geoproximity** (traffic flow only) | Need to shift traffic between regions using a **bias** value without moving users geographically otherwise | Geolocation (no bias/weighting capability) |
| **Geolocation** | Compliance, content licensing, language localization — "must serve EU users from EU region" (legal/regulatory requirement) | Latency-based (doesn't guarantee a specific region) |
| **Weighted** | Blue/green, canary releases, A/B testing — percentage-based split | Failover (that's binary, not percentage) |
| **Failover** | Active-passive DR with health checks | Weighted (no primary/secondary concept) |
| **Multivalue answer** | Simple client-side load balancing/health checking without an ALB, returns multiple healthy IPs | Confused with Round Robin DNS — MVA actually health-checks each record |

**Exam trigger**: "lowest latency" → latency-based. "Users in a specific country/region for legal reasons" → geolocation. "Shift percentage of traffic gradually" → weighted. Combining health checks with any policy is standard — don't overthink it as a separate answer choice.

## Aurora Global Database

- Use when: cross-region **disaster recovery with RPO in seconds** and/or **low-latency cross-region reads** for a relational workload. Typical exam phrasing: "single global database," "reads from secondary region must be fast," "recovery in under a minute in a regional outage."
- Mechanism: storage-level replication (not logical/binlog-based), so replication lag is materially lower than standard cross-region read replicas. This is the differentiator vs a plain Aurora cross-region read replica — if the question emphasizes *very fast replication* or *sub-second/low-second lag*, Global Database beats a manually configured cross-region replica.
- Write forwarding: allows secondary regions to accept writes forwarded to the primary — useful when app in secondary region needs to write without app-level routing logic. **Caveat**: write forwarding is an Aurora MySQL-Compatible Edition feature — it is not available for Aurora PostgreSQL-Compatible Global Database. If a question specifies PostgreSQL and describes needing writes accepted in a secondary region, write forwarding is not the answer.
- Distractor: RDS (non-Aurora) does **not** have Global Database — only cross-region read replicas with higher lag. If exam says "MySQL/PostgreSQL RDS" and asks for the *fastest* cross-region DR with minimal lag, correct answer is often "migrate to Aurora and use Global Database," not "just add a cross-region read replica."

## DynamoDB Global Tables

- Use when: **multi-region active-active** for a NoSQL workload, needing local low-latency read/write in each region with eventual cross-region consistency.
- It is **multi-master** — every replica table accepts writes (unlike Aurora Global Database's single-writer-region model). This is the single most tested distinction: if the question needs *writes in multiple regions simultaneously*, Global Tables is right; Aurora Global DB is not (pre-write-forwarding nuance aside, and write forwarding still funnels to one primary, MySQL-only).
- Conflict resolution: last-writer-wins based on timestamp — if the question requires strict conflict resolution logic, flag that Global Tables' default conflict handling may not suffice.
- Distractor: DynamoDB Accelerator (DAX) is a **caching** layer, unrelated to multi-region — don't confuse the two when the question mixes "global" and "fast reads" language.

## CloudFront + Global Accelerator — Combined and Contrasted

- **CloudFront**: caches/optimizes **HTTP(S) content delivery** — static assets, API responses cacheable at edge, video streaming. Exam cue: "cacheable content," "static website," "reduce origin load," "TTL."
- **Global Accelerator**: optimizes **network-layer routing** using the AWS global network backbone for TCP/UDP traffic, including **non-HTTP** and **non-cacheable** workloads (gaming, VoIP, IoT, non-HTTP APIs). Provides static anycast IPs and instant regional failover at the network layer.
- **When to combine both**: application has a mix of cacheable static content (served via CloudFront) plus dynamic/non-cacheable or non-HTTP traffic needing fast regional failover and consistent low-latency routing (via Global Accelerator) — e.g., global SaaS with a web frontend (CloudFront) and a gaming/API backend on TCP (Global Accelerator). Also useful when you need **static IP allow-listing** for a corporate firewall while still getting CloudFront-style acceleration for parts of the app.
- Exam trigger words: "static anycast IP addresses" + "corporate firewall whitelisting" → Global Accelerator, not CloudFront (CloudFront edge IPs are not static/stable for allow-listing). "Reduce latency for a non-HTTP TCP/UDP protocol" → Global Accelerator. "Cache content close to users" → CloudFront.

---

# Cost Optimization Reasoning

## EC2 Purchase Models — Decision Boundary

| Model | Choose when | Exam trigger |
|---|---|---|
| **On-Demand** | Unpredictable, short-term, can't be interrupted, no long-term commitment desired | "unpredictable workloads," "short-term," "testing/dev spikes" |
| **Reserved Instances / Savings Plans** | Steady-state, predictable baseline usage; committed to a 1-year or 3-year term | "steady state," "known usage," "long-running production database tier" |
| **Spot** | Fault-tolerant, flexible start/end time, stateless, can be interrupted | "fault-tolerant," "flexible," "batch processing," "can withstand interruption," "significant cost reduction acceptable" |
| **Dedicated Hosts** | Licensing tied to physical cores/sockets (BYOL), compliance requiring host-level isolation | "server-bound software licenses," "regulatory requirement for physical isolation" |
| **Dedicated Instances** | Compliance needs dedicated hardware but no visibility/control over host needed | "dedicated hardware" without licensing language |

**Savings Plans vs Reserved Instances**: Savings Plans (Compute or EC2 Instance) give commitment-based discounts with more flexibility (instance family/size/OS/region flexibility for Compute Savings Plans; also applies to Fargate and Lambda). RIs are more rigid but can be resold on the Reserved Instance Marketplace. If the question emphasizes **flexibility across instance families or including serverless (Lambda/Fargate)**, Savings Plans wins. If it emphasizes **capacity reservation guarantee**, RI (specifically a zonal/AZ-scoped RI) is the answer — Savings Plans do not guarantee capacity, and even a regional-scoped RI does not reserve capacity (only AZ-scoped RIs do).

## Savings Plans vs Spot — the Real Trade-off

This is a classic "both reduce cost, pick the right one" question. Savings Plans reduce cost via **commitment** (you will run this much compute regardless) — appropriate for baseline/production. Spot reduces cost via **interruptibility** — appropriate for elastic/batch/stateless capacity. Correct architecture at scale = a **layered strategy**: Savings Plans/RI cover baseline steady-state capacity, On-Demand covers unpredictable delta, Spot covers flexible/fault-tolerant burst — this "blend" answer is frequently the best-scoring choice on cost-optimization scenario questions that describe a workload with both a steady floor and a bursty ceiling.

## Auto Scaling for Cost

- **Target tracking** is the default cost-efficient answer for "scale to match load automatically" — simplest to reason about and exam-preferred unless the question needs scheduled or step-based logic.
- **Scheduled scaling**: use when load pattern is *predictable by time* (e.g., batch jobs at night, business-hours traffic) — lets you proactively set capacity (including scaling down to a hard floor outside business hours) ahead of a known pattern, rather than waiting for a metric to cross a threshold.
- **Predictive scaling**: forecasts demand from historical data and scales ahead of it — trigger words "recurring daily/weekly pattern," "scale ahead of predictable spikes."
- Mixed instance policies + Spot allocation strategies inside an ASG (capacity-optimized, price-capacity-optimized) are the exam's preferred way to say "reduce cost of an Auto Scaling fleet while maintaining availability" — combines Spot savings with diversification to reduce interruption risk.

## Lambda Cost Reasoning

- Cost driver = **invocations × duration × memory allocated** (and now also provisioned concurrency if used). Increasing memory can *reduce* cost if it proportionally reduces execution time (more memory = more CPU) — a classic "counter-intuitive but correct" exam answer: "increase memory to reduce total cost" is valid when duration drops enough.
- **Provisioned Concurrency** costs extra and is a **performance** (cold start) fix, not a cost optimization — don't pick it when the question asks purely to reduce cost.
- Lambda vs EC2/Fargate cost crossover: Lambda is cheaper for **spiky, low-to-moderate, short-duration** workloads; for sustained high-throughput long-running compute, container/EC2 with Savings Plans becomes cheaper. Exam cue: "infrequent," "unpredictable," "short execution" → Lambda; "constant high volume," "long-running" → containers/EC2.

## S3 Storage Classes & Lifecycle

| Class | Use when |
|---|---|
| **S3 Standard** | Frequently accessed, unknown/short-term retention |
| **S3 Intelligent-Tiering** | **Unknown or unpredictable access patterns** — this is the exam's default answer whenever the question says "access patterns are unknown/changing" and asks to minimize cost *without* performance/retrieval-time tradeoffs (no retrieval fees, small monitoring fee) |
| **S3 Standard-IA / One Zone-IA** | Infrequent access but need millisecond retrieval; One Zone-IA when data is reproducible/non-critical (no AZ redundancy needed) — trigger: "easily recreatable" |
| **S3 Glacier Instant Retrieval** | Archive but need **immediate (ms) access**, accessed maybe once a quarter |
| **S3 Glacier Flexible Retrieval** | Archive, retrieval in minutes-to-hours acceptable, occasional access |
| **S3 Glacier Deep Archive** | Lowest cost, retrieval in hours acceptable, accessed ~once or twice a year — trigger: "regulatory retention," "7-10 years," "rarely if ever accessed" |

**Lifecycle policies**: the "set it and forget it" cost answer whenever access patterns *are* known/predictable and follow a decay curve (hot → warm → cold over time) — contrast with Intelligent-Tiering, which is for *unknown/unpredictable* patterns. Don't pick Intelligent-Tiering when the question gives you a clear, known aging timeline — lifecycle rules are cheaper and simpler there.

## CloudFront Cost Optimization

- Increasing **TTL / cache hit ratio** is the primary cost lever — reduces both origin load and CloudFront-to-origin data transfer cost. Exam framing: "reduce cost and load on origin" → increase cacheable content / TTLs, use Cache-Control headers, consolidate cache keys.
- **Price class selection**: restricting CloudFront **price class** to only the edge locations covering your actual user base (e.g., exclude South America/Australia edge pricing tiers) reduces cost when the question specifies a limited target geography.
- Data transfer from CloudFront to internet is cheaper than data transfer directly from EC2/S3 to internet at scale — "reduce data transfer costs for globally distributed content" → CloudFront is frequently the correct primary lever, not just a performance one.

## DynamoDB Capacity Modes

- **On-Demand**: unpredictable/spiky traffic, new applications without traffic history, avoid capacity planning — costs more per request but zero waste from over-provisioning. Trigger: "unpredictable," "unknown traffic patterns," "don't want to manage capacity."
- **Provisioned (with Auto Scaling)**: steady, predictable traffic — cheaper at scale if utilization is high and consistent. Trigger: "known, steady request rate," "cost-sensitive at high, consistent volume."
- Distractor: Provisioned without Auto Scaling is rarely the right answer on exam unless the question explicitly wants a hard cap for cost control (predictable budget ceiling) — Auto Scaling on provisioned mode is the usual "best of both" answer for known-but-variable workloads.

## RDS/Aurora Scaling Cost Reasoning

- **Read replicas** scale read throughput horizontally and cost linearly per replica — right answer when read-heavy bottleneck, wrong when write-bottlenecked (replicas don't help writes).
- **Aurora Serverless v2**: scales compute capacity automatically in fine-grained increments — cost answer for **intermittent, unpredictable, or variable workloads** (dev/test, infrequent apps, SaaS with variable per-tenant load) where paying for constant provisioned capacity would waste money. Trigger: "variable/unpredictable database load," "infrequently used application," "spiky."
- **Vertical scaling (bigger instance class)** is simplest but has ceiling and downtime (non-Aurora Multi-AZ) — not the cost-optimal answer when workload is spiky (you'd be paying for peak capacity at all times); Serverless v2 or read replicas usually beat it on cost-optimization questions.
- Multi-AZ standby costs double compute for HA — this is a **Reliability** cost, not eliminable without sacrificing HA; don't "optimize" it away when the question requires HA.

## NAT Gateway Cost Traps

- NAT Gateway charges **per-hour + per-GB processed** — a very common cost-optimization scenario is "high NAT Gateway data processing charges" for traffic that doesn't need to leave the VPC at all (e.g., S3/DynamoDB access from private subnets).
- **Fix pattern**: Gateway VPC Endpoints (S3, DynamoDB — free) or Interface VPC Endpoints (PrivateLink, hourly + data cost but still often cheaper than NAT for high volume) eliminate the need to route that traffic through NAT Gateway entirely. If the question shows a private subnet resource talking to S3/DynamoDB via NAT and asks to reduce cost, the answer is **add a Gateway VPC Endpoint**, not "resize the NAT Gateway" or "add more NAT Gateways."
- One NAT Gateway per AZ is a **resilience** best practice (avoid cross-AZ data transfer + single point of failure), but exam may test that this also *multiplies* NAT cost — tension between HA and cost is a deliberate distractor; pick based on what the question is actually optimizing for.

## VPC Endpoints for Cost Savings

- **Gateway endpoints** (S3, DynamoDB only): no hourly charge, no data processing charge — always the free/cheap answer for these two services when traffic is currently traversing NAT Gateway or an Internet Gateway.
- **Interface endpoints (PrivateLink)**: hourly charge per AZ + per-GB, used for most other AWS services (SNS, SQS, Kinesis, Secrets Manager, etc.) — still typically cheaper than NAT Gateway data processing at volume, and add the side-benefit of keeping traffic off the public internet (security angle too — watch for questions combining cost + "traffic must not traverse the internet").

## Data Transfer Cost Reasoning

- Data transfer **within the same AZ over private IP addresses** is free; the same traffic over public/Elastic IP addresses within the same AZ is not automatically free. Cross-AZ, cross-Region, and egress-to-internet costs increase in that order. Architecture choices that keep chatty traffic same-AZ over private IPs (e.g., placement groups, AZ-aware routing, same-AZ NAT Gateway usage per subnet) reduce cost — commonly tested with NAT Gateway/AZ topology questions.
- Egress to internet is the most expensive tier — CloudFront, S3 Transfer Acceleration only where actually beneficial, and Direct Connect for high-volume steady on-prem-to-cloud transfer are the standard cost levers.
- **Direct Connect vs Site-to-Site VPN for cost**: DX has lower long-term data transfer cost for high, consistent volume; VPN is cheaper for lower/variable volume with no upfront commitment. Trigger: "large, consistent volume of data transferred to on-premises" → Direct Connect (plus DX has a cost benefit via reduced data transfer OUT rates compared to internet egress).

## Storage Tiering (General Reasoning)

Beyond S3, the same known-vs-unknown access pattern logic applies across EBS (gp3 vs io2 vs st1/sc1 based on IOPS/throughput needs vs cost), EFS (Infrequent Access lifecycle management), and FSx. Exam signal: "cost-effective," "infrequently accessed," "large sequential throughput workloads" → cheaper HDD-backed tiers (st1 for big data/streaming, sc1 for cold/infrequent); "sustained high IOPS," "transactional databases" → gp3/io2 SSD tiers, provisioned independently of volume size with gp3 (cost lever: gp3 lets you provision IOPS/throughput without buying a bigger/more expensive volume, unlike gp2).

---

# Performance Problem → AWS Solution Candidates Matrix

| Performance Problem | Primary Candidate(s) | Notes / Distractor to Reject |
|---|---|---|
| **Global users experience high latency to a single-region app** | Route 53 latency routing + multi-region deployment; CloudFront for static/cacheable parts; Global Accelerator for TCP/UDP/non-cacheable | Don't pick a bigger instance type — that fixes compute, not network latency |
| **Relational DB read bottleneck** | Read replicas (same-region or cross-region); ElastiCache in front of DB for hot reads; Aurora Serverless v2 for variable load | Don't pick sharding/write scaling fixes — read replicas specifically address read-only bottlenecks |
| **DynamoDB read latency / hot partition throttling** | DAX (microsecond caching) for read latency; fix partition key design for hot-partition throttling; On-Demand or higher provisioned RCU for throughput throttling | DAX solves *latency*, not *throttling from poor key design* — know which symptom the question describes |
| **Static content delivery is slow globally** | CloudFront (edge caching) | S3 Transfer Acceleration is for **uploads** to a single bucket over long distances, not general content delivery — common distractor |
| **Repeated identical DB queries hammering the database** | ElastiCache (Redis/Memcached) as a cache-aside layer in front of RDS/Aurora | Read replicas don't dedupe repeated *identical* queries as efficiently/cheaply as an in-memory cache |
| **High-throughput real-time data streaming / ingestion** | Kinesis Data Streams (custom processing, replay) or Kinesis Data Firehose (managed delivery to S3/Redshift/OpenSearch) or MSK (Kafka compatibility requirement) | SQS is for decoupled point-to-point/queueing, not high-throughput ordered streaming with multiple consumers — trigger "multiple consumers need to read the same stream" → Kinesis, not SQS |
| **Shared file storage across multiple Linux EC2 instances** | EFS (multi-AZ, POSIX, NFS) | EBS is single-instance (or Multi-Attach only within an AZ, specific instance types, still not a general "shared storage" answer) — if "multiple instances, concurrent read/write, Linux" → EFS |
| **Shared file storage across multiple Windows instances** | FSx for Windows File Server (SMB) | Don't pick EFS — POSIX/NFS only |
| **High-performance computing / ML shared storage needing very high throughput** | FSx for Lustre | Trigger: "HPC," "machine learning training," "high IOPS/throughput scratch storage" |
| **API layer has high latency due to repeated auth/compute-heavy logic per request** | API Gateway caching, Lambda with increased memory / provisioned concurrency (cold starts), ElastiCache for session/token caching | — |
| **Cold start latency for Lambda in latency-sensitive path** | Provisioned Concurrency | This is a **performance**, not cost, fix — don't confuse with cost optimization questions |
| **Compute-bound workload needs more power without re-architecting** | Vertical scaling (larger instance family/size) or compute-optimized instance family | Horizontal scaling assumes statelessness — if workload can't be distributed, vertical scaling / instance family change is the right lever |
| **Network throughput bottleneck between instances in a cluster** | Cluster placement group (low latency, high throughput, same AZ) + Elastic Fabric Adapter for HPC/tightly-coupled workloads | Spread/partition placement groups solve *availability*, not throughput — know the three placement group types by purpose |
| **Database connection exhaustion under high concurrency** | RDS Proxy | Pools/multiplexes connections, especially relevant for Lambda-to-RDS patterns where each invocation could open a new connection |
| **Slow large file uploads to S3 from geographically distant clients** | S3 Transfer Acceleration | Distinct from CloudFront (delivery/download) — this is specifically upload acceleration via edge locations |

---

# AWS Well-Architected Framework — 6 Pillars (Exam-Relevant Lessons Only)

## Operational Excellence
- Favor **Infrastructure as Code** (CloudFormation/CDK) and small, reversible, frequent changes over large manual changes — exam framing: "reduce risk of deployment errors" → IaC + CI/CD, not manual console changes.
- Use **runbooks/playbooks** and automate response where possible (EventBridge + Lambda/SSM Automation) — trigger: "automate operational response to an event."

## Security
- **Principle of least privilege** applied via IAM policies/roles/SCPs is the near-universal correct answer whenever a question asks "how to restrict access" — reject broad wildcard (`*`) permission answers.
- **Never hardcode credentials** — use IAM roles for compute (EC2 instance profiles, Lambda execution roles), Secrets Manager/Parameter Store for app secrets. Any answer choice with access keys embedded in code/AMI is wrong.
- **Defense in depth**: security groups (stateful, instance-level) + NACLs (stateless, subnet-level) work together, not as substitutes — exam tests whether you know NACLs need explicit inbound AND outbound rules (ephemeral ports) while SGs are stateful.
- Encryption: prefer **KMS-managed encryption at rest by default** for new resources when the question doesn't specify a strict compliance/BYOK need; use **customer-managed CMKs** when the requirement mentions key rotation control, cross-account access control, or audit of key usage.
- Data in transit: TLS/SSL termination at ALB or CloudFront with ACM-issued certs is the standard answer for "encrypt traffic between clients and the app" without operational cert management overhead.

## Reliability
- **Multi-AZ ≠ Multi-Region** (see above) — match the blast radius in the question to the right scope of redundancy.
- Design for **failure as the default assumption**: stateless application tier + externalized session/state (ElastiCache, DynamoDB) enables horizontal scaling and graceful instance replacement — trigger: "instance can be terminated at any time" (Spot, ASG health-check replacement) requires stateless design.
- **Health checks + Auto Scaling replacement** and **circuit breakers/retries with exponential backoff** (SDK default behavior, or explicitly via Step Functions/SQS DLQ) are the standard resilience patterns tested for distributed system fault handling.
- Backups: automated RDS/Aurora snapshots + cross-region snapshot copy for DR; versioning + cross-region replication for S3 — match RPO stated in the question to the mechanism (continuous replication vs periodic snapshot).

## Performance Efficiency
- Choose the **right resource type/family for the workload shape** (compute-optimized, memory-optimized, storage-optimized, accelerated computing) rather than defaulting to general purpose — exam often signals workload type (e.g., "in-memory caching," "video transcoding," "genomics") to steer instance family choice.
- **Serverless-first** when the question emphasizes reducing operational/scaling overhead for variable load — Lambda, Fargate, DynamoDB On-Demand, Aurora Serverless v2 collectively represent the "let AWS handle scaling" performance-efficiency answer.
- Use **caching at every layer where re-computation or repeated I/O is the bottleneck** (CloudFront, API Gateway cache, DAX, ElastiCache) — this pillar's most-tested single idea.

## Cost Optimization
- **Right-sizing** based on actual utilization (CloudWatch/Compute Optimizer recommendations) before committing to Reserved Instances/Savings Plans — sequence matters: right-size first, then commit.
- Turn off/scale down non-production resources on a schedule (dev/test environments) — Instance Scheduler / scheduled scaling is the standard "reduce cost for non-prod" answer.
- Use **Cost Explorer, Budgets, and Trusted Advisor** for visibility/governance-triggered questions ("notify when spend exceeds threshold" → Budgets; "identify idle/underutilized resources" → Trusted Advisor/Compute Optimizer).

## Sustainability
- Newer, lighter-weighted pillar on the exam — key testable ideas: prefer **managed/serverless services** (AWS optimizes underlying hardware utilization/efficiency at scale better than self-managed fleets), **right-size to avoid over-provisioning** (waste = both cost and sustainability issue — these two pillars' guidance often overlaps and reinforces the same correct answer), and choose **regions strategically** when sustainability/carbon goals are explicitly mentioned in the question (AWS guidance recommends selecting regions with lower-carbon energy sources; account-level usage emissions can be tracked over time via the Customer Carbon Footprint Tool). If a question explicitly says "minimize environmental impact" alongside a choice that's otherwise cost/performance-neutral, favor managed services and higher resource utilization efficiency over self-managed always-on infrastructure.
