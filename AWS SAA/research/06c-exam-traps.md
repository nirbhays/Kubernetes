# AWS SAA-C03 — 50 Exam Traps

# AWS SAA Exam Traps — Batch 1 of 2 (Traps 1–25)

### Trap 1: Multi-AZ mistaken for a read-scaling feature
**The trap:** Choosing "enable Multi-AZ" as the answer for "reduce read load on our RDS database" or "improve read performance."
**Why it's tempting:** Multi-AZ sounds like it adds more database capacity, and both features involve a standby/secondary copy of data.
**Why it's wrong:** The Multi-AZ standby is not accessible for reads (Aurora Multi-AZ readers are the exception) — it exists purely for synchronous failover/HA. Read Replicas are the feature that offloads read traffic asynchronously.
**The correct mental model:** Multi-AZ = availability/durability (standby, not queryable in standard RDS); Read Replica = horizontal read scaling.

### Trap 2: NAT Gateway for private access to S3
**The trap:** Routing traffic from a private subnet to S3 through a NAT Gateway because "S3 is on the public internet."
**Why it's tempting:** NAT Gateway is the tool you already used to let private instances reach "the internet," so it feels like the default answer for any AWS-service access.
**Why it's wrong:** It works but incurs unnecessary NAT data-processing charges and adds an extra hop, when a free Gateway VPC Endpoint gives private, in-VPC routing directly to S3 (or DynamoDB).
**The correct mental model:** For S3/DynamoDB from a VPC, always default to a Gateway Endpoint (free) before considering NAT Gateway or Interface Endpoints.

### Trap 3: Making a database "publicly accessible" to fix a connectivity issue
**The trap:** Setting an RDS instance's "Publicly Accessible" flag to Yes and opening the security group to 0.0.0.0/0 so an application "can finally connect."
**Why it's tempting:** It's the fastest way to unblock a connection error during troubleshooting.
**Why it's wrong:** It exposes the database to the internet and almost never matches the exam's security-first expectations; the real fix is usually a security-group rule scoped to the app tier's SG, or correct subnet/route table placement.
**The correct mental model:** Databases stay in private subnets with security groups scoped to specific source SGs — public accessibility is a red flag, not a fix.

### Trap 4: Hardcoding IAM access keys into application code
**The trap:** Embedding an IAM user's access key/secret key in an EC2 instance, container, or Lambda function to grant it AWS API access.
**Why it's tempting:** It's conceptually simple — "give the app credentials like a login."
**Why it's wrong:** Hardcoded long-lived credentials are a security anti-pattern (leak risk, no rotation, no least-privilege scoping); AWS compute services can assume temporary, auto-rotated credentials instead.
**The correct mental model:** Compute resources get permissions via IAM roles (instance profiles, task roles, execution roles) — never via embedded access keys.

### Trap 5: Picking ALB when the requirement demands NLB
**The trap:** Defaulting to Application Load Balancer for every load-balancing question, including ones needing static IP addresses, ultra-low latency, or raw TCP/UDP passthrough.
**Why it's tempting:** ALB is the more commonly discussed/"modern" load balancer and handles HTTP(S) well, so it feels like the safe generic pick.
**Why it's wrong:** ALB operates at Layer 7 and cannot preserve source IP transparently at Layer 4, doesn't natively expose a fixed IP per AZ, and adds more latency than NLB — all things the exam calls out explicitly (e.g., "millions of requests per second," "static IP," "preserve client IP," "non-HTTP TCP/UDP protocol").
**The correct mental model:** Content-based routing/HTTP(S) → ALB; extreme performance, static IP, or non-HTTP TCP/UDP → NLB.

### Trap 6: Confusing CloudFront with Global Accelerator
**The trap:** Reaching for CloudFront to "improve global performance" of a non-HTTP TCP/UDP application, or reaching for Global Accelerator to cache static web content.
**Why it's tempting:** Both are described as "improve global application performance" services, so they look interchangeable.
**Why it's wrong:** CloudFront is a caching CDN for HTTP(S) content at the edge; Global Accelerator routes traffic over the AWS global network to the optimal endpoint without caching, and works for any TCP/UDP application, including gaming and IoT.
**The correct mental model:** Need to cache/serve HTTP content close to users → CloudFront; need fast routing/failover for TCP/UDP (including non-HTTP) traffic with static anycast IPs → Global Accelerator.

### Trap 7: Choosing provisioned infrastructure when the question says "least operational overhead"
**The trap:** Answering with self-managed EC2 + Auto Scaling + manually patched software when the scenario explicitly emphasizes minimizing operational/management burden.
**Why it's tempting:** EC2-based solutions feel more "in your control" and familiar from earlier exam objectives.
**Why it's wrong:** "Least operational overhead" is exam code for serverless/managed services — Lambda, Fargate, Aurora Serverless, DynamoDB, managed queues — which eliminate patching, scaling, and capacity management.
**The correct mental model:** See "least operational overhead," "minimal management," or "no servers to manage" → default to the most serverless/managed option among the choices.

### Trap 8: Relying on manual snapshots where automatic HA is required
**The trap:** Proposing "take frequent manual RDS snapshots" as the answer to a requirement for automatic failover with minimal downtime (low RTO).
**Why it's tempting:** Snapshots are a familiar backup mechanism and feel like a reasonable HA safety net.
**Why it's wrong:** Manual snapshot restores are slow and require human/scripted intervention — they solve durability (RPO/backup), not availability (RTO); Multi-AZ deployments provide automatic, fast failover instead.
**The correct mental model:** Snapshots/backups answer "how do we not lose data"; Multi-AZ/automatic failover answers "how do we stay up" — match the keyword (durability vs. availability) to the mechanism.

### Trap 9: Wrong S3 storage class for the access/retrieval pattern
**The trap:** Picking S3 Glacier Deep Archive for data that needs occasional access within minutes, or picking S3 Standard for logs accessed once a year.
**Why it's tempting:** "Cheapest storage" sounds universally correct for infrequently accessed data, and "durable/available" sounds universally correct when access time isn't read carefully.
**Why it's wrong:** Each class trades cost against retrieval latency and minimum storage duration: S3 Standard-IA/One Zone-IA (accessed monthly, millisecond retrieval, resilience differs), Glacier Instant Retrieval (quarterly access, milliseconds), Glacier Flexible Retrieval (minutes-to-hours), Glacier Deep Archive (12+ hours, cheapest, for rarely-touched archives).
**The correct mental model:** Match retrieval-time and access-frequency wording in the question precisely to a storage class — don't optimize for cost alone.

### Trap 10: Treating Security Groups and NACLs as interchangeable
**The trap:** Using a Network ACL to solve a problem that only needs a security group rule (or vice versa), or forgetting NACLs are stateless.
**Why it's tempting:** Both "filter traffic in a VPC," so they seem like two names for the same tool.
**Why it's wrong:** Security groups are stateful (return traffic auto-allowed) and instance-level, allow-only; NACLs are stateless (you must explicitly allow both directions) and subnet-level, supporting explicit deny rules.
**The correct mental model:** Need to explicitly block a specific IP/CIDR at the subnet boundary → NACL (remember the return-traffic rule); everything else, default to security groups.

### Trap 11: SQS Standard queue where strict ordering/exactly-once is required
**The trap:** Using a default SQS Standard queue for a workload description that says "messages must be processed in the exact order sent" or "no duplicate processing allowed."
**Why it's tempting:** Standard queues are the default SQS option and support nearly unlimited throughput, so they seem like the safe general-purpose choice.
**Why it's wrong:** Standard queues offer best-effort ordering and at-least-once delivery (duplicates possible); only FIFO queues guarantee strict order and exactly-once processing, at a lower throughput ceiling (unless using high-throughput mode).
**The correct mental model:** "Order matters" or "no duplicates" in the question → FIFO queue; otherwise Standard queue for max throughput.

### Trap 12: Scaling vertically to meet an elasticity/HA requirement
**The trap:** Answering "resize the EC2 instance to a larger type" when the scenario asks for handling variable/unpredictable load or improving fault tolerance.
**Why it's tempting:** A bigger instance is the most direct-sounding fix for "not enough capacity."
**Why it's wrong:** Vertical scaling requires downtime to resize, has a ceiling, and does nothing for redundancy across failures; horizontal scaling (Auto Scaling Group across multiple AZs) provides both elasticity and fault tolerance.
**The correct mental model:** "Variable load," "high availability," or "handle traffic spikes" → horizontal scaling (ASG + multiple AZs), not a bigger single instance.

### Trap 13: Low-cardinality DynamoDB partition key causing hot partitions
**The trap:** Choosing an attribute like "status" (few possible values) or "date" as the DynamoDB partition key for a high-traffic table.
**Why it's tempting:** These attributes are often the most natural query filter, so they seem like an obvious key choice.
**Why it's wrong:** Low-cardinality keys concentrate reads/writes onto a small number of partitions, causing throttling even when overall table capacity is sufficient — DynamoDB scales by spreading load across many distinct partition key values.
**The correct mental model:** Pick high-cardinality, evenly-accessed attributes (e.g., userId, deviceId) as partition keys; use sort keys or GSIs for range/date-based queries.

### Trap 14: Sharing IAM user credentials across accounts instead of role assumption
**The trap:** Creating an IAM user in Account A and handing out its access keys to Account B so it can access resources, instead of using cross-account IAM roles.
**Why it's tempting:** Creating a user and sharing a key feels like the simplest "give them access" solution.
**Why it's wrong:** It creates long-lived, hard-to-rotate, hard-to-audit shared secrets and violates least-privilege/temporary-credential best practice that the exam consistently tests.
**The correct mental model:** Cross-account access = IAM role with a trust policy + `sts:AssumeRole`, granting short-lived, auditable temporary credentials — never shared long-term keys.

### Trap 15: Assuming an IAM policy alone grants access to a KMS-encrypted resource
**The trap:** Attaching an IAM policy that allows `s3:GetObject` (or similar) and expecting that to be sufficient when the object is encrypted with a customer-managed KMS key.
**Why it's tempting:** IAM policies are usually described as the single source of truth for "can this principal do this action."
**Why it's wrong:** Access to a CMK-encrypted resource requires both the resource-action permission AND permission on the KMS key itself (via key policy and/or IAM policy for `kms:Decrypt`) — missing either one causes access denied.
**The correct mental model:** Encrypted-resource access is a two-gate check: IAM/resource policy for the action AND the KMS key policy/grant for the key.

### Trap 16: Assuming a bucket policy alone secures objects if Block Public Access is off
**The trap:** Writing a restrictive S3 bucket policy and assuming the bucket is private, without checking S3 Block Public Access settings or legacy object ACLs.
**Why it's tempting:** A bucket policy denying public access looks like it should be the final word on access control.
**Why it's wrong:** Individual object ACLs or a misconfigured/overridden bucket policy can still expose data if Block Public Access is disabled; BPA is the account/bucket-level safety net that overrides looser policies/ACLs.
**The correct mental model:** For guaranteed private buckets, enable S3 Block Public Access (ideally at the account level) rather than relying solely on policy wording.

### Trap 17: Wrong EC2 placement group type for the stated goal
**The trap:** Using a Cluster placement group for "high availability across failures" or a Spread placement group for "lowest possible inter-instance network latency."
**Why it's tempting:** All three placement group types sound like generic "performance/availability" tuning knobs.
**Why it's wrong:** Cluster groups pack instances in one AZ for low latency/high throughput but increase correlated-failure risk; Spread groups place a small number of critical instances on distinct underlying hardware for max fault isolation; Partition groups isolate groups of instances (e.g., Hadoop/Kafka nodes) across racks for large distributed workloads.
**The correct mental model:** Low latency & don't care about blast radius → Cluster; a handful of critical, isolated instances → Spread; large distributed/big-data workload → Partition.

### Trap 18: Using Spot Instances for stateful, interruption-intolerant workloads
**The trap:** Recommending Spot Instances to cut costs for a primary database, a single-instance critical service, or any workload with no tolerance for sudden termination.
**Why it's tempting:** Spot's steep discount makes it look like an automatic "reduce cost" answer.
**Why it's wrong:** Spot capacity can be reclaimed by AWS with only a two-minute warning, which is unacceptable for stateful/critical/non-fault-tolerant workloads; it's designed for flexible, interruption-tolerant, distributed jobs (batch, CI, stateless workers).
**The correct mental model:** Spot = "cheap but can vanish anytime" → only for fault-tolerant/stateless/flexible workloads, never for the one thing that must always be up.

### Trap 19: Reserved Instances/Savings Plans for unpredictable or short-term workloads
**The trap:** Recommending 1- or 3-year Reserved Instances or Savings Plans to reduce cost for a workload whose usage pattern is spiky, temporary, or not yet well understood.
**Why it's tempting:** RIs/Savings Plans are the "save money on compute" go-to answer whenever cost optimization is mentioned.
**Why it's wrong:** They require a long commitment against steady-state usage; committing to unpredictable or short-lived workloads risks paying for unused capacity — On-Demand or Spot fits better there.
**The correct mental model:** Match the commitment to usage predictability: steady, known baseline → RI/Savings Plan; unpredictable/short-term → On-Demand; flexible/interruptible → Spot.

### Trap 20: Direct Connect vs. Site-to-Site VPN mismatch
**The trap:** Recommending a Site-to-Site VPN when the requirement is "consistent, dedicated low-latency bandwidth," or recommending Direct Connect for "quick to set up, encrypted-by-default connectivity."
**Why it's tempting:** Both connect on-premises networks to a VPC, so they read as interchangeable "hybrid connectivity" answers.
**Why it's wrong:** VPN runs over the public internet (variable latency, but encrypted and fast to provision) while Direct Connect is a dedicated physical/private link (consistent low-latency, high bandwidth, but not encrypted by default and slower to provision — weeks); DX + VPN can be combined for private + encrypted.
**The correct mental model:** "Consistent/dedicated/high bandwidth" → Direct Connect; "quick, encrypted, lower cost" → Site-to-Site VPN; "both" → DX with VPN overlay.

### Trap 21: Mistaking Multi-AZ for disaster recovery across regions
**The trap:** Believing a Multi-AZ deployment satisfies a disaster-recovery requirement that specifies surviving a full region outage.
**Why it's tempting:** Multi-AZ already involves "multiple locations," so it feels like it should cover any large-scale disaster.
**Why it's wrong:** AZs are physically separate but still within a single AWS Region; a region-wide event (or the exam's DR scenario) requires resources replicated to a second Region (cross-Region read replicas/replication, backups, or a full DR strategy like pilot light/warm standby).
**The correct mental model:** Multi-AZ protects against AZ/data-center failure; only a multi-Region design protects against Region-level disasters.

### Trap 22: Forgetting Elastic IPs (and public IPv4 addresses generally) are not free
**The trap:** Assuming an Elastic IP is a free "static IP for AWS," including when it's unattached or attached to a stopped instance.
**Why it's tempting:** EIPs are commonly introduced as a free-feeling convenience for keeping a stable public IP.
**Why it's wrong:** AWS has always charged for EIPs that are allocated but unattached, or attached to a stopped instance, to discourage IP hoarding. In addition, since February 2024 AWS charges an hourly fee for every public IPv4 address — including Elastic IPs attached to a running instance — so there is no longer a scenario where a public IPv4/EIP is simply "free."
**The correct mental model:** Treat every public IPv4 address (Elastic IP or otherwise) as carrying a small ongoing charge; release any EIP you're not actively using rather than assuming attachment to a running resource makes it free.

### Trap 23: Wrong Auto Scaling policy type for the load pattern
**The trap:** Using scheduled scaling for unpredictable, bursty traffic, or using only dynamic/target-tracking scaling for a known, recurring traffic pattern (e.g., daily 9am batch job).
**Why it's tempting:** Both are "Auto Scaling policies," so it's easy to reach for whichever one you remember first.
**Why it's wrong:** Scheduled scaling only reacts to time-based patterns you already know about and can't respond to surprise spikes; dynamic/target-tracking scaling reacts to real-time metrics but has some lag, which underperforms against a known, sudden recurring spike compared to pre-scaling on a schedule.
**The correct mental model:** Known recurring pattern → scheduled scaling (or predictive scaling); unknown/variable pattern → dynamic/target-tracking scaling; combine both when a workload has a known baseline plus unpredictable variance.

### Trap 24: SNS vs. SQS role confusion
**The trap:** Using SNS to decouple a single producer from a single, ordered work queue, or using SQS to broadcast one event to many independent subscribers.
**Why it's tempting:** Both are "messaging services" that appear together constantly, so their roles blur.
**Why it's wrong:** SNS is pub/sub — it pushes one message to many subscribers (fan-out) and doesn't retain/queue messages for a single consumer to process at its own pace; SQS is a durable point-to-point queue where messages are pulled and processed (and can be deleted) by consumers, ideal for decoupling and buffering work.
**The correct mental model:** "Notify many subscribers/fan-out" → SNS; "buffer/decouple work for one or more pollers to process" → SQS (often combined: SNS fan-out to multiple SQS queues).

### Trap 25: Assuming VPC Peering is transitive
**The trap:** Expecting that if VPC A is peered with VPC B, and VPC B is peered with VPC C, then A can automatically reach C through B.
**Why it's tempting:** "Peering" sounds like it should create one connected mesh network, similar to how routing normally works.
**Why it's wrong:** VPC Peering connections are explicitly non-transitive — each peering relationship only connects the two VPCs directly involved, with no pass-through routing, no matter how the route tables are configured.
**The correct mental model:** Need multiple VPCs to route through each other or a hub-and-spoke topology → use a Transit Gateway, not chained VPC Peering.

---

### Trap 26: SQS Standard vs FIFO for "exactly-once, ordered" requirements
**The trap:** A scenario says messages must be processed in the exact order they were sent, and the answer choices include a default SQS Standard queue plus some batching logic.
**Why it's tempting:** SQS is the go-to "decoupling queue" service, so test-takers pick it without checking the ordering guarantee.
**Why it's wrong:** Standard queues offer at-least-once delivery and best-effort ordering only — messages can arrive out of order or be duplicated; you'd need custom dedup/sequencing logic to compensate.
**The correct mental model:** If the requirement says "strict order" or "exactly-once," the answer is an SQS FIFO queue (with message group ID), not Standard plus workarounds.

### Trap 27: SNS fan-out vs SQS point-to-point
**The trap:** A design needs one event (e.g., an order placed) to trigger multiple independent downstream systems, and SQS alone is offered as the messaging layer.
**Why it's tempting:** SQS is familiar and "queues connect services," so it seems reusable for any messaging need.
**Why it's wrong:** A single SQS queue is consumed by one logical consumer group — it doesn't natively broadcast one message to many independent subscribers.
**The correct mental model:** One-to-many broadcast = SNS (optionally fanning out to multiple SQS queues); one-to-one work distribution = SQS.

### Trap 28: EventBridge vs SQS/SNS for content-based routing and scheduling
**The trap:** A requirement needs events routed to different targets based on event content, or run on a cron-like schedule, and the answer offers SNS topics with subscription filters as the "simplest" fix.
**Why it's tempting:** SNS filter policies can technically do basic attribute filtering, so it looks sufficient.
**Why it's wrong:** SNS filtering is limited to message attributes and lacks native scheduling, multi-source ingestion (SaaS partners, AWS service events), and rich content-based pattern matching.
**The correct mental model:** For complex event routing rules, scheduled triggers, or third-party SaaS event integration, choose EventBridge; use SNS for simple pub/sub fan-out.

### Trap 29: SQS visibility timeout too short
**The trap:** A queue is processing slow jobs (e.g., 10-minute video transcoding) but the visibility timeout is left at the default (30s), and the question asks why messages are being processed multiple times.
**Why it's tempting:** Test-takers assume duplicate processing means a code bug or missing dedup logic.
**Why it's wrong:** If the visibility timeout is shorter than actual processing time, SQS makes the message visible again before the first consumer finishes, causing a second consumer to pick it up.
**The correct mental model:** Visibility timeout must exceed your worst-case processing time (or use heartbeats/ChangeMessageVisibility) — duplicate processing is often a timeout misconfiguration, not an architecture flaw.

### Trap 30: DynamoDB Provisioned vs On-Demand capacity mode
**The trap:** A workload has unpredictable, spiky traffic, and the answer choices push you toward "provisioned capacity with Auto Scaling" as the modern best practice.
**Why it's tempting:** Provisioned + Auto Scaling sounds like the "properly engineered" answer versus the seemingly lazy on-demand option.
**Why it's wrong:** Provisioned Auto Scaling reacts to sustained CloudWatch alarms with a lag, so sudden spiky/unpredictable traffic can throttle before capacity adjusts.
**The correct mental model:** Unpredictable/spiky traffic with unknown patterns → DynamoDB On-Demand; steady, predictable traffic where cost optimization matters → Provisioned with Auto Scaling.

### Trap 31: DynamoDB hot partition despite "enough" table throughput
**The trap:** A table has generous provisioned RCU/WCU overall, but requests still throttle, and the fix offered is simply "increase provisioned capacity."
**Why it's tempting:** Throttling looks like a capacity-sizing problem, so adding more capacity feels intuitive.
**Why it's wrong:** Throughput is distributed across partitions based on partition key; a low-cardinality or skewed partition key (or a GSI with its own separate throughput) creates a hot partition that throttles regardless of total table capacity.
**The correct mental model:** Throttling with headroom on paper means fix the partition key design (higher cardinality / write sharding) or GSI capacity, not just raise the table's overall throughput.

### Trap 32: Wrong S3 storage class for the access pattern
**The trap:** A scenario describes infrequently accessed but resilience-critical data, and "S3 One Zone-IA" is offered as the cost-optimized answer.
**Why it's tempting:** One Zone-IA is cheaper than Standard-IA, matching the "cost optimization" keyword in the question.
**Why it's wrong:** One Zone-IA has no cross-AZ redundancy, so it fails any requirement implying durability/availability across AZ failure.
**The correct mental model:** Only pick One Zone-IA for easily-recreatable, non-critical data; anything requiring AZ-level resilience needs Standard-IA or above.

### Trap 33: S3 Glacier retrieval tier vs RTO requirement
**The trap:** Data is archived to Glacier Deep Archive for cost savings, but the recovery scenario needs data back within a few hours.
**Why it's tempting:** Deep Archive is the cheapest tier, so it seems like the obvious "lowest cost" archive choice.
**Why it's wrong:** Glacier Deep Archive standard retrieval takes up to 12 hours (bulk retrieval up to 48 hours), which can blow past a tight RTO.
**The correct mental model:** Match the Glacier tier and retrieval speed (Expedited/Standard/Bulk) to the stated RTO, not just to minimizing storage cost.

### Trap 34: Forgetting KMS key policy is required in addition to IAM policy
**The trap:** A cross-account (or even same-account) user has an IAM policy granting `kms:Decrypt`, but they still get access denied, and the fix offered is "grant broader IAM permissions."
**Why it's tempting:** For most AWS resources, IAM policy alone is sufficient, so it's natural to assume the same for KMS.
**Why it's wrong:** KMS keys are a special case — the key's resource-based key policy must also explicitly allow the principal (or delegate to IAM policies via the default key policy), otherwise IAM permissions alone are ignored.
**The correct mental model:** KMS access requires the "AND" of both the IAM policy AND the key policy (or a grant) — fixing only one side won't resolve access-denied errors.

### Trap 35: KMS grants vs key policy edits for temporary access
**The trap:** An application needs to programmatically and temporarily delegate decrypt access to another service/role, and the proposed fix is editing the key policy each time.
**Why it's tempting:** Key policy is the "official" access control mechanism, so modifying it feels correct.
**Why it's wrong:** Editing key policies for frequent, temporary, or programmatic delegation is slow, error-prone, and not designed for that use case.
**The correct mental model:** Use KMS grants for temporary, programmatic, fine-grained permission delegation; reserve key policy edits for durable, administrative access changes.

### Trap 36: Auto Scaling cooldown period blocking rapid response
**The trap:** An ASG scaling policy is correctly configured, but during a traffic spike it "won't scale again," and instances stay under-provisioned.
**Why it's tempting:** It looks like a broken scaling policy or wrong CloudWatch alarm threshold.
**Why it's wrong:** The default cooldown period prevents additional scaling activities from triggering immediately after a previous one, which can stall response to rapidly escalating load.
**The correct mental model:** Cooldown (or target-tracking's built-in fast-scale-out logic) governs pacing of scaling actions — tune it or use target tracking (which handles this more gracefully) instead of assuming the policy itself is broken.

### Trap 37: Step scaling vs target tracking for "simplest self-adjusting" requirement
**The trap:** A question asks for the scaling method requiring the least ongoing management to keep a metric (like CPU) near a target, and answers offer "step scaling with multiple CloudWatch alarms" as thorough/robust.
**Why it's tempting:** Step scaling with finely tuned thresholds looks more "engineered" and precise.
**Why it's wrong:** Step scaling requires manually defining and maintaining multiple alarm thresholds and adjustment steps — more operational overhead, not less.
**The correct mental model:** When the goal is "maintain a target metric with minimal management," choose Target Tracking scaling, not step scaling.

### Trap 38: Health check grace period too short in Auto Scaling
**The trap:** New instances with a slow bootstrap (long user-data script, JVM warm-up) get terminated and replaced repeatedly, and the fix offered is "increase instance size."
**Why it's tempting:** Instance churn looks like a performance/sizing issue.
**Why it's wrong:** If the ASG health check grace period is shorter than the app's actual startup time, ASG marks the instance unhealthy and replaces it before it ever finishes initializing — a loop unrelated to instance size.
**The correct mental model:** Grace period must cover full application startup time; churning "unhealthy" new instances is usually a grace-period misconfiguration, not a capacity problem.

### Trap 39: Route 53 Weighted vs Latency-based routing
**The trap:** A scenario wants users routed to the endpoint that gives them the best performance, and "Weighted routing with a 50/50 split" is offered as the answer.
**Why it's tempting:** Weighted routing is common and simple, so it feels like a safe general-purpose choice.
**Why it's wrong:** Weighted routing distributes traffic by a fixed proportion regardless of user location or actual network performance — it doesn't optimize for latency.
**The correct mental model:** "Best performance for the user" → Latency-based routing; "controlled traffic split for testing/migration" → Weighted routing.

### Trap 40: Route 53 Failover vs Multi-Value Answer confusion
**The trap:** A requirement needs simple DNS-level load distribution across several healthy endpoints (not strict active/passive), and "Failover routing" is offered as the resilience answer.
**Why it's tempting:** Failover routing sounds inherently "highly available," matching resilience keywords in the question.
**Why it's wrong:** Failover routing is strictly active/passive (primary/secondary) — it doesn't distribute load across multiple simultaneously active healthy records.
**The correct mental model:** Active/passive DR failover → Failover routing policy; simple client-side load distribution across multiple healthy IPs → Multi-Value Answer routing (not a substitute for a real load balancer).

### Trap 41: Full-mesh VPC Peering instead of Transit Gateway at scale
**The trap:** A company needs to connect a growing number of VPCs (10+) across accounts/regions, and the proposed design is "just add more VPC Peering connections between each pair."
**Why it's tempting:** Peering is simpler and cheaper per-connection than deploying a Transit Gateway, so it looks fine for "a few more VPCs."
**Why it's wrong:** VPC Peering connections scale as O(n²) pairs and each must be individually configured/routed, becoming unmanageable and hitting peering limits as VPC count grows.
**The correct mental model:** A handful of VPCs → VPC Peering is fine; many VPCs / hub-and-spoke / cross-region at scale → Transit Gateway.

### Trap 42: VPC Peering non-transitivity trap
**The trap:** VPC A is peered with VPC B, and VPC B is peered with VPC C, and the design assumes A can now reach C through B.
**Why it's tempting:** It seems logical that peering "chains" like transitive network routes.
**Why it's wrong:** VPC Peering is explicitly non-transitive — A cannot route to C just because both are peered with B; a direct A-C peering (or Transit Gateway) is required.
**The correct mental model:** Peering connections never transit through an intermediate VPC — each pair needing connectivity must be directly peered, or use Transit Gateway instead.

### Trap 43: Direct Connect vs Site-to-Site VPN for setup speed and consistency trade-off
**The trap:** A requirement asks for a solution to be set up "quickly" for a hybrid connection, and "Direct Connect" is offered as the premium/best answer.
**Why it's tempting:** Direct Connect is the "enterprise-grade" answer test-takers associate with best hybrid connectivity.
**Why it's wrong:** Direct Connect provisioning typically takes weeks to months (physical cross-connects, carrier coordination) — it fails any "quick" or "immediate" setup requirement.
**The correct mental model:** Need it fast/cheap and can tolerate internet-based variability → Site-to-Site VPN; need consistent, high-bandwidth, low-latency dedicated connectivity and have lead time → Direct Connect.

### Trap 44: Single Direct Connect connection presented as "highly resilient"
**The trap:** A design uses one Direct Connect connection to one AWS Direct Connect location and claims high availability for a critical hybrid workload.
**Why it's tempting:** Direct Connect already sounds more robust than a VPN, so a single connection feels "good enough."
**Why it's wrong:** A single DX connection (or even a single DX location) is a single point of failure for fiber cuts, hardware failure, or location outages.
**The correct mental model:** True DX resiliency requires redundant connections across multiple DX locations/devices, or a Direct Connect + VPN failover combination — one connection alone is not highly available.

### Trap 45: Reserved Instances vs Savings Plans for flexibility
**The trap:** A workload's instance family/region/OS may change over time, but "Standard Reserved Instances" is offered as the best cost-optimization answer because it has the deepest discount on paper.
**Why it's tempting:** RIs advertise the largest headline discount percentage, which seems like the obvious cost winner.
**Why it's wrong:** Standard RIs lock you into a specific instance family/region, so if the workload shifts (e.g., different instance type or region), you lose the discount value or must trade/exchange (Convertible RI only).
**The correct mental model:** Need flexibility across instance family, size, OS, and region while still saving cost → Savings Plans (or Convertible RIs); need max discount for a fixed, unchanging instance configuration → Standard RIs.

### Trap 46: Spot Instances for stateful or long-running critical workloads
**The trap:** A cost-optimization question suggests running a stateful database or a long, uninterruptible batch job on Spot Instances to cut cost.
**Why it's tempting:** Spot offers the biggest discount, and "cost optimization" keywords push toward the cheapest compute option.
**Why it's wrong:** Spot Instances can be reclaimed with only a two-minute interruption notice, which risks data loss or job failure for stateful/non-checkpointed or non-fault-tolerant workloads.
**The correct mental model:** Spot is for fault-tolerant, interruptible, stateless workloads (batch, CI, stateless web tiers); stateful or uninterruptible workloads need On-Demand, Reserved, or Savings Plans coverage.

### Trap 47: RDS Read Replica cross-region promotion vs Aurora Global Database
**The trap:** A scenario needs sub-minute RPO/RTO failover to another region, and "RDS (MySQL/PostgreSQL) cross-region read replica" is offered as the DR solution.
**Why it's tempting:** Cross-region read replicas already exist in the architecture and sound like a ready-made DR mechanism.
**Why it's wrong:** Promoting a standard RDS cross-region read replica to a standalone primary takes time and involves replication lag, which can miss tight RTO/RPO targets.
**The correct mental model:** For fast (typically under a minute), low-lag cross-region failover, use Aurora Global Database's managed failover; plain cross-region read replicas are slower and lag-prone.

### Trap 48: Aurora Serverless v2 vs provisioned Aurora for intermittent workloads
**The trap:** A workload has long idle periods with occasional unpredictable bursts (e.g., a dev/test database or infrequent internal app), and "provisioned Aurora with a large instance sized for peak" is chosen to "guarantee performance."
**Why it's tempting:** Sizing for peak feels like the safe, reliable choice to avoid any performance risk.
**Why it's wrong:** Paying for a large provisioned instance around the clock for a workload that's idle most of the time wastes money — it fails the "cost-effective" requirement.
**The correct mental model:** Intermittent, unpredictable, or idle-heavy database workloads → Aurora Serverless v2 (scales capacity automatically, pay for what's used); steady, predictable high-throughput workloads → provisioned Aurora.

### Trap 49: Pilot Light chosen when RTO demands Warm Standby (or better)
**The trap:** A DR requirement states RTO of a few minutes, but the answer picks "Pilot Light" because it's cheaper and still a recognized DR pattern.
**Why it's tempting:** Pilot Light is a legitimate, well-known DR strategy, so it seems safely "correct" for any DR question.
**Why it's wrong:** Pilot Light only keeps core data/services (e.g., a replicated database) running, with the rest of the environment scaled up from AMIs/templates during an actual disaster — that scale-up takes longer than a true minutes-level RTO allows.
**The correct mental model:** Match the DR pattern to the stated RTO/RPO, in increasing order of speed (and cost): Backup & Restore is slowest and cheapest; Pilot Light is faster but still requires standing up most of the environment during a disaster; Warm Standby keeps a scaled-down copy of the full environment already running for a much quicker cutover; Multi-Site Active-Active runs at capacity in multiple sites for near-zero RTO/RPO. Pick based on the stated recovery numbers, not on cost preference alone.

### Trap 50: Backup & Restore offered when near-zero RTO/RPO is required
**The trap:** A DR requirement explicitly says "near-zero downtime and data loss," but the proposed (cheapest) solution is scheduled backups to another region restored on demand.
**Why it's tempting:** Backup & Restore is the cheapest DR option and "DR" keywords make it seem like a valid catch-all answer.
**Why it's wrong:** Backup & Restore requires provisioning infrastructure and restoring data from backups during an actual event, incurring hours of downtime and potential data loss since the last backup — nowhere near "zero."
**The correct mental model:** "Near-zero RTO/RPO" always points to Multi-Site Active-Active (or at minimum Warm Standby); Backup & Restore is reserved only for scenarios where extended downtime is explicitly acceptable.
