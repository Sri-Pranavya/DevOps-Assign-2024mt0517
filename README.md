# DevOps for Cloud Assignment – 2024MT03517

*Student Name:* M.B. Sri Pranavya
*Roll Number:* 2024MT03517
*Course:* DevOps for Cloud

---

## 🧩 Task 1 – Develop the Flask Application

*Objective:*
Create a simple Flask API returning application info and metrics.

*Key Files:*
main.py

*Steps Done:*

1. Created a Flask app exposing two endpoints:

   * /get_info → returns JSON with APP_TITLE, APP_VERSION, and pod name.
   * /metrics → exposes Prometheus metrics.
2. Added environment variables for configuration.
3. Integrated prometheus_client to export:

   * get_info_requests_total
   * app_cpu_usage_percent
   * app_memory_usage_percent

*Verification:*


curl http://localhost:8000/get_info
→ {"APP_TITLE":"Devops for Cloud Assignment","APP_VERSION":"1.0","served_by":"<pod-name>"}


*Screenshots to Include:*

* Flask app folder structure
* main.py code snippet
* Terminal output of /get_info response

---

## 🐳 Task 2 – Dockerization

*Objective:*
Containerize the Flask app and push the image to ECR.

*Steps Done:*

1. Wrote Dockerfile:

   dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   
2. Built and tagged image:

   bash
   docker build -t img-2024mt03517 .
   docker tag img-2024mt03517:latest 390685732640.dkr.ecr.ap-south-1.amazonaws.com/img-2024mt03517:latest
   
3. Pushed to AWS ECR.

*Verification:*
aws ecr describe-images --repository-name img-2024mt03517

*Screenshots to Include:*

* Dockerfile content
* Successful docker build and docker push output
* ECR console showing uploaded image

---

## 🧱 Task 3 – Run the Docker Container

*Objective:*
Run container locally and confirm app access.

*Steps Done:*

bash
docker run -d -p 8000:8000 --name cnr-2024mt03517 img-2024mt03517:latest
docker ps


*Verification:*
Access http://localhost:8000/get_info in browser or via curl.

*Screenshots to Include:*

* Output of docker ps
* Browser window showing /get_info JSON response

---

## ☸️ Task 4 – Kubernetes Deployment

*Objective:*
Deploy Flask app on EKS with 2 replicas and ConfigMap.

*Files:*

* config-2024mt03517.yaml
* dep-2024mt03517.yaml

*Key Steps:*

1. Created ConfigMap:

   yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: config-2024mt03517
   data:
     APP_VERSION: "1.0-k8s"
     APP_TITLE: "Devops App on Kubernetes"
   
2. Created Deployment:

   yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: dep-2024mt03517
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: my-flask-app
     template:
       metadata:
         labels:
           app: my-flask-app
         annotations:
           prometheus.io/scrape: "true"
           prometheus.io/path: "/metrics"
           prometheus.io/port: "8000"
       spec:
         containers:
           - name: flask-app
             image: 390685732640.dkr.ecr.ap-south-1.amazonaws.com/img-2024mt03517:latest
             ports:
               - containerPort: 8000
             envFrom:
               - configMapRef:
                   name: config-2024mt03517
   
3. Applied both files:

   bash
   kubectl apply -f config-2024mt03517.yaml
   kubectl apply -f dep-2024mt03517.yaml
   

*Verification:*
kubectl get pods -o wide → shows 2 running replicas.

*Screenshots to Include:*

* YAML file contents
* Pod list showing two replicas
* kubectl describe pod confirming environment vars

---

## 🌐 Task 5 – Load Balancer & Request Distribution

*Objective:*
Expose the app externally and verify load balancing.

*File:*
svc-2024mt03517.yaml

*Steps Done:*

1. Initially tried LoadBalancer (stayed <pending>).
2. Switched to NodePort type for external access.

yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-2024mt03517
spec:
  type: NodePort
  selector:
    app: my-flask-app
  ports:
    - port: 80
      targetPort: 8000
      nodePort: 30080


*Verification:*
Used node external IP:
curl http://3.110.173.100:30080/get_info → successful response.

*Load Balancing Check:*

bash
for i in {1..10}; do curl -s http://3.110.173.100:30080/get_info; done
kubectl logs -l app=my-flask-app


Logs alternated between both pods confirming round-robin behavior.

*Screenshots to Include:*

* Service YAML content
* kubectl get svc output
* Successful curl responses from both replicas
* Pod logs showing alternating “served_by” values

---

## 📊 Task 6 – Prometheus Metrics Collection

*Objective:*
Set up Prometheus to scrape and visualize Flask app metrics.

*Steps Done:*

1. Installed Prometheus:

   bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/prometheus -n prometheus \
     --create-namespace \
     --set server.persistentVolume.enabled=false \
     --set alertmanager.persistentVolume.enabled=false
   

2. Verified pods:

   
   kubectl get pods -n prometheus
   

3. Exposed UI:

   bash
   kubectl edit svc -n prometheus prometheus-server
   # changed type: NodePort
   kubectl get svc -n prometheus prometheus-server
   

4. Accessed Prometheus via
   http://3.110.173.100:<nodePort>/

5. Verified Flask app targets (Status → Targets) were *UP*.

6. Ran queries:

   * sum by (pod_name) (get_info_requests_total)
   * avg by (pod_name) (app_cpu_usage_percent)
   * avg by (pod_name) (app_memory_usage_percent)

7. Generated requests to update metrics:

   bash
   for i in {1..20}; do curl -s http://3.110.173.100:30080/get_info >/dev/null; done
   

*Verification:*

* Metrics updated per replica.
* Prometheus graphs displayed request count, CPU %, and memory %.

*Screenshots to Include:*

1. /metrics output from curl
2. Prometheus “Targets” page showing both pods UP
3. Graph/table for each metric (get_info_requests_total, app_cpu_usage_percent, app_memory_usage_percent)
4. Pod logs showing balanced requests

*Challenges Fixed:*

* Prometheus pods pending due to PVC → reinstalled without persistent volumes.
* Added scrape annotations to Deployment for auto-discovery.

---

## ✅ Final Outcome

* Application fully deployed on AWS EKS.
* LoadBalancer/NodePort provides external access.
* Prometheus successfully scrapes and visualizes per-replica metrics.
* All tasks 1–6 completed successfully.

---

*Useful Commands Summary*

bash
kubectl get pods -o wide
kubectl get svc
kubectl logs -l app=my-flask-app
kubectl port-forward -n prometheus svc/prometheus-server 9090:80


---

*End of README*
