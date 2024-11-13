# PDFGenie

## Overview
PDFGenie is an interactive chatbot that helps you extract insights from your PDF documents. Using OpenAI's language model, the chatbot answers questions related to the content of your uploaded PDFs. It supports voice-based interaction, allows users to input their names, provides personalized responses, and can export the chat history to a PDF.

## Features:
- Upload PDFs (up to 300MB).
- Ask questions related to the content of the uploaded PDF.
- Chatbot remembers the user's first and last name and addresses them personally.
- Export the chat conversation to a PDF.
- Voice-based input: Users can ask questions using their voice.
- License Activation: Users need to input their API key, which will be valid for 3 months.

## Prerequisites:
1. Python 3.7 or higher.
2. An OpenAI API key (used for querying the OpenAI model).
3. Microphone (if using the voice input feature).

## Installation:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/PDFGenie.git
    cd PDFGenie
    ```

2. **Install required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Save your OpenAI API key:**
    You will need to provide your OpenAI API key to interact with the chatbot. You can enter it when prompted by the application or save it manually.
    
    - After the first login, your API key will be saved for future use.
    - The key will expire in 3 months, and you will be prompted to enter a new one when it expires.

4. **Run the chatbot:**
    ```bash
    streamlit run app.py
    ```

5. **Interact with the Chatbot:**
    - When you first visit the chatbot, you will be asked to provide your first and last name and your OpenAI API key.
    - After successful authentication, you can upload your PDFs and start asking questions.
    - The chatbot will address you by your name and answer questions based on the content of your uploaded PDFs.

## Chatbot Flow:
1. **Enter Name**: Enter your first and last name.
2. **Enter API Key**: Enter your OpenAI API key for license activation.
3. **Upload PDFs**: Upload PDF files (up to 300MB).
4. **Ask Questions**: Ask questions related to your PDF. You can also use voice input.
5. **Export Chat**: Export the chat conversation to a PDF.

## License Activation:
- The API key is required for the first-time activation.
- After entering the key, users will receive a confirmation that their license is activated.
- The key will expire in 3 months, and users will need to input a new key to continue using the service.

## Voice Input (Optional):
- Users can ask questions using voice input via the "Ask a question with your voice" button.
- The chatbot supports offline voice recognition using pocketsphinx.
- Ensure you have a microphone connected and the required packages installed (`speech_recognition` and `pocketsphinx`).

## Troubleshooting:
- If the API key is invalid or expired, you will receive an error message and be asked to enter a new key.
- If you encounter issues with voice recognition, ensure that your microphone is correctly configured and the `pocketsphinx` package is installed.


