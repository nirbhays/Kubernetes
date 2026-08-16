# SAA-C03 Practice Questions — Domain 3: Design High-Performing Architectures (24%)
Focus: CloudFront caching/origin selection · CloudFront vs Global Accelerator · Direct Connect vs VPN for performance · Transit Gateway vs Peering at scale · Route 53 latency-based routing

Original practice content for study purposes only — these are **not** real AWS exam questions and do not reproduce any leaked/dumped material. Based on current (2026) AWS service behavior and the official SAA-C03 exam guide scope.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A publishing company hosts its blog's static assets (HTML, CSS, JS, and article images) in a single S3 bucket in `us-east-1`. Readers in Europe, South America, and Southeast Asia report slow page-load times, while the company's small operations team has no budget for managing additional infrastructure. Traffic is 100% read-heavy and the content changes only a few times per day. The company wants the fastest way to reduce global latency with the least operational overhead.
**Options:**
A. Put an Amazon CloudFront distribution in front of the S3 bucket and enable caching for the static asset paths.
B. Enable S3 Cross-Region Replication to buckets in `eu-west-1`, `sa-east-1`, and `ap-southeast-1`, and use Route 53 latency-based routing across the bucket endpoints.
C. Enable S3 Transfer Acceleration on the bucket so global readers download assets faster.
D. Move the S3 bucket's contents to Amazon EFS and mount it from EC2 instances in each target region.
**Correct answer(s):** A
**Why correct:** CloudFront caches the read-heavy, infrequently-changing static content at edge locations worldwide with a single configuration change, directly solving global latency for a caching-shaped problem with minimal ongoing operations.
**Why each wrong option is wrong:** B requires managing multiple replicated bucket copies and a routing layer for what is fundamentally a caching problem, adding operational overhead the company explicitly doesn't want; C, S3 Transfer Acceleration optimizes the network path for individual, direct transfers to and from a bucket over long distances — it does not cache objects at edge locations, so every request still travels all the way back to the origin bucket, meaning it does nothing to solve the repeated-read, many-concurrent-reader latency problem the way CloudFront's edge caching does; D, EFS is a regional POSIX file system for EC2 workloads, not a global content delivery mechanism, and would require running and patching EC2 fleets in every region.
**Trigger words:** "static assets," "read-heavy," "changes only a few times per day," "least operational overhead."
**Underlying architectural principle:** When the requirement is "cache read-heavy static content closer to global users," CloudFront is almost always the lowest-effort, purpose-built answer over replicating storage or provisioning compute.

---

### Question 2 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A SaaS company runs an identical, fully independent stack (ALB + Auto Scaling EC2 fleet + RDS) in `us-east-1`, `eu-west-1`, and `ap-southeast-1`. There is no legal or data-residency requirement dictating which region serves which customer — the sole goal is that every user's browser is directed to whichever regional endpoint currently gives them the best network performance, and this should adapt automatically if network conditions change.
**Options:**
A. Create Route 53 latency-based routing records pointing to each regional ALB, with health checks enabled on each record.
B. Create Route 53 geolocation routing records mapping each continent to its nearest regional ALB.
C. Create Route 53 weighted routing records with an even 33/33/34 split across the three ALBs.
D. Create Route 53 failover routing with `us-east-1` as primary and the other two regions as secondary.
**Correct answer(s):** A
**Why correct:** Latency-based routing continuously uses AWS's measured network latency data between users and each region to return the endpoint with the best performance for that specific resolver, which is exactly "best network performance, adapts automatically."
**Why each wrong option is wrong:** B routes strictly by the geographic location of the query, which correlates with but does not guarantee the lowest-latency path (and there's no stated compliance/localization reason to force it); C splits traffic by a fixed arbitrary ratio with no regard to actual performance; D is designed for active/passive disaster recovery, not for concurrently optimizing performance across three active regions.
**Trigger words:** "no legal or data-residency requirement," "best network performance," "adapts automatically."
**Underlying architectural principle:** When the goal is purely speed (not compliance or arbitrary traffic splitting), Route 53 latency-based routing is the routing policy purpose-built for directing users to their fastest available endpoint.

---

### Question 3 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A game studio runs a real-time multiplayer shooter where game clients communicate with regional game servers over a custom UDP protocol. Players worldwide report inconsistent latency and occasional multi-second connection drops during regional network events. The studio wants a solution that improves and stabilizes the network path to the nearest healthy regional deployment and provides fast, automatic rerouting away from an unhealthy region — all without changing the client-side UDP protocol.
**Options:**
A. Deploy AWS Global Accelerator in front of Network Load Balancers in each region, with health checks configured on the endpoint groups.
B. Deploy an Amazon CloudFront distribution in front of the regional game servers.
C. Switch to Route 53 latency-based routing with a very low DNS TTL for the game server domain.
D. Add an Application Load Balancer in each region and rely on cross-zone load balancing.
**Correct answer(s):** A
**Why correct:** Global Accelerator operates at the network layer, supports TCP and UDP, routes traffic over the AWS global backbone to the closest healthy regional endpoint, and reroutes traffic to the next healthy endpoint quickly once a health check fails — with no DNS involvement at all — matching every stated requirement without touching the client protocol.
**Why each wrong option is wrong:** B, CloudFront is an HTTP(S) content delivery service and does not support arbitrary UDP traffic; C, DNS-based routing failover is limited by resolver caching and TTL expiry, which explains the multi-second drops the studio is already experiencing, not a fix for them; D, an ALB is HTTP(S)-only (Layer 7) and provides no cross-region routing or global static entry point on its own.
**Trigger words:** "custom UDP protocol," "fast, automatic rerouting," "without changing the client-side protocol."
**Underlying architectural principle:** For non-HTTP or latency-sensitive TCP/UDP workloads needing network-layer acceleration and fast, DNS-independent regional failover, Global Accelerator is the tool — CloudFront and DNS-based routing are not substitutes for it.

---

### Question 4 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company serves product images through a CloudFront distribution backed by an S3 bucket in `us-east-1`. After a regional S3 disruption caused image delivery failures for several hours, the company wants CloudFront to automatically start serving images from a secondary S3 bucket in `us-west-2` (kept in sync via replication) whenever the primary origin returns errors, with no manual intervention and no DNS changes required.
**Options:**
A. Configure a CloudFront origin group containing both S3 buckets as primary and secondary origins, with failover triggered on specified HTTP status codes.
B. Create a Route 53 health check on the primary S3 bucket's website endpoint and configure DNS failover to the secondary bucket.
C. Enable S3 Cross-Region Replication between the buckets and manually update the CloudFront origin setting during an outage.
D. Put both S3 buckets behind an AWS Global Accelerator endpoint group with health checks.
**Correct answer(s):** A
**Why correct:** CloudFront origin groups are purpose-built for this exact pattern — CloudFront automatically retries the secondary origin when the primary returns the configured failure status codes, requiring no DNS changes or manual action.
**Why each wrong option is wrong:** B introduces a DNS-layer failover mechanism that duplicates and conflicts with CloudFront's own origin resolution, and is not how CloudFront origin failover is implemented; C explicitly requires manual intervention, which the company wants to eliminate; D, Global Accelerator's endpoint groups target ALBs, NLBs, EC2 instances, or Elastic IPs — not S3 buckets — so it cannot front this origin at all.
**Trigger words:** "automatically start serving," "no manual intervention," "no DNS changes."
**Underlying architectural principle:** Origin failover for S3-backed CloudFront distributions is handled natively with CloudFront origin groups, not through DNS-layer failover or manual origin swaps.

---

### Question 5 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A manufacturing company must connect a new factory's sensor network to its AWS VPC for near-real-time analytics. The pilot must be live within two weeks. Leadership has already approved a plan to move to a dedicated 10 Gbps connection for full production traffic roughly six months from now, once the pilot proves value, and wants the pilot approach to not create rework later.
**Options:**
A. Establish an AWS Site-to-Site VPN connection now for the pilot, and in parallel initiate the Direct Connect order so the dedicated connection is ready ahead of the production rollout.
B. Delay the pilot launch until the Direct Connect connection is provisioned, to avoid migrating between connectivity methods later.
C. Use a Direct Connect Gateway immediately, since it can be provisioned within the two-week window.
D. Connect the factory to the VPC using VPC Peering as a temporary bridge until Direct Connect is ready.
**Correct answer(s):** A
**Why correct:** Site-to-Site VPN can be stood up within hours to meet the two-week pilot deadline, and since Direct Connect provisioning routinely takes weeks to months, starting that order in parallel now is the only way to have the dedicated connection ready in roughly six months without idle lead time.
**Why each wrong option is wrong:** B fails the two-week deadline entirely by waiting on a circuit that isn't provisioned yet; C is a distractor — Direct Connect Gateway only aggregates/extends existing Direct Connect connections across VPCs or regions, it does not shorten the physical circuit lead time of the underlying Direct Connect connection itself; D, VPC Peering connects two VPCs to each other, it has no role in connecting an on-premises factory network to a VPC.
**Trigger words:** "must be live within two weeks," "roughly six months from now," "not create rework later."
**Underlying architectural principle:** When there is real time pressure but a longer-term dedicated-connection goal, start VPN immediately for the interim need while placing the Direct Connect order in parallel, rather than waiting on DX's multi-week-to-month lead time.

---

### Question 6 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A large enterprise has 25 departmental VPCs today and expects to add several more each quarter. Every VPC must be able to reach every other VPC, and all VPCs must route their internet-bound traffic through a shared central inspection VPC running a fleet of security appliances. The networking team wants a design that keeps management overhead roughly flat as more VPCs are added.
**Options:**
A. Deploy an AWS Transit Gateway, attach every departmental VPC and the inspection VPC to it, and configure route tables for transitive routing through the inspection VPC.
B. Create full-mesh VPC Peering connections between every pair of the 25 VPCs plus the inspection VPC.
C. Create VPC Peering connections from every departmental VPC to a single central "hub" VPC, and route inter-VPC traffic through that hub.
D. Expose the inspection VPC's security appliances to all other VPCs using AWS PrivateLink endpoint services.
**Correct answer(s):** A
**Why correct:** Transit Gateway is a managed regional routing hub that natively supports transitive routing, so adding a new VPC only requires one new attachment (not connections to every existing VPC), keeping operational effort flat as the environment scales.
**Why each wrong option is wrong:** B, a full mesh of 26 VPCs requires 325 individual peering connections (n(n-1)/2) and grows quadratically with every new VPC, the opposite of flat overhead; C looks like a shortcut but VPC Peering is explicitly non-transitive, so spoke VPCs peered only to the hub still cannot reach each other or route through the hub for internet egress; D, PrivateLink exposes a specific service endpoint one-way to consumers, it is not a mechanism for full bidirectional network routing or shared internet egress across many VPCs.
**Trigger words:** "every VPC must be able to reach every other VPC," "route through a shared central inspection VPC," "management overhead roughly flat."
**Underlying architectural principle:** Once transitive routing or more than a handful of VPCs are involved, Transit Gateway is the scalable answer — VPC Peering's non-transitive nature makes hub-and-spoke peering designs a trap, not a solution.

---

### Question 7 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A video streaming company sells premium content that must only be viewable by subscribers with an active, paid session, delivered through its existing CloudFront distribution. Subscribers' IP addresses change frequently (mobile networks, VPNs), so IP-based restriction is not viable, and each access grant must expire automatically a few minutes after the backend issues it.
**Options:**
A. Have the application backend generate CloudFront signed URLs (or signed cookies) with a short expiration time after validating the subscriber's session.
B. Add a bucket policy on the S3 origin restricting access to the IP address ranges of known subscribers.
C. Restrict the CloudFront distribution to a smaller price class covering only the subscriber base's regions.
D. Add an AWS WAF geo-match rule on the distribution to block requests from countries with no subscribers.
**Correct answer(s):** A
**Why correct:** CloudFront signed URLs/cookies are generated per authenticated session with a defined, short expiration, giving exactly the time-limited, per-subscriber access control the scenario requires without depending on client IP addresses.
**Why each wrong option is wrong:** B is explicitly ruled out by the scenario since subscriber IPs change frequently and can't be reliably enumerated; C, price class only controls which edge locations serve the distribution for cost purposes, it has no effect on who is authorized to view content; D, geo-blocking filters by country, not by individual subscriber authentication or time-limited access, so a non-subscriber in an allowed country could still view the content.
**Trigger words:** "must only be viewable by subscribers with an active, paid session," "IP addresses change frequently," "expire automatically."
**Underlying architectural principle:** Per-user, time-limited content access on CloudFront is achieved with signed URLs/cookies tied to application-level authentication, not with network-level controls like IP allow-lists or geo-blocking.

---

### Question 8 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A B2B software vendor's enterprise customers require IP allow-listing on their own corporate firewalls before any traffic is permitted to the vendor's application. The application runs behind Application Load Balancers in two AWS Regions and serves both standard HTTPS traffic and a custom TCP protocol on port 8443 used by a legacy client. The vendor needs a small, fixed set of IP addresses customers can whitelist once, that also route each customer to whichever region is currently healthy and closest.
**Options:**
A. Front both regional ALBs with AWS Global Accelerator and give customers the accelerator's static anycast IP addresses to whitelist.
B. Put a CloudFront distribution in front of both ALBs and give customers CloudFront's published IP ranges to whitelist.
C. Use Route 53 latency-based routing and give customers the DNS name to resolve, instructing them to whitelist whatever IP it currently returns.
D. Allocate Elastic IP addresses and associate them directly with each regional Application Load Balancer for customers to whitelist.
**Correct answer(s):** A
**Why correct:** Global Accelerator provides a small set of static anycast IP addresses that remain constant regardless of backend or regional changes, supports both HTTPS and arbitrary TCP protocols like the custom port 8443 traffic, and uses health checks to route each customer to the nearest healthy region.
**Why each wrong option is wrong:** B, CloudFront is HTTP(S)-only and cannot carry the custom TCP protocol on port 8443, and its edge IP ranges are large, shared, and not intended as a small fixed allow-list; C, DNS-resolved IPs can change over time and vary by resolver/location, making a stable one-time firewall whitelist impossible; D, Application Load Balancers do not support direct association of Elastic IP addresses (only Network Load Balancers do), so this option is not technically achievable as described.
**Trigger words:** "fixed set of IP addresses," "custom TCP protocol," "corporate firewalls," "closest healthy region."
**Underlying architectural principle:** When customers need a small number of static IPs to whitelist for non-HTTP or mixed-protocol traffic with automatic regional failover, Global Accelerator's anycast IPs are the purpose-built answer.

---

### Question 9 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A financial services firm connects its data center to AWS using a single AWS Direct Connect connection at one Direct Connect location. An internal resiliency review flagged this as a single point of failure: the firm must be able to tolerate the loss of the Direct Connect connection itself, and even the loss of that entire Direct Connect location's facility, without a full multi-day outage to its AWS connectivity. Budget constraints rule out building a second full 10 Gbps dedicated connection with matching bandwidth immediately, but some added resiliency this quarter is required. **(Choose TWO.)**
**Options:**
A. Provision a second Direct Connect connection at a different Direct Connect location.
B. Configure an AWS Site-to-Site VPN connection as a backup path with BGP-based failover to Direct Connect.
C. Increase the bandwidth of the existing Direct Connect connection.
D. Enable a Direct Connect Gateway on the existing connection.
E. Deploy a NAT Gateway in each Availability Zone the VPC uses.
**Correct answer(s):** A, B
**Why correct:** A second Direct Connect connection at a different physical location removes the single-location dependency, and a Site-to-Site VPN backup with BGP failover provides an independent, lower-cost path that survives the loss of the Direct Connect location entirely — together they give layered resiliency within this quarter's budget.
**Why each wrong option is wrong:** C only increases throughput on the same single connection and location, it does nothing to address the loss of that connection or facility; D, Direct Connect Gateway is used to connect one Direct Connect connection to multiple VPCs or regions, it does not add redundancy to the underlying physical connection; E, NAT Gateways manage outbound internet access for private subnets and have no relationship to on-premises-to-AWS hybrid connectivity resiliency.
**Trigger words:** "single point of failure," "tolerate the loss of the Direct Connect connection... or the location," "some added resiliency this quarter."
**Underlying architectural principle:** Direct Connect resiliency is achieved by adding physically diverse connections and/or a VPN backup path — not by scaling bandwidth or using constructs like Direct Connect Gateway that solve a different problem (multi-VPC/region reach, not availability).

---

### Question 10 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A regional online retailer confirms via analytics that essentially all of its customers are located in the United States, Canada, and Western Europe. Its product catalog site is served through CloudFront in front of S3, and a recent cost review found the distribution is incurring charges for edge locations in South America, Asia Pacific, Australia, and the Middle East where it has effectively zero legitimate traffic. The retailer wants to reduce CloudFront cost without changing its caching behavior or degrading performance for its actual customer base.
**Options:**
A. Change the CloudFront distribution's price class to restrict it to North America and Europe edge locations only.
B. Replace CloudFront with AWS Global Accelerator to reduce delivery costs.
C. Reduce the cache TTL on the distribution's static asset behaviors to lower cost.
D. Add an AWS WAF geo-match rule to block requests originating from regions outside North America and Europe.
**Correct answer(s):** A
**Why correct:** CloudFront's price class setting directly controls which set of edge locations are used to serve the distribution, and restricting it to the regions covering the actual customer base reduces cost precisely because requests are no longer served (and billed) from unused higher-cost edge location tiers, with no change to caching behavior.
**Why each wrong option is wrong:** B, Global Accelerator is a network-path optimization service for TCP/UDP workloads with its own separate pricing model, it is not a caching replacement and would not reduce this specific CloudFront edge-location cost driver; C, lowering TTL causes more requests to fall through to the origin, increasing origin fetches and data transfer cost — the opposite of the desired outcome, and it doesn't address unused edge locations at all; D, geo-blocking with WAF filters requests for security/access-control reasons and could incorrectly block legitimate travelers or VPN users, and it is not how CloudFront edge-location billing works, so it does not directly control which price-tier edge locations serve traffic.
**Trigger words:** "essentially all customers... United States, Canada, and Western Europe," "reduce CloudFront cost," "without... degrading performance for its actual customer base."
**Underlying architectural principle:** When a CloudFront audience is geographically concentrated, price class restriction is the direct cost lever — it is a distinct control from caching behavior (TTL) and from access control (WAF/geo-blocking).

---

### Question 11 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A multinational retailer runs identical order-processing APIs in `eu-west-1` and `us-east-1`. A new EU data-protection requirement mandates that all requests originating from EU member countries must always be served exclusively by the `eu-west-1` stack, with no exceptions, regardless of measured network conditions. All other users worldwide should simply be routed to whichever of the two regions currently gives them the best latency. The solution must use Amazon Route 53.
**Options:**
A. Configure Route 53 geolocation routing records mapping EU country codes to `eu-west-1`, and configure a "Default" geolocation record as an alias pointing to a separate set of latency-based routing records spanning both regions, to serve all other traffic.
B. Configure Route 53 latency-based routing records across both regions for all traffic, relying on `eu-west-1` naturally being lowest-latency for EU users.
C. Configure Route 53 geoproximity routing with a bias value favoring `eu-west-1` for European traffic.
D. Configure Route 53 weighted routing with a 50/50 split between the two regions and instruct EU clients to retry until they land on `eu-west-1`.
**Correct answer(s):** A
**Why correct:** Geolocation routing is the only Route 53 policy that guarantees a hard, compliance-grade mapping of EU country codes to `eu-west-1` regardless of network conditions, and aliasing the "Default" location to a separate latency-based record set correctly optimizes performance for every non-EU user without violating the EU rule.
**Why each wrong option is wrong:** B is a compliance violation risk — pure latency-based routing could, in an edge case (e.g., a network event degrading `eu-west-1`), route an EU user to `us-east-1`, which the "no exceptions" requirement forbids; C, geoproximity routing biases traffic by geographic distance with an adjustable weight, it does not provide a hard, guaranteed regional mapping the way geolocation does; D, weighted routing plus client-side retry logic provides no compliance guarantee at all and pushes an unreliable workaround onto every client.
**Trigger words:** "always be served exclusively," "no exceptions, regardless of measured network conditions," "all other users... best latency."
**Underlying architectural principle:** When a routing requirement is a hard compliance rule for a specific population and a performance optimization for everyone else, combine geolocation (for the guarantee) with latency-based routing as its default fallback — pure latency-based routing cannot provide compliance guarantees.

---

### Question 12 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A global enterprise operates VPCs in six AWS Regions. Within each region there are multiple departmental VPCs plus a shared network-inspection VPC, and every VPC in a region must be able to reach every other VPC in that same region as well as VPCs in all five other regions. The company plans to add new regions periodically as it expands and wants a design that avoids per-VPC-pair connections growing unmanageable as regions and VPCs are added.
**Options:**
A. Deploy a Transit Gateway in each of the six regions, attach that region's VPCs to its local Transit Gateway, and create a Transit Gateway peering connection between each pair of the six Transit Gateways (since TGW peering connections are point-to-point and non-transitive).
B. Create VPC Peering connections between every pair of VPCs across all six regions.
C. Deploy a single Transit Gateway in one region and attach every VPC across all six regions directly to it.
D. Merge all regional VPCs into a single VPC with subnets spanning multiple AWS Regions.
**Correct answer(s):** A
**Why correct:** A regional Transit Gateway per region joined by direct peering links between every pair of Transit Gateways is the standard scalable pattern — it gives transitive routing within each region and controlled connectivity between regions, and adding a new VPC to an existing region only requires one new attachment (no new peering links at all), while adding a new region only requires one new Transit Gateway plus peering links to the existing Transit Gateways — never a connection to every individual VPC.
**Why each wrong option is wrong:** B, full-mesh peering across dozens of VPCs in six regions grows quadratically and is explicitly non-transitive, making the "every VPC reaches every other VPC" requirement operationally unmanageable; C is not achievable as described — a Transit Gateway attachment must be to a VPC in the same region as the Transit Gateway, so VPCs in the other five regions cannot attach directly to one region's Transit Gateway; D, a VPC is a regional construct and cannot span multiple AWS Regions.
**Trigger words:** "six AWS Regions," "reach every other VPC... in all five other regions," "avoids per-VPC-pair connections growing unmanageable."
**Underlying architectural principle:** Multi-region, multi-VPC transitive connectivity at scale is achieved with one Transit Gateway per region joined by inter-region Transit Gateway peering, since Transit Gateway attachments are strictly regional and full-mesh peering does not scale.

---

### Question 13 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A media company's homepage and thumbnail images are static and already served successfully through an existing CloudFront distribution with a good cache-hit ratio. Separately, the company's live video streaming feature uses a custom low-latency UDP-based protocol served from EC2 media servers running in three regions. Viewers report inconsistent latency on live streams and no automatic failover when a region's media servers become unhealthy. The company wants to improve performance and add automatic regional failover specifically for the live-stream UDP component, without altering the CloudFront configuration that already works well for static assets. **(Choose TWO.)**
**Options:**
A. Place a Network Load Balancer per region in front of the EC2 media servers, then front all three NLBs with a single AWS Global Accelerator using health-check-based endpoint groups.
B. Migrate the live-stream UDP traffic to be served through the existing CloudFront distribution alongside the static content.
C. Configure the Global Accelerator endpoint groups' health checks to use the fastest supported check interval, minimizing the time needed to detect an unhealthy region and reroute traffic to a healthy one.
D. Increase the CloudFront distribution's cache TTL specifically for the video segment paths.
E. Add an S3 origin group with failover criteria to the CloudFront distribution for the live-stream content.
**Correct answer(s):** A, C
**Why correct:** Global Accelerator is designed exactly for this kind of non-HTTP, latency-sensitive, multi-region TCP/UDP workload — fronting regional NLBs with it (A) provides anycast entry and automatic health-check-driven routing to the closest healthy region, and tightening each endpoint group's health check interval to the fastest supported setting (C) minimizes the time it takes to detect a regional failure and reroute traffic, all independent of the already-working CloudFront distribution.
**Why each wrong option is wrong:** B is not technically possible — CloudFront serves HTTP(S) content and cannot carry a custom UDP protocol, and it would also risk disrupting the static-content configuration the company wants left alone; D only affects cacheable HTTP video segment delivery through CloudFront and has no bearing on the separate UDP live-stream path served from EC2; E, S3 origin groups are a CloudFront/S3 failover mechanism and are irrelevant to EC2-hosted, non-S3, UDP-based media servers.
**Trigger words:** "custom low-latency UDP-based protocol," "automatic regional failover," "without altering the CloudFront configuration."
**Underlying architectural principle:** CloudFront and Global Accelerator solve different problems and can coexist unmodified in the same architecture — CloudFront for cacheable HTTP(S) content, Global Accelerator for non-HTTP or latency-sensitive TCP/UDP traffic needing fast network-layer failover.

---

### Question 14 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A healthcare analytics company must transfer large volumes of protected health information (PHI) from an on-premises data center to a VPC for a nightly batch analytics job, sustaining roughly 10 Gbps of consistent throughput. Compliance requires that the connection never traverse the public internet and that all PHI be encrypted end-to-end in transit, with a strict nightly processing window that leaves no tolerance for unpredictable network jitter.
**Options:**
A. Provision a Direct Connect dedicated connection with a private virtual interface, and additionally establish an IPsec VPN connection over that Direct Connect connection to encrypt the traffic.
B. Provision a Direct Connect dedicated connection with a private virtual interface only, since it is a private physical circuit outside the public internet.
C. Provision an AWS Site-to-Site VPN connection, since it provides built-in IPsec encryption and can be provisioned quickly.
D. Provision a Direct Connect connection and attach a Direct Connect Gateway to encrypt traffic across virtual interfaces.
**Correct answer(s):** A
**Why correct:** Direct Connect provides the private, non-internet, consistent 10 Gbps-class throughput with low jitter that the nightly window requires, but Direct Connect traffic is not encrypted by default — layering an IPsec VPN over the Direct Connect private virtual interface satisfies the end-to-end encryption requirement while keeping the private, high-throughput path.
**Why each wrong option is wrong:** B fails the "encrypted end-to-end in transit" compliance requirement, since a Direct Connect private virtual interface alone carries traffic unencrypted at the network layer; C, Site-to-Site VPN traverses the public internet and cannot reliably sustain 10 Gbps with the jitter-free consistency the nightly batch window demands; D, Direct Connect Gateway is used to extend a Direct Connect connection to multiple VPCs or regions, it provides no encryption capability whatsoever.
**Trigger words:** "never traverse the public internet," "encrypted end-to-end," "10 Gbps of consistent throughput," "no tolerance for unpredictable network jitter."
**Underlying architectural principle:** Direct Connect is not encrypted by default — when a scenario demands both Direct Connect-class performance and encryption in transit, the correct architecture layers a VPN over the Direct Connect connection rather than choosing one service alone.

---

### Question 15 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** Building on an existing multi-region Transit Gateway design (one Transit Gateway per region, connected via inter-region Transit Gateway peering), a company now has a strict new requirement: a PCI-compliant VPC in `us-east-1` may communicate only with one specific finance-department VPC in `eu-west-1`, and with no other VPC attached to either region's Transit Gateway — even though both the PCI VPC and the finance VPC remain attached to their regional Transit Gateways for other necessary connectivity. Auditors require this isolation to be enforced at the routing layer, not solely through security groups.
**Options:**
A. Create separate Transit Gateway route tables in each region, associate only the PCI VPC's and finance VPC's attachments with a dedicated route table containing routes only to each other, and keep them out of the route table(s) used by all other attachments.
B. Take no additional action, since Transit Gateway inter-region peering is already non-transitive beyond two hops and this isolates the PCI VPC automatically.
C. Establish a direct VPC Peering connection between the PCI VPC and the finance VPC in addition to their existing Transit Gateway attachments, and rely on security groups to block all other traffic.
D. Detach both VPCs from their Transit Gateways and connect them to each other solely through a Direct Connect Gateway.
**Correct answer(s):** A
**Why correct:** Transit Gateway route table segmentation (multiple route tables with selective attachment association and route propagation) is exactly the mechanism for restricting which attachments can reach which other attachments within a shared Transit Gateway, satisfying the auditors' routing-layer isolation requirement while leaving both VPCs' other connectivity intact.
**Why each wrong option is wrong:** B is false and dangerous — by default, attachments associated with the same (e.g., main/default) Transit Gateway route table can reach one another, so "taking no action" would leave the PCI VPC transitively reachable by every other attachment in that route table, which is the exact problem needing a fix; C adds a working reachability path between the two intended VPCs but does nothing to remove the PCI VPC's existing Transit Gateway attachment from the shared route table, so other VPCs could still transitively reach it via the Transit Gateway regardless of the new peering link; D, Direct Connect Gateway connects Direct Connect connections to VPCs/regions for on-premises hybrid connectivity, it is not a mechanism for connecting two VPCs to each other.
**Trigger words:** "may communicate only with one specific... VPC, and with no other VPC," "enforced at the routing layer, not solely through security groups."
**Underlying architectural principle:** Selective reachability between specific attachments on a shared Transit Gateway is achieved through route table segmentation (multiple route tables, controlled association/propagation), not by adding parallel connectivity paths or assuming default non-transitivity that doesn't actually exist within a single route table.

---

### Question 16 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A global fintech platform has four requirements. First, its public marketing site's static content must load in well under a second worldwide (already correctly solved with an existing CloudFront distribution — no changes needed here). Second, its trading API is HTTP-based but latency-sensitive and effectively non-cacheable, runs behind ALBs in four regions, and must route each client to the best-performing healthy region with failover measured in seconds, not dependent on DNS caching behavior. Third, a connection to an on-premises clearing-house system carrying regulatory settlement data needs a dedicated, non-internet path with a contracted bandwidth SLA and consistent sub-10ms latency. Fourth, the finance team wants to avoid provisioning redundant services where one existing service already satisfies a need. **(Choose TWO actions that best complete this architecture.)**
**Options:**
A. Deploy AWS Global Accelerator in front of the trading API's regional Application Load Balancers, using health-check-based endpoint groups for requirement two.
B. Rely solely on Route 53 latency-based routing with a very low DNS TTL configured on the trading API's record for requirement two.
C. Provision an AWS Direct Connect dedicated connection with a private virtual interface for requirement three.
D. Provision an AWS Site-to-Site VPN connection for requirement three, since it can be established faster than Direct Connect.
E. Deploy a second CloudFront distribution in front of the trading API's ALBs to reduce its failover time.
**Correct answer(s):** A, C
**Why correct:** Global Accelerator (A) provides network-layer, health-check-driven routing to the best-performing healthy regional ALB with failover in seconds, independent of DNS TTLs, directly meeting requirement two; Direct Connect (C) is the only option that can contractually guarantee dedicated bandwidth and consistent sub-10ms latency over a non-internet path for the regulated settlement data in requirement three.
**Why each wrong option is wrong:** B's failover speed is fundamentally bounded by DNS resolver caching and TTL honoring behavior across the internet, which is precisely why "not dependent on DNS caching behavior" rules it out even at a low TTL; D, a VPN traverses the public internet, so it cannot provide a contracted bandwidth SLA or guarantee consistent sub-10ms latency the way a dedicated Direct Connect circuit can; E, CloudFront caches HTTP(S) content and provides no benefit for a non-cacheable, latency-sensitive API, and adding a second distribution is also a redundant service given Global Accelerator already correctly solves requirement two — directly conflicting with requirement four.
**Trigger words:** "effectively non-cacheable," "failover measured in seconds, not dependent on DNS caching behavior," "contracted bandwidth SLA and consistent sub-10ms latency," "avoid provisioning redundant services."
**Underlying architectural principle:** A high-performing global architecture typically layers purpose-built services rather than stretching one service to cover every need: CloudFront for cacheable HTTP(S) content, Global Accelerator for latency-sensitive or non-cacheable TCP/UDP traffic needing fast network-layer failover, and Direct Connect for dedicated, SLA-backed hybrid connectivity — each solving a distinct performance problem the others cannot.

---

*16 original Domain 3 (Design High-Performing Architectures) practice questions. Distribution: 2 Easy, 7 Medium, 5 Hard, 2 Very Hard; 3 Multiple-Response, 13 Single-Answer.*
