# CKA Final Cheat Sheet — Read This Right Before The Exam

*Ultra-compact. One-liners only. If you need the "why," it's in `02-topics/*` and `03-cheatsheets/*`.
Cross-check nothing here against v1.36 drift — verify version-sensitive bits live if time permits.*

---

## Aliases & env vars — type these first, every session

```bash
alias k=kubectl
export do="--dry-run=client -o yaml"
export now="--force --grace-period 0"
alias e='etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key'
export ETCDCTL_API=3   # harmless, default since etcd 3.4
```

Other useful env vars:
- `KUBECONFIG=/path/to/config` — point kubectl at a specific/merged kubeconfig (colon-separate multiple paths to merge for `config view`).
- `KUBE_EDITOR=vi` — force the editor `k edit` opens (if `$EDITOR` is unset/wrong).

---

## kubectl commands — highest-frequency one-liners

```bash
k get pods -A -o wide
k get all -n <ns>
k get pods -o wide --field-selector spec.nodeName=<node>
k get events -A --sort-by=.lastTimestamp
k get events --field-selector reason=FailedScheduling
k describe pod <name>            # Events at bottom = answer key 90% of the time
k describe node <name>           # Conditions + Taints + Allocated resources
k describe svc <name>            # Selector + Endpoints in one shot
k logs <pod> --previous          # crashed attempt — real answer for CrashLoopBackOff
k logs <pod> -c <container>
k exec -it <pod> -- /bin/sh
k top nodes ; k top pods -A --sort-by=memory
k rollout status deployment/web --timeout=60s
k rollout undo deployment/web --to-revision=2
k rollout restart deployment/web       # force env-based ConfigMap/Secret pickup
k scale deployment/web --replicas=5
k label nodes node01 disktype=ssd --overwrite
k label nodes node01 disktype-                    # trailing dash, no space = remove
k taint nodes node01 key1=value1:NoSchedule
k taint nodes node01 key1=value1:NoSchedule-      # remove: key+effect must match
k cordon <node> ; k drain <node> --ignore-daemonsets --delete-emptydir-data --force ; k uncordon <node>
k get pdb -A                       # check BEFORE draining
k delete pod mypod $now            # stuck-terminating pods
k delete statefulset <name> --cascade=orphan
k replace --force -f pod.yaml      # delete+recreate when field is immutable (selector, nodeName)
k auth can-i <verb> <resource> --as=<id> -n <ns>     # ALWAYS pass -n explicitly
k auth can-i --list --as=system:serviceaccount:<ns>:<sa>
k config view --minify -o jsonpath='{.contexts[0].context.user}'
k config set-context --current --namespace=<ns>
k explain pod.spec.affinity.podAntiAffinity --recursive
k apply -k <kustomization-dir>      # Kustomize — no allowed CKA docs domain, know cold
```

---

## Imperative generators — generate, edit only what's missing, apply

```bash
k run mypod --image=nginx --restart=Never $do > pod.yaml
k run tmp --rm -it --image=busybox:1.36 -- wget -qO- <svc>.<ns>.svc.cluster.local:<port>
k create deployment web --image=nginx:1.25 --replicas=3 $do > deploy.yaml
k create job myjob --image=busybox $do -- /bin/sh -c "echo hi" > job.yaml
k create cronjob mycron --image=busybox --schedule="*/1 * * * *" $do -- date > cj.yaml
k create job --from=cronjob/mycron manual-run-1
k create ns shop
k create configmap myconfig --from-literal=key=value --from-file=app.conf
k create secret generic mysecret --from-literal=password=abc123
k create secret docker-registry regcred --docker-server=<s> --docker-username=<u> --docker-password=<p> --docker-email=<e>
k create secret tls mytls --cert=path/to/cert --key=path/to/key
k create sa build-bot -n ci
k create token build-bot -n ci --duration=1h
k create role pod-reader -n ci --verb=get,list,watch --resource=pods
k create rolebinding X-binding -n Y --role=X-role --serviceaccount=Y:X
k create clusterrole node-reader --verb=get,list,watch --resource=nodes
k create clusterrolebinding X-binding --clusterrole=X --user=jane   # or --group=/--serviceaccount=
k create service clusterip my-svc --tcp=80:8080
k create service externalname ext-svc --external-name=db.example.com
k create ingress web-ingress --rule="app.example.com/=web-svc:80" --class=nginx
k expose deployment myapp --port=80 --target-port=8080 --type=NodePort
k set image deployment/web nginx=nginx:1.27
k set env deployment/web --from=configmap/myconfig
```

**No imperative generator exists for:** NetworkPolicy, PV, PVC, Gateway API objects, StatefulSet, DaemonSet
(take a Deployment skeleton, swap `kind`, drop `replicas`/`strategy`) — hand-write these from memorized skeletons.

---

## YAML skeletons worth knowing cold (faster to recall than to look up)

**NetworkPolicy default-deny-ingress + allow:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: deny-all-ingress, namespace: prod}
spec:
  podSelector: {}
  policyTypes: [Ingress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: allow-frontend, namespace: prod}
spec:
  podSelector: {matchLabels: {app: backend}}
  policyTypes: [Ingress, Egress]
  ingress:
  - from: [{podSelector: {matchLabels: {app: frontend}}}]
    ports: [{protocol: TCP, port: 8080}]
  egress:                                    # DNS carve-out — forgetting this kills all DNS
  - to: [{namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: kube-system}}}]
    ports: [{protocol: UDP, port: 53}, {protocol: TCP, port: 53}]
```
Rules: no `policyTypes` entry = that direction's rules ignored. Multiple policies on same pod = OR'd. Peer entries in one `from[]` item = AND; separate `from[]` items = OR.

**PV + PVC (static provisioning):**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata: {name: pv-static-01}
spec:
  capacity: {storage: 1Gi}
  accessModes: [ReadWriteOnce]
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath: {path: /mnt/data/pv-static-01}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: pvc-static-01, namespace: default}
spec:
  accessModes: [ReadWriteOnce]
  resources: {requests: {storage: 500Mi}}
  storageClassName: manual        # must match PV explicitly on both sides
```

**Node affinity (required + preferred):**
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions: [{key: topology.kubernetes.io/zone, operator: In, values: [zone-a]}]
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 80
      preference: {matchExpressions: [{key: disktype, operator: In, values: [ssd]}]}
```
nodeSelectorTerms = OR'd; matchExpressions inside one term = AND'd.

**Pod anti-affinity (spread replicas):**
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector: {matchLabels: {app: web}}
      topologyKey: kubernetes.io/hostname   # mandatory, most-forgotten field
```

**Toleration matching a taint:**
```yaml
tolerations:
- key: workload
  operator: Equal
  value: batch
  effect: NoSchedule
```

**Role / RoleBinding (subresource rule):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {namespace: ci, name: pod-reader}
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get","list","watch"]
- apiGroups: [""]
  resources: ["pods/log"]        # subresources = separate resource strings
  verbs: ["get"]
```

**StatefulSet headless Service (always required, generator won't make it):**
```yaml
apiVersion: v1
kind: Service
metadata: {name: web}
spec: {clusterIP: None, selector: {app: web}, ports: [{port: 80}]}
```

**Gateway API HTTPRoute skeleton:**
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: {name: web-route}
spec:
  parentRefs: [{name: web-gateway}]
  hostnames: ["app.example.com"]
  rules:
  - matches: [{path: {type: PathPrefix, value: /api}}]
    backendRefs: [{name: api-svc, port: 8080, weight: 100}]
```

---

## Linux commands (node-level, exam-typical usage)

```bash
systemctl status kubelet containerd
systemctl daemon-reload && systemctl restart kubelet   # after ANY systemd file edit
journalctl -u kubelet -n 200 --no-pager
journalctl -u kubelet -f
ps -ef | grep kubelet | grep -o '\--config=\S*'
ss -tlnp | grep 6443
ip addr show ; ip route
curl -H "Host: app.example.com" http://<node-ip>:<nodePort>/
wget -qO- <svc>.<ns>.svc.cluster.local:<port>     # when curl isn't on the image
crictl ps -a
crictl logs <id> ; crictl logs -f <id>
crictl inspect <id> | less
crictl images ; crictl rmi <image>
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -dates -subject
openssl s_client -connect <ip>:6443 -showcerts
mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/ && mv /tmp/kube-scheduler.yaml /etc/kubernetes/manifests/   # restart trick
find /etc/kubernetes -name "*.conf"
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && chown $(id -u):$(id -g) $HOME/.kube/config
chmod 600 /etc/kubernetes/admin.conf
df -h ; free -h                    # disk/memory pressure
```

---

## kubeadm commands

```bash
kubeadm init --pod-network-cidr=192.168.0.0/16 --control-plane-endpoint=<lb-host>:6443 --upload-certs
kubeadm token create --print-join-command
kubeadm token list
kubeadm join <ep>:6443 --token <t> --discovery-token-ca-cert-hash sha256:<hash>
kubeadm join <ep>:6443 --token <t> --discovery-token-ca-cert-hash sha256:<hash> --control-plane --certificate-key <key>

# Upgrade — sequential, one minor at a time, FIRST cp node = apply, everyone else = node
apt-mark unhold kubeadm && apt-get install -y kubeadm=1.35.x-1.1 && apt-mark hold kubeadm
kubeadm upgrade plan
kubeadm upgrade apply v1.35.x        # first control-plane node ONLY
kubeadm upgrade node                 # every other CP node AND every worker
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
apt-mark unhold kubelet kubectl && apt-get install -y kubelet=1.35.x-1.1 kubectl=1.35.x-1.1 && apt-mark hold kubelet kubectl
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon <node>

kubeadm certs check-expiration
kubeadm certs renew all              # then force-restart affected static pods (move-manifest trick)
kubeadm certs renew apiserver
kubeadm config print init-defaults
```

**Version skew, memorize verbatim:** apiserver instances (HA) ≤1 minor apart · controller-manager/scheduler ≤ apiserver, never newer · kubelet up to 3 minors older than apiserver · kube-proxy same 3-minor rule as kubelet, must match its own node's kubelet · kubectl ±1 minor from apiserver.

---

## etcd commands

```bash
# BACKUP = etcdctl
e endpoint health
e endpoint status --write-out=table
e member list --write-out=table
e alarm list                         # NOSPACE = full disk
e alarm disarm                       # required even after freeing space
e snapshot save /opt/etcd-backup.db
e snapshot status /opt/etcd-backup.db --write-out=table

# RESTORE = etcdutl, OFFLINE, brand-new empty --data-dir, never the live one
etcdutl snapshot restore /opt/etcd-backup.db --data-dir=/var/lib/etcd-restored
# then edit /etc/kubernetes/manifests/etcd.yaml -> spec.volumes[].hostPath.path to new dir
# kubelet auto-reconciles within ~20s, no manual restart needed
```
**Hard rule:** etcdctl backs up, etcdutl restores. `etcdctl snapshot restore` is removed since etcd 3.5 — never use it. Never restore into the live data-dir. Never forget to repoint the manifest's `hostPath`.

---

## Troubleshooting commands — master order

`k describe` (Events) → `k get events -A --sort-by=.lastTimestamp` → `journalctl`/`crictl` only once below-kubelet.

```bash
k get pods -A | grep -v Running
k describe pod <name>
k logs <pod> --previous
crictl ps -a
crictl logs <containerID>
crictl inspect <containerID> | less
journalctl -u kubelet -n 200 --no-pager
cat /etc/kubernetes/manifests/*.yaml
k get pod <name> -o jsonpath='{.status.containerStatuses[0].lastState.terminated}'
k describe node <name> | grep -A10 "Allocated resources"
k get events -A --field-selector reason=Evicted
```

**Symptom → likely cause quick map:**
| Symptom | Check first |
|---|---|
| Pod `Pending` | `describe pod` Events (taint/affinity/resources) verbatim |
| `CrashLoopBackOff` | `logs --previous`, `Last State: OOMKilled?` |
| `ImagePullBackOff` | exact error string in `describe pod` (typo/auth/network) |
| Node `NotReady` | `systemctl status kubelet containerd`, `describe node` Conditions |
| kubectl unreachable | apiserver static pod down — go `crictl`/`journalctl`, not `kubectl` |
| Svc has no endpoints | selector vs Pod labels, Pod readiness |
| Svc has endpoints, unreachable | `targetPort` vs actual listening port, NetworkPolicy |
| `nslookup` fails cluster-wide | CoreDNS pod/Service health, Corefile |
| `nslookup` fails one namespace only | NetworkPolicy egress on port 53 |
| PVC `Pending` | `describe pvc` Events — class/size/access-mode/WaitForFirstConsumer |
| Whole-node pod networking dead | CNI DaemonSet health, `/etc/cni/net.d` |

---

## Networking checks

```bash
k get svc -o wide
k get endpointslices -l kubernetes.io/service-name=<svc>
k get endpoints <svc>                       # empty = selector problem, full stop
k describe svc <svc>                        # Selector + Endpoints in one shot
k get ingressclass
k describe ingress <name>                   # resolved backends per path
k get gatewayclass ; k api-resources | grep gateway.networking.k8s.io
k get gateway,httproute -o yaml             # check status.conditions Accepted/ResolvedRefs
k -n kube-system get pods,svc -l k8s-app=kube-dns
k -n kube-system logs -l k8s-app=kube-dns --tail=100
k run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- nslookup kubernetes.default
k -n kube-system rollout restart deployment coredns    # ConfigMap edits don't hot-reload
k get networkpolicy -A
k get pods -n prod --show-labels ; k get ns --show-labels   # namespaceSelector checks
k get nodes -o jsonpath='{.items[*].spec.podCIDR}'
ip route                                     # cross-node pod CIDR routes present?
sudo iptables -t nat -L -n | grep <service-cluster-ip>     # last resort, kube-proxy layer
```

---

## RBAC checks

```bash
k auth can-i <verb> <resource> --as=<user|sa> -n <ns>          # ALWAYS pass -n
k auth can-i <verb> <resource> --subresource=<log|exec> -n <ns>
k auth can-i --list --as=system:serviceaccount:<ns>:<sa>
k auth can-i '*' '*' -A                     # am I cluster-admin right now?
k get pod <p> -n <ns> -o jsonpath='{.spec.serviceAccountName}'
k get rolebindings,clusterrolebindings -A -o wide
k describe rolebinding <name> -n <ns>       # roleRef + subjects in one shot
k describe role <name> -n <ns>
k describe clusterrole view                 # inspect built-ins: cluster-admin/admin/edit/view
```
**Immutable:** `roleRef` — delete+recreate the binding, never `edit`. **Mutable:** `subjects[]` and Role/ClusterRole `rules[]` — `edit` in place. Fully-qualified SA subject format: `system:serviceaccount:<ns>:<name>`.

---

## Storage checks

```bash
k get pv,pvc,sc -A                          # full-picture triage in one shot
k describe pvc <name>                       # Events = exact binding-failure reason
k describe pv <name>
k get sc                                    # exactly one should show (default)
k patch storageclass <name> -p '{"allowVolumeExpansion": true}'
k patch pvc <name> -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'   # never shrink
k patch pv <name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
k patch pv <name> -p '{"spec":{"claimRef": null}}'   # free a Released PV for rebind
```
Binding-failure order to check: `storageClassName` match → capacity → accessModes subset → `volumeMode` match → (dynamic) is the provisioner pod actually Running.

---

## Context switching

```bash
k config view
k config get-contexts
k config current-context
k config use-context <name>
k config set-context --current --namespace=<ns>
k config view --minify -o jsonpath='{.contexts[0].context.user}'
```

---

## Documentation search keywords per task type

| Task type | Search phrase | Where it lives |
|---|---|---|
| NetworkPolicy | "network policies" | Concepts → Services, Networking & DNS → Network Policies (has the default-deny examples, IS your generator) |
| PV/PVC static | "configure a pod to use a persistentvolume for storage" | Tasks → Configure Pods and Containers |
| StorageClass | "storage classes" | Concepts → Storage → Storage Classes |
| RBAC | "using rbac authorization" | Reference → Access Authn Authz — has Troubleshooting subsection |
| Init containers | "init containers" | Concepts → Workloads → Pods |
| Sidecars | "sidecar containers" | Concepts → Workloads → Pods (separate page from Init) |
| DaemonSet | "daemonset" | Concepts → Workloads → Controllers |
| Taints/Tolerations | "taints and tolerations" | Concepts → Scheduling |
| Node/Pod affinity | "assign pods to nodes using node affinity" | Concepts → Scheduling (pod affinity merged onto same page) |
| Topology spread | "pod topology spread constraints" | Concepts → Scheduling |
| nodeName | `k explain pod.spec.nodeName` | no doc page, use CLI |
| kubeadm init/join | "creating a cluster with kubeadm" | Setup → kubeadm |
| kubeadm upgrade | "upgrading kubeadm clusters" | Tasks → Administer a Cluster + Version Skew Policy ref page |
| Certs | "certificate management with kubeadm" / "pki certificates and requirements" | Setup → kubeadm |
| etcd backup/restore | "operating etcd clusters for kubernetes" | Tasks → Administer a Cluster (NOT etcd.io) |
| Static pods | "static pods" | Concepts → Workloads → Pods |
| Drain a node | "safely drain a node" | Tasks → Administer a Cluster + "Disruptions" for PDB |
| Services | "service" (Concepts, not Tasks) | has "Debugging Services" subsection at bottom |
| Ingress | "ingress" then "ingress controllers" | Concepts → Services, Networking & DNS |
| Gateway API | "httproute" / "gateway api getting started" | **gateway-api.sigs.k8s.io** (separate allowed domain) |
| CoreDNS/DNS | "debug dns resolution" | Tasks → Administer a Cluster |
| CNI/addons | "installing addons" | Tasks → Administer a Cluster → Networking (vendor CIDR field names from memory, not docs) |
| Probes | "configure liveness readiness startup probes" | Tasks → Configure Pods and Containers |
| ConfigMap/Secret | "configmap" / "secret" | Concepts → Configuration |
| Requests/Limits/Quota | "resource management for pods and containers" then "limit ranges"/"resource quotas" | Concepts → Workloads/Policies |
| Jobs/CronJobs | "jobs run to completion" / "cronjob" | Concepts → Workloads → Controllers |
| StatefulSets | "statefulsets" | Concepts → Workloads → Controllers |
| Deployments/rollback | "deployments" | Concepts → Workloads → Controllers (rollback section inline, Ctrl-F on page) |
| General troubleshooting | "troubleshooting" / "debug pods" / "determine the reason for pod failure" | Tasks → Troubleshooting hub |
| kubectl syntax lookup | "kubectl cheat sheet" | Reference → kubectl Cheat Sheet |
| Exact field nesting | N/A | `k explain <path> --recursive` — faster than any doc page |

Allowed docs domains for CKA: `kubernetes.io/docs/*` and `gateway-api.sigs.k8s.io`. `etcd.io` is generally **not** allowed — use the kubeadm-side etcd pages on kubernetes.io instead.
