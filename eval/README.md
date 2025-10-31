# Kubernetes-eval
Exam context for datascientest kubernetes

## 1. Prerequisites

```bash
# creation des répertoires
mkdir -p eval/data eval/fastapi eval/mysql eval/test
# creation du namespace et bascule sur ce contexte par défaut
kubectl create namespace eval
sudo kubectl config set-context --current --namespace=eval
```

## 2. MySQL

```bash
# creation et execution des YAML séparément dans eval/mysql
# - secret root : mysql-root-password.yaml
kubectl apply -f mysql/mysql-root-password.yaml
# - secret user : mysql-user.yaml
kubectl apply -f mysql/mysql-user.yaml
# - persistent volume : mysql-local-data-folder-pv.yaml (correspondant au PVC attendu par le statefulset)
kubectl apply -f mysql/mysql-local-data-folder-pv.yaml
# - statefulset complété : mysql-statefulset.yaml
kubectl apply -f mysql/mysql-statefulset.yaml
# - service : mysql-service.yaml
kubectl apply -f mysql/mysql-service.yaml
```

## 2. FastAPI

Ces étapes sont effectuée dans eval/test comme demandé dans l'énoncé mais il aurait été probablement plus judicieux 
de faire effectuer cette étape depuis eval/fastapi ?

```bash
# récupération des sources externes depuis dans eval/test (en supprimant le premier niveau de sous répertoire de l'archive)
wget -qO- https://dst-de.s3.eu-west-3.amazonaws.com/kubernetes_fr/eval/k8s-eval-fastapi.tar | tar -xv -C ./test --strip-components=1

# creation de l'image et push sur docker hub (en latest par défaut)
docker login
docker build -t k8s-dst-eval-fastapi ./test
docker tag k8s-dst-eval-fastapi zheddhe/k8s-dst-eval-fastapi
docker push zheddhe/k8s-dst-eval-fastapi

# dev itératif du contenu de main.py avec un pod simple bindé a /test/app
kubectl apply -f test/fastapi-pod.yaml
kubectl logs -f fastapi # pour visualisation des logs d'executions du pod fastapi

# recreation de l'image finale avec le tag
kubectl delete pod/fastapi
docker build -t k8s-dst-eval-fastapi ./test
docker tag k8s-dst-eval-fastapi zheddhe/k8s-dst-eval-fastapi
docker push zheddhe/k8s-dst-eval-fastapi

# creation et execution des yaml dans eval/fastapi
# - deployment d'un replicat set de 3 pods fastapi : fastapi-deployment.yaml
kubectl apply -f fastapi/fastapi-deployment.yaml
# - service avec node port 30000 : fastapi-service.yaml
kubectl apply -f fastapi/fastapi-service.yaml
```

## Commentaires généraux

Ici le paradigme utilisé est celui de kubernetes qui exposer de manière normée le host et le port des services (en CAPITAL_SNAKE_CASE) donc pour le service "mysql" qu'on a défini, cela donne
>- MYSQL_SERVICE_HOST
>- MYSQL_SERVICE_PORT

On aurait aussi pu utiliser en alternative une configMap additionnelle avec la cartographie de nos services (mysql seulement ici) et la résolution DNS dans son namespace "eval" du coup il aurait fallu passer ces variables spécifiques en tant que variable d'environnement additionnelles sur les deployments/pods et les traiter dans le main.py de l'image fastapi en lieu et place de celles de kubernetes (après revue il semble que les deux stratégies peuvent se valoir en production dans les entreprises)
```bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: eval
data:
  MYSQL_HOST: "mysql"
  MYSQL_PORT: "3306"
```