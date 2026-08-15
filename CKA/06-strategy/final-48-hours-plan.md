# Final 48 Hours — CKA Exam Countdown Plan

*Assumes you have already worked through `01-exam-snapshot-and-priorities.md`, the topic files in
`02-topics/`, the question banks in `04-question-bank/`, and at least one full timed run of a mock
exam in `05-mock-exams/`. This document is not a re-teaching pass — it is a triage and logistics
plan for the last two days. If you find yourself reading Kubernetes docs on a concept you've never
touched before at this stage, stop: that is exactly the failure mode this plan exists to prevent.*

**Context this plan assumes:** you will most likely sit the exam on your Siemens corporate laptop,
on a corporate/VPN-managed network. Every environment-check step below is written with that
assumption front and center, per the corporate-network note in
`01-exam-snapshot-and-priorities.md` ("Handbook explicitly requires HTTPS access to AWS S3
endpoints not be blocked by firewall/VPN"). If you have any doubt about whether you'll be allowed
local admin rights, unrestricted webcam/mic access, or unfiltered HTTPS egress on that machine,
the **48 hours before** checks below are your last real window to switch to a personal device
instead.

---

## 48 hours before

**Practice — one full timed mock, then targeted drilling on what it exposes.**

- Run **`05-mock-exams/mock-exam-2-real-difficulty.md`** as a single, uninterrupted 120-minute
  session if you haven't already run it this week. It's calibrated to real-exam difficulty and
  pacing (~6–7 min/task) — a better signal at this stage than the easier
  `mock-exam-1-normal.md` (save that one only as a confidence warm-up if you're feeling shaky, not
  as your primary data point) or `mock-exam-3-hard-mode.md` (deliberately stacks multiple faults
  per task — useful earlier in prep, but overkill and possibly demoralizing 48 hours out).
- Self-grade against the point tables and domain totals at the bottom of that file. Note which
  **domain** (Troubleshooting 30 / Cluster Architecture 25 / Services & Networking 20 /
  Workloads & Scheduling 15 / Storage 10) cost you the most points — that domain gets your
  remaining drilling time today, not an even split across all five.
- For whichever domain(s) came out weakest, go back to the matching file in `04-question-bank/`
  (`01-cluster-architecture-maintenance.md`, `02-workloads-scheduling.md`, `03-networking.md`,
  `04-storage-rbac.md`, `05-troubleshooting.md`) and redo only the questions you got wrong or were
  slow on — not the whole file again. If your miss was in cross-cutting diagnosis rather than a
  single domain, use `07-troubleshooting-scenarios-workload-network-storage.md` or
  `08-troubleshooting-scenarios-cluster-security.md` instead — those are built specifically to mix
  root causes the way real tasks do.
- If your weak spot was raw command recall speed rather than conceptual understanding, run
  `06-micro-drills.md` end to end once, timing yourself against the stated targets. This is the
  single highest-value 45 minutes you can spend today if you're still hesitating on syntax for
  things like `kubectl taint`, `kubectl rollout undo --to-revision`, or `kubectl autoscale`.

**Do NOT learn anything new.** No new topics, no reading fresh sections of the Kubernetes docs on
concepts you haven't drilled yet, no Gateway API deep-dives if you've never touched it, no
Kustomize overlay authoring from scratch if that's still shaky — 48 hours is not enough time for a
genuinely new skill to become exam-fast, and every hour spent on something brand-new is an hour not
spent hardening something you're 80% solid on. If a mock task exposes a total blind spot (e.g. you
truly cannot do a `kubeadm upgrade` sequence at all), treat that as a targeted "patch this one gap"
exercise using the exact worked solution in the question bank — not an invitation to go read
background theory.

**Commands to actively re-drill today (highest failure-risk per the priority matrix in
`01-exam-snapshot-and-priorities.md`):**
- `kubeadm token create --print-join-command`, `kubeadm upgrade plan` / `apply` / `node`
- `etcdctl snapshot save` (backup) vs. `etcdutl snapshot restore` (restore) — say the split out loud
  until it's reflexive; this is called out as a near-guaranteed, single-mistake-fails-the-task item
- `kubeadm certs check-expiration`, `kubeadm certs renew <name>` / `renew all`, and the fact that a
  renewed cert requires a static-pod restart (move the manifest out of
  `/etc/kubernetes/manifests/` and back) to actually take effect
- `kubectl auth can-i ... --as=system:serviceaccount:<ns>:<name> -n <ns>` — the fully-qualified
  `system:serviceaccount:` form, always with an explicit `-n`
- `kubectl drain --ignore-daemonsets --delete-emptydir-data`, cordon/uncordon
- Reading `kubectl describe pod` Events *before* `kubectl logs`, and `crictl`/`journalctl` as the
  next layer down when `kubectl` itself is degraded or unavailable

**Environment and proctoring checks — do these today, not tomorrow, because today is when you
still have time to switch machines if something fails:**
- Run PSI Bridge's official system compatibility/readiness check on the **actual machine** you
  intend to test on. If it's the Siemens corporate laptop, pay specific attention to whether the
  check can reach whatever S3 endpoints the proctoring client needs — per the snapshot file, the
  handbook explicitly warns this can be blocked by corporate firewall/VPN. If it fails or times out
  here, you have 48 hours to escalate to IT for a firewall exception, or pivot to a personal
  device — you do not have that runway if you discover this 30 minutes before the exam.
  For example, run the readiness check while connected to the normal corporate VPN, and separately
  note whether split-tunneling or a temporary VPN disconnect is even something you're allowed to do
  on that machine — that answer needs to come from IT today, not be improvised tomorrow.
- Confirm you have local admin rights (or a known workaround) on the laptop if the PSI Bridge
  client needs to install anything — many corporate images lock this down by policy.
- Confirm webcam and microphone are physically present, working, and not disabled by a corporate
  MDM/endpoint-security policy (some corporate builds block camera/mic access at the OS level for
  non-approved apps).
- Confirm you have a valid, physical, government-issued photo ID (not a photo of one, not a
  digital ID) that matches the name on your exam registration.
- Confirm single-monitor capability: if you normally work with a docking station driving two
  monitors, plan now for exactly one connected display on exam day — dual monitors are explicitly
  unsupported by the remote proctoring platform.
- Book/confirm a quiet, private room for your actual exam time slot, and mentally note that
  Teams/Outlook notification popups, corporate chat pings, or a shared-office interruption are
  exactly the kind of thing that can trigger a proctor flag or just wreck your focus mid-task.

**Mistakes to avoid at this stage:**
- Cramming a second full mock exam back-to-back with the first — fatigue degrades your diagnostic
  speed more than a second data point helps you.
- Treating a single wrong answer as "I don't know this domain" — re-read the specific
  **Common mistake** callout for that question first; several of the traps in the question banks
  are one-line, easily-internalized gotchas (e.g. `roleRef` immutability, `policyTypes` needing to
  be set explicitly, `requests` vs. `limits`) rather than genuine knowledge gaps.
- Discovering a corporate-network blocker on exam morning instead of today.

---

## 24 hours before

**Practice — light, targeted, and time-boxed. No new full mock exam today.**

- Do **not** run a third full 120-minute mock exam. At this distance from the exam, a full mock
  mostly produces fatigue and second-guessing rather than new learning — you already have data
  from yesterday's run telling you exactly where your gaps are.
- Instead, pick a **timed subset**: 6–8 questions pulled specifically from your weakest domain(s)
  in `04-question-bank/`, or a handful of scenarios from
  `07-troubleshooting-scenarios-workload-network-storage.md` /
  `08-troubleshooting-scenarios-cluster-security.md` if Troubleshooting was your soft spot (it
  carries the most exam weight at 30%, so it's the highest-value place to spend a scarce 24-hour
  budget if you have to choose one domain). Cap this at 60–90 minutes total.
- Re-run the **30-second and 1-minute drills** in `06-micro-drills.md` once more, purely for speed
  — the goal today is reflex, not new understanding. If you're still hesitating for more than the
  stated target time on any of these, that command goes on a short mental "say it out loud twice
  before bed" list.
- Re-read the **Priority Matrix** in `01-exam-snapshot-and-priorities.md` once, end to end, as a
  refresher of what's P0 vs. P1/P2 — this recalibrates your in-exam triage instincts (which task to
  attempt first, which to skip and come back to) without requiring any new hands-on practice.
- Skim (don't re-solve) the **Common mistake** call-outs across the question banks you've already
  worked through. These are short, and re-reading them fresh the day before is far higher-value
  per minute than re-solving tasks you already got right yesterday.

**Do NOT learn anything new today.** This bears repeating at 24 hours specifically because it's the
point where anxiety most often pushes people toward "let me just quickly read up on X" — resist
it. If something is still a genuine blind spot at this point, the correct move is to accept the
risk on that narrow topic and make sure you don't get stuck on it mid-exam (time-box it and move
on), not to attempt to learn it from scratch tonight.

**Commands to review (recognition-level, not deep practice):** skim your own notes or
`03-cheatsheets/` once for anything you still have to consciously think about rather than type
automatically — particularly `kubectl patch` JSON-patch syntax
(`--type=json -p='[{"op":"add","path":"...","value":...}]'`), the `nodeSelectorTerms` AND/OR
nesting rule for node affinity, and the exact `NetworkPolicy` shape for a DNS egress carve-out
(`namespaceSelector` matching `kube-system` on UDP/TCP 53) — these show up repeatedly across the
question banks and are easy to fumble under time pressure even when you conceptually know them
cold.

**Environment and proctoring checks:**
- Confirm the outcome of yesterday's PSI Bridge system check was fully green. If you raised an IT
  ticket for a firewall/VPN exception yesterday, confirm today whether it's actually been applied
  — don't assume it went through silently.
- Do a final rehearsal disconnect of any second monitor/docking-station display so you know exactly
  what "single monitor" looks like on this machine before exam day.
- Confirm your exam time slot, time zone, and calendar block are all correct, and that the block on
  your Siemens calendar is marked so you won't get pulled into a meeting mid-exam.
- Charge the laptop fully and identify where you'll sit with a stable wired or strong Wi-Fi
  connection — do not plan to test from a shared or open office space.
- Lay out your physical photo ID somewhere you won't have to search for it tomorrow.

**Mistakes to avoid at this stage:**
- Running another full-length mock "just to be safe" — it costs you sleep and mental freshness
  for a marginal, often misleading, confidence signal (mock fatigue commonly looks like new
  weakness that isn't real).
- Leaving the IT firewall-exception question unresolved and just hoping it'll be fine tomorrow.
- Staying up late drilling — sleep quality tonight has a bigger effect on tomorrow's diagnostic
  speed under time pressure than one more hour of practice does.

---

## Morning of the exam

**Practice — warm-up only, nothing evaluative.**

- Do **not** attempt a new mock exam, a new question-bank section, or any scenario you haven't
  already seen. There is no time left for a bad result here to translate into a fix — it can only
  cost you confidence right before you need it most.
- Spend 15–20 minutes on a light warm-up: redo 8–10 of the **30-second drills** from
  `06-micro-drills.md` purely to get your hands moving on `kubectl` syntax before the real thing.
  Stop as soon as you feel warmed up — this is not the time to chase a hard question.
- Skim (2–3 minutes, no more) the **Executive Summary** at the top of
  `01-exam-snapshot-and-priorities.md` as a final framing reminder: Troubleshooting is the largest
  domain, generate YAML rather than hand-write it, `etcdctl` backs up / `etcdutl` restores.
- Mentally rehearse your **triage discipline** one more time: read the whole task before typing,
  confirm the right `kubectl config use-context` before touching anything, don't burn more than
  roughly double a task's implied time budget before moving on and coming back later.

**Do NOT learn anything new.** By this point the only thing left to optimize is your physical and
mental state, not your knowledge.

**Commands to have fresh in your head (recognition only, don't grind on these):**
```bash
alias k=kubectl
export do="--dry-run=client -o yaml"
```
plus the exam's own aliasing note: on the real exam `kubectl` is pre-aliased to `k` with
autocompletion already set up for you — you don't need to configure this yourself, but knowing the
`do` shorthand pattern (`k create deployment ... $do > file.yaml`) should be reflexive.

**Environment and proctoring checks — do these before you sit down for real, ideally with buffer
time:**
- Boot the laptop fresh (not just wake from sleep) to clear out any lingering corporate background
  processes, forced update prompts, or antivirus scans that could interrupt you mid-exam.
- Confirm you are on the network you tested with 24–48 hours ago, not a different guest/hotspot
  network with different firewall behavior.
- Fully close Teams, Outlook, Slack, and any other corporate notification-generating app; disable
  notification banners at the OS level if your MDM policy allows it.
- Physically disconnect any second monitor and any unnecessary peripherals.
- Have your physical photo ID next to you, ready.
- Do a final webcam/mic check.
- Use the bathroom, get water, and clear your desk of anything the proctor's room-scan might flag
  as disallowed (secondary devices, notes, phone).

**Mistakes to avoid this morning:**
- Trying to squeeze in "just one more" practice question you haven't done before.
- Doom-scrolling exam-anxiety forum threads — per `01-exam-snapshot-and-priorities.md`, a lot of
  that community "intelligence" is unverifiable anecdote anyway and won't change your prep at this
  point.
- Skipping breakfast/water because you're rushing — a 2-hour exam with real time pressure is not
  the moment to be dealing with hunger or dehydration as an added distraction.

---

## 30 minutes before the exam

**Practice:** none. Stop touching any study material entirely — the last useful practice already
happened this morning.

**Final environment and proctoring checklist (work through in order):**
1. Sit at your confirmed quiet, private location with the door closed and others in the household
   or office aware you're not to be interrupted for two hours.
2. Confirm single monitor only, laptop plugged into power (not running on battery).
3. Close every application except what the PSI Bridge client itself requires; disable
   notifications at the OS level one final time.
4. Confirm Wi-Fi/network stability one last time; if you have any control over it, avoid other
   heavy network usage in your household/office for the duration.
5. Have your physical, government-issued photo ID in hand, ready for the check-in scan.
6. Do the room scan/webcam walkthrough calmly and fully — don't rush it, since a flagged or
   incomplete scan can cost you real exam time to resolve.
7. Confirm you know the terminal shortcuts you'll actually need in the exam's Linux terminal:
   **Copy = Ctrl+Shift+C, Paste = Ctrl+Shift+V** (not the normal Ctrl+C/Ctrl+V), and that the
   **Insert key is disabled** — use `i` to enter insert mode and `Esc` to exit it in `vi`, since
   muscle-memory keyboard habits from your normal editor will not transfer.
8. Water within reach, bathroom already handled, phone silenced and out of reach/out of the room
   per the proctoring rules.

**Mental checklist — say these to yourself once, then stop thinking about prep entirely:**
- Read every task fully before typing anything.
- Confirm `kubectl config current-context` immediately after every context switch the exam gives
  you — this is the single most common, entirely avoidable way to lose points.
- `etcdctl` backs up, `etcdutl` restores.
- Generate YAML with `--dry-run=client -o yaml` rather than hand-writing it from memory.
- Check `kubectl describe pod` Events before `kubectl logs`; drop to `crictl`/`journalctl` when
  `kubectl` itself is unavailable or the component in question is below the API layer.
- If a task is taking roughly double its implied time budget with no progress, mark it and move
  on — points are points regardless of order, and a stuck task shouldn't cost you an easy one
  later in the exam.
- Passing score is 66/100 — you do not need every task perfect, you need most of them solid.

**Mistakes to avoid in this final window:**
- Opening a question bank or mock exam "one last time" for reassurance — there is no new
  information to gain here, only the risk of spiking anxiety over something you can no longer fix.
- Rushing the ID check or room scan and having to redo it under time pressure.
- Forgetting the Ctrl+Shift+C/V and disabled-Insert-key quirks and losing your first few minutes
  fighting the terminal instead of the task.
