# SAA-C03 Domain 2 Question Bank — Decoupling & Event-Driven Architectures

**Domain:** Design Resilient Architectures (26% exam weight)
**Focus area:** SQS (Standard vs FIFO), SNS, EventBridge, Kinesis Data Streams/Firehose, Step Functions — fan-out, dead-letter queues, ordering guarantees, event routing.

These are **original, practice-only questions** written to reinforce SAA-C03 exam competencies. They are **not** reproductions of any real, leaked, or dumped AWS exam content. All service behavior described reflects AWS functionality as of 2026.

---

### Question 1 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A logistics company ingests GPS location pings from a fleet of roughly 3,000 delivery trucks reporting every few seconds across a region, for a total sustained load in the low tens of thousands of messages per second. Each truck's own location updates must be processed in the exact order they were sent (so a truck's route history never appears to jump backward), but there is no requirement to preserve ordering between different trucks. The platform team wants the simplest, most cost-effective managed queuing solution that satisfies the per-truck ordering requirement without building custom resequencing logic.

**Options:**
A. Create an SQS FIFO queue and use each truck's vehicle ID as the message group ID, with high throughput mode enabled.
B. Create an SQS Standard queue and attach the truck ID as a message attribute so consumers can buffer and resequence messages themselves before processing.
C. Create an SNS standard topic that fans out each location ping to a Lambda function for processing.
D. Create an SQS Standard queue and rely on its at-least-once delivery, since messages are usually delivered in the order sent.

**Correct answer(s):** A

**Why correct:** SQS FIFO queues guarantee strict ordering within a message group, and using the truck ID as the group ID gives independent per-truck ordering while allowing different trucks' messages to be processed in parallel across groups. FIFO high throughput mode removes the need to manually shard across many message groups just to scale, making this the simplest managed fit for the stated throughput.

**Why each wrong option is wrong:** B pushes ordering logic into custom application code (buffering/resequencing), which is exactly the operational burden a managed FIFO queue eliminates. C uses SNS, which provides no ordering guarantee at all on a standard topic. D is incorrect because SQS Standard explicitly documents best-effort, not guaranteed, ordering — occasional out-of-order and duplicate delivery is expected behavior, not an edge case.

**Trigger words:** "exact order they were sent," "no requirement... between different trucks," "without building custom resequencing logic."

**Underlying architectural principle:** When ordering must be guaranteed per independent entity/key but not globally, use FIFO with that key as the message group ID rather than building custom sequencing on top of a best-effort queue.

---

### Question 2 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** An e-commerce platform publishes an "OrderPlaced" event that must be processed independently by three internal systems: Billing, Inventory, and Shipping. The Inventory service undergoes planned maintenance for up to two hours roughly once a month, during which it must not miss any OrderPlaced events, while Billing and Shipping continue processing normally and immediately. The team wants a decoupled design with minimal custom code and no risk of one service's downtime affecting the others.

**Options:**
A. Publish OrderPlaced to an SNS topic with one dedicated SQS queue subscribed per downstream service (Billing, Inventory, Shipping).
B. Publish OrderPlaced to an SNS topic with each service's Lambda function subscribed directly to the topic.
C. Publish OrderPlaced to a single SQS standard queue that all three services poll for messages.
D. Publish OrderPlaced to an EventBridge bus with an Archive enabled, and have each service poll the Archive for new events.

**Correct answer(s):** A

**Why correct:** SNS fan-out to one SQS queue per subscriber gives each downstream service its own durable, independently-paced buffer — if Inventory is down for maintenance, its messages simply queue up in its dedicated SQS queue until it resumes polling, with zero impact on Billing or Shipping.

**Why each wrong option is wrong:** B subscribes Lambda directly to SNS, so during Inventory's two-hour maintenance window there is no durable backlog — SNS's retry for a failing/unavailable Lambda target does not queue messages for hours the way a dedicated SQS queue does. C uses a single shared queue, where each message is delivered to only one of the three competing consumers, so Billing, Inventory, and Shipping would each only see a subset of orders, not all of them. D describes polling an Archive, which is a replay/audit mechanism, not a real-time per-service delivery mechanism, and it is not how services are meant to consume live events.

**Trigger words:** "processed independently," "must not miss any events," "no risk of one service's downtime affecting the others."

**Underlying architectural principle:** True fan-out to independently-durable consumers requires SNS-to-SQS-per-subscriber, not direct push subscriptions or a single shared queue.

---

### Question 3 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A SaaS company ingests "payment.succeeded" and "payment.failed" events from a third-party payment provider's partner event source. "payment.failed" events must route to a fraud-detection Lambda function in a separate AWS account, "payment.succeeded" events must route to a billing Step Functions state machine in yet another account, and all events regardless of type must also be archived for an internal audit team — all based on matching nested JSON fields in the event payload, with minimal custom parsing code and native schema discovery support.

**Options:**
A. Create a custom EventBridge event bus, define content-based rules that match on the event detail fields to route to the appropriate cross-account targets, and use resource-based policies to permit cross-account delegation.
B. Create an SNS topic and use message filter policies on each subscription to route based on the event type, subscribing the fraud Lambda and billing Step Functions state machine directly across accounts.
C. Create an SQS queue and have a single Lambda function poll it, inspect each message body, and directly invoke the appropriate cross-account target from within the function.
D. Create a Kinesis Data Stream and have a Lambda consumer read every record, filter by event type in code, and forward matching records to the correct targets.

**Correct answer(s):** A

**Why correct:** EventBridge is purpose-built for exactly this shape of problem: content-based routing on nested JSON fields, native cross-account targeting via resource policies, built-in schema registry/discovery, and first-class support for partner/SaaS event sources — all without custom parsing code.

**Why each wrong option is wrong:** B is technically possible for simple attribute-based filtering, but SNS lacks EventBridge's schema registry, partner event source integration, and is a weaker fit for the "nested JSON, cross-account, SaaS partner" combination the scenario emphasizes. C requires hand-written routing logic inside a Lambda function, defeating the "minimal custom parsing code" requirement and creating a single point of coupling between all destinations. D misuses Kinesis, a streaming/replay service, for what is fundamentally a routing problem — it adds shard management overhead with no routing, schema, or cross-account benefit over EventBridge.

**Trigger words:** "route... based on... nested JSON fields," "different AWS accounts," "native schema discovery," "minimal custom parsing code."

**Underlying architectural principle:** When routing decisions depend on rich event content across many services or accounts, or involve SaaS/partner sources, EventBridge's rule engine is the purpose-built answer over SNS topic-level filtering or hand-rolled Lambda routing.

---

### Question 4 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An IoT platform ingests clickstream/telemetry events at a sustained peak of roughly 500,000 events per second. Three independent applications must each consume the full event stream at their own pace: a real-time dashboard requiring sub-second delivery latency, a fraud-detection ML pipeline consuming continuously, and a batch analytics job that runs once an hour and reads through the same data. If a bug is discovered in any consumer's logic, the team must be able to reprocess the last 7 days of events from the beginning without asking any upstream system to resend data.

**Options:**
A. Use a Kinesis Data Stream with a 7-day extended retention period, have each application maintain its own independent consumer/checkpoint position, and enable enhanced fan-out for the latency-sensitive dashboard consumer.
B. Fan out events from an SNS topic to three separate SQS standard queues, one per consuming application.
C. Publish events to an EventBridge custom bus with three rules, one targeting each of the three consuming applications.
D. Use Kinesis Data Firehose to deliver events to S3, and have each of the three applications read the delivered files from S3 independently.

**Correct answer(s):** A

**Why correct:** Kinesis Data Streams is designed for exactly this pattern: multiple independent consumer applications reading the same ordered data at their own pace, with configurable retention (up to 365 days) enabling replay of the last 7 days on demand, and enhanced fan-out providing dedicated 2 MB/s throughput per consumer for the latency-sensitive dashboard.

**Why each wrong option is wrong:** B fails the replay requirement — once a message is deleted from an SQS queue after processing, it cannot be replayed 7 days later, and SQS/SNS were never designed for this ordered-replay pattern. C has the same fundamental limitation as B — EventBridge delivers events to targets in near-real time but does not provide a durable, replayable, per-consumer-offset stream at this scale. D misapplies Firehose, which is a one-way delivery service to a destination (S3, in this case) — it does not support multiple independent low-latency stream readers with their own checkpoints, and introduces unacceptable latency for the sub-second dashboard requirement.

**Trigger words:** "each consume the full stream at their own pace," "reprocess the last 7 days," "sub-second delivery latency," "500,000 events per second."

**Underlying architectural principle:** Multiple independent consumers needing replay and their own read offsets over the same ordered dataset is the signature use case for Kinesis Data Streams — not SQS/SNS, which delete messages once consumed, and not Firehose, which only delivers one-way to a destination.

---

### Question 5 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company wants clickstream events to land in an S3-based data lake within 60–90 seconds of being generated, converted from JSON to Parquet along the way, with a lightweight Lambda-based transformation that masks a few PII fields before the data is written. The team explicitly does not want to write or operate any consumer application code, manage shard counts, or run any EC2/container infrastructure for this pipeline.

**Options:**
A. Use Kinesis Data Firehose with a Lambda transformation step and built-in Parquet format conversion, delivering directly to S3.
B. Use a Kinesis Data Stream with a custom KCL-based consumer application running on an EC2 Auto Scaling group that transforms records and writes Parquet files to S3.
C. Use an SQS standard queue with a scheduled batch job that polls the queue every 60 seconds and writes objects to S3.
D. Use an EventBridge rule with an S3 target to deliver events directly, and a nightly Glue job to convert the accumulated JSON files to Parquet.

**Correct answer(s):** A

**Why correct:** Kinesis Data Firehose is the fully managed, no-consumer-code delivery service purpose-built for exactly this pattern: near-real-time buffered delivery to S3, an inline Lambda transformation step, and native record format conversion to Parquet — with no shard management or servers to operate.

**Why each wrong option is wrong:** B reintroduces exactly the operational burden the scenario explicitly rejects — a self-managed consumer application and EC2 Auto Scaling group for shard processing and Parquet conversion. C is not a real-time streaming pattern and provides no native transformation or format-conversion capability; it is a fragile, hand-rolled substitute for a managed delivery service. D delays Parquet conversion to a "nightly" batch step, which does not meet the 60–90 second near-real-time landing requirement, and EventBridge is not designed for high-volume clickstream delivery with inline record transformation.

**Trigger words:** "near-real-time," "Parquet," "does not want to... operate any consumer application code," "no shard... management."

**Underlying architectural principle:** When the requirement is fully-managed near-real-time delivery-with-transformation to a destination and there is no need for multiple independent replayable consumers, Kinesis Data Firehose — not Data Streams — is the lower-operational-overhead answer.

---

### Question 6 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** An order-processing Lambda function consumes messages from an SQS standard queue. Occasionally, an upstream bug produces a malformed JSON message that causes the Lambda function to throw an exception every time it is invoked with that message. Because the message becomes visible again each time its visibility timeout expires, it is retried indefinitely, consuming Lambda invocations without ever succeeding. The team wants malformed messages automatically set aside for manual inspection after 5 failed processing attempts, with no risk of losing the message.

**Options:**
A. Configure a redrive policy on the source queue with a maxReceiveCount of 5, pointing to a dead-letter queue.
B. Increase the queue's visibility timeout to 24 hours so failed messages are retried much less frequently.
C. Add a try/catch block in the Lambda function that deletes the message from the queue whenever processing throws an exception.
D. Reduce the message retention period on the queue to 5 minutes so that malformed messages expire and disappear quickly.

**Correct answer(s):** A

**Why correct:** A redrive policy with maxReceiveCount=5 automatically moves a message to a dead-letter queue after it has been received and has failed processing 5 times, isolating poison-pill messages for manual review while preserving them (rather than losing them) and preventing indefinite reprocessing.

**Why each wrong option is wrong:** B only slows down the retry frequency of a message that will never succeed; it does not stop the indefinite retry loop or isolate the bad message. C silently discards failed messages entirely, which violates the explicit "no risk of losing the message" requirement. D causes messages — including good ones a consumer hasn't yet processed — to be deleted purely due to age, which is an unrelated and destructive mechanism, not a targeted fix for repeatedly-failing messages.

**Trigger words:** "retried indefinitely," "automatically set aside... after 5 failed processing attempts," "no risk of losing the message."

**Underlying architectural principle:** Isolating messages that repeatedly fail processing (poison pills) without losing them is the job of a dead-letter queue with a redrive policy, not visibility timeout tuning or manual delete-on-failure logic.

---

### Question 7 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An IoT platform ingests millions of sensor readings per hour. Each reading triggers a short workflow (validate → enrich → store → notify) that completes in under 10 seconds and includes conditional branching. Downstream steps are idempotent, so at-least-once execution semantics are acceptable, and the team does not need a years-long, per-execution audit trail — but they do need per-execution cost to stay as low as possible at this volume.

**Options:**
A. Use AWS Step Functions Express Workflows to orchestrate the four steps.
B. Use AWS Step Functions Standard Workflows to orchestrate the four steps.
C. Have a single Lambda function synchronously invoke the other three Lambda functions in sequence, one after another.
D. Chain the four Lambda functions using an SQS queue between each pair of functions.

**Correct answer(s):** A

**Why correct:** Step Functions Express Workflows are priced per execution and duration rather than per state transition, are designed for exactly this high-volume, short-duration, at-least-once profile, and still provide the conditional branching and retry semantics the workflow needs — at dramatically lower cost than Standard Workflows at millions of executions per hour.

**Why each wrong option is wrong:** B (Standard Workflows) is priced per state transition and provides exactly-once semantics and long execution history the scenario says isn't needed — at this volume it would cost substantially more for capability that isn't required. C is the classic Lambda-chaining anti-pattern: tight coupling between functions, no built-in retry/branching visualization, and the calling function pays for idle wait time while blocked on downstream responses. D adds unmanaged queues and custom glue code between every step, losing the built-in conditional branching and unified execution view that Step Functions provides natively.

**Trigger words:** "millions... per hour," "under 10 seconds," "at-least-once... acceptable," "cost... minimal at this volume."

**Underlying architectural principle:** High-volume, short-duration, at-least-once orchestration favors Step Functions Express Workflows over Standard Workflows (cost) and over ad hoc Lambda chaining or queue-glued steps (loses native branching/retry and adds coupling).

---

### Question 8 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A bank must fan out "AccountTransaction" events to two independent downstream systems — a ledger service and a fraud-monitoring service. Both systems require strictly ordered, deduplicated (exactly-once) processing of transactions per account number, and each system must be able to durably queue a backlog and catch up at its own pace if it experiences temporary downtime, without any custom checkpoint-management code.

**Options:**
A. Publish to an SNS FIFO topic with two SQS FIFO queues subscribed (one per downstream system), using the account number as the message group ID and content-based deduplication enabled.
B. Publish to an SNS standard topic with two SQS standard queues subscribed, and have each consumer use a sequence number message attribute to manually resequence transactions before processing.
C. Publish to an EventBridge custom bus with two Lambda targets, each performing an idempotency check against a DynamoDB table before processing.
D. Publish to a Kinesis Data Stream using the account number as the partition key, with two separate consumer applications each processing the stream independently.

**Correct answer(s):** A

**Why correct:** SNS FIFO topics fanning out to SQS FIFO queues is the one combination that delivers strict per-account ordering (via message group ID), built-in deduplication, and durable, independently-pollable per-subscriber backlogs — all without custom code, exactly matching every stated requirement.

**Why each wrong option is wrong:** B forces the team to build and maintain custom resequencing logic in every consumer, which the requirement explicitly wants to avoid, and standard SNS/SQS provide no ordering or dedup guarantees to build on. C can achieve correctness but requires hand-built idempotency checks (a DynamoDB table and custom logic) rather than a native guarantee, and EventBridge targets don't provide the same "durably queue a backlog and catch up independently" semantics as a dedicated SQS queue per subscriber. D provides per-shard ordering by partition key, but Kinesis has no native per-message deduplication, and giving two independent applications their own durable, delete-on-completion "queue" semantics (rather than shard iterators/checkpoints they must manage themselves) requires more custom operational work than SNS FIFO → SQS FIFO.

**Trigger words:** "strictly ordered, deduplicated (exactly-once)... per account number," "durably queue a backlog," "without any custom checkpoint-management code."

**Underlying architectural principle:** When a scenario combines fan-out, strict per-key ordering, deduplication, and independent durable per-subscriber backlogs, SNS FIFO topics feeding SQS FIFO queues is a fully native fit — don't default to "SNS can't do ordering" without checking for the FIFO variant.

---

### Question 9 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retailer needs a single "InventoryUpdated" event broadcast to four internal subscribers, all of which need to receive every single update with no content-based filtering or conditional routing required. There is no cross-account or third-party SaaS integration need today. The team wants the cheapest, simplest possible setup for this pure broadcast pattern.

**Options:**
A. Publish to an SNS standard topic with all four systems subscribed.
B. Publish to an EventBridge custom bus with four rules, each matching all events and targeting one of the four systems.
C. Publish to a Kinesis Data Stream with four independent consumer applications, one per system.
D. Publish to a single SQS standard queue, with all four systems' workers polling that same queue.

**Correct answer(s):** A

**Why correct:** SNS is the simplest and cheapest managed service for pure one-to-many broadcast where every subscriber wants every message and no content-based routing is required — a topic with four subscriptions is a minimal, low-cost configuration with no extra routing rules or stream infrastructure to manage.

**Why each wrong option is wrong:** B works technically but adds EventBridge's per-event and rule-matching costs and complexity for a use case that has no actual content-based routing requirement — pure overhead here. C misapplies a streaming/replay service to a simple broadcast need, adding shard management and cost with no offsetting benefit since replay and independent-pace analytics aren't required. D is a competing-consumers pattern: each message is delivered to only one of the four pollers, so the four systems would each only see roughly a quarter of the updates rather than all of them.

**Trigger words:** "broadcast," "all of which need to receive every single update," "no content-based filtering," "cheapest, simplest."

**Underlying architectural principle:** For simple, uniform one-to-many broadcast with no content-based routing complexity, SNS remains the lowest-cost, lowest-overhead choice over EventBridge, Kinesis, or a shared queue.

---

### Question 10 [Priority: P0] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A video transcoding service pulls jobs from an SQS standard queue. Processing time varies unpredictably from 2 minutes to 45 minutes depending on file size, but the queue's visibility timeout is fixed at 5 minutes. The team is seeing large files transcoded multiple times concurrently by different workers, wasting compute and occasionally producing corrupted, double-written output files. The fix must handle jobs of unpredictable, variable duration without capping the maximum processing time or giving up at-least-once delivery.

**Options:**
A. Increase the visibility timeout to comfortably exceed the expected maximum processing time, and have the consumer call the ChangeMessageVisibility API to extend it further if a specific job runs longer than expected.
B. Switch the queue to SQS FIFO, since FIFO queues guarantee exactly-once processing and will eliminate the duplicate-processing behavior regardless of visibility timeout settings.
C. Modify the consumer to delete each message from the queue immediately upon receipt, before transcoding begins, so the message can never be redelivered.
D. Reduce the visibility timeout to 30 seconds so the consumer receives a fresh copy of the message more frequently and can use that to track its own processing progress.

**Correct answer(s):** A

**Why correct:** The root cause is a visibility timeout shorter than actual processing time, causing the message to become visible again — and get picked up by a second worker — before the first worker finishes. Setting the timeout above the realistic maximum and dynamically extending it for outliers via ChangeMessageVisibility directly fixes the mismatch while preserving at-least-once delivery and requiring no cap on job duration.

**Why each wrong option is wrong:** B is a common trap: FIFO's deduplication interval and single-message-group processing lock reduce certain duplicate scenarios, but FIFO does not eliminate redelivery once a message's visibility timeout expires — the same short-timeout-vs-long-processing mismatch can still cause a message to become available again and be picked up by a second worker. C removes the safety net entirely — if the worker or instance crashes mid-transcode, the job is lost forever with no possibility of retry, which is a worse failure mode than duplicate processing. D shortens the timeout further, making the redelivery-during-processing problem dramatically worse, not better.

**Trigger words:** "processing time varies unpredictably," "duplicate... without... losing at-least-once delivery," "without capping the maximum processing time."

**Underlying architectural principle:** Duplicate concurrent processing from a queue is almost always a visibility-timeout-vs-processing-time mismatch; the fix is sizing the timeout correctly and extending it dynamically for outliers, not switching queue types or deleting messages early.

---

### Question 11 [Priority: P0] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A clickstream Kinesis Data Stream is provisioned with 20 shards. Roughly 90% of all traffic originates from a single high-volume customer whose customer ID is used as the partition key. That customer's records consistently trigger ProvisionedThroughputExceededException on whatever shard they land on, while the other 19 shards sit almost idle — even though total account-wide throughput is well under the stream's aggregate provisioned capacity.

**Options:**
A. Redesign the partition key to a higher-cardinality value, such as a composite of customer ID and a random or rotating suffix (or a session/event ID), so the high-volume customer's records are spread across multiple shards rather than hashing to a single one.
B. Increase the shard count from 20 to 50 using UpdateShardCount, while keeping the customer ID as the partition key.
C. Migrate from Kinesis Data Streams to Kinesis Data Firehose to avoid shard-level throttling entirely.
D. Enable enhanced fan-out for the consumer application that processes the high-volume customer's shard.

**Correct answer(s):** A

**Why correct:** The throttling is a hot-key problem, not a capacity problem — a single partition key value always hashes into the same shard's key range. Only changing the key design (adding higher-cardinality entropy) actually spreads that customer's writes across multiple shards and resolves the throttling.

**Why each wrong option is wrong:** B increases the number of shards, but the single customer ID key still deterministically hashes to one (new) shard's range, so the hot-shard throttling persists on whichever shard it lands on — resharding does not fix a hot-key distribution problem. C is a service mismatch: Firehose is a one-way delivery service and does not solve write-side partition-key hot-spotting, nor does it preserve the real-time shard-based processing this stream implies. D increases a consumer's dedicated read throughput/latency but does nothing for the write-side throttling on the shard receiving this customer's records — it addresses the wrong side of the pipeline.

**Trigger words:** "90% of all traffic originates from a single... customer," "consistently... throttled... while the other 19 shards sit almost idle," "well under the stream's aggregate provisioned capacity."

**Underlying architectural principle:** Shard-level throttling despite ample aggregate stream capacity is a partition-key design problem; fix it by increasing key cardinality, not by blindly adding shards or switching services.

---

### Question 12 [Priority: P1] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A media company must process 2 million objects stored in S3 as a nightly batch job, applying a transformation to each object. The workflow needs per-item retry logic, must throttle overall concurrency so as not to exceed a downstream third-party API's hard limit of 300 requests per second, and must produce a single auditable execution with a consolidated success/failure report — all within a 4-hour SLA window.

**Options:**
A. Use a Step Functions Standard Workflow with a Distributed Map state that reads the object listing directly from S3 and processes items with a configured maximum concurrency.
B. Use a Step Functions Standard Workflow with a regular (inline) Map state that iterates over all 2 million items within a single execution.
C. Trigger 2 million individual Lambda invocations via an S3 Batch Operations job, using reserved concurrency on the function to throttle to roughly 300 invocations per second.
D. Use EventBridge to publish 2 million individual events, each starting its own Step Functions Express Workflow execution.

**Correct answer(s):** A

**Why correct:** Distributed Map is purpose-built for exactly this scale — it can read object lists directly from S3, fan out to a very large number of child executions (well beyond the limits of an inline Map state), enforce a configurable maximum concurrency to respect the downstream rate limit, and still produce one parent execution with a consolidated, auditable result and per-item retry.

**Why each wrong option is wrong:** B (a regular, inline Map state) is constrained by much lower practical concurrency and total state/payload size limits, making it unsuitable for iterating 2 million items within a single execution — this is precisely the gap Distributed Map was introduced to close. C provides no built-in orchestration, retry policy, or consolidated reporting, and coordinating a precise global 300 requests/sec ceiling across 2 million independently-invoked Lambda functions is far more fragile and complex than Distributed Map's native concurrency control. D loses the single auditable execution and consolidated report entirely — it creates 2 million separate, disconnected Express executions with no unified view, and still requires custom coordination to enforce the shared 300/sec downstream limit.

**Trigger words:** "2 million objects," "throttle... to a downstream... hard limit," "single auditable execution with a consolidated... report."

**Underlying architectural principle:** Massive-scale, per-item fan-out with centralized concurrency control and a single auditable execution is the specific problem Step Functions Distributed Map solves — an inline Map state, decoupled bulk Lambda invocations, or independently-fired Express executions all lack one or more of those properties.

---

### Question 13 [Priority: P0] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A team is migrating a payment-reconciliation service from an SQS standard queue to an SQS FIFO queue. Before the change is approved, they must correctly explain to a security review board exactly two true characteristics of SQS FIFO queues related to ordering guarantees and throughput behavior — no more, no fewer, since some commonly assumed FIFO facts are actually inaccurate or oversimplified.

**Options:**
A. Message order is guaranteed only within the same message group ID; messages belonging to different message groups may still be delivered out of order relative to one another.
B. FIFO queues guarantee absolute global exactly-once delivery across the entire queue, with no possibility of any duplicate ever occurring, regardless of producer retries, consumer failures, or network issues.
C. With high throughput mode enabled, a FIFO queue can sustain up to 3,000 messages per second for a single API action even without using batched send/receive/delete calls.
D. FIFO queue names must end in the .fifo suffix, and an existing SQS standard queue can be converted to a FIFO queue in place without needing to create a new queue.
E. Content-based deduplication, when enabled, computes a SHA-256 hash of the message body to generate the deduplication ID, valid within a rolling 5-minute deduplication interval.

**Correct answer(s):** A, E

**Why correct:** A correctly describes the actual scope of FIFO's ordering guarantee (per message group, not queue-wide). E correctly describes how content-based deduplication is computed and its time-bounded interval — both are precise, exam-accurate statements about FIFO behavior.

**Why each wrong option is wrong:** B overstates FIFO's guarantee — "exactly-once processing" applies within the bounds of the deduplication interval and correct application-side deletion behavior; it is not an absolute, unconditional impossibility of any duplicate under every failure mode. C is inaccurate because reaching the higher throughput ceiling with high throughput mode requires batched API calls (SendMessageBatch/ReceiveMessage with batching); a single non-batched API call is capped at a much lower per-second rate. D contains a false claim: while FIFO queue names must indeed end in .fifo, an existing standard queue cannot be converted to FIFO in place — a new queue must be created and traffic migrated to it.

**Trigger words:** "exactly two true characteristics," "some commonly assumed FIFO facts are actually inaccurate."

**Underlying architectural principle:** Exam-accurate knowledge of FIFO requires precision about *scope* (per-group, not global) and *mechanism* (batching required for peak throughput; new queue required for conversion) — not just the marketing-level summary of "FIFO means ordered and exactly-once."

---

### Question 14 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A serverless order-processing pipeline uses Lambda functions triggered asynchronously by S3 event notifications. The team wants two things using AWS's current recommended mechanism rather than an older one: first, automatic routing of the full event payload plus rich error context (error type, stack trace) for any invocation that exhausts all retries; second, the ability to separately route information about successful invocations to a monitoring pipeline for downstream reporting.

**Options:**
A. Configure Lambda Destinations, with an on-failure destination pointing to an SQS queue and a separate on-success destination pointing to an EventBridge bus.
B. Configure a Dead Letter Queue (DLQ) on the Lambda function, pointing to an SQS queue.
C. Wrap the function's business logic in a try/catch block that manually publishes a message to an SNS topic on both success and failure paths.
D. Enable AWS X-Ray active tracing on the function to capture success and failure metadata for downstream consumption.
**Correct answer(s):** A

**Why correct:** Lambda Destinations (the modern, AWS-recommended replacement for the older DLQ-only mechanism) natively supports separate on-success and on-failure routing, and the failure destination payload includes richer invocation/error context than a classic DLQ, satisfying both stated requirements without custom code.

**Why each wrong option is wrong:** B (classic DLQ) only captures failed invocations, provides less error context than Destinations, and has no concept of routing successful invocations elsewhere. C reinvents functionality Lambda already provides natively, adding custom code, maintenance burden, and risk of missed edge cases (e.g., the function crashing before the catch block executes). D provides tracing and observability data for debugging performance/latency, not a mechanism for routing invocation records (success or failure) to other services.

**Trigger words:** "richer error information," "route... successful invocations," "AWS's modern recommended feature rather than an older mechanism."

**Underlying architectural principle:** Lambda Destinations, not the legacy DLQ-only configuration, is the current best-practice mechanism for capturing and routing both successful and failed asynchronous invocation outcomes.

---

### Question 15 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A fintech company runs a custom EventBridge bus that has had an Archive enabled with no event pattern filter (capturing every event on the bus) since well before the events in question occurred. Six weeks after a regulatory change, compliance requires that every "TradeExecuted" event from the past 30 days be redelivered — exactly as originally published — to a newly added fraud-analysis Lambda target that did not exist at the time the original events occurred, without re-triggering any of the bus's other pre-existing rule targets and without asking the original producing services to resend anything.

**Options:**
A. Use EventBridge Replay, scoped to the relevant time window, to redeliver the archived events matched by a rule filtering for TradeExecuted events targeting only the new fraud-analysis Lambda function.
B. Query CloudTrail data events covering the past 30 days and manually reconstruct and republish the TradeExecuted payloads to the bus under a new rule scoped to the fraud-analysis target.
C. Ask the original producing services to republish all TradeExecuted events from the past 30 days to the bus, with a new rule scoped only to the fraud-analysis Lambda target.
D. Configure an EventBridge Pipe from a Kinesis stream to redeliver the events, assuming the original producers were also streaming a parallel copy of every event to Kinesis.

**Correct answer(s):** A

**Why correct:** Because the Archive was already capturing all bus traffic with no filter before these events occurred, EventBridge Replay can redeliver the exact original event payloads for the specified time window to a specific target (the new rule/target combination), without touching any other pre-existing target and without any producer involvement.

**Why each wrong option is wrong:** B requires manually reconstructing events from CloudTrail data, which is unreliable, operationally heavy, and not guaranteed to preserve the exact original event structure — it exists only because the scenario is designed to test whether you recognize the Archive already made this unnecessary. C explicitly violates the stated constraint that producers must not need to resend anything. D relies on an unstated, unconfirmed assumption (that a parallel Kinesis copy exists) rather than using the capability the scenario already establishes (a pre-existing, unfiltered Archive).

**Trigger words:** "has had an Archive enabled... since well before the events... occurred," "redelivered... exactly as originally published," "without asking the original producing services to resend anything."

**Underlying architectural principle:** EventBridge Archive and Replay let you retroactively redeliver historical events to new targets — but only if an Archive was proactively enabled before those events occurred; recognizing this precondition is the key exam trap.

---

### Question 16 [Priority: P0] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A retailer's OrderService publishes an "OrderPlaced" event that must reach three downstream systems — Billing, Inventory, and Shipping — independently. Each downstream system occasionally has planned maintenance windows of up to 4 hours, during which it must not miss events. The team also wants messages that a given downstream consumer fails to process after several attempts to be captured separately per service for manual review, so that one service's processing failures never affect or are ever confused with another service's failures. Select the two design elements essential to satisfying all of these requirements.

**Options:**
A. Fan out the OrderPlaced event from an SNS topic to one dedicated SQS queue per downstream service.
B. Configure a separate dead-letter queue with its own redrive policy on each downstream service's SQS queue.
C. Use a single shared SQS queue polled by all three downstream services, with visibility timeout tuned per service's expected processing time.
D. Rely solely on SNS's built-in delivery retry policy, without adding SQS queues, to buffer through each service's 4-hour maintenance windows.
E. Use one shared dead-letter queue across all three downstream services to simplify failure monitoring.

**Correct answer(s):** A, B

**Why correct:** A gives each service its own durable, independently-paced buffer so a 4-hour maintenance window on one service never causes it to miss events or affect the others. B gives each service its own isolated dead-letter queue, so persistently failing messages are captured per service for manual review without commingling failures across services.

**Why each wrong option is wrong:** C is a competing-consumers pattern — each message on the shared queue is delivered to only one of the three pollers, so Billing, Inventory, and Shipping would each see only a subset of orders rather than all of them. D is unsound because SNS's own delivery retry mechanism is not designed as a multi-hour durable buffer substitute for a genuinely unavailable subscriber — it does not reliably hold undelivered messages for hours the way a dedicated SQS queue does. E defeats the explicit "never affect or be confused with another service's failures" requirement by mixing all three services' failed messages into one undifferentiated queue, making per-service manual review and root-cause tracing much harder.

**Trigger words:** "processed independently," "must not miss events," "captured separately per service," "never affect or... be confused with another service's failures."

**Underlying architectural principle:** Reliable, isolated multi-consumer fan-out requires both a dedicated queue per subscriber (for independent durability) and a dedicated DLQ per subscriber (for isolated failure handling) — sharing either resource across consumers reintroduces cross-service coupling the design is meant to eliminate.

---

### Question 17 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A company implements an order-fulfillment saga as four Lambda functions that synchronously invoke one another in sequence: reserve inventory, charge payment, arrange shipping, send confirmation. When payment fails after inventory has already been reserved, the current code relies on scattered, ad hoc try/catch blocks across functions to release the inventory reservation as a compensating action — and this logic has bugs that sometimes leave inventory incorrectly locked. The team wants to refactor onto AWS Step Functions for correctness and auditability. Select the two statements that accurately describe why and how this redesign should work.

**Options:**
A. Step Functions Standard Workflows provide built-in execution history showing exactly where in the saga a failure occurred, and native Catch/Retry transitions can route a payment failure directly to a compensating "ReleaseInventory" state.
B. Direct synchronous Lambda-to-Lambda invocation chains tightly couple the functions' availability and force the calling function to pay for idle compute time while blocked waiting on the next function's response — overhead that Step Functions avoids because the state machine, not a Lambda function, manages transitions and waits.
C. Migrating this saga to Step Functions requires rewriting each Lambda function using a Step Functions-specific SDK, since ordinary Lambda functions cannot be invoked as Task states.
D. Step Functions Express Workflows are strictly required for any saga involving compensating transactions, because Standard Workflows do not support Catch/Retry.
E. Because Lambda automatically retries failed asynchronous invocations, no additional orchestration layer is needed to implement reliable compensating transactions for this saga.

**Correct answer(s):** A, B

**Why correct:** A correctly describes Step Functions' native ability to visualize failure points and route to compensating states via Catch/Retry — directly solving the described bug-prone, ad hoc compensation logic. B correctly identifies a real cost and coupling downside of synchronous Lambda-to-Lambda chains that Step Functions removes by having the state machine own transitions and waits instead of a billed, blocked Lambda function.

**Why each wrong option is wrong:** C is false — ordinary Lambda functions are invoked from Step Functions as Task states by referencing their ARN; no rewrite or special SDK is required. D is false — Standard Workflows fully support Catch/Retry (it is a core, long-standing feature) and are often the better fit specifically because of their long execution duration and detailed audit history, not a limitation compared to Express. E is false on two counts: the functions in this saga are invoked synchronously (Lambda's automatic async retry does not apply to synchronous invocations at all), and even where retries do apply, retrying a failed step alone does not implement compensating-transaction logic for prior, already-completed steps.

**Trigger words:** "scattered, ad hoc try/catch blocks," "compensating action," "correctness and auditability."

**Underlying architectural principle:** Step Functions replaces error-prone, hand-coded compensating-transaction logic embedded in chained Lambda invocations with native Catch/Retry state transitions and a visualized, auditable execution history — without requiring any change to how the underlying Lambda functions themselves are written.

---

*End of Domain 2 decoupling question set (17 questions). Original practice content for personal SAA-C03 study — not sourced from or representing any real, leaked, or NDA-restricted exam material.*
