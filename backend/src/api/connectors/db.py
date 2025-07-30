# Fichier: ./backend/src/api/connectors/db.py (Finalisé)

import asyncpg
from uuid import UUID
from pydantic import BaseModel, Field
from typing import List, Optional
from ..config import settings

# --- MODÈLES PYDANTIC ---

class ModelPersonality(BaseModel):
    id: UUID
    name: str
    language: str
    prompt_additions: Optional[str] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    body_type: Optional[str] = None
    clothing_style: Optional[str] = None
    distinguishing_features: Optional[str] = None
    libido_level: int
    intelligence_level: int
    dominance: int
    audacity: int
    tone: int
    emotion: int
    initiative: int
    vocabulary: int
    emojis: int
    imperfection: int
    class Config: from_attributes = True

class CreateModelRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    language: str = Field(default='fr')
    prompt_additions: Optional[str] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    body_type: Optional[str] = None
    clothing_style: Optional[str] = None
    distinguishing_features: Optional[str] = None
    libido_level: int = Field(default=3, ge=1, le=5)
    intelligence_level: int = Field(default=3, ge=1, le=5)
    dominance: int = Field(default=3, ge=1, le=5)
    audacity: int = Field(default=3, ge=1, le=5)
    tone: int = Field(default=2, ge=1, le=5)
    emotion: int = Field(default=3, ge=1, le=5)
    initiative: int = Field(default=3, ge=1, le=5)
    vocabulary: int = Field(default=3, ge=1, le=5)
    emojis: int = Field(default=3, ge=1, le=5)
    imperfection: int = Field(default=1, ge=1, le=5)

class UpdateModelNameRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)

class ModelInfo(BaseModel):
    id: UUID
    name: str

# --- FONCTIONS BDD ---

async def get_db_connection():
    try:
        return await asyncpg.connect(settings.DATABASE_URL)
    except asyncpg.PostgresError as e:
        print(f"Erreur critique de connexion à la base de données: {e}")
        raise

async def get_model_by_id(model_id: UUID) -> Optional[ModelPersonality]:
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM public.models WHERE id = $1', model_id)
        return ModelPersonality.model_validate(dict(row)) if row else None
    finally:
        await conn.close()

async def list_models() -> List[ModelInfo]:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch('SELECT id, name FROM public.models ORDER BY name')
        return [ModelInfo(id=row['id'], name=row['name']) for row in rows]
    finally:
        await conn.close()

async def create_model(model_data: CreateModelRequest) -> ModelPersonality:
    conn = await get_db_connection()
    try:
        query = """
            INSERT INTO public.models (
                name, language, prompt_additions, gender, race, eye_color, hair_color, hair_style,
                body_type, clothing_style, distinguishing_features,
                libido_level, intelligence_level, dominance, audacity, tone, emotion,
                initiative, vocabulary, emojis, imperfection
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                      $14, $15, $16, $17, $18, $19, $20, $21)
            RETURNING *
        """
        row = await conn.fetchrow(query, *model_data.model_dump().values())
        return ModelPersonality.model_validate(dict(row))
    except asyncpg.UniqueViolationError:
        raise ValueError(f"Une personnalité avec le nom '{model_data.name}' existe déjà.")
    finally:
        await conn.close()

async def update_model_name(model_id: UUID, new_name: str) -> Optional[ModelPersonality]:
    conn = await get_db_connection()
    try:
        query = "UPDATE public.models SET name = $1 WHERE id = $2 RETURNING *"
        row = await conn.fetchrow(query, new_name, model_id)
        return ModelPersonality.model_validate(dict(row)) if row else None
    except asyncpg.UniqueViolationError:
        raise ValueError(f"Une personnalité avec le nom '{new_name}' existe déjà.")
    finally:
        await conn.close()

async def log_chat_interaction(session_id: UUID, model_id: UUID, user_message: str, assistant_response: str) -> None:
    conn = None
    try:
        conn = await get_db_connection()
        query = "INSERT INTO public.chat_logs (session_id, model_id, user_message, assistant_response) VALUES ($1, $2, $3, $4)"
        await conn.execute(query, session_id, model_id, user_message, assistant_response)
    except Exception as e:
        print(f"ATTENTION : Échec de l'enregistrement du log de chat. Erreur: {e}")
    finally:
        if conn:
            await conn.close()