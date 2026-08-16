# SAA-C03 Domain 1 Practice Questions — IAM & Access Management (part of Design Secure Architectures, 30% weight)

Focus areas: IAM users/groups/roles/policies and policy evaluation logic, STS/AssumeRole, cross-account access, permission boundaries, AWS IAM Identity Center, SCPs/AWS Organizations, identity federation (SAML/OIDC/web identity), temporary credentials.

This set complements `domain1-secure-architectures-practice.md` (which covers KMS, Secrets Manager, and S3-specific encryption controls) by focusing specifically on identity, access, and organization-level guardrails.

These are **original practice questions** written for personal study, based on publicly documented AWS service behavior as of 2026 and the official SAA-C03 exam guide scope. They are **not** reproductions of any real, leaked, or dumped exam content.

---

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

*End of Domain 1 — IAM & Access Management practice set (20 questions). Distribution: 3 Easy, 8 Medium, 6 Hard, 3 Very Hard; 4 Multiple-Response, 16 Single-Answer. Original content for personal study — not sourced from or reproducing any real/leaked SAA-C03 exam questions.*
