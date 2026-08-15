# Question Bank — Cluster Architecture & Maintenance

*Domain weight: Cluster Architecture, Installation & Configuration — 25%. Questions below are original drills built from the general competency areas identified in `01-exam-snapshot-and-priorities.md` and `02-topics/cluster-architecture-kubeadm-etcd.md` — none reproduce a specific remembered real exam question. Attempt each task cold before expanding the solution. Assume containerd as the runtime and a kubeadm-built cluster unless stated otherwise.*

**Coverage:** kubeadm init/join/upgrade, static pods, certificate management, etcd snapshot backup/restore, node drain/cordon/uncordon, control-plane component config/troubleshooting.

**Distribution:** 25 questions — 17 P0, 6 P1, 2 P2, 0 P3 · 9 Easy, 11 Medium, 5 Hard.

---

### Question 1 — Read the join command back out of a live cluster
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Your `kubeadm init` output scrolled off-screen an hour ago and you never saved it. Without re-running `init`, produce a fully valid `kubeadm join` command a new worker node could use right now.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubeadm token create --print-join-command
```

**Verify:**
```bash
kubeadm token list
# confirm a new token appears with a fresh TTL (24h default)
```

**Common mistake:** Trying to reconstruct the command manually from `kubeadm token list` (which only shows the token, not the CA cert hash) — `--print-join-command` is the only command that assembles both pieces correctly.

</details>

---

### Question 2 — Bootstrap a control plane with a specific pod network CIDR
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 6 min
**Task:** On a fresh node with containerd already installed and kubeadm/kubelet/kubectl packages present, initialize a control plane so it is compatible with a CNI that expects pod network `10.244.0.0/16`. Set up kubeconfig access for the current user afterward.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

**Verify:**
```bash
kubectl get nodes
# control-plane node appears (NotReady is expected until a CNI is applied)
kubectl cluster-info
```

**Common mistake:** Applying a CNI manifest whose default pod CIDR doesn't match `--pod-network-cidr` (or forgetting the flag entirely) — nodes then sit `NotReady` indefinitely and it looks like a kubelet problem, not a CIDR mismatch.

</details>

---

### Question 3 — Diagnose a worker stuck NotReady after join
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 8 min
**Task:** A worker node successfully ran `kubeadm join` and appears in `kubectl get nodes`, but it has been `NotReady` for 10+ minutes. Find and fix the root cause without re-joining the node.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe node <node>            # check Conditions / Events for CNI-related messages
kubectl get pods -n kube-system -o wide | grep <node>   # is the CNI daemonset pod even scheduled/running there?
# on the node itself:
crictl ps -a | grep -i cni
journalctl -u kubelet -n 100 --no-pager | grep -i cni
ls /etc/cni/net.d/                       # empty or missing = CNI never applied/propagated
# fix: (re)apply the CNI manifest from the control-plane node
kubectl apply -f <cni-manifest-url>
```

**Verify:**
```bash
kubectl get nodes
# node flips to Ready within ~30-60s of the CNI pod going Running on it
```

**Common mistake:** Assuming a `NotReady` node means a broken kubelet/join and spending the whole time budget on `systemctl restart kubelet` loops, when the real gap is simply "no CNI was ever installed on the cluster."

</details>

---

### Question 4 — Find which static pod manifest sets an apiserver flag
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Without opening any file with a text editor, determine what value `--service-cluster-ip-range` is currently set to on the running kube-apiserver, using only `kubectl`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl -n kube-system get pod kube-apiserver-<controlplane-node> -o yaml | grep -A1 service-cluster-ip-range
```

**Verify:**
```bash
# cross-check against the manifest on disk to confirm they match
grep service-cluster-ip-range /etc/kubernetes/manifests/kube-apiserver.yaml
```

**Common mistake:** Forgetting the mirror pod's name includes the node suffix (`kube-apiserver-<nodename>`, not just `kube-apiserver`) and getting a "not found" error.

</details>

---

### Question 5 — Restart a static pod without kubectl delete
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Force the kube-scheduler static pod to restart on a control-plane node. `kubectl delete pod kube-scheduler-<node>` is not an acceptable method (it will just get recreated identically and doesn't demonstrate the correct mechanism) — use the technique that actually applies here.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/
# wait for the mirror pod to disappear
sudo mv /tmp/kube-scheduler.yaml /etc/kubernetes/manifests/
```

**Verify:**
```bash
kubectl get pod kube-scheduler-<node> -n kube-system -o jsonpath='{.status.startTime}'
# a fresh, recent timestamp confirms restart
crictl ps | grep scheduler
```

**Common mistake:** Trying `kubectl edit` on the static pod object itself — the edit appears to succeed but is silently discarded because kubelet reconciles from the manifest file, not the API object.

</details>

---

### Question 6 — Diagnose and fix a broken static pod manifest (kubectl still available)
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** `kube-scheduler` on the control-plane node is crash-looping (apiserver itself is healthy). Find the root cause and fix it using node-local tooling, then confirm recovery via `kubectl`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
crictl ps -a | grep scheduler                     # find the exited/crash-looping container id
crictl logs <container-id>                        # log states the exact bad flag/value
sudo vi /etc/kubernetes/manifests/kube-scheduler.yaml   # fix the identified flag
```

**Verify:**
```bash
crictl ps | grep scheduler   # new container, not restarting
kubectl get pods -n kube-system | grep scheduler   # Running 1/1
```

**Common mistake:** Reading only `crictl ps -a`'s STATE column and guessing at the fix instead of actually reading `crictl logs` on the exited container, which almost always states the problem verbatim in the first few lines.

</details>

---

### Question 7 — Diagnose a fully broken apiserver (kubectl unavailable)
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 12 min
**Task:** `kubectl` commands all time out with "connection refused" on the control-plane node itself. Diagnose and repair the root cause using only node-local tools (no working `kubectl` allowed during diagnosis), then confirm the cluster is healthy again.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
systemctl status kubelet                           # is kubelet itself alive?
journalctl -u kubelet -n 200 --no-pager | tail -50
crictl ps -a | grep apiserver                       # is the container even attempting to start?
crictl logs <apiserver-container-id>                # states the exact failure (bad cert path, bad flag, etc.)
cat /etc/kubernetes/manifests/kube-apiserver.yaml   # diff against what the log implies is wrong
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml  # fix and save
```

**Verify:**
```bash
crictl ps | grep apiserver     # stable, non-restarting container
kubectl get nodes              # now works again
kubectl get pods -n kube-system   # all control-plane pods Running
```

**Common mistake:** Repeatedly retrying `kubectl` commands hoping the problem is transient, burning minutes before pivoting to `crictl`/`journalctl` on the node — recognize "apiserver itself is the broken component" as the signal to immediately drop to node-local diagnostics.

</details>

---

### Question 8 — Check certificate expiration across the cluster
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Produce a report of every kubeadm-managed certificate's expiration date on the control-plane node, and separately confirm the apiserver cert's expiry directly from the file using `openssl`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo kubeadm certs check-expiration
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate -subject
```

**Verify:**
```bash
# the RESIDUAL TIME column from kubeadm certs check-expiration should roughly
# match the delta between "now" and the openssl -enddate output for apiserver.crt
```

**Common mistake:** Only checking `kubeadm certs check-expiration` and never cross-checking with `openssl` on the actual file — on the exam you may be handed a scenario where `kubeadm` itself can't run (e.g. admin.conf is also affected) and `openssl` is the only path.

</details>

---

### Question 9 — Renew all certificates and force reload
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** All control-plane certificates on a single-control-plane cluster are within 30 days of expiring. Renew them and make sure the running components actually pick up the new certs (not just the files on disk).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo kubeadm certs renew all
# force every control-plane static pod to restart to pick up new certs
cd /etc/kubernetes/manifests
sudo mkdir -p /tmp/manifests-restart
sudo mv kube-apiserver.yaml kube-controller-manager.yaml kube-scheduler.yaml etcd.yaml /tmp/manifests-restart/
sudo mv /tmp/manifests-restart/*.yaml .
```

**Verify:**
```bash
sudo kubeadm certs check-expiration     # residual time reset to ~1 year for all certs
kubectl get pods -n kube-system         # all control-plane pods freshly restarted, Running
openssl s_client -connect 127.0.0.1:6443 -showcerts </dev/null 2>/dev/null | openssl x509 -noout -enddate
# confirms the LIVE connection (not just the file) presents the new expiry
```

**Common mistake:** Renewing certs and declaring the task done without restarting the static pods — the running processes keep serving the old certs from memory (loaded at process start) until restarted, so `check-expiration` looks fixed but the live connection still presents the stale cert.

</details>

---

### Question 10 — Renew a single named certificate and prove the file changed
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Renew only the `apiserver-etcd-client` certificate (leave every other cert untouched), force the affected static pod to pick it up, and prove via `openssl` that specifically that file's `notBefore` timestamp changed.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
openssl x509 -in /etc/kubernetes/pki/apiserver-etcd-client.crt -noout -dates   # note the "before" timestamp
sudo kubeadm certs renew apiserver-etcd-client
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

**Verify:**
```bash
openssl x509 -in /etc/kubernetes/pki/apiserver-etcd-client.crt -noout -dates   # notBefore is now "just now"
kubeadm certs check-expiration | grep -E 'apiserver-etcd-client|apiserver$|controller-manager|scheduler'
# only apiserver-etcd-client's residual time reset; others unchanged
```

**Common mistake:** Running `kubeadm certs renew all` when the task explicitly scopes it to one certificate — on the real exam a scoped instruction usually means the grader checks that unrelated certs' timestamps were *not* touched.

</details>

---

### Question 11 — Full etcd backup and restore cycle
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 10 min
**Task:** Create a Namespace called `pre-snap`. Take an etcd snapshot to `/opt/backup/etcd-snap.db`. Create a second Namespace called `post-snap`. Restore the cluster to the point-in-time of the snapshot.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create namespace pre-snap

sudo ETCDCTL_API=3 etcdctl snapshot save /opt/backup/etcd-snap.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

kubectl create namespace post-snap

sudo etcdutl snapshot restore /opt/backup/etcd-snap.db --data-dir=/var/lib/etcd-restored

sudo vi /etc/kubernetes/manifests/etcd.yaml
# change the hostPath.path for the etcd-data volume from /var/lib/etcd to /var/lib/etcd-restored
```

**Verify:**
```bash
crictl ps | grep etcd                 # fresh container after manifest change
kubectl get ns pre-snap               # exists
kubectl get ns post-snap              # NotFound — proves point-in-time restore worked
```

**Common mistake:** Using `etcdctl snapshot restore` for the restore step (removed/non-functional on etcd 3.5+) instead of `etcdutl`, or restoring into `/var/lib/etcd` in place instead of a brand-new directory, then forgetting to repoint the manifest's `hostPath`.

</details>

---

### Question 12 — Restore etcd with apiserver already down
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 12 min
**Task:** You are handed a snapshot file at `/opt/backup/etcd-snap.db`. The apiserver is currently down (etcd itself is corrupted/unreachable) so you cannot sanity-check anything via `kubectl` before or during the restore. Restore the cluster to a working state from the snapshot alone.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# no live kubectl available — work purely against the snapshot file and manifests
sudo etcdutl snapshot restore /opt/backup/etcd-snap.db --data-dir=/var/lib/etcd-restored
sudo vi /etc/kubernetes/manifests/etcd.yaml
# repoint hostPath.path (both the volume entry and confirm volumeMounts.mountPath still matches /var/lib/etcd internally)
```

**Verify:**
```bash
crictl ps | grep etcd                 # new, stable etcd container
crictl logs <etcd-container-id> | tail -30   # no error loop, "ready to serve client requests"
kubectl get nodes                     # kubectl works again now that etcd/apiserver chain is healthy
```

**Common mistake:** Waiting for a "working kubectl" before attempting anything — the restore is entirely file/CLI driven and doesn't need a live API at all; blocking on `kubectl` here wastes the whole time budget.

</details>

---

### Question 13 — Verify an etcd snapshot's integrity before trusting it
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** You inherited a snapshot file at `/opt/backup/etcd-snap.db` from a teammate and don't know if it's valid or how many keys/what revision it represents. Confirm it's usable before attempting any restore.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo etcdctl snapshot status /opt/backup/etcd-snap.db --write-out=table
```

**Verify:**
```bash
# output table shows non-zero HASH, REVISION, TOTAL KEYS, TOTAL SIZE
# a zero/garbage value or a command error means the file is corrupt or not an etcd snapshot at all
```

**Common mistake:** Skipping this check and discovering the snapshot is corrupt only after already tearing down the live data directory to attempt a restore — always validate first.

</details>

---

### Question 14 — Backup etcd running on a separate dedicated node
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 8 min
**Task:** In this cluster, etcd does not run co-located with the control-plane node you have shell access to — it runs on a separate dedicated etcd node at `10.0.0.50:2379`. Take a snapshot and get it onto the control-plane node at `/opt/backup/etcd-snap.db`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# run against the remote etcd node's endpoint (certs must be available locally, e.g. copied beforehand)
sudo ETCDCTL_API=3 etcdctl snapshot save /opt/backup/etcd-snap.db \
  --endpoints=https://10.0.0.50:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
# if the snapshot was taken directly on the etcd node instead, copy it over:
scp root@10.0.0.50:/opt/backup/etcd-snap.db /opt/backup/etcd-snap.db
```

**Verify:**
```bash
etcdctl snapshot status /opt/backup/etcd-snap.db --write-out=table
ls -la /opt/backup/etcd-snap.db
```

**Common mistake:** Defaulting to `--endpoints=https://127.0.0.1:2379` out of habit when etcd isn't actually local to the node you're running the command from — this fails with a connection error that's easy to misdiagnose as a cert problem.

</details>

---

### Question 15 — Cordon and drain a node with DaemonSets present
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** A worker node needs OS patching. Safely remove all evictable workloads from it (the node runs the cluster's CNI and kube-proxy as DaemonSets), then return it to service afterward.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
# ... perform maintenance ...
kubectl uncordon <node>
```

**Verify:**
```bash
kubectl get nodes    # SchedulingDisabled during drain, Ready after uncordon
kubectl get pods -o wide --all-namespaces --field-selector spec.nodeName=<node>
# only DaemonSet-managed pods remain during the drain window
```

**Common mistake:** Omitting `--ignore-daemonsets` and having the command hang or error indefinitely because DaemonSet pods are expected to run on every node and can't be gracefully evicted the normal way.

</details>

---

### Question 16 — Drain blocked by a PodDisruptionBudget
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** A Deployment with 2 replicas runs on the node you need to drain, protected by a PodDisruptionBudget requiring `minAvailable: 2`. Successfully drain the node anyway, choosing an approach that doesn't just delete the PDB outright.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get pdb -A                                    # confirm the impossible-to-satisfy PDB
kubectl scale deployment <name> --replicas=3 -n <ns>  # give it slack so evicting one pod still satisfies minAvailable:2
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
```

**Verify:**
```bash
kubectl drain <node> --ignore-daemonsets   # completes without a PDB violation error
kubectl get nodes                          # node shows SchedulingDisabled
kubectl get pdb -n <ns>                    # ALLOWED DISRUPTIONS > 0 throughout
```

**Common mistake:** Deleting or editing the PDB down to `minAvailable: 0` to force the drain through — technically unblocks it but defeats the purpose of the PDB and is the wrong-technique answer a grader is likely checking against; scaling up (or temporarily loosening thoughtfully) is the safer read of "drain successfully."

</details>

---

### Question 17 — Drain a node with local emptyDir data
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** A node runs a bare (unmanaged, no controller) Pod with an `emptyDir` volume containing scratch data, plus normal Deployment-backed pods. Drain the node fully.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --force
```

**Verify:**
```bash
kubectl get pods -o wide --all-namespaces --field-selector spec.nodeName=<node>
# only DaemonSet pods remain; the bare pod and its emptyDir data are gone
```

**Common mistake:** Running plain `kubectl drain <node>` without `--force` and `--delete-emptydir-data` — it aborts with explicit errors about the unmanaged pod and the local-data volume rather than silently failing, but under time pressure it's easy to not read the error and just retry the same command.

</details>

---

### Question 18 — Upgrade a single control-plane + worker cluster one minor version
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 18 min
**Task:** Upgrade a 1 control-plane + 1 worker kubeadm cluster currently on v1.34.x fully to the latest v1.35.x patch, following the correct sequencing, without skipping a minor version.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# --- control-plane node ---
sudo apt-mark unhold kubeadm
sudo apt-get update && sudo apt-get install -y kubeadm='1.35.*'
sudo apt-mark hold kubeadm
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.35.x

kubectl drain <cp-node> --ignore-daemonsets --delete-emptydir-data

sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet='1.35.*' kubectl='1.35.*'
sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload
sudo systemctl restart kubelet

kubectl uncordon <cp-node>

# --- worker node ---
sudo apt-mark unhold kubeadm
sudo apt-get install -y kubeadm='1.35.*'
sudo apt-mark hold kubeadm
sudo kubeadm upgrade node

kubectl drain <worker-node> --ignore-daemonsets --delete-emptydir-data

sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet='1.35.*' kubectl='1.35.*'
sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload
sudo systemctl restart kubelet

kubectl uncordon <worker-node>
```

**Verify:**
```bash
kubectl get nodes -o wide          # both nodes show v1.35.x, both Ready, no lingering SchedulingDisabled
kubectl get pods -n kube-system    # all control-plane pods healthy post-upgrade
kubeadm upgrade plan               # reports no further action for this minor
```

**Common mistake:** Running `kubeadm upgrade apply` on the worker (should always be `kubeadm upgrade node` on every node except the very first control-plane node); or letting `apt-get install` pull the newest available version without pinning, silently jumping two minors at once and violating the one-minor-at-a-time rule.

</details>

---

### Question 19 — Upgrade the second control-plane node in an HA pair
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 15 min
**Task:** You have a 2 control-plane-node HA cluster already upgraded on the first control-plane node (kubeadm/kubelet/kubectl all on the new minor). Bring the second control-plane node up to the same version while keeping the API reachable throughout (via the first node).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# on the SECOND control-plane node
sudo apt-mark unhold kubeadm
sudo apt-get install -y kubeadm='1.35.*'
sudo apt-mark hold kubeadm

sudo kubeadm upgrade node        # NOT "upgrade apply" — that's only for the first CP node

kubectl drain <cp2-node> --ignore-daemonsets --delete-emptydir-data

sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet='1.35.*' kubectl='1.35.*'
sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload
sudo systemctl restart kubelet

kubectl uncordon <cp2-node>
```

**Verify:**
```bash
kubectl get nodes -o wide            # both control-plane nodes report v1.35.x
kubectl get pods -n kube-system -o wide | grep <cp2-node>   # static pods rewritten and Running there too
# confirm the API stayed reachable throughout by checking that kubectl commands
# issued during cp2's drain window succeeded (served by cp1)
```

**Common mistake:** Running `kubeadm upgrade apply v1.35.x` on the second control-plane node — `apply` performs cluster-wide config changes meant to run exactly once (on the first node); running it again on the second node is redundant at best and a wrong-technique answer on the exam.

</details>

---

### Question 20 — Diagnose a kubelet that won't rejoin Ready after a package upgrade
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** After upgrading the `kubelet` and `kubectl` packages on a worker node as part of a cluster upgrade, the node stays `NotReady` after `systemctl restart kubelet`. Diagnose and fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
systemctl status kubelet                 # check for a failed/inactive state
journalctl -u kubelet -n 100 --no-pager  # look for unit/version mismatch or config load errors
sudo systemctl daemon-reload             # reload the systemd unit definition after the binary swap
sudo systemctl restart kubelet
```

**Verify:**
```bash
systemctl status kubelet     # active (running)
kubectl get nodes            # node flips back to Ready
kubelet --version            # matches the freshly installed package version
```

**Common mistake:** Swapping the kubelet binary/package without running `systemctl daemon-reload` first — systemd keeps using cached unit-file state, producing a subtly broken kubelet startup that's easy to misattribute to a CNI or cert problem.

</details>

---

### Question 21 — CertificateSigningRequest approval for a new kubelet
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** A new node's kubelet has generated a bootstrap CertificateSigningRequest that is sitting `Pending`. Inspect it and approve it so the node can complete TLS bootstrap.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get csr
kubectl describe csr <csr-name>          # confirm signerName is kubernetes.io/kube-apiserver-client-kubelet and requestor looks legitimate
kubectl certificate approve <csr-name>
```

**Verify:**
```bash
kubectl get csr <csr-name>    # CONDITION column shows Approved,Issued
kubectl get nodes             # the new node eventually shows up / becomes Ready
```

**Common mistake:** Blindly approving every `Pending` CSR without checking `signerName`/requestor first — on a troubleshooting-flavored task the CSR may be deliberately for the wrong signer or from an unexpected identity, and the correct answer is to *not* approve it and investigate instead.

</details>

---

### Question 22 — RBAC-restricted ServiceAccount for a node-maintenance script
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 8 min
**Task:** Create a ServiceAccount `node-ops` in the `kube-system` namespace that is permitted only to `get`, `list`, and `patch` Node objects cluster-wide (no other resources), and confirm the permission boundary works both ways (allowed verb succeeds, disallowed verb is denied).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create serviceaccount node-ops -n kube-system

kubectl create clusterrole node-ops-role \
  --verb=get,list,patch --resource=nodes

kubectl create clusterrolebinding node-ops-binding \
  --clusterrole=node-ops-role \
  --serviceaccount=kube-system:node-ops
```

**Verify:**
```bash
kubectl auth can-i patch nodes --as=system:serviceaccount:kube-system:node-ops     # yes
kubectl auth can-i delete nodes --as=system:serviceaccount:kube-system:node-ops    # no
kubectl auth can-i get pods --as=system:serviceaccount:kube-system:node-ops        # no
```

**Common mistake:** Using `kubectl create role` (namespaced) instead of `kubectl create clusterrole` — Node is a cluster-scoped resource, so a namespaced Role can never grant access to it regardless of the RoleBinding, and the ServiceAccount silently gets zero effective permission on nodes.

</details>

---

### Question 23 — Simulate and recover from a control-plane node clock skew
**Priority:** P2 · **Difficulty:** Hard · **Target time:** 10 min
**Task:** A control-plane node's system clock has drifted several hours out of sync, causing TLS handshake failures between components (certs appear "not yet valid" or "expired" even though they're not, per `openssl -dates`). Diagnose the symptom correctly and restore normal operation.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
timedatectl                                   # confirm System clock synchronized: no / large offset
date                                          # compare against a known-good reference
crictl logs <apiserver-container-id> | grep -i -E 'certificate|x509|not yet valid|expired'

# fix: resync the clock
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd      # or chronyd, depending on distro
# once synced, restart affected static pods so any TLS handshake state is retried fresh
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

**Verify:**
```bash
timedatectl               # System clock synchronized: yes
kubectl get nodes         # cluster responds normally again
crictl ps | grep apiserver   # stable, non-restarting
```

**Common mistake:** Chasing this as a certificate-renewal problem (running `kubeadm certs renew all` repeatedly) when the certs themselves are fine and the actual root cause is clock skew — renewing certs won't fix anything if the clock keeps drifting, and the "not yet valid" / "expired" wording in logs is the specific tell that should redirect diagnosis toward `timedatectl`, not `kubeadm certs`.

</details>

---

### Question 24 — Rebuild kubeconfig access after admin.conf is lost
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** `$HOME/.kube/config` was accidentally deleted on the control-plane node and the original `/etc/kubernetes/admin.conf` is also gone. The cluster's certs and static pods are otherwise healthy. Regain `kubectl` admin access without re-running `kubeadm init`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo kubeadm init phase kubeconfig admin
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

**Verify:**
```bash
kubectl get nodes         # succeeds using the regenerated kubeconfig
kubectl get pods -n kube-system
```

**Common mistake:** Reaching for a full `kubeadm init` (or `kubeadm reset` + reinit) out of panic — `kubeadm init phase kubeconfig admin` regenerates just the missing admin kubeconfig from the existing CA without touching the running cluster at all.

</details>

---

### Question 25 — Install a cluster component via Helm with a pinned chart version
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 5 min
**Task:** Install a cluster-facing component (e.g. metrics-server) into the `kube-system` namespace using Helm, pinned to a specific chart version, and confirm the installed release matches that pin.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system --version <x.y.z>
```

**Verify:**
```bash
helm list -n kube-system              # CHART column shows metrics-server-<x.y.z>
kubectl get deployment metrics-server -n kube-system
kubectl top nodes                     # eventually returns data once the deployment is Ready
```

**Common mistake:** Omitting `--version` and getting whatever the latest chart happens to be, then failing a task that specifically asked for a pinned version — always check `helm list` afterward to confirm the exact chart version landed, not just that the pod is Running.

</details>

