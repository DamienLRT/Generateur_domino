# Streamlit - Outils ludiques : Dominos & « J’ai… qui a ? »

Cette application Streamlit permet de générer facilement :

1. Des **dominos personnalisés** à partir d’images avec fond blanc, et de les télécharger en PDF.
2. Un **jeu « J’ai… qui a ? »** à partir d’images, avec génération automatique des cartes en PDF.

L’application est organisée en **deux onglets** pour naviguer facilement entre les deux fonctionnalités.

---

## Fonctionnalités

### 1. Dominos
- Importer **au moins 2 images** (PNG, JPG, JPEG).
- Génération automatique des dominos :
  - Chaque domino est divisé en deux parties avec une ligne de séparation.
  - Fond blanc pour une impression propre.
- Télécharger **tous les dominos en PDF**.
- Aperçu des dominos générés directement dans l’application.

### 2. « J’ai… qui a ? »
- Importer **une ou plusieurs images** (PNG, JPG, JPEG).  
  L’ordre des images définit l’ordre du jeu.
- Génération automatique des cartes :
  - La première carte indique « J’ai la première carte ! » et « Qui a ? ».
  - Les cartes intermédiaires affichent « J’ai » et « Qui a ? » avec les images correspondantes.
  - La dernière carte indique « … c’est la dernière carte ! ».
- Télécharger **le jeu complet en PDF** prêt à imprimer.

---

## Installation

1. Cloner le dépôt ou télécharger le fichier `app.py`.
2. Installer les dépendances Python nécessaires :
