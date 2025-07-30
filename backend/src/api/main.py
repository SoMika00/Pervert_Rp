# Fichier: backend/src/api/main.py (Modifié)

from fastapi import FastAPI
from .routers import chat, models # On importe le nouveau routeur

app = FastAPI(
    title="API de Chat RP Propre",
    description="Une API structurée professionnellement pour un chatbot de Roleplay.",
    version="3.0.0"
)

# Inclusion des routeurs
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(models.router, prefix="/api/v1/models", tags=["Models"]) # Nouveau

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "API Backend fonctionnelle"}