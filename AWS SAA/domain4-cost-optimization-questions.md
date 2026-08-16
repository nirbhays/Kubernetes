# SAA-C03 Domain 4 Practice Questions — Design Cost-Optimized Architectures (20% weight)

Original practice content written for self-study. These are **not** real AWS exam questions and do not reproduce any leaked/dumped exam content — they are built from the official SAA-C03 exam guide scope and current (2026) documented AWS service behavior.

Focus areas: EC2 purchasing options cost trade-offs, Auto Scaling for cost efficiency, Lambda vs EC2/Fargate cost reasoning, right-sizing decisions.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs its core order database on a single EC2 instance family, in a single Region, and finance has confirmed the workload will run continuously, 24/7, for at least the next three years with no planned changes to instance family or Region. The workload cannot tolerate interruption. Finance wants the maximum possible percentage discount off On-Demand pricing and is willing to pay the full amount upfront to get it.
**Options:**
A. Keep the instance on On-Demand pricing to preserve flexibility.
B. Purchase a 3-year Standard Reserved Instance with the All Upfront payment option.
C. Move the workload to Spot Instances to reduce cost immediately.
D. Purchase a Dedicated Host for the instance.
**Correct answer(s):** B
**Why correct:** A known, unchanging, 3-year, non-interruptible workload is exactly the steady-state case Reserved Instances are priced for, and the All Upfront payment option yields the largest discount off On-Demand of any RI payment option.
**Why each wrong option is wrong:** A. On-Demand carries no commitment discount and is the most expensive option for a workload with zero uncertainty about duration or configuration. C. Spot Instances can be reclaimed with a two-minute warning, which directly violates the "cannot tolerate interruption" constraint. D. A Dedicated Host addresses physical hardware isolation/licensing needs, not cost minimization, and costs more than a Standard RI for this workload.
**Trigger words:** "continuously, 24/7," "at least the next three years," "no planned changes," "cannot tolerate interruption," "maximum possible percentage discount," "willing to pay the full amount upfront."
**Underlying architectural principle:** Match the EC2 purchasing model to how certain and how long-lived the demand is — steady, known, long-term demand should always be committed, not paid for at On-Demand rates.

---

### Question 2 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A media company runs a fleet of EC2 instances that decode and transcode uploaded video files pulled from an SQS queue. Each job can be checkpointed and safely restarted from the last checkpoint on any instance if interrupted, and jobs can start and finish at any time without a fixed deadline. The company wants the lowest possible compute cost for this fleet and has no need for guaranteed capacity availability.
**Options:**
A. Reserved Instances with a 3-year term.
B. On-Demand Instances only.
C. Spot Instances, ideally across multiple instance types and Availability Zones.
D. Dedicated Instances.
**Correct answer(s):** C
**Why correct:** The workload is explicitly fault-tolerant, checkpointed, restartable, and has no fixed deadline or capacity guarantee requirement — exactly the profile Spot Instances are designed for, offering up to ~90% savings versus On-Demand.
**Why each wrong option is wrong:** A. A 3-year Reserved Instance commitment is unnecessary and inflexible for a workload the company describes with no stated long-term steady-state need. B. On-Demand pays full price for capacity that the workload doesn't actually require guaranteed, uninterrupted access to. D. Dedicated Instances solve hardware-isolation compliance needs, not cost, and cost more than On-Demand, let alone Spot.
**Trigger words:** "checkpointed and safely restarted," "start and finish at any time without a fixed deadline," "lowest possible compute cost," "no need for guaranteed capacity."
**Underlying architectural principle:** Interruptibility is the resource you sell for the deepest EC2 discount — only trade it away for jobs truly designed to tolerate being killed and restarted.

---

### Question 3 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company is lifting-and-shifting a legacy Windows Server application whose commercial database license is billed per physical CPU socket and per physical core (bring-your-own-license). The software vendor's license terms require the customer to know and control exactly which physical server sockets/cores the software runs on, and to be able to pin the workload to the same physical host across restarts.
**Options:**
A. Dedicated Instances.
B. Dedicated Hosts.
C. Standard Reserved Instances.
D. On-Demand Instances with a placement group.
**Correct answer(s):** B
**Why correct:** Dedicated Hosts give visibility into and control over the physical server's sockets and cores and support host affinity, which is exactly what per-socket/per-core BYOL licensing requires — Dedicated Instances do not expose this host-level information.
**Why each wrong option is wrong:** A. Dedicated Instances run on single-tenant hardware but give no visibility or control over host ID, sockets, or cores, so they cannot satisfy per-socket/per-core license compliance. C. Reserved Instances are a billing/commitment model layered on top of a tenancy choice, not a tenancy or licensing solution by themselves. D. Placement groups control network/physical proximity for performance, not license-relevant host visibility or control.
**Trigger words:** "billed per physical CPU socket and per physical core," "know and control exactly which physical server," "pin the workload to the same physical host."
**Underlying architectural principle:** When the requirement is licensing tied to physical hardware attributes, only Dedicated Hosts expose the host-level visibility and control that BYOL socket/core licensing demands.

---

### Question 4 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A growing SaaS company runs EC2 workloads across several instance families in two Regions, and the mix of instance families in use changes every few months as engineering adopts newer instance generations. The company also runs a meaningful and growing amount of AWS Fargate and AWS Lambda usage. Finance wants a single, three-year committed-use discount plan that automatically applies to all of this usage without requiring any manual exchange or modification transactions when the instance mix changes.
**Options:**
A. EC2 Instance Savings Plans, one per instance family in use today.
B. Compute Savings Plans.
C. Convertible Reserved Instances, exchanged quarterly to match the current instance mix.
D. Standard Reserved Instances purchased per Region and instance family.
**Correct answer(s):** B
**Why correct:** Compute Savings Plans automatically apply their discount to EC2 usage regardless of instance family, size, OS, tenancy, or Region, and also apply to Fargate and Lambda usage, with no manual exchange step ever required — the only option matching every stated requirement.
**Why each wrong option is wrong:** A. EC2 Instance Savings Plans are locked to a specific instance family within a Region, so they would need to be repurchased whenever the family mix shifts, and they don't cover Fargate/Lambda. C. Convertible RIs can be exchanged for a different configuration, but that exchange is a manual transaction the company explicitly wants to avoid, and RIs never cover Fargate or Lambda usage. D. Standard RIs are the least flexible option and, like the others, do not extend to Fargate or Lambda.
**Trigger words:** "mix of instance families... changes every few months," "Fargate and AWS Lambda usage," "single... plan that automatically applies," "without requiring any manual exchange."
**Underlying architectural principle:** Flexibility across instance family, Region, and compute type (including serverless) is the defining strength of Compute Savings Plans versus every RI variant.

---

### Question 5 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retailer is launching a major new product in a single Availability Zone-pinned application stack and must guarantee that a specific quantity of a specific EC2 instance type will physically be available to launch in that exact AZ on launch day, regardless of what other AWS customers are doing in that AZ at the time. The company also wants a billing discount on this capacity since it will run for at least a year afterward.
**Options:**
A. A Regional Reserved Instance.
B. A Compute Savings Plan sized to the expected usage.
C. A Zonal (AZ-scoped) Reserved Instance.
D. An EC2 Instance Savings Plan scoped to the Region.
**Correct answer(s):** C
**Why correct:** Only a Zonal Reserved Instance, scoped to a specific Availability Zone, provides an actual capacity reservation guaranteeing that capacity will be available in that AZ — every other option here provides a billing discount only, with no capacity guarantee.
**Why each wrong option is wrong:** A. A Regional RI provides billing flexibility across AZs in the Region but explicitly does not reserve physical capacity in any specific AZ. B. Savings Plans, of any type, never provide a capacity reservation — they are a pure pricing/billing construct. D. An EC2 Instance Savings Plan, like all Savings Plans, provides no capacity guarantee regardless of scope.
**Trigger words:** "guarantee that a specific quantity... will physically be available," "in that exact AZ," "regardless of what other AWS customers are doing."
**Underlying architectural principle:** Capacity reservation and billing discount are separate concerns — only an AZ-scoped (zonal) Reserved Instance combines both; Savings Plans and Regional RIs are discount-only.

---

### Question 6 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A logistics company runs a nightly ETL batch job on an Auto Scaling group. The job always starts at 22:00 and finishes by 02:00, seven days a week, with virtually identical resource needs each night. Outside that window the ASG should run at a minimal baseline to save cost. The company wants capacity to be ready at exactly 22:00 without waiting for a CloudWatch metric to cross a threshold first.
**Options:**
A. A target tracking scaling policy on average CPU utilization.
B. Predictive scaling based on historical load forecasting.
C. Scheduled scaling actions that raise desired capacity just before 22:00 and lower it just after 02:00.
D. A step scaling policy triggered by SQS queue depth.
**Correct answer(s):** C
**Why correct:** Scheduled scaling lets the ASG proactively change desired/min/max capacity at a specific, known clock time — exactly matching a fixed, unvarying daily window — with zero dependency on a metric first breaching a threshold.
**Why each wrong option is wrong:** A. Target tracking only reacts once utilization changes, meaning instances would still be booting after the job's demand had already arrived, causing the exact lag the company wants to avoid. B. Predictive scaling is built for variable, ML-forecasted demand patterns; it adds unnecessary complexity for a fixed, identical daily schedule that scheduled scaling already handles precisely. D. Queue-depth-based step scaling is still reactive to a metric crossing a threshold, not proactive on a clock schedule.
**Trigger words:** "always starts at 22:00... finishes by 02:00," "virtually identical... each night," "ready at exactly 22:00 without waiting for a... metric."
**Underlying architectural principle:** When demand timing is fixed and known in advance, scheduled scaling is the cost-efficient, proactive answer — reserve metric-driven policies for demand that isn't clock-predictable.

---

### Question 7 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An online ticketing platform sees a sharp, repeating traffic surge every Monday between 08:45 and 09:30 as weekly releases go on sale, ramping from baseline to 8x baseline over about 20 minutes. New instances in the Auto Scaling group take roughly 5 minutes to become healthy. Using only target tracking, the ASG's reactive scale-out consistently lags the ramp, causing a few minutes of degraded response times every Monday. The company has over a year of CloudWatch metrics showing this exact recurring weekly pattern and wants the ASG to have extra capacity already warmed before the ramp begins each week, without hand-maintaining a fixed calendar of scaling times.
**Options:**
A. Increase the target tracking policy's target CPU value so the ASG scales out earlier.
B. Add a scheduled scaling action for every Monday at 08:40 indefinitely.
C. Enable predictive scaling on the Auto Scaling group in addition to the existing target tracking policy.
D. Switch entirely from target tracking to simple/step scaling with a shorter cooldown.
**Correct answer(s):** C
**Why correct:** Predictive scaling uses machine learning on historical CloudWatch metrics to forecast a recurring load pattern like this weekly surge and proactively scales out ahead of the forecast, layering on top of target tracking's ongoing reactive fine-tuning — directly matching "over a year of data showing this exact recurring pattern" without manual calendar maintenance.
**Why each wrong option is wrong:** A. Lowering the target threshold makes the policy trigger sooner but is still purely reactive to current metrics, not the underlying root cause of boot-time lag against a known ramp shape. B. A manually maintained weekly scheduled action works but requires ongoing manual upkeep (e.g., adjusting if the pattern shifts), which the company explicitly wants to avoid by asking for a forecast-driven approach. D. Simple/step scaling is still purely reactive to a metric breach and does not pre-provision capacity ahead of a predictable ramp.
**Trigger words:** "over a year of CloudWatch metrics showing this exact recurring weekly pattern," "already warmed before the ramp begins," "without hand-maintaining a fixed calendar."
**Underlying architectural principle:** Predictive scaling is the purpose-built answer whenever a recurring, forecastable demand pattern exists in historical data and manual schedule maintenance is explicitly unwanted — it complements, rather than replaces, reactive dynamic scaling.

---

### Question 8 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A startup is building a stateless REST API used by an internal tool. Usage is extremely uneven: some days it receives zero requests for 10+ hours at a stretch, and other days it receives a short burst of a few hundred requests per second for only a few minutes. Each request completes in well under a second and requires no persistent local state. The CTO wants to pay only for actual compute time consumed and have zero infrastructure cost during idle periods.
**Options:**
A. An ECS service on Fargate with a minimum running task count of 1, scaled by request count.
B. AWS Lambda functions behind Amazon API Gateway.
C. An Auto Scaling group of t3.micro On-Demand EC2 instances with a minimum of 1 instance.
D. An ECS service on EC2 with a single always-on instance and Auto Scaling for bursts.
**Correct answer(s):** B
**Why correct:** Lambda bills per invocation and per-millisecond of execution with no charge at all during idle time, which precisely matches "zero infrastructure cost during idle periods" for a stateless, sub-second, highly uneven-traffic workload.
**Why each wrong option is wrong:** A. A Fargate service with a minimum task count of 1 incurs continuous cost for that always-running task even during the hours of zero traffic, violating the zero-idle-cost requirement. C. An Auto Scaling group with a minimum of 1 instance keeps at least one EC2 instance running (and billed) continuously regardless of traffic. D. Running ECS on a single always-on EC2 instance has the same continuous idle-cost problem as options A and C, plus added patching/scaling overhead for the underlying host.
**Trigger words:** "zero requests for 10+ hours," "burst... for only a few minutes," "well under a second," "pay only for actual compute time consumed," "zero infrastructure cost during idle periods."
**Underlying architectural principle:** For spiky, idle-heavy, short-duration workloads, Lambda's true pay-per-invocation billing beats any option (Fargate or EC2) that requires a minimum always-on capacity floor.

---

### Question 9 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media company runs a video-encoding pipeline where each encoding job consistently takes about 35 minutes of continuous CPU-bound processing, and the pipeline runs jobs back-to-back nearly 24/7, processing hundreds of videos a day for the foreseeable future (well over a year). The workload can tolerate a job being interrupted and restarted from a checkpoint. The company wants the architecture with the lowest sustained cost per hour of compute.
**Options:**
A. AWS Lambda, using the maximum available memory/vCPU allocation to shorten each job's duration.
B. AWS Step Functions orchestrating short Lambda functions that each process a few minutes of the job and hand off state to the next function.
C. EC2 Spot Instances (with On-Demand or Reserved fallback for baseline reliability) committed via a Savings Plan for the steady-state portion.
D. Amazon API Gateway with Lambda integration and a 29-second timeout override.
**Correct answer(s):** C
**Why correct:** A single job's continuous 35-minute runtime already exceeds Lambda's hard 15-minute maximum execution timeout, ruling out any direct Lambda approach, and for sustained, near-24/7, long-running, interruption-tolerant compute over a year-plus horizon, EC2 (Spot for the fault-tolerant bulk, committed via Savings Plans for the steady baseline) is cheaper per hour than any serverless per-invocation billing model at this volume.
**Why each wrong option is wrong:** A. A single Lambda invocation is hard-capped at 15 minutes of execution time no matter how much memory/vCPU is allocated; nothing in the scenario indicates that more vCPU would cut this specific job's runtime by more than half (from 35 minutes to under 15), so betting on that unproven, unstated assumption is far riskier than an architecture with no execution-time ceiling at all. B. Splitting the job across chained Lambda functions is technically possible but adds significant orchestration complexity and still costs more than committed EC2/Spot compute at this sustained, high-volume, long-duration workload profile. D. API Gateway's request timeout is unrelated to background batch processing and, like A, is bounded by Lambda's execution limits.
**Trigger words:** "35 minutes of continuous... processing," "nearly 24/7," "hundreds of videos a day... well over a year," "can tolerate a job being interrupted," "lowest sustained cost per hour."
**Underlying architectural principle:** Lambda's 15-minute execution ceiling and per-invocation pricing make it unsuitable and non-cost-competitive for sustained, long-running, high-volume compute — that workload profile crosses over to EC2/Fargate with commitment-based and Spot discounts.

---

### Question 10 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A finance team flags that EC2 spend has grown 40% year over year. Investigation using CloudWatch shows the majority of the company's m5.2xlarge fleet averages 8% CPU utilization and under 15% memory utilization. Someone on the platform team proposes immediately locking in a 3-year All Upfront Reserved Instance commitment across the entire fleet at its current instance sizes to capture savings as fast as possible.
**Options:**
A. Proceed with the 3-year All Upfront RI purchase immediately at current instance sizes, since RIs always reduce cost regardless of utilization.
B. Use AWS Compute Optimizer (or Cost Explorer's rightsizing recommendations) to identify smaller, better-fitting instance types first, then purchase Reserved Instances or Savings Plans sized to the right-sized fleet.
C. Switch the entire fleet to Spot Instances instead of pursuing any Reserved Instance strategy.
D. Increase all instances to m5.4xlarge to reduce the total instance count needed.
**Correct answer(s):** B
**Why correct:** Committing a 3-year Reserved Instance purchase to oversized instances would lock in the waste for the full term; right-sizing first (using utilization-based recommendations) reduces the baseline need, and only then should a multi-year commitment be purchased against that smaller, accurate baseline.
**Why each wrong option is wrong:** A. Buying RIs at current oversized capacity discounts a price that's still fundamentally wasteful — it locks in 3 years of paying for CPU/memory the application doesn't use. C. Moving everything to Spot ignores the underlying utilization problem entirely and reintroduces interruption risk for a workload whose interruption tolerance was never established. D. Increasing instance size further would only worsen the already-low utilization percentages and increase cost.
**Trigger words:** "EC2 spend has grown 40%," "averages 8% CPU utilization," "immediately locking in a 3-year... commitment... to capture savings as fast as possible."
**Underlying architectural principle:** Right-size based on actual utilization data before making any multi-year commitment purchase — committing to waste only makes the waste more expensive and harder to unwind.

---

### Question 11 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A company with 500+ EC2 instances across several accounts wants to reduce compute waste organization-wide before committing to any multi-year purchase. Leadership wants this done using AWS-native tooling with minimal custom scripting, and wants recommendations that are based on actual observed utilization data rather than guesswork or blanket policy changes. Select the two actions that best satisfy these requirements.
**Options:**
A. Use AWS Compute Optimizer to generate rightsizing recommendations for EC2, Auto Scaling groups, EBS, and Lambda based on CloudWatch utilization history.
B. Immediately purchase 3-year Standard Reserved Instances for every instance at its current size to lock in savings right away.
C. Review AWS Cost Explorer's rightsizing recommendations to identify EC2 instances that are strong candidates for downsizing or family changes.
D. Convert the entire fleet to Spot Instances as a blanket policy across all workloads.
E. Manually inspect CloudWatch dashboards for each of the 500+ instances one at a time to eyeball utilization trends.
**Correct answer(s):** A, C
**Why correct:** Compute Optimizer and Cost Explorer's rightsizing recommendations are both AWS-native, ML/data-driven tools purpose-built to surface instance-level rightsizing opportunities from real utilization metrics at scale, satisfying "minimal custom scripting" and "actual observed utilization data."
**Why each wrong option is wrong:** B. Committing to 3-year RIs before rightsizing locks in whatever waste currently exists in the fleet for the full term. D. Blanket-converting every workload to Spot ignores interruption tolerance entirely and isn't a rightsizing action. E. Manually reviewing 500+ dashboards one at a time is exactly the non-scalable, custom/manual effort the company wants to avoid.
**Trigger words:** "reduce compute waste... before committing to any multi-year purchase," "AWS-native tooling with minimal custom scripting," "based on actual observed utilization data."
**Underlying architectural principle:** AWS provides two complementary, utilization-data-driven, native rightsizing tools (Compute Optimizer and Cost Explorer recommendations) that should be exhausted before any RI/Savings Plan commitment or blanket tenancy/pricing-model change is made.

---

### Question 12 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company currently runs its fleet on m5 (Intel) instances and has firmly scheduled a migration to Graviton-based m7g instances in about 9 months to cut compute cost further. Finance wants to lock in a 3-year committed-use discount today, covering both the current m5 fleet and the post-migration m7g fleet, without requiring any manual "exchange" transaction when the migration happens, and with the discount also applying to a modest amount of Fargate usage the team runs alongside it.
**Options:**
A. A 3-year Standard Reserved Instance scoped to the m5 family today, to be repurchased after the migration.
B. A 3-year Convertible Reserved Instance, exchanged for m7g RIs once the migration completes.
C. A 3-year Compute Savings Plan.
D. A 3-year EC2 Instance Savings Plan scoped to the m5 family.
**Correct answer(s):** C
**Why correct:** A Compute Savings Plan's discount applies automatically to EC2 usage regardless of instance family (m5 today, m7g after migration) and also covers Fargate usage, with no manual conversion step ever required — the only option meeting every stated condition simultaneously.
**Why each wrong option is wrong:** A. A Standard RI is locked to the m5 family; after migrating to m7g it would go unused, forcing a fresh purchase and wasting the remaining committed term. B. A Convertible RI can eventually cover m7g, but only via a manual exchange transaction the company explicitly wants to avoid, and RIs of any kind never cover Fargate usage. D. An EC2 Instance Savings Plan is locked to one instance family within a Region, so it has the identical family-lock problem as option A and still excludes Fargate.
**Trigger words:** "migration to Graviton-based m7g... in about 9 months," "covering both... without requiring any manual exchange transaction," "also applying to... Fargate usage."
**Underlying architectural principle:** When a future instance-family change is already planned and Fargate/Lambda coverage matters, Compute Savings Plans' automatic, no-exchange flexibility beats every RI variant, even Convertible RIs.

---

### Question 13 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A company runs a large fleet of stateless web-scraping workers on EC2 Spot Instances managed by an Auto Scaling group with a mixed instances policy. The group is currently configured to use only two instance types in a single Availability Zone and uses the "lowest price" Spot allocation strategy. Over the past month, interruption rates have climbed sharply, and the resulting job restarts have started to erode the cost savings versus On-Demand, even though the advertised per-hour Spot price for the chosen instance types remains low. Select the two changes that would reduce the interruption rate while still preserving most of the Spot cost savings.
**Options:**
A. Expand the mixed instances policy to include many more instance types and sizes, and spread the group across all Availability Zones in the Region.
B. Switch the Spot allocation strategy from "lowest price" to "capacity-optimized" (or "price-capacity-optimized").
C. Reduce the number of Availability Zones used to concentrate demand into a single, deep capacity pool.
D. Raise the ASG's maximum Spot price bid far above the current On-Demand price to guarantee the instances are never reclaimed.
E. Replace the Spot fleet with Dedicated Hosts to guarantee physical capacity.
**Correct answer(s):** A, B
**Why correct:** Diversifying across many instance types/sizes and AZs (A) gives the Spot allocation logic many capacity pools to draw from instead of contending for the same narrow pool, and the "capacity-optimized" strategy (B) specifically chooses instances from pools with the most available spare capacity to minimize interruption risk — both directly address interruption rate while keeping Spot pricing.
**Why each wrong option is wrong:** C. Concentrating into fewer AZs/pools does the opposite of diversification and would likely increase interruption frequency, not reduce it. D. Modern Spot pricing already caps at the On-Demand price and doesn't work as a "bid" to avoid reclamation — interruptions are driven by capacity, not price, so this doesn't address the root cause. E. Dedicated Hosts eliminate Spot's cost savings entirely and are a tenancy/licensing solution, not a Spot-interruption mitigation.
**Trigger words:** "only two instance types in a single Availability Zone," "'lowest price' Spot allocation strategy," "interruption rates have climbed sharply," "reduce the interruption rate while still preserving most of the Spot cost savings."
**Underlying architectural principle:** Spot interruption risk is driven by capacity-pool depth and diversity, not by price — diversify instance types/AZs and use a capacity-aware allocation strategy rather than trying to "outbid" reclamation.

---

### Question 14 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company's Lambda function is configured with 512 MB of memory and, on average, takes 4,000 ms to complete because it is CPU-bound (heavy JSON parsing and compression). Profiling shows that raising the memory allocation to 1,769 MB — which proportionally increases the share of vCPU allocated to the function, since Lambda allocates CPU power in proportion to configured memory — drops average duration to about 900 ms, because the function is far less CPU-throttled than it was at 512 MB. The function is invoked 2 million times per month. The team wants to minimize total monthly Lambda compute cost.
**Options:**
A. Keep the function at 512 MB, since higher memory always costs more regardless of duration.
B. Increase the function's memory to 1,769 MB, because the resulting drop in billed duration more than offsets the higher per-millisecond rate.
C. Split the function into two smaller Lambda functions chained together to average out the memory allocation.
D. Enable Provisioned Concurrency at 512 MB to reduce cold starts and lower cost.
**Correct answer(s):** B
**Why correct:** Lambda bills on GB-seconds (memory in GB × billed duration), so for a CPU-bound function, increasing memory (which also increases vCPU) can cut duration by more than the memory increase, producing lower total GB-seconds and lower total cost — a well-documented, counter-intuitive but correct Lambda cost optimization.
**Why each wrong option is wrong:** A. This ignores that cost is driven by GB-seconds, not memory setting alone; here the large duration drop (4,000ms → 900ms) more than compensates for the ~3.5x memory increase, since 512×4000 = 2,048,000 vs 1,769×900 ≈ 1,592,100 memory-milliseconds — a net decrease. C. Splitting into chained functions adds invocation overhead, orchestration cost/complexity, and doesn't address the underlying CPU-throttling cause. D. Provisioned Concurrency addresses cold-start latency (a performance concern) and adds cost — it does not address per-invocation compute duration or reduce cost here.
**Trigger words:** "CPU-bound," "proportionally increases the vCPU," "drops average duration," "minimize total monthly Lambda compute cost."
**Underlying architectural principle:** Lambda cost is a function of memory × duration, not memory alone — for CPU-bound functions, more memory (and thus more vCPU) can lower total cost by cutting duration enough to offset the higher rate.

---

### Question 15 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A healthcare company's compliance policy requires that certain workloads run on physical servers not shared with any other AWS customer, for regulatory audit purposes. There is no software licensing requirement tied to physical socket or core counts, and the company has no need to see or control the host's physical identifiers, or to pin workloads to a specific returning physical host across stop/start cycles. The company wants to satisfy the isolation requirement at the lowest additional cost over On-Demand pricing.
**Options:**
A. Dedicated Hosts.
B. Dedicated Instances.
C. Standard Reserved Instances with a tenancy of "default."
D. A placement group with tenancy set to "shared."
**Correct answer(s):** B
**Why correct:** Dedicated Instances run on hardware dedicated to a single customer, satisfying the "not shared with any other customer" audit requirement, without the extra cost and operational overhead of Dedicated Hosts, which are only necessary when host-level visibility, control, or license-driven host affinity is actually required.
**Why each wrong option is wrong:** A. Dedicated Hosts cost more and add host-level management overhead (visibility into sockets/cores, host affinity) that this scenario explicitly says isn't needed. C. A "default" tenancy Reserved Instance still runs on shared, multi-tenant hardware and does not satisfy a physical-isolation compliance requirement regardless of the RI commitment. D. Placement groups control network proximity/performance, not multi-tenancy isolation, and "shared" tenancy is the opposite of what's required here.
**Trigger words:** "physical servers not shared with any other AWS customer," "no software licensing requirement tied to physical socket or core counts," "no need to see or control the host's physical identifiers," "lowest additional cost."
**Underlying architectural principle:** Choose Dedicated Instances over Dedicated Hosts when single-tenant physical isolation is the requirement but host-level visibility/control or license-driven host affinity is not — Dedicated Hosts are the more expensive, higher-control tier reserved for that extra need.

---

### Question 16 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** Eighteen months into a 3-year, All Upfront Standard Reserved Instance commitment made for a planned data-center-exit migration project, the company cancels the remaining phases of the project. The reserved capacity (in a Region and instance family the company no longer needs) now sits completely unused for the remaining 18 months of the term, and finance wants to recover as much of the sunk cost as possible.
**Options:**
A. List and sell the remaining term of the Standard Reserved Instances on the AWS Reserved Instance Marketplace.
B. Convert the Reserved Instances into a Compute Savings Plan to redirect the discount elsewhere.
C. Request AWS terminate the RI early and issue a partial refund for unused months.
D. Exchange the Standard RIs for Convertible RIs in a different instance family that's still in use, at no cost.
**Correct answer(s):** A
**Why correct:** The AWS Reserved Instance Marketplace exists specifically to let customers sell the remaining term of unused Standard Reserved Instances to other AWS customers, allowing partial recovery of the upfront cost — this option is only available for Standard RIs.
**Why each wrong option is wrong:** B. Reserved Instances cannot be converted into a Savings Plan — the two are entirely separate commercial constructs with no conversion path between them. C. AWS does not refund unused portions of an All Upfront RI commitment upon voluntary cancellation; the commitment is non-refundable outside the RI Marketplace resale path. D. Only Convertible RIs can be exchanged for different configurations — Standard RIs are not eligible for the exchange feature, only for resale on the Marketplace.
**Trigger words:** "3-year, All Upfront Standard Reserved Instance," "cancels the remaining phases," "sits completely unused," "recover as much of the sunk cost as possible."
**Underlying architectural principle:** Standard RIs, unlike Convertible RIs or Savings Plans, can be resold on the Reserved Instance Marketplace — this is the one purchasing-model detail with a genuine secondary-market exit path.

---

### Question 17 [Priority: P0] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An e-commerce company's order-processing tier must run continuously and cannot tolerate interruption; it holds steady at 50 EC2 instances 24/7, and finance has confirmed this baseline will remain unchanged for at least three years. A separate, unrelated nightly fraud-detection analytics tier runs fully fault-tolerant, checkpointed batch jobs and scales unpredictably between 0 and 150 instances each night depending on transaction volume. Select the two purchasing decisions that minimize total cost while respecting each tier's availability requirements.
**Options:**
A. Purchase a 3-year Compute Savings Plan sized to the order-processing tier's confirmed 50-instance steady baseline.
B. Run the order-processing tier's baseline on On-Demand Instances to preserve maximum flexibility.
C. Run the fraud-detection analytics tier on diversified Spot Instances (multiple instance types/AZs, capacity-optimized allocation) sized dynamically to nightly demand.
D. Purchase 3-year Standard Reserved Instances for the fraud-detection tier sized to its peak of 150 instances.
E. Run the fraud-detection tier on Dedicated Hosts to guarantee capacity every night.
**Correct answer(s):** A, C
**Why correct:** The order-processing tier's confirmed, unchanging 3-year steady-state baseline is exactly what a Savings Plan should cover (A), while the fraud-detection tier's fault-tolerant, highly variable nightly demand is exactly what diversified Spot Instances are priced and designed for (C) — matching each tier's purchasing model to its actual demand and interruption-tolerance profile.
**Why each wrong option is wrong:** B. On-Demand for a confirmed, unchanging 3-year steady baseline leaves a large, avoidable discount on the table for no real flexibility benefit, since the requirement is already fixed. D. Sizing a Reserved Instance commitment to the fraud tier's peak (150) would pay for RIs sitting idle most nights when actual demand is far below peak, and RIs provide no benefit for a workload whose whole value proposition is tolerating interruption cheaply via Spot. E. Dedicated Hosts are a tenancy/licensing solution, not a cost-minimization one, and are far more expensive than Spot for a fault-tolerant, bursty batch workload with no stated licensing or physical-isolation need.
**Trigger words:** "must run continuously and cannot tolerate interruption... confirmed... for at least three years," "fully fault-tolerant, checkpointed batch jobs," "scales unpredictably between 0 and 150."
**Underlying architectural principle:** Real-world fleets are almost never single-purchasing-model — the cost-optimal architecture layers a commitment discount (RI/Savings Plan) under the confirmed non-interruptible steady floor and Spot under the fault-tolerant, bursty ceiling.

---

### Question 18 [Priority: P1] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company's normalized EC2 usage never drops below 80 units/hour (a guaranteed trough that holds for 8 months of the year) but averages 115 units/hour overall because of a predictable 4-month seasonal peak that reaches up to 160 units/hour. Finance is deciding how to size the hourly dollar commitment for a 3-year, No Upfront Compute Savings Plan, and understands that any committed amount not consumed in a given hour is billed anyway and does not roll over or carry forward to other hours.
**Options:**
A. Size the Savings Plan commitment to the 115 units/hour average usage, since that best reflects typical demand.
B. Size the Savings Plan commitment to the 160 units/hour seasonal peak, to maximize the discount captured.
C. Size the Savings Plan commitment to the 80 units/hour guaranteed trough, and cover all usage above that floor with On-Demand (or Spot, where workload characteristics allow) pricing.
D. Purchase a 3-year Standard Reserved Instance sized to the 115 units/hour average instead, since RIs don't have this hourly commitment mechanic.
**Correct answer(s):** C
**Why correct:** Because unused Savings Plan commitment in any given hour is billed but not refunded or carried forward, sizing the commitment to the one number that is guaranteed to be consumed every single hour of the year — the 80 units/hour trough — avoids ever paying for committed-but-unused capacity, while the variable amount above the trough is covered at On-Demand/Spot rates only when actually needed.
**Why each wrong option is wrong:** A. Sizing to the 115 average guarantees that during every hour of the 8-month trough period (usage at 80, commitment at 115), the company pays for 35 units/hour of commitment it never uses. B. Sizing to the 160 peak is even worse — it guarantees substantial unused, non-refundable commitment during the 8-month trough and even during much of the 4-month peak period itself. D. Standard RIs have the same "pay for it whether you use it or not" commitment mechanic as Savings Plans (a reserved instance-hour not used is still paid for) — the RI/Savings Plan choice is orthogonal to this sizing problem, and it doesn't avoid the fundamental oversizing error.
**Trigger words:** "never drops below 80 units/hour... guaranteed trough," "any committed amount not consumed in a given hour is billed anyway and does not roll over."
**Underlying architectural principle:** Size any hourly commitment-based discount (RI or Savings Plan) to the workload's guaranteed floor, not its average or peak, and let elastic, uncommitted pricing absorb everything above that floor.

---

### Question 19 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company is about to purchase a large 3-year Compute Savings Plan sized to its EC2 fleet's current hourly spend. Separately, and unrelated to the Savings Plan decision, a re-platforming project scheduled to complete in about 6 months will migrate 40% of the fleet to smaller, cheaper Graviton-based instance types, which is projected to reduce the fleet's total hourly EC2 spend by roughly 25% once complete — with total instance count and workload demand otherwise unchanged. The team debates whether the re-platforming timeline should affect how the Savings Plan purchase is sized today.
**Options:**
A. It doesn't matter — Compute Savings Plans apply regardless of instance family or size, so sizing to current spend is safe no matter what happens during the re-platforming.
B. Size the Savings Plan's hourly commitment to the fleet's projected post-re-platforming hourly spend (about 25% lower), not its current pre-migration spend.
C. Size the Savings Plan to current spend, then plan to exchange it for a smaller Savings Plan once the migration completes.
D. Delay the Savings Plan purchase decision by a full year to be extra safe, forgoing any discount in the meantime.
**Correct answer(s):** B
**Why correct:** A Compute Savings Plan commitment is a fixed hourly dollar amount, not a fixed number of instances or instance-hours — while it's flexible about which instance family/size satisfies it, it does not adjust itself if the fleet's total hourly dollar spend genuinely drops; sizing to current (pre-migration) spend would leave the company overcommitted and paying for unused commitment for the remaining ~2.5 years after the migration completes.
**Why each wrong option is wrong:** A. This confuses Savings Plans' flexibility across instance family/size/OS (true) with immunity from the fleet's total hourly-dollar-spend changing (false) — the commitment is a dollar figure, and a 25% drop in hourly spend after migration would exceed the flexibility can absorb. C. Savings Plans, unlike Convertible RIs, have no exchange mechanism at all — a Savings Plan commitment cannot be resized or exchanged mid-term. D. Delaying a full year unnecessarily forgoes ~6 months of achievable discount on the pre-migration baseline that could have been captured by simply sizing correctly today.
**Trigger words:** "3-year Compute Savings Plan sized to... current hourly spend," "reduce the fleet's total hourly EC2 spend by roughly 25%," "whether the re-platforming timeline should affect how the... purchase is sized."
**Underlying architectural principle:** Savings Plan flexibility covers *which* resources satisfy the commitment, not *how much* total hourly spend exists — a known future change in aggregate spend must be reflected in the commitment size, since the commitment itself cannot later be resized or exchanged.

---

### Question 20 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A company runs three workloads: (1) a non-interruptible order-processing application on EC2 holding a steady, confirmed 3-year baseline; (2) a stateless image-resizing function invoked unpredictably — mostly idle, with occasional sub-second bursts during promotions; and (3) a nightly, fully fault-tolerant video-encoding batch where each job runs continuously for about 35 minutes. Select the two statements below that describe correct, cost-optimal decisions for this environment.
**Options:**
A. The video-encoding batch cannot run directly on Lambda at all, because a single 35-minute continuous job exceeds Lambda's 15-minute maximum execution timeout — EC2 or Fargate must handle that tier regardless of relative cost.
B. The image-resizing workload should be moved off Lambda onto EC2 Reserved Instances, since a multi-year commitment discount always beats Lambda's per-invocation pricing at any volume.
C. A 3-year Compute Savings Plan should be purchased sized to the order-processing tier's confirmed steady baseline.
D. The order-processing tier should be moved to Spot Instances, since Spot always yields the greatest overall savings regardless of interruption tolerance.
E. The video-encoding batch should run on continuously-running On-Demand instances sized for peak nightly load and left on 24/7 for operational simplicity.
**Correct answer(s):** A, C
**Why correct:** A is a hard technical constraint (Lambda's 15-minute timeout makes it structurally unusable for a single continuous 35-minute job, independent of cost), and C correctly matches a confirmed, non-interruptible, unchanging 3-year baseline to a committed-use discount — both are unambiguously correct architectural decisions for their respective tiers.
**Why each wrong option is wrong:** B. This is backwards — the image-resizing workload is exactly the idle-heavy, sub-second, unpredictable-burst profile Lambda is cheapest for; forcing it onto always-on Reserved Instances would pay for continuous capacity the mostly-idle workload doesn't need. D. Spot Instances can be reclaimed with a two-minute warning, which is fundamentally incompatible with the order-processing tier's explicit non-interruptible requirement — cost savings can never override a hard availability constraint that a purchasing option can't satisfy. E. Leaving On-Demand instances running 24/7 for a workload that is explicitly nightly-only and fault-tolerant wastes money for roughly two-thirds of the day and ignores that Spot is the appropriate, much cheaper fit for this exact fault-tolerant batch profile.
**Trigger words:** "each job runs continuously for about 35 minutes," "confirmed 3-year baseline," "mostly idle, with occasional sub-second bursts," "non-interruptible," "fully fault-tolerant."
**Underlying architectural principle:** Cost optimization requires matching each workload's own interruption tolerance, duration profile, and demand predictability to the purchasing/compute model built for it — a single "cheapest option" never applies uniformly across a mixed environment.

---

*End of Domain 4 practice set (20 questions). Original study content — not sourced from or reproducing any real/leaked SAA-C03 exam questions.*
