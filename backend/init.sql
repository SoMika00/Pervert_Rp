CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crée la table 'models' si elle n'existe pas déjà, avec la structure finale
CREATE TABLE IF NOT EXISTS models (
    -- Métadonnées
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Champs de base
    name VARCHAR(100) NOT NULL UNIQUE,
    language VARCHAR(5) NOT NULL DEFAULT 'fr',

    -- Les instructions de l'utilisateur sont maintenant des ajouts optionnels
    prompt_additions TEXT,

    -- Caractéristiques physiques et de caractère (toutes optionnelles)
    gender VARCHAR(50),
    race VARCHAR(50),
    eye_color VARCHAR(50),
    hair_color VARCHAR(50),
    hair_style VARCHAR(100),
    body_type VARCHAR(100),
    clothing_style VARCHAR(100),
    distinguishing_features TEXT,
    
    -- Sliders de comportement
    libido_level INTEGER NOT NULL DEFAULT 3 CHECK (libido_level BETWEEN 1 AND 5),
    intelligence_level INTEGER NOT NULL DEFAULT 3 CHECK (intelligence_level BETWEEN 1 AND 5),
    dominance INTEGER NOT NULL DEFAULT 3 CHECK (dominance BETWEEN 1 AND 5),
    audacity INTEGER NOT NULL DEFAULT 3 CHECK (audacity BETWEEN 1 AND 5),
    tone INTEGER NOT NULL DEFAULT 2 CHECK (tone BETWEEN 1 AND 5),
    emotion INTEGER NOT NULL DEFAULT 3 CHECK (emotion BETWEEN 1 AND 5),
    initiative INTEGER NOT NULL DEFAULT 3 CHECK (initiative BETWEEN 1 AND 5),
    vocabulary INTEGER NOT NULL DEFAULT 3 CHECK (vocabulary BETWEEN 1 AND 5),
    emojis INTEGER NOT NULL DEFAULT 3 CHECK (emojis BETWEEN 1 AND 5),
    imperfection INTEGER NOT NULL DEFAULT 1 CHECK (imperfection BETWEEN 1 AND 5)
);

-- Table pour les logs de conversation
CREATE TABLE IF NOT EXISTS chat_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id UUID NOT NULL,
    model_id UUID,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);