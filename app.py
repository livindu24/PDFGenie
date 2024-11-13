import os
import streamlit as st
from datetime import datetime, timedelta
from streamlit_chat import message
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from collections import deque
from io import BytesIO
import base64
import speech_recognition as sr  # For voice recognition

# File to save the API key
API_KEY_FILE = "api_key.txt"
KEY_EXPIRATION_FILE = "key_expiration.txt"

def save_api_key(api_key):
    """Save the API key to a file."""
    with open(API_KEY_FILE, "w") as f:
        f.write(api_key)
    expiration_date = datetime.now() + timedelta(days=90)  # Expire after 3 months
    with open(KEY_EXPIRATION_FILE, "w") as f:
        f.write(expiration_date.strftime("%Y-%m-%d"))

def load_api_key():
    """Load the API key from a file if it exists.""" 
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return None

def load_key_expiration():
    """Load the expiration date of the API key.""" 
    if os.path.exists(KEY_EXPIRATION_FILE):
        with open(KEY_EXPIRATION_FILE, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d")
    return None

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'pdfs_processed' not in st.session_state:
        st.session_state.pdfs_processed = False
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None
    if 'messages' not in st.session_state:
        st.session_state.messages = deque(maxlen=6)
    if 'all_messages' not in st.session_state:
        st.session_state.all_messages = []
    if 'user_name' not in st.session_state:  # Initialize user_name if not set
        st.session_state.user_name = None
    if 'api_key_saved' not in st.session_state:
        st.session_state.api_key_saved = False
    if 'api_key_valid' not in st.session_state:
        st.session_state.api_key_valid = False

def process_pdfs(pdfs):
    """Extract text from PDFs and create a knowledge base."""
    with st.spinner('Processing PDFs...'):
        text = ''
        for pdf in pdfs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()

        text_splitter = CharacterTextSplitter(
            separator='\n', chunk_size=500, chunk_overlap=20, length_function=len
        )
        chunks = text_splitter.split_text(text)
        embeddings = OpenAIEmbeddings()
        st.session_state.knowledge_base = FAISS.from_texts(chunks, embeddings)
        st.session_state.pdfs_processed = True
        st.success('PDFs processed. You may now ask questions.')

def answer_question(question):
    """Generate an answer to a question using the knowledge base."""
    st.session_state.messages.append({'message': question, 'is_user': True})
    st.session_state.all_messages.append({'message': question, 'is_user': True})
    with st.spinner('Thinking...'):
        docs = st.session_state.knowledge_base.similarity_search(question)
        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=question)
            print(cb)
    # Use the user's name if available
    if st.session_state.user_name:
        response = f"Hello {st.session_state.user_name}, {response}"
    st.session_state.messages.append({'message': response, 'is_user': False})
    st.session_state.all_messages.append({'message': response, 'is_user': False})

def export_chat_to_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    style = styles['BodyText']
    style.alignment = 4
    story.append(Spacer(1, 0.5 * inch))
    for i in range(0, len(st.session_state.all_messages), 2):
        user_msg = st.session_state.all_messages[i]
        bot_msg = st.session_state.all_messages[i + 1] if i + 1 < len(st.session_state.all_messages) else None
        user_text = 'You: ' + user_msg['message']
        story.append(Paragraph(user_text, style))
        if bot_msg:
            bot_text = 'Bot: ' + bot_msg['message']
            story.append(Paragraph(bot_text, style))
        story.append(Spacer(1, 0.2 * inch))
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def display_chat():
    """Display the chat messages."""
    for i, msg in enumerate(st.session_state.messages):
        message(msg['message'], is_user=msg['is_user'], key=str(i))

# Function for speech recognition
def voice_to_text():
    """Capture voice input and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Say something...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)  # Using Google Speech Recognition API
            st.success(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand your speech.")
            return ""
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
            return ""

def main():
    initialize_session_state()
    st.title('PDFGenie')

    # Load API key and expiration date
    api_key = load_api_key()
    key_expiration = load_key_expiration()

    if not api_key:
        # First-time user to enter the API key
        api_key = st.text_input("Enter your License Key:", type="password")
        if st.button("Activate Product"):
            save_api_key(api_key)
            st.session_state.api_key_saved = True
            st.session_state.api_key_valid = True
            st.success("Your license has been activated successfully! The key will expire in 3 months.")
    else:
        if key_expiration and datetime.now() > key_expiration:
            # Key expired
            st.session_state.api_key_valid = False
            st.warning("Your API key has expired. Please enter a new key.")
        else:
            # Valid API key
            st.session_state.api_key_valid = True
            os.environ["OPENAI_API_KEY"] = api_key

            # User first and last name input
            if not st.session_state.user_name:
                first_name = st.text_input("Enter your First Name:")
                last_name = st.text_input("Enter your Last Name:")
                if st.button("OK"):
                    if first_name and last_name:
                        st.session_state.user_name = f"{first_name} {last_name}"
                        st.success(f"Hello {st.session_state.user_name}, ready to chat!")

            # Upload PDF files
            pdfs = st.file_uploader('Choose PDF files (Max size: 300MB)', type=['pdf'], accept_multiple_files=True)
            process_pdfs_button = st.button('Process PDFs')

            if process_pdfs_button and pdfs and not st.session_state.pdfs_processed:
                process_pdfs(pdfs)
            
            question_placeholder = st.empty()

            if st.session_state.pdfs_processed:
                # Button for voice input
                voice_input_button = st.button("Ask a question with your voice")
                if voice_input_button:
                    user_question = voice_to_text()
                else:
                    user_question = question_placeholder.text_input('Ask a question about your PDF:')

                export_chat_button = st.button('Export Chat')
                if user_question and not export_chat_button:
                    answer_question(user_question)
                    display_chat()

                if len(st.session_state.all_messages) > 0 and export_chat_button:
                    pdf_bytes = export_chat_to_pdf()
                    b64 = base64.b64encode(pdf_bytes).decode()
                    linko = f'<a href="data:application/octet-stream;base64,{b64}" download="chat_history.pdf">Click Here to download your PDF file</a>'
                    st.markdown(linko, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
