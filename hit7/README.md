# Hit #7 — Despliegue con Docker y Kubernetes

Este Hit se encarga de containerizar el scraper y prepararlo para ser desplegado en un cluster de Kubernetes. Se definen dos modalidades de ejecución mediante manifiestos: un `Job` para una ejecución única (one-off) y un `CronJob` para ejecuciones periódicas automatizadas.

## Requisitos previos

- Docker instalado en el sistema.
- Un cluster local de Kubernetes (como k3s o k3d) funcional y levantado.
- El binario `kubectl` configurado para apuntar a tu cluster.

## Construcción de la imagen (Build)

Desde la raíz del proyecto (`TP1-Selenium/`), se debe construir la imagen de Docker usando el `Dockerfile` del Hit 7:

```bash
docker build -t ml-scraper:latest hit7/
```

## Importar la imagen al cluster

Dependiendo de cómo tengas levantado tu entorno local (k3s directamente sobre tu host o k3d), es necesario importar la imagen generada al registro interno del cluster para que los Pods puedan utilizarla.

### Opción A: Usando k3s nativo
Primero, exporta la imagen a un `.tar` y luego impórtala a k3s:
```bash
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar
rm /tmp/ml-scraper.tar
```

### Opción B: Usando k3d
Importa la imagen directamente apuntando a tu cluster:
```bash
k3d image import ml-scraper:latest -c <nombre-del-cluster>
```

## Despliegue de los manifiestos

Una vez la imagen está disponible en el cluster, aplicamos todos los objetos definidos en la carpeta `k8s/`:

```bash
kubectl apply -f hit7/k8s/
```

Esto desplegará tanto el **Job** como el **CronJob**.

## Monitorear la ejecución

### Verificar el Job one-off

El Job se ejecutará inmediatamente para una prueba única. Para obtener los logs y ver la salida del scraper:

```bash
# Consultar los pods asociados a este Job
kubectl get pods -l job-type=one-off

# Seguir el log de ejecución del pod en tiempo real
kubectl logs -l job-type=one-off -f
```

### Verificar el CronJob

El CronJob está definido para correr en un ciclo (revisar la expresión cron en los archivos `.yaml`). Puedes consultar su estado con:

```bash
kubectl get cronjobs
kubectl get jobs --watch
```

## Limpieza

Cuando termines las pruebas, puedes borrar todos los objetos creados por este Hit en el cluster:

```bash
kubectl delete -f hit7/k8s/
```
