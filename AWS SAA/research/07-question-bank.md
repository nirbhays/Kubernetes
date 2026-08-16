# AWS SAA-C03 — Original Practice Question Bank (200+ Questions)

*These are original practice questions modeled on the current SAA-C03 exam domains and scope, not real/leaked exam content, each independently quality-audited for single-best-answer integrity.*

## Domain 1: Design Secure Architectures (30%)

### Question 1 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A retail company's IAM user "priya" has an identity-based policy attached via her group membership that grants `s3:*` on all buckets, since she's a member of the "data-engineers" group. Separately, a specific S3 bucket containing terminated-employee records has a bucket policy with an explicit `Deny` statement blocking `s3:GetObject` for every principal except two named compliance-team roles. Priya attempts to read an object in that bucket and receives `Access Denied`.

**Options:**
A. This is a misconfiguration — since Priya's IAM policy explicitly allows `s3:*`, AWS should grant access and the bucket policy is only advisory.
B. An explicit `Deny` in any applicable policy (bucket policy, identity policy, SCP, or permission boundary) always overrides any `Allow` found elsewhere in the evaluation, regardless of which policy type grants the allow.
C. Bucket policies only affect principals outside the bucket owner's own AWS account, so Priya's same-account access should not be affected by it.
D. `s3:*` in an IAM policy does not actually include `s3:GetObject`, so Priya never had read access in the first place.

**Correct answer(s):** B

**Why correct:** AWS IAM's policy evaluation logic is deny-by-default, and if *any* applicable policy in the evaluation set contains an explicit `Deny` that matches the request, that deny wins over any `Allow` from any other policy — identity-based, resource-based, SCP, or permission boundary.

**Why each wrong option is wrong:** A is factually backwards — bucket policies are fully enforced resource-based policies, not advisory, and an explicit deny inside one is authoritative. C is incorrect — bucket policies apply to principals in the bucket owner's own account exactly as they do to external accounts; the well-known "a resource-based policy alone can grant same-account access" rule concerns `Allow` statements only and has no bearing on `Deny` scope — an explicit deny always applies regardless of the principal's account. D is false — `s3:*` is a full wildcard that includes `s3:GetObject`.

**Trigger words:** "explicit `Deny` statement blocking... for every principal except," "Access Denied" despite a broad `s3:*` allow.

**Underlying architectural principle:** An explicit deny in any applicable policy always overrides any allow, no matter where in the identity/resource/organization policy stack that allow originates.

---

### Question 2 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A startup's engineering team is auditing its EC2 fleet ahead of a SOC 2 assessment and discovers that several application servers have long-term IAM user access keys hard-coded in a configuration file to call S3 and DynamoDB APIs. The auditor flags this as a finding, noting the keys have no rotation policy, don't expire, and would remain valid indefinitely even if the EC2 instance were terminated and rebuilt. The team wants the standard AWS-recommended remediation with the least ongoing operational burden.

**Options:**
A. Rotate the access keys manually every 24 hours using a cron job on each instance.
B. Attach an IAM role to each EC2 instance (via an instance profile) that grants the needed S3/DynamoDB permissions, remove the hard-coded keys, and let the instance retrieve short-lived, automatically rotated temporary credentials from the instance metadata service.
C. Move the access keys into an environment variable instead of a configuration file, since environment variables are encrypted at rest by the OS.
D. Create one shared IAM user per application tier and rotate its single key set quarterly instead of per-instance keys.

**Correct answer(s):** B

**Why correct:** IAM roles for EC2 automatically vend temporary, short-lived credentials via STS through the instance metadata service and rotate them continuously with zero operational effort, which is the AWS-recommended pattern specifically to eliminate long-term credentials on compute resources.

**Why each wrong option is wrong:** A requires the team to build and maintain custom rotation tooling, which is exactly the ongoing operational burden they want to avoid, and still leaves a long-term credential type in use. C is a false claim — environment variables are not inherently encrypted at rest by the OS, and this doesn't address the core problem of using long-term credentials at all. D still uses long-term IAM user access keys, just shared and rotated less frequently, which is a weaker security posture than temporary credentials.

**Trigger words:** "hard-coded in a configuration file," "no rotation policy," "least ongoing operational burden."

**Underlying architectural principle:** Compute resources should use IAM roles for automatically rotated temporary credentials instead of any form of long-term IAM user access keys.

---

### Question 3 [Priority: P2] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company onboards 60 new developers who all need identical read-only access to a shared set of S3 buckets and `ec2:Describe*` permissions across the account. The security team wants to grant this access in a way that is simple to audit, easy to update for everyone at once if the requirement changes, and doesn't require touching each of the 60 individual IAM users whenever a policy needs adjustment.

**Options:**
A. Attach the two required managed policies individually to each of the 60 IAM users.
B. Create an IAM group, attach the required policies to the group once, and add all 60 developers as members of that group.
C. Create a separate IAM role for each developer and require them to manually call `sts:AssumeRole` every time they need access.
D. Write a single SCP granting the required permissions and attach it to the account.

**Correct answer(s):** B

**Why correct:** IAM groups exist specifically to manage permissions for a collection of users with identical needs — attaching policies once at the group level automatically applies to every current and future member, making bulk updates trivial and auditing straightforward.

**Why each wrong option is wrong:** A requires 60 separate policy attachments and 60 separate updates any time the permission set changes, which is exactly the operational burden the team wants to avoid. C adds unnecessary manual friction (an extra AssumeRole step) for permissions that should simply be available on login, with no benefit over group membership for this use case. D is not possible in the way described — SCPs never grant permissions; they only set a maximum permissions ceiling and require an underlying identity-based allow to actually grant access.

**Trigger words:** "identical read-only access," "simple to audit," "doesn't require touching each of the 60 individual IAM users."

**Underlying architectural principle:** IAM groups are the standard mechanism for managing identical permissions across many users, letting administrators update access for the whole cohort in a single place.

---

### Question 4 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** Company A (account `111111111111`) has agreed to a six-month data-sharing partnership requiring Company B (account `222222222222`) to have read-only access to one specific S3 bucket in Company A's account. Company A's security team wants to avoid creating any IAM users or sharing any long-term credentials with Company B, wants Company B's existing employees to use their own company's IAM identities to obtain the access, and wants the ability to revoke the entire arrangement instantly if the partnership ends early.

**Options:**
A. Create an IAM role in Account A with a trust policy naming Account B (or a specific role/user ARN in Account B) as the trusted principal, attach a permissions policy granting read-only S3 access to the bucket, and have Company B's users call `sts:AssumeRole` to obtain temporary credentials.
B. Create an IAM user in Account A scoped to read-only S3 access, and securely email the access key and secret key to Company B's team.
C. Add a bucket policy to the S3 bucket that makes the bucket public so Company B can access it via an unauthenticated URL.
D. Set up a full AWS Organizations merge between the two companies' accounts so both share a single management account.

**Correct answer(s):** A

**Why correct:** Cross-account access without sharing long-term credentials or creating IAM users in the granting account is the textbook use case for an IAM role with a cross-account trust policy — the external account's own identities call `sts:AssumeRole` to receive temporary, revocable credentials, and deleting or modifying the trust policy instantly cuts off access.

**Why each wrong option is wrong:** B reintroduces exactly the long-term-credential-sharing pattern the team wants to avoid, with no automatic expiration and much weaker auditability. C exposes the bucket to the entire internet, far exceeding the requirement of "Company B only" and creating a serious data exposure risk. D is a drastically disproportionate structural change — merging AWS Organizations for a temporary, narrowly scoped partnership is not a supported or sensible pattern for simple cross-account resource sharing.

**Trigger words:** "read-only access to one specific S3 bucket," "avoid creating any IAM users or sharing any long-term credentials," "revoke the entire arrangement instantly."

**Underlying architectural principle:** Cross-account access between two separate AWS accounts is implemented with an IAM role and cross-account trust policy, letting external identities obtain temporary credentials via STS rather than sharing long-term secrets or IAM users.

---

### Question 5 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A platform engineering team delegates to individual "team lead" IAM users the ability to create new IAM users and roles for their own sub-teams within a single AWS account, using `iam:CreateUser`, `iam:CreateRole`, and `iam:AttachUserPolicy`/`iam:AttachRolePolicy` permissions. Security mandates that no matter what managed or inline policy a team lead attaches to an entity they create, that new entity must never be able to gain `AdministratorAccess`-level permissions or delete production S3 buckets — while explicitly not wanting to restrict any other, pre-existing IAM users or roles in the account that the team leads did not create.

**Options:**
A. Attach a Service Control Policy at the account's OU in AWS Organizations that denies `iam:*`, `s3:DeleteBucket` for the whole account.
B. Set a permissions boundary on the `iam:CreateUser`/`iam:CreateRole` calls the team leads make, so every new IAM entity they create is capped at a maximum permission set regardless of which policy is later attached to it.
C. Add a resource-based policy to the production S3 buckets denying delete actions from any principal.
D. Require MFA on the team lead's own IAM user login.

**Correct answer(s):** B

**Why correct:** A permissions boundary is an advanced IAM feature specifically designed for this delegated-administration scenario: it sets a maximum permissions ceiling on the entities a delegated admin creates, so no policy the team lead later attaches to that new user/role can exceed the boundary — while leaving every other principal in the account untouched.

**Why each wrong option is wrong:** A is too blunt an instrument — an SCP applies to the entire account (or OU) for every principal including pre-existing ones, directly violating the requirement not to restrict entities the team leads didn't create, and SCPs cannot be scoped only to newly created identities. C would block legitimate delete operations by existing authorized admins too, and doesn't address the broader "never gain AdministratorAccess-level permissions" requirement across all actions, only S3 deletes. D addresses authentication strength, not what permissions a created entity can be granted, and does nothing to cap the ceiling of new users/roles.

**Trigger words:** "no matter what... policy a team lead attaches," "must never be able to gain `AdministratorAccess`-level permissions," "explicitly not wanting to restrict any other, pre-existing IAM users."

**Underlying architectural principle:** Permission boundaries cap the maximum permissions a delegated administrator can grant to the specific entities they create, without affecting any other IAM principal in the account — distinct from SCPs, which apply account/OU-wide to every principal, including ones the delegated admin never touched.

---

### Question 6 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A global enterprise runs AWS Organizations with 40 member accounts and 2,000 employees who already authenticate to Okta for all other corporate applications. The company wants employees to access multiple AWS accounts using role-based permission sets, wants every access assignment centrally visible and auditable from one place, wants to enforce MFA centrally rather than per-account, and explicitly wants to avoid creating or managing individual IAM users in each of the 40 accounts. Select the two actions that together satisfy these requirements.

**Options:**
A. Enable AWS IAM Identity Center for the organization and configure Okta as an external SAML identity provider so employees authenticate with their existing corporate credentials.
B. In IAM Identity Center, define permission sets (backed by AWS managed or customer managed policies) and assign them to users/groups against specific AWS accounts or OUs, letting Identity Center provision the underlying IAM roles automatically in each account.
C. Create an individual IAM user for each of the 2,000 employees inside every one of the 40 AWS accounts they need to access.
D. Write a Service Control Policy that grants employees the ability to log in to any of the 40 accounts.
E. Distribute the AWS Organizations management account's root credentials to team leads so they can manually provision cross-account access.

**Correct answer(s):** A, B

**Why correct:** A gives the company centralized, federated authentication against its existing Okta identity source, avoiding per-account IAM users entirely. B provides the centrally managed, auditable, permission-set-based access-assignment model across accounts/OUs that IAM Identity Center is purpose-built for, with the underlying IAM roles provisioned and deprovisioned automatically.

**Why each wrong option is wrong:** C is the exact unmanageable, non-centralized anti-pattern (2,000 users × 40 accounts) the company explicitly wants to avoid. D is not possible — SCPs only ever restrict maximum available permissions within an account; they cannot grant login access or create any form of authentication mechanism. E is a severe security anti-pattern — sharing root credentials with anyone, let alone distributing them broadly, violates the most basic IAM best practice and provides no auditability or centralized control.

**Trigger words:** "already authenticate to Okta," "centrally visible and auditable from one place," "avoid creating or managing individual IAM users in each of the 40 accounts."

**Underlying architectural principle:** IAM Identity Center federated with an existing corporate identity provider, combined with permission sets assigned per account/OU, is the standard way to give a large workforce centrally managed, auditable multi-account access without provisioning IAM users anywhere.

---

### Question 7 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A security team attaches a Service Control Policy at the "Production" OU in AWS Organizations that denies `ec2:RunInstances` unless the request's region is `us-east-1` or `eu-west-1`, in order to enforce data-residency requirements across the 15 production accounts under that OU. A developer holding the `AdministratorAccess` managed IAM policy in one of those production accounts attempts to launch an EC2 instance in `ap-southeast-1` for a quick proof-of-concept and receives an authorization failure, even though `AdministratorAccess` normally permits every action in every region.

**Options:**
A. `AdministratorAccess` is deprecated in 2026 and no longer includes `ec2:RunInstances` by default.
B. The SCP defines the maximum permissions available anywhere in that account; since the SCP explicitly denies the action for that region, no identity-based policy in the account — including `AdministratorAccess` — can grant an action the SCP has already excluded.
C. The developer's session must not have MFA enabled, which is unrelated to the region restriction but is what's actually causing the denial.
D. `ec2:RunInstances` requires an explicit resource-based policy on the target subnet before any IAM policy can grant it.

**Correct answer(s):** B

**Why correct:** SCPs act as an organization-level guardrail that establishes the ceiling of permissions available within an account, evaluated independently of and prior to any IAM identity-based policy; even the broadest IAM policy in the account cannot restore an action the SCP has explicitly denied.

**Why each wrong option is wrong:** A is false — `AdministratorAccess` still grants `ec2:*` including `RunInstances`; the denial has nothing to do with the policy's contents. C introduces an unrelated, unsupported explanation not indicated anywhere in the scenario — the stated condition is clearly regional, not MFA-based. D is false — EC2 subnets do not have resource-based policies in this way, and this isn't how the described SCP condition works.

**Trigger words:** "SCP... denies `ec2:RunInstances` unless the request's region is," "`AdministratorAccess`... normally permits every action in every region."

**Underlying architectural principle:** SCPs set an absolute ceiling on permissions across an OU/account that no identity-based policy, no matter how permissive, can override.

---

### Question 8 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A mobile photo-sharing app expects millions of installs, supports both anonymous guest browsing and sign-in via Google and Facebook, and needs each app instance to upload photos directly to S3 without routing every upload through a custom backend server. Guest users should get more restricted permissions (upload only to a "pending" prefix) than authenticated users (upload to their own user-specific prefix), and the solution needs to scale to millions of concurrent app instances without provisioning any individual IAM identity per user.

**Options:**
A. Use an Amazon Cognito identity pool (federated identities) configured with Google and Facebook as identity providers, mapped to two distinct IAM roles — one for unauthenticated (guest) identities and one for authenticated identities — so the app receives short-lived STS credentials scoped accordingly.
B. Create an IAM user for every app installation the first time it launches, and store that user's access keys locally on the device.
C. Embed a single shared IAM access key and secret key inside the app binary for all users to use when calling S3 directly.
D. Configure AWS IAM Identity Center and have each mobile user authenticate against it directly from the app.

**Correct answer(s):** A

**Why correct:** Cognito identity pools are purpose-built for exactly this consumer-facing, web-identity-federation use case — mapping external identity providers (or unauthenticated access) to distinct IAM roles and issuing scoped, short-lived STS credentials directly to the client at effectively unlimited scale, with no per-user IAM identity to provision.

**Why each wrong option is wrong:** B does not scale operationally or securely — provisioning millions of individual IAM users is unsupported at that scale and defeats the purpose of using temporary, federated credentials. C is a severe security anti-pattern, embedding a single long-term shared secret in a distributable app binary where it can be extracted and abused by anyone. D is the wrong tool — IAM Identity Center is designed for workforce (employee) access to AWS accounts and business applications, not for authenticating anonymous or consumer-facing mobile app end users.

**Trigger words:** "millions of installs," "anonymous... and sign-in via Google and Facebook," "without provisioning any individual IAM identity per user."

**Underlying architectural principle:** Amazon Cognito identity pools provide web identity federation for consumer-facing applications at scale, issuing temporary STS credentials mapped to distinct IAM roles for guest vs. authenticated users — this is a different tool from IAM Identity Center, which targets workforce access.

---

### Question 9 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A large enterprise already operates an on-premises Active Directory Federation Services (AD FS) deployment issuing SAML 2.0 assertions for dozens of non-AWS SaaS applications, with a custom attribute-mapping schema the identity team has invested years building and does not want to re-architect. The company now wants employees to sign in to the AWS Management Console using their existing AD credentials, with no IAM users created per employee, while continuing to use their existing AD FS SAML setup rather than adopting a new identity system for this one use case.

**Options:**
A. Create an IAM SAML identity provider resource in IAM referencing the AD FS metadata, create one or more IAM roles with a trust policy that trusts that SAML provider, and let employees authenticate through AD FS which redirects them into the AWS Console via a SAML assertion (either IdP-initiated or SP-initiated) mapped to the appropriate role.
B. Enable IAM Identity Center and configure it to use AD FS as an identity source without any additional trust policy configuration.
C. Manually create an IAM user in AWS for every AD user, and synchronize passwords nightly using a custom script.
D. Configure Amazon Cognito user pools to sync directly with the on-premises Active Directory schema.

**Correct answer(s):** A

**Why correct:** IAM's native SAML 2.0 federation support lets an organization keep its existing AD FS SAML infrastructure and attribute-mapping schema entirely as-is, simply adding IAM as one more relying party that trusts SAML assertions from that existing IdP via IAM roles — with no per-user IAM identity required and no need to adopt a separate AWS-specific identity system.

**Why each wrong option is wrong:** B is wrong on its own stated premise — configuring IAM Identity Center to use AD FS as an external identity source still requires setting up a SAML trust relationship (exchanging IdP/SP metadata) before anyone can sign in, so "without any additional trust policy configuration" is false; more importantly, routing through IAM Identity Center layers in an entirely new AWS-managed identity system on top of AD FS, which directly contradicts the company's stated wish not to adopt a new identity system for this one use case. C reintroduces per-user IAM identities and a fragile custom password-sync process, exactly what the company wants to avoid. D is not a valid pattern — Cognito user pools are not designed to directly sync with on-premises Active Directory schemas for AWS Console federation.

**Trigger words:** "existing on-premises Active Directory Federation Services (AD FS)," "custom attribute-mapping schema... does not want to re-architect," "no IAM users created per employee."

**Underlying architectural principle:** Direct SAML 2.0 federation via an IAM identity provider and role trust policies lets an organization reuse an existing enterprise SAML IdP for AWS Console access without provisioning IAM users or replacing existing federation infrastructure.

---

### Question 10 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** Account A creates an IAM role intended for Account B to assume, with a permissions policy granting `s3:GetObject` on a specific bucket owned by Account A. Account B's engineers successfully call `sts:AssumeRole` and receive valid temporary credentials, but every subsequent `GetObject` call against the bucket still returns `Access Denied`. The bucket also has a bucket policy that explicitly lists only a small set of specific principal ARNs as allowed.

**Options:**
A. Nothing is missing — Account B should already have access once the role's permissions policy allows `s3:GetObject`.
B. The bucket policy must also explicitly include the cross-account role's ARN as an allowed principal; for cross-account resource access, both the caller's identity-based policy and the resource's resource-based policy must independently authorize the request when a restrictive resource policy exists.
C. Account B needs to attach its own bucket policy to the object before it can read it.
D. The role's permissions policy should be changed from `s3:GetObject` to `s3:*` to fully resolve the access issue.

**Correct answer(s):** B

**Why correct:** When a resource-based policy (like this bucket policy) exists and explicitly restricts principals, cross-account requests must be authorized by both the identity-based policy attached to the calling principal (the role) and the resource-based policy on the target resource — unlike same-account access, where either one alone can be sufficient.

**Why each wrong option is wrong:** A ignores that the bucket policy explicitly limits allowed principals to a specific list, which will block any principal — including a fully permissioned cross-account role — not named in it. C is not a real mechanism — S3 objects don't have their own bucket policies attached by the requester's account. D doesn't address the actual root cause (the bucket policy's principal restriction); broadening the role's own permissions policy has no effect on a resource-based policy denying the principal outright.

**Trigger words:** "role's permissions policy grants `s3:GetObject`," "bucket policy... explicitly lists only a small set of specific principal ARNs," "still returns Access Denied."

**Underlying architectural principle:** For cross-account access to a resource protected by a restrictive resource-based policy, both the caller's identity-based policy and the resource owner's resource-based policy must grant the access — a same-account allow-by-either-policy shortcut does not apply across accounts.

---

### Question 11 [Priority: P0] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A company engages a third-party SaaS monitoring vendor that requires a cross-account IAM role to pull CloudWatch metrics from the customer's AWS account. The vendor is known to reuse the same IAM role name and trust relationship pattern across all of its customers, creating a documented "confused deputy" risk where the vendor's own compromised credentials — or a mistake on the vendor's side — could potentially be used to assume a role in the wrong customer's account if the trust policy is too permissive. Select the two measures that AWS best-practice guidance recommends adding to the role's trust policy to mitigate this specific risk.

**Options:**
A. Require a unique, secret external ID via the `sts:ExternalId` condition key in the trust policy, agreed upon out-of-band between the vendor and this specific customer.
B. Scope the trust policy's `Principal` element to the vendor's specific AWS account ID (or specific IAM role ARN) rather than a wildcard or overly broad principal.
C. Attach the `AdministratorAccess` managed policy to the role so the vendor's monitoring tooling never hits an unexpected permissions gap.
D. Require interactive MFA approval on every `sts:AssumeRole` call made by the vendor's fully automated monitoring system.
E. Grant the vendor the customer's AWS account root user credentials so root-level trust is established directly.

**Correct answer(s):** A, B

**Why correct:** The external ID condition (A) is AWS's documented mechanism specifically designed to prevent the confused-deputy problem in third-party cross-account role scenarios, ensuring only requests presenting the correct secret value are honored. Scoping the trust policy's principal to the vendor's specific account/role (B) ensures only that vendor's specific identity can even attempt the assumption in the first place, rather than relying on the external ID as the only control.

**Why each wrong option is wrong:** C violates least privilege badly — CloudWatch metrics retrieval needs only read-only monitoring permissions, and granting `AdministratorAccess` massively expands blast radius if the vendor's role is ever misused. D is impractical for a fully automated, unattended system with no human present to approve an MFA challenge, and MFA on role assumption is not the standard control for this specific confused-deputy risk. E is a severe anti-pattern that hands over complete, unrestricted control of the entire AWS account to an external party, far beyond the narrow CloudWatch read access actually required.

**Trigger words:** "reuse the same IAM role name and trust relationship pattern across all of its customers," "confused deputy risk," "measures... to the role's trust policy."

**Underlying architectural principle:** Third-party cross-account role trust relationships should combine a unique external ID condition with a tightly scoped trust policy principal to prevent confused-deputy scenarios where one vendor's credentials could be misused against the wrong customer account.

---

### Question 12 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A cloud engineer creates a new IAM role intended for a data-processing Lambda function, attaches a permissions boundary that allows up to `s3:*` and `dynamodb:*` actions (intended as a generous future ceiling), but forgets to attach any actual identity-based permissions policy granting specific actions to the role. When the Lambda function executes using this role, every AWS API call — including basic `s3:GetObject` calls the boundary would clearly permit — fails with `Access Denied`.

**Options:**
A. This is expected behavior — a permissions boundary only defines the maximum permissions an identity is *allowed* to have; it does not, by itself, grant any permissions. Without a separate identity-based policy actually allowing `s3:GetObject`, the role has no effective permissions at all.
B. This is a bug — permissions boundaries are supposed to function as identity-based policies once attached, granting all actions within their scope automatically.
C. The role needs an SCP attached directly to it to activate the permissions defined in the boundary.
D. Permissions boundaries only take effect after the role has been used successfully at least once, so a second invocation would succeed.

**Correct answer(s):** A

**Why correct:** A permissions boundary is strictly a ceiling — the intersection of what an identity-based policy allows and what the boundary allows — never a grant of permissions on its own; an entity with only a boundary and no identity-based policy effectively has zero permissions, exactly as observed here.

**Why each wrong option is wrong:** B misunderstands the fundamental mechanic of permission boundaries; they never function as a standalone grant, regardless of how generous the boundary's allowed actions are. C is not how SCPs work — SCPs are attached to AWS Organizations accounts/OUs, not to individual IAM roles, and have no relationship to activating a permissions boundary. D describes non-existent behavior; there is no "warm-up" period or first-use exception for permissions boundaries.

**Trigger words:** "attaches a permissions boundary... but forgets to attach any actual identity-based permissions policy," "every AWS API call... fails with Access Denied."

**Underlying architectural principle:** A permissions boundary only caps the maximum permissions an entity can have — it never substitutes for or grants permissions on its own; an identity-based policy is still required to actually allow any action.

---

### Question 13 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An automation engineer configures a workflow where an application first calls `sts:AssumeRole` on "RoleA" (whose maximum session duration is configured as 12 hours) and requests a 12-hour session. From within that active RoleA session, the application's code then calls `sts:AssumeRole` again to assume a second role, "RoleB" (whose own maximum session duration is separately configured as 8 hours), also requesting the longest duration possible. The engineer is confused when the resulting RoleB credentials expire after just one hour, far short of either role's configured maximum.

**Options:**
A. This is a misconfiguration; both `DurationSeconds` values should simply be increased to override the unexpected 1-hour expiration.
B. When temporary security credentials obtained from one role assumption are used to call `sts:AssumeRole` again ("role chaining"), the resulting session is capped at a maximum duration of one hour, regardless of either role's configured `MaxSessionDuration` or the requested `DurationSeconds`.
C. RoleB's 8-hour maximum session duration setting was never applied because the role was created after RoleA.
D. Role chaining is not supported by AWS STS at all, so the second `AssumeRole` call should have failed outright rather than succeeding with a short session.

**Correct answer(s):** B

**Why correct:** AWS STS explicitly limits role-chained sessions — where temporary credentials from one assumed role are used to assume a second role — to a hard maximum of one hour, independent of any `MaxSessionDuration` configured on either role or any longer duration requested in the API call.

**Why each wrong option is wrong:** A is incorrect because no `DurationSeconds` value can override the hard one-hour role-chaining limit; increasing it has no effect. C invents an unrelated and incorrect explanation — role creation order has nothing to do with session duration behavior. D is false — role chaining is a supported and commonly used AWS pattern; it simply carries this specific one-hour session-duration constraint.

**Trigger words:** "temporary security credentials... to call `sts:AssumeRole` again," "resulting RoleB credentials expire after just one hour, far short of either role's configured maximum."

**Underlying architectural principle:** Role chaining — assuming a second role using another role's temporary credentials — is capped at a one-hour maximum session duration regardless of any role's configured maximum, a limit unique to chained (as opposed to direct) role assumption.

---

### Question 14 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A software team wants its CI/CD pipeline (running in GitHub Actions) to deploy infrastructure into a separate AWS production account without storing any long-lived AWS credentials as pipeline secrets, and wants the ability to guarantee that only workflow runs triggered from a specific repository and branch (e.g., `main` on `org/prod-infra`) can ever obtain deployment credentials — even if the same GitHub organization runs many other unrelated repositories. Select the two measures that best satisfy both requirements.

**Options:**
A. Configure an OIDC identity provider in the AWS account trusting GitHub's OIDC token issuer, and create an IAM role that GitHub Actions assumes via `sts:AssumeRoleWithWebIdentity` using the workflow's short-lived OIDC token — eliminating the need to store any long-lived AWS access keys as a pipeline secret.
B. Scope the IAM role's trust policy with a condition on the OIDC token's `sub` (and/or `aud`) claim so that only tokens asserting the exact repository and branch (e.g., `repo:org/prod-infra:ref:refs/heads/main`) are permitted to assume the role.
C. Generate a long-lived IAM user access key for the pipeline, store it as an encrypted GitHub Actions secret, and rotate it manually every 90 days.
D. Create one broad, shared deployment role with `AdministratorAccess` and use it across every repository and workflow in the GitHub organization for simplicity.
E. Remove all conditions from the OIDC trust policy so that any successfully authenticated GitHub Actions workflow can assume the role without restriction.

**Correct answer(s):** A, B

**Why correct:** OIDC federation with `AssumeRoleWithWebIdentity` (A) eliminates long-lived AWS credentials from the pipeline entirely, since GitHub issues short-lived, cryptographically verifiable tokens per workflow run. Scoping the trust policy's condition to the exact repository/branch claim (B) is what actually restricts which specific workflow runs can obtain credentials, directly satisfying the requirement that only that one repo/branch combination can deploy — a plain OIDC trust relationship without this condition would still let any repository in the account/org's trusted OIDC provider potentially assume the role.

**Why each wrong option is wrong:** C reintroduces exactly the long-lived-credential storage problem the team wants to eliminate, and manual 90-day rotation is a much weaker control than short-lived, per-run federated tokens. D violates least privilege severely by granting full administrative access broadly across unrelated repositories/workflows, and provides no way to enforce the "only this repo/branch" requirement. E directly removes the specific control needed to satisfy the second requirement, allowing any GitHub Actions workflow in the trusted OIDC configuration to assume the deployment role.

**Trigger words:** "without storing any long-lived AWS credentials as pipeline secrets," "only workflow runs triggered from a specific repository and branch," "even if the same GitHub organization runs many other unrelated repositories."

**Underlying architectural principle:** OIDC federation lets CI/CD systems assume IAM roles using short-lived, per-run tokens instead of long-lived credentials, and the trust policy's claim-based conditions (not just enabling the OIDC provider) are what actually scope which specific workflows can obtain access.

---

### Question 15 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** As a company scales from 5 to 30 AWS accounts organized under Dev and Prod OUs in AWS Organizations, the security team wants every engineer to automatically receive broad, PowerUser-style access in any Dev-OU account and strictly read-only access in any Prod-OU account, with the mapping managed in exactly one central place so that extending access to a new account added to either OU never requires hand-authoring a new IAM role or policy in that account, and so permission drift between accounts never occurs.

**Options:**
A. In IAM Identity Center, define one "DeveloperAccess" permission set (backed by a PowerUserAccess-equivalent policy) and one "ReadOnlyAccess" permission set (backed by a read-only policy), then assign "DeveloperAccess" to the engineers' group against every account in the Dev OU and "ReadOnlyAccess" against every account in the Prod OU in a single bulk operation — Identity Center provisions and manages the underlying IAM roles in every targeted account from these two centrally defined permission sets, so extending coverage to a newly added account means re-applying the existing OU-scoped assignment rather than hand-authoring a brand-new IAM role and policy in that account.
B. Manually create and maintain an IAM role with the appropriate policy in each of the 30 accounts individually, updating all 30 whenever the policy needs to change.
C. Write a Service Control Policy that grants `PowerUserAccess`-equivalent permissions in Dev accounts and read-only permissions in Prod accounts.
D. Create an IAM user for each engineer replicated identically into all 30 accounts using a shared password stored in a spreadsheet.

**Correct answer(s):** A

**Why correct:** IAM Identity Center permission sets are precisely the mechanism designed for this scale requirement — access is defined exactly once per role type (as a permission set) and assigned centrally across every account in an OU in a single operation instead of being hand-built account by account, so a newly added account is covered by re-applying that same central assignment rather than authoring a brand-new IAM role/policy for it, and there is only ever one place where the DeveloperAccess/ReadOnlyAccess mapping is defined — eliminating the per-account permission drift that comes from maintaining 30-plus separate hand-written IAM roles.

**Why each wrong option is wrong:** B is the exact manual, error-prone, drift-prone anti-pattern the team is trying to eliminate as it scales, requiring 30 (and growing) separate updates for any policy change. C is not achievable — SCPs are guardrails that only restrict maximum permissions; they can never grant permissions such as PowerUserAccess, so this approach would grant nothing. D reintroduces IAM users replicated across every account with shared, spreadsheet-stored passwords — an unmanageable and seriously insecure pattern with no centralized control point.

**Trigger words:** "mapping managed in exactly one central place," "never requires hand-authoring a new IAM role or policy," "permission drift between accounts never occurs."

**Underlying architectural principle:** IAM Identity Center permission sets, defined once and assigned in bulk across every account in an OU, scale cleanly as an organization adds accounts, keeping access centrally defined and consistent without hand-authoring per-account IAM roles — a capability SCPs and manual per-account IAM roles cannot provide, since SCPs never grant permissions at all and manual roles require independent, per-account maintenance.

---

### Question 16 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A SaaS company uses a single shared IAM role, "TenantDataRole," with a broad identity-based policy granting `s3:*` across an entire multi-tenant data bucket, because creating one dedicated IAM role per customer would not scale past the AWS soft limit on roles per account as the customer base grows into the thousands. The security team requires that, at the moment each customer's session is established, the effective permissions for that specific session be dynamically restricted to only that customer's own prefix within the bucket — without creating any additional IAM roles.

**Options:**
A. Pass a scoped-down session policy (or use session tags combined with attribute-based access control conditions referencing the tenant identifier) in the `sts:AssumeRole` call, so the resulting temporary credentials' effective permissions are the intersection of the role's identity-based policy and the session policy — dynamically restricting each session to only that tenant's prefix.
B. Create a new, separate IAM role for every tenant as soon as they sign up, accepting the eventual per-account role-count limit as an acceptable tradeoff.
C. Attach a new bucket policy statement for every tenant listing their specific prefix, updating the bucket policy in real time as tenants are added.
D. Grant `s3:*` broadly and rely entirely on tenant-side application logic to avoid accessing another tenant's prefix, since IAM cannot scope access by dynamic runtime values.

**Correct answer(s):** A

**Why correct:** STS session policies (and attribute-based access control via session tags) let a single, shared IAM role's effective permissions be narrowed dynamically per `AssumeRole` call — the resulting session can never exceed the role's own policy, but can be scoped down further at assumption time to just that tenant's prefix, exactly matching the "one role, thousands of dynamically scoped sessions" requirement.

**Why each wrong option is wrong:** B directly reintroduces the per-tenant-role scaling problem the team explicitly wants to avoid. C requires continuously rewriting a single bucket policy for every tenant addition, which does not scale cleanly and risks the bucket policy's own size limits at thousands of tenants. D is also wrong on its embedded factual claim — IAM can scope access by dynamic runtime values (that is exactly what session tags and ABAC conditions do); D abandons IAM-level enforcement entirely and relies on trusting application code never to make a mistake, which is not a defensible access-control boundary for a multi-tenant system handling customer data.

**Trigger words:** "single shared IAM role... because creating one dedicated IAM role per customer would not scale," "dynamically restricted to only that customer's own prefix... without creating any additional IAM roles."

**Underlying architectural principle:** STS session policies (or session-tag-based ABAC) let one shared IAM role serve many dynamically scoped sessions, narrowing effective permissions per assumption without provisioning a role per principal.

---

### Question 17 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** In a single AWS account, a specific IAM role named "AuditToolRole" has an identity-based policy attached granting `AdministratorAccess`. Separately, the security team attaches a permissions boundary to that same role that only allows `iam:Get*` and `iam:List*` actions (a read-only IAM-inspection boundary). No Service Control Policy in the account restricts IAM or any other service. A developer asks what actions "AuditToolRole" can actually perform when assumed.

**Options:**
A. The role can perform any action allowed by `AdministratorAccess`, since permissions boundaries only apply to newly created entities, not to existing roles with pre-existing identity-based policies.
B. The role's effective permissions are the intersection of its identity-based policy and its permissions boundary — since the boundary only allows `iam:Get*`/`iam:List*` actions, and `AdministratorAccess` also happens to include those same actions, the role can only ever call read-only IAM inspection actions such as `iam:GetRole` or `iam:ListPolicies`, and nothing else.
C. The role can perform any `iam:*` action, since the boundary was clearly intended to scope IAM management access broadly.
D. The role has zero permissions at all, since attaching both an identity-based policy and a permissions boundary to the same role is not a supported configuration.

**Correct answer(s):** B

**Why correct:** A permissions boundary applies to any IAM entity it is attached to (new or existing) and effective permissions are always the intersection of what the identity-based policy allows and what the boundary allows; since the boundary restricts the role to only `iam:Get*`/`iam:List*`, and those actions are indeed a subset of what `AdministratorAccess` grants, the intersection is exactly those read-only IAM inspection actions — nothing from S3, EC2, or any other service, and no IAM write/delete/create actions either.

**Why each wrong option is wrong:** A is false — permissions boundaries apply the moment they are attached to an entity, regardless of when that entity or its identity-based policy was created. C incorrectly assumes the boundary grants broad IAM management access; it explicitly lists only `Get*`/`List*` (read-only) actions, excluding create/update/delete IAM actions. D is false — attaching both an identity-based policy and a permissions boundary to the same role is fully supported and is precisely how permissions boundaries are meant to be used.

**Trigger words:** "permissions boundary... that only allows `iam:Get*` and `iam:List*`," "identity-based policy attached granting `AdministratorAccess`," "what actions... can actually perform."

**Underlying architectural principle:** Effective IAM permissions are always the intersection of the identity-based policy and any attached permissions boundary — the boundary can only narrow, never widen, what the identity-based policy already grants.

---

### Question 18 [Priority: P1] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A junior engineer, trying to implement least privilege by "blocklisting" only the two service prefixes considered dangerous, writes the following IAM policy for a contractor's IAM user: `Effect: Allow`, `NotAction: ["iam:*", "organizations:*"]`, `Resource: "*"`. The engineer believes this correctly restricts the contractor from touching IAM or AWS Organizations while allowing everything else needed for their EC2-focused contract work. A security reviewer flags this policy as a critical finding during review.

**Options:**
A. There is nothing wrong with this policy — it correctly implements least privilege by excluding only the two sensitive service prefixes.
B. `NotAction` combined with `Effect: Allow` grants access to every AWS action *except* the ones listed — meaning this policy grants the contractor's user full permissions across every other AWS service (S3 deletion, EC2 termination, RDS deletion, VPC changes, billing, and more), which is the opposite of least privilege; `NotAction` is safe for narrowly scoping a `Deny` (blocklisting specific actions within an otherwise-scoped statement), but pairing it with a broad `Allow` and `Resource: "*"` produces a dangerously broad grant.
C. This policy will fail IAM policy validation and never actually take effect, so there is no real risk.
D. This is a non-issue because IAM automatically also implicitly denies billing and cost-management actions regardless of what the policy states.

**Correct answer(s):** B

**Why correct:** `NotAction` describes the complement of the listed actions; when paired with `Allow` and an unrestricted resource, it grants everything *not* in the list — turning what was meant as a narrow blocklist of two services into a nearly account-wide administrative grant across every other AWS service, which is precisely why this is a critical, non-obvious least-privilege violation.

**Why each wrong option is wrong:** A repeats the junior engineer's own flawed reasoning and misses that "blocklisting" via `NotAction`+`Allow` is fundamentally different from, and far more dangerous than, an explicit allow-list of only the actions actually needed. C is factually incorrect — this is syntactically valid IAM policy JSON and will be evaluated and enforced exactly as written, with no validation error. D is false — IAM has no such blanket automatic implicit protection for billing actions that would neutralize an overly broad `Allow`/`NotAction` statement like this one.

**Trigger words:** "blocklisting only the two service prefixes considered dangerous," "`Effect: Allow`, `NotAction`," "flagged as a critical finding."

**Underlying architectural principle:** `NotAction` paired with `Allow` grants everything except the listed actions and should never be used to "blocklist" a small set of sensitive services — true least privilege requires an explicit allow-list of only the specific actions actually needed, reserving `NotAction` for scoping `Deny` statements.

---

### Question 19 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A security audit of a company's contractor cross-account access finds several problems at once: the S3 bucket policy on a production data bucket grants access using `Principal: {"AWS": "arn:aws:iam::CONTRACTOR-ACCOUNT-ID:root"}` (the contractor's entire account, not a specific role), the cross-account IAM role the contractor assumes carries the `AdministratorAccess` managed policy with no permissions boundary attached, the role's trust policy has no `sts:ExternalId` condition and no source-IP restriction, and the role's maximum session duration is configured at 12 hours even though contractor tasks are typically completed within 30–60 minutes. Select the two remediations with the greatest impact on reducing the actual blast radius and attack surface of this configuration.

**Options:**
A. Attach a permissions boundary to the cross-account role that caps it to only the specific S3 read/write actions and object prefixes the contractor's work actually requires, replacing the current `AdministratorAccess` grant.
B. Narrow the bucket policy's principal from the contractor's entire account root to the specific role ARN the contractor actually assumes, add an `sts:ExternalId` condition (and/or a source-IP condition) to the role's trust policy, and reduce the role's maximum session duration to match the contractor's actual task duration (e.g., 60 minutes).
C. Create a dedicated IAM user in the company's own account for the contractor to use instead of a cross-account role, since IAM users are simpler to audit than roles.
D. Disable CloudTrail logging for this role's activity to reduce noise in the security team's monitoring dashboards, since the access is now considered fully trusted.
E. Add an additional `Allow` statement granting `s3:*` explicitly, to make sure no legitimate contractor action is ever accidentally blocked by the new restrictions.

**Correct answer(s):** A, B

**Why correct:** A directly reduces blast radius by replacing an unrestricted `AdministratorAccess` grant with a permissions boundary scoped to only the actions/prefixes actually needed, so even a compromised or misused role session cannot exceed that narrow ceiling. B closes multiple distinct attack-surface gaps at once — a wildcard account-root principal in the bucket policy allows any role/user in the contractor's account to potentially gain access, the missing external ID/source-IP conditions leave the trust policy vulnerable to confused-deputy-style misuse, and the excessive 12-hour session window needlessly extends how long a leaked credential remains valid well beyond the actual task duration.

**Why each wrong option is wrong:** C moves in the wrong direction entirely, replacing temporary, revocable, federated role-based access with a long-term IAM user and its associated credential-management risks — the opposite of the recommended pattern for external party access. D is a severe anti-pattern that removes visibility into exactly the access path the audit is concerned about, directly undermining the ability to detect misuse. E reintroduces the same overly broad access the remediation is trying to eliminate, defeating the purpose of scoping the role down at all.

**Trigger words:** "grants access using... the contractor's entire account, not a specific role," "no `sts:ExternalId` condition and no source-IP restriction," "maximum session duration configured at 12 hours even though contractor tasks are typically completed within 30–60 minutes."

**Underlying architectural principle:** Reducing the risk of third-party cross-account access requires tightening every layer at once — the resource policy's principal scope, the trust policy's confused-deputy conditions, the identity policy's permission ceiling, and the session's maximum duration — since any one loose layer can undermine the others.

---

### Question 20 [Priority: P0] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** An AWS Organizations OU has a Service Control Policy containing a single statement: `Effect: Deny`, `Action: "s3:DeleteObject"`, `Resource: "*"`, with no conditions — a blanket, organization-wide guardrail preventing object deletion across every account in that OU. Inside one member account, an IAM role named "DataOpsRole" has an identity-based policy granting `s3:*` with no permissions boundary attached. The target S3 bucket (owned by the same account) has a bucket policy with an explicit `Allow` statement specifically naming DataOpsRole's ARN and granting it `s3:DeleteObject`. A DataOps engineer assumes DataOpsRole and calls `s3:DeleteObject` on an object in that bucket.

**Options:**
A. The call succeeds, because the bucket policy's explicit `Allow` for the specific role ARN is more specific than the SCP's blanket deny and therefore takes precedence.
B. The call is denied — the SCP's explicit deny is an organization-level guardrail evaluated as an absolute ceiling on what is possible within the account; no identity-based policy, resource-based policy, or combination of the two inside the account can override an SCP's explicit deny.
C. The call is denied, but only because DataOpsRole lacks a permissions boundary; attaching one that allows `s3:DeleteObject` would let the call succeed despite the SCP.
D. The call succeeds, because `s3:*` in the identity-based policy is evaluated as broader and therefore overrides the narrower `s3:DeleteObject` denial in the SCP.

**Correct answer(s):** B

**Why correct:** SCPs are evaluated as an organization-wide ceiling that exists entirely outside and above the account's own policy evaluation; an explicit SCP deny removes an action from what is possible in the account at all, so no combination of identity-based policy, resource-based (bucket) policy, or permissions boundary inside the account — no matter how explicit or specifically targeted — can restore it.

**Why each wrong option is wrong:** A is incorrect — "more specific policy wins" is not how SCP-versus-account-policy evaluation works; SCPs are not compared for specificity against in-account policies, they simply gate what's possible before those policies are even considered. C is a common misconception — a permissions boundary is itself only an in-account IAM control and is just as incapable of overriding an SCP explicit deny as any other identity-based or resource-based policy; adding one allowing the action would not change the outcome at all. D is incorrect — policy evaluation does not resolve conflicts by comparing the "breadth" of wildcards across different policy types, and even if it did, this misunderstands that the SCP operates at a different, higher evaluation layer entirely.

**Trigger words:** "Service Control Policy containing a single statement: `Effect: Deny`, `Action: s3:DeleteObject`... no conditions," "bucket policy with an explicit `Allow` statement specifically naming DataOpsRole's ARN."

**Underlying architectural principle:** An SCP's explicit deny is an absolute, organization-level ceiling — it is evaluated independently of, and prior to, all in-account identity-based policies, resource-based policies, and permissions boundaries, none of which can override it regardless of how explicit or narrowly targeted they are.

---

### Question 21 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A 6-person startup is about to provision its primary customer database on Amazon RDS for PostgreSQL, ahead of signing a prospective enterprise customer whose security questionnaire requires that "data at rest be encrypted," but does not require the startup to control the key policy, define a custom rotation schedule, or share the key with any other AWS account. The team has no dedicated security engineer, is extremely cost-sensitive, and wants the fastest path to satisfying this one line item before the deal closes next week — and the database has not been created yet, so there is no existing unencrypted instance to migrate.

**Options:**
A. Create the new RDS instance with encryption at rest enabled at launch time, using the AWS managed key (`aws/rds`).
B. Create a customer managed KMS key with a custom key policy restricting usage to specific IAM roles, and use it for RDS encryption.
C. Note in the response that RDS "supports" encryption and leave it disabled, since the requirement only asks about capability, not current configuration.
D. Implement application-level encryption of each database column before writing to RDS, using a key generated and stored by the application itself.

**Correct answer(s):** A

**Why correct:** The AWS managed key is free, requires zero key-policy configuration, and satisfies "data at rest is encrypted" immediately — exactly matching a requirement with no custom control, rotation, or sharing needs. Enabling it is a one-time checkbox at launch (`--storage-encrypted` with the default `aws/rds` key), which fits the "fastest path" constraint. Note that RDS encryption can only be set at instance creation — an already-running, unencrypted RDS instance cannot have encryption toggled on in place; the only path for an existing instance is snapshot it, copy the snapshot with encryption enabled, and restore a new instance from that copy. Since this database has not been created yet, that limitation doesn't apply here.

**Why each wrong option is wrong:** B adds unnecessary key-policy management overhead and cost for a requirement that never asked for custom key control. C fails the stated requirement outright since the questionnaire asks about actual configuration, not theoretical capability. D introduces major application complexity, breaks native RDS indexing/query features, and is wildly disproportionate to a simple at-rest encryption requirement.

**Trigger words:** "no dedicated security engineer," "extremely cost-sensitive," "does not require... control the key policy," "fastest path," "has not been created yet."

**Underlying architectural principle:** Reach for an AWS managed key whenever the requirement is simply "encryption at rest enabled" with no need for custom key policies, rotation schedules, or cross-account sharing — reserve customer managed keys (CMKs) for scenarios that explicitly need that control. Also remember RDS encryption at rest can only be configured at creation time; converting an existing unencrypted instance always requires a snapshot-copy-restore cycle, never an in-place toggle.

---

### Question 22 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A Lambda function's execution role has an identity-based IAM policy granting `kms:Decrypt` on a specific KMS key ARN. A developer testing from the CLI with an IAM user that has the identical `kms:Decrypt` permission on the same key can successfully decrypt objects, but the Lambda function fails every invocation with `AccessDeniedException` when calling the same `Decrypt` API on the same key. The customer managed key (CMK) was originally created by a different platform team using a CloudFormation template. No CloudTrail events show any explicit Deny statements from an SCP or permissions boundary.

**Options:**
A. Update the CMK's key policy to explicitly allow the Lambda execution role's ARN to call `kms:Decrypt` (or verify the key policy includes the default "Enable IAM User Permissions" statement delegating control to IAM policies).
B. Attach the `AdministratorAccess` managed policy to the Lambda execution role to eliminate any possible permission gap.
C. Switch the encryption key from the customer managed key to an AWS managed key so Lambda no longer needs any key-policy configuration.
D. Increase the Lambda function's memory and timeout settings, since `AccessDeniedException` typically indicates the function is being throttled before it can complete the KMS call.

**Correct answer(s):** A

**Why correct:** A KMS key policy is the root of access control for that key — an IAM identity policy allow is necessary but never sufficient by itself. Since the CMK was created outside the Lambda team's control, its key policy likely omits the Lambda role (or lacks the default statement delegating to IAM), so KMS denies the call regardless of what the identity policy says.

**Why each wrong option is wrong:** B grants unrelated, overly broad permissions that violate least privilege and doesn't address the actual dual-gate root cause (though it would coincidentally work, it is not the correct/secure fix). C avoids the problem rather than fixing it and removes the deliberate custom control the platform team presumably created the CMK for. D misdiagnoses the error entirely — `AccessDeniedException` is an authorization error, not a performance/timeout symptom.

**Trigger words:** "customer managed key," "created by a different... team," "identical `kms:Decrypt` permission," "AccessDeniedException" despite matching IAM policy.

**Underlying architectural principle:** For KMS, both the caller's IAM identity policy AND the key's own resource-based key policy must allow the action — an allow on one side without the other results in denial, identical in shape to the S3 bucket-policy-plus-IAM-policy interplay.

---

### Question 23 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A fintech company runs Amazon RDS for MySQL and must rotate the master database password every 30 days as part of a PCI-DSS control, without writing or maintaining any custom rotation Lambda code. The company only has about five secrets total to manage, cost is a secondary concern relative to reducing operational burden, and the security team wants rotation to be natively integrated with RDS so a failed rotation doesn't lock the application out of the database.

**Options:**
A. Store the credential in AWS Secrets Manager and enable its native RDS rotation, which provisions and manages the required rotation Lambda function automatically.
B. Store the credential in Systems Manager Parameter Store as a `SecureString`, and build a custom Lambda function triggered by an EventBridge scheduled rule every 30 days to rotate it.
C. Store the credential in Parameter Store Standard tier as plaintext, and set a calendar reminder for the DBA team to rotate it manually every 30 days.
D. Store the credential in an S3 object encrypted with SSE-KMS, and rotate it manually by re-uploading a new object every 30 days.

**Correct answer(s):** A

**Why correct:** Secrets Manager has native, built-in rotation integration for RDS/Aurora/DocumentDB/Redshift that provisions the rotation Lambda and coordinates safely with the database engine, requiring no custom rotation code from the team.

**Why each wrong option is wrong:** B requires the team to build and maintain their own rotation Lambda and scheduling — exactly what they explicitly want to avoid. C relies on a manual, error-prone human process with no automation, failing the "rotate every 30 days" control reliably. D has no rotation mechanism at all, no RDS integration, and no automatic credential distribution to the application.

**Trigger words:** "rotate... every 30 days," "without writing or maintaining any custom rotation Lambda code," "natively integrated with RDS."

**Underlying architectural principle:** Choose Secrets Manager over Parameter Store whenever the requirement is automatic, native rotation of database (or other supported service) credentials — Parameter Store has no built-in rotation engine.

---

### Question 24 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A healthcare analytics company replicates objects from an S3 bucket in Account A (us-east-1), encrypted with SSE-KMS using a customer managed key owned by Account A, to a disaster-recovery bucket in Account B (eu-west-1) using S3 Cross-Region Replication. Compliance requires the replicated copies to be encrypted with a separate customer managed key that Account B fully controls, and RPO must stay near-zero so replication cannot silently skip encrypted objects. After enabling the replication rule, the team notices SSE-KMS-encrypted objects are not appearing in the destination bucket at all, while unencrypted test objects replicate fine.

**Options:**
A. Grant the replication IAM role permission to use both CMKs (`kms:Decrypt` on the source key, `kms:Encrypt` on the destination key), update both key policies to allow that role, and explicitly configure the replication rule to encrypt replicas using Account B's destination KMS key.
B. Take no further action — SSE-KMS-encrypted objects replicate automatically once Cross-Region Replication is enabled, so the issue must be an unrelated networking problem.
C. Convert all source objects to SSE-S3 before enabling replication, since objects encrypted with SSE-KMS can never be replicated cross-account.
D. Export the source CMK's key material from Account A and import it into a new CMK in Account B so both accounts share identical key material.
E. (not applicable — single-answer)

**Correct answer(s):** A

**Why correct:** S3 replication of SSE-KMS-encrypted objects requires explicit additional configuration: the replication rule must specify a destination encryption key, and the replication role needs permission on both the source and destination CMKs, with both key policies granting that role access — none of which happens automatically just by enabling CRR.

**Why each wrong option is wrong:** B is factually incorrect — SSE-KMS objects are the documented exception that do not replicate under default settings without extra KMS configuration, which is precisely why the test objects (unencrypted) succeeded while the KMS ones silently failed. C is unnecessary since SSE-KMS objects absolutely can be replicated with correct configuration. D is not how AWS KMS works — a CMK's key material generated by AWS cannot be exported/extracted this way (only imported, externally-sourced key material can be re-imported, and this isn't a valid cross-account key-sharing mechanism).

**Trigger words:** "encrypted with SSE-KMS," "separate customer managed key that Account B fully controls," "not appearing in the destination bucket... while unencrypted test objects replicate fine."

**Underlying architectural principle:** SSE-KMS-encrypted objects require explicit KMS key permissions and a destination-key configuration on the replication rule itself — they are not replicated "for free" the way SSE-S3 or unencrypted objects are.

---

### Question 25 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A small photo-sharing startup stores user-uploaded images in S3 and needs encryption at rest enabled for basic due diligence. The team does not need to audit individual decrypt calls, does not need a custom key rotation schedule, and has no plan to share encryption keys across AWS accounts. They want the lowest-cost, lowest-operational-overhead option available.

**Options:**
A. Enable default bucket encryption using SSE-S3 (Amazon S3 managed keys).
B. Enable default bucket encryption using SSE-KMS with a newly created customer managed key and a custom rotation schedule.
C. Require every client application to supply its own encryption key on each request using SSE-C.
D. Implement client-side encryption in the mobile app before any image is uploaded to S3.

**Correct answer(s):** A

**Why correct:** SSE-S3 provides encryption at rest with zero key management overhead and no additional cost, which is exactly sufficient when there is no requirement to audit key usage, control a key policy, or rotate on a custom schedule.

**Why each wrong option is wrong:** B introduces KMS request costs and key-policy management for a requirement that explicitly doesn't need that control. C requires every client to manage and transmit its own key on every request, adding significant operational and security burden for no stated benefit. D requires building and maintaining a client-side encryption/key-management system, far exceeding what "basic due diligence" requires.

**Trigger words:** "does not need to audit," "no custom key rotation schedule," "no plan to share... across AWS accounts," "lowest-cost, lowest-operational-overhead."

**Underlying architectural principle:** SSE-S3 is the correct default whenever a scenario needs "encryption at rest" with no additional control, audit, or sharing requirements — adding SSE-KMS, SSE-C, or client-side encryption without such a requirement is over-engineering.

---

### Question 26 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retail brokerage firm must retain trade confirmation records in S3 for 6 years to satisfy SEC Rule 17a-4, which mandates that records be stored in a non-rewriteable, non-erasable format that cannot be altered or deleted by any party — including the firm's own system administrators and AWS account root user — before the retention period expires. The firm still needs to be able to upload new versions of ongoing records and wants old, expired versions to eventually age out automatically once compliant.

**Options:**
A. Enable S3 Object Lock in Compliance mode with a 6-year retention period and versioning enabled on the bucket.
B. Enable S3 Object Lock in Governance mode with a 6-year retention period, and remove `s3:BypassGovernanceRetention` from every IAM policy in the account.
C. Enable versioning and S3 MFA Delete on the bucket, and rely on a restrictive bucket policy denying `s3:DeleteObject` to all principals.
D. Apply a Legal Hold to every object in the bucket, with no retention period set, and instruct administrators not to remove the hold for 6 years.

**Correct answer(s):** A

**Why correct:** Compliance mode is the only Object Lock mode that guarantees no principal — including the root user — can shorten retention or delete/overwrite a locked version before the retention period expires, which directly satisfies the "cannot be altered by any party, including administrators" requirement of SEC 17a-4.

**Why each wrong option is wrong:** B's protection depends entirely on IAM permissions staying correctly configured forever; a future misconfiguration, or granting `s3:BypassGovernanceRetention` to an over-privileged role, lets that role delete or overwrite locked objects before the retention period ends, which does not meet an "including administrators/root" bar. C's bucket policy can be modified or deleted by an account administrator at any time, so it provides no true WORM guarantee. D's Legal Hold has no fixed retention/expiration behavior and depends on humans never removing it — it's designed for indefinite litigation holds, not a defined 6-year regulatory retention schedule.

**Trigger words:** "cannot be altered or deleted by any party, including... AWS account root user," "SEC Rule 17a-4," "non-rewriteable, non-erasable."

**Underlying architectural principle:** When a scenario says protection must hold even against administrators or the root user, only S3 Object Lock Compliance mode (among S3-native controls) provides that guarantee — Governance mode and bucket-policy-based deletion prevention both remain overridable by sufficiently privileged identities.

---

### Question 27 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A defense contractor's compliance program requires that a specific S3 bucket only ever contain objects encrypted with one designated customer managed KMS key. Any upload attempt that explicitly specifies SSE-S3 or a different KMS key must be rejected outright by S3 — not silently re-encrypted or allowed through — while uploads that omit an encryption header entirely are acceptable, since the bucket's default encryption is expected to transparently apply the designated CMK to them. A recent internal audit found that an application team had explicitly requested SSE-S3 on some uploads and those objects were accepted anyway, even though the bucket's default encryption was already set to the designated CMK. The team needs a combination of controls that closes this gap without breaking legitimate uploads that already specify the correct key (or that omit the header and rely on the default).

**Options:**
A. Configure the bucket's default encryption setting to SSE-KMS using the designated customer managed key.
B. Add a bucket policy statement that denies `s3:PutObject` unless the request's `x-amz-server-side-encryption` header equals `aws:kms` and its `x-amz-server-side-encryption-aws-kms-key-id` header matches the designated CMK's ARN exactly.
C. Enable S3 Object Lock in Governance mode on the bucket.
D. Rely solely on the bucket's default encryption setting, since S3 always overrides any client-specified encryption header with the bucket default.
E. Enable S3 Transfer Acceleration on the bucket so that all in-flight objects are automatically encrypted using the designated CMK before storage.

**Correct answer(s):** A, B

**Why correct:** Default encryption (A) ensures uploads that omit encryption headers entirely are encrypted with the correct CMK — which the requirement accepts — but it does not stop a client from explicitly requesting a different algorithm or key — that gap is exactly what the audit exposed. Only an explicit deny condition in the bucket policy (B) can guarantee rejection of any PUT that explicitly names a non-compliant algorithm or key, which is what's needed together with the default setting to fully close the gap.

**Why each wrong option is wrong:** C's Object Lock controls write-once-read-many retention behavior and has nothing to do with which encryption key is used. D is factually wrong and is the root cause of the audit finding — default encryption does not override an explicitly specified encryption header, it only applies when no header is present. E is unrelated; Transfer Acceleration is a network-path performance feature for faster uploads over the AWS backbone, it does not perform or enforce any encryption.

**Trigger words:** "explicitly specifies SSE-S3 or a different KMS key... rejected outright," "explicitly requested SSE-S3... accepted anyway, even though the bucket's default encryption was already set," "combination of controls."

**Underlying architectural principle:** Default bucket encryption only fills in a *missing* encryption specification; enforcing a specific key against *explicit* client overrides requires a bucket policy condition that denies non-compliant requests outright.

---

### Question 28 [Priority: P2] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media post-production studio handles content under contracts that require the studio itself — not AWS — to generate, hold, and control every encryption key used, down to supplying the exact key material on each individual request. The studio still wants Amazon S3 to perform the actual server-side encryption and decryption operations rather than encrypting content in their own application before upload, and is willing to transmit the key material over HTTPS with every PUT and GET request.

**Options:**
A. Use SSE-C (server-side encryption with customer-provided keys), supplying the key material in the request headers for every upload and download.
B. Use SSE-S3 with S3-managed keys, which already satisfies "the studio controls the key" since AWS manages it on their behalf.
C. Use SSE-KMS with a customer managed key, since a CMK gives the studio full control over the key policy.
D. Use client-side encryption with a custom encryption library, encrypting objects before they ever leave the studio's application.

**Correct answer(s):** A

**Why correct:** SSE-C is the specific S3 encryption mode designed for exactly this requirement: the customer supplies and manages the key material entirely outside AWS, providing it on each request, while S3 still performs the actual server-side encrypt/decrypt work — AWS never stores the key.

**Why each wrong option is wrong:** B is the opposite of the requirement — with SSE-S3 the key is fully AWS-managed and never touched by the customer at all. C still leaves the key stored and managed inside AWS KMS, not held/supplied directly by the studio per request as required. D means AWS never performs the encryption at all (S3 only ever sees ciphertext), which contradicts the explicit requirement that S3 perform the encryption operation.

**Trigger words:** "the studio itself... must generate, hold, and control every encryption key," "supplying the exact key material on each individual request," "wants Amazon S3 to perform the actual... encryption."

**Underlying architectural principle:** SSE-C is the narrow answer for "customer supplies the key per request, but AWS still does the encryption work" — distinct from SSE-KMS (AWS holds the key, customer controls the policy) and client-side encryption (AWS never sees the key or the plaintext).

---

### Question 29 [Priority: P3] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A real-time ad-tech bidding platform ingests millions of small JSON objects per minute into an S3 bucket encrypted with SSE-KMS using a single customer managed key, which is also used by several other buckets across the account for compliance-driven audit consistency. During a traffic surge, application logs begin showing `ThrottlingException: Rate exceeded for GenerateDataKey` on a growing percentage of S3 PUT and GET requests. Compliance mandates continued use of a customer managed KMS key with full CloudTrail audit logging of key usage, ruling out any change that removes KMS from the encryption path, and engineering wants a fix deployable within hours, not a redesign.

**Options:**
A. Request a KMS request-rate quota increase for the account/Region via AWS Support or Service Quotas, and/or reduce the number of `GenerateDataKey` calls needed per object by using data key caching (for example, via the AWS Encryption SDK).
B. Change the bucket's default encryption from SSE-KMS to SSE-S3 to eliminate all KMS API calls from the request path.
C. Enable S3 Transfer Acceleration on the bucket, since it reduces the number of KMS `GenerateDataKey` calls required per object.
D. Migrate all objects to SSE-C so the application supplies its own key material and bypasses the KMS API entirely.

**Correct answer(s):** A

**Why correct:** The throttling is a documented KMS API request-rate quota limitation: cryptographic operations like `GenerateDataKey`, `Encrypt`, and `Decrypt` on symmetric keys share a single quota per AWS account per Region (not a quota scoped to an individual CMK), and that quota is exactly what a traffic surge can exceed. The correct, compliant fix is to raise that account/Region quota via Service Quotas or AWS Support, and/or reduce the number of calls needed through data key caching — not to abandon the encryption approach the compliance requirement mandates. Note that splitting traffic across multiple CMKs would not by itself relieve this throttling, since the quota is shared across all symmetric keys in the account and Region regardless of how many distinct CMKs are involved.

**Why each wrong option is wrong:** B directly violates the compliance mandate to keep a customer managed KMS key with audit logging in the encryption path. C is irrelevant — Transfer Acceleration optimizes network transfer routing and has no effect on the number of KMS API calls generated per object. D also abandons KMS entirely (violating compliance) and additionally shifts significant key-management burden onto the application at a scale where it would be operationally very difficult.

**Trigger words:** "ThrottlingException: Rate exceeded for GenerateDataKey," "rules out any change that removes KMS from the encryption path," "fix deployable within hours, not a redesign."

**Underlying architectural principle:** High-throughput SSE-KMS workloads can hit KMS's own shared, per-account-per-Region API request-rate quota (independent of S3's request limits, and not a per-key quota — spreading requests across multiple CMKs does not increase the available throughput); the fix is a quota increase and/or reducing call volume via data key caching, never switching encryption type when compliance requires KMS.

---

### Question 30 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A large enterprise consolidates finance, marketing, and data-science datasets into a single shared S3 bucket to reduce storage sprawl. Each of the three teams needs a distinct set of permissions scoped to its own prefix within the bucket (finance: read/write to `/finance/*` only; marketing: read-only to `/marketing/*`; data science: read-only across all three prefixes for cross-team analytics), and the security team wants each team's access managed and audited independently without constructing one increasingly complex, hard-to-review bucket policy that has to be edited every time a team's needs change.

**Options:**
A. Create a separate S3 Access Point for each team, scoped to the relevant prefix(es), with an access point policy defining that team's specific permissions, optionally layered under a minimal baseline bucket policy for defense-in-depth.
B. Continue using a single bucket policy, adding a new, clearly labeled statement block for each team as requirements evolve.
C. Split the shared bucket into three separate buckets — one per team — and use S3 Cross-Region Replication to keep data science's read access synchronized with the other two.
D. Attach only IAM identity-based policies to each team's roles referencing the shared bucket ARN and prefix conditions, with no other bucket-level controls.

**Correct answer(s):** A

**Why correct:** S3 Access Points are purpose-built for exactly this scenario — multiple teams/applications needing distinct permission sets to a shared bucket — giving each team its own named access point, DNS endpoint, and independently manageable policy, without one monolithic bucket policy growing unmanageable.

**Why each wrong option is wrong:** B is the exact anti-pattern the team wants to avoid — a single bucket policy that keeps growing and becomes harder to review and audit as more teams are added. C introduces unnecessary architectural complexity (three buckets plus replication) to solve what is fundamentally an access-management problem, not a data-partitioning one, and CRR doesn't provide live read-through access, only asynchronous copies. D ignores that resource-level controls are still valuable for defense-in-depth and doesn't provide the clean, per-team management boundary (separate policy, separate endpoint) that Access Points offer.

**Trigger words:** "distinct set of permissions scoped to its own prefix," "managed and audited independently," "increasingly complex, hard-to-review bucket policy."

**Underlying architectural principle:** Use S3 Access Points when multiple applications or teams need differentiated access to a shared bucket at scale — they decompose one unwieldy bucket policy into multiple independently manageable, named policies.

---

### Question 31 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A payment processor handling cardholder data under PCI-DSS must guarantee that absolutely no request to a specific S3 bucket ever succeeds over plain HTTP, regardless of which IAM principal makes the request, including principals the security team may not yet know about (contractors, forgotten service accounts, future roles). An internal review found that some legacy scripts were still occasionally reaching the bucket over unencrypted HTTP by using an S3 SDK path that didn't default to TLS.

**Options:**
A. Add a bucket policy statement that denies all S3 actions on the bucket and its objects when the condition `aws:SecureTransport` is `false`.
B. Enable default encryption (SSE-KMS) on the bucket, which also enforces that all connections to the bucket use TLS.
C. Attach an IAM policy to every known IAM user and role denying `s3:GetObject` and `s3:PutObject` whenever the request is made over HTTP.
D. Enable S3 Object Lock in Compliance mode, which rejects any request that does not arrive over an encrypted channel.
E. (not applicable — single-answer)

**Correct answer(s):** A

**Why correct:** A resource-based bucket policy with a `Deny` on `aws:SecureTransport: false` is evaluated against every single request to that bucket regardless of the calling principal's identity — including principals not yet created — because it's enforced at the resource level, not per-identity.

**Why each wrong option is wrong:** B is a common misconception — at-rest encryption settings have no effect on the transport protocol used to reach the bucket; SSE-KMS does not force TLS. C only protects the identities the security team remembers to update, failing exactly the "principals we don't yet know about" requirement, and is an operationally fragile, per-principal approach compared to a single resource-level rule. D's Object Lock governs write-once-read-many retention behavior for object versions, not the transport protocol of the connection.

**Trigger words:** "no request... ever succeeds over plain HTTP, regardless of which IAM principal," "principals the security team may not yet know about," "occasionally reaching the bucket over unencrypted HTTP."

**Underlying architectural principle:** To enforce encryption in transit universally and future-proof against unknown principals, use a resource-based policy condition (`aws:SecureTransport`) on the bucket itself rather than per-identity IAM policies, which only cover principals you remember to configure.

---

### Question 32 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A platform team is documenting KMS key rotation behavior for an internal security runbook ahead of a compliance audit, covering a mix of symmetric customer managed keys, an asymmetric CMK used for code signing, an HMAC key used for message authentication, a CMK created from imported external key material, and several AWS managed keys used by default service encryption. They need to identify exactly two statements below that are factually accurate to include in the runbook.

**Options:**
A. Automatic key rotation is only supported for symmetric encryption customer managed keys — the asymmetric and HMAC keys require a manual rotation process instead.
B. The rotation period for a customer managed key with automatic rotation enabled can now be configured to a custom interval (roughly 90 to 2560 days) rather than being fixed at exactly 365 days.
C. When a CMK's key material rotates, the previous key material is deleted immediately, so any ciphertext encrypted under the prior key version becomes permanently undecryptable.
D. AWS managed keys (`aws/service-name`) are never rotated automatically and must be rotated manually by the account owner on their own schedule.
E. Enabling automatic rotation on a CMK created from imported key material causes KMS to automatically generate and import fresh key material for that CMK every rotation period.

**Correct answer(s):** A, B

**Why correct:** A is accurate — automatic rotation only applies to symmetric encryption CMKs; asymmetric and HMAC key types are excluded and require manual rotation (create new key/material and cut over). B is accurate — AWS now allows configuring a custom rotation period (roughly 90–2560 days) for CMKs with automatic rotation enabled, rather than a fixed 365-day cycle.

**Why each wrong option is wrong:** C is false — KMS retains all previous key material internally after rotation, transparently using the correct historical version to decrypt old ciphertext; nothing becomes undecryptable due to rotation. D is false — AWS managed keys ARE rotated automatically on a fixed yearly cadence by AWS; the customer simply cannot configure or disable that rotation. E is false — imported key material does not support automatic rotation at all; keeping it current requires manually importing new key material into a new key (or new key version) and updating aliases.

**Trigger words:** "asymmetric CMK... HMAC key... CMK created from imported external key material," "exactly two statements... are factually accurate."

**Underlying architectural principle:** Automatic KMS rotation is scoped narrowly to symmetric CMKs on a configurable (not fixed) schedule, retains old key material for decrypting historical ciphertext, and never applies to asymmetric keys, HMAC keys, imported key material, or AWS managed keys' rotation mechanism (which is automatic but not customer-configurable).

---

### Question 33 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An engineering organization manages several hundred non-secret configuration values for its microservices — feature flags, service endpoint URLs, timeout thresholds — organized hierarchically (e.g., `/app/prod/checkout/timeout-ms`, `/app/staging/checkout/timeout-ms`). Values change infrequently, don't require automatic rotation, and the team wants tight integration with their existing CloudFormation stacks and SSM Automation documents, while keeping cost as close to zero as possible given the sheer number of values involved.

**Options:**
A. Store the values as `SecureString` and `String` parameters in AWS Systems Manager Parameter Store (Standard tier), organized under a hierarchical naming structure.
B. Store each value as an individual secret in AWS Secrets Manager, since it provides stronger encryption guarantees than Parameter Store.
C. Hard-code the values as environment variables baked into each service's container image at build time.
D. Store the values as items in a DynamoDB table with a partition key representing the hierarchical path.

**Correct answer(s):** A

**Why correct:** Parameter Store's Standard tier is free, natively supports hierarchical naming (`/app/prod/...`), integrates directly with CloudFormation and SSM documents, and is purpose-built for exactly this kind of high-volume, infrequently-changing, non-rotated configuration data.

**Why each wrong option is wrong:** B would incur a per-secret cost multiplied across several hundred values for capability (rotation, fine-grained resource policies) the requirement never asks for, making it needlessly expensive. C requires rebuilding and redeploying every container image just to change a single config value, eliminating any runtime flexibility. D works technically but requires building custom read/write tooling and IAM access patterns from scratch, duplicating functionality Parameter Store already provides natively and integrates with CloudFormation out of the box.

**Trigger words:** "organized hierarchically," "don't require automatic rotation," "tight integration with... CloudFormation... SSM Automation," "cost as close to zero as possible."

**Underlying architectural principle:** Parameter Store is the cost-efficient, hierarchical answer for high-volume configuration data without rotation needs; Secrets Manager is reserved for secrets that specifically need native automatic rotation or fine-grained cross-account secret sharing.

---

### Question 34 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A global SaaS company runs an active-active application in us-east-1 and eu-west-1, backed by a DynamoDB Global Table replicated between the two regions. Before writing any record, the application itself performs client-side envelope encryption of the sensitive payload (generating a data key via KMS and encrypting the payload with it) — the ciphertext, not the plaintext, is what's actually stored in the item and replicated by DynamoDB Global Tables. The company requires that failover between regions be near-instantaneous: whichever region's application servers receive traffic must be able to decrypt any record immediately — including records originally encrypted by application servers in the other region — using a purely local KMS API call, with no cross-region call and no re-encryption/conversion step of any kind.

**Options:**
A. Create an AWS KMS multi-Region key, replicate it into eu-west-1, and have the application call the local replica key directly (via the AWS Encryption SDK or native `GenerateDataKey`/`Decrypt` calls) for envelope encryption in whichever region is handling the request — so a data key generated against the key in one region can be decrypted locally against its replica in the other region, with no cross-region call.
B. Create two independent, single-region customer managed keys — one in each region — and use AWS Database Migration Service to re-encrypt data with the target region's key immediately upon failover.
C. Use the AWS managed key for DynamoDB (`aws/dynamodb`) in both regions, since AWS managed keys are global resources automatically available and identical in every region.
D. Use a single-region customer managed key created in us-east-1, and grant the eu-west-1 application role cross-region access to it via a permissive key policy statement, so eu-west-1 servers call the us-east-1 key directly for every decrypt.

**Correct answer(s):** A

**Why correct:** AWS KMS multi-Region keys are sets of related keys — one primary and one or more replicas — that share the same key ID and underlying key material across regions. A data key wrapped by the key in one region can be unwrapped by its replica in another region with a purely local KMS call and no re-encryption step, which is exactly the "encrypt once, decrypt anywhere, instantly" property this failover design needs. AWS documents this specifically for client-side/application-level encryption and active-active, multi-region architectures — it's a property of the application (or the AWS Encryption SDK) calling the key directly, not something DynamoDB's own transparent server-side encryption-at-rest layer automatically inherits just because an MRK happens to sit underneath it (most AWS services that manage their own encryption-at-rest, including S3's default-encryption-plus-replication path, still perform their normal decrypt-and-re-encrypt-at-the-destination behavior even when the configured key is technically a multi-Region key).

**Why each wrong option is wrong:** B introduces an explicit re-encryption step via DMS at failover time, directly violating the "no re-encryption/conversion step" and "near-instantaneous" requirements. C is factually incorrect — AWS managed keys are independent, region-scoped resources with independent key material per region, not a single shared global key, so `aws/dynamodb` in eu-west-1 cannot decrypt something wrapped under `aws/dynamodb` in us-east-1. D is technically possible to configure (a KMS API call can be addressed to a key's home region from anywhere with network connectivity and permissions), but it reintroduces the exact cross-region call the design is trying to eliminate, adds latency, and — critically — creates a hard dependency on us-east-1's availability: if us-east-1 is the region experiencing the outage that triggered failover, eu-west-1 could lose the ability to decrypt anything at all, the opposite of resilient failover.

**Trigger words:** "active-active," "client-side envelope encryption," "no cross-region call and no re-encryption/conversion step," "near-instantaneous... whichever region."

**Underlying architectural principle:** KMS multi-Region keys let an application encrypt with one regional key and decrypt with its interoperable replica in another region using only local API calls — this benefit applies to how the *application* (or the AWS Encryption SDK) directly calls KMS for envelope encryption. Most AWS services that transparently manage their own encryption-at-rest (S3 default encryption plus replication, DynamoDB's own SSE) still perform their usual decrypt-and-re-encrypt-at-the-destination behavior even when the underlying key is a multi-Region key, so multi-Region keys don't automatically make *those* managed-replication paths re-encryption-free — only direct, application-level key usage reliably gets that property.

---

### Question 35 [Priority: P1] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A telehealth SaaS platform stores electronic protected health information (ePHI) subject to HIPAA. Traffic flows from patient browsers to an Application Load Balancer, then to EC2 application servers, which write clinical notes into an S3 bucket. The security team requires that ePHI be encrypted at rest using a customer managed key that they can disable at any moment to instantly and completely revoke all access to stored data, and that all network traffic carrying ePHI — from the browser all the way to storage — be encrypted, with no segment of the path ever carrying plaintext ePHI over the network. Cost and RTO are not primary constraints for this particular design decision; correctness of the security control is. Select the two actions that together satisfy both requirements.

**Options:**
A. Configure HTTPS-only listeners on the ALB using an ACM-issued certificate, configure the ALB's target group to use HTTPS as the backend protocol (so the ALB re-encrypts traffic to the EC2 instances rather than forwarding it as plain HTTP), and add a bucket policy statement denying any S3 request where `aws:SecureTransport` is `false` — ensuring every network hop carrying ePHI (browser-to-ALB, ALB-to-EC2, and EC2-to-S3) is TLS-encrypted end to end.
B. Set the S3 bucket's default encryption to SSE-KMS using a customer managed key whose key policy restricts `kms:Decrypt` to only the application's EC2 instance role, so the security team can disable the key at any time to immediately block all data access.
C. Configure the ALB in raw TCP pass-through mode so encrypted traffic reaches the EC2 instances without the ALB terminating TLS at all, eliminating the need to manage a certificate.
D. Rely on the default encryption AWS automatically applies to all new S3 buckets (SSE-S3), since it already satisfies HIPAA's at-rest encryption expectations without any additional key management.
E. Store clinical notes in S3 without encryption, relying entirely on IAM policies to restrict access, since HIPAA's Security Rule addresses access control rather than encryption specifically.

**Correct answer(s):** A, B

**Why correct:** A guarantees encryption in transit across all three hops (browser-to-ALB via TLS termination, ALB-to-EC2 via an HTTPS backend/target-group protocol so the ALB re-encrypts before forwarding, and EC2-to-S3 enforced via the `aws:SecureTransport` deny condition), while B guarantees at-rest encryption under a customer managed key whose disablement instantly cuts off `kms:Decrypt` for every consumer, satisfying the "instantly and completely revoke all access" requirement — something only a CMK the security team controls can provide.

**Why each wrong option is wrong:** C is not achievable with an Application Load Balancer — raw TCP pass-through without TLS termination is an NLB (Layer 4) capability, not an ALB (Layer 7) one, and removing certificate management doesn't address the stated encryption or key-control requirements anyway. D fails the explicit "customer managed key they can disable to instantly revoke access" requirement, since SSE-S3 uses an AWS-controlled key the customer cannot disable or control. E fails the at-rest encryption requirement outright by leaving ePHI unencrypted, which does not meet the security team's explicit mandate regardless of how HIPAA's addressable specifications are interpreted elsewhere.

**Trigger words:** "customer managed key that they can disable... to instantly and completely revoke all access," "no segment of the path ever carrying plaintext ePHI over the network," "correctness of the security control is [the primary constraint]."

**Underlying architectural principle:** Meeting a combined "instant revocation" plus "true end-to-end transit encryption" requirement needs two independent controls — a customer managed KMS key (for at-rest, revocable-by-disable) and enforced TLS at *every* hop (client-facing ALB HTTPS listener, an HTTPS backend/target-group protocol so the ALB-to-instance leg isn't silently downgraded to plain HTTP, and a bucket-level `aws:SecureTransport` deny for the application-to-S3 leg) — neither control alone satisfies both halves of the requirement, and it's easy to forget the ALB's backend leg since ALBs default to HTTP there unless explicitly configured otherwise.

---

### Question 36 [Priority: P2] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A logistics company needs to share a database credential secret with a trusted partner's Lambda function running in the partner's own AWS account, so the partner's function can query a shared reporting database. The company does not want to duplicate the secret into the partner's account, does not want to create any IAM users for the partner, and needs the ability to revoke the partner's access instantly by removing a single policy statement if the partnership ends.

**Options:**
A. Attach a resource-based policy to the AWS Secrets Manager secret granting the partner account's specific IAM role ARN `secretsmanager:GetSecretValue`, and update the secret's encryption key policy (if a customer managed key is used) to also grant that role `kms:Decrypt`.
B. Export the secret's plaintext value and share it with the partner over an encrypted email so they can store it in their own Secrets Manager instance.
C. Create an IAM user in the logistics company's account scoped only to that secret, and issue the partner a long-lived access key.
D. Store the value in a Systems Manager Parameter Store `SecureString` instead, since Parameter Store has stronger native cross-account resource-based policy support than Secrets Manager.
E. (not applicable — single-answer)

**Correct answer(s):** A

**Why correct:** Secrets Manager secrets support native resource-based (secret) policies that can name a specific external account's principal, enabling direct cross-account access to a single secret with no duplication, no shared credentials, and instant revocation by removing the policy statement — and if a CMK protects the secret, the key policy must grant the same principal decrypt access as well.

**Why each wrong option is wrong:** B creates a duplicated, unmanaged copy of the secret with no central revocation point and introduces an insecure sharing channel. C reintroduces exactly the long-lived-credential-sharing pattern the company wants to avoid, with none of the auditability of resource-based cross-account access. D is factually backwards — Secrets Manager, not Parameter Store, has the more mature native cross-account resource-based policy support for secret sharing.

**Trigger words:** "does not want to duplicate the secret," "no IAM users for the partner," "revoke the partner's access instantly by removing a single policy statement."

**Underlying architectural principle:** Cross-account access to a single, specific secret without duplicating it or issuing credentials is achieved via a resource-based (secret) policy on the Secrets Manager secret — paired with the KMS key policy if a CMK is used — rather than any IAM-user-and-key-sharing pattern.

---

### Question 37 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A pharmaceutical company's compliance mandate requires that every object in a specific S3 bucket be encrypted with one designated customer managed KMS key — CMK "alpha." Any upload attempt that explicitly specifies a different key or SSE-S3 must be rejected outright by S3 itself; uploads that omit an encryption specification entirely are acceptable, since the bucket's default encryption — already configured to use CMK alpha — fills that in automatically. During an incident review, the security team discovers that a misconfigured internal tool has been successfully uploading objects encrypted with CMK "beta" (a different customer managed key the tool's IAM role also happens to have permission to use) by explicitly specifying that key on each PUT request.

**Options:**
A. Add a bucket policy statement denying `s3:PutObject` unless the request's `x-amz-server-side-encryption` header equals `aws:kms` and its `x-amz-server-side-encryption-aws-kms-key-id` header exactly matches CMK alpha's ARN.
B. Revoke the misconfigured tool's IAM role's `s3:PutObject` permission entirely on that bucket, since removing the tool's write access is the most direct fix.
C. Re-save the bucket's default encryption setting to CMK alpha again, since default encryption settings can silently degrade over time and need periodic reapplication.
D. Enable S3 Object Lock in Governance mode on the bucket to prevent uploads that don't match the compliance-designated key.

**Correct answer(s):** A

**Why correct:** Default bucket encryption only applies when a request omits an encryption specification — it does not override or block a request that explicitly names a different key, which is exactly how CMK beta got through. Only an explicit deny condition scoped to CMK alpha's ARN in the bucket policy will reject any PUT that doesn't specify exactly that key, closing the gap regardless of what the calling role's IAM permissions otherwise allow.

**Why each wrong option is wrong:** B only stops this one specific tool and doesn't create a durable, bucket-wide guarantee against any future misconfigured client explicitly specifying the wrong key. C is based on a false premise — default encryption settings don't "degrade" and re-saving it would not have prevented an explicit key override in the first place. D's Object Lock governs WORM retention/deletion behavior for object versions, not which encryption key is permitted on upload.

**Trigger words:** "explicitly specifying that key on each PUT request," "successfully uploading objects encrypted with CMK 'beta'... even though the bucket's default encryption was already configured to use CMK alpha."

**Underlying architectural principle:** Enforcing that only one specific KMS key is ever accepted for uploads requires an explicit bucket-policy deny keyed on the KMS key ARN header — default encryption alone never blocks an explicitly specified alternate key or algorithm.

---

### Question 38 [Priority: P2] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A pharmaceutical company must retain clinical trial documents in S3 for 10 years under FDA regulation, with an absolute mandate that not even the company's own AWS account root user can delete the documents or shorten their retention period before the 10 years elapse. Separately, to protect against ransomware and insider threats within the primary AWS account, the company also wants an independent, equally immutable copy of every document maintained in a completely separate AWS account owned by an external compliance auditor, so a compromise of the primary account cannot affect the auditor's copy. Select the two actions that together satisfy both requirements.

**Options:**
A. Enable versioning and S3 Object Lock in Compliance mode with a 10-year retention period on the primary bucket.
B. Configure S3 Replication (Same-Region or Cross-Region) from the primary bucket to a bucket in the auditor's separate AWS account, with the destination bucket also configured with versioning and Object Lock in Compliance mode, using the replication owner override option (`AccessControlTranslation`) so the auditor's account owns the replicated objects.
C. Enable S3 Object Lock in Governance mode on the primary bucket, and grant the compliance team's role `s3:BypassGovernanceRetention` so they retain a documented, centrally audited way to manage exceptions.
D. Add an S3 lifecycle rule that transitions objects older than 30 days to S3 Glacier Deep Archive in the auditor's AWS account to reduce long-term storage cost.
E. Attach an IAM permissions boundary to every role and user in the primary account that denies `s3:DeleteObject`, ensuring even the root user cannot remove the documents.

**Correct answer(s):** A, B

**Why correct:** Compliance mode (A) is the only Object Lock mode that blocks deletion or retention-shortening by every principal, including the root user, satisfying the first requirement on the primary bucket. Replication to a bucket in the auditor's own account with the owner override option and its own Compliance-mode Object Lock configuration (B) creates the independently owned, equally immutable second copy needed to survive a compromise of the primary account.

**Why each wrong option is wrong:** C explicitly grants a bypass permission, which directly contradicts an "absolute mandate" that no one — including administrators — can override the retention, and Governance mode's protection depends entirely on that permission staying restricted. D is not a valid mechanism for placing a copy into a different AWS account — S3 lifecycle rules operate within the same bucket/account and cannot target a bucket owned by another account, so it fails the "separate AWS account" requirement entirely. E is ineffective because IAM permissions boundaries do not apply to (and cannot restrict) the AWS account root user, which directly fails the "not even the root user" requirement — one of several documented cases where root remains unrestricted by an IAM-layer control.

**Trigger words:** "not even the company's own AWS account root user," "completely separate AWS account owned by an external compliance auditor," "a compromise of the primary account cannot affect the auditor's copy."

**Underlying architectural principle:** Achieving both "immutable even against root" and "immutable, independently-owned off-account copy" requires layering S3 Object Lock Compliance mode on both the primary bucket and a cross-account replica (with the replication owner override option) — permissions boundaries and Governance-mode bypasses cannot satisfy a "not even root/admins" requirement.

---

### Question 39 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company is launching a new public-facing web application behind an Application Load Balancer and wants all browser traffic encrypted end-to-end using a certificate that is free and renews automatically with no manual intervention. They also want any request that arrives on plain HTTP to be automatically redirected to HTTPS, and want to avoid any custom certificate-management process for a small internal team with no PKI experience.

**Options:**
A. Request a public TLS certificate through AWS Certificate Manager (ACM), attach it to an HTTPS listener on the ALB, and add a listener rule that redirects HTTP:80 traffic to HTTPS:443.
B. Generate a self-signed certificate using OpenSSL and upload it to IAM for use as the ALB's certificate.
C. Configure only an HTTP listener on the ALB, and enable an "Enforce HTTPS" flag on the target group to upgrade connections automatically.
D. Store a certificate as a Secrets Manager secret and reference the secret ARN directly in the ALB's target group configuration.

**Correct answer(s):** A

**Why correct:** ACM issues free public certificates that auto-renew with zero manual steps, and attaching one to an ALB HTTPS listener plus a redirect rule for the HTTP listener is the standard, fully managed pattern for end-to-end encrypted traffic with automatic HTTP-to-HTTPS redirection.

**Why each wrong option is wrong:** B requires manual certificate generation and renewal, and browsers will show trust warnings for a self-signed certificate, defeating the "free, auto-renewing" and end-user-trust requirements. C describes a non-existent ALB feature — there is no target-group-level flag that "enforces HTTPS" on an HTTP-only listener; TLS termination requires an actual HTTPS listener with a certificate. D is not how ALB certificates work — target groups don't reference certificates via Secrets Manager ARNs; certificates are attached directly to HTTPS/TLS listeners, typically sourced from ACM (or IAM for imported certs).

**Trigger words:** "free and renews automatically with no manual intervention," "avoid any custom certificate-management process," "no PKI experience."

**Underlying architectural principle:** ACM-issued public certificates attached to an ALB HTTPS listener, paired with an HTTP-to-HTTPS redirect rule, is the standard zero-maintenance pattern for enforcing encryption in transit on a public web application.

---

### Question 40 [Priority: P3] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A defense contractor imported its own externally generated key material into a KMS customer managed key (BYOK) to satisfy a regulatory requirement about key provenance, and separately maintains an asymmetric CMK used to sign software release artifacts. Security policy requires periodically refreshing the cryptographic material behind both keys, but the team must retain the ability to decrypt data encrypted under the older material (for the imported-material key) and verify signatures created with the older material (for the asymmetric key) after each refresh. A junior engineer proposes simply toggling on "automatic key rotation" in the KMS console for both keys to satisfy the policy.

**Options:**
A. For the imported-material CMK, import new key material into the same key and perform on-demand rotation (`kms:RotateKeyOnDemand`) so the key ID/ARN never changes and KMS automatically retains the prior key material to decrypt data encrypted before the rotation. For the asymmetric signing CMK — which supports neither automatic nor on-demand rotation — manually create a new CMK, use a key alias to point new signing operations at it going forward, and keep the original CMK enabled and available to verify signatures created before the cutover.
B. Enable the automatic key rotation toggle on both keys — as of 2026, KMS extended automatic rotation support to all key types, including imported key material and asymmetric keys.
C. Delete the old CMK immediately once new key material is imported, since retaining old, "rotated-out" key material anywhere is itself a compliance risk.
D. Configure AWS Certificate Manager to manage rotation of the underlying KMS key material automatically on the team's behalf.

**Correct answer(s):** A

**Why correct:** Neither imported key material nor asymmetric keys support *automatic* rotation. Imported (`EXTERNAL` origin) symmetric key material does, however, support *on-demand* rotation: you import new key material into the existing key (placing it in a "pending rotation" state) and then call `RotateKeyOnDemand`, which rotates in place — same key ID, same ARN, no application changes — while KMS keeps the previous key material available to decrypt older ciphertext. Asymmetric CMKs support neither automatic nor on-demand rotation at all, so refreshing the signing key's material requires the fully manual pattern: create a new CMK, cut new signing traffic over to it via an alias, and retain the original CMK (still enabled) so old signatures remain verifiable.

**Why each wrong option is wrong:** B is factually false — KMS automatic rotation remains unsupported for imported key material and asymmetric (and HMAC) keys; the junior engineer's proposal would silently fail to achieve anything for either key. C is unsafe — deleting the old key material immediately, without first ensuring nothing still needs to decrypt old ciphertext or verify old signatures, breaks that access with no recovery path (KMS key deletion is deliberately delayed/irreversible-after-waiting-period for this reason). D is not a real capability — ACM manages TLS certificates, not KMS key material, and has no role in KMS key rotation.

**Trigger words:** "imported its own externally generated key material," "asymmetric CMK used to sign," "retain the ability to decrypt... and verify signatures created with the older material," "simply toggling on 'automatic key rotation.'"

**Underlying architectural principle:** Automatic key rotation is available only for symmetric CMKs; on-demand rotation additionally covers symmetric CMKs with imported key material (rotate in place via `RotateKeyOnDemand` after importing new material — same key ID, old material retained automatically for decryption). Asymmetric keys, HMAC keys, and custom-key-store keys support neither and must be refreshed via the fully manual create-new-key-and-alias-over process, always while deliberately retaining the old key to preserve access to data or signatures created under it.

---

### Question 41 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A three-tier web application runs in a VPC with public web servers in a public subnet and application servers in a private subnet. The security team wants the web tier's security group to allow inbound HTTPS from the internet, and wants the application tier's security group to allow inbound traffic on port 8080 only from instances that carry the web tier's security group — not from any specific hardcoded IP range, since web tier instances scale in and out constantly and their private IPs change.

**Options:**
A. In the application tier's security group inbound rule, set the source to the web tier's security group ID rather than a CIDR range.
B. In the application tier's security group inbound rule, set the source to the VPC's CIDR block, since that covers all current and future web tier instance IPs.
C. Create a NACL rule on the private subnet allowing inbound traffic on port 8080 only from the public subnet's CIDR range.
D. Hardcode the current Auto Scaling group's instance private IPs into the application tier's security group and update the rule via a scheduled Lambda function every time the group scales.

**Correct answer(s):** A

**Why correct:** Security groups can reference another security group ID as the source, which automatically includes any instance (current or future) that has that security group attached — exactly matching the requirement to allow traffic from "the web tier" as a role, regardless of changing IPs.

**Why each wrong option is wrong:** B is far too broad, allowing any resource anywhere in the VPC (including future unrelated subnets/services) to reach port 8080, violating least privilege. C uses subnet-level CIDR matching, which permits any instance in the public subnet — not specifically web tier instances — and NACLs are a coarser, less precise tool for this kind of role-based rule. D reintroduces exactly the brittle, high-maintenance IP-tracking problem the team is trying to avoid, and duplicates functionality security-group-to-security-group references already provide natively.

**Trigger words:** "instances that carry the web tier's security group," "not from any specific hardcoded IP range," "private IPs change."

**Underlying architectural principle:** Reference a security group as the source/destination of another security group's rule whenever the permitted peer is defined by "role" (a group of instances) rather than by a fixed network range — it self-updates as instances scale.

---

### Question 42 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company's security team is troubleshooting a reported outage where application servers in a private subnet can no longer receive return traffic from an external API they call over HTTPS on port 443. The subnet's NACL was recently tightened by a new team member. The NACL currently has an inbound rule allowing TCP port 443 from 0.0.0.0/0, an inbound rule allowing TCP port 22 from a bastion CIDR, and no other inbound allow rules; the outbound rules only allow TCP port 443 to 0.0.0.0/0. The instances' security group is unchanged and correctly allows all outbound traffic.

**Options:**
A. Add an inbound NACL rule allowing TCP traffic on the ephemeral port range (1024–65535) from 0.0.0.0/0, since NACLs are stateless and must explicitly permit the return traffic on the client's ephemeral port.
B. Add an inbound security group rule allowing TCP port 443 from 0.0.0.0/0, since the security group must also explicitly allow the return traffic.
C. Remove the outbound port 443 restriction and allow all outbound traffic on the NACL, since the outbound rule is what's blocking the request from ever leaving the subnet.
D. Reboot the affected instances, since NACL rule changes require an instance restart to take effect.

**Correct answer(s):** A

**Why correct:** NACLs are stateless, so return traffic for an outbound request must be separately permitted by an inbound rule matching the ephemeral port range the client OS used for that connection — the missing ephemeral-port inbound allow is exactly what a "recently tightened" NACL would have removed.

**Why each wrong option is wrong:** B misdiagnoses the layer — security groups are stateful, so a security group only needs to allow the outbound request; it automatically permits the matching inbound return traffic without any separate rule, so this change wouldn't be the fix and isn't necessary. C is wrong because the described outbound rule (port 443 to 0.0.0.0/0) already permits the original outbound request; the problem is the missing inbound rule for the response, not the outbound leg. D is factually incorrect — NACL rule changes apply immediately to new and in-progress evaluations without requiring any instance reboot.

**Trigger words:** "no longer receive return traffic," "NACL was recently tightened," "no other inbound allow rules," stateless implied by symptom.

**Underlying architectural principle:** Because NACLs are stateless, every connection direction must be explicitly permitted on both inbound and outbound, including inbound allowance of the ephemeral port range for responses to outbound-initiated connections — unlike stateful security groups, which auto-permit return traffic.

---

### Question 43 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company suspects that a single compromised EC2 instance's outbound traffic is being used to scan other instances within the same subnet. The security team wants a control that can immediately and explicitly block all traffic — inbound and outbound — to and from one specific instance's IP address, evaluated before that instance's own security group is even consulted, and that can be applied without modifying the security group configuration other teams rely on for that instance.

**Options:**
A. Add explicit deny rules on the subnet's NACL blocking the compromised instance's IP address in both the inbound and outbound rule sets, with a rule number lower than any allow rule.
B. Remove all inbound rules from the compromised instance's security group, leaving only the default outbound allow-all rule.
C. Add a security group rule denying all traffic to and from the compromised instance's IP address.
D. Detach the instance's elastic network interface to physically prevent any further network communication.

**Correct answer(s):** A

**Why correct:** NACLs support explicit deny rules and evaluate every packet crossing the subnet boundary in each direction, independently of the instance's security group. For inbound traffic this NACL evaluation happens before the security group is even consulted; for outbound traffic the NACL still independently enforces the deny after the local security group check runs. Either way, a single low-numbered deny rule targeting that specific IP blocks traffic immediately in both directions without touching the security group other teams depend on.

**Why each wrong option is wrong:** B only removes inbound allow rules but security groups have no explicit "deny" concept — an attacker's existing established connections and any subsequent security-group misconfiguration risk remain, and it still doesn't block outbound traffic, which security groups' default behavior would otherwise still allow. C is not possible — security groups only support allow rules, never explicit deny rules, so this option describes a feature that doesn't exist. D is a valid but far more disruptive and operationally heavier-handed action (it also removes the instance from all other legitimate use immediately and complicates forensics) compared to a targeted, reversible NACL deny rule, and the requirement specifically asks to avoid touching the security group setup others rely on — not to isolate the instance from the network entirely via infrastructure surgery.

**Trigger words:** "explicit deny," "evaluated before that instance's own security group," "without modifying the security group configuration."

**Underlying architectural principle:** Only NACLs support explicit deny rules and operate at the subnet level, independently of and (for inbound traffic) ahead of security group evaluation — security groups are allow-only and stateful, making NACLs the correct tool for an immediate, targeted block affecting both traffic directions without disturbing existing security group rules.

---

### Question 44 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company runs a three-tier VPC and wants to enforce defense-in-depth so that even if an application server's security group is ever misconfigured to accidentally allow inbound traffic from the internet, a second independent layer of network control still blocks any such traffic before it reaches the private application subnet. The team wants this second layer to apply automatically to every instance placed in that subnet, present and future, without needing to be attached to each instance individually, and accepts that legitimate return traffic on ephemeral ports will need to be explicitly permitted as a trade-off.

**Options:**
A. Configure the private application subnet's NACL to allow inbound traffic only from the web tier subnet's CIDR range (and the necessary ephemeral port range for return traffic), denying all other inbound sources by default.
B. Rely exclusively on well-configured security groups on each application instance, since security groups alone are sufficient defense-in-depth by design.
C. Add a second security group to each application instance restricting inbound sources to the web tier's CIDR range, in addition to the existing security group.
D. Configure a route table rule on the private subnet that drops any packet whose source is not within the VPC's CIDR block.

**Correct answer(s):** A

**Why correct:** A subnet-level NACL applies automatically to every instance in that subnet without per-instance attachment, and because NACLs are stateless, it independently enforces source restrictions and requires explicitly permitting ephemeral-port return traffic — exactly the described second, independent layer that still functions even if a security group is misconfigured.

**Why each wrong option is wrong:** B provides only a single layer of control; if that one security-group layer is misconfigured (the exact failure mode the scenario is defending against), there is no independent backstop, so it fails the explicit defense-in-depth requirement. C still requires per-instance attachment (violating "applies automatically... without needing to be attached to each instance") and, being another security group, is evaluated at the same layer/logic as the original misconfigured one rather than being an independent second layer — worse, because multiple security groups attached to the same instance are combined additively (the union of all their allow rules applies), a second, more restrictive security group can never revoke access the first, misconfigured one already grants; it can only add further allowances. D describes a capability route tables do not have — route tables direct traffic to targets based on destination, they do not perform source-based packet filtering or dropping.

**Trigger words:** "even if an application server's security group is ever misconfigured," "second independent layer," "applies automatically... without needing to be attached to each instance," "legitimate return traffic on ephemeral ports will need to be explicitly permitted."

**Underlying architectural principle:** Subnet-level NACLs provide an automatically-applied, independent second layer of defense-in-depth behind per-instance security groups precisely because they operate at a different scope (subnet vs. instance) and evaluate rules statelessly and explicitly, unlike security groups.

---

### Question 45 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company is designing a new VPC and wants to document, for a security audit, the fundamental behavioral difference between the security groups and network ACLs they plan to use together. The auditor specifically asks: if an EC2 instance in a subnet initiates an outbound connection to an external service and receives a response, which statement correctly describes how each control evaluates that response traffic by default?

**Options:**
A. The security group automatically allows the stateful return traffic without a matching inbound rule, while the NACL requires an explicit inbound rule permitting the response (typically on the ephemeral port range) because it evaluates each direction statelessly.
B. Both the security group and the NACL automatically allow the stateful return traffic without any explicit inbound rule needed on either.
C. The NACL automatically allows the stateful return traffic without a matching inbound rule, while the security group requires an explicit inbound rule permitting the response.
D. Neither control allows the return traffic automatically; both require explicit matching inbound rules for the response to reach the instance.

**Correct answer(s):** A

**Why correct:** This is the core, well-documented behavioral distinction between the two controls: security groups are stateful (tracking connections so return traffic is automatically permitted) while NACLs are stateless (evaluating every packet independently in each direction, requiring explicit inbound allow rules for responses).

**Why each wrong option is wrong:** B incorrectly states NACLs are stateful, which is the opposite of their documented behavior. C reverses which control is stateful and which is stateless — it is the security group that is stateful, not the NACL. D incorrectly claims security groups also require explicit inbound rules for return traffic, contradicting their stateful nature.

**Trigger words:** "fundamental behavioral difference," "receives a response," "evaluates that response traffic by default."

**Underlying architectural principle:** Security groups are stateful (automatic return-traffic allowance); NACLs are stateless (explicit allow rules required in both directions) — this single distinction underlies nearly every SG-vs-NACL troubleshooting scenario.

---

### Question 46 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company's public-facing website, served through an Application Load Balancer, has recently experienced repeated SQL injection attempts and a Layer 7 HTTP flood that isn't large enough to qualify as a large-scale volumetric event but is still degrading application performance by exhausting backend connection pools with malformed and excessive requests. The security team wants a service that can inspect HTTP request content and block requests matching known injection patterns, while also rate-limiting individual IP addresses that send abnormally high request volumes to specific URI paths.

**Options:**
A. Create an AWS WAF web ACL with a managed SQL injection rule group and a rate-based rule scoped to the relevant URI paths, and associate it with the ALB.
B. Enable AWS Shield Advanced on the ALB, since Shield Advanced inspects HTTP request bodies for injection patterns and enforces per-IP rate limits automatically.
C. Enable AWS Shield Standard on the ALB, since it is included at no additional cost and mitigates all Layer 7 attacks, including application-layer floods and injection attempts.
D. Enable GuardDuty with S3 protection and EKS protection features to detect and automatically block the malicious HTTP requests at the ALB.

**Correct answer(s):** A

**Why correct:** WAF is purpose-built to inspect HTTP request content (headers, body, URI) against rule groups — including managed SQL injection rule sets — and rate-based rules that throttle individual source IPs exceeding a request threshold on specified paths, directly matching both requirements in the scenario.

**Why each wrong option is wrong:** B is factually incorrect — Shield Advanced's value-add is enhanced DDoS protection, cost protection, and 24/7 DRT access; it does not itself perform HTTP content inspection or rule-based request filtering, that's WAF's job (Shield Advanced is commonly paired with WAF, not a substitute for it). C is also incorrect — Shield Standard provides only baseline, automatic protection against common infrastructure-layer (L3/L4) DDoS attacks and does not inspect or filter Layer 7 HTTP request content at all. D misapplies GuardDuty, which is a threat-detection service analyzing logs (VPC Flow Logs, DNS logs, CloudTrail, S3/EKS data events) for anomalous account/resource behavior — it does not inspect or block live HTTP requests at a load balancer.

**Trigger words:** "SQL injection attempts," "inspect HTTP request content," "rate-limiting individual IP addresses... specific URI paths."

**Underlying architectural principle:** AWS WAF is the Layer 7 content-inspection and rate-limiting tool for HTTP(S) traffic (SQLi/XSS rules, rate-based rules); Shield addresses network/transport-layer (and broader infrastructure) DDoS protection, and the two are complementary, not interchangeable.

---

### Question 47 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A publicly traded financial services company running a high-visibility public API on an ALB behind CloudFront is a known, named target for sophisticated, large-scale DDoS campaigns. Executive leadership requires financial protection against usage-based cost spikes (scaling charges) incurred specifically as a result of a DDoS attack, guaranteed access to AWS's specialized DDoS Response Team (DRT) during an active incident, and proactive, near-real-time attack detection and mitigation for complex, multi-vector Layer 3/4/7 events — with cost considered secondary to guaranteed incident response capability.

**Options:**
A. Subscribe to AWS Shield Advanced on the CloudFront distribution and ALB, pair it with AWS WAF for Layer 7 rule enforcement, and maintain a Business, Enterprise On-Ramp, or Enterprise Support plan, which is required in addition to Shield Advanced to contact the DRT directly.
B. Rely on AWS Shield Standard, since it is automatically enabled on CloudFront and ELB at no cost and provides the same DRT access and cost protection as Shield Advanced.
C. Enable AWS Config with conformance packs to continuously monitor and automatically remediate DDoS-related configuration drift in near-real time.
D. Enable GuardDuty with all protection plans (S3, EKS, RDS, Lambda) to detect DDoS traffic patterns and automatically engage the AWS DDoS Response Team.

**Correct answer(s):** A

**Why correct:** Shield Advanced is specifically the tier that adds DDoS cost protection (credits for scaling charges incurred during an attack), 24/7 DRT engagement, and advanced, near-real-time detection/mitigation for complex multi-vector attacks — none of which Shield Standard includes — and it's designed to be paired with WAF for the Layer 7 rule-enforcement component. Note that Shield Advanced alone enables proactive engagement, but direct, on-demand DRT contact additionally requires a Business, Enterprise On-Ramp, or Enterprise Support plan — a detail the scenario's "cost secondary to guaranteed incident response" framing means the company should budget for as well.

**Why each wrong option is wrong:** B is factually wrong — Shield Standard, while free and automatic, explicitly does not include DRT access or DDoS cost protection; those are Shield Advanced-exclusive benefits, which is precisely the gap the scenario's requirements expose. C misapplies AWS Config, which is a configuration compliance and drift-detection/remediation service for resource configurations — it has no DDoS detection, mitigation, or response-team engagement capability. D misapplies GuardDuty, which detects anomalous account and network behavior from logs but does not provide DDoS-specific cost protection, DRT access, or dedicated attack mitigation infrastructure the way Shield Advanced does.

**Trigger words:** "financial protection against usage-based cost spikes," "guaranteed access to AWS's specialized DDoS Response Team," "cost considered secondary to guaranteed incident response capability."

**Underlying architectural principle:** Shield Advanced (not Standard) is required whenever a scenario explicitly needs DDoS cost protection, guaranteed DRT engagement, or advanced multi-vector mitigation — Shield Standard's free, automatic protection covers only common, baseline infrastructure-layer attacks with no cost guarantee or dedicated response team access.

---

### Question 48 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A security engineer is building a company-wide threat-detection and compliance strategy spanning GuardDuty, Macie, Inspector, and Security Hub, and wants to sanity-check the team's understanding before assigning ownership of each service to different sub-teams. Select the two statements below that correctly describe a service's actual, documented purpose.

**Options:**
A. Amazon GuardDuty continuously analyzes VPC Flow Logs, DNS query logs, and CloudTrail management/data events using threat intelligence and machine learning to detect anomalous behavior like cryptomining or compromised credentials.
B. Amazon Macie performs automated vulnerability scanning of EC2 instances and container images stored in Amazon ECR against known CVE databases.
C. AWS Security Hub discovers and classifies sensitive data such as PII within S3 buckets, replacing the need for a separate data-classification service.
D. Amazon Inspector performs automated, continuous vulnerability assessments of EC2 instances, container images in ECR, and Lambda functions against known CVEs and network reachability issues.
E. AWS Security Hub itself scans EC2 instances and container images for CVEs, in addition to aggregating findings from other services.

**Correct answer(s):** A, D

**Why correct:** A is accurate — GuardDuty's core purpose is exactly this log-based anomaly and threat detection across VPC Flow Logs, DNS logs, and CloudTrail. D is accurate — Inspector is the automated vulnerability-assessment service for EC2, ECR images, and Lambda against CVEs and network exposure.

**Why each wrong option is wrong:** B swaps Macie's actual purpose (sensitive-data discovery/classification in S3) for Inspector's purpose (vulnerability scanning) — Macie has no CVE-scanning capability at all. C swaps Security Hub's actual purpose (finding aggregation and normalized scoring) for Macie's purpose (data classification) — Security Hub does not scan S3 content for PII itself. E incorrectly gives Security Hub a scanning capability it doesn't have — Security Hub aggregates and normalizes findings that other services (like Inspector) generate; it never performs the underlying vulnerability scan itself.

**Trigger words:** "cryptocurrency-mining traffic or credential compromise" (GuardDuty), "vulnerability assessments... known CVEs" (Inspector), "discovers and classifies sensitive data... PII" (Macie, misattributed to Security Hub in C), "aggregating findings from other services" (Security Hub's real role, contradicted by E's added scanning claim).

**Underlying architectural principle:** GuardDuty = behavioral/log-based threat detection, Macie = S3 sensitive-data discovery/classification, Inspector = vulnerability/CVE scanning of compute resources, Security Hub = cross-service finding aggregation and normalized scoring only — each of the four owns exactly one of these responsibilities with no overlap.

---

### Question 49 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A healthcare company stores patient intake forms, scanned insurance documents, and internal HR files across dozens of S3 buckets accumulated over several years of organic growth. A new compliance mandate requires the company to identify which buckets currently contain personally identifiable information (PII) and protected health information (PHI) so those buckets can be prioritized for tighter access controls, without manually opening and inspecting every object by hand.

**Options:**
A. Enable Amazon Macie and run a sensitive data discovery job across the S3 buckets to automatically identify and classify objects containing PII/PHI.
B. Enable Amazon GuardDuty S3 Protection, since it scans object contents in S3 buckets for sensitive data patterns like PII and PHI.
C. Enable Amazon Inspector's S3 scanning feature to classify object content by sensitivity level.
D. Enable AWS Config with a managed rule that flags any S3 object containing a valid-format social security or medical record number.

**Correct answer(s):** A

**Why correct:** Macie is purpose-built for exactly this task — using machine learning and pattern matching to discover and classify sensitive data types (PII, PHI, financial data, credentials) within S3 objects at scale, without manual inspection, and surfacing findings prioritized by sensitivity and bucket.

**Why each wrong option is wrong:** B misapplies GuardDuty S3 Protection, which monitors S3 data-plane API activity (via CloudTrail S3 data events) for anomalous access patterns and threats — it does not read or classify object content for sensitive data types. C is not a real Inspector capability — Inspector performs vulnerability/CVE and network-reachability scanning of compute resources (EC2, ECR, Lambda), not content classification of S3 objects. D describes AWS Config incorrectly — Config evaluates resource *configuration* state against rules (e.g., "is versioning enabled," "is the bucket public") and has no capability to inspect the actual byte content of objects for PII/PHI patterns.

**Trigger words:** "identify which buckets currently contain personally identifiable information (PII) and protected health information (PHI)," "without manually opening and inspecting every object by hand."

**Underlying architectural principle:** Amazon Macie is the dedicated service for automated, content-level sensitive-data discovery and classification within S3 — no other listed security or compliance service inspects object content for PII/PHI patterns.

---

### Question 50 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company's cloud operations team needs to answer two related but distinct questions during a security incident: first, "exactly which IAM principal called the `TerminateInstances` API, from what source IP, and at what timestamp, for this specific EC2 instance that unexpectedly disappeared last Tuesday," and second, "has the security group attached to our production database instance ever been changed to allow an overly permissive inbound rule, and if so, when and by whom, plus can we get notified automatically the next time it happens." The team needs one service to answer the first question and a different service to answer the second.

**Options:**
A. Use AWS CloudTrail (event history / logs) to answer the first question by locating the specific `TerminateInstances` API call record, and use AWS Config (configuration history plus a custom or managed rule with an EventBridge/SNS notification) to answer the second question about historical and future security group changes.
B. Use AWS Config for both questions, since Config records every API call made in the account including who made it and from where.
C. Use AWS CloudTrail for both questions, since CloudTrail retains a full historical timeline of every resource's configuration state changes, including security group rule history.
D. Use Amazon GuardDuty to answer the first question by identifying the malicious termination event, and use AWS CloudTrail to answer the second question by replaying historical security group configuration snapshots.

**Correct answer(s):** A

**Why correct:** CloudTrail is the service that logs discrete API calls (who, what action, source IP, when) — exactly what's needed to pinpoint the specific `TerminateInstances` call; AWS Config tracks resource *configuration state over time* and supports rules with automated notifications, making it the right tool to answer "was this security group ever changed to something risky, and alert us going forward." (Config's configuration items also link to the related CloudTrail event IDs for each change, which is how the "by whom" detail is ultimately traced.)

**Why each wrong option is wrong:** B is incorrect — Config does not log individual API calls with caller identity/source IP; it records configuration item snapshots and changes, not action-level audit events. C is incorrect — CloudTrail logs discrete API events, not a queryable timeline of a resource's evolving configuration state; reconstructing "was this SG ever risky" from raw CloudTrail events is far harder than using Config's built-in configuration timeline and rules. D misapplies GuardDuty, which is a behavioral threat detector, not an API audit log lookup tool for a specific already-known API call, and reverses CloudTrail's actual capability (it doesn't "replay configuration snapshots" — that's Config's job).

**Trigger words:** "exactly which IAM principal called... from what source IP, and at what timestamp" (CloudTrail), "ever been changed to allow... and if so, when and by whom, plus... notified automatically the next time" (Config).

**Underlying architectural principle:** CloudTrail answers "who did what API action, when, from where" (event/audit log); AWS Config answers "what did this resource's configuration look like over time, and alert me on future non-compliant changes" (configuration state and compliance) — the two are complementary, not interchangeable, services.

---

### Question 51 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A mobile banking app needs to let end users (retail customers, potentially millions) sign up and log in with a username and password or via Google/Facebook social login, and after authenticating, those same users need temporary AWS credentials scoped by IAM role to directly upload profile photos to a specific S3 bucket prefix without routing the upload through the app's backend servers.

**Options:**
A. Use a Cognito User Pool to handle end-user sign-up/sign-in (including social identity provider federation), then use a Cognito Identity Pool to exchange the User Pool token for temporary, IAM-role-scoped AWS credentials for direct S3 access.
B. Use a Cognito Identity Pool alone to handle both the username/password sign-up flow and the temporary AWS credential vending, since Identity Pools natively manage user directories.
C. Create an IAM user for each retail customer with permissions scoped to their own S3 prefix, and distribute long-term access keys to the mobile app on first login.
D. Use AWS IAM Identity Center to federate retail customers as workforce users, granting each a permission set scoped to the specific S3 prefix.

**Correct answer(s):** A

**Why correct:** This is the textbook Cognito two-service pattern: a User Pool is the actual user directory/authenticator (handling sign-up, sign-in, and social/SAML/OIDC federation), while an Identity Pool takes an authenticated identity (from a User Pool or a third party) and exchanges it for temporary, IAM-role-scoped AWS credentials usable directly against services like S3 — exactly the two capabilities the scenario needs in sequence.

**Why each wrong option is wrong:** B is factually backwards — Identity Pools do not manage user directories, sign-up, or password authentication at all; that is the User Pool's job, and Identity Pools only vend AWS credentials for already-authenticated identities. C creates an unscalable, insecure operational nightmare — provisioning a distinct IAM user with long-term access keys per retail customer does not scale to millions of users and violates the strong preference against long-lived credentials for end users. D misapplies IAM Identity Center, which is designed for workforce (employee/partner) identity federation into AWS accounts and permission sets, not for consumer-facing, internet-scale end-user authentication in a mobile app.

**Trigger words:** "end users... sign up and log in... username and password or via Google/Facebook," "temporary AWS credentials scoped by IAM role... direct S3 access... without routing... through the app's backend."

**Underlying architectural principle:** Cognito User Pools handle consumer identity and authentication (who is this user); Cognito Identity Pools convert an authenticated identity into temporary, role-scoped AWS credentials (what can this user directly touch in AWS) — the two are typically used together, in that order, for direct-to-AWS-service mobile/web app access patterns.

---

### Question 52 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A B2B SaaS company wants to allow its enterprise customers' employees to log into the SaaS company's application using the enterprise customer's own existing corporate identity provider (which speaks SAML 2.0), without the SaaS company ever creating or storing separate username/password credentials for those employees, and without the employees needing any direct AWS-level access — they only need to be recognized and authenticated within the SaaS application itself.

**Options:**
A. Configure a Cognito User Pool with a SAML 2.0 identity provider federation, so enterprise employees authenticate against their own corporate IdP and Cognito issues the application-level tokens the SaaS app relies on.
B. Configure a Cognito Identity Pool with a SAML 2.0 identity provider federation, since Identity Pools are the correct entry point for federating external SAML users into an application.
C. Create IAM Identity Center permission sets for each enterprise customer's employees, federated via the enterprise's SAML IdP.
D. Require every enterprise customer to export their employee directory and have the SaaS company create matching Cognito User Pool user records with generated passwords.

**Correct answer(s):** A

**Why correct:** Cognito User Pools natively support federation with external SAML 2.0 (and OIDC) identity providers, letting the SaaS application authenticate users against the enterprise's own IdP and receive standard tokens (ID/access tokens) without ever managing a separate password for those users — precisely the described requirement.

**Why each wrong option is wrong:** B is incorrect because Identity Pools are not the authentication/federation entry point for issuing application-level identity — they only vend temporary AWS credentials after a User Pool (or another identity source) has already authenticated the user, and this scenario has no stated need for direct AWS credential access at all. C misapplies IAM Identity Center, which is intended for workforce access to AWS accounts/applications integrated with AWS SSO, not for embedding customer-facing SAML login into a third-party SaaS application's own user experience. D directly contradicts the explicit requirement to avoid creating/storing separate credentials for enterprise employees, and adds unnecessary manual data-import operational overhead.

**Trigger words:** "own existing corporate identity provider... SAML 2.0," "without... ever creating or storing separate username/password credentials," "no direct AWS-level access."

**Underlying architectural principle:** Cognito User Pools support direct SAML/OIDC federation for application-level authentication with no AWS credential vending required — reach for a User Pool alone (no Identity Pool) whenever the requirement stops at "authenticate the user into my app," and add an Identity Pool only when the user additionally needs temporary AWS credentials.

---

### Question 53 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A gaming company's mobile app allows users to play as a guest without creating an account, but guest users still need to save their game progress to a per-user-scoped DynamoDB partition and upload screenshots to a per-user S3 prefix, using temporary AWS credentials with permissions limited to that specific guest's own data. If the guest later creates a real account, their existing guest-generated data and identity must carry over seamlessly to the newly authenticated identity without starting over.

**Options:**
A. Configure a Cognito Identity Pool with unauthenticated (guest) identities enabled, and when the user later signs up through a linked Cognito User Pool, use identity linking so the unauthenticated identity's unique ID (and its associated data) merges into the newly authenticated identity.
B. Issue a static, shared IAM role's long-term access keys embedded in the app binary for all guest users, since guests don't need individually scoped permissions.
C. Require every guest user to complete Cognito User Pool sign-up before any gameplay begins, eliminating the need for unauthenticated identity support entirely.
D. Use AWS IAM Identity Center's guest access feature to issue temporary, per-guest scoped credentials that automatically convert to authenticated access on sign-up.

**Correct answer(s):** A

**Why correct:** Cognito Identity Pools explicitly support unauthenticated (guest) identities, each with its own unique, per-identity ID and scoped temporary IAM credentials, and natively support merging/linking that guest identity to a subsequent authenticated identity so previously-generated data tied to the guest ID isn't orphaned — directly satisfying both stated requirements.

**Why each wrong option is wrong:** B violates least privilege and basic credential-security hygiene by sharing one static, long-term, embedded credential across every guest user with no per-user scoping or rotation, and directly contradicts the requirement for permissions "limited to that specific guest's own data." C removes the guest-play feature the product explicitly requires, forcing sign-up before any use is allowed. D describes a capability that does not exist — IAM Identity Center is a workforce federation service with no "guest access" feature and no involvement in consumer mobile app identity flows at all.

**Trigger words:** "play as a guest without creating an account," "temporary AWS credentials... limited to that specific guest's own data," "carry over seamlessly to the newly authenticated identity."

**Underlying architectural principle:** Cognito Identity Pools' unauthenticated (guest) identity support, combined with identity linking on later sign-up, is the purpose-built pattern for scoped, per-guest AWS access that seamlessly upgrades to a full authenticated identity without data loss.

---

### Question 54 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A startup is deploying its first public HTTPS website behind an Application Load Balancer and separately needs a TLS certificate for an internal API served through API Gateway with a custom domain. The team wants both certificates issued and renewed with zero manual certificate-signing-request handling or renewal reminders, and wants to avoid ever downloading a private key file that could be mishandled.

**Options:**
A. Request public certificates for both domains through AWS Certificate Manager (ACM), validate ownership via DNS or email validation, and attach the certificates directly to the ALB listener and the API Gateway custom domain — ACM manages issuance and renewal with the private key never leaving AWS.
B. Generate a certificate signing request manually, submit it to a third-party public certificate authority, download the issued certificate and private key, and upload both into IAM for use by the ALB and API Gateway.
C. Use AWS Secrets Manager's built-in certificate-issuance feature to generate and rotate TLS certificates for both the ALB and API Gateway automatically.
D. Rely on the default self-signed certificate that ACM automatically generates for any AWS resource, since ACM defaults to self-signed issuance unless a paid public CA is explicitly configured.

**Correct answer(s):** A

**Why correct:** ACM is purpose-built for exactly this: requesting free public certificates, automating domain validation, keeping the private key material entirely within AWS (never downloadable), and handling automatic renewal before expiration — directly satisfying "zero manual CSR/renewal handling" and "never download a private key."

**Why each wrong option is wrong:** B reintroduces every manual step (CSR generation, third-party submission, private key download/handling, manual renewal tracking) the team explicitly wants to avoid, and also risks private key mishandling. C describes a capability Secrets Manager does not have — it stores and rotates secrets/credentials generically, but it is not a certificate authority and does not issue TLS certificates. D is factually false — ACM does not default to self-signed certificates; it issues certificates from Amazon's trusted public CA (or supports importing third-party certs), and there is no "self-signed by default" behavior.

**Trigger words:** "issued and renewed with zero manual certificate-signing-request handling or renewal reminders," "avoid ever downloading a private key file."

**Underlying architectural principle:** ACM is the default choice for public TLS certificates on AWS-integrated resources (ALB, CloudFront, API Gateway) whenever automated issuance, validation, and renewal with no private-key extraction is required — manual CA processes or third-party certificates should only be used when ACM integration isn't available for the target service.

---

### Question 55 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company needs a public TLS certificate for a legacy on-premises web server that is not fronted by any AWS load balancer, CloudFront distribution, or API Gateway — it's a standalone server in a colocation facility that the company still wants centrally tracked for expiration alongside its AWS-hosted certificates. Separately, the company also needs a private certificate to secure internal service-to-service mTLS traffic between microservices running on EC2 within a VPC, issued from a private CA the company controls rather than a public one.

**Options:**
A. Import the on-premises server's public certificate (obtained from a third-party public CA — not ACM, since ACM-issued public certificates can never be exported for installation outside AWS-integrated services — and installed on the server through its own web server TLS configuration) into ACM using ACM's certificate-import feature purely for centralized expiration tracking and CloudWatch alarms alongside AWS-hosted certificates — noting that ACM does not auto-renew imported certificates — and separately use AWS Certificate Manager Private Certificate Authority (ACM Private CA) to issue the internal mTLS certificates, exporting the certificate and private key for direct installation on the EC2 microservices, from a company-controlled private CA hierarchy.
B. Attach the on-premises server directly to an ALB target group so ACM can automatically manage its certificate, and use a second ACM public certificate for the internal mTLS traffic since ACM only issues one type of certificate.
C. Use AWS Certificate Manager for both needs, since ACM certificates can always be exported as plaintext private keys regardless of validation type or CA source.
D. Use AWS Secrets Manager to generate a self-signed root CA and distribute it manually to both the on-premises server and the internal microservices.

**Correct answer(s):** A

**Why correct:** Public ACM certificates can never be exported — their private keys never leave AWS by design — so a certificate destined for a standalone on-premises server must be obtained/installed outside that constraint; ACM's import feature lets you bring in a certificate you already hold (public or otherwise) purely for centralized expiration visibility and CloudWatch alarms, even though ACM won't renew it for you since it didn't issue it. Separately, ACM Private CA is the purpose-built service for issuing private certificates from a company-controlled CA hierarchy, and — unlike public ACM certificates — its private certificates and their private keys can be exported for direct installation on resources like the EC2 microservices needing mTLS, exactly matching the internal requirement.

**Why each wrong option is wrong:** B is not feasible — an ALB target group cannot make an on-premises, non-AWS server "ACM-managed," and even if the server were reachable as an IP target, an ALB certificate only secures the ALB listener, not the origin server's own TLS stack; the claim that "ACM only issues one type of certificate" also ignores the distinct public-ACM vs. ACM Private CA certificate types. C is false as a blanket statement — standard public ACM certificates are never exportable, full stop, regardless of validation type; only certificates issued by ACM Private CA (private certificates) support export, so treating all ACM certificates as freely exportable plaintext keys is incorrect. D bypasses AWS's managed PKI services entirely in favor of a fully manual, unmanaged self-signed CA process, which does not provide the centralized management, revocation, and lifecycle tracking that ACM Private CA offers, and Secrets Manager has no CA-issuance capability at all.

**Trigger words:** "standalone server in a colocation facility... not fronted by any AWS load balancer," "centrally tracked for expiration," "private certificate... from a private CA the company controls."

**Underlying architectural principle:** Public ACM certificates never leave AWS and can never be exported, but ACM's import feature still lets you centrally track expiration for certificates it didn't issue, extending visibility to non-integrated/on-premises resources without auto-renewal. ACM Private CA is the distinct service for organization-controlled private certificate hierarchies such as internal mTLS, and — unlike public ACM certificates — its private certificates can be exported for installation anywhere, including on-premises or self-managed compute. The two solve different halves of "public vs. private trust" and are not interchangeable.

---

### Question 56 [Priority: P2] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A compliance team must implement continuous, automatic governance over AWS resource configuration in a regulated environment. Specifically, they need to: (1) automatically detect within minutes whenever any security group in the account is modified to allow unrestricted inbound SSH (0.0.0.0/0 on port 22), and trigger an automatic remediation that removes the offending rule; and (2) maintain a complete, tamper-evident record of every management API call made in the account, delivered to a centralized, access-restricted S3 bucket in a separate account for long-term audit retention. Select the two actions that together satisfy both requirements.

**Options:**
A. Enable AWS Config with the managed rule `restricted-ssh` (or an equivalent custom rule) and attach an automatic remediation action (via an SSM Automation document) that removes the non-compliant inbound rule when the rule evaluates as non-compliant.
B. Enable AWS CloudTrail with an organization trail (or a trail with log file validation) delivering logs to a centralized S3 bucket in a dedicated logging account, with bucket policies restricting access to authorized audit roles only.
C. Enable Amazon GuardDuty with the "Automated Remediation" feature to detect and automatically close overly permissive security group rules across the organization.
D. Enable AWS Config alone, since Config natively delivers all management API call history to S3 with the same tamper-evident guarantees as CloudTrail.
E. Enable AWS CloudTrail Insights exclusively, since Insights automatically remediates any detected anomalous security group change without additional configuration.

**Correct answer(s):** A, B

**Why correct:** A directly satisfies requirement 1 — Config continuously evaluates resource configuration against a rule and can trigger automatic remediation via SSM Automation the moment a security group drifts into a non-compliant (open-SSH) state. B directly satisfies requirement 2 — CloudTrail (as an organization/multi-account trail with log file validation) is the API-call audit log service, and centralizing delivery to a separate, access-restricted logging-account bucket is the standard tamper-evident, cross-account audit pattern.

**Why each wrong option is wrong:** C describes a capability GuardDuty does not have — GuardDuty detects and reports findings but has no native "automated remediation" action that modifies security group rules on its own; remediation requires separate automation (e.g., via EventBridge + Lambda/SSM), and it is not the standard tool for configuration-compliance rule evaluation in the first place. D is false — Config records configuration item changes and compliance evaluations, not a full log of every management API call; that is CloudTrail's specific role, and Config does not provide CloudTrail's tamper-evident API audit trail. E is false — CloudTrail Insights only surfaces unusual API activity patterns as findings for human/automated review; it does not itself remediate or reverse any resource change.

**Trigger words:** "automatically detect... and trigger an automatic remediation" (Config), "complete, tamper-evident record of every management API call... centralized... in a separate account" (CloudTrail).

**Underlying architectural principle:** AWS Config drives configuration-compliance detection and automated remediation of drifted resource settings, while CloudTrail provides the immutable, centralized audit trail of API activity — a mature governance posture in a regulated environment requires both services configured for their distinct, non-overlapping purposes.

---

### Question 57 [Priority: P1] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A multinational retailer runs a public e-commerce platform behind CloudFront and an ALB and has been targeted by a coordinated attack combining a volumetric UDP reflection flood against its infrastructure and a simultaneous credential-stuffing campaign against its login API that is also triggering suspicious cross-region API calls in CloudTrail consistent with a compromised IAM access key. The security team has an unlimited emergency budget for this specific incident and needs to select the two actions that most directly and immediately address detecting/mitigating the credential compromise signal and gaining guaranteed expert incident-response support for the ongoing DDoS event, respectively.

**Options:**
A. Engage AWS Shield Advanced's DDoS Response Team (DRT) for hands-on mitigation support and guidance during the active volumetric attack (the account already carries Shield Advanced plus the Business/Enterprise Support plan needed for direct DRT contact, consistent with the described unlimited emergency budget).
B. Review and act on Amazon GuardDuty findings (e.g., anomalous API calls from unusual geolocations, credential compromise indicators tied to the IAM access key) to identify and rotate/disable the compromised credential.
C. Enable AWS WAF's SQL injection managed rule group on the ALB, since SQL injection is the root cause of both the DDoS flood and the credential stuffing.
D. Disable AWS CloudTrail temporarily to stop logging the suspicious API calls until the investigation concludes, reducing log noise for the response team.
E. Rely solely on Shield Standard's automatic mitigations to resolve both the DDoS flood and the credential-stuffing campaign without further action, since Shield Standard covers all attack vectors described.

**Correct answer(s):** A, B

**Why correct:** A directly provides the guaranteed, expert, hands-on DDoS incident response the scenario asks for — this is precisely Shield Advanced's DRT engagement benefit during an active volumetric event. B directly addresses the credential-compromise signal — GuardDuty is the service that surfaces exactly this kind of anomalous-API-call/compromised-credential finding from CloudTrail analysis, enabling the team to identify and act on (rotate/disable) the specific compromised key.

**Why each wrong option is wrong:** C misattributes root cause — SQL injection is unrelated to either a volumetric UDP flood or a credential-stuffing campaign (which is a brute-force login-attempt pattern, not an injection technique), so a SQLi rule group would not mitigate either described attack. D is actively harmful and against security best practice — disabling CloudTrail during an active incident destroys the audit trail needed for investigation and is never an appropriate incident-response action. E is incorrect because Shield Standard only mitigates common, automatic infrastructure-layer (L3/L4) DDoS patterns and provides no application-layer credential-stuffing protection or guaranteed expert engagement — both gaps this multi-vector incident explicitly has.

**Trigger words:** "detecting/mitigating the credential compromise signal" (GuardDuty), "guaranteed expert incident-response support for the ongoing DDoS event" (Shield Advanced DRT), "unlimited emergency budget."

**Underlying architectural principle:** Multi-vector incidents typically require pairing distinct, purpose-specific services — GuardDuty for anomalous-behavior/credential-compromise detection and Shield Advanced's DRT for guaranteed expert DDoS mitigation support — rather than expecting any single free/default service (Shield Standard) or a mismatched control (WAF SQLi rules, disabling audit logging) to cover an attack outside its actual scope.

---

### Question 58 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company operates a VPC with a public subnet hosting a NAT gateway and a private subnet hosting application servers with no public IP addresses. During a security review, an auditor asks the team to explain precisely why an external attacker on the internet cannot directly initiate a connection to the private application servers, even though the private subnet's NACL currently has an inbound allow rule for 0.0.0.0/0 on all ports (an oversight the team plans to fix), and the servers' security groups also currently allow inbound traffic from 0.0.0.0/0 on port 443 (also flagged as needing tightening).

**Options:**
A. Because the application servers have no public IP address and no route from the internet gateway directly to the private subnet, there is no network path for an external attacker's traffic to reach the private subnet at all — the NACL and security group rules are moot for inbound-from-internet traffic given the subnet's routing and addressing, though they should still be tightened as defense-in-depth.
B. Because NACLs always override security groups when both exist, and the NACL rule is misconfigured, the security group's port 443 rule is what's actually preventing the attack.
C. Because the NAT gateway itself blocks all unsolicited inbound connections originating from the internet by inspecting and filtering packet contents for malicious signatures.
D. Because Amazon GuardDuty automatically drops any inbound packet from the internet destined for a private subnet before it reaches the NACL or security group evaluation.

**Correct answer(s):** A

**Why correct:** With no public IP on the instances and no route table entry sending internet-gateway-bound return paths into the private subnet (the private subnet's route table only has a route to the NAT gateway for outbound), there is fundamentally no reachable network path for externally-initiated inbound connections regardless of NACL/SG misconfiguration — routing/addressing is the actual root-cause control here, even though the flagged rules are still real risks worth fixing (e.g., if the instance were later given a public IP, or reachable via some other path).

**Why each wrong option is wrong:** B describes a nonexistent interaction — NACLs and security groups don't "override" each other; both must independently permit traffic, and neither one is what's preventing this specific inbound-from-internet scenario, since the real blocker is the lack of a routable path in the first place. C mischaracterizes the NAT gateway — a NAT gateway translates and forwards traffic that instances in its subnet initiate outbound; it is not a packet-inspection firewall and does not evaluate inbound internet traffic content for malicious signatures, and more fundamentally NAT gateways don't route unsolicited inbound internet traffic to private instances at all by design (no inbound NAT/port-forwarding path exists for a standard NAT gateway). D describes a capability GuardDuty does not have — GuardDuty is a detection service that analyzes logs and generates findings; it has no inline packet-filtering or blocking function anywhere in the data path.

**Trigger words:** "no public IP addresses," "even though the private subnet's NACL currently has an inbound allow rule for 0.0.0.0/0," "precisely why an external attacker... cannot directly initiate a connection."

**Underlying architectural principle:** Network reachability (addressing and routing) is a foundational, independent layer of defense beneath NACLs and security groups — a resource with no public IP and no inbound route from an internet gateway is unreachable from the internet regardless of how permissive its NACL or security group rules are, though those rules should never be relied upon as the only control.

---

### Question 59 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A small internal tool team wants to detect, without deploying any new agents, sensors, or third-party software, whether any of their EC2 instances are communicating with known command-and-control (C2) IP addresses or exhibiting DNS query patterns consistent with malware, using only existing AWS-native log sources they already have available (VPC Flow Logs, DNS logs, CloudTrail) and AWS threat intelligence feeds.

**Options:**
A. Enable Amazon GuardDuty for the account, which analyzes VPC Flow Logs, DNS query logs, and CloudTrail events against AWS and third-party threat intelligence feeds to surface findings like C2 communication and malware-consistent DNS activity — with no agents to deploy.
B. Enable AWS Config with the `ec2-instance-managed-by-systems-manager` managed rule, which flags any instance communicating with known malicious IP addresses.
C. Install the Amazon Inspector agent on every EC2 instance to monitor real-time network connections for command-and-control traffic.
D. Enable Amazon Macie on the VPC, since Macie analyzes network flow logs for malware command-and-control signatures in addition to its S3 data classification role.

**Correct answer(s):** A

**Why correct:** GuardDuty is exactly this: an agentless threat-detection service that continuously analyzes existing log sources (VPC Flow Logs, DNS logs, CloudTrail) against curated threat intelligence to detect things like C2 communication and malicious DNS activity, requiring no new infrastructure or agents to deploy.

**Why each wrong option is wrong:** B misapplies Config, whose managed rules evaluate resource configuration compliance (e.g., "is SSM Agent installed"), not live network threat-intelligence matching against malicious IPs. C contradicts the explicit "without deploying any new agents" requirement, and mischaracterizes Inspector, whose role is vulnerability/CVE assessment, not real-time C2 network monitoring. D incorrectly expands Macie's scope — Macie is scoped specifically to S3 sensitive-data discovery and has no VPC network flow or DNS analysis capability at all.

**Trigger words:** "without deploying any new agents, sensors, or third-party software," "command-and-control (C2) IP addresses," "existing AWS-native log sources... and AWS threat intelligence feeds."

**Underlying architectural principle:** GuardDuty's core value proposition is agentless, continuous threat detection built entirely on log sources AWS accounts already generate, cross-referenced against managed threat intelligence — no separate sensor deployment is ever required.

---

### Question 60 [Priority: P3] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A financial services company operating under strict regulatory audit requirements is designing its Domain 1 security posture end-to-end and must correctly identify, from a mixed list of claims about VPC security and AWS security services, the two statements that are factually accurate based on documented 2026 AWS behavior, in order to avoid embedding incorrect assumptions into its architecture runbook.

**Options:**
A. A subnet can be associated with only one NACL at a time, but a single NACL can be associated with multiple subnets simultaneously.
B. Security group rules are evaluated in a specific numbered priority order, similar to NACL rule numbers, where a lower-numbered rule takes precedence over a higher-numbered one.
C. AWS Config can be configured with an aggregator to evaluate compliance across multiple accounts and regions from a single delegated administrator or aggregator account.
D. Amazon Inspector's EC2 vulnerability scanning works by passively mirroring VPC traffic to an appliance, with no dependency on any agent running on the instance itself.
E. Amazon GuardDuty must be individually enabled and configured separately in every AWS account within an AWS Organization, since it has no native multi-account delegated administrator model.

**Correct answer(s):** A, C

**Why correct:** A is accurate — each subnet has exactly one associated NACL at any time (a default NACL if none is explicitly assigned), while one NACL can be reused across many subnets. C is accurate — AWS Config supports aggregators that consolidate compliance and configuration data across multiple accounts and regions into a single view for a designated aggregator account, a standard multi-account governance pattern.

**Why each wrong option is wrong:** B is false — security groups have no rule-numbering or priority-order concept at all; all rules are evaluated together as an allow-list with no ordering semantics (numbered rule-priority evaluation is specific to NACLs, not security groups). D is false — Inspector's EC2 vulnerability scanning is CVE/package-based, not network-traffic-based: it assesses installed software either through the SSM Agent already running on a managed instance, or, for accounts using Inspector's newer agentless assessment option, by analyzing EBS volume snapshots and instance metadata out-of-band. Neither mechanism involves mirroring live VPC network traffic to an inspection appliance, so the specific mechanism this option describes doesn't match how Inspector works even under its agentless mode. E is false — GuardDuty explicitly supports a multi-account delegated administrator model via AWS Organizations, allowing centralized enablement and finding aggregation across all member accounts from one designated account, contradicting the claim that each account must be configured separately.

**Trigger words:** "only one NACL at a time... multiple subnets simultaneously" (A), "aggregator... single delegated administrator" (C), "no dependency on any agent" (D, contradicted), "individually enabled... in every AWS account" (E, contradicted).

**Underlying architectural principle:** Precise, testable distinctions — NACLs use numbered rule evaluation and a strict one-NACL-per-subnet model while security groups have no rule ordering, and both Config and GuardDuty (like most modern AWS security services) support Organizations-wide delegated administrator/aggregator patterns for centralized multi-account governance — are exactly the kind of "know the exact mechanism, not just the vocabulary" traps the exam favors.

---

## Domain 2: Design Resilient Architectures (26%)

### Question 61 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A three-tier web application runs its application servers in a single Auto Scaling group spread across two Availability Zones, fronted by an Application Load Balancer that is also configured across both AZs. The database, however, is a single RDS MySQL instance running in only one of the two AZs, with no standby configured. During a recent AZ-level network disruption, the application tier stayed up, but every request failed once it tried to reach the database. Leadership wants the database tier to survive the loss of a single AZ without manual intervention, with minimal application changes.
**Options:**
A. Enable RDS Multi-AZ deployment so a synchronously replicated standby in a second AZ can be automatically promoted on failure.
B. Take manual daily snapshots of the RDS instance and store them in S3 for recovery if the AZ fails.
C. Add a read replica of the RDS instance in the second AZ and update the application to write to whichever replica is currently reachable.
D. Move the RDS instance into the same AZ as the majority of the application servers to reduce cross-AZ latency.
**Correct answer(s):** A
**Why correct:** RDS Multi-AZ maintains a synchronously replicated standby in a different AZ and automatically fails over the DNS endpoint to it during an AZ-level disruption, with no application code changes required — directly matching "survive the loss of a single AZ without manual intervention, with minimal application changes."
**Why each wrong option is wrong:** B provides a recovery point measured in up to a day of data loss and requires a manual restore process, which is neither automatic nor minimal-effort; C is wrong because RDS read replicas are read-only by default and application-level failover logic to pick "whichever replica is reachable" is exactly the manual, custom engineering effort the requirement wants avoided, and standard read replicas replicate asynchronously; D actively removes AZ redundancy entirely and does the opposite of what's being asked.
**Trigger words:** "single RDS MySQL instance running in only one of the two AZs," "survive the loss of a single AZ without manual intervention," "minimal application changes."
**Underlying architectural principle:** A single-AZ resource anywhere in an otherwise multi-AZ stack is a single point of failure; RDS Multi-AZ is the native, code-free way to remove that SPOF at the database layer.

---

### Question 62 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retail company's checkout service runs behind an Application Load Balancer with an Auto Scaling group spanning three Availability Zones. A post-incident review reveals that the NAT Gateway used for outbound internet access (to reach a third-party payment API) exists as a single NAT Gateway in only one AZ, shared by route tables in all three private subnets. When that AZ experienced an outage last month, instances in the other two healthy AZs also lost the ability to reach the payment API, even though those instances themselves were fine. The team needs to eliminate this single point of failure at the lowest additional monthly cost that still preserves full-region NAT resilience.
**Options:**
A. Deploy one NAT Gateway per AZ, and update each AZ's private subnet route table to use the NAT Gateway in its own AZ.
B. Replace the NAT Gateway with a single NAT instance sized to handle triple the current traffic.
C. Keep the single NAT Gateway but add a second Elastic IP address to it for redundancy.
D. Route outbound traffic from all three AZs through a Gateway Load Balancer endpoint instead of a NAT Gateway.
**Correct answer(s):** A
**Why correct:** A NAT Gateway is an AZ-scoped resource, so the only way to remove the cross-AZ dependency it creates is to deploy one per AZ and keep each AZ's outbound traffic local to its own NAT Gateway — this is the standard, minimum-cost pattern that fully eliminates the single point of failure while preserving resilience for all three AZs.
**Why each wrong option is wrong:** B replaces a managed, highly available service with a single self-managed NAT instance, which is itself a single point of failure (and a single instance) and adds operational burden, not less; C is wrong because attaching a second Elastic IP to the same NAT Gateway does nothing to protect against the AZ hosting that NAT Gateway going down — the resource itself is still confined to one AZ; D is wrong because Gateway Load Balancer is designed for inserting third-party virtual appliances (firewalls, IDS/IPS) into the traffic path, not for providing outbound internet NAT functionality.
**Trigger words:** "single NAT Gateway used... in only one AZ," "instances in the other two healthy AZs also lost the ability to reach," "eliminate this single point of failure at the lowest additional monthly cost."
**Underlying architectural principle:** NAT Gateways are AZ-scoped, so true multi-AZ resilience requires one NAT Gateway per AZ with per-AZ route tables, not a single shared NAT Gateway.

---

### Question 63 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs a fleet of internal microservices communicating purely over raw TCP on a non-HTTP custom binary protocol at extremely high throughput (millions of requests per second), and needs the client's source IP address preserved end-to-end for internal audit logging. The services do not need any HTTP-layer routing rules, host/path-based routing, or WebSocket support.
**Options:**
A. Network Load Balancer, using its ability to preserve client source IP and handle ultra-high-throughput Layer 4 TCP traffic with minimal latency.
B. Application Load Balancer, because it is AWS's most feature-rich and generally recommended load balancer for all new workloads.
C. Gateway Load Balancer, because it scales to the highest throughput of any AWS load balancer type.
D. Classic Load Balancer, because it operates at both Layer 4 and Layer 7 simultaneously.
**Correct answer(s):** A
**Why correct:** NLB operates at Layer 4, is purpose-built for extremely high throughput with ultra-low latency, natively preserves the client's source IP address, and requires no HTTP-layer features — matching every requirement in the scenario exactly.
**Why each wrong option is wrong:** B is wrong because ALB operates at Layer 7 and is designed for HTTP/HTTPS traffic with content-based routing, which this raw TCP, non-HTTP workload doesn't use or need, and ALB's request-based model isn't optimized for this use case; C is wrong because Gateway Load Balancer's purpose is transparently inserting third-party network appliances into a traffic path (using GENEVE encapsulation), not serving as a general-purpose internal load balancer for application traffic; D is wrong because Classic Load Balancer is a legacy load balancer type that AWS explicitly recommends against for new workloads in favor of ALB/NLB, and — unlike NLB, which preserves the client source IP by default — a Classic Load Balancer's TCP listener only preserves the original source IP if Proxy Protocol is manually enabled, so it does not match the "preserved end-to-end" requirement out of the box.
**Trigger words:** "raw TCP," "custom binary protocol," "millions of requests per second," "client's source IP address preserved," "no... HTTP-layer routing rules."
**Underlying architectural principle:** Choose NLB when a workload is Layer 4, throughput/latency-critical, and requires client IP preservation; reserve ALB for Layer 7 HTTP(S)-aware routing needs.

---

### Question 64 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company runs a single-page application with a REST API backend. Traffic must be routed to different backend target groups depending on the URL path (`/api/orders/*` goes to the orders service, `/api/users/*` goes to the users service), and the security team additionally requires TLS termination with automatic integration to AWS Certificate Manager, plus native WebSocket support for a live order-status feature.
**Options:**
A. Application Load Balancer, using path-based routing rules across target groups with an ACM certificate attached to the HTTPS listener.
B. Network Load Balancer, using TCP listener rules to distribute traffic based on URL path.
C. Gateway Load Balancer, using GENEVE-based rules to inspect and route HTTP paths to different target groups.
D. Route 53 weighted routing pointed directly at each backend service's IP addresses, bypassing the need for a load balancer entirely.
**Correct answer(s):** A
**Why correct:** ALB is the only option here operating at Layer 7 with native path-based routing across multiple target groups, native ACM integration for TLS termination, and native WebSocket support — matching every stated requirement.
**Why each wrong option is wrong:** B is wrong because NLB operates at Layer 4 and has no visibility into HTTP URL paths, so it cannot make routing decisions based on `/api/orders/*` versus `/api/users/*`; C is wrong because Gateway Load Balancer is designed to transparently forward traffic to third-party virtual appliances for inspection, not to make application-aware HTTP path-routing decisions to target groups; D is wrong because Route 53 performs DNS resolution, not per-request Layer 7 routing, TLS termination, or health-check-driven load balancing — it cannot inspect a URL path within an established connection to route to different backends.
**Trigger words:** "route to different backend target groups depending on the URL path," "TLS termination with... ACM," "native WebSocket support."
**Underlying architectural principle:** Path-based and host-based routing, TLS termination with ACM, and WebSocket support are defining Layer 7 capabilities unique to ALB among AWS load balancer types.

---

### Question 65 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A cybersecurity vendor sells a virtual firewall appliance that customers deploy inside their own VPCs. The vendor wants all inbound and outbound traffic for a customer's application subnet to be transparently intercepted, inspected, and either allowed or blocked by a fleet of these third-party firewall appliances, which must be able to scale horizontally and be added or removed without customers having to reconfigure their route tables each time. The solution must preserve the original packet as closely as possible for deep packet inspection.
**Options:**
A. Gateway Load Balancer, distributing traffic to a scalable fleet of appliance instances using GENEVE encapsulation and a single Gateway Load Balancer endpoint referenced from route tables.
B. Application Load Balancer, using host-based routing rules to direct traffic to whichever firewall appliance is healthy.
C. Network Load Balancer, since it operates at Layer 4 and is therefore capable of transparent traffic inspection.
D. Route 53 failover routing pointed at the healthy firewall appliance's Elastic IP address.
**Correct answer(s):** A
**Why correct:** Gateway Load Balancer is purpose-built for exactly this pattern — transparently inserting a horizontally scalable fleet of third-party virtual appliances (firewalls, IDS/IPS) into a traffic path using GENEVE encapsulation, with a single, stable Gateway Load Balancer endpoint that route tables reference, so the appliance fleet can scale or change without customer route table edits.
**Why each wrong option is wrong:** B is wrong because ALB terminates and re-generates HTTP requests at Layer 7, which does not preserve the original packet for deep inspection and isn't designed for appliance-fleet insertion; C is wrong because plain NLB, while Layer 4, does not provide the transparent bump-in-the-wire appliance-insertion model or GENEVE encapsulation that Gateway Load Balancer specifically provides — it load-balances application traffic to targets, not traffic through inspection appliances; D is wrong because Route 53 is DNS-based and does not intercept or inspect in-flight traffic at the packet level at all.
**Trigger words:** "third-party firewall appliances," "transparently intercepted, inspected," "scale horizontally... without... reconfigur[ing] route tables," "preserve the original packet."
**Underlying architectural principle:** Gateway Load Balancer is the specific AWS service for transparently distributing traffic across a scalable fleet of third-party network virtual appliances via GENEVE, distinct from ALB/NLB's target-load-balancing role.

---

### Question 66 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company's corporate website is hosted entirely as a static site on S3 with CloudFront in front of it, serving marketing content to a global audience with no dynamic backend, no per-request routing logic, and no health-check-driven target selection needed. The team wants the absolute simplest DNS setup that maps their apex domain to the CloudFront distribution.
**Options:**
A. Simple routing policy with a Route 53 alias record pointing to the CloudFront distribution.
B. Weighted routing policy split 100/0 across two identical CloudFront distributions.
C. Latency-based routing policy across CloudFront distributions deployed in multiple regions.
D. Multivalue answer routing policy returning multiple CloudFront IP addresses with health checks.
**Correct answer(s):** A
**Why correct:** A Simple routing policy with an alias record is the most straightforward way to map a domain to a single AWS resource like a CloudFront distribution, and it's explicitly the right fit when there's no need for weighting, latency-based selection, or health-check-driven answers — CloudFront itself is already a globally distributed edge network, so no DNS-level traffic-steering logic is needed.
**Why each wrong option is wrong:** B introduces unnecessary complexity and a second distribution to manage for no functional benefit when 100/0 weighting is functionally identical to just using one record; C is unnecessary and doesn't apply meaningfully here since CloudFront distributions are already globally edge-optimized — this pattern is meant for steering between distinct regional origins/endpoints, not needed for a single global CDN distribution; D adds health-checked multiple answers when there is only one distribution and no described need for DNS-level failover or client-side load spreading across multiple endpoints, and CloudFront distributions aren't referenced by static IP addresses in the way multivalue answer is designed for.
**Trigger words:** "static site," "no dynamic backend," "no per-request routing logic," "no health-check-driven target selection needed," "absolute simplest DNS setup."
**Underlying architectural principle:** Simple routing is the correct (and often overlooked) answer whenever a scenario explicitly has only one target and no requirement for weighting, latency awareness, or health-check-based failover.

---

### Question 67 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A SaaS company runs identical production stacks in us-east-1 and eu-west-1, each behind its own regional Application Load Balancer. Customers should always be routed to whichever region gives them the lowest network round-trip time, since the application is latency-sensitive (real-time collaborative editing), and both regions are fully capable of serving 100% of global traffic if the other region fails.
**Options:**
A. Latency-based routing policy across both regional ALB endpoints, combined with Route 53 health checks so an unhealthy region is automatically removed from consideration.
B. Weighted routing policy with a 50/50 split between the two regional ALB endpoints.
C. Geolocation routing policy mapping each country to its geographically nearest region.
D. Simple routing policy with a single alias record pointing to the ALB in us-east-1, since it was the original primary region.
**Correct answer(s):** A
**Why correct:** Latency-based routing is specifically designed to direct users to whichever endpoint gives them the best measured network latency, which directly matches "lowest network round-trip time," and pairing it with health checks means Route 53 stops directing traffic to a region that fails, providing both the performance goal and the resilience goal in one configuration.
**Why each wrong option is wrong:** B is wrong because a fixed 50/50 weighted split ignores actual measured latency and would send some users to the farther, slower region regardless of their real round-trip time; C is wrong because geolocation routing is based on the geographic location of the user (or a static country/continent mapping) rather than measured network latency, so a user could be geographically closer to a region that isn't actually the fastest path due to network conditions, which doesn't satisfy "lowest network round-trip time" as precisely as latency-based routing; D is wrong because it sends 100% of global traffic to a single region regardless of where users are, directly contradicting the stated latency requirement and removing the benefit of running two regions at all.
**Trigger words:** "lowest network round-trip time," "latency-sensitive," "both regions are fully capable of serving 100% of global traffic if the other region fails."
**Underlying architectural principle:** Latency-based routing optimizes for measured network performance to each endpoint, which is a different (and often better-fitting) goal than geolocation routing's static geographic-to-region mapping.

---

### Question 68 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A streaming media company operates regional edge clusters in North America, Europe, and Asia-Pacific to serve video content with minimal latency. Legal counsel has mandated that, regardless of network latency, all users physically located in the European Union must always be served exclusively from the Europe cluster, for GDPR data-residency compliance — this requirement takes priority over performance considerations. The company also wants any other users worldwide to be routed based on the lowest measured latency across the remaining clusters.
**Options:**
A. A Route 53 Traffic Flow policy that pins EU-located users to the Europe cluster via a geolocation rule, with a nested latency-based rule as the default branch for all other locations.
B. A pure latency-based routing policy across all three clusters, since it will naturally send most EU users to the Europe cluster anyway.
C. A weighted routing policy giving the Europe cluster a very high weight so most traffic lands there.
D. A geoproximity routing policy with a large negative bias applied to the North America and Asia-Pacific clusters.
**Correct answer(s):** A
**Why correct:** Geolocation routing is the only policy that can create a hard, compliance-grade guarantee based on a user's actual location (mapping the EU specifically to the Europe cluster) regardless of measured latency. A plain geolocation record's default branch normally points to a single static resource, not a dynamically-chosen lowest-latency cluster, so "latency-based for everyone else" needs a nested policy: Route 53 Traffic Flow's visual policy editor is the standard way to build this (a geolocation rule with a nested latency-based rule as its default branch) as a single policy record, though the same effect can also be produced with plain record sets by aliasing the default geolocation record to a separate name that holds the latency-based records. Either way, the compliance mandate and the performance goal are both satisfied.
**Why each wrong option is wrong:** B is wrong because pure latency-based routing has no compliance guarantee — an EU user with an unusually fast path to a non-EU cluster (e.g., due to transient network conditions or ISP peering) could legitimately be routed outside the EU, violating the mandate that this "takes priority over performance"; C is wrong because weighting is probabilistic and traffic-percentage-based, not deterministic by user location, so it cannot guarantee that every single EU user lands on the Europe cluster; D is wrong because geoproximity's bias shifts the geographic boundary of a resource's catchment area but does not offer a hard, location-based compliance guarantee tied to legal jurisdiction (e.g., "the EU") the way geolocation's country/continent mapping does.
**Trigger words:** "regardless of network latency," "must always be served exclusively from the Europe cluster," "GDPR data-residency compliance," "this requirement takes priority over performance."
**Underlying architectural principle:** When a scenario requires a hard, deterministic location-to-endpoint guarantee for compliance reasons, geolocation routing is correct even over latency-based or geoproximity routing, which optimize for performance or shift traffic probabilistically rather than guaranteeing jurisdictional placement.

---

### Question 69 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A gaming company runs matchmaking servers in three regions. The North America region has recently been over capacity relative to its physical infrastructure, so the team wants to shift a portion of the traffic that would normally go to the North America region toward the neighboring South America region instead, without physically moving any servers or changing where users are located, and without setting up entirely separate location-to-region mapping rules. They want fine-grained, incremental control over how much the North America catchment area shrinks.
**Options:**
A. Geoproximity routing policy using Route 53 Traffic Flow, applying a negative bias value to the North America resource to shrink its effective geographic catchment area in favor of South America.
B. Geolocation routing policy, remapping specific South American countries from the North America record to the South America record.
C. Weighted routing policy splitting traffic 70/30 between the North America and South America endpoints for all users worldwide.
D. Latency-based routing policy, since it will automatically detect the North America region is overloaded and shift traffic accordingly.
**Correct answer(s):** A
**Why correct:** Geoproximity routing with a bias value is specifically designed to expand or shrink a resource's effective geographic catchment area without moving infrastructure or manually remapping specific locations, giving fine-grained, incremental control — exactly the mechanism the team wants for shifting load between geographically adjacent regions.
**Why each wrong option is wrong:** B would work but requires manually identifying and remapping specific countries one by one, which is coarser and more operationally heavy than a single bias adjustment, and doesn't offer the same fine-grained incremental control the team wants; C is wrong because a flat weighted split applies the same 70/30 ratio to all users everywhere, including users far from either region, rather than specifically shrinking North America's geographic catchment near the South America boundary; D is wrong because latency-based routing has no awareness of a region's capacity or infrastructure load — it only measures network round-trip time, and it has no bias-style lever to intentionally shift traffic between regions for capacity reasons.
**Trigger words:** "shift a portion of the traffic... without physically moving any servers," "without... entirely separate location-to-region mapping rules," "fine-grained, incremental control over how much the... catchment area shrinks."
**Underlying architectural principle:** Geoproximity routing's bias value is the purpose-built mechanism for incrementally shifting traffic volume between geographically-based endpoints without manual location remapping or infrastructure changes.

---

### Question 70 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company runs its primary order-processing stack in us-east-1 and maintains a fully functional, continuously running (though downsized) standby stack in us-west-2. Under normal operation, 100% of customer traffic must go to us-east-1. If, and only if, us-east-1 becomes unavailable, all traffic must automatically shift to us-west-2 within a few minutes, with no manual DNS changes.
**Options:**
A. Failover routing policy with Route 53 health checks on the primary (us-east-1) endpoint, and a secondary record pointing to us-west-2.
B. Weighted routing policy with a 100/0 split, manually flipped to 0/100 by an on-call engineer during an incident.
C. Latency-based routing policy across both regions, relying on us-east-1 naturally having lower latency for most customers.
D. Multivalue answer routing policy returning both regions' IP addresses so clients can retry the other one on failure.
**Correct answer(s):** A
**Why correct:** Failover routing is purpose-built for exactly this active/passive pattern — it sends all traffic to a designated primary record as long as its associated health check passes, and automatically shifts all traffic to the secondary record the moment the primary fails a health check, with no manual DNS intervention required.
**Why each wrong option is wrong:** B explicitly requires a human ("on-call engineer") to manually flip the split during an incident, which directly violates "no manual DNS changes"; C is wrong because latency-based routing has no concept of a strict "100% to primary unless it's down" rule — it would continuously send some traffic to us-west-2 for any customers who happen to have lower latency there, even while us-east-1 is fully healthy; D is wrong because multivalue answer returns multiple IPs for client-side selection and does not guarantee 100% of traffic goes to one specific "primary" resource under normal conditions, nor does it provide a clean all-or-nothing failover semantics tied to a single primary/secondary hierarchy.
**Trigger words:** "100% of customer traffic must go to us-east-1," "if, and only if,... unavailable, all traffic must automatically shift," "no manual DNS changes."
**Underlying architectural principle:** Failover routing is the correct choice whenever a scenario describes a strict active/passive (primary/secondary) relationship with automatic, health-check-driven all-or-nothing traffic redirection.

---

### Question 71 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An online learning platform runs three independent Kubernetes-style microservice clusters, each in a different AWS Region, all serving the exact same content and all considered production-grade and equally capable of serving any user. The company wants basic DNS-level load spreading across all three clusters along with automatic exclusion of any cluster that fails a health check, but has a very small operational budget and explicitly does not want to pay for or manage a global load balancing service like AWS Global Accelerator or run a full Route 53 Traffic Flow policy record — they want the simplest native DNS mechanism available.
**Options:**
A. A multivalue answer routing policy record listing all three cluster endpoints, each with an associated Route 53 health check.
B. A weighted routing policy with equal weights (33/33/34) and no health checks configured.
C. AWS Global Accelerator with three endpoint groups, one per cluster.
D. A latency-based routing policy across all three clusters with Traffic Flow enabled for visualization.
**Correct answer(s):** A
**Why correct:** Multivalue answer routing is Route 53's lightweight, native mechanism for returning multiple healthy IP addresses per DNS query (up to eight), each independently health-checked, providing basic DNS-level load spreading and automatic exclusion of failed endpoints — matching the stated need for simplicity and low operational/cost overhead without adopting a full traffic-management product.
**Why each wrong option is wrong:** B is wrong because without health checks configured, an unhealthy cluster would keep receiving its share of traffic indefinitely, failing the "automatic exclusion of any cluster that fails a health check" requirement; C is wrong because Global Accelerator is explicitly called out in the scenario as something the team does not want to pay for or manage; D is wrong because Traffic Flow is a paid, policy-record-based visual traffic management feature the scenario explicitly wants to avoid, and latency-based routing alone (without multivalue's multiple-IP-per-response behavior) returns only a single best endpoint rather than DNS-level spreading across all three.
**Trigger words:** "basic DNS-level load spreading," "automatic exclusion of any cluster that fails a health check," "very small operational budget," "simplest native DNS mechanism."
**Underlying architectural principle:** Multivalue answer routing is the low-cost, health-check-aware, DNS-only alternative to a true load balancer or traffic-management service when basic multi-endpoint spreading is all that's required.

---

### Question 72 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A financial services firm runs its trading platform across two AZs within a single region: two ALBs (one per AZ, intentionally not sharing a single ALB to reduce blast radius), two separate Auto Scaling groups, and two independent RDS Multi-AZ clusters, with no data or traffic sharing between the two "cells." An architect reviewing the design flags that Route 53 currently has a single simple routing record pointing only at the AZ-A ALB, meaning all customer traffic depends entirely on AZ-A's ALB being reachable, even though the AZ-B cell is fully built and idle. The firm wants both cells actively used under normal conditions to maximize the value of the AZ-B investment, while still shifting fully away from either cell if that cell's ALB becomes unhealthy.
**Options:**
A. Replace the single simple routing record with a failover routing policy that treats one ALB as primary and the other as secondary, each behind its own Route 53 health check.
B. Replace the single simple routing record with a weighted routing policy (e.g., 50/50) across both ALBs, each behind its own Route 53 health check, so an unhealthy ALB's weight is effectively removed from consideration.
C. Keep the simple routing record as is, since ALBs are already highly available by default and DNS-level distribution isn't necessary.
D. Add a second simple routing record for the AZ-B ALB with the same record name, relying on round-robin behavior between the two records.
**Correct answer(s):** B
**Why correct:** Weighted routing with health checks on each weighted record lets Route 53 actively distribute traffic across both ALBs under normal conditions (satisfying "both cells actively used"), while automatically excluding a record from answers once its associated health check fails, achieving the "shift fully away from either cell if... unhealthy" requirement — matching an active/active goal rather than the active/passive model of failover routing.
**Why each wrong option is wrong:** A is wrong because failover routing is an active/passive model — it sends 100% of traffic to the primary and ignores the secondary entirely as long as the primary is healthy, which fails the stated goal of actively using both cells simultaneously; C is wrong because a single simple routing record pointed at only one AZ's ALB makes that specific ALB a Route-53-level single point of failure regardless of how resilient the ALB itself is internally, since no DNS answer ever points anywhere else; D is wrong (and not actually achievable as described) because Route 53 does not allow two separate resource record sets with the same name and type under the Simple routing policy — Simple routing supports only a single record per name/type (a lone Simple record can list multiple IP values, which gives basic client-side round-robin, but with no per-value health-check exclusion). Getting weighted, health-check-driven distribution across two named endpoints requires switching to the Weighted (or Multivalue Answer) routing policy specifically — which is exactly what B does.
**Trigger words:** "single simple routing record pointing only at the AZ-A ALB," "both cells actively used under normal conditions," "shifting fully away from either cell if that cell's ALB becomes unhealthy."
**Underlying architectural principle:** A single DNS record pointing at one resource reintroduces a single point of failure even when that resource is itself internally redundant; active/active distribution with health-check-based exclusion calls for weighted (or latency-based) routing, not failover routing.

---

### Question 73 [Priority: P0] [Difficulty: Easy] [Type: Multiple-Response]
**Scenario:** A three-tier application currently has the following architecture: an Application Load Balancer spanning two AZs, an Auto Scaling group spanning two AZs, a single RDS instance (no Multi-AZ) in one AZ, and a single NAT Gateway in one AZ shared by both AZs' private subnets. The team has been asked to identify which elements currently represent single points of failure that could cause an outage if their specific AZ fails.
**Options:**
A. The single RDS instance with no Multi-AZ configuration.
B. The single NAT Gateway shared across both AZs.
C. The Application Load Balancer, since it only has one DNS name.
D. The Auto Scaling group, since it only has one name/identifier.
E. The two-AZ span of the Auto Scaling group itself.
**Correct answer(s):** A, B
**Why correct:** The RDS instance (A) and the single shared NAT Gateway (B) are both confined to a single AZ, meaning the loss of that specific AZ takes down database access and outbound internet access for the entire application, regardless of how healthy the other AZ's resources are — these are the genuine single points of failure in this design.
**Why each wrong option is wrong:** C is wrong because an ALB is a managed, inherently multi-AZ service when configured to span multiple AZs (as stated here) — having one DNS name does not make it AZ-bound the way a NAT Gateway or standalone EC2/RDS instance is; D is wrong for the same reason — having a single logical ASG name is irrelevant to fault tolerance, since the ASG's actual EC2 instances are correctly spread across two AZs; E is wrong because spanning two AZs is the correct, resilient design for an Auto Scaling group — it is the described SPOF-free part of the architecture, not a SPOF itself.
**Trigger words:** "single RDS instance (no Multi-AZ)," "single NAT Gateway shared across both AZs," "single points of failure... if their specific AZ fails."
**Underlying architectural principle:** A resource confined to a single AZ (regardless of the rest of the stack's redundancy) reintroduces an AZ-level single point of failure; managed multi-AZ services like a correctly configured ALB or ASG are not automatically SPOFs just because they have one logical name.

---

### Question 74 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An architect is redesigning a legacy payment-processing platform that currently has these known issues: (1) a single Elastic IP is attached to a single standalone EC2 instance running the payment gateway software, with no load balancer or Auto Scaling group in front of it; (2) the RDS database is single-AZ; (3) all application logs are written only to that instance's local EBS volume with no shipping to a durable store; (4) DNS currently uses a single simple routing record pointing directly at the instance's Elastic IP. Which two changes would most directly eliminate single points of failure described here?
**Options:**
A. Replace the standalone EC2 instance with an Auto Scaling group (min size ≥ 2, spanning multiple AZs) behind an Application Load Balancer, updating the Route 53 record to alias to the ALB.
B. Enable RDS Multi-AZ for the database.
C. Increase the standalone EC2 instance's size to a larger instance type to reduce the chance of failure.
D. Configure the EC2 instance to write logs to a second local EBS volume in addition to the first, for redundancy.
E. Switch the Route 53 record from simple routing to latency-based routing, still pointing at the same single Elastic IP.
**Correct answer(s):** A, B
**Why correct:** Option A removes the single-instance, single-Elastic-IP dependency entirely by introducing a multi-AZ Auto Scaling group behind an ALB, which also resolves the DNS single-point-of-failure issue since the record now points at a resilient, multi-target ALB rather than one static IP; option B removes the single-AZ database as a point of failure via automatic, synchronous standby failover.
**Why each wrong option is wrong:** C only makes a single point of failure "bigger and presumably more reliable per-unit," but a single, larger instance is still exactly one instance — it remains a complete SPOF if that one instance or its AZ fails; D keeps logs durable only within the same single instance/AZ, so losing that instance or its AZ still risks losing the logs, and it does nothing about the compute, database, or DNS SPOFs; E is a routing-policy change with no effect at all, since it's explicitly stated to still point at the exact same single Elastic IP/instance — the underlying SPOF is untouched.
**Trigger words:** "single Elastic IP is attached to a single standalone EC2 instance," "no load balancer or Auto Scaling group," "RDS database is single-AZ," "most directly eliminate single points of failure."
**Underlying architectural principle:** Eliminating a single point of failure requires actually introducing redundant, independently-failing resources (multiple instances/AZs) — resizing, duplicating within the same failure domain, or changing an unrelated routing policy does not remove the underlying SPOF.

---

### Question 75 [Priority: P2] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A logistics company runs a fleet of IoT gateway devices that establish long-lived TCP connections to a backend ingestion service in AWS to stream sensor telemetry continuously. The ingestion service must (1) preserve the original client IP for downstream device-authentication logic that keys off IP reputation, (2) support a static IP address per AZ that the device firmware can safely allowlist in restrictive corporate firewalls, and (3) handle extremely high and bursty connection volumes with minimal added latency. The team is deciding between load balancer types and is also considering whether any Route 53 configuration changes are needed.
**Options:**
A. Use a Network Load Balancer in front of the ingestion service, since NLB provides static IP addresses per AZ (or supports Elastic IPs) and preserves the original client source IP by default.
B. Use an Application Load Balancer instead, since ALB automatically preserves client IP in the `X-Forwarded-For` header, which is functionally equivalent for this use case.
C. Rely on NLB's Layer 4 design and connection-handling to absorb extremely high, bursty long-lived TCP connection volume with low added latency.
D. Add a Route 53 latency-based routing policy across multiple NLBs in different regions, since this is required for any high-throughput ingestion workload.
E. Assume ALB's `X-Forwarded-For` header requires no application-side code changes to parse compared to using the raw source IP with NLB.
**Correct answer(s):** A, C
**Why correct:** NLB is the correct load balancer here because it natively supports static/Elastic IPs per AZ (satisfying firewall allowlisting) and preserves the true client source IP at the network layer by default (satisfying IP-reputation logic) — option A; and NLB's Layer 4 architecture is specifically built to handle very high volumes of long-lived TCP connections with minimal latency overhead — option C.
**Why each wrong option is wrong:** B is wrong because relying on the `X-Forwarded-For` header from an ALB is not "functionally equivalent" to raw source IP preservation — it requires the application to trust and correctly parse a header (which can be more error-prone, especially behind additional proxies) rather than reading the connection's actual source IP directly, and ALB doesn't offer the same static-IP-per-AZ guarantee that firewall allowlisting needs; D is wrong because nothing in the scenario requires multi-region deployment or latency-based routing — that's an unjustified architectural addition not supported by any stated requirement; E is wrong because it inverts the actual trade-off — using NLB with the real source IP typically requires zero application-side parsing changes, whereas relying on `X-Forwarded-For` from an ALB does require application code to extract and trust that header correctly.
**Trigger words:** "preserve the original client IP," "static IP address per AZ... allowlist," "extremely high and bursty connection volumes with minimal added latency," "long-lived TCP connections."
**Underlying architectural principle:** NLB's Layer 4 design, native client-IP preservation, and static/Elastic IP support make it the correct choice over ALB whenever firewall allowlisting or true source-IP-based logic (rather than a forwarded header) is required alongside high-throughput, low-latency connection handling.

---

### Question 76 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A multinational retailer operates six regional Application Load Balancers behind Route 53, one per continent-scale market, and currently uses a geolocation routing policy mapping each continent to its regional ALB — with no default ("*") record configured to catch unmapped or failed-over locations. During a major shopping event, the South America ALB begins failing its Route 53 health check due to a regional capacity issue, and the team is alarmed to discover that South American users are now getting no valid DNS answer at all for the domain (queries from that location go unresolved) instead of being routed anywhere, even though four of the other five regional ALBs are healthy and technically capable of absorbing overflow traffic.
**Options:**
A. This is expected geolocation routing behavior without a fallback in place: unlike latency-based or weighted routing, geolocation records with an associated failing health check and no alternate resource for that location will return no answer rather than automatically overflowing traffic elsewhere; the fix is to add explicit failover behavior (e.g., a secondary geolocation record for South America pointing to another healthy regional ALB, or combining with a failover routing policy).
B. This indicates Route 53 itself is malfunctioning, since DNS should never fail to resolve as long as any healthy endpoint exists anywhere in the account.
C. Geolocation routing automatically overflows to the geographically nearest healthy region by default, so this must be a misconfigured health check threshold rather than a routing behavior issue.
D. The fix is to switch entirely to a single global Simple routing record, since it would guarantee an answer is always returned.
**Correct answer(s):** A
**Why correct:** Geolocation routing strictly maps a location to a specific record/resource; if that specific record's associated health check fails and there is no explicit alternate/failover resource configured for that same location, Route 53 will not automatically substitute a different geographic region's healthy resource — the location simply gets no valid DNS answer, which matches the described behavior, and the correct remediation is to add an explicit fallback (a secondary record or a nested failover configuration) for that location. (Note: had a default/"*" record been configured, Route 53 *would* automatically fall back to it once South America's record failed its health check — a default record is itself a valid form of fallback. The root cause here is specifically that no default record and no location-specific secondary/failover record exist for South America.)
**Why each wrong option is wrong:** B is wrong because this is documented, expected behavior of geolocation routing's location-to-resource binding, not a Route 53 malfunction — the service is behaving correctly according to its configured policy, which lacks a fallback; C is wrong because geolocation routing does not have any built-in "nearest healthy region" overflow behavior — that kind of dynamic reassignment is not part of how geolocation resolves failing health checks, so no such default exists to be "misconfigured"; D is wrong because a single global simple record would indeed always return an answer, but it would send 100% of global traffic — including from every continent — to one ALB, destroying the entire purpose of the regional geolocation design and creating a severe overload/latency problem for everyone.
**Trigger words:** "South America ALB begins failing its... health check," "South American users are now getting no valid DNS answer... instead of being routed anywhere," "four of the other five regional ALBs are healthy."
**Underlying architectural principle:** Geolocation routing does not automatically fail over to a different geographic region's resource on health-check failure; the only built-in fallback is a configured default ("*") record (or a nested failover configuration for that location). Production geolocation designs need one of those explicit fallbacks for each location to avoid unresolvable DNS answers during a regional outage.

---

### Question 77 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A B2B SaaS company runs its API on ECS Fargate tasks registered to target groups behind an Application Load Balancer, spread across three AZs. Customers connect over HTTPS, and several enterprise customers require the ability to know they are always talking to one of a small, fixed set of IP addresses so they can configure narrow allowlist rules in their own corporate firewalls, since their security teams refuse to allowlist a broad or changing CIDR range. The company does not want to change its load balancer type if it can avoid an architectural rewrite, since ALB's path-based routing across several microservice target groups is a hard requirement.
**Options:**
A. Attach an AWS Global Accelerator in front of the existing ALB, giving customers a small set of static Anycast IP addresses to allowlist while keeping the ALB and all of its Layer 7 routing behavior unchanged.
B. Request that ALB be assigned static Elastic IP addresses directly, since ALB supports Elastic IP assignment in the same way NLB does.
C. Replace the ALB entirely with an NLB to get static IP addresses, and reimplement path-based routing using target group weighted rules on the NLB.
D. Tell the enterprise customers to instead allowlist the entire published AWS IP address range for the region.
**Correct answer(s):** A
**Why correct:** Global Accelerator provisions a small, fixed set of static Anycast IP addresses that can sit in front of an existing ALB without changing the ALB itself, letting the company keep all of its required Layer 7 path-based routing while giving enterprise customers the small, stable IP set their firewalls need.
**Why each wrong option is wrong:** B is wrong because, unlike NLB, ALB does not support direct assignment of static Elastic IP addresses to its listener — its IP addresses can change over time; C is wrong because it would require abandoning ALB's Layer 7 path-based routing capability entirely, which the scenario explicitly states is a hard requirement, and NLB does not perform HTTP path-based routing the way ALB does; D is an operationally unreasonable answer since AWS regional IP ranges are broad, large, and shared across countless AWS customers, which defeats the purpose of a narrow allowlist and is not something enterprise security teams would accept.
**Trigger words:** "small, fixed set of IP addresses," "refuse to allowlist a broad or changing CIDR range," "does not want to change its load balancer type," "path-based routing... is a hard requirement."
**Underlying architectural principle:** AWS Global Accelerator provides static Anycast IPs in front of existing load balancers (including ALB) without requiring a load-balancer-type change, making it the standard fix when static-IP allowlisting must coexist with ALB's Layer 7 features.

---

### Question 78 [Priority: P2] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An architect is reviewing a proposed multi-region active-active e-commerce design: production traffic is served simultaneously from us-east-1 and eu-west-1, each with its own ALB, ASG spanning three AZs, and DynamoDB Global Tables for cart/session data. Route 53 uses a latency-based routing policy across both regional ALBs, each with an associated health check. The architect wants to confirm which two statements correctly describe remaining resilience considerations in this design, beyond what's already handled by the components described.
**Options:**
A. If an entire region's ALB and every AZ's targets become unreachable, Route 53's health check on that region's latency-based record will fail, and Route 53 will stop returning that region's ALB as an answer, directing new DNS resolutions to the healthy region.
B. Because DynamoDB Global Tables replicate asynchronously, concurrent writes to the same item key from both regions can conflict and are resolved via last-writer-wins, which the application must account for if strict per-item write consistency across regions is required.
C. Latency-based routing guarantees zero data loss for in-flight transactions during a regional failure, since Route 53 will instantly redirect all affected users before any request can fail.
D. Because each region's ALB spans three AZs, no additional Route 53-level health checking is necessary for the ALBs themselves — only for the individual EC2 targets.
E. Since traffic is being served from two regions simultaneously, this design has already achieved zero RTO and zero RPO under all failure scenarios by definition.
**Correct answer(s):** A, B
**Why correct:** A correctly describes how latency-based routing combined with per-record health checks provides regional-level automatic failover for new DNS resolutions once a region becomes fully unreachable; B correctly identifies the well-known DynamoDB Global Tables trade-off — asynchronous cross-region replication with last-writer-wins conflict resolution — which is a real remaining consideration the application layer must handle, not something the infrastructure resolves automatically.
**Why each wrong option is wrong:** C overstates DNS-based failover — DNS record TTLs, client-side caching, and already-in-flight requests to the failing region mean some requests can still fail or experience delay before traffic fully shifts, so "zero data loss" and "instantly" are not accurate guarantees of latency-based routing; D is wrong because Route 53 health checks are still valuable at the ALB/region level to detect broader regional-level failures (e.g., DNS/network path issues to the region) that individual target health checks inside the ALB wouldn't necessarily surface to Route 53 — the two health-check layers serve different purposes and neither one replaces the need for the other; E is wrong because active-active multi-region with asynchronous replication (as this design uses for DynamoDB Global Tables) does not achieve "zero RTO and zero RPO under all failure scenarios" — there is still replication lag and conflict-resolution behavior, and DNS-based failover itself is not instantaneous for every client.
**Trigger words:** "DynamoDB Global Tables," "latency-based routing policy... each with an associated health check," "remaining resilience considerations... beyond what's already handled."
**Underlying architectural principle:** Even a well-designed active-active multi-region architecture retains real resilience trade-offs — DNS-based failover is not instantaneous or loss-free, and asynchronously replicated multi-region data stores still require application-level handling of write conflicts.

---

### Question 79 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A retail startup is building an order-intake microservice. Orders must be processed in the exact sequence they were placed by each customer, and no order may ever be processed twice, even if a consumer crashes mid-processing. Throughput is modest — around 250 orders per second across all customers combined. The team wants the simplest AWS-managed queuing solution that guarantees strict per-customer ordering and exactly-once processing without building custom deduplication logic.
**Options:**
A. Amazon SQS Standard queue with a single consumer thread to preserve order
B. Amazon SQS FIFO queue using customer ID as the message group ID
C. Amazon SNS standard topic with an SQS subscriber
D. Amazon MQ with a single ActiveMQ broker and no clustering
**Correct answer(s):** B
**Why correct:** SQS FIFO queues guarantee strict ordering within a message group and provide built-in exactly-once processing (deduplication) when content-based deduplication or a deduplication ID is used. Using customer ID as the message group ID ensures per-customer order is preserved while still allowing parallelism across different customers, and 250 msg/sec is well within FIFO's throughput limits (especially with high-throughput mode).
**Why each wrong option is wrong:** A. SQS Standard cannot guarantee ordering or exactly-once delivery even with a single consumer, since it offers at-least-once delivery with only best-effort ordering. C. SNS standard topics do not guarantee ordering or deduplication, and adding an SQS standard subscriber inherits the same limitations. D. Amazon MQ is a valid message broker but is a heavier, self-managed-feeling service (unmanaged scaling/clustering) that is not the "simplest AWS-managed" fit compared to a purpose-built FIFO queue.
**Trigger words:** "exact sequence," "no order may ever be processed twice," "simplest AWS-managed"
**Underlying architectural principle:** Use SQS FIFO with message group IDs whenever strict ordering and exactly-once processing are hard requirements within logical partitions.

---

### Question 80 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media company ingests a single "video uploaded" event that must trigger four independent downstream workflows: thumbnail generation, transcoding, content moderation scanning, and metadata indexing. Each workflow runs at its own pace and uses different consumer technology (Lambda, ECS, and two third-party SaaS webhooks). The company wants to add or remove downstream consumers in the future without modifying the upload service, and each consumer must be able to process the event independently without losing messages if it is temporarily down.
**Options:**
A. Have the upload service call each downstream service's API directly via synchronous HTTP requests
B. Publish the event to an SNS topic with one SQS queue subscribed per downstream workflow
C. Publish the event to a single SQS Standard queue and have all four workflows poll it
D. Publish the event to an SQS FIFO queue and have each workflow poll it with a distinct message group ID
**Correct answer(s):** B
**Why correct:** The SNS fan-out pattern lets one publish operation deliver the event to multiple independent SQS queues, decoupling the publisher from consumers entirely. Each subscribing queue buffers messages durably for its own consumer, so a slow or down consumer doesn't affect others, and new consumers can be added by simply subscribing a new queue — no changes to the upload service.
**Why each wrong option is wrong:** A. Direct synchronous calls tightly couple the upload service to every consumer's availability and latency, defeating resilience and extensibility goals. C. A single SQS queue delivers each message to only one consumer (queues don't broadcast), so three of the four workflows would never see most messages. D. FIFO queues also deliver each message to a single consumer per group; message group IDs control ordering/parallelism, not multi-consumer fan-out.
**Trigger words:** "trigger four independent downstream workflows," "add or remove downstream consumers... without modifying the upload service," "process the event independently"
**Underlying architectural principle:** Use SNS-to-multiple-SQS fan-out when one event must reach many independent, durable, loosely-coupled consumers.

---

### Question 81 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A logistics company processes shipment update messages from an SQS Standard queue using a Lambda function. Occasionally a message contains malformed JSON that causes the Lambda function to throw an exception every time it's invoked with that message. Without a dead-letter queue, these poison messages are redelivered repeatedly, consuming Lambda invocations and delaying processing of valid messages behind them. The team wants failed messages set aside automatically after a bounded number of retries so an on-call engineer can inspect them later, while healthy messages continue flowing normally.
**Options:**
A. Reduce the queue's visibility timeout to 0 seconds so failed messages are retried immediately
B. Configure a redrive policy on the source queue pointing to a dead-letter queue with maxReceiveCount set to a small number like 3
C. Enable long polling on the source queue to reduce the number of empty receives
D. Set the source queue's message retention period to the minimum of 60 seconds
**Correct answer(s):** B
**Why correct:** A redrive policy with maxReceiveCount automatically moves a message to the configured dead-letter queue once it has been received (and presumably failed processing) that many times, isolating poison-pill messages so healthy messages aren't blocked and giving engineers a queue to inspect independently.
**Why each wrong option is wrong:** A. Setting visibility timeout to 0 would make the message immediately available again after every failed receive, increasing redundant retries rather than bounding them. C. Long polling reduces empty-receive API calls and cost but has no effect on how poison messages are isolated. D. Shrinking retention to 60 seconds risks losing legitimate unprocessed messages entirely and does not address the redrive/isolation requirement.
**Trigger words:** "redelivered repeatedly," "set aside automatically after a bounded number of retries," "inspect them later"
**Underlying architectural principle:** Dead-letter queues with a redrive policy isolate messages that repeatedly fail processing, preventing poison pills from blocking the main queue.

---

### Question 82 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An image-processing pipeline uses SQS Standard with a Lambda-based consumer (via event source mapping) that typically finishes processing each message in about 45 seconds, but occasionally, when downstream image transformation is complex, takes up to 4 minutes. The queue's visibility timeout is currently set to 30 seconds. The team has noticed duplicate processing: the same image is sometimes transformed twice, wasting compute and occasionally producing two output files. No changes to the consumer code are desired right now.
**Options:**
A. Decrease the visibility timeout further to speed up retries for failed messages
B. Increase the visibility timeout to comfortably exceed the maximum expected processing time (e.g., 5-6 minutes)
C. Switch the queue to short polling to reduce the delay before messages are redelivered
D. Reduce the Lambda function's reserved concurrency to prevent parallel processing of the same message
**Correct answer(s):** B
**Why correct:** When a consumer takes longer than the visibility timeout to process a message, SQS assumes the consumer failed and makes the message visible again for another consumer, causing duplicate processing. Setting the visibility timeout comfortably above the worst-case processing time (with margin) prevents the message from reappearing while it is still legitimately being processed.
**Why each wrong option is wrong:** A. Decreasing the visibility timeout would make the message reappear even sooner, worsening duplicate processing. C. Short vs. long polling affects how quickly a consumer discovers new messages in an empty queue, not how long a message stays invisible during processing. D. Reducing concurrency limits parallelism generally but does not stop the same message from becoming visible again to a second Lambda invocation once its visibility timeout expires — it doesn't address the root cause.
**Trigger words:** "takes up to 4 minutes," "visibility timeout is currently set to 30 seconds," "duplicate processing"
**Underlying architectural principle:** Visibility timeout must be set longer than the maximum realistic processing time to prevent a message from being redelivered to another consumer while still in flight.

---

### Question 83 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A ticketing platform uses an SQS FIFO queue to process seat reservation requests, using event ID (a unique concert date) as the message group ID so that seats for the same event are reserved in strict order. During a highly anticipated concert on-sale, the platform needs to sustain roughly 4,500 reservation messages per second for that single event ID, but reservations across the tens of thousands of other concerts on the platform remain low-volume. The team is willing to relax strict ordering down to a coarser granularity (for example, per seat section) for this one hot event if that's what it takes to hit the throughput target, but ordering must remain fully intact for every other, low-volume concert on the platform.
**Options:**
A. Switch the entire queue to SQS Standard to eliminate the FIFO throughput ceiling
B. Enable high-throughput mode on the FIFO queue and further shard the popular event's traffic across multiple message group IDs (e.g., by seat section), accepting a relaxed ordering guarantee within that event
C. Create a separate SQS FIFO queue per concert date and route traffic with an application-level router
D. Increase the number of consumers polling the single message group ID for the popular event
**Correct answer(s):** B
**Why correct:** A single FIFO message group is inherently limited in throughput because messages in that group are processed strictly sequentially; even with high-throughput mode enabled, a single group ID cannot exceed roughly 300 msg/sec (3,000 with batching). Splitting the hot event's traffic into multiple message group IDs (e.g., per seat section) parallelizes processing across groups, letting the platform reach ~4,500 msg/sec for that event at the cost of narrowing its ordering guarantee from event-wide to per-section — an acceptable tradeoff given the team's stated willingness to relax ordering for this one event, while every other concert (each on its own message group ID) keeps full per-event strict ordering untouched.
**Why each wrong option is wrong:** A. Moving the entire queue to SQS Standard would remove ordering and exactly-once-processing guarantees for every concert on the platform, not just the hot one — an unnecessary and unacceptable sacrifice when only a single event needs the throughput boost. C. Creating a separate FIFO queue per concert date doesn't by itself solve the throughput ceiling for the single hot event; that event's dedicated queue would still be bottlenecked by the per-message-group-id throughput cap unless its own traffic is also sharded across multiple group IDs. D. Adding more consumers to a single message group ID does not increase throughput because SQS FIFO only allows one message in a group to be in-flight (or delivered per ordering rules) at a time regardless of consumer count.
**Trigger words:** "roughly 4,500 reservation messages per second for that single event ID," "willing to relax strict ordering... for this one hot event," "ordering must remain fully intact for every other... concert," "high-throughput"
**Underlying architectural principle:** FIFO queue throughput scales with the number of distinct message group IDs, not the number of consumers, so scaling a hot logical partition beyond the per-group throughput cap requires intentionally sharding it into finer-grained groups, trading part of its ordering guarantee for throughput.

---

### Question 84 [Priority: P0] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A healthcare claims processor is redesigning its intake pipeline for resilience. Claims arrive from three separate hospital systems and must be validated by a Lambda function; a small percentage of claims fail validation permanently due to malformed data and should never block processing of valid claims. The company has a compliance requirement to retain failed claims for 14 days for audit review, and also wants an alert sent to the compliance team's email whenever a claim fails validation and is set aside. Ordering between different hospitals' claims is not required. Choose the two actions that best satisfy these requirements.
**Options:**
A. Configure a redrive policy on the intake SQS queue directing failed messages to a dedicated DLQ with a 14-day message retention period
B. Subscribe an SNS topic that emails the compliance team directly to the intake queue's redrive policy
C. Configure the DLQ to trigger a CloudWatch alarm on ApproximateNumberOfMessagesVisible, with the alarm's SNS action emailing the compliance team
D. Set the intake queue's visibility timeout to 14 days to match the compliance retention requirement
E. Increase maxReceiveCount to a very high number so claims are retried indefinitely instead of being moved to a DLQ
**Correct answer(s):** A, C
**Why correct:** A dead-letter queue with a redrive policy and retention set to 14 days isolates permanently-failing claims while meeting the audit retention requirement. Since SQS has no native "on message arrival" email notification, the standard pattern is a CloudWatch alarm on the DLQ's visible-message-count metric that triggers an SNS email notification to compliance whenever messages land there.
**Why each wrong option is wrong:** B. SQS redrive policies can only target another SQS queue as the DLQ destination, not an SNS topic directly, so this configuration is not valid. D. Visibility timeout controls how long an in-flight message is hidden from other consumers during processing, not how long messages are retained — conflating the two would break normal processing behavior. E. Retrying indefinitely (or with an extremely high maxReceiveCount) means permanently malformed claims would never be set aside and could keep consuming processing capacity, directly contradicting the "never block processing of valid claims" requirement.
**Trigger words:** "fail validation permanently," "never block processing," "retain failed claims for 14 days," "alert sent... whenever a claim fails"
**Underlying architectural principle:** DLQs isolate poison messages and satisfy retention/audit needs, while CloudWatch alarms on DLQ metrics (not the redrive policy itself) are the mechanism for real-time notification.

---

### Question 85 [Priority: P2] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A cost-conscious startup runs a low-traffic SQS Standard queue that receives roughly one message every few minutes. Their consumer application polls continuously using the default short polling configuration, and the team notices their SQS API request costs and CloudWatch logs are dominated by ReceiveMessage calls that return empty responses. They want to reduce both cost and empty-response noise without changing how quickly new messages are eventually picked up in a meaningful way for their use case.
**Options:**
A. Reduce the queue's visibility timeout so consumers poll more frequently
B. Enable long polling by setting ReceiveMessageWaitTimeSeconds to a value up to 20 seconds
C. Switch the queue from Standard to FIFO to reduce polling frequency
D. Increase the maxReceiveCount on the queue's redrive policy
**Correct answer(s):** B
**Why correct:** Long polling (setting the wait time up to 20 seconds) causes ReceiveMessage calls to wait for a message to arrive rather than returning immediately when the queue is empty, which drastically reduces the number of empty responses and the associated API call costs while still delivering messages promptly once they arrive.
**Why each wrong option is wrong:** A. Visibility timeout governs how long a received message stays hidden from other consumers during processing; it has no effect on empty-receive polling frequency or cost. C. FIFO queues have their own throughput and ordering characteristics but do not inherently reduce polling frequency or empty-response costs. D. maxReceiveCount is a redrive policy setting related to DLQ moves after repeated failed processing attempts, unrelated to polling behavior or cost.
**Trigger words:** "empty responses," "reduce both cost and empty-response noise," "without changing how quickly... picked up"
**Underlying architectural principle:** Long polling reduces empty ReceiveMessage responses and API costs for low-traffic queues by waiting for messages instead of returning immediately.

---

### Question 86 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An e-commerce company's order fulfillment system currently has the web front end call the warehouse service, payment service, and notification service synchronously in sequence for every order, and the front end times out or fails visibly to customers whenever any downstream service is slow or briefly unavailable. Leadership wants the front end to remain fast and available even during downstream outages, wants failed orders that can't be fulfilled after repeated attempts to be captured for manual review, and wants to avoid losing any order even under a full warehouse-service outage lasting up to two hours. Select the two changes that best achieve these goals.
**Options:**
A. Replace the synchronous calls with the front end publishing an "order placed" message to an SNS topic fanning out to SQS queues consumed independently by the warehouse, payment, and notification services
B. Configure a dead-letter queue on the warehouse service's SQS queue with an appropriate maxReceiveCount so orders that repeatedly fail fulfillment are captured for manual review
C. Keep the synchronous architecture but add exponential backoff retries in the front end's HTTP client for each downstream call
D. Enable server-side encryption (SSE-KMS) on the warehouse queue to protect order data at rest
E. Set the warehouse queue's message retention period to 60 seconds to force fast failure and immediate customer notification
**Correct answer(s):** A, B
**Why correct:** Decoupling via SNS fan-out to independent SQS queues (A) lets the front end respond immediately after publishing, insulating customers from downstream slowness or outages, since each service consumes and retries against its own durable queue at its own pace — and the queue's default message retention (up to 4 days) comfortably outlasts a 2-hour outage without any extra configuration. Adding a DLQ with a bounded maxReceiveCount on the warehouse queue (B) ensures orders that genuinely can't be fulfilled after repeated attempts are captured for manual review instead of being lost or retried forever.
**Why each wrong option is wrong:** C. Retrying synchronously in the front end still ties customer-facing latency and availability directly to downstream service health, failing the "remain fast and available during outages" goal. D. Encrypting the queue with SSE-KMS is a reasonable security practice, but it does nothing to address the availability, decoupling, or failed-order-capture requirements described, so it isn't one of the two changes that solve the stated problem. E. A 60-second retention would delete unprocessed orders long before even a short outage ends, directly causing order loss and violating the two-hour survivability requirement.
**Trigger words:** "remain fast and available even during downstream outages," "captured for manual review," "avoid losing any order... under a full warehouse-service outage lasting up to two hours"
**Underlying architectural principle:** Asynchronous queue-based decoupling isolates producer availability from consumer health, while DLQs provide the safety net for messages that exhaust legitimate retry attempts.

---

### Question 87 [Priority: P1] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A financial settlement service uses an SQS FIFO queue with content-based deduplication enabled to process fund-transfer instructions, using account ID as the message group ID. The consumer is an ECS task that calls a downstream banking API taking anywhere from 2 to 90 seconds depending on the bank's response time, and occasionally the ECS task itself is abruptly stopped by a deployment during processing. The team has observed that some transfers are executed twice by the downstream bank API, and investigation shows the visibility timeout is set to 30 seconds while the deduplication ID window (5 minutes) and message group ID configuration are otherwise correct. The team cannot change the downstream bank API to be idempotent in the short term. What is the most effective immediate fix?
**Options:**
A. Switch content-based deduplication off and generate explicit MessageDeduplicationId values instead
B. Increase the visibility timeout to safely exceed the maximum processing time (e.g., 120+ seconds) and extend it dynamically for tasks that run longer, while ensuring ECS task stop events allow in-flight processing to complete or the message to be safely returned
C. Reduce the number of ECS tasks consuming the queue to exactly one to eliminate concurrent processing
D. Change the message group ID from account ID to a random UUID per message to increase parallelism
**Correct answer(s):** B
**Why correct:** The duplicates are happening because a message becomes visible again (to be redelivered) after 30 seconds even though the consumer may still legitimately be processing it for up to 90 seconds, or because an abrupt task stop leaves the message's fate ambiguous; SQS's own deduplication window only prevents duplicate *enqueuing* within 5 minutes of an identical message, it does not prevent redelivery of an in-flight message whose visibility timeout expired. Raising the visibility timeout above worst-case processing time (and using ChangeMessageVisibility to extend it for long-running work) directly addresses the root cause of premature redelivery.
**Why each wrong option is wrong:** A. Deduplication ID controls whether SQS treats two *separately submitted* messages as duplicates within the dedup window; it has no bearing on a single message being redelivered after its visibility timeout expires during processing. C. Reducing to one consumer doesn't prevent the same message from becoming visible again to that same (or a replacement) consumer once the timeout lapses — the redelivery-during-processing problem persists. D. Randomizing message group IDs would break the required per-account ordering guarantee and does nothing to fix the visibility timeout mismatch causing duplicates.
**Trigger words:** "2 to 90 seconds," "visibility timeout is set to 30 seconds," "some transfers are executed twice," "cannot change the downstream bank API to be idempotent"
**Underlying architectural principle:** SQS deduplication ID/window prevents duplicate message ingestion, but only a correctly sized (and dynamically extendable) visibility timeout prevents duplicate delivery of a single message that is still being processed.

---

### Question 88 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** An e-commerce company's order-processing microservice needs to notify four independent downstream systems whenever a new order is placed: an inventory-reservation Lambda function, a shipping-label SQS-backed worker fleet, a third-party email/SMS notification service, and an analytics pipeline. Some of these consumers are occasionally offline for maintenance, and the company cannot tolerate losing an order event just because one consumer happens to be down at publish time. Each consumer also processes orders at a different rate and must not interfere with the others' processing. The company wants to add or remove consumers in the future without modifying the order service. Cost is a secondary concern; message durability and loose coupling are the priorities.

**Options:**
A. Publish order events to a single standard SQS queue and have all four consumers poll it
B. Publish order events to an SNS topic with the shipping and analytics systems subscribed directly via HTTPS endpoints, and the Lambda function invoked directly
C. Publish order events to an SNS topic and subscribe an SQS queue per consumer (fan-out pattern), letting each consumer poll its own queue at its own pace
D. Have the order service write directly to each consumer's queue or invoke each consumer's API synchronously in a loop

**Correct answer(s):** C

**Why correct:** The SNS-to-multiple-SQS fan-out pattern decouples the publisher from every consumer, gives each consumer a durable, independently-scaled buffer, and guarantees no message is lost even if a consumer is offline, since SQS retains messages until they are processed or expire.

**Why each wrong option is wrong:** A) A single SQS queue creates a competing-consumers scenario — only one of the four consumers would receive each message, not all four. B) Direct HTTPS/Lambda subscriptions with no SQS buffer risk message loss or throttling if a consumer endpoint is down or slow, and it also tightly couples delivery semantics to consumer availability. D) Direct synchronous writes/invocations tightly couple the order service to every consumer's availability and scaling, defeating the purpose of an event-driven architecture.

**Trigger words:** "notify four independent downstream systems," "occasionally offline," "cannot tolerate losing an order event," "add or remove consumers in the future without modifying the order service."

**Underlying architectural principle:** The SNS fan-out pattern (one topic, many SQS subscriber queues) is the standard way to achieve durable, decoupled, one-to-many message distribution in AWS.

---

### Question 89 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A SaaS integration team is building an event-driven backend that must ingest events natively from a third-party partner application (Zendesk), respond to native AWS service events (CodePipeline state changes), and route both types of events to different Step Functions state machines and Lambda functions based on the event's content. The team also wants AWS to automatically infer and store a schema for each event type so developers can generate strongly-typed code bindings in their IDE. They do not need to retain or replay raw event payloads for more than a day, and throughput is a few hundred events per minute.

**Options:**
A. Amazon SQS with separate queues per event type and consumer-side filtering logic
B. Amazon SNS with subscription filter policies for each target
C. Amazon EventBridge with a custom event bus, partner event source integration, rules for routing, and the schema registry enabled
D. Amazon Kinesis Data Streams with a Lambda consumer that inspects and routes each record

**Correct answer(s):** C

**Why correct:** EventBridge is purpose-built for exactly this: it natively supports partner (SaaS) event sources, AWS service events, content-based routing rules to multiple target types (including Step Functions and Lambda), and a built-in schema registry with code-binding generation — none of which the other services provide out of the box.

**Why each wrong option is wrong:** A) SQS has no native partner event source integration, no built-in content-based routing rules, and no schema registry. B) SNS can filter by message attributes but has no partner event source integrations and no schema registry/code-binding feature. D) Kinesis is designed for high-throughput streaming/ordered records, not discrete partner/service event routing, and requires custom code to inspect and route — it also has no schema registry for this use case.

**Trigger words:** "ingest events natively from a third-party partner application," "AWS to automatically infer and store a schema," "generate strongly-typed code bindings."

**Underlying architectural principle:** EventBridge is the AWS-native event bus for routing structured events from AWS services and SaaS partners with content-based rules and schema discovery, distinct from SNS (pub/sub messaging) and SQS (queuing).

---

### Question 90 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A ride-sharing company ingests GPS location pings from millions of driver devices. Three completely separate applications must all process every ping independently and in near real time: a live map-rendering service, a fraud-detection service, and a data lake ingestion job. Pings for a given driver must be processed in the exact order they were generated within that driver's session. If the fraud-detection service falls behind or needs to be redeployed, it must be able to re-read the last several hours of pings without affecting the other two applications. Peak throughput is roughly 50,000 pings per second.

**Options:**
A. A standard Amazon SQS queue with three consumer groups reading from it
B. An Amazon SQS FIFO queue with three separate consumer applications long-polling the same queue
C. Amazon Kinesis Data Streams with a partition key based on driver ID, and each application implemented as a separate consumer (e.g., using the Kinesis Client Library) reading independently from the stream
D. Amazon SNS with three SQS queues subscribed, one per application

**Correct answer(s):** C

**Why correct:** Kinesis Data Streams retains records for a configurable window (up to 365 days) and allows multiple independent consumer applications to read the same data at their own pace and replay from any point in the retention window, while partitioning by driver ID guarantees per-driver ordering within a shard — exactly the multi-consumer, replayable, ordered-per-key requirement described.

**Why each wrong option is wrong:** A) A standard SQS queue does not support multiple independent full reads of the same messages by different consumer groups, nor does it preserve per-key ordering. B) SQS FIFO does not allow multiple applications to each independently receive and reprocess every message — a message is deleted once one consumer processes it, and it also caps throughput well below 50,000/sec without high-throughput mode workarounds and still lacks replay. D) SNS+SQS fan-out (one queue per app) solves the multi-consumer problem but standard SNS/SQS queues don't guarantee ordering by driver, and SQS queues don't offer hours of replay after a message is deleted/processed.

**Trigger words:** "three completely separate applications must all process every ping independently," "must be processed in the exact order," "re-read the last several hours of pings without affecting the other two applications."

**Underlying architectural principle:** Kinesis Data Streams is the right choice when multiple independent consumers each need to read the full ordered data stream and require replay capability, unlike SQS/SNS where a message is consumed once.

---

### Question 91 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A manufacturing company has thousands of IoT sensors streaming temperature and vibration telemetry. The requirement is to land this data into an S3 data lake in Parquet format, partitioned by date/hour, for later querying with Athena, and also load a rolling aggregate into Amazon Redshift for a dashboard. A few minutes of latency between sensor reading and data landing in S3 is acceptable. The team explicitly wants to avoid writing or operating any custom consumer application, managing shards, or handling checkpointing — they want a fully managed "point at a destination and go" solution with built-in format conversion and compression.

**Options:**
A. Amazon Kinesis Data Streams with a Lambda consumer that batches records and writes Parquet files to S3
B. Amazon Kinesis Data Firehose delivering directly to S3 with Parquet conversion enabled, and a second Firehose delivery stream to Redshift
C. Amazon SQS with a scheduled Lambda function that polls, converts to Parquet, and uploads to S3
D. Amazon MSK (Managed Streaming for Kafka) with a Kafka Connect S3 sink connector

**Correct answer(s):** B

**Why correct:** Kinesis Data Firehose is the fully managed, no-shard-management, no-checkpointing delivery service purpose-built for near-real-time (seconds-to-minutes latency) loading into S3 and Redshift, with native record format conversion (JSON to Parquet/ORC) and compression built in — matching every stated requirement with zero custom consumer code.

**Why each wrong option is wrong:** A) This requires writing and operating a custom Lambda consumer, plus manual Parquet conversion logic — exactly what the team wants to avoid. C) SQS plus a polling Lambda is not a streaming-ingestion pattern, doesn't scale cleanly for thousands of sensors, and requires custom Parquet conversion code and orchestration. D) MSK requires standing up and operating a Kafka cluster (or MSK Serverless) plus Connect infrastructure — far more operational overhead than "point and go," and is overkill for a straightforward S3/Redshift delivery need.

**Trigger words:** "avoid writing or operating any custom consumer application," "fully managed 'point at a destination and go' solution," "built-in format conversion and compression," "a few minutes of latency ... is acceptable."

**Underlying architectural principle:** Choose Kinesis Data Firehose over Data Streams when you need managed, near-real-time delivery to a fixed set of destinations (S3, Redshift, OpenSearch, etc.) without writing consumer code; choose Data Streams when you need custom, low-latency, multi-consumer processing logic.

---

### Question 92 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A retail company publishes every order event (as JSON, including an `orderTotal` numeric field and a `region` string field) to a single EventBridge custom bus. Compliance requires that only orders where `orderTotal` is greater than 10,000 AND `region` equals `"EU"` are forwarded to a dedicated fraud-review Step Functions workflow — all other orders must never reach that workflow, and no Lambda-based pre-filtering code should be introduced (to minimize cost and latency). The team is deciding how to configure the routing rule.

**Options:**
A. Create an EventBridge rule with an event pattern using the `numeric` matching operator (e.g., `[{"numeric": [">", 10000]}]`) on `orderTotal` combined with an exact match on `region`, targeting the Step Functions state machine directly
B. Create an EventBridge rule that matches on `region` only, and have the Step Functions state machine's first state evaluate `orderTotal` and exit early if it's below the threshold
C. Subscribe an SNS topic to all order events and use an SNS filter policy with a numeric condition on `orderTotal`, then have the SNS topic invoke the Step Functions workflow
D. Create a Lambda function subscribed to all events that checks both conditions in code and manually starts the Step Functions execution only when both are true

**Correct answer(s):** A

**Why correct:** EventBridge event patterns natively support numeric comparison operators and exact-match string conditions combined in a single pattern, allowing precise content-based filtering with zero custom code, no wasted Step Functions executions, and EventBridge can invoke Step Functions as a native target.

**Why each wrong option is wrong:** B) This still starts (and pays for/logs) a Step Functions execution for every EU order regardless of amount, violating the "must never reach that workflow" requirement and wasting cost. C) SNS has no native subscription protocol for Step Functions state machines, so it cannot directly target Step Functions as an invocation target without an intermediary (e.g., Lambda or SQS+poller), adding unnecessary components. D) This reintroduces the custom Lambda pre-filtering code the requirement explicitly says to avoid.

**Trigger words:** "no Lambda-based pre-filtering code should be introduced," "must never reach that workflow," "greater than 10,000 AND region equals."

**Underlying architectural principle:** EventBridge's rich event-pattern matching (including numeric, prefix, exists, and anything-but operators) enables serverless, code-free content-based routing that SNS's simpler attribute-based filter policies cannot fully replicate.

---

### Question 93 [Priority: P0] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A logistics company is redesigning its order-fulfillment process: payment authorization, inventory reservation, and carrier label generation happen in sequence, with automatic retries using exponential backoff on transient failures. For any order over $5,000, the workflow must pause — for up to several days if necessary — until a human fraud reviewer approves it via a separate internal web application, after which the workflow resumes exactly where it left off. Auditors require a complete, queryable execution history showing every state transition, input, and output for each order, retained for compliance review. The architecture team is deciding how to implement the pause-for-approval step and which workflow type to use. (Select TWO.)

**Options:**
A. Use an AWS Step Functions Standard Workflow, since it supports executions lasting up to one year and provides a complete, retained execution history for each run
B. Implement the human-approval pause using the Step Functions task token ("waitForTaskToken") integration, where the workflow halts until the review application calls SendTaskSuccess or SendTaskFailure
C. Use an AWS Step Functions Express Workflow, since it is cheaper per execution and this is a high-volume order process
D. Chain the entire multi-step process using only EventBridge rules, where each service publishes a completion event that a rule routes to the next service
E. Use an SQS standard queue with a 12-hour maximum visibility timeout to hold the order while waiting for reviewer approval

**Correct answer(s):** A, B

**Why correct:** Standard Workflows support long-running executions (up to a year) and retain full execution history for audit purposes, and the task-token callback pattern is the AWS-native mechanism for pausing a state machine indefinitely until an external system explicitly signals completion — exactly matching the multi-day human-approval requirement.

**Why each wrong option is wrong:** C) Express Workflows are capped at a 5-minute maximum duration and don't retain long-term execution history in the same queryable way, making them unsuitable for a multi-day pause with audit requirements. D) EventBridge has no built-in concept of pausing/resuming a stateful, multi-day workflow or waiting for an external callback — it's a stateless router, not an orchestrator with execution state. E) SQS's maximum visibility timeout (12 hours) is far shorter than "several days," and a queue has no mechanism to represent a paused, resumable multi-step execution with full state.

**Trigger words:** "pause — for up to several days if necessary — until a human fraud reviewer approves," "resumes exactly where it left off," "complete, queryable execution history."

**Underlying architectural principle:** Use Step Functions Standard Workflows with the task-token callback pattern for long-running, human-in-the-loop orchestration requiring durable state and audit history; EventBridge excels at stateless event routing, not multi-day stateful orchestration.

---

### Question 94 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A bank's core-banking platform publishes per-account transaction events that must be fanned out to three independent downstream systems: the general ledger, real-time fraud scoring, and customer notifications. Regulatory requirements mandate that, for any given account, all three downstream systems must receive and be able to process transactions in the exact same relative order that they occurred — a debit must never be visible to any consumer before its preceding credit for the same account. Duplicate transaction publishes (from upstream retries) within a 5-minute window must also be automatically deduplicated before fan-out, without custom dedup code. The three consumers must remain fully decoupled so that any one of them can be down or slow without affecting the others.

**Options:**
A. Publish to a standard SNS topic with three standard SQS queues subscribed (one per consumer)
B. Publish to an SNS FIFO topic using the account ID as the MessageGroupId and content-based deduplication enabled, with an SQS FIFO queue subscribed for each of the three consumers
C. Publish to a single Kinesis Data Stream partitioned by account ID, with each consumer implementing its own KCL application and custom deduplication logic
D. Publish to an SNS FIFO topic with three standard SQS queues subscribed, relying on SNS FIFO's ordering guarantee to flow through to standard queues

**Correct answer(s):** B

**Why correct:** SNS FIFO preserves strict publish order and provides built-in content-based deduplication at the topic level, and when subscribed by SQS FIFO queues (the only queue type that preserves that ordering end-to-end), each of the three consumers gets its own fully ordered, deduplicated, independently-consumable copy of every transaction — satisfying ordering, dedup, and decoupling simultaneously with zero custom code.

**Why each wrong option is wrong:** A) Standard SNS/SQS provide only best-effort ordering and no deduplication, failing the strict per-account ordering and dedup requirements. C) Kinesis preserves per-partition-key order but has no built-in deduplication feature, forcing the "custom dedup code" the requirement wants to avoid, and burdens each of the three teams with operating their own KCL consumer application. D) SNS FIFO topics can only be subscribed by SQS FIFO queues in the first place — AWS does not permit subscribing a standard (non-FIFO) SQS queue to an SNS FIFO topic — so this configuration isn't achievable as described, and even conceptually it would break the end-to-end ordering guarantee, which only holds when SQS FIFO queues are used throughout.

**Trigger words:** "exact same relative order," "duplicate transaction publishes ... must also be automatically deduplicated," "without custom dedup code," "remain fully decoupled."

**Underlying architectural principle:** Strict ordering and built-in deduplication in a fan-out architecture require SNS FIFO topics paired with SQS FIFO subscriber queues end-to-end — mixing in any standard component breaks the ordering/dedup guarantee (and in fact, SNS FIFO topics don't allow standard SQS subscriptions at all).

---

### Question 95 [Priority: P3] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A global trading platform uses a central EventBridge custom event bus in `us-east-1` as the backbone for order and market-data events consumed by dozens of internal services, with a Step Functions state machine and multiple Lambda targets subscribed via rules. The business has set an RTO of 30 seconds and an RPO as close to zero as possible for this event bus in the event of a regional outage of `us-east-1`, and requires that event ingestion automatically fail over to `eu-west-1` without manual intervention, with minimal event loss during the cutover. The team is finalizing the multi-region resilience design. (Select TWO.)

**Options:**
A. Configure EventBridge Global Endpoints across the two event buses (one per region) with a Route 53 health check, so that PutEvents calls are automatically routed to the healthy region within the configured failover interval
B. Enable event replication for the Global Endpoint so that events routed to the primary bus are also replicated to the secondary region's bus, keeping it synchronized for failover
C. Rely on native SNS topic cross-region replication to mirror all EventBridge targets' notifications into `eu-west-1` automatically
D. Run a single EventBridge bus only in `us-east-1` and use a scheduled Lambda function in `eu-west-1` that is manually triggered by on-call engineers if a regional outage is detected
E. Replicate the Step Functions Standard Workflow executions to `eu-west-1` using S3 Cross-Region Replication of the execution history so workflows resume automatically in the secondary region

**Correct answer(s):** A, B

**Why correct:** EventBridge Global Endpoints, combined with a Route 53 health check, provide automatic, near-real-time failover of `PutEvents` traffic between two regional event buses to meet a tight RTO, and enabling event replication on the Global Endpoint keeps the secondary bus continuously synchronized with events sent to the primary, minimizing event loss (near-zero RPO) during a failover.

**Why each wrong option is wrong:** C) SNS has no native cross-region topic replication feature — this option describes a nonexistent capability. D) A manual, on-call-triggered failover cannot meet a 30-second automated RTO requirement. E) Step Functions does not store execution history in S3, and there is no mechanism to "resume" a Standard Workflow execution in another region via S3 replication — executions are region-bound and this approach would not work as described.

**Trigger words:** "RTO of 30 seconds," "RPO as close to zero as possible," "automatically fail over ... without manual intervention," "minimal event loss during the cutover."

**Underlying architectural principle:** EventBridge Global Endpoints with Route 53 health checks and managed event replication is the purpose-built AWS mechanism for automated, low-RPO/low-RTO multi-region failover of event ingestion — don't assume cross-region replication exists natively for every messaging service (e.g., SNS).

---

### Question 96 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A ticketing platform runs a Java web application behind an Application Load Balancer and an Auto Scaling group. Average CPU utilization fluctuates unpredictably throughout the day — sometimes 20%, sometimes 70% — with no recurring daily pattern the team can rely on. The platform team wants the ASG to continuously and automatically add or remove instances to keep average CPU near 50%, without the team having to define and maintain multiple manual thresholds.
**Options:**
A. Configure a target tracking scaling policy with a target value of 50% average CPU utilization.
B. Configure simple scaling with a single CloudWatch alarm threshold at 50% CPU and a fixed cooldown period.
C. Configure scheduled scaling actions that increase capacity at historically busy hours of the day.
D. Have an operator manually run `aws autoscaling set-desired-capacity` via a cron job on a monitoring server.
**Correct answer(s):** A
**Why correct:** Target tracking scaling is purpose-built to keep a chosen metric at (or near) a specified target value, continuously adjusting capacity up or down without manually maintained thresholds — exactly what's needed for unpredictable, non-recurring traffic.
**Why each wrong option is wrong:** B (simple scaling) reacts to a single alarm crossing a threshold and then waits out a cooldown before acting again, which doesn't continuously track a target the way target tracking does, and still requires manual threshold tuning; C (scheduled scaling) only helps if traffic follows a known, recurring time pattern, which this scenario explicitly says it does not; D introduces manual operational overhead and a single point of failure (the monitoring server/cron job), which defeats the goal of automatic scaling.
**Trigger words:** "fluctuates unpredictably," "no recurring daily pattern," "keep average CPU near 50%," "without... manually maintained... thresholds."
**Underlying architectural principle:** Target tracking is the default best-practice Auto Scaling policy for maintaining a metric at a set point under unpredictable load.

---

### Question 97 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company runs an Auto Scaling group of EC2 instances registered to an ALB target group. The EC2 console shows all instances as healthy, but the ALB target group console shows roughly 30% of targets as unhealthy because the application intermittently returns HTTP 500 on its `/health` endpoint due to a slow-starting internal cache. The ASG never replaces these targets, so a meaningful share of live customer traffic keeps hitting instances returning errors.
**Options:**
A. Enable the ELB health check type on the Auto Scaling group so the ASG uses the target group's health check results to decide when to replace instances.
B. Set the ASG's health check grace period to 0 seconds so instances are evaluated immediately after launch.
C. Increase the target group's deregistration delay to 900 seconds.
D. Replace the ALB with a Network Load Balancer, since NLB health checks are stricter than ALB health checks.
**Correct answer(s):** A
**Why correct:** By default, an ASG only uses EC2 status checks (instance reachability), which cannot see application-level failures reported by a target group. Enabling the ELB health check type makes the ASG honor the target group's health verdict and replace instances the load balancer considers unhealthy.
**Why each wrong option is wrong:** B changes when health evaluation starts, not which health check source the ASG listens to, and setting it to 0 would risk terminating instances before they even finish booting; C only controls how long an already-deregistering target keeps draining in-flight connections, it does nothing to make the ASG detect or act on the /health failures; D swaps load balancer types without addressing the actual root cause — the ASG still would not be configured to use ELB health check results, so replacing the ALB with an NLB (which can itself be configured with HTTP/HTTPS-based health checks, not just TCP) changes nothing about the ASG-to-target-group integration that's actually broken here.
**Trigger words:** "EC2 console shows all instances as healthy," "target group... shows... unhealthy," "ASG never replaces these targets."
**Underlying architectural principle:** An ASG must be explicitly configured to use ELB health checks, or it will remain blind to application-level failures that only the load balancer's health checks can detect.

---

### Question 98 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A media transcoding company runs its worker fleet on Spot Instances in an Auto Scaling group spread across three Availability Zones to control compute cost — the team is cost-sensitive and must continue using Spot Instances rather than On-Demand. Each instance takes about 6 minutes to boot and initialize because it must download large codec libraries before it can process jobs. The team wants to (1) reduce the customer-facing impact when Spot Instances receive an interruption notice, and (2) reduce the lag between a scale-out trigger and having usable capacity, without paying for a fully active standby fleet at all times.
**Options:**
A. Enable Auto Scaling group Capacity Rebalancing and maintain a Warm Pool of pre-initialized, mostly-stopped instances.
B. Change the ASG termination policy to `OldestInstance` and disable automatic instance rebalancing.
C. Migrate the entire fleet from Spot to On-Demand Instances and rely on target tracking scaling alone.
D. Run a single large Spot Instance outside of an Auto Scaling group with a shell script that restarts it if it's interrupted.
**Correct answer(s):** A
**Why correct:** Capacity Rebalancing proactively replaces Spot Instances that receive a rebalance recommendation before they're actually reclaimed, directly reducing interruption impact, while a Warm Pool keeps pre-initialized (largely stopped, low-cost) instances ready to join the ASG quickly, directly cutting the 6-minute boot lag — together they solve both stated problems without running a fully active standby fleet.
**Why each wrong option is wrong:** B's termination policy choice only affects which instance is selected for termination during scale-in, and disabling rebalancing actively removes the interruption-mitigation behavior the team needs; C solves reliability but directly contradicts the stated cost-sensitivity constraint requiring continued use of Spot; D removes Auto Scaling and multi-AZ resilience entirely, creating a single point of failure with no automated health-based recovery.
**Trigger words:** "cost-sensitive and must continue using Spot," "6 minutes to boot," "reduce... impact when Spot Instances receive an interruption notice," "without paying for a fully active standby fleet."
**Underlying architectural principle:** Warm Pools cut scale-out latency for slow-booting instances while Capacity Rebalancing proactively mitigates Spot interruptions — the two features solve different resilience problems and are commonly combined.

---

### Question 99 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An order-processing Lambda function is invoked asynchronously by S3 object-created events. Occasionally the function fails because a downstream partner API returns transient errors. The team wants failed events to never simply disappear, and wants a durable, queryable record of failed invocations that a separate reprocessing pipeline can consume later — with as little custom retry code as possible.
**Options:**
A. Configure an on-failure destination pointing to an SQS queue, so failed events are routed there automatically after Lambda's built-in asynchronous retries are exhausted.
B. Increase the Lambda function's timeout to 15 minutes so the transient partner API errors no longer cause failures.
C. Wrap the S3 event trigger in a synchronous Step Functions Express Workflow with a Catch state to handle errors.
D. Set the function's reserved concurrency to 0 until the partner API issue is resolved.
**Correct answer(s):** A
**Why correct:** Asynchronous Lambda invocations already retry automatically (twice, by default) on failure; configuring an on-failure destination is the native, code-minimal way to durably route events that still fail after those retries into SQS for later reprocessing, satisfying both the durability and "queryable record" requirements.
**Why each wrong option is wrong:** B doesn't address the root cause (an unreliable downstream API returning errors, not a slow one) and a longer timeout doesn't guarantee success or capture failures for reprocessing; C requires re-architecting the trigger path with a workflow orchestrator (S3 event notifications don't invoke Step Functions directly — an intermediary such as EventBridge would be needed), which is unnecessary custom-integration effort compared to the built-in destinations feature and doesn't fit "as little custom retry code as possible"; D would stop the function from processing any events at all, losing new orders rather than preserving failed ones.
**Trigger words:** "asynchronously," "transient errors," "never simply disappear," "durable, queryable record," "as little custom retry code as possible."
**Underlying architectural principle:** Lambda's built-in asynchronous retry behavior combined with on-failure destinations is the standard, low-code pattern for capturing and durably routing failed async invocations.

---

### Question 100 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A small nonprofit runs a low-traffic donor management application. The budget is extremely tight, and leadership has explicitly accepted up to 8 hours of downtime and up to 24 hours of data loss in the event of a regional disaster, since such an event is considered rare and no ongoing DR spend is desired. The team already takes nightly RDS and EBS snapshots and copies AMIs to a second region; nothing else currently runs in that second region.
**Options:**
A. Use AWS Backup (or equivalent) with cross-region copy of snapshots/AMIs, and keep CloudFormation templates ready so the full environment can be launched on demand in the second region only if a disaster is actually declared.
B. Run a continuously replicating cross-region read replica of the database with no application servers running in the second region.
C. Run a full but downsized copy of the entire stack, including application servers, continuously in the second region.
D. Run full-capacity production stacks simultaneously in both regions behind Route 53 latency-based routing.
**Correct answer(s):** A
**Why correct:** With an 8-hour RTO and a 24-hour RPO tolerance and an explicit "extremely tight budget" constraint, nightly cross-region backups (worst case, up to ~24 hours of data since the last snapshot) plus templated, on-demand launch (Backup and Restore) meets the stated tolerances at the lowest possible ongoing cost — there is no requirement that justifies paying for any standing DR-region infrastructure.
**Why each wrong option is wrong:** B (Pilot Light) introduces continuous cross-region replication cost that isn't needed to meet an RPO measured in a full day, since nightly snapshots already satisfy a 24-hour RPO tolerance; C (Warm Standby) adds continuously running compute cost that directly conflicts with the stated tight budget and isn't needed for an 8-hour RTO; D (Multi-Site Active-Active) is the most expensive of the four strategies and wildly exceeds both the budget constraint and the stated tolerance for downtime/data loss.
**Trigger words:** "extremely tight budget," "up to 8 hours of downtime," "up to 24 hours of data loss," "nightly... snapshots," "nothing else currently runs."
**Underlying architectural principle:** When RTO/RPO tolerance is measured in hours and cost is the dominant constraint, the correct classification is Backup and Restore — even if the strategy is never named in the scenario.

---

### Question 101 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A SaaS company maintains an Aurora Global Database secondary cluster continuously replicating in a second AWS region, with sub-second replication lag. No EC2 or ECS application resources currently run in that second region at all. If a disaster is declared, the plan is to promote the Aurora secondary to a standalone writer and use pre-baked launch templates and CloudFormation stacks to stand up the application tier from scratch, targeting a recovery time of roughly 30–45 minutes.
**Options:**
A. Pilot Light — only the data layer is kept live in the DR region (giving a low RPO), while the compute/application tier is provisioned on demand, consistent with a 30–45 minute RTO.
B. Backup and Restore — because no compute is running continuously in the DR region.
C. Warm Standby — because a continuously replicating database qualifies as the "reduced capacity" tier that's already running.
D. Multi-Site Active-Active — because Aurora Global Database is technically capable of serving reads from the secondary region.
**Correct answer(s):** A
**Why correct:** The defining signature of Pilot Light is a continuously replicating data tier with zero standing compute, where the application tier is provisioned from templates only when a disaster is declared — this matches the scenario exactly, and the 30–45 minute RTO is consistent with needing to provision compute from scratch.
**Why each wrong option is wrong:** B is wrong because Backup and Restore has no continuous replication at all (just periodic backups), and its typical RTO is hours, not tens of minutes, which this sub-second-replication design clearly beats; C is wrong because Warm Standby requires the application/compute tier itself to also be running (even at reduced capacity) — here there is no compute tier running at all, only the database; D is wrong because Multi-Site Active-Active requires production traffic to actually be served from multiple regions simultaneously, and here the secondary is not promoted and no application tier exists there to serve anything.
**Trigger words:** "no... application resources currently run," "promote the Aurora secondary," "pre-baked launch templates," "30–45 minutes."
**Underlying architectural principle:** A continuously replicating data tier paired with zero standing compute is the defining signature of Pilot Light, regardless of whether the term ever appears in the scenario.

---

### Question 102 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An insurance claims portal keeps a full copy of its architecture running at all times in a secondary region: an ALB, two `t3.micro` application instances at the ASG's minimum capacity, and an RDS read replica continuously replicating from the primary region. Under normal conditions this secondary-region stack only receives internal health-check traffic, no customer traffic. During a scheduled failover drill, Route 53 failover routing shifts customer traffic to the secondary region, and the ASG there scales from 2 to 40 instances within about 6 minutes to absorb full production load. The stated RTO target is under 15 minutes and RPO under 5 minutes.
**Options:**
A. Warm Standby — a full stack, including the application tier, is already running at reduced capacity, and failover only requires scaling up rather than provisioning from nothing.
B. Pilot Light — because the running application tier is minimal, consisting of only two small instances.
C. Backup and Restore — because most of the production capacity is only provisioned after failover is triggered.
D. Multi-Site Active-Active — because customer traffic is actively being served from the secondary region during the drill.
**Correct answer(s):** A
**Why correct:** Warm Standby is defined by a full (but downsized) stack — including the application/compute tier — running continuously, with failover consisting only of a scale-up step; that is exactly what's described here, and the sub-15-minute RTO and sub-5-minute RPO align with Warm Standby's typical numbers.
**Why each wrong option is wrong:** B is wrong because Pilot Light requires the application/compute tier to be entirely absent under normal conditions, not merely small — two running instances actively capable of serving traffic disqualifies it from being Pilot Light; C is wrong because Backup and Restore has nothing standing continuously in the DR region and typically recovers in hours, not the minutes described here; D is wrong because Multi-Site Active-Active means both regions serve live production traffic under normal day-to-day conditions, not only during a failover drill or an actual disaster.
**Trigger words:** "full copy of its architecture running at all times," "two... application instances at... minimum capacity," "scales from 2 to 40... on failover," "RTO... under 15 minutes."
**Underlying architectural principle:** The discriminator between Pilot Light and Warm Standby is whether an application/compute tier is running at all — even minimally — versus being entirely absent until a disaster is declared.

---

### Question 103 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A global multiplayer leaderboard service uses DynamoDB Global Tables replicated across three regions, with application servers actively serving live read/write production traffic simultaneously in all three regions via Route 53 latency-based routing. The stated requirement is near-zero RTO/RPO and tolerance for the loss of any single region with no customer-visible impact. During a load test, two players in different regions update the same leaderboard record within milliseconds of each other, and the team is worried one of the two updates might be silently lost.
**Options:**
A. This is a known, inherent trade-off of DynamoDB Global Tables' last-writer-wins conflict resolution under a Multi-Site Active-Active design; the team should redesign the data model to avoid concurrent writes to the same key where correctness matters (e.g., partitioning updates so each key is normally owned by one region), or add application-level version/timestamp attributes to detect conflicting updates after replication and reconcile them, rather than treating this as an architecture defect.
B. This indicates a misconfiguration; enabling strongly consistent reads across all three regions will eliminate the conflict.
C. The team should switch to Aurora Global Database instead, since it supports true multi-region simultaneous writes without conflicts.
D. This is unrelated to the DR strategy; the fix is to place a Global Accelerator in front of the three regions to serialize writes.
**Correct answer(s):** A
**Why correct:** DynamoDB Global Tables replicate asynchronously and resolve same-key conflicting writes with last-writer-wins; this is an accepted, well-documented trade-off of achieving near-zero RTO/RPO in a Multi-Site Active-Active design, and the correct response is to handle it at the data-model layer (avoid same-key concurrent writes, or detect and reconcile conflicts after the fact using version/timestamp attributes) rather than assume the platform is misconfigured.
**Why each wrong option is wrong:** B is wrong because there is no "strongly consistent read across regions" feature in DynamoDB Global Tables — consistent reads apply only within a single region/table, and cross-region replication remains asynchronous regardless; C is wrong because Aurora Global Database secondary regions are read-only until explicitly promoted, meaning it does not offer true multi-master simultaneous relational writes and would not even satisfy the stated active-active write requirement; D is wrong because Global Accelerator improves network-layer routing and failover performance for TCP/UDP traffic, it has no role in serializing or coordinating application-level database writes.
**Trigger words:** "DynamoDB Global Tables," "simultaneously in all three regions," "near-zero RTO/RPO," "worried one of the two updates might be silently lost."
**Underlying architectural principle:** Multi-Site Active-Active with DynamoDB Global Tables trades strict write consistency for near-zero RTO/RPO via eventual consistency and last-writer-wins conflict resolution, which must be managed in the application/data model, not fixed at the infrastructure layer.

---

### Question 104 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A ride-hailing company's pricing-quote API is built on API Gateway backed by a Java Lambda function. During sharp, predictable morning and evening commute-hour traffic spikes, p99 latency jumps to over 4 seconds because of JVM cold starts on newly initialized execution environments, even though overall average traffic isn't unusually high. The business requires consistently low latency (under 300ms p99) during these commute windows, and the team wants to keep the workload fully serverless with no new infrastructure to manage, and to avoid rewriting the function in a different runtime.
**Options:**
A. Configure Provisioned Concurrency on the function, scheduled (via Application Auto Scaling) to increase ahead of the known commute windows.
B. Increase only the function's memory allocation, leaving all concurrency settings at their defaults.
C. Set Reserved Concurrency equal to the peak expected number of concurrent executions.
D. Migrate the pricing-quote logic to a permanently running ECS Fargate service.
**Correct answer(s):** A
**Why correct:** Provisioned Concurrency pre-initializes execution environments so requests don't pay the cold-start initialization cost, and scheduling it ahead of known commute-hour spikes directly targets the described predictable pattern — this is the standard fix for cold-start-driven p99 latency spikes in a latency-sensitive Lambda workload.
**Why each wrong option is wrong:** B may reduce execution CPU time slightly but does nothing to eliminate the cold-start initialization delay itself, so the p99 spikes would persist; C caps or guarantees a level of concurrency but does not pre-warm execution environments, so cold starts still occur on newly created environments, and setting it too low risks throttling; D would technically eliminate cold starts (an always-on service has none), but Fargate still requires building and operating new infrastructure — a cluster, service definition, task definition, and typically a load balancer — which directly contradicts the stated requirement of "no new infrastructure to manage"; it's a disproportionate re-architecture when a targeted, schedulable Lambda configuration change meets the same latency requirement without adding anything new to operate.
**Trigger words:** "JVM cold starts," "p99 latency," "predictable... commute-hour... spikes," "fully serverless with no new infrastructure to manage," "avoid rewriting the function in a different runtime."
**Underlying architectural principle:** Provisioned Concurrency, ideally scheduled ahead of known traffic patterns, is the direct fix for cold-start latency spikes in latency-sensitive Lambda workloads.

---

### Question 105 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** An inventory-sync Lambda function is triggered by an SQS event source mapping using a batch size of 10 (kept at 10 deliberately, since reducing it would raise per-invocation costs significantly for this high-volume queue). Occasionally 2 of the 10 messages in a batch fail due to a downstream validation error while the other 8 succeed. Today, Lambda treats the whole batch as failed, so all 10 messages return to the queue after the visibility timeout — including the 8 that already succeeded — and those 8 get reprocessed, producing duplicate inventory updates that break downstream idempotency assumptions. The team wants only the genuinely failed messages retried, while keeping the batch size at 10.
**Options:**
A. Enable partial batch response by having the function return `batchItemFailures` identifiers, and configure the event source mapping to use `ReportBatchItemFailures`.
B. Reduce the batch size to 1 so each message is processed and implicitly acknowledged individually.
C. Increase the SQS queue's visibility timeout to six times the function's timeout.
D. Switch the trigger from SQS to SNS, since SNS retries failed message deliveries individually.
**Correct answer(s):** A
**Why correct:** `ReportBatchItemFailures` combined with returning the specific failed message IDs is the native SQS-Lambda mechanism for reprocessing only the messages that actually failed within a batch, leaving successfully processed messages alone — solving the exact duplicate-reprocessing problem described while preserving the required batch size of 10.
**Why each wrong option is wrong:** B would technically prevent partial-batch duplication too, but it directly contradicts the stated requirement to keep batch size at 10 for cost/throughput reasons, so it is not a viable answer here; C only delays when failed messages become visible again for retry, it does nothing to distinguish which of the 10 messages actually failed, so the 8 successful ones would still eventually be redelivered and reprocessed; D changes the trigger's delivery and retry semantics entirely and doesn't provide the same durable, queue-backed redelivery model needed here — it's an unnecessary architecture change that doesn't directly solve the partial-batch-failure problem.
**Trigger words:** "2 of the 10... fail," "entire batch is treated as failed," "want only the genuinely failed messages retried," "keeping the batch size at 10."
**Underlying architectural principle:** `ReportBatchItemFailures` with a partial batch response is the standard SQS-to-Lambda pattern for retrying only failed messages within a batch, avoiding duplicate side effects from messages that already succeeded.

---

### Question 106 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A video transcoding fleet runs as background workers in an Auto Scaling group, polling an SQS queue for jobs — there is no load balancer or target group involved. Each job takes 3–5 minutes to finish and upload results to S3. During scale-in events, the ASG sometimes terminates an instance mid-job, losing the in-progress transcode entirely. The team needs instances to finish their current job and upload results before being terminated.
**Options:**
A. Configure an Auto Scaling lifecycle hook on the `EC2_INSTANCE_TERMINATING` transition that runs a script to complete the job and upload results before the instance is allowed to terminate.
B. Increase the ASG's health check grace period to 5 minutes.
C. Add an ALB target group in front of the workers solely to take advantage of connection draining.
D. Use EC2 Spot Instance hibernation so instances are paused instead of terminated during scale-in.
**Correct answer(s):** A
**Why correct:** A termination lifecycle hook pauses the ASG's termination process for a configurable window, giving a custom script time to finish the in-progress job and upload results before the instance actually terminates — this is precisely what's needed for a worker with no load balancer to rely on for draining.
**Why each wrong option is wrong:** B only affects how long the ASG waits before evaluating health checks after launch, it has no effect on the termination path during scale-in; C introduces a load balancer purely for its draining behavior even though these workers pull jobs from SQS rather than receive inbound connections, so connection draining is irrelevant and provides no guarantee the in-progress job itself finishes; D's hibernation feature is specific to Spot Instance interruption handling (it lets a Spot Instance's in-memory state be suspended to EBS instead of the instance being terminated when Spot capacity is reclaimed) — this scenario never establishes these are Spot Instances, and even where hibernation applies it pauses the in-progress job rather than running any custom logic to finish it and upload results, so it still doesn't satisfy the stated requirement of completing the job and persisting its output before the instance stops.
**Trigger words:** "no load balancer or target group involved," "finish their current job... before being terminated," "loses the in-progress transcode entirely."
**Underlying architectural principle:** Lifecycle hooks let custom code run to gracefully finish work before an ASG instance terminates, independent of any load-balancer-based draining mechanism.

---

### Question 107 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A backend fleet behind an ALB is managed by an Auto Scaling group. Two separate problems are occurring: (1) brief JVM garbage-collection pauses of up to 45 seconds occasionally cause an instance to fail a single health check, and the ASG immediately terminates and replaces an otherwise healthy instance, creating replacement churn and brief 502 errors; (2) newly launched instances take about 90 seconds to fully initialize, but some are being marked unhealthy and replaced within 30 seconds of launch, before initialization finishes. The team wants to reduce both kinds of unnecessary replacement without turning off health-based replacement altogether. (Choose two.)
**Options:**
A. Increase the target group's healthy/unhealthy threshold count so several consecutive failed checks are required before an instance is marked unhealthy.
B. Increase the ASG's health check grace period to at least the application's real initialization time (e.g., 120 seconds).
C. Disable ELB health checks on the ASG and rely solely on EC2 status checks.
D. Change the ASG's termination policy to `ClosestToNextInstanceHour`.
E. Reduce the target group's deregistration delay to 0 seconds so replacements happen faster.
**Correct answer(s):** A, B
**Why correct:** Raising the unhealthy threshold count means a single 45-second GC blip no longer trips replacement, since several consecutive failures would be needed; increasing the grace period past 90 seconds ensures new instances aren't evaluated for health at all until they've actually finished initializing, directly stopping the premature replacements.
**Why each wrong option is wrong:** C would stop both problems but only by removing the ability to detect real application-level failures entirely, which the scenario explicitly says to avoid; D only controls which instance is chosen when the ASG scales in, it has no effect on why instances are being incorrectly flagged unhealthy in the first place; E speeds up how quickly a deregistering target stops receiving new connections, but it does nothing to address why instances are being falsely marked unhealthy, and cutting drain time to zero could increase in-flight request errors during otherwise-correct replacements.
**Trigger words:** "GC pauses of up to 45 seconds," "marked unhealthy and replaced within 30 seconds of launch," "without turning off health-based replacement altogether."
**Underlying architectural principle:** False-positive instance replacements are usually solved by tuning health check thresholds and the grace period to match real application behavior, not by disabling health-based detection.

---

### Question 108 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** An architect is designing a Pilot Light disaster recovery strategy for a relational order-management system, targeting an RPO of about 5 minutes and an RTO of about 45 minutes, on a moderate budget that specifically avoids paying for continuous compute in the DR region. Which two elements belong in this design?
**Options:**
A. A cross-region Aurora/RDS read replica (or equivalent continuous database replication) running in the DR region at all times.
B. Pre-baked AMIs or launch templates plus Infrastructure-as-Code (e.g., CloudFormation) ready to launch the full application/compute tier in the DR region on demand.
C. A fully deployed application tier running at reduced capacity (e.g., 10% of production) continuously in the DR region.
D. Full-capacity production compute running simultaneously in both regions behind Route 53 latency-based routing.
E. Nightly database snapshots copied to the DR region with no continuous replication.
**Correct answer(s):** A, B
**Why correct:** Option A delivers the required ~5 minute RPO through continuous data replication while avoiding continuous compute cost, and option B is what makes the ~45 minute RTO achievable — the application tier is ready to launch from templates on demand rather than being built from scratch, without the cost of running it continuously.
**Why each wrong option is wrong:** C describes Warm Standby, since it keeps the application/compute tier itself running continuously (even at reduced capacity), which directly conflicts with the stated goal of avoiding continuous compute cost; D describes Multi-Site Active-Active, a far more expensive pattern than the moderate budget stated, and delivers a much lower RTO/RPO than what's required here; E describes Backup and Restore, whose RPO (hours, tied to snapshot frequency) is too coarse to meet the stated ~5 minute RPO requirement.
**Trigger words:** "RPO of about 5 minutes," "RTO of about 45 minutes," "moderate budget," "avoids paying for continuous compute."
**Underlying architectural principle:** Pilot Light is defined by continuously replicated data paired with templated, on-demand compute — introducing continuously running compute or relying only on periodic snapshots shifts the design into a different DR category.

---

### Question 109 [Priority: P2] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A Lambda function invoked synchronously via API Gateway writes to a DynamoDB table that intermittently throws `ProvisionedThroughputExceededException` during traffic bursts, causing user-facing request failures. A cost-governance policy prohibits switching the table to on-demand capacity mode. Which two changes will most directly improve resilience to these transient throttling errors?
**Options:**
A. Implement (or rely on the SDK's built-in) exponential backoff with jitter for the DynamoDB calls, so transient throttles are retried instead of immediately failing the user's request.
B. Enable auto scaling on the table's provisioned read/write capacity so throughput ceilings rise automatically during bursts, while remaining in provisioned mode.
C. Increase the Lambda function's memory allocation to reduce execution duration.
D. Set the function's reserved concurrency to a very low fixed number to intentionally limit request volume reaching DynamoDB.
E. Move the Lambda function into a VPC and add a NAT Gateway route toward DynamoDB.
**Correct answer(s):** A, B
**Why correct:** Backoff-with-jitter (A) absorbs short throttling bursts at the call level instead of surfacing them to the user immediately, and DynamoDB auto scaling within provisioned mode (B) raises capacity ceilings ahead of sustained bursts — reducing how often throttling happens at all — while still satisfying the cost-governance requirement to stay in provisioned capacity mode.
**Why each wrong option is wrong:** C speeds up CPU-bound execution but has no effect on DynamoDB's own throughput limits or throttling behavior; D reduces load on DynamoDB only by rejecting legitimate user requests outright at the Lambda layer, which makes the user-facing failure problem worse, not better; E is irrelevant because DynamoDB is reachable over its standard public AWS API endpoint (or a Gateway VPC endpoint) — moving the function into a VPC with a NAT Gateway addresses network path/connectivity concerns that don't exist here and has no bearing on throttling.
**Trigger words:** "ProvisionedThroughputExceededException," "cost-governance policy prohibits switching... to on-demand," "most directly improve resilience."
**Underlying architectural principle:** Resilience to a downstream service's transient capacity limits comes from combining client-side retry/backoff with proactively scaling the downstream capacity itself, not from throttling your own front door or optimizing unrelated resources.

---

### Question 110 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company must roll out a new AMI to all 20 instances in a production Auto Scaling group behind an ALB. The rollout must never drop available capacity below 90%, must not require manually replacing instances one at a time, and must automatically roll back if the new instances start failing health checks.
**Options:**
A. Start an Auto Scaling group Instance Refresh, specifying a minimum healthy percentage of 90% and the new launch template version, letting the ASG use existing ALB health checks to detect failures and drive rollback.
B. Manually terminate instances one at a time so the ASG replaces each with an instance using the updated launch template's default version.
C. Create a second Auto Scaling group using the new AMI and manually shift Route 53 weighted routing once it's verified healthy.
D. Update the launch template to reference the new AMI and take no further action, since the ASG will eventually replace running instances on its own.
**Correct answer(s):** A
**Why correct:** Instance Refresh natively performs a rolling replacement of every instance in the ASG according to a specified minimum healthy percentage, and it automatically monitors health checks during the rollout, rolling back if instances fail — meeting every stated constraint without manual orchestration.
**Why each wrong option is wrong:** B is explicitly excluded by "must not require manually replacing instances one at a time," and it provides no automatic rollback if the new AMI turns out to be unhealthy; C is a valid blue/green pattern in general, but as described it depends on a human manually verifying the new ASG's health before shifting Route 53 weights — it doesn't automatically roll back based on health check failures the way the requirement demands, and it also doubles running infrastructure temporarily, adding operational overhead that Instance Refresh avoids natively; D is wrong because updating the launch template only affects instances launched in the future — it does not trigger any replacement of the 20 instances already running.
**Trigger words:** "roll out a new AMI to all 20 instances," "never drop available capacity below 90%," "must not require manually replacing instances," "automatically roll back."
**Underlying architectural principle:** ASG Instance Refresh with a minimum healthy percentage natively performs a rolling, capacity-aware rollout of a new launch template version with automatic health-check-driven rollback.

---

### Question 111 [Priority: P3] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A high-frequency trading firm maintains an Aurora Global Database secondary in a DR region with sub-1-minute replication lag. It also keeps a fleet of fully pre-configured EC2 instances for its trading application in a **stopped** (not terminated) state in that same DR region, so they can be started rather than launched fresh from an AMI during failover, meaningfully cutting boot time. Under normal conditions, none of these stopped instances are attached to a load balancer, none receive health checks, and no traffic is served from the DR region. The stated RTO target is under 10 minutes.
**Options:**
A. Pilot Light — the compute tier is not running or serving traffic under normal conditions; pre-configuring instances in a stopped state is simply an optimization to reduce the time needed to "ignite" the fleet, and it does not change the classification.
B. Warm Standby — because the instances already exist and are pre-provisioned in the DR region, the compute tier counts as "running" for classification purposes.
C. Backup and Restore — because the compute tier requires an explicit start action before it can be used.
D. Multi-Site Active-Active — because Aurora Global Database is technically capable of serving reads from the secondary region at any time.
**Correct answer(s):** A
**Why correct:** The classification test for Pilot Light versus Warm Standby is whether compute is actively running and capable of serving traffic, not merely whether it has been provisioned — a stopped EC2 instance consumes no compute cycles, serves no traffic, and receives no health checks, so this remains Pilot Light, just an optimized variant with a faster "ignition" step than building instances from scratch.
**Why each wrong option is wrong:** B conflates "pre-provisioned" with "running" — a stopped instance is not functioning or serving anything, so it does not meet Warm Standby's requirement of a live (even if downsized) application tier; C is wrong because Backup and Restore typically has no pre-existing configured instances at all (just backups) and a much slower typical RTO measured in hours, while this design has continuous DB replication and a sub-10-minute RTO, well beyond what plain Backup and Restore provides; D is wrong because the mere technical capability of Aurora Global Database to serve reads doesn't make this active-active — no traffic is actually being served from the DR region under normal conditions, which is the defining trait of Multi-Site Active-Active.
**Trigger words:** "kept in a stopped (not terminated) state," "started rather than launched fresh from an AMI," "no traffic is served from the DR region under normal conditions," "none... attached to a load balancer, none receive health checks."
**Underlying architectural principle:** DR strategy classification depends on whether compute is actively running and serving production traffic, not merely whether it has been pre-provisioned — pre-staging stopped resources is a valid Pilot Light optimization, not a promotion to Warm Standby.

---

### Question 112 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A Lambda function processes messages from an SQS queue and calls an internal microservice on EC2 inside a private VPC subnet, so the function itself is VPC-attached to reach that private endpoint. A recent deployment introduced a bug that causes every message currently in the queue to fail deterministically ("poison pill" messages). Because the SQS visibility timeout keeps returning failed messages to the queue for retry, the function is now continuously reprocessing the same failing messages at high concurrency, consuming most of the account's regional concurrency limit and starving other, unrelated Lambda functions of execution capacity.
**Options:**
A. Configure reserved concurrency on this specific function to cap its maximum concurrent executions, and configure a redrive policy (`maxReceiveCount`) on the source SQS queue pointing to a dead-letter queue so poison-pill messages stop being retried indefinitely.
B. Remove the function from the VPC so it can scale without ENI-related limits.
C. Increase the SQS visibility timeout to 12 hours to slow down the retry rate.
D. Increase the function's memory allocation so it processes messages faster and clears the backlog sooner.
**Correct answer(s):** A
**Why correct:** Reserved concurrency caps how much of the shared account-level concurrency pool this one misbehaving function can consume, protecting other functions, while a `maxReceiveCount`-based redrive policy to a DLQ is what actually stops a deterministically failing message from being retried forever — together they isolate the blast radius and resolve the poison-pill problem.
**Why each wrong option is wrong:** B is wrong because modern Lambda VPC networking (Hyperplane ENIs) doesn't impose the old per-invoke ENI throttle that would explain this behavior, and the function needs the VPC to reach the internal microservice — removing it would break required connectivity without addressing the actual concurrency-starvation or poison-pill issue; C slows how often each individual message becomes visible again for retry, but it does nothing to stop those same deterministically-failing messages from eventually being redelivered and consumed indefinitely, nor does it protect other functions' concurrency; D is wrong because the messages fail deterministically regardless of processing speed, so faster execution just retries the same failure faster and doesn't address the missing redrive policy or the account-wide concurrency starvation.
**Trigger words:** "fails deterministically," "poison pill," "continuously reprocessing the same failing messages," "starving other, unrelated Lambda functions of execution capacity."
**Underlying architectural principle:** Reserved concurrency isolates one misbehaving function's blast radius from the shared account concurrency pool, while a dead-letter/redrive policy on the source queue is what actually stops a poison-pill message from being retried forever.

---

## Domain 3: Design High-Performing Architectures (24%)

### Question 113 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media company runs a fleet of EC2 instances that perform batch video transcoding. The workload is entirely CPU-bound (no significant memory or disk I/O pressure), runs 24/7 at sustained high CPU utilization, and the company is highly cost-sensitive because transcoding is billed internally per compute-hour. They want the best price-performance for sustained CPU-bound work and are open to any CPU architecture. Which instance choice should they select?

**Options:**
A. C7g (Graviton3, compute-optimized)
B. M6i (general purpose, x86)
C. R6i (memory-optimized, x86)
D. T3.unlimited (burstable, x86)

**Correct answer(s):** A

**Why correct:** C7g is a compute-optimized family built on AWS Graviton3, which AWS documents as delivering the best price-performance for sustained, CPU-bound workloads like transcoding, batch processing, and HPC compared to equivalent x86 compute-optimized instances.

**Why each wrong option is wrong:** B is a general-purpose family with a balanced (not CPU-heavy) vCPU-to-memory ratio, so you pay for memory capacity you don't need; C is memory-optimized and wastes spend on RAM the workload doesn't use; D's burstable CPU credit model is designed for workloads with variable, intermittent CPU spikes around a lower performance baseline. In "unlimited" mode, T3 won't throttle at the baseline the way standard mode does — instead it lets the instance sustain high CPU beyond its credit balance by charging an additional per-vCPU-hour surcharge for that surplus usage. For a workload running at sustained high CPU 24/7, that surcharge accumulates continuously and makes T3.unlimited more expensive than simply right-sizing to a compute-optimized family — the opposite of the stated cost-sensitivity goal.

**Trigger words:** "entirely CPU-bound," "sustained high CPU utilization," "cost-sensitive," "best price-performance."

**Underlying architectural principle:** Match the EC2 instance family's resource ratio to the workload's actual bottleneck resource, and prefer Graviton compute-optimized instances for sustained CPU-bound workloads when architecture flexibility exists.

---

### Question 114 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A financial services firm runs a tightly-coupled MPI-based risk simulation across 20 EC2 instances. The simulation involves constant inter-node communication with strict requirements for low network latency and high throughput between nodes, all of which must reside in the same Availability Zone. The firm has no requirement for the instances to survive a single rack-level hardware failure — if the whole simulation needs to be rerun, that is acceptable. What should the architect configure to meet the networking requirement?

**Options:**
A. Cluster placement group
B. Spread placement group
C. Partition placement group
D. Distribute the instances across three Availability Zones with a Network Load Balancer

**Correct answer(s):** A

**Why correct:** A cluster placement group packs instances close together inside a single AZ on the same low-latency, high-throughput network fabric, which is exactly what tightly coupled HPC/MPI workloads need, and the scenario explicitly says correlated-failure risk is acceptable.

**Why each wrong option is wrong:** B (spread) prioritizes fault isolation across distinct hardware for a small number of critical instances, which increases inter-instance latency — the opposite of this requirement; C (partition) is designed for distributed data systems that need rack-level fault isolation (e.g., Kafka, HDFS), not lowest possible latency; D introduces cross-AZ network hops that add latency, directly working against the tightly-coupled communication requirement.

**Trigger words:** "tightly-coupled MPI," "constant inter-node communication," "low network latency and high throughput," "acceptable" to lose the whole job on failure.

**Underlying architectural principle:** Cluster placement groups optimize for network performance within a single AZ at the cost of fault isolation — use them only when the workload's failure-domain tolerance matches that trade-off.

---

### Question 115 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs 5 domain controller instances that are critical to authentication for the entire organization. They want to minimize the chance that a single underlying hardware, power, or network failure could take down more than one domain controller at a time. Instance-to-instance latency is not a concern for this use case. Which placement strategy best fits this requirement?

**Options:**
A. Cluster placement group
B. Spread placement group
C. Partition placement group
D. No placement group, single subnet

**Correct answer(s):** B

**Why correct:** A spread placement group places each instance on distinct underlying hardware, with separate racks, power sources, and network paths, which is exactly designed for a small number (max 7 per AZ) of critical instances that must not share a failure domain.

**Why each wrong option is wrong:** A (cluster) intentionally colocates instances for low latency, which increases — not decreases — correlated failure risk; C (partition) is intended for large distributed systems needing rack-awareness across many instances, not a small handful of independent critical instances; D provides no hardware isolation guarantee at all, since EC2 could still place instances on the same physical host.

**Trigger words:** "critical," "minimize the chance that a single... failure could take down more than one," "latency... is not a concern."

**Underlying architectural principle:** Use spread placement groups when the priority is maximizing fault isolation for a small set of critical instances, not networking performance.

---

### Question 116 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A retailer runs an in-memory analytics database (similar to SAP HANA) that requires an extremely high memory-to-vCPU ratio. The database software is licensed per vCPU, so the company wants to minimize the number of vCPUs provisioned while still obtaining the maximum memory capacity per instance, in order to control both infrastructure and software licensing costs. Which EC2 family should they choose?

**Options:**
A. R6i (memory-optimized, ~8 GiB memory per vCPU)
B. X2iedn (memory-optimized, ~32 GiB memory per vCPU)
C. M6i (general purpose, ~4 GiB memory per vCPU)
D. C6i (compute-optimized, ~2 GiB memory per vCPU)

**Correct answer(s):** B

**Why correct:** X2iedn offers one of the highest memory-to-vCPU ratios available in standard EC2 families (roughly 4x that of R6i), which directly minimizes the number of licensed vCPUs required to reach a given memory footprint — the exact cost lever the scenario calls out.

**Why each wrong option is wrong:** A (R6i) is memory-optimized but has only about a quarter of the memory-per-vCPU ratio of X2iedn, requiring more vCPUs (and more license cost) to reach the same memory capacity; C (M6i) has a balanced ratio unsuited to memory-dominant, licensing-sensitive workloads; D (C6i) is compute-optimized with the lowest memory ratio of the options, the opposite of what's needed.

**Trigger words:** "extremely high memory-to-vCPU ratio," "licensed per vCPU," "minimize the number of vCPUs... while... maximum memory."

**Underlying architectural principle:** When software licensing is billed per vCPU, the memory-to-vCPU ratio of the instance family becomes a direct cost optimization lever, not just a performance one.

---

### Question 117 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A gaming company runs a latency-sensitive NoSQL database cluster that requires millions of IOPS and sub-millisecond storage latency. The database software already replicates data synchronously across multiple nodes at the application layer, so durability of any single node's local disk is not a concern if that node fails — the cluster self-heals. The team wants the lowest possible storage latency at the lowest cost. Which storage approach should they choose?

**Options:**
A. EBS io2 Block Express volumes attached to R6i instances
B. gp3 volumes attached to M6i instances
C. Local NVMe instance store on I4i or I3en instances
D. EBS-optimized gp2 volumes with maximum provisioned IOPS

**Correct answer(s):** C

**Why correct:** Instance store on I-family instances is physically attached NVMe SSD, avoiding the network hop inherent to any EBS volume, giving the lowest possible latency and highest IOPS ceiling — and since the scenario states the application already handles cross-node durability, instance store's lack of persistence beyond instance lifetime is an acceptable trade-off for the performance gain.

**Why each wrong option is wrong:** A (io2 Block Express) is EBS's highest-performance tier but is still network-attached storage, adding latency instance store avoids, and adds unnecessary cost for a workload that doesn't need durable block storage; B (gp3) has a fixed baseline IOPS/throughput ceiling far below what "millions of IOPS" requires; D (gp2) has an even lower IOPS ceiling than gp3 and ties IOPS to volume size, making it the least suitable choice.

**Trigger words:** "millions of IOPS," "sub-millisecond storage latency," "already replicates data... durability... is not a concern," "lowest possible storage latency at the lowest cost."

**Underlying architectural principle:** When an application already provides its own data durability/replication, local NVMe instance store can deliver higher performance at lower cost than any EBS tier by eliminating the network-attached storage hop.

---

### Question 118 [Priority: P2] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A data engineering team is deploying a large Kafka cluster and wants to use a partition placement group to achieve rack-level fault isolation, so that a single rack failure only affects instances in one partition. Before implementing this, they want to confirm their understanding of how partition placement groups behave. Which two statements are correct?

**Options:**
A. Instances in different partitions of the same placement group do not share underlying racks, power, or networking, reducing the chance of a correlated multi-partition failure.
B. Each instance can query the EC2 instance metadata service to determine which partition it belongs to, allowing Kafka to make rack-aware placement decisions in its own logic.
C. A single partition placement group supports a maximum of 7 partitions total per AWS Region.
D. Partition placement groups provide the same ultra-low-latency, high-throughput networking guarantees between all instances as cluster placement groups.
E. Partition placement groups can only be used within a single Availability Zone and cannot span multiple AZs.

**Correct answer(s):** A, B

**Why correct:** Partitions within a partition placement group are isolated onto distinct hardware racks with separate power/network to contain failures (A), and AWS exposes each instance's partition number via instance metadata specifically so distributed applications like Kafka/HDFS/Cassandra can build rack-aware replica placement logic (B).

**Why each wrong option is wrong:** C is wrong because the 7-partition limit applies per Availability Zone, not per Region as a whole; D is wrong because partition placement groups optimize for fault isolation, not the tight network-latency guarantees that cluster placement groups provide; E is wrong because a partition placement group can span multiple Availability Zones within a Region, with each AZ containing its own set of up to 7 partitions.

**Trigger words:** "rack-level fault isolation," "single rack failure only affects instances in one partition," "confirm their understanding."

**Underlying architectural principle:** Partition placement groups exist to give large, self-replicating distributed systems rack-awareness and blast-radius containment, not the low-latency networking benefits of cluster placement groups.

---

### Question 119 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A platform team is containerizing a new application and already has significant existing investment in Kubernetes tooling — Helm charts, kubectl-based CI/CD pipelines, and custom Kubernetes operators — from workloads running on-premises and in another cloud provider. Leadership wants the new AWS-hosted workload to remain portable and manageable with the same standard Kubernetes API and tooling the team already uses. Which AWS container orchestration service should they choose?

**Options:**
A. Amazon ECS with the EC2 launch type
B. Amazon EKS
C. AWS Fargate for ECS
D. AWS Lambda with container image support

**Correct answer(s):** B

**Why correct:** Amazon EKS is a managed Kubernetes control plane that exposes the standard, upstream Kubernetes API, so the team's existing Helm charts, kubectl workflows, and operators work with minimal changes, directly satisfying the portability requirement.

**Why each wrong option is wrong:** A (ECS) uses AWS's own proprietary orchestration API and task definition model, not Kubernetes, so existing Kubernetes tooling would need to be rebuilt; C (Fargate for ECS) is a compute launch type for ECS, not a Kubernetes-compatible orchestrator, so it has the same portability gap as A; D (Lambda) is an event-driven serverless compute service with no relationship to Kubernetes tooling or the container orchestration model described.

**Trigger words:** "existing investment in Kubernetes tooling," "Helm charts, kubectl-based CI/CD," "standard Kubernetes API."

**Underlying architectural principle:** Choose EKS over ECS specifically when Kubernetes API compatibility and tooling portability across environments is a stated requirement, not just "run containers on AWS."

---

### Question 120 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A startup runs an ECS-based API service with highly variable, unpredictable traffic that can spike 10x within minutes and drop back down just as quickly. The team is small, has no dedicated infrastructure engineer, and explicitly wants to avoid managing EC2 capacity, AMI patching, or cluster bin-packing decisions. They are willing to accept a moderate per-vCPU/memory cost premium in exchange for eliminating that operational burden and getting fast, granular scaling. Which ECS launch type best fits this requirement?

**Options:**
A. ECS with the EC2 launch type and a Cluster Auto Scaling group
B. AWS Fargate launch type for ECS
C. ECS with EC2 Spot Instances and manual capacity provider configuration
D. ECS with EC2 launch type sized using Reserved Instances for steady-state capacity

**Correct answer(s):** B

**Why correct:** Fargate removes server/AMI/capacity management entirely, bills per-second per task, and scales tasks independently of any underlying instance capacity, which directly matches the team's stated priorities of no operational burden and fast, granular scaling for unpredictable traffic — even at a per-unit cost premium they've explicitly accepted.

**Why each wrong option is wrong:** A requires the team to manage an Auto Scaling group, instance types, and bin-packing decisions, and EC2 launch time adds latency to scale-out compared to Fargate, contradicting the "avoid managing EC2 capacity" requirement; C adds Spot interruption risk and manual capacity provider tuning, which conflicts with a small team wanting low operational burden for unpredictable, bursty traffic; D relies on pre-committed steady-state capacity, which is a poor fit for a workload described as highly variable and unpredictable, since reserved capacity sits idle or falls short depending on the spike.

**Trigger words:** "highly variable, unpredictable traffic," "no dedicated infrastructure engineer," "avoid managing EC2 capacity," "willing to accept a moderate... cost premium."

**Underlying architectural principle:** Fargate trades a per-unit cost premium for eliminating capacity management and enabling faster, more granular scaling — the right choice when operational simplicity is explicitly prioritized over maximum cost efficiency.

---

### Question 121 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company runs an ECS worker service (no load balancer involved) that pulls jobs from an SQS queue and processes them. The team observes that CPU and memory utilization stay low even when the queue backs up significantly, because each task spends most of its time waiting on a slow downstream API rather than consuming compute resources. As a result, scaling based on CPU or memory utilization does not keep the queue drained during bursts. What should the architect configure to scale the ECS service appropriately?

**Options:**
A. Target tracking scaling policy based on average CPU utilization
B. Target tracking scaling policy based on a custom CloudWatch metric for SQS ApproximateNumberOfMessagesVisible
C. Scheduled scaling that adds tasks every day during known peak business hours
D. Step scaling based on Application Load Balancer request count per target

**Correct answer(s):** B

**Why correct:** Application Auto Scaling supports target tracking on custom CloudWatch metrics, and tying scaling directly to SQS queue depth (messages visible per task, or a similar backlog-based custom metric) scales the service based on actual work waiting to be processed, which is the true bottleneck signal in this scenario.

**Why each wrong option is wrong:** A is explicitly ruled out by the scenario, since CPU/memory stay low regardless of queue depth due to I/O wait time; C reacts to a fixed schedule rather than actual demand, so it won't respond to unpredictable bursts outside those hours; D requires an Application Load Balancer, but this is a queue-worker pattern with no ALB in the request path, so that metric doesn't exist for this service.

**Trigger words:** "pulls jobs from an SQS queue," "CPU and memory utilization stay low even when the queue backs up," "does not keep the queue drained."

**Underlying architectural principle:** Scale on the metric that actually reflects the workload's real bottleneck (e.g., queue backlog for I/O-bound worker patterns), not a generic resource metric that may be decoupled from true demand.

---

### Question 122 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A machine learning platform team runs EKS with highly heterogeneous workloads — some pods need GPU instances, some need memory-optimized instances, and some need standard compute, all with unpredictable and fast-changing scheduling requirements. The team wants new nodes to be provisioned as quickly as possible after pods become unschedulable, with the scheduler automatically selecting the most cost-efficient instance type and size that fits pending pod requirements, without the team having to pre-create and maintain a separate Auto Scaling group for every instance type/AZ combination. Which node-scaling approach best fits this requirement?

**Options:**
A. Kubernetes Cluster Autoscaler with one Auto Scaling group per instance type
B. Karpenter
C. Horizontal Pod Autoscaler (HPA) only
D. Run all workloads on EKS Fargate profiles exclusively

**Correct answer(s):** B

**Why correct:** Karpenter provisions nodes directly against the EC2 fleet API based on aggregate pending-pod resource requirements, dynamically selecting from a broad, flexible set of instance types/sizes without requiring pre-defined Auto Scaling groups per type, which provides faster, more cost-efficient scale-out than the ASG-per-instance-type model — exactly what the heterogeneous, fast-changing workload needs.

**Why each wrong option is wrong:** A works but requires the team to pre-create and maintain a separate ASG for every instance type/AZ combination they might need, adding exactly the operational overhead the scenario says they want to avoid, and its scale-out decisions are slower since they're mediated through ASG scaling first; C (HPA) scales the number of pod replicas, not the number of underlying nodes, so it doesn't solve the "pods become unschedulable due to no node capacity" problem; D (Fargate profiles only) removes the ability to select GPU or memory-optimized instance types for specialized ML workloads, since Fargate abstracts away instance type selection entirely.

**Trigger words:** "highly heterogeneous workloads," "as quickly as possible," "automatically selecting the most cost-efficient instance type," "without... a separate Auto Scaling group for every instance type/AZ combination."

**Underlying architectural principle:** Karpenter's direct-to-EC2-API, group-less provisioning model outperforms Cluster Autoscaler's ASG-based model specifically when workloads need fast, flexible, heterogeneous instance selection.

---

### Question 123 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A team runs a bursty ECS batch-processing service on EC2 launch type. They want to minimize the number of active EC2 instances in the cluster (to reduce cost) by packing tasks as densely as possible onto existing instances, while also ensuring tasks are still distributed across Availability Zones so a single AZ failure doesn't take down the whole batch run. Which two ECS task placement strategies should they configure together to meet both goals?

**Options:**
A. binpack, using the memory field, so ECS fills the most heavily-utilized instances first before starting new ones
B. random, so tasks are placed on any available instance with no evaluation of current utilization
C. spread, using the attribute:ecs.availability-zone attribute, so tasks are distributed evenly across AZs
D. spread, using the instanceId attribute, so no two tasks ever run on the same instance
E. binpack, using the cpu field exclusively, with no other strategy configured, to guarantee AZ balance as a side effect

**Correct answer(s):** A, C

**Why correct:** binpack (A) maximizes density on existing instances, directly minimizing the number of active EC2 instances needed and thus cost, while spread by Availability Zone (C) ensures the resulting tasks are still distributed across AZs for fault tolerance — ECS supports combining multiple placement strategies in a single service, so these complement rather than conflict with each other.

**Why each wrong option is wrong:** B (random) makes no attempt to maximize density, so it won't minimize the number of active instances; D (spread by instanceId) forces at most one task per instance, which is the opposite of density packing and directly increases the instance count needed; E (binpack alone) only affects density within instances and has no logic for AZ distribution, so it cannot "guarantee" AZ balance as claimed.

**Trigger words:** "minimize the number of active EC2 instances," "pack... as densely as possible," "still ensure tasks are... distributed across Availability Zones."

**Underlying architectural principle:** ECS placement strategies can be combined (e.g., binpack + AZ spread) to simultaneously optimize for cost density and fault-tolerant distribution, rather than treating cost and availability as mutually exclusive goals.

---

### Question 124 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A company exposes a synchronous customer-facing API through API Gateway backed by a Lambda function written in Java, which has a known cold-start penalty from JVM initialization. The API has a strict p99 latency SLA of under 100ms, and traffic arrives in sporadic bursts throughout the day rather than a smooth, constant rate, meaning new execution environments are frequently created. Increasing memory allocation alone has not been sufficient to meet the SLA during these bursts. What should the team configure to most directly address this?

**Options:**
A. Reserved concurrency set equal to expected peak traffic
B. Provisioned concurrency
C. A scheduled CloudWatch Events rule that invokes the function every 5 minutes to keep it "warm"
D. Deploy the function as Lambda@Edge instead

**Correct answer(s):** B

**Why correct:** Provisioned concurrency keeps a specified number of execution environments pre-initialized and warm at all times, so bursts of traffic are served by already-initialized environments instead of triggering new cold starts, directly targeting the JVM initialization latency causing the SLA violations.

**Why each wrong option is wrong:** A (reserved concurrency) only sets a maximum/guaranteed concurrency pool for the function — it does not pre-initialize environments or reduce cold start latency at all; C (scheduled warm-up pings) is a legacy workaround that only keeps one or a few environments warm regardless of actual concurrent burst size, and is unreliable and superseded by provisioned concurrency; D (Lambda@Edge) is designed for running logic at CloudFront edge locations for request/response manipulation, not for solving general cold-start latency, and actually has additional constraints that can increase cold start exposure across more edge locations.

**Trigger words:** "known cold-start penalty," "strict p99 latency SLA," "sporadic bursts... new execution environments are frequently created," "increasing memory alone has not been sufficient."

**Underlying architectural principle:** Provisioned concurrency, not reserved concurrency or memory tuning alone, is the specific lever for eliminating cold-start latency for bursty, latency-sensitive synchronous Lambda workloads.

---

### Question 125 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A team has a Lambda function that performs CPU-intensive image resizing. Profiling shows the function is consistently CPU-bound (high CPU utilization for the full invocation duration) but does not use much of its allocated memory. The function's duration — and therefore its cost, since Lambda bills by GB-seconds — is higher than the team would like. They understand that AWS Lambda allocates vCPU power proportionally to the memory configured for a function. What should they do to reduce the function's execution duration?

**Options:**
A. Increase the function's reserved concurrency
B. Increase the function's memory allocation, even though it doesn't need the additional RAM
C. Increase the function's timeout setting
D. Enable AWS X-Ray active tracing on the function

**Correct answer(s):** B

**Why correct:** Because Lambda allocates vCPU power (and network bandwidth) in linear proportion to the memory configured, increasing memory for a CPU-bound function gives it more compute power even if it doesn't need the extra RAM, which reduces execution duration and can lower or hold cost steady despite the higher GB-seconds rate.

**Why each wrong option is wrong:** A (reserved concurrency) only controls how many concurrent executions are guaranteed/allowed for the function — it has no effect on the compute power available to any single invocation; C (timeout) only changes the maximum allowed duration before Lambda terminates the invocation, it does not make the function execute any faster; D (X-Ray tracing) adds observability instrumentation and, if anything, adds a small overhead — it does nothing to increase compute capacity.

**Trigger words:** "consistently CPU-bound," "does not use much of its allocated memory," "vCPU power proportionally to the memory configured," "reduce the function's execution duration."

**Underlying architectural principle:** Lambda memory configuration is really a compute-power dial, not just a RAM dial — for CPU-bound functions, over-provisioning memory relative to RAM needs can be a legitimate performance optimization.

---

### Question 126 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company runs 50 Lambda functions in a single AWS account and Region. During a traffic spike, a non-critical internal reporting function's invocation rate surged and consumed most of the account's available concurrent execution capacity, causing a separate, business-critical checkout function (sharing the same account/Region) to be throttled with 429 errors. The team needs to guarantee, going forward, that the checkout function always has execution capacity available regardless of what any other function in the account is doing — using a Lambda configuration change rather than submitting a AWS Support service quota increase request or re-architecting the invocation pattern. What should they configure?

**Options:**
A. Provisioned concurrency on the checkout function
B. Reserved concurrency on the checkout function
C. Request an account-level concurrency limit increase via AWS Support
D. Deploy the reporting function behind an SQS queue with a small Lambda batch size

**Correct answer(s):** B

**Why correct:** Reserved concurrency carves out a portion of the account's total concurrency pool exclusively for the checkout function, guaranteeing it always has that capacity available and cannot be starved by other functions in the account, regardless of how much concurrency those other functions consume — this is precisely the isolation mechanism AWS Lambda provides for this exact scenario.

**Why each wrong option is wrong:** A (provisioned concurrency) reduces cold starts and pre-warms environments, but by itself does not reserve capacity or prevent account-level throttling — it must be paired with reserved concurrency to guarantee availability, so on its own it doesn't solve the stated problem; C (requesting a quota increase) only raises the total shared pool size, it doesn't guarantee checkout's isolation from future spikes by other functions and requires a manual, non-automatic process each time; D would reduce the reporting function's burst invocation rate but doesn't directly guarantee capacity for checkout, and the scenario explicitly asks for a configuration fix rather than an invocation-pattern re-architecture.

**Trigger words:** "consumed most of the account's available concurrent execution capacity," "guarantee... always has execution capacity available regardless of what any other function... is doing," "configuration change rather than... re-architecting."

**Underlying architectural principle:** Reserved concurrency is the mechanism for guaranteeing per-function concurrency isolation within a shared account-level Lambda concurrency pool; provisioned concurrency solves a different problem (cold starts) and does not by itself provide that guarantee.

---

### Question 127 [Priority: P1] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A team runs a Java 21 Lambda function behind API Gateway with a strict p99 latency SLA. Cold starts spike noticeably right after deployments and during predictable low-traffic overnight hours (2am–5am local time), causing SLA violations during those windows specifically. The team is cost-sensitive and explicitly does not want to pay for standing warm capacity running at full scale 24/7, since traffic during the day is high enough that environments stay naturally warm. They are open to combining more than one technique. Select the two most effective techniques for this specific scenario.

**Options:**
A. Enable Lambda SnapStart, which restores execution environments from a pre-initialized, cached snapshot rather than re-running the full JVM startup and function initialization code on every cold start
B. Configure a scheduled Application Auto Scaling action that increases the function's provisioned concurrency shortly before the predictable overnight low-traffic window begins, and scales it back down once daytime traffic resumes
C. Increase the function's reserved concurrency limit, since a higher concurrency ceiling reduces the frequency of cold starts
D. Reduce the deployment package size and trim unused imports/classes loaded during Java static initialization
E. Switch the function's instruction set architecture from arm64 to x86_64, since AWS documentation states this reduces Java cold start latency

**Correct answer(s):** A, D

**Why correct:** SnapStart (A) is purpose-built for JVM-based runtimes and directly attacks the largest source of Java cold-start latency by caching a fully initialized, ready-to-resume snapshot instead of repeating JVM startup and static initialization work on every cold start — and because it only adds a small snapshot-cache cost rather than requiring any standing pre-warmed capacity, it fits the team's cost-sensitivity without needing a 24/7 or scheduled spend commitment. Trimming the deployment package and unused static-initialization work (D) is AWS's own documented complementary best practice on top of SnapStart: less code to execute during the (already-fast) snapshot restore further shrinks the residual cold-start time, at no ongoing cost.

**Why each wrong option is wrong:** B looks plausible in isolation, but AWS Lambda does not allow SnapStart and Provisioned Concurrency to be enabled on the same function version at the same time — so it cannot be layered on top of the SnapStart fix in A. Even evaluated as a stand-alone alternative to SnapStart, scheduled provisioned concurrency still requires paying for reserved warm capacity during the whole scheduled window, which is a less cost-optimal fit for this scenario than SnapStart's pay-only-for-what-you-use snapshot-restore model; C is a common misconception — reserved concurrency only sets a maximum/guaranteed concurrency ceiling and has no effect on cold start frequency or latency; E is a fabricated claim — AWS does not document a general architecture-based cold-start advantage of x86_64 over arm64 for Java, and Graviton (arm64) Lambda functions are generally equal or better on price-performance.

**Trigger words:** "cold starts spike... during predictable low-traffic overnight hours," "cost-sensitive," "does not want to pay for standing warm capacity... 24/7," "open to combining more than one technique."

**Underlying architectural principle:** For JVM-based Lambda functions, SnapStart is generally the most cost-effective cold-start mitigation because it eliminates the need for standing warm capacity; since it cannot be combined with provisioned concurrency on the same function version, pair it instead with free, complementary optimizations like trimming static initialization and package size rather than layering on a second, cost-incurring capacity mechanism.

---

### Question 128 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A research institution runs a tightly-coupled, GPU-based distributed ML training job (using NCCL/MPI-style collective communication) across multiple EC2 instances within a single Availability Zone, using instance types that support Elastic Fabric Adapter (EFA). The job is currently deployed in a cluster placement group with standard Elastic Network Adapter (ENA) networking, but the team is still seeing inter-node collective communication latency and kernel-level networking overhead that is bottlenecking training throughput below expectations, even though standard enhanced networking (ENA) is already enabled. What additional configuration should the architect apply to reduce this specific bottleneck?

**Options:**
A. Enable Elastic Fabric Adapter (EFA) on the instances within the existing cluster placement group
B. Move to a spread placement group to reduce hardware contention between nodes
C. Increase the instance size (more vCPUs) without changing the networking configuration
D. Distribute the training job across three Availability Zones behind a Transit Gateway for higher aggregate bandwidth

**Correct answer(s):** A

**Why correct:** EFA provides an OS-bypass hardware interface (via libfabric, used by NCCL/MPI) that lets application-level collective communication traffic skip the kernel's standard networking stack entirely, eliminating exactly the kernel-level overhead and inter-node latency described — this is the specific problem EFA is designed to solve on top of standard ENA networking. EFA doesn't strictly require a cluster placement group, but AWS recommends pairing it with one for the lowest possible latency between instances, which the team already has in place.

**Why each wrong option is wrong:** B (spread placement group) would increase inter-node network latency by placing instances further apart on distinct hardware, directly working against the tightly-coupled communication requirement; C (bigger instances only) adds more compute per node but does nothing to address the network-stack-level bottleneck described, since the issue is networking overhead, not raw vCPU count; D actively worsens latency by introducing cross-AZ hops through a Transit Gateway for a workload that requires the lowest possible inter-node latency.

**Trigger words:** "tightly-coupled, GPU-based distributed ML training," "NCCL/MPI-style collective communication," "kernel-level networking overhead," "even though standard enhanced networking (ENA) is already enabled."

**Underlying architectural principle:** For the most demanding tightly-coupled HPC/ML workloads, standard ENA enhanced networking may not be sufficient — Elastic Fabric Adapter provides OS-bypass networking specifically to eliminate kernel overhead for MPI/NCCL-style collective communication, best paired with (though not strictly requiring) a cluster placement group.

---

### Question 129 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A media analytics company allows customers to upload raw video files ranging from 2 GB to 40 GB directly into an S3 bucket from their office network. Several customers report that uploads of the larger files frequently fail partway through, forcing a full restart from byte zero, which wastes hours of upload time on an unreliable ISP connection. The company wants uploads to resume from the point of failure and would also like faster throughput by sending pieces of a file in parallel.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket and have customers upload through the acceleration endpoint.
B. Use the S3 multipart upload API to split each file into parts, upload parts in parallel, and retry only the failed parts.
C. Increase the customers' client-side HTTP request timeout setting so a single PutObject call has more time to complete.
D. Enable S3 Cross-Region Replication so a partially uploaded object is retried automatically in a second region.
**Correct answer(s):** B
**Why correct:** Multipart upload splits an object into independently uploaded parts, each of which can be retried on its own if it fails, and parts can be sent in parallel to improve throughput — directly addressing both stated pain points (resumability and parallel speed) for large objects.
**Why each wrong option is wrong:** A speeds up transfer over long network distances via edge locations but does nothing to make a single large PutObject resumable after a failure; C only delays the inevitable failure of a single monolithic request and does nothing for parallelism or partial resume; D replicates already-stored objects to another region and has no effect on how an object is uploaded or on upload reliability.
**Trigger words:** "uploads... frequently fail partway through," "resume from the point of failure," "sending pieces of a file in parallel."
**Underlying architectural principle:** Large object uploads should be split into independently retriable, parallelizable parts via multipart upload rather than relying on a single large atomic request.

---

### Question 130 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A global logistics company has field offices in Nairobi, Manila, and Buenos Aires that each generate large (5-15 GB) sensor-log bundles daily and upload them to a single S3 bucket in us-east-1. Offices in these regions consistently report upload times 4-6x slower than a comparable office in Virginia, even though their local internet connections are otherwise fast and uncongested. The company does not want to create regional buckets or manage any replication, and needs a change that requires no modification to the existing upload application logic beyond pointing it at a different endpoint.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket and have the offices upload via the acceleration endpoint.
B. Create a CloudFront distribution in front of the bucket and configure it to cache PUT and POST requests.
C. Set up S3 Cross-Region Replication to buckets closer to each office and have each office upload locally.
D. Switch the bucket's storage class to S3 Intelligent-Tiering so uploads are automatically optimized for access frequency.
**Correct answer(s):** A
**Why correct:** Transfer Acceleration routes uploads through the nearest CloudFront edge location and over the optimized AWS backbone network to the bucket's region, which directly reduces the long-haul latency and packet-loss penalty that geographically distant uploaders experience, with only an endpoint change required.
**Why each wrong option is wrong:** B is incorrect because CloudFront caches and accelerates content reads/distribution, not object writes — it does not meaningfully accelerate PUT/POST upload traffic to an origin; C solves the problem but requires standing up and managing additional buckets and replication/routing logic, which the scenario explicitly rules out; D changes cost/storage-tiering behavior for stored objects and has no effect on upload transfer speed.
**Trigger words:** "field offices... geographically distant," "upload times 4-6x slower," "no modification to the existing upload application logic beyond pointing it at a different endpoint."
**Underlying architectural principle:** S3 Transfer Acceleration solves long-distance upload/download latency by using CloudFront's edge network and AWS's backbone, whereas CloudFront itself is a read/distribution caching layer, not an upload accelerator.

---

### Question 131 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A stock-market data vendor writes tick data into an S3 bucket using object keys of the form `2026-08-15/13-45-00-123.json`, sorted by timestamp. During the first 90 seconds of each trading day's opening bell, write throughput spikes almost instantly from near zero to over 12,000 PUT requests per second, and the application begins receiving intermittent `503 SlowDown` responses during that spike, even though S3's published per-prefix request limits are well above the vendor's average sustained rate. Traffic settles into a sustainable pattern within about two minutes. The vendor wants to eliminate the throttling during the opening-bell spike without introducing a queue or any additional infrastructure to buffer requests.
**Options:**
A. Prepend a high-cardinality hash (e.g., a few random hex characters) to each object key so that writes are spread across many partitions from the very first request.
B. Request an S3 service-quota increase for PutObject requests per second through AWS Support.
C. Enable S3 Transfer Acceleration on the bucket to increase the effective request rate the bucket can absorb.
D. Switch the bucket's storage class to S3 One Zone-IA, which supports a higher baseline request rate than S3 Standard.
**Correct answer(s):** A
**Why correct:** S3 automatically scales request capacity per prefix over time, but that scaling ramps up gradually rather than instantaneously; a sequential timestamp-based key concentrates all writes onto what is effectively a single prefix at the moment of a sudden spike, so distributing keys across many prefixes from the first request (via a random/hashed prefix) immediately parallelizes writes across many partitions instead of waiting for gradual scaling to catch up.
**Why each wrong option is wrong:** B is not applicable because S3 request-rate performance is not gated by a per-account raise-able service quota in the way EC2/Lambda limits are — there is no "PutObject requests per second" quota to increase in the Service Quotas console; the bottleneck here is partition scaling behavior tied to key naming, not an account ceiling (the closest real analog — asking AWS Support to pre-warm a bucket ahead of a known traffic increase — is a different, informal action, not a quota increase, and still would not be as immediate or self-contained as fixing the key design); C accelerates long-distance transfer speed over the network path, not the rate at which a bucket's internal partitions can absorb sudden concentrated write bursts; D is incorrect because storage class does not change S3's request-rate/partitioning behavior — One Zone-IA has no distinct baseline request-rate advantage over Standard.
**Trigger words:** "sorted by timestamp," "spikes almost instantly," "503 SlowDown," "well above the vendor's average sustained rate," "without introducing a queue."
**Underlying architectural principle:** S3 scales request rate per prefix automatically but progressively, so workloads with sudden, extreme write bursts on sequentially-patterned keys benefit from deliberately randomizing key prefixes to spread load across partitions immediately rather than relying on S3 to catch up.

---

### Question 132 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A mid-sized SaaS company is migrating a PostgreSQL database from on-premises to an EC2-hosted instance. The database needs consistently good, predictable IOPS and throughput for typical OLTP traffic, but the workload is not described as latency-sensitive to sub-millisecond levels, and the team is cost-conscious and wants to provision IOPS and throughput independently of how large the volume is.
**Options:**
A. Amazon EBS gp3 volume, with IOPS and throughput provisioned to match the workload's needs.
B. Amazon EBS io2 Block Express volume, provisioned at its maximum IOPS tier.
C. Amazon EBS gp2 volume, sized larger than needed so its IOPS baseline scales up accordingly.
D. Amazon EBS st1 (Throughput Optimized HDD) volume for consistent throughput at low cost.
**Correct answer(s):** A
**Why correct:** gp3 provides a solid baseline of 3,000 IOPS and 125 MiB/s throughput independent of volume size, and lets you provision additional IOPS/throughput separately at a lower cost than the equivalent gp2 or io-family performance, matching the description of predictable-but-not-extreme performance needs with cost sensitivity.
**Why each wrong option is wrong:** B is over-provisioned and needlessly expensive for a workload with no stated sub-millisecond-latency or mission-critical extreme-IOPS requirement; C ties IOPS to volume size (3 IOPS/GB) and requires oversizing the volume purely to buy performance, which is both wasteful and still burst-credit-dependent rather than a guaranteed baseline; D is a throughput-optimized HDD meant for large sequential I/O like big-data/log workloads and cannot even serve as a boot/database volume needing random-access OLTP performance.
**Trigger words:** "consistently good, predictable IOPS," "not... sub-millisecond," "cost-conscious," "provision IOPS and throughput independently of... size."
**Underlying architectural principle:** gp3 is the default modern choice for general-purpose workloads needing predictable, independently-tunable performance at low cost, reserving io2/io2 Block Express for explicit extreme-IOPS or sub-millisecond-latency requirements.

---

### Question 133 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An engineering team migrated a data-processing application from a modern EC2 instance type to an older-generation instance type to save cost, keeping the exact same gp3 EBS volume with the same provisioned IOPS and throughput settings. After the migration, the team observes that disk read/write throughput is capped well below the volume's provisioned throughput, even though CloudWatch shows the instance's network throughput and CPU are not saturated. No changes were made to the application code or the EBS volume configuration.
**Options:**
A. Confirm the instance type is EBS-optimized (or has sufficient dedicated EBS bandwidth) and, if not, move to a current-generation instance type that provides adequate dedicated EBS throughput.
B. Increase the gp3 volume's provisioned IOPS further, since the bottleneck must be insufficient IOPS on the volume itself.
C. Convert the gp3 volume to gp2 so its performance scales automatically with its size.
D. Enable EBS Multi-Attach on the volume to distribute I/O across multiple network paths.
**Correct answer(s):** A
**Why correct:** EBS-optimized instances provide dedicated bandwidth between the instance and EBS, separate from general network traffic; older-generation or smaller instance types can have insufficient dedicated EBS bandwidth to sustain a volume's full provisioned throughput even when the volume itself is correctly configured and CPU/network aren't the bottleneck, so the fix is ensuring adequate EBS-optimized bandwidth on the instance side.
**Why each wrong option is wrong:** B assumes the volume's provisioned IOPS is the bottleneck, but the scenario states the same provisioned settings worked before the instance change, pointing to the instance's EBS bandwidth ceiling instead; C moves to a volume type whose performance is tied to size and burst credits, which does not address an instance-side bandwidth limitation and is a downgrade in guaranteed performance; D is for attaching one volume to multiple instances concurrently for cluster-aware filesystems and has no effect on a single instance's dedicated bandwidth to a single attached volume.
**Trigger words:** "migrated... to an older-generation instance type," "throughput is capped... even though... network throughput and CPU are not saturated," "no changes... to the... EBS volume configuration."
**Underlying architectural principle:** EBS performance is bounded by both the volume's provisioned capability and the instance's dedicated EBS bandwidth, so a throughput ceiling with a correctly-configured, unsaturated volume points to insufficient EBS-optimized bandwidth on the compute side.

---

### Question 134 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A financial risk-modeling firm runs a single EC2 instance that needs to sustain roughly 400,000 IOPS and 6 GB/s of throughput against its working dataset for overnight batch simulations, a level that exceeds the documented per-volume maximum for even the highest-performance single EBS volume type available. The workload requires block-storage semantics (not a shared file system), must run on a single instance, and the firm wants to stay within standard EBS offerings rather than adopting a different storage service.
**Options:**
A. Provision a single io2 Block Express volume and request a soft-limit increase from AWS Support to exceed its published per-volume maximum.
B. Stripe multiple io2 Block Express volumes together using RAID 0 at the OS level to aggregate their IOPS and throughput.
C. Attach the io2 Block Express volume to multiple instances simultaneously using EBS Multi-Attach to parallelize I/O across instances.
D. Migrate the workload to Amazon EFS with Max I/O performance mode, which scales throughput across many parallel clients.
**Correct answer(s):** B
**Why correct:** When a workload's required IOPS/throughput exceeds what even the highest-performing single EBS volume can deliver, the standard AWS pattern is to stripe multiple volumes together with RAID 0 at the OS level, aggregating their individual IOPS and throughput ceilings into a combined pool available to the single instance.
**Why each wrong option is wrong:** A is invalid because per-volume IOPS/throughput maximums for io2 Block Express are hard architectural limits, not adjustable soft limits that AWS Support can raise; C parallelizes attachment to multiple instances for cluster-aware filesystems, it does not increase the throughput ceiling delivered to any single instance and isn't intended to aggregate performance for one host; D changes both the storage paradigm (shared file system vs block) and is optimized for many concurrent clients rather than maximizing single-instance block I/O, which doesn't fit the stated single-instance block-storage requirement.
**Trigger words:** "exceeds the documented per-volume maximum," "block-storage semantics... single instance," "stay within standard EBS offerings."
**Underlying architectural principle:** When a single EBS volume's maximum IOPS or throughput is insufficient, RAID 0 striping across multiple volumes at the OS level is the standard way to exceed a single volume's performance ceiling for one instance.

---

### Question 135 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media-processing company runs a fleet of EC2 instances that mount a shared EFS file system for a video-transcoding pipeline. Traffic is highly unpredictable: some days see near-zero jobs, while breaking-news days can spike file-system throughput demand by 20x within minutes. The team does not want to forecast or manually configure a fixed throughput value ahead of time, wants to avoid overpaying during idle periods, and wants throughput to scale automatically without any capacity planning exercise.
**Options:**
A. Configure the file system to use Provisioned Throughput mode, sized generously to cover the highest expected spike.
B. Configure the file system to use Elastic Throughput mode, which scales throughput up and down automatically with the workload.
C. Configure the file system to use Bursting Throughput mode, relying on burst credits accumulated during idle periods.
D. Configure the file system to use Max I/O performance mode, since it provides the highest aggregate throughput ceiling.
**Correct answer(s):** B
**Why correct:** Elastic Throughput mode automatically scales a file system's throughput up and down to match the current workload in near-real time with no capacity planning or fixed provisioning, and bills based on actual usage — precisely matching the requirement for unpredictable, spiky traffic with no manual forecasting and no overpaying during idle periods. Throughput mode (unlike performance mode) can be changed on an existing file system at any time, so this requires no migration.
**Why each wrong option is wrong:** A requires provisioning a fixed throughput value up front sized for the worst case, which both requires capacity planning the team wants to avoid and results in overpaying during idle periods; C ties available throughput to a burst-credit balance accumulated based on storage size and recent usage, which can be exhausted precisely during a sudden large spike after idle periods, unlike Elastic's real-time auto-scaling; D is a performance mode governing latency/parallelism characteristics, not a throughput-scaling mechanism, and does not by itself solve unpredictable throughput demand.
**Trigger words:** "highly unpredictable," "spike... by 20x within minutes," "avoid overpaying during idle periods," "without any capacity planning exercise."
**Underlying architectural principle:** EFS Elastic Throughput mode is the modern, management-free answer for unpredictable or highly variable workloads, replacing manual throughput provisioning or burst-credit dependency.

---

### Question 136 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A genomics research lab runs a data pipeline where 800 EC2 instances in an Auto Scaling group simultaneously mount the same EFS file system and each read and write many small files in parallel as part of a highly parallelized batch analysis job. The lab has profiled the workload and found that aggregate throughput across all 800 clients — not the latency of any single client's individual operation — is the limiting factor in total job completion time. A prior attempt using the default file-system configuration showed throughput plateauing well before the fleet's combined demand was met. The lab is willing to provision a new file system and migrate data if required, since they know some EFS settings can only be chosen at file-system creation time.
**Options:**
A. Create a new EFS file system with Max I/O performance mode selected at creation, migrate the pipeline's data to it, and repoint the fleet's mount targets at the new file system.
B. Switch the existing file system's throughput mode from Bursting to Provisioned, provisioned at a very high fixed value.
C. Reduce the size of the Auto Scaling group so fewer clients compete for the same aggregate throughput.
D. Migrate from EFS to a single large gp3 EBS volume shared across all 800 instances via Multi-Attach.
**Correct answer(s):** A
**Why correct:** Max I/O performance mode is purpose-built to scale to higher levels of aggregate throughput and IOPS across a very large number of concurrent clients, at the cost of slightly higher per-operation latency — exactly the tradeoff described, where aggregate fleet-wide throughput (not single-client latency) is the bottleneck. Performance mode can only be set when a file system is created and cannot be changed afterward, so realizing this fix requires provisioning a new file system with Max I/O selected at creation (e.g., copying data over with a tool like AWS DataSync) and migrating the fleet to it, rather than modifying the existing file system in place.
**Why each wrong option is wrong:** B addresses throughput mode (bandwidth budget), which can be changed on an existing file system, but doesn't touch the performance mode dimension of scaling metadata operations and aggregate IOPS across massively parallel clients, so throughput can still plateau due to the performance-mode ceiling of General Purpose; C reduces the workload's parallelism to work around the platform's limits rather than fixing the underlying scaling ceiling, directly hurting the stated goal of a highly parallelized job; D is invalid on multiple counts — EBS Multi-Attach is only supported for io1 and io2 volumes, not gp3, so a "gp3 volume... via Multi-Attach" is not even a valid configuration; even with a supported volume type, Multi-Attach is capped at 16 Nitro-based instances within a single Availability Zone (nowhere near 800), and it still requires a cluster-aware file system to coordinate concurrent writes rather than the general-purpose concurrent read/write access EFS provides natively.
**Trigger words:** "800 EC2 instances... simultaneously mount," "aggregate throughput... not the latency of any single client," "throughput plateauing... before the fleet's combined demand was met," "some EFS settings can only be chosen at file-system creation time."
**Underlying architectural principle:** EFS Max I/O performance mode should be chosen specifically when many concurrent clients need scaled-up aggregate throughput/IOPS and can tolerate marginally higher per-operation latency, distinguishing it from General Purpose mode's low single-operation latency optimization — and because performance mode is immutable after creation (unlike throughput mode), switching to it requires provisioning a new file system and migrating data.

---

### Question 137 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A retail company runs its order-processing system on a single Amazon RDS for MySQL instance using a classic Multi-AZ (single-standby) deployment for high availability — not a Multi-AZ DB cluster deployment. The business intelligence team now wants to run heavy, long-running analytical queries against the same data for daily reporting, but these queries are starting to noticeably slow down the production order-processing workload on the primary instance. The company wants to isolate the reporting workload's load from the primary without re-architecting into a separate data warehouse, and with minimal application changes.
**Options:**
A. Create one or more RDS Read Replicas from the primary instance and point the BI reporting tool at a replica's endpoint.
B. Point the BI reporting tool at the Multi-AZ standby instance's endpoint instead of the primary.
C. Increase the Multi-AZ primary instance's class to a larger size so it can absorb both workloads.
D. Enable RDS Storage Auto Scaling on the primary instance so it can handle the additional query load.
**Correct answer(s):** A
**Why correct:** RDS Read Replicas are purpose-built for offloading read-heavy workloads like reporting from the primary instance, providing their own distinct endpoint that the BI tool can be pointed at with no changes to the production application, directly isolating the reporting load.
**Why each wrong option is wrong:** B is invalid because in a classic Multi-AZ (single-standby) deployment, the standby exists purely as a synchronous failover target and is not readable or queryable (this is distinct from the newer Multi-AZ DB cluster deployment option, which does expose two readable standbys via a dedicated reader endpoint — but the scenario explicitly specifies the classic single-standby deployment, so that capability does not apply here); C only pushes the primary instance's capacity ceiling higher without isolating the two workloads, so BI queries would still directly contend with production traffic on the same instance; D scales storage capacity (disk space) automatically, which has nothing to do with compute/query contention between reporting and production workloads.
**Trigger words:** "heavy, long-running analytical queries," "slow down the production... workload," "isolate the reporting workload's load," "minimal application changes."
**Underlying architectural principle:** RDS Read Replicas, not a classic Multi-AZ standby, are the mechanism for offloading and isolating read-heavy secondary workloads from a primary database instance.

---

### Question 138 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company built a serverless order-confirmation workflow where an AWS Lambda function is invoked on every checkout event and opens a new connection to an Amazon RDS for PostgreSQL instance to write the order record. During flash-sale traffic bursts, thousands of concurrent Lambda invocations open thousands of simultaneous database connections, and the database begins rejecting connections with "too many connections" errors, causing failed checkouts. The company wants to fix this without redesigning the checkout flow away from Lambda-per-request and without manually implementing custom connection-pooling logic inside the function.
**Options:**
A. Place Amazon RDS Proxy in front of the RDS instance and have the Lambda function connect through the proxy endpoint instead of directly to the database.
B. Increase the RDS instance's max_connections parameter to a much higher value to accommodate the concurrency spike.
C. Add an Amazon ElastiCache for Redis layer in front of RDS to cache and reduce the number of write operations.
D. Switch the Lambda function's concurrency model to reserved concurrency set to 1 so only one invocation runs at a time.
**Correct answer(s):** A
**Why correct:** RDS Proxy sits between the application and the database, pooling and multiplexing many client connections (including bursty Lambda invocations) over a much smaller number of actual database connections, which directly solves connection exhaustion without requiring the application to implement its own pooling logic.
**Why each wrong option is wrong:** B raises a ceiling but doesn't solve the underlying inefficiency of one-connection-per-invocation at scale, is bounded by instance memory/class limits, and can itself degrade database performance well before matching flash-sale concurrency; C is aimed at caching reads or reducing read load, not at solving a write-path connection-exhaustion problem, since orders are being written, not read; D would eliminate the connection storm but at the cost of serializing all checkouts to one at a time, destroying the scalability the flash sale requires and effectively breaking the checkout flow under load.
**Trigger words:** "thousands of concurrent Lambda invocations open thousands of simultaneous database connections," "too many connections," "without... manually implementing custom connection-pooling logic."
**Underlying architectural principle:** RDS Proxy is the managed solution for connection pooling/multiplexing when serverless, highly concurrent clients like Lambda would otherwise overwhelm a relational database's maximum connection limit.

---

### Question 139 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A SaaS analytics company runs Amazon Aurora MySQL as its primary database and has added several Aurora Replicas to handle a growing read-heavy dashboard workload. As they add and remove replicas over time to match load (via Aurora Auto Scaling for replicas), the application team is manually updating each application server's configuration with the current list of replica endpoints, which is error-prone and has caused stale-endpoint errors after scaling events. The company wants read traffic to automatically and transparently load-balance across whichever replicas currently exist, without the application needing to track individual replica endpoints.
**Options:**
A. Configure the application to connect to the Aurora cluster's Reader endpoint instead of individual replica instance endpoints.
B. Configure the application to connect to the Aurora cluster's Writer endpoint for all read and write traffic.
C. Manually maintain a Route 53 weighted routing policy across all current replica endpoints and update it via a script after every scaling event.
D. Switch from Aurora Replicas to standard RDS Read Replicas, which expose a single shared endpoint for all replicas automatically.
**Correct answer(s):** A
**Why correct:** The Aurora cluster's Reader endpoint automatically load-balances connections across all currently available Aurora Replicas and transparently reflects replicas added or removed by Auto Scaling, eliminating the need for the application to track individual replica endpoints itself.
**Why each wrong option is wrong:** B routes all traffic to the single writer instance, defeating the purpose of having read replicas at all and adding unnecessary write-instance load; C reinvents endpoint management with custom automation, which is exactly the manual, error-prone tracking the company wants to eliminate, and Route 53 weighted routing doesn't have native awareness of Aurora Auto Scaling replica membership; D is factually backwards — standard RDS Read Replicas each expose their own distinct endpoint that the application must track individually and do not provide an automatic load-balancing reader endpoint the way Aurora does.
**Trigger words:** "manually updating each application server's configuration with the current list of replica endpoints," "automatically and transparently load-balance," "without the application needing to track individual replica endpoints."
**Underlying architectural principle:** Aurora's cluster Reader endpoint provides automatic, membership-aware load balancing across Aurora Replicas, a capability standard RDS Read Replicas do not offer natively.

---

### Question 140 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A gaming company's leaderboard service reads player-ranking data from a DynamoDB table extremely frequently — the same small set of "top player" items are read thousands of times per second by many game clients. The engineering team wants to reduce read latency for these hot items from single-digit milliseconds down to microseconds, wants to avoid rewriting the application's existing DynamoDB SDK calls, and wants the caching layer to be automatically kept reasonably in sync with the underlying table without the application managing cache invalidation logic itself.
**Options:**
A. Add Amazon DynamoDB Accelerator (DAX) in front of the table and point the application's DynamoDB client at the DAX cluster endpoint.
B. Add an Amazon ElastiCache for Memcached cluster in front of the table and modify the application to check the cache before calling DynamoDB.
C. Enable DynamoDB Accelerated Read Scaling by switching the table's read capacity mode to On-Demand.
D. Increase the table's provisioned read capacity units substantially to reduce per-request latency.
**Correct answer(s):** A
**Why correct:** DAX is an in-memory cache built specifically for DynamoDB that is API-compatible with the existing DynamoDB SDK (requiring minimal code change beyond pointing at the DAX endpoint), delivers microsecond read latency for cached items, and uses write-through caching to stay reasonably synchronized with the table automatically.
**Why each wrong option is wrong:** B requires the application to add explicit cache-check-then-fallback logic and cache-population code, directly conflicting with the "avoid rewriting the application's existing DynamoDB SDK calls" requirement, and ElastiCache is not natively API-compatible with DynamoDB calls; C is not a real DynamoDB feature — capacity mode (On-Demand vs Provisioned) affects auto-scaling of throughput capacity, not per-request latency down to microseconds; D can improve throughput headroom and reduce throttling but does not fundamentally change DynamoDB's normal single-digit-millisecond latency profile down to microseconds.
**Trigger words:** "same small set of... items are read thousands of times per second," "microseconds," "avoid rewriting the application's existing DynamoDB SDK calls," "without the application managing cache invalidation logic."
**Underlying architectural principle:** DAX is the purpose-built, drop-in caching layer for DynamoDB read-heavy hot-item workloads needing microsecond latency with minimal application changes, distinct from general-purpose caches like ElastiCache that require explicit application-level cache logic.

---

### Question 141 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A ride-sharing company's pricing engine writes a new surge-pricing value to a DynamoDB item roughly 200 times per second for each of 50 active city zones, and every write is immediately followed by a read of that same item by a downstream billing service that must always see the value from the most recent write with no staleness whatsoever. A junior engineer proposes adding DAX in front of the table to "speed everything up," but a senior architect is concerned this will not deliver the expected benefit for this specific access pattern and may add unnecessary cost and operational surface area. Which statement best explains the senior architect's concern?
**Options:**
A. DAX's write-through cache does not help this pattern because the billing service's strongly consistent reads bypass the DAX cache and go directly to DynamoDB, so DAX adds cost without meaningfully speeding up the read path that matters here.
B. DAX cannot be used at all with a table that receives more than 100 writes per second, so the proposal is technically infeasible regardless of consistency requirements.
C. DAX only caches read operations and has no write-through behavior, so every write still bypasses the cache and reads will always return stale data.
D. DAX requires the application to explicitly invalidate cache entries after every write, which the pricing engine does not currently do, so reads would silently return outdated surge prices.
**Correct answer(s):** A
**Why correct:** DAX honors DynamoDB consistency semantics by routing strongly consistent read requests through to the underlying table rather than serving them from cache, so for a workload whose defining requirement is "always see the most recent write with no staleness," DAX's cache is effectively bypassed for the reads that matter, meaning the extra cluster is added cost and operational complexity without the intended latency benefit for this specific read pattern.
**Why each wrong option is wrong:** B is factually incorrect — DAX has no such hard write-per-second ceiling that makes it infeasible; C is factually incorrect — DAX does implement write-through caching, updating the cache on writes, it's simply that consistency semantics for this scenario route reads elsewhere; D is incorrect because DAX's write-through and TTL-based invalidation are automatic and do not require the application to explicitly invalidate cache entries.
**Trigger words:** "must always see the value from the most recent write with no staleness whatsoever," "concerned this will not deliver the expected benefit," "unnecessary cost and operational surface area."
**Underlying architectural principle:** DAX accelerates eventually-consistent (and cached strongly-consistent-eligible) read-heavy access patterns, but strongly consistent reads pass through to DynamoDB directly, so DAX provides little to no benefit for workloads whose reads specifically require strong consistency on every request.

---

### Question 142 [Priority: P0] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A platform team is choosing an in-memory caching engine on Amazon ElastiCache for a new stateless web-tier session store. Requirements include: sessions must survive an individual cache node failure without being lost, the cache must support automatic failover to a replica if the primary node fails, and the team occasionally needs to take a point-in-time backup of the cache's contents for disaster-recovery testing. The team is evaluating both available engines and needs to select the reasons that specifically justify choosing Redis over Memcached for this use case. (Select TWO.)
**Options:**
A. Redis supports replication with automatic failover to a read replica, which Memcached's multi-node architecture does not provide.
B. Redis supports snapshot-based backup and restore of the dataset, while Memcached has no native backup/restore capability.
C. Redis always delivers lower absolute read latency per item than Memcached under any workload.
D. Memcached cannot be deployed with more than a single node, making it inherently less scalable than Redis.
E. Redis uses less memory per cached item than Memcached for equivalent key-value data.
**Correct answer(s):** A, B
**Why correct:** Redis (via replication groups / Cluster Mode) provides automatic failover to a replica when the primary node fails, directly satisfying the "survive node failure" and "automatic failover" requirements; Redis also supports snapshot (RDB) and append-only-file backups that can be restored later, directly satisfying the "point-in-time backup for DR testing" requirement — neither capability exists natively in Memcached.
**Why each wrong option is wrong:** C is false as a blanket claim — Memcached's multi-threaded architecture can outperform Redis for simple key-value gets on many small objects under certain workloads, so "always lower latency" is not a valid or exam-accurate justification; D is factually wrong because Memcached does support multiple nodes for horizontal sharding of the keyspace, it simply lacks built-in replication/HA between nodes, which is a different limitation than "cannot have more than one node"; E is not an accurate or exam-relevant differentiator — memory efficiency per item is not the basis for the Redis-vs-Memcached decision in this scenario, and no such consistent property is true in general.
**Trigger words:** "survive an individual cache node failure," "automatic failover to a replica," "point-in-time backup... for disaster-recovery testing."
**Underlying architectural principle:** Choose Redis over Memcached specifically when a caching layer needs durability features — replication with automatic failover and backup/restore — rather than for a generic "faster" or "more scalable" claim, which are not the reliable differentiators between the two engines.

---

### Question 143 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A satellite-imagery company has research partners on four continents who each need to upload newly captured 3-8 GB image files into a single centralized S3 bucket in eu-central-1 as quickly and reliably as possible. Partners report slow, sometimes-failing uploads over their long-haul internet connections. The company wants to improve upload speed and reliability for these large, geographically distant uploads without standing up additional buckets, without introducing any intermediate compute layer, and with the least possible ongoing operational overhead. Select the TWO changes that best address this requirement.
**Options:**
A. Enable S3 Transfer Acceleration on the destination bucket and have partners upload through the acceleration endpoint.
B. Have the upload client use the S3 multipart upload API to split each large file into parts uploaded in parallel, retrying only failed parts.
C. Set up S3 Cross-Region Replication from a new local bucket in each partner's nearest region back to the central eu-central-1 bucket.
D. Increase the multipart upload part size to the maximum allowed so fewer, larger parts are transferred per file.
E. Front the bucket with an EC2-based upload proxy fleet in each partner region that relays files to the central bucket over a Site-to-Site VPN.
**Correct answer(s):** A, B
**Why correct:** Transfer Acceleration reduces the long-haul latency and loss impact for geographically distant uploaders by routing traffic through the nearest edge location onto the AWS backbone, and multipart upload makes each large object's transfer both faster (parallel parts) and resilient (only failed parts are retried) — together directly addressing both the "slow" and "sometimes-failing" symptoms with no new infrastructure to operate.
**Why each wrong option is wrong:** C requires provisioning and maintaining an additional bucket per region plus ongoing replication configuration, which conflicts with "without standing up additional buckets" and adds operational overhead; D is a tuning detail that can help marginally but larger part sizes reduce parallelism benefits and increase the amount of data lost on a single part's failure, making it a weaker/partial answer compared to the multipart approach itself, and it is not a required or sufficient standalone fix; E introduces an entirely new compute layer (EC2 fleet, VPN) to manage and secure, directly violating "without introducing any intermediate compute layer" and adding substantial operational overhead.
**Trigger words:** "geographically distant uploads," "slow, sometimes-failing," "without standing up additional buckets," "without introducing any intermediate compute layer," "least possible ongoing operational overhead."
**Underlying architectural principle:** For large-object uploads across long distances, Transfer Acceleration (network path optimization) and multipart upload (parallel, resumable transfer) are complementary, infrastructure-light solutions that should be combined rather than solved via additional buckets, replication, or custom relay compute.

---

### Question 144 [Priority: P2] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A subscription-billing platform runs Amazon Aurora PostgreSQL as its transactional database. Billing calculations are triggered by AWS Lambda functions invoked on a schedule every minute across thousands of customer accounts in parallel, causing periodic bursts of database connections that occasionally exhaust the database's connection limit. Separately, the customer-facing dashboard repeatedly re-runs the same expensive aggregate query (current-month invoice totals per account) on every page load, and this identical query is currently re-executed against Aurora every single time even though the underlying invoice data only changes a few times per day. The team wants to address both the connection-exhaustion problem and the redundant-expensive-query problem with the most targeted, purpose-built services for each, without switching database engines. Select the TWO services that correctly address these two distinct problems.
**Options:**
A. Amazon RDS Proxy, placed in front of Aurora to pool and multiplex the Lambda functions' bursty connections.
B. Amazon ElastiCache for Redis, placed in front of Aurora to cache the repeated aggregate query's results with a TTL matching the data's actual change frequency.
C. Amazon DynamoDB Accelerator (DAX), placed in front of Aurora to cache the repeated aggregate query's results.
D. Amazon Aurora Serverless v2, replacing the connection-management problem entirely by auto-scaling ACUs during connection bursts.
E. AWS Database Migration Service (DMS), used to continuously replicate invoice totals into a pre-aggregated read-optimized table.
**Correct answer(s):** A, B
**Why correct:** RDS Proxy is purpose-built to pool and multiplex bursty, short-lived connections (the classic Lambda-to-relational-database problem) in front of Aurora, directly solving connection exhaustion; ElastiCache for Redis is the correct general-purpose cache for repeated, expensive relational query results, letting the dashboard serve a cached aggregate with a TTL that matches the actual data change cadence instead of re-querying Aurora on every page load.
**Why each wrong option is wrong:** C is invalid because DAX is a cache exclusively for DynamoDB and is not compatible with or usable in front of a relational engine like Aurora PostgreSQL; D addresses compute capacity auto-scaling under load but does not itself pool/multiplex connections the way RDS Proxy does — a connection-count ceiling can still be hit regardless of ACU scaling, so it doesn't reliably solve connection exhaustion the way RDS Proxy does; E is designed for data migration/continuous replication between data stores, not for serving low-latency cached query results to a web dashboard, and introduces unnecessary architectural complexity for what is fundamentally a caching problem.
**Trigger words:** "periodic bursts of database connections... exhaust the database's connection limit," "same expensive aggregate query... re-executed... every single time," "underlying invoice data only changes a few times per day," "most targeted, purpose-built services for each."
**Underlying architectural principle:** Connection-exhaustion problems from bursty serverless clients call for RDS Proxy, while redundant expensive relational query results call for a general-purpose cache like ElastiCache — two distinct performance problems each with a distinct, purpose-built AWS solution, neither of which is interchangeable with DynamoDB-specific tooling like DAX.

---

### Question 145 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A publishing company hosts its blog's static assets (HTML, CSS, JS, and article images) in a single S3 bucket in `us-east-1`. Readers in Europe, South America, and Southeast Asia report slow page-load times, while the company's small operations team has no budget for managing additional infrastructure. Traffic is 100% read-heavy and the content changes only a few times per day. The company wants the fastest way to reduce global latency with the least operational overhead.
**Options:**
A. Put an Amazon CloudFront distribution in front of the S3 bucket and enable caching for the static asset paths.
B. Enable S3 Cross-Region Replication to buckets in `eu-west-1`, `sa-east-1`, and `ap-southeast-1`, and use Route 53 latency-based routing across the bucket endpoints.
C. Enable S3 Transfer Acceleration on the bucket so global readers download assets faster.
D. Move the S3 bucket's contents to Amazon EFS and mount it from EC2 instances in each target region.
**Correct answer(s):** A
**Why correct:** CloudFront caches the read-heavy, infrequently-changing static content at edge locations worldwide with a single configuration change, directly solving global latency for a caching-shaped problem with minimal ongoing operations.
**Why each wrong option is wrong:** B requires managing multiple replicated bucket copies and a routing layer for what is fundamentally a caching problem, adding operational overhead the company explicitly doesn't want; C, S3 Transfer Acceleration speeds up long-distance uploads into a bucket, not downloads/delivery to end readers; D, EFS is a regional POSIX file system for EC2 workloads, not a global content delivery mechanism, and would require running and patching EC2 fleets in every region.
**Trigger words:** "static assets," "read-heavy," "changes only a few times per day," "least operational overhead."
**Underlying architectural principle:** When the requirement is "cache read-heavy static content closer to global users," CloudFront is almost always the lowest-effort, purpose-built answer over replicating storage or provisioning compute.

---

### Question 146 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A SaaS company runs an identical, fully independent stack (ALB + Auto Scaling EC2 fleet + RDS) in `us-east-1`, `eu-west-1`, and `ap-southeast-1`. There is no legal or data-residency requirement dictating which region serves which customer — the sole goal is that every user's browser is directed to whichever regional endpoint currently gives them the best network performance, and this should adapt automatically if network conditions change.
**Options:**
A. Create Route 53 latency-based routing records pointing to each regional ALB, with health checks enabled on each record.
B. Create Route 53 geolocation routing records mapping each continent to its nearest regional ALB.
C. Create Route 53 weighted routing records with an even 33/33/34 split across the three ALBs.
D. Create Route 53 failover routing with `us-east-1` as primary and the other two regions as secondary.
**Correct answer(s):** A
**Why correct:** Latency-based routing continuously uses AWS's measured network latency data between users and each region to return the endpoint with the best performance for that specific resolver, which is exactly "best network performance, adapts automatically."
**Why each wrong option is wrong:** B routes strictly by the geographic location of the query, which correlates with but does not guarantee the lowest-latency path (and there's no stated compliance/localization reason to force it); C splits traffic by a fixed arbitrary ratio with no regard to actual performance; D is designed for active/passive disaster recovery, not for concurrently optimizing performance across three active regions.
**Trigger words:** "no legal or data-residency requirement," "best network performance," "adapts automatically."
**Underlying architectural principle:** When the goal is purely speed (not compliance or arbitrary traffic splitting), Route 53 latency-based routing is the routing policy purpose-built for directing users to their fastest available endpoint.

---

### Question 147 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A game studio runs a real-time multiplayer shooter where game clients communicate with regional game servers over a custom UDP protocol. Players worldwide report inconsistent latency and occasional multi-second connection drops during regional network events. The studio wants a solution that improves and stabilizes the network path to the nearest healthy regional deployment and provides fast, automatic rerouting away from an unhealthy region — all without changing the client-side UDP protocol.
**Options:**
A. Deploy AWS Global Accelerator in front of Network Load Balancers in each region, with health checks configured on the endpoint groups.
B. Deploy an Amazon CloudFront distribution in front of the regional game servers.
C. Switch to Route 53 latency-based routing with a very low DNS TTL for the game server domain.
D. Add an Application Load Balancer in each region and rely on cross-zone load balancing.
**Correct answer(s):** A
**Why correct:** Global Accelerator operates at the network layer, supports TCP and UDP, routes traffic over the AWS global backbone to the closest healthy regional endpoint, and performs fast, health-check-driven failover away from an unhealthy endpoint — independent of DNS caching or TTL behavior — matching every stated requirement without touching the client protocol.
**Why each wrong option is wrong:** B, CloudFront is an HTTP(S) content delivery service and does not support arbitrary UDP traffic; C, DNS-based routing failover is limited by resolver caching and TTL expiry, which explains the multi-second drops the studio is already experiencing, not a fix for them; D, an ALB is HTTP(S)-only (Layer 7) and provides no cross-region routing or global static entry point on its own.
**Trigger words:** "custom UDP protocol," "fast, automatic rerouting," "without changing the client-side protocol."
**Underlying architectural principle:** For non-HTTP or latency-sensitive TCP/UDP workloads needing network-layer acceleration and fast regional failover, Global Accelerator is the tool — CloudFront and DNS-based routing are not substitutes for it.

---

### Question 148 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An e-commerce company serves product images through a CloudFront distribution backed by an S3 bucket in `us-east-1`. After a regional S3 disruption caused image delivery failures for several hours, the company wants CloudFront to automatically start serving images from a secondary S3 bucket in `us-west-2` (kept in sync via replication) whenever the primary origin returns errors, with no manual intervention and no DNS changes required.
**Options:**
A. Configure a CloudFront origin group containing both S3 buckets as primary and secondary origins, with failover triggered on specified HTTP status codes.
B. Create a Route 53 health check on the primary S3 bucket's website endpoint and configure DNS failover to the secondary bucket.
C. Enable S3 Cross-Region Replication between the buckets and manually update the CloudFront origin setting during an outage.
D. Put both S3 buckets behind an AWS Global Accelerator endpoint group with health checks.
**Correct answer(s):** A
**Why correct:** CloudFront origin groups are purpose-built for this exact pattern — CloudFront automatically retries the secondary origin when the primary returns the configured failure status codes, requiring no DNS changes or manual action.
**Why each wrong option is wrong:** B introduces a DNS-layer failover mechanism that duplicates and conflicts with CloudFront's own origin resolution, and is not how CloudFront origin failover is implemented; C explicitly requires manual intervention, which the company wants to eliminate; D, Global Accelerator's endpoint groups target ALBs, NLBs, EC2 instances, or Elastic IPs — not S3 buckets — so it cannot front this origin at all.
**Trigger words:** "automatically start serving," "no manual intervention," "no DNS changes."
**Underlying architectural principle:** Origin failover for S3-backed CloudFront distributions is handled natively with CloudFront origin groups, not through DNS-layer failover or manual origin swaps.

---

### Question 149 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A manufacturing company must connect a new factory's sensor network to its AWS VPC for near-real-time analytics. The pilot must be live within two weeks. Leadership has already approved a plan to move to a dedicated 10 Gbps connection for full production traffic roughly six months from now, once the pilot proves value, and wants the pilot approach to not create rework later.
**Options:**
A. Establish an AWS Site-to-Site VPN connection now for the pilot, and in parallel initiate the Direct Connect order so the dedicated connection is ready ahead of the production rollout.
B. Delay the pilot launch until the Direct Connect connection is provisioned, to avoid migrating between connectivity methods later.
C. Use a Direct Connect Gateway immediately, since it can be provisioned within the two-week window.
D. Connect the factory to the VPC using VPC Peering as a temporary bridge until Direct Connect is ready.
**Correct answer(s):** A
**Why correct:** Site-to-Site VPN can be stood up within hours to meet the two-week pilot deadline, and since Direct Connect provisioning routinely takes weeks to months, starting that order in parallel now is the only way to have the dedicated connection ready in roughly six months without idle lead time.
**Why each wrong option is wrong:** B fails the two-week deadline entirely by waiting on a circuit that isn't provisioned yet; C is a distractor — Direct Connect Gateway only aggregates/extends existing Direct Connect connections across VPCs or regions, it does not shorten the physical circuit lead time of the underlying Direct Connect connection itself; D, VPC Peering connects two VPCs to each other, it has no role in connecting an on-premises factory network to a VPC.
**Trigger words:** "must be live within two weeks," "roughly six months from now," "not create rework later."
**Underlying architectural principle:** When there is real time pressure but a longer-term dedicated-connection goal, start VPN immediately for the interim need while placing the Direct Connect order in parallel, rather than waiting on DX's multi-week-to-month lead time.

---

### Question 150 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A large enterprise has 25 departmental VPCs today and expects to add several more each quarter. Every VPC must be able to reach every other VPC, and all VPCs must route their internet-bound traffic through a shared central inspection VPC running a fleet of security appliances. The networking team wants a design that keeps management overhead roughly flat as more VPCs are added.
**Options:**
A. Deploy an AWS Transit Gateway, attach every departmental VPC and the inspection VPC to it, and configure route tables for transitive routing through the inspection VPC.
B. Create full-mesh VPC Peering connections between every pair of the 25 VPCs plus the inspection VPC.
C. Create VPC Peering connections from every departmental VPC to a single central "hub" VPC, and route inter-VPC traffic through that hub.
D. Expose the inspection VPC's security appliances to all other VPCs using AWS PrivateLink endpoint services.
**Correct answer(s):** A
**Why correct:** Transit Gateway is a managed regional routing hub that natively supports transitive routing, so adding a new VPC only requires one new attachment (not connections to every existing VPC), keeping operational effort flat as the environment scales.
**Why each wrong option is wrong:** B, a full mesh of 26 VPCs requires 325 individual peering connections (n(n-1)/2) and grows quadratically with every new VPC, the opposite of flat overhead; C looks like a shortcut but VPC Peering is explicitly non-transitive, so spoke VPCs peered only to the hub still cannot reach each other or route through the hub for internet egress; D, PrivateLink exposes a specific service endpoint one-way to consumers, it is not a mechanism for full bidirectional network routing or shared internet egress across many VPCs.
**Trigger words:** "every VPC must be able to reach every other VPC," "route through a shared central inspection VPC," "management overhead roughly flat."
**Underlying architectural principle:** Once transitive routing or more than a handful of VPCs are involved, Transit Gateway is the scalable answer — VPC Peering's non-transitive nature makes hub-and-spoke peering designs a trap, not a solution.

---

### Question 151 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A video streaming company sells premium content that must only be viewable by subscribers with an active, paid session, delivered through its existing CloudFront distribution. Subscribers' IP addresses change frequently (mobile networks, VPNs), so IP-based restriction is not viable, and each access grant must expire automatically a few minutes after the backend issues it.
**Options:**
A. Have the application backend generate CloudFront signed URLs (or signed cookies) with a short expiration time after validating the subscriber's session.
B. Add a bucket policy on the S3 origin restricting access to the IP address ranges of known subscribers.
C. Restrict the CloudFront distribution to a smaller price class covering only the subscriber base's regions.
D. Add an AWS WAF geo-match rule on the distribution to block requests from countries with no subscribers.
**Correct answer(s):** A
**Why correct:** CloudFront signed URLs/cookies are generated per authenticated session with a defined, short expiration, giving exactly the time-limited, per-subscriber access control the scenario requires without depending on client IP addresses.
**Why each wrong option is wrong:** B is explicitly ruled out by the scenario since subscriber IPs change frequently and can't be reliably enumerated; C, price class only controls which edge locations serve the distribution for cost purposes, it has no effect on who is authorized to view content; D, geo-blocking filters by country, not by individual subscriber authentication or time-limited access, so a non-subscriber in an allowed country could still view the content.
**Trigger words:** "must only be viewable by subscribers with an active, paid session," "IP addresses change frequently," "expire automatically."
**Underlying architectural principle:** Per-user, time-limited content access on CloudFront is achieved with signed URLs/cookies tied to application-level authentication, not with network-level controls like IP allow-lists or geo-blocking.

---

### Question 152 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A B2B software vendor's enterprise customers require IP allow-listing on their own corporate firewalls before any traffic is permitted to the vendor's application. The application runs behind Application Load Balancers in two AWS Regions and serves both standard HTTPS traffic and a custom TCP protocol on port 8443 used by a legacy client. The vendor needs a small, fixed set of IP addresses customers can whitelist once, that also route each customer to whichever region is currently healthy and closest.
**Options:**
A. Front both regional ALBs with AWS Global Accelerator and give customers the accelerator's static anycast IP addresses to whitelist.
B. Put a CloudFront distribution in front of both ALBs and give customers CloudFront's published IP ranges to whitelist.
C. Use Route 53 latency-based routing and give customers the DNS name to resolve, instructing them to whitelist whatever IP it currently returns.
D. Allocate Elastic IP addresses and associate them directly with each regional Application Load Balancer for customers to whitelist.
**Correct answer(s):** A
**Why correct:** Global Accelerator provides a small set of static anycast IP addresses that remain constant regardless of backend or regional changes, supports both HTTPS and arbitrary TCP protocols like the custom port 8443 traffic, and uses health checks to route each customer to the nearest healthy region.
**Why each wrong option is wrong:** B, CloudFront is HTTP(S)-only and cannot carry the custom TCP protocol on port 8443, and its edge IP ranges are large, shared, and not intended as a small fixed allow-list; C, DNS-resolved IPs can change over time and vary by resolver/location, making a stable one-time firewall whitelist impossible; D, Application Load Balancers do not support direct association of Elastic IP addresses (only Network Load Balancers do), so this option is not technically achievable as described.
**Trigger words:** "fixed set of IP addresses," "custom TCP protocol," "corporate firewalls," "closest healthy region."
**Underlying architectural principle:** When customers need a small number of static IPs to whitelist for non-HTTP or mixed-protocol traffic with automatic regional failover, Global Accelerator's anycast IPs are the purpose-built answer.

---

### Question 153 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A financial services firm connects its data center to AWS using a single AWS Direct Connect connection at one Direct Connect location. An internal resiliency review flagged this as a single point of failure: the firm must be able to tolerate the loss of the Direct Connect connection itself, and even the loss of that entire Direct Connect location's facility, without a full multi-day outage to its AWS connectivity. Budget constraints rule out building a second full 10 Gbps dedicated connection with matching bandwidth immediately, but some added resiliency this quarter is required. **(Choose TWO.)**
**Options:**
A. Provision a second Direct Connect connection at a different Direct Connect location.
B. Configure an AWS Site-to-Site VPN connection as a backup path with BGP-based failover to Direct Connect.
C. Increase the bandwidth of the existing Direct Connect connection.
D. Enable a Direct Connect Gateway on the existing connection.
E. Deploy a NAT Gateway in each Availability Zone the VPC uses.
**Correct answer(s):** A, B
**Why correct:** A second Direct Connect connection at a different physical location removes the single-location dependency (and doesn't have to match the primary connection's bandwidth to add real resiliency within budget), and a Site-to-Site VPN backup with BGP failover provides an independent, lower-cost path that survives the loss of the Direct Connect location entirely — together they give layered resiliency within this quarter's budget.
**Why each wrong option is wrong:** C only increases throughput on the same single connection and location, it does nothing to address the loss of that connection or facility; D, Direct Connect Gateway is used to connect one Direct Connect connection to multiple VPCs or regions, it does not add redundancy to the underlying physical connection; E, NAT Gateways manage outbound internet access for private subnets and have no relationship to on-premises-to-AWS hybrid connectivity resiliency.
**Trigger words:** "single point of failure," "tolerate the loss of the Direct Connect connection... or the location," "some added resiliency this quarter."
**Underlying architectural principle:** Direct Connect resiliency is achieved by adding physically diverse connections and/or a VPN backup path — not by scaling bandwidth or using constructs like Direct Connect Gateway that solve a different problem (multi-VPC/region reach, not availability).

---

### Question 154 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A regional online retailer confirms via analytics that essentially all of its customers are located in the United States, Canada, and Western Europe. Its product catalog site is served through CloudFront in front of S3, and a recent cost review found the distribution is incurring charges for edge locations in South America, Asia Pacific, Australia, and the Middle East where it has effectively zero legitimate traffic. The retailer wants to reduce CloudFront cost without changing its caching behavior or degrading performance for its actual customer base.
**Options:**
A. Change the CloudFront distribution's price class to restrict it to North America and Europe edge locations only.
B. Replace CloudFront with AWS Global Accelerator to reduce delivery costs.
C. Reduce the cache TTL on the distribution's static asset behaviors to lower cost.
D. Add an AWS WAF geo-match rule to block requests originating from regions outside North America and Europe.
**Correct answer(s):** A
**Why correct:** CloudFront's price class setting directly controls which set of edge locations are used to serve the distribution, and restricting it to the regions covering the actual customer base reduces cost precisely because requests are no longer served (and billed) from unused higher-cost edge location tiers, with no change to caching behavior.
**Why each wrong option is wrong:** B, Global Accelerator is a network-path optimization service for TCP/UDP workloads with its own separate pricing model, it is not a caching replacement and would not reduce this specific CloudFront edge-location cost driver; C, lowering TTL causes more requests to fall through to the origin, increasing origin fetches and data transfer cost — the opposite of the desired outcome, and it doesn't address unused edge locations at all; D, geo-blocking with WAF filters requests for security/access-control reasons and could incorrectly block legitimate travelers or VPN users, and it is not how CloudFront edge-location billing works, so it does not directly control which price-tier edge locations serve traffic.
**Trigger words:** "essentially all customers... United States, Canada, and Western Europe," "reduce CloudFront cost," "without... degrading performance for its actual customer base."
**Underlying architectural principle:** When a CloudFront audience is geographically concentrated, price class restriction is the direct cost lever — it is a distinct control from caching behavior (TTL) and from access control (WAF/geo-blocking).

---

### Question 155 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A multinational retailer runs identical order-processing APIs in `eu-west-1` and `us-east-1`. A new EU data-protection requirement mandates that all requests originating from EU member countries must always be served exclusively by the `eu-west-1` stack, with no exceptions, regardless of measured network conditions. All other users worldwide should simply be routed to whichever of the two regions currently gives them the best latency. The solution must use Amazon Route 53.
**Options:**
A. Configure Route 53 geolocation routing records mapping EU country codes to `eu-west-1`, and configure a "Default" geolocation record that resolves (via an alias to a separate set of latency-based records) using a latency-based routing policy across both regions for all other traffic.
B. Configure Route 53 latency-based routing records across both regions for all traffic, relying on `eu-west-1` naturally being lowest-latency for EU users.
C. Configure Route 53 geoproximity routing with a bias value favoring `eu-west-1` for European traffic.
D. Configure Route 53 weighted routing with a 50/50 split between the two regions and instruct EU clients to retry until they land on `eu-west-1`.
**Correct answer(s):** A
**Why correct:** Geolocation routing is the only Route 53 policy that guarantees a hard, compliance-grade mapping of EU country codes to `eu-west-1` regardless of network conditions. Route 53 supports combining routing policies by aliasing the "Default" geolocation record to a separate name that holds two latency-based record sets (one per region) — this correctly optimizes performance for every non-EU user without violating the EU rule.
**Why each wrong option is wrong:** B is a compliance violation risk — pure latency-based routing could, in an edge case (e.g., a network event degrading `eu-west-1`), route an EU user to `us-east-1`, which the "no exceptions" requirement forbids; C, geoproximity routing biases traffic by geographic distance with an adjustable weight, it does not provide a hard, guaranteed regional mapping the way geolocation does; D, weighted routing plus client-side retry logic provides no compliance guarantee at all and pushes an unreliable workaround onto every client.
**Trigger words:** "always be served exclusively," "no exceptions, regardless of measured network conditions," "all other users... best latency."
**Underlying architectural principle:** When a routing requirement is a hard compliance rule for a specific population and a performance optimization for everyone else, combine geolocation (for the guarantee) with latency-based routing as its default fallback — pure latency-based routing cannot provide compliance guarantees.

---

### Question 156 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A global enterprise operates VPCs in six AWS Regions. Within each region there are multiple departmental VPCs plus a shared network-inspection VPC, and every VPC in a region must be able to reach every other VPC in that same region as well as VPCs in all five other regions. The company plans to add new regions periodically as it expands and wants a design that avoids per-VPC-pair connections growing unmanageable as regions and VPCs are added.
**Options:**
A. Deploy a Transit Gateway in each of the six regions, attach that region's VPCs to its local Transit Gateway, and directly peer every pair of the six Transit Gateways with each other (since Transit Gateway peering connections are not transitive, a chain through an intermediate Transit Gateway would not provide full reachability).
B. Create VPC Peering connections between every pair of VPCs across all six regions.
C. Deploy a single Transit Gateway in one region and attach every VPC across all six regions directly to it.
D. Merge all regional VPCs into a single VPC with subnets spanning multiple AWS Regions.
**Correct answer(s):** A
**Why correct:** A regional Transit Gateway per region gives transitive routing within each region. Because Transit Gateway peering itself is non-transitive, full any-to-any reachability across regions requires directly peering every pair of the six regional Transit Gateways (15 peering connections for six regions) rather than chaining them — still a small, linearly-growing number of connections compared to a VPC-level mesh, and adding a new region only requires one new Transit Gateway plus peering links to the existing ones, not a connection to every individual VPC.
**Why each wrong option is wrong:** B, full-mesh peering across dozens of VPCs in six regions grows quadratically and is explicitly non-transitive, making the "every VPC reaches every other VPC" requirement operationally unmanageable; C is not achievable as described — a Transit Gateway attachment must be to a VPC in the same region as the Transit Gateway, so VPCs in the other five regions cannot attach directly to one region's Transit Gateway; D, a VPC is a regional construct and cannot span multiple AWS Regions.
**Trigger words:** "six AWS Regions," "reach every other VPC... in all five other regions," "avoids per-VPC-pair connections growing unmanageable."
**Underlying architectural principle:** Multi-region, multi-VPC transitive connectivity at scale is achieved with one Transit Gateway per region joined by direct, full-mesh inter-region Transit Gateway peering (since peering connections themselves are non-transitive), since Transit Gateway attachments are strictly regional and full-mesh VPC peering does not scale.

---

### Question 157 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A media company's homepage and thumbnail images are static and already served successfully through an existing CloudFront distribution with a good cache-hit ratio. Separately, the company's live video streaming feature uses a custom low-latency UDP-based protocol served from EC2 media servers running in three regions. Viewers report inconsistent latency on live streams and no automatic failover when a region's media servers become unhealthy. The company wants to improve performance and add automatic regional failover specifically for the live-stream UDP component, without altering the CloudFront configuration that already works well for static assets. **(Choose TWO.)**
**Options:**
A. Place a Network Load Balancer per region in front of the EC2 media servers, then front all three NLBs with a single AWS Global Accelerator using health-check-based endpoint groups.
B. Migrate the live-stream UDP traffic to be served through the existing CloudFront distribution alongside the static content.
C. Configure the Global Accelerator endpoint groups' health checks to use the fast (10-second) interval so an unhealthy region's media servers are detected and traffic is failed away from as quickly as possible.
D. Increase the CloudFront distribution's cache TTL specifically for the video segment paths.
E. Add an S3 origin group with failover criteria to the CloudFront distribution for the live-stream content.
**Correct answer(s):** A, C
**Why correct:** Global Accelerator is designed exactly for this kind of non-HTTP, latency-sensitive, multi-region TCP/UDP workload — fronting regional NLBs with it (A) provides anycast entry and health-check-based routing to the nearest healthy region, and tuning the endpoint groups to the fast 10-second health-check interval (C) minimizes detection-and-failover time away from an unhealthy region, all independent of the already-working CloudFront distribution.
**Why each wrong option is wrong:** B is not technically possible — CloudFront serves HTTP(S) content and cannot carry a custom UDP protocol, and it would also risk disrupting the static-content configuration the company wants left alone; D only affects cacheable HTTP video segment delivery through CloudFront and has no bearing on the separate UDP live-stream path served from EC2; E, S3 origin groups are a CloudFront/S3 failover mechanism and are irrelevant to EC2-hosted, non-S3, UDP-based media servers.
**Trigger words:** "custom low-latency UDP-based protocol," "automatic regional failover," "without altering the CloudFront configuration."
**Underlying architectural principle:** CloudFront and Global Accelerator solve different problems and can coexist unmodified in the same architecture — CloudFront for cacheable HTTP(S) content, Global Accelerator for non-HTTP or latency-sensitive TCP/UDP traffic needing fast network-layer failover, tunable via its health-check interval.

---

### Question 158 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A healthcare analytics company must transfer large volumes of protected health information (PHI) from an on-premises data center to a VPC for a nightly batch analytics job, sustaining roughly 10 Gbps of consistent throughput. Compliance requires that the connection never traverse the public internet and that all PHI be encrypted end-to-end in transit, with a strict nightly processing window that leaves no tolerance for unpredictable network jitter.
**Options:**
A. Provision a Direct Connect dedicated connection with a private virtual interface, and enable AWS Direct Connect MACsec encryption on the connection.
B. Provision a Direct Connect dedicated connection with a private virtual interface only, since it is a private physical circuit outside the public internet.
C. Provision an AWS Site-to-Site VPN connection, since it provides built-in IPsec encryption and can be provisioned quickly.
D. Provision a Direct Connect connection with a private virtual interface, and layer a standard IPsec Site-to-Site VPN on top of it to encrypt the traffic.
**Correct answer(s):** A
**Why correct:** Direct Connect gives the private, non-internet path capable of sustaining roughly 10 Gbps. MACsec, supported on eligible 10 Gbps and 100 Gbps dedicated connections at MACsec-capable locations, provides native IEEE 802.1AE encryption at the link layer and line rate, satisfying "encrypted end-to-end in transit" without introducing the tunnel throughput ceiling or added encryption-processing overhead that an IPsec VPN would layer on top of the circuit.
**Why each wrong option is wrong:** B fails the encryption requirement outright, a Direct Connect private virtual interface alone carries traffic unencrypted at the network layer; C, Site-to-Site VPN traverses the public internet, violating the "never traverse the public internet" requirement, and each VPN tunnel is throughput-limited to roughly 1.25 Gbps, far short of the required 10 Gbps; D, while technically possible, layering a standard IPsec VPN over a Direct Connect connection still subjects the encrypted traffic to that same per-tunnel throughput ceiling (well below 10 Gbps) and adds encryption-processing latency, which directly conflicts with "no tolerance for unpredictable network jitter" — MACsec's native hardware-based encryption avoids this bottleneck entirely.
**Trigger words:** "never traverse the public internet," "encrypted end-to-end," "10 Gbps of consistent throughput," "no tolerance for unpredictable network jitter."
**Underlying architectural principle:** Direct Connect is not encrypted by default. For workloads needing both DX-class sustained high throughput and encryption in transit, native MACsec on an eligible dedicated connection avoids the bandwidth ceiling of layering a standard IPsec VPN on top of Direct Connect — VPN-over-DX remains a reasonable pattern for lower-throughput encryption needs, but doesn't fit a strict high-throughput, zero-jitter batch window.

---

### Question 159 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** Building on an existing multi-region Transit Gateway design (one Transit Gateway per region, connected via inter-region Transit Gateway peering), a company now has a strict new requirement: a PCI-compliant VPC in `us-east-1` may communicate only with one specific finance-department VPC in `eu-west-1`, and with no other VPC attached to either region's Transit Gateway — even though both the PCI VPC and the finance VPC remain attached to their regional Transit Gateways for other necessary connectivity. Auditors require this isolation to be enforced at the routing layer, not solely through security groups.
**Options:**
A. Create separate Transit Gateway route tables in each region, associate only the PCI VPC's and finance VPC's attachments with a dedicated route table containing routes only to each other, and keep them out of the route table(s) used by all other attachments.
B. Take no additional action, since Transit Gateway inter-region peering is already non-transitive beyond two hops and this isolates the PCI VPC automatically.
C. Establish a direct VPC Peering connection between the PCI VPC and the finance VPC in addition to their existing Transit Gateway attachments, and rely on security groups to block all other traffic.
D. Detach both VPCs from their Transit Gateways and connect them to each other solely through a Direct Connect Gateway.
**Correct answer(s):** A
**Why correct:** Transit Gateway route table segmentation (multiple route tables with selective attachment association and route propagation) is exactly the mechanism for restricting which attachments can reach which other attachments within a shared Transit Gateway, satisfying the auditors' routing-layer isolation requirement while leaving both VPCs' other connectivity intact.
**Why each wrong option is wrong:** B is false and dangerous — by default, attachments associated with the same (e.g., main/default) Transit Gateway route table can reach one another, so "taking no action" would leave the PCI VPC transitively reachable by every other attachment in that route table, which is the exact problem needing a fix; C adds a working reachability path between the two intended VPCs but does nothing to remove the PCI VPC's existing Transit Gateway attachment from the shared route table, so other VPCs could still transitively reach it via the Transit Gateway regardless of the new peering link; D, Direct Connect Gateway connects Direct Connect connections to VPCs/regions for on-premises hybrid connectivity, it is not a mechanism for connecting two VPCs to each other.
**Trigger words:** "may communicate only with one specific... VPC, and with no other VPC," "enforced at the routing layer, not solely through security groups."
**Underlying architectural principle:** Selective reachability between specific attachments on a shared Transit Gateway is achieved through route table segmentation (multiple route tables, controlled association/propagation), not by adding parallel connectivity paths or assuming default non-transitivity that doesn't actually exist within a single route table.

---

### Question 160 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A global fintech platform has four requirements. First, its public marketing site's static content must load in well under a second worldwide (already correctly solved with an existing CloudFront distribution — no changes needed here). Second, its trading API is HTTP-based but latency-sensitive and effectively non-cacheable, runs behind ALBs in four regions, and must route each client to the best-performing healthy region with failover measured in seconds, not dependent on DNS caching behavior. Third, a connection to an on-premises clearing-house system carrying regulatory settlement data needs a dedicated, non-internet path with a contracted bandwidth SLA and consistent sub-10ms latency. Fourth, the finance team wants to avoid provisioning redundant services where one existing service already satisfies a need. **(Choose TWO actions that best complete this architecture.)**
**Options:**
A. Deploy AWS Global Accelerator in front of the trading API's regional Application Load Balancers, using health-check-based endpoint groups for requirement two.
B. Rely solely on Route 53 latency-based routing with a very low DNS TTL configured on the trading API's record for requirement two.
C. Provision an AWS Direct Connect dedicated connection with a private virtual interface for requirement three.
D. Provision an AWS Site-to-Site VPN connection for requirement three, since it can be established faster than Direct Connect.
E. Deploy a second CloudFront distribution in front of the trading API's ALBs to reduce its failover time.
**Correct answer(s):** A, C
**Why correct:** Global Accelerator (A) provides network-layer, health-check-driven routing to the best-performing healthy regional ALB with failover in seconds, independent of DNS TTLs, directly meeting requirement two; Direct Connect (C) is the only option that can contractually guarantee dedicated bandwidth and consistent sub-10ms latency over a non-internet path for the regulated settlement data in requirement three.
**Why each wrong option is wrong:** B's failover speed is fundamentally bounded by DNS resolver caching and TTL honoring behavior across the internet, which is precisely why "not dependent on DNS caching behavior" rules it out even at a low TTL; D, a VPN traverses the public internet, so it cannot provide a contracted bandwidth SLA or guarantee consistent sub-10ms latency the way a dedicated Direct Connect circuit can; E, CloudFront caches HTTP(S) content and provides no benefit for a non-cacheable, latency-sensitive API, and adding a second distribution is also a redundant service given Global Accelerator already correctly solves requirement two — directly conflicting with requirement four.
**Trigger words:** "effectively non-cacheable," "failover measured in seconds, not dependent on DNS caching behavior," "contracted bandwidth SLA and consistent sub-10ms latency," "avoid provisioning redundant services."
**Underlying architectural principle:** A high-performing global architecture typically layers purpose-built services rather than stretching one service to cover every need: CloudFront for cacheable HTTP(S) content, Global Accelerator for latency-sensitive or non-cacheable TCP/UDP traffic needing fast network-layer failover, and Direct Connect for dedicated, SLA-backed hybrid connectivity — each solving a distinct performance problem the others cannot.

---

## Domain 4: Design Cost-Optimized Architectures (20%)

### Question 161 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs its core order database on a single EC2 instance family, in a single Region, and finance has confirmed the workload will run continuously, 24/7, for at least the next three years with no planned changes to instance family or Region. The workload cannot tolerate interruption. Finance wants the maximum possible percentage discount off On-Demand pricing and is willing to pay the full amount upfront to get it.
**Options:**
A. Keep the instance on On-Demand pricing to preserve flexibility.
B. Purchase a 3-year Standard Reserved Instance with the All Upfront payment option.
C. Move the workload to Spot Instances to reduce cost immediately.
D. Purchase a Dedicated Host for the instance.
**Correct answer(s):** B
**Why correct:** A known, unchanging, 3-year, non-interruptible workload is exactly the steady-state case Reserved Instances are priced for, and the All Upfront payment option yields the largest discount off On-Demand of any RI payment option.
**Why each wrong option is wrong:** A. On-Demand carries no commitment discount and is the most expensive option for a workload with zero uncertainty about duration or configuration. C. Spot Instances can be reclaimed with a two-minute warning, which directly violates the "cannot tolerate interruption" constraint. D. A Dedicated Host addresses physical hardware isolation/licensing needs, not cost minimization, and costs more than a Standard RI for this workload.
**Trigger words:** "continuously, 24/7," "at least the next three years," "no planned changes," "cannot tolerate interruption," "maximum possible percentage discount," "willing to pay the full amount upfront."
**Underlying architectural principle:** Match the EC2 purchasing model to how certain and how long-lived the demand is — steady, known, long-term demand should always be committed, not paid for at On-Demand rates.

---

### Question 162 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A media company runs a fleet of EC2 instances that decode and transcode uploaded video files pulled from an SQS queue. Each job can be checkpointed and safely restarted from the last checkpoint on any instance if interrupted, and jobs can start and finish at any time without a fixed deadline. The company wants the lowest possible compute cost for this fleet and has no need for guaranteed capacity availability.
**Options:**
A. Reserved Instances with a 3-year term.
B. On-Demand Instances only.
C. Spot Instances, ideally across multiple instance types and Availability Zones.
D. Dedicated Instances.
**Correct answer(s):** C
**Why correct:** The workload is explicitly fault-tolerant, checkpointed, restartable, and has no fixed deadline or capacity guarantee requirement — exactly the profile Spot Instances are designed for, offering up to ~90% savings versus On-Demand.
**Why each wrong option is wrong:** A. A 3-year Reserved Instance commitment is unnecessary and inflexible for a workload the company describes with no stated long-term steady-state need. B. On-Demand pays full price for capacity that the workload doesn't actually require guaranteed, uninterrupted access to. D. Dedicated Instances solve hardware-isolation compliance needs, not cost, and cost more than On-Demand, let alone Spot.
**Trigger words:** "checkpointed and safely restarted," "start and finish at any time without a fixed deadline," "lowest possible compute cost," "no need for guaranteed capacity."
**Underlying architectural principle:** Interruptibility is the resource you sell for the deepest EC2 discount — only trade it away for jobs truly designed to tolerate being killed and restarted.

---

### Question 163 [Priority: P1] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company is lifting-and-shifting a legacy Windows Server application whose commercial database license is billed per physical CPU socket and per physical core (bring-your-own-license). The software vendor's license terms require the customer to know and control exactly which physical server sockets/cores the software runs on, and to be able to pin the workload to the same physical host across restarts.
**Options:**
A. Dedicated Instances.
B. Dedicated Hosts.
C. Standard Reserved Instances.
D. On-Demand Instances with a placement group.
**Correct answer(s):** B
**Why correct:** Dedicated Hosts give visibility into and control over the physical server's sockets and cores and support host affinity, which is exactly what per-socket/per-core BYOL licensing requires — Dedicated Instances do not expose this host-level information.
**Why each wrong option is wrong:** A. Dedicated Instances run on single-tenant hardware but give no visibility or control over host ID, sockets, or cores, so they cannot satisfy per-socket/per-core license compliance. C. Reserved Instances are a billing/commitment model layered on top of a tenancy choice, not a tenancy or licensing solution by themselves. D. Placement groups control network/physical proximity for performance, not license-relevant host visibility or control.
**Trigger words:** "billed per physical CPU socket and per physical core," "know and control exactly which physical server," "pin the workload to the same physical host."
**Underlying architectural principle:** When the requirement is licensing tied to physical hardware attributes, only Dedicated Hosts expose the host-level visibility and control that BYOL socket/core licensing demands.

---

### Question 164 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A growing SaaS company runs EC2 workloads across several instance families in two Regions, and the mix of instance families in use changes every few months as engineering adopts newer instance generations. The company also runs a meaningful and growing amount of AWS Fargate and AWS Lambda usage. Finance wants a single, three-year committed-use discount plan that automatically applies to all of this usage without requiring any manual exchange or modification transactions when the instance mix changes.
**Options:**
A. EC2 Instance Savings Plans, one per instance family in use today.
B. Compute Savings Plans.
C. Convertible Reserved Instances, exchanged quarterly to match the current instance mix.
D. Standard Reserved Instances purchased per Region and instance family.
**Correct answer(s):** B
**Why correct:** Compute Savings Plans automatically apply their discount to EC2 usage regardless of instance family, size, OS, tenancy, or Region, and also apply to Fargate and Lambda usage, with no manual exchange step ever required — the only option matching every stated requirement.
**Why each wrong option is wrong:** A. EC2 Instance Savings Plans are locked to a specific instance family within a Region, so they would need to be repurchased whenever the family mix shifts, and they don't cover Fargate/Lambda. C. Convertible RIs can be exchanged for a different configuration, but that exchange is a manual transaction the company explicitly wants to avoid, and RIs never cover Fargate or Lambda usage. D. Standard RIs are the least flexible option and, like the others, do not extend to Fargate or Lambda.
**Trigger words:** "mix of instance families... changes every few months," "Fargate and AWS Lambda usage," "single... plan that automatically applies," "without requiring any manual exchange."
**Underlying architectural principle:** Flexibility across instance family, Region, and compute type (including serverless) is the defining strength of Compute Savings Plans versus every RI variant.

---

### Question 165 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retailer is launching a major new product in a single Availability Zone-pinned application stack and must guarantee that a specific quantity of a specific EC2 instance type will physically be available to launch in that exact AZ on launch day, regardless of what other AWS customers are doing in that AZ at the time. The company also wants a billing discount on this capacity since it will run for at least a year afterward.
**Options:**
A. A Regional Reserved Instance.
B. A Compute Savings Plan sized to the expected usage.
C. A Zonal (AZ-scoped) Reserved Instance.
D. An EC2 Instance Savings Plan scoped to the Region.
**Correct answer(s):** C
**Why correct:** Only a Zonal Reserved Instance, scoped to a specific Availability Zone, provides an actual capacity reservation guaranteeing that capacity will be available in that AZ — every other option here provides a billing discount only, with no capacity guarantee.
**Why each wrong option is wrong:** A. A Regional RI provides billing flexibility across AZs in the Region but explicitly does not reserve physical capacity in any specific AZ. B. Savings Plans, of any type, never provide a capacity reservation — they are a pure pricing/billing construct. D. An EC2 Instance Savings Plan, like all Savings Plans, provides no capacity guarantee regardless of scope.
**Trigger words:** "guarantee that a specific quantity... will physically be available," "in that exact AZ," "regardless of what other AWS customers are doing."
**Underlying architectural principle:** Capacity reservation and billing discount are separate concerns — only an AZ-scoped (zonal) Reserved Instance combines both; Savings Plans and Regional RIs are discount-only.

---

### Question 166 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A logistics company runs a nightly ETL batch job on an Auto Scaling group. The job always starts at 22:00 and finishes by 02:00, seven days a week, with virtually identical resource needs each night. Outside that window the ASG should run at a minimal baseline to save cost. The company wants capacity to be ready at exactly 22:00 without waiting for a CloudWatch metric to cross a threshold first.
**Options:**
A. A target tracking scaling policy on average CPU utilization.
B. Predictive scaling based on historical load forecasting.
C. Scheduled scaling actions that raise desired capacity just before 22:00 and lower it just after 02:00.
D. A step scaling policy triggered by SQS queue depth.
**Correct answer(s):** C
**Why correct:** Scheduled scaling lets the ASG proactively change desired/min/max capacity at a specific, known clock time — exactly matching a fixed, unvarying daily window — with zero dependency on a metric first breaching a threshold.
**Why each wrong option is wrong:** A. Target tracking only reacts once utilization changes, meaning instances would still be booting after the job's demand had already arrived, causing the exact lag the company wants to avoid. B. Predictive scaling is built for variable, ML-forecasted demand patterns; it adds unnecessary complexity for a fixed, identical daily schedule that scheduled scaling already handles precisely. D. Queue-depth-based step scaling is still reactive to a metric crossing a threshold, not proactive on a clock schedule.
**Trigger words:** "always starts at 22:00... finishes by 02:00," "virtually identical... each night," "ready at exactly 22:00 without waiting for a... metric."
**Underlying architectural principle:** When demand timing is fixed and known in advance, scheduled scaling is the cost-efficient, proactive answer — reserve metric-driven policies for demand that isn't clock-predictable.

---

### Question 167 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An online ticketing platform sees a sharp, repeating traffic surge every Monday between 08:45 and 09:30 as weekly releases go on sale, ramping from baseline to 8x baseline over about 20 minutes. New instances in the Auto Scaling group take roughly 5 minutes to become healthy. Using only target tracking, the ASG's reactive scale-out consistently lags the ramp, causing a few minutes of degraded response times every Monday. The company has over a year of CloudWatch metrics showing this exact recurring weekly pattern and wants the ASG to have extra capacity already warmed before the ramp begins each week, without hand-maintaining a fixed calendar of scaling times.
**Options:**
A. Increase the target tracking policy's target CPU value so the ASG scales out earlier.
B. Add a scheduled scaling action for every Monday at 08:40 indefinitely.
C. Enable predictive scaling on the Auto Scaling group in addition to the existing target tracking policy.
D. Switch entirely from target tracking to simple/step scaling with a shorter cooldown.
**Correct answer(s):** C
**Why correct:** Predictive scaling uses machine learning on historical CloudWatch metrics to forecast a recurring load pattern like this weekly surge and proactively scales out ahead of the forecast, layering on top of target tracking's ongoing reactive fine-tuning — directly matching "over a year of data showing this exact recurring pattern" without manual calendar maintenance.
**Why each wrong option is wrong:** A. Lowering the target threshold makes the policy trigger sooner but is still purely reactive to current metrics, not the underlying root cause of boot-time lag against a known ramp shape. B. A manually maintained weekly scheduled action works but requires ongoing manual upkeep (e.g., adjusting if the pattern shifts), which the company explicitly wants to avoid by asking for a forecast-driven approach. D. Simple/step scaling is still purely reactive to a metric breach and does not pre-provision capacity ahead of a predictable ramp.
**Trigger words:** "over a year of CloudWatch metrics showing this exact recurring weekly pattern," "already warmed before the ramp begins," "without hand-maintaining a fixed calendar."
**Underlying architectural principle:** Predictive scaling is the purpose-built answer whenever a recurring, forecastable demand pattern exists in historical data and manual schedule maintenance is explicitly unwanted — it complements, rather than replaces, reactive dynamic scaling.

---

### Question 168 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A startup is building a stateless REST API used by an internal tool. Usage is extremely uneven: some days it receives zero requests for 10+ hours at a stretch, and other days it receives a short burst of a few hundred requests per second for only a few minutes. Each request completes in well under a second and requires no persistent local state. The CTO wants to pay only for actual compute time consumed and have zero infrastructure cost during idle periods.
**Options:**
A. An ECS service on Fargate with a minimum running task count of 1, scaled by request count.
B. AWS Lambda functions behind Amazon API Gateway.
C. An Auto Scaling group of t3.micro On-Demand EC2 instances with a minimum of 1 instance.
D. An ECS service on EC2 with a single always-on instance and Auto Scaling for bursts.
**Correct answer(s):** B
**Why correct:** Lambda bills per invocation and per-millisecond of execution with no charge at all during idle time, which precisely matches "zero infrastructure cost during idle periods" for a stateless, sub-second, highly uneven-traffic workload.
**Why each wrong option is wrong:** A. A Fargate service with a minimum task count of 1 incurs continuous cost for that always-running task even during the hours of zero traffic, violating the zero-idle-cost requirement. C. An Auto Scaling group with a minimum of 1 instance keeps at least one EC2 instance running (and billed) continuously regardless of traffic. D. Running ECS on a single always-on EC2 instance has the same continuous idle-cost problem as options A and C, plus added patching/scaling overhead for the underlying host.
**Trigger words:** "zero requests for 10+ hours," "burst... for only a few minutes," "well under a second," "pay only for actual compute time consumed," "zero infrastructure cost during idle periods."
**Underlying architectural principle:** For spiky, idle-heavy, short-duration workloads, Lambda's true pay-per-invocation billing beats any option (Fargate or EC2) that requires a minimum always-on capacity floor.

---

### Question 169 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media company runs a video-encoding pipeline where each encoding job consistently takes about 35 minutes of continuous CPU-bound processing, and the pipeline runs jobs back-to-back nearly 24/7, processing hundreds of videos a day for the foreseeable future (well over a year). The workload can tolerate a job being interrupted and restarted from a checkpoint. The company wants the architecture with the lowest sustained cost per hour of compute.
**Options:**
A. AWS Lambda, using the maximum available memory/vCPU allocation to shorten each job's duration.
B. AWS Step Functions orchestrating short Lambda functions that each process a few minutes of the job and hand off state to the next function.
C. EC2 Spot Instances (with On-Demand or Reserved fallback for baseline reliability) committed via a Savings Plan for the steady-state portion.
D. Amazon API Gateway with Lambda integration and a 29-second timeout override.
**Correct answer(s):** C
**Why correct:** A single job's continuous 35-minute runtime already exceeds Lambda's hard 15-minute maximum execution timeout, ruling out any direct Lambda approach, and for sustained, near-24/7, long-running, interruption-tolerant compute over a year-plus horizon, EC2 (Spot for the fault-tolerant bulk, committed via Savings Plans for the steady baseline) is cheaper per hour than any serverless per-invocation billing model at this volume.
**Why each wrong option is wrong:** A. A single Lambda invocation is hard-capped at 15 minutes of execution time no matter how much memory/vCPU is allocated; nothing in the scenario indicates that more vCPU would cut this specific job's runtime by more than half (from 35 minutes to under 15), so betting on that unproven, unstated assumption is far riskier than an architecture with no execution-time ceiling at all. B. Splitting the job across chained Lambda functions is technically possible but adds significant orchestration complexity and still costs more than committed EC2/Spot compute at this sustained, high-volume, long-duration workload profile. D. API Gateway's request timeout is unrelated to background batch processing and, like A, is bounded by Lambda's execution limits.
**Trigger words:** "35 minutes of continuous... processing," "nearly 24/7," "hundreds of videos a day... well over a year," "can tolerate a job being interrupted," "lowest sustained cost per hour."
**Underlying architectural principle:** Lambda's 15-minute execution ceiling and per-invocation pricing make it unsuitable and non-cost-competitive for sustained, long-running, high-volume compute — that workload profile crosses over to EC2/Fargate with commitment-based and Spot discounts.

---

### Question 170 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A finance team flags that EC2 spend has grown 40% year over year. Investigation using CloudWatch shows the majority of the company's m5.2xlarge fleet averages 8% CPU utilization and under 15% memory utilization. Someone on the platform team proposes immediately locking in a 3-year All Upfront Reserved Instance commitment across the entire fleet at its current instance sizes to capture savings as fast as possible.
**Options:**
A. Proceed with the 3-year All Upfront RI purchase immediately at current instance sizes, since RIs always reduce cost regardless of utilization.
B. Use AWS Compute Optimizer (or Cost Explorer's rightsizing recommendations) to identify smaller, better-fitting instance types first, then purchase Reserved Instances or Savings Plans sized to the right-sized fleet.
C. Switch the entire fleet to Spot Instances instead of pursuing any Reserved Instance strategy.
D. Increase all instances to m5.4xlarge to reduce the total instance count needed.
**Correct answer(s):** B
**Why correct:** Committing a 3-year Reserved Instance purchase to oversized instances would lock in the waste for the full term; right-sizing first (using utilization-based recommendations) reduces the baseline need, and only then should a multi-year commitment be purchased against that smaller, accurate baseline.
**Why each wrong option is wrong:** A. Buying RIs at current oversized capacity discounts a price that's still fundamentally wasteful — it locks in 3 years of paying for CPU/memory the application doesn't use. C. Moving everything to Spot ignores the underlying utilization problem entirely and reintroduces interruption risk for a workload whose interruption tolerance was never established. D. Increasing instance size further would only worsen the already-low utilization percentages and increase cost.
**Trigger words:** "EC2 spend has grown 40%," "averages 8% CPU utilization," "immediately locking in a 3-year... commitment... to capture savings as fast as possible."
**Underlying architectural principle:** Right-size based on actual utilization data before making any multi-year commitment purchase — committing to waste only makes the waste more expensive and harder to unwind.

---

### Question 171 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A company with 500+ EC2 instances across several accounts wants to reduce compute waste organization-wide before committing to any multi-year purchase. Leadership wants this done using AWS-native tooling with minimal custom scripting, and wants recommendations that are based on actual observed utilization data rather than guesswork or blanket policy changes. Select the two actions that best satisfy these requirements.
**Options:**
A. Use AWS Compute Optimizer to generate rightsizing recommendations for EC2, Auto Scaling groups, EBS, and Lambda based on CloudWatch utilization history.
B. Immediately purchase 3-year Standard Reserved Instances for every instance at its current size to lock in savings right away.
C. Review AWS Cost Explorer's rightsizing recommendations to identify EC2 instances that are strong candidates for downsizing or family changes.
D. Convert the entire fleet to Spot Instances as a blanket policy across all workloads.
E. Manually inspect CloudWatch dashboards for each of the 500+ instances one at a time to eyeball utilization trends.
**Correct answer(s):** A, C
**Why correct:** Compute Optimizer and Cost Explorer's rightsizing recommendations are both AWS-native, ML/data-driven tools purpose-built to surface instance-level rightsizing opportunities from real utilization metrics at scale, satisfying "minimal custom scripting" and "actual observed utilization data."
**Why each wrong option is wrong:** B. Committing to 3-year RIs before rightsizing locks in whatever waste currently exists in the fleet for the full term. D. Blanket-converting every workload to Spot ignores interruption tolerance entirely and isn't a rightsizing action. E. Manually reviewing 500+ dashboards one at a time is exactly the non-scalable, custom/manual effort the company wants to avoid.
**Trigger words:** "reduce compute waste... before committing to any multi-year purchase," "AWS-native tooling with minimal custom scripting," "based on actual observed utilization data."
**Underlying architectural principle:** AWS provides two complementary, utilization-data-driven, native rightsizing tools (Compute Optimizer and Cost Explorer recommendations) that should be exhausted before any RI/Savings Plan commitment or blanket tenancy/pricing-model change is made.

---

### Question 172 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company currently runs its fleet on m5 (Intel) instances and has firmly scheduled a migration to Graviton-based m7g instances in about 9 months to cut compute cost further. Finance wants to lock in a 3-year committed-use discount today, covering both the current m5 fleet and the post-migration m7g fleet, without requiring any manual "exchange" transaction when the migration happens, and with the discount also applying to a modest amount of Fargate usage the team runs alongside it.
**Options:**
A. A 3-year Standard Reserved Instance scoped to the m5 family today, to be repurchased after the migration.
B. A 3-year Convertible Reserved Instance, exchanged for m7g RIs once the migration completes.
C. A 3-year Compute Savings Plan.
D. A 3-year EC2 Instance Savings Plan scoped to the m5 family.
**Correct answer(s):** C
**Why correct:** A Compute Savings Plan's discount applies automatically to EC2 usage regardless of instance family (m5 today, m7g after migration) and also covers Fargate usage, with no manual conversion step ever required — the only option meeting every stated condition simultaneously.
**Why each wrong option is wrong:** A. A Standard RI is locked to the m5 family; after migrating to m7g it would go unused, forcing a fresh purchase and wasting the remaining committed term. B. A Convertible RI can eventually cover m7g, but only via a manual exchange transaction the company explicitly wants to avoid, and RIs of any kind never cover Fargate usage. D. An EC2 Instance Savings Plan is locked to one instance family within a Region, so it has the identical family-lock problem as option A and still excludes Fargate.
**Trigger words:** "migration to Graviton-based m7g... in about 9 months," "covering both... without requiring any manual exchange transaction," "also applying to... Fargate usage."
**Underlying architectural principle:** When a future instance-family change is already planned and Fargate/Lambda coverage matters, Compute Savings Plans' automatic, no-exchange flexibility beats every RI variant, even Convertible RIs.

---

### Question 173 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A company runs a large fleet of stateless web-scraping workers on EC2 Spot Instances managed by an Auto Scaling group with a mixed instances policy. The group is currently configured to use only two instance types in a single Availability Zone and uses the "lowest price" Spot allocation strategy. Over the past month, interruption rates have climbed sharply, and the resulting job restarts have started to erode the cost savings versus On-Demand, even though the advertised per-hour Spot price for the chosen instance types remains low. Select the two changes that would reduce the interruption rate while still preserving most of the Spot cost savings.
**Options:**
A. Expand the mixed instances policy to include many more instance types and sizes, and spread the group across all Availability Zones in the Region.
B. Switch the Spot allocation strategy from "lowest price" to "capacity-optimized" (or "price-capacity-optimized").
C. Reduce the number of Availability Zones used to concentrate demand into a single, deep capacity pool.
D. Raise the ASG's maximum Spot price bid far above the current On-Demand price to guarantee the instances are never reclaimed.
E. Replace the Spot fleet with Dedicated Hosts to guarantee physical capacity.
**Correct answer(s):** A, B
**Why correct:** Diversifying across many instance types/sizes and AZs (A) gives the Spot allocation logic many capacity pools to draw from instead of contending for the same narrow pool, and the "capacity-optimized" strategy (B) specifically chooses instances from pools with the most available spare capacity to minimize interruption risk — both directly address interruption rate while keeping Spot pricing.
**Why each wrong option is wrong:** C. Concentrating into fewer AZs/pools does the opposite of diversification and would likely increase interruption frequency, not reduce it. D. Spot interruptions are driven by AWS needing the capacity back, not by being outbid — pricing has not worked as a competitive bidding war since 2018, so raising your maximum price does not address the root cause. E. Dedicated Hosts eliminate Spot's cost savings entirely and are a tenancy/licensing solution, not a Spot-interruption mitigation.
**Trigger words:** "only two instance types in a single Availability Zone," "'lowest price' Spot allocation strategy," "interruption rates have climbed sharply," "reduce the interruption rate while still preserving most of the Spot cost savings."
**Underlying architectural principle:** Spot interruption risk is driven by capacity-pool depth and diversity, not by price — diversify instance types/AZs and use a capacity-aware allocation strategy rather than trying to "outbid" reclamation.

---

### Question 174 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company's Lambda function is configured with 512 MB of memory and, on average, takes 4,000 ms to complete because it is CPU-bound (heavy JSON parsing and compression). Profiling shows that raising the memory allocation to 1,769 MB — which proportionally increases the share of vCPU allocated to the function, since Lambda allocates CPU power in proportion to configured memory — drops average duration to about 900 ms, because the function is far less CPU-throttled than it was at 512 MB. The function is invoked 2 million times per month. The team wants to minimize total monthly Lambda compute cost.
**Options:**
A. Keep the function at 512 MB, since higher memory always costs more regardless of duration.
B. Increase the function's memory to 1,769 MB, because the resulting drop in billed duration more than offsets the higher per-millisecond rate.
C. Split the function into two smaller Lambda functions chained together to average out the memory allocation.
D. Enable Provisioned Concurrency at 512 MB to reduce cold starts and lower cost.
**Correct answer(s):** B
**Why correct:** Lambda bills on GB-seconds (memory in GB × billed duration), so for a CPU-bound function, increasing memory (which also increases the vCPU share) can cut duration by more than the memory increase, producing lower total GB-seconds and lower total cost — a well-documented, counter-intuitive but correct Lambda cost optimization.
**Why each wrong option is wrong:** A. This ignores that cost is driven by GB-seconds, not memory setting alone; here the large duration drop (4,000ms → 900ms) more than compensates for the ~3.5x memory increase, since 512×4000 = 2,048,000 vs 1,769×900 ≈ 1,592,100 memory-milliseconds — a net decrease. C. Splitting into chained functions adds invocation overhead, orchestration cost/complexity, and doesn't address the underlying CPU-throttling cause. D. Provisioned Concurrency addresses cold-start latency (a performance concern) and adds cost — it does not address per-invocation compute duration or reduce cost here.
**Trigger words:** "CPU-bound," "proportionally increases the vCPU," "drops average duration," "minimize total monthly Lambda compute cost."
**Underlying architectural principle:** Lambda cost is a function of memory × duration, not memory alone — for CPU-bound functions, more memory (and thus more vCPU) can lower total cost by cutting duration enough to offset the higher rate.

---

### Question 175 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A healthcare company's compliance policy requires that certain workloads run on physical servers not shared with any other AWS customer, for regulatory audit purposes. There is no software licensing requirement tied to physical socket or core counts, and the company has no need to see or control the host's physical identifiers, or to pin workloads to a specific returning physical host across stop/start cycles. The company wants to satisfy the isolation requirement at the lowest additional cost over On-Demand pricing.
**Options:**
A. Dedicated Hosts.
B. Dedicated Instances.
C. Standard Reserved Instances with a tenancy of "default."
D. A placement group with tenancy set to "shared."
**Correct answer(s):** B
**Why correct:** Dedicated Instances run on hardware dedicated to a single customer, satisfying the "not shared with any other customer" audit requirement, without the extra cost and operational overhead of Dedicated Hosts, which are only necessary when host-level visibility, control, or license-driven host affinity is actually required.
**Why each wrong option is wrong:** A. Dedicated Hosts cost more and add host-level management overhead (visibility into sockets/cores, host affinity) that this scenario explicitly says isn't needed. C. A "default" tenancy Reserved Instance still runs on shared, multi-tenant hardware and does not satisfy a physical-isolation compliance requirement regardless of the RI commitment. D. Placement groups control network proximity/performance, not multi-tenancy isolation, and "shared" tenancy is the opposite of what's required here.
**Trigger words:** "physical servers not shared with any other AWS customer," "no software licensing requirement tied to physical socket or core counts," "no need to see or control the host's physical identifiers," "lowest additional cost."
**Underlying architectural principle:** Choose Dedicated Instances over Dedicated Hosts when single-tenant physical isolation is the requirement but host-level visibility/control or license-driven host affinity is not — Dedicated Hosts are the more expensive, higher-control tier reserved for that extra need.

---

### Question 176 [Priority: P2] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** Eighteen months into a 3-year, All Upfront Standard Reserved Instance commitment made for a planned data-center-exit migration project, the company cancels the remaining phases of the project. The reserved capacity (in a Region and instance family the company no longer needs) now sits completely unused for the remaining 18 months of the term, and finance wants to recover as much of the sunk cost as possible.
**Options:**
A. List and sell the remaining term of the Standard Reserved Instances on the AWS Reserved Instance Marketplace.
B. Convert the Reserved Instances into a Compute Savings Plan to redirect the discount elsewhere.
C. Request AWS terminate the RI early and issue a partial refund for unused months.
D. Exchange the Standard RIs for Convertible RIs in a different instance family that's still in use, at no cost.
**Correct answer(s):** A
**Why correct:** The AWS Reserved Instance Marketplace exists specifically to let customers sell the remaining term of unused Standard Reserved Instances to other AWS customers, allowing partial recovery of the upfront cost — this option is only available for Standard RIs.
**Why each wrong option is wrong:** B. Reserved Instances cannot be converted into a Savings Plan — the two are entirely separate commercial constructs with no conversion path between them. C. AWS does not refund unused portions of an All Upfront RI commitment upon voluntary cancellation; the commitment is non-refundable outside the RI Marketplace resale path. D. Only Convertible RIs can be exchanged for different configurations — Standard RIs are not eligible for the exchange feature, only for resale on the Marketplace.
**Trigger words:** "3-year, All Upfront Standard Reserved Instance," "cancels the remaining phases," "sits completely unused," "recover as much of the sunk cost as possible."
**Underlying architectural principle:** Standard RIs, unlike Convertible RIs or Savings Plans, can be resold on the Reserved Instance Marketplace — this is the one purchasing-model detail with a genuine secondary-market exit path.

---

### Question 177 [Priority: P0] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** An e-commerce company's order-processing tier must run continuously and cannot tolerate interruption; it holds steady at 50 EC2 instances 24/7, and finance has confirmed this baseline will remain unchanged for at least three years. A separate, unrelated nightly fraud-detection analytics tier runs fully fault-tolerant, checkpointed batch jobs and scales unpredictably between 0 and 150 instances each night depending on transaction volume. Select the two purchasing decisions that minimize total cost while respecting each tier's availability requirements.
**Options:**
A. Purchase a 3-year Compute Savings Plan sized to the order-processing tier's confirmed 50-instance steady baseline.
B. Run the order-processing tier's baseline on On-Demand Instances to preserve maximum flexibility.
C. Run the fraud-detection analytics tier on diversified Spot Instances (multiple instance types/AZs, capacity-optimized allocation) sized dynamically to nightly demand.
D. Purchase 3-year Standard Reserved Instances for the fraud-detection tier sized to its peak of 150 instances.
E. Run the fraud-detection tier on Dedicated Hosts to guarantee capacity every night.
**Correct answer(s):** A, C
**Why correct:** The order-processing tier's confirmed, unchanging 3-year steady-state baseline is exactly what a Savings Plan should cover (A), while the fraud-detection tier's fault-tolerant, highly variable nightly demand is exactly what diversified Spot Instances are priced and designed for (C) — matching each tier's purchasing model to its actual demand and interruption-tolerance profile.
**Why each wrong option is wrong:** B. On-Demand for a confirmed, unchanging 3-year steady baseline leaves a large, avoidable discount on the table for no real flexibility benefit, since the requirement is already fixed. D. Sizing a Reserved Instance commitment to the fraud tier's peak (150) would pay for RIs sitting idle most nights when actual demand is far below peak, and RIs provide no benefit for a workload whose whole value proposition is tolerating interruption cheaply via Spot. E. Dedicated Hosts are a tenancy/licensing solution, not a cost-minimization one, and are far more expensive than Spot for a fault-tolerant, bursty batch workload with no stated licensing or physical-isolation need.
**Trigger words:** "must run continuously and cannot tolerate interruption... confirmed... for at least three years," "fully fault-tolerant, checkpointed batch jobs," "scales unpredictably between 0 and 150."
**Underlying architectural principle:** Real-world fleets are almost never single-purchasing-model — the cost-optimal architecture layers a commitment discount (RI/Savings Plan) under the confirmed non-interruptible steady floor and Spot under the fault-tolerant, bursty ceiling.

---

### Question 178 [Priority: P1] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company's normalized EC2 usage never drops below 80 units/hour (a guaranteed trough that holds for 8 months of the year) but averages 115 units/hour overall because of a predictable 4-month seasonal peak that reaches up to 160 units/hour. Finance is deciding how to size the hourly dollar commitment for a 3-year, No Upfront Compute Savings Plan, and understands that any committed amount not consumed in a given hour is billed anyway and does not roll over or carry forward to other hours.
**Options:**
A. Size the Savings Plan commitment to the 115 units/hour average usage, since that best reflects typical demand.
B. Size the Savings Plan commitment to the 160 units/hour seasonal peak, to maximize the discount captured.
C. Size the Savings Plan commitment to the 80 units/hour guaranteed trough, and cover all usage above that floor with On-Demand (or Spot, where workload characteristics allow) pricing.
D. Purchase a 3-year Standard Reserved Instance sized to the 115 units/hour average instead, since RIs don't have this hourly commitment mechanic.
**Correct answer(s):** C
**Why correct:** Because unused Savings Plan commitment in any given hour is billed but not refunded or carried forward, sizing the commitment to the one number that is guaranteed to be consumed every single hour of the year — the 80 units/hour trough — avoids ever paying for committed-but-unused capacity, while the variable amount above the trough is covered at On-Demand/Spot rates only when actually needed.
**Why each wrong option is wrong:** A. Sizing to the 115 average guarantees that during every hour of the 8-month trough period (usage at 80, commitment at 115), the company pays for 35 units/hour of commitment it never uses. B. Sizing to the 160 peak is even worse — it guarantees substantial unused, non-refundable commitment during the 8-month trough and even during much of the 4-month peak period itself. D. Standard RIs have the same "pay for it whether you use it or not" commitment mechanic as Savings Plans (a reserved instance-hour not used is still paid for) — the RI/Savings Plan choice is orthogonal to this sizing problem, and it doesn't avoid the fundamental oversizing error.
**Trigger words:** "never drops below 80 units/hour... guaranteed trough," "any committed amount not consumed in a given hour is billed anyway and does not roll over."
**Underlying architectural principle:** Size any hourly commitment-based discount (RI or Savings Plan) to the workload's guaranteed floor, not its average or peak, and let elastic, uncommitted pricing absorb everything above that floor.

---

### Question 179 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company is about to purchase a large 3-year Compute Savings Plan sized to its EC2 fleet's current hourly spend. Separately, and unrelated to the Savings Plan decision, a re-platforming project scheduled to complete in about 6 months will migrate 40% of the fleet to smaller, cheaper Graviton-based instance types, which is projected to reduce the fleet's total hourly EC2 spend by roughly 25% once complete — with total instance count and workload demand otherwise unchanged. The team debates whether the re-platforming timeline should affect how the Savings Plan purchase is sized today.
**Options:**
A. It doesn't matter — Compute Savings Plans apply regardless of instance family or size, so sizing to current spend is safe no matter what happens during the re-platforming.
B. Size the Savings Plan's hourly commitment to the fleet's projected post-re-platforming hourly spend (about 25% lower), not its current pre-migration spend.
C. Size the Savings Plan to current spend, then plan to exchange it for a smaller Savings Plan once the migration completes.
D. Delay the Savings Plan purchase decision by a full year to be extra safe, forgoing any discount in the meantime.
**Correct answer(s):** B
**Why correct:** A Compute Savings Plan commitment is a fixed hourly dollar amount, not a fixed number of instances or instance-hours — while it's flexible about which instance family/size satisfies it, it does not adjust itself if the fleet's total hourly dollar spend genuinely drops; sizing to current (pre-migration) spend would leave the company overcommitted and paying for unused commitment for the remaining ~2.5 years after the migration completes.
**Why each wrong option is wrong:** A. This confuses Savings Plans' flexibility across instance family/size/OS (true) with immunity from the fleet's total hourly-dollar-spend changing (false) — the commitment is a dollar figure, and a 25% drop in hourly spend after migration would exceed what that flexibility can absorb. C. Savings Plans, unlike Convertible RIs, have no exchange mechanism at all — a Savings Plan commitment cannot be resized or exchanged mid-term. D. Delaying a full year unnecessarily forgoes ~6 months of achievable discount on the pre-migration baseline that could have been captured by simply sizing correctly today.
**Trigger words:** "3-year Compute Savings Plan sized to... current hourly spend," "reduce the fleet's total hourly EC2 spend by roughly 25%," "whether the re-platforming timeline should affect how the... purchase is sized."
**Underlying architectural principle:** Savings Plan flexibility covers *which* resources satisfy the commitment, not *how much* total hourly spend exists — a known future change in aggregate spend must be reflected in the commitment size, since the commitment itself cannot later be resized or exchanged.

---

### Question 180 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A company runs three workloads: (1) a non-interruptible order-processing application on EC2 holding a steady, confirmed 3-year baseline; (2) a stateless image-resizing function invoked unpredictably — mostly idle, with occasional sub-second bursts during promotions; and (3) a nightly, fully fault-tolerant video-encoding batch where each job runs continuously for about 35 minutes. Select the two statements below that describe correct, cost-optimal decisions for this environment.
**Options:**
A. The video-encoding batch cannot run directly on Lambda at all, because a single 35-minute continuous job exceeds Lambda's 15-minute maximum execution timeout — EC2 or Fargate must handle that tier regardless of relative cost.
B. The image-resizing workload should be moved off Lambda onto EC2 Reserved Instances, since a multi-year commitment discount always beats Lambda's per-invocation pricing at any volume.
C. A 3-year Compute Savings Plan should be purchased sized to the order-processing tier's confirmed steady baseline.
D. The order-processing tier should be moved to Spot Instances, since Spot always yields the greatest overall savings regardless of interruption tolerance.
E. The video-encoding batch should run on continuously-running On-Demand instances sized for peak nightly load and left on 24/7 for operational simplicity.
**Correct answer(s):** A, C
**Why correct:** A is a hard technical constraint (Lambda's 15-minute timeout makes it structurally unusable for a single continuous 35-minute job, independent of cost), and C correctly matches a confirmed, non-interruptible, unchanging 3-year baseline to a committed-use discount — both are unambiguously correct architectural decisions for their respective tiers.
**Why each wrong option is wrong:** B. This is backwards — the image-resizing workload is exactly the idle-heavy, sub-second, unpredictable-burst profile Lambda is cheapest for; forcing it onto always-on Reserved Instances would pay for continuous capacity the mostly-idle workload doesn't need. D. Spot Instances can be reclaimed with a two-minute warning, which is fundamentally incompatible with the order-processing tier's explicit non-interruptible requirement — cost savings can never override a hard availability constraint that a purchasing option can't satisfy. E. Leaving On-Demand instances running 24/7 for a workload that is explicitly nightly-only and fault-tolerant wastes money for roughly two-thirds of the day and ignores that Spot is the appropriate, much cheaper fit for this exact fault-tolerant batch profile.
**Trigger words:** "each job runs continuously for about 35 minutes," "confirmed 3-year baseline," "mostly idle, with occasional sub-second bursts," "non-interruptible," "fully fault-tolerant."
**Underlying architectural principle:** Cost optimization requires matching each workload's own interruption tolerance, duration profile, and demand predictability to the purchasing/compute model built for it — a single "cheapest option" never applies uniformly across a mixed environment.

---

### Question 181 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A hospital network must retain de-identified patient billing records for 10 years to satisfy a regulatory retention requirement. The records are essentially never accessed after the first 90 days, and on the rare occasion legal or compliance needs a record, waiting up to 12 hours for retrieval is explicitly acceptable per the company's documented retention policy. The compliance team's only stated priority is achieving the lowest possible per-GB monthly storage cost for this data.
**Options:**
A. S3 Standard-IA
B. S3 Glacier Instant Retrieval
C. S3 Glacier Deep Archive
D. S3 Intelligent-Tiering
**Correct answer(s):** C
**Why correct:** A 10-year regulatory retention requirement with essentially no access after 90 days and an explicitly acceptable retrieval time of up to 12 hours is the exact profile S3 Glacier Deep Archive is built for, and it offers the lowest per-GB storage cost of any S3 storage class.
**Why each wrong option is wrong:** A. S3 Standard-IA is priced for data still needing millisecond retrieval and is materially more expensive per GB than Deep Archive for data that will sit untouched for years. B. Glacier Instant Retrieval is for archive data still needing millisecond access (e.g., accessed quarterly), which costs more than Deep Archive and isn't needed given the explicit 12-hour retrieval tolerance. D. Intelligent-Tiering is priced and designed for unknown/changing access patterns with a monitoring fee — this data's pattern (near-zero access after 90 days) is already known, so a static lifecycle transition to Deep Archive beats Intelligent-Tiering's per-object monitoring overhead on cost.
**Trigger words:** "retain... for 10 years," "essentially never accessed after the first 90 days," "waiting up to 12 hours... explicitly acceptable," "lowest possible per-GB monthly storage cost."
**Underlying architectural principle:** When retrieval-time tolerance is explicit and generous and the access pattern is already known to be near-zero, always route to the cheapest storage tier compatible with that stated tolerance rather than a tier priced for faster access you don't need.

---

### Question 182 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A startup is launching a brand-new mobile app backend on DynamoDB with no historical traffic data to reference. Usage could range from a handful of requests per day during a slow beta period to an unpredictable viral spike of thousands of requests per second if a launch post goes viral on social media, and the team has no engineering time to build or tune capacity-planning automation before launch. Leadership's primary concern is avoiding both throttling during a surprise spike and paying for idle provisioned capacity during quiet periods.
**Options:**
A. Provisioned capacity mode with a fixed RCU/WCU value set conservatively low to control cost.
B. Provisioned capacity mode with Application Auto Scaling configured from day one.
C. On-Demand capacity mode.
D. Provisioned capacity mode with a fixed RCU/WCU value set high enough to cover the largest anticipated viral spike, paid for continuously regardless of actual traffic.
**Correct answer(s):** C
**Why correct:** On-Demand capacity mode requires no capacity planning, scales instantly to absorb unpredictable request-rate changes (including a viral spike), and bills only for actual reads/writes consumed — directly matching "no historical traffic data," "no engineering time to tune," and "avoid paying for idle capacity."
**Why each wrong option is wrong:** A. A fixed, conservatively low provisioned value guarantees throttling the moment traffic exceeds that ceiling, which is precisely the outcome leadership wants to avoid. B. Auto Scaling on provisioned capacity still reacts to CloudWatch metric thresholds with a lag, and tuning its scaling policy well is exactly the "engineering time" the team says it doesn't have before launch. D. Provisioning a fixed ceiling high enough to survive a hypothetical viral spike means paying for that ceiling around the clock, including the long quiet stretches when traffic is near zero — the opposite of "avoid paying for idle provisioned capacity," and it still requires guessing a numeric ceiling for a workload with zero historical data to base that guess on.
**Trigger words:** "no historical traffic data," "unpredictable viral spike," "no engineering time... before launch," "avoiding both throttling... and paying for idle provisioned capacity."
**Underlying architectural principle:** DynamoDB On-Demand is the correct default for new, unproven, or highly unpredictable workloads — Provisioned (with or without Auto Scaling) only becomes the cheaper choice once real, steady traffic data justifies committing to a capacity level.

---

### Question 183 [Priority: P0] [Difficulty: Easy] [Type: Single-Answer]
**Scenario:** A company runs a fleet of EC2 instances in private subnets that need to read and write objects in Amazon S3 buckets located in the same Region. There is no requirement to reach S3 from on-premises networks, from a different Region, or from outside the VPC in any way. The team wants to remove this S3 traffic from its NAT Gateway (to eliminate the associated NAT data-processing charges for this traffic) at the lowest possible additional cost.
**Options:**
A. Add an Interface VPC Endpoint (PrivateLink) for S3.
B. Add a Gateway VPC Endpoint for S3.
C. Deploy a second NAT Gateway in each Availability Zone dedicated to S3 traffic.
D. Assign public IP addresses to the EC2 instances and route S3 traffic through the Internet Gateway instead of NAT.
**Correct answer(s):** B
**Why correct:** A Gateway VPC Endpoint for S3 has no hourly or per-GB charge, works entirely within the constraints described (same-Region, from within the VPC only), and removes S3 traffic from the NAT Gateway's billed data path entirely — the lowest-cost option that fully satisfies every stated constraint.
**Why each wrong option is wrong:** A. An Interface VPC Endpoint for S3 works but incurs hourly and per-GB PrivateLink charges, making it a strictly more expensive choice than the free Gateway Endpoint when the Gateway Endpoint's constraints (same-Region, VPC-only access) are already satisfied. C. Adding more NAT Gateways only multiplies the hourly NAT charge and does nothing to remove or reduce the per-GB data-processing fee this traffic generates. D. Assigning public IPs and routing via the Internet Gateway trades one cost (NAT data processing) for another (public IPv4 address charges and internet data transfer) while also removing the private-subnet security posture, and doesn't uniquely solve the cost problem.
**Trigger words:** "same Region," "no requirement to reach S3 from on-premises... or outside the VPC," "remove this... traffic from its NAT Gateway," "lowest possible additional cost."
**Underlying architectural principle:** Whenever private-subnet resources need only same-Region access to S3 or DynamoDB, a free Gateway VPC Endpoint is always the cost-optimal way to remove that traffic from NAT Gateway billing — reach for the paid Interface Endpoint only when Gateway Endpoint's constraints genuinely can't be met.

---

### Question 184 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An application writes structured audit logs to S3 with a well-documented, predictable access pattern: logs are read frequently by a compliance dashboard for the first 30 days, read only occasionally (a few times) between day 30 and day 90 for periodic audits, and after day 90 are essentially never read again but must be retained for 3 more years for legal reasons. The platform team wants this cost optimization automated with no ongoing manual intervention and no per-object monitoring fee.
**Options:**
A. Enable S3 Intelligent-Tiering on the bucket and let it handle all the transitions automatically.
B. Configure an S3 Lifecycle rule that transitions objects to S3 Standard-IA at 30 days and to S3 Glacier Flexible Retrieval (or Deep Archive) at 90 days.
C. Write a scheduled Lambda function that runs nightly, inspects object age, and calls CopyObject to move objects between storage classes manually.
D. Store all logs in S3 Glacier Deep Archive from the moment they're written, since that has the lowest baseline storage cost.
**Correct answer(s):** B
**Why correct:** The access pattern here is fully known and predictable (hot for 30 days, warm for 60 more, cold indefinitely after), which is exactly the case a native S3 Lifecycle rule is designed to automate cheaply and permanently — no per-object monitoring fee, no custom code, and no manual intervention once configured.
**Why each wrong option is wrong:** A. Intelligent-Tiering is priced for the opposite situation — unknown or unpredictable per-object access patterns — and its small monthly monitoring fee per object is pure waste when the aging curve is already fully known in advance, as it is here. C. A custom Lambda-based mover reinvents a feature S3 already provides natively for free, adding operational cost, code to maintain, and Lambda invocation charges for no benefit over a native Lifecycle rule. D. Storing logs in Deep Archive immediately would make the frequent day-0-to-30 compliance dashboard reads either impossible at the needed speed or extremely expensive due to Deep Archive's hours-long retrieval time and higher retrieval fees for frequently accessed data.
**Trigger words:** "well-documented, predictable access pattern," "essentially never read again but must be retained," "automated with no ongoing manual intervention," "no per-object monitoring fee."
**Underlying architectural principle:** Native S3 Lifecycle rules, not Intelligent-Tiering and not custom automation, are the correct answer whenever an object's access-pattern decay curve over time is already known — Intelligent-Tiering exists specifically for the cases where that curve is unknown.

---

### Question 185 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A retailer's order-history table on DynamoDB has run in production for over a year. CloudWatch metrics show consistent, predictable daily and weekly traffic cycles (higher during business hours, lower overnight, a known weekly peak on Mondays) with utilization comfortably within a well-understood, gradually growing range. Finance has asked the platform team to reduce the table's monthly DynamoDB bill without introducing throttling risk or requiring a full re-architecture.
**Options:**
A. Switch the table to On-Demand capacity mode to guarantee no throttling regardless of traffic pattern.
B. Switch the table to Provisioned capacity mode with Application Auto Scaling configured against the well-understood historical traffic range.
C. Enable DynamoDB Accelerator (DAX) in front of the table to reduce the number of billed read requests.
D. Keep On-Demand mode but request a support-ticket-based discount from AWS based on consistent usage.
**Correct answer(s):** B
**Why correct:** A year of consistent, predictable, cyclical traffic with a well-understood range is exactly the profile where Provisioned capacity (with Auto Scaling layered on top to absorb the known daily/weekly swings without manual re-tuning) costs meaningfully less per request than On-Demand, while Auto Scaling protects against the throttling risk finance wants to avoid.
**Why each wrong option is wrong:** A. On-Demand already eliminates throttling risk today, but it charges a premium per request that isn't justified once the traffic pattern is well-understood and predictable — this option doesn't address the cost-reduction ask at all. C. DAX reduces read *latency* via caching, but reads that hit the cache are typically driven by application read-through logic and DAX itself has its own hourly node cost — it doesn't restructure DynamoDB's underlying capacity billing model the way switching capacity modes does, and isn't the direct lever for this specific cost problem. D. DynamoDB has no such ad hoc negotiated-discount mechanism tied to a support ticket; the only way to pay less per request is to actually change capacity mode (as option B proposes), not to ask for a discount while remaining on On-Demand.
**Trigger words:** "run in production for over a year," "consistent, predictable daily and weekly traffic cycles," "well-understood... range," "reduce... bill without introducing throttling risk."
**Underlying architectural principle:** Once real production data proves a workload's traffic is steady and predictable, Provisioned capacity with Auto Scaling becomes the cost-optimal DynamoDB choice — On-Demand's premium exists specifically to buy freedom from that kind of capacity planning, and that premium stops paying for itself once the planning is easy.

---

### Question 186 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An analytics dashboard backed by an Amazon Aurora MySQL cluster is experiencing degraded performance because read query volume has grown steadily and now saturates the single writer instance's CPU during business hours, even though write volume itself remains low and unchanged. The engineering team wants the most cost-effective way to relieve this specific read bottleneck without altering the application's write path or its disaster-recovery posture.
**Options:**
A. Add one or more Aurora Replicas to the cluster and point the read-heavy dashboard queries at the cluster's reader endpoint.
B. Convert the entire Aurora cluster (writer included) to Aurora Serverless v2.
C. Rely on the Multi-AZ standby instance to absorb some of the read queries.
D. Vertically resize the writer instance to the next larger instance class.
**Correct answer(s):** A
**Why correct:** Aurora Replicas share the cluster's underlying storage volume (so there's no separate replication lag mechanism to manage) and are specifically designed to absorb read traffic via the reader endpoint's automatic load balancing, directly and cheaply relieving a read-only bottleneck without touching the write path.
**Why each wrong option is wrong:** B. Converting the whole cluster to Serverless v2 is a much larger architectural change than the read-bottleneck problem calls for, and since write volume is low and unchanged, most of that migration's benefit would go unused while adding scaling behavior the team didn't ask to change. C. Aurora does not have a separate non-readable "standby" instance the way traditional Single-AZ/Multi-AZ RDS deployments do — in Aurora, both high availability and read scaling come from Aurora Replicas, and the scenario explicitly describes only a single writer instance with no replicas yet provisioned. There is no existing standby to route queries to here; the real fix is to explicitly provision one or more Aurora Replicas, which is exactly what option A does. D. Vertically resizing the writer pays for more CPU capacity 24/7 (including the low-write, low-read overnight hours) purely to fix a read-only bottleneck that only occurs during business hours — Aurora Replicas scoped to the actual bottleneck are cheaper and more targeted.
**Trigger words:** "read query volume has grown... saturates the... writer instance's CPU," "write volume itself remains low and unchanged," "most cost-effective way to relieve this specific read bottleneck."
**Underlying architectural principle:** A read-only bottleneck should be solved by adding read capacity (Aurora Replicas) scoped to reads, not by paying more for the writer's compute or re-architecting the entire cluster's scaling model.

---

### Question 187 [Priority: P0] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A cost review flags that a company's NAT Gateway data-processing charges have grown to be one of the largest line items on its monthly AWS bill. Investigation traces the bulk of this traffic to a fleet of Lambda functions running inside private subnets that make frequent GetItem/PutItem calls to DynamoDB tables in the same Region and account. No other destinations account for a meaningful share of the NAT Gateway's processed data.
**Options:**
A. Increase the memory allocated to the Lambda functions so each invocation completes faster and generates less NAT-processed data.
B. Add a Gateway VPC Endpoint for DynamoDB to the VPC's route tables.
C. Move the Lambda functions out of the VPC entirely so they no longer route through NAT.
D. Add an Interface VPC Endpoint (PrivateLink) for DynamoDB.
**Correct answer(s):** B
**Why correct:** DynamoDB is one of only two services (along with S3) supported by the free Gateway VPC Endpoint type, and adding it removes essentially all of this same-Region DynamoDB traffic from the NAT Gateway's billed data path at no additional hourly or per-GB cost — directly and fully addressing the described cost driver.
**Why each wrong option is wrong:** A. Lambda memory/duration affects Lambda's own GB-second billing, not the volume of network traffic traversing NAT Gateway per DynamoDB API call — this doesn't address the NAT data-processing charge at all. C. Removing the functions from the VPC would only be viable if they don't need private-subnet-only resources for anything else, and even where viable, it's a bigger architectural change than necessary when a Gateway Endpoint solves the described problem directly and for free. D. An Interface Endpoint for DynamoDB works technically but incurs its own hourly and per-GB PrivateLink charges, which is strictly worse on cost than the free Gateway Endpoint when the traffic is same-Region DynamoDB access, exactly the case the Gateway Endpoint is built for.
**Trigger words:** "NAT Gateway data-processing charges have grown," "frequent... calls to DynamoDB tables in the same Region," "no other destinations account for a meaningful share."
**Underlying architectural principle:** When NAT Gateway cost is traced specifically to S3 or DynamoDB traffic, the fix is always a free Gateway VPC Endpoint for that service — never a NAT Gateway resize, a Lambda tuning change, or a more expensive Interface Endpoint.

---

### Question 188 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** Two backend services in the same VPC and the same Availability Zone exchange a very high volume of data every minute as part of a real-time processing pipeline. A cost review reveals a meaningful and unexpected data-transfer charge tied to this traffic, even though both services run in the same AZ, which the engineering team had assumed meant the traffic would be free. Investigation shows the calling service was configured to reach the other service using its public Elastic IP address rather than its private VPC IP address.
**Options:**
A. Move one of the two services to a different Availability Zone to isolate the traffic cost.
B. Reconfigure the calling service to address the other service using its private IP address (or private DNS name) instead of its public Elastic IP address.
C. Request an AWS Support case to waive the same-AZ data-transfer charge, since it should already be free.
D. Attach a NAT Gateway between the two services to route the traffic through a single metered path.
**Correct answer(s):** B
**Why correct:** Data transfer between two resources in the same Availability Zone over private IP addresses is free, but the same traffic routed over a public or Elastic IP address is billed even within the same AZ — switching the calling service to address its peer by private IP directly eliminates the unexpected charge while keeping both services exactly where they are.
**Why each wrong option is wrong:** A. Moving a service to a different AZ would introduce cross-AZ data-transfer charges, which are higher than the same-AZ public-IP charge being incurred now — this makes the cost problem worse, not better. C. This isn't a billing error to dispute; AWS's documented pricing already treats same-AZ traffic over public/Elastic IPs as billable, so no waiver applies, and the actual fix is architectural. D. Introducing a NAT Gateway between two resources that are already in the same VPC adds its own hourly and per-GB charges and is not how intra-VPC service-to-service traffic should ever be routed.
**Trigger words:** "same Availability Zone," "unexpected data-transfer charge," "assumed... would be free," "using its public Elastic IP address rather than its private VPC IP address."
**Underlying architectural principle:** "Same AZ" alone does not guarantee free data transfer — the free tier applies specifically to same-AZ traffic over private IP addresses, so intra-VPC services should always address each other privately, never via public or Elastic IPs.

---

### Question 189 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** A media-sharing platform stores millions of user-uploaded photos and videos in S3. Access behavior per object is highly unpredictable: some objects go viral and are accessed thousands of times within days, most receive only a handful of views and then go quiet, and a small number that appeared dormant for months suddenly get accessed heavily again when re-shared. The platform absolutely cannot tolerate a per-GB retrieval fee being charged unexpectedly when a dormant object suddenly becomes popular again, since that unpredictability has caused billing surprises in the past.
**Options:**
A. Configure an S3 Lifecycle rule transitioning all objects to S3 Standard-IA after 30 days of no access.
B. Enable S3 Intelligent-Tiering on the bucket.
C. Configure an S3 Lifecycle rule transitioning all objects to S3 One Zone-IA after 30 days of no access.
D. Manually re-classify objects into different storage classes based on weekly view-count reports.
**Correct answer(s):** B
**Why correct:** S3 Intelligent-Tiering is purpose-built for exactly this scenario — objects with genuinely unknown, changing access patterns — automatically moving objects between frequent- and infrequent-access tiers based on observed usage with no retrieval fees at all, which directly eliminates the billing-surprise risk from a dormant object suddenly being re-accessed.
**Why each wrong option is wrong:** A. S3 Standard-IA charges a per-GB retrieval fee every time an object is read; a dormant object going viral again after being moved to Standard-IA would trigger exactly the unpredictable retrieval-fee billing surprise the platform explicitly wants to avoid. C. One Zone-IA has the same retrieval-fee structure as Standard-IA (plus reduced redundancy, inappropriate for irreplaceable user uploads), so it carries the identical billing-surprise risk as option A. D. Manually re-classifying millions of objects weekly based on view-count reports is operationally unscalable and still can't react fast enough to prevent a retrieval-fee event on an object that goes viral between reporting cycles.
**Trigger words:** "highly unpredictable" per object, "dormant for months suddenly get accessed heavily again," "cannot tolerate a per-GB retrieval fee being charged unexpectedly."
**Underlying architectural principle:** Whenever a scenario explicitly rules out retrieval-fee risk on top of an unpredictable access pattern, S3 Intelligent-Tiering is the only storage-class strategy that satisfies both constraints simultaneously — IA-family classes and manual reclassification both reintroduce the exact risk being avoided.

---

### Question 190 [Priority: P1] [Difficulty: Medium] [Type: Single-Answer]
**Scenario:** An engineering organization maintains a dozen separate Aurora PostgreSQL clusters, one per feature team, used exclusively for development and integration testing. Usage is sporadic: most clusters see active queries only during a portion of the workday when a given team is actively testing, with long idle stretches overnight, on weekends, and between sprints. The organization wants to minimize the combined cost of these dev/test clusters without giving up full Aurora PostgreSQL compatibility or asking engineers to remember to manually stop and start databases.
**Options:**
A. Keep each cluster on a small provisioned instance class running continuously, since it's already the smallest available size.
B. Migrate each dev/test cluster to Aurora Serverless v2, allowing capacity to scale down automatically (including toward zero ACUs) during idle periods.
C. Purchase 1-year Reserved Instance pricing for each cluster's provisioned instance to lock in a discount.
D. Consolidate all twelve teams' schemas onto a single shared, larger provisioned Aurora instance running continuously.
**Correct answer(s):** B
**Why correct:** Aurora Serverless v2 automatically scales compute capacity up when a team is actively testing and back down — including toward zero ACUs — during the long idle stretches described, which directly minimizes cost for sporadic, idle-heavy dev/test usage while preserving full Aurora PostgreSQL feature compatibility and requiring no manual stop/start action from engineers.
**Why each wrong option is wrong:** A. Even the smallest provisioned instance class still bills continuously 24/7 regardless of the long idle periods described, wasting money for all the hours no team is actively testing. C. A 1-year Reserved Instance commitment is priced for steady, predictable, continuous usage — locking in a discount on a workload that's explicitly sporadic and idle-heavy still pays for capacity that sits unused most of the time. D. Consolidating twelve teams onto one shared, always-on instance removes each team's isolation (a real operational and testing-safety concern) and still runs continuously regardless of aggregate idle time, rather than scaling down when nobody is actively testing.
**Trigger words:** "development and integration testing," "sporadic," "long idle stretches overnight, on weekends," "minimize... cost... without giving up full Aurora... compatibility or asking engineers to remember to manually stop and start."
**Underlying architectural principle:** Aurora Serverless v2's auto-scale-to-near-zero behavior is the standard cost answer for intermittent, idle-heavy database workloads (dev/test, low-traffic apps) where a continuously running provisioned instance — discounted or not — would otherwise pay for idle time.

---

### Question 191 [Priority: P1] [Difficulty: Medium] [Type: Multiple-Response]
**Scenario:** A company ingests millions of small objects into an S3 bucket every day via a data pipeline that occasionally experiences network interruptions mid-upload. A cost review shows the bucket's total storage size and bill have been climbing noticeably faster than the growth in objects the application itself reports having successfully written, and separately, the team has a known, predictable access-decay pattern for successfully written objects (hot for 14 days, rarely touched after). Select the two actions that directly and correctly address these findings.
**Options:**
A. Add a Lifecycle rule that uses `AbortIncompleteMultipartUpload` to automatically clean up abandoned multipart upload parts left behind by interrupted uploads.
B. Add a Lifecycle rule that transitions successfully written objects to a cheaper storage class after the known 14-day hot period ends.
C. Enable S3 Versioning on the bucket to protect against the interrupted uploads causing data loss.
D. Increase the bucket's default encryption from SSE-S3 to SSE-KMS to get better cost visibility per object.
E. Disable multipart upload for this pipeline entirely so interrupted uploads can no longer occur.
**Correct answer(s):** A, B
**Why correct:** Interrupted multipart uploads leave behind incomplete parts that continue to incur storage charges indefinitely without ever appearing as a "successful" object in application logs — exactly matching the described storage-growth-vs-reported-object-growth gap — and `AbortIncompleteMultipartUpload` (A) is the native lifecycle action built to clean these up; separately, the bucket's known, predictable 14-day hot/cold access pattern (B) is exactly the case a standard Lifecycle transition rule is designed to automate.
**Why each wrong option is wrong:** C. Versioning protects against accidental overwrite/deletion of completed objects — it does nothing to reclaim or prevent the storage cost of abandoned incomplete multipart parts, and would add its own noncurrent-version storage cost on top. D. Switching encryption type changes how objects are encrypted, not what's tracked or billed for storage, and provides no per-object cost visibility feature by itself. E. Multipart upload is required for large objects (mandatory above 5 GB, recommended above 100 MB) and disabling it doesn't fix the underlying interruption problem — network interruptions would instead cause full single-PUT failures, and the abandoned-parts problem already accumulated would still need cleanup.
**Trigger words:** "occasionally experiences network interruptions mid-upload," "climbing noticeably faster than the growth in objects the application itself reports," "known, predictable access-decay pattern... hot for 14 days, rarely touched after."
**Underlying architectural principle:** Unexplained S3 storage growth beyond an application's own reported object count is a classic signature of abandoned multipart upload parts, cleaned up via `AbortIncompleteMultipartUpload`; this is independent from and complementary to ordinary Lifecycle transition rules for known access-decay patterns.

---

### Question 192 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A logistics company's DynamoDB table supporting its shipment-tracking API has now run in production for 14 months on On-Demand capacity mode. CloudWatch metrics for that entire period show request volume holding within a narrow, predictable band that grows slowly and linearly month over month, with no unexpected spikes ever recorded and utilization consistently high relative to any reasonable provisioned ceiling the team might set. Finance wants to reduce the DynamoDB bill for this specific table without introducing meaningful throttling risk, and understands that On-Demand's per-request pricing is structured to include a premium for not requiring any capacity forecasting.
**Options:**
A. Leave the table on On-Demand capacity mode indefinitely, since On-Demand is always the lowest-cost option regardless of traffic predictability.
B. Switch the table to Provisioned capacity mode with Application Auto Scaling, sized against the 14 months of stable, high-utilization historical data.
C. Enable DynamoDB Streams on the table to reduce per-request billing overhead.
D. Shard the table's partition key into many smaller tables to reduce per-request cost.
**Correct answer(s):** B
**Why correct:** Fourteen months of stable, high-utilization, low-variance traffic is precisely the evidence needed to size a Provisioned + Auto Scaling configuration with confidence — since On-Demand's premium exists specifically to pay for not needing that forecast, and the forecast is now easy and well-supported by real data, Provisioned capacity becomes the cheaper choice at this steady, high utilization level while Auto Scaling still absorbs the slow linear growth and protects against throttling.
**Why each wrong option is wrong:** A. On-Demand is not unconditionally the cheapest mode — its convenience premium only pays for itself when traffic is genuinely unpredictable; the scenario explicitly establishes the opposite (stable, predictable, high utilization), which is exactly when Provisioned capacity is the documented cheaper choice. C. DynamoDB Streams is a change-data-capture feature for downstream event processing (e.g., Lambda triggers) — it has no effect on the underlying read/write capacity billing model. D. Splitting the table into many smaller tables adds significant application complexity and operational overhead without changing the fundamental economics of On-Demand versus Provisioned pricing, and DynamoDB pricing isn't structured around table count in a way that would make this cheaper.
**Trigger words:** "run in production for 14 months on On-Demand," "narrow, predictable band," "no unexpected spikes ever recorded," "utilization consistently high," "premium for not requiring any capacity forecasting."
**Underlying architectural principle:** On-Demand's per-request premium is the price of not forecasting capacity — once real production history proves a workload's demand is stable, predictable, and consistently high-utilization, that premium stops being worth paying, and Provisioned capacity with Auto Scaling becomes the cost-optimal choice.

---

### Question 193 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A company runs a business-critical application on Amazon RDS for SQL Server with Multi-AZ enabled for high availability, which the compliance team requires and which must not be removed or weakened. Over the past several months, read query load from a growing internal reporting tool has increased significantly and is now measurably degrading the primary instance's performance. The team wants the most cost-effective way to relieve this specific read-load problem while keeping the existing Multi-AZ HA configuration completely unchanged.
**Options:**
A. Create one or more RDS Read Replicas and point the reporting tool's connection string at a Read Replica instead of the primary.
B. Add additional Multi-AZ standby instances to the deployment so reporting queries can be routed to a standby.
C. Increase the primary instance to the next larger instance class to absorb the additional read load.
D. Migrate the entire database engine to Aurora Serverless v2 immediately to gain read scaling.
**Correct answer(s):** A
**Why correct:** RDS Read Replicas are purpose-built for offloading read traffic from the primary instance at a cost scoped specifically to the additional read capacity needed, and they operate entirely independently of — and don't require any change to — the existing Multi-AZ HA configuration, satisfying every constraint in the scenario.
**Why each wrong option is wrong:** B. Standard RDS for SQL Server Multi-AZ uses a single non-readable standby for failover only (the readable-standby "Multi-AZ DB Cluster" deployment option is available only for MySQL and PostgreSQL, not SQL Server), so there is no such thing as "additional readable standbys" to route reporting queries to in this configuration. C. Vertically resizing the primary pays for more compute capacity around the clock to fix a read-specific bottleneck, which is a more expensive and less targeted fix than adding read capacity scoped to reads only. D. Migrating the entire production database engine to Aurora is a major, high-risk, non-trivial re-architecture effort that is not justified as an "immediate," cost-effective fix when a native RDS feature (Read Replicas) already solves the stated problem directly.
**Trigger words:** "RDS for SQL Server," "Multi-AZ... must not be removed or weakened," "read query load... increased significantly," "most cost-effective way to relieve this specific read-load problem."
**Underlying architectural principle:** RDS Read Replicas and Multi-AZ solve two entirely different problems (read scaling vs. HA/failover) and can be layered independently — don't assume Multi-AZ's standby can absorb reads, especially for engines (like SQL Server) that don't support the readable Multi-AZ DB Cluster deployment option.

---

### Question 194 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A fintech company's private-subnet application fleet retrieves database credentials from AWS Secrets Manager on every connection attempt, generating dozens of terabytes of monthly traffic that currently routes through a NAT Gateway. This traffic now accounts for the single largest component of the company's NAT Gateway data-processing bill. The security team separately requires that this traffic never traverse the public internet, ruling out any option that would route it through an Internet Gateway.
**Options:**
A. Add a Gateway VPC Endpoint for Secrets Manager to remove this traffic from the NAT Gateway.
B. Add an Interface VPC Endpoint (PrivateLink) for Secrets Manager in the relevant subnets.
C. Deploy additional NAT Gateways across more Availability Zones to spread out the data-processing charges.
D. Cache credentials locally on each instance indefinitely to avoid calling Secrets Manager altogether.
**Correct answer(s):** B
**Why correct:** Secrets Manager is not one of the two services supported by the free Gateway VPC Endpoint type, so an Interface VPC Endpoint (PrivateLink) is the only way to keep this traffic off the public internet while removing it from the NAT Gateway's billed data path; at this traffic volume, PrivateLink's hourly-plus-per-GB pricing is well documented to come in below the equivalent NAT Gateway data-processing cost for the same volume.
**Why each wrong option is wrong:** A. Gateway VPC Endpoints only support S3 and DynamoDB — Secrets Manager has no Gateway Endpoint option, so this choice is not technically available regardless of cost. C. Spreading traffic across more NAT Gateways multiplies the fixed hourly charge without changing the underlying per-GB data-processing rate that's driving the bulk of the cost — it doesn't solve the problem. D. Indefinitely caching credentials locally undermines the security purpose of using Secrets Manager (timely credential rotation and centralized access control) and isn't a cost-optimization answer the scenario is asking for; it also isn't the kind of architectural network fix the "never traverse the public internet" constraint calls for.
**Trigger words:** "Secrets Manager," "dozens of terabytes of monthly traffic... through a NAT Gateway," "never traverse the public internet."
**Underlying architectural principle:** For AWS services other than S3 and DynamoDB, an Interface VPC Endpoint (PrivateLink) — not a Gateway Endpoint, which doesn't exist for them — is the way to remove high-volume private-subnet traffic from NAT Gateway billing while keeping it off the public internet; at sufficient volume, PrivateLink's per-GB rate typically undercuts NAT Gateway's.

---

### Question 195 [Priority: P1] [Difficulty: Hard] [Type: Single-Answer]
**Scenario:** A media company stores large video files in an S3 bucket in a single Region and serves them directly to a global audience by generating presigned URLs pointing straight at the bucket. A cost review shows that data-transfer-out-to-internet charges from this bucket have become the single largest line item on the AWS bill, and the same files are being downloaded repeatedly by large numbers of viewers around the world. The company wants to substantially reduce this specific cost while maintaining or improving the global viewing experience.
**Options:**
A. Enable S3 Transfer Acceleration on the bucket to speed up file delivery to distant viewers.
B. Put Amazon CloudFront in front of the S3 bucket (using Origin Access Control) and serve viewers through CloudFront instead of directly from S3.
C. Set up Cross-Region Replication to additional Regions and use Route 53 latency-based routing to send each viewer to their nearest S3 bucket copy.
D. Enable S3 Intelligent-Tiering on the bucket to reduce the per-GB storage cost of the video files.
**Correct answer(s):** B
**Why correct:** CloudFront's data-transfer-out-to-internet pricing is lower than S3's direct-to-internet data-transfer pricing at scale, and because the same popular files are being downloaded repeatedly, CloudFront's edge caching also eliminates most repeat trips back to the S3 origin entirely — directly and substantially cutting the largest cost driver named while improving global viewer latency.
**Why each wrong option is wrong:** A. S3 Transfer Acceleration speeds up **uploads** to S3 from geographically distant clients over the AWS backbone — it has no relevance to reducing the cost or improving the experience of **downloads** being served out to viewers. C. Replicating the files into multiple Regions still results in each regional copy incurring its own full data-transfer-out-to-internet charges with no caching benefit for repeated downloads of the same popular files, and adds ongoing storage cost in every additional Region — a more expensive path to a worse outcome than caching. D. Intelligent-Tiering optimizes storage cost based on access frequency, but the cost problem described here is data-transfer-out cost, not storage cost — this doesn't address the stated bottleneck at all.
**Trigger words:** "data-transfer-out-to-internet charges... single largest line item," "downloaded repeatedly by large numbers of viewers around the world," "substantially reduce this specific cost while... improving the global viewing experience."
**Underlying architectural principle:** For globally distributed, repeatedly downloaded content, fronting S3 with CloudFront reduces cost on two independent axes simultaneously — cheaper data-transfer-out pricing than direct S3 egress, and cache hit ratio eliminating redundant origin fetches — making it the default answer whenever repeated-download egress cost is the stated problem.

---

### Question 196 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A company's private-subnet application fleet currently reaches three destinations exclusively through a single NAT Gateway: (1) a high-volume S3 bucket used for object storage, (2) a high-volume DynamoDB table, and (3) AWS Systems Manager, used moderately for Session Manager access by operators (no bastion host or SSH exists). The NAT Gateway's data-processing charges have grown substantially, and a cost review confirms these three destinations account for effectively all of the fleet's outbound traffic — there is no other internet-bound traffic from this fleet. Select the two changes that most directly and correctly reduce cost here.
**Options:**
A. Add Gateway VPC Endpoints for S3 and DynamoDB.
B. Add an Interface VPC Endpoint (PrivateLink) for Systems Manager (including the endpoints Session Manager requires) in the relevant subnets.
C. Remove the NAT Gateway entirely without adding any VPC endpoints, since the fleet apparently has no other need for internet access.
D. Add an Interface VPC Endpoint (PrivateLink) for S3 instead of a Gateway VPC Endpoint, to get finer security-group-based access control.
E. Increase the NAT Gateway's provisioned bandwidth to reduce its per-GB processing rate.
**Correct answer(s):** A, B
**Why correct:** Gateway VPC Endpoints for S3 and DynamoDB (A) are free and remove the two highest-volume destinations from NAT Gateway billing entirely; a Systems Manager Interface VPC Endpoint (B) is required because Session Manager depends on SSM endpoints that have no Gateway Endpoint option, and adding it removes the NAT Gateway's dependency for operator access as well — together these two changes address all three named destinations.
**Why each wrong option is wrong:** C. Removing the NAT Gateway outright before confirming that literally zero other traffic (including any not yet identified, such as OS/agent updates or other AWS API calls not covered by an endpoint) needs internet egress is a risky, unverified assumption that could silently break functionality — the safe, verified action is adding the specific endpoints needed for the three named destinations. D. A Gateway VPC Endpoint for S3 is free, while an Interface VPC Endpoint for S3 incurs hourly and per-GB charges — since the scenario's goal is minimizing cost and Gateway Endpoint constraints (S3, same VPC/Region) are already satisfied, swapping to the paid Interface Endpoint variant for "finer security-group control" is an unnecessary added cost not justified by any stated requirement. E. NAT Gateway bandwidth already scales automatically up to its ceiling with no manual provisioning step or "bandwidth setting" to adjust, and even if such a lever existed, it wouldn't change the per-GB data-processing rate driving the cost.
**Trigger words:** "S3 bucket... DynamoDB table... Systems Manager, used... for Session Manager access," "NAT Gateway's data-processing charges have grown substantially," "no other internet-bound traffic from this fleet."
**Underlying architectural principle:** Systematically map every distinct destination behind a costly NAT Gateway to the cheapest correct VPC Endpoint type available for it (Gateway for S3/DynamoDB, Interface for everything else that supports PrivateLink) rather than removing NAT outright or defaulting to the more expensive endpoint type out of caution.

---

### Question 197 [Priority: P1] [Difficulty: Hard] [Type: Multiple-Response]
**Scenario:** A B2B SaaS company runs a separate Aurora PostgreSQL cluster per customer tenant for data isolation. Usage analysis reveals two clearly distinct groups: a small number of large "enterprise" tenants generate steady, high, predictable 24/7 database load that has held consistent for over a year, while the much larger group of "starter" tier tenants generates sporadic, idle-heavy, highly variable load with long stretches of near-zero activity between bursts of use. Finance wants a strategy that minimizes total cost across all tenant clusters while preserving full Aurora PostgreSQL compatibility and each tenant's data isolation. Select the two best actions.
**Options:**
A. Run the "starter" tier tenant clusters on Aurora Serverless v2, allowing capacity to scale down toward zero ACUs during their long idle stretches.
B. Consolidate every tenant, both enterprise and starter, onto a single large provisioned Aurora cluster sized to the combined peak load of all tenants.
C. Run the "enterprise" tier tenants' clusters on provisioned Aurora instances covered by Reserved Instance pricing, since their usage is steady and predictable.
D. Migrate every tenant, regardless of usage pattern, to Aurora Serverless v2, since it is the newest Aurora capacity model and is always the cheapest option.
E. Purchase 3-year Reserved Instances sized to each tenant's individual historical peak usage, including the starter tier tenants.
**Correct answer(s):** A, C
**Why correct:** Matching each usage profile to the purchasing model built for it minimizes total cost: the starter tenants' sporadic, idle-heavy pattern (A) is exactly what Aurora Serverless v2's scale-to-near-zero behavior is priced for, while the enterprise tenants' steady, predictable, year-long 24/7 baseline (C) is exactly the profile a committed-use Reserved Instance discount on provisioned Aurora is priced for.
**Why each wrong option is wrong:** B. Consolidating all tenants onto one shared cluster eliminates the per-tenant data isolation the company explicitly wants to preserve, and still requires sizing to the combined peak of every tenant, which doesn't reduce the fundamental waste of paying for idle starter-tenant capacity most of the time. D. Aurora Serverless v2 is not unconditionally the cheapest option in every case — for the enterprise tenants' steady, high, 24/7 utilization, a Reserved Instance's committed-use discount on provisioned capacity is cheaper than paying Serverless v2's per-ACU-second rate with no commitment discount for that same guaranteed demand. E. Sizing a Reserved Instance to each starter tenant's individual historical peak wastes money during that tenant's long idle stretches, which make up most of its usage — this is the opposite of matching the purchasing model to the workload's actual (mostly idle) profile.
**Trigger words:** "steady, high, predictable 24/7 database load that has held consistent for over a year" vs. "sporadic, idle-heavy, highly variable load with long stretches of near-zero activity," "minimizes total cost... while preserving... each tenant's data isolation."
**Underlying architectural principle:** In a mixed-workload environment, the cost-optimal strategy is rarely a single uniform choice — layer a committed-use discount (Reserved Instance / Savings Plan) under confirmed steady demand and an auto-scaling, pay-per-use model (Aurora Serverless v2, DynamoDB On-Demand) under genuinely variable or idle-heavy demand.

---

### Question 198 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A company ingests millions of small log objects into S3 daily and, wanting maximum savings, configured a Lifecycle rule transitioning every object to S3 Glacier Deep Archive just 1 day after creation. After implementing this rule, the monthly S3 bill actually increased rather than decreased. Investigation reveals that a separate, pre-existing automated cleanup process permanently deletes roughly 90% of these log objects after about 10 days once they've been identified as duplicates or superseded by newer data — well before any archive tier's minimum storage duration commitment has elapsed.
**Options:**
A. Switch the 1-day transition target from Glacier Deep Archive to Glacier Flexible Retrieval instead, keeping the same 1-day transition timing.
B. Remove the 1-day transition entirely; keep the existing 10-day deletion behavior, and only add a transition to a cheaper storage class (timed appropriately) for the subset of objects confirmed to survive past the cleanup process.
C. Keep the transition to Glacier Deep Archive at 1 day, and additionally add a Lifecycle expiration rule deleting all objects after exactly 5 days regardless of the cleanup process's own logic.
D. Replace the Glacier Deep Archive transition with S3 Intelligent-Tiering enabled from day 1.
**Correct answer(s):** B
**Why correct:** Because roughly 90% of these objects are deleted around day 10 — well short of any cold-tier's minimum storage duration commitment — transitioning them early into a class with a minimum-duration charge triggers an effective early-deletion cost that exceeds what they would have cost simply sitting in Standard for those 10 days; removing the premature transition and only moving the smaller surviving subset of objects (the ones that outlive the cleanup process) into a cheaper tier eliminates this waste at its root.
**Why each wrong option is wrong:** A. Glacier Flexible Retrieval also carries its own minimum storage duration commitment, which is still longer than the ~10-day real lifetime of most of these objects — this reduces the per-object penalty somewhat but doesn't fix the underlying mismatch between transition timing and actual object lifetime. C. Forcing an unconditional 5-day expiration ignores that the existing cleanup process needs up to ~10 days to correctly identify duplicates/superseded objects, risking premature deletion of objects still needed for that comparison, while also still paying the early-deletion penalty on the objects already transitioned to Deep Archive at day 1. D. Since most of these objects are deleted around day 10, well before Intelligent-Tiering's Infrequent Access tier threshold (30 days) would ever move them out of the frequent-access tier, enabling Intelligent-Tiering produces essentially zero savings for this object population and adds its per-object monitoring fee for no benefit — it doesn't address the root cause of the cost increase at all.
**Trigger words:** "monthly S3 bill actually increased rather than decreased," "deletes roughly 90%... after about 10 days," "well before any archive tier's minimum storage duration commitment has elapsed."
**Underlying architectural principle:** Never transition objects into a storage class with a minimum storage duration commitment unless the object's real expected lifetime is confidently longer than that minimum — doing so converts an intended savings action into an early-deletion cost penalty.

---

### Question 199 [Priority: P2] [Difficulty: Very Hard] [Type: Single-Answer]
**Scenario:** A financial analytics platform's Aurora MySQL cluster has two distinct demand components: the writer handles a steady, guaranteed baseline equivalent to roughly 8 ACUs sustained continuously, 24 hours a day, all year; separately, an internal BI tool periodically runs heavy read-only analytical queries that spike demand up to roughly 64 ACUs for a few hours at unpredictable times, several times a week, with no fixed schedule. The company wants an architecture that commits to (and gets a committed-use discount for) only the portion of demand that is truly guaranteed, while letting the unpredictable analytical burst scale automatically with no manual intervention and no standing over-provisioning for the peak.
**Options:**
A. Run the entire cluster (writer and readers together) on Aurora Serverless v2, auto-scaling anywhere between 8 and 64 ACUs as needed.
B. Run a provisioned writer instance sized to the guaranteed 8 ACU baseline, covered by Reserved Instance pricing, and add one or more Aurora Serverless v2 readers that auto-scale up only during the unpredictable analytical bursts.
C. Run a single provisioned writer instance sized to the full 64 ACU peak, covered by Reserved Instance pricing, so it's always ready for a burst.
D. Run the writer on Aurora Serverless v2 with both its minimum and maximum ACU settings fixed at 64, to guarantee burst headroom is always available.
**Correct answer(s):** B
**Why correct:** This mixed-fleet architecture matches each demand component to the purchasing model built for it: the guaranteed, steady 8-ACU baseline goes on a provisioned instance eligible for a Reserved Instance commitment discount (something Serverless v2's per-ACU-second pricing has no equivalent mechanism for), while the genuinely unpredictable analytical bursts are absorbed by Serverless v2 readers that scale automatically only when actually needed — avoiding paying either a commitment premium for capacity that isn't guaranteed or a no-discount rate for capacity that is guaranteed.
**Why each wrong option is wrong:** A. Running the entire cluster on Serverless v2 means even the guaranteed, always-on 8-ACU baseline is billed at Serverless v2's uncommitted per-ACU-second rate with no long-term discount mechanism, costing more over a year than covering that same guaranteed demand with a Reserved Instance. C. Sizing a Reserved Instance to the 64-ACU peak means paying for that much capacity continuously even though it's only actually needed for a few hours, several times a week — the vast majority of the time this capacity sits idle and wasted. D. Fixing Serverless v2's minimum ACU at 64 defeats the entire purpose of its auto-scaling model, guaranteeing the cost of running at peak capacity continuously — this is worse than every other option, including the peak-sized Reserved Instance in C.
**Trigger words:** "steady, guaranteed baseline... sustained continuously, 24 hours a day, all year," "unpredictable... at unpredictable times," "commits to... only the portion of demand that is truly guaranteed," "no standing over-provisioning for the peak."
**Underlying architectural principle:** Aurora's mixed reader fleet capability lets an architecture combine a committed-discount provisioned instance for guaranteed baseline demand with auto-scaling Serverless v2 capacity for genuinely unpredictable demand within the same cluster — this beats forcing the entire cluster onto either model alone whenever demand has both a guaranteed floor and an unpredictable ceiling.

---

### Question 200 [Priority: P0] [Difficulty: Very Hard] [Type: Multiple-Response]
**Scenario:** A three-tier application runs across multiple Availability Zones in one Region: a web tier behind an ALB in public subnets, an app tier in private subnets that calls S3 and DynamoDB heavily and also calls an external third-party payment gateway over the public internet, and a database tier on Aurora with Multi-AZ. A cost audit surfaces three unexpectedly large monthly charges: (1) NAT Gateway data-processing charges, (2) cross-AZ data-transfer charges between the app tier and a single-AZ ElastiCache Memcached cluster that every app instance in every AZ calls constantly, and (3) S3 storage cost that has grown steadily even though the application's own logged object-write count has stayed flat. Select the two changes that most directly address the largest, clearly-attributable cost drivers actually described here.
**Options:**
A. Add Gateway VPC Endpoints for S3 and DynamoDB so that traffic to those two services no longer traverses the NAT Gateway (the third-party payment gateway call still requires a NAT Gateway or Internet Gateway path, since it's a genuine external internet destination with no VPC endpoint available).
B. Add an S3 Lifecycle rule using `AbortIncompleteMultipartUpload` to clean up abandoned multipart upload parts, which accumulate storage cost without ever appearing in the application's own logged object-write count.
C. Move the ElastiCache Memcached cluster into a cluster placement group spanning all the Availability Zones in use, to eliminate the cross-AZ latency and cost.
D. Replace the NAT Gateway with a single self-managed NAT Instance to lower the hourly charge, accepting the added patching and single-point-of-failure operational overhead.
E. Replace the Gateway VPC Endpoint approach with routing the payment gateway's traffic through a newly created Interface VPC Endpoint for the payment provider.
**Correct answer(s):** A, B
**Why correct:** A directly removes the NAT Gateway's largest addressable traffic category (same-Region S3 and DynamoDB calls) at no additional cost while correctly leaving the genuinely internet-bound payment gateway traffic on NAT/IGW where it belongs, and B directly matches the classic signature of S3 storage growing faster than an application's own reported object count — abandoned incomplete multipart upload parts — with the native lifecycle action built to clean them up.
**Why each wrong option is wrong:** C. Cluster placement groups are explicitly confined to a single Availability Zone and cannot span multiple AZs, so this doesn't just fail to fix the cross-AZ cost — it's not even a valid configuration for the stated goal; the real fix for a single-AZ cache being hit from every AZ is deploying cache nodes/replicas in each AZ (or an equivalent multi-AZ caching topology) so instances read from a local-AZ node. D. A self-managed NAT Instance trades NAT Gateway's hourly and per-GB data-processing charges for ordinary EC2 instance and data-transfer-out charges instead — but once option A removes the high-volume S3/DynamoDB traffic from the NAT path, the only traffic left (the third-party payment gateway calls) is no longer the largest cost driver, making this swap a disproportionate, higher-risk change (patching burden, bandwidth ceiling, single point of failure) for a traffic category that isn't the problem being solved. E. There is no such thing as a VPC Endpoint (Gateway or Interface) for a third-party, non-AWS payment gateway reachable only over the public internet — VPC Endpoints (via PrivateLink) connect to AWS services or specifically published PrivateLink-enabled SaaS endpoints, not arbitrary external internet destinations.
**Trigger words:** "S3 and DynamoDB heavily," "external third-party payment gateway over the public internet," "single-AZ ElastiCache Memcached cluster that every app instance in every AZ calls constantly," "S3 storage cost... grown steadily even though the application's own logged object-write count has stayed flat."
**Underlying architectural principle:** Cost audits require attributing each charge to its real, specific root cause before choosing a fix — VPC Endpoints only ever apply to AWS (or PrivateLink-published) services, placement groups never span AZs, and unexplained S3 growth against flat logged writes points specifically at incomplete multipart uploads, not general lifecycle mistuning.
