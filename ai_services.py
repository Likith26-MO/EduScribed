import os
import json
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default_key")
openai = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return response
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")

def generate_summary(transcript):
    """
    Generate a comprehensive summary of the lecture transcript.
    
    Args:
        transcript (str): The lecture transcript
        
    Returns:
        str: Generated summary
    """
    try:
        prompt = f"""
        Please analyze the following lecture transcript and create a comprehensive summary that includes:
        
        1. Main topics and key concepts covered
        2. Important definitions and terminology
        3. Key takeaways and conclusions
        4. Any examples or case studies mentioned
        5. Action items or assignments mentioned
        
        Please format the summary in a clear, structured manner with bullet points and headings where appropriate.
        
        Transcript:
        {transcript}
        """
        
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content summarizer. Create clear, comprehensive summaries that help students understand and retain key information from lectures."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2048
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Failed to generate summary: {str(e)}")

def generate_content_with_gpt(transcript, content_type, prompt_template):
    """
    Generate educational content using GPT-5.
    
    Args:
        transcript (str): The lecture transcript
        content_type (str): Type of content (flashcards, quiz, etc.)
        prompt_template (str): The prompt template to use
        
    Returns:
        dict: Generated content in JSON format
    """
    try:
        prompt = prompt_template.format(transcript=transcript)
        
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert educational content creator. Generate high-quality {content_type} based on lecture content. Always respond with valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        
        return json.loads(response.choices[0].message.content)
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response for {content_type}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate {content_type}: {str(e)}")
