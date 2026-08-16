# AWS SAA-C03: Compute & Scaling Mastery

## EC2 Instance Families (Selection Logic, Not Specs)

Don't memorize vCPU/RAM tables — the exam tests *which family class* fits a workload signature:

- **General purpose (M, T)**: balanced CPU:RAM ratio. T-family is burstable (CPU credits) — exam distractor: T instances that sustain high CPU exhaust credits and throttle unless `Unlimited` mode is enabled. If a question mentions "unpredictable bursty traffic that occasionally sustains high CPU," the trap answer is a plain T-instance without unlimited mode.
- **Compute optimized (C)**: high CPU:RAM ratio — batch processing, gaming servers, scientific modeling, media transcoding.
- **Memory optimized (R, X, z1d)**: in-memory DBs, SAP HANA, real-time big data analytics. z1d = high frequency + memory, used for licensing-sensitive high single-thread performance workloads.
- **Storage optimized (I, D, H)**: high sequential/random I/O — NoSQL DBs, data warehousing, distributed file systems. Trigger phrase "high IOPS local storage" → storage-optimized + instance store, not EBS.
- **Accelerated computing (P, G, Inf, Trn)**: GPU/ML training vs inference — Trn (training) vs Inf (inference) is a real exam distinction now.

**Decision boundary the exam wants**: workload *characteristic* (CPU-bound, memory-bound, IOPS-bound, burstable) → family class. Never the specific instance size.

## EC2 Purchasing Options

| Option | When to choose | Exam trigger words |
|---|---|---|
| **On-Demand** | Short-term, spiky, unpredictable, first-time workloads, can't tolerate interruption | "unpredictable," "short-term," "no long-term commitment" |
| **Reserved Instances (Standard)** | Steady-state, known workload for 1–3 years, want max discount. Commitment is to a specific instance type in a region (regional RIs get instance-*size* flexibility within the same family, not a full family swap), or to a specific instance type in a specific AZ if zonal | "steady-state," "predictable," "1 or 3 year commitment," "highest discount for a specific instance type" |
| **Reserved Instances (Convertible)** | Steady-state but need flexibility to change instance family over the term | "may need to change instance type later" |
| **Savings Plans (Compute SP)** | Steady baseline spend across EC2 (any family/region/OS/tenancy) + Fargate + Lambda, want flexibility over discount | "flexibility across instance families, regions, or compute services" — this is the modern default answer over RIs when flexibility is mentioned |
| **Savings Plans (EC2 Instance SP)** | Steady-state, locked to a specific instance family in a region, want the highest possible discount | "highest savings," "committed to specific family" |
| **Spot** | Fault-tolerant, stateless, flexible-timing workloads (batch, CI/CD, big data, rendering); up to ~90% discount but can be reclaimed with a 2-minute interruption notice | "fault-tolerant," "flexible start/end time," "can be interrupted," "significant cost savings" — never for stateful/order-sensitive workloads unless checkpointing is described |
| **Dedicated Instances** | Compliance requires instance-level tenancy isolation, no visibility into physical host needed | "isolated at the instance level" |
| **Dedicated Hosts** | BYOL licensing tied to physical sockets/cores, need visibility/control of host placement, server-bound software licenses | "socket," "core," "BYOL," "license tied to physical hardware" — this is the giveaway distinguishing Hosts from Instances |

**Common distractor**: a question describing license compliance tied to physical cores → answer is Dedicated **Host**, not Dedicated **Instance** (Instance gives tenancy isolation only, not hardware visibility).

**Spot resilience pattern**: combine Spot with ASG **mixed instances policy** + multiple instance types/AZs, using allocation strategy `capacity-optimized` (lowest interruption rate) or `price-capacity-optimized` — the current recommended default. `lowest-price` is a legacy distractor that increases interruption risk.

## Placement Groups

- **Cluster**: single AZ, low-latency/high-throughput network performance (HPC, tightly-coupled node-to-node traffic). Trade-off: correlated hardware failure risk — an entire cluster placement group can go down together.
- **Spread**: instances placed on distinct underlying hardware, max limited to a small number of instances per AZ (7 per AZ). Use for small numbers of critical instances that must not share failure domains (e.g., a handful of leader/quorum nodes).
- **Partition**: instances grouped into partitions, each on separate racks with separate power/network — for large distributed systems (HDFS, HBase, Cassandra, Kafka) that need rack-awareness at scale, across multiple AZs.

**Exam boundary**: "low latency between instances" → Cluster. "Avoid simultaneous failure of a small number of critical instances" → Spread. "Large-scale distributed data system with rack-aware replication" → Partition.

## Elastic Network Interfaces (ENI)

- Attach/detach independently of instance lifecycle — used for **failover patterns**: pre-configure a secondary ENI with a static private IP, and on primary instance failure, detach and reattach to a standby instance to preserve IP/MAC without touching DNS.
- Security groups, source/dest check, and MAC address travel with the ENI, not the instance — relevant for software licensing tied to MAC.
- Don't confuse with **Enhanced Networking (ENA/EFA)** — that's about throughput/PPS, not identity/failover. EFA specifically appears for HPC/tightly-coupled MPI workloads on Cluster Placement Groups.

## AMI

- Region-scoped; must **copy** an AMI to use it in another region (relevant for DR/multi-region designs).
- **Golden AMI pattern**: bake dependencies/config into the AMI to minimize boot-time work → faster ASG scale-out, more consistent fleet. This is the "high-performing/resilient architecture" answer when a question complains about slow instance launch times during scale-out.
- Trade-off vs **user data**: golden AMI = fast launch, harder to update (must rebuild + roll new AMI via ASG instance refresh); user data = flexible/always fresh, but slower boot. Exam often pairs this with an instance refresh or Image Builder pipeline for automation.

## User Data

- Executes once at first boot (as root, base64-encoded under the hood) — used for bootstrapping (installing agents, pulling config, joining a cluster).
- Not a secrets-delivery mechanism from a security-domain standpoint — sensitive values belong in Secrets Manager/SSM Parameter Store fetched at boot, not hardcoded in user data (user data is readable in plaintext by anyone with shell access to the instance via the Instance Metadata Service, and separately by anyone with IAM permission to call `DescribeInstanceAttribute` via the API — it is not a protected secret store either way).

## Instance Store vs EBS

| | Instance Store | EBS |
|---|---|---|
| Persistence | Ephemeral — lost on stop, terminate, or underlying hardware failure | Persistent, survives stop/terminate (unless configured to delete on termination) |
| Performance | Very high IOPS, physically attached | Network-attached, gp3/io2 tunable IOPS |
| Use case | Cache, buffer, scratch space, temporary processing, replicated/shardable data (e.g., a Kafka broker's local log with replication) | Boot volumes, databases, anything requiring durability |
| Exam trigger | "temporary," "cache," "buffer," "data will be regenerated" | "must persist," "durable," "survive instance stop" |

**Distractor pattern**: a question emphasizing "extremely high IOPS" tempts you toward instance store, but if it also says "data must survive a reboot/stop," the correct answer is EBS io2 (or io2 Block Express), not instance store — durability requirement overrides IOPS requirement.

---

## Auto Scaling Groups

### Scaling Policies

- **Target tracking**: default/simplest — pick a metric (e.g., average CPU, ALB request count per target, or a custom CloudWatch metric) and a target value; ASG manages the math. This is the exam's default correct answer whenever the scenario doesn't demand fine-grained control.
- **Step scaling**: define multiple scaling adjustments based on the *magnitude* of alarm breach (e.g., +1 instance if CPU 50–70%, +3 if CPU >70%). Choose when target tracking's single-target model is too coarse and load spikes vary in severity.
- **Scheduled scaling**: known, calendar-predictable load (start of business day, batch windows). Often paired with target tracking as a "floor" — schedule sets minimum capacity ahead of a known spike, target tracking handles the rest.
- **Predictive scaling**: ML-based forecast of daily/weekly patterns, pre-provisions ahead of predicted load. Relevant when the scenario says "recurring daily pattern" and wants scaling *ahead of* demand rather than reactively — this is the differentiator vs. scheduled (predictive learns the pattern; scheduled requires you to know and hardcode it).

**Cooldown**: applies to step/simple scaling to prevent rapid-fire duplicate actions before a prior scaling activity's effect is visible in metrics; target tracking manages this internally.

### Health Checks

- Default ASG health check = **EC2 status checks only** (instance reachability). If the instance is running but the application is unhealthy (e.g., failing to respond on its port), EC2 status checks won't catch it.
- Must explicitly enable **ELB health checks** on the ASG for it to honor target group health check failures and replace instances accordingly. This is a frequent exam gotcha: "instances pass EC2 checks but ALB shows unhealthy targets, and ASG isn't replacing them" → the fix is enabling ELB health check type on the ASG, not touching the ALB.

### Warm Pools

- Pre-initialized (stopped or running) instances held outside the active ASG capacity, ready to be moved in fast. Use when instance **boot/initialization time is long** (heavy application bootstrap, large golden AMI decompression, JVM warm-up) and target-tracking reaction time isn't fast enough with cold launches. Cuts scale-out latency without the full cost of running fully active instances (stopped warm pool instances only cost EBS storage, not compute).

### Lifecycle Hooks

- Insert custom pause states: **`Pending:Wait`** (before instance enters service — run config management, register with monitoring/service discovery) and **`Terminating:Wait`** (before termination — drain connections, flush logs, deregister from external systems).
- Exam trigger: "run a custom script before an instance is put into service" or "gracefully drain connections before termination" → lifecycle hooks, not user data (user data can't pause the ASG state machine) and not simple ELB connection draining alone (that only covers deregistration delay from the target group, not custom scripts).

---

## Vertical vs Horizontal Scaling Patterns

- **Vertical (resize instance)**: requires stop/start (downtime), single point of failure remains, ceiling exists at largest instance size. Correct answer only when: single-writer relational DB bottleneck before you're ready to shard/read-replica, legacy monolith that can't be made stateless, or a stopgap before re-architecting.
- **Horizontal (add instances/nodes)**: the default correct answer across Resilient and High-Performing domains — stateless design, ASG/ELB fronting, no ceiling (within account limits), improves both scalability and availability simultaneously.
- **Exam signal**: if a question emphasizes "high availability" or "no single point of failure" alongside scaling, horizontal is virtually always correct; vertical scaling answers are usually distractors in HA-flavored questions, valid only in narrowly-scoped DB-bottleneck questions.

---

## ECS vs EKS vs Fargate Scaling Behavior

- **ECS on EC2**: two scaling layers — (1) **Service Auto Scaling** (task count, via target tracking on ECS service metrics like CPU/memory or ALB request count), and (2) **cluster capacity scaling** (the underlying EC2 ASG must also scale, ideally automated via a **Capacity Provider** with managed scaling so cluster capacity tracks task demand). Forgetting layer 2 — "tasks are stuck in PENDING despite service wanting to scale" — is a classic exam scenario pointing to insufficient cluster capacity/capacity provider misconfiguration.
- **ECS on Fargate**: only one scaling layer — task-level Service Auto Scaling. No cluster/node capacity management at all; AWS handles it. Correct answer whenever the scenario wants to **eliminate infrastructure/capacity management** for containers.
- **EKS**: mirrors Kubernetes scaling — **HPA** (Horizontal Pod Autoscaler, pod-level, metric-driven) and **VPA** (vertical, pod resource sizing) at the pod layer, plus **Cluster Autoscaler** or **Karpenter** at the node layer to add/remove EC2 capacity based on unschedulable pods. Karpenter is the current preferred/faster-provisioning answer over Cluster Autoscaler when the scenario emphasizes rapid node provisioning or bin-packing efficiency.
- **EKS on Fargate**: removes the node-scaling layer entirely (one pod = one Fargate micro-VM), same trade-off logic as ECS Fargate vs ECS EC2 — pick when operational simplicity outweighs the cost premium and Fargate's constraints (no DaemonSets, limited privileged workloads) are acceptable.

**Decision boundary**: "avoid managing servers/clusters" → Fargate (either ECS or EKS launch type). "Already standardized on Kubernetes tooling/API" → EKS over ECS regardless of Fargate/EC2 choice. "Cost-sensitive, want maximum control over instance types/Spot mixing" → EC2 launch type with Capacity Providers or Karpenter.

---

## Lambda Concurrency & Scaling Model

- Each concurrent invocation gets its own execution environment; Lambda scales horizontally per-invocation automatically, no capacity planning by default.
- **Reserved concurrency**: sets both a guaranteed and a maximum concurrency ceiling for a function — used to protect downstream systems (e.g., an RDS connection pool) from being overwhelmed by too many simultaneous Lambda executions, and to guarantee capacity isn't starved by other functions sharing the account-level pool.
- **Provisioned concurrency**: pre-initializes execution environments to eliminate cold starts — correct answer whenever the scenario mentions **latency-sensitive** synchronous invocations (e.g., API Gateway-fronted APIs) suffering from cold-start spikes, especially after a deployment or scale-out event.
- Account/region-level concurrency has a burst scaling rate before settling into a steady increase — don't cite exact numbers, but know qualitatively that a sudden massive spike in invocations can hit **throttling (429)** before scaling catches up, which is why async/event-driven sources should be buffered (see SQS pattern below) and why a Dead Letter Queue or `on-failure` destination matters for handling throttled/failed async invocations.
- **Exam distractor**: "function is throttling under sudden bursty traffic" → don't jump to "increase reserved concurrency" if the real fix is smoothing the burst via SQS/EventBridge buffering, or provisioned concurrency for cold-start-specific latency issues — pick the fix that matches the *stated symptom* (throttling from volume vs. latency from cold start).

---

## DynamoDB & Aurora Scaling

### DynamoDB

- **On-Demand mode**: unpredictable/spiky traffic, pay-per-request, zero capacity planning — correct default when workload is "new," "unpredictable," or "spiky."
- **Provisioned + Auto Scaling**: steady, predictable baseline with target-tracking on consumed capacity % — more cost-efficient at steady, well-understood volume.
- **Hot partition** is the recurring exam failure scenario: poor partition key cardinality/distribution causes throttling even when overall table capacity looks sufficient — the fix is partition key design (higher cardinality, write sharding), not just raising capacity.
- **DAX**: in-memory caching layer in front of DynamoDB for read-heavy, low-latency microsecond access patterns — the caching/scaling answer when read load (not write load) is the bottleneck.
- **Global Tables**: multi-region active-active scaling/resilience, not just DR.

### Aurora

- **Read scaling**: add Aurora Replicas (up to a documented multi-replica ceiling) behind the reader endpoint — correct answer for read-heavy relational workloads. Combine with **Aurora Auto Scaling** (replica count driven by a target metric like average CPU or connections) for variable read load.
- **Write scaling**: single primary writer in standard Aurora — vertical scaling (bigger writer instance) or offloading reads to replicas is the lever. Aurora MySQL Multi-Master (the older true multi-writer capability) has been deprecated/retired by AWS — new multi-master clusters can no longer be created and existing ones have been migrated to single-writer, so it is not a valid exam answer for write scaling even in "multi-master" sounding scenarios. Treat "scale writes" questions as vertical-scale-the-writer-or-shard/re-architect, not multi-writer Aurora.
- **Aurora Serverless v2**: variable, intermittent, or hard-to-predict workloads (dev/test, infrequent-use apps, unpredictable spiky relational traffic) — auto-scales capacity units up/down without the manual capacity planning of provisioned Aurora. Exam trigger: "database is idle most of the time but occasionally spikes" or "can't predict capacity needs" → Serverless v2.

---

## SQS as a Buffering/Scaling Pattern

- Core exam pattern: **decouple producer from consumer** to absorb traffic spikes ("load leveling") — producer writes to queue at whatever rate, consumers (EC2/ASG, ECS, Lambda) drain at a sustainable rate, protecting downstream systems (DBs, legacy APIs) from being overwhelmed.
- Consumer-side ASG scaling should target the **queue depth metric** (`ApproximateNumberOfMessagesVisible`) via a custom CloudWatch metric/target tracking policy — this is the standard "scale workers based on backlog" architecture question answer.
- Also the fix for Lambda/API throttling scenarios described above — insert SQS between the bursty producer and the rate-limited consumer.
- **FIFO** vs standard queue matters only when ordering/exactly-once is explicitly required — don't default to FIFO for pure throughput/buffering questions since it has lower throughput ceilings than standard queues.

---

## CloudFront/Caching as a Scaling Pattern

- Shifts load **off the origin entirely** for cacheable content — the highest-leverage "high-performing architecture" answer whenever a scenario describes read-heavy, geographically distributed users hitting the same content repeatedly (static assets, images, video, or even cacheable API/dynamic responses with appropriate TTL/cache-key configuration).
- Reduces the *scaling burden* on origin compute (EC2/ALB/ECS) and on origin storage/DB, meaning you can right-size origin capacity lower than raw request volume would suggest — exam framing: "reduce load on the origin" or "improve global latency" → CloudFront, not "add more origin instances."
- **API Gateway caching** is the equivalent pattern specifically for REST API responses — same logic, narrower scope.
- **ElastiCache (Redis/Memcached)** is the analogous caching-as-scaling pattern at the database tier — offloads read pressure from RDS/Aurora/DynamoDB, correct answer when the bottleneck is described as **read-heavy database load** rather than origin/edge content delivery. Distinguish from DAX: DAX is DynamoDB-specific and API-compatible; ElastiCache is general-purpose and used with relational or custom data access patterns.
- **Common distractor**: a question about global read latency might tempt "add read replicas in each region" (valid but heavier/costlier) vs. "front with CloudFront" (cheaper, simpler) — pick based on whether the content is cacheable (CloudFront) or requires live/consistent data reads (replicas/Global Tables).
