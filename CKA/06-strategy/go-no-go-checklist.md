# CKA Go / No-Go Readiness Checklist

*Objective, checkable gate for booking the exam. Every threshold below ties to a specific file/question
number that exists in this repo (`01-exam-snapshot-and-priorities.md`, `04-question-bank/*.md`,
`05-mock-exams/*.md`) — nothing here is a vibe check. "Do not book the exam until you can honestly
check every box below."*

**How to use this:** Run through the sections in order. Log your actual numbers (score, time, date)
in the tables — don't just tick boxes from memory. If you fail a gate, go back to the relevant
question-bank file, drill the weak spot, and re-attempt only that gate before moving on. Re-run this
whole checklist cold (no peeking at solutions first) no more than 5-7 days before your booked date,
since kubeadm/etcd muscle memory decays fast without repetition.

---

## Gate 0 — Environment and format sanity (5 minutes, do this first)

- [ ] All drills and mocks below were run on **real multi-node kubeadm VMs** (not kind/minikube) —
      per `01-exam-snapshot-and-priorities.md`, several P0 skills (static pod manifests, `crictl`,
      `journalctl -u kubelet`, `/var/lib/kubelet/kubeadm-flags.env` edits, cgroup driver mismatches)
      depend on systemd/CRI-level access that kind/minikube abstract away. If your reps were on
      kind/minikube, they don't count toward the gates below — re-run the P0 troubleshooting items on
      real VMs before booking.
- [ ] You re-checked the **live LF program page** for the current exam Kubernetes version within the
      last 1-2 weeks (was v1.35 as of 2026-08-15 per `01-exam-snapshot-and-priorities.md`, with v1.36
      already GA — this is flagged as a moving target, don't trust a stale number).
- [ ] You can recite, without looking: passing score **66%**, duration **120 minutes**, **15-20**
      performance-based tasks, `etcdctl` backs up / `etcdutl` restores (not interchangeable), and
      Kustomize has **no** exam-allowed documentation domain (must be memorized, not looked up).
- [ ] Exam logistics confirmed: single monitor only, no VM exam client, physical government ID ready,
      quiet room booked, and (Siemens corporate network specifically) HTTPS access to AWS S3 endpoints
      is not blocked by firewall/VPN.

---

## Gate 1 — Question bank coverage (P0 items must be at ~100%, not "mostly")

Pull your actual pass/fail per question from each file. A question only counts as a correct pass if
you solved it **cold** (task text only, no solution peeking) inside roughly 1.5x its stated target
time, and your own verification commands confirmed the fix — not just "it looked right."

| File | P0 question count | Your P0 pass count | Threshold | Status |
|---|---|---|---|---|
| `04-question-bank/01-cluster-architecture-maintenance.md` | 17 | ___ / 17 | **17/17 (100%)** | [ ] |
| `04-question-bank/02-workloads-scheduling.md` | 5 | ___ / 5 | **5/5 (100%)** | [ ] |
| `04-question-bank/03-networking.md` | 5 | ___ / 5 | **5/5 (100%)** | [ ] |
| `04-question-bank/04-storage-rbac.md` | 13 | ___ / 13 | **13/13 (100%)** | [ ] |
| `04-question-bank/05-troubleshooting.md` | 19 | ___ / 19 | **19/19 (100%)** | [ ] |
| **Total P0 across all 5 files** | **59** | ___ / 59 | **59/59 (100%)** | [ ] |

- [ ] **P0 total is 59/59 (100%).** These are explicitly the highest-frequency, highest-failure-risk
      items per the priority matrix — a single-mistake-fails-the-task item like etcd restore or a
      static-pod fix has no partial credit on the real exam either, so "mostly correct" on a P0 item
      is not a pass.
- [ ] **P1 items are at ≥80% correct** across `01`, `02`, `03`, `04`, `05` combined (P1 counts: 6 + 11
      + 17 + 5 + 7 = 46 total; threshold = at least 37/46 correct).
- [ ] **Troubleshooting scenario banks** (`07-troubleshooting-scenarios-workload-network-storage.md`,
      20 scenarios; `08-troubleshooting-scenarios-cluster-security.md`, 21 scenarios) — **at least
      35/41 (≈85%) solved within their stated time limit**, diagnosing from symptom alone (Setup
      block applied by you or a study partner, not read in advance).
- [ ] **Micro-drills** (`06-micro-drills.md`, 69 total across 30-second/1/2/3/5-minute tiers) — **at
      least 60/69 (≈87%) answered within the stated time limit** on a cold run (command recall, not
      conceptual understanding — these should be reflexive by now).

---

## Gate 2 — Named skill timing thresholds

These are the specific, high-failure-risk skills the snapshot file rates **P0 / Very-High-or-Very-Very-High
failure risk**. Each must be demonstrable cold, from an unseeded fresh scenario (not the exact one
you memorized), within the stated time. Do at least 2 clean cold reps of each before checking the box.

| Skill | Reference drill(s) | Time threshold | Rep 1 time | Rep 2 time | Status |
|---|---|---|---|---|---|
| etcd snapshot backup (`etcdctl snapshot save` + `snapshot status` verification, correct TLS flags) | `01-...md` Q11/Q13/Q14; Mock 2 Task 2 | **≤ 5 min** | ___ | ___ | [ ] |
| etcd disaster recovery (`etcdutl snapshot restore` to a **new** data-dir, repoint manifest `hostPath`, confirm point-in-time correctness) | `01-...md` Q11/Q12; Mock 1 Task 8; Mock 3 Task 9 | **≤ 10 min** | ___ | ___ | [ ] |
| kubeadm join (generate fresh token + hash, join, confirm `Ready`) | `01-...md` Q1; Mock 2 Task 10 | **≤ 5 min** | ___ | ___ | [ ] |
| kubeadm cluster upgrade, one full node (drain → `upgrade node`/`upgrade apply` → kubelet/kubectl bump → uncordon) | `01-...md` Q18/Q19; `06-micro-drills.md` 5-Minute Drill 1; Mock 2 Task 14 | **≤ 18 min per node** | ___ | ___ | [ ] |
| Certificate diagnosis + renewal + forced static-pod reload (no CA regen) | `01-...md` Q9/Q10; Mock 1 Task 9; Mock 3 Task 10 | **≤ 8 min** | ___ | ___ | [ ] |
| Static pod / control-plane component crash-loop diagnosis and fix (`crictl logs` → manifest fix) | `01-...md` Q6/Q7; Mock 2 Task 11; Mock 3 Task 2 | **≤ 8 min** | ___ | ___ | [ ] |
| Worker node `NotReady` diagnosis and repair (no reboot, no re-join) | `01-...md` Q3; Mock 1 Task 1; Mock 2 Task 7; Mock 3 Task 1 | **≤ 8 min** | ___ | ___ | [ ] |
| Any single troubleshooting scenario, symptom to verified fix, averaged across a random 5-scenario pull from `07`/`08` | files `07`/`08` | **≤ 7 min average** (matches the confirmed ~7 min/task real-exam pace) | ___ | ___ | [ ] |
| RBAC least-privilege build (ServiceAccount + Role/ClusterRole + Binding scoped correctly, verified with `auth can-i` both directions) | `04-...md` Part B; Mock 1 Task 10; Mock 3 Task 11 | **≤ 8 min** | ___ | ___ | [ ] |
| NetworkPolicy default-deny + scoped allow + DNS carve-out (3-rule pattern) | `03-...md` Q13-Q17; Mock 1 Task 12; Mock 2 Task 9 | **≤ 8 min** | ___ | ___ | [ ] |
| Static PV + PVC binding to a specific PV (`spec.volumeName`, all 4 fields agreeing) | `04-...md` Part A; Mock 1 Task 17; Mock 2 Task 5 | **≤ 6 min** | ___ | ___ | [ ] |

- [ ] All 11 rows above have **two clean cold reps**, both inside threshold, on **different randomized
      scenarios** (not the same memorized task run twice).

---

## Gate 3 — Mock exam scores (the actual bar)

Score strictly against each mock's own verification commands — no self-generous partial credit beyond
what the mock's task text already allows. Record every attempt, not just your best one.

| Mock | Difficulty | Attempt 1 | Attempt 2 | Attempt 3 | Minimum required | Status |
|---|---|---|---|---|---|---|
| Mock Exam 1 (Normal) | On-ramp, single-fault tasks | ___ / 100 | ___ / 100 | ___ / 100 | **≥ 80/100**, on the *first* timed attempt | [ ] |
| Mock Exam 2 (Real-Exam Difficulty) | Matches real exam pacing/difficulty | ___ / 100 | ___ / 100 | ___ / 100 | **≥ 75/100**, and specifically on a **fresh, cold attempt** (not one you've seen the seed faults for) | [ ] |
| Mock Exam 3 (Hard Mode) | Deliberately stacked/compound faults, tighter pacing | ___ / 100 | ___ / 100 | ___ / 100 | **≥ 66/100** (bare real-exam pass bar) — ideally **≥ 75/100** | [ ] |

Hard requirements, not just the raw score:

- [ ] **Mock Exam 2 ≥ 75/100 achieved within the 120-minute limit**, run start-to-finish in one sitting
      with no pausing the clock — this is the load-bearing gate since it's explicitly built to match
      real-exam difficulty and pacing (per its own instructions: ~6-7 min/task average, matching the
      community-reported real-exam pace).
- [ ] On that qualifying Mock 2 attempt, **domain sub-scores** were each individually at or above 66%
      of that domain's mock points — i.e. you did not compensate for a weak domain by over-performing
      in another. Record below:

  | Domain | Mock 2 points available | Your points | ≥ 66% of domain? |
  |---|---|---|---|
  | Troubleshooting | 30 | ___ | [ ] (≥ 20) |
  | Cluster Architecture | 25 | ___ | [ ] (≥ 17) |
  | Services & Networking | 20 | ___ | [ ] (≥ 14) |
  | Workloads & Scheduling | 15 | ___ | [ ] (≥ 10) |
  | Storage | 10 | ___ | [ ] (≥ 7) |

- [ ] **Mock Exam 3 attempted at least once end-to-end within 120 minutes** and scored ≥ 66/100. If you
      haven't cleared 66 on Hard Mode, that's a signal your margin on the real exam is thin, not a hard
      blocker by itself — but it should not be your only mock-based evidence of readiness. Treat a
      Mock 3 pass as the difference between "will pass" and "should pass."
- [ ] No mock attempt above relied on reading the Solutions section first, mid-attempt, "just to check
      the approach" — if that happened, the attempt doesn't count toward these gates; re-run a fresh
      attempt.

---

## Gate 4 — Killer.sh simulator (if you've purchased/activated it)

- [ ] Attempt 1 scored **≥ 60%** (killer.sh is confirmed intentionally harder than the real exam per
      the snapshot file — don't hold it to the same 66% bar, but don't wave off a sub-50% score either).
- [ ] Attempt 2 (of your 2 included attempts) scored **higher than Attempt 1**, demonstrating the gap
      closed rather than stayed flat.
- [ ] Every question you missed on killer.sh has a corresponding fixed gap: you can now redo that exact
      skill cold, correctly, from `04-question-bank/` or the mocks.

*(If you have not yet activated killer.sh, this gate is not blocking — but do not let both attempts
sit unused past your booking date; use at least one within the final week before the exam.)*

---

## Gate 5 — Final week sanity checks

- [ ] You can do a full etcd backup-and-restore cycle **from memory, no notes, no docs lookup**, in
      under 10 minutes, including verifying `snapshot status` before restoring and confirming a
      point-in-time-correct outcome (a namespace created before the snapshot exists; one created after
      does not).
- [ ] You can state the `kubeadm upgrade apply` (first control-plane node only) vs `kubeadm upgrade
      node` (every other node) distinction without hesitation — this is called out as a common
      wrong-answer pattern in Mock 2 Task 14's grading notes.
- [ ] You have re-verified the current Kubernetes version target on the live LF page (Gate 0, second
      box) no more than 1-2 weeks before your actual exam date.
- [ ] You've re-run at least one full mock (any of the three) within the last 5-7 days before booking,
      and it still clears its own threshold above — readiness measured 3+ weeks ago does not carry
      forward automatically.
- [ ] You are not carrying a known, unfixed P0 gap into the exam "because it probably won't come up" —
      if any P0 row in Gate 1 or Gate 2 is still unchecked, that is itself your answer to whether you're
      ready.

---

## The actual gate

**Do not book the exam until you can honestly check every box above.**

If you're short on exactly one or two items, don't book "to force yourself to be ready" — go back to
the specific file/question referenced next to the failing box, drill it to threshold, and re-check
only that box. Booking against an honest, fully-checked list is what the $445 (or $625/$645 with
add-ons) and your one free retake are for — not a substitute for clearing this list first.
