# CKA Micro-Drills

*Purpose: pure command-recall reps, not concept review — for concepts see `02-topics/`. Each drill
states a target time; time yourself, then check the answer. The goal is that the fastest correct
command becomes reflexive, not that you understand *why* (you already do, from CKAD + `02-topics/`).
Distribution across drills is deliberately skewed toward the P0 rows in
`01-exam-snapshot-and-priorities.md` — Troubleshooting, kubeadm/static-pods/certs, etcd
backup/restore, and RBAC dominate the count below; Storage, CRDs, and Argo/GitOps-adjacent topics
get almost none, matching their P2/P3 priority. All scenarios (pod names, node names, namespaces)
are invented for drilling purposes only.*

Assume every session starts with:

```bash
alias k=kubectl
export do="--dry-run=client -o yaml"
```

Answers show the single fastest command — not the only valid one, and not an explanation. If your
own muscle-memory command reaches the same end state, that's fine.

---

## 30-Second Drills

1. Create a namespace called `billing`.

<details><summary>Answer</summary>

```bash
k create namespace billing
```
</details>

2. Show the last 20 log lines for pod `web-1`.

<details><summary>Answer</summary>

```bash
k logs web-1 --tail=20
```
</details>

3. List every pod, across all namespaces, that is not currently `Running`.

<details><summary>Answer</summary>

```bash
k get pods -A --field-selector=status.phase!=Running
```
</details>

4. Show the expiration dates of all kubeadm-managed certificates on this control-plane node.

<details><summary>Answer</summary>

```bash
kubeadm certs check-expiration
```
</details>

5. Check whether your current context's user can create Deployments in namespace `shop`.

<details><summary>Answer</summary>

```bash
k auth can-i create deployments -n shop
```
</details>

6. Add a `NoSchedule` taint with key `maintenance=true` to node `worker-3`.

<details><summary>Answer</summary>

```bash
k taint node worker-3 maintenance=true:NoSchedule
```
</details>

7. Get the ClusterIP of Service `catalog` in namespace `shop`.

<details><summary>Answer</summary>

```bash
k get svc catalog -n shop -o jsonpath='{.spec.clusterIP}'
```
</details>

8. Confirm the etcd static pod is `Running` on this control-plane node.

<details><summary>Answer</summary>

```bash
k -n kube-system get pods -l component=etcd
```
</details>

9. Check the current status (target vs. actual replicas) of HPA `web`.

<details><summary>Answer</summary>

```bash
k get hpa web
```
</details>

10. Scale Deployment `web` to 5 replicas.

<details><summary>Answer</summary>

```bash
k scale deployment web --replicas=5
```
</details>

11. List every `Pending` PersistentVolumeClaim in namespace `data`.

<details><summary>Answer</summary>

```bash
k get pvc -n data --field-selector=status.phase=Pending
```
</details>

12. List every ClusterRoleBinding that references ClusterRole `cluster-admin`.

<details><summary>Answer</summary>

```bash
k get clusterrolebindings | grep cluster-admin
```
</details>

13. Show the kubeadm CLI version installed on this node.

<details><summary>Answer</summary>

```bash
kubeadm version
```
</details>

14. Check the kubelet service's current run state on this node.

<details><summary>Answer</summary>

```bash
systemctl status kubelet
```
</details>

15. Cordon node `worker-2` so no new pods land there (existing pods stay put).

<details><summary>Answer</summary>

```bash
k cordon worker-2
```
</details>

16. Delete Service `orphan-svc` in namespace `test`.

<details><summary>Answer</summary>

```bash
k delete svc orphan-svc -n test
```
</details>

---

## 1-Minute Drills

1. Generate a Deployment YAML for image `nginx:1.27` named `web` with 3 replicas, without applying it.

<details><summary>Answer</summary>

```bash
k create deployment web --image=nginx:1.27 --replicas=3 $do
```
</details>

2. Find which node Pod `payments-0` is currently scheduled on.

<details><summary>Answer</summary>

```bash
k get pod payments-0 -o wide
```
</details>

3. Show the last 50 lines of the kubelet's own journal on this node.

<details><summary>Answer</summary>

```bash
journalctl -u kubelet -n 50
```
</details>

4. Generate a ready-to-run join command for adding a new worker node.

<details><summary>Answer</summary>

```bash
kubeadm token create --print-join-command
```
</details>

5. List the static pod manifests currently active on this control-plane node.

<details><summary>Answer</summary>

```bash
ls /etc/kubernetes/manifests
```
</details>

6. Show the current kubeadm-tracked cluster version and the next available upgrade target.

<details><summary>Answer</summary>

```bash
kubeadm upgrade plan
```
</details>

7. Take an etcd snapshot backup to `/opt/etcd-backup.db` (TLS env vars already exported).

<details><summary>Answer</summary>

```bash
etcdctl snapshot save /opt/etcd-backup.db
```
</details>

8. Create a Role `pod-reader` in namespace `shop` allowed to get/list/watch Pods.

<details><summary>Answer</summary>

```bash
k create role pod-reader --verb=get,list,watch --resource=pods -n shop
```
</details>

9. Bind ClusterRole `view` to ServiceAccount `monitor` in namespace `ops`, scoped to that namespace only.

<details><summary>Answer</summary>

```bash
k create rolebinding monitor-view --clusterrole=view --serviceaccount=ops:monitor -n ops
```
</details>

10. List every Helm release across all namespaces.

<details><summary>Answer</summary>

```bash
helm list -A
```
</details>

11. Create a PriorityClass named `high-priority` with value `100000`.

<details><summary>Answer</summary>

```bash
k create priorityclass high-priority --value=100000
```
</details>

12. Check whether any NetworkPolicy already exists in namespace `finance`.

<details><summary>Answer</summary>

```bash
k get networkpolicy -n finance
```
</details>

13. Expose existing Deployment `catalog` as a ClusterIP Service on port 80.

<details><summary>Answer</summary>

```bash
k expose deployment catalog --port=80 --target-port=80
```
</details>

14. Create an HPA for Deployment `web`: target 60% CPU, min 2, max 8 replicas.

<details><summary>Answer</summary>

```bash
k autoscale deployment web --cpu-percent=60 --min=2 --max=8
```
</details>

15. List every CustomResourceDefinition installed in the cluster.

<details><summary>Answer</summary>

```bash
k get crds
```
</details>

16. Pause the rollout of Deployment `web` so you can batch several changes.

<details><summary>Answer</summary>

```bash
k rollout pause deployment web
```
</details>

---

## 2-Minute Drills

1. Pod `web-7` is stuck `ImagePullBackOff` — find the exact error reason.

<details><summary>Answer</summary>

```bash
k describe pod web-7 | grep -A5 Events
```
</details>

2. Pod `db-2` is `Pending` — confirm whether it's an insufficient-resources scheduling failure.

<details><summary>Answer</summary>

```bash
k describe pod db-2 | grep -A10 Events
```
</details>

3. List every container on this node directly via the container runtime, bypassing the kubelet.

<details><summary>Answer</summary>

```bash
crictl ps -a
```
</details>

4. Fetch the runtime-level logs for container ID `abc123` directly via CRI (kubelet layer unavailable).

<details><summary>Answer</summary>

```bash
crictl logs abc123
```
</details>

5. Check the expiration date of just the apiserver certificate (not the whole cert list).

<details><summary>Answer</summary>

```bash
kubeadm certs check-expiration | grep apiserver
```
</details>

6. Renew only the etcd server certificate, without touching the rest of the control plane.

<details><summary>Answer</summary>

```bash
kubeadm certs renew etcd-server
```
</details>

7. Temporarily pull the `kube-scheduler` static pod out of rotation without deleting its manifest for good.

<details><summary>Answer</summary>

```bash
mv /etc/kubernetes/manifests/kube-scheduler.yaml /tmp/
```
</details>

8. Verify the health of every etcd cluster member endpoint.

<details><summary>Answer</summary>

```bash
etcdctl endpoint health --cluster
```
</details>

9. Check whether ServiceAccount `deployer` (namespace `ci`) can delete Pods in namespace `prod`.

<details><summary>Answer</summary>

```bash
k auth can-i delete pods --as=system:serviceaccount:ci:deployer -n prod
```
</details>

10. Find every RoleBinding/ClusterRoleBinding that references ServiceAccount `deployer`.

<details><summary>Answer</summary>

```bash
k get rolebindings,clusterrolebindings -A -o wide | grep deployer
```
</details>

11. Render the Kustomize overlay in `./overlays/prod` to stdout without applying it.

<details><summary>Answer</summary>

```bash
k kustomize ./overlays/prod
```
</details>

12. Pin Deployment `cache`'s pods to nodes labeled `disktype=ssd` via a live patch.

<details><summary>Answer</summary>

```bash
k patch deployment cache -p '{"spec":{"template":{"spec":{"nodeSelector":{"disktype":"ssd"}}}}}'
```
</details>

13. Create a default-deny-all-ingress NetworkPolicy for every pod in namespace `finance`.

<details><summary>Answer</summary>

```bash
k apply -n finance -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes: ["Ingress"]
EOF
```
</details>

14. List every Gateway API `HTTPRoute` in namespace `shop`.

<details><summary>Answer</summary>

```bash
k get httproutes -n shop
```
</details>

15. Check which CNI config files are currently present on this node.

<details><summary>Answer</summary>

```bash
ls /etc/cni/net.d/
```
</details>

16. Check whether Pod Security Admission `restricted` is enforced on namespace `payments`.

<details><summary>Answer</summary>

```bash
k get ns payments -o jsonpath='{.metadata.labels}'
```
</details>

---

## 3-Minute Drills

1. Safely drain node `worker-1` for maintenance (DaemonSets and local ephemeral data expected).

<details><summary>Answer</summary>

```bash
k drain worker-1 --ignore-daemonsets --delete-emptydir-data --force
```
</details>

2. Bring `worker-1` back into rotation after maintenance and confirm it's schedulable again.

<details><summary>Answer</summary>

```bash
k uncordon worker-1 && k get node worker-1
```
</details>

3. Upgrade the `kubeadm` package itself (not the cluster yet) to `1.35.2-1.1` on this control-plane node.

<details><summary>Answer</summary>

```bash
apt-mark unhold kubeadm && apt-get install -y kubeadm=1.35.2-1.1 && apt-mark hold kubeadm
```
</details>

4. Take a full etcd snapshot with explicit endpoint and TLS flags (no pre-exported env vars).

<details><summary>Answer</summary>

```bash
etcdctl snapshot save /opt/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```
</details>

5. Verify an existing snapshot file's integrity and revision before trusting it for a restore.

<details><summary>Answer</summary>

```bash
etcdctl snapshot status /opt/etcd-backup.db --write-out=table
```
</details>

6. Create a ClusterRole `node-viewer` (get/list nodes only) and bind it cluster-wide to group `ops-team`.

<details><summary>Answer</summary>

```bash
k create clusterrole node-viewer --verb=get,list --resource=nodes && k create clusterrolebinding node-viewer-binding --clusterrole=node-viewer --group=ops-team
```
</details>

7. Manually inspect the SAN and expiry of the apiserver certificate file (no `kubeadm` available).

<details><summary>Answer</summary>

```bash
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -A2 "Subject Alternative\|Not After"
```
</details>

8. Pod `web-4` is `CrashLoopBackOff` — pull the logs from its previous, already-crashed instance.

<details><summary>Answer</summary>

```bash
k logs web-4 --previous
```
</details>

9. Test whether cluster DNS resolution is working at all, from a disposable pod.

<details><summary>Answer</summary>

```bash
k run dns-test --rm -it --image=busybox:1.28 --restart=Never -- nslookup kubernetes.default
```
</details>

10. Node `worker-2` shows `NotReady` — scan the kubelet's own journal for the root-cause error.

<details><summary>Answer</summary>

```bash
journalctl -u kubelet -n 100 --no-pager | grep -i error
```
</details>

11. Upgrade Helm release `web-app` to a new chart version, auto-rolling-back on failure.

<details><summary>Answer</summary>

```bash
helm upgrade web-app ./chart --atomic
```
</details>

12. Patch Deployment `cache` so its own pods never land two-per-node (required pod anti-affinity).

<details><summary>Answer</summary>

```bash
k patch deployment cache --type=json -p '[{"op":"add","path":"/spec/template/spec/affinity","value":{"podAntiAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":[{"labelSelector":{"matchLabels":{"app":"cache"}},"topologyKey":"kubernetes.io/hostname"}]}}}]'
```
</details>

13. Allow namespace `shop`'s pods to reach only namespace `db` on port 5432, denying all other egress.

<details><summary>Answer</summary>

```bash
k apply -n shop -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shop-to-db-only
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: db
    ports:
    - protocol: TCP
      port: 5432
EOF
```
</details>

---

## 5-Minute Drills

1. Fully upgrade this control-plane node to `v1.35.2`: drain, upgrade kubeadm, apply, upgrade kubelet/kubectl, uncordon.

<details><summary>Answer</summary>

```bash
k drain cp-1 --ignore-daemonsets
apt-mark unhold kubeadm && apt-get install -y kubeadm=1.35.2-1.1 && apt-mark hold kubeadm
kubeadm upgrade apply v1.35.2
apt-mark unhold kubelet kubectl && apt-get install -y kubelet=1.35.2-1.1 kubectl=1.35.2-1.1 && apt-mark hold kubelet kubectl
systemctl daemon-reload && systemctl restart kubelet
k uncordon cp-1
```
</details>

2. Rehearse a full etcd backup-and-restore: snapshot, restore into a fresh data-dir, repoint the static pod at it.

<details><summary>Answer</summary>

```bash
etcdctl snapshot save /opt/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
etcdutl snapshot restore /opt/etcd-backup.db --data-dir=/var/lib/etcd-restore
# then edit /etc/kubernetes/manifests/etcd.yaml hostPath -> /var/lib/etcd-restore
```
</details>

3. Node `worker-3`'s pods are all stuck `ContainerCreating` because the CNI plugin is missing — diagnose and fix.

<details><summary>Answer</summary>

```bash
k describe node worker-3 | grep -A5 Conditions
ls /etc/cni/net.d/ /opt/cni/bin/
k apply -f <cni-daemonset-manifest-url>
systemctl restart kubelet
```
</details>

4. Renew every kubeadm-managed certificate cluster-wide and force all control-plane static pods to pick up the new ones.

<details><summary>Answer</summary>

```bash
kubeadm certs renew all
mkdir -p /tmp/manifests-backup && mv /etc/kubernetes/manifests/*.yaml /tmp/manifests-backup/ && sleep 20 && mv /tmp/manifests-backup/*.yaml /etc/kubernetes/manifests/
```
</details>

5. Build least-privilege access for a CI ServiceAccount: create it, scope a ClusterRole to deployments/services, bind it to one namespace, verify.

<details><summary>Answer</summary>

```bash
k create serviceaccount ci-deployer -n ci
k create clusterrole ci-deploy-role --verb=get,list,watch,create,update,patch --resource=deployments,services
k create rolebinding ci-deploy-binding --clusterrole=ci-deploy-role --serviceaccount=ci:ci-deployer -n prod
k auth can-i create deployments --as=system:serviceaccount:ci:ci-deployer -n prod
```
</details>

6. Review then apply the Kustomize overlay in `overlays/prod`, checking the diff against the live cluster first.

<details><summary>Answer</summary>

```bash
k kustomize overlays/prod
k diff -k overlays/prod
k apply -k overlays/prod
```
</details>

7. Node `worker-2` is `NotReady` with x509 client-cert errors — rotate its kubelet client cert and confirm it recovers.

<details><summary>Answer</summary>

```bash
rm -f /var/lib/kubelet/pki/kubelet-client-current.pem
systemctl restart kubelet
k get csr
k certificate approve <csr-name>
k get node worker-2
```
</details>

8. Provision a StorageClass, a dynamically-bound PVC on it, and a pod mounting that PVC — confirm it all binds.

<details><summary>Answer</summary>

```bash
k apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: storage-test
spec:
  containers:
  - name: storage-test
    image: busybox
    command: ["sleep", "3600"]
    volumeMounts:
    - mountPath: /data
      name: vol
  volumes:
  - name: vol
    persistentVolumeClaim:
      claimName: data-pvc
EOF
k get pvc data-pvc
```
</details>

---

## Drill Count by Domain (for calibration against `01-exam-snapshot-and-priorities.md`)

| Domain | Priority | Drill count |
|---|---|---|
| Troubleshooting (logs, events, crictl, journalctl, DNS, CrashLoop) | P0 | 14 |
| kubeadm bootstrap/upgrade/static pods + certificate management | P0 | 15 |
| etcd backup & restore | P0 | 6 |
| RBAC (Roles, ClusterRoles, bindings, `auth can-i`) | P0 | 8 |
| Advanced scheduling (taints, affinity, PriorityClass) | P1 | 4 |
| Helm & Kustomize | P1 | 4 |
| Services & Gateway API | P1 | 4 |
| NetworkPolicy | P1 | 3 |
| HPA / autoscaling | P1 | 2 |
| Workloads core (Deployments, scale, rollout) | P2 | 4 |
| Storage | P2 | 2 |
| CNI (config inspection) | P2 | 1 |
| CRDs | P2 | 1 |
| Admission / Pod Security Admission | P2 | 1 |
| **Total** | | **69** |
