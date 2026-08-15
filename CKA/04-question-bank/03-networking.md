# CKA Question Bank — Services & Networking (20%)

*24 original, hands-on questions. Distribution weighted per `01-exam-snapshot-and-priorities.md`: DNS/CoreDNS troubleshooting is pulled up to P0 here because the priority matrix names it explicitly inside the P0 "control-plane/node/kubelet/CNI/DNS troubleshooting" row even though that row formally lives in the Troubleshooting domain — it's tested constantly through this domain's objects (Services, EndpointSlices, NetworkPolicy) so it gets the most questions. Everything else in this domain (Services, NetworkPolicy, Ingress, Gateway API) is P1 per the matrix; EndpointSlice hand-authoring and the CNI-adjacent edge case are P2. Attempt every task cold before opening the solution — that's the whole point.*

**Tally:** 6 Easy · 10 Medium · 8 Hard | 5×P0 · 17×P1 · 2×P2

---

### Question 1 — Expose a Deployment on ClusterIP
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** In namespace `netlab` (create it), you have a Deployment `web` with 2 replicas of `nginx` listening on container port 80. Expose it as a ClusterIP Service named `web-svc` on port 8080, routing to the container's port 80. Do this imperatively, not with a hand-written manifest.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create namespace netlab
k create deployment web -n netlab --image=nginx --replicas=2
k expose deployment web -n netlab --name=web-svc --port=8080 --target-port=80
```

**Verify:**
```bash
k get svc web-svc -n netlab -o wide
k get endpointslices -n netlab -l kubernetes.io/service-name=web-svc
k run tmp --image=busybox:1.36 -n netlab -it --rm --restart=Never -- wget -qO- web-svc:8080
```

**Common mistake:** Forgetting `--target-port` and letting it default to the Service's own `port` (8080) — nginx isn't listening on 8080, so it silently fails even though endpoints exist and look fine at a glance.

</details>

---

### Question 2 — NodePort with a pinned port number
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Create a NodePort Service `edge-svc` for the `web` Deployment from Question 1, using node port `30081` specifically (not an auto-assigned one), Service port 80, target port 80.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k expose deployment web -n netlab --name=edge-svc --port=80 --target-port=80 --type=NodePort --dry-run=client -o yaml > edge-svc.yaml
# edit edge-svc.yaml: add spec.ports[0].nodePort: 30081
k apply -f edge-svc.yaml
```

**Verify:**
```bash
k get svc edge-svc -n netlab
# PORT(S) column should show 80:30081/TCP
NODE_IP=$(k get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
curl "$NODE_IP:30081"
```

**Common mistake:** Trying to set `nodePort` via `kubectl expose` flags directly — there's no `--node-port` flag on `kubectl expose`; you must generate YAML and patch the field, or use `kubectl create service nodeport ... ` then `kubectl patch`/`kubectl edit`. Also forgetting the 30000–32767 range — anything outside it is rejected by the apiserver at apply time.

</details>

---

### Question 3 — ExternalName for a legacy database host
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Create a Service `legacy-db` in namespace `netlab` of type `ExternalName` that resolves to `db.internal.example.com`. Confirm from inside a Pod that `legacy-db.netlab.svc.cluster.local` resolves as a CNAME to that hostname — no proxying, no ClusterIP.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create service externalname legacy-db -n netlab --external-name=db.internal.example.com
```

**Verify:**
```bash
k get svc legacy-db -n netlab -o wide
# CLUSTER-IP column should show <none>
k run dnsutils -n netlab --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- nslookup legacy-db.netlab.svc.cluster.local
# answer should show it as a CNAME pointing at db.internal.example.com
```

**Common mistake:** Expecting `k describe svc` to show `Endpoints:` for an ExternalName Service — it never will, by design (no selector, no proxying). Looking for endpoints here is the wrong verification step entirely; DNS resolution is the only thing to check.

</details>

---

### Question 4 — Silent empty-Endpoints failure
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** A Service `api-svc` in namespace `netlab` was created against a Deployment `api` (Pods labeled `app=api-server`), but `curl api-svc:9090` from inside the cluster hangs/times out. The Service and Deployment both exist and show no errors. Find the root cause and fix it without deleting either object.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce the scenario first if practicing standalone:
k create deployment api -n netlab --image=nginx --port=9090
POD=$(k get pods -n netlab -l app=api -o jsonpath='{.items[0].metadata.name}')
k label pod -n netlab "$POD" app=api-server --overwrite
k expose deployment api -n netlab --name=api-svc --port=9090 --target-port=9090 --selector=app=wrong-label

# Diagnose:
k describe svc api-svc -n netlab       # Endpoints: <none>
k get pods -n netlab --show-labels     # compare actual Pod labels to the Service's Selector line

# Fix — patch the Service's selector to match reality:
k patch svc api-svc -n netlab -p '{"spec":{"selector":{"app":"api-server"}}}'
```

**Verify:**
```bash
k get endpointslices -n netlab -l kubernetes.io/service-name=api-svc
# should now list Pod IPs
k run tmp --image=busybox:1.36 -n netlab -it --rm --restart=Never -- wget -qO- --timeout=3 api-svc:9090
```

**Common mistake:** Assuming a mismatched selector will produce a visible error from `kubectl apply`/`kubectl describe` — it never does. `kubectl` accepts any selector value; an empty `Endpoints:`/`EndpointSlice` list is the *only* signal, and you have to think to check it.

</details>

---

### Question 5 — Endpoints look fine, traffic still fails (targetPort trap)
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** Service `echo-svc` in namespace `netlab` has healthy endpoints (correct Pod IPs listed) pointing at a Pod running a custom `busybox` container that starts a listener with `nc -lk -p 9500 -e echo ok`. The manifest declares `containerPort: 8080` and the Service's `targetPort` is also `8080`. Traffic still fails. Fix it without changing what the container actually listens on.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce:
cat <<'EOF' | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: echo-pod
  namespace: netlab
  labels: { app: echo }
spec:
  containers:
    - name: echo
      image: busybox:1.36
      command: ["sh","-c","nc -lk -p 9500 -e echo ok"]
      ports:
        - containerPort: 8080
EOF
k expose pod echo-pod -n netlab --name=echo-svc --port=80 --target-port=8080

# Diagnose — confirm the manifest lies about the real listening port:
k exec -n netlab echo-pod -- netstat -tlnp 2>/dev/null || k exec -n netlab echo-pod -- ss -tlnp

# Fix — targetPort must match the ACTUAL listening port, not the declared containerPort:
k patch svc echo-svc -n netlab -p '{"spec":{"ports":[{"port":80,"targetPort":9500}]}}'
```

**Verify:**
```bash
k run tmp --image=busybox:1.36 -n netlab -it --rm --restart=Never -- wget -qO- --timeout=3 echo-svc
```

**Common mistake:** Trusting the Pod spec's declared `containerPort` as ground truth. It is documentation only, not enforced by the kubelet or container runtime — the process inside can bind to any port regardless of what the manifest says. Endpoints being populated only proves the *selector* matched; it says nothing about whether `targetPort` matches the real listening socket.

</details>

---

### Question 6 — EndpointSlice shows an address that's not ready
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Service `ready-svc` in namespace `netlab` selects 3 Pods, but only 2 of the 3 are ever receiving traffic even though all 3 show `Running`. Use EndpointSlices (not just `kubectl get pods`) to pinpoint which Pod is excluded and why.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce: deploy 3 replicas, then make one fail readiness (not just liveness)
k create deployment ready-app -n netlab --image=nginx --replicas=3
k expose deployment ready-app -n netlab --name=ready-svc --port=80
# a bare `kubectl create deployment` has NO readinessProbe at all — without one, a
# Running container is always considered Ready, so a probe must exist before anything
# can meaningfully fail it. Add one that checks index.html:
k patch deployment ready-app -n netlab --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/readinessProbe","value":{"httpGet":{"path":"/index.html","port":80},"periodSeconds":2,"failureThreshold":1}}]'
k rollout status deployment ready-app -n netlab
# now break readiness on exactly one replica by removing the file the probe checks:
POD=$(k get pods -n netlab -l app=ready-app -o jsonpath='{.items[0].metadata.name}')
k exec -n netlab $POD -- sh -c "rm /usr/share/nginx/html/index.html"

# Diagnose:
k get endpointslices -n netlab -l kubernetes.io/service-name=ready-svc -o yaml
# look at each endpoint's conditions.ready field — one will be false, cross-reference its address/targetRef.name
```

**Verify:**
```bash
k get endpointslices -n netlab -l kubernetes.io/service-name=ready-svc \
  -o jsonpath='{range .items[*].endpoints[*]}{.targetRef.name}{" ready="}{.conditions.ready}{"\n"}{end}'
```

**Common mistake:** Only running `k get pods` and seeing all 3 as `Running` (which just reflects container process state) and concluding the Service must be misconfigured — `Running` says nothing about readiness-probe status. `k describe svc` also only gives a rolled-up `Endpoints:` line; you need the EndpointSlice's per-address `conditions.ready` field to see the not-ready one explicitly. Also: a Pod with no `readinessProbe` defined at all is always treated as ready the instant it's `Running` — "break" a Pod's container process or a file it serves without first confirming a probe actually exercises that failure path, and nothing will change from the Service's point of view.

</details>

---

### Question 7 — Hand-author an EndpointSlice for an external (non-Pod) backend
**Priority:** P2 · **Difficulty:** Hard · **Target time:** 9 min
**Task:** A legacy PostgreSQL VM lives at `10.244.9.9:5432`, outside the cluster's Pod network but reachable from nodes. Create a selector-less ClusterIP Service `legacy-pg` in namespace `netlab` on port 5432, and manually back it with an EndpointSlice pointing at that IP, so in-cluster Pods can reach it via `legacy-pg.netlab.svc.cluster.local:5432`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
cat <<'EOF' | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: legacy-pg
  namespace: netlab
spec:
  ports:
    - port: 5432
      protocol: TCP
  # deliberately no selector
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: legacy-pg-manual
  namespace: netlab
  labels:
    kubernetes.io/service-name: legacy-pg
addressType: IPv4
ports:
  - port: 5432
    protocol: TCP
endpoints:
  - addresses: ["10.244.9.9"]
    conditions:
      ready: true
EOF
```

**Verify:**
```bash
k describe svc legacy-pg -n netlab
# Endpoints: 10.244.9.9:5432
k run tmp --image=busybox:1.36 -n netlab -it --rm --restart=Never -- nslookup legacy-pg.netlab.svc.cluster.local
```

**Common mistake:** Omitting the `kubernetes.io/service-name: legacy-pg` label on the EndpointSlice — without it the slice is a valid, harmless object sitting in the namespace, completely disconnected from the Service, no matter how correctly its own `metadata.name` looks. There's no error at apply time; `k describe svc` will just keep showing `Endpoints: <none>`.

</details>

---

### Question 8 — Baseline DNS sanity check
**Priority:** P0 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Before touching any DNS troubleshooting task, prove cluster DNS is currently healthy: resolve the built-in `kubernetes.default` Service from a throwaway Pod, and also confirm which cluster DNS IP that Pod is actually configured to query.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- nslookup kubernetes.default
k run dnsutils2 --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- cat /etc/resolv.conf
```

**Verify:**
```bash
# nslookup should return an A record equal to the cluster IP of Service "kubernetes" in namespace default
k get svc kubernetes -o jsonpath='{.spec.clusterIP}'
# should match the nameserver line in resolv.conf
```

**Common mistake:** Testing DNS with a Pod's own `dnsPolicy: None` or a custom `dnsConfig` still attached from a previous exercise — always sanity-check `/etc/resolv.conf` itself before concluding CoreDNS is broken; the test Pod's own DNS config can be the actual fault, not the cluster.

</details>

---

### Question 9 — CoreDNS scaled to zero
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** Every Pod in the cluster has stopped resolving any DNS name, in-cluster or external. Diagnose and restore service using the smallest possible fix.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce:
k -n kube-system scale deployment coredns --replicas=0

# Diagnose:
k -n kube-system get pods -l k8s-app=kube-dns
k -n kube-system get deployment coredns
k -n kube-system describe svc kube-dns   # Endpoints: <none> because there are no coredns pods at all

# Fix:
k -n kube-system scale deployment coredns --replicas=2
```

**Verify:**
```bash
k -n kube-system get pods -l k8s-app=kube-dns -w   # wait for Running/Ready
k run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- nslookup kubernetes.default
```

**Common mistake:** Reflexively deleting the `coredns` Deployment and reapplying it from scratch (or reinstalling the CNI) instead of just checking replica count first — the fastest fix for a cluster-wide, sudden, total DNS outage is almost always to check whether CoreDNS Pods exist and are scheduled at all before assuming config corruption.

</details>

---

### Question 10 — kube-dns Service selector broken
**Priority:** P0 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** CoreDNS Pods in `kube-system` show `Running`/`2/2 Ready`, but DNS lookups still fail cluster-wide. Find the actual break point and fix it.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce:
k -n kube-system patch svc kube-dns -p '{"spec":{"selector":{"k8s-app":"kube-dns-broken"}}}'

# Diagnose:
k -n kube-system get pods -l k8s-app=kube-dns    # healthy
k -n kube-system describe svc kube-dns           # Endpoints: <none> — the tell
k -n kube-system get svc kube-dns -o jsonpath='{.spec.selector}'
k -n kube-system get pods --show-labels | grep coredns

# Fix — restore the correct selector:
k -n kube-system patch svc kube-dns -p '{"spec":{"selector":{"k8s-app":"kube-dns"}}}'
```

**Verify:**
```bash
k -n kube-system describe svc kube-dns   # Endpoints populated again
k run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- nslookup kubernetes.default
```

**Common mistake:** Jumping straight to reading CoreDNS Pod logs or the Corefile when the Pods themselves are already confirmed healthy — a healthy CoreDNS Deployment with a broken fronting Service is functionally identical, from the client's point of view, to CoreDNS being down entirely. Always check `kube-dns` Service endpoints as a distinct step from checking CoreDNS Pod status.

</details>

---

### Question 11 — Corefile syntax error crashes CoreDNS
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 9 min
**Task:** After a teammate "cleaned up" the `coredns` ConfigMap, CoreDNS Pods are now crash-looping. Identify the exact malformed line from the Pods' own logs and repair the Corefile, then make sure CoreDNS actually picks up the fix.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce — inject a broken forward block (missing closing brace):
k -n kube-system get cm coredns -o yaml > coredns-backup.yaml
k -n kube-system edit cm coredns
# deliberately delete a closing "}" in the "forward . /etc/resolv.conf {" block, save

k -n kube-system rollout restart deployment coredns
k -n kube-system get pods -l k8s-app=kube-dns   # CrashLoopBackOff

# Diagnose:
k -n kube-system logs -l k8s-app=kube-dns --tail=50
# error text will point at a Corefile parse error and line number

# Fix — correct the Corefile in the ConfigMap:
k -n kube-system apply -f coredns-backup.yaml
k -n kube-system rollout restart deployment coredns
```

**Verify:**
```bash
k -n kube-system rollout status deployment coredns
k run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.7 -it --rm --restart=Never -- nslookup kubernetes.default
```

**Common mistake:** Editing the `coredns` ConfigMap correctly but stopping there and expecting an automatic hot-reload — a plain `kubectl edit`/`kubectl apply` on the ConfigMap does not restart already-running CoreDNS Pods (the `reload` plugin polls on its own interval, not instantly), and a crash-looping Pod won't even get to reload logic. A `kubectl rollout restart deployment coredns` is the reliable way to force pickup.

</details>

---

### Question 12 — NetworkPolicy silently breaks DNS in one namespace
**Priority:** P0 · **Difficulty:** Hard · **Target time:** 8 min
**Task:** Pods in namespace `restricted` (create it) can't resolve any DNS name, but Pods in `default` resolve fine and CoreDNS itself is healthy. Find the actual cause — it isn't CoreDNS — and fix it with the minimal necessary change.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce:
k create namespace restricted
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
  namespace: restricted
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress: []
EOF

# Diagnose:
k -n kube-system get pods -l k8s-app=kube-dns    # healthy — rules this out
k run tmp -n restricted --image=busybox:1.36 -it --rm --restart=Never -- nslookup kubernetes.default   # times out
k get networkpolicy -n restricted                 # the actual culprit

# Fix — add a narrow DNS egress carve-out, don't just delete the policy:
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: restricted
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
EOF
```

**Verify:**
```bash
k run tmp -n restricted --image=busybox:1.36 -it --rm --restart=Never -- nslookup kubernetes.default
# succeeds now; confirm the original deny-all-egress policy is still in place for everything else
k run tmp2 -n restricted --image=busybox:1.36 -it --rm --restart=Never -- wget -qO- --timeout=3 http://example.com   # still blocked
```

**Common mistake:** A "namespace works / namespace doesn't work" split is a near-certain NetworkPolicy signature (CoreDNS itself has no per-namespace concept of who's allowed to query it) — chasing CoreDNS Pod logs or the Corefile first wastes time on a symptom that's identical whether the fault is CoreDNS-side or policy-side. Also: fixing this by deleting `deny-all-egress` entirely "solves" DNS but reintroduces open egress for everything else, which is a worse fix than a scoped port-53 allow rule.

</details>

---

### Question 13 — Default-deny all ingress
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** In namespace `secure` (create it), lock down all Pods so that no ingress traffic is accepted from anywhere, using the fewest lines of YAML possible.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create namespace secure
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: secure
spec:
  podSelector: {}
  policyTypes: [Ingress]
EOF
```

**Verify:**
```bash
k -n secure run target --image=nginx
k -n secure expose pod target --port=80
k run tmp --image=busybox:1.36 -n secure -it --rm --restart=Never -- wget -qO- --timeout=3 target
# must time out
```

**Common mistake:** Adding an empty `ingress: []` block "to be explicit" — this is functionally identical to omitting `ingress` entirely (both mean "no allowed ingress rules," i.e. full deny once `Ingress` is in `policyTypes`), but candidates sometimes second-guess themselves into thinking an empty list means "allow all" (it's the opposite: an *absent* key means no rules of that type at all, and either way nothing is allowed in).

</details>

---

### Question 14 — Scoped allow on top of default-deny
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** In namespace `secure`, Pods labeled `tier=backend` should accept ingress only from Pods labeled `tier=frontend`, only on TCP port 8080. Everything else to `backend` Pods must remain blocked. Do not touch any policy affecting `frontend` Pods themselves.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k -n secure run backend --image=nginx --labels=tier=backend --port=8080
k -n secure expose pod backend --port=8080 --target-port=8080
k -n secure run frontend --image=busybox:1.36 --labels=tier=frontend --command -- sleep 3600
k -n secure run intruder --image=busybox:1.36 --command -- sleep 3600

cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-default-deny
  namespace: secure
spec:
  podSelector:
    matchLabels: { tier: backend }
  policyTypes: [Ingress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: secure
spec:
  podSelector:
    matchLabels: { tier: backend }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels: { tier: frontend }
      ports:
        - protocol: TCP
          port: 8080
EOF
```

**Verify:**
```bash
k -n secure exec frontend -- wget -qO- --timeout=3 backend:8080   # succeeds
k -n secure exec intruder -- wget -qO- --timeout=3 backend:8080   # times out
```

**Common mistake:** Writing only the allow policy and skipping the separate default-deny policy, assuming the allow rule alone implies exclusivity — it doesn't. Multiple NetworkPolicies selecting the same Pod are unioned (OR'd), not intersected; without a policy putting `backend` into default-deny mode for `Ingress` in the first place, all other ingress traffic remains implicitly allowed regardless of how narrow your allow rule is.

</details>

---

### Question 15 — Fix a policy that "does nothing"
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 5 min
**Task:** A policy `block-intruder` was applied to namespace `secure` intending to block all ingress to `backend` except from `frontend`, but `intruder` can still reach `backend:8080`. Find the single missing field and fix it in place (don't rewrite the policy from scratch).

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce the bug:
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-intruder
  namespace: secure
spec:
  podSelector:
    matchLabels: { tier: backend }
  ingress:
    - from:
        - podSelector:
            matchLabels: { tier: frontend }
      ports:
        - protocol: TCP
          port: 8080
  # policyTypes is missing entirely
EOF

# Diagnose:
k -n secure get networkpolicy block-intruder -o yaml   # note: no policyTypes key at all
k -n secure exec intruder -- wget -qO- --timeout=3 backend:8080   # unexpectedly succeeds

# Fix:
k -n secure patch networkpolicy block-intruder --type=merge -p '{"spec":{"policyTypes":["Ingress"]}}'
```

**Verify:**
```bash
k -n secure exec intruder -- wget -qO- --timeout=3 backend:8080   # now times out
k -n secure exec frontend -- wget -qO- --timeout=3 backend:8080   # still succeeds
```

**Common mistake:** Assuming that writing an `ingress:` block is by itself enough to put a Pod into default-deny mode for ingress. Without the corresponding entry in `policyTypes`, the `ingress` rules are parsed but never enforced — Kubernetes silently treats the Pod as unrestricted for that traffic direction. This is arguably the single most common NetworkPolicy authoring bug.

</details>

---

### Question 16 — Three-tier segmentation with DNS carve-out
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 10 min
**Task:** In namespace `tier3` (create it), you have Pods labeled `tier=frontend`, `tier=backend`, and `tier=db`. Enforce: `frontend` may call `backend` on port 8080 only; `backend` may call `db` on port 5432 only; `frontend` must NOT be able to reach `db` directly under any circumstance; all three tiers must retain DNS resolution.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create namespace tier3
k -n tier3 run frontend --image=busybox:1.36 --labels=tier=frontend --command -- sleep 3600
k -n tier3 run backend  --image=nginx        --labels=tier=backend  --port=8080
k -n tier3 run db       --image=nginx        --labels=tier=db       --port=5432
k -n tier3 expose pod backend --port=8080 --target-port=8080
k -n tier3 expose pod db      --port=5432 --target-port=5432

cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-ingress
  namespace: tier3
spec:
  podSelector: { matchLabels: { tier: backend } }
  policyTypes: [Ingress]
  ingress:
    - from: [{ podSelector: { matchLabels: { tier: frontend } } }]
      ports: [{ protocol: TCP, port: 8080 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-ingress
  namespace: tier3
spec:
  podSelector: { matchLabels: { tier: db } }
  policyTypes: [Ingress]
  ingress:
    - from: [{ podSelector: { matchLabels: { tier: backend } } }]
      ports: [{ protocol: TCP, port: 5432 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-all-tiers
  namespace: tier3
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to: [{ namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } } }]
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
    - to: [{ podSelector: { matchLabels: { tier: backend } } }]
      ports: [{ protocol: TCP, port: 8080 }]
    - to: [{ podSelector: { matchLabels: { tier: db } } }]
      ports: [{ protocol: TCP, port: 5432 }]
EOF
```

**Verify:**
```bash
k -n tier3 exec frontend -- nslookup kubernetes.default                          # works
k -n tier3 exec frontend -- wget -qO- --timeout=3 backend:8080                   # works
k -n tier3 exec frontend -- wget -qO- --timeout=3 db:5432                        # times out
# backend/db are plain nginx images with no wget/curl binary — test backend's identity
# with a throwaway busybox Pod carrying the same label instead of exec'ing into nginx:
k -n tier3 run backend-tester --image=busybox:1.36 --labels=tier=backend -it --rm --restart=Never -- wget -qO- --timeout=3 db:5432   # works
```

**Common mistake:** Writing one blanket `allow-dns-all-tiers` egress policy without also scoping `frontend`'s own egress — since egress policies are additive per selected Pod, if `frontend` isn't itself selected by any restrictive egress policy, it retains full outbound access (including to `db`) regardless of how tightly `db`'s *ingress* is locked down. Ingress-side restriction on `db` alone is not sufficient if the task requires "must NOT be able to reach" as a hard guarantee — belt-and-suspenders means restricting both sides where the requirement is explicit.

</details>

---

### Question 17 — AND vs OR in policy peers
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 7 min
**Task:** Namespace `multi-ns` (create it) has Pods labeled `role=client`. Write a NetworkPolicy on Pods labeled `role=server` that allows ingress from **either** (a) any Pod labeled `role=client` in the *same* namespace, **or** (b) any Pod at all (regardless of label) in a namespace labeled `env=trusted` — without accidentally requiring both conditions simultaneously.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create namespace multi-ns
k label namespace multi-ns env=trusted --overwrite=false 2>/dev/null || true
k create namespace other-ns
k label namespace other-ns env=trusted

k -n multi-ns run server --image=nginx --labels=role=server --port=80
k -n multi-ns expose pod server --port=80
k -n multi-ns run client --image=busybox:1.36 --labels=role=client --command -- sleep 3600
k -n other-ns run any-pod --image=busybox:1.36 --command -- sleep 3600
k create namespace stranger-ns
k -n stranger-ns run stranger --image=busybox:1.36 --command -- sleep 3600

cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: server-allow-or
  namespace: multi-ns
spec:
  podSelector:
    matchLabels: { role: server }
  policyTypes: [Ingress]
  ingress:
    - from:
        # two SEPARATE list entries = OR
        - podSelector:
            matchLabels: { role: client }
        - namespaceSelector:
            matchLabels: { env: trusted }
      ports:
        - protocol: TCP
          port: 80
EOF
```

**Verify:**
```bash
k -n multi-ns exec client -- wget -qO- --timeout=3 server.multi-ns.svc.cluster.local     # allowed (rule a)
k -n other-ns exec any-pod -- wget -qO- --timeout=3 server.multi-ns.svc.cluster.local    # allowed (rule b — namespace is trusted, no label needed)
k -n stranger-ns exec stranger -- wget -qO- --timeout=3 server.multi-ns.svc.cluster.local # blocked (neither condition met)
```

**Common mistake:** Nesting `podSelector` and `namespaceSelector` inside the *same single peer entry* — that combination is a logical AND ("must be a `role=client` Pod, AND that Pod must live in a namespace with no other label constraint" collapses into something far narrower than intended, or worse, "must match both label conditions on the same object," which is often unsatisfiable). The fix is two distinct entries in the same `from` list, which the NetworkPolicy spec ORs together — this exact same/separate-entry distinction is one of the easiest things to get backwards under exam time pressure.

</details>

---

### Question 18 — Imperative Ingress creation
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 4 min
**Task:** Assuming `ingress-nginx` is already installed with IngressClass `nginx`, create an Ingress `shop-ingress` routing host `shop.local` path `/` to Service `shop-svc:80`, using a single imperative command.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create deployment shop --image=nginx
k expose deployment shop --name=shop-svc --port=80
k create ingress shop-ingress --rule="shop.local/=shop-svc:80" --class=nginx
```

**Verify:**
```bash
k describe ingress shop-ingress
# Rules section should show host shop.local, path /, and a resolved backend with non-empty endpoints
CTRL_IP=$(k -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || k get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
curl -H "Host: shop.local" "http://$CTRL_IP/"
```

**Common mistake:** Omitting `--class=nginx` and assuming a single installed controller will just pick it up — without a default `IngressClass` configured cluster-wide, an Ingress with no `ingressClassName` is never claimed by any controller and sits permanently inert with no error surfaced anywhere in `kubectl get ingress` output.

</details>

---

### Question 19 — Ingress exists, returns nothing
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 6 min
**Task:** Ingress `api-ingress` was created to route `api.local/` to `api-svc:8080`, but curling with the right Host header gets no response through the controller. `k get ingress` shows the object exists. Find and fix the misconfiguration.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Reproduce:
k create deployment api --image=nginx --port=8080
k expose deployment api --name=api-svc --port=8080 --target-port=80
cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
spec:
  ingressClassName: nginxx      # typo'd class name
  rules:
    - host: api.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-svc
                port:
                  number: 8080
EOF

# Diagnose:
k get ingressclass                      # real class is "nginx", not "nginxx"
k describe ingress api-ingress          # ingress class shown won't match any installed controller

# Fix:
k patch ingress api-ingress -p '{"spec":{"ingressClassName":"nginx"}}'
```

**Verify:**
```bash
k describe ingress api-ingress
CTRL_IP=$(k -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || k get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
curl -H "Host: api.local" "http://$CTRL_IP/"
```

**Common mistake:** Debugging the Service and backend Pod first (checking endpoints, targetPort, etc.) when the object never even reaches the controller in the first place because of the class mismatch — always confirm `k get ingressclass` and cross-check the Ingress's `ingressClassName` character-for-character before going deeper into backend-layer diagnosis.

</details>

---

### Question 20 — pathType semantics and TLS
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 10 min
**Task:** Deploy two Services, `v1-svc` and `v2-svc`. Create one Ingress on host `versions.local` with `/v1` and `/v2` prefix-routed to each — plus add TLS termination for `versions.local` using a self-signed certificate. Confirm HTTPS works for both paths.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create deployment v1 --image=nginx
k create deployment v2 --image=httpd
k expose deployment v1 --name=v1-svc --port=80
k expose deployment v2 --name=v2-svc --port=80

openssl req -x509 -nodes -days 30 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt -subj "/CN=versions.local/O=versions.local"
k create secret tls versions-tls --cert=tls.crt --key=tls.key

cat <<'EOF' | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: versions-ingress
spec:
  ingressClassName: nginx
  tls:
    - hosts: ["versions.local"]
      secretName: versions-tls
  rules:
    - host: versions.local
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend: { service: { name: v1-svc, port: { number: 80 } } }
          - path: /v2
            pathType: Prefix
            backend: { service: { name: v2-svc, port: { number: 80 } } }
EOF
```

**Verify:**
```bash
CTRL_IP=$(k -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || k get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
curl -k -H "Host: versions.local" "https://$CTRL_IP/v1"
curl -k -H "Host: versions.local" "https://$CTRL_IP/v2"
```

**Common mistake:** Using `pathType: Exact` for `/v1` and `/v2` when the task implies matching everything under those prefixes (e.g. `/v1/status`) — `Exact` only matches the literal string with no trailing content, so any sub-path 404s even though the top-level path works, which is easy to miss if verification only tests the bare `/v1` URL. Also: referencing the Service's `targetPort` value in the Ingress backend `port.number` field instead of its `port` — the Ingress backend always refers to the Service's own exposed `port`, never the container's port.

</details>

---

### Question 21 — Confirm Gateway API is actually installed
**Priority:** P1 · **Difficulty:** Easy · **Target time:** 3 min
**Task:** Before authoring any Gateway API objects, determine definitively whether the Gateway API CRDs and at least one `GatewayClass` are present in the cluster, and report what you'd need to do if they weren't.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k api-resources | grep gateway.networking.k8s.io
k get gatewayclass
k get crd | grep gateway.networking.k8s.io
```

**Verify:**
```bash
# If any of the above return results, CRDs + at least a class definition exist.
# If "no matches for kind" or empty output: CRDs must be installed first, e.g.:
# k apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.1.0/standard-install.yaml
# ...plus a controller implementation (nginx-gateway-fabric, Istio, Envoy Gateway, etc.) — a GatewayClass with no controller behind it never reaches Accepted:true.
```

**Common mistake:** Assuming Gateway API objects are core Kubernetes resources available by default the way `Ingress` is — they are CRDs installed separately and were only added to the CKA curriculum relatively recently; a task that hands you a broken/empty Gateway API setup and expects you to notice the CRDs simply aren't there is a very plausible trap.

</details>

---

### Question 22 — Basic Gateway + HTTPRoute
**Priority:** P1 · **Difficulty:** Medium · **Target time:** 8 min
**Task:** Assuming a Gateway API controller and `GatewayClass` named `nginx` are pre-installed, create a `Gateway` named `demo-gw` with a single HTTP listener on port 80 accepting routes from all namespaces, then an `HTTPRoute` named `demo-route` attached to it, routing path prefix `/` to Service `demo-svc:80`. Confirm both objects report `Accepted: True`.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create deployment demo --image=nginx
k expose deployment demo --name=demo-svc --port=80

cat <<'EOF' | k apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: demo-gw
spec:
  gatewayClassName: nginx
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces:
          from: All
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: demo-route
spec:
  parentRefs:
    - name: demo-gw
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: demo-svc
          port: 80
EOF
```

**Verify:**
```bash
k get gateway demo-gw -o jsonpath='{.status.conditions}'
k get httproute demo-route -o jsonpath='{.status.parents[0].conditions}'
GW_IP=$(k get gateway demo-gw -o jsonpath='{.status.addresses[0].value}')
curl "http://$GW_IP/"
```

**Common mistake:** Checking only that `kubectl apply` succeeded and stopping there — a syntactically valid `HTTPRoute` can apply cleanly while its `status.parents[].conditions` shows `Accepted: False` (e.g. because `parentRefs` doesn't resolve to an existing Gateway, or the Gateway's listener doesn't allow routes from that namespace). Gateway API is far more status-condition-driven than Ingress ever was — treat a clean `apply` as necessary, not sufficient.

</details>

---

### Question 23 — Cross-namespace backend and weighted traffic split
**Priority:** P1 · **Difficulty:** Hard · **Target time:** 12 min
**Task:** `demo-gw` and `demo-route` from Question 22 exist in the `default` namespace. Add a second backend `demo-v2-svc` living in namespace `canary` (create it), and update `demo-route` to split traffic 80/20 between `demo-svc` (default ns) and `demo-v2-svc` (canary ns) using `weight`. Cross-namespace backend references are denied by default — make the necessary authorization change too.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
k create namespace canary
k -n canary create deployment demo-v2 --image=httpd
k -n canary expose deployment demo-v2 --name=demo-v2-svc --port=80

cat <<'EOF' | k apply -f -
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-default-to-canary
  namespace: canary
spec:
  from:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      namespace: default
  to:
    - group: ""
      kind: Service
      name: demo-v2-svc
EOF

cat <<'EOF' | k apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: demo-route
spec:
  parentRefs:
    - name: demo-gw
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: demo-svc
          port: 80
          weight: 80
        - name: demo-v2-svc
          namespace: canary
          port: 80
          weight: 20
EOF
```

**Verify:**
```bash
k get httproute demo-route -o jsonpath='{.status.parents[0].conditions}'
# ResolvedRefs should be True only once the ReferenceGrant exists — check without it first, then with it
GW_IP=$(k get gateway demo-gw -o jsonpath='{.status.addresses[0].value}')
for i in $(seq 1 20); do curl -s "http://$GW_IP/"; done | sort | uniq -c
```

**Common mistake:** Adding the cross-namespace `backendRef` and expecting it to just work because the Service name/namespace/port are all technically correct — Gateway API denies cross-namespace backend references by default as a security boundary, and the fix lives in the *target* namespace (`canary`, where the Service is), not in the `HTTPRoute`'s own namespace. Without the `ReferenceGrant`, `status.parents[].conditions` shows `ResolvedRefs: False` and zero traffic is ever sent to the canary backend, even though `kubectl apply` on the route succeeds without error.

</details>

---

### Question 24 — CNI pod-CIDR mismatch strands a node's Pods in ContainerCreating
**Priority:** P2 · **Difficulty:** Medium · **Target time:** 8 min
**Task:** Node `worker-2` shows `Ready` in `kubectl get nodes`, but every new Pod scheduled onto it stays stuck in `ContainerCreating` indefinitely, while Pods on other nodes are fine. Diagnose whether this is a CNI pod-CIDR configuration mismatch (as opposed to a kubelet health problem), and fix it without draining or rejoining the node.

<details>
<summary>Solution & Verification (attempt it yourself first!)</summary>

**Solve:**
```bash
# Diagnose — confirm the node itself is healthy, then look at what's actually failing:
k get nodes -o wide
k describe node worker-2 | grep -A5 Conditions
k get pods -A -o wide --field-selector spec.nodeName=worker-2 | grep ContainerCreating
STUCK=$(k get pods -A -o wide --field-selector spec.nodeName=worker-2 --no-headers | awk '$4=="ContainerCreating"{print $1" "$2; exit}')
k describe pod -n $(echo "$STUCK" | awk '{print $1}') $(echo "$STUCK" | awk '{print $2}')
# Events will show something like: "failed to set bridge addr" or
# "no IP addresses available in range set: 10.244.2.0/24" from the CNI plugin itself

# Compare the CNI's configured network against what kubeadm actually initialized:
k -n kube-system get cm kubeadm-config -o yaml | grep -i podSubnet
k -n kube-system get cm kube-flannel-cfg -o yaml | grep -A3 net-conf.json
# a mismatch here (e.g. kubeadm's podSubnet is 10.244.0.0/16 but the CNI ConfigMap
# still has an old/different Network value) is the actual root cause

# Fix — correct the CNI ConfigMap to match the cluster's real pod-network-cidr,
# then restart the CNI DaemonSet so every node (including worker-2) picks it up:
k -n kube-system patch cm kube-flannel-cfg --type=merge -p \
  '{"data":{"net-conf.json":"{\"Network\": \"10.244.0.0/16\", \"Backend\": {\"Type\": \"vxlan\"}}"}}'
k -n kube-system rollout restart daemonset kube-flannel-ds
```

**Verify:**
```bash
k -n kube-system rollout status daemonset kube-flannel-ds
k -n kube-system get pods -o wide -l app=flannel   # Running on every node, including worker-2
k get pods -A -o wide --field-selector spec.nodeName=worker-2   # previously-stuck Pod now Running with a valid Pod IP
```

**Common mistake:** Treating a `Ready` node condition as proof that networking is fully functional — `NodeReady` reflects kubelet's own health/heartbeat status, not whether the CNI plugin actually has a working IP range assigned on that node. A pod-CIDR mismatch only surfaces once you try to actually schedule and sandbox a Pod there; nothing about the node object itself flags it. Also: restarting the kubelet or rejoining the node "fixes" the symptom temporarily at best — the CNI ConfigMap itself is the source of truth and must be corrected, or the same failure recurs on the next new Pod.

</details>
