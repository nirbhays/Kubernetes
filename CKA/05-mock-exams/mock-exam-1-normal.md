# CKA Mock Exam 1 — Normal Difficulty

*Difficulty profile: a fair on-ramp. Generous time-per-task, mostly single-issue faults (one root
cause per task, not stacked failures), and straightforward point values. Intended as your first
full timed run before moving on to harder mocks. All tasks are original — built from the general
competency/skill patterns in `CKA/02-topics/`, not reproductions of any real exam question.*

---

# Instructions

**Time limit: 2 hours (120 minutes), same as the real CKA exam.**

**Context-switching discipline.** This mock simulates a multi-cluster exam environment. Every task
begins with an explicit `kubectl config use-context <name>` instruction. Run that command *before*
touching anything else in the task — do not assume you are still on the context from the previous
task. On the real exam, working in the wrong cluster/context is one of the most common
entirely-avoidable ways to score zero on an otherwise-correct answer. Treat every context switch
as a checkpoint: after switching, run `kubectl config current-context` and `kubectl get nodes` to
confirm you landed where you think you did before making changes.

**Scoring.** Each task lists a point value. Point values are weighted to track the official CKA
domain weighting as closely as a fixed task set allows:

| Domain | Official weight | Points in this mock |
|---|---|---|
| Troubleshooting | 30% | 30 |
| Cluster Architecture, Installation & Configuration | 25% | 25 |
| Services & Networking | 20% | 20 |
| Workloads & Scheduling | 15% | 15 |
| Storage | 10% | 10 |
| **Total** | **100%** | **100** |

**Passing score: 66/100** (66%), matching the real CKA's confirmed passing threshold. There is no
partial credit built into this mock beyond what's implied by multi-part tasks — grade yourself
strictly against the verification command(s) given for each task in the Solutions section.

**Rules while attempting this mock:**
- Do not read the "Solutions & Scoring" section until you have either finished or run out of time.
  It is placed at the very end of this file for exactly that reason.
- Assume `kubectl` is aliased to `k` and `--dry-run=client -o yaml` is your default way of
  generating YAML — mirror real exam conditions.
- Assume `kubernetes.io/docs/`, `kubernetes.io/blog/`, `helm.sh/docs/`, and
  `gateway-api.sigs.k8s.io/` are available to you (in-page search only), exactly as the real exam
  permits.
- Where a task references SSH-ing to a node, treat that as "get a root shell on that node by
  whatever mechanism your lab provides" (`ssh`, `docker exec`, a VM console, etc.).
- Move on if you're stuck for more than double a task's implied time budget — this mirrors real
  exam triage discipline. Points are points regardless of task order.

---

# Tasks

## Task 1 — Worker node NotReady (5 points)

**Context:** `kubectl config use-context k8s-alpha-admin`

Worker node `alpha-wk1` is showing `NotReady`. Bring it back to `Ready` **without rebooting the
node and without running `kubeadm join` again**. Do not cordon, drain, or delete the node as part
of your fix — the expectation is a targeted repair of whatever is actually broken.

---

## Task 2 — Control-plane component crash-looping (5 points)

**Context:** `kubectl config use-context k8s-alpha-admin`

On control-plane node `alpha-cp1`, `kube-controller-manager` is crash-looping. Cluster reconciliation
has stalled — new Deployments are not producing ReplicaSets. Restore `kube-controller-manager` to a
stable `Running` state by fixing the root cause in place. Do not delete and re-`kubeadm init` the
control plane.

---

## Task 3 — CrashLoopBackOff application pod (5 points)

**Context:** `kubectl config use-context k8s-alpha-admin`, namespace `retail`

The `cart` Deployment's pods are stuck in `CrashLoopBackOff`. Diagnose the exact reason the
container is being killed and fix it by adjusting the Deployment's pod spec (do not change the
application image). The fix should result in a stable, non-restarting pod.

---

## Task 4 — ImagePullBackOff (5 points)

**Context:** `kubectl config use-context k8s-alpha-admin`, namespace `retail`

The `catalog` Deployment's pods are stuck in `ImagePullBackOff`. The intended image for this
workload is `nginx:1.27`. Fix the Deployment so its pods pull successfully and reach `Running`.

---

## Task 5 — Service not reaching Pods (5 points)

**Context:** `kubectl config use-context k8s-alpha-admin`, namespace `retail`

The `catalog` Deployment's pods are `Running` and `Ready` (labeled `app=catalog`, listening on
container port 8080). A `ClusterIP` Service named `catalog-svc` exists on port 80 but no traffic
ever reaches the pods. Fix the Service so that traffic sent to `catalog-svc:80` reaches the
`catalog` pods. **Do not change the pod labels or the Deployment.**

---

## Task 6 — Cluster-wide DNS resolution failure (5 points)

**Context:** `kubectl config use-context k8s-alpha-admin`

Pods in every namespace are failing to resolve any DNS name — in-cluster Service names and
external hostnames both fail. Diagnose the root cause and restore DNS resolution cluster-wide.
Do not modify any application Deployments as part of your fix — the fault is in the cluster's DNS
layer itself.

---

## Task 7 — Take an etcd snapshot (6 points)

**Context:** `kubectl config use-context k8s-bravo-admin`

Take a consistent snapshot of this cluster's etcd datastore and save it to
`/opt/backups/etcd-snapshot-bravo.db` on control-plane node `bravo-cp1`. Confirm the snapshot file
is valid and readable before considering the task complete.

---

## Task 8 — Restore a cluster from an etcd snapshot (7 points)

**Context:** `kubectl config use-context k8s-bravo-admin`

Namespace `pre-incident` and everything in it was accidentally deleted. A known-good snapshot taken
before the deletion exists at `/opt/backups/etcd-pre-incident.db` on control-plane node `bravo-cp1`.
Restore the cluster's etcd state from that snapshot so that namespace `pre-incident` exists again.
It is acceptable (and expected) that any cluster resources created *after* the snapshot was taken
are lost as a result of this restore.

---

## Task 9 — Certificate failure diagnosis and renewal (6 points)

**Context:** `kubectl config use-context k8s-bravo-admin`

Cluster operations against `bravo-cp1` are intermittently failing with TLS/`x509` errors. Identify
which certificate(s) are the problem, renew them **without regenerating the cluster CA**, and make
sure the affected component(s) actually pick up the renewed certificate (a renewal alone is not
sufficient if the running process still holds the old cert in memory). Confirm normal cluster
operation afterward.

---

## Task 10 — Least-privilege RBAC for a ServiceAccount (6 points)

**Context:** `kubectl config use-context k8s-bravo-admin`, namespace `ci`

Create a ServiceAccount named `deploy-bot` in namespace `ci`. Grant it exactly the following
permissions, scoped to namespace `ci` only, using the minimum RBAC objects necessary:
- `get`, `list`, and `watch` on `pods`
- `get` on `pods/log`

`deploy-bot` must **not** have any permissions outside namespace `ci`, and must not have any verb
beyond the three listed above on `pods`.

---

## Task 11 — Expose a Deployment and fix a broken Service (6 points)

**Context:** `kubectl config use-context k8s-charlie-admin`, namespace `shop`

The `frontend` Deployment (2 replicas, labeled `app=frontend`, containers listening on port 8080)
currently has no Service. Create a `ClusterIP` Service named `frontend-svc` on port 80 that routes
to the pods' actual listening port.

Separately, a pre-existing Service named `legacy-frontend` in the same namespace is supposed to
also route to the `frontend` pods but currently has no endpoints. Fix `legacy-frontend` so it
routes correctly too, without changing the `frontend` Deployment.

---

## Task 12 — NetworkPolicy: default-deny plus scoped allow (8 points)

**Context:** `kubectl config use-context k8s-charlie-admin`, namespace `shop`

Pods labeled `app=backend` in namespace `shop` currently accept traffic from anywhere. Lock this
down:
1. By default, `app=backend` pods must reject all ingress traffic.
2. The only ingress traffic that should be allowed to `app=backend` pods is from pods labeled
   `app=frontend`, on TCP port 8080.
3. `app=backend` pods must retain the ability to resolve DNS (UDP and TCP port 53 to the
   `kube-system` namespace) — do not leave them unable to resolve names as a side effect of your
   egress policy, if you choose to add one.

A pod labeled `app=frontend` and a pod with no matching labels (`app=intruder`) both already exist
in the namespace for you to test against.

---

## Task 13 — Ingress with two path-based routes (6 points)

**Context:** `kubectl config use-context k8s-charlie-admin`, namespace `shop`

An `ingress-nginx` controller is already installed and healthy in this cluster (`IngressClass` name:
`nginx`). Create an Ingress named `shop-ingress` for host `shop.example.local` that routes:
- path `/api` (prefix match) → Service `api-svc` port `8080`
- path `/` (prefix match) → Service `frontend-svc` port `80`

Both target Services already exist and have healthy endpoints.

---

## Task 14 — Taint a node and schedule a tolerating workload (5 points)

**Context:** `kubectl config use-context k8s-delta-admin`

Taint node `delta-wk2` so that no ordinary workload is scheduled there by default. Then create a
Pod named `batch-runner` (image `busybox`, running `sleep 3600`) that tolerates that exact taint
**and** is guaranteed to land specifically on `delta-wk2` (not merely permitted to land there).

---

## Task 15 — Required node affinity for a Deployment (5 points)

**Context:** `kubectl config use-context k8s-delta-admin`, namespace `finance`

The `ledger` Deployment (3 replicas) must run **only** on nodes labeled `tier=secure`. No node in
the cluster currently carries that label. Label the single most appropriate node `tier=secure` and
configure `ledger` with a **required** node affinity rule so all 3 replicas land there.

---

## Task 16 — Diagnose a Pod stuck Pending (5 points)

**Context:** `kubectl config use-context k8s-delta-admin`, namespace `finance`

Pod `audit-job` has been `Pending` for a long time. Diagnose the exact reason using the pod's
events and fix it so the pod reaches `Running`. Do not loosen any existing node taint or cluster
security constraint that isn't actually the cause — find and fix the real, specific reason this
one pod cannot schedule.

---

## Task 17 — Static PersistentVolume and matching PVC (5 points)

**Context:** `kubectl config use-context k8s-echo-admin`

Create a `PersistentVolume` named `pv-reports-01` backed by `hostPath` at `/mnt/data/reports`, with
capacity `500Mi`, access mode `ReadWriteOnce`, reclaim policy `Retain`, and `storageClassName:
manual`. Then create a `PersistentVolumeClaim` named `reports-claim` in namespace `reporting`
requesting `200Mi`, `ReadWriteOnce`, `storageClassName: manual`, such that it binds to
`pv-reports-01` specifically (not to any other PV that might exist in the cluster).

---

## Task 18 — Fix an ambiguous default StorageClass (5 points)

**Context:** `kubectl config use-context k8s-echo-admin`

Two StorageClasses, `fast` and `standard`, are both currently annotated as the default class,
which makes default-class selection ambiguous for any PVC that omits `storageClassName`. Fix this
so that **only** `standard` remains the default. Then create a test PVC with no `storageClassName`
set and confirm it binds using `standard`.

---

# Solutions & Scoring

*Do not read past this point until you've finished your attempt.*

---

## Task 1 — Worker node NotReady (5 points)

**Solution**
```bash
kubectl config use-context k8s-alpha-admin
kubectl describe node alpha-wk1          # check Conditions/Reason at the bottom
ssh alpha-wk1                            # or your lab's equivalent root-shell mechanism
systemctl status kubelet containerd      # identify which is down/misconfigured
journalctl -u kubelet -n 100 --no-pager  # look for the specific error (bad flag, bad config, etc.)
cat /var/lib/kubelet/kubeadm-flags.env   # check for corruption/wrong container-runtime-endpoint
cat /var/lib/kubelet/config.yaml         # check for invalid YAML / wrong cgroupDriver
# fix whatever file/flag is broken, then:
systemctl daemon-reload
systemctl restart containerd kubelet
```

**Verification**
```bash
kubectl get node alpha-wk1               # STATUS = Ready
kubectl get pods -A -o wide --field-selector spec.nodeName=alpha-wk1
# previously-stuck pods on this node should now be Running
```

**Points:** 5

---

## Task 2 — Control-plane component crash-looping (5 points)

**Solution**
```bash
kubectl config use-context k8s-alpha-admin
ssh alpha-cp1
crictl ps -a | grep controller-manager           # confirm restart/exit pattern
crictl logs <most-recently-exited-container-id>  # exact error, e.g. hostPath mount failure
cat /etc/kubernetes/manifests/kube-controller-manager.yaml
vi /etc/kubernetes/manifests/kube-controller-manager.yaml
# fix the broken field (e.g. a hostPath volume path pointing at a nonexistent directory,
# a typo'd flag, or a bad image tag) and save — kubelet reconciles the static pod automatically
```

**Verification**
```bash
crictl ps -a | grep controller-manager   # Running, stable (non-incrementing) restart count
kubectl create deployment verify-cm --image=nginx -n default
kubectl get rs -l app=verify-cm -n default   # a ReplicaSet actually gets created -> controller-manager is reconciling
kubectl delete deployment verify-cm -n default
```

**Points:** 5

---

## Task 3 — CrashLoopBackOff application pod (5 points)

**Solution**
```bash
kubectl config use-context k8s-alpha-admin
kubectl -n retail describe pod -l app=cart | grep -A5 "Last State"   # look for Reason: OOMKilled
kubectl -n retail logs -l app=cart --previous
kubectl -n retail edit deployment cart
# raise spec.template.spec.containers[].resources.limits.memory to a sufficient value
```

**Verification**
```bash
kubectl -n retail rollout status deployment/cart
kubectl -n retail get pods -l app=cart -w    # watch restart count stay flat for ~60s
```

**Points:** 5

---

## Task 4 — ImagePullBackOff (5 points)

**Solution**
```bash
kubectl config use-context k8s-alpha-admin
kubectl -n retail describe pod -l app=catalog | tail -20   # confirm exact pull error / bad tag
kubectl -n retail set image deployment/catalog catalog=nginx:1.27
kubectl -n retail rollout status deployment/catalog
```

**Verification**
```bash
kubectl -n retail get pods -l app=catalog        # all Running
kubectl -n retail describe pod -l app=catalog | grep -iE "err|fail|backoff"   # no pull-error events
```

**Points:** 5

---

## Task 5 — Service not reaching Pods (5 points)

**Solution**
```bash
kubectl config use-context k8s-alpha-admin
kubectl -n retail get pods --show-labels | grep catalog
kubectl -n retail get svc catalog-svc -o yaml | grep -A3 selector
kubectl -n retail get endpoints catalog-svc     # confirm empty -> selector mismatch
kubectl -n retail edit svc catalog-svc
# fix spec.selector to app: catalog (matching the pods' actual label)
# also confirm spec.ports[].targetPort is 8080, matching the container's listening port
```

**Verification**
```bash
kubectl -n retail get endpoints catalog-svc     # lists pod IPs, not empty
kubectl -n retail run tmp --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- catalog-svc.retail.svc.cluster.local:80
```

**Points:** 5

---

## Task 6 — Cluster-wide DNS resolution failure (5 points)

**Solution**
```bash
kubectl config use-context k8s-alpha-admin
kubectl -n kube-system get pods -l k8s-app=kube-dns    # confirm 0/0 replicas or crash-looping
kubectl -n kube-system get deployment coredns          # REPLICAS column shows 0
kubectl -n kube-system scale deployment coredns --replicas=2
kubectl -n kube-system get pods -l k8s-app=kube-dns -w  # wait for Running/Ready
```

**Verification**
```bash
kubectl run dnstest --rm -it --image=busybox:1.36 --restart=Never -- nslookup kubernetes.default
kubectl run dnstest2 --rm -it --image=busybox:1.36 --restart=Never -- nslookup google.com
```

**Points:** 5

---

## Task 7 — Take an etcd snapshot (6 points)

**Solution**
```bash
kubectl config use-context k8s-bravo-admin
ssh bravo-cp1
ETCDCTL_API=3 etcdctl snapshot save /opt/backups/etcd-snapshot-bravo.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

**Verification**
```bash
ETCDCTL_API=3 etcdctl snapshot status /opt/backups/etcd-snapshot-bravo.db --write-out=table
# non-zero "hash", "revision", and "total keys" columns confirm a valid, readable snapshot
ls -la /opt/backups/etcd-snapshot-bravo.db
```

**Points:** 6

---

## Task 8 — Restore a cluster from an etcd snapshot (7 points)

**Solution**
```bash
kubectl config use-context k8s-bravo-admin
ssh bravo-cp1
# stop etcd from being live-reconciled while you restore
mv /etc/kubernetes/manifests/etcd.yaml /tmp/etcd.yaml.bak
etcdutl snapshot restore /opt/backups/etcd-pre-incident.db \
  --data-dir=/var/lib/etcd-restored
# point the static pod manifest's data-dir at the newly restored directory
vi /tmp/etcd.yaml.bak    # change --data-dir and the matching hostPath.path to /var/lib/etcd-restored
mv /tmp/etcd.yaml.bak /etc/kubernetes/manifests/etcd.yaml
```

**Verification**
```bash
crictl ps | grep etcd                       # fresh, stable container
kubectl get ns pre-incident                 # exists again
kubectl get pods -A                         # cluster overall responsive
# anything legitimately created after the snapshot was taken is now gone -- expected, not a bug
```

**Points:** 7

---

## Task 9 — Certificate failure diagnosis and renewal (6 points)

**Solution**
```bash
kubectl config use-context k8s-bravo-admin
ssh bravo-cp1
kubeadm certs check-expiration                 # find the expired/near-expired cert(s)
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates -subject
kubeadm certs renew apiserver                  # or: kubeadm certs renew all
# force the static pod to pick up the new cert (renewal alone doesn't restart it):
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
# if your own kubectl access was the thing failing, also re-sync admin.conf:
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
```

**Verification**
```bash
kubeadm certs check-expiration      # new, later expiry date for the renewed cert(s)
kubectl get nodes                   # succeeds with no x509 errors
crictl logs $(crictl ps -q --name kube-apiserver) | grep -i x509   # no expiry/x509 errors
```

**Points:** 6

---

## Task 10 — Least-privilege RBAC for a ServiceAccount (6 points)

**Solution**
```bash
kubectl config use-context k8s-bravo-admin
kubectl -n ci create serviceaccount deploy-bot
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-log-reader
  namespace: ci
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
EOF
kubectl -n ci create rolebinding deploy-bot-pod-log-reader \
  --role=pod-log-reader --serviceaccount=ci:deploy-bot
```
(`kubectl create role pod-log-reader --verb=get,list,watch --resource=pods --verb=get
--resource=pods/log` looks like it would produce the two rules above, but it does not: `kubectl
create role` groups every `--resource` that shares an API group into a *single* rule and applies
the full, deduplicated union of every `--verb` given to that whole group. Because `pods` and
`pods/log` are both in the core API group, the generated Role would grant `get,list,watch` on
**both** — i.e. `pods/log` would end up with `list`/`watch` it should never have. Write the Role as
explicit YAML with two separate `rules[]` entries, as above, to get exactly the permissions asked
for.)

**Verification**
```bash
kubectl auth can-i get pods --as=system:serviceaccount:ci:deploy-bot -n ci        # yes
kubectl auth can-i list pods --as=system:serviceaccount:ci:deploy-bot -n ci       # yes
kubectl auth can-i watch pods --as=system:serviceaccount:ci:deploy-bot -n ci      # yes
kubectl auth can-i get pods/log --as=system:serviceaccount:ci:deploy-bot -n ci    # yes
kubectl auth can-i list pods/log --as=system:serviceaccount:ci:deploy-bot -n ci   # no
kubectl auth can-i watch pods/log --as=system:serviceaccount:ci:deploy-bot -n ci  # no
kubectl auth can-i delete pods --as=system:serviceaccount:ci:deploy-bot -n ci     # no
kubectl auth can-i get pods --as=system:serviceaccount:ci:deploy-bot -n default   # no
```

**Points:** 6

---

## Task 11 — Expose a Deployment and fix a broken Service (6 points)

**Solution**
```bash
kubectl config use-context k8s-charlie-admin
kubectl -n shop expose deployment frontend --name=frontend-svc --port=80 --target-port=8080 --type=ClusterIP

kubectl -n shop get svc legacy-frontend -o yaml | grep -A3 selector
kubectl -n shop get pods --show-labels | grep frontend
kubectl -n shop edit svc legacy-frontend
# fix spec.selector to match app: frontend (and confirm targetPort matches 8080)
```

**Verification**
```bash
kubectl -n shop get endpoints frontend-svc legacy-frontend    # both list pod IPs
kubectl -n shop run tmp --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- frontend-svc.shop.svc.cluster.local:80
kubectl -n shop run tmp2 --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- legacy-frontend.shop.svc.cluster.local
```

**Points:** 6

---

## Task 12 — NetworkPolicy: default-deny plus scoped allow (8 points)

**Solution**
```bash
kubectl config use-context k8s-charlie-admin
cat <<'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-default-deny
  namespace: shop
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: [Ingress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: shop
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
EOF
```
(The `backend-default-deny` policy alone would already deny all ingress; `backend-allow-frontend`
supplies the one allowed ingress path and, because it also declares `Egress` in `policyTypes`,
supplies the mandatory DNS carve-out. Two policies are shown for clarity — a single combined
policy achieves the same result and is equally correct.)

**Verification**
```bash
kubectl -n shop exec deploy/frontend -- wget -qO- --timeout=3 backend:8080   # succeeds
kubectl -n shop exec <intruder-pod> -- wget -qO- --timeout=3 backend:8080    # times out
kubectl -n shop exec <a-backend-pod> -- nslookup kubernetes.default          # still resolves
```

**Points:** 8

---

## Task 13 — Ingress with two path-based routes (6 points)

**Solution**
```bash
kubectl config use-context k8s-charlie-admin
kubectl -n shop create ingress shop-ingress \
  --class=nginx \
  --rule="shop.example.local/api*=api-svc:8080" \
  --rule="shop.example.local/*=frontend-svc:80"
```
Or via YAML:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop-ingress
  namespace: shop
spec:
  ingressClassName: nginx
  rules:
    - host: shop.example.local
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-svc
                port:
                  number: 8080
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-svc
                port:
                  number: 80
```

**Verification**
```bash
kubectl -n shop describe ingress shop-ingress   # both paths show resolved, non-empty backends
curl -H "Host: shop.example.local" http://<ingress-controller-ip>/api
curl -H "Host: shop.example.local" http://<ingress-controller-ip>/
```

**Points:** 6

---

## Task 14 — Taint a node and schedule a tolerating workload (5 points)

**Solution**
```bash
kubectl config use-context k8s-delta-admin
kubectl taint nodes delta-wk2 workload=batch:NoSchedule
```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-runner
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
                values: [delta-wk2]
  containers:
    - name: busybox
      image: busybox
      command: ["sleep", "3600"]
```

**Verification**
```bash
kubectl get pod batch-runner -o wide     # NODE = delta-wk2
kubectl run untainted-check --image=nginx --restart=Never
kubectl get pod untainted-check -o wide  # never lands on delta-wk2
```

**Points:** 5

---

## Task 15 — Required node affinity for a Deployment (5 points)

**Solution**
```bash
kubectl config use-context k8s-delta-admin
kubectl get nodes    # pick one node, e.g. delta-wk1
kubectl label nodes delta-wk1 tier=secure
kubectl -n finance patch deployment ledger --type merge -p '{
  "spec": {"template": {"spec": {"affinity": {"nodeAffinity": {
    "requiredDuringSchedulingIgnoredDuringExecution": {
      "nodeSelectorTerms": [{
        "matchExpressions": [{"key": "tier", "operator": "In", "values": ["secure"]}]
      }]
    }
  }}}}}
}'
```

**Verification**
```bash
kubectl -n finance rollout status deployment/ledger
kubectl -n finance get pods -l app=ledger -o wide   # all 3 on delta-wk1
```

**Points:** 5

---

## Task 16 — Diagnose a Pod stuck Pending (5 points)

**Solution**
```bash
kubectl config use-context k8s-delta-admin
kubectl -n finance describe pod audit-job | grep -A5 Events
# Events show something like:
# "0/3 nodes are available: 3 node(s) didn't match Pod's node selector"
kubectl -n finance get pod audit-job -o jsonpath='{.spec.nodeSelector}'
kubectl get nodes --show-labels
# the pod's nodeSelector references a label value that no node actually carries (e.g. a typo)
kubectl -n finance edit pod audit-job     # nodeSelector is immutable on a running Pod -- if so:
kubectl -n finance get pod audit-job -o yaml > /tmp/audit-job.yaml
# edit /tmp/audit-job.yaml: fix spec.nodeSelector to the correct existing label/value
kubectl -n finance delete pod audit-job
kubectl -n finance apply -f /tmp/audit-job.yaml
```

**Verification**
```bash
kubectl -n finance get pod audit-job -o wide   # Running, NODE assigned
kubectl -n finance describe pod audit-job | grep -i FailedScheduling   # no more matches
```

**Points:** 5

---

## Task 17 — Static PersistentVolume and matching PVC (5 points)

**Solution**
```bash
kubectl config use-context k8s-echo-admin
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-reports-01
spec:
  capacity:
    storage: 500Mi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data/reports
EOF

kubectl create namespace reporting --dry-run=client -o yaml | kubectl apply -f -

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: reports-claim
  namespace: reporting
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 200Mi
  storageClassName: manual
  volumeName: pv-reports-01
EOF
```
(Matching `storageClassName`, `accessModes`, and sufficient capacity is normally enough for the
PVC to bind to *a* PV of that class, but if any other `manual`-class PV with enough capacity ever
exists in the cluster, capacity/class matching alone doesn't guarantee it picks `pv-reports-01`
specifically. Setting `spec.volumeName: pv-reports-01` on the PVC forces an explicit 1:1 bind to
that exact PV.)

**Verification**
```bash
kubectl get pv pv-reports-01                          # STATUS = Bound
kubectl -n reporting get pvc reports-claim             # STATUS = Bound, VOLUME = pv-reports-01
```

**Points:** 5

---

## Task 18 — Fix an ambiguous default StorageClass (5 points)

**Solution**
```bash
kubectl config use-context k8s-echo-admin
kubectl get sc                    # confirm both fast and standard show (default)
kubectl patch storageclass fast -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
kubectl patch storageclass standard -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

kubectl create namespace sc-test --dry-run=client -o yaml | kubectl apply -f -
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: default-class-test
  namespace: sc-test
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Mi
EOF
```

**Verification**
```bash
kubectl get sc                                          # only "standard" shows (default)
kubectl -n sc-test get pvc default-class-test -o jsonpath='{.spec.storageClassName}'
# should print "standard"
```

**Points:** 5

---

## Points Recap

| # | Task | Domain | Points |
|---|---|---|---|
| 1 | Worker node NotReady | Troubleshooting | 5 |
| 2 | Control-plane component crash-looping | Troubleshooting | 5 |
| 3 | CrashLoopBackOff application pod | Troubleshooting | 5 |
| 4 | ImagePullBackOff | Troubleshooting | 5 |
| 5 | Service not reaching Pods | Troubleshooting | 5 |
| 6 | Cluster-wide DNS resolution failure | Troubleshooting | 5 |
| 7 | Take an etcd snapshot | Cluster Architecture | 6 |
| 8 | Restore a cluster from an etcd snapshot | Cluster Architecture | 7 |
| 9 | Certificate failure diagnosis and renewal | Cluster Architecture | 6 |
| 10 | Least-privilege RBAC for a ServiceAccount | Cluster Architecture | 6 |
| 11 | Expose a Deployment and fix a broken Service | Services & Networking | 6 |
| 12 | NetworkPolicy: default-deny plus scoped allow | Services & Networking | 8 |
| 13 | Ingress with two path-based routes | Services & Networking | 6 |
| 14 | Taint a node and schedule a tolerating workload | Workloads & Scheduling | 5 |
| 15 | Required node affinity for a Deployment | Workloads & Scheduling | 5 |
| 16 | Diagnose a Pod stuck Pending | Workloads & Scheduling | 5 |
| 17 | Static PersistentVolume and matching PVC | Storage | 5 |
| 18 | Fix an ambiguous default StorageClass | Storage | 5 |
| | **Total** | | **100** |

**Domain totals:** Troubleshooting 30 · Cluster Architecture 25 · Services & Networking 20 ·
Workloads & Scheduling 15 · Storage 10 — matching the official CKA weighting exactly.

**Pass mark: 66/100.**
