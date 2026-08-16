# AWS SAA-C03 — 20 Architecture Diagram Critique Exercises

*Model answers follow each exercise — try to spot the issues yourself before reading on.*

### Exercise 1: E-Commerce Flash-Sale Platform — Single-Instance Bottleneck

**Starting architecture (ASCII diagram):**
```text
Internet
   |
   v
[Route 53 (simple routing)]
   |
   v
[EC2 - single instance, us-east-1a, m5.2xlarge]
   |  (session state stored in local /tmp on instance)
   v
[RDS MySQL - single AZ, db.r5.xlarge, gp2 storage]
   |
   v
[S3 bucket - product images, public-read ACL]
```
**Scenario context:** A mid-size retailer runs seasonal flash sales that spike traffic 20x for a few hours. Product catalog and order data live in MySQL; product images are served directly from S3 with public ACLs.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: A single EC2 instance is both a scaling and availability bottleneck; local session state prevents horizontal scaling (sticky-session dependency the moment you try to add instances); single-AZ RDS means any AZ impairment causes an outage during your highest-revenue hours; the S3 bucket with public-read ACLs is a stale, riskier pattern than a bucket policy plus Origin Access Control (OAC) and provides no CDN caching for images, wasting bandwidth and adding latency during spikes; m5.2xlarge sized for peak means over-provisioning cost 360+ days a year.
- Improved architecture (ASCII diagram):
```text
Internet
   |
   v
[Route 53 -> CloudFront (caches images + static assets)]
   |
   v
[Application Load Balancer, multi-AZ]
   |
   v
[Auto Scaling Group (EC2 or ECS Fargate), 2-3 AZs,
 target tracking on CPU/RequestCount, scheduled scaling
 pre-sale]
   |
   +--> [ElastiCache for Redis - replication group with
   |     Multi-AZ automatic failover, holds session state]
   |
   v
[RDS MySQL Multi-AZ + read replicas for catalog reads]
   |
   v
[S3 (private, OAC-only) <- served via CloudFront]
```
- Reasoning: Offloading session state to ElastiCache lets the ASG scale/replace instances freely (12-factor stateless tier). Multi-AZ RDS gives automatic failover during the exact window revenue is highest. CloudFront + private S3 with Origin Access Control cuts egress cost (CDN cache hit ratio) and closes the public-bucket security gap. Scheduled scaling policies (scale out 30 min before a known flash-sale start) reduce cold-start latency versus reactive-only scaling, and scaling back down after the sale eliminates year-round over-provisioning cost.

---

### Exercise 2: E-Commerce Flash-Sale Platform — Fixed-Capacity Over-Provisioning

**Starting architecture (ASCII diagram):**
```text
Users (global)
   |
   v
Route 53 (simple routing)
   |
   v
ALB (us-east-1, 2 AZs)
   |
   v
EC2 Auto Scaling Group (m5.2xlarge, min=10 max=10, On-Demand)
   |
   v
RDS PostgreSQL (db.r5.4xlarge, Multi-AZ)
   |
   v
Self-managed Redis on EC2 (single instance, session + cart cache)

Static product images served directly from EC2 web root
No caching layer in front of ALB
```
**Scenario context:** An online retailer runs seasonal flash sales where traffic spikes 20x for 2-hour windows, then drops to baseline for the rest of the month.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: The ASG is fixed at `min=10 max=10` — it's sized for peak load 24/7/30, so roughly 95% of the month it pays for capacity it doesn't use (cost is the primary weak pillar here, not availability — Multi-AZ RDS and multi-AZ ALB already cover HA reasonably). The self-managed Redis on a single EC2 instance is an unmanaged single point of failure for cart/session data with no failover. Static images served from the web tier waste compute cycles and add latency for global users. No caching layer means every product-page hit round-trips to RDS.
- Improved architecture (ASCII diagram):
```text
Users (global)
   |
   v
Route 53 (latency-based) --> CloudFront (caches product images/static assets, WAF attached)
   |
   v
ALB (us-east-1, 3 AZs)
   |
   v
EC2 ASG (mixed instances, Graviton + x86, min=2 max=40,
          target-tracking on CPU, scheduled scale-out ahead of
          known sale start, Spot for 60% of burst capacity)
   |
   v
ElastiCache Serverless (Redis) -- session/cart, spans multiple AZs
   |
   v
Aurora PostgreSQL (Serverless v2, Multi-AZ, auto-scales ACUs with traffic)
   |
   v
S3 (product images, versioned) <-- served via CloudFront, not EC2
```
- Reasoning: Aurora Serverless v2 and a right-sized ASG with target-tracking/scheduled scaling plus Spot for burst capacity eliminate the 24/7 peak-sizing cost tax while still meeting the 20x spike. Moving static assets to S3+CloudFront cuts origin load and improves TTFB globally. ElastiCache Serverless removes the unmanaged-Redis SPOF and scales with cart traffic automatically. WAF on CloudFront mitigates credential-stuffing/scraping bots that spike during sales. This is a cost-and-resilience fix together, not just "add more instances."

---

### Exercise 3: Video-on-Demand / Media Streaming Service

**Starting architecture (ASCII diagram):**
```text
Content creators --> Upload --> EC2 (single instance, us-east-1)
                                 -- runs ffmpeg, transcodes to a single MP4 rendition
                                     |
                                     v
                              EBS volume (2 TB gp3, stores all transcoded renditions)
                                     |
                                     v
                              Nginx on same EC2 serves video files directly
                              to viewers worldwide, single bitrate, no CDN
                                     |
                                     v
                              RDS PostgreSQL (single AZ) -- metadata, view counts,
                              watch history
```
**Scenario context:** A niche streaming startup hosts documentary content for a global subscriber base, currently transcoding and serving every byte of every stream from a single EC2 instance and its attached EBS volume in one region.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is fundamentally a performance/architecture-pattern failure, not just an HA gap. Serving video bytes from EC2/EBS means every stream transits compute you pay for by the hour, and the instance's network/EBS throughput becomes a hard ceiling on concurrent viewers; EBS is provisioned, single-instance-attached block storage, not built for massive concurrent read fan-out. Transcoding new uploads on the same instance that serves live traffic means a viral video competes for CPU with in-flight transcode jobs. Single-AZ EC2 and single-AZ RDS have no fault isolation, and global users all hit one region — high latency and poor buffering far from us-east-1. There's also no adaptive bitrate — a single MP4 rendition burns bandwidth and stalls playback for users on poor connections.
- Improved architecture (ASCII diagram):
```text
Creators --> S3 (raw uploads bucket, event notification)
                    |
                    v
             EventBridge --> AWS Elemental MediaConvert
             (transcodes to multi-bitrate HLS/DASH renditions)
                    |
                    v
             S3 (processed renditions, Standard for hot titles +
             Intelligent-Tiering for long-tail catalog)
                    |
                    v
             CloudFront (global edge caching, signed URLs/cookies
             for access control; pair with MediaPackage + SPEKE
             if full DRM/key rotation is required)
                    |
                    v
             Viewers worldwide (low-latency, edge-cached, ABR)

Metadata/view counts/watch history --> RDS PostgreSQL Multi-AZ
(or DynamoDB for high-frequency view-count/watch-progress writes)
```
- Reasoning: Moving video delivery entirely to S3 + CloudFront removes compute from the data path (pay for storage/transfer, not idle EC2 hours) and gives global low-latency delivery via edge caching — directly answering the "global/lower-latency" requirement. MediaConvert decouples transcoding from serving and produces adaptive-bitrate (HLS/DASH) renditions, reducing rebuffering and bandwidth cost simultaneously. Signed URLs/cookies on CloudFront replace "security via obscurity" of raw EBS-hosted files; true DRM (key rotation, license servers) would layer MediaPackage + SPEKE on top. Multi-AZ RDS protects metadata/watch-history availability, and the API/metadata tier is now a thin control-plane service rather than the data-plane bottleneck.

---

### Exercise 4: IoT Sensor Ingestion Pipeline — API Gateway + Lambda + RDS Anti-Pattern

**Starting architecture (ASCII diagram):**
```text
[50,000 field sensors]
   |  (HTTPS POST, one request per reading, every 5s)
   v
[API Gateway (REST)]
   |
   v
[Lambda - writes directly to RDS PostgreSQL]
   |
   v
[RDS PostgreSQL - single db.t3.medium, single AZ]
```
**Scenario context:** An agricultural tech company collects soil-moisture and temperature readings from 50,000 field sensors across several countries, writing every reading straight into a relational database for later dashboarding.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a performance/scalability failure at the data layer: 50,000 sensors × 1 reading/5s ≈ 10,000 writes/sec sustained, which will exhaust a t3.medium's connections and baseline IOPS almost immediately (Lambda-per-request also multiplies concurrent DB connections, a classic "Lambda + RDS connection storm" anti-pattern). There's no buffering/backpressure — a DB slowdown cascades directly into API Gateway timeouts and sensor-side retries/data loss. No decoupling means you can't reprocess historical data or fan out to multiple consumers (analytics, alerting) without hitting the same DB.
- Improved architecture (ASCII diagram):
```text
[50,000 field sensors]
   |  (MQTT via IoT Core for lower overhead and per-device auth)
   v
[AWS IoT Core] --> [Kinesis Data Streams]
                         |
          +--------------+---------------+
          v                              v
  [Kinesis Data Firehose]        [Lambda - real-time alerts]
          |                              |
          v                              v
  [S3 data lake, partitioned      [DynamoDB - latest reading
   by date/device, Parquet]        per sensor for dashboards]
          |
          v
  [Athena / Redshift Spectrum for analytics queries]
          |
  [RDS Proxy + RDS Multi-AZ - only for relational
   reference data (device registry, farm metadata)]
```
- Reasoning: IoT Core is purpose-built for device fleets (MQTT, per-device X.509 auth, device shadow state) and is far cheaper per-message than API Gateway + Lambda at this volume. Kinesis/Firehose decouples ingestion rate from processing rate, absorbing bursts without data loss and enabling multiple independent consumers (real-time alerting vs. batch analytics) — solving both the performance and the single-point-of-failure problem. Moving time-series data to S3/Athena instead of RDS removes the write bottleneck entirely and is drastically cheaper at this volume. RDS is retained only for genuinely relational, low-volume data, fronted by RDS Proxy to prevent connection exhaustion from any remaining Lambda callers.

---

### Exercise 5: IoT Sensor Ingestion Platform — Self-Managed Broker Anti-Pattern

**Starting architecture (ASCII diagram):**
```text
50,000 field sensors (MQTT, intermittent connectivity)
        |
        v
EC2 instance running Mosquitto broker (single instance, public IP, us-west-2)
        |
        v
Application on same EC2 polls broker, writes to RDS PostgreSQL (single AZ, db.t3.medium)
        |
        v
Nightly cron job exports RDS table to CSV in S3 for analytics team (Athena queries against CSVs)
```
**Scenario context:** An industrial IoT company collects telemetry (temperature, vibration, GPS) from 50,000 field sensors every 30 seconds for predictive maintenance analytics.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: The core weakness is architectural mismatch for scale/security — a self-managed Mosquitto broker on a single public EC2 instance can't handle 50K devices' connection churn/reconnect storms, has no per-device authentication/authorization, and is a single point of failure with no mutual TLS mentioned. Writing ~1,667 writes/sec (50,000 devices ÷ 30s) directly into a `db.t3.medium` single-AZ RDS instance will hit connection/IOPS limits. Nightly CSV export means analytics is up to 24h stale, and Athena-over-CSV is slower and costlier per query than a columnar format.
- Improved architecture (ASCII diagram):
```text
50,000 sensors (MQTT/TLS, per-device X.509 cert)
        |
        v
AWS IoT Core (managed MQTT broker, device registry, per-device auth via IoT policies)
        |
        v
IoT Rules Engine --> splits to:
   |-- Kinesis Data Streams (on-demand mode) --> Kinesis Data Firehose --> S3 (Parquet, partitioned by date/device)
   |                                                                          |
   |                                                                          v
   |                                                                   Glue Catalog + Athena (columnar queries)
   |
   |-- DynamoDB (latest-reading table, per-device hot state for dashboards)
```
- Reasoning: IoT Core replaces the unmanaged broker with per-device cert-based auth (fixes the security gap), scales natively to millions of devices, and removes the SPOF. Kinesis + Firehose decouples ingestion rate from storage/query, and writing Parquet instead of CSV typically cuts Athena scan costs by 80–90%+. DynamoDB serves "current state" dashboard reads without hammering an analytical store. This also removes the RDS write bottleneck entirely — RDS was never the right tool for high-cardinality time-series ingestion at this scale.

---

### Exercise 6: Internal Enterprise Reporting Tool — Public Exposure

**Starting architecture (ASCII diagram):**
```text
Corporate employees (VPN not required)
   |
   v
[Internet-facing ALB, public subnets]
   |
   v
[EC2 fleet, public subnets, Auto Scaling Group]
   |
   v
[RDS SQL Server - public subnet, publicly accessible = true]
   |
   v
[Security Group: 0.0.0.0/0 on port 1433 "for developer convenience"]
```
**Scenario context:** A 3,000-person manufacturing company built an internal BI/reporting tool for finance and ops teams, but deployed it using the same public-facing pattern as their customer website.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a pure security-pillar failure, and a severe one: an internal-only tool has zero business reason for a public-facing ALB or public subnets; the database is directly internet-reachable with a security group open to 0.0.0.0/0 on 1433 — a textbook data-breach/ransomware vector (SQL Server is a common target for internet-wide scanning). There's no network segmentation between web/app/data tiers, and no defense-in-depth (WAF, NACLs) even if it were meant to be public. Availability-wise it's reasonably provisioned (ASG + ALB), so don't over-fix what isn't broken — the grading signal is security, not HA.
- Improved architecture (ASCII diagram):
```text
Corporate employees
   |
   v
[Corporate VPN / AWS Client VPN / Direct Connect]
   |
   v
[Internal ALB, private subnets, security group allows
 only corporate CIDR]
   |
   v
[EC2 ASG or ECS, private subnets, multi-AZ]
   |
   v
[RDS SQL Server Multi-AZ, private subnets,
 publiclyAccessible = false, SG allows port 1433
 ONLY from app-tier security group]
   |
   v
[Secrets Manager - DB credentials, rotated automatically]
```
- Reasoning: Eliminating public subnets/public accessibility for both the ALB and RDS closes the internet exposure entirely — access is only possible through the corporate network boundary (VPN/Direct Connect), matching the actual access requirement ("internal tool" ≠ "internet tool"). Security-group-to-security-group references (app SG -> DB SG) replace the 0.0.0.0/0 rule, enforcing least privilege regardless of IP changes. Secrets Manager removes hardcoded/shared DB credentials. This is also incidentally cheaper (no NAT/data-transfer costs tied to public internet paths), and instances can be right-sized knowing traffic is bounded to internal user counts.

---

### Exercise 7: Internal Enterprise Tool — Hardcoded Credentials (Expense Reporting)

**Starting architecture (ASCII diagram):**
```text
Employees (corporate laptops, VPN-connected to corp network)
        |
        v
Internet --> ALB (public subnet, 0.0.0.0/0 allowed on security group)
        |
        v
EC2 (Java app, public subnet, IAM role with AdministratorAccess attached)
        |
        v
RDS Oracle (public subnet, publicly accessible = true, master password
in app's application.properties file committed to internal Git repo)
```
**Scenario context:** A mid-size enterprise built an internal expense-reporting tool used only by ~2,000 employees, all of whom already connect via corporate VPN.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is almost entirely a security-pillar failure, not availability/cost: (1) an internal-only app is exposed to the public internet unnecessarily, expanding attack surface; (2) RDS is publicly accessible with credentials hardcoded and committed to source control — a critical exposure since any Git history access leaks DB credentials permanently; (3) the EC2 instance role has `AdministratorAccess`, violating least privilege — a single app-tier RCE becomes a full account compromise; (4) DB and app tiers sit in public subnets with no network segmentation.
- Improved architecture (ASCII diagram):
```text
Employees (corp VPN, on-prem)
        |
        v (Direct Connect / Site-to-Site VPN into VPC)
Internal ALB (private subnet, SG allows only corp CIDR)
        |
        v
EC2 ASG (private subnet, IAM role scoped to only the S3 bucket + Secrets Manager secret it needs)
        |
        v
RDS Oracle (private subnet, publicly accessible = false)
        |
        v
Secrets Manager (DB credentials, auto-rotation enabled) <-- fetched at runtime via IAM role, never in code
```
- Reasoning: Since every user already comes from a trusted corporate network, there's no business reason to expose anything publicly — moving ALB/EC2/RDS into private subnets reachable only via Direct Connect/VPN removes most of the internet-facing attack surface at essentially zero cost. Secrets Manager with rotation eliminates hardcoded credentials and the Git-leak risk (existing leaked credentials should also be rotated and purged from history). Replacing the admin IAM role with a least-privilege role scoped via policy conditions is the single highest-leverage fix. Availability/cost were never really the problem here — resist the urge to "add Multi-AZ everything" when the actual finding is credential and network exposure.

---

### Exercise 8: SaaS Multi-Tenant Project Management App — Isolation Enforcement

**Starting architecture (ASCII diagram):**
```text
Tenant A, Tenant B, Tenant C, ... Tenant N (all customers)
   |
   v
[ALB, multi-AZ]
   |
   v
[ECS Fargate service, shared by all tenants]
   |
   v
[Single RDS PostgreSQL instance, single database,
 single schema, tenant_id column on every table]
   |
   v
[Single S3 bucket, all tenant file uploads under
 s3://app-uploads/{tenant_id}/... with same IAM
 role used for every tenant's Lambda export job]
```
**Scenario context:** A project-management SaaS onboarded several enterprise clients, including ones in regulated industries, who now require contractual guarantees around tenant data isolation.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a security/isolation-pillar failure specific to multi-tenancy: relying purely on application-layer `WHERE tenant_id = ?` filtering with no database-level enforcement means a single query bug or SQL-injection vector can leak cross-tenant data — there's no defense-in-depth (no row-level security, no per-tenant schema/database option for regulated clients). The shared IAM role for the export Lambda means one compromised function has blast radius across every tenant's S3 prefix instead of being scoped per-tenant. There's also a noisy-neighbor availability risk: one tenant's heavy reporting query can degrade performance for all others since compute and DB are fully shared with no isolation tier.
- Improved architecture (ASCII diagram):
```text
Tenants (standard tier)          Tenants (regulated/enterprise tier)
   |                                        |
   v                                        v
[ALB, multi-AZ]                    [Dedicated ECS service +
   |                                 dedicated RDS instance
   v                                 per tenant, or silo VPC]
[ECS Fargate - shared pool]
   |
   v
[RDS PostgreSQL Multi-AZ, Row-Level
 Security (RLS) policies enforced
 at DB engine level per tenant_id,
 set via session variable per request]
   |
   v
[S3 - per-tenant prefixes + per-tenant
 scoped IAM roles (assumed via STS
 with tenant-specific session tags/
 conditions), SSE-KMS with per-tenant
 CMK for regulated tier]
```
- Reasoning: PostgreSQL Row-Level Security adds a database-enforced isolation layer so isolation doesn't depend solely on correct application code — a defense-in-depth control regulated customers specifically look for in vendor security questionnaires. Offering a "silo" deployment tier (dedicated RDS/compute) for regulated/enterprise tenants satisfies contractual isolation requirements without forcing that cost onto the entire customer base. Scoping IAM via STS session tags/conditions per tenant, plus per-tenant KMS keys for the regulated tier, bounds the blast radius of a compromised credential or function to a single tenant instead of the whole platform.

---

### Exercise 9: SaaS Multi-Tenant Analytics App — Noisy Neighbor & Backup Granularity

**Starting architecture (ASCII diagram):**
```text
Tenant A, Tenant B, ... Tenant N (500 tenants) --> shared subdomain routing
        |
        v
ALB --> ECS Fargate service (shared, no per-tenant isolation)
        |
        v
Single RDS PostgreSQL instance (db.r6g.4xlarge)
   - one schema per tenant (500 schemas)
   - single master credential shared by app for all tenants
        |
        v
Nightly full pg_dump backup to S3 (one large dump, all tenants together)
```
**Scenario context:** A B2B SaaS analytics vendor onboards enterprise customers (tenants) who each expect predictable performance and strong data isolation guarantees in their contracts.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: The dominant weakness is noisy-neighbor risk and weak tenant isolation — one large tenant running a heavy analytical query can starve I/O/CPU for all 499 others on the same RDS instance, directly violating per-tenant performance SLAs. A single shared master credential used across all tenant schemas means the blast radius of any credential leak or SQL-injection bug is every customer's data, which large enterprise customers will flag in security review. A single monolithic nightly backup also means restoring one tenant requires restoring/extracting from the whole dump, and RPO is 24h for everyone.
- Improved architecture (ASCII diagram):
```text
Tenants --> ALB --> ECS Fargate (tenant context resolved from JWT claim)
                          |
                          v
              Tiering by tenant size:
   - Large/enterprise tenants --> dedicated Aurora PostgreSQL cluster per tenant (or RDS instance)
   - Small/mid tenants        --> shared Aurora cluster, RLS (Row-Level Security) enforced,
                                    per-tenant DB role via Secrets Manager-issued short-lived creds
                          |
                          v
              AWS Backup (per-cluster backup plans, point-in-time recovery, per-tenant restore path)
```
- Reasoning: Splitting large/regulated tenants onto dedicated Aurora clusters removes noisy-neighbor risk and gives a clean isolation story for enterprise security questionnaires, while keeping cost-efficient pooling for smaller tenants via RLS. Per-tenant DB roles (instead of one shared master credential) with Secrets Manager-issued credentials limit blast radius. AWS Backup with per-cluster plans enables tenant-scoped RPO/RTO instead of a single 24h all-or-nothing dump. This is fundamentally a tenancy-model fix, not a "make RDS Multi-AZ" fix — Multi-AZ helps availability but doesn't address isolation.

---

### Exercise 10: Real-Time Gaming Leaderboard

**Starting architecture (ASCII diagram):**
```text
Mobile game clients (millions of concurrent players, global)
   |  (submit score after every match; leaderboard viewed far
   |   more often than submitted - read:write ~50:1, bursty
   |   around live events)
   v
[ALB] --> [API Gateway + Lambda (submit score)]
                                                     |
                                                     v
                                    RDS MySQL (db.r5.4xlarge, Multi-AZ)
                                    ORDER BY score DESC LIMIT 100 query run on
                                    every leaderboard view (global + per-region boards)
                                                     |
                                                     v
                                        1x read replica for leaderboard reads
```
**Scenario context:** A mobile battle-royale game needs a global top-100 leaderboard plus per-region leaderboards that update in near-real-time and are viewed far more often than scores are submitted.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a performance/data-modeling failure, not primarily an availability gap: `ORDER BY score DESC LIMIT 100` on a large, constantly-updated table run on every leaderboard view is an expensive sort-heavy operation that degrades badly under 50:1 read-heavy, event-driven bursty load — a relational engine is the wrong tool for a ranked-set access pattern at this scale. A single read replica saturates quickly and becomes the new bottleneck. MySQL also doesn't cleanly support "get a player's rank plus surrounding players" (a common leaderboard UX need) without expensive windowed queries. Running this on a db.r5.4xlarge Multi-AZ instance is also expensive relative to the workload — Multi-AZ was solving the wrong problem, since the bottleneck is query pattern, not node failure.
- Improved architecture (ASCII diagram):
```text
Game clients
   |
   v
[ALB] -> [ECS/EC2 game-backend service]
   |
   +--> WRITE: score submitted
   |        v
   |    ElastiCache Serverless (Redis, Sorted Sets)
   |    ZADD leaderboard:global <score> <player>
   |    ZADD leaderboard:<region> <score> <player>
   |        |
   |        v
   |    DynamoDB - player_scores, durable record of truth,
   |    async write via Lambda/stream for auditing/history
   |
   +--> READ: leaderboard view
            v
        ElastiCache Serverless (Redis)
        ZREVRANGE 0 99 (top-100, O(log N + M))
        ZRANK (player's rank + surrounding players)
```
- Reasoning: Redis Sorted Sets are purpose-built for exactly this pattern — O(log N) inserts and O(log N + M) range reads, plus native rank lookups (ZRANK) that a relational `ORDER BY` can't match at this QPS — replacing an expensive full-table sort with a data structure designed for leaderboards. This also solves cost, since Redis nodes for this workload are cheaper than an r5.4xlarge relational instance, and ElastiCache Serverless auto-scales for event-driven bursts without capacity planning. DynamoDB, fed asynchronously via Lambda/stream, serves as the durable system-of-record for auditing/history, decoupled from the hot read path so a cache flush doesn't lose data. This also improves availability, since the hot leaderboard-read path no longer contends with the write path on the same engine, and ElastiCache with automatic failover survives node failures.

---

### Exercise 11: Financial Transaction Processing Service — Account-Level Controls

**Starting architecture (ASCII diagram):**
```text
Partner banks (API integrations)
   |
   v
[API Gateway]
   |
   v
[Lambda - processes payment transaction]
   |
   v
[RDS PostgreSQL Multi-AZ - stores transaction records,
 encryption at rest: disabled ("can enable later")]
   |
   v
[CloudTrail: not enabled in this account]
   |
   v
[IAM: Lambda execution role has AdministratorAccess
 "to avoid permission errors during development"]
```
**Scenario context:** A fintech startup processes interbank payment transactions and is preparing for a SOC 2 Type II audit and PCI-DSS scoping review.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is almost entirely a security/compliance-pillar failure and would fail a SOC 2 or PCI-DSS review outright: encryption-at-rest disabled on a database holding financial transaction records is a direct compliance blocker; CloudTrail disabled means there's no audit trail of API activity across the account (a hard requirement for both SOC 2 and PCI-DSS); an `AdministratorAccess` Lambda execution role massively violates least-privilege — a single injection or dependency-confusion bug becomes full account compromise. Availability (Multi-AZ RDS) is actually fine here — resist the urge to "fix" what isn't the weak pillar.
- Improved architecture (ASCII diagram):
```text
Partner banks
   |
   v
[API Gateway - mTLS/API key + WAF]
   |
   v
[Lambda - execution role scoped to exactly the
 RDS/KMS/SQS actions it needs, resource-level ARNs]
   |
   v
[RDS PostgreSQL Multi-AZ - encryption at rest via
 KMS CMK, encryption in transit enforced (SSL required)]
   |
   v
[CloudTrail - enabled org-wide, multi-region,
 log file validation on, delivered to a dedicated
 log-archive account S3 bucket with Object Lock]
   |
   v
[AWS Config conformance packs (PCI-DSS/SOC2) +
 Security Hub PCI DSS standard - continuous
 compliance checks]
   |
   v
[GuardDuty - threat detection on the account]
```
- Reasoning: KMS-encrypted storage and enforced TLS in transit are baseline PCI-DSS/SOC2 requirements, not optional hardening — non-negotiable for a financial-transaction workload. Enabling org-wide, multi-region CloudTrail with log-file validation delivered to a separate, access-restricted log-archive account gives the immutable audit trail auditors require and protects logs from tampering even if the processing account is compromised. Replacing `AdministratorAccess` with a least-privilege, resource-scoped role limits blast radius to exactly the resources the function touches. AWS Config conformance packs plus Security Hub's PCI DSS standard give continuous, evidence-generating compliance monitoring rather than a point-in-time manual check — directly useful for a recurring Type II audit.

---

### Exercise 12: Financial Transaction Processing — Cardholder Data Handling

**Starting architecture (ASCII diagram):**
```text
Payment initiators --> ALB --> EC2 ASG (transaction service)
                                     |
                                     v
                              RDS PostgreSQL (Multi-AZ, encryption NOT enabled -- "we'll add it later")
                                     |
                                     v
                              Same EC2 instances write application logs (incl. full request/response
                              payloads with card numbers) to local disk, shipped to CloudWatch Logs
                                     |
                                     v
                              No CloudTrail; IAM users share one "finance-ops" access key
                              used by 12 engineers for troubleshooting
```
**Scenario context:** A fintech processes card-not-present payment transactions for e-commerce merchants and must maintain PCI DSS compliance.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a compliance/security-critical failure, not an availability gap (Multi-AZ RDS is already fine): (1) unencrypted RDS storage fails PCI DSS Requirement 3 outright; (2) logging full card numbers (PAN) to CloudWatch Logs is a severe PCI violation (cardholder data must never be logged in cleartext, and if logged at all must be tokenized/masked); (3) no CloudTrail means no audit trail for who accessed what — a hard PCI/SOC2 requirement; (4) a single shared IAM access key for 12 engineers destroys accountability/non-repudiation and massively increases blast radius if leaked.
- Improved architecture (ASCII diagram):
```text
Payment initiators --> ALB --> EC2 ASG (transaction service, PAN tokenized at ingress via
                                          AWS Payment Cryptography or a dedicated tokenization service)
                                     |
                                     v
                              RDS PostgreSQL (Multi-AZ, storage encryption with KMS CMK,
                                               TLS enforced in transit)
                                     |
                                     v
                              Structured logging with PAN masked/tokenized before write
                                     -> CloudWatch Logs (encrypted, restricted log group)
                                     |
                                     v
                              CloudTrail (org trail, log file validation, delivered to
                                          S3 with Object Lock for immutability)
                                     |
                                     v
                              IAM Identity Center: individual SSO roles per engineer,
                              scoped permission sets, session logging, no long-lived shared keys
```
- Reasoning: PCI DSS explicitly requires encryption at rest/in transit for cardholder data environments, masking of PAN in any logs/displays, comprehensive audit logging (CloudTrail with integrity validation), and individual accountability for access (no shared credentials). KMS CMKs plus tokenization address Requirements 3/4, CloudTrail with Object Lock addresses Requirement 10 (immutable audit trails), and IAM Identity Center per-engineer access addresses Requirements 7/8. None of this is about EC2/RDS failover — recognize when the weak pillar is compliance-driven security, not HA.

---

### Exercise 13: Centralized Log Analytics Platform — Hot-Tier Over-Provisioning

**Starting architecture (ASCII diagram):**
```text
200 microservices (multiple accounts)
   |  (application + access logs)
   v
[CloudWatch Logs - all log groups, retention: Never Expire]
   |
   v
[Kinesis Data Firehose]
   |
   v
[Amazon OpenSearch Service - single 10-node
 r6g.2xlarge cluster, hot storage only, no ISM
 (Index State Management) policies, holds 3 years
 of logs "just in case"]
```
**Scenario context:** A platform engineering team centralizes logs from 200 microservices for debugging and compliance retention, and the OpenSearch bill has grown to be one of the largest line items in the AWS invoice.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a cost-pillar failure: keeping 3 years of logs entirely in a "hot" OpenSearch cluster on r6g.2xlarge nodes is drastically over-provisioned for the actual access pattern (recent logs are queried constantly; logs older than roughly 30–90 days are rarely queried and mostly needed for retention/compliance, not fast search). CloudWatch Logs with "Never Expire" retention across every log group also silently accumulates storage cost indefinitely with no lifecycle policy. There's no tiering (no UltraWarm/cold storage, no ISM policies to roll indices to cheaper tiers or delete them), meaning premium hot-node pricing is paid for data that should be in S3.
- Improved architecture (ASCII diagram):
```text
200 microservices
   |
   v
[CloudWatch Logs - retention set per log-group
 tier (e.g., 30 days for debug logs, 1 year for
 audit-relevant logs)]
   |
   v
[Kinesis Data Firehose]
   |
   +--> [OpenSearch - hot tier: last 14-30 days,
   |     right-sized nodes + ISM policy auto-rolls
   |     to UltraWarm at 14 days, cold storage at 30]
   |
   v
[S3 (Standard -> Intelligent-Tiering/Glacier via
 lifecycle rule) - full raw log archive for
 compliance retention, queried via Athena when
 historical investigation is needed]
```
- Reasoning: Tiering logs by access recency (hot OpenSearch for the ~2–4 weeks that actually get interactively searched, then UltraWarm/cold tiers or S3+Athena for anything older) matches storage cost to actual query patterns instead of paying hot-node prices for years of cold data — the single biggest lever on an OpenSearch bill. Setting explicit CloudWatch Logs retention per log group (rather than "Never Expire" everywhere) stops silent indefinite accumulation. S3 lifecycle rules (Standard -> Intelligent-Tiering -> Glacier) satisfy long-term compliance retention at a fraction of the cost, with Athena providing on-demand queryability for the rare historical investigation.

---

### Exercise 14: Log Analytics Platform — Ingestion & Query Anti-Patterns

**Starting architecture (ASCII diagram):**
```text
200 application servers --> CloudWatch Logs agent --> CloudWatch Logs (all log groups, no retention set = never expire)
                                                              |
                                                              v
                                                    Lambda (runs every 5 min, scans ALL logs,
                                                             filters for ERROR strings, writes matches to S3 Standard)
                                                              |
                                                              v
                                                    Data analysts query S3 objects by downloading
                                                    and grepping locally (no Athena/OpenSearch)
```
**Scenario context:** An engineering org ingests logs from 200 servers for troubleshooting and compliance retention, with a small analytics team needing to search historical logs occasionally.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is squarely a cost and usability failure: CloudWatch Logs with no retention policy accumulates indefinitely at CloudWatch's per-GB storage price, which is far more expensive long-term than object storage — a classic "forgot to set retention" cost leak. Running a Lambda every 5 minutes that scans the entire log corpus (rather than just the incremental window since the last run) means processing cost grows superlinearly as log volume grows. Manually downloading S3 objects and grepping locally doesn't scale past a trivial data volume, has no indexing/search capability, and stores everything in S3 Standard forever with no lifecycle tiering.
- Improved architecture (ASCII diagram):
```text
200 app servers --> CloudWatch Logs (retention set: 14 days hot)
                          |
                          v (subscription filter, near-real-time)
                    Kinesis Data Firehose --> S3 (Parquet/compressed, partitioned by date/source)
                                                     |
                                                     v
                                          Lifecycle: Standard (30d) -> IA (90d) -> Glacier IR (1yr+)
                                                     |
                                                     v
                                          Glue Crawler --> Athena (ad hoc SQL) for analysts
                                          + OpenSearch Service (hot 7-day index) for real-time troubleshooting
```
- Reasoning: Short CloudWatch retention plus a subscription-filter-driven Firehose pipeline turns CloudWatch into a cheap short-term buffer while S3 (with lifecycle policies) becomes the cheap long-term compliance archive — this alone typically cuts logging storage cost by 70–90% at this scale. Athena-over-Parquet replaces "download and grep" with indexed, parallelized SQL that scales to terabytes. OpenSearch Service serves the fast, recent-window troubleshooting use case that Athena is comparatively slow at. This decouples "cheap long-term retention for compliance" from "fast recent-window search," which a single log store can't do well simultaneously.

---

### Exercise 15: Mobile App Backend — Global Latency & Synchronous Coupling (Social Fitness App)

**Starting architecture (ASCII diagram):**
```text
Mobile clients (iOS/Android, global user base)
   |  (REST API calls, no offline queuing on client)
   v
[API Gateway - single region: eu-west-1]
   |
   v
[Lambda - synchronous, calls push-notification
 provider inline during the same request]
   |
   v
[DynamoDB - single table, on-demand capacity]
   |
   v
[SNS - push notifications sent synchronously
 inside the API request/response cycle]
```
**Scenario context:** A social fitness app lets users log workouts and get real-time encouragement pushes from friends; the user base is split roughly evenly across North America, Europe, and Asia-Pacific.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a performance + global-latency-pillar failure: a single region (eu-west-1) means North American and APAC users incur significant round-trip latency on every API call, hurting the "real-time encouragement" experience specifically. Calling the push-notification provider (SNS) synchronously inside the request/response cycle couples API latency and reliability to a third-party dependency — if SNS or the push provider is slow, the user's "log workout" action itself hangs, an unnecessary coupling of a core action to a non-critical side-effect.
- Improved architecture (ASCII diagram):
```text
Mobile clients (global)
   |
   v
[API Gateway - regional endpoints in us-east-1,
 eu-west-1, ap-southeast-1, behind Route 53
 latency-based routing]
   |
   v
[Lambda - writes workout event, returns immediately]
   |
   v
[DynamoDB Global Tables - multi-region replication,
 on-demand capacity]
   |
   v
[EventBridge/SQS - decouples notification trigger]
   |
   v
[Lambda (async) -> SNS - push notification sent
 out-of-band, doesn't block the API response]
```
- Reasoning: Deploying regional API Gateway + Lambda stacks behind Route 53 latency-based routing, together with DynamoDB Global Tables for multi-region data, puts compute and data physically closer to each user cluster, directly addressing the global-latency requirement for NA/EU/APAC users. Decoupling the push notification into an async event (EventBridge/SQS -> Lambda -> SNS) means the core "log workout" write completes and returns to the client immediately regardless of push-provider latency or transient failures — improving perceived responsiveness and resilience, since a notification-provider outage no longer degrades the primary write path. DynamoDB Global Tables also give multi-region read/write availability, so a regional outage doesn't take down the whole user base, just requires failover/rerouting.

---

### Exercise 16: Mobile App Backend — Connection Pool Exhaustion

**Starting architecture (ASCII diagram):**
```text
Mobile app (iOS/Android, global users) --> API Gateway (regional endpoint, us-east-1 only)
                                                    |
                                                    v
                                             Lambda (business logic, no reserved/provisioned concurrency)
                                                    |
                                                    v
                                             RDS PostgreSQL (single AZ, db.t3.large,
                                                              max_connections=100, no RDS Proxy)
                                                    |
                                                    v
                                             Push notifications sent synchronously from the same
                                             Lambda via direct calls to APNs/FCM before returning response
```
**Scenario context:** A consumer mobile app has grown from a regional launch to a global user base of several million MAU, and users increasingly report timeouts during peak evening hours.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: Multiple compounding weaknesses: (1) single-AZ RDS is a real availability gap — any AZ impairment takes the whole backend down; (2) with no RDS Proxy, a Lambda concurrency burst (very plausible at global scale) exhausts the `max_connections=100` limit quickly since each concurrent Lambda execution can open its own DB connection — this is the most likely direct cause of the reported timeouts; (3) a single regional API Gateway endpoint in us-east-1 forces every global request to round-trip to one region, adding latency for distant users; (4) synchronous push-notification calls inside the request/response Lambda add latency and a third-party-dependency failure mode (APNs/FCM slowness) directly into the user-facing critical path.
- Improved architecture (ASCII diagram):
```text
Mobile app (global) --> API Gateway (regional endpoints + CloudFront, or
                         multi-region deployment + Route 53 latency-based routing)
                                    |
                                    v
                             Lambda (provisioned concurrency for baseline peak-hour load)
                                    |
                                    v
                             RDS Proxy --> Aurora PostgreSQL (Multi-AZ)
                                    |
                                    v
                             Lambda publishes to SNS/SQS --> separate async Lambda handles
                                                              APNs/FCM push delivery (decoupled, retried)
```
- Reasoning: RDS Proxy pools and multiplexes connections so Lambda concurrency spikes don't exhaust the database's connection limit — this directly fixes the peak-hour timeouts. Aurora Multi-AZ closes the availability gap. Provisioned concurrency removes cold-start latency during evening peak traffic. Decoupling push notifications via SNS/SQS removes a third-party dependency from the synchronous critical path, improving both perceived latency and resilience (a slow APNs won't fail the API response). Regional API Gateway deployments behind Route 53 latency-based routing (or CloudFront in front of a single regional API) address the global-latency ask.

---

### Exercise 17: Healthcare Patient Data Platform — Overly Broad Network Access

**Starting architecture (ASCII diagram):**
```text
Clinician web portal + patient mobile app
   |
   v
[ALB, single AZ]
   |
   v
[EC2 fleet - single AZ, runs app server]
   |
   v
[RDS PostgreSQL - single AZ, stores PHI
 (patient records, diagnoses, prescriptions),
 encryption at rest: enabled
 encryption in transit: not enforced (SSL optional)]
   |
   v
[S3 bucket - lab result PDFs, default encryption
 (SSE-S3), bucket policy allows access from
 entire VPC CIDR, no access logging enabled]
   |
   v
[IAM: clinicians and app service share one
 IAM role with broad S3 + RDS access]
```
**Scenario context:** A telehealth startup stores and serves protected health information (PHI) for patients and clinicians, and must comply with HIPAA as a condition of its BAAs with covered-entity hospital partners.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This mixes an availability gap with a more serious HIPAA-compliance/security gap. Single-AZ ALB and EC2 mean any AZ impairment takes down clinician/patient access to potentially urgent health data. More critically for compliance: encryption in transit is optional (SSL not enforced) on a database holding PHI — HIPAA's technical safeguards expect encryption of ePHI both at rest and in transit; S3 access logging is disabled, so there's no audit trail of who accessed lab results, required for HIPAA's audit-control safeguard; the bucket policy scoping access to "entire VPC CIDR" rather than specific roles is far too broad (any compromised instance in the VPC can read all patient lab results); and a shared IAM role between clinicians and the app service violates least-privilege and prevents attributing access to a specific user during an audit.
- Improved architecture (ASCII diagram):
```text
Clinician web portal + patient mobile app
   |
   v
[ALB, multi-AZ, HTTPS only, security policy TLS1.2+]
   |
   v
[EC2 ASG or ECS, multi-AZ]
   |
   v
[RDS PostgreSQL Multi-AZ, encryption at rest (KMS CMK),
 encryption in transit enforced (rds.force_ssl=1)]
   |
   v
[S3 - SSE-KMS (CMK), bucket policy scoped to specific
 IAM roles (not VPC CIDR), S3 access logging + CloudTrail
 data events enabled for object-level audit trail]
   |
   v
[IAM: distinct roles per function - app-service role
 (least privilege, resource-scoped), clinician access
 via federated SSO + role assumption, individually
 attributable and logged]
```
- Reasoning: Enforcing TLS on the RDS connection and using KMS CMKs for both RDS and S3 closes the "PHI unencrypted in transit" gap and gives customer-managed key control (useful for BAA key-management commitments and independent revoke/rotate ability). Enabling S3 access logging plus CloudTrail data events on the PHI bucket creates the object-level audit trail HIPAA's audit-control safeguard requires. Scoping the bucket policy to specific IAM roles instead of a VPC CIDR, and separating the app-service role from individually-attributable, SSO-federated clinician roles, gives least-privilege access and — critically for a HIPAA audit — the ability to prove exactly which identity accessed which PHI record. Multi-AZ across ALB/EC2/RDS closes the availability gap, which matters both for uptime and because HIPAA's contingency-plan safeguard expects resilient access to health data.

---

### Exercise 18: Healthcare Data Platform — Public Exposure

**Starting architecture (ASCII diagram):**
```text
Clinics (upload patient records, HL7/FHIR files) --> S3 bucket (public read ACL enabled for "easy sharing"
                                                                  with partner labs, unencrypted, versioning off)
                                                              |
                                                              v
                                                       EC2 (parses FHIR files, writes to RDS)
                                                              |
                                                              v
                                                       RDS PostgreSQL (contains PHI: patient names, DOB,
                                                                        diagnoses -- no encryption at rest,
                                                                        accessible from 0.0.0.0/0 on port 5432)
                                                              |
                                                              v
                                                       Analysts query RDS directly with a shared
                                                       read-only password posted in a team wiki page
```
**Scenario context:** A healthtech startup ingests clinical records from partner clinics to build a patient-outcomes analytics product, and must comply with HIPAA as a business associate.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This architecture has near-total security/compliance failure around Protected Health Information (PHI): (1) a public-read S3 bucket containing patient FHIR records is a reportable HIPAA breach waiting to happen — PHI must never be publicly accessible; (2) no encryption at rest on either S3 or RDS violates the HIPAA Security Rule's requirement for encryption of ePHI (or a documented equivalent safeguard); (3) RDS open to `0.0.0.0/0` on 5432 exposes PHI directly to the internet; (4) a shared password posted on a wiki eliminates any audit trail of who accessed which patient's data, required under HIPAA's access-control and audit-control requirements; (5) versioning off on the S3 bucket also risks accidental/malicious data loss with no recovery path.
- Improved architecture (ASCII diagram):
```text
Clinics --> S3 (private bucket, block-public-access ON, SSE-KMS with CMK, versioning + Object Lock)
                    |
                    v
             AWS PrivateLink / VPN for partner clinic uploads (no public internet path to the bucket where possible)
                    |
                    v
             Lambda/EC2 (private subnet) parses FHIR --> writes to RDS
                    |
                    v
             RDS PostgreSQL (private subnet, encryption at rest via KMS CMK, TLS enforced,
                              publicly accessible = false)
                    |
                    v
             IAM Identity Center: per-analyst roles, scoped least-privilege DB access via
             Secrets Manager-issued short-lived credentials, all access logged via CloudTrail
                    |
                    v
             Macie (continuously scans S3 for PHI/PII exposure) + AWS Config rules
             (auto-remediate any public-bucket or unencrypted-volume drift)
             + signed Business Associate Addendum (BAA) covering all AWS services used
```
- Reasoning: HIPAA's Security Rule mandates encryption of ePHI at rest/in transit, strict access controls with individual accountability, and audit logging of all PHI access — none of which the original design meets. Blocking public access plus SSE-KMS on S3 and moving RDS into a private subnet with encryption closes the two biggest breach vectors. Per-analyst Secrets Manager credentials plus CloudTrail give the audit trail HIPAA requires. Macie continuously catches PHI exposure drift (e.g., someone re-enabling public access later), and AWS Config can auto-remediate. Critically, only AWS services covered under the signed BAA may be used to process/store PHI — a governance step, not just a technical control.

---

### Exercise 19: Event-Driven Order Processing — Synchronous Call Chain

**Starting architecture (ASCII diagram):**
```text
Web/mobile clients
   |
   v
[API Gateway]
   |
   v
[Lambda - OrderService: validates order, calls Payment API synchronously,
 calls Inventory API synchronously, calls Shipping API synchronously,
 all inline before returning response]
   |
   v
[RDS MySQL - orders table]

(No queue, no DLQ, no idempotency key checking; client retries
 on timeout re-submit the same order)
```
**Scenario context:** An online retailer's checkout flow chains three downstream service calls synchronously inside one Lambda invocation, and duplicate orders have started appearing during periods of elevated latency.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: This is a reliability/architecture-pattern failure: synchronously chaining three downstream calls inside a single Lambda invocation means total latency is the sum of all three calls plus the DB write, and any one dependency being slow or down fails the entire checkout. Client-side retries on timeout with no idempotency key produce duplicate orders/duplicate charges — a classic distributed-systems failure, since a timeout doesn't mean the request actually failed downstream. No DLQ or queue means failed order steps are simply lost rather than retried safely. Tight coupling also means the Payment/Inventory/Shipping integrations can't be deployed, scaled, or fail independently of the checkout path.
- Improved architecture (ASCII diagram):
```text
Clients --> API Gateway --> Lambda (OrderService: validates, writes order
                                     with status=PENDING + idempotency-key
                                     to DynamoDB via a conditional put,
                                     publishes OrderCreated to EventBridge,
                                     returns 202 Accepted immediately)
                                          |
                    +---------------------+---------------------+
                    v                     v                     v
            SQS -> Payment Lambda   SQS -> Inventory Lambda  SQS -> Shipping Lambda
            (each with its own DLQ, retry policy, and an idempotent
             handler keyed on order id)
                    |
                    v
            Lambda (OrderStatus aggregator) updates the DynamoDB order
            record as each step completes; clients poll or subscribe
            (WebSocket API or push) for status updates
```
- Reasoning: A conditional put on the idempotency key before doing anything else means duplicate client retries are rejected at the door instead of creating duplicate orders. Returning 202 immediately and fanning out via EventBridge/SQS decouples the three downstream integrations so a slow Shipping API no longer blocks Payment or Inventory, and each consumer gets its own DLQ so a failure in one path doesn't take down the whole order flow or silently drop it. This is the standard "orchestrate via events, not a synchronous call chain" fix for checkout-style multi-service workflows, and it incidentally reduces cost too, since Lambda no longer pays for idle wall-clock time waiting on sequential downstream calls.

---

### Exercise 20: Disaster Recovery for a Line-of-Business Application

**Starting architecture (ASCII diagram):**
```text
[Single-region LOB app: ALB -> EC2 ASG -> RDS PostgreSQL Multi-AZ]
   |
   v
[RDS automated backups: 1-day retention, no snapshot copied
 cross-region]
   |
   v
[EC2 AMIs: none baked; instances configured manually via SSH
 after launch ("runbook in a shared Google Doc")]
   |
   v
No documented or tested failover procedure; no defined RTO/RPO
```
**Scenario context:** A company runs a business-critical internal LOB app that the team considers "Multi-AZ, so we're covered," but has never tested what happens if the entire region becomes unavailable, and a new compliance requirement now mandates a documented, tested DR plan with defined RTO/RPO.

**Your task:** Identify the weakness(es) in this architecture, then answer: (a) how to improve availability, (b) how to reduce cost, (c) how to improve security, (d) how to make it global/lower-latency if relevant.

**Model answer (reveal after attempting):**
- Weakness(es) identified: Multi-AZ RDS protects against AZ failure, not regional failure or logical/human-error data loss (e.g., an accidental `DROP TABLE`) — a common misconception that "Multi-AZ" equals "disaster recovery." One-day backup retention with no cross-region copy means a regional outage or a corruption/ransomware event has no recovery path outside the affected region. Manually-configured EC2 instances with no AMI/Infrastructure-as-Code mean rebuilding compute after a loss is slow, error-prone, and dependent on tribal knowledge in a shared doc. With no defined or tested RTO/RPO, the organization has no way to know whether its actual recovery capability meets the new compliance mandate, or even how long a real recovery would take.
- Improved architecture (ASCII diagram):
```text
Primary region: ALB -> EC2 ASG (launched from versioned, IaC-managed
                 AMI/launch template) -> RDS PostgreSQL Multi-AZ
                        |
                        v
        Automated backups (7-35 day retention) + cross-region
        automated snapshot copy to DR region
                        |
                        v
        AWS Backup (cross-region backup vault, backup plan with
        defined retention, restore jobs tested on a schedule)

DR region (warm standby, pilot light, or backup-restore
tier chosen per RTO/RPO target):
   - Cross-region read replica (promotable) or Aurora Global
     Database for near-zero RPO
   - CloudFormation/Terraform stacks kept ready to launch
     ASG+ALB from the same versioned AMI/template
   - Route 53 health-check-based failover routing policy

Game-day: scheduled failover drills, documented runbook
in version control, RTO/RPO formally measured and reported
```
- Reasoning: Cross-region snapshot copy (or Aurora Global Database for near-real-time replication) is what actually protects against a regional event or a corruption rollback, which Multi-AZ alone does not address — this is the single biggest correction to the "we're already covered" assumption. Baking AMIs or using launch templates through IaC, rather than manual SSH configuration, makes compute in the DR region reproducible in minutes instead of depending on a person and a doc. AWS Backup centralizes retention/cross-region copy policy and, critically, supports scheduled restore testing — a documented runbook that has never been executed isn't a tested DR plan. Route 53 health-check failover, combined with a deliberately chosen RTO/RPO target (warm-standby vs. pilot-light vs. backup-restore, rather than a default), gives the organization a measurable answer to "how long would recovery take," which is what the compliance mandate is really asking for.
