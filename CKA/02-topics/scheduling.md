# Scheduling (Workloads & Scheduling — 15%, Priority P1)

![Scheduling — The Matchmaker & the Bouncers](../images/cka-09-scheduling-matchmaking.jpg)

*Scope note: this domain sits under the official curriculum bullet "Configure Pod admission and
scheduling (limits, node affinity, etc.)" — Workloads & Scheduling 15%, confirmed Medium
difficulty/time-cost/failure-risk per the priority matrix in `01-exam-snapshot-and-priorities.md`.
You already know these concepts cold from CKAD-adjacent experience; the gap is exact YAML field
names and the admin-flavored troubleshooting angle (a Pending pod is also a Troubleshooting-domain
symptom, so this overlaps the 30% domain too). All syntax below is stable API (GA since well
before v1.20) and unchanged for the v1.35 target — nothing here is version-sensitive.*

---

## Part A — Rapid Knowledge Refresh

### Labels and Selectors

Labels are arbitrary key/value pairs attached to any object (most relevantly Nodes and Pods here)
and are the substrate every scheduling mechanism in this file is built on — nodeSelector, node
affinity, and pod affinity/anti-affinity all resolve down to label matching against either node
labels or pod labels. Selectors come in two flavors: **equality-based** (`key=value`,
`key!=value`) used by `nodeSelector` and `matchLabels`, and **set-based**
(`In`, `NotIn`, `Exists`, `DoesNotExist`) used by `matchExpressions` inside affinity rules. Nodes
get labels automatically from kubelet (e.g. `kubernetes.io/hostname`,
`kubernetes.io/os`, `kubernetes.io/arch`) plus whatever you add manually. Know the difference
between a **label** (identifying metadata, used for selection) and an **annotation**
(non-identifying metadata, never used for selection) — this trips people up under time pressure.

#### Important objects
Nodes, Pods (labels live in `metadata.labels` on both).

#### Important YAML fields
`metadata.labels: {key: value}`

#### Important commands
```bash
kubectl label nodes node01 disktype=ssd
kubectl label nodes node01 disktype=ssd --overwrite   # required to change an existing label
kubectl label nodes node01 disktype-                  # trailing dash removes a label
kubectl get nodes --show-labels
kubectl get nodes -l disktype=ssd
kubectl get pods -l app=frontend,tier!=cache
```

#### How to verify
`kubectl get nodes --show-labels` or `kubectl describe node node01 | grep -A5 Labels`.

#### Common exam mistake
Forgetting `--overwrite` when a label key already exists (the command errors out silently-ish —
you'll see "L already has a value..."); forgetting the trailing `-` (no space before it) removes
a label — `disktype -` (with a space) is parsed as a new positional arg and fails.

#### One mini exercise
Label `node01` with `env=staging`, then list only pods with `app=web` scheduled anywhere, in one
`-l` expression combining both an equality and an `In`-style multi-value match
(`-l 'app in (web,api)'`).

---

### nodeSelector

The simplest scheduling constraint: a flat map on the Pod spec that the scheduler treats as a hard
requirement — the pod will only be placed on a node whose labels are a superset of
`nodeSelector`. No operators, no weighting, no soft preference — it's an AND of equality matches.
Good for simple cases ("must run on SSD nodes"); node affinity supersedes it for anything needing
`NotIn`, `Exists`, or a preference instead of a hard requirement. If no node matches, the pod
stays `Pending` indefinitely.

#### Important objects
Pod / Pod template (Deployment, ReplicaSet, DaemonSet, Job spec.template).

#### Important YAML fields
`spec.nodeSelector: {key: value, ...}`

#### Important commands
```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml   # then edit in nodeSelector
```

#### How to verify
```bash
kubectl get pod nginx -o wide          # check NODE column matches expectation
kubectl describe pod nginx             # Events show FailedScheduling if no node matched
```

#### Common exam mistake
Typo'ing the label key/value (case-sensitive, exact string match) and then wasting time
debugging affinity logic when the real bug is a mismatched label — always
`kubectl get nodes --show-labels` first to confirm the label actually exists as spelled.

#### One mini exercise
Create a pod that must land on a node labeled `disktype=ssd` using `nodeSelector`; if no node has
that label yet, add it, then confirm the pod schedules there.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-pod
spec:
  nodeSelector:
    disktype: ssd
  containers:
  - name: nginx
    image: nginx
```

---

### Node Affinity

Node affinity is `nodeSelector`'s expressive superset: `matchExpressions` support `In`, `NotIn`,
`Exists`, `DoesNotExist`, `Gt`, `Lt`, and — critically — it distinguishes **hard** requirements
(`requiredDuringSchedulingIgnoredDuringExecution`) from **soft** preferences
(`preferredDuringSchedulingIgnoredDuringExecution`, weighted 1–100). "IgnoredDuringExecution"
means the constraint is only checked at schedule time — if node labels change after the pod is
already running, the pod is **not** evicted (there's no `RequiredDuringExecution` variant in the
stable API). Multiple `nodeSelectorTerms` are OR'd together; multiple `matchExpressions` inside
one term are AND'd together — this nesting is the single most common source of exam-time
confusion.

#### Important objects
Pod / Pod template — `spec.affinity.nodeAffinity`.

#### Important YAML fields
```
spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[].matchExpressions[].{key,operator,values}
spec.affinity.nodeAffinity.preferredDuringSchedulingIgnoredDuringExecution[].{weight,preference.matchExpressions}
```

#### Important commands
No dedicated `kubectl` verb — always via YAML (`kubectl explain pod.spec.affinity.nodeAffinity`
for field lookup mid-exam).

#### How to verify
```bash
kubectl get pod <name> -o wide
kubectl describe pod <name>        # Events: FailedScheduling + reason if no node satisfies "required"
```

#### Common exam mistake
Using `required...` when the task says "prefer" (or vice versa) — read the task wording
carefully; also forgetting that `preferred` never blocks scheduling, so a pod landing on an
"undesired" node with a preferred rule is *correct behavior*, not a bug.

#### One mini exercise
Write a pod spec requiring `topology.kubernetes.io/zone In [zone-a, zone-b]` and preferring
(weight 80) `disktype=ssd`. Confirm via `kubectl explain` that you got the nesting right before
applying.

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: topology.kubernetes.io/zone
          operator: In
          values: [zone-a, zone-b]
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 80
      preference:
        matchExpressions:
        - key: disktype
          operator: In
          values: [ssd]
```

---

### Pod Affinity / Anti-Affinity

Same required/preferred + weight structure as node affinity, but the match target is **other
pods' labels** (via `labelSelector`), scoped to a failure domain via `topologyKey` (commonly
`kubernetes.io/hostname` for per-node, `topology.kubernetes.io/zone` for per-zone). Pod affinity
says "schedule me near pods matching X"; pod anti-affinity says "schedule me away from pods
matching X" — the canonical anti-affinity use case is spreading replicas of the same app across
nodes/zones for HA. `topologyKey` is mandatory and is the field people forget most: without it
the rule is meaningless (it defines what "near"/"away" actually measures). `namespaces` defaults
to the pod's own namespace if omitted — set it explicitly when matching across namespaces.

#### Important objects
Pod / Pod template — `spec.affinity.podAffinity` / `spec.affinity.podAntiAffinity`.

#### Important YAML fields
```
spec.affinity.podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution[].{labelSelector,topologyKey,namespaces}
spec.affinity.podAffinity.preferredDuringSchedulingIgnoredDuringExecution[].{weight,podAffinityTerm.{labelSelector,topologyKey}}
```

#### Important commands
`kubectl explain pod.spec.affinity.podAntiAffinity --recursive` to get the exact nesting right
under time pressure.

#### How to verify
```bash
kubectl get pods -o wide          # confirm no two match on the same NODE (hard anti-affinity + hostname topologyKey)
kubectl describe pod <name>       # FailedScheduling if required anti-affinity can't be satisfied
```

#### Common exam mistake
Forgetting `topologyKey`; using `matchLabels` with the wrong key (must match an actual label on
the *target* pods, not the pod being scheduled); expecting a required anti-affinity rule to work
with fewer nodes than replicas — it will correctly leave excess pods `Pending`, that's not a bug
to fix by relaxing anything except the task's own requirement.

#### One mini exercise
Write a Deployment with 3 replicas using required pod anti-affinity on `app: web` with
`topologyKey: kubernetes.io/hostname` on a 3-node cluster; verify each replica lands on a
different node. Then scale to 4 and observe the 4th pod stay `Pending`.

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: web
      topologyKey: kubernetes.io/hostname
```

---

### Taints and Tolerations

Taints go on **nodes** and repel pods; tolerations go on **pods** and let them (but don't force
them to) land on tainted nodes — this is the inverse relationship of affinity (affinity is a pod
pulling itself toward nodes; taints are a node pushing pods away). Three effects:
`NoSchedule` (won't schedule new pods, existing ones stay), `PreferNoSchedule` (soft, best-effort
avoid), and `NoExecute` (evicts already-running pods that don't tolerate it, and blocks new ones —
`tolerationSeconds` lets a toleration delay that eviction rather than tolerate it forever).
Control-plane nodes are tainted `node-role.kubernetes.io/control-plane:NoSchedule` by kubeadm by
default — this is *why* workloads don't land on control-plane nodes, not a scheduler default
behavior. Tolerating a taint never guarantees placement there; combine with node affinity if you
need pods to *only* run on a specific tainted node.

#### Important objects
Node (taint), Pod / Pod template (toleration).

#### Important YAML fields
```
spec.tolerations[].{key,operator,value,effect,tolerationSeconds}
```
`operator: Exists` matches any value for the given key (or all taints if `key` is also omitted);
`operator: Equal` (default) requires an exact value match.

#### Important commands
```bash
kubectl taint nodes node01 key1=value1:NoSchedule
kubectl taint nodes node01 key1=value1:NoSchedule-       # remove (note trailing dash, no value needed to remove by key+effect)
kubectl describe node node01 | grep Taints
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```

#### How to verify
`kubectl describe node <node>` (Taints line) and confirm the pod's Events don't show
`node(s) had untolerated taint`.

#### Common exam mistake
Confusing which side is which under time pressure (taint = node repels, toleration = pod
permits); using `PreferNoSchedule` when the task says a pod must never land there (needs
`NoSchedule` or `NoExecute`); forgetting `effect` is part of the taint's identity — removing a
taint requires matching key **and** effect, not just the key.

#### One mini exercise
Taint `node01` with `dedicated=gpu:NoSchedule`. Confirm a plain nginx pod does not land there
(`kubectl get pods -o wide` across several retries/scale-ups). Add a matching toleration to a new
pod and confirm it *can* land there — then add `nodeAffinity` requiring that node so it *always*
does.

---

### Manual Scheduling (`nodeName`)

Setting `spec.nodeName` directly on a Pod bypasses the scheduler entirely — the kubelet on the
named node picks it up without any scheduling decision being made at all (no taint/toleration
check, no affinity evaluation, no resource-fit check). This is the classic "scheduler is down,
schedule this pod manually" exam scenario. It's immutable once set (you cannot patch `nodeName`
on a running pod — delete and recreate). If the named node doesn't exist or lacks capacity, the
pod sits in a broken/`Pending`-like state at the kubelet level rather than being retried
elsewhere, since nothing is watching to retry it.

#### Important objects
Pod (this field does not exist on Deployment/ReplicaSet pod templates in a way that's useful —
each replica would collide trying to bind the same node/port, so this is a Pod-level trick, not a
workload-controller pattern).

#### Important YAML fields
`spec.nodeName: <node-name>`

#### Important commands
```bash
kubectl get nodes                       # confirm exact node name
kubectl explain pod.spec.nodeName
```

#### How to verify
```bash
kubectl get pod <name> -o wide          # NODE column should show the forced node immediately, no scheduling delay
kubectl get pod <name> -o jsonpath='{.spec.nodeName}'
```

#### Common exam mistake
Trying to `kubectl edit` or `kubectl patch` `nodeName` on an existing pod — the API server
rejects it ("field is immutable"); you must delete and recreate. Also: this is the *only*
mechanism in this file that has nothing to do with labels — don't waste time checking node labels
if a task says "manually schedule," it means this field.

#### One mini exercise
Create a pod with `spec.nodeName` set to a specific worker node and confirm via `-o wide` that it
lands there instantly (no `Pending` transition), even if you also taint that node
`NoSchedule` beforehand — proving the taint is ignored for `nodeName`-forced placement.

---

### Scheduler Behavior & Troubleshooting

`kube-scheduler` watches for pods with an empty `spec.nodeName`, filters nodes (taints,
affinity, resource requests, `nodeSelector`, volume constraints), then scores and binds. On a
kubeadm cluster it runs as a **static pod** from
`/etc/kubernetes/manifests/kube-scheduler.yaml` on control-plane node(s), so a totally broken
scheduler shows up as `Pending` pods cluster-wide with no scheduling events at all — check the
static pod manifest and `crictl`/kubelet logs on the control-plane node, not just
`kubectl` (if the API server itself is fine but the scheduler container is crash-looping,
`kubectl get pods -n kube-system` still works and will show you the scheduler pod's own status).
The most common exam-time "scheduling problem" isn't the scheduler being broken at all — it's a
pod correctly stuck `Pending` because no node satisfies its constraints (unmatched
label/taint/resource request), which you diagnose entirely through `kubectl describe pod`
Events, not scheduler logs.

#### Important objects
The `kube-scheduler` static pod (`kube-system` namespace), `Node` conditions, `Event` objects.

#### Important YAML fields
`/etc/kubernetes/manifests/kube-scheduler.yaml` (static pod definition — flags live here, e.g.
`--leader-elect`, `--bind-address`).

#### Important commands
```bash
kubectl get pods -n kube-system -l component=kube-scheduler
kubectl -n kube-system logs kube-scheduler-<control-plane-node-name>
kubectl describe pod <pending-pod>            # Events: FailedScheduling + human-readable reason
kubectl get events --field-selector reason=FailedScheduling --sort-by=.lastTimestamp
kubectl get nodes -o wide                     # check Ready/SchedulingDisabled (cordoned)
kubectl top nodes                             # sanity-check capacity if reason is "Insufficient cpu/memory"
```

#### How to verify
`kubectl describe pod` Events tell you *exactly* why (unmatched node selector/taint, insufficient
resources, no nodes available) — always read that message verbatim before hypothesizing.

#### Common exam mistake
Jumping straight to scheduler logs/manifest edits when the fix is really "the pod's own spec
is unsatisfiable" (typo'd label, forgotten toleration); conversely, chasing pod-spec fixes when
the real problem is the scheduler static pod itself crash-looping (check
`crictl ps -a` / `journalctl -u kubelet` on the control-plane node in that case) or the node
being cordoned (`SchedulingDisabled` in `kubectl get nodes`, from a leftover `kubectl cordon`).

#### One mini exercise
Cordon a node (`kubectl cordon node01`), then create a Deployment with 3 replicas on a 2-remaining-node
cluster whose `nodeSelector` also excludes one of those two — observe and correctly diagnose
the resulting `Pending` pod purely from `kubectl describe pod` output, then `kubectl uncordon`
and fix the selector.

---

## Part B — Task Patterns

### Pattern A — Force a Pod (or workload) onto a specific node

#### Skill tested
`nodeSelector` and node affinity as the primary "constrain placement" mechanisms.

#### What the task usually looks like
"Create a pod/deployment named X using image Y that must only run on node(s) with label
`key=value`" — sometimes phrased as "must run," sometimes "should preferably run" (required vs.
preferred), and sometimes the label doesn't exist yet and you must add it first.

#### Commands I need
```bash
kubectl get nodes --show-labels
kubectl label nodes <node> <key>=<value>
kubectl run <name> --image=<image> --dry-run=client -o yaml > pod.yaml
# edit in nodeSelector or affinity block
kubectl apply -f pod.yaml
kubectl get pod <name> -o wide
```

#### Files/directories commonly involved
A single pod/deployment YAML you generate with `--dry-run=client -o yaml`, then hand-edit.

#### Kubernetes documentation page worth knowing
"Assign Pods to Nodes" and "Assign Pods to Nodes using Node Affinity" under
Concepts → Scheduling, Preemption and Eviction.

#### Common mistakes
Editing the wrong indentation level (`nodeSelector` is a sibling of `containers`, not nested
inside it); forgetting the label doesn't pre-exist and needing to create it first; using
`nodeName` when the task actually wants scheduler-mediated placement (nodeName skips fit checks
entirely, which matters if the task later checks resource-based scoring).

#### Fastest solution strategy
Generate the base YAML with `--dry-run=client -o yaml`, redirect to a file, then insert
`nodeSelector` (fastest, use it unless the task explicitly needs `In`/`NotIn`/`Exists` semantics
or a soft preference — then go straight to `affinity.nodeAffinity`).

#### Typical troubleshooting variation
Task says the pod "isn't landing where expected" — diagnose via `kubectl describe pod` Events
(look for `node(s) didn't match Pod's node affinity/selector`) and `kubectl get nodes
--show-labels` to spot a label typo or case mismatch.

#### Estimated time target
3–4 minutes for a straightforward nodeSelector task; 5–6 minutes if it requires node affinity
with multiple `matchExpressions`.

#### Original practice task
*(Original exercise, not reproduced from any real exam.)*

**Solve:** On a cluster with at least 2 worker nodes, label one node `env=prod`. Create a
Deployment `billing` (image `nginx`, 2 replicas) that must run only on nodes labeled `env=prod`,
using node affinity with `operator: In`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: billing
spec:
  replicas: 2
  selector:
    matchLabels: {app: billing}
  template:
    metadata:
      labels: {app: billing}
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: env
                operator: In
                values: [prod]
      containers:
      - name: nginx
        image: nginx
```

**Verify:**
```bash
kubectl get pods -l app=billing -o wide      # both pods' NODE column = the env=prod node
kubectl get pods -l app=billing -o jsonpath='{.items[*].spec.nodeName}'
```

#### Hard-mode version
Repeat with only one node labeled `env=prod`, replicas raised to 3, and add a required pod
anti-affinity (`topologyKey: kubernetes.io/hostname`) on `app: billing` — correctly explain (via
`kubectl describe pod`) why only **one** replica ever schedules and the other **two** are
intentionally stuck `Pending`: node affinity restricts all 3 to the single `env=prod` node, but
anti-affinity forbids more than one `app: billing` pod per node, so the constraints leave room
for exactly one, not two.

---

### Pattern B — Taint a node and configure matching tolerations

#### Skill tested
Taints/tolerations as a repel-based (not pull-based) placement control, including the
control-plane-taint mental model.

#### What the task usually looks like
"Taint node X so that no pods are scheduled there by default, then create a pod that can
tolerate that taint and run there anyway" — or the inverse: "an existing pod won't schedule,
figure out why (a taint) and fix it."

#### Commands I need
```bash
kubectl taint nodes <node> <key>=<value>:<effect>
kubectl describe node <node> | grep Taints
kubectl taint nodes <node> <key>=<value>:<effect>-   # remove
```

#### Files/directories commonly involved
Pod/Deployment YAML for the `tolerations` block; no cluster config files needed for this pattern
specifically.

#### Kubernetes documentation page worth knowing
"Taints and Tolerations" under Concepts → Scheduling, Preemption and Eviction.

#### Common mistakes
Mismatched `effect` between taint and toleration (must match exactly, or omit `effect` in the
toleration to match any effect for that key); forgetting `operator: Exists` doesn't need/allow a
meaningful `value` field; assuming a toleration alone forces placement (it only permits — pair
with affinity if the task wants exclusivity).

#### Fastest solution strategy
Taint first, confirm with `describe node`, then write the toleration block matching key/value/
effect exactly — copy the taint's own string to avoid transcription typos.

#### Typical troubleshooting variation
"This DaemonSet/pod isn't running on all nodes as expected" — check for a `NoSchedule` or
`NoExecute` taint that the pod's spec doesn't tolerate. Caution: the DaemonSet controller only
auto-injects tolerations for **node-condition** taints (`not-ready`, `unreachable`,
`disk-pressure`, etc.) — it does **not** auto-tolerate the built-in control-plane taint
(`node-role.kubernetes.io/control-plane:NoSchedule`). Official system DaemonSets (kube-proxy,
CNI) only run on control-plane nodes because their own manifests carry an explicit toleration for
it. So a missing toleration for the *built-in* control-plane taint is just as plausible a cause
in a deliberately broken task as a custom one — check both.

#### Estimated time target
3–5 minutes.

#### Original practice task
*(Original exercise, not reproduced from any real exam.)*

**Solve:** Taint `node01` with `workload=batch:NoSchedule`. Create a pod `batch-job`
(image `busybox`, command `sleep 3600`) with a toleration for that exact taint, and node affinity
requiring `node01` so it lands there deterministically.

```bash
kubectl taint nodes node01 workload=batch:NoSchedule
```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-job
spec:
  tolerations:
  - key: workload
    operator: Equal
    value: batch
    effect: NoSchedule
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/hostname
            operator: In
            values: [node01]
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
```

**Verify:**
```bash
kubectl get pod batch-job -o wide             # NODE = node01
kubectl run untainted-test --image=nginx --restart=Never
kubectl get pod untainted-test -o wide        # confirm it lands elsewhere, never node01
```

#### Hard-mode version
Change the taint's effect to `NoExecute` with `tolerationSeconds: 60` on a *different* already-
running pod that doesn't have node affinity to node01 — watch it get evicted after the grace
period and explain why (`NoExecute` affects already-scheduled pods, unlike `NoSchedule`).

---

### Pattern C — Diagnose a Pod stuck in `Pending` (scheduling-failure troubleshooting)

#### Skill tested
Reading scheduling failure signals end-to-end — this is where Scheduling (15%) and
Troubleshooting (30%) overlap, so it's disproportionately high-value to drill.

#### What the task usually looks like
A pod or deployment is given to you already `Pending` (possibly pre-broken by the exam setup
script) with no explanation — "this deployment isn't running, fix it" — and the root cause is
one of: unmatched nodeSelector/affinity, untolerated taint, insufficient resource
requests vs. node capacity, a cordoned node, or (rarer) the scheduler pod itself down.

#### Commands I need
```bash
kubectl get pods -o wide
kubectl describe pod <pending-pod>                 # read Events bottom-to-top, verbatim
kubectl get nodes                                  # check Ready + SchedulingDisabled
kubectl describe node <node> | grep -A5 Taints
kubectl get nodes --show-labels
kubectl top nodes                                  # resource-fit reasons
kubectl get pods -n kube-system -l component=kube-scheduler
```

#### Files/directories commonly involved
No files usually — this is a read/diagnose/patch-the-pod-spec task, not a config-file task,
unless the scheduler itself is broken (`/etc/kubernetes/manifests/kube-scheduler.yaml`).

#### Kubernetes documentation page worth knowing
"Troubleshooting" hub → "Debug Pods" page; also re-check "Assign Pods to Nodes" for the exact
selector/affinity semantics you're likely misreading under pressure.

#### Common mistakes
Only reading the Status/Conditions section of `describe pod` and skipping the Events at the
bottom, which contain the actual `FailedScheduling` reason string; assuming `Pending` always
means scheduler-down when 95% of the time it's an unsatisfiable pod spec.

#### Fastest solution strategy
`kubectl describe pod` first, always — the Events message is nearly verbatim the fix you need
("0/3 nodes are available: 1 node(s) had untolerated taint..., 2 node(s) didn't match Pod's node
affinity/selector"). Cross-reference against `get nodes --show-labels` /
`describe node | grep Taints` only to confirm, not to blind-guess.

#### Typical troubleshooting variation
Multiple stacked causes in one task (e.g., correct nodeSelector but the only matching node is
also cordoned) — fix one, re-describe, and check if a *new* reason appears before declaring
done.

#### Estimated time target
4–6 minutes including verification.

#### Original practice task
*(Original exercise, not reproduced from any real exam.)*

**Solve:** Given a pre-existing `Pending` pod with `nodeSelector: {disktype: ssd}` where no node
carries that label, and a node named `node02` that is also cordoned — diagnose using
`kubectl describe pod`, then either label a suitable node `disktype=ssd` and uncordon it, or
retarget the selector to an existing labeled/schedulable node.

```bash
kubectl describe pod <pod-name>          # confirms: didn't match node selector + SchedulingDisabled
kubectl get nodes --show-labels
kubectl uncordon node02
kubectl label nodes node02 disktype=ssd
```

**Verify:**
```bash
kubectl get pod <pod-name> -o wide       # STATUS=Running, NODE=node02
kubectl get nodes                        # node02 no longer SchedulingDisabled
```

#### Hard-mode version
Same setup, but the scheduler's own static pod manifest has a deliberately broken flag (e.g. a
typo'd `--bind-address`) causing it to crash-loop cluster-wide — first prove via
`kubectl get pods -n kube-system` / `crictl ps -a` on the control-plane node that *no* pods are
being scheduled anywhere (not just this one), fix the manifest, confirm kubelet picks up the
static pod change automatically, then re-verify the original pod schedules.

---

### Pattern D — Spread replicas for HA using pod anti-affinity

#### Skill tested
Required pod anti-affinity with `topologyKey` to guarantee no two replicas share a failure
domain — a realistic "make this Deployment resilient to a node loss" framing.

#### What the task usually looks like
"Modify Deployment X so that no two of its pods ever run on the same node" (or "same zone," using
a zone label as `topologyKey`).

#### Commands I need
```bash
kubectl edit deployment <name>            # or patch the manifest and re-apply
kubectl get pods -l app=<name> -o wide
```

#### Files/directories commonly involved
The Deployment manifest's `spec.template.spec.affinity.podAntiAffinity` block.

#### Kubernetes documentation page worth knowing
"Assign Pods to Nodes using Node Affinity" page's pod affinity/anti-affinity section (same page
as node affinity in current docs), plus "Pod Topology Spread Constraints" as the related-but-
distinct alternative mechanism worth recognizing by name even if not the primary ask.

#### Common mistakes
Using `preferred` when the task says "must never" (needs `required`); matching the wrong label
in `labelSelector` (must match the *pod template's own* labels, e.g. `app: web`, not some
unrelated key); omitting `topologyKey` entirely.

#### Fastest solution strategy
`kubectl edit deployment` in place for a quick patch during the exam (faster than
export-edit-reapply for a single nested field), inserting the `podAntiAffinity` block under
`spec.template.spec.affinity`.

#### Typical troubleshooting variation
"Deployment X won't scale past N replicas" where N = node count — correctly identify this as
expected behavior of required anti-affinity plus insufficient nodes, not a bug, and either scale
down, add nodes, or switch to `preferred` per the task's actual intent.

#### Estimated time target
4–5 minutes.

#### Original practice task
*(Original exercise, not reproduced from any real exam.)*

**Solve:** Given a 3-node cluster and an existing Deployment `web` (3 replicas, label
`app: web`), patch it so no two `web` pods ever share a node.

```bash
kubectl patch deployment web --type merge -p '{
  "spec": {"template": {"spec": {"affinity": {"podAntiAffinity": {
    "requiredDuringSchedulingIgnoredDuringExecution": [{
      "labelSelector": {"matchLabels": {"app": "web"}},
      "topologyKey": "kubernetes.io/hostname"
    }]
  }}}}}
}'
```

**Verify:**
```bash
kubectl get pods -l app=web -o wide
kubectl get pods -l app=web -o jsonpath='{.items[*].spec.nodeName}' | tr ' ' '\n' | sort -u
# unique node count should equal replica count (3)
```

#### Hard-mode version
Scale to 4 replicas on the same 3-node cluster and, instead of accepting a `Pending` 4th pod,
correctly convert the rule to `preferredDuringSchedulingIgnoredDuringExecution` (weight 100) so
all 4 run with best-effort spreading rather than one stuck forever — demonstrating you understand
required vs. preferred is a deliberate trade-off, not just a syntax choice.
