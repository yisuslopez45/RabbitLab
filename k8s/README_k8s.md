# Kubernetes (Minikube) deployment for RabbitLab

This guide explains how to run the RabbitLab stack on Minikube.

Prerequisites
- minikube installed
- kubectl configured for your minikube cluster
- docker (used by minikube's docker-env)

Steps

1) Start minikube (if not already running)

   minikube start

2) Point your shell to minikube's Docker daemon so images you build become available to the cluster

   eval $(minikube -p minikube docker-env)

3) Build images for all services inside minikube's Docker daemon

   docker build -t query-svc:latest ./query-svc
   docker build -t commercialinfo-svc:latest ./comercialinfo-scv
   docker build -t socialmedia-svc:latest ./socialmedia-svc
   docker build -t officialrecords-svc:latest ./officialrecords-svc
   docker build -t dashboard-svc:latest ./dashboard-svc

   ### Note: the manifests use imagePullPolicy: Never so the cluster will run the images built locally.

4) Apply manifests

   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/deployments-services.yaml

5) Wait for pods to be ready

   kubectl get pods -n rabbitlab -w

6) Access endpoints

   ### Query service (NodePort 30000)
   minikube service query-svc -n rabbitlab --url

   ### Dashboard (NodePort 30001)
   minikube service dashboard-svc -n rabbitlab --url

   ### RabbitMQ management UI (ClusterIP port 15672). You can port-forward:
   kubectl port-forward svc/rabbitmq 15672:15672 -n rabbitlab
   ### Then open http://localhost:15672 (guest/guest)

7) Test the flow

   ### Send a query to query-svc (replace <query-url> with the minikube service URL):
   curl -X POST http://127.0.0.1:33903/query -H "Content-Type: application/json" -d '{"name":"Juan Perez","id":"12345","phone":"555-1234"}'

   ### Then open Dashboard URL:
   ### http://<minikube-ip>:30001/viewresults  (or use the minikube service command)

Notes and caveats
- RabbitMQ persists data only in the container filesystem in this simple manifest (no PVC). For production you should add a PersistentVolumeClaim.
- Services are configured with `imagePullPolicy: Never` so you must build images in minikube's Docker environment (step 2).
- If you prefer to push images to a registry, change image names to include registry and set imagePullPolicy: IfNotPresent.
- The manifests run everything in the `rabbitlab` namespace.

Cleanup

   kubectl delete -f k8s/deployments-services.yaml -n rabbitlab
   kubectl delete -f k8s/namespace.yaml

Troubleshooting
- If a pod fails because it can't find the image, ensure you built images inside minikube's Docker daemon.
- Use `kubectl logs` to inspect logs from a failing pod.

!