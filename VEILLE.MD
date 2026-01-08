Choix des modèles et performances
1. Quels sont aujourd’hui les principaux modèles de détection d’objets
utilisés en vidéosurveillance (YOLOv8/YOLO11, Faster R-CNN, DETR, etc.)
et quels compromis font-ils entre vitesse d’inférence, précision (mAP)
et consommation de ressources pour un déploiement temps réel sur du
matériel limité ?

Answer:

yolo*
rtdetr*
Resnet 16 ?

-----


2. Quelles bonnes pratiques permettent d’évaluer rigoureusement un
modèle de détection d’objets sur des scènes de caméras fixes
(métriques mAP, précision/rappel par classe, IoU, analyse d’erreurs)
afin de garantir la fiabilité des statistiques de comptage dans des
conditions réelles (jour/nuit, pluie, foule dense) ?

-----

Données, annotation et robustesse
3. Comment sélectionner, combiner et annoter des datasets (Roboflow
Universe, datasets de trafic, webcams publiques) pour couvrir la
variété des contextes clients (places, ports, stations de ski) tout en contrôlant la taille du dataset pour un entraînement faisable sur
laptop/Colab ?

-----

4. Quelles stratégies d’augmentation de données et d’adaptation de
domaine (changement de météo, saison, angle de caméra, résolution)
sont pertinentes pour améliorer la robustesse d’un modèle de détection
appliqué à des flux webcams hétérogènes et évolutifs ?

-----

Architecture logicielle, DataOps et MLOps
5. Quelles architectures applicatives sont les plus adaptées pour relier
flux vidéo, service d’inférence, base de données temporelle et frontend
(Flask) : traitement batch périodique vs quasi temps réel, microservices,
file de messages, et quels impacts sur la scalabilité et la tolérance aux
pannes ?

-----

6. Quels outils et patterns MLOps (MLflow, CI/CD, versioning de modèles,
tests automatisés) sont recommandés pour assurer un cycle de vie
maîtrisé des modèles de détection d’objets, depuis l’expérimentation
jusqu’au déploiement reproductible en production (Docker, cloud/on
premise) ? Monitoring, dérive et réentraînement

-----

7. Quelles métriques et quels signaux (statistiques de distribution, taux
de détection, feedback utilisateur, anomalies sur les séries temporelles
de comptage) permettent de détecter efficacement la dérive de
données ou de concepts dans un système de vidéosurveillance
algorithmique, et comment déclencher un processus de
réentraînement pertinent ?

-----

8. Quelles approches existent pour intégrer le monitoring de modèles
(MLflow, dashboards, alertes) dans une application de vision par
ordinateur en production, afin de suivre à la fois la qualité des
prédictions et la santé opérationnelle du pipeline de traitement vidéo ? RGPD, AI Act et éthique

-----

9. Comment les cadres réglementaires RGPD et AI Act classifient-ils les
systèmes de vidéosurveillance algorithmique, quelles obligations en
découlent (base légale, DPIA, registres, transparence) et quelles
pratiques techniques (anonymisation, absence de stockage vidéo,
agrégation) sont recommandées pour rester conforme ?

-----

10. Quels sont les principaux enjeux éthiques liés au comptage
automatisé de personnes et de véhicules dans l’espace public (risque
de surveillance de masse, biais sur certaines populations, réutilisation
des données) et quelles mesures de conception (privacy by design, limitation des finalités, gouvernance des modèles) peuvent en limiter les risques ?