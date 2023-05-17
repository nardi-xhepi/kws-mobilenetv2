# Reconnaissance Vocale de mot-clés (Keyword spotting)

Ce projet est une application web interactive qui permet aux utilisateurs d'interagir avec un réseau de neurones pour enregistrer leur voix, la former et la reconnaître. Le modèle d'apprentissage est basé sur le MobileNetV2.

## Structure du Projet

La structure du projet est organisée comme suit:

```bash
.
├─── kws
│    ├─── ia
│    │    ├─── data
│    │    │    ├─── keyword
│    │    │    ├─── noise
│    │    │    └─── unknown
│    │    ├─── scripts
│    │    └─── user_data
│    ├─── migrations
│    ├─── templates
│    │    ├─── css
│    │    ├─── html
│    │    ├─── javascript
│    │    └─── media
│    └─── __pycache__
└─── website
     └─── __pycache__
```

- `kws` : Contient tous les fichiers principaux de l'application.
   - `ia` : Contient les scripts et les données nécessaires pour la formation et la prédiction du modèle.
   - `data` : Contient les données audio utilisées pour l'entraînement du modèle, classées par 'keyword', 'noise' et 'unknown'.
   - `scripts` : Contient les scripts python pour la préparation des données et l'entraînement du modèle.
   - `user_data` : Contient les données enregistrées par les utilisateurs.
   - `migrations` : Contient les fichiers de migration de Django pour la base de données.
   - `templates` : Contient les fichiers statiques et les templates HTML pour l'interface utilisateur.
   - `__pycache__` : Contient les fichiers bytecode Python générés par l'interpréteur.
- `website` : Contient les fichiers de configuration de Django pour le site web.

## Utilisation

### Prérequis

- Python 3.8 ou supérieur
- Django 2.2 ou supérieur
- Librairies Python : TensorFlow, Librosa, Numpy

### Installation

1. Clonez ce dépôt dans votre environnement local.
2. Installez les dépendances avec `pip install -r requirements.txt`.
3. Lancez le serveur Django avec `python manage.py runserver`.
4. Accédez à `http://localhost:8000` dans votre navigateur pour utiliser l'application.

## À propos de l'application KWS

L'application KWS (Keyword Spotting) est une application de reconnaissance vocale basée sur l'apprentissage profond. Elle utilise un réseau de neurones entraîné pour reconnaître des mots-clés spécifiques dans des enregistrements audio. Les utilisateurs peuvent interagir avec le réseau de neurones, enregistrer leur voix, la former et la reconnaître.

Le processus de formation du modèle est le suivant :

1. Les fichiers audio sont chargés et convertis en une représentation MFCC (Mel-Frequency Cepstral Coefficients).
2. Les données sont divisées en ensembles d'entraînement et de validation.
3. Un modèle pré-entraîné, MobileNetV2, est utilisé comme base pour le réseau de neurones.
4. Le modèle est adapté à la tâche en ajoutant quelques nouvelles couches à la fin.
5. Le modèle est entraîné sur les données d'entraînement et validé sur les données de validation.

L'application KWS est conçue pour être facile à utiliser et à interagir. Elle fournit une interface utilisateur intuitive qui guide les utilisateurs à travers le processus d'entraînement et de prédiction.

## Contribuer

Nous accueillons les contributions de tous ceux qui souhaitent améliorer ce projet. N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
