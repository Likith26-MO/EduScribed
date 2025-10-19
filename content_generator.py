import json
from utils.ai_services import generate_content_with_gpt

def generate_flashcards(transcript):
    """
    Generate flashcards from lecture transcript.
    
    Args:
        transcript (str): The lecture transcript
        
    Returns:
        list: List of flashcard dictionaries
    """
    prompt_template = """
    Based on the following lecture transcript, create comprehensive study flashcards that cover:
    - Key concepts and definitions
    - Important facts and figures
    - Theoretical principles
    - Examples and applications
    - Formulas or procedures (if any)
    
    Generate 10-15 flashcards in the following JSON format:
    {{
        "flashcards": [
            {{
                "question": "What is the main concept discussed?",
                "answer": "Detailed answer explaining the concept",
                "category": "Main Topics"
            }},
            {{
                "question": "Define [important term]",
                "answer": "Clear definition with context",
                "category": "Definitions"
            }}
        ]
    }}
    
    Categories should include: "Main Topics", "Definitions", "Examples", "Key Facts", "Applications"
    
    Lecture Transcript:
    {transcript}
    """
    
    try:
        result = generate_content_with_gpt(transcript, "flashcards", prompt_template)
        return result.get("flashcards", [])
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return []

def generate_quiz(transcript):
    """
    Generate quiz questions from lecture transcript.
    
    Args:
        transcript (str): The lecture transcript
        
    Returns:
        dict: Dictionary containing multiple choice and open-ended questions
    """
    prompt_template = """
    Based on the following lecture transcript, create a comprehensive quiz that tests understanding of the material.
    
    Generate questions in the following JSON format:
    {{
        "multiple_choice": [
            {{
                "question": "What is the primary focus of this lecture?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "Brief explanation of why this is correct"
            }}
        ],
        "open_ended": [
            {{
                "question": "Explain the relationship between concept A and concept B discussed in the lecture.",
                "sample_answer": "A comprehensive answer that demonstrates understanding",
                "key_points": ["Point 1", "Point 2", "Point 3"]
            }}
        ]
    }}
    
    Create:
    - 5-8 multiple choice questions that test factual knowledge and understanding
    - 3-5 open-ended questions that require deeper analysis and explanation
    - Ensure questions cover different aspects of the lecture content
    - Include explanations for multiple choice answers
    - Provide comprehensive sample answers for open-ended questions
    
    Lecture Transcript:
    {transcript}
    """
    
    try:
        result = generate_content_with_gpt(transcript, "quiz", prompt_template)
        return {
            "multiple_choice": result.get("multiple_choice", []),
            "open_ended": result.get("open_ended", [])
        }
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return {"multiple_choice": [], "open_ended": []}

def generate_study_guide(transcript):
    """
    Generate a comprehensive study guide from lecture transcript.
    
    Args:
        transcript (str): The lecture transcript
        
    Returns:
        dict: Dictionary containing structured study guide content
    """
    prompt_template = """
    Based on the following lecture transcript, create a comprehensive study guide that includes:
    
    Generate the study guide in the following JSON format:
    {{
        "title": "Lecture Topic - Study Guide",
        "overview": "Brief overview of the main topic",
        "key_concepts": [
            {{
                "concept": "Concept Name",
                "definition": "Clear definition",
                "importance": "Why this concept is important"
            }}
        ],
        "main_points": [
            "Key point 1",
            "Key point 2"
        ],
        "examples": [
            {{
                "example": "Example description",
                "explanation": "What this example illustrates"
            }}
        ],
        "review_questions": [
            "Review question 1",
            "Review question 2"
        ],
        "further_reading": [
            "Suggested topic for additional research"
        ]
    }}
    
    Lecture Transcript:
    {transcript}
    """
    
    try:
        result = generate_content_with_gpt(transcript, "study guide", prompt_template)
        return result
    except Exception as e:
        print(f"Error generating study guide: {e}")
        return {}

def generate_key_terms(transcript):
    """
    Extract and define key terms from lecture transcript.
    
    Args:
        transcript (str): The lecture transcript
        
    Returns:
        list: List of key term dictionaries
    """
    prompt_template = """
    Based on the following lecture transcript, identify and define the key terms, concepts, and vocabulary.
    
    Generate the terms in the following JSON format:
    {{
        "key_terms": [
            {{
                "term": "Important Term",
                "definition": "Clear, comprehensive definition",
                "context": "How this term was used in the lecture",
                "related_terms": ["Related term 1", "Related term 2"]
            }}
        ]
    }}
    
    Focus on:
    - Technical terminology
    - Important concepts
    - Proper nouns (people, places, organizations)
    - Specialized vocabulary
    - Acronyms and abbreviations
    
    Lecture Transcript:
    {transcript}
    """
    
    try:
        result = generate_content_with_gpt(transcript, "key terms", prompt_template)
        return result.get("key_terms", [])
    except Exception as e:
        print(f"Error generating key terms: {e}")
        return []
