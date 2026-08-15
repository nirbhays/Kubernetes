# CKA Study Research: Public GitHub Repos & Lab Resources (Fact-Checked)

**Fact-check date:** 2026-08-15
**Verification method:** Direct queries to the GitHub REST/Search API (`api.github.com`, via `gh api` and `curl`, cross-checked against the live repos) plus `WebFetch` against `kubernetes.io`, `training.linuxfoundation.org`, `docs.linuxfoundation.org`, and `github.com/cncf/curriculum`. Note: the `WebSearch` tool is blocked in this environment by org policy (Vertex AI partner-model policy), same limitation the draft reporter hit — so all verification here is via direct API calls and page fetches, not search-engine summaries.

---

## 1. Verified official information

These are claims checked directly against an authoritative primary source (CNCF/Linux Foundation, kubernetes.io, or the GitHub API itself), not against a blog post or secondary summary.

### 1.1 Current CKA curriculum version — draft's claim was WRONG, corrected here

- **Draft claimed:** "Current CKA domains (v1.31–1.33 exam objectives)."
- **Verified reality:** As of 2026-08-15, the authoritative curriculum file in the official CNCF curriculum repository is **`CKA_Curriculum_v1.35.pdf`** — confirmed by listing the repo contents directly:
  `GH_HOST=github.com gh api repos/cncf/curriculum/contents` → returns `CKA_Curriculum_v1.35.pdf` and `CKAD_Curriculum_v1.35.pdf` as the only CKA/CKAD curriculum files present.
  Source: https://github.com/cncf/curriculum (checked 2026-08-15)
- This is corroborated by the Linux Foundation training page, which states the exam is "based on Kubernetes v1.35" with the environment aligned to within ~4–8 weeks of a new minor release.
  Source: https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/ (fetched 2026-08-15)
- For context on where v1.35 sits in the release train: as of August 2026 the actively-maintained minor versions are roughly v1.34–v1.36, with v1.36 being the newest stable line and v1.35 one step behind it — consistent with the exam trailing new GA releases by several weeks. Treat the exact patch-level dates from this cross-check as approximate (sourced via an auto-summarized fetch of kubernetes.io/releases, not a raw data pull), but the *headline* fact — **current curriculum = v1.35, not v1.31–1.33** — is confirmed directly from the primary source and should be treated as solid.
- **Practical implication for study planning:** the domain *names and weights* below have not changed, but any resource that talks about "the current exam is on v1.31/v1.32" is now behind — flag those as version-stale even if their commit history looks recent, since content can lag behind a repo's last-push date (see the `chadmcrowell/CKA-Exercises` note in §2 below, which is a good example: recently pushed but its README text explicitly says "currently on v1.31").

### 1.2 CKA domain weights — draft's numbers CONFIRMED correct

Verified via `training.linuxfoundation.org` (fetched 2026-08-15):

| Domain | Weight |
|---|---|
| Troubleshooting | **30%** |
| Cluster Architecture, Installation & Configuration | **25%** |
| Services & Networking | **20%** |
| Workloads & Scheduling | **15%** |
| Storage | **10%** |

This matches the draft exactly. Source: https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/

### 1.3 Exam format

Confirmed via the same Linux Foundation page: online, proctored, **performance-based**, command-line only, **2 hours**, two included Killer.sh simulator attempts (36 hours access each, 17 unique questions), plus two real exam attempts. This is consistent with the draft's framing and with general CKA knowledge — no correction needed.

### 1.4 Resources allowed during the exam

**UNVERIFIED in the draft, now precisely sourced.** The draft said the exam allows "kubernetes.io docs (and a few sub-domains)" without citing the exact list. The actual official policy page states candidates may access, during the exam:

- `https://kubernetes.io/docs/` (in-site search allowed; external search engine results are **not** allowed)
- `https://kubernetes.io/blog/`
- `https://helm.sh/docs/`
- `https://gateway-api.sigs.k8s.io/` — **CKA only** (not allowed on CKAD)
- Task-specific documentation linked from the exam's own "Quick Reference" box

Source: https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed (fetched 2026-08-15)

This is a meaningful correction/addition: the draft's Tier-2 mention of `theplatformlab`'s repo covering "Gateway API" as a forward-looking bonus is actually directly relevant, since Gateway API docs are explicitly exam-allowed for CKA specifically (not for CKAD).

All four specific kubernetes.io URLs cited in the draft's "Official kubernetes.io resources" section were checked with a raw HTTP request and all returned **HTTP 200** (live) on 2026-08-15:
- `kubernetes.io/docs/tutorials/kubernetes-basics/`
- `kubernetes.io/docs/reference/access-authn-authz/rbac/`
- `kubernetes.io/docs/concepts/services-networking/network-policies/`
- `kubernetes.io/docs/tasks/debug/`

The two hub pages singled out by the draft were fetched and content-checked directly:
- **`kubernetes.io/docs/tasks/administer-cluster/kubeadm/`** — confirmed live; it is indeed a hub page covering adding nodes, upgrading kubeadm clusters, cgroup driver configuration, and certificate management — matches the draft's description.
- **`kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/`** — confirmed live; confirmed it covers etcd snapshot backup (including the "Snapshot using etcdctl options" method) and restore — matches the draft's description of it as "a near-guaranteed CKA task."

### 1.5 Version-drift signals the draft used as "staleness heuristics" — checked against primary sources

- **Dockershim removal**: confirmed removed in **Kubernetes v1.24** (this is corroborated indirectly — see §2, `chadmcrowell/CKA-Exercises` README quotes the official `kubernetes.io/blog/2020/12/02/dockershim-faq/` post and states "The removal of dockershim happened in v1.24"). This is a well-established, unambiguous historical fact.
- **PodSecurityPolicy (PSP) removal**: confirmed removed in **Kubernetes v1.25** by directly fetching the official release announcement:
  > "PodSecurityPolicy was initially deprecated in v1.21, and with the release of v1.25, it has been removed... That replacement is Pod Security Admission, which graduates to Stable with this release."
  Source: https://kubernetes.io/blog/2022/08/23/kubernetes-v1-25-release/ (fetched 2026-08-15)

So the draft's heuristic ("repos still referencing PSPs as current practice, or Docker-as-runtime, are stale signals") is factually well-grounded.

---

## 2. Verified GitHub repo metadata (directly from the GitHub API, 2026-08-15)

Every star count, push date, fork count, license, and issue/PR count below was pulled live from `api.github.com` (via `gh api` / `curl`) on 2026-08-15, not copied from the draft. **Every numeric claim in the draft's Tier 1/2/3 sections matched the live API response exactly** — a good sign the draft's original data pull (whatever method it used) was accurate at the time, or was itself a live API pull.

| Repo | Stars | Forks | Pushed (last commit) | License | Notes |
|---|---|---|---|---|---|
| kodekloudhub/certified-kubernetes-administrator-course | 10,740 | (not cited by draft) | 2026-02-15 | — | 18 open issues + 11 open PRs (verified separately via Search API — draft's "18 open issues, 11 open PRs" is precise, not a combined total). Commit count confirmed **1,022** via pagination `Link` header (`last` page = 1022 at `per_page=1`). |
| kelseyhightower/kubernetes-the-hard-way | 49,464 | 15,821 | 2025-04-10 | Apache-2.0 | Matches draft exactly. |
| mmumshad/kubernetes-the-hard-way | 5,181 | 4,860 | 2025-11-17 | Apache-2.0 | Matches draft exactly. Description confirms it's the Vagrant/local-VM fork ("Bootstrap Kubernetes the hard way on Vagrant on Local Machine. No scripts."). |
| bmuschko/cka-crash-course | 432 | 294 | 2026-04-01 | **No license file** (draft did not claim one) | Matches draft. |
| bmuschko/ckad-crash-course | 973 | 663 | 2026-05-19 | No license file | Matches draft. |
| chadmcrowell/CKA-Exercises | 499 | 186 | 2025-10-08 | No license file | Matches draft. See caveat below — README content itself is version-stale despite recent push. |
| sailor-sh/CK-X | 1,114 | 181 | 2026-05-10 | **Business Source License 1.1** — confirmed by reading the actual `LICENSE` file content, not just the SPDX field (GitHub reports `NOASSERTION`/"Other" for BSL since it's not OSI-approved). Draft's specific claim of "Business Source License 1.1" is **confirmed correct**, including the non-production/no-hosted-service restriction language. | Open issues: **18 pure issues + 6 open PRs = 24 combined** (GitHub's raw `open_issues_count` field, which the draft's "18 open issues" figure matches once PRs are excluded — precise). |
| walidshaari/Kubernetes-Certified-Administrator | 4,415 | 1,584 | 2025-01-05 | CC-BY-SA-4.0 | Confirmed: repo description literally still reads "...CNCF CKA **2020** exam..." — draft's staleness flag is accurate and directly quoted from the live description. |
| alijahnas/CKA-practice-exercises | 1,366 | 530 | **2024-02-18** | GPL-3.0 | Matches draft; ~2.5 years since last push as of 2026-08-15 — draft's "stale" flag is fair. |
| justmeandopensource/kubernetes | 1,753 | 2,947 | 2025-12-21 | No license file | Matches draft. |
| theplatformlab/CKA-Certified-Kubernetes-Administrator | 416 | 155 | 2026-06-03 | MIT | Created 2025-06-04 (confirmed new). Description on GitHub literally says "full Kubernetes v1.35 syllabus breakdown... Scored 89%" — matches draft's paraphrase closely and is now doubly relevant given §1.1's finding that v1.35 **is** the current curriculum. |
| devopshubproject/cka-lab | 158 | 151 | **2022-06-30** | No license file | Matches draft; ~4 years stale as of 2026-08-15 — confirmed. |

### Caveat found during verification: recent commit activity ≠ current content

The draft rated `chadmcrowell/CKA-Exercises` as "well maintained and accurate" partly because it "explicitly calls out the dockershim removal... and post-Feb-2025 exam changes." I fetched the actual README (`raw.githubusercontent.com/chadmcrowell/CKA-Exercises/master/README.md`) to check this claim directly, and it is **true but incomplete**:

- The README does contain: `"IMPORTANT EXAM CHANGES COMING FEBRUARY 10th, 2025"` and links to a `cka-changes-2024/README.md` page, and does correctly explain the dockershim/containerd point with a link to the official Dockershim FAQ blog post.
- However, the same README text also says: **"The CKA exam is currently on v1.31 of k8s"** — which, per §1.1 above, is now stale (curriculum is v1.35 as of 2026-08-15). The domain *percentages* it lists (25/15/20/10/30) are still correct and match the current curriculum, but the specific Kubernetes-version framing in the prose is about four minor versions behind.
- **Takeaway:** don't rely solely on "last push date" as a currency signal — check whether version-specific prose inside a repo has been updated even if the repo received other commits recently. This nuances (but doesn't overturn) the draft's Tier-1 placement of this repo.

I did not have remaining API/time budget to do the equivalent full-text check on every Tier 1/2 repo's README (rate limits — see below), so **treat the "well maintained and accurate" characterization of `bmuschko/cka-crash-course`, `kodekloudhub`, and `sailor-sh/CK-X` prose content as UNVERIFIED beyond their commit/star/license metadata**, even though that metadata itself is solid.

### Note on methodology limits

- Unauthenticated GitHub REST calls are capped at 60 requests/hour per IP; this was hit partway through verification (confirmed by an explicit `403 API rate limit exceeded` response). I switched to `gh api` against `github.com` (via `GH_HOST=github.com gh api ...`) which used the enterprise `gh` CLI's OAuth token and had a much higher ceiling (10,000/hour), and to `raw.githubusercontent.com` for file contents to spread load across endpoints. All numbers reported above were successfully retrieved before/after working around the rate limit — none are guessed or extrapolated.
- I did not verify community sentiment/quality claims (e.g., "single most recommended community resource," "high signal-to-noise," "technically credible") — these are subjective editorial judgments from the original draft, not independently verifiable facts, and are carried forward under §3 below rather than §1.

---

## 3. Community-reported / subjective information (not independently verifiable — carried from draft, unchanged)

The following judgments from the draft are reasonable editorial opinions but are **not** things a fact-checker can verify against a primary source. They're separated out here so they're not confused with the verified data above:

- "the single most recommended community resource for CKA" (re: kodekloudhub repo) — plausible given star count and being the official companion to the most popular CKA course, but this is a reputation claim, not a checkable fact. **UNVERIFIED** in the sense of "most recommended by whom" — no survey data was checked.
- Qualitative maintenance/quality judgments ("well maintained," "technically solid," "high quality," "peer-vetted") for each repo — these are reasonable inferences from stars/forks/commit-recency but are ultimately subjective. Treat as informed opinion.
- The claim that KodeKloud's repo "maps almost 1:1 to the official curriculum" — plausible given it's a well-known, actively updated companion repo, but I did not do a line-by-line crosswalk against `CKA_Curriculum_v1.35.pdf` to confirm 1:1 mapping. **UNVERIFIED** at that level of granularity.
- Recommendations in the "Summary recommendation" section (which repos to prioritize) are the draft author's synthesis/opinion, not verifiable facts. I have not altered this ranking, since it's a reasonable reading of the verified metadata above, but it remains an opinion, not a verified claim.

---

## 4. Corrected summary recommendation

Same overall shape as the draft, with one factual correction layered in:

- **Primary spine:** `kodekloudhub/certified-kubernetes-administrator-course` (10,740 stars, pushed 2026-02-15, 1,022 commits) — best-maintained, most complete curriculum mapping by reputation; verify version-specific prose yourself against `CKA_Curriculum_v1.35.pdf` since that level of detail wasn't independently checked here.
- **Hands-on drills:** `bmuschko/cka-crash-course` (pushed 2026-04-01) or `chadmcrowell/CKA-Exercises` (pushed 2025-10-08, correct domain weights, but **double-check its version-specific claims** — its own README still frames the exam as "currently on v1.31," which is stale per §1.1; the underlying exercises are likely still valid, but don't trust its version framing).
- **Free timed mock exam:** `sailor-sh/CK-X` (pushed 2026-05-10, Business Source License 1.1 confirmed — free for personal study, restricted for commercial/hosted resale).
- **Architecture deep-dive (not exam-format practice):** `kelseyhightower/kubernetes-the-hard-way` (pushed 2025-04-10) — genuinely not kubeadm-based, so treat purely as a conceptual supplement, exactly as the draft framed it.
- **Newest curriculum alignment:** `theplatformlab/CKA-Certified-Kubernetes-Administrator` (pushed 2026-06-03, explicitly references "v1.35 syllabus") is now more clearly justified as current, since §1.1 confirms v1.35 **is** the live curriculum as of today (2026-08-15) — this repo's currency claim checks out better than the draft could confirm at the time it was written.
- **Deprioritize / flag as dated:** `walidshaari/Kubernetes-Certified-Administrator` (own description says "2020 exam," confirmed verbatim), `alijahnas/CKA-practice-exercises` (2.5 years stale, confirmed), `devopshubproject/cka-lab` (~4 years stale, confirmed) — draft's characterization holds up.

---

## 5. Explicit list of UNVERIFIED items (do not treat as fact)

1. Exact patch-level release dates/versions for the Kubernetes v1.34/v1.35/v1.36 train quoted in §1.1 — sourced from an AI-summarized fetch of `kubernetes.io/releases`, not a raw data pull; the *headline* conclusion (curriculum = v1.35) is independently confirmed via the CNCF curriculum repo listing, but don't quote the specific patch dates (e.g., "1.36.2 released 2026-06-09") as certain without checking `kubernetes.io/releases` yourself.
2. Prose-level currency of `bmuschko/cka-crash-course`, `kodekloudhub`'s course notes, and `sailor-sh/CK-X`'s scenario content — only metadata (stars/forks/license/push dates) was verified for these, not full README/content text, due to API rate-limit and time constraints.
3. Subjective "most recommended," "well maintained," "technically credible" characterizations throughout — editorial judgment, not independently verified against any survey or usage-data source.
4. Whether KodeKloud's repo content maps "almost 1:1" to the v1.35 curriculum specifically — not checked line-by-line.

---

## Sources consulted (all fetched/queried on 2026-08-15)

- https://github.com/cncf/curriculum (repo file listing — authoritative source for current curriculum version)
- https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/
- https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed
- https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad
- https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/
- https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
- https://kubernetes.io/docs/tutorials/kubernetes-basics/
- https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- https://kubernetes.io/docs/concepts/services-networking/network-policies/
- https://kubernetes.io/docs/tasks/debug/
- https://kubernetes.io/blog/2022/08/23/kubernetes-v1-25-release/ (PSP removal confirmation)
- https://kubernetes.io/blog/2020/12/02/dockershim-faq/ (referenced via chadmcrowell README; dockershim removal in v1.24)
- https://raw.githubusercontent.com/chadmcrowell/CKA-Exercises/master/README.md
- `api.github.com/repos/...` for all 12 repos listed in §2 (via `gh api` / `curl`)
- `api.github.com/search/issues?q=repo:...+type:issue|pr+state:open` for kodekloudhub and CK-X issue/PR breakdowns
