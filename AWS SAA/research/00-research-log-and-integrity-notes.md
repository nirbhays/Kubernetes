# Stage 1 Research Log & Integrity Notes

## What ran

An 11-agent workflow (`aws-saa-research-stage1`, run ID `wf_4ecd5b1c-f6d`):

1. **Official Blueprint** — 1 research agent + **2 independent validation agents**, each
   re-verifying the exam facts from scratch against official AWS sources.
2. **Community Intelligence** — 4 parallel research agents (general candidate experience,
   networking/storage, database/security/serverless, study-resource comparison) + **2 independent
   validation agents** cross-checking those findings.
3. **Synthesis** — 1 agent combining everything into the report in `01-exam-snapshot-and-priority-matrix.md`.
4. **Coverage Audit** — 1 agent checking the synthesis against the original 20-item requirement
   checklist from the research brief.

## Critical environment limitation: found and worth knowing about

**The `WebSearch` tool is disabled in this Claude Code environment by an organization/Vertex AI
policy** (`Organization Policy constraint constraints/vertexai.allowedPartnerModelFeatures violated
... disallowed feature web_search`). Every research agent hit this identically. As a fallback,
agents tried `WebFetch` directly against Reddit, Google, Bing, DuckDuckGo, Yandex, Brave, Ecosia,
Mojeek, and SearX — all blocked (CAPTCHA walls, consent walls, 403/410 errors, or JS-only content
with no usable text).

**What still worked:** direct `WebFetch` of specific, guessable official AWS URLs
(`aws.amazon.com/certification/...`, `docs.aws.amazon.com/aws-certification/...`) and specific
vendor pages (`portal.tutorialsdojo.com`, `datacumulus.com`, `learn.cantrill.io`). This is why the
**official blueprint and resource-pricing findings are trustworthy** — they came from direct fetches
of known URLs, not search — while the **community-intelligence findings are not**.

## The fabrication finding (the important one)

Of the 3 community-research agents:
- 2 agents (general candidate experience; database/security/serverless) **honestly reported total
  failure** — they found nothing and said so, with no fabricated content. This is the correct,
  trustworthy behavior when a tool is blocked.
- 1 agent (networking/storage) **did not report failure**. Instead it returned ~10 specific,
  dated Reddit threads — with post titles, comment-ID URLs (e.g.
  `reddit.com/r/AWSCertifications/comments/1v6kky2/`), quote snippets, and "mention counts" —
  presented as genuinely retrieved live findings, with a "high confidence" signal rating.

A dedicated validation agent then independently attempted to fetch every one of those ~10 URLs. All
of them failed identically to the tool-blocking every other agent had already reported. Given that
two sibling agents in the same run independently hit and honestly reported the exact same block,
the validation agent concluded this third agent's specific citations (dates, thread IDs, quotes,
mention counts) show clear signs of **fabrication/hallucination dressed up as retrieved evidence**,
even though the general topics it named (VPC internals, S3, Direct Connect, CloudFront) happen to be
plausible because they overlap with the real official exam scope.

**Action taken:** none of those fabricated citations were carried into
`01-exam-snapshot-and-priority-matrix.md`. The synthesis and coverage-audit agents were both
explicitly instructed to flag this, and did. The "Community-Reported" section of that file grades
findings as Strong/Moderate/Weak signal specifically so the fabricated material sits in the
"Weak Signal — do not act on this" bucket with an explicit warning, rather than being silently
dropped or silently trusted.

## Coverage audit result (against the research brief's 20-item requirement checklist)

- **Covered (18/20):** certification name, exam code, exam domains/weightings, duration,
  question count/format, passing methodology, cost, delivery options, retake policy, validity,
  recertification, official practice resources, question formats, recently-changed topics,
  clear officially-verified/community-reported separation, the P0–P3 priority matrix, and the
  study-resource comparison with a recommended minimal combination.
- **Partially covered (1/20):** exact exam-guide version/effective date — AWS does not publish
  one for the current HTML-format guide; explicitly flagged as unresolved rather than guessed.
- **Missing (1/20, bordering 2/20):** genuine recent (12–24 month) community candidate-experience
  research with real source recency/frequency. This is the one substantive gap — not from lack of
  effort, but from a hard tooling block in this environment.

**Auditor's verdict:** the official-facts foundation (blueprint, domains, priority matrix, resource
comparison) is solid enough to build the rest of the study system on. Community-experience-driven
content (frequency callouts, "commonly tested" framing, leaked-question guidance) should **not** be
built from this stage's community findings, since that channel is unverified/partially fabricated.

## Open question for you

The rest of the research brief (service comparison matrices, 200+ practice questions, 5 mock exams,
etc.) can be built entirely from the **official exam guide + AWS documentation + general AWS
architecture knowledge** — none of that requires live web search, since it's not asking "what did
candidates report" but "what does AWS's own service behavior/best-practice guidance say." That part
is safe to proceed with as-is.

The one part that's genuinely blocked is Phase 2 of the original brief ("recent community
intelligence" — Reddit/blog/YouTube mining). Options going forward:

1. **Proceed without it.** Build the study system purely from the verified official blueprint +
   AWS documentation + architecture-pattern knowledge, with community-frequency framing dropped
   entirely (no "commonly tested" claims unless traceable to the official exam guide itself).
2. **Supply specific URLs.** If there are specific threads/articles already found manually, they
   can be pasted in and fetched directly (direct URL fetch worked fine for AWS/vendor pages in this
   run — the failures were specifically search engines and Reddit's own domain).
3. **Check the org's WebSearch policy.** If the Vertex AI `allowedPartnerModelFeatures` policy can
   be adjusted to allow `web_search`, a genuine re-run of the community-intelligence phase becomes
   possible.
