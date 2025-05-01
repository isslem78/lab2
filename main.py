from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# Créer toutes les tables et colonnes dans PostgreSQL (si elles n'existent pas déjà)
models.Base.metadata.create_all(bind=engine)

# Modèle pour un choix
class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

# Modèle pour une question contenant une liste de choix
class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()  # Crée une session pour interagir avec la base de données
    try:
        yield db  # Utilisation de la session dans les endpoints
    finally:
        db.close()  # Ferme la session après l'utilisation

# Cette annotation sera utilisée plus tard pour une injection de dépendance
db_dependency = Annotated[Session, Depends(get_db)]

# Exemple d'endpoint pour récupérer toutes les questions
@app.get("/questions", response_model=List[QuestionBase])
def get_questions(db: db_dependency):
    questions = db.query(models.Questions).all()  # Requête pour récupérer toutes les questions
    return questions

# Endpoint pour ajouter une nouvelle question avec ses choix
@app.post('/questions/')
def create_questions(question: QuestionBase, db: db_dependency):
    # Création de la question dans la base de données
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)  # Récupère les dernières informations sur la question après l'insertion

    # Ajout des choix associés à la question
    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)

    db.commit()  # Enregistre les choix dans la base de données
    return {"message": "Question and choices added successfully", "question_id": db_question.id}

# Endpoint pour récupérer une question spécifique avec son ID
@app.get('/questions/{question_id}', response_model=QuestionBase)
def read_questions(question_id: int, db: db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Question not found!")
    
    # Retrieve associated choices for the question
    choices = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    return {"question_text": result.question_text, "choices": [choice.choice_text for choice in choices]}

# Endpoint pour récupérer les choix d'une question spécifique
@app.get('/choices/{question_id}', response_model=List[ChoiceBase])
def read_choices(question_id: int, db: db_dependency):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found!")
    
    # Returning the choices associated with the given question_id
    return result
