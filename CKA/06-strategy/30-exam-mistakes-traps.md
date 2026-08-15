# 30 CKA Exam Mistakes That Cost Real Points

*Grounded in `01-exam-snapshot-and-priorities.md` and the five `CKA/research/*.md` files (official LF/CNCF pages, etcd docs, and the handful of independently-fetched 2026 community articles), plus standard high-risk exam patterns. Each entry names the mistake, what it looks like in the moment, why it happens even to experienced engineers, and the one-line habit that prevents it. Ordered by where in the exam flow you'd hit it, not by severity — treat every P0-domain item (Cluster Architecture, Troubleshooting) as higher-stakes than its position in the list implies.*

None of these are reproductions of a specific real exam question — they're the general failure patterns the research converged on (etcd tool split, Kustomize's missing doc domain, PSI Bridge's proctoring constraints) plus standard CKA-shaped traps in kubeadm, RBAC, networking, storage, and scheduling.

---

## A. Exam logistics & environment (lose points before you've typed a command)

### 1. Dual-monitor or VM exam client setup
**What it looks like:** You launch the PSI Bridge check-in with a second monitor still connected, or you're running the exam client inside a VM because that's your normal dev setup.
**Why it happens:** Almost every other remote-proctored exam and normal daily workflow tolerates multiple monitors and VMs; CKA's handbook is stricter than what candidates assume by default.
**Habit:** The night before, do the system check on the exact single physical monitor, non-VM machine you'll test on — confirmed: dual monitors are explicitly unsupported and VMs are prohibited even if the compatibility checker doesn't flag it.

### 2. Not setting exam aliases before starting the clock
**What it looks like:** You're 20 minutes in, still typing `kubectl` in full and hand-writing `--dry-run=client -o yaml` from memory each time.
**Why it happens:** It feels like a "setup tax" candidates skip to "get to the real work faster," which is backwards — the alias pays for itself within 3 tasks.
**Habit:** First 60 seconds, every time: `alias k=kubectl` and `export do="--dry-run=client -o yaml"` (kubectl is already aliased to `k` in-exam, but re-confirm it and add the dry-run export yourself).

### 3. Wrong kubeconfig context/cluster for the task
**What it looks like:** You run a command, it "succeeds," but you're modifying the wrong cluster because a prior task told you to switch context and you never switched back.
**Why it happens:** Exams with multiple clusters/contexts routinely instruct a context switch per task; muscle memory from single-cluster daily work makes it easy to just keep going in whatever context is currently active.
**Habit:** Before every task, run `kubectl config current-context` (or check the prompt if it's set to show it) and confirm it matches what the task specifies — every single time, not just when the task "sounds like" a switch.

### 4. Wrong namespace (forgetting `-n` or assuming `default`)
**What it looks like:** A resource you created looks perfect in `default`, but the task specified `app-prod` — it silently doesn't count.
**Why it happens:** `kubectl` defaults to whatever namespace your current context has set (often `default`), and task text sometimes states the namespace once, early, and never repeats it.
**Habit:** Re-read every task for a namespace name before running anything, and pass `-n <namespace>` explicitly rather than relying on `kubectl config set-context --current --namespace=`.

---

## B. Cluster Architecture / kubeadm / etcd (largest non-Troubleshooting domain, 25%)

### 5. Using `etcdctl` to restore instead of `etcdutl`
**What it looks like:** You run `etcdctl snapshot restore` out of habit (or because an old tutorial showed it) and get an error or, worse, a partially-applied restore.
**Why it happens:** `etcdctl` used to do both backup and restore; the restore subcommand has been deprecated/removed from `etcdctl` since etcd v3.5 in favor of a separate binary, and a lot of still-circulating material hasn't caught up.
**Habit:** Say the split out loud as one rule: **`etcdctl` saves, `etcdutl` restores** — `etcdctl snapshot save` (network, talks to the live cluster), `etcdutl snapshot restore` (offline, operates directly on files).

### 6. Restoring the etcd snapshot to the wrong `--data-dir`, or not pointing the static pod at it
**What it looks like:** The restore command runs cleanly, but the API server still shows the old data — because the etcd static pod manifest was never updated to point at the new data directory, or you restored on top of the live directory instead of a fresh one.
**Why it happens:** `etcdutl snapshot restore` writes to a new directory you specify; it does not modify the running etcd's config for you, and it's easy to assume the restore is "done" once the command exits 0.
**Habit:** Always restore to a **new**, uniquely-named data directory, then edit `/etc/kubernetes/manifests/etcd.yaml`'s `--data-dir` (and matching volume `hostPath`) to point at it — and verify with `etcdctl endpoint status` / `kubectl get pods -n kube-system` afterward, don't trust the restore command's exit code alone.

### 7. Getting `kubeadm upgrade apply` vs `kubeadm upgrade node` backwards
**What it looks like:** You run `kubeadm upgrade apply` on a second control-plane node, or `kubeadm upgrade node` on the first one, and it either errors or silently does the wrong thing for HA setups.
**Why it happens:** The two subcommands look almost interchangeable by name, but only the **first** control-plane node uses `upgrade apply`; every other control-plane and every worker node uses `upgrade node`.
**Habit:** Before touching any node, ask "is this the first control-plane node I'm upgrading in this cluster?" — if yes, `apply`; if no (including additional control-plane nodes), `node`.

### 8. Forgetting to `uncordon` a node after maintenance/upgrade
**What it looks like:** The upgrade or maintenance task itself is done correctly, but the node stays `SchedulingDisabled` and the grader (or a later task depending on that node's capacity) fails.
**Why it happens:** `drain`/`cordon` is the memorable, active step; `uncordon` is a cleanup step at the very end, easy to forget once the "interesting" work is finished and you've mentally moved to the next task.
**Habit:** Treat cordon and uncordon as a single unit of work — don't mark a drain/upgrade task complete until you've run `kubectl get nodes` and confirmed the node shows `Ready` with no `SchedulingDisabled`.

### 9. Editing a static pod via `kubectl edit` instead of its manifest file
**What it looks like:** You `kubectl edit pod kube-apiserver-<node>` in the cluster, the edit appears to succeed, but moments later the pod reverts or restarts with your change gone.
**Why it happens:** What you're editing through the API server is a **mirror pod** — a read-mostly reflection of the real source of truth, the manifest file the kubelet watches on disk. Editing the mirror doesn't persist.
**Habit:** For any static pod (`kube-apiserver`, `kube-scheduler`, `kube-controller-manager`, `etcd`), always edit the file directly in `/etc/kubernetes/manifests/` and let the kubelet pick up the change — never `kubectl edit` a static pod expecting it to stick.

### 10. Confusing cert renewal with cert expiration checking, or forgetting to restart after renewing
**What it looks like:** You run `kubeadm certs check-expiration` and treat it as if it renewed something, or you run `kubeadm certs renew all` and don't restart the control-plane static pods that need the new certs picked up.
**Why it happens:** The two subcommands sound similar and are used in sequence in real workflows, so it's easy to mentally merge "checked" with "fixed."
**Habit:** Remember they're a pair, not one action: `check-expiration` (read-only, diagnostic) then `renew <cert>`/`renew all` (mutating) — and after renewing, restart the affected static pods (moving the manifest out and back, or `crictl rm` on the container, forces the kubelet to recreate it).

### 11. Touching control-plane files without backing up `admin.conf`/certs first
**What it looks like:** Mid-edit on `/etc/kubernetes/`, you lose `kubectl` access entirely and have no working credential to diagnose your own outage with.
**Why it happens:** Under time pressure, backing up a config file before editing it feels like a wasted 10 seconds — until it's the 10 seconds that would have saved the task.
**Habit:** Before editing anything under `/etc/kubernetes/`, `cp` it to a `.bak` suffix in the same command sequence — it costs nothing and gives you an instant rollback.

---

## C. Troubleshooting workflow (largest single domain, 30%)

### 12. Not verifying after every change
**What it looks like:** You apply a fix, assume it worked because the command didn't error, and move to the next task — then a later task's grading depends on a state you never actually confirmed.
**Why it happens:** Under a 6–7-minute-per-task budget, verification feels like the part you can skip to save time; it's actually the part that prevents wasted time later when you have to debug your own unverified fix.
**Habit:** End every task with a status check appropriate to what you changed — `kubectl get/describe`, `kubectl rollout status`, or `kubectl logs` — before moving on, every single time, no exceptions for "obvious" fixes.

### 13. Watching a hanging or slow command instead of working elsewhere
**What it looks like:** A `kubectl drain` or `rollout status` is taking a while, and you just sit there watching the terminal instead of doing anything else.
**Why it happens:** It feels like the command needs your attention to "finish," and switching context feels risky when you're not sure how long it'll take.
**Habit:** The moment a command looks like it'll run more than a few seconds, open a second terminal tab and start the next task — come back and check the first one when it's convenient, not when it's the only thing you're doing.

### 14. Misreading task wording (exact name, namespace, label, or count)
**What it looks like:** You build a technically-correct resource, but the required name is `web-prod-01` and you typed `web-prod-1`, or the task asked for 3 replicas and you left the default of 1.
**Why it happens:** Performance-based exam tasks are graded on exact string/field matches in many cases; skimming a task the way you'd skim a Slack message misses the specific literal values that actually get checked.
**Habit:** Before running anything, re-read the task once specifically hunting for quoted names, namespaces, label key=value pairs, and numbers — treat them as the graded surface, not incidental detail.

### 15. Diagnosing out of order instead of following a consistent triage sequence
**What it looks like:** You jump straight to `journalctl -u kubelet` on a hunch before checking whether the pod even scheduled, and burn several minutes down the wrong path.
**Why it happens:** Under time pressure it's tempting to guess at the "interesting" cause rather than working outward systematically, especially for someone whose instincts are tuned to app-level (CKAD) debugging rather than cluster-level diagnosis.
**Habit:** Default triage order for anything broken: `kubectl get pods -o wide` / `kubectl get events --sort-by=.metadata.creationTimestamp` → `kubectl describe` the affected object → `kubectl logs` (and `--previous` if it crashed) → only then drop to `crictl`/`journalctl` on the node itself.

### 16. Modifying or deleting the wrong resource entirely
**What it looks like:** Two similarly-named Deployments exist across two namespaces (or a Pod vs. its owning Deployment), and you edit/delete the one that isn't actually broken.
**Why it happens:** Under time pressure, `kubectl get pods` output across namespaces or similar naming conventions (`web`, `web-canary`, `web-v2`) is easy to conflate, and `kubectl delete` gives no "are you sure" prompt.
**Habit:** Before any `delete`, `edit`, or `patch`, run the matching `get -o wide` (or `get -n <ns>`) immediately beforehand in the same terminal so the exact name/namespace you're about to act on is the last thing on screen.

---

## D. Workloads & Scheduling (15%, but this is where rusty exact-syntax mistakes concentrate)

### 17. Hand-writing YAML from scratch
**What it looks like:** You start typing a Deployment manifest line-by-line from memory, including indentation, instead of generating a skeleton.
**Why it happens:** It feels faster when you "know" the shape, but every manually-typed field is a chance for a typo or a forgotten required field the generator would have supplied automatically.
**Habit:** Generate first, edit second — `kubectl create deployment ... $do > file.yaml` or `kubectl run ... $do > file.yaml`, then open the file and change only what the task requires.

### 18. Bad YAML indentation silently breaking a manifest
**What it looks like:** A container spec that looks right at a glance is actually nested one level off — `env` sitting as a sibling of `containers` instead of inside a container, or vice versa — and `kubectl apply` either errors cryptically or applies something that isn't what you intended.
**Why it happens:** YAML has no braces to visually anchor nesting, and a quick copy-paste edit under time pressure easily shifts indentation by a couple of spaces without you noticing.
**Habit:** After every manual edit, run `kubectl apply -f file.yaml --dry-run=server` (or at minimum `--dry-run=client`) before the real apply, and glance at `kubectl explain <resource>.spec.<field>` if a nesting level feels uncertain.

### 19. Wrong `apiVersion` for a resource
**What it looks like:** You write `apiVersion: extensions/v1beta1` for an Ingress, or `policy/v1beta1` for a PodDisruptionBudget, from muscle memory built on an older cluster, and it's rejected on a current version.
**Why it happens:** `apiVersion` values genuinely changed across Kubernetes releases (Ingress moved to `networking.k8s.io/v1`, PDB to `policy/v1`, etc.), and old tutorials/memory don't update themselves.
**Habit:** Never write `apiVersion` from memory for anything you're not 100% sure of — generate the resource via `--dry-run=client -o yaml` or check `kubectl explain <kind>` (its `VERSION:` line is authoritative for the cluster you're actually on) instead of typing what you remember.

### 20. Mixing up `nodeSelectorTerms` OR-semantics with `matchExpressions` AND-semantics
**What it looks like:** You add a second `nodeSelectorTerms` entry expecting it to narrow the match (like adding another `AND` condition), but it actually broadens it, since multiple `nodeSelectorTerms` are OR'd together — only the `matchExpressions` *within* a single term are AND'd.
**Why it happens:** The nesting looks similar to a flat list of conditions, and the OR-vs-AND split isn't visually obvious from the YAML shape alone.
**Habit:** Say the rule explicitly before writing affinity YAML: "terms are OR'd, expressions inside one term are AND'd" — if you need an AND across multiple conditions, they must live in the same `matchExpressions` list, not separate terms.

### 21. Toleration that doesn't actually match the taint
**What it looks like:** A pod stays `Pending` even after you add a toleration, because the `effect` was left off (defaults to matching all effects only when omitted correctly) or the `operator`/`value` doesn't exactly match the taint's key/value.
**Why it happens:** Toleration matching is exact-match by default (`Equal` operator requires the value to match precisely), and it's easy to assume "close enough" tolerations will work the way loose label selectors sometimes do.
**Habit:** Copy the taint's exact `key`, `value`, and `effect` from `kubectl describe node` directly into the toleration rather than retyping them from memory, and double check whether the taint uses `NoSchedule` vs `NoExecute` (the latter also needs `tolerationSeconds` if you want eviction delay).

---

## E. Services & Networking (20%)

### 22. Service selector doesn't match Pod labels
**What it looks like:** The Service exists, looks correctly configured, but `kubectl get endpoints`/`endpointslices` shows nothing — traffic has nowhere to go.
**Why it happens:** Service `spec.selector` and Pod `metadata.labels` are independently editable, and a small mismatch (a missing label, a typo, a leftover `version: v1` from a template) breaks the link silently — no error is raised anywhere.
**Habit:** After creating or editing any Service, immediately run `kubectl get endpoints <svc>` (or `endpointslices`) and confirm it lists Pod IPs — an empty result means selector/label mismatch, every time.

### 23. `targetPort` doesn't match the port the container actually listens on
**What it looks like:** The Service and Endpoints both look correct, but requests time out or connection-refuse, because `targetPort` points at a port the application isn't bound to.
**Why it happens:** `port` (the Service's own port) and `targetPort` (the container's port) are easy to conflate, especially when copying a Service spec across apps that listen on different ports (80 vs. 8080 vs. 3000).
**Habit:** Check the actual listening port in the container image/Deployment spec (`containerPort`, or `kubectl exec ... -- netstat`/`ss` if unsure) before setting `targetPort` — don't assume it matches the Service's `port`.

### 24. Declaring NetworkPolicy rules without the matching `policyTypes` entry
**What it looks like:** You write `egress:` rules into a NetworkPolicy, but traffic still isn't restricted the way you expect, because `policyTypes` only lists `Ingress`.
**Why it happens:** `policyTypes` is a separate, easy-to-forget field — Kubernetes doesn't infer it from which of `ingress`/`egress` blocks you populated, so a policy with only an `egress` block but `policyTypes: [Ingress]` silently does nothing on the egress side.
**Habit:** Every time you add an `ingress:` or `egress:` block to a NetworkPolicy, immediately check that the matching value is present in `policyTypes` — treat it as a two-part edit, never one without the other.

### 25. Applying a NetworkPolicy in the wrong namespace
**What it looks like:** The policy looks perfect, but nothing changes, because NetworkPolicy is namespace-scoped and it landed in `default` while the affected pods live in `app-ns`.
**Why it happens:** It's easy to forget a resource is namespace-scoped when you're focused on getting the `podSelector`/rules right, especially coming from a CKAD background where NetworkPolicy is used less often than RBAC/Services.
**Habit:** Set `-n <namespace>` explicitly on the `kubectl apply`/`create` command for any NetworkPolicy, and confirm with `kubectl get networkpolicy -n <namespace>` rather than a namespace-less `get` that might be scanning the wrong default.

---

## F. RBAC & Security

### 26. `kubectl auth can-i` without `-n`
**What it looks like:** You test permissions with `kubectl auth can-i create pods --as=system:serviceaccount:app-ns:sa-name` and get a `no` that seems to contradict the RoleBinding you just created — because the check ran against `default`, not `app-ns`.
**Why it happens:** `auth can-i` respects the same namespace-defaulting behavior as any other `kubectl` command, and it's easy to think of it as a global permission check rather than a namespace-scoped one.
**Habit:** Always pass `-n <namespace>` explicitly to `kubectl auth can-i` when testing a namespaced permission — treat a `no` result as inconclusive until you've confirmed the namespace matches the RoleBinding's.

### 27. Trying to edit immutable fields in place
**What it looks like:** `kubectl edit rolebinding ...` to change `roleRef`, or `kubectl edit pvc ...` to change `accessModes`/`storageClassName`, and the API server rejects the edit (or silently ignores it depending on the field).
**Why it happens:** Most Kubernetes fields are mutable via `edit`/`patch`, so it's a reasonable but wrong default assumption that all of them are — `roleRef` on Role/ClusterRoleBindings and several PVC spec fields are explicit exceptions.
**Habit:** For RoleBindings/ClusterRoleBindings, delete and recreate rather than trying to edit `roleRef`; for PVCs, treat `accessModes`, `storageClassName`, `volumeMode`, and `selector` as fixed at creation time and plan the correct values up front.

---

## G. Storage (smallest domain at 10%, but a fast, cheap win when done right)

### 28. Pending PVC from a mismatch on any of four independent fields
**What it looks like:** A PVC sits `Pending` indefinitely against a PV that looks like an obvious match, because one of four independent binding criteria — `storageClassName`, `accessModes`, `volumeMode`, or requested capacity — doesn't line up.
**Why it happens:** It's easy to check one or two of the four (usually class and size) and assume that's sufficient, since any single mismatch produces the identical symptom: a silently `Pending` claim with no obvious error.
**Habit:** When a PVC won't bind, check all four fields side-by-side against every candidate PV in one pass (`kubectl get pv,pvc -o wide` plus `describe` on both) rather than fixing the first mismatch you spot and assuming that was the only one.

---

## H. Time & process management

### 29. Spending too long on one task instead of flagging and returning
**What it looks like:** You're 12 minutes into a task budgeted for 6–7, still convinced you're "almost there," while 3 easier tasks elsewhere sit untouched.
**Why it happens:** Sunk-cost thinking is strong under exam pressure — the more time already spent, the harder it feels to walk away, even though the marginal minute is worth more on an untouched task.
**Habit:** Set a personal hard cap (5 minutes is a commonly cited threshold) — when you hit it without a clear path to done, mark the task number on scratch paper/notes and move on; sweep back only after all other tasks are attempted.

### 30. Trying to look up Kustomize documentation mid-exam
**What it looks like:** You hit a `kubectl apply -k` task, aren't sure of the overlay/patch syntax, and instinctively try to search for `kustomize.io` — which isn't on the exam's allowed-documentation list at all (unlike Helm and Gateway API, which do have allowed domains).
**Why it happens:** Helm and Gateway API both have an explicit allowed doc domain, so it's a reasonable but wrong assumption that Kustomize does too — there's no equivalent for it.
**Habit:** Treat `kubectl kustomize`/`kubectl apply -k` (bases, overlays, `kustomization.yaml` structure, common patch strategies) as something to have cold before exam day, not something to plan on looking up — kubernetes.io's own docs are the only fallback, and even those don't cover Kustomize as deeply as kustomize.io would.

---

## Quick-reference: the one-line habits, all in one place

1. Single monitor, no VM — verify on the exact exam-day machine the night before.
2. Set `alias k=kubectl` and `export do="--dry-run=client -o yaml"` before task 1.
3. Check `kubectl config current-context` before every task.
4. Pass `-n <namespace>` explicitly; never trust the default.
5. `etcdctl` saves, `etcdutl` restores.
6. Restore etcd to a new `--data-dir`, then update the static pod manifest to match.
7. First control-plane node = `kubeadm upgrade apply`; every other node = `kubeadm upgrade node`.
8. Cordon and uncordon are one unit of work — verify `Ready` before calling it done.
9. Edit static pod manifests on disk, never via `kubectl edit`.
10. `check-expiration` is read-only; `renew` mutates and needs a static pod restart after.
11. `cp` any `/etc/kubernetes/` file before editing it.
12. Verify every change with `get`/`describe`/`rollout status` before moving on.
13. Open a second terminal instead of watching a slow command.
14. Re-read task text once specifically for names/namespaces/labels/numbers.
15. Triage order: events/pods → describe → logs (`--previous`) → node-level (`crictl`/`journalctl`).
16. `get` the exact target immediately before any `delete`/`edit`/`patch`.
17. Generate YAML via `--dry-run=client -o yaml`, then edit — never hand-write from scratch.
18. `--dry-run=server` (or at least client) after any manual YAML edit.
19. Never type `apiVersion` from memory — generate it or check `kubectl explain`.
20. Node affinity: terms are OR'd, expressions within one term are AND'd.
21. Copy taint key/value/effect verbatim from `describe node` into the toleration.
22. Empty `kubectl get endpoints` after a Service change means selector/label mismatch — check first.
23. Confirm the container's actual listening port before setting `targetPort`.
24. Every `ingress:`/`egress:` block needs its type listed in `policyTypes`, or it's a no-op.
25. NetworkPolicy is namespace-scoped — set `-n` and verify with a namespaced `get`.
26. Always pass `-n` to `kubectl auth can-i` for namespaced permission checks.
27. Delete and recreate RoleBindings/PVCs for immutable fields; don't try to edit them in place.
28. Check all four PVC-binding fields (class, access mode, volume mode, size) in one pass, not one at a time.
29. Hard-cap time per stuck task (e.g., 5 minutes), flag it, and come back later.
30. Know `kubectl apply -k` cold — there's no allowed Kustomize doc domain to fall back on.
