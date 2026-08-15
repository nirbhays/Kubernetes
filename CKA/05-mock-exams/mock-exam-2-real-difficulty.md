# CKA Mock Exam 2 — Real-Exam Difficulty

*Original material. Every task below is built from the general CKA competencies and failure patterns documented in `CKA/01-exam-snapshot-and-priorities.md` and `CKA/02-topics/`, not from any specific remembered real-exam question. Domain point allocation mirrors the official weighting as closely as integer task scoring allows: Troubleshooting 30, Cluster Architecture/Installation/Configuration 25, Services & Networking 20, Workloads & Scheduling 15, Storage 10.*

---

# Instructions

**Time limit:** 2 hours (120 minutes), matching the real CKA. With 19 tasks this is roughly 6–7 minutes/task on average — consistent with the community-reported real-exam time pressure cited in `01-exam-snapshot-and-priorities.md`. Some tasks are worth more points and warrant more time; budget accordingly rather than spending equal time on every task.

**Scoring:** Each task has a point value shown in brackets after its title. Point values are weighted toward the higher-value domains (Troubleshooting and Cluster Architecture carry the most points, Storage the fewest), exactly mirroring the official domain weighting. All task points sum to **100**. The passing score is **66%** (66 points), identical to the real CKA per the LF FAQ.

**Context-switching discipline:** This mock simulates multiple clusters, exactly as the real exam frequently does. Every task states the exact `kubectl config use-context <name>` command to run first — **run it before touching anything else in that task**, even if the previous task used the same context. Forgetting to switch context and editing the wrong cluster is one of the most common self-inflicted real-exam failures.

**Simulated environment topology** (assume these clusters and nodes exist and are reachable; `k` is pre-aliased to `kubectl` exactly as on the real exam):

| Context name | Nodes | Notes |
|---|---|---|
| `kubeadm-prod01` | control-plane `prod01-cp1`; workers `prod01-worker1`, `prod01-worker2` | General-purpose cluster, containerd runtime, Kubernetes v1.35.x, `ingress-nginx` pre-installed |
| `kubeadm-ha01` | control-plane `ha01-cp1`, `ha01-cp2`; worker `ha01-worker1` | HA control-plane cluster, currently on Kubernetes v1.35.x, used for architecture/etcd/cert/upgrade tasks |
| `kubeadm-edge01` | control-plane `edge01-cp1`; worker `edge01-worker1` | Small edge cluster; `edge01-worker1` has a deliberately broken component for one troubleshooting task |
| `kubeadm-secure01` | control-plane `secure01-cp1`; worker `secure01-worker1` | Used for RBAC / NetworkPolicy / DNS security-adjacent tasks |

No solutions or hints beyond the task text appear below this point until the final **Solutions & Scoring** section. Do not scroll ahead.

---

# Tasks

## Task 1 — Rolling update with a forced rollback [5 points]
*(Workloads & Scheduling)*

```
kubectl config use-context kubeadm-prod01
```

In namespace `shop` there is an existing Deployment named `checkout` running image `nginx:1.25` with container name `nginx`. Perform the following in order:

1. Update `checkout` to image `nginx:1.27` and confirm the rollout completes successfully.
2. Immediately update `checkout` again to the image tag `nginx:1.27-doesnotexist`.
3. Detect that this second rollout is stuck (do not wait out any default timeout blindly), and roll back `checkout` to the last known-good revision.
4. Leave `checkout` in a stable, fully-`Ready` state running `nginx:1.27`.

---

## Task 2 — etcd snapshot backup [7 points]
*(Cluster Architecture, Installation & Configuration)*

```
kubectl config use-context kubeadm-ha01
```

On control-plane node `ha01-cp1`, take a consistent backup of the cluster's etcd data store and save the snapshot to `/opt/backups/ha01-etcd.db` on that node. Confirm the snapshot file is valid and non-empty using the appropriate tool before considering this task complete. Do not alter the running etcd cluster in any way.

---

## Task 3 — Application pod crash-looping [5 points]
*(Troubleshooting)*

```
kubectl config use-context kubeadm-prod01
```

In namespace `shop`, a Pod named `receipts-worker` (created directly, not via a controller) is stuck in `CrashLoopBackOff`. Diagnose the root cause and fix it so the Pod reaches a stable `Running` state with a restart count that stops climbing. Do not simply delete and recreate the Pod with a different, unrelated image — fix the actual defect.

---

## Task 4 — Expose a Deployment via a ClusterIP Service [4 points]
*(Services & Networking)*

```
kubectl config use-context kubeadm-prod01
```

In namespace `reports`, a Deployment named `reports-api` runs 3 replicas of a container listening on port `8080`, labeled `app=reports-api`. Create a Service named `reports-api-svc` of type `ClusterIP` that exposes port `80` and correctly routes to the Pods' listening port. Confirm the Service has populated endpoints and that a request from a temporary Pod to `reports-api-svc.reports.svc.cluster.local:80` succeeds.

---

## Task 5 — Static provisioning: PV, PVC, and a consuming Pod [5 points]
*(Storage)*

```
kubectl config use-context kubeadm-prod01
```

1. Create namespace `data-drill`.
2. Create a PersistentVolume named `pv-exam01` backed by `hostPath: /mnt/examdata`, capacity `500Mi`, access mode `ReadWriteOnce`, reclaim policy `Retain`, and `storageClassName: manual`.
3. Create a PersistentVolumeClaim named `pvc-exam01` in `data-drill` requesting `300Mi`, access mode `ReadWriteOnce`, `storageClassName: manual`, such that it binds specifically to `pv-exam01`.
4. Create a Pod named `data-pod` in `data-drill` running `busybox` (command: sleep for a long duration, e.g. `sleep 3600`) that mounts `pvc-exam01` at `/data`.
5. Prove persistence: write a file into `/data`, delete `data-pod`, recreate an identical Pod, and confirm the file is still present.

---

## Task 6 — Certificate expiration check and renewal [5 points]
*(Cluster Architecture, Installation & Configuration)*

```
kubectl config use-context kubeadm-ha01
```

On control-plane node `ha01-cp1`, the cluster's certificates have not been renewed in a long time and several are close to expiry. Without touching the cluster CA itself:

1. Identify which certificates are nearest to expiry.
2. Renew all kubeadm-managed certificates on this node.
3. Ensure every static-pod control-plane component that holds a now-stale certificate in memory is restarted so it picks up the renewed certificate.
4. Confirm `kubectl` (using `admin.conf`) still works with no `x509` errors anywhere afterward.

---

## Task 7 — Worker node stuck NotReady [7 points]
*(Troubleshooting)*

```
kubectl config use-context kubeadm-edge01
```

Node `edge01-worker1` is showing `NotReady`. Bring it back to a healthy `Ready` state **without rebooting the node and without running `kubeadm join` again**. Diagnose using the node's own systemd/CRI-level tooling before making any change, and confirm afterward that Pods can schedule and run successfully on this node again.

---

## Task 8 — Taint a node and schedule a matching workload [5 points]
*(Workloads & Scheduling)*

```
kubectl config use-context kubeadm-prod01
```

1. Taint node `prod01-worker2` with `dedicated=batch:NoSchedule`.
2. Create a Deployment named `batch-runner` (2 replicas, image `busybox`, command that sleeps for a long duration, e.g. `sleep 3600`) that both tolerates this exact taint and is constrained via node affinity to run **only** on `prod01-worker2`.
3. Confirm both replicas land on `prod01-worker2`.
4. Confirm a separate, ordinary test Pod (no toleration) scheduled around the same time never lands on `prod01-worker2`.

---

## Task 9 — Namespace network segmentation with NetworkPolicy [6 points]
*(Services & Networking)*

```
kubectl config use-context kubeadm-secure01
```

In namespace `secure-app`, three Pods exist: `frontend` (label `app=frontend`), `backend` (label `app=backend`, listens on port `8080`), and `scanner` (no relevant labels, simulating an untrusted workload). Implement network policy such that:

1. `backend` accepts ingress **only** from Pods labeled `app=frontend`, on port `8080` — all other ingress to `backend` must be denied.
2. `backend` may make egress connections only to DNS (port 53, TCP and UDP, to the `kube-system` namespace) — no other egress is permitted from `backend`.
3. Confirm `frontend → backend:8080` succeeds, `scanner → backend:8080` times out, and `backend`'s own DNS lookups (e.g. `nslookup kubernetes.default`) still succeed.

---

## Task 10 — Join a new worker node to an HA cluster [4 points]
*(Cluster Architecture, Installation & Configuration)*

```
kubectl config use-context kubeadm-ha01
```

A new node, `ha01-worker2`, has containerd and the matching `kubeadm`/`kubelet`/`kubectl` packages already installed but has not yet joined the cluster. Generate a fresh join token and CA cert hash from the cluster (do not reuse any stale/expired token), and join `ha01-worker2` to `kubeadm-ha01` as a worker node. Confirm it reaches `Ready` status.

---

## Task 11 — Control-plane component crash-looping [6 points]
*(Troubleshooting)*

```
kubectl config use-context kubeadm-ha01
```

On control-plane node `ha01-cp2`, `kube-controller-manager` is crash-looping. `kubectl` against this cluster still works (via `ha01-cp1`), but reconciliation driven by the controller-manager on `ha01-cp2` is not happening when it holds leadership. Diagnose the root cause at the node level (this is a static pod problem, not something `kubectl edit` can fix directly) and restore `kube-controller-manager` to a stable, non-restarting `Running` state on `ha01-cp2`.

---

## Task 12 — Diagnose a Pending PersistentVolumeClaim [5 points]
*(Storage)*

```
kubectl config use-context kubeadm-prod01
```

Namespace `data-drill2` contains a PersistentVolumeClaim named `pvc-broken` that has been stuck `Pending` for a while. **Do not delete or recreate `pvc-broken`.** Diagnose why it isn't binding and resolve the issue by creating and/or fixing whatever PersistentVolume(s) are needed so that `pvc-broken` transitions to `Bound`.

---

## Task 13 — Ingress path-based routing [5 points]
*(Services & Networking)*

```
kubectl config use-context kubeadm-prod01
```

In namespace `shop-web`, two Deployments/Services already exist: `catalog-v1` (Service `catalog-v1-svc`, port `8080`) and `catalog-v2` (Service `catalog-v2-svc`, port `8081`). Using the pre-installed `nginx` ingress controller, create a single Ingress named `catalog-ingress` on host `catalog.demo.local` that routes:

- `/v1` (and anything under it) to `catalog-v1-svc:8080`
- `/v2` (and anything under it) to `catalog-v2-svc:8081`

Confirm both paths resolve to their correct backend via `curl` with the appropriate `Host` header, and that `kubectl describe ingress` shows both backends with populated endpoints.

---

## Task 14 — Upgrade the HA cluster by one minor version [5 points]
*(Cluster Architecture, Installation & Configuration)*

```
kubectl config use-context kubeadm-ha01
```

`kubeadm-ha01` is currently running Kubernetes v1.35.x on all nodes. Upgrade the entire cluster to the latest available v1.36.x patch release, following the correct kubeadm sequencing:

1. `ha01-cp1` first (the control-plane node kubeadm treats as primary for the upgrade).
2. `ha01-cp2` next.
3. `ha01-worker1` last.

Each node must be properly drained before its own `kubelet`/`kubectl` package upgrade and uncordoned afterward. Do not skip a minor version. Confirm via `kubectl get nodes -o wide` that all three nodes report the new version and are `Ready`/schedulable at the end.

---

## Task 15 — Service exists but traffic never reaches the Pods [6 points]
*(Troubleshooting)*

```
kubectl config use-context kubeadm-prod01
```

In namespace `shop`, users report that `webshop-svc` (backing the `webshop` Deployment) is completely unreachable, even though both the Service and the Deployment's Pods appear individually healthy in `kubectl get`. Diagnose and fix the issue so that a request from a temporary Pod to `webshop-svc.shop.svc.cluster.local` succeeds. There may be more than one contributing misconfiguration — after each fix, re-verify before declaring the task complete.

---

## Task 16 — Diagnose a Deployment stuck with Pending Pods [5 points]
*(Workloads & Scheduling)*

```
kubectl config use-context kubeadm-prod01
```

In namespace `shop`, a Deployment named `analytics` has 3 desired replicas but 0 are `Running` — all Pods are `Pending`. Without loosening the Deployment's intended placement requirements beyond what's necessary, diagnose the exact cause(s) from the Pods' own scheduling events and get all 3 replicas to a `Running` state.

---

## Task 17 — Fix a ServiceAccount's insufficient RBAC permissions [4 points]
*(Cluster Architecture, Installation & Configuration)*

```
kubectl config use-context kubeadm-secure01
```

In namespace `billing`, a monitoring agent authenticates as ServiceAccount `billing-agent` and needs to `list` and `watch` Pods (it currently only has `get`, which is insufficient — its client is failing with `Forbidden` errors on `list`/`watch` calls). **Without deleting or recreating the ServiceAccount or its RoleBinding**, grant exactly the additional permissions needed — no more, no less (do not grant it `delete`, `create`, or any other verb it doesn't need).

---

## Task 18 — CNI misconfiguration causing stuck pods on one node [5 points]
*(Services & Networking)*

```
kubectl config use-context kubeadm-prod01
```

Node `prod01-worker2` shows `Ready`, but every new Pod scheduled onto it (including a freshly created test Pod you should create as part of diagnosis) gets stuck in `ContainerCreating` indefinitely. Pods on `prod01-worker1` are unaffected. Diagnose the CNI-layer root cause on `prod01-worker2` and fix it so new Pods scheduled there reach `Running` normally.

---

## Task 19 — Cluster DNS resolution failing for one namespace [6 points]
*(Troubleshooting)*

```
kubectl config use-context kubeadm-secure01
```

Pods in namespace `checkout-ns` cannot resolve any DNS names — internal Service names or external hosts. CoreDNS itself, and DNS resolution from other namespaces, both appear completely healthy. Diagnose why resolution fails specifically for `checkout-ns` and fix it so that `nslookup kubernetes.default` (and an external lookup) both succeed from a test Pod in `checkout-ns`.

---

# Solutions & Scoring

*Verification commands below assume `k` is aliased to `kubectl` as stated in the Instructions. Where a task's underlying seed fault is described for solution completeness, remember on the real exam you will not be told the seed fault in advance — the diagnostic sequence shown is the actual skill being tested.*

---

## Task 1 — Rolling update with a forced rollback [5 points]

**Solution:**
```bash
k set image deployment/checkout nginx=nginx:1.27 -n shop
k rollout status deployment/checkout -n shop --timeout=60s

k set image deployment/checkout nginx=nginx:1.27-doesnotexist -n shop
k rollout status deployment/checkout -n shop --timeout=30s || k rollout undo deployment/checkout -n shop
k rollout status deployment/checkout -n shop --timeout=60s
```

**Verify:**
```bash
k get deploy checkout -n shop                                                   # READY 3/3 (or whatever replica count exists)
k get deploy checkout -n shop -o jsonpath='{.spec.template.spec.containers[0].image}'   # nginx:1.27
k get pods -n shop -l app=checkout                                              # all Running, no ImagePullBackOff
```

**Points: 5**

---

## Task 2 — etcd snapshot backup [7 points]

**Solution (run on `ha01-cp1`):**
```bash
sudo etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/backups/ha01-etcd.db

sudo etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot status /opt/backups/ha01-etcd.db --write-out=table
```

**Verify:** `snapshot status` returns a table with a non-zero `HASH`, `REVISION`, and `TOTAL KEYS`; `ls -lh /opt/backups/ha01-etcd.db` shows a non-trivial file size (not 0 bytes). Grading note: using `etcdutl` for the save step, or omitting any of the three TLS flags, is a scoring failure on the real exam even if a file gets written — the flags/tool must be exactly right.

**Points: 7**

---

## Task 3 — Application pod crash-looping [5 points]

**Seed fault (for context):** the Pod's `command`/`args` reference a script path that does not exist inside the `busybox`/similar image, so the container exits immediately every time.

**Solution:**
```bash
k describe pod receipts-worker -n shop           # Events / Last State: Terminated, exit code
k logs receipts-worker -n shop --previous        # confirms "no such file or directory" or similar

k get pod receipts-worker -n shop -o yaml > /tmp/receipts-worker.yaml
# edit: fix spec.containers[0].command/args to a valid, existing entrypoint
k delete pod receipts-worker -n shop
k apply -f /tmp/receipts-worker.yaml
```

**Verify:**
```bash
k get pod receipts-worker -n shop -w         # watch ~60s: Running, RESTARTS not climbing
k get pod receipts-worker -n shop -o jsonpath='{.status.containerStatuses[0].restartCount}'
```

**Points: 5**

---

## Task 4 — Expose a Deployment via a ClusterIP Service [4 points]

**Solution:**
```bash
k expose deployment reports-api -n reports --name=reports-api-svc --port=80 --target-port=8080
```

**Verify:**
```bash
k get endpoints reports-api-svc -n reports                 # 3 pod IPs listed
k run tmp --rm -it --image=busybox:1.36 -n reports --restart=Never -- \
  wget -qO- reports-api-svc.reports.svc.cluster.local:80
```

**Points: 4**

---

## Task 5 — Static provisioning: PV, PVC, and a consuming Pod [5 points]

**Solution:**
```bash
k create ns data-drill

cat <<'EOF' | k apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-exam01
spec:
  capacity:
    storage: 500Mi
  accessModes: ["ReadWriteOnce"]
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/examdata
EOF

cat <<'EOF' | k apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-exam01
  namespace: data-drill
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests:
      storage: 300Mi
EOF

cat <<'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: data-pod
  namespace: data-drill
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: pvc-exam01
EOF
```

**Verify:**
```bash
k get pv pv-exam01                                  # Bound
k get pvc -n data-drill pvc-exam01                  # Bound, VOLUME=pv-exam01
k exec -n data-drill data-pod -- sh -c 'echo hello > /data/f && cat /data/f'
k delete pod data-pod -n data-drill
# recreate the same Pod manifest
k exec -n data-drill data-pod -- cat /data/f        # still prints "hello"
```

**Points: 5**

---

## Task 6 — Certificate expiration check and renewal [5 points]

**Solution (on `ha01-cp1`):**
```bash
sudo kubeadm certs check-expiration
sudo kubeadm certs renew all
# renew all also rotates the etcd-server/etcd-peer/etcd-healthcheck-client certs, so etcd
# itself must be recycled too, not just the apiserver/controller-manager/scheduler:
# force every static pod holding a stale cert to restart:
sudo mv /etc/kubernetes/manifests/etcd.yaml /tmp/ && sleep 5 && sudo mv /tmp/etcd.yaml /etc/kubernetes/manifests/
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
sudo mv /etc/kubernetes/manifests/kube-controller-manager.yaml /tmp/ && sleep 5 && sudo mv /tmp/kube-controller-manager.yaml /etc/kubernetes/manifests/
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/ && sleep 5 && sudo mv /tmp/kube-scheduler.yaml /etc/kubernetes/manifests/
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
```

**Verify:**
```bash
sudo kubeadm certs check-expiration          # all future dates, ~1 year out
kubectl get nodes                            # succeeds with no x509 errors
sudo crictl logs $(sudo crictl ps -q --name kube-apiserver) 2>&1 | grep -i x509   # no output
sudo crictl logs $(sudo crictl ps -q --name etcd) 2>&1 | grep -i x509            # no output
```

**Points: 5**

---

## Task 7 — Worker node stuck NotReady [7 points]

**Seed fault (for context):** `kubelet` was stopped and `/var/lib/kubelet/kubeadm-flags.env` was edited so the container runtime endpoint points at a nonexistent socket path.

**Solution (on `edge01-worker1`):**
```bash
kubectl describe node edge01-worker1              # Conditions/Reason string first, from the control-plane side
ssh edge01-worker1   # or sudo -i if already there
systemctl status kubelet containerd
journalctl -u kubelet -n 100 --no-pager           # reveals the bad --container-runtime-endpoint value
cat /var/lib/kubelet/kubeadm-flags.env
# fix the socket path back to unix:///var/run/containerd/containerd.sock
systemctl daemon-reload
systemctl restart containerd kubelet
```

**Verify:**
```bash
kubectl get nodes                                                             # edge01-worker1 = Ready
kubectl get pods -A -o wide --field-selector spec.nodeName=edge01-worker1     # previously stuck pods now Running
kubectl run edge-test --image=busybox --restart=Never -n default -- sleep 60
kubectl get pod edge-test -o wide                                             # schedules/runs successfully
```

**Points: 7**

---

## Task 8 — Taint a node and schedule a matching workload [5 points]

**Solution:**
```bash
kubectl taint nodes prod01-worker2 dedicated=batch:NoSchedule

cat <<'EOF' | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: batch-runner
spec:
  replicas: 2
  selector:
    matchLabels: {app: batch-runner}
  template:
    metadata:
      labels: {app: batch-runner}
    spec:
      tolerations:
      - key: dedicated
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
                values: [prod01-worker2]
      containers:
      - name: busybox
        image: busybox
        command: ["sleep", "3600"]
EOF

k run untainted-test --image=nginx --restart=Never
```

**Verify:**
```bash
k get pods -l app=batch-runner -o wide            # both NODE = prod01-worker2
k get pod untainted-test -o wide                  # NODE != prod01-worker2
```

**Points: 5**

---

## Task 9 — Namespace network segmentation with NetworkPolicy [6 points]

**Solution:**
```bash
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-default-deny
  namespace: secure-app
spec:
  podSelector:
    matchLabels: {app: backend}
  policyTypes: [Ingress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: secure-app
spec:
  podSelector:
    matchLabels: {app: backend}
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector:
        matchLabels: {app: frontend}
    ports:
    - protocol: TCP
      port: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-egress-dns-only
  namespace: secure-app
spec:
  podSelector:
    matchLabels: {app: backend}
  policyTypes: [Egress]
  egress:
  - to:
    - namespaceSelector:
        matchLabels: {kubernetes.io/metadata.name: kube-system}
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
EOF
```

**Verify:**
```bash
k exec -n secure-app frontend -- wget -qO- --timeout=3 backend:8080     # succeeds
k exec -n secure-app scanner  -- wget -qO- --timeout=3 backend:8080     # times out
k exec -n secure-app backend  -- nslookup kubernetes.default            # resolves
```

**Points: 6**

---

## Task 10 — Join a new worker node to an HA cluster [4 points]

**Solution (from `ha01-cp1`, then on `ha01-worker2`):**
```bash
kubeadm token create --print-join-command
# copy the printed command, run on ha01-worker2:
sudo kubeadm join <ha01-cp1-ip-or-endpoint>:6443 \
  --token <new-token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

**Verify:**
```bash
kubectl get nodes -o wide       # ha01-worker2 appears, transitions to Ready
kubeadm token list              # confirm the token was actually used/consumed
```

**Points: 4**

---

## Task 11 — Control-plane component crash-looping [6 points]

**Seed fault (for context):** `kube-controller-manager.yaml`'s `hostPath` volume for the PKI directory was edited to a nonexistent path.

**Solution (on `ha01-cp2`):**
```bash
sudo crictl ps -a | grep controller-manager               # Exited, high restart count
sudo crictl logs $(sudo crictl ps -a -q --name kube-controller-manager | head -1)
# log line reveals the missing/renamed hostPath directory
sudo cat /etc/kubernetes/manifests/kube-controller-manager.yaml   # find the bad hostPath.path
sudo vi /etc/kubernetes/manifests/kube-controller-manager.yaml    # restore correct path (/etc/kubernetes/pki)
```

**Verify:**
```bash
sudo crictl ps | grep controller-manager        # Running, restart count stable across ~1 min
kubectl get pods -n kube-system -o wide | grep controller-manager-ha01-cp2   # Running 1/1
kubectl create ns rollout-proof-test && kubectl delete ns rollout-proof-test  # controller-manager reconciling
```

**Points: 6**

---

## Task 12 — Diagnose a Pending PersistentVolumeClaim [5 points]

**Seed fault (for context):** `pvc-broken` requests `storageClassName: manual` and `ReadWriteOnce`, `150Mi`, but no PV with that class currently exists.

**Solution:**
```bash
kubectl describe pvc pvc-broken -n data-drill2      # Events: no persistent volumes available for this claim / class "manual" has no matches
kubectl get sc                                      # confirm "manual" is not a provisioner-backed dynamic class

cat <<'EOF' | k apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-drill2-fix
spec:
  capacity:
    storage: 200Mi
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  hostPath:
    path: /mnt/drill2-data
EOF
```

**Verify:**
```bash
kubectl get pvc -n data-drill2 pvc-broken     # STATUS = Bound
kubectl get pv pv-drill2-fix                  # STATUS = Bound, CLAIM = data-drill2/pvc-broken
```

**Points: 5**

---

## Task 13 — Ingress path-based routing [5 points]

**Solution:**
```bash
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: catalog-ingress
  namespace: shop-web
spec:
  ingressClassName: nginx
  rules:
  - host: catalog.demo.local
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: catalog-v1-svc
            port:
              number: 8080
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: catalog-v2-svc
            port:
              number: 8081
EOF
```

**Verify:**
```bash
kubectl describe ingress catalog-ingress -n shop-web       # both backends resolved, non-empty endpoints
curl -H "Host: catalog.demo.local" http://<ingress-controller-ip>/v1
curl -H "Host: catalog.demo.local" http://<ingress-controller-ip>/v2
```

**Points: 5**

---

## Task 14 — Upgrade the HA cluster by one minor version [5 points]

**Solution (abbreviated — full command set per node):**
```bash
# On ha01-cp1:
sudo apt-mark unhold kubeadm && sudo apt-get update && sudo apt-get install -y kubeadm=1.36.x-1.1 && sudo apt-mark hold kubeadm
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.36.x
kubectl drain ha01-cp1 --ignore-daemonsets --delete-emptydir-data
sudo apt-mark unhold kubelet kubectl && sudo apt-get install -y kubelet=1.36.x-1.1 kubectl=1.36.x-1.1 && sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload && sudo systemctl restart kubelet
kubectl uncordon ha01-cp1

# On ha01-cp2:
sudo apt-mark unhold kubeadm && sudo apt-get install -y kubeadm=1.36.x-1.1 && sudo apt-mark hold kubeadm
sudo kubeadm upgrade node
kubectl drain ha01-cp2 --ignore-daemonsets --delete-emptydir-data
sudo apt-mark unhold kubelet kubectl && sudo apt-get install -y kubelet=1.36.x-1.1 kubectl=1.36.x-1.1 && sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload && sudo systemctl restart kubelet
kubectl uncordon ha01-cp2

# On ha01-worker1:
sudo apt-mark unhold kubeadm && sudo apt-get install -y kubeadm=1.36.x-1.1 && sudo apt-mark hold kubeadm
sudo kubeadm upgrade node
kubectl drain ha01-worker1 --ignore-daemonsets --delete-emptydir-data
sudo apt-mark unhold kubelet kubectl && sudo apt-get install -y kubelet=1.36.x-1.1 kubectl=1.36.x-1.1 && sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload && sudo systemctl restart kubelet
kubectl uncordon ha01-worker1
```

**Verify:**
```bash
kubectl get nodes -o wide      # all three show v1.36.x and Ready, no lingering SchedulingDisabled
kubectl get pods -n kube-system   # all control-plane pods healthy post-upgrade
```

Grading note: running `kubeadm upgrade apply` on `ha01-cp2` instead of `kubeadm upgrade node` is a common wrong-answer pattern that costs points even if the cluster technically ends up healthy.

**Points: 5**

---

## Task 15 — Service exists but traffic never reaches the Pods [6 points]

**Seed faults (for context):** `webshop-svc`'s selector is `app=webshop-app` (a near-miss of the Pods' actual label `app=webshop`), **and** even after fixing the selector, `targetPort` is set to `80` while the container actually listens on `8080`.

**Solution:**
```bash
kubectl get endpoints webshop-svc -n shop                  # empty
kubectl get pods -n shop --show-labels                     # actual label is app=webshop
kubectl get svc webshop-svc -n shop -o yaml | grep -A3 selector

kubectl patch svc webshop-svc -n shop -p '{"spec":{"selector":{"app":"webshop"}}}'
kubectl get endpoints webshop-svc -n shop                  # now populated, but still fails on request

kubectl exec -n shop <a-webshop-pod> -- netstat -tlnp       # confirms listening on 8080, not 80
kubectl patch svc webshop-svc -n shop -p '{"spec":{"ports":[{"port":80,"targetPort":8080}]}}'
```

**Verify:**
```bash
kubectl get endpoints webshop-svc -n shop
kubectl run tmp --rm -it --image=busybox:1.36 -n shop --restart=Never -- wget -qO- webshop-svc.shop.svc.cluster.local
```

**Points: 6**

---

## Task 16 — Diagnose a Deployment stuck with Pending Pods [5 points]

**Seed faults (for context):** the Pod template's `nodeSelector` requires `disktype=ssd`, which no node currently has, and additionally the one node that could reasonably be labeled (`prod01-worker2`) is cordoned from earlier maintenance.

**Solution:**
```bash
kubectl get pods -n shop -l app=analytics -o wide
kubectl describe pod <one-of-the-pending-pods> -n shop     # Events: didn't match node selector, SchedulingDisabled
kubectl get nodes                                          # prod01-worker2 shows SchedulingDisabled
kubectl get nodes --show-labels                             # no node has disktype=ssd

kubectl label nodes prod01-worker2 disktype=ssd
kubectl uncordon prod01-worker2
```

**Verify:**
```bash
kubectl get pods -n shop -l app=analytics -o wide    # all 3 Running, NODE=prod01-worker2
kubectl get nodes                                    # prod01-worker2 no longer SchedulingDisabled
```

**Points: 5**

---

## Task 17 — Fix a ServiceAccount's insufficient RBAC permissions [4 points]

**Solution:**
```bash
kubectl auth can-i list pods --as=system:serviceaccount:billing:billing-agent -n billing    # no
kubectl get role -n billing            # find the Role bound to billing-agent
kubectl edit role <role-name> -n billing
# change verbs: ["get"] to verbs: ["get", "list", "watch"]
```

**Verify:**
```bash
kubectl auth can-i list pods --as=system:serviceaccount:billing:billing-agent -n billing     # yes
kubectl auth can-i watch pods --as=system:serviceaccount:billing:billing-agent -n billing    # yes
kubectl auth can-i delete pods --as=system:serviceaccount:billing:billing-agent -n billing   # no (unchanged — least privilege preserved)
```

**Points: 4**

---

## Task 18 — CNI misconfiguration causing stuck pods on one node [5 points]

**Seed fault (for context):** the CNI config file under `/etc/cni/net.d/` on `prod01-worker2` was renamed/removed, so the kubelet can't set up pod sandboxes on that node even though the node itself reports `Ready`.

**Solution:**
```bash
kubectl run cni-test --image=busybox --restart=Never --overrides='{"spec":{"nodeName":"prod01-worker2"}}' -- sleep 3600
kubectl describe pod cni-test          # Events: failed to set up sandbox / network: failed to find plugin
ssh prod01-worker2
ls /etc/cni/net.d/                     # empty or missing the expected .conflist
# restore the CNI config file from the CNI DaemonSet's own ConfigMap/expected content, e.g.:
sudo cp /etc/cni/net.d.bak/10-flannel.conflist /etc/cni/net.d/    # or re-trigger the CNI DaemonSet pod on that node
kubectl delete pod -n kube-system <cni-daemonset-pod-on-prod01-worker2>   # let it recreate and re-lay the config
```

**Verify:**
```bash
kubectl get pod cni-test -o wide             # transitions to Running
kubectl run cni-test2 --image=busybox --restart=Never --overrides='{"spec":{"nodeName":"prod01-worker2"}}' -- sleep 60
kubectl get pod cni-test2 -o wide            # Running promptly, no ContainerCreating hang
```

**Points: 5**

---

## Task 19 — Cluster DNS resolution failing for one namespace [6 points]

**Seed fault (for context):** `checkout-ns` has a default-deny egress `NetworkPolicy` applied with no port-53 carve-out, while CoreDNS itself and every other namespace are fine.

**Solution:**
```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns             # healthy, rules out CoreDNS itself
kubectl run dnstest --rm -it --image=busybox:1.36 -n checkout-ns --restart=Never -- nslookup kubernetes.default   # times out
kubectl get networkpolicy -n checkout-ns                        # a default-deny-egress policy exists with no DNS exception

cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: checkout-ns
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
  - to:
    - namespaceSelector:
        matchLabels: {kubernetes.io/metadata.name: kube-system}
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
EOF
```

**Verify:**
```bash
kubectl run dnstest --rm -it --image=busybox:1.36 -n checkout-ns --restart=Never -- nslookup kubernetes.default   # resolves
kubectl run dnstest --rm -it --image=busybox:1.36 -n checkout-ns --restart=Never -- nslookup example.com          # resolves
```

Grading note: if the pre-existing default-deny-egress policy is a genuine requirement of the environment, the fix must **add** a DNS-specific allow policy, not delete the default-deny policy outright — deleting it removes intended segmentation and is the wrong fix even though it also "solves" the symptom.

**Points: 6**

---

## Scoring Recap

| # | Task | Domain | Points |
|---|---|---|---|
| 1 | Rolling update with a forced rollback | Workloads & Scheduling | 5 |
| 2 | etcd snapshot backup | Cluster Architecture | 7 |
| 3 | Application pod crash-looping | Troubleshooting | 5 |
| 4 | Expose a Deployment via a ClusterIP Service | Services & Networking | 4 |
| 5 | Static provisioning: PV, PVC, Pod | Storage | 5 |
| 6 | Certificate expiration check and renewal | Cluster Architecture | 5 |
| 7 | Worker node stuck NotReady | Troubleshooting | 7 |
| 8 | Taint a node and schedule a matching workload | Workloads & Scheduling | 5 |
| 9 | Namespace network segmentation with NetworkPolicy | Services & Networking | 6 |
| 10 | Join a new worker node to an HA cluster | Cluster Architecture | 4 |
| 11 | Control-plane component crash-looping | Troubleshooting | 6 |
| 12 | Diagnose a Pending PersistentVolumeClaim | Storage | 5 |
| 13 | Ingress path-based routing | Services & Networking | 5 |
| 14 | Upgrade the HA cluster by one minor version | Cluster Architecture | 5 |
| 15 | Service exists but traffic never reaches the Pods | Troubleshooting | 6 |
| 16 | Diagnose a Deployment stuck with Pending Pods | Workloads & Scheduling | 5 |
| 17 | Fix a ServiceAccount's insufficient RBAC permissions | Cluster Architecture | 4 |
| 18 | CNI misconfiguration causing stuck pods on one node | Services & Networking | 5 |
| 19 | Cluster DNS resolution failing for one namespace | Troubleshooting | 6 |

**Domain totals:** Troubleshooting 30 · Cluster Architecture, Installation & Configuration 25 · Services & Networking 20 · Workloads & Scheduling 15 · Storage 10 — **100 points total**, mirroring the official CKA domain weighting from `01-exam-snapshot-and-priorities.md`.

**Pass mark:** 66/100 (66%), matching the real CKA passing score.
