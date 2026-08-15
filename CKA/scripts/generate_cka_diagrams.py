"""
Generate a full set of visual-learner diagrams for the CKA study program.

Theme: "Kubernetes Control Tower" — the cluster reimagined as a port city.
Control plane = Control Tower, Nodes = Terminals/Districts, Pods = Cargo
containers, Services = Roads/Highways, Storage = Warehouse District,
RBAC = Security Checkpoint, Troubleshooting = Diagnostic War Room.

Every diagram is designed to read at two depths at once:
  1. A 3-second glance via bold color-coded metaphor + icons (the big idea)
  2. A 30-second read via small precise technical labels (real k8s object
     names, real flags/commands) placed next to each metaphor element

Usage:
    python CKA/scripts/generate_cka_diagrams.py [key1 key2 ...]

    With no arguments, generates every diagram that doesn't already exist
    on disk (safe to re-run / resume). Pass one or more diagram keys to
    force-regenerate just those (used for the post-generation fix pass).

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
STRICT VISUAL STYLE — "Kubernetes Control Tower" theme, rendered as an
ELEGANT HAND-DRAWN TECHNICAL SKETCH (premium consulting-notebook / architect's
sketchbook aesthetic, NOT a cartoon, NOT a flat corporate infographic).
Follow exactly:

- Background: warm off-white paper texture (#FBF9F4), extremely subtle and
  barely visible — like fine cold-press illustration paper, no visible grid
- MEDIUM: fine-line pen-and-ink illustration with confident, precise, slightly
  organic linework (variable line weight, like a skilled architect or
  editorial illustrator sketched it by hand) — NOT flat vector shapes, NOT
  3D render, NOT photorealistic, NO drop shadows, NO clip-art look
- COLOR TREATMENT: restrained, elegant light watercolor-style ink washes for
  fills (soft, slightly uneven edges, translucent — like watercolor bleeding
  gently within the ink linework), never solid flat corporate fill. Overall
  palette stays muted and sophisticated — think a high-end architecture
  firm's concept sketch, not a children's book
- DOMAIN COLOR CODING (use consistently as watercolor-wash tints — this is
  the same visual language across the whole diagram series so the reader
  learns to recognize domains by color):
    Deep Navy ink wash (#1A2B4A/#D4AF37 gold ink highlights) -> Cluster Architecture / kubeadm / etcd ("Control Tower")
    Forest Green wash (#1E8A5F)   -> Workloads & Scheduling ("Cargo Yard")
    Sky Blue wash (#2E86DE)       -> Services & Networking ("Highways & Bridges")
    Warm Amber wash (#E67E22)     -> Storage ("Warehouse District")
    Royal Purple wash (#8E44AD)   -> RBAC ("Security Checkpoint")
    Alert Red wash (#C0392B)      -> Troubleshooting ("Diagnostic War Room")
    Neutral warm grey wash        -> generic infrastructure/meta
- TWO READING DEPTHS on every element (this is critical — and typography must
  stay crisp and professionally TYPESET even though the illustration is
  sketched):
    (a) A confident hand-drawn icon + short plain-English metaphor label in
        clean, elegant, perfectly legible typeset lettering (NOT sloppy
        handwriting — think refined hand-lettering used in premium editorial
        infographics), readable instantly from across a room
    (b) A small precise monospace technical caption directly beneath or
        beside it giving the REAL Kubernetes object name, field, or exact
        command (e.g. metaphor "Vault" + technical caption "etcd" /
        "etcdctl snapshot save"). This caption is always CRISP, sharp,
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
        "00-exam-universe-map",
        "cka-00-exam-universe-map.jpg",
        "The CKA Exam Universe",
        "Layer 1 — Foundational",
        "This is a MASTER MAP combining all domain colors — use each domain's color for its territory.",
        """
Draw a stylized port-city MAP from a bird's-eye/isometric-flat view, divided into 5
territories whose AREA is proportional to official exam weight:
- "Diagnostic War Room" (Alert Red, 30% of map area) — largest territory, drawn
  with flashing alarm-light icons, technical caption "Troubleshooting — 30%"
- "Control Tower District" (Navy/Gold, 25% area) — a tall tower icon,
  technical caption "Cluster Architecture, Installation & Configuration — 25%"
- "Highway & Bridge District" (Sky Blue, 20% area) — roads/bridges icon,
  technical caption "Services & Networking — 20%"
- "Cargo Yard" (Forest Green, 15% area) — shipping containers icon,
  technical caption "Workloads & Scheduling — 15%"
- "Warehouse District" (Amber, 10% area, smallest) — warehouse icon,
  technical caption "Storage — 10%"
Place a glowing golden marker labeled "YOU ARE HERE — CKAD Certified" on the
Cargo Yard and a small satellite dot on the Highway District (already familiar
territory), while the Control Tower District and Diagnostic War Room glow
with a bright "NEW GROUND" badge (these are the least-familiar-to-a-CKAD-
holder territories). Draw thin connecting roads between all territories to
show they form one connected city (one exam). Add a compass rose in a
corner labeled "Priority Compass: P0 = City Center, P3 = Outskirts".
""",
    ),
    diagram(
        "00b-three-pass-race-track",
        "cka-00b-three-pass-race-track.jpg",
        "Exam Strategy — The Three-Pass Race Track",
        "Layer 1 — Foundational",
        "Neutral/grey base with green/amber/red accents for the three passes.",
        """
Draw a circular race track (like a clock face) divided into three colored
laps, run left-to-right around the circle:
- Lap 1 (Green, ~35% of the track): "First Pass — Grab the Easy Points",
  technical caption "solve everything you recognize instantly, skip anything
  unclear"
- Lap 2 (Amber, ~40% of the track): "Second Pass — Medium Problems",
  technical caption "multi-step YAML/kubectl tasks, budget ~1.5x time"
- Lap 3 (Red, ~25% of the track): "Third Pass — Troubleshooting & Hard Mode",
  technical caption "deep diagnosis tasks, highest points-per-minute risk"
In the center of the circle, draw a stopwatch/clock face showing "120
minutes total" with three colored wedge segments matching the laps'
proportions. Add small pit-stop flag icons at intervals around the track,
each labeled "Pit Stop = Context Safety Ritual (verify context + namespace
before every task)". Add a small "checkered flag" icon near the end labeled
"Reserve final 10 min for review pass".
""",
    ),
    diagram(
        "00c-preflight-checklist",
        "cka-00c-context-safety-preflight-checklist.jpg",
        "The Context-Safety Pre-Flight Checklist",
        "Layer 1 — Foundational",
        "Neutral cockpit grey with sky-blue highlight accents.",
        """
Draw an aircraft cockpit instrument panel with exactly 5 round gauges/dials
arranged left to right, each glowing sky-blue when "checked":
1. Gauge labeled "VERIFY CONTEXT" — needle pointing at a cluster icon,
   technical caption "kubectl config current-context"
2. Gauge labeled "VERIFY NAMESPACE" — needle pointing at a folder icon,
   technical caption "kubectl config set-context --current --namespace=X"
3. Gauge labeled "INSPECT RESOURCES" — needle pointing at a magnifying
   glass, technical caption "kubectl get / describe"
4. Gauge labeled "SOLVE" — needle pointing at a wrench icon,
   technical caption "apply the fix"
5. Gauge labeled "VALIDATE" — needle pointing at a checkmark icon,
   technical caption "kubectl get/describe/logs/auth can-i to confirm"
Draw a single bold arrow flowing left to right beneath all 5 gauges labeled
"Repeat this exact sequence before EVERY single exam task, every time,
without exception."
""",
    ),
    diagram(
        "01-control-plane-cross-section",
        "cka-01-control-plane-cross-section.jpg",
        "Control Plane — Inside the Control Tower",
        "Layer 2 — Operational",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw a cutaway CROSS-SECTION of a tall navy-and-gold control tower building,
showing floors stacked top to bottom:
- ROOFTOP: a radio antenna / communications dish labeled "Front Door",
  technical caption "kube-apiserver — all cluster communication passes here"
- UPPER FLOOR: an air-traffic-control radar screen with a controller figure
  labeled "The Dispatcher", technical caption "kube-scheduler — assigns Pods
  to Nodes"
- MIDDLE FLOOR: a room full of gears/engines labeled "The Reconciliation
  Engine Room", technical caption "kube-controller-manager — drives actual
  state toward desired state"
- BASEMENT: a bank vault door labeled "The Vault", technical caption "etcd —
  the cluster's only source of truth, back it up!"
Below the tower, draw two smaller "Terminal" buildings (worker nodes)
connected to the tower by a highway, each with a small dockworker figure
labeled "kubelet — takes orders from the tower" and a small signal-flag
icon labeled "kube-proxy — routes traffic on this terminal". Draw arrows
from apiserver down to both terminals labeled "watch / report status".
""",
    ),
    diagram(
        "02-kubeadm-bootstrap-assembly-line",
        "cka-02-kubeadm-bootstrap-assembly-line.jpg",
        "kubeadm — Assembling the Control Tower",
        "Layer 2 — Operational",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw a horizontal factory ASSEMBLY LINE with 4 numbered stations, left to
right, each with a construction crane icon lowering a piece into place:
1. "Lay the Foundation" — crane places the tower base, technical caption
   "kubeadm init --pod-network-cidr=<cidr>"
2. "Print the Join Ticket" — a small ticket-printing machine spits out a
   ticket, technical caption "kubeadm token create --print-join-command"
3. "Deliver the Ticket to a New Terminal" — a courier truck carries the
   ticket to a new, unbuilt terminal building outline
4. "Bolt the Terminal to the Tower" — a crane bolts the new terminal
   building into place next to the tower, technical caption "kubeadm join
   <ip>:<port> --token <token> --discovery-token-ca-cert-hash <hash>"
At the far right, draw a completed skyline with the tower and multiple
terminals connected by roads, labeled "Cluster Ready — kubectl get nodes".
Add a small side note box: "Upgrading? Same crane, one floor at a time:
kubeadm upgrade plan -> kubeadm upgrade apply -> drain -> upgrade kubelet ->
uncordon, repeat per node."
""",
    ),
    diagram(
        "03-etcd-vault-backup-restore",
        "cka-03-etcd-vault-backup-restore.jpg",
        "etcd — Vault Deposits and Withdrawals",
        "Layer 3 — Exam-Critical",
        "Navy/Gold palette (Cluster Architecture domain), split composition.",
        """
Split the image into two clearly separated halves with a thick vertical
divider line:

LEFT HALF — "BACKUP" (calm, confident tone):
An armored truck driving UP to a bank vault, depositing a labeled snapshot
box into the vault. Truck side panel reads "etcdctl" in large letters.
Technical caption beneath: "ETCDCTL_API=3 etcdctl snapshot save
/backup/snap.db --endpoints=... --cacert=... --cert=... --key=..."
Add a small green checkmark badge "Safe to run against a LIVE cluster".

RIGHT HALF — "RESTORE" (cautionary, alarmed tone with warning stripes):
A DIFFERENT truck, side panel reading "etcdutl" in large letters (visually
distinct color trim from the etcdctl truck to emphasize it's a different
tool), withdrawing a snapshot box and carrying it to a brand NEW, empty
vault building (not the original one) with a sign "NEW --data-dir".
Technical caption beneath: "etcdutl snapshot restore /backup/snap.db
--data-dir=/var/lib/etcd-restored"
Add a bold red warning banner across this half: "etcdctl CANNOT restore —
its own restore subcommand is removed since etcd v3.5. Different tool,
different truck!"
Below both halves, a shared final step: an arrow showing "update the static
Pod manifest's etcd volume path to the new data-dir, then restart".
""",
    ),
    diagram(
        "04-static-pod-mechanism",
        "cka-04-static-pod-mechanism.jpg",
        "Static Pods — The Foreman's Bulletin Board",
        "Layer 2 — Operational",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw a factory floor scene: a foreman figure (labeled "kubelet") standing
next to a bulletin board on the wall labeled "/etc/kubernetes/manifests/".
Show the foreman's eyes with visible "watching" lines aimed at the board.
A hand is pinning a new sheet of paper (labeled "etcd.yaml" or
"kube-apiserver.yaml") onto the board. An arrow shows the foreman
immediately walking over to start up a matching container the moment the
sheet appears — technical caption "kubelet polls this directory directly
and creates/removes Pods to match, NO scheduler, NO apiserver involved in
this loop". Draw a faint, greyed-out image of the Control Tower (apiserver)
off to the side with a dotted "mirror pod reported here (read-only)" arrow,
to show the apiserver only finds out about it afterward, it doesn't control
it. Add a small callout: "This is how the control plane itself boots up
before etcd/apiserver even exist yet — chicken and egg, solved."
""",
    ),
    diagram(
        "05-certificate-trust-chain",
        "cka-05-certificate-trust-chain.jpg",
        "Certificates — The Badge Issuing Office",
        "Layer 3 — Exam-Critical",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw a grand government "Badge Issuing Office" building at the top labeled
"Root CA", with a large ornate wax-seal stamp icon, technical caption
"/etc/kubernetes/pki/ca.crt + ca.key". From it, draw branching lines down
to 4 ID-badge cards being issued to different figures:
- A tower guard labeled "kube-apiserver", technical caption "apiserver.crt"
- A terminal worker labeled "kubelet", technical caption "kubelet client
  cert"
- A person in a suit labeled "cluster-admin (you)", technical caption
  "admin.conf"
- A robot labeled "a ServiceAccount", technical caption "projected token /
  service account cert"
Each badge has a small clock icon on it showing an expiration date. Draw
one badge with its clock glowing red/cracked, labeled "EXPIRED!", with a
technical caption "kubeadm certs check-expiration" pointing at it and a
renewal arrow looping back to the office labeled "kubeadm certs renew all".
""",
    ),
    diagram(
        "06-workload-family-tree",
        "cka-06-workload-family-tree.jpg",
        "Workloads — The Cargo Family Tree",
        "Layer 1 — Foundational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a family-tree / org-chart style diagram, green palette:
TOP: "Deployment" box (a parent cargo ship icon), technical caption
"declares desired state + rollout strategy"
  -> down to "ReplicaSet" box (a fleet manager with a clipboard), technical
     caption "guarantees N identical Pods exist right now"
    -> down to a row of 3 small "Pod" boxes (identical shipping containers),
       technical caption "the actual running containers"
To the SIDE, draw 3 sibling structures at the same tree level as Deployment,
each visually distinct:
- "DaemonSet" — one container automatically placed on EVERY dock/terminal
  in the yard, technical caption "exactly one Pod per Node"
- "StatefulSet" — a row of numbered, permanently-numbered parking spots
  (container-0, container-1, container-2) that keep their names even if
  replaced, technical caption "stable network identity + storage per Pod"
- "Job / CronJob" — a delivery truck making a single delivery (Job) next to
  a truck parked at a recurring bus-stop schedule sign (CronJob), technical
  caption "run-to-completion, not long-running"
""",
    ),
    diagram(
        "07-rolling-update-conveyor",
        "cka-07-rolling-update-conveyor.jpg",
        "Rolling Updates & Rollback — The Conveyor Belt",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a horizontal conveyor belt with a row of 5 containers on it,
transitioning left (old, dull grey, labeled "v1") to right (new, bright
green, labeled "v2"), being swapped ONE AT A TIME by a robot arm — show 2
already swapped to green, 1 mid-swap in the robot arm, 2 still grey.
Technical caption beneath the belt: "kubectl set image deployment/app
app=v2 — controlled by maxSurge / maxUnavailable". Draw a progress bar
above the belt showing "3/5 updated". Add a big circular "REWIND" arrow
looping from the right side (v2 containers) back to a "restore to v1"
container labeled "kubectl rollout undo deployment/app", plus a small
"History Book" icon labeled "kubectl rollout history / --revision=N".
""",
    ),
    diagram(
        "08-probes-health-checkpoints",
        "cka-08-probes-health-checkpoints.jpg",
        "Probes — Health Checkpoints on the Line",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a single cargo container moving left to right through 3 sequential
checkpoint gates, each gate a distinct color with a traffic light:
1. GATE 1 (grey) "Startup Gate" — a guard asking "Are you even awake yet?",
   technical caption "startupProbe — blocks the other two probes until it
   passes"
2. GATE 2 (blue) "Liveness Gate" — a heart-rate monitor scanning the
   container, technical caption "livenessProbe — fails it? kubelet KILLS
   and RESTARTS the container"
3. GATE 3 (green) "Readiness Gate" — a gate onto the highway with a
   "Service traffic this way" sign, technical caption "readinessProbe —
   fails it? Pod stays alive but is pulled OUT of Service Endpoints"
Show one container failing Gate 3 with its traffic light red, sitting in a
siding off the highway (still running, just not receiving traffic), with a
label "common exam trap: confusing liveness failure (restart) with
readiness failure (no traffic)".
""",
    ),
    diagram(
        "09-scheduling-matchmaking",
        "cka-09-scheduling-matchmaking.jpg",
        "Scheduling — The Matchmaker & the Bouncers",
        "Layer 3 — Exam-Critical",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a nightclub-entrance scene:
- A "Matchmaker" figure at a podium labeled "Scheduler", holding a
  clipboard, technical caption "kube-scheduler"
- A queue of "Pod" guests, some holding VIP invitation cards labeled
  "nodeAffinity / podAffinity — I want to stand near my friends", one
  holding a card labeled "podAntiAffinity — keep me AWAY from my rivals"
- Several "Node" doors, each with a "Bouncer" figure standing in front
  wearing a sash labeled "Taint: NoSchedule" — bouncers only let in guests
  holding a matching "Toleration" wristband, shown as a glowing wristband
  icon on one lucky guest
- A simple VIP-list clipboard at one door labeled "nodeSelector — name must
  literally be on this list, no exceptions"
- A "Priority" guest with a gold crown icon cutting the line, technical
  caption "PriorityClass — higher priority Pods can preempt lower ones"
Show the Matchmaker successfully pairing one guest to one open door with a
dotted line, labeled "Pod successfully scheduled".
""",
    ),
    diagram(
        "10-services-highway-system",
        "cka-10-services-highway-system.jpg",
        "Services — The Layered Highway System",
        "Layer 1 — Foundational",
        "Sky Blue palette (Services & Networking domain).",
        """
Draw a layered road-network cross-section, from innermost to outermost:
- INNERMOST: quiet neighborhood streets connecting rows of houses (Pods),
  labeled "ClusterIP — internal-only traffic", technical caption "type:
  ClusterIP (default)"
- NEXT LAYER: an on-ramp from the neighborhood onto a numbered highway exit,
  labeled "NodePort — a fixed exit number (30000-32767) on every Node",
  technical caption "type: NodePort"
- OUTER LAYER: a toll bridge crossing out of the city entirely to an
  external cloud icon, labeled "LoadBalancer — a cloud-provisioned bridge",
  technical caption "type: LoadBalancer"
- A separate SMART TRAFFIC ROUTER sign structure sitting above the highway,
  reading paths/hostnames and directing cars to different neighborhoods,
  labeled "Ingress — host/path-based routing to multiple Services",
  technical caption "IngressClass + rules"
At the very bottom, small mailbox icons labeled "EndpointSlices — the real
list of Pod IPs a Service currently routes to" sit outside each house.
""",
    ),
    diagram(
        "11-dns-resolution-post-office",
        "cka-11-dns-resolution-post-office.jpg",
        "DNS — The CoreDNS Post Office",
        "Layer 2 — Operational",
        "Sky Blue palette (Services & Networking domain).",
        """
Draw a Pod character dropping a letter into a mailbox labeled with the
address "my-svc.my-ns.svc.cluster.local". An arrow carries the letter to a
post-office building labeled "CoreDNS", technical caption "kube-system
coredns Pods, exposed via the kube-dns Service". Inside the post office,
show a sorting shelf resolving the address down to a ClusterIP, which is
mailed back to the original Pod as a reply postcard.
Below, draw a small "Undeliverable Mail" bin with 3 branching problem tags
coming out of it, each pointing to a broken-mail icon:
- "Wrong namespace suffix" (letter addressed to the wrong .svc.NAMESPACE)
- "Post office is closed" (technical caption "coredns Pods CrashLooping —
  check kubectl -n kube-system get pods")
- "No forwarding address on file" (technical caption "kube-dns Service
  missing or misconfigured")
Add a small diagnostic tool icon: "kubectl exec <pod> -- nslookup
kubernetes.default".
""",
    ),
    diagram(
        "12-networkpolicy-security-gates",
        "cka-12-networkpolicy-security-gates.jpg",
        "NetworkPolicy — The Security Gates",
        "Layer 3 — Exam-Critical",
        "Sky Blue palette (Services & Networking domain).",
        """
Draw a walled district (namespace) with a solid, unbroken wall around it
labeled "Default state once ANY NetworkPolicy selects a Pod: DENY ALL",
technical caption "podSelector: {} + no rules = default-deny".
In the wall, draw exactly 2 open, guarded gates:
- An INGRESS gate on the left, with a guard checking incoming visitors'
  ID badges against a list, labeled "ingress rule — only visitors wearing
  the 'role: frontend' badge (label selector) may enter", technical caption
  "spec.ingress[].from[].podSelector"
- An EGRESS gate on the right, with a guard checking outgoing traffic
  against an allowed destination list, labeled "egress rule — residents may
  only exit toward the DNS post office and the payments district",
  technical caption "spec.egress[].to[] + ports"
Show one visitor without a badge being turned away at the ingress gate with
a red X, and one being waved through with a matching badge and a green
check.
""",
    ),
    diagram(
        "13-gateway-api-vs-ingress-bridges",
        "cka-13-gateway-api-vs-ingress-bridges.jpg",
        "Ingress vs Gateway API — Two Generations of Bridges",
        "Layer 2 — Operational",
        "Sky Blue palette (Services & Networking domain), split composition.",
        """
Split the image into two halves showing two eras of the same city entrance:

LEFT HALF — "The Old Bridge" (slightly weathered, simpler look):
A single stone bridge with ONE toll-keeper booth controlling everything,
labeled "Ingress", technical caption "a single Ingress resource + rules[]
+ an IngressClass/controller (e.g. nginx)". Caption: "One object couples
routing rules AND infrastructure config together."

RIGHT HALF — "The New Modular Bridge Complex" (sleek, modern, well-lit):
A multi-lane bridge complex with a separate control building labeled
"Gateway" (technical caption "infrastructure — provisioned by platform
team, defines listeners/ports") feeding into several clearly marked lane
signs labeled "HTTPRoute" (technical caption "routing rules — owned by app
teams, host/path/header matching, traffic splitting"). Show 3 separate
HTTPRoute lanes merging into the one Gateway structure, illustrating the
separation of concerns.
Add a small banner: "Exam-relevant docs live at gateway-api.sigs.k8s.io —
allowed during the CKA."
""",
    ),
    diagram(
        "14-storage-warehouse-requisition",
        "cka-14-storage-warehouse-requisition.jpg",
        "Storage — The Warehouse Requisition Office",
        "Layer 2 — Operational",
        "Amber palette (Storage domain).",
        """
Draw a warehouse district process, left to right:
1. A Pod character filling out a requisition form at a desk, labeled
   "PersistentVolumeClaim", technical caption "requests size + accessMode +
   storageClassName"
2. The form is handed to a clerk at a window labeled "StorageClass —
   Provisioning Office", technical caption "provisioner + parameters"
3. Two possible outcomes branch out from the clerk:
   (a) UPPER path — the clerk walks to a shelf of PRE-BUILT labeled crates
       in a "Static Provisioning" shelf, technical caption "a matching
       PersistentVolume already exists and gets Bound"
   (b) LOWER path — the clerk presses a button and a construction robot
       builds a BRAND NEW warehouse unit on demand, labeled "Dynamic
       Provisioning", technical caption "provisioner auto-creates a new PV"
4. The finished warehouse unit has two door types shown as icons: a single
   private door labeled "ReadWriteOnce — one tenant" and a wide shared
   loading dock labeled "ReadWriteMany — many tenants"
5. At the very end, a signpost at the exit reads "When the PVC is deleted:
   Retain (keep the crate) vs Delete (demolish it)", technical caption
   "persistentVolumeReclaimPolicy"
""",
    ),
    diagram(
        "15-rbac-security-badges",
        "cka-15-rbac-security-badges.jpg",
        "RBAC — The Security Checkpoint HQ",
        "Layer 3 — Exam-Critical",
        "Royal Purple palette (RBAC domain).",
        """
Draw a security-checkpoint headquarters, left to right flow:
1. Badge-holder figures on the left: a person labeled "User", a robot
   labeled "ServiceAccount", technical caption "system:serviceaccount:ns:name"
2. A badge-printing machine in the middle-left labeled "Role /
   ClusterRole — permission templates", with TWO output trays: one marked
   "Role — this district (namespace) only" and one marked "ClusterRole —
   valid city-wide", technical caption "rules: [apiGroups, resources, verbs]"
3. A lanyard-clipping station labeled "RoleBinding / ClusterRoleBinding —
   attaches a printed badge to a specific person/robot", technical caption
   "subjects: [] + roleRef"
4. On the right, a guard at a door holding a handheld scanner labeled
   "kubectl auth can-i", scanning a badge and showing a green check or red
   X, technical caption "kubectl auth can-i delete pods --as=system:
   serviceaccount:ns:name"
Show one badge-holder being denied entry with a red X and the caption
"Forbidden — check: does the RoleBinding actually reference this Role AND
this subject, in the right namespace?"
""",
    ),
    diagram(
        "16-troubleshooting-decision-tree",
        "cka-16-troubleshooting-decision-tree.jpg",
        "The Master Troubleshooting Decision Tree",
        "Layer 3 — Exam-Critical",
        "Alert Red palette (Troubleshooting domain), subway-map style.",
        """
Draw a subway-map style diagram starting from a central hub station labeled
"SOMETHING IS WRONG", branching into 4 colored subway lines, each with 3-4
stations (stops):

RED LINE — "Pod Line": stations "Pending" (technical caption "kubectl
describe pod — check Events for scheduling failures"), "ImagePullBackOff"
(caption "check image name/tag/registry auth"), "CrashLoopBackOff" (caption
"kubectl logs --previous"), ending at a green "Fix Confirmed" station.

ORANGE LINE — "Node Line": stations "NotReady" (caption "kubectl describe
node — check Conditions"), "kubelet down" (caption "systemctl status
kubelet / journalctl -u kubelet"), "CNI missing" (caption "check
/etc/cni/net.d and crictl pods"), ending at "Fix Confirmed".

BLUE LINE — "Network Line": stations "Service unreachable" (caption "check
selector matches Pod labels + Endpoints"), "DNS failing" (caption "check
CoreDNS Pods + kube-dns Service"), ending at "Fix Confirmed".

PURPLE/NAVY LINE — "Control Plane Line": stations "Static Pod not starting"
(caption "check kubelet logs + manifest YAML validity"), "Certificate
expired" (caption "kubeadm certs check-expiration"), "etcd unhealthy"
(caption "etcdctl endpoint health"), ending at "Fix Confirmed".

All 4 lines visually converge back at a final interchange station labeled
"VALIDATE — kubectl get/describe/logs before declaring victory".
""",
    ),
    diagram(
        "17-pod-lifecycle-traffic-lights",
        "cka-17-pod-lifecycle-traffic-lights.jpg",
        "Pod Lifecycle — The Diagnostic Dashboard",
        "Layer 2 — Operational",
        "Alert Red palette (Troubleshooting domain).",
        """
Draw a wall-mounted diagnostic control panel with 4 large round traffic-
light indicators in a row, each with a magnifying glass hovering over it
showing the diagnostic command used:
1. GREY light "Pending" — magnifying glass shows "kubectl describe pod —
   read the Events section for the scheduling reason"
2. FLASHING RED light "CrashLoopBackOff" — magnifying glass shows "kubectl
   logs <pod> --previous — see why the LAST attempt died"
3. AMBER light "ImagePullBackOff / ErrImagePull" — magnifying glass shows
   "kubectl describe pod — check image name, tag, and imagePullSecrets"
4. STEADY GREEN light "Running" (but with a small yellow sub-indicator)
   "Running but not Ready" — magnifying glass shows "kubectl get pod -o
   wide + check readinessProbe config"
Below the panel, a single master switch labeled "kubectl get events
--sort-by=.lastTimestamp — always check this first".
""",
    ),
    diagram(
        "18-node-notready-triage",
        "cka-18-node-notready-triage.jpg",
        "Node NotReady — The Mechanic's Garage",
        "Layer 3 — Exam-Critical",
        "Alert Red palette (Troubleshooting domain).",
        """
Draw a mechanic's garage scene: a broken-down vehicle labeled "Node
(NotReady)" up on a lift, with a mechanic figure holding a toolbox labeled
"systemctl / journalctl / crictl". Around the vehicle, draw 4 dashboard
warning lights the mechanic is checking, each with a technical caption:
1. Engine warning light — "kubelet service stopped", technical caption
   "systemctl status kubelet -> systemctl restart kubelet"
2. Oil-pressure light — "Disk pressure / memory pressure", technical
   caption "kubectl describe node — check Conditions: DiskPressure,
   MemoryPressure"
3. Tire-pressure light — "CNI plugin not installed/misconfigured",
   technical caption "check /etc/cni/net.d/, crictl ps, journalctl -u
   kubelet | grep cni"
4. Battery light — "kubelet certificate expired", technical caption
   "journalctl -u kubelet | grep -i certificate"
Show the mechanic plugging in a diagnostic scanner labeled "journalctl -u
kubelet -f" directly into the vehicle's dashboard, with a readout screen
showing scrolling log lines.
""",
    ),

    # -----------------------------------------------------------------
    # Round 2 — smaller/granular modules that deserved their own diagram
    # -----------------------------------------------------------------

    diagram(
        "19-kubeconfig-anatomy",
        "cka-19-kubeconfig-anatomy.jpg",
        "kubeconfig — The Travel Passport",
        "Layer 1 — Foundational",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw an open passport booklet. On the LEFT page, a row of stamped visa
entries labeled "clusters:" — each stamp showing a different city skyline
icon (a different cluster) with technical caption "cluster.server (the API
endpoint URL) + certificate-authority-data". On the RIGHT page, a row of ID
photos labeled "users:" — each with a small key icon, technical caption
"user.client-certificate-data + client-key-data (or a token)". Below both
pages, draw a boarding pass labeled "contexts:" that STAPLES one cluster
stamp to one user photo PLUS a namespace field, technical caption
"context = cluster + user + namespace". At the bottom, a passport-control
officer stamping "CURRENT" on exactly one boarding pass, technical caption
"kubectl config current-context / kubectl config use-context <name> /
kubectl config set-context --current --namespace=<ns>". Add a small side
note: "--kubeconfig flag or $KUBECONFIG env var picks WHICH passport book
you're even holding — merge multiple files by separating paths with ':'".
""",
    ),
    diagram(
        "20-kubeadm-upgrade-node-maintenance",
        "cka-20-kubeadm-upgrade-node-maintenance.jpg",
        "kubeadm Upgrade — One Floor at a Time",
        "Layer 3 — Exam-Critical",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw the same Control Tower skyline as before, but now under RENOVATION,
floor by floor, left to right in 5 numbered steps:
1. "Plan" — an inspector with a clipboard checking the tower, technical
   caption "kubeadm upgrade plan"
2. "Upgrade the Tower First" — a crane replacing ONLY the Control Tower's
   floors (control-plane node), technical caption "kubeadm upgrade apply
   v1.x.y (control-plane node only)"
3. "Cordon & Drain One Terminal" — a worker terminal building roped off
   with tape and its cargo containers being carried onto neighboring
   terminals, technical caption "kubectl cordon <node> && kubectl drain
   <node> --ignore-daemonsets"
4. "Upgrade That Terminal" — a small crane swaps the terminal's kubelet
   floor, technical caption "apt-get upgrade kubelet kubeadm && kubeadm
   upgrade node && systemctl restart kubelet"
5. "Uncordon & Repeat" — the tape comes off, cargo flows back in, an arrow
   loops back to step 3 for the NEXT terminal, technical caption "kubectl
   uncordon <node> — repeat steps 3-5 per remaining node, ONE AT A TIME"
Add a warning banner across the bottom: "Version skew rule: kubelet must
never be newer than kube-apiserver, and no more than 2 minor versions
older."
""",
    ),
    diagram(
        "21-admission-controllers-gatekeepers",
        "cka-21-admission-controllers-gatekeepers.jpg",
        "Admission Control — The Gatekeepers Beyond the Front Door",
        "Layer 3 — Exam-Critical",
        "Navy/Gold palette (Cluster Architecture domain).",
        """
Draw the Control Tower's Front Door (apiserver) from diagram 01, but now
show a SECOND checkpoint corridor just inside the door, after RBAC has
already waved someone through, with two guard posts in sequence:
1. "Mutating Admission" guard post — a guard with a rubber stamp that
   QUIETLY EDITS the incoming request as it passes (e.g. adding a default
   label), technical caption "MutatingAdmissionWebhook — can modify the
   object"
2. "Validating Admission" guard post — a stricter guard with a checklist
   who can only ACCEPT or REJECT, never edit, technical caption
   "ValidatingAdmissionWebhook — accept or reject only"
Beyond both posts, show a large sign with 3 tiers like a nightclub dress
code, labeled "Pod Security Admission levels": "Privileged" (no dress
code, anything goes), "Baseline" (no obviously dangerous outfits — blocks
known privilege escalations), "Restricted" (strict hardened dress code —
enforces Pod security best practices). Show this dress-code sign attached
to a specific namespace door, technical caption "namespace label:
pod-security.kubernetes.io/enforce=restricted".
""",
    ),
    diagram(
        "22-init-containers-sidecars",
        "cka-22-init-containers-sidecars.jpg",
        "Init Containers & Sidecars — The Prep Crew and the Ride-Along",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a cargo container (Pod) being prepared for departure, left to right:
LEFT — "The Prep Crew" (initContainers): a line of workers each finishing
one task in STRICT SEQUENCE before the next starts (worker 1 finishes
"wait for database" and steps aside, THEN worker 2 starts "fetch config
file"), technical caption "spec.initContainers — run to completion, in
order, before any app container starts". Show a locked gate that only
opens once the LAST prep worker gives a thumbs-up.
RIGHT — "The Ride-Along" (native sidecar): the main app container driving
off, with a smaller container PERMANENTLY WELDED to its side going along
for the whole trip, technical caption "initContainers[].restartPolicy:
Always — starts before the main container but keeps running alongside it
for the Pod's entire life (e.g. a log shipper or service mesh proxy)".
Add a small comparison note: "Old-style sidecar = just another entry in
containers[], starts at the same time as everything else, no ordering
guarantee."
""",
    ),
    diagram(
        "23-configmaps-secrets-consumption",
        "cka-23-configmaps-secrets-consumption.jpg",
        "ConfigMaps & Secrets — The Supply Cabinet",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a supply-room cabinet labeled "ConfigMap / Secret" (Secret drawer
shown with a small padlock icon, base64 stamp). Two delivery methods branch
out to a waiting Pod:
1. UPPER path — "Slip a memo under the door": a single sheet of paper
   sliding under the Pod's door, technical caption "envFrom / env.valueFrom
   .configMapKeyRef — injected as environment variables, FROZEN at
   container start, a Secret update will NOT change a running container's
   env vars"
2. LOWER path — "Wheel in a filing drawer": a whole filing cabinet drawer
   rolled into the Pod's room and left there, technical caption "volumes +
   volumeMounts — mounted as files, kubelet syncs updates automatically
   (subject to sync period), the app must watch the file for changes
   itself"
Show a small red warning flag on the memo path: "common exam trap:
expecting an updated Secret to auto-refresh injected env vars — it won't,
only mounted volumes update live". Add a small padlock detail note on the
Secret drawer: "stored base64-encoded, NOT encrypted, in etcd by default —
that's obfuscation, not security".
""",
    ),
    diagram(
        "24-resource-requests-limits-qos",
        "cka-24-resource-requests-limits-qos.jpg",
        "Requests & Limits — The Cargo Weight Manifest",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a cargo container on a weighing scale with two marked lines on a
gauge: a lower line labeled "requests — guaranteed floor space, what the
Scheduler reserves on a Node" and a higher red line labeled "limits — hard
ceiling, exceeding CPU gets throttled, exceeding memory gets the container
OOMKilled". Technical caption: "resources.requests / resources.limits per
container".
Below, draw 3 tiers of shipping-priority stickers on 3 example containers,
like boarding-priority tags, labeled "QoS Classes":
1. Gold sticker "Guaranteed" — requests == limits on every resource,
   technical caption "evicted LAST under node pressure"
2. Silver sticker "Burstable" — requests < limits (at least one resource
   set), technical caption "evicted SECOND"
3. Bronze/no sticker "BestEffort" — no requests or limits set at all,
   technical caption "evicted FIRST under node memory/disk pressure"
Show a sinking-ship style "Node Under Pressure" scene where the BestEffort
containers get thrown overboard first, then Burstable, Guaranteed staying
safely aboard longest.
""",
    ),
    diagram(
        "25-jobs-completion-modes",
        "cka-25-jobs-completion-modes.jpg",
        "Jobs & CronJobs — The Delivery Fleet Dispatch Board",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a fleet-dispatch office with a large dispatch board showing 3 knobs:
- "completions" knob set to a number (e.g. 5) — technical caption "total
  successful deliveries needed before the Job is Complete"
- "parallelism" knob set to a smaller number (e.g. 2) — technical caption
  "how many delivery trucks run AT ONCE"
- "backoffLimit" knob — technical caption "how many failed delivery
  attempts are tolerated before giving up"
Show a small fleet of delivery trucks driving out in waves of 2 at a time
(parallelism), with a tally board ticking up toward 5 completions, and one
crashed truck icon with a retry counter next to backoffLimit.
Beside the dispatch office, draw a wall calendar labeled "CronJob" with a
recurring alarm-clock icon circling specific calendar squares, technical
caption "schedule: cron syntax (min hour day month weekday), e.g. "*/15 * *
* *" — spawns a fresh Job dispatch each time the alarm rings".
""",
    ),
    diagram(
        "26-hpa-workload-autoscaling",
        "cka-26-hpa-workload-autoscaling.jpg",
        "HPA — The Elastic Cargo Yard",
        "Layer 2 — Operational",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a cargo yard that visibly EXPANDS and CONTRACTS like an accordion or
bellows. On the left, a large pressure gauge labeled "Metrics Watcher"
(technical caption "HorizontalPodAutoscaler — watches CPU/memory or a
custom metric") with a needle swinging between "low load" and "high load".
When the needle swings into the red "high load" zone, show new cargo
containers (Pods) popping up along the yard like an accordion expanding,
up to a fence-post marked "maxReplicas: 10". When the needle swings back to
green "low load", show containers being removed, down to a fence-post
marked "minReplicas: 2". Technical caption at the bottom: "kubectl autoscale
deployment app --cpu-percent=50 --min=2 --max=10, or a full
HorizontalPodAutoscaler manifest targeting a Deployment/StatefulSet".
Add a small clock icon labeled "stabilization window — waits briefly before
scaling down again to avoid flapping".
""",
    ),
    diagram(
        "27-priority-preemption",
        "cka-27-priority-preemption.jpg",
        "Priority & Preemption — The VIP Eviction",
        "Layer 3 — Exam-Critical",
        "Forest Green palette (Workloads & Scheduling domain).",
        """
Draw a fully-booked venue (a Node completely full of Pods). A new VIP
guest arrives holding a gold "high-priority" ticket, technical caption
"PriorityClass value: 1000000 (higher number = higher priority)". A
bouncer looks at the room, picks the guest with the LOWEST-priority
ticket already inside (a guest with a dull grey ticket, technical caption
"PriorityClass value: 0 or none"), and physically escorts them OUT the
door (technical caption "preempted — evicted to free room for the
higher-priority Pod, then reschedule itself elsewhere"), making space for
the VIP to enter. Add a side note: "preemption only happens if the node is
genuinely full — it does not evict Pods just because a higher-priority one
exists elsewhere. A PriorityClass with preemptionPolicy: Never asks for
priority in the queue WITHOUT evicting anyone."
""",
    ),
    diagram(
        "28-kube-proxy-service-internals",
        "cka-28-kube-proxy-service-internals.jpg",
        "kube-proxy — Behind the Highway Toll Booths",
        "Layer 3 — Exam-Critical",
        "Sky Blue palette (Services & Networking domain).",
        """
Draw a cutaway view UNDER one of the highway toll booths from the Services
diagram, revealing a mechanic (kube-proxy) programming a routing switchboard.
The switchboard has ONE fixed dial on top labeled with the Service's stable
ClusterIP (e.g. "10.96.5.20") and MULTIPLE wires underneath leading to
rotating real Pod IPs (e.g. "10.244.1.5", "10.244.2.10", "10.244.1.15"),
which shuffle/rotate to illustrate load-balancing. Technical caption:
"kube-proxy watches Services + EndpointSlices and programs iptables (or
IPVS) rules on every Node so ANY Node can receive traffic for the
Service's ClusterIP and forward it to a live Pod backend". Show two small
mode-selector switches on the mechanic's toolbox labeled "iptables mode
(default, random selection)" and "IPVS mode (more scalable, supports more
LB algorithms)". Add a diagnostic tool label: "iptables-save | grep
<service-name> — inspect the actual rules if a Service seems unreachable".
""",
    ),
    diagram(
        "29-cni-pod-cidr-troubleshooting",
        "cka-29-cni-pod-cidr-troubleshooting.jpg",
        "CNI — The Road Construction Crew",
        "Layer 3 — Exam-Critical",
        "Sky Blue palette (Services & Networking domain).",
        """
Draw a construction crew paving roads between two districts (Nodes) BEFORE
any cargo containers (Pods) can be placed there — an empty Node with a
"NO ROADS YET" sign and Pods stuck in a holding pen labeled "Pending /
ContainerCreating". Technical caption: "CNI plugin (Calico, Flannel,
Cilium...) must be installed for Pods to get IP addresses at all — check
/etc/cni/net.d/ and crictl pods". Beside it, draw two districts whose road
grids DON'T CONNECT at the border — a torn/mismatched road seam — labeled
"Pod-CIDR mismatch between kubeadm init --pod-network-cidr and the CNI
plugin's own config file", with cars unable to cross between districts.
Add a diagnostic checklist signpost: "1. kubectl get pods -n kube-system
(CNI Pods running?) 2. crictl ps 3. journalctl -u kubelet | grep cni 4.
check the CNI manifest's podCIDR matches kubeadm's --pod-network-cidr".
""",
    ),
    diagram(
        "30-pvc-pending-troubleshooting",
        "cka-30-pvc-pending-troubleshooting.jpg",
        "Storage — The Stuck Requisition",
        "Layer 3 — Exam-Critical",
        "Amber palette (Storage domain).",
        """
Draw the Warehouse Requisition Office from before, but now the requisition
form (PVC) is stuck at the clerk's window with a big "PENDING" stamp on
it and a confused clerk. Draw 4 branching diagnostic thought-bubbles coming
off the clerk's head, each a common cause:
1. "No matching StorageClass exists" — an empty nameplate slot, technical
   caption "kubectl get storageclass — does the requested storageClassName
   actually exist?"
2. "Provisioner isn't running" — a broken-down construction robot,
   technical caption "check the provisioner Pod/controller logs in
   kube-system or the CSI driver namespace"
3. "No PV matches for static provisioning" — an empty warehouse shelf,
   technical caption "kubectl get pv — check capacity, accessModes, and
   storageClassName all match the PVC exactly"
4. "Capacity too large / accessMode unsupported" — a requisition form
   asking for a warehouse bigger than any exist, technical caption
   "requested size or ReadWriteMany not supported by this storage backend"
End with a checkmark path: "kubectl describe pvc <name> — the Events
section names the exact reason, always check this first".
""",
    ),
    diagram(
        "31-rbac-troubleshooting-impersonation",
        "cka-31-rbac-troubleshooting-impersonation.jpg",
        "RBAC Troubleshooting — The Undercover Inspector",
        "Layer 3 — Exam-Critical",
        "Royal Purple palette (RBAC domain).",
        """
Draw an inspector at the Security Checkpoint HQ holding a special
"Undercover Badge" that lets them TEMPORARILY see through someone else's
credentials, technical caption "kubectl auth can-i <verb> <resource> --as
system:serviceaccount:<ns>:<name> (or --as=<user> --as-group=<group>) —
test permissions without actually being that identity". Show the inspector
getting a red "Forbidden" stamp and following a decision checklist posted
on the wall:
1. "Does a RoleBinding/ClusterRoleBinding even exist for this
   subject?" — kubectl get rolebinding,clusterrolebinding -A -o wide
2. "Does its roleRef point at the Role/ClusterRole you THINK it does?" —
   check roleRef.name and roleRef.kind match exactly
3. "Does that Role actually grant this verb+resource+apiGroup?" — kubectl
   describe role/clusterrole <name>
4. "Right namespace?" — a RoleBinding only grants access within its OWN
   namespace, even if it references a ClusterRole
Show a green checkmark once all 4 boxes are ticked, badge now glowing
"Access Granted".
""",
    ),
    diagram(
        "32-crashloopbackoff-deep-dive",
        "cka-32-crashloopbackoff-deep-dive.jpg",
        "Anatomy of a CrashLoopBackOff",
        "Layer 3 — Exam-Critical",
        "Alert Red palette (Troubleshooting domain).",
        """
Draw a container repeatedly popping up and immediately collapsing, with a
growing backoff-timer clock next to each attempt: attempt 1 (10s wait),
attempt 2 (20s wait), attempt 3 (40s wait), showing the doubling delay,
technical caption "exponential backoff, capped at 5 minutes". Beside the
looping container, a magnifying glass inspects an "Exit Code" tag on the
fallen container, branching to 3 possible readouts:
- Exit code "0" — a shrugging figure, technical caption "clean exit — the
  main process finished/quit, but a Pod's main container isn't supposed to
  exit at all"
- Exit code "1" (or other non-zero) — an error sheet, technical caption
  "application crashed — kubectl logs <pod> --previous is the very first
  command to run"
- "OOMKilled (137)" — a red memory gauge pegged at max, technical caption
  "container exceeded its memory limit — check resources.limits.memory and
  actual usage with kubectl top pod"
Add the master command banner: "kubectl describe pod <pod> — read BOTH the
Last State/Exit Code block AND the Events section before touching
anything."
""",
    ),
    diagram(
        "33-dns-troubleshooting-flow",
        "cka-33-dns-troubleshooting-flow.jpg",
        "DNS Troubleshooting — The Post Office Inspection",
        "Layer 3 — Exam-Critical",
        "Alert Red palette (Troubleshooting domain).",
        """
Draw a step-by-step inspection checklist as a series of 5 numbered
inspection stamps on a clipboard, an inspector working through them in
order:
1. "Test from inside a Pod" — technical caption "kubectl exec <pod> --
   nslookup kubernetes.default (or the target Service name)"
2. "Are CoreDNS Pods even running?" — technical caption "kubectl -n
   kube-system get pods -l k8s-app=kube-dns"
3. "Check CoreDNS logs for errors" — technical caption "kubectl -n
   kube-system logs -l k8s-app=kube-dns"
4. "Is the kube-dns Service healthy?" — technical caption "kubectl -n
   kube-system get svc kube-dns -o wide — check it has Endpoints"
5. "Check the Pod's own resolv.conf" — technical caption "kubectl exec
   <pod> -- cat /etc/resolv.conf — nameserver should point at the
   kube-dns ClusterIP, search domains should include the right
   .svc.cluster.local suffix"
Each stamp is either a green check or, on one of them, a red X with an
arrow branching off to the specific fix. End with: "Also check: does a
NetworkPolicy in this namespace block egress to UDP/TCP port 53?"
""",
    ),
    diagram(
        "34-etcd-health-troubleshooting",
        "cka-34-etcd-health-troubleshooting.jpg",
        "etcd Health — Inspecting the Vault",
        "Layer 3 — Exam-Critical",
        "Alert Red palette (Troubleshooting domain) with Navy/Gold vault imagery.",
        """
Draw a vault inspector standing in front of the etcd vault (reuse the vault
imagery from the earlier etcd diagram) with a diagnostic clipboard showing
3 checks:
1. "Is the vault door even responding?" — technical caption "etcdctl
   endpoint health --endpoints=... --cacert=... --cert=... --key=..."
2. "Who are all the vault keepers?" — technical caption "etcdctl member
   list -w table — confirms all control-plane etcd members are present and
   not flagged unhealthy"
3. "Any alarms tripped?" — technical caption "etcdctl alarm list — e.g. a
   NOSPACE alarm means the vault's disk quota is full and etcd goes
   read-only until you etcdctl alarm disarm after freeing space/compacting"
Show one vault member's light flashing red/offline with an arrow to
"check that control-plane node's static Pod: kubectl -n kube-system logs
etcd-<node> or crictl logs if the apiserver itself is unreachable".
""",
    ),
    diagram(
        "35-control-plane-down-triage",
        "cka-35-control-plane-down-triage.jpg",
        "The Tower Has Gone Dark — Control Plane Down Triage",
        "Layer 3 — Exam-Critical",
        "Alert Red palette (Troubleshooting domain) with Navy/Gold tower imagery.",
        """
Draw the Control Tower from earlier, now dark with its lights off and
"kubectl" commands failing (a speech bubble showing "connection refused"
error near a frustrated admin figure). A technician climbs the tower
checking a sequence of 4 floors, each a diagnostic step:
1. Ground floor — "Is the container runtime even alive?" technical caption
   "crictl ps -a / systemctl status containerd"
2. "Is the static Pod manifest valid?" — technical caption "check
   /etc/kubernetes/manifests/kube-apiserver.yaml for YAML syntax errors —
   kubelet silently fails to start a malformed static Pod"
3. "Check kubelet's own logs, since apiserver Pods are invisible to
   kubectl right now" — technical caption "journalctl -u kubelet -f, or
   crictl logs <container-id> directly, bypassing kubectl entirely"
4. "Certificates still valid?" — technical caption "openssl x509 -in
   /etc/kubernetes/pki/apiserver.crt -noout -dates, or kubeadm certs
   check-expiration"
Add a bold callout: "When kubectl itself is broken, crictl + journalctl +
reading YAML directly become your ONLY tools — this is the moment static
Pod knowledge from diagram 04 matters most."
""",
    ),
    diagram(
        "36-priority-matrix-heatmap",
        "cka-36-priority-matrix-heatmap.jpg",
        "The Priority Heat Map",
        "Layer 1 — Foundational",
        "Full multi-domain palette — this is a META overview diagram, not a single domain.",
        """
Draw a large grid/heat-map, rows = the 6 territories from the Exam Universe
map (Diagnostic War Room, Control Tower, Highways & Bridges, Cargo Yard,
Warehouse District, Security Checkpoint), columns = "P0", "P1", "P2", "P3".
Fill each cell with a small stack of colored ticket stubs (in that row's
domain color) representing how many named skills fall into that priority
tier — make the Diagnostic War Room and Control Tower rows visibly
STACKED HIGH in the P0 column (most of their skills are P0), while
Warehouse District and the CRD/Argo-CD-style items stack mostly in P2/P3.
Add a small heat-intensity glow (brighter = hotter = more exam-critical)
overlaid on the P0 column specifically. Caption at the bottom: "Study time
should roughly mirror this heat map — glowing cells first."
""",
    ),
    diagram(
        "37-study-roadmap-7-14-21",
        "cka-37-study-roadmap-7-14-21.jpg",
        "Three Roads to Exam Day",
        "Layer 1 — Foundational",
        "Neutral grey base with green/amber/red road accents for the three plans.",
        """
Draw 3 parallel roads running left to right across a landscape, all
converging at a single checkered-flag finish line labeled "EXAM DAY":
- TOP road (short, green, labeled "7-Day Sprint") — few, densely-packed
  milestone markers, technical caption "for someone who can study 4-6
  focused hours/day"
- MIDDLE road (medium length, amber, labeled "14-Day Balanced") — evenly
  spaced milestone markers alternating "Refresh", "Drill", "Mock", "Review"
  icons, technical caption "for someone studying alongside full-time work"
- BOTTOM road (longest, blue-grey, labeled "21-Day Thorough") — more
  gradual milestone markers with extra "buffer/rest" markers built in,
  technical caption "for maximum margin and multiple full mock exams"
Show a small golden star marker on the 14-Day road with a flag reading
"Recommended for a CKAD-certified engineer working full-time" (do not put
this star on the other two roads). Each road has small mile-markers shaped
like the domain-color icons (tower, cargo box, road sign, etc.) showing
roughly where each domain gets studied along the way.
""",
    ),
    diagram(
        "38-final-48-hour-countdown",
        "cka-38-final-48-hour-countdown.jpg",
        "The Final Countdown",
        "Layer 1 — Foundational",
        "Neutral grey/navy base, mission-control countdown aesthetic.",
        """
Draw a rocket-launch mission countdown clock/timeline running left to
right with 4 marked countdown stations, each with a small icon of the
activity appropriate to that stage:
1. "T-minus 48 hours" — a stack of books/mock-exam icon, technical caption
   "last full mock exam + review every miss, then stop learning brand-new
   topics"
2. "T-minus 24 hours" — a lighter review icon (flashcards/cheat sheet),
   technical caption "cheat-sheet review + command drills only, no new
   material, protect your sleep"
3. "T-minus 30 minutes" — a checklist/webcam icon, technical caption
   "environment + proctoring checks: single monitor, ID ready, quiet room,
   stable connection"
4. "LAUNCH — Exam Start" — a rocket lifting off, technical caption "run the
   Context-Safety Pre-Flight Checklist before task 1"
Show a descending anxiety-meter gauge next to the timeline that gets calmer
(from red to green) as the countdown proceeds, captioned "confidence should
RISE as new-material-learning STOPS".
""",
    ),
    diagram(
        "39-go-no-go-dashboard",
        "cka-39-go-no-go-dashboard.jpg",
        "The Launch Control Panel",
        "Layer 1 — Foundational",
        "Neutral mission-control grey base with green/red status-light accents.",
        """
Draw a mission-control panel with a row of 6 large status-light switches,
each labeled with a readiness criterion and currently shown either GREEN
(lit, ready) or RED (unlit, not ready) — show a mix so the panel reads as
"almost ready, one switch still red":
1. "P0 Question Bank Coverage" — technical caption "≥90% of P0-tagged
   questions solved correctly"
2. "Mock Exam 2 Score" — technical caption "≥66% on the real-difficulty
   mock, ideally higher for margin"
3. "etcd Backup/Restore Timing" — technical caption "completed reliably
   under time target"
4. "kubeadm Task Timing" — technical caption "bootstrap/upgrade tasks
   completed under time target"
5. "Troubleshooting Diagnosis Speed" — technical caption "root cause found
   within target time on fresh scenarios"
6. "RBAC / Storage / Networking Benchmarks" — technical caption "core
   task-pattern completion times met"
A large master lever at the bottom reads "BOOK THE EXAM", currently locked
with a padlock because not all 6 lights are green, captioned "Do not pull
this lever until every single light above is green."
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
