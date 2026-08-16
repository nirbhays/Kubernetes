# SAA-C03 Domain 1 Practice Questions — Design Secure Architectures (30% weight), Part 2

Focus areas: Security Groups vs. NACLs, VPC security design, WAF vs. Shield Standard/Advanced, GuardDuty vs. Macie vs. Security Hub vs. Inspector, Cognito User Pools vs. Identity Pools, ACM, CloudTrail vs. AWS Config.

This set complements `domain1-secure-architectures-practice.md` (which covers KMS, Secrets Manager/Parameter Store, and S3 encryption/access) — together they span Domain 1's full topic breadth.

These are **original practice questions** written for personal study, based on publicly documented AWS service behavior as of 2026 and the official SAA-C03 exam guide scope. They are **not** reproductions of any real, leaked, or dumped exam content.

---

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A three-tier web application runs in a VPC with public web servers in a public subnet and application servers in a private subnet. The security team wants the web tier's security group to allow inbound HTTPS from the internet, and wants the application tier's security group to allow inbound traffic on port 8080 only from instances that carry the web tier's security group — not from any specific hardcoded IP range, since web tier instances scale in and out constantly and their private IPs change.

**Options:**
A. In the application tier's security group inbound rule, set the source to the web tier's security group ID rather than a CIDR range.
B. In the application tier's security group inbound rule, set the source to the VPC's CIDR block, since that covers all current and future web tier instance IPs.
C. Create a NACL rule on the private subnet allowing inbound traffic on port 8080 only from the public subnet's CIDR range.
D. Hardcode the current Auto Scaling group's instance private IPs into the application tier's security group and update the rule via a scheduled Lambda function every time the group scales.

**Correct answer(s):** A

**Why correct:** Security groups can reference another security group ID as the source, which automatically includes any instance (current or future) that has that security group attached — exactly matching the requirement to allow traffic from "the web tier" as a role, regardless of changing IPs.

**Why each wrong option is wrong:** B is far too broad, allowing any resource anywhere in the VPC (including future unrelated subnets/services) to reach port 8080, violating least privilege. C uses subnet-level CIDR matching, which permits any instance in the public subnet — not specifically web tier instances — and NACLs are a coarser, less precise tool for this kind of role-based rule. D reintroduces exactly the brittle, high-maintenance IP-tracking problem the team is trying to avoid, and duplicates functionality security-group-to-security-group references already provide natively.

**Trigger words:** "instances that carry the web tier's security group," "not from any specific hardcoded IP range," "private IPs change."

**Underlying architectural principle:** Reference a security group as the source/destination of another security group's rule whenever the permitted peer is defined by "role" (a group of instances) rather than by a fixed network range — it self-updates as instances scale.

---

### Question 2 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company's security team is troubleshooting a reported outage where application servers in a private subnet can no longer receive return traffic from an external API they call over HTTPS on port 443. The subnet's NACL was recently tightened by a new team member. The NACL currently has an inbound rule allowing TCP port 443 from 0.0.0.0/0, an inbound rule allowing TCP port 22 from a bastion CIDR, and no other inbound allow rules; the outbound rules only allow TCP port 443 to 0.0.0.0/0. The instances' security group is unchanged and correctly allows all outbound traffic.

**Options:**
A. Add an inbound NACL rule allowing TCP traffic on the ephemeral port range (1024–65535) from 0.0.0.0/0, since NACLs are stateless and must explicitly permit the return traffic on the client's ephemeral port.
B. Add an inbound security group rule allowing TCP port 443 from 0.0.0.0/0, since the security group must also explicitly allow the return traffic.
C. Remove the outbound port 443 restriction and allow all outbound traffic on the NACL, since the outbound rule is what's blocking the request from ever leaving the subnet.
D. Reboot the affected instances, since NACL rule changes require an instance restart to take effect.

**Correct answer(s):** A

**Why correct:** NACLs are stateless, so return traffic for an outbound request must be separately permitted by an inbound rule matching the ephemeral port range the client OS used for that connection — the missing ephemeral-port inbound allow is exactly what a "recently tightened" NACL would have removed.

**Why each wrong option is wrong:** B misdiagnoses the layer — security groups are stateful, so a security group only needs to allow the outbound request; it automatically permits the matching inbound return traffic without any separate rule, so this change wouldn't be the fix and isn't necessary. C is wrong because the described outbound rule (port 443 to 0.0.0.0/0) already permits the original outbound request; the problem is the missing inbound rule for the response, not the outbound leg. D is factually incorrect — NACL rule changes apply immediately to new and in-progress evaluations without requiring any instance reboot.

**Trigger words:** "no longer receive return traffic," "NACL was recently tightened," "no other inbound allow rules," stateless implied by symptom.

**Underlying architectural principle:** Because NACLs are stateless, every connection direction must be explicitly permitted on both inbound and outbound, including inbound allowance of the ephemeral port range for responses to outbound-initiated connections — unlike stateful security groups, which auto-permit return traffic.

---

### Question 3 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company suspects that a single compromised EC2 instance's outbound traffic is being used to scan other instances within the same subnet. The security team wants a control that can immediately and explicitly block all traffic — inbound and outbound — to and from one specific instance's IP address, evaluated before that instance's own security group is even consulted, and that can be applied without modifying the security group configuration other teams rely on for that instance.

**Options:**
A. Add explicit deny rules on the subnet's NACL blocking the compromised instance's IP address in both the inbound and outbound rule sets, with a rule number lower than any allow rule.
B. Remove all inbound rules from the compromised instance's security group, leaving only the default outbound allow-all rule.
C. Add a security group rule denying all traffic to and from the compromised instance's IP address.
D. Detach the instance's elastic network interface to physically prevent any further network communication.

**Correct answer(s):** A

**Why correct:** NACLs support explicit deny rules and evaluate every packet crossing the subnet boundary in each direction, independently of the instance's security group. For inbound traffic this NACL evaluation happens before the security group is even consulted; for outbound traffic the NACL still independently enforces the deny after the local security group check runs. Either way, a single low-numbered deny rule targeting that specific IP blocks traffic immediately in both directions without touching the security group other teams depend on.

**Why each wrong option is wrong:** B only removes inbound allow rules but security groups have no explicit "deny" concept — an attacker's existing established connections and any subsequent security-group misconfiguration risk remain, and it still doesn't block outbound traffic, which security groups' default behavior would otherwise still allow. C is not possible — security groups only support allow rules, never explicit deny rules, so this option describes a feature that doesn't exist. D is a valid but far more disruptive and operationally heavier-handed action (it also removes the instance from all other legitimate use immediately and complicates forensics) compared to a targeted, reversible NACL deny rule, and the requirement specifically asks to avoid touching the security group setup others rely on — not to isolate the instance from the network entirely via infrastructure surgery.

**Trigger words:** "explicit deny," "evaluated before that instance's own security group," "without modifying the security group configuration."

**Underlying architectural principle:** Only NACLs support explicit deny rules and operate at the subnet level, independently of and (for inbound traffic) ahead of security group evaluation — security groups are allow-only and stateful, making NACLs the correct tool for an immediate, targeted block affecting both traffic directions without disturbing existing security group rules.

---

### Question 4 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company runs a three-tier VPC and wants to enforce defense-in-depth so that even if an application server's security group is ever misconfigured to accidentally allow inbound traffic from the internet, a second independent layer of network control still blocks any such traffic before it reaches the private application subnet. The team wants this second layer to apply automatically to every instance placed in that subnet, present and future, without needing to be attached to each instance individually, and accepts that legitimate return traffic on ephemeral ports will need to be explicitly permitted as a trade-off.

**Options:**
A. Configure the private application subnet's NACL to allow inbound traffic only from the web tier subnet's CIDR range (and the necessary ephemeral port range for return traffic), denying all other inbound sources by default.
B. Rely exclusively on well-configured security groups on each application instance, since security groups alone are sufficient defense-in-depth by design.
C. Add a second security group to each application instance restricting inbound sources to the web tier's CIDR range, in addition to the existing security group.
D. Configure a route table rule on the private subnet that drops any packet whose source is not within the VPC's CIDR block.

**Correct answer(s):** A

**Why correct:** A subnet-level NACL applies automatically to every instance in that subnet without per-instance attachment, and because NACLs are stateless, it independently enforces source restrictions and requires explicitly permitting ephemeral-port return traffic — exactly the described second, independent layer that still functions even if a security group is misconfigured.

**Why each wrong option is wrong:** B provides only a single layer of control; if that one security-group layer is misconfigured (the exact failure mode the scenario is defending against), there is no independent backstop, so it fails the explicit defense-in-depth requirement. C still requires per-instance attachment (violating "applies automatically... without needing to be attached to each instance") and, being another security group, is evaluated at the same layer/logic as the original misconfigured one rather than being an independent second layer — worse, because multiple security groups attached to the same instance are combined additively (the union of all their allow rules applies), a second, more restrictive security group can never revoke access the first, misconfigured one already grants; it can only add further allowances. D describes a capability route tables do not have — route tables direct traffic to targets based on destination, they do not perform source-based packet filtering or dropping.

**Trigger words:** "even if an application server's security group is ever misconfigured," "second independent layer," "applies automatically... without needing to be attached to each instance," "legitimate return traffic on ephemeral ports will need to be explicitly permitted."

**Underlying architectural principle:** Subnet-level NACLs provide an automatically-applied, independent second layer of defense-in-depth behind per-instance security groups precisely because they operate at a different scope (subnet vs. instance) and evaluate rules statelessly and explicitly, unlike security groups.

---

### Question 5 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company is designing a new VPC and wants to document, for a security audit, the fundamental behavioral difference between the security groups and network ACLs they plan to use together. The auditor specifically asks: if an EC2 instance in a subnet initiates an outbound connection to an external service and receives a response, which statement correctly describes how each control evaluates that response traffic by default?

**Options:**
A. The security group automatically allows the stateful return traffic without a matching inbound rule, while the NACL requires an explicit inbound rule permitting the response (typically on the ephemeral port range) because it evaluates each direction statelessly.
B. Both the security group and the NACL automatically allow the stateful return traffic without any explicit inbound rule needed on either.
C. The NACL automatically allows the stateful return traffic without a matching inbound rule, while the security group requires an explicit inbound rule permitting the response.
D. Neither control allows the return traffic automatically; both require explicit matching inbound rules for the response to reach the instance.

**Correct answer(s):** A

**Why correct:** This is the core, well-documented behavioral distinction between the two controls: security groups are stateful (tracking connections so return traffic is automatically permitted) while NACLs are stateless (evaluating every packet independently in each direction, requiring explicit inbound allow rules for responses).

**Why each wrong option is wrong:** B incorrectly states NACLs are stateful, which is the opposite of their documented behavior. C reverses which control is stateful and which is stateless — it is the security group that is stateful, not the NACL. D incorrectly claims security groups also require explicit inbound rules for return traffic, contradicting their stateful nature.

**Trigger words:** "fundamental behavioral difference," "receives a response," "evaluates that response traffic by default."

**Underlying architectural principle:** Security groups are stateful (automatic return-traffic allowance); NACLs are stateless (explicit allow rules required in both directions) — this single distinction underlies nearly every SG-vs-NACL troubleshooting scenario.

---

### Question 6 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company's public-facing website, served through an Application Load Balancer, has recently experienced repeated SQL injection attempts and a Layer 7 HTTP flood that isn't large enough to qualify as a large-scale volumetric event but is still degrading application performance by exhausting backend connection pools with malformed and excessive requests. The security team wants a service that can inspect HTTP request content and block requests matching known injection patterns, while also rate-limiting individual IP addresses that send abnormally high request volumes to specific URI paths.

**Options:**
A. Create an AWS WAF web ACL with a managed SQL injection rule group and a rate-based rule scoped to the relevant URI paths, and associate it with the ALB.
B. Enable AWS Shield Advanced on the ALB, since Shield Advanced inspects HTTP request bodies for injection patterns and enforces per-IP rate limits automatically.
C. Enable AWS Shield Standard on the ALB, since it is included at no additional cost and mitigates all Layer 7 attacks, including application-layer floods and injection attempts.
D. Enable GuardDuty with S3 protection and EKS protection features to detect and automatically block the malicious HTTP requests at the ALB.

**Correct answer(s):** A

**Why correct:** WAF is purpose-built to inspect HTTP request content (headers, body, URI) against rule groups — including managed SQL injection rule sets — and rate-based rules that throttle individual source IPs exceeding a request threshold on specified paths, directly matching both requirements in the scenario.

**Why each wrong option is wrong:** B is factually incorrect — Shield Advanced's value-add is enhanced DDoS protection, cost protection, and 24/7 DRT access; it does not itself perform HTTP content inspection or rule-based request filtering, that's WAF's job (Shield Advanced is commonly paired with WAF, not a substitute for it). C is also incorrect — Shield Standard provides only baseline, automatic protection against common infrastructure-layer (L3/L4) DDoS attacks and does not inspect or filter Layer 7 HTTP request content at all. D misapplies GuardDuty, which is a threat-detection service analyzing logs (VPC Flow Logs, DNS logs, CloudTrail, S3/EKS data events) for anomalous account/resource behavior — it does not inspect or block live HTTP requests at a load balancer.

**Trigger words:** "SQL injection attempts," "inspect HTTP request content," "rate-limiting individual IP addresses... specific URI paths."

**Underlying architectural principle:** AWS WAF is the Layer 7 content-inspection and rate-limiting tool for HTTP(S) traffic (SQLi/XSS rules, rate-based rules); Shield addresses network/transport-layer (and broader infrastructure) DDoS protection, and the two are complementary, not interchangeable.

---

### Question 7 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A publicly traded financial services company running a high-visibility public API on an ALB behind CloudFront is a known, named target for sophisticated, large-scale DDoS campaigns. Executive leadership requires financial protection against usage-based cost spikes (scaling charges) incurred specifically as a result of a DDoS attack, guaranteed access to AWS's specialized DDoS Response Team (DRT) during an active incident, and proactive, near-real-time attack detection and mitigation for complex, multi-vector Layer 3/4/7 events — with cost considered secondary to guaranteed incident response capability.

**Options:**
A. Subscribe to AWS Shield Advanced on the CloudFront distribution and ALB, pair it with AWS WAF for Layer 7 rule enforcement, and maintain a Business, Enterprise On-Ramp, or Enterprise Support plan, which is required in addition to Shield Advanced to contact the DRT directly.
B. Rely on AWS Shield Standard, since it is automatically enabled on CloudFront and ELB at no cost and provides the same DRT access and cost protection as Shield Advanced.
C. Enable AWS Config with conformance packs to continuously monitor and automatically remediate DDoS-related configuration drift in near-real time.
D. Enable GuardDuty with all protection plans (S3, EKS, RDS, Lambda) to detect DDoS traffic patterns and automatically engage the AWS DDoS Response Team.

**Correct answer(s):** A

**Why correct:** Shield Advanced is specifically the tier that adds DDoS cost protection (credits for scaling charges incurred during an attack), 24/7 DRT engagement, and advanced, near-real-time detection/mitigation for complex multi-vector attacks — none of which Shield Standard includes — and it's designed to be paired with WAF for the Layer 7 rule-enforcement component. Note that Shield Advanced alone enables proactive engagement, but direct, on-demand DRT contact additionally requires a Business, Enterprise On-Ramp, or Enterprise Support plan — a detail the scenario's "cost secondary to guaranteed incident response" framing means the company should budget for as well.

**Why each wrong option is wrong:** B is factually wrong — Shield Standard, while free and automatic, explicitly does not include DRT access or DDoS cost protection; those are Shield Advanced-exclusive benefits, which is precisely the gap the scenario's requirements expose. C misapplies AWS Config, which is a configuration compliance and drift-detection/remediation service for resource configurations — it has no DDoS detection, mitigation, or response-team engagement capability. D misapplies GuardDuty, which detects anomalous account and network behavior from logs but does not provide DDoS-specific cost protection, DRT access, or dedicated attack mitigation infrastructure the way Shield Advanced does.

**Trigger words:** "financial protection against usage-based cost spikes," "guaranteed access to AWS's specialized DDoS Response Team," "cost considered secondary to guaranteed incident response capability."

**Underlying architectural principle:** Shield Advanced (not Standard) is required whenever a scenario explicitly needs DDoS cost protection, guaranteed DRT engagement, or advanced multi-vector mitigation — Shield Standard's free, automatic protection covers only common, baseline infrastructure-layer attacks with no cost guarantee or dedicated response team access.

---

### Question 8 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A security engineer is building a company-wide threat-detection and compliance strategy spanning GuardDuty, Macie, Inspector, and Security Hub, and wants to sanity-check the team's understanding before assigning ownership of each service to different sub-teams. Select the two statements below that correctly describe a service's actual, documented purpose.

**Options:**
A. Amazon GuardDuty continuously analyzes VPC Flow Logs, DNS query logs, and CloudTrail management/data events using threat intelligence and machine learning to detect anomalous behavior like cryptomining or compromised credentials.
B. Amazon Macie performs automated vulnerability scanning of EC2 instances and container images stored in Amazon ECR against known CVE databases.
C. AWS Security Hub discovers and classifies sensitive data such as PII within S3 buckets, replacing the need for a separate data-classification service.
D. Amazon Inspector performs automated, continuous vulnerability assessments of EC2 instances, container images in ECR, and Lambda functions against known CVEs and network reachability issues.
E. AWS Security Hub itself scans EC2 instances and container images for CVEs, in addition to aggregating findings from other services.

**Correct answer(s):** A, D

**Why correct:** A is accurate — GuardDuty's core purpose is exactly this log-based anomaly and threat detection across VPC Flow Logs, DNS logs, and CloudTrail. D is accurate — Inspector is the automated vulnerability-assessment service for EC2, ECR images, and Lambda against CVEs and network exposure.

**Why each wrong option is wrong:** B swaps Macie's actual purpose (sensitive-data discovery/classification in S3) for Inspector's purpose (vulnerability scanning) — Macie has no CVE-scanning capability at all. C swaps Security Hub's actual purpose (finding aggregation and normalized scoring) for Macie's purpose (data classification) — Security Hub does not scan S3 content for PII itself. E incorrectly gives Security Hub a scanning capability it doesn't have — Security Hub aggregates and normalizes findings that other services (like Inspector) generate; it never performs the underlying vulnerability scan itself.

**Trigger words:** "cryptocurrency-mining traffic or credential compromise" (GuardDuty), "vulnerability assessments... known CVEs" (Inspector), "discovers and classifies sensitive data... PII" (Macie, misattributed to Security Hub in C), "aggregating findings from other services" (Security Hub's real role, contradicted by E's added scanning claim).

**Underlying architectural principle:** GuardDuty = behavioral/log-based threat detection, Macie = S3 sensitive-data discovery/classification, Inspector = vulnerability/CVE scanning of compute resources, Security Hub = cross-service finding aggregation and normalized scoring only — each of the four owns exactly one of these responsibilities with no overlap.

---

### Question 9 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A healthcare company stores patient intake forms, scanned insurance documents, and internal HR files across dozens of S3 buckets accumulated over several years of organic growth. A new compliance mandate requires the company to identify which buckets currently contain personally identifiable information (PII) and protected health information (PHI) so those buckets can be prioritized for tighter access controls, without manually opening and inspecting every object by hand.

**Options:**
A. Enable Amazon Macie and run a sensitive data discovery job across the S3 buckets to automatically identify and classify objects containing PII/PHI.
B. Enable Amazon GuardDuty S3 Protection, since it scans object contents in S3 buckets for sensitive data patterns like PII and PHI.
C. Enable Amazon Inspector's S3 scanning feature to classify object content by sensitivity level.
D. Enable AWS Config with a managed rule that flags any S3 object containing a valid-format social security or medical record number.

**Correct answer(s):** A

**Why correct:** Macie is purpose-built for exactly this task — using machine learning and pattern matching to discover and classify sensitive data types (PII, PHI, financial data, credentials) within S3 objects at scale, without manual inspection, and surfacing findings prioritized by sensitivity and bucket.

**Why each wrong option is wrong:** B misapplies GuardDuty S3 Protection, which monitors S3 data-plane API activity (via CloudTrail S3 data events) for anomalous access patterns and threats — it does not read or classify object content for sensitive data types. C is not a real Inspector capability — Inspector performs vulnerability/CVE and network-reachability scanning of compute resources (EC2, ECR, Lambda), not content classification of S3 objects. D describes AWS Config incorrectly — Config evaluates resource *configuration* state against rules (e.g., "is versioning enabled," "is the bucket public") and has no capability to inspect the actual byte content of objects for PII/PHI patterns.

**Trigger words:** "identify which buckets currently contain personally identifiable information (PII) and protected health information (PHI)," "without manually opening and inspecting every object by hand."

**Underlying architectural principle:** Amazon Macie is the dedicated service for automated, content-level sensitive-data discovery and classification within S3 — no other listed security or compliance service inspects object content for PII/PHI patterns.

---

### Question 10 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company's cloud operations team needs to answer two related but distinct questions during a security incident: first, "exactly which IAM principal called the `TerminateInstances` API, from what source IP, and at what timestamp, for this specific EC2 instance that unexpectedly disappeared last Tuesday," and second, "has the security group attached to our production database instance ever been changed to allow an overly permissive inbound rule, and if so, when and by whom, plus can we get notified automatically the next time it happens." The team needs one service to answer the first question and a different service to answer the second.

**Options:**
A. Use AWS CloudTrail (event history / logs) to answer the first question by locating the specific `TerminateInstances` API call record, and use AWS Config (configuration history plus a custom or managed rule with an EventBridge/SNS notification) to answer the second question about historical and future security group changes.
B. Use AWS Config for both questions, since Config records every API call made in the account including who made it and from where.
C. Use AWS CloudTrail for both questions, since CloudTrail retains a full historical timeline of every resource's configuration state changes, including security group rule history.
D. Use Amazon GuardDuty to answer the first question by identifying the malicious termination event, and use AWS CloudTrail to answer the second question by replaying historical security group configuration snapshots.

**Correct answer(s):** A

**Why correct:** CloudTrail is the service that logs discrete API calls (who, what action, source IP, when) — exactly what's needed to pinpoint the specific `TerminateInstances` call; AWS Config tracks resource *configuration state over time* and supports rules with automated notifications, making it the right tool to answer "was this security group ever changed to something risky, and alert us going forward."

**Why each wrong option is wrong:** B is incorrect — Config does not log individual API calls with caller identity/source IP; it records configuration item snapshots and changes, not action-level audit events. C is incorrect — CloudTrail logs discrete API events, not a queryable timeline of a resource's evolving configuration state; reconstructing "was this SG ever risky" from raw CloudTrail events is far harder than using Config's built-in configuration timeline and rules. D misapplies GuardDuty, which is a behavioral threat detector, not an API audit log lookup tool for a specific already-known API call, and reverses CloudTrail's actual capability (it doesn't "replay configuration snapshots," that's Config's job.

**Trigger words:** "exactly which IAM principal called... from what source IP, and at what timestamp" (CloudTrail), "ever been changed to allow... and if so, when and by whom, plus... notified automatically the next time" (Config).

**Underlying architectural principle:** CloudTrail answers "who did what API action, when, from where" (event/audit log); AWS Config answers "what did this resource's configuration look like over time, and alert me on future non-compliant changes" (configuration state and compliance) — the two are complementary, not interchangeable, services.

---

### Question 11 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A mobile banking app needs to let end users (retail customers, potentially millions) sign up and log in with a username and password or via Google/Facebook social login, and after authenticating, those same users need temporary AWS credentials scoped by IAM role to directly upload profile photos to a specific S3 bucket prefix without routing the upload through the app's backend servers.

**Options:**
A. Use a Cognito User Pool to handle end-user sign-up/sign-in (including social identity provider federation), then use a Cognito Identity Pool to exchange the User Pool token for temporary, IAM-role-scoped AWS credentials for direct S3 access.
B. Use a Cognito Identity Pool alone to handle both the username/password sign-up flow and the temporary AWS credential vending, since Identity Pools natively manage user directories.
C. Create an IAM user for each retail customer with permissions scoped to their own S3 prefix, and distribute long-term access keys to the mobile app on first login.
D. Use AWS IAM Identity Center to federate retail customers as workforce users, granting each a permission set scoped to the specific S3 prefix.

**Correct answer(s):** A

**Why correct:** This is the textbook Cognito two-service pattern: a User Pool is the actual user directory/authenticator (handling sign-up, sign-in, and social/SAML/OIDC federation), while an Identity Pool takes an authenticated identity (from a User Pool or a third party) and exchanges it for temporary, IAM-role-scoped AWS credentials usable directly against services like S3 — exactly the two capabilities the scenario needs in sequence.

**Why each wrong option is wrong:** B is factually backwards — Identity Pools do not manage user directories, sign-up, or password authentication at all; that is the User Pool's job, and Identity Pools only vend AWS credentials for already-authenticated identities. C creates an unscalable, insecure operational nightmare — provisioning a distinct IAM user with long-term access keys per retail customer does not scale to millions of users and violates the strong preference against long-lived credentials for end users. D misapplies IAM Identity Center, which is designed for workforce (employee/partner) identity federation into AWS accounts and permission sets, not for consumer-facing, internet-scale end-user authentication in a mobile app.

**Trigger words:** "end users... sign up and log in... username and password or via Google/Facebook," "temporary AWS credentials scoped by IAM role... direct S3 access... without routing... through the app's backend."

**Underlying architectural principle:** Cognito User Pools handle consumer identity and authentication (who is this user); Cognito Identity Pools convert an authenticated identity into temporary, role-scoped AWS credentials (what can this user directly touch in AWS) — the two are typically used together, in that order, for direct-to-AWS-service mobile/web app access patterns.

---

### Question 12 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A B2B SaaS company wants to allow its enterprise customers' employees to log into the SaaS company's application using the enterprise customer's own existing corporate identity provider (which speaks SAML 2.0), without the SaaS company ever creating or storing separate username/password credentials for those employees, and without the employees needing any direct AWS-level access — they only need to be recognized and authenticated within the SaaS application itself.

**Options:**
A. Configure a Cognito User Pool with a SAML 2.0 identity provider federation, so enterprise employees authenticate against their own corporate IdP and Cognito issues the application-level tokens the SaaS app relies on.
B. Configure a Cognito Identity Pool with a SAML 2.0 identity provider federation, since Identity Pools are the correct entry point for federating external SAML users into an application.
C. Create IAM Identity Center permission sets for each enterprise customer's employees, federated via the enterprise's SAML IdP.
D. Require every enterprise customer to export their employee directory and have the SaaS company create matching Cognito User Pool user records with generated passwords.

**Correct answer(s):** A

**Why correct:** Cognito User Pools natively support federation with external SAML 2.0 (and OIDC) identity providers, letting the SaaS application authenticate users against the enterprise's own IdP and receive standard tokens (ID/access tokens) without ever managing a separate password for those users — precisely the described requirement.

**Why each wrong option is wrong:** B is incorrect because Identity Pools are not the authentication/federation entry point for issuing application-level identity — they only vend temporary AWS credentials after a User Pool (or another identity source) has already authenticated the user, and this scenario has no stated need for direct AWS credential access at all. C misapplies IAM Identity Center, which is intended for workforce access to AWS accounts/applications integrated with AWS SSO, not for embedding customer-facing SAML login into a third-party SaaS application's own user experience. D directly contradicts the explicit requirement to avoid creating/storing separate credentials for enterprise employees, and adds unnecessary manual data-import operational overhead.

**Trigger words:** "own existing corporate identity provider... SAML 2.0," "without... ever creating or storing separate username/password credentials," "no direct AWS-level access."

**Underlying architectural principle:** Cognito User Pools support direct SAML/OIDC federation for application-level authentication with no AWS credential vending required — reach for a User Pool alone (no Identity Pool) whenever the requirement stops at "authenticate the user into my app," and add an Identity Pool only when the user additionally needs temporary AWS credentials.

---

### Question 13 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A gaming company's mobile app allows users to play as a guest without creating an account, but guest users still need to save their game progress to a per-user-scoped DynamoDB partition and upload screenshots to a per-user S3 prefix, using temporary AWS credentials with permissions limited to that specific guest's own data. If the guest later creates a real account, their existing guest-generated data and identity must carry over seamlessly to the newly authenticated identity without starting over.

**Options:**
A. Configure a Cognito Identity Pool with unauthenticated (guest) identities enabled, and when the user later signs up through a linked Cognito User Pool, use identity linking so the unauthenticated identity's unique ID (and its associated data) merges into the newly authenticated identity.
B. Issue a static, shared IAM role's long-term access keys embedded in the app binary for all guest users, since guests don't need individually scoped permissions.
C. Require every guest user to complete Cognito User Pool sign-up before any gameplay begins, eliminating the need for unauthenticated identity support entirely.
D. Use AWS IAM Identity Center's guest access feature to issue temporary, per-guest scoped credentials that automatically convert to authenticated access on sign-up.

**Correct answer(s):** A

**Why correct:** Cognito Identity Pools explicitly support unauthenticated (guest) identities, each with its own unique, per-identity ID and scoped temporary IAM credentials, and natively support merging/linking that guest identity to a subsequent authenticated identity so previously-generated data tied to the guest ID isn't orphaned — directly satisfying both stated requirements.

**Why each wrong option is wrong:** B violates least privilege and basic credential-security hygiene by sharing one static, long-term, embedded credential across every guest user with no per-user scoping or rotation, and directly contradicts the requirement for permissions "limited to that specific guest's own data." C removes the guest-play feature the product explicitly requires, forcing sign-up before any use is allowed. D describes a capability that does not exist — IAM Identity Center is a workforce federation service with no "guest access" feature and no involvement in consumer mobile app identity flows at all.

**Trigger words:** "play as a guest without creating an account," "temporary AWS credentials... limited to that specific guest's own data," "carry over seamlessly to the newly authenticated identity."

**Underlying architectural principle:** Cognito Identity Pools' unauthenticated (guest) identity support, combined with identity linking on later sign-up, is the purpose-built pattern for scoped, per-guest AWS access that seamlessly upgrades to a full authenticated identity without data loss.

---

### Question 14 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A startup is deploying its first public HTTPS website behind an Application Load Balancer and separately needs a TLS certificate for an internal API served through API Gateway with a custom domain. The team wants both certificates issued and renewed with zero manual certificate-signing-request handling or renewal reminders, and wants to avoid ever downloading a private key file that could be mishandled.

**Options:**
A. Request public certificates for both domains through AWS Certificate Manager (ACM), validate ownership via DNS or email validation, and attach the certificates directly to the ALB listener and the API Gateway custom domain — ACM manages issuance and renewal with the private key never leaving AWS.
B. Generate a certificate signing request manually, submit it to a third-party public certificate authority, download the issued certificate and private key, and upload both into IAM for use by the ALB and API Gateway.
C. Use AWS Secrets Manager's built-in certificate-issuance feature to generate and rotate TLS certificates for both the ALB and API Gateway automatically.
D. Rely on the default self-signed certificate that ACM automatically generates for any AWS resource, since ACM defaults to self-signed issuance unless a paid public CA is explicitly configured.

**Correct answer(s):** A

**Why correct:** ACM is purpose-built for exactly this: requesting free public certificates, automating domain validation, keeping the private key material entirely within AWS (never downloadable), and handling automatic renewal before expiration — directly satisfying "zero manual CSR/renewal handling" and "never download a private key."

**Why each wrong option is wrong:** B reintroduces every manual step (CSR generation, third-party submission, private key download/handling, manual renewal tracking) the team explicitly wants to avoid, and also risks private key mishandling. C describes a capability Secrets Manager does not have — it stores and rotates secrets/credentials generically, but it is not a certificate authority and does not issue TLS certificates. D is factually false — ACM does not default to self-signed certificates; it issues certificates from Amazon's trusted public CA (or supports importing third-party certs), and there is no "self-signed by default" behavior.

**Trigger words:** "issued and renewed with zero manual certificate-signing-request handling or renewal reminders," "avoid ever downloading a private key file."

**Underlying architectural principle:** ACM is the default choice for public TLS certificates on AWS-integrated resources (ALB, CloudFront, API Gateway) whenever automated issuance, validation, and renewal with no private-key extraction is required — manual CA processes or third-party certificates should only be used when ACM integration isn't available for the target service.

---

### Question 15 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company needs a public TLS certificate for a legacy on-premises web server that is not fronted by any AWS load balancer, CloudFront distribution, or API Gateway — it's a standalone server in a colocation facility that the company still wants centrally tracked for expiration alongside its AWS-hosted certificates. Separately, the company also needs a private certificate to secure internal service-to-service mTLS traffic between microservices running on EC2 within a VPC, issued from a private CA the company controls rather than a public one.

**Options:**
A. Import the on-premises server's public certificate (obtained from a third-party public CA — not ACM, since ACM-issued public certificates can never be exported for installation outside AWS-integrated services — and installed on the server through its own web server TLS configuration) into ACM using ACM's certificate-import feature purely for centralized expiration tracking and CloudWatch alarms alongside AWS-hosted certificates — noting that ACM does not auto-renew imported certificates — and separately use AWS Certificate Manager Private Certificate Authority (ACM Private CA) to issue the internal mTLS certificates, exporting the certificate and private key for direct installation on the EC2 microservices, from a company-controlled private CA hierarchy.
B. Attach the on-premises server directly to an ALB target group so ACM can automatically manage its certificate, and use a second ACM public certificate for the internal mTLS traffic since ACM only issues one type of certificate.
C. Use AWS Certificate Manager for both needs, since ACM certificates can always be exported as plaintext private keys regardless of validation type or CA source.
D. Use AWS Secrets Manager to generate a self-signed root CA and distribute it manually to both the on-premises server and the internal microservices.

**Correct answer(s):** A

**Why correct:** Public ACM certificates can never be exported — their private keys never leave AWS by design — so a certificate destined for a standalone on-premises server must be obtained/installed outside that constraint; ACM's import feature lets you bring in a certificate you already hold (public or otherwise) purely for centralized expiration visibility and CloudWatch alarms, even though ACM won't renew it for you since it didn't issue it. Separately, ACM Private CA is the purpose-built service for issuing private certificates from a company-controlled CA hierarchy, and — unlike public ACM certificates — its private certificates and their private keys can be exported for direct installation on resources like the EC2 microservices needing mTLS, exactly matching the internal requirement.

**Why each wrong option is wrong:** B is not feasible — an ALB target group cannot make an on-premises, non-AWS server "ACM-managed," and even if the server were reachable as an IP target, an ALB certificate only secures the ALB listener, not the origin server's own TLS stack; the claim that "ACM only issues one type of certificate" also ignores the distinct public-ACM vs. ACM Private CA certificate types. C is false as a blanket statement — standard public ACM certificates are never exportable, full stop, regardless of validation type; only certificates issued by ACM Private CA (private certificates) support export, so treating all ACM certificates as freely exportable plaintext keys is incorrect. D bypasses AWS's managed PKI services entirely in favor of a fully manual, unmanaged self-signed CA process, which does not provide the centralized management, revocation, and lifecycle tracking that ACM Private CA offers, and Secrets Manager has no CA-issuance capability at all.

**Trigger words:** "standalone server in a colocation facility... not fronted by any AWS load balancer," "centrally tracked for expiration," "private certificate... from a private CA the company controls."

**Underlying architectural principle:** Public ACM certificates never leave AWS and can never be exported, but ACM's import feature still lets you centrally track expiration for certificates it didn't issue, extending visibility to non-integrated/on-premises resources without auto-renewal. ACM Private CA is the distinct service for organization-controlled private certificate hierarchies such as internal mTLS, and — unlike public ACM certificates — its private certificates can be exported for installation anywhere, including on-premises or self-managed compute. The two solve different halves of "public vs. private trust" and are not interchangeable.

---

### Question 16 [Priority: P2] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A compliance team must implement continuous, automatic governance over AWS resource configuration in a regulated environment. Specifically, they need to: (1) automatically detect within minutes whenever any security group in the account is modified to allow unrestricted inbound SSH (0.0.0.0/0 on port 22), and trigger an automatic remediation that removes the offending rule; and (2) maintain a complete, tamper-evident record of every management API call made in the account, delivered to a centralized, access-restricted S3 bucket in a separate account for long-term audit retention. Select the two actions that together satisfy both requirements.

**Options:**
A. Enable AWS Config with the managed rule `restricted-ssh` (or an equivalent custom rule) and attach an automatic remediation action (via an SSM Automation document) that removes the non-compliant inbound rule when the rule evaluates as non-compliant.
B. Enable AWS CloudTrail with an organization trail (or a trail with log file validation) delivering logs to a centralized S3 bucket in a dedicated logging account, with bucket policies restricting access to authorized audit roles only.
C. Enable Amazon GuardDuty with the "Automated Remediation" feature to detect and automatically close overly permissive security group rules across the organization.
D. Enable AWS Config alone, since Config natively delivers all management API call history to S3 with the same tamper-evident guarantees as CloudTrail.
E. Enable AWS CloudTrail Insights exclusively, since Insights automatically remediates any detected anomalous security group change without additional configuration.

**Correct answer(s):** A, B

**Why correct:** A directly satisfies requirement 1 — Config continuously evaluates resource configuration against a rule and can trigger automatic remediation via SSM Automation the moment a security group drifts into a non-compliant (open-SSH) state. B directly satisfies requirement 2 — CloudTrail (as an organization/multi-account trail with log file validation) is the API-call audit log service, and centralizing delivery to a separate, access-restricted logging-account bucket is the standard tamper-evident, cross-account audit pattern.

**Why each wrong option is wrong:** C describes a capability GuardDuty does not have — GuardDuty detects and reports findings but has no native "automated remediation" action that modifies security group rules on its own; remediation requires separate automation (e.g., via EventBridge + Lambda/SSM), and it is not the standard tool for configuration-compliance rule evaluation in the first place. D is false — Config records configuration item changes and compliance evaluations, not a full log of every management API call; that is CloudTrail's specific role, and Config does not provide CloudTrail's tamper-evident API audit trail. E is false — CloudTrail Insights only surfaces unusual API activity patterns as findings for human/automated review; it does not itself remediate or reverse any resource change.

**Trigger words:** "automatically detect... and trigger an automatic remediation" (Config), "complete, tamper-evident record of every management API call... centralized... in a separate account" (CloudTrail).

**Underlying architectural principle:** AWS Config drives configuration-compliance detection and automated remediation of drifted resource settings, while CloudTrail provides the immutable, centralized audit trail of API activity — a mature governance posture in a regulated environment requires both services configured for their distinct, non-overlapping purposes.

---

### Question 17 [Priority: P1] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A multinational retailer runs a public e-commerce platform behind CloudFront and an ALB and has been targeted by a coordinated attack combining a volumetric UDP reflection flood against its infrastructure and a simultaneous credential-stuffing campaign against its login API that is also triggering suspicious cross-region API calls in CloudTrail consistent with a compromised IAM access key. The security team has an unlimited emergency budget for this specific incident and needs to select the two actions that most directly and immediately address detecting/mitigating the credential compromise signal and gaining guaranteed expert incident-response support for the ongoing DDoS event, respectively.

**Options:**
A. Engage AWS Shield Advanced's DDoS Response Team (DRT) for hands-on mitigation support and guidance during the active volumetric attack (the account already carries Shield Advanced plus the Business/Enterprise Support plan needed for direct DRT contact, consistent with the described unlimited emergency budget).
B. Review and act on Amazon GuardDuty findings (e.g., anomalous API calls from unusual geolocations, credential compromise indicators tied to the IAM access key) to identify and rotate/disable the compromised credential.
C. Enable AWS WAF's SQL injection managed rule group on the ALB, since SQL injection is the root cause of both the DDoS flood and the credential stuffing.
D. Disable AWS CloudTrail temporarily to stop logging the suspicious API calls until the investigation concludes, reducing log noise for the response team.
E. Rely solely on Shield Standard's automatic mitigations to resolve both the DDoS flood and the credential-stuffing campaign without further action, since Shield Standard covers all attack vectors described.

**Correct answer(s):** A, B

**Why correct:** A directly provides the guaranteed, expert, hands-on DDoS incident response the scenario asks for — this is precisely Shield Advanced's DRT engagement benefit during an active volumetric event. B directly addresses the credential-compromise signal — GuardDuty is the service that surfaces exactly this kind of anomalous-API-call/compromised-credential finding from CloudTrail analysis, enabling the team to identify and act on (rotate/disable) the specific compromised key.

**Why each wrong option is wrong:** C misattributes root cause — SQL injection is unrelated to either a volumetric UDP flood or a credential-stuffing campaign (which is a brute-force login-attempt pattern, not an injection technique), so a SQLi rule group would not mitigate either described attack. D is actively harmful and against security best practice — disabling CloudTrail during an active incident destroys the audit trail needed for investigation and is never an appropriate incident-response action. E is incorrect because Shield Standard only mitigates common, automatic infrastructure-layer (L3/L4) DDoS patterns and provides no application-layer credential-stuffing protection or guaranteed expert engagement — both gaps this multi-vector incident explicitly has.

**Trigger words:** "detecting/mitigating the credential compromise signal" (GuardDuty), "guaranteed expert incident-response support for the ongoing DDoS event" (Shield Advanced DRT), "unlimited emergency budget."

**Underlying architectural principle:** Multi-vector incidents typically require pairing distinct, purpose-specific services — GuardDuty for anomalous-behavior/credential-compromise detection and Shield Advanced's DRT for guaranteed expert DDoS mitigation support — rather than expecting any single free/default service (Shield Standard) or a mismatched control (WAF SQLi rules, disabling audit logging) to cover an attack outside its actual scope.

---

### Question 18 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company operates a VPC with a public subnet hosting a NAT gateway and a private subnet hosting application servers with no public IP addresses. During a security review, an auditor asks the team to explain precisely why an external attacker on the internet cannot directly initiate a connection to the private application servers, even though the private subnet's NACL currently has an inbound allow rule for 0.0.0.0/0 on all ports (an oversight the team plans to fix), and the servers' security groups also currently allow inbound traffic from 0.0.0.0/0 on port 443 (also flagged as needing tightening).

**Options:**
A. Because the application servers have no public IP address and no route from the internet gateway directly to the private subnet, there is no network path for an external attacker's traffic to reach the private subnet at all — the NACL and security group rules are moot for inbound-from-internet traffic given the subnet's routing and addressing, though they should still be tightened as defense-in-depth.
B. Because NACLs always override security groups when both exist, and the NACL rule is misconfigured, the security group's port 443 rule is what's actually preventing the attack.
C. Because the NAT gateway itself blocks all unsolicited inbound connections originating from the internet by inspecting and filtering packet contents for malicious signatures.
D. Because Amazon GuardDuty automatically drops any inbound packet from the internet destined for a private subnet before it reaches the NACL or security group evaluation.

**Correct answer(s):** A

**Why correct:** With no public IP on the instances and no route table entry sending internet-gateway-bound return paths into the private subnet (the private subnet's route table only has a route to the NAT gateway for outbound), there is fundamentally no reachable network path for externally-initiated inbound connections regardless of NACL/SG misconfiguration — routing/addressing is the actual root-cause control here, even though the flagged rules are still real risks worth fixing (e.g., if the instance were later given a public IP, or reachable via some other path).

**Why each wrong option is wrong:** B describes a nonexistent interaction — NACLs and security groups don't "override" each other; both must independently permit traffic, and neither one is what's preventing this specific inbound-from-internet scenario, since the real blocker is the lack of a routable path in the first place. C mischaracterizes the NAT gateway — a NAT gateway translates and forwards traffic that instances in its subnet initiate outbound; it is not a packet-inspection firewall and does not evaluate inbound internet traffic content for malicious signatures, and more fundamentally NAT gateways don't route unsolicited inbound internet traffic to private instances at all by design (no inbound NAT/port-forwarding path exists for a standard NAT gateway). D describes a capability GuardDuty does not have — GuardDuty is a detection service that analyzes logs and generates findings; it has no inline packet-filtering or blocking function anywhere in the data path.

**Trigger words:** "no public IP addresses," "even though the private subnet's NACL currently has an inbound allow rule for 0.0.0.0/0," "precisely why an external attacker... cannot directly initiate a connection."

**Underlying architectural principle:** Network reachability (addressing and routing) is a foundational, independent layer of defense beneath NACLs and security groups — a resource with no public IP and no inbound route from an internet gateway is unreachable from the internet regardless of how permissive its NACL or security group rules are, though those rules should never be relied upon as the only control.

---

### Question 19 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A small internal tool team wants to detect, without deploying any new agents, sensors, or third-party software, whether any of their EC2 instances are communicating with known command-and-control (C2) IP addresses or exhibiting DNS query patterns consistent with malware, using only existing AWS-native log sources they already have available (VPC Flow Logs, DNS logs, CloudTrail) and AWS threat intelligence feeds.

**Options:**
A. Enable Amazon GuardDuty for the account, which analyzes VPC Flow Logs, DNS query logs, and CloudTrail events against AWS and third-party threat intelligence feeds to surface findings like C2 communication and malware-consistent DNS activity — with no agents to deploy.
B. Enable AWS Config with the `ec2-instance-managed-by-systems-manager` managed rule, which flags any instance communicating with known malicious IP addresses.
C. Install the Amazon Inspector agent on every EC2 instance to monitor real-time network connections for command-and-control traffic.
D. Enable Amazon Macie on the VPC, since Macie analyzes network flow logs for malware command-and-control signatures in addition to its S3 data classification role.

**Correct answer(s):** A

**Why correct:** GuardDuty is exactly this: an agentless threat-detection service that continuously analyzes existing log sources (VPC Flow Logs, DNS logs, CloudTrail) against curated threat intelligence to detect things like C2 communication and malicious DNS activity, requiring no new infrastructure or agents to deploy.

**Why each wrong option is wrong:** B misapplies Config, whose managed rules evaluate resource configuration compliance (e.g., "is SSM Agent installed"), not live network threat-intelligence matching against malicious IPs. C contradicts the explicit "without deploying any new agents" requirement, and mischaracterizes Inspector, whose role is vulnerability/CVE assessment, not real-time C2 network monitoring. D incorrectly expands Macie's scope — Macie is scoped specifically to S3 sensitive-data discovery and has no VPC network flow or DNS analysis capability at all.

**Trigger words:** "without deploying any new agents, sensors, or third-party software," "command-and-control (C2) IP addresses," "existing AWS-native log sources... and AWS threat intelligence feeds."

**Underlying architectural principle:** GuardDuty's core value proposition is agentless, continuous threat detection built entirely on log sources AWS accounts already generate, cross-referenced against managed threat intelligence — no separate sensor deployment is ever required.

---

### Question 20 [Priority: P3] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A financial services company operating under strict regulatory audit requirements is designing its Domain 1 security posture end-to-end and must correctly identify, from a mixed list of claims about VPC security and AWS security services, the two statements that are factually accurate based on documented 2026 AWS behavior, in order to avoid embedding incorrect assumptions into its architecture runbook.

**Options:**
A. A subnet can be associated with only one NACL at a time, but a single NACL can be associated with multiple subnets simultaneously.
B. Security group rules are evaluated in a specific numbered priority order, similar to NACL rule numbers, where a lower-numbered rule takes precedence over a higher-numbered one.
C. AWS Config can be configured with an aggregator to evaluate compliance across multiple accounts and regions from a single delegated administrator or aggregator account.
D. Amazon Inspector's EC2 vulnerability scanning works by passively mirroring VPC traffic to an appliance, with no dependency on any agent running on the instance itself.
E. Amazon GuardDuty must be individually enabled and configured separately in every AWS account within an AWS Organization, since it has no native multi-account delegated administrator model.

**Correct answer(s):** A, C

**Why correct:** A is accurate — each subnet has exactly one associated NACL at any time (a default NACL if none is explicitly assigned), while one NACL can be reused across many subnets. C is accurate — AWS Config supports aggregators that consolidate compliance and configuration data across multiple accounts and regions into a single view for a designated aggregator account, a standard multi-account governance pattern.

**Why each wrong option is wrong:** B is false — security groups have no rule-numbering or priority-order concept at all; all rules are evaluated together as an allow-list with no ordering semantics (numbered rule-priority evaluation is specific to NACLs, not security groups). D is false — Inspector's EC2 vulnerability scanning is CVE/package-based, not network-traffic-based: it assesses installed software either through the SSM Agent already running on a managed instance, or, for accounts using Inspector's newer agentless assessment option, by analyzing EBS volume snapshots and instance metadata out-of-band. Neither mechanism involves mirroring live VPC network traffic to an inspection appliance, so the specific mechanism this option describes doesn't match how Inspector works even under its agentless mode. E is false — GuardDuty explicitly supports a multi-account delegated administrator model via AWS Organizations, allowing centralized enablement and finding aggregation across all member accounts from one designated account, contradicting the claim that each account must be configured separately.

**Trigger words:** "only one NACL at a time... multiple subnets simultaneously" (A), "aggregator... single delegated administrator" (C), "no dependency on any agent" (D, contradicted), "individually enabled... in every AWS account" (E, contradicted).

**Underlying architectural principle:** Precise, testable distinctions — NACLs use numbered rule evaluation and a strict one-NACL-per-subnet model while security groups have no rule ordering, and both Config and GuardDuty (like most modern AWS security services) support Organizations-wide delegated administrator/aggregator patterns for centralized multi-account governance — are exactly the kind of "know the exact mechanism, not just the vocabulary" traps the exam favors.

---

*End of Domain 1, Part 2 practice set (20 questions). Distribution: 3 Easy (15%), 8 Medium (40%), 6 Hard (30%), 3 Very Hard (15%); 4 Multiple-Response (20%), 16 Single-Answer (80%). Original content for personal study — not sourced from or reproducing any real/leaked SAA-C03 exam questions.*
