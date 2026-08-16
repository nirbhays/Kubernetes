# SAA-C03 Practice Questions — Domain 2: Design Resilient Architectures (26%)
Focus: Auto Scaling Group policies & health checks | Lambda resilience patterns | DR strategy selection (Backup & Restore, Pilot Light, Warm Standby, Multi-Site Active-Active)

Original practice content created for study purposes — these are **not** real AWS exam questions and do not reproduce any leaked/dumped exam content. Based on 2026 AWS service behavior and the official SAA-C03 exam guide scope.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A ticketing platform runs a Java web application behind an Application Load Balancer and an Auto Scaling group. Average CPU utilization fluctuates unpredictably throughout the day — sometimes 20%, sometimes 70% — with no recurring daily pattern the team can rely on. The platform team wants the ASG to continuously and automatically add or remove instances to keep average CPU near 50%, without the team having to define and maintain multiple manual thresholds.
**Options:**
A. Configure a target tracking scaling policy with a target value of 50% average CPU utilization.
B. Configure simple scaling with a single CloudWatch alarm threshold at 50% CPU and a fixed cooldown period.
C. Configure scheduled scaling actions that increase capacity at historically busy hours of the day.
D. Have an operator manually run `aws autoscaling set-desired-capacity` via a cron job on a monitoring server.
**Correct answer(s):** A
**Why correct:** Target tracking scaling is purpose-built to keep a chosen metric at (or near) a specified target value, continuously adjusting capacity up or down without manually maintained thresholds — exactly what's needed for unpredictable, non-recurring traffic.
**Why each wrong option is wrong:** B (simple scaling) reacts to a single alarm crossing a threshold and then waits out a cooldown before acting again, which doesn't continuously track a target the way target tracking does, and still requires manual threshold tuning; C (scheduled scaling) only helps if traffic follows a known, recurring time pattern, which this scenario explicitly says it does not; D introduces manual operational overhead and a single point of failure (the monitoring server/cron job), which defeats the goal of automatic scaling.
**Trigger words:** "fluctuates unpredictably," "no recurring daily pattern," "keep average CPU near 50%," "without... manually maintained... thresholds."
**Underlying architectural principle:** Target tracking is the default best-practice Auto Scaling policy for maintaining a metric at a set point under unpredictable load.

---

### Question 2 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company runs an Auto Scaling group of EC2 instances registered to an ALB target group. The EC2 console shows all instances as healthy, but the ALB target group console shows roughly 30% of targets as unhealthy because the application intermittently returns HTTP 500 on its `/health` endpoint due to a slow-starting internal cache. The ASG never replaces these targets, so a meaningful share of live customer traffic keeps hitting instances returning errors.
**Options:**
A. Enable the ELB health check type on the Auto Scaling group so the ASG uses the target group's health check results to decide when to replace instances.
B. Set the ASG's health check grace period to 0 seconds so instances are evaluated immediately after launch.
C. Increase the target group's deregistration delay to 900 seconds.
D. Replace the ALB with a Network Load Balancer, since NLB health checks are stricter than ALB health checks.
**Correct answer(s):** A
**Why correct:** By default, an ASG only uses EC2 status checks (instance reachability), which cannot see application-level failures reported by a target group. Enabling the ELB health check type makes the ASG honor the target group's health verdict and replace instances the load balancer considers unhealthy.
**Why each wrong option is wrong:** B changes when health evaluation starts, not which health check source the ASG listens to, and setting it to 0 would risk terminating instances before they even finish booting; C only controls how long an already-deregistering target keeps draining in-flight connections, it does nothing to make the ASG detect or act on the /health failures; D swaps load balancer types without addressing the actual root cause — the ASG still would not be configured to use ELB health check results, so replacing the ALB with an NLB (which can itself be configured with HTTP/HTTPS-based health checks, not just TCP) changes nothing about the ASG-to-target-group integration that's actually broken here.
**Trigger words:** "EC2 console shows all instances as healthy," "target group... shows... unhealthy," "ASG never replaces these targets."
**Underlying architectural principle:** An ASG must be explicitly configured to use ELB health checks, or it will remain blind to application-level failures that only the load balancer's health checks can detect.

---

### Question 3 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A media transcoding company runs its worker fleet on Spot Instances in an Auto Scaling group spread across three Availability Zones to control compute cost — the team is cost-sensitive and must continue using Spot Instances rather than On-Demand. Each instance takes about 6 minutes to boot and initialize because it must download large codec libraries before it can process jobs. The team wants to (1) reduce the customer-facing impact when Spot Instances receive an interruption notice, and (2) reduce the lag between a scale-out trigger and having usable capacity, without paying for a fully active standby fleet at all times.
**Options:**
A. Enable Auto Scaling group Capacity Rebalancing and maintain a Warm Pool of pre-initialized, mostly-stopped instances.
B. Change the ASG termination policy to `OldestInstance` and disable automatic instance rebalancing.
C. Migrate the entire fleet from Spot to On-Demand Instances and rely on target tracking scaling alone.
D. Run a single large Spot Instance outside of an Auto Scaling group with a shell script that restarts it if it's interrupted.
**Correct answer(s):** A
**Why correct:** Capacity Rebalancing proactively replaces Spot Instances that receive a rebalance recommendation before they're actually reclaimed, directly reducing interruption impact, while a Warm Pool keeps pre-initialized (largely stopped, low-cost) instances ready to join the ASG quickly, directly cutting the 6-minute boot lag — together they solve both stated problems without running a fully active standby fleet.
**Why each wrong option is wrong:** B's termination policy choice only affects which instance is selected for termination during scale-in, and disabling rebalancing actively removes the interruption-mitigation behavior the team needs; C solves reliability but directly contradicts the stated cost-sensitivity constraint requiring continued use of Spot; D removes Auto Scaling and multi-AZ resilience entirely, creating a single point of failure with no automated health-based recovery.
**Trigger words:** "cost-sensitive and must continue using Spot," "6 minutes to boot," "reduce... impact when Spot Instances receive an interruption notice," "without paying for a fully active standby fleet."
**Underlying architectural principle:** Warm Pools cut scale-out latency for slow-booting instances while Capacity Rebalancing proactively mitigates Spot interruptions — the two features solve different resilience problems and are commonly combined.

---

### Question 4 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An order-processing Lambda function is invoked asynchronously by S3 object-created events. Occasionally the function fails because a downstream partner API returns transient errors. The team wants failed events to never simply disappear, and wants a durable, queryable record of failed invocations that a separate reprocessing pipeline can consume later — with as little custom retry code as possible.
**Options:**
A. Configure an on-failure destination pointing to an SQS queue, so failed events are routed there automatically after Lambda's built-in asynchronous retries are exhausted.
B. Increase the Lambda function's timeout to 15 minutes so the transient partner API errors no longer cause failures.
C. Wrap the S3 event trigger in a synchronous Step Functions Express Workflow with a Catch state to handle errors.
D. Set the function's reserved concurrency to 0 until the partner API issue is resolved.
**Correct answer(s):** A
**Why correct:** Asynchronous Lambda invocations already retry automatically (twice, by default) on failure; configuring an on-failure destination is the native, code-minimal way to durably route events that still fail after those retries into SQS for later reprocessing, satisfying both the durability and "queryable record" requirements.
**Why each wrong option is wrong:** B doesn't address the root cause (an unreliable downstream API returning errors, not a slow one) and a longer timeout doesn't guarantee success or capture failures for reprocessing; C requires re-architecting the trigger path with a workflow orchestrator (S3 event notifications don't invoke Step Functions directly — an intermediary such as EventBridge would be needed), which is unnecessary custom-integration effort compared to the built-in destinations feature and doesn't fit "as little custom retry code as possible"; D would stop the function from processing any events at all, losing new orders rather than preserving failed ones.
**Trigger words:** "asynchronously," "transient errors," "never simply disappear," "durable, queryable record," "as little custom retry code as possible."
**Underlying architectural principle:** Lambda's built-in asynchronous retry behavior combined with on-failure destinations is the standard, low-code pattern for capturing and durably routing failed async invocations.

---

### Question 5 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A small nonprofit runs a low-traffic donor management application. The budget is extremely tight, and leadership has explicitly accepted up to 8 hours of downtime and up to 24 hours of data loss in the event of a regional disaster, since such an event is considered rare and no ongoing DR spend is desired. The team already takes nightly RDS and EBS snapshots and copies AMIs to a second region; nothing else currently runs in that second region.
**Options:**
A. Use AWS Backup (or equivalent) with cross-region copy of snapshots/AMIs, and keep CloudFormation templates ready so the full environment can be launched on demand in the second region only if a disaster is actually declared.
B. Run a continuously replicating cross-region read replica of the database with no application servers running in the second region.
C. Run a full but downsized copy of the entire stack, including application servers, continuously in the second region.
D. Run full-capacity production stacks simultaneously in both regions behind Route 53 latency-based routing.
**Correct answer(s):** A
**Why correct:** With an 8-hour RTO and a 24-hour RPO tolerance and an explicit "extremely tight budget" constraint, nightly cross-region backups (worst case, up to ~24 hours of data since the last snapshot) plus templated, on-demand launch (Backup and Restore) meets the stated tolerances at the lowest possible ongoing cost — there is no requirement that justifies paying for any standing DR-region infrastructure.
**Why each wrong option is wrong:** B (Pilot Light) introduces continuous cross-region replication cost that isn't needed to meet an RPO measured in a full day, since nightly snapshots already satisfy a 24-hour RPO tolerance; C (Warm Standby) adds continuously running compute cost that directly conflicts with the stated tight budget and isn't needed for an 8-hour RTO; D (Multi-Site Active-Active) is the most expensive of the four strategies and wildly exceeds both the budget constraint and the stated tolerance for downtime/data loss.
**Trigger words:** "extremely tight budget," "up to 8 hours of downtime," "up to 24 hours of data loss," "nightly... snapshots," "nothing else currently runs."
**Underlying architectural principle:** When RTO/RPO tolerance is measured in hours and cost is the dominant constraint, the correct classification is Backup and Restore — even if the strategy is never named in the scenario.

---

### Question 6 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A SaaS company maintains an Aurora Global Database secondary cluster continuously replicating in a second AWS region, with sub-second replication lag. No EC2 or ECS application resources currently run in that second region at all. If a disaster is declared, the plan is to promote the Aurora secondary to a standalone writer and use pre-baked launch templates and CloudFormation stacks to stand up the application tier from scratch, targeting a recovery time of roughly 30–45 minutes.
**Options:**
A. Pilot Light — only the data layer is kept live in the DR region (giving a low RPO), while the compute/application tier is provisioned on demand, consistent with a 30–45 minute RTO.
B. Backup and Restore — because no compute is running continuously in the DR region.
C. Warm Standby — because a continuously replicating database qualifies as the "reduced capacity" tier that's already running.
D. Multi-Site Active-Active — because Aurora Global Database is technically capable of serving reads from the secondary region.
**Correct answer(s):** A
**Why correct:** The defining signature of Pilot Light is a continuously replicating data tier with zero standing compute, where the application tier is provisioned from templates only when a disaster is declared — this matches the scenario exactly, and the 30–45 minute RTO is consistent with needing to provision compute from scratch.
**Why each wrong option is wrong:** B is wrong because Backup and Restore has no continuous replication at all (just periodic backups), and its typical RTO is hours, not tens of minutes, which this sub-second-replication design clearly beats; C is wrong because Warm Standby requires the application/compute tier itself to also be running (even at reduced capacity) — here there is no compute tier running at all, only the database; D is wrong because Multi-Site Active-Active requires production traffic to actually be served from multiple regions simultaneously, and here the secondary is not promoted and no application tier exists there to serve anything.
**Trigger words:** "no... application resources currently run," "promote the Aurora secondary," "pre-baked launch templates," "30–45 minutes."
**Underlying architectural principle:** A continuously replicating data tier paired with zero standing compute is the defining signature of Pilot Light, regardless of whether the term ever appears in the scenario.

---

### Question 7 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An insurance claims portal keeps a full copy of its architecture running at all times in a secondary region: an ALB, two `t3.micro` application instances at the ASG's minimum capacity, and an RDS read replica continuously replicating from the primary region. Under normal conditions this secondary-region stack only receives internal health-check traffic, no customer traffic. During a scheduled failover drill, Route 53 failover routing shifts customer traffic to the secondary region, and the ASG there scales from 2 to 40 instances within about 6 minutes to absorb full production load. The stated RTO target is under 15 minutes and RPO under 5 minutes.
**Options:**
A. Warm Standby — a full stack, including the application tier, is already running at reduced capacity, and failover only requires scaling up rather than provisioning from nothing.
B. Pilot Light — because the running application tier is minimal, consisting of only two small instances.
C. Backup and Restore — because most of the production capacity is only provisioned after failover is triggered.
D. Multi-Site Active-Active — because customer traffic is actively being served from the secondary region during the drill.
**Correct answer(s):** A
**Why correct:** Warm Standby is defined by a full (but downsized) stack — including the application/compute tier — running continuously, with failover consisting only of a scale-up step; that is exactly what's described here, and the sub-15-minute RTO and sub-5-minute RPO align with Warm Standby's typical numbers.
**Why each wrong option is wrong:** B is wrong because Pilot Light requires the application/compute tier to be entirely absent under normal conditions, not merely small — two running instances actively capable of serving traffic disqualifies it from being Pilot Light; C is wrong because Backup and Restore has nothing standing continuously in the DR region and typically recovers in hours, not the minutes described here; D is wrong because Multi-Site Active-Active means both regions serve live production traffic under normal day-to-day conditions, not only during a failover drill or an actual disaster.
**Trigger words:** "full copy of its architecture running at all times," "two... application instances at... minimum capacity," "scales from 2 to 40... on failover," "RTO... under 15 minutes."
**Underlying architectural principle:** The discriminator between Pilot Light and Warm Standby is whether an application/compute tier is running at all — even minimally — versus being entirely absent until a disaster is declared.

---

### Question 8 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A global multiplayer leaderboard service uses DynamoDB Global Tables replicated across three regions, with application servers actively serving live read/write production traffic simultaneously in all three regions via Route 53 latency-based routing. The stated requirement is near-zero RTO/RPO and tolerance for the loss of any single region with no customer-visible impact. During a load test, two players in different regions update the same leaderboard record within milliseconds of each other, and the team is worried one of the two updates might be silently lost.
**Options:**
A. This is a known, inherent trade-off of DynamoDB Global Tables' last-writer-wins conflict resolution under a Multi-Site Active-Active design; the team should redesign the data model to avoid concurrent writes to the same key where correctness matters (e.g., partitioning updates so each key is normally owned by one region), or add application-level version/timestamp attributes to detect conflicting updates after replication and reconcile them, rather than treating this as an architecture defect.
B. This indicates a misconfiguration; enabling strongly consistent reads across all three regions will eliminate the conflict.
C. The team should switch to Aurora Global Database instead, since it supports true multi-region simultaneous writes without conflicts.
D. This is unrelated to the DR strategy; the fix is to place a Global Accelerator in front of the three regions to serialize writes.
**Correct answer(s):** A
**Why correct:** DynamoDB Global Tables replicate asynchronously and resolve same-key conflicting writes with last-writer-wins; this is an accepted, well-documented trade-off of achieving near-zero RTO/RPO in a Multi-Site Active-Active design, and the correct response is to handle it at the data-model layer (avoid same-key concurrent writes, or detect and reconcile conflicts after the fact using version/timestamp attributes) rather than assume the platform is misconfigured.
**Why each wrong option is wrong:** B is wrong because there is no "strongly consistent read across regions" feature in DynamoDB Global Tables — consistent reads apply only within a single region/table, and cross-region replication remains asynchronous regardless; C is wrong because Aurora Global Database secondary regions are read-only until explicitly promoted, meaning it does not offer true multi-master simultaneous relational writes and would not even satisfy the stated active-active write requirement; D is wrong because Global Accelerator improves network-layer routing and failover performance for TCP/UDP traffic, it has no role in serializing or coordinating application-level database writes.
**Trigger words:** "DynamoDB Global Tables," "simultaneously in all three regions," "near-zero RTO/RPO," "worried one of the two updates might be silently lost."
**Underlying architectural principle:** Multi-Site Active-Active with DynamoDB Global Tables trades strict write consistency for near-zero RTO/RPO via eventual consistency and last-writer-wins conflict resolution, which must be managed in the application/data model, not fixed at the infrastructure layer.

---

### Question 9 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A ride-hailing company's pricing-quote API is built on API Gateway backed by a Java Lambda function. During sharp, predictable morning and evening commute-hour traffic spikes, p99 latency jumps to over 4 seconds because of JVM cold starts on newly initialized execution environments, even though overall average traffic isn't unusually high. The business requires consistently low latency (under 300ms p99) during these commute windows, and the team wants to keep the workload fully serverless with no new infrastructure to manage, and to avoid rewriting the function in a different runtime.
**Options:**
A. Configure Provisioned Concurrency on the function, scheduled (via Application Auto Scaling) to increase ahead of the known commute windows.
B. Increase only the function's memory allocation, leaving all concurrency settings at their defaults.
C. Set Reserved Concurrency equal to the peak expected number of concurrent executions.
D. Migrate the pricing-quote logic to a permanently running ECS Fargate service.
**Correct answer(s):** A
**Why correct:** Provisioned Concurrency pre-initializes execution environments so requests don't pay the cold-start initialization cost, and scheduling it ahead of known commute-hour spikes directly targets the described predictable pattern — this is the standard fix for cold-start-driven p99 latency spikes in a latency-sensitive Lambda workload.
**Why each wrong option is wrong:** B may reduce execution CPU time slightly but does nothing to eliminate the cold-start initialization delay itself, so the p99 spikes would persist; C caps or guarantees a level of concurrency but does not pre-warm execution environments, so cold starts still occur on newly created environments, and setting it too low risks throttling; D would technically eliminate cold starts (an always-on service has none), but Fargate still requires building and operating new infrastructure — a cluster, service definition, task definition, and typically a load balancer — which directly contradicts the stated requirement of "no new infrastructure to manage"; it's a disproportionate re-architecture when a targeted, schedulable Lambda configuration change meets the same latency requirement without adding anything new to operate.
**Trigger words:** "JVM cold starts," "p99 latency," "predictable... commute-hour... spikes," "fully serverless with no new infrastructure to manage," "avoid rewriting the function in a different runtime."
**Underlying architectural principle:** Provisioned Concurrency, ideally scheduled ahead of known traffic patterns, is the direct fix for cold-start latency spikes in latency-sensitive Lambda workloads.

---

### Question 10 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An inventory-sync Lambda function is triggered by an SQS event source mapping using a batch size of 10 (kept at 10 deliberately, since reducing it would raise per-invocation costs significantly for this high-volume queue). Occasionally 2 of the 10 messages in a batch fail due to a downstream validation error while the other 8 succeed. Today, Lambda treats the whole batch as failed, so all 10 messages return to the queue after the visibility timeout — including the 8 that already succeeded — and those 8 get reprocessed, producing duplicate inventory updates that break downstream idempotency assumptions. The team wants only the genuinely failed messages retried, while keeping the batch size at 10.
**Options:**
A. Enable partial batch response by having the function return `batchItemFailures` identifiers, and configure the event source mapping to use `ReportBatchItemFailures`.
B. Reduce the batch size to 1 so each message is processed and implicitly acknowledged individually.
C. Increase the SQS queue's visibility timeout to six times the function's timeout.
D. Switch the trigger from SQS to SNS, since SNS retries failed message deliveries individually.
**Correct answer(s):** A
**Why correct:** `ReportBatchItemFailures` combined with returning the specific failed message IDs is the native SQS-Lambda mechanism for reprocessing only the messages that actually failed within a batch, leaving successfully processed messages alone — solving the exact duplicate-reprocessing problem described while preserving the required batch size of 10.
**Why each wrong option is wrong:** B would technically prevent partial-batch duplication too, but it directly contradicts the stated requirement to keep batch size at 10 for cost/throughput reasons, so it is not a viable answer here; C only delays when failed messages become visible again for retry, it does nothing to distinguish which of the 10 messages actually failed, so the 8 successful ones would still eventually be redelivered and reprocessed; D changes the trigger's delivery and retry semantics entirely and doesn't provide the same durable, queue-backed redelivery model needed here — it's an unnecessary architecture change that doesn't directly solve the partial-batch-failure problem.
**Trigger words:** "2 of the 10... fail," "entire batch is treated as failed," "want only the genuinely failed messages retried," "keeping the batch size at 10."
**Underlying architectural principle:** `ReportBatchItemFailures` with a partial batch response is the standard SQS-to-Lambda pattern for retrying only failed messages within a batch, avoiding duplicate side effects from messages that already succeeded.

---

### Question 11 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A video transcoding fleet runs as background workers in an Auto Scaling group, polling an SQS queue for jobs — there is no load balancer or target group involved. Each job takes 3–5 minutes to finish and upload results to S3. During scale-in events, the ASG sometimes terminates an instance mid-job, losing the in-progress transcode entirely. The team needs instances to finish their current job and upload results before being terminated.
**Options:**
A. Configure an Auto Scaling lifecycle hook on the `EC2_INSTANCE_TERMINATING` transition that runs a script to complete the job and upload results before the instance is allowed to terminate.
B. Increase the ASG's health check grace period to 5 minutes.
C. Add an ALB target group in front of the workers solely to take advantage of connection draining.
D. Use EC2 Spot Instance hibernation so instances are paused instead of terminated during scale-in.
**Correct answer(s):** A
**Why correct:** A termination lifecycle hook pauses the ASG's termination process for a configurable window, giving a custom script time to finish the in-progress job and upload results before the instance actually terminates — this is precisely what's needed for a worker with no load balancer to rely on for draining.
**Why each wrong option is wrong:** B only affects how long the ASG waits before evaluating health checks after launch, it has no effect on the termination path during scale-in; C introduces a load balancer purely for its draining behavior even though these workers pull jobs from SQS rather than receive inbound connections, so connection draining is irrelevant and provides no guarantee the in-progress job itself finishes; D's hibernation feature is specific to Spot Instance interruption handling (it lets a Spot Instance's in-memory state be suspended to EBS instead of the instance being terminated when Spot capacity is reclaimed) — this scenario never establishes these are Spot Instances, and even where hibernation applies it pauses the in-progress job rather than running any custom logic to finish it and upload results, so it still doesn't satisfy the stated requirement of completing the job and persisting its output before the instance stops.
**Trigger words:** "no load balancer or target group involved," "finish their current job... before being terminated," "loses the in-progress transcode entirely."
**Underlying architectural principle:** Lifecycle hooks let custom code run to gracefully finish work before an ASG instance terminates, independent of any load-balancer-based draining mechanism.

---

### Question 12 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A backend fleet behind an ALB is managed by an Auto Scaling group. Two separate problems are occurring: (1) brief JVM garbage-collection pauses of up to 45 seconds occasionally cause an instance to fail a single health check, and the ASG immediately terminates and replaces an otherwise healthy instance, creating replacement churn and brief 502 errors; (2) newly launched instances take about 90 seconds to fully initialize, but some are being marked unhealthy and replaced within 30 seconds of launch, before initialization finishes. The team wants to reduce both kinds of unnecessary replacement without turning off health-based replacement altogether. (Choose two.)
**Options:**
A. Increase the target group's healthy/unhealthy threshold count so several consecutive failed checks are required before an instance is marked unhealthy.
B. Increase the ASG's health check grace period to at least the application's real initialization time (e.g., 120 seconds).
C. Disable ELB health checks on the ASG and rely solely on EC2 status checks.
D. Change the ASG's termination policy to `ClosestToNextInstanceHour`.
E. Reduce the target group's deregistration delay to 0 seconds so replacements happen faster.
**Correct answer(s):** A, B
**Why correct:** Raising the unhealthy threshold count means a single 45-second GC blip no longer trips replacement, since several consecutive failures would be needed; increasing the grace period past 90 seconds ensures new instances aren't evaluated for health at all until they've actually finished initializing, directly stopping the premature replacements.
**Why each wrong option is wrong:** C would stop both problems but only by removing the ability to detect real application-level failures entirely, which the scenario explicitly says to avoid; D only controls which instance is chosen when the ASG scales in, it has no effect on why instances are being incorrectly flagged unhealthy in the first place; E speeds up how quickly a deregistering target stops receiving new connections, but it does nothing to address why instances are being falsely marked unhealthy, and cutting drain time to zero could increase in-flight request errors during otherwise-correct replacements.
**Trigger words:** "GC pauses of up to 45 seconds," "marked unhealthy and replaced within 30 seconds of launch," "without turning off health-based replacement altogether."
**Underlying architectural principle:** False-positive instance replacements are usually solved by tuning health check thresholds and the grace period to match real application behavior, not by disabling health-based detection.

---

### Question 13 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** An architect is designing a Pilot Light disaster recovery strategy for a relational order-management system, targeting an RPO of about 5 minutes and an RTO of about 45 minutes, on a moderate budget that specifically avoids paying for continuous compute in the DR region. Which two elements belong in this design?
**Options:**
A. A cross-region Aurora/RDS read replica (or equivalent continuous database replication) running in the DR region at all times.
B. Pre-baked AMIs or launch templates plus Infrastructure-as-Code (e.g., CloudFormation) ready to launch the full application/compute tier in the DR region on demand.
C. A fully deployed application tier running at reduced capacity (e.g., 10% of production) continuously in the DR region.
D. Full-capacity production compute running simultaneously in both regions behind Route 53 latency-based routing.
E. Nightly database snapshots copied to the DR region with no continuous replication.
**Correct answer(s):** A, B
**Why correct:** Option A delivers the required ~5 minute RPO through continuous data replication while avoiding continuous compute cost, and option B is what makes the ~45 minute RTO achievable — the application tier is ready to launch from templates on demand rather than being built from scratch, without the cost of running it continuously.
**Why each wrong option is wrong:** C describes Warm Standby, since it keeps the application/compute tier itself running continuously (even at reduced capacity), which directly conflicts with the stated goal of avoiding continuous compute cost; D describes Multi-Site Active-Active, a far more expensive pattern than the moderate budget stated, and delivers a much lower RTO/RPO than what's required here; E describes Backup and Restore, whose RPO (hours, tied to snapshot frequency) is too coarse to meet the stated ~5 minute RPO requirement.
**Trigger words:** "RPO of about 5 minutes," "RTO of about 45 minutes," "moderate budget," "avoids paying for continuous compute."
**Underlying architectural principle:** Pilot Light is defined by continuously replicated data paired with templated, on-demand compute — introducing continuously running compute or relying only on periodic snapshots shifts the design into a different DR category.

---

### Question 14 [Priority: P2] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A Lambda function invoked synchronously via API Gateway writes to a DynamoDB table that intermittently throws `ProvisionedThroughputExceededException` during traffic bursts, causing user-facing request failures. A cost-governance policy prohibits switching the table to on-demand capacity mode. Which two changes will most directly improve resilience to these transient throttling errors?
**Options:**
A. Implement (or rely on the SDK's built-in) exponential backoff with jitter for the DynamoDB calls, so transient throttles are retried instead of immediately failing the user's request.
B. Enable auto scaling on the table's provisioned read/write capacity so throughput ceilings rise automatically during bursts, while remaining in provisioned mode.
C. Increase the Lambda function's memory allocation to reduce execution duration.
D. Set the function's reserved concurrency to a very low fixed number to intentionally limit request volume reaching DynamoDB.
E. Move the Lambda function into a VPC and add a NAT Gateway route toward DynamoDB.
**Correct answer(s):** A, B
**Why correct:** Backoff-with-jitter (A) absorbs short throttling bursts at the call level instead of surfacing them to the user immediately, and DynamoDB auto scaling within provisioned mode (B) raises capacity ceilings ahead of sustained bursts — reducing how often throttling happens at all — while still satisfying the cost-governance requirement to stay in provisioned capacity mode.
**Why each wrong option is wrong:** C speeds up CPU-bound execution but has no effect on DynamoDB's own throughput limits or throttling behavior; D reduces load on DynamoDB only by rejecting legitimate user requests outright at the Lambda layer, which makes the user-facing failure problem worse, not better; E is irrelevant because DynamoDB is reachable over its standard public AWS API endpoint (or a Gateway VPC endpoint) — moving the function into a VPC with a NAT Gateway addresses network path/connectivity concerns that don't exist here and has no bearing on throttling.
**Trigger words:** "ProvisionedThroughputExceededException," "cost-governance policy prohibits switching... to on-demand," "most directly improve resilience."
**Underlying architectural principle:** Resilience to a downstream service's transient capacity limits comes from combining client-side retry/backoff with proactively scaling the downstream capacity itself, not from throttling your own front door or optimizing unrelated resources.

---

### Question 15 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company must roll out a new AMI to all 20 instances in a production Auto Scaling group behind an ALB. The rollout must never drop available capacity below 90%, must not require manually replacing instances one at a time, and must automatically roll back if the new instances start failing health checks.
**Options:**
A. Start an Auto Scaling group Instance Refresh, specifying a minimum healthy percentage of 90% and the new launch template version, letting the ASG use existing ALB health checks to detect failures and drive rollback.
B. Manually terminate instances one at a time so the ASG replaces each with an instance using the updated launch template's default version.
C. Create a second Auto Scaling group using the new AMI and manually shift Route 53 weighted routing once it's verified healthy.
D. Update the launch template to reference the new AMI and take no further action, since the ASG will eventually replace running instances on its own.
**Correct answer(s):** A
**Why correct:** Instance Refresh natively performs a rolling replacement of every instance in the ASG according to a specified minimum healthy percentage, and it automatically monitors health checks during the rollout, rolling back if instances fail — meeting every stated constraint without manual orchestration.
**Why each wrong option is wrong:** B is explicitly excluded by "must not require manually replacing instances one at a time," and it provides no automatic rollback if the new AMI turns out to be unhealthy; C is a valid blue/green pattern in general, but as described it depends on a human manually verifying the new ASG's health before shifting Route 53 weights — it doesn't automatically roll back based on health check failures the way the requirement demands, and it also doubles running infrastructure temporarily, adding operational overhead that Instance Refresh avoids natively; D is wrong because updating the launch template only affects instances launched in the future — it does not trigger any replacement of the 20 instances already running.
**Trigger words:** "roll out a new AMI to all 20 instances," "never drop available capacity below 90%," "must not require manually replacing instances," "automatically roll back."
**Underlying architectural principle:** ASG Instance Refresh with a minimum healthy percentage natively performs a rolling, capacity-aware rollout of a new launch template version with automatic health-check-driven rollback.

---

### Question 16 [Priority: P3] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A high-frequency trading firm maintains an Aurora Global Database secondary in a DR region with sub-1-minute replication lag. It also keeps a fleet of fully pre-configured EC2 instances for its trading application in a **stopped** (not terminated) state in that same DR region, so they can be started rather than launched fresh from an AMI during failover, meaningfully cutting boot time. Under normal conditions, none of these stopped instances are attached to a load balancer, none receive health checks, and no traffic is served from the DR region. The stated RTO target is under 10 minutes.
**Options:**
A. Pilot Light — the compute tier is not running or serving traffic under normal conditions; pre-configuring instances in a stopped state is simply an optimization to reduce the time needed to "ignite" the fleet, and it does not change the classification.
B. Warm Standby — because the instances already exist and are pre-provisioned in the DR region, the compute tier counts as "running" for classification purposes.
C. Backup and Restore — because the compute tier requires an explicit start action before it can be used.
D. Multi-Site Active-Active — because Aurora Global Database is technically capable of serving reads from the secondary region at any time.
**Correct answer(s):** A
**Why correct:** The classification test for Pilot Light versus Warm Standby is whether compute is actively running and capable of serving traffic, not merely whether it has been provisioned — a stopped EC2 instance consumes no compute cycles, serves no traffic, and receives no health checks, so this remains Pilot Light, just an optimized variant with a faster "ignition" step than building instances from scratch.
**Why each wrong option is wrong:** B conflates "pre-provisioned" with "running" — a stopped instance is not functioning or serving anything, so it does not meet Warm Standby's requirement of a live (even if downsized) application tier; C is wrong because Backup and Restore typically has no pre-existing configured instances at all (just backups) and a much slower typical RTO measured in hours, while this design has continuous DB replication and a sub-10-minute RTO, well beyond what plain Backup and Restore provides; D is wrong because the mere technical capability of Aurora Global Database to serve reads doesn't make this active-active — no traffic is actually being served from the DR region under normal conditions, which is the defining trait of Multi-Site Active-Active.
**Trigger words:** "kept in a stopped (not terminated) state," "started rather than launched fresh from an AMI," "no traffic is served from the DR region under normal conditions," "none... attached to a load balancer, none receive health checks."
**Underlying architectural principle:** DR strategy classification depends on whether compute is actively running and serving production traffic, not merely whether it has been pre-provisioned — pre-staging stopped resources is a valid Pilot Light optimization, not a promotion to Warm Standby.

---

### Question 17 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A Lambda function processes messages from an SQS queue and calls an internal microservice on EC2 inside a private VPC subnet, so the function itself is VPC-attached to reach that private endpoint. A recent deployment introduced a bug that causes every message currently in the queue to fail deterministically ("poison pill" messages). Because the SQS visibility timeout keeps returning failed messages to the queue for retry, the function is now continuously reprocessing the same failing messages at high concurrency, consuming most of the account's regional concurrency limit and starving other, unrelated Lambda functions of execution capacity.
**Options:**
A. Configure reserved concurrency on this specific function to cap its maximum concurrent executions, and configure a redrive policy (`maxReceiveCount`) on the source SQS queue pointing to a dead-letter queue so poison-pill messages stop being retried indefinitely.
B. Remove the function from the VPC so it can scale without ENI-related limits.
C. Increase the SQS visibility timeout to 12 hours to slow down the retry rate.
D. Increase the function's memory allocation so it processes messages faster and clears the backlog sooner.
**Correct answer(s):** A
**Why correct:** Reserved concurrency caps how much of the shared account-level concurrency pool this one misbehaving function can consume, protecting other functions, while a `maxReceiveCount`-based redrive policy to a DLQ is what actually stops a deterministically failing message from being retried forever — together they isolate the blast radius and resolve the poison-pill problem.
**Why each wrong option is wrong:** B is wrong because modern Lambda VPC networking (Hyperplane ENIs) doesn't impose the old per-invoke ENI throttle that would explain this behavior, and the function needs the VPC to reach the internal microservice — removing it would break required connectivity without addressing the actual concurrency-starvation or poison-pill issue; C slows how often each individual message becomes visible again for retry, but it does nothing to stop those same deterministically-failing messages from eventually being redelivered and consumed indefinitely, nor does it protect other functions' concurrency; D is wrong because the messages fail deterministically regardless of processing speed, so faster execution just retries the same failure faster and doesn't address the missing redrive policy or the account-wide concurrency starvation.
**Trigger words:** "fails deterministically," "poison pill," "continuously reprocessing the same failing messages," "starving other, unrelated Lambda functions of execution capacity."
**Underlying architectural principle:** Reserved concurrency isolates one misbehaving function's blast radius from the shared account concurrency pool, while a dead-letter/redrive policy on the source queue is what actually stops a poison-pill message from being retried forever.
