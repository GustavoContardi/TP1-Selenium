# TP1-Selenium
TP1 Selenium

## Hit #7 — Kubernetes

### Prerrequisitos
- k3s o k3d instalado y cluster activo (ver TP 0)
- Imagen Docker buildeada: `docker build -t ml-scraper:latest .`

### Importar la imagen al cluster

**k3s nativo:**
```bash
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar
rm /tmp/ml-scraper.tar
```

**k3d:**
```bash
k3d image import ml-scraper:latest -c <nombre-del-cluster>
```

### Aplicar todos los manifests
```bash
kubectl apply -f hit7/k8s/
```

### Disparar el Job one-off y seguir los logs
```bash
kubectl get jobs
kubectl wait --for=condition=complete job/scraper-once --timeout=600s
kubectl logs -l job-type=one-off -f
```

### Verificar los JSON generados en el PVC
```bash
kubectl exec -it $(kubectl get pod -l job-type=one-off -o jsonpath='{.items[0].metadata.name}') -- ls /app/output
```

### Verificar el CronJob
```bash
kubectl get cronjobs
kubectl get jobs --watch
```

### Limpiar todos los recursos
```bash
kubectl delete -f hit7/k8s/
```
