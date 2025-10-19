import streamlit as st
import json
import os
from io import BytesIO
import importlib

# REMOVE this line if present:
# from streamlit_audiorec import st_audiorec

try:
    _sr = importlib.import_module('streamlit_audiorec')
    st_audiorec = _sr.st_audiorec
except Exception:
    def st_audiorec():
        st.warning("Optional package 'streamlit-audiorec' is not installed; please install with `pip install streamlit-audiorec` or use the 'Upload Audio' tab.")
        return None

# Import utility functions (make sure these exist in your project)
try:
    from utils.audio_processor import process_audio_file
    from utils.ai_services import transcribe_audio, generate_summary
    from utils.content_generator import generate_flashcards, generate_quiz
    from utils.ocr_processor import process_handwritten_notes, enhance_ocr_text_with_ai
    from utils.ai_services import openai
except ImportError as e:
    st.error(f"Error importing utility modules: {e}")
    # Define placeholder functions to prevent crashes
    def process_audio_file(path): return path
    def transcribe_audio(path): return "Sample transcript - please check your imports"
    def generate_summary(text): return "Sample summary - please check your imports"
    def generate_flashcards(text): return [{"question": "Sample?", "answer": "Sample answer"}]
    def generate_quiz(text): return {"multiple_choice": [], "open_ended": []}
    def process_handwritten_notes(image_data): return "Sample OCR text"
    def enhance_ocr_text_with_ai(text, client): return "Enhanced: " + text
    openai = None

# Configure page
st.set_page_config(
    page_title="AI Classroom Assistant",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for Google Classroom inspired design
st.markdown("""
<style>
    /* Import Google Sans font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for colors */
    :root {
        --primary-blue: #4285F4;
        --success-green: #34A853;
        --light-grey: #F8F9FA;
        --dark-grey: #202124;
        --highlight-red: #EA4335;
        --white: #FFFFFF;
    }
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #4285F4 0%, #34A853 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: black; /* Changed from white to black */
        text-align: center;
    }
    
    .app-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 2.5rem;
        margin: 0;
        color: black !important; /* Changed from white to black */
    }
    
    .app-header p {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: black !important; /* Changed from white to black */
    }
    
    /* Card styling */
    .content-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e8eaed;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 2px dashed #4285F4;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs > div > div > div > div {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4285F4;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #3367d6;
    }
    
    /* Download button styling */
    .download-button {
        background-color: #34A853 !important;
        color: white !important;
    }
    
    .download-button:hover {
        background-color: #2d8f47 !important;
    }
    
    /* Success message styling */
    .success-message {
        background-color: #e8f5e8;
        border: 1px solid #34A853;
        border-radius: 8px;
        padding: 1rem;
        color: #137333;
        font-family: 'Inter', sans-serif;
    }
    
    /* Error message styling */
    .error-message {
        background-color: #fce8e6;
        border: 1px solid #EA4335;
        border-radius: 8px;
        padding: 1rem;
        color: #d33b2c;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'quiz' not in st.session_state:
    st.session_state.quiz = {}
if 'current_lecture_id' not in st.session_state:
    st.session_state.current_lecture_id = None
if 'show_history' not in st.session_state:
    st.session_state.show_history = False
if 'study_mode' not in st.session_state:
    st.session_state.study_mode = False
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'flashcard_ids' not in st.session_state:
    st.session_state.flashcard_ids = []

# OpenAI API Key Configuration
st.sidebar.markdown("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")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", 
                               help="Enter your OpenAI API key to enable AI features")

if not api_key:
    st.sidebar.warning("⚠️ Please enter your OpenAI API key to use AI features")
else:
    st.sidebar.success("✅ API key configured")
    # Set the API key for your AI services
    os.environ["OPENAI_API_KEY"] = api_key

# Sidebar for lecture history
with st.sidebar:
    st.markdown("### 📚 Lecture History")
    st.info("Lecture history is disabled (no database). Content will not be saved between sessions.")
    st.markdown("---")
    if st.button("➕ New Lecture", use_container_width=True):
        st.session_state.current_lecture_id = None
        st.session_state.transcript = ""
        st.session_state.summary = ""
        st.session_state.flashcards = []
        st.session_state.quiz = {}
        st.rerun()

# Header
st.markdown("""
<div class="app-header">
    <h1>🎓 AI Classroom Assistant</h1>
    <p>Transform lecture audio into summaries, flashcards, and quizzes with AI</p>
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown('<div class="content-card">', unsafe_allow_html=True)

# Tabs for upload, record, and OCR
upload_tab, record_tab, ocr_tab = st.tabs(["📁 Upload Audio", "🎙️ Record Audio", "📸 Scan Notes"])

with upload_tab:
    st.markdown("### Upload Lecture Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        help="Upload your lecture recording in MP3, WAV, M4A, OGG, or FLAC format"
    )

with record_tab:
    st.markdown("### Record Audio Live")
    st.info("🎙️ Click the microphone button below to start recording your lecture")
    
    audio_bytes = st_audiorec()
    
    if audio_bytes is not None:
        st.audio(audio_bytes, format='audio/wav')
        st.success("✅ Recording captured! Click 'Process Recording' to transcribe.")

with ocr_tab:
    st.markdown("### Scan Handwritten Notes")
    st.info("📸 Upload an image of your handwritten notes to extract text using OCR")
    
    uploaded_image = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Upload a clear image of your handwritten notes",
        key="image_uploader"
    )
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Notes", use_container_width=True)
        
        if st.button("🔍 Extract Text from Notes", type="primary"):
            if not api_key:
                st.error("❌ Please enter your OpenAI API key in the sidebar first")
            else:
                try:
                    with st.spinner("Extracting text from image..."):
                        # Extract text using OCR
                        ocr_text = process_handwritten_notes(uploaded_image.getvalue())
                        
                        # Enhance text with AI
                        with st.spinner("Enhancing extracted text with AI..."):
                            enhanced_text = enhance_ocr_text_with_ai(ocr_text, openai)
                        
                        # Use enhanced text as transcript
                        st.session_state.transcript = enhanced_text
                        
                        # Generate content from extracted text
                        with st.spinner("Generating summary..."):
                            st.session_state.summary = generate_summary(st.session_state.transcript)
                        with st.spinner("Creating flashcards..."):
                            st.session_state.flashcards = generate_flashcards(st.session_state.transcript)
                        with st.spinner("Generating quiz questions..."):
                            st.session_state.quiz = generate_quiz(st.session_state.transcript)
                        
                        st.success("✅ Text extracted and content generated successfully!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error processing image: {str(e)}")

# Process uploaded or recorded audio
audio_to_process = None
audio_filename = None

if uploaded_file is not None:
    audio_to_process = uploaded_file.getvalue()
    audio_filename = uploaded_file.name
    st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")

elif 'audio_bytes' in locals() and audio_bytes is not None:
    audio_to_process = audio_bytes
    audio_filename = "recorded_lecture.wav"
    st.info(f"📄 Recorded audio ready to process")

if audio_to_process is not None:
    # Process button
    if st.button("🎯 Process Audio", type="primary"):
        if not api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar first")
        else:
            try:
                with st.spinner("Processing audio file..."):
                    # Save audio file temporarily
                    temp_path = f"temp_audio_{audio_filename}"
                    with open(temp_path, "wb") as f:
                        f.write(audio_to_process)
                    
                    # Process audio
                    processed_path = process_audio_file(temp_path)
                    
                    # Transcribe audio
                    with st.spinner("Transcribing audio..."):
                        st.session_state.transcript = transcribe_audio(processed_path)
                    
                    # Generate content
                    if st.session_state.transcript:
                        with st.spinner("Generating summary..."):
                            st.session_state.summary = generate_summary(st.session_state.transcript)
                        with st.spinner("Creating flashcards..."):
                            st.session_state.flashcards = generate_flashcards(st.session_state.transcript)
                        with st.spinner("Generating quiz questions..."):
                            st.session_state.quiz = generate_quiz(st.session_state.transcript)
                    
                    # Cleanup temp files
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    if os.path.exists(processed_path) and processed_path != temp_path:
                        os.remove(processed_path)
                    
                    st.success("✅ Audio processed successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error processing audio: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs
if st.session_state.transcript:
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transcript", "📊 Summary", "🎯 Flashcards", "❓ Quiz"])
    
    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Lecture Transcript")
        st.text_area("Transcribed Text", st.session_state.transcript, height=400, disabled=True, key="transcript_area")
        
        # Download transcript
        st.download_button(
            label="📥 Download Transcript",
            data=st.session_state.transcript,
            file_name="lecture_transcript.txt",
            mime="text/plain",
            key="download_transcript"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Lecture Summary")
        if st.session_state.summary:
            st.write(st.session_state.summary)
            
            # Download summary
            st.download_button(
                label="📥 Download Summary",
                data=st.session_state.summary,
                file_name="lecture_summary.txt",
                mime="text/plain",
                key="download_summary"
            )
        else:
            st.info("Summary will appear here after processing audio.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        if st.session_state.flashcards:
            # Study mode toggle
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 🎯 Study Flashcards")
            with col2:
                if not st.session_state.study_mode:
                    if st.button("📖 Start Study Mode", type="primary", key="start_study"):
                        st.session_state.study_mode = True
                        st.session_state.current_card_index = 0
                        st.session_state.show_answer = False
                        st.rerun()
                else:
                    if st.button("📋 Exit Study Mode", key="exit_study"):
                        st.session_state.study_mode = False
                        st.session_state.show_answer = False
                        st.rerun()
            
            if st.session_state.study_mode:
                # Interactive study mode with flip animation
                st.markdown("---")
                
                total_cards = len(st.session_state.flashcards)
                current_index = st.session_state.current_card_index
                current_card = st.session_state.flashcards[current_index]
                
                # Progress bar
                st.progress((current_index + 1) / total_cards, text=f"Card {current_index + 1} of {total_cards}")
                
                # Flashcard with flip animation
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 16px;
                    padding: 3rem;
                    margin: 2rem 0;
                    min-height: 250px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    font-size: 1.3rem;
                    font-family: 'Inter', sans-serif;
                ">
                    {'<strong>Question:</strong><br><br>' + current_card.get('question', 'N/A') if not st.session_state.show_answer else '<strong>Answer:</strong><br><br>' + current_card.get('answer', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
                
                if current_card.get('category'):
                    st.caption(f"📌 Category: {current_card['category']}")
                
                # Flip button
                col_flip1, col_flip2, col_flip3 = st.columns([1, 2, 1])
                with col_flip2:
                    if not st.session_state.show_answer:
                        if st.button("🔄 Show Answer", use_container_width=True, type="primary", key="show_ans"):
                            st.session_state.show_answer = True
                            st.rerun()
                    else:
                        if st.button("🔄 Show Question", use_container_width=True, key="show_ques"):
                            st.session_state.show_answer = False
                            st.rerun()
                
                # Navigation
                st.markdown("---")
                nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
                
                with nav_col1:
                    if current_index > 0:
                        if st.button("⬅️ Previous", use_container_width=True, key="prev_card"):
                            st.session_state.current_card_index -= 1
                            st.session_state.show_answer = False
                            st.rerun()
                
                with nav_col3:
                    if current_index < total_cards - 1:
                        if st.button("Next ➡️", use_container_width=True, key="next_card"):
                            st.session_state.current_card_index += 1
                            st.session_state.show_answer = False
                            st.rerun()
                    else:
                        st.success("🎉 You've completed all flashcards!")
            
            else:
                # List view of all flashcards
                for i, card in enumerate(st.session_state.flashcards, 1):
                    with st.expander(f"📋 Flashcard {i}: {card.get('question', 'Question')[:50]}", key=f"card_{i}"):
                        st.markdown(f"**Question:** {card.get('question', 'N/A')}")
                        st.markdown(f"**Answer:** {card.get('answer', 'N/A')}")
                        if card.get('category'):
                            st.markdown(f"**Category:** {card.get('category')}")
                
                # Download flashcards
                flashcards_json = json.dumps(st.session_state.flashcards, indent=2)
                st.download_button(
                    label="📥 Download Flashcards (JSON)",
                    data=flashcards_json,
                    file_name="lecture_flashcards.json",
                    mime="application/json",
                    key="download_flashcards"
                )
        else:
            st.markdown("### 🎯 Study Flashcards")
            st.info("Flashcards will appear here after processing audio.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### ❓ Practice Quiz")
        if st.session_state.quiz:
            quiz_data = st.session_state.quiz
            
            if 'multiple_choice' in quiz_data and quiz_data['multiple_choice']:
                st.markdown("#### 🎯 Multiple Choice Questions")
                for i, question in enumerate(quiz_data['multiple_choice'], 1):
                    st.markdown(f"**Question {i}:** {question.get('question', 'N/A')}")
                    
                    # Radio buttons for options
                    options = question.get('options', [])
                    if options:
                        selected = st.radio(
                            "Choose your answer:",
                            options,
                            key=f"mc_{i}",
                            index=None
                        )
                        
                        # Show answer button
                        if st.button(f"Show Answer", key=f"show_answer_mc_{i}"):
                            correct_answer = question.get('correct_answer', 'N/A')
                            st.success(f"✅ Correct Answer: {correct_answer}")
                            if question.get('explanation'):
                                st.info(f"💡 Explanation: {question['explanation']}")
                    
                    st.divider()
            
            if 'open_ended' in quiz_data and quiz_data['open_ended']:
                st.markdown("#### 📝 Open-Ended Questions")
                for i, question in enumerate(quiz_data['open_ended'], 1):
                    st.markdown(f"**Question {i}:** {question.get('question', 'N/A')}")
                    
                    # Text area for answer
                    user_answer = st.text_area(
                        "Your answer:",
                        key=f"oe_{i}",
                        height=100
                    )
                    
                    # Show sample answer button
                    if st.button(f"Show Sample Answer", key=f"show_answer_oe_{i}"):
                        sample_answer = question.get('sample_answer', 'N/A')
                        st.success(f"📋 Sample Answer: {sample_answer}")
                    
                    st.divider()
            
            # Download quiz
            quiz_json = json.dumps(st.session_state.quiz, indent=2)
            st.download_button(
                label="📥 Download Quiz (JSON)",
                data=quiz_json,
                file_name="lecture_quiz.json",
                mime="application/json",
                key="download_quiz"
            )
        else:
            st.info("Quiz questions will appear here after processing audio.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Export section
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📥 Export All Content")
    st.write("Download all lecture content in different formats:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export to PDF (placeholder function)
        if st.button("📄 Export to PDF", use_container_width=True, key="export_pdf"):
            st.info("PDF export functionality would be implemented here")
            # This would require additional dependencies like reportlab or weasyprint
    
    with col2:
        # Export to Markdown
        if st.button("📝 Export to Markdown", use_container_width=True, key="export_md"):
            try:
                md_content = f"""# Lecture Content\n\n## Transcript\n\n{st.session_state.transcript}\n\n## Summary\n\n{st.session_state.summary}\n\n## Flashcards\n\n"""
                
                for i, card in enumerate(st.session_state.flashcards, 1):
                    md_content += f"### Flashcard {i}\n\n**Question:** {card.get('question', 'N/A')}\n\n**Answer:** {card.get('answer', 'N/A')}\n\n"
                
                md_content += "\n## Quiz\n\n"
                
                if 'multiple_choice' in st.session_state.quiz:
                    md_content += "### Multiple Choice Questions\n\n"
                    for i, q in enumerate(st.session_state.quiz.get('multiple_choice', []), 1):
                        md_content += f"{i}. {q.get('question', 'N/A')}\n\n"
                
                st.download_button(
                    label="Download Markdown",
                    data=md_content,
                    file_name="lecture_content.md",
                    mime="text/markdown",
                    type="primary",
                    key="download_md"
                )
            except Exception as e:
                st.error(f"Error generating markdown: {e}")
    
    with col3:
        # Export flashcards to CSV
        if st.button("📊 Export Flashcards CSV", use_container_width=True, key="export_csv"):
            if st.session_state.flashcards:
                try:
                    csv_content = "Question,Answer,Category\n"
                    for card in st.session_state.flashcards:
                        question = card.get('question', '').replace('"', '""')
                        answer = card.get('answer', '').replace('"', '""')
                        category = card.get('category', '').replace('"', '""')
                        csv_content += f'"{question}","{answer}","{category}"\n'
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_content,
                        file_name="flashcards.csv",
                        mime="text/csv",
                        type="primary",
                        key="download_csv"
                    )
                except Exception as e:
                    st.error(f"Error generating CSV: {e}")
            else:
                st.warning("No flashcards to export")
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Welcome message when no audio is uploaded
    st.markdown("""
    <div class="content-card" style="color: #222; background: #fff;">
        <h3 style="color: #222;">🚀 Get Started</h3>
        <p style="color: #222;">Upload a lecture audio file to begin generating educational content:</p>
        <ul style="color: #222;">
            <li>📝 <strong>Transcription</strong> - Convert speech to text using AI</li>
            <li>📊 <strong>Summaries</strong> - Get key points and main ideas</li>
            <li>🎯 <strong>Flashcards</strong> - Create study cards for review</li>
            <li>❓ <strong>Quizzes</strong> - Generate practice questions</li>
        </ul>
        <p style="color: #222;"><em>Supported formats: MP3, WAV, M4A, OGG, FLAC</em></p>
        <div class="success-message" style="color: #137333;">
            <strong>🔑 Don't forget:</strong> Enter your OpenAI API key in the sidebar to enable AI features.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #5f6368; font-size: 0.9rem;'>"
    "🤖 Powered by OpenAI | Built with ❤️ using Streamlit"
    "</div>", 
    unsafe_allow_html=True
)