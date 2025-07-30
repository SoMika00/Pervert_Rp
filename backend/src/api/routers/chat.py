# Fichier: ./backend/src/api/routers/chat.py (Final et Complet)

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID
import httpx

from ..connectors import db
from ..services import vllm_client
from ..services.persona_builder import build_dynamic_system_prompt

router = APIRouter()

# --- Modèles Pydantic pour la validation des données entrantes et sortantes ---

class ChatRequest(BaseModel):
    model_id: UUID = Field(..., description="L'ID de la personnalité à utiliser pour la conversation.")
    session_id: UUID = Field(..., description="L'ID de la session de chat actuelle pour regrouper les logs.")
    message: str = Field(..., description="Le message textuel de l'utilisateur.")
    history: List[Dict[str, str]] = Field(default=[], description="L'historique des derniers échanges pour le contexte.")

class ChatResponse(BaseModel):
    response: str

# --- Endpoint principal de la conversation ---

@router.post(
    "/",
    response_model=ChatResponse,
    summary="Générer une réponse de chat et enregistrer l'interaction"
)
async def handle_chat(request: ChatRequest):
    """
    Prend en charge une requête de chat pour un modèle de personnalité spécifique.
    Le processus est le suivant :
    1. Récupère la personnalité complète depuis la base de données via son ID.
    2. Construit le prompt système dynamique en utilisant les données de la personnalité.
    3. Appelle le service vLLM externe pour obtenir une réponse textuelle.
    4. Enregistre l'interaction (message utilisateur et réponse IA) dans la base de données.
    """
    try:
        # Étape 1: Récupérer la personnalité depuis la BDD
        personality = await db.get_model_by_id(request.model_id)
        if not personality:
            # Si le modèle n'est pas trouvé, il est impossible de continuer.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"La personnalité avec l'ID {request.model_id} n'a pas été trouvée."
            )

        # Étape 2: Construire le prompt système dynamique
        system_prompt = build_dynamic_system_prompt(personality)
        
        # Préparer la liste complète de messages pour le LLM
        messages_for_llm = [system_prompt] + request.history + [{"role": "user", "content": request.message}]

        # Étape 3: Appeler le service vLLM pour obtenir une réponse
        response_text = await vllm_client.get_vllm_response(messages_for_llm)
        
        # Étape 4: Enregistrer l'interaction dans les logs
        await db.log_chat_interaction(
            session_id=request.session_id,
            model_id=request.model_id,
            user_message=request.message,
            assistant_response=response_text
        )
        
        return ChatResponse(response=response_text)

    except httpx.ConnectError as e:
        # Erreur spécifique si le service vLLM n'est pas joignable.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"Impossible de se connecter au service du modèle LLM (vLLM): {e}"
        )
    except Exception as e:
        # Gestionnaire générique pour toutes les autres erreurs.
        if isinstance(e, HTTPException):
            raise e # Si c'est déjà une erreur HTTP (comme notre 404), on la propage.
        
        print(f"ERREUR INATTENDUE dans handle_chat: {e}") # Log pour le débogage serveur
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Une erreur interne inattendue est survenue: {str(e)}"
        )