# Docs Navigation & Linux Skills Cheatsheet

*Purpose: this file is not for learning concepts (see `02-topics/*.md` for that) — it's for **fast retrieval under a clock**. Two things only: (1) where in the allowed docs a needed example actually lives, so you don't waste exam minutes searching, and (2) a one-line refresher per Linux command so raw syntax doesn't cost you time. Allowed docs domains for CKA: `kubernetes.io/docs/*` and, CKA-specifically, `gateway-api.sigs.k8s.io`. `etcd.io` is generally *not* on the allowed list — rely on the kubeadm-side etcd pages on kubernetes.io instead.*

---

# Part 1 — Kubernetes Docs Navigation Map

For each row: **what I'd search** (the literal phrase to type into the in-page/site search or recall by title) and **where the example lives** (the doc section/page that has the copy-pasteable YAML or command block).

## NetworkPolicy
- **Search:** "network policies" or "declare network policy"
- **Lives at:** Concepts → Services, Networking, and DNS → **Network Policies**. This page itself has default-deny-all-ingress, default-deny-all-egress, and allow-from-namespace example blocks near the bottom — don't hand-write from memory, copy and edit the podSelector/policyTypes. Remember: no dry-run/imperative generator exists for this object, so this page *is* your generator.

## PersistentVolume / PersistentVolumeClaim (static provisioning)
- **Search:** "configure a pod to use a persistentvolume for storage" or "persistent volumes"
- **Lives at:** Tasks → Configure Pods and Containers → **Configure a Pod to Use a PersistentVolume for Storage** (has the full hostPath PV + PVC + Pod trio verbatim) and Concepts → Storage → **Persistent Volumes** (for the field reference: accessModes, reclaimPolicy, volumeMode, phases).

## StorageClass / dynamic provisioning
- **Search:** "storage classes"
- **Lives at:** Concepts → Storage → **Storage Classes** — has the `is-default-class` annotation example, `volumeBindingMode`, and per-provisioner parameter tables. This is also where `allowVolumeExpansion` is documented.

## RBAC (Role/RoleBinding/ClusterRole/ClusterRoleBinding)
- **Search:** "using rbac authorization"
- **Lives at:** Reference → Access Authn Authz → **Using RBAC Authorization** — has copy-pasteable Role/RoleBinding/ClusterRole/ClusterRoleBinding YAML, the built-in ClusterRoles table (`cluster-admin`/`admin`/`edit`/`view`), and a dedicated "Referring to Resources" section for subresource/nonResourceURL syntax. Also has a **Troubleshooting** subsection near the bottom worth knowing by name.

## Init Containers
- **Search:** "init containers"
- **Lives at:** Concepts → Workloads → Pods → **Init Containers** — has the wait-for-service and shared-emptyDir examples ready to adapt.

## Native Sidecar Containers
- **Search:** "sidecar containers"
- **Lives at:** Concepts → Workloads → Pods → **Sidecar Containers** (distinct page from Init Containers as of the docs' current structure) — shows the `restartPolicy: Always` inside `initContainers[]` pattern.

## DaemonSet
- **Search:** "daemonset"
- **Lives at:** Concepts → Workloads → Controllers → **DaemonSet** — has the tolerations-for-control-plane example and `updateStrategy` (RollingUpdate vs OnDelete) fields.

## Taints and Tolerations
- **Search:** "taints and tolerations"
- **Lives at:** Concepts → Scheduling, Preemption and Eviction → **Taints and Tolerations** — has the `kubectl taint` command syntax plus the toleration YAML block with `operator: Exists` vs `Equal` examples, and the full effects table (NoSchedule/PreferNoSchedule/NoExecute).

## Node Affinity / Pod Affinity & Anti-Affinity
- **Search:** "assign pods to nodes using node affinity"
- **Lives at:** Concepts → Scheduling, Preemption and Eviction → **Assign Pods to Nodes Using Node Affinity** — covers node affinity in full, and pod affinity/anti-affinity now lives on the same page (current docs structure merged them) with the `topologyKey`/`labelSelector` examples.

## Pod Topology Spread Constraints
- **Search:** "pod topology spread constraints"
- **Lives at:** Concepts → Scheduling, Preemption and Eviction → **Pod Topology Spread Constraints** — the related-but-distinct alternative to pod anti-affinity; know this page exists even if affinity is your default tool.

## Manual Scheduling / nodeName
- **Search:** `kubectl explain pod.spec.nodeName` (faster than the website for this one — it's a single field, not a whole concept page)
- **Lives at:** No dedicated concept page; the field reference lives in **kubectl explain** output directly, which is faster to reach than searching the website mid-exam.

## kubeadm init / join / cluster bring-up
- **Search:** "creating a cluster with kubeadm"
- **Lives at:** Setup → Production Environment → Tools → kubeadm → **Creating a cluster with kubeadm** — has the full init/join flag reference, `--pod-network-cidr`, `--control-plane-endpoint`, `--upload-certs`, and the token/discovery-hash join command shape.

## kubeadm upgrade
- **Search:** "upgrading kubeadm clusters"
- **Lives at:** Tasks → Administer a Cluster → **Upgrading kubeadm clusters** — has the exact per-node sequence (`upgrade plan` → `upgrade apply` on first CP node → `upgrade node` on the rest → drain/upgrade-kubelet/uncordon per node). Pair with Reference → **Version Skew Policy** for the exact skew table if a task's version gap looks unusual.

## Certificate management (kubeadm)
- **Search:** "certificate management with kubeadm" and "pki certificates and requirements"
- **Lives at:** Setup → kubeadm → **Certificate Management with kubeadm** (the `kubeadm certs check-expiration`/`renew` commands) and the separate **PKI certificates and requirements** reference page (file paths under `/etc/kubernetes/pki/`, which cert backs which component).

## etcd backup and restore
- **Search:** "operating etcd clusters for kubernetes"
- **Lives at:** Tasks → Administer a Cluster → **Operating etcd clusters for Kubernetes** — has the `etcdctl snapshot save`/`etcdutl snapshot restore` commands with TLS flags spelled out. This page (not etcd.io, which isn't reliably in-scope for the exam's allowed docs) is the one to actually search for live.

## Static Pods
- **Search:** "static pods"
- **Lives at:** Concepts → Workloads → Pods → **Static Pods** — explains `staticPodPath`, mirror pods, and the manifest-file-is-truth model; short page, worth a full read-through once, not just a lookup.

## Safely drain a node (cordon/drain/PDB interaction)
- **Search:** "safely drain a node"
- **Lives at:** Tasks → Administer a Cluster → **Safely Drain a Node** — has the exact `kubectl drain` flag set (`--ignore-daemonsets`, `--delete-emptydir-data`, `--force`) and explains the eviction-API-vs-PDB relationship. Pair with Concepts → Workloads → Pods → **Disruptions** for PDB semantics/`minAvailable`/`maxUnavailable`.

## Services (ClusterIP/NodePort/LoadBalancer/ExternalName)
- **Search:** "service" (Concepts, not Tasks)
- **Lives at:** Concepts → Services, Networking, and DNS → **Service** — has every Service type's YAML plus the "Debugging Services" subsection at the bottom, which is the fastest checklist for "Service exists but traffic doesn't reach the Pod."

## Ingress
- **Search:** "ingress" then separately "ingress controllers"
- **Lives at:** Concepts → Services, Networking, and DNS → **Ingress** (object YAML, `pathType`, TLS block) and the sibling **Ingress Controllers** page (the reminder that a controller is a separately-installed workload, not built in).

## Gateway API / HTTPRoute
- **Search:** "httproute" or "gateway api getting started"
- **Lives at:** **gateway-api.sigs.k8s.io** (separate domain, explicitly allowed for CKA) → Guides → **HTTPRoute**, and the **API Reference** for the exact field names (`parentRefs`, `backendRefs[].weight`, `ReferenceGrant`). Do not expect this material on kubernetes.io itself beyond a high-level comparison page.

## CoreDNS / DNS debugging
- **Search:** "debug dns resolution"
- **Lives at:** Tasks → Administer a Cluster → **Debug DNS Resolution** — this page's step order (CoreDNS pods → Service/Endpoints → Corefile → test-pod nslookup) is close to a verbatim checklist worth reproducing.

## CNI / Pod networking install
- **Search:** "installing addons" (for the generic "how CNI add-ons fit in" framing) — the actual CNI vendor page (flannel/Calico) is *not* always on kubernetes.io, so know the CIDR field names from memory rather than planning to search for them live.
- **Lives at:** Tasks → Administer a Cluster → Networking → **Installing Addons**; cross-reference Concepts → Cluster Architecture → **Nodes** for the CIDR/podCIDR field on the Node object itself.

## Probes (liveness/readiness/startup)
- **Search:** "configure liveness readiness startup probes"
- **Lives at:** Tasks → Configure Pods and Containers → **Configure Liveness, Readiness and Startup Probes** — has ready-to-adapt `httpGet`/`exec`/`tcpSocket`/`grpc` blocks for all three probe types.

## ConfigMaps / Secrets
- **Search:** "configmap" / "secret" (Concepts pages, not Tasks, for the field reference; Tasks → "Distribute Credentials Securely" only if the private-registry angle comes up)
- **Lives at:** Concepts → Configuration → **ConfigMaps** and **Secrets** — both have the env-var vs volume-mount consumption examples and (for Secrets) the built-in `type` values.

## Resource Requests/Limits, LimitRange, ResourceQuota
- **Search:** "resource management for pods and containers" then separately "limit ranges" / "resource quotas"
- **Lives at:** Concepts → Workloads → Pods → **Resource Management for Pods and Containers** (requests/limits/QoS classes) plus Concepts → Policies → **Limit Ranges** and **Resource Quotas** for the namespace-admin side.

## Jobs / CronJobs
- **Search:** "jobs run to completion" / "cronjob"
- **Lives at:** Concepts → Workloads → Controllers → **Job** (completions/parallelism/backoffLimit/completionMode) and **CronJob** (schedule/concurrencyPolicy/timeZone).

## StatefulSets
- **Search:** "statefulsets"
- **Lives at:** Concepts → Workloads → Controllers → **StatefulSets** — has the headless-Service requirement, `volumeClaimTemplates`, and `podManagementPolicy` documented together.

## Deployments / Rolling Updates
- **Search:** "deployments" (the concept page, which includes the updating/rollback section inline)
- **Lives at:** Concepts → Workloads → Controllers → **Deployments** — the "Updating a Deployment" and "Rolling Back a Deployment" subsections are on this same page, not a separate one; search in-page (Ctrl/Cmd-F) rather than hunting for a distinct rollout page.

## Troubleshooting hub (general)
- **Search:** "troubleshooting" / "debug pods" / "debug running pods" / "determine the reason for pod failure"
- **Lives at:** Tasks → Troubleshooting — this whole tree (Debug Pods, Debug Services, Debug a StatefulSet, Debug Running Pods, Determine the Reason for Pod Failure) is the fastest place to re-derive a diagnostic order if you blank under pressure; each sub-page is short and command-heavy by design.

## kubectl quick reference
- **Search:** "kubectl cheat sheet"
- **Lives at:** Reference → **kubectl Cheat Sheet** — the single fastest page for syntax you've half-forgotten (jsonpath examples, `--field-selector`, `--sort-by`, resource shortnames); bookmark this mentally as your first stop for "what's the exact flag" questions that aren't concept-specific.

## kubectl explain (not a doc page, but faster than one)
- **Search:** N/A — this is a CLI substitute for docs search
- **Use it for:** any exact field-nesting question (`kubectl explain pod.spec.affinity.podAntiAffinity --recursive`, `kubectl explain deployment.spec.strategy.rollingUpdate`) — faster than opening a browser tab for field-name/nesting recall specifically, even though the conceptual explanation still lives on kubernetes.io.

---

# Part 2 — Linux Skills for CKA

*Each line is scoped to how the command actually shows up in a CKA task — not a general tutorial. `k` = `kubectl` alias assumed set up per your exam routine.*

**systemctl** — Manage/inspect the kubelet and containerd host services on a node; almost every "node NotReady" or "static pod won't start" task ends with `systemctl status kubelet containerd` and, after any config-file edit, `systemctl daemon-reload && systemctl restart kubelet`.

**journalctl** — Read systemd service logs when `kubectl logs` isn't an option (kubelet itself, containerd, or a fully-down apiserver); exam-typical: `journalctl -u kubelet -n 200 --no-pager` or `journalctl -u kubelet -f` to watch it pick up a manifest fix live.

**ps** — Confirm a process is actually running and inspect its exact invocation flags on a node, e.g. `ps -ef | grep kubelet | grep -o '\--config=\S*'` to find the kubelet's config file path when you're not sure it's the default.

**ss** — Check what's actually listening on a port on a node/container, the modern replacement for `netstat`; exam-typical: `ss -tlnp | grep 6443` to confirm apiserver is bound, or inside a Pod via `k exec` to catch a targetPort mismatch.

**ip** — Inspect node-level networking state during CNI troubleshooting; exam-typical: `ip addr show` to confirm a `cni0`/`flannel.1`/`cali*` interface exists, and `ip route` to confirm a route to another node's Pod CIDR is present.

**curl** — Functional-test a Service/Ingress/Gateway from a throwaway Pod or a node; exam-typical: `curl -H "Host: app.example.com" http://<node-ip>:<nodePort>/` to prove Ingress routing end-to-end, or `curl --max-time 3 <svc>.<ns>.svc.cluster.local:<port>` to distinguish a NetworkPolicy timeout from a real error.

**wget** — Same functional-test role as `curl` but frequently the *only* HTTP client actually present in minimal images like `busybox`; exam-typical: `wget -qO- <svc>.<ns>.svc.cluster.local:<port>` from inside a `busybox` test Pod when `curl` isn't installed there.

**grep** — Filter `kubectl`/`crictl`/`journalctl`/file output down to the one line that matters under time pressure; exam-typical: `crictl ps -a | grep -E 'apiserver|scheduler|controller|etcd'` or `journalctl -u kubelet | grep -i "x509\|certificate"`.

**awk** — Pull a specific column out of plain-text command output when `-o jsonpath`/`-o custom-columns` isn't handy or you're working outside `kubectl`; exam-typical: `ps -ef | awk '/kubelet/{print $NF}'` or slicing a `df -h`/`free -h` column during a disk/memory-pressure investigation.

**sed** — Quick in-place text substitution on a manifest or config file without opening an editor; exam-typical: `sed -i 's/1\.34/1.35/' somefile.yaml`, though for static pod manifests you'll usually still open `vi` to be safe about YAML indentation.

**cat** — Dump a whole file inline for a quick read, the default way to inspect static pod manifests and kubelet config; exam-typical: `cat /etc/kubernetes/manifests/kube-apiserver.yaml` or `cat /var/lib/kubelet/kubeadm-flags.env`.

**less** — Page through long output you don't want to scroll past, especially `crictl inspect`/`kubectl get ... -o yaml` dumps; exam-typical: `crictl inspect <containerID> | less` to search (`/etcd-servers`) inside a large JSON blob.

**tail** — Grab the most recent lines of a log or file, or follow it live; exam-typical: `journalctl -u kubelet -n 200 --no-pager` (recent lines) or `crictl logs -f <id>` isn't `tail` per se, but `tail -f /var/log/pods/.../*.log` shows up when `crictl`/`kubectl logs` aren't available.

**head** — Grab the first lines of large output, mostly for a quick sanity peek at file structure; exam-typical: `head -20 /etc/kubernetes/manifests/etcd.yaml` before deciding whether to `cat` the whole thing.

**find** — Locate a file whose exact path you don't remember on a node; exam-typical: `find /etc/kubernetes -name "*.conf"` to enumerate kubeconfigs, or `find / -name kubelet.sock 2>/dev/null` when chasing a CRI socket path mismatch.

**ls** — Confirm a directory's contents before assuming a file exists (or doesn't); exam-typical: `ls /etc/kubernetes/manifests/` to see which static pods are currently active, or `ls /etc/cni/net.d/` to confirm CNI config is actually present.

**cp** — Copy files, most commonly the kubeadm admin kubeconfig into place; exam-typical: `cp -i /etc/kubernetes/admin.conf $HOME/.kube/config` right after `kubeadm init`, or `cp` a snapshot file between nodes when etcd isn't co-located.

**mv** — The canonical "restart a static pod" trick (move manifest out, then back in) and general file relocation; exam-typical: `mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/ && mv /tmp/kube-scheduler.yaml /etc/kubernetes/manifests/`.

**mkdir** — Create a directory before writing into it, most often for `.kube/config` setup or a new PV's `hostPath` backing directory; exam-typical: `mkdir -p $HOME/.kube` or `mkdir -p /mnt/data/pv-static-01` before a static-provisioning task expects that path to exist.

**chmod** — Set file permissions, occasionally required on a mounted Secret's `defaultMode` equivalent at the host level, or on a kubeconfig; exam-typical: `chmod 600 /etc/kubernetes/admin.conf` if a task checks kubeconfig permission hygiene, or fixing a `hostPath` directory's mode so a non-root container can write to it.

**chown** — Fix file ownership, most commonly right after copying `admin.conf`; exam-typical: `chown $(id -u):$(id -g) $HOME/.kube/config` so a non-root exam user's `kubectl` actually works.

**openssl** — Inspect certificate metadata directly from disk (or live) when `kubeadm certs check-expiration` isn't enough or the apiserver itself is down; exam-typical: `openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates -subject` or `openssl s_client -connect <ip>:6443 -showcerts` to confirm the live-served cert actually changed after a renewal.

**crictl** — The CRI-level escape hatch that works even when `kubectl`/the apiserver is fully unreachable; exam-typical: `crictl ps -a` to see every container including exited ones, `crictl logs <id>` for the crash reason, and `crictl inspect <id> | less` to read the exact config (mounts, env, command) the runtime actually launched with.
