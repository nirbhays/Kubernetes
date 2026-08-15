# CKS Security Toolbox, Speed Drills & Rapid Refresh

> **Purpose:** Unified command reference, search speed drills, YAML muscle memory program, and rapid security refresh for CKS exam preparation.
> **Created:** 2026-08-15
> **Exam context:** CKS is performance-based (2 hours, 15-20 tasks). Every second counts.

---

# SECTION 1: CKS SECURITY COMMAND TOOLBOX

> Master every tool the CKS exam environment provides. For each tool: what it does, when to reach for it, and 3-5 practical exam-style examples.

---

## 1.1 kubectl -- Security-Relevant Commands

kubectl is your primary tool. These are the security-specific patterns you must have at your fingertips.

### Authorization Checking

```bash
# Check if current user can create pods in namespace "secure"
kubectl auth can-i create pods -n secure

# Check if ServiceAccount "dev-sa" in namespace "apps" can list secrets
kubectl auth can-i list secrets --as=system:serviceaccount:apps:dev-sa -n apps

# List ALL permissions for a ServiceAccount
kubectl auth can-i --list --as=system:serviceaccount:default:my-sa

# Check if a user can exec into pods (common hardening task)
kubectl auth can-i create pods/exec --as=dev-user -n production

# Check cluster-wide permissions
kubectl auth can-i '*' '*' --all-namespaces --as=system:serviceaccount:kube-system:default
```

### Secrets Operations

```bash
# Get secret and decode it
kubectl get secret db-creds -n app -o jsonpath='{.data.password}' | base64 -d

# List all secrets across namespaces (audit exposure)
kubectl get secrets -A

# Create a secret from literal values
kubectl create secret generic my-secret --from-literal=user=admin --from-literal=pass=s3cur3

# Check if secrets are encrypted at rest (look at etcd)
kubectl -n kube-system get pod etcd-controlplane -o yaml | grep -i encrypt
```

### Pod Security Investigation

```bash
# Describe pod to check securityContext, serviceAccount, volumes
kubectl describe pod suspicious-pod -n default

# Get pod YAML to inspect full security configuration
kubectl get pod web-pod -n production -o yaml

# Exec into a pod for investigation
kubectl exec -it debug-pod -n default -- /bin/sh

# Get logs from a pod (security event investigation)
kubectl logs api-pod -n kube-system --tail=100

# Label a namespace for Pod Security Admission
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted

# Annotate namespace for audit/warn levels
kubectl label namespace staging pod-security.kubernetes.io/audit=restricted
kubectl label namespace staging pod-security.kubernetes.io/warn=restricted
```

### RBAC Operations

```bash
# Create a Role
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n dev

# Create a RoleBinding
kubectl create rolebinding pod-reader-binding --role=pod-reader --serviceaccount=dev:app-sa -n dev

# Create a ClusterRole
kubectl create clusterrole node-reader --verb=get,list --resource=nodes

# Create a ClusterRoleBinding
kubectl create clusterrolebinding node-reader-binding --clusterrole=node-reader --user=dev-user

# Delete a risky ClusterRoleBinding
kubectl delete clusterrolebinding insecure-binding
```

---

## 1.2 crictl -- Container Runtime Interface CLI

crictl talks directly to the container runtime (containerd/CRI-O). Use it when you need to inspect containers at the node level, not through the Kubernetes API.

```bash
# List all running containers on this node
crictl ps

# List all containers including stopped ones
crictl ps -a

# Inspect a specific container (full JSON details including mounts, env, security)
crictl inspect <container-id>

# Inspect a container and extract PID
crictl inspect <container-id> | grep -i pid

# List images on the node (check for unauthorized images)
crictl images

# Get logs from a container directly (bypasses kubelet)
crictl logs <container-id>

# Get logs with tail
crictl logs --tail=50 <container-id>

# List pods on this node
crictl pods

# Inspect a pod sandbox
crictl inspectp <pod-id>
```

**CKS use cases:**
- Investigate which containers are running when kubectl is unavailable
- Check container runtime configuration and security settings
- Verify image digests match expected values
- Debug container-level networking/security issues

---

## 1.3 systemctl -- Service Management

```bash
# Check kubelet status (is it running? any errors?)
systemctl status kubelet

# Restart kubelet after config changes
systemctl restart kubelet

# Check containerd status
systemctl status containerd

# Restart containerd
systemctl restart containerd

# Enable kubelet to start on boot
systemctl enable kubelet

# Check if a service is enabled
systemctl is-enabled kubelet

# Daemon-reload after changing unit files
systemctl daemon-reload
```

**CKS patterns:**
- After modifying `/var/lib/kubelet/config.yaml`, always `systemctl restart kubelet`
- After modifying `/etc/kubernetes/manifests/*.yaml` (static pods), kubelet auto-detects but sometimes needs a restart
- After modifying containerd config, restart containerd then kubelet

---

## 1.4 journalctl -- System Journal Logs

```bash
# Kubelet logs (most recent)
journalctl -u kubelet --no-pager -n 50

# Kubelet logs since last boot
journalctl -u kubelet -b

# Kubelet logs with follow (live tailing)
journalctl -u kubelet -f

# Containerd logs
journalctl -u containerd --no-pager -n 50

# Filter kubelet logs for errors only
journalctl -u kubelet --no-pager | grep -i error

# Kubelet logs in a time range
journalctl -u kubelet --since "2026-08-15 10:00:00" --until "2026-08-15 11:00:00"

# Show kubelet logs with priority (err and above)
journalctl -u kubelet -p err --no-pager
```

**CKS use cases:**
- Debugging why kubelet won't start after config changes
- Investigating admission controller rejections
- Finding certificate-related errors
- Checking audit log delivery issues

---

## 1.5 ps -- Process Listing

```bash
# List all processes (find kube-apiserver flags)
ps aux | grep kube-apiserver

# Find kubelet process and its flags
ps aux | grep kubelet

# Find etcd process and check its flags
ps aux | grep etcd

# Find all processes in a PID namespace (container investigation)
ps -ef | grep <process-name>

# Check if a specific process is running
ps aux | grep kube-controller-manager
```

**CKS patterns:**
- Verify API server flags: `--enable-admission-plugins`, `--audit-policy-file`, `--encryption-provider-config`
- Verify kubelet flags: `--authorization-mode`, `--anonymous-auth`
- Check etcd encryption flags: `--cert-file`, `--key-file`

---

## 1.6 ss -- Socket Statistics

```bash
# List all listening TCP ports
ss -tlnp

# List all listening UDP ports
ss -ulnp

# Check which process is listening on port 6443 (API server)
ss -tlnp | grep 6443

# Check which process is listening on port 10250 (kubelet)
ss -tlnp | grep 10250

# Check which process is listening on port 2379 (etcd)
ss -tlnp | grep 2379

# List all established connections
ss -tnp state established
```

**CKS use cases:**
- Verify API server is listening on expected port
- Check kubelet port binding (10250 secure vs 10255 read-only)
- Confirm etcd is not exposed on 0.0.0.0
- Investigate unexpected open ports on nodes

---

## 1.7 ip -- Network Interfaces

```bash
# Show all network interfaces
ip a

# Show routing table
ip route

# Show specific interface details
ip addr show eth0

# Show link layer information
ip link show

# Show neighbor (ARP) table
ip neigh
```

**CKS use cases:**
- Verify network namespace isolation
- Check pod network interface configuration
- Investigate hostNetwork pod exposure

---

## 1.8 curl -- API and Service Testing

```bash
# Test API server anonymously (should be forbidden if hardened)
curl -k https://localhost:6443/api/v1/pods

# Test API server with a ServiceAccount token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
curl -k -H "Authorization: Bearer $TOKEN" https://kubernetes.default.svc/api/v1/namespaces/default/pods

# Test kubelet read-only port (should be disabled -- connection refused = good)
curl http://localhost:10255/pods

# Test kubelet secure port
curl -k https://localhost:10250/pods

# Test a service endpoint
curl http://service-name.namespace.svc.cluster.local

# Test metrics server
curl -k https://localhost:6443/metrics
```

**CKS patterns:**
- Verify anonymous auth is disabled: `curl -k https://localhost:6443/api` should return 401/403
- Verify kubelet read-only port is closed: `curl http://localhost:10255/pods` should fail
- Test network policies by curling between pods

---

## 1.9 grep -- Configuration Searching

```bash
# Search API server manifest for admission plugins
grep -i "enable-admission-plugins" /etc/kubernetes/manifests/kube-apiserver.yaml

# Search for insecure settings
grep -r "anonymous-auth" /etc/kubernetes/

# Search for privileged containers in all manifests
grep -r "privileged: true" /etc/kubernetes/manifests/

# Search kubelet config for authorization mode
grep -i "authorization" /var/lib/kubelet/config.yaml

# Search for encryption provider config reference
grep -i "encryption-provider-config" /etc/kubernetes/manifests/kube-apiserver.yaml

# Recursive case-insensitive search
grep -ri "seccomp" /etc/kubernetes/
```

---

## 1.10 awk/sed -- Output Parsing

```bash
# Extract container IDs from crictl output
crictl ps | awk '{print $1}'

# Get image names from crictl
crictl images | awk '{print $1":"$2}'

# Extract specific field from kubectl output
kubectl get pods -A -o wide | awk '{print $1, $2, $4}'

# Replace a value in a YAML file (change replicas)
sed -i 's/privileged: true/privileged: false/' pod.yaml

# Remove a specific line from config
sed -i '/insecure-port/d' /etc/kubernetes/manifests/kube-apiserver.yaml

# Add a line after a match
sed -i '/--enable-admission-plugins/a\    - --audit-policy-file=/etc/kubernetes/audit-policy.yaml' /etc/kubernetes/manifests/kube-apiserver.yaml
```

---

## 1.11 find -- File Discovery

```bash
# Find all certificate files
find /etc/kubernetes/pki -name "*.crt"

# Find all key files
find /etc/kubernetes/pki -name "*.key"

# Find AppArmor profiles
find /etc/apparmor.d/ -type f

# Find seccomp profiles
find /var/lib/kubelet/seccomp -type f

# Find static pod manifests
find /etc/kubernetes/manifests/ -name "*.yaml"

# Find kubeconfig files
find /etc/kubernetes -name "*.conf"

# Find files modified in last 10 minutes (detect tampering)
find /etc/kubernetes -mmin -10

# Find world-readable files in kubernetes config (security issue)
find /etc/kubernetes -perm -o+r -type f
```

---

## 1.12 openssl -- Certificate Inspection

```bash
# View certificate details (issuer, subject, validity)
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -text -noout

# Check certificate expiry date
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate

# Check certificate subject (CN and SANs)
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -subject -ext subjectAltName

# Verify a certificate against a CA
openssl verify -CAfile /etc/kubernetes/pki/ca.crt /etc/kubernetes/pki/apiserver.crt

# Check certificate start date
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -startdate

# Inspect client certificate
openssl x509 -in /etc/kubernetes/pki/apiserver-kubelet-client.crt -text -noout | grep -A 2 "Subject:"

# Check all certs in pki directory for expiry
for cert in /etc/kubernetes/pki/*.crt; do
  echo "=== $cert ==="
  openssl x509 -in "$cert" -noout -enddate
done
```

---

## 1.13 trivy -- Image Vulnerability Scanning

```bash
# Scan an image for vulnerabilities
trivy image nginx:1.25

# Scan and show only HIGH and CRITICAL
trivy image --severity HIGH,CRITICAL nginx:1.25

# Scan an image and output in JSON
trivy image -f json nginx:1.25

# Scan a local image (already pulled)
trivy image --input /path/to/image.tar

# Scan with specific vulnerability types
trivy image --vuln-type os,library python:3.11

# Scan and filter by specific CVE
trivy image nginx:1.25 | grep CVE-2024-XXXX
```

**CKS exam pattern:** You will be asked to identify images with critical vulnerabilities and either fix them (update tag) or remove the pods using those images.

---

## 1.14 kube-bench -- CIS Benchmark Auditing

```bash
# Run full CIS benchmark check
kube-bench run

# Run checks for master node only
kube-bench run --targets master

# Run checks for worker node only
kube-bench run --targets node

# Run a specific check (e.g., 1.2.1 - API server)
kube-bench run --targets master --check 1.2.1

# Run and output as JSON
kube-bench run --json

# Run checks for etcd
kube-bench run --targets etcd

# Run checks for policies
kube-bench run --targets policies
```

**CKS exam pattern:** Run kube-bench, identify failures, then fix the configuration files (usually in `/etc/kubernetes/manifests/` or `/var/lib/kubelet/config.yaml`).

---

## 1.15 falco -- Runtime Security Monitoring

```bash
# Check Falco service status
systemctl status falco

# View Falco logs (detected events)
journalctl -u falco --no-pager -n 50

# Tail Falco output in real time
tail -f /var/log/syslog | grep falco

# Check Falco rules file
cat /etc/falco/falco_rules.yaml

# Check custom Falco rules
cat /etc/falco/falco_rules.local.yaml

# Restart Falco after rule changes
systemctl restart falco

# Hot-reload Falco rules (no restart needed)
kill -1 $(pidof falco)

# Test Falco by triggering a rule (exec into a pod and read /etc/shadow)
kubectl exec -it test-pod -- cat /etc/shadow
# Then check: journalctl -u falco --no-pager -n 10
```

**CKS exam pattern:** Either write a custom Falco rule to detect a specific behavior, or investigate Falco output to identify which pod is compromised.

---

## 1.16 apparmor_parser -- AppArmor Profile Management

```bash
# Load an AppArmor profile in enforce mode
apparmor_parser /etc/apparmor.d/my-profile

# Load in complain mode (log but don't block)
apparmor_parser -C /etc/apparmor.d/my-profile

# Replace/reload an existing profile
apparmor_parser -r /etc/apparmor.d/my-profile

# Remove a loaded profile
apparmor_parser -R /etc/apparmor.d/my-profile

# Check loaded profiles
aa-status

# List all loaded profiles (alternative)
cat /sys/kernel/security/apparmor/profiles
```

**CKS exam pattern:** Load a provided AppArmor profile on the node, then annotate the pod to use it:
```yaml
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/container-name: localhost/profile-name
```

---

## 1.17 etcdctl -- etcd Operations

```bash
# Set environment for etcdctl v3
export ETCDCTL_API=3

# Check etcd cluster health
etcdctl endpoint health \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Read a secret from etcd (verify encryption at rest)
etcdctl get /registry/secrets/default/my-secret \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# List all keys in etcd (careful -- lots of output)
etcdctl get / --prefix --keys-only \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Snapshot etcd
etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

**CKS exam pattern:** Verify that secrets are encrypted at rest. If the `etcdctl get` output shows plaintext, configure EncryptionConfiguration and restart API server.

---
---

# SECTION 2: GREP / SEARCH SPEED DRILLS

> 15 micro-drills for rapid configuration discovery. Each drill has a target completion time. Practice until you can do them without thinking.

---

## Drill 1: Find All Static Pod Manifests on a Node
**Time target:** 30 seconds

```bash
# Primary location
ls /etc/kubernetes/manifests/

# If non-standard, find the kubelet's staticPodPath
grep -i "staticPodPath" /var/lib/kubelet/config.yaml
# or check the kubelet process flags
ps aux | grep kubelet | grep -- "--pod-manifest-path"
```

**Expected output pattern:**
```
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
```

---

## Drill 2: Search API Server Flags for Specific Settings
**Time target:** 30 seconds

```bash
# Check the manifest directly
grep -E "enable-admission-plugins|audit-policy|encryption-provider|authorization-mode|anonymous-auth" \
  /etc/kubernetes/manifests/kube-apiserver.yaml

# Alternative: check running process
ps aux | grep kube-apiserver | tr ' ' '\n' | grep -E "admission|audit|encrypt|authori|anon"
```

**Expected output pattern:**
```
--enable-admission-plugins=NodeRestriction,PodSecurity
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
--authorization-mode=Node,RBAC
```

---

## Drill 3: Find Kubelet Config File and Check Authorization Mode
**Time target:** 30 seconds

```bash
# The kubelet config is usually at:
cat /var/lib/kubelet/config.yaml | grep -A2 "authorization"

# Also check for anonymous auth
grep "anonymous" /var/lib/kubelet/config.yaml
# or
grep -A1 "authentication" /var/lib/kubelet/config.yaml
```

**Expected output pattern:**
```
authorization:
  mode: Webhook
authentication:
  anonymous:
    enabled: false
```

---

## Drill 4: Find All Pods Running as Privileged
**Time target:** 45 seconds

```bash
# Across all namespaces
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{range .spec.containers[*]}{.securityContext.privileged}{"\t"}{end}{"\n"}{end}' | grep true

# Simpler alternative
kubectl get pods -A -o yaml | grep -B 20 "privileged: true" | grep "name:"
```

**Expected output pattern:**
```
kube-system    kube-proxy-xxxxx    true
default        insecure-pod        true
```

---

## Drill 5: Find All Pods with hostNetwork: true
**Time target:** 45 seconds

```bash
# Using jsonpath
kubectl get pods -A -o jsonpath='{range .items[?(@.spec.hostNetwork==true)]}{.metadata.namespace}{"\t"}{.metadata.name}{"\n"}{end}'

# Using grep
kubectl get pods -A -o yaml | grep -B 10 "hostNetwork: true" | grep -E "name:|namespace:"
```

**Expected output pattern:**
```
kube-system    kube-proxy-xxxxx
kube-system    calico-node-xxxxx
```

---

## Drill 6: Search Audit Policy for Specific Rules
**Time target:** 30 seconds

```bash
# Find audit policy file location
grep "audit-policy-file" /etc/kubernetes/manifests/kube-apiserver.yaml

# View the policy
cat /etc/kubernetes/audit-policy.yaml

# Search for specific resource rules
grep -A 5 "secrets" /etc/kubernetes/audit-policy.yaml
grep -A 5 "configmaps" /etc/kubernetes/audit-policy.yaml
```

**Expected output pattern:**
```
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
```

---

## Drill 7: Find Seccomp Profiles on Disk
**Time target:** 30 seconds

```bash
# Default kubelet seccomp profile directory
ls /var/lib/kubelet/seccomp/profiles/
# or
find /var/lib/kubelet/seccomp -type f -name "*.json"

# Check if a specific profile exists
cat /var/lib/kubelet/seccomp/profiles/my-profile.json
```

**Expected output pattern:**
```
audit.json
fine-grained.json
violation.json
```

---

## Drill 8: Find AppArmor Profiles Loaded
**Time target:** 30 seconds

```bash
# List all loaded AppArmor profiles and their mode (enforce/complain)
aa-status

# Alternative
cat /sys/kernel/security/apparmor/profiles

# Find custom profile files on disk
ls /etc/apparmor.d/
```

**Expected output pattern:**
```
docker-default (enforce)
k8s-apparmor-example-deny-write (enforce)
```

---

## Drill 9: Locate Encryption Configuration
**Time target:** 45 seconds

```bash
# Step 1: Find the flag in API server manifest
grep "encryption-provider-config" /etc/kubernetes/manifests/kube-apiserver.yaml

# Step 2: Read the encryption config file
# Path from step 1, commonly:
cat /etc/kubernetes/enc/enc.yaml
# or
cat /etc/kubernetes/pki/encryption-config.yaml

# Step 3: Verify which provider is first (identity = no encryption)
grep -A 5 "providers:" /etc/kubernetes/enc/enc.yaml
```

**Expected output pattern:**
```
--encryption-provider-config=/etc/kubernetes/enc/enc.yaml
providers:
  - aescbc:
      keys:
        - name: key1
          secret: <base64-encoded-key>
  - identity: {}
```

---

## Drill 10: Find Certificate Files and Check Expiry
**Time target:** 1 minute

```bash
# List all certs
find /etc/kubernetes/pki -name "*.crt" -maxdepth 1

# Quick expiry check for API server cert
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate

# Check all cert expiry dates at once
for cert in /etc/kubernetes/pki/*.crt; do
  echo "--- $cert ---"
  openssl x509 -in "$cert" -noout -enddate -subject 2>/dev/null
done

# Using kubeadm (if available)
kubeadm certs check-expiration
```

**Expected output pattern:**
```
--- /etc/kubernetes/pki/apiserver.crt ---
notAfter=Sep 15 10:00:00 2027 GMT
subject=CN = kube-apiserver
```

---

## Drill 11: Find All ServiceAccounts with automountServiceAccountToken Not Disabled
**Time target:** 45 seconds

```bash
# Check pods that auto-mount tokens
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.spec.automountServiceAccountToken}{"\n"}{end}' | grep -v false

# Check ServiceAccount definitions
kubectl get sa -A -o yaml | grep -B 5 "automountServiceAccountToken"
```

---

## Drill 12: Find API Server Admission Controllers
**Time target:** 30 seconds

```bash
# From the manifest
grep "enable-admission-plugins" /etc/kubernetes/manifests/kube-apiserver.yaml

# From the running process
ps aux | grep kube-apiserver | tr ',' '\n' | grep -i admission
```

**Expected output pattern:**
```
--enable-admission-plugins=NodeRestriction,PodSecurity
```

---

## Drill 13: Find All Namespaces with Pod Security Labels
**Time target:** 30 seconds

```bash
# Show all namespace labels
kubectl get ns --show-labels | grep pod-security

# More specific
kubectl get ns -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels.pod-security\.kubernetes\.io/enforce}{"\n"}{end}' | grep -v "^$"
```

**Expected output pattern:**
```
production    restricted
staging       baseline
```

---

## Drill 14: Find kubelet Certificate Rotation Settings
**Time target:** 30 seconds

```bash
# Check kubelet config
grep -i "rotateCertificates\|rotate-certificates\|serverTLSBootstrap" /var/lib/kubelet/config.yaml

# Check kubelet process flags
ps aux | grep kubelet | tr ' ' '\n' | grep -i rotat
```

**Expected output pattern:**
```
rotateCertificates: true
serverTLSBootstrap: true
```

---

## Drill 15: Identify the Container Runtime and Its Config
**Time target:** 30 seconds

```bash
# Check kubelet for container runtime endpoint
grep -i "containerRuntimeEndpoint" /var/lib/kubelet/config.yaml
# or
ps aux | grep kubelet | tr ' ' '\n' | grep runtime

# Check containerd config
cat /etc/containerd/config.toml | head -30

# Check containerd is running
systemctl status containerd
```

**Expected output pattern:**
```
containerRuntimeEndpoint: unix:///var/run/containerd/containerd.sock
```

---
---

# SECTION 3: CKS YAML MUSCLE MEMORY PROGRAM

> Speed-training program: know WHEN to use each method, then drill YAML creation until it is automatic.

---

## 3.1 Method Selection Guide

### When to GENERATE YAML (kubectl create/run --dry-run=client -o yaml)

Use this for standard resources where kubectl supports generation:

```bash
# Pod
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Deployment
kubectl create deployment web --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Service
kubectl expose pod nginx --port=80 --target-port=80 --dry-run=client -o yaml > svc.yaml

# ServiceAccount
kubectl create sa my-sa --dry-run=client -o yaml > sa.yaml

# Role
kubectl create role pod-reader --verb=get,list --resource=pods --dry-run=client -o yaml > role.yaml

# RoleBinding
kubectl create rolebinding pod-reader-bind --role=pod-reader --serviceaccount=default:my-sa --dry-run=client -o yaml > rb.yaml

# ClusterRole
kubectl create clusterrole node-reader --verb=get,list --resource=nodes --dry-run=client -o yaml > cr.yaml

# ClusterRoleBinding
kubectl create clusterrolebinding crb --clusterrole=node-reader --user=jane --dry-run=client -o yaml > crb.yaml

# ConfigMap
kubectl create configmap myconfig --from-literal=key=value --dry-run=client -o yaml > cm.yaml

# Secret
kubectl create secret generic mysecret --from-literal=pass=abc --dry-run=client -o yaml > secret.yaml

# NetworkPolicy -- NOT SUPPORTED by kubectl create, must write from scratch or docs
# Audit Policy -- NOT SUPPORTED, write from scratch or docs
# EncryptionConfig -- NOT SUPPORTED, write from scratch
```

### When to COPY from Official Docs (Bookmark These URLs)

Keep these tabs open during the exam (kubernetes.io is allowed):

| Resource | URL Path |
|----------|----------|
| NetworkPolicy | `kubernetes.io/docs/concepts/services-networking/network-policies/` |
| Pod Security Admission | `kubernetes.io/docs/concepts/security/pod-security-admission/` |
| Audit Policy | `kubernetes.io/docs/tasks/debug/debug-cluster/audit/` |
| Seccomp | `kubernetes.io/docs/tutorials/security/seccomp/` |
| AppArmor | `kubernetes.io/docs/tutorials/security/apparmor/` |
| SecurityContext | `kubernetes.io/docs/tasks/configure-pod-container/security-context/` |
| EncryptionConfig | `kubernetes.io/docs/tasks/administer-cluster/encrypt-data/` |
| RBAC | `kubernetes.io/docs/reference/access-authn-authz/rbac/` |
| AdmissionControllers | `kubernetes.io/docs/reference/access-authn-authz/admission-controllers/` |

### When to EDIT Existing Resources (kubectl edit)

```bash
# Edit a deployment in-place
kubectl edit deployment web -n production

# Edit a pod (will recreate it)
kubectl edit pod nginx -n default

# Edit namespace labels
kubectl edit namespace production
```

Use `kubectl edit` when:
- You need to add/change a single field in an existing resource
- The resource is too complex to patch on the command line
- You need to add securityContext to existing pods

### When to PATCH Resources (kubectl patch)

```bash
# Patch a ServiceAccount to disable automount
kubectl patch sa default -n production -p '{"automountServiceAccountToken": false}'

# Patch a deployment to add security context
kubectl patch deployment web -n production -p '{"spec":{"template":{"spec":{"containers":[{"name":"web","securityContext":{"runAsNonRoot":true}}]}}}}'

# Patch a namespace to add PSA labels
kubectl patch namespace production -p '{"metadata":{"labels":{"pod-security.kubernetes.io/enforce":"restricted"}}}'
```

Use `kubectl patch` when:
- Changing a single field and you know the JSON path
- Scripting changes across multiple resources
- The change is small and well-defined

### When to Use kubectl set

```bash
# Change image (very fast)
kubectl set image deployment/web nginx=nginx:1.25-alpine -n production

# Set resources
kubectl set resources deployment/web -c=nginx --limits=cpu=200m,memory=256Mi

# Set ServiceAccount
kubectl set serviceaccount deployment/web my-secure-sa -n production
```

Use `kubectl set` when:
- Changing container image (fastest method)
- Setting resource limits
- Changing ServiceAccount on a deployment

---

## 3.2 YAML From Memory: 20 Timed Challenges

### Challenge 1: SecurityContext (Restricted Profile)
**Target: 1 minute**

Write a pod with full restricted security context:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  namespace: production
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx:1.25-alpine
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
    resources:
      limits:
        memory: "128Mi"
        cpu: "250m"
```

**Key memory anchors:** runAsNonRoot, allowPrivilegeEscalation: false, drop ALL caps, readOnlyRootFilesystem, seccompProfile RuntimeDefault.

---

### Challenge 2: NetworkPolicy Default Deny All
**Target: 30 seconds**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**Key memory anchor:** Empty `podSelector: {}` means all pods. Empty `policyTypes` with no rules = deny all.

---

### Challenge 3: NetworkPolicy Allow Specific Traffic
**Target: 1 minute**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          env: production
    ports:
    - protocol: TCP
      port: 8080
```

**Key memory anchor:** `podSelector` selects the TARGET pods. `ingress.from` defines SOURCES. Multiple items under `from` are OR. Items in same `from` entry with both pod and namespace are AND.

---

### Challenge 4: RBAC Role + RoleBinding
**Target: 2 minutes**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: dev
subjects:
- kind: ServiceAccount
  name: dev-sa
  namespace: dev
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**Key memory anchors:** `rules` has apiGroups/resources/verbs. Core API group is `""`. `roleRef` uses `apiGroup: rbac.authorization.k8s.io`. RoleBinding subjects need `kind`, `name`, and optionally `namespace`.

---

### Challenge 5: ServiceAccount with automount Disabled
**Target: 30 seconds**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: restricted-sa
  namespace: production
automountServiceAccountToken: false
```

**Key memory anchor:** `automountServiceAccountToken` is a top-level field on ServiceAccount, NOT under `spec`.

---

### Challenge 6: Pod Security Admission Namespace Labels
**Target: 30 seconds**

```bash
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

Or as YAML:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Key memory anchor:** Three levels: enforce (block), audit (log), warn (warn user). Three profiles: privileged, baseline, restricted.

---

### Challenge 7: Audit Policy
**Target: 2 minutes**

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Log no operations on requests to the RequestReceived stage
  - level: None
    resources:
    - group: ""
      resources: ["endpoints", "services", "services/status"]

  # Log secret access at Metadata level
  - level: Metadata
    resources:
    - group: ""
      resources: ["secrets", "configmaps"]

  # Log pod changes at RequestResponse level
  - level: RequestResponse
    resources:
    - group: ""
      resources: ["pods"]
    verbs: ["create", "update", "patch", "delete"]

  # Catch-all: log everything else at Metadata
  - level: Metadata
    omitStages:
    - RequestReceived
```

**Key memory anchors:** apiVersion is `audit.k8s.io/v1`. Four levels: None, Metadata, Request, RequestResponse. Rules are evaluated in order, first match wins.

---

### Challenge 8: Encryption Configuration
**Target: 3 minutes**

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-32-byte-key>
    - identity: {}
```

Generate the key:
```bash
head -c 32 /dev/urandom | base64
```

Then add to API server manifest:
```yaml
# In /etc/kubernetes/manifests/kube-apiserver.yaml
spec:
  containers:
  - command:
    - kube-apiserver
    - --encryption-provider-config=/etc/kubernetes/enc/enc.yaml
    volumeMounts:
    - name: enc
      mountPath: /etc/kubernetes/enc
      readOnly: true
  volumes:
  - name: enc
    hostPath:
      path: /etc/kubernetes/enc
      type: DirectoryOrCreate
```

**Key memory anchors:** apiVersion is `apiserver.config.k8s.io/v1`. Provider order matters: first provider is used for encryption, all are tried for decryption. `identity: {}` means no encryption (fallback). Must mount the config file into API server pod.

---

### Challenge 9: Falco Rule (Custom)
**Target: 2 minutes**

```yaml
- rule: Detect Shell in Container
  desc: Alert when a shell is spawned in a container
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, zsh, csh, ksh)
  output: >
    Shell spawned in container
    (user=%user.name container_id=%container.id
    container_name=%container.name
    image=%container.image.repository
    shell=%proc.name parent=%proc.pname
    cmdline=%proc.cmdline)
  priority: WARNING
  tags: [container, shell, mitre_execution]
```

Place in `/etc/falco/falco_rules.local.yaml` and restart Falco.

**Key memory anchors:** Fields are `rule`, `desc`, `condition`, `output`, `priority`, `tags`. Priorities: EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFORMATIONAL, DEBUG. Use `falco_rules.local.yaml` for custom rules (overrides base rules).

---

### Challenge 10: Seccomp Profile Reference in Pod
**Target: 30 seconds**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-pod
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/my-profile.json
  containers:
  - name: app
    image: nginx:1.25-alpine
```

Profile file goes in `/var/lib/kubelet/seccomp/profiles/my-profile.json`.

**Key memory anchor:** Three types: `RuntimeDefault`, `Localhost`, `Unconfined`. For Localhost, `localhostProfile` is relative to `/var/lib/kubelet/seccomp/`.

---

### Challenge 11: AppArmor Pod Annotation
**Target: 30 seconds**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: apparmor-pod
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-deny-write
spec:
  containers:
  - name: app
    image: nginx:1.25-alpine
```

**Key memory anchor:** Annotation key pattern: `container.apparmor.security.beta.kubernetes.io/<container-name>`. Value: `localhost/<profile-name>`, `runtime/default`, or `unconfined`.

**Note:** From Kubernetes v1.30+, AppArmor can also be set via the `securityContext.appArmorProfile` field (GA), similar to seccomp:

```yaml
spec:
  containers:
  - name: app
    image: nginx:1.25-alpine
    securityContext:
      appArmorProfile:
        type: Localhost
        localhostProfile: k8s-deny-write
```

---

### Challenge 12: Pod with Specific Linux Capabilities
**Target: 1 minute**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cap-pod
spec:
  containers:
  - name: app
    image: nginx:1.25-alpine
    securityContext:
      capabilities:
        drop:
          - ALL
        add:
          - NET_BIND_SERVICE
```

**Key memory anchor:** Always drop ALL first, then add only what is needed. Common CKS capabilities: NET_BIND_SERVICE, SYS_TIME, CHOWN. NEVER add SYS_ADMIN (essentially root).

---

### Challenge 13: ClusterRole for Read-Only Access
**Target: 1 minute**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: readonly-all
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
```

---

### Challenge 14: Pod Using a Specific ServiceAccount
**Target: 30 seconds**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sa-pod
  namespace: secure
spec:
  serviceAccountName: restricted-sa
  automountServiceAccountToken: false
  containers:
  - name: app
    image: nginx:1.25-alpine
```

**Key memory anchor:** `serviceAccountName` (not `serviceAccount` which is deprecated). `automountServiceAccountToken` can be set at both SA and pod level; pod level takes precedence.

---

### Challenge 15: ImagePolicyWebhook Admission Config
**Target: 2 minutes**

```yaml
# /etc/kubernetes/admission/admission-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  configuration:
    imagePolicy:
      kubeConfigFile: /etc/kubernetes/admission/imagepolicy-kubeconfig.yaml
      allowTTL: 50
      denyTTL: 50
      retryBackoff: 500
      defaultAllow: false
```

Then reference in API server:
```
--enable-admission-plugins=...,ImagePolicyWebhook
--admission-control-config-file=/etc/kubernetes/admission/admission-config.yaml
```

**Key memory anchor:** `defaultAllow: false` means deny if webhook is unreachable (secure default). Must mount the config directory into the API server pod.

---

### Challenge 16: OPA Gatekeeper ConstraintTemplate
**Target: 2 minutes**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

---

### Challenge 17: RuntimeClass Definition
**Target: 1 minute**

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
---
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-pod
spec:
  runtimeClassName: gvisor
  containers:
  - name: app
    image: nginx:1.25-alpine
```

**Key memory anchor:** `handler` maps to the container runtime handler name (e.g., `runsc` for gVisor, `kata` for Kata Containers). Pod references it via `runtimeClassName`.

---

### Challenge 18: Network Policy -- Allow DNS Egress Only
**Target: 1 minute**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-only
  namespace: restricted
spec:
  podSelector:
    matchLabels:
      app: locked-down
  policyTypes:
  - Egress
  egress:
  - to: []
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

**Key memory anchor:** DNS runs on port 53, both UDP (primary) and TCP (fallback). Without DNS egress, most pods break.

---

### Challenge 19: PodDisruptionBudget
**Target: 30 seconds**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

---

### Challenge 20: Ingress with TLS
**Target: 1 minute**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
  namespace: production
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: tls-secret
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

Create the TLS secret:
```bash
kubectl create secret tls tls-secret --cert=cert.pem --key=key.pem -n production
```

---
---

# SECTION 4: RAPID SECURITY REFRESH

> 15 CKS topics, each in a compact reference block. Review all 15 in under 30 minutes.

---

### 1. RBAC

**Security Objective:** Enforce least-privilege access to the Kubernetes API.

**Attack Prevented:** Unauthorized users or compromised ServiceAccounts escalating privileges, reading secrets, or modifying workloads.

**Kubernetes Mechanism:** Role/ClusterRole define permissions (apiGroups + resources + verbs). RoleBinding/ClusterRoleBinding assign them to subjects (users, groups, ServiceAccounts).

**Configuration:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: app
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: app
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: app
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**Command:**
```bash
kubectl auth can-i list secrets --as=system:serviceaccount:app:app-sa -n app
```

**Verification:**
```bash
kubectl auth can-i --list --as=system:serviceaccount:app:app-sa -n app
# Should show only get/list pods, nothing else
```

**Common CKS Trap:** Mixing up Role (namespaced) vs ClusterRole (cluster-wide). Using ClusterRoleBinding when RoleBinding is sufficient -- this grants access across ALL namespaces. Forgetting `apiGroup: rbac.authorization.k8s.io` in roleRef.

**Mini Lab (3 min):**
1. Create a ServiceAccount `audit-sa` in namespace `default`
2. Create a Role allowing only `get` on `pods`
3. Bind the Role to the ServiceAccount
4. Verify: `kubectl auth can-i get pods --as=system:serviceaccount:default:audit-sa` (should be "yes")
5. Verify: `kubectl auth can-i delete pods --as=system:serviceaccount:default:audit-sa` (should be "no")

---

### 2. ServiceAccounts

**Security Objective:** Control pod identity and limit automatic API access.

**Attack Prevented:** Compromised pod using its auto-mounted ServiceAccount token to access the Kubernetes API, enumerate resources, or escalate privileges.

**Kubernetes Mechanism:** Each pod runs under a ServiceAccount. By default, a token is auto-mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`. Disabling automount and using dedicated SAs with minimal RBAC prevents abuse.

**Configuration:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
automountServiceAccountToken: false
```

Pod using the SA:
```yaml
spec:
  serviceAccountName: app-sa
  automountServiceAccountToken: false   # belt and suspenders
```

**Command:**
```bash
# Check which SA a pod uses
kubectl get pod my-pod -o jsonpath='{.spec.serviceAccountName}'
# Check if token is mounted
kubectl exec my-pod -- ls /var/run/secrets/kubernetes.io/serviceaccount/ 2>/dev/null
```

**Verification:**
```bash
# Token directory should not exist or be empty when automount is disabled
kubectl exec my-pod -- cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>&1
# Expected: "No such file or directory"
```

**Common CKS Trap:** Setting `automountServiceAccountToken: false` on the ServiceAccount but the pod overrides it to `true`. Pod-level setting takes precedence over SA-level. Also: forgetting that the `default` SA in every namespace has a token auto-mounted unless explicitly disabled.

**Mini Lab (3 min):**
1. Create SA `no-access` in namespace `default` with `automountServiceAccountToken: false`
2. Create a pod using this SA
3. Exec into the pod and confirm no token is mounted
4. Verify: `kubectl auth can-i --list --as=system:serviceaccount:default:no-access`

---

### 3. NetworkPolicy

**Security Objective:** Restrict pod-to-pod and pod-to-external network traffic.

**Attack Prevented:** Lateral movement after pod compromise. Attacker in one pod cannot reach databases, internal services, or the metadata API.

**Kubernetes Mechanism:** NetworkPolicy resources define allowed ingress/egress per pod label selector. Requires a CNI that supports NetworkPolicy (Calico, Cilium, Weave). Without a policy, all traffic is allowed.

**Configuration:**
```yaml
# Default deny all in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# Allow frontend to backend on port 8080
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - port: 8080
```

**Command:**
```bash
kubectl get networkpolicies -n production
kubectl describe networkpolicy default-deny -n production
```

**Verification:**
```bash
# From frontend pod, curl backend should work
kubectl exec frontend-pod -- curl -s --max-time 3 backend-svc:8080
# From unauthorized pod, curl backend should timeout
kubectl exec other-pod -- curl -s --max-time 3 backend-svc:8080
```

**Common CKS Trap:** Forgetting to add DNS egress when creating default-deny egress. Without port 53 UDP/TCP egress, pod DNS resolution breaks and services become unreachable by name. Another trap: AND vs OR logic in `from` arrays -- items in the same list entry with both `podSelector` and `namespaceSelector` are AND; separate list entries are OR.

**Mini Lab (3 min):**
1. Create namespace `netpol-test` with two pods: `client` and `server`
2. Apply default-deny-ingress NetworkPolicy
3. Verify: curl from client to server times out
4. Apply allow policy from client to server on port 80
5. Verify: curl now succeeds

---

### 4. SecurityContext

**Security Objective:** Restrict container privileges at the pod and container level.

**Attack Prevented:** Container breakout, privilege escalation, host filesystem access, kernel exploitation.

**Kubernetes Mechanism:** `securityContext` at pod level (applies to all containers) and container level (overrides pod level). Controls user/group IDs, capabilities, filesystem access, privilege escalation.

**Configuration:**
```yaml
spec:
  securityContext:            # Pod level
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    securityContext:          # Container level
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
```

**Command:**
```bash
# Check a pod's security context
kubectl get pod my-pod -o jsonpath='{.spec.securityContext}'
kubectl get pod my-pod -o jsonpath='{.spec.containers[0].securityContext}'
```

**Verification:**
```bash
# Exec into pod and verify running as non-root
kubectl exec my-pod -- id
# Expected: uid=1000 gid=3000
kubectl exec my-pod -- touch /test 2>&1
# Expected: "Read-only file system" (if readOnlyRootFilesystem: true)
```

**Common CKS Trap:** Setting `runAsNonRoot: true` but using an image whose Dockerfile specifies USER root -- pod will fail to start with "must run as non-root" error. Fix: also set `runAsUser: 1000`. Another trap: `readOnlyRootFilesystem: true` breaks apps that write to temp directories -- mount an emptyDir at `/tmp`.

**Mini Lab (3 min):**
1. Create a pod with `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, capabilities drop ALL
2. Mount an emptyDir at `/tmp`
3. Exec in, verify: `id` shows non-root, `touch /test` fails, `touch /tmp/test` succeeds

---

### 5. Pod Security Admission

**Security Objective:** Enforce cluster-wide security standards at the namespace level without custom webhooks.

**Attack Prevented:** Deployment of privileged, hostNetwork, hostPID, or otherwise insecure pods.

**Kubernetes Mechanism:** Built-in admission controller (replaces deprecated PodSecurityPolicy). Three modes: `enforce` (reject), `audit` (log), `warn` (warn user). Three profiles: `privileged` (no restrictions), `baseline` (prevents known escalations), `restricted` (hardened).

**Configuration:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Command:**
```bash
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted --overwrite
```

**Verification:**
```bash
# Try to create a privileged pod -- should be rejected
kubectl run test --image=nginx -n production --dry-run=server -o yaml --overrides='{"spec":{"containers":[{"name":"test","image":"nginx","securityContext":{"privileged":true}}]}}'
# Expected: "Forbidden: violates PodSecurity"
```

**Common CKS Trap:** Applying `restricted` to `kube-system` namespace breaks system pods that need host access. Use `enforce: privileged` for kube-system. Another trap: forgetting that PSA is a label on the namespace, not a cluster-wide config -- you must label EACH namespace.

**Mini Lab (3 min):**
1. Create namespace `psa-test`
2. Label it with `enforce=restricted`
3. Try to create a pod without securityContext -- observe rejection
4. Fix the pod to comply with restricted profile (runAsNonRoot, drop ALL, seccomp RuntimeDefault)
5. Apply again -- should succeed

---

### 6. Linux Capabilities

**Security Objective:** Grant only the minimum kernel-level privileges a container needs.

**Attack Prevented:** Container breakout via excessive capabilities (e.g., `SYS_ADMIN` allows mounting filesystems, loading kernel modules).

**Kubernetes Mechanism:** Containers start with a default set of capabilities. Use `securityContext.capabilities` to `drop` and `add` specific capabilities.

**Configuration:**
```yaml
securityContext:
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE   # Bind to ports < 1024
```

Common capabilities:
| Capability | Purpose | Risk |
|-----------|---------|------|
| NET_BIND_SERVICE | Bind to low ports | Low |
| SYS_TIME | Modify system clock | Medium |
| CHOWN | Change file ownership | Medium |
| SYS_ADMIN | Almost everything | CRITICAL - never add |
| NET_RAW | Raw sockets | Medium - allows packet sniffing |
| DAC_OVERRIDE | Bypass file permissions | High |

**Command:**
```bash
# Check capabilities of running container process
kubectl exec my-pod -- cat /proc/1/status | grep Cap
# Decode capability bitmask
capsh --decode=<hex-value>
```

**Verification:**
```bash
# After dropping ALL and adding NET_BIND_SERVICE:
kubectl exec my-pod -- cat /proc/1/status | grep CapEff
# Decode should show only cap_net_bind_service
```

**Common CKS Trap:** Dropping ALL capabilities without adding back what the app actually needs, causing the container to crash. Test with `baseline` profile first, then move to `restricted`. Another trap: capabilities are set at the CONTAINER level, not the pod level.

**Mini Lab (3 min):**
1. Deploy a pod with `capabilities: drop: [ALL]`
2. Verify it starts (image should not need special caps)
3. Check `cat /proc/1/status | grep Cap` -- CapEff should be 0000000000000000
4. Add `NET_BIND_SERVICE`, verify CapEff changes

---

### 7. Seccomp

**Security Objective:** Restrict which system calls a container can make to the kernel.

**Attack Prevented:** Kernel exploitation via dangerous syscalls (e.g., `ptrace`, `mount`, `reboot`).

**Kubernetes Mechanism:** `securityContext.seccompProfile` at pod or container level. Three types: `RuntimeDefault` (container runtime's built-in profile), `Localhost` (custom profile from node disk), `Unconfined` (no restrictions).

**Configuration:**
```yaml
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault    # Use container runtime's default profile
```

Custom profile (placed at `/var/lib/kubelet/seccomp/profiles/custom.json`):
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "exit", "exit_group", "openat", "close",
                "fstat", "mmap", "mprotect", "brk", "rt_sigaction",
                "access", "getpid", "clone", "execve"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

**Command:**
```bash
# Check if a pod has seccomp applied
kubectl get pod my-pod -o jsonpath='{.spec.securityContext.seccompProfile}'
# List available seccomp profiles on the node
ls /var/lib/kubelet/seccomp/profiles/
```

**Verification:**
```bash
# RuntimeDefault blocks dangerous syscalls:
kubectl exec my-pod -- unshare --user --pid 2>&1
# Expected: "Operation not permitted" (unshare syscall blocked)
```

**Common CKS Trap:** `Unconfined` means no seccomp at all (insecure). `RuntimeDefault` is the minimum you should use. Localhost profiles: the path is RELATIVE to `/var/lib/kubelet/seccomp/`, so `profiles/custom.json` maps to `/var/lib/kubelet/seccomp/profiles/custom.json`.

**Mini Lab (3 min):**
1. Create a pod with `seccompProfile.type: RuntimeDefault`
2. Verify pod starts and runs normally
3. Try to run a restricted syscall from inside the pod
4. Change to `Unconfined` and compare behavior

---

### 8. AppArmor

**Security Objective:** Restrict what files, network, and capabilities a container process can access using Linux kernel MAC.

**Attack Prevented:** Container process reading/writing sensitive host files, loading kernel modules, or accessing unauthorized network resources.

**Kubernetes Mechanism:** AppArmor profiles are loaded on the node, then referenced in pod annotations (legacy) or securityContext (v1.30+). Modes: `enforce` (block and log), `complain` (log only), `unconfined`.

**Configuration:**

Profile on node (`/etc/apparmor.d/k8s-deny-write`):
```
#include <tunables/global>
profile k8s-deny-write flags=(attach_disconnected) {
  #include <abstractions/base>
  file,
  deny /** w,   # deny all writes
}
```

Load the profile:
```bash
apparmor_parser /etc/apparmor.d/k8s-deny-write
```

Pod annotation (legacy, pre-v1.30):
```yaml
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-deny-write
```

Pod securityContext (v1.30+):
```yaml
spec:
  containers:
  - name: app
    securityContext:
      appArmorProfile:
        type: Localhost
        localhostProfile: k8s-deny-write
```

**Command:**
```bash
# Check loaded profiles
aa-status
# Load a profile
apparmor_parser /etc/apparmor.d/my-profile
# Reload
apparmor_parser -r /etc/apparmor.d/my-profile
```

**Verification:**
```bash
# Profile loaded
aa-status | grep k8s-deny-write
# Test: write should fail
kubectl exec apparmor-pod -- touch /tmp/test 2>&1
# Expected: "Permission denied"
```

**Common CKS Trap:** Profile must be loaded on the SPECIFIC NODE where the pod runs. If the pod gets scheduled to a node without the profile, it fails. Use nodeSelector or DaemonSet to ensure profile is loaded everywhere. Also: profile name in annotation must exactly match the loaded profile name.

**Mini Lab (3 min):**
1. Write AppArmor profile that denies writes to `/proc`
2. Load it with `apparmor_parser`
3. Create pod with the annotation referencing it
4. Exec into pod, verify `echo test > /proc/sysrq-trigger` is denied

---

### 9. Image Security / Trivy

**Security Objective:** Prevent deploying container images with known vulnerabilities or from untrusted registries.

**Attack Prevented:** Running containers with exploitable CVEs (remote code execution, privilege escalation in libraries or OS packages).

**Kubernetes Mechanism:** Image scanning with Trivy (or similar), admission controllers to enforce image policies (ImagePolicyWebhook, OPA Gatekeeper, Kyverno), private registry with pull secrets.

**Configuration:**

Private registry pull secret:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-pod
spec:
  imagePullSecrets:
  - name: registry-creds
  containers:
  - name: app
    image: private-registry.example.com/app:v1.2
```

Create the secret:
```bash
kubectl create secret docker-registry registry-creds \
  --docker-server=private-registry.example.com \
  --docker-username=user \
  --docker-password=pass
```

**Command:**
```bash
# Scan image for HIGH and CRITICAL vulnerabilities
trivy image --severity HIGH,CRITICAL nginx:1.25

# Scan and filter for specific CVE
trivy image nginx:1.25 2>&1 | grep CVE-2024

# List images used by pods
kubectl get pods -A -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}' | sort -u
```

**Verification:**
```bash
# After fixing (e.g., updating image tag):
trivy image --severity HIGH,CRITICAL nginx:1.25-alpine
# Expected: 0 vulnerabilities (or fewer than before)
```

**Common CKS Trap:** Using `latest` tag instead of specific version -- can't reproduce scans. Using image tag instead of digest -- tag can be overwritten. Always prefer `image: nginx@sha256:abc123...` in production.

**Mini Lab (3 min):**
1. Run `trivy image nginx:1.21` (old version, will have vulnerabilities)
2. Note the HIGH/CRITICAL count
3. Run `trivy image nginx:1.25-alpine` (newer, fewer vulns)
4. Update the pod to use the safer image
5. Verify the pod restarts with the new image

---

### 10. Admission Control

**Security Objective:** Intercept and validate/mutate API requests before objects are persisted.

**Attack Prevented:** Deployment of non-compliant resources (missing labels, insecure images, excessive privileges, non-approved registries).

**Kubernetes Mechanism:** Admission controllers are plugins in the API server. Two types: Validating (accept/reject) and Mutating (modify requests). Built-in (NodeRestriction, PodSecurity) and webhook-based (OPA Gatekeeper, Kyverno).

**Configuration:**

Enable admission controllers in API server:
```yaml
# /etc/kubernetes/manifests/kube-apiserver.yaml
spec:
  containers:
  - command:
    - kube-apiserver
    - --enable-admission-plugins=NodeRestriction,PodSecurity
```

ValidatingWebhookConfiguration:
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-policy
webhooks:
- name: validate.images.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["pods"]
  clientConfig:
    service:
      name: image-validator
      namespace: webhook-system
      path: /validate
    caBundle: <base64-ca-cert>
  admissionReviewVersions: ["v1"]
  sideEffects: None
  failurePolicy: Fail
```

**Command:**
```bash
# Check enabled admission plugins
grep "enable-admission-plugins" /etc/kubernetes/manifests/kube-apiserver.yaml
# List webhook configurations
kubectl get validatingwebhookconfigurations
kubectl get mutatingwebhookconfigurations
```

**Verification:**
```bash
# Create a pod that should be rejected by the webhook
kubectl run test --image=untrusted-registry.com/evil:latest
# Expected: rejected by admission webhook
```

**Common CKS Trap:** `failurePolicy: Ignore` means the webhook failing silently allows everything through (insecure). Use `failurePolicy: Fail` in production. Another trap: forgetting to mount the CA bundle for webhook TLS verification.

**Mini Lab (3 min):**
1. Check current admission plugins: `ps aux | grep kube-apiserver | tr ',' '\n' | grep -i admission`
2. Add `PodSecurity` to the list if missing
3. Restart API server (edit static pod manifest)
4. Label a namespace with `enforce=restricted`
5. Verify: privileged pods are rejected

---

### 11. Audit Logging

**Security Objective:** Record all API requests for security investigation and compliance.

**Attack Prevented:** Not an attack prevention mechanism directly, but enables detection of unauthorized access, data exfiltration, and forensic investigation after incidents.

**Kubernetes Mechanism:** API server audit logging with configurable policy (what to log) and backend (where to send logs). Four audit levels: None, Metadata, Request, RequestResponse.

**Configuration:**

Audit policy (`/etc/kubernetes/audit-policy.yaml`):
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  resources:
  - group: ""
    resources: ["secrets"]
  verbs: ["create", "update", "patch", "delete"]
- level: Metadata
  resources:
  - group: ""
    resources: ["pods", "services"]
- level: None
  resources:
  - group: ""
    resources: ["endpoints", "services/status"]
- level: Metadata
  omitStages:
  - RequestReceived
```

API server flags:
```yaml
- --audit-policy-file=/etc/kubernetes/audit-policy.yaml
- --audit-log-path=/var/log/kubernetes/audit.log
- --audit-log-maxage=30
- --audit-log-maxbackup=10
- --audit-log-maxsize=100
```

Must add volume mounts for both the policy file and the log directory.

**Command:**
```bash
# Check if auditing is enabled
grep "audit" /etc/kubernetes/manifests/kube-apiserver.yaml
# Read audit logs
tail -20 /var/log/kubernetes/audit.log | jq .
# Search audit logs for specific user
cat /var/log/kubernetes/audit.log | jq 'select(.user.username=="system:anonymous")'
```

**Verification:**
```bash
# Create a secret, then check audit log for the event
kubectl create secret generic test-audit --from-literal=key=value
tail -5 /var/log/kubernetes/audit.log | jq '.verb, .objectRef.resource'
# Expected: "create" "secrets"
```

**Common CKS Trap:** Forgetting to add volume and volumeMount for BOTH the policy file AND the log directory in the API server manifest. The API server pod will crash if the policy file is not mounted. Also: audit log files can grow very large -- always set maxage/maxbackup/maxsize.

**Mini Lab (3 min):**
1. Create audit policy that logs all secret operations at RequestResponse level
2. Add the flags and volume mounts to the API server manifest
3. Wait for API server to restart
4. Create a secret
5. Verify the event appears in the audit log

---

### 12. Runtime Security / Falco

**Security Objective:** Detect suspicious behavior in running containers in real time.

**Attack Prevented:** Shell access to containers, reading sensitive files (`/etc/shadow`, `/etc/passwd`), unexpected process execution, network connections to suspicious destinations.

**Kubernetes Mechanism:** Falco runs as a DaemonSet or systemd service, monitors kernel syscalls via eBPF, and triggers alerts based on rules. Not a Kubernetes-native resource but a standard CKS exam tool.

**Configuration:**

Custom rule (`/etc/falco/falco_rules.local.yaml`):
```yaml
- rule: Terminal Shell in Container
  desc: Detect shell spawned in a container
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, zsh) and
    not proc.pname in (healthcheck, node)
  output: >
    Shell in container (user=%user.name
    container=%container.name image=%container.image.repository
    shell=%proc.name parent=%proc.pname cmdline=%proc.cmdline
    namespace=%k8s.ns.name pod=%k8s.pod.name)
  priority: WARNING
  tags: [container, shell]
```

Falco config (`/etc/falco/falco.yaml`) key settings:
```yaml
rules_file:
  - /etc/falco/falco_rules.yaml
  - /etc/falco/falco_rules.local.yaml    # Custom rules override here
json_output: true
log_level: info
```

**Command:**
```bash
# Check Falco status
systemctl status falco
# View recent Falco alerts
journalctl -u falco --no-pager -n 20
# Hot-reload rules without restart
kill -1 $(pidof falco)
```

**Verification:**
```bash
# Trigger a rule: exec shell into a pod
kubectl exec -it test-pod -- /bin/bash
# Check Falco detected it
journalctl -u falco --no-pager -n 5
# Expected: "Shell in container" alert
```

**Common CKS Trap:** Editing `/etc/falco/falco_rules.yaml` instead of `/etc/falco/falco_rules.local.yaml`. The base rules file gets overwritten on Falco updates. Always use the local file for custom rules. Another trap: Falco outputs are configurable -- if the exam asks you to write output to a specific file, you need to configure `file_output` in `falco.yaml`.

**Mini Lab (3 min):**
1. Check Falco is running: `systemctl status falco`
2. Add a rule to `/etc/falco/falco_rules.local.yaml` that detects reading `/etc/shadow`
3. Restart Falco: `systemctl restart falco`
4. Trigger: `kubectl exec test-pod -- cat /etc/shadow`
5. Verify: `journalctl -u falco --no-pager -n 5`

---

### 13. Secrets / Encryption at Rest

**Security Objective:** Protect sensitive data (passwords, tokens, keys) stored in etcd.

**Attack Prevented:** Secrets read in plaintext from etcd backups, etcd snapshots, or direct etcd access.

**Kubernetes Mechanism:** Kubernetes Secrets are base64-encoded by default (NOT encrypted). EncryptionConfiguration enables encryption at rest using aescbc, aesgcm, or secretbox providers. The config is referenced by the API server.

**Configuration:**

EncryptionConfiguration (`/etc/kubernetes/enc/enc.yaml`):
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: $(head -c 32 /dev/urandom | base64)
  - identity: {}
```

API server manifest additions:
```yaml
- --encryption-provider-config=/etc/kubernetes/enc/enc.yaml
volumeMounts:
- name: enc
  mountPath: /etc/kubernetes/enc
  readOnly: true
volumes:
- name: enc
  hostPath:
    path: /etc/kubernetes/enc
    type: DirectoryOrCreate
```

**Command:**
```bash
# Verify encryption: read a secret from etcd directly
ETCDCTL_API=3 etcdctl get /registry/secrets/default/my-secret \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key | hexdump -C | head
# If encrypted: you'll see "k8s:enc:aescbc:v1:key1" prefix
# If NOT encrypted: you'll see plaintext secret data
```

**Verification:**
```bash
# After enabling encryption, re-encrypt all existing secrets:
kubectl get secrets -A -o json | kubectl replace -f -
# Then verify with etcdctl again
```

**Common CKS Trap:** Provider order matters. If `identity: {}` is listed FIRST, secrets are stored unencrypted. The first provider is used for encryption; all providers are tried for decryption. Always put the encryption provider (aescbc) first. Another trap: forgetting to re-encrypt existing secrets after enabling encryption -- old secrets remain unencrypted.

**Mini Lab (3 min):**
1. Create a secret: `kubectl create secret generic test-enc --from-literal=password=supersecret`
2. Read it from etcd -- observe plaintext
3. Create EncryptionConfiguration with aescbc
4. Add to API server manifest, restart
5. Create a new secret and verify it is encrypted in etcd

---

### 14. Cluster Hardening / kube-bench

**Security Objective:** Ensure the cluster configuration follows CIS Kubernetes Benchmark security best practices.

**Attack Prevented:** Misconfigured API server, kubelet, etcd, or controller-manager exposing the cluster to unauthorized access, data leaks, or privilege escalation.

**Kubernetes Mechanism:** kube-bench is an open-source tool that checks Kubernetes component configurations against CIS benchmarks. It scans static pod manifests, kubelet config, and etcd settings.

**Configuration:**

Key hardening settings to check/fix:

API server (`/etc/kubernetes/manifests/kube-apiserver.yaml`):
```yaml
- --anonymous-auth=false
- --authorization-mode=Node,RBAC       # NOT AlwaysAllow
- --enable-admission-plugins=NodeRestriction,PodSecurity
- --insecure-port=0                    # Deprecated but ensure it's 0
- --profiling=false
- --audit-log-path=/var/log/audit.log
```

Kubelet (`/var/lib/kubelet/config.yaml`):
```yaml
authentication:
  anonymous:
    enabled: false
  webhook:
    enabled: true
authorization:
  mode: Webhook                        # NOT AlwaysAllow
readOnlyPort: 0                        # Disable read-only port
protectKernelDefaults: true
```

**Command:**
```bash
# Run kube-bench on master
kube-bench run --targets master
# Run on worker
kube-bench run --targets node
# Check specific benchmark item
kube-bench run --targets master --check 1.2.1
```

**Verification:**
```bash
# After fixing issues, re-run kube-bench
kube-bench run --targets master 2>&1 | grep -E "PASS|FAIL|WARN" | sort | uniq -c
# Goal: 0 FAIL items for scored checks
```

**Common CKS Trap:** kube-bench reports many items. Focus on FAIL items, not WARN. Some WARN items are informational and cannot be automated. Also: after editing `/etc/kubernetes/manifests/kube-apiserver.yaml`, the API server restarts automatically (static pod), but if the YAML is malformed, it won't come back -- always validate YAML before saving.

**Mini Lab (3 min):**
1. Run `kube-bench run --targets master` and note FAIL count
2. Pick the first FAIL item, read the remediation
3. Apply the fix (edit the relevant config file)
4. Restart the affected component if needed
5. Re-run kube-bench and verify the item now passes

---

### 15. kubelet Security

**Security Objective:** Secure the kubelet API and configuration to prevent unauthorized node-level access.

**Attack Prevented:** Unauthenticated access to the kubelet API (port 10250) allowing pod listing, exec, log reading, or even arbitrary command execution on the node.

**Kubernetes Mechanism:** kubelet configuration file (`/var/lib/kubelet/config.yaml`) and flags control authentication, authorization, TLS, and read-only port settings.

**Configuration:**

Secure kubelet config (`/var/lib/kubelet/config.yaml`):
```yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
authentication:
  anonymous:
    enabled: false               # Block unauthenticated requests
  webhook:
    enabled: true                # Use API server for authn
    cacheTTL: 2m0s
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: Webhook                  # Use API server for authz (NOT AlwaysAllow)
readOnlyPort: 0                  # Disable insecure read-only port (10255)
protectKernelDefaults: true      # Enforce sysctl safety
rotateCertificates: true         # Auto-rotate kubelet certs
serverTLSBootstrap: true         # Request serving cert from API
eventRecordQPS: 5
```

**Command:**
```bash
# Check kubelet config
cat /var/lib/kubelet/config.yaml | grep -A5 "authentication\|authorization\|readOnlyPort"
# Test anonymous access (should fail)
curl -k https://localhost:10250/pods
# Test read-only port (should be refused)
curl http://localhost:10255/pods
```

**Verification:**
```bash
# Anonymous access returns 401
curl -sk https://localhost:10250/pods 2>&1 | head -5
# Expected: "Unauthorized"

# Read-only port is closed
curl -s http://localhost:10255/pods 2>&1
# Expected: "Connection refused"

# kubelet running with correct config
ps aux | grep kubelet | grep config
```

**Common CKS Trap:** Editing kubelet flags vs config file. Modern kubelet uses the config file (`--config=/var/lib/kubelet/config.yaml`), not command-line flags. If both exist, the config file takes precedence for most settings. Always check which one is being used with `ps aux | grep kubelet`. Another trap: forgetting `systemctl restart kubelet` after config changes.

**Mini Lab (3 min):**
1. Check current kubelet config: `cat /var/lib/kubelet/config.yaml`
2. Verify anonymous auth is disabled, authorization mode is Webhook
3. Verify readOnlyPort is 0
4. Test: `curl -k https://localhost:10250/pods` should return 401
5. Test: `curl http://localhost:10255/pods` should fail (connection refused)

---
---

# QUICK REFERENCE: CKS EXAM DAY CHECKLIST

```
FIRST 60 SECONDS OF EXAM:
  alias k=kubectl
  export do="--dry-run=client -o yaml"
  export now="--force --grace-period=0"

TOOL PRIORITY (reach for these in order):
  1. kubectl        -- always your first tool
  2. vim/nano       -- editing YAML and configs
  3. grep/find      -- locating files and settings
  4. openssl        -- certificate inspection
  5. crictl         -- container-level investigation
  6. systemctl      -- service management
  7. journalctl     -- log investigation
  8. trivy          -- image scanning
  9. falco          -- runtime security
  10. etcdctl       -- etcd operations

YAML GENERATION SPEED:
  Can kubectl generate it?  -->  use --dry-run=client -o yaml
  Is it a NetworkPolicy?    -->  copy from k8s docs
  Is it an Audit Policy?    -->  copy from k8s docs
  Is it EncryptionConfig?   -->  write from memory (this doc)
  Is it a Falco rule?       -->  write from memory (this doc)

AFTER EVERY CONFIG CHANGE:
  Static pod manifest changed  -->  wait for pod restart (or systemctl restart kubelet)
  Kubelet config changed       -->  systemctl restart kubelet
  Containerd config changed    -->  systemctl restart containerd && systemctl restart kubelet
  AppArmor profile changed     -->  apparmor_parser -r /etc/apparmor.d/profile
  Falco rules changed          -->  systemctl restart falco (or kill -1 $(pidof falco))
```

---

*End of CKS Security Toolbox, Speed Drills & Rapid Refresh*
