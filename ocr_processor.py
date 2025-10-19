import pytesseract
from PIL import Image
import io

def extract_text_from_image(image_bytes):
    """
    Extract text from an image using OCR (Tesseract).
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")

def process_handwritten_notes(image_bytes):
    """
    Process handwritten notes from an image.
    Uses OCR to extract text and then can be used for generating content.
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        str: Extracted and cleaned text
    """
    try:
        # Extract text using OCR
        extracted_text = extract_text_from_image(image_bytes)
        
        if not extracted_text:
            raise Exception("No text could be extracted from the image. Please ensure the image contains readable text.")
        
        # Basic cleaning
        lines = extracted_text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        cleaned_text = '\n'.join(cleaned_lines)
        
        return cleaned_text
        
    except Exception as e:
        raise Exception(f"Failed to process handwritten notes: {str(e)}")

def enhance_ocr_text_with_ai(ocr_text, openai_client):
    """
    Use AI to clean up and enhance OCR-extracted text.
    This can help correct OCR errors and improve readability.
    
    Args:
        ocr_text: Raw OCR-extracted text
        openai_client: OpenAI client instance
        
    Returns:
        str: Enhanced and cleaned text
    """
    try:
        prompt = f"""
        The following text was extracted from handwritten notes using OCR. 
        Please clean it up, correct any obvious OCR errors, and organize it in a clear, readable format.
        Preserve all the original information and meaning.
        
        OCR Text:
        {ocr_text}
        
        Please provide the cleaned and enhanced version:
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at cleaning and organizing text extracted from handwritten notes. You preserve all information while correcting OCR errors and improving readability."
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
        # If enhancement fails, return original OCR text
        return ocr_text
