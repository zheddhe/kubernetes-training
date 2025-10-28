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
kubectl apply -f deploy/deployment.yml

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

### Management des volumes (/pv)

```bash
# verifier les classes de stockage
kubectl get storageclass

# creation d'un volume via yaml (pas de ligne de commande disponible) et listing
kubectl apply -f pv/persistent_volume.yml
kubectl get pv

# creation d'un volume claim via yaml (pas de ligne de commande disponible) et listing
kubectl apply -f pv/persistent_volume_claim.yml
kubectl get pvc

# creer un pod consommant ce volume claim
kubectl apply -f pv/datascientest_pod.yml
kubectl get pod | grep pod-datascientest

# Ajustement du contenu du pod et démarrage d'un service associé
kubectl exec -it pod-datascientest -- bin/bash
# -- dans le shell du pod
echo "DATASCIENTEST" > /usr/share/nginx/html/index.html
cat /usr/share/nginx/html/index.html
# -- à l'extérieur du pod
kubectl apply -f pv/datascientest_service.yml
```

