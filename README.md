# Kubernetes-training
Training ground for practising kubernetes

## 1. Rappel des vérification d'usage de la VM (avec OS Ubuntu)

Non demandé mais par acquis de conscience si UV n'est encore présent...

### Mise à jour globale des paquets et rattrapage éventuel des installations manquantes

```bash
# Mise à jour de la liste des paquets
sudo apt update
# Récupère et corrige d'éventuels paquets manquants
sudo apt install --fix-missing
```

### Mise à jour python3

```bash
# (Ré)installation/verif de python3 (par sureté)
sudo apt install -y python3
```

### Mise à jour pip3 et pipx

```bash
# (Ré)installation/verif de pip3 et pipx (par sureté)
sudo apt-get install -y python3-pip
sudo apt install -y pipx
pipx ensurepath
source ~/.bashrc
```

### Installation UV (gestionnaire environnement virtuel)

```bash
# Lance l’installation de uv
pipx install uv
```

### Check final des composants nécessaires (ils doivent être tous présents)

```bash
# l'ensemble des composants de base est présent
python3 --version
pip3 --version
pipx --version
uv --version
```

## 2. K3s

### Installation (et arrêt/relance si besoin)

```bash
# download / install / check version
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.5+k3s1 sh -s - --write-kubeconfig-mode 644
kubectl version

# propagation de la config pour le user courant (puis l'activer via l'extension kubernetes)
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
kubectl cluster-info
kubectl get nodes -o wide

# arrêt (et relance)
sudo systemctl stop k3s
sudo systemctl start k3s
# sudo systemctl restart k3s
```

### Management des pods/services (/pod + /deploy + /svc)

```bash
### commands are like : kubectl [command] [TYPE] [NAME] [flags]
# command = [create/describe/get/delete/apply]
# type = [pod/service/deployment/node/replicaset/job/...]
k3s kubectl get nodes
# ...

# creaton d'une instance NGINX et listing des pods
kubectl run nginx --image=nginx
kubectl get pod

# execution d'un pod configuré par yaml et listing des pods
kubectl apply -f pod/wordpress.yml
kubectl get pod

# suppression de pod créés par les deux méthodes
kubectl delete pod nginx wordpress

# creation et suppression d'un déploiement de 10 replicas NGINX
kubectl create deployment nginx-deployment --image=nginx --replicas=10
kubectl delete deployment nginx-deployment

# execution d'un deploiement de pod configuré par yaml
kubectl apply -f deploy/deployment-nginx.yml

# lister les ressources
kubectl api-resources

# deployer un cluster IP service et le consulter puis le supprimer
kubectl expose deploy nginx-deployment --port=80 --type=ClusterIP
kubectl get service # ou kubectl get svc
kubectl delete service nginx-deployment

# déployer un cluster IP service configuré par yaml
kubectl apply -f svc/service-cluster-ip.yml

# lister les endpoints des services
kubectl get endpoints

# créer un pod permettant de faire du curl interactif (ou l'exécuter par suite)
kubectl run curl --image=curlimages/curl -i --tty -- sh
kubectl exec curl -i --tty -- sh

# deployer un node port service et le consulter puis le supprimer
kubectl expose deployment nginx-deployment --port=80 --type=NodePort
kubectl get service # ou kubectl get svc
kubectl delete service nginx-deployment

# déployer un node port service configuré par yaml
kubectl apply -f svc/service-node-port.yml

# deployer un load balancer service et le consulter puis le supprimer 
# - prérequis : requiert MetalLB pour simuler un loadbalancer
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.15.2/config/manifests/metallb-native.yaml
kubectl apply -f svc/metallb-config.yaml
# - les commandes service a proprement parler
kubectl expose deployment nginx-deployment --port=80 --type=LoadBalancer
kubectl get service # ou kubectl get svc
kubectl delete service nginx-deployment
```

```texte
[Client local] 
     ↓
http://10.0.0.241  (MetalLB IP)
     ↓
[NodePort (automatique)]
     ↓
[ClusterIP]
     ↓
[Pods nginx-deployment]
```

```bash
# déployer un load balancer service configuré par yaml
kubectl apply -f svc/service-load-balancer.yml

# vérifier les replica set et les resizer dynamiquement
kubectl get replicaset # ou kubectl get rs
kubectl scale deploy nginx-deployment --replicas=1

# créer un replica set par yaml
kubectl create -f rs/replica-set.yml

# visualiser les composant d'un replica set
kubectl describe replicaset httpd-replicaset # ou kubectl describe rs httpd-replicaset

# lister et créer des namespace et afficher leur ressources specifiques
kubectl get namespace # ou kubectl get ns
kubectl create namespace datascientest
kubectl get all -n datascientest

# exemple d'utilisation du namespace et récupération multi cible
kubectl create deployment wordpress --image=wordpress --replicas=3 --namespace datascientest
kubectl get pod,deploy -n datascientest

# suppression (/!\ en cascade) d'un namespace et de tout ses composants
kubectl delete namespace datascientest
```

### Management des persistent volumes et claims (/pv + /pvc)

```bash
# verifier les classes de stockage
kubectl get storageclass

# creation d'un volume via yaml (pas de ligne de commande disponible) et listing
kubectl apply -f pv/persistent-volume.yml
kubectl get pv

# creation d'un volume claim via yaml (pas de ligne de commande disponible) et listing
kubectl apply -f pvc/persistent-volume-claim.yml
kubectl get pvc

# creer un pod consommant ce volume claim
kubectl apply -f pvc/datascientest-pod.yml
kubectl get pod | grep pod-datascientest

# Ajustement du contenu du pod et démarrage d'un service associé
kubectl exec -it pod-datascientest -- bin/bash
# -- dans le shell du pod
echo "DATASCIENTEST" > /usr/share/nginx/html/index.html
cat /usr/share/nginx/html/index.html
# -- à l'extérieur du pod
kubectl apply -f pvc/datascientest-service.yml
```

### Management des secrets et config map (/secret + /cm)

```bash
# conversion d'un secret en base 64
echo -n 'Datascientest2023@!!' | base64 # le mot de passe root sera "Datascientest2023@!!"

# creation d'un secret via yaml et listing
kubectl apply -f secret/secret.yml
kubectl get secret
kubectl describe secret mariadb-root-password

# édition d'un secret
kubectl edit secret mariadb-root-password

# recuperation et decodage d'un secret
kubectl get secret mariadb-root-password -o jsonpath='{.data.password}' | base64 --decode

# creation d'un secret via ligne de commande puis récupération
kubectl create secret generic mariadb-user --from-literal=MARIADB_USER=datascientestuser --from-literal=MARIADB_PASSWORD=DatascientestMariadb@..
kubectl get secret mariadb-user -o jsonpath='{.data.MARIADB_USER}' | base64 --decode
kubectl get secret mariadb-user -o jsonpath='{.data.MARIADB_PASSWORD}' | base64 --decode

# creation d'une config map par ligne de commande et listing
kubectl create configmap cm-mariadb --from-file=cm/mysqld.cnf
kubectl describe cm cm-mariadb
kubectl delete cm cm-mariadb

# edition puis récupération de la conf
kubectl edit configmap cm-mariadb
kubectl get configmap cm-mariadb -o jsonpath='{.data.mysqld\.cnf}' # le . doit être échapé en \.
# alternative avec go-template
kubectl get configmap cm-mariadb -o go-template='{{ index .data "mysqld.cnf" }}'

# creation (ou réapplication) d'un statefulset mariadb utilisant les secret par reference de variable d'env/fichier de configmap
kubectl create -f cm/statefulset.yml --save-config

# reapplication (suite a modif) du statefulset mariadb
kubectl apply -f cm/statefulset.yml
# redémarrage d'un statefulset si changement (cas replica == 1)
kubectl delete pod mariadb-0
# (alternatif propre) redémarrage d'un statefulset si changement (cas replica > 1)
kubectl rollout restart statefulset mariadb
kubectl rollout status statefulset mariadb

# afficher les variable d'env d'un pod
kubectl exec -it mariadb-0 -- env | grep MARIADB

# vérifier les bind de config 
kubectl exec -it mariadb-0 -- ls -latR /etc/mysql/conf.d

# execution d'un bash dans l'instance pod mariadb et affichage des BDD (Cf doc mariadb)
kubectl exec -it mariadb-0 -- /bin/sh
mysql -uroot -p${MARIADB_ROOT_PASSWORD} -e 'show databases;'
mysql -uroot -p${MARIADB_ROOT_PASSWORD} -e "SHOW VARIABLES LIKE 'max_allowed_packet';"
```

### Management du healthcheck (/deploy)

```bash
# verification healthcheck par probes (liveness / readyness)
kubectl apply -f deploy/deployement-vote-probes.yaml

# modification d'un deploiement avec effet immédiat (changement des conditions readyness/liveness pour mettre en erreur)
kubectl edit deploy vote

# verification des pods/replicaset/deployment
kubectl get deploy,rs,pods
kubectl describe pod vote-xxxx # ajuster avec le nom effectif du pod
```

### Exercice de déploiement API (/exo_api)

```bash
# deployement d'une API fake de prediction sentiment et verification
# NB : apply = create or update
kubectl apply -f exo_api/my-api.yml
kubectl get pods,rs,deploy

# lancement d'un service sur ce deployment
# NB : apply = create or update
kubectl apply -f exo_api/my-service.yml
kubectl get svc
# NB : get plus global sur un namespace en particulier (default ici)
kubectl get all -n default

# creation d'une configmap et application aux pods utilisant ce ENVIRONMENT_TYPE
kubectl create configmap my-config-map --from-literal ENVIRONMENT_TYPE=production
kubectl apply -f exo_api/my-api.yml

# modification de la valeur ENVIRONMENT_TYPE de la config map et rollout (avec verif)
kubectl edit cm my-config-map
kubectl rollout restart deployment sentiment-analysis-api
kubectl rollout status deploy sentiment-analysis-api

# ajout d'un secret alimentant ENVIRONMENT_TYPE lors du deployment et rollout (avec verif)
kubectl create secret generic my-secret --from-literal my-key=my-value
kubectl apply -f exo_api/my-api.yml
kubectl rollout restart deployment sentiment-analysis-api
kubectl rollout status deploy sentiment-analysis-api
```

## 3. Helm

### Installation

```bash
# download / install / check version
sudo apt-get install -y curl gpg apt-transport-https
curl -fsSL https://packages.buildkite.com/helm-linux/helm-debian/gpgkey \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get update
sudo apt-get install -y helm
helm version

# listing des ressources récupérées localement
helm list
```

### Configuration

```bash
# ajuster le fichier ~/.bashrc avec
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo "helm version: $(helm version)"
```

### Exemple avec airflow (/airflow)

```bash
# recuperation du chart airflow et verification
helm repo add apache-airflow https://airflow.apache.org
helm repo list
# (optionnel nettoyage)
helm repo remove apache-airflow 

# Recupérer un chart spécifique et ses valeurs par défaut
helm template apache-airflow/airflow --version 1.16.0 --set airflow.image.tag=2.10.5 > templates.yaml
helm show values apache-airflow/airflow --version 1.16.0 > values.yaml

# initier un namespace k8s et y basculer à ce contexte par defaut (et afficher les contextes)
kubectl create namespace airflow
# basculer sur le contexte namespace airflow
sudo kubectl config set-context --current --namespace=airflow
kubectl config get-contexts

# deployment airflow et verification
helm upgrade --install airflow apache-airflow/airflow \
  --namespace airflow \
  --version 1.16.0 \
  --set postgresql.enabled=true \
  --set postgresql.image.registry=docker.io \
  --set postgresql.image.repository=bitnamilegacy/postgresql \
  --set postgresql.image.tag=16.1.0-debian-11-r15
kubectl -n airflow describe pod airflow-postgresql-0 | sed -n '/Events/,$p'
helm list
# (optionnel nettoyage) rollback une installation
helm -n airflow uninstall airflow
# (1) Forcer suppression du(des) pod(s) bloqué(s)
kubectl get pods -A | grep airflow # donne la liste pour laquelle executer la commande suivante
kubectl -n airflow delete pod airflow-redis-0 --grace-period=0 --force --ignore-not-found
# (2) Supprimer namespace (ou finalizers)
kubectl delete ns airflow
# (3) Nettoyer runtime
sudo crictl rm --all
sudo crictl rmi --prune
sudo systemctl restart k3s

# verification du service et activation d'un forward du port service -> machine virtuelle
kubectl get svc
kubectl port-forward svc/airflow-webserver --address 0.0.0.0 8080:8080

# creer les PV et PVC pour les dags et logs
mkdir -p dags
kubectl create -f airflow-local-dags-folder-pvc.yaml
kubectl create -f airflow-local-dags-folder-pv.yaml
mkdir -p logs
kubectl create -f airflow-local-logs-folder-pvc.yaml
kubectl create -f airflow-local-logs-folder-pv.yaml

# upgrade de la configuration en surchargeant avec un fichier de config yaml additionnel (my-values.yaml)
# necessite au préalable d'avoir arrêté en cascade les statefulset qui sont immuables
kubectl delete sts airflow-triggerer -n airflow --cascade=orphan
kubectl delete sts airflow-worker -n airflow --cascade=orphan

helm upgrade --install airflow apache-airflow/airflow \
  --namespace airflow \
  --version 1.16.0 \
  --set postgresql.enabled=true \
  --set postgresql.image.registry=docker.io \
  --set postgresql.image.repository=bitnamilegacy/postgresql \
  --set postgresql.image.tag=16.1.0-debian-11-r15 \
  -f my-values.yaml

# verification de commande dans un pod (exemple listing d'un fichier a un emplacement souhaité via PV)
kubectl exec airflow-triggerer-0 -- ls dags # une commande unique et sortie
kubectl exec -it airflow-triggerer-0 -- bash # un bash en interactif
kubectl exec -it airflow-webserver-6fd8d648b5-zkqmw -- bash
kubectl exec -it airflow-scheduler-7896d679dc-hkqzz -- bash
# pip show apache-airflow-providers-postgres

# verification en continu des pods
kubectl get pod -w

# login sur docker (si credentials deja OK)
docker login
# login sur docker si credentials pas encore connus 
docker login -u <user> -p <token_pwd>

# creation d'une image docker à pousser sur docker hub (afin d'être visible par kubernetes)
# NB : se positionner dans airflow/order/docker/prod/python_transform -> ajuster le chemin dans la commande
cd ~/github-kubernetes/kubernetes-training/airflow/order/docker/prod/python_transform
docker build -t python-transform .
# tag et push de l'image sur docker hub
# NB : ajuster le nom d'utilisateur dans les deux commandes
docker tag python-transform zheddhe/order-python-transform
docker push zheddhe/order-python-transform
# execution de test de cette image avec initialisation des fichiers de test et visualisation logs
cd ~/github-kubernetes/kubernetes-training/airflow/order/
cp data/orders/2024-05-09.json data/to_ingest/bronze/orders.json
kubectl create -f python-transform-job.yaml
kubectl get pod -w
# NB : remplacer par le nom exact du pod
kubectl logs python-transform-dfngv -c python-transform

# creation d'une image docker à pousser sur docker hub (afin d'être visible par kubernetes)
# NB : se positionner dans airflow/order/docker/prod/python_transform -> ajuster le chemin dans la commande
cd ~/github-kubernetes/kubernetes-training/airflow/order/docker/prod/python_load
docker build -t python-load .
# tag et push de l'image sur docker hub
# NB : ajuster le nom d'utilisateur dans les deux commandes
docker tag python-load zheddhe/order-python-load
docker push zheddhe/order-python-load
# execution de test de cette image avec initialisation des fichiers de test et visualisation logs
cd ~/github-kubernetes/kubernetes-training/airflow/order/
kubectl create -f python-load-job.yaml
kubectl get pod -w
# NB : remplacer par le nom exact du pod
kubectl logs python-load-kcc9d -c python-load
# deployer les secrets et recréer le pod
kubectl create -f sql-conn-secret.yaml
kubectl delete job python-load
kubectl create -f python-load-job.yaml

# creation des PV/PVC
kubectl create -f order-data-folder-pv.yaml
kubectl create -f order-data-folder-pvc.yaml

# affichage dans le pod postgresql
kubectl exec -it airflow-postgresql-0 -- psql -U postgres postgres
```

## 3. Skopeo

### Installation

```bash
# mise en contexte de la version ubuntu et listing des librairies associées
. /etc/os-release
echo "deb [signed-by=/usr/share/keyrings/containers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" \
  | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list

# recupération des librairies a jour via release key
curl -fsSL https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/xUbuntu_${VERSION_ID}/Release.key \
  | gpg --dearmor | sudo tee /usr/share/keyrings/containers-archive-keyring.gpg > /dev/null

# apt update et installation skopeo
sudo apt update
sudo apt install --reinstall skopeo -y
```

### Utilisation

```bash
# verifier une version dans un repo public sans autentification
skopeo inspect docker://docker.io/bitnami/postgresql:latest

# recuperer la liste des tag dans un repo sans autentification
skopeo list-tags docker://docker.io/bitnami/postgresql | jq -r '.Tags[]'
```
