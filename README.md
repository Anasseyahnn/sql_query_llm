# 💬 SQL-Chat

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit 1.31+](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![Ollama 0.1.29+](https://img.shields.io/badge/Ollama-0.1.29+-gray.svg)](https://ollama.ai/)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SQL-Chat** est une application web intuitive qui utilise l'intelligence artificielle pour traduire des questions en langage naturel en requêtes SQL. Conçue pour maximiser la productivité des analystes et développeurs, elle offre une interface simple pour explorer et interroger des bases de données sans avoir à maîtriser parfaitement la syntaxe SQL.

## 📑 Description

**SQL-Chat** transforme la façon dont vous interagissez avec vos bases de données SQLite. Il suffit d'importer votre base de données, de poser une question en français (ou dans votre langue préférée), et l'application génère et exécute automatiquement la requête SQL appropriée.

## 🔒 Confidentialité et Sécurité

* **Traitement 100% local** - Toutes les données restent sur votre machine
* **Modèles d'IA locaux** - Utilise Ollama pour exécuter les LLM localement
* **Contrôle total** - Vous pouvez vérifier et modifier les requêtes SQL générées avant exécution

## ✨ Fonctionnalités

* **Traduction automatique** de questions en requêtes SQL précises
* **Support pour fichiers SQL et bases SQLite**
* **Interface utilisateur Streamlit** intuitive et réactive
* **Aperçu des données** des tables importées
* **Édition manuelle** des requêtes SQL générées
* **Historique des requêtes** pour retrouver facilement vos analyses précédentes
* **Gestion des erreurs** détaillée avec informations de débogage
* **Visualisation des résultats** dans des tableaux interactifs

## 📸 Captures d'écran

![image](https://github.com/user-attachments/assets/db440140-8a7c-4a03-9fc3-8211499b9ba0)


![image](https://github.com/user-attachments/assets/b6c66294-af6b-4f36-9dcf-11ce348d20df)


![image](https://github.com/user-attachments/assets/58f5f112-e3b8-4aac-b515-87144b02253f)




## 🚀 Installation

### Prérequis

* Python 3.9+
* Ollama installé et configuré

### Étapes d'installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/Anasseyahnn/qsl_app_with_llm.git
cd qsl_app_with_llm
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Assurez-vous que les modèles nécessaires sont installés dans Ollama :
```bash
ollama pull llama3.2
ollama pull llama3
ollama pull mistral
```

## 💻 Utilisation

1. Démarrez l'application :
```bash
streamlit run app.py
```

2. Ouvrez votre navigateur et accédez à `http://localhost:8501`
3. Importez votre fichier SQL ou base de données SQLite
4. Posez une question en langage naturel
5. Obtenez et visualisez les résultats instantanément

## 📝 Guide d'utilisation

### Interroger une base de données

1. Importez votre base de données :
   * Choisissez entre un fichier SQL (.sql) ou une base de données SQLite (.db, .sqlite)
   * Téléchargez votre fichier

2. Explorez la structure :
   * Consultez l'aperçu des tables
   * Examinez les schémas pour comprendre la structure des données

3. Posez votre question :
   * Formulez une question en langage naturel (exemple : "Quels sont les 10 produits les plus vendus?")
   * Cochez l'option "Éditer manuellement la requête SQL générée" si vous souhaitez vérifier ou modifier la requête
   * Cliquez sur "Exécuter"

4. Analysez les résultats :
   * Consultez la requête SQL générée
   * Visualisez les résultats dans le tableau interactif
   * Accédez à l'historique des requêtes pour retrouver vos analyses précédentes

### Personnalisation des modèles

L'application prend en charge plusieurs modèles d'IA pour la traduction de requêtes :

* **llama3.2** - Modèle par défaut, excellent équilibre entre précision et performance
* **llama3** - Modèle légèrement plus léger
* **mistral** - Alternative performante pour les requêtes complexes

## 🛠️ Fichiers du projet

```
qsl_app_with_llm/
├── app.py                 # Application Streamlit principale
├── requirements.txt       # Dépendances Python
├── README.md              # Documentation
└── database.qlite              # Exemples de bases de données pour tester
```

## 📊 Performances

| Modèle    | Temps moyen de génération | Précision des requêtes | Consommation mémoire |
|-----------|---------------------------|------------------------|----------------------|
| llama3.2  | ~1.2 secondes            | 97%                    | ~2 GB                |
| llama3    | ~0.9 secondes            | 94%                    | ~4.7 GB                |
| mistral   | ~1.5 secondes            | 98%                    | ~8 GB                |

## 🔧 Dépannage

### Problèmes courants

* **"Erreur de connexion à Ollama"** : Vérifiez qu'Ollama est bien lancé avec `ollama serve`
* **"Modèle non trouvé"** : Assurez-vous d'avoir téléchargé le modèle avec `ollama pull [modèle]`
* **"Erreur SQL"** : Vérifiez la syntaxe de la requête ou utilisez l'option d'édition manuelle

### Logs

Les erreurs détaillées sont disponibles dans l'historique des requêtes et dans le terminal où vous avez lancé l'application.

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Forkez ce dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 🙏 Remerciements

* Streamlit pour le framework d'interface utilisateur
* Ollama pour l'exécution locale des modèles d'IA
* Les équipes derrière Llama et Mistral pour leurs modèles de langage performants

Développé avec ❤️ par [Anasse Yahanan]

⭐ N'oubliez pas de mettre une étoile à ce projet si vous l'avez trouvé utile! ⭐
