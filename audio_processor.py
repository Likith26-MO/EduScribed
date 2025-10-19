import os
from pydub import AudioSegment
from pydub.utils import which

def process_audio_file(file_path):
    """
    Process audio file to ensure compatibility with Whisper API.
    Converts to WAV format and optimizes for transcription.
    
    Args:
        file_path (str): Path to the input audio file
        
    Returns:
        str: Path to the processed audio file
    """
    try:
        # Check if ffmpeg is available
        if not which("ffmpeg"):
            # If ffmpeg is not available, return original file
            # Whisper API can handle most formats directly
            return file_path
        
        # Load audio file
        audio = AudioSegment.from_file(file_path)
        
        # Convert to mono if stereo (reduces file size)
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Set sample rate to 16kHz (optimal for speech recognition)
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        
        # Normalize audio levels
        audio = audio.normalize()
        
        # Export as WAV for best compatibility
        output_path = file_path.rsplit('.', 1)[0] + '_processed.wav'
        audio.export(output_path, format="wav")
        
        return output_path
        
    except Exception as e:
        # If processing fails, return original file
        print(f"Audio processing failed: {e}. Using original file.")
        return file_path

def get_audio_duration(file_path):
    """
    Get duration of audio file in seconds.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except:
        return 0

def split_audio_for_transcription(file_path, chunk_length_ms=300000):  # 5 minutes
    """
    Split large audio files into smaller chunks for better transcription.
    
    Args:
        file_path (str): Path to the audio file
        chunk_length_ms (int): Length of each chunk in milliseconds
        
    Returns:
        list: List of paths to audio chunks
    """
    try:
        audio = AudioSegment.from_file(file_path)
        
        # If audio is shorter than chunk length, return original file
        if len(audio) <= chunk_length_ms:
            return [file_path]
        
        chunks = []
        chunk_number = 0
        
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunk_path = f"{file_path.rsplit('.', 1)[0]}_chunk_{chunk_number}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
            chunk_number += 1
        
        return chunks
        
    except Exception as e:
        print(f"Audio splitting failed: {e}. Using original file.")
        return [file_path]
