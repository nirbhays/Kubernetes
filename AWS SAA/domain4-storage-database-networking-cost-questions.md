# SAA-C03 Domain 4 Practice Questions (Batch 2) — Design Cost-Optimized Architectures (20% weight)

Original practice content written for self-study. These are **not** real AWS exam questions and do not reproduce any leaked/dumped exam content — they are built from the official SAA-C03 exam guide scope and current (2026) documented AWS service behavior.

Focus areas: S3 storage class and lifecycle cost optimization, DynamoDB capacity mode selection for cost, RDS/Aurora cost-scaling decisions (including Aurora Serverless v2), NAT Gateway vs VPC Endpoint cost traps, data transfer cost minimization.

This set complements `domain4-cost-optimization-questions.md` (which covers EC2 purchasing options, Auto Scaling, and Lambda/EC2/Fargate cost trade-offs) — together they span the full Domain 4 blueprint.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A hospital network must retain de-identified patient billing records for 10 years to satisfy a regulatory retention requirement. The records are essentially never accessed after the first 90 days, and on the rare occasion legal or compliance needs a record, waiting up to 12 hours for retrieval is explicitly acceptable per the company's documented retention policy. The compliance team's only stated priority is achieving the lowest possible per-GB monthly storage cost for this data.
**Options:**
A. S3 Standard-IA
B. S3 Glacier Instant Retrieval
C. S3 Glacier Deep Archive
D. S3 Intelligent-Tiering
**Correct answer(s):** C
**Why correct:** A 10-year regulatory retention requirement with essentially no access after 90 days and an explicitly acceptable retrieval time of up to 12 hours is the exact profile S3 Glacier Deep Archive is built for, and it offers the lowest per-GB storage cost of any S3 storage class.
**Why each wrong option is wrong:** A. S3 Standard-IA is priced for data still needing millisecond retrieval and is materially more expensive per GB than Deep Archive for data that will sit untouched for years. B. Glacier Instant Retrieval is for archive data still needing millisecond access (e.g., accessed quarterly), which costs more than Deep Archive and isn't needed given the explicit 12-hour retrieval tolerance. D. Intelligent-Tiering is priced and designed for unknown/changing access patterns with a monitoring fee — this data's pattern (near-zero access after 90 days) is already known, so a static lifecycle transition to Deep Archive beats Intelligent-Tiering's per-object monitoring overhead on cost.
**Trigger words:** "retain... for 10 years," "essentially never accessed after the first 90 days," "waiting up to 12 hours... explicitly acceptable," "lowest possible per-GB monthly storage cost."
**Underlying architectural principle:** When retrieval-time tolerance is explicit and generous and the access pattern is already known to be near-zero, always route to the cheapest storage tier compatible with that stated tolerance rather than a tier priced for faster access you don't need.

---

### Question 2 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A startup is launching a brand-new mobile app backend on DynamoDB with no historical traffic data to reference. Usage could range from a handful of requests per day during a slow beta period to an unpredictable viral spike of thousands of requests per second if a launch post goes viral on social media, and the team has no engineering time to build or tune capacity-planning automation before launch. Leadership's primary concern is avoiding both throttling during a surprise spike and paying for idle provisioned capacity during quiet periods.
**Options:**
A. Provisioned capacity mode with a fixed RCU/WCU value set conservatively low to control cost.
B. Provisioned capacity mode with Application Auto Scaling configured from day one.
C. On-Demand capacity mode.
D. Provisioned capacity mode with a fixed RCU/WCU value set high enough to cover the largest anticipated viral spike, paid for continuously regardless of actual traffic.
**Correct answer(s):** C
**Why correct:** On-Demand capacity mode requires no capacity planning, scales instantly to absorb unpredictable request-rate changes (including a viral spike), and bills only for actual reads/writes consumed — directly matching "no historical traffic data," "no engineering time to tune," and "avoid paying for idle capacity."
**Why each wrong option is wrong:** A. A fixed, conservatively low provisioned value guarantees throttling the moment traffic exceeds that ceiling, which is precisely the outcome leadership wants to avoid. B. Auto Scaling on provisioned capacity still reacts to CloudWatch metric thresholds with a lag, and tuning its scaling policy well is exactly the "engineering time" the team says it doesn't have before launch. D. Provisioning a fixed ceiling high enough to survive a hypothetical viral spike means paying for that ceiling around the clock, including the long quiet stretches when traffic is near zero — the opposite of "avoid paying for idle provisioned capacity," and it still requires guessing a numeric ceiling for a workload with zero historical data to base that guess on.
**Trigger words:** "no historical traffic data," "unpredictable viral spike," "no engineering time... before launch," "avoiding both throttling... and paying for idle provisioned capacity."
**Underlying architectural principle:** DynamoDB On-Demand is the correct default for new, unproven, or highly unpredictable workloads — Provisioned (with or without Auto Scaling) only becomes the cheaper choice once real, steady traffic data justifies committing to a capacity level.

---

### Question 3 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs a fleet of EC2 instances in private subnets that need to read and write objects in Amazon S3 buckets located in the same Region. There is no requirement to reach S3 from on-premises networks, from a different Region, or from outside the VPC in any way. The team wants to remove this S3 traffic from its NAT Gateway (to eliminate the associated NAT data-processing charges for this traffic) at the lowest possible additional cost.
**Options:**
A. Add an Interface VPC Endpoint (PrivateLink) for S3.
B. Add a Gateway VPC Endpoint for S3.
C. Deploy a second NAT Gateway in each Availability Zone dedicated to S3 traffic.
D. Assign public IP addresses to the EC2 instances and route S3 traffic through the Internet Gateway instead of NAT.
**Correct answer(s):** B
**Why correct:** A Gateway VPC Endpoint for S3 has no hourly or per-GB charge, works entirely within the constraints described (same-Region, from within the VPC only), and removes S3 traffic from the NAT Gateway's billed data path entirely — the lowest-cost option that fully satisfies every stated constraint.
**Why each wrong option is wrong:** A. An Interface VPC Endpoint for S3 works but incurs hourly and per-GB PrivateLink charges, making it a strictly more expensive choice than the free Gateway Endpoint when the Gateway Endpoint's constraints (same-Region, VPC-only access) are already satisfied. C. Adding more NAT Gateways only multiplies the hourly NAT charge and does nothing to remove or reduce the per-GB data-processing fee this traffic generates. D. Assigning public IPs and routing via the Internet Gateway trades one cost (NAT data processing) for another (public IPv4 address charges and internet data transfer) while also removing the private-subnet security posture, and doesn't uniquely solve the cost problem.
**Trigger words:** "same Region," "no requirement to reach S3 from on-premises... or outside the VPC," "remove this... traffic from its NAT Gateway," "lowest possible additional cost."
**Underlying architectural principle:** Whenever private-subnet resources need only same-Region access to S3 or DynamoDB, a free Gateway VPC Endpoint is always the cost-optimal way to remove that traffic from NAT Gateway billing — reach for the paid Interface Endpoint only when Gateway Endpoint's constraints genuinely can't be met.

---

### Question 4 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An application writes structured audit logs to S3 with a well-documented, predictable access pattern: logs are read frequently by a compliance dashboard for the first 30 days, read only occasionally (a few times) between day 30 and day 90 for periodic audits, and after day 90 are essentially never read again but must be retained for 3 more years for legal reasons. The platform team wants this cost optimization automated with no ongoing manual intervention and no per-object monitoring fee.
**Options:**
A. Enable S3 Intelligent-Tiering on the bucket and let it handle all the transitions automatically.
B. Configure an S3 Lifecycle rule that transitions objects to S3 Standard-IA at 30 days and to S3 Glacier Flexible Retrieval (or Deep Archive) at 90 days.
C. Write a scheduled Lambda function that runs nightly, inspects object age, and calls CopyObject to move objects between storage classes manually.
D. Store all logs in S3 Glacier Deep Archive from the moment they're written, since that has the lowest baseline storage cost.
**Correct answer(s):** B
**Why correct:** The access pattern here is fully known and predictable (hot for 30 days, warm for 60 more, cold indefinitely after), which is exactly the case a native S3 Lifecycle rule is designed to automate cheaply and permanently — no per-object monitoring fee, no custom code, and no manual intervention once configured.
**Why each wrong option is wrong:** A. Intelligent-Tiering is priced for the opposite situation — unknown or unpredictable per-object access patterns — and its small monthly monitoring fee per object is pure waste when the aging curve is already fully known in advance, as it is here. C. A custom Lambda-based mover reinvents a feature S3 already provides natively for free, adding operational cost, code to maintain, and Lambda invocation charges for no benefit over a native Lifecycle rule. D. Storing logs in Deep Archive immediately would make the frequent day-0-to-30 compliance dashboard reads either impossible at the needed speed or extremely expensive due to Deep Archive's hours-long retrieval time and higher retrieval fees for frequently accessed data.
**Trigger words:** "well-documented, predictable access pattern," "essentially never read again but must be retained," "automated with no ongoing manual intervention," "no per-object monitoring fee."
**Underlying architectural principle:** Native S3 Lifecycle rules, not Intelligent-Tiering and not custom automation, are the correct answer whenever an object's access-pattern decay curve over time is already known — Intelligent-Tiering exists specifically for the cases where that curve is unknown.

---

### Question 5 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retailer's order-history table on DynamoDB has run in production for over a year. CloudWatch metrics show consistent, predictable daily and weekly traffic cycles (higher during business hours, lower overnight, a known weekly peak on Mondays) with utilization comfortably within a well-understood, gradually growing range. Finance has asked the platform team to reduce the table's monthly DynamoDB bill without introducing throttling risk or requiring a full re-architecture.
**Options:**
A. Switch the table to On-Demand capacity mode to guarantee no throttling regardless of traffic pattern.
B. Switch the table to Provisioned capacity mode with Application Auto Scaling configured against the well-understood historical traffic range.
C. Enable DynamoDB Accelerator (DAX) in front of the table to reduce the number of billed read requests.
D. Keep On-Demand mode but request a support-ticket-based discount from AWS based on consistent usage.
**Correct answer(s):** B
**Why correct:** A year of consistent, predictable, cyclical traffic with a well-understood range is exactly the profile where Provisioned capacity (with Auto Scaling layered on top to absorb the known daily/weekly swings without manual re-tuning) costs meaningfully less per request than On-Demand, while Auto Scaling protects against the throttling risk finance wants to avoid.
**Why each wrong option is wrong:** A. On-Demand already eliminates throttling risk today, but it charges a premium per request that isn't justified once the traffic pattern is well-understood and predictable — this option doesn't address the cost-reduction ask at all. C. DAX reduces read *latency* via caching, but reads that hit the cache are typically driven by application read-through logic and DAX itself has its own hourly node cost — it doesn't restructure DynamoDB's underlying capacity billing model the way switching capacity modes does, and isn't the direct lever for this specific cost problem. D. DynamoDB has no such ad hoc negotiated-discount mechanism tied to a support ticket; the only way to pay less per request is to actually change capacity mode (as option B proposes), not to ask for a discount while remaining on On-Demand.
**Trigger words:** "run in production for over a year," "consistent, predictable daily and weekly traffic cycles," "well-understood... range," "reduce... bill without introducing throttling risk."
**Underlying architectural principle:** Once real production data proves a workload's traffic is steady and predictable, Provisioned capacity with Auto Scaling becomes the cost-optimal DynamoDB choice — On-Demand's premium exists specifically to buy freedom from that kind of capacity planning, and that premium stops paying for itself once the planning is easy.

---

### Question 6 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An analytics dashboard backed by an Amazon Aurora MySQL cluster is experiencing degraded performance because read query volume has grown steadily and now saturates the single writer instance's CPU during business hours, even though write volume itself remains low and unchanged. The engineering team wants the most cost-effective way to relieve this specific read bottleneck without altering the application's write path or its disaster-recovery posture.
**Options:**
A. Add one or more Aurora Replicas to the cluster and point the read-heavy dashboard queries at the cluster's reader endpoint.
B. Convert the entire Aurora cluster (writer included) to Aurora Serverless v2.
C. Rely on the Multi-AZ standby instance to absorb some of the read queries.
D. Vertically resize the writer instance to the next larger instance class.
**Correct answer(s):** A
**Why correct:** Aurora Replicas share the cluster's underlying storage volume (so there's no separate replication lag mechanism to manage) and are specifically designed to absorb read traffic via the reader endpoint's automatic load balancing, directly and cheaply relieving a read-only bottleneck without touching the write path.
**Why each wrong option is wrong:** B. Converting the whole cluster to Serverless v2 is a much larger architectural change than the read-bottleneck problem calls for, and since write volume is low and unchanged, most of that migration's benefit would go unused while adding scaling behavior the team didn't ask to change. C. Aurora does not have a separate non-readable "standby" instance the way traditional Single-AZ/Multi-AZ RDS deployments do — in Aurora, both high availability and read scaling come from Aurora Replicas, and the scenario explicitly describes only a single writer instance with no replicas yet provisioned. There is no existing standby to route queries to here; the real fix is to explicitly provision one or more Aurora Replicas, which is exactly what option A does. D. Vertically resizing the writer pays for more CPU capacity 24/7 (including the low-write, low-read overnight hours) purely to fix a read-only bottleneck that only occurs during business hours — Aurora Replicas scoped to the actual bottleneck are cheaper and more targeted.
**Trigger words:** "read query volume has grown... saturates the... writer instance's CPU," "write volume itself remains low and unchanged," "most cost-effective way to relieve this specific read bottleneck."
**Underlying architectural principle:** A read-only bottleneck should be solved by adding read capacity (Aurora Replicas) scoped to reads, not by paying more for the writer's compute or re-architecting the entire cluster's scaling model.

---

### Question 7 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A cost review flags that a company's NAT Gateway data-processing charges have grown to be one of the largest line items on its monthly AWS bill. Investigation traces the bulk of this traffic to a fleet of Lambda functions running inside private subnets that make frequent GetItem/PutItem calls to DynamoDB tables in the same Region and account. No other destinations account for a meaningful share of the NAT Gateway's processed data.
**Options:**
A. Increase the memory allocated to the Lambda functions so each invocation completes faster and generates less NAT-processed data.
B. Add a Gateway VPC Endpoint for DynamoDB to the VPC's route tables.
C. Move the Lambda functions out of the VPC entirely so they no longer route through NAT.
D. Add an Interface VPC Endpoint (PrivateLink) for DynamoDB.
**Correct answer(s):** B
**Why correct:** DynamoDB is one of only two services (along with S3) supported by the free Gateway VPC Endpoint type, and adding it removes essentially all of this same-Region DynamoDB traffic from the NAT Gateway's billed data path at no additional hourly or per-GB cost — directly and fully addressing the described cost driver.
**Why each wrong option is wrong:** A. Lambda memory/duration affects Lambda's own GB-second billing, not the volume of network traffic traversing NAT Gateway per DynamoDB API call — this doesn't address the NAT data-processing charge at all. C. Removing the functions from the VPC would only be viable if they don't need private-subnet-only resources for anything else, and even where viable, it's a bigger architectural change than necessary when a Gateway Endpoint solves the described problem directly and for free. D. An Interface Endpoint for DynamoDB works technically but incurs its own hourly and per-GB PrivateLink charges, which is strictly worse on cost than the free Gateway Endpoint when the traffic is same-Region DynamoDB access, exactly the case the Gateway Endpoint is built for.
**Trigger words:** "NAT Gateway data-processing charges have grown," "frequent... calls to DynamoDB tables in the same Region," "no other destinations account for a meaningful share."
**Underlying architectural principle:** When NAT Gateway cost is traced specifically to S3 or DynamoDB traffic, the fix is always a free Gateway VPC Endpoint for that service — never a NAT Gateway resize, a Lambda tuning change, or a more expensive Interface Endpoint.

---

### Question 8 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** Two backend services in the same VPC and the same Availability Zone exchange a very high volume of data every minute as part of a real-time processing pipeline. A cost review reveals a meaningful and unexpected data-transfer charge tied to this traffic, even though both services run in the same AZ, which the engineering team had assumed meant the traffic would be free. Investigation shows the calling service was configured to reach the other service using its public Elastic IP address rather than its private VPC IP address.
**Options:**
A. Move one of the two services to a different Availability Zone to isolate the traffic cost.
B. Reconfigure the calling service to address the other service using its private IP address (or private DNS name) instead of its public Elastic IP address.
C. Request an AWS Support case to waive the same-AZ data-transfer charge, since it should already be free.
D. Attach a NAT Gateway between the two services to route the traffic through a single metered path.
**Correct answer(s):** B
**Why correct:** Data transfer between two resources in the same Availability Zone over private IP addresses is free, but the same traffic routed over a public or Elastic IP address is billed even within the same AZ — switching the calling service to address its peer by private IP directly eliminates the unexpected charge while keeping both services exactly where they are.
**Why each wrong option is wrong:** A. Moving a service to a different AZ would introduce cross-AZ data-transfer charges, which are higher than the same-AZ public-IP charge being incurred now — this makes the cost problem worse, not better. C. This isn't a billing error to dispute; AWS's documented pricing already treats same-AZ traffic over public/Elastic IPs as billable, so no waiver applies, and the actual fix is architectural. D. Introducing a NAT Gateway between two resources that are already in the same VPC adds its own hourly and per-GB charges and is not how intra-VPC service-to-service traffic should ever be routed.
**Trigger words:** "same Availability Zone," "unexpected data-transfer charge," "assumed... would be free," "using its public Elastic IP address rather than its private VPC IP address."
**Underlying architectural principle:** "Same AZ" alone does not guarantee free data transfer — the free tier applies specifically to same-AZ traffic over private IP addresses, so intra-VPC services should always address each other privately, never via public or Elastic IPs.

---

### Question 9 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media-sharing platform stores millions of user-uploaded photos and videos in S3. Access behavior per object is highly unpredictable: some objects go viral and are accessed thousands of times within days, most receive only a handful of views and then go quiet, and a small number that appeared dormant for months suddenly get accessed heavily again when re-shared. The platform absolutely cannot tolerate a per-GB retrieval fee being charged unexpectedly when a dormant object suddenly becomes popular again, since that unpredictability has caused billing surprises in the past.
**Options:**
A. Configure an S3 Lifecycle rule transitioning all objects to S3 Standard-IA after 30 days of no access.
B. Enable S3 Intelligent-Tiering on the bucket.
C. Configure an S3 Lifecycle rule transitioning all objects to S3 One Zone-IA after 30 days of no access.
D. Manually re-classify objects into different storage classes based on weekly view-count reports.
**Correct answer(s):** B
**Why correct:** S3 Intelligent-Tiering is purpose-built for exactly this scenario — objects with genuinely unknown, changing access patterns — automatically moving objects between frequent- and infrequent-access tiers based on observed usage with no retrieval fees at all, which directly eliminates the billing-surprise risk from a dormant object suddenly being re-accessed.
**Why each wrong option is wrong:** A. S3 Standard-IA charges a per-GB retrieval fee every time an object is read; a dormant object going viral again after being moved to Standard-IA would trigger exactly the unpredictable retrieval-fee billing surprise the platform explicitly wants to avoid. C. One Zone-IA has the same retrieval-fee structure as Standard-IA (plus reduced redundancy, inappropriate for irreplaceable user uploads), so it carries the identical billing-surprise risk as option A. D. Manually re-classifying millions of objects weekly based on view-count reports is operationally unscalable and still can't react fast enough to prevent a retrieval-fee event on an object that goes viral between reporting cycles.
**Trigger words:** "highly unpredictable" per object, "dormant for months suddenly get accessed heavily again," "cannot tolerate a per-GB retrieval fee being charged unexpectedly."
**Underlying architectural principle:** Whenever a scenario explicitly rules out retrieval-fee risk on top of an unpredictable access pattern, S3 Intelligent-Tiering is the only storage-class strategy that satisfies both constraints simultaneously — IA-family classes and manual reclassification both reintroduce the exact risk being avoided.

---

### Question 10 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An engineering organization maintains a dozen separate Aurora PostgreSQL clusters, one per feature team, used exclusively for development and integration testing. Usage is sporadic: most clusters see active queries only during a portion of the workday when a given team is actively testing, with long idle stretches overnight, on weekends, and between sprints. The organization wants to minimize the combined cost of these dev/test clusters without giving up full Aurora PostgreSQL compatibility or asking engineers to remember to manually stop and start databases.
**Options:**
A. Keep each cluster on a small provisioned instance class running continuously, since it's already the smallest available size.
B. Migrate each dev/test cluster to Aurora Serverless v2, allowing capacity to scale down automatically (including toward zero ACUs) during idle periods.
C. Purchase 1-year Reserved Instance pricing for each cluster's provisioned instance to lock in a discount.
D. Consolidate all twelve teams' schemas onto a single shared, larger provisioned Aurora instance running continuously.
**Correct answer(s):** B
**Why correct:** Aurora Serverless v2 automatically scales compute capacity up when a team is actively testing and back down — including toward zero ACUs — during the long idle stretches described, which directly minimizes cost for sporadic, idle-heavy dev/test usage while preserving full Aurora PostgreSQL feature compatibility and requiring no manual stop/start action from engineers.
**Why each wrong option is wrong:** A. Even the smallest provisioned instance class still bills continuously 24/7 regardless of the long idle periods described, wasting money for all the hours no team is actively testing. C. A 1-year Reserved Instance commitment is priced for steady, predictable, continuous usage — locking in a discount on a workload that's explicitly sporadic and idle-heavy still pays for capacity that sits unused most of the time. D. Consolidating twelve teams onto one shared, always-on instance removes each team's isolation (a real operational and testing-safety concern) and still runs continuously regardless of aggregate idle time, rather than scaling down when nobody is actively testing.
**Trigger words:** "development and integration testing," "sporadic," "long idle stretches overnight, on weekends," "minimize... cost... without giving up full Aurora... compatibility or asking engineers to remember to manually stop and start."
**Underlying architectural principle:** Aurora Serverless v2's auto-scale-to-near-zero behavior is the standard cost answer for intermittent, idle-heavy database workloads (dev/test, low-traffic apps) where a continuously running provisioned instance — discounted or not — would otherwise pay for idle time.

---

### Question 11 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A company ingests millions of small objects into an S3 bucket every day via a data pipeline that occasionally experiences network interruptions mid-upload. A cost review shows the bucket's total storage size and bill have been climbing noticeably faster than the growth in objects the application itself reports having successfully written, and separately, the team has a known, predictable access-decay pattern for successfully written objects (hot for 14 days, rarely touched after). Select the two actions that directly and correctly address these findings.
**Options:**
A. Add a Lifecycle rule that uses `AbortIncompleteMultipartUpload` to automatically clean up abandoned multipart upload parts left behind by interrupted uploads.
B. Add a Lifecycle rule that transitions successfully written objects to a cheaper storage class after the known 14-day hot period ends.
C. Enable S3 Versioning on the bucket to protect against the interrupted uploads causing data loss.
D. Increase the bucket's default encryption from SSE-S3 to SSE-KMS to get better cost visibility per object.
E. Disable multipart upload for this pipeline entirely so interrupted uploads can no longer occur.
**Correct answer(s):** A, B
**Why correct:** Interrupted multipart uploads leave behind incomplete parts that continue to incur storage charges indefinitely without ever appearing as a "successful" object in application logs — exactly matching the described storage-growth-vs-reported-object-growth gap — and `AbortIncompleteMultipartUpload` (A) is the native lifecycle action built to clean these up; separately, the bucket's known, predictable 14-day hot/cold access pattern (B) is exactly the case a standard Lifecycle transition rule is designed to automate.
**Why each wrong option is wrong:** C. Versioning protects against accidental overwrite/deletion of completed objects — it does nothing to reclaim or prevent the storage cost of abandoned incomplete multipart parts, and would add its own noncurrent-version storage cost on top. D. Switching encryption type changes how objects are encrypted, not what's tracked or billed for storage, and provides no per-object cost visibility feature by itself. E. Multipart upload is required for large objects (mandatory above 5 GB, recommended above 100 MB) and disabling it doesn't fix the underlying interruption problem — network interruptions would instead cause full single-PUT failures, and the abandoned-parts problem already accumulated would still need cleanup.
**Trigger words:** "occasionally experiences network interruptions mid-upload," "climbing noticeably faster than the growth in objects the application itself reports," "known, predictable access-decay pattern... hot for 14 days, rarely touched after."
**Underlying architectural principle:** Unexplained S3 storage growth beyond an application's own reported object count is a classic signature of abandoned multipart upload parts, cleaned up via `AbortIncompleteMultipartUpload`; this is independent from and complementary to ordinary Lifecycle transition rules for known access-decay patterns.

---

### Question 12 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A logistics company's DynamoDB table supporting its shipment-tracking API has now run in production for 14 months on On-Demand capacity mode. CloudWatch metrics for that entire period show request volume holding within a narrow, predictable band that grows slowly and linearly month over month, with no unexpected spikes ever recorded and utilization consistently high relative to any reasonable provisioned ceiling the team might set. Finance wants to reduce the DynamoDB bill for this specific table without introducing meaningful throttling risk, and understands that On-Demand's per-request pricing is structured to include a premium for not requiring any capacity forecasting.
**Options:**
A. Leave the table on On-Demand capacity mode indefinitely, since On-Demand is always the lowest-cost option regardless of traffic predictability.
B. Switch the table to Provisioned capacity mode with Application Auto Scaling, sized against the 14 months of stable, high-utilization historical data.
C. Enable DynamoDB Streams on the table to reduce per-request billing overhead.
D. Shard the table's partition key into many smaller tables to reduce per-request cost.
**Correct answer(s):** B
**Why correct:** Fourteen months of stable, high-utilization, low-variance traffic is precisely the evidence needed to size a Provisioned + Auto Scaling configuration with confidence — since On-Demand's premium exists specifically to pay for not needing that forecast, and the forecast is now easy and well-supported by real data, Provisioned capacity becomes the cheaper choice at this steady, high utilization level while Auto Scaling still absorbs the slow linear growth and protects against throttling.
**Why each wrong option is wrong:** A. On-Demand is not unconditionally the cheapest mode — its convenience premium only pays for itself when traffic is genuinely unpredictable; the scenario explicitly establishes the opposite (stable, predictable, high utilization), which is exactly when Provisioned capacity is the documented cheaper choice. C. DynamoDB Streams is a change-data-capture feature for downstream event processing (e.g., Lambda triggers) — it has no effect on the underlying read/write capacity billing model. D. Splitting the table into many smaller tables adds significant application complexity and operational overhead without changing the fundamental economics of On-Demand versus Provisioned pricing, and DynamoDB pricing isn't structured around table count in a way that would make this cheaper.
**Trigger words:** "run in production for 14 months on On-Demand," "narrow, predictable band," "no unexpected spikes ever recorded," "utilization consistently high," "premium for not requiring any capacity forecasting."
**Underlying architectural principle:** On-Demand's per-request premium is the price of not forecasting capacity — once real production history proves a workload's demand is stable, predictable, and consistently high-utilization, that premium stops being worth paying, and Provisioned capacity with Auto Scaling becomes the cost-optimal choice.

---

### Question 13 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company runs a business-critical application on Amazon RDS for SQL Server with Multi-AZ enabled for high availability, which the compliance team requires and which must not be removed or weakened. Over the past several months, read query load from a growing internal reporting tool has increased significantly and is now measurably degrading the primary instance's performance. The team wants the most cost-effective way to relieve this specific read-load problem while keeping the existing Multi-AZ HA configuration completely unchanged.
**Options:**
A. Create one or more RDS Read Replicas and point the reporting tool's connection string at a Read Replica instead of the primary.
B. Add additional Multi-AZ standby instances to the deployment so reporting queries can be routed to a standby.
C. Increase the primary instance to the next larger instance class to absorb the additional read load.
D. Migrate the entire database engine to Aurora Serverless v2 immediately to gain read scaling.
**Correct answer(s):** A
**Why correct:** RDS Read Replicas are purpose-built for offloading read traffic from the primary instance at a cost scoped specifically to the additional read capacity needed, and they operate entirely independently of — and don't require any change to — the existing Multi-AZ HA configuration, satisfying every constraint in the scenario.
**Why each wrong option is wrong:** B. Standard RDS for SQL Server Multi-AZ uses a single non-readable standby for failover only (the readable-standby "Multi-AZ DB Cluster" deployment option is available only for MySQL and PostgreSQL, not SQL Server), so there is no such thing as "additional readable standbys" to route reporting queries to in this configuration. C. Vertically resizing the primary pays for more compute capacity around the clock to fix a read-specific bottleneck, which is a more expensive and less targeted fix than adding read capacity scoped to reads only. D. Migrating the entire production database engine to Aurora is a major, high-risk, non-trivial re-architecture effort that is not justified as an "immediate," cost-effective fix when a native RDS feature (Read Replicas) already solves the stated problem directly.
**Trigger words:** "RDS for SQL Server," "Multi-AZ... must not be removed or weakened," "read query load... increased significantly," "most cost-effective way to relieve this specific read-load problem."
**Underlying architectural principle:** RDS Read Replicas and Multi-AZ solve two entirely different problems (read scaling vs. HA/failover) and can be layered independently — don't assume Multi-AZ's standby can absorb reads, especially for engines (like SQL Server) that don't support the readable Multi-AZ DB Cluster deployment option.

---

### Question 14 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A fintech company's private-subnet application fleet retrieves database credentials from AWS Secrets Manager on every connection attempt, generating dozens of terabytes of monthly traffic that currently routes through a NAT Gateway. This traffic now accounts for the single largest component of the company's NAT Gateway data-processing bill. The security team separately requires that this traffic never traverse the public internet, ruling out any option that would route it through an Internet Gateway.
**Options:**
A. Add a Gateway VPC Endpoint for Secrets Manager to remove this traffic from the NAT Gateway.
B. Add an Interface VPC Endpoint (PrivateLink) for Secrets Manager in the relevant subnets.
C. Deploy additional NAT Gateways across more Availability Zones to spread out the data-processing charges.
D. Cache credentials locally on each instance indefinitely to avoid calling Secrets Manager altogether.
**Correct answer(s):** B
**Why correct:** Secrets Manager is not one of the two services supported by the free Gateway VPC Endpoint type, so an Interface VPC Endpoint (PrivateLink) is the only way to keep this traffic off the public internet while removing it from the NAT Gateway's billed data path; at this traffic volume, PrivateLink's hourly-plus-per-GB pricing is well documented to come in below the equivalent NAT Gateway data-processing cost for the same volume.
**Why each wrong option is wrong:** A. Gateway VPC Endpoints only support S3 and DynamoDB — Secrets Manager has no Gateway Endpoint option, so this choice is not technically available regardless of cost. C. Spreading traffic across more NAT Gateways multiplies the fixed hourly charge without changing the underlying per-GB data-processing rate that's driving the bulk of the cost — it doesn't solve the problem. D. Indefinitely caching credentials locally undermines the security purpose of using Secrets Manager (timely credential rotation and centralized access control) and isn't a cost-optimization answer the scenario is asking for; it also isn't the kind of architectural network fix the "never traverse the public internet" constraint calls for.
**Trigger words:** "Secrets Manager," "dozens of terabytes of monthly traffic... through a NAT Gateway," "never traverse the public internet."
**Underlying architectural principle:** For AWS services other than S3 and DynamoDB, an Interface VPC Endpoint (PrivateLink) — not a Gateway Endpoint, which doesn't exist for them — is the way to remove high-volume private-subnet traffic from NAT Gateway billing while keeping it off the public internet; at sufficient volume, PrivateLink's per-GB rate typically undercuts NAT Gateway's.

---

### Question 15 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A media company stores large video files in an S3 bucket in a single Region and serves them directly to a global audience by generating presigned URLs pointing straight at the bucket. A cost review shows that data-transfer-out-to-internet charges from this bucket have become the single largest line item on the AWS bill, and the same files are being downloaded repeatedly by large numbers of viewers around the world. The company wants to substantially reduce this specific cost while maintaining or improving the global viewing experience.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket to speed up file delivery to distant viewers.
B. Put Amazon CloudFront in front of the S3 bucket (using Origin Access Control) and serve viewers through CloudFront instead of directly from S3.
C. Set up Cross-Region Replication to additional Regions and use Route 53 latency-based routing to send each viewer to their nearest S3 bucket copy.
D. Enable S3 Intelligent-Tiering on the bucket to reduce the per-GB storage cost of the video files.
**Correct answer(s):** B
**Why correct:** CloudFront's data-transfer-out-to-internet pricing is lower than S3's direct-to-internet data-transfer pricing at scale, and because the same popular files are being downloaded repeatedly, CloudFront's edge caching also eliminates most repeat trips back to the S3 origin entirely — directly and substantially cutting the largest cost driver named while improving global viewer latency.
**Why each wrong option is wrong:** A. S3 Transfer Acceleration speeds up **uploads** to S3 from geographically distant clients over the AWS backbone — it has no relevance to reducing the cost or improving the experience of **downloads** being served out to viewers. C. Replicating the files into multiple Regions still results in each regional copy incurring its own full data-transfer-out-to-internet charges with no caching benefit for repeated downloads of the same popular files, and adds ongoing storage cost in every additional Region — a more expensive path to a worse outcome than caching. D. Intelligent-Tiering optimizes storage cost based on access frequency, but the cost problem described here is data-transfer-out cost, not storage cost — this doesn't address the stated bottleneck at all.
**Trigger words:** "data-transfer-out-to-internet charges... single largest line item," "downloaded repeatedly by large numbers of viewers around the world," "substantially reduce this specific cost while... improving the global viewing experience."
**Underlying architectural principle:** For globally distributed, repeatedly downloaded content, fronting S3 with CloudFront reduces cost on two independent axes simultaneously — cheaper data-transfer-out pricing than direct S3 egress, and cache hit ratio eliminating redundant origin fetches — making it the default answer whenever repeated-download egress cost is the stated problem.

---

### Question 16 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A company's private-subnet application fleet currently reaches three destinations exclusively through a single NAT Gateway: (1) a high-volume S3 bucket used for object storage, (2) a high-volume DynamoDB table, and (3) AWS Systems Manager, used moderately for Session Manager access by operators (no bastion host or SSH exists). The NAT Gateway's data-processing charges have grown substantially, and a cost review confirms these three destinations account for effectively all of the fleet's outbound traffic — there is no other internet-bound traffic from this fleet. Select the two changes that most directly and correctly reduce cost here.
**Options:**
A. Add Gateway VPC Endpoints for S3 and DynamoDB.
B. Add an Interface VPC Endpoint (PrivateLink) for Systems Manager (including the endpoints Session Manager requires) in the relevant subnets.
C. Remove the NAT Gateway entirely without adding any VPC endpoints, since the fleet apparently has no other need for internet access.
D. Add an Interface VPC Endpoint (PrivateLink) for S3 instead of a Gateway VPC Endpoint, to get finer security-group-based access control.
E. Increase the NAT Gateway's provisioned bandwidth to reduce its per-GB processing rate.
**Correct answer(s):** A, B
**Why correct:** Gateway VPC Endpoints for S3 and DynamoDB (A) are free and remove the two highest-volume destinations from NAT Gateway billing entirely; a Systems Manager Interface VPC Endpoint (B) is required because Session Manager depends on SSM endpoints that have no Gateway Endpoint option, and adding it removes the NAT Gateway's dependency for operator access as well — together these two changes address all three named destinations.
**Why each wrong option is wrong:** C. Removing the NAT Gateway outright before confirming that literally zero other traffic (including any not yet identified, such as OS/agent updates or other AWS API calls not covered by an endpoint) needs internet egress is a risky, unverified assumption that could silently break functionality — the safe, verified action is adding the specific endpoints needed for the three named destinations. D. A Gateway VPC Endpoint for S3 is free, while an Interface VPC Endpoint for S3 incurs hourly and per-GB charges — since the scenario's goal is minimizing cost and Gateway Endpoint constraints (S3, same VPC/Region) are already satisfied, swapping to the paid Interface Endpoint variant for "finer security-group control" is an unnecessary added cost not justified by any stated requirement. E. NAT Gateway bandwidth already scales automatically up to its ceiling with no manual provisioning step or "bandwidth setting" to adjust, and even if such a lever existed, it wouldn't change the per-GB data-processing rate driving the cost.
**Trigger words:** "S3 bucket... DynamoDB table... Systems Manager, used... for Session Manager access," "NAT Gateway's data-processing charges have grown substantially," "no other internet-bound traffic from this fleet."
**Underlying architectural principle:** Systematically map every distinct destination behind a costly NAT Gateway to the cheapest correct VPC Endpoint type available for it (Gateway for S3/DynamoDB, Interface for everything else that supports PrivateLink) rather than removing NAT outright or defaulting to the more expensive endpoint type out of caution.

---

### Question 17 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A B2B SaaS company runs a separate Aurora PostgreSQL cluster per customer tenant for data isolation. Usage analysis reveals two clearly distinct groups: a small number of large "enterprise" tenants generate steady, high, predictable 24/7 database load that has held consistent for over a year, while the much larger group of "starter" tier tenants generates sporadic, idle-heavy, highly variable load with long stretches of near-zero activity between bursts of use. Finance wants a strategy that minimizes total cost across all tenant clusters while preserving full Aurora PostgreSQL compatibility and each tenant's data isolation. Select the two best actions.
**Options:**
A. Run the "starter" tier tenant clusters on Aurora Serverless v2, allowing capacity to scale down toward zero ACUs during their long idle stretches.
B. Consolidate every tenant, both enterprise and starter, onto a single large provisioned Aurora cluster sized to the combined peak load of all tenants.
C. Run the "enterprise" tier tenants' clusters on provisioned Aurora instances covered by Reserved Instance pricing, since their usage is steady and predictable.
D. Migrate every tenant, regardless of usage pattern, to Aurora Serverless v2, since it is the newest Aurora capacity model and is always the cheapest option.
E. Purchase 3-year Reserved Instances sized to each tenant's individual historical peak usage, including the starter tier tenants.
**Correct answer(s):** A, C
**Why correct:** Matching each usage profile to the purchasing model built for it minimizes total cost: the starter tenants' sporadic, idle-heavy pattern (A) is exactly what Aurora Serverless v2's scale-to-near-zero behavior is priced for, while the enterprise tenants' steady, predictable, year-long 24/7 baseline (C) is exactly the profile a committed-use Reserved Instance discount on provisioned Aurora is priced for.
**Why each wrong option is wrong:** B. Consolidating all tenants onto one shared cluster eliminates the per-tenant data isolation the company explicitly wants to preserve, and still requires sizing to the combined peak of every tenant, which doesn't reduce the fundamental waste of paying for idle starter-tenant capacity most of the time. D. Aurora Serverless v2 is not unconditionally the cheapest option in every case — for the enterprise tenants' steady, high, 24/7 utilization, a Reserved Instance's committed-use discount on provisioned capacity is cheaper than paying Serverless v2's per-ACU-second rate with no commitment discount for that same guaranteed demand. E. Sizing a Reserved Instance to each starter tenant's individual historical peak wastes money during that tenant's long idle stretches, which make up most of its usage — this is the opposite of matching the purchasing model to the workload's actual (mostly idle) profile.
**Trigger words:** "steady, high, predictable 24/7 database load that has held consistent for over a year" vs. "sporadic, idle-heavy, highly variable load with long stretches of near-zero activity," "minimizes total cost... while preserving... each tenant's data isolation."
**Underlying architectural principle:** In a mixed-workload environment, the cost-optimal strategy is rarely a single uniform choice — layer a committed-use discount (Reserved Instance / Savings Plan) under confirmed steady demand and an auto-scaling, pay-per-use model (Aurora Serverless v2, DynamoDB On-Demand) under genuinely variable or idle-heavy demand.

---

### Question 18 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company ingests millions of small log objects into S3 daily and, wanting maximum savings, configured a Lifecycle rule transitioning every object to S3 Glacier Deep Archive just 1 day after creation. After implementing this rule, the monthly S3 bill actually increased rather than decreased. Investigation reveals that a separate, pre-existing automated cleanup process permanently deletes roughly 90% of these log objects after about 10 days once they've been identified as duplicates or superseded by newer data — well before any archive tier's minimum storage duration commitment has elapsed.
**Options:**
A. Switch the 1-day transition target from Glacier Deep Archive to Glacier Flexible Retrieval instead, keeping the same 1-day transition timing.
B. Remove the 1-day transition entirely; keep the existing 10-day deletion behavior, and only add a transition to a cheaper storage class (timed appropriately) for the subset of objects confirmed to survive past the cleanup process.
C. Keep the transition to Glacier Deep Archive at 1 day, and additionally add a Lifecycle expiration rule deleting all objects after exactly 5 days regardless of the cleanup process's own logic.
D. Replace the Glacier Deep Archive transition with S3 Intelligent-Tiering enabled from day 1.
**Correct answer(s):** B
**Why correct:** Because roughly 90% of these objects are deleted around day 10 — well short of any cold-tier's minimum storage duration commitment — transitioning them early into a class with a minimum-duration charge triggers an effective early-deletion cost that exceeds what they would have cost simply sitting in Standard for those 10 days; removing the premature transition and only moving the smaller surviving subset of objects (the ones that outlive the cleanup process) into a cheaper tier eliminates this waste at its root.
**Why each wrong option is wrong:** A. Glacier Flexible Retrieval also carries its own minimum storage duration commitment, which is still longer than the ~10-day real lifetime of most of these objects — this reduces the per-object penalty somewhat but doesn't fix the underlying mismatch between transition timing and actual object lifetime. C. Forcing an unconditional 5-day expiration ignores that the existing cleanup process needs up to ~10 days to correctly identify duplicates/superseded objects, risking premature deletion of objects still needed for that comparison, while also still paying the early-deletion penalty on the objects already transitioned to Deep Archive at day 1. D. Since most of these objects are deleted around day 10, well before Intelligent-Tiering's Infrequent Access tier threshold (30 days) would ever move them out of the frequent-access tier, enabling Intelligent-Tiering produces essentially zero savings for this object population and adds its per-object monitoring fee for no benefit — it doesn't address the root cause of the cost increase at all.
**Trigger words:** "monthly S3 bill actually increased rather than decreased," "deletes roughly 90%... after about 10 days," "well before any archive tier's minimum storage duration commitment has elapsed."
**Underlying architectural principle:** Never transition objects into a storage class with a minimum storage duration commitment unless the object's real expected lifetime is confidently longer than that minimum — doing so converts an intended savings action into an early-deletion cost penalty.

---

### Question 19 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A financial analytics platform's Aurora MySQL cluster has two distinct demand components: the writer handles a steady, guaranteed baseline equivalent to roughly 8 ACUs sustained continuously, 24 hours a day, all year; separately, an internal BI tool periodically runs heavy read-only analytical queries that spike demand up to roughly 64 ACUs for a few hours at unpredictable times, several times a week, with no fixed schedule. The company wants an architecture that commits to (and gets a committed-use discount for) only the portion of demand that is truly guaranteed, while letting the unpredictable analytical burst scale automatically with no manual intervention and no standing over-provisioning for the peak.
**Options:**
A. Run the entire cluster (writer and readers together) on Aurora Serverless v2, auto-scaling anywhere between 8 and 64 ACUs as needed.
B. Run a provisioned writer instance sized to the guaranteed 8 ACU baseline, covered by Reserved Instance pricing, and add one or more Aurora Serverless v2 readers that auto-scale up only during the unpredictable analytical bursts.
C. Run a single provisioned writer instance sized to the full 64 ACU peak, covered by Reserved Instance pricing, so it's always ready for a burst.
D. Run the writer on Aurora Serverless v2 with both its minimum and maximum ACU settings fixed at 64, to guarantee burst headroom is always available.
**Correct answer(s):** B
**Why correct:** This mixed-fleet architecture matches each demand component to the purchasing model built for it: the guaranteed, steady 8-ACU baseline goes on a provisioned instance eligible for a Reserved Instance commitment discount (something Serverless v2's per-ACU-second pricing has no equivalent mechanism for), while the genuinely unpredictable analytical bursts are absorbed by Serverless v2 readers that scale automatically only when actually needed — avoiding paying either a commitment premium for capacity that isn't guaranteed or a no-discount rate for capacity that is guaranteed.
**Why each wrong option is wrong:** A. Running the entire cluster on Serverless v2 means even the guaranteed, always-on 8-ACU baseline is billed at Serverless v2's uncommitted per-ACU-second rate with no long-term discount mechanism, costing more over a year than covering that same guaranteed demand with a Reserved Instance. C. Sizing a Reserved Instance to the 64-ACU peak means paying for that much capacity continuously even though it's only actually needed for a few hours, several times a week — the vast majority of the time this capacity sits idle and wasted. D. Fixing Serverless v2's minimum ACU at 64 defeats the entire purpose of its auto-scaling model, guaranteeing the cost of running at peak capacity continuously — this is worse than every other option, including the peak-sized Reserved Instance in C.
**Trigger words:** "steady, guaranteed baseline... sustained continuously, 24 hours a day, all year," "unpredictable... at unpredictable times," "commits to... only the portion of demand that is truly guaranteed," "no standing over-provisioning for the peak."
**Underlying architectural principle:** Aurora's mixed reader fleet capability lets an architecture combine a committed-discount provisioned instance for guaranteed baseline demand with auto-scaling Serverless v2 capacity for genuinely unpredictable demand within the same cluster — this beats forcing the entire cluster onto either model alone whenever demand has both a guaranteed floor and an unpredictable ceiling.

---

### Question 20 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A three-tier application runs across multiple Availability Zones in one Region: a web tier behind an ALB in public subnets, an app tier in private subnets that calls S3 and DynamoDB heavily and also calls an external third-party payment gateway over the public internet, and a database tier on Aurora with Multi-AZ. A cost audit surfaces three unexpectedly large monthly charges: (1) NAT Gateway data-processing charges, (2) cross-AZ data-transfer charges between the app tier and a single-AZ ElastiCache Memcached cluster that every app instance in every AZ calls constantly, and (3) S3 storage cost that has grown steadily even though the application's own logged object-write count has stayed flat. Select the two changes that most directly address the largest, clearly-attributable cost drivers actually described here.
**Options:**
A. Add Gateway VPC Endpoints for S3 and DynamoDB so that traffic to those two services no longer traverses the NAT Gateway (the third-party payment gateway call still requires a NAT Gateway or Internet Gateway path, since it's a genuine external internet destination with no VPC endpoint available).
B. Add an S3 Lifecycle rule using `AbortIncompleteMultipartUpload` to clean up abandoned multipart upload parts, which accumulate storage cost without ever appearing in the application's own logged object-write count.
C. Move the ElastiCache Memcached cluster into a cluster placement group spanning all the Availability Zones in use, to eliminate the cross-AZ latency and cost.
D. Replace the NAT Gateway with a single self-managed NAT Instance to lower the hourly charge, accepting the added patching and single-point-of-failure operational overhead.
E. Replace the Gateway VPC Endpoint approach with routing the payment gateway's traffic through a newly created Interface VPC Endpoint for the payment provider.
**Correct answer(s):** A, B
**Why correct:** A directly removes the NAT Gateway's largest addressable traffic category (same-Region S3 and DynamoDB calls) at no additional cost while correctly leaving the genuinely internet-bound payment gateway traffic on NAT/IGW where it belongs, and B directly matches the classic signature of S3 storage growing faster than an application's own reported object count — abandoned incomplete multipart upload parts — with the native lifecycle action built to clean them up.
**Why each wrong option is wrong:** C. Cluster placement groups are explicitly confined to a single Availability Zone and cannot span multiple AZs, so this doesn't just fail to fix the cross-AZ cost — it's not even a valid configuration for the stated goal; the real fix for a single-AZ cache being hit from every AZ is deploying cache nodes/replicas in each AZ (or an equivalent multi-AZ caching topology) so instances read from a local-AZ node. D. A self-managed NAT Instance trades NAT Gateway's hourly and per-GB data-processing charges for ordinary EC2 instance and data-transfer-out charges instead — but once option A removes the high-volume S3/DynamoDB traffic from the NAT path, the only traffic left (the third-party payment gateway calls) is no longer the largest cost driver, making this swap a disproportionate, higher-risk change (patching burden, bandwidth ceiling, single point of failure) for a traffic category that isn't the problem being solved. E. There is no such thing as a VPC Endpoint (Gateway or Interface) for a third-party, non-AWS payment gateway reachable only over the public internet — VPC Endpoints (via PrivateLink) connect to AWS services or specifically published PrivateLink-enabled SaaS endpoints, not arbitrary external internet destinations.
**Trigger words:** "S3 and DynamoDB heavily," "external third-party payment gateway over the public internet," "single-AZ ElastiCache Memcached cluster that every app instance in every AZ calls constantly," "S3 storage cost... grown steadily even though the application's own logged object-write count has stayed flat."
**Underlying architectural principle:** Cost audits require attributing each charge to its real, specific root cause before choosing a fix — VPC Endpoints only ever apply to AWS (or PrivateLink-published) services, placement groups never span AZs, and unexplained S3 growth against flat logged writes points specifically at incomplete multipart uploads, not general lifecycle mistuning.

---

*End of Domain 4 practice set, Batch 2 (20 questions). Original study content — not sourced from or reproducing any real/leaked SAA-C03 exam questions.*
