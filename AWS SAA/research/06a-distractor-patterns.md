# AWS SAA-C03 — How AWS Tricks You With Plausible Answers

# How AWS Tricks You With Plausible Answers — SAA-C03 Distractor Training

*Original study material — not real exam questions. Built for exam pattern-recognition practice
against current (2026) AWS service behavior and the official SAA-C03 exam guide (Phase 13 of the
research brief: "HOW AWS TRICKS YOU WITH PLAUSIBLE ANSWERS").*

**How to use this file:** SAA-C03 rarely has one clearly right answer and three clearly broken
ones. Instead, most wrong answers *work* — they just fail some unstated-but-implied constraint
(cost, ops burden, HA, security, or "least X" wording). Each pattern below is a category of trap.
For each one: a scenario, the answer that *feels* right, the answer that *is* right, and the one
sentence that separates them. Read the "decisive difference" line out loud — that's the sentence
you should be able to produce for any real exam question before picking an answer.

---

## 1. Possible but overly complicated

The tempting answer technically achieves the goal but reinvents a wheel AWS already sells as a
single managed feature — usually recognizable because it requires you to build and wire together
several primitives to match what one native service already does.

**Example A — Global content delivery**
- **Scenario:** A static marketing site needs low latency worldwide and basic DDoS resilience.
- **Tempting answer:** Deploy EC2 web servers in every AWS Region behind a Route 53 latency-based
  routing policy, with a custom sync job pushing content from S3 to each fleet.
- **Correct answer:** Host the site in a single S3 bucket (static website hosting) fronted by a
  single CloudFront distribution.
- **Decisive difference:** CloudFront already replicates content to hundreds of edge locations and
  integrates with AWS Shield — standing up and content-syncing a multi-region EC2 fleet reinvents a
  CDN AWS already operates for you.

**Example B — Decoupling with fan-out**
- **Scenario:** A producer service must not block on consumer availability, and multiple independent
  consumers need to process every event.
- **Tempting answer:** Have consumers repeatedly list an S3 bucket for new objects, process them,
  delete them, and use a DynamoDB table to track "already processed" status and avoid duplicates.
- **Correct answer:** Publish events to an SNS topic with multiple SQS queue subscriptions (the
  SNS→SQS fan-out pattern).
- **Decisive difference:** SNS/SQS fan-out gives push delivery, per-consumer independent processing,
  and built-in visibility-timeout/retry handling for free (with FIFO queues available if strict
  ordering/dedup is required); the S3-polling-plus-DynamoDB design hand-rolls a message queue,
  complete with race conditions AWS's managed services already solved.

**Example C — Multi-VPC connectivity at scale**
- **Scenario:** Six VPCs across departments must all communicate, with new VPCs onboarding
  regularly.
- **Tempting answer:** Create a full-mesh of VPC Peering connections between every pair of VPCs and
  update every affected route table each time a new VPC joins.
- **Correct answer:** Attach every VPC once to a central AWS Transit Gateway.
- **Decisive difference:** Peering connections grow quadratically (n(n-1)/2) and don't support
  transitive routing, so every new VPC means touching every existing route table; Transit Gateway
  needs one attachment per VPC and centralizes routing, so growth stays linear.

---

## 2. Works but expensive

The tempting answer is functionally correct but ignores a cost lever the scenario is quietly
testing — usually a pricing model mismatch (on-demand vs. committed, wrong storage tier, or paying
for a network path that has a free alternative).

**Example A — NAT Gateway vs. Gateway VPC Endpoint**
- **Scenario:** EC2 instances in private subnets read/write terabytes of data to S3 every month.
- **Tempting answer:** Route S3 traffic out through the existing NAT Gateway, since it already
  provides internet egress and "it works."
- **Correct answer:** Add an S3 Gateway VPC Endpoint so traffic reaches S3 without touching the NAT
  Gateway.
- **Decisive difference:** NAT Gateway bills a per-GB data processing charge on every byte that
  passes through it, while a Gateway VPC Endpoint for S3 (or DynamoDB) is free and keeps that
  traffic off the NAT device entirely — same connectivity, materially different bill at TB scale.

**Example B — Steady-state compute pricing**
- **Scenario:** A production workload has a stable, well-understood baseline load that will run
  24/7 for the next three years.
- **Tempting answer:** Keep running On-Demand EC2 instances indefinitely — no commitment, always
  available, simplest to reason about.
- **Correct answer:** Purchase a Reserved Instance or Savings Plan sized to the known baseline (with
  On-Demand only covering burst above it).
- **Decisive difference:** On-Demand "always works" but is the highest per-hour rate; a multi-year
  commitment against a workload that is explicitly steady and predictable is the textbook signal to
  trade flexibility you don't need for a substantial discount.

**Example C — Storage class for cold data**
- **Scenario:** Compliance requires seven-year retention of audit logs that are accessed roughly
  once a year, and a 12-hour retrieval time is explicitly acceptable.
- **Tempting answer:** Leave the logs in S3 Standard (or Standard-IA) indefinitely because retrieval
  is instant and nobody has to think about restore delays.
- **Correct answer:** Add an S3 Lifecycle rule transitioning the objects to S3 Glacier Deep Archive
  shortly after creation.
- **Decisive difference:** Standard/Standard-IA cost far more per GB-month than Deep Archive for data
  that is essentially write-once-read-never; Deep Archive's ~12-hour retrieval sits comfortably
  inside the stated tolerance, so paying for instant access nobody needs is pure waste.

---

## 3. Works but high operational overhead

The tempting answer is a self-managed version of a capability AWS sells as a managed service. It
runs fine on day one; the trap is the ongoing patching, scaling, and failure-handling toil it
quietly commits the team to.

**Example A — Self-managed Kafka vs. MSK**
- **Scenario:** A small platform team needs a durable streaming ingestion pipeline for clickstream
  events and wants to minimize ongoing operational burden.
- **Tempting answer:** Stand up a self-managed Apache Kafka cluster on EC2, handling broker
  patching, storage scaling, and failure recovery in-house.
- **Correct answer:** Amazon MSK (or MSK Serverless).
- **Decisive difference:** MSK abstracts broker provisioning, patching, and recovery; self-managed
  Kafka on EC2 is technically possible but hands the team hours of recurring toil for a capability
  AWS already operates as a managed service.

**Example B — Custom backup automation vs. AWS Backup**
- **Scenario:** An RDS database needs automated backups, point-in-time recovery, and cross-region
  backup copies retained for compliance.
- **Tempting answer:** Write a Lambda function on an EventBridge schedule that calls the RDS
  snapshot API, copies snapshots cross-region, and tags/expires old ones.
- **Correct answer:** Enable RDS automated backups and point-in-time recovery, and use AWS Backup
  with a cross-region copy rule.
- **Decisive difference:** The custom Lambda path requires you to build and maintain the exact
  retention/expiry/error-handling logic AWS Backup already ships with — same outcome, but now you
  own a small application whose bugs can silently break compliance.

**Example C — Manual fleet patching vs. Systems Manager**
- **Scenario:** 200 EC2 instances across environments need consistent OS patching within a defined
  maintenance window, with compliance reporting.
- **Tempting answer:** Engineers SSH into each instance (or run custom shell scripts from a bastion)
  on a schedule.
- **Correct answer:** AWS Systems Manager Patch Manager with a patch baseline and maintenance
  window.
- **Decisive difference:** Patch Manager centrally schedules, applies, and reports on compliance
  across the whole fleet; manual/scripted SSH patching works for a handful of instances but doesn't
  scale without becoming someone's full-time job.

---

## 4. Violates HA requirement (e.g., single-AZ)

The tempting answer looks resilient because *something* is redundant (backups exist, a load
balancer is configured) but a single AZ is still a single point of failure somewhere in the design.

**Example A — RDS backups vs. Multi-AZ**
- **Scenario:** A production order-processing database must survive the loss of an entire
  Availability Zone with automatic failover and minimal downtime.
- **Tempting answer:** A single-AZ RDS instance with automated backups enabled for recovery.
- **Correct answer:** Enable RDS Multi-AZ (a synchronous standby in a second AZ with automatic
  failover).
- **Decisive difference:** Automated backups protect against data loss and let you recover in
  minutes-to-hours from a snapshot, but they do nothing for availability during an AZ outage;
  Multi-AZ is what makes failover automatic, typically completing within one to two minutes with no
  manual intervention.

**Example B — ASG confined to one AZ**
- **Scenario:** A web tier must remain available if any single AZ becomes unavailable.
- **Tempting answer:** Run an Auto Scaling group behind an ALB, but place every subnet, target, and
  the ASG itself inside a single AZ "for simplicity" and lower inter-instance latency.
- **Correct answer:** Spread the ASG (and the ALB's subnets) across at least two AZs.
- **Decisive difference:** An ALB registered only to targets in one AZ still has an AZ-level single
  point of failure — HA requires the Auto Scaling group to actually span multiple AZs, not just sit
  behind a load balancer that's theoretically capable of it.

**Example C — EFS One Zone**
- **Scenario:** A shared file system for a multi-AZ application fleet must remain accessible if one
  AZ fails.
- **Tempting answer:** Use the EFS One Zone storage class because it's cheaper and simpler.
- **Correct answer:** Use standard (regional) EFS, which replicates data across multiple AZs by
  design.
- **Decisive difference:** EFS One Zone deliberately trades AZ resilience for a lower price — it is
  explicitly not designed to survive an AZ failure, so it fails a stated HA requirement no matter
  how attractive the cost looks.

---

## 5. Violates security best practice

The tempting answer is the "fastest to implement" option. It's almost always recognizable because
it either opens something to the public internet or hands out broad, unaudited access instead of
scoped, revocable access.

**Example A — Public S3 bucket vs. pre-signed URLs**
- **Scenario:** An app needs to serve private user-uploaded images, with access controlled by
  app-level authorization.
- **Tempting answer:** Make the bucket/objects public-read so the app (and anyone with the URL) can
  fetch images directly.
- **Correct answer:** Keep the bucket private (Block Public Access on) and use time-limited
  pre-signed URLs, or serve through CloudFront with Origin Access Control.
- **Decisive difference:** A public bucket grants permanent, unrevocable, unaudited access to
  anyone with the URL; pre-signed URLs/OAC give the same user experience while keeping the bucket
  private and access time-bound and traceable.

**Example B — Open SSH vs. Session Manager**
- **Scenario:** Administrators need occasional shell access to EC2 instances in private subnets.
- **Tempting answer:** Open inbound port 22 to 0.0.0.0/0 in the security group so admins can connect
  from anywhere.
- **Correct answer:** Use AWS Systems Manager Session Manager (no inbound port required), or
  restrict SSH to a bastion/VPN CIDR if a shell-in-terminal workflow is mandatory.
- **Decisive difference:** Session Manager needs zero open inbound ports and produces an IAM-audited
  session log; opening SSH to the entire internet is a standing, scannable attack surface that any
  "least exposure" requirement should immediately flag.

**Example C — Default SSE-S3 vs. customer-managed KMS key**
- **Scenario:** Compliance requires that all data at rest be encrypted *and* that the company can
  control and audit exactly which principals can use the encryption key.
- **Tempting answer:** Enable default SSE-S3 encryption on the bucket and consider the requirement
  met, since "encryption is on."
- **Correct answer:** Use SSE-KMS with a customer-managed key (CMK) whose key policy scopes which
  principals may use it, with usage logged via CloudTrail.
- **Decisive difference:** SSE-S3 encrypts data but the key is fully AWS-managed with no
  per-principal access control or usage audit trail; a customer-managed KMS key is what actually
  satisfies "control and audit who can decrypt this data."

---

## 6. Long-lived credentials where a role/temporary credential fits

The tempting answer is an IAM user with an access key — it's the most familiar mechanism, but it's
almost never the right answer whenever a *compute resource* or *federated identity* needs AWS API
access, because a role can hand out temporary credentials instead.

**Example A — EC2 instance calling S3/DynamoDB**
- **Scenario:** An application on EC2 needs to call S3 and DynamoDB APIs.
- **Tempting answer:** Create an IAM user, generate an access key/secret pair, and store them in
  environment variables (or bake them into the AMI).
- **Correct answer:** Attach an IAM role to the instance via an instance profile and let the SDK
  retrieve credentials automatically.
- **Decisive difference:** An instance-profile role hands the SDK short-lived, automatically-rotated
  credentials with nothing to leak; a long-lived access key pair is a permanent secret that must be
  manually rotated and remains valid forever if it leaks.

**Example B — CI/CD pipeline deploying to AWS**
- **Scenario:** A GitHub Actions workflow needs to deploy CloudFormation stacks into an AWS account.
- **Tempting answer:** Create an IAM user with programmatic access and store its access key/secret
  as a GitHub repository secret for the workflow to use.
- **Correct answer:** Configure an IAM OIDC identity provider for GitHub Actions and have the
  workflow assume an IAM role via `sts:AssumeRoleWithWebIdentity`, scoped to that repo/branch.
- **Decisive difference:** OIDC federation issues short-lived credentials scoped to a single
  workflow run with no static secret stored anywhere; a long-lived key in repo secrets is a
  permanent credential that keeps working even after the pipeline that needed it is long gone.

**Example C — Cross-account access**
- **Scenario:** A Lambda function in Account A needs to read a DynamoDB table in Account B.
- **Tempting answer:** Create an IAM user in Account B, generate an access key/secret, and pass them
  into Account A's Lambda as environment variables.
- **Correct answer:** Create an IAM role in Account B whose trust policy allows Account A's Lambda
  execution role to assume it via `sts:AssumeRole`.
- **Decisive difference:** A cross-account role produces temporary, CloudTrail-logged
  assume-role events scoped to exactly the needed permissions; distributing Account B's static keys
  creates an unrotated, unscoped secret now living inside another account's code.

---

## 7. Manual scaling instead of Auto Scaling

The tempting answer keeps a human (or a runbook a human triggers) in the scaling loop. It's
recognizable whenever "someone watches a dashboard and acts" replaces a metric-driven or
schedule-driven policy.

**Example A — Predictable daily traffic pattern**
- **Scenario:** Traffic spikes every weekday morning and drops off at night; capacity should track
  demand without human intervention.
- **Tempting answer:** An on-call engineer manually launches extra EC2 instances each morning and
  terminates them each evening per a runbook.
- **Correct answer:** An EC2 Auto Scaling group with a scheduled scaling policy (or dynamic/
  target-tracking scaling on CPU or request count).
- **Decisive difference:** Scheduled/dynamic Auto Scaling reacts precisely and automatically to the
  known pattern with no human latency or missed-step risk; manual scaling depends on a person being
  available and remembering to act, every single day.

**Example B — Bursty DynamoDB traffic**
- **Scenario:** A DynamoDB table sees unpredictable, bursty traffic; the team currently watches a
  CloudWatch alarm and manually raises provisioned RCU/WCU when throttling starts.
- **Tempting answer:** Stay on Provisioned capacity mode and keep manually adjusting RCU/WCU when
  alarms fire.
- **Correct answer:** Switch to DynamoDB On-Demand capacity mode (or enable Application Auto
  Scaling on the provisioned table).
- **Decisive difference:** On-Demand absorbs sudden traffic spikes without any manual capacity
  planning; manual RCU/WCU adjustment always lags the spike, since throttling has to happen first
  before a human notices and reacts.

**Example C — ECS service sizing**
- **Scenario:** An ECS service's task count needs to grow and shrink with request latency during
  unpredictable traffic.
- **Tempting answer:** An engineer periodically runs `aws ecs update-service --desired-count` based
  on eyeballing a CloudWatch dashboard.
- **Correct answer:** Configure ECS Service Auto Scaling (Application Auto Scaling) with a
  target-tracking policy on a metric such as `ALBRequestCountPerTarget` or CPU utilization.
- **Decisive difference:** Target-tracking scaling adjusts desired count within seconds of the
  metric changing; manual CLI updates require a human watching a dashboard around the clock and
  reacting after the fact.

---

## 8. EC2 solution where managed/serverless is preferable

The tempting answer is "keep a server running for it," even when the workload is short, spiky, or
zero-to-low most of the time — exactly the profile Lambda/Fargate/API Gateway are built for.

**Example A — A five-minute daily job**
- **Scenario:** A nightly report runs for five minutes, once a day, then does nothing until the next
  run.
- **Tempting answer:** Keep a small EC2 instance running 24/7 with a cron job "just in case," so the
  report always fires reliably.
- **Correct answer:** An AWS Lambda function triggered by an EventBridge scheduled rule.
- **Decisive difference:** Lambda only runs (and is billed) for the five minutes of actual work;
  an always-on EC2 instance pays for roughly 23 hours 55 minutes of idle time — plus patching — to
  produce the exact same daily output.

**Example B — Spiky, unpredictable API traffic**
- **Scenario:** A new product's API has unpredictable traffic — sometimes zero requests for hours,
  sometimes sudden bursts — and the team wants to avoid managing servers.
- **Tempting answer:** An Auto Scaling group of EC2 instances behind an ALB, scaled to a minimum of
  one instance to control cost.
- **Correct answer:** Amazon API Gateway with AWS Lambda (or Fargate for longer-running requests).
- **Decisive difference:** Lambda scales from zero to thousands of concurrent invocations
  automatically and costs nothing at zero traffic; even a "min of 1" EC2 instance is a fixed
  always-on cost that still needs OS patching, which the serverless path removes entirely.

**Example C — Containers without managing worker nodes**
- **Scenario:** A team wants to run containerized microservices using standard Docker images
  without managing or patching the underlying compute.
- **Tempting answer:** Run ECS/EKS with self-managed EC2 worker nodes, since the team is already
  comfortable with EC2.
- **Correct answer:** Run the same containers on ECS/EKS with the Fargate launch type.
- **Decisive difference:** Fargate eliminates worker-node provisioning, patching, and capacity
  management entirely — you only define tasks/pods; EC2 worker nodes still require you to operate an
  underlying server fleet, which is exactly what "prefer managed/serverless" is testing for.

---

## 9. Wrong load balancer type (ALB / NLB / GWLB mismatch)

All three "sound" like reasonable load balancers. The trap is picking based on vague notions like
"performance" or "it's the default" instead of the specific OSI layer and feature the scenario
actually needs.

**Example A — Path-based routing needs ALB, not NLB**
- **Scenario:** An app must route `/api/*` to one target group and `/images/*` to another, based on
  HTTP path, across microservices.
- **Tempting answer:** A Network Load Balancer, because it "handles more throughput" and sounds like
  the higher-performance choice.
- **Correct answer:** An Application Load Balancer (path-based/host-based routing is a Layer 7
  feature).
- **Decisive difference:** NLB operates at Layer 4 and has no concept of HTTP paths or headers —
  content-based routing only exists on ALB, so raw throughput isn't the axis this question is
  actually testing.

**Example B — Static IP and source-IP preservation needs NLB, not ALB**
- **Scenario:** A trading platform needs millions of requests per second at ultra-low, consistent
  latency, must preserve the client's source IP, and needs a static/Elastic IP per AZ.
- **Tempting answer:** An Application Load Balancer, since it's the "default"/most commonly
  recommended choice for most workloads.
- **Correct answer:** A Network Load Balancer.
- **Decisive difference:** NLB offers far higher throughput and more consistent low latency than
  ALB, and it's the only ELB type that supports a static/Elastic IP per AZ and preserves the source
  IP by default — requirements ALB simply doesn't meet.

**Example C — Transparent appliance insertion needs GWLB, not ALB**
- **Scenario:** A company wants to insert a scalable fleet of third-party virtual appliances (e.g.,
  deep packet inspection) transparently in front of all inbound VPC traffic, regardless of protocol.
- **Tempting answer:** Front the appliance fleet with an Application Load Balancer.
- **Correct answer:** A Gateway Load Balancer.
- **Decisive difference:** GWLB is purpose-built to distribute traffic to a scalable third-party
  appliance fleet at Layer 3 using GENEVE encapsulation while keeping the path transparent; ALB
  operates strictly at Layer 7 over HTTP/HTTPS and can't pass arbitrary IP traffic through
  appliances at all.

---

## 10. Wrong database replication method (Multi-AZ vs. Read Replica confusion)

Both features add a second copy of the database, so the trap is picking based on "more copies =
more resilient" instead of matching the mechanism (synchronous standby vs. asynchronous readable
copy) to whether the requirement is availability, read scaling, or cross-region reach.

**Example A — Automatic failover needs Multi-AZ, not a Read Replica**
- **Scenario:** A production database must automatically fail over with minimal downtime if the
  primary or its AZ fails; there's no read-scaling problem, purely an availability requirement.
- **Tempting answer:** Create a Read Replica in a second AZ and manually promote it if the primary
  fails.
- **Correct answer:** Enable RDS Multi-AZ (a synchronous standby with automatic failover).
- **Decisive difference:** A Multi-AZ standby is kept in synchronous lock-step and fails over
  automatically — typically within one to two minutes, with no data loss and no manual step; a Read
  Replica uses asynchronous replication and requires a manual promotion, making it a DR/scaling tool,
  not an HA/failover tool.

**Example B — Read scaling needs a Read Replica, not Multi-AZ**
- **Scenario:** A read-heavy reporting workload is saturating the primary RDS instance's CPU with
  SELECT queries, while writes stay light; the team wants to offload reads without touching writes.
- **Tempting answer:** Enable Multi-AZ and point some read traffic at the standby instance to spread
  the load.
- **Correct answer:** Create one or more Read Replicas and direct read traffic to them.
- **Decisive difference:** The classic single-standby RDS Multi-AZ deployment is not accessible for
  application read or write traffic — it exists purely for failover. (Newer Multi-AZ DB cluster
  deployments do permit limited reads from their two standbys, but that capacity is bound to the
  HA/failover architecture, not an independently scalable read path.) A Read Replica is the tool
  purpose-built for offloading and scaling reads.

**Example C — Cross-region low-latency reads need Aurora Global Database, not per-region Multi-AZ**
- **Scenario:** A global application needs low-latency reads in three AWS Regions from a single
  Aurora database that keeps accepting writes in one Region.
- **Tempting answer:** Deploy independent Multi-AZ Aurora clusters in each of the three Regions and
  sync data between them with custom application-level replication logic.
- **Correct answer:** Aurora Global Database, replicating the primary Region's cluster to up to five
  secondary Regions with typically sub-second replica lag, using dedicated replication
  infrastructure.
- **Decisive difference:** Multi-AZ only protects within a single Region; a managed cross-region
  replication path with low-latency reads is exactly what Aurora Global Database provides natively,
  with no custom sync code required.

---

## 11. Wrong storage service selection

All the AWS storage services can technically "store the bytes." The trap is matching the access
pattern (block vs. shared file vs. object, single-instance vs. many-instance, general-purpose vs.
HPC-scale) to the right service instead of the one that sounds most flexible.

**Example A — Many-instance shared file access needs EFS, not EBS Multi-Attach**
- **Scenario:** A legacy application migrating to EC2 needs a shared file system mountable by
  hundreds of Linux instances concurrently, with POSIX permissions.
- **Tempting answer:** Attach a single EBS volume with Multi-Attach enabled so every instance can
  mount the same block volume.
- **Correct answer:** Amazon EFS (or Amazon FSx for Windows File Server if the requirement is
  SMB/Windows instead).
- **Decisive difference:** EBS Multi-Attach only shares a raw block volume between a handful of
  instances in a single AZ and needs a cluster-aware file system layered on top; EFS is a
  regionally-resilient, POSIX-compliant network file system purpose-built for many-instance
  concurrent file access.

**Example B — Single-instance database storage needs EBS, not EFS**
- **Scenario:** A self-managed relational database on a single EC2 instance needs sustained high
  IOPS and low, consistent latency for its data volume.
- **Tempting answer:** Use Amazon EFS because it "auto-scales storage" and sounds more hands-off than
  provisioning an EBS volume size upfront.
- **Correct answer:** Amazon EBS (io2 Block Express, or gp3 with provisioned IOPS) attached to the
  instance.
- **Decisive difference:** EFS is a network file system optimized for shared, elastic access with
  higher per-operation latency; a single-instance workload needing consistent low-latency block I/O
  is exactly EBS's use case, and EFS is a worse fit despite sounding "simpler."

**Example C — HPC scratch storage needs FSx for Lustre, not EFS**
- **Scenario:** An HPC training job on EC2 needs a scratch file system with hundreds of GB/s
  throughput and sub-millisecond latency, tightly integrated with training data already in S3.
- **Tempting answer:** Use Amazon EFS since it's the "standard" shared-file-system answer for
  multi-instance workloads.
- **Correct answer:** Amazon FSx for Lustre, linked to the S3 bucket as its data repository.
- **Decisive difference:** FSx for Lustre is purpose-built for high-throughput, low-latency HPC
  scratch workloads with native S3 data-repository integration; EFS's throughput/latency profile is
  designed for general-purpose shared file access, not HPC-scale parallel compute.

---

## Quick-reference: the one-sentence tell for each pattern

| Pattern | The tell |
|---|---|
| Overly complicated | You're assembling several primitives to match what one managed feature already does. |
| Works but expensive | The workload profile (steady, cold, predictable) signals a pricing model you didn't apply. |
| High operational overhead | You're volunteering to patch/scale/recover something AWS already manages. |
| Single-AZ / HA violation | A backup or snapshot is doing the job a synchronous standby should be doing. |
| Security best practice violation | Something is public, or a port is open to 0.0.0.0/0, or a key is unaudited. |
| Long-lived credentials | A human-shaped credential (IAM user + access key) is doing a machine-shaped job. |
| Manual scaling | A human watching a dashboard is standing in for a metric or schedule. |
| EC2 instead of managed/serverless | You're paying for idle capacity to handle short or spiky work. |
| Wrong load balancer | The requirement (path routing, static IP, appliance insertion) maps to one specific ELB type. |
| Wrong DB replication | Ask: is this about failover (Multi-AZ) or read scaling/cross-region (Read Replica/Global Database)? |
| Wrong storage service | Ask: block or file? single-instance or shared? general-purpose or HPC-scale? |
