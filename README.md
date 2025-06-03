# 🧰 supertouf/shelly

Ce dépôt rassemble une collection de scripts et d'outils pour faciliter l'intégration de divers appareils domotiques (Shelly, Deye, Netatmo, etc.) avec des systèmes de gestion comme Home Assistant, en utilisant des protocoles tels que MQTT.

## 📁 Structure du projet

- **`shelly/`** : Scripts pour les appareils Shelly, y compris des intégrations spécifiques comme pour les onduleurs Eaton UPS.
- **`deye-mqtt/`** : Scripts Python pour interagir avec les onduleurs Deye via TCP et publier les données sur MQTT.
- **`netatmo-mqtt/`** : Scripts pour récupérer les données des capteurs Netatmo et les publier sur MQTT.
- **`mqtt-docker/`** : Configuration Docker Compose pour déployer rapidement un serveur MQTT.
- **`ajax-sia/`** : Scripts pour intégrer des systèmes d'alarme Ajax via le protocole SIA.
- **`pysolarman/`** : Scripts pour interagir avec les onduleurs Solarman.
- **`docker-compose.yml`** : Fichier de configuration pour orchestrer les services Docker nécessaires.

## 🚀 Démarrage rapide

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/supertouf/shelly.git
   cd shelly
   ```

2. **Configurer le serveur MQTT avec Docker :**

   ```bash
   cd mqtt-docker
   docker-compose up -d
   ```

3. **Configurer les scripts selon vos besoins :**

   - Modifier les fichiers de configuration dans les répertoires correspondants (`deye-mqtt/`, `netatmo-mqtt/`, etc.) pour adapter les paramètres à votre environnement.
   - Lancer les scripts appropriés pour commencer à publier les données sur MQTT.

## 🧩 Intégrations disponibles

- **Shelly** : Intégration avec les modules Shelly via MQTT pour Home Assistant.
- **Deye** : Connexion aux onduleurs Deye et publication des données sur MQTT.
- **Netatmo** : Récupération des données de capteurs Netatmo vers MQTT.
- **Ajax** : Connexion aux systèmes d’alarme Ajax via le protocole SIA.
- **Solarman** : Interaction avec les onduleurs Solarman.

## 📦 Dépendances

- Python 3.x
- Docker & Docker Compose
- Modules Python requis (voir les fichiers `requirements.txt` dans les différents répertoires)

## 🛠️ Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request pour proposer des améliorations ou signaler des bugs.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.
