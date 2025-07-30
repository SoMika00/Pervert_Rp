# Fichier: ./backend/src/api/routers/models.py (Final et Complet)

from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from ..connectors import db

router = APIRouter()

@router.get(
    "/",
    response_model=List[db.ModelInfo],
    summary="Lister toutes les personnalités disponibles"
)
async def get_all_models():
    """
    Récupère une liste de toutes les personnalités (modèles) stockées
    dans la base de données, en retournant uniquement leur ID et leur nom.
    Cette route est utilisée pour peupler les menus déroulants dans l'interface.
    """
    try:
        return await db.list_models()
    except Exception as e:
        # Si une erreur de base de données se produit, on lève une erreur serveur interne.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des modèles depuis la base de données: {e}"
        )

@router.post(
    "/",
    response_model=db.ModelPersonality,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle personnalité"
)
async def create_new_model(model_data: db.CreateModelRequest):
    """
    Crée une nouvelle personnalité (modèle) en recevant toutes ses caractéristiques
    depuis le frontend. Elle est sauvegardée dans la base de données et
    l'objet complet nouvellement créé est retourné.
    """
    try:
        new_model = await db.create_model(model_data)
        return new_model
    except ValueError as e: # Cas où le nom existe déjà (UniqueViolation)
        # On retourne un code 409 Conflict pour indiquer que la ressource existe déjà.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur interne est survenue lors de la création du modèle: {e}"
        )

@router.put(
    "/{model_id}/name",
    response_model=db.ModelPersonality,
    summary="Mettre à jour le nom d'une personnalité"
)
async def edit_model_name(model_id: UUID, request: db.UpdateModelNameRequest):
    """
    Met à jour uniquement le nom d'une personnalité existante en utilisant son ID.
    Ceci est utile pour corriger une faute de frappe ou renommer un modèle.
    """
    try:
        updated_model = await db.update_model_name(model_id, request.name)
        if not updated_model:
            # Si la base de données ne retourne rien, c'est que l'ID n'existait pas.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La personnalité avec l'ID {model_id} n'a pas été trouvée."
            )
        return updated_model
    except ValueError as e: # Cas où le nouveau nom est déjà pris par un autre modèle.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur interne est survenue lors de la mise à jour du nom: {e}"
        )