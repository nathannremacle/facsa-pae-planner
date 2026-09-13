# FACSA PAE Planner — Outil d'aide à la décision pour le PAE et les Masters

[![ULiège](https://img.shields.io/badge/ULi%C3%A8ge-FACSA-f07f3c.svg)](https://www.facsa.uliege.be/)
[![Bachelier](https://img.shields.io/badge/Programme-ABICIV0099-00707f.svg)](https://www.programmes.uliege.be/cocoon/20242025/programmes/ABICIV0099_C.html)
[![Compatibilité](https://img.shields.io/badge/R%C3%A9trocompatibilit%C3%A9-100%25%20Officielle-137333.svg)](https://www.mmm.uliege.be/facsa/horaires/ABICIV0099)
[![License](https://img.shields.io/badge/Licence-MIT-blue.svg)](LICENSE)

Application web interactive conçue pour les étudiants et la **Faculté des Sciences Appliquées (FACSA)** de l'**Université de Liège (ULiège)**. 

Elle permet de composer son **Programme Annuel de l'Étudiant (PAE)**, de simuler son **horaire hebdomadaire sans conflit**, de vérifier le respect des **règles académiques officielles (prérequis et corequis)**, et de projeter ses choix vers les **12 Masters d'ingénieur civil**.

---

## 🔗 Lien avec l'outil officiel ULiège & Rétrocompatibilité

L'application est bâtie sur le socle de l'outil horaire officiel développé pour la faculté :
* **Outil officiel ULiège** : [https://www.mmm.uliege.be/facsa/horaires/ABICIV0099](https://www.mmm.uliege.be/facsa/horaires/ABICIV0099)

### 🔁 Rétrocompatibilité totale à 100%
* **Encodage d'URL bidirectionnel** : L'outil utilise rigoureusement le même algorithme officiel de compression bitpack (`#b=...`).
* **Interopérabilité immédiate** :
  * N'importe quel lien généré sur le site officiel de l'université s'ouvre fidèlement dans cette application.
  * À l'inverse, toute composition de PAE faite ici génère un lien de partage officiel et peut être ouverte en un clic sur le site `www.mmm.uliege.be` grâce au bouton dédié.

---

## 🚀 Pourquoi ce projet ? (Nouveautés vs Outil officiel)

L'outil officiel existant permet de visualiser un horaire à partir d'un ensemble de cours, mais suppose que l'étudiant connaît déjà par cœur tous ses prérequis, le nombre de crédits autorisés par bloc et les conditions d'accès aux futurs masters.

| Fonctionnalité | Outil officiel ULiège | FACSA PAE Planner |
| :--- | :---: | :---: |
| **Grille horaire interactive (Q1 / Q2)** | ✅ | ✅ *(Identique)* |
| **Détection des conflits d'horaires** | ✅ | ✅ *(Identique)* |
| **Partage par URL compressée (`#b=...`)** | ✅ | ✅ *(100% compatible)* |
| **Export de l'horaire en calendrier (.ics)** | ❌ | ✅ *(Google Calendar, Apple, Outlook)* |
| **Déclaration des cours déjà validés (Étape 1)** | ❌ | ✅ *(Raccourcis Bloc 1, Blocs 1&2)* |
| **Masquage intelligent des cours réussis** | ❌ | ✅ |
| **Contrôle strict des prérequis bloquants** | ❌ | ✅ *(Pastilles P et alertes jury)* |
| **Détection des dérogations de corequis requises** | ❌ | ✅ *(Pastilles C et récapitulatif)* |
| **Contrôle des crédits (Q1, Q2, total)** | Sommaire | ✅ *(Comptage précis & équilibre)* |
| **Simulateur d'accès aux 12 Masters (Étape 3)** | ❌ | ✅ *(Accès direct, mineure, standard)* |
| **Détail des cours de domaine manquants** | ❌ | ✅ *(Par Bloc 2 et Bloc 3)* |
| **Sauvegarde automatique (`localStorage`)** | ❌ | ✅ *(Aucune perte au rafraîchissement)* |

---

## 🧭 Articulation de l'outil en 3 étapes

Le flux utilisateur est structuré en **3 étapes guidées**, respectant la charte graphique et l'ergonomie officielle de la faculté :

### 1. Cours déjà acquis (Validation des années précédentes)
* Permet de cocher en quelques secondes les cours déjà réussis.
* Boutons rapides en un clic : **« Bloc 1 réussi »** (60 ECTS obligatoires) et **« Blocs 1 & 2 réussis »** (106 ECTS obligatoires).
* Les crédits acquis sont comptabilisés et immédiatement mémorisés dans le navigateur.

### 2. Mon PAE & Horaire (Construction de l'année en cours)
* Affiche l'offre de cours de la faculté **débarrassée des cours déjà acquis**.
* **Pastilles discrètes `P` (prérequis) et `C` (corequis)** sur chaque cours :
  * `P` vert : prérequis bien validé à l'étape 1.
  * `P` rouge : ⛔ prérequis manquant bloquant selon le règlement officiel.
  * `C` vert : corequis acquis ou inscrit au PAE.
  * `C` orange : ⚠️ corequis non inscrit nécessitant une dérogation officielle auprès du jury.
* **Panneaux de contrôle officiels sous le tableau** : synthétisent exactement les formulaires de dérogation à cocher sur le portail institutionnel.
* **Grille horaire interactive officielle** : bascule en mode horaire d'un clic avec vue sur les cours du matin/après-midi et coloration en rouge des plages en conflit.

### 3. Débouchés & Simulateur des 12 Masters d'ingénieur civil
* Analyse en direct la projection du parcours vers l'ensemble des **12 Masters en Sciences de l'Ingénieur** de l'ULiège :
  1. *Informatique*
  2. *Science des Données*
  3. *Mécanique*
  4. *Aérospatiale*
  5. *Électricien*
  6. *Énergie*
  7. *Génie Civil / Constructions*
  8. *Chimie et Science des Matériaux*
  9. *Biomédical*
  10. *Mines et Géologue*
  11. *Physicien*
  12. *Architecte*
* **Règles officielles d'admission appliquées automatiquement** :
  * 🟢 **Accès direct de plein droit garanti** : dès que l'étudiant cumule $\ge$ **30 crédits ECTS** dans les cours prérequis du domaine (option principale).
  * 🟡 **Accès avec mineure (passerelle allégée)** : dès que l'étudiant cumule entre **10 et 25 crédits ECTS** dans le domaine.
  * ⚪ **Programme standard** : moins de 10 crédits.
* **Tableaux détaillés par Bloc (Bloc 2 / Bloc 3)** sous chaque Master :
  * Affiche pour chaque cours du domaine son statut exact avec pastilles soignées : `✓ Acquis`, `✓ Au PAE` ou `Non suivi`.
  * Possibilité d'ajouter ou retirer directement un cours prérequis à son PAE depuis la fiche du Master pour voir la jauge d'admission progresser en temps réel.

---

## 💻 Architecture technique

Le projet a été pensé pour être **100 % autonome, ultra-léger et sans maintenance serveur** :
* **Fichier unique autonome** : [index.html](index.html) intègre l'ensemble du DOM, des styles, de la logique Alpine.js, du SVG sprite et des dictionnaires de cours.
* **Zéro dépendance externe / Aucun backend requis** : aucun framework lourd, aucune base de données, respect total de la vie privée des étudiants (aucun tracking, données conservées localement dans `localStorage`).
* **Script de génération reproductible** : [build_clean_official.py](build_clean_official.py) est le script Python (standard library pure, sans pip install) qui compile les données institutionnelles et génère l'application.

---

## 🛠️ Utilisation locale

Pour lancer l'application en local :

```bash
# Cloner le dépôt
git clone https://github.com/nathannremacle/facsa-pae-planner.git
cd facsa-pae-planner

# Lancer un serveur local léger (Python)
python -m http.server 8080
```
Ouvrez ensuite simplement `http://localhost:8080/` dans votre navigateur.

Pour recompiler l'application après modification des données :
```bash
python build_clean_official.py
```

---

## 📜 Licence & Droits

* Modèle d'horaire initial et styles officiels © Université de Liège (ULiège) — Faculté des Sciences Appliquées.
* Extension PAE, vérification des prérequis/corequis, algorithmes de débouchés Masters et développements © Nathan Remacle — Projet partagé avec la communauté universitaire sous licence MIT.
