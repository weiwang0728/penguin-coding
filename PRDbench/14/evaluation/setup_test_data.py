#!/usr/bin/env python3
"""
Setup script to populate the database with test data for anonymization testing.
This script creates questionnaires, questions, response sessions, and responses
based on the test data CSV file.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import SessionLocal, create_db_and_tables
from src.models.questionnaire import Questionnaire, Question
from src.models.response import ResponseSession, Response
from datetime import datetime
import csv

def setup_test_data():
    """Setup test data for anonymization testing"""
    
    # Initialize database
    create_db_and_tables()
    db = SessionLocal()
    
    try:
        # Create a test questionnaire
        questionnaire = Questionnaire(
            title="Personal Information Survey",
            description="Questionnaire for testing data anonymization functionality"
        )
        db.add(questionnaire)
        db.commit()
        db.refresh(questionnaire)

        # Create questions
        from src.models.questionnaire import QuestionType
        questions_data = [
            {"id": 1, "text": "What is your name?", "module": "Basic Personal Information", "type": QuestionType.OPEN_TEXT},
            {"id": 2, "text": "What is your contact phone?", "module": "Basic Personal Information", "type": QuestionType.OPEN_TEXT},
            {"id": 3, "text": "What is your gender?", "module": "Basic Personal Information", "type": QuestionType.SINGLE_CHOICE},
            {"id": 4, "text": "What is your age group?", "module": "Basic Personal Information", "type": QuestionType.SINGLE_CHOICE},
        ]
        
        question_objects = {}
        for q_data in questions_data:
            question = Question(
                questionnaire_id=questionnaire.id,
                text=q_data["text"],
                module=q_data["module"],
                question_type=q_data["type"]
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            question_objects[q_data["id"]] = question
        
        # Read test data and create response sessions and responses
        test_data_file = os.path.join(os.path.dirname(__file__), 'test_data_with_personal_info.csv')
        
        with open(test_data_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            sessions = {}
            
            for row in reader:
                session_id = int(row['session_id'])
                
                # Create response session if not exists
                if session_id not in sessions:
                    session = ResponseSession(
                        questionnaire_id=questionnaire.id,
                        collector=row['collector'],
                        location=row['location'],
                        created_at=datetime.strptime(row['session_created_at'], '%Y-%m-%d %H:%M:%S')
                    )
                    db.add(session)
                    db.commit()
                    db.refresh(session)
                    sessions[session_id] = session
                
                # Create response
                question_id = int(row['question_id'])
                if question_id in question_objects:
                    response = Response(
                        session_id=sessions[session_id].id,
                        question_id=question_objects[question_id].id,
                        answer=row['answer']
                    )
                    db.add(response)
        
        db.commit()
        print("Test data has been successfully created!")

    except Exception as e:
        print(f"Error occurred while creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_data()