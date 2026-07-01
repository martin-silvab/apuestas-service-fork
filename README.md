# VidalCasino 2.0 - Apuestas Service

Este repositorio contiene el microservicio **apuestas-service** del proyecto VidalCasino 2.0, desarrollado para la evaluación EP3 de Introducción a Herramientas DevOps. Este servicio gestiona eventos deportivos, apuestas realizadas por usuarios y operaciones asociadas a apuestas deportivas.

## Descripción general

`apuestas-service` permite consultar eventos deportivos, realizar apuestas y registrar apuestas asociadas a los usuarios del sistema. Este microservicio se ejecuta dentro del clúster de Kubernetes en Amazon EKS y se mantiene como servicio interno mediante `ClusterIP`.

El frontend consume este servicio mediante rutas `/api/apuestas`, sin exponer el microservicio directamente a Internet.

## Arquitectura del sistema

El sistema VidalCasino está compuesto por:

- **casino-frontend:** interfaz web pública mediante LoadBalancer.
- **casino-backend:** backend principal interno.
- **bonos-service:** microservicio de bonos.
- **apuestas-service:** microservicio de apuestas deportivas.
- **estadisticas-service:** microservicio de estadísticas.
- **postgres:** base de datos interna.

## Tecnologías utilizadas

- Python
- FastAPI
- PostgreSQL
- Docker
- Kubernetes
- Amazon EKS
- Amazon ECR
- GitHub Actions
- Horizontal Pod Autoscaler
- AWS Academy Learner Lab

## Endpoints de salud

El servicio incorpora sondas de salud para Kubernetes:

```txt
/livez
/readyz
/livez: verifica que el contenedor se encuentra vivo.
/readyz: verifica que el servicio puede operar correctamente y conectarse a la base de datos.
Despliegue en Kubernetes

Los manifiestos se encuentran en:

k8s/

Archivos principales:

k8s/deployment.yaml
k8s/service.yaml
k8s/hpa.yaml

El servicio se despliega con 2 réplicas y se expone internamente mediante un Service de tipo ClusterIP en el puerto 8005.

También cuenta con un HorizontalPodAutoscaler que escala el servicio según uso de CPU.

CI/CD

El despliegue automático se encuentra definido en:

.github/workflows/deploy.yml

El workflow se ejecuta al realizar un push sobre la rama deploy.

El pipeline realiza:

Descarga del código.
Configuración de credenciales de AWS Academy.
Login en Amazon ECR.
Construcción de imagen Docker.
Publicación en ECR con tags latest, v1.0.1 y SHA del commit.
Conexión con Amazon EKS.
Actualización del Deployment.
Verificación del rollout y estado de pods.
Comandos de verificación
kubectl get deployment apuestas-service
kubectl get svc apuestas-service
kubectl get hpa apuestas-service-hpa
kubectl get pods -l app=apuestas-service -o wide
kubectl describe deployment apuestas-service
Estado esperado
Deployment disponible con 2 réplicas.
Service interno tipo ClusterIP.
HPA activo con objetivo de CPU.
Pods en estado Running.
Imagen desplegada desde Amazon ECR.
CI/CD exitoso en GitHub Actions.