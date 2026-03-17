# objet : note de cadrage réglementaire concernant le projet de comptage de piétons par vision artificielle

## introduction
Dans le cadre de notre projet de déploiement de webcams sur les places publiques pour le comptage de piétons, nous avons analysé les implications juridiques liées au RGPD et au futur IA Act européen. La réussite de ce projet repose sur notre capacité à transformer une captation vidéo en donnée statistique anonyme sans porter atteinte aux libertés individuelles.

## conformité au RGPD

### La protection par la conception
Le comptage de personnes dans l'espace public implique la captation de données à caractère personnel, car les individus y sont potentiellement identifiables. Pour garantir notre conformité, nous préconisons les mesures suivantes :

### Anonymisation immédiate et irréversible
Nous devons privilégier une architecture de type "edge computing". Cela signifie que l'image est traitée localement par la caméra et immédiatement supprimée. Seule la donnée numérique (le nombre de personnes) est transmise à nos serveurs.

### Réalisation d'une AIPD
Nous engagerons une analyse d'impact sur la protection des données. Ce document est obligatoire dès lors qu'il existe une surveillance systématique à grande échelle d'une zone accessible au public.

### Transparence et information
Nous mettrons en place une signalétique claire sur chaque site. Nous devons informer les citoyens de la finalité du traitement, de l'absence d'enregistrement d'images et de leurs droits d'accès via un contact dédié.

## conformité à l'IA Act

### Gestion des risques
Le nouveau règlement européen sur l'intelligence artificielle impose des obligations strictes selon le niveau de risque du système.

### Classification du système
Notre solution de comptage est classée comme un système d'IA à risque limité. À l'inverse des systèmes de reconnaissance biométrique (considérés comme à haut risque ou interdits), notre algorithme doit se limiter à la détection d'objets (formes humaines) sans identification.

### Oligations de transparence
Nous sommes tenus d'informer explicitement les usagers qu'ils sont exposés à un système d'IA. Cette mention sera intégrée à notre communication publique.

### Gouvernance des données
Nous veillerons à ce que les jeux de données utilisés pour l'entraînement de nos modèles soient exempts de biais, afin d'assurer une précision de comptage équitable pour tous les types de profils.

### Préconisations de mise en œuvre
Pour sécuriser le projet, nous recommandons le plan d'action suivant :

- sélection du matériel : nous choisirons des capteurs dont la résolution est optimisée pour le comptage mais insuffisante pour la reconnaissance faciale à distance.
- limitation stricte de la finalité : nous nous interdisons contractuellement et techniquement tout usage de ces caméras à des fins de vidéo-verbalisation ou de surveillance comportementale.
- audit de sécurité : nous réaliserons un test d'intrusion sur le flux de données pour nous assurer qu'aucun accès tiers ne permette de détourner le flux vidéo brut.

# Conclusion
En adoptant une approche de "privacy by design", nous minimisons les risques juridiques tout en garantissant l'acceptabilité sociale du projet. Nous restons à votre disposition pour détailler le budget nécessaire à la mise en conformité de ces dispositifs.