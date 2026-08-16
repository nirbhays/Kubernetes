# SAA-C03 Practice Questions — Domain 2: Design Resilient Architectures (26%)
Focus: Multi-AZ and multi-region HA patterns | Eliminating single points of failure | ALB vs NLB vs Gateway Load Balancer selection | Route 53 routing policies (simple/weighted/latency/failover/geolocation/geoproximity/multivalue)

Original practice content created for study purposes — these are **not** real AWS exam questions and do not reproduce any leaked/dumped exam content. Based on 2026 AWS service behavior and the official SAA-C03 exam guide scope.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A three-tier web application runs its application servers in a single Auto Scaling group spread across two Availability Zones, fronted by an Application Load Balancer that is also configured across both AZs. The database, however, is a single RDS MySQL instance running in only one of the two AZs, with no standby configured. During a recent AZ-level network disruption, the application tier stayed up, but every request failed once it tried to reach the database. Leadership wants the database tier to survive the loss of a single AZ without manual intervention, with minimal application changes.
**Options:**
A. Enable RDS Multi-AZ deployment so a synchronously replicated standby in a second AZ can be automatically promoted on failure.
B. Take manual daily snapshots of the RDS instance and store them in S3 for recovery if the AZ fails.
C. Add a read replica of the RDS instance in the second AZ and update the application to write to whichever replica is currently reachable.
D. Move the RDS instance into the same AZ as the majority of the application servers to reduce cross-AZ latency.
**Correct answer(s):** A
**Why correct:** RDS Multi-AZ maintains a synchronously replicated standby in a different AZ and automatically fails over the DNS endpoint to it during an AZ-level disruption, with no application code changes required — directly matching "survive the loss of a single AZ without manual intervention, with minimal application changes."
**Why each wrong option is wrong:** B provides a recovery point measured in up to a day of data loss and requires a manual restore process, which is neither automatic nor minimal-effort; C is wrong because RDS read replicas are read-only by default and application-level failover logic to pick "whichever replica is reachable" is exactly the manual, custom engineering effort the requirement wants avoided, and standard read replicas replicate asynchronously; D actively removes AZ redundancy entirely and does the opposite of what's being asked.
**Trigger words:** "single RDS MySQL instance running in only one of the two AZs," "survive the loss of a single AZ without manual intervention," "minimal application changes."
**Underlying architectural principle:** A single-AZ resource anywhere in an otherwise multi-AZ stack is a single point of failure; RDS Multi-AZ is the native, code-free way to remove that SPOF at the database layer.

---

### Question 2 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retail company's checkout service runs behind an Application Load Balancer with an Auto Scaling group spanning three Availability Zones. A post-incident review reveals that the NAT Gateway used for outbound internet access (to reach a third-party payment API) exists as a single NAT Gateway in only one AZ, shared by route tables in all three private subnets. When that AZ experienced an outage last month, instances in the other two healthy AZs also lost the ability to reach the payment API, even though those instances themselves were fine. The team needs to eliminate this single point of failure at the lowest additional monthly cost that still preserves full-region NAT resilience.
**Options:**
A. Deploy one NAT Gateway per AZ, and update each AZ's private subnet route table to use the NAT Gateway in its own AZ.
B. Replace the NAT Gateway with a single NAT instance sized to handle triple the current traffic.
C. Keep the single NAT Gateway but add a second Elastic IP address to it for redundancy.
D. Route outbound traffic from all three AZs through a Gateway Load Balancer endpoint instead of a NAT Gateway.
**Correct answer(s):** A
**Why correct:** A NAT Gateway is an AZ-scoped resource, so the only way to remove the cross-AZ dependency it creates is to deploy one per AZ and keep each AZ's outbound traffic local to its own NAT Gateway — this is the standard, minimum-cost pattern that fully eliminates the single point of failure while preserving resilience for all three AZs.
**Why each wrong option is wrong:** B replaces a managed, highly available service with a single self-managed NAT instance, which is itself a single point of failure (and a single instance) and adds operational burden, not less; C is wrong because attaching a second Elastic IP to the same NAT Gateway does nothing to protect against the AZ hosting that NAT Gateway going down — the resource itself is still confined to one AZ; D is wrong because Gateway Load Balancer is designed for inserting third-party virtual appliances (firewalls, IDS/IPS) into the traffic path, not for providing outbound internet NAT functionality.
**Trigger words:** "single NAT Gateway used... in only one AZ," "instances in the other two healthy AZs also lost the ability to reach," "eliminate this single point of failure at the lowest additional monthly cost."
**Underlying architectural principle:** NAT Gateways are AZ-scoped, so true multi-AZ resilience requires one NAT Gateway per AZ with per-AZ route tables, not a single shared NAT Gateway.

---

### Question 3 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs a fleet of internal microservices communicating purely over raw TCP on a non-HTTP custom binary protocol at extremely high throughput (millions of requests per second), and needs the client's source IP address preserved end-to-end for internal audit logging. The services do not need any HTTP-layer routing rules, host/path-based routing, or WebSocket support.
**Options:**
A. Network Load Balancer, using its ability to preserve client source IP and handle ultra-high-throughput Layer 4 TCP traffic with minimal latency.
B. Application Load Balancer, because it is AWS's most feature-rich and generally recommended load balancer for all new workloads.
C. Gateway Load Balancer, because it scales to the highest throughput of any AWS load balancer type.
D. Classic Load Balancer, because it operates at both Layer 4 and Layer 7 simultaneously.
**Correct answer(s):** A
**Why correct:** NLB operates at Layer 4, is purpose-built for extremely high throughput with ultra-low latency, natively preserves the client's source IP address, and requires no HTTP-layer features — matching every requirement in the scenario exactly.
**Why each wrong option is wrong:** B is wrong because ALB operates at Layer 7 and is designed for HTTP/HTTPS traffic with content-based routing, which this raw TCP, non-HTTP workload doesn't use or need, and ALB's request-based model isn't optimized for this use case; C is wrong because Gateway Load Balancer's purpose is transparently inserting third-party network appliances into a traffic path (using GENEVE encapsulation), not serving as a general-purpose internal load balancer for application traffic; D is wrong because Classic Load Balancer is a legacy load balancer type that AWS explicitly recommends against for new workloads in favor of ALB/NLB, and — unlike NLB, which preserves the client source IP by default — a Classic Load Balancer's TCP listener only preserves the original source IP if Proxy Protocol is manually enabled, so it does not match the "preserved end-to-end" requirement out of the box.
**Trigger words:** "raw TCP," "custom binary protocol," "millions of requests per second," "client's source IP address preserved," "no... HTTP-layer routing rules."
**Underlying architectural principle:** Choose NLB when a workload is Layer 4, throughput/latency-critical, and requires client IP preservation; reserve ALB for Layer 7 HTTP(S)-aware routing needs.

---

### Question 4 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company runs a single-page application with a REST API backend. Traffic must be routed to different backend target groups depending on the URL path (`/api/orders/*` goes to the orders service, `/api/users/*` goes to the users service), and the security team additionally requires TLS termination with automatic integration to AWS Certificate Manager, plus native WebSocket support for a live order-status feature.
**Options:**
A. Application Load Balancer, using path-based routing rules across target groups with an ACM certificate attached to the HTTPS listener.
B. Network Load Balancer, using TCP listener rules to distribute traffic based on URL path.
C. Gateway Load Balancer, using GENEVE-based rules to inspect and route HTTP paths to different target groups.
D. Route 53 weighted routing pointed directly at each backend service's IP addresses, bypassing the need for a load balancer entirely.
**Correct answer(s):** A
**Why correct:** ALB is the only option here operating at Layer 7 with native path-based routing across multiple target groups, native ACM integration for TLS termination, and native WebSocket support — matching every stated requirement.
**Why each wrong option is wrong:** B is wrong because NLB operates at Layer 4 and has no visibility into HTTP URL paths, so it cannot make routing decisions based on `/api/orders/*` versus `/api/users/*`; C is wrong because Gateway Load Balancer is designed to transparently forward traffic to third-party virtual appliances for inspection, not to make application-aware HTTP path-routing decisions to target groups; D is wrong because Route 53 performs DNS resolution, not per-request Layer 7 routing, TLS termination, or health-check-driven load balancing — it cannot inspect a URL path within an established connection to route to different backends.
**Trigger words:** "route to different backend target groups depending on the URL path," "TLS termination with... ACM," "native WebSocket support."
**Underlying architectural principle:** Path-based and host-based routing, TLS termination with ACM, and WebSocket support are defining Layer 7 capabilities unique to ALB among AWS load balancer types.

---

### Question 5 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A cybersecurity vendor sells a virtual firewall appliance that customers deploy inside their own VPCs. The vendor wants all inbound and outbound traffic for a customer's application subnet to be transparently intercepted, inspected, and either allowed or blocked by a fleet of these third-party firewall appliances, which must be able to scale horizontally and be added or removed without customers having to reconfigure their route tables each time. The solution must preserve the original packet as closely as possible for deep packet inspection.
**Options:**
A. Gateway Load Balancer, distributing traffic to a scalable fleet of appliance instances using GENEVE encapsulation and a single Gateway Load Balancer endpoint referenced from route tables.
B. Application Load Balancer, using host-based routing rules to direct traffic to whichever firewall appliance is healthy.
C. Network Load Balancer, since it operates at Layer 4 and is therefore capable of transparent traffic inspection.
D. Route 53 failover routing pointed at the healthy firewall appliance's Elastic IP address.
**Correct answer(s):** A
**Why correct:** Gateway Load Balancer is purpose-built for exactly this pattern — transparently inserting a horizontally scalable fleet of third-party virtual appliances (firewalls, IDS/IPS) into a traffic path using GENEVE encapsulation, with a single, stable Gateway Load Balancer endpoint that route tables reference, so the appliance fleet can scale or change without customer route table edits.
**Why each wrong option is wrong:** B is wrong because ALB terminates and re-generates HTTP requests at Layer 7, which does not preserve the original packet for deep inspection and isn't designed for appliance-fleet insertion; C is wrong because plain NLB, while Layer 4, does not provide the transparent bump-in-the-wire appliance-insertion model or GENEVE encapsulation that Gateway Load Balancer specifically provides — it load-balances application traffic to targets, not traffic through inspection appliances; D is wrong because Route 53 is DNS-based and does not intercept or inspect in-flight traffic at the packet level at all.
**Trigger words:** "third-party firewall appliances," "transparently intercepted, inspected," "scale horizontally... without... reconfigur[ing] route tables," "preserve the original packet."
**Underlying architectural principle:** Gateway Load Balancer is the specific AWS service for transparently distributing traffic across a scalable fleet of third-party network virtual appliances via GENEVE, distinct from ALB/NLB's target-load-balancing role.

---

### Question 6 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company's corporate website is hosted entirely as a static site on S3 with CloudFront in front of it, serving marketing content to a global audience with no dynamic backend, no per-request routing logic, and no health-check-driven target selection needed. The team wants the absolute simplest DNS setup that maps their apex domain to the CloudFront distribution.
**Options:**
A. Simple routing policy with a Route 53 alias record pointing to the CloudFront distribution.
B. Weighted routing policy split 100/0 across two identical CloudFront distributions.
C. Latency-based routing policy across CloudFront distributions deployed in multiple regions.
D. Multivalue answer routing policy returning multiple CloudFront IP addresses with health checks.
**Correct answer(s):** A
**Why correct:** A Simple routing policy with an alias record is the most straightforward way to map a domain to a single AWS resource like a CloudFront distribution, and it's explicitly the right fit when there's no need for weighting, latency-based selection, or health-check-driven answers — CloudFront itself is already a globally distributed edge network, so no DNS-level traffic-steering logic is needed.
**Why each wrong option is wrong:** B introduces unnecessary complexity and a second distribution to manage for no functional benefit when 100/0 weighting is functionally identical to just using one record; C is unnecessary and doesn't apply meaningfully here since CloudFront distributions are already globally edge-optimized — this pattern is meant for steering between distinct regional origins/endpoints, not needed for a single global CDN distribution; D adds health-checked multiple answers when there is only one distribution and no described need for DNS-level failover or client-side load spreading across multiple endpoints, and CloudFront distributions aren't referenced by static IP addresses in the way multivalue answer is designed for.
**Trigger words:** "static site," "no dynamic backend," "no per-request routing logic," "no health-check-driven target selection needed," "absolute simplest DNS setup."
**Underlying architectural principle:** Simple routing is the correct (and often overlooked) answer whenever a scenario explicitly has only one target and no requirement for weighting, latency awareness, or health-check-based failover.

---

### Question 7 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A SaaS company runs identical production stacks in us-east-1 and eu-west-1, each behind its own regional Application Load Balancer. Customers should always be routed to whichever region gives them the lowest network round-trip time, since the application is latency-sensitive (real-time collaborative editing), and both regions are fully capable of serving 100% of global traffic if the other region fails.
**Options:**
A. Latency-based routing policy across both regional ALB endpoints, combined with Route 53 health checks so an unhealthy region is automatically removed from consideration.
B. Weighted routing policy with a 50/50 split between the two regional ALB endpoints.
C. Geolocation routing policy mapping each country to its geographically nearest region.
D. Simple routing policy with a single alias record pointing to the ALB in us-east-1, since it was the original primary region.
**Correct answer(s):** A
**Why correct:** Latency-based routing is specifically designed to direct users to whichever endpoint gives them the best measured network latency, which directly matches "lowest network round-trip time," and pairing it with health checks means Route 53 stops directing traffic to a region that fails, providing both the performance goal and the resilience goal in one configuration.
**Why each wrong option is wrong:** B is wrong because a fixed 50/50 weighted split ignores actual measured latency and would send some users to the farther, slower region regardless of their real round-trip time; C is wrong because geolocation routing is based on the geographic location of the user (or a static country/continent mapping) rather than measured network latency, so a user could be geographically closer to a region that isn't actually the fastest path due to network conditions, which doesn't satisfy "lowest network round-trip time" as precisely as latency-based routing; D is wrong because it sends 100% of global traffic to a single region regardless of where users are, directly contradicting the stated latency requirement and removing the benefit of running two regions at all.
**Trigger words:** "lowest network round-trip time," "latency-sensitive," "both regions are fully capable of serving 100% of global traffic if the other region fails."
**Underlying architectural principle:** Latency-based routing optimizes for measured network performance to each endpoint, which is a different (and often better-fitting) goal than geolocation routing's static geographic-to-region mapping.

---

### Question 8 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A streaming media company operates regional edge clusters in North America, Europe, and Asia-Pacific to serve video content with minimal latency. Legal counsel has mandated that, regardless of network latency, all users physically located in the European Union must always be served exclusively from the Europe cluster, for GDPR data-residency compliance — this requirement takes priority over performance considerations. The company also wants any other users worldwide to be routed based on the lowest measured latency across the remaining clusters.
**Options:**
A. A Route 53 Traffic Flow policy that pins EU-located users to the Europe cluster via a geolocation rule, with a nested latency-based rule as the default branch for all other locations.
B. A pure latency-based routing policy across all three clusters, since it will naturally send most EU users to the Europe cluster anyway.
C. A weighted routing policy giving the Europe cluster a very high weight so most traffic lands there.
D. A geoproximity routing policy with a large negative bias applied to the North America and Asia-Pacific clusters.
**Correct answer(s):** A
**Why correct:** Geolocation routing is the only policy that can create a hard, compliance-grade guarantee based on a user's actual location (mapping the EU specifically to the Europe cluster) regardless of measured latency. A plain geolocation record's default branch normally points to a single static resource, not a dynamically-chosen lowest-latency cluster, so "latency-based for everyone else" needs a nested policy: Route 53 Traffic Flow's visual policy editor is the standard way to build this (a geolocation rule with a nested latency-based rule as its default branch) as a single policy record, though the same effect can also be produced with plain record sets by aliasing the default geolocation record to a separate name that holds the latency-based records. Either way, the compliance mandate and the performance goal are both satisfied.
**Why each wrong option is wrong:** B is wrong because pure latency-based routing has no compliance guarantee — an EU user with an unusually fast path to a non-EU cluster (e.g., due to transient network conditions or ISP peering) could legitimately be routed outside the EU, violating the mandate that this "takes priority over performance"; C is wrong because weighting is probabilistic and traffic-percentage-based, not deterministic by user location, so it cannot guarantee that every single EU user lands on the Europe cluster; D is wrong because geoproximity's bias shifts the geographic boundary of a resource's catchment area but does not offer a hard, location-based compliance guarantee tied to legal jurisdiction (e.g., "the EU") the way geolocation's country/continent mapping does.
**Trigger words:** "regardless of network latency," "must always be served exclusively from the Europe cluster," "GDPR data-residency compliance," "this requirement takes priority over performance."
**Underlying architectural principle:** When a scenario requires a hard, deterministic location-to-endpoint guarantee for compliance reasons, geolocation routing is correct even over latency-based or geoproximity routing, which optimize for performance or shift traffic probabilistically rather than guaranteeing jurisdictional placement.

---

### Question 9 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A gaming company runs matchmaking servers in three regions. The North America region has recently been over capacity relative to its physical infrastructure, so the team wants to shift a portion of the traffic that would normally go to the North America region toward the neighboring South America region instead, without physically moving any servers or changing where users are located, and without setting up entirely separate location-to-region mapping rules. They want fine-grained, incremental control over how much the North America catchment area shrinks.
**Options:**
A. Geoproximity routing policy using Route 53 Traffic Flow, applying a negative bias value to the North America resource to shrink its effective geographic catchment area in favor of South America.
B. Geolocation routing policy, remapping specific South American countries from the North America record to the South America record.
C. Weighted routing policy splitting traffic 70/30 between the North America and South America endpoints for all users worldwide.
D. Latency-based routing policy, since it will automatically detect the North America region is overloaded and shift traffic accordingly.
**Correct answer(s):** A
**Why correct:** Geoproximity routing with a bias value is specifically designed to expand or shrink a resource's effective geographic catchment area without moving infrastructure or manually remapping specific locations, giving fine-grained, incremental control — exactly the mechanism the team wants for shifting load between geographically adjacent regions.
**Why each wrong option is wrong:** B would work but requires manually identifying and remapping specific countries one by one, which is coarser and more operationally heavy than a single bias adjustment, and doesn't offer the same fine-grained incremental control the team wants; C is wrong because a flat weighted split applies the same 70/30 ratio to all users everywhere, including users far from either region, rather than specifically shrinking North America's geographic catchment near the South America boundary; D is wrong because latency-based routing has no awareness of a region's capacity or infrastructure load — it only measures network round-trip time, and it has no bias-style lever to intentionally shift traffic between regions for capacity reasons.
**Trigger words:** "shift a portion of the traffic... without physically moving any servers," "without... entirely separate location-to-region mapping rules," "fine-grained, incremental control over how much the... catchment area shrinks."
**Underlying architectural principle:** Geoproximity routing's bias value is the purpose-built mechanism for incrementally shifting traffic volume between geographically-based endpoints without manual location remapping or infrastructure changes.

---

### Question 10 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company runs its primary order-processing stack in us-east-1 and maintains a fully functional, continuously running (though downsized) standby stack in us-west-2. Under normal operation, 100% of customer traffic must go to us-east-1. If, and only if, us-east-1 becomes unavailable, all traffic must automatically shift to us-west-2 within a few minutes, with no manual DNS changes.
**Options:**
A. Failover routing policy with Route 53 health checks on the primary (us-east-1) endpoint, and a secondary record pointing to us-west-2.
B. Weighted routing policy with a 100/0 split, manually flipped to 0/100 by an on-call engineer during an incident.
C. Latency-based routing policy across both regions, relying on us-east-1 naturally having lower latency for most customers.
D. Multivalue answer routing policy returning both regions' IP addresses so clients can retry the other one on failure.
**Correct answer(s):** A
**Why correct:** Failover routing is purpose-built for exactly this active/passive pattern — it sends all traffic to a designated primary record as long as its associated health check passes, and automatically shifts all traffic to the secondary record the moment the primary fails a health check, with no manual DNS intervention required.
**Why each wrong option is wrong:** B explicitly requires a human ("on-call engineer") to manually flip the split during an incident, which directly violates "no manual DNS changes"; C is wrong because latency-based routing has no concept of a strict "100% to primary unless it's down" rule — it would continuously send some traffic to us-west-2 for any customers who happen to have lower latency there, even while us-east-1 is fully healthy; D is wrong because multivalue answer returns multiple IPs for client-side selection and does not guarantee 100% of traffic goes to one specific "primary" resource under normal conditions, nor does it provide a clean all-or-nothing failover semantics tied to a single primary/secondary hierarchy.
**Trigger words:** "100% of customer traffic must go to us-east-1," "if, and only if,... unavailable, all traffic must automatically shift," "no manual DNS changes."
**Underlying architectural principle:** Failover routing is the correct choice whenever a scenario describes a strict active/passive (primary/secondary) relationship with automatic, health-check-driven all-or-nothing traffic redirection.

---

### Question 11 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An online learning platform runs three independent Kubernetes-style microservice clusters, each in a different AWS Region, all serving the exact same content and all considered production-grade and equally capable of serving any user. The company wants basic DNS-level load spreading across all three clusters along with automatic exclusion of any cluster that fails a health check, but has a very small operational budget and explicitly does not want to pay for or manage a global load balancing service like AWS Global Accelerator or run a full Route 53 Traffic Flow policy record — they want the simplest native DNS mechanism available.
**Options:**
A. A multivalue answer routing policy record listing all three cluster endpoints, each with an associated Route 53 health check.
B. A weighted routing policy with equal weights (33/33/34) and no health checks configured.
C. AWS Global Accelerator with three endpoint groups, one per cluster.
D. A latency-based routing policy across all three clusters with Traffic Flow enabled for visualization.
**Correct answer(s):** A
**Why correct:** Multivalue answer routing is Route 53's lightweight, native mechanism for returning multiple healthy IP addresses per DNS query (up to eight), each independently health-checked, providing basic DNS-level load spreading and automatic exclusion of failed endpoints — matching the stated need for simplicity and low operational/cost overhead without adopting a full traffic-management product.
**Why each wrong option is wrong:** B is wrong because without health checks configured, an unhealthy cluster would keep receiving its share of traffic indefinitely, failing the "automatic exclusion of any cluster that fails a health check" requirement; C is wrong because Global Accelerator is explicitly called out in the scenario as something the team does not want to pay for or manage; D is wrong because Traffic Flow is a paid, policy-record-based visual traffic management feature the scenario explicitly wants to avoid, and latency-based routing alone (without multivalue's multiple-IP-per-response behavior) returns only a single best endpoint rather than DNS-level spreading across all three.
**Trigger words:** "basic DNS-level load spreading," "automatic exclusion of any cluster that fails a health check," "very small operational budget," "simplest native DNS mechanism."
**Underlying architectural principle:** Multivalue answer routing is the low-cost, health-check-aware, DNS-only alternative to a true load balancer or traffic-management service when basic multi-endpoint spreading is all that's required.

---

### Question 12 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A financial services firm runs its trading platform across two AZs within a single region: two ALBs (one per AZ, intentionally not sharing a single ALB to reduce blast radius), two separate Auto Scaling groups, and two independent RDS Multi-AZ clusters, with no data or traffic sharing between the two "cells." An architect reviewing the design flags that Route 53 currently has a single simple routing record pointing only at the AZ-A ALB, meaning all customer traffic depends entirely on AZ-A's ALB being reachable, even though the AZ-B cell is fully built and idle. The firm wants both cells actively used under normal conditions to maximize the value of the AZ-B investment, while still shifting fully away from either cell if that cell's ALB becomes unhealthy.
**Options:**
A. Replace the single simple routing record with a failover routing policy that treats one ALB as primary and the other as secondary, each behind its own Route 53 health check.
B. Replace the single simple routing record with a weighted routing policy (e.g., 50/50) across both ALBs, each behind its own Route 53 health check, so an unhealthy ALB's weight is effectively removed from consideration.
C. Keep the simple routing record as is, since ALBs are already highly available by default and DNS-level distribution isn't necessary.
D. Add a second simple routing record for the AZ-B ALB with the same record name, relying on round-robin behavior between the two records.
**Correct answer(s):** B
**Why correct:** Weighted routing with health checks on each weighted record lets Route 53 actively distribute traffic across both ALBs under normal conditions (satisfying "both cells actively used"), while automatically excluding a record from answers once its associated health check fails, achieving the "shift fully away from either cell if... unhealthy" requirement — matching an active/active goal rather than the active/passive model of failover routing.
**Why each wrong option is wrong:** A is wrong because failover routing is an active/passive model — it sends 100% of traffic to the primary and ignores the secondary entirely as long as the primary is healthy, which fails the stated goal of actively using both cells simultaneously; C is wrong because a single simple routing record pointed at only one AZ's ALB makes that specific ALB a Route-53-level single point of failure regardless of how resilient the ALB itself is internally, since no DNS answer ever points anywhere else; D is wrong (and not actually achievable as described) because Route 53 does not allow two separate resource record sets with the same name and type under the Simple routing policy — Simple routing supports only a single record per name/type (a lone Simple record can list multiple IP values, which gives basic client-side round-robin, but with no per-value health-check exclusion). Getting weighted, health-check-driven distribution across two named endpoints requires switching to the Weighted (or Multivalue Answer) routing policy specifically — which is exactly what B does.
**Trigger words:** "single simple routing record pointing only at the AZ-A ALB," "both cells actively used under normal conditions," "shifting fully away from either cell if that cell's ALB becomes unhealthy."
**Underlying architectural principle:** A single DNS record pointing at one resource reintroduces a single point of failure even when that resource is itself internally redundant; active/active distribution with health-check-based exclusion calls for weighted (or latency-based) routing, not failover routing.

---

### Question 13 [Priority: P0] [Difficulty: Easy] [Type: Multiple-Response]
**Scenario:** A three-tier application currently has the following architecture: an Application Load Balancer spanning two AZs, an Auto Scaling group spanning two AZs, a single RDS instance (no Multi-AZ) in one AZ, and a single NAT Gateway in one AZ shared by both AZs' private subnets. The team has been asked to identify which elements currently represent single points of failure that could cause an outage if their specific AZ fails.
**Options:**
A. The single RDS instance with no Multi-AZ configuration.
B. The single NAT Gateway shared across both AZs.
C. The Application Load Balancer, since it only has one DNS name.
D. The Auto Scaling group, since it only has one name/identifier.
E. The two-AZ span of the Auto Scaling group itself.
**Correct answer(s):** A, B
**Why correct:** The RDS instance (A) and the single shared NAT Gateway (B) are both confined to a single AZ, meaning the loss of that specific AZ takes down database access and outbound internet access for the entire application, regardless of how healthy the other AZ's resources are — these are the genuine single points of failure in this design.
**Why each wrong option is wrong:** C is wrong because an ALB is a managed, inherently multi-AZ service when configured to span multiple AZs (as stated here) — having one DNS name does not make it AZ-bound the way a NAT Gateway or standalone EC2/RDS instance is; D is wrong for the same reason — having a single logical ASG name is irrelevant to fault tolerance, since the ASG's actual EC2 instances are correctly spread across two AZs; E is wrong because spanning two AZs is the correct, resilient design for an Auto Scaling group — it is the described SPOF-free part of the architecture, not a SPOF itself.
**Trigger words:** "single RDS instance (no Multi-AZ)," "single NAT Gateway shared across both AZs," "single points of failure... if their specific AZ fails."
**Underlying architectural principle:** A resource confined to a single AZ (regardless of the rest of the stack's redundancy) reintroduces an AZ-level single point of failure; managed multi-AZ services like a correctly configured ALB or ASG are not automatically SPOFs just because they have one logical name.

---

### Question 14 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An architect is redesigning a legacy payment-processing platform that currently has these known issues: (1) a single Elastic IP is attached to a single standalone EC2 instance running the payment gateway software, with no load balancer or Auto Scaling group in front of it; (2) the RDS database is single-AZ; (3) all application logs are written only to that instance's local EBS volume with no shipping to a durable store; (4) DNS currently uses a single simple routing record pointing directly at the instance's Elastic IP. Which two changes would most directly eliminate single points of failure described here?
**Options:**
A. Replace the standalone EC2 instance with an Auto Scaling group (min size ≥ 2, spanning multiple AZs) behind an Application Load Balancer, updating the Route 53 record to alias to the ALB.
B. Enable RDS Multi-AZ for the database.
C. Increase the standalone EC2 instance's size to a larger instance type to reduce the chance of failure.
D. Configure the EC2 instance to write logs to a second local EBS volume in addition to the first, for redundancy.
E. Switch the Route 53 record from simple routing to latency-based routing, still pointing at the same single Elastic IP.
**Correct answer(s):** A, B
**Why correct:** Option A removes the single-instance, single-Elastic-IP dependency entirely by introducing a multi-AZ Auto Scaling group behind an ALB, which also resolves the DNS single-point-of-failure issue since the record now points at a resilient, multi-target ALB rather than one static IP; option B removes the single-AZ database as a point of failure via automatic, synchronous standby failover.
**Why each wrong option is wrong:** C only makes a single point of failure "bigger and presumably more reliable per-unit," but a single, larger instance is still exactly one instance — it remains a complete SPOF if that one instance or its AZ fails; D keeps logs durable only within the same single instance/AZ, so losing that instance or its AZ still risks losing the logs, and it does nothing about the compute, database, or DNS SPOFs; E is a routing-policy change with no effect at all, since it's explicitly stated to still point at the exact same single Elastic IP/instance — the underlying SPOF is untouched.
**Trigger words:** "single Elastic IP is attached to a single standalone EC2 instance," "no load balancer or Auto Scaling group," "RDS database is single-AZ," "most directly eliminate single points of failure."
**Underlying architectural principle:** Eliminating a single point of failure requires actually introducing redundant, independently-failing resources (multiple instances/AZs) — resizing, duplicating within the same failure domain, or changing an unrelated routing policy does not remove the underlying SPOF.

---

### Question 15 [Priority: P2] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A logistics company runs a fleet of IoT gateway devices that establish long-lived TCP connections to a backend ingestion service in AWS to stream sensor telemetry continuously. The ingestion service must (1) preserve the original client IP for downstream device-authentication logic that keys off IP reputation, (2) support a static IP address per AZ that the device firmware can safely allowlist in restrictive corporate firewalls, and (3) handle extremely high and bursty connection volumes with minimal added latency. The team is deciding between load balancer types and is also considering whether any Route 53 configuration changes are needed.
**Options:**
A. Use a Network Load Balancer in front of the ingestion service, since NLB provides static IP addresses per AZ (or supports Elastic IPs) and preserves the original client source IP by default.
B. Use an Application Load Balancer instead, since ALB automatically preserves client IP in the `X-Forwarded-For` header, which is functionally equivalent for this use case.
C. Rely on NLB's Layer 4 design and connection-handling to absorb extremely high, bursty long-lived TCP connection volume with low added latency.
D. Add a Route 53 latency-based routing policy across multiple NLBs in different regions, since this is required for any high-throughput ingestion workload.
E. Assume ALB's `X-Forwarded-For` header requires no application-side code changes to parse compared to using the raw source IP with NLB.
**Correct answer(s):** A, C
**Why correct:** NLB is the correct load balancer here because it natively supports static/Elastic IPs per AZ (satisfying firewall allowlisting) and preserves the true client source IP at the network layer by default (satisfying IP-reputation logic) — option A; and NLB's Layer 4 architecture is specifically built to handle very high volumes of long-lived TCP connections with minimal latency overhead — option C.
**Why each wrong option is wrong:** B is wrong because relying on the `X-Forwarded-For` header from an ALB is not "functionally equivalent" to raw source IP preservation — it requires the application to trust and correctly parse a header (which can be more error-prone, especially behind additional proxies) rather than reading the connection's actual source IP directly, and ALB doesn't offer the same static-IP-per-AZ guarantee that firewall allowlisting needs; D is wrong because nothing in the scenario requires multi-region deployment or latency-based routing — that's an unjustified architectural addition not supported by any stated requirement; E is wrong because it inverts the actual trade-off — using NLB with the real source IP typically requires zero application-side parsing changes, whereas relying on `X-Forwarded-For` from an ALB does require application code to extract and trust that header correctly.
**Trigger words:** "preserve the original client IP," "static IP address per AZ... allowlist," "extremely high and bursty connection volumes with minimal added latency," "long-lived TCP connections."
**Underlying architectural principle:** NLB's Layer 4 design, native client-IP preservation, and static/Elastic IP support make it the correct choice over ALB whenever firewall allowlisting or true source-IP-based logic (rather than a forwarded header) is required alongside high-throughput, low-latency connection handling.

---

### Question 16 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A multinational retailer operates six regional Application Load Balancers behind Route 53, one per continent-scale market, and currently uses a geolocation routing policy mapping each continent to its regional ALB — with no default ("*") record configured to catch unmapped or failed-over locations. During a major shopping event, the South America ALB begins failing its Route 53 health check due to a regional capacity issue, and the team is alarmed to discover that South American users are now getting no valid DNS answer at all for the domain (queries from that location go unresolved) instead of being routed anywhere, even though four of the other five regional ALBs are healthy and technically capable of absorbing overflow traffic.
**Options:**
A. This is expected geolocation routing behavior without a fallback in place: unlike latency-based or weighted routing, geolocation records with an associated failing health check and no alternate resource for that location will return no answer rather than automatically overflowing traffic elsewhere; the fix is to add explicit failover behavior (e.g., a secondary geolocation record for South America pointing to another healthy regional ALB, or combining with a failover routing policy).
B. This indicates Route 53 itself is malfunctioning, since DNS should never fail to resolve as long as any healthy endpoint exists anywhere in the account.
C. Geolocation routing automatically overflows to the geographically nearest healthy region by default, so this must be a misconfigured health check threshold rather than a routing behavior issue.
D. The fix is to switch entirely to a single global Simple routing record, since it would guarantee an answer is always returned.
**Correct answer(s):** A
**Why correct:** Geolocation routing strictly maps a location to a specific record/resource; if that specific record's associated health check fails and there is no explicit alternate/failover resource configured for that same location, Route 53 will not automatically substitute a different geographic region's healthy resource — the location simply gets no valid DNS answer, which matches the described behavior, and the correct remediation is to add an explicit fallback (a secondary record or a nested failover configuration) for that location. (Note: had a default/"*" record been configured, Route 53 *would* automatically fall back to it once South America's record failed its health check — a default record is itself a valid form of fallback. The root cause here is specifically that no default record and no location-specific secondary/failover record exist for South America.)
**Why each wrong option is wrong:** B is wrong because this is documented, expected behavior of geolocation routing's location-to-resource binding, not a Route 53 malfunction — the service is behaving correctly according to its configured policy, which lacks a fallback; C is wrong because geolocation routing does not have any built-in "nearest healthy region" overflow behavior — that kind of dynamic reassignment is not part of how geolocation resolves failing health checks, so no such default exists to be "misconfigured"; D is wrong because a single global simple record would indeed always return an answer, but it would send 100% of global traffic — including from every continent — to one ALB, destroying the entire purpose of the regional geolocation design and creating a severe overload/latency problem for everyone.
**Trigger words:** "South America ALB begins failing its... health check," "South American users are now getting no valid DNS answer... instead of being routed anywhere," "four of the other five regional ALBs are healthy."
**Underlying architectural principle:** Geolocation routing does not automatically fail over to a different geographic region's resource on health-check failure; the only built-in fallback is a configured default ("*") record (or a nested failover configuration for that location). Production geolocation designs need one of those explicit fallbacks for each location to avoid unresolvable DNS answers during a regional outage.

---

### Question 17 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A B2B SaaS company runs its API on ECS Fargate tasks registered to target groups behind an Application Load Balancer, spread across three AZs. Customers connect over HTTPS, and several enterprise customers require the ability to know they are always talking to one of a small, fixed set of IP addresses so they can configure narrow allowlist rules in their own corporate firewalls, since their security teams refuse to allowlist a broad or changing CIDR range. The company does not want to change its load balancer type if it can avoid an architectural rewrite, since ALB's path-based routing across several microservice target groups is a hard requirement.
**Options:**
A. Attach an AWS Global Accelerator in front of the existing ALB, giving customers a small set of static Anycast IP addresses to allowlist while keeping the ALB and all of its Layer 7 routing behavior unchanged.
B. Request that ALB be assigned static Elastic IP addresses directly, since ALB supports Elastic IP assignment in the same way NLB does.
C. Replace the ALB entirely with an NLB to get static IP addresses, and reimplement path-based routing using target group weighted rules on the NLB.
D. Tell the enterprise customers to instead allowlist the entire published AWS IP address range for the region.
**Correct answer(s):** A
**Why correct:** Global Accelerator provisions a small, fixed set of static Anycast IP addresses that can sit in front of an existing ALB without changing the ALB itself, letting the company keep all of its required Layer 7 path-based routing while giving enterprise customers the small, stable IP set their firewalls need.
**Why each wrong option is wrong:** B is wrong because, unlike NLB, ALB does not support direct assignment of static Elastic IP addresses to its listener — its IP addresses can change over time; C is wrong because it would require abandoning ALB's Layer 7 path-based routing capability entirely, which the scenario explicitly states is a hard requirement, and NLB does not perform HTTP path-based routing the way ALB does; D is an operationally unreasonable answer since AWS regional IP ranges are broad, large, and shared across countless AWS customers, which defeats the purpose of a narrow allowlist and is not something enterprise security teams would accept.
**Trigger words:** "small, fixed set of IP addresses," "refuse to allowlist a broad or changing CIDR range," "does not want to change its load balancer type," "path-based routing... is a hard requirement."
**Underlying architectural principle:** AWS Global Accelerator provides static Anycast IPs in front of existing load balancers (including ALB) without requiring a load-balancer-type change, making it the standard fix when static-IP allowlisting must coexist with ALB's Layer 7 features.

---

### Question 18 [Priority: P2] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An architect is reviewing a proposed multi-region active-active e-commerce design: production traffic is served simultaneously from us-east-1 and eu-west-1, each with its own ALB, ASG spanning three AZs, and DynamoDB Global Tables for cart/session data. Route 53 uses a latency-based routing policy across both regional ALBs, each with an associated health check. The architect wants to confirm which two statements correctly describe remaining resilience considerations in this design, beyond what's already handled by the components described.
**Options:**
A. If an entire region's ALB and every AZ's targets become unreachable, Route 53's health check on that region's latency-based record will fail, and Route 53 will stop returning that region's ALB as an answer, directing new DNS resolutions to the healthy region.
B. Because DynamoDB Global Tables replicate asynchronously, concurrent writes to the same item key from both regions can conflict and are resolved via last-writer-wins, which the application must account for if strict per-item write consistency across regions is required.
C. Latency-based routing guarantees zero data loss for in-flight transactions during a regional failure, since Route 53 will instantly redirect all affected users before any request can fail.
D. Because each region's ALB spans three AZs, no additional Route 53-level health checking is necessary for the ALBs themselves — only for the individual EC2 targets.
E. Since traffic is being served from two regions simultaneously, this design has already achieved zero RTO and zero RPO under all failure scenarios by definition.
**Correct answer(s):** A, B
**Why correct:** A correctly describes how latency-based routing combined with per-record health checks provides regional-level automatic failover for new DNS resolutions once a region becomes fully unreachable; B correctly identifies the well-known DynamoDB Global Tables trade-off — asynchronous cross-region replication with last-writer-wins conflict resolution — which is a real remaining consideration the application layer must handle, not something the infrastructure resolves automatically.
**Why each wrong option is wrong:** C overstates DNS-based failover — DNS record TTLs, client-side caching, and already-in-flight requests to the failing region mean some requests can still fail or experience delay before traffic fully shifts, so "zero data loss" and "instantly" are not accurate guarantees of latency-based routing; D is wrong because Route 53 health checks are still valuable at the ALB/region level to detect broader regional-level failures (e.g., DNS/network path issues to the region) that individual target health checks inside the ALB wouldn't necessarily surface to Route 53 — the two health-check layers serve different purposes and neither one replaces the need for the other; E is wrong because active-active multi-region with asynchronous replication (as this design uses for DynamoDB Global Tables) does not achieve "zero RTO and zero RPO under all failure scenarios" — there is still replication lag and conflict-resolution behavior, and DNS-based failover itself is not instantaneous for every client.
**Trigger words:** "DynamoDB Global Tables," "latency-based routing policy... each with an associated health check," "remaining resilience considerations... beyond what's already handled."
**Underlying architectural principle:** Even a well-designed active-active multi-region architecture retains real resilience trade-offs — DNS-based failover is not instantaneous or loss-free, and asynchronously replicated multi-region data stores still require application-level handling of write conflicts.

---
