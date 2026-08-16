"""
Generate a full set of visual-learner diagrams for the AWS SAA-C03 study program.

Theme: "The Orbital Colony" — AWS reimagined as a self-sufficient space
station. Security & IAM = Security Checkpoint (badge/airlock control),
Compute = Habitation & Fabrication Modules, Networking = Docking Bays &
Transit Tubes, Storage = The Cargo Vault Bay, Databases = The Central
Databank, Serverless & Integration = The Automated Drone Relay,
Monitoring & Governance = The Command Bridge, Resilience & DR = Redundant
Life-Support Sectors, Cost & Org = Mission Control Budget Office.

Every diagram is designed to read at two depths at once:
  1. A 3-second glance via bold color-coded metaphor + icons (the big idea)
  2. A 30-second read via small precise technical labels (real AWS service
     names, console fields, or exact CLI/ARN syntax) placed next to each
     metaphor element

Usage:
    python "AWS SAA/scripts/generate_aws_saa_diagrams.py" [key1 key2 ...]

    With no arguments, generates every diagram that doesn't already exist
    on disk (safe to re-run / resume). Pass one or more diagram keys to
    force-regenerate just those.

Requires:
    - google-genai SDK (pip install google-genai)
    - GOOGLE_API_KEY or GEMINI_API_KEY environment variable
"""

import os
import sys
from pathlib import Path

from google import genai
from google.genai.types import GenerateContentConfig, ImageConfig

MODEL_ID = "gemini-3-pro-image-preview"
OUTPUT_DIR = Path(__file__).parent.parent / "images"
IMAGE_SIZE = "4K"          # highest resolution the model supports
ASPECT_RATIO = "16:9"      # landscape, matches the diagram layouts below

# ---------------------------------------------------------------------------
# Shared style guide — the visual "constitution" every diagram must obey
# ---------------------------------------------------------------------------

STYLE_GUIDE = """
STRICT VISUAL STYLE — "The Orbital Colony" theme, rendered as an ELEGANT
HAND-DRAWN TECHNICAL SKETCH (premium consulting-notebook / architect's
sketchbook aesthetic, NOT a cartoon, NOT a flat corporate infographic).
Follow exactly:

- Background: warm off-white paper texture (#FBF9F4), extremely subtle and
  barely visible — like fine cold-press illustration paper, no visible grid
- MEDIUM: fine-line pen-and-ink illustration with confident, precise,
  slightly organic linework (variable line weight, like a skilled architect
  or editorial illustrator sketched it by hand) — NOT flat vector shapes,
  NOT 3D render, NOT photorealistic, NO drop shadows, NO clip-art look
- COLOR TREATMENT: restrained, elegant light watercolor-style ink washes for
  fills (soft, slightly uneven edges, translucent — like watercolor bleeding
  gently within the ink linework), never solid flat corporate fill. Overall
  palette stays muted and sophisticated — think a high-end architecture
  firm's concept sketch, not a children's book
- DOMAIN COLOR CODING (use consistently as watercolor-wash tints — this is
  the same visual language across the whole diagram series so the reader
  learns to recognize domains by color):
    Royal Purple wash (#8E44AD)          -> Security & IAM ("Security Checkpoint")
    Forest Green wash (#1E8A5F)          -> Compute ("Habitation & Fabrication Modules")
    Sky Blue wash (#2E86DE)              -> Networking ("Docking Bays & Transit Tubes")
    Warm Amber wash (#E67E22)            -> Storage ("The Cargo Vault Bay")
    Deep Navy + Gold ink (#1A2B4A/#D4AF37) -> Databases ("The Central Databank")
    Teal wash (#16A085)                  -> Serverless & Integration ("The Automated Drone Relay")
    Slate Grey wash (#5D6D7E)            -> Monitoring & Governance ("The Command Bridge")
    Alert Red wash (#C0392B)             -> Resilience & DR ("Redundant Life-Support Sectors")
    Neutral Grey wash (#8A8A8A)          -> Cost & Org / Meta-Strategy ("Mission Control Budget Office")
- TWO READING DEPTHS on every element (this is critical — and typography must
  stay crisp and professionally TYPESET even though the illustration is
  sketched):
    (a) A confident hand-drawn icon + short plain-English metaphor label in
        clean, elegant, perfectly legible typeset lettering (NOT sloppy
        handwriting — think refined hand-lettering used in premium editorial
        infographics), readable instantly from across a room
    (b) A small precise monospace technical caption directly beneath or
        beside it giving the REAL AWS service name, console field, or exact
        CLI/API concept (e.g. metaphor "Badge Kiosk" + technical caption
        "IAM Role + STS AssumeRole"). This caption is always CRISP, sharp,
        perfectly legible dark-ink monospace typography — never sketched or
        stylized, it must be as readable as a printed textbook, since the
        reader will zoom in on it for exam-critical accuracy
- Title: elegant serif hand-lettered display heading at the top center, with
  a single fine hand-drawn underline stroke in that diagram's domain color
- A small "Complexity Layer" tag in the top-left corner, drawn like a
  notebook sticky-tab, reading one of: "Layer 1 — Foundational",
  "Layer 2 — Operational", "Layer 3 — Exam-Critical" (specified per diagram)
- A compact, elegant legend box in the bottom-right corner (drawn like a
  small index card) mapping each color wash used in THIS diagram to its
  domain name
- MAXIMUM PROFESSIONAL POLISH: composition is clean and uncluttered with
  generous whitespace, confident linework, gallery-quality finish — this
  should look like a single beautiful page from a very expensive technical
  book, not a rough doodle
- Crisp, perfectly legible text at every size, in sharp focus everywhere —
  this will be viewed at full resolution and zoomed in on
- Ultra-high resolution, landscape, maximum render quality, fine
  anti-aliased ink-line edges, no compression artifacts
"""


def diagram(key, filename, title, layer, domain_note, body):
    return {
        "key": key,
        "filename": filename,
        "prompt": f"""{STYLE_GUIDE}

TITLE: "{title}"
COMPLEXITY LAYER TAG (top-left): "{layer}"
{domain_note}

{body}
""",
    }


# ---------------------------------------------------------------------------
# Diagram set
# ---------------------------------------------------------------------------

DIAGRAMS = [
diagram(
    "00a-colony-domain-map",
    "aws-saa-00a-colony-domain-map.jpg",
    "The AWS SAA Colony Map",
    "Layer 1 — Foundational",
    "Neutral Grey #8A8A8A base, with each sector tinted by its own domain's accent color.",
    """
Draw a top-down blueprint MAP of the entire orbital colony, divided into four
irregular sectors whose floor AREA is drawn proportional to its official
SAA-C03 exam domain weight, so the viewer can visually compare importance at
a glance. The largest sector, tinted Royal Purple, is the "Security
Checkpoint Sector" with badge kiosks and airlocks, technical caption
"Design Secure Architectures - 30% of exam". The second sector, tinted a
blend of Forest Green and Alert Red, is the "Habitation & Redundant
Life-Support Sector" showing duplicate oxygen tanks and backup generators,
technical caption "Design Resilient Architectures - 26% of exam". The third
sector, tinted a blend of Sky Blue and Amber, is the "Docking Bays & Cargo
Vault Sector" full of loading cranes and storage crates, technical caption
"Design High-Performing Architectures - 24% of exam". The smallest sector,
tinted Neutral Grey, is "Mission Control Budget Sector" with ledgers and
dimmed lights, technical caption "Design Cost-Optimized Architectures - 20%
of exam". Connect all four sectors with glowing transit tubes meeting at a
central hub, and place a compass rose in one corner labeled "Priority
Compass: P0 = Colony Core, P3 = Outer Ring", with faint concentric rings
radiating outward from the hub to reinforce the priority gradient.
""",
),
diagram(
    "00b-well-architected-wheel",
    "aws-saa-00b-well-architected-wheel.jpg",
    "The Well-Architected Command Wheel",
    "Layer 1 — Foundational",
    "Neutral Grey #8A8A8A base, with each spoke tinted by its own pillar's accent color.",
    """
Draw a large ship's steering wheel mounted in the colony's command deck, with
exactly six spokes radiating from a glowing center hub. Each spoke ends in a
handle labeled with one Well-Architected pillar and a short technical
caption stating its exam-relevant lesson. Spoke one, "Operational
Excellence", caption "automate operations, make small reversible changes".
Spoke two, tinted Royal Purple, "Security", caption "least privilege,
defense in depth across every layer". Spoke three, tinted Forest Green,
"Reliability", caption "design to recover from failure, scale horizontally
not vertically". Spoke four, tinted Sky Blue, "Performance Efficiency",
caption "use the right tool for the job, prefer serverless where possible".
Spoke five, tinted Amber, "Cost Optimization", caption "pay only for what
you use, right-size continuously". Spoke six, tinted a soft teal,
"Sustainability", caption "maximize utilization, minimize environmental
footprint". The center hub is engraved with "Well-Architected Framework - 6
Pillars", and a helmsman colonist grips two opposite spokes simultaneously,
visually implying that pillars are trade-offs balanced together rather than
optimized in isolation, a common exam trap where students wrongly assume one
pillar always wins.
""",
),
diagram(
    "00c-cost-decision-tree",
    "aws-saa-00c-cost-decision-tree.jpg",
    "The Budget Office Decision Tree",
    "Layer 1 — Foundational",
    "Neutral Grey #8A8A8A base, with Amber accents marking cost-optimized outcomes.",
    """
Draw the interior of Mission Control's Budget Office as a wall of branching
pipes and valves forming a decision tree. The first valve is labeled "Is
compute usage steady and predictable?" A pipe branches right labeled "YES"
into a glowing Amber tank captioned "Reserved Instances / Savings Plans -
commit for discount". A pipe branches left labeled "NO" into a second valve
"Is the workload interruption-tolerant?", which itself branches into a
spiky, cheap-looking tank captioned "Spot Instances - up to 90% off, can be
reclaimed" and a standard tank captioned "On-Demand - pay full price, no
commitment, use for unpredictable spikes". Below this, a second smaller
pipe cluster for storage begins at a valve "How often is this data
accessed?" descending a ladder of tanks labeled "S3 Standard", "S3
Standard-IA", "S3 Glacier Instant/Flexible Retrieval", "S3 Glacier Deep
Archive", captioned "S3 Storage Class lifecycle - colder tiers = cheaper but
slower retrieval". A third small pipe cluster for databases starts at "Is
the workload read-heavy?" branching to a tank "Read Replica / DAX cache" and
a separate valve "Need high availability?" branching to "Multi-AZ
deployment - failover, not for read scaling", with a warning flag noting
this common exam trap: Multi-AZ improves availability, not read throughput.
""",
),
diagram(
    "00d-readiness-dashboard",
    "aws-saa-00d-readiness-dashboard.jpg",
    "The Launch Readiness Dashboard",
    "Layer 1 — Foundational",
    "Neutral Grey #8A8A8A base, with each gauge tinted by its own domain's accent color.",
    """
Draw a mission-control dashboard console studded with four large round
analog gauges arranged in a row, each wired down into a central console with
thick cables. The first gauge, rimmed in Royal Purple, is labeled "Security"
and its needle sits in a yellow "not yet green" zone, technical caption
"IAM least-privilege audits, encryption at rest/in transit reviewed?". The
second gauge, rimmed in a Forest Green and Alert Red blend, is labeled
"Resilience", needle also short of green, caption "Multi-AZ, backups, and
failover drills completed?". The third gauge, rimmed in Sky Blue, is labeled
"Performance", needle short of green, caption "caching, auto scaling, and
right-sized instance types validated?". The fourth gauge, rimmed in Amber,
is labeled "Cost", needle short of green, caption "budgets, Savings Plans,
and storage lifecycle policies confirmed?". All four gauges feed thick
conduits down into one oversized master lever at the bottom of the console,
labeled "AUTHORIZE EXAM LAUNCH", currently locked shut with a heavy padlock
and chain. A small brass plaque beneath the lever reads "Do not pull until
every gauge reads GREEN across 5 mock exams", with a mission clock on the
wall ticking down as a reminder that readiness, not urgency, should trigger
launch.
""",
),
diagram(
    "01-iam-badge-checkpoint",
    "aws-saa-01-iam-badge-checkpoint.jpg",
    "IAM — The Badge Issuing Checkpoint",
    "Layer 3 — Exam-Critical",
    "Royal Purple wash (#8E44AD) - The Security Checkpoint (badge/airlock control).",
    """
Draw an airlock security checkpoint at the colony's entrance. A badge-printing
kiosk labeled "IAM" issues badges to three figures in a queue: a colonist
labeled "User", a group of colonists under one banner labeled "Group", and a
robot labeled "Role" whose badge visibly expires and reprints itself every few
minutes. Technical caption beneath the kiosk: "IAM Policies (JSON) attached to
Users / Groups / Roles". A guard scans each badge against a policy checklist
on a clipboard with three stacked stamps reading "Explicit Deny", "Explicit
Allow", "Default Deny", technical caption "policy evaluation order: explicit
Deny > explicit Allow > implicit/default Deny". Show one colonist turned away
at the gate with a red X stamped on their badge and a caption "Access Denied
- no matching Allow statement found (trap: missing Allow ≠ Deny statement)".
In the background, a supervisor's booth labeled "Root Account" sits locked
and unused behind a sign reading "Do not use for daily tasks - break glass
only", with a smaller kiosk beside it labeled "IAM Identity Center / SSO"
routing most traffic through federated badges instead.
""",
),
diagram(
    "02-sts-assumerole-trust",
    "aws-saa-02-sts-assumerole-trust.jpg",
    "STS AssumeRole — The Cross-Colony Trust Handshake",
    "Layer 3 — Exam-Critical",
    "Royal Purple wash (#8E44AD) - The Security Checkpoint (badge/airlock control).",
    """
Draw a docking gate between two orbital colonies connected by a narrow bridge.
A visitor colonist from "Colony B (Account B)" walks up to a gate agent on
"Colony A (Account A)" side, presenting a folded document labeled "Trust
Policy - who may enter". The gate agent checks a second document pinned to
the gate labeled "Permissions Policy - what they may do once inside",
technical caption "both trust policy AND permissions policy must allow the
action". The agent hands the visitor a glowing wristband labeled "Temporary
Security Credentials" with a visible countdown ring shrinking from 1hr to 0,
technical caption "sts:AssumeRole - session duration configurable, default
1 hour, max defined by role". A control panel beside the gate reads
"AssumeRoleWithWebIdentity" and "AssumeRoleWithSAML" as alternate entry
lanes for federated visitors. A trap callout sign hangs nearby: "Cross-account
S3 access denied? Check both the bucket policy on Colony A AND the IAM
policy on the visitor's role." A wristband on the ground has gone dark and
faded, captioned "expired credentials - must re-assume role".
""",
),
diagram(
    "03-kms-envelope-encryption",
    "aws-saa-03-kms-envelope-encryption.jpg",
    "KMS — The Vault-Within-a-Vault",
    "Layer 3 — Exam-Critical",
    "Royal Purple wash (#8E44AD) - The Security Checkpoint (badge/airlock control).",
    """
Draw the colony's deepest storage bay: a massive circular vault door labeled
"CMK - Customer Master Key (KMS)" that never leaves the wall it is bolted to.
In front of it, a technician requests a key from a small dispensing slot,
technical caption "kms:GenerateDataKey API call". The slot dispenses two
copies of a small silver key: one "Plaintext Data Key" used to lock a
supply crate labeled "Your Data" on the spot, and one "Encrypted Data Key"
that gets clipped to the outside of the crate itself. The plaintext key then
visibly dissolves into vapor with a caption "plaintext key discarded from
memory immediately after use", while the crate travels away sealed, showing
technical caption "envelope encryption - data encrypted locally, data key
encrypted by CMK, both stored together". A second smaller crate arriving
later needs unlocking: the encrypted data key is sent back through the vault
door slot and returns as a plaintext key to open it, caption "kms:Decrypt".
Beside the vault door, two separate guard posts stand: one holding a "Key
Policy" scroll and another holding an "IAM Policy" scroll, joined by a chain,
trap callout: "Both the key policy AND an IAM policy must grant access -
missing either one causes AccessDenied."
""",
),
diagram(
    "04-sg-vs-nacl-gates",
    "aws-saa-04-sg-vs-nacl-gates.jpg",
    "Security Groups vs NACLs — Stateful Guard vs Stateless Checkpoint",
    "Layer 3 — Exam-Critical",
    "Royal Purple wash (#8E44AD) - The Security Checkpoint (badge/airlock control).",
    """
Split the scene down the middle. On the left, inside a habitat pod's doorway,
a personal bodyguard stands labeled "Security Group", who waves a colonist
out and, remembering their face, automatically waves them back in without
rechecking, technical caption "stateful - return traffic automatically
allowed" and "operates at instance/ENI level, allow rules only (no explicit
deny)". On the right, at the outer wall of the colony sector, a checkpoint
gate has two completely separate lanes labeled "Inbound Rules" and "Outbound
Rules" leading through the same wall, technical caption "NACL - stateless,
subnet-level, must define BOTH inbound and outbound rules". Each lane has
numbered rule signs (100, 200, 300...) checked in strict ascending order
until a match is found, with some signs marked green "ALLOW" and others red
"DENY", technical caption "NACLs support explicit Deny; Security Groups do
not". A trap callout sign flashes at the checkpoint: "Response traffic
blocked! Remember: NACL is stateless - an inbound Allow does NOT
automatically allow the matching outbound reply." A confused colonist stands
stuck between the gates, luggage in hand, unable to get a reply message out.
""",
),
diagram(
    "05-waf-shield-perimeter",
    "aws-saa-05-waf-shield-perimeter.jpg",
    "WAF & Shield — The Outer Perimeter Shield",
    "Layer 3 — Exam-Critical",
    "Royal Purple wash (#8E44AD) - The Security Checkpoint (badge/airlock control).",
    """
Draw the colony encased in a shimmering translucent energy dome labeled
"AWS Shield", deflecting a storm of incoming meteors labeled "DDoS - volumetric
/ SYN flood attack" harmlessly off its surface, technical caption "Shield
Standard - automatic, free, enabled for every AWS customer". A reinforced
section of the dome glows brighter, labeled "Shield Advanced", with a small
console beside it reading "24/7 DDoS Response Team + cost protection", caption
"paid tier for high-value / high-risk workloads". Just inside the dome, a
fine wire mesh filter layer intercepts smaller individual objects trying to
slip through gaps, labeled "AWS WAF", technical caption "Web ACL - Rule
Groups inspect HTTP/HTTPS requests". Show the mesh catching specific labeled
projectiles: one marked "SQL Injection", one marked "Cross-Site Scripting
(XSS)", and one marked "Bad Bot / known malicious IP", each with a small
"Managed Rule Group" tag. A control tower nearby shows a rate meter reading
"Rate-based rule: >2000 req/5min from single IP" triggering a gate to
temporarily seal shut. A trap callout: "WAF works at Layer 7 (Application) -
it does not stop network-layer floods; that's Shield's job."
""",
),
diagram(
    "06-secrets-vs-parameter-store",
    "aws-saa-06-secrets-vs-parameter-store.jpg",
    "Secrets Manager vs Parameter Store — Two Supply Lockers",
    "Layer 3 — Exam-Critical",
    "Royal Purple wash (#8E44AD) - The Security Checkpoint (badge/airlock control).",
    """
Draw a supply room with two lockers standing side by side. The left locker
is labeled "Secrets Manager", fitted with an ornate rotating combination
dial, and a small robot arm reaches out on a visible timer track labeled
"automatic rotation schedule (e.g. every 30 days)" to spin the dial to a new
combination, technical caption "native rotation for RDS, Redshift, DocumentDB
via Lambda rotation function" and a price tag reading "$0.40/secret/month +
API calls". The right locker is labeled "Systems Manager Parameter Store",
plainer with a simple keyed lock and a static combination card taped to it,
technical caption "Standard tier - free, manual rotation only" and a second
smaller tag "Advanced tier - higher limits, added cost". Both lockers hold
glowing items labeled "database passwords / API keys / config values", with
an arrow from each locker to an application pod labeled "retrieved at
runtime via SDK/API call, not hardcoded". A trap callout sign between them
reads: "Need automatic rotation of a database credential? Use Secrets
Manager, not Parameter Store." A dusty, forgotten combination card lies on
the floor near the Parameter Store locker labeled "manual rotation - often
forgotten".
""",
),
diagram(
    "07-ec2-instance-families-dock",
    "aws-saa-07-ec2-instance-families-dock.jpg",
    "EC2 Instance Families — The Module Fabrication Dock",
    "Layer 2 — Operational",
    "Forest Green wash (#1E8A5F) - Habitation & Fabrication Modules",
    """
Draw a fabrication dock with a conveyor line producing distinct module shapes,
each destined for a different colony role. A lean, angular, stripped-down
module speeds down the line labeled "Compute-Optimized", technical caption
"high vCPU-to-memory ratio — batch processing, HPC, video encoding". A
wide-bellied module with bulging cargo tanks rolls out labeled
"Memory-Optimized", technical caption "high RAM footprint — in-memory caches,
large databases". A squat module with a visible thruster array and glowing
exhaust vents is labeled "GPU / Accelerated Computing", technical caption
"hardware accelerators — ML training, graphics rendering". A balanced,
general-purpose module with even proportions sits at the head of the line
labeled "General Purpose", technical caption "balanced compute/memory/network
— default choice for most workloads". A dock foreman holds a clipboard titled
"Instance Type Selection" with an exam-trap sticky note: "picking oversized
GPU modules for a simple web server wastes budget — right-size to workload".
Storage-optimized module with high-speed cargo rails sits nearby, technical
caption "high IOPS local storage — databases, data warehousing".
""",
),
diagram(
    "08-asg-elastic-bay",
    "aws-saa-08-asg-elastic-bay.jpg",
    "Auto Scaling Groups — The Elastic Habitation Bay",
    "Layer 2 — Operational",
    "Forest Green wash (#1E8A5F) - Habitation & Fabrication Modules",
    """
Draw an accordion-style habitation bay built from folding wall segments that
physically expand and contract along a track. A large pressure gauge mounted
on the bay's exterior needle-swings toward "high" as crowding increases,
technical caption "scaling metric — e.g. average CPU utilization". Two fence
posts bracket the far ends of the accordion track, labeled "Min" and "Max",
technical caption "MinSize / MaxSize — hard boundaries on group capacity", with
a middle marker labeled "Desired Capacity". As the gauge climbs past a red
line, extra wall segments unfold automatically, technical caption "target
tracking scaling policy — maintain metric at target value". A colony medic
robot patrols the bay checking each habitation pod's vital signs; a pod
flashing red is yanked out and instantly replaced with a fresh one from a
supply chute, technical caption "health check failure — instance terminated
and replaced automatically". A dispatcher panel on the wall reads "Launch
Template" showing the blueprint used to fabricate every new pod. Small
warning icon near the Max fence: "exam trap — scaling has a ceiling, requests
beyond Max are queued or rejected".
""",
),
diagram(
    "09-spot-ondemand-reserved-tickets",
    "aws-saa-09-spot-ondemand-reserved-tickets.jpg",
    "Spot vs On-Demand vs Reserved — The Ticket Pricing Booth",
    "Layer 2 — Operational",
    "Forest Green wash (#1E8A5F) - Habitation & Fabrication Modules",
    """
Draw a colony transit ticket booth with three service windows side by side.
The left window has a flickering "Standby Discount" sign and a posted warning
"You may be bumped with 2 minutes' notice", technical caption "Spot Instances
— steep discount, reclaimed via interruption notice when capacity is needed
elsewhere". The middle window is a plain walk-up counter with a static price
board reading "Pay As You Go", technical caption "On-Demand — full hourly
rate, no commitment, ideal for unpredictable or short-term workloads". The
right window requires travelers to sign a long-term contract scroll before
receiving a "Season Pass", technical caption "Reserved Instances / Savings
Plans — 1 or 3 year commitment term in exchange for significant discount".
A colonist juggling three boarding passes stands at a signpost labeled
"Cost Optimization Pillar", visually weighing discount against risk. An exam
trap caption floats above the Spot window: "trigger word 'fault-tolerant,
flexible start time, can be interrupted' → Spot is the answer". Behind the
booth, a ledger board tallies "Total Colony Compute Bill" ticking down as more
tickets shift from the middle to the outer windows.
""",
),
diagram(
    "10-placement-groups",
    "aws-saa-10-placement-groups.jpg",
    "Placement Groups — Module Arrangement Strategies",
    "Layer 2 — Operational",
    "Forest Green wash (#1E8A5F) - Habitation & Fabrication Modules",
    """
Draw an overhead schematic of the colony ring showing three side-by-side
arrangement diagrams, each a cluster of small habitation modules. The first
diagram shows modules bolted edge-to-edge in a tight huddle labeled "Cluster
Placement Group", technical caption "low-latency, high-throughput networking
— but shared failure domain, one power outage takes them all down". The second
diagram shows modules deliberately scattered into separate isolated sections
of the ring, each on its own support strut, labeled "Spread Placement Group",
technical caption "each instance on distinct underlying hardware — maximizes
fault isolation, limited to a handful of instances per group per zone". The
third diagram shows modules organized into labeled rack partitions with clear
dividing walls, labeled "Partition Placement Group", technical caption "groups
of instances share racks, but partitions are isolated from each other —
used for large distributed systems like HDFS or Kafka". A colony architect
stands at a drafting table comparing the three layouts with a caption:
"exam trap — 'lowest network latency between instances' always points to
Cluster, not Spread".
""",
),
diagram(
    "11-lambda-coldstart-concurrency",
    "aws-saa-11-lambda-coldstart-concurrency.jpg",
    "Lambda — The Instant Fabricator Drone",
    "Layer 2 — Operational",
    "Forest Green wash (#1E8A5F) - Habitation & Fabrication Modules",
    """
Draw a small autonomous fabricator drone hovering in a dedicated bay with no
crew present. When an event signal light flashes, the drone briefly emits a
warming glow before snapping into action, technical caption "cold start —
brief initialization delay when no warm execution environment is available".
Once warmed, it stamps out finished units instantly on repeat triggers,
technical caption "warm start — reused execution environment, near-zero
latency". A control dial on the bay wall shows multiple ghostly duplicate
drones spawning in parallel from a single blueprint when many event signals
arrive at once, capped by a marked limit line, technical caption "concurrency
limit — maximum simultaneous function executions, configurable reserved
concurrency". A conveyor of event triggers feeds the bay: a message pod, a
storage-upload chute, and a scheduled clock icon, technical caption
"event-driven invocation — triggered by S3, SQS, API Gateway, EventBridge,
etc.". A billing meter beside the dock ticks only while a drone is actively
fabricating, technical caption "pay-per-invocation and duration — no charge
while idle". Exam trap sign on the wall: "long-running, stateful, or
sub-millisecond-latency workloads — Lambda is the wrong tool, not this bay".
""",
),
diagram(
    "12-ecs-eks-fargate-modules",
    "aws-saa-12-ecs-eks-fargate-modules.jpg",
    "ECS vs EKS vs Fargate — Crewed vs Serverless Module Bays",
    "Layer 2 — Operational",
    "Forest Green wash (#1E8A5F) - Habitation & Fabrication Modules",
    """
Draw three neighboring module bays on the colony ring, each housing rows of
small standardized cargo containers. The first bay has a colony-native crew
chief in Bosch-orange coveralls directing containers onto docking clamps
using the colony's own rulebook, labeled "ECS", technical caption "AWS-native
container orchestration — Task Definitions and Services managed by AWS's own
control plane". The second bay operates under a thick universal rulebook
stamped with a ship's wheel emblem recognized across many other colonies and
starfleets, labeled "EKS", technical caption "managed Kubernetes control
plane — portable orchestration standard usable across cloud providers and
on-premises". The third bay is eerily quiet: containers simply materialize
onto docking clamps and start running with no crew chief, no visible dock
machinery, and no maintenance crew in sight, labeled "Fargate", technical
caption "serverless compute engine for containers — no EC2 instances or
servers to provision, patch, or scale manually". A signpost between all three
bays reads "Choose based on: need Kubernetes portability? need direct server
control? or want zero infrastructure management?" with an exam trap note:
"'no server management' or 'no capacity planning' in the question stem →
Fargate is the answer".
""",
),
diagram(
    "13-vpc-anatomy",
    "aws-saa-13-vpc-anatomy.jpg",
    "VPC Anatomy — The Colony Transit Grid Blueprint",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Draw a cutaway architectural blueprint of the colony's entire transit grid,
labeled "VPC" in bold at the top corner with a stenciled address range
"10.0.0.0/16" beside it as a technical caption reading "CIDR block". Inside
the blueprint, show several numbered transit tube segments branching off the
main grid, each stamped with its own smaller address range like
"10.0.1.0/24", technical caption "Subnet — must fall within VPC CIDR". At the
grid's center, draw a rotating switching junction wheel with tube-connectors
plugged into it, technical caption "Route Table — determines where traffic
from a subnet is directed" and a smaller label "Route Table Association"
showing dotted lines linking specific tubes to the wheel. On the outer wall
of the blueprint, draw a reinforced docking port opening to a starfield
background, technical caption "Internet Gateway (IGW) — attached to VPC,
enables route to 0.0.0.0/0". Include a small warning icon near an
unconnected tube segment reading "Subnet without route to IGW = no internet
access, even if 'public' by name — exam trap". Add a legend corner listing
Availability Zones as parallel blueprint layers.
""",
),
diagram(
    "14-public-private-subnet-nat",
    "aws-saa-14-public-private-subnet-nat.jpg",
    "Public vs Private Subnets & NAT Gateway",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Split the scene into two parallel transit tube segments side by side. The
left segment has a wide-open airlock directly exposed to starry open space,
technical caption "Public Subnet — has route to Internet Gateway (0.0.0.0/0
via IGW)", with colonist modules freely floating in and out through the
airlock. The right segment is fully sealed with reinforced plating on its
outer wall, technical caption "Private Subnet — no direct route to IGW", and
colonist modules inside look boxed in. A small outbound-only relay drone
sits at a hatch on the sealed wall, ejecting request-pods outward into space
but visibly blocking anything from re-entering, technical caption "NAT
Gateway — placed in public subnet, gives private subnet outbound internet
access without inbound reachability". Draw a dotted route line from the
private segment's route table through the relay drone's hatch to the open
airlock's docking port. Add a callout bubble near the NAT drone reading
"Exam trap: NAT Gateway must live in a PUBLIC subnet, and needs its own
Elastic IP", with a small icon of an EIP tag attached to the drone.
""",
),
diagram(
    "15-peering-vs-transit-gateway",
    "aws-saa-15-peering-vs-transit-gateway.jpg",
    "VPC Peering vs Transit Gateway — Direct Tube vs Central Hub",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Split the scene into two panels. Left panel: two colony segments connected
by exactly one straight reinforced tube, technical caption "VPC Peering —
one-to-one connection, non-transitive". Beside it, draw a third segment
floating nearby with no tube reaching it, and a broken dotted line trying to
route through the peered segment, crossed out with a red X and caption
"Peering is non-transitive — Segment C cannot reach Segment A through
Segment B's peering link, even though B is connected to both — exam trap".
Right panel: a central hub station in the middle with many spoke tubes
radiating outward to a dozen surrounding colony segments, technical caption
"Transit Gateway — central hub, transitive routing across many VPCs". Behind
the hub panel, sketch a faded tangle of dozens of crisscrossing direct tubes
connecting every segment to every other segment, stamped with a red
"DON'T DO THIS AT SCALE" banner and caption "Full-mesh peering — becomes
unmanageable as VPC count grows". Show a small route table icon on the hub
station reading "Transit Gateway Route Table — controls attachment
reachability".
""",
),
diagram(
    "16-direct-connect-vs-vpn",
    "aws-saa-16-direct-connect-vs-vpn.jpg",
    "Direct Connect vs Site-to-Site VPN — Dedicated Cable vs Encrypted Relay",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Draw an Earth-based mission control tower on one side and the orbital colony
on the other. Between them, show a thick physical gangway cable, individually
laid and bolted at both ends, technical caption "Direct Connect — dedicated
private physical link, consistent bandwidth and latency, bypasses public
internet". A small crew is shown slowly installing this gangway with a
calendar icon reading "provisioning takes weeks". Above this, draw a second
connection: a shimmering, translucent energy-tunnel assembled almost
instantly between the same two points, technical caption "Site-to-Site VPN —
encrypted tunnel over the public internet, fast to establish (minutes to
hours)". Small lightning-bolt jitter marks ripple along the energy-tunnel
to show variable latency, contrasted with a smooth steady glow along the
dedicated gangway. Include a caption box comparing the two: "Direct Connect:
high consistency, high setup cost/time. VPN: quick setup, internet-dependent
latency". Add a small hybrid icon showing both running together labeled
"Direct Connect + VPN often paired for failover — common exam scenario".
""",
),
diagram(
    "17-alb-nlb-clb",
    "aws-saa-17-alb-nlb-clb.jpg",
    "ALB vs NLB vs CLB — Three Docking Traffic Controllers",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Draw three docking traffic controllers standing at three separate docking
bay entrances of the colony. The first controller holds a clipboard actively
reading cargo manifests and content labels on each incoming ship, directing
them to different bay doors marked "/images", "/api", "/videos", technical
caption "Application Load Balancer (ALB) — Layer 7, path-based and
host-based routing, understands HTTP/HTTPS". The second controller is a
lean, high-speed traffic cop waving through enormous volumes of ships
without inspecting contents, standing beside a fixed glowing beacon,
technical caption "Network Load Balancer (NLB) — Layer 4, ultra-high
throughput, supports static IP / Elastic IP per subnet". The third
controller is retired, sitting in a dusty corner chair with a faded uniform
and a "LEGACY" tag pinned on, technical caption "Classic Load Balancer (CLB)
— legacy, EC2-Classic era, avoid for new designs — exam trap when a question
implies 'older/classic' setups". Draw dotted lines from each controller to
backend target groups behind their bay doors, with a caption noting "NLB
required when a static IP is a hard requirement".
""",
),
diagram(
    "18-route53-routing-policies",
    "aws-saa-18-route53-routing-policies.jpg",
    "Route 53 — The Colony Address Dispatcher",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Draw a central dispatcher tower labeled "Route 53" perched above the colony,
with incoming ships approaching from open space and being sorted toward
different docking bays. The dispatcher has three glowing dial panels it can
switch between. First dial shows a pie-slice percentage split labeled
"70% / 30%", technical caption "Weighted Routing Policy — split traffic by
assigned weight, useful for canary releases". Second dial shows a stopwatch
comparing response times from two distant docks, with the dispatcher pointing
ships toward the faster-responding one, technical caption "Latency-based
Routing Policy — routes to the region with lowest measured latency". Third
dial shows a primary dock lit green and a backup dock lit dim gray that
flips to bright red-to-green when the primary goes dark, technical caption
"Failover Routing Policy — relies on health checks to reroute to standby".
Add a fourth small dial in the background labeled "Geolocation / Geoproximity
— route by requester location" for completeness. Include a health-check
drone icon inspecting the primary dock's hull, captioned "Route 53 Health
Check — required for failover routing to function".
""",
),
diagram(
    "19-cloudfront-edge-locations",
    "aws-saa-19-cloudfront-edge-locations.jpg",
    "CloudFront — The Relay Beacon Network",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Draw a wide starfield with the home orbital colony glowing at the center,
labeled "Origin — S3 bucket or ALB serving the original content". Scattered
across the starfield at varying distances are small glowing relay beacon
stations, each holding a cached crate stamped with a duplicate of the
colony's cargo, technical caption "Edge Locations — cache copies of content
close to distant requesters". Draw distant ships requesting cargo from the
nearest beacon instead of making the long journey home, with a highlighted
short glowing path from ship to nearby beacon labeled "Cache Hit — served
instantly from edge" versus a faint long dashed path from a different ship
all the way back to the home colony labeled "Cache Miss — beacon fetches
from Origin, then caches it". Add a small dial on one beacon labeled "TTL —
Time To Live, controls how long cached cargo stays fresh before re-fetching
from Origin". Include a caption near the whole network: "CloudFront (CDN) —
reduces latency and Origin load for globally distributed users", and a small
lock icon reading "supports HTTPS and signed URLs for private content".
""",
),
diagram(
    "20-global-accelerator",
    "aws-saa-20-global-accelerator.jpg",
    "Global Accelerator — The Optimized Flight Path Router",
    "Layer 3 — Exam-Critical",
    "Sky Blue wash (#2E86DE) - Docking Bays & Transit Tubes",
    """
Draw a distant ship in deep space attempting to reach one of several
regional orbital colonies scattered across the map. A routing beacon
labeled "AWS Global Accelerator" sits near the ship and calculates a glowing,
brightly lit optimal path that rides along a dedicated AWS backbone lane
straight to the nearest healthy regional colony, technical caption "routes
over the AWS global network backbone, not the public internet". Beside this
glowing path, draw a dimmer, jagged, meandering line representing the
old default route through open turbulent space, labeled "Public internet
path — more hops, less predictable latency". Show two anycast static
beacon-IP markers fixed in space that always point toward the same
accelerator entry regardless of which colony is healthiest, technical
caption "Two static Anycast IPs — fixed entry points, automatic failover to
healthy endpoint". Add a clear distinguishing caption box: "Not a CDN — no
content caching; optimizes TCP/UDP traffic routing and failover, unlike
CloudFront which caches static content at edge locations — common exam
trap confusing the two services".
""",
),
diagram(
    "21-s3-storage-class-ladder",
    "aws-saa-21-s3-storage-class-ladder.jpg",
    "S3 Storage Classes — The Cargo Vault Depth Ladder",
    "Layer 2 — Operational",
    "Warm Amber wash (#E67E22) - The Cargo Vault Bay.",
    """
Draw a tall vertical cargo vault shaft cut away to reveal four depths. Top
level bathed in bright light, crates stacked within arm's reach of a colonist,
technical caption "S3 Standard - millisecond access, highest storage cost,
99.99% availability". One level down, dimmer lighting, crates labeled with a
dusty stencil, technical caption "S3 Standard-IA / One Zone-IA - lower storage
cost, per-GB retrieval fee, minimum storage duration charge". Deep below,
frozen crates encased in ice require a retrieval elevator with a wall clock
showing wait times, technical caption "S3 Glacier Flexible Retrieval (mins-
hours) vs Glacier Deep Archive (12hrs) - cheapest storage, retrieval delay is
the exam trap". At the shaft's core, an auto-sorting robot arm labeled
"Intelligent-Tiering" scans crates with a motion sensor and silently moves
them up or down between levels, technical caption "monitors access patterns,
moves objects automatically, no retrieval fees, small monthly monitoring
charge". A colonist supervisor holds a decision chart asking "how often will
this be accessed?" pointing down the ladder.
""",
),
diagram(
    "22-s3-lifecycle-versioning",
    "aws-saa-22-s3-lifecycle-versioning.jpg",
    "S3 Lifecycle & Versioning — The Crate Stacking History",
    "Layer 2 — Operational",
    "Warm Amber wash (#E67E22) - The Cargo Vault Bay.",
    """
Draw a single tall crate slot in the cargo vault wall containing a leaning
stack of dated crates, each stamped with a timestamp and a small tag reading
"v1", "v2", "v3" up to the newest crate on top glowing faintly, technical
caption "S3 Versioning - each PUT to the same key creates a new version ID,
prior versions preserved". Beside the slot, a red crate marked with a skull
icon shows a "Delete Marker" placed on top instead of erasing the stack,
technical caption "DELETE on versioned bucket adds a delete marker, does not
remove old versions - exam trap". A conveyor belt extends from the base of the
stack, automatically pulling older, dimmer crates downward on a timed schedule
toward a hatch marked "Deeper Vault Levels", technical caption "Lifecycle
rule: noncurrent version transition to Standard-IA at 30 days, Glacier at 90
days, permanent expiration at 365 days". A control panel beside the slot reads
"Lifecycle Configuration (bucket-level, JSON rules)" with dials for transition
and expiration actions.
""",
),
diagram(
    "23-ebs-efs-instance-store",
    "aws-saa-23-ebs-efs-instance-store.jpg",
    "EBS vs EFS vs Instance Store — Personal Locker vs Shared Warehouse vs Temporary Crate",
    "Layer 2 — Operational",
    "Warm Amber wash (#E67E22) - The Cargo Vault Bay.",
    """
Draw three storage scenes side by side inside the colony. On the left, a
personal locker bolted directly to the wall of a single habitation module,
chained so it can only be unbolted and reattached to another module in the
same docking zone, technical caption "EBS - block storage, single AZ, attach
to one EC2 instance at a time (except Multi-Attach io1/io2)". In the middle, a
vast shared warehouse floor with multiple modules' colonists walking in
through separate doors simultaneously to access the same shelving, technical
caption "EFS - NFS file storage, multi-AZ, concurrent access from many
instances, POSIX permissions, elastic scaling". On the right, a flimsy crate
sitting loose on a module's floor that dissolves into dust the instant the
module's power shuts off, a colonist frantically labeling it "TEMPORARY -
copy data out now!", technical caption "Instance Store - ephemeral, physically
attached NVMe SSD, data lost on stop/terminate, highest IOPS". A signpost
above all three reads "Choose your storage: persistence vs sharing vs
performance".
""",
),
diagram(
    "24-cross-region-replication",
    "aws-saa-24-cross-region-replication.jpg",
    "Cross-Region Replication — The Backup Colony Mirror",
    "Layer 2 — Operational",
    "Warm Amber wash (#E67E22) - The Cargo Vault Bay.",
    """
Draw the source colony's cargo vault with a colonist placing a fresh crate
onto a receiving pad labeled "Source Bucket". The instant the crate lands, a
beam of light duplicates it and a small cargo drone launches it across a
starfield toward a distant sister colony's matching vault labeled "Destination
Bucket - Different Region", technical caption "S3 Cross-Region Replication
(CRR) - asynchronous, near-real-time copy to another region". Both vault
entrances display a glowing padlock icon stamped "Versioning: Enabled",
technical caption "CRR requires versioning enabled on BOTH source and
destination buckets - exam trap if forgotten". A mission control panel nearby
lists configuration options: "Replicate existing objects? (Batch Replication
needed)", "Replicate delete markers? (off by default)", and "IAM replication
role required". A dashed line on a star map shows the great distance between
colonies with a caption "Same-Region Replication (SRR) also available for
compliance/log aggregation use cases".
""",
),
diagram(
    "25-snowball-datasync-storagegateway",
    "aws-saa-25-snowball-datasync-storagegateway.jpg",
    "Snow Family, DataSync & Storage Gateway — Three Cargo Migration Methods",
    "Layer 2 — Operational",
    "Warm Amber wash (#E67E22) - The Cargo Vault Bay.",
    """
Draw three migration methods bringing cargo from Earth to the orbital colony.
On the left, a rugged armored shipping container physically loaded onto a
cargo rocket by dock workers, labeled "Snowball / Snowcone / Snowmobile",
technical caption "Snow Family - offline bulk data transfer, petabyte-scale,
use when network transfer would take too many days (exam trap: calculate
transfer time vs bandwidth)". In the middle, a continuous glowing conveyor
belt stretching from an Earth warehouse straight into the colony vault,
steadily carrying new and changed crates, technical caption "AWS DataSync -
online, automated, incremental sync of ongoing file changes, encrypted in
transit". On the right, a hybrid airlock module bridging an Earth-based
warehouse directly to the colony's storage systems, letting Earth workers
grab crates as if local, technical caption "Storage Gateway - File Gateway
(NFS/SMB to S3), Volume Gateway (iSCSI block, cached or stored), Tape Gateway
(virtual tape library backup)". A signpost overhead reads "Choose: one-time
physical, continuous online, or hybrid on-premises access".
""",
),
diagram(
    "26-s3-access-patterns",
    "aws-saa-26-s3-access-patterns.jpg",
    "S3 Access Patterns — Presigned Passes & Vault Policies",
    "Layer 2 — Operational",
    "Warm Amber wash (#E67E22) - The Cargo Vault Bay.",
    """
Draw the cargo vault's front desk where a vault clerk hands an outside visitor
a glowing wristband stamped with a countdown timer, technical caption
"Presigned URL - temporary, time-limited access to a specific object, signed
with the requester's credentials, no permanent IAM identity granted". The
visitor uses the wristband to open one specific crate hatch before it fades
out, "expired" flashing once the timer hits zero. On the vault's outer wall
hangs a large posted scroll titled "Vault Policy" listing who may enter and
under what conditions (technical caption "S3 Bucket Policy - resource-based
JSON policy attached to the bucket, evaluated for any principal"), while each
badge-holding colonist also carries their own folded permission slip
(technical caption "IAM Identity Policy - attached to user/role, evaluated
together with bucket policy, access requires no explicit Deny and at least
one Allow"). A guard cross-checks both documents at the gate with a caption
"Effective permission = union of policies minus any explicit Deny", and a
locked "Block Public Access" lever is shown overriding an otherwise open
policy as a highlighted exam trap.
""",
),
diagram(
    "27-rds-multiaz-vs-read-replica",
    "aws-saa-27-rds-multiaz-vs-read-replica.jpg",
    "RDS Multi-AZ vs Read Replicas — Standby Twin vs Reading Room Branches",
    "Layer 3 — Exam-Critical",
    "Deep Navy + Gold (#1A2B4A/#D4AF37) - The Central Databank",
    """
Draw the Central Databank as a primary vault in Sector A, connected by a thick
synchronous umbilical cable to a silent, dust-covered standby twin vault in
Sector B behind a curtain, technical caption "RDS Multi-AZ - synchronous
replication to standby in different Availability Zone, standby is NOT
readable". The standby twin has a dormant control panel that only lights up
and swaps in when Sector A's alarm blares and the primary explodes into
smoke, caption "automatic failover, same endpoint - for High Availability,
NOT for read scaling". Beside this, draw a separate wing with three open
"Reading Room" branch terminals, each fed by an asynchronous conveyor belt
carrying paper copies of records from the primary with a visible time-lag
gauge reading "replication lag", caption "Read Replicas - offload read
traffic, up to 5 (15 for Aurora), can be cross-region, promotable to standalone".
Add a large warning sign held by an exam-proctor robot between the two wings:
"TRAP: Multi-AZ standby ≠ read scaling! Read Replica lag ≠ automatic failover!"
with a red circle-slash over a colonist trying to run analytics queries on
the dormant standby twin.
""",
),
diagram(
    "28-aurora-architecture",
    "aws-saa-28-aurora-architecture.jpg",
    "Aurora — The Distributed Databank Core",
    "Layer 3 — Exam-Critical",
    "Deep Navy + Gold (#1A2B4A/#D4AF37) - The Central Databank",
    """
Draw the Aurora Databank Core as two distinct decoupled modules floating
near each other, connected by thin data-lines rather than fused together.
The lower module is a glowing storage ring built from six segments spread
across three separate sectors (Availability Zones), each segment
self-healing and automatically widening as more records are stuffed in,
technical caption "Aurora storage layer - auto-scales up to 128TiB across
3 AZs, 6 copies of data, self-healing". The upper module is a detachable
"Compute Brain" capsule labeled with an instance-size dial, which can be
unplugged and swapped for a bigger or smaller brain without touching the
storage ring below, caption "compute and storage scale independently".
Show a small fleet of up to 15 replica-brain capsules plugged into the same
storage ring, one glowing gold as "Writer" and the others as "Reader"
capsules, with a lightning-bolt icon showing near-instant handover when the
Writer capsule fails, caption "fast failover - typically under 30 seconds,
replicas share the same storage - no re-sync needed". A small plaque reads
"Aurora - MySQL/PostgreSQL compatible, up to 5x/3x throughput".
""",
),
diagram(
    "29-dynamodb-partition-keys",
    "aws-saa-29-dynamodb-partition-keys.jpg",
    "DynamoDB — The Distributed Filing Vault & Hot Partition Trap",
    "Layer 3 — Exam-Critical",
    "Deep Navy + Gold (#1A2B4A/#D4AF37) - The Central Databank",
    """
Draw a vast wall of identical filing drawers inside the Databank, each drawer
stamped with a hash-code label above it, technical caption "DynamoDB
partition key - hashed to determine physical partition placement". Small
robotic couriers deliver request-slips to drawers evenly across the wall
under normal conditions, caption "even key distribution = even read/write
throughput across partitions". In the center, spotlight one drawer glowing
red-hot with smoke rising, buried under a huge pile of request-slips while
neighboring drawers sit nearly empty, caption "Hot Partition - too many
requests hitting one partition key value (e.g. a single popular
'customerID'), causing throttling even with high overall provisioned
capacity". A robot supervisor holds a checklist titled "Fixes" pointing at
the glowing drawer: "add a random suffix / use composite sort key / switch
to on-demand capacity mode". A secondary caption near the wall reads
"WCU/RCU or on-demand throughput consumed per-partition, not table-wide" to
flag the common exam trap that provisioned table capacity does not prevent
a single hot partition from throttling.
""",
),
diagram(
    "30-dynamodb-gsi-lsi",
    "aws-saa-30-dynamodb-gsi-lsi.jpg",
    "DynamoDB GSI vs LSI — Alternate Filing Indexes",
    "Layer 3 — Exam-Critical",
    "Deep Navy + Gold (#1A2B4A/#D4AF37) - The Central Databank",
    """
Draw the same filing vault wall from before, now with two card-catalog
kiosks standing beside it representing alternate lookup indexes. The first
kiosk is mobile on wheels, visibly wheeled in and bolted on at any time
after the vault was built, with its own separate power meter labeled
"independent RCU/WCU", technical caption "Global Secondary Index (GSI) -
different partition key and/or sort key, created or deleted anytime, own
provisioned throughput, eventually consistent by default". The second kiosk
is fused into the vault's original foundation with visible construction
scaffolding only present at "vault creation day", drawing power from the
same shared meter as the main vault, technical caption "Local Secondary
Index (LSI) - same partition key as base table, different sort key, MUST be
created at table creation time, shares table's throughput, supports strongly
consistent reads". A signpost between them lists a size-limit warning: "LSI
max 10GB per partition key value" and an exam-trap banner overhead reads
"TRAP: Forgot to plan LSIs before table creation = must delete and rebuild
the entire table!"
""",
),
diagram(
    "31-elasticache-redis-memcached",
    "aws-saa-31-elasticache-redis-memcached.jpg",
    "ElastiCache — The Rapid-Access Front Desk",
    "Layer 3 — Exam-Critical",
    "Deep Navy + Gold (#1A2B4A/#D4AF37) - The Central Databank",
    """
Draw a bright, fast-moving Front Desk standing directly in front of the
Central Databank's main gate, intercepting a stream of colonist requests
before they ever reach the heavy vault doors behind it, technical caption
"ElastiCache - in-memory cache reduces read load and latency on the
database". Show two desk clerks side by side representing the two engine
choices. The left clerk is elaborate, wearing multiple tool-belts for
persistence snapshots, a pub/sub megaphone for messaging, sorted-list
sorting trays, and a backup vault key, caption "Redis - persistence (RDB/AOF
snapshots), replication with Multi-AZ failover, pub/sub, sorted sets,
transactions". The right clerk is stripped-down, working fast at a
multi-window counter with several arms serving requests simultaneously but
no backup key or memory of past shifts, caption "Memcached - simple
multi-threaded caching, no persistence, no replication, data lost on
restart". A small ticket dispenser near the desks reads "Lazy loading vs
Write-through caching strategies" to reinforce exam vocabulary, with a
faded colonist walking past both clerks toward the vault labeled "cache
miss".
""",
),
diagram(
    "32-redshift-analytics",
    "aws-saa-32-redshift-analytics.jpg",
    "Redshift — The Historical Archive Analysis Hall",
    "Layer 3 — Exam-Critical",
    "Deep Navy + Gold (#1A2B4A/#D4AF37) - The Central Databank",
    """
Draw a massive columned Archive Analysis Hall attached to the Databank,
with towering shelves organized by column rather than by row, and a fleet of
scanning drones sweeping down entire columns simultaneously across
petabytes of historical crates, technical caption "Redshift - columnar
storage, MPP (Massively Parallel Processing), OLAP for complex analytical
queries across huge datasets". A leader-drone labeled "Leader Node"
directs a swarm of "Compute Nodes" that each scan their own slice of
columns in parallel, caption "distributes query execution across compute
nodes". A conveyor belt labeled "Redshift Spectrum" reaches out of the hall
directly into an S3 data-lake silo outside, caption "query data directly in
S3 without loading it in". Off to the side, contrast this with a small,
brightly lit Teller Window with a single clerk rapidly stamping one
transaction slip at a time, labeled "RDS/Aurora - OLTP, row-based storage,
fast single-row inserts/updates". A signpost between the two areas reads
"TRAP: Don't use Redshift for real-time transactional apps - it's built for
analytics/BI, not OLTP", with a confused colonist trying to submit a single
$5 purchase transaction into the vast Archive Hall and being redirected to
the Teller Window instead.
""",
),
diagram(
    "33-sqs-standard-vs-fifo",
    "aws-saa-33-sqs-standard-vs-fifo.jpg",
    "SQS — Standard vs FIFO Drone Queues",
    "Layer 2 — Operational",
    "Teal wash (#16A085) - The Automated Drone Relay.",
    """
Draw two parallel drone conveyor lanes feeding the colony's cargo bay. The
left lane is wide and chaotic, labeled "SQS Standard Queue", with packages
zipping through at high speed on multiple parallel belts; two crates bear the
same barcode, and one caption reads "at-least-once delivery: possible
duplicates", another reads "best-effort ordering: nearly unlimited throughput
(near-infinite TPS)". The right lane is a narrow single-file conveyor with a
numbered turnstile gate, labeled "SQS FIFO Queue (.fifo suffix)", packages
marching through strictly in sequence 1,2,3,4 with a technical caption
"exactly-once processing + strict ordering" and a speed gauge capped low,
captioned "throughput limit: 300 msg/sec (3000 with batching)". Above the
FIFO lane, a small placard reads "MessageGroupId groups related packages;
MessageDeduplicationId blocks repeats" — a common exam trap since candidates
often forget FIFO queue names must end in .fifo. A drone supervisor stands
between both lanes holding a decision chart: "Need strict order + no dupes?
-> FIFO. Need massive scale + can tolerate reordering? -> Standard."
""",
),
diagram(
    "34-sns-fanout",
    "aws-saa-34-sns-fanout.jpg",
    "SNS Fan-Out — The Broadcast Relay Tower",
    "Layer 2 — Operational",
    "Teal wash (#16A085) - The Automated Drone Relay.",
    """
Draw a tall broadcast relay tower at the colony's center, labeled "SNS Topic",
with a rotating dish emitting one pulse of light outward in all directions.
The pulse simultaneously strikes three separate drone dispatch hangars below,
each holding its own queue of waiting drones, labeled "SQS Subscriber Queue
A", "SQS Subscriber Queue B", "SQS Subscriber Queue C". Each hangar processes
its copy of the signal at its own pace — Hangar A's drones already unloading,
Hangar B's queue backed up, Hangar C idle — with a technical caption "each
subscriber gets its own durable copy of the message; consumers decoupled and
independently scaled". A control plaque beneath the tower reads "Pub/Sub
Fan-Out Pattern: SNS -> multiple SQS queues" and a smaller sign notes "also
fans out to Lambda, email, SMS, HTTP endpoints". A dotted overlay shows a
filter policy scroll attached to Hangar C's subscription, captioned "SNS
subscription filter policy: only deliver matching message attributes" —
flagging the exam trap where candidates forget filtering happens at the
subscription, not the topic.
""",
),
diagram(
    "35-eventbridge-rules",
    "aws-saa-35-eventbridge-rules.jpg",
    "EventBridge — The Smart Signal Router",
    "Layer 2 — Operational",
    "Teal wash (#16A085) - The Automated Drone Relay.",
    """
Draw a circular routing station at a junction of colony corridors, labeled
"Amazon EventBridge - Event Bus". Incoming signal capsules arrive from
various colony systems — a solar panel sensor, an S3 cargo hold, a scheduled
chime clock — each capsule stamped with a JSON tag. A router robot at the
station's center reads each capsule's tag and holds it up against a large
corkboard of posted rule patterns, labeled "Event Pattern Rules (JSON match)".
When a capsule matches a posted rule, the robot flings it down one of several
color-coded chutes to a specific destination: a Lambda fabricator drone, a
Step Functions control panel, or a second relay tower labeled "custom event
bus". A technical caption beneath the corkboard reads "rule = event pattern
+ target(s); supports multiple targets per rule". A ticking wall clock chute
is labeled "EventBridge Scheduler / cron(...) expression" for time-based
triggers. A discarded capsule with no matching rule drops into a bin labeled
"unmatched events silently dropped — always define a catch-all or DLQ",
calling out a common exam trap.
""",
),
diagram(
    "36-step-functions-state-machine",
    "aws-saa-36-step-functions-state-machine.jpg",
    "Step Functions — The Mission Sequence Control Panel",
    "Layer 2 — Operational",
    "Teal wash (#16A085) - The Automated Drone Relay.",
    """
Draw a large wall-mounted control panel in the colony's mission control room,
labeled "AWS Step Functions - State Machine (Amazon States Language)". The
panel shows a sequence of glowing circular nodes connected by illuminated
lines: "Task State" (a drone performing a Lambda job), then a diamond-shaped
"Choice State" branching into two paths, one splitting further into a
"Parallel State" running two lanes of tasks simultaneously with a technical
caption "parallel branches execute concurrently, results aggregated". One
node has a looping arrow curling back to an earlier step, labeled "Retry /
Catch policy on task failure", with a small counter showing "attempt 2 of 3,
backoff rate 2.0". A final node glows green, labeled "Succeed State", while
a red node off to the side is labeled "Fail State". Beneath the panel, a
technical caption reads "visual workflow orchestration for multi-step,
long-running distributed processes; standard vs express workflows". A
mission control officer points at the panel comparing it to a sticky-note
list on the wall labeled "SQS/SNS alone can't do branching, retries, or
human-approval wait states" — the exam trap that Step Functions is the
answer for orchestration, not simple messaging.
""",
),
diagram(
    "37-api-gateway-lambda",
    "aws-saa-37-api-gateway-lambda.jpg",
    "API Gateway + Lambda — The Automated Reception Desk",
    "Layer 2 — Operational",
    "Teal wash (#16A085) - The Automated Drone Relay.",
    """
Draw a sleek, unmanned reception desk at the colony's public entrance,
labeled "Amazon API Gateway". Visitors (incoming HTTP requests) approach the
desk and are checked by a floating rulebook hologram against posted policies:
one page reads "Throttling: burst limit / steady-state rate limit — trap:
returns 429 Too Many Requests", another reads "Authorization: IAM, Cognito
User Pool, or Lambda authorizer token check". Approved visitors step onto a
teleport pad that instantly materializes a on-demand fabricator drone,
labeled "AWS Lambda function", which builds a custom response package and
then dissolves into vapor the moment it's done, with a technical caption
"serverless compute: pay only for invocation duration, scales to zero when
idle". A routing map behind the desk shows request paths mapped to different
drone specialists: "GET /orders -> ordersLambda", "POST /orders ->
createOrderLambda", labeled "resource + method mapping". A side booth shows
a cached response being handed out instantly without waking a drone, captioned
"API Gateway response caching reduces Lambda invocations". A signpost reads
"No servers to patch or provision — fully managed serverless API pattern".
""",
),
diagram(
    "38-multiaz-vs-multiregion",
    "aws-saa-38-multiaz-vs-multiregion.jpg",
    "Multi-AZ vs Multi-Region — Redundant Sectors vs Sister Colonies",
    "Layer 3 — Exam-Critical",
    "Alert Red wash (#C0392B) - Redundant Life-Support Sectors.",
    """
Split the illustration in two. Left side: a single orbital colony sliced into
three physically separate but nearby sectors, each with its own power core,
water recycler, and dock, connected by short reinforced tunnels. Label the
whole structure "Availability Zones within one Region". Technical caption:
"Multi-AZ deployment - RDS Multi-AZ, ALB across AZs - protects against a
single sector failure (power outage, fire) within milliseconds to seconds of
failover". Right side: a completely separate sister colony orbiting a distant
planet, connected to the first only by a slow long-range transit beam.
Label it "Region B (e.g. eu-west-1)". Technical caption: "Multi-Region
architecture - S3 Cross-Region Replication, Route 53 failover, Global
Accelerator - protects against an entire region outage, but adds latency and
complexity". Show a warning flare icon over the exam trap phrase "Multi-AZ is
NOT the same as Multi-Region" stamped in red between the two halves, with a
small note: "Multi-AZ ≠ disaster recovery for regional disasters".
""",
),
diagram(
    "39-dr-strategy-ladder",
    "aws-saa-39-dr-strategy-ladder.jpg",
    "The 4 Disaster Recovery Strategies — An Escalating Readiness Ladder",
    "Layer 3 — Exam-Critical",
    "Alert Red wash (#C0392B) - Redundant Life-Support Sectors.",
    """
Draw a tall vertical maintenance ladder bolted to the colony's outer hull,
with four rungs, cost and readiness increasing as a colonist climbs upward.
Bottom rung: a dusty storage crate labeled "Backup and Restore", technical
caption "S3 + snapshots, restore on demand - cheapest, RTO/RPO measured in
hours". Second rung: a small dim emergency capsule with one blinking light
labeled "Pilot Light", technical caption "core services (DB) always running
minimally, rest scaled up on failover - RTO in tens of minutes". Third rung:
a fully built but powered-down mini colony module labeled "Warm Standby",
technical caption "full stack running at reduced capacity, scales up on
failover - RTO in minutes". Top rung: a gleaming fully staffed sister colony
segment labeled "Multi-Site Active-Active", technical caption "full capacity
live in 2+ Regions simultaneously, traffic split by Route 53 - near-zero
RTO/RPO, highest cost". Along the ladder's side rail, a rising cost gauge and
a falling stopwatch icon reinforce the cost-vs-speed tradeoff visually.
""",
),
diagram(
    "40-asg-health-checks",
    "aws-saa-40-asg-health-checks.jpg",
    "Auto Scaling Health Checks — The Life-Support Vitals Monitor",
    "Layer 3 — Exam-Critical",
    "Alert Red wash (#C0392B) - Redundant Life-Support Sectors.",
    """
Show a curved wall of habitation modules (EC2 instances) each wired to a
central vitals monitor console labeled "Auto Scaling Group Health Check".
Every module displays a heartbeat line on a small screen; most pulse steadily
and glow green. One module's screen flatlines and turns red, captioned
"failed EC2 status check / failed ELB health check". A robotic arm
immediately detaches the flatlined module, jettisons it into a disposal
chute labeled "Terminate", and clicks a fresh replacement module into the
same slot from a stockpile rack labeled "Launch Template". Technical caption
beneath the console: "ASG health check replaces unhealthy instances
automatically to maintain desired capacity". A secondary dial on the console
shows a toggle between "EC2 status checks only" and "ELB health checks
included", with an exam-trap flag noting "must enable ELB health check type
or ASG won't see load-balancer-level failures".
""",
),
diagram(
    "41-route53-health-check-failover",
    "aws-saa-41-route53-health-check-failover.jpg",
    "Route 53 Health-Check Failover — The Automatic Backup Dock Switch",
    "Layer 3 — Exam-Critical",
    "Alert Red wash (#C0392B) - Redundant Life-Support Sectors.",
    """
Depict a traffic dispatcher robot stationed at the colony's navigation beacon
tower, labeled "Route 53". Two docks are visible: a busy Primary Dock with a
pulsing green health beacon on top, and a quiet Standby Dock with a dimmed
beacon, connected by a routing signpost labeled "Failover Routing Policy".
Incoming ships (user traffic) stream toward the Primary Dock. Suddenly the
Primary Dock's beacon flickers and goes dark, captioned "health check failed
- 3 consecutive checks over threshold". The dispatcher robot instantly swings
its signal arm to redirect the incoming ship stream to the Standby Dock,
whose beacon lights up, captioned "automatic failover - no human
intervention, no manual DNS update". A small technical readout box lists
"Health Checkers monitor endpoint every 30s (or 10s fast interval), TTL
governs how quickly resolvers pick up the change". A red exam-trap sticker
reads "Failover routing needs a health check attached to the primary record
or it will never fail over".
""",
),
diagram(
    "42-backup-restore-automation",
    "aws-saa-42-backup-restore-automation.jpg",
    "Backup & Restore Automation — The Automatic Vault Snapshot Drone",
    "Layer 3 — Exam-Critical",
    "Alert Red wash (#C0392B) - Redundant Life-Support Sectors.",
    """
Show a small maintenance drone labeled "AWS Backup" flying on a fixed patrol
route between the colony's Central Databank (RDS/DynamoDB) and Cargo Vault
(EBS volumes, EFS), following a posted schedule board that reads "Backup
Plan - daily at 03:00, retain 35 days". At each stop the drone clips on a
glowing snapshot capsule and carries it away to a fortified Archive Sector
in a separate wing of the colony, technical caption "cross-region / cross-
account copy for durability". A timeline dial on the Archive Sector wall
shows "Point-in-Time Recovery window" with a slider a colonist can drag to
any past moment, technical caption "restore to any second within the
retention window (RDS PITR)". A logbook pinned nearby lists completed runs
with green checkmarks and one red-flagged missed run captioned "monitor
backup job status - failed backups are silent unless alarmed via
EventBridge/CloudWatch". A locked side vault labeled "Vault Lock" shows a
padlock icon with caption "compliance mode - immutable backups, cannot be
deleted even by root".
""",
),
diagram(
    "43-cloudwatch-metrics-alarms",
    "aws-saa-43-cloudwatch-metrics-alarms.jpg",
    "CloudWatch — The Command Bridge Instrument Panel",
    "Layer 2 — Operational",
    "Slate Grey wash (#5D6D7E) - The Command Bridge",
    """
Draw the colony's command bridge, dominated by a wide instrument console.
Rows of analog dials labeled "CPUUtilization", "NetworkIn", "DiskReadOps",
and "StatusCheckFailed" needle-sweep in real time, technical caption "CloudWatch
Metrics - namespaced data points from EC2, RDS, Lambda, custom app metrics".
Above the dials, a bank of amber warning lights wired to tripwire switches;
one light flips to flashing red as a needle crosses a painted red threshold
line, triggering a robotic arm that flips a lever labeled "SNS Notify" and
another labeled "Auto Scaling Action", technical caption "CloudWatch Alarms -
threshold breached for N evaluation periods triggers state change: OK to ALARM
to INSUFFICIENT_DATA". Beside the dials, a curved scrolling readout screen
tiles multiple live graphs into one pane, technical caption "CloudWatch
Dashboards - customizable cross-service visualization". A crewmember labeled
"Ops Engineer" watches a smaller side panel of raw scrolling text, technical
caption "CloudWatch Logs / Logs Insights - queryable log groups and streams".
A trap callout box reads "Common trap: Alarms need actions configured -
creating an alarm alone does not stop or scale anything".
""",
),
diagram(
    "44-cloudtrail-audit-log",
    "aws-saa-44-cloudtrail-audit-log.jpg",
    "CloudTrail — The Colony Black Box Recorder",
    "Layer 2 — Operational",
    "Slate Grey wash (#5D6D7E) - The Command Bridge",
    """
Draw a heavily armored black-box flight recorder bolted to the colony's core
structural spine, wires running to every module, airlock, and console in the
station. Every crew member and every automated drone wears a badge-camera
that streams a continuous feed into the box, technical caption "CloudTrail -
records every API call made in the AWS account, including console, CLI, and
SDK actions". A printout scrolls from a slot in the recorder listing entries
like "who: Role/DeploymentBot, what: TerminateInstances, when: 03:14:07,
source IP: 10.0.4.12", technical caption "Event history - Who, What, When,
Where for governance and forensics". A second armored duplicate of the box
sits in a separate module across the colony, connected by a sealed tube,
technical caption "Multi-Region trail / Organization trail - aggregate logs
across accounts and regions into one S3 bucket". A guard tries to smash the
recorder with a wrench, and a shield deflects the blow, technical caption
"Log file integrity validation - tamper-evident digital signatures". Trap
callout: "CloudTrail logs API activity, not resource performance - that's
CloudWatch".
""",
),
diagram(
    "45-config-trusted-advisor",
    "aws-saa-45-config-trusted-advisor.jpg",
    "Config & Trusted Advisor — The Compliance Inspector & Efficiency Coach",
    "Layer 2 — Operational",
    "Slate Grey wash (#5D6D7E) - The Command Bridge",
    """
Draw two figures walking the colony's corridors on separate rounds. The first,
a stern inspector in a hard hat labeled "AWS Config", carries a rulebook and
a scanner that photographs each module's settings every time a change is
detected, comparing the snapshot against a rule labeled "restricted-ssh" and
"required-tags"; a module with an open port glows red with a tag "NON_COMPLIANT",
technical caption "Config Rules - continuous configuration compliance and
change history timeline, drift detection over time". The inspector's scanner
also feeds a timeline reel showing a module's settings at three past dates,
technical caption "Configuration history / configuration items - point-in-time
resource state". The second figure, a friendly coach in a tracksuit labeled
"Trusted Advisor", walks a separate round holding a clipboard with five colored
category tabs: Cost Optimization, Performance, Security, Fault Tolerance, and
Service Limits; the coach circles an idle, oversized generator with a note
"low utilization - downsize instance", technical caption "Trusted Advisor
checks - best-practice recommendations, not enforcement". Trap callout box:
"Config reports what IS versus a defined rule; Trusted Advisor only
recommends improvements - neither one auto-remediates without extra
automation (Config Rules + SSM Automation)".
""",
),
]

DIAGRAMS_BY_KEY = {d["key"]: d for d in DIAGRAMS}


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def get_client():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def generate_one(client, d, force=False):
    output_path = OUTPUT_DIR / d["filename"]
    if output_path.exists() and not force:
        print(f"  [SKIP - exists] {d['filename']}")
        return True

    print(f"  Generating: {d['filename']} ...")
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=d["prompt"],
            config=GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                temperature=0.3,
                image_config=ImageConfig(
                    image_size=IMAGE_SIZE,
                    aspect_ratio=ASPECT_RATIO,
                ),
            ),
        )
        for part in response.candidates[0].content.parts:
            if getattr(part, "inline_data", None) is not None:
                mime = part.inline_data.mime_type
                ext = ".png" if "png" in mime else ".jpg"
                out = output_path.with_suffix(ext)
                with open(out, "wb") as f:
                    f.write(part.inline_data.data)
                size_kb = os.path.getsize(out) / 1024
                print(f"    [OK] {out.name}  ({size_kb:.0f} KB, {mime})")
                return True
            elif getattr(part, "text", None):
                print(f"    Model text: {part.text[:200]}")
        print(f"    [WARN] No image returned for {d['filename']}")
        return False
    except Exception as e:
        print(f"    [ERROR] {d['filename']}: {e}")
        return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = get_client()

    requested_keys = sys.argv[1:]
    if requested_keys:
        targets = []
        for k in requested_keys:
            if k not in DIAGRAMS_BY_KEY:
                print(f"Unknown diagram key: {k}")
                sys.exit(1)
            targets.append(DIAGRAMS_BY_KEY[k])
        force = True
    else:
        targets = DIAGRAMS
        force = False

    print(f"Model: {MODEL_ID}  |  Resolution: {IMAGE_SIZE} {ASPECT_RATIO}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Diagrams to process: {len(targets)}\n")

    results = {}
    for d in targets:
        results[d["key"]] = generate_one(client, d, force=force)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    ok = sum(1 for v in results.values() if v)
    for k, v in results.items():
        print(f"  [{'OK' if v else 'FAILED'}] {k}")
    print(f"\n{ok}/{len(results)} succeeded.")


if __name__ == "__main__":
    main()
