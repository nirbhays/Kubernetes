# Database Mastery — AWS SAA-C03 Exam Prep

## RDS Core Mechanics

**Multi-AZ vs Read Replicas — the #1 confused pair**
- Multi-AZ = synchronous standby in another AZ, same region, for **HA/DR only**. Standby is not readable (except the **Multi-AZ DB Cluster deployment** option — available for **MySQL and PostgreSQL only**, not SQL Server, MariaDB, or Oracle — which adds two readable standby instances and DOES allow read traffic on them. Note this is not literally "Aurora storage": it uses its own distributed, quorum-based replication architecture conceptually similar to Aurora's approach, but each instance keeps its own storage volume rather than sharing one common volume). Failover triggers automatically on instance failure, AZ failure, or maintenance; DNS endpoint stays the same, app doesn't need reconfiguration. Failover time: exam expects "minute or two," not zero.
- Read Replicas = asynchronous, for **read scaling**, can be cross-region, ARE readable, do NOT provide automatic failover (you must manually promote). A Read Replica can itself have Multi-AZ enabled for DR of the replica.
- **Trigger words:** "read-heavy workload, reduce load on primary" → Read Replica. "Minimize downtime during instance failure/patching" → Multi-AZ. "Disaster recovery in another region" → cross-region Read Replica (or Aurora Global Database if Aurora).
- **Distractor:** Multi-AZ does NOT improve read performance — standby is idle (single-standby model). Don't pick Multi-AZ for a "scale reads" question.

**Backups**
- Automated backups: daily snapshot + transaction logs → enables **Point-in-Time Recovery (PITR)** to any second within the retention window (1–35 days). Stored in S3, free up to the size of the DB.
- Manual snapshots: retained until explicitly deleted, can be shared cross-account, copied cross-region.
- Restoring a snapshot (automated or manual) always creates a **new RDS instance** with a new endpoint — exam loves testing this ("how do you fix a corrupted DB" → restore to new instance, then repoint app / swap CNAME).
- Encrypting an unencrypted RDS instance: cannot enable encryption in-place. Snapshot → copy snapshot with encryption enabled → restore from encrypted snapshot. Same pattern applies for Aurora.

**Encryption**
- At-rest via KMS, enabled at creation time only (see above workaround for existing unencrypted DBs).
- Read Replicas of encrypted instances must be encrypted with same key (or via KMS multi-region keys for cross-region).
- In-transit via SSL/TLS enforced through parameter group (`rds.force_ssl`).

**Scaling**
- Vertical: change instance class (brief downtime unless Multi-AZ, where failover masks it).
- Storage: RDS Storage Autoscaling — grows automatically when free storage drops below threshold; no downtime, one-way (can't shrink).
- Horizontal read scaling: Read Replicas (up to several per source, chainable for MySQL/MariaDB).
- **Exam boundary:** RDS scales reads via replicas; it does NOT scale writes horizontally — that's an Aurora/DynamoDB differentiator. If question demands "horizontally scalable writes," RDS is wrong regardless of engine.

**IAM Database Authentication**
- Generates short-lived (15-min) auth tokens via IAM instead of storing DB passwords. Supported: MySQL, PostgreSQL (and Aurora equivalents). Good fit whenever question mentions "avoid hardcoded credentials," "centralize access control with IAM," or "rotate credentials automatically" without wanting the overhead of Secrets Manager rotation Lambdas. Does not scale to high-throughput connection churn (auth overhead) — that's a legitimate limiter callout, but no exam-relevant numeric limit to cite.
- Distractor vs **Secrets Manager**: Secrets Manager handles automatic password rotation for the master/app credentials and is engine-agnostic including on-prem; IAM auth removes passwords entirely for supported engines. If the scenario says "rotate secrets automatically without app changes" → Secrets Manager. If it says "use IAM roles/policies to control who connects" → IAM DB auth.

**RDS Proxy**
- Connection pooling/multiplexing layer sitting in front of RDS/Aurora. Solves: Lambda-triggered connection storms exhausting DB max_connections, and long failover times as seen by the app.
- Reduces failover time app perceives (proxy holds connections, retries transparently) — pick RDS Proxy when question mentions **Lambda + RDS** and "too many connections" or "connection exhaustion." Also improves failover behavior without app-side retry logic.
- Requires Secrets Manager for credential storage (another cross-link the exam tests).
- Does NOT reduce query latency or provide caching — that's ElastiCache/DAX territory; don't confuse it as a performance cache.

---

## Aurora

**Storage & Availability architecture**
- Storage layer is distributed 6-way across 3 AZs automatically, self-healing, decoupled from compute. This is why Aurora failover is much faster than standard RDS Multi-AZ (typically sub-minute) — cite this qualitatively as "significantly faster than RDS Multi-AZ," not a specific SLA number.
- One writer instance + up to 15 Aurora Replicas, all sharing the same underlying storage volume (no replication lag for storage, only for the in-memory buffer state) — this is why Aurora Replica lag is typically much lower than RDS async Read Replica lag.

**Replicas & Failover**
- Aurora Replicas can serve reads AND are automatic failover targets (priority tiers 0–15 configurable) — unlike RDS Read Replicas which require manual promotion. This is a key "why choose Aurora over RDS" argument on resilience-domain questions.
- **Aurora Global Database**: one primary region (read/write) plus multiple secondary read-only regions, storage-based replication (typically sub-second, described qualitatively as "typically under a second"), used for cross-region DR with low RPO and low RTO, and for global low-latency reads. Managed planned failover can promote a secondary region in about a minute (again — qualitative, "on the order of a minute," don't over-cite). This is the answer whenever the scenario says "global read latency" + "cross-region DR" + Aurora already in play — beats cross-region Read Replicas or manual replication.
- **Trigger words:** "near-zero RPO/RTO across regions," "global application, single writer" → Aurora Global Database. "Occasional cross-region reporting only, cost-sensitive" → cross-region Read Replica may suffice as distractor-correct answer if Global DB is overkill/not mentioned as available (rare, but budget-domain questions test this).

**Aurora Serverless v2**
- Auto-scales capacity (in fine-grained ACUs) up/down instantly based on load. AWS has extended Serverless v2 to also support scaling capacity down to 0 ACUs (auto-pause) for idle databases, so "scale-to-zero" is no longer a clean v1-only discriminator the way older material frames it — treat that distinction with caution on current exam content. The durable differentiator to lean on instead: v2 gives fine-grained, near-instant, per-second capacity adjustments and integrates with standard Aurora capabilities (Read Replicas, Global Database, mixed reader fleets, etc.), whereas Serverless v1 is the older, more limited model with coarser scaling steps and fewer feature integrations.
- Fits: "unpredictable/spiky workloads," "avoid over-provisioning," "multi-tenant SaaS with variable per-tenant load," "dev/test environments with intermittent usage."
- Coexists with provisioned Aurora instances in the same cluster (mixed reader fleet) — a nuance sometimes tested for "mix serverless readers with provisioned writer."

**Backups**
- Continuous backup to S3, PITR same as RDS, backtrack feature (MySQL-compatible Aurora) lets you rewind the DB in place without restoring a new instance — differentiator vs RDS where restore always creates a new instance.

**Scaling**
- Read scaling: Aurora Replicas (up to 15) with an Aurora Reader endpoint that load-balances automatically — mention "Reader endpoint" when a question wants automatic read load balancing across replicas (vs RDS where you manage replica endpoints individually).
- Write scaling: still single-writer per cluster in standard Aurora (multi-master exists historically but is not the exam's expected answer); **Aurora Limitless Database** (newer distributed sharding capability) is the answer if a question explicitly demands horizontally scalable writes within Aurora — know it exists conceptually but don't over-index on it unless the question is unmistakably about write sharding.

---

## DynamoDB

**Partition key design**
- Choose a partition key with high cardinality and even access distribution to avoid "hot partitions" — exam trigger phrase: "uneven traffic to certain items," "throttling on specific keys" → fix is redesign partition key (e.g., add high-cardinality suffix/prefix, write-sharding), not just "increase capacity."
- Composite key (partition + sort key) enables one-to-many item collections queried efficiently via `Query` (vs `Scan`, which is the anti-pattern answer whenever the question implies full-table reads — always the wrong choice for "efficient lookup" questions).

**Capacity modes**
- **On-Demand**: pay-per-request, auto-scales instantly, ideal for unknown/unpredictable/spiky traffic or new workloads — trigger words: "unpredictable traffic," "don't want to manage capacity," "spiky."
- **Provisioned** (with optional Auto Scaling on top): cheaper at steady, predictable, high-utilization workloads — trigger words: "consistent/predictable traffic," "cost optimization for steady workload." Cost-domain questions often want Provisioned + Auto Scaling as the "cheaper than on-demand at scale" answer.

**Global Tables**
- Multi-region, multi-active (multi-master) replication, last-writer-wins conflict resolution, near real-time propagation (qualitative). This is the DynamoDB analog of Aurora Global Database for resilience-domain "multi-region active-active" questions. Distractor: it is NOT read-only in secondary regions like Aurora Global DB — Global Tables allow writes in every region, which is a key differentiator to call out explicitly when a question asks about "active-active writes across regions."

**DynamoDB Streams**
- Time-ordered change log (item-level create/update/delete) feeding Lambda triggers or Kinesis — trigger words: "react to data changes in near real time," "event-driven architecture off table changes," "replicate changes to another system/table." Common pairing: Streams + Lambda for cross-region replication before Global Tables existed, or for building audit logs/derived views.

**DAX (DynamoDB Accelerator)**
- In-memory cache **specifically for DynamoDB**, API-compatible (drop-in, minimal code change), microsecond read latency, write-through cache. Choose DAX over ElastiCache whenever the workload is specifically DynamoDB read-heavy and the question emphasizes "minimal application changes" or "microsecond latency for DynamoDB reads." ElastiCache is the general-purpose answer when caching spans multiple data sources or isn't DynamoDB-specific, or when you need pub/sub, complex data structures, or cross-service caching (e.g., caching RDS query results).

**TTL**
- Automatic item expiry/deletion (no extra RCU/WCU cost for the delete) — trigger: "automatically expire old data," "reduce storage costs for stale items," "clean up session data" without a manual cleanup job/Lambda cron.

**Transactions**
- `TransactWriteItems`/`TransactGetItems` give ACID across multiple items/tables in one request — trigger: "all-or-nothing update across multiple items," "financial consistency," "avoid partial writes." Costs 2x the write/read capacity of a normal request — occasionally relevant to cost-domain questions ("why did DynamoDB costs double after adding transactions").

**Encryption**
- Encryption at rest is enabled by default (AWS-owned key baseline), can upgrade to AWS-managed or customer-managed KMS key for auditability/control — pick CMK when question demands "control over key rotation/access policy" or cross-account key sharing scenarios.

**Consistency models**
- Eventually consistent reads (default, cheaper, half the RCU cost) vs strongly consistent reads (`ConsistentRead=true`, more expensive, not available in Global Tables cross-region or on Global Secondary Indexes). Trigger: "must read your own writes immediately" → strongly consistent (same-region only). "Cost-optimized reads, slight staleness acceptable" → eventually consistent (default).

**Backups / PITR**
- On-demand backups: full table backup, no performance impact, retained until deleted, doesn't consume throughput.
- PITR: continuous backups enabling restore to any second in the last 35 days (same window concept as RDS) — restoring always creates a **new table**, same "restore = new resource" pattern as RDS/Aurora.

---

## ElastiCache

**Redis vs Memcached — the classic decision matrix**
| Need | Choice |
|---|---|
| Multi-AZ with automatic failover | Redis (Cluster Mode or replication group) |
| Data persistence / durability (snapshots, AOF) | Redis |
| Complex data structures (sorted sets, lists, hashes, pub/sub, geospatial) | Redis |
| Simple key-value cache, need multi-threaded performance for many small objects | Memcached |
| Need to horizontally shard/scale out cache with simplicity, no HA requirement | Memcached |
| Need backup/restore of cache state | Redis only |
| Need transactions/atomic ops beyond simple increments | Redis |

- **Trigger words:** "session store requiring persistence/failover" → Redis. "Simple, horizontally scalable, multi-node cache for ephemeral data, no replication needed" → Memcached. If the question mentions *any* of: pub/sub, replication, snapshots, sorted sets, geospatial, leaderboard → answer is Redis, full stop.

**Caching patterns (exam loves naming these)**
- **Lazy loading (cache-aside)**: app checks cache, on miss reads DB and populates cache. Pro: only requested data cached, resilient to cache node failure. Con: cache miss penalty (extra round trip), potential stale data.
- **Write-through**: every DB write also updates cache. Pro: cache always fresh. Con: write latency increase, wasted cache space for rarely-read data, cache can go cold on node replacement without population.
- **TTL** is the standard mitigation the exam wants for stale-data concerns in write-through/lazy-loading answer choices.
- **Session storage / stateless app tier**: ElastiCache (Redis, for durability/failover) is the standard answer whenever a question wants to remove session affinity/sticky sessions from an Auto Scaling Group behind an ALB — trigger phrase "decouple session state from EC2 instances."
- **Database offload for read-heavy relational workloads**: ElastiCache in front of RDS is the answer for "reduce read load on RDS without adding read replicas" or "sub-millisecond latency for frequently accessed relational query results" (DAX is DynamoDB-only, so RDS/Aurora caching scenarios always point to ElastiCache).

---

## Redshift — where SAA-C03 actually needs it

SAA-C03 tests Redshift at a **decision-boundary level only** — you need to recognize when it's the right category of tool, not tune WLM queues or distribution styles.

**Redshift vs RDS vs Athena**
- **RDS/Aurora**: OLTP — transactional, row-based, low-latency single-record reads/writes, normalized schemas, application backend.
- **Redshift**: OLAP data warehouse — columnar storage, MPP (massively parallel processing), built for complex analytical queries/aggregations across large historical datasets (BI dashboards, large-scale joins, terabyte-to-petabyte scale). Trigger words: "data warehouse," "business intelligence," "complex analytical queries across historical data," "columnar," "star schema," "BI tool integration (QuickSight)."
- **Athena**: serverless, ad-hoc SQL queries directly against data **in S3**, pay-per-query-scanned, zero infrastructure to manage. Trigger words: "ad-hoc/infrequent queries," "no need to provision a cluster/infrastructure," "query data already sitting in S3/data lake," "pay only for what you scan," "server-less analytics."
- **Decision rule:** frequent/complex/sustained analytical workload with dedicated compute justified → Redshift. Infrequent/exploratory querying of S3 data lake without wanting to manage or pay for standing infrastructure → Athena. Transactional app backend → RDS/Aurora, never Redshift or Athena.

**Redshift-specific exam nuggets**
- **Redshift Spectrum**: query data directly in S3 from within Redshift without loading it — bridges warehouse + data lake; trigger: "query S3 data alongside data already in Redshift without an ETL load step."
- Scaling: Concurrency Scaling (handles spikes in concurrent queries) and Elastic Resize (add/remove nodes) — if a question mentions "sporadic spikes in concurrent BI users" for an existing Redshift cluster, that's Concurrency Scaling, not a bigger instance type.
- **Cost-domain angle**: Reserved nodes for steady-state warehouse cost savings (same RI pattern as EC2/RDS); Redshift Serverless exists for intermittent analytics workloads without cluster management — pick it over provisioned Redshift when the question wants "pay only when queries run" for a data warehouse (vs Athena, which is for *querying S3 directly*, not maintaining a warehouse schema/performance profile).
- **Distractor to watch:** don't pick Redshift for "occasional log analysis in S3" — that's over-provisioning; Athena (or Athena + Glue for cataloging) is the lean, exam-preferred answer.
