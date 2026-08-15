# CKA Accelerated Study Plans — 7-Day / 14-Day / 21-Day

*Built directly from the material that already exists in this repo: `01-exam-snapshot-and-priorities.md` (priority matrix), `02-topics/*.md` (concept references), `03-cheatsheets/*.md`, `04-question-bank/*.md` (237 original questions/drills/scenarios across 8 files), and `05-mock-exams/*.md` (3 full 100-point, 120-minute mocks). No plan below tells you to "study networking" — every day points at specific files and specific question numbers that exist right now in this repo. All three plans assume the P0 skew documented in the priority matrix: Troubleshooting (30%) and Cluster Architecture/kubeadm/etcd/certs (25%) get the majority of reps; Storage (10%) and the CKAD-overlap parts of Workloads (Deployments, Jobs, DaemonSets) get the least.*

**Non-negotiable, per `01-exam-snapshot-and-priorities.md`:** run all hands-on labs and troubleshooting drills on real multi-node kubeadm VMs, not kind/minikube — several drills (static pod manifests, `crictl`, `journalctl -u kubelet`, `/var/lib/kubelet/kubeadm-flags.env`, cgroup driver mismatches) depend on systemd/CRI-level access that kind/minikube abstract away. Set exam-realistic aliases every session: `alias k=kubectl` and `export do="--dry-run=client -o yaml"`.

---

## How to read these plans

Each day lists six blocks. "Mock Exam / timed practice" only appears on the days it's actually scheduled — not padded onto every day. Every reference like "Q1–7" or "Scenario 3–6" points at a real, numbered item in the named file. Time budgets assume evenings/weekend-hours for a full-time employee, not a full study day, except where explicitly marked as a weekend block.

---

# 7-Day Plan — Intensive Refresher

*For someone who needs a compressed, high-intensity pass: 2.5–3.5 hrs on weekdays, 5–6 hrs across the weekend day(s) that fall inside the window. Assumes you can front-load two weekend days near the start or end. This plan has no slack — if you're regularly running over, you're the target audience for the 14-day plan instead.*

### Day 1 (weekend day, ~5 hrs) — Cluster Architecture foundation
- **Knowledge Refresh (45 min):** Read `01-exam-snapshot-and-priorities.md` in full (Executive Summary through Priority Matrix) — this is your syllabus for the week. Then skim `02-topics/cluster-architecture-kubeadm-etcd.md` for kubeadm init/join, static pod mechanics, and the `etcdctl`-backs-up/`etcdutl`-restores split.
- **Command Drills (30 min):** `04-question-bank/06-micro-drills.md` — all 16 "30-Second Drills" and all 16 "1-Minute Drills." Time yourself against the stated limits.
- **Hands-on Labs (2 hrs):** `04-question-bank/01-cluster-architecture-maintenance.md` Q1–12 (kubeadm join token regeneration, pod-CIDR init, static pod restart/diagnosis, cert expiration checks, full etcd backup/restore cycle Q11, restore-with-apiserver-down Q12). Attempt cold, then check solutions.
- **Troubleshooting (1 hr):** `04-question-bank/01-cluster-architecture-maintenance.md` Q3, Q6, Q7 (NotReady-after-join, static pod crash-loop, apiserver fully down with no kubectl) — these three are the P0 diagnostic backbone of the whole domain.
- **Mock Exam:** none today.
- **Review (15 min):** Re-read the "Common mistake" callout on every question you got wrong or were slow on. Write down (paper or a scratch file) the etcdctl-vs-etcdutl rule and the "edit the manifest file, not the mirror pod" rule — these two recur constantly.

### Day 2 (weekday, ~3 hrs) — Cluster Architecture completion + upgrades
- **Knowledge Refresh (20 min):** Re-skim the kubeadm upgrade sequencing section of `02-topics/cluster-architecture-kubeadm-etcd.md` (drain → upgrade kubeadm → `upgrade apply`/`upgrade node` → upgrade kubelet/kubectl → uncordon, one minor version at a time).
- **Command Drills (20 min):** `06-micro-drills.md` "3-Minute Drills" #1–6 (drain/uncordon, kubeadm package upgrade, etcd snapshot with explicit flags, snapshot status check, ClusterRole+group binding).
- **Hands-on Labs (1.5 hrs):** `01-cluster-architecture-maintenance.md` Q13–19 (drain with DaemonSets, drain blocked by PDB, drain with emptyDir data, single control-plane upgrade Q18, second-control-plane-in-HA upgrade Q19). Q18 and Q19 are Hard/15–18 min each — budget accordingly.
- **Troubleshooting (30 min):** `01-cluster-architecture-maintenance.md` Q20–24 (kubelet won't rejoin after package upgrade, CSR approval, RBAC ServiceAccount for node-ops, clock-skew TLS failures, lost admin.conf recovery).
- **Mock Exam:** none today.
- **Review (10 min):** Confirm you can state from memory, without looking: the difference between `kubeadm upgrade apply` (first control-plane node only) and `kubeadm upgrade node` (every other node) — Q18/Q19's shared "Common mistake."

### Day 3 (weekday, ~3 hrs) — Workloads & Scheduling (the CKA-flavored half)
- **Knowledge Refresh (20 min):** Skim `02-topics/scheduling.md` for taints/tolerations, node/pod affinity syntax (`nodeSelectorTerms` AND/OR semantics), and PriorityClass preemption — this is the least-CKAD-overlap part of the domain per the priority matrix.
- **Command Drills (15 min):** `06-micro-drills.md` "1-Minute Drills" #11 (PriorityClass) and #14 (HPA), "2-Minute Drills" #12 (nodeSelector patch), "3-Minute Drills" #12 (anti-affinity patch).
- **Hands-on Labs (1.5 hrs):** `04-question-bank/02-workloads-scheduling.md` Q7–14 (nodeSelector, required+preferred node affinity, the broken-OR `nodeSelectorTerms` trap in Q9, pod anti-affinity for HA spread, pod affinity co-location, exact-match tolerations, `NoExecute` + `tolerationSeconds` in Q13, PriorityClass preemption Q14). This block is dense — don't rush Q9 and Q13, they're the two most commonly-missed concepts.
- **Troubleshooting (45 min):** `04-question-bank/02-workloads-scheduling.md` Q1–5 (untolerated taint, oversized resource requests, stacked cordoned-node + selector mismatch, liveness-probe-induced CrashLoopBackOff, Pending-vs-OOMKilled side-by-side).
- **Mock Exam:** none today.
- **Review (10 min):** Re-read Q9's explanation until the AND/OR rule for `nodeSelectorTerms` vs `matchExpressions` is automatic — this is called out in official docs as the single most common node-affinity mistake.

### Day 4 (weekday, ~3 hrs) — Services & Networking + DNS
- **Knowledge Refresh (20 min):** Skim `02-topics/networking.md` for Service/Endpoints/EndpointSlice mechanics and the NetworkPolicy `policyTypes` gotcha (declaring `ingress:`/`egress:` rules without the matching entry in `policyTypes` does nothing).
- **Command Drills (15 min):** `06-micro-drills.md` "2-Minute Drills" #13 (default-deny NetworkPolicy), "3-Minute Drills" #13 (namespace-scoped egress allow).
- **Hands-on Labs (1.5 hrs):** `04-question-bank/03-networking.md` Q1–7 (ClusterIP expose, pinned NodePort, ExternalName, silent empty-Endpoints selector mismatch, the `targetPort`-vs-actual-listening-port trap in Q5, EndpointSlice readiness diagnosis, hand-authored EndpointSlice for an external backend).
- **Troubleshooting (1 hr):** `04-question-bank/03-networking.md` Q8–12, the DNS block that the priority matrix explicitly elevates to P0 (baseline DNS sanity check, CoreDNS scaled to zero, broken `kube-dns` Service selector, Corefile syntax crash, NetworkPolicy silently blocking DNS in one namespace). This 5-question run is the highest-value 60 minutes in the whole networking domain.
- **Mock Exam:** none today.
- **Review (10 min):** Memorize the DNS troubleshooting order: check CoreDNS pods → check `kube-dns` Service endpoints → check Corefile/logs → check NetworkPolicy in the *affected namespace* — in that order, per Q8–Q12 and reinforced in `07-troubleshooting-scenarios-workload-network-storage.md` Scenario 10.

### Day 5 (weekend day, ~5.5 hrs) — Storage, RBAC, NetworkPolicy/Ingress depth, and cross-domain scenarios
- **Knowledge Refresh (20 min):** Skim `02-topics/storage.md` for the four independent PVC-binding criteria (class, access mode, volume mode, size) and `02-topics/rbac.md` for Role vs ClusterRole scope-vs-binding-kind rules.
- **Command Drills (15 min):** `06-micro-drills.md` "30-Second Drills" #11–12 (Pending PVCs, ClusterRoleBindings referencing `cluster-admin`), "1-Minute Drills" #8–9 (Role creation, ClusterRole-bound-via-RoleBinding).
- **Hands-on Labs (2.5 hrs):**
  - `04-question-bank/04-storage-rbac.md` Part A Q1–11 (static PV, PVC-to-specific-PV binding via `spec.volumeName`, RWX-on-hostPath access-mode mismatch, default StorageClass conflicts, `WaitForFirstConsumer` immutability trap, `Retain` reclaim lifecycle, three distinct Pending-PVC root causes in Q8/Q9/Q11 — nonexistent class, access-mode decoy, volumeMode decoy).
  - `04-question-bank/04-storage-rbac.md` Part B Q12–24 (ServiceAccount+token, Role+RoleBinding, the `can-i` no-namespace-flag trap in Q14, subresource permissions for `pods/log`, `roleRef` immutability, cluster-scoped-resource ClusterRole, reusing a built-in ClusterRole at namespace scope via RoleBinding, group bindings with no Group object, impersonation rights and the two-layer impersonation check in Q20/Q21, and the two RBAC "Forbidden" diagnosis traps in Q22/Q23 — missing verb vs. wrong-namespace subject).
- **Troubleshooting (1.5 hrs):** `04-question-bank/03-networking.md` Q13–20 (default-deny ingress, scoped allow layered on default-deny, the missing-`policyTypes` "does nothing" bug, three-tier segmentation with DNS carve-out, AND-vs-OR in policy peers, imperative Ingress creation, `ingressClassName` typo diagnosis, `pathType`/TLS depth).
- **Mock Exam:** none today (but this is the longest single day — treat it as the day you consolidate everything before Day 6's full mock).
- **Review (15 min):** Write out from memory the four fields a Pending PVC/PV pair must agree on (`storageClassName`, `accessModes`, `volumeMode`, capacity) and the three RBAC objects that are immutable once created (`roleRef`, and on PVCs specifically: `accessModes`, `storageClassName`, `volumeMode`, `selector`).

### Day 6 (weekend day, ~4 hrs) — Full mock exam + targeted repair
- **Knowledge Refresh:** none scheduled — this day is application, not new input.
- **Command Drills (15 min warm-up):** `06-micro-drills.md` "5-Minute Drills" #1–2 (full node upgrade sequence, full etcd backup-and-restore rehearsal) as a warm-up before the timed mock.
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-1-normal.md` in full — 18 tasks, 100 points, 66-point pass bar. Do not open the Solutions section until you finish or the clock runs out.
- **Hands-on Labs / Troubleshooting (1.5 hrs, immediately after grading):** For every task you missed or were slow on, go back to the matching question-bank file and drill 2–3 adjacent questions of the same type (e.g., missed Task 12's NetworkPolicy → redo `03-networking.md` Q13–16; missed Task 8's etcd restore → redo `01-cluster-architecture-maintenance.md` Q11–12).
- **Review (15 min):** Score yourself against the 66/100 pass bar and the domain-totals table at the end of Mock 1. Identify your single weakest domain by points lost, not by task count — that domain gets extra attention on Day 7.

### Day 7 (weekday, ~3.5 hrs) — Hard-mode mock + final gap closure
- **Knowledge Refresh (15 min):** Re-read only the priority matrix rows for your weakest domain from Day 6 in `01-exam-snapshot-and-priorities.md`.
- **Command Drills (10 min):** `06-micro-drills.md` — redo any drill category where you hesitated on Day 1–2 timing.
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-3-hard-mode.md` — this is the deliberately stacked/compound-fault mock (multiple independent faults per task, tighter 6-min/task pacing). Treat a score anywhere near 66/100 here as a strong signal you're exam-ready, since it's harder than the real thing by design.
- **Troubleshooting (45 min):** Pick 4–5 scenarios from whichever of `07-troubleshooting-scenarios-workload-network-storage.md` or `08-troubleshooting-scenarios-cluster-security.md` maps to your weakest domain, and drill only those.
- **Mock Exam:** (see above — this is the day's core activity).
- **Review (20 min):** Final pass over the "Common mistake" / "Common wrong turn candidates take" callouts across every file you struggled with this week. Re-verify the exam's current Kubernetes version target on the live LF page before booking, per the snapshot file's explicit warning that v1.35 may already be stale.

---

# 14-Day Plan — Balanced Refresher

*~1.5–2.5 hrs on weeknights, ~4 hrs each weekend day. Two full mocks plus the hard-mode mock, with real spacing between first exposure and mock application.*

### Day 1 (weeknight, 2 hrs) — Orientation + kubeadm basics
- **Knowledge Refresh (30 min):** Read `01-exam-snapshot-and-priorities.md` in full. This is your map for the next two weeks — note which domains are P0 for you specifically (you're CKAD-certified, so Troubleshooting's DNS/log-reading half and Workloads' Deployment/Job basics are already yours).
- **Command Drills (20 min):** `04-question-bank/06-micro-drills.md` "30-Second Drills" #1–16.
- **Hands-on Labs (1 hr):** `04-question-bank/01-cluster-architecture-maintenance.md` Q1–5 (join-command regeneration, pod-CIDR init, NotReady-after-join diagnosis, reading a static pod flag via `kubectl -o yaml`, restarting a static pod via manifest move).
- **Troubleshooting:** none scheduled — Day 2 covers it.
- **Mock Exam:** none today.
- **Review (10 min):** Confirm you can explain, unprompted, why `kubectl edit` against a static pod's mirror object silently does nothing (Q5's "Common mistake").

### Day 2 (weeknight, 1.5 hrs) — Static pods & certs
- **Knowledge Refresh (15 min):** `02-topics/cluster-architecture-kubeadm-etcd.md` — cert file layout under `/etc/kubernetes/pki/`, `kubeadm certs check-expiration` vs `openssl x509 -noout -dates`.
- **Command Drills (10 min):** `06-micro-drills.md` "2-Minute Drills" #5–8 (apiserver cert expiry, etcd-server cert renewal, pull scheduler out of rotation, etcd endpoint health).
- **Hands-on Labs (1 hr):** `01-cluster-architecture-maintenance.md` Q6–10 (broken static pod manifest with kubectl available, fully broken apiserver with kubectl unavailable, cert expiration report, renew-all-and-force-reload, renew-one-named-cert-and-prove-it).
- **Troubleshooting (15 min, if time allows — otherwise roll into Day 3):** Skim Q6/Q7's "Common mistake" callouts again out loud.
- **Mock Exam:** none.
- **Review:** none separate — folded into the drill above.

### Day 3 (weeknight, 2 hrs) — etcd backup/restore mastery
- **Knowledge Refresh (15 min):** Re-read the `01-exam-snapshot-and-priorities.md` callout on `etcdctl` (backup) vs `etcdutl` (restore) being a genuine tool-boundary split, not a naming quirk.
- **Command Drills (15 min):** `06-micro-drills.md` "1-Minute Drills" #7, "3-Minute Drills" #4–5, "5-Minute Drills" #2.
- **Hands-on Labs (1 hr):** `01-cluster-architecture-maintenance.md` Q11–14 (full backup/restore cycle, restore with apiserver already down, snapshot integrity verification, backup against a remote/dedicated etcd node).
- **Troubleshooting (25 min):** `04-question-bank/05-troubleshooting.md` Q10–12 (etcd NOSPACE alarm blocking writes, the `etcdctl`-restore-is-removed trap, full disaster-recovery drill with a marker ConfigMap).
- **Mock Exam:** none.
- **Review (5 min):** Say out loud, from memory, the four etcd flags (`--endpoints`, `--cacert`, `--cert`, `--key`) and why `etcdutl snapshot restore` never takes them.

### Day 4 (weeknight, 1.5 hrs) — Node lifecycle & upgrades
- **Knowledge Refresh (15 min):** kubeadm upgrade sequencing in `02-topics/cluster-architecture-kubeadm-etcd.md`.
- **Command Drills (10 min):** `06-micro-drills.md` "3-Minute Drills" #1–3, "5-Minute Drills" #1.
- **Hands-on Labs (55 min):** `01-cluster-architecture-maintenance.md` Q15–17 (drain with DaemonSets, drain blocked by a PDB — scale up rather than delete the PDB, drain with unmanaged emptyDir pods).
- **Troubleshooting:** none new — revisit any Day 1–3 item you missed.
- **Mock Exam:** none.
- **Review (10 min):** Confirm the PDB rule: never lower `minAvailable`/delete the PDB to force a drain through — scale the workload up instead.

### Day 5 (weeknight, 2 hrs) — Upgrades in HA + RBAC intro
- **Knowledge Refresh (15 min):** `02-topics/rbac.md` — Role/ClusterRole vs RoleBinding/ClusterRoleBinding scope rules.
- **Command Drills (15 min):** `06-micro-drills.md` "1-Minute Drills" #8–9, "3-Minute Drills" #6.
- **Hands-on Labs (1 hr):** `01-cluster-architecture-maintenance.md` Q18–19 (single-node full upgrade, second-control-plane-in-HA upgrade — memorize `upgrade apply` vs `upgrade node`).
- **Troubleshooting (25 min):** `01-cluster-architecture-maintenance.md` Q20–21 (kubelet won't rejoin after package upgrade — the `daemon-reload` trap; CSR approval and when *not* to blindly approve).
- **Mock Exam:** none.
- **Review (5 min):** Restate the rule: `kubeadm upgrade apply` runs exactly once, on the first control-plane node only; every other node (including other control-plane nodes) uses `kubeadm upgrade node`.

### Day 6 (weekend day, 4 hrs) — RBAC deep dive + Storage
- **Knowledge Refresh (20 min):** `02-topics/storage.md` — the four independent PVC/PV binding criteria; `02-topics/rbac.md` — impersonation and subresource permission rules.
- **Command Drills (15 min):** `06-micro-drills.md` "30-Second Drills" #11–12, "1-Minute Drills" #8–9.
- **Hands-on Labs (2.5 hrs):**
  - `04-question-bank/04-storage-rbac.md` Part A Q1–11 in full (static PV/PVC lifecycle, access-mode/volumeMode/class mismatches, `WaitForFirstConsumer`, `Retain` reclaim lifecycle, resize-in-place needing `allowVolumeExpansion`).
  - `04-question-bank/04-storage-rbac.md` Part B Q12–19 (ServiceAccount+token, Role+RoleBinding, `can-i` namespace-flag trap, `pods/log` subresource, `roleRef` immutability, cluster-scoped ClusterRole+non-resource URL, reusing `view` at namespace scope, group binding with no Group object).
- **Troubleshooting (45 min):** `04-question-bank/04-storage-rbac.md` Q20–24 (impersonation rights, the two-layer impersonation check, and the two "Forbidden" diagnosis traps — missing verb vs. wrong-namespace subject, plus cross-namespace Role/RoleBinding rules).
- **Mock Exam:** none.
- **Review (10 min):** Write down the rule from Q24: a RoleBinding's *subject* may reference a ServiceAccount in a different namespace, but its *Role* (`roleRef`) must live in the same namespace as the RoleBinding itself.

### Day 7 (weekend day, 4 hrs) — Networking + DNS (P0 slice)
- **Knowledge Refresh (20 min):** `02-topics/networking.md` — Service/Endpoints/EndpointSlice chain, NetworkPolicy `policyTypes` semantics.
- **Command Drills (15 min):** `06-micro-drills.md` "2-Minute Drills" #13, "3-Minute Drills" #13.
- **Hands-on Labs (2 hrs):** `04-question-bank/03-networking.md` Q1–7 (ClusterIP, pinned NodePort, ExternalName, selector-mismatch silent failure, targetPort-vs-real-listening-port, EndpointSlice readiness diagnosis, hand-authored EndpointSlice).
- **Troubleshooting (1 hr):** `04-question-bank/03-networking.md` Q8–12 — the full P0 DNS troubleshooting chain (baseline sanity check, CoreDNS scaled to zero, broken `kube-dns` selector, Corefile crash, NetworkPolicy blocking DNS in one namespace).
- **Mock Exam:** none.
- **Review (10 min):** Recite the DNS diagnostic order (CoreDNS pods → `kube-dns` Service endpoints → Corefile/logs → namespace NetworkPolicy) without looking.

### Day 8 (weeknight, 2 hrs) — NetworkPolicy depth + Ingress
- **Knowledge Refresh (15 min):** Re-read the AND-vs-OR `nodeSelectorTerms`/policy-peer distinction (it recurs in both scheduling and networking).
- **Command Drills (10 min):** `06-micro-drills.md` "2-Minute Drills" #14 (Gateway API HTTPRoute listing).
- **Hands-on Labs (1 hr):** `03-networking.md` Q13–17 (default-deny ingress, scoped allow layered on it, the missing-`policyTypes` bug, three-tier segmentation with DNS carve-out, AND-vs-OR in policy peers).
- **Troubleshooting (30 min):** `03-networking.md` Q18–20 (imperative Ingress creation, `ingressClassName` typo diagnosis, `pathType`/TLS depth).
- **Mock Exam:** none.
- **Review (5 min):** State the single most common NetworkPolicy authoring bug (Q15): writing `ingress:`/`egress:` rules without the matching entry in `policyTypes` — the rules are parsed but never enforced.

### Day 9 (weeknight, 2 hrs) — Workloads & Scheduling
- **Knowledge Refresh (15 min):** `02-topics/scheduling.md` — taints/tolerations effects (`NoSchedule`/`NoExecute`/`PreferNoSchedule`), `tolerationSeconds` semantics.
- **Command Drills (10 min):** `06-micro-drills.md` "1-Minute Drills" #11, #14; "3-Minute Drills" #12.
- **Hands-on Labs (1 hr):** `04-question-bank/02-workloads-scheduling.md` Q6–14 (Guaranteed QoS, nodeSelector, required+preferred affinity, the broken-OR nodeSelectorTerms trap, pod anti-affinity HA spread, pod affinity co-location, exact-match tolerations, `NoExecute`+`tolerationSeconds`, PriorityClass preemption).
- **Troubleshooting (25 min):** `02-workloads-scheduling.md` Q1–5 (untolerated taint, oversized requests, stacked cordon+selector-mismatch, liveness-probe CrashLoopBackOff, Pending-vs-OOMKilled).
- **Mock Exam:** none.
- **Review (10 min):** Restate Q13's rule: `tolerationSeconds` delays *eviction after* a `NoExecute` taint is applied — it does not delay when the toleration "starts working."

### Day 10 (weekend day, 4.5 hrs) — Mock Exam 1 (normal difficulty)
- **Knowledge Refresh:** none — application day.
- **Command Drills (15 min warm-up):** `06-micro-drills.md` "5-Minute Drills" #5 (least-privilege ServiceAccount build) as a warm-up.
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-1-normal.md` in full, 18 tasks / 100 points / 66-point pass bar.
- **Hands-on Labs / Troubleshooting (2 hrs, post-mock repair):** For each missed/slow task, return to the matching question-bank file and redrill 3–4 adjacent questions (e.g., missed Task 6's DNS task → redo `03-networking.md` Q8–12; missed Task 17/18's Storage tasks → redo `04-storage-rbac.md` Q1–11).
- **Review (15 min):** Grade against the domain-totals table; identify your two weakest domains by points lost for the second week's focus.

### Day 11 (weeknight, 1.5 hrs) — StatefulSets, Jobs, HPA (CKA-flavored Workloads tail)
- **Knowledge Refresh (15 min):** `02-topics/workloads.md` — StatefulSet ordinal/partition rollout semantics, HPA `autoscaling/v2` behavior blocks.
- **Command Drills (10 min):** `06-micro-drills.md` "1-Minute Drills" #14 (HPA autoscale).
- **Hands-on Labs (50 min):** `04-question-bank/02-workloads-scheduling.md` Q15–20 (basic CPU-based HPA, tuning `behavior.scaleDown` to prevent flapping, the immutable-selector Deployment trap, DaemonSet+control-plane-taint toleration, StatefulSet with per-Pod PVCs, canary rollout via `partition`).
- **Troubleshooting:** none new today.
- **Mock Exam:** none.
- **Review (5 min):** Restate Q20's rule: StatefulSet rolling updates always proceed in *reverse* ordinal order (highest number first).

### Day 12 (weeknight, 1.5 hrs) — Probes, init containers, rollout mechanics
- **Knowledge Refresh (10 min):** `02-topics/workloads.md` — `startupProbe` vs `initialDelaySeconds` for slow-starting apps.
- **Command Drills (10 min):** `06-micro-drills.md` "1-Minute Drills" #16 (pause rollout).
- **Hands-on Labs (45 min):** `02-workloads-scheduling.md` Q21–25 (exact Job `completions`/`parallelism`/`completionMode`, CronJob `concurrencyPolicy: Forbid`, rollback to a *specific* revision via `--to-revision`, layering startup/readiness/liveness probes correctly, init-container-gated main container start).
- **Troubleshooting (25 min):** Pick 3 scenarios from `04-question-bank/07-troubleshooting-scenarios-workload-network-storage.md` Scenario 3–5 (readiness-probe Endpoints exclusion, ImagePullBackOff triage, taint/toleration FailedScheduling).
- **Mock Exam:** none.
- **Review:** none separate.

### Day 13 (weekend day, 4.5 hrs) — Mock Exam 2 (real-exam difficulty)
- **Knowledge Refresh:** none.
- **Command Drills (15 min warm-up):** `06-micro-drills.md` "5-Minute Drills" #7–8 (kubelet client-cert rotation, StorageClass+PVC+Pod provisioning chain).
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-2-real-difficulty.md` in full — 19 tasks across the `kubeadm-prod01`/`kubeadm-ha01`/`kubeadm-edge01`/`kubeadm-secure01` simulated contexts. This mock explicitly drills context-switching discipline; treat every context switch as a checkpoint.
- **Troubleshooting (1.5 hrs, post-mock repair):** For every missed task, cross-reference against `07-troubleshooting-scenarios-workload-network-storage.md` and `08-troubleshooting-scenarios-cluster-security.md` for a matching scenario and redrill it (e.g., missed Task 15's stacked Service bug → Scenario 1–2 in file 07; missed Task 11's controller-manager crash-loop → Scenario 5 in file 08).
- **Review (30 min):** Compare your Mock 1 vs Mock 2 domain-by-domain scores. Any domain that dropped between mocks is your Day 14 focus.

### Day 14 (weekday or weekend day, 3.5–4 hrs) — Hard-mode mock + final consolidation
- **Knowledge Refresh (15 min):** Re-read only the priority-matrix rows for your weakest domain across both mocks.
- **Command Drills (10 min):** Redo any micro-drill category where you were still over the stated time limit.
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-3-hard-mode.md` — deliberately stacked/compound-fault tasks (e.g., Task 2's dual-fault controller-manager, Task 5's two-independent-root-cause Service outage, Task 9's full disaster-recovery chain). A score near or above 66/100 here is a strong exam-readiness signal since it's intentionally harder than the real thing.
- **Troubleshooting (45 min):** Sweep back through every "Common mistake"/"Common wrong turn candidates take" callout you've hit across all three mocks and confirm you can state the fix without re-reading.
- **Mock Exam:** (core activity above).
- **Review (20 min):** Final gap check against `01-exam-snapshot-and-priorities.md`'s Priority Matrix — confirm every P0 row has at least one confident, timed rep behind it. Re-verify the live Kubernetes version on the LF exam page before booking (the snapshot file flags v1.35 vs v1.36 as an open question as of 2026-08-15).

---

# 21-Day Plan — Thorough Refresher

*~1–2 hrs on weeknights, ~3–4 hrs each weekend day. Adds a full pass over `02-topics/` and `03-cheatsheets/` as deliberate reading (not just reference-on-demand), a second lap through the harder question-bank items, and three full mocks with real recovery time between them.*

### Week 1 — Cluster Architecture, kubeadm, etcd, certs (the least-CKAD-overlap domain)

**Day 1 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** Read `01-exam-snapshot-and-priorities.md` in full — this is the syllabus for all 21 days. Read `03-cheatsheets/command-muscle-memory.md` start to finish once, not to memorize yet, just to know what's in it for later reference.
- **Command Drills:** `06-micro-drills.md` "30-Second Drills" #1–8.
- **Hands-on Labs:** `01-cluster-architecture-maintenance.md` Q1–3 (join-command regen, pod-CIDR init, NotReady-after-join).
- **Troubleshooting:** none yet.
- **Mock Exam:** none.
- **Review:** Note your 3 "P0, rusty" domains from the priority matrix for personal tracking across the 21 days.

**Day 2 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/cluster-architecture-kubeadm-etcd.md`, first half (kubeadm init/join internals, static pod mechanics).
- **Command Drills:** `06-micro-drills.md` "30-Second Drills" #9–16.
- **Hands-on Labs:** `01-cluster-architecture-maintenance.md` Q4–6 (reading apiserver flags via `-o yaml`, restarting a static pod via manifest move, diagnosing a broken static pod manifest with kubectl still up).
- **Troubleshooting:** none yet.
- **Mock Exam:** none.
- **Review:** Confirm the mirror-pod-vs-manifest-file distinction (Q5) is solid.

**Day 3 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/cluster-architecture-kubeadm-etcd.md`, second half (cert layout, `kubeadm certs` subcommands).
- **Command Drills:** `06-micro-drills.md` "1-Minute Drills" #1–8.
- **Hands-on Labs:** `01-cluster-architecture-maintenance.md` Q7–10 (fully broken apiserver with no kubectl, cert expiration report cross-checked with `openssl`, renew-all-and-force-reload, renew-one-named-cert).
- **Troubleshooting:** `01-cluster-architecture-maintenance.md` Q7 again, timed cold this time (12 min target) — this is the hardest Easy/Medium-tier diagnostic in the file and worth a second rep.
- **Mock Exam:** none.
- **Review:** Restate why renewing a cert alone is insufficient without restarting the static pod that holds the old one in memory.

**Day 4 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** Re-read the etcdctl/etcdutl split callout in `01-exam-snapshot-and-priorities.md`.
- **Command Drills:** `06-micro-drills.md` "1-Minute Drills" #9–16.
- **Hands-on Labs:** `01-cluster-architecture-maintenance.md` Q11–14 (full backup/restore cycle, restore with apiserver down, snapshot integrity check, remote-etcd-node backup).
- **Troubleshooting:** `04-question-bank/05-troubleshooting.md` Q10–11 (NOSPACE alarm, the `etcdctl`-restore-removed trap).
- **Mock Exam:** none.
- **Review:** Say the four TLS flags for `etcdctl` from memory (`--endpoints`, `--cacert`, `--cert`, `--key`) and confirm `etcdutl` takes none of them.

**Day 5 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** kubeadm upgrade sequencing, `02-topics/cluster-architecture-kubeadm-etcd.md`.
- **Command Drills:** `06-micro-drills.md` "2-Minute Drills" #1–8.
- **Hands-on Labs:** `01-cluster-architecture-maintenance.md` Q15–17 (drain with DaemonSets, PDB-blocked drain, drain with unmanaged emptyDir pods).
- **Troubleshooting:** none new.
- **Mock Exam:** none.
- **Review:** Restate the PDB rule — scale up, never delete/relax the PDB, to force a drain through.

**Day 6 (weekend day, 3.5 hrs):**
- **Knowledge Refresh (20 min):** `03-cheatsheets/docs-navigation-and-linux.md` in full — this is the file that tells you how to search the allowed kubernetes.io docs efficiently under exam time pressure; read it once now so it's reflexive later.
- **Command Drills (15 min):** `06-micro-drills.md` "2-Minute Drills" #9–16.
- **Hands-on Labs (2 hrs):** `01-cluster-architecture-maintenance.md` Q18–25 (single-node full upgrade, HA second-control-plane upgrade, kubelet-won't-rejoin-after-upgrade, CSR approval, RBAC ServiceAccount for node-ops, clock-skew TLS diagnosis, lost-admin.conf recovery, Helm-installed cluster component with a pinned version).
- **Troubleshooting (45 min):** `04-question-bank/08-troubleshooting-scenarios-cluster-security.md` Scenario 1–4 (kubelet stopped, kubelet-alive-but-CRI-unreachable, cgroup-driver mismatch, unparseable static pod manifest).
- **Mock Exam:** none.
- **Review (10 min):** You've now completed all 25 questions in `01-cluster-architecture-maintenance.md`. Re-skim every "Common mistake" line in that file once, back to back.

**Day 7 (weekend day, 3 hrs) — Week 1 checkpoint mock, cluster-architecture-only:**
- **Knowledge Refresh:** none.
- **Command Drills (15 min):** Redo any Week 1 micro-drill category you hesitated on.
- **Hands-on Labs / Troubleshooting (2 hrs):** `08-troubleshooting-scenarios-cluster-security.md` Scenario 5–14 (crash-looping controller-manager, apiserver-vanished disaster, CoreDNS forwarding loop, healthy-CoreDNS-broken-Service, RBAC verb-gap and wrong-namespace-subject Forbidden diagnoses, roleRef-typo binding, cert SAN gap after adding a load balancer, stale-client-kubeconfig-vs-real-outage).
- **Mock Exam (45 min, self-timed subset):** From `05-mock-exams/mock-exam-1-normal.md`, do only Tasks 1–10 (the Troubleshooting + Cluster Architecture tasks, 55 of the 100 points) as a Week 1 checkpoint — do not do Tasks 11–18 yet.
- **Review (15 min):** Grade Tasks 1–10 against a 36/55-point bar (66% of that subset). This is a diagnostic checkpoint, not a full mock — note weak spots for Week 3.

### Week 2 — Workloads & Scheduling, Storage, RBAC

**Day 8 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/scheduling.md`, first half (taints/tolerations, effects, `tolerationSeconds`).
- **Command Drills:** `06-micro-drills.md` "3-Minute Drills" #1–7.
- **Hands-on Labs:** `04-question-bank/02-workloads-scheduling.md` Q1–5.
- **Troubleshooting:** none yet.
- **Mock Exam:** none.
- **Review:** Restate the requests-fix-Pending / limits-fix-OOMKilled distinction from Q5.

**Day 9 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/scheduling.md`, second half (node/pod affinity, PriorityClass).
- **Command Drills:** `06-micro-drills.md` "3-Minute Drills" #8–13.
- **Hands-on Labs:** `02-workloads-scheduling.md` Q6–10 (Guaranteed QoS, nodeSelector, required+preferred affinity, the broken-OR trap in Q9, pod anti-affinity HA spread).
- **Troubleshooting:** none yet.
- **Mock Exam:** none.
- **Review:** Redo Q9 cold a second time without looking at your Day-9-first-pass notes.

**Day 10 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** none new — apply Day 9's concepts.
- **Command Drills:** `06-micro-drills.md` "5-Minute Drills" #1.
- **Hands-on Labs:** `02-workloads-scheduling.md` Q11–14 (pod affinity co-location, exact-match tolerations, `NoExecute`+`tolerationSeconds`, PriorityClass preemption).
- **Troubleshooting:** `04-question-bank/07-troubleshooting-scenarios-workload-network-storage.md` Scenario 5–6 (taint-blocked scheduling, node-affinity-to-a-nonexistent-label).
- **Mock Exam:** none.
- **Review:** Restate Q14's two traps: pin both the filler and the critical pod to the same node, and give the filler pods real resource requests (BestEffort pods can't be preempted because nothing is contended).

**Day 11 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/workloads.md` — HPA `autoscaling/v2` behavior blocks, StatefulSet ordinal/partition semantics.
- **Command Drills:** `06-micro-drills.md` "1-Minute Drills" #10–16 again as a speed check (second pass).
- **Hands-on Labs:** `02-workloads-scheduling.md` Q15–20 (CPU-based HPA, `behavior.scaleDown` tuning, immutable-selector Deployment trap, DaemonSet control-plane toleration, StatefulSet+per-Pod PVCs, canary via `partition`).
- **Troubleshooting:** none new.
- **Mock Exam:** none.
- **Review:** Restate the StatefulSet reverse-ordinal rollout order.

**Day 12 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/workloads.md` — `startupProbe` design intent vs `initialDelaySeconds` guessing.
- **Command Drills:** `06-micro-drills.md` "1-minute" and "2-minute" categories, any items still slow.
- **Hands-on Labs:** `02-workloads-scheduling.md` Q21–25 (exact Job fields, CronJob `Forbid`, rollback to a specific revision, probe layering, init-container gating).
- **Troubleshooting:** `07-troubleshooting-scenarios-workload-network-storage.md` Scenario 12–14 (dies-before-it-tries CrashLoopBackOff, OOMKilled vs generic crash, liveness-probe-vs-slow-startup).
- **Mock Exam:** none.
- **Review:** none separate.

**Day 13 (weekend day, 3.5 hrs) — Storage:**
- **Knowledge Refresh (20 min):** `02-topics/storage.md` in full.
- **Command Drills (15 min):** `06-micro-drills.md` "5-Minute Drills" #8 (StorageClass+PVC+Pod chain).
- **Hands-on Labs (2 hrs):** `04-question-bank/04-storage-rbac.md` Part A Q1–11 in full.
- **Troubleshooting (1 hr):** `04-question-bank/07-troubleshooting-scenarios-workload-network-storage.md` Scenario 7–9, 20 (missing StorageClass, accessMode-mismatch decoy, ambiguous-default-StorageClass tie-break rule, the WaitForFirstConsumer-is-not-a-bug trap).
- **Mock Exam:** none.
- **Review (10 min):** Restate the four independent PVC/PV binding criteria and which three PVC fields are immutable post-creation (`accessModes`, `storageClassName`, `volumeMode`).

**Day 14 (weekend day, 3.5 hrs) — RBAC + Week 2 checkpoint mock:**
- **Knowledge Refresh (15 min):** `02-topics/rbac.md` in full.
- **Command Drills (10 min):** `06-micro-drills.md` "1-Minute Drills" #8–9 second pass.
- **Hands-on Labs (1.5 hrs):** `04-storage-rbac.md` Part B Q12–24 in full (ServiceAccount+token through cross-namespace Role/RoleBinding rules — all 13 RBAC questions).
- **Troubleshooting (45 min):** `08-troubleshooting-scenarios-cluster-security.md` Scenario 9–11 (verb-gap Forbidden, wrong-namespace-subject Forbidden, roleRef-typo binding).
- **Mock Exam (30 min, self-timed subset):** From `05-mock-exams/mock-exam-1-normal.md`, do only Tasks 14–18 (Workloads + Storage tasks) as a Week 2 checkpoint.
- **Review (10 min):** Grade Tasks 14–18 against a 16/25-point bar (66% of that subset).

### Week 3 — Services & Networking, full mocks, final consolidation

**Day 15 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/networking.md`, first half (Service types, Endpoints/EndpointSlice chain).
- **Command Drills:** `06-micro-drills.md` "2-Minute Drills" #13, "3-Minute Drills" #13, second pass for speed.
- **Hands-on Labs:** `04-question-bank/03-networking.md` Q1–4 (ClusterIP, pinned NodePort, ExternalName, silent selector-mismatch).
- **Troubleshooting:** none yet.
- **Mock Exam:** none.
- **Review:** none separate.

**Day 16 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** `02-topics/networking.md`, second half (NetworkPolicy `policyTypes` semantics, Ingress/Gateway API basics).
- **Command Drills:** none new.
- **Hands-on Labs:** `03-networking.md` Q5–7 (targetPort-vs-real-port trap, EndpointSlice readiness diagnosis, hand-authored EndpointSlice for an external backend).
- **Troubleshooting:** `07-troubleshooting-scenarios-workload-network-storage.md` Scenario 1–3 (selector-mismatch hang, targetPort connection-refused, readiness-probe Endpoints exclusion).
- **Mock Exam:** none.
- **Review:** Restate the difference between a hang (selector/policy problem) and a connection-refused (targetPort/app problem) as diagnostic signals.

**Day 17 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** none new — apply.
- **Command Drills:** none new.
- **Hands-on Labs:** `03-networking.md` Q8–12, the full P0 DNS chain (baseline check, CoreDNS scaled to zero, broken `kube-dns` selector, Corefile crash, NetworkPolicy blocking DNS).
- **Troubleshooting:** `08-troubleshooting-scenarios-cluster-security.md` Scenario 7–8 (Corefile forwarding loop, healthy-CoreDNS-broken-Service) as a second exposure to the same failure class from a different angle.
- **Mock Exam:** none.
- **Review:** Recite the DNS diagnostic order once more, unaided.

**Day 18 (weeknight, 1.5 hrs):**
- **Knowledge Refresh:** none new.
- **Command Drills:** none new.
- **Hands-on Labs:** `03-networking.md` Q13–20 (default-deny+scoped-allow, missing-policyTypes bug, three-tier segmentation, AND-vs-OR peers, imperative Ingress, ingressClassName typo, pathType/TLS).
- **Troubleshooting:** `07-troubleshooting-scenarios-workload-network-storage.md` Scenario 10–11 (default-deny-blocks-DNS, typo'd podSelector in an allow rule).
- **Mock Exam:** none.
- **Review:** Restate the single most common NetworkPolicy bug (missing `policyTypes` entry) once more.

**Day 19 (weekend day, 4 hrs) — Gateway API + full Mock Exam 2:**
- **Knowledge Refresh (15 min):** `03-networking.md` Q21–24 read-through (Gateway API install-check, basic Gateway+HTTPRoute, cross-namespace ReferenceGrant, CNI pod-CIDR mismatch) — treat these as knowledge refresh if short on time, or as labs if you have the full window.
- **Command Drills (10 min):** full speed-check across all five `06-micro-drills.md` categories — anything still over its stated time limit gets flagged.
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-2-real-difficulty.md` in full, 19 tasks across 4 simulated contexts.
- **Troubleshooting (1 hr, post-mock repair):** For every missed task, cross-reference the matching scenario in `07-troubleshooting-scenarios-workload-network-storage.md` / `08-troubleshooting-scenarios-cluster-security.md` and redrill it.
- **Mock Exam:** (core activity above).
- **Review (20 min):** Compare against your Day 7 and Day 14 checkpoint scores — you should see clear improvement in your previously weak domains.

**Day 20 (weekend day, 3.5 hrs) — Hard-mode mock:**
- **Knowledge Refresh (15 min):** Re-read the priority-matrix rows for whichever domain scored lowest on Day 19.
- **Command Drills:** none new.
- **Mock Exam (2 hrs, strictly timed):** `05-mock-exams/mock-exam-3-hard-mode.md` in full — the deliberately stacked/compound-fault, tighter-paced mock.
- **Troubleshooting (45 min):** Pick any two full scenario sets you haven't fully cleared yet from files 07/08 and finish them.
- **Mock Exam:** (core activity above).
- **Review (20 min):** Full domain-by-domain comparison across all three mocks (Day 6/7 checkpoint, Day 14 checkpoint, Day 19 Mock 2, Day 20 Mock 3). Identify anything that regressed, not just what's still weak.

**Day 21 (weekday or short weekend session, 2–2.5 hrs) — Final consolidation:**
- **Knowledge Refresh (20 min):** Re-read `01-exam-snapshot-and-priorities.md` Executive Summary and Priority Matrix one last time, cover to cover.
- **Command Drills (20 min):** Full timed run through `06-micro-drills.md` "30-Second" and "1-Minute" categories only — these should now all be comfortably under time.
- **Hands-on Labs (30 min):** Re-run only the 3–4 hands-on labs across the whole repo that gave you the most trouble in any week (your own notes from Day 6, 7, 13, 14, 19, 20 reviews should already tell you which ones).
- **Troubleshooting (30 min):** Re-run 2–3 of the Hard-difficulty scenarios from `07-troubleshooting-scenarios-workload-network-storage.md` or `08-troubleshooting-scenarios-cluster-security.md` that you found hardest.
- **Mock Exam:** none — do not cram a fourth full mock the day before/of booking; you have none left unused in this repo, and a fresh mock this late risks manufacturing new anxiety over an unfamiliar task rather than confirming readiness.
- **Review (30 min):** Final checklist: `etcdctl` backs up / `etcdutl` restores; `kubeadm upgrade apply` (first control-plane node only) vs `kubeadm upgrade node` (everyone else); DNS diagnostic order; the four PVC/PV binding criteria; NetworkPolicy `policyTypes` must match declared rules; RoleBinding subject-namespace vs Role-namespace rules. Re-verify the live Kubernetes version on the LF exam page before your exam, per the snapshot file's open-as-of-2026-08-15 v1.35-vs-v1.36 flag.

---

# Which plan should you actually use?

**Recommendation: the 14-day plan.**

Reasoning, given your specific starting point (CKAD-certified, 11+ years cloud/platform architecture, Principal Platform Engineer, full-time job):

- **The 7-day plan is the wrong shape for a working professional**, not because the content is too hard but because it has zero slack. It front-loads two 5+ hour weekend days and still needs 3–3.5 hours on every single weeknight in between. One bad work day (an incident, a late meeting, on-call) collapses the whole schedule, and unlike a from-scratch learner you don't need the compression — you're not learning Kubernetes, you're re-learning admin-specific syntax and building muscle memory for tools (`crictl`, `etcdctl`/`etcdutl`, `journalctl -u kubelet`, static pod manifests) you don't touch daily as an architect. Compressing that into 7 days trades retention for speed you don't actually need.

- **The 21-day plan is safer but has real opportunity cost and diminishing returns for you specifically.** Its main value-adds over the 14-day plan are (a) a full deliberate read of every `02-topics/*.md` file rather than skimming them on demand, and (b) three full mocks with more recovery time between them instead of two. For someone starting from zero, that spacing matters. For someone who already has the underlying Kubernetes mental model from CKAD and 11+ years of production cloud experience, the extra week is mostly repetition of concepts you'll recognize on first exposure — the marginal knowledge gained per extra hour invested drops fast after the two-mock mark the 14-day plan already hits.

- **The 14-day plan is the right fit** because it: (1) still runs a real spaced-repetition arc — first exposure to a domain, a mock exam roughly a week later, a harder mock at the end — rather than cramming exposure and testing into the same 48 hours like the 7-day plan does; (2) fits realistically into weeknight evenings (1.5–2.5 hrs) plus two weekend days per week without requiring you to burn vacation days; (3) still gets solid coverage across every file in this repo (all five question-bank files, all five drill tiers, both scenario banks) and all three mocks, even though — unlike the 21-day plan — it doesn't drill literally every one of the 237 individual questions/drills/scenarios (most notably, most of `05-troubleshooting.md`'s 29 questions beyond Q10–12 and `03-networking.md`'s Q21–24 Gateway API section go untouched unless picked up during post-mock repair); and (4) matches what the priority matrix itself implies — you're not building new mental models, you're drilling admin-specific tool fluency (kubeadm, etcd, crictl, RBAC syntax, NetworkPolicy semantics) until it's reflexive, and 14 days of consistent, moderate-intensity repetition is enough for that kind of muscle-memory work for someone with your depth of underlying platform experience.

If your work calendar over the next two weeks looks unusually heavy (multiple on-call rotations, travel, etc.), fall back to the 21-day plan rather than the 7-day plan — extending the timeline costs you calendar time, not exam readiness; compressing it below 14 days risks the opposite.
