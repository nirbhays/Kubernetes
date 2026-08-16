# Networking Mastery — AWS SAA-C03

## VPC Fundamentals

**CIDR block design**
- VPC CIDR range: `/16` to `/28`. Exam trigger: "plan for future growth" → pick the largest CIDR you can (`/16`), because the primary VPC CIDR block is immutable — you can never shrink, expand, or otherwise resize it after creation. Growth beyond the original range is handled by *adding* a secondary CIDR block (not by resizing the primary one), but overlapping secondary ranges break peering/TGW routing later — a classic scenario question.
- Reserved addresses per subnet: AWS reserves 5 IPs (network address, VPC router, DNS, future use, broadcast — even though VPC doesn't support broadcast). Distractor: candidates forget this and miscalculate usable host counts on subnet-sizing questions.
- Secondary CIDR blocks: used when you outgrow the original range. Distractor: exam sometimes proposes "create a new VPC and peer it" when the correct minimal-effort answer is "add a secondary CIDR to the existing VPC."

**Public vs private subnet — the only distinguishing factor**
- A subnet is "public" **solely** because its route table has a route to an Internet Gateway (IGW) for `0.0.0.0/0`. It is not about NACLs, not about auto-assign public IP. Exam loves testing this: a subnet with auto-assign-public-IP enabled but no IGW route is still private.
- Route tables are associated per-subnet; if unassociated, subnet uses the VPC main route table. Trigger phrase "instances in this subnet unexpectedly have internet access" → check if it's implicitly associated with the main route table which has an IGW route.

**Internet Gateway (IGW)**
- Horizontally scaled, redundant, HA by design — no bandwidth constraints to size for. One IGW per VPC. Distractor: answers proposing "multiple IGWs for HA" are always wrong — IGW is already regionally resilient across AZs.

**NAT Gateway vs NAT Instance**
- NAT Gateway: managed, AZ-scoped (deploy one per AZ for HA — a single NAT GW is a single point of failure for that AZ), automatically scales bandwidth up to 100 Gbps with no configuration required, no security groups, cannot be used as a bastion, cannot serve as a network address translator for anything other than outbound-initiated + response traffic.
- NAT Instance: legacy, only correct answer when the question mentions "port forwarding," "acting as a bastion," "network appliance functionality," or "cost-sensitive with very low/no traffic and can tolerate managing patching." Otherwise NAT Gateway wins on every "least operational overhead" question.
- Key exam boundary: NAT Gateway is deployed in a **public** subnet and used by **private** subnet route tables pointing `0.0.0.0/0` → NAT GW ID. Getting the direction backwards is the most common distractor.
- Elastic IP is mandatory for a public NAT Gateway; private NAT Gateway (VPC-to-VPC/on-prem via TGW/VPN, no internet) does not need one — know this exists for "NAT without internet egress" scenarios.

**Elastic IP (EIP)**
- Static, account-owned public IPv4 that persists across stop/start (unlike the ephemeral public IP auto-assigned at launch, which changes on stop/start). Trigger: "IP address must survive instance stop/start" → EIP.
- Cost trap (2026 behavior): AWS now charges hourly for **all public IPv4 addresses**, including EIPs whether attached or not, and even the default ephemeral public IPv4 on instances — this shifted cost-optimization answers toward minimizing public IP usage (prefer NAT Gateway/PrivateLink/IPv6 over assigning public IPs per-instance). Distractor: assuming EIPs are "free when attached" — no longer categorically true; the exam guide expects awareness that unused/idle public IPs cost money, reinforcing "release unattached EIPs" as a cost-optimization answer.

**ENI (Elastic Network Interface)**
- Detachable from one instance, attachable to another in the same AZ (not cross-AZ) — used for failover architectures where you want to move an IP identity between instances without DNS propagation delay. Trigger words: "maintain the same private IP/MAC after failover," "management network interface separate from data network."
- Multiple ENIs per instance = multiple subnets/security-group sets on one instance (common in dual-homed appliance or management-vs-data-plane questions).

**Security Groups vs NACLs — the recurring comparison**
| | Security Group | NACL |
|---|---|---|
| Level | ENI/instance | Subnet |
| State | Stateful (return traffic auto-allowed) | Stateless (must allow both directions explicitly) |
| Rules | Allow only | Allow AND deny |
| Evaluation | All rules evaluated | Rules evaluated in numeric order, first match wins |
| Default | Deny all inbound, allow all outbound | Default NACL allows all; custom NACL denies all until rules added |

- Exam trigger: "explicitly block a specific malicious IP" → NACL (SGs can't deny). "Ephemeral port range must be opened for return traffic" → NACL-only concern (stateful SGs don't need this).
- Distractor: candidates try to "deny" via security group — always wrong, SGs have no deny rules.
- Rule numbering distractor: a lower-numbered explicit DENY before an ALLOW wins even if the ALLOW looks more specific — classic "why is traffic still blocked" troubleshooting question.

**DNS in VPC**
- `enableDnsSupport` + `enableDnsHostnames` both required for instances to get resolvable DNS hostnames (private and public).
- The Amazon-provided DNS server (Route 53 Resolver) that handles default VPC DNS lives at the base of the VPC's IPv4 CIDR range plus two (e.g., `10.0.0.2` for a `10.0.0.0/16` VPC) — don't confuse this with the EC2 instance metadata service address `169.254.169.254`, which is unrelated to DNS resolution. For **hybrid DNS** (on-prem ↔ VPC resolution) the answer is **Route 53 Resolver endpoints (inbound + outbound)**, not a custom BIND server, unless the question specifically wants a self-managed solution for legacy compatibility.
- Trigger: "resolve on-prem hostnames from within VPC and vice versa" → Route 53 Resolver inbound/outbound endpoints + conditional forwarding rules. Distractor: proposing Route 53 public hosted zones (wrong — those are for internet-facing DNS, not hybrid private resolution).

---

## VPC Peering

- Non-transitive: if A↔B and B↔C are peered, A cannot reach C through B. This is the single most tested peering fact — any "hub and spoke via peering" design with >3 VPCs needing full-mesh reachability is a distractor pointing you toward **Transit Gateway** instead.
- No overlapping CIDRs allowed between peered VPCs.
- Cross-region and cross-account peering supported.
- Use peering when: small number of VPCs (2–ish, or need simple point-to-point), cost sensitivity (peering has no hourly charge, only data transfer), or when you specifically don't want transitive routing (isolation requirement is actually the *correct* reason to choose peering over TGW).
- Distractor: "we have 10 VPCs that all need to talk to each other" → peering would require ~45 individual connections (n(n-1)/2) — this scaling pain is the setup for the TGW answer.

## Transit Gateway (TGW)

- Regional hub-and-spoke construct; connects VPCs, VPN, and Direct Connect (via DX Gateway) through one attachment-managed hub. Transitive routing supported natively.
- Trigger words: "hundreds of VPCs," "simplify a complex mesh of connections," "centralized routing/inspection," "multiple accounts and multiple VPCs need to communicate."
- TGW route tables are separate from VPC route tables — you can segment traffic (e.g., prod TGW route table vs non-prod) for network segmentation without separate TGWs. Exam tests "how do I isolate dev and prod VPCs attached to the same TGW" → answer is separate TGW route table associations/propagations, not separate TGWs.
- Cross-region: TGW peering (inter-region) exists — connects two TGWs in different regions; still non-transitive at the TGW-peering level (a TGW peering attachment itself doesn't propagate further transitively across a third TGW without explicit route config).
- Cost model: hourly per attachment + data processing per GB — this is why "just 2 VPCs, cost-sensitive" scenarios still favor peering over TGW.
- Centralized egress/inspection pattern: TGW + shared VPC with NAT Gateway or firewall appliances = common "centralize internet egress across all VPCs" answer.

## PrivateLink & VPC Endpoints

**The core decision boundary: Gateway Endpoint vs Interface Endpoint**
- **Gateway Endpoint**: only for **S3 and DynamoDB**. Free. Implemented as a route table target (prefix list), not an ENI. No cross-region, no on-prem access (can't route to it from VPN/DX because it's not an IP-addressable ENI).
- **Interface Endpoint (PrivateLink)**: an ENI with a private IP in your subnet, for most other AWS services (and third-party/custom SaaS services hosted behind NLBs). Costs hourly + per-GB. Reachable from on-prem via DX/VPN since it has a real IP.
- Exam trigger: "access S3 privately, no NAT Gateway, minimize cost" → Gateway Endpoint for S3 (free, and removes the need for a NAT Gateway just for S3 traffic — this combo is a favorite cost-optimization question).
- Distractor: proposing Interface Endpoint for S3 — technically now possible for S3 in some cases but never the "best/cheapest" answer when Gateway Endpoint fits; exam wants Gateway Endpoint whenever S3/DynamoDB + private-only + cost-optimized appear together.
- Trigger: "on-premises servers need private access to an AWS service" → must be Interface Endpoint (Gateway Endpoints aren't reachable from outside the VPC).
- **PrivateLink for custom services**: you expose your own service (behind an NLB) to other VPCs/accounts without peering, without route tables, without CIDR overlap concerns, and without exposing to the public internet. Trigger: "SaaS provider," "expose a service to thousands of customer VPCs without peering," "no transitive routing risk," "no overlapping CIDR concerns." This is the #1 distractor-eliminator against VPC Peering — if the question emphasizes many consumers or strict one-way access (consumer initiates, provider never sees consumer's VPC), it's PrivateLink, not peering/TGW.

## Site-to-Site VPN

- Two tunnels per Virtual Private Gateway (VGW) or TGW attachment, for HA — always design for both tunnels (customer gateway device HA), not just accept the default as a single path.
- Fast to provision (minutes), encrypted over the public internet — inherently variable latency/throughput, capped well below Direct Connect.
- Trigger: "quick to set up," "temporary/backup connectivity," "encryption required," "low-to-moderate bandwidth," "cost-sensitive hybrid connection."
- Common combo answer: VPN as a **backup path for Direct Connect** (DX primary, VPN secondary via BGP failover) — this exact pairing appears often in resilience-domain questions.
- Accelerated Site-to-Site VPN uses Global Accelerator's AWS backbone edge locations to improve consistency/performance of the VPN tunnel setup — know this exists as the answer to "improve VPN performance without going to Direct Connect."

## Direct Connect (DX)

- Dedicated private physical network connection to AWS, bypassing the public internet entirely — the only correct answer when question demands consistent low-latency, high-bandwidth, or explicitly says "not over the public internet"/"predictable network performance"/"reduce bandwidth costs for large consistent data transfer."
- Provisioning takes **weeks to months** — distractor is proposing DX for "urgent" or "temporary" connectivity needs; VPN wins there.
- Not encrypted by default (it's a private physical link, not inherently encrypted) — if question requires both DX-level performance AND encryption in transit, correct answer is **DX + VPN over DX (or a VPN over public VIF)**, not DX alone.
- Public VIF (virtual interface) → reach AWS public services (S3, DynamoDB) and public IPs. Private VIF → reach VPC private resources (via VGW). Transit VIF → reach TGW. Know which VIF type maps to which target — commonly quizzed.

## Direct Connect Gateway (DXGW)

- Solves: one DX connection needing to reach **multiple VPCs across multiple regions** (private VIFs alone are limited to one VGW/region). DXGW is a global construct that associates with VGWs (private VIF path) or TGWs (transit VIF path) across regions.
- Trigger: "single Direct Connect connection, multiple VPCs in different regions," "centralize DX connectivity for multiple accounts." Distractor: proposing a separate DX connection per region — unnecessarily costly and the DXGW exists exactly to avoid that.
- DXGW + TGW (via transit VIF) is now the standard modern pattern over DXGW + multiple VGWs, especially when many VPCs per region are involved.

---

## Route 53 Routing Policies

All records live in a hosted zone; routing policy is chosen per record set. Exam gives a scenario and expects you to map it to exactly one policy — know the differentiator, not just the definition.

- **Simple**: one resource, no health checks, no logic. Distractor bait: any scenario mentioning failover/multiple values with health awareness is NOT simple, even if "simple-looking."
- **Weighted**: distribute traffic by assigned proportion across multiple resources — canary/blue-green deployments, A/B testing, gradual traffic shifting. Trigger words: "70/30 split," "gradually shift traffic," "canary release."
- **Latency-based**: route to the region giving the **lowest network latency** to the user, based on latency measurements between the user and AWS regions — not physical distance. Trigger: "best performance," "lowest latency," resources in multiple AWS regions.
- **Failover**: active-passive with health checks — primary record served unless it fails health check, then Route 53 returns secondary. Trigger: "disaster recovery," "active-passive," "automatically fail over to a backup site."
- **Geolocation**: routes based on the **user's geographic location** (country/continent/state) — used for content restriction/localization/compliance (e.g., "must serve EU users an EU-compliant endpoint," "restrict content by country"). Distractor vs Latency: geolocation is about *where the user is legally/physically from* for compliance/localization, not about performance.
- **Geoproximity** (requires Route 53 Traffic Flow): routes based on geographic location of users AND resources, with a **bias** value to expand/shrink the geographic region from which traffic is routed to a resource. Trigger: "shift more or less traffic to a region based on a bias without moving infrastructure." Rarely the primary answer but tested as the distractor-eliminator against Geolocation/Latency when "bias" or "traffic flow" is mentioned explicitly.
- **Multivalue answer**: return up to eight healthy IP addresses (selected at random) in response to DNS queries, each optionally health-checked — a lightweight, non-ELB way to add basic client-side load balancing + health checking DNS-level redundancy. Trigger: "return multiple IPs," "improve availability without a load balancer," "DNS-level health checking for several resources." Distractor: don't confuse with a real load balancer's L7 capabilities — multivalue is DNS-only round-robin-with-health-checks, not intelligent routing.

Exam pattern: a scenario names two candidate-sounding policies (e.g., Latency vs Geolocation, or Failover vs Weighted) — the differentiator keyword (compliance/legal restriction → Geolocation; performance → Latency; gradual rollout → Weighted; DR/health-check-triggered switch → Failover) decides it.

---

## CloudFront

- CDN with edge caching; correct answer whenever "reduce latency for global users," "reduce load on origin," "cache static content," "protect origin from direct access" appear together.
- Origin can be S3 (use **Origin Access Control (OAC)** — the current recommended mechanism, replacing legacy OAI — to keep the S3 bucket private and only accessible via CloudFront), an ALB, or a custom/on-prem HTTP origin.
- Trigger: "S3 bucket must not be publicly accessible but content must be served globally" → CloudFront + OAC + bucket policy restricting to the CloudFront distribution. Distractor: making the S3 bucket public — always wrong when the question says "private"/"restricted."
- Field-level encryption, signed URLs/cookies for restricted premium content, Lambda@Edge/CloudFront Functions for edge logic (Functions = lightweight/cheap/high-scale for simple header/URL manipulation; Lambda@Edge = when you need more compute, longer execution, or access to the request/response body).
- Distractor vs Global Accelerator: CloudFront caches content and terminates HTTP(S) at the edge (works for **cacheable, HTTP/S** workloads); Global Accelerator does not cache — it's for improving the network path to non-cacheable, TCP/UDP, or non-HTTP workloads (gaming, VoIP, IoT protocols) or when you need static anycast IPs.

## Global Accelerator

- Provides static anycast IP addresses that route traffic over the AWS global backbone network to the closest healthy edge, then to optimal regional endpoints (ALB/NLB/EC2/EIP) — improves performance for non-cacheable and non-HTTP(S) traffic.
- Trigger words: "static IP addresses required" (e.g., allow-listing at client firewalls), "TCP/UDP traffic," "non-HTTP protocols," "improve availability and performance via fast regional failover without DNS propagation delay," "multi-region active-active with instant failover."
- Key differentiator from Route 53 failover: GA failover happens at the network layer without waiting for DNS TTL expiry/client-side DNS caching — this is the answer whenever the question stresses "instant"/"fast" failover and DNS caching/TTL is called out as a problem with the Route 53 approach.
- Distractor: using CloudFront for a workload requiring static IPs or raw TCP/UDP — CloudFront doesn't offer static entry IPs the same way and is HTTP(S)-oriented; GA is the correct pick there.

---

## Cross-Cutting Exam Heuristics

- **"Least operational overhead" / "fully managed"** → eliminate self-managed options (NAT instance, custom BIND DNS, self-managed VPN appliances) unless the scenario has a hard requirement only the self-managed option satisfies (port forwarding, proxy/bastion behavior, legacy protocol support).
- **"No overlapping CIDR" mentioned explicitly** → signals Peering/TGW is *infeasible*; steers you toward PrivateLink (no CIDR dependency) as the actual intended answer.
- **"Thousands of consumer accounts/VPCs" + "provider doesn't want visibility into consumer VPC"** → PrivateLink, always, over peering/TGW.
- **"Cannot use public internet" but "needs consistent, high throughput, contracted SLA"** → Direct Connect; if timeline is "immediately"/"today" → VPN (with DX as future/parallel upgrade path).
- **Health-check-driven automatic recovery** across regions at DNS layer → Route 53 Failover; at network layer with no DNS wait → Global Accelerator.
- Whenever a question lists a public IPv4 address anywhere "idle," "unattached," or "unused," expect a cost-optimization answer to release it — this reflects the 2026 public IPv4 hourly billing model change.
