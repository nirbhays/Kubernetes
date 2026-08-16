# AWS SAA-C03 — Choose X, Not Y

> High-value paired distinctions for commonly confused services.

# AWS SAA-C03: "Choose X, Not Y" Cheat Sheet

## Compute

**Spot Instances**
-> interruption-tolerant, stateless workloads (batch, CI/CD, big data) at up to 90% discount

**On-Demand Instances**
-> short-term, unpredictable workloads with no interruption tolerance

---

**Savings Plans / Reserved Instances**
-> steady-state, predictable 24/7 usage over 1-3 yrs for deep discounts

**On-Demand Instances**
-> flexible, no long-term commitment needed

---

**EC2**
-> long-running, stateful, full OS/runtime control

**Lambda**
-> short, event-driven bursts with zero server management

---

**Application Load Balancer (ALB)**
-> HTTP/HTTPS layer 7 routing (path/host-based, microservices)

**Network Load Balancer (NLB)**
-> TCP/UDP layer 4, ultra-low latency, static IP, extreme throughput

---

**Cluster Placement Group**
-> low-latency, high-throughput workloads within a single AZ (HPC, tightly coupled nodes)

**Spread Placement Group**
-> small number of critical instances that must stay on distinct underlying hardware

---

**Target Tracking Scaling**
-> simplest option — maintain one metric (e.g., CPU 50%) automatically

**Step Scaling**
-> fine-grained control — different scaling magnitudes based on alarm breach size

---

## Storage

**EBS**
-> persistent block storage that survives stop/terminate

**Instance Store**
-> ephemeral, high-IOPS temporary storage, lost on stop/terminate

---

**EBS gp3**
-> general-purpose SSD, independently scalable IOPS/throughput, lower cost baseline

**EBS io2 (Block Express)**
-> mission-critical, sub-millisecond latency, highest durability (99.999%)

---

**S3 Standard**
-> frequently accessed, general-purpose object data

**S3 Glacier Deep Archive**
-> long-term archival, retrieved in hours, lowest storage cost

---

**Amazon S3**
-> object storage for unstructured data, unlimited scale, web/app access

**Amazon EFS**
-> POSIX-compliant shared file system, concurrent multi-AZ Linux access

---

**Amazon EFS**
-> Linux NFS shared file storage

**Amazon FSx for Windows File Server**
-> SMB shared storage for Windows-based applications

---

**S3 Versioning**
-> recover from accidental overwrites/deletes, keep object history

**S3 Object Lock**
-> WORM compliance — prevent deletion/modification for regulatory retention

---

**S3 Standard-IA**
-> infrequent access data that still needs multi-AZ resilience

**S3 One Zone-IA**
-> infrequent access, reproducible/non-critical data, single AZ, cheaper

---

**AMI**
-> full launchable image of an instance (OS, config, attached volume snapshots)

**EBS Snapshot**
-> point-in-time backup of a single volume's data only

---

## Database

**RDS Multi-AZ**
-> HA/failover (synchronous standby, same region)

**RDS Read Replica**
-> read scaling (asynchronous, eventually consistent)

---

**Amazon RDS**
-> need a specific engine (SQL Server, Oracle) or off-the-shelf relational DB

**Amazon Aurora**
-> MySQL/PostgreSQL-compatible workload needing higher performance, auto storage scaling, faster failover

---

**Aurora Global Database**
-> multi-region DR with <1s replication lag

**RDS Cross-Region Read Replica**
-> simpler multi-region read scaling, higher replication lag

---

**DynamoDB**
-> NoSQL key-value/document data, massive scale, single-digit ms latency

**RDS**
-> relational data needing complex queries, joins, and transactions

---

**DynamoDB On-Demand Capacity**
-> unpredictable/spiky traffic, pay-per-request

**DynamoDB Provisioned Capacity (+ Auto Scaling)**
-> steady, predictable traffic — cheaper at scale

---

**DynamoDB Accelerator (DAX)**
-> microsecond in-memory caching specifically for DynamoDB

**ElastiCache**
-> general-purpose caching in front of RDS or other data sources

---

**ElastiCache for Redis**
-> persistence, replication, complex data structures, pub/sub needed

**ElastiCache for Memcached**
-> simple, multi-threaded, pure cache with easy horizontal sharding, no persistence

---

## Networking

**NAT Gateway**
-> managed, highly available, auto-scaling outbound internet access

**NAT Instance**
-> self-managed EC2, customizable but manual scaling/HA

---

**Internet Gateway**
-> public subnet resources need direct bidirectional internet access

**NAT Gateway**
-> private subnet resources need outbound-only internet access

---

**VPC Peering**
-> simple 1:1 VPC connections, no transitive routing

**Transit Gateway**
-> hub-and-spoke for many VPCs/on-prem networks, transitive routing at scale

---

**AWS Direct Connect**
-> dedicated, private, high-bandwidth, low-latency connection (slower to provision)

**Site-to-Site VPN**
-> quick setup, encrypted over public internet, lower bandwidth

---

**Route 53 Latency-Based Routing**
-> route users to the region with the lowest latency

**Route 53 Failover Routing**
-> active-passive DR based on health checks

---

**CloudFront**
-> edge-caches HTTP(S) content for static/dynamic web delivery

**Global Accelerator**
-> improves availability/performance for TCP/UDP apps via anycast IPs, multi-region failover

---

**Security Group**
-> stateful, instance-level, allow rules only

**Network ACL**
-> stateless, subnet-level, allow AND deny rules

---

**VPC Gateway Endpoint**
-> free, route-table-based, S3 and DynamoDB only

**VPC Interface Endpoint (PrivateLink)**
-> ENI with private IP, hourly cost, covers most other AWS services

---

**Application Load Balancer**
-> simple, cheap HTTP routing directly to EC2/ECS/Lambda targets

**API Gateway**
-> full API management (throttling, API keys, caching, WebSocket) for serverless APIs

---

## Security

**IAM Role**
-> temporary credentials assumed by services, apps, or federated users

**IAM User**
-> long-term credentials tied to a specific person or application identity

---

**AWS KMS**
-> managed, multi-tenant key service integrated with AWS services

**CloudHSM**
-> dedicated single-tenant HSM for full control, needed for strict compliance (FIPS 140-2 Level 3)

---

**Secrets Manager**
-> automatic credential rotation, built for database/API secrets (higher cost)

**Systems Manager Parameter Store**
-> general config/parameters, free tier, manual rotation

---

**AWS WAF**
-> layer 7 filtering against SQL injection/XSS via custom rules

**AWS Shield**
-> DDoS protection at network/transport layer (L3/L4)

---

**Amazon GuardDuty**
-> continuous threat detection from logs (VPC Flow Logs, CloudTrail, DNS)

**Amazon Inspector**
-> automated vulnerability/CVE assessment of EC2, ECR, and Lambda

---

**Amazon Macie**
-> discovers and protects sensitive data (PII) in S3 using ML

**AWS Config**
-> tracks resource configuration changes and compliance over time

---

**Cognito User Pools**
-> authentication — sign-up/sign-in, user directory

**Cognito Identity Pools**
-> authorization — temporary AWS credentials for federated/guest access

---

## Messaging & Streaming

**SQS Standard Queue**
-> at-least-once delivery, best-effort ordering, unlimited throughput

**SQS FIFO Queue**
-> exactly-once processing, strict ordering, limited throughput

---

**Amazon SQS**
-> pull-based queue for point-to-point decoupling

**Amazon SNS**
-> push-based pub/sub fan-out to multiple subscribers

---

**Amazon SNS**
-> simple pub/sub fan-out from a single source

**Amazon EventBridge**
-> event bus with advanced routing/filtering from many AWS/SaaS/custom sources

---

**Kinesis Data Streams**
-> real-time streaming with ordering, replay, and multiple concurrent consumers

**Amazon SQS**
-> transient queue, message deleted after single consumer processes it

---

**Kinesis Data Streams**
-> fully managed, AWS-native streaming, simpler to operate

**Amazon MSK**
-> managed Apache Kafka for teams needing Kafka APIs/ecosystem

---

## Migration

**AWS DMS**
-> migrates the actual data with minimal downtime (homogeneous or heterogeneous)

**AWS SCT**
-> converts schema/code when source and target database engines differ

---

**AWS Snowball**
-> petabyte-scale (tens of TB per device) offline bulk data transfer

**AWS Snowmobile**
-> exabyte-scale transfer via a literal shipping container/truck

---

## Cost & Management

**Cost Explorer**
-> visualize and forecast historical spend

**AWS Budgets**
-> set thresholds and get alerts on spend/usage

---

**Trusted Advisor**
-> broad best-practice checks across cost, security, fault tolerance, performance, limits

**Compute Optimizer**
-> ML-based rightsizing recommendations specifically for EC2, ASG, EBS, Lambda

---

**Service Control Policy (SCP)**
-> sets maximum permission guardrails across accounts in an Organization (doesn't grant access itself)

**IAM Policy**
-> grants actual permissions to a specific user, role, or group within an account

---

**AWS CloudFormation**
-> infrastructure as code, precise control over all AWS resources

**Elastic Beanstalk**
-> PaaS, quick deploy for standard web apps without managing underlying infra details
