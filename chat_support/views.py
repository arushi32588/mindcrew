import os
import google.generativeai as genai
from flask import Blueprint, request, jsonify, render_template, session
from flask_session import Session
from flask_login import login_required

chat_support_blueprint = Blueprint('chat_support', __name__)

# Initialize the Gemini API with the API key from the environment variable
genai.configure(api_key='AIzaSyCFoeceKdTmB2WsQgpanU7uCCgGQdKVP4I')
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_response(prompt):
    messages = [
        {"role": "user", "parts": [{"text": "You are a chatbot for answering mental health related queries. Do not provide emotional support, diagnosis or help. Just Answer questions only related to mental health using the following context. Your mission is to excel as a conversational chatbot, specializing in mental health-related inquiries while embracing empathy and understanding."}]}
    ]
    
    # Check if there's previous context in the session
    if 'conversation_history' in session:
        conversation_history = session['conversation_history']
    else:
        conversation_history = []

    conversation_history.append({"role": "user", "parts": [{"text": prompt}]})
    messages.extend(conversation_history)

    try:
        response = model.generate_content(messages)
        response_text = response.parts[0].text.strip()
        
        conversation_history.append({"role": "model", "parts": [{"text": response_text}]})
        session['conversation_history'] = conversation_history
        
        return response_text
    except Exception as e:
        return f"Error: {e}"

@chat_support_blueprint.route('/')
@login_required
def index():
    session.pop('conversation_history', None)
    return render_template('chat_support.html')

@chat_support_blueprint.route('/message', methods=['POST'])
@login_required
def message():
    user_message = request.json['message']
    response = generate_response(user_message)
    return jsonify({"response": response})
