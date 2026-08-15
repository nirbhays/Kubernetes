# CKA (Certified Kubernetes Administrator) Exam — Verified Snapshot as of 2026-08-15

Fact-check pass on the original draft. Methodology: `WebSearch` is blocked in this environment (org-level Vertex AI policy disallows the `web_search` feature for this model — confirmed again during this review, same failure the draft author hit). All verification below was done via direct `WebFetch` against official Linux Foundation / CNCF / GitHub URLs, with most load-bearing claims corroborated by **two or more independent official pages**, matching the standard requested. Nothing here comes from third-party blogs, Reddit, or exam-dump sites.

Every numbered fact below was re-fetched fresh in this session (2026-08-15) rather than trusted from the draft. Where my fetch matched the draft, I've marked it **Confirmed**. Where I found a nuance, correction, or inability to verify, I've called it out explicitly.

---

## Verified Official Information

### Exam Domains & Weightings
**Confirmed** — identical across LF program page and CNCF page, re-fetched independently:

| Domain | Weight |
|---|---|
| Troubleshooting | 30% |
| Cluster Architecture, Installation & Configuration | 25% |
| Services & Networking | 20% |
| Workloads & Scheduling | 15% |
| Storage | 10% |

Sources: [training.linuxfoundation.org CKA page](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/) (page reports `dateModified: 2026-07-27T17:48:59+00:00`, re-confirmed this session), [cncf.io/training/certification/cka](https://www.cncf.io/training/certification/cka/) (re-fetched this session, same table).

### Kubernetes Version Used in the Exam
**Confirmed**, and now on stronger footing than the draft — the draft treated "v1.35" as coming from one FAQ line; I independently re-fetched both the LF program page *and* the FAQ page separately and both state the environment runs **v1.35**, with updates "within approximately 4–8 weeks of new [Kubernetes] releases."

Curriculum version history, verified via direct commit lookups in [github.com/cncf/curriculum](https://github.com/cncf/curriculum/commits/master) (each date pulled from an individual commit, not just the commit-list summary):

| Curriculum version | Commit date |
|---|---|
| v1.32 | 2025-02-17 |
| v1.33 | 2025-07-03 |
| v1.34 | 2025-10-28 |
| v1.35 (current) | 2026-03-03 |

**Correction to the draft:** the draft/CNCF page calls this cadence "quarterly." The actual gaps are ~4.5, ~3.9, and ~4.0 months — closer to **"roughly 3–4 times a year"** than strictly quarterly (91 days). Minor wording nitpick, but worth knowing exam content could shift slightly off a calendar-quarter cadence. The versioning convention itself (major.minor of the curriculum doc tracks the Kubernetes major.minor it targets) is confirmed via the repo's own README text.

### Exam Duration
**Confirmed: 2 hours.** Identical wording on LF program page, CNCF page, and FAQ, all re-fetched this session.

### Passing Score
**Confirmed: 66%.** Direct quote re-verified from the FAQ: "For the CKA Exam, a score of 66% or above must be earned to pass."

### Number of Tasks
**Confirmed: 15–20 performance-based tasks**, per direct quote re-fetched from the [tips-cka-and-ckad](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad) page: "15-20 performance-based tasks... within a 2-hour timeframe." The core LF program page and FAQ still don't state this number themselves — it's official LF documentation, just on a secondary (prep-tips) page rather than the main handbook page. Treat as reliable but not from the single most-canonical source.

### Exam Delivery Platform
**Confirmed.** Proctoring platform is **PSI Bridge**; re-fetched the handbook root page directly and the literal page title is: *"Linux Foundation Certification Exam: Candidate Handbook (using PSI BRIDGE Proctoring platform)."*

Environment details, re-confirmed via direct fetch of the tips page:
- Browser-hosted terminal with SSH access to designated hosts
- Pre-installed: `kubectl` (aliased to `k`, with bash autocompletion), `yq`, `curl`, `wget`, man pages
- `sudo -i` available for elevated privileges

### Allowed Documentation During Exam
**Confirmed**, re-fetched directly from [certification-resources-allowed](https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed):
- `kubernetes.io/docs/` — in-page search allowed, but opening external search results is prohibited
- `kubernetes.io/blog/`
- `helm.sh/docs/`
- `gateway-api.sigs.k8s.io/` — explicitly labeled **CKA only**, not permitted for CKAD (re-confirmed)
- Man pages, distro-installed docs (`/usr/share/...`), installable distro packages
- Task-specific docs provided in the exam's own "Quick Reference" box (new detail not in the draft — worth knowing: some questions link you directly to the relevant doc page)

**Additional detail beyond the draft:** CKS-only extra allowed docs, confirmed by direct fetch, are more extensive than the draft listed — **Falco, etcd, NGINX Ingress Controller, Cilium, Istio, and Bom** (the draft omitted Istio). Not relevant to CKA prep itself, but flagging since the draft's CKS list was incomplete.

### Retake Policy
**Confirmed.**
- $445 list price includes **one free retake** (i.e., two total attempts per registration) — consistent phrasing across LF and CNCF pages.
- Renewal: if you pass a renewal/retake exam, the certification is valid for **another 2 years** from that pass date — confirmed via direct FAQ quote: "the renewed certification will remain current for a further 2 years effective from the date the exam is passed."

**New pricing detail found (not in draft):** re-fetch of the LF program page surfaced bundle pricing not mentioned in the draft:
- Exam only: $445
- Exam + THRIVE-ONE subscription: $625
- Exam + Kubernetes Fundamentals course: $645

### Killer.sh Simulator — Question Count Now CONFIRMED (draft had this as UNVERIFIED)
The draft flagged "17 questions per attempt" as unverified, sourced from a single AI-summarized fetch. On re-fetch in this session, **the LF program page itself states this directly**: "Each simulator session contains 17 questions, with a different set of questions per attempt, providing graded results." This is now corroborated by an official page, not just an AI paraphrase — **upgrading this from UNVERIFIED to Confirmed.**

Other simulator facts, re-confirmed via both the LF program page and the FAQ page independently:
- Two simulator attempts per registration
- 36 hours of access per attempt, from time of activation
- Simulator access is bundled with a full exam purchase, not with retake-only purchases (this specific exclusion clause I could **not** re-find explicit wording for in either page fetched this session — **downgrading to UNVERIFIED**; it's plausible/commonly repeated but I did not see it stated in the two official pages I fetched)

Note: killer.sh itself still returns only a page title with no body content on fetch (same result the draft author got) — its own site is not usable as a source here.

### Remote Proctoring Requirements
**Confirmed**, re-fetched directly from the handbook's ID-authentication and exam-rules-and-policies sub-pages:
- **ID:** valid, unexpired, government-issued **original physical** document (no photocopies/digital), name + photo + signature or biometric data; non-Latin-script names entered in native script, not romanized. Confirmed acceptable ID types include passports, driver's licenses, national ID cards, alien registration cards, and (notably, a detail not in the draft) **Japanese Basic Resident Registers and My Number Cards** as explicitly named acceptable documents.
- **Minors (16–18):** parent/guardian must submit a "Parental Release for Testing of Minors" form **at least 2 weeks before the exam date** (this lead-time detail is new vs. the draft, which didn't mention it), present valid student ID, and have the guardian present ID + give verbal consent at PSI check-in.
- **Environment:** private, quiet, well-lit room, no one else present (ADA service animals excepted), no bright light/windows behind candidate, desk clear of notes/electronics, public spaces prohibited.
- **Conduct:** visible on webcam at all times, no leaving desk without proctor permission, no talking/reading aloud, no communication with anyone but the proctor, no food (clear liquids in a label-free clear container only), no gum, no earpieces/smartwatches/phones/smart glasses (medical exceptions require prior approval), no covering face.
- **Enforcement:** sessions recorded/reviewed, zero-tolerance policy, violations can revoke passing scores and restrict future eligibility.
- **System requirements, re-confirmed with more precision than the draft:** single monitor only (**dual monitors explicitly unsupported**, not just "not recommended"), 15"+ screen, 1080p recommended, webcam + microphone required, and a hard rule that **"you cannot take an exam using a virtual machine even though the compatibility check may not display any issues."** Also newly confirmed: connectivity requirements specifically mention **HTTPS access to AWS S3 endpoints** must not be blocked by corporate firewalls — relevant for anyone testing from a corporate laptop/VPN (worth flagging given the reader's employer context).

### Terminal/Browser Restrictions
**Confirmed**, with one correction to the draft:
- Copy = **Ctrl+Shift+C**, Paste = **Ctrl+Shift+V** inside the Linux terminal application itself. My re-fetch did **not** turn up the draft's specific claims of "close tab = Ctrl+Alt+W" or "locate cursor = Ctrl+Alt+K" as distinct documented keybindings — I could not independently confirm those two on re-fetch. **Marking those two specific keybindings as UNVERIFIED** (they may exist in the full handbook but didn't surface in my fetch of the tips page).
- **Insert key is disabled/prohibited** — confirmed directly: "The INSERT key is prohibited within the Remote Desktop." Use `i` to enter insert mode and `Esc` to exit in vi-style editors — confirmed.
- Note also (re-confirmed): for the outer remote-desktop chrome (as opposed to the inner Linux terminal app), standard Windows shortcuts (Ctrl+C/V) apply — a distinction the draft didn't clearly separate.

---

## Community-Reported / Unverified Information

These items could not be pinned to an official source on re-fetch, or the official source's wording was ambiguous. Treat as directionally useful but not exam-day-certain:

- **UNVERIFIED:** Content-level differences between curriculum v1.34 and v1.35 (e.g., specific objectives added/removed). The PDF itself is not machine-readable via fetch in this environment; no changelog was found describing line-item deltas between versions.
- **UNVERIFIED:** The claim that killer.sh simulator access is excluded specifically from "retake-only" purchases — plausible and commonly repeated in community writeups, but not found verbatim in the two official pages fetched this session.
- **UNVERIFIED:** Specific terminal keybindings "close tab = Ctrl+Alt+W" and "locate cursor = Ctrl+Alt+K" from the draft — not found on re-fetch of the tips page; may be in a different handbook sub-page not fetched here.
- **Community-reported (exam-experience forums, Reddit r/kubernetes, exam-dump-adjacent blog posts — NOT independently checked in this session):** anecdotal claims about typical task difficulty distribution, which specific troubleshooting scenarios recur most often, typical time pressure per task, and whether Gateway API questions actually appear in practice despite being an allowed doc. None of this was verified here — flagging only because such claims circulate widely and should not be treated as official just because they're repeated often.

---

## Sources (all re-fetched directly in this session, 2026-08-15)

- https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/ (`dateModified: 2026-07-27T17:48:59+00:00`)
- https://www.cncf.io/training/certification/cka/
- https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks
- https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad
- https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed
- https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2 (handbook root — title confirms "PSI BRIDGE Proctoring platform")
- https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/candidate-identification-and-authentication
- https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-rules-and-policies
- https://github.com/cncf/curriculum (repo root + README versioning convention)
- https://github.com/cncf/curriculum/commits/master (commit-by-commit dates for v1.32, v1.34, v1.35)
- GitHub commit search for v1.33 commit (commit `4722108...`, dated 2025-07-03, author zuzannapn)
- https://killer.sh (still returns only a page title on fetch — not independently substantive as a source; simulator facts sourced from LF pages instead)

## Methodology Note

`WebSearch` failed with the same Vertex AI org-policy error the draft reported (`FAILED_PRECONDITION`, `vertexai.allowedPartnerModelFeatures` blocking `web_search` for this model). All verification in this pass was done via `WebFetch` against the official URLs above, fetched fresh in this session rather than reused from the draft's earlier fetches. Where a re-fetch surfaced new detail, contradicted the draft, or failed to reproduce a draft claim, it's called out explicitly above rather than silently folded in.
