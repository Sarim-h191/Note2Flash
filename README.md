# Note2Flash  

An AI-powered flashcard generator that helps students study smarter by converting lecture notes into concise flashcards. Built with Python, Flask, and OpenAI’s GPT models.  

## Features  
- Converts lecture notes or topics into structured Q&A flashcards  
- Uses OpenAI’s GPT model to create concise, educational questions and answers  
- Simple web interface built with Flask, HTML, and CSS  
- Supports customization of number of flashcards (1–10)  

## How to Run  

1. Clone the repository:  
   [https://github.com/Sarim-h191/note2flash](https://github.com/Sarim-h191/note2flash)  
   git clone https://github.com/Sarim-h191/note2flash.git  
   cd note2flash  

2. Install dependencies:  
   pip install -r requirements.txt  

3. Set up your OpenAI API key as an environment variable:  

   **Mac/Linux (bash/zsh):**  
   export OPENAI_API_KEY=your_api_key_here  

   **Windows (PowerShell):**  
   setx OPENAI_API_KEY "your_api_key_here"  

4. Run the Flask app:  
   python app.py  

5. Open your browser and go to:  
   http://127.0.0.1:5000/  

## Results  
- Successfully generates study-ready flashcards from lecture notes or topics  
- Provides an interactive interface to flip and review flashcards  
- Demonstrated usefulness for quick and effective studying  
