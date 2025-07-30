# Projet Chatbot RP v3 - Plateforme de Personnalités Multi-Modèles

Ce projet est une API et une interface web pour un chatbot de Roleplay avancé. La version 3 introduit une architecture complète permettant aux utilisateurs de créer, sauvegarder et interagir avec de multiples personnalités (appelées "modèles").

## Architecture

- **Frontend (Streamlit)**: Interface utilisateur pour discuter et pour créer/configurer de nouvelles personnalités.
- **Backend (FastAPI)**: Gère la logique métier, la communication avec le LLM et les interactions avec la base de données.
- **LLM Service (vLLM)**: Sert le modèle de langage principal.
- **Database (PostgreSQL)**: Stocke les définitions des personnalités créées par les utilisateurs.
- **Vector Store (Qdrant)**: Prêt pour une utilisation future (recherche sémantique, mémoire à long terme).

## Fonctionnalités Clés

- **Création de Personnalité Dynamique**: Une interface dédiée permet de nommer une nouvelle personnalité, de lui donner des instructions de base et d'ajuster ses traits de caractère via des sliders.
- **Persistance en Base de Données**: Les personnalités créées sont sauvegardées dans une base de données PostgreSQL, lancée via Docker Compose.
- **Sélection de Modèle**: Les utilisateurs peuvent choisir avec quelle personnalité interagir via un menu déroulant dans l'interface de chat.
- **Historique de Conversation par Session**: L'historique est maintenu pour la conversation en cours.
- **Architecture Découplée et Scalable** grâce à Docker.