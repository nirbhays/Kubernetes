# High Availability & Disaster Recovery Mastery (AWS SAA-C03)

## Availability Zones & Failure Domains

An AZ is the atomic failure domain for compute/storage — physically isolated (separate power, cooling, network), but connected to other AZs in the same Region via redundant, high-throughput, low-latency private fiber links. AWS does not publish a specific committed millisecond figure for inter-AZ latency, but it is consistently described as single-digit-millisecond round trip — low enough that synchronous replication (e.g., RDS Multi-AZ, EBS io2 Block Express in some configs) is practical, but not zero, which is why cross-AZ chattiness still shows up as a cost/performance consideration. The exam's core resiliency pattern is: **never have a single point of failure inside a single AZ**. Any architecture with one EC2 instance, one NAT Gateway, one RDS instance (non-Multi-AZ), or one subnet pinned to one AZ is a trigger for "this design has a flaw — fix it" questions.

Key inference cues:
- "The application must survive the loss of a data center" → AZ failure, needs Multi-AZ, not necessarily multi-Region.
- "The application must survive the loss of an entire AWS Region" → multi-Region design required.
- Don't over-engineer: if the scenario only demands AZ resilience, multi-Region answers are usually the *higher-cost distractor* the exam wants you to reject (extra cross-Region replication, latency, and operational overhead aren't justified when the stated failure scope is a single AZ).

## Regional vs. Global Services — Know This Cold

This distinction is tested constantly, often indirectly (e.g., "which of these does NOT need to be replicated per-Region").

**Global services** (single control plane, no Region selection): IAM, Route 53, CloudFront, WAF (for CloudFront), AWS Organizations, S3 (bucket namespace is global, but data/storage is regional), Global Accelerator (anycast IPs are global, but backend resources are regional).

**Regional services** (deployed per-Region, fail independently): EC2, RDS, Lambda, VPC, ELB, EBS, most everything else. S3 *buckets* live in a Region even though the naming is global — a common trap: "does S3 need Multi-AZ configuration?" No — S3 Standard (and Standard-IA) redundantly stores objects across a minimum of three AZs within a Region automatically. (S3 One Zone-IA is the deliberate exception — single-AZ by design, cheaper, and not resilient to AZ loss — a frequent distractor when the scenario needs AZ resilience.) The exam distractor is offering "deploy S3 in multiple AZs" as an answer — it's meaningless for the Standard classes, S3 is already regionally resilient by default; what you configure is Cross-Region Replication (CRR) for regional failure, not AZ failure.

IAM being global means you don't re-create users/roles per Region — a scenario testing multi-Region DR should never include "replicate IAM users to DR Region" as a correct answer; that's a distractor testing whether you know IAM is already everywhere.

## Multi-AZ Architecture Patterns

- **Compute**: ASG spanning ≥2 AZs behind an ELB. Exam wants you to explicitly spread subnets across AZs in the ASG's VPC config — a common wrong-answer trap is an ASG that only references a single AZ/subnet.
- **RDS Multi-AZ (instance)**: synchronous replication to a single standby in a second AZ, automatic failover (DNS CNAME flip, typically 60–120s per AWS's published guidance), standby is **not readable** (that's what Read Replicas are for — different feature, different purpose: RDS Multi-AZ = HA/DR, Read Replicas = scaling/read offload, and they can be combined). Exam trigger: "minimize downtime during AZ failure" or "automatic failover without app changes" → Multi-AZ. "Reduce read load on primary" → Read Replica (which can itself be Multi-AZ for its own resiliency, or cross-Region for DR reads).
- **RDS Multi-AZ DB cluster** (a separate, newer deployment option — don't conflate it with the classic Multi-AZ instance deployment above): one writer plus **two readable standby instances** spread across three AZs, using a quorum-based semi-synchronous replication protocol. Because the standbys are readable, you can offload read traffic to them (via the reader endpoint) without needing a separate Read Replica, and failover is typically faster (well under a minute) than the classic single-standby Multi-AZ deployment. Trigger words: "readable standby instances," "faster failover than Multi-AZ instance deployment," "reduce read load using the standby itself rather than a Read Replica."
- **Aurora**: stores 6 copies of data across 3 AZs automatically (2 per AZ), and is designed to handle the loss of an entire AZ (2 copies) without impacting write availability, and the loss of an AZ plus one additional copy without impacting read availability — all without manual intervention. Failover is typically faster (well under 30s) than standard RDS Multi-AZ (instance) — if the scenario emphasizes "fastest failover" or "storage-level self-healing replication" with a relational engine, that's Aurora, not vanilla Multi-AZ RDS.
- **EFS/S3**: regionally resilient across AZs by default (for S3 Standard/Standard-IA and EFS Standard) — no "Multi-AZ" toggle needed, unlike EBS (which is AZ-scoped and requires snapshots or replication to move across AZs).
- **NAT Gateway**: AZ-scoped resource. HA pattern = one NAT Gateway per AZ, each private subnet routes to the NAT Gateway in its own AZ. A single shared NAT Gateway across all AZs is a classic single-point-of-failure exam trap (also creates cross-AZ data transfer cost — relevant to cost-optimization domain too).

## Multi-Region Architecture

Triggers: "global user base with low latency everywhere," "must survive Regional outage," "data residency across geographies," "active-active worldwide."

Building blocks:
- **Route 53** for traffic steering across Regions (latency-based, geolocation, geoproximity routing policies).
- **DynamoDB Global Tables** for multi-region active-active NoSQL with conflict resolution (last-writer-wins) — the go-to answer whenever the scenario says "multi-region writes" + "DynamoDB" + "minimal operational overhead."
- **Aurora Global Database** for relational multi-region with fast cross-region replication (typically sub-second lag) and fast promotion of a secondary Region (typically under a minute) — this is the answer whenever you see "relational database," "multi-region DR," "RPO in seconds," "RTO in under a minute." Distinguish from a single Aurora cluster's cross-AZ replicas, which don't span Regions. Note secondary Regions are read-only until promoted — this is not a multi-region *write* active-active solution.
- **S3 Cross-Region Replication (CRR)** for object durability/DR across Regions; combine with **S3 Multi-Region Access Points** when the exam wants "single endpoint, active-active access across Regions with automatic routing to lowest latency/failover."
- **Global Accelerator** vs **CloudFront**: Global Accelerator improves TCP/UDP performance for non-HTTP or mixed protocols and gives static anycast IPs with fast failover at the network layer; CloudFront is for HTTP(S)-cacheable content at the edge. If the question says "static IP addresses for whitelisting" + "multi-region failover for non-web TCP/UDP application," that's Global Accelerator, not CloudFront/Route 53 alone. If it says "cache content close to users" + "HTTP/S," that's CloudFront.
- IAM, Route 53 config, CloudFormation templates/StackSets are how you keep the DR Region "ready" — since IAM/Route 53 are already global, you don't replicate them, you just reference them.

## Auto Scaling — Exam Decision Points

- **Target Tracking** is the default recommended policy (e.g., keep average CPU at 50%) — exam prefers this over Step Scaling unless the scenario needs different scaling magnitudes at different thresholds (Step Scaling) or truly custom scheduling (Scheduled Scaling — trigger words: "predictable traffic spike at a known time," e.g., "every day at 9am").
- **Predictive Scaling** — trigger words: "recurring, predictable daily/weekly traffic pattern," "scale ahead of forecasted demand using ML," "reduce under-provisioning during traffic ramp-up." Combine with dynamic scaling for unexpected variance.
- Multi-AZ ASGs automatically attempt to rebalance instances across AZs; enabling **Capacity Rebalancing** proactively replaces Spot instances that received a rebalance recommendation before interruption — relevant when Spot + resilience both appear in the same scenario.
- ASG + ELB health checks: ASG's default EC2 status check is not enough to detect an app-level failure — must enable **ELB health checks** on the ASG so unhealthy-but-running instances get replaced. This is a subtle but frequently tested config detail.
- Warm pools reduce scale-out latency for slow-booting instances — trigger: "reduce time to scale out," "expensive bootstrapping/initialization process."

## Elastic Load Balancing — ALB vs NLB vs GWLB

| | ALB | NLB | GWLB |
|---|---|---|---|
| OSI Layer | Layer 7 (HTTP/HTTPS/gRPC) | Layer 4 (TCP/UDP/TLS passthrough) | Layer 3 (GENEVE, transparent) |
| Routing | Path-based, host-based, header/query-string/method-based | Connection/flow-based, no content inspection | Transparent bump-in-the-wire |
| Static IP | No (use an NLB in front, or Global Accelerator) | Yes — one static/Elastic IP per AZ | N/A (paired with GWLB endpoints) |
| TLS | Termination (offload) supported, SNI-based multi-cert | Passthrough or termination (TLS listener) | Passthrough only |
| WebSockets | Native support | Native (it's just TCP) | N/A |
| Target types | Instance, IP, Lambda | Instance, IP, ALB (chaining) | Instance, IP (appliance instances) |
| Preserve source IP | Via X-Forwarded-For header | Natively preserves client IP (no header needed) | Preserves the entire original packet (including source IP) inside the GENEVE encapsulation delivered to the appliance |
| Use case | Microservices/containers needing content routing, Lambda-backed APIs | Extreme performance/low-latency, static IP requirement, non-HTTP TCP/UDP | Deploying/scaling 3rd-party virtual appliances (firewalls, IDS/IPS) transparently |

Exam trigger words → answer:
- "static IP address" / "IP allowlisting by a partner" / "millions of requests per second, ultra-low latency" → **NLB**.
- "route based on URL path" / "/api vs /images" / "host-based routing across microservices" → **ALB**.
- "Lambda function as a target" / "serverless backend for HTTP API" → **ALB** (NLB doesn't support Lambda targets).
- "preserve client source IP without extra config" → **NLB** (ALB requires reading X-Forwarded-For).
- "inspect/filter traffic transparently through third-party security appliances, scale them elastically" → **GWLB**.
- "WebSocket support" → both ALB and NLB support it; ALB is usual answer if also doing content routing, NLB if raw performance/static IP also required.
- **Target type "IP"** matters when targets are in a peered VPC, on-prem via Direct Connect/VPN, or when using containers with awsvpc networking (each task gets its own ENI/IP) — trigger: "register on-premises servers as targets" or "Fargate tasks as ALB targets" → IP target type, not Instance.
- Cross-zone load balancing: ALB has it enabled by default (free); NLB has it disabled by default (enabling it may incur cross-AZ data transfer charges) — a cost-optimization-domain nuance that occasionally intersects with resiliency questions about "even distribution across AZs."

## Route 53 for Failover & DNS-Based HA

- **Failover routing policy**: primary/secondary records with health checks — the direct, literal answer for "automatically fail over to a DR site if the primary becomes unhealthy." Requires a Route 53 health check on the primary endpoint (HTTP/HTTPS/TCP, or calculated/CloudWatch alarm-based health checks for private/complex resources).
- **Health checks** can monitor endpoints directly, or be **calculated health checks** (combine multiple child health checks with AND/OR/NOT), or based on a **CloudWatch alarm** — use the alarm-based type when checking something Route 53 can't reach directly (e.g., an internal resource, or a custom business metric).
- Other routing policies occasionally masquerade as "HA" answers but serve different purposes — don't confuse them:
  - **Weighted**: canary/blue-green traffic shifting, A/B testing — not failover per se, though shifting a record's weight to 0 can be used to fully cut traffic away from an unhealthy or deprecated target.
  - **Latency-based**: route to lowest-latency Region — used for multi-region *performance*, but combined with health checks it also provides regional failover.
  - **Geolocation/Geoproximity**: compliance/data-residency or shifting traffic bias geographically (Geoproximity + bias for load-shifting).
  - **Multi-value answer**: returns multiple healthy IPs, lightweight client-side load balancing — DNS-level alternative to a load balancer for simple use cases, still health-check aware but not a substitute for full failover orchestration.
- DNS TTL matters for RTO: lower TTLs reduce the failover time perceived by clients (at the cost of increased query volume/cost) — if the scenario complains about "clients still hitting the old Region for minutes after failover," the answer is lowering the TTL, not changing the routing policy.
- Route 53 Application Recovery Controller (Route 53 ARC) — for more rigorous, tested failover automation with readiness checks and routing controls; mention when the scenario demands "regularly tested, audited failover process," beyond a basic health-check failover record.

## Eliminating Single Points of Failure — AWS's Mental Model

The exam consistently expects the following default assumptions unless a requirement contradicts them:
1. Compute is stateless and horizontally scaled behind an ELB, spread across ≥2 AZs, managed by an ASG.
2. State lives in a managed, replicated data service (RDS Multi-AZ/Aurora, DynamoDB, S3, EFS) — never on local/instance-store disk that isn't backed up.
3. Anything provisioned "once" per Region (NAT Gateway, Bastion, single EC2 for a control-plane-ish role) is immediately suspect — the "fix the architecture" question type nearly always targets this.
4. Decoupling via SQS/SNS/EventBridge between tiers so failure/backpressure in one component doesn't cascade — tested under resiliency domain when a synchronous chain is described as fragile ("if service B is slow, service A times out and drops requests" → insert a queue).
5. Infrastructure as Code (CloudFormation/StackSets, or Terraform mentioned generically) to make environments — including DR Regions — reproducible; this is how "warm standby" or "pilot light" environments in a second Region are kept up to date without manual duplication.
6. Idempotent, retry-safe operations plus exponential backoff/circuit breaking for resilience against transient failures — SDK default retry behavior is assumed; the exam sometimes tests recognizing that a custom retry storm ("thundering herd") is the actual root cause of an outage, expecting jitter/backoff as the fix.

## DR Strategies — Backup & Restore, Pilot Light, Warm Standby, Multi-Site Active-Active

The four canonical AWS DR strategies sit on a single RTO/RPO/cost spectrum. The exam frequently does **not** name the strategy directly — it describes budget, RTO/RPO tolerance, or architecture details, and expects you to classify it.

### Backup and Restore
- **RTO**: hours (highest of the four).
- **RPO**: hours (depends on backup frequency — as low as your last snapshot/backup job).
- **Cost**: lowest — pay for backup storage (S3, EBS snapshots, RDS snapshots, AWS Backup) in the DR Region; no standing compute.
- **Architecture**: regular automated backups (AWS Backup, RDS automated snapshots + cross-Region copy, S3 CRR for objects, AMIs copied cross-Region) with infrastructure defined in CloudFormation/StackSets ready to launch on-demand in the DR Region during an actual disaster.
- **Exam trigger words**: "most cost-effective DR," "budget-constrained," "can tolerate several hours of downtime," "infrequent disaster events," "minimal ongoing spend." Inference trap: a question describing "nightly snapshots copied to another Region, no resources running there" without ever saying "Backup and Restore" — that phrase IS this strategy.

### Pilot Light
- **RTO**: tens of minutes to a few hours (faster than backup/restore because core data services are already running/replicating; slower than Warm Standby because the application/compute tier still needs to be provisioned from scratch).
- **RPO**: minutes (continuous or near-continuous data replication, e.g., RDS Read Replica or Aurora Global Database cross-Region, or DB replication already active).
- **Cost**: low-moderate — only the "core" (typically the database/data layer) runs continuously in DR Region at minimal size; application/compute tier is provisioned (from AMI/launch templates/CFN) only when disaster is declared.
- **Architecture**: think of a literal pilot light in a furnace — a small flame (replicated data tier) always on, ready to "ignite" the rest (scale up ASG, launch instances from pre-baked AMIs) when needed.
- **Exam trigger words**: "database replication already running in DR Region but application servers are not," "minimize cost while keeping data ready," "spin up compute only during a disaster." Inference trap: description of "only the data tier is live in the second Region; everything else is templated and launched on failover" — that's Pilot Light even if unnamed.
- Common confusion vs. Warm Standby: if it says application/web tier also runs at **reduced/minimal capacity** (not zero) in the DR Region, that's Warm Standby, not Pilot Light — the presence/absence of a scaled-down (but running) app tier is the discriminator.

### Warm Standby
- **RTO**: minutes.
- **RPO**: seconds to minutes (near-real-time replication).
- **Cost**: moderate-high — a scaled-down but fully functional full stack (all tiers, including compute/app layer) runs continuously in the DR Region; failover = scale up the ASG/capacity rather than provisioning from scratch.
- **Architecture**: full replica environment at low capacity (e.g., minimal instance count/size), Route 53 weighted or failover routing already configured, database continuously replicating (Aurora Global Database / DynamoDB Global Tables / cross-region read replica promoted on failover).
- **Exam trigger words**: "fully functional environment running at reduced capacity in a second Region," "scale up on failover," "faster recovery than pilot light but cheaper than full active-active." Inference trap: "a scaled-down copy of production is always running and just needs to be scaled up during failover" — Warm Standby, even if the word never appears.

### Multi-Site Active-Active
- **RTO**: near-zero / seconds (traffic is already being served from multiple Regions).
- **RPO**: near-zero (or effectively zero for eventually-consistent systems like DynamoDB Global Tables, though be aware of eventual consistency/conflict-resolution caveats — last-writer-wins can lose data in true simultaneous conflicting writes, which the exam sometimes flags as a trade-off, not a flaw to "fix").
- **Cost**: highest — full production-capacity stacks running in ≥2 Regions simultaneously, all serving live traffic.
- **Architecture**: Route 53 latency-based or geoproximity routing across Regions, DynamoDB Global Tables or Aurora Global Database (with the caveat that Aurora Global Database secondary Regions are typically read-only until promoted — true multi-region **write** active-active at the relational layer is a more advanced/limited capability, so if the scenario demands multi-region simultaneous writes for a relational workload, expect DynamoDB or a "promote secondary" pattern to be discussed, not casual claims of unrestricted multi-master SQL).
- **Exam trigger words**: "zero/near-zero RTO and RPO," "no acceptable downtime," "active traffic served from multiple Regions simultaneously," "cost is not the primary constraint." Inference trap: "users worldwide are actively served from the nearest Region, and any Region can be lost without customer impact" — Multi-Site Active-Active, unnamed.

### Quick Classification Heuristic for Ambiguous Wording
Ask, in order:
1. Is anything besides backups/snapshots running continuously in the DR Region? No → **Backup and Restore**.
2. Is only the data/replication layer running (no app/compute tier)? → **Pilot Light**.
3. Is a full (but downsized) stack running, requiring a scale-up step to reach production capacity? → **Warm Standby**.
4. Is full-capacity production traffic already being actively served from 2+ Regions with no scale-up step? → **Multi-Site Active-Active**.

Cost and RTO/RPO move in lockstep and inversely: cheapest = slowest recovery/most data loss (Backup & Restore); most expensive = fastest recovery/least data loss (Active-Active). Whenever the exam gives an explicit RTO/RPO number or a budget constraint without naming a strategy, map it along this spectrum rather than searching for the literal term.
