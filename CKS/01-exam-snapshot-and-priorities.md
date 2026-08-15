# CKS Exam Snapshot -- Certified Kubernetes Security Specialist

![CKS exam domain map and weights](images/cks-00-exam-domain-map.jpg)

![API request security flow](images/cks-02-api-request-security-flow.jpg)

![Attack to defense quick reference](images/cks-13-attack-defense-mapping.jpg)

![Context safety preflight ritual](images/cks-17-context-safety-preflight-ritual.jpg)

> **Research Date:** 2026-08-15
> **Sources:** Linux Foundation official pages, CNCF curriculum repo, Kubernetes docs, LF FAQ
> **Researcher context:** CKAD-certified Principal Platform Engineer, 11+ yrs cloud architecture

---

## Table of Contents

1. [Exam Overview](#1-exam-overview)
2. [Prerequisites](#2-prerequisites)
3. [Exam Domains and Weightings](#3-exam-domains-and-weightings)
4. [Allowed Resources During Exam](#4-allowed-resources-during-exam)
5. [Exam Environment Details](#5-exam-environment-details)
6. [Killer.sh Simulator](#6-killersh-simulator)
7. [Retake and Scheduling Policy](#7-retake-and-scheduling-policy)
8. [Certification Validity and CARE Program](#8-certification-validity-and-care-program)
9. [Pricing and Bundle Options](#9-pricing-and-bundle-options)
10. [Deprecated Topics -- What Old Courses Get Wrong](#10-deprecated-topics----what-old-courses-get-wrong)
11. [Verification Status Table](#11-verification-status-table)
12. [Key Tools and Technologies to Study](#12-key-tools-and-technologies-to-study)
13. [Sources](#13-sources)

---

## 1. Exam Overview

| Attribute                | Detail                                               | Verification   |
|--------------------------|------------------------------------------------------|----------------|
| **Official Name**        | Certified Kubernetes Security Specialist (CKS)       | Officially Verified |
| **Exam Code**            | CKS                                                  | Officially Verified |
| **Duration**             | 2 hours                                              | Officially Verified |
| **Passing Score**        | 67%                                                  | Officially Verified |
| **Format**               | Performance-based (command line, live K8s clusters)   | Officially Verified |
| **Number of Tasks**      | 15-20 tasks                                          | Officially Verified |
| **Kubernetes Version**   | v1.35                                                | Officially Verified |
| **Proctoring**           | Online, PSI Secure Browser (Chrome-based)            | Officially Verified |
| **Languages**            | English, Simplified Chinese, Japanese                | Officially Verified |
| **Results Delivery**     | Email within 24 hours                                | Officially Verified |
| **Preparation Course**   | Kubernetes Security Essentials (LFS260)              | Officially Verified |

### Note on Kubernetes Version

The exam environment is updated to match the most recent Kubernetes minor version within approximately 4-8 weeks of its release. As of this research, the environment runs **v1.35**. The CNCF curriculum PDF on GitHub is labeled v1.34, which may indicate the curriculum document lags slightly behind the running environment version.

---

## 2. Prerequisites

| Requirement                                      | Status              |
|--------------------------------------------------|---------------------|
| **Must hold active CKA certification**           | Officially Verified |
| CKA must be passed **before** attempting CKS     | Officially Verified |
| No specific training course required              | Officially Verified |

**Direct quote from Linux Foundation:** "Certified Kubernetes Security Specialist (CKS) candidates must have taken and passed the Certified Kubernetes Administrator (CKA) exam prior to attempting the CKS exam."

**Important for planning:** You need CKA first. If your CKA has expired, the CARE program (see Section 8) now means passing CKS will automatically re-extend your CKA.

---

## 3. Exam Domains and Weightings

### Domain Summary

| # | Domain                                        | Weight | Questions (est.) |
|---|-----------------------------------------------|--------|------------------|
| 1 | Cluster Setup                                 | 15%    | ~2-3             |
| 2 | Cluster Hardening                             | 15%    | ~2-3             |
| 3 | System Hardening                              | 10%    | ~1-2             |
| 4 | Minimize Microservice Vulnerabilities         | 20%    | ~3-4             |
| 5 | Supply Chain Security                         | 20%    | ~3-4             |
| 6 | Monitoring, Logging and Runtime Security      | 20%    | ~3-4             |
|   | **Total**                                     | **100%** | **15-20**      |

### Domain 1: Cluster Setup (15%)

- Use Network security policies to restrict cluster level access
- Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi)
- Properly set up Ingress with TLS
- Protect node metadata and endpoints
- Verify platform binaries before deploying

### Domain 2: Cluster Hardening (15%)

- Use Role Based Access Controls to minimize exposure
- Exercise caution in using service accounts (disable defaults, minimize permissions on newly created ones)
- Restrict access to Kubernetes API
- Upgrade Kubernetes to avoid vulnerabilities

### Domain 3: System Hardening (10%)

- Minimize host OS footprint (reduce attack surface)
- Using least-privilege identity and access management
- Minimize external access to the network
- Appropriately use kernel hardening tools such as AppArmor, seccomp

### Domain 4: Minimize Microservice Vulnerabilities (20%)

- Use appropriate pod security standards
- Manage Kubernetes secrets
- Understand and implement isolation techniques (multi-tenancy, sandboxed containers, etc.)
- Implement Pod-to-Pod encryption (Cilium, Istio)

### Domain 5: Supply Chain Security (20%)

- Minimize base image footprint
- Understand your supply chain (e.g. SBOM, CI/CD, artifact repositories)
- Secure your supply chain (permitted registries, sign and validate artifacts, etc.)
- Perform static analysis of user workloads and container images (e.g. Kubesec, KubeLinter)

### Domain 6: Monitoring, Logging and Runtime Security (20%)

- Perform behavioral analytics to detect malicious activities
- Detect threats within physical infrastructure, apps, networks, data, users and workloads
- Investigate and identify phases of attack and bad actors within the environment
- Ensure immutability of containers at runtime
- Use Kubernetes audit logs to monitor access

---

## 4. Allowed Resources During Exam

### Allowed Documentation URLs

| Resource                                | URL                                                                      |
|-----------------------------------------|--------------------------------------------------------------------------|
| Kubernetes Documentation                | https://kubernetes.io/docs/                                              |
| Kubernetes Blog                         | https://kubernetes.io/blog/                                              |
| Falco Documentation                     | https://falco.org/docs/                                                  |
| Bom CLI Reference                       | https://kubernetes-sigs.github.io/bom/cli-reference/                     |
| etcd Documentation                      | https://etcd.io/docs/                                                    |
| NGINX Ingress Controller Documentation  | https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/ |
| Cilium Documentation                    | https://docs.cilium.io/en/stable                                        |
| Istio Documentation                     | https://istio.io/latest/docs/                                           |

### Additional Allowed Resources

- Task-specific documentation from the Quick Reference box
- Exam instructions presented in the command-line terminal
- Documents installed by the distribution (`/usr/share` and subdirectories)
- Distribution packages (may be installed if not available by default)

### Restrictions

- Using the search function on https://kubernetes.io/docs/ IS allowed
- You must NOT open external search results (e.g., Google, Stack Overflow)
- No browser windows other than the exam window
- No notes, books, or external materials

### Key Insight for CKS vs CKAD/CKA

The CKS exam allows access to **Falco, Cilium, Istio, etcd, and Bom docs** in addition to the standard Kubernetes documentation. This tells you exactly which tools are exam-relevant. Bookmark key pages in these docs before the exam.

---

## 5. Exam Environment Details

### System Setup

| Component                | Detail                                                |
|--------------------------|-------------------------------------------------------|
| **Delivery Platform**    | PSI Secure Browser (Chrome-based)                     |
| **Base Node**            | hostname: `base` (DO NOT reboot -- will not restart)  |
| **Task Execution**       | SSH into designated hosts per task                     |
| **Elevated Privileges**  | `sudo -i` or `sudo` commands                          |
| **Return After Task**    | Return to base node after each task                   |
| **Nested SSH**           | NOT supported                                         |

### Pre-installed Tools on SSH Hosts

| Tool                     | Details                                               |
|--------------------------|-------------------------------------------------------|
| `kubectl`                | Pre-installed with `k` alias and Bash autocompletion  |
| `yq`                     | YAML processing                                       |
| `curl` and `wget`        | HTTP testing                                          |
| `man` and man pages      | Documentation lookup                                  |

**WARNING:** The base node (`base`) does NOT have these tools. All tasks must be completed on designated SSH hosts.

### Keyboard Shortcuts (Critical for Exam)

| Action                   | Shortcut                                              |
|--------------------------|-------------------------------------------------------|
| Copy (terminal)          | `Ctrl+Shift+C`                                        |
| Paste (terminal)         | `Ctrl+Shift+V`                                        |
| Copy (other apps)        | `Ctrl+C`                                              |
| Paste (other apps)       | `Ctrl+V`                                              |
| Close tab WORKAROUND     | `Ctrl+Alt+W` (never use Ctrl+W -- closes Chrome tab!) |
| Vim insert mode          | `i` key (INSERT key is prohibited)                    |
| Find in page (Firefox)   | `Ctrl+F`                                              |
| Cursor location          | `Ctrl+Alt+K`                                          |

### Hardware and Environment Requirements

- Single active monitor (15"+ recommended, 1080p minimum)
- Dual monitors NOT supported
- Webcam with panning capability
- Microphone
- Wired internet connection strongly preferred
- Private, quiet, well-lit room
- Clear desk (no paper, devices, electronics)
- Laptop must be plugged in
- No VMs (even if compatibility checks pass)
- Disable corporate firewalls and antivirus if possible
- WebRTC must be allowed

### ID Requirements

- Valid government-issued photo ID (passport, driver's license, national ID)
- First and last name must exactly match registration
- Must include name, photo, and signature

---

## 6. Killer.sh Simulator

| Attribute                    | Detail                                    | Verification       |
|------------------------------|-------------------------------------------|---------------------|
| **Sessions Included**        | 2 sessions with exam purchase             | Officially Verified |
| **Session Duration**         | 36 hours access per session               | Officially Verified |
| **Number of Questions**      | 17 questions per session                  | Officially Verified |
| **Grading**                  | Automated with scored results             | Officially Verified |
| **Difficulty vs Real Exam**  | Harder than the real exam                 | Community Reported  |

### Strategy Notes

- Use the first session early in your study to identify gaps
- Use the second session 1-2 weeks before the real exam as a final check
- The 36-hour window starts when you activate the session, not when you purchase
- Community consensus: if you score well on killer.sh, you will likely pass the real exam
- Questions cover similar domains but are generally more difficult and time-pressured

---

## 7. Retake and Scheduling Policy

| Policy                       | Detail                                    | Verification       |
|------------------------------|-------------------------------------------|---------------------|
| **Exam Attempts Included**   | 2 (one exam + one free retake)            | Officially Verified |
| **Scheduling Window**        | 12 months from purchase                   | Officially Verified |
| **Results Delivery**         | Email within 24 hours                     | Officially Verified |
| **Misconduct Policy**        | Zero tolerance; recordings reviewed       | Officially Verified |

### Scheduling Tips

- Schedule well in advance for preferred time slots
- Ensure stable internet (wired preferred)
- Test PSI browser compatibility before exam day
- Allow time for the room/ID check process (15-20 minutes before exam)

---

## 8. Certification Validity and CARE Program

| Attribute                    | Detail                                    | Verification       |
|------------------------------|-------------------------------------------|---------------------|
| **Validity Period**          | 2 years from exam date                    | Officially Verified |
| **Renewal Method**           | Retake and pass the exam                  | Officially Verified |
| **Legacy Validity**          | 3 years (for certs earned before Apr 2024)| Officially Verified |

### CARE Program (New -- June 18, 2026)

**Major recent change:** Earning or recertifying CKS on or after June 18, 2026, automatically extends your CKA certification.

| CARE Detail                  | Information                                                                   |
|------------------------------|-------------------------------------------------------------------------------|
| **Effective Date**           | June 18, 2026                                                                |
| **What Happens**             | Passing CKS auto-extends CKA to match CKS expiry date                        |
| **Applies To**               | All CKA statuses (active or expired)                                          |
| **Action Required**          | None -- automatic                                                             |
| **Rationale**                | Recognizes natural progression from K8s admin to K8s security                 |

**Strategic implication:** If you plan to hold both CKA and CKS, you only need to actively renew CKS going forward. Passing CKS keeps CKA alive automatically.

---

## 9. Pricing and Bundle Options

| Option                                          | Price  | Savings |
|-------------------------------------------------|--------|---------|
| CKS Exam Only                                   | $445   | --      |
| CKS Exam + THRIVE-ONE Annual Subscription       | $625   | 40%     |
| CKS Exam + Kubernetes Security Essentials (LFS260) | $645 | --      |

All options include 2 exam attempts, 2 killer.sh sessions, 12-month scheduling window.

---

## 10. Deprecated Topics -- What Old Courses Get Wrong

This section is critical. Many CKS courses and study materials were written for Kubernetes 1.23-1.24 era. The exam now runs K8s v1.35, and several major security features have changed.

### PodSecurityPolicy -- REMOVED (K8s 1.25)

| Aspect                       | Old (Pre-1.25)                        | Current (1.25+)                             |
|------------------------------|---------------------------------------|---------------------------------------------|
| **Mechanism**                | PodSecurityPolicy (PSP) resource      | Pod Security Admission (PSA) controller     |
| **API**                      | `policy/v1beta1 PodSecurityPolicy`    | Namespace labels + Pod Security Standards   |
| **Configuration**            | Create PSP objects + RBAC bindings    | Label namespaces with enforce/audit/warn    |
| **Levels**                   | Custom per-PSP                        | Three standard levels: privileged, baseline, restricted |
| **Status**                   | Deprecated 1.21, REMOVED 1.25        | Stable since 1.25                           |

**What to study instead:**

```yaml
# Pod Security Admission via namespace labels
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

Three modes: `enforce` (reject), `audit` (log), `warn` (warn user).
Three levels: `privileged`, `baseline`, `restricted`.

### AppArmor -- New Field-Based API (K8s 1.30+)

| Aspect                       | Old (Pre-1.30)                                        | Current (1.30+)                                      |
|------------------------------|-------------------------------------------------------|------------------------------------------------------|
| **Configuration**            | Annotations on pod metadata                           | `securityContext.appArmorProfile` field               |
| **Annotation Format**        | `container.apparmor.security.beta.kubernetes.io/<name>` | N/A (deprecated)                                    |
| **Field Format**             | N/A                                                   | `appArmorProfile.type` + `appArmorProfile.localhostProfile` |
| **GA Status**                | Beta (annotations)                                    | Stable since v1.31                                   |

**What to study instead:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    appArmorProfile:
      type: Localhost
      localhostProfile: k8s-apparmor-example-deny-write
  containers:
  - name: app
    image: busybox:1.28
```

Profile types: `RuntimeDefault`, `Localhost`, `Unconfined`.

### Seccomp -- Field-Based API (GA since K8s 1.19)

| Aspect                       | Old (Pre-1.19)                                        | Current (1.19+)                                      |
|------------------------------|-------------------------------------------------------|------------------------------------------------------|
| **Configuration**            | Annotations on pod metadata                           | `securityContext.seccompProfile` field               |
| **Annotation Format**        | `seccomp.security.alpha.kubernetes.io/pod`            | N/A (deprecated long ago)                            |
| **Field Format**             | N/A                                                   | `seccompProfile.type` + `seccompProfile.localhostProfile` |
| **GA Status**                | Alpha (annotations)                                   | Stable since v1.19                                   |

**What to study instead:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-pod
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: hashicorp/http-echo:1.0
    securityContext:
      allowPrivilegeEscalation: false
```

Profile types: `RuntimeDefault`, `Localhost`, `Unconfined`.

### Docker-Specific Content -- Largely Irrelevant

| Aspect                       | Old                                   | Current                                             |
|------------------------------|---------------------------------------|-----------------------------------------------------|
| **Container Runtime**        | Docker (dockershim)                   | containerd (dockershim removed in K8s 1.24)         |
| **CLI Tool**                 | `docker` commands                     | `crictl` for CRI-compatible runtimes                |
| **Image Building**           | `docker build`                        | Still relevant but exam focuses on security, not building |

### Deprecated API Versions

| Old API                              | Replacement                      | Removed In |
|--------------------------------------|----------------------------------|------------|
| `policy/v1beta1 PodSecurityPolicy`   | Pod Security Admission (labels)  | 1.25       |
| `extensions/v1beta1 Ingress`         | `networking.k8s.io/v1 Ingress`   | 1.22       |
| `extensions/v1beta1 NetworkPolicy`   | `networking.k8s.io/v1 NetworkPolicy` | 1.16   |
| `rbac.authorization.k8s.io/v1beta1`  | `rbac.authorization.k8s.io/v1`   | 1.22       |

### Summary: Red Flags in Old Study Materials

If a course or guide teaches any of the following, it is outdated:

1. Creating `PodSecurityPolicy` objects -- use Pod Security Admission labels instead
2. Using AppArmor annotations (`container.apparmor.security.beta.kubernetes.io`) -- use `securityContext.appArmorProfile` field
3. Using seccomp annotations (`seccomp.security.alpha.kubernetes.io`) -- use `securityContext.seccompProfile` field
4. Using `docker` CLI for container inspection -- use `crictl`
5. Using `extensions/v1beta1` for any resource
6. Any reference to dockershim or Docker as the container runtime

---

## 11. Verification Status Table

| Information                              | Status              | Source                                    |
|------------------------------------------|---------------------|-------------------------------------------|
| Exam name: CKS                           | Officially Verified | training.linuxfoundation.org              |
| Duration: 2 hours                        | Officially Verified | training.linuxfoundation.org              |
| Passing score: 67%                       | Officially Verified | LF FAQ                                    |
| K8s version: v1.35                       | Officially Verified | LF important-instructions-cks             |
| CKA prerequisite required                | Officially Verified | training.linuxfoundation.org              |
| 6 domains with listed weightings         | Officially Verified | training.linuxfoundation.org              |
| 2 killer.sh sessions included            | Officially Verified | training.linuxfoundation.org              |
| 36-hour killer.sh session window         | Officially Verified | training.linuxfoundation.org              |
| 17 questions per killer.sh session       | Officially Verified | training.linuxfoundation.org              |
| 2 exam attempts included                 | Officially Verified | training.linuxfoundation.org              |
| 12-month scheduling window              | Officially Verified | training.linuxfoundation.org              |
| Certification valid for 2 years          | Officially Verified | LF FAQ                                    |
| CARE: CKS extends CKA (from Jun 2026)   | Officially Verified | LF blog (Jun 18, 2026)                   |
| Exam price: $445                         | Officially Verified | training.linuxfoundation.org              |
| PSI Secure Browser proctoring            | Officially Verified | LF important-instructions-cks             |
| Pre-installed: kubectl, yq, curl, wget   | Officially Verified | LF important-instructions-cks             |
| Allowed docs: K8s, Falco, Cilium, etc.   | Officially Verified | LF certification-resources-allowed        |
| PSP removed in K8s 1.25                  | Officially Verified | kubernetes.io blog                        |
| AppArmor field API stable in 1.31        | Officially Verified | kubernetes.io docs                        |
| Seccomp field API GA since 1.19          | Officially Verified | kubernetes.io docs                        |
| Killer.sh harder than real exam          | Community Reported  | Community consensus                       |
| CKS-specific tools (Trivy, Falco, etc.) available | Community Reported | Not confirmed in official docs   |
| Curriculum PDF version: v1.34            | Officially Verified | github.com/cncf/curriculum               |

---

## 12. Key Tools and Technologies to Study

Based on the curriculum domains, allowed documentation, and exam environment, these are the tools and technologies you should be proficient with:

### Security Tools (Exam-Relevant)

| Tool/Technology        | CKS Domain                          | What to Know                                         |
|------------------------|--------------------------------------|------------------------------------------------------|
| **Falco**              | Domain 6: Runtime Security           | Rules, configuration, detecting anomalies            |
| **Trivy**              | Domain 5: Supply Chain Security      | Image scanning, vulnerability assessment             |
| **Kubesec**            | Domain 5: Supply Chain Security      | Static analysis of K8s manifests                     |
| **KubeLinter**         | Domain 5: Supply Chain Security      | Lint K8s YAML for best practices                     |
| **AppArmor**           | Domain 3: System Hardening           | Profile creation, loading, applying via securityContext |
| **seccomp**            | Domain 3: System Hardening           | Profile types, applying via securityContext           |
| **Cilium**             | Domain 4: Microservice Vulns         | Network policies, pod-to-pod encryption              |
| **Istio**              | Domain 4: Microservice Vulns         | mTLS, pod-to-pod encryption                          |
| **CIS Benchmarks**     | Domain 1: Cluster Setup              | kube-bench, reviewing component configs              |
| **SBOM tools (bom)**   | Domain 5: Supply Chain Security      | Generating/verifying SBOMs                           |

### Kubernetes Native Security Features

| Feature                       | Domain          | Key Concepts                                             |
|-------------------------------|-----------------|----------------------------------------------------------|
| NetworkPolicy                 | Domain 1        | Ingress/egress rules, default deny                       |
| RBAC                          | Domain 2        | Roles, ClusterRoles, RoleBindings, least privilege       |
| ServiceAccounts               | Domain 2        | Disable automount, minimize permissions                  |
| Pod Security Admission        | Domain 4        | enforce/audit/warn, three levels, namespace labels       |
| Secrets                       | Domain 4        | Creation, mounting, encryption at rest                   |
| etcd Encryption               | Domain 1        | EncryptionConfiguration, providers (aesgcm, kms, etc.)   |
| Audit Logging                 | Domain 6        | Audit policy, stages, levels                             |
| Admission Controllers         | Domain 2        | ImagePolicyWebhook, NodeRestriction, PodSecurity         |
| Ingress TLS                   | Domain 1        | TLS termination, certificate management                  |
| RuntimeClass                  | Domain 4        | gVisor, Kata Containers (sandboxed runtimes)             |
| Container immutability        | Domain 6        | readOnlyRootFilesystem, no privilege escalation          |

### etcd Encryption at Rest (High-Priority Topic)

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aesgcm:
          keys:
            - name: key1
              secret: <base64-encoded-key>
      - identity: {}
```

Key points:
- First provider in list encrypts; all providers can decrypt
- Apply via `--encryption-provider-config` flag on kube-apiserver
- Existing data must be re-written to be encrypted
- Providers: identity (none), aescbc (weak), aesgcm (strong), secretbox (strong), kms (strongest)

---

## 13. Sources

All information in this document was gathered from the following official sources:

- [Linux Foundation CKS Certification Page](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/)
- [Linux Foundation CKS Important Instructions](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-cks)
- [Linux Foundation CKA/CKAD/CKS FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-cka-ckad-cks)
- [Linux Foundation Certification Resources Allowed](https://docs.linuxfoundation.org/tc-docs/certification/certification-resources-allowed)
- [Linux Foundation Exam Rules and Policies](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-rules-and-policies)
- [CNCF Curriculum Repository](https://github.com/cncf/curriculum)
- [Linux Foundation Blog: CARE Program Expansion](https://training.linuxfoundation.org/blog/expanding-care-passing-cks-can-now-extend-your-cka-certification/)
- [Kubernetes Pod Security Admission Docs](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Kubernetes Pod Security Standards Docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Kubernetes AppArmor Tutorial](https://kubernetes.io/docs/tutorials/security/apparmor/)
- [Kubernetes Seccomp Tutorial](https://kubernetes.io/docs/tutorials/security/seccomp/)
- [Kubernetes Admission Controllers Reference](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Kubernetes Encrypting Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Kubernetes v1.25 Release Blog (PSP Removal)](https://kubernetes.io/blog/2022/08/23/kubernetes-v1-25-release/)
- [Falco Documentation](https://falco.org/docs/)
