"""
Generate visual-learner diagrams for the CKS study program.

Theme: "Kubernetes Security Fortress" — the cluster reimagined as a medieval
fortress city under siege. Control plane = Inner Keep, Nodes = Outer Walls,
Pods = Inhabitants, NetworkPolicy = City Gates, RBAC = Royal Guard,
Secrets = Treasury Vault, Admission Control = Checkpoint Gate,
Runtime Security = Watchtower Sentries, Supply Chain = Trade Route.

Every diagram is designed to read at two depths at once:
  1. A 3-second glance via bold color-coded metaphor + icons (the big idea)
  2. A 30-second read via small precise technical labels (real k8s object
     names, real flags/commands) placed next to each metaphor element

Usage:
    python CKS/generate_cks_diagrams.py [key1 key2 ...]

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
IMAGE_SIZE = "4K"
ASPECT_RATIO = "16:9"

STYLE_GUIDE = """
STRICT VISUAL STYLE — "Kubernetes Security Fortress" theme, rendered as an
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
- SECURITY DOMAIN COLOR CODING (use consistently as watercolor-wash tints):
    Deep Navy ink wash (#1A2B4A / #D4AF37 gold highlights) -> Cluster Hardening, API Server, etcd ("Inner Keep")
    Crimson Red wash (#C0392B)      -> Attacks, Vulnerabilities, Insecure Configs ("Siege Forces")
    Forest Green wash (#1E8A5F)     -> Defenses, Secure Configs, Remediations ("Fortress Walls")
    Sky Blue wash (#2E86DE)         -> NetworkPolicy, Services, Network Controls ("City Gates & Bridges")
    Warm Amber wash (#E67E22)       -> Supply Chain, Admission, Image Security ("Trade Route Checkpoint")
    Royal Purple wash (#8E44AD)     -> RBAC, ServiceAccounts, Access Control ("Royal Guard")
    Teal wash (#16A085)             -> Runtime Security, Falco, Audit ("Watchtower Sentries")
    Neutral warm grey wash          -> generic infrastructure / meta
- TWO READING DEPTHS on every element (critical — typography must stay
  crisp and professionally TYPESET even though the illustration is sketched):
    (a) A confident hand-drawn icon + short plain-English metaphor label in
        clean, elegant, perfectly legible typeset lettering (NOT sloppy
        handwriting — think refined hand-lettering used in premium editorial
        infographics), readable instantly from across a room
    (b) A small precise monospace technical caption directly beneath or
        beside it giving the REAL Kubernetes object name, field, or exact
        command. This caption is always CRISP, sharp, perfectly legible
        dark-ink monospace typography — never sketched or stylized, it must
        be as readable as a printed textbook
- Title: elegant serif hand-lettered display heading at the top center, with
  a single fine hand-drawn underline stroke in that diagram's domain color
- A small "Complexity Layer" tag in the top-left corner, drawn like a
  notebook sticky-tab
- A compact, elegant legend box in the bottom-right corner (drawn like a
  small index card) mapping each color wash used in THIS diagram to its
  domain name
- SECURITY VISUAL LANGUAGE (use these sketch-style icons consistently):
    Shield icon = defense mechanism / security control
    Skull icon = attack vector / vulnerability
    Lock icon = encryption / secrets
    Eye icon = monitoring / audit / Falco
    Gate icon = admission control / NetworkPolicy
    Guard figure = RBAC / access control
    Watchtower = runtime monitoring
    Scroll = audit policy / configuration
    Chain links = supply chain
- MAXIMUM PROFESSIONAL POLISH: composition is clean and uncluttered with
  generous whitespace, confident linework, gallery-quality finish — this
  should look like a single beautiful page from a very expensive technical
  security book, not a rough doodle
- Crisp, perfectly legible text at every size, in sharp focus everywhere
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


DIAGRAMS = [
    diagram(
        "00-exam-domain-map",
        "cks-00-exam-domain-map.jpg",
        "The CKS Exam Fortress — Domain Map & Weights",
        "Layer 1 — Foundational",
        "MASTER MAP combining all domain colors — use each domain's color for its territory.",
        """
Draw a stylized FORTRESS CITY MAP from a bird's-eye view, divided into 6
territories whose AREA is proportional to official CKS exam weight:

- "Microservice Defenses" (Forest Green, 20% area) — a walled district with
  shield icons, technical caption "Minimize Microservice Vulnerabilities — 20%"
  Sub-labels: SecurityContext, Pod Security, Secrets, Sandboxing

- "Trade Route Checkpoint" (Amber, 20% area) — a guarded trade road with
  inspection stations, technical caption "Supply Chain Security — 20%"
  Sub-labels: Image Scanning, Admission Control, Static Analysis, Trusted Registries

- "Watchtower Quarter" (Teal, 20% area) — tall watchtowers with sentries,
  technical caption "Monitoring, Logging & Runtime Security — 20%"
  Sub-labels: Falco, Audit Logs, Behavioral Analytics, Immutable Containers

- "Inner Keep" (Navy/Gold, 15% area) — the central fortified tower,
  technical caption "Cluster Setup — 15%"
  Sub-labels: CIS Benchmarks, Network Security, Ingress TLS

- "Royal Guard Barracks" (Purple, 15% area) — guard quarters with
  checkpoint gates, technical caption "Cluster Hardening — 15%"
  Sub-labels: RBAC, Service Accounts, API Server, Upgrades

- "Outer Wall Garrison" (Grey, 10% area, smallest) — the outer defensive wall,
  technical caption "System Hardening — 10%"
  Sub-labels: OS Footprint, IAM, Kernel Hardening

Place a golden callout banner reading "Top 3 territories = 60% of exam — FOCUS HERE"
pointing at the three 20% territories. Draw thin roads connecting all territories.
Add a compass rose labeled "Priority: P0 = Inner Keep, P3 = Outskirts".
At the bottom, add a bar showing: "2 hours | 15-20 tasks | 67% to pass | K8s v1.35"
""",
    ),
    diagram(
        "01-attack-surface",
        "cks-01-attack-surface-map.jpg",
        "The Siege — Kubernetes Attack Surface Map",
        "Layer 3 — Exam-Critical",
        "Crimson Red wash for attacks, Forest Green for defenses, Navy for cluster components.",
        """
Draw the Kubernetes cluster as a MEDIEVAL FORTRESS UNDER SIEGE, viewed from
an elevated angle. Show concentric defensive rings with attackers trying to
breach from outside:

OUTER RING — "Beyond the Walls" (red-tinted, attackers):
- Attacker figures with red banners approaching from the left
- "Untrusted Images" — a poisoned supply cart, caption "Malicious container image"
- "Compromised Registry" — a merchant with fake goods, caption "Supply chain attack"
- "Stolen Credentials" — a spy with stolen keys, caption "Leaked kubeconfig"

MIDDLE RING — "The Walls & Gates" (navy, cluster perimeter):
- "API Server" drawn as the MAIN GATE (largest element), caption "Primary target —
  all requests pass here"
- "kubelet" drawn as WALL GUARD POSTS on each node tower, caption "Node-level API"
- "etcd" drawn as the TREASURY VAULT inside the keep, caption "All secrets stored here"
- Each with a small red flag showing its #1 risk

INNER RING — "Inside the Walls" (blue, workload level):
- Pods drawn as inhabitants/workers inside buildings
- ServiceAccounts drawn as ID badges/passes, caption "Token theft risk"
- Secrets drawn as treasure chests, caption "Accessible if RBAC too broad"
- hostPath drawn as a tunnel under the wall, caption "Container escape path"

CENTER — "Crown Jewels" (gold, glowing):
- Cluster Admin access (crown icon)
- etcd data (vault icon)
- All secrets (treasure icon)

Draw a numbered ATTACK SEQUENCE PATH: 1→ Compromised Pod → 2→ SA Token Theft →
3→ API Access → 4→ Cluster Takeover, shown as a red dotted line snaking inward.
""",
    ),
    diagram(
        "02-api-request-flow",
        "cks-02-api-request-security-flow.jpg",
        "The Gauntlet — API Request Security Flow",
        "Layer 2 — Operational",
        "Navy for gates, Purple for RBAC, Amber for admission, Green for success, Red for rejection.",
        """
Draw the API request lifecycle as a CASTLE GATE GAUNTLET — a series of
fortified checkpoints that every request must pass through, left to right:

ENTRANCE — "The Petitioner" (grey):
- A messenger figure carrying a scroll, caption "kubectl apply -f pod.yaml"
- Or a worker figure with an ID badge, caption "Pod ServiceAccount request"

GATE 1 — "Identity Check" (Navy archway with guard):
- A guard checking papers, caption "AUTHENTICATION"
- Small labels: "x509 Certs | Bearer Token | OIDC"
- RED trapdoor below: "401 Unauthorized → REJECTED" with figure falling

GATE 2 — "Authority Check" (Purple archway with royal guard):
- A royal guard checking a permission scroll, caption "AUTHORIZATION (RBAC)"
- Label: "Can subject X perform verb Y on resource Z?"
- RED trapdoor: "403 Forbidden → REJECTED"

GATE 3 — "The Shapers" (light purple archway):
- Scribes modifying the scroll, caption "MUTATING ADMISSION"
- Label: "Add defaults, inject sidecars, modify request"

GATE 4 — "The Inspectors" (Amber archway, LARGEST gate):
- Multiple inspectors examining the scroll closely, caption "VALIDATING ADMISSION"
- Inspector badges labeled:
  - "Pod Security Admission (enforce: restricted)"
  - "ValidatingAdmissionPolicy (CEL)"
  - "ImagePolicyWebhook"
  - "Custom Webhooks"
- RED trapdoor: "Denied by policy → REJECTED"

DESTINATION — "The Vault" (Green, with lock icon):
- The scroll being placed in a locked vault, caption "Persisted in etcd"
- Sub-caption: "Encrypted at rest (if EncryptionConfiguration set)"

Below the gauntlet, draw a thin banner: "WHERE CKS SECURITY CONTROLS APPLY"
with colored markers at each gate matching their domain color.
""",
    ),
    diagram(
        "03-pod-security-layers",
        "cks-03-pod-security-defense-in-depth.jpg",
        "Defense in Depth — Pod Security Layers",
        "Layer 3 — Exam-Critical",
        "Use all defense colors — green layers getting stronger toward center.",
        """
Draw a FORTIFIED TOWER CROSS-SECTION showing concentric defensive layers
protecting a central treasure (the container workload), viewed as a cutaway:

CENTER (white) — "The Inhabitant":
- A worker figure inside a room, caption "Container Application"
- Small and protected by all surrounding layers

LAYER 1 (innermost green wall) — "Personal Armor":
- Armor icons on the inhabitant, caption "Container securityContext"
- Inscribed stones on the wall reading:
  "runAsNonRoot: true"
  "readOnlyRootFilesystem: true"
  "allowPrivilegeEscalation: false"
  "capabilities: drop ALL"

LAYER 2 (blue wall) — "Room Fortification":
- Reinforced room walls, caption "Pod securityContext"
- Inscribed: "runAsUser: 1000" / "fsGroup: 2000" / "seccompProfile: RuntimeDefault"

LAYER 3 (teal wall) — "Magical Wards":
- Glowing runes on walls, caption "Linux Security Modules"
- Left rune: "seccomp — syscall filter" (RuntimeDefault / Localhost)
- Right rune: "AppArmor — file/network restrictions" (enforce / complain)

LAYER 4 (purple gate) — "District Decree":
- A posted decree/edict on the wall, caption "Pod Security Admission"
- Three wax seal badges: "privileged" (red) → "baseline" (amber) → "restricted" (green)

LAYER 5 (sky blue outer wall) — "City Gates":
- Guarded gates with traffic control, caption "NetworkPolicy"
- Left gate: "Ingress rules" / Right gate: "Egress rules"

LAYER 6 (outermost grey wall) — "Kingdom Law":
- Royal banners on the outer wall, caption "Cluster Controls"
- Banners: "RBAC" / "Admission Controllers" / "Audit Logging"

Draw small red attack arrows being STOPPED at each layer.
Add callout: "Each layer catches what the others miss!"

Include a side panel showing "Pod-level vs Container-level fields" as two
columns on a posted notice.
""",
    ),
    diagram(
        "04-rbac-architecture",
        "cks-04-rbac-complete-architecture.jpg",
        "The Royal Guard — RBAC Architecture",
        "Layer 3 — Exam-Critical",
        "Royal Purple palette with red accents for escalation dangers.",
        """
Draw a ROYAL GUARD HEADQUARTERS with three sections, top to bottom:

TOP — "WHO Seeks Entry" (Subjects):
Three figures standing at the entrance:
- A person with a name badge, caption "Users" (alice@example.com)
- A group of people, caption "Groups" (developers, sre-team)
- A mechanical automaton/golem, caption "ServiceAccounts"
  (default:deployer, kube-system:monitoring)

MIDDLE — "The Commission" (Bindings as bridge/connector):
Two types of official decree scrolls:
- A scroll with a namespace seal, caption "RoleBinding — namespace-scoped"
  Shows: Subject → Role Reference → Namespace
- A larger scroll with a royal seal, caption "ClusterRoleBinding — cluster-wide"
  Shows: Subject → ClusterRole Reference → All Namespaces

BOTTOM — "The Authority Granted" (Permissions):
Two types of authority documents:
- A local charter, caption "Role — namespace-scoped"
  Fields: apiGroups, resources, verbs, resourceNames
  Example YAML in monospace
- A royal charter, caption "ClusterRole — cluster-wide"
  Same fields, broader scope

VERB BADGES (draw as colored medal/badge icons):
- Green medals: get, list, watch (read operations)
- Amber medals: create, update, patch (write operations)
- Red medals: delete (destructive)
- Bright crimson skull medals: bind, escalate, impersonate (DANGEROUS)

RIGHT SIDEBAR — "Escalation Dangers" (Red warning scroll):
5 attack paths drawn as red arrows:
1. "bind verb → self-grant roles"
2. "create pods → exec into them"
3. "get secrets → steal tokens"
4. "impersonate → act as admin"
5. "escalate → grant higher permissions"

BOTTOM BANNER — Key Commands in monospace:
kubectl auth can-i --list
kubectl auth can-i create pods --as=system:serviceaccount:ns:sa
""",
    ),
    diagram(
        "05-networkpolicy-guide",
        "cks-05-networkpolicy-visual-guide.jpg",
        "City Gates — NetworkPolicy Visual Reference",
        "Layer 3 — Exam-Critical",
        "Sky Blue palette for network controls, Red for blocked traffic, Green for allowed.",
        """
Draw a FOUR-PANEL diagram on the sketch page, like four scenes in an
architect's storyboard:

PANEL 1 (top-left) — "Open City vs Walled City":
LEFT: An open town with free-flowing traffic between buildings (pods),
green arrows everywhere, caption "Without NetworkPolicy: ALL traffic allowed"
RIGHT: Same town now walled, with gates and guards, red X marks on blocked
paths, caption "With deny-all: traffic blocked unless explicitly allowed"

PANEL 2 (top-right) — "Anatomy of a Gate Order":
A NetworkPolicy YAML shown as a POSTED DECREE on a city wall, with
color-coded annotations pointing to each section:
- podSelector → Blue arrow: "Which buildings (pods) this gate order covers"
- policyTypes → Purple arrow: "Ingress, Egress, or both"
- ingress.from → Green arrow: "Who may ENTER"
- egress.to → Amber arrow: "Where inhabitants may TRAVEL"
- ports → Teal arrow: "Which doors (ports) are open"

PANEL 3 (bottom-left) — "AND vs OR — The Critical Gate Logic":
Two side-by-side scenes with Venn diagram overlays:
LEFT "AND Logic" (single entry with both selectors):
- Two overlapping circles, only the INTERSECTION highlighted
- Caption: "Must match BOTH namespace AND pod selector"
- Show the YAML indentation that creates AND

RIGHT "OR Logic" (separate entries):
- Two circles, BOTH fully highlighted (union)
- Caption: "Match EITHER namespace OR pod selector"
- Show the YAML indentation that creates OR

Large warning banner: "MOST COMMON CKS TRAP — indentation changes meaning!"

PANEL 4 (bottom-right) — "Four Essential Gate Patterns":
Four mini-scenes in a 2x2 grid:
1. "Default Deny All" (red shield, locked gate) with minimal YAML
2. "Allow from Namespace" (green arrow from labeled district) with YAML
3. "Allow DNS Egress" (arrow to kube-dns tower, port 53) with YAML
4. "Allow Pod-to-Pod" (specific green arrow between buildings) with YAML

Bottom warning ribbon: "ALWAYS allow DNS egress (port 53) when applying deny-all egress!"
""",
    ),
    diagram(
        "06-supply-chain-pipeline",
        "cks-06-supply-chain-security-pipeline.jpg",
        "The Trade Route — Supply Chain Security",
        "Layer 2 — Operational",
        "Warm Amber palette for supply chain, with red danger markers and green security controls.",
        """
Draw a LEFT-TO-RIGHT TRADE ROUTE through the fortress landscape, showing
goods (container images) traveling from outside the kingdom to inside:

STAGE 1 — "The Artisan's Workshop" (grey, far left):
- A craftsperson at a workbench, caption "Developer"
- Small red flag: "Malicious code injection"
- Green shield: "Code review, branch protection"

STAGE 2 — "The Warehouse" (grey):
- A storage building with scrolls, caption "Source Repository"
- Red flag: "Compromised dependencies"
- Green shield: "Signed commits, access control"

STAGE 3 — "The Forge" (amber):
- A forge/smithy building, caption "CI/CD Build Pipeline"
- Red flag: "Build tampering"
- Green shield: "SAST, minimal base images (distroless/alpine)"

STAGE 4 — "Quality Inspection" (amber, with magnifying glass):
- An inspector examining goods, caption "Image Scanning (Trivy)"
- Monospace: "trivy image --severity CRITICAL,HIGH <image>"
- Red flag: "Known CVEs"
- Green shield: "Scan before ship"

STAGE 5 — "The Trading Post" (amber):
- A guarded market, caption "Container Registry"
- Red flag: "Unauthorized images"
- Green shield: "Trusted registries only, pull secrets"

STAGE 6 — "THE GREAT GATE" (amber, LARGEST element — fortified checkpoint):
- A massive gate with multiple inspectors, caption "ADMISSION CONTROL"
- Inspector figures labeled:
  - "ImagePolicyWebhook"
  - "ValidatingAdmissionWebhook"
  - "ValidatingAdmissionPolicy (CEL)"
  - "Pod Security Admission"
- Red flag: "Policy bypass"
- This gate is drawn LARGER than other stages — it's the primary defense

STAGE 7 — "Inside the Fortress" (green, far right):
- Safe buildings inside walls, caption "Kubernetes Runtime"
- Green shields: "Falco monitoring, Audit logging, seccomp, AppArmor"

Bottom banner: "Supply Chain Security = 20% of CKS exam"
""",
    ),
    diagram(
        "07-encryption-at-rest",
        "cks-07-encryption-at-rest-flow.jpg",
        "The Treasury — Encryption at Rest",
        "Layer 2 — Operational",
        "Navy/Gold for cluster components, Green for encrypted, Red for unencrypted.",
        """
Draw the encryption flow as a TREASURY VAULT SYSTEM:

LEFT — "The Message Arrives":
- A messenger delivering a scroll, caption "kubectl create secret"
- Arrow labeled "API Request"

CENTER — "The API Server Vault Master" (navy, large):
- A vault master at a desk, caption "API Server"
- On the desk: a key ring and a codebook
- Monospace caption: "--encryption-provider-config=/etc/kubernetes/enc/enc.yaml"

Below desk — "The Cipher Selection" (key decision point):
Draw a STACK of cipher books, top = primary (used for encryption):
- TOP (green, active): "aescbc" or "secretbox" — glowing, caption "ENCRYPTS new data"
- BOTTOM (grey): "identity" — dusty, caption "Fallback: no encryption (reads old data)"

Important callout scroll: "ORDER MATTERS! First provider encrypts.
All providers tried for decryption."

COMPARISON TABLE drawn as a posted chart:
| Provider  | Speed  | Security | Recommended |
| aescbc    | Medium | Good     | Yes         |
| aesgcm    | Fast   | Strong   | Rotate keys!|
| secretbox | Fast   | Strong   | Yes (newest)|
| identity  | N/A    | NONE     | NO!         |
| kms v2    | Varies | Best     | Enterprise  |

RIGHT — "The Vault" (navy with gold lock):
- A locked vault door, caption "etcd"
- Inside vault, show encrypted text: "k8s:enc:aescbc:v1:key1:..." (green)
- Crossed-out plaintext: "base64-decoded plaintext" (red X)

BOTTOM — "The Cipher Codebook" (EncryptionConfiguration YAML):
Show the YAML in elegant monospace on a posted scroll:
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources: [secrets]
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-key>
  - identity: {}

WARNING banner (red seal): "identity as FIRST provider = NO ENCRYPTION!"
TIP scroll (green): "Re-encrypt existing: kubectl get secrets -A -o json | kubectl replace -f -"
""",
    ),
    diagram(
        "08-audit-logging",
        "cks-08-audit-logging-architecture.jpg",
        "The Watchtower Scribes — Audit Logging",
        "Layer 2 — Operational",
        "Teal palette for monitoring/audit, Navy for API server.",
        """
Draw an AUDIT LOGGING system as a WATCHTOWER SCRIBE'S OFFICE:

TOP SECTION — "The Audit Flow":
- A messenger arrives at the watchtower (API request)
- The Head Scribe (Audit Policy Engine) consults a rulebook
- Decision diamond: "Does this event match a recording rule?"
  → YES: Scribe writes in the appropriate detail level
  → NO: "Try next rule" or "Default: silence (None)"
- The completed record goes to: "The Archive" (audit log file)
  or "The Courier" (webhook to external system)

MIDDLE — "Four Levels of Detail" (ascending staircase/tower levels):
Draw as four ascending tower floors, each recording MORE detail:

Floor 1 (ground, grey): "None" — Empty desk, caption "Don't record this event"
Floor 2 (blue): "Metadata" — Scribe noting basics, caption "Who, what, when, response code"
Floor 3 (amber): "Request" — Scribe copying the full petition, caption "Metadata + request body"
Floor 4 (top, green): "RequestResponse" — Scribe copying everything,
caption "Metadata + request + response body"

Side note: "Higher floors = more detail but more parchment (storage)"

BOTTOM-LEFT — "The Rulebook" (Audit Policy YAML):
Show on a posted scroll in monospace:
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse  ← GREEN (most verbose)
  resources:
  - group: ""
    resources: ["secrets"]
- level: Metadata          ← BLUE
  resources:
  - group: ""
    resources: ["pods"]
- level: None              ← GREY
  users: ["system:kube-proxy"]

Arrow label: "Rules evaluated TOP-DOWN — first match wins!"

BOTTOM-RIGHT — "Tower Configuration" (API Server setup):
A posted notice showing required flags and volume mounts:

Flags:
--audit-policy-file=/etc/kubernetes/audit/policy.yaml
--audit-log-path=/var/log/kubernetes/audit.log

WARNING seal: "MUST add BOTH volume AND volumeMount — missing either crashes API server!"
""",
    ),
    diagram(
        "09-runtime-security-falco",
        "cks-09-runtime-security-and-falco.jpg",
        "The Watchtower — Runtime Security & Falco",
        "Layer 3 — Exam-Critical",
        "Teal palette for monitoring, with layered green defenses.",
        """
SECTION 1 (left half) — "The Fortress Defense Stack":
Draw a WATCHTOWER with layered defenses, bottom to top:

Foundation (grey): "Linux Kernel" — bedrock, caption "syscalls"
Wall 1 (green): "seccomp" — a fine mesh filter, caption "Syscall filter"
Wall 2 (blue): "AppArmor/SELinux" — magical wards, caption "Mandatory Access Control"
Wall 3 (teal): "Container Runtime (containerd)" — inner walls, caption "Process isolation"
Wall 4 (green): "Kubernetes SecurityContext" — armor, caption "Pod security settings"
Top (teal, with eye): "Falco — The Sentry" — a vigilant guard with a spyglass,
caption "Behavioral detection & alerting"

Show a red attacker figure trying to climb the tower, being stopped at
different layers. Each layer has a small shield showing what it blocks.

SECTION 2 (right half) — "Falco Rule Anatomy":
Draw a GUARD'S INSTRUCTION CARD with color-coded sections:

- rule: Detect Shell in Container     ← WHITE (rule name)
  desc: Alert on shell spawned        ← GREY (description)
  condition: >                        ← CYAN (detection logic)
    spawned_process and
    container and
    proc.name in (bash, sh, zsh)
  output: >                           ← GREEN (what to log)
    Shell spawned (user=%user.name
    container=%container.name
    command=%proc.cmdline)
  priority: WARNING                   ← AMBER (severity)

SECTION 3 (bottom strip) — "Six Common Alerts":
Draw 6 small guard-report cards in a row:
1. "Shell in Container" — terminal icon, proc.name in (bash, sh)
2. "Sensitive File Read" — scroll icon, fd.name in (/etc/shadow)
3. "Privilege Escalation" — up-arrow icon, evt.type=setuid
4. "Unexpected Network" — bridge icon, outbound from container
5. "Binary Dropped" — package icon, file written to /bin
6. "Package Manager" — crate icon, proc.name in (apt, yum, apk)

Bottom note: "Falco docs are ALLOWED during CKS exam — bookmark rules reference!"
""",
    ),
    diagram(
        "10-incident-response",
        "cks-10-incident-response-playbook.jpg",
        "Battle Stations — Incident Response Playbook",
        "Layer 2 — Operational",
        "Teal for detection, Red for threat, Blue for isolation, Green for remediation.",
        """
Draw a TOP-TO-BOTTOM BATTLE PLAN showing the incident response protocol
for a compromised workload, as a medieval battle commander's strategy scroll:

STEP 1 — "ALARM" (red bell icon):
- A watchtower sentry ringing a bell, caption "DETECT"
- "Falco alert / suspicious process / unusual network activity"
- Decision crossroads: "Real threat?" → NO: "Log and dismiss" → YES: continue

STEP 2 — "IDENTIFY THE THREAT" (amber magnifying glass):
- A scout examining the scene, caption "IDENTIFY"
- Monospace commands on a field report:
  kubectl get pods -o wide
  kubectl describe pod <suspicious>
  kubectl logs <pod>

STEP 3 — "RAISE THE DRAWBRIDGE" (blue shield):
- Two parallel actions shown as two guards:
  LEFT guard: "Network Isolation" — closing a gate
  caption "Apply deny-all NetworkPolicy"
  RIGHT guard: "Node Isolation" — blocking a road
  caption "kubectl cordon <node>"
  Warning note: "Do NOT delete pod yet — preserve evidence!"

STEP 4 — "INVESTIGATE" (teal detective icon):
- Five scouts sent on parallel missions:
  a) "Processes" — ps aux
  b) "Network" — ss -tlnp
  c) "Files" — find / -mtime -1
  d) "Permissions" — kubectl auth can-i --list --as=SA
  e) "Image" — trivy image <image>

STEP 5 — "PRESERVE EVIDENCE" (purple scroll icon):
- A scribe copying records
  kubectl get pod <pod> -o yaml > evidence.yaml
  kubectl logs <pod> > evidence-logs.txt

STEP 6 — "REMEDIATE" (green wrench icon):
- Workers repairing and fortifying:
  1. Delete compromised pod
  2. Rotate SA tokens
  3. Fix RBAC
  4. Update image
  5. Apply security controls
  6. Redeploy hardened

STEP 7 — "VERIFY ALL CLEAR" (green checkmark):
- Captain inspecting the restored defenses
  kubectl get pods / auth can-i / exec curl tests

Time banner: "Complete in under 15 minutes for CKS exam"
""",
    ),
    diagram(
        "11-securitycontext-cheatsheet",
        "cks-11-securitycontext-pod-vs-container.jpg",
        "The Armor Smith — SecurityContext Pod vs Container",
        "Layer 3 — Exam-Critical",
        "Green for secure settings, Red for dangerous, Navy for structure.",
        """
Draw a SPLIT-VIEW ARMOR WORKSHOP showing two workbenches:

LEFT WORKBENCH — "Pod-Level Armor" (blue border):
A suit of armor on a stand representing POD securityContext, with labeled parts:

spec:
  securityContext:         ← "ARMOR FOR THE WHOLE SQUAD"
    runAsUser: 1000        (each piece labeled on the armor)
    runAsGroup: 3000
    runAsNonRoot: true     (green glow)
    fsGroup: 2000
    supplementalGroups:
    sysctls:               (amber warning)
    seccompProfile:
      type: RuntimeDefault (teal glow)

Posted note: "fsGroup, supplementalGroups, sysctls — ONLY exist at Pod level"

RIGHT WORKBENCH — "Container-Level Armor" (green border):
Individual armor pieces for ONE soldier, representing container securityContext:

spec:
  containers:
  - name: app
    securityContext:              ← "ARMOR FOR ONE SOLDIER"
      runAsUser: 1000             — "Overrides squad armor"
      runAsNonRoot: true          (green)
      privileged: false           (RED DANGER label if true)
      allowPrivilegeEscalation: false  (RED DANGER label if true)
      readOnlyRootFilesystem: true     (green)
      capabilities:               (amber)
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
      seccompProfile:
        type: RuntimeDefault

Posted note: "privileged, allowPrivilegeEscalation, readOnlyRootFilesystem,
capabilities — ONLY exist at Container level"

CENTER — "Override Rules" (connecting arrows):
Arrows between workbenches showing which fields exist at both levels:
- runAsUser → "Container overrides Pod"
- runAsNonRoot → "Container overrides Pod"
- seccompProfile → "Container overrides Pod"

BOTTOM — "THE RESTRICTED PROFILE" (gold-bordered, starred):
A MASTER TEMPLATE posted prominently:

spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
  - securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]

Star banner: "MEMORIZE THIS — appears on nearly every CKS exam"
""",
    ),
    diagram(
        "12-cluster-hardening-checklist",
        "cks-12-cluster-hardening-checklist.jpg",
        "Fortress Inspection — Cluster Hardening Checklist",
        "Layer 2 — Operational",
        "Navy for components, Green for secure checks, Red for insecure findings.",
        """
Draw a FORTRESS INSPECTION REPORT with four columns, like a commander's
checklist posted on the war room wall:

COLUMN 1 — "The Main Gate (API Server)" (navy, gate icon):
Checklist scroll with inspection items:
☐ --anonymous-auth=false
☐ --authorization-mode=Node,RBAC
☐ --enable-admission-plugins: NodeRestriction, PodSecurity
☐ --audit-policy-file configured
☐ --encryption-provider-config set
☐ --kubelet-certificate-authority set
☐ --profiling=false
File location: /etc/kubernetes/manifests/kube-apiserver.yaml

COLUMN 2 — "The Wall Guards (kubelet)" (teal, guard icon):
☐ authentication.anonymous.enabled: false
☐ authorization.mode: Webhook
☐ readOnlyPort: 0
☐ protectKernelDefaults: true
☐ rotateCertificates: true
☐ TLS configured
File: /var/lib/kubelet/config.yaml

COLUMN 3 — "The Treasury (etcd)" (amber, vault icon):
☐ --client-cert-auth=true
☐ --peer-client-cert-auth=true
☐ TLS certificates configured
☐ Access restricted to API server only
☐ File permissions: 0600 for keys
File: /etc/kubernetes/manifests/etcd.yaml

COLUMN 4 — "Kingdom Law (General)" (green, shield icon):
☐ CIS Benchmark passed (kube-bench)
☐ Default ServiceAccount restricted
☐ RBAC least privilege
☐ NetworkPolicy default-deny
☐ PSA enforced
☐ Encryption at rest enabled
☐ Audit logging active

BOTTOM — "Inspection Commands" in monospace:
kube-bench run --targets master
kubectl auth can-i --list --as=system:serviceaccount:default:default
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates

Each item has a priority badge: P0 (red wax seal) / P1 (amber) / P2 (blue)
""",
    ),
    diagram(
        "13-attack-defense-map",
        "cks-13-attack-defense-mapping.jpg",
        "Battle Tactics — Attack → Defense Quick Reference",
        "Layer 3 — Exam-Critical",
        "Red for attacks on left, Green for defenses on right.",
        """
Draw a TWO-COLUMN BATTLE TACTICS BOARD — like a war room planning board
with red attack cards on the left and green defense cards on the right,
connected by arrows:

GROUP 1 — "Container Siege" (header banner):
🔴 Privileged container → 🟢 privileged: false
🔴 Root user → 🟢 runAsNonRoot: true, runAsUser: 1000
🔴 Privilege escalation → 🟢 allowPrivilegeEscalation: false
🔴 Excessive capabilities → 🟢 drop ALL, add only needed
🔴 Writable filesystem → 🟢 readOnlyRootFilesystem: true
🔴 Host namespace access → 🟢 hostPID/hostNetwork/hostIPC: false
🔴 Host filesystem mount → 🟢 Remove hostPath volumes

GROUP 2 — "Fortress Breach" (header banner):
🔴 Excessive API permissions → 🟢 RBAC least privilege
🔴 Unnecessary SA token → 🟢 automountServiceAccountToken: false
🔴 Unauthenticated kubelet → 🟢 anonymous-auth=false, webhook authz
🔴 Unencrypted etcd → 🟢 TLS + client certs
🔴 Unencrypted secrets → 🟢 EncryptionConfiguration
🔴 Anonymous API access → 🟢 --anonymous-auth=false

GROUP 3 — "Lateral Movement" (header banner):
🔴 East-west attack → 🟢 NetworkPolicy default-deny
🔴 Unrestricted egress → 🟢 Egress NetworkPolicy
🔴 Service exposure → 🟢 Ingress TLS

GROUP 4 — "Supply Chain Poison" (header banner):
🔴 Vulnerable image → 🟢 Trivy scan + image update
🔴 Untrusted registry → 🟢 Admission controller restriction
🔴 Unscanned deployment → 🟢 ValidatingAdmissionPolicy

GROUP 5 — "Infiltrator Detection" (header banner):
🔴 Shell in container → 🟢 Falco detection + alert
🔴 Suspicious process → 🟢 Runtime monitoring
🔴 Unrestricted syscalls → 🟢 seccomp RuntimeDefault

Bottom scroll: "Print this page. Review before exam."
""",
    ),
    diagram(
        "14-study-roadmap",
        "cks-14-study-roadmap-14-day.jpg",
        "The Campaign — 14-Day CKS Study Roadmap",
        "Layer 1 — Foundational",
        "All domain colors used for their respective topics, road metaphor.",
        """
Draw a WINDING ROAD / CAMPAIGN PATH from bottom-left to top-right across
the fortress landscape, with milestone markers at each day:

WEEK 1 — "Build the Fortress" (bottom half, blue-tinted region):

Day 1-2 milestone: "Fortify the Keep" (navy tower icon)
- CIS Benchmarks, kube-bench, API Server, kubelet, etcd security
- Milestone flag: "Core infrastructure secured"

Day 3 milestone: "Train the Guards" (purple guard icon)
- RBAC, ServiceAccounts, auth can-i
- Flag: "Access control mastered"

Day 4 milestone: "Forge the Armor" (green shield icon)
- SecurityContext, PSA, capabilities, seccomp
- Flag: "30 securityContext exercises done"

Day 5 milestone: "Build the Gates" (blue gate icon)
- NetworkPolicy: default deny, allow rules, troubleshooting
- Flag: "20 NetworkPolicies from scratch"

Day 6 milestone: "Secure the Trade Routes" (amber checkpoint icon)
- Trivy, admission controllers, image policy
- Flag: "Scan & restrict images"

Day 7 milestone: "Man the Watchtowers" (teal eye icon)
- Falco, audit policies, secrets/encryption
- Flag: "Week 1 complete — all domains covered"

WEEK 2 — "Battle Drills" (top half, green-tinted region):

Day 8-9: "Mixed Combat Drills" (stopwatch icon)
- Timed exercises across all domains
- Flag: "Speed improving"

Day 10: "Weak Points" (target icon) — Focus on gaps

Day 11: "War Game 1" (sword icon) — Full mock exam

Day 12: "Repairs" (wrench icon) — Fix gaps + Killer.sh Session 1

Day 13: "War Game 2" (sword icon) — Second mock, target 75%+

Day 14: "Final Review" (flag icon)
- Cheat sheet, quick drills, Killer.sh Session 2
- "GO / NO-GO decision"
- FINISH LINE with victory flag: "EXAM READY"

Draw a confidence meter along the path: RED → AMBER → GREEN
""",
    ),
    diagram(
        "15-psa-levels",
        "cks-15-pod-security-admission-levels.jpg",
        "Three Kingdoms — Pod Security Admission Levels",
        "Layer 3 — Exam-Critical",
        "Red for privileged, Amber for baseline, Green for restricted.",
        """
Draw three KINGDOMS side by side, each representing a PSA level:

LEFT — "The Lawless Lands" (RED territory, skull banner):
- Chaotic landscape, no walls, no guards
- Caption: "PRIVILEGED — Unrestricted, no security enforced"
- Badge: "DO NOT USE in production"
- Posted rules: "Everything allowed: privileged ✓, hostNetwork ✓,
  hostPID ✓, hostPath ✓, root ✓, any capabilities ✓"
- Use case label: "System-level pods only (kube-system)"
- Namespace label in monospace:
  pod-security.kubernetes.io/enforce: privileged

CENTER — "The Frontier" (AMBER territory, caution banner):
- Basic walls and simple gates, some guards
- Caption: "BASELINE — Prevents known privilege escalations"
- Badge: "Good starting point"
- BLOCKED sign: "privileged ✗, hostNetwork ✗, hostPID ✗"
- ALLOWED sign: "Run as root ✓ (not ideal), most capabilities ✓"
- Namespace label:
  pod-security.kubernetes.io/enforce: baseline

RIGHT — "The Fortress" (GREEN territory, shield banner):
- Thick walls, many guards, well-fortified
- Caption: "RESTRICTED — Best practice security posture"
- Badge: "CKS TARGET — know this cold"
- REQUIRED placard:
  runAsNonRoot: true ✓
  allowPrivilegeEscalation: false ✓
  capabilities: drop ALL ✓
  seccompProfile: RuntimeDefault ✓
- Namespace label:
  pod-security.kubernetes.io/enforce: restricted

BOTTOM — "Three Enforcement Modes" (horizontal bar):
- enforce (red stop sign) → "Block pod creation"
- warn (amber triangle) → "Allow but warn"
- audit (teal eye) → "Allow but log"

Example namespace labels in monospace:
kubectl label ns myapp \\
  pod-security.kubernetes.io/enforce=restricted \\
  pod-security.kubernetes.io/warn=restricted \\
  pod-security.kubernetes.io/audit=restricted

Banner: "PSA replaced PodSecurityPolicy (removed K8s 1.25) — old courses teach wrong approach!"
""",
    ),
    diagram(
        "16-secrets-lifecycle",
        "cks-16-secrets-security-lifecycle.jpg",
        "The Treasury Cycle — Kubernetes Secrets Lifecycle",
        "Layer 2 — Operational",
        "Navy/Gold for storage, Green for secure, Red for insecure paths.",
        """
Draw a CIRCULAR LIFECYCLE of a Kubernetes Secret as a treasury/vault cycle:

STAGE 1 (top) — "DEPOSIT" (messenger arriving with scroll):
- Caption: "CREATE"
- kubectl create secret generic mysecret --from-literal=password=abc123
- WARNING stamp: "base64 is ENCODING, not ENCRYPTION!"
- Visual: "abc123" → base64 → "YWJjMTIz" with red X: "NOT secure by itself"

STAGE 2 (right) — "VAULT STORAGE" (treasury vault):
- Caption: "STORE in etcd"
- TWO PATHS diverging:
  RED path (broken lock): "WITHOUT encryption config"
    "Stored as base64 — readable with etcdctl!" (danger)
  GREEN path (strong lock): "WITH EncryptionConfiguration"
    "Encrypted blob: k8s:enc:aescbc:..." (secure)

STAGE 3 (bottom-right) — "WITHDRAWAL" (guard checking ID):
- Caption: "ACCESS via RBAC"
- "kubectl get secret -o yaml → base64 (decode with base64 -d)"
- Warning: "Any pod with RBAC access can read ALL namespace secrets"
- Defense: "Use resourceNames to restrict to specific secrets"

STAGE 4 (bottom-left) — "DELIVERY METHOD" (two messengers):
LEFT messenger (green, preferred):
- "Volume Mount" — scroll carried in sealed tube
- "tmpfs, auto-rotated, not in environment"
RIGHT messenger (red, avoid):
- "Environment Variable" — scroll carried openly
- "Visible in pod spec, describe, logs — NOT rotated"

STAGE 5 (left) — "PROTECTION MEASURES" (guard station):
- Caption: "PROTECT"
- Checklist:
  ✓ EncryptionConfiguration enabled
  ✓ RBAC restricts secret access
  ✓ Audit logging captures reads
  ✓ automountServiceAccountToken: false
  ✓ Volume mounts, not env vars
  ✓ Immutable secrets where possible

CENTER — "Security Assessment" comparison posted:
| Control | Insecure | Secure |
| Storage | base64 in etcd | encrypted at rest |
| Access | default SA reads | RBAC + resourceNames |
| Delivery | env var | volume mount |
| Audit | no logging | RequestResponse level |
""",
    ),
    diagram(
        "17-context-safety",
        "cks-17-context-safety-preflight-ritual.jpg",
        "Pre-Flight Check — Context Safety Ritual",
        "Layer 1 — Foundational",
        "Neutral grey with sky-blue highlight accents, red warning borders.",
        """
Draw an AIRCRAFT COCKPIT INSTRUMENT PANEL (like the CKA style) with
exactly 6 round gauges/dials arranged in two rows of 3, each glowing
sky-blue when "checked":

ROW 1:
1. Gauge "SWITCH CONTEXT" — cluster icon needle,
   caption "kubectl config use-context <context-name>"
   Red warning placard below: "Wrong context = ZERO points!"

2. Gauge "SET NAMESPACE" — folder icon needle,
   caption "kubectl config set-context --current --namespace=<ns>"
   Note: "Default is 'default' — questions use other namespaces"

3. Gauge "VERIFY" — checkmark needle,
   caption "kubectl config current-context"
   caption "kubectl config view --minify | grep namespace"
   Note: "5 seconds to confirm, saves 5 minutes of wrong-cluster work"

ROW 2:
4. Gauge "INSPECT" — magnifying glass needle,
   caption "kubectl get/describe <resource>"
   caption "cat manifest.yaml (before editing)"
   Red placard: "For API server: ALWAYS cp manifest.yaml manifest.yaml.bak"

5. Gauge "MODIFY" — wrench needle,
   caption "Make changes, one at a time for control plane"
   caption "watch crictl ps | grep kube-apiserver (wait for restart)"

6. Gauge "VERIFY AGAIN" — double-checkmark needle,
   caption "kubectl auth can-i / curl / exec to test"
   caption "Confirm the security property holds"

Draw a bold arrow flowing left-to-right beneath all gauges:
"Execute this EXACT sequence before EVERY exam question, EVERY time."

TIME COST badge: "~30 seconds"
VALUE badge: "Prevents catastrophic exam mistakes"
""",
    ),
    # ── NEW BATCH: 22 additional sub-topic diagrams ──────────────────
    diagram(
        "20-linux-capabilities",
        "cks-20-linux-capabilities-reference.jpg",
        "The Armory — Linux Capabilities Reference",
        "Layer 3 — Exam-Critical",
        "Red for dangerous capabilities, Green for commonly needed, Amber for defaults.",
        """
Draw a WEAPONS ARMORY with three racks of capability badges/medals:

RACK 1 — "DANGEROUS — Never Grant Unless Required" (RED rack, skull icons):
Draw each capability as a red medal with skull:
- CAP_SYS_ADMIN — "God mode" (biggest medal, brightest red)
  Caption: "Mount filesystems, load kernel modules, namespace ops"
- CAP_NET_ADMIN — "Network takeover"
  Caption: "Modify routing, iptables, interfaces"
- CAP_SYS_PTRACE — "Process spy"
  Caption: "Trace/inspect any process, container escape risk"
- CAP_DAC_OVERRIDE — "Ignore file permissions"
- CAP_SYS_RAWIO — "Raw I/O access"
- CAP_NET_RAW — "Raw sockets, packet sniffing"

RACK 2 — "DEFAULT SET" (AMBER rack):
Show the ~14 capabilities granted by default in Docker/containerd:
CHOWN, DAC_OVERRIDE, FSETID, FOWNER, MKNOD, NET_RAW, SETGID, SETUID,
SETFCAP, SETPCAP, NET_BIND_SERVICE, SYS_CHROOT, KILL, AUDIT_WRITE
Caption: "These are granted even WITHOUT privileged: true"

RACK 3 — "COMMONLY NEEDED" (GREEN rack, shield icons):
- NET_BIND_SERVICE — "Bind ports < 1024" (most common add-back)
  Caption: "Web servers on port 80/443"

CENTER FLOW — "The CKS Pattern" (golden scroll):
Step 1: capabilities: drop: ["ALL"]  (red → empty rack)
Step 2: capabilities: add: ["NET_BIND_SERVICE"]  (green → one badge)
Caption: "ALWAYS drop ALL, then add back ONLY what's needed"

YAML in monospace:
securityContext:
  capabilities:
    drop: ["ALL"]
    add: ["NET_BIND_SERVICE"]

Bottom warning: "privileged: true = ALL capabilities granted — NEVER use!"
""",
    ),
    diagram(
        "21-seccomp-architecture",
        "cks-21-seccomp-architecture.jpg",
        "The Syscall Filter — Seccomp Architecture",
        "Layer 2 — Operational",
        "Teal for seccomp, Green for allowed syscalls, Red for blocked.",
        """
Draw a FILTER MECHANISM showing how seccomp intercepts syscalls:

TOP — "The Application" (grey figure):
- A worker figure making a request, caption "Container process calls syscall"
- Arrow down labeled "syscall (read, write, socket, mount...)"

MIDDLE — "The Seccomp Filter" (teal, LARGEST element):
Draw as a fine mesh sieve/filter with three modes shown side by side:

MODE 1: "Unconfined" (red border, open mesh):
- All syscalls pass through freely
- Caption: "NO filtering — all ~400 syscalls allowed"
- Badge: "INSECURE — avoid in CKS"

MODE 2: "RuntimeDefault" (green border, medium mesh):
- Most syscalls pass, dangerous ones blocked
- Blocked (red X): mount, reboot, ptrace, kexec_load
- Caption: "Blocks ~50 dangerous syscalls"
- Badge: "CKS DEFAULT — use this"
- YAML: seccompProfile: { type: RuntimeDefault }

MODE 3: "Localhost" (teal border, fine custom mesh):
- Custom profile loaded from file
- Caption: "Custom JSON profile"
- Path: /var/lib/kubelet/seccomp/profiles/my-profile.json
- YAML: seccompProfile: { type: Localhost, localhostProfile: profiles/my.json }

BOTTOM-LEFT — "Profile JSON Structure" (posted card):
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    { "names": ["read","write","exit"],
      "action": "SCMP_ACT_ALLOW" }
  ]
}

BOTTOM-RIGHT — "Decision Actions" (four colored badges):
- SCMP_ACT_ALLOW (green) — "Permit syscall"
- SCMP_ACT_ERRNO (amber) — "Return error"
- SCMP_ACT_KILL (red) — "Kill process"
- SCMP_ACT_LOG (teal) — "Allow but log"

Arrow below: "Kernel → (allowed syscall executes) OR (blocked → error/kill)"
""",
    ),
    diagram(
        "22-apparmor-workflow",
        "cks-22-apparmor-workflow.jpg",
        "The Magical Wards — AppArmor Workflow",
        "Layer 2 — Operational",
        "Teal/green for AppArmor lifecycle, Purple for enforcement modes.",
        """
Draw a LEFT-TO-RIGHT WORKFLOW showing the AppArmor lifecycle:

STEP 1 — "Write the Profile" (grey, scroll icon):
A scribe writing on a scroll, caption "Create AppArmor profile"
Show profile structure:
  #include <tunables/global>
  profile k8s-deny-write flags=(attach_disconnected) {
    #include <abstractions/base>
    file,
    deny /** w,    ← RED highlight "deny all writes"
  }
Caption: "Profile restricts what a process can do"

STEP 2 — "Load the Profile" (amber, magic wand icon):
A wizard loading the ward, caption "Load on EVERY node"
Command: apparmor_parser -q /etc/apparmor.d/k8s-deny-write
Warning: "Must be loaded on the node where pod runs!"

STEP 3 — "Verify Loaded" (teal, eye icon):
An inspector checking, caption "Confirm profile active"
Command: aa-status | grep k8s-deny-write
Expected output: k8s-deny-write (enforce)

STEP 4 — "Apply to Pod" (green, shield icon):
Two SIDE-BY-SIDE methods:

LEFT — "Legacy (Annotation)" (amber border):
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-deny-write
Caption: "Old method — still works"

RIGHT — "Native (K8s 1.30+)" (green border, starred):
spec:
  containers:
  - name: app
    securityContext:
      appArmorProfile:
        type: Localhost
        localhostProfile: k8s-deny-write
Caption: "NEW method — preferred for CKS"
Star: "CKS exam likely uses this"

BOTTOM — "Three Enforcement Modes" (three colored badges):
- enforce (green shield) — "Enforce AND log violations"
- complain (amber triangle) — "Log only, don't enforce"
- unconfined (red X) — "No restrictions"
""",
    ),
    diagram(
        "23-pod-transformation",
        "cks-23-pod-transformation-guide.jpg",
        "From Insecure to Restricted — Pod Transformation",
        "Layer 3 — Exam-Critical",
        "Red for insecure fields, Green for secure fields, arrows for transformations.",
        """
Draw a BEFORE/AFTER TRANSFORMATION showing two pods side by side:

LEFT — "INSECURE POD" (red border, skull banner):
A posted YAML manifest with RED highlights on every insecure field:

apiVersion: v1
kind: Pod
metadata:
  name: insecure-app
spec:
  containers:
  - name: app
    image: nginx:latest        ← RED "Use specific tag"
    securityContext:
      privileged: true         ← RED "God mode!"
      runAsUser: 0             ← RED "Running as ROOT"
      allowPrivilegeEscalation: true  ← RED
      readOnlyRootFilesystem: false   ← RED
      capabilities:
        add: ["ALL"]           ← RED "All capabilities!"
    volumeMounts:
    - name: host
      mountPath: /host
  volumes:
  - name: host
    hostPath:                  ← RED "Host filesystem access!"
      path: /

RIGHT — "RESTRICTED POD" (green border, shield banner):
Same pod with GREEN highlights on every secure field:

apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  automountServiceAccountToken: false  ← GREEN "NEW"
  securityContext:
    runAsNonRoot: true                 ← GREEN
    seccompProfile:
      type: RuntimeDefault             ← GREEN
  containers:
  - name: app
    image: nginx:1.27-alpine           ← GREEN "Pinned + minimal"
    securityContext:
      allowPrivilegeEscalation: false  ← GREEN
      readOnlyRootFilesystem: true     ← GREEN
      runAsUser: 1000                  ← GREEN
      capabilities:
        drop: ["ALL"]                  ← GREEN
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}                       ← GREEN "Safe volume"

CENTER ARROWS between fields showing each transformation.

BOTTOM — "Transformation Checklist" (8 numbered steps):
1. Pin image tag  2. runAsNonRoot  3. runAsUser: non-zero
4. allowPrivilegeEscalation: false  5. readOnlyRootFilesystem: true
6. capabilities: drop ALL  7. seccompProfile: RuntimeDefault
8. Remove hostPath, add emptyDir for writable paths

Banner: "THIS transformation appears on nearly every CKS exam!"
""",
    ),
    diagram(
        "24-container-immutability",
        "cks-24-container-immutability.jpg",
        "The Sealed Vault — Container Immutability",
        "Layer 2 — Operational",
        "Green for immutable techniques, Red for what attackers can't do.",
        """
Draw a SEALED VAULT showing three layers of immutability:

LAYER 1 — "Read-Only Filesystem" (green, lock on door):
A container building with a padlocked door:
readOnlyRootFilesystem: true
Plus emptyDir volumes for writable paths:
  volumeMounts:
  - name: tmp
    mountPath: /tmp
  - name: cache
    mountPath: /var/cache
volumes:
- name: tmp
  emptyDir: {}
Caption: "Can't write malware to disk"

LAYER 2 — "Distroless / Minimal Images" (green, empty room):
Show two rooms side by side:
LEFT (red): Full OS image — bash, apt, curl, wget visible
RIGHT (green): Distroless — only the app binary, nothing else
Caption: "No shell = can't exec into container"
Examples: gcr.io/distroless/static, alpine (minimal)

LAYER 3 — "No Package Manager" (green, sealed crate):
Show a sealed supply crate with no tools:
Caption: "Can't install packages at runtime"
Blocked commands: apt-get, yum, apk (red X on each)

RIGHT SIDE — "What Attackers CAN'T Do" (red X marks):
- ✗ Drop malware binaries
- ✗ Open a reverse shell
- ✗ Install hacking tools
- ✗ Modify application files
- ✗ Change configuration

BOTTOM — "Immutability Detection with Falco" (teal):
Falco rule that fires if filesystem is modified:
- rule: Write below binary dir
  condition: write and bin_dir
Caption: "Even if attacker bypasses, Falco detects"

Banner: "Immutable containers = defense in depth + detection"
""",
    ),
    diagram(
        "25-rbac-escalation-paths",
        "cks-25-rbac-escalation-paths.jpg",
        "Eight Gates of Danger — RBAC Privilege Escalation",
        "Layer 3 — Exam-Critical",
        "Red for attack chains, Green for defenses, Purple for RBAC.",
        """
Draw 8 ATTACK PATH DIAGRAMS arranged in a 2x4 grid, each showing an
escalation chain (red arrows) and its defense (green shield):

PATH 1 — "bind verb" (top-left):
Red chain: User with 'bind' verb → self-assign cluster-admin
Green shield: "Never grant bind verb to non-admins"

PATH 2 — "escalate verb" (top-right):
Red chain: User with 'escalate' → create Role with higher privileges
Green shield: "Never grant escalate verb"

PATH 3 — "create pods" (second row left):
Red chain: Create pod → mount SA token → use token for API access
Green shield: "Restrict pod creation, automountServiceAccountToken: false"

PATH 4 — "get secrets" (second row right):
Red chain: get secrets permission → read all secrets in namespace → extract tokens/passwords
Green shield: "Use resourceNames to restrict to specific secrets"

PATH 5 — "impersonate" (third row left):
Red chain: impersonate verb → --as=admin → full cluster access
Green shield: "Never grant impersonate on users/groups"

PATH 6 — "node proxy" (third row right):
Red chain: nodes/proxy permission → direct kubelet API → exec into any pod
Green shield: "Restrict nodes/proxy, use NodeRestriction"

PATH 7 — "SA token theft" (bottom left):
Red chain: exec into pod → cat /var/run/secrets/.../ → steal token → API access
Green shield: "automountServiceAccountToken: false + projected tokens"

PATH 8 — "aggregation labels" (bottom right):
Red chain: Create CRD with aggregation label → auto-merge into system roles
Green shield: "Restrict CRD creation, audit aggregation labels"

BOTTOM BANNER — Key audit commands:
kubectl auth can-i --list --as=system:serviceaccount:ns:sa
kubectl get clusterrolebindings -o wide | grep cluster-admin
""",
    ),
    diagram(
        "26-sa-token-evolution",
        "cks-26-serviceaccount-token-evolution.jpg",
        "Token Evolution — Legacy vs Projected vs Bound",
        "Layer 2 — Operational",
        "Red for legacy (insecure), Amber for projected, Green for bound (most secure).",
        """
Draw a THREE-ERA TIMELINE showing ServiceAccount token evolution:

ERA 1 — "The Old Way" (RED, pre-K8s 1.24):
Draw an old, worn scroll:
- Type: Secret-based token
- Lifetime: NEVER EXPIRES (red danger)
- Audience: unrestricted
- Location: Secret object in namespace
- Risk: "Token lives forever, even after pod deleted"
- YAML: type: kubernetes.io/service-account-token
- Status: "Auto-creation DISABLED since 1.24"

ERA 2 — "The Modern Way" (AMBER, K8s 1.22+):
Draw a newer, sealed scroll:
- Type: Projected volume token
- Lifetime: 1 hour (auto-rotated)
- Audience: bound to API server
- Location: /var/run/secrets/kubernetes.io/serviceaccount/token
- Benefit: "Time-limited, audience-bound, auto-rotated"
- Pod spec:
  volumes:
  - name: kube-api-access
    projected:
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607

ERA 3 — "The Secure Way" (GREEN, K8s 1.31+):
Draw a modern, reinforced scroll:
- Type: Node-bound token
- Lifetime: short-lived
- Bound to: specific node + pod
- Benefit: "Token invalidated if pod moves to different node"
- Status: "Latest and most secure"

CENTER — "Comparison Table" (posted chart):
| Feature      | Legacy    | Projected | Node-Bound |
| Expiry       | Never     | 1 hour    | Short      |
| Audience     | Any       | Specific  | Specific   |
| Auto-rotate  | No        | Yes       | Yes        |
| Node-bound   | No        | No        | Yes        |
| CKS Relevant | Know risk | Default   | Best       |

BOTTOM — "CKS Pattern":
automountServiceAccountToken: false  (disable for pods that don't need it)
""",
    ),
    diagram(
        "27-sa-hardening",
        "cks-27-serviceaccount-hardening.jpg",
        "Lock the Golem — ServiceAccount Hardening",
        "Layer 3 — Exam-Critical",
        "Green for hardened, Red for insecure defaults.",
        """
Draw a GOLEM (mechanical automaton) MAINTENANCE MANUAL with 6 sections:

SECTION 1 — "Disable Auto-Mount" (biggest section, green border):
Two golems side by side:
LEFT (red): Golem with exposed key on chest
  automountServiceAccountToken: true (DEFAULT!)
  "Token mounted at /var/run/secrets/..."
RIGHT (green): Golem with locked chest
  automountServiceAccountToken: false
  "No token mounted — pod can't access API"

SECTION 2 — "Dedicated SA Per Workload" (green):
Three golems, each with unique name badge:
BAD (red): All pods using "default" SA
GOOD (green): Each deployment has its own SA
  kubectl create sa frontend-sa
  kubectl create sa backend-sa

SECTION 3 — "Least Privilege RBAC" (purple/green):
A golem with minimal medals:
BAD: ClusterRoleBinding to cluster-admin
GOOD: Role with specific resources and verbs only
  rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]

SECTION 4 — "Restrict Default SA" (green):
The default SA in every namespace:
  kubectl patch sa default -n <ns> -p '{"automountServiceAccountToken": false}'
Caption: "Do this for EVERY namespace"

SECTION 5 — "Clean Up Unused Tokens" (amber):
  kubectl get secrets --field-selector type=kubernetes.io/service-account-token
Caption: "Delete legacy tokens that shouldn't exist"

SECTION 6 — "Audit SA Permissions" (teal):
  kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa>
Caption: "Run this for every SA to find over-privileged accounts"

BOTTOM BANNER: "ServiceAccount security = top RBAC exam topic"
""",
    ),
    diagram(
        "28-networkpolicy-and-or",
        "cks-28-networkpolicy-and-vs-or.jpg",
        "The Gate Logic — AND vs OR Deep Dive",
        "Layer 3 — Exam-Critical",
        "Blue for AND logic, Green for OR logic, Red for common mistakes.",
        """
Draw a FULL-PAGE COMPARISON of AND vs OR selector logic:

TOP BANNER (red, large): "#1 CKS EXAM TRAP — Indentation Changes Meaning!"

LEFT HALF — "AND Logic" (blue border):
YAML (with indentation arrows):
  ingress:
  - from:
    - namespaceSelector:     ← SAME list entry
        matchLabels:
          team: frontend
      podSelector:           ← SAME list entry (no dash!)
        matchLabels:
          role: api

Venn diagram below: Two overlapping circles
- Circle 1: "Pods in namespace team=frontend"
- Circle 2: "Pods with role=api"
- ONLY the INTERSECTION is highlighted (small area)
- Caption: "Must match BOTH — namespace AND pod label"

Traffic flow diagram: Only pods matching BOTH criteria get through gate.

RIGHT HALF — "OR Logic" (green border):
YAML (with indentation arrows):
  ingress:
  - from:
    - namespaceSelector:     ← First list entry (has dash)
        matchLabels:
          team: frontend
    - podSelector:           ← Second list entry (has dash!)
        matchLabels:
          role: api

Venn diagram below: Two circles
- Circle 1: "ALL pods in namespace team=frontend"
- Circle 2: "ALL pods with role=api (any namespace)"
- BOTH circles fully highlighted (large area!)
- Caption: "Match EITHER — much broader than AND!"

Traffic flow: Many more pods get through gate.

CENTER — "The Critical Difference" (red highlight box):
Show the YAML diff — the ONLY change is a single dash "-" character:
  AND: "  podSelector:" (no dash, indented under namespaceSelector's dash)
  OR:  "- podSelector:" (has its own dash, new list entry)

BOTTOM — "Memory Trick" (golden scroll):
"Same dash = AND (both must match)"
"Separate dash = OR (either can match)"
"When in doubt, create the policy and test with curl!"
""",
    ),
    diagram(
        "29-networkpolicy-patterns",
        "cks-29-networkpolicy-essential-patterns.jpg",
        "Five Essential Gate Orders — NetworkPolicy Patterns",
        "Layer 3 — Exam-Critical",
        "Blue for network controls, Red for denied traffic, Green for allowed.",
        """
Draw FIVE MINI DIAGRAMS in a row, each showing a pattern:

PATTERN 1 — "Deny All Ingress" (red lock on gate):
Three pods, all incoming arrows blocked (red X)
YAML card:
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: deny-all-ingress
  spec:
    podSelector: {}
    policyTypes: [Ingress]
Caption: "Empty podSelector = all pods. No ingress rules = deny all."

PATTERN 2 — "Deny All Egress" (red lock on exit):
Three pods, all outgoing arrows blocked (red X)
YAML card:
  spec:
    podSelector: {}
    policyTypes: [Egress]
Caption: "WARNING — also blocks DNS! Add Pattern 3."

PATTERN 3 — "Allow DNS Egress" (green arrow to DNS tower):
Pod with green arrow to kube-dns, red X on everything else
YAML card:
  spec:
    podSelector: {}
    policyTypes: [Egress]
    egress:
    - to:
      - namespaceSelector: {}
      ports:
      - port: 53
        protocol: UDP
      - port: 53
        protocol: TCP
Caption: "ALWAYS pair with deny-all-egress!"
Star: "EXAM FAVORITE"

PATTERN 4 — "Allow From Namespace" (green arrow from labeled district):
Pod receiving green arrow from namespace with label env=prod
YAML card:
  spec:
    podSelector:
      matchLabels: { app: api }
    ingress:
    - from:
      - namespaceSelector:
          matchLabels: { env: prod }
Caption: "Only pods from prod namespace can reach api"

PATTERN 5 — "Deny All Both" (full lockdown):
Pod with all arrows blocked in both directions
YAML card:
  spec:
    podSelector: {}
    policyTypes: [Ingress, Egress]
Caption: "Complete isolation — start here, then open what's needed"

BOTTOM: "CKS Strategy: Apply deny-all FIRST, then add specific allow rules"
""",
    ),
    diagram(
        "30-admission-control-types",
        "cks-30-admission-control-comparison.jpg",
        "Three Checkpoint Guards — Admission Control Comparison",
        "Layer 2 — Operational",
        "Amber for admission, Navy for API server, Green for best practice.",
        """
Draw THREE CHECKPOINT GUARDS side by side, each representing a type:

GUARD 1 — "ImagePolicyWebhook" (amber, left):
A guard checking cargo manifests:
Architecture: API Server → webhook call → External service → allow/deny
Setup steps (numbered):
1. Enable admission plugin in kube-apiserver
2. Create AdmissionConfiguration file
3. Create kubeconfig for webhook
4. Mount configs into API server pod
Key field: defaultAllow: true/false
Pros: "Simple image policy"
Cons: "External service needed, complex setup"
Star: "HIGH exam probability"

GUARD 2 — "ValidatingAdmissionWebhook" (amber, center):
A guard with a rulebook calling for backup:
Architecture: API Server → webhook call → Your service → allow/deny
Setup: ValidatingWebhookConfiguration resource
Key features:
- Can match on any resource
- Full request context available
- Namespace selector for targeting
Pros: "Flexible, any logic"
Cons: "Must run your own webhook server"

GUARD 3 — "ValidatingAdmissionPolicy" (green, right, STARRED):
A guard with a built-in rulebook (no external call):
Architecture: API Server → CEL expression → allow/deny (NO webhook!)
Setup: ValidatingAdmissionPolicy + PolicyBinding
Example CEL: object.spec.containers.all(c, c.securityContext.runAsNonRoot == true)
Pros: "No webhook server needed, GA in 1.30"
Cons: "CEL expressions only"
Star: "NEWEST — likely on CKS exam"

COMPARISON TABLE (bottom):
| Feature          | ImagePolicy | Webhook | VAP (CEL) |
| External service | Yes         | Yes     | No        |
| Complexity       | High        | Medium  | Low       |
| K8s version      | Old         | 1.16+   | 1.30+ GA  |
| CKS weight       | High        | Medium  | Growing   |
""",
    ),
    diagram(
        "31-trivy-workflow",
        "cks-31-trivy-scanning-workflow.jpg",
        "The Inspector — Trivy Scanning Workflow",
        "Layer 2 — Operational",
        "Amber for scanning, Red for vulnerabilities found, Green for clean.",
        """
Draw a QUALITY INSPECTION STATION with conveyor belt:

INPUT (left) — container images on conveyor belt arriving for inspection

STATION 1 — "Image Scan" (amber, magnifying glass):
Inspector examining the image layers:
Command: trivy image nginx:1.27
Output shows: CVE table with severity columns
Flags highlighted:
  --severity CRITICAL,HIGH   ← "Filter to exam-relevant"
  --ignore-unfixed           ← "Skip unfixable CVEs"
  -f json                    ← "Machine-readable output"

STATION 2 — "Filesystem Scan" (amber, folder icon):
Inspector examining source code:
Command: trivy fs /path/to/project
Caption: "Scan source code, IaC files, Dockerfiles"

STATION 3 — "Config Scan" (amber, scroll icon):
Inspector examining YAML manifests:
Command: trivy config /path/to/k8s-manifests/
Caption: "Check Kubernetes YAML for misconfigurations"

OUTPUT — Two paths:
GREEN path (checkmark): "No CRITICAL/HIGH CVEs → Deploy"
RED path (X mark): "Vulnerabilities found → Fix before deploying"

SEVERITY GUIDE (color-coded badges):
- CRITICAL (bright red) — "Exploit available, patch immediately"
- HIGH (red) — "Significant risk"
- MEDIUM (amber) — "Moderate risk"
- LOW (green) — "Minimal risk"

BOTTOM — "Key Exam Commands" (monospace scroll):
trivy image --severity CRITICAL,HIGH nginx:1.27
trivy image --severity CRITICAL --ignore-unfixed <image>
trivy image -f json -o results.json <image>

Banner: "Trivy = PRIMARY scanning tool for CKS exam"
""",
    ),
    diagram(
        "32-imagepolicywebhook",
        "cks-32-imagepolicywebhook-setup.jpg",
        "The Great Gate — ImagePolicyWebhook Setup",
        "Layer 2 — Operational",
        "Amber for configuration, Navy for API server, Green for completion.",
        """
Draw a STEP-BY-STEP CONSTRUCTION BLUEPRINT for ImagePolicyWebhook:

STEP 1 — "Enable Plugin" (navy, wrench icon):
Modify kube-apiserver.yaml:
  --enable-admission-plugins=...,ImagePolicyWebhook
File: /etc/kubernetes/manifests/kube-apiserver.yaml
Warning: "API server will restart after edit!"

STEP 2 — "Create Admission Config" (amber, scroll icon):
/etc/kubernetes/admission/admission-config.yaml:
  apiVersion: apiserver.config.k8s.io/v1
  kind: AdmissionConfiguration
  plugins:
  - name: ImagePolicyWebhook
    configuration:
      imagePolicy:
        kubeConfigFile: /etc/kubernetes/admission/kubeconfig.yaml
        allowTTL: 50
        denyTTL: 50
        retryBackoff: 500
        defaultAllow: false    ← RED "false = deny if webhook unavailable"

STEP 3 — "Create Kubeconfig" (amber, key icon):
/etc/kubernetes/admission/kubeconfig.yaml:
  clusters:
  - cluster:
      certificate-authority: /etc/kubernetes/admission/webhook-ca.pem
      server: https://image-review.example.com/review
  users:
  - user:
      client-certificate: /etc/kubernetes/admission/webhook-client.pem
      client-key: /etc/kubernetes/admission/webhook-client-key.pem

STEP 4 — "Mount Into API Server" (green, volume icon):
Add to kube-apiserver.yaml:
  --admission-control-config-file=/etc/kubernetes/admission/admission-config.yaml
  volumeMounts:
  - name: admission
    mountPath: /etc/kubernetes/admission
    readOnly: true
  volumes:
  - name: admission
    hostPath:
      path: /etc/kubernetes/admission

STEP 5 — "Verify" (green, checkmark):
  kubectl run test --image=untrusted:latest
  Expected: Error — image rejected by webhook

BOTTOM WARNING: "Missing volume mount = API server crash! Always backup manifest first."
""",
    ),
    diagram(
        "33-certificate-map",
        "cks-33-kubernetes-pki-certificate-map.jpg",
        "The Royal Seals — Kubernetes PKI Certificate Map",
        "Layer 2 — Operational",
        "Navy for CA certs, Green for server certs, Amber for client certs.",
        """
Draw a CERTIFICATE TREE showing /etc/kubernetes/pki/:

ROOT — "Cluster CA" (navy, crown icon):
ca.crt + ca.key
Caption: "Signs all cluster certificates"
Branches into:

BRANCH 1 — "API Server" (green, gate icon):
├── apiserver.crt + apiserver.key
│   Caption: "API server's TLS cert"
│   Used by: kube-apiserver (--tls-cert-file)
├── apiserver-kubelet-client.crt + .key
│   Caption: "API server → kubelet client cert"
│   Used by: kube-apiserver (--kubelet-client-certificate)
└── apiserver-etcd-client.crt + .key
    Caption: "API server → etcd client cert"

BRANCH 2 — "etcd CA" (amber, vault icon):
etcd/ca.crt + etcd/ca.key
├── etcd/server.crt + .key (etcd server TLS)
├── etcd/peer.crt + .key (etcd peer TLS)
└── etcd/healthcheck-client.crt + .key

BRANCH 3 — "Front Proxy CA" (grey):
front-proxy-ca.crt + .key
└── front-proxy-client.crt + .key
    Caption: "API aggregation layer"

BRANCH 4 — "Service Account" (purple):
sa.key + sa.pub
Caption: "Signs SA tokens (not a CA)"

RIGHT PANEL — "File Permissions" (checklist):
- Private keys (.key): 0600 (owner read/write only)
- Certificates (.crt): 0644 (world readable)
- CA keys: MOST CRITICAL — guard with your life
Command: ls -la /etc/kubernetes/pki/

BOTTOM — "Certificate Check Commands":
openssl x509 -in apiserver.crt -noout -text
openssl x509 -in apiserver.crt -noout -dates
kubeadm certs check-expiration
""",
    ),
    diagram(
        "34-kubelet-security",
        "cks-34-kubelet-security-config.jpg",
        "The Wall Guard — Kubelet Security Configuration",
        "Layer 2 — Operational",
        "Navy for kubelet, Red for insecure defaults, Green for secure settings.",
        """
Draw a GUARD POST CONFIGURATION PANEL for kubelet security:

Split into TWO COLUMNS: INSECURE (red, left) vs SECURE (green, right)

ROW 1 — "Anonymous Access":
RED: authentication.anonymous.enabled: true
  "Anyone can access kubelet API!"
GREEN: authentication.anonymous.enabled: false
  "Must authenticate to access kubelet"

ROW 2 — "Authorization":
RED: authorization.mode: AlwaysAllow
  "All authenticated requests permitted!"
GREEN: authorization.mode: Webhook
  "Delegates to API server RBAC"

ROW 3 — "Read-Only Port":
RED: readOnlyPort: 10255
  "Unauthenticated metrics/info exposure!"
GREEN: readOnlyPort: 0
  "Disabled — use authenticated port only"

ROW 4 — "Certificate Rotation":
RED: rotateCertificates: false
  "Certs expire, manual renewal needed"
GREEN: rotateCertificates: true
  "Auto-rotates kubelet client certificates"

ROW 5 — "Kernel Defaults":
RED: protectKernelDefaults: false
GREEN: protectKernelDefaults: true
  "Refuse to start if kernel params are insecure"

ROW 6 — "TLS Configuration":
RED: No TLS configured
GREEN: tlsCertFile + tlsPrivateKeyFile set

CONFIG FILE LOCATION:
/var/lib/kubelet/config.yaml
OR kubelet flags in systemd unit

BOTTOM — "Quick Check Commands":
curl -sk https://<node>:10250/pods  (should get 401)
curl -sk http://<node>:10255/pods   (should timeout/refuse)
ps aux | grep kubelet | grep -- --config
""",
    ),
    diagram(
        "35-etcd-security",
        "cks-35-etcd-security-config.jpg",
        "The Treasury Guard — etcd Security Configuration",
        "Layer 2 — Operational",
        "Navy for etcd, Gold accents for encryption, Green for secure.",
        """
Draw a VAULT GUARD STATION showing etcd security:

CENTER — "etcd Vault" (navy with gold lock):
A fortified vault with three security layers:

LAYER 1 — "Client TLS" (green border):
Flags on the vault door:
  --cert-file=/path/to/server.crt
  --key-file=/path/to/server.key
  --client-cert-auth=true          ← CRITICAL (green star)
  --trusted-ca-file=/path/to/ca.crt
Caption: "Require client certificates for ALL connections"

LAYER 2 — "Peer TLS" (green border):
Flags on the side wall:
  --peer-cert-file=/path/to/peer.crt
  --peer-key-file=/path/to/peer.key
  --peer-client-cert-auth=true     ← CRITICAL
  --peer-trusted-ca-file=/path/to/ca.crt
Caption: "Encrypt etcd-to-etcd communication"

LAYER 3 — "Access Restriction" (navy):
  --listen-client-urls=https://127.0.0.1:2379
Caption: "Only API server can connect"

LEFT PANEL — "File Permissions Check":
Checklist:
  etcd data dir: 0700
  Key files: 0600
  Cert files: 0644
Command: stat -c '%a %n' /etc/kubernetes/pki/etcd/*

RIGHT PANEL — "Verify etcd Encryption":
  ETCDCTL_API=3 etcdctl \\
    --cacert=/etc/kubernetes/pki/etcd/ca.crt \\
    --cert=/etc/kubernetes/pki/etcd/server.crt \\
    --key=/etc/kubernetes/pki/etcd/server.key \\
    get /registry/secrets/default/my-secret

  If encrypted: "k8s:enc:aescbc:v1:..." (green)
  If NOT encrypted: readable base64 text (red danger!)

BOTTOM — "etcd Backup Command" (amber):
  ETCDCTL_API=3 etcdctl snapshot save backup.db \\
    --endpoints=https://127.0.0.1:2379 \\
    --cacert --cert --key (same flags)

Static pod manifest: /etc/kubernetes/manifests/etcd.yaml
""",
    ),
    diagram(
        "36-secret-delivery",
        "cks-36-secret-delivery-env-vs-volume.jpg",
        "Two Messengers — Env Var vs Volume Mount",
        "Layer 2 — Operational",
        "Red for env var (insecure), Green for volume mount (secure).",
        """
Draw TWO MESSENGERS delivering secrets to a pod:

LEFT — "The Careless Messenger" (RED border, open scroll):
Environment Variable delivery:
  env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password

RISKS (red flags, each with icon):
1. "Visible in pod spec" — kubectl describe pod shows it
2. "Visible in /proc" — cat /proc/1/environ exposes it
3. "Inherited by child processes" — every subprocess gets it
4. "Appears in crash dumps/logs" — accidental exposure
5. "NOT auto-updated" — pod restart needed for changes
6. "Shows in container inspect" — crictl inspect reveals it

RIGHT — "The Secure Messenger" (GREEN border, sealed tube):
Volume Mount delivery:
  volumeMounts:
  - name: secret-vol
    mountPath: /etc/secrets
    readOnly: true
  volumes:
  - name: secret-vol
    secret:
      secretName: db-secret
      defaultMode: 0400

BENEFITS (green shields):
1. "tmpfs backed" — never written to disk on node
2. "Not in kubectl describe" — not visible in pod spec
3. "File permissions" — restrict read access (0400)
4. "Auto-updated" — kubelet refreshes periodically
5. "Not inherited by child processes" — app must read file
6. "Can use subPath for specific keys"

CENTER — "Verdict" (gold banner):
"ALWAYS use volume mounts for secrets in CKS exam"

BOTTOM — "Reading secrets in the app":
  cat /etc/secrets/password   (volume)
  echo $DB_PASSWORD           (env — avoid!)
""",
    ),
    diagram(
        "37-encryption-provider-order",
        "cks-37-encryption-provider-ordering.jpg",
        "First Scribe Writes — Encryption Provider Ordering",
        "Layer 2 — Operational",
        "Green for correct ordering, Red for dangerous ordering.",
        """
Draw TWO SCENARIOS side by side:

LEFT — "CORRECT ORDER" (green border, shield):
Title: "Encrypted by Default"
EncryptionConfiguration YAML:
  providers:
  - aescbc:           ← GREEN "FIRST = encrypts new data"
      keys:
      - name: key1
        secret: <key>
  - identity: {}      ← GREY "FALLBACK = reads old unencrypted data"

Flow diagram:
  New Secret → aescbc provider → ENCRYPTED in etcd ✓
  Old Secret ← identity provider ← reads old plaintext ✓

Badge: "CORRECT — new data encrypted, old data still readable"

RIGHT — "WRONG ORDER" (red border, skull):
Title: "Identity First = NO ENCRYPTION!"
EncryptionConfiguration YAML:
  providers:
  - identity: {}      ← RED "FIRST = stores as plaintext!"
  - aescbc:
      keys:
      - name: key1
        secret: <key>

Flow diagram:
  New Secret → identity provider → PLAINTEXT in etcd ✗
  "aescbc is never used for new writes!"

Badge: "WRONG — data stored unencrypted!"

CENTER — "The Rule" (golden banner):
"FIRST provider in the list = ENCRYPTS new data"
"ALL providers = tried for DECRYPTION (in order)"

BOTTOM — "Key Rotation Process" (numbered steps):
1. Add new key as FIRST in aescbc keys list
2. Restart API server
3. Re-encrypt all secrets:
   kubectl get secrets --all-namespaces -o json | kubectl replace -f -
4. Remove old key from list
5. Restart API server again

Warning: "Never remove old key before re-encrypting all data!"
""",
    ),
    diagram(
        "38-crictl-cheatsheet",
        "cks-38-crictl-command-cheatsheet.jpg",
        "The Runtime Inspector — crictl Cheatsheet",
        "Layer 2 — Operational",
        "Teal for crictl commands, Grey for comparison with kubectl.",
        """
Draw a TOOL REFERENCE CARD organized by task:

HEADER: "crictl — Container Runtime Interface CLI"
Subheader: "Direct runtime access, bypasses Kubernetes API"
Config: /etc/crictl.yaml → runtime-endpoint: unix:///run/containerd/containerd.sock

SECTION 1 — "Container Operations" (teal):
crictl ps                    — List running containers
crictl ps -a                 — List ALL containers (inc. stopped)
crictl inspect <container>   — Container details (JSON)
crictl logs <container>      — Container logs
crictl exec -it <container> sh — Shell into container
crictl stop <container>      — Stop container
crictl rm <container>        — Remove container

SECTION 2 — "Image Operations" (amber):
crictl images                — List images on node
crictl pull <image>          — Pull image
crictl rmi <image>           — Remove image
crictl inspecti <image>      — Image details

SECTION 3 — "Pod Operations" (blue):
crictl pods                  — List pods (sandbox)
crictl inspectp <pod>        — Pod sandbox details
crictl stopp <pod>           — Stop pod sandbox
crictl rmp <pod>             — Remove pod sandbox

SECTION 4 — "Troubleshooting" (green):
crictl stats                 — Container resource usage
crictl info                  — Runtime info

COMPARISON TABLE — "crictl vs kubectl":
| Task          | crictl          | kubectl          |
| List pods     | crictl pods     | kubectl get pods |
| Container logs| crictl logs     | kubectl logs     |
| Exec into     | crictl exec     | kubectl exec     |
| Level         | Runtime (node)  | API (cluster)    |
| Auth needed   | SSH to node     | kubeconfig       |

BOTTOM: "Use crictl when: kubectl not available, investigating at runtime level,
checking container state after API server is down, CKS incident response"
""",
    ),
    diagram(
        "39-tool-decision-tree",
        "cks-39-security-tool-decision-tree.jpg",
        "Which Tool? — CKS Security Tool Decision Tree",
        "Layer 1 — Foundational",
        "All domain colors for their respective tool categories.",
        """
Draw a DECISION TREE flowchart starting from the center:

ROOT — "What security task?" (grey, compass icon):

BRANCH 1 (amber) — "Scan for vulnerabilities?"
→ "Container image" → trivy image <image>
→ "Source code" → trivy fs /path
→ "K8s manifests" → trivy config /path
→ "CIS benchmarks" → kube-bench run --targets master

BRANCH 2 (teal) — "Monitor runtime?"
→ "Syscall monitoring" → Falco
→ "Process inspection" → crictl ps / crictl inspect
→ "Network connections" → ss -tlnp / netstat
→ "Container logs" → crictl logs / kubectl logs

BRANCH 3 (purple) — "Check access control?"
→ "What can user X do?" → kubectl auth can-i --list --as=X
→ "Who has cluster-admin?" → kubectl get clusterrolebindings -o wide
→ "SA permissions?" → kubectl auth can-i --list --as=system:serviceaccount:ns:sa

BRANCH 4 (green) — "Verify certificates?"
→ "Check cert details" → openssl x509 -in cert.crt -noout -text
→ "Check expiration" → openssl x509 -in cert.crt -noout -dates
→ "All cluster certs" → kubeadm certs check-expiration

BRANCH 5 (blue) — "Test network?"
→ "Connectivity test" → kubectl exec -- curl <service>
→ "DNS resolution" → kubectl exec -- nslookup <svc>
→ "Port check" → kubectl exec -- nc -zv <host> <port>

BRANCH 6 (navy) — "Generate YAML?"
→ "Quick pod" → kubectl run --dry-run=client -o yaml
→ "Quick deployment" → kubectl create deploy --dry-run=client -o yaml
→ "Quick service" → kubectl expose --dry-run=client -o yaml

Each leaf has the exact command in monospace.
""",
    ),
    diagram(
        "40-exam-time-management",
        "cks-40-exam-time-management.jpg",
        "The Battle Clock — CKS Exam Time Management",
        "Layer 1 — Foundational",
        "Green for early phases, Amber for middle, Red for crunch time.",
        """
Draw a CLOCK/TIMELINE showing 120 minutes divided into phases:

PHASE 1 (0-5 min) — "RECONNAISSANCE" (green, scout icon):
- Read ALL questions quickly
- Mark difficulty: Easy / Medium / Hard
- Note which clusters each question uses
- Caption: "5 minutes of planning saves 15 minutes of mistakes"

PHASE 2 (5-50 min) — "QUICK VICTORIES" (green, sword icon):
- Tackle all Easy questions first (~3-4 min each)
- Expected: 6-8 questions completed
- Types: generate YAML, apply labels, create NetworkPolicy,
  create RBAC, enable admission plugin
- Caption: "Build confidence, secure base score"

PHASE 3 (50-100 min) — "SIEGE WARFARE" (amber, shield icon):
- Medium-difficulty questions (~6-8 min each)
- Expected: 5-7 questions completed
- Types: Fix securityContext, configure audit policy,
  set up encryption at rest, Falco rules
- Caption: "Core CKS skills — where most points are"

PHASE 4 (100-115 min) — "HARD TARGETS" (red, castle icon):
- Attempt Hard questions if time allows
- Skip if stuck > 10 minutes
- Types: Complex multi-step, debug broken API server,
  incident response scenarios
- Caption: "Only attempt with solid base score"

PHASE 5 (115-120 min) — "FINAL SWEEP" (teal, checkmark icon):
- Review flagged questions
- Verify context switches
- Check all answers saved
- Caption: "Never leave a question blank — partial credit exists"

CENTER — "Rules of Engagement":
- Each question shows point value — prioritize high-value
- Context switch: ALWAYS run kubectl config use-context first
- Stuck > 5 min: Flag it, move on, come back
- 67% to pass = you can afford to miss ~33%

BOTTOM — Time-per-question guide:
Easy: 3-4 min | Medium: 6-8 min | Hard: 10-12 min
""",
    ),
    diagram(
        "41-doc-navigation",
        "cks-41-documentation-navigation-map.jpg",
        "The Library Map — Exam Documentation Navigation",
        "Layer 1 — Foundational",
        "All domain colors for topic areas, green for bookmarks.",
        """
Draw a LIBRARY MAP showing which documentation pages to bookmark:

HEADER: "Allowed Documentation During CKS Exam"
kubernetes.io/docs + kubernetes.io/blog + github.com/kubernetes
+ Falco docs + Cilium docs + Istio docs (if relevant)

BOOKMARKS organized by domain (color-coded shelves):

SHELF 1 — "Pod Security" (green):
📖 /docs/concepts/security/pod-security-standards/
   "PSA levels: privileged, baseline, restricted"
📖 /docs/tasks/configure-pod-container/security-context/
   "securityContext field reference"
📖 /docs/tutorials/security/seccomp/
   "Seccomp profile setup"
📖 /docs/tutorials/security/apparmor/
   "AppArmor profiles"

SHELF 2 — "RBAC" (purple):
📖 /docs/reference/access-authn-authz/rbac/
   "Role, ClusterRole, Binding reference"
📖 /docs/reference/access-authn-authz/authentication/
   "Authentication methods"

SHELF 3 — "Network" (blue):
📖 /docs/concepts/services-networking/network-policies/
   "NetworkPolicy spec and examples"
📖 /docs/tasks/administer-cluster/declare-network-policy/
   "Step-by-step NetworkPolicy"

SHELF 4 — "Admission & Supply Chain" (amber):
📖 /docs/reference/access-authn-authz/admission-controllers/
   "All admission plugins"
📖 /docs/reference/access-authn-authz/validating-admission-policy/
   "CEL-based ValidatingAdmissionPolicy"

SHELF 5 — "Encryption & Audit" (navy):
📖 /docs/tasks/administer-cluster/encrypt-data/
   "EncryptionConfiguration"
📖 /docs/tasks/debug/debug-cluster/audit/
   "Audit policy configuration"

SHELF 6 — "Falco" (teal):
📖 falco.org/docs/rules/
   "Falco rules reference"

BOTTOM — "Search Tips":
1. Use site search: "securityContext site:kubernetes.io"
2. Navigate via sidebar, not search (faster)
3. YAML examples in docs are copy-paste ready
4. Bookmark these URLs BEFORE exam day
""",
    ),
]

DIAGRAMS_BY_KEY = {d["key"]: d for d in DIAGRAMS}


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
