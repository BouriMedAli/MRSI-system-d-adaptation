import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import defaultdict
from typing import List, Dict, Optional
import time
import os

# FastAPI app
app = FastAPI(title="Student Recommendation API")

# ----------- Utility functions --------------

def load_pickle_file(filepath: str, description: str):
    try:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"{description} file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading {description}: {str(e)}")

def normalize(value: float, max_val: float) -> float:
    return value / max_val if max_val else 0

# ----------- Load data and model -------------

def load_all_resources():
    print("Loading model and student data...")
    model = load_pickle_file('model.pkl', 'model')
    data = load_pickle_file('data.pkl', 'data')
    student_features = load_pickle_file('student_features.pkl', 'student features')
    metadata = load_pickle_file('metadata.pkl', 'metadata')
    print("Loaded all resources successfully.")
    return model, data, student_features, metadata

model, data, student_features, metadata = load_all_resources()

# Preprocessed sets for fast lookup
student_communities = {row['ID_Étudiant']: set(row['Communautés']) for _, row in data.iterrows()}
student_skills = {row['ID_Étudiant']: set(row['Compétences']) for _, row in data.iterrows()}
student_interests = {row['ID_Étudiant']: set(row["Centres_d'Intérêt"]) for _, row in data.iterrows()}

# ------------- Pydantic Schemas --------------

class QueryProfile(BaseModel):
    numeric: List[float]
    communautés: List[str]
    compétences: List[str]
    centres_d_intérêt: List[str]
    student_id: Optional[int] = None

class StudentRegistration(BaseModel):
    nom: str
    travaux_collaboratifs: float
    nombre_interactions: float
    communautés: List[str]
    compétences: List[str]
    centres_d_intérêt: List[str]

# ----------- Similarity and recommendation functions --------------

def convert_to_ratings(profile: QueryProfile):
    ratings = []
    for cat, prefix in [
        (profile.communautés, "comm"),
        (profile.compétences, "skill"),
        (profile.centres_d_intérêt, "int")
    ]:
        ratings += [("query_user", f"{prefix}_{val}", 1) for val in cat]
    return ratings
