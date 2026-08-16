# Serverless & Messaging Mastery (SAA-C03)

## Lambda — Triggers

Two invocation models drive most exam distractors:

- **Synchronous (push)**: API Gateway, ALB, CLI/SDK invoke. Caller waits for a response; errors are returned to caller — Lambda does **not** retry synchronous invokes on failure.
- **Asynchronous (event)**: S3, SNS, EventBridge, CloudWatch Logs. Lambda queues the event internally and retries automatically (twice by default) on failure, then optionally routes to a **Dead Letter Queue (DLQ)** or, preferably in 2026, a configured **on-failure destination** (SQS, SNS, Lambda, EventBridge) — destinations are the modern replacement for DLQs and also support on-success routing.
- **Poll-based (event source mapping)**: SQS, Kinesis Data Streams, DynamoDB Streams, MSK/Kafka. Lambda's poller reads batches and invokes synchronously on your function's behalf. For **SQS**, failed batches return to the queue (respecting visibility timeout) and you tune `ReportBatchItemFailures` for partial-batch failure handling — a frequent exam scenario ("some messages in a batch fail, don't want to reprocess successful ones").

**Exam trigger words**: "process each S3 object as it's uploaded" → S3 event notification → Lambda (async). "React to changes across accounts/services" → EventBridge → Lambda. "Ordered processing of a stream" → Kinesis/DynamoDB Streams event source mapping.

## Lambda — VPC Configuration Trade-offs

Decision boundary: **only put a Lambda in a VPC if it needs to reach a VPC-only resource** (RDS, ElastiCache, private ALB/EC2, on-prem via VPN/DX). If it only talks to AWS public service APIs (S3, DynamoDB, SNS/SQS via public endpoints), **do not attach it to a VPC** — it adds ENI management overhead for no benefit.

- Modern Lambda (post-2019 networking model) uses **Hyperplane ENIs** shared across functions, which largely eliminated the old "cold start VPC penalty" and slow ENI provisioning problem. The exam guide may still test the *old* mental model as a distractor ("VPC-attached Lambda always has higher cold start latency") — this is no longer categorically true, but it's still true that VPC Lambdas need **subnets with sufficient free IPs** and, if they need internet/public AWS API access, a **NAT Gateway** (private subnet) or **VPC endpoints** (Gateway endpoint for S3/DynamoDB, Interface endpoint for others) — using VPC endpoints is the cost/performance-optimized answer over NAT Gateway when the exam asks "reduce cost of Lambda-in-VPC accessing S3/DynamoDB."
- Distractor to watch: "Lambda times out reaching the internet after being moved into a VPC" → answer is missing NAT Gateway/route, not "remove from VPC" (if it genuinely needs private resource access).

## Lambda — Concurrency

- **Reserved concurrency**: caps *and guarantees* a max number of concurrent executions for a function — used to (a) protect downstream systems (e.g., RDS connection exhaustion) by capping, or (b) guarantee capacity by reserving from the account pool away from other functions.
- **Provisioned concurrency**: pre-initializes execution environments to eliminate cold starts for latency-sensitive, spiky, or scheduled-traffic workloads (e.g., synchronous API backing a user-facing app, predictable traffic spike at 9am). This is the answer whenever the exam says "consistent low latency" + "Lambda" + "cold start" together.
- **Account concurrency limit** is a soft limit shared across all functions in a region — the exam tests recognizing that one runaway function (e.g., processing an SQS/S3 flood) can starve concurrency from unrelated functions unless reserved concurrency partitions it.
- SQS-triggered Lambda concurrency scales based on queue depth but is capped by the function's concurrency limit (reserved or account-level) — throttled invokes leave messages on the queue rather than being lost, which is a key resiliency point vs. Kinesis (where a throttled/errored shard iterator can stall an entire shard's processing).

## Lambda — Cold Starts

Exam-relevant mitigations, roughly in order of what the exam wants you to pick:
1. **Provisioned concurrency** — deterministic fix for latency-sensitive sync workloads.
2. Smaller deployment package / fewer dependencies, and language choice (interpreted languages like Python/Node typically cold-start faster than JVM-based runtimes for equivalent workloads) — the exam sometimes frames "Java Lambda has high p99 latency spikes" and wants provisioned concurrency or a runtime/package-size fix, not "move off Lambda."
3. **SnapStart** — caches an initialized execution environment snapshot to cut cold start time without provisioned concurrency's standing cost. SnapStart originally launched as a **Java-only** feature (Corretto runtimes), but AWS extended it to **Python and .NET** runtimes (previewed late 2024, generally available in 2025) — don't assume "Java-specific" is still true if the exam names a runtime explicitly; check what the question is actually testing (typically Java, since that's the classic slow-JVM-cold-start scenario), but know the feature is no longer limited to Java.
4. Cold starts are a **Design High-Performing Architectures** domain topic — if the question emphasizes cost sensitivity over latency, provisioned concurrency (which incurs standing cost) is the *wrong* answer; accept cold starts instead.

## API Gateway — REST API vs HTTP API

This comparison is a classic exam distractor because both are "API Gateway" but sit in different cost/feature trade-off zones:

| Dimension | REST API | HTTP API |
|---|---|---|
| Cost | Higher per-request cost | Significantly cheaper (~70% less) |
| Feature depth | Full feature set: request/response transformation (mapping templates), API keys + usage plans, WAF integration, private VPC endpoints (execute-api), caching | Leaner: no request/response VTL mapping templates (basic parameter mapping only), no built-in API key/usage plan quotas. **AWS WAF support was added to HTTP APIs in late 2024** — the older "HTTP API has no WAF option" distractor is outdated; don't assume WAF automatically means REST API |
| Auth | Cognito User Pools, IAM, Lambda authorizers | JWT authorizers (OIDC/Cognito), IAM, Lambda authorizers (simpler payload) |
| Use case signal | "Need usage plans/API keys for external partners," "need full request/response mapping templates" | "Cost-optimized," "simple proxy to Lambda/HTTP backend," "just need JWT auth" |

**Decision rule**: if the question emphasizes **cost optimization** and the workload is a simple proxy (Lambda or HTTP backend) needing basic JWT/IAM auth → **HTTP API**. If it mentions **API keys, usage plans/throttling per client, or full request/response VTL mapping templates** → **REST API** (these remain REST-only). WAF alone is **no longer** a reliable REST-vs-HTTP discriminator since both API types support it today — if an exam question treats "needs WAF" as automatically implying REST API, that reflects the pre-2024 feature set; read the rest of the question for a REST-specific requirement (usage plans, API keys, VTL mapping) before committing to that answer.

## API Gateway — Throttling

- Throttling is layered: **account-level (region) limits**, **API/stage-level limits**, and **per-client usage plans with API keys** (REST API only) for granular quota + rate limiting per customer/tenant.
- Exam pattern: "Different partners should have different rate limits" → usage plans + API keys (REST API required — HTTP API doesn't support this natively).
- Throttling returns **429** to the caller; this is distinguished from Lambda concurrency throttling (which returns 429 from Lambda itself) — a multi-hop question may ask you to identify *where* in the chain (API GW stage limit vs. Lambda reserved concurrency) a bottleneck occurred based on which error code/log surfaces it.

## API Gateway — Auth Options

- **IAM authorization**: caller signs requests with SigV4 — used for internal service-to-service calls within the same AWS environment (other AWS accounts, EC2/Lambda callers).
- **Cognito User Pool authorizer**: built-in, no custom code, best when you're already using Cognito for the app's user directory — the "native/managed" answer.
- **Lambda authorizer (custom)**: use when auth logic is custom (validate a third-party token, check a legacy identity provider, implement custom business rules) — the "flexible/build-your-own" answer. Exam trigger: "integrate with existing OAuth/OIDC provider that isn't Cognito," or "custom token format."
- **Resource policies**: control *network-level* access (restrict to a VPC, VPC endpoint, or IP range) — this is about *where the call comes from*, not *who* the caller is; don't confuse with authorizers when the question says "restrict API to only be callable from within our VPC."

## Step Functions

- Use when you need **orchestration with state, branching, retries/backoff, human-in-the-loop wait steps, or long-running workflows** (up to a year) — distinguishing signal vs. plain Lambda chaining or SQS/SNS choreography.
- **Standard workflows**: exactly-once execution, up to a year in duration, visual execution history/audit trail — pick for long-running, auditable business processes (order fulfillment, approval workflows).
- **Express workflows**: at-least-once, short-duration (up to 5 minutes), high-volume/high-throughput event processing — pick when the question says "process millions of IoT/streaming events with low-cost, short-duration orchestration."
- Exam trigger words: "coordinate multiple Lambda functions with conditional logic and retries," "need to wait for external human approval," "visual workflow with error handling and rollback (compensating transactions)" → Step Functions, not EventBridge Pipes or plain Lambda-invokes-Lambda (which the exam flags as an anti-pattern — direct Lambda-to-Lambda synchronous calls create tight coupling and pay-per-wait costs).

## Event-Driven Architectural Patterns

**S3 → Lambda**: object-created/removed/restored events trigger a Lambda directly or via SNS/SQS fan-out. Use direct S3→Lambda for single-consumer processing (thumbnail generation, virus scan, format conversion). If **multiple** independent consumers need the same object event, insert **SNS** (fan-out) or **EventBridge** (if you need content-based filtering across many rule consumers) between S3 and Lambda — for a given event type and matching prefix/suffix filter, S3 notification configuration targets one destination, which is the giveaway for needing SNS/EventBridge in the middle when several independent consumers must react to the same event.

**API Gateway → Lambda → DynamoDB**: canonical serverless REST backend. Exam angles: use **IAM roles (least privilege)** for the Lambda execution role scoped to specific DynamoDB actions/table, not the API Gateway itself, to access DynamoDB. For high-throughput bursts, DynamoDB **on-demand capacity** avoids throttling without pre-provisioning; if cost-predictable and steady, provisioned capacity + auto scaling. Watch for DynamoDB throttling (ProvisionedThroughputExceededException) bubbling up as Lambda errors — the fix is capacity mode or exponential backoff, not scaling Lambda concurrency.

**SNS → multiple SQS (fan-out)**: the standard pattern when one event must be independently and durably consumed by multiple decoupled systems — each subscriber gets its own SQS queue so one slow/down consumer doesn't block or lose messages for others (vs. subscribing Lambda functions directly to SNS, where a failed Lambda invoke only gets SNS's built-in retry, not a durable queue backlog). Exam trigger: "order placed event must be processed by billing, inventory, and shipping systems independently, and no message should be lost if one service is down" → SNS fan-out to SQS per consumer.

**EventBridge → Lambda/Step Functions**: use when you need **content-based filtering/routing** (rules matching on event payload attributes), **schema registry/discovery**, **cross-account/cross-service event routing**, or **SaaS partner event sources**. This is a differentiator vs. SNS, though a narrower one than it used to be: EventBridge rules filter on structured event content (including numeric matching, prefix/suffix, anything-but, and other rich operators) across many targets, with schema registry and cross-account routing built in. SNS filter policies can also match on the **message body**, not just message attributes (added 2022), so simple content-based routing to a *single* topic's subscribers is achievable with SNS too — but EventBridge remains the stronger pick when the question emphasizes many event types routed by content across many services/accounts or SaaS integrations. Exam trigger words: "route different event types to different targets based on event content," "third-party SaaS integration," "schedule-based invocation" (EventBridge Scheduler/rules) → EventBridge.

## Decoupling Deep-Dive: SQS vs SNS vs EventBridge vs Kinesis

Use this reasoning framework, in order, to pick the service — the exam is testing whether you apply the framework, not memorize a lookup table:

**1. Consumer count and delivery model — is this point-to-point or fan-out?**
- Exactly one logical consumer pool pulling work items → **SQS** (queue, pull-based, competing consumers, message deleted after processing).
- One event, many independent subscribers, each wants its own durable copy → **SNS** (pub/sub push) — typically fanned into SQS queues per subscriber for durability (SNS alone doesn't retain undelivered messages the way a queue does).
- Many event *types* need to be routed differently to many *targets* based on content → **EventBridge** (rule-based routing across a bus), not SNS (topic-based, coarser).
- Many consumers need to **independently and repeatedly re-read** the same event stream (replay) → **Kinesis** (or MSK), not SQS/SNS (messages are consumed/removed, no replay).

**2. Ordering guarantees**
- Strict ordering per key/entity required (e.g., processing a specific user's events in order) → **SQS FIFO** queue (ordering within a message group) or **Kinesis** (ordering within a shard, keyed by partition key).
- No ordering requirement, maximize throughput → **SQS Standard** (at-least-once, best-effort ordering, near-unlimited throughput) or Kinesis without needing per-key semantics.
- **SNS standard topics** and **EventBridge** provide no ordering guarantee by default — if the question demands strict ordering, these are distractors regardless of other fit. Note the exception: **SNS FIFO topics** (paired with SQS FIFO subscribers) do provide strict, deduplicated, in-order delivery within a message group — if a question explicitly combines "SNS," "fan-out," and "strict ordering," SNS FIFO → SQS FIFO is a legitimate answer, not automatically wrong.

**3. Event routing / filtering complexity**
- Simple topic-based broadcast (all subscribers care about "all messages on this topic," maybe basic attribute or body-based filter) → **SNS**.
- Complex, content-based filtering with many rules matching on nested JSON fields, and routing across services/accounts/regions or to SaaS/partner destinations → **EventBridge**.
- If the exam says "filter events based on their content/payload to route to different targets across many services/accounts" → **EventBridge** is almost always correct over SNS; for simpler single-topic filtering, SNS filter policies (attribute- or body-based) can suffice.

**4. Streaming / replay needs**
- Need to **replay** historical events, have **multiple consumer applications reading the same data independently at their own pace**, or need **real-time analytics/aggregation over an ordered stream** (e.g., clickstream, IoT telemetry, log aggregation feeding multiple analytics consumers) → **Kinesis Data Streams** (or Kafka/MSK for teams already invested in Kafka tooling).
- No replay need, message is consumed once and gone → SQS/SNS.
- Kinesis retains data for a configurable retention window (extendable well beyond the default 24 hours, up to 365 days with long-term retention) enabling multiple independent consumers (via enhanced fan-out or Lambda event source mappings) to read the same stream at different offsets — this replay/multi-reader capability is the single biggest differentiator vs. SQS.

**5. Decoupling "shape" summary (the fast heuristic for exam questions)**:
- **SQS** = buffer/level-load between a producer and a single processing tier; smooths spiky load, enables retry via visibility timeout + DLQ, decouples producer/consumer availability.
- **SNS** = one-to-many push notification/fan-out at the topic level; simple, low-latency, no replay (ordering only if using FIFO topics).
- **EventBridge** = many-producers-to-many-consumers event bus with content-based routing, schema awareness, SaaS/cross-account integration, and scheduling — the "enterprise event router."
- **Kinesis** = ordered, replayable, high-throughput streaming data ingestion for multiple independent real-time/analytics consumers.

**Common distractors to flag explicitly**:
- "Need to decouple microservices and guarantee no message loss if a consumer is down" — could look like it needs Kinesis, but if there's no replay/multi-independent-reader/streaming-analytics requirement, **SQS is the simpler, cheaper, correct answer**. Don't over-engineer toward Kinesis just because "streaming" sounds impressive.
- "Fan out one event to multiple services" defaults exam-takers to SNS, but if the requirement includes **rich, multi-service, content-based filtering/routing** across many targets, the stronger answer is **EventBridge**; note that SNS filter policies now support body-based (not just attribute-based) matching, so don't assume simple content filtering automatically rules out SNS — the deciding factor is the *complexity and breadth* of routing, not filtering's mere existence.
- "Process records in the exact order received, at massive scale, with multiple analytics consumers" → **Kinesis**, not SQS FIFO. SQS FIFO throughput has increased substantially since the "high throughput mode" launch (2023) — it can now handle tens of thousands of messages per second per API action with batching in many regions — so "FIFO is throughput-capped" is no longer an absolute distinction; the real differentiators for choosing Kinesis are **replay** and **multiple independent analytics consumers reading the same data at their own pace**, which SQS FIFO cannot provide.
- Seeing the word **"schedule"** (cron-like invocation) → EventBridge Scheduler/rules, not Step Functions or Lambda alone.
