# CKA Mock Exam 3 — Hard Mode

*Original, hand-built mock exam. No task below reproduces or paraphrases any specific remembered real CKA exam question — every scenario is constructed from the general competency/skill patterns documented in `CKA/01-exam-snapshot-and-priorities.md` and `CKA/02-topics/`. This exam is deliberately harder than the real thing: several tasks stack two or more independent faults into one task, the time budget is tighter than Mock Exam 2, and several task descriptions are written the way a rushed proctor-written task actually reads — slightly ambiguous, front-loaded with backstory, requiring you to extract the actual acceptance criteria before you start typing.*

---

# Instructions

**Time limit: 2 hours (120 minutes) for 20 tasks.** That's an average of 6 minutes per task — tighter than Mock Exam 2 and tighter than the real exam's ~7-minutes-per-task community-reported pace (per the snapshot file, this pacing claim carries "Moderate" signal strength but is directionally right). Several tasks below are deliberately worth more points *because* they bundle multiple faults or multiple skills — budget your time against the point value, not against task count. A 7-point task earning the same clock time as a 3-point task is a losing trade.

**Context-switching discipline.** This mock simulates multiple clusters via invented `kubectl` contexts. Every task states the exact context to switch to before you touch anything:

```bash
kubectl config get-contexts
kubectl config use-context <name>
kubectl config current-context   # confirm before every task, not just the first one
```

This mock groups tasks into contiguous blocks per context (unlike the real exam, where tasks are not grouped by cluster and you'll jump between contexts far more unpredictably) — treat that as an easier on-ramp here, not a pattern to rely on for the real exam. Grading an answer applied to the wrong context is the single most avoidable way to lose points on the real exam — verify `current-context` after every switch, not just once at the start.

**Setup blocks.** Each task includes a short "Setup" section describing the pre-existing state of the cluster (backstory + the fault(s) already present). Since this is a self-administered mock rather than a live proctored environment, you must first *apply* the Setup block yourself (as if it were done by "a previous admin") before attempting the fix — treat the moment you finish running Setup as the moment the real exam clock would start on that task. Do not read ahead into the Solutions section while doing this.

**Scoring.** 100 points total across 20 tasks. Point values are weighted to track the official CKA domain weighting as closely as a 20-task exam allows:

| Domain | Official weight | Points in this mock | Task count |
|---|---|---|---|
| Troubleshooting | 30% | 30 | 6 |
| Cluster Architecture, Installation & Configuration | 25% | 25 | 5 |
| Services & Networking | 20% | 20 | 4 |
| Workloads & Scheduling | 15% | 15 | 3 |
| Storage | 10% | 10 | 2 |
| **Total** | **100%** | **100** | **20** |

**Passing score: 66/100 (66%)** — matching the real CKA exam's confirmed passing threshold.

**Exam-realistic allowances (per the confirmed exam format):** `kubectl` pre-aliased to `k` is assumed allowed — set it yourself (`alias k=kubectl`, `export do="--dry-run=client -o yaml"`) since this mock doesn't do it for you. `kubernetes.io/docs/`, `kubernetes.io/blog/`, `helm.sh/docs/`, and `gateway-api.sigs.k8s.io/` are all fair game to consult mid-task, exactly as they are on the real exam — using them is not cheating on this mock, it's practicing the real workflow. Do not consult external search engines, forums, or AI tools while attempting tasks — that would defeat the point of a mock.

**Read every task twice before acting.** Several tasks in this mock understate how many things are actually wrong, or state a constraint in passing (a "without also breaking X" or "the app only ever runs as Y" clause) that changes which fix is correct. This is intentional and mirrors genuinely ambiguous real task wording, not sloppy writing on this mock's part.

---

# Tasks

## Task 1 — Worker node NotReady (5 points)

**Context:** `kubectl config use-context k8s-trouble-alpha`

**Domain:** Troubleshooting

**Setup (apply this first):** SSH to worker node `node-alpha-2`. Run:
```bash
sudo systemctl stop kubelet
```
Then open `/var/lib/kubelet/kubeadm-flags.env` and append `-broken` to the container-runtime-endpoint socket filename referenced inside `KUBELET_KUBEADM_ARGS` (e.g. turn `...containerd.sock` into `...containerd.sock-broken`). Save, then run:
```bash
sudo systemctl start kubelet
```

**Your task:** `node-alpha-2` is now `NotReady`. Bring it back to `Ready` using only node-local diagnosis — do not reboot the node and do not re-run `kubeadm join`.

---

## Task 2 — Control-plane component not reconciling (6 points)

**Context:** `kubectl config use-context k8s-trouble-alpha`

**Domain:** Troubleshooting

**Setup (apply this first):** On the control-plane node, edit `/etc/kubernetes/manifests/kube-controller-manager.yaml` and make **two** independent changes: (1) change the `hostPath.path` of the volume that mounts the PKI directory to `/etc/kubernetes/pki-old` (a directory that does not exist), and (2) introduce a typo in the leader-election flag, changing `--leader-elect=true` to `--leader-electt=true`. Save the file.

**Your task:** `kubectl` itself works fine (the apiserver is healthy), but nothing is reconciling — newly created Deployments never produce a ReplicaSet, and Node taint cleanup after Task 1's fix isn't happening either. Diagnose and fully restore `kube-controller-manager` to a stable, non-restarting state. Fixing only one of the two faults will not be enough — confirm stability, don't just confirm the pod exists.

---

## Task 3 — Node maintenance blocked by a PodDisruptionBudget (3 points)

**Context:** `kubectl config use-context k8s-trouble-alpha`

**Domain:** Cluster Architecture (node lifecycle)

**Setup (apply this first):**
```bash
kubectl create namespace ops
kubectl -n ops create deployment billing-worker --image=nginx --replicas=2
kubectl -n ops patch deployment billing-worker -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"node-alpha-2"}}}}}'
```
Then create a PodDisruptionBudget in `ops` named `billing-worker-pdb` selecting `billing-worker`'s pods with `minAvailable: 2`.

**Your task:** `node-alpha-2` needs an emergency kernel patch tonight. Take it fully out of service (no schedulable pods left running on it except unavoidable DaemonSets) and confirm the drain actually completes rather than hanging or erroring — then bring it back into service once the (simulated) patch is done. You may not simply delete the PDB to make the problem go away; the availability guarantee it encodes must still be respected by whatever you do to `billing-worker` itself.

---

## Task 4 — CrashLoopBackOff with a compounding fix (4 points)

**Context:** `kubectl config use-context k8s-trouble-beta`

**Domain:** Troubleshooting

**Setup (apply this first):**
```bash
kubectl create namespace fintech
```
Create a Deployment `payments-api` in `fintech` (1 replica) running an image that takes roughly 20 seconds to become ready (any slow-starting image is fine, e.g. one with a startup sleep, or simulate with a `postStart`-style delay in your own test image) with:
- `resources.limits.memory: 64Mi` (the process needs closer to 150Mi once warmed up)
- `livenessProbe` with `initialDelaySeconds: 5`

**Your task:** `payments-api` is stuck in `CrashLoopBackOff`. Get it stable. Note: fixing only the most obvious symptom you find first will not fully resolve this.

---

## Task 5 — Service unreachable, two independent root causes (6 points)

**Context:** `kubectl config use-context k8s-trouble-beta`

**Domain:** Troubleshooting

**Setup (apply this first):**
```bash
kubectl create namespace shop
kubectl -n shop create deployment checkout --image=nginx --replicas=2
kubectl -n shop label deployment checkout app=checkout --overwrite
kubectl -n shop patch deployment checkout -p '{"spec":{"template":{"metadata":{"labels":{"app":"checkout"}}}}}'
kubectl -n shop expose deployment checkout --name=checkout-svc --port=8080 --target-port=80
kubectl -n shop patch service checkout-svc -p '{"spec":{"selector":{"app":"checkoutt"}}}'
kubectl -n shop create deployment web --image=nginx --replicas=1
kubectl -n shop label deployment web app=web --overwrite
```
Then apply a default-deny ingress `NetworkPolicy` named `checkout-default-deny` in `shop` selecting `app: checkout` pods, with no corresponding allow policy for anything.

**Your task:** Nothing reaches `checkout-svc` from the `web` tier — not intermittently, not at all. Restore full connectivity from `web` pods to `checkout` pods on port 8080, without removing `checkout-default-deny` and without opening `checkout` up to traffic from pods other than `web`.

---

## Task 6 — Namespace-scoped DNS failure (5 points)

**Context:** `kubectl config use-context k8s-trouble-beta`

**Domain:** Troubleshooting

**Setup (apply this first):**
```bash
kubectl create namespace analytics
```
Apply a default-deny-egress `NetworkPolicy` in `analytics` (selecting all pods, `policyTypes: [Egress]`, empty `egress: []`) with no port-53 carve-out.

**Your task:** Pods you create in `analytics` cannot resolve any DNS name — not `kubernetes.default`, not external names. Pods in `default` namespace resolve fine, and CoreDNS itself is healthy. Fix DNS resolution for `analytics` without disabling the namespace's egress restriction entirely — only the minimum needed for DNS should be opened.

---

## Task 7 — Pending pod, two-stage fix under a fixed constraint (4 points)

**Context:** `kubectl config use-context k8s-trouble-beta`

**Domain:** Troubleshooting

**Setup (apply this first):** On a 2-worker-node section of this cluster (call them `node-beta-1` and `node-beta-2`), label `node-beta-2` with `disktype=ssd`. Then taint `node-beta-2` with `maintenance=true:NoSchedule` (left over from work that actually finished an hour ago — nobody removed it). Create a namespace `jobs` and a Pod `batch-loader` in it with:
- a **hard** node affinity requirement: `disktype In [ssd]`
- `resources.requests`: `cpu: "4"`, `memory: "8Gi"` (deliberately oversized for this lab's node capacity)
- no tolerations

**Your task:** `batch-loader` has been `Pending` for a while. Get it `Running` — it must still end up running only on an `ssd`-labeled node (do not relabel `node-beta-1` to make this trivially true; that would silently violate the actual intent of the constraint).

---

## Task 8 — etcd snapshot backup (4 points)

**Context:** `kubectl config use-context k8s-admin-etcd`

**Domain:** Cluster Architecture

**Setup (apply this first):**
```bash
kubectl create namespace pre-incident
```

**Your task:** Take a snapshot of this cluster's etcd data and save it to `/opt/backups/etcd-pre-migration.db`. Before you consider this task done, verify the snapshot is actually valid and non-empty — a snapshot file existing on disk is not the same thing as a snapshot you can actually restore from later, and that distinction is the entire point of this task.

---

## Task 9 — etcd disaster recovery (7 points)

**Context:** `kubectl config use-context k8s-admin-etcd`

**Domain:** Cluster Architecture

**Setup (apply this first, only after Task 8 is genuinely complete):**
```bash
kubectl create namespace post-incident
```
Then simulate the disaster: move `etcd.yaml` to `/tmp/etcd.yaml` (out of `/etc/kubernetes/manifests/`) to stop etcd, and delete the contents of its data directory (`/var/lib/etcd`, or whatever `--data-dir` the manifest specified).

**Your task:** The control plane's etcd is gone. Restore cluster state from the snapshot at `/opt/backups/etcd-pre-migration.db` (from Task 8) into a **new** data directory, repoint etcd at it, and get the control plane serving again. When you're done, `pre-incident` namespace must exist and `post-incident` must not — that asymmetry is your actual proof of a correct point-in-time restore, not merely "etcd is Running again."

---

## Task 10 — Certificate SAN gap plus a stale local kubeconfig (6 points)

**Context:** `kubectl config use-context k8s-admin-security`

**Domain:** Cluster Architecture

**Setup (apply this first):** Note (no action needed yet — this is backstory): ops just started routing internal traffic to this control plane through a new hostname, `cp.internal.example`, which resolves to the control-plane node's IP. The current `kube-apiserver` certificate's Subject Alternative Names do not include this hostname. Also make a throwaway backup copy of your current `~/.kube/config` right now, before doing anything else (`cp ~/.kube/config ~/.kube/config.bak-before-task`) — you'll need to reason about which copy is "current" later.

**Your task:** Make a client connecting via `https://cp.internal.example:6443` with an admin identity succeed with no TLS hostname-mismatch error, **without regenerating the cluster CA**. Once fixed, make sure your own working `~/.kube/config` actually reflects the cluster's current state — don't leave yourself with a kubeconfig that happened to work before your fix but is now stale.

---

## Task 11 — RBAC: replace an over-broad grant with least privilege (5 points)

**Context:** `kubectl config use-context k8s-admin-security`

**Domain:** Cluster Architecture

**Setup (apply this first):**
```bash
kubectl create namespace ci
kubectl -n ci create serviceaccount build-bot
kubectl create clusterrolebinding build-bot-admin --clusterrole=cluster-admin --serviceaccount=ci:build-bot
kubectl -n ci create deployment sample-app --image=nginx
```

**Your task:** `build-bot-admin` was granted "temporarily" months ago and was never revisited. Remove it, and replace it with exactly the access the CI pipeline actually needs: `get`/`list`/`watch` on `pods` and `deployments`, plus `get` on `pods/log` (log streams can only be fetched one pod at a time — `list`/`watch` don't apply to that subresource) — all scoped to the `ci` namespace only, nothing cluster-wide. The pipeline must still be able to do its job after your change; it must not be able to do anything outside `ci`, and it must not be able to write/delete anything anywhere.

---

## Task 12 — Service exists, selector looks fine, still unreachable (4 points)

**Context:** `kubectl config use-context k8s-net`

**Domain:** Services & Networking

**Setup (apply this first):**
```bash
kubectl create namespace store
kubectl -n store create deployment catalog --image=nginx --replicas=3
kubectl -n store label deployment catalog app=catalog --overwrite
kubectl -n store patch deployment catalog -p '{"spec":{"template":{"metadata":{"labels":{"app":"catalog"}}}}}'
kubectl -n store expose deployment catalog --name=catalog-svc --port=80 --target-port=8080
```
Then, inside the `catalog` pods' container spec, make the actual process listen on port `8081` instead of `8080` (e.g. if using nginx, remap its listen directive, or substitute any simple HTTP server image you control that listens on 8081) — leave every manifest's stated port fields exactly as created above.

**Your task:** `catalog-svc`'s selector correctly matches the `catalog` pods, and `kubectl describe svc` shows non-empty endpoints — yet nothing reaching the Service on port 80 gets a response. Fix it without recreating the Deployment.

---

## Task 13 — Three-tier NetworkPolicy segmentation (6 points)

**Context:** `kubectl config use-context k8s-net`

**Domain:** Services & Networking

**Setup (apply this first):**
```bash
kubectl create namespace secure-app
kubectl -n secure-app create deployment frontend --image=nginx
kubectl -n secure-app label deployment frontend tier=frontend --overwrite
kubectl -n secure-app create deployment backend --image=nginx
kubectl -n secure-app label deployment backend tier=backend --overwrite
kubectl -n secure-app create deployment db --image=nginx
kubectl -n secure-app label deployment db tier=db --overwrite
```
(Patch each Deployment's pod template labels to match, the same way as in earlier setup blocks.)

**Your task:** In `secure-app`, enforce: `frontend` may reach `backend` on port 8080 and nothing else; `backend` may reach `db` on port 5432 and nothing else; `frontend` must never be able to reach `db` directly, under any circumstance, at any point in your rollout of these policies; every tier must retain working DNS resolution; anything not explicitly allowed above must be denied.

---

## Task 14 — Ingress with two independent misconfigurations (5 points)

**Context:** `kubectl config use-context k8s-net`

**Domain:** Services & Networking

**Setup (apply this first):**
```bash
kubectl create namespace shopfront
kubectl -n shopfront create deployment web --image=nginx
kubectl -n shopfront expose deployment web --name=web-svc --port=80
kubectl -n shopfront create deployment api --image=nginx
kubectl -n shopfront expose deployment api --name=api-svc --port=8080
```
Then apply an Ingress `shop-ingress` in `shopfront` for host `shop.example.internal` with `ingressClassName: ngnix` (note the spelling), routing `/` (Prefix) to `web-svc:80` and `/api` (Prefix) to `api-svc:8000`.

**Your task:** "Nothing routes, and there's no obvious error." Get both paths working correctly against the actual installed ingress controller in this cluster (its real `IngressClass` name is whatever `kubectl get ingressclass` shows you — don't assume it matches what's currently in the manifest).

---

## Task 15 — Gateway API HTTPRoute across namespaces (5 points)

**Context:** `kubectl config use-context k8s-net`

**Domain:** Services & Networking

**Setup (apply this first):** Assume a Gateway API controller and CRDs are already installed on this cluster (confirm with `kubectl get gatewayclass` and `kubectl api-resources | grep gateway.networking.k8s.io` — if they're genuinely missing in your own lab, install a controller first as a prerequisite, but that setup step itself is not part of this task's scoring). Create namespace `edge` with a `Gateway` named `edge-gw` that has **two** listeners: `http-internal` (port 8080) and `http-external` (port 80). Create namespace `analytics-backend` with a Service `reports-backend` (port 8080, backed by any simple Deployment). Create an `HTTPRoute` named `reports-route` in namespace `edge` with `parentRefs` naming only `edge-gw` (no `sectionName`), `hostnames: ["reports.example.internal"]`, and a `backendRef` pointing at `reports-backend` in `analytics-backend`.

**Your task:** `reports-route`'s status conditions are not happy. Get `reports.example.internal` correctly routed to `reports-backend` specifically through the `http-external` listener (not `http-internal`), with both `Accepted` and `ResolvedRefs` reporting `True`.

---

## Task 16 — Node affinity, toleration, and a specific-node exclusion (5 points)

**Context:** `kubectl config use-context k8s-workloads`

**Domain:** Workloads & Scheduling

**Setup (apply this first):** Label three nodes `hardware=gpu`: `node-gamma-1`, `node-gamma-2`, `node-gamma-3`. Taint `node-gamma-1` and `node-gamma-2` (but not `node-gamma-3`) with `dedicated=gpu:NoSchedule`. Create namespace `ml`.

**Your task:** Deploy `gpu-inference` (2 replicas) in `ml` such that: it only ever schedules on `hardware=gpu` nodes, it is able to land on the two tainted nodes, and it must **never** land on `node-gamma-3` specifically — that node is reserved for a different team's exclusive workload even though it carries the same `hardware=gpu` label and no taint of its own.

---

## Task 17 — Anti-affinity spread with a resource-fit constraint (5 points)

**Context:** `kubectl config use-context k8s-workloads`

**Domain:** Workloads & Scheduling

**Setup (apply this first):** Confirm this cluster has exactly 3 worker nodes available for scheduling and check each one's allocatable memory (`kubectl describe node <name> | grep -A5 Allocatable`). Create namespace `cache`.

**Your task:** Deploy `session-store` in `cache` with exactly 3 replicas such that no two replicas ever land on the same node (now or after any future reschedule), and each replica's memory *request* is set to at least 70% of a single node's allocatable memory (compute the real number from what you observed — don't guess a round figure that happens to be too low or so high it can't fit three of them across three separate nodes at all).

---

## Task 18 — CronJob silently never running, then getting stuck (5 points)

**Context:** `kubectl config use-context k8s-workloads`

**Domain:** Workloads & Scheduling

**Setup (apply this first):**
```bash
kubectl create namespace maintenance
```
Create a CronJob `nightly-cleanup` in `maintenance` with `schedule: "0 0 31 2 *"` (midnight on February 31st — every field is individually in-range, so the API accepts it, but that calendar date never occurs), `concurrencyPolicy: Forbid`, running any simple image, with **no** `activeDeadlineSeconds` set on its job template, and manually create one stuck Job from its template right now that will never complete on its own (e.g. a container that sleeps far longer than you're willing to wait, with no way to self-terminate) labeled so it's clearly associated with this CronJob.

**Your task:** `nightly-cleanup` shows as enabled in `kubectl get cronjob` but has not produced a single completed Job in two weeks. Fix it so it runs on a sane, valid schedule, and make sure a stuck previous run can never again permanently block all future runs the way the current stuck Job would. Prove it works by getting one full, successful completion within a short test window (temporarily set the schedule to run within the next couple of minutes for verification purposes).

---

## Task 19 — PVC stuck Pending against an existing PV (5 points)

**Context:** `kubectl config use-context k8s-storage`

**Domain:** Storage

**Setup (apply this first):**
```bash
kubectl create namespace orders
```
Create a PV `pv-orders-01`: capacity `2Gi`, `accessModes: [ReadWriteOnce]`, `storageClassName: manual`, any `hostPath` backing. Create a StorageClass `standard-fast` annotated as the cluster default (`storageclass.kubernetes.io/is-default-class: "true"`). Create a PVC `orders-data` in `orders` requesting `2Gi`, `accessModes: [ReadWriteMany]`, with **no** `storageClassName` field set at all.

**Your task:** `orders-data` has been `Pending` since this morning. Bind it to `pv-orders-01` specifically, without recreating either object and without changing `pv-orders-01`'s advertised capacity. The application that will consume this volume only ever runs as a single replica on a single node at a time — factor that into which field(s) you actually need to change.

---

## Task 20 — Conflicting default StorageClasses and a wrong reclaim policy (5 points)

**Context:** `kubectl config use-context k8s-storage`

**Domain:** Storage

**Setup (apply this first):** Create two StorageClasses, both annotated `storageclass.kubernetes.io/is-default-class: "true"`: `slow-hdd` (legacy, provisioner can be anything for this lab) and `fast-ssd` (the intended current default). Create a PV `pv-legacy-logs` (any backing, `reclaimPolicy: Delete`) representing storage for a decommissioned app whose PVC will be deleted later today as part of a cleanup job someone else is running.

**Your task:** Exactly one StorageClass in this cluster should be marked default, and it should be `fast-ssd`. Separately, `pv-legacy-logs` must not lose its underlying data when its PVC is deleted later today — fix its reclaim behavior accordingly before that cleanup job runs.

---

# Solutions & Scoring

Work through the tasks yourself and self-grade against the point values below before reading further. Total: 100 points. **Passing score: 66/100 (66%)**, matching the real CKA exam's confirmed passing threshold.

---

## Task 1 — Worker node NotReady (5 points)

**Diagnosis:** `kubectl describe node node-alpha-2` shows `Ready: Unknown/False`. SSH to the node. `systemctl status kubelet` shows it failed or is repeatedly restarting. `journalctl -u kubelet -n 100 --no-pager` shows an error resolving/dialing the CRI socket (the corrupted `-broken` suffix path in `kubeadm-flags.env`).

**Fix:**
```bash
sudo cat /var/lib/kubelet/kubeadm-flags.env    # spot the "-broken" suffix on the runtime endpoint
sudo vi /var/lib/kubelet/kubeadm-flags.env     # remove the "-broken" suffix, restore the real socket path
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo crictl info   # confirm the runtime is reachable again
```

**Verify:**
```bash
kubectl get node node-alpha-2                                            # Ready
kubectl get pods -A -o wide --field-selector spec.nodeName=node-alpha-2  # pods scheduling/Running again
```

**Points: 5**

---

## Task 2 — Control-plane component not reconciling (6 points)

**Diagnosis:**
```bash
crictl ps -a | grep controller-manager
crictl logs <most-recently-exited-container-id>
```
The log shows both a failure to find the mounted PKI path (from the bad `hostPath`) and/or a flag-parsing error from the typo'd `--leader-electt`.

**Fix:** On the control-plane node:
```bash
sudo vi /etc/kubernetes/manifests/kube-controller-manager.yaml
# 1. Fix the hostPath volume back to /etc/kubernetes/pki
# 2. Fix --leader-electt back to --leader-elect
# save — kubelet reconciles the static pod automatically within ~20s
```

**Verify:**
```bash
crictl ps | grep controller-manager        # Running, restart count stable over ~60s
kubectl create deployment verify-test --image=nginx -n default
kubectl get rs -n default -l app=verify-test    # a ReplicaSet actually gets created — proof reconciliation resumed
kubectl delete deployment verify-test -n default
```

**Common trap this task was built to catch:** fixing only one of the two faults and declaring victory the moment `crictl ps` shows a container running at all, without watching for a few restart cycles or testing actual reconciliation behavior.

**Points: 6**

---

## Task 3 — Node maintenance blocked by a PodDisruptionBudget (3 points)

**Diagnosis:** `kubectl drain node-alpha-2 --ignore-daemonsets` fails/hangs with "Cannot evict pod as it would violate the pod's disruption budget" — `minAvailable: 2` on a 2-replica Deployment mathematically forbids evicting either replica while both must stay available.

**Fix (one valid approach — scale up first so draining one replica still leaves 2 available):**
```bash
kubectl -n ops scale deployment billing-worker --replicas=3
# remove the nodeSelector pin (or add tolerations/allow a second node) so the 3rd replica can actually land elsewhere
kubectl -n ops patch deployment billing-worker --type=json -p='[{"op":"remove","path":"/spec/template/spec/nodeSelector"}]'
kubectl -n ops rollout status deployment billing-worker
kubectl cordon node-alpha-2
kubectl drain node-alpha-2 --ignore-daemonsets --delete-emptydir-data
# ... simulate the patch ...
kubectl uncordon node-alpha-2
```

**Verify:**
```bash
kubectl get nodes                                    # node-alpha-2 shows SchedulingDisabled during drain, Ready after uncordon
kubectl get pdb -n ops                               # billing-worker-pdb still present, unmodified
kubectl -n ops get pods -o wide                       # replicas rescheduled off node-alpha-2 during drain, minAvailable never violated
```

**Points: 3**

---

## Task 4 — CrashLoopBackOff with a compounding fix (4 points)

**Diagnosis:**
```bash
kubectl -n fintech describe pod <payments-api-pod>   # Last State: Terminated, Reason: OOMKilled — first fault
kubectl -n fintech logs <pod> --previous              # may also show the process killed mid-startup by the liveness probe
```
Raising only the memory limit still leaves the liveness probe killing the container before it finishes its ~20-second startup, since `initialDelaySeconds: 5` fires long before readiness.

**Fix:**
```bash
kubectl -n fintech edit deployment payments-api
# resources.limits.memory: 64Mi -> 256Mi (or whatever comfortably exceeds ~150Mi observed usage)
# livenessProbe.initialDelaySeconds: 5 -> 30 (comfortably past the ~20s startup window)
```

**Verify:**
```bash
kubectl -n fintech get pod -w   # Running, restart count stable across a 60+ second observation window
```

**Points: 4**

---

## Task 5 — Service unreachable, two independent root causes (6 points)

**Diagnosis:**
```bash
kubectl -n shop get endpoints checkout-svc          # empty — selector mismatch (app=checkoutt vs app=checkout)
kubectl -n shop get networkpolicy                    # checkout-default-deny selecting app=checkout, Ingress, no allow policy
```
Fixing only the selector still leaves all ingress to `checkout` denied by policy; fixing only the policy still leaves the Service with no endpoints at all.

**Fix:**
```bash
kubectl -n shop patch service checkout-svc -p '{"spec":{"selector":{"app":"checkout"}}}'
```
```yaml
# checkout-allow-web.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: checkout-allow-web
  namespace: shop
spec:
  podSelector:
    matchLabels: { app: checkout }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: web } }
      ports:
        - protocol: TCP
          port: 8080
```
```bash
kubectl apply -f checkout-allow-web.yaml
```

**Verify:**
```bash
kubectl -n shop get endpoints checkout-svc          # now lists pod IPs
kubectl -n shop run tmp --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- --timeout=3 checkout-svc:8080   # from a pod labeled app=web, succeeds
# from a pod WITHOUT app=web, the same wget should time out — confirming the policy still restricts appropriately
```

**Points: 6**

---

## Task 6 — Namespace-scoped DNS failure (5 points)

**Diagnosis:** CoreDNS pods healthy, `kube-dns` Service has endpoints, DNS works fine in `default` — points straight at a namespace-scoped NetworkPolicy rather than a CoreDNS problem. `kubectl get networkpolicy -n analytics` shows a default-deny-egress policy with no DNS carve-out.

**Fix:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: analytics
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns   # adjust to match this cluster's actual CoreDNS pod label
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```
```bash
kubectl apply -f allow-dns-egress.yaml
```
(Combining `namespaceSelector` with `podSelector` in the same `to` entry scopes the carve-out to the actual CoreDNS pods, not every pod in `kube-system` — that's the "minimum needed" the task asks for. A bare `namespaceSelector` alone would over-open egress to all of `kube-system`.)

**Verify:**
```bash
kubectl -n analytics run dnstest --rm -it --image=busybox:1.36 --restart=Never -- nslookup kubernetes.default
# succeeds; the original default-deny-egress policy is still present and unmodified otherwise
```

**Points: 5**

---

## Task 7 — Pending pod, two-stage fix under a fixed constraint (4 points)

**Diagnosis:** `kubectl describe pod batch-loader -n jobs` shows `FailedScheduling` — first likely reason listed is the stale `maintenance=true:NoSchedule` taint on the only `ssd` node; after tolerating that, a second `FailedScheduling` reason (`Insufficient cpu`/`Insufficient memory`) appears from the oversized requests.

**Fix:**
```bash
# Option A (preferred — the taint's underlying reason is over): remove the stale taint
kubectl taint nodes node-beta-2 maintenance=true:NoSchedule-

kubectl -n jobs edit pod batch-loader
# right-size requests down to something this lab's node can actually satisfy, e.g. cpu: "250m", memory: "256Mi"
# (if the field is immutable on a bare Pod, delete and recreate from an edited manifest instead)
```

**Verify:**
```bash
kubectl -n jobs get pod batch-loader -o wide     # Running, NODE = node-beta-2 (the ssd-labeled node)
kubectl describe node node-beta-2 | grep -A3 Taints   # stale taint gone
```

**Points: 4**

---

## Task 8 — etcd snapshot backup (4 points)

```bash
sudo ETCDCTL_API=3 etcdctl snapshot save /opt/backups/etcd-pre-migration.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

sudo ETCDCTL_API=3 etcdctl snapshot status /opt/backups/etcd-pre-migration.db --write-out=table
```

**Verify:** `snapshot status` returns a table with a non-zero `HASH`, `REVISION`, and `TOTAL KEYS` — not an error, not a zero-byte file. Confirming the file merely exists (`ls -la`) is not sufficient verification for this task.

**Points: 4**

---

## Task 9 — etcd disaster recovery (7 points)

**Fix:**
```bash
# etcd is already stopped and its data directory already emptied per the Setup block
sudo etcdutl snapshot restore /opt/backups/etcd-pre-migration.db \
  --data-dir=/var/lib/etcd-restored

sudo vi /etc/kubernetes/manifests/etcd.yaml
# update the hostPath volume's "path" (and matching volumeMount) from /var/lib/etcd to /var/lib/etcd-restored

sudo mv /tmp/etcd.yaml /etc/kubernetes/manifests/etcd.yaml   # move the manifest back in if you'd relocated it
```

**Verify:**
```bash
crictl ps | grep etcd                 # fresh, stable container
kubectl get ns pre-incident           # exists
kubectl get ns post-incident          # NotFound — this asymmetry is the actual proof of a correct point-in-time restore
```

**Common trap this task was built to catch:** using `etcdctl snapshot restore` (removed since etcd 3.5) instead of `etcdutl`; restoring into the original `/var/lib/etcd` path instead of a fresh directory; forgetting to update the manifest's `hostPath` so kubelet keeps mounting the untouched old (empty) directory.

**Points: 7**

---

## Task 10 — Certificate SAN gap plus a stale local kubeconfig (6 points)

**Fix:**
```bash
# 1. Add the missing SAN and regenerate just the apiserver cert (no CA regeneration)
sudo kubeadm init phase certs apiserver --config /path/to/existing/kubeadm-cluster-config.yaml \
  # (ensure that config file's apiServer.certSANs list now includes cp.internal.example before running this)

# force the apiserver static pod to pick up the new cert
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# 2. Refresh the local kubeconfig so it isn't stale relative to current cluster state
sudo cp /etc/kubernetes/admin.conf ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
```

**Verify:**
```bash
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -A2 "Subject Alternative Name"
# cp.internal.example now listed

kubectl --kubeconfig ~/.kube/config get nodes    # succeeds, no x509 hostname-mismatch error, whether reached via the node IP or cp.internal.example
```

**Points: 6**

---

## Task 11 — RBAC: replace an over-broad grant with least privilege (5 points)

**Fix:**
```bash
kubectl delete clusterrolebinding build-bot-admin

kubectl -n ci create role ci-pipeline-role \
  --verb=get,list,watch --resource=pods,deployments
kubectl -n ci create role ci-pipeline-role-logs \
  --verb=get --resource=pods/log
# (or combine both rule sets into a single Role's rules[] block by hand-editing)

kubectl -n ci create rolebinding ci-pipeline-binding \
  --role=ci-pipeline-role --serviceaccount=ci:build-bot
kubectl -n ci create rolebinding ci-pipeline-binding-logs \
  --role=ci-pipeline-role-logs --serviceaccount=ci:build-bot
```

**Verify:**
```bash
kubectl auth can-i get pods -n ci --as=system:serviceaccount:ci:build-bot         # yes
kubectl auth can-i get pods/log -n ci --as=system:serviceaccount:ci:build-bot     # yes
kubectl auth can-i list deployments -n ci --as=system:serviceaccount:ci:build-bot # yes
kubectl auth can-i delete deployments -n ci --as=system:serviceaccount:ci:build-bot   # no
kubectl auth can-i get pods -n default --as=system:serviceaccount:ci:build-bot    # no
kubectl get clusterrolebinding build-bot-admin                                    # NotFound
```

**Points: 5**

---

## Task 12 — Service exists, selector looks fine, still unreachable (4 points)

**Diagnosis:**
```bash
kubectl -n store describe svc catalog-svc      # Selector and Endpoints both look correct
kubectl -n store exec <a-catalog-pod> -- ss -tlnp   # or netstat -tlnp — reveals the process is actually listening on 8081, not 8080
```

**Fix:**
```bash
kubectl -n store patch service catalog-svc -p '{"spec":{"ports":[{"port":80,"targetPort":8081}]}}'
```

**Verify:**
```bash
kubectl -n store run tmp --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- --timeout=3 catalog-svc
```

**Points: 4**

---

## Task 13 — Three-tier NetworkPolicy segmentation (6 points)

**Fix:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: secure-app
spec:
  podSelector:
    matchLabels: { tier: backend }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector: { matchLabels: { tier: frontend } }
      ports: [{ protocol: TCP, port: 8080 }]
  egress:
    - to:
        - podSelector: { matchLabels: { tier: db } }
      ports: [{ protocol: TCP, port: 5432 }]
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector: { matchLabels: { k8s-app: kube-dns } }
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-policy
  namespace: secure-app
spec:
  podSelector:
    matchLabels: { tier: db }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector: { matchLabels: { tier: backend } }
      ports: [{ protocol: TCP, port: 5432 }]
  egress: []   # db needs nothing outbound for this task — explicit empty list denies all egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
  namespace: secure-app
spec:
  podSelector:
    matchLabels: { tier: frontend }
  policyTypes: [Ingress, Egress]
  ingress: []   # nothing in-cluster needs to initiate to frontend for this task — explicit empty list denies all ingress
  egress:
    - to:
        - podSelector: { matchLabels: { tier: backend } }
      ports: [{ protocol: TCP, port: 8080 }]
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector: { matchLabels: { k8s-app: kube-dns } }
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
```
Every direction not explicitly listed above is now denied by an explicit empty rule list, not merely left unmentioned — `db-policy` declares `policyTypes: [Ingress, Egress]` with an empty `egress: []` (no outbound needed), and `frontend-policy` declares both types with an empty `ingress: []` (nothing needs to initiate a connection to `frontend` for this task). Declaring a `policyType` without a matching rules key defaults to deny-all for that direction, which is exactly the "anything not explicitly allowed must be denied" requirement — leaving a `policyType` off entirely (as an earlier draft of this solution did) does not deny that direction, it leaves it unregulated by this policy.

**Verify:**
```bash
# from a frontend pod:
kubectl -n secure-app exec <frontend-pod> -- wget -qO- --timeout=3 backend:8080   # succeeds
kubectl -n secure-app exec <frontend-pod> -- wget -qO- --timeout=3 db:5432        # times out
# from a backend pod:
kubectl -n secure-app exec <backend-pod> -- wget -qO- --timeout=3 db:5432         # succeeds
kubectl -n secure-app exec <backend-pod> -- nslookup kubernetes.default          # succeeds (DNS carve-out present)
```

**Points: 6**

---

## Task 14 — Ingress with two independent misconfigurations (5 points)

**Diagnosis:**
```bash
kubectl get ingressclass                         # real class name, e.g. "nginx" — manifest says "ngnix"
kubectl -n shopfront describe ingress shop-ingress   # backend for /api resolves against api-svc:8000, but api-svc only exposes port 8080
```

**Fix:**
```bash
kubectl -n shopfront patch ingress shop-ingress --type=merge -p '{"spec":{"ingressClassName":"nginx"}}'
kubectl -n shopfront edit ingress shop-ingress
# change the /api path's backend.service.port.number from 8000 to 8080
```

**Verify:**
```bash
kubectl -n shopfront describe ingress shop-ingress   # both rules resolve to non-empty, correct-port endpoints
curl -H "Host: shop.example.internal" http://<ingress-controller-ip>/       # web-svc response
curl -H "Host: shop.example.internal" http://<ingress-controller-ip>/api   # api-svc response
```

**Points: 5**

---

## Task 15 — Gateway API HTTPRoute across namespaces (5 points)

**Diagnosis:**
```bash
kubectl -n edge get httproute reports-route -o jsonpath='{.status.parents[0].conditions}'
# Accepted may be ambiguous/false due to no sectionName against a multi-listener Gateway;
# ResolvedRefs likely False due to the missing ReferenceGrant for the cross-namespace backend
```

**Fix:**
```bash
kubectl -n edge edit httproute reports-route
# under parentRefs, add: sectionName: http-external
```
```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-edge-to-reports-backend
  namespace: analytics-backend
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: edge
  to:
    - group: ""
      kind: Service
      name: reports-backend
```
```bash
kubectl apply -f referencegrant.yaml
```

**Verify:**
```bash
kubectl -n edge get httproute reports-route -o jsonpath='{.status.parents[0].conditions}'
# Accepted: True, ResolvedRefs: True
curl -H "Host: reports.example.internal" http://<gateway-external-address>:80/
```

**Points: 5**

---

## Task 16 — Node affinity, toleration, and a specific-node exclusion (5 points)

**Fix:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-inference
  namespace: ml
spec:
  replicas: 2
  selector:
    matchLabels: { app: gpu-inference }
  template:
    metadata:
      labels: { app: gpu-inference }
    spec:
      tolerations:
        - key: dedicated
          operator: Equal
          value: gpu
          effect: NoSchedule
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: hardware
                    operator: In
                    values: [gpu]
                  - key: kubernetes.io/hostname
                    operator: NotIn
                    values: [node-gamma-3]
      containers:
        - name: app
          image: nginx
```

**Verify:**
```bash
kubectl -n ml get pods -o wide   # both replicas land only on node-gamma-1 and/or node-gamma-2, never node-gamma-3
```

**Common trap this task was built to catch:** tolerating the taint alone is not sufficient (would still allow `node-gamma-3` since it's untainted); node affinity on `hardware=gpu` alone is not sufficient either (doesn't exclude `node-gamma-3`, and without the toleration the pod couldn't land on the two tainted nodes at all) — both the `NotIn` clause and the toleration are required simultaneously.

**Points: 5**

---

## Task 17 — Anti-affinity spread with a resource-fit constraint (5 points)

**Fix (example assuming each node reports ~2Gi allocatable memory — substitute your lab's real observed value):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: session-store
  namespace: cache
spec:
  replicas: 3
  selector:
    matchLabels: { app: session-store }
  template:
    metadata:
      labels: { app: session-store }
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels: { app: session-store }
              topologyKey: kubernetes.io/hostname
      containers:
        - name: app
          image: redis
          resources:
            requests:
              memory: "1500Mi"   # >= 70% of ~2Gi allocatable, and still small enough to fit one per node
```

**Verify:**
```bash
kubectl -n cache get pods -o wide   # 3 distinct NODE values, no duplicates
kubectl -n cache get pods -o jsonpath='{.items[*].spec.containers[0].resources.requests.memory}'
kubectl describe node <any-node> | grep -A10 "Allocated resources"   # confirm the request actually reflects >=70% of that node's allocatable
```

**Points: 5**

---

## Task 18 — CronJob silently never running, then getting stuck (5 points)

**Diagnosis:** `"0 0 31 2 *"` passes the API server's field-range validation (minute 0, hour 0, day-of-month 31, month 2 are each individually valid, so `kubectl` does *not* reject it at creation the way it would reject a truly out-of-range field like a day-of-week of `8`) — but day-of-month 31 can never land in February, so the schedule matches zero real calendar dates and the CronJob controller silently never fires it. That's why it shows as "enabled" in `kubectl get cronjob` with an empty `LAST SCHEDULE` forever. Separately, `concurrencyPolicy: Forbid` plus a manually-created stuck Job with no `activeDeadlineSeconds` means even after fixing the schedule, the CronJob controller will see an "active" job and skip every subsequent scheduled run indefinitely.

**Fix:**
```bash
kubectl -n maintenance delete job <the-manually-created-stuck-job>

kubectl -n maintenance edit cronjob nightly-cleanup
# schedule: "0 0 31 2 *"  ->  "*/2 * * * *"   (temporarily, for verification)
# add under .spec.jobTemplate.spec: activeDeadlineSeconds: 120
```

**Verify:**
```bash
kubectl -n maintenance get jobs -w   # a new Job appears within ~2 minutes and reaches Complete
kubectl -n maintenance get cronjob nightly-cleanup   # LAST SCHEDULE populated, no stuck ACTIVE count
```
Reminder: reset the schedule to its intended production value (e.g. a real nightly cron expression) after verifying — leaving it at `*/2 * * * *` would itself be a wrong final state.

**Points: 5**

---

## Task 19 — PVC stuck Pending against an existing PV (5 points)

**Diagnosis:**
```bash
kubectl -n orders describe pvc orders-data
# Events show it's being evaluated against the default StorageClass (standard-fast) rather than binding to pv-orders-01,
# and/or an access-mode mismatch: PVC wants ReadWriteMany, pv-orders-01 only advertises ReadWriteOnce
```

**Fix:** Both `storageClassName` and `accessModes` are immutable on an existing PVC — and this PVC needs both changed (`""`/default → `manual`, and `ReadWriteMany` → `ReadWriteOnce`), so an in-place `kubectl patch` cannot get there regardless of which field you try first. Delete and recreate the PVC with the correct spec from the start (the PV itself is untouched, so no data risk):
```bash
kubectl -n orders delete pvc orders-data
kubectl apply -f orders-data-fixed.yaml
```
```yaml
# orders-data-fixed.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: orders-data
  namespace: orders
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce   # single-replica, single-node app — RWO is correct and is what pv-orders-01 actually advertises
  resources:
    requests:
      storage: 2Gi
```

**Verify:**
```bash
kubectl -n orders get pvc orders-data     # Bound, VOLUME = pv-orders-01
kubectl get pv pv-orders-01               # STATUS: Bound, CLAIM: orders/orders-data, capacity still 2Gi
```

**Points: 5**

---

## Task 20 — Conflicting default StorageClasses and a wrong reclaim policy (5 points)

**Fix:**
```bash
kubectl patch storageclass slow-hdd \
  -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
# fast-ssd's annotation was already "true" per Setup — leave it as-is

kubectl patch pv pv-legacy-logs \
  -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

**Verify:**
```bash
kubectl get sc    # exactly one entry shows "(default)", and it's fast-ssd
kubectl get pv pv-legacy-logs -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'   # Retain
```
Remember: once its PVC is later deleted, `pv-legacy-logs` will show `STATUS: Released` (not automatically reusable) — that is the correct and expected outcome of `Retain`, not a follow-up bug to chase.

**Points: 5**

---

## Scoring Recap

| # | Task | Domain | Points |
|---|---|---|---|
| 1 | Worker node NotReady | Troubleshooting | 5 |
| 2 | Control-plane component not reconciling | Troubleshooting | 6 |
| 3 | Node maintenance blocked by a PDB | Cluster Architecture | 3 |
| 4 | CrashLoopBackOff, compounding fix | Troubleshooting | 4 |
| 5 | Service unreachable, two root causes | Troubleshooting | 6 |
| 6 | Namespace-scoped DNS failure | Troubleshooting | 5 |
| 7 | Pending pod, two-stage fix | Troubleshooting | 4 |
| 8 | etcd snapshot backup | Cluster Architecture | 4 |
| 9 | etcd disaster recovery | Cluster Architecture | 7 |
| 10 | Certificate SAN gap + stale kubeconfig | Cluster Architecture | 6 |
| 11 | RBAC least-privilege replacement | Cluster Architecture | 5 |
| 12 | Service reachable-looking but broken port | Services & Networking | 4 |
| 13 | Three-tier NetworkPolicy segmentation | Services & Networking | 6 |
| 14 | Ingress, two misconfigurations | Services & Networking | 5 |
| 15 | Gateway API HTTPRoute cross-namespace | Services & Networking | 5 |
| 16 | Node affinity + toleration + exclusion | Workloads & Scheduling | 5 |
| 17 | Anti-affinity spread + resource fit | Workloads & Scheduling | 5 |
| 18 | CronJob never running, then stuck | Workloads & Scheduling | 5 |
| 19 | PVC stuck Pending against existing PV | Storage | 5 |
| 20 | Conflicting default StorageClasses | Storage | 5 |
| | **Total** | | **100** |

**Domain totals:** Troubleshooting 30 · Cluster Architecture 25 · Services & Networking 20 · Workloads & Scheduling 15 · Storage 10 — matching the official CKA domain weighting exactly.

**Pass threshold: 66/100.**
