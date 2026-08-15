# Troubleshooting Scenarios — Cluster / Control-Plane / Security

*21 original "broken cluster" scenarios built from the general competencies in `01-exam-snapshot-and-priorities.md` (Troubleshooting 30%, Cluster Architecture 25%) and the topic files under `02-topics/` (`cluster-architecture-kubeadm-etcd.md`, `troubleshooting-playbook.md`, `rbac.md`). None of these reproduce a specific remembered real exam question — each is constructed purely from the underlying skill pattern (kubelet health, static pods, DNS, RBAC, certs, control-plane components, etcd, scheduling/resources, kubeconfig) so you can safely rebuild them on a real lab cluster. Work the **Symptom** first with only the tools a real exam terminal gives you; open the hint only if stuck for more than ~2x the time limit, and don't peek at Root Cause & Fix until you've made a real attempt.*

*Assumes containerd as the runtime, kubeadm-provisioned cluster, v1.35-ish. Run destructive setups only on disposable lab VMs, never on anything you rely on.*

---

### Scenario 1 — The node that stopped saying hello
**Time limit:** 6 min · **Skills tested:** kubelet health, systemd triage · **Points/difficulty:** Easy
**Symptom:** `kubectl get nodes` shows `worker-1` as `NotReady`. All pods that were running on it are stuck `Unknown`/`Terminating`. No recent deploys, no maintenance was scheduled.
**Setup (reproduce it yourself):**
```bash
# on worker-1
sudo systemctl stop kubelet
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl describe node worker-1` tells you *when* the node last heartbeated but not *why*. The answer lives one layer below the API — go check the node's own systemd state, not the API object.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The kubelet service was stopped on `worker-1`, so it stopped reporting Node status/heartbeats entirely.
**Fix:**
```bash
sudo systemctl status kubelet          # confirm inactive/dead
sudo systemctl enable --now kubelet
```
**Verify:**
```bash
kubectl get nodes                       # worker-1 back to Ready within ~40s
kubectl get pods -A -o wide --field-selector spec.nodeName=worker-1
```
**Common wrong turn candidates take:** Restarting containerd instead of checking kubelet first, or jumping straight to `kubeadm join` again assuming the node fell out of the cluster — it never left, kubelet was just not running.

</details>

---

### Scenario 2 — Ready-looking kubelet, dead node
**Time limit:** 10 min · **Skills tested:** kubelet config vs. CRI runtime wiring, `crictl`, `journalctl` · **Points/difficulty:** Medium
**Symptom:** `worker-2` is `NotReady`. `systemctl status kubelet` shows `active (running)` — no crash, no obvious error at a glance. Pods scheduled to it stay `ContainerCreating` forever.
**Setup (reproduce it yourself):**
```bash
# on worker-2
sudo sed -i 's#unix:///var/run/containerd/containerd.sock#unix:///var/run/containerd/containerd-x.sock#' \
  /var/lib/kubelet/kubeadm-flags.env
sudo systemctl daemon-reload && sudo systemctl restart kubelet
```

<details>
<summary>Hint (use only if stuck)</summary>

"Running" only tells you the process didn't exit — it says nothing about whether it can actually talk to the container runtime. Compare the endpoint kubelet is configured to use against where containerd is actually listening.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `kubeadm-flags.env`'s `--container-runtime-endpoint` points at a socket path that doesn't exist, so every CRI call (`RunPodSandbox`, etc.) fails, even though the kubelet process itself stays alive.
**Fix:**
```bash
journalctl -u kubelet -n 100 --no-pager | grep -i "runtime\|socket"
sudo sed -i 's#containerd-x.sock#containerd.sock#' /var/lib/kubelet/kubeadm-flags.env
sudo systemctl daemon-reload && sudo systemctl restart kubelet
```
**Verify:**
```bash
crictl info | head -5
kubectl get nodes                       # worker-2 Ready
```
**Common wrong turn candidates take:** Concluding "kubelet is fine, must be a hardware/network problem" and rebooting the node, which doesn't fix a config file typo and wastes the whole time budget.

</details>

---

### Scenario 3 — Kubelet won't even start on a "healthy-looking" node
**Time limit:** 10 min · **Skills tested:** cgroup driver consistency between kubelet and runtime · **Points/difficulty:** Medium
**Symptom:** `worker-3` is `NotReady`; `systemctl status kubelet` shows the unit repeatedly restarting/failing (`activating (auto-restart)`).
**Setup (reproduce it yourself):**
```bash
# on worker-3, force a mismatch with containerd's SystemdCgroup=true default
sudo sed -i 's/cgroupDriver: systemd/cgroupDriver: cgroupfs/' /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet
```

<details>
<summary>Hint (use only if stuck)</summary>

`journalctl -u kubelet` will name the exact mismatch. Cross-check the value against what the container runtime itself is configured for — one command tells you the runtime's view.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `KubeletConfiguration.cgroupDriver` (`cgroupfs`) no longer matches containerd's configured cgroup driver (`systemd`), so kubelet refuses to start cleanly.
**Fix:**
```bash
crictl info | grep -i cgroupDriver      # confirms containerd expects systemd
sudo sed -i 's/cgroupDriver: cgroupfs/cgroupDriver: systemd/' /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet
```
**Verify:**
```bash
kubectl get nodes                       # worker-3 Ready, stays Ready across a minute of watching
```
**Common wrong turn candidates take:** Reinstalling/downgrading the kubelet package, or editing containerd's `config.toml` instead of kubelet's own config — either "fixes" a driver that wasn't actually the broken one.

</details>

---

### Scenario 4 — A control-plane component that never even appears
**Time limit:** 7 min · **Skills tested:** static Pod manifest parsing, kubelet's manifest watch loop · **Points/difficulty:** Easy
**Symptom:** `kubectl get pods -n kube-system` doesn't list `kube-scheduler-<node>` at all — not `CrashLoopBackOff`, not `Pending`, simply absent, as if it never existed.
**Setup (reproduce it yourself):**
```bash
# on the control-plane node
sudo cp /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/kube-scheduler.yaml.bak
sudo python3 - <<'EOF'
import re
p = "/etc/kubernetes/manifests/kube-scheduler.yaml"
s = open(p).read()
# break indentation of the first list item under containers
s = s.replace("  - command:", " - command:", 1)
open(p, "w").write(s)
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

A mirror Pod only exists in the API if kubelet successfully *parsed* the manifest file. If it can't parse it at all, there's nothing to `describe` — go look at what kubelet itself logged about that file.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** Broken YAML indentation in `kube-scheduler.yaml` makes the file unparsable, so kubelet never creates a Pod (mirror or otherwise) for it at all.
**Fix:**
```bash
journalctl -u kubelet -n 100 --no-pager | grep -i "error\|invalid\|scheduler"
sudo cp /tmp/kube-scheduler.yaml.bak /etc/kubernetes/manifests/kube-scheduler.yaml
```
**Verify:**
```bash
kubectl get pods -n kube-system | grep scheduler   # appears, Running 1/1 within ~20s
```
**Common wrong turn candidates take:** Running `kubectl describe pod kube-scheduler-<node>` and getting "NotFound," then assuming the component was deliberately deleted and trying to recreate it from scratch with `kubeadm init phase` instead of just fixing the file that's already there.

</details>

---

### Scenario 5 — A control-plane component that crashloops forever
**Time limit:** 8 min · **Skills tested:** `crictl` log-first diagnosis, static Pod flag correctness · **Points/difficulty:** Medium
**Symptom:** `kube-controller-manager-<node>` shows `CrashLoopBackOff` with a climbing restart count. `kubectl get nodes` and most other `kubectl` commands still work fine.
**Setup (reproduce it yourself):**
```bash
sudo sed -i 's/--leader-elect=true/--leader-elect=truthy/' \
  /etc/kubernetes/manifests/kube-controller-manager.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl` still works because only this one static pod is broken. Go to the container runtime layer directly for the exact parse error rather than guessing which flag is wrong.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `--leader-elect` was set to an invalid boolean string (`truthy`), so the binary fails flag parsing on every start attempt.
**Fix:**
```bash
crictl ps -a | grep controller-manager
crictl logs <exited-container-id> | tail -20    # shows the flag parse error verbatim
sudo sed -i 's/--leader-elect=truthy/--leader-elect=true/' \
  /etc/kubernetes/manifests/kube-controller-manager.yaml
```
**Verify:**
```bash
crictl ps | grep controller-manager             # Running, stable restart count over 1 min
kubectl create deployment probe --image=nginx --replicas=1 --dry-run=server
```
**Common wrong turn candidates take:** Repeatedly restarting kubelet hoping the static pod "un-sticks" itself, instead of reading the one log line that names the exact bad flag.

</details>

---

### Scenario 6 — The apiserver that vanished
**Time limit:** 15 min · **Skills tested:** `crictl`/`journalctl`-only diagnosis when `kubectl` is fully dead, cert file paths · **Points/difficulty:** Hard
**Symptom:** Every `kubectl` command returns `The connection to the server <ip>:6443 was refused`. This is on the cluster's only control-plane node.
**Setup (reproduce it yourself):**
```bash
# on the control-plane node
sudo mv /etc/kubernetes/pki/apiserver.crt /etc/kubernetes/pki/apiserver.crt.bak
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl` is not available to you for this one — accept that immediately instead of retrying it. Everything you need is visible via the container runtime directly, on the node itself.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The apiserver's own TLS serving certificate file was moved away, so the container can't find the file its manifest's `--tls-cert-file` flag points at and exits immediately on every start attempt.
**Fix:**
```bash
crictl ps -a | grep apiserver
crictl logs <exited-id> | tail -20              # "no such file or directory" naming apiserver.crt
sudo mv /etc/kubernetes/pki/apiserver.crt.bak /etc/kubernetes/pki/apiserver.crt
```
**Verify:**
```bash
crictl ps | grep apiserver                      # Running, stable
kubectl get nodes                               # kubectl works again
```
**Common wrong turn candidates take:** Assuming the whole control plane needs rebuilding from a fresh `kubeadm init` because "kubectl is completely dead," when the actual fix is a two-minute file-path repair readable straight out of `crictl logs`.

</details>

---

### Scenario 7 — Names that never resolve
**Time limit:** 10 min · **Skills tested:** CoreDNS Corefile diagnosis, forward-loop detection · **Points/difficulty:** Medium
**Symptom:** Every pod's `nslookup`/`curl` against any in-cluster or external DNS name times out. `kubectl get pods -n kube-system -l k8s-app=kube-dns` shows the CoreDNS pods in `CrashLoopBackOff`.
**Setup (reproduce it yourself):**
```bash
kubectl -n kube-system get cm coredns -o yaml > /tmp/coredns-cm.bak.yaml
kubectl -n kube-system get svc kube-dns -o jsonpath='{.spec.clusterIP}'
# edit the Corefile so `forward` points back at the kube-dns Service's own ClusterIP (self-referential)
kubectl -n kube-system edit cm coredns
#   forward . /etc/resolv.conf   →   forward . <kube-dns-clusterIP>
kubectl -n kube-system rollout restart deployment coredns
```

<details>
<summary>Hint (use only if stuck)</summary>

CoreDNS's `loop` plugin exists specifically to detect and crash on exactly this kind of self-referential forwarding — read the CoreDNS pod's own logs, not the app pods that are failing to resolve names.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The Corefile's `forward` directive was pointed at CoreDNS's own Service IP, creating a forwarding loop; CoreDNS's `loop` plugin detects this and deliberately crashes rather than looping forever.
**Fix:**
```bash
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=30   # "Loop (127.0.0.1:...) detected..."
kubectl -n kube-system apply -f /tmp/coredns-cm.bak.yaml
kubectl -n kube-system rollout restart deployment coredns
```
**Verify:**
```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns          # Running, restarts stop climbing
kubectl run dnstest --rm -it --image=busybox:1.36 -- nslookup kubernetes.default
```
**Common wrong turn candidates take:** Scaling CoreDNS up/down or blaming a NetworkPolicy on port 53, when the CrashLoopBackOff itself (visible from `kubectl get pods -n kube-system`) already tells you CoreDNS isn't even staying up long enough for a NetworkPolicy to matter.

</details>

---

### Scenario 8 — Healthy CoreDNS, still no resolution
**Time limit:** 6 min · **Skills tested:** Service selector → Endpoints diagnosis applied to `kube-dns` itself · **Points/difficulty:** Easy
**Symptom:** DNS lookups from application pods time out, but `kubectl get pods -n kube-system -l k8s-app=kube-dns` shows both CoreDNS replicas `Running` and `Ready`.
**Setup (reproduce it yourself):**
```bash
kubectl -n kube-system patch svc kube-dns --type=json \
  -p='[{"op":"replace","path":"/spec/selector/k8s-app","value":"kube-dns-typo"}]'
```

<details>
<summary>Hint (use only if stuck)</summary>

CoreDNS being healthy and the `kube-dns` Service actually routing traffic to it are two separate facts. There's one command that proves whether they're actually connected.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The `kube-dns` Service's `spec.selector` no longer matches the CoreDNS pods' labels, so its Endpoints/EndpointSlice is empty — the Service has no backends even though the pods themselves are fine.
**Fix:**
```bash
kubectl -n kube-system get endpoints kube-dns          # empty ENDPOINTS column
kubectl -n kube-system patch svc kube-dns --type=json \
  -p='[{"op":"replace","path":"/spec/selector/k8s-app","value":"kube-dns"}]'
```
**Verify:**
```bash
kubectl -n kube-system get endpoints kube-dns          # pod IPs populated
kubectl run dnstest --rm -it --image=busybox:1.36 -- nslookup kubernetes.default
```
**Common wrong turn candidates take:** Restarting CoreDNS pods repeatedly (they were never broken) or editing the Corefile, when the actual break is one label field on the Service object.

</details>

---

### Scenario 9 — An app that's "not allowed" to do its job
**Time limit:** 6 min · **Skills tested:** `Forbidden` error reading, Role verb gaps · **Points/difficulty:** Easy
**Symptom:** A monitoring Pod's container logs repeat: `pods is forbidden: User "system:serviceaccount:app1:metrics-reader" cannot list resource "pods"`.
**Setup (reproduce it yourself):**
```bash
kubectl create ns app1
kubectl create sa metrics-reader -n app1
kubectl create role pod-viewer -n app1 --verb=get --resource=pods
kubectl create rolebinding pod-viewer-binding -n app1 --role=pod-viewer --serviceaccount=app1:metrics-reader
```

<details>
<summary>Hint (use only if stuck)</summary>

The error message already names the exact identity and exact missing capability — don't guess, reproduce that exact check with `kubectl auth can-i` before touching anything.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The `pod-viewer` Role only grants the `get` verb on `pods`, not `list`/`watch`, so the monitoring agent's `list` calls are correctly denied.
**Fix:**
```bash
kubectl auth can-i list pods --as=system:serviceaccount:app1:metrics-reader -n app1   # no
kubectl edit role pod-viewer -n app1
# verbs: ["get"]  →  verbs: ["get", "list", "watch"]
```
**Verify:**
```bash
kubectl auth can-i list pods --as=system:serviceaccount:app1:metrics-reader -n app1   # yes
kubectl auth can-i delete pods --as=system:serviceaccount:app1:metrics-reader -n app1 # no (still least-privilege)
```
**Common wrong turn candidates take:** Reaching for a `ClusterRoleBinding` to `cluster-admin` as a "just make it work" fix, which over-grants far beyond what the task/least-privilege intent requires.

</details>

---

### Scenario 10 — The binding that binds nothing
**Time limit:** 9 min · **Skills tested:** `RoleBinding.subjects[].namespace` correctness, distinguishing binding vs. rule bugs · **Points/difficulty:** Medium
**Symptom:** A Pod's `Forbidden` error persists even though `kubectl describe role` shows exactly the verbs/resources the task requires, and a `RoleBinding` referencing that Role clearly exists.
**Setup (reproduce it yourself):**
```bash
kubectl create ns app2
kubectl create ns app2-workloads
kubectl create sa report-bot -n app2-workloads
kubectl create role report-reader -n app2 --verb=get,list,watch --resource=configmaps
kubectl create rolebinding report-reader-binding -n app2 --role=report-reader \
  --serviceaccount=app2:report-bot     # wrong namespace for the SA reference on purpose
```

<details>
<summary>Hint (use only if stuck)</summary>

`roleRef` and `rules` both look completely correct here — that's the point. Check the one field that names *which* ServiceAccount, in *which* namespace, the binding is actually granting to.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The RoleBinding's `subjects[].namespace` points at `app2` instead of `app2-workloads`, so it's granting the Role to a ServiceAccount that doesn't exist in that namespace — not the real `report-bot` in `app2-workloads`.
**Fix:**
```bash
kubectl describe rolebinding report-reader-binding -n app2   # subjects: namespace: app2 (wrong)
kubectl auth can-i list configmaps --as=system:serviceaccount:app2-workloads:report-bot -n app2   # no
kubectl edit rolebinding report-reader-binding -n app2
# subjects[0].namespace: app2  →  app2-workloads
```
**Verify:**
```bash
kubectl auth can-i list configmaps --as=system:serviceaccount:app2-workloads:report-bot -n app2   # yes
```
**Common wrong turn candidates take:** Re-editing the Role's `rules` repeatedly (they were never the problem) instead of checking the binding's subject namespace field, since `subjects` is mutable via `edit` and easy to overlook as "probably fine."

</details>

---

### Scenario 11 — A binding pointing at a role that isn't there
**Time limit:** 8 min · **Skills tested:** `roleRef` correctness, immutability of `roleRef` · **Points/difficulty:** Medium
**Symptom:** `kubectl auth can-i list persistentvolumes --as=jane --as-group=storage-admins` returns `no`, even though a `ClusterRoleBinding` for `storage-admins` clearly exists and looks reasonable in `kubectl get clusterrolebinding`.
**Setup (reproduce it yourself):**
```bash
kubectl create clusterrole pv-viewer --verb=get,list,watch --resource=persistentvolumes
kubectl create clusterrolebinding pv-viewer-binding --clusterrole=pv-viewers --group=storage-admins
# note: --clusterrole=pv-viewers (typo, plural) — kubectl does NOT validate this exists at creation time
```

<details>
<summary>Hint (use only if stuck)</summary>

RBAC objects don't validate that a referenced Role/ClusterRole actually exists at creation time — a binding to a nonexistent role is created successfully and fails silently at *evaluation* time. Check whether the thing `roleRef` names actually exists.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The `ClusterRoleBinding`'s `roleRef.name` is `pv-viewers` (typo), but the actual `ClusterRole` is named `pv-viewer` — the binding references a role that doesn't exist, so it grants nothing.
**Fix:**
```bash
kubectl describe clusterrolebinding pv-viewer-binding | grep -A2 "Role:"
kubectl get clusterrole pv-viewers                       # NotFound — confirms the typo
kubectl delete clusterrolebinding pv-viewer-binding       # roleRef is immutable, must recreate
kubectl create clusterrolebinding pv-viewer-binding --clusterrole=pv-viewer --group=storage-admins
```
**Verify:**
```bash
kubectl auth can-i list persistentvolumes --as=jane --as-group=storage-admins   # yes
```
**Common wrong turn candidates take:** Trying `kubectl edit clusterrolebinding pv-viewer-binding` to fix `roleRef.name` in place — the API server rejects changes to `roleRef` (it's immutable), so the edit silently fails to apply and time gets burned re-trying it.

</details>

---

### Scenario 12 — The certificate that's valid for the wrong address
**Time limit:** 15 min · **Skills tested:** reading SANs, `kubeadm init phase certs`, distinguishing renew vs. re-issue · **Points/difficulty:** Hard
**Symptom:** `kubectl --server=https://10.0.0.50:6443 get nodes` (a newly added load-balancer front-end IP) fails with `x509: certificate is valid for 10.0.0.10, 127.0.0.1, ..., not 10.0.0.50`. The original control-plane IP still works fine.
**Setup (reproduce it yourself):**
```bash
# simulate: cluster was kubeadm-init'd without certSANs for the LB IP that's now in front of it
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -A2 "Subject Alternative Name"
# (confirm the LB IP 10.0.0.50 is genuinely absent from the list before "fixing" anything)
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubeadm certs renew apiserver` re-issues the cert with the *same* SAN list it already had — it will not add a brand-new address. You need the phase that actually regenerates SANs from a config file.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The apiserver's serving certificate was generated without the new load-balancer IP in its Subject Alternative Names, so TLS validation correctly rejects connections made to that address.
**Fix:**
```bash
cat <<EOF > /tmp/kubeadm-certsans.yaml
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
apiServer:
  certSANs:
  - "10.0.0.10"
  - "10.0.0.50"
EOF
sudo kubeadm init phase certs apiserver --config /tmp/kubeadm-certsans.yaml
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && \
  sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```
**Verify:**
```bash
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -A2 "Subject Alternative Name"
kubectl --server=https://10.0.0.50:6443 get nodes
```
**Common wrong turn candidates take:** Running `kubeadm certs renew all` and declaring victory — it reissues with the existing (still-incomplete) SAN list, so the exact same error reappears against the new address.

</details>

---

### Scenario 13 — Your own laptop is the broken thing, not the cluster
**Time limit:** 6 min · **Skills tested:** distinguishing a stale client kubeconfig from an actual cluster outage · **Points/difficulty:** Medium
**Symptom:** From your workstation, every `kubectl` command fails with an x509 error. From directly on the control-plane node, `crictl ps` shows every static pod `Running` and stable.
**Setup (reproduce it yourself):**
```bash
# on the control-plane node — rotate certs but "forget" to resync the workstation copy
sudo kubeadm certs renew all
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/ && sleep 5 && \
  sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
# ~/.kube/config on the workstation is now stale relative to the freshly rotated admin.conf
```

<details>
<summary>Hint (use only if stuck)</summary>

The cluster-side evidence (`crictl ps`, static pods stable) already tells you the control plane is healthy. If `kubectl` is still failing after that, the broken thing is probably the credential you're using to talk to it, not the cluster.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `kubeadm certs renew all` rotated the client certificate embedded in `/etc/kubernetes/admin.conf`, but `~/.kube/config` (a copy made at bootstrap time) still has the old, now-invalid client cert.
**Fix:**
```bash
diff <(sudo cat /etc/kubernetes/admin.conf) ~/.kube/config   # confirms drift
sudo cp -i /etc/kubernetes/admin.conf ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
```
**Verify:**
```bash
kubectl get nodes                       # works again, no x509 error
```
**Common wrong turn candidates take:** Assuming apiserver itself is broken and diving into static-pod-manifest debugging on the control-plane node — the node-side evidence already ruled that out; the fix is entirely on the client side.

</details>

---

### Scenario 14 — The apiserver that can't reach its own database
**Time limit:** 14 min · **Skills tested:** distinguishing an apiserver flag bug from an actual etcd outage, `crictl`-only diagnosis · **Points/difficulty:** Hard
**Symptom:** `kubectl` is completely unreachable (`connection refused`). On the control-plane node, `crictl ps -a` shows `etcd` `Running` and stable, but `kube-apiserver` repeatedly exits.
**Setup (reproduce it yourself):**
```bash
sudo sed -i 's/--etcd-servers=https:\/\/127.0.0.1:2379/--etcd-servers=https:\/\/127.0.0.1:2390/' \
  /etc/kubernetes/manifests/kube-apiserver.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

Notice which of the two components is actually stable and which is crashing — that already tells you which one to inspect. Then read what the crashing one's own log says about *why* it can't reach the thing it depends on.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `--etcd-servers` in the apiserver's own manifest points at the wrong port, so apiserver can never establish a connection to (a perfectly healthy) etcd and exits repeatedly.
**Fix:**
```bash
crictl ps -a | grep apiserver
crictl logs <exited-id> | tail -20     # "context deadline exceeded" dialing :2390
sudo sed -i 's/--etcd-servers=https:\/\/127.0.0.1:2390/--etcd-servers=https:\/\/127.0.0.1:2379/' \
  /etc/kubernetes/manifests/kube-apiserver.yaml
```
**Verify:**
```bash
crictl ps | grep apiserver              # Running, stable
kubectl get nodes
```
**Common wrong turn candidates take:** Spending the whole time budget diagnosing etcd itself (`etcdctl endpoint health`, alarm checks) when etcd was never the broken component — the `crictl ps -a` output already showed it was stable from the start.

</details>

---

### Scenario 15 — Deployments that create nothing
**Time limit:** 10 min · **Skills tested:** recognizing a controller-manager failure vs. a scheduler or app-level issue · **Points/difficulty:** Medium
**Symptom:** `kubectl get nodes` and `kubectl get pods` both work fine. `kubectl create deployment web --image=nginx --replicas=3` succeeds and the `Deployment` object exists, but `kubectl get rs` and `kubectl get pods` never show any ReplicaSet or Pod for it — not even `Pending`.
**Setup (reproduce it yourself):**
```bash
sudo sed -i 's#--kubeconfig=/etc/kubernetes/controller-manager.conf#--kubeconfig=/etc/kubernetes/controller-mgr.conf#' \
  /etc/kubernetes/manifests/kube-controller-manager.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

A Deployment object existing with zero child ReplicaSets is a very specific signature — it means the reconciliation loop that turns Deployments into ReplicaSets never ran, not that scheduling failed (scheduling would still produce a Pod object first).
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `kube-controller-manager`'s `--kubeconfig` flag points at a file that no longer exists (typo'd filename), so the container fails to start and no controllers — including the Deployment controller — are running.
**Fix:**
```bash
crictl ps -a | grep controller-manager
crictl logs <exited-id> | tail -20       # "no such file or directory" for the kubeconfig path
sudo sed -i 's#--kubeconfig=/etc/kubernetes/controller-mgr.conf#--kubeconfig=/etc/kubernetes/controller-manager.conf#' \
  /etc/kubernetes/manifests/kube-controller-manager.yaml
```
**Verify:**
```bash
crictl ps | grep controller-manager      # Running
kubectl get rs,pods -l app=web           # ReplicaSet and Pods now appear
```
**Common wrong turn candidates take:** Re-editing/re-applying the Deployment YAML repeatedly assuming a typo in its own spec, when the Deployment object itself was always correct — the reconciler that acts on it was simply not running.

</details>

---

### Scenario 16 — Pods that queue up forever with no explanation
**Time limit:** 7 min · **Skills tested:** recognizing "scheduler isn't running" vs. a real scheduling constraint · **Points/difficulty:** Easy
**Symptom:** Newly created Pods stay `Pending` indefinitely. `kubectl describe pod <name>` shows no `FailedScheduling` event at all — the Events section is essentially empty.
**Setup (reproduce it yourself):**
```bash
sudo sed -i 's/--leader-elect=true/--leader-elect=truee/' \
  /etc/kubernetes/manifests/kube-scheduler.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

A normal "nothing fits" scheduling failure always produces a `FailedScheduling` event with a specific reason. The total *absence* of any scheduling event — success or failure — points somewhere else entirely.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `kube-scheduler`'s manifest has a malformed `--leader-elect` flag value, so the scheduler binary fails to start at all — there's no scheduler running to emit any scheduling event, successful or failed.
**Fix:**
```bash
crictl ps -a | grep scheduler
crictl logs <exited-id> | tail -20        # flag parse error
sudo sed -i 's/--leader-elect=truee/--leader-elect=true/' \
  /etc/kubernetes/manifests/kube-scheduler.yaml
```
**Verify:**
```bash
crictl ps | grep scheduler                # Running, stable
kubectl get pods -o wide                  # previously-Pending pods now scheduled
```
**Common wrong turn candidates take:** Adding tolerations, node affinity, or resource-request changes to the stuck Pod's spec — none of that matters if there's no scheduler process alive to act on any Pod at all.

</details>

---

### Scenario 17 — Writes stop working, reads still fine
**Time limit:** 10 min · **Skills tested:** etcd alarm diagnosis, disarm step often forgotten · **Points/difficulty:** Medium
**Symptom:** `kubectl get pods`/`get nodes` work fine, but `kubectl create ns test` (and any other write) fails with a timeout or an `etcdserver` error surfaced through the apiserver.
**Setup (reproduce it yourself):**
```bash
# on the control-plane node, shrink etcd's backend quota to trigger NOSPACE quickly
sudo sed -i '/--data-dir=/a\    - --quota-backend-bytes=16777216' /etc/kubernetes/manifests/etcd.yaml
sleep 15
for i in $(seq 1 500); do
  kubectl create configmap filler-$i --from-literal=x=$(head -c 20000 </dev/urandom | base64) >/dev/null 2>&1
done
```

<details>
<summary>Hint (use only if stuck)</summary>

Reads working but writes failing is a very specific etcd signature. Check its own health/alarm state directly with its client tool rather than guessing from the apiserver side.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** etcd raised a `NOSPACE` alarm after its backend database filled up (in this drill, due to an artificially tiny quota); once raised, etcd puts itself into a read-only-for-writes state until the alarm is explicitly disarmed — freeing space alone is not enough.
**Fix:**
```bash
alias e='etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key'
e alarm list                              # NOSPACE
kubectl -n default delete configmap $(kubectl -n default get cm -o name | grep '^configmap/filler-')
sudo sed -i '/--quota-backend-bytes=16777216/d' /etc/kubernetes/manifests/etcd.yaml
e alarm disarm
```
**Verify:**
```bash
e alarm list                              # empty
kubectl create ns test && kubectl delete ns test   # both succeed
```
**Common wrong turn candidates take:** Freeing disk/backend space and stopping there — etcd remains in the alarmed, write-rejecting state until `alarm disarm` is run explicitly, even after space is available again.

</details>

---

### Scenario 18 — etcd that won't come back after "the incident"
**Time limit:** 18 min · **Skills tested:** full disaster-recovery flow, `etcdutl` restore, manifest hostPath repointing · **Points/difficulty:** Hard
**Symptom:** The cluster is completely unreachable via `kubectl`. On the control-plane node, `crictl ps -a | grep etcd` shows the etcd container repeatedly exiting.
**Setup (reproduce it yourself, lab-only, single-node etcd):**
```bash
# first, take a legitimate backup to have something to restore from
alias e='etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key'
kubectl create ns pre-incident
e snapshot save /opt/etcd-good.db
kubectl create ns post-incident        # created AFTER the snapshot, on purpose

# now simulate the "incident" — never do this on shared/production data
sudo mv /etc/kubernetes/manifests/etcd.yaml /tmp/
sudo rm -rf /var/lib/etcd/member/wal/*
sudo mv /tmp/etcd.yaml /etc/kubernetes/manifests/
```

<details>
<summary>Hint (use only if stuck)</summary>

`crictl logs` on the etcd container will make it clear the existing data directory is unrecoverable — the fix is not to repair it in place, but to bring up a fresh data directory from your most recent snapshot.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** etcd's write-ahead log directory was destroyed, so etcd cannot start against its existing `--data-dir` at all; the cluster's control plane is fully dependent on etcd, so nothing else works either.
**Fix:**
```bash
crictl logs $(crictl ps -a | awk '/etcd/{print $1; exit}')   # confirms wal/data corruption
sudo mv /etc/kubernetes/manifests/etcd.yaml /tmp/             # stop etcd
sudo etcdutl snapshot restore /opt/etcd-good.db --data-dir=/var/lib/etcd-restored
# repoint only the hostPath volume (not the container's --data-dir mount path) at the restored dir
sudo sed -i '0,/path: \/var\/lib\/etcd$/s#path: /var/lib/etcd$#path: /var/lib/etcd-restored#' /tmp/etcd.yaml
sudo mv /tmp/etcd.yaml /etc/kubernetes/manifests/
```
**Verify:**
```bash
crictl ps | grep etcd                           # fresh, stable container
kubectl get ns pre-incident                     # exists — restored
kubectl get ns post-incident                    # NotFound — proves point-in-time restore, not a lucky recovery
```
**Common wrong turn candidates take:** Trying to repair or `fsck` the existing corrupted data directory instead of accepting data loss and restoring from the snapshot; or using `etcdctl snapshot restore` (removed since etcd 3.5) instead of `etcdutl`.

</details>

---

### Scenario 19 — The pod nothing wants to schedule
**Time limit:** 6 min · **Skills tested:** reading `FailedScheduling` verbatim, requests vs. limits · **Points/difficulty:** Easy
**Symptom:** A newly created Deployment's Pods sit `Pending`. `kubectl get nodes` shows two healthy `Ready` nodes.
**Setup (reproduce it yourself, on small lab nodes e.g. 2 vCPU each):**
```bash
kubectl create deployment cpu-hog --image=nginx --replicas=1 \
  --dry-run=client -o yaml > /tmp/cpu-hog.yaml
kubectl patch -f /tmp/cpu-hog.yaml --local --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/resources","value":{"requests":{"cpu":"4"}}}]' \
  --dry-run=client -o yaml > /tmp/cpu-hog2.yaml
kubectl apply -f /tmp/cpu-hog2.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

The Events section of `describe pod` names the exact resource and the exact numbers involved per node — read it literally before touching any YAML.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The Pod's `resources.requests.cpu` (4 full cores) exceeds the allocatable CPU on every node in the cluster, so the scheduler correctly can't place it anywhere.
**Fix:**
```bash
kubectl describe pod -l app=cpu-hog | grep -A5 Events   # "0/2 nodes are available: 2 Insufficient cpu"
kubectl set resources deployment cpu-hog --requests=cpu=250m
```
**Verify:**
```bash
kubectl get pods -l app=cpu-hog -o wide     # Running, NODE assigned
```
**Common wrong turn candidates take:** Lowering `resources.limits.cpu` instead of `requests.cpu` — limits don't factor into the scheduler's bin-packing decision at all, so the Pod stays Pending unchanged.

</details>

---

### Scenario 20 — Pods rejected before they're even created
**Time limit:** 8 min · **Skills tested:** LimitRange admission behavior vs. ResourceQuota, vs. scheduler-level Pending · **Points/difficulty:** Medium
**Symptom:** `kubectl apply -f deployment.yaml` in namespace `constrained` returns an immediate error from the API server — no Pod, ReplicaSet event, or `Pending` state ever appears; the object is rejected outright at creation time.
**Setup (reproduce it yourself):**
```bash
kubectl create ns constrained
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-cap
  namespace: constrained
spec:
  limits:
  - type: Container
    max:
      cpu: "200m"
EOF
kubectl create deployment capped --image=nginx -n constrained \
  --dry-run=client -o yaml > /tmp/capped.yaml
kubectl patch -f /tmp/capped.yaml --local --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/resources","value":{"limits":{"cpu":"500m"}}}]' \
  --dry-run=client -o yaml | kubectl apply -f -
```

<details>
<summary>Hint (use only if stuck)</summary>

The failure happens at admission time, before scheduling is even relevant — that's a strong signal it isn't `FailedScheduling` at all. Check what governs the *maximum allowed* resource values in this specific namespace.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** A `LimitRange` in the `constrained` namespace caps container CPU limits at `200m`; the Deployment's Pod template requests `500m`, which the LimitRange admission controller rejects at creation time rather than letting it become `Pending`.
**Fix:**
```bash
kubectl get limitrange -n constrained -o yaml     # shows max cpu: 200m
kubectl patch deployment capped -n constrained --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/cpu","value":"150m"}]'
```
**Verify:**
```bash
kubectl get pods -n constrained -l app=capped     # Running
```
**Common wrong turn candidates take:** Checking `ResourceQuota` (a different, aggregate-across-namespace mechanism with a similarly-shaped error) instead of `LimitRange` (a per-object ceiling) — the two produce easily-confused admission error text.

</details>

---

### Scenario 21 — You've been debugging the wrong cluster the whole time
**Time limit:** 6 min · **Skills tested:** `kubectl config` fluency, recognizing a client-side misdirection instead of a cluster fault · **Points/difficulty:** Easy
**Symptom:** Changes you apply with `kubectl apply` seem to "not take" — a Deployment you scaled to 5 replicas keeps showing 2, a namespace you deleted keeps coming back, `kubectl get nodes` lists node names you don't recognize as belonging to this environment at all.
**Setup (reproduce it yourself):**
```bash
kubectl config set-context lab-2 --cluster=lab-2-cluster --user=lab-2-admin
kubectl config set-cluster lab-2-cluster --server=https://10.0.0.99:6443 --insecure-skip-tls-verify=true
kubectl config set-credentials lab-2-admin --client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt \
  --client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key
kubectl config use-context lab-2       # silently points at a different/stale cluster IP
```

<details>
<summary>Hint (use only if stuck)</summary>

Before troubleshooting any object inside the cluster, confirm you're actually talking to the cluster you think you are. There's a single command that shows exactly which context and server URL is currently active.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The active `kubectl` context (`lab-2`) points at a different (or stale/decommissioned) control-plane address than the one you intend to operate on, so every command is silently succeeding or failing against the wrong cluster.
**Fix:**
```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
kubectl config use-context <intended-context>
```
**Verify:**
```bash
kubectl get nodes                        # node names now match the expected environment
kubectl config current-context            # matches intended cluster
```
**Common wrong turn candidates take:** Troubleshooting the "broken" object (re-scaling the Deployment, re-deleting the namespace) repeatedly against what turns out to be an entirely different cluster, burning the whole time budget before ever questioning which cluster is actually being talked to.

</details>
