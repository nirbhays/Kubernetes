# SAA-C03 Practice Questions — Domain 3: Design High-Performing Architectures

Focus: S3 performance (Transfer Acceleration, multipart upload, request-rate scaling), EBS volume type selection, EFS performance/throughput modes, RDS/Aurora read scaling + RDS Proxy, DynamoDB DAX, ElastiCache Redis vs Memcached.

Original practice content written for study purposes — these are **not** real AWS exam questions and do not reproduce any leaked/dumped exam material. Content reflects AWS service behavior as understood as of 2026 and the official SAA-C03 exam guide scope.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A media analytics company allows customers to upload raw video files ranging from 2 GB to 40 GB directly into an S3 bucket from their office network. Several customers report that uploads of the larger files frequently fail partway through, forcing a full restart from byte zero, which wastes hours of upload time on an unreliable ISP connection. The company wants uploads to resume from the point of failure and would also like faster throughput by sending pieces of a file in parallel.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket and have customers upload through the acceleration endpoint.
B. Use the S3 multipart upload API to split each file into parts, upload parts in parallel, and retry only the failed parts.
C. Increase the customers' client-side HTTP request timeout setting so a single PutObject call has more time to complete.
D. Enable S3 Cross-Region Replication so a partially uploaded object is retried automatically in a second region.
**Correct answer(s):** B
**Why correct:** Multipart upload splits an object into independently uploaded parts, each of which can be retried on its own if it fails, and parts can be sent in parallel to improve throughput — directly addressing both stated pain points (resumability and parallel speed) for large objects.
**Why each wrong option is wrong:** A speeds up transfer over long network distances via edge locations but does nothing to make a single large PutObject resumable after a failure; C only delays the inevitable failure of a single monolithic request and does nothing for parallelism or partial resume; D replicates already-stored objects to another region and has no effect on how an object is uploaded or on upload reliability.
**Trigger words:** "uploads... frequently fail partway through," "resume from the point of failure," "sending pieces of a file in parallel."
**Underlying architectural principle:** Large object uploads should be split into independently retriable, parallelizable parts via multipart upload rather than relying on a single large atomic request.

---

### Question 2 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A global logistics company has field offices in Nairobi, Manila, and Buenos Aires that each generate large (5-15 GB) sensor-log bundles daily and upload them to a single S3 bucket in us-east-1. Offices in these regions consistently report upload times 4-6x slower than a comparable office in Virginia, even though their local internet connections are otherwise fast and uncongested. The company does not want to create regional buckets or manage any replication, and needs a change that requires no modification to the existing upload application logic beyond pointing it at a different endpoint.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket and have the offices upload via the acceleration endpoint.
B. Create a CloudFront distribution in front of the bucket and configure it to cache PUT and POST requests.
C. Set up S3 Cross-Region Replication to buckets closer to each office and have each office upload locally.
D. Switch the bucket's storage class to S3 Intelligent-Tiering so uploads are automatically optimized for access frequency.
**Correct answer(s):** A
**Why correct:** Transfer Acceleration routes uploads through the nearest CloudFront edge location and over the optimized AWS backbone network to the bucket's region, which directly reduces the long-haul latency and packet-loss penalty that geographically distant uploaders experience, with only an endpoint change required.
**Why each wrong option is wrong:** B is incorrect because CloudFront caches and accelerates content reads/distribution, not object writes — it does not meaningfully accelerate PUT/POST upload traffic to an origin; C solves the problem but requires standing up and managing additional buckets and replication/routing logic, which the scenario explicitly rules out; D changes cost/storage-tiering behavior for stored objects and has no effect on upload transfer speed.
**Trigger words:** "field offices... geographically distant," "upload times 4-6x slower," "no modification to the existing upload application logic beyond pointing it at a different endpoint."
**Underlying architectural principle:** S3 Transfer Acceleration solves long-distance upload/download latency by using CloudFront's edge network and AWS's backbone, whereas CloudFront itself is a read/distribution caching layer, not an upload accelerator.

---

### Question 3 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A stock-market data vendor writes tick data into an S3 bucket using object keys of the form `2026-08-15/13-45-00-123.json`, sorted by timestamp. During the first 90 seconds of each trading day's opening bell, write throughput spikes almost instantly from near zero to over 12,000 PUT requests per second, and the application begins receiving intermittent `503 SlowDown` responses during that spike, even though S3's published per-prefix request limits are well above the vendor's average sustained rate. Traffic settles into a sustainable pattern within about two minutes. The vendor wants to eliminate the throttling during the opening-bell spike without introducing a queue or any additional infrastructure to buffer requests.
**Options:**
A. Prepend a high-cardinality hash (e.g., a few random hex characters) to each object key so that writes are spread across many partitions from the very first request.
B. Request an S3 service-quota increase for PutObject requests per second through AWS Support.
C. Enable S3 Transfer Acceleration on the bucket to increase the effective request rate the bucket can absorb.
D. Switch the bucket's storage class to S3 One Zone-IA, which supports a higher baseline request rate than S3 Standard.
**Correct answer(s):** A
**Why correct:** S3 automatically scales request capacity per prefix over time, but that scaling ramps up gradually rather than instantaneously; a sequential timestamp-based key concentrates all writes onto what is effectively a single prefix at the moment of a sudden spike, so distributing keys across many prefixes from the first request (via a random/hashed prefix) immediately parallelizes writes across many partitions instead of waiting for gradual scaling to catch up.
**Why each wrong option is wrong:** B is not applicable because S3 request-rate performance is not gated by a per-account raise-able service quota in the way EC2/Lambda limits are — the bottleneck here is partition scaling behavior tied to key naming, not an account ceiling; C accelerates long-distance transfer speed over the network path, not the rate at which a bucket's internal partitions can absorb sudden concentrated write bursts; D is incorrect because storage class does not change S3's request-rate/partitioning behavior — One Zone-IA has no distinct baseline request-rate advantage over Standard.
**Trigger words:** "sorted by timestamp," "spikes almost instantly," "503 SlowDown," "well above the vendor's average sustained rate," "without introducing a queue."
**Underlying architectural principle:** S3 scales request rate per prefix automatically but progressively, so workloads with sudden, extreme write bursts on sequentially-patterned keys benefit from deliberately randomizing key prefixes to spread load across partitions immediately rather than relying on S3 to catch up.

---

### Question 4 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A mid-sized SaaS company is migrating a PostgreSQL database from on-premises to an EC2-hosted instance. The database needs consistently good, predictable IOPS and throughput for typical OLTP traffic, but the workload is not described as latency-sensitive to sub-millisecond levels, and the team is cost-conscious and wants to provision IOPS and throughput independently of how large the volume is.
**Options:**
A. Amazon EBS gp3 volume, with IOPS and throughput provisioned to match the workload's needs.
B. Amazon EBS io2 Block Express volume, provisioned at its maximum IOPS tier.
C. Amazon EBS gp2 volume, sized larger than needed so its IOPS baseline scales up accordingly.
D. Amazon EBS st1 (Throughput Optimized HDD) volume for consistent throughput at low cost.
**Correct answer(s):** A
**Why correct:** gp3 provides a solid baseline of 3,000 IOPS and 125 MiB/s throughput independent of volume size, and lets you provision additional IOPS/throughput separately at a lower cost than the equivalent gp2 or io-family performance, matching the description of predictable-but-not-extreme performance needs with cost sensitivity.
**Why each wrong option is wrong:** B is over-provisioned and needlessly expensive for a workload with no stated sub-millisecond-latency or mission-critical extreme-IOPS requirement; C ties IOPS to volume size (3 IOPS/GB) and requires oversizing the volume purely to buy performance, which is both wasteful and still burst-credit-dependent rather than a guaranteed baseline; D is a throughput-optimized HDD meant for large sequential I/O like big-data/log workloads and cannot even serve as a boot/database volume needing random-access OLTP performance.
**Trigger words:** "consistently good, predictable IOPS," "not... sub-millisecond," "cost-conscious," "provision IOPS and throughput independently of... size."
**Underlying architectural principle:** gp3 is the default modern choice for general-purpose workloads needing predictable, independently-tunable performance at low cost, reserving io2/io2 Block Express for explicit extreme-IOPS or sub-millisecond-latency requirements.

---

### Question 5 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An engineering team migrated a data-processing application from a modern EC2 instance type to an older-generation instance type to save cost, keeping the exact same gp3 EBS volume with the same provisioned IOPS and throughput settings. After the migration, the team observes that disk read/write throughput is capped well below the volume's provisioned throughput, even though CloudWatch shows the instance's network throughput and CPU are not saturated. No changes were made to the application code or the EBS volume configuration.
**Options:**
A. Confirm the instance type is EBS-optimized (or has sufficient dedicated EBS bandwidth) and, if not, move to a current-generation instance type that provides adequate dedicated EBS throughput.
B. Increase the gp3 volume's provisioned IOPS further, since the bottleneck must be insufficient IOPS on the volume itself.
C. Convert the gp3 volume to gp2 so its performance scales automatically with its size.
D. Enable EBS Multi-Attach on the volume to distribute I/O across multiple network paths.
**Correct answer(s):** A
**Why correct:** EBS-optimized instances provide dedicated bandwidth between the instance and EBS, separate from general network traffic; older-generation or smaller instance types can have insufficient dedicated EBS bandwidth to sustain a volume's full provisioned throughput even when the volume itself is correctly configured and CPU/network aren't the bottleneck, so the fix is ensuring adequate EBS-optimized bandwidth on the instance side.
**Why each wrong option is wrong:** B assumes the volume's provisioned IOPS is the bottleneck, but the scenario states the same provisioned settings worked before the instance change, pointing to the instance's EBS bandwidth ceiling instead; C moves to a volume type whose performance is tied to size and burst credits, which does not address an instance-side bandwidth limitation and is a downgrade in guaranteed performance; D is for attaching one volume to multiple instances concurrently for cluster-aware filesystems and has no effect on a single instance's dedicated bandwidth to a single attached volume.
**Trigger words:** "migrated... to an older-generation instance type," "throughput is capped... even though... network throughput and CPU are not saturated," "no changes... to the... EBS volume configuration."
**Underlying architectural principle:** EBS performance is bounded by both the volume's provisioned capability and the instance's dedicated EBS bandwidth, so a throughput ceiling with a correctly-configured, unsaturated volume points to insufficient EBS-optimized bandwidth on the compute side.

---

### Question 6 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A financial risk-modeling firm runs a single EC2 instance that needs to sustain roughly 400,000 IOPS and 6 GB/s of throughput against its working dataset for overnight batch simulations, a level that exceeds the documented per-volume maximum for even the highest-performance single EBS volume type available. The workload requires block-storage semantics (not a shared file system), must run on a single instance, and the firm wants to stay within standard EBS offerings rather than adopting a different storage service.
**Options:**
A. Provision a single io2 Block Express volume and request a soft-limit increase from AWS Support to exceed its published per-volume maximum.
B. Stripe multiple io2 Block Express volumes together using RAID 0 at the OS level to aggregate their IOPS and throughput.
C. Attach the io2 Block Express volume to multiple instances simultaneously using EBS Multi-Attach to parallelize I/O across instances.
D. Migrate the workload to Amazon EFS with Max I/O performance mode, which scales throughput across many parallel clients.
**Correct answer(s):** B
**Why correct:** When a workload's required IOPS/throughput exceeds what even the highest-performing single EBS volume can deliver, the standard AWS pattern is to stripe multiple volumes together with RAID 0 at the OS level, aggregating their individual IOPS and throughput ceilings into a combined pool available to the single instance.
**Why each wrong option is wrong:** A is invalid because per-volume IOPS/throughput maximums for io2 Block Express are hard architectural limits, not adjustable soft limits that AWS Support can raise; C parallelizes attachment to multiple instances for cluster-aware filesystems, it does not increase the throughput ceiling delivered to any single instance and isn't intended to aggregate performance for one host; D changes both the storage paradigm (shared file system vs block) and is optimized for many concurrent clients rather than maximizing single-instance block I/O, which doesn't fit the stated single-instance block-storage requirement.
**Trigger words:** "exceeds the documented per-volume maximum," "block-storage semantics... single instance," "stay within standard EBS offerings."
**Underlying architectural principle:** When a single EBS volume's maximum IOPS or throughput is insufficient, RAID 0 striping across multiple volumes at the OS level is the standard way to exceed a single volume's performance ceiling for one instance.

---

### Question 7 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media-processing company runs a fleet of EC2 instances that mount a shared EFS file system for a video-transcoding pipeline. Traffic is highly unpredictable: some days see near-zero jobs, while breaking-news days can spike file-system throughput demand by 20x within minutes. The team does not want to forecast or manually configure a fixed throughput value ahead of time, wants to avoid overpaying during idle periods, and wants throughput to scale automatically without any capacity planning exercise.
**Options:**
A. Configure the file system to use Provisioned Throughput mode, sized generously to cover the highest expected spike.
B. Configure the file system to use Elastic Throughput mode, which scales throughput up and down automatically with the workload.
C. Configure the file system to use Bursting Throughput mode, relying on burst credits accumulated during idle periods.
D. Configure the file system to use Max I/O performance mode, since it provides the highest aggregate throughput ceiling.
**Correct answer(s):** B
**Why correct:** Elastic Throughput mode automatically scales a file system's throughput up and down to match the current workload in near-real time with no capacity planning or fixed provisioning, and bills based on actual usage — precisely matching the requirement for unpredictable, spiky traffic with no manual forecasting and no overpaying during idle periods.
**Why each wrong option is wrong:** A requires provisioning a fixed throughput value up front sized for the worst case, which both requires capacity planning the team wants to avoid and results in overpaying during idle periods; C ties available throughput to a burst-credit balance accumulated based on storage size and recent usage, which can be exhausted precisely during a sudden large spike after idle periods, unlike Elastic's real-time auto-scaling; D is a performance mode governing latency/parallelism characteristics, not a throughput-scaling mechanism, and does not by itself solve unpredictable throughput demand.
**Trigger words:** "highly unpredictable," "spike... by 20x within minutes," "avoid overpaying during idle periods," "without any capacity planning exercise."
**Underlying architectural principle:** EFS Elastic Throughput mode is the modern, management-free answer for unpredictable or highly variable workloads, replacing manual throughput provisioning or burst-credit dependency.

---

### Question 8 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A genomics research lab runs a data pipeline where 800 EC2 instances in an Auto Scaling group simultaneously mount the same EFS file system and each read and write many small files in parallel as part of a highly parallelized batch analysis job. The lab has profiled the workload and found that aggregate throughput across all 800 clients — not the latency of any single client's individual operation — is the limiting factor in total job completion time. A prior attempt using the default file-system configuration showed throughput plateauing well before the fleet's combined demand was met.
**Options:**
A. Switch the file system's performance mode from General Purpose to Max I/O.
B. Switch the file system's throughput mode from Bursting to Provisioned, provisioned at a very high fixed value.
C. Reduce the size of the Auto Scaling group so fewer clients compete for the same aggregate throughput.
D. Migrate from EFS to a single large gp3 EBS volume shared across all 800 instances via Multi-Attach.
**Correct answer(s):** A
**Why correct:** Max I/O performance mode is purpose-built to scale to higher levels of aggregate throughput and IOPS across a very large number of concurrent clients, at the cost of slightly higher per-operation latency — exactly the tradeoff described, where aggregate fleet-wide throughput (not single-client latency) is the bottleneck.
**Why each wrong option is wrong:** B addresses throughput mode (bandwidth budget) but doesn't touch the performance mode dimension of scaling metadata operations and aggregate IOPS across massively parallel clients, so throughput can still plateau due to the performance-mode ceiling of General Purpose; C reduces the workload's parallelism to work around the platform's limits rather than fixing the underlying scaling ceiling, directly hurting the stated goal of a highly parallelized job; D is invalid on multiple counts — EBS Multi-Attach is only supported for io1 and io2 volumes, not gp3, so a "gp3 volume... via Multi-Attach" is not even a valid configuration; even with a supported volume type, Multi-Attach is capped at 16 Nitro-based instances within a single Availability Zone (nowhere near 800), and it still requires a cluster-aware file system to coordinate concurrent writes rather than the general-purpose concurrent read/write access EFS provides natively.
**Trigger words:** "800 EC2 instances... simultaneously mount," "aggregate throughput... not the latency of any single client," "throughput plateauing... before the fleet's combined demand was met."
**Underlying architectural principle:** EFS Max I/O performance mode should be chosen specifically when many concurrent clients need scaled-up aggregate throughput/IOPS and can tolerate marginally higher per-operation latency, distinguishing it from General Purpose mode's low single-operation latency optimization.

---

### Question 9 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A retail company runs its order-processing system on a single Amazon RDS for MySQL instance with Multi-AZ enabled for high availability. The business intelligence team now wants to run heavy, long-running analytical queries against the same data for daily reporting, but these queries are starting to noticeably slow down the production order-processing workload on the primary instance. The company wants to isolate the reporting workload's load from the primary without re-architecting into a separate data warehouse, and with minimal application changes.
**Options:**
A. Create one or more RDS Read Replicas from the primary instance and point the BI reporting tool at a replica's endpoint.
B. Point the BI reporting tool at the Multi-AZ standby instance's endpoint instead of the primary.
C. Increase the Multi-AZ primary instance's class to a larger size so it can absorb both workloads.
D. Enable RDS Storage Auto Scaling on the primary instance so it can handle the additional query load.
**Correct answer(s):** A
**Why correct:** RDS Read Replicas are purpose-built for offloading read-heavy workloads like reporting from the primary instance, providing their own distinct endpoint that the BI tool can be pointed at with no changes to the production application, directly isolating the reporting load.
**Why each wrong option is wrong:** B is invalid because the Multi-AZ standby is not readable — it exists purely as a synchronous failover target and cannot serve query traffic; C only pushes the primary instance's capacity ceiling higher without isolating the two workloads, so BI queries would still directly contend with production traffic on the same instance; D scales storage capacity (disk space) automatically, which has nothing to do with compute/query contention between reporting and production workloads.
**Trigger words:** "heavy, long-running analytical queries," "slow down the production... workload," "isolate the reporting workload's load," "minimal application changes."
**Underlying architectural principle:** RDS Read Replicas, not the Multi-AZ standby, are the mechanism for offloading and isolating read-heavy secondary workloads from a primary database instance.

---

### Question 10 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company built a serverless order-confirmation workflow where an AWS Lambda function is invoked on every checkout event and opens a new connection to an Amazon RDS for PostgreSQL instance to write the order record. During flash-sale traffic bursts, thousands of concurrent Lambda invocations open thousands of simultaneous database connections, and the database begins rejecting connections with "too many connections" errors, causing failed checkouts. The company wants to fix this without redesigning the checkout flow away from Lambda-per-request and without manually implementing custom connection-pooling logic inside the function.
**Options:**
A. Place Amazon RDS Proxy in front of the RDS instance and have the Lambda function connect through the proxy endpoint instead of directly to the database.
B. Increase the RDS instance's max_connections parameter to a much higher value to accommodate the concurrency spike.
C. Add an Amazon ElastiCache for Redis layer in front of RDS to cache and reduce the number of write operations.
D. Switch the Lambda function's concurrency model to reserved concurrency set to 1 so only one invocation runs at a time.
**Correct answer(s):** A
**Why correct:** RDS Proxy sits between the application and the database, pooling and multiplexing many client connections (including bursty Lambda invocations) over a much smaller number of actual database connections, which directly solves connection exhaustion without requiring the application to implement its own pooling logic.
**Why each wrong option is wrong:** B raises a ceiling but doesn't solve the underlying inefficiency of one-connection-per-invocation at scale, is bounded by instance memory/class limits, and can itself degrade database performance well before matching flash-sale concurrency; C is aimed at caching reads or reducing read load, not at solving a write-path connection-exhaustion problem, since orders are being written, not read; D would eliminate the connection storm but at the cost of serializing all checkouts to one at a time, destroying the scalability the flash sale requires and effectively breaking the checkout flow under load.
**Trigger words:** "thousands of concurrent Lambda invocations open thousands of simultaneous database connections," "too many connections," "without... manually implementing custom connection-pooling logic."
**Underlying architectural principle:** RDS Proxy is the managed solution for connection pooling/multiplexing when serverless, highly concurrent clients like Lambda would otherwise overwhelm a relational database's maximum connection limit.

---

### Question 11 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A SaaS analytics company runs Amazon Aurora MySQL as its primary database and has added several Aurora Replicas to handle a growing read-heavy dashboard workload. As they add and remove replicas over time to match load (via Aurora Auto Scaling for replicas), the application team is manually updating each application server's configuration with the current list of replica endpoints, which is error-prone and has caused stale-endpoint errors after scaling events. The company wants read traffic to automatically and transparently load-balance across whichever replicas currently exist, without the application needing to track individual replica endpoints.
**Options:**
A. Configure the application to connect to the Aurora cluster's Reader endpoint instead of individual replica instance endpoints.
B. Configure the application to connect to the Aurora cluster's Writer endpoint for all read and write traffic.
C. Manually maintain a Route 53 weighted routing policy across all current replica endpoints and update it via a script after every scaling event.
D. Switch from Aurora Replicas to standard RDS Read Replicas, which expose a single shared endpoint for all replicas automatically.
**Correct answer(s):** A
**Why correct:** The Aurora cluster's Reader endpoint automatically load-balances connections across all currently available Aurora Replicas and transparently reflects replicas added or removed by Auto Scaling, eliminating the need for the application to track individual replica endpoints itself.
**Why each wrong option is wrong:** B routes all traffic to the single writer instance, defeating the purpose of having read replicas at all and adding unnecessary write-instance load; C reinvents endpoint management with custom automation, which is exactly the manual, error-prone tracking the company wants to eliminate, and Route 53 weighted routing doesn't have native awareness of Aurora Auto Scaling replica membership; D is factually backwards — standard RDS Read Replicas require the application to manage individual replica endpoints itself and do not provide an automatic load-balancing reader endpoint the way Aurora does.
**Trigger words:** "manually updating each application server's configuration with the current list of replica endpoints," "automatically and transparently load-balance," "without the application needing to track individual replica endpoints."
**Underlying architectural principle:** Aurora's cluster Reader endpoint provides automatic, membership-aware load balancing across Aurora Replicas, a capability standard RDS Read Replicas do not offer natively.

---

### Question 12 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A gaming company's leaderboard service reads player-ranking data from a DynamoDB table extremely frequently — the same small set of "top player" items are read thousands of times per second by many game clients. The engineering team wants to reduce read latency for these hot items from single-digit milliseconds down to microseconds, wants to avoid rewriting the application's existing DynamoDB SDK calls, and wants the caching layer to be automatically kept reasonably in sync with the underlying table without the application managing cache invalidation logic itself.
**Options:**
A. Add Amazon DynamoDB Accelerator (DAX) in front of the table and point the application's DynamoDB client at the DAX cluster endpoint.
B. Add an Amazon ElastiCache for Memcached cluster in front of the table and modify the application to check the cache before calling DynamoDB.
C. Enable DynamoDB Accelerated Read Scaling by switching the table's read capacity mode to On-Demand.
D. Increase the table's provisioned read capacity units substantially to reduce per-request latency.
**Correct answer(s):** A
**Why correct:** DAX is an in-memory cache built specifically for DynamoDB that is API-compatible with the existing DynamoDB SDK (requiring minimal code change beyond pointing at the DAX endpoint), delivers microsecond read latency for cached items, and uses write-through caching to stay reasonably synchronized with the table automatically.
**Why each wrong option is wrong:** B requires the application to add explicit cache-check-then-fallback logic and cache-population code, directly conflicting with the "avoid rewriting the application's existing DynamoDB SDK calls" requirement, and ElastiCache is not natively API-compatible with DynamoDB calls; C is not a real DynamoDB feature — capacity mode (On-Demand vs Provisioned) affects auto-scaling of throughput capacity, not per-request latency down to microseconds; D can improve throughput headroom and reduce throttling but does not fundamentally change DynamoDB's normal single-digit-millisecond latency profile down to microseconds.
**Trigger words:** "same small set of... items are read thousands of times per second," "microseconds," "avoid rewriting the application's existing DynamoDB SDK calls," "without the application managing cache invalidation logic."
**Underlying architectural principle:** DAX is the purpose-built, drop-in caching layer for DynamoDB read-heavy hot-item workloads needing microsecond latency with minimal application changes, distinct from general-purpose caches like ElastiCache that require explicit application-level cache logic.

---

### Question 13 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A ride-sharing company's pricing engine writes a new surge-pricing value to a DynamoDB item roughly 200 times per second for each of 50 active city zones, and every write is immediately followed by a read of that same item by a downstream billing service that must always see the value from the most recent write with no staleness whatsoever. A junior engineer proposes adding DAX in front of the table to "speed everything up," but a senior architect is concerned this will not deliver the expected benefit for this specific access pattern and may add unnecessary cost and operational surface area. Which statement best explains the senior architect's concern?
**Options:**
A. DAX's write-through cache does not help this pattern because the billing service's strongly consistent reads bypass the DAX cache and go directly to DynamoDB, so DAX adds cost without meaningfully speeding up the read path that matters here.
B. DAX cannot be used at all with a table that receives more than 100 writes per second, so the proposal is technically infeasible regardless of consistency requirements.
C. DAX only caches read operations and has no write-through behavior, so every write still bypasses the cache and reads will always return stale data.
D. DAX requires the application to explicitly invalidate cache entries after every write, which the pricing engine does not currently do, so reads would silently return outdated surge prices.
**Correct answer(s):** A
**Why correct:** DAX honors DynamoDB consistency semantics by routing strongly consistent read requests through to the underlying table rather than serving them from cache, so for a workload whose defining requirement is "always see the most recent write with no staleness," DAX's cache is effectively bypassed for the reads that matter, meaning the extra cluster is added cost and operational complexity without the intended latency benefit for this specific read pattern.
**Why each wrong option is wrong:** B is factually incorrect — DAX has no such hard write-per-second ceiling that makes it infeasible; C is factually incorrect — DAX does implement write-through caching, updating the cache on writes, it's simply that consistency semantics for this scenario route reads elsewhere; D is incorrect because DAX's write-through and TTL-based invalidation are automatic and do not require the application to explicitly invalidate cache entries.
**Trigger words:** "must always see the value from the most recent write with no staleness whatsoever," "concerned this will not deliver the expected benefit," "unnecessary cost and operational surface area."
**Underlying architectural principle:** DAX accelerates eventually-consistent (and cached strongly-consistent-eligible) read-heavy access patterns, but strongly consistent reads pass through to DynamoDB directly, so DAX provides little to no benefit for workloads whose reads specifically require strong consistency on every request.

---

### Question 14 [Priority: P0] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A platform team is choosing an in-memory caching engine on Amazon ElastiCache for a new stateless web-tier session store. Requirements include: sessions must survive an individual cache node failure without being lost, the cache must support automatic failover to a replica if the primary node fails, and the team occasionally needs to take a point-in-time backup of the cache's contents for disaster-recovery testing. The team is evaluating both available engines and needs to select the reasons that specifically justify choosing Redis over Memcached for this use case. (Select TWO.)
**Options:**
A. Redis supports replication with automatic failover to a read replica, which Memcached's multi-node architecture does not provide.
B. Redis supports snapshot-based backup and restore of the dataset, while Memcached has no native backup/restore capability.
C. Redis always delivers lower absolute read latency per item than Memcached under any workload.
D. Memcached cannot be deployed with more than a single node, making it inherently less scalable than Redis.
E. Redis uses less memory per cached item than Memcached for equivalent key-value data.
**Correct answer(s):** A, B
**Why correct:** Redis (via replication groups / Cluster Mode) provides automatic failover to a replica when the primary node fails, directly satisfying the "survive node failure" and "automatic failover" requirements; Redis also supports snapshot (RDB) and append-only-file backups that can be restored later, directly satisfying the "point-in-time backup for DR testing" requirement — neither capability exists natively in Memcached.
**Why each wrong option is wrong:** C is false as a blanket claim — Memcached's multi-threaded architecture can outperform Redis for simple key-value gets on many small objects under certain workloads, so "always lower latency" is not a valid or exam-accurate justification; D is factually wrong because Memcached does support multiple nodes for horizontal sharding of the keyspace, it simply lacks built-in replication/HA between nodes, which is a different limitation than "cannot have more than one node"; E is not an accurate or exam-relevant differentiator — memory efficiency per item is not the basis for the Redis-vs-Memcached decision in this scenario, and no such consistent property is true in general.
**Trigger words:** "survive an individual cache node failure," "automatic failover to a replica," "point-in-time backup... for disaster-recovery testing."
**Underlying architectural principle:** Choose Redis over Memcached specifically when a caching layer needs durability features — replication with automatic failover and backup/restore — rather than for a generic "faster" or "more scalable" claim, which are not the reliable differentiators between the two engines.

---

### Question 15 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A satellite-imagery company has research partners on four continents who each need to upload newly captured 3-8 GB image files into a single centralized S3 bucket in eu-central-1 as quickly and reliably as possible. Partners report slow, sometimes-failing uploads over their long-haul internet connections. The company wants to improve upload speed and reliability for these large, geographically distant uploads without standing up additional buckets, without introducing any intermediate compute layer, and with the least possible ongoing operational overhead. Select the TWO changes that best address this requirement.
**Options:**
A. Enable S3 Transfer Acceleration on the destination bucket and have partners upload through the acceleration endpoint.
B. Have the upload client use the S3 multipart upload API to split each large file into parts uploaded in parallel, retrying only failed parts.
C. Set up S3 Cross-Region Replication from a new local bucket in each partner's nearest region back to the central eu-central-1 bucket.
D. Increase the multipart upload part size to the maximum allowed so fewer, larger parts are transferred per file.
E. Front the bucket with an EC2-based upload proxy fleet in each partner region that relays files to the central bucket over a Site-to-Site VPN.
**Correct answer(s):** A, B
**Why correct:** Transfer Acceleration reduces the long-haul latency and loss impact for geographically distant uploaders by routing traffic through the nearest edge location onto the AWS backbone, and multipart upload makes each large object's transfer both faster (parallel parts) and resilient (only failed parts are retried) — together directly addressing both the "slow" and "sometimes-failing" symptoms with no new infrastructure to operate.
**Why each wrong option is wrong:** C requires provisioning and maintaining an additional bucket per region plus ongoing replication configuration, which conflicts with "without standing up additional buckets" and adds operational overhead; D is a tuning detail that can help marginally but larger part sizes reduce parallelism benefits and increase the amount of data lost on a single part's failure, making it a weaker/partial answer compared to the multipart approach itself, and it is not a required or sufficient standalone fix; E introduces an entirely new compute layer (EC2 fleet, VPN) to manage and secure, directly violating "without introducing any intermediate compute layer" and adding substantial operational overhead.
**Trigger words:** "geographically distant uploads," "slow, sometimes-failing," "without standing up additional buckets," "without introducing any intermediate compute layer," "least possible ongoing operational overhead."
**Underlying architectural principle:** For large-object uploads across long distances, Transfer Acceleration (network path optimization) and multipart upload (parallel, resumable transfer) are complementary, infrastructure-light solutions that should be combined rather than solved via additional buckets, replication, or custom relay compute.

---

### Question 16 [Priority: P2] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A subscription-billing platform runs Amazon Aurora PostgreSQL as its transactional database. Billing calculations are triggered by AWS Lambda functions invoked on a schedule every minute across thousands of customer accounts in parallel, causing periodic bursts of database connections that occasionally exhaust the database's connection limit. Separately, the customer-facing dashboard repeatedly re-runs the same expensive aggregate query (current-month invoice totals per account) on every page load, and this identical query is currently re-executed against Aurora every single time even though the underlying invoice data only changes a few times per day. The team wants to address both the connection-exhaustion problem and the redundant-expensive-query problem with the most targeted, purpose-built services for each, without switching database engines. Select the TWO services that correctly address these two distinct problems.
**Options:**
A. Amazon RDS Proxy, placed in front of Aurora to pool and multiplex the Lambda functions' bursty connections.
B. Amazon ElastiCache for Redis, placed in front of Aurora to cache the repeated aggregate query's results with a TTL matching the data's actual change frequency.
C. Amazon DynamoDB Accelerator (DAX), placed in front of Aurora to cache the repeated aggregate query's results.
D. Amazon Aurora Serverless v2, replacing the connection-management problem entirely by auto-scaling ACUs during connection bursts.
E. AWS Database Migration Service (DMS), used to continuously replicate invoice totals into a pre-aggregated read-optimized table.
**Correct answer(s):** A, B
**Why correct:** RDS Proxy is purpose-built to pool and multiplex bursty, short-lived connections (the classic Lambda-to-relational-database problem) in front of Aurora, directly solving connection exhaustion; ElastiCache for Redis is the correct general-purpose cache for repeated, expensive relational query results, letting the dashboard serve a cached aggregate with a TTL that matches the actual data change cadence instead of re-querying Aurora on every page load.
**Why each wrong option is wrong:** C is invalid because DAX is a cache exclusively for DynamoDB and is not compatible with or usable in front of a relational engine like Aurora PostgreSQL; D addresses compute capacity auto-scaling under load but does not itself pool/multiplex connections the way RDS Proxy does — a connection-count ceiling can still be hit regardless of ACU scaling, so it doesn't reliably solve connection exhaustion the way RDS Proxy does; E is designed for data migration/continuous replication between data stores, not for serving low-latency cached query results to a web dashboard, and introduces unnecessary architectural complexity for what is fundamentally a caching problem.
**Trigger words:** "periodic bursts of database connections... exhaust the database's connection limit," "same expensive aggregate query... re-executed... every single time," "underlying invoice data only changes a few times per day," "most targeted, purpose-built services for each."
**Underlying architectural principle:** Connection-exhaustion problems from bursty serverless clients call for RDS Proxy, while redundant expensive relational query results call for a general-purpose cache like ElastiCache — two distinct performance problems each with a distinct, purpose-built AWS solution, neither of which is interchangeable with DynamoDB-specific tooling like DAX.

---

*16 questions covering S3 performance, EBS volume selection, EFS performance/throughput modes, RDS/Aurora read scaling with RDS Proxy, DynamoDB DAX, and ElastiCache Redis vs Memcached — Domain 3: Design High-Performing Architectures (24% weight).*
