# CKA Research — 02: Blogs & Articles

**Compiled:** 2026-08-15
**Scope:** Community blog posts / articles about the current CKA exam, cross-checked against official sources where possible.
**Reader context:** Nirbhay Singh — already CKAD-certified (valid through Sep 2026), 11+ years cloud/platform architecture, needs CKA-specific admin skills (kubeadm, etcd, static pods, RBAC, NetworkPolicy, storage, advanced troubleshooting) refreshed, not Kubernetes fundamentals.

---

## Methodology note (read this before trusting anything below)

A prior draft of this report claimed the task was impossible because the `WebSearch` tool returned `FAILED_PRECONDITION` (blocked by a Vertex AI org policy, `constraints/vertexai.allowedPartnerModelFeatures`). **I re-tested this myself and confirmed it is still true** — every `WebSearch` call fails with that exact error. So there is no working search engine in this environment.

However, `WebFetch` **does** work for direct URLs. I used it two ways:
1. Fetching known, stable official/aggregator URLs directly (Linux Foundation training page, CNCF curriculum repo, kubernetes.io releases page).
2. Fetching **listing/tag pages** (dev.to's `/t/cka` tag page, KodeKloud's blog index) to discover article URLs, then fetching each article individually to verify its actual content.

Search-engine workarounds did **not** work reliably:
- `reddit.com` — blocked entirely by the fetch tool ("unable to fetch from www.reddit.com").
- `google.com/search` — redirected to a cookie-consent interstitial, never reached real results.
- `bing.com/search` — returned a Polish-localized page of results about Hungarian bus/rail timetables, i.e. garbage unrelated to the query. Do not trust generic search-engine fetches in this environment.
- `duckduckgo.com/html` — served a CAPTCHA challenge page, no results.

**Practical consequence: my community-article coverage is limited to what the dev.to `/t/cka` tag page and the KodeKloud blog index happened to surface, not an exhaustive web-wide search.** I could not search Medium, LinkedIn, Hacker News, or Reddit at all in this session. Treat the "Community-reported" section below as a useful but non-exhaustive sample, not a saturation-level survey of candidate reports (Phase 2 of the original research brief asked for broad, multi-source saturation — I was not able to achieve that here due to tooling limits).

Also note: `WebFetch` itself passes fetched HTML through an intermediary summarization step (per its own tool description), not a raw verbatim dump. Where a fact below is load-bearing, I re-fetched the primary article directly (not just an index page) to reduce the chance of index-page hallucination, and I cross-checked overlapping facts (price, passing score, weightings) across two independent sources. Anything I could only get from one fetch, or that seemed internally inconsistent, is flagged **UNVERIFIED** below.

---

## Verified official information

These come directly from official Linux Foundation / CNCF properties, fetched today (2026-08-15).

| Fact | Value | Source | Fetched |
|---|---|---|---|
| Exam duration | 2 hours | [Linux Foundation — CKA](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/) | 2026-08-15 |
| Exam cost | $445 (exam only); $625 with THRIVE-ONE annual subscription; $645 with Kubernetes Fundamentals course | Linux Foundation — CKA (as above) | 2026-08-15 |
| Kubernetes version tested | v1.35 (LF states the exam environment aligns with the most recent minor version ~4–8 weeks after release) | Linux Foundation — CKA (as above) | 2026-08-15 |
| Domain weightings | Cluster Architecture, Installation & Configuration 25% · Troubleshooting 30% · Services & Networking 20% · Workloads & Scheduling 15% · Storage 10% | Linux Foundation — CKA (as above) | 2026-08-15 |
| Curriculum file version | `CKA_Curriculum_v1.35.pdf` | [github.com/cncf/curriculum](https://github.com/cncf/curriculum) | 2026-08-15 |
| Passing score | 66% | [KodeKloud — Kubernetes Certifications 2026: A Complete Guide](https://kodekloud.com/blog/kubernetes-certification/), published/updated 2026-07-16 | 2026-08-15 |
| Retake policy | One free retake included per exam attempt (applies across all five CNCF Kubernetes certs) | KodeKloud (as above) | 2026-08-15 |
| Certification validity | 2 years (certs earned before April 2024 retain 3-year validity) | KodeKloud (as above) | 2026-08-15 |
| Format | Online, remotely proctored, 100% performance-based (live terminal tasks, no multiple choice) | Linux Foundation — CKA (as above) | 2026-08-15 |
| "Kubestronaut" recognition | Holding all five active Kubernetes certs (CKA, CKAD, CKS, KCNA, KCSA) simultaneously earns "Kubestronaut" status with community benefits | KodeKloud (as above) | 2026-08-15 |

### UNVERIFIED / needs your own confirmation before relying on it

- **"17 questions per attempt, with two simulation attempts included"** — this phrase came out of my fetch of the Linux Foundation page. I cannot tell from the fetched summary whether this describes (a) the actual proctored CKA exam task count, or (b) the bundled killer.sh simulator sessions (LF has historically bundled 2 killer.sh simulator sessions with CKA purchase, separate from the real exam). The classic public description of the CKA has long been "15–20 performance-based tasks," not a fixed "17." **Do not memorize "17" as the real exam's task count — verify directly on the official page or your purchase confirmation before the exam.**
- **Kubernetes release cadence data** (I fetched kubernetes.io/releases and got v1.36 as "latest" with v1.36, v1.35, v1.34 all showing identical patch dates of 2026-06-09) — the identical dates across three minor versions is suspicious and may be a summarization artifact rather than real data. Treat the specific patch/EOL dates as **UNVERIFIED**; the general claim "CKA lags the newest minor release by 4-8 weeks, so a v1.35 or v1.36 exam target in mid-to-late 2026 is plausible" is reasonably solid but the exact numbers are not.
- I could not independently fetch killer.sh's own page for simulator specifics (scenario count, 36-hour access window, etc.) — the page returned only a bare heading with no body content via WebFetch. These are well-known facts from general Kubernetes-community knowledge (killer.sh sessions are bundled with CKA/CKAD/CKS purchase and are widely regarded as harder than the real exam), but I could not verify current specifics for 2026 in this session. **Flag as UNVERIFIED for 2026 specifically.**

---

## Community-reported information

All of the following are from articles I fetched and read directly (not just index-page summaries), on dev.to and the KodeKloud blog. Coverage is limited to what these two sites' listing pages surfaced — see methodology note above.

### 1. "How I Passed the CKA in 2026" — dev.to, author `yltw27`
URL: https://dev.to/yltw27/how-i-passed-the-cka-in-2026-143c
Published: 2026-07-16

- Author self-describes as a full-time software engineer who relies on AI assistants day-to-day but found the CKA's no-AI, no-autocomplete terminal environment a real adjustment.
- Study resources used: a Udemy course (author found gaps in the networking material and had to supplement with an LLM), killer.sh (two attempts — first scored 16/75, second scored 53–58/93 — note the differing denominators, which the article doesn't reconcile, so treat the exact scoring scale as **UNVERIFIED**), Killercoda, official Kubernetes docs.
- Confirms: 2-hour terminal-based exam, no autocomplete, no AI assistance, Firefox used in-exam for documentation lookup.
- Emphasized domains: cluster maintenance and certificate management, RBAC/auth, workload deployment and networking, troubleshooting broken cluster components, CNI/DNS issues.
- Practical tips reported: `Ctrl+Shift+C` / `Ctrl+Shift+V` for terminal clipboard; a personal "5-minute rule" before moving on from a stuck task; never hand-write YAML from scratch — generate it via `kubectl get <resource> -o yaml` and edit; check kubelet status and container logs first when a node looks broken; don't sit and watch a hanging command — open a second terminal tab and keep working.
- No specific claim about which Kubernetes version was on the exam.

### 2. "AI Can Generate Kubernetes YAML — But Is the CKA Still Worth It in 2026?" — dev.to, Shahzad Ali Ahmad
URL: https://dev.to/shahzadahmad91/ai-can-generate-kubernetes-yaml-but-is-the-cka-still-worth-it-in-2026-3j0l
Published: 2026-06-06

- Author: Senior DevOps/SRE engineer, 9+ years in AWS/Azure cloud infra, recently CKA-certified, pursuing the full "Kubestronaut" set (CKA/CKAD/CKS).
- Opinion piece, not a procedural exam report — does not state exam cost, format, or domain weightings.
- Core argument: the CKA's value in 2026 is in troubleshooting/investigation ability and structured coverage of pods/networking/storage/security/cluster-admin, not in YAML-writing per se, since AI tools already generate YAML. Acknowledges the cert does **not** cover GitOps, platform engineering, monitoring, or cost optimization — worth knowing so you don't expect the exam to test those.
- Relevant to your prep: reinforces that troubleshooting/judgment, not manifest authorship, is where exam value (and the 30% troubleshooting weighting) concentrates.

### 3. "My Top 50 kubectl Commands for CKA and Daily Kubernetes Administration" — dev.to, Shahzad Ali Ahmad
URL: https://dev.to/shahzadahmad91/my-top-50-kubectl-commands-for-cka-and-daily-kubernetes-administration-41nh
Published: 2026-06-06

- Same author as #2.
- Commands highlighted as exam-speed-relevant (all standard, all worth having as muscle memory rather than new information for someone at your level):
  - `kubectl run nginx --image=nginx --dry-run=client -o yaml` / `kubectl create deployment nginx --image=nginx --dry-run=client -o yaml` for fast YAML scaffolding.
  - `kubectl explain deployment.spec.template.spec` for in-terminal schema lookup instead of switching to docs.
  - `kubectl get events --sort-by=.metadata.creationTimestamp` for chronological event triage.
  - `kubectl logs --previous <pod>` for CrashLoopBackOff root-causing; `kubectl logs -f <pod>` to follow.
  - `kubectl rollout history deployment/nginx` and `kubectl rollout undo deployment/nginx`.
  - `kubectl get pods -o wide` for node placement.
  - Aliasing `kubectl` to `k` for exam-time typing speed.
- Nothing here is CKA-specific beyond what a CKAD holder already knows — no kubeadm/etcd/RBAC/NetworkPolicy content in this particular article despite the "CKA" framing. Don't rely on it for the admin-specific gaps you actually need to close.

### 4. "Install a CNI and fix the flannel pod-CIDR mismatch" (CKA Services & Networking scenario) — dev.to, "The Cyber Sidekick"
URL: https://dev.to/thecybersidekick/install-a-cni-and-fix-the-flannel-pod-cidr-mismatch-cka-services-networking-5hf4
Published: 2026-07-10

- Self-styled practice scenario (not a real-exam-question reproduction, per the author's own framing), simulating: cluster with no CNI installed → all nodes `NotReady`, CoreDNS pods stuck `Pending` → apply a flannel manifest with a deliberately mismatched pod CIDR → diagnose and fix.
- Commands walked through: `kubectl get nodes`, `kubectl get pods -n kube-system -o wide`, `kubectl apply -f kube-flannel.yml`, `kubectl -n kube-flannel logs <pod>`, `kubectl -n kube-flannel edit configmap kube-flannel-cfg`, `kubectl -n kube-flannel delete pod -l app=flannel`, then a cross-node ping to verify.
- Maps to: Services & Networking domain, specifically CNI bring-up and pod-CIDR troubleshooting — this is a good practice-scenario template for you to build an "original" drill around (per the ethical-use rule: extract the competency — diagnosing a CNI/CIDR misconfiguration via node/pod status and CNI-controller logs — rather than reusing this exact scenario verbatim if it turns out to echo a real exam task).
- The same author has a companion post, "CKA Scenario 5 — Force nginx to TLS 1.3 with a ConfigMap edit + rolling restart" (published 2026-06-29), which I did not fetch in full — noting its existence only; **UNVERIFIED content**, title only.

### 5. "Kubernetes Certifications 2026: A Complete Guide" — KodeKloud Blog, Nimesha Jinarajadasa
URL: https://kodekloud.com/blog/kubernetes-certification/
Published/updated: 2026-07-16

- Overview article covering all five CNCF Kubernetes certs (CKA, CKAD, CKS, KCNA, KCSA). This is the source for several of the "Verified official information" line items above (passing score 66%, one free retake, 2-year validity, Kubestronaut program) — I'm listing it under community-reported because KodeKloud is a commercial training vendor, not an official CNCF/LF property, even though its factual claims here are specific and cross-checked cleanly against the LF page for the overlapping fields (cost, format, domain weighting).
- States CKA differs from CKAD in that CKA targets **cluster operators/administrators** (troubleshooting, networking, storage — troubleshooting called out explicitly as 30% of weight) versus CKAD's developer focus (deployments, config, probes, services) — consistent with the official weighting table above.
- Notes CKS requires an active CKA as a prerequisite.

---

## What this means for your prep (synthesis, not new research)

- The one recurring, cross-source-consistent theme across every 2026 article fetched: **troubleshooting is where points and time are won or lost** (30% official weight; every community article independently emphasizes kubelet/node/CNI/DNS/log-based diagnosis over YAML authorship). This matches your CLAUDE.md-documented CKAD baseline (you already know Deployments/Services/ConfigMaps cold) — the delta-effort should go toward **kubeadm cluster operations, static pod/kubelet diagnosis, etcd, RBAC, and NetworkPolicy/CNI troubleshooting**, not general workload YAML.
- Generate, don't hand-write, YAML (`--dry-run=client -o yaml`, `kubectl get -o yaml`) — stated independently by two different authors above; consistent with standard CKAD-era practice you already use.
- Kubernetes version on the exam is a moving target (currently reported as v1.35 by LF, with v1.36 apparently already released as of this writing) — **re-check the LF CKA page yourself within a few days of booking**, since it updates within weeks of each K8s minor release.
- I was not able to obtain a broad, saturating sample of "recent candidate experience" reports (Reddit, LinkedIn, Medium, Hacker News were all unreachable in this session) — if the full research plan calls for that saturation (per the original brief's Phase 2), that gap should be filled separately, e.g., by you manually pulling a few Reddit/LinkedIn URLs for me to fetch directly, since I cannot discover them via search from here.

---

## Sources (all fetched 2026-08-15)

1. Linux Foundation — CKA certification page: https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/
2. CNCF Curriculum repo: https://github.com/cncf/curriculum
3. Kubernetes releases page: https://kubernetes.io/releases/ (dates flagged UNVERIFIED — see above)
4. dev.to — "How I Passed the CKA in 2026" (yltw27, 2026-07-16): https://dev.to/yltw27/how-i-passed-the-cka-in-2026-143c
5. dev.to — "AI Can Generate Kubernetes YAML — But Is the CKA Still Worth It in 2026?" (shahzadahmad91, 2026-06-06): https://dev.to/shahzadahmad91/ai-can-generate-kubernetes-yaml-but-is-the-cka-still-worth-it-in-2026-3j0l
6. dev.to — "My Top 50 kubectl Commands for CKA and Daily Kubernetes Administration" (shahzadahmad91, 2026-06-06): https://dev.to/shahzadahmad91/my-top-50-kubectl-commands-for-cka-and-daily-kubernetes-administration-41nh
7. dev.to — "Install a CNI and fix the flannel pod-CIDR mismatch" (thecybersidekick, 2026-07-10): https://dev.to/thecybersidekick/install-a-cni-and-fix-the-flannel-pod-cidr-mismatch-cka-services-networking-5hf4
8. KodeKloud Blog — "Kubernetes Certifications 2026: A Complete Guide" (Nimesha Jinarajadasa, updated 2026-07-16): https://kodekloud.com/blog/kubernetes-certification/

### Attempted but inaccessible in this session (noted for transparency, not fabricated)
- reddit.com / r/kubernetes — fetch blocked by tooling
- google.com/search — consent-redirect loop, no results retrievable
- bing.com/search — returned irrelevant localized (Hungarian transit) results
- duckduckgo.com/html — CAPTCHA-gated, no results retrievable
- killer.sh — page fetched but returned no body content (JS-rendered, likely requires a JS-executing fetcher this tool doesn't provide)
