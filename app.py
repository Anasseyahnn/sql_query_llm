import streamlit as st
import pandas as pd
import sqlite3
import time
import os
import re
from openai import OpenAI

# Configuration de la page
st.set_page_config(
    page_title="Système d'interrogation de base de données en langage naturel",
    page_icon="🎮",
    layout="wide"
)


# Fonctions utilitaires pour la base de données
def import_sql_file(sql_file, db_name='temp_database.db'):
    """Importer un fichier SQL dans une base de données SQLite"""
    try:
        # Lire le contenu du fichier SQL
        content = sql_file.read().decode('utf-8')

        # Créer une nouvelle base de données SQLite
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Exécuter les commandes SQL
        # On divise les requêtes en fonction des points-virgules
        sql_commands = content.split(';')

        # On garde une trace des tables créées
        tables = []

        for command in sql_commands:
            if command.strip():
                # Exécuter chaque commande SQL
                cursor.execute(command)

                # Extraire les noms de tables des commandes CREATE TABLE
                match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?', command, re.IGNORECASE)
                if match:
                    tables.append(match.group(1))

        conn.commit()

        # Si aucune table n'a été créée, vérifier les tables existantes
        if not tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall() if table[0] != 'sqlite_sequence']

        # Obtenir les informations sur les schémas des tables
        schemas = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            schema_info = cursor.fetchall()
            schema_str = f"create table {table}("
            schema_str += ", ".join([f"{col[1]} {col[2]}" for col in schema_info])
            schema_str += ");"
            schemas[table] = schema_str

        # Créer un aperçu des données pour chaque table
        previews = {}
        for table in tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
                previews[table] = df
            except:
                previews[table] = pd.DataFrame({"message": ["Impossible de lire cette table"]})

        conn.close()

        return {
            'success': True,
            'db_path': db_name,
            'tables': tables,
            'schemas': schemas,
            'previews': previews
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def import_sqlite_db(db_file, db_name='temp_database.db'):
    """Importer une base de données SQLite existante"""
    try:
        # Lire le contenu binaire du fichier
        file_content = db_file.read()

        # Écrire le contenu dans un fichier temporaire
        with open(db_name, 'wb') as f:
            f.write(file_content)

        # Connexion à la base de données
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Obtenir les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall() if table[0] != 'sqlite_sequence']

        # Obtenir les informations sur les schémas des tables
        schemas = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            schema_info = cursor.fetchall()
            schema_str = f"create table {table}("
            schema_str += ", ".join([f"{col[1]} {col[2]}" for col in schema_info])
            schema_str += ");"
            schemas[table] = schema_str

        # Créer un aperçu des données pour chaque table
        previews = {}
        for table in tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
                previews[table] = df
            except:
                previews[table] = pd.DataFrame({"message": ["Impossible de lire cette table"]})

        conn.close()

        return {
            'success': True,
            'db_path': db_name,
            'tables': tables,
            'schemas': schemas,
            'previews': previews
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def execute_sql_query(query, db_path):
    """Exécuter une requête SQL sur la base de données"""
    try:
        # Journaliser la requête pour le débogage
        st.session_state.last_executed_query = query

        conn = sqlite3.connect(db_path)
        result = pd.read_sql_query(query, conn)
        conn.close()
        return {
            'success': True,
            'data': result
        }
    except Exception as e:
        # Journaliser l'erreur complète
        import traceback
        error_details = traceback.format_exc()

        return {
            'success': False,
            'error': str(e),
            'details': error_details
        }


# Fonction pour créer un prompt qui traduit les questions en requêtes SQL
def create_prompt(question, schemas):
    """Créer un prompt qui traduit les questions en requêtes SQL.

    Args:
        question: question sur les données en langage naturel.
        schemas: schémas des tables de la base de données.

    Returns:
        traduction des questions en requêtes SQL
    """
    parts = []
    parts += ['Database:']
    for schema in schemas.values():
        parts += [schema]
    parts += ['Translate this question into SQL query:']
    parts += [question]
    parts += [
        'The query should be valid for SQLite. Do not use window functions or other features that may not be supported by SQLite. Return only the SQL query without any additional text or explanations.']
    return '\n'.join(parts)


# Fonction pour interroger le LLM
def call_llm(prompt, model_name):
    """Interroger le LLM et renvoyer la réponse.

    Args:
        prompt: Entrée du prompt
        model_name: Nom du modèle à utiliser

    Returns:
        la réponse du LLM (uniquement la requête SQL)
    """
    try:
        with st.spinner("Génération de la requête SQL en cours..."):
            ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
            response = ollama_via_openai.chat.completions.create(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            raw_response = response.choices[0].message.content

            # Extraire uniquement la requête SQL (si elle est entre ```sql et ```)
            sql_match = re.search(r'```sql\s*(.*?)\s*```', raw_response, re.DOTALL)
            if sql_match:
                return sql_match.group(1).strip()

            # Si pas de bloc de code SQL, essayer de trouver la requête sans formatage
            sql_match = re.search(r'```\s*(.*?)\s*```', raw_response, re.DOTALL)
            if sql_match:
                return sql_match.group(1).strip()

            # Essayer de capturer la requête directement
            sql_lines = []
            capture = False

            for line in raw_response.split('\n'):
                line = line.strip()

                # Détecter le début d'une requête SQL
                if line and (
                        line.upper().startswith(
                            ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'WITH'))):
                    capture = True
                    sql_lines.append(line)
                # Continuer à capturer les lignes de la requête
                elif capture and line and not line.startswith('#') and not re.match(r'^\w+:', line):
                    sql_lines.append(line)
                # Arrêter la capture si on rencontre un commentaire ou une ligne vide
                elif capture and (not line or line.startswith('#')):
                    capture = False

            if sql_lines:
                return ' '.join(sql_lines)

            # Si tout échoue, retourner la réponse brute
            return raw_response

    except Exception as e:
        st.error(f"Erreur lors de l'interrogation du modèle: {str(e)}")
        return None


# Initialisation des variables de session
if 'db_info' not in st.session_state:
    st.session_state.db_info = None
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'last_executed_query' not in st.session_state:
    st.session_state.last_executed_query = None
if 'error_log' not in st.session_state:
    st.session_state.error_log = {}

# Interface utilisateur principale
st.title("💬 Système d'interrogation de base de données en langage naturel")

# Sidebar pour les configurations
with st.sidebar:
    st.header("Configuration")
    model_name = st.selectbox(
        "Choisir un modèle",
        ["llama3.2", "llama3", "mistral"],
        index=0
    )

    st.markdown("---")

    if st.session_state.db_info:
        st.success(f"Base de données chargée: {len(st.session_state.db_info['tables'])} tables")
        if st.button("Réinitialiser la base de données"):
            st.session_state.db_info = None
            st.session_state.selected_table = None
            st.session_state.query_history = []
            st.session_state.last_executed_query = None
            st.session_state.error_log = {}
            st.rerun()

    st.markdown("---")
    st.markdown("""
    ### Comment ça marche
    1. Importez votre fichier SQL ou base de données SQLite
    2. Posez une question en langage naturel
    3. L'IA la traduira en SQL
    4. Les résultats s'afficheront automatiquement
    """)

# Étape 1: Téléchargement de la base de données
if st.session_state.db_info is None:
    st.header("1️⃣ Importez votre base de données")

    file_type = st.radio(
        "Type de fichier à importer",
        ["Fichier SQL (.sql)", "Base de données SQLite (.db, .sqlite)"]
    )

    if file_type == "Fichier SQL (.sql)":
        uploaded_file = st.file_uploader("Choisissez un fichier SQL", type="sql")

        if uploaded_file is not None:
            with st.spinner("Importation et analyse de la base de données..."):
                db_info = import_sql_file(uploaded_file)

                if db_info['success']:
                    st.session_state.db_info = db_info
                    if len(db_info['tables']) > 0:
                        st.session_state.selected_table = db_info['tables'][0]
                    st.success("Base de données importée avec succès!")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de l'importation de la base de données: {db_info['error']}")

    else:  # Base de données SQLite
        uploaded_file = st.file_uploader("Choisissez un fichier de base de données", type=["db", "sqlite", "sqlite3"])

        if uploaded_file is not None:
            with st.spinner("Importation et analyse de la base de données..."):
                db_info = import_sqlite_db(uploaded_file)

                if db_info['success']:
                    st.session_state.db_info = db_info
                    if len(db_info['tables']) > 0:
                        st.session_state.selected_table = db_info['tables'][0]
                    st.success("Base de données importée avec succès!")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de l'importation de la base de données: {db_info['error']}")

# Étape 2-4: Interrogation et affichage des résultats
else:
    # Afficher les informations sur la base de données
    st.header("Base de données importée")

    # Si plusieurs tables, permettre la sélection
    if len(st.session_state.db_info['tables']) > 1:
        table_tabs = st.tabs(st.session_state.db_info['tables'])

        for i, tab in enumerate(table_tabs):
            table_name = st.session_state.db_info['tables'][i]
            with tab:
                st.subheader(f"Table: {table_name}")

                st.write("Aperçu des données:")
                st.dataframe(st.session_state.db_info['previews'][table_name])

                st.write("Schéma de la table:")
                st.code(st.session_state.db_info['schemas'][table_name], language="sql")
    else:
        table_name = st.session_state.db_info['tables'][0]

        with st.expander("Aperçu des données"):
            st.dataframe(st.session_state.db_info['previews'][table_name])

        with st.expander("Schéma de la table"):
            st.code(st.session_state.db_info['schemas'][table_name], language="sql")

    # Zone de question
    st.header("2️⃣ Posez votre question")
    question = st.text_area(
        "Question en langage naturel",
        placeholder="Exemple: Quels sont les 5 premiers éléments de la table?",
        height=80
    )

    # Option pour éditer manuellement la requête SQL générée
    edit_sql = st.checkbox("Éditer manuellement la requête SQL générée")

    # Bouton pour exécuter la traduction et la requête
    execute_pressed = st.button("Exécuter", type="primary")

    if execute_pressed:
        if not question:
            st.warning("Veuillez entrer une question.")
        else:
            # Traduire la question en SQL
            prompt = create_prompt(question, st.session_state.db_info['schemas'])
            sql_query = call_llm(prompt, model_name)

            if sql_query:
                # Permettre l'édition manuelle de la requête SQL
                if edit_sql:
                    sql_query = st.text_area("Modifier la requête SQL", value=sql_query, height=150)
                    execute_button = st.button("Exécuter la requête modifiée", type="primary")
                    if not execute_button:
                        st.stop()

                # Exécuter la requête SQL
                with st.spinner("Exécution de la requête..."):
                    result = execute_sql_query(sql_query, st.session_state.db_info['db_path'])

                # Sauvegarder les détails d'erreur éventuels dans session_state
                query_id = len(st.session_state.query_history)
                if not result['success'] and 'details' in result:
                    st.session_state.error_log[query_id] = result['details']

                # Ajouter à l'historique des requêtes
                st.session_state.query_history.append({
                    'id': query_id,
                    'question': question,
                    'query': sql_query,
                    'result': result
                })

                # Afficher les résultats
                st.header("3️⃣ Résultats")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Votre question")
                    st.info(question)

                with col2:
                    st.subheader("Requête SQL générée")
                    st.code(sql_query, language="sql")

                if result['success']:
                    st.subheader("Résultats de la requête")
                    if len(result['data']) > 0:
                        st.dataframe(result['data'])
                    else:
                        st.info("La requête n'a retourné aucun résultat.")
                else:
                    st.error(f"Erreur lors de l'exécution de la requête: {result['error']}")
                    # Afficher la requête exécutée directement ici plutôt que dans un expander
                    st.subheader("Requête exécutée")
                    st.code(st.session_state.last_executed_query, language="sql")

    # Afficher l'historique des requêtes
    if len(st.session_state.query_history) > 0:
        st.header("Historique des requêtes")

        # Bouton pour effacer l'historique
        if st.button("Effacer l'historique des requêtes"):
            st.session_state.query_history = []
            st.session_state.error_log = {}
            st.success("L'historique des requêtes a été effacé.")
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"Question {len(st.session_state.query_history) - i}: {item['question'][:50]}..."):
                st.markdown("**Question:**")
                st.info(item['question'])

                st.markdown("**Requête SQL:**")
                st.code(item['query'], language="sql")

                st.markdown("**Résultat:**")
                if item['result']['success']:
                    if len(item['result']['data']) > 0:
                        st.dataframe(item['result']['data'])
                    else:
                        st.info("La requête n'a retourné aucun résultat.")
                else:
                    st.error(f"Erreur: {item['result']['error']}")
                    # Au lieu d'utiliser un expander imbriqué, afficher directement le détail d'erreur
                    if item['id'] in st.session_state.error_log:
                        st.text("Détails de l'erreur:")
                        st.code(st.session_state.error_log[item['id']])