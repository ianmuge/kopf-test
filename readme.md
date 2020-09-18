
# KOPF test
Deployment was done on on GKE

First to configure the project ID, we run the commands below on gcloud.
```
export PROJECT_ID="$(gcloud config get-value project -q)"
gcloud auth configure-docker
```
We build, tag and push the image to the project gcr private repository
```
docker build --no-cache -t operator:latest ./operator
docker tag operator:latest "gcr.io/${PROJECT_ID}/operator:latest"
docker push "gcr.io/${PROJECT_ID}/operator:latest"
```
We deploy the crd, setup rbac and operator; substituting the project_id env variable
```
kubectl apply -f setup/crd.yml
kubectl apply -f setup/rbac.yml
envsubst < setup/operator.yml | kubectl apply -f -
```
Finally, we deploy the mysql and mongoDB services and pods
```
kubectl apply -f deploy/
```