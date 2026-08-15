# CKA Question Bank — Storage & RBAC

*24 original, hands-on exercises covering PV/PVC/StorageClass provisioning, access modes, reclaim policy, Pending-PVC troubleshooting (Storage — 10% weight, `P1`–`P2` per `01-exam-snapshot-and-priorities.md`), plus ServiceAccounts, Roles/RoleBindings, ClusterRoles/ClusterRoleBindings, `kubectl auth can-i`, and impersonation (RBAC — folded into Cluster Architecture 25% and Troubleshooting 30%, rated `P0`). Question count and difficulty are weighted toward RBAC because the priority matrix marks the whole domain `P0` for this candidate, versus Storage's `P1`/`P2`. All scenarios are original — built from the general skill/pattern described in `02-topics/storage.md` and `02-topics/rbac.md`, not reproduced or paraphrased from any real or claimed exam question. Attempt each task cold before opening the solution.*

---

## Part A — Storage (11 questions)

### Question 1 — Static PV from scratch
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create a PersistentVolume named `pv-reports-01` backed by `hostPath: /mnt/reports-data`, capacity `750Mi`, access mode `ReadWriteOnce`, reclaim policy `Retain`, and `storageClassName: manual`. Confirm it registers as `Available`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-reports-01
spec:
  capacity:
    storage: 750Mi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/reports-data
EOF
```

**Verify:**
```bash
k get pv pv-reports-01                                   # STATUS = Available, CLAIM = <none>
k describe pv pv-reports-01 | grep -E 'Status|Reclaim|StorageClass'
```

**Common mistake:** Forgetting `storageClassName: manual` — an unset class (`""`) only binds to a PVC that *also* has an empty `storageClassName`, so it would silently fail to match any PVC that explicitly asks for `manual`.

</details>

---

### Question 2 — PVC binds to a specific PV
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create namespace `reporting`. Create a PVC named `pvc-reports-01` in `reporting` requesting `500Mi`, `ReadWriteOnce`, `storageClassName: manual`, and confirm it binds specifically to `pv-reports-01` (Question 1) rather than any other PV that might also satisfy the request.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create ns reporting
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-reports-01
  namespace: reporting
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  resources:
    requests:
      storage: 500Mi
EOF
```

**Verify:**
```bash
k get pvc -n reporting pvc-reports-01     # STATUS=Bound, VOLUME=pv-reports-01
k get pv pv-reports-01                    # STATUS=Bound, CLAIM=reporting/pvc-reports-01
```

**Common mistake:** Assuming a PVC always binds to the PV you "meant" — if more than one `manual`-class, RWO, sufficiently-sized PV exists, Kubernetes binds to whichever satisfies the request first. Use `spec.volumeName` on the PVC if you must force an exact match.

</details>

---

### Question 3 — Mount a PVC and confirm data persistence
**Priority:** P2 · **Difficulty:** Easy · **Target time:** 5 min
**Task:** Mount `pvc-reports-01` into a new Pod `reports-writer` (image `busybox`, command `sleep 3600`) at `/data` in namespace `reporting`. Write a file into it, delete the Pod, recreate an identically-spec'd Pod, and confirm the file survives.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' > reports-writer.yaml
apiVersion: v1
kind: Pod
metadata:
  name: reports-writer
  namespace: reporting
spec:
  containers:
    - name: writer
      image: busybox
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: pvc-reports-01
EOF
k apply -f reports-writer.yaml
k exec -n reporting reports-writer -- sh -c 'echo persisted > /data/marker.txt'
k delete pod -n reporting reports-writer
k apply -f reports-writer.yaml
```

**Verify:**
```bash
k exec -n reporting reports-writer -- cat /data/marker.txt   # prints "persisted"
```

**Common mistake:** Assuming deleting the Pod deletes the data. A PVC (and its bound PV, unless the PV's reclaim policy is `Delete` *and* the PVC itself is also removed) outlives any Pod that mounts it.

</details>

---

### Question 4 — Access-mode mismatch on a hostPath-backed claim
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** A PVC `pvc-cache-rwx` in namespace `reporting` requests `ReadWriteMany` against `storageClassName: manual`, where the only PV of that class is `hostPath`-backed and advertises only `ReadWriteOnce`. Diagnose exactly why it won't bind, then fix it — try the most obvious in-place fix first, observe what the API says, then apply the correct fix.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-cache-rwx
  namespace: reporting
spec:
  accessModes: ["ReadWriteMany"]
  storageClassName: manual
  resources:
    requests:
      storage: 100Mi
EOF
k describe pvc -n reporting pvc-cache-rwx
# Events: no persistent volumes available for this claim and no storage class is set / mode mismatch

k patch pvc -n reporting pvc-cache-rwx -p '{"spec":{"accessModes":["ReadWriteOnce"]}}'
# error: ...spec is immutable after creation... accessModes is one of a handful of PVC
# spec fields (accessModes, storageClassName, volumeMode, selector) the API refuses to update
```
`hostPath` can never serve `ReadWriteMany` anyway, so the realistic fix is deleting and recreating the PVC with the corrected mode (a real RWX workload would instead need an NFS/CSI backend, not just a mode change):
```bash
k delete pvc -n reporting pvc-cache-rwx
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-cache-rwx
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests:
      storage: 100Mi
EOF
```

**Verify:**
```bash
k get pvc -n reporting pvc-cache-rwx    # STATUS=Bound
```

**Common mistake:** Assuming `accessModes` can be patched in place once a PVC exists — the API rejects any change to it (along with `storageClassName`, `volumeMode`, and `selector`) as an immutable field regardless of Bound/Pending phase, so delete-and-recreate is the only real fix. A second trap: treating this as a size/quota problem and bumping `storage:` — the Events message names the capability gap explicitly; `hostPath` cannot serve `ReadWriteMany` regardless of requested size.

</details>

---

### Question 5 — Exactly one default StorageClass
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 4 min
**Task:** Your cluster currently has StorageClass `standard` marked default. Create a new StorageClass `fast-local` using the same provisioner as `standard`, with `allowVolumeExpansion: true`, and make it the new cluster default — ensure `standard` is no longer marked default afterward.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k get sc                                            # note current default's provisioner
PROV=$(k get sc standard -o jsonpath='{.provisioner}')
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-local
provisioner: $PROV
reclaimPolicy: Delete
allowVolumeExpansion: true
EOF
k patch storageclass standard -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
k patch storageclass fast-local -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

**Verify:**
```bash
k get sc     # exactly one row shows "(default)", and it's fast-local
```

**Common mistake:** Patching the new class to `true` without first un-defaulting the old one — both can legally carry the annotation simultaneously, which leaves default-class selection ambiguous for any PVC that omits `storageClassName`.

</details>

---

### Question 6 — `WaitForFirstConsumer` is not a bug
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Configure `fast-local` (Question 5) to use `volumeBindingMode: WaitForFirstConsumer` — try the obvious in-place fix first and observe why it's rejected, then apply it correctly. Create a PVC `pvc-deferred` in namespace `reporting` with no `storageClassName` set, requesting `50Mi`. Using command output (not assumption), explain why it stays `Pending`, then create a consuming Pod and confirm it transitions to `Bound`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k patch storageclass fast-local -p '{"volumeBindingMode":"WaitForFirstConsumer"}'
# error: StorageClass.storage.k8s.io "fast-local" is invalid: volumeBindingMode: Invalid value:
# "WaitForFirstConsumer": field is immutable — provisioner, parameters, reclaimPolicy, and
# volumeBindingMode can only be set at StorageClass creation time

# no PV/PVC references fast-local yet, so delete/recreate is safe:
PROV=$(k get sc fast-local -o jsonpath='{.provisioner}')
k delete storageclass fast-local
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-local
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: $PROV
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-deferred
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 50Mi
EOF
k describe pvc -n reporting pvc-deferred
# Events: waiting for first consumer to be created before binding

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: deferred-consumer
  namespace: reporting
spec:
  containers:
    - name: app
      image: busybox
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: pvc-deferred
EOF
```

**Verify:**
```bash
k get pvc -n reporting pvc-deferred   # STATUS flips to Bound once the Pod schedules
```

**Common mistake:** Trying to `patch`/`edit` `volumeBindingMode` on an existing StorageClass — it's immutable (along with `provisioner`, `parameters`, and `reclaimPolicy`), so changing it always requires deleting and recreating the object. Separately: deleting/recreating the PVC or "fixing" the StorageClass the moment it's seen `Pending` with no Pod present is also wrong — under `WaitForFirstConsumer`, that's the designed behavior, not a failure.

</details>

---

### Question 7 — Retain reclaim policy lifecycle
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 7 min
**Task:** `pv-reports-01` (Question 1) is currently Bound to `pvc-reports-01`. Delete `pvc-reports-01`. Confirm the PV neither disappears nor becomes auto-reusable. Then, without recreating the PV object, manually make it bindable again for a brand-new PVC.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k get pv pv-reports-01 -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'   # confirm Retain
k delete pvc -n reporting pvc-reports-01
k get pv pv-reports-01     # STATUS=Released, CLAIM still shows stale reporting/pvc-reports-01
k patch pv pv-reports-01 -p '{"spec":{"claimRef": null}}'
k get pv pv-reports-01     # STATUS back to Available
```

**Verify:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-reports-02
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests:
      storage: 500Mi
EOF
k get pvc -n reporting pvc-reports-02   # Bound to pv-reports-01
```

**Common mistake:** Assuming `Released` means the PV is already free to bind, or that the data is already gone — under `Retain`, both the stale `claimRef` and the underlying data persist until an admin explicitly clears `claimRef` (or deletes and recreates the PV).

</details>

---

### Question 8 — Troubleshoot a Pending PVC: nonexistent StorageClass
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** PVC `pvc-billing` in namespace `reporting` has been `Pending` for several minutes. Find the root cause. If your first fix attempt is rejected by the API, read why before deciding what to do next.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve (setup representing a pre-broken state you're handed):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-billing
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: gold-tier
  resources:
    requests:
      storage: 200Mi
EOF
k describe pvc -n reporting pvc-billing
# Events: storageclass.storage.k8s.io "gold-tier" not found

k patch pvc -n reporting pvc-billing -p '{"spec":{"storageClassName":"manual"}}'
# error: ...spec is immutable after creation... storageClassName cannot be changed once set
```
`storageClassName` is immutable on an existing PVC, so repoint it by deleting and recreating with the corrected class, then ensure a matching PV exists:
```bash
k delete pvc -n reporting pvc-billing
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-billing
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests:
      storage: 200Mi
EOF
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-billing-01
spec:
  capacity:
    storage: 300Mi
  accessModes: ["ReadWriteOnce"]
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/billing-data
EOF
```

**Verify:**
```bash
k get pvc -n reporting pvc-billing    # STATUS=Bound
```

**Common mistake:** Assuming `storageClassName` can be patched on an existing PVC — like `accessModes` and `volumeMode`, it's immutable once the object is created regardless of Bound/Pending phase, and the API rejects the patch outright. Read `describe`'s Events block first to confirm the real cause, then delete-and-recreate the PVC with the corrected class — there's no live binding to lose since it was never `Bound`.

</details>

---

### Question 9 — Troubleshoot a Pending PVC: the decoy is access mode, not class
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** PVC `pvc-audit` in namespace `reporting` requests `storageClassName: manual`, `ReadWriteOnce`, `150Mi`, and is `Pending`. A PV of the right class and sufficient size already exists and shows `Available`. Find the real mismatch (it is not size or class) and fix it by editing the existing PV — do not delete/recreate the PVC.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve (setup):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-audit-01
spec:
  capacity:
    storage: 300Mi
  accessModes:
    - ReadOnlyMany        # trap: PVC needs RWO, this PV only offers ROX
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/audit-data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-audit
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests:
      storage: 150Mi
EOF
```
Diagnose:
```bash
k describe pvc -n reporting pvc-audit         # generic "no persistent volumes available" message
k get pv -o custom-columns=NAME:.metadata.name,CLASS:.spec.storageClassName,ACCESS:.spec.accessModes,STATUS:.status.phase
# pv-audit-01: class=manual, size sufficient, STATUS=Available — but ACCESS=[ReadOnlyMany] only
```
Fix:
```bash
k patch pv pv-audit-01 -p '{"spec":{"accessModes":["ReadWriteOnce"]}}'
```

**Verify:**
```bash
k get pvc -n reporting pvc-audit   # STATUS=Bound, VOLUME=pv-audit-01
```

**Common mistake:** Stopping at "class matches, size matches, so it must be a provisioner issue" — access mode is a separate, easy-to-skip binding criterion. Always diff `accessModes` on both objects explicitly rather than assuming any `Available` PV of the right class is automatically compatible.

</details>

---

### Question 10 — Resize a PVC in place
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** `pvc-reports-02` currently requests `500Mi` against class `manual`. Increase it to `800Mi` in place, without deleting/recreating it. If the patch has no visible effect, identify the missing precondition and fix it, then retry.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k patch pvc -n reporting pvc-reports-02 -p '{"spec":{"resources":{"requests":{"storage":"800Mi"}}}}'
k get pvc -n reporting pvc-reports-02 -o jsonpath='{.status.capacity.storage}'
# still 500Mi -> the storage class doesn't allow expansion
k get sc manual -o jsonpath='{.allowVolumeExpansion}'   # empty/false
k patch storageclass manual -p '{"allowVolumeExpansion": true}'
k patch pvc -n reporting pvc-reports-02 -p '{"spec":{"resources":{"requests":{"storage":"800Mi"}}}}'
```

**Verify:**
```bash
k get pvc -n reporting pvc-reports-02 -w   # watch until CAPACITY becomes 800Mi
```

**Common mistake:** Only patching the PVC and concluding "resize doesn't work here" without first checking whether the referenced StorageClass permits expansion — the API accepts the PVC patch silently either way; it just never materializes without `allowVolumeExpansion: true`.

</details>

---

### Question 11 — `volumeMode` mismatch (Block vs. Filesystem)
**Priority:** P2 · **Difficulty:** Hard · **Target time:** 6 min
**Task:** PVC `pvc-block-test` in namespace `reporting`, requesting `volumeMode: Block`, stays `Pending` even though a same-class, same-size, same-access-mode PV exists and shows `Available`. Identify the exact field causing the mismatch and fix it on the PVC.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve (setup):**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-fs-only
spec:
  capacity:
    storage: 100Mi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  hostPath:
    path: /mnt/fs-only
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-block-test
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  volumeMode: Block
  resources:
    requests:
      storage: 100Mi
EOF
k get pv pv-fs-only -o jsonpath='{.spec.volumeMode}'
k get pvc -n reporting pvc-block-test -o jsonpath='{.spec.volumeMode}'

k patch pvc -n reporting pvc-block-test -p '{"spec":{"volumeMode":"Filesystem"}}'
# error: ...spec is immutable after creation... volumeMode cannot be changed once set
```
`hostPath` cannot back a raw block device anyway, and `volumeMode` is immutable on an existing PVC, so the realistic fix is deleting and recreating it with the corrected intent:
```bash
k delete pvc -n reporting pvc-block-test
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-block-test
  namespace: reporting
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  volumeMode: Filesystem
  resources:
    requests:
      storage: 100Mi
EOF
```

**Verify:**
```bash
k get pvc -n reporting pvc-block-test   # STATUS=Bound
```

**Common mistake:** Checking size, access mode, and `storageClassName`, finding them all correct, and assuming a provisioner bug — `volumeMode` is a fourth, independent binding criterion that's easy to forget during triage. It's also immutable on the PVC once created (like `accessModes` and `storageClassName`), so the fix is delete-and-recreate, not `kubectl patch`/`edit`.

</details>

---

## Part B — RBAC (13 questions)

### Question 12 — ServiceAccount + on-demand token
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** In namespace `ci-tools` (create it), create a ServiceAccount `pipeline-runner`. Mint a 30-minute token for it. Confirm it currently has zero permission to list Pods in that namespace.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create ns ci-tools
k create sa pipeline-runner -n ci-tools
k create token pipeline-runner -n ci-tools --duration=30m
```

**Verify:**
```bash
k auth can-i list pods --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools   # no
```

**Common mistake:** Forgetting the fully-qualified `system:serviceaccount:<namespace>:<name>` form with `--as` — bare `--as=pipeline-runner` impersonates a *User* named `pipeline-runner`, not the ServiceAccount, and silently gives a meaningless answer.

</details>

---

### Question 13 — Namespace-scoped Role + RoleBinding
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Grant `pipeline-runner` (namespace `ci-tools`) permission to `get`/`list`/`watch` `pods`, scoped only to `ci-tools`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create role pod-viewer -n ci-tools --verb=get,list,watch --resource=pods
k create rolebinding pipeline-runner-pods -n ci-tools --role=pod-viewer --serviceaccount=ci-tools:pipeline-runner
```

**Verify:**
```bash
k auth can-i list pods --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools     # yes
k auth can-i list pods --as=system:serviceaccount:ci-tools:pipeline-runner -n default      # no
```

**Common mistake:** Using `--serviceaccount=<name>` without the `<namespace>:` prefix in `create rolebinding` — the flag requires the `namespace:name` form; omitting it errors or silently targets the wrong SA.

</details>

---

### Question 14 — `can-i` and the namespace-flag trap
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Without creating any new bindings, determine whether `pipeline-runner` can `get` `configmaps` in namespace `kube-public`, then whether it can in `ci-tools`. Then demonstrate why running the same check with no `-n` at all would be misleading.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k auth can-i get configmaps --as=system:serviceaccount:ci-tools:pipeline-runner -n kube-public   # no
k auth can-i get configmaps --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools       # no (only pods granted so far)
k auth can-i get configmaps --as=system:serviceaccount:ci-tools:pipeline-runner                   # uses YOUR current-context namespace, not ci-tools
```

**Verify:**
```bash
kubectl config view --minify -o jsonpath='{.contexts[0].context.namespace}'
# compare this against whatever the no -n check silently used
```

**Common mistake:** Trusting `can-i`'s answer without an explicit `-n` — it silently defaults to your *current kubectl context's* namespace, which may have nothing to do with the identity or resource actually in question.

</details>

---

### Question 15 — Subresource permissions (`pods/log`)
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** `pipeline-runner` also needs to read Pod logs. Adjust the existing `pod-viewer` Role so `k auth can-i get pods/log --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools` returns `yes`, without removing its existing Pod permissions.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k get role pod-viewer -n ci-tools -o yaml > pod-viewer.yaml
cat <<'EOF' >> pod-viewer.yaml
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
EOF
k apply -f pod-viewer.yaml
```

**Verify:**
```bash
k auth can-i get pods/log --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools   # yes
k auth can-i list pods --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools       # still yes
```

**Common mistake:** Assuming granting `pods` automatically covers `pods/log` — subresources are distinct resource strings in RBAC rules and must be listed explicitly, even though they conceptually "belong to" the same object.

</details>

---

### Question 16 — `roleRef` is immutable
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 4 min
**Task:** RoleBinding `pipeline-runner-pods` currently references Role `pod-viewer`. Re-point it to a new Role, `pod-viewer-v2`. Attempt the most obvious fix first, observe why it fails, then apply the correct fix.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create role pod-viewer-v2 -n ci-tools --verb=get,list,watch,delete --resource=pods
k patch rolebinding pipeline-runner-pods -n ci-tools -p '{"roleRef":{"name":"pod-viewer-v2"}}'
# error: roleRef is immutable — the patch is rejected by the API
k delete rolebinding pipeline-runner-pods -n ci-tools
k create rolebinding pipeline-runner-pods -n ci-tools --role=pod-viewer-v2 --serviceaccount=ci-tools:pipeline-runner
```

**Verify:**
```bash
k auth can-i delete pods --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools   # yes
```

**Common mistake:** Burning exam time trying every `edit`/`patch` variant to change `roleRef` — it's immutable by API validation, full stop. The only path is delete-and-recreate the binding.

</details>

---

### Question 17 — ClusterRole for a cluster-scoped resource + non-resource URL
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 4 min
**Task:** Create a ClusterRole `node-inspector` allowing `get`/`list`/`watch` on `nodes` and `get` on the non-resource URL `/healthz`. Bind it cluster-wide to ServiceAccount `pipeline-runner` (namespace `ci-tools`).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-inspector
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/healthz"]
  verbs: ["get"]
EOF
k create clusterrolebinding pipeline-runner-nodes --clusterrole=node-inspector --serviceaccount=ci-tools:pipeline-runner
```

**Verify:**
```bash
k auth can-i get nodes --as=system:serviceaccount:ci-tools:pipeline-runner              # yes (cluster-scoped, no -n needed)
k auth can-i get /healthz --as=system:serviceaccount:ci-tools:pipeline-runner           # yes (non-resource URL grant)
k auth can-i list pods --as=system:serviceaccount:ci-tools:pipeline-runner -n default   # still no — unrelated grant
```

**Common mistake:** Trying to add the `nonResourceURLs` rule via `k create clusterrole ... --resource=nodes` in one imperative command — imperative `create clusterrole` has no flag for non-resource URL rules; they require hand-written or patched YAML.

</details>

---

### Question 18 — Reuse a built-in ClusterRole at namespace scope
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 4 min
**Task:** Grant `pipeline-runner` the built-in `view` ClusterRole, but only inside namespace `ci-tools` — not cluster-wide. Confirm the access does not leak into namespace `default`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create rolebinding pipeline-runner-view -n ci-tools --clusterrole=view --serviceaccount=ci-tools:pipeline-runner
```

**Verify:**
```bash
k auth can-i list deployments --as=system:serviceaccount:ci-tools:pipeline-runner -n ci-tools   # yes
k auth can-i list deployments --as=system:serviceaccount:ci-tools:pipeline-runner -n default    # no
```

**Common mistake:** Reaching for `k create clusterrolebinding --clusterrole=view ...` instead — that grants `view` in *every* namespace, failing a "only this one namespace" requirement even though `view` itself is a cluster-scoped role object. Binding *kind* (RoleBinding vs. ClusterRoleBinding) controls the effective scope, not the referenced role's own scope-ness.

</details>

---

### Question 19 — Group binding with no Group object
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 4 min
**Task:** Create a ClusterRole `secret-viewer` allowing `get`/`list` on `secrets`. Bind it cluster-wide to group `sre-team` (there is no such Group object anywhere in Kubernetes). Then demonstrate that a typo'd group name is accepted silently at creation time but denied at `can-i` time.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create clusterrole secret-viewer --verb=get,list --resource=secrets
k create clusterrolebinding sre-secret-viewer --clusterrole=secret-viewer --group=sre-team
```

**Verify:**
```bash
k auth can-i list secrets --as=alice --as-group=sre-team -A     # yes
k auth can-i list secrets --as=alice --as-group=sre-tema -A     # no (typo'd group — bound fine, grants nothing)
```

**Common mistake:** Expecting a typo'd `--group=sre-tema` to fail at `create clusterrolebinding` time — RBAC never validates that a User or Group "exists" since neither is a real API object; the mistake is invisible until someone actually tries to use it and is denied.

</details>

---

### Question 20 — Granting impersonation rights
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 4 min
**Task:** Create a ClusterRole `identity-switcher` that allows impersonating Users, Groups, ServiceAccounts, and UIDs. Bind it to ServiceAccount `pipeline-runner`. Confirm the impersonation-level grant itself with `can-i` (not what the impersonated identity can do).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: identity-switcher
rules:
- apiGroups: [""]
  resources: ["users", "groups", "serviceaccounts"]
  verbs: ["impersonate"]
- apiGroups: ["authentication.k8s.io"]
  resources: ["uids"]
  verbs: ["impersonate"]
EOF
k create clusterrolebinding pipeline-runner-impersonate --clusterrole=identity-switcher --serviceaccount=ci-tools:pipeline-runner
```

**Verify:**
```bash
k auth can-i impersonate users --as=system:serviceaccount:ci-tools:pipeline-runner            # yes
k auth can-i impersonate serviceaccounts --as=system:serviceaccount:ci-tools:pipeline-runner   # yes
k auth can-i impersonate uids --as=system:serviceaccount:ci-tools:pipeline-runner               # yes
```

**Common mistake:** Putting all four resources under one `apiGroups: [""]` rule — `uids` lives in the `authentication.k8s.io` API group, not core; a single-group rule silently fails to grant UID impersonation.

</details>

---

### Question 21 — The two-layer impersonation check
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** `pipeline-runner` has impersonation rights (Question 20), but user `dana` has never been granted any Pod permissions anywhere. Predict, then confirm with commands, what happens when `pipeline-runner` runs `kubectl get pods -n ci-tools --as=dana`, and at which of the two authorization layers it is actually decided.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve / Verify:**
```bash
k auth can-i impersonate users --as=system:serviceaccount:ci-tools:pipeline-runner   # yes — layer 1 (impersonation itself) succeeds
k auth can-i get pods --as=dana -n ci-tools                                          # no — layer 2 (dana's own rights) is what actually gates the real request
```

**Common mistake:** Concluding that because impersonation is "allowed," the impersonated action must also succeed — these are two independent authorization checks. Passing the first only means the request is allowed to *proceed as* `dana`; it says nothing about what `dana` can do once there.

</details>

---

### Question 22 — Forbidden diagnosis: missing verb
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 6 min
**Task:** A controller in namespace `billing-app` uses SA `billing-runner` and is logging `Forbidden` errors trying to `watch` `configmaps`. Fix the cluster configuration (not the app) so it can, granting nothing beyond what's needed, and without recreating the SA or the binding.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve (setup representing pre-existing broken state):**
```bash
k create ns billing-app
k create sa billing-runner -n billing-app
k create role cm-reader -n billing-app --verb=get,list --resource=configmaps    # missing "watch" on purpose
k create rolebinding billing-cm -n billing-app --role=cm-reader --serviceaccount=billing-app:billing-runner
```
Diagnose and fix:
```bash
k auth can-i watch configmaps --as=system:serviceaccount:billing-app:billing-runner -n billing-app   # no
k edit role cm-reader -n billing-app
# change verbs: ["get","list"] to verbs: ["get","list","watch"]
```

**Verify:**
```bash
k auth can-i watch configmaps --as=system:serviceaccount:billing-app:billing-runner -n billing-app    # yes
k auth can-i delete configmaps --as=system:serviceaccount:billing-app:billing-runner -n billing-app   # no (unchanged — least privilege intact)
```

**Common mistake:** Jumping straight to `verbs: ["*"]` to "just make it work" — graders (and real production security) check that you added the exact missing verb, not a blanket wildcard.

</details>

---

### Question 23 — Forbidden diagnosis: the decoy is the binding's subject namespace
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 7 min
**Task:** SA `billing-runner` (namespace `billing-app`) gets `Forbidden` listing `secrets` — but this time the Role and its verbs are already completely correct. Find the actual cause and fix it without editing the Role at all.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve (setup — the decoy: the RoleBinding's subject references the SA in the wrong namespace):**
```bash
k create role secret-reader -n billing-app --verb=get,list --resource=secrets
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: billing-secret-binding
  namespace: billing-app
subjects:
- kind: ServiceAccount
  name: billing-runner
  namespace: billing-ops    # wrong — the real SA lives in billing-app
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
EOF
```
Diagnose:
```bash
k auth can-i list secrets --as=system:serviceaccount:billing-app:billing-runner -n billing-app   # no
k describe rolebinding billing-secret-binding -n billing-app
# Subjects: ServiceAccount billing-runner, namespace billing-ops (wrong)
```
Fix (unlike `roleRef`, `subjects` is mutable):
```bash
k patch rolebinding billing-secret-binding -n billing-app --type=json \
  -p='[{"op":"replace","path":"/subjects/0/namespace","value":"billing-app"}]'
```

**Verify:**
```bash
k auth can-i list secrets --as=system:serviceaccount:billing-app:billing-runner -n billing-app   # yes
```

**Common mistake:** Assuming any RBAC `Forbidden` means a missing rule and heading straight for the Role — always `describe` the binding first. A perfectly correct Role bound to the wrong subject produces an identical-looking `Forbidden`, but needs a completely different fix.

</details>

---

### Question 24 — A Role can't be referenced across namespaces
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** SA `billing-runner` lives in `billing-app`. A separate team wants that same SA to also read Pods in namespace `billing-reports` (a different namespace from where the SA lives). Using only a `Role` + `RoleBinding` pattern living in `billing-reports`, wire this up correctly.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create role pod-reader -n billing-reports --verb=get,list,watch --resource=pods
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: billing-runner-cross-ns
  namespace: billing-reports
subjects:
- kind: ServiceAccount
  name: billing-runner
  namespace: billing-app
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
EOF
```

**Verify:**
```bash
k auth can-i list pods --as=system:serviceaccount:billing-app:billing-runner -n billing-reports   # yes
```

**Common mistake:** Confusing which side of a RoleBinding may cross namespaces — the *subject* (SA) may reference a different namespace than the RoleBinding itself, but the *Role* named in `roleRef` must live in the same namespace as the RoleBinding. There is no such thing as a RoleBinding referencing a Role from a foreign namespace; that use case requires a `ClusterRole` instead.

</details>
