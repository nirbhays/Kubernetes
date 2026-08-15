# Troubleshooting Scenario Bank — Workload / Scheduling / Networking / Storage

*20 original practice scenarios built from the general competency patterns in `02-topics/troubleshooting-playbook.md`, `02-topics/networking.md`, `02-topics/scheduling.md`, and `02-topics/storage.md` — not reproductions of any real exam question. Each scenario gives you the **symptom only**; resist jumping to the collapsed sections until you've actually run the diagnostic commands yourself. Aligned to the Troubleshooting (30%) + Services & Networking (20%) + Workloads & Scheduling (15%) + Storage (10%) domains.*

Suggested drill discipline: set a timer for the stated time limit, use only `kubectl`/`k describe`/`k get events`/`k logs` first (per the "events before logs, logs before guessing" law), and only open the Hint if you're genuinely stuck for 2+ minutes with no lead.

---

### Scenario 1 — The webshop that answers no one
**Time limit:** 5 min · **Skills tested:** Service/Endpoints diagnosis, label selector matching · **Points/difficulty:** Easy

**Symptom:** A Deployment `webshop` shows 3/3 pods `Running` and `Ready`. `kubectl get svc webshop` shows a ClusterIP allocated. Every request to `webshop.shop.svc.cluster.local:80` from another pod in the cluster times out (not "connection refused" — a hang).

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl create ns shop
kubectl create deployment webshop --image=nginx --replicas=3 -n shop
kubectl expose deployment webshop --port=80 --target-port=80 -n shop
kubectl patch svc webshop -n shop -p '{"spec":{"selector":{"app":"webshop-app"}}}'
# the Service's selector was overwritten to app=webshop-app, which no longer matches
# any pod's actual label (app=webshop, the Deployment's real template label) —
# relabeling the pods themselves instead would just make the Deployment/ReplicaSet
# controller notice the "missing" replicas and spin up new correctly-labeled pods,
# which would defeat the point of this exercise
```

<details>
<summary>Hint (use only if stuck)</summary>

Don't read the Service's full YAML top-to-bottom. Run the one command that immediately tells you whether this is a selector problem or something further downstream.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The Service's `spec.selector` was overwritten to `app=webshop-app`, which doesn't match any Pod's actual labels (`app=webshop`, the label the Deployment actually put on its pods), so `Endpoints`/`EndpointSlice` is empty — the ClusterIP has nothing to route to, producing a hang rather than a clean rejection.
**Fix:**
```bash
kubectl get endpoints webshop -n shop          # confirms empty ENDPOINTS column
kubectl get pods --show-labels -n shop
kubectl patch svc webshop -n shop -p '{"spec":{"selector":{"app":"webshop"}}}'
```
**Verify:**
```bash
kubectl get endpoints webshop -n shop           # now lists 3 pod IPs
kubectl run tmp --rm -it --image=busybox:1.36 -n shop -- wget -qO- webshop:80
```
**Common wrong turn candidates take:** Restarting the pods or scaling the Deployment, assuming a transient issue, instead of checking `Endpoints` first — the pods were never the problem.

</details>

---

### Scenario 2 — Right door, wrong room
**Time limit:** 6 min · **Skills tested:** Service targetPort vs container port · **Points/difficulty:** Easy

**Symptom:** `kubectl get endpoints api` shows three populated pod IPs. `kubectl describe svc api` shows nothing alarming. Yet every request to the Service from inside the cluster returns `curl: (7) Failed to connect ... Connection refused` (not a timeout).

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl create deployment api --image=hashicorp/http-echo --replicas=3 -- /http-echo -listen=:5678 -text="hello"
# note: "kubectl create deployment ... -- X" sets the container's *command* (full
# entrypoint override), not args — so the binary path must be included explicitly,
# unlike "kubectl run", where "-- X" only sets args and the image's own ENTRYPOINT still applies
kubectl expose deployment api --port=80 --target-port=8080   # container actually listens on 5678, not 8080
```

<details>
<summary>Hint (use only if stuck)</summary>

Endpoints being populated only proves the selector is correct — it proves nothing about whether the *port* the Service forwards to is the one the container is actually listening on. Check what port the container really binds.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `spec.ports[].targetPort` (8080) doesn't match the container's actual listening port (5678 per the `-listen` flag in its command), so connections reach the pod's network namespace but nothing answers on that port — a connection refused, not a hang, which is the tell that distinguishes this from a selector problem.
**Fix:**
```bash
kubectl get pod -l app=api -o jsonpath='{.items[0].spec.containers[0].command}'
kubectl patch svc api -p '{"spec":{"ports":[{"port":80,"targetPort":5678}]}}'
```
**Verify:**
```bash
kubectl run tmp --rm -it --image=busybox:1.36 -- wget -qO- api:80
```
**Common wrong turn candidates take:** Re-checking the selector/Endpoints repeatedly since "Endpoints looked fine," without noticing `Connection refused` (app-level) reads completely differently from a timeout (network/policy-level) — the error text itself is the fastest branch signal.

</details>

---

### Scenario 3 — The pod that never gets invited to the party
**Time limit:** 7 min · **Skills tested:** readiness probes, Endpoints exclusion logic · **Points/difficulty:** Medium

**Symptom:** Service `catalog` has a correct selector and correct `targetPort`. `kubectl get pods` shows all 3 `catalog` pods in phase `Running`, but the READY column reads `0/1` for all three (not `1/1`). `kubectl get endpoints catalog` is empty.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl create deployment catalog --image=nginx --replicas=3
kubectl expose deployment catalog --port=80 --target-port=80
kubectl patch deployment catalog -p '{"spec":{"template":{"spec":{"containers":[{"name":"nginx","readinessProbe":{"httpGet":{"path":"/nonexistent-health","port":80},"periodSeconds":5}}]}}}}'
```

<details>
<summary>Hint (use only if stuck)</summary>

A Service only routes to pods that are individually `Ready`, regardless of whether the selector and targetPort are perfect. Check the READY column, not just the phase.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The `readinessProbe` checks a path (`/nonexistent-health`) that returns 404 on stock nginx, so the probe never succeeds, the containers never reach `Ready`, and Endpoints stays empty even though selector and targetPort are both correct — a perfectly healthy Service with a broken upstream signal.
**Fix:**
```bash
kubectl describe pod -l app=catalog | grep -A5 Readiness
kubectl patch deployment catalog --type=json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/"}]'
```
**Verify:**
```bash
kubectl get pods -l app=catalog          # READY 1/1
kubectl get endpoints catalog            # populated
```
**Common wrong turn candidates take:** Re-diffing the Service's selector against pod labels repeatedly because "Endpoints is empty, must be a selector bug" — without ever running `kubectl describe pod` to see the probe failure in Events.

</details>

---

### Scenario 4 — The image that isn't where you think
**Time limit:** 4 min · **Skills tested:** ImagePullBackOff triage, reading Events verbatim · **Points/difficulty:** Easy

**Symptom:** A newly rolled-out Deployment `billing` shows pods stuck in `ImagePullBackOff`, restart count 0.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl create deployment billing --image=nginx:1.99.99-doesnotexist
```

<details>
<summary>Hint (use only if stuck)</summary>

The exact failure reason is printed verbatim in one specific command's output — no deep diagnosis needed here, just read carefully.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The image tag `nginx:1.99.99-doesnotexist` doesn't exist in the registry — `manifest unknown` in the pull error.
**Fix:**
```bash
kubectl describe pod -l app=billing | tail -15
kubectl set image deployment/billing nginx=nginx:1.27
```
**Verify:**
```bash
kubectl rollout status deployment/billing
```
**Common wrong turn candidates take:** Editing the bare Pod's `image` field directly (immutable field on most controllers' generated pods) instead of patching the Deployment template, then wondering why the edit is rejected or has no effect.

</details>

---

### Scenario 5 — The Pod nobody will host
**Time limit:** 6 min · **Skills tested:** taint/toleration matching, FailedScheduling diagnosis · **Points/difficulty:** Medium

**Symptom:** A single-replica Pod `batch-worker` has been `Pending` for several minutes. The cluster has spare CPU/memory capacity on all nodes.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl taint nodes <worker-node> workload=restricted:NoSchedule
kubectl run batch-worker --image=busybox --restart=Never -- sleep 3600
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl describe pod` prints the exact per-node reason under `FailedScheduling` — it will tell you precisely which taint blocked scheduling, verbatim.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The only available node carries a `NoSchedule` taint (`workload=restricted`) that the pod has no matching `toleration` for.
**Fix (add a toleration — do not blindly remove the taint, since it may be intentional):**
```bash
kubectl describe pod batch-worker | grep -A3 Events
kubectl patch pod batch-worker -p '{"spec":{"tolerations":[{"key":"workload","operator":"Equal","value":"restricted","effect":"NoSchedule"}]}}'
# tolerations are one of the few Pod spec fields the API allows to change post-creation —
# but only additively (existing tolerations can't be removed or altered, aside from
# tolerationSeconds), which is exactly what this patch does, so no delete+recreate needed
```
**Verify:**
```bash
kubectl get pod batch-worker -o wide       # NODE column populated, STATUS Running
```
**Common wrong turn candidates take:** Removing the taint from the node entirely (`kubectl taint nodes <node> workload=restricted:NoSchedule-`) when the task intent was to add the correct toleration to the workload instead — this "fixes" the symptom but violates the actual requirement if the taint exists on purpose (e.g., dedicated-node policy).

</details>

---

### Scenario 6 — The Pod that insists on a node that doesn't exist
**Time limit:** 6 min · **Skills tested:** node affinity diagnosis · **Points/difficulty:** Medium

**Symptom:** `kubectl get pods` shows `analytics-0` stuck `Pending`. No taints are present on any node (`kubectl describe node <n> | grep Taints` shows `<none>` everywhere).

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: analytics-0
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values: ["ssd-nvme"]
  containers:
  - name: app
    image: busybox
    command: ["sleep", "3600"]
EOF
# no node in the cluster is labeled disktype=ssd-nvme
```

<details>
<summary>Hint (use only if stuck)</summary>

Since taints are ruled out, check the other half of `FailedScheduling`'s possible reasons — read the pod spec's `affinity` block and cross-reference against actual node labels.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `requiredDuringSchedulingIgnoredDuringExecution` node affinity demands a label (`disktype=ssd-nvme`) that no node in the cluster carries — a hard requirement with zero satisfying nodes.
**Fix (label a real node to match, or relax the affinity — pick based on task intent):**
```bash
kubectl get nodes --show-labels
kubectl label node <node> disktype=ssd-nvme
```
**Verify:**
```bash
kubectl get pod analytics-0 -o wide       # now Running with a NODE assigned
```
**Common wrong turn candidates take:** Assuming `Pending` always means a resource/taint problem and never actually opening the Pod's own YAML to check for a self-inflicted affinity constraint — `describe pod`'s `FailedScheduling` message does name the affinity mismatch explicitly, but it's easy to skim past if you're pattern-matching only on the taint scenario.

</details>

---

### Scenario 7 — The claim no one will approve
**Time limit:** 6 min · **Skills tested:** PVC binding diagnosis, missing/absent PV · **Points/difficulty:** Medium

**Symptom:** Pod `report-gen` is stuck `Pending` with `ContainerCreating` never reached. `kubectl get pvc` shows `report-data` in status `Pending`.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: report-data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual-nonexistent
  resources:
    requests:
      storage: 1Gi
EOF
kubectl run report-gen --image=busybox --restart=Never --overrides='
{"spec":{"containers":[{"name":"app","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"mountPath":"/data","name":"vol"}]}],"volumes":[{"name":"vol","persistentVolumeClaim":{"claimName":"report-data"}}]}}'
```

<details>
<summary>Hint (use only if stuck)</summary>

Trace the chain in the right direction: Pod → PVC → (PV or StorageClass). Start with `kubectl describe pvc`, not the Pod — its Events block usually states the exact reason in plain English.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The PVC references `storageClassName: manual-nonexistent`, which doesn't exist as a `StorageClass` object in the cluster, so nothing — static or dynamic — can ever satisfy the claim.
**Fix:**
```bash
kubectl describe pvc report-data     # Events: storageclass.storage.k8s.io "manual-nonexistent" not found
kubectl get storageclass
kubectl patch pvc report-data -p '{"spec":{"storageClassName":"<real-default-class-name>"}}'
# storageClassName is immutable post-creation on most clusters — if the patch is rejected,
# delete and recreate the PVC with the correct class instead
```
**Verify:**
```bash
kubectl get pvc report-data          # STATUS Bound (or Pending+WaitForFirstConsumer if that binding mode — expected, not broken)
kubectl get pod report-gen -o wide   # Running
```
**Common wrong turn candidates take:** Deleting and recreating the Pod repeatedly, assuming a scheduling glitch, without ever running `kubectl describe pvc` — the PVC's own Events line names the exact missing StorageClass verbatim.

</details>

---

### Scenario 8 — The volume that only tolerates one kind of reader
**Time limit:** 8 min · **Skills tested:** PV/PVC accessModes mismatch, layered storage diagnosis · **Points/difficulty:** Hard

**Symptom:** A matching PV *does* exist for the PVC's storage class and size, but `kubectl get pvc` still shows `logs-claim` stuck `Pending`.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: logs-pv
spec:
  capacity:
    storage: 2Gi
  accessModes: ["ReadOnlyMany"]
  storageClassName: manual
  hostPath:
    path: /mnt/logs-data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logs-claim
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests:
      storage: 1Gi
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

Size and StorageClass both look fine at a glance — that's the trap. Diff every field of the PV against the PVC, not just the ones that jump out, especially `accessModes`.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The PV only offers `ReadOnlyMany`, but the PVC requests `ReadWriteOnce` — capacity and storageClassName match, so it's easy to assume the pair should bind, but `accessModes` must also be compatible and isn't.
**Fix (adjust the PV's accessModes to include what's needed, without deleting/recreating the PVC):**
```bash
kubectl describe pvc logs-claim     # Events may be sparse/generic here — this is the harder variant
kubectl get pv logs-pv -o yaml | grep -A3 accessModes
kubectl patch pv logs-pv -p '{"spec":{"accessModes":["ReadWriteOnce","ReadOnlyMany"]}}'
```
**Verify:**
```bash
kubectl get pvc logs-claim          # STATUS Bound
kubectl get pv logs-pv              # STATUS Bound, CLAIM shows logs-claim
```
**Common wrong turn candidates take:** Deleting and recreating the PVC as a first move (loses task credit if the task says not to, and changes nothing anyway since the underlying PV is still access-mode-incompatible) instead of diffing PV vs PVC field by field.

</details>

---

### Scenario 9 — The default that quietly forgot who's default
**Time limit:** 6 min · **Skills tested:** StorageClass default annotation conflicts, the "most-recently-created default wins" tie-break rule · **Points/difficulty:** Medium

**Symptom:** A new PVC `app-data` (no `storageClassName` specified) sits `Pending` indefinitely, even though the cluster clearly has a working dynamic provisioner — other PVCs that explicitly name a StorageClass bind fine.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl get storageclass                          # note the existing working default, e.g. "standard"
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: broken-fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/no-such-provisioner
EOF
# broken-fast-ssd is now ALSO annotated as default. Kubernetes does not treat two
# default-annotated classes as an error or a block — its DefaultStorageClass admission
# controller deterministically picks the most-recently-created default-annotated class
# for any PVC that omits storageClassName. Since broken-fast-ssd was created after the
# real default, it silently wins even though its provisioner doesn't exist.
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

The PVC omits `storageClassName` entirely, which means Kubernetes must pick "the" default class for it. Having two classes claim that title isn't itself an error — check which `storageClassName` actually landed on the PVC, then ask whether that specific class can provision anything at all.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** Two `StorageClass` objects are both annotated `storageclass.kubernetes.io/is-default-class=true`. Kubernetes doesn't leave this ambiguous or block the PVC — the `DefaultStorageClass` admission controller sorts default-annotated classes by creation timestamp (newest first) and silently writes the newest one onto any PVC that doesn't name a class explicitly. Here that's `broken-fast-ssd`, whose provisioner (`kubernetes.io/no-such-provisioner`) doesn't exist, so the PVC can never be provisioned — while the older, working default is shadowed and never even considered.
**Fix:**
```bash
kubectl get pvc app-data -o jsonpath='{.spec.storageClassName}'   # shows "broken-fast-ssd" — not what anyone intended
kubectl get storageclass                                          # (default) marker shows on both
kubectl annotate storageclass broken-fast-ssd storageclass.kubernetes.io/is-default-class=false --overwrite
```
**Verify:**
```bash
kubectl get storageclass                      # exactly one shows (default)
kubectl delete pvc app-data && kubectl apply -f app-data-pvc.yaml
kubectl get pvc app-data -o jsonpath='{.spec.storageClassName}'   # now the real default
kubectl get pvc app-data                      # Bound (or Pending+WaitForFirstConsumer if that's the binding mode)
```
**Common wrong turn candidates take:** Assuming two default-annotated classes means the PVC binding is stuck on an unresolved "conflict" and hunting Events for an ambiguity error that doesn't exist, instead of just checking which `storageClassName` was actually assigned — the selection is deterministic (newest wins), not blocked, so the fix is removing the default annotation from the wrong (newer) class, not from either one at random. Explicitly hardcoding `storageClassName` on this one PVC as a workaround also "fixes" the symptom locally but leaves every future unclassed PVC silently landing on the broken class.

</details>

---

### Scenario 10 — The wall that blocks the mailroom too
**Time limit:** 8 min · **Skills tested:** NetworkPolicy default-deny + DNS egress carve-out · **Points/difficulty:** Hard

**Symptom:** In namespace `orders`, application pods that were working fine now can't reach any Service by DNS name — `nslookup <svc>.orders.svc.cluster.local` from inside a pod times out. CoreDNS pods themselves show `Running`, 0 restarts, healthy logs.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl create ns orders
kubectl create deployment app --image=nginx -n orders
cat <<'EOF' | kubectl apply -n orders -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress: []
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

CoreDNS being healthy tells you the problem is not the DNS server — it's whether pods in `orders` are even *allowed* to send a packet to it. Check what's applied in the `orders` namespace itself, not `kube-system`.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** A default-deny egress `NetworkPolicy` in `orders` blocks all outbound traffic, including UDP/TCP port 53 to `kube-system` where CoreDNS lives — DNS fails for every pod in the namespace even though CoreDNS itself is perfectly healthy.
**Fix:**
```bash
kubectl get networkpolicy -n orders
cat <<'EOF' | kubectl apply -n orders -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
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
kubectl run tmp --rm -it --image=busybox:1.36 -n orders -- nslookup kubernetes.default
```
**Common wrong turn candidates take:** Restarting/scaling CoreDNS or inspecting the `coredns` ConfigMap at length, because "it's a DNS problem" — when the actual fault lives entirely in the requesting namespace's NetworkPolicy, not in CoreDNS configuration at all.

</details>

---

### Scenario 11 — The good neighbor who's suddenly a stranger
**Time limit:** 7 min · **Skills tested:** NetworkPolicy ingress selector precision · **Points/difficulty:** Medium

**Symptom:** Pods labeled `app=backend` in namespace `prod` used to accept traffic from `app=frontend` pods on port 8080. After a policy change, `frontend`→`backend` requests now time out, but `backend` pods themselves report healthy in `describe`.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl create ns prod
kubectl run backend --image=hashicorp/http-echo -n prod --labels=app=backend -- -listen=:8080 -text=ok
kubectl run frontend --image=busybox -n prod --labels=app=frontend -- sleep 3600
kubectl expose pod backend --port=8080 -n prod
cat <<'EOF' | kubectl apply -n prod -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: fronted    # typo: "fronted" not "frontend"
    ports:
    - protocol: TCP
      port: 8080
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

The policy exists and looks reasonable at a glance. Read every character of the `podSelector.matchLabels` value against the actual label on the source pod — don't just confirm the field is present.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The ingress rule's `podSelector` matches `app: fronted` (typo) instead of `app: frontend`, so the intended source pods never match the allow rule, and — because any `NetworkPolicy` selecting a pod switches that pod to default-deny for the covered direction — `backend` now rejects everyone, including the real `frontend`.
**Fix:**
```bash
kubectl get networkpolicy backend-allow-frontend -n prod -o yaml | grep -A2 podSelector
kubectl edit networkpolicy backend-allow-frontend -n prod   # fix "fronted" -> "frontend"
```
**Verify:**
```bash
kubectl exec -n prod frontend -- wget -qO- --timeout=3 backend:8080
```
**Common wrong turn candidates take:** Assuming the policy is fine because it "exists and has an ingress rule," and instead investigating the Service or CNI plugin — a NetworkPolicy that exists but has a mismatched selector fails silently (traffic just times out) with no error naming the typo anywhere.

</details>

---

### Scenario 12 — The container that dies before it even tries
**Time limit:** 5 min · **Skills tested:** CrashLoopBackOff root-causing, --previous logs · **Points/difficulty:** Easy

**Symptom:** Pod `worker` is in `CrashLoopBackOff`, restart count climbing. `kubectl logs worker` returns nothing.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl run worker --image=busybox -- /bin/nonexistent-script.sh
# no --restart=Never here: the pod needs the default restartPolicy (Always) so the
# kubelet actually retries and racks up a restart count — Never would just leave it
# as a single Failed pod, not a genuine CrashLoopBackOff
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl logs` with no flags only shows the *current* attempt, which for a crashlooping container is often already empty by the time you look. There's a specific flag for the crashed attempt's output.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The pod's `args` is `["/bin/nonexistent-script.sh"]` — since the `busybox` image defines no `ENTRYPOINT`, that args value becomes the effective process to exec directly, and that path doesn't exist inside the image, so the container fails at exec time before producing any stdout — visible only via the container runtime's own status/events, not app logs.
**Fix:**
```bash
kubectl describe pod worker | grep -A5 "Last State"
kubectl logs worker --previous
kubectl delete pod worker
kubectl run worker --image=busybox --restart=Never -- sleep 3600
```
**Verify:**
```bash
kubectl get pod worker -w    # Running, restart count stable
```
**Common wrong turn candidates take:** Concluding "no logs = no clue" and escalating straight to `journalctl`/`crictl` on the node, when `kubectl describe pod`'s `Last State: Terminated: Reason` (e.g. `StartError`/`ContainerCannotRun`) already answers it at the API level.

</details>

---

### Scenario 13 — The memory diet nobody agreed to
**Time limit:** 6 min · **Skills tested:** OOMKilled diagnosis vs generic crash · **Points/difficulty:** Medium

**Symptom:** Pod `cache` restarts every 30-60 seconds, exit code shown in `describe` is `137`. CPU usage looks fine in `kubectl top`.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl run cache --image=polinux/stress \
  --limits=memory=20Mi --requests=memory=20Mi \
  -- stress --vm 1 --vm-bytes 150M --vm-hang 0
# no --restart=Never here: with the default restartPolicy (Always), the kubelet actually
# restarts the OOMKilled container repeatedly — Never would leave it as one dead pod, not a cycle
```

<details>
<summary>Hint (use only if stuck)</summary>

Exit code 137 always means SIGKILL — but SIGKILL has more than one possible sender. Check `describe pod`'s `Last State` block for the specific reason string before assuming which one.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The container's memory `limit` (20Mi) is far below what the workload actually needs (~150M requested by `stress`), so the kernel OOM-killer terminates it repeatedly — `Last State: Terminated: Reason: OOMKilled` confirms this specifically (vs. a liveness-probe-triggered SIGKILL, which shows a different reason).
**Fix:**
```bash
kubectl describe pod cache | grep -A6 "Last State"
kubectl delete pod cache
kubectl run cache --image=polinux/stress --restart=Never \
  --limits=memory=200Mi --requests=memory=200Mi \
  -- stress --vm 1 --vm-bytes 150M --vm-hang 0
```
**Verify:**
```bash
kubectl get pod cache -w             # stable, no restart climb
kubectl top pod cache                # usage comfortably under new limit
```
**Common wrong turn candidates take:** Raising `resources.requests` instead of `resources.limits` (requests only affect scheduling/QoS, not the enforced ceiling that triggers OOMKill) — the pod keeps crashing because the limit, not the request, was the actual constraint.

</details>

---

### Scenario 14 — The liveness probe that never gives the app a chance
**Time limit:** 7 min · **Skills tested:** liveness probe timing vs app startup time · **Points/difficulty:** Medium

**Symptom:** Pod `slow-api` cycles through `Running` → killed → `Running` every ~15 seconds. The application, when tested standalone (outside the cluster), works fine and only takes about 25 seconds to become ready to serve traffic.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: slow-api
spec:
  containers:
  - name: app
    image: nginx
    command: ["sh", "-c", "sleep 25 && nginx -g 'daemon off;'"]
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
      failureThreshold: 1
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

The app isn't broken — check the timing math. `initialDelaySeconds` + a couple of `periodSeconds` cycles versus how long the app genuinely takes to start listening.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `livenessProbe.initialDelaySeconds` (5s) is far shorter than the app's real startup time (25s), so the probe starts failing and killing the container (`failureThreshold: 1` makes it merciless) long before nginx is even listening — the container never survives long enough to become genuinely healthy.
**Fix:** either raise `initialDelaySeconds` well past the real startup time, or better, add a `startupProbe` to cover the slow-start window separately from steady-state liveness checks:
```bash
kubectl edit pod slow-api   # (or delete/recreate — most probe fields aren't mutable in place)
```
```yaml
    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 6
      periodSeconds: 5
    livenessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 10
```
**Verify:**
```bash
kubectl get pod slow-api -w      # stays Running past 60s with restart count 0
```
**Common wrong turn candidates take:** Assuming the app image itself is broken (rebuilding, checking Dockerfile) because it "keeps crashing," rather than reading the `describe pod` Events, which explicitly show `Liveness probe failed` immediately before every `Killing` event.

</details>

---

### Scenario 15 — The node that quietly stopped answering
**Time limit:** 8 min · **Skills tested:** Node NotReady triage, kubelet vs containerd layering · **Points/difficulty:** Hard

**Symptom:** `kubectl get nodes` shows worker node `<name>` as `NotReady`. Pods previously running there show `Unknown`/stuck `Terminating`. The node responds to `ping`/SSH fine.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
# on the worker node:
sudo systemctl stop containerd
# leave kubelet running — this isolates the fault to the runtime layer, not kubelet itself
```

<details>
<summary>Hint (use only if stuck)</summary>

Don't fixate on the kubelet first just because "NotReady = kubelet problem" is the common assumption. Check both services independently before diagnosing further — the node responding to ping/SSH already rules out a total network/host outage.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `containerd` is stopped, so the kubelet (still running) can't reach the CRI socket to report container/pod status or run new containers — the node self-reports `NotReady` even though the kubelet process itself is healthy.
**Fix:**
```bash
kubectl describe node <name> | grep -A10 Conditions
ssh <name>
systemctl status kubelet containerd     # kubelet active, containerd inactive/dead
crictl info                              # will error: cannot connect to the runtime
sudo systemctl start containerd
```
**Verify:**
```bash
kubectl get nodes                        # <name> back to Ready
kubectl get pods -A -o wide --field-selector spec.nodeName=<name>   # pods reschedule/resume
```
**Common wrong turn candidates take:** Restarting kubelet repeatedly (`systemctl restart kubelet`) without checking containerd's status first — kubelet restarts cleanly and looks "fine" in its own status output, but the node stays `NotReady` because the actual broken layer is one level below it.

</details>

---

### Scenario 16 — The scheduler that's technically alive but not helping
**Time limit:** 8 min · **Skills tested:** distinguishing "nothing fits" Pending from "scheduler itself is down" · **Points/difficulty:** Hard

**Symptom:** Multiple newly created Pods across different namespaces are all stuck `Pending`. `kubectl describe pod` on any of them shows no `FailedScheduling` event at all — the Events section is simply empty.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice, single control-plane lab):**
```bash
sudo mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/kube-scheduler.yaml.bak
kubectl run test1 --image=busybox --restart=Never -- sleep 3600
```

<details>
<summary>Hint (use only if stuck)</summary>

An empty Events section on a Pending pod is itself informative — it means nothing ever *tried* to schedule it and failed; something further upstream never ran at all. Check whether the component responsible for scheduling decisions is even present.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `kube-scheduler`'s static pod manifest was moved out of `/etc/kubernetes/manifests`, so the kubelet deleted the corresponding static pod and the scheduler component is entirely absent from the cluster — no `FailedScheduling` events are generated because no scheduler ever evaluated the pods in the first place.
**Fix:**
```bash
kubectl get pods -n kube-system | grep scheduler     # missing entirely
sudo mv /tmp/kube-scheduler.yaml.bak /etc/kubernetes/manifests/kube-scheduler.yaml
```
**Verify:**
```bash
kubectl get pods -n kube-system | grep scheduler     # Running within ~20s
kubectl get pod test1 -o wide                        # transitions to Running with a NODE assigned
```
**Common wrong turn candidates take:** Repeatedly checking taints, affinity rules, and resource requests on the stuck pods (the usual Pending playbook) when the actual signal — a completely empty Events section instead of a populated `FailedScheduling` reason — already pointed at "no scheduler is running" rather than "scheduler rejected this pod."

</details>

---

### Scenario 17 — The Job that fills the node's disk one log line at a time
**Time limit:** 8 min · **Skills tested:** DiskPressure eviction, distinguishing from OOM/CPU issues · **Points/difficulty:** Hard

**Symptom:** Several unrelated Pods on worker node `<name>` are getting evicted with reason `Evicted` and message referencing ephemeral storage, even though their own `resources.limits` look generous and `kubectl top pod` shows low CPU/memory.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice — disposable lab node only):**
```bash
kubectl run logspammer --image=busybox --restart=Never \
  --overrides='{"spec":{"nodeName":"<worker-node>"}}' \
  -- sh -c 'while true; do head -c 50M /dev/urandom; sleep 1; done'
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl top` reports CPU/memory, not disk. The node's own `Conditions` block reports a different pressure type — check which one is actually `True` before assuming this is a memory story.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** `logspammer`'s runaway stdout output fills the node's filesystem (container logs are captured to disk by the runtime), triggering the node's `DiskPressure` condition; the kubelet then evicts other pods by QoS class to reclaim space — the evicted pods themselves are innocent, the true offender is the noisy one filling the disk.
**Fix:**
```bash
kubectl describe node <name> | grep -A5 Conditions       # DiskPressure: True
kubectl delete pod logspammer
ssh <name> -- df -h
ssh <name> -- crictl rmi --prune                          # reclaim space from unused images if needed
```
**Verify:**
```bash
kubectl describe node <name> | grep -A5 Conditions       # DiskPressure: False
kubectl get events -A --field-selector reason=Evicted    # stops accumulating new entries
```
**Common wrong turn candidates take:** Raising `resources.limits`/`requests` on the *evicted* pods to try to "give them more room," when the actual fault is a completely different pod consuming node-level disk — QoS-based eviction targets victims by class/usage, not by cause, so the evicted pod's own spec is rarely where the fix belongs.

</details>

---

### Scenario 18 — The manifest edit that looked harmless
**Time limit:** 8 min · **Skills tested:** static pod manifest repair, crictl-based diagnosis when kubectl is unreachable · **Points/difficulty:** Hard

**Symptom:** `kubectl` from the control-plane node itself returns `The connection to the server <ip>:6443 was refused - did you specify the right host or port?` for every command.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice, single control-plane lab):**
```bash
sudo sed -i 's/--secure-port=6443/--secure-port=6443x/' /etc/kubernetes/manifests/kube-apiserver.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

`kubectl` is unusable by definition here — that's the point of the scenario. There's a tool that talks directly to the container runtime and works even when the apiserver is fully down.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** A typo'd flag value (`--secure-port=6443x`) in the `kube-apiserver` static pod manifest is not a valid integer, so the apiserver binary fails to start at all — the kubelet keeps retrying the static pod, but it crashloops before ever binding a port, making `kubectl` unreachable from any host.
**Fix:**
```bash
sudo crictl ps -a | grep apiserver                 # shows Exited, high restart count
sudo crictl logs $(sudo crictl ps -a --name kube-apiserver -q | head -1)   # shows the flag-parse error
sudo cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep secure-port
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml   # fix 6443x -> 6443
```
**Verify:**
```bash
sudo crictl ps -a | grep apiserver     # Running, restart count stops climbing
kubectl get nodes                      # kubectl works again within ~20-30s
```
**Common wrong turn candidates take:** Trying `kubectl edit pod kube-apiserver-<node>` (impossible — `kubectl` itself is down, and even if it weren't, the mirror pod is read-only) or assuming the whole control plane needs to be rebuilt with `kubeadm reset`/`kubeadm init` instead of a two-minute manifest fix.

</details>

---

### Scenario 19 — The wrong path in the certs mount
**Time limit:** 7 min · **Skills tested:** static pod hostPath volume diagnosis · **Points/difficulty:** Medium

**Symptom:** `kubectl get pods -n kube-system` shows `kube-controller-manager-<node>` in `CrashLoopBackOff`. `kubectl get nodes` and basic `kubectl` commands still work fine (apiserver is healthy) — but newly created Deployments never get a ReplicaSet created for them.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
sudo sed -i 's#path: /etc/kubernetes/pki#path: /etc/kubernetes/pki-typo#' /etc/kubernetes/manifests/kube-controller-manager.yaml
```

<details>
<summary>Hint (use only if stuck)</summary>

The apiserver being healthy while reconciliation silently stalls (no ReplicaSets appearing) points at one specific control-plane component. Since `kubectl logs` might not even reach a crashlooping static pod cleanly, check its container status directly at the runtime level.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** The `hostPath` volume mount for the controller-manager's cert directory was pointed at a nonexistent path (`/etc/kubernetes/pki-typo`), so the container can't find the certs it needs at startup and exits immediately — the apiserver is unaffected since it's a completely separate static pod.
**Fix:**
```bash
kubectl get pods -n kube-system | grep controller-manager
sudo crictl ps -a | grep controller-manager
sudo crictl logs <exited-container-id>
sudo vi /etc/kubernetes/manifests/kube-controller-manager.yaml   # fix path back to /etc/kubernetes/pki
```
**Verify:**
```bash
kubectl get pods -n kube-system | grep controller-manager   # Running, stable restart count
kubectl create deployment probe-test --image=nginx
kubectl get rs -l app=probe-test    # ReplicaSet actually gets created — proof reconciliation works
```
**Common wrong turn candidates take:** Trying `kubectl edit`/`kubectl apply` against the mirror pod object (no effect — source of truth is the file on disk), or restarting kubelet itself when kubelet was never the broken component.

</details>

---

### Scenario 20 — The PVC that's "stuck" but actually isn't
**Time limit:** 5 min · **Skills tested:** WaitForFirstConsumer binding mode, avoiding false-positive fixes · **Points/difficulty:** Easy (conceptual trap)

**Symptom:** A freshly created PVC `deferred-data` shows `STATUS: Pending` in `kubectl get pvc`, and no Pod references it yet.

**Setup (how this scenario is created, so you can reproduce it in a real cluster to practice):**
```bash
kubectl get storageclass                          # note a class with volumeBindingMode: WaitForFirstConsumer
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: deferred-data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: <class-with-waitforfirstconsumer>
  resources:
    requests:
      storage: 1Gi
EOF
```

<details>
<summary>Hint (use only if stuck)</summary>

Before treating `Pending` as broken, check the `StorageClass`'s `volumeBindingMode` field and whether any Pod currently references this PVC at all.
</details>

<details>
<summary>Root Cause & Fix (attempt it yourself first!)</summary>

**Root cause:** This isn't actually a bug — `volumeBindingMode: WaitForFirstConsumer` on the referenced StorageClass intentionally delays provisioning/binding until a Pod that uses the PVC is scheduled, so the PVC being `Pending` with no consuming Pod is expected behavior, not a failure to fix.
**Fix:** create a Pod that actually mounts the PVC — no PVC/StorageClass edit needed:
```bash
kubectl describe pvc deferred-data | grep -A3 Events   # "waiting for first consumer to be created before binding"
kubectl run consumer --image=busybox --restart=Never --overrides='
{"spec":{"containers":[{"name":"app","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"mountPath":"/data","name":"vol"}]}],"volumes":[{"name":"vol","persistentVolumeClaim":{"claimName":"deferred-data"}}]}}'
```
**Verify:**
```bash
kubectl get pvc deferred-data    # transitions to Bound once the pod schedules
```
**Common wrong turn candidates take:** "Fixing" the PVC by deleting and recreating it, switching its StorageClass, or hand-authoring a matching PV — all unnecessary and potentially destructive, since the real issue is simply that no consumer exists yet and the binding mode is working exactly as designed.

</details>
