# CKA Lab & Practice Platform Comparison

**Research date:** 2026-08-15
**Audience assumption:** CKAD-certified, rusty on CKA-specific admin skills (kubeadm, etcd, static pods, RBAC, NetworkPolicy, storage provisioning).

---

## Note on research method (read this first)

A prior draft of this report claimed the task was impossible because `WebSearch` is blocked by a Vertex AI organization-policy constraint (`constraints/vertexai.allowedPartnerModelFeatures`). **I independently re-confirmed that block is real** — every `WebSearch` call in this session failed with the identical `FAILED_PRECONDITION` error. That part of the prior draft was accurate, and open-ended discovery search genuinely is unavailable in this environment.

However, the prior draft's conclusion ("I cannot complete this task... no files were written") was too pessimistic. `WebFetch` (fetch-a-known-URL) and direct `curl` calls **do work**, and combined with GitHub's public search API I was able to retrieve and cross-check live content from most of the primary sources (CNCF, Linux Foundation docs, kubernetes.io, KodeKloud, Docker's Play-with-Kubernetes page). Two sites — **killer.sh** and **killercoda.com** — are pure client-side JavaScript SPAs with no server-rendered content, so `WebFetch`/`curl` returned only `<title>`/meta tags for those. Where that happened, it's called out explicitly below as **UNVERIFIED (could not fetch live content)**, and I've relied on well-established prior knowledge only where I'm confident it's stable, flagged accordingly.

No claim below is presented as "verified" unless I actually retrieved it from a live source during this session, with URL and fetch date given.

---

## 1. Verified official information

### CKA exam itself (baseline facts, for context)
Source: [CNCF – Certified Kubernetes Administrator](https://www.cncf.io/certification/cka/) (fetched 2026-08-15)

- Price: **$445 USD**, includes **one free retake**.
- Format: online, proctored, performance-based, command-line only. **2 hours** duration.
- Domain weights (current):
  - Cluster Architecture, Installation & Configuration — **25%**
  - Workloads & Scheduling — **15%**
  - Services & Networking — **20%**
  - Storage — **10%**
  - Troubleshooting — **30%**
- The CNCF page does not itself state the Kubernetes version or list killer.sh — it defers to the Candidate Handbook/FAQ (see below).

### Exam simulator (killer.sh) bundling and session mechanics
Source: [Linux Foundation Certification FAQ – CKA/CKAD/CKS](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks) (fetched 2026-08-15)

- Registering for a CKA exam includes access to a **killer.sh exam simulator**, made available via your training portal.
- **Two simulator attempts** per exam registration.
- **Each attempt grants 36 hours of access** from the time you activate it.
- Simulator questions are described as similar in style/difficulty to the real exam.
- **Important:** simulator access is explicitly **excluded from "CKA-SINGLE" (exam-only, no retake) purchases** — it comes with the standard/bundled registration. If you bought a bare single-attempt exam voucher, confirm you actually have simulator access before relying on it.

### Kubernetes version used in the exam — flag this as time-sensitive
Same FAQ source states: the exam environment "will be aligned with the most recent K8s minor version within approximately 4 to 8 weeks of the K8s release date," and at the time of my fetch the page text said the current exam environment runs **Kubernetes v1.35**.

**This is flagged UNVERIFIED-CURRENT rather than taken at face value**, because it doesn't reconcile cleanly with the official Kubernetes release table (see next section): v1.35 shipped ~December 2025, and v1.36 shipped 2026-06-09 — over 8 weeks before today's date (2026-08-15), which is past the FAQ's own stated 4–8 week alignment window. This could mean either (a) the FAQ text is stale/hadn't been updated at crawl time, or (b) the LF team is running behind their stated SLA. **Action for Nirbhay:** re-check the live FAQ page yourself within a week or two of booking/sitting the exam — do not study version-specific syntax assuming v1.35 vs v1.36 without confirming.

### Official Kubernetes release cadence (for cross-checking exam-version claims)
Source: [kubernetes.io/releases](https://kubernetes.io/releases/) (fetched 2026-08-15)

| Version | Latest patch (at fetch) | Release date | End of life |
|---|---|---|---|
| 1.36 | 1.36.2 | 2026-06-09 | 2027-06-28 |
| 1.35 | 1.35.6 | — (released ~Dec 2025) | 2027-02-28 |
| 1.34 | 1.34.9 | — | 2026-10-27 |
| 1.33 | 1.33.13 | — | 2026-06-28 |

- Kubernetes supports the **3 most recent minor releases** at any time.
- **v1.37 is the next upcoming release** (schedule tracked in the [kubernetes/sig-release repo](https://github.com/kubernetes/sig-release/tree/master/releases/release-1.37)).

### Official local learning-tool recommendations
Source: [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) (fetched 2026-08-15)

- **kind** (Kubernetes-in-Docker) — https://kind.sigs.k8s.io/ — requires Docker or Podman; good for fast multi-node clusters on a laptop.
- **minikube** — https://minikube.sigs.k8s.io/ — cross-platform, single- or multi-node.
- **kubeadm** — for building a "minimum viable, secure" cluster the way CKA's Cluster Architecture domain expects you to operate one. This is the most CKA-relevant of the three since the exam explicitly tests kubeadm-based cluster admin (join/upgrade nodes, etc.), unlike kind/minikube which abstract that away.

---

## 2. Platform-by-platform comparison

### killer.sh (official CNCF/LF exam simulator)
**Status: Verified (bundling/mechanics) + UNVERIFIED (page content/standalone pricing)**

- Confirmed via LF FAQ above: 2 sessions × 36 hours, bundled with standard CKA registration, excluded from CKA-SINGLE.
- I could **not** verify from live content whether killer.sh is purchasable **standalone** (without an exam registration) or at what price — killer.sh's site (`https://killer.sh`) is a pure JS SPA; both `WebFetch` and raw `curl` only returned the page `<head>` metadata:
  > "Linux Foundation CKS CKA CKAD CNPE LFCS Kubernetes Linux Exam Simulators / Example Questions / Practice Exam" — publisher "KLLR GmbH"
  No pricing, session-count, or Kubernetes-version text was retrievable. **Mark standalone pricing as UNVERIFIED** — check https://killer.sh directly in a real browser before assuming a price.
- Widely and consistently reported by the community (r/kubernetes, various blog walkthroughs) to closely mirror the actual exam UI (terminal, notes panel, question flagging) — this is **community-reported, not independently re-verified this session**.

### Killercoda (`killer-shell-cka` and related scenarios)
**Status: Mostly UNVERIFIED this session (SPA, no server-rendered content retrievable)**

- `https://killercoda.com` and `https://killercoda.com/killer-shell-cka` both returned only a client-rendered app shell via `curl`/`WebFetch` — confirmed metadata only: "Learn DevOps Linux Kubernetes CKS CKA CKAD Git Linux Programming," publisher "KLLR" (same publisher entity as killer.sh, per the `author` meta tag — this connection *is* directly verifiable from the raw HTML, fetched 2026-08-15).
- I confirmed via the **GitHub public API** that a `killercoda` GitHub org exists and is active (e.g. `github.com/killercoda/scenario-examples`), which supports (but doesn't fully prove) that Killercoda is a live, maintained platform as of fetch time.
- **Community-reported information (NOT verified live this session):** Killercoda is generally known as a free, browser-based, no-signup interactive scenario platform (successor to the old Katacoda), offering free CKA/CKAD/CKS-style scenarios built by the same team as killer.sh, useful for low-stakes command practice before paying for a real killer.sh session. Treat exact scope, current scenario list, and any usage limits as **UNVERIFIED** — confirm directly in-browser.

### KodeKloud CKA course
**Status: Verified (course structure) + UNVERIFIED (exact pricing)**

Source: KodeKloud CKA course page (fetched 2026-08-15) and KodeKloud Playgrounds page (fetched 2026-08-15)

- Course: **17 lessons / ~309 topics / ~25 hours of video**, hands-on labs embedded (no local setup needed), mock exams included, Discord/forum community access.
- Content updates reported on-page: **Helm Basics** and **Kustomize Basics** sections added January 2025; admission-controller lectures/labs added more recently.
- Lab environment version: page text at fetch time said labs were "most recently upgraded to version 1.33 (May 2026, in progress)." **Flag as possibly stale** for the same reason as the killer.sh version claim above — v1.36 has been out since June 2026 — so don't assume 1.33 is still current; check in-platform before your study session.
- **Pricing is paywalled/behind account context** — I could not retrieve an exact current price. Page referenced "up to 50% off" promotions and some free-enrollment content, but treat exact $ figures as **UNVERIFIED**.
- **KodeKloud free Playgrounds** (separate from the paid course, confirmed free, no course purchase required per page text): "Kubernetes Multi-Cluster," "Kubernetes multi-node (latest)," "Kubernetes single-node (latest)," plus extended variants bundling gVisor, HA etcd, Helm, Istio, CRI-O, EFK, Calico. Exact node counts, kubectl-access details, and session time limits were **not retrievable** from the fetched excerpt — page mentions playgrounds "can be extended for an additional period of time" implying a time limit exists, but the duration itself is UNVERIFIED.

### Play with Kubernetes (Docker/Tutorius) — **DEPRECATED, do not rely on this**
**Status: Verified directly from source HTML**

Source: raw HTML fetch of `https://labs.play-with-k8s.com/` (fetched 2026-08-15)

The live page itself carries this banner, quoted verbatim:

> "**Deprecation notice:** Play with Kubernetes will be unavailable starting March 1, 2026. Visit Docker Docs for supported labs and guides."

**This is a materially important, time-sensitive correction for anyone using older CKA study guides**: as of today (2026-08-15), Play with Kubernetes has been unavailable for over five months. Any older CKA prep material (blog posts, older KodeKloud/Udemy course videos, older Reddit threads) recommending `labs.play-with-k8s.com` as a free scratch environment is **out of date**. Docker's replacement pointer is https://docs.docker.com/guides/?tags=labs — I did not deep-dive that page's specific lab offerings in this session; treat as a lead to follow up, not a verified alternative.

### Local tooling: kind / minikube / kubeadm-on-VMs
**Status: Verified (official recommendation) + reasoning is mine, not sourced**

- kind and minikube are officially endorsed by kubernetes.io (see Section 1) for general learning/dev use.
- **For CKA specifically**, neither kind nor minikube is a great substitute for real practice, because the CKA Cluster Architecture domain (25% of the exam) tests kubeadm-based multi-node cluster operations (init, join, upgrade, certificate rotation, static pod manipulation on control-plane nodes) that kind/minikube deliberately abstract away or don't expose the same way a real kubeadm cluster does. This assessment is my own reasoning based on the verified exam-domain weightings and kubeadm's documented purpose, not a claim I sourced from a third party — flag it as **analysis, not a verified external claim**.
- A cheap, well-known way to get a real kubeadm cluster for practice: 2–3 VMs (local via multipass/VirtualBox, or cheap cloud VMs) + manual `kubeadm init`/`kubeadm join`. This is standard, uncontroversial CKA prep advice repeated across the ecosystem, but I did not re-verify a specific source for it this session — **community-reported / general knowledge**.

---

## 3. Summary table

| Platform | Cost | Verified this session? | CKA-relevance | Key caveat |
|---|---|---|---|---|
| killer.sh | Bundled w/ CKA reg. (2×36h); standalone price UNVERIFIED | Bundling: yes / Content: no (SPA) | High — mirrors real exam UI | Excluded from CKA-SINGLE purchases |
| Killercoda | Believed free | No (SPA, could not fetch) | Unknown scope — verify live | Same publisher (KLLR) as killer.sh, confirmed via meta tags |
| KodeKloud course | Paid, exact price UNVERIFIED | Structure: yes / Price: no | High — full course + mock exams | Lab K8s version claim may be stale |
| KodeKloud Playgrounds | Free | Partially (existence/list yes, limits no) | Medium — good for quick sandbox | Session time limits not confirmed |
| Play with Kubernetes | N/A | Yes — confirmed dead | **None — deprecated 2026-03-01** | Remove from any study plan referencing it |
| kind / minikube | Free | Yes (official docs) | Low-medium — not kubeadm-realistic | Doesn't replicate multi-node kubeadm admin tasks |
| Real VMs + kubeadm | Cost of VMs (often near-free locally) | N/A (general knowledge) | Highest fidelity to exam tasks | Requires manual setup time |

---

## 4. Recommendation for Nirbhay (given CKAD already held, rusty on admin specifics)

This is my synthesis, not a sourced claim:

1. Do NOT plan around Play with Kubernetes — it's gone. Drop it from any existing study plan or bookmarks.
2. Prioritize getting real kubeadm reps (VMs, 2–3 nodes) over kind/minikube for the Cluster Architecture (25%) and Troubleshooting (30%) domains specifically, since those are the two heaviest-weighted domains and the ones least well-simulated by kind/minikube.
3. Budget your two killer.sh sessions for the final 1–2 weeks before the exam (timed, exam-like) rather than early study — you already have the general K8s fluency from CKAD, so the simulator is better spent validating speed/muscle-memory on kubeadm/etcd/RBAC/NetworkPolicy tasks than on relearning basics.
4. Before committing to a Kubernetes-version-specific study resource (KodeKloud lab version, killer.sh version, etc.), re-check the live version claims yourself — this report found the version claims from both LF's FAQ and KodeKloud's course page potentially stale relative to the actual current release (v1.36 as of 2026-08-15). Version-specific flag/field syntax (e.g., API deprecations) does occasionally matter for CKA troubleshooting tasks.
5. Use KodeKloud's free Playgrounds for ad hoc command practice between paid resources — confirmed free and currently listed as active.

---

## 5. Sources (all fetched 2026-08-15 unless noted)

- CNCF CKA certification page — https://www.cncf.io/certification/cka/
- Linux Foundation Certification FAQ (CKA/CKAD/CKS) — https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks
- Kubernetes official release list — https://kubernetes.io/releases/
- Kubernetes 1.37 release tracking — https://github.com/kubernetes/sig-release/tree/master/releases/release-1.37
- Kubernetes official tools docs — https://kubernetes.io/docs/tasks/tools/
- killer.sh homepage (metadata only, SPA) — https://killer.sh
- Killercoda homepage / killer-shell-cka page (metadata only, SPA) — https://killercoda.com , https://killercoda.com/killer-shell-cka
- Killercoda GitHub org (existence check via GitHub API) — https://github.com/killercoda
- KodeKloud CKA course page — https://kodekloud.com/courses/certified-kubernetes-administrator-cka
- KodeKloud Playgrounds page — https://kodekloud.com/playgrounds
- Play with Kubernetes (deprecation banner, direct HTML) — https://labs.play-with-k8s.com/

### Explicitly could not verify / out of scope this session
- killer.sh standalone pricing and current Kubernetes version (SPA, no server-rendered content).
- Killercoda's exact current scenario catalogue, pricing (if any), and session limits (SPA, no server-rendered content).
- KodeKloud exact current subscription price.
- Docker's replacement labs at docs.docker.com/guides (only the pointer was found, not evaluated).
- Any Reddit/community-forum sentiment on these platforms in 2026 — `reddit.com` fetch was blocked in this environment ("Claude Code is unable to fetch from www.reddit.com"), and open discovery `WebSearch` is blocked at the infrastructure level for this session, so no community-forum cross-check was possible beyond what's labeled "community-reported / general knowledge" above.
