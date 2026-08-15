# CKS Study Guide: Pod Security & Linux Kernel Hardening

![Pod security defense in depth](../images/cks-03-pod-security-defense-in-depth.jpg)

![SecurityContext pod versus container](../images/cks-11-securitycontext-pod-vs-container.jpg)

![Pod Security Admission levels](../images/cks-15-pod-security-admission-levels.jpg)

> **Target Audience:** Experienced K8s engineer (CKAD certified), preparing for CKS
> **Kubernetes Versions Covered:** 1.28 - 1.32+ (CKS exam environment)
> **Last Updated:** August 2026
> **Note:** WebSearch was unavailable due to org policy. Content is based on knowledge current through May 2025 (Kubernetes 1.32). Core concepts are stable; verify AppArmor field GA status against your exam cluster version.

---

## Table of Contents

1. [Pod Security Standards Masterclass](#1-pod-security-standards-masterclass)
2. [Security Context Mastery](#2-security-context-mastery)
3. [Linux Capabilities](#3-linux-capabilities)
4. [Seccomp Profiles](#4-seccomp-profiles)
5. [AppArmor](#5-apparmor)
6. [Minimize Microservice Vulnerabilities](#6-minimize-microservice-vulnerabilities)
7. [Quick Reference Tables](#7-quick-reference-tables)

---

## 1. Pod Security Standards Masterclass

### 1.1 Background: PodSecurityPolicy is Dead

PodSecurityPolicy (PSP) was **removed in Kubernetes 1.25**. Its replacement is **Pod Security Admission (PSA)**, which has been **GA since Kubernetes 1.25**. The CKS exam tests PSA exclusively -- you will never see PSP on a modern CKS exam.

Key differences from PSP:
- PSP was a cluster-scoped resource with RBAC bindings -- complex and error-prone
- PSA uses **namespace labels** -- simple, declarative, no RBAC needed
- PSA enforces the **Pod Security Standards** (three predefined levels)
- PSA is a built-in admission controller, not a separate API resource

### 1.2 The Three Pod Security Standards Levels

#### Privileged (Unrestricted)
- **Purpose:** Completely unrestricted. For system-level workloads like CNI, storage drivers, log collectors
- **Restrictions:** None
- **Use case:** `kube-system` namespace workloads, node-level agents

#### Baseline (Minimally Restrictive)
- **Purpose:** Prevents known privilege escalations. Allows most standard workloads
- **What it blocks:**
  - `hostNetwork: true`, `hostPID: true`, `hostIPC: true`
  - `privileged: true` containers
  - Capabilities beyond a small allowed set (AUDIT_WRITE, CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL, MKNOD, NET_BIND_SERVICE, SETFCAP, SETGID, SETPCAP, SETUID, SYS_CHROOT)
  - Adding capabilities with `NET_RAW` (dropped from allowed list in v1.25+)
  - HostPath volumes
  - Host ports (unless specifically allowed)
  - `procMount` other than Default
  - Seccomp profiles set to `Unconfined`
  - Sysctls outside the safe set
  - SELinux types outside the allowed set
  - `appArmorProfile` type set to anything other than RuntimeDefault or Localhost
- **Use case:** General application workloads

#### Restricted (Heavily Restrictive)
- **Purpose:** Hardened best practices. Maximum security
- **What it enforces (on top of baseline):**
  - `allowPrivilegeEscalation: false` (required)
  - `runAsNonRoot: true` (required)
  - Drop `ALL` capabilities (must explicitly drop ALL)
  - Only `NET_BIND_SERVICE` may be added back
  - Seccomp profile must be `RuntimeDefault` or `Localhost` (required)
  - Volume types limited to: configMap, csi, downwardAPI, emptyDir, ephemeral, persistentVolumeClaim, projected, secret
  - Containers must not set `runAsUser: 0`
- **Use case:** Security-sensitive workloads, multi-tenant clusters

### 1.3 PSA Namespace Labels

PSA is configured via namespace labels. There are three **modes** for each level:

```
pod-security.kubernetes.io/<MODE>: <LEVEL>
pod-security.kubernetes.io/<MODE>-version: <VERSION>
```

| Mode | Behavior |
|------|----------|
| `enforce` | Pods violating the policy are **rejected** |
| `warn` | Pods violating the policy trigger a **warning** to the user (but are admitted) |
| `audit` | Pods violating the policy generate an **audit log entry** (but are admitted) |

The `version` label pins to a specific Kubernetes version (e.g., `v1.30`). If omitted, it defaults to `latest`.

### 1.4 Applying PSA to a Namespace

**Example: Enforce restricted on a namespace:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-apps
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.30
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

**Apply to an existing namespace via kubectl:**

```bash
kubectl label namespace my-namespace \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/audit=restricted
```

**Common CKS exam pattern -- use warn first:**

```bash
# Step 1: Check what would break (dry-run with warnings)
kubectl label namespace my-namespace \
  pod-security.kubernetes.io/warn=restricted

# Step 2: Once workloads are compliant, enforce
kubectl label namespace my-namespace \
  pod-security.kubernetes.io/enforce=restricted
```

### 1.5 Transforming an Insecure Pod to Pass "Restricted" Level

**Before (fails restricted):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: insecure-app
spec:
  containers:
  - name: app
    image: nginx:1.27
    ports:
    - containerPort: 80
```

**After (passes restricted):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL: required by restricted
    runAsUser: 1000                         # POD-LEVEL: non-root UID
    runAsGroup: 1000                        # POD-LEVEL: non-root GID
    fsGroup: 1000                           # POD-LEVEL: file system group
    seccompProfile:                         # POD-LEVEL: required by restricted
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx:1.27
    ports:
    - containerPort: 8080                   # Non-privileged port (>1024)
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false       # CONTAINER-LEVEL: required by restricted
      readOnlyRootFilesystem: true          # CONTAINER-LEVEL: best practice
      capabilities:                         # CONTAINER-LEVEL
        drop:
        - ALL                               # required by restricted: drop ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}                            # Only allowed volume types
```

**Restricted level checklist (must satisfy ALL):**

- [ ] `runAsNonRoot: true` (pod or container level)
- [ ] `allowPrivilegeEscalation: false` (every container)
- [ ] `capabilities.drop: ["ALL"]` (every container)
- [ ] Only `NET_BIND_SERVICE` may be added back
- [ ] `seccompProfile.type: RuntimeDefault` or `Localhost` (pod or container level)
- [ ] No `hostNetwork`, `hostPID`, `hostIPC`
- [ ] No `privileged: true`
- [ ] No `hostPath` volumes
- [ ] `runAsUser` must not be `0`
- [ ] Volume types limited to safe list

### 1.6 Cluster-Wide PSA Defaults (AdmissionConfiguration)

For CKS, you may be asked to configure cluster-wide defaults:

```yaml
# /etc/kubernetes/admission/admission-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: PodSecurity
  configuration:
    apiVersion: pod-security.admission.config.k8s.io/v1
    kind: PodSecurityConfiguration
    defaults:
      enforce: "baseline"
      enforce-version: "latest"
      warn: "restricted"
      warn-version: "latest"
      audit: "restricted"
      audit-version: "latest"
    exemptions:
      usernames: []
      runtimeClasses: []
      namespaces:
      - kube-system
```

Then reference in the API server:

```
--admission-control-config-file=/etc/kubernetes/admission/admission-config.yaml
```

---

## 2. Security Context Mastery

![From insecure to restricted — pod transformation guide](../images/cks-23-pod-transformation-guide.jpg)

### 2.1 Pod-Level vs Container-Level Fields

This is a critical distinction for the CKS exam. Getting the placement wrong causes YAML validation errors or silent non-application.

#### Fields That Are ONLY Pod-Level (`spec.securityContext`)

| Field | Purpose |
|-------|---------|
| `fsGroup` | GID applied to all volumes mounted by the pod |
| `fsGroupChangePolicy` | Controls when fsGroup ownership is applied ("OnRootMismatch" or "Always") |
| `supplementalGroups` | Additional GIDs for the pod's processes |
| `sysctls` | Kernel parameters to set for the pod |

#### Fields That Are ONLY Container-Level (`spec.containers[].securityContext`)

| Field | Purpose |
|-------|---------|
| `allowPrivilegeEscalation` | Whether a process can gain more privileges than its parent |
| `privileged` | Run container in privileged mode (full host access) |
| `readOnlyRootFilesystem` | Mount root filesystem as read-only |
| `capabilities` | Linux capabilities to add or drop |
| `procMount` | Type of proc mount (Default or Unmasked) |

#### Fields That Exist at BOTH Levels (Container overrides Pod)

| Field | Pod-Level Path | Container-Level Path | Precedence |
|-------|---------------|---------------------|------------|
| `runAsUser` | `spec.securityContext.runAsUser` | `spec.containers[].securityContext.runAsUser` | Container wins |
| `runAsGroup` | `spec.securityContext.runAsGroup` | `spec.containers[].securityContext.runAsGroup` | Container wins |
| `runAsNonRoot` | `spec.securityContext.runAsNonRoot` | `spec.containers[].securityContext.runAsNonRoot` | Container wins |
| `seccompProfile` | `spec.securityContext.seccompProfile` | `spec.containers[].securityContext.seccompProfile` | Container wins |
| `seLinuxOptions` | `spec.securityContext.seLinuxOptions` | `spec.containers[].securityContext.seLinuxOptions` | Container wins |
| `appArmorProfile` | `spec.securityContext.appArmorProfile` | `spec.containers[].securityContext.appArmorProfile` | Container wins |
| `windowsOptions` | `spec.securityContext.windowsOptions` | `spec.containers[].securityContext.windowsOptions` | Container wins |

**Precedence Rule:** When the same field is set at both levels, the **container-level value always overrides** the pod-level value for that specific container. Unset container-level fields inherit from pod-level.

### 2.2 Complete SecurityContext Reference YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:                           # === POD-LEVEL ===
    runAsUser: 1000                          # BOTH (default UID for all containers)
    runAsGroup: 3000                         # BOTH (default GID for all containers)
    runAsNonRoot: true                       # BOTH (reject if image runs as root)
    fsGroup: 2000                            # POD-ONLY (GID for mounted volumes)
    fsGroupChangePolicy: "OnRootMismatch"    # POD-ONLY
    supplementalGroups: [4000, 5000]         # POD-ONLY (additional GIDs)
    seccompProfile:                          # BOTH (default seccomp for all containers)
      type: RuntimeDefault
    seLinuxOptions:                           # BOTH (default SELinux for all containers)
      level: "s0:c123,c456"
    sysctls:                                 # POD-ONLY
    - name: net.core.somaxconn
      value: "1024"
    appArmorProfile:                         # BOTH (K8s 1.30+, default for all containers)
      type: RuntimeDefault

  containers:
  - name: app
    image: busybox:1.36
    securityContext:                          # === CONTAINER-LEVEL ===
      runAsUser: 2000                        # BOTH (overrides pod's 1000 for this container)
      runAsGroup: 4000                       # BOTH (overrides pod's 3000)
      runAsNonRoot: true                     # BOTH (overrides pod-level)
      allowPrivilegeEscalation: false        # CONTAINER-ONLY
      privileged: false                      # CONTAINER-ONLY
      readOnlyRootFilesystem: true           # CONTAINER-ONLY
      capabilities:                          # CONTAINER-ONLY
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
      seccompProfile:                        # BOTH (overrides pod-level for this container)
        type: RuntimeDefault
      procMount: Default                     # CONTAINER-ONLY
      appArmorProfile:                       # BOTH (K8s 1.30+, overrides pod-level)
        type: RuntimeDefault
```

### 2.3 SecurityContext Exercises

#### Set A: Identify What's Insecure (10 exercises)

**Exercise SC-A01:** Identify all security issues in this pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a01
spec:
  containers:
  - name: web
    image: nginx:1.27
    securityContext:
      privileged: true
      runAsUser: 0
```

<details>
<summary>Answer SC-A01</summary>

Issues:
1. `privileged: true` -- container has full host access, can see all devices, bypass all security modules
2. `runAsUser: 0` -- explicitly running as root
3. Missing `allowPrivilegeEscalation: false`
4. Missing `readOnlyRootFilesystem: true`
5. Missing `capabilities.drop: ["ALL"]`
6. Missing `seccompProfile` (defaults to Unconfined)
7. Missing `runAsNonRoot: true` at pod level

</details>

---

**Exercise SC-A02:** What is wrong with this security configuration?

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a02
spec:
  securityContext:
    runAsNonRoot: true
  containers:
  - name: app
    image: alpine:3.19
    securityContext:
      runAsUser: 0
      allowPrivilegeEscalation: false
```

<details>
<summary>Answer SC-A02</summary>

Issues:
1. **Contradiction:** Pod-level sets `runAsNonRoot: true`, but container-level sets `runAsUser: 0` (root). Container-level overrides pod-level, so this pod will be **rejected** because the container wants UID 0 but `runAsNonRoot: true` at pod-level also applies (the container does not override `runAsNonRoot`). Actually, since `runAsNonRoot` is not set at container level, it inherits `true` from pod level, and `runAsUser: 0` conflicts with it. The pod will fail admission.
2. Missing `capabilities.drop: ["ALL"]`
3. Missing `readOnlyRootFilesystem: true`
4. Missing `seccompProfile`

</details>

---

**Exercise SC-A03:** Rate the security of this pod (1-10, 10 = most secure).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a03
spec:
  hostNetwork: true
  hostPID: true
  containers:
  - name: debug
    image: busybox:1.36
    command: ["sleep", "3600"]
    securityContext:
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
```

<details>
<summary>Answer SC-A03</summary>

Rating: **2/10** -- despite having some container-level hardening, the pod-level settings are catastrophic:
1. `hostNetwork: true` -- container shares the node's network namespace, can see all node traffic
2. `hostPID: true` -- container can see all host processes, enables process injection attacks
3. Missing `runAsNonRoot: true`
4. Missing `capabilities.drop: ["ALL"]`
5. Missing `seccompProfile`
6. The `readOnlyRootFilesystem` and `allowPrivilegeEscalation: false` are good but insufficient when host namespaces are shared

</details>

---

**Exercise SC-A04:** Identify the security anti-pattern.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a04
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      capabilities:
        add:
        - SYS_ADMIN
        - NET_ADMIN
        - SYS_PTRACE
      allowPrivilegeEscalation: true
```

<details>
<summary>Answer SC-A04</summary>

Issues:
1. `SYS_ADMIN` -- near-root capability. Allows mounting filesystems, using `clone()` with new namespaces, many kernel operations. This single capability is almost equivalent to running as privileged.
2. `NET_ADMIN` -- can modify routing tables, firewall rules, network interfaces. Enables network-level attacks.
3. `SYS_PTRACE` -- can trace and control other processes, read their memory. Enables container escape via process injection.
4. `allowPrivilegeEscalation: true` -- allows processes to gain more privileges (e.g., via SUID binaries).
5. No capabilities are dropped -- all default Linux capabilities remain.
6. Missing `runAsNonRoot`, `readOnlyRootFilesystem`, `seccompProfile`.

</details>

---

**Exercise SC-A05:** What happens when this pod starts?

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a05
spec:
  securityContext:
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: writer
    image: busybox:1.36
    command: ["sh", "-c", "id && ls -la /data"]
    volumeMounts:
    - name: data-vol
      mountPath: /data
  volumes:
  - name: data-vol
    emptyDir: {}
```

<details>
<summary>Answer SC-A05</summary>

What happens:
1. The container runs as UID `1000` (from pod-level `runAsUser`)
2. The primary GID is `0` (root group -- no `runAsGroup` is set, so default GID is 0)
3. The `/data` directory and its files will have group ownership of GID `2000` (from `fsGroup`)
4. `id` output will show: `uid=1000 gid=0 groups=2000`
5. Files created in `/data` will be owned by `1000:2000`

**Security gap:** No `runAsGroup` is set, so the primary group is root (GID 0). You should always set `runAsGroup` alongside `runAsUser`.

</details>

---

**Exercise SC-A06:** Spot the misconfiguration.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a06
spec:
  containers:
  - name: app
    image: nginx:1.27
    securityContext:
      fsGroup: 1000
      readOnlyRootFilesystem: true
```

<details>
<summary>Answer SC-A06</summary>

**`fsGroup` is a pod-level only field.** Placing it under `containers[].securityContext` is invalid and will cause an API validation error. The correct placement is `spec.securityContext.fsGroup`.

Corrected:
```yaml
spec:
  securityContext:
    fsGroup: 1000
  containers:
  - name: app
    image: nginx:1.27
    securityContext:
      readOnlyRootFilesystem: true
```

</details>

---

**Exercise SC-A07:** This pod is supposed to run securely. What's missing?

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a07
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
  containers:
  - name: app
    image: myapp:2.0
    securityContext:
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

<details>
<summary>Answer SC-A07</summary>

Missing:
1. `allowPrivilegeEscalation: false` -- not set at container level (defaults to `true` if not explicitly set, though this depends on capabilities). Best practice is to always set it explicitly to `false`.
2. `seccompProfile` -- no seccomp profile is set at either level. Should be `RuntimeDefault` or `Localhost` for restricted compliance.
3. `fsGroup` -- not set, so mounted volumes may not be writable by the non-root user.
4. No resource limits (not securityContext but related to security -- DoS prevention).

</details>

---

**Exercise SC-A08:** Identify the hidden privilege escalation path.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a08
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
  containers:
  - name: app
    image: myapp:3.0
    securityContext:
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - SETUID
        - SETGID
```

<details>
<summary>Answer SC-A08</summary>

**Hidden privilege escalation:** The `SETUID` and `SETGID` capabilities allow the process to change its user and group IDs. Even though the container starts as UID 65534 (nobody), a process inside can use `setuid(0)` to become root. This defeats the purpose of `runAsNonRoot`.

Also:
1. `allowPrivilegeEscalation` is not set to `false` -- this is required when SETUID/SETGID are present to be flagged.
2. Actually, even with `allowPrivilegeEscalation: false`, having SETUID/SETGID capabilities is dangerous because the capability itself allows UID changes.
3. Missing `seccompProfile`.

**Fix:** Remove `SETUID` and `SETGID` from added capabilities unless absolutely required.

</details>

---

**Exercise SC-A09:** What is the effective UID for each container?

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a09
spec:
  securityContext:
    runAsUser: 1000
  containers:
  - name: container-a
    image: busybox:1.36
    command: ["id"]
  - name: container-b
    image: busybox:1.36
    command: ["id"]
    securityContext:
      runAsUser: 2000
  - name: container-c
    image: busybox:1.36
    command: ["id"]
    securityContext:
      runAsUser: 0
```

<details>
<summary>Answer SC-A09</summary>

- **container-a:** UID `1000` (inherits from pod-level)
- **container-b:** UID `2000` (container-level overrides pod-level)
- **container-c:** UID `0` (container-level overrides pod-level -- runs as root!)

**Key insight:** Container-level always overrides pod-level. `container-c` runs as root despite the pod-level `runAsUser: 1000`. If `runAsNonRoot: true` were also set at pod-level, `container-c` would be rejected.

</details>

---

**Exercise SC-A10:** Identify ALL issues with this multi-container pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-a10
spec:
  hostIPC: true
  volumes:
  - name: host-vol
    hostPath:
      path: /etc/shadow
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      privileged: false
    volumeMounts:
    - name: host-vol
      mountPath: /secrets
  - name: sidecar
    image: busybox:1.36
    securityContext:
      runAsUser: 0
      capabilities:
        add:
        - NET_RAW
```

<details>
<summary>Answer SC-A10</summary>

Issues:
1. `hostIPC: true` -- shares IPC namespace with the node, enables shared memory attacks
2. `hostPath` volume mounting `/etc/shadow` -- direct access to host password file! Critical vulnerability.
3. Container `app` mounts `/etc/shadow` at `/secrets` -- can read all host user password hashes
4. Container `sidecar` runs as `runAsUser: 0` (root)
5. `NET_RAW` capability on sidecar -- enables raw socket access, packet sniffing, spoofing
6. Neither container has `allowPrivilegeEscalation: false`
7. Neither container has `readOnlyRootFilesystem: true`
8. Neither container has `capabilities.drop: ["ALL"]`
9. No `seccompProfile` set
10. No `runAsNonRoot` set at pod level

</details>

---

#### Set B: Add Correct SecurityContext (10 exercises)

**Exercise SC-B01:** Add the minimum securityContext to make this pod compliant with the "restricted" Pod Security Standard.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b01
spec:
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 8080
```

<details>
<summary>Answer SC-B01</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b01
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL (required by restricted)
    runAsUser: 1000                         # POD-LEVEL
    runAsGroup: 1000                        # POD-LEVEL
    seccompProfile:                         # POD-LEVEL (required by restricted)
      type: RuntimeDefault
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 8080
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL (required by restricted)
      capabilities:                        # CONTAINER-LEVEL (required by restricted)
        drop:
        - ALL
```

Note: `runAsNonRoot`, `seccompProfile` at pod-level covers all containers. `allowPrivilegeEscalation` and `capabilities` must be set per-container.

</details>

---

**Exercise SC-B02:** Secure this pod so it can write to `/data` but has a read-only root filesystem.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b02
spec:
  containers:
  - name: app
    image: myapp:1.0
    command: ["sh", "-c", "echo hello > /data/output.txt && cat /data/output.txt"]
  volumes:
  - name: data
    emptyDir: {}
```

<details>
<summary>Answer SC-B02</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b02
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL
    runAsUser: 1000                         # POD-LEVEL
    runAsGroup: 1000                        # POD-LEVEL
    fsGroup: 1000                           # POD-LEVEL -- ensures /data is writable
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    command: ["sh", "-c", "echo hello > /data/output.txt && cat /data/output.txt"]
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL -- root FS is read-only
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
    volumeMounts:
    - name: data
      mountPath: /data                     # This mount is writable (emptyDir)
    - name: tmp
      mountPath: /tmp                      # Many apps need a writable /tmp
  volumes:
  - name: data
    emptyDir: {}
  - name: tmp
    emptyDir: {}
```

Key pattern: `readOnlyRootFilesystem: true` + writable `emptyDir` mounts for data and tmp directories.

</details>

---

**Exercise SC-B03:** This is a log collector that needs to read host logs. Secure it as much as possible while preserving functionality.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b03
spec:
  containers:
  - name: log-collector
    image: fluentd:v1.16
    volumeMounts:
    - name: varlog
      mountPath: /var/log
  volumes:
  - name: varlog
    hostPath:
      path: /var/log
```

<details>
<summary>Answer SC-B03</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b03
spec:
  securityContext:                          # POD-LEVEL
    runAsUser: 1000                         # POD-LEVEL
    runAsGroup: 1000                        # POD-LEVEL
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: log-collector
    image: fluentd:v1.16
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
        add:
        - DAC_READ_SEARCH                  # CONTAINER-LEVEL: read files regardless of permission
    volumeMounts:
    - name: varlog
      mountPath: /var/log
      readOnly: true                       # Mount as read-only! Collector only reads.
    - name: tmp
      mountPath: /tmp
    - name: fluentd-buffer
      mountPath: /var/fluentd/buffer
  volumes:
  - name: varlog
    hostPath:
      path: /var/log
      type: Directory                      # Validate it's a directory
  - name: tmp
    emptyDir: {}
  - name: fluentd-buffer
    emptyDir: {}
```

Key: Mount hostPath as `readOnly: true`, drop ALL capabilities then add only `DAC_READ_SEARCH` for reading files across permission boundaries. Note: This pod cannot pass "restricted" PSA because it uses `hostPath` volumes and `DAC_READ_SEARCH`. For system-level workloads, use "baseline" or "privileged" PSA.

</details>

---

**Exercise SC-B04:** Secure this init container + main container pod. Both must be hardened.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b04
spec:
  initContainers:
  - name: init-db
    image: busybox:1.36
    command: ["sh", "-c", "until nslookup mydb; do sleep 2; done"]
  containers:
  - name: app
    image: myapp:2.0
```

<details>
<summary>Answer SC-B04</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b04
spec:
  securityContext:                          # POD-LEVEL (applies to init + main containers)
    runAsNonRoot: true                      # POD-LEVEL
    runAsUser: 1000                         # POD-LEVEL
    runAsGroup: 1000                        # POD-LEVEL
    fsGroup: 1000                           # POD-LEVEL
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  initContainers:
  - name: init-db
    image: busybox:1.36
    command: ["sh", "-c", "until nslookup mydb; do sleep 2; done"]
    securityContext:                        # CONTAINER-LEVEL (init containers need it too!)
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
  containers:
  - name: app
    image: myapp:2.0
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
```

**CKS trap:** Init containers must ALSO have securityContext set. Pod Security Standards check ALL containers including init containers. Forgetting init containers is a common exam mistake.

</details>

---

**Exercise SC-B05:** Add securityContext so this pod runs as UID 1000 by default, but the sidecar runs as UID 2000.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b05
spec:
  containers:
  - name: app
    image: myapp:1.0
  - name: sidecar
    image: busybox:1.36
    command: ["sleep", "3600"]
```

<details>
<summary>Answer SC-B05</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b05
spec:
  securityContext:                          # POD-LEVEL
    runAsUser: 1000                         # POD-LEVEL: default UID for all containers
    runAsGroup: 1000                        # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
      # runAsUser NOT set -- inherits 1000 from pod-level
  - name: sidecar
    image: busybox:1.36
    command: ["sleep", "3600"]
    securityContext:                        # CONTAINER-LEVEL
      runAsUser: 2000                      # CONTAINER-LEVEL: overrides pod's 1000
      runAsGroup: 2000                     # CONTAINER-LEVEL: override for consistency
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
```

</details>

---

**Exercise SC-B06:** This web server needs to bind to port 80. Add security context that allows this while remaining as restrictive as possible.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b06
spec:
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 80
```

<details>
<summary>Answer SC-B06</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b06
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL
    runAsUser: 1000                         # POD-LEVEL
    runAsGroup: 1000                        # POD-LEVEL
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 80
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE                 # CONTAINER-LEVEL: allows binding to ports < 1024
```

`NET_BIND_SERVICE` is the **only** capability allowed by the "restricted" Pod Security Standard. This is the correct way to handle low-port binding without root.

Note: Many modern images (like `nginxinc/nginx-unprivileged`) listen on port 8080 instead, eliminating the need for even this capability.

</details>

---

**Exercise SC-B07:** Secure this pod that runs a database needing persistent storage.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b07
spec:
  containers:
  - name: postgres
    image: postgres:16
    env:
    - name: POSTGRES_PASSWORD
      value: "mysecretpassword"
    volumeMounts:
    - name: pgdata
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: pgdata
    persistentVolumeClaim:
      claimName: pg-pvc
```

<details>
<summary>Answer SC-B07</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b07
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL
    runAsUser: 999                          # POD-LEVEL (postgres UID in official image)
    runAsGroup: 999                         # POD-LEVEL (postgres GID)
    fsGroup: 999                            # POD-LEVEL: ensures PVC files are accessible
    fsGroupChangePolicy: "OnRootMismatch"  # POD-LEVEL: performance optimization
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: postgres
    image: postgres:16
    env:
    - name: POSTGRES_PASSWORD
      valueFrom:                           # Use a Secret instead of plaintext!
        secretKeyRef:
          name: pg-secret
          key: password
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
    volumeMounts:
    - name: pgdata
      mountPath: /var/lib/postgresql/data
    - name: run
      mountPath: /var/run/postgresql        # Postgres needs this writable
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: pgdata
    persistentVolumeClaim:
      claimName: pg-pvc
  - name: run
    emptyDir: {}
  - name: tmp
    emptyDir: {}
```

Key changes:
1. Password moved from plaintext `value` to `secretKeyRef`
2. `fsGroup: 999` ensures PVC is writable by postgres user
3. `readOnlyRootFilesystem` with writable mounts for runtime dirs

</details>

---

**Exercise SC-B08:** Secure this CronJob. Remember: CronJob -> Job -> Pod template.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sc-b08
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: busybox:1.36
            command: ["sh", "-c", "echo cleanup done"]
          restartPolicy: OnFailure
```

<details>
<summary>Answer SC-B08</summary>

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sc-b08
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          securityContext:                          # POD-LEVEL (inside pod template)
            runAsNonRoot: true                      # POD-LEVEL
            runAsUser: 1000                         # POD-LEVEL
            runAsGroup: 1000                        # POD-LEVEL
            seccompProfile:                         # POD-LEVEL
              type: RuntimeDefault
          containers:
          - name: cleanup
            image: busybox:1.36
            command: ["sh", "-c", "echo cleanup done"]
            securityContext:                        # CONTAINER-LEVEL
              allowPrivilegeEscalation: false       # CONTAINER-LEVEL
              readOnlyRootFilesystem: true          # CONTAINER-LEVEL
              capabilities:                         # CONTAINER-LEVEL
                drop:
                - ALL
          restartPolicy: OnFailure
          automountServiceAccountToken: false       # CronJobs rarely need API access
```

CKS tip: SecurityContext goes at the same path in the pod template, not at the CronJob or Job level. Also set `automountServiceAccountToken: false` for jobs that don't need K8s API access.

</details>

---

**Exercise SC-B09:** This multi-container pod needs containers to communicate via shared volume. Secure it with different UIDs per container, both able to write to the shared volume.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b09
spec:
  containers:
  - name: producer
    image: busybox:1.36
    command: ["sh", "-c", "while true; do date >> /shared/log.txt; sleep 5; done"]
    volumeMounts:
    - name: shared
      mountPath: /shared
  - name: consumer
    image: busybox:1.36
    command: ["sh", "-c", "tail -f /shared/log.txt"]
    volumeMounts:
    - name: shared
      mountPath: /shared
  volumes:
  - name: shared
    emptyDir: {}
```

<details>
<summary>Answer SC-B09</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-b09
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL
    fsGroup: 3000                           # POD-LEVEL: both containers share this GID on the volume
    seccompProfile:                         # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: producer
    image: busybox:1.36
    command: ["sh", "-c", "while true; do date >> /shared/log.txt; sleep 5; done"]
    securityContext:                        # CONTAINER-LEVEL
      runAsUser: 1000                      # CONTAINER-LEVEL: different UID
      runAsGroup: 1000                     # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
    volumeMounts:
    - name: shared
      mountPath: /shared
  - name: consumer
    image: busybox:1.36
    command: ["sh", "-c", "tail -f /shared/log.txt"]
    securityContext:                        # CONTAINER-LEVEL
      runAsUser: 2000                      # CONTAINER-LEVEL: different UID
      runAsGroup: 2000                     # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
    volumeMounts:
    - name: shared
      mountPath: /shared
  volumes:
  - name: shared
    emptyDir: {}
```

**Key insight:** `fsGroup` at pod-level sets the group owner of volume files to GID 3000 for ALL containers. Both containers (running as different UIDs) can write to the shared volume because `fsGroup` adds supplemental group 3000 to both processes, and emptyDir files get group-writable permissions.

</details>

---

**Exercise SC-B10:** Harden this Deployment (not just a Pod). Apply security to the Deployment's pod template.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sc-b10
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: mywebapp:2.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
```

<details>
<summary>Answer SC-B10</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sc-b10
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      automountServiceAccountToken: false    # Disable unless needed
      securityContext:                        # POD-LEVEL (in Deployment's pod template)
        runAsNonRoot: true                    # POD-LEVEL
        runAsUser: 1000                       # POD-LEVEL
        runAsGroup: 1000                      # POD-LEVEL
        fsGroup: 1000                         # POD-LEVEL
        seccompProfile:                       # POD-LEVEL
          type: RuntimeDefault
      containers:
      - name: webapp
        image: mywebapp:2.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:                             # Add limits for DoS prevention
            cpu: 500m
            memory: 256Mi
        securityContext:                      # CONTAINER-LEVEL
          allowPrivilegeEscalation: false     # CONTAINER-LEVEL
          readOnlyRootFilesystem: true        # CONTAINER-LEVEL
          capabilities:                       # CONTAINER-LEVEL
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir:
          sizeLimit: 100Mi                   # Limit tmpfs size
```

</details>

---

#### Set C: Fix This Broken SecurityContext (10 exercises)

**Exercise SC-C01:** This pod won't start. Fix the securityContext error.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c01
spec:
  securityContext:
    runAsNonRoot: true
  containers:
  - name: app
    image: nginx:1.27
```

<details>
<summary>Answer SC-C01</summary>

**Problem:** `runAsNonRoot: true` is set, but the official `nginx:1.27` image runs as root by default (UID 0). Without specifying a `runAsUser`, the container runtime checks the image's default user, finds it's root, and rejects the pod.

**Error message:** `Error: container has runAsNonRoot and image will run as root`

**Fix -- Option A:** Set a specific non-root UID:
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000          # POD-LEVEL: force non-root UID
```

**Fix -- Option B:** Use an image that defaults to non-root:
```yaml
  containers:
  - name: app
    image: nginxinc/nginx-unprivileged:1.27   # Already runs as UID 101
```

</details>

---

**Exercise SC-C02:** This pod fails with `CrashLoopBackOff`. The logs show "read-only file system".

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c02
spec:
  containers:
  - name: app
    image: nginx:1.27
    securityContext:
      readOnlyRootFilesystem: true
      runAsUser: 1000
```

<details>
<summary>Answer SC-C02</summary>

**Problem:** Nginx needs to write to `/var/cache/nginx`, `/var/run`, and `/tmp` at startup. With `readOnlyRootFilesystem: true`, these writes fail.

**Fix:** Add writable emptyDir mounts for the directories nginx needs:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c02
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx:1.27
    securityContext:
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL: keep this
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
    volumeMounts:
    - name: cache
      mountPath: /var/cache/nginx
    - name: run
      mountPath: /var/run
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: cache
    emptyDir: {}
  - name: run
    emptyDir: {}
  - name: tmp
    emptyDir: {}
```

**CKS pattern:** `readOnlyRootFilesystem` + `emptyDir` for writable paths is the standard hardening pattern.

</details>

---

**Exercise SC-C03:** This pod is rejected by the "restricted" PSA. Fix it to pass.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c03
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - NET_RAW
        - SYS_ADMIN
```

<details>
<summary>Answer SC-C03</summary>

**Problems:**
1. `capabilities.drop` only drops specific capabilities, but "restricted" requires dropping **ALL**
2. Missing `seccompProfile` (required by restricted)

**Fix:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c03
spec:
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # POD-LEVEL
    runAsUser: 1000                         # POD-LEVEL
    seccompProfile:                         # POD-LEVEL -- was missing
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL                              # Must be ALL, not individual capabilities
```

</details>

---

**Exercise SC-C04:** The API server rejects this YAML with a validation error. Fix it.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c04
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      fsGroup: 1000
      supplementalGroups: [2000]
      sysctls:
      - name: net.core.somaxconn
        value: "1024"
      capabilities:
        drop:
        - ALL
```

<details>
<summary>Answer SC-C04</summary>

**Problem:** Three fields are placed at the wrong level:
- `fsGroup` -- POD-LEVEL ONLY
- `supplementalGroups` -- POD-LEVEL ONLY
- `sysctls` -- POD-LEVEL ONLY

These fields are only valid under `spec.securityContext`, not under `spec.containers[].securityContext`.

**Fix:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c04
spec:
  securityContext:                          # POD-LEVEL
    fsGroup: 1000                           # POD-LEVEL ONLY -- moved here
    supplementalGroups: [2000]              # POD-LEVEL ONLY -- moved here
    sysctls:                                # POD-LEVEL ONLY -- moved here
    - name: net.core.somaxconn
      value: "1024"
  containers:
  - name: app
    image: myapp:1.0
    securityContext:                        # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL -- stays here
        drop:
        - ALL
```

</details>

---

**Exercise SC-C05:** Two containers should both be non-root. Container B keeps starting as root. Why?

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c05
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: container-a
    image: busybox:1.36
    command: ["id"]
  - name: container-b
    image: busybox:1.36
    command: ["id"]
    securityContext:
      runAsUser: 0
```

<details>
<summary>Answer SC-C05</summary>

**Problem:** `container-b` has `runAsUser: 0` at container-level, which **overrides** the pod-level `runAsUser: 1000`. However, `runAsNonRoot: true` at pod-level should cause rejection... unless `runAsNonRoot` is overridden at container level too.

Actually, in this case, `runAsNonRoot: true` is at pod level and NOT overridden at container level for container-b. So container-b inherits `runAsNonRoot: true` but also sets `runAsUser: 0`. This causes a **conflict** and the pod will be rejected with an error.

If the question states "container B keeps starting as root," then perhaps `runAsNonRoot` was accidentally overridden:

**Fix:** Remove the container-level `runAsUser: 0`:

```yaml
  - name: container-b
    image: busybox:1.36
    command: ["id"]
    # No container-level securityContext -- inherits pod's runAsUser: 1000
```

Or if container-b needs a different non-root UID:

```yaml
  - name: container-b
    image: busybox:1.36
    command: ["id"]
    securityContext:
      runAsUser: 2000                      # Different non-root UID
```

</details>

---

**Exercise SC-C06:** This pod passes "restricted" PSA but has a security gap. Find and fix it.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c06
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
  serviceAccountName: cluster-admin-sa
  automountServiceAccountToken: true
```

<details>
<summary>Answer SC-C06</summary>

**Problem:** The pod uses a service account named `cluster-admin-sa` and auto-mounts its token. If this SA has `cluster-admin` ClusterRoleBinding, the pod has full cluster access despite all the securityContext hardening. A container escape or application vulnerability gives the attacker full cluster control.

**Fix:**

```yaml
  serviceAccountName: app-sa              # Use a least-privilege service account
  automountServiceAccountToken: false     # Don't mount token unless app needs K8s API access
```

If the app needs API access, create a dedicated SA with minimal RBAC:
```bash
kubectl create serviceaccount app-sa
kubectl create role app-role --verb=get,list --resource=configmaps
kubectl create rolebinding app-rb --role=app-role --serviceaccount=default:app-sa
```

</details>

---

**Exercise SC-C07:** This pod is supposed to have readOnlyRootFilesystem but the application writes config at startup. Fix without removing readOnlyRootFilesystem.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c07
spec:
  containers:
  - name: app
    image: myapp:1.0
    command: ["sh", "-c", "echo 'key=val' > /app/config/app.conf && ./start.sh"]
    securityContext:
      readOnlyRootFilesystem: true
```

<details>
<summary>Answer SC-C07</summary>

**Fix:** Mount a writable emptyDir at the config path, and use an init container or configMap to provide the config:

**Option A: emptyDir for writable config:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c07
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  initContainers:
  - name: init-config
    image: busybox:1.36
    command: ["sh", "-c", "echo 'key=val' > /config/app.conf"]
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    volumeMounts:
    - name: config
      mountPath: /config
  containers:
  - name: app
    image: myapp:1.0
    command: ["./start.sh"]
    securityContext:
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL: keep it
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
    volumeMounts:
    - name: config
      mountPath: /app/config
      readOnly: true                       # Main container only reads
  volumes:
  - name: config
    emptyDir: {}
```

**Option B: Use a ConfigMap (preferred):**

```yaml
    volumeMounts:
    - name: config
      mountPath: /app/config
  volumes:
  - name: config
    configMap:
      name: app-config
```

</details>

---

**Exercise SC-C08:** Fix this pod -- it fails because the seccomp profile is not found.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c08
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: my-seccomp-profile.json
  containers:
  - name: app
    image: myapp:1.0
```

<details>
<summary>Answer SC-C08</summary>

**Problem:** The `localhostProfile` path is relative to the kubelet's seccomp directory: `/var/lib/kubelet/seccomp/`. The profile file `my-seccomp-profile.json` must exist at `/var/lib/kubelet/seccomp/my-seccomp-profile.json` on the node where the pod is scheduled.

**Possible fixes:**

1. Ensure the file exists on the node:
```bash
# SSH to the node
sudo cp my-seccomp-profile.json /var/lib/kubelet/seccomp/my-seccomp-profile.json
```

2. If the file is in a subdirectory:
```yaml
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/my-seccomp-profile.json
      # Looks for: /var/lib/kubelet/seccomp/profiles/my-seccomp-profile.json
```

3. If you don't need a custom profile, use RuntimeDefault:
```yaml
    seccompProfile:
      type: RuntimeDefault                 # Uses container runtime's built-in profile
```

</details>

---

**Exercise SC-C09:** This pod starts but containers cannot communicate on localhost. Fix the security issue.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c09
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 80
    securityContext:
      capabilities:
        drop:
        - ALL
        - NET_BIND_SERVICE
  - name: proxy
    image: envoyproxy/envoy:v1.29
    ports:
    - containerPort: 8080
```

<details>
<summary>Answer SC-C09</summary>

**Problem:** The `web` container drops ALL capabilities AND explicitly drops `NET_BIND_SERVICE` again (redundant but not the issue). The real issue is that nginx needs to bind to port 80 (a privileged port < 1024), and without `NET_BIND_SERVICE` it cannot.

Also, both containers in the same pod already share the same network namespace (localhost communication works by default in pods) -- so the "cannot communicate" issue is likely because nginx fails to start (cannot bind port 80).

**Fix:**

```yaml
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 8080                  # Use non-privileged port instead
    securityContext:
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      readOnlyRootFilesystem: true         # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL
        # Don't need NET_BIND_SERVICE if using port > 1024
```

Or if port 80 is required:
```yaml
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE                 # Add back after dropping ALL
```

</details>

---

**Exercise SC-C10:** This multi-container pod fails "restricted" PSA. One container is compliant, one is not. Fix only the non-compliant container.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sc-c10
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: compliant
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
  - name: non-compliant
    image: helper:1.0
    securityContext:
      allowPrivilegeEscalation: true
      capabilities:
        add:
        - SYS_PTRACE
```

<details>
<summary>Answer SC-C10</summary>

**Problems with `non-compliant` container:**
1. `allowPrivilegeEscalation: true` -- restricted requires `false`
2. `capabilities.add: SYS_PTRACE` -- restricted only allows adding `NET_BIND_SERVICE`
3. No `capabilities.drop: ["ALL"]` -- restricted requires dropping ALL

**Fix for `non-compliant` container only:**

```yaml
  - name: non-compliant
    image: helper:1.0
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL: changed from true
      capabilities:                        # CONTAINER-LEVEL
        drop:
        - ALL                              # CONTAINER-LEVEL: added
        # Removed SYS_PTRACE -- not allowed by restricted
```

</details>

---

## 3. Linux Capabilities

![Linux capabilities reference — the armory](../images/cks-20-linux-capabilities-reference.jpg)

### 3.1 What Are Linux Capabilities?

Linux capabilities break the monolithic root privilege into distinct units. Instead of a process being either fully privileged (root/UID 0) or unprivileged, capabilities allow fine-grained privilege assignment.

Traditional Linux: `root (UID 0)` = all privileges, `non-root` = no special privileges.

Capabilities: Each privilege is a separate flag that can be independently granted or revoked.

**Why this matters for Kubernetes/CKS:**
- Containers run Linux processes. Capabilities determine what those processes can do.
- Default Docker/containerd containers get a set of ~14 capabilities.
- The CKS exam tests your ability to minimize capabilities to reduce attack surface.
- Pod Security Standards enforce capability restrictions.

### 3.2 Important Capabilities for CKS

#### High-Risk Capabilities (almost never allow these)

| Capability | What It Allows | Risk Level |
|-----------|---------------|------------|
| `SYS_ADMIN` | Mount filesystems, configure namespaces, many kernel ops | **CRITICAL** -- nearly equivalent to full root |
| `NET_ADMIN` | Configure network interfaces, routing, firewall rules, raw sockets | **HIGH** -- network-level attacks |
| `SYS_PTRACE` | Trace/debug other processes, read their memory | **HIGH** -- container escape via process injection |
| `NET_RAW` | Raw sockets, packet crafting, sniffing | **HIGH** -- spoofing, MITM attacks |
| `SYS_MODULE` | Load/unload kernel modules | **CRITICAL** -- kernel-level compromise |
| `SYS_RAWIO` | Raw I/O port access | **CRITICAL** -- direct hardware access |
| `SYS_BOOT` | Reboot the system | **HIGH** -- denial of service |
| `DAC_OVERRIDE` | Bypass file read/write/execute permission checks | **HIGH** -- read any file |
| `DAC_READ_SEARCH` | Bypass file read and directory search permission checks | **MEDIUM** -- read any file |

#### Commonly Needed Capabilities

| Capability | What It Allows | Typical Use Case |
|-----------|---------------|-----------------|
| `NET_BIND_SERVICE` | Bind to ports below 1024 | Web servers on port 80/443 |
| `CHOWN` | Change file ownership | File management processes |
| `SETUID` | Change UID of a process | Switching to non-root after startup |
| `SETGID` | Change GID of a process | Switching group after startup |
| `KILL` | Send signals to other processes | Process managers |
| `FOWNER` | Bypass permission checks on operations that require matching file owner | File management |

#### Default Container Capabilities (containerd/Docker)

By default, containers get these capabilities:
```
AUDIT_WRITE, CHOWN, DAC_OVERRIDE, FOWNER, FSETID, KILL,
MKNOD, NET_BIND_SERVICE, NET_RAW, SETFCAP, SETGID, SETPCAP,
SETUID, SYS_CHROOT
```

This default set is **too permissive** for most applications.

### 3.3 Best Practice: Drop ALL, Add Only What's Needed

```yaml
# CONTAINER-LEVEL ONLY -- capabilities cannot be set at pod level
securityContext:
  capabilities:
    drop:
    - ALL                    # Drop every capability
    add:
    - NET_BIND_SERVICE       # Add back only what's needed
```

**The "restricted" PSA requires:**
- `drop: ["ALL"]`
- Only `NET_BIND_SERVICE` may be added back

### 3.4 YAML Syntax Reference

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cap-demo
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:                    # CONTAINER-LEVEL ONLY for capabilities
      capabilities:                    # CONTAINER-LEVEL ONLY
        drop:                          # List of capabilities to remove
        - ALL                          # Special keyword: drops ALL capabilities
        add:                           # List of capabilities to add back
        - NET_BIND_SERVICE             # Must be UPPERCASE, no "CAP_" prefix
```

**Important syntax notes:**
- Capability names are **UPPERCASE** in Kubernetes YAML
- Do NOT include the `CAP_` prefix (use `NET_ADMIN` not `CAP_NET_ADMIN`)
- `capabilities` is a **container-level only** field
- `drop` is evaluated before `add` -- so `drop: ALL` + `add: NET_BIND_SERVICE` works correctly

### 3.5 Linux Capabilities Exercises (10)

**Exercise CAP-01:** Identify the excessive capabilities.

```yaml
securityContext:
  capabilities:
    add:
    - NET_ADMIN
    - SYS_ADMIN
    - SYS_PTRACE
    - NET_BIND_SERVICE
    - CHOWN
```

<details>
<summary>Answer CAP-01</summary>

Excessive capabilities:
1. `NET_ADMIN` -- allows full network reconfiguration. Almost never needed by applications.
2. `SYS_ADMIN` -- near-root. Absolutely should not be granted to application containers.
3. `SYS_PTRACE` -- allows debugging/tracing other processes. Only needed for specialized debugging tools.

Likely needed:
- `NET_BIND_SERVICE` -- if binding to ports < 1024
- `CHOWN` -- if the app changes file ownership (questionable -- often unnecessary)

Fix: `drop: ALL`, add only `NET_BIND_SERVICE` if needed. Challenge whether `CHOWN` is truly required.

</details>

---

**Exercise CAP-02:** This container runs a ping utility. What's the minimum capability set?

```yaml
containers:
- name: pinger
  image: busybox:1.36
  command: ["ping", "-c", "3", "google.com"]
  securityContext:
    capabilities:
      add:
      - NET_ADMIN
      - NET_RAW
      - SYS_ADMIN
```

<details>
<summary>Answer CAP-02</summary>

`ping` traditionally requires `NET_RAW` for raw ICMP sockets. However:
- `NET_ADMIN` is not needed for ping -- remove it
- `SYS_ADMIN` is definitely not needed -- remove it
- Modern kernels support ping via `net.ipv4.ping_group_range` sysctl, which can eliminate the need for `NET_RAW`

**Minimum fix:**
```yaml
    securityContext:
      capabilities:
        drop:
        - ALL
        add:
        - NET_RAW              # Only if kernel ping_group_range doesn't cover it
```

**Best fix (no capabilities):**
Use an image/kernel that supports unprivileged ping, and drop ALL with no adds.

</details>

---

**Exercise CAP-03:** Fix this: the app needs to bind to port 443 but the pod is rejected by "restricted" PSA.

```yaml
securityContext:
  capabilities:
    add:
    - NET_BIND_SERVICE
    - NET_ADMIN
```

<details>
<summary>Answer CAP-03</summary>

**Problem:** `NET_ADMIN` is not allowed by "restricted" PSA. Only `NET_BIND_SERVICE` is permitted.

**Fix:**
```yaml
securityContext:
  capabilities:
    drop:
    - ALL                      # Required by restricted
    add:
    - NET_BIND_SERVICE         # The only allowed add for restricted
```

</details>

---

**Exercise CAP-04:** Is this capability configuration secure?

```yaml
securityContext:
  capabilities:
    drop:
    - NET_RAW
    - SYS_ADMIN
```

<details>
<summary>Answer CAP-04</summary>

**No, this is insufficient.** Only two capabilities are dropped. The container still has all other default capabilities (~14 total), including:
- `DAC_OVERRIDE` (bypass file permissions)
- `CHOWN` (change file ownership)
- `SETUID`, `SETGID` (change user/group IDs)
- `FOWNER`, `FSETID`, etc.

**Fix:** Always use `drop: ["ALL"]` as the starting point:
```yaml
securityContext:
  capabilities:
    drop:
    - ALL
    add:                       # Only if needed
    - NET_BIND_SERVICE
```

</details>

---

**Exercise CAP-05:** The container needs to create device nodes. What's the minimum capability?

```yaml
containers:
- name: device-manager
  image: device-mgr:1.0
  securityContext:
    privileged: true
```

<details>
<summary>Answer CAP-05</summary>

**`privileged: true` is overkill.** Creating device nodes requires only `MKNOD`.

**Fix:**
```yaml
securityContext:
  privileged: false
  capabilities:
    drop:
    - ALL
    add:
    - MKNOD                   # Create special files (device nodes)
```

Note: In most CKS scenarios, application containers should NEVER need `MKNOD`. This is typically only for system-level DaemonSets. Question why the application needs device node creation.

</details>

---

**Exercise CAP-06:** Why does this container fail to chown files even though it runs as root?

```yaml
securityContext:
  runAsUser: 0
  capabilities:
    drop:
    - ALL
```

<details>
<summary>Answer CAP-06</summary>

**Answer:** The container drops ALL capabilities, including `CHOWN`. Even as root (UID 0), without the `CHOWN` capability, the process cannot change file ownership.

This demonstrates that **capabilities are independent of UID**. A root process without capabilities is significantly restricted.

**Fix (if chown is truly needed):**
```yaml
securityContext:
  runAsUser: 0               # Still root -- try to avoid this
  capabilities:
    drop:
    - ALL
    add:
    - CHOWN                  # Add back only CHOWN
```

**Better fix:** Redesign so the app doesn't need chown. Use `fsGroup` and proper volume permissions instead.

</details>

---

**Exercise CAP-07:** Convert this privileged container to use minimum capabilities. It needs to modify iptables rules.

```yaml
containers:
- name: firewall
  image: iptables-manager:1.0
  securityContext:
    privileged: true
```

<details>
<summary>Answer CAP-07</summary>

iptables requires `NET_ADMIN` and `NET_RAW`:

```yaml
containers:
- name: firewall
  image: iptables-manager:1.0
  securityContext:
    privileged: false                 # Remove privileged mode
    allowPrivilegeEscalation: false
    capabilities:
      drop:
      - ALL
      add:
      - NET_ADMIN                    # Required for iptables
      - NET_RAW                      # Required for iptables
```

Note: This will NOT pass "restricted" PSA because `NET_ADMIN` and `NET_RAW` are not in the restricted allowed list. This type of workload belongs in a "privileged" or "baseline" namespace (like `kube-system`).

</details>

---

**Exercise CAP-08:** Identify the capability needed: container must send signals to processes in other containers in the same pod.

<details>
<summary>Answer CAP-08</summary>

Containers in the same pod share the same PID namespace **only if `shareProcessNamespace: true`** is set at pod level. With shared PID namespace:

```yaml
spec:
  shareProcessNamespace: true          # POD-LEVEL
  containers:
  - name: signal-sender
    securityContext:
      capabilities:
        drop:
        - ALL
        add:
        - KILL                         # Send signals to other processes
```

Without `shareProcessNamespace`, containers have isolated PID namespaces and cannot see each other's processes regardless of capabilities.

The `KILL` capability allows sending signals (SIGTERM, SIGKILL, etc.) to processes owned by different UIDs.

</details>

---

**Exercise CAP-09:** Audit this DaemonSet's capabilities. It's a log forwarder that reads log files and sends them over HTTPS.

```yaml
securityContext:
  capabilities:
    add:
    - SYS_ADMIN
    - NET_ADMIN
    - NET_RAW
    - DAC_OVERRIDE
    - DAC_READ_SEARCH
    - CHOWN
    - FOWNER
    - SETUID
    - SETGID
```

<details>
<summary>Answer CAP-09</summary>

For a log forwarder that reads files and sends HTTPS:
- `SYS_ADMIN` -- **NOT NEEDED.** Remove.
- `NET_ADMIN` -- **NOT NEEDED.** Standard network operations (HTTPS) don't need this. Remove.
- `NET_RAW` -- **NOT NEEDED.** HTTPS uses normal sockets. Remove.
- `DAC_OVERRIDE` -- **MAYBE.** If reading files owned by other users. Prefer `DAC_READ_SEARCH` instead (read-only).
- `DAC_READ_SEARCH` -- **POSSIBLY NEEDED.** Allows reading any file regardless of permissions. Appropriate for a log collector.
- `CHOWN` -- **NOT NEEDED.** A log forwarder doesn't change file ownership. Remove.
- `FOWNER` -- **NOT NEEDED.** Remove.
- `SETUID` -- **NOT NEEDED.** Remove.
- `SETGID` -- **NOT NEEDED.** Remove.

**Minimal fix:**
```yaml
securityContext:
  capabilities:
    drop:
    - ALL
    add:
    - DAC_READ_SEARCH          # Only if log files have restrictive permissions
```

Even `DAC_READ_SEARCH` might be avoidable if the log directory is mounted with proper group permissions.

</details>

---

**Exercise CAP-10:** What capability is this pod missing? It crashes trying to adjust the system clock.

```yaml
containers:
- name: ntp-sync
  image: chrony:4.0
  securityContext:
    capabilities:
      drop:
      - ALL
      add:
      - NET_BIND_SERVICE
```

<details>
<summary>Answer CAP-10</summary>

**Missing: `SYS_TIME`** -- required to set the system clock.

```yaml
securityContext:
  capabilities:
    drop:
    - ALL
    add:
    - SYS_TIME               # Set system clock / hardware clock
    - NET_BIND_SERVICE        # Bind to NTP port 123 (< 1024)
```

Note: In Kubernetes, it's generally better to run NTP/chrony on the **node** level (not in a container), because clock changes affect the entire node. Container-level time adjustment is unusual and should be questioned.

</details>

---

## 4. Seccomp Profiles

![Seccomp architecture — the syscall filter](../images/cks-21-seccomp-architecture.jpg)

### 4.1 What is Seccomp?

**Seccomp (Secure Computing Mode)** restricts which **system calls** a process can make to the Linux kernel. It acts as a syscall firewall.

- **Without seccomp:** A container process can invoke any of 300+ Linux syscalls
- **With seccomp:** Only allowed syscalls work; blocked syscalls return an error or kill the process

**Why it matters for CKS:**
- Reduces kernel attack surface
- Prevents container escapes that rely on specific syscalls
- The "restricted" PSA **requires** a seccomp profile
- CKS tests seccomp configuration and troubleshooting

### 4.2 Seccomp Profile Types

| Type | Description | Use Case |
|------|-------------|----------|
| `RuntimeDefault` | Container runtime's built-in profile (containerd/CRI-O) | **Best default.** Blocks ~44 dangerous syscalls while allowing ~270+ common ones |
| `Localhost` | Custom profile stored on the node | Fine-grained control for specific workloads |
| `Unconfined` | No seccomp filtering | **Insecure.** Only for debugging or system-level workloads |

### 4.3 Seccomp Field Syntax (Current API -- NOT Annotations)

The old annotation method (`seccomp.security.alpha.kubernetes.io/pod`) is **deprecated and removed**. Use the `seccompProfile` field.

**Pod-Level (applies to all containers as default):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-pod
spec:
  securityContext:                         # POD-LEVEL
    seccompProfile:                        # POD-LEVEL (BOTH -- can also be container-level)
      type: RuntimeDefault                 # RuntimeDefault | Localhost | Unconfined
```

**Container-Level (overrides pod-level for this container):**

```yaml
spec:
  containers:
  - name: app
    securityContext:                        # CONTAINER-LEVEL
      seccompProfile:                      # CONTAINER-LEVEL (overrides pod-level)
        type: RuntimeDefault
```

**Localhost profile:**

```yaml
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/fine-grained.json
      # File must exist at: /var/lib/kubelet/seccomp/profiles/fine-grained.json
```

### 4.4 Where Localhost Profiles Are Stored

```
/var/lib/kubelet/seccomp/
  |- profiles/
  |    |- audit.json          # Logs all syscalls (for discovery)
  |    |- fine-grained.json   # Custom application profile
  |- my-profile.json          # Also valid (any path under seccomp/)
```

The `localhostProfile` value is **relative** to `/var/lib/kubelet/seccomp/`.

### 4.5 Custom Seccomp Profile Format

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "accept4", "bind", "clone", "close", "connect",
        "execve", "exit", "exit_group", "futex",
        "getdents64", "getpid", "ioctl", "mmap",
        "mprotect", "nanosleep", "openat", "read",
        "recvfrom", "rt_sigaction", "sendto", "socket",
        "stat", "write"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

**Actions:**
| Action | Behavior |
|--------|----------|
| `SCMP_ACT_ALLOW` | Allow the syscall |
| `SCMP_ACT_ERRNO` | Return an error (EPERM) -- blocks the syscall safely |
| `SCMP_ACT_KILL` | Kill the process immediately |
| `SCMP_ACT_KILL_PROCESS` | Kill the entire process (not just the thread) |
| `SCMP_ACT_LOG` | Allow but log (useful for auditing/discovery) |
| `SCMP_ACT_TRACE` | Notify a tracer |

**Audit/Discovery profile (log all syscalls to find what your app uses):**

```json
{
  "defaultAction": "SCMP_ACT_LOG"
}
```

### 4.6 Troubleshooting Workloads Blocked by Seccomp

**Symptoms:**
- Container starts but immediately crashes
- Application errors with "Operation not permitted" (EPERM)
- Mysterious "permission denied" errors not related to file permissions

**Diagnosis steps:**

```bash
# 1. Check pod events
kubectl describe pod <name>

# 2. Check container logs
kubectl logs <name>

# 3. Check syslog/audit log on the node for seccomp violations
# On the node:
sudo journalctl -k | grep -i seccomp
sudo cat /var/log/audit/audit.log | grep -i seccomp
# Look for: audit: type=1326 audit(...): auid=... uid=... ... syscall=<number> ...

# 4. Map syscall numbers to names
ausyscall --dump    # Shows all syscall number-to-name mappings

# 5. Temporary: switch to audit mode to identify needed syscalls
# Use a profile with "defaultAction": "SCMP_ACT_LOG"
```

**Common syscalls that trip seccomp:**
- `mount` (blocked by RuntimeDefault -- image builds that need mount will fail)
- `unshare` (namespace creation -- blocked by RuntimeDefault)
- `clone` with `CLONE_NEWUSER` (user namespace -- blocked)
- `ptrace` (debugging -- blocked)
- `keyctl` (kernel key management -- blocked)

### 4.7 Seccomp Exercises (10)

**Exercise SEC-01:** Add the correct seccomp profile to pass "restricted" PSA.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-01
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      capabilities:
        drop: ["ALL"]
```

<details>
<summary>Answer SEC-01</summary>

Add seccomp at pod-level (covers all containers):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-01
spec:
  securityContext:                         # POD-LEVEL
    seccompProfile:                        # POD-LEVEL
      type: RuntimeDefault                 # Satisfies restricted PSA
    runAsNonRoot: true                     # Move to pod-level for cleaner config
    runAsUser: 1000
  containers:
  - name: app
    image: myapp:1.0
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false      # CONTAINER-LEVEL
      capabilities:                        # CONTAINER-LEVEL
        drop: ["ALL"]
```

Both `RuntimeDefault` and `Localhost` satisfy the "restricted" level. `Unconfined` does NOT.

</details>

---

**Exercise SEC-02:** Apply a custom seccomp profile from `/var/lib/kubelet/seccomp/profiles/nginx.json`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-02
spec:
  containers:
  - name: web
    image: nginx:1.27
```

<details>
<summary>Answer SEC-02</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-02
spec:
  securityContext:                         # POD-LEVEL
    seccompProfile:                        # POD-LEVEL
      type: Localhost
      localhostProfile: profiles/nginx.json
      # Resolves to: /var/lib/kubelet/seccomp/profiles/nginx.json
  containers:
  - name: web
    image: nginx:1.27
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
```

</details>

---

**Exercise SEC-03:** Two containers, different seccomp profiles. Container A uses RuntimeDefault, Container B uses a custom profile.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-03
spec:
  containers:
  - name: container-a
    image: app-a:1.0
  - name: container-b
    image: app-b:1.0
```

<details>
<summary>Answer SEC-03</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-03
spec:
  containers:
  - name: container-a
    image: app-a:1.0
    securityContext:                        # CONTAINER-LEVEL
      seccompProfile:                      # CONTAINER-LEVEL
        type: RuntimeDefault
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
  - name: container-b
    image: app-b:1.0
    securityContext:                        # CONTAINER-LEVEL
      seccompProfile:                      # CONTAINER-LEVEL (different from container-a)
        type: Localhost
        localhostProfile: profiles/app-b.json
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```

Alternatively, set `RuntimeDefault` at pod-level and override only container-b:

```yaml
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault                 # POD-LEVEL default
  containers:
  - name: container-a                      # Inherits RuntimeDefault from pod
    ...
  - name: container-b
    securityContext:
      seccompProfile:                      # CONTAINER-LEVEL override
        type: Localhost
        localhostProfile: profiles/app-b.json
```

</details>

---

**Exercise SEC-04:** Write a seccomp profile that allows only read, write, close, exit, and exit_group syscalls. Block everything else with ERRNO.

<details>
<summary>Answer SEC-04</summary>

Create file at `/var/lib/kubelet/seccomp/profiles/minimal.json`:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_AARCH64"
  ],
  "syscalls": [
    {
      "names": [
        "read",
        "write",
        "close",
        "exit",
        "exit_group"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

Apply in pod:
```yaml
securityContext:
  seccompProfile:
    type: Localhost
    localhostProfile: profiles/minimal.json
```

Note: This extremely restrictive profile will block most real applications. It's useful as a starting point -- use an audit profile first to discover needed syscalls, then build a whitelist.

</details>

---

**Exercise SEC-05:** Create an audit seccomp profile to discover which syscalls an application uses.

<details>
<summary>Answer SEC-05</summary>

Create `/var/lib/kubelet/seccomp/profiles/audit.json`:

```json
{
  "defaultAction": "SCMP_ACT_LOG"
}
```

Apply to pod:
```yaml
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/audit.json
```

After running the workload, check the node's audit logs:
```bash
# On the node
sudo journalctl -k | grep "audit" | grep "syscall"
# Or
sudo grep SECCOMP /var/log/audit/audit.log

# Extract unique syscall numbers
sudo grep SECCOMP /var/log/audit/audit.log | awk -F'syscall=' '{print $2}' | awk '{print $1}' | sort -u

# Map numbers to names
ausyscall <number>
```

Then build a whitelist profile with only those syscalls set to `SCMP_ACT_ALLOW` and `defaultAction: SCMP_ACT_ERRNO`.

</details>

---

**Exercise SEC-06:** Fix this pod. Error: `CreateContainerError: localhostProfile must be set when type is Localhost`.

```yaml
spec:
  securityContext:
    seccompProfile:
      type: Localhost
```

<details>
<summary>Answer SEC-06</summary>

When `type: Localhost`, the `localhostProfile` field is **mandatory**.

**Fix:**
```yaml
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/my-profile.json   # Add this
```

If you don't have a custom profile, use `RuntimeDefault` instead:
```yaml
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault                         # No localhostProfile needed
```

</details>

---

**Exercise SEC-07:** Convert this deprecated annotation-based seccomp to the current field-based syntax.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-07
  annotations:
    seccomp.security.alpha.kubernetes.io/pod: runtime/default
    container.seccomp.security.alpha.kubernetes.io/special: localhost/profiles/special.json
spec:
  containers:
  - name: app
    image: myapp:1.0
  - name: special
    image: special:1.0
```

<details>
<summary>Answer SEC-07</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sec-07
  # No annotations needed -- remove the old seccomp annotations
spec:
  securityContext:                         # POD-LEVEL
    seccompProfile:                        # Replaces pod-level annotation
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    # Inherits RuntimeDefault from pod-level
  - name: special
    image: special:1.0
    securityContext:                        # CONTAINER-LEVEL
      seccompProfile:                      # Replaces container-specific annotation
        type: Localhost
        localhostProfile: profiles/special.json
```

Mapping:
- `runtime/default` -> `type: RuntimeDefault`
- `localhost/<path>` -> `type: Localhost`, `localhostProfile: <path>`
- `unconfined` -> `type: Unconfined`

</details>

---

**Exercise SEC-08:** The application crashes with `EPERM` on `mount` syscall. The seccomp profile is `RuntimeDefault`. How to fix without switching to `Unconfined`?

<details>
<summary>Answer SEC-08</summary>

The `mount` syscall is blocked by `RuntimeDefault` because it's dangerous (can be used for container escape). Options:

**Option 1 (Preferred): Redesign the application** so it doesn't need `mount`. Often the mount can be replaced by a Kubernetes volume mount in the pod spec.

**Option 2: Create a custom Localhost profile** that adds `mount` to the whitelist:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": ["mount"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "names": [
        "... all RuntimeDefault allowed syscalls ..."
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

Better approach: Start with the RuntimeDefault profile (you can find it in the container runtime source), copy it, and add `mount` to the allowed list.

**Option 3: If the container absolutely needs mount (e.g., a storage plugin)**, it likely needs `SYS_ADMIN` capability too, and belongs in a `privileged` PSA namespace.

</details>

---

**Exercise SEC-09:** Verify which seccomp profile is applied to a running pod.

<details>
<summary>Answer SEC-09</summary>

```bash
# Method 1: Check the pod spec
kubectl get pod <name> -o jsonpath='{.spec.securityContext.seccompProfile}'
kubectl get pod <name> -o jsonpath='{.spec.containers[0].securityContext.seccompProfile}'

# Method 2: Check via describe
kubectl describe pod <name> | grep -A2 -i seccomp

# Method 3: Check the container's /proc status on the node
# First, find the container ID
kubectl get pod <name> -o jsonpath='{.status.containerStatuses[0].containerID}'

# SSH to the node, find the container's PID
crictl inspect <containerID> | grep pid
# Then check:
cat /proc/<PID>/status | grep Seccomp
# Output: Seccomp: 2 (means filtering mode is active)
# 0 = disabled, 1 = strict, 2 = filter (what we want)

# Method 4: Full pod YAML
kubectl get pod <name> -o yaml | grep -A3 seccompProfile
```

</details>

---

**Exercise SEC-10:** A node has this seccomp profile. What does it do?

```json
{
  "defaultAction": "SCMP_ACT_ALLOW",
  "syscalls": [
    {
      "names": ["mount", "umount2", "unshare", "clone3", "ptrace", "keyctl"],
      "action": "SCMP_ACT_KILL_PROCESS"
    }
  ]
}
```

<details>
<summary>Answer SEC-10</summary>

This is a **blacklist** (deny-list) approach:
- `defaultAction: SCMP_ACT_ALLOW` -- allow all syscalls by default
- Then explicitly **kill the process** if it tries to use: `mount`, `umount2`, `unshare`, `clone3`, `ptrace`, `keyctl`

These are syscalls commonly used in container escapes:
- `mount`/`umount2`: filesystem manipulation
- `unshare`: create new namespaces (escape isolation)
- `clone3`: create processes with new namespace flags
- `ptrace`: trace/debug other processes
- `keyctl`: kernel keyring manipulation (CVE-2016-0728)

**Important:** This is the **WRONG** approach. Blacklisting is inherently weaker than whitelisting because new dangerous syscalls may be added in future kernel versions. The correct approach is:
- `defaultAction: SCMP_ACT_ERRNO` (block everything by default)
- Explicitly allow only needed syscalls

`RuntimeDefault` uses a deny-specific-syscalls approach but is maintained by the container runtime team and is considered acceptable.

</details>

---

## 5. AppArmor

![AppArmor workflow — the magical wards](../images/cks-22-apparmor-workflow.jpg)

### 5.1 Is AppArmor Still on the CKS Exam?

**Yes.** AppArmor remains part of the CKS curriculum under "System Hardening" and "Minimize Microservice Vulnerabilities." It is tested alongside seccomp as a Linux Security Module (LSM).

### 5.2 AppArmor in Kubernetes: API Evolution

| Kubernetes Version | AppArmor Method | Status |
|-------------------|----------------|--------|
| 1.4 - 1.29 | **Annotation only:** `container.apparmor.security.beta.kubernetes.io/<container>: <profile>` | Beta |
| 1.30+ | **Native field:** `securityContext.appArmorProfile` (preferred) AND annotations (still supported) | Field is GA as of 1.30 |

**CKS exam note:** Know BOTH methods. The exam cluster version determines which to use. If unsure, the annotation method works across all versions. The field-based approach is preferred on 1.30+.

### 5.3 AppArmor Profile Modes

| Mode | Description |
|------|-------------|
| `enforce` | Policy is enforced. Violations are blocked AND logged |
| `complain` | Policy is NOT enforced. Violations are only logged (for testing/development) |
| `unconfined` | No AppArmor restrictions |

### 5.4 Loading AppArmor Profiles

Profiles must be loaded on each node where the pod may run.

```bash
# Check loaded profiles
sudo aa-status
sudo cat /sys/kernel/security/apparmor/profiles

# Load a profile in enforce mode
sudo apparmor_parser -r /etc/apparmor.d/my-profile
# -r = replace (load or reload)

# Load in complain mode
sudo apparmor_parser -C /etc/apparmor.d/my-profile
# -C = complain mode

# Remove a profile
sudo apparmor_parser -R /etc/apparmor.d/my-profile

# Check if AppArmor is enabled
sudo aa-enabled
# Output: "Yes"
```

### 5.5 Example AppArmor Profile

```
#include <tunables/global>

profile k8s-deny-write flags=(attach_disconnected) {
  #include <abstractions/base>

  # Allow all reads
  file,

  # Deny all writes to /sensitive/
  deny /sensitive/** w,

  # Deny network raw access
  deny network raw,

  # Deny mount operations
  deny mount,

  # Allow specific network operations
  network inet tcp,
  network inet udp,
  network inet icmp,
}
```

### 5.6 Applying AppArmor in Kubernetes

#### Method 1: Native Field (Kubernetes 1.30+) -- Preferred

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: apparmor-pod
spec:
  securityContext:                         # POD-LEVEL (default for all containers)
    appArmorProfile:                       # POD-LEVEL (BOTH levels)
      type: RuntimeDefault                 # RuntimeDefault | Localhost | Unconfined

  containers:
  - name: app
    image: myapp:1.0
    securityContext:                        # CONTAINER-LEVEL (overrides pod-level)
      appArmorProfile:                     # CONTAINER-LEVEL
        type: Localhost
        localhostProfile: k8s-deny-write   # Name of the loaded profile
```

**AppArmor field types:**
| Type | Description |
|------|-------------|
| `RuntimeDefault` | Container runtime's default AppArmor profile |
| `Localhost` | Custom profile loaded on the node |
| `Unconfined` | No AppArmor restrictions |

#### Method 2: Annotations (All versions, still supported)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: apparmor-pod
  annotations:
    # Format: container.apparmor.security.beta.kubernetes.io/<container-name>: <profile>
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-deny-write
spec:
  containers:
  - name: app       # Must match the container name in the annotation key
    image: myapp:1.0
```

**Annotation profile values:**
| Value | Meaning |
|-------|---------|
| `runtime/default` | Container runtime's default AppArmor profile |
| `localhost/<profile-name>` | Custom profile loaded on the node |
| `unconfined` | No AppArmor restrictions |

### 5.7 AppArmor Exercises (5)

**Exercise AA-01:** Apply the `runtime/default` AppArmor profile using the native field (1.30+).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-01
spec:
  containers:
  - name: app
    image: nginx:1.27
```

<details>
<summary>Answer AA-01</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-01
spec:
  securityContext:                         # POD-LEVEL
    appArmorProfile:                       # POD-LEVEL
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx:1.27
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```

Or at container level:
```yaml
  containers:
  - name: app
    image: nginx:1.27
    securityContext:
      appArmorProfile:                     # CONTAINER-LEVEL
        type: RuntimeDefault
```

</details>

---

**Exercise AA-02:** Apply a custom AppArmor profile named `k8s-restricted` using the annotation method (for pre-1.30 clusters).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-02
spec:
  containers:
  - name: web
    image: nginx:1.27
  - name: sidecar
    image: busybox:1.36
```

<details>
<summary>Answer AA-02</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-02
  annotations:
    container.apparmor.security.beta.kubernetes.io/web: localhost/k8s-restricted
    container.apparmor.security.beta.kubernetes.io/sidecar: localhost/k8s-restricted
spec:
  containers:
  - name: web
    image: nginx:1.27
  - name: sidecar
    image: busybox:1.36
```

Note: Each container needs its own annotation. The container name in the annotation key must match exactly.

**Prerequisite:** The `k8s-restricted` profile must be loaded on every node:
```bash
sudo apparmor_parser -r /etc/apparmor.d/k8s-restricted
```

</details>

---

**Exercise AA-03:** Write an AppArmor profile that denies writing to `/etc/` and denies all network raw access. Apply it to a pod.

<details>
<summary>Answer AA-03</summary>

**Step 1: Create the profile** `/etc/apparmor.d/k8s-deny-etc-write`:

```
#include <tunables/global>

profile k8s-deny-etc-write flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow all file operations by default
  file,

  # Deny writes to /etc/
  deny /etc/** w,
  deny /etc/ w,

  # Deny raw network access (prevents packet sniffing/spoofing)
  deny network raw,

  # Allow standard networking
  network inet tcp,
  network inet udp,
  network inet6 tcp,
  network inet6 udp,
}
```

**Step 2: Load the profile on each node:**
```bash
sudo apparmor_parser -r /etc/apparmor.d/k8s-deny-etc-write
sudo aa-status | grep k8s-deny-etc-write
```

**Step 3: Apply to pod (using native field for 1.30+):**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-03
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      appArmorProfile:                     # CONTAINER-LEVEL
        type: Localhost
        localhostProfile: k8s-deny-etc-write
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```

</details>

---

**Exercise AA-04:** Troubleshoot: This pod is stuck in `Blocked` status. The node runs AppArmor.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-04
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/nonexistent-profile
spec:
  containers:
  - name: app
    image: nginx:1.27
```

<details>
<summary>Answer AA-04</summary>

**Problem:** The AppArmor profile `nonexistent-profile` is not loaded on the node.

**Diagnosis:**
```bash
# Check pod events
kubectl describe pod aa-04
# Error: "failed to find profile \"nonexistent-profile\": ..."

# Check if profile is loaded on the node
ssh <node>
sudo aa-status | grep nonexistent-profile
# (no output -- profile not found)
```

**Fix options:**

1. **Load the missing profile:**
```bash
sudo apparmor_parser -r /etc/apparmor.d/nonexistent-profile
```

2. **Use an existing profile:**
```yaml
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: runtime/default
```

3. **Remove AppArmor restriction:**
```yaml
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: unconfined
```

</details>

---

**Exercise AA-05:** Convert this annotation-based AppArmor config to the native field (1.30+).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-05
  annotations:
    container.apparmor.security.beta.kubernetes.io/web: localhost/k8s-web-profile
    container.apparmor.security.beta.kubernetes.io/proxy: runtime/default
spec:
  containers:
  - name: web
    image: nginx:1.27
  - name: proxy
    image: envoy:v1.29
```

<details>
<summary>Answer AA-05</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: aa-05
  # Annotations removed -- using native fields instead
spec:
  containers:
  - name: web
    image: nginx:1.27
    securityContext:                        # CONTAINER-LEVEL
      appArmorProfile:                     # CONTAINER-LEVEL
        type: Localhost
        localhostProfile: k8s-web-profile  # Maps from "localhost/k8s-web-profile"
  - name: proxy
    image: envoy:v1.29
    securityContext:                        # CONTAINER-LEVEL
      appArmorProfile:                     # CONTAINER-LEVEL
        type: RuntimeDefault               # Maps from "runtime/default"
```

Or using pod-level default + container override:
```yaml
spec:
  securityContext:
    appArmorProfile:
      type: RuntimeDefault                 # Default for all containers
  containers:
  - name: web
    image: nginx:1.27
    securityContext:
      appArmorProfile:
        type: Localhost                    # Override for web container
        localhostProfile: k8s-web-profile
  - name: proxy
    image: envoy:v1.29
    # Inherits RuntimeDefault from pod-level
```

</details>

---

## 6. Minimize Microservice Vulnerabilities

![Container immutability — the sealed vault](../images/cks-24-container-immutability.jpg)

### 6.1 Comprehensive Pod Hardening Checklist

Use this checklist to transform any insecure pod manifest into a hardened one:

#### Identity & Access
- [ ] `runAsNonRoot: true` (pod-level)
- [ ] `runAsUser: <non-zero UID>` (pod-level, e.g., 1000)
- [ ] `runAsGroup: <non-zero GID>` (pod-level)
- [ ] `automountServiceAccountToken: false` (unless K8s API access is needed)
- [ ] Use a dedicated ServiceAccount with minimal RBAC (not `default`)
- [ ] No secrets in environment variables (use Secrets with `secretKeyRef` or volume mounts)

#### Container Isolation
- [ ] `allowPrivilegeEscalation: false` (every container)
- [ ] `privileged: false` (or absent -- never `true`)
- [ ] `readOnlyRootFilesystem: true` (every container, add emptyDir for writable paths)
- [ ] `capabilities.drop: ["ALL"]` (every container)
- [ ] Only add back strictly needed capabilities (prefer `NET_BIND_SERVICE` at most)

#### Linux Security Modules
- [ ] `seccompProfile.type: RuntimeDefault` (pod-level or every container)
- [ ] AppArmor profile applied (RuntimeDefault at minimum)

#### Network Isolation
- [ ] No `hostNetwork: true`
- [ ] No `hostPID: true`
- [ ] No `hostIPC: true`
- [ ] No `hostPort` usage (use Services instead)

#### Volume Security
- [ ] No `hostPath` volumes (use PVCs, ConfigMaps, Secrets, emptyDir)
- [ ] `fsGroup` set for volume access
- [ ] Volume mounts set to `readOnly: true` where possible

#### Resource Limits (DoS Prevention)
- [ ] CPU and memory `requests` set
- [ ] CPU and memory `limits` set
- [ ] `emptyDir.sizeLimit` set on tmpfs volumes

#### Image Security
- [ ] Use specific image tags, not `latest`
- [ ] Use image digests for critical workloads (e.g., `nginx@sha256:abc...`)
- [ ] Images from trusted registries only

### 6.2 Harden This Manifest Exercises (10)

**Exercise HARD-01:** Harden this basic web application pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-01
spec:
  containers:
  - name: web
    image: nginx:latest
    ports:
    - containerPort: 80
```

<details>
<summary>Answer HARD-01</summary>

Vulnerabilities found: 7

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-01
spec:
  automountServiceAccountToken: false       # [FIX 1] No K8s API access needed
  securityContext:                          # POD-LEVEL
    runAsNonRoot: true                      # [FIX 2] Don't run as root
    runAsUser: 101                          # nginx-unprivileged UID
    runAsGroup: 101
    fsGroup: 101
    seccompProfile:                         # [FIX 3] Add seccomp
      type: RuntimeDefault
  containers:
  - name: web
    image: nginxinc/nginx-unprivileged:1.27 # [FIX 4] Pinned tag + non-root image
    ports:
    - containerPort: 8080                   # [FIX 5] Non-privileged port
    securityContext:                        # CONTAINER-LEVEL
      allowPrivilegeEscalation: false       # [FIX 6] Prevent priv esc
      readOnlyRootFilesystem: true          # [FIX 7] Read-only root FS
      capabilities:
        drop: ["ALL"]
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        cpu: 200m
        memory: 128Mi
    volumeMounts:
    - name: cache
      mountPath: /var/cache/nginx
    - name: run
      mountPath: /var/run
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: cache
    emptyDir: { sizeLimit: 50Mi }
  - name: run
    emptyDir: { sizeLimit: 10Mi }
  - name: tmp
    emptyDir: { sizeLimit: 50Mi }
```

</details>

---

**Exercise HARD-02:** Harden this pod with secrets exposure.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-02
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_PASSWORD
      value: "supersecret123"
    - name: API_KEY
      value: "ak_live_xxxxxxxxxxxxx"
    - name: DB_HOST
      value: "db.internal.svc"
```

<details>
<summary>Answer HARD-02</summary>

Vulnerabilities: Plaintext secrets, latest tag, no securityContext.

First, create the Secret:
```bash
kubectl create secret generic app-secrets \
  --from-literal=DB_PASSWORD=supersecret123 \
  --from-literal=API_KEY=ak_live_xxxxxxxxxxxxx
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-02
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0                        # [FIX 1] Pinned version
    env:
    - name: DB_PASSWORD
      valueFrom:                            # [FIX 2] Secret reference
        secretKeyRef:
          name: app-secrets
          key: DB_PASSWORD
    - name: API_KEY
      valueFrom:                            # [FIX 3] Secret reference
        secretKeyRef:
          name: app-secrets
          key: API_KEY
    - name: DB_HOST
      value: "db.internal.svc"              # Non-secret, OK as plaintext
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

Even better: Mount secrets as files (not env vars) to prevent exposure via `/proc/<pid>/environ`:
```yaml
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: app-secrets
```

</details>

---

**Exercise HARD-03:** Harden this privileged debugging pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-03
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true
  containers:
  - name: debug
    image: ubuntu:latest
    command: ["sleep", "infinity"]
    securityContext:
      privileged: true
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
```

<details>
<summary>Answer HARD-03</summary>

This pod is essentially running as root on the node with full access. Total vulnerabilities: 8+

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-03
spec:
  # [FIX 1-3] Removed hostNetwork, hostPID, hostIPC
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: debug
    image: busybox:1.36                     # [FIX 4] Minimal image, pinned version
    command: ["sleep", "3600"]              # [FIX 5] Bounded sleep, not infinity
    securityContext:
      privileged: false                     # [FIX 6] Removed privileged mode
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
  # [FIX 7] Removed hostPath volume mounting /
  # [FIX 8] If specific files needed, use ConfigMap or PVC
```

If you truly need a debug pod (exam scenario), minimize access:
```yaml
# Temporary debug pod -- delete after use
kubectl debug node/<node-name> -it --image=busybox:1.36
```

</details>

---

**Exercise HARD-04:** Harden this multi-container pod with an init container.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-04
spec:
  serviceAccountName: admin-sa
  initContainers:
  - name: init-data
    image: busybox
    command: ["sh", "-c", "wget -O /data/config.json http://config-server/config"]
    volumeMounts:
    - name: data
      mountPath: /data
  containers:
  - name: app
    image: myapp
    volumeMounts:
    - name: data
      mountPath: /data
  - name: logger
    image: fluentd
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}
```

<details>
<summary>Answer HARD-04</summary>

Vulnerabilities: 9+

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-04
spec:
  serviceAccountName: app-reader-sa         # [FIX 1] Least-privilege SA
  automountServiceAccountToken: false       # [FIX 2] Unless needed
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  initContainers:
  - name: init-data
    image: busybox:1.36                     # [FIX 3] Pinned tag
    command: ["sh", "-c", "wget -O /data/config.json http://config-server/config"]
    securityContext:                        # [FIX 4] Init container needs securityContext too!
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    volumeMounts:
    - name: data
      mountPath: /data
    - name: tmp
      mountPath: /tmp
  containers:
  - name: app
    image: myapp:1.0                        # [FIX 5] Pinned tag
    securityContext:                        # [FIX 6] Container-level security
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 500m, memory: 256Mi }
    volumeMounts:
    - name: data
      mountPath: /data
      readOnly: true                        # [FIX 7] App only reads config
    - name: tmp
      mountPath: /tmp
  - name: logger
    image: fluentd:v1.16-1                  # [FIX 8] Pinned tag
    securityContext:                        # [FIX 9] Container-level security
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      requests: { cpu: 50m, memory: 64Mi }
      limits: { cpu: 200m, memory: 128Mi }
    volumeMounts:
    - name: data
      mountPath: /data
      readOnly: true
    - name: fluentd-buffer
      mountPath: /var/fluentd/buffer
  volumes:
  - name: data
    emptyDir: { sizeLimit: 100Mi }
  - name: tmp
    emptyDir: { sizeLimit: 50Mi }
  - name: fluentd-buffer
    emptyDir: { sizeLimit: 200Mi }
```

</details>

---

**Exercise HARD-05:** Harden this DaemonSet used for node monitoring.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: hard-05
spec:
  selector:
    matchLabels:
      app: monitor
  template:
    metadata:
      labels:
        app: monitor
    spec:
      containers:
      - name: monitor
        image: prom/node-exporter
        ports:
        - containerPort: 9100
          hostPort: 9100
        securityContext:
          privileged: true
        volumeMounts:
        - name: proc
          mountPath: /host/proc
        - name: sys
          mountPath: /host/sys
        - name: root
          mountPath: /host/root
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      - name: root
        hostPath:
          path: /
```

<details>
<summary>Answer HARD-05</summary>

Node-exporter legitimately needs some host access, but not full privileged mode.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: hard-05
spec:
  selector:
    matchLabels:
      app: monitor
  template:
    metadata:
      labels:
        app: monitor
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534                     # nobody
        runAsGroup: 65534
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: monitor
        image: prom/node-exporter:v1.7.0    # [FIX 1] Pinned version
        args:
        - "--path.procfs=/host/proc"
        - "--path.sysfs=/host/sys"
        - "--path.rootfs=/host/root"
        ports:
        - containerPort: 9100               # [FIX 2] Removed hostPort -- use Service
        securityContext:
          privileged: false                  # [FIX 3] Not privileged
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop: ["ALL"]
        resources:
          requests: { cpu: 50m, memory: 64Mi }
          limits: { cpu: 200m, memory: 128Mi }
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true                     # [FIX 4] Read-only mounts
        - name: sys
          mountPath: /host/sys
          readOnly: true                     # [FIX 5] Read-only
        # [FIX 6] Removed /host/root -- too much access. Only mount if needed.
      volumes:
      - name: proc
        hostPath:
          path: /proc
          type: Directory                    # [FIX 7] Type validation
      - name: sys
        hostPath:
          path: /sys
          type: Directory
      # Removed root volume
```

Note: This DaemonSet uses hostPath (needed for node monitoring), so it cannot run in a "restricted" PSA namespace. Use "baseline" or create a PSA exemption.

</details>

---

**Exercise HARD-06:** Harden this StatefulSet with a database.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: hard-06
spec:
  serviceName: db
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: postgres
        image: postgres
        env:
        - name: POSTGRES_PASSWORD
          value: "admin123"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: pgdata
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: pgdata
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

<details>
<summary>Answer HARD-06</summary>

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: hard-06
spec:
  serviceName: db
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      automountServiceAccountToken: false
      securityContext:                       # POD-LEVEL
        runAsNonRoot: true
        runAsUser: 999                       # postgres UID
        runAsGroup: 999                      # postgres GID
        fsGroup: 999                         # PVC ownership
        fsGroupChangePolicy: "OnRootMismatch"
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: postgres
        image: postgres:16.2                 # [FIX 1] Pinned version
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:                         # [FIX 2] From Secret
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGDATA                       # Required with readOnlyRootFilesystem
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
        securityContext:                     # CONTAINER-LEVEL
          allowPrivilegeEscalation: false    # [FIX 3]
          readOnlyRootFilesystem: true       # [FIX 4]
          capabilities:                      # [FIX 5]
            drop: ["ALL"]
        resources:                           # [FIX 6]
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: "1"
            memory: 1Gi
        volumeMounts:
        - name: pgdata
          mountPath: /var/lib/postgresql/data
        - name: run
          mountPath: /var/run/postgresql
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: run
        emptyDir: {}
      - name: tmp
        emptyDir: {}
  volumeClaimTemplates:
  - metadata:
      name: pgdata
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
      storageClassName: encrypted-gp3        # [FIX 7] Encrypted storage
```

</details>

---

**Exercise HARD-07:** Harden this pod that processes messages from a queue.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-07
spec:
  containers:
  - name: worker
    image: worker:latest
    command: ["python", "process.py"]
    env:
    - name: QUEUE_URL
      value: "amqp://admin:password@rabbitmq:5672"
    - name: AWS_ACCESS_KEY_ID
      value: "AKIAIOSFODNN7EXAMPLE"
    - name: AWS_SECRET_ACCESS_KEY
      value: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

<details>
<summary>Answer HARD-07</summary>

Critical: AWS credentials and queue password in plaintext. 5+ vulnerabilities.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-07
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: worker
    image: worker:1.4.2                      # [FIX 1] Pinned version
    command: ["python", "process.py"]
    env:
    - name: QUEUE_URL
      valueFrom:                             # [FIX 2] Queue URL from Secret
        secretKeyRef:
          name: queue-credentials
          key: url
    # [FIX 3] AWS credentials via IRSA/Workload Identity, NOT env vars
    # If using AWS EKS: use IAM Roles for Service Accounts (IRSA)
    # If using GKE: use Workload Identity
    # If must use static creds (not recommended):
    - name: AWS_SHARED_CREDENTIALS_FILE
      value: /etc/aws/credentials
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 500m, memory: 256Mi }
    volumeMounts:
    - name: aws-creds
      mountPath: /etc/aws
      readOnly: true
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: aws-creds
    secret:
      secretName: aws-credentials            # Store creds as K8s Secret
  - name: tmp
    emptyDir: {}
```

Best practice: Use cloud-native identity (IRSA, Workload Identity, Pod Identity) instead of static credentials.

</details>

---

**Exercise HARD-08:** Harden this pod that runs as root to bind to port 443.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-08
spec:
  containers:
  - name: api
    image: api-server:latest
    ports:
    - containerPort: 443
    securityContext:
      runAsUser: 0
    volumeMounts:
    - name: tls
      mountPath: /etc/tls
  volumes:
  - name: tls
    secret:
      secretName: api-tls-cert
```

<details>
<summary>Answer HARD-08</summary>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-08
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true                       # [FIX 1] Non-root
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: api
    image: api-server:2.1.0                  # [FIX 2] Pinned version
    ports:
    - containerPort: 443
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add:
        - NET_BIND_SERVICE                   # [FIX 3] Bind to 443 without root
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 500m, memory: 256Mi }
    volumeMounts:
    - name: tls
      mountPath: /etc/tls
      readOnly: true                         # [FIX 4] TLS certs are read-only
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tls
    secret:
      secretName: api-tls-cert
      defaultMode: 0400                      # [FIX 5] Restrictive file permissions
  - name: tmp
    emptyDir: {}
```

Alternative: Configure the API server to listen on port 8443 (non-privileged) and use a Kubernetes Service to expose it on 443. This eliminates the need for `NET_BIND_SERVICE`.

</details>

---

**Exercise HARD-09:** Harden this CI/CD runner pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-09
spec:
  serviceAccountName: cluster-admin
  containers:
  - name: runner
    image: gitlab-runner:latest
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
    env:
    - name: CI_TOKEN
      value: "glrt-xxxxxxxxxxxx"
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
```

<details>
<summary>Answer HARD-09</summary>

This is extremely dangerous: Docker socket mount + privileged + cluster-admin = full node AND cluster compromise.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-09
spec:
  serviceAccountName: ci-runner-sa           # [FIX 1] Dedicated SA with minimal RBAC
  automountServiceAccountToken: true         # Runner may need K8s API access
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: runner
    image: gitlab-runner:16.8.0              # [FIX 2] Pinned version
    securityContext:
      privileged: false                      # [FIX 3] Remove privileged
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    # [FIX 4] Removed Docker socket mount!
    # Use kaniko, buildah, or buildkit for container builds instead of Docker-in-Docker
    env:
    - name: CI_TOKEN
      valueFrom:                             # [FIX 5] Token from Secret
        secretKeyRef:
          name: ci-runner-secrets
          key: token
    resources:
      requests: { cpu: 500m, memory: 512Mi }
      limits: { cpu: "2", memory: 2Gi }
    volumeMounts:
    - name: work
      mountPath: /home/gitlab-runner
    - name: tmp
      mountPath: /tmp
  volumes:
  # [FIX 6] Removed hostPath docker.sock volume
  - name: work
    emptyDir: { sizeLimit: 5Gi }
  - name: tmp
    emptyDir: { sizeLimit: 500Mi }
```

For container builds without Docker socket:
- **Kaniko:** Builds container images in userspace (no daemon needed)
- **Buildah:** Daemonless container builder
- **BuildKit:** Rootless build support

</details>

---

**Exercise HARD-10:** Harden this complete microservice with all vulnerabilities present.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hard-10
spec:
  replicas: 2
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      hostNetwork: true
      serviceAccountName: default
      containers:
      - name: payment
        image: payment:latest
        ports:
        - containerPort: 8080
          hostPort: 8080
        env:
        - name: STRIPE_SECRET_KEY
          value: "sk_live_xxxxxxxxxxxxxx"
        - name: DB_CONN_STRING
          value: "postgresql://admin:password@db:5432/payments"
        securityContext:
          privileged: true
          runAsUser: 0
        volumeMounts:
        - name: host-etc
          mountPath: /host-etc
        - name: logs
          mountPath: /var/log/app
      - name: sidecar
        image: busybox
        command: ["sh", "-c", "tail -f /var/log/app/payment.log"]
        volumeMounts:
        - name: logs
          mountPath: /var/log/app
      volumes:
      - name: host-etc
        hostPath:
          path: /etc
      - name: logs
        emptyDir: {}
```

<details>
<summary>Answer HARD-10</summary>

Vulnerabilities found: **15+**

1. `hostNetwork: true` -- shares node network
2. `hostPort: 8080` -- exposes directly on node
3. `serviceAccountName: default` -- default SA may have excessive RBAC
4. `image: payment:latest` -- unpinned tag
5. `STRIPE_SECRET_KEY` in plaintext env var
6. `DB_CONN_STRING` with password in plaintext
7. `privileged: true` -- full host access
8. `runAsUser: 0` -- runs as root
9. `hostPath: /etc` mounted -- access to host configuration
10. Sidecar image `busybox` unpinned
11. No `allowPrivilegeEscalation: false`
12. No `readOnlyRootFilesystem`
13. No `capabilities.drop: ALL`
14. No `seccompProfile`
15. No resource limits
16. No `automountServiceAccountToken: false`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hard-10
spec:
  replicas: 2
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      # [FIX 1] Removed hostNetwork
      serviceAccountName: payment-sa          # [FIX 2] Dedicated SA
      automountServiceAccountToken: false     # [FIX 3] No API access needed
      securityContext:                        # POD-LEVEL
        runAsNonRoot: true                    # [FIX 4]
        runAsUser: 1000                       # [FIX 5] Non-root
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:                       # [FIX 6]
          type: RuntimeDefault
      containers:
      - name: payment
        image: payment:3.2.1                  # [FIX 7] Pinned version
        ports:
        - containerPort: 8080                 # [FIX 8] Removed hostPort
        env:
        - name: STRIPE_SECRET_KEY
          valueFrom:                          # [FIX 9]
            secretKeyRef:
              name: payment-secrets
              key: stripe-key
        - name: DB_CONN_STRING
          valueFrom:                          # [FIX 10]
            secretKeyRef:
              name: payment-secrets
              key: db-conn-string
        securityContext:                      # CONTAINER-LEVEL
          privileged: false                   # [FIX 11]
          allowPrivilegeEscalation: false     # [FIX 12]
          readOnlyRootFilesystem: true        # [FIX 13]
          capabilities:                       # [FIX 14]
            drop: ["ALL"]
        resources:                            # [FIX 15]
          requests: { cpu: 200m, memory: 256Mi }
          limits: { cpu: "1", memory: 512Mi }
        volumeMounts:
        # [FIX 16] Removed hostPath mount
        - name: logs
          mountPath: /var/log/app
        - name: tmp
          mountPath: /tmp
      - name: sidecar
        image: busybox:1.36                   # [FIX 17] Pinned version
        command: ["sh", "-c", "tail -f /var/log/app/payment.log"]
        securityContext:                      # [FIX 18] Sidecar also needs security
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop: ["ALL"]
        resources:
          requests: { cpu: 10m, memory: 16Mi }
          limits: { cpu: 50m, memory: 32Mi }
        volumeMounts:
        - name: logs
          mountPath: /var/log/app
          readOnly: true                      # Sidecar only reads logs
      volumes:
      # [FIX 19] Removed hostPath volume
      - name: logs
        emptyDir: { sizeLimit: 500Mi }
      - name: tmp
        emptyDir: { sizeLimit: 100Mi }
```

</details>

---

## 7. Quick Reference Tables

### 7.1 SecurityContext Field Placement Cheat Sheet

```
POD-LEVEL ONLY               CONTAINER-LEVEL ONLY          BOTH LEVELS (container overrides)
----------------------------  ----------------------------  ---------------------------------
fsGroup                       allowPrivilegeEscalation      runAsUser
fsGroupChangePolicy           privileged                    runAsGroup
supplementalGroups            readOnlyRootFilesystem        runAsNonRoot
sysctls                       capabilities (add/drop)       seccompProfile
                              procMount                     seLinuxOptions
                                                            appArmorProfile (K8s 1.30+)
                                                            windowsOptions
```

### 7.2 Pod Security Standards Summary

```
FEATURE               PRIVILEGED   BASELINE         RESTRICTED
--------------------------------------------------------------
hostNetwork            Allowed      Blocked          Blocked
hostPID                Allowed      Blocked          Blocked
hostIPC                Allowed      Blocked          Blocked
privileged             Allowed      Blocked          Blocked
capabilities           Any          Limited set      drop ALL, add only NET_BIND_SERVICE
hostPath volumes       Allowed      Blocked          Blocked
hostPorts              Allowed      Limited          Limited
runAsNonRoot           Any          Any              Required (true)
runAsUser              Any          Any              Must not be 0
allowPrivEsc           Any          Any              Required (false)
seccompProfile         Any          Not Unconfined   Required RuntimeDefault/Localhost
Volume types           Any          Any              Restricted list only
```

### 7.3 CKS Exam Quick Commands

```bash
# Apply PSA to namespace
kubectl label ns <name> pod-security.kubernetes.io/enforce=restricted

# Check PSA labels
kubectl get ns <name> --show-labels

# Check seccomp profile on running pod
kubectl get pod <name> -o jsonpath='{.spec.securityContext.seccompProfile.type}'

# Check AppArmor status on node
ssh <node> sudo aa-status

# Load AppArmor profile
ssh <node> sudo apparmor_parser -r /etc/apparmor.d/<profile>

# Check capabilities of running container (on node)
# Find PID first:
crictl inspect <containerID> | grep pid
cat /proc/<PID>/status | grep Cap
# Decode: capsh --decode=<hex_value>

# Test if pod passes restricted PSA
kubectl label ns test-ns pod-security.kubernetes.io/enforce=restricted --dry-run=server

# Create a hardened pod quickly (exam shortcut)
kubectl run secure-pod --image=nginx:1.27 --dry-run=client -o yaml > pod.yaml
# Then edit to add securityContext
```

### 7.4 Hardening Priority Order (CKS Exam)

When time is limited, apply security in this priority order:

1. **runAsNonRoot: true + runAsUser** (prevents root execution)
2. **allowPrivilegeEscalation: false** (prevents privilege escalation)
3. **capabilities: drop ALL** (removes all Linux capabilities)
4. **seccompProfile: RuntimeDefault** (syscall filtering)
5. **readOnlyRootFilesystem: true** (prevents filesystem writes)
6. **Remove hostNetwork/hostPID/hostIPC** (namespace isolation)
7. **Remove hostPath volumes** (filesystem isolation)
8. **automountServiceAccountToken: false** (API access restriction)
9. **Resource limits** (DoS prevention)
10. **AppArmor profile** (additional MAC enforcement)

---

*End of Pod Security & Linux Kernel Hardening Study Guide*
