# 14848_cloud_infra_proj_sonarqube_sonarscanner

## How to build docker image
- Run `docker build --no-cache --progress=plain -t YOUR_DOCKER_ID/14848_proj_sonar:ubuntu . ` and push the image to DockerHub.

## Deploy docker image to Google Cloud Platform Kubernetes Cluster
- Open Cloud Shell on GCP and clone the repository:
```
git clone https://github.com/shihsunl/14848_cloud_infra_proj_sonarqube_sonarscanner.git
```
- Modify docker image in `resource-manifests/sonarqube_deployment.yaml`.
- Execute 2 yaml file in resource-manifests folder.
```
cd 14848_cloud_infra_proj_sonarqube_sonarscanner
kubectl apply -f sonarqube_deployment.yaml 
kubectl create -f service-sonarqube.yaml
```
- Then, you can check Workloads and Service & Ingress
![workloads](screenshot/workloads.png)
![service](screenshot/service.png)

- Next, you can access to the Service Website and select the sonarqube and sonarscanner service. Please check: `https://github.com/shihsunl/14848_cloud_infra_proj_driver`
