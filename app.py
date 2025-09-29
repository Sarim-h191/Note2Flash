# Note2Flash
# This is the main Flask application that creates flashcards using OpenAI

from flask import Flask, render_template, request, redirect, url_for
import os
import json
from openai import OpenAI

# Create the Flask app instance
# Flask is a web framework that helps us create web applications
app = Flask(__name__)

# Set up OpenAI client using the API key from environment variables
# The integration we added handles the API key automatically
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_flashcards(topic, num_cards=5):
    """
    This function takes a topic and generates flashcards using OpenAI's GPT model.
    
    Args:
        topic (str): The subject or notes the user wants flashcards for
        num_cards (int): How many flashcards to generate (default is 5)
    
    Returns:
        list: A list of dictionaries, each containing a question and answer
    """
    try:
        # Create a detailed prompt that tells GPT how to generate flashcards
        prompt = f"""
        Create {num_cards} educational flashcards about: {topic}
        
        Generate clear, educational question-and-answer pairs that would help someone study this topic.
        Make the questions specific and the answers concise but informative.
        
        Respond with valid JSON in this exact format:
        {{
            "flashcards": [
                {{"question": "Your question here?", "answer": "Your answer here"}},
                {{"question": "Another question?", "answer": "Another answer"}}
            ]
        }}
        """
        
        # Call OpenAI's API to generate the flashcards
        # Use a reliable model that works with most API keys
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator who creates high-quality study flashcards."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        # Parse the JSON response from OpenAI
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
            return result.get("flashcards", [])
        else:
            return [{"question": "Error occurred", "answer": "No response received from AI"}]
        
    except Exception as e:
        # If something goes wrong, return a helpful error message
        print(f"Error generating flashcards: {e}")
        error_msg = str(e)
        if "model" in error_msg.lower():
            return [{"question": "Model Error", "answer": "The AI model is not available. Please try again or contact support if the issue persists."}]
        elif "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
            return [{"question": "Quota Exceeded", "answer": "Your OpenAI account has exceeded its usage quota. Please check your billing details at platform.openai.com or add credits to your account."}]
        elif "api" in error_msg.lower() or "key" in error_msg.lower():
            return [{"question": "API Error", "answer": "There was an issue with the API connection. Please check your API key and try again."}]
        else:
            return [{"question": "Generation Error", "answer": f"Sorry, there was an error generating flashcards: {error_msg}"}]

@app.route('/')
def home():
    """
    This is the homepage route - it shows the main form where users enter their topic.
    When someone visits the website, they'll see this page first.
    """
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    This route handles the form submission when users want to generate flashcards.
    It gets the topic from the form, generates flashcards, and shows the results.
    """
    # Get the topic the user entered in the form
    topic = request.form.get('topic', '').strip()
    
    # Get the number of cards requested (default to 5 if not specified)
    try:
        num_cards = int(request.form.get('num_cards', 5))
        # Make sure the number is reasonable (between 1 and 10)
        num_cards = max(1, min(num_cards, 10))
    except:
        num_cards = 5
    
    # Check if the user actually entered a topic
    if not topic:
        return redirect(url_for('home'))
    
    # Generate the flashcards using our OpenAI function
    flashcards = generate_flashcards(topic, num_cards)
    
    # Show the results page with the generated flashcards
    return render_template('results.html', flashcards=flashcards, topic=topic)

# This runs the Flask app when we start the program
if __name__ == '__main__':
    # Run the app in debug mode so we can see errors and it auto-reloads when we make changes
    # We bind to all interfaces (0.0.0.0) and port 5000 so it works in the Replit environment
    app.run(host='0.0.0.0', port=5000, debug=True)