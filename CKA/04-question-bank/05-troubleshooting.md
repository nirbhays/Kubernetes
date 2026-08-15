# Question Bank — Troubleshooting (30% domain, largest on the exam)

*29 original, hands-on exercises. Aligned to `CKA/01-exam-snapshot-and-priorities.md` (priority matrix) and `CKA/02-topics/troubleshooting-playbook.md`. Distribution skews toward P0 skills — control-plane/kubelet/static-pod/certificate/etcd diagnosis and DNS — since those carry the highest official weight, frequency, and failure risk for a CKAD-certified candidate who is rusty on admin-level diagnosis specifically. CrashLoopBackOff/ImagePullBackOff/basic Pending triage are kept to a handful of speed-drills since they overlap your CKAD baseline. Every scenario here is an original lab construction built from the general competency, not a reproduction of any specific claimed real-exam question.*

**Tally:** 19× P0 · 7× P1 · 3× P2 — 9× Easy · 15× Medium · 5× Hard

Run all of these on real multi-node VMs (kubeadm), not kind/minikube — several depend on systemd/CRI-level access that's abstracted away in those tools.

---

### Question 1 — Kubelet down, node stuck NotReady
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 5 min
**Task:** Node `worker-1` is showing `NotReady`. Without rebooting the node or re-running `kubeadm join`, bring it back to `Ready` as fast as possible.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# On the control-plane host, confirm the symptom first
kubectl get nodes
kubectl describe node worker-1 | tail -20     # Conditions + Events

# SSH/sudo to worker-1
sudo -i
systemctl status kubelet
journalctl -u kubelet -n 100 --no-pager       # find the actual error line
systemctl restart kubelet                     # if it's just stopped/crashed
systemctl status kubelet                      # confirm active (running)
```

**Verify:**
```bash
kubectl get nodes                                                   # worker-1 Ready
kubectl get pods -A -o wide --field-selector spec.nodeName=worker-1 # pods scheduling again
kubectl describe node worker-1 | grep Taints                        # NoExecute taint gone
```

**Common mistake:** Restarting kubelet without first reading `journalctl -u kubelet` — if the underlying cause is a corrupted config file, the service will just crash-loop again immediately after restart. Always read the log line before restarting blindly.

</details>

---

### Question 2 — containerd down, kubelet looks fine
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Node `worker-2` is `NotReady`. `systemctl status kubelet` on the node shows `active (running)`. Find the real root cause and fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe node worker-2 | tail -20     # Ready condition reason/message text

sudo -i
systemctl status kubelet containerd           # containerd is the one that's down
journalctl -u containerd -n 100 --no-pager
crictl info                                   # will error: "connection refused" while containerd is down

systemctl start containerd
systemctl status containerd                   # confirm active
crictl info | grep -i cgroupDriver            # sanity check it's actually serving requests
systemctl restart kubelet                     # give kubelet a clean handshake with the runtime
```

**Verify:**
```bash
kubectl get nodes                             # worker-2 Ready
crictl ps -a | head                           # containers visible again at the CRI level
```

**Common mistake:** Fixating on kubelet because it's the first thing candidates check, and missing that the CRI socket (`unix:///var/run/containerd/containerd.sock`) is simply unreachable because containerd itself, not kubelet, is the stopped process. `k describe node` Conditions/Events almost always hints at this if read carefully before SSHing in.

</details>

---

### Question 3 — Corrupted kubelet config, wrong cgroup driver
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** On `worker-3`, `/var/lib/kubelet/config.yaml` was hand-edited by a colleague and now `cgroupDriver` doesn't match containerd's configured driver. The kubelet crash-loops on start. Fix it so the node reaches `Ready`, using only the diagnostic commands from the playbook (do not just diff against a backup).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo -i
systemctl status kubelet                      # crash-looping / failed
journalctl -u kubelet -n 100 --no-pager | grep -i cgroup

crictl info | grep -i cgroupDriver            # what containerd actually expects, e.g. "systemd"
cat /var/lib/kubelet/config.yaml | grep -i cgroupDriver

vi /var/lib/kubelet/config.yaml               # set cgroupDriver to match containerd's value
systemctl daemon-reload
systemctl restart kubelet
```

**Verify:**
```bash
systemctl status kubelet                      # active (running), no restart churn
kubectl get nodes                             # worker-3 Ready
```

**Common mistake:** Editing `config.yaml` but skipping `daemon-reload` before restart out of a mistaken belief it's only needed for unit-file changes — harmless to run every time, so make it a reflex after any file edit under `/var/lib/kubelet/` or `/etc/systemd/`.

</details>

---

### Question 4 — Freshly joined node stuck NotReady, no CNI
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** A brand-new worker node, `worker-4`, was just joined to the cluster with `kubeadm join`. Both kubelet and containerd are `active (running)` on it, yet the node stays `NotReady` and pods scheduled to it stick in `ContainerCreating`. Diagnose and fix.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe node worker-4 | grep -A5 Conditions   # look for NetworkUnavailable=True

sudo -i
ls /etc/cni/net.d/ /opt/cni/bin/               # empty or missing → CNI was never installed on this node
```
CNI is normally installed cluster-wide via a DaemonSet (Calico/Flannel/etc.) — a node joined *after* the CNI DaemonSet was rolled out should get it automatically once its `Ready`-blocking condition clears, but if the DaemonSet's pod on that node is itself failing (e.g., `ImagePullBackOff`, or a `nodeSelector`/toleration gap), fix that first:
```bash
kubectl get pods -n kube-system -o wide | grep -i -E 'calico|flannel|cni' | grep worker-4
kubectl describe pod <cni-pod-on-worker-4> -n kube-system   # read the actual failure
# fix the underlying CNI pod issue (image pull, toleration for a taint, etc.)
```

**Verify:**
```bash
kubectl get nodes                                       # worker-4 Ready, NetworkUnavailable gone
kubectl run cnitest --image=busybox:1.36 --overrides='{"spec":{"nodeName":"worker-4"}}' --rm -it -- true
```

**Common mistake:** Treating "CNI missing" as something you fix by hand-copying binaries — on a kubeadm cluster the CNI is a DaemonSet; the real diagnostic target is almost always *why that DaemonSet's pod on this specific node* isn't healthy, not the node's local filesystem.

</details>

---

### Question 5 — kube-scheduler crash-looping from a flag typo
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** No new pods are being scheduled anywhere in the cluster; existing workloads are unaffected. `kubectl get pods -n kube-system` shows `kube-scheduler-cp-1` cycling through restarts. Fix it by editing the static pod manifest directly.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe pod kube-scheduler-cp-1 -n kube-system   # restart count climbing

# on cp-1:
crictl ps -a | grep scheduler                             # find the exited container ID
crictl logs <containerID>                                 # e.g. "unknown flag: --leader-electt"

cat /etc/kubernetes/manifests/kube-scheduler.yaml | grep leader
vi /etc/kubernetes/manifests/kube-scheduler.yaml           # fix --leader-electt -> --leader-elect
# save — kubelet watches the directory and reconciles automatically, no restart command needed
```

**Verify:**
```bash
crictl ps -a | grep scheduler                              # Running, stable
kubectl get pods -n kube-system | grep scheduler            # Running
kubectl run schedtest --image=busybox:1.36 --command -- sleep 3600
kubectl get pod schedtest -o wide -w                         # leaves Pending within seconds
```

**Common mistake:** Running `kubectl edit pod kube-scheduler-cp-1` — this edits a read-only mirror pod and has zero effect on the actual component. You must edit the file on disk under `/etc/kubernetes/manifests/`.

</details>

---

### Question 6 — kube-controller-manager can't find its cert
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** `kubectl get pods -n kube-system` shows `kube-controller-manager-cp-1` in `CrashLoopBackOff`. Deployments in the cluster are not producing ReplicaSets. Find and fix the root cause using only file-level and `crictl` tools.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# on cp-1:
crictl ps -a | grep controller-manager
crictl logs <containerID>                       # e.g. "no such file or directory: /etc/kubernetes/pki-typo/ca.crt"

cat /etc/kubernetes/manifests/kube-controller-manager.yaml | grep -A2 hostPath
# find the volume whose hostPath.path was changed to a nonexistent directory
vi /etc/kubernetes/manifests/kube-controller-manager.yaml
# correct the path back to /etc/kubernetes/pki (or wherever it should point)
```

**Verify:**
```bash
crictl ps -a | grep controller-manager           # Running, restart count stable for 60s
kubectl create deployment probe --image=nginx --replicas=1
kubectl get rs -l app=probe                       # a ReplicaSet actually gets created
kubectl delete deployment probe
```

**Common mistake:** Assuming a syntactically valid manifest can't be the problem — the YAML parses fine, the bug is a `hostPath` pointing at a directory that was renamed/moved. Only `crictl logs` (the component's own error output), not a YAML linter, reveals this class of fault.

</details>

---

### Question 7 — kube-apiserver fully down, kubectl unreachable
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 10 min
**Task:** `kubectl` on the control-plane node returns `connection refused` for every command. Diagnose and repair without any working `kubectl` access until the very end.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
sudo -i
crictl ps -a | grep apiserver                    # find it, note state (Exited) and exit code
crictl logs <containerID> --tail 100             # e.g. "failed to create listener: ... invalid --etcd-servers"

cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep etcd-servers
vi /etc/kubernetes/manifests/kube-apiserver.yaml # fix the malformed --etcd-servers value
```

**Verify:**
```bash
crictl ps -a | grep apiserver                    # Running
kubectl get nodes                                # kubectl works again — proves apiserver is back
```

**Common mistake:** Assuming a dead apiserver means the cluster needs to be rebuilt from scratch and reaching for `kubeadm reset`/re-init. The overwhelming majority of "kubectl unreachable" scenarios are a single static pod manifest fix, recoverable in a few minutes with zero data loss.

</details>

---

### Question 8 — Editing the mirror pod does nothing
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** A teammate tried to bump `kube-apiserver`'s `--v` log verbosity flag by running `kubectl edit pod kube-apiserver-cp-1 -n kube-system`, saved successfully with no errors, but the running component's log verbosity never changed. Explain why, and make the change actually take effect.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# kubectl edit against a mirror pod succeeds against the API object but is discarded/overwritten
# on the next kubelet reconciliation loop — the API object is not the source of truth.
sudo -i
vi /etc/kubernetes/manifests/kube-apiserver.yaml    # edit --v=<level> here instead
# save — kubelet detects the file change and recreates the static pod automatically
```

**Verify:**
```bash
crictl ps -a | grep apiserver                       # new container, fresh start time
crictl inspect <new-containerID> | grep -A2 '"-v"'  # confirm the new flag value took effect
```

**Common mistake:** Not realizing `kubectl edit`/`kubectl apply` against a mirror pod can silently "succeed" (no error returned) while having zero durable effect — the object gets reset back to whatever the manifest file says almost immediately.

</details>

---

### Question 9 — HA control plane, scheduler seems dead on one node
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** In a 3-control-plane-node cluster, `kubectl logs -n kube-system kube-scheduler-cp-2` shows nothing happening for the last 10 minutes, no scheduling activity logged. Determine whether this is actually a problem before touching anything.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get pods -n kube-system -l component=kube-scheduler -o wide   # all 3 Running?
kubectl get lease -n kube-system kube-scheduler -o yaml                # who holds the lease right now
kubectl get lease -n kube-system kube-scheduler -o jsonpath='{.spec.holderIdentity}'
```
If `cp-2` isn't the current leader, the quiet logs are expected — only the leader performs scheduling. Confirm the actual leader is healthy instead:
```bash
kubectl logs -n kube-system kube-scheduler-<leader-node>              # active scheduling activity here
```

**Verify:**
```bash
kubectl run leasetest --image=busybox:1.36 --command -- sleep 60
kubectl get pod leasetest -o wide                                      # gets a NODE assigned promptly
kubectl delete pod leasetest
```

**Common mistake:** Treating a non-leader replica's quiet logs as a failure and restarting/deleting it — in a leader-elected HA setup that's expected, healthy behavior. Always check `kubectl get lease -n kube-system` before concluding a control-plane component "isn't doing anything."

</details>

---

### Question 10 — etcd NOSPACE alarm blocking all writes
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** `kubectl create namespace test` hangs and eventually times out, but `kubectl get nodes` works fine. Diagnose and restore write capability to the cluster.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
alias e='etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key'

e endpoint health
e alarm list                          # NOSPACE alarm present

df -h /var/lib/etcd                   # confirm disk is actually full/near-full
# free up space (remove old snapshots, rotate logs, etc.)
e alarm disarm                        # etcd stays read-only until explicitly disarmed
```

**Verify:**
```bash
e alarm list                          # empty
kubectl create namespace test         # succeeds
kubectl delete namespace test
```

**Common mistake:** Freeing disk space and assuming that alone fixes it — etcd remains in the read-only alarm state until `alarm disarm` is run explicitly, even after space is available again.

</details>

---

### Question 11 — Restore command silently fails
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** You need to restore etcd from a snapshot at `/tmp/backup.db`. A colleague suggests `etcdctl snapshot restore /tmp/backup.db --data-dir=/var/lib/etcd-restored`. Explain what's wrong with this command and give the correct one.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# WRONG — etcdctl's restore subcommand was removed since etcd v3.5:
etcdctl snapshot restore /tmp/backup.db --data-dir=/var/lib/etcd-restored

# CORRECT — restore is an offline operation owned by etcdutl:
etcdutl snapshot restore /tmp/backup.db --data-dir=/var/lib/etcd-restored
```
Remember the split: `etcdctl` is the network client used for *backup* (`snapshot save`, talks to a live endpoint); `etcdutl` is the offline tool used for *restore* (operates directly on data files, no endpoint/TLS flags needed).

**Verify:**
```bash
ls -la /var/lib/etcd-restored/member/                 # new data directory populated
etcdutl snapshot status /tmp/backup.db --write-out=table   # confirms the snapshot itself is valid
```

**Common mistake:** Passing `--cacert`/`--cert`/`--key`/`--endpoints` to `etcdutl snapshot restore` out of muscle memory from `etcdctl` — `etcdutl` doesn't talk to a running endpoint at all, those flags are meaningless here and some versions will simply ignore or reject them.

</details>

---

### Question 12 — Full etcd disaster recovery
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 12 min
**Task:** Create a marker object (`kubectl create configmap pre-disaster --from-literal=k=v`), take an etcd snapshot, then simulate total data loss on a single-node lab control plane by wiping `/var/lib/etcd`'s contents. Recover the cluster from the snapshot so the marker ConfigMap exists again.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl create configmap pre-disaster --from-literal=k=v

alias e='etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key'
e snapshot save /tmp/disaster-snap.db
e snapshot status /tmp/disaster-snap.db --write-out=table

# simulate disaster (single-node lab ONLY):
sudo mv /etc/kubernetes/manifests/etcd.yaml /tmp/etcd.yaml.bak   # stop etcd first
sudo rm -rf /var/lib/etcd/*

sudo etcdutl snapshot restore /tmp/disaster-snap.db \
  --data-dir=/var/lib/etcd-restored

# point etcd.yaml at the restored data dir
sudo sed -i 's#/var/lib/etcd#/var/lib/etcd-restored#' /tmp/etcd.yaml.bak
sudo mv /tmp/etcd.yaml.bak /etc/kubernetes/manifests/etcd.yaml
```

**Verify:**
```bash
kubectl get pods -n kube-system | grep etcd        # Running again
kubectl get configmap pre-disaster                  # exists — proves restore worked
```

**Common mistake:** Restoring into the *same* `--data-dir` the manifest still references while etcd is (or was) running against it — always restore into a fresh directory and repoint the manifest, never overwrite live data files in place.

</details>

---

### Question 13 — Expired apiserver certificate
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** `kubectl` on the control-plane node fails with a TLS error resembling `x509: certificate has expired or is not yet valid`. Fix it without touching the cluster CA.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubeadm certs check-expiration                     # confirm which cert(s) are expired
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates

kubeadm certs renew apiserver                       # renew just the affected cert

# static pods hold the old cert in memory until restarted — force a reconcile:
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && \
  sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

**Verify:**
```bash
kubeadm certs check-expiration | grep apiserver     # new, future EXPIRES date
kubectl get nodes                                    # succeeds, no x509 errors
```

**Common mistake:** Renewing the certificate but never restarting the apiserver static pod — the running process keeps using the cert it loaded at startup until something forces a restart (moving the manifest out and back, or `crictl stop` on the container).

</details>

---

### Question 14 — Missing SAN after adding a load balancer
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 10 min
**Task:** A new load-balancer IP (`10.0.0.50`) was placed in front of the control plane. `kubectl` clients configured to talk to `https://10.0.0.50:6443` fail TLS validation, even though the apiserver cert is not expired. Fix the apiserver certificate so it's valid for the new address, without regenerating the CA.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -A2 "Subject Alternative Name"
# confirms 10.0.0.50 is absent from the SAN list — this is a SAN gap, not expiry

# Update kubeadm's cluster config to include the new SAN, then regenerate just the apiserver cert:
kubectl get cm kubeadm-config -n kube-system -o jsonpath='{.data.ClusterConfiguration}' > /tmp/kubeadm-cfg.yaml
# edit /tmp/kubeadm-cfg.yaml: add 10.0.0.50 under apiServer.certSANs
# (this file is now the raw ClusterConfiguration object itself — passing the full
#  `kubectl get cm ... -o yaml` dump instead would fail, since kubeadm's --config expects a
#  stream of kubeadm.k8s.io API objects, not a core/v1 ConfigMap wrapper)

kubeadm init phase certs apiserver --config /tmp/kubeadm-cfg.yaml

sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && \
  sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

**Verify:**
```bash
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -A2 "Subject Alternative Name"
# 10.0.0.50 now present
curl -k https://10.0.0.50:6443/healthz          # no TLS validation error
```

**Common mistake:** Reaching for `kubeadm certs renew apiserver` for this — a plain renew re-issues the cert with the *same* SAN list it already had. A missing SAN requires regenerating with an updated `certSANs` config via `kubeadm init phase certs apiserver`, not the renew subcommand.

</details>

---

### Question 15 — CoreDNS crash-looping from a Corefile edit
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** After a teammate "cleaned up" the `coredns` ConfigMap, DNS lookups from every pod in the cluster started timing out. `kubectl get pods -n kube-system -l k8s-app=kube-dns` shows both replicas in `CrashLoopBackOff`. Fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50   # Corefile syntax error reported here
kubectl get cm coredns -n kube-system -o yaml                 # spot the malformed plugin line

kubectl edit cm coredns -n kube-system     # fix the Corefile syntax
kubectl rollout restart deployment coredns -n kube-system   # ConfigMap edits aren't picked up instantly
```

**Verify:**
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns          # both Running, restarts stable
kubectl run dnstest --rm -it --image=busybox:1.36 -- nslookup kubernetes.default
```

**Common mistake:** Editing the ConfigMap and expecting an immediate fix — CoreDNS only reloads on its own polling interval (via the `reload` plugin) or on pod restart; if you need it instant, explicitly `rollout restart` the Deployment.

</details>

---

### Question 16 — CoreDNS refuses to start: forwarding loop detected
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** CoreDNS pods are stuck `CrashLoopBackOff` with logs mentioning a detected forwarding loop, even though nobody touched the Corefile. Diagnose the actual root cause (hint: it's not in the ConfigMap) and resolve it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
# "Loop (127.0.0.1:xxxxx -> :53) detected for zone \".\", see health plugin documentation..."

# Root cause: the node's /etc/resolv.conf points at systemd-resolved's local stub (127.0.0.53),
# and the Corefile's "forward . /etc/resolv.conf" ends up forwarding back to CoreDNS itself.
cat /etc/resolv.conf                                # confirms nameserver 127.0.0.53

# Fix at the kubelet level: point clusterDNS's upstream resolution at the real
# systemd-resolved config, not the stub file:
sudo cat /run/systemd/resolve/resolv.conf            # the actual upstream nameservers
sudo vi /var/lib/kubelet/config.yaml                 # set resolvConf to /run/systemd/resolve/resolv.conf
sudo systemctl restart kubelet
```

**Verify:**
```bash
kubectl delete pod -n kube-system -l k8s-app=kube-dns   # force recreate against new config
kubectl get pods -n kube-system -l k8s-app=kube-dns       # Running, no loop errors
kubectl run dnstest --rm -it --image=busybox:1.36 -- nslookup google.com
```

**Common mistake:** Trying to "fix" this by editing the Corefile's `forward` target instead of the node-level `resolvConf` setting — the Corefile is working exactly as configured; the actual bug is upstream, in what `/etc/resolv.conf` on the host resolves to.

</details>

---

### Question 17 — kubectl reports Forbidden for a service account
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** A CI pipeline running as ServiceAccount `deployer` in namespace `apps` gets `Error from server (Forbidden): deployments.apps is forbidden: User "system:serviceaccount:apps:deployer" cannot list resource "deployments"`. Grant exactly the access needed, nothing broader.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get rolebinding,role -n apps                      # confirm nothing currently grants this

kubectl create role deployer-role -n apps \
  --verb=get,list,watch,create,update,patch,delete \
  --resource=deployments

kubectl create rolebinding deployer-binding -n apps \
  --role=deployer-role \
  --serviceaccount=apps:deployer
```

**Verify:**
```bash
kubectl auth can-i list deployments -n apps --as=system:serviceaccount:apps:deployer   # yes
kubectl auth can-i delete secrets -n apps --as=system:serviceaccount:apps:deployer     # no — confirms scope wasn't over-granted
```

**Common mistake:** Reaching for a `ClusterRole`/`ClusterRoleBinding` out of habit when the task only requires access in one namespace — always default to the narrower `Role`/`RoleBinding` unless cross-namespace access is explicitly required.

</details>

---

### Question 18 — Pick the right diagnostic layer
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** A pod named `worker-app` has been stuck in `ContainerCreating` for 5 minutes. `kubectl logs worker-app` returns an error saying the container has not yet started. Identify the correct next diagnostic command (not `kubectl logs`) and use it to find the actual blocker.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe pod worker-app | tail -20        # Events section — check first, always
# e.g.: "Unable to attach or mount volumes: unmounted volumes=[cfg]..."

# If Events don't fully explain it, drop one layer to the node hosting the pod:
kubectl get pod worker-app -o wide                # find the node
ssh <node>
journalctl -u kubelet --since "10 min ago" -o cat | grep worker-app
```

**Verify:**
Confirm you can articulate *why* `kubectl logs` was the wrong first tool: the container process never started, so there is no log stream to read — `describe`'s Events (API-level) and `journalctl -u kubelet` (below the pod abstraction) are the only layers with relevant information before a container exists.

**Common mistake:** Repeatedly retrying `kubectl logs` on a pod that has never had a running container — if `describe` shows no container ever started, the fault is at the kubelet/CNI/volume-mount level, and `logs` will never produce anything useful no matter how many times you run it.

</details>

---

### Question 19 — Taint blocks scheduling
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Node `worker-5` was tainted `env=prod:NoSchedule`. A plain pod `probe-pod` (no tolerations) has been `Pending` ever since. Get it scheduled onto `worker-5` specifically, by tolerating the taint (do not remove the taint).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe pod probe-pod | grep -A3 Events    # "1 node(s) had taint {env: prod}, that the pod didn't tolerate"
kubectl describe node worker-5 | grep Taints

# NOTE: spec.tolerations can be appended to on a live pod, but spec.nodeSelector is immutable
# once the pod object exists — `kubectl edit`/`kubectl patch` adding it will be rejected
# ("Forbidden: pod updates may not change fields other than ..."). Since this pod must be
# pinned to worker-5 specifically, save its spec, delete it, and recreate it instead.
kubectl get pod probe-pod -o yaml > /tmp/probe-pod.yaml
vi /tmp/probe-pod.yaml
# under spec, add:
#   tolerations:
#   - key: "env"
#     operator: "Equal"
#     value: "prod"
#     effect: "NoSchedule"
#   nodeSelector:
#     kubernetes.io/hostname: worker-5
# also strip status:, metadata.resourceVersion/uid/creationTimestamp before reapplying

kubectl delete pod probe-pod
kubectl apply -f /tmp/probe-pod.yaml
```

**Verify:**
```bash
kubectl get pod probe-pod -o wide     # Running, NODE = worker-5
```

**Common mistake:** Reaching for `kubectl edit pod probe-pod` to add `nodeSelector` directly — `nodeSelector` is immutable on an existing Pod object and the API server rejects the change outright, unlike `tolerations`, which the API does permit appending to on a live pod. The other classic trap is a mismatched `value` or missing `effect`: `key`, `value`, and `effect` must all match the taint exactly (or use `operator: Exists` with no `value`), otherwise the pod silently stays `Pending` with the identical error message, and it's easy to misread that as "still not applied."

</details>

---

### Question 20 — Pod Pending due to oversized resource requests
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** A Deployment's pods request `memory: 8Gi` each, but no single node in the cluster has that much allocatable memory. Get the pods running without adding cluster capacity.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe pod <pod> | grep -A5 Events        # "0/3 nodes are available: 3 Insufficient memory"
kubectl describe node <any-node> | grep -A5 "Allocated resources"   # confirm real allocatable ceiling

kubectl set resources deployment <name> --requests=memory=512Mi --limits=memory=1Gi
```

**Verify:**
```bash
kubectl get pods -o wide                             # Running, NODE assigned
kubectl describe node <node> | grep -A10 "Allocated resources"   # headroom remains
```

**Common mistake:** Adjusting `limits` instead of `requests` — scheduling decisions are made purely against `requests`; a Pending pod's fix is almost always to right-size `requests`, not `limits`, unless capacity genuinely needs to be added.

</details>

---

### Question 21 — Service selector points at nothing
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Deployment `web` runs pods labeled `app: web`. Service `web-svc` was created selecting `app: web-frontend`. Requests to `web-svc` time out. Fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get endpoints web-svc              # ENDPOINTS column is empty — confirms selector problem
kubectl get pods --show-labels | grep web
kubectl get svc web-svc -o yaml | grep -A2 selector

kubectl patch svc web-svc -p '{"spec":{"selector":{"app":"web"}}}'
```

**Verify:**
```bash
kubectl get endpoints web-svc                                  # pod IPs now listed
kubectl run tmp --rm -it --image=busybox:1.36 -- wget -qO- web-svc:80
```

**Common mistake:** Reading through the entire Service YAML top-to-bottom looking for the bug — `kubectl get endpoints <svc>` is a single command that instantly confirms/rules out a selector mismatch before you even open the YAML.

</details>

---

### Question 22 — Endpoints populated, still unreachable
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Service `api-svc` has correct Endpoints listing pod IPs, but every request still fails to connect. The container's application actually listens on port `8080`. Fix the Service.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get endpoints api-svc                              # IPs present, but check the PORT column too
kubectl get svc api-svc -o yaml | grep -A5 ports            # targetPort: 80, doesn't match container

kubectl exec <a-backing-pod> -- ss -tlnp                    # confirm app really listens on 8080

kubectl patch svc api-svc -p '{"spec":{"ports":[{"port":80,"targetPort":8080}]}}'
```

**Verify:**
```bash
kubectl run tmp --rm -it --image=busybox:1.36 -- wget -qO- api-svc:80   # succeeds now
```

**Common mistake:** Stopping the investigation once `kubectl get endpoints` shows populated IPs — a non-empty Endpoints list only proves the *selector* is correct; it says nothing about whether `targetPort` actually matches what the container is listening on.

</details>

---

### Question 23 — Endpoints empty despite a correct selector
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Service `cache-svc`'s selector correctly matches pod labels, and the pods themselves show `Running`. `kubectl get endpoints cache-svc` is still empty. Find out why and fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get pods -l app=cache                          # Running, but check READY column: 0/1
kubectl describe pod <cache-pod> | grep -A8 Readiness   # readinessProbe failing — path/port wrong

kubectl edit deployment cache
# fix readinessProbe.httpGet.path (or port) to match what the app actually serves
```

**Verify:**
```bash
kubectl get pods -l app=cache                          # READY 1/1
kubectl get endpoints cache-svc                         # pod IPs now populated
```

**Common mistake:** Only checking `Running` status and concluding the pods are "healthy" — `Running` says nothing about readiness. A pod that's `Running` but `0/1 Ready` is deliberately excluded from Service Endpoints, and that's the actual root cause here, not the Service at all.

</details>

---

### Question 24 — DNS blocked by a default-deny NetworkPolicy
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Namespace `checkout` has a default-deny egress `NetworkPolicy`. Pods in that namespace can reach each other but `nslookup` for any name fails/times out. CoreDNS itself is healthy. Fix the namespace's networking so DNS resolution works, without removing the default-deny policy.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get networkpolicy -n checkout -o yaml
kubectl run dnstest --rm -it --image=busybox:1.36 -n checkout -- nslookup kubernetes.default   # times out
kubectl get pods -n kube-system -l k8s-app=kube-dns    # confirm CoreDNS itself is Running/healthy

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: checkout
spec:
  podSelector: {}
  policyTypes: ["Egress"]
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

**Verify:**
```bash
kubectl run dnstest --rm -it --image=busybox:1.36 -n checkout -- nslookup kubernetes.default   # resolves
```

**Common mistake:** Deleting the default-deny policy entirely to "make DNS work" — the correct fix is a narrow additional egress rule permitting UDP/TCP 53 to `kube-system`, preserving the rest of the default-deny posture the task presumably wants intact.

</details>

---

### Question 25 — Distinguishing a Pending fix from an OOMKilled fix
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Two unrelated pods are broken: `pod-a` is stuck `Pending` with `Insufficient memory` in its events; `pod-b` is `CrashLoopBackOff` with `OOMKilled` in its last-state. Fix each with the correct one of `requests`/`limits` — do not touch the wrong field on either.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe pod pod-a | grep -A3 Events           # Insufficient memory -> scheduling problem -> requests
kubectl patch deployment pod-a-deploy --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/memory","value":"256Mi"}]'

kubectl describe pod pod-b | grep -A5 "Last State"     # OOMKilled -> runtime ceiling problem -> limits
kubectl patch deployment pod-b-deploy --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"512Mi"}]'
```

**Verify:**
```bash
kubectl get pods -o wide         # pod-a: Running with NODE assigned; pod-b: Running, restarts stop climbing
kubectl top pods                  # both comfortably under their new limits
```

**Common mistake:** Raising `limits` on `pod-a` (does nothing for a scheduling-stage problem) or raising `requests` on `pod-b` (does nothing for a runtime OOM ceiling) — the two fields solve two different problems at two different lifecycle stages, and mixing them up is the single most common resource-troubleshooting mistake.

</details>

---

### Question 26 — Node evicting pods under DiskPressure
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** Pods on `worker-6` are being evicted repeatedly. `kubectl describe node worker-6` shows `DiskPressure: True`. Diagnose what's actually consuming disk and remediate without touching any pod's resource fields.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe node worker-6 | grep -A5 Conditions          # DiskPressure=True confirmed
kubectl get events -A --field-selector reason=Evicted | grep worker-6

ssh worker-6
df -h                                    # confirm which filesystem is full
crictl images                            # look for a large number of unused/dangling images
du -sh /var/lib/containerd/* 2>/dev/null | sort -h | tail

crictl rmi --prune                       # remove unused images not referenced by any container
```

**Verify:**
```bash
df -h                                                  # meaningful free space recovered
kubectl describe node worker-6 | grep -A5 Conditions    # DiskPressure=False
kubectl get events -A --field-selector reason=Evicted   # no new Evicted events after remediation
```

**Common mistake:** Reflexively lowering pod resource `requests`/`limits` because that's the usual "resource problem" fix — `DiskPressure` is a node-filesystem problem (usually stale images/logs), completely unrelated to a pod's CPU/memory fields, and adjusting those does nothing to free disk space.

</details>

---

### Question 27 — kubectl top fails cluster-wide
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** `kubectl top nodes` and `kubectl top pods` both return `error: Metrics API not available`. Diagnose and fix.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl get deployment metrics-server -n kube-system      # missing, or 0/1 Ready
kubectl get pods -n kube-system -l k8s-app=metrics-server
kubectl describe pod -n kube-system -l k8s-app=metrics-server   # e.g. CrashLoopBackOff, TLS error to kubelets

# common kubeadm-lab cause: metrics-server can't verify kubelet certs in a self-signed lab setup
kubectl edit deployment metrics-server -n kube-system
# add to the container args: --kubelet-insecure-tls   (lab-only workaround, not a production practice)
```

**Verify:**
```bash
kubectl get pods -n kube-system -l k8s-app=metrics-server   # Running
kubectl top nodes                                            # returns real numbers
```

**Common mistake:** Treating `kubectl top` failing as evidence of "no resource problem" — it's actually evidence of a *different* problem (the metrics pipeline itself), and should be fixed and re-checked before drawing any conclusion about actual resource pressure.

</details>

---

### Question 28 — CrashLoopBackOff from a memory limit that's too tight
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Pod `mem-hog` is `CrashLoopBackOff`. Diagnose the exact reason using `describe`, then fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl describe pod mem-hog | grep -A5 "Last State"   # Reason: OOMKilled, ExitCode: 137
kubectl get pod mem-hog -o jsonpath='{.spec.containers[0].resources}'

kubectl patch deployment mem-hog-deploy --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"256Mi"}]'
```

**Verify:**
```bash
kubectl get pod -l app=mem-hog -w    # Running, restart count stops climbing after ~60s
```

**Common mistake:** Reading only `kubectl logs mem-hog` (frequently empty, since the container is mid-restart) instead of `describe`'s `Last State: Terminated` block, which names `OOMKilled` and exit code `137` directly.

</details>

---

### Question 29 — CrashLoopBackOff with no current logs
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Pod `bad-cmd` is `CrashLoopBackOff`. `kubectl logs bad-cmd` prints nothing. Find the real error and fix the pod's `command`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
kubectl logs bad-cmd --previous              # the crashed attempt's actual output
# e.g.: "exec: \"/app/start.sh\": stat /app/start.sh: no such file or directory"

kubectl get pod bad-cmd -o jsonpath='{.spec.containers[0].command}'
kubectl edit deployment bad-cmd-deploy       # correct the command/args to the real entrypoint path
```

**Verify:**
```bash
kubectl get pod -l app=bad-cmd -w            # Running, stable across a 60s watch
```

**Common mistake:** Concluding "no logs, no clue" from a blank `kubectl logs` output — the current container is usually already mid-restart with an empty stream; `--previous` targets the crashed attempt and is almost always where the real error message lives.

</details>
