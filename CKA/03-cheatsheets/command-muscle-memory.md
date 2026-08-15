# CKA Command Muscle Memory Sheet

*Purpose: drill exact invocations until they're typed without thinking. Every `kubectl` example
below assumes the exam's pre-aliased `k=kubectl` and `export do="--dry-run=client -o yaml"`
(set both first thing, every session). Favors imperative generation + edit over hand-written YAML
per the exam-priority research (`01-exam-snapshot-and-priorities.md`) — generate, redirect, edit
only what the generator can't express, apply. Scope covers `01`–`02-topics/*` in this repo; nothing
here is beginner material.*

```bash
# First two lines of every exam session:
alias k=kubectl
export do="--dry-run=client -o yaml"
```

---

## 1. `kubectl get`

```bash
k get pods                                        # current namespace
k get pods -A                                      # all namespaces
k get pods -o wide                                 # +NODE, +IP
k get pods --show-labels
k get pods -l app=web,tier!=cache                  # label selector, equality
k get pods -l 'app in (web,api)'                   # set-based selector
k get pods --field-selector spec.nodeName=node01
k get pods -o yaml                                 # full object, for editing/inspection
k get pods -o json
k get pods -o jsonpath='{.items[*].metadata.name}'
k get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
k get pods --sort-by=.metadata.creationTimestamp
k get pods -w                                      # watch
k get all -n <ns>
k get events -A --sort-by=.lastTimestamp
k get events --field-selector reason=FailedScheduling
k get nodes -o wide
k get nodes --show-labels
k get componentstatuses                            # deprecated but often still works
k get endpointslices -l kubernetes.io/service-name=<svc>
k get endpoints <svc>                              # legacy, fast glance
k get lease -n kube-system                          # leader-election check
```

## 2. `kubectl describe`

```bash
k describe pod <name>            # Events at bottom = answer key 90% of the time
k describe node <name>           # Conditions + Taints + Allocated resources
k describe svc <name>            # Selector + Endpoints in one shot
k describe deploy <name>
k describe pvc <name>            # binding failure reasons
k describe networkpolicy <name>
k describe ingress <name>        # resolved backends per path
```

## 3. `kubectl logs`

```bash
k logs <pod>
k logs <pod> -c <container>                 # required once >1 container
k logs <pod> --previous                     # crashed attempt — the real answer for CrashLoopBackOff
k logs <pod> -f
k logs <pod> --all-containers
k logs -n kube-system kube-scheduler-<node>
k logs -n kube-system -l k8s-app=kube-dns --tail=100
k logs deploy/coredns -n kube-system
k logs job/myjob
```

## 4. `kubectl exec`

```bash
k exec <pod> -- env
k exec <pod> -- cat /path/to/file
k exec -it <pod> -- /bin/sh
k exec <pod> -c <container> -- ls /data
k exec -n shop deploy/catalog -- env | grep FEATURE_FLAG
```

## 5. `kubectl run` (generate a Pod fast)

```bash
k run nginx --image=nginx $do > pod.yaml
k run mypod --image=nginx --restart=Never $do > pod.yaml   # bare pod, no controller
k run busy1 --image=busybox:1.36 --restart=Never -- sleep 3600
k run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 \
  -it --rm --restart=Never -- nslookup kubernetes.default
k run tmp --rm -it --image=busybox:1.36 -- wget -qO- <svc>.<ns>.svc.cluster.local:<port>
```

## 6. `kubectl create` (generate everything else fast)

```bash
k create deployment web --image=nginx:1.25 --replicas=3 $do > deploy.yaml
k create job myjob --image=busybox $do -- /bin/sh -c "echo hi" > job.yaml
k create cronjob mycron --image=busybox --schedule="*/1 * * * *" $do -- /bin/sh -c date > cj.yaml
k create job --from=cronjob/mycron manual-run-1              # one-off trigger
k create namespace shop            # or: k create ns shop
k create configmap myconfig --from-literal=key=value --from-file=app.conf
k create secret generic mysecret --from-literal=password=abc123
k create secret docker-registry regcred \
  --docker-server=<s> --docker-username=<u> --docker-password=<p> --docker-email=<e>
k create secret tls mytls --cert=path/to/cert --key=path/to/key
k create serviceaccount build-bot -n ci             # or: k create sa
k create token build-bot -n ci --duration=1h
k create role pod-reader -n ci --verb=get,list,watch --resource=pods
k create rolebinding X-binding -n Y --role=X-role --serviceaccount=Y:X
k create clusterrole node-reader --verb=get,list,watch --resource=nodes
k create clusterrolebinding X-binding --clusterrole=X --user=jane      # or --group=/--serviceaccount=
k create service clusterip my-svc --tcp=80:8080
k create service externalname ext-svc --external-name=db.example.com
k create ingress web-ingress --rule="app.example.com/=web-svc:80" --class=nginx
```

## 7. `kubectl expose`

```bash
k expose deployment myapp --port=80 --target-port=8080 --type=ClusterIP
k expose deployment web --port=80 --target-port=8080 --type=NodePort
k expose deployment X -n Y --port=P --target-port=<containerPort>
```

## 8. `kubectl set`

```bash
k set image deployment/web nginx=nginx:1.27
k set image deployment/catalog nginx=nginx:1.27 -n shop
k set env deployment/web LOG_LEVEL=debug
k set env deployment/web --from=configmap/myconfig
k set env deployment/web --from=secret/mysecret
```

## 9. `kubectl scale`

```bash
k scale deployment/web --replicas=5
k scale deployment/web --current-replicas=3 --replicas=5    # precondition, scripted safety
k scale --replicas=5 -f deploy.yaml
k scale statefulset/web --replicas=3
```

## 10. `kubectl rollout`

```bash
k rollout status deployment/web --timeout=60s
k rollout history deployment/web
k rollout history deployment/web --revision=2
k rollout undo deployment/web
k rollout undo deployment/web --to-revision=2
k rollout pause deployment/web
k rollout resume deployment/web
k rollout restart deployment/web         # force re-pull of env-based ConfigMap/Secret changes
k rollout restart deployment coredns -n kube-system
k rollout status daemonset/<name>
k rollout status statefulset/<name>
```

## 11. `kubectl patch`

```bash
# merge patch (most common)
k patch configmap flags -n shop --type=merge -p '{"data":{"feature":"on"}}'
k patch pv <name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
k patch pvc <name> -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
k patch storageclass <name> -p '{"allowVolumeExpansion": true}'
k patch storageclass <old> -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'

# json patch (array ops, precise path targeting)
k patch deployment catalog -n shop --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/env","value":[{"name":"X","value":"1"}]}]'

# merge patch for a nested structural block (podAntiAffinity example)
k patch deployment web --type merge -p '{
  "spec": {"template": {"spec": {"affinity": {"podAntiAffinity": {
    "requiredDuringSchedulingIgnoredDuringExecution": [{
      "labelSelector": {"matchLabels": {"app": "web"}},
      "topologyKey": "kubernetes.io/hostname"
    }]
  }}}}}
}'
```

## 12. `kubectl edit`

```bash
k edit deployment web            # fastest path for a single nested-field tweak (e.g. add affinity block)
k edit role pod-viewer -n app1   # rules ARE mutable
k edit rolebinding <name>        # subjects[] ARE mutable — roleRef is NOT (delete+recreate instead)
k edit configmap coredns -n kube-system   # remember: needs rollout restart to take effect
```
**Never** `k edit` a static-pod mirror object (`kube-apiserver-<node>` etc.) — it's read-only, edit
the manifest file on disk (`/etc/kubernetes/manifests/*.yaml`) instead.

## 13. `kubectl replace`

```bash
k replace -f deploy.yaml
k replace --force -f pod.yaml       # delete+recreate when a field is immutable (e.g. selector, nodeName)
k get pod nginx -o yaml | k replace --force -f -
```

## 14. `kubectl delete`

```bash
k delete pod mypod --grace-period=0 --force     # last resort, stuck-terminating pods
k delete statefulset <name> --cascade=orphan    # keep pods running, remove only the controller
k taint nodes node01 key1=value1:NoSchedule-    # note: trailing dash removes, not `delete`
```

## 15. `kubectl label`

```bash
k label nodes node01 disktype=ssd
k label nodes node01 disktype=ssd --overwrite     # required if key already exists
k label nodes node01 disktype-                    # trailing dash (no space) removes
k label pods mypod env=staging -n shop
```

## 16. `kubectl annotate`

```bash
k annotate deployment/web kubernetes.io/change-cause="bump to 1.27"
k annotate deployment/web kubernetes.io/change-cause-       # remove
```

## 17. `kubectl taint`

```bash
k taint nodes node01 key1=value1:NoSchedule
k taint nodes node01 dedicated=gpu:NoSchedule
k taint nodes node01 key1=value1:NoSchedule-      # remove (key+effect must match, no value needed)
k describe node node01 | grep Taints
```

## 18. `kubectl drain` / `cordon` / `uncordon`

```bash
k cordon <node>
k drain <node> --ignore-daemonsets --delete-emptydir-data --force
k uncordon <node>
k get nodes                        # SchedulingDisabled column confirms state
k get pdb -A                       # check BEFORE draining, not after it hangs
```

## 19. `kubectl top`

```bash
k top nodes
k top pods -A --sort-by=memory
k top pod <name>
# errors "metrics not available" → check metrics-server Deployment in kube-system, that's the actual bug
```

## 20. `kubectl auth can-i`

```bash
k auth can-i create deployments -n dev
k auth can-i delete pods --as=jane -n dev
k auth can-i get pods --as=system:serviceaccount:ci:build-bot -n ci
k auth can-i get pods --as=jane --as-group=developers -n dev
k auth can-i --list
k auth can-i --list --as=system:serviceaccount:ci:build-bot -n ci
k auth can-i get pods --subresource=log -n dev
k auth can-i '*' '*' -A                       # am I cluster-admin right now?
```
Always pass `-n <namespace>` explicitly — a missing `-n` silently checks the current-context
namespace and gives a misleading answer.

## 21. `kubectl config`

```bash
k config view
k config view --minify -o jsonpath='{.contexts[0].context.user}'
k config current-context
k config get-contexts
k config use-context <name>
k config set-context --current --namespace=<ns>
```

## 22. `kubectl apply`

```bash
k apply -f deploy.yaml
k apply -f pv.yaml -f pvc.yaml -f pod.yaml
k apply -k <kustomization-dir>            # Kustomize — no allowed exam-docs domain, know this cold
k kubectl kustomize <dir>                 # render without applying, to sanity-check first
k apply -f - <<'EOF'
...
EOF
```

## 23. `kubectl explain`

```bash
k explain pod.spec.affinity.nodeAffinity
k explain pod.spec.affinity.podAntiAffinity --recursive    # get nesting exactly right, fast
k explain deployment.spec.strategy.rollingUpdate
k explain pod.spec.nodeName
```

---

## 24. `kubeadm`

```bash
# Bootstrap
kubeadm init --pod-network-cidr=192.168.0.0/16 --control-plane-endpoint=<lb-host>:6443 --upload-certs
mkdir -p $HOME/.kube && cp -i /etc/kubernetes/admin.conf $HOME/.kube/config \
  && chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f <cni-manifest-url>

# Join
kubeadm token create --print-join-command
kubeadm token list
kubeadm join <ep>:6443 --token <t> --discovery-token-ca-cert-hash sha256:<hash>
kubeadm join <ep>:6443 --token <t> --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane --certificate-key <key>

# Upgrade (sequential, one minor at a time)
apt-mark unhold kubeadm && apt-get update && apt-get install -y kubeadm=1.35.x-1.1 && apt-mark hold kubeadm
kubeadm upgrade plan
kubeadm upgrade apply v1.35.x        # FIRST control-plane node ONLY
kubeadm upgrade node                 # every OTHER control-plane node AND every worker
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
apt-mark unhold kubelet kubectl && apt-get install -y kubelet=1.35.x-1.1 kubectl=1.35.x-1.1 \
  && apt-mark hold kubelet kubectl
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon <node>

# Certificates
kubeadm certs check-expiration
kubeadm certs renew all
kubeadm certs renew apiserver
kubeadm certs certificate-key

# Misc
kubeadm version
kubeadm config print init-defaults
```

**Version-skew cheat, memorize verbatim:**
apiserver instances (HA) ≤1 minor apart · controller-manager/scheduler ≤ apiserver, not newer ·
kubelet up to 3 minors older than apiserver · kube-proxy same 3-minor rule as kubelet, must match
kubelet's own node · kubectl ±1 minor from apiserver.

---

## 25. `etcdctl` (backup — network client) / `etcdutl` (restore — offline)

```bash
# Always export or alias the TLS flags first — never retype per command
export ETCDCTL_API=3     # harmless; etcd ≥3.4 already defaults to v3
alias e='etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key'

e endpoint health
e endpoint status --write-out=table
e member list --write-out=table
e alarm list                              # NOSPACE = full disk
e alarm disarm                            # required even after freeing space

# BACKUP — etcdctl
e snapshot save /opt/etcd-backup.db
e snapshot status /opt/etcd-backup.db --write-out=table

# RESTORE — etcdutl, OFFLINE, brand-new empty --data-dir, never the live one
etcdutl snapshot restore /opt/etcd-backup.db --data-dir=/var/lib/etcd-restored
# then: edit /etc/kubernetes/manifests/etcd.yaml -> spec.volumes[].hostPath.path to the new dir
# kubelet auto-reconciles the static pod within ~20s
```
**Hard rule:** `etcdctl` backs up, `etcdutl` restores. `etcdctl snapshot restore` is
removed/deprecated since etcd 3.5 — do not use it. Restoring into the live data-dir in place, or
forgetting to repoint the manifest's `hostPath`, are the two most common ways to fail this task
outright.

---

# YAML Speed Training

Fastest path per object type — generate imperatively wherever possible, hand-edit only what the
generator can't express, and use `patch`/`set`/`edit` in place of a full export-edit-reapply cycle
whenever the change is small and the object already exists.

| Object | Fastest generation path | When to hand-edit / patch instead |
|---|---|---|
| **Pod** | `k run <name> --image=<img> $do > pod.yaml` | Edit for `nodeSelector`, `affinity`, multi-container, probes, volumes — `run` can't express these |
| **Deployment** | `k create deployment <name> --image=<img> --replicas=N [--port=P] $do > deploy.yaml` | Edit for `resources`, probes, `strategy.rollingUpdate`, affinity/anti-affinity. Use `k set image`/`k scale`/`k rollout` for live changes — never re-apply a whole file just to bump an image or replica count |
| **Service** | `k expose deployment <name> --port=P --target-port=TP --type=T` or `k create service clusterip/externalname ...` | Hand-edit only for `sessionAffinity`, multiple named ports, or selector-less + manual EndpointSlice patterns |
| **ConfigMap** | `k create configmap <name> --from-literal=k=v --from-file=<path>` | Never hand-write `data:` unless the value needs exact multi-line formatting — `--from-file` covers that too |
| **Secret** | `k create secret generic/tls/docker-registry ...` | Never hand-encode base64 `data:` — if authoring YAML directly, use `stringData:` (auto-encoded on write), never plaintext under `data:` |
| **NetworkPolicy** | **No reliable imperative generator** — hand-write from a memorized skeleton | Always hand-write; know default-deny-all-ingress and allow-from-podSelector-on-port skeletons cold; `k edit`/`k apply -f` to iterate |
| **PV** | **No imperative generator** — hand-write | Always hand-write (short, fixed skeleton: `capacity`, `accessModes`, `persistentVolumeReclaimPolicy`, `storageClassName`, `hostPath`) |
| **PVC** | **No imperative generator** — hand-write | Always hand-write (even shorter skeleton); `k patch` in place to resize (`allowVolumeExpansion` permitting) rather than recreate |
| **Role** | `k create role <name> -n <ns> --verb=v1,v2 --resource=r1,r2` | Generator can't add a second rule block (e.g. a subresource like `pods/log`) in one shot — generate with `$do`, append the extra `rules[]` entry by hand, then apply. `k edit role` to add verbs/resources later (mutable) |
| **RoleBinding** | `k create rolebinding <name> -n <ns> --role=<r> --serviceaccount=<ns>:<sa>` (or `--user=`/`--group=`) | `subjects[]` is mutable via `k edit`; `roleRef` is **immutable** — delete + recreate if the Role/ClusterRole target itself is wrong |
| **ClusterRole** | `k create clusterrole <name> --verb=v1,v2 --resource=r1,r2` | Hand-edit for `nonResourceURLs` (no imperative flag for it) |
| **ClusterRoleBinding** | `k create clusterrolebinding <name> --clusterrole=<cr> --user=/--group=/--serviceaccount=` | Same immutable-`roleRef` rule as RoleBinding |
| **ServiceAccount** | `k create serviceaccount <name> -n <ns>` (or `k create sa`) | Rarely needs YAML at all; `automountServiceAccountToken: false` is the one field worth hand-adding when asked |
| **Job** | `k create job <name> --image=<img> $do -- <cmd> > job.yaml` | Generator defaults `completions`/`parallelism` to 1 and can't set `backoffLimit`/`completionMode` — always hand-edit these three after generating |
| **CronJob** | `k create cronjob <name> --image=<img> --schedule="<cron>" $do -- <cmd> > cj.yaml` | Hand-edit `concurrencyPolicy`, `successfulJobsHistoryLimit`/`failedJobsHistoryLimit`, `suspend`, `timeZone` — none are exposed as flags |
| **DaemonSet** | **No imperative generator** — take a Deployment skeleton (`k create deployment ... $do`) and swap `kind: DaemonSet`, delete `replicas`/`strategy`, keep `template` | Hand-edit `updateStrategy`, and add the control-plane-taint toleration explicitly if it must run there |
| **Ingress** | `k create ingress <name> --rule="host/path=svc:port" --class=<ingressClassName>` | Hand-edit for `pathType` precision, TLS block, controller-specific annotations |
| **Gateway / HTTPRoute** | **No imperative generator** — hand-write from memorized skeleton (`gatewayClassName`, `listeners[]`; `parentRefs`, `rules[].matches`/`backendRefs[].weight`) | Always hand-write; check `k get gatewayclass` / `k api-resources \| grep gateway` first — CRDs may not even be installed |
| **StatefulSet** | **No imperative generator** — hand-write, or take a Deployment skeleton and add `serviceName` + `volumeClaimTemplates` | Always needs a hand-authored headless Service (`clusterIP: None`) alongside it — generator won't create that either |

**General rule of thumb:** if `kubectl create <noun>` exists and covers 80%+ of the required
fields, generate-then-edit beats hand-writing every time. If no imperative generator exists
(NetworkPolicy, PV, PVC, Gateway API, StatefulSet, DaemonSet), keep a mentally-memorized minimal
skeleton for each rather than re-deriving field names from `kubectl explain` under time pressure —
use `explain --recursive` only to double-check nesting you're unsure of, not to look up field
names from scratch.
