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

### Installation

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
kubectl apply -f deploy/deployment_nginx.yml

# lister les ressources
kubectl api-resources

# deployer un cluster IP service et le consulter puis le supprimer
kubectl expose deploy nginx-deployment --port=80 --type=ClusterIP
kubectl get service # ou kubectl get svc
kubectl delete service nginx-deployment

# déployer un cluster IP service configuré par yaml
kubectl apply -f svc/service_cluster_ip.yml

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
kubectl apply -f svc/service_node_port.yml

# deployer un load balancer service et le consulter puis le supprimer 
# - prérequis : requiert MetalLB pour simuler un loadbalancer
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.15.2/config/manifests/metallb-native.yaml
kubectl apply -f svc/metallb_config.yaml
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
kubectl apply -f svc/service_load_balancer.yml

# vérifier les replica set et les resizer dynamiquement
kubectl get replicaset # ou kubectl get rs
kubectl scale deploy nginx-deployment --replicas=1

# créer un replica set par yaml
kubectl create -f rs/replica_set.yml

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
kubectl apply -f pv/persistent_volume.yml
kubectl get pv

# creation d'un volume claim via yaml (pas de ligne de commande disponible) et listing
kubectl apply -f pvc/persistent_volume_claim.yml
kubectl get pvc

# creer un pod consommant ce volume claim
kubectl apply -f pvc/datascientest_pod.yml
kubectl get pod | grep pod-datascientest

# Ajustement du contenu du pod et démarrage d'un service associé
kubectl exec -it pod-datascientest -- bin/bash
# -- dans le shell du pod
echo "DATASCIENTEST" > /usr/share/nginx/html/index.html
cat /usr/share/nginx/html/index.html
# -- à l'extérieur du pod
kubectl apply -f pvc/datascientest_service.yml
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
kubectl apply -f deploy/deployement_vote_probes.yaml

# modification d'un deploiement avec effet immédiat (changement des conditions readyness/liveness pour mettre en erreur)
kubectl edit deploy vote

# verification des pods/replicaset/deployment
kubectl get deploy,rs,pods
kubectl describe pod vote-xxxx # ajuster avec le nom effectif du pod
```