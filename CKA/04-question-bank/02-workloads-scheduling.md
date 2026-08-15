# Question Bank — Workloads & Scheduling (15%)

*25 original, hands-on drills covering Deployments/ReplicaSets/DaemonSets/StatefulSets/Jobs/CronJobs,
rolling updates & rollback, probes, init containers, resource requests/limits, node/pod affinity &
anti-affinity, taints/tolerations, priority classes, and workload autoscaling — built from the
competencies in `01-exam-snapshot-and-priorities.md` and `02-topics/{workloads,scheduling}.md`, not
from any remembered real exam question.*

**Priority weighting rationale:** per the priority matrix, this domain's own line items
("Workloads core objects" and "Advanced scheduling") sit at **P2** and **P1** respectively — you
already have most of this cold from CKAD, so the domain-internal skew favors P1 (taints/affinity/
resources/priority-classes/HPA — the genuinely CKA-flavored, less-drilled half) over P2 (Deployments/
DaemonSets/Jobs/etc. — CKAD-mastered refresh). A handful of questions are tagged **P0**: these are
pod-scheduling and pod-lifecycle *diagnosis* drills that both topic files explicitly call out as the
highest-value overlap with the 30%-weighted Troubleshooting domain — disproportionately worth
drilling even though they technically live under a 15% domain. Difficulty and target time are this
document's own estimate, calibrated for a CKAD-certified, CKA-rusty candidate.

**Setup convention:** because this is self-study (no proctor pre-breaks a cluster for you), each
"Solve" block includes the commands to *create* the broken/starting scenario as well as the fix —
read only the **Task** line before attempting, then use the Solve block's setup commands to
reproduce the scenario yourself if you want a second attempt later.

---

### Question 1 — Pending Pods Behind an Untolerated Taint
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Deployment `orders` in namespace `retail` is supposed to run 3/3 replicas but `kubectl get pods -n retail` shows only 1 Running and 2 Pending. A teammate tainted one of your worker nodes earlier today for a batch-only initiative. Without removing that taint, get all 3 replicas to `Running`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create ns retail
kubectl create deployment orders -n retail --image=nginx --replicas=3
# reproduce the scenario: taint a node the scheduler would otherwise use
kubectl taint nodes node02 dedicated=batch:NoSchedule

# diagnose
kubectl get pods -n retail -o wide
kubectl describe pod -n retail -l app=orders | grep -A5 Events
# Events: "0/2 nodes are available: 1 node(s) had untolerated taint {dedicated: batch}..."

# fix: add a matching toleration to the pod template
kubectl patch deployment orders -n retail --type=json -p '[
  {"op":"add","path":"/spec/template/spec/tolerations","value":[
    {"key":"dedicated","operator":"Equal","value":"batch","effect":"NoSchedule"}
  ]}
]'
```

**Verify:**
```bash
kubectl get pods -n retail -o wide                 # 3/3 Running, one possibly on node02
kubectl describe pod -n retail -l app=orders | grep -i "untolerated"   # no matches
```

**Common mistake:** adding a toleration with the wrong `effect` (taints are identified by key **and**
effect together) or leaving `operator` unset while also leaving `value` blank — `operator: Equal`
(the default) requires an exact `value` match; use `operator: Exists` only if you genuinely want to
match the key regardless of value.

</details>

---

### Question 2 — Pending Pod: Resource Request Too Large for Any Node
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Pod `cache-warmup` in namespace `retail` never leaves `Pending`. Diagnose the root cause from Events and fix the manifest so it schedules, while still keeping sane, explicit resource requests and limits (don't just delete the `resources` block).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: cache-warmup
  namespace: retail
spec:
  containers:
  - name: warmup
    image: redis
    resources:
      requests:
        memory: "32Gi"
        cpu: "500m"
      limits:
        memory: "32Gi"
        cpu: "1"
EOF

kubectl describe pod cache-warmup -n retail | tail -10
# Events: "0/2 nodes are available: 2 Insufficient memory"

kubectl delete pod cache-warmup -n retail
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: cache-warmup
  namespace: retail
spec:
  containers:
  - name: warmup
    image: redis
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "500m"
EOF
```

**Verify:**
```bash
kubectl get pod cache-warmup -n retail            # Running, 1/1
kubectl get pod cache-warmup -n retail -o jsonpath='{.spec.containers[0].resources}'
```

**Common mistake:** lowering `limits` instead of `requests` — the scheduler only ever looks at
`requests` for the fit check, so a huge `limits` value with a small `requests` value schedules fine
(and is a legitimate "Burstable" pattern); it's specifically an oversized `requests` that leaves a pod
`Pending` forever.

</details>

---

### Question 3 — Stacked Causes: Cordoned Node Plus a Mismatched Selector
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** Deployment `search` in namespace `retail` (2 replicas, image `nginx`) has both pods stuck `Pending`. There are exactly two worker nodes in the cluster. Diagnose and resolve — but don't stop at the first fix; re-check whether a *second*, independent cause is still blocking scheduling before declaring success.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# reproduce: cordon one node, and require a label that exists on neither
kubectl cordon node01
kubectl create deployment search -n retail --image=nginx --replicas=2
kubectl patch deployment search -n retail --type=json -p '[
  {"op":"add","path":"/spec/template/spec/nodeSelector","value":{"tier":"search"}}
]'

# diagnose — round 1
kubectl describe pod -n retail -l app=search | grep -A5 Events
# "0/2 nodes are available: 1 node(s) had untolerated taint {node.kubernetes.io/unschedulable: },
#  2 node(s) didn't match Pod's node affinity/selector."

# fix cause #1: the missing label
kubectl label nodes node02 tier=search

# re-check — a NEW pod may schedule on node02, but if replicas > available nodes, the cordon on
# node01 still blocks the second one
kubectl describe pod -n retail -l app=search | grep -A5 Events

# fix cause #2: uncordon
kubectl uncordon node01
kubectl label nodes node01 tier=search
```

**Verify:**
```bash
kubectl get pods -n retail -l app=search -o wide   # 2/2 Running
kubectl get nodes                                  # neither node shows SchedulingDisabled
```

**Common mistake:** fixing the label mismatch, seeing one pod turn `Running`, and closing the task
while the second pod is still `Pending` for the *other* reason (the cordon) — always re-run
`kubectl describe pod` after each fix rather than assuming one Event message was the whole story.

</details>

---

### Question 4 — CrashLoopBackOff Caused by a Misconfigured Liveness Probe
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** Deployment `web-cache` in namespace `retail` shows climbing `RESTARTS` and Pods cycling through `CrashLoopBackOff`. Determine whether this is an application bug or a probe misconfiguration, and fix it — without changing the container image.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-cache
  namespace: retail
spec:
  replicas: 1
  selector:
    matchLabels: {app: web-cache}
  template:
    metadata:
      labels: {app: web-cache}
    spec:
      containers:
      - name: nginx
        image: nginx
        livenessProbe:
          httpGet:
            path: /healthz     # nginx doesn't serve this path by default -> always 404
            port: 80
          initialDelaySeconds: 2
          periodSeconds: 3
          failureThreshold: 2
EOF

kubectl describe pod -n retail -l app=web-cache | grep -A5 Events
# Events: repeated "Liveness probe failed: HTTP probe failed with statuscode: 404" -> container killed

# fix: point the probe at a path the image actually serves (or add a startupProbe if slow-starting)
kubectl patch deployment web-cache -n retail --type=json -p '[
  {"op":"replace","path":"/spec/template/spec/containers/0/livenessProbe/httpGet/path","value":"/"}
]'
```

**Verify:**
```bash
kubectl get pods -n retail -l app=web-cache -w   # RESTARTS stops climbing, watch for ~30s then Ctrl+C
kubectl describe pod -n retail -l app=web-cache | grep -i unhealthy   # no recent occurrences
```

**Common mistake:** assuming any `CrashLoopBackOff` means the application itself is broken and going
straight to `kubectl logs` — a liveness-probe-induced restart often shows a perfectly healthy
application log with no error, because the *kubelet* killed the container, not the app itself. Always
check `kubectl describe pod` Events for `Liveness probe failed` / `Unhealthy` before touching the app.

</details>

---

### Question 5 — Same Symptom Class, Opposite Fix: Pending vs. OOMKilled
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** You're given two broken pods, `ledger-a` and `ledger-b`, both "not working." Diagnose each independently from its Events/status (don't assume they share a root cause) and apply the correct, distinct fix to each.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ledger-a
  namespace: retail
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests: {memory: "16Gi"}   # far more than any node has -> stuck Pending
---
apiVersion: v1
kind: Pod
metadata:
  name: ledger-b
  namespace: retail
spec:
  containers:
  - name: app
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "150M", "--vm-hang", "1"]
    resources:
      requests: {memory: "20Mi"}
      limits: {memory: "50Mi"}   # app allocates more than this -> OOMKilled
EOF

# diagnose ledger-a
kubectl describe pod ledger-a -n retail | grep -A3 Events    # "Insufficient memory"
# diagnose ledger-b
kubectl get pod ledger-b -n retail -o jsonpath='{.status.containerStatuses[0].lastState}'  # reason: OOMKilled

# fix ledger-a: lower the request to something realistic
# (Pod fields other than a narrow allow-list are immutable, and `kubectl run` has no
# --requests/--limits flags in current kubectl — delete and re-apply with a smaller request instead)
kubectl delete pod ledger-a -n retail
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ledger-a
  namespace: retail
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests: {memory: "64Mi"}
      limits: {memory: "128Mi"}
EOF

# fix ledger-b: raise the limit above actual usage
kubectl delete pod ledger-b -n retail
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ledger-b
  namespace: retail
spec:
  containers:
  - name: app
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "150M", "--vm-hang", "1"]
    resources:
      requests: {memory: "20Mi"}
      limits: {memory: "200Mi"}
EOF
```

**Verify:**
```bash
kubectl get pod ledger-a -n retail             # Running
kubectl get pod ledger-b -n retail -o jsonpath='{.status.containerStatuses[0].restartCount}'  # stable, not climbing
```

**Common mistake:** treating both as "a resources problem" and editing the same field on both —
`Pending` is a **scheduling-time** problem fixed via `requests`; `OOMKilled` is a **runtime**
problem fixed via `limits`. Editing the wrong field on either leaves the real symptom unchanged.

</details>

---

### Question 6 — Force `Guaranteed` QoS Class
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create a Pod `billing-api` in namespace `retail`, image `nginx`, configured so its QoS class is exactly `Guaranteed`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: billing-api
  namespace: retail
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "250m"
        memory: "256Mi"
      limits:
        cpu: "250m"
        memory: "256Mi"
EOF
```

**Verify:**
```bash
kubectl get pod billing-api -n retail -o jsonpath='{.status.qosClass}'   # Guaranteed
```

**Common mistake:** setting matching `requests`/`limits` for only one resource (e.g. CPU) and leaving
memory unset or mismatched — `Guaranteed` requires **every** resource on **every** container to have
`requests == limits`; a single unset or mismatched field silently downgrades the whole Pod to
`Burstable`.

</details>

---

### Question 7 — Hard-Constrain Placement with `nodeSelector`
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Label exactly one worker node `storage=nvme`. Create Deployment `ledger` (image `nginx`, 2 replicas) that must run only on nodes carrying that label, using `nodeSelector`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl label nodes node01 storage=nvme

kubectl create deployment ledger -n retail --image=nginx --replicas=2 --dry-run=client -o yaml > ledger.yaml
# edit ledger.yaml: add spec.template.spec.nodeSelector: {storage: nvme}  (sibling of containers, not nested inside it)
kubectl apply -f ledger.yaml
```

**Verify:**
```bash
kubectl get pods -n retail -l app=ledger -o wide      # NODE column = node01 for both
kubectl get pods -n retail -l app=ledger -o jsonpath='{.items[*].spec.nodeName}'
```

**Common mistake:** indenting `nodeSelector` as a child of `containers` instead of a sibling under
`spec.template.spec` — this either fails schema validation or silently does nothing, depending on
exactly where it lands.

</details>

---

### Question 8 — Node Affinity: Required *and* Preferred Together
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Deployment `analytics` (namespace `retail`, image `nginx`, 2 replicas) must **only** run on nodes labeled `zone=zone-a`, and should **preferably** (weight 60) land on nodes additionally labeled `tier=compute` — but a lack of `tier=compute` nodes must never block scheduling.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl label nodes node01 zone=zone-a
kubectl label nodes node01 tier=compute
kubectl label nodes node02 zone=zone-a

cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics
  namespace: retail
spec:
  replicas: 2
  selector:
    matchLabels: {app: analytics}
  template:
    metadata:
      labels: {app: analytics}
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values: [zone-a]
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 60
            preference:
              matchExpressions:
              - key: tier
                operator: In
                values: [compute]
      containers:
      - name: nginx
        image: nginx
EOF
```

**Verify:**
```bash
kubectl get pods -n retail -l app=analytics -o wide      # both on zone=zone-a nodes only
kubectl describe pod -n retail -l app=analytics | grep -i FailedScheduling   # none
```

**Common mistake:** putting the `tier=compute` condition inside the `required` block "just to be
safe" — that turns a soft preference into a hard requirement, and if no node has both labels, pods
sit `Pending` for a constraint the task never asked to be mandatory.

</details>

---

### Question 9 — Node Affinity: Fix a Broken OR Across `nodeSelectorTerms`
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 7 min
**Task:** You're handed the affinity block below, intended to mean *"schedule on a node that is either (zone=zone-a AND disktype=ssd), OR (zone=zone-b), regardless of disk type"* — but it's wrong and pods sit `Pending` even though nodes satisfying the second condition exist. Find the structural bug and fix it.

```yaml
requiredDuringSchedulingIgnoredDuringExecution:
  nodeSelectorTerms:
  - matchExpressions:
    - key: zone
      operator: In
      values: [zone-a, zone-b]
    - key: disktype
      operator: In
      values: [ssd]
```

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Bug: everything is inside ONE nodeSelectorTerm, so both matchExpressions are AND'd together —
# this actually means "(zone in [zone-a,zone-b]) AND (disktype=ssd)", not the intended OR-of-cases.
# Fix: split into two separate nodeSelectorTerms (terms are OR'd; expressions within a term are AND'd).

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: mixed-placement
  namespace: retail
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: zone
            operator: In
            values: [zone-a]
          - key: disktype
            operator: In
            values: [ssd]
        - matchExpressions:
          - key: zone
            operator: In
            values: [zone-b]
  containers:
  - name: nginx
    image: nginx
EOF
```

**Verify:**
```bash
kubectl explain pod.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms --recursive | head -20
kubectl get pod mixed-placement -n retail -o wide     # lands on any zone-b node, or a zone-a+ssd node
```

**Common mistake:** treating `matchExpressions` inside a single term as if they were OR'd (like a
flat list of "acceptable conditions") — they are always AND'd. OR only happens **across** separate
entries in `nodeSelectorTerms`. This exact nesting confusion is called out in official docs as the
single most common node-affinity mistake.

</details>

---

### Question 10 — Pod Anti-Affinity for HA Spread, Including the Expected Pending Case
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** On a 3-node cluster, patch existing Deployment `sessions` (3 replicas, label `app=sessions`) so that no two of its Pods ever land on the same node. Then scale to 4 and correctly explain (don't "fix") the result.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create deployment sessions -n retail --image=nginx --replicas=3

kubectl patch deployment sessions -n retail --type=merge -p '{
  "spec": {"template": {"spec": {"affinity": {"podAntiAffinity": {
    "requiredDuringSchedulingIgnoredDuringExecution": [{
      "labelSelector": {"matchLabels": {"app": "sessions"}},
      "topologyKey": "kubernetes.io/hostname"
    }]
  }}}}}
}'

kubectl scale deployment sessions -n retail --replicas=4
```

**Verify:**
```bash
kubectl get pods -n retail -l app=sessions -o wide
kubectl get pods -n retail -l app=sessions -o jsonpath='{.items[*].spec.nodeName}' | tr ' ' '\n' | sort -u
# exactly 3 unique nodes for the 3 Running pods; the 4th pod stays Pending — this is correct, not a bug
```

**Common mistake:** treating the 4th Pod's `Pending` state as something to "fix" by relaxing the
rule without being asked to — a required anti-affinity rule with fewer nodes than replicas
*correctly* leaves the excess Pod unscheduled; changing that changes the guarantee the task asked
for.

</details>

---

### Question 11 — Pod Affinity: Co-locate by Zone
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Deployment `frontend` (label `app=frontend`) already exists and is running. Create Deployment `edge-cache` (image `redis`, 2 replicas) whose Pods must run in the **same zone** as `frontend` Pods (not necessarily the same node), using required pod affinity.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl label nodes node01 topology.kubernetes.io/zone=zone-a --overwrite
kubectl label nodes node02 topology.kubernetes.io/zone=zone-a --overwrite
kubectl create deployment frontend -n retail --image=nginx --replicas=2

cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-cache
  namespace: retail
spec:
  replicas: 2
  selector:
    matchLabels: {app: edge-cache}
  template:
    metadata:
      labels: {app: edge-cache}
    spec:
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels: {app: frontend}
            topologyKey: topology.kubernetes.io/zone
      containers:
      - name: redis
        image: redis
EOF
```

**Verify:**
```bash
kubectl get pods -n retail -l app=edge-cache -o wide
kubectl get pods -n retail -l "app in (frontend,edge-cache)" \
  -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
```

**Common mistake:** writing the `labelSelector` to match the Pod *being scheduled* (`app: edge-cache`)
instead of the **target** Pods it should be near (`app: frontend`) — pod affinity/anti-affinity
`labelSelector`s always describe the pods you're relating *to*, never the pod carrying the rule.

</details>

---

### Question 12 — Exact-Match Toleration for a Custom Taint
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Taint `node03` with `gpu=true:NoSchedule`. Create Pod `ml-job` (image `busybox`, command `sleep 3600`) that can land there, and confirm a plain, toleration-less Pod cannot.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl taint nodes node03 gpu=true:NoSchedule

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ml-job
  namespace: retail
spec:
  tolerations:
  - key: gpu
    operator: Equal
    value: "true"
    effect: NoSchedule
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
EOF

kubectl run control-pod -n retail --image=nginx --restart=Never
```

**Verify:**
```bash
kubectl get pods -n retail -o wide      # ml-job may land on node03; control-pod never does
kubectl describe node node03 | grep Taints
```

**Common mistake:** quoting/typing the taint's `value` inconsistently (`gpu=true` vs. an unquoted
boolean-looking `true` in YAML, which is fine as a string but easy to fat-finger) — a toleration
whose `value` doesn't byte-for-byte match the taint's value simply doesn't match, with no error, just
a Pod that silently avoids the tainted node like any other.

</details>

---

### Question 13 — `NoExecute` Taint with `tolerationSeconds`: Delayed Eviction
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** You have three already-Running Pods on `node04`: `evict-now` (no tolerations), `evict-later` (tolerates the taint you're about to apply, but only for 30 seconds), and `stay-forever` (tolerates it with no `tolerationSeconds`, i.e. indefinitely). Apply a `NoExecute` taint to `node04` and observe/explain the three different outcomes.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
for name in evict-now evict-later stay-forever; do
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $name
  namespace: retail
spec:
  nodeName: node04
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
EOF
done
# add tolerations to the two that need them (nodeName pods must be recreated to edit)
kubectl delete pod evict-later stay-forever -n retail
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: evict-later
  namespace: retail
spec:
  nodeName: node04
  tolerations:
  - key: maintenance
    operator: Equal
    value: "true"
    effect: NoExecute
    tolerationSeconds: 30
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: stay-forever
  namespace: retail
spec:
  nodeName: node04
  tolerations:
  - key: maintenance
    operator: Equal
    value: "true"
    effect: NoExecute
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
EOF

kubectl taint nodes node04 maintenance=true:NoExecute
```

**Verify:**
```bash
kubectl get pods -n retail -o wide -w
# evict-now: Terminating almost immediately
# evict-later: still Running, then Terminating ~30s after the taint was applied
# stay-forever: remains Running indefinitely
```

**Common mistake:** expecting `tolerationSeconds` to *delay when the toleration starts applying* —
it actually delays *eviction after the toleration would otherwise no longer apply/taint appears*; a
Pod without `tolerationSeconds` at all tolerates the taint forever, it isn't "immediately evicted
because the field is missing."

</details>

---

### Question 14 — PriorityClass-Driven Preemption
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Create two `PriorityClass` objects, `retail-high` (value `100000`) and `retail-low` (value `100`). Fill a node's spare capacity with low-priority Pods, then schedule one high-priority Pod that doesn't fit without eviction — confirm the scheduler preempts a low-priority Pod to make room.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: {name: retail-high}
value: 100000
globalDefault: false
description: "Critical retail workloads"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: {name: retail-low}
value: 100
globalDefault: false
description: "Best-effort batch work"
EOF

# pin the whole exercise to one node with a nodeSelector, so contention is guaranteed regardless of
# how much spare capacity happens to exist elsewhere in the cluster — otherwise the high-priority Pod
# could simply land on a different, still-free node and no preemption would ever be triggered
kubectl label nodes node02 role=priority-test --overwrite

# check allocatable capacity on the target node first, then size requests to consume most of it
kubectl describe node node02 | grep -A5 Allocatable

kubectl create deployment filler -n retail --image=nginx --replicas=4
kubectl patch deployment filler -n retail --type=json -p '[
  {"op":"add","path":"/spec/template/spec/priorityClassName","value":"retail-low"},
  {"op":"add","path":"/spec/template/spec/nodeSelector","value":{"role":"priority-test"}},
  {"op":"add","path":"/spec/template/spec/containers/0/resources","value":
    {"requests":{"cpu":"400m","memory":"256Mi"}}}
]'

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: critical-job
  namespace: retail
spec:
  priorityClassName: retail-high
  nodeSelector: {role: priority-test}
  containers:
  - name: nginx
    image: nginx
    resources:
      requests: {cpu: "400m", memory: "256Mi"}
EOF
```

**Verify:**
```bash
kubectl get pod critical-job -n retail -o wide     # Running, on node02
kubectl get events -n retail --field-selector reason=Preempted
kubectl get pods -n retail -l app=filler -o wide   # one fewer than before, one shows Pending/Terminating
```

**Common mistake:** forgetting to also pin `critical-job` itself to the same `nodeSelector`-labeled
node as the filler Pods — without that, a multi-node cluster may simply schedule it onto a different,
still-uncontended node, and no preemption happens at all even though the setup looks right.
Separately, assuming preemption requires the low-priority Pods to have **no** resource
requests — with zero requests they're `BestEffort` and free to co-exist without ever blocking the
scheduler, so nothing gets preempted because nothing was actually contended; preemption is only
triggered when the higher-priority Pod genuinely can't fit otherwise.

</details>

---

### Question 15 — Basic CPU-Based Horizontal Pod Autoscaling
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 5 min
**Task:** Deployment `worker` (image `nginx`, `resources.requests.cpu: 100m` already set) exists in namespace `retail`. Create an HPA targeting 50% average CPU utilization, with a floor of 2 and a ceiling of 6 replicas.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create deployment worker -n retail --image=nginx
kubectl set resources deployment/worker -n retail --requests=cpu=100m

kubectl autoscale deployment worker -n retail --cpu=50% --min=2 --max=6
```

**Verify:**
```bash
kubectl get hpa worker -n retail
# NAME  REFERENCE          TARGETS    MINPODS  MAXPODS  REPLICAS
# worker Deployment/worker <unknown>/50%  2       6        2
kubectl describe hpa worker -n retail | grep -A5 Conditions
```

**Common mistake:** creating the HPA before the target Deployment has an explicit `resources.requests.cpu`
set on every container — utilization percentage is calculated relative to the request, so without it
the HPA can compute against Pods and shows `<unknown>` for TARGETS indefinitely, which looks like a
broken HPA but is actually a missing-prerequisite problem on the Deployment side.

</details>

---

### Question 16 — Tune HPA Scaling Behavior to Prevent Flapping
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** The `worker` HPA from the previous question scales down too aggressively during brief traffic dips, causing flapping. Reconfigure it (via `autoscaling/v2`) so that scale-down waits for a 2-minute stabilization window and removes at most 1 Pod per minute, while leaving scale-up behavior at its default.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get hpa worker -n retail -o yaml > worker-hpa.yaml
# edit worker-hpa.yaml: apiVersion must be autoscaling/v2 (autoscale generates v2 by default in
# recent kubectl, but confirm), add under spec:
cat <<'EOF' | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker
  namespace: retail
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worker
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 120
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
EOF
```

**Verify:**
```bash
kubectl get hpa worker -n retail -o jsonpath='{.spec.behavior.scaleDown}'
kubectl describe hpa worker -n retail | grep -A10 Behavior
```

**Common mistake:** forgetting that adding a `behavior.scaleDown` block **replaces** the built-in
default policies rather than layering on top of them — if the task also needs scale-up left at
default, omit `behavior.scaleUp` entirely rather than copying scale-down values into it "to be
consistent."

</details>

---

### Question 17 — Fix a Deployment That Won't Apply After a Selector Edit
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Someone tried to change Deployment `inventory`'s `spec.selector.matchLabels` from `app: inventory` to `app: inventory-v2` and re-apply, and it's now failing. Get the Deployment back to a working, applying state while still ending up with Pods labeled `app: inventory-v2`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create deployment inventory -n retail --image=nginx --replicas=2

kubectl get deployment inventory -n retail -o yaml > inventory.yaml
sed -i 's/app: inventory$/app: inventory-v2/' inventory.yaml   # only under selector.matchLabels in this exercise
kubectl apply -f inventory.yaml
# error: spec.selector: Invalid value: ... field is immutable

# selector is immutable -> delete and recreate is the only path for a scratch object like this
kubectl delete deployment inventory -n retail
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory
  namespace: retail
spec:
  replicas: 2
  selector:
    matchLabels: {app: inventory-v2}
  template:
    metadata:
      labels: {app: inventory-v2}
    spec:
      containers:
      - name: nginx
        image: nginx
EOF
```

**Verify:**
```bash
kubectl get deploy inventory -n retail            # 2/2 ready
kubectl get pods -n retail -l app=inventory-v2    # 2 pods present
```

**Common mistake:** editing only `spec.template.metadata.labels` and leaving `spec.selector.matchLabels`
untouched (or vice versa) — the API server validates on every write that `spec.template.metadata.labels`
is a superset of `spec.selector.matchLabels`, so editing just one of the two is rejected immediately
(`selector does not match template labels`), not just when you later try to change the selector itself.
The separate, `field is immutable` error only shows up once the labels *do* still match each other but
you're attempting to change `spec.selector` to a different value than what the Deployment was created
with — which is why the fix here is delete-and-recreate rather than an in-place edit.

</details>

---

### Question 18 — DaemonSet That Actually Reaches Every Node, Including Control-Plane
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create DaemonSet `node-agent` (image `busybox`, command `sleep 3600`) that runs on **every** node in the cluster, including the control-plane node(s).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
  namespace: retail
spec:
  selector:
    matchLabels: {app: node-agent}
  template:
    metadata:
      labels: {app: node-agent}
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - name: agent
        image: busybox
        command: ["sleep", "3600"]
EOF
```

**Verify:**
```bash
kubectl get ds node-agent -n retail    # DESIRED == CURRENT == READY == total node count
kubectl get pods -n retail -l app=node-agent -o wide   # one Pod per node, including control-plane
```

**Common mistake:** assuming DaemonSets automatically tolerate the control-plane taint because
"they're supposed to run everywhere" — a stock DaemonSet manifest has no built-in special treatment
for that specific taint; system DaemonSets like `kube-proxy` only land there because their own
manifests carry this exact toleration explicitly.

</details>

---

### Question 19 — StatefulSet with Stable Identity and Per-Pod Storage
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Create headless Service `ledger-db` and StatefulSet `ledger-db` (image `nginx`, 3 replicas) with a `volumeClaimTemplate` requesting `1Gi` each. Confirm ordinal Pod names, per-Pod DNS, and that each Pod's PVC survives Pod deletion.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ledger-db
  namespace: retail
spec:
  clusterIP: None
  selector: {app: ledger-db}
  ports:
  - port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ledger-db
  namespace: retail
spec:
  serviceName: ledger-db
  replicas: 3
  selector:
    matchLabels: {app: ledger-db}
  template:
    metadata:
      labels: {app: ledger-db}
    spec:
      containers:
      - name: nginx
        image: nginx
        volumeMounts:
        - name: data
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata: {name: data}
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests: {storage: 1Gi}
EOF
```

**Verify:**
```bash
kubectl get pods -n retail -l app=ledger-db -o name        # ledger-db-0, ledger-db-1, ledger-db-2, in order
kubectl run dns-test -n retail --image=busybox --restart=Never -- sleep 60
kubectl exec -n retail dns-test -- nslookup ledger-db-0.ledger-db.retail.svc.cluster.local
kubectl get pvc -n retail -l app=ledger-db                  # one PVC per Pod
kubectl delete pod ledger-db-0 -n retail
kubectl get pvc -n retail | grep ledger-db-0                # PVC still present after Pod recreation
```

**Common mistake:** forgetting `clusterIP: None` on the Service (making it non-headless) — the
StatefulSet still creates Pods and PVCs fine, but per-Pod DNS names never resolve, and the failure is
silent unless you specifically test DNS resolution rather than just checking Pod status.

</details>

---

### Question 20 — Canary a StatefulSet Update with `partition`
**Priority:** P2 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** StatefulSet `ledger-db` (3 replicas, currently `nginx:1.25`) needs a canary rollout to `nginx:1.27`: only the highest-ordinal Pod (`ledger-db-2`) should update initially. Once you've confirmed it, complete the rollout to all three.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl patch statefulset ledger-db -n retail --type=merge -p '{
  "spec": {"updateStrategy": {"rollingUpdate": {"partition": 2}}}
}'
kubectl set image statefulset/ledger-db -n retail nginx=nginx:1.27

kubectl get pods -n retail -l app=ledger-db -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[0].image}{"\n"}{end}'
# ledger-db-0 and ledger-db-1 still nginx:1.25; only ledger-db-2 updated to nginx:1.27

# satisfied with the canary -> roll the rest forward
kubectl patch statefulset ledger-db -n retail --type=merge -p '{
  "spec": {"updateStrategy": {"rollingUpdate": {"partition": 0}}}
}'
```

**Verify:**
```bash
kubectl rollout status statefulset/ledger-db -n retail
kubectl get pods -n retail -l app=ledger-db -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[0].image}{"\n"}{end}'
# all three now nginx:1.27
```

**Common mistake:** forgetting that StatefulSet rolling updates always proceed in **reverse** ordinal
order (highest number first) — expecting `ledger-db-0` to be the canary and being confused when it's
actually the last one touched.

</details>

---

### Question 21 — Job with Exact `completions`/`parallelism`/`backoffLimit`
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create Job `reconcile` (image `busybox`) that must reach exactly 6 successful completions, run at most 3 Pods concurrently, using `completionMode: Indexed`, and give up after 1 retry per index (`backoffLimit: 1`).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create job reconcile -n retail --image=busybox --dry-run=client -o yaml \
  -- sh -c 'echo "reconciling index $JOB_COMPLETION_INDEX"' > reconcile.yaml
# edit reconcile.yaml: spec.completions=6, spec.parallelism=3, spec.backoffLimit=1,
#   spec.completionMode=Indexed
kubectl apply -f reconcile.yaml
```

**Verify:**
```bash
kubectl get job reconcile -n retail                # COMPLETIONS eventually 6/6
kubectl get pods -n retail -l job-name=reconcile -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.phase}{"\n"}{end}'
```

**Common mistake:** relying on `kubectl create job` alone and stopping there — it doesn't expose
`completions`, `parallelism`, or `completionMode` as flags, so the generated YAML silently defaults
both numeric fields to `1`; the task's exact numbers only land if you hand-edit the file afterward.

</details>

---

### Question 22 — CronJob with `concurrencyPolicy: Forbid`
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Create CronJob `nightly-report` (image `busybox`) running every minute, whose Job sleeps for 90 seconds, with `concurrencyPolicy: Forbid`. Observe and explain why the second scheduled run is skipped.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create cronjob nightly-report -n retail --image=busybox --schedule="*/1 * * * *" \
  --dry-run=client -o yaml -- sh -c "sleep 90" > nightly-report.yaml
# edit nightly-report.yaml: spec.concurrencyPolicy: Forbid
kubectl apply -f nightly-report.yaml
```

**Verify:**
```bash
kubectl get jobs -n retail --watch     # over ~3 minutes, watch for a scheduled minute producing NO new job
kubectl get cronjob nightly-report -n retail   # LAST SCHEDULE TIME advances even when a run is skipped
kubectl get events -n retail --field-selector reason=JobAlreadyActive
```

**Common mistake:** assuming a "missing" Job for a given minute means the CronJob controller is
broken — with `Forbid`, that's the intended, correct behavior whenever the previous run is still
active; check `concurrencyPolicy` before assuming a scheduling bug.

</details>

---

### Question 23 — Roll Back to a Specific (Not Just "Previous") Revision
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Deployment `gateway` goes through three image updates (`nginx:1.24` → `nginx:1.25` → `nginx:1.26`), each with a recorded change-cause. Roll back specifically to the `nginx:1.24` revision — not simply "the previous one" — and confirm you landed on the exact intended revision.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create deployment gateway -n retail --image=nginx:1.24
kubectl annotate deployment gateway -n retail kubernetes.io/change-cause="initial 1.24"

kubectl set image deployment/gateway -n retail nginx=nginx:1.25
kubectl annotate deployment gateway -n retail kubernetes.io/change-cause="bump to 1.25" --overwrite
kubectl rollout status deployment/gateway -n retail

kubectl set image deployment/gateway -n retail nginx=nginx:1.26
kubectl annotate deployment gateway -n retail kubernetes.io/change-cause="bump to 1.26" --overwrite
kubectl rollout status deployment/gateway -n retail

kubectl rollout history deployment/gateway -n retail
# identify the revision number whose CHANGE-CAUSE is "initial 1.24"
kubectl rollout undo deployment/gateway -n retail --to-revision=1
```

**Verify:**
```bash
kubectl get deploy gateway -n retail -o jsonpath='{.spec.template.spec.containers[0].image}'  # nginx:1.24
kubectl rollout history deployment/gateway -n retail   # a new revision now exists reflecting the rollback
```

**Common mistake:** running a plain `kubectl rollout undo` (no `--to-revision`) expecting it to reach
revision 1 — with three revisions already applied, a bare `undo` only reverts one step (to the
`nginx:1.25` revision), not all the way back; getting to a *specific*, non-adjacent revision always
requires `--to-revision=N`.

</details>

---

### Question 24 — Layer Startup, Readiness, and Liveness Probes Correctly
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Pod `slow-starter` (image `nginx`) simulates an app that takes ~20 seconds to become healthy after container start. Configure probes so that: (1) liveness never fires prematurely during that startup window, (2) readiness independently gates traffic once genuinely healthy, and (3) once past startup, a broken app is still restarted by liveness in a reasonable time.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: slow-starter
  namespace: retail
spec:
  containers:
  - name: nginx
    image: nginx
    command: ["sh", "-c", "sleep 20 && nginx -g 'daemon off;'"]
    startupProbe:
      httpGet: {path: /, port: 80}
      periodSeconds: 5
      failureThreshold: 6        # allows up to 30s of startup before giving up
    readinessProbe:
      httpGet: {path: /, port: 80}
      periodSeconds: 5
      failureThreshold: 1
    livenessProbe:
      httpGet: {path: /, port: 80}
      periodSeconds: 10
      failureThreshold: 3
EOF
```

**Verify:**
```bash
kubectl get pod slow-starter -n retail -w      # 0/1 for ~20s, no restarts, then 1/1
kubectl describe pod slow-starter -n retail | grep -i unhealthy   # none during the startup window
kubectl exec slow-starter -n retail -- rm /usr/share/nginx/html/index.html
kubectl get pod slow-starter -n retail          # drops to 0/1 (readiness), stays Running (no restart yet)
```

**Common mistake:** setting a long `initialDelaySeconds` on the liveness probe instead of using a
dedicated `startupProbe` — a fixed delay is a guess that either wastes time on fast starts or still
fails on slow ones; a `startupProbe` disables liveness/readiness checks entirely until it itself
succeeds, which is the mechanism actually designed for variable-length startup.

</details>

---

### Question 25 — Gate Main-Container Start on an Init Container
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create Pod `settle-batch` with an init container that waits 5 seconds and then writes a marker file to a shared `emptyDir`; the main container must not start doing its real work until that marker exists.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: settle-batch
  namespace: retail
spec:
  initContainers:
  - name: prep
    image: busybox
    command: ["sh", "-c", "sleep 5 && echo ready > /work/ready"]
    volumeMounts:
    - name: work
      mountPath: /work
  containers:
  - name: main
    image: busybox
    command: ["sh", "-c", "cat /work/ready && sleep 3600"]
    volumeMounts:
    - name: work
      mountPath: /work
  volumes:
  - name: work
    emptyDir: {}
EOF
```

**Verify:**
```bash
kubectl get pod settle-batch -n retail        # shows Init:0/1 for ~5s, then Running
kubectl logs settle-batch -n retail -c prep   # (no stdout expected; check exit via describe)
kubectl logs settle-batch -n retail -c main   # prints "ready"
```

**Common mistake:** mounting the shared `emptyDir` in the init container but forgetting the matching
`volumeMounts` entry in the main container (or vice versa) — the Pod still starts fine either way,
but the main container never actually sees the marker file, which is a much quieter failure than a
Pod stuck `Init:0/1`.

</details>
