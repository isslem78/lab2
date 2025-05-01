
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL string pour la base de données PostgreSQL
# Remplace 'USERNAME', 'PASSWD' et 'quizApp' par tes informations de connexion
URL_DATABASE = 'postgresql://postgresql:azerty2004!@localhost:5432/QuizApplicationYT'

# Création de l'engine SQLAlchemy avec l'URL de la base de données
engine = create_engine(URL_DATABASE)

# Session locale pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Déclaration de la base pour la création des modèles SQLAlchemy
Base = declarative_base()
