# AWS SAA-C03 Service Differentiation Matrix

*Every category below was independently technical-accuracy-audited (corrections applied) before inclusion — see `02-audit-log.md` for the list of issues the audit caught.*

## Compute

*AWS SAA-C03 — Compute Service Comparison Deep-Dive*

Scope note: this is written at decision-boundary altitude — the "which one does the exam want here" line, not a service intro. Mapped loosely against the four SAA-C03 domains (Secure 30% / Resilient 26% / Performance 24% / Cost 20%) where relevant per row.

---

### 1. EC2 vs Lambda

| Dimension | EC2 | Lambda |
|---|---|---|
| **Primary use case** | Long-running processes, stateful workloads, custom OS/kernel/network stack requirements, licensed software (BYOL), workloads needing >15 min execution, persistent in-memory caches, custom AMIs | Event-driven, short-lived, bursty/unpredictable traffic, glue logic between AWS services, microservices with sporadic invocation, cron-like scheduled jobs via EventBridge |
| **Scalability** | Horizontal via Auto Scaling Groups (ASG) — scales in minutes (boot time + warm-up), needs launch template/AMI baked or bootstrap via user data | Scales per-request automatically, near-instant (subject to concurrency limits & cold starts); scales to zero when idle |
| **Availability** | You engineer it: multi-AZ ASG + ELB. No inherent HA — a single instance is a single point of failure | Inherently multi-AZ within a region, managed by AWS — no ASG/ELB design needed |
| **Latency** | Consistent, predictable — no cold start once warm; better for latency-sensitive, sustained traffic | Cold start latency (function init, VPC attachment adds ENI latency historically — largely mitigated now via Hyperplane ENIs, but still a factor with large deployment packages or SnapStart-eligible runtime absence); unpredictable tail latency under low-frequency invocation |
| **Operational overhead** | High — patch OS, manage AMIs, configure ASG/health checks, SSM patch baselines, agent management | Near-zero — no OS/runtime patching (AWS patches the execution environment), no capacity planning |
| **Pricing characteristics** | Pay for provisioned capacity regardless of utilization (unless using Spot); rate quoted per instance-hour, billed per-second (60-second minimum) | Pay-per-invocation + duration (ms) + memory allocated; no charge when idle — but can exceed EC2 cost at sustained high-volume/steady-state traffic |
| **Encryption/security notes** | You own IAM instance profile scoping, security groups, NACLs, OS-level hardening, EBS encryption (KMS) | Execution role (IAM) scoped per-function is the primary boundary; environment variables encrypted via KMS; VPC access optional (adds ENI overhead); no OS to harden — smaller attack surface but shared responsibility shifts further to AWS |
| **Limitations** | You manage patching cadence, scaling lag, capacity headroom | Max execution timeout (15 min), deployment package size limits, ephemeral storage cap (/tmp), concurrency throttling (regional + reserved/provisioned concurrency), not ideal for long-lived DB connections (needs RDS Proxy) |
| **Exam trigger words** | "custom AMI," "specific OS/kernel version," "licensed software requiring dedicated hardware," "long-running batch >15 minutes," "persistent connection," "full control over the environment" | "event-driven," "S3 upload trigger," "serverless," "no servers to manage," "sporadic/unpredictable traffic," "pay only when code runs," "process each file as it arrives" |
| **Common exam traps** | Distractor: EC2 chosen for "cost savings on infrequent small tasks" — wrong, idle EC2 still bills. Trap: assuming EC2 auto-scales fast enough for sub-second bursts — it doesn't, Lambda does | Distractor: Lambda for workloads >15 min (invalid — must re-architect to Step Functions or Fargate/EC2). Trap: Lambda in VPC needing NAT Gateway for internet access — often missed cost/complexity add. Trap: assuming Lambda is "always cheaper" — high-sustained-throughput workloads flip the cost curve toward EC2/Fargate |

---

### 2. EC2 vs ECS

Note: this is really "EC2 (self-managed compute) vs ECS (container orchestration control plane)" — apples-to-oranges, but the exam frames it as "when do you containerize/orchestrate vs just run instances."

| Dimension | EC2 (standalone/ASG) | ECS |
|---|---|---|
| **Primary use case** | Monolithic apps, apps needing full OS access, non-containerized legacy workloads, custom kernel modules | Containerized microservices needing orchestration — scheduling, service discovery, rolling deployments, task placement across a cluster |
| **Scalability** | ASG scales instances; each instance = one unit of scaling (coarse-grained) | ECS Service Auto Scaling scales **tasks** (fine-grained) independently of underlying capacity; can bin-pack multiple containers per instance for density |
| **Availability** | Multi-AZ via ASG + ELB, self-designed | Multi-AZ task placement built into ECS scheduler; integrates natively with ALB/NLB target groups per service |
| **Latency** | Predictable, no orchestration layer overhead | Slight scheduling/placement latency for task startup; otherwise same network performance as underlying EC2/Fargate |
| **Operational overhead** | Full instance lifecycle management, no orchestration awareness (unless you build your own) | Cluster/task-definition management; still need to manage EC2 capacity if using EC2 launch type (ECS agent, AMI, patching) — Fargate removes this entirely (see §4) |
| **Pricing characteristics** | Pay for EC2 instances only | Control plane is free; you pay only for underlying compute (EC2 or Fargate) — ECS itself has no additional charge |
| **Encryption/security notes** | Standard EC2 IAM instance profile model | Task IAM role assigned per task definition (finer-grained than an instance profile shared across everything on a host, though all containers within one task share that same task role); awsvpc networking mode gives each task its own ENI/security group |
| **Limitations** | No native container orchestration, service discovery, or rolling deployment primitives — must build manually | AWS-proprietary orchestrator (not portable like Kubernetes); fewer third-party ecosystem tools than EKS |
| **Exam trigger words** | "run a legacy application," "requires full control of the OS" | "containerized application," "Docker," "microservices architecture," "task definition," "AWS-native container orchestration," "simplicity over Kubernetes" |
| **Common exam traps** | Trap: choosing raw EC2 + manual Docker for a multi-service containerized app instead of ECS — technically works but is never the "best" answer when orchestration/scaling of containers is implied | Distractor: "ECS requires Kubernetes expertise" (false — that's EKS). Trap: forgetting ECS still needs an EC2 launch type cluster (with capacity to manage) unless Fargate is explicitly chosen |

---

### 3. ECS vs EKS

| Dimension | ECS | EKS |
|---|---|---|
| **Primary use case** | AWS-native container orchestration, teams without existing Kubernetes investment, simpler mental model | Kubernetes-standard workloads, multi-cloud/hybrid portability requirement, existing K8s manifests/Helm charts, teams with K8s expertise, need for K8s-specific ecosystem (operators, CRDs, service mesh like Istio) |
| **Scalability** | ECS Service Auto Scaling (target tracking on CPU/memory/custom CloudWatch metric) | Kubernetes-native HPA/VPA/Cluster Autoscaler or Karpenter; comparable scaling limits in practice, since both are ultimately bounded by underlying compute capacity and account quotas — configuration overhead differs more than the ceiling itself |
| **Availability** | Multi-AZ scheduling built-in, simpler HA story | Multi-AZ via node groups spread across AZs + control plane already multi-AZ-managed by AWS; more moving parts to get right (node group per AZ, pod topology spread constraints) |
| **Latency** | Marginally simpler/faster scheduling due to less abstraction | Comparable runtime latency; K8s API server round trips can add scheduling overhead vs ECS's simpler scheduler |
| **Operational overhead** | Lower — no Kubernetes control plane to reason about, AWS-proprietary but simple | Higher — must understand Kubernetes concepts (pods, deployments, ingress controllers, RBAC, CNI plugin (VPC CNI)), plus EKS version upgrade cadence management |
| **Pricing characteristics** | No control plane charge | EKS control plane has an hourly charge (per cluster) in addition to node/Fargate compute cost — this is a real cost delta the exam sometimes tests |
| **Encryption/security notes** | Task IAM roles, awsvpc mode, straightforward IAM integration | IAM Roles for Service Accounts (IRSA) for pod-level least privilege, K8s RBAC layered on top of IAM (dual authZ model — more complex to secure correctly), secrets can integrate with Secrets Manager/Parameter Store via CSI driver |
| **Limitations** | Not portable outside AWS; smaller ecosystem/tooling; no native support for K8s-specific patterns (CRDs, operators) | Steeper learning curve, more components to patch/secure (CNI, ingress controllers, add-ons), version deprecation forces periodic upgrades |
| **Exam trigger words** | "AWS-native," "simplest container orchestration," "no Kubernetes experience," "minimize operational complexity" | "Kubernetes," "portability across cloud providers," "existing Kubernetes manifests/Helm," "hybrid cloud," "open-source orchestration standard," "K8s API" |
| **Common exam traps** | Distractor offering EKS for a "simplify operations, team is AWS-only, no K8s skill" scenario — wrong, ECS wins | Distractor offering ECS when the question explicitly says "must be portable to on-premises/other clouds" or mentions existing Helm charts — EKS is the only correct answer there. Trap: forgetting EKS control plane cost exists as a distinct line item in cost-optimization questions |

---

### 4. ECS on EC2 vs Fargate

| Dimension | ECS on EC2 (EC2 launch type) | ECS/EKS on Fargate |
|---|---|---|
| **Primary use case** | Need control over instance type (GPU, specific family), want to use Reserved/Spot pricing for cost optimization at scale, need to bin-pack many tasks per host for density/cost efficiency, need host-level customization (custom AMI, daemon agents) | Serverless containers — no infrastructure management, unpredictable/spiky workloads, small number of long-running services, teams wanting to eliminate patching entirely |
| **Scalability** | Two-layer scaling: scale the ASG (capacity) AND scale ECS tasks (scheduling) — must keep both in sync (capacity providers help automate this) | Single-layer scaling: just scale tasks; AWS provisions underlying compute per-task transparently |
| **Availability** | Multi-AZ if ASG spans AZs; you're responsible for capacity headroom per AZ | Multi-AZ inherent per task placement; no capacity planning needed |
| **Latency** | No cold-start for task placement onto already-running instances (if capacity available); potential scheduling delay if ASG must scale out first | Task startup includes provisioning a micro-VM (Firecracker) — slower cold start than placing onto an already-warm EC2 instance; magnitude varies by image size, networking mode (awsvpc/ENI attach), and container count, and has improved across platform iterations, but treat it as a real factor for bursty, latency-sensitive scale-out rather than a fixed number |
| **Operational overhead** | Highest — manage AMI (ECS-optimized AMI), patch OS, manage ECS agent, capacity providers, instance draining on scale-in | Lowest — zero host management, no patching, no capacity planning |
| **Pricing characteristics** | Pay for EC2 instance regardless of bin-packing efficiency; can leverage Spot/RI/Savings Plans for significant savings; cost-efficient at high, steady density | Pay per vCPU/memory-second actually reserved by the task (per-task granularity); typically more expensive per-unit-compute than well-utilized EC2, but no waste from under-utilized instances — cheaper for spiky/low-density workloads |
| **Encryption/security notes** | You harden the host OS; shared kernel across tasks on same instance (weaker task isolation) unless careful | Each Fargate task runs in its own isolated micro-VM (Firecracker) — stronger tenant isolation, no shared kernel across tasks, no host-level access at all (reduces attack surface, satisfies stricter multi-tenant isolation requirements) |
| **Limitations** | Must manage instance draining, capacity provider strategies, AMI lifecycle | **No GPU support at all** — GPU-accelerated tasks require the EC2 launch type, full stop; also less control over underlying instance type/networking tuning, no SSH/host access, ephemeral storage limits per task |
| **Exam trigger words** | "cost optimization using Spot/Reserved Instances for containers," "control over instance type," "GPU workloads," "maximize resource utilization/bin packing" | "serverless containers," "no EC2 instances to manage," "eliminate patching," "unpredictable scaling," "strong isolation between tasks/tenants" |
| **Common exam traps** | Distractor: choosing EC2 launch type when the requirement is "minimize operational overhead" — wrong, that's Fargate's exact value prop | Distractor: choosing Fargate for "maximum cost efficiency at high sustained utilization with Reserved Instance discounts" — Fargate has no RI-style discount; Compute Savings Plans apply to Fargate usage, but pure Spot+RI density optimization is only available on the EC2 launch type. Distractor: choosing Fargate for a GPU workload — not supported at all, automatic disqualifier. Trap: assuming Fargate = free from any capacity limits (there are account-level vCPU quotas) |

---

### 5. Auto Scaling (EC2/ASG) vs Lambda Scaling

| Dimension | EC2 Auto Scaling | Lambda Concurrency Scaling |
|---|---|---|
| **Primary use case** | Scaling stateful/long-running compute in response to load (target tracking, step, scheduled, predictive scaling policies) | Scaling stateless, short-duration function invocations in response to concurrent event volume |
| **Scalability** | Scale-out constrained by boot time (minutes) — instance launch, bootstrap, health check grace period, warm pool can mitigate | Scale-out near-instant per invocation, bounded by account/region concurrency limit and (if configured) reserved concurrency per function; burst concurrency has an initial burst allowance then a ramp per region |
| **Availability** | You define min/max/desired across AZs; ASG replaces unhealthy instances automatically (self-healing) | Inherently HA — AWS manages execution environment placement across AZs |
| **Latency** | Reactive scaling has lag (metric evaluation period + instance boot); predictive scaling (ML-based, forecasts EC2 ASG capacity ahead of demand) reduces this for cyclical patterns | Scaling itself is near-instant, but cold starts add per-invocation latency spikes especially after scale-out events or idle periods |
| **Operational overhead** | Requires tuning scaling policies, cooldowns, health check grace periods, warm pools for latency-sensitive launches | Effectively none — concurrency scaling is automatic; only tuning lever is Provisioned Concurrency (to pre-warm, at a cost) or Reserved Concurrency (to cap/guarantee) |
| **Pricing characteristics** | Pay for instances while running, including during scale-out ramp-up even if underutilized | Pay per invocation/duration; Provisioned Concurrency adds a standing charge (similar economics to keeping EC2 warm) — using it defeats some of Lambda's pure pay-per-use advantage |
| **Encryption/security notes** | Same IAM instance profile scoped per ASG launch template | Concurrency scaling doesn't change the security model — still per-function execution role; Provisioned Concurrency environments are pre-initialized but same IAM boundary |
| **Limitations** | Cannot react instantaneously to sudden spikes (predictive scaling helps only for recurring/forecastable patterns); requires headroom buffer for true burst protection | Regional concurrency limits can throttle at extreme scale (mitigated by requesting limit increases); cold starts under Provisioned Concurrency absence hurt tail latency during rapid scale-out |
| **Exam trigger words** | "target tracking scaling policy," "predictive scaling," "warm pools," "scheduled scaling for known traffic patterns," "step scaling" | "automatically scales with number of requests," "no capacity planning for scaling," "concurrency limit," "provisioned concurrency to reduce cold starts" |
| **Common exam traps** | Trap: expecting ASG to handle a sudden 10x spike within seconds — it can't, that's a Lambda/serverless or pre-scaled/warm-pool answer. Distractor: dynamic scaling alone for a known, recurring traffic pattern (e.g., daily batch spike) — scheduled or predictive scaling is the better/exam-preferred answer | Trap: assuming Lambda has literally unlimited instant concurrency — regional limits exist and are a valid exam gotcha for "massive sudden traffic" scenarios feeding into SQS/throttling design questions. Distractor: recommending Provisioned Concurrency as default for cost-sensitive infrequent workloads — it adds standing cost, only justified when cold-start latency is unacceptable |

---

### 6. EC2 Purchasing Options

| Option | Primary use case | Commitment/Flexibility | Pricing characteristics | Availability guarantee | Interruption risk | Exam trigger words | Common exam traps |
|---|---|---|---|---|---|---|---|
| **On-Demand** | Unpredictable, short-term, spiky workloads; new/untested applications; dev/test | No commitment, pay by second/hour | Highest per-hour rate, full flexibility | Standard EC2 SLA | None (you control termination) | "unpredictable workloads," "cannot be interrupted," "short-term, spiky, cannot be predicted," "no long-term commitment" | Distractor: On-Demand recommended purely for "lowest cost" — never true when workload is steady-state/predictable (RI/Savings Plans always win on cost there) |
| **Reserved Instances (RI)** | Steady-state, predictable workloads (e.g., baseline database tier) known in advance for 1 or 3 years | 1 or 3-year term; Standard RIs (less flexible, higher discount) vs Convertible RIs (can change instance family/OS, lower discount); can be Regional (flexible AZ) or Zonal (capacity reservation guaranteed in specific AZ) | Discounts commonly cited around 70%+ vs On-Demand for 3-yr All Upfront Standard RIs — treat this as illustrative, not a fixed guarantee; actual savings vary by instance family, region, term, and payment option. Billing discount applies automatically to matching usage | Zonal RI = capacity reservation guarantee in that AZ; Regional RI = no capacity guarantee, just billing discount | N/A — it's a billing construct, not a capacity type tied to interruption | "steady-state usage," "predictable for the next 1-3 years," "committed to a specific instance family/region," "capacity reservation in a specific AZ" | Trap: confusing Regional RI (flexible, no capacity guarantee) with Zonal RI (fixed AZ, capacity guaranteed) — exam tests this distinction directly. Distractor: recommending Standard RI when question implies instance family may change — Convertible RI is correct there |
| **Savings Plans** | Steady-state usage where compute needs may shift across instance families, sizes, OS, region, or even to Fargate/Lambda | 1 or 3-year $/hour commitment (Compute Savings Plans = most flexible, applies across EC2/Fargate/Lambda, any instance family/region; EC2 Instance Savings Plans = locked to instance family in a region but higher discount) | EC2 Instance Savings Plans can match Standard RI's discount ceiling with added flexibility (instance size flexible within family). Compute Savings Plans trade some discount depth for the cross-service flexibility — their max discount ceiling is generally *lower* than EC2 Instance SP/Standard RI (in the Convertible-RI-like range), not similar or better | No capacity reservation associated | N/A | "flexible across instance families, regions, and compute services," "commitment to a dollar amount per hour," "spans EC2, Fargate, and Lambda" | Distractor: recommending RI when the question explicitly wants flexibility across EC2/Fargate/Lambda — that's a Compute Savings Plan, RIs cannot span services. Trap: assuming Savings Plans provide a capacity reservation — they do not (only Zonal RIs / On-Demand Capacity Reservations do) |
| **Spot Instances** | Fault-tolerant, flexible, stateless workloads — batch processing, big data (EMR), CI/CD, containerized microservices with graceful interruption handling, HPC | No commitment; capacity can be reclaimed by AWS with a 2-minute interruption notice (via CloudWatch Event/EventBridge) | Deepest discount of all options — commonly cited up to ~90% vs On-Demand, but this is illustrative/market-dependent (Spot pricing floats with supply and demand per instance type/AZ), not a fixed number to rely on | No guarantee — Spot capacity can be reclaimed at any time when AWS needs the capacity back | High — must design for interruption (ASG with mixed instances policy — AWS's current recommended approach — or Spot Fleet, diversified instance pools, Spot interruption handling in app logic) | "fault-tolerant," "flexible start/end time," "can withstand interruptions," "significant cost savings," "batch processing," "stateless workers" | Distractor: Spot recommended for a stateful, latency-sensitive, or must-not-be-interrupted workload (e.g., production database) — an automatic wrong answer whenever the scenario says "cannot tolerate interruption." Trap: forgetting instance/AZ diversification to reduce simultaneous reclaim risk |
| **Dedicated Hosts** | Compliance/licensing requirements needing visibility into physical server (socket/core/host ID) — typically BYOL scenarios for licenses tied to physical cores/sockets (e.g., Windows Server, SQL Server, some Oracle licenses) | Can be purchased On-Demand or Reserved (for a discount); host-level allocation | Most expensive purchasing model generally, but can be net-cheaper when it lets you bring existing per-socket/per-core licenses instead of buying new ones | You control instance placement on that physical host explicitly | None from AWS side (you own the whole host) | "bring your own license (BYOL)," "per-socket, per-core, or per-VM licensing," "visibility into the underlying physical server," "compliance requiring dedicated physical hardware," "server-bound licensing" | Distractor: choosing Dedicated Instances when the question specifically mentions licensing tied to physical **sockets/cores** — that requires Dedicated Hosts (visibility into physical host attributes), not just tenancy isolation |
| **Dedicated Instances** | Regulatory/compliance requirement for single-tenant hardware isolation but WITHOUT needing visibility/control of the physical host itself (no per-core licensing concern) | On-Demand or Reserved billing; instance-level (not host-level) dedication | Cheaper than Dedicated Hosts, more expensive than shared-tenancy On-Demand/RI equivalents | Runs on hardware dedicated to a single customer account, but you don't control/see host placement details across launches | None | "single-tenant hardware," "instances must not share hardware with other AWS customers," "compliance requires physical isolation" (without licensing/socket visibility language) | Distractor: choosing Dedicated Hosts when only tenancy isolation is required (adds unnecessary cost/complexity — Dedicated Instances is the leaner correct answer). Trap: conflating "Dedicated Instances" tenancy with "Dedicated Host" allocation type — exam deliberately uses near-identical wording to test precision |

#### Cross-cutting cost-optimization exam heuristic (Domain 4, 20%)
When a question gives workload **predictability + duration + interruptibility**, map it like this:
- Unknown/short/spiky → **On-Demand**
- Known, steady, 1-3yr, fixed instance family → **RI (Standard, Zonal if capacity needed)**
- Known, steady, 1-3yr, but flexible across family/region/service → **Savings Plans (Compute)**
- Flexible timing, interruption-tolerant → **Spot**
- Licensing tied to physical cores/sockets → **Dedicated Hosts**
- Compliance wants single-tenancy only → **Dedicated Instances**

This is the exact decision tree the SAA-C03 cost domain tests repeatedly with reworded scenarios.

## Storage

*AWS SAA-C03 Storage Deep Dive: S3 vs EBS vs EFS vs FSx*

---

### 1. S3 vs EBS vs EFS — Core Comparison

| Dimension | **S3** | **EBS** | **EFS** |
|---|---|---|---|
| **Type** | Object storage | Block storage | Managed file storage (NFSv4.1) |
| **Primary use case** | Static assets, data lake, backups, logs, hosting, cross-region/app storage | Boot volumes, databases, low-latency single-instance transactional workloads | Shared POSIX filesystem across many EC2/containers/Lambda concurrently |
| **Attachment model** | Accessed over HTTP(S) API from anywhere (with auth) | Attaches to **one** EC2 instance at a time (Multi-Attach only for io1/io2, same AZ, cluster-aware FS required) | Mountable by **thousands** of instances/AZs/VPCs concurrently |
| **Scalability** | Virtually unlimited, scales automatically, no provisioning | Fixed size at creation (resizable, but manual/online resize op), tied to AZ | Elastic — grows/shrinks automatically, no provisioning |
| **Availability/Durability** | Durability: 99.999999999% (11 9s), multi-AZ by design (Standard). Availability: *designed for* 99.99%, but the contractual **SLA** (service-credit threshold) is **99.9%** — these are two different numbers, don't conflate them | Reliability is expressed as **annual failure rate (AFR)**, not an "availability %": gp2/gp3/st1/sc1 ≈ 99.8–99.9% durability (0.1–0.2% AFR); io1/io2 ≈ 99.999% durability (0.001% AFR). Separately, EBS carries its own **99.9% SLA** for volume I/O availability — a distinct contractual figure, not the durability number. **AZ-bound** | 99.999999999% (11 9s) durability (Standard); designed for 99.99% availability, data replicated across multiple AZs |
| **Latency** | Tens–hundreds of ms (first byte); not for low-latency block I/O | Sub-ms to low single-digit ms (SSD-backed types) | Low single-digit ms, higher than EBS due to network/NFS overhead |
| **Throughput model** | Scales with parallel requests (request-rate based) | Provisioned per volume (IOPS/throughput caps) | Scales with storage size (Bursting mode), a fixed provisioned rate (Provisioned Throughput mode), or auto-scaling on demand (Elastic Throughput mode) |
| **Operational overhead** | None — fully managed, no capacity/patching | Must size, monitor IOPS/throughput, snapshot manage, monitor burst balance (gp2) | Minimal — no capacity planning, but must choose performance/throughput mode |
| **Pricing model** | Pay per GB stored (tiered by class) + requests + data transfer out; cheapest at scale | Pay per **provisioned** GB (+ IOPS/throughput for io1/io2/gp3) regardless of usage | Pay per GB **actually used** (no provisioning) — can be pricier per-GB than EBS but no waste |
| **Encryption** | SSE-S3, SSE-KMS, SSE-C, client-side; bucket policies, ACLs (legacy), Block Public Access. Since Jan 2023, **SSE-S3 is applied automatically to all new objects by default** — no bucket configuration required | EBS encryption (KMS) — encrypts data at rest, in-transit between instance and volume, and snapshots | Encryption at rest (KMS) and in-transit (TLS via mount helper) |
| **Consistency** | Strong read-after-write consistency for all operations (PUTS/DELETES/overwrites) — since Dec 2020 | Block-level consistency, no eventual consistency concerns | Standard NFS consistency model (close-to-open) |
| **Access pattern** | Object-level (whole object PUT/GET, or byte-range GET) | Raw block device — filesystem installed by OS | POSIX file semantics — file locking, directories, permissions |
| **Multi-instance access** | Yes, natively (many readers/writers via API) | No (except Multi-Attach io1/io2 — requires cluster-aware FS like GFS2, not for arbitrary use) | Yes, natively, cross-AZ |
| **Cross-region** | Cross-Region Replication (CRR) available | Snapshots can be copied cross-region; volume itself is AZ-locked | EFS Replication (managed, async) across regions |
| **Limitations** | Not a block device — can't boot an OS from S3, no in-place random-write file semantics | AZ-locked (must snapshot+restore to move AZ/region); single-attach for general use | More expensive per-GB than EBS/S3 for large steady-state data; higher latency than EBS |

#### Exam Trigger Words
- "Needs to be accessed by **multiple EC2 instances simultaneously**, POSIX-compliant" → **EFS**
- "**Database** or **boot volume**, single instance, low latency" → **EBS**
- "**Static website**, **data lake**, **unlimited scale**, **durable long-term storage**" → **S3**
- "**Lift-and-shift** on-prem NFS file share" → **EFS**
- "Needs **highest IOPS for a database**" → **EBS (io2 Block Express)**
- "**Cost-effective storage for infrequently accessed shared files**" → EFS IA storage class

#### Common Traps
- Assuming EBS can be attached to multiple instances by default — **only Multi-Attach io1/io2**, and even then requires a cluster-aware filesystem; **not a general file-sharing solution**.
- Thinking S3 has "folders" — it's a flat namespace with key prefixes simulating a hierarchy.
- Forgetting EBS volumes are **AZ-locked**: an EC2 instance in AZ-b cannot attach a volume created in AZ-a without snapshot + restore.
- Confusing EFS with FSx — EFS is Linux/NFS only; Windows workloads need **FSx for Windows File Server** (SMB).
- Assuming S3 is always cheapest — for **large, constantly-accessed shared filesystems needed by many compute nodes with POSIX semantics**, EFS may be the only fit despite higher $/GB.
- Believing EBS snapshots are instantly consistent across huge volumes without stopping I/O — snapshots are point-in-time but for crash consistency across large multi-volume RAID setups you may need to freeze I/O or use fleet/multi-volume snapshots.
- **Conflating "durability" with "availability"** for EBS and S3 — durability (11 9s, AFR) describes the odds of losing data; availability/SLA describes uptime access to that data. The exam sometimes exploits this distinction directly.

---

### 2. EBS Volume Types

| Type | Category | Use Case | Max IOPS | Max Throughput | Max Size | Boot Volume? | Price Basis |
|---|---|---|---|---|---|---|---|
| **gp3** | General Purpose SSD | Default choice for most workloads (boot volumes, dev/test, low-latency apps) | 16,000 (baseline 3,000 free) | 1,000 MB/s (baseline 125 free) | 16 TiB | Yes | Storage + IOPS + throughput billed **independently** |
| **gp2** | General Purpose SSD (legacy) | Same as gp3 but older, burst-credit based | Baseline 3 IOPS/GiB (min 100), up to 16,000 at ~5,334 GiB+; volumes **≤1 TiB** can burst to 3,000 IOPS via I/O credits | Up to 250 MB/s | 16 TiB | Yes | Storage only (IOPS tied to size) |
| **io2 (Block Express)** | Provisioned IOPS SSD | Mission-critical, high-IOPS DBs (Oracle, SAP HANA, large SQL/NoSQL) | Up to 256,000 | Up to 4,000 MB/s | 64 TiB | Yes | Storage + provisioned IOPS (higher $/IOPS than gp3, but 99.999% durability) |
| **io1** | Provisioned IOPS SSD (legacy) | Predecessor to io2; still supports Multi-Attach | Up to 64,000 | Up to 1,000 MB/s | 16 TiB | Yes | Storage + provisioned IOPS |
| **st1** | Throughput Optimized HDD | Big data, data warehouses, log processing, streaming — **throughput-bound, sequential access** | 500 (burst) | 500 MB/s | 16 TiB | **No** | Cheaper per-GB than SSD, billed on size |
| **sc1** | Cold HDD | Infrequently accessed data, lowest cost block storage | 250 (burst) | 250 MB/s | 16 TiB | **No** | Lowest $/GB of all EBS types |

#### Key Exam Facts
- **gp3 vs gp2**: gp3 decouples IOPS/throughput from volume size and is commonly cited as **~20% cheaper** than gp2 at equivalent baseline performance (treat as an approximate, region-dependent figure, not an exact universal number). Exam wants gp3 as the "cost-optimize this general-purpose volume" answer.
- **io2 Block Express**: sub-millisecond latency, 4x IOPS of io1, 99.999% durability (vs 99.8–99.9% for other types) — trigger for "**highest durability + highest IOPS**" DB requirement.
- **st1/sc1 cannot be boot volumes** and are **HDD-only, throughput-oriented** — a classic trap is picking st1 for random I/O workloads (wrong — st1 is for **large, sequential** workloads).
- **Multi-Attach** (io1/io2 only): up to 16 instances, same AZ, requires cluster-aware filesystem (no native file locking) — NOT a substitute for EFS.
- Volumes are **AZ-specific**; to move data cross-AZ or cross-region, take a **snapshot** (stored in S3, region-durable) and restore into target AZ/region.
- **Elastic Volumes**: can modify size, IOPS, and type live without detaching or stopping the instance. The exam-relevant point is simply that **online resize without downtime is possible** — AWS has adjusted the exact cooldown/throttling rules between successive modifications over time, so don't memorize a specific wait-time figure; verify current limits in the console/docs if it matters for your use case.

#### Common Traps
- Choosing io1/io2 automatically for "high performance" when gp3 now handles up to 16,000 IOPS at lower cost — check if requirement truly exceeds gp3 ceiling.
- Picking sc1 for a workload needing occasional bursts of IOPS-heavy random access — sc1 is for **cold, infrequent, throughput/sequential** access only.
- Forgetting HDD volumes (st1/sc1) **cannot be used as boot volumes**.
- Assuming increasing volume size increases performance for gp2 in real time — it does (3 IOPS/GB baseline), but people forget gp3 breaks this coupling.
- Not recognizing that EBS snapshots are **incremental** but each snapshot appears "full" — first snapshot is full, subsequent ones only store changed blocks (relevant for cost/RTO questions).

---

### 3. EFS vs FSx Family

| Service | Protocol | OS Target | Use Case | Performance Profile | Key Differentiator |
|---|---|---|---|---|---|
| **EFS** | NFSv4.1 | Linux | General-purpose shared Linux file storage, container/Lambda shared storage | Bursting, Provisioned, or Elastic Throughput mode; General Purpose vs Max I/O performance mode | Serverless, pay-per-use, multi-AZ by default |
| **FSx for Lustre** | Lustre | Linux | **HPC**, machine learning training, genomics, media rendering — massively parallel, high-throughput compute | Sub-ms latencies; AWS states throughput up to hundreds of GB/s and IOPS into the millions at scale — treat these as best-case ceilings that vary by deployment type (Scratch/Persistent) and file system size, not guaranteed fixed numbers | Native **S3 integration** (lazy-load from/write back to S3 buckets as POSIX FS) |
| **FSx for Windows File Server** | SMB | Windows | Windows-native apps needing **SMB, Active Directory (AD) integration, DFS namespaces, ACLs, VSS shadow copies** | Configurable SSD/HDD, provisioned throughput | Purpose-built, fully Windows-native file server with native DFS/VSS/NTFS ACL support — **not the only FSx option with AD integration** (see ONTAP), but the only one delivering full native Windows Server file-sharing semantics |
| **FSx for NetApp ONTAP** | NFS, SMB, iSCSI | Multi-protocol (Linux + Windows) | Enterprise NAS migration (NetApp customers), needs **multi-protocol access, snapshots, cloning, dedup, SnapMirror** | High performance, sub-ms latency | Only AWS storage with **multi-protocol (NFS+SMB+iSCSI) simultaneous access** + storage efficiency features; also supports AD integration for SMB access (like FSx for Windows) |
| **FSx for OpenZFS** | NFS | Linux | Migrating on-prem ZFS workloads, needing ZFS snapshots/clones, high IOPS at low latency | AWS states up to 1,000,000+ IOPS and sub-ms latency at scale — treat as a best-case ceiling, varies by deployment size | Native ZFS features (snapshots, compression, cloning) fully managed |

#### Exam Trigger Words
- "**HPC / ML training / genomics**, needs to process data **already in S3**" → **FSx for Lustre**
- "**Windows-based application**, requires **Active Directory**, **SMB shares**, **DFS**" → **FSx for Windows File Server**
- "**Migrating existing NetApp** on-prem storage, needs **multi-protocol (NFS + SMB)**" → **FSx for ONTAP**
- "**ZFS snapshots/clones**, Linux workload, sub-millisecond latency" → **FSx for OpenZFS**
- "**Simple Linux shared storage**, serverless, containers/Lambda, unpredictable growth" → **EFS**
- "**Lift-and-shift Windows file server**" → **FSx for Windows** (not EFS — EFS is Linux/NFS only, common trap)

#### Common Traps
- Choosing **EFS** for a Windows workload — EFS does **not support SMB**; must use FSx for Windows File Server.
- Choosing **FSx for Lustre** for general enterprise file sharing — it's **purpose-built for HPC/ML**, overkill and operationally heavier for typical shared storage.
- Forgetting FSx for Lustre can be backed directly by an **S3 bucket** as its data repository — a huge exam signal when the question mentions "process S3 data with an HPC cluster."
- Assuming all FSx types are multi-AZ by default — **Windows File Server and ONTAP support Single-AZ or Multi-AZ deployment options**; must be explicitly chosen for HA.
- Not knowing EFS has two **performance** modes (**General Purpose** — default, lower latency; **Max I/O** — higher throughput/IOPS ceiling but higher per-op latency) and **three** distinct **throughput** modes: **Bursting** (tied to storage size), **Provisioned** (fixed MB/s you set and pay for regardless of use), and **Elastic** (auto-scales to actual workload, no provisioning — the newer, AWS-recommended default for unpredictable workloads). Don't collapse Provisioned and Elastic into one option — they have different billing and scaling behavior.
- Conflating **EFS Infrequent Access (EFS-IA)** storage class (via Lifecycle Management) with S3-IA — they're separate cost-optimization mechanisms per service.
- Assuming **FSx for Windows File Server is the only FSx service that integrates with Active Directory** — FSx for NetApp ONTAP also supports AD-joined SMB shares; the real differentiator for FSx for Windows is native Windows Server file-sharing feature parity (DFS, VSS, NTFS ACLs), not AD support in isolation.

---

### 4. S3 Storage Classes

| Class | Availability | Durability | Min Storage Duration | Retrieval Time | Retrieval Fee | Use Case |
|---|---|---|---|---|---|---|
| **S3 Standard** | 99.99% (design target; contractual SLA is 99.9%) | 11 9s | None | Milliseconds | None | Frequently accessed data, active workloads |
| **S3 Intelligent-Tiering** | 99.9% | 11 9s | None (no min duration charge) | Milliseconds (Frequent/Infrequent tiers) | None (monitoring fee per object instead) | Unknown/changing access patterns |
| **S3 Standard-IA** | 99.9% | 11 9s | 30 days | Milliseconds | Per-GB retrieval fee | Infrequent access, but needs millisecond access when accessed (backups, DR) |
| **S3 One Zone-IA** | 99.5% (single AZ) | 11 9s (within that AZ) | 30 days | Milliseconds | Per-GB retrieval fee | Infrequent, **re-creatable** data — secondary backups, replicas |
| **Glacier Instant Retrieval** | 99.9% | 11 9s | 90 days | Milliseconds | Higher per-GB retrieval fee than Standard-IA | Archive data needing **immediate** access (medical images, news media) accessed ~1x/quarter |
| **Glacier Flexible Retrieval** | 99.99% (after restore) | 11 9s | 90 days | Expedited: 1–5 min; Standard: 3–5 hrs; Bulk: 5–12 hrs | Yes, tiered by speed | True archive, occasional access, disaster recovery |
| **Glacier Deep Archive** | 99.99% (after restore) | 11 9s | 180 days | Standard: 12 hrs; Bulk: 48 hrs | Yes, lowest storage cost but retrieval fee applies | Long-term compliance/regulatory archive (7–10 year retention), rarely if ever accessed |

#### Key Exam Facts
- All classes (except One Zone-IA) replicate across **≥3 AZs**.
- **Minimum storage duration charges**: deleting/transitioning an object before the minimum duration incurs a pro-rated early-deletion charge (Standard-IA/One Zone-IA: 30 days; Glacier Flexible: 90 days; Deep Archive: 180 days).
- **Small-object overhead**: S3 Standard-IA, One Zone-IA, and Glacier Instant Retrieval bill objects smaller than 128 KB as if they were 128 KB — a frequent gotcha for "lots of small files" scenarios. Glacier Flexible Retrieval and Glacier Deep Archive apply their own per-object metadata/overhead charges, which are **not necessarily identical to the 128 KB IA figure** — confirm current numbers on the AWS S3 pricing page before treating this as one universal rule across all Glacier tiers.
- Lifecycle policies commonly chain: Standard → Standard-IA (30d) → Glacier Flexible Retrieval (90d) → Deep Archive (180d).
- **Glacier Instant Retrieval** vs **Glacier Flexible Retrieval**: the differentiator is access latency — Instant Retrieval behaves like Standard-IA speed-wise but cheaper storage for rarely-touched data; Flexible Retrieval trades cost for **minutes-to-hours** retrieval.

#### Exam Trigger Words
- "**Unknown or unpredictable access patterns**, want automatic cost optimization **without performance impact**" → **Intelligent-Tiering**
- "**Compliance archive, 7 years, rarely accessed, retrieval time not critical**" → **Glacier Deep Archive**
- "**Backup that must be retrievable within minutes** even though rarely used" → **Glacier Flexible Retrieval (Expedited)** or **Glacier Instant Retrieval** (if truly millisecond-need)
- "**Re-creatable data, non-critical, cost-sensitive, single-AZ acceptable**" → **One Zone-IA**
- "**Data accessed less than once a month but needs immediate access when it is**" → **Standard-IA**

#### Common Traps
- Choosing One Zone-IA for critical/irreplaceable data — it has **no cross-AZ redundancy**, so an AZ failure = data loss risk.
- Forgetting **retrieval fees** exist on IA/Glacier tiers — total cost of ownership questions often hinge on access frequency, not just storage cost.
- Assuming Glacier Deep Archive can serve data instantly — minimum 12-hour standard retrieval.
- Using lifecycle transitions on **small objects** expecting savings — small-object overhead charges can erode or eliminate expected savings (verify current thresholds per class rather than assuming one fixed KB number applies everywhere).
- Confusing **Intelligent-Tiering's monitoring fee** (small per-object/month charge) with "always cheaper" — for **very large numbers of small objects with predictable stable access**, plain Standard or Standard-IA can be cheaper.
- Not knowing Intelligent-Tiering has optional **Archive Instant Access, Archive Access, and Deep Archive Access** tiers for automatic long-term archival within the same storage class (added complexity vs manual lifecycle rules).

---

### 5. S3 Standard vs Intelligent-Tiering (Deep Dive)

| Dimension | **S3 Standard** | **S3 Intelligent-Tiering** |
|---|---|---|
| **Primary use case** | Consistently, frequently accessed data (active application data, content distribution origin) | Data with **unknown, changing, or unpredictable** access patterns |
| **Cost model** | Flat rate per GB, no monitoring fee, no retrieval fee | Same $/GB as Standard for Frequent Access tier, **plus** small monthly per-object monitoring/automation fee; objects auto-move to cheaper tiers (Infrequent, Archive Instant Access, and optionally Archive Access / Deep Archive Access) after periods of no access (30/90/180+ days) |
| **Performance** | Millisecond latency always | Millisecond latency for Frequent/Infrequent/Archive Instant Access tiers; **hours** latency if opted into Archive Access/Deep Archive Access tiers |
| **Operational overhead** | None | None — fully automated tiering, **no retrieval fees ever** for the standard 3 tiers (this is the key sell vs manual lifecycle rules to Standard-IA which DO charge retrieval fees) |
| **Availability** | Designed for 99.99% (contractual SLA 99.9%) | 99.9% |
| **Minimum object size/duration** | None | No minimum storage duration; monitoring fee applies per object >128KB (objects <128KB not monitored/moved, stay in Frequent tier at Standard-equivalent cost) |
| **When Standard wins** | Access pattern is well-known, consistently high-frequency, or data lifespan is very short (< 30 days, avoiding monitoring fee for no benefit) | — |
| **When Intelligent-Tiering wins** | — | Data lake / analytics buckets where some objects go cold and hot unpredictably; eliminates need for manual lifecycle rule engineering and avoids the **retrieval fee risk** of manually using Standard-IA |

#### Exam Trigger Words
- "**Automatically optimizes storage costs without performance impact or operational overhead, no retrieval fees**" → **Intelligent-Tiering** (this exact phrasing appears frequently)
- "**Access pattern well understood and stable**" → Standard (or direct IA/One Zone-IA choice) is more cost-effective than paying the monitoring fee
- "**Want the archival benefits of Glacier but fully automated within a single storage class**" → Intelligent-Tiering with Archive Access tiers enabled

#### Common Traps
- Believing Intelligent-Tiering is "always the best default" — for **short-lived objects** (<30 days) or objects **smaller than 128 KB**, the monitoring fee overhead isn't worth it since they never get evaluated for tier movement anyway (small objects) or churn before the 30-day threshold.
- Forgetting that the **Archive Access and Deep Archive Access** optional tiers of Intelligent-Tiering **do** introduce retrieval latency (hours) — treating Intelligent-Tiering as "always millisecond access" is only true if you haven't opted into the archive tiers.
- Confusing "Intelligent-Tiering has no retrieval fees" with "Intelligent-Tiering has no fees at all" — the **monitoring/automation fee** is a real per-object monthly cost distinct from retrieval fees.

---

### Quick-Reference Decision Cheat Sheet (for exam speed)

- **Need a POSIX filesystem shared by many Linux instances/containers** → EFS
- **Need SMB/AD-integrated Windows file share** → FSx for Windows
- **Need HPC/ML scratch storage backed by S3** → FSx for Lustre
- **Migrating NetApp/multi-protocol NAS** → FSx for ONTAP
- **Need ZFS features on Linux** → FSx for OpenZFS
- **Single-instance low-latency block storage / boot volume** → EBS (gp3 default, io2 for extreme IOPS, st1/sc1 for cold/sequential-only, never as boot)
- **Object storage at any scale, static content, data lake** → S3
- **Don't know access pattern, want zero-ops cost optimization, no retrieval fee risk** → S3 Intelligent-Tiering
- **Know access pattern is infrequent but need millisecond retrieval** → S3 Standard-IA (or One Zone-IA if data is reproducible)
- **True cold archive, minutes-to-hours retrieval acceptable, cost is priority** → Glacier Flexible Retrieval
- **Compliance/regulatory, years-long retention, retrieval rarely needed, lowest cost** → Glacier Deep Archive

## Databases

*AWS SAA-C03 — Database Services Comparison (Domain 3 & 4 Focus)*

---

### 1. RDS vs DynamoDB

> **Note on terminology:** Aurora is technically one of the RDS database engines. For the rest of this guide, "RDS" by itself means the *standard* (non-Aurora) engines — MySQL, PostgreSQL, MariaDB, Oracle, SQL Server — to match how exam scenarios typically distinguish "RDS" from "Aurora." Section 2 treats them side by side explicitly.

**Primary use case**
- RDS: Relational workloads needing joins, transactions, complex queries, existing SQL schemas (migrated ERP/CRM, financial ledgers with ACID across tables).
- DynamoDB: Key-value/document access patterns at massive scale — session state, gaming leaderboards, IoT telemetry, shopping carts, single-digit-ms lookups on known access patterns.

**Scalability**
- RDS: Vertical scaling primarily (instance class up to a ceiling); read scaling via up to 15 read replicas (Aurora) or 5 (standard RDS engines). Storage autoscaling exists but compute is not horizontally elastic.
- DynamoDB: Horizontally, near-infinitely scalable via partitioning; on-demand capacity mode auto-scales throughput instantly; provisioned mode with auto-scaling reacts to CloudWatch alarms (minutes, not instant).

**Availability**
- RDS: Multi-AZ standby (99.95% SLA typical); failover 60–120s.
- DynamoDB: Multi-AZ by default within a region, no configuration needed; Global Tables for multi-region active-active. SLA 99.99% (99.999% with Global Tables).

**Latency**
- RDS: Single-digit ms to tens of ms depending on query complexity/joins.
- DynamoDB: Consistent single-digit ms regardless of table size, because access is by key not scan/join.

**Operational overhead**
- RDS: Patching windows, engine version upgrades, parameter groups, storage scaling decisions — even "managed" still requires tuning.
- DynamoDB: Fully serverless — zero patching, zero instance sizing (on-demand mode).

**Pricing characteristics**
- RDS: Pay for provisioned instance + storage (GB-month) + IOPS, running 24/7 regardless of load (unless you stop dev/test instances).
- DynamoDB: On-demand = pay per request (RCU/WCU consumed); Provisioned = pay per RCU/WCU-hour reserved, cheaper at steady predictable load. No charge for idle compute in on-demand mode.

**Encryption/security**
- Both support encryption at rest via KMS and TLS in transit.
- RDS: Security groups + IAM auth (optional, engine-dependent) + native DB user/password.
- DynamoDB: IAM policies down to item/attribute level (fine-grained access control via `dynamodb:LeadingKeys` condition), no network-layer SG (VPC endpoint optional for private access).

**Consistency model**
- RDS: Strong consistency always (ACID transactions).
- DynamoDB: Eventually consistent reads (default, cheaper) or strongly consistent reads (opt-in, 2x RCU cost). Strong consistency is **not** available on Global Secondary Indexes — GSIs only ever support eventually consistent reads — and reading from a Global Tables replica region is always eventually consistent relative to the writer region, regardless of the consistency setting requested.

**Limitations**
- RDS: Max storage ceiling varies by engine — up to 64 TiB for MySQL/MariaDB/PostgreSQL/Oracle, but lower (edition-dependent, historically up to 16 TiB) for SQL Server. No cross-shard joins; connection limits under load (mitigated by RDS Proxy).
- DynamoDB: 400 KB item size limit, no native joins/aggregations, query patterns must be designed upfront (access-pattern-first modeling), hot partition risk with poor key design.

**Exam trigger words**
- "relational," "joins," "complex transactions," "existing SQL application" → RDS.
- "key-value," "millisecond latency at any scale," "unpredictable/massive traffic spikes," "serverless," "session store," "no ops" → DynamoDB.

**Common traps**
- Assuming DynamoDB is "always cheaper" — at steady, high, predictable throughput, provisioned RDS/Aurora can beat DynamoDB on-demand costs.
- Choosing DynamoDB for workloads needing multi-table joins/ad-hoc reporting (should pair with Redshift/Athena via export, not force joins into Dynamo).
- Forgetting DynamoDB Global Tables requires application-level conflict resolution awareness (last-writer-wins).

---

### 2. RDS vs Aurora

**Primary use case**
- RDS (standard engines): Lift-and-shift of existing MySQL/PostgreSQL/MariaDB/Oracle/SQL Server workloads, licensing continuity (BYOL Oracle/SQL Server).
- Aurora: Cloud-native relational workloads needing higher throughput/availability than stock MySQL/PostgreSQL, without app rewrite (wire-compatible).

**Scalability**
- RDS: Storage auto-scales but is tied to instance; read replicas up to 5.
- Aurora: Storage auto-scales in 10 GB increments up to 128 TiB, decoupled from compute; up to 15 read replicas with typically low (single-digit-to-low-double-digit ms) replica lag thanks to the shared storage layer — this is a *typical* figure, not a guaranteed ceiling, and lag can grow under heavy write load; Aurora Serverless v2 scales compute in fine-grained ACU increments in seconds.

**Availability**
- RDS: Multi-AZ = one standby, manual-ish failover (60–120s), standby is not readable (unless Multi-AZ w/ 2 readable standbys option on RDS for MySQL/PostgreSQL now exists).
- Aurora: 6 copies of data across 3 AZs automatically; storage is self-healing; failover to a replica typically <30s; Aurora Global Database gives <1s replication lag cross-region with RPO near-zero and RTO <1 min.

**Latency**
- Aurora generally lower write latency due to log-structured storage (only writes redo log records to storage, not full pages) — reduces network I/O between compute and storage layer.

**Operational overhead**
- Both are "managed," but Aurora removes more toil: no manual storage provisioning, automated crash recovery is near-instant (no redo log replay wait), backtrack feature (rewind DB without restore).

**Pricing characteristics**
- RDS: Instance + provisioned storage (even if unused) + IOPS.
- Aurora: Instance + storage consumed (pay only for what's used, auto-grows) + I/O operations (unless using Aurora I/O-Optimized, which has higher instance price but no per-I/O charge — better for I/O-heavy workloads). Aurora Serverless v2 bills per ACU consumed, metered per second.
- Aurora instance-hour pricing is typically somewhat higher than the equivalent RDS instance class. A commonly cited rule of thumb is roughly 20% higher, but this is not an AWS-published constant — it varies by region, instance family/generation, and over time. For exam purposes, know the *conceptual* pricing model (pay for consumed storage/IO vs. provisioned capacity), not a specific percentage; storage/IO efficiency and reduced replica-count needs can offset the higher instance price for the right workload.

**Encryption/security**
- Identical model: KMS at rest, TLS in transit, IAM DB auth supported on both for MySQL/PostgreSQL-compatible engines.

**Consistency model**
- Both strongly consistent for writes/primary reads; read replicas (RDS or Aurora) are asynchronous → eventual consistency on replica reads. Aurora's shared storage layer reduces replica lag versus RDS's log-shipping replication.

**Limitations**
- RDS: Limited to 5 read replicas, storage scaling requires downtime-free but slower resize, no cross-region native replica without setting up read replica across regions manually (supported but heavier).
- Aurora: Engine limited to MySQL- and PostgreSQL-compatible only (no Oracle/SQL Server/MariaDB Aurora flavor), slightly higher baseline cost, some extensions/plugins unsupported vs vanilla engine.

**Exam trigger words**
- "cloud-native," "3x MySQL throughput," "5x PostgreSQL throughput," "global database," "fast failover under 30 seconds" (note: RDS Multi-AZ DB Cluster deployments also offer fast failover, ~35s — read the full scenario to confirm it's asking about Aurora specifically rather than a Multi-AZ DB Cluster), "storage auto-scaling to 128TB," "backtrack" → Aurora.
- "Oracle," "SQL Server," "licensing (BYOL)," "specific engine version/extension not supported by Aurora" → RDS.

**Common traps**
- Assuming Aurora = always cheaper because "you pay for what you use" — for large provisioned steady workloads, storage savings can be outweighed by higher instance pricing.
- Forgetting Aurora doesn't support Oracle/SQL Server — a question needing Windows auth/SQL Server-specific features forces you back to RDS.
- Confusing Aurora Replicas (storage-shared, low lag) with RDS Read Replicas (log-shipped, higher lag) when a question asks for "lowest replication lag."

---

### 3. Aurora vs Standard RDS Engines (Deep Dive)

**Primary use case**
- Same as above but emphasizing: Aurora when the exam scenario explicitly needs enterprise-grade relational performance/availability without managing a cluster (e.g., "SaaS platform needing database performance close to commercial-grade at open-source cost").

**Scalability**
- Aurora Serverless v2 is the key differentiator for "unpredictable/intermittent workloads" (dev/test, new app with unknown traffic) — scales in fine granularity (0.5 ACU steps) without connection drops, unlike v1 which had scaling points causing brief interruption.

**Availability**
- Aurora's continuous backup to S3 (no performance impact) vs RDS automated backups (snapshot + transaction logs, can have I/O impact on non-Aurora engines during backup window unless Multi-AZ deployed, since standby is used for backup in Multi-AZ RDS).

**Latency**
- Aurora Global Database: writer in primary region, up to 5 secondary read regions with typically <1 second lag — used for global read scaling and DR. Standard RDS cross-region read replica lag is seconds-to-minutes and consumes more bandwidth (full binlog shipped).

**Operational overhead**
- Aurora: self-healing storage (automatically repairs corrupted disk blocks by re-replicating from other 5 copies) — this is unique to Aurora and frequently tested.
- Standard RDS: DBA must manage storage type choice (gp3/io1/io2) and IOPS provisioning manually for performance.

**Pricing characteristics**
- Aurora I/O-Optimized: choose when I/O costs exceed ~25% of total Aurora bill — flat higher instance price, zero I/O charges. Exam scenario: "unpredictable heavy read/write I/O, want predictable billing" → Aurora I/O-Optimized.
- Standard mode: choose when I/O is low relative to compute.

**Encryption/security**
- Identical KMS/TLS/IAM auth mechanics; no differentiator here — don't overthink if a question tests only this axis.

**Consistency model**
- Aurora Replicas share the same underlying storage volume as the writer, so replica reads see the same data view almost immediately after commit (much smaller consistency window than RDS read replicas, which replicate via binlog/WAL shipping).

**Limitations**
- Aurora Serverless v2 originally had a minimum floor of 0.5 ACU and could not scale to true zero the way Aurora Serverless v1 could pause fully. **This is an area that has changed since launch** — AWS has since introduced the ability to scale Aurora Serverless v2 capacity down to 0 ACUs in certain configurations. Treat "v2 can/can't pause to zero" as a fact to verify against current AWS documentation close to your exam date rather than memorizing a fixed floor, since this is exactly the kind of service detail that evolves faster than static study notes.
- Standard RDS engines support more third-party extensions (e.g., specific PostgreSQL extensions Aurora hasn't certified).

**Exam trigger words**
- "self-healing storage," "6 copies across 3 AZs," "faster crash recovery," "database cloning without copying data" (Aurora fast clones, copy-on-write) → Aurora.
- "specific unsupported extension," "need to pause database to zero cost" — historically this trigger favored stopping the RDS/Aurora instance for dev/test (auto-restarts after 7 days) rather than assuming Serverless v2 pauses to zero; confirm current Aurora Serverless v2 zero-capacity behavior before treating this as settled, since AWS has been actively changing it.

**Common traps**
- Historically: believing Aurora Serverless v2 scales to zero when it could not (fixed 0.5 ACU minimum). Aurora Serverless v1 could scale to zero but is legacy/deprecated for new deployments. Because AWS has since added zero-capacity scaling to v2 in some form, don't treat either "v2 never reaches zero" or "v2 always reaches zero" as a safe blanket assumption — verify current behavior.
- Confusing "fast database cloning" (Aurora-only, copy-on-write, seconds regardless of size) with RDS snapshot restore (full copy, time proportional to size).

---

### 4. Multi-AZ vs Read Replica

**Primary use case**
- Multi-AZ: High availability / disaster recovery for the SAME workload — synchronous standby purely for failover, not for offloading reads (in classic RDS Multi-AZ; note newer "Multi-AZ DB Cluster" deployment option DOES allow reading from the 2 readable standbys).
- Read Replica: Horizontal read scaling — offload reporting/analytics/read-heavy traffic from the primary; can also be promoted for DR across regions.

**Scalability**
- Multi-AZ: Does not scale read/write throughput (classic instance-based Multi-AZ); Multi-AZ DB Cluster (newer) does add 2 readable replicas with fast (<35s) failover, blending the two concepts.
- Read Replica: Scales reads horizontally; up to 5 per RDS source, 15 per Aurora source; can be cross-region.

**Availability**
- Multi-AZ: Automatic failover (RDS handles DNS CNAME repoint), typically 60–120s (classic) or faster with Multi-AZ DB Cluster (~35s using Aurora-like replication).
- Read Replica: NOT automatic failover — must be manually promoted (breaks replication permanently once promoted); no automatic detection/repoint.

**Latency**
- Multi-AZ: Synchronous replication to standby (adds a small amount of write latency, especially cross-AZ) but zero replica lag by definition (standby always current).
- Read Replica: Asynchronous — replica lag can range from milliseconds (Aurora) to seconds/minutes (standard RDS under heavy write load) — CloudWatch `ReplicaLag` metric is exam-relevant.

**Operational overhead**
- Multi-AZ: Fully automatic, transparent — just enable the flag.
- Read Replica: Requires app-level read/write splitting logic (or RDS Proxy/Route 53 weighted routing) since it's a separate endpoint.

**Pricing characteristics**
- Multi-AZ: Doubles compute + storage cost (standby is full copy) but standby is NOT independently queryable in classic mode, meaning you pay for capacity you can't use for reads.
- Read Replica: Additional instance cost too, but delivers usable read capacity — better "cost efficiency per dollar of extra capacity" when the goal is scaling, not just HA.

**Encryption/security**
- Both replicate encryption settings from source; you cannot make an unencrypted replica of an encrypted source non-encrypted (encryption is inherited/immutable on RDS).

**Consistency model**
- Multi-AZ: Strong consistency maintained (synchronous) — no stale reads because standby isn't read from (classic mode).
- Read Replica: Eventual consistency — exam scenario "read-after-write consistency required" should make you cautious about routing that specific read to a replica.

**Limitations**
- Multi-AZ standby cannot be used as a read endpoint in classic single-standby mode (common exam trap).
- Read Replica of a Read Replica is supported on some engines but adds cascading lag; cross-region replicas incur data transfer charges.

**Exam trigger words**
- "disaster recovery," "automatic failover," "durability," "protect against AZ failure" → Multi-AZ.
- "reporting workload," "offload read traffic," "scale reads," "analytics without impacting production" → Read Replica.
- "both HA and read scaling" → Aurora (replicas serve both purposes natively) or Multi-AZ DB Cluster.

**Common traps**
- Thinking enabling Multi-AZ improves read throughput — it does not (classic deployment).
- Assuming Read Replicas provide HA — they require manual promotion and DNS/connection string changes at the app layer; RTO is not "automatic."
- For cross-region DR exam questions: Read Replica (cross-region) is the mechanism, not Multi-AZ (which is intra-region, cross-AZ only, except Aurora Global Database which is the cross-region HA/DR answer for Aurora).

---

### 5. DynamoDB DAX vs ElastiCache

**Primary use case**
- DAX: Purpose-built, drop-in write-through/read-through cache exclusively in front of DynamoDB — microsecond latency for DynamoDB API calls without app rewrite (same API compatible SDK).
- ElastiCache (Redis/Memcached): General-purpose caching layer for ANY backend (RDS, DynamoDB, custom app data, session store) — requires app to manage cache logic (cache-aside pattern typically).

**Scalability**
- DAX: Cluster of up to 10 nodes, one primary + up to 9 read replicas within a cluster.
- ElastiCache: Redis Cluster mode scales to hundreds of shards/nodes; Memcached scales via auto-discovery and adding nodes (pure horizontal partitioning, no replication).

**Availability**
- DAX: Multi-AZ within a cluster (replicas across AZs), automatic failover of primary.
- ElastiCache Redis: Multi-AZ with automatic failover (cluster mode enabled or disabled); Memcached has NO replication/persistence/failover — node loss = data loss, must be re-populated from source.

**Latency**
- DAX: Microsecond latency (vs single-digit ms for DynamoDB directly) — this "microseconds" keyword is a strong exam signal.
- ElastiCache: Sub-millisecond (Redis) typical.

**Operational overhead**
- DAX: Near-zero — it's purpose-built and requires only SDK endpoint change.
- ElastiCache: Requires cache invalidation strategy, TTL management, potential cache stampede handling at app level.

**Pricing characteristics**
- Both billed per node-hour by instance type; DAX has no separate "request" pricing (you already pay DynamoDB RCU/WCU for cache misses that hit the table).
- ElastiCache Redis with persistence (AOF) costs more in I/O than Memcached (no persistence).

**Encryption/security**
- DAX: Encryption at rest (KMS) and in-transit (TLS) supported; IAM policies control access to DAX cluster.
- ElastiCache Redis: Encryption at rest and in-transit + Redis AUTH/RBAC (Redis 6+); Memcached: NO encryption at rest, NO built-in auth (SASL support is limited) — security-sensitive question favoring Redis strongly.

**Consistency model**
- DAX item cache: eventually consistent by default (like DynamoDB). **Strongly consistent reads bypass the DAX cache entirely** — when the client requests strong consistency, DAX passes the request straight through to DynamoDB rather than serving it from (or populating) the cache; only eventually-consistent reads use the cache. Separately, DAX's write-through behavior means writes go to DynamoDB AND update the DAX item cache synchronously, while the query/scan result cache has its own default TTL of 5 minutes.
- ElastiCache: Consistency is fully app-managed (whatever the cache-aside implementation guarantees).

**Limitations**
- DAX: Only works with DynamoDB, not usable as a generic cache. DAX does **not** support the DynamoDB Transactions API (`TransactGetItems`/`TransactWriteItems`) at all — transactional calls must bypass DAX and go directly to DynamoDB.
- Memcached: No persistence, no backup/restore, no pub/sub, no complex data structures, no replication — pure ephemeral cache only.

**Exam trigger words**
- "microsecond read latency for DynamoDB," "no application code changes for caching DynamoDB" → DAX.
- "cache database query results," "session store with persistence," "pub/sub," "leaderboards / sorted sets," "multi-threading needed for simple cache" → ElastiCache (Redis vs Memcached split below).

**Common traps**
- Using DAX to cache RDS queries — impossible, DAX is DynamoDB-only.
- Choosing ElastiCache when the scenario says "no code changes, just want faster DynamoDB" — that's DAX (ElastiCache requires app-level integration).
- Assuming DAX guarantees strong consistency pass-through is cached — it isn't; strongly consistent reads are deliberately routed around the cache to DynamoDB.

---

### 6. ElastiCache Redis vs Memcached

**Primary use case**
- Redis: Complex data structures (sorted sets, lists, hashes, streams), leaderboard/ranking, pub/sub messaging, geospatial queries, need for persistence/durability or replication.
- Memcached: Simple, high-throughput, multi-threaded pure object cache with no need for persistence or complex data types — classic "cache database query result blob" use case.

**Scalability**
- Redis: Cluster Mode Enabled shards data across up to 500 nodes (with resharding online); Cluster Mode Disabled = single shard with up to 5 read replicas.
- Memcached: Scales horizontally by adding nodes; client-side (or Auto Discovery) hashing distributes keys — no data replication, so scaling = more capacity, not more resilience.

**Availability**
- Redis: Multi-AZ with automatic failover to a replica (when Cluster Mode enabled or with replicas configured); supports backup/restore via RDB snapshots.
- Memcached: No replication, no Multi-AZ failover, no persistence — node failure = data loss for keys on that node (rehydrate from source of truth).

**Latency**
- Both sub-millisecond; Memcached often marginally faster for pure simple get/set at very high throughput due to multi-threaded architecture (utilizes multiple cores per node natively); Redis is largely single-threaded per core for command execution (though I/O threading improvements exist in Redis 6+/7 and AWS's Redis engine versions).

**Operational overhead**
- Redis: More features = more configuration (persistence mode, eviction policy, cluster topology).
- Memcached: Simpler — practically no configuration beyond node count/size.

**Pricing characteristics**
- Comparable node-hour pricing at same instance type; Redis with Multi-AZ/replicas costs proportionally more (extra nodes for replicas); Memcached typically cheaper for equivalent raw cache capacity since no replica overhead needed.

**Encryption/security**
- Redis: Encryption in-transit and at-rest (KMS), Redis AUTH token, and since Redis 6 — RBAC with granular user permissions.
- Memcached: No at-rest encryption, no native strong auth — this is a frequently tested security differentiator ("which engine supports encryption" → always Redis).

**Consistency model**
- Redis: Single-threaded command execution per shard gives strong consistency for operations within a shard; async replication to read replicas (eventual consistency for replica reads).
- Memcached: No replication at all, so "consistency" is simply whatever's in that one node — no cross-node consistency guarantee, and cache misses require going back to source.

**Limitations**
- Redis: More complex failover mechanics, potential for larger memory overhead per key (metadata for data structures).
- Memcached: Max item size 1MB, no transactions, no persistence/backup, no pub/sub, no multi-key atomic operations, no built-in HA.

**Exam trigger words**
- "need Multi-AZ failover," "need backup and restore for cache," "need pub/sub," "need sorted sets/leaderboard," "need encryption for cached data" → Redis.
- "simplest, fastest, multi-threaded object cache," "no need for persistence or replication," "large scale simple caching," "cost-efficient simple cache" → Memcached.

**Common traps**
- Picking Memcached when the question mentions ANY durability/persistence/backup/security requirement — Memcached fails all of these by design.
- Assuming Redis Cluster Mode Disabled gives you sharding — it doesn't; you must explicitly enable Cluster Mode for horizontal write scaling across shards.
- Overlooking that Memcached's "multi-threaded" nature is the deliberate trigger phrase distinguishing it from Redis in throughput-per-node scenarios.

---

### 7. Neptune vs DocumentDB

**Primary use case**
- Neptune: Graph database for highly connected data — social networks, fraud detection graphs, recommendation engines, knowledge graphs, network/IT topology mapping. Supports Gremlin, SPARQL, and openCypher.
- DocumentDB: MongoDB-compatible document database — JSON/BSON document storage for content management, catalogs, user profiles where schema flexibility matters but relationships aren't graph-shaped.

**Scalability**
- Neptune: Up to 15 read replicas sharing storage (Aurora-style storage architecture), storage auto-scales to 128 TiB; Neptune Serverless available for variable workloads.
- DocumentDB: Similarly Aurora-storage-based, up to 15 read replicas, storage auto-scales up to 64 TiB (varies by engine version); DocumentDB Elastic Clusters now support horizontal sharding for write scaling beyond single-writer limits.

**Availability**
- Both: 99.99% SLA, Multi-AZ by design (storage replicated 6-way across 3 AZs, same lineage as Aurora), fast failover <30s typical.

**Latency**
- Neptune: Optimized for traversal queries (multi-hop relationship queries) — a query like "friends of friends of friends" is fast because it's index-free adjacency, whereas the same in RDS would require expensive recursive joins.
- DocumentDB: Optimized for single-document retrieval/aggregation pipelines; not optimized for deep relationship traversal.

**Operational overhead**
- Both fully managed, no OS-level patching; DocumentDB requires understanding MongoDB driver compatibility version differences (not 100% API parity with native MongoDB, especially newer MongoDB features).
- Neptune requires familiarity with graph query languages (Gremlin/SPARQL/openCypher) — a skill-set differentiator for teams.

**Pricing characteristics**
- Both priced like Aurora: instance-hour + storage GB-month + I/O (or I/O-Optimized option) + backup storage beyond retention.
- Neptune Serverless bills per NCU (Neptune Capacity Unit) similar to Aurora Serverless ACU — good for spiky graph workloads.

**Encryption/security**
- Both support KMS encryption at rest, TLS in transit, IAM database authentication, VPC-only deployment (no public endpoint by default) — identical security posture pattern to Aurora.

**Consistency model**
- Both: Strong consistency on primary writer; eventual consistency on read replicas (same Aurora storage architecture behavior).

**Limitations**
- Neptune: Not a general-purpose DB — poor fit for tabular reporting or simple CRUD; steep learning curve for graph query languages; no SQL.
- DocumentDB: Not 100% MongoDB API-compatible (certain aggregation operators / newer MongoDB features may be unsupported) — exam may test "migrating self-managed MongoDB, need compatibility check."

**Exam trigger words**
- "relationships between entities," "graph traversal," "fraud detection network," "recommendation engine," "social graph," "Gremlin/SPARQL" → Neptune.
- "MongoDB compatible," "JSON documents," "migrate existing MongoDB workload to managed service" → DocumentDB.

**Common traps**
- Choosing DynamoDB for graph-relationship-heavy questions instead of Neptune — DynamoDB can't efficiently do multi-hop traversal queries.
- Assuming DocumentDB = MongoDB fully — some driver/feature version gaps exist; exam sometimes tests "requires code changes" caveat during migration questions.
- Forgetting both are VPC-only services (no default public access) — relevant for connectivity/architecture questions.

---

### 8. Redshift vs RDS

**Primary use case**
- Redshift: OLAP — data warehousing, complex analytical queries/aggregations over large historical datasets (petabyte scale), BI tool backend.
- RDS: OLTP — transactional workloads, frequent small reads/writes, application backend.

**Scalability**
- Redshift: Scales via adding nodes to a cluster (columnar, MPP architecture) or Redshift Serverless (auto-scales compute in RPUs); RA3 node types decouple compute/storage.
- RDS: Vertical scaling of a single instance + limited read replicas — not designed for MPP-style parallel analytical scans.

**Availability**
- Redshift: Single-AZ by default historically, but Multi-AZ support now available for Redshift (relatively newer capability) for higher availability of the cluster; automated snapshots to S3.
- RDS: Standard Multi-AZ synchronous replication model (well-established).

**Latency**
- Redshift: Higher latency per query due to complex aggregation scans, but far higher throughput on large scans (columnar storage, zone maps, MPP parallel execution) — bad for point lookups, excellent for `SELECT SUM(...) GROUP BY ... FROM billions_of_rows`.
- RDS: Low latency for point lookups/small transactional queries; degrades severely on large-scale analytical scans (row-based storage, single-node execution in standard engines).

**Operational overhead**
- Redshift: Requires vacuum/analyze maintenance (or auto-vacuum in newer versions), distribution key/sort key design decisions for performance.
- RDS: Requires index tuning, but overall simpler operational model for transactional patterns.

**Pricing characteristics**
- Redshift: Priced per node-hour (or RPU-hour for Serverless) + storage (for RA3, storage is separate on S3-backed managed storage); Reserved Instances available for steady workloads; can pause/resume clusters (provisioned) to save cost during idle periods.
- RDS: Instance + storage + IOPS, similar model to other RDS discussions above.

**Encryption/security**
- Both: KMS at rest, SSL/TLS in transit, VPC deployment, IAM auth support; Redshift additionally integrates tightly with Lake Formation/Glue for governed data lake access patterns.

**Consistency model**
- Redshift: Effectively eventually consistent from a data-freshness standpoint since data is typically loaded via ETL/COPY batches (not real-time transactional writes); not designed for high-frequency single-row transactional consistency.
- RDS: Full ACID transactional consistency, real-time.

**Limitations**
- Redshift: Not suited for high-concurrency small transactional writes (COPY/bulk load is the standard ingestion pattern, not row-by-row INSERT); concurrency scaling add-on needed for many simultaneous BI users.
- RDS: Not suited for scanning/aggregating over huge historical datasets — becomes the classic "why is my dashboard query so slow" exam scenario.

**Exam trigger words**
- "data warehouse," "BI reporting across historical data," "petabyte-scale analytics," "columnar storage," "OLAP" → Redshift.
- "OLTP," "real-time transactional application," "ACID compliance for financial transactions" → RDS.

**Common traps**
- Using RDS as a reporting database for large historical aggregation — exam wants you to recognize the OLAP/OLTP split and route reporting workloads to Redshift (or Athena).
- Forgetting Redshift Serverless exists as the answer for "unpredictable analytics workload, don't want to manage cluster sizing."
- Assuming Redshift is real-time — it's batch/ETL-oriented unless paired with Redshift Streaming Ingestion (Kinesis/MSK direct ingestion, a newer capability worth knowing exists).

---

### 9. Athena vs Redshift

**Primary use case**
- Athena: Serverless, ad-hoc SQL queries directly against data in S3 (data lake) — infrequent/exploratory querying, log analysis, one-off analytics without provisioning infrastructure.
- Redshift: Persistent, high-performance data warehouse for frequent, complex, high-concurrency analytical queries requiring consistent low-latency BI performance.

**Scalability**
- Athena: Fully serverless — automatically scales query execution across many workers per query; no cluster to size.
- Redshift: Scales via node count or Serverless RPU auto-scaling; requires capacity planning even in Serverless mode (base RPU + max RPU config).

**Availability**
- Athena: No infrastructure to fail over — it's a query service on top of durable S3 storage (S3's own 99.99% availability applies).
- Redshift: Cluster-based, so availability depends on node health / Multi-AZ configuration (as discussed above).

**Latency**
- Athena: Query latency varies (seconds to minutes) depending on data format/partitioning — poorly partitioned/non-columnar data (e.g., raw JSON/CSV) is slow and costly; querying Parquet/ORC partitioned data is much faster.
- Redshift: Generally faster and more consistent latency for repeated complex queries because data is already loaded/optimized (sort keys, distribution keys, in-memory result caching) rather than scanned fresh from S3 each time.

**Operational overhead**
- Athena: Zero infrastructure management — just define a schema (via Glue Data Catalog) over existing S3 data.
- Redshift: Requires ETL pipelines to load data, ongoing maintenance (vacuum, distribution key tuning, WLM/queue configuration).

**Pricing characteristics**
- Athena: Pay-per-query, $5 per TB scanned (approx, varies by region) — cost directly tied to how much data your query scans, heavily incentivizing partitioning/columnar formats (Parquet) to reduce scan size and cost.
- Redshift: Pay for provisioned cluster/RPU-hours regardless of query volume (provisioned) or per RPU-second (Serverless) — better economics for frequent, heavy, concurrent querying; Athena becomes expensive/inefficient at very high query frequency on large unoptimized datasets.

**Encryption/security**
- Athena: Encrypts query results in S3 (SSE-S3/SSE-KMS), uses IAM + Lake Formation for fine-grained access control over the data catalog/tables.
- Redshift: KMS encryption, VPC isolation, column-level access control via grants, and integration with Lake Formation for Redshift Spectrum queries.

**Consistency model**
- Athena: Reads whatever is currently in S3 at query time — reflects the latest committed S3 objects (subject to S3 strong read-after-write consistency, now standard) but has no concept of "transactions" — pure read-only query engine (unless using Athena ACID via Iceberg table format, a newer capability).
- Redshift: ACID-ish within loaded data, but again load process itself is batch/ETL-driven.

**Limitations**
- Athena: No support for arbitrary DML at scale like a warehouse (though INSERT INTO / CTAS supported); performance highly dependent on file format/partition design; not ideal for extremely high query concurrency from many BI dashboard users simultaneously (throttling limits per account/region).
- Redshift: Requires upfront capacity planning/cost commitment (unless Serverless); data must be loaded/ETL'd into the cluster (or accessed via Redshift Spectrum for S3 data, blurring the line with Athena).

**Exam trigger words**
- "ad-hoc query," "infrequent analysis," "serverless," "query data directly in S3," "no infrastructure to manage," "pay only for queries run" → Athena.
- "frequent complex BI queries," "many concurrent analysts," "need consistent sub-second/sub-minute performance," "data warehouse" → Redshift.

**Common traps**
- Choosing Athena for high-frequency, high-concurrency BI dashboards — cost and latency can spiral versus a provisioned Redshift cluster; the exam often tests "which is more cost-effective at scale" and the answer flips to Redshift once query frequency is high.
- Forgetting Redshift Spectrum lets Redshift query S3 data directly (external tables) — this is the convergence point between the two services, frequently used as a distractor ("can Redshift query S3 without loading?" — yes, via Spectrum).
- Assuming Athena requires data movement — it does not; it queries S3 in place, which is the key differentiator vs. Redshift's load-then-query model.

---

### Cross-Cutting Exam Themes (Domain 3 & 4)

| Signal in question | Likely intended answer |
|---|---|
| "No ops, unpredictable traffic, key-value" | DynamoDB (on-demand) |
| "Millisecond latency at massive scale, need microseconds" | DAX in front of DynamoDB |
| "Global, active-active, low RPO/RTO relational" | Aurora Global Database |
| "Cheapest way to survive AZ failure for OLTP" | Multi-AZ (single standby) |
| "Offload reporting from primary DB" | Read Replica |
| "Graph/relationship traversal" | Neptune |
| "MongoDB compatibility" | DocumentDB |
| "Petabyte analytics, frequent BI queries" | Redshift |
| "One-off query on S3 data lake, pay-per-query" | Athena |
| "Cache needing persistence/pub-sub/security" | ElastiCache Redis |
| "Simplest raw multi-threaded cache" | ElastiCache Memcached |
| "Cost optimization for idle dev/test databases" | Stop RDS instances (up to 7 days auto-restart) / Aurora Serverless v2 / Redshift pause-resume (verify current Aurora Serverless v2 zero-capacity behavior before the exam, as this has been changing) |

## Networking

*AWS SAA-C03 — Networking Service Comparison Deep-Dive*

---

### 1. ALB vs NLB vs Gateway Load Balancer

| Dimension | ALB (Application LB) | NLB (Network LB) | GWLB (Gateway LB) |
|---|---|---|---|
| **OSI Layer / Mechanism** | L7 — HTTP/HTTPS/gRPC/WebSocket. Terminates TCP, inspects headers/path/host, re-establishes connection to target. | L4 — TCP/UDP/TLS. Passes packets with minimal manipulation; preserves source IP (unless behind another proxy). Uses flow hashing. | L3/L4 (GENEVE encapsulation, port 6081). Operates as a transparent bump-in-the-wire for third-party virtual appliances (firewalls, IDS/IPS, DPI). |
| **Primary Use Case** | Microservices routing, path/host-based routing, container-native apps (ECS/EKS), API layer, WAF integration. | Extreme performance, static IP/EIP requirement, TCP/UDP non-HTTP protocols (gaming, IoT, financial), PrivateLink service endpoint backend. | Centralized third-party virtual appliance insertion (firewall, IDS) for traffic inspection without redesigning VPC routing per-appliance. |
| **Scalability** | Auto-scales horizontally; pre-warming can be requested for sudden spike tests. | Scales to millions of req/sec with ultra-low latency; single static IP per AZ scales without pre-warming (built for burst). | Scales with appliance fleet behind it (via target group of appliances), auto-scaling handled by ASG of appliances. |
| **Availability** | Multi-AZ, cross-zone LB enabled by default (no extra charge as of ALB). | Multi-AZ; cross-zone LB is **disabled by default** and incurs data transfer charges if enabled. | Multi-AZ; deployed with GWLB endpoints (GWLBe) in each AZ for HA appliance access. |
| **Latency/Performance** | Higher latency than NLB due to L7 parsing/connection termination. | Lowest latency of the three — near line-rate, no L7 parsing. | Adds latency for the appliance hop (GENEVE encap/decap) — acceptable trade-off for inspection use cases. |
| **Operational Overhead** | Moderate — listener rules, target groups, health checks per path. | Low — simple TCP/UDP listener + target group. | Higher — requires managing appliance fleet, GWLB endpoint service, route table redirection to GWLBe ENIs. |
| **Pricing** | LCU-based (new connections, active connections, bandwidth, rule evaluations). | LCU-based (different formula — new flows, active flows, bandwidth). No per-rule cost. | GWLB-hours **plus** GLCU-hours (Gateway Load Balancer Capacity Units — a composite metric covering connections/bandwidth) + GWLB Endpoint hourly charge on the consumer side. Directionally similar in shape to Interface Endpoint pricing, but not a flat per-GB charge — verify current pricing page for exact unit definitions. |
| **Security** | Native WAF/Shield integration, SNI-based multi-cert TLS termination, OIDC/Cognito auth at listener. | No WAF integration (not L7-aware); TLS listener supports termination but no header inspection. | Enables centralized security appliance chaining; itself does not inspect — delegates to third-party appliance. |
| **Limitations** | Cannot preserve raw client IP without X-Forwarded-For; no static IP (mitigate with Global Accelerator **or** by placing an NLB in front of the ALB — both are accepted exam answers). | No content-based routing; no WAF. | Requires appliance marketplace AMI or custom appliance; adds architectural complexity; not for simple LB needs. |
| **Exam Trigger Words** | "path-based routing," "host-based routing," "microservices," "container," "WebSocket," "OIDC authentication at LB." | "static IP," "Elastic IP for load balancer," "extreme performance," "preserve source IP," "UDP," "TCP passthrough," "PrivateLink backend." | "third-party firewall/IDS/IPS," "traffic inspection appliance," "GENEVE," "centralized security appliance fleet." |
| **Common Traps** | Assuming ALB can give you a fixed IP — it can't; must front with Global Accelerator or an NLB. Forgetting ALB doesn't do raw TCP well. | Assuming cross-zone LB is free/on by default (it's off by default and billed when enabled, unlike ALB). Assuming NLB does content routing. | Confusing GWLB with GWLB **Endpoint** (GWLBe) — GWLB sits in appliance VPC, GWLBe sits in consumer VPC/subnet for route redirection. Exam loves testing this split. |

---

### 2. Route 53 Routing Policies

| Policy | Mechanism | Use Case | Health Check Support | Exam Trigger Words | Common Traps |
|---|---|---|---|---|---|
| **Simple** | Single record, no health check, can return multiple values (client picks randomly, no failover logic). | Single resource, dev/test, no HA requirement. | ❌ No automatic failover behavior — there's nothing to fail over to. (A health check can be attached only in narrow alias-to-AWS-resource edge cases, but it does not provide failover logic the way Failover/Multivalue policies do.) | "single resource," "no failover needed." | Assuming Simple + multiple IPs = load balancing with failover — it's NOT; it's just random client-side selection with zero health awareness. |
| **Weighted** | Assign relative numeric weights to record sets; traffic split proportionally (the Route 53 console commonly bounds this field to 0–255 — verify the current limit in AWS docs before treating it as a fixed exam fact). | A/B testing, canary deployments, gradual migration. | ✅ Yes | "canary deployment," "percentage of traffic," "gradual rollout," "A/B testing." | Setting weight to 0 stops traffic to that record but doesn't delete it (useful for temporary removal) — exam may test this nuance. |
| **Latency-based (LBR)** | Routes to region with lowest measured **network latency** from Route 53's perspective (not literal geographic distance). | Multi-region active-active deployments optimizing for user experience/performance. | ✅ Yes (recommended — combine with failover) | "lowest latency," "best performance," "multi-region deployment." | Confusing with Geoproximity — latency-based uses AWS-measured latency, NOT geographic distance. Two regions can have a "wrong" closest match if network paths differ. |
| **Failover** | Active-passive DNS failover; primary/secondary designation; requires health check on primary. | DR architecture, active-passive multi-region. | ✅ Required on primary | "active-passive," "disaster recovery," "primary and secondary site." | Forgetting the health check is **mandatory** on the primary record for failover to function — without it, failover never triggers. |
| **Geolocation** | Routes based on **end-user's geographic location** (continent/country/state), not network path. | Content localization/licensing restrictions, compliance (data residency), language-specific content. | ✅ Yes | "compliance," "restrict content by country," "localize content," "legal/regulatory requirement." | Must configure a "default" record to catch unresolvable locations — otherwise those users get NXDOMAIN. Exam frequently tests this gap. |
| **Geoproximity** | Routes based on geographic distance between user and resource, with an optional **bias** value to expand/shrink the "pull" of a region. Requires Route 53 Traffic Flow. | Shifting traffic proportionally between regions by adjusting bias without moving infrastructure. | ✅ Yes | "bias," "shift traffic by geographic region," "expand/shrink regional traffic footprint," "Traffic Flow." | Requires **Route 53 Traffic Flow** (policy records, additional cost) — plain Route 53 console doesn't fully expose bias without Traffic Flow. Also works with non-AWS resources if you supply lat/long. |
| **Multivalue Answer** | Returns up to 8 healthy records randomly per query; each can have a health check. | Simple client-side load balancing + health checking WITHOUT a load balancer. | ✅ Yes (per record) | "multiple IP addresses with health checks," "simple load balancing without ELB," "DNS-level health check." | This is NOT a substitute for a real load balancer at scale — it's DNS-level pseudo-LB. Exam distinguishes it from Simple (Simple = no health check; Multivalue = up to 8 healthy records with health checks). |

**Cross-cutting exam notes:** Route 53 health checks can check endpoints directly, check other health checks (calculated health checks), or check CloudWatch alarms. Alias records (vs CNAME) are required for zone apex records pointing to AWS resources (ALB, CloudFront, S3 website endpoints) and don't incur a query charge when pointing to AWS resources.

---

### 3. CloudFront vs Global Accelerator

| Dimension | CloudFront | Global Accelerator |
|---|---|---|
| **Mechanism** | CDN — caches content at a large, continually-growing global network of edge locations (verify current count on the AWS site rather than relying on a fixed number); L7 (HTTP/HTTPS), terminates TLS at edge. | Anycast static IPs (2 by default) routed over AWS global network backbone to nearest healthy endpoint; L4 (TCP/UDP), no caching. |
| **Primary Use Case** | Static/dynamic web content, video streaming, API acceleration with caching, S3/ALB/MediaStore origin content delivery. | Non-HTTP TCP/UDP workloads, gaming, VoIP, IoT, or HTTP workloads needing **static entry-point IPs** and fast regional failover without caching. |
| **Scalability** | Massive — edge network absorbs load, offloads origin. | Scales via AWS backbone; doesn't reduce origin load (no caching) but improves path to origin. |
| **Availability** | High; origin failover (origin groups: primary + secondary) supported for HTTP(S) origins. | High; automatic endpoint failover across regions/AZs based on health checks, typically sub-minute. |
| **Latency/Performance** | Reduces latency via caching at edge (best for cacheable content). | Reduces latency by routing onto AWS backbone as early as possible (best for uncacheable/dynamic or non-HTTP traffic) — bypasses public internet congestion. |
| **Operational Overhead** | Cache invalidation management, behavior/path patterns, origin access control (OAC) setup for S3. | Low — mostly endpoint group + listener config; no cache logic needed. |
| **Pricing** | Pay for data transfer out + requests (tiered by region), no hourly fee. | Fixed hourly fee **plus** data transfer premium (DT-premium) — generally pricier for low-traffic use cases. |
| **Security** | Native AWS WAF, Shield, Origin Access Control/Identity (restrict S3 direct access), signed URLs/cookies, field-level encryption. | Shield Standard included; no WAF (it's not L7); provides DDoS resilience via Anycast absorbing at edge. |
| **Limitations** | Not ideal for pure TCP/UDP non-HTTP traffic; cache invalidation isn't instant (costs extra beyond free tier). | No content caching — doesn't reduce origin compute load; no signed URL/cookie mechanism; endpoint types are limited to ALB, NLB, EC2 instances, and Elastic IPs. |
| **Exam Trigger Words** | "cache static content," "reduce origin load," "video streaming," "signed URLs," "edge caching," "WAF at edge." | "static IP addresses for application," "non-HTTP protocol acceleration," "fast regional failover for TCP/UDP," "gaming/VoIP," "improve performance without caching." |
| **Common Traps** | Assuming CloudFront improves ALL traffic types equally — dynamic, non-cacheable content gets less benefit (though CloudFront does have some TCP optimization for dynamic content too). | Assuming Global Accelerator caches — it does NOT; it only optimizes network path and provides static IPs + fast failover. Also: don't confuse it with Route 53 latency routing — GA operates at the network/anycast layer, not DNS. |

**Combined use case exam pattern:** CloudFront and Global Accelerator solve different problems and are not typically chained — Global Accelerator's supported endpoint types are ALB, NLB, EC2 instances, and Elastic IPs; a **CloudFront distribution is not a supported GA endpoint**, so "GA in front of CloudFront" is not an available architecture. In practice, GA is paired with ALB/NLB/EC2 for non-cacheable global apps needing static IPs, while CloudFront pairs with S3/ALB for cacheable content delivery.

---

### 4. VPC Peering vs Transit Gateway

| Dimension | VPC Peering | Transit Gateway (TGW) |
|---|---|---|
| **Mechanism** | 1:1 direct network connection between two VPCs using private IP; non-transitive. | Regional hub-and-spoke router; connects VPCs, VPNs, Direct Connect gateways via attachments; supports transitive routing. |
| **Primary Use Case** | Small number of VPCs needing direct connectivity (e.g., 2–5), simple architectures. | Large-scale multi-VPC/multi-account/multi-region hub architectures (hundreds of VPCs), centralized egress, shared services VPC. |
| **Scalability** | Does NOT scale well — peering is non-transitive, so full mesh required (N(N-1)/2 connections) as VPC count grows. | Scales to thousands of attachments; single hub simplifies routing exponentially vs. mesh. |
| **Availability** | Highly available (no single point of failure — it's just routing), but each peering must be individually managed. | Highly available, AWS-managed redundant infrastructure across AZs within the region. |
| **Latency/Performance** | Very low latency — direct route over AWS backbone, no intermediate hop. | Slightly higher latency than direct peering due to TGW hop, but still backbone-based and low. |
| **Operational Overhead** | Low per-connection but grows quadratically with VPC count (route table entries per peering, no transitive simplification). | Higher initial setup complexity but low incremental overhead — new VPC = one attachment + route table entry. |
| **Pricing** | No hourly charge; pay only for data transfer between VPCs (cross-AZ/cross-region rates apply). | Hourly charge per attachment + per-GB data processing charge — more expensive at low scale, cheaper at high scale (avoids mesh sprawl). |
| **Security** | Security Groups can be referenced across peered VPCs (same region) — a key differentiator. | Security groups CANNOT be referenced across TGW attachments directly (must use CIDR-based rules in SGs); TGW supports route table segmentation for isolation (multi-tenant). |
| **Limitations** | Non-transitive (A-B and B-C peering does NOT allow A-C traffic); no overlapping CIDRs allowed; no edge-to-edge routing (can't route through peered VPC to VPN/DX/IGW of that VPC). | No SG cross-referencing; overlapping CIDRs among attachments still problematic; regional resource — cross-region requires TGW peering attachments, and TGW-to-TGW peering is itself non-transitive. |
| **Exam Trigger Words** | "two VPCs," "simple direct connection," "reference security groups across VPCs," "cost-sensitive small-scale." | "hub and spoke," "hundreds of VPCs," "centralized connectivity," "multiple accounts," "transitive routing," "shared services VPC," "simplify complex mesh." |
| **Common Traps** | Believing peering is transitive — classic exam trap: "VPC A peered to B, B peered to C, can A reach C?" **No.** Also: peering does NOT support edge-to-edge routing through the peer's IGW/VPN/DX. | Assuming TGW allows security group referencing across attachments the same way peering does within a region — it does not; must use CIDR/prefix-list based SG or NACL rules. |

---

### 5. Site-to-Site VPN vs Direct Connect

| Dimension | Site-to-Site VPN | Direct Connect (DX) |
|---|---|---|
| **Mechanism** | IPsec tunnels over the public internet, terminating on a Virtual Private Gateway (VGW) or Transit Gateway. | Dedicated private physical network connection from on-prem to AWS via DX location/partner, bypassing public internet entirely. |
| **Primary Use Case** | Quick setup, backup/failover path for DX, low-to-moderate bandwidth needs, temporary/POC connectivity. | Consistent, high-bandwidth, low-latency production workloads (large data transfer, hybrid architectures, database replication). |
| **Scalability** | Each tunnel is capped at roughly 1.25 Gbps; use ECMP with multiple tunnels/Transit Gateway for aggregate throughput. | Scales to 1/10/100 Gbps dedicated connections (or hosted connections from 50 Mbps–10 Gbps via partners); can aggregate with LAG. |
| **Availability** | Each VPN connection provisions 2 tunnels (different AWS endpoints) for HA by default. | Single DX connection is a SPOF unless you provision a second connection (ideally in a different DX location) — AWS recommends dual DX for resilience, or DX + VPN as backup. |
| **Latency/Performance** | Variable — subject to public internet congestion/jitter; encryption overhead. | Consistent, predictable low latency; no internet congestion; supports jumbo frames (MTU 9001) for higher throughput efficiency. |
| **Operational Overhead** | Low — provision in minutes via console/API. | High — physical cross-connect provisioning typically takes weeks to months; requires coordination with DX location/partner. |
| **Pricing** | Hourly connection charge + data transfer OUT charge (standard rates). | Port-hour charge (by capacity) + significantly cheaper data transfer OUT rates than internet/VPN — cost-effective at scale. |
| **Security** | Encrypted by design (IPsec) — inherently secure in transit. | NOT encrypted by default (it's a private dedicated line) — must layer VPN over DX (DX + VPN) or use MACsec (available on certain DX ports) if encryption-in-transit is a compliance requirement. |
| **Limitations** | Bandwidth ceiling per tunnel; internet-dependent reliability/jitter. | Long lead time to provision; requires physical presence at DX location or partner relationship; higher fixed cost even at low usage. |
| **Exam Trigger Words** | "quick to set up," "backup connection," "encrypted internet-based connection," "low upfront cost." | "consistent network performance," "large data volumes," "avoid public internet," "dedicated connection," "hybrid cloud production workload," "MTU/jumbo frames." |
| **Common Traps** | Assuming a single VPN connection = single tunnel (it's actually 2 tunnels by default for HA). | Assuming DX is encrypted by default — it is NOT; must explicitly add VPN over DX or MACsec for encryption. Also: exam loves "DX takes too long, need connectivity NOW" → answer is VPN as an interim/backup solution, potentially via DX failover pattern (VPN as backup to DX, or "DX + VPN" combined for both performance and resilience). |

**Exam pattern:** "Fastest reliable hybrid connectivity with encryption and resilience" → Direct Connect + Site-to-Site VPN as backup (or DX with MACsec). "Need connectivity today while DX is being provisioned" → VPN now, DX later.

---

### 6. NAT Gateway vs Internet Gateway

| Dimension | NAT Gateway | Internet Gateway (IGW) |
|---|---|---|
| **Mechanism** | Managed, AZ-scoped service performing source NAT for **outbound-only** IPv4 traffic from private subnets. | Horizontally scaled, redundant VPC component providing **bidirectional** internet connectivity (allows inbound + outbound) for resources with public IPs. |
| **Primary Use Case** | Private subnet resources (e.g., app servers, DB patch downloads) needing outbound internet access without being reachable from the internet. | Public subnet resources (bastion hosts, public-facing ALBs, web servers) requiring direct internet reachability. |
| **Scalability** | Scales automatically to a high per-gateway bandwidth ceiling that AWS has raised over time (check the current published limit before quoting an exact figure — it has changed from earlier stated values); deploy one per AZ for HA and to avoid cross-AZ data charges. | Scales automatically, no bandwidth constraints documented as a bottleneck — fully AWS managed. |
| **Availability** | AZ-scoped (a single NAT GW is a SPOF for its AZ) — best practice: 1 NAT GW per AZ. | Regionally resilient by design (redundant across AZs automatically) — one IGW serves entire VPC across all AZs. |
| **Latency/Performance** | Minimal added latency; performance scales with connections/bandwidth automatically. | No material latency addition — direct routing. |
| **Operational Overhead** | Low but requires per-AZ deployment planning + Elastic IP association + route table updates per subnet. | Very low — attach once per VPC, update route tables; no scaling decisions needed. |
| **Pricing** | Hourly charge PLUS per-GB data processing charge (this is often the highest hidden cost in a VPC design) — NAT Instance is the cheaper-but-unmanaged alternative. | No hourly charge for the IGW itself; only standard data transfer OUT rates apply. |
| **Security** | Cannot be a security boundary itself — outbound only, no inbound initiation possible (stateful-like behavior for return traffic). | Must be paired with SGs/NACLs for actual access control — IGW itself does zero filtering. |
| **Limitations** | IPv4 only for NAT Gateway (use egress-only IGW for IPv6 outbound-only); cannot be used for inbound connections; not shareable across AZs without cross-AZ charges. | Requires resources to have a public IP/EIP and appropriate route table entries — doesn't work for private-IP-only resources wanting outbound access. |
| **Exam Trigger Words** | "private subnet needs outbound internet access," "instances should not be reachable from internet," "one-way outbound connectivity," "cost optimization for NAT" (→ compare to NAT instance). | "public subnet," "instances need to be reached from the internet," "bastion host," "internet-facing." |
| **Common Traps** | Forgetting NAT Gateway is AZ-scoped — architecture with one NAT GW in one AZ creates a hidden SPOF and cross-AZ data transfer costs for other AZs' private subnets. Confusing with **egress-only internet gateway** (IPv6-specific, stateless-outbound-only equivalent). | Assuming attaching an IGW alone gives internet access — route table AND SG/NACL AND public IP assignment are all still required; a classic multi-part exam question. |

---

### 7. Security Groups vs NACLs

| Dimension | Security Groups (SG) | Network ACLs (NACL) |
|---|---|---|
| **Mechanism/Layer** | Instance/ENI level (stateful) — operates at the instance boundary. | Subnet level (stateless) — operates at the subnet boundary. |
| **State** | **Stateful** — return traffic automatically allowed regardless of outbound rules. | **Stateless** — must explicitly allow both inbound AND outbound rules (e.g., ephemeral ports 1024-65535 for return traffic). |
| **Rule Evaluation** | Evaluates ALL rules before deciding (only "allow" rules exist — no explicit deny). | Evaluates rules **in numeric order** (lowest number first) until a match; supports explicit ALLOW and DENY rules. |
| **Primary Use Case** | Fine-grained instance-level access control (e.g., "only allow port 443 from ALB SG"). | Subnet-wide coarse control, explicit deny (e.g., blocking a known malicious IP range at the subnet level). |
| **Scalability** | Reference other SGs by ID (great for dynamic architectures, autoscaling); default of 5 SGs per ENI (soft limit, adjustable), default rule limit per SG (60 inbound/60 outbound, adjustable) — confirm current defaults in AWS Service Quotas before relying on exact figures. | Default and custom NACLs per subnet; simpler at scale for blanket rules but doesn't reference SGs/dynamic groups. |
| **Availability** | N/A (logical construct, not a scaled resource) — always available/applied per ENI. | N/A — applied automatically to all subnet traffic; default NACL allows all traffic. |
| **Operational Overhead** | Moderate — must manage per-application/tier SG rules; easier long-term due to SG-referencing reducing IP churn issues. | Higher for fine-grained use because of stateless nature (must remember ephemeral port ranges) — typically used sparingly for blanket allow/deny. |
| **Pricing** | Free. | Free. |
| **Security Considerations** | Cannot explicitly DENY — only allow (default deny-all implicit). Best for positive-allow-list security posture. | Can explicitly DENY specific IPs/ranges — useful for quickly blocking a known bad actor without touching every SG. |
| **Limitations** | Cannot block specific IP if using broad CIDR allows elsewhere at SG level in same chain (no deny). Applies at ENI, so must be attached to every relevant instance/interface. | Because stateless, misconfiguring ephemeral port range is the #1 real-world/exam error, breaking return traffic. Order-dependent (rule #100 evaluated before #200). |
| **Exam Trigger Words** | "stateful," "instance-level," "allow traffic from another security group," "no deny rules." | "stateless," "subnet-level," "explicitly deny/block an IP address," "rule numbers/order," "ephemeral ports." |
| **Common Traps** | Forgetting SGs are stateful — candidates over-configure outbound rules unnecessarily when inbound alone suffices for the return path. | Forgetting to allow ephemeral ports (1024-65535) on both inbound and outbound for NACL when troubleshooting "SG is correct but connection still fails" scenarios — classic exam scenario question. Also: NACL rule numbers matter — a DENY at rule 100 blocks even if ALLOW exists at rule 200. |

**Defense-in-depth exam pattern:** SG = allow-list at instance; NACL = additional subnet-level guardrail, often used to explicitly block/deny specific malicious CIDR ranges that SGs structurally cannot deny.

---

### 8. PrivateLink vs VPC Peering

| Dimension | AWS PrivateLink | VPC Peering |
|---|---|---|
| **Mechanism** | Exposes a specific **service** (via NLB or GWLB) as an ENI (Interface Endpoint) in the consumer VPC — one-directional service exposure, not full network connectivity. | Full bidirectional network-level connection between two entire VPC CIDR ranges. |
| **Primary Use Case** | SaaS providers exposing a service to many customer VPCs without network merging; multi-tenant service architectures; connecting to AWS services (e.g., S3 via Interface Endpoint) or third-party SaaS securely. | Full network integration between two VPCs — needed when broader resource-to-resource communication (not just a single service) is required. |
| **Scalability** | Highly scalable — a single service can be consumed by many customer VPCs (including cross-account) without CIDR conflicts. | Poor at scale — full mesh problem; also CANNOT have overlapping CIDR ranges between peered VPCs. |
| **Availability** | HA via multi-AZ ENI deployment of the Interface Endpoint. | HA (AWS-managed routing), but individual peering connections must be managed per pair. |
| **Latency/Performance** | Low latency — traffic stays on AWS backbone, single hop via ENI. | Low latency — direct backbone routing, arguably marginally lower since no service-layer indirection. |
| **Operational Overhead** | Consumer side: simple (create endpoint, associate SG). Provider side: requires NLB/GWLB + endpoint service configuration + accepting connection requests. | Low per-pair but grows with VPC count; requires route table updates on both sides for every peering. |
| **Pricing** | Hourly charge per AZ for the endpoint + per-GB data processing charge. | No hourly charge; standard data transfer pricing only. |
| **Security** | Strong isolation — consumer only sees the exposed service/port, NOT the provider's full VPC/network; no CIDR overlap issue since it's not a network merge — it's a private ENI. | Full network exposure between VPCs (whatever routes/SGs allow) — broader blast radius if misconfigured; overlapping CIDRs will break it entirely. |
| **Limitations** | Only exposes specific services (TCP-based via NLB), not full network reachability; NOT transitive (endpoint only reaches the specific backend service). | Non-transitive; no overlapping CIDR; no edge-to-edge routing through the peer's other connections (VPN/DX/IGW). |
| **Exam Trigger Words** | "expose a service to multiple VPCs/accounts without peering," "SaaS provider," "overlapping CIDR ranges," "minimize exposed attack surface," "one specific service/application." | "full VPC-to-VPC connectivity," "access all resources across VPCs," "CIDRs must not overlap." |
| **Common Traps** | Assuming PrivateLink gives full network access — it does NOT; it's service-specific, single-port exposure via ENI, much narrower than peering. Also: PrivateLink is the standard exam answer when overlapping CIDRs exist between two parties (since it doesn't merge networks). | Assuming peering can expose "just one service" cleanly — technically possible via SG restriction, but the exam expects PrivateLink as the "least privilege / minimal exposure" answer when the scenario emphasizes multi-tenant SaaS or overlapping CIDR. |

---

### 9. Interface Endpoint vs Gateway Endpoint (VPC Endpoints)

| Dimension | Interface Endpoint | Gateway Endpoint |
|---|---|---|
| **Mechanism** | ENI with a private IP deployed in your subnet(s), backed by PrivateLink; supports most AWS services + PrivateLink-enabled SaaS/partner/custom services. | A route table target/prefix-list entry (no ENI) added to route table pointing to the AWS service — only for **S3** and **DynamoDB**. |
| **Primary Use Case** | Private access to most AWS services (e.g., SNS, SQS, KMS, Secrets Manager, EC2 API, Kinesis) and PrivateLink-shared third-party/cross-account services, without traversing internet/NAT. | Private, no-additional-cost access to S3/DynamoDB from within a VPC without using NAT Gateway/IGW. |
| **Scalability** | Deploy per-AZ ENIs for HA; DNS resolution (private DNS) automatically routes standard service endpoint names to the private ENI. | Route table based — automatically available to any subnet whose route table has the endpoint entry; scales trivially. |
| **Availability** | Multi-AZ if you provision ENI in multiple subnets/AZs. | Inherently regional/highly available (route-table construct, no single point of failure). |
| **Latency/Performance** | Very low latency (private ENI, backbone routing) — negligible overhead vs public endpoint. | Very low latency, essentially route-table redirection over the backbone — no ENI hop at all, arguably marginally more efficient. |
| **Operational Overhead** | Moderate — must enable private DNS, manage SGs on the endpoint ENI, deploy per AZ. | Very low — one route table entry; also must update endpoint policy and route tables in each associated subnet. |
| **Pricing** | Hourly charge per AZ + per-GB data processing charge. | **Free** — no hourly charge, no data processing charge. |
| **Security** | Controlled via Security Groups (on the ENI) AND endpoint policies (resource-based IAM policy on the endpoint). | Controlled via endpoint policies AND route table/subnet association — no SG since there's no ENI. |
| **Limitations** | Costs scale with usage/AZ count; requires private DNS toggling to avoid breaking existing SDK/CLI calls to public service endpoints. | Only supports S3 and DynamoDB; cannot be extended to other services; cannot be accessed from on-premises via VPN/DX directly (gateway endpoints are VPC-route-table scoped only) — for on-prem private S3 access, must use Interface Endpoint instead. |
| **Exam Trigger Words** | "private access to AWS service without internet," "most AWS services," "PrivateLink," "on-premises access to S3 via VPN/DX" (→ needs Interface Endpoint, NOT Gateway, since gateway endpoints aren't reachable from on-prem). | "S3 or DynamoDB private access," "avoid NAT Gateway data charges for S3 traffic," "no additional cost private access." |
| **Common Traps** | Forgetting to enable "Private DNS" — without it, applications must use the endpoint-specific DNS name rather than the standard service DNS name, breaking unmodified applications. | Classic trap: on-premises resources connecting via Direct Connect/VPN CANNOT use a Gateway Endpoint to reach S3 privately — only Interface Endpoints support that hybrid access pattern. Also, forgetting Gateway Endpoints require route table association per subnet (a subnet without the route entry has no access even though the endpoint exists in the VPC). |

---

### Quick-Reference Exam Decision Triggers

- **"Static IP for HTTP app behind ALB"** → Global Accelerator (not CloudFront) or an NLB placed in front of the ALB — both are valid.
- **"Overlapping CIDRs between two companies' VPCs"** → PrivateLink, never Peering/TGW.
- **"On-prem needs private S3 access via Direct Connect"** → Interface Endpoint (S3), not Gateway Endpoint.
- **"Hundreds of VPCs, need transitive routing"** → Transit Gateway, not Peering.
- **"DR active-passive across regions"** → Route 53 Failover routing with health check on primary.
- **"Gradual canary rollout of new API version"** → Route 53 Weighted routing.
- **"Compliance-driven content restriction by country"** → Route 53 Geolocation (with default record!).
- **"Need encryption over a dedicated private connection"** → Direct Connect + VPN (or MACsec), DX alone is unencrypted.
- **"Explicitly deny a malicious IP subnet-wide"** → NACL, not SG (SGs can't deny).
- **"Insert third-party firewall/IDS transparently"** → Gateway Load Balancer + GWLB Endpoint.

## Messaging

*AWS SAA-C03 — Messaging & Decoupling Deep Dive (Domain 2: Resilient Architectures)*

---

### 1. SQS vs SNS

**Core distinction:** SQS is a **pull-based queue** (point-to-point, one consumer group processes each message); SNS is a **push-based pub/sub topic** (fan-out to many subscribers).

| Dimension | SQS | SNS |
|---|---|---|
| Primary use case | Decouple producer from consumer(s); buffer/level load spikes; work queue for async processing | Fan-out one event to many independent subscribers (SQS, Lambda, HTTP/S, email, SMS, Firehose, mobile push) |
| Scalability | Virtually unlimited throughput (Standard); horizontally scaled automatically | Virtually unlimited publish throughput; supports fan-out to a very large number of subscribers per topic (millions, per AWS's current documented quotas — treat the exact figure as subject to change, not something to memorize) |
| Availability | Multi-AZ by default within a region | Multi-AZ by default within a region |
| Latency | Sub-second for Standard; polling adds latency (unless long polling) | Near real-time push (typically <1s to invoke subscribers) |
| Operational overhead | Zero infra; must manage visibility timeout, DLQ, polling logic | Zero infra; must manage subscription filtering, delivery retry policies |
| Pricing | Per request (API calls), charged for polling even with no messages (mitigated by long polling) | Per publish + per delivery (delivery pricing varies by protocol — SMS/email costlier) |
| Consistency/ordering | Standard = best-effort ordering, at-least-once, possible duplicates; FIFO = strict ordering, exactly-once | No ordering guarantee across subscribers unless using FIFO SNS→FIFO SQS; at-least-once delivery |
| Limitations | Messages retained max 14 days; 256KB payload limit (use S3 + Extended Client Library for larger); no native fan-out | No message persistence/replay — if subscriber is down and it's not SQS-backed, message is lost (unless retry policy catches transient failures) |
| Exam trigger words | "decouple producer and consumer," "buffer requests," "retry failed processing," "asynchronous worker queue" | "fan-out," "notify multiple systems," "one event, many subscribers," "pub/sub" |
| Common traps | Assuming SQS alone can broadcast to multiple consumers — it can't (only one consumer group gets each message unless you use separate queues). Forgetting DLQ for poison-pill messages. | Assuming SNS retains/replays messages — it does NOT persist undelivered messages for non-queue endpoints. Exam loves the "SNS fan-out to SQS" pattern as the canonical decoupled, durable fan-out answer — SNS alone talking to HTTP endpoints is fragile. |

**Canonical exam pattern:** SNS → multiple SQS queues (fan-out + durability) is the gold-standard combo when a question says "one order event must trigger independent processing in billing, shipping, and inventory systems, each processed reliably even if a service is down."

---

### 2. SQS Standard vs FIFO

| Dimension | Standard | FIFO |
|---|---|---|
| Primary use case | High-throughput, order-doesn't-matter workloads (e.g., log ingestion, generic task queue) | Order-sensitive workloads (e.g., financial transactions, sequential command processing, ensuring dedup) |
| Scalability | Nearly unlimited TPS | Up to 3,000 msg/sec with batching (300/sec without) — this is a per-queue, per-API-action ceiling, not one that grows simply by adding more Message Group IDs; Message Group ID governs ordering scope and consumer-side parallelism, not the raw throughput ceiling |
| Availability | Multi-AZ | Multi-AZ |
| Latency | Low latency | Slightly higher due to dedup/ordering overhead, still sub-second typically |
| Operational overhead | Minimal — no MessageGroupId/DeduplicationId management | Must design MessageGroupId strategy for parallel processing/ordering scope; must supply/enable dedup (content-based or explicit ID) |
| Pricing | Standard SQS pricing | FIFO queues carry a real, modest per-request price premium over Standard (higher price per million requests on the SQS pricing page) — this is a direct pricing difference, not just an indirect cost from needing more queues/groups at scale |
| Consistency/ordering | At-least-once delivery, **no ordering guarantee**, possible duplicates | Exactly-once processing (within 5-min dedup window), **strict FIFO ordering per Message Group** |
| Limitations | Duplicates and out-of-order delivery possible | Name must end in `.fifo`; lower max throughput per queue; single message group = fully serialized processing (bottleneck) |
| Exam trigger words | "high throughput," "order doesn't matter," "maximize throughput" | "exactly once," "strict ordering," "must be processed in order," "no duplicates" |
| Common traps | Assuming Standard guarantees order "most of the time" is good enough when requirement explicitly says strict ordering — it's not designed for that. | Assuming FIFO throughput scales linearly just by adding message groups — under default High Throughput Mode the 300/3,000 TPS ceiling is per-queue regardless of group count; groups mainly control ordering/parallel consumption, and truly higher aggregate throughput requires additional queues (with request-level cost implications), not just more groups. Also assuming FIFO can be used with SNS Standard topics — you need a **FIFO SNS topic** to feed a FIFO SQS queue with ordering preserved end-to-end. |

**Key nuance for 2026 scope:** High-throughput FIFO mode (enabled by default in new FIFO queues) supports up to 3,000 TPS per API call with batching without requiring you to shard artificially across many Message Group IDs — exam questions increasingly test whether you know FIFO ≠ automatically slow, and that this throughput ceiling is a queue-level quota rather than something message groups multiply.

---

### 3. SNS vs EventBridge

| Dimension | SNS | EventBridge |
|---|---|---|
| Primary use case | Simple pub/sub fan-out with a small, generally fixed set of subscribers; also apps needing SMS/email/mobile push | Event-driven architectures with **content-based routing**, SaaS integration, multi-source event buses, and complex filtering across many producers/consumers |
| Scalability | Massive fan-out (thousands of subscribers per topic) | Scales to many event buses, rules, and targets; higher-level orchestration of events across accounts/regions |
| Availability | Multi-AZ | Multi-AZ |
| Latency | Near real-time (~sub-second) | Near real-time but generally slightly higher latency than SNS due to rule evaluation engine |
| Operational overhead | Simple topic + subscription model | More setup: event buses, rules, schema registry, input transformers — more powerful but heavier to configure |
| Pricing | Pay per publish/delivery | Pay per event published (custom events), plus schema discovery costs; **no charge for AWS service-generated events on default bus** in many cases |
| Consistency/ordering | No ordering (unless FIFO) | No strict ordering guarantee (event bus is not FIFO); best-effort delivery, at-least-once |
| Limitations | Filter policies are simpler than EventBridge's pattern matching (fewer attributes/combinations, no schema registry); can't efficiently express deeply nested content rules the way EventBridge event patterns can | Rule matching adds latency; not meant for very high throughput low-latency streaming (that's Kinesis/SQS territory); harder to reason about many overlapping rules |
| Exam trigger words | "simple fan-out," "SMS/email notification," "mobile push" | "event bus," "SaaS integration (e.g., Zendesk, Datadog)," "content-based filtering," "route events based on payload content," "schema registry," "decouple based on event patterns," "third-party SaaS events" |
| Common traps | Assuming SNS can *only* filter on message attributes and never payload content — since 2022 SNS also supports filter policies scoped to the message body, so simple body-based filtering is possible. EventBridge remains the better choice when the requirement needs deep/nested JSON pattern matching, numeric ranges, or multi-source aggregation, but don't assume SNS has zero content-filtering capability. | Assuming EventBridge replaces SNS for simple fan-out — it's often overkill/costlier for trivial pub/sub. Also assuming EventBridge is ordered — it is NOT a FIFO service. |

**Exam heuristic:** If the scenario mentions **SaaS partner integration** (e.g., "receive events from Salesforce/PagerDuty"), or **schema discovery/registry**, or **routing rules based on deeply nested JSON payload fields** → EventBridge. If it's a straightforward "notify N endpoints of an event," optionally with light body/attribute filtering → SNS.

---

### 4. EventBridge vs SQS

| Dimension | EventBridge | SQS |
|---|---|---|
| Primary use case | Routing/orchestrating events from many sources (AWS services, SaaS, custom apps) to many targets based on rules | Simple, durable buffer/queue between a producer and a consumer (or consumer group) |
| Scalability | High, rule-based routing at scale; near-limitless targets per rule | Virtually unlimited throughput for Standard queues |
| Availability | Multi-AZ | Multi-AZ |
| Latency | Near real-time; rule evaluation adds slight overhead | Very low latency with long polling; consumer must poll (introduces polling latency if misconfigured) |
| Operational overhead | Higher — need to design event patterns, buses, targets, DLQ for targets | Lower — one queue, one/many consumers pull |
| Pricing | Per event ingested (custom bus); free for many AWS-service-native events | Per API request |
| Consistency/ordering | No ordering; at-least-once | Standard = no ordering; FIFO = strict ordering |
| Limitations | Max event size 256KB; 5 targets per rule (soft, raisable); not ideal for pure task-queue workloads | No native content-based routing; single logical consumer pattern per queue |
| Exam trigger words | "route based on event type/source," "central event bus," "multiple AWS services need to react differently" | "decouple," "buffering," "retry with backoff," "asynchronous processing of a single workload" |
| Common traps | Using EventBridge purely as a task queue (no need — adds unnecessary complexity/cost vs SQS) | Using SQS when the real requirement is intelligent routing to *different* targets based on event type — you'd need custom Lambda logic to replicate what EventBridge rules do natively |

**Important complementary pattern (heavily tested):** EventBridge often triggers/targets an **SQS queue** as one of its targets — this combines content-based routing (EventBridge) with durable buffering (SQS). Exam scenario: "route order-created events to a queue for the fulfillment team, but only when order value > $1000" → EventBridge rule (content filter) → SQS target.

---

### 5. Kinesis (Data Streams / Data Firehose) vs SQS

| Dimension | Kinesis Data Streams | Kinesis Data Firehose | SQS |
|---|---|---|---|
| Primary use case | Real-time streaming analytics, multiple concurrent consumers replaying the same stream (e.g., clickstream, IoT telemetry, log aggregation with multiple readers) | Near-real-time delivery/ETL of streaming data **into** S3, Redshift, OpenSearch, Splunk (fully managed, no consumer app needed) | Decouple discrete work items between producer and single logical consumer group |
| Scalability | Scales via shards (manual or on-demand mode); each shard = 1MB/s in, 2MB/s out | Fully auto-scaled, no shard management | Virtually unlimited (Standard) |
| Availability | Multi-AZ | Multi-AZ | Multi-AZ |
| Latency | ~200ms (real-time) | Near real-time — buffers (60s+ or size-based) before delivery, so **not** sub-second | Low latency with long polling |
| Operational overhead | Higher — must manage shard count (unless on-demand mode), consumer checkpointing (KCL), scaling | Lowest — fully managed, no consumer code needed for delivery use case | Low — no shard/partition management |
| Pricing | Per shard-hour + PUT payload units (provisioned) or per-stream on-demand pricing | Per GB ingested/processed | Per API request |
| Consistency/ordering | Ordering guaranteed **per shard/partition key**; data retained 24h (default) to 365 days — supports **replay** | No replay — it's a delivery pipe, not persistent storage | Standard: no ordering; FIFO: ordering per message group |
| Limitations | 24hr default retention (extendable); consumers must manage checkpoints (or use Enhanced Fan-Out for dedicated 2MB/s/consumer throughput); resharding is operationally nontrivial | No consumer flexibility — destination-bound; can't replay/re-read; transform via Lambda adds latency | 14-day max retention; no replay after deletion; no multi-consumer replay (each message consumed once) |
| Exam trigger words | "multiple consumers need to process the same stream independently," "real-time analytics," "replay data," "ordered by partition key," "millions of records/sec," "clickstream/IoT" | "load streaming data into S3/Redshift/OpenSearch," "near real-time ETL," "no code to manage delivery" | "decouple," "buffer discrete jobs," "single consumer group processes each message" |
| Common traps | Choosing SQS when the requirement is "**multiple independent applications must consume and replay the same data**" — SQS deletes messages after consumption (no replay), Kinesis retains and allows multiple consumer apps to read independently via KCL/Enhanced Fan-Out. Also confusing Kinesis ordering — it's per-partition-key, NOT globally ordered across shards. | Assuming Firehose is real-time — it buffers (default 60s or 1-5MB) before flushing, so it's **near-real-time**, not true real-time like Data Streams. | Using SQS for streaming analytics use case — wrong tool; SQS is a queue, not a stream, no replay, no fan-out consumption. |

**Core exam discriminator:** If question emphasizes **"replay"**, **"multiple consumer applications reading the same data independently"**, or **"ordered processing per key at massive scale"** → Kinesis Data Streams. If it says **"just deliver streaming data to a data lake/warehouse with transformation, no infra to manage"** → Firehose. If it's **"discrete units of work, one-time processing"** → SQS.

---

### 6. Step Functions vs EventBridge

| Dimension | Step Functions | EventBridge |
|---|---|---|
| Primary use case | **Orchestration** of a multi-step workflow with defined state transitions, branching, retries, and error handling (e.g., order fulfillment saga, ML pipeline) | **Choreography** — reactive routing of independent events to decoupled targets; no central workflow state |
| Scalability | Standard Workflows: near-unlimited duration (up to 1 year), exactly-once execution; Express Workflows: high-volume, short-duration (<5 min), at-least-once | High throughput event routing; scales independently per rule |
| Availability | Multi-AZ | Multi-AZ |
| Latency | Standard: higher per-transition overhead (~tens of ms to seconds); Express: optimized for high-volume, low-latency (sub-second) event processing | Near real-time event delivery to targets |
| Operational overhead | Higher initial design (state machine ASL definition) but simplifies complex orchestration logic that would otherwise require custom code | Lower per-event overhead but doesn't manage workflow *state* — you'd need to build your own state tracking if simulating a workflow |
| Pricing | Standard: per state transition; Express: per execution + duration/memory (like Lambda) | Per event published |
| Consistency/ordering | Explicit state machine ensures deterministic step order, built-in retry/catch/error handling per step | No ordering/state — each event handled independently; no visibility into "workflow progress" |
| Limitations | Standard Workflow max execution history/size limits; Express has at-least-once (possible duplicate execution) semantics — must be idempotent | No native retries/state per "workflow" — must chain multiple event-consumer functions manually to approximate orchestration, quickly becomes unmanageable for complex flows |
| Exam trigger words | "orchestrate," "workflow with multiple steps," "saga pattern," "human approval step," "sequential steps with error handling/retry logic," "visual workflow" | "loosely coupled event routing," "reactive architecture," "each service reacts independently," "no central coordinator" |
| Common traps | Using EventBridge to try to build/represent a multi-step ordered workflow with dependencies and rollback — technically possible via chained rules but an anti-pattern; exam wants Step Functions here. | Using Step Functions for a scenario that's actually simple decoupled fan-out with no dependency between steps — unnecessary complexity/cost when EventBridge (or SNS) fits better. |

**Complementary pattern (also tested):** EventBridge can **trigger** a Step Functions state machine as a target (event-driven kickoff of an orchestrated workflow), and Step Functions can **emit events to EventBridge** on completion/failure for downstream reactive consumers — the two are often combined, not purely either/or.

---

### Quick Decision Matrix (memorize for exam speed)

| Signal in the question | Reach for |
|---|---|
| "Decouple producer/consumer," simple buffering | SQS Standard |
| "Exactly-once, strict order" | SQS FIFO |
| "Broadcast to many subscribers" | SNS |
| "Content-based routing / SaaS integration / event bus" | EventBridge |
| "Replay / multiple independent consumers of same data / real-time analytics" | Kinesis Data Streams |
| "Managed delivery into S3/Redshift/OpenSearch, near-real-time ETL" | Kinesis Data Firehose |
| "Multi-step orchestrated workflow with retries/branching" | Step Functions |
| "React independently to an event, no central coordination" | EventBridge (or SNS if simple) |

---

### Traps AWS Loves to Combine (multi-service scenario questions)

1. **SNS fan-out + SQS durability**: "Multiple teams must independently process the same event, and none should lose messages if their service is temporarily down" → SNS → multiple SQS queues (not SNS → Lambda directly, which can drop messages on failure without a DLQ).
2. **EventBridge filtering + SQS buffering**: content-based routing feeding a durable queue.
3. **Kinesis Data Streams + Firehose together**: Streams for real-time processing (Lambda/KCL consumers) *and* Firehose consuming the same stream (as a "consumer") to also archive to S3 — tests whether you know Firehose can be a Kinesis Data Streams consumer, not just a standalone service.
4. **Step Functions + EventBridge Scheduler for time-based orchestration triggers.** Note EventBridge Scheduler is a separate, higher-scale scheduling capability (supporting very large numbers of schedules, flexible time windows, per-schedule timezone handling) that was added *alongside* EventBridge's existing cron/rate-expression scheduled rules — it did not replace or deprecate them, and exam scenarios may reference either.
5. **SQS visibility timeout misconfiguration**: classic trap where visibility timeout < Lambda function timeout causes duplicate processing — tests operational nuance, not just conceptual knowledge.
6. **Dead-letter queue redrive**: DLQs (redrive policies) exist for both SQS and SNS. SNS subscription-level DLQs can be attached to any subscription protocol (including SQS), but they matter most for protocols like HTTP/S, Lambda, and mobile push that don't have their own built-in durable buffer — an SQS subscriber already persists messages on its own, so the DLQ is less critical (but still configurable) there.

## Migration

*AWS SAA-C03: Migration & Transfer Services — Comparison Guide*

---

### 1. AWS DataSync vs. Storage Gateway (File / Volume / Tape Gateway)

#### DataSync — Primary Use Case
**Online, automated, one-time OR recurring bulk data transfer** between on-premises storage (NFS, SMB, HDFS) and AWS (S3, EFS, FSx for Windows/ONTAP/OpenZFS/Lustre), or between AWS services/regions. It's a **transfer engine**, not a storage endpoint — data lands natively in AWS storage, not behind a gateway.

#### Storage Gateway — Primary Use Case
**Hybrid, ongoing storage extension** — on-prem apps keep reading/writing to a *local* gateway appliance that transparently backs onto AWS storage. Three modes, each answering a different exam scenario:
- **File Gateway** — NFS/SMB mount point backed by S3 objects (with local cache). Trigger: "on-prem app needs a file share that also lands in S3."
- **Volume Gateway** — iSCSI block volumes, two sub-modes:
  - *Cached volumes* — primary data in S3, hot data cached locally (large capacity, e.g. up to 32 TB per volume).
  - *Stored volumes* — primary data on-prem, async point-in-time EBS snapshot backups to S3 (disaster recovery pattern).
- **Tape Gateway** — Virtual Tape Library (VTL) replacing physical tape backup infrastructure; integrates with existing backup software (NetBackup, Veeam, etc.), archives to S3/Glacier/Deep Archive.

#### Scalability
- **DataSync**: Per-agent throughput depends heavily on network conditions, file size/count, and the performance of source/destination storage — AWS materials sometimes cite figures in the range of several Gbps up to roughly 10 Gbps per agent under favorable conditions, but this is **not a fixed, guaranteed ceiling** and shouldn't be treated as a hard spec to memorize. Scales horizontally by deploying multiple agents. Designed for **petabyte-scale** one-shot or scheduled migrations. Preserves metadata (permissions, timestamps, ownership).
- **Storage Gateway**: Bounded by gateway VM sizing and cache disk allocation; designed for **continuous, moderate-throughput hybrid access**, not bulk one-time petabyte dumps. File Gateway cache and Volume Gateway cache sizing directly limits performance.

#### Network / Bandwidth Considerations
- **DataSync**: Built-in **bandwidth throttling**, automatic retry, in-flight encryption (TLS), and **checksums for data validation**. Can use Direct Connect or public internet; supports **incremental transfers** — on subsequent runs it compares file metadata (size/timestamps) and re-copies only files that are new or changed, avoiding a full re-scan/re-copy of unchanged data (a clear win vs. plain `cp`). Note: unlike `rsync`'s block-level delta algorithm, DataSync re-copies a **changed file in its entirety** rather than just the changed byte ranges within it — so don't overstate this as strictly more efficient than `rsync` for large files with small in-place edits; the real differentiator vs. `rsync` is that DataSync is a managed, schedulable, monitored AWS-native service with built-in checksumming, not that it transfers less data per changed file.
- **Storage Gateway**: Bandwidth throttling schedules exist too, but the traffic pattern is **continuous** (ongoing reads/writes/uploads), not a bulk push — so it's evaluated more on latency-sensitivity of the local cache hit ratio.

#### Operational Overhead
- **DataSync**: Deploy an agent (VM/EC2/Outposts), point source→destination, schedule task, done. **Low ongoing overhead** — it's a migration utility, not infrastructure you run apps against.
- **Storage Gateway**: You are running **persistent hybrid infrastructure** — a virtual appliance sized for cache, monitored, patched. Higher ongoing operational footprint because applications depend on it continuously.

#### Pricing
- **DataSync**: Pay **per GB transferred** (no separate license charge for the agent software itself, though if you run the agent on your own EC2 instance you pay standard EC2 costs for that VM). This is **usage-based, not literally "pay once"** — a one-time bulk migration incurs a single transfer charge, but a recurring/scheduled task (as DataSync also supports) bills per GB **every time it runs**, even though incremental runs typically move much less data.
- **Storage Gateway**: Pay for **underlying storage consumed** (S3/EBS snapshots) + **data transfer out** + no charge for the gateway software itself, but there's an ongoing storage cost since it's a permanent hybrid architecture.

#### Limitations
- **DataSync** does not provide a live mount point for on-prem apps — it copies data, it doesn't front it. Not a substitute for ongoing hybrid file access.
- **Storage Gateway** File/Volume modes have **cache-miss latency** exposure — if working set exceeds local cache, performance degrades to S3/round-trip latency. Tape Gateway has **no physical tape hardware** — purely virtual, so it doesn't solve "get rid of tape drives" if compliance requires literal tape.

#### Exam Trigger Words
- "**Migrate petabytes of on-prem NFS data to S3 with minimal effort**," "**one-time bulk migration**," "**preserve file metadata during migration**," "**incremental/delta sync**," "**migrate and validate data integrity**" → **DataSync**.
- "**On-premises application needs low-latency access to files that also need to live in the cloud**," "**replace physical tape backup infrastructure**," "**hybrid cloud storage / cached volumes**," "**iSCSI**," "**continuous/ongoing hybrid access**" → **Storage Gateway**.

#### Common Traps
- Assuming DataSync is for *ongoing hybrid access* — it isn't; it's task-based/batch (even if scheduled repeatedly, it's not a live mount).
- Assuming Storage Gateway is the answer for large one-time migrations — it's the wrong tool if there's no ongoing on-prem access requirement (over-provisioning hybrid infra for a one-shot job).
- Confusing "Cached" vs "Stored" Volume Gateway direction of primary data (Cached = primary in AWS; Stored = primary on-prem, async backup to AWS) — SAA-C03 loves flipping this.
- Forgetting Tape Gateway integrates with **existing backup software** — it's not a standalone backup product, so if the question implies "no existing backup software," Tape Gateway is a trap answer.
- DataSync **can** be used gateway-to-gateway or S3-to-S3/EFS-to-FSx (AWS-to-AWS), not just on-prem-to-cloud — questions test this cross-region/cross-service use.

---

### 2. Snow Family (Snowcone / Snowball Edge / Snowmobile) vs. DataSync

#### Snow Family — Primary Use Case
**Offline, physical data transport** for environments where network transfer is impractical due to **bandwidth constraints, cost, or lack of connectivity** (remote/edge sites, disconnected environments, or truly massive datasets where physics beats network throughput).
- **Snowcone** — smallest (8TB HDD / 14TB SSD), ruggedized, can run **edge compute** (EC2 instances, Greengrass), usable in tiny/rugged/disconnected field environments; can ship back OR transfer over network via DataSync agent onboard.
- **Snowball Edge** (Storage Optimized ~80TB usable, Compute Optimized with GPU option) — mid-scale, on-device compute/ML/edge processing + storage migration, cluster multiple devices for local high-availability compute at the edge.
- **Snowmobile** — **exabyte-scale** migration via a shipping container on a truck; a single Snowmobile has a stated capacity of **up to 100PB**, and exabyte-scale migrations are achieved by using multiple Snowmobiles in parallel. Used only for the most extreme migrations.

#### DataSync (as the counterpoint) — Primary Use Case
**Online network-based transfer** — appropriate when there IS sufficient network bandwidth/connectivity to move the data in an acceptable timeframe.

#### Scalability
- **Snow Family** scales by **shipping more devices** (parallel jobs) rather than network throughput — this is the key exam differentiator: scalability is bound by **logistics**, not bandwidth.
- **DataSync** scales with network bandwidth and number of agents; scalability is bound by **available bandwidth × time**.

#### Network / Bandwidth Considerations — THE Core Decision Point
This is the classic SAA-C03 decision tree:
- **Calculate**: `data size / available bandwidth = transfer time`. AWS's public rule of thumb: if a network transfer would take **more than about 1 week** (some guidance uses different thresholds, but "would take too long over the network" is the qualitative test), physical (Snow) is preferred.
- **No connectivity / restricted networks** (ships, oil rigs, military, disaster response, remote field sites) → Snow Family is **the only option** regardless of data size, because there is no meaningful network path at all — this is a bigger trigger than raw data volume.
- **Sufficient bandwidth exists** (even if it takes some days) and connectivity is reliable → DataSync is operationally simpler and avoids device logistics/shipping risk.

#### Operational Overhead
- **Snow Family**: Physical logistics — ordering, on-site connection, data copy job, **physical shipping back to AWS**, chain-of-custody/security concerns, potential for shipping delays/damage. Snowcone/Snowball Edge also require local power, network cabling, and physical security at the site.
- **DataSync**: Purely software — deploy agent, configure task, done. No physical handling risk.

#### Pricing
- **Snow Family**: Job fee per device + daily usage fee (per day held beyond free period) + shipping. Flat/predictable cost regardless of data volume within device capacity — cost-effective specifically because it **avoids data transfer/network egress costs** and time.
- **DataSync**: Per-GB transferred pricing + your own network/Direct Connect costs (which can be substantial for huge datasets over long timeframes) + potential egress if pulling FROM AWS.

#### Limitations
- Snow devices have **fixed capacity ceilings** (Snowcone 8/14TB, Snowball Edge ~80TB usable) — for anything beyond that, you need **multiple devices** or escalate to Snowmobile.
- Snowmobile is only economical/available for **truly massive (multi-PB to EB)** migrations — using it for anything smaller is a trap; AWS guidance generally points toward using **multiple Snowball Edge devices in parallel** instead of Snowmobile for data volumes under roughly 10PB, reserving a Snowmobile (capacity up to ~100PB each) for the largest data-center-scale moves.
- Snow Family transfer is inherently **not real-time** — there's a data-cutover/consistency gap between when you seal the device and when data lands in AWS (must plan for delta sync afterward, often via DataSync, for a final incremental catch-up).
- Edge compute use cases (Snowcone/Snowball Edge running Lambda/EC2/Greengrass at disconnected sites) is a distinct exam angle from "migration" — don't conflate "migrate data" scenario with "run compute at a disconnected edge site" scenario, though the same device answers both.

#### Exam Trigger Words
- "**No network connectivity / limited bandwidth site**," "**petabytes/exabytes with a hard deadline**," "**satellite office with slow WAN link**," "**data center decommission, physically move data**," "**disconnected/remote/tactical edge location**," "**ship a device**," "**cannot use the internet for security reasons**" → **Snow Family**.
- "**Ongoing/incremental transfer**," "**sufficient bandwidth available**," "**automate recurring sync**," "**preserve metadata**," "**network-based migration**" → **DataSync**.
- "**Exabytes**" or "**entire data center, tens of petabytes**" → **Snowmobile** specifically (not Snowball Edge).
- "**Rugged, small form factor, edge location with local compute (ML inference, IoT)**" → **Snowcone**.

#### Common Traps
- Choosing Snowmobile for "just" a few hundred TB — should be Snowball Edge (cheaper, multiple devices, avoids single point of physical failure that Snowmobile represents).
- Forgetting that **after a Snow device transfer**, you typically still need a **DataSync incremental sync** to catch changes made on-prem after the device was sealed and shipped — combined workflow questions test this.
- Assuming bandwidth is always the deciding factor — sometimes the trigger is pure **lack of connectivity**, not slowness, which still forces Snow Family even for modest data sizes.
- Confusing Snowcone's dual nature — it can be **shipped back** OR **used with DataSync client to send data over network** directly from the device; it's not purely offline-only like Snowball/Snowmobile.
- Thinking Storage Gateway and Snow Family solve the same problem — they don't; Snow is for the *initial bulk data move*, Storage Gateway is for *ongoing hybrid access* after migration.

---

### 3. AWS DMS (Database Migration Service) vs. DataSync

#### DMS — Primary Use Case
**Database-aware migration and replication** — moves data at the **schema/table/row level** between database engines (homogeneous: Oracle→Oracle; or heterogeneous: Oracle→Aurora PostgreSQL using the **Schema Conversion Tool (SCT)**), with support for **Full Load + CDC (Change Data Capture)** for near-zero-downtime cutovers. Also handles source→target combos where target isn't even a "traditional" DB (e.g., replicate to S3, Kinesis, Redshift, OpenSearch, Kafka for analytics pipelines).

> Note: **Babelfish for Aurora PostgreSQL** is a related but distinct compatibility feature — it lets Aurora PostgreSQL understand T-SQL and SQL Server's wire protocol, specifically to ease migrations **from SQL Server**. It's not a general-purpose heterogeneous conversion tool applicable to arbitrary source engines like Oracle, so don't pair it with an Oracle→Aurora PostgreSQL example.

#### DataSync — Primary Use Case
**File-system/object-level data transfer** — has **no awareness of database internals**, transactions, schemas, or referential integrity. It moves files/objects, not rows.

#### Scalability
- **DMS**: Scales via **replication instance sizing** (compute/memory for the migration task) and can run multiple **replication tasks** in parallel across table subsets for large schemas. CDC throughput is bound by source DB's transaction log read capacity and target write capacity.
- **DataSync**: Scales via network bandwidth/agents as described earlier — irrelevant for structured DB migration because it can't interpret DB engine formats correctly for a live cutover.

#### Network / Bandwidth Considerations
- **DMS**: Typically used **online, continuously**, often over Direct Connect/VPN/PrivateLink for security; CDC keeps source and target in sync in **near real-time**, minimizing cutover downtime to seconds/minutes.
- **DataSync**: Bulk transfer pattern; not designed for **continuous low-latency replication** of a live transactional system's data files (and copying raw DB files while the DB is running risks corruption — DataSync has no transactional consistency guarantees).

#### Operational Overhead
- **DMS**: Requires **provisioning a replication instance**, defining source/target endpoints, table mappings, and (for heterogeneous migrations) running **SCT** first to convert schema/stored procedures/functions — non-trivial for complex schemas with proprietary SQL dialects (PL/SQL, T-SQL). Higher operational/skills overhead than DataSync.
- **DataSync**: Simple agent + task model, but simply **not applicable** to live database migration use cases.

#### Pricing
- **DMS**: Pay for the **replication instance** (EC2-like hourly billing) for the duration of migration/replication, plus storage for logs; **DMS Serverless** is also available (billed per DMS Capacity Unit), removing the need to size a replication instance up front — a real, relatively recent (2023) feature worth knowing, though don't assume any particular exam version tests it explicitly.
- **DataSync**: Pay per GB transferred, no compute instance to size/manage.

#### Limitations
- **DMS**: Homogeneous migrations are straightforward; **heterogeneous migrations require SCT** and can leave a percentage of objects (complex stored procedures, triggers) requiring **manual conversion** — DMS doesn't magically convert business logic. Large Objects (LOBs) can slow full-load performance if not tuned. Not meant for one-off flat-file transfer.
- **DataSync**: Cannot understand DB storage formats, transactions, or provide CDC — attempting to use it for "migrate my running production database with minimal downtime" is architecturally wrong.

#### Pricing/Overhead Trade-off Framing (exam angle)
DMS is the **only correct choice** whenever the source is a **live, running database** requiring **minimal downtime** and/or an **engine change** — no file-copy tool can substitute.

#### Exam Trigger Words
- "**Migrate a database with minimal/near-zero downtime**," "**ongoing replication between source and target databases**," "**heterogeneous database migration (e.g., Oracle to Aurora)**," "**Change Data Capture / CDC**," "**consolidate multiple databases**," "**replicate database changes to a data lake/analytics target**" → **DMS** (+ SCT if engines differ).
- "**Migrate files/objects**," "**home directories, NFS shares, media files**" → **DataSync**, never DMS.

#### Common Traps
- Using DMS for **non-database** file migration — wrong tool entirely.
- Forgetting **SCT is a separate/complementary tool**, not part of DMS itself — needed specifically for heterogeneous schema/code conversion before DMS handles the data movement.
- Assuming DMS requires downtime — the whole point of **Full Load + CDC** is to avoid it; picking an answer that says "take the DB offline to migrate" when DMS CDC is available is the trap.
- Not recognizing **DMS as a valid ongoing replication tool** for feeding analytics targets (S3/Redshift/Kinesis), not just "migration" in the literal one-time sense — SAA-C03 questions sometimes frame this as a data pipeline problem, not a "migration" problem, and testers still expect DMS.

---

### 4. AWS Application Migration Service (MGN) vs. DMS

#### MGN — Primary Use Case
**Lift-and-shift (rehost) of entire servers** — physical servers, VMs (VMware, Hyper-V), or other-cloud instances — into AWS as EC2 instances, using **continuous block-level replication** via a lightweight agent installed on the source server. This is AWS's **recommended/default migration service**, having superseded CloudEndure Migration and the older Server Migration Service (SMS, which is deprecated/retired).

#### DMS — Primary Use Case
(As above) **database-only** migration — not whole servers, just the DB engine/data.

#### Scalability
- **MGN**: Scales to **thousands of servers** for large-scale data center migrations; replication runs continuously per-server via lightweight agents, with a **staging area** (low-cost EC2/EBS in a staging subnet) that holds continuously-replicated data before cutover.
- **DMS**: Scales per-database/per-replication-task, not per-server — fundamentally different unit of migration.

#### Network / Bandwidth Considerations
- **MGN**: Continuous, **block-level, near-real-time replication** (agent captures disk writes) over the network to the AWS staging area; bandwidth throttling configurable. Replication is continuous until you **launch a test/cutover instance**, allowing **non-disruptive testing** of the migrated server before final cutover with **minimal downtime** (typically just the final cutover window).
- **DMS**: Uses transaction log-based CDC at the database layer, not block-level disk replication — different mechanism.

#### Operational Overhead
- **MGN**: Install replication agent on each source server → data continuously replicates to staging → launch test instances to validate → perform cutover (final sync + instance launch) → decommission source. Overhead is per-server agent management, but **the actual migration logic (OS/driver conversion) is automated** by MGN (it handles boot volume conversion, driver injection for AWS hypervisor compatibility).
- **DMS**: Overhead centers on **replication instance + schema conversion (SCT)**, an entirely different skill set (DBA-oriented vs. sysadmin-oriented for MGN).

#### Pricing
- **MGN**: MGN itself is **free to use for the first 90 days per source server** from when replication starts — during that window you only pay for the underlying staging area resources (small EC2 instances + low-cost EBS + data transfer). **After 90 days per server, a low hourly MGN service fee applies** in addition to the staging resource costs, until cutover. Once cutover happens, standard EC2 pricing applies to the migrated instances. The "free for an initial period" model is the exam-relevant fact — don't overstate it as free indefinitely regardless of how long replication runs.
- **DMS**: Pay for replication instance compute the entire time it runs — no free replication tier.

#### Limitations
- **MGN**: Only migrates at the **server/OS/disk level** — it is agnostic to what's running on the server, meaning it **cannot perform database engine conversion** (heterogeneous). If a server runs Oracle and you want to end up on Aurora, MGN will just give you Oracle-on-EC2 (a rehost), NOT a re-platform — you'd need DMS (+SCT) for the DB engine change specifically.
- **DMS**: Cannot migrate an entire server/application stack — only the database component.

#### Exam Trigger Words
- "**Rehost / lift-and-shift entire servers/VMs to AWS with minimal changes**," "**large-scale data center migration/evacuation**," "**physical or virtual servers, minimal downtime cutover**," "**test migrated servers before cutover without affecting source**," "**replatform later after rehosting (MGN then modernize)**" → **MGN**.
- "**Change database engine**," "**consolidate/migrate only the database tier**," "**heterogeneous DB migration**" → **DMS**.
- Scenario combining both: "**Migrate an entire application stack including its Oracle database to AWS, and eventually convert the database to Aurora**" → **MGN for the app/OS servers + DMS/SCT for the database tier** — a very common "pick two/compound" SAA-C03 pattern.

#### Common Traps
- Confusing MGN with **SMS (Server Migration Service)** — SMS is **deprecated/retired**; any answer choice referencing SMS as current is a distractor to eliminate.
- Assuming MGN handles database re-platforming — it does not; it treats the DB as just another process on the disk being replicated as-is (same engine, same version, just relocated to EC2).
- Assuming MGN is either "free forever" or "expensive throughout" — the reality is a **90-day free window per server** (paying only for staging resources), after which a modest hourly MGN fee kicks in; both oversimplifications are traps.
- Overlooking that MGN supports **non-disruptive test launches** — a trap answer might claim you must "take source systems offline to validate the migration," when MGN explicitly allows testing the target without impacting the still-running source.
- Choosing DMS for a "migrate our whole fleet of on-prem VMs" scenario — DMS operates at the database layer only and cannot rehost an entire OS/server.

---

### Quick-Reference Decision Matrix

| Trigger Phrase | Correct Service |
|---|---|
| Petabytes over network, incremental/scheduled sync, metadata preservation | **DataSync** |
| Ongoing hybrid file/block access, on-prem app needs local performance | **Storage Gateway** (File/Volume) |
| Replace physical tape backup, VTL integration with existing backup software | **Tape Gateway** |
| No/limited network connectivity, remote/disconnected site | **Snow Family** |
| Exabyte-scale, entire data center | **Snowmobile** |
| Edge compute + storage at rugged/small site | **Snowcone** / **Snowball Edge** |
| Live database, minimal downtime, CDC, engine change | **DMS (+SCT for heterogeneous)** |
| Feed data lake/analytics target continuously from a DB | **DMS** |
| Rehost entire servers/VMs, minimal downtime, non-disruptive testing | **MGN** |
| Server migration + DB engine conversion (compound scenario) | **MGN (servers) + DMS/SCT (database)** |
