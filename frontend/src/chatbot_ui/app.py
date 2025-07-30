import streamlit as st
import requests
import uuid
import os
from typing import List, Dict
import time

# --- CONFIGURATION ET CONSTANTES ---
st.set_page_config(page_title="Créateur de Personnalités", layout="wide")
BASE_API_URL = os.environ.get("STREAMLIT_BACKEND_API_URL", "http://localhost:8001/api/v1")
MODELS_URL = f"{BASE_API_URL}/models/"
CHAT_URL = f"{BASE_API_URL}/chat/"

# --- INITIALISATION DE L'ÉTAT DE SESSION ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_name" not in st.session_state:
    st.session_state.selected_model_name = None
# NOUVEAU: Drapeau pour déclencher l'auto-scroll
if "scroll_to_bottom" not in st.session_state:
    st.session_state.scroll_to_bottom = False

# --- MODÈLE DE DONNÉES ET FONCTIONS API ---
class ModelInfo:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

@st.cache_data(ttl=30)
def get_available_models() -> List[ModelInfo]:
    try:
        response = requests.get(MODELS_URL)
        response.raise_for_status()
        return [ModelInfo(id=m['id'], name=m['name']) for m in response.json()]
    except requests.RequestException:
        return []

# --- CHARGEMENT DES DONNÉES ---
st.title("🎭 Plateforme de Chat et Création de Personnalités")
available_models = get_available_models()
model_map = {m.name: m.id for m in available_models}

# --- INTERFACE À ONGLETS ---
tab_chat, tab_create_edit = st.tabs(["💬 Chat", "✍️ Créer & Modifier une Personnalité"])

# ===================================================================
# ==================== ONGLET DE CHAT (LOGIQUE FINALE) ================
# ===================================================================
with tab_chat:
    st.header("Discutez avec une personnalité")

    if not available_models:
        st.info("Aucune personnalité n'est disponible. Veuillez en créer une dans l'onglet 'Créer & Modifier'.")
    else:
        model_names = list(model_map.keys())
        if st.session_state.selected_model_name not in model_names:
            st.session_state.selected_model_name = model_names[0]
        current_index = model_names.index(st.session_state.selected_model_name)
        selected_name = st.selectbox(
            "Choisissez une personnalité avec qui discuter :",
            options=model_names,
            index=current_index
        )
        if st.session_state.selected_model_name != selected_name:
            st.session_state.selected_model_name = selected_name
            st.session_state.messages = []
            st.rerun()

        st.subheader(f"En conversation avec : {st.session_state.selected_model_name}")
        st.markdown("---")

        # AFFICHAGE DE L'HISTORIQUE
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # LOGIQUE DE RÉPONSE DE L'ASSISTANT
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            with st.chat_message("assistant"):
                # AMÉLIORATION: Spinner plus immersif
                with st.spinner("..."):
                    history_for_api = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
                    payload = {
                        "model_id": model_map[st.session_state.selected_model_name],
                        "session_id": st.session_state.session_id,
                        "message": history_for_api[-1]["content"],
                        "history": history_for_api[:-1]
                    }
                    try:
                        response = requests.post(CHAT_URL, json=payload, timeout=180)
                        response.raise_for_status()
                        full_response = response.json().get("response", "")
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        # NOUVEAU: On active le drapeau pour l'auto-scroll
                        st.session_state.scroll_to_bottom = True
                        st.rerun()
                    except requests.RequestException as e:
                        detail = f"Erreur de communication : {e.response.json().get('detail', 'inconnue') if e.response else e}"
                        st.error(detail)
                        st.session_state.messages.pop()

        # CAPTURE DE L'ENTRÉE UTILISATEUR
        if prompt := st.chat_input(f"Écrivez à {st.session_state.selected_model_name}..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# --- NOUVEAU : LOGIQUE D'AUTO-SCROLL ---
# Ce code s'exécute après le rendu de la page.
if st.session_state.scroll_to_bottom:
    # On injecte du JavaScript pour faire défiler la fenêtre.
    # Le délai (50ms) laisse le temps à Streamlit de dessiner le nouveau message avant de scroller.
    js = f"""
        <script>
            function scroll(dummy_var_to_force_reexecution){{
                var body = window.parent.document.querySelector(".main");
                body.scrollTop = body.scrollHeight;
            }}
            setTimeout(scroll, 50);
        </script>
    """
    st.components.v1.html(js)
    # On réinitialise le drapeau pour ne pas scroller à chaque interaction.
    st.session_state.scroll_to_bottom = False


# =====================================================================
# ================= ONGLET DE CRÉATION ET MODIFICATION =================
# =====================================================================
with tab_create_edit:
    st.header("Gestion des Personnalités")

    # (Le code de cet onglet est complet et ne change pas)
    st.subheader("Modifier le nom d'une personnalité")
    if not model_map:
        st.info("Aucune personnalité à modifier.")
    else:
        col1, col2 = st.columns([2, 3])
        with col1:
            model_to_edit_name = st.selectbox("Personnalité à modifier", options=list(model_map.keys()), key="editor_select_modifier")
        if model_to_edit_name:
            with col2:
                with st.form("edit_name_form"):
                    new_name_for_edit = st.text_input("Nouveau nom", value=model_to_edit_name, label_visibility="collapsed")
                    if st.form_submit_button("Mettre à jour le nom"):
                        if new_name_for_edit.strip() and new_name_for_edit.strip() != model_to_edit_name:
                            try:
                                response = requests.put(f"{MODELS_URL}{model_map[model_to_edit_name]}/name", json={"name": new_name_for_edit.strip()})
                                response.raise_for_status()
                                st.success("Nom mis à jour avec succès !")
                                st.cache_data.clear()
                                st.rerun()
                            except requests.RequestException as e:
                                st.error(f"Erreur: {e.response.json().get('detail', 'Erreur inconnue')}")

    st.divider()

    st.subheader("Créer une nouvelle personnalité")
    with st.form("create_persona_form"):
        st.markdown("**1. Identité de Base**")
        c1, c2 = st.columns(2)
        name = c1.text_input("Nommez votre personnalité*", placeholder="Ex: Seline, la tentatrice")
        gender = c1.text_input("Genre", placeholder="Ex: Femme, Homme... (Défaut: Femme)")
        language = c2.radio("Langue*", ["Français", "English"], horizontal=True)

        st.markdown("**2. Instructions Additionnelles (Optionnel)**")
        prompt_additions = st.text_area("Vos instructions", placeholder="Ex: Passionnée d'astronomie, déteste l'impolitesse.")

        st.markdown("**3. Attributs Physiques (Optionnel)**")
        c1, c2 = st.columns(2)
        race = c1.text_input("Race / Origine", placeholder="Ex: Caucasienne")
        hair_color = c1.text_input("Couleur des cheveux", placeholder="Ex: Blonds")
        body_type = c2.text_input("Physique / Silhouette", placeholder="Ex: Svelte")
        clothing_style = c2.text_input("Style vestimentaire", placeholder="Ex: Élégant")
        
        st.markdown("**4. Réglages Fins du Comportement**")
        c1, c2 = st.columns(2)
        libido_level = c1.slider("Désir / Libido", 1, 5, 3, help="1: Froid(e) -> 5: Insatiable")
        intelligence_level = c1.slider("Intelligence", 1, 5, 3, help="1: Naïf/Simple -> 5: Brillant/Calculateur")
        dominance = c1.slider("Comportement (Soumis vs Dominant)", 1, 5, 3, help="1: Soumise -> 5: Dominatrice")
        audacity = c1.slider("Audace / Langage Cru", 1, 5, 3, help="1: Timide -> 5: Très direct et explicite")
        tone = c1.slider("Tonalité (Joueur vs Sérieux)", 1, 5, 2, help="1: Joueuse -> 5: Sérieuse")
        emotion_level = c2.slider("Intensité Émotionnelle", 1, 5, 3, help="1: Robotique -> 5: Très expressif")
        initiative_level = c2.slider("Initiative", 1, 5, 3, help="1: Réactive -> 5: Mène la conversation")
        vocabulary_level = c2.slider("Richesse du Vocabulaire", 1, 5, 3, help="1: Basique -> 5: Littéraire")
        emojis_level = c2.slider("Fréquence des Emojis", 1, 5, 3, help="1: Jamais -> 5: Très fréquent")
        imperfection_level = c2.slider("Style d'écriture (Parfait vs Oral)", 1, 5, 1, help="1: Parfait -> 5: Oral/Fautes")

        if st.form_submit_button("Sauvegarder la Nouvelle Personnalité"):
            name_clean = name.strip()
            if not name_clean:
                st.error("Le nom de la personnalité est obligatoire.")
            else:
                gender_final = gender.strip().lower() if gender.strip() else "femme"
                payload = {
                    "name": name_clean, "language": 'en' if language == 'English' else 'fr',
                    "gender": gender_final, "prompt_additions": prompt_additions,
                    "race": race, "hair_color": hair_color, "body_type": body_type, "clothing_style": clothing_style,
                    "libido_level": libido_level, "intelligence_level": intelligence_level, "dominance": dominance,
                    "audacity": audacity, "tone": tone, "emotion": emotion_level, "initiative": initiative_level,
                    "vocabulary": vocabulary_level, "emojis": emojis_level, "imperfection": imperfection_level
                }
                try:
                    final_payload = {k: v for k, v in payload.items() if v or isinstance(v, int)}
                    response = requests.post(MODELS_URL, json=final_payload)
                    response.raise_for_status()
                    st.success(f"Personnalité '{name_clean}' créée ! Elle est disponible dans l'onglet Chat.")
                    st.cache_data.clear()
                    st.rerun()
                except requests.RequestException as e:
                    st.error(f"Erreur de création: {e.response.json().get('detail', 'Erreur inconnue')}")